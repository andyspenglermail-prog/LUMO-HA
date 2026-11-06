"""Authenticated reads and explicit capability ingress; no generic proxy routes."""
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import TCPServer
from pathlib import Path
from urllib.parse import urlsplit,parse_qsl
import json
import re
import socket
from threading import Timer
from policy import SAFE_ID
from client import ReadError,parse_json
from control import ControlSessions,execute_control
from capabilities import MISSING
from data import discovery,states,selected_ids,history
from dashboard_reads import dashboard_list,dashboard_config
from dashboard_publish import DashboardSessions,validate_request,MAX_BODY

def create_server(index_path,bind=('127.0.0.1',0),*,options_snapshot,client,trusted_proxy_ip='172.30.32.2'):
    page=Path(index_path).read_bytes()
    if len(page)>2*1024*1024:raise ValueError('page_limit')
    sessions=ControlSessions()
    dashboard_sessions=DashboardSessions()
    class HeaderReader:
        """Bound all header bytes, not just each individual HTTP line."""
        def __init__(self,stream):self.stream=stream;self.remaining=32768
        def readline(self,limit=-1):
            line=self.stream.readline(min(limit,self.remaining+1) if limit>=0 else self.remaining+1)
            self.remaining-=len(line)
            if self.remaining<0:raise OSError('header_limit')
            return line
        def read(self,n):return self.stream.read(n)
        def close(self):self.stream.close()
    class Handler(BaseHTTPRequestHandler):
        timeout=5
        def setup(self):
            super().setup();self.rfile=HeaderReader(self.rfile)
        def finish_headers(self):
            self.header_timer.cancel();self.header_timer.join()
        def handle_one_request(self):
            # One synchronous request + one watchdog: no unbounded worker pool.
            # Socket idle timeouts alone allow an infinite slow-header drip.
            def expire():
                try:self.connection.shutdown(socket.SHUT_RDWR)
                except OSError:pass
            self.header_timer=Timer(2,expire);self.header_timer.daemon=True;self.header_timer.start()
            try:super().handle_one_request()
            finally:self.finish_headers()
        def log_message(self,*args):pass
        def version_string(self):return 'LUMO'
        def send_error(self,code,message=None,explain=None):self.error(405 if code==501 else code,'invalid_request')
        def reply(self,status,body,kind='application/json'):
            self.close_connection=True;self.send_response(status)
            for k,v in [('Content-Type',kind),('Content-Length',str(len(body))),('Cache-Control','no-store'),('X-Content-Type-Options','nosniff'),('X-Frame-Options','SAMEORIGIN'),('Content-Security-Policy',"frame-ancestors 'self'"),('Connection','close')]:self.send_header(k,v)
            self.end_headers()
            if self.command!='HEAD':self.wfile.write(body)
        def api(self,status,value):self.reply(status,json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode())
        def error(self,status,code):self.api(status,{'error':code})
        def work(self):
            self.finish_headers()
            try:self.handle_read()
            except ReadError as e:self.error(e.status,e.code)
            except (OSError,ValueError,TypeError,KeyError,RecursionError):self.error(502,'read_unavailable')
        def handle_read(self):
            target=self.requestline.split()[1]
            hosts=self.headers.get_all('Host',[])
            if len(hosts)!=1 or not re.fullmatch(r'[A-Za-z0-9.\[\]:_-]{1,300}',hosts[0]) or self.headers.get_all('Expect'):raise ReadError('invalid_request',400)
            create=target=='/lumo/data/v1/dashboard-create' and self.command=='POST'
            create_session=target=='/lumo/data/v1/dashboard-create-session' and self.command=='GET'
            control=target=='/lumo/data/v1/control' and self.command=='POST'
            session=target=='/lumo/data/v1/control-session' and self.command=='GET'
            lengths=self.headers.get_all('Content-Length',[])
            if self.headers.get_all('Transfer-Encoding') or len(lengths)>1:raise ReadError('invalid_request',400)
            if control or create:
                limit=MAX_BODY if create else 2048
                if len(lengths)!=1 or not re.fullmatch(r'[1-9][0-9]{0,6}',lengths[0]) or int(lengths[0])>limit:raise ReadError('request_limit',400)
                if self.headers.get_all('Content-Type',[])!=['application/json']:raise ReadError('invalid_request',400)
            elif lengths and lengths!=['0']:raise ReadError('invalid_request',400)
            if self.command not in ('GET','HEAD') and not (control or create):raise ReadError('read_only',405)
            if target=='/health':self.reply(200,b'ok\n','text/plain');return
            static=target in ('/','/index.html')
            catalog=target=='/lumo/data/v1/catalog'
            dashboards_route=target=='/lumo/data/v1/dashboards'
            dashboard_route=target.startswith('/lumo/data/v1/dashboard?')
            state_route=target.startswith('/lumo/data/v1/states?')
            history_route=target.startswith('/lumo/data/v1/history?')
            if len(target)>12000:raise ReadError('request_limit',400)
            if not static and not (control or create) and (self.command!='GET' or not (catalog or state_route or history_route or session or dashboards_route or dashboard_route or create_session)):raise ReadError('not_found',404)
            users=self.headers.get_all('X-Remote-User-Id',[])
            if self.client_address[0]!=trusted_proxy_ip or len(users)!=1 or not SAFE_ID.fullmatch(users[0]):raise ReadError('forbidden',403)
            if static:self.reply(200,page,'text/html; charset=utf-8');return
            if self.headers.get_all('X-LUMO-Read',[])!=['1']:raise ReadError('forbidden',403)
            fetch=self.headers.get_all('Sec-Fetch-Site',[]);origins=self.headers.get_all('Origin',[])
            if len(fetch)>1 or fetch and fetch[0] not in ('same-origin','none'):raise ReadError('forbidden',403)
            if origins:
                hosts=self.headers.get_all('Host',[])
                try:
                    origin=urlsplit(origins[0]);valid=len(origins)==1 and len(hosts)==1 and origin.scheme in ('http','https') and origin.netloc==hosts[0] and not (origin.path or origin.query or origin.fragment or origin.username)
                except ValueError:valid=False
                if not valid:raise ReadError('forbidden',403)
            if (control or create) and (not origins or fetch and fetch!=['same-origin'] or self.headers.get_all('X-LUMO-Action',[])!=['1']):raise ReadError('forbidden',403)
            # Browsers omit Origin on same-origin GET. Custom headers/no CORS
            # still prevent cross-origin session issuance, including plain HTTP.
            if create_session and (fetch and fetch!=['same-origin'] or self.headers.get_all('X-LUMO-Action',[])!=['1']):raise ReadError('forbidden',403)
            policy=options_snapshot.current()
            if policy is None:raise ReadError(getattr(options_snapshot,'error_code',None) or 'configuration_invalid',403)
            if users[0] not in policy.users:raise ReadError('user_not_allowed',403)
            def guard():
                if options_snapshot.current() is not policy:raise ReadError('options_changed',403)
            guard()
            if create_session:
                client.dashboard_admin(users[0]);guard()
                result=dashboard_sessions.issue(users[0],policy)
            elif session:result=sessions.issue(users[0],policy)
            elif control or create:
                def expire_body():
                    try:self.connection.shutdown(socket.SHUT_RDWR)
                    except OSError:pass
                timer=Timer(2,expire_body);timer.daemon=True;timer.start()
                try:
                    body=self.rfile.read(int(lengths[0]))
                    if len(body)!=int(lengths[0]):raise ReadError('invalid_request',400)
                    value=parse_json(body.decode('utf-8'))
                except (OSError,ValueError,UnicodeError,RecursionError):raise ReadError('invalid_request',400) from None
                finally:timer.cancel();timer.join()
                if create:
                    validate_request(value,policy)
                    guard();dashboard_sessions.consume(value['token'],users[0],policy)
                    result=client.create_dashboard(value,users[0],policy,guard)
                    self.api(200,result);return
                if type(value) is not dict or set(value) not in ({'entityId','action','token'},{'entityId','action','token','value'}) or any(type(value[k]) is not str for k in ('entityId','action','token')):raise ReadError('invalid_request',400)
                if not re.fullmatch(r'[A-Za-z0-9_-]{43}',value['token']):raise ReadError('invalid_control_token',403)
                guard();sessions.consume(value['token'],users[0],policy)
                ids=selected_ids(value['entityId'],policy)
                if len(ids)!=1:raise ReadError('invalid_selection',400)
                result=execute_control(client,policy,ids[0],value['action'],guard,value.get('value',MISSING))
            elif dashboards_route:result=dashboard_list(client,guard)
            elif dashboard_route:
                # Canonical unescaped slug only; reject duplicate/opaque query fields.
                match=re.fullmatch(r'/lumo/data/v1/dashboard\?url_path=([a-z0-9][a-z0-9_-]{0,127})',target)
                if not match:raise ReadError('invalid_dashboard_path',400)
                result=dashboard_config(client,policy,match[1],guard)
            elif catalog:result=discovery(client,policy)
            else:
                pairs=parse_qsl(target.split('?',1)[1],keep_blank_values=True,strict_parsing=True,max_num_fields=3)
                query=dict(pairs)
                if len(query)!=len(pairs) or set(query)!=({'entity_ids','start','end'} if history_route else {'entity_ids'}):raise ReadError('invalid_request',400)
                ids=selected_ids(query['entity_ids'],policy)
                result=history(client,ids,query['start'],query['end'],guard) if history_route else states(client,ids,guard)
            guard()
            self.api(200,result)
        do_GET=work
        do_HEAD=work
        do_POST=work
        do_PUT=work
        do_DELETE=work
        do_PATCH=work
        do_OPTIONS=work
    class QuietServer(HTTPServer):
        request_queue_size=5
        def verify_request(self,request,client_address):
            # Before Handler construction or any request-line/header parsing.
            # Loopback may reach health only; handle_read still gates all other
            # routes on the exact ingress peer and identity (no forwarded-IP trust).
            return client_address[0] in (trusted_proxy_ip,'127.0.0.1')
        def handle_error(self,request,client_address):pass  # Never log private request context.
    server=QuietServer(bind,Handler,bind_and_activate=False)
    try:
        TCPServer.server_bind(server);server.server_name,server.server_port=server.server_address;server.server_activate()
    except BaseException:server.server_close();raise
    return server

def main(*,options_snapshot=None):
    import os
    from client import CoreClient
    if os.getresuid()!=(65532,)*3 or os.getresgid()!=(65532,)*3 or os.getgroups() or options_snapshot is None:raise RuntimeError('safe_bootstrap_required')
    # Official native environment only. Never options, browser headers or CLI argv.
    client=CoreClient(os.environ.pop('SUPERVISOR_TOKEN',''))
    with create_server(Path(__file__).with_name('index.html'),bind=('0.0.0.0',8099),options_snapshot=options_snapshot,client=client,trusted_proxy_ip='172.30.32.2') as server:
        server.serve_forever()

if __name__=='__main__':
    import sys
    print('LUMO startup unavailable',file=sys.stderr)
    sys.exit(3)
