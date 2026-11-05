"""Explicit on/off only. No toggle, generic service proxy or automatic retry."""
import secrets
import time
from client import ReadError

DOMAINS=('light','switch','input_boolean')
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
    available=set();seen=set()
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
        if domain in DOMAINS and all(action in names for action in ACTIONS):available.add(domain)
    return available

def capability(state,available):
    domain=state['entityId'].split('.')[0]
    reason=('unsupported' if domain not in DOMAINS else
            'unavailable' if state['quality']!='good' or state['value'] not in ('on','off') else
            'service-unavailable' if domain not in available else None)
    return {'actions':list(ACTIONS) if reason is None else [],'reason':reason}

def execute_control(client,policy,entity,action,guard):
    from data import clean_state,now
    if entity.split('.')[0] not in DOMAINS or action not in ACTIONS:raise ReadError('unsupported_control',400)
    if not policy.permits(entity):raise ReadError('forbidden',403)
    deadline=time.monotonic()+15
    guard();current=clean_state(entity,client.state(entity,deadline=deadline));guard()
    if current['quality']!='good' or current['value'] not in ('on','off'):raise ReadError('entity_unavailable',409)
    available=service_domains(client.services(deadline=deadline));guard()
    if entity.split('.')[0] not in available:raise ReadError('service_unavailable',409)
    # Check immediately before AND after dispatch; a changed policy releases no state.
    guard()
    try:client.turn(entity,action,deadline=deadline)
    finally:guard()
    confirmation='unknown';result=None
    try:
        result=clean_state(entity,client.state(entity,deadline=deadline))
        result['control']=capability(result,available)
        if result['quality']=='good' and result['value'] in ('on','off'):
            confirmation='confirmed' if result['value']==('on' if action=='turn_on' else 'off') else 'pending'
    except ReadError:pass  # Dispatch acknowledged, readback is separately unknown.
    guard()
    return {'entityId':entity,'action':action,'accepted':True,'state':result,'fetchedAt':now(),'confirmation':confirmation}
