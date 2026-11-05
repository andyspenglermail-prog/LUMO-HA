"""Closed action vocabulary. Metadata is evidence, never a service payload."""
import math
from decimal import Decimal,localcontext
from client import ReadError

MISSING=object()
LEGACY=('light','switch','input_boolean')
COVER={
 'open_cover':(1,'Öffnen',None),'close_cover':(2,'Schließen',None),
 'stop_cover':(8,'Stopp',None),'set_cover_position':(4,'Position','position'),
 'open_cover_tilt':(16,'Lamellen öffnen',None),'close_cover_tilt':(32,'Lamellen schließen',None),
 'stop_cover_tilt':(64,'Lamellen stoppen',None),'set_cover_tilt_position':(128,'Lamellenposition','tilt_position')}
SPECS={d:{a:(a,None) for a in ('turn_on','turn_off')} for d in LEGACY}
SPECS['cover']={a:(a,row[2]) for a,row in COVER.items()}
SPECS['light'].update({'set_brightness':('turn_on','brightness'),'set_color_temperature':('turn_on','color_temp_kelvin')})
SPECS['climate']={'set_temperature':('set_temperature','temperature'),'set_hvac_mode':('set_hvac_mode','hvac_mode')}
SPECS['fan']={'turn_on':('turn_on',None),'turn_off':('turn_off',None),'set_percentage':('set_percentage','percentage'),'set_preset_mode':('set_preset_mode','preset_mode')}
for domain in ('number','input_number'):SPECS[domain]={'set_value':('set_value','value')}
for domain in ('select','input_select'):SPECS[domain]={'select_option':('select_option','option')}
SELECT_ACTIONS={'set_hvac_mode','set_preset_mode','select_option'}
DOMAINS=tuple(SPECS)

def number(v):return type(v) in (int,float) and abs(v)<=1e12 and math.isfinite(v)
def string(v):return type(v) is str and 0<len(v)<=256 and not any(ord(c)<32 or ord(c)==127 for c in v)
def options(v):return type(v) is list and 0<len(v)<=256 and all(string(x) for x in v) and len(set(v))==len(v)

def attributes(raw):
    result={}
    for key in ('supported_features','current_position','current_tilt_position','brightness','color_temp_kelvin','min_color_temp_kelvin','max_color_temp_kelvin','temperature','current_temperature','min_temp','max_temp','target_temp_step','percentage','percentage_step','min','max','step'):
        v=raw.get(key)
        if number(v) and (key!='supported_features' or type(v) is int and 0<=v<=2147483647):result[key]=v
    for key in ('supported_color_modes','hvac_modes','preset_modes','options'):
        if options(raw.get(key)):result[key]=raw[key][:]
    if raw.get('temperature_unit') in ('°C','°F'):result['temperature_unit']=raw['temperature_unit']
    if string(raw.get('preset_mode')):result['preset_mode']=raw['preset_mode']
    return result

def numeric(action,label,lo,hi,step,current=None,unit=None):
    if not all(number(v) for v in (lo,hi,step)) or not lo<hi or step<=0 or step>hi-lo:return None
    result={'action':action,'label':label,'kind':'number','min':lo,'max':hi,'step':step}
    if unit:result['unit']=unit
    if number(current) and lo<=current<=hi:result['current']=current
    return result

def selection(action,label,values,current):
    if not options(values):return None
    result={'action':action,'label':label,'kind':'select','options':values[:]}
    if type(current) is str and current in values:result['current']=current
    return result

def capability(state,available):
    domain=state['entityId'].split('.')[0];attrs=state.get('attributes',{});controls=[];notes=[]
    def add(c):
        if c is not None and SPECS[domain][c['action']][0] in available.get(domain,set()):controls.append(c)
    def button(a,label):add({'action':a,'label':label,'kind':'button'})
    reason=None
    if domain not in DOMAINS:reason='unsupported'
    elif state['quality']!='good' or domain in (*LEGACY,'fan') and state['value'] not in ('on','off'):reason='unavailable'
    elif domain in LEGACY:
        if all(a in available.get(domain,set()) for a in ('turn_on','turn_off')):
            button('turn_on','Einschalten');button('turn_off','Ausschalten')
        else:reason='service-unavailable'
        if domain=='light':
            modes=set(attrs.get('supported_color_modes',[]))
            if modes & {'brightness','color_temp','hs','xy','rgb','rgbw','rgbww','white'}:
                add(numeric('set_brightness','Helligkeit',0,255,1,attrs.get('brightness')))
            lo=attrs.get('min_color_temp_kelvin');hi=attrs.get('max_color_temp_kelvin')
            if 'color_temp' in modes and number(lo) and number(hi) and lo>0:
                add(numeric('set_color_temperature','Farbtemperatur',lo,hi,1,attrs.get('color_temp_kelvin'),'K'))
            if controls:reason=None
    elif domain in ('number','input_number'):
        if not number(state['value']):reason='unavailable'
        else:add(numeric('set_value','Wert',attrs.get('min'),attrs.get('max'),attrs.get('step'),state['value'],state.get('unit')))
    elif domain in ('select','input_select'):
        add(selection('select_option','Auswahl',attrs.get('options'),state['value']))
    elif domain=='fan':
        flags=attrs.get('supported_features',0)
        if flags&32:button('turn_on','Einschalten')
        if flags&16:button('turn_off','Ausschalten')
        step=attrs.get('percentage_step')
        if flags&1 and number(step) and step%1==0:add(numeric('set_percentage','Drehzahl',0,100,step,attrs.get('percentage'),'%'))
        elif flags&1:notes.append('Drehzahlschritt fehlt oder ist kein ganzzahliger Prozentwert; kein Regler.')
        if flags&8:add(selection('set_preset_mode','Voreinstellung',attrs.get('preset_modes'),attrs.get('preset_mode')))
    elif domain=='climate':
        flags=attrs.get('supported_features',0)
        if flags&1 and attrs.get('temperature_unit') in ('°C','°F'):
            add(numeric('set_temperature','Zieltemperatur',attrs.get('min_temp'),attrs.get('max_temp'),attrs.get('target_temp_step'),attrs.get('temperature'),attrs['temperature_unit']))
        add(selection('set_hvac_mode','Betriebsart',attrs.get('hvac_modes'),state['value']))
        if not attrs.get('temperature_unit'):notes.append('Temperatureinheit nicht gemeldet; kein Temperaturregler.')
    elif domain=='cover':
        flags=attrs.get('supported_features',0)
        if state['value'] not in ('open','closed','opening','closing'):reason='unavailable'
        elif not flags:reason='unsupported'
        else:
            for action,(flag,label,key) in COVER.items():
                if flags&flag:
                    add(numeric(action,label,0,100,1,attrs.get('current_'+key),'%')) if key else button(action,label)
            if flags&240!=240:notes.append('Lamellenaktionen nur mit gemeldeter Unterstützung verfügbar.')
    if reason is None and not controls:reason='service-unavailable'
    result={'actions':[c['action'] for c in controls],'controls':controls,'reason':reason}
    if notes:result['notes']=notes
    return result

def validate_shape(entity,action,value=MISSING):
    domain=entity.split('.')[0]
    if type(action) is not str or action not in SPECS.get(domain,{}):raise ReadError('unsupported_control',400)
    key=SPECS[domain][action][1]
    if key is None:
        if value is not MISSING:raise ReadError('invalid_value',400)
    elif action in SELECT_ACTIONS:
        if not string(value):raise ReadError('invalid_value',400)
    elif value is MISSING or not number(value):raise ReadError('invalid_value',400)
    elif action in ('set_cover_position','set_cover_tilt_position','set_brightness','set_color_temperature','set_percentage') and value%1!=0:raise ReadError('invalid_value',400)
    return domain

def validate(entity,action,value,state,available):
    domain=validate_shape(entity,action,value)
    cap=capability(state,available)
    control=next((c for c in cap['controls'] if c['action']==action),None)
    if control is None:raise ReadError('entity_unavailable' if cap['reason']=='unavailable' else 'service_unavailable',409)
    if control['kind']=='select' and value not in control['options']:raise ReadError('invalid_value',400)
    if control['kind']=='number':
        if not control['min']<=value<=control['max']:raise ReadError('invalid_value',400)
        # Exact decimal grid, no tolerance that accepts tiny off-step writes.
        with localcontext() as ctx:
            ctx.prec=400
            if (Decimal(str(value))-Decimal(str(control['min'])))%Decimal(str(control['step']))!=0:raise ReadError('invalid_value',400)
    service,key=SPECS[domain][action]
    return service,{'entity_id':entity,**({key:value} if key else {})}

def confirmation(state,action,value=MISSING):
    if state['quality']!='good':return 'unknown'
    observed=state['value'];attrs=state.get('attributes',{})
    if action in ('stop_cover','stop_cover_tilt'):return 'unknown' # No reliable stopped state / tilt-motion evidence.
    expected={'turn_on':'on','turn_off':'off','open_cover':'open','close_cover':'closed'}.get(action,MISSING)
    if action=='set_temperature':observed=attrs.get('temperature',MISSING);expected=value
    if action=='set_hvac_mode':expected=value
    if action in ('set_value','select_option'):expected=value
    if action in ('set_percentage','set_preset_mode'):
        observed=attrs.get('percentage' if action=='set_percentage' else 'preset_mode',MISSING);expected=value
    if action in ('open_cover','close_cover') and 'current_position' in attrs:
        observed=attrs['current_position'];expected=100 if action=='open_cover' else 0
    if action in ('set_brightness','set_color_temperature'):
        observed=attrs.get('brightness' if action=='set_brightness' else 'color_temp_kelvin',MISSING);expected=value
        if action=='set_brightness' and value==0:return 'confirmed' if state['value']=='off' else 'pending'
        if state['value']!='on':return 'pending'
    if action in ('set_cover_position','set_cover_tilt_position','open_cover_tilt','close_cover_tilt'):
        key='current_tilt_position' if 'tilt' in action else 'current_position'
        observed=attrs.get(key,MISSING)
        expected=100 if action=='open_cover_tilt' else 0 if action=='close_cover_tilt' else value
    if observed is MISSING or expected is MISSING:return 'unknown'
    return 'confirmed' if observed==expected else 'pending'
