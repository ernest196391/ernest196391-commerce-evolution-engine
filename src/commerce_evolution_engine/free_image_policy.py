"""Fail-closed reservation ledger for one supervised Cloudflare pilot per UTC day.
No network calls, credentials, publishing or paid fallback.
The server-side connector must independently verify account plan and identity.
"""
from datetime import datetime, timezone, timedelta
import sqlite3
import math

MODEL = "@cf/black-forest-labs/flux-2-klein-4b"
DAILY_LIMIT = 10000
PILOT_MAX = 250
MAX_AGE = timedelta(hours=1)

def reserve(db, *, job_id, account_key, certified_account_key, plan, checked_at,
            neurons_used, approved, input_size=(512,512), output_size=(1024,1024),
            now=None):
    """Reserve before transport. A crash or uncertain response never refunds.
    account_key is an opaque internal identifier, not a token.
    """
    now = now or datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None:
        raise ValueError("UTC-aware clock required")
    if not isinstance(checked_at, datetime) or checked_at.tzinfo is None:
        raise ValueError("Missing plan verification timestamp")
    if plan != "Workers Free" or not account_key or account_key != certified_account_key:
        raise ValueError("Free account not certified")
    if not timedelta(0) <= now - checked_at <= MAX_AGE or approved is not True:
        raise ValueError("Fresh verification and explicit preview approval required")
    if type(neurons_used) is not int or not 0 <= neurons_used <= DAILY_LIMIT:
        raise ValueError("Unknown usage")
    if not isinstance(job_id, str) or not job_id.strip():
        raise ValueError("Missing stable job id")
    if input_size not in ((512,512), None) or output_size != (1024,1024):
        raise ValueError("Pilot dimensions restricted")
    estimate = math.ceil((5.37 if input_size else 0) + 4 * 26.05)
    if estimate > PILOT_MAX or neurons_used + PILOT_MAX > DAILY_LIMIT:
        raise ValueError("Quota insufficient")
    day = now.astimezone(timezone.utc).date().isoformat()
    with sqlite3.connect(db, timeout=10) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS reservations (account TEXT NOT NULL, day TEXT NOT NULL, job TEXT NOT NULL, neurons INTEGER NOT NULL, PRIMARY KEY(account, day), UNIQUE(account,job))")
        try:
            conn.execute("INSERT INTO reservations VALUES (?, ?, ?, ?)", (account_key, day, job_id, PILOT_MAX))
        except sqlite3.IntegrityError as exc:
            raise ValueError("Pilot already reserved or job previously attempted; no retries") from exc
    return {"model": MODEL, "job_id": job_id, "day_utc": day,
            "estimated_neurons": estimate, "reserved_neurons": PILOT_MAX,
            "max_additional_usd": 0, "mode": "preview_only",
            "paid_fallback": False, "requires_visual_review": True}
