-- Relational adaptation of RecomenRestaurant's table occupancy workflow.
BEGIN;
CREATE TABLE IF NOT EXISTS public.salon_mesas (
 id_mesa bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 id_restaurante bigint NOT NULL REFERENCES public.restaurantes(id_restaurante),
 nombre varchar(24) NOT NULL CHECK(length(trim(nombre))>0),
 zona varchar(40) NOT NULL DEFAULT 'General',
 capacidad integer NOT NULL CHECK(capacidad BETWEEN 1 AND 40),
 estado text NOT NULL DEFAULT 'libre' CHECK(estado IN ('libre','ocupada','limpieza')),
 personas integer NOT NULL DEFAULT 0,
 actualizado_en timestamptz NOT NULL DEFAULT now(),
 CHECK((estado='ocupada' AND personas BETWEEN 1 AND capacidad) OR (estado<>'ocupada' AND personas=0))
);
CREATE UNIQUE INDEX IF NOT EXISTS salon_mesas_nombre_zona ON public.salon_mesas(id_restaurante,lower(zona),lower(nombre));
ALTER TABLE public.salon_mesas ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.salon_mesas FROM PUBLIC;
COMMIT;
