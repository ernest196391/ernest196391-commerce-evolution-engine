"""Offline daily worker: content-addressed inputs/results, no publishing."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

from .catalog_queue import CatalogQueue
from .catalog_supervisor import review
from .editorial_review import triage
from .photo_quality import SLOTS


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False).encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


class Worker:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.objects = self.root / 'objects'
        self.objects.mkdir(parents=True, exist_ok=True)
        self.queue = CatalogQueue(self.root / 'queue.sqlite')

    def put(self, data: bytes) -> str:
        key = digest(data)
        dest = self.objects / key
        if not dest.exists():
            # Write and sync before atomically exposing the immutable object.
            with tempfile.NamedTemporaryFile(dir=self.objects, delete=False) as f:
                temp = Path(f.name)
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            try:
                os.replace(temp, dest)
                if os.name == 'posix':
                    fd = os.open(self.objects, os.O_RDONLY)
                    try:
                        os.fsync(fd)
                    finally:
                        os.close(fd)
            finally:
                temp.unlink(missing_ok=True)
        if self.get(key) != data:
            raise ValueError('objeto persistente corrupto')
        return key

    def get(self, key: str) -> bytes:
        if len(key) != 64 or any(c not in '0123456789abcdef' for c in key):
            raise ValueError('huella inválida')
        data = (self.objects / key).read_bytes()
        if digest(data) != key:
            raise ValueError('objeto persistente corrupto')
        return data

    def submit(self, product: dict, research: dict, draft: dict, photos: Path) -> int:
        tenant, sku = product['tenant_id'], product['product_id']
        images = {}
        for name in SLOTS:
            path = photos / name
            if path.is_file():
                if path.stat().st_size > 25*1024*1024:
                    raise ValueError('archivo excesivo')
                images[name] = self.put(path.read_bytes())
        key = self.put(encode({'version': 1, 'product': product, 'research': research,
                               'draft': draft, 'images': images}))
        priority = 100 - triage(draft, tenant_id=tenant)['editorial_score']
        return self.queue.enqueue(tenant, sku, key, priority)

    def run(self, tenant: str, *, daily_limit: int = 10) -> list[dict]:
        completed = []
        while job := self.queue.claim(tenant, daily_limit=daily_limit):
            try:
                data = json.loads(self.get(job['fingerprint']))
                product = data['product']
                if (product['tenant_id'], product['product_id']) != (tenant, job['product']):
                    raise ValueError('identidad inconsistente')
                with tempfile.TemporaryDirectory() as temp:
                    folder = Path(temp)
                    for name, key in data['images'].items():
                        if name not in SLOTS:
                            raise ValueError('slot desconocido')
                        (folder / name).write_bytes(self.get(key))
                    result = review(product, data['research'], data['draft'], folder)
                result['input_fingerprint'] = job['fingerprint']
            except (OSError, ValueError, KeyError, TypeError):
                result = {'status':'blocked', 'blockers':['entrada_invalida_o_no_disponible'],
                          'tenant_id':tenant, 'product_id':job['product'],
                          'input_fingerprint':job['fingerprint'], 'publish_allowed':False,
                          'billable_generations':0, 'products_modified':0}
            key = self.put(encode(result))
            state = 'awaiting_review' if result['status'] == 'awaiting_human_review' else 'blocked'
            if self.queue.finish(tenant, job['id'], job['token'], state=state, result_hash=key):
                completed.append({'job':job['id'], 'product':job['product'], 'state':state, 'result_hash':key})
        return completed


def main(argv=None):
    p = argparse.ArgumentParser(description='Cola offline de candidatos, sin publicación')
    p.add_argument('--root', required=True, type=Path)
    sub = p.add_subparsers(dest='command', required=True)
    submit = sub.add_parser('submit')
    for name in ('product','research','draft','photos'):
        submit.add_argument('--'+name, required=True, type=Path)
    run = sub.add_parser('run')
    run.add_argument('--tenant', required=True)
    run.add_argument('--daily-limit', type=int, default=10)
    status = sub.add_parser('status')
    status.add_argument('--tenant', required=True)
    args = p.parse_args(argv)
    worker = Worker(args.root)
    if args.command == 'submit':
        result = worker.submit(*(json.loads(getattr(args,n).read_text(encoding='utf-8')) for n in ('product','research','draft')), args.photos)
    elif args.command == 'run':
        result = worker.run(args.tenant, daily_limit=args.daily_limit)
    else:
        result = worker.queue.snapshot(args.tenant)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
