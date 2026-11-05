"""Bounded Core adapter. Native bootstrap fixes origin; constructor is a private diagnostic seam.
Only reads and explicit scoped turn_on/turn_off; no retry, proxy environment,
redirect, TLS bypass, logging or public arbitrary request API.
"""
import base64
import hashlib
import http.client
import json
import os
import re
import socket
import ssl
import struct
import time

MAX_BYTES=16*1024*1024
MAX_SECONDS=15
ENTITY=re.compile(r'[a-z_][a-z0-9_]*\.[a-z0-9_]{1,254}')

class ReadError(Exception):
    def __init__(self,code='upstream_unavailable',status=502):
        self.code=code;self.status=status
        super().__init__(code)

def parse_json(data):
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise ValueError()
            result[k]=v
        return result
    def constant(_):raise ValueError()
    return json.loads(data,object_pairs_hook=pairs,parse_constant=constant)

class Wire:
    """Single RFC6455 connection, bounded total traffic, frames and wall deadline."""
    def __init__(self,sock,deadline):
        self.sock=sock;self.deadline=deadline;self.bytes=0;self.frames=0
    def budget(self):
        remaining=self.deadline-time.monotonic()
        if remaining<=0:raise ReadError('upstream_timeout')
        self.sock.settimeout(min(3,remaining))
    def exact(self,n):
        if self.bytes+n>MAX_BYTES:raise ReadError('response_limit')
        self.bytes+=n;result=bytearray()
        while len(result)<n:
            self.budget();part=self.sock.recv(n-len(result))
            if not part:raise ReadError()
            result.extend(part)
        return bytes(result)
    def send(self,data,opcode=1):
        self.budget()
        if len(data)>8192:raise ReadError('request_limit')
        mask=os.urandom(4);length=len(data)
        prefix=bytes([128|opcode,128|(length if length<126 else 126)])
        if length>=126:prefix+=struct.pack('!H',length)
        self.sock.sendall(prefix+mask+bytes(b^mask[i%4] for i,b in enumerate(data)))
    def json_send(self,value):self.send(json.dumps(value,separators=(',',':')).encode())
    def message(self):
        parts=[];size=0;fragmented=False
        while True:
            self.frames+=1
            if self.frames>2048:raise ReadError('response_limit')
            a,b=self.exact(2);fin=bool(a&128);opcode=a&15;n=b&127
            if a&112 or b&128:raise ReadError('invalid_websocket')
            if n==126:
                n=struct.unpack('!H',self.exact(2))[0]
                if n<126:raise ReadError('invalid_websocket')
            elif n==127:
                n=struct.unpack('!Q',self.exact(8))[0]
                if n<65536 or n>>63:raise ReadError('invalid_websocket')
            if opcode>=8:
                if not fin or n>125:raise ReadError('invalid_websocket')
                data=self.exact(n)
                if opcode==9:self.send(data,10);continue
                if opcode==10:continue
                raise ReadError('upstream_closed')
            if opcode not in (0,1) or (opcode==0)!=fragmented:raise ReadError('invalid_websocket')
            size+=n
            if size>MAX_BYTES:raise ReadError('response_limit')
            parts.append(self.exact(n))
            if fin:
                value=parse_json(b''.join(parts).decode('utf-8'))
                if type(value) is not dict:raise ReadError('invalid_websocket')
                return value
            fragmented=True

class CoreClient:
    def __init__(self,token,*,host='supervisor',port=80,tls=False,api_prefix='/core/api/',ws_path='/core/websocket'):
        # These arguments are Python-only diagnostics, NEVER app options or HTTP input.
        if not isinstance(token,str) or not re.fullmatch(r'[!-~]{1,4096}',token):raise ReadError('credential_unavailable',503)
        if not isinstance(host,str) or not re.fullmatch(r'[A-Za-z0-9.:-]{1,253}',host) or type(port) is not int or not 1<=port<=65535 or type(tls) is not bool:raise ReadError('invalid_origin')
        if api_prefix not in ('/core/api/','/api/') or ws_path not in ('/core/websocket','/api/websocket'):raise ReadError('invalid_origin')
        self._token=token;self.host=host;self.port=port;self.tls=tls;self.api_prefix=api_prefix;self.ws_path=ws_path
    def __repr__(self):return '<CoreClient private credentials>'
    def _get(self,path,deadline):
        return self._exchange(path,deadline)
    def _exchange(self,path,deadline,body=None):
        # Private transport: the only writer is the narrowly validated turn().
        connection=None;watchdog=None;dispatched=False
        writing=body is not None
        try:
            remaining=deadline-time.monotonic()
            if remaining<=0:raise ReadError('upstream_timeout')
            cls=http.client.HTTPSConnection if self.tls else http.client.HTTPConnection
            connection=cls(self.host,self.port,timeout=min(3,remaining))
            connection.connect()
            sock=connection.sock
            def expire():
                try:sock.shutdown(socket.SHUT_RDWR)
                except OSError:pass
            from threading import Timer
            remaining=deadline-time.monotonic()
            if remaining<=0:raise ReadError('upstream_timeout')
            watchdog=Timer(remaining,expire);watchdog.daemon=True;watchdog.start()
            headers={'Authorization':'Bearer '+self._token,'Accept':'application/json','Accept-Encoding':'identity','Connection':'close'}
            if writing:headers['Content-Type']='application/json'
            dispatched=writing  # A send exception cannot prove nothing reached HA.
            connection.request('POST' if writing else 'GET',self.api_prefix+path,body=body,headers=headers)
            response=connection.getresponse()
            if not writing and response.status==404:return None
            if response.status!=200:
                if writing:raise ReadError('control_rejected' if 400<=response.status<500 else 'dispatch_unknown')
                raise ReadError('upstream_rejected')
            lengths=response.headers.get_all('Content-Length',[])
            transfer=response.headers.get_all('Transfer-Encoding',[])
            if (len(lengths)>1 or lengths and (not re.fullmatch(r'[0-9]{1,9}',lengths[0]) or int(lengths[0])>MAX_BYTES) or transfer and (lengths or transfer!=['chunked']) or response.headers.get('Content-Encoding','identity')!='identity' or response.headers.get('Content-Type','').split(';')[0]!='application/json'):raise ReadError('response_limit')
            body=bytearray()
            while True:
                remaining=deadline-time.monotonic()
                if remaining<=0:raise ReadError('upstream_timeout')
                if connection.sock:connection.sock.settimeout(min(3,remaining))
                part=response.read1(min(65536,MAX_BYTES+1-len(body)))
                if not part:break
                body.extend(part)
                if len(body)>MAX_BYTES:raise ReadError('response_limit')
            if lengths and len(body)!=int(lengths[0]):raise ReadError('invalid_response')
            return parse_json(body.decode('utf-8'))
        except ReadError as error:
            if dispatched and error.code not in ('control_rejected','dispatch_unknown'):raise ReadError('dispatch_unknown') from None
            raise
        except (OSError,ValueError,TypeError,RecursionError,UnicodeError,http.client.HTTPException):
            raise ReadError('dispatch_unknown' if dispatched else 'upstream_unavailable') from None
        finally:
            if watchdog is not None:watchdog.cancel();watchdog.join()
            if connection is not None:connection.close()
    def services(self,*,deadline=None):
        return self._get('services',deadline or time.monotonic()+MAX_SECONDS)
    def turn(self,entity,action,*,deadline=None):
        if type(entity) is not str or len(entity)>256 or not ENTITY.fullmatch(entity):raise ReadError('invalid_entity',400)
        domain=entity.split('.')[0]
        if domain not in ('light','switch','input_boolean') or action not in ('turn_on','turn_off'):raise ReadError('unsupported_control',400)
        result=self._exchange('services/'+domain+'/'+action,deadline or time.monotonic()+MAX_SECONDS,
            json.dumps({'entity_id':entity},separators=(',',':')).encode())
        if type(result) is not list:raise ReadError('dispatch_unknown')
    def state(self,entity,*,deadline=None):
        if type(entity) is not str or len(entity)>256 or not ENTITY.fullmatch(entity):raise ReadError('invalid_entity',400)
        return self._get('states/'+entity,deadline or time.monotonic()+MAX_SECONDS)
    def history(self,ids,start,end,*,deadline=None):
        from data import history_window,entity_id
        history_window(start,end)
        if type(ids) is not list or not 1<=len(ids)<=32 or len(set(ids))!=len(ids):raise ReadError('invalid_selection',400)
        for id in ids:entity_id(id)
        from urllib.parse import quote,urlencode
        from datetime import timedelta
        left,_=history_window(start,end)
        # Recorder uses strict > start. One millisecond of lookback admits the
        # exact left event despite float timestamp rounding; data.history filters
        # by original [start,end). Lookback rows still count toward response limits.
        try:acquisition_start=(left-timedelta(milliseconds=1)).isoformat()
        except OverflowError:raise ReadError('invalid_window',400) from None
        return self._get('history/period/'+quote(acquisition_start,safe='')+'?'+urlencode({'filter_entity_id':','.join(ids),'end_time':end,'skip_initial_state':'','significant_changes_only':'0'}),deadline or time.monotonic()+MAX_SECONDS)
    def registries(self):
        sock=None
        try:
            deadline=time.monotonic()+MAX_SECONDS
            sock=socket.create_connection((self.host,self.port),timeout=3)
            if self.tls:sock=ssl.create_default_context().wrap_socket(sock,server_hostname=self.host)
            wire=Wire(sock,deadline);key=base64.b64encode(os.urandom(16)).decode()
            authority=('['+self.host+']' if ':' in self.host else self.host)+':'+str(self.port)
            wire.budget();sock.sendall((f'GET {self.ws_path} HTTP/1.1\r\nHost: {authority}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Version: 13\r\nSec-WebSocket-Key: {key}\r\n\r\n').encode('ascii'))
            header=b''
            while not header.endswith(b'\r\n\r\n'):
                if len(header)>=8192:raise ReadError('response_limit')
                header+=wire.exact(1)
            lines=header.decode('ascii').split('\r\n');headers={}
            if not re.fullmatch(r'HTTP/1\.[01] 101 [^\r\n]*',lines[0]):raise ReadError('websocket_handshake')
            for line in lines[1:-2]:
                k,separator,v=line.partition(':');k=k.lower()
                if not separator or k in headers or not re.fullmatch(r'[a-z0-9-]+',k):raise ReadError('websocket_handshake')
                headers[k]=v.strip()
            expected=base64.b64encode(hashlib.sha1((key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
            if (headers.get('upgrade','').lower()!='websocket' or headers.get('connection','').lower()!='upgrade' or headers.get('sec-websocket-accept')!=expected or 'sec-websocket-extensions' in headers or 'sec-websocket-protocol' in headers):raise ReadError('websocket_handshake')
            if wire.message().get('type')!='auth_required':raise ReadError('upstream_auth')
            wire.json_send({'type':'auth','access_token':self._token})
            if wire.message().get('type')!='auth_ok':raise ReadError('upstream_auth')
            results=[]
            for i,registry in enumerate(('area','device','entity'),1):
                wire.json_send({'id':i,'type':f'config/{registry}_registry/list'})
                value=wire.message()
                if value.get('type')!='result' or type(value.get('id')) is not int or value['id']!=i or value.get('success') is not True or type(value.get('result')) is not list:raise ReadError('registry_unavailable')
                results.append(value['result'])
            return results
        except ReadError:raise
        except (OSError,ValueError,TypeError,RecursionError,UnicodeError):raise ReadError() from None
        finally:
            if sock is not None:sock.close()
