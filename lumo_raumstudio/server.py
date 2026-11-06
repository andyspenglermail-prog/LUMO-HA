"""Ingress-only app. Fixed HA reads, local owner writes, narrow confirmed area correction."""
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from threading import Timer
import base64,hashlib,hmac,json,re,secrets,socket,sqlite3
from client import ReadError,parse_json
from policy import SAFE_ID
from store import StudioError
from dashboard_reads import DashboardReads,bounded
ROOT=Path(__file__).parent

def version():return json.loads((ROOT/'config.json').read_text())['version']
SETUP='Raumstudio ist noch nicht freigegeben. In der App-Konfiguration enabled aktivieren und Deine HA-Benutzer-ID unter allowed_user_ids eintragen. Anschließend die App neu starten. Keine Zugangsdaten im Browser nötig.'

def create_server(*,store,options_snapshot,client,bind=('127.0.0.1',0),trusted_proxy_ip='172.30.32.2'):
    from rooms import RoomReads
    reads=DashboardReads(client);room_reads=RoomReads(client);key=secrets.token_bytes(32)
    from area_corrections import AreaCorrections
    corrections=AreaCorrections(room_reads,store)
    def csrf(user):return hmac.new(key,user.encode(),hashlib.sha256).hexdigest()
    class HeaderReader:
        def __init__(self,stream):self.stream=stream;self.remaining=32768
        def readline(self,limit=-1):
            line=self.stream.readline(min(limit,self.remaining+1) if limit>=0 else self.remaining+1);self.remaining-=len(line)
            if self.remaining<0:raise OSError('header_limit')
            return line
        def read(self,n):return self.stream.read(n)
        def close(self):self.stream.close()
    class Handler(BaseHTTPRequestHandler):
        timeout=5
        def setup(self):super().setup();self.rfile=HeaderReader(self.rfile)
        def log_message(self,*args):pass
        def version_string(self):return 'LUMO Raumstudio'
        def handle_one_request(self):
            def expire():
                try:self.connection.shutdown(socket.SHUT_RDWR)
                except OSError:pass
            self.timer=Timer(3,expire);self.timer.daemon=True;self.timer.start()
            try:super().handle_one_request()
            finally:self.timer.cancel();self.timer.join()
        def reply(self,status,body,kind='application/json',attachment=None):
            self.close_connection=True;self.send_response(status)
            headers={'Content-Type':kind,'Content-Length':str(len(body)),'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','X-Frame-Options':'SAMEORIGIN','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'self'",'Connection':'close'}
            if attachment:headers['Content-Disposition']='attachment; filename="'+attachment+'"'
            for k,v in headers.items():self.send_header(k,v)
            self.end_headers()
            if self.command!='HEAD':self.wfile.write(body)
        def api(self,status,value):self.reply(status,json.dumps(value,ensure_ascii=True,allow_nan=False,separators=(',',':')).encode())
        def send_error(self,code,message=None,explain=None):self.api(405 if code==501 else code,{'error':'Diese Anfrage wird nicht unterstützt.'})
        def work(self):
            self.timer.cancel();self.timer.join()
            try:self.route()
            except StudioError as e:self.api(e.status,{'error':e.message,'details':e.details})
            except ReadError as e:self.api(e.status,{'error':'Home Assistant konnte nicht sicher gelesen werden. Verbindung und Administratorrechte prüfen. Es wurde nichts in HA geändert.'})
            except (ValueError,TypeError,KeyError,RecursionError,UnicodeError):self.api(400,{'error':'Die Anfrage ist ungültig oder zu groß. Bitte Eingaben prüfen.'})
            except (OSError,sqlite3.Error):self.api(503,{'error':'Speicherung oder Verbindung nicht bestätigt. Deine Eingaben behalten und den gespeicherten Stand neu laden; nicht ungeprüft erneut ausführen.'})
        def route(self):
            target=self.path;hosts=self.headers.get_all('Host',[])
            if len(hosts)!=1 or not re.fullmatch(r'[A-Za-z0-9.\[\]:_-]{1,300}',hosts[0]) or self.headers.get_all('Expect') or len(target)>512:raise StudioError('Ungültige Anfrage.')
            lengths=self.headers.get_all('Content-Length',[])
            if self.headers.get_all('Transfer-Encoding') or len(lengths)>1:raise StudioError('Ungültige Anfrage.')
            writing=self.command=='POST'
            limit=12*1024*1024 if target=='/api/images' else 1052672
            if writing:
                if len(lengths)!=1 or not re.fullmatch('[1-9][0-9]{0,7}',lengths[0]) or int(lengths[0])>limit:raise StudioError('Die Datei oder Anfrage ist zu groß.',413)
                if self.headers.get_all('Content-Type',[])!=['application/json']:raise StudioError('Ungültiges Datenformat.')
            elif lengths and lengths!=['0']:raise StudioError('Ungültige Anfrage.')
            if target=='/health' and self.command=='GET':self.reply(200,b'ok\n','text/plain');return
            users=self.headers.get_all('X-Remote-User-Id',[])
            if self.client_address[0]!=trusted_proxy_ip or len(users)!=1 or not SAFE_ID.fullmatch(users[0]):raise StudioError('Bitte Raumstudio über Home Assistant öffnen. Die Ingress-Identität fehlt.',403)
            user=users[0]
            static={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/room.js':'room.js','/room.css':'room.css','/style.css':'style.css','/lumo-logo.png':'lumo-logo.png','/mdi.json':'mdi.json'}
            if target in static and self.command in ('GET','HEAD'):
                ext=Path(static[target]).suffix;kind={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.png':'image/png','.json':'application/json'}[ext]
                self.reply(200,(ROOT/static[target]).read_bytes(),kind);return
            if self.command not in ('GET','POST'):raise StudioError('Diese Schnittstelle ist nicht verfügbar.',405)
            image_match=re.fullmatch(r'/api/images/([a-f0-9]{32})',target)
            if not image_match and self.headers.get_all('X-LUMO-Read',[])!=['1']:raise StudioError('Diese Anfrage ist nicht freigegeben.',403)
            fetch=self.headers.get_all('Sec-Fetch-Site',[]);origins=self.headers.get_all('Origin',[])
            if len(fetch)>1 or fetch and fetch[0] not in ('same-origin','none'):raise StudioError('Fremde Webseiten dürfen Raumstudio nicht verwenden.',403)
            if origins:
                o=urlsplit(origins[0])
                if len(origins)!=1 or o.scheme not in ('http','https') or o.netloc!=hosts[0] or o.path or o.query or o.fragment or o.username:raise StudioError('Die Herkunft der Anfrage stimmt nicht überein.',403)
            policy=options_snapshot.current()
            ready=policy is not None and user in policy.users
            if target=='/api/session' and self.command=='GET':
                if policy is not None and user not in policy.users:raise StudioError('Deine HA-Benutzer-ID ist für Raumstudio nicht freigegeben.',403)
                self.api(200,{'version':version(),'userId':user,'ready':ready,'message':'' if ready else SETUP,'csrf':csrf(user) if ready else None,'haStatus':'Noch nicht geprüft'});return
            if not ready:raise StudioError(SETUP if policy is None else 'Deine HA-Benutzer-ID ist nicht freigegeben.',403)
            def guard():
                if options_snapshot.current() is not policy:raise StudioError('Die App-Konfiguration wurde geändert. Bitte die App neu starten.',403)
            value=None
            if writing:
                tokens=self.headers.get_all('X-LUMO-CSRF',[])
                if not origins or fetch and fetch!=['same-origin'] or self.headers.get_all('X-LUMO-Action',[])!=['1'] or len(tokens)!=1 or not hmac.compare_digest(tokens[0],csrf(user)):raise StudioError('Die Sitzung ist abgelaufen oder nicht freigegeben. Bitte neu laden; ungespeicherte Eingaben vorher behalten.',403)
                def expire():
                    try:self.connection.shutdown(socket.SHUT_RDWR)
                    except OSError:pass
                timer=Timer(5,expire);timer.daemon=True;timer.start()
                try:
                    raw=self.rfile.read(int(lengths[0]))
                    if len(raw)!=int(lengths[0]):raise StudioError('Die Anfrage wurde unterbrochen.')
                    value=parse_json(raw.decode())
                finally:timer.cancel();timer.join()
                if type(value) is not dict:raise StudioError('Ein Datenobjekt wird erwartet.')
                if target!='/api/images':bounded(value)
            guard()
            if target=='/api/ha/inventory' and not writing:
                result=room_reads.inventory(user);guard();self.api(200,result);return
            if target=='/api/dashboards':
                if not writing:self.api(200,store.list(user));return
                if set(value)!={'name','icon'}:raise StudioError('Name und optionales Icon werden benötigt.')
                self.api(201,store.create(user,value['name'],value['icon']));return
            correction_match=re.fullmatch(r'/api/dashboards/([a-f0-9]{32})/area-correction/(preview|confirm)',target)
            if correction_match and writing:
                result=getattr(corrections,correction_match[2])(user,correction_match[1],value,guard);self.api(200,result);return
            room_match=re.fullmatch(r'/api/dashboards/([a-f0-9]{32})/rooms',target)
            if room_match:
                from room_store import get_plan,save_plan
                id=room_match[1];d=store.get(user,id)
                if not writing:self.api(200,{'dashboardId':id,'revision':d['revision'],'plan':get_plan(d)});return
                if set(value)!={'revision','plan','confirmedDeletes'}:raise StudioError('Ungültige Raumansichten.')
                # Local metadata remains saveable on disconnect; new references need evidence.
                try:inventory=room_reads.inventory(user)
                except (ReadError,StudioError):inventory={}
                guard();self.api(200,save_plan(store,user,id,value['revision'],value['plan'],value['confirmedDeletes'],inventory));return
            match=re.fullmatch(r'/api/dashboards/([a-f0-9]{32})(?:/(save|duplicate|delete|native-edit|report|export))?',target)
            if match:
                id,action=match.groups()
                if not writing and not action:self.api(200,store.get(user,id));return
                if not writing and action in ('report','export'):
                    d=store.get(user,id)
                    if 'nativeImport' not in d:raise StudioError('Dieser Entwurf ist keine verlustfreie HA-Kopie.',422)
                    if action=='report':
                        from imported import report
                        self.api(200,report(d));return
                    from native import compile_native
                    raw=json.dumps(compile_native(store,user,d),ensure_ascii=True,allow_nan=False,indent=2).encode()+b'\n'
                    self.reply(200,raw,attachment='lumo-'+id+'-r'+str(d['revision'])+'.json');return
                if writing and action=='native-edit' and set(value)=={'revision','edits'}:result=store.edit_native(user,id,value['revision'],value['edits'])
                elif writing and action=='save' and set(value)=={'revision','patch'}:result=store.update(user,id,value['revision'],value['patch'])
                elif writing and action=='duplicate' and set(value)=={'revision'}:result=store.duplicate(user,id,value['revision'])
                elif writing and action=='delete' and set(value)=={'revision','confirm'}:result=store.delete(user,id,value['revision'],value['confirm'])
                else:raise StudioError('Ungültige Entwurfsaktion.')
                self.api(200,result);return
            if target=='/api/images':
                if not writing:self.api(200,store.images(user));return
                if set(value)!={'name','data'} or type(value['data']) is not str:raise StudioError('Ungültiger Bildupload.')
                try:data=base64.b64decode(value['data'],validate=True)
                except ValueError:raise StudioError('Ungültige Bilddaten.') from None
                self.api(201,store.put_image(user,value['name'],data));return
            if image_match and not writing:
                meta,data=store.image(user,image_match[1]);self.reply(200,data,meta['mime']);return
            if target=='/api/ha/dashboards' and not writing:
                result=reads.catalog(user);guard();self.api(200,{'dashboards':result,'status':'Lesend verbunden · Administrator geprüft'});return
            if target=='/api/ha/import' and writing:
                if set(value)!={'path','name'}:raise StudioError('Ungültige Importauswahl.')
                result=reads.read(user,value['path']);guard();self.api(201,store.import_native(user,value['name'],result['config'],source_path=result['path'],resources=result['resources']));return
            raise StudioError('Diese Schnittstelle ist nicht verfügbar.',404)
        do_GET=work;do_HEAD=work;do_POST=work;do_PUT=work;do_DELETE=work;do_PATCH=work;do_OPTIONS=work
    class QuietServer(HTTPServer):
        request_queue_size=8
        def verify_request(self,request,address):return address[0] in (trusted_proxy_ip,'127.0.0.1')
        def handle_error(self,*args):pass
    return QuietServer(bind,Handler)

def main(*,options_snapshot,client):
    import os
    from store import Store
    if os.getresuid()!=(65532,)*3 or os.getresgid()!=(65532,)*3 or os.getgroups():raise RuntimeError('safe_bootstrap_required')
    with create_server(store=Store('/data/raumstudio/studio.sqlite'),options_snapshot=options_snapshot,client=client,bind=('0.0.0.0',8099)) as s:s.serve_forever()
