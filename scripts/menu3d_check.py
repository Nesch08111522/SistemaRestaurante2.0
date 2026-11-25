"""Read-only deployment preflight; no credentials or business rows printed."""
import os
from app.config import Config
from app.db.connection import connection


def main():
    required = ['SUPABASE_URL','SUPABASE_SERVICE_ROLE_KEY','MESHY_API_KEY']
    missing = [key for key in required if not os.getenv(key)]
    ready = not missing
    print('CONFIG: ' + ('missing '+', '.join(missing) if missing else 'present'))
    try:
        with connection() as conn:
            for table in ('platos','restaurantes','platos_menu3d','platos_recursos3d'):
                row = conn.execute('SELECT to_regclass(%s) AS name',('public.'+table,)).fetchone()
                print(table+': '+('present' if row['name'] else 'missing'))
                ready = ready and bool(row['name'])
            row = conn.execute("SELECT public,file_size_limit FROM storage.buckets WHERE id='platos-media'").fetchone()
            print('BUCKET: '+('private' if row and row['public'] is False else 'missing or public: blocked'))
            ready = ready and bool(row and row['public'] is False)
            role = conn.execute('SELECT rolbypassrls,rolsuper FROM pg_roles WHERE rolname=current_user').fetchone()
            print('DB_ROLE_BYPASSES_RLS: '+str(bool(role and (role['rolbypassrls'] or role['rolsuper']))))
            # Table owners can also bypass RLS unless FORCE ROW LEVEL SECURITY is enabled.
            rows = conn.execute("SELECT tablename,rowsecurity FROM pg_tables WHERE schemaname='public' AND tablename IN ('platos_menu3d','platos_recursos3d')").fetchall()
            print('RLS_NEW_TABLES_ENABLED: '+str(len(rows)==2 and all(r['rowsecurity'] for r in rows)))
            ready = ready and len(rows)==2 and all(r['rowsecurity'] for r in rows)
            policy = conn.execute("SELECT policyname FROM pg_policies WHERE schemaname='storage' AND tablename='objects' AND policyname='menu3d_private_objects' AND permissive='RESTRICTIVE'").fetchone()
            print('STORAGE_RESTRICTIVE_POLICY: '+str(bool(policy)))
            ready = ready and bool(policy)
    except Exception as error:
        print('DATABASE_CHECK_FAILED: '+type(error).__name__)
        return 1
    if not missing:
        from app.services.menu3d_storage import Storage
        try:
            bucket = Storage()._request('GET','/bucket/platos-media').json()
            print('STORAGE_API_PRIVATE_BUCKET: '+str(bucket.get('public') is False))
            ready = ready and bucket.get('public') is False
        except Exception as error:
            print('STORAGE_CHECK_FAILED: '+type(error).__name__)
            return 1
    return 0 if ready else 1


if __name__=='__main__':
    raise SystemExit(main())
