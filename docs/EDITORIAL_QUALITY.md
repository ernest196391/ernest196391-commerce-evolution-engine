# Agente principal — primera rúbrica editorial (v0.1)

**Esta fase está activa.** Este instrumento mejora la identificación de fichas que necesitan atención, sin afirmar que un texto largo sea automáticamente bueno o que exista verificación SEO profesional.

## Objetivo
Priorizar, con datos reproducibles, los productos con títulos pobres, textos genéricos, falta de detalles útiles para decidir, texto corto duplicado y galerías con pocas referencias.

## Comando
```bash
python -m unittest discover -s tests -v
python -m src.commerce_evolution_engine.editorial_review --input examples/products.csv --outdir results/editorial --tenant demo
```

Genera `editorial-report.json` y `editorial-priorities.csv`. El CSV puede ser exportación WooCommerce sin clientes ni pedidos.

## Criterios automáticos provisionales
- Título ausente, breve, demasiado extenso o todo en mayúsculas.
- Descripción ausente o breve, poco vocabulario y ausencia de señales de especificaciones.
- Lenguaje publicitario genérico y descripción corta que repite literalmente el título.
- Menos de cuatro referencias de imágenes.
- Detección de **afirmaciones técnicas que requieren fuentes**, como mAh, horas, watts o garantías. No significa que sean falsas.

**Limitaciones:** sin inspección semántica avanzada, sin juicio sobre diseño/fidelidad fotográfica, sin validación factual ni puntuación SEO reconocida. Una ficha larga, llena de palabras técnicas o cuatro referencias de fotos aún puede ser muy mala. Toda salida es candidata a revisión humana.

## Control de cambios
`review_key` distingue tienda y producto como identificador para futura cola de tareas. No hay escritura en WooCommerce, cron, precios, stock ni publicación. Los resultados contienen título y SKU: no colocar exportaciones privadas en GitHub público.

## Siguiente bloque
Conectar datos reales en **modo lectura**, revisar muestra estratificada, definir fichas objetivo y generar borradores con evidencia por afirmación, incluyendo fotos del artículo original. Un ejemplo aprobado servirá para calibrar la rúbrica antes de programar ejecuciones diarias.
