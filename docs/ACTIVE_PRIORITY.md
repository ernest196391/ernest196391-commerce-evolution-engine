# CHECKPOINT — Prioridad del producto (2026-11-18)

## Decisión del propietario
**El trabajo activo y prioritario es completar el agente de mejora diaria del catálogo:** fotografías, títulos, SEO y descripciones verificables de producto para Casa Viva.

**No avanzar por ahora** en la ingesta de WhatsApp, revisión nocturna de grupos, radar de proveedores, despublicación por agotamiento o búsqueda continua de productos nuevos. Esas ideas se conservan como **fase posterior** y no deben competir por tiempo, permisos ni coste del agente principal. La autorización declarada sobre las ofertas de proveedores no equivale a que ya exista un conector ni un flujo de acceso técnicamente configurado.

## Secuencia obligatoria
1. Auditar visualmente y editorialmente una muestra de productos reales de Casa Viva, comparando títulos, textos y fotografías existentes.
2. Establecer rúbricas útiles: fidelidad a la foto real, datos técnicos verificados, título SEO, descripción completa, descripción corta, fotos y diseño móvil. No confundir «campo no vacío» con calidad.
3. Crear borradores de mejora, con imágenes y textos sujetos a revisión; nunca inventar prestaciones ni cambiar atributos de la pieza.
4. Aprobar un producto piloto con imágenes reales y texto; garantizar que las mejoras se pueden revertir.
5. Construir proceso incremental de mejora **diaria** con priorización, control de duplicados, coste cero por defecto, logs y revisión/aprobación. No permitir publicación autónoma antes de certificarla.
6. Solo tras completar el agente principal, pasar al radar nocturno de proveedores y al buscador de nuevos productos.

## Reutilización transversal — desde ahora
La arquitectura del agente principal **sí debe preparar** componentes reutilizables para los futuros agentes:
- Identidad de comercio (`tenant_id`), tienda, SKU, variante, proveedor y fuente.
- Evidencias y grado de confianza: observado, suministrado, externo, inferido, desconocido.
- Registro incremental de eventos y observaciones; idempotencia y checkpoints.
- Cola de tareas con estados, prioridad, coste y correlación de fuente.
- Motor de políticas y permisos específicos, operaciones de lectura vs escritura, reversión, `dry_run`, apagado rápido.
- Conectores encapsulados, no lógica específica de Casa Viva incrustada en la skill genérica.
- Puertas de revisión humana para fotos, títulos, stock, precios y publicación.
- Panel de resultados móvil-first y artefactos comprobables.

Esto **no autoriza implementar ya** conectores de chats, stock o exploración. Solo definir interfaces limpias y no cerrar puertas arquitectónicas.

## Estado verificable
- Repositorio público y código del auditor CSV publicados.
- Código Playwright y workflow manual publicados; **ejecución real de capturas no verificada**.
- Radar offline prototipo y documentación de proveedores publicados; **postergados**. No se han conectado chats ni habilitado cambios de inventario.
- No hay agente diario completo o autónomo implementado todavía.
- Casa Viva Core v3.14.172: cinco archivos críticos coincidieron con GitHub en auditoría anterior; 893 productos publicados, 12 borradores, 292 variaciones. 893 con descripción principal y corta **rellenadas**, pero no clasificadas como buenas. Uno sin imagen principal asignada.
- Mantener protección de producción, stock, pedidos, credenciales, caja y cobros.

## Qué debe hacer el próximo agente al retomar
Leer primero `AGENTS.md`, este `docs/ACTIVE_PRIORITY.md`, `docs/VISUAL_AUDIT.md`, `docs/ROADMAP.md` y `SECURITY.md`. Trabajar directamente en el **agente diario de calidad de catálogo**, no en Supplier Radar. Comparar y verificar implementaciones antes de afirmar despliegues o pruebas.

## Definición de terminado para el agente principal
Ejemplo real aprobado; pruebas de seguridad y regresión; ejecución diaria incremental reproducible; resultados antes/después; trazabilidad del origen; mecanismo de revisión y reversión; coste verificable; documentación de instalación y operación para otros comercios. La publicación automática solo se podrá habilitar con autorización separada y pruebas específicas.
