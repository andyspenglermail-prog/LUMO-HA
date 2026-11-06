'use strict';
// Configure surface: local references and genuine HA observations never share state.
let roomPlan=null,roomSaved=null,roomDashboard=null,roomRevision=null,roomActive=null,roomDirty=false,roomHistory=[],roomDeleted=[],roomInventory=null,roomReading=false,roomGeneration=0,roomContext=null,roomPreview=null,roomPoll=null,roomFresh=false;
const roomExpanded=new Set();
const roomAvailability={available:'Verfügbar',disabled:'Deaktiviert',missing_state:'Kein Zustand',missing:'Nicht mehr im Bestand',unavailable:'Nicht verfügbar',unknown:'Unbekannt',no_entities:'Keine Entitäten',no_available_entities:'Keine verfügbare Entität'};
function roomId(){const a=crypto.getRandomValues(new Uint8Array(16));a[6]=(a[6]&15)|64;a[8]=(a[8]&63)|128;return [...a].map(x=>x.toString(16).padStart(2,'0')).join('');}
function roomView(){return roomPlan?.views.find(v=>v.id===roomActive);}
function roomArea(id){return roomInventory?.areas.find(a=>a.area_id===id);}
function roomAreaLabel(id){return id===null||id===undefined?'Nicht zugeordnet':(roomArea(id)?.name||'Fehlender Bereich')+' · '+id;}
function roomPanel(panel){$('.room-columns').dataset.panel=panel;$$('[data-room-panel]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.roomPanel===panel)));}
function roomChanged(){roomDirty=JSON.stringify(roomPlan)!==JSON.stringify(roomSaved);$('#room-dirty').textContent=roomDirty?'Ungespeicherte Änderungen · nur in diesem Tab':'Gespeichert · Revision '+(roomRevision||'–');$('#room-undo').disabled=busy||!roomHistory.length;roomCancelPreview();}
function roomRemember(){roomHistory.push({plan:clone(roomPlan),active:roomActive,deleted:[...roomDeleted]});if(roomHistory.length>50)roomHistory.shift();}
function roomMutate(fn,editor=false){if(busy||!roomPlan)return;roomRemember();fn();roomChanged();roomRender(editor);}
function roomCancelPreview(){roomPreview=null;$('#correction-confirm').hidden=true;$('#correction-details').replaceChildren();}
function roomStop(){roomGeneration++;clearInterval(roomPoll);roomPoll=null;}
async function roomEnter(){
  roomStop();const generation=roomGeneration;$('#room-dashboard').textContent=selected?'Dashboard: '+selected.name:'Bitte zuerst ein Dashboard auswählen.';
  if(!selected||roomDashboard!==selected.id||roomRevision!==selected.revision){
    const id=selected?.id,revision=selected?.revision;
    // Never expose the previous dashboard's editor while another context loads.
    roomPlan=roomSaved=roomDashboard=roomRevision=roomActive=roomContext=null;roomHistory=[];roomDeleted=[];roomDirty=false;roomExpanded.clear();roomChanged();roomRender(true);
    if(!id)return;
    try{const r=await api('dashboards/'+id+'/rooms');if(generation!==roomGeneration||selected?.id!==id||selected?.revision!==revision)return;if(r.dashboardId!==id||r.revision!==revision)throw Error('Der Dashboardstand wurde inzwischen geändert. Bitte bewusst erneut öffnen.');roomPlan=clone(r.plan);roomSaved=clone(r.plan);roomDashboard=id;roomRevision=revision;roomActive=roomPlan.views[0]?.id||null;roomChanged();roomRender(true);}
    catch(e){if(generation===roomGeneration)notice(e.message,true);return;}
  }else roomRender(true);
  await roomRefresh();if(generation!==roomGeneration)return;
  roomPoll=setInterval(()=>{if(!document.hidden&&!busy&&!$('#room-step').hidden)void roomRefresh(false);},30000);
}
async function roomRefresh(manual=true){
  if(roomReading)return;roomReading=true;const generation=roomGeneration;
  $('#room-refresh').disabled=true;$('#room-status').textContent=roomInventory?'Bestand wird neu gelesen …':'HA-Bestand wird gelesen …';
  try{const value=await api('ha/inventory');if(generation!==roomGeneration)return;roomInventory=value;roomFresh=true;
    $('#connection').textContent='Home Assistant · lesend verbunden';$('#room-status').textContent='Frisch gelesen · '+new Date(value.fetchedAt).toLocaleTimeString('de-DE')+' · automatische Abfrage alle 30 s';
    // A telemetry refresh never mutates the staged plan or authored form fields.
    roomRender(false);
  }catch(e){if(generation!==roomGeneration)return;roomFresh=false;roomCancelPreview();$('#connection').textContent='HA · Verbindung / Rechte nicht bestätigt';$('#room-status').textContent=(roomInventory?'Veraltet · letzter erfolgreicher Abruf '+new Date(roomInventory.fetchedAt).toLocaleTimeString('de-DE'):'Kein HA-Bestand verfügbar')+' · '+e.message;roomRender(false);}
  finally{roomReading=false;$('#room-refresh').disabled=busy;}
}
function roomAllEntities(){
  const result=[...(roomInventory?.entities||[])],known=new Set(result.map(e=>e.key));
  for(const v of roomPlan?.views||[])for(const ref of v.entityRefs)if(!known.has(ref.key)){known.add(ref.key);result.push({key:ref.key,registryId:ref.key.startsWith('registry:')?ref.key.slice(9):null,entityId:ref.entityId,name:ref.entityId,domain:ref.entityId.split('.')[0],deviceId:null,effectiveAreaId:null,areaSource:'none',availability:'missing',attributes:{},state:null});}
  return result;
}
function roomAllDevices(){
  const result=[...(roomInventory?.devices||[])],known=new Set(result.map(d=>d.id));
  for(const v of roomPlan?.views||[])for(const id of v.deviceIds)if(!known.has(id)){known.add(id);result.push({id,name:id,areaId:null,entityKeys:[],entityCount:0,availability:'missing'});}
  return result;
}
function roomSelected(key){return Boolean(roomView()?.entityRefs.some(e=>e.key===key));}
function roomSetEntity(entity,on){const v=roomView();if(!v)return;v.entityRefs=v.entityRefs.filter(e=>e.key!==entity.key);if(on)v.entityRefs.push({key:entity.key,entityId:entity.entityId});}
function roomSetDevice(device,on){const v=roomView();if(!v)return;v.deviceIds=v.deviceIds.filter(id=>id!==device.id);if(on)v.deviceIds.push(device.id);for(const e of roomAllEntities().filter(e=>e.deviceId===device.id))roomSetEntity(e,on);}
function roomPickView(id){roomActive=id;roomContext=null;roomCancelPreview();roomRender(true);roomPanel('inventory');}
function roomMake(title,area=null){const id=roomId();roomMutate(()=>{roomPlan.views.push({id,title:title.slice(0,80),icon:'',visible:true,areaId:area,source:area?'ha-area':'virtual',nativeViewId:null,deviceIds:[],entityRefs:[]});roomActive=id;},true);roomPanel('inventory');}
function roomRender(editor=false){
  const v=roomView();$('#room-new').disabled=busy||!roomPlan;$('#room-save').disabled=busy||!roomPlan;$('#room-editor').hidden=!v;$('#room-empty').hidden=Boolean(v);$('#room-heading-title').textContent=v?v.title+' – Raumansicht':'Deine Raumansicht';$('#room-selection-count').textContent=v?v.deviceIds.length+' Geräte · '+v.entityRefs.length+' Entitäten':'';
  if(editor&&v){$('#room-title').value=v.title;if(![...$('#room-icon').options].some(o=>o.value===v.icon))$('#room-icon').add(new Option(v.icon,v.icon));$('#room-icon').value=v.icon;$('#room-visible').checked=v.visible;}
  const origin=$('#room-origin');origin.replaceChildren();if(v){const area=roomArea(v.areaId),floor=roomInventory?.floors.find(f=>f.floor_id===area?.floor_id);origin.append(text('strong',v.areaId?roomAreaLabel(v.areaId):v.source==='native'?'Native HA-Kopie · lokale Referenz':'Virtuelle Ansicht · ohne HA-Bereich'));if(area?.floor_id)origin.append(text('p','Etage: '+(floor?.name||'Fehlend')+' · '+area.floor_id));if(v.source==='native')origin.append(text('p','Native Inhalte bleiben geschützt und unverändert. Die lokale Auswahl ist eine separate Vorbereitung.','hint'));}
  const query=$('#room-view-search').value.toLocaleLowerCase(),views=$('#room-views'),sources=$('#room-sources');views.replaceChildren();sources.replaceChildren();
  for(const view of roomPlan?.views||[]){if(!(view.title+' '+roomAreaLabel(view.areaId)).toLocaleLowerCase().includes(query))continue;const b=button('',()=>roomPickView(view.id),'room-view-item');b.dataset.view=view.id;b.setAttribute('aria-current',view.id===roomActive?'page':'false');b.append(icon(view.icon||'mdi:view-dashboard'),text('span',view.title),text('small',(view.source==='virtual'?'Virtuell':view.source==='native'?'Native Kopie':'HA-Bereich')+' · '+view.deviceIds.length+' Geräte · '+view.entityRefs.length+' Entitäten'+(!view.visible?' · verborgen':'')));views.append(b);}
  if(!roomPlan?.views.length)views.append(text('p','Noch keine lokalen Ansichten.','empty'));
  for(const area of roomInventory?.areas||[]){if(!(area.name+' '+area.area_id).toLocaleLowerCase().includes(query))continue;const b=button('',()=>{if(!roomPlan)return;const existing=roomPlan.views.find(x=>x.areaId===area.area_id);if(existing)roomPickView(existing.id);else roomMake(area.name,area.area_id);},'room-source-item');b.dataset.area=area.area_id;b.append(icon('mdi:home'),text('span',area.name),text('small',area.deviceCount+' Geräte · '+area.entityCount+' Entitäten · '+area.area_id));b.disabled=busy||!roomPlan;sources.append(b);}
  if(!roomInventory)sources.append(text('p','HA-Bereiche noch nicht verfügbar. Es werden keine Beispieldaten verwendet.','hint'));
  const all=roomAllEntities(),devices=roomAllDevices();$('#room-unassigned').textContent='Nicht zugeordnet · '+devices.filter(d=>!d.areaId).length+' Geräte · '+all.filter(e=>!e.effectiveAreaId).length+' Entitäten';
  roomRenderInventory(all,devices);roomRenderProperties();$('#room-undo').disabled=busy||!roomHistory.length;
  for(const id of ['room-title','room-icon','room-visible','room-up','room-down','room-duplicate','room-delete','room-select-visible','room-clear-visible'])$('#'+id).disabled=busy||!v;
}
function roomMatches(e,device){
  const v=roomView(),scope=$('#room-scope').value,filter=$('#room-filter').value,q=$('#room-search').value.trim().toLocaleLowerCase();
  if(scope==='none'&&e.effectiveAreaId||scope==='view'&&v?.areaId&&e.effectiveAreaId!==v.areaId)return false;
  if(q&&![e.name,e.entityId,e.domain,device?.name,roomAreaLabel(e.effectiveAreaId)].join(' ').toLocaleLowerCase().includes(q))return false;
  if(filter==='all')return true;if(filter==='none')return !e.effectiveAreaId;if(filter==='unavailable')return e.availability!=='available';if(filter==='selected')return roomSelected(e.key);
  if(filter==='sensor')return ['sensor','binary_sensor'].includes(e.domain);if(filter==='climate')return ['climate','fan','humidifier','water_heater'].includes(e.domain);if(filter==='switch')return ['switch','input_boolean'].includes(e.domain);if(filter==='other')return !['sensor','binary_sensor','light','cover','climate','fan','humidifier','water_heater','switch','input_boolean'].includes(e.domain);return e.domain===filter;
}
function roomVisibleEntities(){const devices=new Map(roomAllDevices().map(d=>[d.id,d]));return roomAllEntities().filter(e=>roomMatches(e,devices.get(e.deviceId)));}
function roomCheckbox(label,checked,fn,attr,value){const l=text('label','','room-check');const c=document.createElement('input');c.type='checkbox';c.checked=checked;c.disabled=busy||!roomView();c.setAttribute('aria-label',label);c.dataset[attr]=value;c.onchange=()=>roomMutate(()=>fn(c.checked));l.append(c);return l;}
function roomEntityRow(e,matched=true){
  const row=text('div','','room-entity'+(matched?'':' outside-filter'));row.dataset.entity=e.key;
  const label=roomCheckbox('In LUMO auswählen: '+e.entityId,roomSelected(e.key),on=>roomSetEntity(e,on),'entityCheck',e.key);const inspect=button('',()=>{roomContext={kind:'entity',id:e.key};roomCancelPreview();$('#room-correction').open=false;roomRenderProperties();roomPanel('properties');},'room-inspect');inspect.dataset.inspectEntity=e.key;
  inspect.append(icon(e.icon&&Object.hasOwn(icons,e.icon)?e.icon:({light:'mdi:lightbulb',cover:'mdi:blinds',sensor:'mdi:thermometer'}[e.domain]||'mdi:circle-outline')),text('strong',e.name),text('small',e.entityId+' · '+roomAreaLabel(e.effectiveAreaId)));
  const status=text('span',e.availability==='available'?String(e.state??'–')+(e.unit?' '+e.unit:''):roomAvailability[e.availability]||e.availability,'room-value');if(!roomFresh)status.append(text('small','Veraltet'));
  if(e.disabledBy||e.hiddenBy||e.entityCategory)inspect.append(text('small',[e.disabledBy?'deaktiviert: '+e.disabledBy:'',e.hiddenBy?'in HA verborgen: '+e.hiddenBy:'',e.entityCategory].filter(Boolean).join(' · ')));
  if(!matched)inspect.append(text('small','Außerhalb des Filters · tatsächliche Geräteentität'));
  row.append(label,inspect,status);return row;
}
function roomRenderInventory(all,devices){
  const root=$('#room-inventory'),scroll=root.scrollTop,focused=root.contains(document.activeElement)?Object.entries(document.activeElement.dataset):[];root.replaceChildren();let matches=0,deviceCount=0;
  const q=$('#room-search').value.trim().toLocaleLowerCase(),scope=$('#room-scope').value,filter=$('#room-filter').value;
  for(const d of devices){const entities=all.filter(e=>e.deviceId===d.id),matching=entities.filter(e=>roomMatches(e,d));const emptyMatch=!entities.length&&(!q||(d.name+' '+d.id).toLocaleLowerCase().includes(q))&&(scope==='all'||scope==='none'&&!d.areaId||scope==='view'&&(!roomView()?.areaId||d.areaId===roomView().areaId))&&(filter==='all'||filter==='none'&&!d.areaId||filter==='selected'&&roomView()?.deviceIds.includes(d.id)||filter==='unavailable');if(!matching.length&&!emptyMatch)continue;
    matches+=matching.length;deviceCount++;const group=text('section','','room-device'),head=text('div','','room-device-head');group.dataset.device=d.id;
    const expand=button(roomExpanded.has(d.id)?'⌄':'›',()=>{if(roomExpanded.has(d.id))roomExpanded.delete(d.id);else roomExpanded.add(d.id);roomRenderInventory(all,devices);});expand.dataset.expand=d.id;expand.setAttribute('aria-label','Entitäten von '+d.name+' auf-/zuklappen');expand.setAttribute('aria-expanded',String(roomExpanded.has(d.id)));
    const inspect=button('',()=>{roomContext={kind:'device',id:d.id};roomCancelPreview();$('#room-correction').open=false;roomRenderProperties();roomPanel('properties');},'room-inspect');inspect.dataset.inspectDevice=d.id;
    const deviceIcon=text('span','','room-device-icon');deviceIcon.title='Generisches Gerätesymbol · kein HA-Geräteicon';deviceIcon.setAttribute('role','img');deviceIcon.setAttribute('aria-label',deviceIcon.title);deviceIcon.append(icon('mdi:devices'));const name=text('strong');name.append(deviceIcon,text('span',d.name));
    inspect.append(name,text('small',entities.length+' tatsächliche Entitäten · '+roomAreaLabel(d.areaId)),text('small','Status: '+(roomAvailability[d.availability]||d.availability)+(!roomFresh?' · Veraltet':''),'room-device-status'));
    const checked=Boolean(roomView()?.deviceIds.includes(d.id));const check=roomCheckbox('Gesamtes Gerät auswählen: '+d.name,checked,on=>roomSetDevice(d,on),'deviceCheck',d.id);check.querySelector('input').indeterminate=entities.some(e=>roomSelected(e.key))&&!entities.every(e=>roomSelected(e.key));head.append(expand,inspect,check);group.append(head);
    if(roomExpanded.has(d.id)){group.append(text('p',matching.length+' von '+entities.length+' entsprechen dem Filter. Aufgeklappt werden alle tatsächlichen Geräteentitäten gezeigt.','hint'));for(const e of entities)group.append(roomEntityRow(e,matching.includes(e)));if(!entities.length)group.append(text('p',roomAvailability[d.availability]||'Keine Entitäten','hint'));}root.append(group);
  }
  const deviceIds=new Set(devices.map(d=>d.id));const loose=all.filter(e=>!deviceIds.has(e.deviceId)&&roomMatches(e,null));matches+=loose.length;if(loose.length){root.append(text('h4','Entitäten ohne Gerät / fehlende Referenzen'));for(const e of loose)root.append(roomEntityRow(e));}
  $('#room-result-count').textContent=matches+' passende Entitäten · '+deviceCount+' Geräte. Auswahl bleibt bei Filterwechsel erhalten.';
  if(!root.childElementCount)root.append(text('p',roomInventory?'Keine Treffer. Filter ändern oder alle Bereiche durchsuchen.':'Noch kein lesbarer HA-Bestand. Lokale Ansichten bleiben erhalten.','empty'));root.scrollTop=scroll;
  // Reconcile every observation, restoring keyboard focus by stable control identity.
  if(focused.length)[...root.querySelectorAll('button,input')].find(e=>focused.every(([k,v])=>e.dataset[k]===v))?.focus({preventScroll:true});
}
function roomRenderProperties(){
  const root=$('#room-properties');root.replaceChildren();const entity=roomContext?.kind==='entity'?roomAllEntities().find(e=>e.key===roomContext.id):null,device=roomContext?.kind==='device'?roomAllDevices().find(d=>d.id===roomContext.id):null;const item=entity||device;
  if(!item)root.append(text('p','Wähle ein Gerät oder eine Entität für Details.'));
  else{
    root.append(text('h3',item.name));const dl=text('dl');const pair=(k,v)=>dl.append(text('dt',k),text('dd',String(v??'Nicht vorhanden')));
    pair('Quelle','Home Assistant · '+(roomFresh?'frisch gelesen':'veraltet / nicht bestätigt'));pair('Identität',entity?entity.entityId:device.id);if(entity){pair('Stabile Registry-ID',entity.registryId||'Keine · reine Zustandsentität');pair('Effektiver HA-Bereich',roomAreaLabel(entity.effectiveAreaId));pair('Herkunft',({entity:'Individueller Entitätsbereich',device:'Gerätebereich (geerbt)',none:'Kein Bereich'})[entity.areaSource]);pair('Individueller Bereich',roomAreaLabel(entity.areaId));pair('Gerät',entity.deviceId);pair('Status',roomAvailability[entity.availability]);pair('Tatsächlicher Zustand',entity.state);pair('Einheit',entity.unit);pair('Letzte Zustandsänderung',entity.lastChanged);pair('Letzte Aktualisierung',entity.lastUpdated);pair('Deaktiviert durch',entity.disabledBy);pair('Verborgen durch',entity.hiddenBy);pair('Kategorie',entity.entityCategory);}
    else{pair('HA-Bereich',roomAreaLabel(device.areaId));pair('Hersteller',device.manufacturer);pair('Modell',device.model);pair('Status',roomAvailability[device.availability]);pair('Via-Gerät',device.viaDeviceId);pair('Parent-Gerät',device.parentDeviceId);}
    root.append(dl,text('h4','Anzeige in LUMO · zusätzliche Referenz'));
    const memberships=(roomPlan?.views||[]).filter(v=>entity?v.entityRefs.some(r=>r.key===entity.key):v.deviceIds.includes(device.id));root.append(text('p',memberships.length?memberships.map(v=>v.title+(!v.visible?' (Ansicht verborgen)':'')).join(' · '):'Noch in keiner lokalen Ansicht ausgewählt.'));
    if(roomView()){const checked=entity?roomSelected(entity.key):roomView().deviceIds.includes(device.id);const label=roomCheckbox('In aktueller LUMO-Ansicht anzeigen',checked,on=>entity?roomSetEntity(entity,on):roomSetDevice(device,on),'contextSelection',entity?.key||device.id);label.append(text('span','In „'+roomView().title+'“ auswählen'));root.append(label);}
    root.append(text('p','Lokale Auswahl verändert weder Bereich noch Etage in Home Assistant. Dieselbe Entität kann in mehreren Ansichten erscheinen.','room-reference-note'));
    if(entity){const details=document.createElement('details');details.append(text('summary','Tatsächliche Attribute · keine zusätzlichen Entitäten'));details.append(text('pre',JSON.stringify(entity.attributes,null,2)));root.append(details);}
    else{root.append(text('h4','Zugehörige tatsächliche Entitäten'));for(const e of roomAllEntities().filter(e=>e.deviceId===device.id)){const b=button(e.name+' · '+e.entityId,()=>{roomContext={kind:'entity',id:e.key};roomCancelPreview();roomRenderProperties();},'room-related');root.append(b);}}
  }
  const capable=Boolean(roomFresh&&roomInventory?.canCorrect&&item&&(device||entity.registryId)&&item.availability!=='missing');$('#correction-rights').textContent=roomInventory?.canCorrect?'Administrator geprüft. Eine Vorschau ist 90 Sekunden gültig. Änderungen seit der Vorschau verhindern den Versand.':'Keine bestätigten Administratorrechte für diesen Benutzer. Lokale Auswahl ist davon unabhängig.';
  const picker=$('#correction-area'),old=picker.value;picker.replaceChildren(new Option('Individuellen Bereich entfernen / erben',''));for(const a of roomInventory?.areas||[])picker.add(new Option(a.name+' · '+a.area_id,a.area_id));if([...picker.options].some(o=>o.value===old))picker.value=old;picker.disabled=busy||!capable;$('#correction-preview').disabled=busy||!capable||roomDirty;$('#correction-confirm').disabled=busy||!capable;
  if(roomDirty&&capable)$('#correction-rights').append(' Bitte lokale Ansichten zuerst speichern.');
}
async function roomSave(){
  if(!roomPlan||roomDashboard!==selected?.id||roomRevision!==selected?.revision)return false;
  if(!roomDirty)return true;
  const bad=roomPlan.views.find(v=>!v.title.trim()||v.title.length>80);if(bad){roomPickView(bad.id);$('#room-title').focus();$('#room-title').reportValidity();notice('Jede Ansicht braucht einen Titel mit 1–80 Zeichen.',true);return false;}
  const id=roomDashboard,revision=roomRevision,plan=clone(roomPlan),active=roomActive;
  return writing(async()=>{const value=await api('dashboards/'+id+'/rooms',{revision,plan,confirmedDeletes:[...roomDeleted]});const actual=await readback(value);selected=actual;fill();roomRevision=actual.revision;roomPlan=clone(actual.roomPlan);roomSaved=clone(roomPlan);roomActive=active;roomHistory=[];roomDeleted=[];roomChanged();roomRender(true);await loadImportReport();await listing();notice('Lokale Ansichten gespeichert und zurückgelesen. Home Assistant und native Quelldaten bleiben unverändert.');return true;});
}
async function roomGuard(){
  if(!roomDirty)return true;const answer=await modal({title:'Raumauswahl behalten?',message:'Ungespeicherte Ansichten und Auswahlen bleiben bis zum Speichern nur in diesem Tab. Speichern, ausdrücklich verwerfen oder hier weiterarbeiten?',confirm:'Speichern & weiter',discard:true});if(answer.action==='cancel')return false;if(answer.action==='confirm')return Boolean(await roomSave());roomPlan=clone(roomSaved);roomDeleted=[];roomHistory=[];roomChanged();roomRender(true);return true;
}
$('#room-refresh').onclick=()=>run(()=>roomRefresh());$('#room-new').onclick=()=>run(async()=>{if(!roomPlan)return;const a=await modal({title:'Neue virtuelle Ansicht',message:'Nur in diesem Dashboard. Kein HA-Bereich wird angelegt.',input:'',confirm:'Ansicht anlegen'});if(a.action==='confirm'&&a.value.trim())roomMake(a.value.trim());});
$('#room-view-search').oninput=()=>roomRender(false);for(const id of ['room-search','room-filter','room-scope'])$('#'+id).addEventListener(id==='room-search'?'input':'change',()=>roomRenderInventory(roomAllEntities(),roomAllDevices()));
for(const id of ['room-title','room-icon','room-visible'])$('#'+id).addEventListener(id==='room-title'?'input':'change',()=>roomMutate(()=>{const v=roomView();v.title=$('#room-title').value;v.icon=$('#room-icon').value;v.visible=$('#room-visible').checked;}));
$('#room-unassigned').onclick=()=>{roomPanel('inventory');$('#room-scope').value='none';$('#room-filter').value='all';$('#room-search').value='';roomRenderInventory(roomAllEntities(),roomAllDevices());};
$('#room-select-visible').onclick=()=>roomMutate(()=>roomVisibleEntities().forEach(e=>roomSetEntity(e,true)));$('#room-clear-visible').onclick=()=>roomMutate(()=>roomVisibleEntities().forEach(e=>roomSetEntity(e,false)));
$('#room-undo').onclick=()=>{if(busy||!roomHistory.length)return;const s=roomHistory.pop();roomPlan=s.plan;roomActive=s.active;roomDeleted=s.deleted;roomChanged();roomRender(true);};
$('#room-expand-all').onclick=()=>{for(const d of roomAllDevices())roomExpanded.add(d.id);roomRenderInventory(roomAllEntities(),roomAllDevices());};$('#room-collapse-all').onclick=()=>{roomExpanded.clear();roomRenderInventory(roomAllEntities(),roomAllDevices());};
for(const [id,delta] of [['room-up',-1],['room-down',1]])$('#'+id).onclick=()=>roomMutate(()=>{const i=roomPlan.views.findIndex(v=>v.id===roomActive),j=i+delta;if(j>=0&&j<roomPlan.views.length)[roomPlan.views[i],roomPlan.views[j]]=[roomPlan.views[j],roomPlan.views[i]];});
$('#room-duplicate').onclick=()=>roomMutate(()=>{const v=clone(roomView());v.id=roomId();v.title=v.title.slice(0,72)+' · Kopie';roomPlan.views.splice(roomPlan.views.findIndex(x=>x.id===roomActive)+1,0,v);roomActive=v.id;},true);
$('#room-delete').onclick=()=>run(async()=>{const v=roomView();if(!v)return;const a=await modal({title:'Lokale Ansicht entfernen?',message:'„'+v.title+'“ wird nur aus der LUMO-Raumauswahl entfernt. HA-Bereiche, Geräte, native Inhalte und andere Ansichten bleiben erhalten. Bis zum Speichern kannst Du dies rückgängig machen.',confirm:'Ansicht entfernen'});if(a.action==='confirm')roomMutate(()=>{roomDeleted.push(v.id);roomPlan.views=roomPlan.views.filter(x=>x.id!==v.id);roomActive=roomPlan.views[0]?.id||null;roomContext=null;},true);});
$('#room-save').onclick=()=>run(roomSave);$('#room-back').onclick=()=>run(()=>guard(()=>setStep(1)));$('#room-next').onclick=()=>run(()=>guard(()=>setStep(3)));$$('[data-room-panel]').forEach(b=>b.onclick=()=>roomPanel(b.dataset.roomPanel));
$('#correction-area').onchange=roomCancelPreview;
$('#correction-preview').onclick=()=>run(()=>writing(async()=>{if(!roomContext||roomDirty)return;const e=roomContext.kind==='entity'?roomAllEntities().find(e=>e.key===roomContext.id):null;const r=await api('dashboards/'+roomDashboard+'/area-correction/preview',{revision:roomRevision,kind:roomContext.kind,targetId:e?e.registryId:roomContext.id,areaId:$('#correction-area').value||null});roomPreview=r;$('#correction-details').replaceChildren(text('strong',r.name),text('p',(r.entityId||r.targetId)+' · '+r.permission),text('p','Aktuell: '+roomAreaLabel(r.beforeAreaId)+' → Gewünscht: '+roomAreaLabel(r.afterAreaId)),text('p',r.impact),text('p',r.affectedEntityIds.length+' betroffene Entitäten: '+r.affectedEntityIds.join(', ')),text('p','Gültig für 90 Sekunden. Home Assistant bietet keine atomare Versionsbedingung; Änderungen im kurzen Zeitraum zwischen Prüfung und Versand sind nicht vollständig ausschließbar.'));$('#correction-confirm').hidden=false;}));
$('#correction-confirm').onclick=()=>run(()=>writing(async()=>{if(!roomPreview)return;const p=roomPreview;roomCancelPreview();const result=await api('dashboards/'+roomDashboard+'/area-correction/confirm',{previewId:p.previewId,confirm:true});notice(result.message);await roomRefresh();}));
window.addEventListener('beforeunload',e=>{if(roomDirty){e.preventDefault();e.returnValue='';}});
document.addEventListener('visibilitychange',()=>{if(!document.hidden&&!$('#room-step').hidden&&!busy)void roomRefresh(false);});
roomPanel('inventory');
