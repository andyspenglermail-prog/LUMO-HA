"""Viewport matrix with actual emulated touch and unscaled target geometry."""
import pathlib,sys,unittest,json,os
sys.path.insert(0,str(pathlib.Path(__file__).parent))
import test_design_browser as setup_module
from playwright.sync_api import expect
OUT=pathlib.Path(os.environ.get('RAUMSTUDIO_EVIDENCE','/workspace/lumo-auftrag03-evidence/implementation/browser'))/'design-matrix'
class DesignMatrixTests(unittest.TestCase):
 setUp=setup_module.DesignBrowserTests.setUp
 tearDown=setup_module.DesignBrowserTests.tearDown
 def test_long_labels_empty_views_and_high_contrast_have_no_target_overflow(self):
  p=self.page;d=self.f.store.update('alice',self.before['id'],self.before['revision'],{'name':'W'*80});p.reload();p.locator('[data-step="3"]').click();expect(p.locator('#design-status')).to_contain_text('Frisch gelesen');p.locator('[data-target="phone"]').check();p.locator('#design-active-target').select_option('phone');p.locator('#design-high-contrast').check();self.assertEqual(p.locator('.design-card').first.evaluate('(e)=>getComputedStyle(e).color'),'rgb(0, 0, 0)');self.assertEqual(p.locator('.design-card').first.evaluate('(e)=>getComputedStyle(e).backgroundColor'),'rgb(255, 255, 255)');self.assertTrue(p.locator('#design-output').evaluate('(e)=>e.scrollWidth<=e.clientWidth'))
  p.locator('[data-step="1"]').click();p.locator('#dialog-discard').click();self.f.store.create('alice','Empty view fixture');p.reload();p.locator('.draft-row').filter(has_text='Empty view fixture').get_by_role('button',name='Öffnen',exact=True).click();p.locator('[data-step="3"]').click();expect(p.locator('#design-cards')).to_contain_text('Noch keine sichtbare Raumansicht');expect(p.locator('#design-cards [data-entity]')).to_have_count(0)
 def test_desktop_panels_and_actions_fit_viewport_without_overlap(self):
  p=self.page;expect(p.locator('#design-status')).to_contain_text('Frisch gelesen');p.set_viewport_size({'width':1500,'height':900});p.evaluate('()=>window.scrollTo(0,0)');r=p.locator('.design-columns').bounding_box();bar=p.locator('.design-savebar').bounding_box();self.assertLess(r['y'],320);self.assertLessEqual(r['y']+r['height'],bar['y']+1);self.assertLessEqual(bar['y']+bar['height'],900)
 def test_all_themes_desktop_tablet_phone_wall_touch_reflow(self):
  OUT.mkdir(parents=True,exist_ok=True);rows=[]
  # Separate contexts: actual DPR / touch, not a label in the target form.
  for target,w,h,dpr,touch,columns in [('desktop',1440,900,1,False,5),('tablet',1024,768,2,True,3),('phone',390,844,3,True,1),('wall',1920,1080,1,True,5)]:
   ctx=self.b.new_context(viewport={'width':w,'height':h},device_scale_factor=dpr,has_touch=touch,is_mobile=target=='phone',extra_http_headers={'X-Remote-User-Id':'alice'});p=ctx.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto(self.proxy.url);action='tap' if touch else 'click';getattr(p.get_by_role('button',name='Öffnen',exact=True),action)();getattr(p.locator('[data-step="3"]'),action)();expect(p.locator('#design-status')).to_contain_text('Frisch gelesen')
   for theme in ('noir','ivory','smart'):
    if w<=1100:getattr(p.locator('[data-design-panel="catalog"]'),action)()
    p.locator('#design-category').select_option('Smart & Functional' if theme=='smart' else 'Luxury & Signature');getattr(p.locator('[data-design-profile="'+theme+'"]'),action)()
    if w<=1100:getattr(p.locator('[data-design-panel="settings"]'),action)()
    if target!='desktop' and not p.locator('[data-target="'+target+'"]').is_checked():getattr(p.locator('[data-target="'+target+'"]'),action)()
    p.locator('#design-active-target').select_option(target)
    if w<=1100:getattr(p.locator('[data-design-panel="preview"]'),action)()
    p.locator('#design-one').uncheck();p.locator('#design-frame').scroll_into_view_if_needed();self.assertFalse(p.evaluate('()=>document.documentElement.scrollWidth>innerWidth'));p.screenshot(path=str(OUT/f'{target}-{theme}.png'),full_page=True)
    getattr(p.locator('#design-one'),action)();expect(p.locator('#design-output')).to_have_css('width',str(w)+'px');grid=p.locator('#design-cards').evaluate('(e)=>getComputedStyle(e).gridTemplateColumns.split(" ").length');self.assertEqual(grid,columns)
    geometry=p.locator('#design-output button,#design-output summary').evaluate_all('(es)=>es.map(e=>{const r=e.getBoundingClientRect(),o=e.closest("#design-output").getBoundingClientRect();return {width:r.width,height:r.height,left:r.left-o.left,right:r.right-o.left}})')
    for g in geometry:self.assertGreaterEqual(g['height'],44);self.assertGreaterEqual(g['width'],44);self.assertGreaterEqual(g['left'],0);self.assertLessEqual(g['right'],w)
    # Real touch tap on output summary at 1:1, not scaled to an unusable hit target.
    getattr(p.locator('#design-cards details summary').first,action)();self.assertTrue(p.locator('#design-cards details').first.evaluate('(e)=>e.open'));getattr(p.locator('#design-cards details summary').first,action)()
    p.locator('#design-one').uncheck();rows.append({'theme':theme,'target':target,'observed':p.evaluate('()=>({width:innerWidth,height:innerHeight,dpr:devicePixelRatio,touch:navigator.maxTouchPoints,orientation:screen.orientation.type,engine:navigator.userAgent,zoom:visualViewport.scale})'),'targetMetrics':p.locator('#design-metrics').inner_text(),'columns':grid,'unscaledControls':geometry,'input':action,'errors':errors.copy()});self.assertEqual(errors,[])
   ctx.close()
  (OUT/'matrix.json').write_text(json.dumps(rows,indent=2))
if __name__=='__main__':unittest.main()
