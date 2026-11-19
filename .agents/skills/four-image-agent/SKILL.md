---
name: four-image-agent
description: Preparar cuatro imágenes comerciales fieles a la foto real del producto, investigando sus datos y exigiendo evidencia y QA antes de cualquier publicación.
---

# Four Image Agent — agente activo

Leer: `AGENTS.md`, `docs/ACTIVE_PRIORITY.md`, `docs/FOUR_IMAGE_AGENT.md`, `docs/AMAZON_BENCHMARK_AND_PRODUCT_RESEARCH.md` y `SECURITY.md`.

1. Identificar producto, variante, foto(s) originales, marca/modelo y permiso de uso.
2. Verificar datos con fabricante, proveedor y documentación fechada; no trasladar características de comparables.
3. Definir resultado deseado del comprador; plan 01 hero, 02 vida real, 03 infografía, 04 detalles.
4. Elegir método económico: composición/recorte gratis o proveedor de IA opt-in dentro de presupuesto y políticas existentes.
5. No inventar datos, accesorios, botones, conectores, medidas, colores, embalaje, logos o etiquetas.
6. `python -m src.commerce_evolution_engine.four_image_planner --input examples/four-image-product.example.json --outdir results/four-images` prepara el manifiesto sin generar imágenes.
7. Cuando existan imágenes reales, examinarlas individualmente a 360 px y tamaño completo, verificando fidelidad contra original.
8. Presentar las 4 piezas por separado para aprobación, sin watermark, texto o precio sobre hero.
9. Guardar fuentes, hashes, revisiones, costo, QA y resultados, y no publicar automáticamente.
10. Compartir componentes de evidencia, políticas e idempotencia con futuros agentes, pero no empezar aún el radar de proveedores.

## Estado actual
Motor de planificación y skill, no generador conectado. No afirmar que los archivos de imagen ya se produjeron.
