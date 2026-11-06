"""Synthetic RFC6455 HA peer. Test-only; never included in image."""
import base64,hashlib,json,struct,socketserver,threading,copy
CONFIG={'title':'Synthetisches Dashboard','views':[{'title':'Testansicht','path':'test','type':'masonry','cards':[{'type':'entity','entity':'sensor.synthetic','name':'Testwert'}]}]}
class Peer:
    def __init__(self):
        self.commands=[];self.users=[{'id':'alice','is_active':True,'is_owner':False,'group_ids':['system-admin']},{'id':'bob','is_active':True,'is_owner':False,'group_ids':['system-users']}]
        self.configs={'fixture-dashboard':copy.deepcopy(CONFIG),'bad-dashboard':{'views':[{'title':'Nicht unterstützt','cards':[{'type':'custom:unknown'}]}]},None:copy.deepcopy(CONFIG)}
        self.resources=[{'id':'fixture','url':'https://external.invalid/custom.js','type':'module','unknown':{'__proto__':True}}]
        peer=self
        class Handler(socketserver.StreamRequestHandler):
            def handle(self):
                self.request.settimeout(3);line=self.rfile.readline();headers={}
                while True:
                    l=self.rfile.readline()
                    if l==b'\r\n':break
                    if not l:return
                    k,v=l.decode().split(':',1);headers[k.lower()]=v.strip()
                key=base64.b64encode(hashlib.sha1((headers['sec-websocket-key']+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest())
                self.wfile.write(b'HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: '+key+b'\r\n\r\n')
                def send(v):
                    b=json.dumps(v).encode();n=len(b);self.wfile.write(bytes([129,n]) + b if n<126 else bytes([129,126])+struct.pack('!H',n)+b)
                def receive():
                    h=self.rfile.read(2)
                    if len(h)!=2:return None
                    n=h[1]&127
                    if n==126:n=struct.unpack('!H',self.rfile.read(2))[0]
                    elif n==127:n=struct.unpack('!Q',self.rfile.read(8))[0]
                    assert n<2000000 and h[1]&128
                    mask=self.rfile.read(4);b=self.rfile.read(n)
                    return json.loads(bytes(x^mask[i%4] for i,x in enumerate(b)))
                send({'type':'auth_required'});auth=receive();assert auth=={'type':'auth','access_token':'synthetic-test-token'};send({'type':'auth_ok'})
                while True:
                    cmd=receive()
                    if cmd is None:break
                    peer.commands.append(cmd.copy());kind=cmd['type']
                    if kind=='config/auth/list':result=peer.users
                    elif kind=='lovelace/dashboards/list':result=[{'url_path':p,'title':p,'mode':'storage','require_admin':False,'show_in_sidebar':True,'icon':'mdi:home'} for p in peer.configs if p]
                    elif kind=='lovelace/config':result=peer.configs.get(cmd.get('url_path'))
                    elif kind=='lovelace/resources/list':result=peer.resources
                    else:raise AssertionError('Forbidden HA command '+kind)
                    send({'id':cmd['id'],'type':'result','success':result is not None,'result':result,'error':{'code':'config_not_found'} if result is None else None})
        class Server(socketserver.ThreadingTCPServer):
            allow_reuse_address=True;daemon_threads=True
        self.server=Server(('127.0.0.1',0),Handler);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def close(self):self.server.shutdown();self.server.server_close();self.thread.join()
