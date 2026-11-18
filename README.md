# Commerce Evolution Engine

**Auditor de catálogos y base abierta para agentes comerciales.**

Commerce Evolution Engine es un proyecto independiente nacido del trabajo con Casa Viva, diseñado para que cualquier comercio pueda auditar la calidad de sus fichas de producto y, por fases, automatizar mejoras con autorización y evidencia.

> **Estado: prototipo v0.1.0.** La primera entrega analiza archivos CSV sin acceder a tiendas, cambiar productos ni consumir APIs de pago. Las capturas visuales Playwright, el conector WooCommerce y el puente hacia servidores son objetivos futuros, **no están implementados**.

## Uso rápido

Requiere Python 3.10+; el auditor no necesita dependencias externas ni credenciales.

```bash
python -m unittest discover -s tests -v
python -m src.commerce_evolution_engine.audit --input examples/products.csv --outdir results
```

Genera `results/report.json` y `results/priorities.csv`.

El CSV admite `id,name,description,short_description,images` y opcionalmente `sku,status,categories`. El campo `images` utiliza enlaces separados por `|`. También reconoce encabezados habituales de exportaciones WooCommerce: `ID,Name,Description,Short description,Images,SKU,Published,Categories`.

## Qué hace realmente v0.1

- Detecta campos vacíos, títulos demasiado breves o genéricos, descripciones insuficientes y menos de cuatro referencias de imagen.
- Asigna una puntuación orientativa de 0 a 100 para priorizar revisión humana.
- **No** comprueba la calidad visual de las fotos, la veracidad de las especificaciones ni resultados SEO.
- **No** modifica el CSV original, WooCommerce ni ningún otro sistema.

## Como skill o agente

La skill está en [`.agents/skills/catalog-auditor/SKILL.md`](.agents/skills/catalog-auditor/SKILL.md). Lee [AGENTS.md](AGENTS.md) y [docs/AGENTS_INSTALL.md](docs/AGENTS_INSTALL.md) antes de usarla con tu asistente. La detección automática depende del programa agente utilizado.

## Principios

**Solo lectura por defecto**; ninguna publicación, cambio de precios, inventario, órdenes, comisiones o cobros sin autorización explícita y pruebas. Sin credenciales, datos de clientes ni fotografías privadas en el repositorio. Nunca inventar características de productos.

## Documentación

- [Arquitectura](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Instalación de agentes](docs/AGENTS_INSTALL.md)
- [Seguridad](SECURITY.md)
- [Licencia MIT](LICENSE)

La marca Casa Viva y sus fotografías no forman parte de esta licencia.
