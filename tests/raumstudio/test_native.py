import sys,pathlib,tempfile,unittest,base64,io,copy
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'lumo_raumstudio'))
from store import Store,defaults
from native import background_css,compile_native
from test_images import png
from PIL import Image
from peer import CONFIG
class NativeTests(unittest.TestCase):
    def test_self_contained_alpha_scale_and_view_precedence(self):
        with tempfile.TemporaryDirectory() as t:
            s=Store(pathlib.Path(t)/'s.sqlite');im=s.put_image('alice','Probe',png());bg=defaults()['background'];bg.update(imageId=im['id'],opacity=0,mode='scale',scale=137,position='right bottom',attachment='fixed')
            css=background_css(s,'alice',bg);self.assertIn('data:image/png;base64,',css,'Native output cannot depend on an ingress image URL')
            self.assertIn('137% auto',css);self.assertIn('right bottom',css);self.assertIn('fixed',css)
            raw=base64.b64decode(css.split('base64,')[1].split('"')[0]);self.assertEqual(Image.open(io.BytesIO(raw)).getextrema()[3],(0,0))
            cfg=copy.deepcopy(CONFIG);cfg['views'][0]['background']='#ff0000';cfg['views'].append({'title':'Erbt','path':'inherit','cards':[]})
            d=s.import_native('alice','Native',cfg);d['settings']['background']=bg;d['settings']['navigation'].update(showIconAndTitle=False,startView=d['views'][1]['id'])
            self.assertEqual(compile_native(s,'alice',d),cfg)  # New imports ignore overlays.
            d.pop('nativeImport')  # Explicit legacy 0.12.0 envelope: retain its mapping proof.
            result=compile_native(s,'alice',d);self.assertEqual(result['views'][0]['title'],'Erbt');self.assertEqual(result['views'][1]['background'],'#ff0000');self.assertEqual(result['background'],css);self.assertFalse(result['views'][0]['show_icon_and_title'])
            self.assertEqual(d['native'],cfg)
if __name__=='__main__':unittest.main()
