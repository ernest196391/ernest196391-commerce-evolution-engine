# Auditoría de prácticas Amazon y adaptación a Commerce Evolution Engine

Fecha de investigación: 2026-11-18. Fuentes primarias: documentación de Amazon Seller Central y Sell on Amazon. Este documento es una **investigación de prácticas y requisitos publicados**, no una evaluación de rendimiento de cuentas de vendedor, un estudio completo de ASIN concretos ni una autorización para copiar contenidos.

## Hallazgos contrastados

### 1. Título = identificación + capacidad de búsqueda
Amazon anunció nuevos requisitos efectivos el 21 de enero de 2025: en la mayoría de categorías, el título no puede superar 200 caracteres ni repetir la misma palabra más de dos veces, con excepciones y diferencias por categoría.
Fuentes:
- https://sellercentral.amazon.com/seller-forums/discussions/t/6dfa6a0c-a331-45cb-966e-1b2ac2973b0d
- https://sellercentral.amazon.com/gp/help/external/YTR6SYGFA5E3EQC

**Adaptación propia:** no imponemos mecánicamente 200 caracteres ni trasladamos las políticas Amazon a WooCommerce. Proponemos títulos españoles claros, cortos y diferenciables: `Tipo + marca + modelo + atributo decisivo + presentación` solo cuando exista evidencia. En móvil, comprobar truncamiento.

### 2. Imagen principal fiel; galería explica
Las normas Amazon para imagen principal incluyen fondo blanco puro RGB 255,255,255 y producto ocupando aproximadamente 85 % de la imagen (según categoría).
- https://sellercentral.amazon.com/gp/help/external/G1881
- https://sellercentral.amazon.com/seller-forums/discussions/t/ab884127-f9b4-4053-8096-4991e1d60d1f

**Adaptación Casa Viva:** foto principal fiel y sin marcas superpuestas; composición de fondo limpio. Galería de cuatro funciones: `hero producto`, `uso realista`, `prestaciones verificadas`, `detalle/medidas`. Las cuatro imágenes son un estándar editorial propuesto para Casa Viva, **no una obligación general de Amazon**. No alterar color, forma, tamaño, modelo, accesorios incluidos o funciones en fotos generadas. La foto original verificada manda.

### 3. Bullets, texto y contenido enriquecido
Amazon destaca listas de ventajas verificables, descripciones útiles, imágenes mejoradas, módulos A+ y comparaciones.
- https://sell.amazon.com/blog/amazon-product-listings
- https://sell.amazon.com/tools/a-content
- https://sell.amazon.com/blog/improve-conversion-rates

**Adaptación:** respuesta rápida antes del desplazamiento en móvil: qué es, compatibilidad, qué incluye, cuál es el resultado útil, límites y garantías confirmadas. La ficha extendida amplía especificaciones, medidas y uso. No escribir promesas sin respaldo.

### 4. Investigación de búsquedas y aprendizaje
Amazon recomienda investigar palabras clave reales y evitar repetirlas artificialmente; presenta herramientas Product Opportunity Explorer y experimentos de contenido para ciertos vendedores.
- https://sell.amazon.com/blog/amazon-keyword-research
- https://sell.amazon.com/tools/product-opportunity-explorer
- https://sell.amazon.com/tools/manage-your-experiments

**Adaptación:** registrar frases de búsqueda locales, preguntas del comprador y taxonomía de tienda. No afirmar que una palabra clave es «tendencia» sin observación. Preparar pruebas controladas de títulos/fotos, pero **no** activar cambios automáticos de SEO sin revisar resultados y datos suficientes.

## Diferencias importantes
Amazon es un marketplace con políticas y catálogo compartido. Casa Viva controla su sitio WooCommerce y tiene condiciones propias de disponibilidad, entrega y pago en Cuba. El agente no puede usar como norma universal cada política Seller Central ni inferir que una presentación de Amazon prueba la ficha del proveedor cubano. Las reseñas de terceros son señales sobre dudas y experiencia, no verifican prestaciones de nuestra unidad.

## Pipeline nuevo obligatorio: investigación antes de creación

1. **Identificación:** nombre original, fotos reales, marca, modelo, número de parte, variante, empaque y documentación. Registrar nivel de confianza.
2. **Coincidencia:** exigir prueba para `modelo_exacto` (marca+modelo+variante relevantes). Un producto `similar` se usa exclusivamente para estudiar presentación/estructura, jamás copiar especificaciones.
3. **Búsqueda de fuentes:** fabricante/manual/etiqueta del artículo; ficha del proveedor; luego recursos oficiales, documentación técnica y comparables comerciales, con URL, fecha, captura o nota verificable.
4. **Extracción de afirmaciones:** cada capacidad, medida, material, autonomía, potencia, accesorio, garantía o recomendación tiene `value,unit,source,evidence,confidence,status`.
5. **Resolución de conflictos:** fabricante y unidad real prevalecen cuando corresponda; contradicciones quedan pendientes. Si faltan datos críticos, no publicarlos como hechos.
6. **Benchmark comercial:** comparar organización, titulares, fotos, bullets, preguntas frecuentes y UX de Amazon y comercios relevantes, sin copiar material protegido.
7. **Borrador:** título SEO, descripción corta, ficha completa, preguntas frecuentes y plan de cuatro fotos. Incluir `before/after`, checklist y dudas abiertas.
8. **Revisión:** humana y técnica. Nunca convertir automáticamente en publicado. Mantener reversión y log de procedencia.
9. **Evaluación continua:** medir CTR, búsqueda, conversión, devoluciones y preguntas por SKU solo cuando existan métricas fiables y consentimiento, sin inferir causalidad sin controles.

## Salida mínima de un producto investigado

`tenant_id,product_id,sku,manufacturer,model,variant,identity_confidence,sources[],claims[],missing_facts[],benchmark_notes[],seo_title_draft,short_description_draft,long_description_draft,image_plan[],approval_status,source_snapshot_hash`.

## Protección legal y operativa
- Las imágenes, videos, títulos y textos de vendedores en Amazon no se redistribuyen ni se reutilizan sin derechos; se documentan **patrones y principios**, no copias.
- Sin navegación autenticada, scraping masivo, extracción de reseñas prohibida por términos, circunvención de controles ni APIs de pago.
- Investigación actualizada al momento de cada ejecución cuando la conexión lo permita; fechar cada fuente.
- Nunca inferir prestaciones de un modelo solo porque otro modelo similar las tenga.
- La primera ejecución es investigación y borrador, sin cambios en WooCommerce.

## Próxima aceptación
Elegir un producto real de Casa Viva, fotografiado y con modelo verificable; documentar cinco afirmaciones clave con fuentes y evidencia; comparar estructura con dos referencias de mercado; preparar ficha y cuatro imágenes fieles; hacer revisión antes/después en móvil; publicar **solo tras autorización separada**.
