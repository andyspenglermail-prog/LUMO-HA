"""Reference regressions: real app, isolated peer, measured controls."""
import pathlib,sys,unittest,os
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from test_rooms import RoomFixture
from proxy import Proxy
from playwright.sync_api import sync_playwright,expect
from ui_navigation import room_action
OUT=pathlib.Path(os.environ['RAUMSTUDIO_EVIDENCE'])/'reference'
class ReferenceBrowserTests(unittest.TestCase):
 def setUp(self):
  OUT.mkdir(parents=True,exist_ok=True);self.f=RoomFixture();self.pr=Proxy(self.f);self.pw=sync_playwright().start();self.b=self.pw.chromium.launch(args=['--no-sandbox']);self.c=self.b.new_context(viewport={'width':1326,'height':735},extra_http_headers={'X-Remote-User-Id':'alice'});self.p=self.c.new_page();self.errors=[];self.p.on('pageerror',lambda e:self.errors.append(str(e)));self.c.route('**/*',lambda r:r.continue_() if r.request.url.startswith(('http://127.0.0.1:','data:','blob:')) else r.abort());self.p.goto(self.pr.url);self.p.locator('#new-name').fill('Referenz · isolierte Testdaten');self.p.locator('#create').click();expect(self.p.locator('#room-status')).to_contain_text('Frisch gelesen')
 def tearDown(self):
  self.assertFalse(self.errors);self.b.close();self.pw.stop();self.pr.close();self.f.close()
 def bounds(self,s):return self.p.locator(s).bounding_box()
 def test_dynamic_labels_and_selection_markers_are_real(self):
  p=self.p;p.reload();expect(p.locator('#selected-title')).to_contain_text('Referenz');expect(p.locator('.draft-row[data-active="true"] .badge svg')).to_have_count(1,timeout=1500);expect(p.locator('#edit-icon-picker summary svg')).to_have_count(1);p.locator('[data-step="2"]').click();expect(p.locator('.room-search-box svg')).to_be_visible();expect(p.locator('#room-status svg')).to_have_count(1);p.locator('[data-step="3"]').click();expect(p.locator('.design-settings>.hint svg')).to_have_count(1);p.locator('#design-override-accent').fill('#123456');expect(p.locator('label[for=design-override-accent]')).to_contain_text('#123456')
 def test_planned_profiles_stay_disabled_in_favorites_and_tabs(self):
  p=self.p;p.locator('[data-step="3"]').click();expect(p.locator('#design-status')).to_contain_text('Frisch');planned=p.locator('[data-design-profile][data-planned="true"]').first;key=planned.get_attribute('data-design-profile');p.locator('[data-favorite="'+key+'"]').click();p.locator('[data-catalog-tab="favorites"]').click();expect(p.locator('[data-design-profile="'+key+'"]').first).to_be_disabled(timeout=1500);p.locator('[data-catalog-tab="profiles"]').click();expect(p.locator('[data-design-profile="'+key+'"]').first).to_be_disabled();self.assertEqual(p.locator('#design-output').get_attribute('data-profile'),'noir')
 def test_ai_samples_require_explicit_upload_and_preserve_background(self):
  import hashlib,copy
  p=self.p;p.set_viewport_size({'width':1486,'height':838});p.locator('[data-area="a"]').click();room_action(p, '#room-select-visible');p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');before=copy.deepcopy(self.f.store.list('alice')[0]);p.locator('#room-next').click();expect(p.locator('#design-status')).to_contain_text('Frisch');expect(p.locator('[data-design-profile="noir"] img')).to_be_visible(timeout=1500)
  pins={'noir':'7a073f578344b4c82f5c6873647e40b68513c9c2b4304a0cc4d9ffc62080f1eb','ivory':'6fc5b26a42b505b8d1d236c8990c440d81443392b6b59ff31b66ca294986b2b3','smart':'e2875f4cc721e672130a94b26d295c6e11e7b49d61fe2e57f9eb6732d26fb087'}
  for theme in pins:
   response=self.c.request.get(self.pr.url+'sample-'+theme+'.jpg');self.assertEqual(response.status,200);self.assertEqual(response.headers['content-type'],'image/jpeg');self.assertEqual(hashlib.sha256(response.body()).hexdigest(),pins[theme]);count=len(self.f.store.images('alice'));p.locator('#design-category').select_option('Smart & Functional' if theme=='smart' else 'Luxury & Signature');p.locator('[data-design-profile="'+theme+'"]').click();self.assertEqual(len(self.f.store.images('alice')),count);p.locator('[data-adjust="background"]').click();p.locator('#design-use-sample').click();expect(p.locator('#dialog-title')).to_contain_text('KI');p.locator('#dialog-cancel').click();self.assertEqual(len(self.f.store.images('alice')),count);p.locator('#design-use-sample').click();p.locator('#dialog-confirm').click();expect(p.locator('#design-room-image option:checked')).to_contain_text({'noir':'Noir Luxury','ivory':'Soft Ivory Premium','smart':'Smart Clean'}[theme]);expect(p.locator('#design-room-hero')).to_have_attribute('data-photo-state','ready');expect(p.locator('#design-room-photo-state')).to_contain_text('KI-generiertes Stilbeispiel');self.assertEqual(len(self.f.store.images('alice')),count+1);p.locator('#design-save').click();expect(p.locator('#design-dirty')).to_contain_text('Gespeichert');saved=self.f.store.list('alice')[0]
   frame=self.bounds('#design-frame');caption=self.bounds('#design-room-photo-state');photo=self.bounds('#design-room-photo img');self.assertLessEqual(caption['y']+caption['height'],frame['y']+frame['height']);self.assertGreaterEqual(photo['height'],frame['height']*.6)
   for key in ('settings','native','views','roomPlan'):self.assertEqual(saved[key],before[key])
   p.locator('[data-adjust="style"]').click();p.evaluate('scrollTo(0,0)');p.screenshot(path=str(OUT/f'ai-{theme}.png'))
  p.reload();p.locator('[data-step="3"]').click();expect(p.locator('#design-room-photo-state')).to_contain_text('KI-generiertes Stilbeispiel');self.assertFalse(any(c['type'].endswith('/update') or c['type']=='call_service' for c in self.f.peer.commands))
 def test_ai_sample_uncertain_readback_blocks_reupload(self):
  p=self.p;p.locator('[data-area="a"]').click();p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');p.locator('#room-next').click();expect(p.locator('#design-status')).to_contain_text('Frisch');p.locator('[data-adjust="background"]').click();expect(p.locator('#design-use-sample')).to_be_visible(timeout=1500);self.pr.lose_read_after_post=('/api/images','/api/images');p.locator('#design-use-sample').click();p.locator('#dialog-confirm').click();expect(p.locator('#notice')).to_contain_text('Bestätigendes Lesen fehlgeschlagen');self.assertEqual(len(self.f.store.images('alice')),1);expect(p.locator('#design-room-image')).to_have_value('');p.locator('#design-use-sample').click();p.locator('#dialog-confirm').click();expect(p.locator('#notice')).to_contain_text('unklar');self.assertEqual(len(self.f.store.images('alice')),1)
 def test_phone_preview_status_has_readable_width(self):
  p=self.p;p.set_viewport_size({'width':390,'height':844});p.locator('[data-step="3"]').click();expect(p.locator('#design-status')).to_contain_text('Frisch');p.locator('[data-design-panel="preview"]').click();self.assertGreaterEqual(self.bounds('#design-status')['width'],220);self.assertGreaterEqual(self.bounds('#design-view')['width'],100);self.assertFalse(p.evaluate('document.documentElement.scrollWidth>innerWidth'))
 def test_responsive_controls_all_steps_and_orientations(self):
  p=self.p;p.locator('[data-area="a"]').click();room_action(p, '#room-select-visible');p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert')
  for w,h in [(1326,735),(1483,835),(1486,838),(768,1024),(1024,768),(390,844),(844,390)]:
   with self.subTest(viewport=(w,h)):
    c=self.b.new_context(viewport={'width':w,'height':h},has_touch=True,extra_http_headers={'X-Remote-User-Id':'alice'});q=c.new_page();q.on('pageerror',lambda e:self.errors.append(str(e)));c.route('**/*',lambda r:r.continue_() if r.request.url.startswith(('http://127.0.0.1:','data:','blob:')) else r.abort());q.goto(self.pr.url);q.get_by_role('button',name='Öffnen',exact=True).tap()
    for step in (1,2,3):
     q.locator('[data-step="'+str(step)+'"]').tap()
     if step==2:expect(q.locator('#room-status')).to_contain_text('Frisch');q.locator('[data-room-panel="inventory"]').tap() if w<=1000 else None
     if step==3:
      expect(q.locator('#design-status')).to_contain_text('Frisch');q.locator('[data-design-panel="preview"]').tap() if w<=1100 else None
     self.assertFalse(q.evaluate('document.documentElement.scrollWidth>innerWidth'))
     if w>1100:
      footer=q.locator('footer').bounding_box();self.assertLessEqual(footer['y']+footer['height'],h+1)
     q.evaluate('scrollTo(0,0)');q.screenshot(path=str(OUT/f'responsive-step{step}-{w}x{h}.png'),full_page=True)
    for theme in ('noir','ivory','smart'):
     if w<=1100:q.locator('[data-design-panel="catalog"]').tap()
     q.locator('#design-category').select_option('Smart & Functional' if theme=='smart' else 'Luxury & Signature');q.locator('[data-design-profile="'+theme+'"]').tap()
     if w<=1100:q.locator('[data-design-panel="preview"]').tap()
     q.locator('[data-adjust="background"]').tap();q.locator('#design-use-sample').tap();q.locator('#dialog-confirm').tap();expect(q.locator('#design-room-image option:checked')).to_contain_text({'noir':'Noir Luxury','ivory':'Soft Ivory Premium','smart':'Smart Clean'}[theme]);expect(q.locator('#design-room-hero')).to_have_attribute('data-photo-state','ready');q.locator('[data-adjust="style"]').tap();swatch=q.locator('[data-swatch]').first;swatch.tap();q.locator('#design-radius-range').focus();q.keyboard.press('End');self.assertEqual(q.locator('#design-override-radius').input_value(),'40');q.keyboard.press('Home');self.assertEqual(q.locator('#design-override-radius').input_value(),'0')
     if w<=1100:
      for control in (swatch,q.locator('[data-material="glass"]').locator('..')):
       box=control.bounding_box();self.assertGreaterEqual(box['height'],40);self.assertGreaterEqual(box['width'],40)
     q.screenshot(path=str(OUT/f'responsive-{theme}-{w}x{h}.png'),full_page=True)
    q.locator('#design-save').tap();expect(q.locator('#design-dirty')).to_contain_text('Gespeichert');c.close()
 def test_dynamic_context_icons_and_action_disclosures(self):
  p=self.p;p.locator('[data-step="1"]').click();expect(p.locator('#metadata-summary dt svg')).to_have_count(6,timeout=1500);menu=p.locator('.draft-actions summary').first;menu.press('Enter');menu.click();expect(p.locator('.draft-row .actions').first).to_be_hidden();menu.press('Enter');expect(p.locator('.draft-row .actions').first).to_be_visible()
  p.locator('[data-step="2"]').click();p.locator('[data-area="a"]').click();expect(p.locator('#room-origin svg')).to_have_count(2);expect(p.locator('.room-source-card>.hint svg')).to_have_count(1);p.locator('[data-device-properties]').first.click();expect(p.locator('#room-properties h3 svg')).to_have_count(1);expect(p.locator('#room-properties .room-source-value svg')).to_have_count(1);p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');p.locator('#room-next').click();expect(p.locator('#design-status')).to_contain_text('Frisch gelesen');expect(p.locator('#design-dashboard svg')).to_have_count(1);expect(p.locator('.design-options h3 svg')).to_have_count(1)
 def test_style_swatches_radius_and_material_are_visible(self):
  p=self.p;p.set_viewport_size({'width':1486,'height':838});p.locator('[data-step="3"]').click();expect(p.locator('#design-status')).to_contain_text('Frisch gelesen');expect(p.locator('[data-swatch]').first).to_be_visible(timeout=1500)
  for selector in ('#design-radius-range','[data-material="glass"]'):
   box=self.bounds(selector);panel=self.bounds('.design-center');self.assertLessEqual(box['y']+box['height'],panel['y']+panel['height']);self.assertGreaterEqual(box['y'],panel['y'])
  swatch=p.locator('[data-swatch]').nth(1);color=swatch.get_attribute('data-swatch');swatch.click();self.assertEqual(p.locator('#design-override-primary').input_value(),color);self.assertEqual(p.locator('#design-output').evaluate('(e)=>getComputedStyle(e).getPropertyValue("--d-primary").trim()'),color);expect(p.locator('[data-swatch="'+color+'"]').first).to_have_attribute('aria-pressed','true');p.locator('#design-save').click();expect(p.locator('#design-dirty')).to_contain_text('Gespeichert');self.assertEqual(self.f.store.list('alice')[0]['design']['overrides']['primary'],color)
 def test_header_help_settings_and_local_icons(self):
  p=self.p;expect(p.locator('#studio-help')).to_be_visible(timeout=1500);p.locator('#studio-help').click();expect(p.locator('#help-dialog')).to_be_visible();expect(p.locator('#help-dialog')).to_contain_text('keine Geräte');p.keyboard.press('Escape');expect(p.locator('#studio-help')).to_be_focused()
  p.locator('[data-area="a"]').click();p.locator('#studio-settings').click();expect(p.locator('#dialog')).to_be_visible();p.locator('#dialog-discard').click();expect(p.locator('#settings-form')).to_be_visible();self.assertEqual(p.locator('.steps svg').count(),4);self.assertEqual(p.locator('#studio-settings svg').count(),1);self.assertEqual(p.locator('.brand img').count(),1)
  p.locator('#new-name').fill('Zweites');p.locator('#create').click();expect(p.locator('#room-status')).to_contain_text('Frisch');p.locator('#studio-settings').click();expect(p.locator('#selected-title')).to_have_text('Zweites')
 def test_dark_linear_glass_controls_have_real_reversible_effect(self):
  p=self.p;p.set_viewport_size({'width':1486,'height':838});p.locator('[data-area="a"]').click();room_action(p, '#room-select-visible');p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');p.locator('#room-next').click();expect(p.locator('#design-status')).to_contain_text('Frisch gelesen');expect(p.locator('#design-dark-mode')).to_be_visible(timeout=1500)
  editor=p.locator('.brandbar').evaluate('(e)=>getComputedStyle(e).backgroundImage')
  for theme in ('noir','ivory','smart'):
   p.locator('#design-category').select_option('Smart & Functional' if theme=='smart' else 'Luxury & Signature');p.locator('[data-design-profile="'+theme+'"]').click();old=p.locator('.design-card').first.evaluate('(e)=>getComputedStyle(e).backgroundColor');p.locator('#design-dark-mode').check();new=p.locator('.design-card').first.evaluate('(e)=>getComputedStyle(e).backgroundColor');self.assertNotEqual(old,new);p.locator('#design-high-contrast').check();self.assertEqual(p.locator('.design-card').first.evaluate('(e)=>getComputedStyle(e).color'),'rgb(0, 0, 0)');p.locator('#design-high-contrast').uncheck();p.locator('#design-dark-mode').uncheck();self.assertEqual(p.locator('.design-card').first.evaluate('(e)=>getComputedStyle(e).backgroundColor'),old)
  path=p.locator('.design-card .mdi-icon path').first.get_attribute('d');p.locator('#design-icon-style').select_option('linear');self.assertNotEqual(p.locator('.design-card .mdi-icon path').first.get_attribute('d'),path);p.locator('[data-material="glass"]').click();self.assertIn('blur',p.locator('.design-card').first.evaluate('(e)=>getComputedStyle(e).backdropFilter'));expect(p.locator('#design-material-note')).to_contain_text('native');self.assertEqual(p.locator('.brandbar').evaluate('(e)=>getComputedStyle(e).backgroundImage'),editor)
  p.locator('#design-save').click();expect(p.locator('#design-dirty')).to_contain_text('Gespeichert');p.reload();p.locator('[data-step="3"]').click();expect(p.locator('#design-output')).to_have_attribute('data-material','glass');self.assertEqual(p.locator('#design-icon-style').input_value(),'linear')
 def test_favorites_and_my_style_are_dashboard_bound(self):
  p=self.p;p.locator('[data-step="3"]').click();expect(p.locator('#design-status')).to_contain_text('Frisch gelesen');expect(p.locator('[data-favorite="ivory"]')).to_be_visible(timeout=1500);p.locator('[data-favorite="ivory"]').click();p.locator('[data-catalog-tab="favorites"]').click();self.assertEqual(p.locator('[data-design-profile]').count(),1);p.locator('#design-save').click();expect(p.locator('#design-dirty')).to_contain_text('Gespeichert');p.reload();p.locator('[data-step="3"]').click();expect(p.locator('[data-favorite="ivory"]')).to_have_attribute('aria-pressed','true');p.locator('[data-catalog-tab="mine"]').click();expect(p.locator('#design-my-style')).to_contain_text('Dashboard');p.locator('#design-override-radius').fill('23');p.locator('#design-override-radius').dispatch_event('change');expect(p.locator('#design-my-style')).to_contain_text('radius');p.locator('[data-my-reset="radius"]').click();self.assertEqual(p.locator('#design-override-radius').input_value(),'16')
 def test_design_stage_tabs_devices_and_fullscreen(self):
  p=self.p;p.set_viewport_size({'width':1486,'height':838});p.locator('[data-area="a"]').click();room_action(p, '#room-select-visible');p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');p.locator('#room-next').click();expect(p.locator('#design-status')).to_contain_text('Frisch gelesen')
  frame=self.bounds('#design-frame');p.screenshot(path=str(OUT/'step3.png'));self.assertLess(frame['y'],310);self.assertGreater(frame['height'],280);self.assertLess(frame['y']+frame['height'],640)
  expect(p.locator('[data-adjust="style"]')).to_be_visible();self.assertLess(self.bounds('[data-adjust="style"]')['y'],650)
  p.locator('[data-preview-target="phone"]').click();expect(p.locator('#design-output')).to_have_css('width','390px');expect(p.locator('[data-target="phone"]')).to_be_checked();expect(p.locator('#design-dirty')).to_contain_text('Ungespeicherte')
  p.locator('[data-preview-target="desktop"]').click();p.locator('#design-fullscreen').click();expect(p.locator('#design-step')).to_have_class('preview-fullscreen');self.assertGreater(self.bounds('#design-frame')['width'],1200);p.keyboard.press('Escape');expect(p.locator('#design-fullscreen')).to_be_focused()
  p.locator('[data-adjust="background"]').click();expect(p.locator('#design-room-file')).to_be_visible();p.locator('[data-adjust="typography"]').click();expect(p.locator('#design-override-font')).to_be_visible();p.locator('[data-adjust="elements"]').click();expect(p.locator('#design-element-note')).to_contain_text('keine');p.locator('[data-adjust="style"]').click();p.locator('#design-radius-range').focus();p.keyboard.press('End');self.assertEqual(p.locator('#design-override-radius').input_value(),'40');p.keyboard.press('Home');self.assertEqual(p.locator('#design-override-radius').input_value(),'0')
 def test_step1_roomplan_projection_hidden_and_single_navigation(self):
  p=self.p;p.locator('[data-area="a"]').click();p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');p.locator('[data-step="1"]').click();expect(p.locator('#preview-empty')).to_contain_text('1 vorhandene',timeout=1500);self.assertEqual(p.locator('#preview-views button').count(),0)
  p.locator('[data-step="2"]').click();p.locator('#room-visible').uncheck();p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');p.locator('[data-step="1"]').click();expect(p.locator('#preview-empty')).to_contain_text('ausgeblendet')
 def test_properties_explicit_target_and_source_preview(self):
  p=self.p;p.set_viewport_size({'width':1483,'height':835});p.locator('[data-area="a"]').click();p.locator('#room-duplicate').click();room_action(p, '#room-expand-all');p.locator('[data-inspect-entity="registry:reg1"]').click()
  expect(p.locator('#room-display-target')).to_be_visible(timeout=1500)
  ids=p.locator('#room-display-target option').evaluate_all('(es)=>es.map(e=>e.value)');p.locator('#room-display-target').select_option(ids[0]);p.locator('[data-context-selection]').check();p.locator('#room-display-target').select_option(ids[1]);expect(p.locator('[data-context-selection]')).not_to_be_checked()
  self.assertLess(self.bounds('#room-display-target')['y'],560);self.assertLess(self.bounds('#room-correction')['y'],700)
  p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');p.locator('[data-step="1"]').click();expect(p.locator('#preview-empty')).to_contain_text('2 vorhandene');self.assertEqual(p.locator('#preview-views button').count(),2)
  self.assertFalse(any(c['type'].endswith('/update') or c['type']=='call_service' for c in self.f.peer.commands))
 def test_step2_devices_visible_above_footer(self):
  p=self.p;p.set_viewport_size({'width':1483,'height':835});p.locator('[data-area="a"]').click();room_action(p, '#room-select-visible');p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');p.evaluate('scrollTo(0,0)')
  p.screenshot(path=str(OUT/'step2.png'))
  panel=self.bounds('.room-center');device=self.bounds('.room-device');bar=self.bounds('.room-savebar')
  self.assertLess(panel['y'],235);self.assertLess(device['y'],590);self.assertLess(device['y']+device['height'],panel['y']+panel['height']);self.assertLessEqual(bar['y']+bar['height'],835)
  self.assertEqual(p.locator('#room-visible').get_attribute('role'),'switch')
  p.locator('#room-visible').focus();p.keyboard.press('Space');expect(p.locator('#room-visible')).not_to_be_checked();expect(p.locator('#room-dirty')).to_contain_text('Ungespeicherte');p.keyboard.press('Space')
  p.locator('[data-room-filter="light"]').click();self.assertEqual(p.locator('#room-filter').input_value(),'light');expect(p.locator('#room-result-count')).to_contain_text('1 passende')
 def test_step1_real_settings_beside_sources_and_compact_shell(self):
  p=self.p;p.locator('[data-step="1"]').click();p.evaluate('scrollTo(0,0)')
  header=self.bounds('.brandbar');src=self.bounds('.sources');settings=self.bounds('#workspace');preview=self.bounds('#preview');ha=self.bounds('.ha')
  p.screenshot(path=str(OUT/'step1.png'))
  self.assertLessEqual(header['height'],66)
  self.assertGreater(settings['x'],src['x']+src['width'])
  self.assertLess(settings['y'],170);self.assertLess(ha['y'],600);self.assertLess(preview['y'],560)
  self.assertLessEqual(preview['y']+preview['height'],735)
  tabs=[b.bounding_box() for b in p.locator('[data-tab]').all()];self.assertLess(max(b['y'] for b in tabs)-min(b['y'] for b in tabs),2)
  p.locator('[data-tab="background"]').click();expect(p.locator('#image-file')).to_be_visible();p.locator('[data-tab="general"]').click();p.locator('#edit-name').fill('Geändert');expect(p.locator('#dirty-label')).to_contain_text('Ungespeicherte');p.locator('#save').click();expect(p.locator('#dirty-label')).to_contain_text('gespeichert')
  self.assertFalse(p.evaluate('document.documentElement.scrollWidth>innerWidth'))
