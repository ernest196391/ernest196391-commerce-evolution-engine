# Descubrimiento incremental de fichas públicas

`python -m src.commerce_evolution_engine.catalog_discovery --root /ruta/persistente/state --origin https://casaviva.company --tenant casa-viva --max-pages 2`

Lee únicamente Woo Store API con GET, sin credenciales, 20 productos por página ordenados por ID. La respuesta se limita a 4 MiB; se valida el encabezado de paginación. Guarda solo identidad, texto e IDs de adjuntos observados; no precio, stock, pedidos ni clientes. No considera la lectura canónica para escribir. El cursor avanza en la misma transacción SQLite que las observaciones y tras persistir los objetos. Una interrupción repite la página no confirmada. Al finalizar el recorrido vuelve a página 1 la próxima vez, para detectar cambios; el catálogo puede variar durante el recorrido, por lo que se requiere reconciliación periódica y no se infieren eliminaciones. Cambios en texto o IDs de fotos producen otra huella; no detecta sustitución de bytes bajo el mismo ID. La lista pending contiene observaciones para investigación, no trabajos aprobados ni una cola de publicaciones. No certifica estética, semántica ni veracidad. El siguiente paso es gestionar el estado de investigación por huella y vincular expedientes al agente diario.

Prueba real 19-nov-2026: página 1 con 20 observaciones; nueva instancia sobre la misma base continuó página 2 con otras 20, total 40. No se hicieron escrituras remotas ni se invocó IA. Prueba sintética de interrupción y reanudación, detección de cambio, origen aislado y ausencia de autenticación.

Contrato oficial: https://developer.woocommerce.com/docs/apis/store-api/resources-endpoints/products y https://developer.woocommerce.com/docs/apis/store-api/guiding-principles.
