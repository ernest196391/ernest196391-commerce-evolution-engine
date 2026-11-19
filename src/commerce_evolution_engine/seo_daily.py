"""Durable, bounded public SEO ticks on the existing Worker store."""
import argparse
import json
import uuid
from pathlib import Path

from .catalog_worker import Worker, encode
from .seo_audit import mark_shared_gallery
from .seo_public import run_batch, validate_scope


def tick(worker, *, origin, tenant, urls, daily_limit=8, tick_limit=2, opener=None):
    urls = list(urls)
    validate_scope(origin, tenant, urls)
    if type(daily_limit) is not int or type(tick_limit) is not int or not 1 <= tick_limit <= daily_limit <= 8:
        raise ValueError('límites inválidos')
    clock = worker.queue.clock
    day = int(clock() // 86400)
    config = encode([origin, urls, daily_limit]).decode()
    scope = (tenant, day)
    with worker.queue._db() as db:
        db.executescript('''CREATE TABLE IF NOT EXISTS seo_daily_runs (
            tenant TEXT, day INTEGER, config TEXT NOT NULL,
            PRIMARY KEY(tenant,day));
            CREATE TABLE IF NOT EXISTS seo_daily_progress (
            tenant TEXT, day INTEGER, url TEXT, position INTEGER,
            attempts INTEGER NOT NULL DEFAULT 0, token TEXT, expires REAL,
            result_hash TEXT, PRIMARY KEY(tenant,day,url));''')
        db.execute('BEGIN IMMEDIATE')
        db.execute('INSERT OR IGNORE INTO seo_daily_runs VALUES(?,?,?)', (*scope, config))
        if db.execute('SELECT config FROM seo_daily_runs WHERE tenant=? AND day=?', scope).fetchone()[0] != config:
            raise ValueError('manifiesto o presupuesto cambiado durante el día')
        db.executemany('INSERT OR IGNORE INTO seo_daily_progress(tenant,day,url,position) VALUES(?,?,?,?)',
                       [(*scope, url, i) for i, url in enumerate(urls)])
        db.commit()
    tried = set()
    for _ in range(tick_limit):
        now = clock()
        if int(now // 86400) != day:
            break
        with worker.queue._db() as db:
            db.execute('BEGIN IMMEDIATE')
            rows = db.execute('''SELECT p.*, (SELECT MAX(h.day) FROM seo_daily_progress h
                WHERE h.tenant=p.tenant AND h.url=p.url AND h.day<p.day AND h.result_hash IS NOT NULL) AS last_done
                FROM seo_daily_progress p WHERE p.tenant=? AND p.day=? ORDER BY attempts,last_done,position''', scope).fetchall()
            eligible = [r for r in rows if not r['result_hash'] and r['url'] not in tried and (not r['token'] or r['expires'] <= now)]
            if sum(r['attempts'] for r in rows) >= daily_limit or not eligible:
                db.commit()
                break
            url = eligible[0]['url']
            token = uuid.uuid4().hex
            db.execute('UPDATE seo_daily_progress SET attempts=attempts+1,token=?,expires=? WHERE tenant=? AND day=? AND url=?',
                       (token, now+120, *scope, url))
            db.commit()
        tried.add(url)
        result = run_batch(worker, origin=origin, tenant=tenant, urls=[url], opener=opener)
        key = result['report_hash'] if result['complete'] else None
        with worker.queue._db() as db:
            db.execute('UPDATE seo_daily_progress SET result_hash=?,token=NULL,expires=NULL WHERE tenant=? AND day=? AND url=? AND token=? AND expires>?',
                       (key, *scope, url, token, clock()))
    with worker.queue._db() as db:
        rows = db.execute('SELECT * FROM seo_daily_progress WHERE tenant=? AND day=? ORDER BY position', scope).fetchall()
    reports = []
    for row in rows:
        if row['result_hash']:
            report = json.loads(worker.get(row['result_hash']))
            reports.extend(report['reports'])
    result = {'tenant_id':tenant, 'day_utc':day, 'mode':'read_only', 'publish_allowed':False,
              'attempts':sum(r['attempts'] for r in rows), 'daily_limit':daily_limit,
              'pending_urls':[r['url'] for r in rows if not r['result_hash']],
              'complete':len(reports)==len(urls), 'reports':mark_shared_gallery(reports)}
    return {**result, 'report_hash':worker.put(encode(result))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--origin', required=True)
    parser.add_argument('--tenant', required=True)
    parser.add_argument('--url', action='append', required=True)
    parser.add_argument('--daily-limit', type=int, default=8)
    parser.add_argument('--tick-limit', type=int, default=2)
    args = parser.parse_args()
    print(encode(tick(Worker(args.root), origin=args.origin, tenant=args.tenant,
                      urls=args.url, daily_limit=args.daily_limit, tick_limit=args.tick_limit)).decode())


if __name__ == '__main__':
    main()
