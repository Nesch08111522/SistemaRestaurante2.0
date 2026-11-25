# Empresa, salón y cocina

Se adaptaron los flujos de `RecomenRestaurant/views/owner.py`,
`views/salon.py` y `models/salon.py` al esquema relacional de este proyecto.
No se copió el repositorio documental ni se migraron sus datos.

## Acceso y registro

Una cuenta de empresario sin empresa activa abre `/owner/` para registrar su
empresa y primer restaurante. El registro es atómico, bloquea la cuenta para
evitar duplicados por concurrencia y asigna el plan básico. El restaurante
permanece sin publicar, sujeto al flujo de revisión existente.
Los enlaces de Salón y Cocina llevan a ese registro si aún falta la empresa.
Los empleados necesitan una membresía activa; no se concede acceso por URL.

## Salón

Aplicar `migrations/20261125_salon.sql` una vez en cada entorno. La aplicación
no modifica el esquema automáticamente. La migración crea `salon_mesas` y su
índice, sin modificar los registros existentes.

El salón permite crear y eliminar mesas libres y seguir el ciclo
`libre → ocupada → limpieza → libre`. Valida capacidad, pertenencia al
restaurante y estado esperado para evitar actualizaciones concurrentes.
Usa `tables.service` para atención y `tables.manage` para crear/eliminar.
La política existente requiere plan decente o premium para `tables.manage`;
el registro inicial básico no cambia ni elude esa condición.

Esta adaptación no incorpora todavía los QR, cuentas divididas, pagos por
comensal ni pedidos vinculados a sesiones del proyecto anterior. Finalizar
atención cambia la ocupación; no registra un cobro ni cancela pedidos.

## Cocina

`/kitchen/` y `/kitchen/tablero` abren el tablero operativo. El selector limita
los pedidos al restaurante elegido dentro de la empresa actual. Se mantienen
las transiciones y autorizaciones del servicio comercial existente.

## Validación

`python -m pytest tests -q -p no:cacheprovider`

Se verificaron las páginas de la cuenta afectada con lecturas de PostgreSQL.
No se hicieron registros o modificaciones de datos comerciales para probar:
la comprobación con escrituras temporales fue rechazada por revisión automática.
