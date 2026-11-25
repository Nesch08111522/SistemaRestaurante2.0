"""Tenant-scoped table operations with optimistic concurrency."""
from app.db.repository import shared_transaction


class SalonRepository:
    @staticmethod
    def list_for(restaurant_id):
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute('SELECT * FROM public.salon_mesas WHERE id_restaurante=%s ORDER BY zona,nombre,id_mesa', (restaurant_id,))
            return list(cur.fetchall())

    @staticmethod
    def create(restaurant_id, name, zone, capacity):
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute('INSERT INTO public.salon_mesas (id_restaurante,nombre,zona,capacidad) VALUES (%s,%s,%s,%s) RETURNING *',
                        (restaurant_id, name, zone, capacity))
            return cur.fetchone()

    @staticmethod
    def transition(restaurant_id, table_id, expected, target, people):
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute('UPDATE public.salon_mesas SET estado=%s, personas=%s, actualizado_en=now() WHERE id_restaurante=%s AND id_mesa=%s AND estado=%s AND capacidad >= %s RETURNING *',
                        (target, people, restaurant_id, table_id, expected, people))
            return cur.fetchone()

    @staticmethod
    def delete(restaurant_id, table_id):
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM public.salon_mesas WHERE id_restaurante=%s AND id_mesa=%s AND estado='libre' RETURNING id_mesa", (restaurant_id, table_id))
            return cur.fetchone()
