import sys,pathlib,tempfile,threading,http.client,json,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'lumo_raumstudio'))
from store import Store
from server import create_server
from policy import load_snapshot
from client import CoreClient
from peer import Peer
class Fixture:
    def __init__(self,enabled=True,trusted='127.0.0.1'):
        self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name)
        self.options=self.root/'options.json';self.options.write_text(json.dumps({'enabled':enabled,'allowed_user_ids':['alice','bob'] if enabled else []}))
        self.store=Store(self.root/'studio.sqlite');self.peer=Peer();self.trusted=trusted;self.start()
    def start(self):
        self.server=create_server(store=self.store,options_snapshot=load_snapshot(str(self.options)),client=CoreClient('synthetic-test-token',host='127.0.0.1',port=self.peer.server.server_address[1]),trusted_proxy_ip=self.trusted)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.port=self.server.server_address[1];self.origin=f'http://127.0.0.1:{self.port}'
    def stop(self):self.server.shutdown();self.server.server_close();self.thread.join()
    def close(self):self.stop();self.peer.close();self.tmp.cleanup()
    def request(self,method,path,value=None,user='alice',extra=None):
        h={'X-Remote-User-Id':user,'X-LUMO-Read':'1','Origin':self.origin,'X-LUMO-Action':'1'}
        if extra:h.update(extra)
        body=None if value is None else json.dumps(value)
        if body is not None:h['Content-Type']='application/json'
        c=http.client.HTTPConnection('127.0.0.1',self.port,timeout=10);c.request(method,path,body,h);r=c.getresponse();raw=r.read();status=r.status;c.close()
        try:return status,json.loads(raw)
        except ValueError:return status,raw
class HTTPTests(unittest.TestCase):
    def setUp(self):self.f=Fixture()
    def tearDown(self):self.f.close()
    def test_create_readback_owner_and_restart(self):
        # A session can be fetched only by same-origin custom-header requests.
        status,session=self.f.request('GET','/api/session')
        csrf=session.get('csrf','not-implemented') if isinstance(session,dict) else 'not-implemented'
        status,d=self.f.request('POST','/api/dashboards',{'name':'Über HTTP','icon':''},extra={'X-LUMO-CSRF':csrf})
        self.assertEqual(status,201,'Local creation must succeed with a valid ingress session')
        self.assertEqual(self.f.request('GET','/api/dashboards/'+d['id'])[1],d)
        self.assertEqual(self.f.request('GET','/api/dashboards/'+d['id'],user='bob')[0],404)
        self.f.stop();self.f.store=Store(self.f.store.path);self.f.start()
        self.assertEqual(self.f.request('GET','/api/dashboards/'+d['id'])[1],d)
    def test_origin_csrf_and_disabled_setup(self):
        self.assertEqual(self.f.request('POST','/api/dashboards',{'name':'X'})[0],403)
        self.assertEqual(self.f.request('GET','/api/session',extra={'Origin':'https://evil.invalid'})[0],403)
        self.assertEqual(self.f.request('GET','/api/session',user='not-allowed')[0],403)
        self.f.options.write_text(json.dumps({'enabled':False,'allowed_user_ids':[]}))
        self.assertEqual(self.f.request('GET','/api/dashboards')[0],403)
if __name__=='__main__':unittest.main()
