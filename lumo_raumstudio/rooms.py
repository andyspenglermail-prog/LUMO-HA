"""Fixed runtime inventory reads. No snapshots, actions or arbitrary proxy.
Registry IDs identify references; labels and entity_ids are observations, not identity.
"""
import copy
from client import ReadError
from store import StudioError,now
from dashboard_reads import DashboardReads
READS=(('areas','config/area_registry/list'),('floors','config/floor_registry/list'),('devices','config/device_registry/list'),('entities','config/entity_registry/list'),('states','get_states'))

def index(rows,key):
    if type(rows) is not list or len(rows)>50000:raise ReadError('inventory_limit')
    result={}
    for row in rows:
        if type(row) is not dict or type(row.get(key)) is not str or not row[key] or row[key] in result:raise ReadError('invalid_inventory')
        result[row[key]]=row
    return result

def normalize(data):
    areas=index(data['areas'],'area_id');floors=index(data['floors'],'floor_id');devices=index(data['devices'],'id');registry=index(data['entities'],'id');states=index(data['states'],'entity_id')
    # A duplicate current entity_id makes binding ambiguous, never guess.
    index(data['entities'],'entity_id')
    result={'areas':[],'floors':[],'devices':[],'entities':[]}
    for f in floors.values():result['floors'].append({k:f.get(k) for k in ('floor_id','name','icon','level')})
    seen=set()
    for r in list(registry.values())+[{'entity_id':s} for s in states if s not in {e['entity_id'] for e in registry.values()}]:
        eid=r['entity_id'];rid=r.get('id');dev=devices.get(r.get('device_id'),{});state=states.get(eid);attrs=copy.deepcopy(state.get('attributes',{})) if state else {}
        if type(attrs) is not dict:raise ReadError('invalid_inventory')
        area=r.get('area_id') if r.get('area_id') is not None else dev.get('area_id')
        provenance='entity' if r.get('area_id') is not None else 'device' if dev.get('area_id') is not None else 'none'
        availability='disabled' if r.get('disabled_by') is not None or dev.get('disabled_by') is not None else 'missing_state' if state is None else state.get('state') if state.get('state') in ('unknown','unavailable') else 'available'
        result['entities'].append({'key':'registry:'+rid if rid else 'state:'+eid,'registryId':rid,'entityId':eid,'deviceId':r.get('device_id'),'name':r.get('name') or attrs.get('friendly_name') or r.get('original_name') or eid,'domain':eid.split('.')[0], 'areaId':r.get('area_id'),'effectiveAreaId':area,'areaSource':provenance,'floorId':areas.get(area,{}).get('floor_id'),'disabledBy':r.get('disabled_by'),'hiddenBy':r.get('hidden_by'),'entityCategory':r.get('entity_category'),'icon':r.get('icon') or attrs.get('icon'),'availability':availability,'state':state.get('state') if state else None,'attributes':attrs,'unit':attrs.get('unit_of_measurement'),'lastUpdated':state.get('last_updated') if state else None,'lastChanged':state.get('last_changed') if state else None,'platform':r.get('platform')})
        seen.add(eid)
    for d in devices.values():
        e=[x for x in result['entities'] if x['deviceId']==d['id']]
        result['devices'].append({'id':d['id'],'name':d.get('name_by_user') or d.get('name') or d['id'],'areaId':d.get('area_id'),'floorId':areas.get(d.get('area_id'),{}).get('floor_id'),'entityKeys':[x['key'] for x in e],'entityCount':len(e),'manufacturer':d.get('manufacturer'),'model':d.get('model'),'disabledBy':d.get('disabled_by'),'viaDeviceId':d.get('via_device_id'),'parentDeviceId':d.get('parent_device_id'),'availability':'disabled' if d.get('disabled_by') else 'no_entities' if not e else 'available' if any(x['availability']=='available' for x in e) else 'no_available_entities'})
    for a in areas.values():
        result['areas'].append({**{k:a.get(k) for k in ('area_id','name','icon','floor_id')},'deviceCount':sum(d['areaId']==a['area_id'] for d in result['devices']),'entityCount':sum(e['effectiveAreaId']==a['area_id'] for e in result['entities'])})
    return result

class RoomReads:
    def __init__(self,client):self.client=client
    def authorize(self,user,*,write=False):
        if self.client is None:raise StudioError('Home Assistant ist noch nicht verbunden.',503)
        identity=self.client._ws_reads(({'type':'auth/current_user'},),dict,'identity_unavailable',1048576)[0]
        if identity.get('id')==user:
            admin=identity.get('is_admin') is True
            if write and not admin:raise StudioError('HA-Korrekturen benötigen Administratorrechte des anfragenden Benutzers.',403)
            return admin
        # Supervisor credentials do not establish the ingress user's permissions.
        try:DashboardReads(self.client).admin(user)
        except ReadError:raise StudioError('Die Leserechte des anfragenden HA-Benutzers können nicht bestätigt werden. Bei abweichender Verbindungsidentität ist ein verifizierter Administrator erforderlich.',403) from None
        return True
    def raw(self):
        rows=self.client._ws_reads(tuple({'type':command} for _,command in READS),list,'inventory_unavailable')
        return {key:value for (key,_),value in zip(READS,rows)}
    def inventory(self,user):
        admin=self.authorize(user);data=self.raw();result=normalize(data)
        config=self.client._ws_reads(({'type':'get_config'},),dict,'config_unavailable')[0]
        result.update(fetchedAt=now(),status='fresh',version=config.get('version'),canCorrect=admin,permission='requester-admin' if admin else 'same-user-upstream-read')
        return result
