"""Single-use, requester-bound area-only corrections. No retry on any dispatch.
HA has no conditional registry update: fresh compare narrows, cannot eliminate,
the external read/update race. See DOCS.md. Preview lifetime is 90 seconds.
"""
import copy,secrets,time,hashlib,json
from store import StudioError
from rooms import index
from client import ReadError

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
class AreaCorrections:
    def __init__(self,reads,store):self.reads=reads;self.store=store;self.pending={}
    def target(self,data,kind,target,area):
        areas=index(data['areas'],'area_id');devices=index(data['devices'],'id');entities=index(data['entities'],'id')
        row=(devices if kind=='device' else entities).get(target)
        if row is None:raise StudioError('Das ausgewählte HA-Objekt ist nicht mehr vorhanden.',404)
        if area is not None and area not in areas:raise StudioError('Der Zielbereich ist nicht vorhanden.',404)
        affected=[e for e in entities.values() if e.get('device_id')==target] if kind=='device' else [row]
        device=devices.get(row.get('device_id')) if kind=='entity' else row
        return row,affected,digest({'object':row,'affected':affected,'device':device,'areas':data['areas'],'floors':data['floors']})
    def preview(self,user,id,value,guard):
        if set(value)!={'revision','kind','targetId','areaId'} or value['kind'] not in ('device','entity') or type(value['targetId']) is not str or value['areaId'] is not None and type(value['areaId']) is not str:raise StudioError('Nur eine konkrete Geräte- oder Entitätsbereichskorrektur ist erlaubt.')
        d=self.store.get(user,id)
        if type(value['revision']) is not int or d['revision']!=value['revision']:raise StudioError('Der Dashboardstand wurde geändert. Bitte neu öffnen.',409)
        self.reads.authorize(user,write=True);data=self.reads.raw();row,affected,stamp=self.target(data,value['kind'],value['targetId'],value['areaId']);guard()
        self.pending={k:v for k,v in self.pending.items() if v['expires']>time.monotonic()}
        if len(self.pending)>=1024 or sum(v['user']==user for v in self.pending.values())>=16:raise StudioError('Zu viele offene Vorschauen. Bitte kurz warten.',429)
        key=secrets.token_hex(32);self.pending[key]={'user':user,'dashboard':id,'revision':d['revision'],'value':copy.deepcopy(value),'stamp':stamp,'expires':time.monotonic()+90}
        return {'previewId':key,'expiresIn':90,'kind':value['kind'],'targetId':value['targetId'],'entityId':row.get('entity_id'),'name':row.get('name_by_user') or row.get('name') or row.get('entity_id') or row['id'],'beforeAreaId':row.get('area_id'),'afterAreaId':value['areaId'],'affectedEntityIds':[e['entity_id'] for e in affected if value['kind']=='entity' or e.get('area_id') is None],'permission':'Administrator des anfragenden Benutzers geprüft','impact':'Ändert ausschließlich die HA-Bereichszuordnung. Individuelle Entitätsbereiche bleiben bei Gerätekorrekturen erhalten. Keine Geräteaktion, kein Verschieben lokaler LUMO-Referenzen. Ohne individuellen Bereich erbt eine Entität gegebenenfalls den Gerätebereich.'}
    def confirm(self,user,id,value,guard):
        if set(value)!={'previewId','confirm'} or type(value['previewId']) is not str or value['confirm'] is not True:raise StudioError('Die konkrete Vorschau muss ausdrücklich bestätigt werden.')
        p=self.pending.get(value['previewId'])
        if p is None or p['user']!=user or p['dashboard']!=id or p['expires']<=time.monotonic():raise StudioError('Diese Vorschau ist abgelaufen oder bereits verbraucht. Nicht ungeprüft wiederholen.',409)
        # Consume before any possibly dispatched operation. Restart also invalidates previews.
        del self.pending[value['previewId']]
        d=self.store.get(user,id)
        if d['revision']!=p['revision']:raise StudioError('Der Dashboardstand hat sich geändert. Keine HA-Korrektur ausgeführt.',409)
        self.reads.authorize(user,write=True);v=p['value'];data=self.reads.raw();row,affected,stamp=self.target(data,v['kind'],v['targetId'],v['areaId'])
        if stamp!=p['stamp']:raise StudioError('Das HA-Objekt oder sein Bereich wurde seit der Vorschau geändert. Keine Korrektur ausgeführt.',409)
        if p['expires']<=time.monotonic():raise StudioError('Die Vorschau ist während der Prüfung abgelaufen. Keine HA-Korrektur ausgeführt.',409)
        guard()
        command={'type':'config/'+v['kind']+'_registry/update','entity_id' if v['kind']=='entity' else 'device_id':row['entity_id'] if v['kind']=='entity' else row['id'],'area_id':v['areaId']}
        try:
            self.reads.client._ws_reads((command,),dict,'area_write_uncertain')
            actual,_,_=self.target(self.reads.raw(),v['kind'],v['targetId'],v['areaId'])
            if actual.get('area_id')!=v['areaId'] or v['kind']=='entity' and actual.get('entity_id')!=row['entity_id']:raise ReadError('readback_mismatch')
            guard()
        except (ReadError,StudioError):raise StudioError('Ergebnis der HA-Korrektur unklar. Nicht erneut senden. Den tatsächlichen Stand in Home Assistant prüfen; es erfolgt keine automatische Wiederholung.',502) from None
        return {'status':'confirmed','kind':v['kind'],'targetId':v['targetId'],'actualAreaId':actual.get('area_id'),'message':'Bereichszuordnung aus HA frisch zurückgelesen und bestätigt.'}
