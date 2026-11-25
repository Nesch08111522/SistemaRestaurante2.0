-- Prepared migration. NOT executed by the application. Review on a disposable database first.
-- Requires the existing relational schema and 20261124_menu3d.sql.
BEGIN;
DO $$ BEGIN
  IF to_regclass('public.pedidos_mercado') IS NULL OR to_regclass('public.platos_menu3d') IS NULL THEN
    RAISE EXCEPTION 'Install and review the relational base schema and Menu3D migration first';
  END IF;
END $$;
CREATE UNIQUE INDEX web_pedido_clave ON public.pedidos_mercado(clave_solicitud) WHERE clave_solicitud LIKE 'web:%';
CREATE TABLE public.web_stock_platos (
 id_plato bigint PRIMARY KEY REFERENCES public.platos(id_plato),
 disponibles integer NOT NULL DEFAULT 0 CHECK(disponibles>=0),
 version bigint NOT NULL DEFAULT 1,
 actualizado_en timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE public.web_pedidos_control (
 id_pedido bigint PRIMARY KEY REFERENCES public.pedidos_mercado(id_pedido),
 hash_solicitud text NOT NULL,
 creado_en timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE public.web_stock_movimientos (
 id_movimiento bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 id_plato bigint NOT NULL REFERENCES public.platos(id_plato),
 id_pedido bigint REFERENCES public.pedidos_mercado(id_pedido),
 id_actor bigint NOT NULL REFERENCES public.usuarios(id_usuario),
 cantidad integer NOT NULL,
 tipo text NOT NULL CHECK(tipo IN ('venta','cancelacion','ajuste')),
 creado_en timestamptz NOT NULL DEFAULT now(),
 UNIQUE(id_pedido,id_plato,tipo)
);
CREATE TABLE public.web_eventos_operacion (
 id_evento bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 id_actor bigint NOT NULL REFERENCES public.usuarios(id_usuario),
 id_restaurante bigint NOT NULL REFERENCES public.restaurantes(id_restaurante),
 id_pedido bigint REFERENCES public.pedidos_mercado(id_pedido),
 accion text NOT NULL,
 creado_en timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX web_eventos_restaurante ON public.web_eventos_operacion(id_restaurante,creado_en DESC);
CREATE INDEX web_movimientos_plato ON public.web_stock_movimientos(id_plato,creado_en DESC);
ALTER TABLE public.web_stock_platos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.web_pedidos_control ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.web_stock_movimientos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.web_eventos_operacion ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.web_stock_platos,public.web_pedidos_control,public.web_stock_movimientos,public.web_eventos_operacion FROM PUBLIC;
DO $$ DECLARE role_name text; BEGIN
 FOREACH role_name IN ARRAY ARRAY['anon','authenticated'] LOOP
  IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname=role_name) THEN
   EXECUTE format('REVOKE ALL ON public.web_stock_platos,public.web_pedidos_control,public.web_stock_movimientos,public.web_eventos_operacion FROM %I',role_name);
  END IF;
 END LOOP;
END $$;
-- The trusted Flask database role needs table/sequence privileges and an appropriate RLS policy
-- or BYPASSRLS. Never grant these tables to the browser's anon/authenticated roles.
COMMIT;
