# Trazabilidad verificable

La migración `migrations/20261125_trazabilidad_anclas.sql` crea la cola PostgreSQL `public.anclas_trazabilidad`. Debe aplicarse mediante el flujo controlado de migraciones, antes de desplegar la versión que crea reseñas o decisiones de IA.

Cada ancla almacena solo un SHA-256 canónico. Las reseñas incluyen el hash normalizado del comentario y un HMAC del identificador del autor; nunca se guarda el comentario ni la identidad en la ancla. Las decisiones de IA incluyen su `hash_entrada`, estado y metadatos de ejecución sin copiar prompts completos.

El proceso disponible es local y seguro:

```powershell
flask anchor-traceability --mode dry-run --limit 50
```

`dry-run` cambia las anclas pendientes a `simulado`; `off` no hace cambios. No existe envío on-chain en esta versión: activarlo requerirá un RPC, un contrato y una revisión de seguridad explícitamente configurados.

`TRACEABILITY_PSEUDONYM_SECRET` debe tener al menos 32 caracteres. Si no se define, se utiliza `SECRET_KEY`, que ya es obligatorio para la aplicación.
