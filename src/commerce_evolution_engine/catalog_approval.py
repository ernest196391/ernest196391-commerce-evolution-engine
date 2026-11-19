"""Local approval ledger and reversible text-change plans, never writes WooCommerce."""
from __future__ import annotations

import json
import time
from .catalog_worker import Worker, encode, digest
from .catalog_supervisor import HUMAN_CHECKS

FIELDS = ('name', 'description', 'short_description')


def _text_fields(snapshot):
    if not all(isinstance(snapshot.get(k), str) for k in FIELDS):
        raise ValueError('snapshot textual incompleto')
    return {k: snapshot[k] for k in FIELDS}


class ApprovalLedger:
    def __init__(self, worker: Worker):
        self.worker = worker
        with worker.queue._db() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS approvals (
                id INTEGER PRIMARY KEY, tenant TEXT NOT NULL, job_id INTEGER NOT NULL,
                plan_hash TEXT NOT NULL, decision TEXT NOT NULL, actor TEXT NOT NULL,
                at REAL NOT NULL, FOREIGN KEY(job_id) REFERENCES jobs(id))''')

    def _candidate(self, tenant, job_id):
        job = next((j for j in self.worker.queue.snapshot(tenant) if j['id'] == job_id), None)
        if not job or job['state'] != 'awaiting_review':
            raise ValueError('candidato bloqueado o inexistente')
        result = json.loads(self.worker.get(job['result_hash']))
        source = json.loads(self.worker.get(job['fingerprint']))
        if (result.get('status') != 'awaiting_human_review' or result.get('blockers')
                or result.get('input_fingerprint') != job['fingerprint']
                or result.get('tenant_id') != tenant or result.get('product_id') != job['product']
                or result.get('publish_allowed') is not False):
            raise ValueError('informe no elegible')
        for key in source['images'].values():
            self.worker.get(key)
        return job, source, result

    def prepare(self, tenant, job_id, snapshot):
        job, source, result = self._candidate(tenant, job_id)
        if snapshot.get('canonical') is not True or snapshot.get('source') != 'woo_rest_edit':
            raise ValueError('se exige snapshot de WooCommerce en contexto edit')
        # Only a resolved canonical numeric WooCommerce ID may enter this plan.
        canonical_id = snapshot.get('id')
        if (snapshot.get('tenant_id') != tenant or not isinstance(canonical_id, int)
                or isinstance(canonical_id, bool) or canonical_id <= 0
                or str(canonical_id) != job['product']
                or not isinstance(snapshot.get('sku'), str)
                or snapshot['sku'] != source['draft'].get('sku')):
            raise ValueError('identidad canónica no coincide')
        before = _text_fields(snapshot)
        after = _text_fields(source['draft'])
        plan = {'version':1,'mode':'dry_run','tenant_id':tenant,'job_id':job_id,
                'product_id':canonical_id,'sku':snapshot['sku'],'input_hash':job['fingerprint'],
                'result_hash':job['result_hash'],'before':before,'after':after,
                'images_excluded':True,'publish_allowed':False}
        return self.worker.put(encode(plan))

    def _plan(self, tenant, key):
        plan = json.loads(self.worker.get(key))
        if plan['tenant_id'] != tenant or plan['publish_allowed'] is not False:
            raise ValueError('plan no elegible')
        job, source, _ = self._candidate(tenant,plan['job_id'])
        if (job['fingerprint'],job['result_hash']) != (plan['input_hash'],plan['result_hash']):
            raise ValueError('plan obsoleto')
        if (plan['after'] != _text_fields(source['draft']) or plan['sku'] != source['draft'].get('sku')
                or str(plan['product_id']) != job['product'] or set(plan['before']) != set(FIELDS)):
            raise ValueError('plan manipulado')
        return plan

    def record(self, tenant, key, *, actor, decision, checks=None):
        if not isinstance(actor,str) or not actor.strip() or decision not in ('approved','revoked'):
            raise ValueError('decisión o actor inválido')
        plan = self._plan(tenant,key)
        if decision == 'approved' and (not isinstance(checks,dict) or set(checks) != set(HUMAN_CHECKS)
                or any(v is not True for v in checks.values())):
            raise ValueError('checklist humano incompleto')
        with self.worker.queue._db() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('INSERT INTO approvals(tenant,job_id,plan_hash,decision,actor,at) VALUES(?,?,?,?,?,?)',
                       (tenant,plan['job_id'],key,decision,actor,time.time()))
            db.commit()

    def preview(self, tenant, key, current, *, rollback=False):
        plan = self._plan(tenant,key)
        if current.get('canonical') is not True or current.get('source') != 'woo_rest_edit':
            raise ValueError('se exige lectura canónica actual')
        with self.worker.queue._db() as db:
            row = db.execute('SELECT decision FROM approvals WHERE tenant=? AND plan_hash=? ORDER BY id DESC LIMIT 1',(tenant,key)).fetchone()
        if not row or row['decision'] != 'approved':
            raise ValueError('sin aprobación vigente')
        if (current.get('tenant_id'),current.get('id'),current.get('sku')) != (tenant,plan['product_id'],plan['sku']):
            raise ValueError('identidad actual no coincide')
        expected, target = (plan['after'],plan['before']) if rollback else (plan['before'],plan['after'])
        if _text_fields(current) != expected:
            raise ValueError('cambios concurrentes: cancelar')
        return {'mode':'dry_run','product_id':plan['product_id'], 'changes':{k:v for k,v in target.items() if expected[k]!=v},
                'plan_hash':key,'rollback':rollback,'publish_allowed':False}
