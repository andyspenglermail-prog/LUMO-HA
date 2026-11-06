"""Internal native mapping proof, NOT a publication/export API.
Generated CSS only; image alpha baked in PNG, independent of LUMO/Ingress.
"""
import base64,copy,io
from PIL import Image
from settings import background,validate

def background_css(store,owner,bg):
    background(bg)
    if bg['imageId'] is None:return bg['color']
    _,raw=store.image(owner,bg['imageId'])
    with Image.open(io.BytesIO(raw)) as im:
        im.load();im=im.convert('RGBA');alpha=im.getchannel('A').point([round(x*bg['opacity']/100) for x in range(256)]);im.putalpha(alpha);out=io.BytesIO();im.save(out,format='PNG')
    uri='data:image/png;base64,'+base64.b64encode(out.getvalue()).decode()
    size=str(bg['scale'])+'% auto' if bg['mode']=='scale' else bg['mode']
    return bg['color']+' url("'+uri+'") '+bg['position']+' / '+size+' no-repeat '+bg['attachment']

def compile_native(store,owner,document):
    validate(document['settings'],document['views']);result=copy.deepcopy(document['native'] or {'views':[]})
    result['title']=document['name'];result['background']=background_css(store,owner,document['settings']['background'])
    n=document['settings']['navigation'];views=[]
    for view in document['views']:
        native=copy.deepcopy(result['views'][view['nativeIndex']]);native.setdefault('path',str(view['nativeIndex']))
        native['show_icon_and_title']=n['showIconAndTitle']
        if view['backgroundOverride'] is not None:native['background']=background_css(store,owner,view['backgroundOverride'])
        views.append((view['id'],native))
    if n['startView']:views.sort(key=lambda pair:pair[0]!=n['startView'])
    result['views']=[v for _,v in views];return result
