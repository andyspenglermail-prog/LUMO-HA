"""Read only our fixed Supervisor options, then irrevocably become UID65532.

No listener, requests, helper thread, environment-secret transport or permission
repair. Test code may supply a local options path to prepare(); main never does.
"""
import ctypes
import os
from pathlib import Path
import sys
from bridge import load_snapshot

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

def prepare(options_path='/data/options.json'):
    if os.getresuid() != (0, 0, 0):
        raise RuntimeError('unsafe_startup')
    snapshot = load_snapshot(options_path)
    drop_privileges()
    return snapshot

def main():
    try:
        snapshot = prepare()  # fixed path; no argv/env configuration transport
        from server import main as serve
        serve(options_snapshot=snapshot)
        return 0
    except Exception:
        # No raw exception, path, options, CA or secret reaches logs.
        print('LUMO startup unavailable', file=sys.stderr)
        return 3

if __name__ == '__main__':
    sys.exit(main())
