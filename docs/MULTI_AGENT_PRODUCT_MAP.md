# Mapa de producto escalable — Commerce Evolution Engine

## Estructura de agentes (planeada)
1. **Catalog Auditor:** fichas, títulos, SEO, fotos y evidencia visual.
2. **Supplier Inbox:** lectura permitida y normalización de mensajes/ofertas.
3. **Availability Sentinel:** compara stock por proveedor y variantes con catálogo; nunca borra.
4. **Product Scout:** detecta candidatos de productos y oportunidades.
5. **Content Studio:** crea borradores revisables con datos y fotos verificables.
6. **Pricing Analyst:** analiza margen, divisas, mensajería e impuestos como propuestas, nunca cambia precios sin autorización.
7. **Customer Insight:** detecta dudas frecuentes y causas de abandono en conversaciones autorizadas, desidentificadas.
8. **Visual QA:** audita mobile-first y consistencia estética.
9. **Supplier Scorecard:** puntualidad, frescura y calidad de evidencias.
10. **Control OS:** bandeja única de hallazgos, roles, permisos, aprobaciones y ejecución segura.

## Separación arquitectónica
- **Fuentes privadas por comercio:** WooCommerce, mensajes con consentimiento, catálogos y ERP.
- **Capa de ingesta:** adaptadores independientes, control de acceso, trazas, deduplicación.
- **Modelo canónico:** producto, variante, proveedor, oferta, observación de stock, evidencia y pedido (solo metadatos necesarios).
- **Motor de políticas:** permisos, costes, calidad de evidencia, aprobaciones.
- **Agentes:** clasifican, proponen y justifican; no reciben acceso directo a la base de datos operativa.
- **Ejecución:** workers con lista blanca e idempotencia; cola futura; límites de rate/concurrencia.
- **UI:** panel móvil-first con bandeja nocturna, cambios sugeridos, simulación antes/después y reversión.
- **Observabilidad:** eventos versionados, métricas y costes por tienda, auditoría y alertas.

## Escalado
Etapa A: una tienda, CSV y exportación autorizada, modo lectura.
Etapa B: cinco proveedores, cientos de SKUs, recolección incremental y revisión humana.
Etapa C: diez comercios aislados por tenant con RBAC y conectores independientes.
Etapa D: marketplace de skills/agentes con instalación por manifiesto firmado, versión y permisos visibles.

## Indicadores
- Cobertura de artículos con SKU canónico.
- Tiempo desde alerta «agotado» hasta revisión.
- Falsos positivos de falta de existencias.
- Tasa de fuentes con ofertas vigentes.
- Tiempo para crear borrador verificable.
- Productos nuevos propuestos/aprobados/vendidos.
- Incidentes de permisos y gasto por tienda (objetivo: cero).

## Política comercial
MIT permite uso comercial del núcleo abierto. Las funciones administradas, soporte, alojamiento e integraciones pueden empaquetarse como producto de pago si se respetan licencias y condiciones de las fuentes. No empaquetar chats ni catálogos privados de terceros.
