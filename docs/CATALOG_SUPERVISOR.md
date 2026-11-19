# Supervisor visual y editorial offline

Reutiliza planificador, investigación estructural, auditor editorial y QA técnico. Recibe tres JSON locales: producto (contrato del planificador), investigación (contrato de research_gate más tenant_id y product_id), borrador (columnas de CSV normalizadas, mismo id) y carpeta de imágenes PNG.

```bash
python -m src.commerce_evolution_engine.catalog_supervisor --product product.json --research research.json --draft draft.json --photos photos --report review.json
```

Tres piezas por defecto; cuarta solo con concepto y evidencia. Un estado awaiting_human_review significa únicamente que no hay bloqueo estructural conocido. Los criterios de fidelidad, derechos, seguridad, semántica, textos y fotos permanecen not_verified hasta una revisión humana comparativa. La huella identifica el candidato y los hashes técnicos, no constituye firma de aprobación. No hay autorización, publicación ni llamada de IA. Las fuentes y el texto libre pueden contener errores; revisar afirmaciones una por una, no confiar en un score. Mantener archivos locales privados y no publicar fotos originales en el repositorio público.

Siguiente: piloto real, revisión humana documentada y recuperación incremental; integraciones de escritura fuera de alcance.
