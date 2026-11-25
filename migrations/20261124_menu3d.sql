-- Apply once, with the database owner, after reviewing the preflight on staging.
BEGIN;
DO $$
DECLARE item record;
BEGIN
  FOR item IN SELECT * FROM (VALUES ('platos','id_plato'),('platos','id_restaurante'),
      ('restaurantes','id_restaurante'),('restaurantes','id_empresa'),('usuarios','id_usuario')) AS t(tab,col)
  LOOP
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public'
        AND table_name=item.tab AND column_name=item.col AND data_type IN ('integer','bigint')) THEN
      RAISE EXCEPTION 'Incompatible schema: %.%', item.tab, item.col;
    END IF;
  END LOOP;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public'
    AND table_name='platos' AND column_name='id_plato'
    AND (column_default IS NOT NULL OR is_identity='YES')) THEN
    RAISE EXCEPTION 'platos.id_plato needs its existing database-generated identity/default';
  END IF;
  IF EXISTS (SELECT 1 FROM storage.buckets WHERE id='platos-media' AND public) THEN
    RAISE EXCEPTION 'platos-media must be private; review existing clients before migration';
  END IF;
END $$;

-- Presentation/publication metadata only; business data stays in public.platos.
CREATE TABLE public.platos_menu3d (
  id_plato bigint PRIMARY KEY REFERENCES public.platos(id_plato) ON DELETE CASCADE,
  publicado boolean NOT NULL DEFAULT false,
  alergenos text[] NOT NULL DEFAULT '{}' CHECK(cardinality(alergenos)<=40),
  actualizado_en timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE public.platos_recursos3d (
  id_recurso bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_plato bigint NOT NULL REFERENCES public.platos(id_plato) ON DELETE CASCADE,
  id_usuario bigint NOT NULL REFERENCES public.usuarios(id_usuario),
  version integer NOT NULL CHECK(version>0),
  originales text[] NOT NULL CHECK(cardinality(originales) BETWEEN 1 AND 4),
  fotografias text[] NOT NULL CHECK(cardinality(fotografias)=cardinality(originales)),
  modelo_path text,
  bytes_fotos bigint NOT NULL CHECK(bytes_fotos>=0),
  bytes_modelo bigint NOT NULL DEFAULT 0 CHECK(bytes_modelo>=0),
  proveedor text NOT NULL DEFAULT 'meshy',
  tarea_externa text,
  estado text NOT NULL DEFAULT 'pendiente' CHECK(estado IN
    ('pendiente','en_cola','procesando','completado','fallido','rechazado')),
  progreso integer NOT NULL DEFAULT 0 CHECK(progreso BETWEEN 0 AND 100),
  intentos integer NOT NULL DEFAULT 0,
  envio_iniciado boolean NOT NULL DEFAULT false,
  clave_idempotencia uuid UNIQUE,
  error_codigo text,
  error_mensaje text,
  aprobado boolean NOT NULL DEFAULT false,
  creado_en timestamptz NOT NULL DEFAULT now(),
  actualizado_en timestamptz NOT NULL DEFAULT now(),
  solicitado_en timestamptz,
  finalizado_en timestamptz,
  siguiente_intento timestamptz NOT NULL DEFAULT now(),
  lease_hasta timestamptz,
  lease_token uuid,
  UNIQUE(id_plato,version),
  CHECK (NOT aprobado OR (estado='completado' AND modelo_path IS NOT NULL AND bytes_modelo>0))
);
CREATE UNIQUE INDEX platos_recursos3d_aprobado ON public.platos_recursos3d(id_plato) WHERE aprobado;
CREATE UNIQUE INDEX platos_recursos3d_activo ON public.platos_recursos3d(id_plato)
  WHERE estado IN ('en_cola','procesando');
CREATE INDEX platos_recursos3d_cola ON public.platos_recursos3d(siguiente_intento)
  WHERE estado IN ('en_cola','procesando');
CREATE INDEX platos_recursos3d_historial ON public.platos_recursos3d(id_plato,version DESC);

-- Flask sessions are not Supabase Auth JWTs: never pretend auth.uid() is id_usuario.
-- No direct anon/authenticated access. Authorized Flask server is the only gateway.
ALTER TABLE public.platos_menu3d ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.platos_recursos3d ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.platos_menu3d, public.platos_recursos3d FROM anon, authenticated;
REVOKE ALL ON SEQUENCE public.platos_recursos3d_id_recurso_seq FROM anon, authenticated;
INSERT INTO storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
VALUES ('platos-media','platos-media',false,52428800,
 ARRAY['image/jpeg','image/png','image/webp','model/gltf-binary'])
ON CONFLICT(id) DO NOTHING;
-- Restrictive policies also protect against existing permissive wildcard policies.
CREATE POLICY menu3d_private_objects ON storage.objects AS RESTRICTIVE FOR ALL
 TO anon, authenticated USING(bucket_id <> 'platos-media') WITH CHECK(bucket_id <> 'platos-media');
COMMIT;
