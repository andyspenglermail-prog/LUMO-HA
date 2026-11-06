import sys,pathlib,unittest,os,json
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from test_http import Fixture
from playwright.sync_api import sync_playwright,expect
OUT=pathlib.Path(os.environ.get('RAUMSTUDIO_EVIDENCE','/workspace/lumo-auftrag02-evidence/implementation/final/browser'));OUT.mkdir(parents=True,exist_ok=True)
class BrowserTests(unittest.TestCase):
    def test_create_settings_reload_second_device(self):
        f=Fixture()
        try:
            with sync_playwright() as p:
                b=p.chromium.launch(headless=True,args=['--no-sandbox']);ctx=b.new_context(viewport={'width':1440,'height':900},extra_http_headers={'X-Remote-User-Id':'alice'});page=ctx.new_page()
                page.goto(f.origin);expect(page.locator('#version')).to_have_text('Version 0.13.0');page.locator('#new-name').fill('Mein Zuhause');page.locator('#new-icon').fill('mdi:home');page.locator('#create').click()
                expect(page.locator('#room-step')).to_be_visible(timeout=3000)
                self.assertEqual(f.store.list('alice')[0]['name'],'Mein Zuhause')
                page.locator('#room-back').click();page.locator('[data-tab="background"]').click();page.locator('#bg-color').fill('#345678');page.locator('#bg-color').dispatch_event('input');page.locator('#bg-opacity').fill('0');page.locator('#save').click()
                expect(page.locator('#dirty-label')).to_have_text('Alle Änderungen gespeichert')
                page.reload();expect(page.locator('#selected-title')).to_have_text('Mein Zuhause')
                page.locator('[data-tab="background"]').click();expect(page.locator('#bg-color')).to_have_value('#345678')
                ctx2=b.new_context(extra_http_headers={'X-Remote-User-Id':'alice'});p2=ctx2.new_page();p2.goto(f.origin);expect(p2.locator('.draft-title')).to_contain_text('Mein Zuhause')
                ctx3=b.new_context(extra_http_headers={'X-Remote-User-Id':'bob'});p3=ctx3.new_page();p3.goto(f.origin);expect(p3.locator('#saved-list')).to_contain_text('Noch keine')
                page.screenshot(path=str(OUT/'desktop-settings.png'),full_page=True);b.close()
        finally:f.close()
    def test_rename_validation_stays_visible_in_dialog(self):
        f=Fixture()
        try:
            f.store.create('alice','Original')
            with sync_playwright() as p:
                b=p.chromium.launch(headless=True,args=['--no-sandbox']);ctx=b.new_context(viewport={'width':320,'height':640},has_touch=True,extra_http_headers={'X-Remote-User-Id':'alice'});page=ctx.new_page();page.goto(f.origin)
                page.get_by_role('button',name='Umbenennen',exact=True).tap();page.locator('#dialog-input').fill('   ');page.locator('#dialog-confirm').tap()
                expect(page.locator('#dialog-error')).to_contain_text('Name:',timeout=3000);expect(page.locator('#dialog')).to_be_visible();expect(page.locator('#dialog-input')).to_have_value('   ')
                page.locator('#dialog-input').fill('Neuer Name');page.locator('#dialog-confirm').tap();expect(page.locator('.draft-title')).to_contain_text('Neuer Name');b.close()
        finally:f.close()
if __name__=='__main__':unittest.main()
