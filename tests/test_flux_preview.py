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
            with Image.open(dest) as rendered:
                self.assertEqual(rendered.size,(816,1020))
                self.assertEqual(rendered.getpixel((408,510)),(200,0,0))
                self.assertEqual(rendered.getpixel((377,510)),(255,255,255))
                self.assertEqual(rendered.getpixel((378,510)),(200,0,0))
            self.assertEqual(result['size'],[816,1020])
            self.assertEqual(result['background_crop'],[104,2,920,1022])
            self.assertEqual(result['output_hash'],hashlib.sha256(dest.read_bytes()).hexdigest())
            # Exact 4:5 and minimum 800 px meet the existing gallery QA.
            from src.commerce_evolution_engine.photo_quality import inspect
            dest.rename(root/'02-lifestyle.png')
            report=inspect(root)
            self.assertEqual(next(s for s in report['slots'] if s['slot']=='02-lifestyle.png')['issues'],[])
            dest=root/'02-lifestyle.png'
            with self.assertRaises(FileExistsError): compose_preview(worker,preview['background_hash'],key,destination=dest,approved_background=True,approved_cutout=True)
