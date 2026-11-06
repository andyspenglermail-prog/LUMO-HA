import sys,pathlib,unittest,os,json
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from test_rooms import RoomFixture
from playwright.sync_api import sync_playwright,expect
OUT=pathlib.Path(os.environ.get('RAUMSTUDIO_EVIDENCE','/workspace/lumo-auftrag02-evidence/implementation/browser'));OUT.mkdir(parents=True,exist_ok=True)
class RoomBrowserTests(unittest.TestCase):
 def test_actual_ui_backend_protocol_select_save_refresh_and_responsive_touch(self):
  f=RoomFixture()
  try:
   with sync_playwright() as p:
    b=p.chromium.launch(headless=True,args=['--no-sandbox']);ctx=b.new_context(viewport={'width':1480,'height':960},extra_http_headers={'X-Remote-User-Id':'alice'});page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f.origin);page.locator('#new-name').fill('Fixture Haus');page.locator('#create').click()
    expect(page.locator('#room-step')).to_be_visible();expect(page.locator('#room-status')).to_contain_text('Frisch gelesen');expect(page.locator('#room-sources')).to_contain_text('Gleicher Name')
    page.locator('[data-area="a"]').click();expect(page.locator('#room-title')).to_have_value('Gleicher Name');expect(page.locator('#room-origin')).to_contain_text('Fixture Etage')
    page.locator('[data-device-check="dev"]').check();self.assertGreater(page.locator('[data-inspect-device="dev"] strong').bounding_box()['width'],100);expect(page.locator('#room-dirty')).to_contain_text('Ungespeichert');page.locator('[data-expand="dev"]').click();expect(page.locator('[data-entity-check="registry:reg3"]')).to_be_checked()
    page.locator('[data-entity-check="registry:reg2"]').uncheck();page.locator('#room-undo').click();expect(page.locator('[data-entity-check="registry:reg2"]')).to_be_checked()
    page.locator('#room-title').fill('Lokaler Raum');page.locator('#room-visible').uncheck();page.locator('#room-save').click();expect(page.locator('#room-dirty')).to_contain_text('Gespeichert')
    d=f.store.list('alice')[0];self.assertEqual(d['roomPlan']['views'][0]['title'],'Lokaler Raum');self.assertEqual(len(d['roomPlan']['views'][0]['entityRefs']),3);self.assertEqual(d['views'],[])
    page.locator('#room-back').click();expect(page.locator('.draft-meta')).to_contain_text('1 Raumansicht');page.locator('#continue').click();expect(page.locator('#room-status')).to_contain_text('Frisch gelesen')
    # Refresh must keep focused/staged title and selection, resolving current ids by registry identity.
    page.locator('#room-title').fill('Nicht gespeichert');f.peer.data['entities'][0]['entity_id']='light.renamed';f.peer.data['states'][0]['entity_id']='light.renamed';f.peer.data['states'][0]['state']='off';page.locator('#room-refresh').click();expect(page.locator('#room-title')).to_have_value('Nicht gespeichert');expect(page.locator('#room-inventory')).to_contain_text('light.renamed')
    page.locator('[data-inspect-entity="registry:reg1"]').click();expect(page.locator('#room-properties')).to_contain_text('off');expect(page.locator('#room-properties')).to_contain_text('Gerätebereich');expect(page.locator('#room-correction')).not_to_have_attribute('open','')
    page.locator('#room-search').fill('switch.disabled');page.locator('#room-filter').select_option('switch');expect(page.locator('#room-inventory')).to_contain_text('switch.disabled');page.locator('#room-search').fill('');page.locator('#room-filter').select_option('all')
    page.locator('#room-save').click();expect(page.locator('#room-dirty')).to_contain_text('Gespeichert');page.evaluate("() => {window.scrollTo(0,0);document.querySelector('.room-center').scrollTop=0;}");page.screenshot(path=str(OUT/'rooms-desktop.png'),full_page=True)
    panel=page.locator('.room-center').bounding_box();device=page.locator('[data-device="dev"] .room-device-head').bounding_box();self.assertLessEqual(device['y']+device['height'],panel['y']+panel['height'])
    geometry=page.locator('.room-columns').bounding_box();self.assertLess(geometry['y'],320);self.assertLessEqual(geometry['y']+geometry['height'],900)
    self.assertEqual(page.evaluate('document.documentElement.scrollWidth <= innerWidth'),True)
    cols=page.locator('.room-columns').evaluate('(e)=>getComputedStyle(e).gridTemplateColumns.split(" ").map(parseFloat)');self.assertEqual(len(cols),3);self.assertAlmostEqual(cols[1]/cols[0],2,delta=.2)
    # Same owner's independent browser gets server data; nothing in localStorage supplies views.
    ctx2=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,extra_http_headers={'X-Remote-User-Id':'alice'});p2=ctx2.new_page();p2.goto(f.origin);p2.get_by_role('button',name='Öffnen',exact=True).tap();p2.locator('#continue').tap();expect(p2.locator('#room-views')).to_contain_text('Nicht gespeichert');p2.locator('[data-room-panel="inventory"]').tap();expect(p2.locator('#room-title')).to_have_value('Nicht gespeichert');p2.locator('#room-scope').select_option('all');p2.locator('#room-search').fill('weather.state_only');p2.locator('[data-entity-check="state:weather.state_only"]').tap();p2.locator('#room-save').tap();expect(p2.locator('#room-dirty')).to_contain_text('Gespeichert');self.assertTrue(p2.evaluate('document.documentElement.scrollWidth <= innerWidth'));p2.screenshot(path=str(OUT/'rooms-phone.png'),full_page=True)
    p2.set_viewport_size({'width':820,'height':1080});p2.locator('[data-room-panel="views"]').tap();p2.locator('#room-new').tap();p2.locator('#dialog-input').fill('Virtueller Fixture Raum');p2.locator('#dialog-confirm').tap();expect(p2.locator('#room-title')).to_have_value('Virtueller Fixture Raum');self.assertTrue(p2.evaluate('document.documentElement.scrollWidth <= innerWidth'));p2.evaluate('window.scrollTo(0,0)');p2.screenshot(path=str(OUT/'rooms-tablet.png'),full_page=True)
    self.assertEqual(errors,[]);self.assertFalse(any(c['type'].endswith('/update') for c in f.peer.commands));b.close()
  finally:f.close()
 def test_view_management_unsaved_guard_cross_room_filter_and_correction(self):
  f=RoomFixture()
  try:
   with sync_playwright() as p:
    b=p.chromium.launch(headless=True,args=['--no-sandbox']);ctx=b.new_context(extra_http_headers={'X-Remote-User-Id':'admin'});page=ctx.new_page();page.goto(f.origin);page.locator('#new-name').fill('Management');page.locator('#create').click();expect(page.locator('#room-status')).to_contain_text('Frisch gelesen')
    page.locator('#room-new').click();page.locator('#dialog-input').fill('Virtuell');page.locator('#dialog-confirm').click();page.locator('#room-search').fill('light.fixture');page.locator('#room-select-visible').click();page.locator('#room-search').fill('');page.locator('#room-duplicate').click();expect(page.locator('#room-title')).to_have_value('Virtuell · Kopie');page.locator('#room-up').click();page.locator('#room-save').click();expect(page.locator('#room-dirty')).to_contain_text('Gespeichert');self.assertEqual(len(f.store.list('admin')[0]['roomPlan']['views']),2)
    page.locator('#room-title').fill('Gestaged');page.locator('#room-next').click();expect(page.locator('#dialog')).to_be_visible();page.locator('#dialog-cancel').click();expect(page.locator('#room-title')).to_have_value('Gestaged');page.locator('#room-next').click();page.locator('#dialog-confirm').click();expect(page.locator('#design-step')).to_be_visible();expect(page.locator('#design-dashboard')).to_contain_text('Dashboard:');page.locator('[data-step="2"]').click();expect(page.locator('#room-title')).to_have_value('Gestaged')
    page.locator('#room-delete').click();page.locator('#dialog-cancel').click();expect(page.locator('#room-title')).to_have_value('Gestaged');page.locator('#room-delete').click();page.locator('#dialog-confirm').click();page.locator('#room-save').click();expect(page.locator('#room-dirty')).to_contain_text('Gespeichert');self.assertEqual(len(f.store.list('admin')[0]['roomPlan']['views']),1)
    page.locator('#room-filter').select_option('selected');page.locator('[data-expand="dev"]').click();page.locator('[data-inspect-entity="registry:reg1"]').click();page.locator('#room-correction summary').click();page.locator('#correction-area').select_option('b');page.locator('#correction-preview').click();expect(page.locator('#correction-details')).to_contain_text('light.fixture');self.assertFalse(any(x['type'].endswith('/update') for x in f.peer.commands));page.locator('#correction-confirm').click();expect(page.locator('#notice')).to_contain_text('bestätigt');self.assertEqual(len([x for x in f.peer.commands if x['type'].endswith('/update')]),1)
    b.close()
  finally:f.close()
if __name__=='__main__':unittest.main()
