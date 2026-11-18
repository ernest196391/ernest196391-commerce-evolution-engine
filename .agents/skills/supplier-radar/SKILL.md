---
name: supplier-radar
description: Procesar observaciones autorizadas de proveedores en modo solo lectura y detectar posibles agotamientos por SKU y variante sin cambiar WooCommerce.
---

# Supplier Radar — skill v0.1

Lee `AGENTS.md`, `SECURITY.md`, `docs/AUTONOMY_AND_PERMISSIONS.md`, `docs/SUPPLIER_RADAR.md`.

1. Asegurar consentimiento, procedencia y minimización de datos.
2. Usar registros sintéticos o exportación **explícitamente autorizada**; no vigilar grupos privados sin permiso.
3. Reconciliar identificadores exactos de SKU + variante + proveedor; no mezclar productos similares.
4. Ejecutar `python -m src.commerce_evolution_engine.supplier_radar --input examples/supplier-observations.example.json --outdir results/suppliers`.
5. Leer propuestas en `results/suppliers/supplier-proposals.json` y mostrar incertidumbre.
6. Nunca interpretar silencio del proveedor como producto agotado.
7. Nunca alterar WooCommerce; requerir validación de disponibilidad total de los proveedores y de reservas antes de recomendar ocultar productos.
8. Registrar bloqueos de acceso con su permiso mínimo requerido; no eludir autenticaciones.
