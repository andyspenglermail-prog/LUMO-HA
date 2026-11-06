"""Private, transactional owner-scoped dashboard management envelope."""
import copy
import json
import sqlite3
import uuid
import re
from contextlib import contextmanager
from pathlib import Path
ICONS=json.loads((Path(__file__).parent/'mdi.json').read_text())

def text(value,label,limit,empty=False):
    if type(value) is not str or len(value)>limit or (not empty and not value.strip()) or any(ord(c)<32 or 127<=ord(c)<160 or 0xD800<=ord(c)<=0xDFFF for c in value):
        raise StudioError(f'{label}: bitte einen gültigen Text mit höchstens {limit} Zeichen eingeben.')
    return value.strip()

def icon_value(value):
    if type(value) is not str or value!='' and value not in ICONS:
        raise StudioError('Icon: nicht im lokalen MDI-Katalog 7.4.47 vorhanden. Bitte ein angebotenes Symbol wählen, zum Beispiel mdi:home.')
    return value
from datetime import datetime, timezone

class StudioError(Exception):
    def __init__(self,message,status=400,details=None):
        self.message=message; self.status=status; self.details=details or []
        super().__init__(message)

def now(): return datetime.now(timezone.utc).isoformat(timespec='microseconds')
def defaults():
    return {'background':{'color':'#eef2ef','imageId':None,'position':'center center','mode':'cover','scale':100,'opacity':100,'attachment':'scroll'},'navigation':{'showIconAndTitle':True,'startView':None,'showInSidebar':True,'requireAdmin':True}}

def import_views(native):
    views=native.get('views')
    if type(views) is not list:return []
    # Display-only metadata, never write these fallbacks into native JSON.
    return [{'id':uuid.uuid4().hex,'title':v.get('title') if type(v) is dict and type(v.get('title')) is str else 'Ansicht '+str(i+1),
             'icon':v.get('icon','') if type(v) is dict and type(v.get('icon','')) is str else '',
             'nativeIndex':i,'backgroundOverride':None} for i,v in enumerate(views)]

class Store:
    def __init__(self,path):
        self.path=Path(path)
        if self.path.is_symlink():raise StudioError('Unsicherer Datenpfad.',503)
        with self.connect() as c:
            version=c.execute('PRAGMA user_version').fetchone()[0]
            if version not in (0,1,2):raise StudioError('Dieses Datenformat benötigt eine andere App-Version. Bitte eine passende Sicherung wiederherstellen.',503)
            if version==0:
                if c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchone():raise StudioError('Unbekannter Datenbestand.',503)
                c.execute('CREATE TABLE dashboards (id TEXT PRIMARY KEY, owner TEXT NOT NULL, revision INTEGER NOT NULL, document TEXT NOT NULL)')
                c.execute('CREATE TABLE images (id TEXT PRIMARY KEY, owner TEXT NOT NULL, metadata TEXT NOT NULL, bytes BLOB NOT NULL)')
                c.execute('CREATE INDEX dashboards_owner ON dashboards(owner)')
                c.execute('PRAGMA user_version=2')
            if c.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise StudioError('Die Datenbank ist beschädigt. Bitte eine Sicherung wiederherstellen.',503)
        from maintenance import migrate,inspect
        if version==1:migrate(self.path)
        inspect(self.path,2)
    @contextmanager
    def connect(self):
        c=sqlite3.connect(self.path,timeout=5); c.row_factory=sqlite3.Row
        c.execute('PRAGMA synchronous=FULL')
        try:
            with c: yield c
        finally:c.close()
    def create(self,owner,name,icon=''):
        name=text(name,'Name',80); icon=icon_value(icon)
        stamp=now(); d={'id':uuid.uuid4().hex,'name':name,'icon':icon,'description':'','createdAt':stamp,'updatedAt':stamp,'status':'Entwurf','schemaVersion':1,'revision':1,'settings':defaults(),'views':[],'native':None}
        with self.connect() as c:c.execute('INSERT INTO dashboards VALUES (?,?,?,?)',(d['id'],owner,1,json.dumps(d)))
        return self.get(owner,d['id'])
    def checked(self,c,owner,id,revision):
        row=c.execute('SELECT document,revision FROM dashboards WHERE id=? AND owner=?',(id,owner)).fetchone()
        if row is None:raise StudioError('Dieser Entwurf ist nicht verfügbar.',404)
        if type(revision) is not int or revision!=row['revision']:
            raise StudioError('Der Entwurf wurde inzwischen geändert. Deine Eingaben bleiben erhalten. Öffne den aktuellen Stand in einem zweiten Tab und übertrage die Änderungen bewusst.',409)
        return json.loads(row['document'])
    def update(self,owner,id,revision,patch):
        if type(patch) is not dict or not patch or not set(patch)<= {'name','icon','description','settings'}:raise StudioError('Ungültige Einstellungen.')
        patch=copy.deepcopy(patch)
        if 'name' in patch:patch['name']=text(patch['name'],'Name',80)
        if 'description' in patch:patch['description']=text(patch['description'],'Beschreibung',1000,True)
        if 'icon' in patch:patch['icon']=icon_value(patch['icon'])
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE'); d=self.checked(c,owner,id,revision)
            if 'settings' in patch:
                from settings import validate
                validate(patch['settings'],d['views'])
                image=patch['settings']['background']['imageId']
                if image is not None:self.image(owner,image)
            d.update(patch); d['revision']+=1; d['updatedAt']=now()
            c.execute('UPDATE dashboards SET revision=?,document=? WHERE id=? AND owner=? AND revision=?',(d['revision'],json.dumps(d),id,owner,revision))
        return self.get(owner,id)
    def duplicate(self,owner,id,revision):
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE'); d=self.checked(c,owner,id,revision)
            d.update(id=uuid.uuid4().hex,name=d['name'][:72]+' · Kopie',revision=1,createdAt=now(),updatedAt=now())
            c.execute('INSERT INTO dashboards VALUES (?,?,?,?)',(d['id'],owner,1,json.dumps(d)))
        return self.get(owner,d['id'])
    def delete(self,owner,id,revision,confirm):
        if confirm is not True:raise StudioError('Bitte das Löschen dieses lokalen Entwurfs bestätigen.')
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE');self.checked(c,owner,id,revision)
            c.execute('DELETE FROM dashboards WHERE id=? AND owner=? AND revision=?',(id,owner,revision))
        return {'deleted':True}
    def import_native(self,owner,name,config,*,source_path=None,resources=None):
        from dashboard_reads import validate_configuration
        from imported import state,validate_state
        native=validate_configuration(config);name=text(name,'Name',80);stamp=now()
        d={'id':uuid.uuid4().hex,'name':name,'icon':'','description':'','createdAt':stamp,'updatedAt':stamp,'status':'Entwurf','schemaVersion':1,'revision':1,'settings':defaults(),'native':native,
           'views':import_views(native), 'nativeImport':state(source_path,resources)}
        validate_state(d)
        with self.connect() as c:c.execute('INSERT INTO dashboards VALUES (?,?,?,?)',(d['id'],owner,1,json.dumps(d)))
        return self.get(owner,d['id'])
    def edit_native(self,owner,id,revision,edits):
        from imported import apply_edits,materialize
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE');d=self.checked(c,owner,id,revision)
            if 'nativeImport' not in d:raise StudioError('Dieser Entwurf ist keine verlustfreie HA-Kopie.',422)
            if type(edits) is not list or not 1<=len(edits)<=32:raise StudioError('Bitte 1–32 gezielte Änderungen senden.',422)
            apply_edits(d['native'],edits)  # Validate the whole batch before any write.
            ledger={tuple(e['path']):e for e in d['nativeImport']['edits']}
            for e in edits:ledger[tuple(e['path'])]=copy.deepcopy(e)
            d['nativeImport']['edits']=list(ledger.values());materialize(d)
            d['revision']+=1;d['updatedAt']=now()
            c.execute('UPDATE dashboards SET revision=?,document=? WHERE id=? AND owner=? AND revision=?',(d['revision'],json.dumps(d),id,owner,revision))
        return self.get(owner,id)
    def put_image(self,owner,name,data):
        from images import decode
        name=text(name,'Bildname',120); raw,w,h=decode(data)
        meta={'id':uuid.uuid4().hex,'name':name,'width':w,'height':h,'createdAt':now(),'mime':'image/png'}
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            count,size=c.execute('SELECT count(*),coalesce(sum(length(bytes)),0) FROM images WHERE owner=?',(owner,)).fetchone()
            if count>=100 or size+len(raw)>128*1024*1024:raise StudioError('Deine Bildbibliothek ist voll (100 Bilder oder 128 MiB).',413)
            c.execute('INSERT INTO images VALUES (?,?,?,?)',(meta['id'],owner,json.dumps(meta),raw))
        return self.image(owner,meta['id'])[0]
    def image(self,owner,id):
        with self.connect() as c:r=c.execute('SELECT metadata,bytes FROM images WHERE id=? AND owner=?',(id,owner)).fetchone()
        if r is None:raise StudioError('Dieses Bild ist nicht verfügbar.',404)
        return json.loads(r['metadata']),r['bytes']
    def images(self,owner):
        with self.connect() as c:rows=c.execute('SELECT metadata FROM images WHERE owner=? ORDER BY rowid DESC',(owner,)).fetchall()
        return [json.loads(r[0]) for r in rows]
    def get(self,owner,id):
        with self.connect() as c:r=c.execute('SELECT document FROM dashboards WHERE id=? AND owner=?',(id,owner)).fetchone()
        if r is None:raise StudioError('Dieser Entwurf ist nicht verfügbar.',404)
        return json.loads(r['document'])
    def list(self,owner):
        with self.connect() as c: rows=c.execute('SELECT document FROM dashboards WHERE owner=? ORDER BY rowid DESC',(owner,)).fetchall()
        return [json.loads(r['document']) for r in rows]
