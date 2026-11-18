# Radar de proveedores, inventario y oportunidades

**Diseño funcional, no implementado.** No existe integración automática con conversaciones privadas, WhatsApp, inventarios de terceros o WooCommerce en este repositorio.

## Objetivo
Observar ofertas de fuentes autorizadas, detectar cambios, localizar oportunidades y presentar decisiones trazables; evitar vender mercancía agotada sin borrar evidencia ni romper enlaces históricos.

## Módulos

### 1. Supplier Inbox / Nightly Review
- Una vez por la noche, procesar mensajes nuevos desde la última marca temporal de fuentes **expresamente autorizadas**.
- Fuentes piloto: exportación voluntaria de WhatsApp del propio usuario y catálogos que un proveedor entrega directamente. Otras fuentes requieren conector autorizado.
- Extraer `supplier_id, source_id, message_id_hash, timestamp, item, variant, model, availability_claim, quantity, currency, price, min_order, offer_expiry, location, evidence_pointer, confidence`.
- Inferencias siempre marcadas; no publicar números, nombres de contactos, fotos privadas ni mensajes completos en repos públicos.
- Crear bandeja de hallazgos: cambios de stock, nuevo artículo, bajada de precio, conflicto de especificaciones, reclamos de garantía y mensajes sin datos suficientes.

### 2. Availability Sentinel
- Comparar por SKU de proveedor y variantes con catálogo propio; primero reconciliar equivalencias (marca, modelo, presentación, color, talla, embalaje).
- Estados: `unknown`, `seen_available`, `suspected_out`, `confirmed_out`, `back_in_stock`, `discontinued`.
- **No tratar falta de nueva oferta como producto agotado.** Tampoco tomar como verdad una afirmación no fechada de terceros.
- Reglas iniciales: un anuncio explícito «agotado» del proveedor con coincidencia inequívoca marca `suspected_out`; segundo indicio independiente o verificación directa marca `confirmed_out`. Permisos y política humana determinan cualquier cambio.
- Salida por defecto: propuesta de poner **sin existencias**, pausa o revisión, nunca `DELETE` o borrado de medios. Preservar URL y SEO.
- El sistema debe manejar varias fuentes por producto: agotado con un proveedor no implica agotado en toda la red; usar stock agregado y tiempos de reserva.
- Si el proveedor vuelve a tener, recuperar disponibilidad solo cuando el abastecimiento y precio se verifiquen.

### 3. Product Scout / Discovery
- Explorar fuentes autorizadas o públicas con respeto a términos, robots.txt y límites de tráfico.
- Encontrar productos nuevos, marcas/modelos, variantes, demanda declarada, margen estimado y logística.
- Comparar contra catálogo, imágenes reales, coste en divisa, coste de mensajería, riesgo de devoluciones y disponibilidad confirmada.
- Entregable: propuestas ordenadas; **nunca** altas o compras automáticas sin aprobación.
- Revisión frecuente solo cuando existan conectores y fuentes legítimas; evitar scraping intensivo continuo.

### 4. Supplier Scorecard
- Frescura de catálogo; tasa de disponibilidad confirmada; días hasta respuesta; precio, calidad de datos y cumplimiento documentado.
- No publicar rankings privados; permitir revisión de errores y pruebas.

## Orquestación recomendada
- `nightly_supplier_review`: diario a las 02:00 **hora de la tienda** (ejemplo, no activado), ventana incremental.
- `availability_reconcile`: después de la revisión y cuando llega cambio verificado.
- `product_scout`: lotes limitados cada 6–12 h al inicio; frecuencia y coste ajustados por métricas.
- `daily_decision_digest`: resumen para responsable de tienda, con aprobación y pruebas.
- `weekly_quality_audit`: evalúa falsos positivos y brechas de cobertura.

## Casos de conflicto
- «No quedan de color rojo» no implica agotar todas las variantes.
- «No tengo ahora» puede significar agotamiento temporal, no discontinuidad.
- Dos proveedores pueden ofrecer el mismo SKU con diferente presentación o condición.
- Oferta vieja reenviada carece de confirmación actual.
- Un producto en pedidos abiertos o reservado requiere bloqueo de cambios no coordinados.
- Artículos de terceros sin capacidad de compra confirmada no se deben marcar como disponibles.

## Seguridad de WhatsApp
La API oficial Meta incluye capacidades específicas de grupos para cuentas/condiciones elegibles, pero eso **no garantiza** acceso a los grupos normales del teléfono ni a su historial anterior. Muchos integradores no entregan eventos de grupos existentes. Validar elegibilidad, fuente y consentimiento antes de implementar.

No usar clientes WhatsApp Web automatizados no autorizados para vigilar grupos ni extraer mensajes. No pedir QR de sesión, claves, chats privados o tokens en GitHub público.

## Aceptación del piloto
- 1 exportación voluntaria o 1 fuente autorizada.
- 25 mensajes sintéticos de prueba; clasificación con pruebas.
- 10 SKUs y 3 variantes conflictivas; falsas bajas = 0 en pruebas.
- Informe sin PII, con fecha/versión y enlace a evidencia privada.
- 7 noches en modo `dry_run`; ningún producto ocultado automáticamente.
- Después decidir si habilitar cambios reversibles con aprobación.

**Estado:** arquitectura documentada; faltan fuentes, consentimiento, conector y pruebas reales.
