"""Allowlisted metadata only; source lists/counts are never silently truncated."""
from client import ENTITY,ReadError
from datetime import datetime,timezone
import re
import math
import time
from capabilities import attributes as clean_attributes

def selected_ids(value,policy):
    if type(value) is not str:raise ReadError('invalid_selection',400)
    ids=value.split(',')
    if not 1<=len(ids)<=32 or len(set(ids))!=len(ids):raise ReadError('invalid_selection',400)
    for id in ids:
        entity_id(id)
        if not policy.permits(id):raise ReadError('forbidden',403)
    return ids

def timestamp(value):
    if type(value) is not str or len(value)>40 or not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?(?:Z|[+-]\d\d:\d\d)',value):raise ReadError('invalid_timestamp',400)
    try:
        date=datetime.fromisoformat(value.replace('Z','+00:00'))
        if date.utcoffset() is None:raise ValueError()
        return date
    except ValueError:raise ReadError('invalid_timestamp',400) from None

def scalar_state(value):
    if type(value) is not str or len(value)>256:raise ReadError('invalid_state')
    if value in ('unknown','unavailable'):return None,value
    if value.strip().lower() in ('nan','inf','+inf','-inf','infinity','+infinity','-infinity'):return None,'invalid'
    if re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?',value):
        number=float(value)
        return (number,'good') if math.isfinite(number) and abs(number)<=1e12 else (None,'invalid')
    return value,'good'

def clean_state(id,raw):
    if raw is None:return {'entityId':id,'value':None,'quality':'missing','unit':'','lastUpdated':None,'lastChanged':None}
    if type(raw) is not dict or raw.get('entity_id')!=id:raise ReadError('invalid_state')
    value,quality=scalar_state(raw.get('state'))
    if id.split('.')[0] in ('select','input_select') and quality=='good':value=raw['state']
    attributes=raw.get('attributes')
    if type(attributes) is not dict:raise ReadError('invalid_state')
    unit=attributes.get('unit_of_measurement') or ''
    if type(unit) is not str or len(unit)>32:raise ReadError('invalid_state')
    updated=raw.get('last_updated');changed=raw.get('last_changed')
    timestamp(updated);timestamp(changed)
    return {'entityId':id,'value':value,'quality':quality,'unit':unit,'lastUpdated':updated,'lastChanged':changed,
        'stateClass':attributes.get('state_class') if attributes.get('state_class') in ('measurement','total','total_increasing') else None,
        'attributes':clean_attributes(attributes)}

def add_capabilities(client,result,guard,deadline):
    from control import DOMAINS,service_domains,capability
    available={}
    if any(s['entityId'].split('.')[0] in DOMAINS and s['quality']=='good' for s in result):
        guard()
        try:available=service_domains(client.services(deadline=deadline))
        except ReadError:pass  # Keep actual state readable; fail closed on controls.
        guard()
    for item in result:item['control']=capability(item,available)

def states(client,ids,guard):
    deadline=time.monotonic()+15;result=[]
    for id in ids:
        guard();result.append(clean_state(id,client.state(id,deadline=deadline)));guard()
    add_capabilities(client,result,guard,deadline)
    return {'states':result,'count':len(result),'fetchedAt':now()}

def history_window(start,end):
    left,right=timestamp(start),timestamp(end)
    if not 0<(right-left).total_seconds()<=7*86400 or right>datetime.now(timezone.utc):raise ReadError('invalid_window',400)
    return left,right

def history(client,ids,start,end,guard):
    left,right=history_window(start,end)
    deadline=time.monotonic()+15
    current=[]
    for id in ids:
        guard();current.append({**clean_state(id,client.state(id,deadline=deadline)),'fetchedAt':now()});guard()
    add_capabilities(client,current,guard,deadline)
    raw=client.history(ids,start,end,deadline=deadline);guard()
    if type(raw) is not list or len(raw)>len(ids):raise ReadError('invalid_history')
    collected={id:[] for id in ids};total=0;excluded=0;seen=set()
    for group in raw:
        if type(group) is not list or len(group)>2048:raise ReadError('history_limit')
        if not group:continue
        id=group[0].get('entity_id') if type(group[0]) is dict else None
        if id not in collected or id in seen:raise ReadError('invalid_history')
        seen.add(id)
        previous=None
        for point in group:
            total+=1
            if total>8192:raise ReadError('history_limit')
            if type(point) is not dict or point.get('entity_id')!=id:raise ReadError('invalid_history')
            t=timestamp(point.get('last_updated'))
            timestamp(point.get('last_changed'))
            if previous is not None and t<previous:raise ReadError('invalid_history')
            previous=t
            value,quality=scalar_state(point.get('state'))
            if not left<=t<right:excluded+=1;continue
            attributes=point.get('attributes')
            # Full attributes without a unit explicitly describe dimensionless
            # data. Missing attributes are not evidence for any unit.
            unit=attributes.get('unit_of_measurement') if type(attributes) is dict else None
            if type(attributes) is dict and unit is None:unit=''
            if unit is not None and (type(unit) is not str or len(unit)>32):raise ReadError('invalid_history')
            if unit is None and quality=='good':quality='unknown-unit'
            collected[id].append({'t':int(t.timestamp()*1000),'value':value,'quality':quality,'unit':unit,
                'lastUpdated':point['last_updated'],'lastChanged':point['last_changed']})
    fetched=now();series=[]
    for s in current:
        samples=collected[s['entityId']]
        units={p['unit'] for p in samples if type(p['value']) in (int,float)}
        unit=next(iter(units)) if len(units)==1 else None
        unit_quality='unknown-unit' if not units or None in units else 'mixed-unit' if len(units)>1 else 'good'
        series.append({'entityId':s['entityId'],'unit':unit,'unitQuality':unit_quality,'samples':samples,
            'observedWindow':[int(left.timestamp()*1000),int(right.timestamp()*1000)],'historyQuality':'good','fetchedAt':fetched})
    return {'series':series,'states':current,'count':len(series),'rowsReceived':total,'rowsOutsideWindow':excluded,'rowsReturned':total-excluded,'fetchedAt':fetched}

def now():return datetime.now(timezone.utc).isoformat()
def text(v,limit,default=None):
    if v is None and default is not None:return default
    if type(v) is not str or not 1<=len(v)<=limit or not v.strip() or any(ord(c)<32 or ord(c)==127 for c in v):raise ReadError('invalid_metadata')
    return v

def registry_id(v):
    v=text(v,128)
    if any(c.isspace() for c in v):raise ReadError('invalid_metadata')
    return v

def ref(v):return None if v is None else registry_id(v)
def entity_id(v):
    if type(v) is not str or len(v)>256 or not ENTITY.fullmatch(v):raise ReadError('invalid_entity',400)
    return v

def discovery(client,policy):
    areas,devices,entities=client.registries()
    for rows,limit in ((areas,256),(devices,20000),(entities,20000)):
        if len(rows)>limit:raise ReadError('registry_limit')
        if any(type(row) is not dict for row in rows):raise ReadError('invalid_metadata')
    rooms=[{'id':registry_id(a.get('area_id')),'name':text(a.get('name'),160)} for a in areas]
    clean_devices=[{'id':registry_id(d.get('id')),'name':text(d.get('name_by_user') or d.get('name') or d.get('id'),160),'areaId':ref(d.get('area_id'))} for d in devices]
    clean=[]
    seen=set()
    for e in entities:
        id=entity_id(e.get('entity_id'))
        if id in seen:raise ReadError('ambiguous_registry')
        seen.add(id)
        if not policy.permits(id):continue
        category=e.get('entity_category');disabled=e.get('disabled_by')
        if category not in (None,'config','diagnostic'):raise ReadError('invalid_metadata')
        if disabled is not None:text(disabled,64)
        device_class=e.get('device_class') or e.get('original_device_class')
        if device_class is not None:text(device_class,64)
        # No entity state is requested here. Kind is a read-only scalar/status, not inferred temperature.
        name=id;name_source='entity-id'
        for key,source in (('name','registry-name'),('original_name','registry-original')):
            candidate=e.get(key)
            if candidate:
                candidate=text(candidate,256)
                if candidate.strip()!=id:name=candidate;name_source=source;break
        icon=e.get('icon') or e.get('original_icon')
        if icon is not None:
            icon=text(icon,128)
            if not re.fullmatch(r'[a-z][a-z0-9_-]*:[a-z0-9]+(?:-[a-z0-9]+)*',icon):raise ReadError('invalid_metadata')
        clean.append({'entityId':id,'name':name,'nameSource':name_source,
          **({'icon':icon} if icon is not None else {}),
          'deviceId':ref(e.get('device_id')),'areaId':ref(e.get('area_id')),
          'entityCategory':category,'disabled':disabled is not None,'deviceClass':device_class,
          'kind':'value' if id.split('.')[0] in ('sensor','binary_sensor','light','cover','switch','input_boolean','input_number','input_select','select','number','fan','climate','humidifier','water_heater','lock','button','input_button','vacuum','valve','event','update','sun','weather') else 'unsupported',
          'value':'Nicht gelesen','unit':'','available':False,'capabilities':[]})
    for rows in (rooms,clean_devices):
        if len({r['id'] for r in rows})!=len(rows):raise ReadError('ambiguous_registry')
    # Under an entity policy, do not disclose unrelated device/area metadata.
    if policy.allowed or policy.denied:
        used_devices={e['deviceId'] for e in clean}
        clean_devices=[d for d in clean_devices if d['id'] in used_devices]
        used_areas={e['areaId'] for e in clean}|{d['areaId'] for d in clean_devices}
        rooms=[a for a in rooms if a['id'] in used_areas]
    return {'source':{'kind':'homeassistant','label':'Home Assistant'},'rooms':rooms,'devices':clean_devices,'entities':clean,
            'fetchedAt':now(),'counts':{'areas':len(rooms),'devices':len(clean_devices),'entities':len(clean),'excludedEntities':len(entities)-len(clean)}}
