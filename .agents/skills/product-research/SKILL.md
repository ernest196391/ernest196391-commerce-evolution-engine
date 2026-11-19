---
name: product-research
description: Investigar productos reales antes de redactar SEO o crear fotografías, comprobando identidad exacta, fabricante, fuentes y atributos sin copiar contenido de competidores.
---

# Product Research — agente de investigación comercial

Leer `AGENTS.md`, `docs/ACTIVE_PRIORITY.md`, `docs/AMAZON_BENCHMARK_AND_PRODUCT_RESEARCH.md` y `SECURITY.md`.

## Pasos obligatorios
1. Identificar artículo real, fotos originales, marca, modelo, variante, etiqueta y empaque.
2. Investigar en fuentes autorizadas y actuales: fabricante, manual, etiqueta, proveedor y documentación técnica. Registrar URL, fecha y fragmento evidencial.
3. Estudiar Amazon y otros referentes para **estructura, dudas de comprador y patrones de presentación**, no copiar textos/fotos ni heredar atributos de un producto similar.
4. Clasificar coincidencia: `exact_verified`, `comparable_only` o `unknown`; registrar diferencias de versión, color, voltaje y accesorios.
5. Construir expediente de claims con `source_ids` y estados `verified`, `unverified`, `conflict`. Comparar evidencia; una referencia registrada no prueba por sí sola veracidad.
6. Ejecutar validador estructural `python -m src.commerce_evolution_engine.research_gate --input examples/product-research.example.json --outdir results/research` cuando exista expediente.
7. No emplear claims no verificados en títulos, fichas o fotos. Marcar incógnitas.
8. Preparar borradores de SEO, descripción corta, descripción detallada y cuatro imágenes propuestas fieles al producto.
9. Exigir revisión humana del expediente y las fotografías originales antes de publicación.

## Límite técnico v0.1
Esta skill define la investigación; el validador offline NO navega Amazon, confirma la realidad de las fuentes o genera imágenes por sí solo. No reclamar esas acciones hasta implementarlas y probarlas.
