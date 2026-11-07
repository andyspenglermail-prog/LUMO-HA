from test_design_browser import reference_control
"""Room photos: isolated real ingress UI, synthetic images only."""
import pathlib,sys,unittest,copy,os,json
sys.path.insert(0,str(pathlib.Path(__file__).parent))
import test_design_browser as setup_module
from playwright.sync_api import expect
OUT=pathlib.Path(os.environ.get('RAUMSTUDIO_EVIDENCE','/tmp/lumo-room-photos'))/'room-photos'
class RoomPhotoBrowserTests(unittest.TestCase):
 setUp=setup_module.DesignBrowserTests.setUp
 tearDown=setup_module.DesignBrowserTests.tearDown
 def test_single_multi_hidden_navigation_preserves_saved_views(self):
  p=self.page;expect(p.locator('#design-status')).to_contain_text('Frisch gelesen');before=copy.deepcopy(self.before)
  expect(p.locator('#design-nav')).to_be_hidden();expect(p.locator('#design-view-title')).to_have_text(before['roomPlan']['views'][0]['title'])
  self.assertEqual(self.f.store.get('alice',before['id']),before)
  p.locator('[data-step="2"]').click();expect(p.locator('#room-status')).to_contain_text('Frisch gelesen');p.locator('#room-new').click();p.locator('#dialog-input').fill('Second synthetic view');p.locator('#dialog-confirm').click();p.locator('#room-save').click();expect(p.locator('#room-dirty')).to_contain_text('Gespeichert');p.locator('#room-next').click();expect(p.locator('#design-nav')).to_be_visible();expect(p.locator('#design-nav button')).to_have_count(2)
  d=self.f.store.get('alice',before['id']);plan=copy.deepcopy(d['roomPlan'])
  for v in plan['views']:v['visible']=False
  from room_store import save_plan
  hidden=save_plan(self.f.store,'alice',d['id'],d['revision'],plan,[],{})
  p.reload();p.locator('[data-step="3"]').click();expect(p.locator('#design-cards')).to_contain_text('Deine gespeicherten Raumansichten sind ausgeblendet. Aktiviere unter „Raum“ die Option „In diesem Dashboard anzeigen“.');expect(p.locator('#design-nav')).to_be_hidden();expect(p.locator('#design-view option')).to_have_count(0);self.assertEqual(self.f.store.get('alice',d['id']),hidden)
 def test_saved_photo_upload_library_remove_and_new_browser_keep_background(self):
  from test_images import png
  from design import defaults,save
  p=self.page;f=self.f;view=self.before['roomPlan']['views'][0]['id'];image=f.store.put_image('alice','Existing synthetic image',png('blue',(640,360)));value=defaults();value['roomImages']={view:image['id']};saved=save(f.store,'alice',self.before['id'],self.before['revision'],value)
  p.reload();p.locator('[data-step="3"]').click();expect(p.locator('#design-room-hero')).to_have_attribute('data-photo-state','ready');expect(p.locator('#design-room-photo img')).to_be_visible();expect(p.locator('#design-room-image')).to_have_value(image['id'])
  p.locator('#design-room-file').set_input_files({'name':'Own synthetic.png','mimeType':'image/png','buffer':png('green',(640,360))});expect(p.locator('#notice')).to_contain_text('Raumfoto');expect(p.locator('#design-dirty')).to_contain_text('Ungespeichert');expect(p.locator('#design-room-hero')).to_have_attribute('data-photo-state','ready');self.assertEqual(f.store.get('alice',saved['id']),saved)
  uploaded=p.locator('#design-room-image').input_value();self.assertNotEqual(uploaded,image['id']);p.locator('#design-save').click();expect(p.locator('#design-dirty')).to_contain_text('Gespeichert');d=f.store.get('alice',saved['id']);self.assertEqual(d['design']['roomImages'],{view:uploaded})
  for k in ('roomPlan','native','views','settings'):self.assertEqual(d[k],self.before[k])
  self.b.close();self.b=self.p.chromium.launch(headless=True,args=['--no-sandbox']);self.ctx=self.b.new_context(viewport={'width':1500,'height':1000},extra_http_headers={'X-Remote-User-Id':'alice'});self.page=self.ctx.new_page();p=self.page;p.goto(self.proxy.url);p.get_by_role('button',name='Öffnen',exact=True).click();p.locator('[data-step="3"]').click();expect(p.locator('#design-room-image')).to_have_value(uploaded);expect(p.locator('#design-room-hero')).to_have_attribute('data-photo-state','ready')
  reference_control(p,'#design-room-image').select_option(image['id']);expect(p.locator('#design-room-photo img')).to_have_attribute('src','api/images/'+image['id']);reference_control(p,'#design-room-remove').click();expect(p.locator('#design-room-photo')).to_be_hidden();p.locator('#design-save').click();expect(p.locator('#design-dirty')).to_contain_text('Gespeichert');self.assertEqual(f.store.get('alice',d['id'])['design']['roomImages'],{});self.assertEqual(f.store.get('alice',d['id'])['settings'],self.before['settings']);self.assertEqual(len(f.store.images('alice')),2)
  p.locator('.design-settings > details').filter(has=p.locator('#design-capabilities')).locator('summary').click();expect(p.locator('#design-capabilities')).to_contain_text('Raumfotos');self.assertFalse(any(c['type'].endswith('/update') or c['type']=='call_service' for c in f.peer.commands))
 def test_failed_uploads_and_uncertain_confirmation_preserve_staged_binding(self):
  from test_images import png
  p=self.page;f=self.f;expect(p.locator('#design-status')).to_contain_text('Frisch gelesen');before=copy.deepcopy(f.store.get('alice',self.before['id']))
  for name,raw,message in [('bad.svg',b'<svg onload="evil()"/>','nicht vollständig'),('truncated.png',png()[:40],'nicht vollständig'),('large.png',b'x'*(8*1024*1024+1),'8 MiB')]:
   p.locator('#design-room-file').set_input_files({'name':name,'mimeType':'image/png','buffer':raw});expect(p.locator('#notice')).to_contain_text(message);expect(p.locator('#design-room-hero')).to_have_attribute('data-photo-state','none');self.assertEqual(f.store.get('alice',before['id']),before);self.assertEqual(f.store.images('alice'),[])
  self.proxy.lose_read_after_post=('/api/images','/api/images');p.locator('#design-room-file').set_input_files({'name':'Uncertain.png','mimeType':'image/png','buffer':png()});expect(p.locator('#notice')).to_contain_text('Bestätigendes Lesen fehlgeschlagen');self.assertEqual(len(f.store.images('alice')),1);self.assertEqual(f.store.get('alice',before['id']),before);expect(p.locator('#design-room-image')).to_have_value('');count=sum(x[0]=='POST' for x in self.proxy.requests)
  p.locator('#design-room-file').set_input_files({'name':'No retry.png','mimeType':'image/png','buffer':png()});expect(p.locator('#notice')).to_contain_text('unklar');self.assertEqual(sum(x[0]=='POST' for x in self.proxy.requests),count)
 def test_upload_busy_phases_dirty_guard_and_cas_keep_photo_target(self):
  from test_images import png
  p=self.page;expect(p.locator('#design-status')).to_contain_text('Frisch gelesen');view=self.before['roomPlan']['views'][0]['id']
  for method,path in [('POST','/api/images'),('GET','/api/images')]:
   self.proxy.hold_response=(method,path);self.proxy.response_arrived.clear();self.proxy.release_response.clear();p.locator('#design-room-file').set_input_files({'name':method+'.png','mimeType':'image/png','buffer':png()});self.assertTrue(self.proxy.response_arrived.wait(5))
   for selector in ('#design-room-file','#design-room-image','#design-view','#design-save','[data-step="1"]'):expect(p.locator(selector)).to_be_disabled()
   p.evaluate('()=>designPreview()');expect(p.locator('#design-room-image')).to_be_disabled();self.proxy.release_response.set();expect(p.locator('#design-room-file')).to_be_enabled();expect(p.locator('#design-dirty')).to_contain_text('Ungespeichert')
  chosen=p.locator('#design-room-image').input_value();p.locator('[data-step="1"]').click();p.locator('#dialog-cancel').click();expect(p.locator('#design-room-image')).to_have_value(chosen)
  other=self.f.store.update('alice',self.before['id'],self.before['revision'],{'description':'Other writer'});p.locator('#design-save').click();expect(p.locator('#notice')).to_contain_text('inzwischen geändert');expect(p.locator('#design-room-image')).to_have_value(chosen);self.assertEqual(p.evaluate('()=>designDraft.roomImages'),{view:chosen});self.assertEqual(self.f.store.get('alice',self.before['id']),other)
 def test_stale_image_and_library_results_cannot_cross_view_or_dashboard(self):
  from test_images import png
  from room_store import get_plan,save_plan
  from design import defaults,save
  f=self.f;p=self.page;d=f.store.import_native('alice','Two image views',{'views':[{'title':'Same','cards':[]},{'title':'Same','cards':[]}]});a,b=[v['id'] for v in d['views']];image=f.store.put_image('alice','Held',png());value=defaults();value['roomImages']={a:image['id']};d=save(f.store,'alice',d['id'],d['revision'],value)
  p.reload();p.locator('.draft-row').filter(has_text=d['name']).get_by_role('button',name='Öffnen',exact=True).click();self.proxy.hold_response=('GET','/api/images/'+image['id']);p.locator('[data-step="3"]').click();self.assertTrue(self.proxy.response_arrived.wait(5));expect(p.locator('#design-room-hero')).to_have_attribute('data-photo-state','loading');p.locator('#design-view').select_option(b);expect(p.locator('#design-room-hero')).to_have_attribute('data-photo-state','none');self.proxy.release_response.set();p.wait_for_timeout(150);expect(p.locator('#design-room-photo')).to_be_hidden();expect(p.locator('#design-room-image')).to_have_value('')
  self.proxy.lost_read_path='/api/images/'+image['id'];p.reload();p.locator('[data-step="3"]').click();expect(p.locator('#design-room-hero')).to_have_attribute('data-photo-state','error');expect(p.locator('#design-room-photo-state')).to_contain_text('nicht verfügbar');expect(p.locator('#design-room-photo')).to_be_hidden();self.assertEqual(f.store.get('alice',d['id']),d)
  self.proxy.lost_read_path=None;p.locator('[data-step="1"]').click();self.proxy.hold_response=('GET','/api/images');self.proxy.response_arrived.clear();self.proxy.release_response.clear();p.locator('[data-step="3"]').click();self.assertTrue(self.proxy.response_arrived.wait(5));expect(p.locator('#design-save')).to_be_disabled();p.locator('[data-step="1"]').click();p.locator('.draft-row').filter(has_text=self.before['name']).get_by_role('button',name='Öffnen',exact=True).click();p.locator('[data-step="3"]').click();expect(p.locator('#design-output-title')).to_have_text(self.before['name']);self.proxy.release_response.set();p.wait_for_timeout(150);expect(p.locator('#design-room-image')).to_have_value('');expect(p.locator('#design-room-photo')).to_be_hidden();self.assertEqual(f.store.get('alice',self.before['id']),self.before)
 def test_photo_profiles_desktop_tablet_phone_contrast_and_touch(self):
  import io
  from PIL import Image,ImageDraw
  from design import defaults,save,contrast
  # Deliberately geometric fixture, never a stock or invented room photograph.
  im=Image.new('RGB',(1200,600),'#b4c9c4');draw=ImageDraw.Draw(im);draw.rectangle((0,380,1200,600),fill='#647b76');draw.rectangle((80,70,470,340),fill='#e9f2e8');draw.rectangle((700,200,1100,500),fill='#9c7654');draw.text((100,100),'SYNTHETIC IMAGE / NOT A ROOM',fill='#172b24');buf=io.BytesIO();im.save(buf,'PNG');image=self.f.store.put_image('alice','Synthetic geometry',buf.getvalue());value=defaults();value['roomImages']={self.before['roomPlan']['views'][0]['id']:image['id']};save(self.f.store,'alice',self.before['id'],self.before['revision'],value);OUT.mkdir(parents=True,exist_ok=True);rows=[]
  for target,w,h,dpr,touch in [('desktop',1440,900,1,False),('tablet',1024,768,2,True),('phone',390,844,3,True)]:
   ctx=self.b.new_context(viewport={'width':w,'height':h},device_scale_factor=dpr,has_touch=touch,is_mobile=touch,extra_http_headers={'X-Remote-User-Id':'alice'});p=ctx.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto(self.proxy.url);action='tap' if touch else 'click';getattr(p.get_by_role('button',name='Öffnen',exact=True),action)();getattr(p.locator('[data-step="3"]'),action)();expect(p.locator('#design-room-hero')).to_have_attribute('data-photo-state','ready');neutral=[]
   for theme in ('noir','ivory','smart'):
    if w<=1100:getattr(p.locator('[data-design-panel="catalog"]'),action)()
    p.locator('#design-category').select_option('Smart & Functional' if theme=='smart' else 'Luxury & Signature');getattr(p.locator('[data-design-profile="'+theme+'"]'),action)()
    if w<=1100:getattr(p.locator('[data-design-panel="settings"]'),action)()
    if target!='desktop' and not p.locator('[data-target="'+target+'"]').is_checked():getattr(p.locator('[data-target="'+target+'"]'),action)()
    reference_control(p,'#design-active-target').select_option(target)
    if w<=1100:getattr(p.locator('[data-design-panel="preview"]'),action)()
    expect(p.locator('#design-room-hero')).to_have_attribute('data-photo-state','ready');reference_control(p,'#design-one').uncheck();p.locator('#design-frame').scroll_into_view_if_needed();self.assertFalse(p.evaluate('()=>document.documentElement.scrollWidth>innerWidth'));p.screenshot(path=str(OUT/f'{target}-{theme}-editor.png'),full_page=True);p.locator('#design-output').screenshot(path=str(OUT/f'{target}-{theme}-output.png'))
    getattr(reference_control(p,'#design-one'),action)();observed=p.evaluate('''()=>{const o=document.querySelector('#design-output'),r=document.querySelector('#design-room-hero'),i=r.querySelector('img'),c=r.querySelector('.design-room-caption'),h=r.querySelector('h3'),s=getComputedStyle(c);return {targetWidth:o.clientWidth,overflow:o.scrollWidth>o.clientWidth,imageWidth:i.clientWidth,imageHeight:i.clientHeight,naturalWidth:i.naturalWidth,titleColor:getComputedStyle(h).color,captionColor:s.backgroundColor,card:getComputedStyle(o).getPropertyValue('--d-card').trim(),text:getComputedStyle(o).getPropertyValue('--d-text').trim(),border:s.borderTopWidth,editorWidth:innerWidth,dpr:devicePixelRatio,touch:navigator.maxTouchPoints}}''');self.assertFalse(observed['overflow']);self.assertGreater(observed['imageWidth'],200);self.assertGreaterEqual(observed['imageHeight'],180);self.assertEqual(observed['naturalWidth'],1200);self.assertGreaterEqual(contrast(observed['text'],observed['card']),4.5)
    reference_control(p,'#design-one').uncheck();neutral.append(p.locator('#design-room-image').evaluate('(e)=>{const s=getComputedStyle(e);return [s.color,s.backgroundColor,s.fontFamily,s.borderRadius]}'))
    getattr(reference_control(p,'#design-room-remove'),action)();expect(p.locator('#design-room-photo')).to_be_hidden();reference_control(p,'#design-room-image').select_option(image['id']);expect(p.locator('#design-room-hero')).to_have_attribute('data-photo-state','ready');rows.append({'target':target,'profile':theme,'input':action,'observed':observed,'errors':errors.copy()});self.assertEqual(errors,[])
   self.assertEqual(neutral[0],neutral[1]);self.assertEqual(neutral[1],neutral[2]);ctx.close()
  (OUT/'matrix.json').write_text(json.dumps(rows,indent=2)+'\n')
 def test_two_same_named_views_keep_independent_photos_and_raw_ui_export(self):
  from test_images import png
  f=self.f;p=self.page;native={'views':[{'title':'Same','cards':[{'type':'custom:opaque','large':9007199254740993,'bool':True,'float':1.0,'nested':{'__proto__':'inert'}}]},{'title':'Same','cards':[]}]};d=f.store.import_native('alice','Raw photo export',native);a,b=[v['id'] for v in d['views']];i=f.store.put_image('alice','First',png('blue'));j=f.store.put_image('alice','Second',png('green'));p.reload();p.locator('.draft-row').filter(has_text=d['name']).get_by_role('button',name='Öffnen',exact=True).click()
  with p.expect_download() as first:p.locator('#native-export').click()
  raw=pathlib.Path(first.value.path()).read_bytes();p.locator('[data-step="3"]').click();expect(p.locator('#design-status')).to_contain_text('Frisch gelesen');reference_control(p,'#design-room-image').select_option(i['id']);p.locator('#design-view').select_option(b);expect(p.locator('#design-room-image')).to_have_value('');reference_control(p,'#design-room-image').select_option(j['id']);p.locator('#design-view').select_option(a);expect(p.locator('#design-room-image')).to_have_value(i['id']);p.locator('#design-save').click();expect(p.locator('#design-dirty')).to_contain_text('Gespeichert');saved=f.store.get('alice',d['id']);self.assertEqual(saved['design']['roomImages'],{a:i['id'],b:j['id']})
  reference_control(p,'#design-room-remove').click();p.locator('[data-step="1"]').click();p.locator('#dialog-discard').click()
  with p.expect_download() as final:p.locator('#native-export').click()
  self.assertEqual(pathlib.Path(final.value.path()).read_bytes(),raw);self.assertEqual(f.store.get('alice',d['id']),saved);p.locator('[data-step="3"]').click();expect(p.locator('#design-room-image')).to_have_value(i['id']);p.locator('#design-view').select_option(b);expect(p.locator('#design-room-image')).to_have_value(j['id'])
if __name__=='__main__':unittest.main()
