# Instalación en agentes

## OpenCode y herramientas compatibles

Clona o descarga el repositorio. Pide al agente: «Lee `AGENTS.md` y `.agents/skills/catalog-auditor/SKILL.md`; audita el CSV local en modo solo lectura». La detección automática de skills depende de la versión de la herramienta; si no detecta la carpeta, señala manualmente el archivo.

## ChatGPT

Adjunta el CSV sin información de clientes y la skill, o facilita acceso de lectura a este repositorio. El proyecto no concede por sí mismo acceso a WordPress, a tu computadora o a servidores.

## Windows

Usa Python 3.10+; desde PowerShell en el repositorio ejecuta:

```powershell
python -m unittest discover -s tests -v
python -m src.commerce_evolution_engine.audit --input examples/products.csv --outdir results
```

## VPS

En esta fase no instales servicios ni programes cron. Las futuras tareas remotas necesitan usuario sin privilegios, aislamiento y presupuesto certificado; nunca root por comodidad.
