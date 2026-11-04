"""Fixed-origin HTTPS text client. No native API proxy or TLS bypass."""
import http.client
import json
import re
import ssl
import os
import stat
from pathlib import Path
from urllib.parse import urlsplit
from validation import parse_body, request_body, InvalidRequest, valid_output

SAFE_ID = re.compile(r'[A-Za-z0-9_-]{1,128}')
ROUTES = (
    ('POST', r'/lumo/v1/conversations', 'create'),
    ('POST', r'/lumo/v1/conversations/[0-9a-f]{32}/turns', 'turn'),
    ('GET', r'/lumo/v1/runs/[0-9a-f]{32}', 'poll'),
    ('POST', r'/lumo/v1/runs/[0-9a-f]{32}/stop', 'stop'),
    ('DELETE', r'/lumo/v1/conversations/[0-9a-f]{32}', 'delete'),
)
def route(method, path):
    return next((op for m,p,op in ROUTES if m == method and re.fullmatch(p,path)), None)

def parse_settings(raw):
    """Validate a private bounded startup buffer without IO or network."""
    try:
        if len(raw)>131072: return None
        # Options contain a bounded public PEM, larger than API request bodies.
        from validation import _pairs, _constant
        value=json.loads(raw.decode('utf-8'),object_pairs_hook=_pairs,parse_constant=_constant)
        if type(value) is not dict or set(value) != {'bridge_url','bridge_ca','bridge_token','allowed_user_ids'}: return None
        url,ca,token,users=(value[k] for k in ('bridge_url','bridge_ca','bridge_token','allowed_user_ids'))
        if any(type(v) is not str for v in (url,ca,token)): return None
        if len(url)>512 or not url.isascii() or any(c.isspace() for c in url): return None
        u=urlsplit(url)
        if (u.scheme!='https' or not u.hostname or u.username is not None or u.password is not None
                or u.path not in ('','/') or u.query or u.fragment or '%' in url or '\\' in url): return None
        if not re.fullmatch(r'[A-Za-z0-9.-]+',u.hostname) or not 1 <= (u.port or 443) <= 65535: return None
        if not re.fullmatch(r'[!-~]{32,256}',token): return None
        if type(users) is not list or len(users)>256 or any(type(v) is not str or not SAFE_ID.fullmatch(v) for v in users): return None
        if len(set(users)) != len(users) or not 1 <= len(ca.encode('utf-8')) <= 65536: return None
        ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_verify_locations(cadata=ca)
        return (u.hostname,u.port or 443,ctx,token,frozenset(users))
    except (OSError,ValueError,TypeError,UnicodeError,RecursionError,ssl.SSLError): return None

def _identity(s):
    return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,
            s.st_uid,s.st_gid,s.st_mode,s.st_nlink)

def _parent(path):
    """Component-wise NOFOLLOW traversal; caller always closes directory FD."""
    parts=Path(path).parts
    if not Path(path).is_absolute() or not 2 <= len(parts) <= 32 or '..' in parts:
        raise ValueError()
    fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    chain=[]
    try:
        for part in parts[1:-1]:
            next_fd=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd)
            os.close(fd);fd=next_fd
            s=os.fstat(fd)
            chain.append((s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid))
        return fd,parts[-1],tuple(chain)
    except BaseException:
        os.close(fd);raise

def _metadata(path):
    fd,name,chain=_parent(path)
    try:
        s=os.stat(name,dir_fd=fd,follow_symlinks=False)
        if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1: raise ValueError()
        return chain,_identity(s)
    finally: os.close(fd)

class OptionsSnapshot:
    """Private immutable validated policy; any observed change latches denial.

    A restart is required even if the previous source bytes are restored. No
    privileged FD/helper or nonroot secret reread is retained.
    """
    def __init__(self,path,config=None,identity=None):
        self._path=str(path);self._config=config;self._identity=identity
        self._disabled=config is None
    def current(self):
        if not self._disabled:
            try:
                if _metadata(self._path)!=self._identity: self._disabled=True
            except (OSError,ValueError): self._disabled=True
        return None if self._disabled else self._config

def load_snapshot(path):
    try:
        parent,name,chain=_parent(path)
        try:
            fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent)
            try:
                before=os.fstat(fd)
                if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_size>131072:
                    raise ValueError()
                raw=b''
                while len(raw)<=131072:
                    chunk=os.read(fd,min(16384,131073-len(raw)))
                    if not chunk: break
                    raw+=chunk
                after=os.fstat(fd)
                identity=(chain,_identity(before))
                if _identity(after)!=_identity(before): raise ValueError()
            finally: os.close(fd)
        finally: os.close(parent)
        config=parse_settings(raw)
        # Re-resolve the pathname AFTER validation; atomic replace must not bind
        # a freshly parsed old inode to a different current pathname.
        if _metadata(path)!=identity: raise ValueError()
        return OptionsSnapshot(path,config,identity)
    except (OSError,ValueError,TypeError):
        return OptionsSnapshot(path)

def settings(path):
    """Readable local test/legacy seam; packaged main uses one startup snapshot."""
    return load_snapshot(path).current()

def forward(config, user, method, path, raw):
    """Only validated routes/bodies/verified user; never forward client headers."""
    op=route(method,path)
    if not op or not SAFE_ID.fullmatch(user) or user not in config[4]: return 403,{'error':'forbidden'}
    try: request_body(raw,op)
    except InvalidRequest as e: return e.status,{'error':e.code}
    connection=http.client.HTTPSConnection(config[0],config[1],timeout=5,context=config[2])
    try:
        connection.request(method,path,body=raw or None,headers={'Authorization':'Bearer '+config[3],'X-LUMO-User-Id':user,'Content-Type':'application/json','Connection':'close','Accept-Encoding':'identity'})
        response=connection.getresponse()
        if response.status not in (200,201,202,400,401,403,404,409,413,429,503): raise ValueError()
        lengths=response.headers.get_all('Content-Length',[])
        if (len(lengths)!=1 or not re.fullmatch(r'[0-9]{1,6}',lengths[0]) or int(lengths[0])>65536
                or response.headers.get_all('Transfer-Encoding') or response.headers.get('Content-Type','').split(';')[0]!='application/json'): raise ValueError()
        body=response.read(65537)
        if len(body)!=int(lengths[0]): raise ValueError()
        # Requests remain 16KiB. Escaped JSON responses may be up to 64KiB;
        # the existing decoded text validator still enforces 8KiB UTF-8.
        from validation import _pairs, _constant
        value=json.loads(body.decode('utf-8'),object_pairs_hook=_pairs,parse_constant=_constant)
        if type(value) is not dict: raise ValueError()
        if response.status>=400:
            # Do not reflect a remote error string, even from the configured host.
            return response.status,{'error':'bridge_rejected'}
        if op=='create':
            good=response.status==201 and set(value)=={'conversation_id'} and type(value['conversation_id']) is str and re.fullmatch(r'[0-9a-f]{32}',value['conversation_id'])
        elif op=='delete': good=response.status==200 and value=={'status':'deleted'}
        else:
            good=(response.status==(202 if op=='turn' else 200) and set(value) in ({'run_id','status','provider_state'},{'run_id','status','provider_state','text'})
                  and type(value['run_id']) is str and re.fullmatch(r'[0-9a-f]{32}',value['run_id'])
                  and value['status'] in ('queued','running','stopping','unknown','cancelled','failed','completed') and value['provider_state']=='unverified'
                  and ('text' not in value or (value['status']=='completed' and valid_output(value['text']))))
            if good and op in ('poll','stop'): good=value['run_id']==path.split('/')[4]
        if not good: raise ValueError()
        return response.status,value
    except (OSError,http.client.HTTPException,ValueError,TypeError,KeyError,InvalidRequest,RecursionError):
        return 502,{'error':'bridge_unknown'}
    finally: connection.close()
