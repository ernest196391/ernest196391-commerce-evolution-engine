# Proveedores de imagen y coste — evaluación 2026-11-18

## Condición operativa
**Presupuesto incremental por defecto = 0 USD.** Ninguna integración debe iniciar cobros, habilitar claves o usar prueba gratis de servicio externo sin una verificación explícita de cuota, licencia, destino y tratamiento de datos.

## Selección por tipo de imagen
| Pieza | Primera opción | Alternativa | Riesgo |
| --- | --- | --- | --- |
| 01 Hero | Foto real original + recorte/composición blanca local | Edición IA supervisada | Halos, aspas finas, recorte, modelo alterado |
| 02 Lifestyle | Editor IA con referencia, **requiere habilitar presupuesto** | Foto real del proveedor con permiso y contexto ya correcto | Producto deformado, persona/escena falsos |
| 03 Beneficios | Escena real + overlays SVG/Pillow locales | Editor IA con referencia y espacio vacío; textos fuera del modelo | Texto mal escrito, datos no verificados |
| 04 Detalles | Fotografía original/recortes reales + cotas vectoriales | Toma adicional al proveedor | Inventar puertos/controles o dimensiones |

## Reuso Casa Viva
Core `CVD_Photo_AI` ya conoce `cloudflare`, `vps`, `openai` y `higgsfield`, según claves disponibles. La vía `vps_image()` está bloqueada por la política `CVD_Content_Policy::billable()` de EVO-001. `vps_recorte()` ejecuta recorte gratuito; una prueba real devolvió `fiable=true` pero dejó halo. Mantener revisión humana y bloqueo de rutas pagadas.

## Opciones de tecnología
- **Python Pillow y SVG:** compone lienzos, encuadres y textos vectoriales; no inventa escenas ni genera fotos fotorrealistas. Gratuidad de licencia no significa coste de infraestructura cero en todo escenario.
- **Rembg:** proyecto abierto para fondo, puede requerir descargar pesos de modelo que tienen licencia independiente; revisar licencia y rendimiento antes de incorporarlo.
  Fuente: https://github.com/danielgatis/rembg
- **OpenAI Image API:** genera/edita con referencia, API independiente de ChatGPT y facturable según uso. Precios dinámicos; revisar antes de habilitar.
  Fuentes: https://developers.openai.com/api/docs/guides/image-generation y https://developers.openai.com/api/docs/pricing
- **Gemini image generation:** tarifas y disponibilidad de free tier dependen del modelo y de la cuenta. No asumir gratis ilimitado para imágenes.
  Fuente: https://ai.google.dev/gemini-api/docs/pricing
- **Cloudflare Workers AI:** integración existente en Core, cuota/modelo/costes deben verificarse por cuenta y resultado; no prometer fidelidad de producto sin pruebas.
- **Higgsfield:** conexión posible, pero precios, derechos y cuota no verificados para esta sesión. No seleccionar automáticamente.

## Objetivo de interoperabilidad
Interfaz futura `ImageProvider.generate(reference_images[],prompt,slot,policy,budget)->result` con `provider_id,model,model_version,request_id,cost_actual,rights,output_hash,quality_assessment`. No crear adaptador que haga llamadas reales hasta pruebas de fallo y autorización.

## Costes y límites
- `max_usd_per_job=0`, `max_billable_calls=0` por defecto.
- Máximo 1 corrida por SKU+versión/fecha cuando exista job incremental; idempotencia por hash de fuente/manifiesto.
- Detectar límites y facturación antes de enviar solicitud; detener ante 429, timeout o pérdida de estado, sin reintento que pueda facturar de nuevo.
- Mantener fase `preview`, revisión humana, restauración de galería y política de no sobreescribir originales.
