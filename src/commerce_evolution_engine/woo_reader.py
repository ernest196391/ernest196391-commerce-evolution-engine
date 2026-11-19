"""Read-only WooCommerce boundary. Never sends writes or follows redirects."""
from __future__ import annotations

import base64
import json
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class WooReader:
    def __init__(self, origin, tenant, *, credentials=None, opener=None):
        parts = urlsplit(origin)
        if (parts.scheme != 'https' or not parts.hostname or parts.username or parts.password
                or parts.path not in ('','/') or parts.query or parts.fragment):
            raise ValueError('origen HTTPS explícito requerido')
        if not tenant:
            raise ValueError('tenant requerido')
        self.origin = origin.rstrip('/')
        self.tenant = tenant
        self.credentials = credentials
        self.opener = opener or build_opener(NoRedirect())

    def public_page(self, page, *, per_page=20):
        if type(page) is not int or page < 1 or type(per_page) is not int or not 1 <= per_page <= 50:
            raise ValueError('paginación inválida')
        route = f'/wp-json/wc/store/v1/products?page={page}&per_page={per_page}&orderby=id&order=asc'
        req = Request(self.origin+route, headers={'Accept':'application/json'}, method='GET')
        with self.opener.open(req, timeout=20) as response:
            raw = response.read(4*1024*1024+1)
            total_pages = int(response.headers['X-WP-TotalPages'])
        if len(raw)>4*1024*1024 or total_pages < 0 or page > max(1,total_pages):
            raise ValueError('página inválida')
        data = json.loads(raw)
        if not isinstance(data,list) or len(data)>per_page:
            raise ValueError('respuesta de catálogo inválida')
        rows = []
        for p in data:
            if (not isinstance(p,dict) or type(p.get('id')) is not int or p['id']<=0
                    or any(not isinstance(p.get(k),str) for k in ('sku','name','description','short_description'))
                    or not isinstance(p.get('images'),list)
                    or any(not isinstance(i,dict) or type(i.get('id')) is not int or i['id']<=0 for i in p['images'])):
                raise ValueError('producto público inválido')
            rows.append({**{k:p[k] for k in ('id','sku','name','description','short_description')},
                         'image_ids':[i['id'] for i in p['images']], 'tenant_id':self.tenant,
                         'canonical':False,'source':'woo_store_public','publish_allowed':False})
        ids = [p['id'] for p in rows]
        if ids != sorted(set(ids)):
            raise ValueError('orden de página inesperado')
        return rows, page >= total_pages

    def read(self, product_id, *, expected_sku, canonical=False):
        if not isinstance(product_id,int) or isinstance(product_id,bool) or product_id <= 0 or not expected_sku:
            raise ValueError('identidad inválida')
        headers = {'Accept':'application/json'}
        if canonical:
            if not self.credentials or len(self.credentials)!=2 or not all(self.credentials):
                raise ValueError('credenciales de lectura requeridas')
            auth = base64.b64encode(':'.join(self.credentials).encode()).decode()
            headers['Authorization'] = 'Basic '+auth
            route = f'/wp-json/wc/v3/products/{product_id}?context=edit'
        else:
            route = f'/wp-json/wc/store/v1/products/{product_id}'
        req = Request(self.origin+route, headers=headers, method='GET')
        with self.opener.open(req, timeout=20) as response:
            raw = response.read(2*1024*1024+1)
        if len(raw)>2*1024*1024:
            raise ValueError('respuesta excesiva')
        data = json.loads(raw)
        if data.get('id') != product_id or data.get('sku') != expected_sku:
            raise ValueError('identidad no coincide')
        fields = ('name','description','short_description')
        if not all(isinstance(data.get(k),str) for k in fields):
            raise ValueError('texto incompleto')
        images = data.get('images')
        if not isinstance(images,list) or any(not isinstance(i,dict) or not isinstance(i.get('id'),int) for i in images):
            raise ValueError('galería inválida')
        return {'tenant_id':self.tenant,'id':product_id,'sku':expected_sku,
                **{k:data[k] for k in fields},'image_ids':[i['id'] for i in images],
                **{k:data[k] for k in ('status','type','price','regular_price','sale_price',
                                      'stock_quantity','stock_status','manage_stock') if canonical and k in data},
                'source':'woo_rest_edit' if canonical else 'woo_store_public',
                'canonical':canonical,'modified_gmt':data.get('date_modified_gmt') if canonical else None,
                'publish_allowed':False}
