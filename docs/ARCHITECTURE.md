# Arquitectura propuesta

Motor genérico, aislamiento multiempresa y una fuente comercial canónica por tienda. Casa Viva es piloto, no dependencia.

1. **Audit CLI — implementada:** CSV local → alertas y puntuación heurística. Cero red y escritura remota.
2. **Visual QA — pendiente:** Playwright en CI, capturas 360/390/768/1280 px, contraste, enlaces y fotos rotas.
3. **Woo Reader — pendiente:** API WooCommerce con permiso solo lectura, paginación, filtros de PII, snapshot y checksum.
4. **Content Studio Agent — pendiente:** fichas SEO, propuestas verificables y manifiestos visuales por SKU con revisión humana.
5. **Audit Bridge — pendiente:** lista blanca de diagnósticos, autenticación, autorización, expiración y resultados. Nunca shell libre.
6. **Control OS — pendiente:** cola, roles, aprobaciones y trazabilidad.
7. **Multiempresa — pendiente:** aislamiento de tiendas y políticas de costes.

## Contrato futuro de tarea
`id, tenant_id, actor_id, capability, source_version, mode, inputs_hash, budget_limit, risk, status, evidence, approval_id, result`.

Estados propuestos: `queued → running → proposed → waiting_approval → approved → completed`; también `blocked, failed, cancelled`.

**No implementados:** workers, API, conectores, autenticación, publicación.
