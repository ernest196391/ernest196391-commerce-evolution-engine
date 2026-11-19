"""Bounded public SEO reader; no cookies, redirects, credentials or writes."""
import json
import re
from urllib.parse import urlsplit
from urllib.request import Request, build_opener

from .woo_reader import NoRedirect
from .seo_audit import audit_batch
from .catalog_worker import encode


def extract(html, url, tenant):
    from lxml import html as parser
    doc=parser.fromstring(html)
    def cls(name):
        return f'contains(concat(" ",normalize-space(@class)," ")," {name} ")'
    def texts(xpath):
        return [' '.join(n.text_content().split()) for n in doc.xpath(xpath)]
    def walk(value):
        if isinstance(value,dict):
            kind=value.get('@type')
            if kind=='Product' or isinstance(kind,list) and 'Product' in kind:
                yield value
            for child in value.values(): yield from walk(child)
        elif isinstance(value,list):
            for child in value: yield from walk(child)
    products=[]
    for script in doc.xpath('//script[@type="application/ld+json"]'):
        try: products.extend(walk(json.loads(script.text or '')))
        except (ValueError,RecursionError): continue
    summary=f'//*[{cls("summary")}]'
    prices=texts(summary+f'//*[{cls("price")}]')
    match=re.fullmatch(r'US\$\s*(\d+(?:\.\d{2})?)',prices[0]) if len(prices)==1 else None
    stocks=texts(summary+f'//*[{cls("stock")}]')
    stock=stocks[0].casefold() if len(stocks)==1 else ''
    availability=('on_request' if 'encargo' in stock else 'out_of_stock' if stock=='agotado'
                  else 'in_stock' if re.fullmatch(r'queda[n]? \d+',stock) or stock=='hay existencias' else None)
    titles=texts('//h1'); canon=doc.xpath('//link[@rel="canonical"]/@href')
    product=products[0] if len(products)==1 else None
    # Store only structured fields needed by the detector, not arbitrary HTML.
    if product:
        product={k:product.get(k) for k in ('@type','name','sku','image','offers')}
    return {'tenant_id':tenant,'url':url,'h1':titles[0] if len(titles)==1 else None,
            'canonical':canon[0] if len(canon)==1 else None,'visible_price':match[1] if match else None,
            'visible_currency':'USD' if match else None,'visible_stock':availability,'product':product}


def run_batch(worker, *, origin, tenant, urls, opener=None):
    if not isinstance(tenant,str) or not tenant.strip() or not 1<=len(urls)<=8 or len(set(urls))!=len(urls):
        raise ValueError('lote inválido')
    base=urlsplit(origin)
    if base.scheme!='https' or not base.hostname or base.username or base.password or base.path not in ('','/') or base.query or base.fragment or base.port not in (None,443):
        raise ValueError('origen no autorizado')
    for url in urls:
        p=urlsplit(url)
        if p.scheme!='https' or p.netloc!=base.netloc or not re.fullmatch(r'/producto/[a-z0-9-]+/',p.path) or p.query or p.fragment:
            raise ValueError('ficha pública fuera del alcance')
    opener=opener or build_opener(NoRedirect())
    rows=[]; failures=[]
    for url in urls:
        try:
            with opener.open(Request(url,headers={'Accept':'text/html'},method='GET'),timeout=20) as res:
                if res.geturl()!=url or res.headers.get_content_type()!='text/html': raise ValueError('respuesta no permitida')
                data=res.read(2*1024*1024+1)
            if len(data)>2*1024*1024: raise ValueError('HTML excesivo')
            rows.append(extract(data,url,tenant))
        except (OSError,ValueError):
            failures.append(url)
    reports=audit_batch(rows)
    report={'tenant_id':tenant,'reports':reports,'failed_urls':failures,'complete':not failures,
            'publish_allowed':False,'mode':'read_only'}
    return {**report,'report_hash':worker.put(encode(report))}
