# Autonomía, permisos y desbloqueos — Contrato v0.1

## Principio
Un agente nunca debe esquivar un control de acceso o inventar permisos. El propietario define de antemano **capacidades autorizadas** con alcance, límites, vencimiento, presupuesto y revocación. Si la conexión no expone una operación (por ejemplo, `workflow_dispatch` o SSH), pedir que se configure el conector/servicio, o dejar un paso de instalación puntual. No usar credenciales en conversaciones, comandos de shell arbitrarios, tokens de terceros ni suplantación de sesiones.

## Matriz mínima

| Capacidad | Por defecto | Delegación propuesta |
| --- | --- | --- |
| Leer catálogo público y hacer capturas | Permitido en dominios propios | Lista de dominios y límites de tráfico |
| Leer catálogo privado, proveedores o mensajes | Bloqueado | Conector autorizado + consentimiento y permisos mínimos |
| Guardar hallazgos y propuestas | Permitido en entorno aislado | Sin PII en GitHub público |
| Crear borradores de productos | Bloqueado | Autorización acotada por tienda + pruebas + rollback |
| Marcar un artículo agotado como no disponible | Bloqueado | Datos fiables, regla explícita, log y periodo de observación |
| Ocultar/despublicar productos | Bloqueado | Aprobación específica o política previamente formalizada y probada |
| Borrar definitivamente productos | Prohibido por defecto | Procedimiento humano excepcional |
| Cambiar precios, caja, cobros, pedidos o comisiones | Bloqueado | Autorización por operación, fuera de agentes de observación |
| Ejecutar comandos SSH arbitrarios o usar root | Prohibido | No forma parte del producto |
| Desplegar o contratar servicios | Bloqueado | Autorización explícita y verificación de costes |

## Política instalable
Cada tienda dispone de manifiesto privado con `tenant_id`, permisos, integraciones, orígenes, usuarios aprobadores, operaciones permitidas, franjas horarias, límites por ejecución y coste máximo. El repositorio público solo contiene ejemplo sintético.

## Desbloqueo sin repetir pasos
1. Descubrir capacidad del conector actual y ejecutar **solo** acciones soportadas.
2. Si falta capacidad, definir operación equivalente mediante API oficial o job de lista blanca.
3. Crear integración con token **de alcance mínimo**, guardado en el gestor de secretos de la plataforma, nunca en el chat.
4. Validar primero en `dry_run` y test; grabar evidencia.
5. Activar modo `propose` para que el humano apruebe.
6. Solo después considerar políticas `apply` con ámbito reducido y reversible.
7. Añadir `kill_switch`, expiración, idempotencia, límites de ejecución y revocación inmediata.

## Trabajos sin intervención
GitHub Actions puede ejecutar `schedule` o `workflow_dispatch` cuando el repo y la cuenta lo permitan. Su API de despacho requiere credenciales con permiso Actions: write; no inferir que un conector ChatGPT permita ese método. Alternativa: tarea periódica en VPS con identidad no privilegiada y archivo de política. Verificar zonas horarias, costes, cuota, registro y políticas de retención.

## Bloqueo estándar (para agentes)
Registrar: `task_id, capability, reason, attempted_safe_steps, permission_needed, one_time_user_action, risk, estimated_cost, next_safe_step`. Una vez que el humano habilita la integración, registrar su capacidad disponible y continuar sin solicitarle el mismo paso en cada corrida; no almacenar secretos ni ocultar dependencias.

## Requisitos para producción
Pruebas de autorización negativa, credenciales revocadas, pérdida de conexión, duplicados, reintentos, colisiones de procesos, comprobación de inventario contra fuente canónica, auditoría de cambios y rollback probado.
