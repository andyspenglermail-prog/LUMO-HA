"""RV-02A: real decoded photo composition against BOTH client clip edges."""
import json,os,pathlib,unittest
import test_review_fix2 as prior
from playwright.sync_api import expect
OUT=pathlib.Path(os.environ['RAUMSTUDIO_EVIDENCE'])/'fix3'
GEOMETRY=r'''()=>{
 const out=document.querySelector('#design-output'),scale=out.getBoundingClientRect().width/out.offsetWidth;
 const box=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e),z=e===document.querySelector('#design-frame')?1:scale;return {left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height,clip:{left:r.left+e.clientLeft*z,top:r.top+e.clientTop*z,right:r.left+(e.clientLeft+e.clientWidth)*z,bottom:r.top+(e.clientTop+e.clientHeight)*z},text:e.textContent,cssWidth:s.width,cssHeight:s.height,gridRows:s.gridTemplateRows,padding:s.padding,margin:s.margin,scroll:[e.scrollLeft,e.scrollTop]};};
 const selectors=['#design-frame','#design-output','#design-room-hero','#design-output-title','#design-view-title','.design-room-caption','#design-room-photo-state','#design-nav','.design-output-header'];
 return {scale,short:out.dataset.short,boxes:Object.fromEntries(selectors.map(s=>[s,box(document.querySelector(s))])),nav:[...document.querySelectorAll('#design-nav button')].map(box),cards:[...document.querySelectorAll('.design-card')].map(e=>({entity:e.dataset.entity,text:e.textContent})),images:[...document.querySelectorAll('#design-room-photo img')].map(i=>({complete:i.complete,naturalWidth:i.naturalWidth,src:i.src})),focus:document.activeElement.id};
}'''
class ReviewFix3Tests(unittest.TestCase):
 setUp=prior.ReviewFix2Tests.setUp
 tearDown=prior.ReviewFix2Tests.tearDown
 two_views=prior.ReviewFix2Tests.two_views
 photo_fixture=prior.ReviewFix2Tests.photo_fixture
 profile_photo=prior.ReviewFix2Tests.profile_photo
 phone_landscape=prior.ReviewFix2Tests.phone_landscape
 def target(self,width,height):
  p=self.p
  if p.viewport_size['width']<=1100:p.locator('[data-design-panel="settings"]').click()
  if not p.locator('#design-display-advanced').evaluate('e=>e.open'):p.locator('#design-display-advanced>summary').click()
  p.locator('#design-orientation').select_option('auto')
  for key,value in [('width',width),('height',height)]:
   p.locator('#design-'+key).fill(str(value));p.locator('#design-'+key).dispatch_event('change')
  if p.viewport_size['width']<=1100:p.locator('[data-design-panel="preview"]').click()
 def capture(self,name):
  p=self.p;OUT.mkdir(parents=True,exist_ok=True)
  p.wait_for_function("()=>[...document.images].filter(i=>i.getClientRects().length).every(i=>i.complete&&i.naturalWidth>0)")
  p.evaluate("async()=>{await Promise.all([...document.images].filter(i=>i.getClientRects().length).map(i=>i.decode()));await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))}")
  p.locator('#design-frame').scroll_into_view_if_needed();g=p.evaluate(GEOMETRY)
  (OUT/(name+'.json')).write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
  p.locator('#design-frame').screenshot(path=str(OUT/(name+'.png')))
  return g
 def contained(self,g,width,height,nav_count=2):
  b=g['boxes'];out=b['#design-output'];self.assertEqual(out['cssWidth'],str(width)+'px');self.assertEqual(out['cssHeight'],str(height)+'px');self.assertEqual(len(g['nav']),nav_count)
  self.assertEqual(out['scroll'],[0,0]);self.assertEqual(b['#design-frame']['scroll'],[0,0])
  elements=[b[s] for s in ['#design-output-title','#design-view-title','.design-room-caption','#design-room-photo-state']]+g['nav']
  for edge in ['#design-output','#design-frame']:
   clip=b[edge]['clip']
   for item in elements:
    for side in ['left','top']:self.assertGreaterEqual(item[side],clip[side],edge+' clips '+side+' '+item['text'])
    for side in ['right','bottom']:self.assertLessEqual(item[side],clip[side],edge+' clips '+side+' '+item['text'])
  self.assertIn('KI-generiertes Stilbeispiel',b['#design-room-photo-state']['text'])
  self.assertTrue(any(c['entity']=='registry:reg1' and 'Fixture' in c['text'] for c in g['cards']))
  self.assertTrue(all(i['complete'] and i['naturalWidth']>0 for i in g['images']))
  self.assertFalse(self.p.evaluate('document.documentElement.scrollWidth>innerWidth'))
 def test_rv02a_exact_height_budget_long_names(self):
  self.photo_fixture();p=self.p
  for profile in ['noir','ivory','smart']:
   self.profile_photo(profile);self.phone_landscape()
   # 500 first: reproduces actual clipping, unlike the historical state-only boundary check.
   for height in [500,390,499,501,600]:
    self.target(844,height)
    for full in [False,True]:
     if full:p.locator('#design-fullscreen').click()
     name=profile+'-'+str(height)+('-full' if full else '-normal');g=self.capture(name)
     with self.subTest(profile=profile,height=height,fullscreen=full):self.contained(g,844,height)
     if full:p.keyboard.press('Escape')
  self.assertFalse(any(c['type'].endswith('/update') or c['type']=='call_service' for c in self.f.peer.commands))
 def one_to_fit(self,name,width,height,nav_count=2):
  p=self.p;p.locator('#design-inspection>summary').click();p.locator('#design-one').check();p.locator('#design-inspection>summary').click()
  self.assertEqual(p.locator('#design-output').evaluate('e=>getComputedStyle(e).transform'),'matrix(1, 0, 0, 1, 0, 0)')
  for button in p.locator('#design-nav button').all():self.assertGreaterEqual(button.bounding_box()['height'],80)
  p.locator('.design-card[data-entity="registry:reg1"]').scroll_into_view_if_needed();expect(p.locator('.design-card[data-entity="registry:reg1"]')).to_contain_text('Fixture')
  p.screenshot(path=str(OUT/(name+'-one-card.png')))
  p.locator('#design-inspection>summary').click();p.locator('#design-one').uncheck();p.locator('#design-inspection>summary').click()
  self.contained(self.capture(name+'-returned-fit'),width,height,nav_count)
 def test_content_switch_neighbors_and_long_orientations(self):
  self.photo_fixture();p=self.p;boundaries=[]
  for profile in ['noir','ivory','smart']:
   self.profile_photo(profile);self.phone_landscape()
   # Find actual content-driven transition using only the public display fields.
   lo,hi=600,843
   self.target(844,lo);self.assertEqual(p.locator('#design-output').get_attribute('data-short'),'true')
   self.target(844,hi);self.assertEqual(p.locator('#design-output').get_attribute('data-short'),'false')
   while hi-lo>1:
    mid=(lo+hi)//2;self.target(844,mid)
    if p.locator('#design-output').get_attribute('data-short')=='true':lo=mid
    else:hi=mid
   boundaries.append({'profile':profile,'firstUncompactedHeight':hi})
   for height in [hi-1,hi,hi+1]:
    self.target(844,height)
    for full in [False,True]:
     if full:p.locator('#design-fullscreen').click()
     g=self.capture(profile+'-switch-'+str(height)+'-'+str(full));self.contained(g,844,height);self.assertEqual(g['short'],'true' if height<hi else 'false')
     if full:p.keyboard.press('Escape')
   # Locate the decorative spacer's own measured limiting boundary as well.
   lo,hi=390,499
   if p.locator('#design-output').evaluate('e=>e.style.getPropertyValue("--d-photo-space")'):self.fail('unexpected residual spacer')
   self.target(844,lo)
   if p.locator('#design-output').evaluate('e=>e.style.getPropertyValue("--d-photo-space")'):
    while hi-lo>1:
     mid=(lo+hi)//2;self.target(844,mid)
     if p.locator('#design-output').evaluate('e=>e.style.getPropertyValue("--d-photo-space")'):lo=mid
     else:hi=mid
    boundaries[-1]['firstFullSpacerHeight']=hi
    for height in [hi-1,hi,hi+1]:
     self.target(844,height)
     for full in [False,True]:
      if full:p.locator('#design-fullscreen').click()
      self.contained(self.capture(profile+'-spacer-'+str(height)+'-'+str(full)),844,height)
      if full:p.keyboard.press('Escape')
   for w,h,target in [(390,844,'phone'),(768,1024,'tablet'),(1024,768,'tablet'),(1486,838,'desktop')]:
    p.set_viewport_size({'width':w,'height':h})
    if w<=1100:p.locator('[data-design-panel="preview"]').click()
    p.locator('[data-preview-target="'+target+'"]').click();self.target(w,h)
    for full in [False,True]:
     if full:p.locator('#design-fullscreen').click()
     name=profile+'-long-'+str(w)+'x'+str(h)+'-'+str(full);g=self.capture(name);self.contained(g,w,h)
     if target=='desktop':self.assertEqual(g['short'],'false')
     self.one_to_fit(name,w,h)
     if full:p.keyboard.press('Escape')
  (OUT/'boundaries.json').write_text(json.dumps(boundaries,indent=2))
 def test_short_names_single_and_multi_view_regressions(self):
  self.photo_fixture();p=self.p
  # Real persisted names, same entity; no synthetic DOM replacement or product mocks.
  p.locator('[data-step="1"]').click();p.locator('#edit-name').fill('Fixture');p.locator('#save').click();expect(p.locator('#dirty-label')).to_contain_text('gespeichert')
  p.locator('[data-step="2"]').click();expect(p.locator('#room-status')).to_contain_text('Frisch');p.locator('[data-area="a"]').click();p.locator('#room-title').fill('A');p.locator('[data-area="b"]').click();p.locator('#room-title').fill('B');p.locator('[data-area="a"]').click();p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');p.locator('#room-next').click();expect(p.locator('#design-status')).to_contain_text('Frisch')
  neutral=[]
  for count in [2,1]:
   if count==1:
    p.locator('#design-save').click();expect(p.locator('#design-dirty')).to_contain_text('Gespeichert');p.locator('[data-step="2"]').click();expect(p.locator('#room-status')).to_contain_text('Frisch');p.locator('[data-area="b"]').click();p.locator('#room-visible').uncheck();p.locator('[data-area="a"]').click();p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');p.locator('#room-next').click();expect(p.locator('#design-status')).to_contain_text('Frisch')
   for profile in ['noir','ivory','smart']:
    self.profile_photo(profile)
    neutral.append(p.locator('#design-room-image').evaluate('e=>{const s=getComputedStyle(e);return [s.color,s.backgroundColor,s.fontFamily,s.borderRadius]}'))
    for w,h,target in [(844,390,'phone'),(844,500,'phone'),(390,844,'phone'),(1024,768,'tablet'),(1486,838,'desktop')]:
     p.set_viewport_size({'width':w,'height':h})
     if w<=1100:p.locator('[data-design-panel="preview"]').click()
     p.locator('[data-preview-target="'+target+'"]').click();self.target(w,h)
     for full in [False,True]:
      if full:p.locator('#design-fullscreen').click()
      name=profile+'-short-'+str(count)+'views-'+str(w)+'x'+str(h)+'-'+str(full);g=self.capture(name);self.contained(g,w,h,2 if count==2 else 0)
      if count==1:expect(p.locator('#design-nav')).to_be_hidden()
      if h==500 or target=='desktop':self.assertEqual(g['short'],'false','Short names must not inherit long-content breakpoint')
      if full:p.keyboard.press('Escape')
     if w==844 and h==390:self.one_to_fit(name,w,h,2 if count==2 else 0)
  self.assertTrue(all(n==neutral[0] for n in neutral),'Editor styles must remain neutral across profiles')
  self.assertFalse(any(c['type'].endswith('/update') or c['type']=='call_service' for c in self.f.peer.commands))
