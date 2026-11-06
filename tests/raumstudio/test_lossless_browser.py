"""Real browser → ingress proxy → HTTP → Store; only synthetic HA peer."""
import copy,json,os,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from test_http import Fixture
from proxy import Proxy
from test_lossless import CONFIG
from playwright.sync_api import sync_playwright,expect
OUT=pathlib.Path(os.environ.get('RAUMSTUDIO_EVIDENCE','/workspace/lumo-import-evidence/implementation/browser'))

class LosslessBrowserTests(unittest.TestCase):
    def test_import_report_download_edit_and_inert_data(self):
        f=Fixture();proxy=Proxy(f);f.peer.configs['fixture-dashboard']=copy.deepcopy(CONFIG);OUT.mkdir(parents=True,exist_ok=True)
        try:
            with sync_playwright() as p:
                b=p.chromium.launch(headless=True,args=['--no-sandbox']);ctx=b.new_context(viewport={'width':1280,'height':900},has_touch=True);page=ctx.new_page();requests=[];errors=[]
                page.on('request',lambda r:requests.append(r.url));page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(proxy.url);page.locator('#load-ha').click()
                page.locator('.ha-item').filter(has_text='fixture-dashboard').get_by_role('button').click()
                expect(page.locator('#selected-title')).to_have_text('fixture-dashboard')
                expect(page.locator('#import-detail')).to_be_visible(timeout=2000)
                expect(page.locator('#import-summary')).to_contain_text('geschützt')
                expect(page.locator('#import-resources')).to_contain_text('ungeprüft')
                self.assertFalse(page.locator('#import-technical').evaluate('(e)=>e.open'))
                self.assertIsNone(page.evaluate('()=>window.__EXECUTED__'))
                self.assertIsNone(page.evaluate('()=>({}).polluted'))
                def download(name):
                    with page.expect_download() as event:page.locator('#native-export').click()
                    dl=event.value;dest=OUT/name;dl.save_as(dest)
                    self.assertTrue(dl.suggested_filename.endswith('.json'))
                    return json.loads(dest.read_text())
                self.assertEqual(download('synthetic-untouched.json'),CONFIG)
                # Renaming and global background/navigation are explicitly local overlays.
                expect(page.locator('#import-overlay-note')).to_contain_text('nicht im JSON-Export')
                page.locator('#edit-name').fill('Only local name');page.locator('#save').click()
                expect(page.locator('#dirty-label')).to_have_text('Alle Änderungen gespeichert')
                page.locator('[data-tab="background"]').click();page.locator('#bg-color').fill('#123456');page.locator('#bg-color').dispatch_event('input');page.locator('#save').click()
                expect(page.locator('#dirty-label')).to_have_text('Alle Änderungen gespeichert')
                self.assertEqual(download('synthetic-overlay.json'),CONFIG)
                page.locator('#native-editor summary').click()
                target=['views',0,'cards',1,'cards',0]
                page.locator('#native-element').select_option(json.dumps(target,separators=(',',':')))
                page.locator('#native-field').select_option('name');page.locator('#native-value').fill('Only this name')
                page.locator('#native-save').click();expect(page.locator('#notice')).to_contain_text('Gezielte Änderung gespeichert')
                expected=copy.deepcopy(CONFIG);expected['views'][0]['cards'][1]['cards'][0]['name']='Only this name'
                self.assertEqual(download('synthetic-edited.json'),expected)
                saved=f.store.list('alice')[0];self.assertEqual(saved['native'],CONFIG)
                page.reload();expect(page.locator('#selected-title')).to_have_text('Only local name');expect(page.locator('#import-detail')).to_be_visible()
                self.assertEqual(download('synthetic-reloaded.json'),expected)
                page.locator('#import-technical summary').click();expect(page.locator('#import-technical')).to_contain_text('custom:button-card')
                self.assertEqual(errors,[]);self.assertTrue(all(u.startswith(proxy.origin) or u.startswith('blob:') for u in requests),requests)
                self.assertEqual(f.peer.configs['fixture-dashboard'],CONFIG)
                self.assertIsNone(page.evaluate('()=>window.__EXECUTED__'));self.assertIsNone(page.evaluate('()=>({}).polluted'))
                page.screenshot(path=str(OUT/'lossless-desktop.png'),full_page=True)
                page.set_viewport_size({'width':390,'height':844});page.locator('#import-technical summary').tap()
                self.assertFalse(page.evaluate('()=>document.documentElement.scrollWidth>innerWidth'))
                page.locator('#native-export').scroll_into_view_if_needed()
                with page.expect_download() as ev:page.locator('#native-export').tap()
                self.assertEqual(json.loads(pathlib.Path(ev.value.path()).read_text()),expected)
                expect(page.locator('#native-export')).to_be_enabled()
                page.screenshot(path=str(OUT/'lossless-mobile.png'),full_page=True)
                page.locator('#native-editor summary').tap();page.locator('#native-value').fill('Mobile pending input')
                expect(page.locator('#native-save')).to_be_enabled()
                self.assertFalse(page.evaluate('()=>document.documentElement.scrollWidth>innerWidth'))
                page.locator('#import-detail').screenshot(path=str(OUT/'lossless-mobile-editor.png'))
                page.locator('#native-cancel').tap();expect(page.locator('#dirty-label')).to_have_text('Alle Änderungen gespeichert')
                self.assertEqual(f.store.get('alice',saved['id'])['native'],CONFIG)
                (OUT/'lossless-browser.json').write_text(json.dumps({'requests':requests,'pageErrors':errors,'externalRequests':False,'touchDownload':True,'originalUnchanged':True},indent=2))
                b.close()
        finally:proxy.close();f.close()

    def test_native_dirty_guard_reveals_invalid_collapsed_field(self):
        f=Fixture();proxy=Proxy(f)
        try:
            f.store.import_native('alice','Validation',CONFIG)
            with sync_playwright() as p:
                b=p.chromium.launch(headless=True,args=['--no-sandbox']);page=b.new_page();page.goto(proxy.url)
                page.get_by_role('button',name='Öffnen',exact=True).click();page.locator('#native-editor summary').click()
                page.locator('#native-value').fill('');page.locator('#native-editor summary').click()
                page.locator('[data-step="2"]').click();page.locator('#dialog-confirm').click()
                expect(page.locator('#native-editor')).to_have_attribute('open','')
                expect(page.locator('#native-value')).to_be_focused()
                expect(page.locator('#dashboard-step')).to_be_visible()
                self.assertEqual(f.store.list('alice')[0]['revision'],1)
                page.locator('#native-cancel').click();expect(page.locator('#dirty-label')).to_have_text('Alle Änderungen gespeichert');b.close()
        finally:proxy.close();f.close()

    def test_native_conflict_and_lost_confirmation_preserve_input(self):
        f=Fixture();proxy=Proxy(f)
        try:
            d=f.store.import_native('alice','Conflict',CONFIG)
            with sync_playwright() as p:
                b=p.chromium.launch(headless=True,args=['--no-sandbox']);page=b.new_page();page.goto(proxy.url)
                page.get_by_role('button',name='Öffnen',exact=True).click();page.locator('#native-editor summary').click()
                page.locator('#native-value').fill('Pending native title')
                expect(page.locator('#edit-name')).to_be_disabled()
                f.store.update('alice',d['id'],1,{'name':'Other device'})
                page.locator('#native-save').click();expect(page.locator('#notice')).to_contain_text('inzwischen geändert')
                expect(page.locator('#native-value')).to_have_value('Pending native title')
                page.on('dialog',lambda dialog:dialog.accept());page.reload()
                expect(page.locator('#selected-title')).to_have_text('Other device');page.locator('#native-editor summary').click()
                page.locator('#native-value').fill('Uncertain native title')
                proxy.lose_read_after_post=('/api/dashboards/'+d['id']+'/native-edit','/api/dashboards/'+d['id'])
                page.locator('#native-save').click();expect(page.locator('#notice')).to_contain_text('nicht eindeutig bestätigt')
                expect(page.locator('#native-value')).to_have_value('Uncertain native title')
                stored=f.store.get('alice',d['id']);self.assertEqual(stored['revision'],3);self.assertEqual(stored['native'],CONFIG)
                count=sum(m=='POST' for m,_ in proxy.requests)
                page.locator('#native-save').click();expect(page.locator('#notice')).to_contain_text('unklar')
                self.assertEqual(sum(m=='POST' for m,_ in proxy.requests),count)
                b.close()
        finally:proxy.close();f.close()

    def test_strategy_has_no_invented_empty_canvas(self):
        f=Fixture();proxy=Proxy(f)
        try:
            f.store.import_native('alice','Strategy',{'strategy':{'type':'custom:strategy','opaque':True}})
            with sync_playwright() as p:
                b=p.chromium.launch(headless=True,args=['--no-sandbox']);page=b.new_page();page.goto(proxy.url)
                page.get_by_role('button',name='Öffnen',exact=True).click()
                expect(page.locator('#preview-empty')).to_contain_text('geschützt')
                expect(page.locator('#preview-empty')).not_to_contain_text('leere Leinwand')
                page.locator('#native-editor summary').click();expect(page.locator('#native-empty')).to_be_visible()
                expect(page.locator('#import-resources')).to_contain_text('nicht verfügbar');b.close()
        finally:proxy.close();f.close()

if __name__=='__main__':unittest.main()
