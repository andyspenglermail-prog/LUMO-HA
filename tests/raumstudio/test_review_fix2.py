"""Last scoped repair: native modal priority and nested preview geometry."""
import copy,json,os,pathlib,unittest
import test_review_fix as prior
from playwright.sync_api import expect
OUT=pathlib.Path(os.environ['RAUMSTUDIO_EVIDENCE'])/'fix2'
class ReviewFix2Tests(unittest.TestCase):
 setUp=prior.ReviewFixTests.setUp
 tearDown=prior.ReviewFixTests.tearDown
 two_views=prior.ReviewFixTests.two_views
 def photo_fixture(self):
  p=self.p;p.set_viewport_size({'width':1486,'height':838});self.two_views();p.locator('[data-area="a"]').click();p.locator('[data-expand]').first.click();p.locator('[data-entity-check="registry:reg1"]').check();p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert')
  p.locator('[data-step="1"]').click();p.locator('#edit-name').fill('Sehr langer Dashboardname mit vielen Wörtern und einer langen Raumansicht');p.locator('#save').click();expect(p.locator('#dirty-label')).to_contain_text('gespeichert');p.locator('[data-step="2"]').click();expect(p.locator('#room-status')).to_contain_text('Frisch');p.locator('[data-area="a"]').click();p.locator('#room-title').fill('Eine sehr lange Raumansicht mit vielen Wörtern für die überprüfte Navigation');p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');p.locator('#room-next').click();expect(p.locator('#design-status')).to_contain_text('Frisch')
 def profile_photo(self,profile):
  p=self.p
  if p.viewport_size['width']<=1100:p.locator('[data-design-panel="catalog"]').click()
  p.locator('#design-category').select_option('Smart & Functional' if profile=='smart' else 'Luxury & Signature');p.locator('[data-design-profile="'+profile+'"]').click()
  if p.viewport_size['width']<=1100:p.locator('[data-design-panel="preview"]').click()
  p.locator('[data-adjust="background"]').click();p.locator('#design-use-sample').click();p.locator('#dialog-confirm').click();expect(p.locator('#design-room-image option:checked')).to_contain_text({'noir':'Noir Luxury','ivory':'Soft Ivory Premium','smart':'Smart Clean'}[profile]);expect(p.locator('#design-room-hero')).to_have_attribute('data-photo-state','ready');p.locator('#design-save').click();expect(p.locator('#design-dirty')).to_contain_text('Gespeichert')
 def phone_landscape(self):
  p=self.p;p.set_viewport_size({'width':844,'height':390});p.locator('[data-design-panel="preview"]').click();p.locator('[data-preview-target="phone"]').click();p.locator('[data-design-panel="settings"]').click()
  if not p.locator('#design-display-advanced').evaluate('e=>e.open'):p.locator('#design-display-advanced>summary').click()
  p.locator('#design-orientation').select_option('landscape');p.locator('[data-design-panel="preview"]').click()
 def capture(self,name):
  p=self.p;OUT.mkdir(parents=True,exist_ok=True)
  p.wait_for_function("()=>[...document.images].filter(i=>i.getClientRects().length).every(i=>i.complete&&i.naturalWidth>0)");p.evaluate("async()=>{await Promise.all([...document.images].filter(i=>i.getClientRects().length).map(i=>i.decode()));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))}");p.locator('#design-frame').scroll_into_view_if_needed()
  g=p.evaluate('''()=>{const box=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height,scrollTop:e.scrollTop,scrollLeft:e.scrollLeft,scrollWidth:e.scrollWidth,scrollHeight:e.scrollHeight,clientWidth:e.clientWidth,clientHeight:e.clientHeight,cssWidth:s.width,cssHeight:s.height,font:s.font,overflow:s.overflow,text:e.textContent}};return {viewport:{width:innerWidth,height:innerHeight},scroll:{x:scrollX,y:scrollY},boxes:Object.fromEntries(['#design-frame','#design-output','#design-room-hero','#design-output-title','#design-nav','#design-room-photo-state','#design-view-title','#design-cards'].map(s=>[s,box(document.querySelector(s))])),nav:[...document.querySelectorAll('#design-nav button')].map(box),images:[...document.querySelectorAll('#design-room-photo img')].map(i=>({src:i.src,complete:i.complete,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight}))}}''')
  (OUT/(name+'.json')).write_text(json.dumps(g,ensure_ascii=False,indent=2));p.screenshot(path=str(OUT/(name+'.viewport.png')));p.locator('#design-frame').screenshot(path=str(OUT/(name+'.frame.png')));return g
 def test_rv02a_combined_long_phone_landscape_all_profiles(self):
  self.photo_fixture();p=self.p
  for profile in ['noir','ivory','smart']:
   self.profile_photo(profile);self.phone_landscape()
   for full in [False,True]:
    if full:p.locator('#design-fullscreen').click()
    g=self.capture(profile+('-fullscreen' if full else '-normal')+'-long-fit');b=g['boxes'];out=b['#design-output'];frame=b['#design-frame']
    with self.subTest(profile=profile,fullscreen=full):
     self.assertEqual(out['cssWidth'],'844px');self.assertEqual(out['cssHeight'],'390px');self.assertEqual((out['scrollTop'],out['scrollLeft']),(0,0));self.assertEqual(len(g['nav']),2)
     for selector in ['#design-output-title','#design-view-title','#design-room-photo-state','#design-nav']:
      self.assertGreaterEqual(b[selector]['y'],max(out['y'],frame['y'])-1);self.assertLessEqual(b[selector]['bottom'],min(out['bottom'],frame['bottom'])+1,selector+' clipped by inner or outer viewport')
     self.assertIn('KI-generiertes Stilbeispiel',b['#design-room-photo-state']['text']);self.assertIn('registry:reg1',b['#design-cards']['text']);self.assertFalse(p.evaluate('document.documentElement.scrollWidth>innerWidth'))
    if full:p.keyboard.press('Escape')
   p.locator('#design-inspection>summary').click();p.locator('#design-one').check();p.locator('#design-inspection>summary').click()
   for button in p.locator('#design-nav button').all():self.assertGreaterEqual(button.bounding_box()['height'],80)
   p.locator('.design-card').first.scroll_into_view_if_needed();expect(p.locator('.design-card').first).to_contain_text('Fixture');self.capture(profile+'-card-one')
   p.locator('#design-inspection>summary').click();p.locator('#design-one').uncheck();p.locator('#design-inspection>summary').click()
   # Reset explicitly in this composition-only test; scroll-return is a separate contract.
   p.locator('#design-output').evaluate('e=>e.scrollTo(0,0)');p.locator('#design-frame').evaluate('e=>e.scrollTo(0,0)')
 def test_rv02b_explicit_fit_resets_nested_scroll_not_refresh(self):
  self.photo_fixture();p=self.p
  for profile in ['noir','ivory','smart']:
   self.profile_photo(profile);self.phone_landscape()
   for full in [False,True]:
    if full:p.locator('#design-fullscreen').click()
    p.locator('#design-inspection>summary').click();p.locator('#design-one').check();p.locator('#design-inspection>summary').click()
    # Exact reviewer UI sequence first, then actual selected function card.
    p.locator('#design-room-photo-state').scroll_into_view_if_needed();self.capture(profile+str(full)+'-caption-one')
    p.locator('.design-card').first.scroll_into_view_if_needed();before=self.capture(profile+str(full)+'-scrolled-one');self.assertGreater(before['boxes']['#design-output']['scrollTop'],0)
    p.locator('#design-refresh').click();expect(p.locator('#design-status')).to_contain_text('Frisch');after=self.capture(profile+str(full)+'-refreshed-one');self.assertEqual(after['boxes']['#design-output']['scrollTop'],before['boxes']['#design-output']['scrollTop'],'Read/render must not discard intentional 1:1 card scroll');self.assertTrue(p.locator('#design-one').is_checked())
    p.locator('#design-inspection>summary').click();p.locator('#design-one').uncheck();p.locator('#design-inspection>summary').click();g=self.capture(profile+str(full)+'-returned-fit');b=g['boxes']
    with self.subTest(profile=profile,fullscreen=full):
     for selector in ['#design-frame','#design-output']:self.assertEqual((b[selector]['scrollLeft'],b[selector]['scrollTop']),(0,0),'Explicit Fit resets both axes of '+selector)
     self.assertGreaterEqual(b['#design-output-title']['y'],max(b['#design-output']['y'],b['#design-frame']['y'])-1);self.assertLessEqual(b['#design-room-photo-state']['bottom'],min(b['#design-output']['bottom'],b['#design-frame']['bottom'])+1)
    if full:p.keyboard.press('Escape')
   p.locator('#design-output').evaluate('e=>e.scrollTo(0,0)')
 def test_code02_native_modal_priority_escape_tab_and_focus(self):
  p=self.p;p.set_viewport_size({'width':1486,'height':838});OUT.mkdir(parents=True,exist_ok=True);rows=[]
  for pane,target in [('background','#design-background-link'),('navigation','#design-navigation-pane button')]:
   p.reload();expect(p.locator('#selected-title')).to_be_visible();p.locator('[data-step="3"]').click();expect(p.locator('#design-status')).to_contain_text('Frisch')
   p.locator('#design-override-radius').fill('29');p.locator('#design-override-radius').dispatch_event('change');p.locator('#design-fullscreen').click();p.locator('[data-adjust="'+pane+'"]').click();p.locator(target).click();expect(p.locator('#dialog')).to_be_visible()
   stored=copy.deepcopy(self.f.store.list('alice'));before=p.evaluate("()=>({inert:[...document.querySelectorAll('[inert]')].map(e=>e.id||e.className),draft:JSON.stringify(designDraft)})")
   p.evaluate("()=>{window.guardKeys=[];window.guardCancels=0;document.addEventListener('keydown',e=>guardKeys.push({key:e.key,prevented:e.defaultPrevented,modal:document.querySelector('#dialog').open}));document.querySelector('#dialog').addEventListener('cancel',()=>guardCancels++);}")
   for key in ['Tab','Tab','Shift+Tab','Shift+Tab']:
    p.keyboard.press(key);self.assertTrue(p.evaluate("document.querySelector('#dialog').contains(document.activeElement)"))
   p.keyboard.press('Escape');p.wait_for_timeout(100)
   state=p.evaluate("()=>({dialog:document.querySelector('#dialog').open,full:document.querySelector('#design-step').classList.contains('preview-fullscreen'),aria:document.querySelector('.design-center').getAttribute('aria-modal'),inert:[...document.querySelectorAll('[inert]')].map(e=>e.id||e.className),draft:JSON.stringify(designDraft),keys:guardKeys,cancels:guardCancels})");rows.append({'pane':pane,'before':before,'after':state,'actualFocusID':p.evaluate('document.activeElement.id'),'targetIDAttribute':p.locator(target).get_attribute('id'),'focusedExactTarget':p.locator(target).evaluate('e=>document.activeElement===e')});(OUT/'modal.json').write_text(json.dumps(rows,indent=2))
   with self.subTest(pane=pane):
    self.assertFalse(state['dialog'],'Native Escape must cancel guard, not underlying fullscreen');self.assertTrue(state['full']);self.assertEqual(state['aria'],'true');self.assertEqual(state['inert'],before['inert']);self.assertEqual(state['draft'],before['draft']);self.assertEqual(state['cancels'],1);self.assertTrue(all(not e['prevented'] for e in state['keys']));expect(p.locator(target)).to_be_focused();self.assertEqual(self.f.store.list('alice'),stored)
    p.screenshot(path=str(OUT/(pane+'-escape-guard.png')));p.keyboard.press('Escape');expect(p.locator('#design-step')).not_to_have_class('preview-fullscreen');self.assertEqual(p.locator('[inert]').count(),0);expect(p.locator('.design-center')).not_to_have_attribute('aria-modal','true');expect(p.locator('#design-fullscreen')).to_be_focused();self.assertEqual(self.f.store.list('alice'),stored)
   if p.locator('#dialog').is_visible():p.locator('#dialog-cancel').click()
