"""Offline SQLite maintenance. Stop the app before restore/rollback.
No HTTP restore route. Backup snapshots contain private user data.
"""
import os,sqlite3,uuid,json,stat
from pathlib import Path
SCHEMA=2

def safe_file(path):
    p=Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_nlink!=1:raise ValueError('unsafe_database')
    for parent in p.parents:
        if parent.is_symlink():raise ValueError('unsafe_database')
    return p

def inspect(path,expected_version=None):
    p=safe_file(path)
    c=sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)
    try:
        if c.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('invalid_database')
        version=c.execute('PRAGMA user_version').fetchone()[0]
        if version not in (1,2) or expected_version is not None and version!=expected_version:raise ValueError('unsupported_schema')
        expected={'dashboards':['id','owner','revision','document'],'images':['id','owner','metadata','bytes']}
        if {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}!=set(expected):raise ValueError('invalid_tables')
        for table,columns in expected.items():
            if [r[1] for r in c.execute('PRAGMA table_info('+table+')')]!=columns:raise ValueError('invalid_columns')
        from store import text,icon_value
        from settings import validate,background
        from dashboard_reads import validate_configuration
        from client import parse_json
        from images import decode
        import re
        from datetime import datetime
        keys={'id','name','icon','description','createdAt','updatedAt','status','schemaVersion','revision','settings','views','native'}
        def ident(value):return type(value) is str and re.fullmatch('[a-f0-9]{32}',value)
        for id,owner,revision,raw in c.execute('SELECT * FROM dashboards'):
            d=parse_json(raw)
            if type(d) is not dict or not keys<=set(d)<=keys|{'nativeImport','roomPlan','design'} or not owner or not ident(id) or d['id']!=id or type(revision) is not int or revision<1 or d['revision']!=revision or d['schemaVersion']!=1 or d['status']!='Entwurf' or type(d['views']) is not list or len(d['views'])>100000:raise ValueError('invalid_document')
            text(d['name'],'Name',80);text(d['description'],'Beschreibung',1000,True);icon_value(d['icon'])
            for k in ('createdAt','updatedAt'):
                if datetime.fromisoformat(d[k]).tzinfo is None:raise ValueError('invalid_timestamp')
            if 'design' in d:
                from design import validate as validate_design
                validate_design(d['design'])
            if 'roomPlan' in d:
                from room_store import validate as validate_rooms
                validate_rooms(d['roomPlan'],d)
            validate(d['settings'],d['views'])
            refs=[d['settings']['background']['imageId']]
            if d['native'] is None:
                if d['views'] or 'nativeImport' in d:raise ValueError('invalid_views')
            elif 'nativeImport' in d:
                from store import import_views
                validate_configuration(d['native'])
                expected=import_views(d['native'])
                if len(d['views'])!=len(expected) or len({v.get('id') for v in d['views']})!=len(d['views']):raise ValueError('invalid_views')
                for v,w in zip(d['views'],expected):
                    if not ident(v.get('id')) or {k:x for k,x in v.items() if k!='id'}!={k:x for k,x in w.items() if k!='id'}:raise ValueError('invalid_view')
                from imported import validate_state
                validate_state(d)
            else:
                from dashboard_reads import validate_supported_configuration
                validate_supported_configuration(d['native'])
                if len(d['views'])!=len(d['native']['views']):raise ValueError('invalid_views')
                ids=set()
                for i,v in enumerate(d['views']):
                    if set(v)!={'id','title','icon','nativeIndex','backgroundOverride'} or not ident(v['id']) or v['id'] in ids or v['nativeIndex']!=i or v['title']!=d['native']['views'][i]['title']:raise ValueError('invalid_view')
                    ids.add(v['id']);icon_value(v['icon'])
                    if v['backgroundOverride'] is not None:refs.append(background(v['backgroundOverride'])['imageId'])
            for ref in refs:
                if ref is not None and not c.execute('SELECT 1 FROM images WHERE id=? AND owner=?',(ref,owner)).fetchone():raise ValueError('foreign_image_reference')
        for id,owner,raw,data in c.execute('SELECT * FROM images'):
            m=parse_json(raw)
            if type(m) is not dict or set(m)!={'id','name','width','height','createdAt','mime'} or not owner or not ident(id) or m['id']!=id or m['mime']!='image/png' or not data.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('invalid_image')
            text(m['name'],'Bildname',120);_,width,height=decode(data)
            if (width,height)!=(m['width'],m['height']):raise ValueError('invalid_image_size')
        return version
    finally:c.close()

def sync_dir(path):
    fd=os.open(str(Path(path).parent),os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)

def backup(source,destination):
    source=safe_file(source);destination=Path(destination);version=inspect(source)
    fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600);os.close(fd)
    try:
        src=sqlite3.connect(source.as_uri()+'?mode=ro',uri=True);dst=sqlite3.connect(destination)
        try:src.backup(dst)
        finally:src.close();dst.close()
        inspect(destination,version)
        with destination.open('rb') as f:os.fsync(f.fileno())
        sync_dir(destination)
        return destination
    except BaseException:
        destination.unlink(missing_ok=True);raise

def restore(source,target,expected_version=None):
    source=safe_file(source);target=safe_file(target);inspect(source,expected_version)
    if any(Path(str(target)+suffix).exists() for suffix in ('-wal','-shm','-journal')):raise ValueError('stop_application_first')
    tmp=target.with_name(target.name+'.restore-'+uuid.uuid4().hex)
    try:
        backup(source,tmp);inspect(tmp,expected_version);os.replace(tmp,target);sync_dir(target)
    finally:tmp.unlink(missing_ok=True)

def migrate(path,*,inject_failure=False):
    path=safe_file(path);version=inspect(path)
    if version==SCHEMA:return
    snapshot=backup(path,path.with_name(path.name+'.pre-v1-'+uuid.uuid4().hex+'.sqlite'))
    c=sqlite3.connect(path)
    try:
        c.execute('BEGIN EXCLUSIVE')
        c.execute('CREATE INDEX dashboards_owner ON dashboards(owner)')
        if inject_failure:raise ValueError('test_migration_failure')
        c.execute('PRAGMA user_version=2');c.commit();inspect(path,2)
    except BaseException:
        c.rollback();c.close();restore(snapshot,path,expected_version=1);raise
    finally:c.close()

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(description='Nur bei gestoppter Raumstudio-App verwenden.');ap.add_argument('action',choices=['backup','restore','inspect']);ap.add_argument('source');ap.add_argument('target',nargs='?');a=ap.parse_args()
    if a.action=='inspect':print(inspect(a.source))
    elif not a.target:ap.error('Ziel fehlt')
    else:globals()[a.action](a.source,a.target);print('Geprüft abgeschlossen.')
