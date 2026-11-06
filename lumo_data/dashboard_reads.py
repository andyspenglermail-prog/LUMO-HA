"""Read-only, closed-schema Lovelace copy boundary. No remote mutation methods."""
import re
from client import ReadError

PATH=re.compile(r'[a-z0-9][a-z0-9_-]{0,127}')

def url_path(value):
    if type(value) is not str or not PATH.fullmatch(value):raise ReadError('invalid_dashboard_path',400)
    return value

def dashboard_list(client,guard):
    guard();raw=client.dashboards();guard()
    if type(raw) is not list or len(raw)>256:raise ReadError('dashboard_read_unavailable')
    result=[];seen=set()
    for entry in raw:
        if type(entry) is not dict:raise ReadError('dashboard_read_unavailable')
        path=entry.get('url_path');title=entry.get('title');mode=entry.get('mode')
        if type(path) is not str or not PATH.fullmatch(path) or path in seen or type(title) is not str or not title.strip() or len(title)>256 or any(ord(c)<32 for c in title) or mode not in ('storage','yaml') or type(entry.get('require_admin')) is not bool:raise ReadError('dashboard_read_unavailable')
        seen.add(path)
        # Supervisor credentials do not prove the ingress user's admin status.
        if entry.get('require_admin',False):continue
        result.append({'urlPath':path,'title':title,'mode':mode})
    return {'dashboards':result,'count':len(result)}

def dashboard_config(client,policy,path,guard):
    path=url_path(path)
    entry=next((entry for entry in dashboard_list(client,guard)['dashboards'] if entry['urlPath']==path),None)
    if entry is None:raise ReadError('dashboard_not_found',404)
    guard();config=client.dashboard(path);guard()
    validate_configuration(config,policy)
    return {'urlPath':path,'title':entry['title'],'config':config}

def validate_configuration(config,policy,*,allow_adjacent_unheaded=False):
    """Closed native grammar; validate every binding before returning any bytes.

    This is a safety gate, not a layout converter. JS applies tighter model
    representability checks and refuses atomically. Never redact an opaque field.
    Publication may preserve separate direct runs around retained empty groups;
    read-import must still reject that non-round-trippable section arrangement.
    """
    import json
    import math
    from client import ENTITY
    def require(ok):
        if not ok:raise ReadError('unsupported_configuration',422)
    def fields(value,required,optional=()):
        require(type(value) is dict and set(required)<=set(value)<=set(required)|set(optional))
    def integer(value,low,high):return type(value) is int and low<=value<=high
    def finite_number(value):
        if type(value) not in (int,float):return False
        try:return math.isfinite(value)
        except OverflowError:return False
    def label(value):return type(value) is str and 0<len(value)<=256 and bool(value.strip()) and not any(ord(c)<32 for c in value)
    def entity(value):require(type(value) is str and len(value)<=256 and ENTITY.fullmatch(value) and policy.permits(value))
    count=[0]
    def data(value,depth=0):
        count[0]+=1;require(depth<=20 and count[0]<=100000)
        if type(value) is dict:
            for key,item in value.items():
                require(type(key) is str and key not in ('__proto__','constructor','prototype'));data(item,depth+1)
        elif type(value) is list:
            for item in value:data(item,depth+1)
        else:require(value is None or type(value) in (str,bool,int) or type(value) is float and math.isfinite(value))
    data(config);require(len(json.dumps(config,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode())<=1048576)
    fields(config,('views',),('title',))
    if 'title' in config:require(label(config['title']))
    require(type(config['views']) is list and 1<=len(config['views'])<=16)
    blocks=0;groups=0;paths=set()
    for index,view in enumerate(config['views']):
        fields(view,('title','type','sections'),('path','max_columns','dense_section_placement'))
        path=view.get('path',str(index))
        require(label(view['title']) and type(path) is str and len(path)<=128 and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]*',path) and path not in paths)
        paths.add(path)
        require(view['type']=='sections' and integer(view.get('max_columns',4),1,4) and view.get('dense_section_placement',False) is False and type(view['sections']) is list and len(view['sections'])<=160)
        previous_unheaded=False
        for section in view['sections']:
            fields(section,('type','cards'));require(section['type']=='grid' and type(section['cards']) is list and 1<=len(section['cards'])<=129)
            headed=section['cards'][0].get('type')=='heading' if type(section['cards'][0]) is dict else False
            require(allow_adjacent_unheaded is True or not (previous_unheaded and not headed));previous_unheaded=not headed
            for ci,card in enumerate(section['cards']):
                require(type(card) is dict);kind=card.get('type');features=[]
                if kind=='heading':
                    fields(card,('type','heading'),('grid_options',));require(ci==0 and len(section['cards'])>1 and label(card['heading']));groups+=1
                elif kind=='history-graph':
                    fields(card,('type','title','entities','grid_options'),('hours_to_show',))
                    require(label(card['title']) and type(card['entities']) is list and 1<=len(card['entities'])<=8 and integer(card.get('hours_to_show',24),1,168))
                    for item in card['entities']:entity(item)
                    blocks+=1
                elif kind=='gauge':
                    fields(card,('type','name','entity','grid_options'),('min','max'))
                    entity(card['entity']);require(label(card['name']))
                    low,high=card.get('min',0),card.get('max',100)
                    require(finite_number(low) and finite_number(high) and low<high);blocks+=1
                else:
                    fields(card,('type','name','entity','tap_action','icon_tap_action'),('grid_options','features','features_position','state_content','hold_action','double_tap_action','icon'))
                    require(kind=='tile' and label(card['name']));entity(card['entity']);blocks+=1
                    if 'icon' in card:require(type(card['icon']) is str and re.fullmatch(r'mdi:[a-z0-9]+(?:-[a-z0-9]+)*',card['icon']) and len(card['icon'])<=80)
                    features=card.get('features',[]);require(type(features) is list and len(features)<=1 and card.get('features_position','bottom')=='bottom')
                    for feature in features:
                        fields(feature,('type',));require(feature['type'] in ('light-brightness','cover-open-close','cover-position','cover-tilt-position'))
                        require(card['entity'].startswith('light.' if feature['type']=='light-brightness' else 'cover.'))
                    for key in ('tap_action','hold_action','double_tap_action','icon_tap_action'):
                        action=card.get(key,{'action':'none'});fields(action,('action',))
                        require(action['action']=='none' or key=='icon_tap_action' and action['action']=='toggle' and card['entity'].startswith('light.') and not features)
                    if 'state_content' in card:
                        require(type(card['state_content']) is list and len(card['state_content'])==1 and card['state_content'][0] in ('brightness','current_position','current_tilt_position','temperature','humidity'))
                    attribute=card.get('state_content')
                    if features:
                        expected={'cover-position':['current_position'],'cover-tilt-position':['current_tilt_position']}.get(features[0]['type'])
                        require(attribute==expected)
                    if card['icon_tap_action']['action']=='toggle':require(attribute is None)
                default={'columns':12,'rows':'auto'} if kind=='heading' else {'columns':6,'rows':2 if features else 1}
                grid=card.get('grid_options',default);fields(grid,('columns','rows'))
                require(integer(grid['columns'],12 if kind in ('heading','history-graph') else 6,12))
                require(grid['rows']=='auto' if kind=='heading' else integer(grid['rows'],4 if kind=='history-graph' else 2 if kind=='gauge' or features else 1,12))
    require(blocks<=128 and groups<=32)
