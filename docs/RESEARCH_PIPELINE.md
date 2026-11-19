# Investigación incremental vinculada a fichas reales

`python -m src.commerce_evolution_engine.research_pipeline --root /ruta/persistente/state --tenant casa-viva --limit 10`

Usa las observaciones de `catalog_discovery` y genera expedientes por tenant, producto y huella. Contienen nombre observado (no identidad verificada), consultas sugeridas, preguntas de compra, IDs de fotos por comprobar, estructura editorial y tres funciones visuales distintas. No realiza búsquedas web por sí mismo ni extrae prestaciones del título como hechos. La lista pendiente se recupera tras reinicios; solo muestra revisiones vigentes sin candidato asociado.

`ResearchPipeline.submit` enlaza evidencia revisada, plan visual y borrador al Worker. Exige ID/SKU literal, identidad exacta, afirmaciones estructuralmente elegibles y original declarado verificado. El Worker aplica el supervisor y la aprobación comercial posterior sigue siendo obligatoria. El ledger rechaza candidatos si cambia la observación o se reemplaza el trabajo asociado. Los candidatos preexistentes sin vínculo siguen bajo sus controles anteriores. No hay escritura externa. La generación de copy, investigación web y verificación visual reales siguen siendo tareas del investigador, no se simulan con datos inventados.

Prueba real local 19-nov-2026: se prepararon 40 expedientes de las 40 observaciones públicas de Casa Viva; repetición: cero nuevos. Prioridades iniciales incluyeron mantel circular, Luminoliss y mantel cuadrado. Son nombres observados, no fichas certificadas. Las pruebas sintéticas cubren rechazo de investigación vacía, idempotencia, reconstrucción de pendientes y cambio de revisión.
