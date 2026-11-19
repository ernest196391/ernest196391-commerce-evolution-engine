"""Bounded, resumable offline daily batch; no provider or Woo writes."""
import argparse
import json
from pathlib import Path
from collections import Counter
from .catalog_worker import Worker


def run_daily(worker, tenant, manifest, *, daily_limit=10):
    if not isinstance(tenant,str) or not tenant.strip() or not 1 <= daily_limit <= 100:
        raise ValueError('tenant o límite diario inválido')
    base = manifest.resolve().parent
    rows = json.loads(manifest.read_text(encoding='utf-8'))
    if not isinstance(rows,list) or len(rows)>10000:
        raise ValueError('manifiesto inválido')

    def local(value):
        path = (base / value).resolve()
        if not path.is_relative_to(base):
            raise ValueError('ruta fuera del lote')
        return path

    seen, submitted, errors = set(), [], []
    for index, row in enumerate(rows):
        try:
            product, research, draft = (json.loads(local(row[k]).read_text(encoding='utf-8'))
                                        for k in ('product','research','draft'))
            pid = product['product_id']
            if not isinstance(pid,str) or not pid.strip() or product['tenant_id'] != tenant or pid in seen:
                raise ValueError('identidad duplicada o incorrecta')
            seen.add(pid)
            photos = local(row['photos'])
            if not photos.is_dir():
                raise ValueError('directorio ausente')
            # No symlink may escape the batch through an image file.
            if any(not p.resolve().is_relative_to(base) for p in photos.iterdir()):
                raise ValueError('imagen fuera del lote')
            submitted.append(worker.submit(product,research,draft,photos))
        except (ValueError, OSError, KeyError, TypeError):
            errors.append({'row':index,'reason':'entrada_invalida'})
    completed = worker.run(tenant,daily_limit=daily_limit)
    snapshot = worker.queue.snapshot(tenant)
    return {'mode':'dry_run','tenant_id':tenant,'manifest_rows':len(rows),
            'submitted_job_ids':submitted,'invalid_rows':errors,'completed_this_run':completed,
            'queue_totals':dict(Counter(j['state'] for j in snapshot)),
            'daily_attempt_limit_utc':daily_limit,'publish_allowed':False,
            'billable_generations':0,'products_modified':0}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--tenant',required=True)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--daily-limit',type=int,default=10)
    a = p.parse_args()
    print(json.dumps(run_daily(Worker(a.root),a.tenant,a.manifest,daily_limit=a.daily_limit),ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
