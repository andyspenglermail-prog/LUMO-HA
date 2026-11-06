"""Real browser → ingress HTTP → app → CoreClient → synthetic WS peer."""
import pathlib,sys,unittest,os,json,copy
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from test_rooms import RoomFixture
from proxy import Proxy
from playwright.sync_api import sync_playwright,expect
OUT=pathlib.Path(os.environ.get('RAUMSTUDIO_EVIDENCE','/workspace/lumo-auftrag03-evidence/implementation/browser'))/'design'
class DesignBrowserTests(unittest.TestCase):
 def setUp(self):
  self.f=RoomFixture();self.proxy=Proxy(self.f);self.p=sync_playwright().start();self.b=self.p.chromium.launch(headless=True,args=['--no-sandbox']);self.ctx=self.b.new_context(viewport={'width':1500,'height':1000},extra_http_headers={'X-Remote-User-Id':'alice'});self.page=self.ctx.new_page();self.page.goto(self.proxy.url);p=self.page;p.locator('#new-name').fill('Synthetic design fixture');p.locator('#create').click();expect(p.locator('#room-status')).to_contain_text('Frisch gelesen');p.locator('[data-area="a"]').click();p.locator('#room-scope').select_option('all');p.locator('#room-select-visible').click();p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');self.before=copy.deepcopy(self.f.store.list('alice')[0]);p.locator('#room-next').click()
 def tearDown(self):self.b.close();self.p.stop();self.proxy.close();self.f.close()
 def test_real_preview_theme_isolation_save_reload(self):
  p=self.page;expect(p.locator('#design-step')).to_be_visible();expect(p.locator('#design-status')).to_contain_text('Frisch gelesen');expect(p.locator('#design-cards [data-entity]')).to_have_count(5)
  neutral=[];output=[]
  for theme in ('noir','ivory','smart'):
   p.locator('#design-category').select_option('Smart & Functional' if theme=='smart' else 'Luxury & Signature');p.locator('[data-design-profile="'+theme+'"]').click()
   expect(p.locator('#design-output')).to_have_attribute('data-profile',theme)
   neutral.append(p.locator('#design-save').evaluate('(e)=>{let s=getComputedStyle(e),r=e.getBoundingClientRect();return [s.color,s.backgroundColor,s.fontFamily,s.borderRadius,r.width,r.height]}'))
   output.append(p.locator('.design-card').first.evaluate('(e)=>{let s=getComputedStyle(e);return [s.fontFamily,s.borderRadius,s.padding,s.boxShadow]}'))
   expect(p.locator('#design-cards')).to_contain_text('Nicht verfügbar');expect(p.locator('#design-cards')).to_contain_text('Deaktiviert')
  self.assertEqual(neutral[0],neutral[1]);self.assertEqual(neutral[1],neutral[2]);self.assertEqual(len({str(x) for x in output}),3)
  p.locator('#design-save').click();expect(p.locator('#design-dirty')).to_contain_text('Gespeichert');d=self.f.store.list('alice')[0]
  for k in ('roomPlan','native','views','settings'):self.assertEqual(d[k],self.before[k])
  self.assertEqual(d['design']['profile'],'smart');p.reload();p.locator('[data-step="3"]').click();expect(p.locator('#design-output')).to_have_attribute('data-profile','smart')
  self.assertFalse(any(c['type'].endswith('/update') or c['type']=='call_service' for c in self.f.peer.commands))
 def test_custom_viewport_reflow_overrides_reset_and_save(self):
  p=self.page;expect(p.locator('#design-status')).to_contain_text('Frisch gelesen');p.locator('#design-customize summary').click()
  expect(p.locator('#design-override-radius')).to_be_visible();p.locator('#design-override-radius').fill('32');p.locator('#design-override-radius').dispatch_event('change');self.assertEqual(p.locator('.design-card').first.evaluate('(e)=>getComputedStyle(e).borderRadius'),'32px')
  p.locator('[data-reset="radius"]').click();self.assertEqual(p.locator('.design-card').first.evaluate('(e)=>getComputedStyle(e).borderRadius'),'16px')
  p.locator('#design-override-text').fill('#202924');p.locator('#design-override-text').dispatch_event('change');expect(p.locator('#design-contrast')).to_contain_text('4,5');expect(p.locator('#design-save')).to_be_disabled();p.locator('[data-reset="text"]').click()
  p.locator('[data-target="custom"]').check();p.locator('#design-active-target').select_option('custom');p.locator('#design-width').fill('390');p.locator('#design-width').dispatch_event('change');p.locator('#design-height').fill('844');p.locator('#design-height').dispatch_event('change');p.locator('#design-one').check()
  self.assertEqual(p.locator('#design-cards').evaluate('(e)=>getComputedStyle(e).gridTemplateColumns.split(" ").length'),1)
  expect(p.locator('#design-output')).to_have_css('width','390px');expect(p.locator('#design-metrics')).to_contain_text('Browser-DPR');p.locator('#design-orientation').select_option('landscape');expect(p.locator('#design-output')).to_have_css('width','844px');self.assertEqual(p.locator('#design-cards').evaluate('(e)=>getComputedStyle(e).gridTemplateColumns.split(" ").length'),3)
  p.locator('#design-width').fill('0');p.locator('#design-width').dispatch_event('change');expect(p.locator('#design-save')).to_be_disabled();expect(p.locator('#design-output')).to_have_css('width','844px');p.locator('#design-width').fill('390');p.locator('#design-width').dispatch_event('change');p.locator('#design-save').click();expect(p.locator('#design-dirty')).to_contain_text('Gespeichert');d=self.f.store.list('alice')[0];self.assertEqual(d['design']['targets'],['desktop','custom']);self.assertEqual(d['roomPlan'],self.before['roomPlan'])
 def test_imported_background_functions_protection_and_native_download(self):
  f=self.f;native={'background':'#123456','views':[{'title':'Own','background':'#654321','cards':[{'type':'tile','entity':'light.fixture'},{'type':'custom:evil','name':'DO NOT EXECUTE'}]},{'title':'Global','cards':[]},{'title':'Blocked','background':'url(https://invalid.example/x)','cards':[]}]};d=f.store.import_native('alice','Native fixture',native);p=self.page;p.reload();p.locator('.draft-row').filter(has_text='Native fixture').get_by_role('button',name='Öffnen',exact=True).click();p.locator('[data-step="3"]').click();expect(p.locator('#design-status')).to_contain_text('Frisch gelesen');expect(p.locator('#design-output')).to_have_css('background-color','rgb(101, 67, 33)');expect(p.locator('#design-cards')).to_contain_text('Fixture Licht');expect(p.locator('#design-cards')).to_contain_text('DO NOT EXECUTE');p.locator('#design-view').select_option(d['views'][1]['id']);expect(p.locator('#design-output')).to_have_css('background-color','rgb(18, 52, 86)');p.locator('#design-view').select_option(d['views'][2]['id']);expect(p.locator('#design-background')).to_contain_text('nicht geladen');p.locator('.design-settings details summary').click();expect(p.locator('#design-capabilities')).to_contain_text('preview-only')
  with p.expect_download() as dl:p.locator('#design-native').click()
  self.assertEqual(json.loads(pathlib.Path(dl.value.path()).read_text())['dashboardId'],d['id']);self.assertEqual(f.store.get('alice',d['id']),d)
if __name__=='__main__':unittest.main()
