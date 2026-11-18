# Commerce Evolution Engine

**Herramientas abiertas de auditoría de catálogos, inspección visual pública y skills para agentes comerciales.**

Proyecto independiente nacido del trabajo con Casa Viva, diseñado para cualquier comercio que quiera evaluar fichas de producto antes de automatizar mejoras.

> **Estado v0.2 (experimental).** Está implementado el análisis CSV sin dependencias externas y el auditor Playwright de páginas públicas. No está implementado el conector WooCommerce autenticado, el acceso remoto a servidores, ni la revisión estética con IA. No se han certificado aún ejecuciones visuales en producción.

## Auditor CSV — v0.1

Requiere Python 3.10+:

```bash
python -m unittest discover -s tests -v
python -m src.commerce_evolution_engine.audit --input examples/products.csv --outdir results
```

Genera `results/report.json` y `results/priorities.csv`. Acepta campos `id,name,description,short_description,images` o columnas equivalentes de CSV WooCommerce. El campo imágenes acepta `|` o comas. Los scores son **heurísticos, no una certificación SEO**.

## Auditor visual público — v0.2

Lee primero [la guía de auditoría visual](docs/VISUAL_AUDIT.md). Playwright necesita instalación opcional y descarga del navegador:

```bash
python -m pip install "playwright>=1.56,<2"
python -m playwright install chromium
python -m src.commerce_evolution_engine.visual_audit --urls examples/public-urls.txt --host casaviva.company --outdir results/visual
```

Genera capturas en 360, 390 y 1280 píxeles, además de `visual-report.json` y `visual-report.csv`. Señala títulos vacíos, H1, desbordamiento, imágenes rotas y `alt` ausente. **No** juzga automáticamente la calidad estética ni verifica afirmaciones técnicas.

### GitHub Actions

- `Test auditor (offline)`: pruebas locales sin servicios externos.
- `Visual audit (manual)`: requiere ejecutarlo expresamente desde Actions. Consume minutos de GitHub Actions; confirmar presupuesto disponible antes de iniciarlo. No se ejecuta con cada push.

## Skills

- [catalog-auditor](.agents/skills/catalog-auditor/SKILL.md): calidad básica de CSV.
- [visual-auditor](.agents/skills/visual-auditor/SKILL.md): capturas públicas y revisión humana.

Consulta [AGENTS.md](AGENTS.md), [instalación](docs/AGENTS_INSTALL.md), [seguridad](SECURITY.md), [arquitectura](docs/ARCHITECTURE.md) y [roadmap](docs/ROADMAP.md).

## Garantías y límites

- Solo lectura de tiendas: ningún cambio de precios, inventario, pedidos, fichas o fotos.
- No incluir credenciales, clientes o fotografías privadas.
- Nunca inventar características de productos.
- No ejecutar diagnósticos remotos sin los permisos pertinentes.
- Sin APIs de pago; Playwright local y GitHub Actions consumen recursos informáticos, que deben revisarse antes de ejecutarse.

Licencia [MIT](LICENSE) para el código; no se transfieren marcas ni material comercial de terceros.
