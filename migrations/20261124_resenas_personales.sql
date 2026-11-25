-- Prepared only: apply through the controlled migration workflow, never at app start.
BEGIN;
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM public.resenas GROUP BY id_usuario, id_restaurante HAVING COUNT(*) > 1
  ) THEN
    RAISE EXCEPTION 'Cannot enforce one review per diner and restaurant: duplicate rows exist';
  END IF;
END $$;
CREATE UNIQUE INDEX IF NOT EXISTS resenas_una_por_usuario_restaurante
  ON public.resenas (id_usuario, id_restaurante);
COMMIT;
