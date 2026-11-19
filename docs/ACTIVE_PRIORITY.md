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

## Avance del agente principal — evaluación editorial implementada

- Archivo `src/commerce_evolution_engine/editorial_review.py`: puntuación heurística de título, contenido, repetición, especificaciones, promesas y referencias de imagen.
- Pruebas `tests/test_editorial_review.py`: textos rellenos pero pobres; afirmaciones que necesitan fuente; identificador aislado por comercio; no modificación del archivo original.
- Skill `.agents/skills/editorial-quality/SKILL.md` y guía `docs/EDITORIAL_QUALITY.md` publicadas.
- **No se ha certificado aún CI ni ejecución con los 893 productos reales.** El contenedor de trabajo no dispone de acceso DNS a GitHub para clonar; archivos publicados y recuperables por conexión GitHub. No declarar pruebas verdes ni calidad real certificada.
- Próximo bloque efectivo: probar en CI, conseguir extracción autorizada del catálogo sin PII, evaluar muestra real, generar la primera ficha de antes/después con fotos originales, revisión y aprobación. No saltar hacia Supplier Radar.

## Ampliación necesaria: investigación de producto (Amazon como referencia)

Decisión de producto: antes de crear fotos, título SEO o descripciones, **investigar el modelo real y qué información está verificada**, contrastando fabricante/manual/fotos del proveedor con fuentes actuales. Amazon sirve como benchmark de presentación y preguntas de compra, no como prueba de características del producto de Casa Viva ni fuente para copiar fotografías/textos.

- Estudio oficial de prácticas Amazon: `docs/AMAZON_BENCHMARK_AND_PRODUCT_RESEARCH.md`.
- Skill de investigación: `.agents/skills/product-research/SKILL.md`.
- Validador estructural de evidencias: `src/commerce_evolution_engine/research_gate.py`.
- Pruebas unitarias: `tests/test_research_gate.py`; pendientes de CI/verificación en ejecución remota.
- **Límite actual:** aún no hay agente que investigue automáticamente la web ni que valide de verdad los documentos. La puerta de evidencias solo comprueba estructura, estados y que no se use una ficha comparable como base del modelo exacto.
- Siguiente: elegir modelo piloto con foto original, navegación/consulta actual verificable, expediente de fuentes, ficha y plan de cuatro fotografías; comparar con Amazon en estructura, no copiar.

## Bloque activo inmediato: generador de cuatro fotografías

Por decisión del propietario, **priorizar ahora la construcción del agente de cuatro fotografías**, no la exploración de proveedores. Las piezas son:
1. HERO 1:1 sobre blanco puro, artículo real idéntico, sin texto.
2. LIFESTYLE 4:5, humano utilizando el producto en contexto creíble.
3. BENEFITS 4:5, diagrama limpio del producto con 1 beneficio principal y máximo dos datos verificables, tipografía vectorial.
4. DETAILS 4:5, recortes o acercamientos de detalles reales, controles y dimensiones documentadas.

La redacción SEO acompaña al paquete pero tiene política de **no redundancia**: título = identificación, resumen = resultado de compra, tabla = datos técnicos una sola vez, texto extendido = usos/limitaciones/FAQ. Evitar repetir tamaño, autonomía y velocidades en cada sección.

Implementado en repositorio: `src/commerce_evolution_engine/four_image_planner.py` (manifiesto de cuatro slots, bloqueo de foto original sin confirmar, filtro de claims, fingerprint), `tests/test_four_image_planner.py`, `docs/FOUR_IMAGE_AGENT.md`, `.agents/skills/four-image-agent/SKILL.md`. **Aún no crea fotos ni conecta proveedor de generación.** No afirmar lo contrario.

**Reutilizar** recorte local de `CVD_Photo_AI::vps_recorte()`, `CVD_Content_Studio` y políticas de Core, sin desbloquear `vps_image()` que permanece cerrado por EVO-001. Mantener gasto 0, origen documentado, QA visual y aprobación humana.

**Futuro punto de entrada:** preguntas frecuentes de chats WhatsApp autorizados (anonimizadas) informan orden de fichas, FAQ y foco de imagen 03, pero no inicia ahora el agente de chats ni el radar de proveedores.

**Siguiente hito:** motor local de composición blanca y texto vectorial, adaptador de edición fiel a original bajo aprobación, QA de cuatro piezas y piloto con foto original real.

## Compositor fotográfico offline publicado

- `src/commerce_evolution_engine/photo_compositor.py`: a partir de un **recorte PNG aprobado**, compone de forma local `01-hero.png` (blanco) y `03-benefits.png` (tipografía real). No fabrica escenas ni altera el original. Dependencia opcional: Pillow.
- `tests/test_photo_compositor.py` y `examples/verified-photo-facts.example.json` agregados. No declarar pruebas aprobadas sin ejecutarlas con Pillow.
- `docs/IMAGE_PROVIDERS_AND_COST.md`: estrategia por pieza, modalidades sin pago vs premium opt-in, límites de facturación y revisión visual.
- Falta `02-lifestyle` con edición de referencia fiel y `04-details` con fotos reales adicionales; faltan primeras fotos originales para probar todo con un producto de Casa Viva.
- No desbloquear por atajo la ruta `CVD_Photo_AI::vps_image()` que EVO-001 tiene bloqueada por coste.

- `src/commerce_evolution_engine/photo_quality.py` y `tests/test_photo_quality.py` publicados para QA offline de cantidad/tamaño/duplicados. **Fidelidad a referencia original y legibilidad requieren revisión humana**; sin las cuatro piezas el QA debe bloquear.

## Qué debe hacer el próximo agente al retomar
Leer primero `AGENTS.md`, este `docs/ACTIVE_PRIORITY.md`, `docs/VISUAL_AUDIT.md`, `docs/ROADMAP.md` y `SECURITY.md`. Trabajar directamente en el **agente diario de calidad de catálogo**, no en Supplier Radar. Comparar y verificar implementaciones antes de afirmar despliegues o pruebas.

## Definición de terminado para el agente principal
Ejemplo real aprobado; pruebas de seguridad y regresión; ejecución diaria incremental reproducible; resultados antes/después; trazabilidad del origen; mecanismo de revisión y reversión; coste verificable; documentación de instalación y operación para otros comercios. La publicación automática solo se podrá habilitar con autorización separada y pruebas específicas.
