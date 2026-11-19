import base64,hashlib,io,tempfile,unittest
from pathlib import Path
from PIL import Image
from src.commerce_evolution_engine.catalog_worker import Worker
from src.commerce_evolution_engine.flux_preview import import_preview,compose_preview


class FluxPreviewTests(unittest.TestCase):
    def test_import_and_preserve_cutout(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); worker=Worker(root/'state')
            def png(image):
                buf=io.BytesIO();image.save(buf,format='PNG');return buf.getvalue()
            data=png(Image.new('RGB',(1024,1024),'white'))
            payload={'mode':'preview_only','reserved_neurons':250,'human_review_required':True,'sha256':hashlib.sha256(data).hexdigest(),'background':'data:image/png;base64,'+base64.b64encode(data).decode()}
            preview=import_preview(payload,worker)
            self.assertFalse(preview['provider_certified'])
            with self.assertRaises(ValueError): import_preview({**payload,'sha256':'wrong'},worker)
            cutout=Image.new('RGBA',(100,100));cutout.paste((200,0,0,255),(20,20,80,80))
            key=worker.put(png(cutout)); dest=root/'candidate.png'
            with self.assertRaises(ValueError): compose_preview(worker,preview['background_hash'],key,destination=dest)
            result=compose_preview(worker,preview['background_hash'],key,destination=dest,approved_background=True,approved_cutout=True)
            self.assertFalse(result['publish_allowed'])
            self.assertEqual(Image.open(dest).getpixel((512,512)),(200,0,0))
            with self.assertRaises(FileExistsError): compose_preview(worker,preview['background_hash'],key,destination=dest,approved_background=True,approved_cutout=True)
