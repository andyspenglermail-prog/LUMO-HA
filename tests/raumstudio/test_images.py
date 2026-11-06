import sys,unittest,tempfile,pathlib,io,sqlite3
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'lumo_raumstudio'))
from store import Store,defaults
from PIL import Image

def png(color='red',size=(12,8)):
    b=io.BytesIO();Image.new('RGBA',size,color).save(b,format='PNG');return b.getvalue()
class ImageTests(unittest.TestCase):
    def test_decoded_owned_immutable_images_and_background(self):
        with tempfile.TemporaryDirectory() as t:
            s=Store(pathlib.Path(t)/'studio.sqlite');r=s.put_image('alice','Test.png',png())
            self.assertIsInstance(r,dict,'Upload must persist decoded image bytes')
            self.assertEqual(s.image('alice',r['id'])[1],png())
            with self.assertRaises(Exception):s.image('bob',r['id'])
            for raw in [b'<svg></svg>',png()[:40],b'x'*(8*1024*1024+1),png(size=(4097,1))]:
                with self.subTest(length=len(raw)),self.assertRaises(Exception):s.put_image('alice','Bad',raw)
            d=s.create('alice','Bild');sett=defaults();sett['background']['imageId']=r['id'];s.update('alice',d['id'],1,{'settings':sett})
            self.assertEqual(Store(s.path).images('alice'),[r])
            sett['background']['imageId']=None;s.update('alice',d['id'],2,{'settings':sett})
            self.assertEqual(s.image('alice',r['id'])[1],png())
if __name__=='__main__':unittest.main()
