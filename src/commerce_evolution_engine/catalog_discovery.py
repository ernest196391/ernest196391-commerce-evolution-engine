"""Public catalog observation, persistent page checkpoint and pending review list."""
import argparse
import json
from pathlib import Path
from .catalog_worker import Worker
from .woo_reader import WooReader
from .catalog_worker import digest, encode
from .editorial_review import triage


class Discovery:
    def __init__(self, worker):
        self.worker = worker
        with worker.queue._db() as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS discovery_cursor (
                tenant TEXT PRIMARY KEY, origin TEXT NOT NULL, page INTEGER NOT NULL, cycle INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS discovery_products (
                tenant TEXT NOT NULL, product INTEGER NOT NULL, fingerprint TEXT NOT NULL,
                report_hash TEXT NOT NULL, priority INTEGER NOT NULL,
                PRIMARY KEY(tenant,product));''')

    def scan(self, reader, *, max_pages=2):
        if type(max_pages) is not int or not 1 <= max_pages <= 10:
            raise ValueError('límite de páginas inválido')
        tenant = reader.tenant
        changed = 0
        for _ in range(max_pages):
            with self.worker.queue._db() as db:
                db.execute('INSERT OR IGNORE INTO discovery_cursor VALUES(?,?,1,1)',(tenant,reader.origin))
                cursor = dict(db.execute('SELECT * FROM discovery_cursor WHERE tenant=?',(tenant,)).fetchone())
            if cursor['origin'] != reader.origin:
                raise ValueError('origen del tenant no coincide')
            rows, last = reader.public_page(cursor['page'])
            prepared=[]
            for row in rows:
                if row['tenant_id'] != tenant or row['canonical'] is not False:
                    raise ValueError('observación inválida')
                key=self.worker.put(encode(row))
                report=triage({**row,'images':'|'.join(map(str,row['image_ids']))},tenant_id=tenant)
                prepared.append((row['id'],key,self.worker.put(encode(report)),100-report['editorial_score']))
            with self.worker.queue._db() as db:
                db.execute('BEGIN IMMEDIATE')
                actual=dict(db.execute('SELECT * FROM discovery_cursor WHERE tenant=?',(tenant,)).fetchone())
                if actual != cursor:
                    raise ValueError('otro escaneo avanzó el cursor')
                for pid,key,report,priority in prepared:
                    old=db.execute('SELECT fingerprint FROM discovery_products WHERE tenant=? AND product=?',(tenant,pid)).fetchone()
                    if old is None or old['fingerprint']!=key:
                        db.execute('INSERT OR REPLACE INTO discovery_products VALUES(?,?,?,?,?)',(tenant,pid,key,report,priority))
                        changed+=1
                db.execute('UPDATE discovery_cursor SET page=?,cycle=? WHERE tenant=?',
                           (1 if last else cursor['page']+1,cursor['cycle']+int(last),tenant))
                db.commit()
            if last:
                break
        return {'changed':changed,'cycle_complete':last,'publish_allowed':False,'pending':self.pending(tenant)}

    def pending(self, tenant):
        with self.worker.queue._db() as db:
            return [dict(r) for r in db.execute('SELECT product,fingerprint,report_hash,priority FROM discovery_products WHERE tenant=? ORDER BY priority DESC,product',(tenant,))]


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--origin',required=True)
    parser.add_argument('--tenant',required=True)
    parser.add_argument('--max-pages',type=int,default=2)
    args=parser.parse_args()
    print(json.dumps(Discovery(Worker(args.root)).scan(WooReader(args.origin,args.tenant),max_pages=args.max_pages),indent=2))
