"""Verify observed staging roundtrips; does not execute requests or authorize writes."""
from .content_studio_adapter import prepare_studio_request

PROTECTED = ('price', 'regular_price', 'sale_price', 'stock_quantity',
             'stock_status', 'manage_stock', 'image_ids', 'status', 'type')
TEXT = ('name', 'description', 'short_description')


def verify_roundtrip(ledger, tenant, key, before, after, restored):
    """Each phase contains fresh canonical Woo and matching Studio projections.

    This verifies evidence consistency, not provenance or a real server execution.
    """
    phases = (before, after, restored)
    forward = prepare_studio_request(ledger, tenant, key, before['woo'], before['studio'])
    reverse = prepare_studio_request(ledger, tenant, key, after['woo'], after['studio'], rollback=True)
    prepare_studio_request(ledger, tenant, key, restored['woo'], restored['studio'])
    baseline = before['woo']
    if any(k not in p['woo'] for p in phases for k in PROTECTED):
        raise ValueError('evidencia comercial incompleta')
    if any(p['woo'][k] != baseline[k] for p in phases[1:] for k in PROTECTED):
        raise ValueError('regresión comercial o visual')
    if any(p['studio']['brief'] != before['studio']['brief'] for p in phases[1:]):
        raise ValueError('brief modificado')
    if any(after['woo'][k] != forward['body']['short' if k == 'short_description' else k] for k in TEXT):
        raise ValueError('texto aplicado no coincide')
    if any(restored['woo'][k] != baseline[k] for k in TEXT):
        raise ValueError('restauración textual incompleta')
    if after['studio']['version'] == before['studio']['version'] or after['studio']['version'] == restored['studio']['version']:
        raise ValueError('versión no cambió entre operaciones')
    if restored['studio']['version'] != before['studio']['version']:
        raise ValueError('versión inicial no restaurada')
    return {'status': 'evidence_consistent', 'plan_hash': key,
            'product_id': forward['body']['id'], 'reverse_version': reverse['body']['version'],
            'protected_fields': list(PROTECTED), 'server_certified': False,
            'publish_allowed': False, 'execute_allowed': False}
