"""Unmodified pinned HA frontend runtime; synthetic isolated root, offline assets."""
import sys,pathlib,json,hashlib,tempfile,unittest,os,io
from urllib.parse import urlsplit
from PIL import Image
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'lumo_raumstudio'))
from store import Store,defaults
from native import compile_native
from test_images import png
CACHE=pathlib.Path(os.environ.get('HA_NATIVE_CACHE','/workspace/lumo-core-usability-evidence/native-feasibility'))
OUT=pathlib.Path(os.environ.get('RAUMSTUDIO_EVIDENCE','/workspace/lumo-auftrag02-evidence/implementation/final/browser'))/'native'
class NativeRuntimeTests(unittest.TestCase):
    def test_original_background_runtime_and_root_inheritance(self):
        OUT.mkdir(parents=True,exist_ok=True);pins=json.loads((CACHE/'asset-pins.json').read_text());network=[];errors=[];matrix=[]
        with tempfile.TemporaryDirectory() as t:
            s=Store(pathlib.Path(t)/'s.sqlite');image=s.put_image('alice','Native probe',png(size=(100,100)))
            d=s.import_native('alice','Native Mappingprobe',{'views':[{'title':'Global','path':'global','cards':[]},{'title':'Eigener Hintergrund','path':'own','background':'#00ff00','cards':[]}]})
            d.pop('nativeImport')  # Exercise the preserved legacy mapping, not new lossless exports.
            bg=d['settings']['background'];bg.update(imageId=image['id'],color='#0000ff')
            with sync_playwright() as pw:
                browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);ctx=browser.new_context(viewport={'width':800,'height':600},service_workers='block');page=ctx.new_page()
                def route(r):
                    u=r.request.url;p=pins.get(u);network.append({'url':u,'cached':bool(p),'method':r.request.method})
                    if not p or r.request.method!='GET' or '/cdn-cgi/' in u:r.abort();return
                    data=(CACHE/'assets'/p['sha256']).read_bytes();assert hashlib.sha256(data).hexdigest()==p['sha256'];path=urlsplit(u).path
                    kind='text/html' if path=='/' else 'text/javascript' if path.endswith('.js') else 'application/json' if path.endswith('.json') else 'text/css' if path.endswith('.css') else 'image/svg+xml' if path.endswith('.svg') else 'application/octet-stream'
                    r.fulfill(body=data,content_type=kind)
                ctx.route('**/*',route);ctx.route_web_socket('**/*',lambda ws:ws.close());page.goto('https://demo.home-assistant.io/',wait_until='domcontentloaded');page.wait_for_function("()=>!!customElements.get('hui-view-background')&&!!customElements.get('hui-root')",timeout=30000)
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.evaluate("""() => {
                  document.querySelector('ha-demo')?.remove();document.body.style.margin='0';window.calls=[];
                  const deny=(name)=>{calls.push(name);return Promise.reject(Error('denied'))};
                  window.h={states:{},entities:{},devices:{},areas:{},floors:{},services:{},themes:{themes:{},default_theme:'default',default_dark_theme:null,darkMode:false},selectedTheme:null,language:'en',locale:{language:'en',number_format:'language',time_format:'language',date_format:'language',time_zone:'local',first_weekday:'language'},config:{components:[],unit_system:{},version:'synthetic'},user:{id:'synthetic',name:'Synthetic',is_admin:false},userData:{},panels:{},localize:()=>'',hassUrl:p=>p,callWS:async c=>c.type==='lovelace/info'?{resource_mode:'storage'}:deny(c.type),callService:()=>deny('service'),callApi:()=>deny('api'),connection:{subscribeMessage:async()=>()=>{},addEventListener:()=>{},removeEventListener:()=>{} }};
                  window.nativeRoot=document.createElement('hui-root');nativeRoot.hass=h;nativeRoot.noEdit=true;nativeRoot.style.cssText='display:block;min-height:600px;position:relative;isolation:isolate';
                  nativeRoot.addEventListener('context-request',e=>{e.stopPropagation();const k=String(e.context);e.callback(k==='narrowViewport'?false:k==='reducedMotion'?true:k.startsWith('hass')?h:h[k],()=>{});});
                }""")
                for mode,scale,opacity,attachment in [('cover',100,100,'scroll'),('contain',100,50,'scroll'),('scale',137,0,'fixed'),('scale',75,100,'fixed')]:
                    bg.update(mode=mode,scale=scale,opacity=opacity,attachment=attachment,position='right bottom');cfg=compile_native(s,'alice',d)
                    page.evaluate("""cfg=>{nativeRoot.lovelace={config:cfg,rawConfig:cfg,editMode:false,mode:'storage',urlPath:'proof',locale:h.locale,embedded:true};nativeRoot.route={path:'/global',prefix:'/proof'};if(!nativeRoot.isConnected)document.body.append(nativeRoot);}""",cfg)
                    page.wait_for_function("()=>nativeRoot.shadowRoot?.querySelector('hui-view-background')?.background?.includes('data:image/png')");page.wait_for_timeout(250)
                    observed=page.evaluate("""()=>{const e=nativeRoot.shadowRoot.querySelector('hui-view-background'),s=getComputedStyle(e);return {background:e.background,css:e.style.getPropertyValue('--view-background'),size:s.backgroundSize,position:s.backgroundPosition,color:s.backgroundColor,image:s.backgroundImage,fixed:e.hasAttribute('fixed-background'),opacity:s.opacity,rootReadback:nativeRoot.lovelace.config}}""")
                    self.assertEqual(observed['background'],cfg['background']);self.assertEqual(observed['rootReadback'],cfg);self.assertEqual(observed['fixed'],attachment=='fixed');self.assertEqual(observed['size'],str(scale)+'% auto' if mode=='scale' else mode);self.assertEqual(observed['position'],'100% 100%');self.assertIn('data:image/png',observed['image'])
                    shot=OUT/f'{mode}-{scale}-{opacity}.png';page.screenshot(path=str(shot));pixel=Image.open(shot).convert('RGB').getpixel((400,450))
                    if opacity==0:self.assertEqual(pixel,(0,0,255))
                    matrix.append({'mode':mode,'scale':scale,'opacity':opacity,'attachment':attachment,'observed':observed,'samplePixel':pixel})
                    page.evaluate("()=>{nativeRoot.route={path:'/own',prefix:'/proof'}}");page.wait_for_function("()=>nativeRoot.shadowRoot.querySelector('hui-view-background').background==='#00ff00'")
                    self.assertEqual(page.evaluate("()=>getComputedStyle(nativeRoot.shadowRoot.querySelector('hui-view-background')).backgroundColor"),'rgb(0, 255, 0)')
                self.assertEqual(page.evaluate('()=>calls'),[]);self.assertEqual(errors,[])
                (OUT/'result.json').write_text(json.dumps({'passed':True,'originalRuntime':'DEMO-20261028.4','sourcePin':'a67b691a451e0b3fc469679b07158f963a61842c','matrix':matrix,'network':network,'errors':errors,'installedHA':False},indent=2));browser.close()
if __name__=='__main__':unittest.main()
