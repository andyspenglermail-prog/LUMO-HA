"""Successful slow HTTP writes must not discard edits made through enabled controls."""
import json,os,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from test_http import Fixture
from proxy import Proxy
from playwright.sync_api import sync_playwright,expect
OUT=pathlib.Path(os.environ.get('RAUMSTUDIO_EVIDENCE','/workspace/lumo-import-evidence/implementation/final/browser'))
class BusyWriteTests(unittest.TestCase):
    def test_successful_delayed_write_keeps_edit_controls_locked(self):
        OUT.mkdir(parents=True,exist_ok=True);records=[]
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
            try:
                for phase in ('post','readback','listing'):
                    with self.subTest(phase=phase):
                        f=Fixture();proxy=Proxy(f);context=browser.new_context(extra_http_headers={'X-Remote-User-Id':'alice'});errors=[]
                        try:
                            d=f.store.import_native('alice','Busy '+phase,{'views':[{'title':'One','path':'one','cards':[]},{'title':'Two','path':'two','cards':[]}]})
                            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(proxy.url)
                            page.get_by_role('button',name='Öffnen',exact=True).click();page.locator('[data-tab="background"]').click();page.locator('#bg-mode').select_option('scale');page.locator('#bg-scale').fill('137')
                            target='/api/dashboards/'+d['id']
                            proxy.hold_response={'post':('POST',target+'/save'),'readback':('GET',target),'listing':('GET','/api/dashboards')}[phase]
                            page.locator('#save').click()
                            self.assertTrue(proxy.response_arrived.wait(5),'Real upstream response never reached the hold gate')
                            self.assertEqual(f.store.get('alice',d['id'])['settings']['background']['scale'],137)
                            locked={'scale':page.locator('#bg-scale').is_disabled(),'startView':page.locator('#start-view').is_disabled()}
                            page.locator('#bg-scale').click(force=True);page.keyboard.press('Control+A');page.keyboard.type('150')
                            during=page.locator('#bg-scale').input_value();proxy.release_response.set()
                            expect(page.locator('#notice')).to_contain_text('Dein Entwurf wurde gespeichert und zurückgelesen.')
                            after=page.locator('#bg-scale').input_value();record={'phase':phase,'locked':locked,'during':during,'after':after,'silentlyDiscarded':during=='150' and after!='150'};records.append(record)
                            expect(page.locator('#bg-scale')).to_be_enabled()
                            # New editing after the confirmed save remains usable and persists normally.
                            page.locator('#bg-scale').fill('150');page.locator('#save').click();expect(page.locator('#dirty-label')).to_have_text('Alle Änderungen gespeichert')
                            self.assertEqual(f.store.get('alice',d['id'])['settings']['background']['scale'],150)
                            self.assertEqual(errors,[]);self.assertTrue(all(locked.values()),record);self.assertEqual(during,'137');self.assertEqual(after,'137')
                        finally:
                            proxy.release_response.set();context.close();proxy.close();f.close();(OUT/'R8-busy-results.json').write_text(json.dumps(records,indent=2)+'\n')
            finally:browser.close()
if __name__=='__main__':unittest.main()
