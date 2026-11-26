-- Per-user feedback. The old feedback_recomendacion tables have no user key,
-- so they cannot be used as a personalization signal without leaking data.
BEGIN;

CREATE TABLE IF NOT EXISTS public.feedback_recomendaciones_usuario (
    id_usuario BIGINT NOT NULL REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE,
    id_plato BIGINT NOT NULL REFERENCES public.platos(id_plato) ON DELETE CASCADE,
    valor VARCHAR(16) NOT NULL CHECK (valor IN ('me_interesa', 'no_me_interesa')),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_usuario, id_plato)
);

CREATE INDEX IF NOT EXISTS feedback_recomendaciones_usuario_lookup
    ON public.feedback_recomendaciones_usuario (id_usuario, valor, actualizado_en DESC);

COMMIT;
