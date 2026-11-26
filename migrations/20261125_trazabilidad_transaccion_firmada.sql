-- Apply after both prior trazabilidad migrations.
BEGIN;
ALTER TABLE public.anclas_trazabilidad ADD COLUMN IF NOT EXISTS transaccion_firmada TEXT;
COMMIT;
