"""Read-only opt-in policy; immutable snapshot with metadata-change latched denial."""
import os
import re
import stat
import fnmatch
from pathlib import Path
from dataclasses import dataclass
from client import parse_json
SAFE_ID=re.compile(r'[A-Za-z0-9_-]{1,128}')
PATTERN=re.compile(r'[a-z_*][a-z0-9_*]*\.[a-z0-9_*]+')
@dataclass(frozen=True)
class Policy:
    users:frozenset
    allowed:tuple
    denied:tuple
    def permits(self,entity):
        return (not self.allowed or any(fnmatch.fnmatchcase(entity,p) for p in self.allowed)) and not any(fnmatch.fnmatchcase(entity,p) for p in self.denied)

def parse_settings(raw):
    try:
        if len(raw)>131072:return None
        v=parse_json(raw)
        if type(v) is not dict or set(v)!={'enabled','allowed_user_ids','allowed_entity_patterns','denied_entity_patterns'} or v['enabled'] is not True:return None
        users=v['allowed_user_ids']
        if type(users) is not list or not 1<=len(users)<=256 or any(type(u) is not str or not SAFE_ID.fullmatch(u) for u in users) or len(set(users))!=len(users):return None
        for key in ('allowed_entity_patterns','denied_entity_patterns'):
            values=v[key]
            if type(values) is not list or len(values)>64 or any(type(p) is not str or len(p)>256 or not PATTERN.fullmatch(p) for p in values) or len(set(values))!=len(values):return None
        return Policy(frozenset(users),tuple(v['allowed_entity_patterns']),tuple(v['denied_entity_patterns']))
    except (ValueError,TypeError,UnicodeError,RecursionError):return None

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

