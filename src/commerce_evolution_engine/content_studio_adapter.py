"""Offline contract adapter for Casa Viva Content Studio; no network writes."""
from __future__ import annotations

import re
from .catalog_approval import FIELDS

BRIEF = ('facts', 'buyer', 'objection', 'evidence', 'use', 'headline', 'offer')
MATRIX = ('duda', 'resultado', 'prueba', 'condicion', 'fuente', 'matriz_ok')
NAMES = dict(zip(FIELDS, ('name', 'description', 'short')))
STATUSES = ('publish', 'draft', 'pending', 'private')


def prepare_studio_request(ledger, tenant, key, current, studio, *, rollback=False):
    """Compile an approved plan against two fresh reads, without sending it."""
    preview = ledger.preview(tenant, key, current, rollback=rollback)
    if (type(studio.get('id')) is not int or studio['id'] != preview['product_id']
            or current.get('status') not in STATUSES
            or studio.get('status') != current['status']
            or any(studio.get(v) != current[k] for k, v in NAMES.items())):
        raise ValueError('proyección Studio no coincide con WooCommerce')
    hero, gallery = studio.get('image_id'), studio.get('gallery')
    if (type(hero) is not int or hero < 0 or not isinstance(gallery, list)
            or any(type(i) is not int or i <= 0 for i in gallery)
            or ([hero] if hero else []) + gallery != current.get('image_ids')):
        raise ValueError('galería concurrente o incompleta')
    version = studio.get('version')
    if not isinstance(version, str) or not re.fullmatch('[a-f0-9]{64}', version):
        raise ValueError('versión Studio inválida')
    brief = studio.get('brief')
    # A missing or partial brief would be overwritten by the PHP endpoint.
    if (not isinstance(brief, dict) or not set(BRIEF) <= set(brief)
            or set(brief) - set(BRIEF + MATRIX)
            or any(not isinstance(brief[k], str) or len(brief[k]) > 1000 for k in BRIEF)):
        raise ValueError('brief no conservable mediante save')
    # Omit matrix keys: the server carries their existing values verbatim.
    if current['sku'].startswith('MK-') and 'short_description' in preview['changes']:
        raise ValueError('Studio protege el resumen canónico MK-')
    target = {**current, **preview['changes']}
    if not target['name'].strip() or any(len(target[k]) > n for k, n in zip(FIELDS, (160, 20000, 2000))):
        raise ValueError('longitud de contenido incompatible')
    return {'mode': 'dry_run', 'publish_allowed': False, 'execute_allowed': False,
            'plan_hash': key, 'tenant_id': tenant, 'rollback': rollback,
            'would_update_live': current['status'] == 'publish',
            'method': 'POST', 'path': '/wp-json/casa-viva/v1/contenido/save',
            'body': {'id': studio['id'], 'version': version,
                     **{v: target[k] for k, v in NAMES.items()},
                     'brief': {k: brief[k] for k in BRIEF}}}
