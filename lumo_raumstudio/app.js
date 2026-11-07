'use strict';
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
let session=null,selected=null,draft=null,dirty=false,newDirty=false,busy=false,uncertain=false,images=[],previewView=null,initialized=false;
const clone=v=>JSON.parse(JSON.stringify(v));
const escDate=v=>new Date(v).toLocaleString('de-DE',{dateStyle:'medium',timeStyle:'short'});
function notice(message,error=false){const n=$('#notice');n.textContent=message;n.classList.toggle('error',error);n.hidden=!message;if(error&&message)n.scrollIntoView({block:'start',behavior:'instant'});}
function text(tag,value,className=''){const e=document.createElement(tag);e.textContent=value;e.className=className;return e;}
function button(label,fn,className=''){const b=text('button',label,className);b.type='button';const glyph=({'Öffnen':'folder-open-outline','Duplizieren':'content-copy','Umbenennen':'pencil-outline','Löschen':'trash-can-outline','Einstellungen':'cog-outline','Als LUMO-Kopie übernehmen':'import'})[label];if(glyph)b.prepend(icon('mdi:'+glyph));b.disabled=!initialized;b.addEventListener('click',()=>run(fn));return b;}
let icons={},uncertainTarget='',importReport=null,importReportId=null,nativeDirty=false;
function icon(name){
  if(!name)return text('span','','no-icon');
  if(!Object.hasOwn(icons,name)){const missing=text('span','Symbol nicht verfügbar','icon-missing');missing.title=name;return missing;}
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg'),path=document.createElementNS(svg.namespaceURI,'path');
  svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('class','mdi-icon');svg.setAttribute('aria-hidden','true');svg.dataset.icon=name;path.setAttribute('d',icons[name]);svg.append(path);return svg;
}
function studioDecorate(){
 const map={'.steps [data-step="1"]':'view-dashboard-outline','.steps [data-step="2"]':'home-outline','.steps [data-step="3"]':'palette-outline','.steps [data-step="4"]':'layers-outline','.pageheading h1':'view-dashboard-outline','.room-heading h1':'home-outline','.design-heading h1':'palette-outline','.room-left>h2':'layers-outline','.room-right>h2':'cog-outline','.room-source-card>h3':'home-assistant','.room-local-card>h3':'layers-outline','.design-catalog>h2':'layers-outline','.design-settings>h2':'monitor','[data-tab="general"]':'information-outline','[data-tab="background"]':'image-outline','[data-tab="navigation"]':'format-list-bulleted','[data-tab="management"]':'layers-outline','.workspace-heading .eyebrow':'cog-outline','#room-correction summary':'wrench-outline','label[for=room-view-search]':'magnify','label:has(#room-visible)':'eye-outline','.room-local-card>.hint':'information-outline','.room-live>span':'circle-small','#create':'plus','#load-ha':'refresh','#room-new':'plus','#room-save':'content-save-outline','#design-save':'content-save-outline','#room-back':'arrow-left','#design-back':'arrow-left','#room-next':'arrow-right','#design-next':'arrow-right','#continue':'arrow-right','#room-up':'arrow-up','#room-down':'arrow-down','#room-undo':'undo','#design-discard':'undo'};
 for(const [selector,name] of Object.entries(map)){const e=$(selector);if(!e)continue;for(const n of [...e.childNodes])if(n.nodeType===Node.TEXT_NODE)n.textContent=n.textContent.replace(/[＋↑↓←→↶⚒]/g,'').trim();e.prepend(icon('mdi:'+name));}
 for(const [selector,name] of [['.new .mark','plus-box-outline'],['.saved .mark','folder-open-outline'],['.ha .mark','home-assistant']])$(selector).replaceChildren(icon('mdi:'+name));
 for(const [id,name,label] of [['studio-help','help-circle-outline','Hilfe zu LUMO Raumstudio'],['studio-settings','cog-outline','Dashboard-Einstellungen']]){const b=button('',()=>id==='studio-help'?$('#help-dialog').showModal():guard(()=>{if(!selected)return;setStep(1);showTab('general');$('#workspace').scrollIntoView({block:'nearest'});$('#edit-name').focus();}));b.id=id;b.setAttribute('aria-label',label);b.title=label;b.append(icon('mdi:'+name));$('.brandbar').append(b);}
 const search=$('#room-view-search'),wrap=text('div','','room-search-box');search.before(wrap);wrap.append(icon('mdi:magnify'),search);$('.design-settings>.hint').prepend(icon('mdi:lightbulb-outline'));
 $('#help-close').onclick=()=>$('#help-dialog').close();$('#help-dialog').addEventListener('close',()=>$('#studio-help').focus());
}
function connectionStatus(message,verified=false){$('#connection').replaceChildren(...(verified?[icon('mdi:check-circle-outline')]:[]),text('span',message));$('#connection').dataset.verified=String(verified);}
function iconPickerPreview(id){const input=$('#'+id),summary=$('#'+id+'-picker summary');if(summary)summary.replaceChildren(icon(input.value&&Object.hasOwn(icons,input.value)?input.value:'mdi:shape-outline'),text('span','Symbol auswählen'));}
function iconPickers(){
  const popular={'mdi:home':'Zuhause','mdi:view-dashboard':'Dashboard','mdi:sofa':'Wohnen','mdi:leaf':'Natur','mdi:lightbulb':'Licht','mdi:weather-sunny':'Sonne','mdi:bed':'Schlafen','mdi:garage':'Garage'};
  for(const id of ['new-icon','edit-icon']){
    const input=$('#'+id),details=document.createElement('details');details.id=id+'-picker';details.className='icon-picker';details.append(text('summary','Symbol auswählen'));
    const search=document.createElement('input');search.id=id+'-search';search.type='search';search.placeholder='Symbole suchen (z. B. home, sofa)';search.setAttribute('aria-label','Symbole suchen');const choices=text('div','','icon-options');choices.id=id+'-options';const hint=text('p','','hint');
    function render(){const q=search.value.trim().toLowerCase(),matches=q?Object.keys(icons).filter(n=>(n+' '+(popular[n]||'')).toLowerCase().includes(q)):Object.keys(popular);choices.replaceChildren();
      for(const name of ['',...matches.slice(0,60)]){const b=button('',()=>{input.value=name;input.dispatchEvent(new Event('input',{bubbles:true}));details.open=false;input.focus();});b.setAttribute('aria-label',name||'Kein Icon');b.append(icon(name),text('span',popular[name]||name.replace('mdi:','')||'Kein Icon'));choices.append(b);}
      hint.textContent=q?matches.length+' Treffer · maximal 60 angezeigt. Suche bei Bedarf genauer.':'Häufige Symbole · Suche im lokalen MDI-Katalog 7.4.47.';
    }
    search.addEventListener('input',e=>{e.stopPropagation();render();});search.addEventListener('change',e=>e.stopPropagation());search.addEventListener('keydown',e=>{if(e.key==='Enter')e.preventDefault();});
    input.addEventListener('input',()=>{iconPickerPreview(id);input.setCustomValidity(input.value&&!Object.hasOwn(icons,input.value)?'Bitte ein Symbol aus dem lokalen MDI-Katalog wählen.':'');});details.append(search,choices,hint);input.after(details);render();iconPickerPreview(id);
  }
}
async function api(path,body){
  if(body!==undefined&&uncertain)throw Error('Der letzte Schreibvorgang ist unklar. '+uncertainTarget+' Bitte den gespeicherten Stand in einem neuen Tab prüfen. Keine automatische Wiederholung.');
  const c=new AbortController(),timer=setTimeout(()=>c.abort(),60000);let response;
  try{response=await fetch('api/'+path,{method:body===undefined?'GET':'POST',headers:{'X-LUMO-Read':'1',...(body===undefined?{}:{'Content-Type':'application/json','X-LUMO-Action':'1','X-LUMO-CSRF':session?.csrf||''})},body:body===undefined?undefined:JSON.stringify(body),signal:c.signal,cache:'no-store'});}
  catch(e){if(body!==undefined)uncertain=true;throw Error(body===undefined?'Verbindung unterbrochen. Deine Eingaben bleiben erhalten.':'Speicherung nicht bestätigt. Eingaben behalten und den gespeicherten Stand in einem neuen Tab prüfen. Nicht ungeprüft erneut ausführen.');}
  finally{clearTimeout(timer);}
  let result;try{result=await response.json();}catch(e){if(body!==undefined)uncertain=true;throw Error('Die Antwort konnte nicht sicher gelesen werden. Bitte den gespeicherten Stand prüfen.');}
  if(!response.ok){if(body!==undefined&&response.status>=500)uncertain=true;throw Error(result.error||'Die Anfrage wurde abgelehnt.');}
  return result;
}
async function run(fn){if(busy)return;try{await fn();}catch(e){notice(e.message,true);}}
async function writing(fn){
  if(busy)return;busy=true;const controls=$$('button,input,select,textarea'),states=controls.map(e=>e.disabled);controls.forEach(e=>e.disabled=true);
  try{return await fn();}finally{controls.forEach((e,i)=>e.disabled=states[i]);busy=false;if(draft){$('#start-view').disabled=!draft.views.length;preview();}if(!$('#room-step').hidden)roomRender(false);if(!$('#design-step').hidden)designLock();}
}
async function readback(value){
  try{const actual=await api('dashboards/'+value.id);if(JSON.stringify(actual)!==JSON.stringify(value))throw Error();return actual;}
  catch(e){uncertain=true;throw Error('Speicherung ist nicht eindeutig bestätigt: Der zurückgelesene Stand stimmt nicht überein oder ist nicht erreichbar. Eingaben bleiben erhalten; bitte in einem neuen Tab prüfen.');}
}
async function confirmCollection(path,check,target){
  try{const rows=await api(path);if(!Array.isArray(rows)||!check(rows))throw Error();return rows;}
  catch(e){uncertain=true;uncertainTarget=target;throw Error('Der Schreibvorgang ist unklar: '+target+' Bestätigendes Lesen fehlgeschlagen. Eingaben und Ziel bleiben erhalten; bitte den gespeicherten Stand in einem neuen Tab prüfen. Keine Wiederholung in diesem Tab.');}
}
function dirtyState(){
  $('#dirty-label').textContent=dirty?'Ungespeicherte Änderungen':'Alle Änderungen gespeichert';
  $('#save-state').textContent=dirty?'Änderungen nur in diesem Tab · noch nicht gespeichert':selected?'Gespeichert · '+escDate(selected.updatedAt):'';
}
function currentForm(){
  if(!draft)return;
  draft.name=$('#edit-name').value;draft.description=$('#edit-description').value;draft.icon=$('#edit-icon').value;
  const bg=draft.settings.background;Object.assign(bg,{color:$('#bg-color').value,imageId:$('#image-choice').value||null,position:$('#bg-position').value,mode:$('#bg-mode').value,scale:Number($('#bg-scale').value),opacity:Number($('#bg-opacity').value),attachment:$('#bg-attachment').value});
  Object.assign(draft.settings.navigation,{showIconAndTitle:$('#nav-labels').checked,startView:$('#start-view').value||null,showInSidebar:$('#nav-sidebar').checked,requireAdmin:$('#nav-admin').checked});
  dirty=nativeDirty||JSON.stringify(draft)!==JSON.stringify(selected);dirtyState();preview();
}
function imageChoices(){
  const choice=$('#image-choice'),old=draft?.settings.background.imageId||'';choice.replaceChildren(new Option('Kein Bild',''));
  images.forEach(m=>choice.add(new Option(m.name+' · '+m.width+' × '+m.height,m.id)));choice.value=old;
}
function fill(){
  if(!selected)return;draft=clone(selected);dirty=false;nativeDirty=false;previewView=draft.settings.navigation.startView;
  $('#workspace').hidden=false;if($('#studio-settings'))$('#studio-settings').disabled=busy;$('#selected-title').textContent=selected.name;
  $('#edit-name').value=draft.name;$('#edit-description').value=draft.description;$('#edit-icon').value=draft.icon;$('#edit-icon').setCustomValidity('');
  const bg=draft.settings.background;$('#bg-color').value=bg.color;$('#bg-position').value=bg.position;$('#bg-mode').value=bg.mode;$('#bg-scale').value=bg.scale;$('#bg-opacity').value=bg.opacity;$('#bg-attachment').value=bg.attachment;
  const n=draft.settings.navigation;$('#nav-labels').checked=n.showIconAndTitle;$('#nav-sidebar').checked=n.showInSidebar;$('#nav-admin').checked=n.requireAdmin;
  $('#start-view').replaceChildren(new Option(draft.views.length?'Erste Ansicht':'Noch keine Ansichten',''));
  draft.views.forEach(v=>$('#start-view').add(new Option(v.title,v.id)));$('#start-view').value=n.startView||'';$('#start-view').disabled=busy||!draft.views.length;
  $('#start-hint').textContent=draft.views.length?'Die Startansicht wird in der Vorschau zuerst gezeigt. Die native Zuordnung wird für eine spätere Ausgabe vorbereitet.':'Sobald echte Ansichten vorhanden sind, kannst Du hier die Startansicht wählen.';
  const meta=$('#metadata');meta.replaceChildren();for(const [k,v] of [['Interne ID',draft.id],['Erstellt',escDate(draft.createdAt)],['Geändert',escDate(draft.updatedAt)],['Status',draft.status],['Revision',draft.revision],['Datenformat',draft.schemaVersion]])meta.append(text('dt',k),text('dd',String(v)));
  [...meta.querySelectorAll('dt')].forEach((e,i)=>e.prepend(icon('mdi:'+['information-outline','calendar','pencil-outline','layers-outline','history','code-tags'][i])));
  $('#metadata-summary').replaceChildren(...[...meta.children].map(e=>e.cloneNode(true)));iconPickerPreview('edit-icon');for(const row of $$('.draft-row')){const active=row.dataset.dashboardId===selected?.id;row.dataset.active=String(active);row.querySelector('.badge').replaceChildren(...(active?[icon('mdi:check-circle-outline')]:[]),text('span','Entwurf'));}
  imageChoices();renderImport();dirtyState();preview();
}
function preview(){
  if($('#studio-settings'))$('#studio-settings').disabled=busy||!selected;
  if(!draft)return;const bg=draft.settings.background,n=draft.settings.navigation,all=draft.roomPlan?draft.roomPlan.views:draft.views,visible=all.filter(v=>v.visible!==false);let view=visible.find(v=>v.id===previewView)||visible.find(v=>v.id===n.startView)||visible[0];
  const nativeView=view?.nativeViewId?draft.views.find(v=>v.id===view.nativeViewId):view;
  const native=nativeView&&!draft.nativeImport?draft.native?.views[nativeView.nativeIndex]:null,override=native?.background;
  $('#preview').style.backgroundColor=override||bg.color;$('#preview').dataset.photo=String(Boolean(bg.imageId&&!override));
  const layer=$('#preview-image');layer.style.backgroundImage=bg.imageId&&!override?`url("api/images/${bg.imageId}")`:'none';layer.style.backgroundPosition=bg.position;layer.style.backgroundSize=bg.mode==='scale'?bg.scale+'% auto':bg.mode;layer.style.opacity=bg.opacity/100;
  // Fixed output is documented; this bounded preview is not the page scroll surface.
  $('#preview-title').textContent=draft.name||'Dein Dashboard';$('#preview-icon').replaceChildren(icon(draft.icon));$('#preview-icon').title=draft.icon;$('#preview-description').textContent=draft.description;
  $('#preview-views').replaceChildren();$('#preview-views').hidden=visible.length<2;(visible.length>1?visible:[]).forEach(v=>{const b=button('',()=>{previewView=v.id;preview();});b.append(icon(v.icon));if(n.showIconAndTitle||!v.icon)b.append(text('span',v.title));b.title=v.title;b.setAttribute('aria-label',v.title);if(v===view)b.setAttribute('aria-current','page');$('#preview-views').append(b);});
  $('#preview-empty').textContent=visible.length?'Ansicht „'+view.title+'“ · '+visible.length+' vorhandene Ansicht'+(visible.length===1?'':'en')+'. Karten bleiben als Daten erhalten und werden hier nicht aktiv ausgeführt.':all.length?'Deine gespeicherten Raumansichten sind ausgeblendet. Aktiviere unter „Raum“ die Option „In diesem Dashboard anzeigen“.':'Deine leere Leinwand. Noch keine Ansichten – und Platz für Deine Ideen.';
  if(view){$('#preview-empty').prepend(icon(view.icon));}
  $('#preview-note').textContent=(override?'Diese Ansicht verwendet ihren vorhandenen eigenen Hintergrund. ':'Globale Gestaltung für Ansichten ohne eigenen Hintergrund. ')+(bg.attachment==='fixed'?'In der späteren nativen Ausgabe am Bildschirm fixiert. ':'')+'Keine Live-Werte oder aktiven HA-Karten.';
  $('#output-preferences').textContent='Nur gespeicherte Ausgabeabsicht: '+(n.showInSidebar?'in der HA-Seitenleiste':'nicht in der HA-Seitenleiste')+' · '+(n.requireAdmin?'nur Administratoren':'alle in HA berechtigten Benutzer')+'. Keine Änderung an HA.';
  if(draft.nativeImport){if(!all.length)$('#preview-empty').textContent='Keine konkreten Ansichten in der importierten Konfiguration. Strategy- und sonstige Daten bleiben geschützt erhalten; LUMO erzeugt daraus keine Ansichten.';$('#preview-note').textContent='Nur lokale LUMO-Vorschau – keine Wiedergabe des HA-Originals. Importierte Hintergründe, Karten und Templates werden nicht geladen. Gestaltung und Navigation ändern den JSON-Export nicht.';$('#start-hint').textContent='Nur lokale Vorschau. Die Reihenfolge der importierten Ansichten bleibt im JSON-Export erhalten.';}
  importLocks();
  $('#bg-scale').disabled=busy||nativeDirty||bg.mode!=='scale';
}
async function listing(){
  const rows=await api('dashboards'),list=$('#saved-list');list.replaceChildren();
  if(!rows.length){list.append(text('p','Noch keine gespeicherten Dashboards. Dein erster Entwurf beginnt links.','empty'));return;}
  rows.forEach(d=>{const row=text('article','','draft-row'),head=text('div','','draft-title');row.dataset.dashboardId=d.id;head.append(icon(d.icon),text('strong',d.name),text('span','Entwurf','badge'));row.append(head,text('p',(d.roomPlan?d.roomPlan.views.length+' Raumansichten · '+d.views.length+' native Ansichten':d.views.length+' Ansichten')+' · geändert '+escDate(d.updatedAt),'draft-meta'));const acts=text('div','','actions');
    const open=button('Öffnen',()=>guard(()=>openDraft(d.id)));open.className='draft-open';row.append(open);acts.append(button('Umbenennen',()=>guardAction(d,rename)),button('Duplizieren',()=>guardAction(d,duplicate)),button('Einstellungen',()=>guard(()=>openDraft(d.id,true))),button('Löschen',()=>guardAction(d,remove),'danger'));const more=document.createElement('details');more.className='draft-actions';const trigger=text('summary');trigger.setAttribute('aria-label','Aktionen für '+d.name);trigger.append(icon('mdi:dots-vertical'));more.append(trigger,acts);row.append(more);if(d.id===selected?.id){row.dataset.active='true';head.querySelector('.badge').prepend(icon('mdi:check-circle-outline'));}list.append(row);});
}
async function openDraft(id,scroll=true){return writing(async()=>{selected=await api('dashboards/'+id);sessionStorage.setItem('lumo-selected',id);fill();await loadImportReport();setStep(1);if(scroll)$('#workspace').scrollIntoView({behavior:'instant',block:'start'});});}
function validateSettings(){
  const invalid=[...$('#settings-form').elements].find(e=>e.willValidate&&!e.validity.valid);
  if(!invalid)return true;
  const pane=invalid.closest('[data-pane]');if(pane)showTab(pane.dataset.pane);
  const details=invalid.closest('details');if(details)details.open=true;
  invalid.focus();invalid.reportValidity();return false;
}
async function save(){
  if(nativeDirty)return saveNative();
  if(!selected||!dirty)return true;if(!validateSettings())return false;
  return writing(async()=>{currentForm();const value=await api('dashboards/'+selected.id+'/save',{revision:selected.revision,patch:{name:draft.name,icon:draft.icon,description:draft.description,settings:draft.settings}});selected=await readback(value);fill();await loadImportReport();await listing();notice('Dein Entwurf wurde gespeichert und zurückgelesen.');return true;});
}
async function create(){
  if(!$('#create-form').reportValidity())return false;
  return writing(async()=>{const value=await api('dashboards',{name:$('#new-name').value,icon:$('#new-icon').value});selected=await readback(value);sessionStorage.setItem('lumo-selected',selected.id);$('#create-form').reset();newDirty=false;fill();await loadImportReport();await listing();setStep(2);notice('Dein Dashboard wurde gespeichert. Es hat noch keine Ansichten.');return true;});
}
let dialogResolve=null;
function modal({title,message,input=null,confirm='Bestätigen',discard=false}){
  $('#dialog-title').textContent=title;$('#dialog-text').textContent=message;$('#dialog-input').hidden=input===null;$('#dialog-label').hidden=input===null;$('#dialog-input').required=input!==null;$('#dialog-input').value=input||'';$('#dialog-confirm').textContent=confirm;$('#dialog-discard').hidden=!discard;$('#dialog-error').textContent='';$('#dialog').showModal();if(input!==null)$('#dialog-input').focus();else $('#dialog-cancel').focus();
  return new Promise(resolve=>dialogResolve=resolve);
}
function closeModal(action){if(!dialogResolve)return;const resolve=dialogResolve;dialogResolve=null;$('#dialog').close();resolve({action,value:$('#dialog-input').value});}
$('#dialog-form').addEventListener('submit',e=>{e.preventDefault();closeModal('confirm');});$('#dialog-cancel').onclick=()=>closeModal('cancel');$('#dialog-discard').onclick=()=>closeModal('discard');$('#dialog').addEventListener('cancel',e=>{e.preventDefault();closeModal('cancel');});
async function guard(next){
  if(busy)return;if(!await designGuard())return;if(!await roomGuard())return;let saved=null;if(dirty||newDirty){const answer=await modal({title:'Deine Änderungen behalten?',message:'Hier gibt es ungespeicherte Eingaben. Speichere sie vor dem Wechsel oder verwerfe sie ausdrücklich.',confirm:'Speichern & weiter',discard:true});
    if(answer.action==='cancel')return;
    if(answer.action==='confirm'){if(dirty){const before={id:selected.id,revision:selected.revision};if(!await save())return;saved={before,after:clone(selected)};}if(newDirty&&!await create())return;}
    else {if(selected)fill();$('#create-form').reset();newDirty=false;}
  }await next(saved);
}
function guardAction(value,action){
  // Freeze identity and CAS before any guard can save/create another draft.
  const target=clone(value);
  return guard(saved=>{const own=saved?.before.id===target.id&&saved.before.revision===target.revision;setStep(1);return action(own?saved.after:target);});
}
async function rename(d){
  let value=d.name,error='';
  while(true){
    const pending=modal({title:'Dashboard umbenennen',message:'Die interne ID, Ansichten und Erstellzeit bleiben unverändert.',input:value,confirm:'Name speichern'});$('#dialog-error').textContent=error;
    const answer=await pending;if(answer.action!=='confirm')return;value=answer.value;
    try{await writing(async()=>{const changed=await readback(await api('dashboards/'+d.id+'/save',{revision:d.revision,patch:{name:value}}));if(selected?.id===d.id){selected=changed;fill();await loadImportReport();}await listing();notice('Name gespeichert.');});return;}
    catch(e){error=e.message;}
  }
}
async function duplicate(d){await writing(async()=>{const value=await readback(await api('dashboards/'+d.id+'/duplicate',{revision:d.revision}));selected=value;sessionStorage.setItem('lumo-selected',value.id);fill();await loadImportReport();await listing();notice('Unabhängige lokale Kopie gespeichert.');});}
async function remove(d){const answer=await modal({title:'Lokalen Entwurf löschen?',message:'„'+d.name+'“ wird aus Deinem LUMO-Speicher entfernt. Das HA-Original und Deine Bildbibliothek bleiben unverändert. Dieser Schritt kann nicht rückgängig gemacht werden.',confirm:'Entwurf löschen'});if(answer.action!=='confirm')return;
  await writing(async()=>{await api('dashboards/'+d.id+'/delete',{revision:d.revision,confirm:true});await confirmCollection('dashboards',rows=>!rows.some(r=>r.id===d.id),'Löschung von „'+d.name+'“ (ID '+d.id+').');if(selected?.id===d.id){selected=draft=null;dirty=false;$('#workspace').hidden=true;sessionStorage.removeItem('lumo-selected');}await listing();notice('Nur der lokale Entwurf wurde gelöscht.');});
}
function setStep(step){const leavingFull=step!==3&&$('#design-step').classList.contains('preview-fullscreen');if(leavingFull)designFull(true);roomStop();designStop();$$('[data-step]').forEach(e=>{if(Number(e.dataset.step)===step)e.setAttribute('aria-current','step');else e.removeAttribute('aria-current');});$('#dashboard-step').hidden=step!==1;$('#room-step').hidden=step!==2;$('#design-step').hidden=step!==3;$('#handoff-step').hidden=step!==4;if(step===2)void roomEnter();if(step===3)void designEnter();if(step===4){$('#handoff-eyebrow').textContent='SCHRITT 4 · ÜBERGABE';$('#handoff-title').textContent='Dein Raumentwurf';$('#handoff-selection').textContent=selected?'Ausgewählt und gespeichert: '+selected.name+' · '+(selected.roomPlan?.views.length??selected.views.length)+' Ansichten':'Noch kein Dashboard ausgewählt. Bitte erst in Schritt 1 beginnen.';}if(leavingFull)$('[data-step="'+step+'"]').focus();window.scrollTo(0,0);}
$$('[data-step]').forEach(b=>b.onclick=()=>run(()=>guard(()=>setStep(Number(b.dataset.step)))));
$('#back-dashboard').onclick=()=>run(()=>guard(()=>setStep(1)));$('#continue').onclick=()=>run(()=>guard(()=>setStep(2)));
function showTab(tab){$$('[data-tab]').forEach(b=>{if(b.dataset.tab===tab)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});$$('[data-pane]').forEach(p=>p.hidden=p.dataset.pane!==tab);}
$$('[data-tab]').forEach(b=>b.onclick=()=>showTab(b.dataset.tab));
$('#create-form').addEventListener('reset',()=>$('#new-icon').setCustomValidity(''));
$('#create-form').addEventListener('input',()=>newDirty=Boolean($('#new-name').value||$('#new-icon').value));
$('#create-form').addEventListener('submit',e=>{e.preventDefault();run(async()=>{
  if(dirty){const answer=await modal({title:'Bestehende Änderungen behalten?',message:'Der ausgewählte Entwurf enthält ungespeicherte Änderungen. Speichere oder verwerfe nur diese Änderungen, bevor Dein neues Dashboard erstellt wird.',confirm:'Speichern & erstellen',discard:true});if(answer.action==='cancel')return;if(answer.action==='confirm'&&!await save())return;if(answer.action==='discard')fill();}
  await create();
});});
$('#settings-form').addEventListener('input',e=>{if(e.target.id==='image-file')return;currentForm();});$('#settings-form').addEventListener('change',e=>{if(e.target.id==='image-file')return;if(e.target.id==='start-view')previewView=e.target.value;currentForm();});
$('#settings-form').addEventListener('submit',e=>{e.preventDefault();run(save);});
$('#remove-image').onclick=()=>{$('#image-choice').value='';currentForm();};
$('#duplicate-selected').onclick=()=>run(()=>guardAction(selected,duplicate));$('#delete-selected').onclick=()=>run(()=>guardAction(selected,remove));
$('#image-file').addEventListener('change',()=>run(async()=>{const file=$('#image-file').files[0];if(!file)return;if(file.size>8*1024*1024)throw Error('Bitte ein Bild bis 8 MiB wählen.');
  await writing(async()=>{const data=await new Promise((res,rej)=>{const reader=new FileReader();reader.onload=()=>res(reader.result.split(',')[1]);reader.onerror=()=>rej(Error('Die Bilddatei konnte nicht gelesen werden.'));reader.readAsDataURL(file);});const uploaded=await api('images',{name:file.name,data});images=await confirmCollection('images',rows=>rows.some(i=>JSON.stringify(i)===JSON.stringify(uploaded)),'Bildupload „'+uploaded.name+'“ (ID '+uploaded.id+').');imageChoices();$('#image-choice').value=uploaded.id;currentForm();$('#image-file').value='';notice('Bild in Deiner Bibliothek gespeichert. Bitte die Hintergrundänderung noch speichern.');});
}));
$('#load-ha').onclick=()=>run(async()=>{await writing(async()=>{let result;try{result=await api('ha/dashboards');}catch(e){connectionStatus('HA · nicht verbunden / Rechte nicht bestätigt');throw e;}connectionStatus(result.status,true);const list=$('#ha-list');list.replaceChildren();if(!result.dashboards.length)list.append(text('p','Keine lesbaren HA-Konfigurationen gefunden. Auch Strategy-Konfigurationen können als geschützte Daten übernommen werden.','empty'));
 result.dashboards.forEach(d=>{const row=text('article','','ha-item'),info=text('div');info.append(text('strong',d.title),text('p',(d.viewCount===null?'Ansichten nicht bestimmbar':d.viewCount+' Ansichten')+' · '+d.mode+' · '+(d.supported?'vollständig übernehmbar · Bearbeitbarkeit getrennt':'nicht lesbar oder Datengrenze überschritten')));if(d.issues.length){const ul=text('ul');d.issues.forEach(i=>ul.append(text('li',i.path+': '+i.message)));info.append(ul);}info.querySelector('p').prepend(icon('mdi:information-outline'));const b=button('Als LUMO-Kopie übernehmen',()=>guard(async()=>{await writing(async()=>{const value=await api('ha/import',{path:d.path,name:d.title.slice(0,80)});selected=await readback(value);sessionStorage.setItem('lumo-selected',selected.id);fill();await loadImportReport();await listing();setStep(1);$('#workspace').scrollIntoView();notice('Vollständige HA-Konfiguration unabhängig kopiert. Geschützte Daten bleiben erhalten; das HA-Original ist unverändert.');});}));b.disabled=!d.supported;row.append(info,b);list.append(row);});notice('Home Assistant wurde nur gelesen. Auch unbekannte Inhalte bleiben vollständig erhalten. Details und Bearbeitbarkeit stehen nach der Übernahme im Importbericht.');});});
// Imported JSON is only read as data. Never merge it into JS objects or DOM/CSS.
function importReady(){return Boolean(selected?.nativeImport&&importReportId===selected.id&&importReport?.revision===selected.revision);}
function nativeElement(){return importReady()?importReport.editableElements.find(e=>JSON.stringify(e.path)===$('#native-element').value):null;}
function nativeField(){return nativeElement()?.fields.find(f=>f.kind===$('#native-field').value);}
function importLocks(){
  if(!draft)return;
  $$('#settings-form input,#settings-form select,#settings-form textarea,#edit-icon-options button').forEach(e=>e.disabled=busy||nativeDirty);
  $('#start-view').disabled=busy||nativeDirty||!draft.views.length;
  for(const id of ['image-file','remove-image'])$('#'+id).disabled=busy||nativeDirty;
  const ready=importReady(),blocked=busy||!ready||(dirty&&!nativeDirty);
  for(const id of ['native-element','native-field'])$('#'+id).disabled=blocked||nativeDirty;
  $('#native-value').disabled=blocked;$('#native-save').disabled=blocked||!nativeDirty;
  $('#native-cancel').disabled=busy||!nativeDirty;$('#native-export').disabled=busy||!selected.nativeImport;
}
function nativeFields(){
  $('#native-field').replaceChildren();for(const f of nativeElement()?.fields||[])$('#native-field').add(new Option(f.label,f.kind));nativeValue();
}
function nativeValue(){
  const f=nativeField();$('#native-value').value=f?.value||'';$('#native-path').textContent=f?'Nur dieses Feld: '+JSON.stringify(f.path):'';
}
function renderImport(){
  $('#import-detail').hidden=!selected?.nativeImport;
  if(!selected?.nativeImport)return;
  const ready=importReady();$('#native-form').hidden=!ready||!importReport.editableElements.length;$('#native-empty').hidden=!ready||Boolean(importReport.editableElements.length);
  $('#import-summary').textContent=ready?importReport.summary:'Importbericht wird geladen … Die serverseitige Kopie bleibt unverändert.';
  $('#import-counts').textContent=ready?importReport.editableCount+' Elemente mit gezielt bearbeitbaren Feldern · '+importReport.protected.count+' geschützte Datenfelder · '+importReport.editCount+' ausdrücklich gespeicherte Feldänderungen.':'';
  $('#import-resources').textContent=ready?importReport.resources.message:'';
  $('#import-technical-text').textContent=ready?JSON.stringify({sourceHash:importReport.sourceHash,exportHash:importReport.exportHash,resources:importReport.resources,dependencies:importReport.dependencies,protected:importReport.protected,editableTruncated:importReport.editableTruncated},null,2):'';
  const picker=$('#native-element'),old=picker.value;picker.replaceChildren();
  if(ready){for(const e of importReport.editableElements)picker.add(new Option(e.label+' · '+e.type+' · '+JSON.stringify(e.path),JSON.stringify(e.path)));if([...picker.options].some(o=>o.value===old))picker.value=old;}
  nativeFields();importLocks();
}
async function loadImportReport(){
  if(!selected?.nativeImport){importReport=null;importReportId=null;return;}
  const id=selected.id,revision=selected.revision;
  try{const value=await api('dashboards/'+id+'/report');if(value.revision!==revision)throw Error('Der Importbericht gehört zu einem neueren Stand. Bitte bewusst neu öffnen; Deine Kopie wurde nicht überschrieben.');importReport=value;importReportId=id;renderImport();}
  catch(e){importReport=null;importReportId=null;renderImport();$('#import-summary').textContent='Bericht nicht verfügbar: '+e.message+' Der gespeicherte Stand bleibt als JSON herunterladbar.';}
}
async function saveNative(){
  const field=nativeField();if(!nativeDirty)return true;
  if(!field||!importReady())throw Error('Bitte den gespeicherten Importbericht neu öffnen.');
  if(!$('#native-form').checkValidity()){$('#native-editor').open=true;$('#native-value').focus();$('#native-form').reportValidity();return false;}
  const id=selected.id,revision=selected.revision,edit={path:clone(field.path),value:$('#native-value').value};
  return writing(async()=>{const value=await api('dashboards/'+id+'/native-edit',{revision,edits:[edit]});selected=await readback(value);fill();await loadImportReport();await listing();notice('Gezielte Änderung gespeichert und zurückgelesen. Nur das gewählte native Feld wurde geändert.');return true;});
}
$('#native-element').onchange=nativeFields;$('#native-field').onchange=nativeValue;
$('#native-value').oninput=()=>{nativeDirty=$('#native-value').value!==nativeField()?.value;dirty=nativeDirty||JSON.stringify(draft)!==JSON.stringify(selected);dirtyState();preview();};
$('#native-form').onsubmit=e=>{e.preventDefault();run(saveNative);};
$('#native-cancel').onclick=()=>{nativeDirty=false;dirty=false;nativeValue();dirtyState();preview();};
$('#native-export').onclick=()=>run(()=>writing(async()=>{
  // Download raw server bytes: JSON.parse/stringify would round large integers.
  const c=new AbortController(),timer=setTimeout(()=>c.abort(),60000);
  try{const response=await fetch('api/dashboards/'+selected.id+'/export',{headers:{'X-LUMO-Read':'1'},cache:'no-store',signal:c.signal});
    if(!response.ok){const error=await response.json();throw Error(error.error||'Export nicht verfügbar.');}
    const blob=await response.blob(),url=URL.createObjectURL(blob),a=document.createElement('a');
    a.href=url;a.download=response.headers.get('Content-Disposition')?.match(/filename="([a-z0-9.-]+)"/)?.[1]||'lumo-kopie.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
    notice('Gespeicherte HA-Kopie als JSON heruntergeladen. Ungespeicherte Eingaben sind nicht enthalten. Externe Dateien und Themes sind nicht mitkopiert.');
  }finally{clearTimeout(timer);}
}));
window.addEventListener('beforeunload',e=>{if(dirty||newDirty||busy||uncertain){e.preventDefault();e.returnValue='';}});
async function start(){
  $$('button,input,select,textarea').forEach(e=>e.disabled=true);
  try{const response=await fetch('mdi.json',{cache:'no-store'});if(!response.ok)throw Error();icons=await response.json();iconPickers();studioDecorate();}
  catch(e){notice('Der lokale Symbolkatalog konnte nicht geladen werden. Bitte die App erneut öffnen.',true);return;}
  try{session=await api('session');$('#version').textContent='Version '+session.version;if(!session.ready){notice(session.message+'\n\nDeine HA-Benutzer-ID: '+session.userId);$('#create').disabled=true;$('#load-ha').disabled=true;$('#saved-list').replaceChildren(text('p','Nach der Freigabe erscheinen hier Deine eigenen Entwürfe.','empty'));return;}await listing();images=await api('images');const id=sessionStorage.getItem('lumo-selected');if(id){try{await openDraft(id,false);}catch(e){sessionStorage.removeItem('lumo-selected');notice('Der zuletzt gewählte Entwurf ist für diesen Benutzer nicht verfügbar.',true);}}}
  catch(e){notice(e.message,true);session=null;}
  finally{initialized=true;$$('button,input,select,textarea').forEach(e=>e.disabled=!session?.ready);if($('#studio-settings'))$('#studio-settings').disabled=!session?.ready||!selected;if(session?.ready){$('#start-view').disabled=!draft?.views.length;preview();}}
}
start();
