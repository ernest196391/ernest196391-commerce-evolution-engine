"""Durable offline catalog work queue. No remote calls or publishing."""
from __future__ import annotations

import sqlite3
import time
import uuid
from pathlib import Path
from contextlib import contextmanager


class CatalogQueue:
    def __init__(self, path: Path, *, clock=time.time):
        self.path = Path(path)
        self.clock = clock
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY, tenant TEXT NOT NULL, product TEXT NOT NULL,
                fingerprint TEXT NOT NULL, priority INTEGER NOT NULL,
                state TEXT NOT NULL DEFAULT 'queued', attempts INTEGER NOT NULL DEFAULT 0,
                lease_until REAL, token TEXT, result_hash TEXT,
                UNIQUE(tenant, product, fingerprint)
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY, job_id INTEGER NOT NULL REFERENCES jobs(id),
                at REAL NOT NULL, event TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS queue_pick ON jobs(tenant,state,priority,id);
            """)

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.path, timeout=15, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA synchronous=FULL')
        try:
            yield db
        finally:
            db.close()

    def enqueue(self, tenant: str, product: str, fingerprint: str, priority: int = 0) -> int:
        if not all(isinstance(x, str) and x.strip() for x in (tenant, product, fingerprint)):
            raise ValueError('identidad o huella vacía')
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            inserted = db.execute('INSERT OR IGNORE INTO jobs(tenant,product,fingerprint,priority) VALUES(?,?,?,?)', (tenant,product,fingerprint,priority))
            job = db.execute('SELECT id FROM jobs WHERE tenant=? AND product=? AND fingerprint=?',(tenant,product,fingerprint)).fetchone()['id']
            if inserted.rowcount:
                db.execute('INSERT INTO events(job_id,at,event) VALUES(?,?,?)',(job,self.clock(),'queued'))
            db.commit()
            return job

    def claim(self, tenant: str, *, lease_seconds: int = 300, daily_limit: int = 10, max_attempts: int = 3):
        if min(lease_seconds,daily_limit,max_attempts) < 1:
            raise ValueError('límites positivos obligatorios')
        now = self.clock()
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            expired = db.execute("SELECT id,attempts FROM jobs WHERE tenant=? AND state='running' AND lease_until<=?",(tenant,now)).fetchall()
            for row in expired:
                state = 'blocked' if row['attempts'] >= max_attempts else 'queued'
                db.execute('UPDATE jobs SET state=?,token=NULL,lease_until=NULL WHERE id=?',(state,row['id']))
                db.execute('INSERT INTO events(job_id,at,event) VALUES(?,?,?)',(row['id'],now,'lease_expired_'+state))
            day_start = int(now // 86400) * 86400
            used = db.execute("SELECT count(*) FROM events e JOIN jobs j ON j.id=e.job_id WHERE j.tenant=? AND e.event='claimed' AND e.at>=?",(tenant,day_start)).fetchone()[0]
            row = None if used >= daily_limit else db.execute("SELECT * FROM jobs WHERE tenant=? AND state='queued' AND attempts<? ORDER BY priority DESC,id LIMIT 1",(tenant,max_attempts)).fetchone()
            if row is None:
                db.commit()
                return None
            token = uuid.uuid4().hex
            db.execute("UPDATE jobs SET state='running',attempts=attempts+1,token=?,lease_until=? WHERE id=?",(token,now+lease_seconds,row['id']))
            db.execute('INSERT INTO events(job_id,at,event) VALUES(?,?,?)',(row['id'],now,'claimed'))
            result = dict(db.execute('SELECT * FROM jobs WHERE id=?',(row['id'],)).fetchone())
            db.commit()
            return result

    def finish(self, tenant: str, job: int, token: str, *, state: str, result_hash: str) -> bool:
        if state not in {'awaiting_review','blocked'} or not isinstance(result_hash,str) or not result_hash.strip():
            raise ValueError('resultado offline inválido')
        now = self.clock()
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            changed = db.execute("UPDATE jobs SET state=?,result_hash=?,token=NULL,lease_until=NULL WHERE tenant=? AND id=? AND token=? AND state='running' AND lease_until>?",(state,result_hash,tenant,job,token,now)).rowcount
            if changed:
                db.execute('INSERT INTO events(job_id,at,event) VALUES(?,?,?)',(job,now,state))
            db.commit()
            return bool(changed)

    def snapshot(self, tenant: str) -> list[dict]:
        with self._db() as db:
            return [dict(row) for row in db.execute('SELECT id,product,fingerprint,priority,state,attempts,result_hash FROM jobs WHERE tenant=? ORDER BY id',(tenant,))]
