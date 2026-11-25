"""Menu projections and durable jobs, using the application's shared transaction."""
from app.db.repository import shared_transaction


def query(sql, args=(), *, many=False):
    with shared_transaction() as conn, conn.cursor() as cur:
        cur.execute(sql, args)
        return list(cur.fetchall()) if many else cur.fetchone()


class Menu3DRepository:
    @staticmethod
    def resource(rid, *, lock=False):
        return query('SELECT m.*, p.id_restaurante, r.id_empresa FROM public.platos_recursos3d m '
            'JOIN public.platos p USING(id_plato) JOIN public.restaurantes r USING(id_restaurante) '
            'WHERE m.id_recurso=%s' + (' FOR UPDATE OF m' if lock else ''), (rid,))

    @staticmethod
    def history(pid):
        return query('SELECT * FROM public.platos_recursos3d WHERE id_plato=%s ORDER BY version DESC', (pid,), many=True)

    @staticmethod
    def lock_company(eid):
        # Serializes reservations, version allocation and daily cost quotas per company.
        return query('SELECT id_empresa FROM public.empresas WHERE id_empresa=%s FOR UPDATE', (eid,))

    @staticmethod
    def insert_resource(pid, uid, originals, photos, size):
        return query('''INSERT INTO public.platos_recursos3d
            (id_plato,id_usuario,version,originales,fotografias,bytes_fotos)
            SELECT %s,%s,COALESCE(MAX(version),0)+1,%s,%s,%s
            FROM public.platos_recursos3d WHERE id_plato=%s RETURNING *''',
            (pid,uid,originals,photos,size,pid))

    @staticmethod
    def usage(eid):
        return query('''SELECT count(*) FILTER(WHERE solicitado_en > now()-interval '1 day') AS solicitudes,
            COALESCE(sum(bytes_fotos + GREATEST(bytes_modelo,52428800)),0) AS reservado
            FROM public.platos_recursos3d m JOIN public.platos p USING(id_plato)
            JOIN public.restaurantes r USING(id_restaurante) WHERE r.id_empresa=%s''', (eid,))

    @staticmethod
    def update(rid, **fields):
        allowed = {'estado','progreso','intentos','envio_iniciado','tarea_externa','clave_idempotencia',
            'error_codigo','error_mensaje','aprobado','modelo_path','bytes_modelo','solicitado_en',
            'finalizado_en','siguiente_intento','lease_hasta','lease_token'}
        if not fields or set(fields) - allowed:
            raise ValueError('Actualización de recurso inválida.')
        return query('UPDATE public.platos_recursos3d SET actualizado_en=now(), ' +
            ','.join(f'{key}=%s' for key in fields) + ' WHERE id_recurso=%s RETURNING *',
            (*fields.values(),rid))

    @staticmethod
    def publish(pid, published):
        return query('''INSERT INTO public.platos_menu3d(id_plato,publicado) VALUES(%s,%s)
            ON CONFLICT(id_plato) DO UPDATE SET publicado=EXCLUDED.publicado,actualizado_en=now()
            RETURNING *''', (pid,published))

    @staticmethod
    def approve(rid, pid):
        query('UPDATE public.platos_recursos3d SET aprobado=false WHERE id_plato=%s AND aprobado RETURNING id_recurso', (pid,))
        return Menu3DRepository.update(rid, aprobado=True)

    @staticmethod
    def claim(token):
        return query('''WITH candidate AS (
            SELECT id_recurso FROM public.platos_recursos3d
            WHERE estado IN ('en_cola','procesando') AND siguiente_intento<=now()
            AND (lease_hasta IS NULL OR lease_hasta<now())
            ORDER BY siguiente_intento FOR UPDATE SKIP LOCKED LIMIT 1)
            UPDATE public.platos_recursos3d m SET lease_token=%s,lease_hasta=now()+interval '10 minutes'
            FROM candidate c WHERE m.id_recurso=c.id_recurso RETURNING m.*''', (token,))

    @staticmethod
    def job_update(rid, token, **fields):
        with shared_transaction():
            row = Menu3DRepository.resource(rid, lock=True)
            if not row or str(row['lease_token']) != str(token):
                raise RuntimeError('La tarea ya pertenece a otro trabajador.')
            return Menu3DRepository.update(rid, **fields)

    @staticmethod
    def menu(rid, filters, *, private=False):
        where, args = ['p.id_restaurante=%s'], [rid]
        if not private: where.append('COALESCE(s.publicado,false)')
        if filters.get('q'):
            where.append('p.nombre ILIKE %s')
            args.append('%' + filters['q'][:160] + '%')
        if filters.get('categoria'):
            where.append('p.categoria=%s'); args.append(filters['categoria'][:100])
        if filters.get('max_precio') is not None:
            where.append('p.precio<=%s'); args.append(filters['max_precio'])
        if filters.get('disponible'):
            where.append('p.esta_disponible=TRUE')
        if filters.get('recomendado'):
            where.append('p.es_recomendado=TRUE')
        if filters.get('id_plato'):
            where.append('p.id_plato=%s'); args.append(filters['id_plato'])
        order = {'precio_asc':'p.precio ASC NULLS LAST','precio_desc':'p.precio DESC NULLS LAST',
                 'nombre':'p.nombre ASC','recomendados':'p.es_recomendado DESC NULLS LAST'}.get(filters.get('orden'), 'p.nombre ASC')
        args += [filters.get('limit',24)+1, filters.get('offset',0)]
        rows = query('''SELECT p.*, COALESCE(s.publicado,false) AS publicado, COALESCE(s.alergenos,'{}') AS alergenos,
            photo.id_recurso AS foto_recurso, model.id_recurso AS modelo_recurso,
            COALESCE((SELECT json_agg(ingrediente ORDER BY posicion) FROM public.platos_ingredientes i WHERE i.id_plato=p.id_plato),'[]') AS ingredientes,
            COALESCE((SELECT json_agg(etiqueta ORDER BY posicion) FROM public.platos_etiquetas e WHERE e.id_plato=p.id_plato),'[]') AS etiquetas,
            COALESCE((SELECT json_agg(restriccion ORDER BY posicion) FROM public.platos_restricciones_dieteticas d WHERE d.id_plato=p.id_plato),'[]') AS restricciones_dieteticas,
            (SELECT to_jsonb(n)-'id_plato' FROM public.platos_informacion_nutricional n WHERE n.id_plato=p.id_plato) AS info_nutricional
            FROM public.platos p LEFT JOIN public.platos_menu3d s USING(id_plato)
            LEFT JOIN LATERAL (SELECT id_recurso FROM public.platos_recursos3d WHERE id_plato=p.id_plato ORDER BY version DESC LIMIT 1) photo ON true
            LEFT JOIN LATERAL (SELECT id_recurso FROM public.platos_recursos3d WHERE id_plato=p.id_plato AND aprobado AND estado='completado') model ON true
            WHERE ''' + ' AND '.join(where) + f' ORDER BY {order},p.id_plato LIMIT %s OFFSET %s', args, many=True)
        limit = filters.get('limit',24)
        return rows[:limit], len(rows)>limit

    @staticmethod
    def categories(rid, *, private=False):
        return query('''SELECT DISTINCT p.categoria FROM public.platos p
            LEFT JOIN public.platos_menu3d s USING(id_plato)
            WHERE p.id_restaurante=%s AND p.categoria IS NOT NULL AND p.categoria<>'' ''' +
            ('' if private else ' AND s.publicado=true') + ' ORDER BY p.categoria', (rid,), many=True)

    @staticmethod
    def stats(rid):
        return query('''SELECT count(*) AS total,
            count(*) FILTER(WHERE s.publicado) AS publicados,
            count(*) FILTER(WHERE EXISTS(SELECT 1 FROM public.platos_recursos3d m WHERE m.id_plato=p.id_plato AND estado='completado')) AS generados,
            count(*) FILTER(WHERE EXISTS(SELECT 1 FROM public.platos_recursos3d m WHERE m.id_plato=p.id_plato AND estado IN ('en_cola','procesando'))) AS procesando,
            count(*) FILTER(WHERE (SELECT estado FROM public.platos_recursos3d m WHERE m.id_plato=p.id_plato ORDER BY version DESC LIMIT 1) IN ('fallido','rechazado')) AS errores,
            count(*) FILTER(WHERE NOT EXISTS(SELECT 1 FROM public.platos_recursos3d m WHERE m.id_plato=p.id_plato AND estado='completado')) AS sin_modelo
            FROM public.platos p LEFT JOIN public.platos_menu3d s USING(id_plato) WHERE p.id_restaurante=%s''', (rid,))
