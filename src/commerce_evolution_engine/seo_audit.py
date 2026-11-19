"""Offline comparison of observed public HTML facts and Product/Offer JSON-LD.

No network, no publication, no inference of inventory or Google eligibility.
"""
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit


def _money(value):
    try:
        if isinstance(value, bool):
            return None
        result = Decimal(str(value))
        return result if result.is_finite() and result >= 0 else None
    except (InvalidOperation, ValueError):
        return None


def _origin(url):
    p = urlsplit(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password or p.fragment:
        raise ValueError('URL HTTPS pública requerida')
    return p.netloc.lower()


def audit(observation):
    tenant, url = observation['tenant_id'], observation['url']
    if not isinstance(tenant, str) or not tenant.strip():
        raise ValueError('tenant requerido')
    _origin(url)
    findings = []
    product = observation.get('product')
    kind = product.get('@type') if isinstance(product,dict) else None
    if not (kind == 'Product' or isinstance(kind,list) and 'Product' in kind):
        return {'tenant_id':tenant,'url':url,'findings':['product_missing_or_ambiguous'], 'images':[], 'publish_allowed':False}
    if not all(isinstance(x,str) and x.strip() for x in (observation.get('h1'),product.get('name'))):
        findings.append('title_unverified')
    elif observation['h1'].strip() != product['name'].strip():
        findings.append('title_mismatch')
    if observation.get('canonical') != url:
        findings.append('canonical_missing_or_different')
    if type(product.get('sku')) is int:
        findings.append('numeric_sku_review')
    images = product.get('image', [])
    if isinstance(images,str):
        images=[images]
    if not isinstance(images,list) or not images or not all(isinstance(x,str) and x.startswith('https://') for x in images):
        findings.append('images_missing_or_unsupported'); images=[]
    if len(set(images)) != len(images):
        findings.append('duplicate_image_urls')
    offers=product.get('offers')
    if isinstance(offers,dict): offers=[offers]
    if not isinstance(offers,list) or len(offers)!=1 or not isinstance(offers[0],dict) or offers[0].get('@type')!='Offer':
        findings.append('offer_missing_or_ambiguous')
    else:
        offer=offers[0]
        a,b=_money(observation.get('visible_price')),_money(offer.get('price'))
        currency=observation.get('visible_currency'); marked=offer.get('priceCurrency')
        if a is None or b is None or not currency or not marked:
            findings.append('price_unverified')
        elif a!=b or currency!=marked:
            findings.append('price_or_currency_mismatch')
        avail=offer.get('availability')
        avail=avail.rsplit('/',1)[-1] if isinstance(avail,str) else None
        stock=observation.get('visible_stock')
        if stock=='on_request':
            findings.append('on_request_semantics_review')
        elif stock not in ('in_stock','out_of_stock') or avail not in ('InStock','OutOfStock'):
            findings.append('availability_unverified')
        elif (stock=='in_stock')!=(avail=='InStock'):
            findings.append('availability_mismatch')
        valid=offer.get('priceValidUntil')
        if valid:
            findings.append('price_expiration_source_review')
    return {'tenant_id':tenant,'url':url,'findings':sorted(set(findings)), 'images':images,'publish_allowed':False}


def audit_batch(observations):
    """Same ordered gallery across distinct URLs is a review signal, not proof of error."""
    reports=[audit(row) for row in observations]
    groups={}
    for report in reports:
        if report['images']:
            key=(report['tenant_id'],_origin(report['url']),tuple(report['images']))
            groups.setdefault(key,set()).add(report['url'])
    for report in reports:
        key=(report['tenant_id'],_origin(report['url']),tuple(report['images']))
        if len(groups.get(key,()))>1:
            report['findings'].append('shared_gallery_review')
    return reports
