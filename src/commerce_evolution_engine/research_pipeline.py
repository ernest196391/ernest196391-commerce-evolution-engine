"""Bind discovered product revisions to evidence briefs and candidate jobs."""
import json
import argparse
from pathlib import Path
from .catalog_worker import encode
from .catalog_worker import Worker
from .catalog_discovery import Discovery
from .research_gate import validate
from .four_image_planner import build

QUESTIONS = ('¿Cuál es el modelo y variante exactos?', '¿Qué problema real resuelve?',
             '¿Qué especificaciones y límites necesita conocer el comprador?',
             '¿Qué incluye y qué garantía está confirmada?', '¿Qué originales autorizados existen?')


class ResearchPipeline:
    def __init__(self, worker):
        self.worker=worker
        self.discovery=Discovery(worker)
        with worker.queue._db() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS research_tasks (
                tenant TEXT NOT NULL, product INTEGER NOT NULL, fingerprint TEXT NOT NULL,
                brief_hash TEXT NOT NULL, job_id INTEGER, PRIMARY KEY(tenant,product,fingerprint))''')

    def prepare(self, tenant, *, limit=10):
        if type(limit) is not int or not 1<=limit<=100:
            raise ValueError('límite inválido')
        prepared=[]
        for item in self.discovery.pending(tenant):
            pid,key=item['product'],item['fingerprint']
            with self.worker.queue._db() as db:
                if db.execute('SELECT 1 FROM research_tasks WHERE tenant=? AND product=? AND fingerprint=?',(tenant,pid,key)).fetchone():
                    continue
            row=json.loads(self.worker.get(key))
            brief={'tenant_id':tenant,'product_id':str(pid),'sku':row['sku'],'observed_name':row['name'],
                   'observation_hash':key,'questions':list(QUESTIONS),'original_attachment_ids':row['image_ids'],
                   'search_terms':[row['name']+' ficha técnica manual',row['name']+' especificaciones'],
                   'copy_sections':['SEO título','beneficio breve','especificaciones verificadas','preguntas de compra'],
                   'gallery':['producto completo','uso o contexto','beneficio diferente'],
                   'status':'needs_research','publish_allowed':False}
            bh=self.worker.put(encode(brief))
            with self.worker.queue._db() as db:
                inserted=db.execute('INSERT OR IGNORE INTO research_tasks VALUES(?,?,?,?,NULL)',(tenant,pid,key,bh)).rowcount
            if inserted:
                prepared.append(brief)
            if len(prepared)>=limit:
                break
        return prepared

    def pending(self, tenant):
        with self.worker.queue._db() as db:
            rows=db.execute('''SELECT t.brief_hash FROM research_tasks t JOIN discovery_products d
                ON t.tenant=d.tenant AND t.product=d.product AND t.fingerprint=d.fingerprint
                WHERE t.tenant=? AND t.job_id IS NULL ORDER BY d.priority DESC,d.product''',(tenant,)).fetchall()
        return [json.loads(self.worker.get(r['brief_hash'])) for r in rows]

    def submit(self, tenant, pid, key, product, research, draft, photos):
        with self.worker.queue._db() as db:
            row=db.execute('''SELECT t.job_id FROM research_tasks t JOIN discovery_products d
                ON t.tenant=d.tenant AND t.product=d.product AND t.fingerprint=d.fingerprint
                WHERE t.tenant=? AND t.product=? AND t.fingerprint=?''',(tenant,pid,key)).fetchone()
        if row is None:
            raise ValueError('expediente ausente u obsoleto')
        observation=json.loads(self.worker.get(key))
        if (any(v.get('tenant_id')!=tenant or v.get('product_id')!=str(pid) for v in (product,research))
                or str(draft.get('id'))!=str(pid) or not observation['sku'] or draft.get('sku')!=observation['sku']):
            raise ValueError('identidad no coincide')
        evidence=validate(research)
        if evidence['identity_status']!='exact_verified' or not evidence['claim_count'] or evidence['eligible_claims']!=evidence['claim_count']:
            raise ValueError('investigación insuficiente o en conflicto')
        if not build(product)['source_image_verified']:
            raise ValueError('original no verificado')
        job=self.worker.submit({**product,'observation_hash':key},research,draft,photos)
        with self.worker.queue._db() as db:
            db.execute('UPDATE research_tasks SET job_id=? WHERE tenant=? AND product=? AND fingerprint=?',(job,tenant,pid,key))
        return job


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--tenant',required=True)
    parser.add_argument('--limit',type=int,default=10)
    args=parser.parse_args()
    pipeline=ResearchPipeline(Worker(args.root))
    created=pipeline.prepare(args.tenant,limit=args.limit)
    print(json.dumps({'new':len(created),'pending':pipeline.pending(args.tenant)},ensure_ascii=False,indent=2))
