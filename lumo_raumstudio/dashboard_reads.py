"""Fixed HA reads; active administrator verified before any dashboard bytes."""
import copy,json,math,re
from client import ReadError,ENTITY
from store import StudioError,ICONS
PATH=re.compile(r'[a-z0-9][a-z0-9_-]{0,127}')

def bounded(value):
    count=0
    def walk(v,depth=0):
        nonlocal count
        count+=1
        if depth>20 or count>100000:raise StudioError('Die Konfiguration ist zu tief oder zu groß.',422)
        if type(v) is dict:
            for k,x in v.items():
                if type(k) is not str or k in ('__proto__','constructor','prototype'):raise StudioError('Ungültige Konfigurationsschlüssel.',422)
                walk(x,depth+1)
        elif type(v) is list:
            for x in v:walk(x,depth+1)
        elif not (v is None or type(v) in (str,bool,int) or type(v) is float and math.isfinite(v)):raise StudioError('Ungültige Konfigurationswerte.',422)
    walk(value)
    if len(json.dumps(value,ensure_ascii=False).encode())>1048576:raise StudioError('Die Konfiguration ist größer als 1 MiB.',422)

def validate_configuration(config):
    bounded(config);issues=[]
    def issue(path,msg):issues.append({'path':path,'message':msg})
    def fields(v,path,allowed):
        if type(v) is not dict:issue(path,'Ein Objekt wird erwartet.');return False
        for k in v:
            if k not in allowed:issue(path+'.'+k,'Diese Option wird noch nicht sicher übernommen.')
        return True
    def label(v,path,limit=256):
        if type(v) is not str or not v.strip() or len(v)>limit or any(ord(c)<32 for c in v):issue(path,'Ungültiger Text.')
    def entity(v,path):
        if type(v) is not str or not ENTITY.fullmatch(v):issue(path,'Ungültige Entitätskennung.')
    def bg(v,path):
        if type(v) is not str or not re.fullmatch(r'#[0-9a-fA-F]{6}',v):issue(path,'Vorhandene Bild-/CSS-Hintergründe werden nicht geladen. Bitte zunächst in HA entfernen oder ein eigenes Bild in LUMO verwenden.')
    card_options={
        'entity':{'entity','name','icon','unit','state_color','attribute'},
        'entities':{'entities','title','show_header_toggle','state_color'},
        'tile':{'entity','name','icon','color','vertical','hide_state','state_content','features','features_position'},
        'gauge':{'entity','name','unit','min','max','severity','needle','segments'},
        'sensor':{'entity','name','icon','graph','hours_to_show','detail','unit'},
        'history-graph':{'entities','title','hours_to_show','logarithmic_scale','min_y_axis','max_y_axis','fit_y_data'},
        'heading':{'heading','icon','heading_style'},
        'grid':{'cards','columns','square'},'vertical-stack':{'cards','title'},'horizontal-stack':{'cards','title'}
    }
    def number(v):return type(v) in (int,float) and math.isfinite(v)
    def typed(v,p):
        for k in ('title','name','heading','unit','attribute'):
            if k in v:label(v[k],p+'.'+k)
        if 'icon' in v and (type(v['icon']) is not str or v['icon'] not in ICONS):issue(p+'.icon','Symbol nicht im lokalen MDI-Katalog 7.4.47 vorhanden.')
        for k in ('state_color','vertical','hide_state','show_header_toggle','square','needle','logarithmic_scale','fit_y_data','dense_section_placement','show_icon_and_title','subview'):
            if k in v and type(v[k]) is not bool:issue(p+'.'+k,'Ein Wahrheitswert wird erwartet.')
        for k in ('min','max','min_y_axis','max_y_axis'):
            if k in v and not number(v[k]):issue(p+'.'+k,'Eine endliche Zahl wird erwartet.')
        if 'min' in v and 'max' in v and number(v['min']) and number(v['max']) and v['min']>=v['max']:issue(p+'.min','Minimum muss kleiner als Maximum sein.')
        for k,hi in (('columns',12),('max_columns',12),('column_span',12),('hours_to_show',168),('detail',2)):
            if k in v and (type(v[k]) is not int or not 1<=v[k]<=hi):issue(p+'.'+k,'Eine ganze Zahl von 1 bis '+str(hi)+' wird erwartet.')
        for k,choices in (('graph',('line',)),('features_position',('bottom','inline')),('heading_style',('title','subtitle'))):
            if k in v and v[k] not in choices:issue(p+'.'+k,'Diese Option wird nicht unterstützt.')
        if 'color' in v and (type(v['color']) is not str or not re.fullmatch(r'(#[0-9a-fA-F]{6}|[a-z][a-z-]{0,40})',v['color'])):issue(p+'.color','Ungültige Farbe.')
        if 'state_content' in v:
            items=v['state_content'] if type(v['state_content']) is list else [v['state_content']]
            if not 1<=len(items)<=8 or any(type(x) is not str or not re.fullmatch(r'[a-z_][a-z0-9_]{0,80}',x) for x in items):issue(p+'.state_content','Ungültige Zustandsfelder.')
        if 'grid_options' in v:
            g=v['grid_options'];gp=p+'.grid_options'
            if fields(g,gp,{'columns','rows'}):
                for k,special in (('columns','full'),('rows','auto')):
                    if k in g and g[k]!=special and (type(g[k]) is not int or not 1<=g[k]<=12):issue(gp+'.'+k,'Erwartet wird ein gültiger nativer Rasterwert.')
        if 'severity' in v:
            sev=v['severity']
            if fields(sev,p+'.severity',{'green','yellow','red'}):
                for k,x in sev.items():
                    if not number(x):issue(p+'.severity.'+k,'Eine Zahl wird erwartet.')
        if 'segments' in v:
            seg=v['segments']
            if type(seg) is not list or len(seg)>32:issue(p+'.segments','Ungültige Segmentliste.')
            else:
                for i,x in enumerate(seg):
                    sp=f'{p}.segments[{i}]'
                    if fields(x,sp,{'from','color','label'}):
                        if not number(x.get('from')):issue(sp+'.from','Eine Zahl wird erwartet.')
                        if type(x.get('color')) is not str or not re.fullmatch(r'(#[0-9a-fA-F]{6}|[a-z]{1,24})',x['color']):issue(sp+'.color','Ungültige Farbe.')
                        if 'label' in x:label(x['label'],sp+'.label')
        if 'visible' in v:
            visible=v['visible']
            if type(visible) is not bool:
                if type(visible) is not list or len(visible)>256 or any(type(x) is not dict or set(x)!={'user'} or type(x['user']) is not str or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}',x['user']) for x in visible):issue(p+'.visible','Ungültige Tab-Sichtbarkeit. Sichtbarkeit ist kein Zugriffsschutz.')
    def card(c,p):
        if type(c) is not dict:issue(p,'Ungültige Karte.');return
        kind=c.get('type')
        if type(kind) is not str or kind not in card_options:issue(p+'.type','Nicht unterstützter Kartentyp: '+str(kind)[:80]);return
        fields(c,p,{'type','grid_options','tap_action','hold_action','double_tap_action','icon_tap_action'}|card_options[kind]);typed(c,p)
        if 'entity' in c:entity(c['entity'],p+'.entity')
        elif kind in ('entity','tile','sensor','gauge'):issue(p+'.entity','Entität fehlt.')
        if 'entities' in c:
            if type(c['entities']) is not list or len(c['entities'])>128:issue(p+'.entities','Ungültige Entitätenliste.')
            else:
                for i,e in enumerate(c['entities']):
                    if type(e) is dict:
                        fields(e,f'{p}.entities[{i}]',{'entity','name','icon'});typed(e,f'{p}.entities[{i}]');entity(e.get('entity'),f'{p}.entities[{i}].entity')
                    else:entity(e,f'{p}.entities[{i}]')
        for k in ('tap_action','hold_action','double_tap_action','icon_tap_action'):
            if k in c and (type(c[k]) is not dict or set(c[k])!={'action'} or c[k]['action'] not in ('none','more-info','toggle')):issue(p+'.'+k,'Diese Aktion wird nicht übernommen; keine Aktionen werden in LUMO ausgeführt.')
        if 'features' in c:
            if type(c['features']) is not list:issue(p+'.features','Ungültige Funktionsliste.')
            else:
                for i,f in enumerate(c['features']):
                    if type(f) is not dict or set(f)!={'type'} or f['type'] not in ('light-brightness','cover-open-close','cover-position','cover-tilt-position'):issue(f'{p}.features[{i}]','Diese Kartenfunktion wird nicht übernommen.')
        if 'cards' in c:cards(c['cards'],p+'.cards')
    def cards(cs,p):
        if type(cs) is not list or len(cs)>512:issue(p,'Ungültige oder zu große Kartenliste.');return
        for i,c in enumerate(cs):card(c,f'{p}[{i}]')
    if fields(config,'config',{'title','views','background'}):
        if 'title' in config:label(config['title'],'config.title')
        if 'background' in config:bg(config['background'],'background')
        views=config.get('views')
        if type(views) is not list or not 1<=len(views)<=16:issue('views','Erwartet werden 1–16 konkrete Ansichten. Automatisch erzeugte Strategy-Dashboards werden nicht übernommen.')
        else:
            paths=set()
            for i,v in enumerate(views):
                p=f'views[{i}]'
                if not fields(v,p,{'title','path','icon','type','cards','sections','max_columns','dense_section_placement','show_icon_and_title','subview','visible','background','badges'}):continue
                label(v.get('title'),p+'.title');typed(v,p)
                path=v.get('path',str(i))
                if type(path) is not str or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}',path) or path in paths:issue(p+'.path','Ungültiger oder doppelter Ansichtspfad.')
                else:paths.add(path)
                if v.get('type','masonry') not in ('masonry','sections','panel'):issue(p+'.type','Dieser Ansichtstyp wird nicht unterstützt.')
                if 'background' in v:bg(v['background'],p+'.background')
                if 'badges' in v and (type(v['badges']) is not list or v['badges']):issue(p+'.badges','Nur eine leere Badgeliste wird übernommen; Badges werden noch nicht unterstützt.')
                if 'cards' in v:cards(v['cards'],p+'.cards')
                if 'sections' in v:
                    ss=v['sections']
                    if type(ss) is not list or len(ss)>128:issue(p+'.sections','Ungültige Abschnittsliste.')
                    else:
                        for j,s in enumerate(ss):
                            sp=f'{p}.sections[{j}]'
                            if fields(s,sp,{'type','cards','column_span'}):
                                typed(s,sp)
                                if s.get('type','grid')!='grid':issue(sp+'.type','Nur native Grid-Abschnitte werden übernommen.')
                                cards(s.get('cards'),sp+'.cards')
    if issues:raise StudioError('Keine Übernahme: '+ '; '.join(x['path']+': '+x['message'] for x in issues[:8]),422,issues[:40])
    return copy.deepcopy(config)

class DashboardReads:
    def __init__(self,client):self.client=client
    def admin(self,user):
        if self.client is None:raise StudioError('Home Assistant ist noch nicht verbunden.',503)
        rows=self.client._ws_reads(({'type':'config/auth/list'},),list,'dashboard_admin_unavailable',1048576)[0]
        if len(rows)>1024:raise StudioError('Die HA-Berechtigung konnte nicht geprüft werden.',403)
        match=[r for r in rows if type(r) is dict and r.get('id')==user]
        if len(match)!=1:raise StudioError('HA-Import ist nur für verifizierte aktive Administratoren verfügbar.',403)
        r=match[0];groups=r.get('group_ids')
        if r.get('is_active') is not True or type(r.get('is_owner')) is not bool or type(groups) is not list or any(type(g) is not str for g in groups) or not (r['is_owner'] or 'system-admin' in groups):raise StudioError('HA-Import ist nur für verifizierte aktive Administratoren verfügbar. Eigene lokale Entwürfe bleiben unabhängig davon nutzbar.',403)
    def config(self,path):
        if path is not None and (type(path) is not str or not PATH.fullmatch(path)):raise StudioError('Ungültiger Dashboardpfad.')
        return self.client._ws_reads(({'type':'lovelace/config','url_path':path},),dict,'dashboard_read_unavailable',1052672)[0]
    def catalog(self,user):
        self.admin(user)
        rows=self.client._ws_reads(({'type':'lovelace/dashboards/list'},),list,'dashboard_read_unavailable',1048576)[0]
        if len(rows)>128:raise StudioError('Zu viele HA-Dashboards.',422)
        result=[];seen=set()
        for r in rows:
            if type(r) is not dict or type(r.get('url_path')) is not str or not PATH.fullmatch(r['url_path']) or r['url_path'] in seen or type(r.get('title')) is not str:raise StudioError('Ungültige HA-Dashboardliste.',502)
            seen.add(r['url_path']);result.append({'path':r['url_path'],'title':r['title'],'mode':r.get('mode','unknown')})
        # Only add default if an actual config read succeeds; never a dummy entry.
        try:
            default=self.config(None)
            result.insert(0,{'path':None,'title':default.get('title','Standarddashboard'),'mode':'default','_config':default})
        except ReadError as e:
            if e.code!='dashboard_not_found':raise
        for r in result:
            try:
                cfg=r.pop('_config') if '_config' in r else self.config(r['path'])
                r['viewCount']=len(cfg['views']) if type(cfg.get('views')) is list else None
                validate_configuration(cfg);r['supported']=True;r['issues']=[]
            except StudioError as e:r.update(supported=False,issues=e.details or [{'path':'config','message':e.message}])
            except ReadError:r.update(supported=False,viewCount=None,issues=[{'path':'config','message':'Konfiguration nicht lesbar; YAML-/Strategy-Grenze oder Verbindung prüfen.'}])
        return result
    def read(self,user,path):
        self.admin(user)
        cfg=validate_configuration(self.config(path))
        return {'config':cfg,'path':path}
