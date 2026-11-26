-- Stateful EVM worker support. Apply after 20261125_trazabilidad_anclas.sql.
BEGIN;

ALTER TABLE public.anclas_trazabilidad
    ADD COLUMN IF NOT EXISTS nonce_transaccion BIGINT,
    ADD COLUMN IF NOT EXISTS enviada_en TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS proximo_intento_en TIMESTAMPTZ;

ALTER TABLE public.anclas_trazabilidad
    DROP CONSTRAINT IF EXISTS anclas_trazabilidad_estado_check;
ALTER TABLE public.anclas_trazabilidad
    ADD CONSTRAINT anclas_trazabilidad_estado_check
    CHECK (estado IN ('pendiente', 'simulado', 'enviado', 'confirmado', 'timeout', 'fallido', 'revertido'));

CREATE INDEX IF NOT EXISTS anclas_trazabilidad_worker
    ON public.anclas_trazabilidad (estado, proximo_intento_en, creado_en)
    WHERE estado IN ('pendiente', 'fallido', 'enviado', 'timeout');

COMMIT;
