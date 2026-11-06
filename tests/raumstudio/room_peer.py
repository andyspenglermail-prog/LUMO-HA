"""Protocol-only synthetic inventory; production never imports tests."""
import copy,json,base64,hashlib,struct,socketserver,threading
DATA={
 'areas':[{'area_id':'a','name':'Gleicher Name','floor_id':'f'},{'area_id':'b','name':'Gleicher Name','floor_id':None}],
 'floors':[{'floor_id':'f','name':'Fixture Etage','level':1}],
 'devices':[{'id':'dev','name':'Fixture Gerät','area_id':'a','manufacturer':'Fixture','model':'Multi','via_device_id':None},{'id':'empty','name':'Ohne Funktionen','area_id':None}],
 'entities':[{'id':'reg1','entity_id':'light.fixture','device_id':'dev','area_id':None,'name':'Fixture Licht','disabled_by':None,'hidden_by':None,'entity_category':None},{'id':'reg2','entity_id':'sensor.fixture','device_id':'dev','area_id':'b','name':None,'original_name':'Messwert','disabled_by':None,'hidden_by':'user','entity_category':'diagnostic'},{'id':'reg3','entity_id':'switch.disabled','device_id':'dev','area_id':None,'disabled_by':'integration'},{'id':'reg4','entity_id':'sensor.loose','device_id':None,'area_id':None}],
 'states':[{'entity_id':'light.fixture','state':'on','attributes':{'brightness':128,'friendly_name':'Fixture Licht'},'last_updated':'2026-01-01T00:00:00Z','last_changed':'2026-01-01T00:00:00Z'},{'entity_id':'sensor.fixture','state':'unavailable','attributes':{'unit_of_measurement':'W'}},{'entity_id':'sensor.loose','state':'unknown','attributes':{}},{'entity_id':'weather.state_only','state':'sunny','attributes':{}}]}
class RoomPeer:
 def __init__(self):
  self.data=copy.deepcopy(DATA);self.commands=[];self.identity={'id':'alice','is_admin':False,'is_owner':False};self.admins=['admin'];self.fail=None;self.drop_write=False;self.ignore_write=False
  peer=self
  class Handler(socketserver.StreamRequestHandler):
   def handle(self):
    self.request.settimeout(3)
    try:
     self.rfile.readline();headers={}
     while True:
      l=self.rfile.readline()
      if l==b'\r\n':break
      if not l:return
      k,v=l.decode().split(':',1);headers[k.lower()]=v.strip()
     key=base64.b64encode(hashlib.sha1((headers['sec-websocket-key']+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest())
     self.wfile.write(b'HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: '+key+b'\r\n\r\n')
     def send(v):
      b=json.dumps(v).encode();n=len(b);prefix=bytes([129,n]) if n<126 else bytes([129,126])+struct.pack('!H',n) if n<65536 else bytes([129,127])+struct.pack('!Q',n);self.wfile.write(prefix+b)
     def receive():
      h=self.rfile.read(2)
      if len(h)!=2:return None
      n=h[1]&127
      if n==126:n=struct.unpack('!H',self.rfile.read(2))[0]
      elif n==127:n=struct.unpack('!Q',self.rfile.read(8))[0]
      assert n<2000000 and h[1]&128
      mask=self.rfile.read(4);b=self.rfile.read(n);return json.loads(bytes(x^mask[i%4] for i,x in enumerate(b)))
     send({'type':'auth_required'});assert receive()=={'type':'auth','access_token':'synthetic-test-token'};send({'type':'auth_ok'})
     while True:
      cmd=receive()
      if cmd is None:return
      peer.commands.append(copy.deepcopy(cmd));kind=cmd['type'];result=None;ok=True
      if kind==peer.fail:ok=False
      elif kind=='auth/current_user':result=peer.identity
      elif kind=='config/auth/list':result=[{'id':x,'is_active':True,'is_owner':False,'group_ids':['system-admin']} for x in peer.admins]
      elif kind=='get_states':result=peer.data['states']
      elif kind=='get_config':result={'version':'2026.11.0'}
      elif kind in ('config/area_registry/list','config/floor_registry/list','config/device_registry/list','config/entity_registry/list'):result=peer.data[{'area':'areas','floor':'floors','device':'devices','entity':'entities'}[kind.split('/')[1].split('_')[0]]]
      elif kind in ('config/device_registry/update','config/entity_registry/update'):
       entity='entity_registry' in kind;key='entity_id' if entity else 'id';rows=peer.data['entities' if entity else 'devices'];target=cmd['entity_id' if entity else 'device_id'];row=next(x for x in rows if x[key]==target)
       assert set(cmd)=={'id','type','area_id','entity_id' if entity else 'device_id'}
       if not peer.ignore_write:row['area_id']=cmd['area_id']
       if peer.drop_write:return
       result={'entity_entry':row} if entity else row
      else:raise AssertionError('Forbidden command '+kind)
      send({'id':cmd['id'],'type':'result','success':ok,'result':result,'error':None if ok else {'code':'unauthorized'}})
    except (BrokenPipeError,ConnectionResetError):pass
  class Server(socketserver.ThreadingTCPServer):allow_reuse_address=True;daemon_threads=True
  self.server=Server(('127.0.0.1',0),Handler);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
 def close(self):self.server.shutdown();self.server.server_close();self.thread.join()
