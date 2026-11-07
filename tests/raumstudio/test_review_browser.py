"""Behavioral review regressions against real app HTTP/SQLite, no fetch mocks."""
import pathlib,sys,unittest,os
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from test_http import Fixture
from proxy import Proxy
from playwright.sync_api import sync_playwright,expect
from ui_navigation import reveal_actions
OUT=pathlib.Path(os.environ.get('RAUMSTUDIO_EVIDENCE','/workspace/lumo-auftrag02-evidence/implementation/final/browser'))
class ReviewBrowserTests(unittest.TestCase):
    def setUp(self):
        self.f=Fixture();self.proxy=Proxy(self.f);OUT.mkdir(parents=True,exist_ok=True)
        self.p=sync_playwright().start();self.b=self.p.chromium.launch(headless=True,args=['--no-sandbox'])
    def tearDown(self):self.b.close();self.p.stop();self.proxy.close();self.f.close()
    def page(self):
        ctx=self.b.new_context(extra_http_headers={'X-Remote-User-Id':'alice'},has_touch=True)
        page=ctx.new_page();page.goto(self.proxy.url);expect(page.locator('#new-name')).to_be_enabled();return page
    def open(self,page,name):page.locator('.draft-row').filter(has=page.locator('strong').filter(has_text=name)).get_by_role('button',name='Öffnen',exact=True).click()
    def test_R1_row_actions_adopt_only_own_guard_save(self):
        for action in ('Umbenennen','Duplizieren','Löschen'):
            with self.subTest(action=action):
                d=self.f.store.create('alice',action);page=self.page();self.open(page,action)
                page.locator('#edit-description').fill('Eigene Änderung')
                reveal_actions(page.locator('.draft-row').filter(has=page.locator('strong').filter(has_text=action))).get_by_role('button',name=action,exact=True).click()
                page.locator('#dialog-confirm').click()
                if action=='Umbenennen':
                    expect(page.locator('#dialog-title')).to_have_text('Dashboard umbenennen');page.locator('#dialog-input').fill('Umbenannt');page.locator('#dialog-confirm').click()
                    expect(page.locator('#selected-title')).to_have_text('Umbenannt',timeout=2000)
                    self.assertEqual(self.f.store.get('alice',d['id'])['description'],'Eigene Änderung')
                elif action=='Duplizieren':
                    expect(page.locator('#selected-title')).to_have_text(action+' · Kopie',timeout=2000)
                    copies=[x for x in self.f.store.list('alice') if x['name']==action+' · Kopie'];self.assertEqual(copies[0]['description'],'Eigene Änderung');self.assertNotEqual(copies[0]['id'],d['id'])
                else:
                    expect(page.locator('#dialog-title')).to_have_text('Lokalen Entwurf löschen?');page.locator('#dialog-confirm').click()
                    expect(page.locator('#notice')).to_contain_text('Nur der lokale Entwurf wurde gelöscht',timeout=2000)
                    self.assertNotIn(d['id'],[x['id'] for x in self.f.store.list('alice')])
                page.context.close()
    def test_R2_management_target_survives_new_form_guard(self):
        for action in ('duplicate','delete'):
            with self.subTest(action=action):
                d=self.f.store.create('alice','A-'+action);page=self.page();self.open(page,d['name'])
                page.locator('#edit-description').fill('A own save');page.locator('#new-name').fill('B-'+action);page.locator('[data-tab="management"]').click();page.locator('#'+action+'-selected').click()
                page.locator('#dialog-confirm').click()
                if action=='delete':
                    expect(page.locator('#dialog-text')).to_contain_text('A-delete',timeout=2000);page.locator('#dialog-confirm').click();expect(page.locator('#notice')).to_contain_text('Nur der lokale Entwurf wurde gelöscht')
                else:
                    expect(page.locator('#selected-title')).to_have_text('A-duplicate · Kopie',timeout=2000)
                    self.assertEqual(next(x for x in self.f.store.list('alice') if x['name']=='A-duplicate · Kopie')['description'],'A own save')
                rows=self.f.store.list('alice');self.assertEqual(len([x for x in rows if x['name']=='B-'+action]),1)
                if action=='delete':self.assertNotIn(d['id'],[x['id'] for x in rows])
                page.context.close()
    def test_R1_R2_cancel_and_foreign_revision_stays_conflict(self):
        for action in ('Umbenennen','Duplizieren','Löschen'):
            with self.subTest(action=action):
                d=self.f.store.create('alice','Foreign-'+action);page=self.page();self.open(page,d['name'])
                page.locator('#new-name').fill('Nicht erstellen');page.locator('[data-tab="management"]').click();page.locator('#delete-selected').click();page.locator('#dialog-cancel').click()
                self.assertEqual(self.f.store.get('alice',d['id'])['revision'],1);expect(page.locator('#new-name')).to_have_value('Nicht erstellen')
                page.locator('#new-name').fill('');page.locator('[data-tab="general"]').click();page.locator('#edit-description').fill('Own')
                reveal_actions(page.locator('.draft-row').filter(has=page.get_by_text(d['name'],exact=True))).get_by_role('button',name=action,exact=True).click()
                # A foreign write AFTER own save confirmation is not adopted by the action.
                if action=='Duplizieren':
                    self.f.store.update('alice',d['id'],1,{'name':'Foreign wins'});page.locator('#dialog-confirm').click();expect(page.locator('#notice')).to_contain_text('inzwischen geändert')
                else:
                    page.locator('#dialog-confirm').click();expect(page.locator('#dialog-title')).to_have_text('Dashboard umbenennen' if action=='Umbenennen' else 'Lokalen Entwurf löschen?')
                    self.f.store.update('alice',d['id'],2,{'name':'Foreign wins'})
                    if action=='Umbenennen':page.locator('#dialog-input').fill('Must not win')
                    page.locator('#dialog-confirm').click();expect(page.locator('#dialog-error' if action=='Umbenennen' else '#notice')).to_contain_text('inzwischen geändert')
                self.assertEqual(self.f.store.get('alice',d['id'])['name'],'Foreign wins');self.assertTrue(any(status==409 for _,_,status in self.proxy.responses));page.context.close()
    def test_R3_real_icons_picker_unknown_and_native_views(self):
        d=self.f.store.create('alice','Icons','mdi:home');page=self.page();requests=[];page.on('request',lambda r:requests.append(r.url));self.open(page,'Icons')
        expect(page.locator('#preview-icon svg path')).to_have_attribute('d','M10,20V14H14V20H19V12H22L12,3L2,12H5V20H10Z',timeout=2000)
        page.locator('#edit-icon-picker summary').click();page.locator('#edit-icon-search').fill('sofa');page.screenshot(path=str(OUT/'R3-picker.png'),full_page=True)
        page.locator('#edit-icon-options').get_by_role('button',name='mdi:sofa',exact=True).tap();page.locator('#save').click();expect(page.locator('#dirty-label')).to_have_text('Alle Änderungen gespeichert')
        self.assertEqual(self.f.store.get('alice',d['id'])['icon'],'mdi:sofa');expect(page.locator('#preview-icon svg')).to_be_visible()
        page.locator('#edit-icon').fill('mdi:not-a-real-lumo-icon');page.locator('#save').click();self.assertEqual(self.f.store.get('alice',d['id'])['icon'],'mdi:sofa');self.assertFalse(page.locator('#edit-icon').evaluate('(e)=>e.checkValidity()'))
        page.locator('#edit-icon').fill('mdi:home');page.locator('#save').click();expect(page.locator('#dirty-label')).to_have_text('Alle Änderungen gespeichert')
        page.screenshot(path=str(OUT/'R3-icons.png'),full_page=True)
        self.f.peer.configs['fixture-dashboard']['views'][0]['icon']='mdi:weather-sunny'
        page.locator('#load-ha').click();page.locator('.ha-item').filter(has_text='fixture-dashboard').get_by_role('button').click()
        expect(page.locator('#preview-empty svg[data-icon="mdi:weather-sunny"] path')).to_have_count(1)
        self.assertTrue(all(url.startswith(self.proxy.origin+'/') for url in requests),requests)
    def test_R4_header_version_right_seven_viewports(self):
        from test_workflows import VIEWPORTS
        import json
        version=json.loads((pathlib.Path(__file__).resolve().parents[2]/'lumo_raumstudio/config.json').read_text())['version']
        rows=[]
        for w,h in VIEWPORTS:
            with self.subTest(viewport=(w,h)):
                page=self.page();page.set_viewport_size({'width':w,'height':h});expect(page.locator('#version')).to_have_text('Version '+version)
                geometry=page.locator('#version').evaluate('(e)=>{const r=e.getBoundingClientRect(),h=e.closest("header"),b=h.getBoundingClientRect(),pad=parseFloat(getComputedStyle(h).paddingRight);return {x:r.x,right:r.right,y:r.y,bottom:r.bottom,headerRight:b.right,headerBottom:b.bottom,pad}}')
                # Header now includes two real help/settings controls after the version.
                end=page.locator('#studio-settings').bounding_box();right=max(geometry['right'],end['x']+end['width'])
                self.assertAlmostEqual(right,geometry['headerRight']-geometry['pad'],delta=1)
                self.assertGreaterEqual(geometry['x'],w/2);self.assertLessEqual(geometry['bottom'],geometry['headerBottom'])
                self.assertFalse(page.evaluate('()=>document.documentElement.scrollWidth>innerWidth'))
                page.locator('#new-icon-picker summary').tap();page.locator('#new-icon-options').get_by_role('button',name='mdi:home',exact=True).tap()
                page.locator('#new-name').tap();page.keyboard.type('Viewport '+str(w));page.keyboard.press('Enter');expect(page.locator('#room-step')).to_be_visible();page.locator('#room-back').tap()
                page.evaluate('()=>scrollTo(0,0)');page.screenshot(path=str(OUT/f'R4-header-{w}x{h}.png'))
                rows.append({'viewport':[w,h],'version':version,'geometry':geometry,'touchPicker':True,'keyboardCreate':True});page.context.close()
        (OUT/'R4-geometry.json').write_text(json.dumps(rows,indent=2))
    def test_R5_hidden_invalid_name_direct_save(self):
        d=self.f.store.create('alice','Name behalten');page=self.page();errors=[];page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);self.open(page,d['name'])
        page.locator('#edit-description').fill('Nicht verlieren');page.locator('#edit-name').fill('');page.locator('[data-tab="navigation"]').click();count=sum(m=='POST' for m,_ in self.proxy.requests);page.locator('#save').click()
        expect(page.locator('#edit-name')).to_be_visible(timeout=2000);expect(page.locator('#edit-name')).to_be_focused();self.assertEqual(sum(m=='POST' for m,_ in self.proxy.requests),count)
        self.assertEqual(errors,[]);expect(page.locator('#edit-description')).to_have_value('Nicht verlieren');page.screenshot(path=str(OUT/'R5-invalid-name.png'))
        page.locator('#edit-name').fill('Korrigiert');page.locator('#save').click();expect(page.locator('#dirty-label')).to_have_text('Alle Änderungen gespeichert');self.assertEqual(self.f.store.get('alice',d['id'])['description'],'Nicht verlieren')
    def test_R5_hidden_invalid_scale_guard_save(self):
        d=self.f.store.create('alice','Scale behalten');page=self.page();errors=[];page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);self.open(page,d['name'])
        page.locator('#edit-description').fill('Nicht verlieren');page.locator('[data-tab="background"]').click();page.locator('#bg-mode').select_option('scale');page.locator('#bg-scale').fill('301');page.locator('[data-tab="navigation"]').click()
        count=sum(m=='POST' for m,_ in self.proxy.requests);page.locator('[data-step="2"]').click();page.locator('#dialog-confirm').click()
        expect(page.locator('#bg-scale')).to_be_visible(timeout=2000);expect(page.locator('#bg-scale')).to_be_focused();self.assertEqual(sum(m=='POST' for m,_ in self.proxy.requests),count);self.assertEqual(errors,[])
        expect(page.locator('#dashboard-step')).to_be_visible();page.screenshot(path=str(OUT/'R5-invalid-scale.png'));page.locator('#bg-scale').fill('137');page.locator('[data-step="2"]').click();page.locator('#dialog-confirm').click();expect(page.locator('#room-step')).to_be_visible()
        saved=self.f.store.get('alice',d['id']);self.assertEqual(saved['description'],'Nicht verlieren');self.assertEqual(saved['settings']['background']['scale'],137)
    def test_R6_upload_confirmation_get_loss_blocks_all_followup_writes(self):
        from test_images import png
        d=self.f.store.create('alice','Upload Ziel');page=self.page();self.open(page,d['name']);page.locator('#edit-description').fill('Behalten');page.locator('[data-tab="background"]').click()
        self.proxy.lose_read_after_post=('/api/images','/api/images');file={'name':'Once.png','mimeType':'image/png','buffer':png()};page.locator('#image-file').set_input_files(file)
        expect(page.locator('#notice')).to_be_visible();page.wait_for_function('()=>!document.querySelector("#image-file").disabled');self.assertEqual(len(self.f.store.images('alice')),1);image=self.f.store.images('alice')[0]
        self.assertIn(('POST','/api/images',201),self.proxy.responses);self.assertTrue(any(m=='GET' and path=='/api/images' for m,path in self.proxy.requests));self.proxy.lost_read_path=None
        count=sum(m=='POST' for m,_ in self.proxy.requests);page.locator('#image-file').set_input_files(file);page.wait_for_function('()=>!document.querySelector("#image-file").disabled')
        expect(page.locator('#notice')).to_contain_text('unklar',timeout=2000);self.assertEqual(sum(m=='POST' for m,_ in self.proxy.requests),count);expect(page.locator('#notice')).to_contain_text(image['id'])
        page.locator('#save').click();expect(page.locator('#notice')).to_contain_text('neuen Tab');self.assertEqual(sum(m=='POST' for m,_ in self.proxy.requests),count)
        expect(page.locator('#selected-title')).to_have_text(d['name']);page.locator('[data-tab="general"]').click();expect(page.locator('#edit-description')).to_have_value('Behalten');page.screenshot(path=str(OUT/'R6-upload-uncertain.png'),full_page=True)
        other=self.page();self.open(other,d['name']);other.locator('[data-tab="background"]').click();expect(other.locator('#image-choice option')).to_have_count(2);self.assertEqual(len(self.f.store.images('alice')),1)
    def test_R6_delete_confirmation_get_loss_keeps_target_blocks_writes(self):
        d=self.f.store.create('alice','Delete Ziel');page=self.page();self.open(page,d['name']);page.locator('[data-tab="management"]').click()
        self.proxy.lose_read_after_post=('/api/dashboards/'+d['id']+'/delete','/api/dashboards');page.locator('#delete-selected').click();page.locator('#dialog-confirm').click()
        expect(page.locator('#notice')).to_be_visible();page.wait_for_function('()=>!document.querySelector("#delete-selected").disabled');self.assertEqual(self.f.store.list('alice'),[])
        self.assertIn(('POST','/api/dashboards/'+d['id']+'/delete',200),self.proxy.responses);self.proxy.lost_read_path=None;expect(page.locator('#selected-title')).to_have_text(d['name'])
        count=sum(m=='POST' for m,_ in self.proxy.requests);page.locator('#duplicate-selected').click();expect(page.locator('#notice')).to_contain_text('unklar',timeout=2000);self.assertEqual(sum(m=='POST' for m,_ in self.proxy.requests),count);expect(page.locator('#notice')).to_contain_text(d['id'])
        page.locator('#new-name').fill('Blocked');page.locator('#create').click();expect(page.locator('#notice')).to_contain_text('neuen Tab');self.assertEqual(sum(m=='POST' for m,_ in self.proxy.requests),count);page.screenshot(path=str(OUT/'R6-delete-uncertain.png'),full_page=True)
        other=self.page();expect(other.locator('#saved-list')).to_contain_text('Noch keine')
    def test_R3_invalid_new_icon_discard_does_not_poison_reset_form(self):
        page=self.page();page.locator('#new-name').fill('Discard');page.locator('#new-icon').fill('mdi:unknown-lumo-icon');page.locator('[data-step="2"]').click();page.locator('#dialog-discard').click();page.locator('#room-back').click()
        page.locator('#new-name').fill('Valid without icon');page.locator('#create').click();expect(page.locator('#room-step')).to_be_visible(timeout=2000);self.assertEqual(self.f.store.list('alice')[0]['icon'],'')
    def test_R1_foreign_row_revision_never_refreshed(self):
        for action in ('Umbenennen','Duplizieren','Löschen'):
            with self.subTest(action=action):
                d=self.f.store.create('alice','Foreign row '+action);page=self.page();self.f.store.update('alice',d['id'],1,{'name':'Foreign retained '+action})
                reveal_actions(page.locator('.draft-row').filter(has=page.get_by_text(d['name'],exact=True))).get_by_role('button',name=action,exact=True).click()
                if action!='Duplizieren':
                    if action=='Umbenennen':page.locator('#dialog-input').fill('Do not overwrite')
                    page.locator('#dialog-confirm').click()
                expect(page.locator('#dialog-error' if action=='Umbenennen' else '#notice')).to_contain_text('inzwischen geändert')
                self.assertEqual(self.proxy.responses[-1][2],409);self.assertEqual(self.f.store.get('alice',d['id'])['name'],'Foreign retained '+action);page.context.close()
if __name__=='__main__':unittest.main()
