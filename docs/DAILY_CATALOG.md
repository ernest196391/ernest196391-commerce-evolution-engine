# Ejecución incremental diaria offline

Preparar un manifiesto JSON local con una fila por producto: `product`, `research`, `draft` y `photos` son rutas relativas al directorio del manifiesto. Cada archivo se valida y se conserva mediante el Worker existente. No se generan nuevos borradores automáticamente ni se consulta WooCommerce en este comando.

```sh
python -m src.commerce_evolution_engine.daily_catalog --root /ruta/persistente/state --tenant casa-viva --manifest /ruta/lote.json --daily-limit 10
```

Repetir el comando al arrancar el equipo o mediante un programador local autorizado. No borrar `state`: incluye SQLite, eventos y objetos inmutables. Límite por tenant/día UTC de intentos, no de productos terminados. Un trabajo interrumpido recupera su turno cuando expira su lease (300 segundos), hasta el máximo de intentos existente. Entradas idénticas reutilizan el mismo trabajo; cambios en contenido o imágenes crean otro. Las entradas inválidas se reportan por índice del manifiesto. El límite se debe mantener fijo entre invocaciones. No hay publicación, generación facturable ni cambios de inventario.

## Evidencia local 19-nov-2026

Lote con los tres expedientes reales ya preparados (sin copiar fotos privadas al repositorio): KM-3018 y KM-9013 quedaron `awaiting_review`, Sankey FN-17BAT10 quedó `blocked`. Segunda invocación idéntica: cero trabajos nuevos ejecutados, mismos tres IDs. Los resultados no constituyen aprobación comercial ni canonicalidad de los IDs de NEXO. Las pruebas sintéticas también verifican persistencia del límite diario tras reinstanciar Worker y avance al día próximo. Pendiente programador en equipo/servidor permanente, ingestión de datos y fuentes, generación gratuita real y renderización comercial aislada. No iniciar radar ni inventario.
