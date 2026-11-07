"""Additional lifecycle coverage. Existing behavior, not claimed as new RED slices."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from test_rooms import RoomFixture
from proxy import Proxy
from playwright.sync_api import sync_playwright,expect
from ui_navigation import room_action
class RoomLifecycleBrowserTests(unittest.TestCase):
 def setUp(self):
  self.f=RoomFixture();self.proxy=Proxy(self.f);self.p=sync_playwright().start();self.b=self.p.chromium.launch(headless=True,args=['--no-sandbox','--no-proxy-server','--host-resolver-rules=MAP studio.invalid 127.0.0.1']);self.ctx=self.b.new_context(extra_http_headers={'X-Remote-User-Id':'alice'});self.page=self.ctx.new_page();self.page.goto(self.proxy.url.replace('127.0.0.1','studio.invalid'));self.page.locator('#new-name').fill('Lifecycle Fixture');self.page.locator('#create').click();expect(self.page.locator('#room-status')).to_contain_text('Frisch gelesen');self.page.locator('[data-area="a"]').click()
 def tearDown(self):self.b.close();self.p.stop();self.proxy.close();self.f.close()
 def save(self):self.page.locator('#room-save').click();expect(self.page.locator('#room-dirty')).to_contain_text('Gespeichert')
 def test_nonsecure_origin_cross_room_refresh_missing_disconnect_and_poll(self):
  p=self.page;self.assertFalse(p.evaluate('isSecureContext'));p.locator('#room-scope').select_option('all');p.locator('#room-search').fill('sensor.fixture');room_action(p, '#room-select-visible');self.save();first=self.f.store.list('alice')[0]['roomPlan']['views'][0];self.assertEqual(first['entityRefs'],[{'key':'registry:reg2','entityId':'sensor.fixture'}]);self.assertEqual(first['areaId'],'a')
  p.locator('[data-area="b"]').click();room_action(p, '#room-select-visible');self.save();d=self.f.store.list('alice')[0];self.assertEqual(len(d['roomPlan']['views']),2);self.assertEqual(d['roomPlan']['views'][0]['entityRefs'],d['roomPlan']['views'][1]['entityRefs']);self.assertEqual(self.f.peer.data['entities'][1]['area_id'],'b')
  p.locator('[data-expand="dev"]').click();p.locator('[data-inspect-entity="registry:reg2"]').click();self.f.peer.data['states'][1]['state']='57';p.evaluate('() => roomRefresh(false)');expect(p.locator('#room-properties')).to_contain_text('57');p.locator('[data-view="'+first['id']+'"]').click();p.locator('[data-inspect-entity="registry:reg2"]').click();expect(p.locator('#room-properties')).to_contain_text('57')
  p.locator('#room-title').fill('Behalten trotz Disconnect');self.f.peer.fail='get_states';p.locator('#room-refresh').click();expect(p.locator('#room-status')).to_contain_text('Veraltet');expect(p.locator('#room-title')).to_have_value('Behalten trotz Disconnect');self.assertTrue(p.locator('[data-entity-check="registry:reg2"]').is_checked());self.save()
  self.f.peer.fail=None;self.f.peer.data['entities'].pop(1);self.f.peer.data['states'].pop(1);p.locator('#room-scope').select_option('all');p.locator('#room-refresh').click();expect(p.locator('#room-inventory')).to_contain_text('Nicht mehr im Bestand');self.assertEqual(len(self.f.store.list('alice')[0]['roomPlan']['views'][0]['entityRefs']),1)
  self.assertFalse(any(c['type'].endswith('/update') for c in self.f.peer.commands))
 def test_cas_keeps_staged_fields_and_does_not_adopt_foreign_revision(self):
  self.save();p=self.page;d=self.f.store.list('alice')[0];p.locator('#room-title').fill('Staged room');self.f.store.update('alice',d['id'],d['revision'],{'description':'Foreign edit'});p.locator('#room-save').click();expect(p.locator('#notice')).to_contain_text('inzwischen geändert');expect(p.locator('#room-title')).to_have_value('Staged room');expect(p.locator('#room-dirty')).to_contain_text('Ungespeichert');self.assertEqual(self.f.store.get('alice',d['id'])['roomPlan']['views'][0]['title'],'Gleicher Name')
 def test_missing_confirmation_blocks_retries_preserves_staged_plan(self):
  self.save();p=self.page;d=self.f.store.list('alice')[0];p.locator('#room-title').fill('Write once');self.proxy.lose_read_after_post=('/api/dashboards/'+d['id']+'/rooms','/api/dashboards/'+d['id']);p.locator('#room-save').click();expect(p.locator('#notice')).to_contain_text('nicht eindeutig bestätigt');expect(p.locator('#room-title')).to_have_value('Write once');expect(p.locator('#room-dirty')).to_contain_text('Ungespeichert');self.assertEqual(self.f.store.get('alice',d['id'])['roomPlan']['views'][0]['title'],'Write once');count=len([x for x in self.proxy.requests if x[0]=='POST']);p.locator('#room-save').click();expect(p.locator('#notice')).to_contain_text('unklar');self.assertEqual(count,len([x for x in self.proxy.requests if x[0]=='POST']))
 def test_delayed_room_write_keeps_inputs_locked_through_readback(self):
  self.save();p=self.page;d=self.f.store.list('alice')[0]
  for method,path in [('POST','/api/dashboards/'+d['id']+'/rooms'),('GET','/api/dashboards/'+d['id']),('GET','/api/dashboards')]:
   with self.subTest(phase=(method,path)):
    p.locator('#room-title').fill('Busy '+method+path);self.proxy.hold_response=(method,path);self.proxy.response_arrived.clear();self.proxy.release_response.clear();p.locator('#room-save').click();self.assertTrue(self.proxy.response_arrived.wait(5));expect(p.locator('#room-title')).to_be_disabled();expect(p.locator('#room-visible')).to_be_disabled();expect(p.locator('#room-new')).to_be_disabled();p.keyboard.type('must not land');self.proxy.release_response.set();expect(p.locator('#room-title')).to_be_enabled();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');self.assertNotIn('must not land',p.locator('#room-title').input_value())
if __name__=='__main__':unittest.main()
