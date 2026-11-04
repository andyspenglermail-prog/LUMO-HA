"""Authenticated ingress pages and bounded fixed-protocol HTTPS client."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from socketserver import TCPServer
from urllib.parse import urlsplit
import json
import re
from bridge import route, settings, forward, SAFE_ID
from validation import request_body, InvalidRequest


def create_server(index_path, bind=('127.0.0.1',0), *, trusted_proxy_ip='172.30.32.2', options_path='/data/options.json', options_snapshot=None):
    """Trust/path injection only for offline tests; main has fixed native values."""
    pages={}
    for target,path in (('/index.html',Path(index_path)),('/devicebook.html',Path(index_path).with_name('devicebook.html'))):
        with path.open('rb') as f: data=f.read(1048577)
        if len(data)>1048576: raise ValueError('Page exceeds 1 MiB')
        pages[target]=data
    pages['/']=pages['/index.html']
    class Handler(BaseHTTPRequestHandler):
        timeout=6
        def log_message(self,*args): pass
        def version_string(self): return 'LUMO'
        def send_error(self,code,message=None,explain=None):
            self.close_connection=True
            self.reply(405 if code==501 else code,b'Request rejected\n','text/plain; charset=utf-8')
        def reply(self,status,body,kind='application/json'):
            self.close_connection=True
            self.send_response(status)
            for k,v in [('Content-Type',kind),('Content-Length',str(len(body))),('X-Content-Type-Options','nosniff'),('Cache-Control','no-store'),('X-Frame-Options','SAMEORIGIN'),('Content-Security-Policy',"frame-ancestors 'self'"),('Connection','close')]: self.send_header(k,v)
            self.end_headers()
            if self.command!='HEAD': self.wfile.write(body)
        def api(self,status,value): self.reply(status,json.dumps(value,ensure_ascii=False,separators=(',',':')).encode())
        def error(self,status,code): self.api(status,{'error':code})
        def work(self):
            target=self.requestline.split()[1]
            op=route(self.command,target)
            mutation=op is not None and op!='poll'
            # Single framing, no chunking, bodies forbidden on GET/HEAD.
            lengths=self.headers.get_all('Content-Length',[])
            if (self.headers.get_all('Transfer-Encoding') or len(lengths)>1 or
                    (lengths and not re.fullmatch(r'[0-9]{1,5}',lengths[0]))):
                self.error(400,'invalid_request');return
            size=int(lengths[0]) if lengths else 0
            if size>16384: self.error(413,'body_too_large');return
            if not mutation and size: self.error(400,'invalid_request');return
            if self.command in ('GET','HEAD') and target=='/health':
                self.reply(200,b'ok\n','text/plain; charset=utf-8');return
            static=self.command in ('GET','HEAD') and target in pages
            identity=self.command=='GET' and target=='/lumo/v1/identity'
            if not static and not identity and op is None:
                self.error(404,'not_found');return
            users=self.headers.get_all('X-Remote-User-Id',[])
            if self.client_address[0]!=trusted_proxy_ip or len(users)!=1 or not SAFE_ID.fullmatch(users[0]):
                self.error(403,'forbidden');return
            if static: self.reply(200,pages[target],'text/html; charset=utf-8');return
            # Browser custom-header + no CORS; fail closed when an Origin is present
            # and cannot be verified against the HTTP authority delivered by ingress.
            fetch=self.headers.get_all('Sec-Fetch-Site',[])
            origins=self.headers.get_all('Origin',[])
            if len(fetch)>1 or (fetch and fetch[0] not in ('same-origin','none')):
                self.error(403,'forbidden');return
            if origins:
                hosts=self.headers.get_all('Host',[])
                try:
                    origin=urlsplit(origins[0])
                    valid=(len(origins)==1 and len(hosts)==1 and origin.scheme in ('http','https') and origin.netloc==hosts[0]
                           and not origin.path and not origin.query and not origin.fragment and not origin.username)
                except ValueError: valid=False
                if not valid: self.error(403,'forbidden');return
            config=options_snapshot.current() if options_snapshot is not None else settings(options_path)
            if identity:
                self.api(200,{'user_id':users[0],'model_access_allowed':bool(config and users[0] in config[4]),'bridge_configured':bool(config)});return
            if mutation:
                if (self.headers.get_all('X-LUMO-Request',[])!=['1'] or self.headers.get_all('Content-Type',[])!=['application/json'] or len(lengths)!=1):
                    self.error(400,'invalid_request');return
            if not config or users[0] not in config[4]: self.error(403,'forbidden');return
            try:
                raw=self.rfile.read(size) if size else b''
                if len(raw)!=size: raise InvalidRequest()
                request_body(raw,op)
            except (InvalidRequest,OSError) as e:
                self.error(e.status if isinstance(e,InvalidRequest) else 400,e.code if isinstance(e,InvalidRequest) else 'invalid_request');return
            # Body reads and HTTPS waits may cross a Supervisor settings update.
            # Never admit or release text using an observed stale startup policy.
            if options_snapshot is not None and options_snapshot.current() is not config:
                self.error(403,'forbidden');return
            status,value=forward(config,users[0],self.command,target,raw)
            if options_snapshot is not None and options_snapshot.current() is not config:
                self.error(403,'forbidden');return
            self.api(status,value)
        do_GET=work
        do_HEAD=work
        do_POST=work
        do_DELETE=work
    server=HTTPServer(bind,Handler,bind_and_activate=False)
    try:
        TCPServer.server_bind(server)
        server.server_name,server.server_port=server.server_address
        server.server_activate()
    except BaseException: server.server_close();raise
    return server

def main(*, options_snapshot=None):
    import os
    if os.getresuid() != (65532,)*3 or os.getresgid() != (65532,)*3 or os.getgroups() or options_snapshot is None:
        raise RuntimeError('safe_bootstrap_required')
    with create_server(Path(__file__).with_name('index.html'),bind=('0.0.0.0',8099),trusted_proxy_ip='172.30.32.2',options_snapshot=options_snapshot) as server:
        server.serve_forever()
if __name__=='__main__': main()
