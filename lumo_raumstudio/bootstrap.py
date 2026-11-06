"""Read only our fixed Supervisor options, then irrevocably become UID65532.

No listener, requests, helper thread, environment-secret transport or permission
repair. Test code may supply a local options path to prepare(); main never does.
"""
import ctypes
import os
from pathlib import Path
import sys
from policy import load_snapshot

UID = GID = 65532

def drop_privileges():
    libc = ctypes.CDLL(None, use_errno=True)
    def prctl(option, arg=0, arg2=0):
        if libc.prctl(option, arg, arg2, 0, 0) != 0:
            raise RuntimeError('unsafe_startup')
    # No inherited privileged descriptor survives into the application.
    for name in os.listdir('/proc/self/fd'):
        fd = int(name)
        if fd >= 3:
            try: os.close(fd)
            except OSError as error:
                # Only enumeration's own already-closed descriptor is benign.
                if error.errno != 9: raise RuntimeError('unsafe_startup') from None
    prctl(38, 1)  # PR_SET_NO_NEW_PRIVS
    prctl(8, 0)   # PR_SET_KEEPCAPS: never retain capabilities across setuid
    prctl(47, 4)  # PR_CAP_AMBIENT_CLEAR_ALL
    initial = dict(line.split(':', 1) for line in Path('/proc/self/status').read_text().splitlines() if ':' in line)
    can_drop_bounding = bool(int(initial['CapEff'], 16) & (1 << 8))  # CAP_SETPCAP
    for cap in range(64):
        ctypes.set_errno(0)
        present = libc.prctl(23, cap, 0, 0, 0)  # PR_CAPBSET_READ
        if present < 0:
            if ctypes.get_errno() == 22: continue  # outside kernel's cap range
            raise RuntimeError('unsafe_startup')
        if present and can_drop_bounding: prctl(24, cap)  # PR_CAPBSET_DROP
    os.setgroups([])
    os.setresgid(GID, GID, GID)
    os.setresuid(UID, UID, UID)
    # Verify kernel state, including effective/permitted/inheritable/bounding/
    # ambient capabilities, rather than relying only on successful setters.
    state = dict(line.split(':', 1) for line in Path('/proc/self/status').read_text().splitlines() if ':' in line)
    if (os.getresuid() != (UID,)*3 or os.getresgid() != (GID,)*3 or os.getgroups()
            or state['NoNewPrivs'].strip() != '1'
            or any(int(state[key], 16) for key in ('CapInh','CapPrm','CapEff','CapAmb'))
            or (can_drop_bounding and int(state['CapBnd'], 16))):
        raise RuntimeError('unsafe_startup')

def prepare(options_path='/data/options.json',data_path='/data/raumstudio'):
    # Private Python-only seams for isolated tests; main always uses fixed paths.
    import stat
    from policy import _parent
    from client import CoreClient
    if os.getresuid()!=(0,0,0):raise RuntimeError('unsafe_startup')
    snapshot=load_snapshot(options_path)
    token=os.environ.pop('SUPERVISOR_TOKEN','')
    client=CoreClient(token) if token else None
    parent,name,_=_parent(data_path)
    try:
        try:os.mkdir(name,0o700,dir_fd=parent);created=True
        except FileExistsError:created=False
        fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
        try:
            s=os.fstat(fd)
            if not stat.S_ISDIR(s.st_mode):raise RuntimeError('unsafe_data_directory')
            if created:os.fchown(fd,UID,GID);os.fchmod(fd,0o700)
            elif s.st_uid!=UID or s.st_gid!=GID or stat.S_IMODE(s.st_mode)!=0o700:raise RuntimeError('unsafe_data_directory')
            # Deliberately no recursive chown and no symlink traversal.
            for entry in os.listdir(fd):
                child=os.stat(entry,dir_fd=fd,follow_symlinks=False)
                if not stat.S_ISREG(child.st_mode) or child.st_nlink!=1 or child.st_uid!=UID or child.st_gid!=GID:raise RuntimeError('unsafe_data_file')
        finally:os.close(fd)
    finally:os.close(parent)
    os.umask(0o077);drop_privileges();return snapshot,client

def main():
    try:
        snapshot,client=prepare()
        from server import main as serve
        serve(options_snapshot=snapshot,client=client);return 0
    except Exception:
        print('LUMO Raumstudio: sicherer Start nicht möglich. Konfiguration, Datenrechte und passende Sicherung prüfen.',file=sys.stderr);return 3
if __name__=='__main__':sys.exit(main())
