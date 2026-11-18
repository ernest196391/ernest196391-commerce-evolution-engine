# Auditoría visual pública v0.2 — Playwright

## Alcance
Inspecciona únicamente URLs HTTPS públicas de un dominio autorizado; no usa sesión, cookies autenticadas, contraseñas, API WooCommerce, ventas o datos personales.

Captura pantalla **viewport visible**, sin scroll completo, en tres anchos: 360, 390 y 1280. Registra title, H1 visible, errores HTTP, desbordamiento horizontal, imágenes visibles sin carga o alt y longitud aproximada de texto principal. Genera JSON y CSV de hallazgos. Son **indicadores técnicos**, no calificaciones fotográficas ni SEO profesional.

## Instalación opcional local (genera descargas)
```bash
python -m pip install "playwright>=1.56,<2"
python -m playwright install chromium
python -m src.commerce_evolution_engine.visual_audit --urls examples/public-urls.txt --host casaviva.company --outdir results/visual
```
Necesita acceso de red, recursos de CPU, descarga de Chromium y consentimiento del administrador del sitio que se examine. No hay API de pago asociada.

## GitHub Actions — ejecución manual
En `Actions → Visual audit (manual) → Run workflow`. Se auditan solo tres URLs estáticas de `examples/public-urls.txt`. No se activa por push ni cron. Las capturas y JSON/CSV se guardan como artefacto de GitHub por 3 días. Ejecutarlo consume minutos/recursos de GitHub Actions; **no se ha comprobado el saldo de la cuenta**, así que confirma costes antes de pulsar Run workflow. No usa secretos ni despliega.

## Límites de seguridad
- Dominio exacto mediante `--host`, sin redirect fuera del dominio.
- URLs explícitas: máximo 8 por ejecución; sin query strings ni fragmentos.
- Evita administración, carrito, checkout, cuenta, control y pedidos.
- No inspecciona ni almacena páginas que requieran login.
- No descubre enlaces ilimitadamente ni navega dentro del checkout.
- No compromete el sitio, pero las solicitudes GET sí generan tráfico normal.
- No usar sobre comercios ajenos sin permiso.
- Los artefactos pueden incluir contenido público cambiante: revisa las capturas antes de compartirlas.

## Lo que falta
Revisión automatizada por IA del *aspecto* de la fotografía, análisis SEO contextual y conector WooCommerce. No confundir el mero recuento de imágenes con su calidad.
