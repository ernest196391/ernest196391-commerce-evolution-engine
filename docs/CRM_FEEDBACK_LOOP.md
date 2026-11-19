# Ciclo de preguntas reales → fichas/fotografías → regresiones

## Decisión
Los chats autorizados son insumo de mejora, **no sustituto del catálogo ni del fabricante**. El estudio de Casa Viva de 2026-11-18 identificó como principales temas de gestoras: detalles del producto, estado del pedido, disponibilidad, comisiones y mensajería. Los conteos están en reporte privado del Centro de Control; no publicar historiales ni identificadores privados en este repositorio.

## Flujo seguro
1. **Ingesta CRM (fuera de este módulo, no implementada):** leer únicamente fuentes autorizadas, producir agregados por fecha, tema, SKU/variante, rol y evidencia, sin teléfonos ni cuerpos completos en archivos públicos.
2. **Clasificación:** separar dudas de contenido, problemas de disponibilidad, seguimiento de pedido, tarifas y comisiones. No convertir preguntas de pedidos o stock en promesas de fichas.
3. **Motor implementado:** `customer_signals.py` usa solo números por tema. Prioriza tickets sin respuesta y sugiere módulo responsable y pieza fotográfica, sin acceso a WhatsApp ni edición del catálogo.
4. **Investigación:** localizar modelo exacto en fabricante/proveedor, consultar preguntas y especificaciones verificadas.
5. **Propuesta:** actualizar FAQ, descripción sin redundancia, foto de beneficios o detalles cuando la cuestión lo requiera.
6. **Revisión humana:** comparar antes/después, fuentes, cambios y calidad móvil.
7. **Evidencia posterior:** medir preguntas repetidas y correcciones del bot; nunca inferir mejora de ventas por un cambio sin datos.

## Auto-reparación de VivaBot (fase separada)
- Auditor lee `crm_errores`, `crm_escalations`, `crm_feedback`, `crm_support_requests` y estados de integraciones.
- Detecta clases (promesa transaccional ficticia, pregunta repetida, estado agotado incorrecto, ambigüedad de mensajería, confusión SKU, enrutamiento de carrera, interpretación de negación).
- Produce issue/PR con reproducciones sintéticas, pruebas de regresión y checklist de permisos.
- Un supervisor de código revisa CI, diferencias en stock/pedidos, evidencia del servidor y canary; no auto fusionar cambios de pagos, reparto, asignaciones, comisiones o pedidos.
- Aprovechar el supervisor y la cola Control OS existentes; no duplicar workers o automaciones ya activas.

## Objetos reutilizables
`tenant_id, product_id, sku, variant, normalized_question, source_kind, evidence_hash, observed_at, confidence, issue_type, proposed_fix, qa_result, approval`. `normalized_question` y texto privado nunca van al repo abierto.

## Estado
La fuente CRM fue auditada manualmente mediante conector Supabase de solo lectura y el resultado concreto se guardó en un repositorio privado de Control OS. `customer_signals.py` está implementado como capa agregada; **no es todavía un cron nocturno ni un conector automático WhatsApp**.
