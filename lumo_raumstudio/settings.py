"""Closed settings contract. Views may override global background later."""
import re
from store import StudioError
POSITIONS=tuple(x+' '+y for x in ('left','center','right') for y in ('top','center','bottom'))
def fields(v,keys):
    if type(v) is not dict or set(v)!=set(keys):raise StudioError('Unbekannte oder fehlende Einstellungen.')
def background(b):
    fields(b,('color','imageId','position','mode','scale','opacity','attachment'))
    if type(b['color']) is not str or not re.fullmatch(r'#[0-9a-fA-F]{6}',b['color']):raise StudioError('Bitte eine gültige Hintergrundfarbe wählen.')
    if b['position'] not in POSITIONS or b['mode'] not in ('auto','cover','contain','scale') or b['attachment'] not in ('scroll','fixed'):raise StudioError('Diese Bilddarstellung wird nicht unterstützt.')
    if type(b['scale']) is not int or not 10<=b['scale']<=300 or type(b['opacity']) is not int or not 0<=b['opacity']<=100:raise StudioError('Skalierung: 10–300 %. Deckkraft: 0–100 %.')
    if b['imageId'] is not None and (type(b['imageId']) is not str or not re.fullmatch('[a-f0-9]{32}',b['imageId'])):raise StudioError('Dieses Bild ist nicht verfügbar.')
    return b

def validate(settings,views):
    fields(settings,('background','navigation'));background(settings['background'])
    n=settings['navigation']; fields(n,('showIconAndTitle','startView','showInSidebar','requireAdmin'))
    if any(type(n[k]) is not bool for k in ('showIconAndTitle','showInSidebar','requireAdmin')):raise StudioError('Ungültige Navigationseinstellung.')
    if n['startView'] is not None and n['startView'] not in [v['id'] for v in views]:raise StudioError('Die Startansicht ist nicht vorhanden.')
    return settings
