"""Lossless import: immutable source plus server-authorized scalar replacements.

Unknown JSON is data, not executable code, CSS, URLs or merge instructions.
No schema normalization, array insertion/removal/reorder or client source writes.
"""
import copy,hashlib,json,re
from store import StudioError,text,icon_value,now
from client import ENTITY

CARD_FIELDS={
    'entity':('name','icon','entity'), 'tile':('name','icon','entity'),
    'sensor':('name','icon','entity'), 'gauge':('name','entity'),
    'entities':('title',), 'history-graph':('title',), 'heading':('heading','icon'),
    'grid':(), 'vertical-stack':('title',), 'horizontal-stack':('title',)
}
LABELS={'title':'Titel','name':'Anzeigename','heading':'Überschrift','icon':'Symbol','entity':'Entitätskennung'}

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,allow_nan=False,separators=(',',':')).encode()).hexdigest()

def resources_unavailable():
    return {'status':'unavailable','items':None,'verification':'unverified',
            'message':'Ressourcenliste nicht verfügbar. Abhängigkeiten sind unbekannt, nicht als fehlend oder funktionsfähig bestätigt.'}

def state(source_path=None,resources=None):
    return {'version':1,'sourcePath':source_path,'capturedAt':now(),
            'resources':copy.deepcopy(resources if resources is not None else resources_unavailable()),'edits':[]}

def field_value(key,value):
    if type(value) is not str or any(s in value for s in ('[[[','{{','{%')):
        raise StudioError('Templates und nicht unterstützte Werte bleiben geschützt.',422)
    try:
        if key=='entity':
            if not ENTITY.fullmatch(value):raise StudioError('Bitte eine gültige Entitätskennung eingeben.')
        elif key=='icon':icon_value(value)
        else:text(value,LABELS[key],256)
    except StudioError as e:raise StudioError(e.message,422) from None
    # Validate without trimming or otherwise normalizing the chosen scalar.
    return value

def editable_elements(config):
    elements=[]
    def fields(obj,path,keys,kind):
        if type(obj) is not dict:return
        fs=[]
        for k in keys:
            if k not in obj:continue
            try:field_value(k,obj[k])
            except StudioError:continue
            fs.append({'path':path+[k],'label':LABELS[k],'kind':k,'value':obj[k]})
        if fs:elements.append({'path':path,'type':kind,'label':str(obj.get('title',obj.get('name',obj.get('heading',kind))))[:256],'fields':fs})
    def cards(items,path):
        if type(items) is not list:return
        for i,c in enumerate(items):
            p=path+[i]
            if type(c) is not dict or type(c.get('type')) is not str or c['type'] not in CARD_FIELDS:continue
            kind=c['type'];fields(c,p,CARD_FIELDS[kind],kind)
            if kind in ('grid','vertical-stack','horizontal-stack'):cards(c.get('cards'),p+['cards'])
    fields(config,[],('title',),'Dashboard')
    views=config.get('views')
    if type(views) is list:
        for i,v in enumerate(views):
            if type(v) is not dict or v.get('type','masonry') not in ('masonry','sections','panel'):continue
            p=['views',i];fields(v,p,('title','icon'),'Ansicht')
            cards(v.get('cards'),p+['cards'])
            sections=v.get('sections')
            if type(sections) is list:
                for j,s in enumerate(sections):
                    if type(s) is dict and s.get('type','grid')=='grid':cards(s.get('cards'),p+['sections',j,'cards'])
    return elements

def apply_edits(original,edits):
    from dashboard_reads import bounded
    if type(edits) is not list or len(edits)>1000:raise StudioError('Zu viele gezielte Änderungen.',422)
    allowed={tuple(f['path']):f['kind'] for e in editable_elements(original) for f in e['fields']}
    result=copy.deepcopy(original);seen=set()
    for edit in edits:
        if type(edit) is not dict or set(edit)!={'path','value'}:raise StudioError('Ungültige gezielte Änderung.',422)
        path=edit['path']
        if type(path) is not list or not path or any(type(p) not in (str,int) for p in path):raise StudioError('Dieser Konfigurationspfad ist geschützt.',422)
        key=tuple(path)
        if key not in allowed or key in seen:raise StudioError('Dieser Konfigurationspfad ist geschützt oder doppelt gewählt.',422)
        seen.add(key);value=field_value(allowed[key],edit['value']);target=result
        for p in path[:-1]:target=target[p]
        target[path[-1]]=value
    bounded(result)
    return result

def materialize(document):
    return apply_edits(document['native'],document['nativeImport']['edits'])

def validate_state(document):
    from dashboard_reads import bounded,PATH
    from datetime import datetime
    s=document['nativeImport']
    if type(s) is not dict or set(s)!={'version','sourcePath','capturedAt','resources','edits'} or type(s['version']) is not int or s['version']!=1:raise ValueError('invalid_import_state')
    if s['sourcePath'] is not None and (type(s['sourcePath']) is not str or not PATH.fullmatch(s['sourcePath'])):raise ValueError('invalid_source_path')
    if datetime.fromisoformat(s['capturedAt']).tzinfo is None:raise ValueError('invalid_capture_time')
    r=s['resources']
    if type(r) is not dict or set(r)!={'status','items','verification','message'} or r['verification']!='unverified' or type(r['message']) is not str:raise ValueError('invalid_resources')
    if r['status']=='captured':
        if type(r['items']) is not list:raise ValueError('invalid_resources')
        bounded(r['items'])
    elif r['status']!='unavailable' or r['items'] is not None:raise ValueError('invalid_resources')
    materialize(document)

def report(document):
    config=materialize(document);elements=editable_elements(config)
    allowed={tuple(f['path']) for e in elements for f in e['fields']}
    protected=[];protected_count=0;custom=set();themes=set();references=set();templates=False;styles=False
    def scan(v,path):
        nonlocal protected_count,templates,styles
        if type(v) is dict:
            for k,x in v.items():
                if k=='button_card_templates':templates=True
                if k in ('card_mod','styles','style'):styles=True
                if k=='theme' and type(x) is str:themes.add(x)
                if k=='type' and type(x) is str and x.startswith('custom:'):custom.add(x)
                scan(x,path+[k])
        elif type(v) is list:
            for i,x in enumerate(v):scan(x,path+[i])
        if type(v) not in (dict,list) or not v:
            if tuple(path) not in allowed:
                protected_count+=1
                if len(protected)<200:
                    short=[p[:160]+'…' if type(p) is str and len(p)>160 else p for p in path]
                    protected.append({'path':short,'pathTruncated':short!=path,'message':'Unverändert geschützt; keine Bearbeitung oder Ausführung in LUMO.'})
        if type(v) is str:
            for ref in re.findall(r'(?:https?://|/local/|/hacsfiles/)[^\s\"\'<>)}\]]+',v):references.add(ref[:512])
    scan(config,[])
    resources=copy.deepcopy(document['nativeImport']['resources'])
    return {'revision':document['revision'],
            'summary':'Vollständig als unabhängige Kopie übernommen. Unbekannte Inhalte, Templates und Styles bleiben erhalten und geschützt. Nichts wird in Home Assistant geändert oder hier ausgeführt.',
            'sourceHash':digest(document['native']),'exportHash':digest(config),
            'editCount':len(document['nativeImport']['edits']),
            'editableElements':elements[:1000],'editableCount':len(elements),'editableTruncated':len(elements)>1000,
            'protected':{'count':protected_count,'details':protected,'truncated':protected_count>len(protected)},
            'dependencies':{'customCardTypes':sorted(custom),'templates':templates,'styles':styles,'themes':sorted(themes),'externalReferences':sorted(references)[:200],'referencesTruncated':len(references)>200,
                            'message':'Ressourcen, Themes und Dateien werden nicht mitkopiert. Registrierung beweist weder Verfügbarkeit noch Funktion. Eine vollständige Zuordnung von Karten zu Dateien ist nicht möglich.'},
            'resources':resources}
