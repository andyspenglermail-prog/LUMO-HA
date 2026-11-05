"""Explicit capability operations; no generic service proxy or retries."""
import secrets
import time
from client import ReadError

from capabilities import DOMAINS,capability,validate,validate_shape,confirmation,MISSING
ACTIONS=('turn_on','turn_off')

class ControlSessions:
    """Process-local, bounded, one-use tokens; server handles requests serially."""
    def __init__(self):self.tokens={}
    def issue(self,user,policy):
        now=time.monotonic()
        self.tokens={key:value for key,value in self.tokens.items() if value[2]>now}
        if len(self.tokens)>=1024:raise ReadError('control_busy',429)
        token=secrets.token_urlsafe(32)
        self.tokens[token]=(user,policy,now+120)
        return {'token':token,'expiresIn':120}
    def consume(self,token,user,policy):
        value=self.tokens.pop(token,None)
        if value is None or value[0]!=user or value[1] is not policy or value[2]<=time.monotonic():
            raise ReadError('invalid_control_token',403)

def service_domains(raw):
    if type(raw) is not list or len(raw)>1024:raise ReadError('invalid_services')
    available={};seen=set()
    for row in raw:
        if type(row) is not dict or type(row.get('domain')) is not str:raise ReadError('invalid_services')
        domain=row['domain'];services=row.get('services')
        if type(services) is list:
            if len(services)>2048 or any(type(name) is not str for name in services) or len(set(services))!=len(services):raise ReadError('invalid_services')
            names=set(services)
        elif type(services) is dict:
            if len(services)>2048 or any(type(value) is not dict for value in services.values()):raise ReadError('invalid_services')
            names=set(services)
        else:raise ReadError('invalid_services')
        if domain in seen:raise ReadError('invalid_services')
        seen.add(domain)
        if domain in DOMAINS:available[domain]=names
    return available

def execute_control(client,policy,entity,action,guard,value=MISSING):
    from data import clean_state,now
    validate_shape(entity,action,value)
    if not policy.permits(entity):raise ReadError('forbidden',403)
    deadline=time.monotonic()+15
    guard();current=clean_state(entity,client.state(entity,deadline=deadline));guard()
    if current['quality']!='good' or capability(current,{})['reason']=='unavailable':raise ReadError('entity_unavailable',409)
    available=service_domains(client.services(deadline=deadline));guard()
    validate(entity,action,value,current,available)
    # Check immediately before AND after dispatch; a changed policy releases no state.
    guard()
    try:client.operate(entity,action,value,state=current,available=available,deadline=deadline)
    finally:guard()
    outcome='unknown';result=None
    try:
        result=clean_state(entity,client.state(entity,deadline=deadline))
        result['control']=capability(result,available)
        outcome=confirmation(result,action,value)
        if action=='set_temperature' and current['attributes'].get('temperature_unit')!=result.get('attributes',{}).get('temperature_unit'):outcome='unknown'
        if action=='set_value' and current['unit']!=result['unit']:outcome='unknown'
    except ReadError:pass  # Dispatch acknowledged, readback is separately unknown.
    guard()
    return {'entityId':entity,'action':action,'accepted':True,'state':result,'fetchedAt':now(),'confirmation':outcome,**({'value':value} if value is not MISSING else {})}
