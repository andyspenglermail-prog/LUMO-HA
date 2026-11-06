import unittest,pathlib,sys,json,http.client,socket,base64,copy,tempfile,io
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from test_http import Fixture
from test_images import png
from PIL import Image
class SecurityTests(unittest.TestCase):
    def setUp(self):self.f=Fixture();self.csrf=self.f.request('GET','/api/session')[1]['csrf']
    def tearDown(self):self.f.close()
    def post(self,path,v,user='alice',csrf=None):return self.f.request('POST',path,v,user=user,extra={'X-LUMO-CSRF':csrf or self.csrf})
    def test_image_http_auth_decode_restart_and_wrong_owner(self):
        status,im=self.post('/api/images',{'name':'Synthetisch','data':base64.b64encode(png()).decode()});self.assertEqual(status,201)
        self.assertEqual(self.f.request('GET','/api/images/'+im['id'])[1],png());self.assertEqual(self.f.request('GET','/api/images/'+im['id'],user='bob')[0],404)
        bob=self.f.request('GET','/api/session',user='bob')[1]['csrf'];_,d=self.post('/api/dashboards',{'name':'Bobs Entwurf','icon':''},user='bob',csrf=bob);d['settings']['background']['imageId']=im['id']
        self.assertEqual(self.post('/api/dashboards/'+d['id']+'/save',{'revision':1,'patch':{'settings':d['settings']}},user='bob',csrf=bob)[0],404)
        for data in [b'<svg/>',png()[:-20],b'bad',png(size=(4097,1))]:self.assertEqual(self.post('/api/images',{'name':'Bad','data':base64.b64encode(data).decode()})[0],422)
        for fmt in ('JPEG','WEBP'):
            out=io.BytesIO();Image.new('RGB',(6,6),'red').save(out,format=fmt);status,result=self.post('/api/images',{'name':fmt,'data':base64.b64encode(out.getvalue()).decode()});self.assertEqual(status,201);self.assertEqual(result['mime'],'image/png')
        self.f.stop();self.f.start();self.assertEqual(self.f.request('GET','/api/images/'+im['id'])[1],png())
    def test_malformed_duplicate_headers_deep_and_denied_requests(self):
        def raw(body,headers=(),user='alice'):
            c=http.client.HTTPConnection('127.0.0.1',self.f.port);c.putrequest('POST','/api/dashboards');pairs=[('X-Remote-User-Id',user),('X-LUMO-Read','1'),('X-LUMO-Action','1'),('X-LUMO-CSRF',self.csrf),('Origin',self.f.origin),('Content-Type','application/json'),('Content-Length',str(len(body)))]+list(headers)
            for k,v in pairs:c.putheader(k,v)
            c.endheaders(body);r=c.getresponse();data=r.read();c.close();return r.status,data
        for body in [b'{"name":"a","name":"b","icon":""}',b'{"name":NaN,"icon":""}',b'{"name":'+b'['*1000+b'0'+b']'*1000+b',"icon":""}',b'null',b'[]',b'{"name":"\\ud800","icon":""}']:
            self.assertIn(raw(body)[0],(400,422));self.assertEqual(raw(body,user='denied')[0],403)
        for h in [('X-Remote-User-Id','alice'),('X-LUMO-CSRF',self.csrf),('Origin',self.f.origin),('X-LUMO-Action','1'),('Content-Length','22'),('Transfer-Encoding','chunked')]:
            status,body=raw(b'{"name":"a","icon":""}',[h]);self.assertIn(status,(400,403));self.assertNotIn(b'Traceback',body)
        self.assertEqual(self.f.store.list('alice'),[])
        self.assertEqual(self.f.request('GET','/api/dashboards',extra={'Sec-Fetch-Site':'cross-site'})[0],403)
        self.assertEqual(self.post('/api/dashboards',{'name':'x','icon':''},user='bob')[0],403)
        self.assertEqual(self.f.request('POST','/api/services/light/turn_on',{})[0],403)
        self.assertEqual(self.post('/api/proxy',{'type':'call_service'})[0],404)
    def test_untrusted_peer_cannot_spoof_ingress(self):
        self.f.stop();self.f.trusted='172.30.32.2';self.f.start()
        self.assertEqual(self.f.request('GET','/api/session',extra={'X-Forwarded-For':'172.30.32.2'})[0],403)
        self.assertEqual(self.f.request('GET','/health')[0],200)
    def test_actual_admin_gate_and_atomic_reject_preserves_both_sides(self):
        before=copy.deepcopy(self.f.peer.configs)
        self.assertEqual(self.f.request('GET','/api/ha/dashboards',user='bob')[0],403)
        status,rows=self.f.request('GET','/api/ha/dashboards');self.assertEqual(status,200);self.assertEqual([r['viewCount'] for r in rows['dashboards']],[1,1,1])
        status,value=self.post('/api/ha/import',{'path':'bad-dashboard','name':'Bad'});self.assertEqual(status,201);self.assertEqual(value['native'],before['bad-dashboard']);self.assertEqual(len(self.f.store.list('alice')),1)
        status,d=self.post('/api/ha/import',{'path':'fixture-dashboard','name':'Kopie'});self.assertEqual(status,201);self.assertEqual(d['native'],before['fixture-dashboard'])
        self.f.peer.users[0]['is_active']=False;self.assertEqual(self.f.request('GET','/api/ha/dashboards')[0],403);self.assertEqual(self.f.peer.configs,before)
    def test_default_disabled_is_honest_and_serves_app(self):
        other=Fixture(enabled=False)
        try:
            self.assertEqual(other.request('GET','/')[0],200);status,s=other.request('GET','/api/session');self.assertEqual(status,200);self.assertFalse(s['ready']);self.assertEqual(s.get('userId'),'alice');self.assertIsNone(s['csrf']);self.assertIn('enabled',s['message']);self.assertEqual(other.peer.commands,[])
        finally:other.close()
if __name__=='__main__':unittest.main()
