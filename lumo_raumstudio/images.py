"""Image uploads: full decoder, bounded raster, no SVG/URLs/animation/metadata."""
import io
import warnings
from PIL import Image,ImageOps
from store import StudioError
MAX_BYTES=8*1024*1024
MAX_PIXELS=8_000_000
Image.MAX_IMAGE_PIXELS=MAX_PIXELS

def decode(raw):
    if not isinstance(raw,bytes) or not 1<=len(raw)<=MAX_BYTES:raise StudioError('Bitte ein Bild bis 8 MiB auswählen.',413)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error',Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(raw)) as im:
                if im.format not in ('PNG','JPEG','WEBP') or getattr(im,'n_frames',1)!=1:raise ValueError()
                w,h=im.size
                if not 1<=w<=4096 or not 1<=h<=4096 or w*h>MAX_PIXELS:raise ValueError()
                im.verify()
            with Image.open(io.BytesIO(raw)) as im:
                im.load(); result=ImageOps.exif_transpose(im).convert('RGBA');result.load()
            b=io.BytesIO();result.save(b,format='PNG');data=b.getvalue()
            if len(data)>MAX_BYTES:raise ValueError()
            return data,result.width,result.height
    except (OSError,ValueError,SyntaxError,Image.DecompressionBombError,Image.DecompressionBombWarning):
        raise StudioError('Das Bild konnte nicht vollständig gelesen werden. Erlaubt: PNG, JPEG oder WebP, ohne Animation, bis 4096 Pixel je Seite und 8 Millionen Pixel.',422) from None
