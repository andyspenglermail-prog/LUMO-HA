"""Optional Step2 overlay in the existing schema-2 document.
Never mutate native, nativeImport or Step1 view metadata. Array order is view order.
"""
import copy,json,re
from store import StudioError,text,icon_value,ICONS,now
from client import ENTITY
ID=re.compile('[a-f0-9]{32}')
TOKEN=re.compile(r'[A-Za-z0-9_:-]{1,256}')
FIELDS={'id','title','icon','visible','areaId','source','nativeViewId','deviceIds','entityRefs'}

def get_plan(document):
    if 'roomPlan' in document:return copy.deepcopy(document['roomPlan'])
    views=[]
    for v in document['views']:
        # Only presentation metadata; custom native code remains inert and intact.
        views.append({'id':v['id'],'title':v['title'][:80] or 'Ansicht','icon':v['icon'] if v['icon'] in ICONS else '', 'visible':True,'areaId':None,'source':'native','nativeViewId':v['id'],'deviceIds':[],'entityRefs':[]})
    return {'schemaVersion':1,'views':views}

def validate(plan,document):
    def bad():raise StudioError('Ungültige Raumansicht oder Referenz.')
    if type(plan) is not dict or set(plan)!={'schemaVersion','views'} or type(plan['schemaVersion']) is not int or plan['schemaVersion']!=1 or type(plan['views']) is not list or len(plan['views'])>256:bad()
    ids=set();native={v['id'] for v in document['views']}
    for v in plan['views']:
        if type(v) is not dict or set(v)!=FIELDS or type(v['id']) is not str or not ID.fullmatch(v['id']) or v['id'] in ids:bad()
        ids.add(v['id']);text(v['title'],'Ansichtstitel',80);icon_value(v['icon'])
        if type(v['visible']) is not bool or v['source'] not in ('virtual','ha-area','native'):bad()
        if v['areaId'] is not None and (type(v['areaId']) is not str or not TOKEN.fullmatch(v['areaId'])):bad()
        if v['source']=='ha-area' and v['areaId'] is None or v['source']=='virtual' and v['areaId'] is not None:bad()
        if v['source']=='native':
            if v['nativeViewId'] not in native:bad()
        elif v['nativeViewId'] is not None:bad()
        ds=v['deviceIds'];es=v['entityRefs']
        if type(ds) is not list or len(ds)>10000 or any(type(x) is not str or not TOKEN.fullmatch(x) for x in ds) or len(set(ds))!=len(ds):bad()
        if type(es) is not list or len(es)>30000:bad()
        seen=set()
        for e in es:
            if type(e) is not dict or set(e)!={'key','entityId'} or type(e['key']) is not str or type(e['entityId']) is not str or not ENTITY.fullmatch(e['entityId']):bad()
            if e['key'].startswith('registry:'):
                if not TOKEN.fullmatch(e['key'][9:]):bad()
            elif e['key']!='state:'+e['entityId']:bad()
            if e['key'] in seen:bad()
            seen.add(e['key'])
    return plan

def save_plan(store,owner,id,revision,plan,confirmed,inventory):
    plan=copy.deepcopy(plan)
    with store.connect() as c:
        c.execute('BEGIN IMMEDIATE');d=store.checked(c,owner,id,revision);validate(plan,d);old=get_plan(d)
        if type(confirmed) is not list or any(type(x) is not str for x in confirmed):raise StudioError('Löschbestätigung fehlt.')
        deleted={v['id'] for v in old['views']}-{v['id'] for v in plan['views']}
        if deleted-set(confirmed):raise StudioError('Das Entfernen jeder lokalen Ansicht muss bestätigt werden.')
        oldrefs={e['key']:e for v in old['views'] for e in v['entityRefs']};olddevices={x for v in old['views'] for x in v['deviceIds']};oldareas={v['areaId'] for v in old['views']}
        entities={e['key']:e for e in inventory.get('entities',[])};devices={x['id'] for x in inventory.get('devices',[])};areas={x['area_id'] for x in inventory.get('areas',[])}
        for v in plan['views']:
            v['title']=text(v['title'],'Ansichtstitel',80)
            if v['areaId'] is not None and v['areaId'] not in areas|oldareas:raise StudioError('Der HA-Bereich ist nicht im gelesenen Bestand.')
            if set(v['deviceIds'])-(devices|olddevices):raise StudioError('Ein Gerät ist nicht im gelesenen Bestand.')
            for e in v['entityRefs']:
                if e['key'] in entities:e['entityId']=entities[e['key']]['entityId']
                elif e['key'] in oldrefs:e['entityId']=oldrefs[e['key']]['entityId']
                else:raise StudioError('Eine Entität ist nicht im gelesenen Bestand.')
        d['roomPlan']=plan;d['revision']+=1;d['updatedAt']=now()
        c.execute('UPDATE dashboards SET revision=?,document=? WHERE id=? AND owner=? AND revision=?',(d['revision'],json.dumps(d),id,owner,revision))
    return store.get(owner,id)
