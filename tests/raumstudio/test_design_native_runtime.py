"""Independent computed styles on pinned, unmodified official ha-card, not a fake div."""
import pathlib,sys,json,hashlib,os,tempfile,unittest
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'lumo_raumstudio'))
from store import Store
from test_rooms import RoomFixture
CACHE=pathlib.Path(os.environ.get('HA_NATIVE_CACHE','/workspace/lumo-core-usability-evidence/native-feasibility'))
OUT=pathlib.Path(os.environ.get('RAUMSTUDIO_EVIDENCE','/workspace/lumo-auftrag03-evidence/implementation/browser'))/'design-native'
class DesignNativeRuntimeTests(unittest.TestCase):
 def test_three_saved_sidecars_consumed_by_actual_official_card(self):
  f=RoomFixture();OUT.mkdir(parents=True,exist_ok=True)
  try:
   d=f.store.create('alice','Native synthetic');url='/api/dashboards/'+d['id'];status,m=f.request('GET',url+'/design-native');self.assertEqual(status,200,m)
   pins=json.loads((CACHE/'asset-pins.json').read_text());network=[];rows=[]
   with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True,args=['--no-sandbox']);ctx=b.new_context(viewport={'width':900,'height':600},service_workers='block');p=ctx.new_page()
    def route(r):
     u=r.request.url;pin=pins.get(u);network.append({'url':u,'cached':bool(pin),'method':r.request.method})
     if not pin or r.request.method!='GET' or '/cdn-cgi/' in u:r.abort();return
     raw=(CACHE/'assets'/pin['sha256']).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),pin['sha256']);path=urlsplit(u).path;kind='text/html' if path=='/' else 'text/javascript' if path.endswith('.js') else 'application/json' if path.endswith('.json') else 'text/css' if path.endswith('.css') else 'application/octet-stream';r.fulfill(body=raw,content_type=kind)
    ctx.route('**/*',route);ctx.route_web_socket('**/*',lambda ws:ws.close());p.goto('https://demo.home-assistant.io/',wait_until='domcontentloaded');p.wait_for_function("()=>!!customElements.get('ha-card')")
    errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.evaluate("()=>{document.querySelector('ha-demo')?.remove();document.body.replaceChildren();window.card=document.createElement('ha-card');card.header='Native Theme · synthetic fixture';card.style.cssText='width:700px;min-height:300px;margin:50px;';document.body.append(card);}")
    base=f.request('GET',url+'/design')[1]['design']
    for theme,color,background,radius,font in [('noir','rgb(247, 241, 229)','rgb(32, 41, 36)','16px','Georgia'),('ivory','rgb(56, 45, 34)','rgb(255, 250, 241)','28px','Trebuchet'),('smart','rgb(21, 44, 59)','rgb(255, 255, 255)','6px','system-ui')]:
     base['profile']=theme;d=f.post(url+'/design',{'revision':d['revision'],'design':base})[1];m=f.request('GET',url+'/design-native')[1];(OUT/(theme+'-mapping.json')).write_text(json.dumps(m,indent=2))
     p.evaluate("m=>{for(const key of [...card.style])if(key.startsWith('--'))card.style.removeProperty(key);for(const [k,v] of Object.entries(m.themes[m.themeName]))card.style.setProperty('--'+k,v);}",m);p.wait_for_timeout(400)
     observed=p.evaluate("()=>{const s=getComputedStyle(card),h=getComputedStyle(card.shadowRoot.querySelector('.card-header'));return {tag:card.constructor.name,color:s.color,background:s.backgroundColor,image:s.backgroundImage,radius:s.borderRadius,shadow:s.boxShadow,border:s.borderColor,headerFont:h.fontFamily,headerSize:h.fontSize}}")
     self.assertEqual(observed['color'],color);self.assertEqual(observed['background'],background);self.assertEqual(observed['radius'],radius);self.assertIn(font,observed['headerFont']);self.assertNotEqual(observed['tag'],'HTMLElement');self.assertEqual(observed['headerSize'],'28px' if theme!='smart' else '24px');self.assertEqual('linear-gradient' in observed['image'],theme=='noir');self.assertEqual(observed['shadow']=='none',theme=='smart');p.screenshot(path=str(OUT/(theme+'.png')));rows.append({'theme':theme,'observed':observed})
    self.assertEqual(errors,[]);b.close()
   (OUT/'result.json').write_text(json.dumps({'matrix':rows,'network':network,'sourcePin':'a67b691a451e0b3fc469679b07158f963a61842c','assetPinsSha256':hashlib.sha256((CACHE/'asset-pins.json').read_bytes()).hexdigest(),'installedHA':False,'errors':errors},indent=2))
  finally:f.close()
if __name__=='__main__':unittest.main()
