"""Native theme sidecar only; never passed into compile_native or published to HA."""
from design import defaults,resolved,validate,CATALOG
from native import background_css
PIN='a67b691a451e0b3fc469679b07158f963a61842c'
CAPABILITIES=[
 {'feature':'Kartenfarbe, Text, Rahmen, Rundung, Schatten','status':'pinned-native','detail':'Original ha-card · berechnete Eigenschaften geprüft. HA-interne Variablen, keine dauerhafte API-Garantie.'},
 {'feature':'Material: flach / weich / Schicht','status':'pinned-native','detail':'Undurchsichtige ha-card-Fläche mit Schatten oder Verlauf. Kein behauptetes Glas/Blur.'},
 {'feature':'Kartenüberschrift: Systemschrift und Größe','status':'pinned-native','detail':'ha-card-header-font-family / -font-size. Schrift-Fallback ist geräteabhängig. Karten können eigene Typografie besitzen.'},
 {'feature':'Globaler Hintergrund','status':'pinned-native','detail':'lovelace-background als Theme-Fallback. Bestehende Ansichts- und Dashboard-Hintergründe haben Vorrang; lokale Bilder werden als PNG eingebettet.'},
 {'feature':'Primär-, Sekundär- und Akzentpalette','status':'theme-variable','detail':'Themevariablen enthalten; Nutzung hängt vom konkreten HA-Control ab. Nicht alle Controls als visuell identisch geprüft.'},
 {'feature':'Navigation, Iconstil, Statusflächen, Schriftgewicht / Inhaltsdichte','status':'preview-only','detail':'LUMO-Funktionsvorschau. Keine identische native Navigation oder Karteninnenstruktur versprochen.'},
 {'feature':'Geräteprofile, responsive Spalten und Touchziele','status':'preview-only','detail':'Reflow in LUMO getestet. Kein Step4-Layoutgenerator; vorhandene native Layouts bleiben unverändert.'},
 {'feature':'Diagrammfarben und Übergänge','status':'preview-only','detail':'Design-Tokens vorbereitet, keine Diagramme oder Analytics erzeugt. LUMO reduziert Bewegung nach Systemeinstellung.'},
 {'feature':'Installierte HA-Version, Fremdkarten und externe Themes','status':'unverified','detail':'Nicht auf deinem HA installiert/geprüft. Importierte Themes und Templates bleiben geschützt; keine CustomCard-Ausführung.'}
]
def mapping(store,owner,document):
    value=document.get('design',defaults());validate(value);t=resolved(value)
    if value['options']['highContrast']:t={**t,'text':'#000000','card':'#ffffff','border':'#000000','primary':'#000000','secondary':'#000000','accent':'#000000'}
    name='LUMO '+{'noir':'Noir Luxury','ivory':'Soft Ivory Premium','smart':'Smart Clean'}[value['profile']]+' '+document['id'][:8]
    shadow='none' if not t['shadow'] else '0 8px '+str(t['shadow'])+'px '+('#73502b20' if t['material']=='soft' else '#00000022')
    surface=('linear-gradient(130deg,#ffffff0a,transparent) ' if t['material']=='layered' else '')+t['card']
    variables={'primary-color':t['primary'],'accent-color':t['accent'],'primary-text-color':t['text'],'secondary-text-color':t['secondary'],'ha-card-background':surface,'card-background-color':t['card'],'ha-card-border-color':t['border'],'ha-card-border-radius':str(t['radius'])+'px','ha-card-box-shadow':shadow,'ha-card-header-font-family':CATALOG['fonts'][t['font']],'ha-card-header-font-size':{'standard':'24px','comfortable':'28px','wall':'34px'}[t['size']],'lovelace-background':background_css(store,owner,document['settings']['background'])}
    return {'schemaVersion':1,'dashboardId':document['id'],'revision':document['revision'],'themeName':name,'themes':{name:variables},'capabilities':CAPABILITIES,'sourcePin':PIN,'runtime':'DEMO-20261028.4','changesOriginalExport':False,'installedHA':False,'instructions':'Separates Theme-Mapping, kein Dashboard. themes enthält einen HA-Theme-Namensraum (JSON ist YAML-kompatibel). Installation und bewusste Themezuweisung sind nicht Teil dieser App-Aktion. Bestehende Hintergründe und Themezuweisungen haben Vorrang.','previewTokens':t}
