"""Review regressions on actual browser/app/peer; no successful API stubs."""
import copy,json,os,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
import test_design_browser as setup_module
from playwright.sync_api import expect
OUT=pathlib.Path(os.environ.get('RAUMSTUDIO_EVIDENCE','/tmp/lumo-review-evidence'))/'design-review'

class DesignReviewBrowserTests(unittest.TestCase):
 setUp=setup_module.DesignBrowserTests.setUp
 tearDown=setup_module.DesignBrowserTests.tearDown
 def test_b2_nested_native_content_is_visibly_protected_and_bounded(self):
  f=self.f;p=self.page;OUT.mkdir(parents=True,exist_ok=True)
  def nested(kind,depth):
   card={'type':kind,'entity':'light.fixture','name':'Protected nested fixture','javascript':'throw Error("MUST NOT EXECUTE")'}
   for i in range(depth):card={'type':('vertical-stack','horizontal-stack','grid')[i%3],'cards':[card]}
   return card
  views=[{'title':f'Depth {depth} {kind}','cards':[nested(kind,depth)]} for depth in (8,9) for kind in ('tile','custom:fixture')]
  views.append({'title':'Section depth','sections':[{'cards':[nested('tile',9)]}]})
  views.append({'title':'Count limit','cards':[{'type':'tile','entity':f'sensor.fixture_{i}'} for i in range(2001)]})
  native={'views':views};d=f.store.import_native('alice','B2 fixture',native);url='/api/dashboards/'+d['id']
  def stored():
   with f.store.connect() as c:return c.execute('SELECT revision,document FROM dashboards WHERE id=?',(d['id'],)).fetchone()
  before=stored();export_before=p.request.get(self.proxy.url+url.lstrip('/'),headers={'X-LUMO-Read':'1'}).body()
  raw_before=p.request.get(self.proxy.url+url.lstrip('/')+'/export',headers={'X-LUMO-Read':'1'}).body();self.assertEqual(json.loads(raw_before),native)
  errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.reload();p.locator('.draft-row').filter(has_text='B2 fixture').get_by_role('button',name='Öffnen',exact=True).click();p.locator('[data-step="3"]').click();expect(p.locator('#design-status')).to_contain_text('Frisch gelesen')
  for i in range(5):
   with self.subTest(view=i):
    p.locator('#design-view').select_option(d['views'][i]['id']);p.screenshot(path=str(OUT/f'depth-view-{i}.png'),full_page=True)
    if i==0:expect(p.locator('#design-cards [data-entity]')).to_have_count(1)
    elif i==1:expect(p.locator('#design-cards')).to_contain_text('custom:fixture · geschützt')
    else:
     expect(p.locator('#design-cards .design-protected').filter(has_text='Verschachtelungsgrenze')).to_be_visible()
     expect(p.locator('#design-cards')).to_contain_text('Original bleibt vollständig erhalten')
     expect(p.locator('#design-cards [data-entity]')).to_have_count(0)
    expect(p.locator('#design-cards .design-empty')).to_have_count(0)
  status,r=f.request('GET',url+'/design');self.assertEqual(status,200)
  for source in r['sources'].values():self.assertLessEqual(len(source['refs'])+len(source['protected']),2001)
  limited=r['sources'][d['views'][5]['id']];self.assertTrue(limited['truncated']);self.assertEqual(len(limited['refs']),2000)
  self.assertEqual(stored(),before);self.assertEqual(f.store.get('alice',d['id']),d)
  self.assertEqual(p.request.get(self.proxy.url+url.lstrip('/'),headers={'X-LUMO-Read':'1'}).body(),export_before)
  self.assertEqual(p.request.get(self.proxy.url+url.lstrip('/')+'/export',headers={'X-LUMO-Read':'1'}).body(),raw_before);self.assertEqual(errors,[])
  (OUT/'depth-result.json').write_text(json.dumps({'views':5,'cardLimit':len(limited['refs']),'sourceBytesUnchanged':True,'rawExportUnchanged':True,'sources':r['sources'],'errors':errors},indent=2))

 def test_n1_zero_shadow_is_none_in_preview_and_pinned_native(self):
  import hashlib
  from urllib.parse import urlsplit
  import test_design_native_runtime as native_setup
  p=self.page;f=self.f;OUT.mkdir(parents=True,exist_ok=True);rows=[];network=[];errors=[];pins=json.loads((native_setup.CACHE/'asset-pins.json').read_text())
  native_ctx=self.b.new_context(viewport={'width':900,'height':600},service_workers='block');np=native_ctx.new_page()
  def route(r):
   u=r.request.url;pin=pins.get(u);network.append({'url':u,'cached':bool(pin),'method':r.request.method})
   if not pin or r.request.method!='GET' or '/cdn-cgi/' in u:r.abort();return
   raw=(native_setup.CACHE/'assets'/pin['sha256']).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),pin['sha256']);path=urlsplit(u).path;kind='text/html' if path=='/' else 'text/javascript' if path.endswith('.js') else 'application/json' if path.endswith('.json') else 'text/css' if path.endswith('.css') else 'application/octet-stream';r.fulfill(body=raw,content_type=kind)
  native_ctx.route('**/*',route);native_ctx.route_web_socket('**/*',lambda ws:ws.close())
  try:
   np.goto('https://demo.home-assistant.io/',wait_until='domcontentloaded');np.wait_for_function("()=>!!customElements.get('ha-card')");np.on('pageerror',lambda e:errors.append(str(e)));p.on('pageerror',lambda e:errors.append(str(e)))
   np.evaluate("()=>{document.querySelector('ha-demo')?.remove();document.body.replaceChildren();window.card=document.createElement('ha-card');card.header='Shadow review · synthetic fixture';card.style.cssText='width:700px;min-height:300px;margin:50px';document.body.append(card)}")
   expect(p.locator('#design-status')).to_contain_text('Frisch gelesen');p.locator('#design-customize summary').click();p.locator('#design-motion').select_option('subtle')
   for theme in ('noir','ivory','smart'):
    p.locator('#design-category').select_option('Smart & Functional' if theme=='smart' else 'Luxury & Signature');p.locator('[data-design-profile="'+theme+'"]').click()
    for shadow in (0,16):
     with self.subTest(theme=theme,shadow=shadow):
      p.locator('#design-override-shadow').fill(str(shadow));p.locator('#design-override-shadow').dispatch_event('change');p.locator('#design-save').click();expect(p.locator('#design-dirty')).to_contain_text('Gespeichert')
      d=f.store.get('alice',self.before['id']);self.assertEqual(d['design']['overrides']['shadow'],shadow)
      for key in ('roomPlan','native','views','settings'):self.assertEqual(d[key],self.before[key])
      status,m=f.request('GET','/api/dashboards/'+d['id']+'/design-native');self.assertEqual(status,200)
      np.evaluate("m=>{for(const key of [...card.style])if(key.startsWith('--'))card.style.removeProperty(key);for(const [k,v] of Object.entries(m.themes[m.themeName]))card.style.setProperty('--'+k,v)}",m)
      native_card=np.locator('ha-card');preview=p.locator('.design-card').first;p.mouse.move(0,0)
      if shadow==0:expect(native_card).to_have_css('box-shadow','none')
      else:expect(native_card).not_to_have_css('box-shadow','none')
      p.screenshot(path=str(OUT/f'shadow-{theme}-{shadow}-preview.png'),full_page=True);np.screenshot(path=str(OUT/f'shadow-{theme}-{shadow}-native.png'))
      if shadow==0:
       expect(preview).to_have_css('box-shadow','none');preview.hover();expect(preview).to_have_css('box-shadow','none');p.mouse.move(0,0)
      else:expect(preview).not_to_have_css('box-shadow','none')
      rows.append({'theme':theme,'shadow':shadow,'preview':preview.evaluate('(e)=>getComputedStyle(e).boxShadow'),'native':native_card.evaluate('(e)=>({shadow:getComputedStyle(e).boxShadow,constructor:e.constructor.name})'),'mapping':m})
      self.assertNotEqual(rows[-1]['native']['constructor'],'HTMLElement')
   self.assertEqual(errors,[]);(OUT/'shadow-result.json').write_text(json.dumps({'rows':rows,'network':network,'errors':errors,'installedHA':False},indent=2))
  finally:native_ctx.close()

 def test_n2_metrics_distinguish_pinch_scale_fit_and_target_dpr(self):
  p=self.page;OUT.mkdir(parents=True,exist_ok=True);expect(p.locator('#design-status')).to_contain_text('Frisch gelesen')
  p.locator('#design-dpr').fill('2');p.locator('#design-dpr').dispatch_event('change');cdp=self.ctx.new_cdp_session(p);rows=[]
  try:
   for pinch in (1,2):
    cdp.send('Emulation.setPageScaleFactor',{'pageScaleFactor':pinch})
    for one in (True,False):
     control=p.locator('#design-one')
     if control.is_checked()!=one:control.focus();control.press('Space')
     measured=p.evaluate("()=>({pinch:visualViewport.scale,browserDpr:devicePixelRatio,width:parseInt(document.querySelector('#design-output').style.width),height:parseInt(document.querySelector('#design-output').style.height),fit:new DOMMatrix(getComputedStyle(document.querySelector('#design-output')).transform).a})")
     self.assertAlmostEqual(measured['pinch'],pinch);self.assertEqual(measured['browserDpr'],1);self.assertEqual((measured['width'],measured['height']),(1440,900))
     text=p.locator('#design-metrics').inner_text();rows.append({'oneToOne':one,'measured':measured,'text':text})
     with self.subTest(pinch=pinch,oneToOne=one):
      self.assertIn(f'Visual-Viewport-/Pinch-Skala {pinch}',text);self.assertNotIn('Browser-Zoom',text);self.assertIn('Ziel-DPR 2 (Absicht, keine Emulation)',text);self.assertIn('Browser-DPR 1',text);self.assertIn('CSS-Viewport 1440 × 900',text);self.assertIn(f"Vorschauzoom {measured['fit']*100:.1f} %",text)
   p.screenshot(path=str(OUT/'metrics-pinch.png'),full_page=True)
   (OUT/'metrics-result.json').write_text(json.dumps(rows,indent=2))
  finally:cdp.send('Emulation.setPageScaleFactor',{'pageScaleFactor':1});cdp.detach()

if __name__=='__main__':unittest.main()
