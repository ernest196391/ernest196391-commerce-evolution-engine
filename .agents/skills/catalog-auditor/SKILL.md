---
name: catalog-auditor
description: Auditar en modo solo lectura un catálogo CSV, priorizar títulos, fichas e imágenes y preparar mejoras sin inventar datos ni publicar.
---

# Catalog Auditor — skill v0.1

## Objetivo
Informe reproducible y lista priorizada de revisiones comerciales. No ejecuta despliegues, no accede por SSH y no edita productos.

## Entrada
CSV autorizado sin datos personales, nombre del comercio, fecha y fuente si se conocen. No incluyas claves WooCommerce.

## Procedimiento
1. Leer `AGENTS.md` y `SECURITY.md`.
2. Validar CSV; conservar el original.
3. Ejecutar `python -m src.commerce_evolution_engine.audit --input RUTA.csv --outdir results`.
4. Revisar alertas heurísticas y campos ausentes.
5. Seleccionar muestra estratificada por categoría y problemas.
6. Proponer fichas solo con prestaciones verificables; marcar desconocidos como pendientes.
7. Para imágenes futuras exigir fotografía real, principal limpia, contexto realista, infografía con datos verificables y detalle/medidas sin cambiar el producto.
8. No confundir campo rellenado con calidad.
9. Presentar informe, evidencias, límites y propuestas en borrador. Solicitar autorización específica para operaciones comerciales futuras.

## Prohibiciones
Comandos remotos, APIs facturables, cambios WooCommerce, inventar fotografías, afirmar calidad visual por contar URLs, publicación automática basada en un score.

## Entregables
`report.json`, `priorities.csv`, limitaciones y propuestas revisables. El score es exclusivamente orientativo.
