import pathlib,unittest,sys,json,os,copy
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from test_http import Fixture
from proxy import Proxy
from test_images import png
from playwright.sync_api import sync_playwright,expect
OUT=pathlib.Path(os.environ.get('RAUMSTUDIO_EVIDENCE','/workspace/lumo-auftrag01-evidence/implementation/browser'))
VIEWPORTS=[(1440,900),(1280,720),(768,1024),(1024,768),(390,844),(844,390),(320,640)]
class WorkflowTests(unittest.TestCase):
    def setUp(self):self.f=Fixture();self.proxy=Proxy(self.f);OUT.mkdir(parents=True,exist_ok=True)
    def tearDown(self):self.proxy.close();self.f.close()
    def browser(self,p,w=1280,h=720,user='alice'):
        b=p.chromium.launch(headless=True,args=['--no-sandbox']);ctx=b.new_context(viewport={'width':w,'height':h},has_touch=True,extra_http_headers={'X-Remote-User-Id':user});page=ctx.new_page();page.goto(self.proxy.url);return b,ctx,page
    def test_viewport_touch_keyboard_and_modal_geometry(self):
        matrix=[]
        with sync_playwright() as p:
            for w,h in VIEWPORTS:
                with self.subTest(viewport=(w,h)):
                    b,ctx,page=self.browser(p,w,h);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                    page.locator('#new-name').tap();page.keyboard.type(f'Entwurf {w}x{h}');page.keyboard.press('Enter');expect(page.locator('#handoff-step')).to_be_visible();page.locator('#back-dashboard').tap()
                    self.assertFalse(page.evaluate('()=>document.documentElement.scrollWidth>innerWidth'))
                    widths=page.locator('[data-step]').evaluate_all('(es)=>es.map(e=>e.getBoundingClientRect().width)');self.assertLess(max(widths)-min(widths),1)
                    page.screenshot(path=str(OUT/f'overview-{w}x{h}.png'),full_page=True)
                    page.locator('.draft-row').first.get_by_role('button',name='Umbenennen',exact=True).tap();page.locator('#dialog-input').fill('   ');page.locator('#dialog-confirm').tap();expect(page.locator('#dialog-error')).to_contain_text('Name:')
                    rects=page.locator('.dialog-footer button:visible').evaluate_all('(es)=>es.map(e=>{let r=e.getBoundingClientRect();return {x:r.x,y:r.y,right:r.right,bottom:r.bottom,height:r.height}})')
                    for r in rects:self.assertTrue(r['x']>=0 and r['right']<=w and r['y']>=0 and r['bottom']<=h and r['height']>=44,r)
                    page.screenshot(path=str(OUT/f'modal-{w}x{h}.png'));page.locator('#dialog-cancel').tap()
                    page.locator('[data-tab="background"]').tap();page.locator('#bg-mode').select_option('scale');page.locator('#bg-scale').fill('137');page.locator('#bg-opacity').fill('35');page.locator('#bg-position').select_option('right bottom');page.locator('#save').tap();expect(page.locator('#dirty-label')).to_have_text('Alle Änderungen gespeichert')
                    self.assertFalse(page.evaluate('()=>document.documentElement.scrollWidth>innerWidth'));page.locator('#workspace').scroll_into_view_if_needed();page.screenshot(path=str(OUT/f'settings-{w}x{h}.png'),full_page=True)
                    geometry=page.locator('button:visible,input:visible,select:visible,textarea:visible').evaluate_all('(es)=>es.map(e=>{let r=e.getBoundingClientRect();return {id:e.id,text:e.textContent,x:r.x,right:r.right,width:r.width,height:r.height}})')
                    for g in geometry:self.assertTrue(g['x']>=0 and g['right']<=w+1 and g['width']>0,g)
                    self.assertEqual(errors,[]);matrix.append({'viewport':[w,h],'touchActions':True,'keyboardCreate':True,'noOverflow':True,'modalFooter':rects,'geometry':geometry});b.close()
        (OUT/'viewport-matrix.json').write_text(json.dumps(matrix,indent=2))
    def test_dirtyguard_images_import_duplicate_delete(self):
        before=copy.deepcopy(self.f.peer.configs)
        with sync_playwright() as p:
            b,ctx,page=self.browser(p);page.locator('#new-name').fill('Bildentwurf');page.locator('#create').click();expect(page.locator('#handoff-step')).to_be_visible();page.locator('#back-dashboard').click()
            page.locator('#edit-description').fill('Nicht verlieren');page.locator('[data-tab="navigation"]').click();page.locator('[data-tab="general"]').click();expect(page.locator('#edit-description')).to_have_value('Nicht verlieren')
            page.locator('[data-step="3"]').click();expect(page.locator('#dialog')).to_be_visible();page.locator('#dialog-cancel').click();expect(page.locator('#edit-description')).to_have_value('Nicht verlieren');page.locator('[data-step="3"]').click();page.locator('#dialog-confirm').click();expect(page.locator('#handoff-step')).to_be_visible();self.assertEqual(self.f.store.list('alice')[0]['description'],'Nicht verlieren');page.locator('#back-dashboard').click()
            page.locator('[data-tab="background"]').click();page.locator('#image-file').set_input_files({'name':'Synthetisch rot.png','mimeType':'image/png','buffer':png()});expect(page.locator('#notice')).to_contain_text('Bild in Deiner Bibliothek gespeichert');one=page.locator('#image-choice').input_value();self.assertTrue(one)
            page.locator('#bg-opacity').fill('40');page.locator('#bg-mode').select_option('scale');page.locator('#bg-scale').fill('137');page.locator('#bg-color').fill('#123456');page.locator('#bg-color').dispatch_event('input');page.locator('#bg-attachment').select_option('fixed')
            self.assertEqual(page.locator('#preview-image').evaluate('(e)=>getComputedStyle(e).opacity'),'0.4');self.assertEqual(page.locator('#preview-image').evaluate('(e)=>getComputedStyle(e).backgroundSize'),'137% auto');self.assertIn('/api/images/',page.locator('#preview-image').evaluate('(e)=>getComputedStyle(e).backgroundImage'))
            editor=page.locator('.workspace').evaluate('(e)=>getComputedStyle(e).backgroundColor');self.assertEqual(editor,'rgb(255, 255, 255)')
            page.locator('#save').click();expect(page.locator('#dirty-label')).to_have_text('Alle Änderungen gespeichert')
            page.locator('#image-file').set_input_files({'name':'Synthetisch blau.png','mimeType':'image/png','buffer':png('blue')});expect(page.locator('#image-choice option')).to_have_count(3);two=page.locator('#image-choice').input_value();self.assertNotEqual(one,two);page.locator('#image-choice').select_option(one);page.locator('#save').click();expect(page.locator('#dirty-label')).to_have_text('Alle Änderungen gespeichert')
            page.reload();page.locator('[data-tab="background"]').click();expect(page.locator('#image-choice')).to_have_value(one);page.locator('#remove-image').click();page.locator('#save').click();expect(page.locator('#dirty-label')).to_have_text('Alle Änderungen gespeichert');self.assertEqual(len(self.f.store.images('alice')),2)
            page.locator('#load-ha').click();expect(page.locator('#ha-list .ha-item')).to_have_count(3);expect(page.locator('#connection')).to_contain_text('Administrator geprüft');bad=page.locator('.ha-item').filter(has_text='bad-dashboard');expect(bad).to_contain_text('views[0].cards[0].type');expect(bad.get_by_role('button')).to_be_disabled()
            page.locator('.ha-item').filter(has_text='fixture-dashboard').get_by_role('button').click();expect(page.locator('#selected-title')).to_have_text('fixture-dashboard');self.assertEqual(self.f.store.list('alice')[0]['native'],self.f.peer.configs['fixture-dashboard'])
            page.locator('[data-tab="navigation"]').click();expect(page.locator('#start-view')).to_be_enabled();page.locator('#nav-labels').uncheck();page.locator('#save').click();expect(page.locator('#dirty-label')).to_have_text('Alle Änderungen gespeichert')
            page.locator('[data-tab="management"]').click();page.locator('#duplicate-selected').click();expect(page.locator('#selected-title')).to_have_text('fixture-dashboard · Kopie');self.assertEqual(len(self.f.store.list('alice')),3)
            page.locator('#delete-selected').click();page.locator('#dialog-cancel').click();self.assertEqual(len(self.f.store.list('alice')),3);page.locator('#delete-selected').click();page.locator('#dialog-confirm').click();expect(page.locator('#notice')).to_contain_text('Nur der lokale Entwurf wurde gelöscht');self.assertEqual(len(self.f.store.list('alice')),2)
            self.assertEqual(self.f.peer.configs,before);self.assertTrue(all(c['type'] in ('config/auth/list','lovelace/config','lovelace/dashboards/list') for c in self.f.peer.commands));b.close()
    def test_cas_keeps_inputs_and_lost_write_is_never_retried(self):
        d=self.f.store.create('alice','Konflikt')
        with sync_playwright() as p:
            b,ctx,page=self.browser(p);page.get_by_role('button',name='Öffnen',exact=True).click();page.locator('#edit-name').fill('Mein nicht gesicherter Name')
            self.f.store.update('alice',d['id'],1,{'name':'Anderes Gerät'});page.locator('#save').click();expect(page.locator('#notice')).to_contain_text('inzwischen geändert');self.assertGreaterEqual(page.locator('#notice').bounding_box()['y'],0);expect(page.locator('#edit-name')).to_have_value('Mein nicht gesicherter Name');self.assertEqual(self.f.store.get('alice',d['id'])['name'],'Anderes Gerät')
            page.on('dialog',lambda dialog:dialog.accept());page.reload();page.get_by_role('button',name='Öffnen',exact=True).click();page.locator('#edit-name').fill('Antwort verloren');self.proxy.drop_next_post=True;page.locator('#save').click();expect(page.locator('#notice')).to_contain_text('nicht bestätigt');self.assertEqual(self.f.store.get('alice',d['id'])['name'],'Antwort verloren');expect(page.locator('#edit-name')).to_have_value('Antwort verloren')
            count=sum(m=='POST' for m,_ in self.proxy.requests);page.locator('#save').click();expect(page.locator('#notice')).to_contain_text('unklar');self.assertEqual(sum(m=='POST' for m,_ in self.proxy.requests),count);b.close()
    def test_two_pending_forms_create_only_once(self):
        self.f.store.create('alice','Bestehend')
        with sync_playwright() as p:
            b,ctx,page=self.browser(p);console_errors=[];page.on('console',lambda m:console_errors.append(m.text) if m.type=='error' else None);page.get_by_role('button',name='Öffnen',exact=True).click();page.locator('#edit-description').fill('Alt behalten');page.locator('#new-name').fill('Neu erstellen');page.locator('#create').click();page.locator('#dialog-confirm').click();expect(page.locator('#handoff-step')).to_be_visible()
            self.assertEqual(len(self.f.store.list('alice')),2);self.assertEqual([d['description'] for d in self.f.store.list('alice') if d['name']=='Bestehend'],['Alt behalten']);page.wait_for_timeout(100);self.assertEqual(console_errors,[]);b.close()
    def test_alternate_prefix_plain_http_and_reload_guard(self):
        with sync_playwright() as p:
            b=p.chromium.launch(headless=True,args=['--no-sandbox','--no-proxy-server','--host-resolver-rules=MAP studio.invalid 127.0.0.1']);ctx=b.new_context(extra_http_headers={'X-Remote-User-Id':'alice'});page=ctx.new_page();url=self.proxy.url.replace('127.0.0.1','studio.invalid');page.goto(url)
            self.assertFalse(page.evaluate('()=>isSecureContext'));page.locator('#new-name').fill('Normales HTTP');page.locator('#create').click();expect(page.locator('#handoff-step')).to_be_visible();page.locator('#back-dashboard').click();page.locator('#edit-description').fill('Bleibt im Tab')
            dialogs=[]
            def cancel_reload(dialog):dialogs.append(dialog.type);dialog.dismiss()
            page.on('dialog',cancel_reload)
            try:page.reload(timeout=2000)
            except Exception:pass
            self.assertIn('beforeunload',dialogs);expect(page.locator('#edit-description')).to_have_value('Bleibt im Tab')
            page.locator('#save').click();expect(page.locator('#dirty-label')).to_have_text('Alle Änderungen gespeichert')
            self.proxy.prefix='/anderer/ingress/pfad/';ctx2=b.new_context(extra_http_headers={'X-Remote-User-Id':'alice'});other=ctx2.new_page();other.goto((self.proxy.origin+self.proxy.prefix).replace('127.0.0.1','studio.invalid'));other.get_by_role('button',name='Öffnen',exact=True).click();expect(other.locator('#edit-description')).to_have_value('Bleibt im Tab');b.close()
if __name__=='__main__':unittest.main()
