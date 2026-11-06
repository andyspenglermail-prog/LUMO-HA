"""Optional owner/CAS presentation overlay. Never compiles or edits a dashboard."""
import copy,json
from store import StudioError,now

def defaults():
    return {'schemaVersion':1,'category':'Luxury & Signature','profile':'noir','overrides':{},'targets':['desktop'],'activeTarget':'desktop','displays':{'desktop':{'width':1440,'height':900,'orientation':'auto','dpr':1,'input':'mouse','diagonal':None,'hardwareWidth':None,'hardwareHeight':None,'client':'browser','kiosk':False}},'options':{'highContrast':False,'motion':'reduced'}}

from pathlib import Path
import re,math
CATALOG=json.loads((Path(__file__).parent/'design-catalog.json').read_text())
COLORS={'primary','secondary','accent','text','card','border'}
ENUMS={'material':('flat','soft','layered'),'font':tuple(CATALOG['fonts']),'size':('standard','comfortable','wall'),'density':('compact','balanced','spacious')}

def contrast(a,b):
    def lum(s):
        v=[int(s[i:i+2],16)/255 for i in (1,3,5)]
        return sum((x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4)*w for x,w in zip(v,(.2126,.7152,.0722)))
    x,y=sorted((lum(a),lum(b)))
    return (y+.05)/(x+.05)

def resolved(value):
    return {**CATALOG['profiles'][value['profile']],**value['overrides']}

def validate(value):
    def bad(message='Ungültiges Design oder Displayprofil.'):raise StudioError(message)
    def num(v,lo,hi,integer=False):
        if type(v) not in ((int,) if integer else (int,float)) or not lo<=v<=hi or not math.isfinite(v):bad()
    if type(value) is not dict or set(value)!=set(defaults()):bad()
    if type(value['schemaVersion']) is not int or value['schemaVersion']!=1:bad()
    if type(value['profile']) is not str or value['profile'] not in CATALOG['profiles']:bad()
    if value['category'] not in [c['name'] for c in CATALOG['categories']]:bad()
    o=value['overrides']
    if type(o) is not dict or not set(o)<=COLORS|set(ENUMS)|{'radius','shadow','weight'}:bad()
    for k,v in o.items():
        if k in COLORS:
            if type(v) is not str or not re.fullmatch('#[a-fA-F0-9]{6}',v):bad()
        elif k in ENUMS:
            if type(v) is not str or v not in ENUMS[k]:bad()
        elif k in ('radius','shadow'):num(v,0,40,True)
        elif k=='weight':
            if type(v) is not int or v not in (400,500,600,700):bad()
    t=resolved(value)
    if contrast(t['text'],t['card'])<4.5:bad('Text und Kartenhintergrund benötigen mindestens 4,5:1 Kontrast.')
    targets=value['targets'];displays=value['displays']
    if type(targets) is not list or not targets or len(targets)>6 or any(type(x) is not str or x not in CATALOG['targets'] for x in targets) or len(set(targets))!=len(targets):bad()
    if value['activeTarget'] not in targets or type(displays) is not dict or set(displays)!=set(targets):bad()
    fields=set(defaults()['displays']['desktop'])
    for d in displays.values():
        if type(d) is not dict or set(d)!=fields:bad()
        num(d['width'],320,3840,True);num(d['height'],240,2160,True);num(d['dpr'],.5,4)
        if d['orientation'] not in ('auto','portrait','landscape') or d['input'] not in ('mouse','touch') or d['client'] not in ('browser','ha-app') or type(d['kiosk']) is not bool:bad()
        if d['diagonal'] is not None:num(d['diagonal'],3,150)
        for k in ('hardwareWidth','hardwareHeight'):
            if d[k] is not None:num(d[k],240,16384,True)
    opts=value['options']
    if type(opts) is not dict or set(opts)!={'highContrast','motion'} or type(opts['highContrast']) is not bool or opts['motion'] not in ('reduced','subtle'):bad()
    return value

def sources(document):
    """Bounded inert projection, not native-card execution or layout conversion."""
    from client import ENTITY
    from imported import materialize
    native=materialize(document) if 'nativeImport' in document else document.get('native') or {}
    result={}
    for v in document['views']:
        view=native.get('views',[])[v['nativeIndex']]
        if type(view) is not dict:view={}
        value=view.get('background',native.get('background'))
        source='Ansicht' if 'background' in view else 'Importiertes Dashboard'
        background=None if value is None else {'value':value if type(value) is str and re.fullmatch('#[a-fA-F0-9]{6}',value) else None,'source':source,'supported':type(value) is str and bool(re.fullmatch('#[a-fA-F0-9]{6}',value))}
        refs=[];protected=[];seen=set();count=0;depth_limited=False
        def walk(cards,depth=0):
            nonlocal count,depth_limited
            if type(cards) is not list:return
            if depth>8:
                if cards and not depth_limited:
                    protected.append({'type':'depth-limit','title':'Verschachtelungsgrenze der Vorschau erreicht. Original bleibt vollständig erhalten.'})
                    depth_limited=True
                return
            for card in cards:
                count+=1
                if count>2000:return
                if type(card) is not dict:continue
                kind=card.get('type')
                if kind in ('vertical-stack','horizontal-stack','grid'):walk(card.get('cards'),depth+1);continue
                if kind not in ('tile','entity','entities','sensor','button','glance','light','thermostat'):
                    protected.append({'type':str(kind)[:100],'title':str(card.get('title',card.get('name','Geschützter Inhalt')))[:160]});continue
                candidates=[card.get('entity')]+(card.get('entities',[]) if type(card.get('entities')) is list else [])
                for item in candidates:
                    eid=item.get('entity') if type(item) is dict else item
                    if type(eid) is str and ENTITY.fullmatch(eid) and eid not in seen:
                        seen.add(eid);refs.append({'key':'state:'+eid,'entityId':eid})
        walk(view.get('cards'))
        for section in view.get('sections',[]) if type(view.get('sections')) is list else []:
            if type(section) is dict:walk(section.get('cards'))
        result[v['id']]={'background':background,'backgroundOverride':v.get('backgroundOverride'),'refs':refs,'protected':protected,'truncated':count>2000,'themeProtected':'theme' in view or 'theme' in native}
    return result

def save(store,owner,id,revision,value):
    value=copy.deepcopy(validate(value))
    with store.connect() as c:
        c.execute('BEGIN IMMEDIATE');d=store.checked(c,owner,id,revision)
        d['design']=value;d['revision']+=1;d['updatedAt']=now()
        c.execute('UPDATE dashboards SET revision=?,document=? WHERE id=? AND owner=? AND revision=?',(d['revision'],json.dumps(d),id,owner,revision))
    return store.get(owner,id)
