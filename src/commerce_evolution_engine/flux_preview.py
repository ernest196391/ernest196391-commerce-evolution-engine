"""Import the existing Core FLUX pilot's background, never invoke a provider."""
import base64
import hashlib
import io
import re
from pathlib import Path

from .photo_compositor import _pillow


def import_preview(payload, worker):
    if (payload.get('mode')!='preview_only' or payload.get('reserved_neurons')!=250
            or payload.get('human_review_required') is not True):
        raise ValueError('respuesta piloto incompatible')
    value=payload.get('background')
    if not isinstance(value,str) or len(value)>12*1024*1024:
        raise ValueError('imagen ausente o excesiva')
    match=re.fullmatch(r'data:image/(png|jpeg|webp);base64,([A-Za-z0-9+/=]+)',value)
    if match is None:
        raise ValueError('formato de preview inválido')
    data=base64.b64decode(match[2],validate=True)
    sha=hashlib.sha256(data).hexdigest()
    if len(data)>8*1024*1024 or payload.get('sha256')!=sha:
        raise ValueError('huella o tamaño inválido')
    Image,_,_=_pillow()
    with Image.open(io.BytesIO(data)) as img:
        if img.size!=(1024,1024) or img.format.lower()!=match[1] or getattr(img,'n_frames',1)!=1:
            raise ValueError('dimensiones o formato inesperado')
        img.verify()
    return {'background_hash':worker.put(data),'mode':'preview_only','provider_certified':False,
            'human_review_required':True,'publish_allowed':False}


def compose_preview(worker, background_hash, cutout_hash, *, destination, approved_background=False, approved_cutout=False):
    """Composite only approved layers; never pass product pixels through an AI model."""
    if approved_background is not True or approved_cutout is not True:
        raise ValueError('las dos capas requieren aprobación visual')
    Image,_,_=_pillow()
    with Image.open(io.BytesIO(worker.get(background_hash))) as source:
        if source.size!=(1024,1024) or getattr(source,'n_frames',1)!=1:
            raise ValueError('fondo incompatible')
        # Center crop a square background to the largest exact 4:5 canvas.
        # Do not stretch either layer or invent pixels through upscaling.
        base=source.crop((104, 2, 920, 1022)).convert('RGBA')
    with Image.open(io.BytesIO(worker.get(cutout_hash))) as source:
        if source.format!='PNG' or source.mode!='RGBA' or source.width*source.height>16000000:
            raise ValueError('recorte PNG transparente requerido')
        alpha=source.getchannel('A')
        bbox=alpha.getbbox()
        if not bbox or alpha.getextrema()[0]!=0:
            raise ValueError('recorte sin transparencia o sin producto')
        item=source.crop(bbox)
        item.thumbnail((int(base.width*.8),int(base.height*.8)),Image.Resampling.LANCZOS)
    base.alpha_composite(item,((base.width-item.width)//2, (base.height-item.height)//2))
    destination=Path(destination)
    with destination.open('xb') as out:
        base.convert('RGB').save(out,format='PNG')
    return {'mode':'preview_only','background_hash':background_hash,'cutout_hash':cutout_hash,
            'output_hash':hashlib.sha256(destination.read_bytes()).hexdigest(),
            'size':[base.width,base.height],'background_crop':[104,2,920,1022],
            'human_review_required':True,'publish_allowed':False,'cost_usd_api':0}
