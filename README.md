# SmartResto: PostgreSQL y Clean Architecture

La persistencia operativa es exclusivamente PostgreSQL. Configura `.env` desde `.env.example`: `SECRET_KEY` requiere al menos 32 bytes y `DATABASE_URL` debe ser una URI PostgreSQL con TLS. Para pruebas usa una base aislada en `SMARTRESTO_TEST_DATABASE_URL`; nunca reutilices la base operativa.

## Migraciones

Las migraciones no se ejecutan al arrancar la aplicación. Aplica las existentes mediante el flujo controlado de PostgreSQL, en orden de fecha. Esta entrega requiere `migrations/20261125_trazabilidad_anclas.sql` y `migrations/20261125_feedback_recomendaciones.sql` antes de activar reseñas, decisiones de IA o feedback personalizado.

## Endpoints incorporados

- `POST /owner/api/menu/import-preview`: multipart `archivo` (CSV, XLSX o DOCX); valida en memoria y no escribe.
- `POST /owner/api/menu/import-confirm`: JSON `{ "restaurante_id": 1, "platos": [...] }`; exige sesión empresarial y confirma el preview revalidado en una sola transacción.
- `POST /discovery/api/recommend`: JSON opcional con `preferencias`, `restricciones`, `max_price`, `ubicacion: {latitud, longitud}` y `contexto`. Para una sesión activa incorpora señales privadas de perfil, favoritos, historial y feedback.
- `POST /discovery/api/recommend/feedback`: sesión iniciada; JSON `{ "id_plato": 1, "valor": "me_interesa" | "no_me_interesa" }`.
- `POST /auth/recover` y `POST /auth/recover/complete`: recuperación de contraseña respaldada por PostgreSQL.

La generación de borradores desde fotografía sigue disponible en `POST /owner/api/ai/dish-from-photo`; el propietario debe revisarla y confirmarla antes de persistir un plato.

## Verificación

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Para simular la cola de anclas sin transacciones on-chain:

```powershell
flask anchor-traceability --mode dry-run --limit 50
```

Consulta [docs/trazabilidad.md](docs/trazabilidad.md) para el modelo de hashes y el límite explícito de no realizar envíos on-chain sin RPC y contrato configurados.
