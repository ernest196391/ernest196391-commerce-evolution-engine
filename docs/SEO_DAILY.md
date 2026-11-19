# B08 — SEO público incremental

Ejecutar con el mismo directorio persistente del Worker:

```sh
python -m src.commerce_evolution_engine.seo_daily --root /ruta/state --tenant casa-viva --origin https://casaviva.company --url https://casaviva.company/producto/ventilador-sankey-fn17bat10-recargable-16/ --daily-limit 8 --tick-limit 2
```

Máximo ocho URLs expresamente autorizadas por manifiesto, ocho intentos por tenant y día UTC. Manifiesto y presupuesto fijos durante ese día. Cada consulta reserva presupuesto antes de salir a la red; expiración de lease a 120 segundos, sin repetir éxitos durables el mismo día. Si se pierde energía entre GET y checkpoint puede repetirse el GET tras expirar el lease, dentro del presupuesto. Prioriza URLs sin éxito previo o de auditoría más antigua al cambiar de día. Compara galerías entre resultados completados del día, incluso en ticks distintos. No confundir resultados parciales con auditoría completa.

No se ha instalado programador remoto ni desplegado a producción. Requiere lxml y almacenamiento persistente; conservar SQLite y objetos. Pruebas locales: 53/53, incluida interrupción simulada, presupuesto persistente, rotación y deduplicación. Sin nuevas consultas reales en B08, sin llamadas facturables, sin modificar WooCommerce. No inicia radar ni inventario.
