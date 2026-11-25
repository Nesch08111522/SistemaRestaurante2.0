"""SQL primitives for operational transactions; all identifiers are code-owned."""
from contextlib import contextmanager
from app.db.repository import shared_transaction


def query(sql, args=(), *, many=False):
    with shared_transaction() as conn, conn.cursor() as cur:
        cur.execute(sql, args)
        return list(cur.fetchall()) if many else cur.fetchone()


@contextmanager
def restaurant_transaction(rid, request_key=None):
    with shared_transaction() as conn:
        if request_key:
            conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))', (request_key,))
        # One lock order for checkout, inventory adjustment and state transitions.
        conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))', (f'commerce:{rid}',))
        yield


class OperationsRepository:
    @staticmethod
    def catalog(rid, *, private=False):
        return query("SELECT p.*, COALESCE(s.disponibles,0) AS stock, COALESCE(s.version,0) AS stock_version "
            "FROM public.platos p LEFT JOIN public.web_stock_platos s USING(id_plato) "
            "LEFT JOIN public.platos_menu3d m USING(id_plato) WHERE p.id_restaurante=%s "
            + ('' if private else 'AND p.esta_disponible AND m.publicado ') + 'ORDER BY p.id_plato LIMIT 500', (rid,), many=True)

    @staticmethod
    def reserve(pid, quantity, order_id, actor):
        row = query('UPDATE public.web_stock_platos SET disponibles=disponibles-%s,version=version+1,actualizado_en=now() '
            'WHERE id_plato=%s AND disponibles>=%s RETURNING id_plato', (quantity,pid,quantity))
        if row:
            query("INSERT INTO public.web_stock_movimientos(id_plato,id_pedido,id_actor,cantidad,tipo) VALUES(%s,%s,%s,%s,'venta') RETURNING id_movimiento", (pid,order_id,actor,-quantity))
        return bool(row)

    @staticmethod
    def restore(order_id, actor):
        rows=query("SELECT id_plato,-cantidad AS cantidad FROM public.web_stock_movimientos WHERE id_pedido=%s AND tipo='venta' ORDER BY id_plato",(order_id,),many=True)
        for row in rows:
            inserted=query("INSERT INTO public.web_stock_movimientos(id_plato,id_pedido,id_actor,cantidad,tipo) VALUES(%s,%s,%s,%s,'cancelacion') ON CONFLICT DO NOTHING RETURNING id_movimiento",(row['id_plato'],order_id,actor,row['cantidad']))
            if inserted:
                query('UPDATE public.web_stock_platos SET disponibles=disponibles+%s,version=version+1,actualizado_en=now() WHERE id_plato=%s RETURNING id_plato',(row['cantidad'],row['id_plato']))

    @staticmethod
    def control(order_id):
        return query('SELECT * FROM public.web_pedidos_control WHERE id_pedido=%s',(order_id,))

    @staticmethod
    def remember(order_id, fingerprint):
        return query('INSERT INTO public.web_pedidos_control(id_pedido,hash_solicitud) VALUES(%s,%s) RETURNING id_pedido',(order_id,fingerprint))

    @staticmethod
    def event(actor,rid,action,order_id=None):
        return query('INSERT INTO public.web_eventos_operacion(id_actor,id_restaurante,id_pedido,accion) VALUES(%s,%s,%s,%s) RETURNING id_evento',(actor,rid,order_id,action))

    @staticmethod
    def adjust(pid, quantity, version, actor):
        before=query('SELECT * FROM public.web_stock_platos WHERE id_plato=%s FOR UPDATE',(pid,))
        if (before or {}).get('version',0)!=version:
            return False
        query('INSERT INTO public.web_stock_platos(id_plato,disponibles) VALUES(%s,%s) ON CONFLICT(id_plato) DO UPDATE SET disponibles=EXCLUDED.disponibles,version=web_stock_platos.version+1,actualizado_en=now() RETURNING id_plato',(pid,quantity))
        query("INSERT INTO public.web_stock_movimientos(id_plato,id_actor,cantidad,tipo) VALUES(%s,%s,%s,'ajuste') RETURNING id_movimiento",(pid,actor,quantity-(before or {}).get('disponibles',0)))
        return True
