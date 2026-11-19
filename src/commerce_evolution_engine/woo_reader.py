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
                'source':'woo_rest_edit' if canonical else 'woo_store_public',
                'canonical':canonical,'modified_gmt':data.get('date_modified_gmt') if canonical else None,
                'publish_allowed':False}
