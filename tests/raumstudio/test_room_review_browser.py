"""B1/B2/B3 regressions through real browser, HTTP store and protocol peer."""
import json, os, pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from test_rooms import RoomFixture
from proxy import Proxy
from playwright.sync_api import sync_playwright, expect

OUT = pathlib.Path(os.environ.get('RAUMSTUDIO_EVIDENCE', '/tmp/lumo-room-review-browser'))

class RoomReviewBrowserTests(unittest.TestCase):
    def setUp(self):
        from test_http import Fixture
        self.f = Fixture() if self._testMethodName.startswith('test_b2') else RoomFixture()
        self.proxy = Proxy(self.f)
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=True, args=['--no-sandbox'])
        self.context = self.browser.new_context(extra_http_headers={'X-Remote-User-Id': 'alice'}, has_touch=True)
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda e: self.errors.append(str(e)))
        OUT.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.proxy.release_response.set()
        (OUT / (self._testMethodName + '.json')).write_text(json.dumps({
            'requests': self.proxy.requests, 'responses': self.proxy.responses,
            'protocolCommands': self.f.peer.commands, 'pageErrors': self.errors,
        }, indent=2))
        self.browser.close()
        self.pw.stop()
        self.proxy.close()
        self.f.close()

    def create(self, name):
        p = self.page
        p.locator('#new-name').fill(name)
        p.locator('#create').click()
        expect(p.locator('#room-dashboard')).to_have_text('Dashboard: ' + name)
        expect(p.locator('#room-status')).to_contain_text('Frisch gelesen')
        expect(p.locator('#room-new')).to_be_enabled()
        p.locator('[data-area="a"]').click()
        p.locator('#room-title').fill(name + ' room')
        self.save()
        return next(d for d in self.f.store.list('alice') if d['name'] == name)

    def save(self):
        self.page.locator('#room-save').click()
        expect(self.page.locator('#room-dirty')).to_contain_text('Gespeichert')
        expect(self.page.locator('#room-save')).to_be_enabled()

    def open(self, name):
        self.page.locator('.draft-row').filter(has_text=name).get_by_role('button', name='Öffnen', exact=True).click()
        expect(self.page.locator('#selected-title')).to_have_text(name)
        expect(self.page.locator('#continue')).to_be_enabled()

    def pair(self):
        p = self.page
        p.goto(self.proxy.url)
        a = self.create('Dashboard Alpha')
        p.locator('#room-back').click()
        b = self.create('Dashboard Beta')
        p.locator('#room-back').click()
        self.open(a['name'])
        p.locator('#continue').click()
        expect(p.locator('#room-title')).to_have_value('Dashboard Alpha room')
        return a, b

    def assert_blocked(self, b):
        p = self.page
        expect(p.locator('#room-dashboard')).to_have_text('Dashboard: ' + b['name'])
        expect(p.locator('#room-save')).to_be_disabled()
        expect(p.locator('#room-new')).to_be_disabled()
        expect(p.locator('#room-title')).to_be_disabled()
        expect(p.locator('#room-editor')).to_be_hidden()
        before = len([r for r in self.proxy.requests if r[0] == 'POST'])
        # An already-queued stale handler must be guarded too, not just its button.
        self.assertFalse(p.evaluate('() => roomSave()'))
        self.assertEqual(before, len([r for r in self.proxy.requests if r[0] == 'POST']))

    def recover_and_save_beta(self, a, b):
        p = self.page
        p.locator('#room-back').click()
        p.locator('#continue').click()
        expect(p.locator('#room-title')).to_have_value('Dashboard Beta room')
        expect(p.locator('#room-new')).to_be_enabled()
        p.locator('#room-title').fill('Beta recovered')
        before = len(self.proxy.requests)
        self.save()
        posts = [r for r in self.proxy.requests[before:] if r[0] == 'POST']
        self.assertEqual(posts, [('POST', '/api/dashboards/' + b['id'] + '/rooms')])
        self.assertEqual(self.f.store.get('alice', b['id'])['roomPlan']['views'][0]['title'], 'Beta recovered')
        self.assertEqual(self.f.store.get('alice', a['id']), a)
        self.assertEqual(self.errors, [])

    def test_b1_delayed_dashboard_load_blocks_old_editor_and_late_overwrite(self):
        p = self.page
        a, b = self.pair()
        p.locator('#room-back').click()
        self.open(b['name'])
        self.proxy.hold_response = ('GET', '/api/dashboards/' + b['id'] + '/rooms')
        p.locator('#continue').click()
        self.assertTrue(self.proxy.response_arrived.wait(5))
        self.assert_blocked(b)
        # Leave the pending B request, load A, stage new input, then deliver old B.
        p.locator('#room-back').click()
        self.open(a['name'])
        p.locator('#continue').click()
        expect(p.locator('#room-title')).to_have_value('Dashboard Alpha room')
        p.locator('#room-title').fill('Alpha staged after switch')
        with p.expect_response(lambda r: r.url.endswith('/' + b['id'] + '/rooms')):
            self.proxy.release_response.set()
        p.wait_for_timeout(150)
        expect(p.locator('#room-title')).to_have_value('Alpha staged after switch')
        expect(p.locator('#room-dirty')).to_contain_text('Ungespeichert')
        expect(p.locator('#room-dashboard')).to_have_text('Dashboard: ' + a['name'])
        p.locator('#room-back').click()
        p.locator('#dialog-cancel').click()
        expect(p.locator('#room-title')).to_have_value('Alpha staged after switch')
        p.locator('#room-back').click()
        p.locator('#dialog-discard').click()
        self.open(b['name'])
        p.locator('#continue').click()
        expect(p.locator('#room-title')).to_have_value('Dashboard Beta room')
        self.recover_and_save_beta(a, b)

    def test_b1_failed_dashboard_load_blocks_wrong_target_then_recovers(self):
        p = self.page
        a, b = self.pair()
        p.locator('#room-back').click()
        self.open(b['name'])
        self.proxy.lost_read_path = '/api/dashboards/' + b['id'] + '/rooms'
        p.locator('#continue').click()
        expect(p.locator('#notice')).to_contain_text('Verbindung unterbrochen')
        self.assert_blocked(b)
        self.assertEqual(self.f.store.get('alice', a['id']), a)
        self.assertEqual(self.f.store.get('alice', b['id']), b)
        self.proxy.lost_read_path = None
        self.recover_and_save_beta(a, b)

    def test_b2_room_save_refreshes_native_editor_revision_without_reopen(self):
        import copy
        from test_lossless import CONFIG
        p = self.page
        self.f.peer.configs['fixture-dashboard'] = copy.deepcopy(CONFIG)
        p.goto(self.proxy.url)
        p.locator('#load-ha').click()
        p.locator('.ha-item').filter(has_text='fixture-dashboard').get_by_role('button').click()
        expect(p.locator('#selected-title')).to_have_text('fixture-dashboard')
        p.locator('#native-editor summary').click()
        target = json.dumps(['views', 0, 'cards', 1, 'cards', 0], separators=(',', ':'))
        p.locator('#native-element').select_option(target)
        p.locator('#native-field').select_option('name')
        p.locator('#native-value').fill('Before room save')
        p.locator('#native-save').click()
        expect(p.locator('#notice')).to_contain_text('Gezielte Änderung gespeichert')
        before = self.f.store.list('alice')[0]

        def download(name):
            with p.expect_download() as event:
                p.locator('#native-export').click()
            path = OUT / name
            event.value.save_as(path)
            return path.read_bytes()

        native_before = download('b2-before.json')
        p.locator('#continue').click()
        expect(p.locator('#room-status')).to_contain_text('Frisch gelesen')
        p.locator('#room-title').fill('Local native room overlay')
        self.save()
        saved = self.f.store.get('alice', before['id'])
        self.assertEqual(saved['revision'], before['revision'] + 1)
        before_return = len(self.proxy.requests)
        p.locator('#room-back').click()
        expect(p.locator('#native-form')).to_be_visible()
        expect(p.locator('#native-value')).to_be_enabled()
        self.assertEqual(p.evaluate('importReport.revision'), saved['revision'])
        self.assertEqual(p.evaluate('importReportId'), saved['id'])
        self.assertEqual(native_before, download('b2-after-room.json'))
        p.locator('#native-element').select_option(target)
        p.locator('#native-field').select_option('name')
        p.locator('#native-value').fill('After room save')
        p.locator('#native-save').click()
        expect(p.locator('#notice')).to_contain_text('Gezielte Änderung gespeichert')
        expected = copy.deepcopy(CONFIG)
        expected['views'][0]['cards'][1]['cards'][0]['name'] = 'After room save'
        # Serialized equality preserves scalar types, large integers and key/list order.
        self.assertEqual(json.dumps(json.loads(download('b2-after-edit.json')), ensure_ascii=False),
                         json.dumps(expected, ensure_ascii=False))
        final = self.f.store.get('alice', saved['id'])
        self.assertEqual(final['revision'], saved['revision'] + 1)
        self.assertEqual(final['roomPlan'], saved['roomPlan'])
        self.assertEqual(final['native'], CONFIG)
        self.assertEqual(self.f.peer.configs['fixture-dashboard'], CONFIG)
        self.assertEqual([x for x in self.proxy.requests[before_return:] if x[0] == 'POST'],
                         [('POST', '/api/dashboards/' + saved['id'] + '/native-edit')])
        self.assertIn('lovelace/config', [c['type'] for c in self.f.peer.commands])
        self.assertIn('get_states', [c['type'] for c in self.f.peer.commands])
        self.assertEqual(self.errors, [])

    def test_b3_automatic_poll_updates_focused_rows_without_losing_staged_input(self):
        p = self.page
        # Only shorten the registered production polling timer; do not invoke refresh
        # or replace fetch/results. All reads traverse backend and websocket peer.
        p.add_init_script("""(() => {
            const interval = window.setInterval.bind(window);
            window.setInterval = (fn, ms, ...args) => interval(fn, ms === 30000 ? 500 : ms, ...args);
        })();""")
        p.goto(self.proxy.url)
        self.create('Polling fixture')
        p.locator('#room-scope').select_option('all')
        p.locator('[data-expand="dev"]').click()
        p.locator('[data-entity-check="registry:reg2"]').check()
        p.locator('#room-title').fill('Staged title during polls')
        for attr, value in [('entity-check', '41'), ('inspect-entity', '42')]:
            with self.subTest(focused=attr):
                focused = p.locator('[data-' + attr + '="registry:reg2"]')
                focused.focus()
                before = len([c for c in self.f.peer.commands if c['type'] == 'get_states'])
                previous_time = p.evaluate('roomInventory.fetchedAt')
                self.f.peer.data['states'][1]['state'] = value
                p.wait_for_function('(old) => roomInventory.fetchedAt !== old', arg=previous_time)
                expect(p.locator('[data-entity="registry:reg2"] .room-value')).to_have_text(value + ' W')
                expect(p.locator('#room-status')).to_contain_text('Frisch gelesen')
                expect(focused).to_be_focused()
                expect(p.locator('[data-entity-check="registry:reg2"]')).to_be_checked()
                expect(p.locator('#room-title')).to_have_value('Staged title during polls')
                expect(p.locator('#room-dirty')).to_contain_text('Ungespeichert')
                self.assertGreater(len([c for c in self.f.peer.commands if c['type'] == 'get_states']), before)
        p.locator('[data-inspect-entity="registry:reg2"]').click()
        self.f.peer.fail = 'get_states'
        expect(p.locator('#room-status')).to_contain_text('Veraltet', timeout=5000)
        expect(p.locator('[data-entity="registry:reg2"] .room-value')).to_contain_text('Veraltet')
        expect(p.locator('[data-inspect-entity="registry:reg2"]')).to_be_focused()
        self.f.peer.fail = None
        self.f.peer.data['states'][1]['state'] = '43'
        expect(p.locator('[data-entity="registry:reg2"] .room-value')).to_have_text('43 W')
        expect(p.locator('#room-properties')).to_contain_text('43')
        expect(p.locator('#room-status')).to_contain_text('Frisch gelesen')
        expect(p.locator('[data-inspect-entity="registry:reg2"]')).to_be_focused()
        expect(p.locator('#room-title')).to_have_value('Staged title during polls')
        expect(p.locator('[data-entity-check="registry:reg2"]')).to_be_checked()
        self.assertEqual(self.errors, [])

    def test_b4_collapsed_device_heads_show_neutral_icon_status_and_staleness(self):
        p = self.page
        p.set_viewport_size({'width': 1480, 'height': 960})
        p.goto(self.proxy.url)
        self.create('Device row fixture')
        p.locator('#room-scope').select_option('all')
        head = p.locator('[data-device="dev"] .room-device-head')
        empty = p.locator('[data-device="empty"] .room-device-head')
        for row, label in [(head, 'Verfügbar'), (empty, 'Keine Entitäten')]:
            expect(row.locator('.room-device-icon svg[data-icon="mdi:devices"]')).to_be_visible()
            expect(row.locator('.room-device-icon')).to_have_attribute('aria-label', 'Generisches Gerätesymbol · kein HA-Geräteicon')
            expect(row.locator('.room-device-status')).to_have_text('Status: ' + label)
        expect(p.locator('[data-expand="dev"]')).to_have_attribute('aria-expanded', 'false')
        for disabled, state, label in [('user', 'on', 'Deaktiviert'),
                                       (None, 'unavailable', 'Keine verfügbare Entität'),
                                       (None, 'on', 'Verfügbar')]:
            with self.subTest(device_status=label):
                self.f.peer.data['devices'][0]['disabled_by'] = disabled
                self.f.peer.data['states'][0]['state'] = state
                p.locator('#room-refresh').click()
                expect(head.locator('.room-device-status')).to_have_text('Status: ' + label)
                expect(p.locator('[data-expand="dev"]')).to_have_attribute('aria-expanded', 'false')
        p.screenshot(path=str(OUT / 'b4-device-desktop.png'), full_page=True)
        self.f.peer.fail = 'get_states'
        p.locator('#room-refresh').click()
        expect(p.locator('#room-status')).to_contain_text('Veraltet')
        expect(head.locator('.room-device-status')).to_have_text('Status: Verfügbar · Veraltet')
        expect(empty.locator('.room-device-status')).to_have_text('Status: Keine Entitäten · Veraltet')
        self.f.peer.fail = None
        p.locator('#room-refresh').click()
        expect(head.locator('.room-device-status')).to_have_text('Status: Verfügbar')
        for width, height in [(1480, 960), (820, 1080), (390, 844)]:
            with self.subTest(viewport=(width, height)):
                p.set_viewport_size({'width': width, 'height': height})
                if width <= 1100:
                    p.locator('[data-room-panel="inventory"]').tap()
                head.scroll_into_view_if_needed()
                box = head.bounding_box()
                for selector in ['button[data-expand]', 'button.room-inspect', '.room-device-icon', '.room-device-status', '.room-check']:
                    child = head.locator(selector).bounding_box()
                    self.assertGreater(child['width'], 0)
                    self.assertGreater(child['height'], 0)
                    self.assertGreaterEqual(child['x'], box['x'])
                    self.assertGreaterEqual(child['y'], box['y'])
                    self.assertLessEqual(child['x'] + child['width'], box['x'] + box['width'] + 1)
                    self.assertLessEqual(child['y'] + child['height'], box['y'] + box['height'] + 1)
                self.assertTrue(p.evaluate('document.documentElement.scrollWidth <= innerWidth'))
                p.locator('[data-expand="dev"]').tap()
                expect(p.locator('[data-entity="registry:reg1"]')).to_be_visible()
                p.locator('[data-expand="dev"]').tap()
                p.locator('[data-device-check="dev"]').tap()
                expect(p.locator('[data-device-check="dev"]')).to_be_checked()
                p.locator('[data-device-check="dev"]').tap()
                expect(p.locator('[data-device-check="dev"]')).not_to_be_checked()
                head.screenshot(path=str(OUT / ('b4-device-row-' + str(width) + '.png')))
        self.assertEqual(self.errors, [])
        self.assertFalse(any(c['type'].endswith('/update') for c in self.f.peer.commands))

if __name__ == '__main__':
    unittest.main()
