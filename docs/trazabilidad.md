# Trazabilidad verificable

Aplica en este orden `migrations/20261125_trazabilidad_anclas.sql`, `migrations/20261125_trazabilidad_anclas_worker.sql` y `migrations/20261125_trazabilidad_transaccion_firmada.sql` mediante el flujo controlado de migraciones.

Cada ancla almacena solo un SHA-256 canónico. Las reseñas incluyen el hash normalizado del comentario y un HMAC del identificador del autor; nunca se guarda el comentario ni la identidad en la ancla. Las decisiones de IA incluyen su `hash_entrada`, estado y metadatos de ejecución sin copiar prompts completos.

El proceso disponible es local y seguro:

```powershell
flask anchor-traceability --mode dry-run --limit 50
```

`dry-run` cambia anclas pendientes o fallidas a `simulado`; `off` no hace cambios. El modo `onchain` usa el contrato `anchor(bytes32)` y guarda la transacción firmada antes de enviarla. Un bloqueo PostgreSQL impide ejecutar dos workers a la vez; ante un error de red se consulta el recibo y se reenvía la misma transacción firmada, nunca una nueva. Una transacción pendiente se procesa antes de crear otra. El contrato desplegado y la conexión todavía deben verificarse en el entorno real.

Instala `requirements.txt` y configura `CHAIN_RPC_URL`, `CHAIN_ID`, `ANCHOR_CONTRACT`, `ANCHOR_PRIVATE_KEY`, `ANCHOR_CONTRACT_METHOD=anchor` y `ANCHOR_MODE=onchain` en el entorno del despliegue. Al recibir tráfico, cada proceso web inicia un trabajador de reseñas; un bloqueo PostgreSQL evita que procesen a la vez. Por defecto consulta cada 20 segundos; puede ajustarse con `ANCHOR_AUTO_INTERVAL_SECONDS` y desactivarse con `ANCHOR_AUTO_ENABLED=false`. El proceso web debe permanecer activo; en infraestructura que duerme procesos, utiliza un servicio worker persistente para garantizar progreso sin tráfico. En modo test no se inicia. También se mantiene el comando manual `flask --app wsgi:app anchor-traceability --mode onchain --limit 50` para diagnóstico. Cada envío consume gas.

`TRACEABILITY_PSEUDONYM_SECRET` debe tener al menos 32 caracteres. Si no se define, se utiliza `ANCHOR_PSEUDONYM_SECRET` del sistema anterior, o en último caso `SECRET_KEY`. Cambiar el secreto modifica los hashes calculados para registros existentes.
