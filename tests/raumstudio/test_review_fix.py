"""Six independently reported defects: real UI + local protocol peer only."""
import pathlib,os,unittest,json
import test_reference_browser as reference
from playwright.sync_api import expect
OUT=pathlib.Path(os.environ['RAUMSTUDIO_EVIDENCE'])/'review-fix'
class ReviewFixTests(unittest.TestCase):
 setUp=reference.ReferenceBrowserTests.setUp
 tearDown=reference.ReferenceBrowserTests.tearDown
 bounds=reference.ReferenceBrowserTests.bounds
 def shot(self,name):
  OUT.mkdir(parents=True,exist_ok=True);self.p.screenshot(path=str(OUT/(name+'.png')),full_page=True)
  geometry=self.p.evaluate('''()=>{const selectors=['#preview','#preview-empty','#preview-views','#design-frame','#design-room-hero','#design-output-title','#design-nav','#design-room-photo-state','#design-customize','.material-choices','#room-inventory','.room-entity','#room-icon-current','.room-local-card>.hint','#saved-list','.draft-row','#ha-list','.ha-item button'];return {viewport:{width:innerWidth,height:innerHeight},fullPage:true,scroll:{x:scrollX,y:scrollY},document:{width:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight},elements:Object.fromEntries(selectors.map(s=>[s,[...document.querySelectorAll(s)].map(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,scrollTop:e.scrollTop,display:getComputedStyle(e).display}})]))}}''')
  (OUT/(name+'.geometry.json')).write_text(json.dumps(geometry,indent=2)+'\n')
 def two_views(self):
  p=self.p
  for area,title,ico in [('a','Fixture-Ansicht A','mdi:sofa'),('b','Fixture-Ansicht B','mdi:bed')]:
   p.locator('[data-area="'+area+'"]').click();p.locator('#room-title').fill(title);p.locator('#room-icon').select_option(ico)
  p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert')
 def global_photo(self):
  p=self.p;p.locator('[data-step="1"]').click();p.locator('[data-tab="background"]').click();p.locator('#image-file').set_input_files({'name':'KI-generiertes Stilbeispiel · Test.jpg','mimeType':'image/jpeg','buffer':(pathlib.Path(__file__).resolve().parents[2]/'lumo_raumstudio/sample-noir.jpg').read_bytes()});expect(p.locator('#image-choice option:checked')).to_contain_text('Test');p.locator('#save').click();expect(p.locator('#dirty-label')).to_contain_text('gespeichert');p.locator('[data-tab="general"]').click();p.reload();expect(p.locator('#selected-title')).to_be_visible()
 def test_rv01_global_photo_title_navigation_and_external_hint(self):
  self.two_views();self.global_photo();p=self.p
  for w,h in [(1326,735),(768,1024),(390,844)]:
   p.set_viewport_size({'width':w,'height':h});p.locator('#preview').scroll_into_view_if_needed();self.shot('rv01-'+str(w))
   photo=self.bounds('#preview');nav=self.bounds('#preview-views');hint=self.bounds('#preview-empty')
   self.assertGreaterEqual(hint['y'],photo['y']+photo['height'],'Erhaltungshinweis must not cover the photograph')
   self.assertGreater(nav['y'],photo['y']+photo['height']*.5)
   self.assertEqual(p.locator('#preview-title').evaluate('e=>getComputedStyle(e).color'),'rgb(255, 255, 255)')
   self.assertIn('api/images/',p.locator('#preview-image').evaluate('e=>getComputedStyle(e).backgroundImage'))
   self.assertEqual(p.locator('#preview-views button').count(),2);p.locator('#preview-views button').last.click();expect(p.locator('#preview-empty')).to_contain_text('Fixture-Ansicht B')
   self.assertFalse(p.evaluate('document.documentElement.scrollWidth>innerWidth'))
 def test_rv02_photo_title_lower_navigation_and_caption(self):
  p=self.p;p.set_viewport_size({'width':1486,'height':838});self.two_views();p.locator('#room-next').click();expect(p.locator('#design-status')).to_contain_text('Frisch');p.locator('[data-adjust="background"]').click();p.locator('#design-use-sample').click();p.locator('#dialog-confirm').click();expect(p.locator('#design-room-hero')).to_have_attribute('data-photo-state','ready');p.locator('#design-save').click();expect(p.locator('#design-dirty')).to_contain_text('Gespeichert');p.locator('[data-adjust="style"]').click();self.shot('rv02-desktop')
  hero=self.bounds('#design-room-hero');nav=self.bounds('#design-nav');title=self.bounds('#design-output-title');frame=self.bounds('#design-frame');caption=self.bounds('#design-room-photo-state')
  self.assertGreater(nav['y'],hero['y']+hero['height']*.5,'Existing navigation belongs in lower photograph, not above it')
  self.assertGreaterEqual(title['height'],26);self.assertLessEqual(caption['y']+caption['height'],frame['y']+frame['height'])
  self.assertEqual(p.locator('#design-nav button').count(),2)
  p.locator('#design-fullscreen').click();self.shot('rv02-fullscreen');p.keyboard.press('Escape')
  for target,w,h,orientation in [('phone',390,844,'portrait'),('phone',844,390,'landscape'),('tablet',768,1024,'portrait'),('tablet',1024,768,'landscape')]:
   p.set_viewport_size({'width':w,'height':h});p.locator('[data-design-panel="preview"]').click();p.locator('[data-preview-target="'+target+'"]').click();p.locator('[data-design-panel="settings"]').click()
   if not p.locator('#design-display-advanced').evaluate('e=>e.open'):p.locator('#design-display-advanced>summary').click()
   p.locator('#design-orientation').select_option(orientation);p.locator('[data-design-panel="preview"]').click();p.locator('#design-frame').scroll_into_view_if_needed();self.shot('rv02-'+target+'-'+orientation)
   hero=self.bounds('#design-room-hero');nav=self.bounds('#design-nav');frame=self.bounds('#design-frame');output=self.bounds('#design-output');caption=self.bounds('#design-room-photo-state');self.assertLessEqual(caption['y']+caption['height'],min(frame['y']+frame['height'],output['y']+output['height']),'Caption must fit the real target viewport too, not just the outer editor frame');self.assertGreater(nav['y'],hero['y']+hero['height']*.4);self.assertFalse(p.evaluate('document.documentElement.scrollWidth>innerWidth'))
   p.locator('#design-inspection>summary').click();p.locator('#design-one').check();p.locator('#design-inspection>summary').click();p.locator('#design-room-photo-state').scroll_into_view_if_needed();self.shot('rv02-one-'+target+'-'+orientation);expect(p.locator('#design-room-photo-state')).to_be_visible();p.locator('#design-inspection>summary').click();p.locator('#design-one').uncheck();p.locator('#design-inspection>summary').click();self.assertEqual(p.locator('#design-frame').evaluate('e=>e.scrollTop'),0,'Returning from 1:1 must show the complete fitted photograph, not retained clipped scroll')
  p.set_viewport_size({'width':1486,'height':838});p.locator('[data-preview-target="desktop"]').click();p.locator('#design-save').click();expect(p.locator('#design-dirty')).to_contain_text('Gespeichert');p.locator('[data-step="1"]').click();p.locator('#edit-name').fill('Sehr langer Dashboardname mit vielen Wörtern und einer langen Raumansicht');p.locator('#save').click();expect(p.locator('#dirty-label')).to_contain_text('gespeichert');p.locator('[data-step="2"]').click();p.locator('#room-title').fill('Eine sehr lange Raumansicht mit vielen Wörtern für die überprüfte Navigation');p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');p.locator('#room-next').click();expect(p.locator('#design-status')).to_contain_text('Frisch');expect(p.locator('#design-output-title')).to_contain_text('Sehr langer Dashboardname');expect(p.locator('#design-room-hero')).to_have_attribute('data-photo-state','ready');self.shot('rv02-long');caption=self.bounds('#design-room-photo-state');frame=self.bounds('#design-frame');self.assertLessEqual(caption['y']+caption['height'],frame['y']+frame['height']);self.assertEqual(p.locator('#design-cards').count(),1)
 def test_rv03_expanded_device_first_entity_visible_and_selectable(self):
  p=self.p;p.set_viewport_size({'width':1483,'height':835});p.locator('[data-area="a"]').click();p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');p.reload();p.locator('[data-step="2"]').click();expect(p.locator('#room-status')).to_contain_text('Frisch');p.locator('[data-expand]').first.click();p.locator('[data-inspect-entity="registry:reg1"]').click();p.locator('#room-inventory').evaluate('e=>e.scrollTo(0,0)');self.shot('rv03-expanded-properties')
  inventory=self.bounds('#room-inventory');row=self.bounds('.room-entity[data-entity="registry:reg1"]');self.assertGreaterEqual(inventory['height'],180,'Inventory needs useful room, not toolbar-dominated residual height');self.assertGreaterEqual(row['y'],inventory['y']);self.assertLessEqual(row['y']+row['height'],inventory['y']+inventory['height'])
  p.locator('[data-entity-check="registry:reg1"]').check();p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');self.assertTrue(any(r['key']=='registry:reg1' for r in self.f.store.list('alice')[0]['roomPlan']['views'][0]['entityRefs']))
  p.locator('#room-selection-menu>summary').click();expect(p.locator('#room-select-visible')).to_be_visible();p.locator('#room-select-visible').click();expect(p.locator('#room-dirty')).to_contain_text('Ungespeicherte');p.locator('#room-selection-menu>summary').click();expect(p.locator('#room-select-visible')).to_be_hidden();expect(p.locator('#room-search')).to_be_visible();expect(p.locator('#room-scope')).to_be_visible();expect(p.locator('#room-result-count')).to_contain_text('Auswahl bleibt')
 def import_peer(self):
  from peer import Peer
  self.f.stop();self.f.peer.close();self.f.peer=Peer();self.f.start();self.p.reload();expect(self.p.locator('#selected-title')).to_be_visible()
 def test_rv04_binding_icons_hint_material_and_read_status(self):
  p=self.p;p.set_viewport_size({'width':1483,'height':835});p.locator('[data-area="a"]').click();p.locator('#room-icon').select_option('mdi:sofa');self.shot('rv04-room-controls')
  with self.subTest(control='selected-icon'):expect(p.locator('#room-icon-current svg[data-icon="mdi:sofa"]')).to_be_visible(timeout=1500)
  with self.subTest(control='source-mark'):self.assertEqual(p.locator('.room-source-card>h3 svg').evaluate('e=>getComputedStyle(e).backgroundColor'),'rgb(8, 174, 224)')
  with self.subTest(control='visibility-hint'):expect(p.locator('.room-local-card>.hint')).to_be_visible(timeout=1500);expect(p.locator('.room-local-card>.hint')).to_contain_text('Zugriffsschutz')
  p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');p.locator('#room-next').click();expect(p.locator('#design-status')).to_contain_text('Frisch');self.shot('rv04-material-initial');choices=self.bounds('.material-choices');custom=self.bounds('#design-customize');self.assertLessEqual(choices['y']+choices['height'],custom['y']+custom['height'],'Material segments must initially fit the clean desktop adjustment area');p.locator('.material-choices').scroll_into_view_if_needed();self.shot('rv04-material-segments')
  with self.subTest(control='material-segments'):
   for value in ['flat','glass','soft','layered']:
    radio=p.locator('input[data-material="'+value+'"]');label=radio.locator('..');self.assertGreaterEqual(label.bounding_box()['height'],32);expect(label.locator('svg')).to_be_visible(timeout=1500);self.assertNotEqual(label.evaluate('e=>getComputedStyle(e).borderStyle'),'none')
   p.locator('[data-material="glass"]').focus();p.keyboard.press('Space');expect(p.locator('#design-output')).to_have_attribute('data-material','glass');p.keyboard.press('ArrowRight');expect(p.locator('#design-output')).to_have_attribute('data-material','soft');expect(p.locator('#design-material-note')).to_contain_text('native')
  p.locator('#design-save').click();expect(p.locator('#design-dirty')).to_contain_text('Gespeichert');p.locator('[data-step="1"]').click();self.import_peer();p.locator('#load-ha').click();expect(p.locator('#ha-list')).to_contain_text('übernehmen');self.shot('rv04-import-read-status')
  with self.subTest(control='verified-read-status'):expect(p.locator('#connection svg')).to_have_count(1,timeout=1500);expect(p.locator('#connection')).to_have_attribute('data-verified','true')
  self.f.peer.users=[];p.locator('#load-ha').click();expect(p.locator('#notice')).to_have_class('error');expect(p.locator('#connection')).to_have_attribute('data-verified','false');expect(p.locator('#connection svg')).to_have_count(0)
 def test_rv05_compact_drafts_and_ha_copy_keep_actions_and_targets(self):
  p=self.p;self.two_views();self.global_photo();p.set_viewport_size({'width':1326,'height':735})
  for name in ['Fixture zweiter Entwurf','Fixture dritter Entwurf']:self.f.store.create('alice',name,'mdi:home')
  p.reload();expect(p.locator('.draft-row')).to_have_count(3);p.evaluate('scrollTo(0,0)');self.shot('rv05-multiple-drafts')
  with self.subTest(control='compact-drafts'):
   self.assertEqual(p.locator('.draft-actions[open]').count(),0,'Secondary actions must start grouped, not all unfolded')
   boxes=p.locator('.draft-row').evaluate_all('es=>es.map(e=>{const r=e.getBoundingClientRect();return {top:r.top,bottom:r.bottom,height:r.height}})');container=self.bounds('#saved-list');self.assertLessEqual(boxes[2]['bottom'],container['y']+container['height']);self.assertLessEqual(max(b['height'] for b in boxes),86)
  target=p.locator('.draft-row').filter(has_text='Fixture zweiter Entwurf');target.get_by_role('button',name='Öffnen',exact=True).click();expect(p.locator('#edit-name')).to_have_value('Fixture zweiter Entwurf');expect(target).to_have_attribute('data-active','true');p.locator('#edit-description').fill('Ungespeicherter lokaler Text')
  if not target.locator('details').evaluate('e=>e.open'):target.locator('summary').click()
  target.get_by_role('button',name='Duplizieren',exact=True).click();p.locator('#dialog-cancel').click();self.assertEqual(len(self.f.store.list('alice')),3);target.get_by_role('button',name='Duplizieren',exact=True).click();p.locator('#dialog-discard').click();expect(p.locator('#notice')).to_contain_text('Kopie gespeichert');self.assertEqual(len(self.f.store.list('alice')),4);expect(p.locator('#selected-title')).to_contain_text('Fixture zweiter Entwurf');self.assertEqual(self.f.store.list('alice')[0]['description'],'')
  self.import_peer();p.locator('#load-ha').click();expect(p.locator('#ha-list')).to_contain_text('übernehmen');p.evaluate('scrollTo(0,0)');self.shot('rv05-loaded-ha')
  with self.subTest(control='compact-ha'):
   panel=self.bounds('#dashboard-step .ha');copy=p.locator('.ha-item button').first.bounding_box();self.assertLessEqual(copy['y']+copy['height'],panel['y']+panel['height']-4,'First actual copy action must fit inside HA card without scrolling');self.assertGreaterEqual(copy['height'],32)
  p.locator('.ha-item button').first.click();expect(p.locator('#import-detail')).to_be_visible();expect(p.locator('#native-export')).to_be_visible();self.shot('rv05-import-report')
  with p.expect_download() as download:p.locator('#native-export').click()
  self.assertEqual(json.loads(pathlib.Path(download.value.path()).read_text()),self.f.peer.configs[None]);self.assertFalse(any(c['type'].endswith('/update') or c['type']=='call_service' for c in self.f.peer.commands))
 def test_code01_fullscreen_real_links_guards_and_focus(self):
  p=self.p;p.set_viewport_size({'width':1486,'height':838})
  # Reuse independent reviewer repro's two actual links, then dirty outcomes.
  for pane,target,dest,step in [('background','#design-background-link','#dashboard-step','1'),('navigation','#design-navigation-pane button','#room-step','2')]:
   for decision in ['clean','cancel','discard','confirm']:
    with self.subTest(pane=pane,decision=decision):
     p.reload();expect(p.locator('#selected-title')).to_be_visible();p.locator('[data-step="3"]').click();expect(p.locator('#design-status')).to_contain_text('Frisch')
     saved=self.f.store.list('alice')[0];before=saved.get('design');revision=saved['revision']
     if decision!='clean':
      p.locator('[data-adjust="style"]').click();p.locator('#design-override-radius').fill('23' if (before or {}).get('overrides',{}).get('radius')!=23 else '24');p.locator('#design-override-radius').dispatch_event('change')
     p.locator('#design-fullscreen').click();p.locator('[data-adjust="'+pane+'"]').click();p.locator(target).click()
     if decision!='clean':
      expect(p.locator('#dialog')).to_be_visible();p.locator('#dialog-'+decision).click()
     if decision=='cancel':
      expect(p.locator('#design-step')).to_have_class('preview-fullscreen');expect(p.locator(target)).to_be_focused();self.assertTrue(p.locator('.steps').evaluate('e=>e.inert'));self.assertEqual(self.f.store.list('alice')[0].get('design'),before)
      self.shot('code01-'+pane+'-cancel');p.locator(target).click();p.locator('#dialog-discard').click()
     expect(p.locator(dest)).to_be_visible();self.shot('code01-'+pane+'-'+decision)
     self.assertFalse(p.locator('#design-step').evaluate('e=>e.classList.contains("preview-fullscreen")'),'Invisible fullscreen must close on actual step transition')
     self.assertEqual(p.locator('[inert]').count(),0);expect(p.locator('.design-center')).not_to_have_attribute('aria-modal','true');expect(p.locator('#design-fullscreen')).to_have_attribute('aria-expanded','false')
     self.assertTrue(p.evaluate('()=>document.activeElement!==document.body && !!document.activeElement.getClientRects().length && !document.activeElement.closest("[hidden],[inert]")'))
     actual=self.f.store.list('alice')[0]
     if decision=='confirm':self.assertEqual(actual['revision'],revision+1);self.assertNotEqual(actual.get('design'),before)
     else:self.assertEqual(actual.get('design'),before);self.assertEqual(actual['revision'],revision)
     p.locator('#studio-help').click();expect(p.locator('#help-dialog')).to_be_visible();p.keyboard.press('Escape');p.locator('[data-step="'+step+'"]').click()
  self.assertFalse(any(c['type'].endswith('/update') or c['type']=='call_service' for c in self.f.peer.commands))
