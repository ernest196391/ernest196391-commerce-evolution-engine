# Commerce Evolution Engine

**Herramientas abiertas de auditoría de catálogos, inspección visual pública, propuestas de stock y skills para agentes comerciales.**

Proyecto independiente nacido del trabajo con Casa Viva, diseñado para cualquier comercio que quiera evaluar fichas de producto antes de automatizar mejoras.

> **Estado v0.2 (experimental).** Está implementado el análisis CSV sin dependencias externas y el auditor Playwright de páginas públicas. No está implementado el conector WooCommerce autenticado, el acceso remoto a servidores, ni la revisión estética con IA. No se han certificado aún ejecuciones visuales en producción.

## Prioridad actual: agente de mejora diaria de productos

**Objetivo único activo:** mejorar progresivamente fotografías reales, títulos SEO, descripción corta y completa del catálogo, con evidencia, aprobación y reversión. Consultar [checkpoint de prioridad](docs/ACTIVE_PRIORITY.md) y [roadmap actualizado](docs/ROADMAP.md).

El radar de proveedores, ingesta de chats WhatsApp, agotados y descubrimiento continuo **se han pospuesto a una fase posterior por decisión del propietario**. Su prototipo y documentación se conservan como referencia, pero no deben distraer ni activar tareas. Los componentes comunes (permisos, fuentes, SKU/variante, cola, evidencia, coste y auditoría) sí deben diseñarse para reutilización.

## Motor editorial del agente principal — implementado, pendiente de validación CI

La nueva [rúbrica editorial](docs/EDITORIAL_QUALITY.md) detecta títulos débiles, descripciones genéricas, textos cortos duplicados, referencias fotográficas insuficientes y afirmaciones técnicas que necesitan fuente. No inventa datos ni modifica productos.

```bash
python -m src.commerce_evolution_engine.editorial_review --input examples/products.csv --outdir results/editorial --tenant demo
```

Incluye [skill editorial-quality](.agents/skills/editorial-quality/SKILL.md) y pruebas de regresión. La validación de CI y una ejecución contra un catálogo real todavía están pendientes.

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

## Fase posterior, en pausa: radar de proveedores — prototipo offline

Este módulo produce **propuestas de revisión**, nunca cambios en el catálogo. Usa observaciones sintéticas o exportadas con permiso, por proveedor, SKU y variante:

```bash
python -m src.commerce_evolution_engine.supplier_radar --input examples/supplier-observations.example.json --outdir results/suppliers
```

Lee [Radar y estado de productos](docs/SUPPLIER_RADAR.md), [Delegación de permisos](docs/AUTONOMY_AND_PERMISSIONS.md), [Mapa multiagente](docs/MULTI_AGENT_PRODUCT_MAP.md) y la [skill supplier-radar](.agents/skills/supplier-radar/SKILL.md). El acceso automático a grupos de WhatsApp, la revisión nocturna programada y el conector WooCommerce **aún no existen**.

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
