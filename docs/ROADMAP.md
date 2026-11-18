# Hoja de ruta y prioridad actual

**Regla de ejecución:** consultar [ACTIVE_PRIORITY.md](ACTIVE_PRIORITY.md) antes de iniciar trabajo. Primero terminar el agente diario de calidad de catálogo; solo después desarrollar radar de proveedores/WhatsApp y descubrimiento.

## Bloque activo — Agente de mejora diaria
1. Auditor CSV offline implementado, probar integración y cobertura.
2. Auditor visual Playwright publicado, pendiente de ejecución real y valoración humana de capturas.
3. Rúbricas de calidad comercial: títulos SEO, ficha breve/completa, datos comprobados, precisión técnica y fotografía real.
4. Piloto completo de un producto con cuatro imágenes fieles, fichas y aprobación.
5. Lector WooCommerce de mínimo privilegio; snapshots, paginación y comparación de versiones.
6. Motor incremental para evaluar diariamente y generar **borradores** seguros, evitando duplicados y cualquier gasto adicional por defecto.
7. Pruebas integradas, revisión móvil, auditoría de errores, reversión, documentación de instalación y aceptación del piloto.

## Componentes compartidos que se diseñan durante el bloque activo
Identidad de comercio/SKU/variante, evidencias, cola idempotente, permisos y políticas, versiones, costes, registro, aprobación y `dry_run`; conexiones encapsuladas. **No implementar módulos de proveedores por anticipado.**

## Fase siguiente — congelada
- Lectura autorizada de conversaciones/grupos, revisión nocturna, normalización de ofertas.
- Radar de disponibilidad con comparación entre proveedores, jamás borrar por silencio.
- Buscador de productos, detección de oportunidades y scorecard de proveedores.
- Integración con WooCommerce para proponer cambios reversibles de existencias, con políticas y pruebas.

## Fases posteriores
- Audit Bridge de diagnósticos seguros sin SSH arbitrario.
- Orquestador multiagente y panel de aprobaciones.
- Aislamiento multiempresa, instalador y distribución.

Cada fase necesita pruebas reproducibles, presupuesto certificado, protección de datos, permisos y evidencia de funcionamiento real.
