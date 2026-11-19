# Four Image Agent — diseño y MVP de planificación v0.1

**Prioridad activa.** El motor `four_image_planner.py` planifica cuatro imágenes con evidencia, crea instrucciones y bloquea originales sin confirmar. **No genera fotografías todavía.** La ejecución/QA visual y el integrador con un proveedor de imágenes requieren una fase técnica separada, sin alterar producción.

## Contrato visual fijo
| Slot | Uso | Regla |
| --- | --- | --- |
| 01 HERO | Catálogo 1:1 | Foto real del artículo, blanco puro, sin textos, logos superpuestos, personas, precios ni accesorios ficticios |
| 02 LIFESTYLE | 4:5 Meta / galería | Resultado humano en situación real, fiel a la referencia exacta. No cambiar estructura ni aparatos |
| 03 BENEFITS | 4:5 Meta / galería | Escena del artículo real y máximo tres datos verificables; titular corto + dos hechos es mejor por defecto. **Texto/vector montado después**, no dibujado por el generador |
| 04 DETAILS | 4:5 galería | Recortes y detalle de piezas reales, cotas o dimensiones solo cuando constan; evitar alucinaciones de conectores, controles y botones |

El formato 9:16 para historias es una **exportación adicional**, no reemplaza las cuatro piezas maestras. Nunca precios en las fotos; conservar originales y metadatos de procedencia.

## Paso 1: Evidencia y producto
Exigir foto original con permiso de uso, identificador exacto, marca/modelo, color/variante, etiqueta técnica, catálogo o manual. Verificar imagen humana: no basta checksum ni una URL de foto ajena. Si faltan vistas de detalles, pedirlas: la IA no debe fingirlas.

## Paso 2: Datos de compra no repetidos
- Título: identificar producto/modelo y diferenciarlo. Sin recitar ficha.
- Resumen breve: deseo/resultados, sin repetir lista completa de especificaciones.
- Tabla técnica: datos concretos, una vez.
- Descripción larga: para quién sirve, uso, límites, instalación y FAQ; solo preguntas no contestadas arriba.
- Infografía: una promesa principal y máximo dos datos verificados, no repetir todo el folleto.
- Preguntas de clientes: módulo futuro opcional, con consentimiento y desidentificación. Sirve para **priorizar FAQ y fotos**, no para inventar especificaciones o modificar stock.
- Un `fact_id` representa cada dato verificable; reutilizarlo visualmente no equivale a repetir texto en todas las secciones.

## Paso 3: Motor de imágenes por estrategia y coste
1. **Sin gasto adicional (primero):** reutilizar foto original, recorte gratuito del VPS Casa Viva cuando esté permitido/fiable, composición blanca, Pillow/SVG para diagramas y tipografía. Revisar halos y detalles finos.
2. **Edición IA premium (opcional):** un proveedor que acepte imagen de referencia real, calidad/fidelidad y resultados exportables; mantener adaptadores OpenAI/Cloudflare/Higgsfield intercambiables. Coste variable y cuota sin garantía. En Casa Viva EVO-001 las rutas de generación facturables están **bloqueadas**, no desbloquear automáticamente ni asumir que una suscripción ChatGPT incluye API.
3. **IA local (experimentación):** evaluar compatibilidad de GPU, memoria y calidad antes de proponer Stable Diffusion/FLUX. Ollama/Qwen de código **no** genera fotografías comerciales por sí mismo. No prometer cuatro imágenes fotográficas de alta calidad offline en una máquina sin recursos medidos.
4. **Fallback:** si falla la fidelidad, usar únicamente composición de fotografía real, no inventar una escena.

## Paso 4: QA fuerte (cada imagen)
- Correspondencia modelo/variante, materiales, geometría, color y número de piezas.
- Texto y números contra manifiesto de evidencias; no deformar etiquetas de fábrica.
- Resolución/foco/recorte, proporción, halo/fondo, legibilidad 360 px.
- Consistencia de las cuatro; no repetir la misma vista como si fueran fotos distintas.
- Datos técnicos y promesas por uso verificables; variante correcta.
- QA visual con comparación lado a lado y humano aprobado; resultados no confiables nunca se autopublican.

## Paso 5: salida y reversión
Directorio privado `tenant/product/revision`:
`source/,` `manifest.json`, `research.json`, `01-hero.webp`, `02-lifestyle.webp`, `03-benefits.webp`, `04-details.webp`, `qa.json`, `approval.json`. Puede haber slots pendientes: nunca archivos ficticios.
Al aprobar: preparar borrador de WordPress con versión y snapshot antes de cambios. Publicación, precios, stock, cobros y pedidos permanecen fuera de alcance hasta autorización expresa.

## CLI actual
```bash
python -m src.commerce_evolution_engine.four_image_planner --input examples/four-image-product.example.json --outdir results/four-images
```
Genera `four-images-plan.json` que por defecto estará bloqueado al faltar foto verificada. No renderiza nada y no gasta créditos.

## Integración con el motor Casa Viva existente
Reutilizar `CVD_Content_Studio`, `CVD_Photo_AI` y el VPS `casaviva-imagen` sin reemplazar sus políticas. `CVD_Photo_AI::vps_image()` devuelve `CVD_Content_Policy::billable()` durante EVO-001; lo que tenga coste está cerrado. `vps_recorte()` existe y fue probado, pero tuvo halos pese a marcar `fiable=true` en una prueba real. Al incluirlo, mantener revisión humana. Nunca eliminar esa compuerta para avanzar más deprisa.

## Fallos por adelantado
- API de pago sin cuota verificada; facturación inadvertida.
- Modelo visual equivocado a partir de una fotografía genérica encontrada en buscador.
- Fondo eliminado con halos o aspas/partes finas recortadas.
- Imágenes con interruptores, enchufes, dedos o manos extra.
- Producto demasiado pequeño en móvil o tipografía ilegible.
- Repetición editorial de especificaciones.
- Producto y variantes cruzados por SKU.
- Mismo producto retrabajado en bucle por ausencia de huella idempotente.
- Cambio de imagen principal que rompe galería/historial.
- Fotos de clientes/proveedores filtradas en repo público.
- Promesa de stock/garantía/voltaje basada en fichas contradictorias.

## Definición de terminado
- Una unidad real con fotos originales aportadas y permiso registrado.
- Cuatro imágenes distintas y fieles (o bloqueo justificado) y QA en móvil.
- Contenido SEO no redundante y verificado.
- Ejecución reproducible, costo medido y reversión.
- Flujo de revisión aprobado en Casa Viva sin publicar automáticamente.
- Pruebas de idempotencia, fallos de proveedor, límites de gasto y seguridad.

## QA técnico offline publicado
`src/commerce_evolution_engine/photo_quality.py` valida la presencia de los cuatro archivos, resolución mínima, relación de aspecto, cuatro esquinas blancas en HERO y hashes duplicados. **No** detecta alucinaciones visuales ni verifica exactitud de la foto y los datos; eso exige contraste humano con los originales.

```bash
python -m src.commerce_evolution_engine.photo_quality --dir results/photos --report results/photos/qa-report.json
```

Mientras falten 02-LIFESTYLE o 04-DETAILS, `technical_ready=false` es correcto. Pruebas `tests/test_photo_quality.py` (Pillow opcional) publicadas, ejecución pendiente de certificar.
