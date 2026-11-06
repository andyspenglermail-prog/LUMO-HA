"""Test-only loopback ingress simulator: strips prefix, forwards real HTTP.
Can intentionally lose a write response after upstream committed; no mocked fetch.
"""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import threading,http.client,socket
class Proxy:
    def __init__(self,fixture,prefix='/api/hassio_ingress/test-token/'):
        self.fixture=fixture;self.prefix=prefix;self.drop_next_post=False;self.requests=[];self.responses=[];self.lose_read_after_post=None;self.lost_read_path=None;outer=self
        self.hold_response=None;self.response_arrived=threading.Event();self.release_response=threading.Event()
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):self.proxy()
            def do_POST(self):self.proxy()
            def proxy(self):
                if not self.path.startswith(outer.prefix):self.send_error(404);return
                path='/'+self.path[len(outer.prefix):];outer.requests.append((self.command,path))
                headers=dict(self.headers);headers['X-Remote-User-Id']=self.headers.get('X-Remote-User-Id','alice')
                body=self.rfile.read(int(headers.get('Content-Length','0'))) or None
                c=http.client.HTTPConnection('127.0.0.1',fixture.port,timeout=30);c.request(self.command,path,body,headers);r=c.getresponse();raw=r.read()
                outer.responses.append((self.command,path,r.status))
                if outer.hold_response==(self.command,path):
                    outer.hold_response=None;outer.response_arrived.set()
                    if not outer.release_response.wait(30):c.close();self.connection.close();return
                if self.command=='POST' and outer.lose_read_after_post and path==outer.lose_read_after_post[0] and 200<=r.status<300:
                    outer.lost_read_path=outer.lose_read_after_post[1];outer.lose_read_after_post=None
                if self.command=='GET' and path==outer.lost_read_path:
                    c.close();self.connection.shutdown(socket.SHUT_RDWR);self.connection.close();return
                if self.command=='POST' and outer.drop_next_post:
                    outer.drop_next_post=False;c.close();self.connection.shutdown(socket.SHUT_RDWR);self.connection.close();return
                self.send_response(r.status)
                for k,v in r.getheaders():
                    if k.lower() not in ('server','date','connection'):self.send_header(k,v)
                try:
                    self.send_header('Connection','close');self.end_headers();self.wfile.write(raw)
                except (BrokenPipeError,ConnectionResetError):pass  # browser context closed after a read
                finally:c.close()
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.origin='http://127.0.0.1:'+str(self.server.server_address[1]);self.url=self.origin+self.prefix
    def close(self):self.server.shutdown();self.server.server_close();self.thread.join()
