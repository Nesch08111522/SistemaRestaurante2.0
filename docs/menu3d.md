# Menú 3D de SmartResto — implementación y despliegue

Estado: implementación local integrada, con validación externa pendiente. No se ha aplicado la migración a Supabase ni realizado una generación pagada. No es una certificación de producción.

## Diagnóstico de la arquitectura

- Flask con fábrica `app.create_app`, blueprints registrados en `app/blueprints/__init__.py`, Jinja y recursos estáticos locales.
- PostgreSQL se consulta mediante psycopg 3 y `shared_transaction`; no existe un cliente Supabase Storage previo.
- Autenticación propia por sesiones Flask. `fresh_session_user` revalida la cuenta; `permitted` comprueba membresía, rol, empresa, plan, vencimiento y módulos habilitados. No equivale a Supabase Auth.
- `platos.id_restaurante` identifica al propietario del plato. Se reutilizan sus datos y las tablas de ingredientes, etiquetas, restricciones e información nutricional. `restaurantes_platos` se mantiene sincronizada al crear/editar para los lectores anteriores.
- No se encontraron recursos 3D, fotografías de platos, publicación individual ni alérgenos específicos en los repositorios auditados. La migración añade solo metadatos necesarios, sin duplicar platos.
- `/ar/` era una página mínima. `/ar/api/modelos/<id>` fabricaba una ruta local que no acreditaba que hubiese un modelo. Ahora devuelve únicamente el recurso aprobado o `null`.
- `model-viewer` 4.1.0 ya está disponible localmente. Se conserva y carga por demanda.
- Tema actual: `data-theme=light|dark`. Los estilos `.m3d` respetan ambos y no alteran otros módulos. Se reutilizan las fuentes del sitio y su footer.
- Versiones instaladas observadas: Python 3.12, Flask 3.1.3, Flask-WTF 1.3.0, psycopg 3.3.9, Pillow 13.0.0, requests 2.34.2, Jinja 3.1.6, pytest 9.2.0. El mínimo de Flask se elevó a 3.1 por el límite multipart por petición.
- El esquema remoto y sus políticas no pudieron inspeccionarse: el host de PostgreSQL no resolvió desde el entorno. Los nombres existentes proceden de los repositorios reales; la migración tiene preflight y debe contrastarse con la base antes de ejecutarla.

## Uso

- Directorio público: `/ar/`.
- Carta de un restaurante publicado: `/ar/restaurantes/ID`.
- Administración: `/ar/gestion`, también enlazada desde el panel del empresario.
- El empresario selecciona un restaurante de sus membresías autorizadas, registra o edita un plato y sus datos alimentarios, y abre **Fotos y modelos**.
- Se aceptan de una a cuatro fotografías reales por versión. La primera es la vista principal. Se conserva el original privado y se genera una copia JPEG optimizada, orientada y sin EXIF para mostrar/enviar al proveedor.
- **Guardar fotografías** no llama a Meshy. **Generar modelo 3D** abre una confirmación del costo y del envío de las imágenes.
- El trabajador genera y valida un GLB. **Revisar en 3D** permite inspeccionarlo antes de **Aprobar para el menú**. El plato debe además estar publicado.
- **Rechazar modelo** retira su aprobación. **Nueva versión con estas fotos** permite regenerar sin subirlas de nuevo, pero exige una nueva confirmación antes del envío pagado.
- **Despublicar** retira el plato de este menú. Para desactivarlo sin borrar el registro, desmarca **Disponible** en el editor.
- El público puede buscar por nombre, categoría real, precio máximo, disponibilidad y recomendación; ordenar por nombre o precio y paginar de 24 en 24. La sección recomendados muestra hasta tres platos marcados por el restaurante.
- El detalle muestra precio, ingredientes, alérgenos declarados, restricciones, etiquetas y los datos nutricionales, tiempo y picante existentes. Nunca infiere que un plato sea seguro por no tener alérgenos registrados.
- Sin modelo aprobado se muestra la fotografía; no se asigna ningún GLB genérico. No se incorporaron modelos de demostración al producto.
- Una fotografía no permite reconstruir las partes ocultas con exactitud. La interfaz lo advierte; cuatro ángulos pueden ayudar, sin garantizar una réplica exacta.

## Variables de entorno

Mantenerlas únicamente en el servidor y en el trabajador; usar un gestor de secretos en producción.

| Variable | Uso / valor inicial |
| --- | --- |
| `DATABASE_URL` | Conexión existente a PostgreSQL Supabase, con TLS |
| `SECRET_KEY` | Configuración existente de sesiones y CSRF |
| `SUPABASE_URL` | Origen HTTPS del proyecto, sin rutas adicionales |
| `SUPABASE_SERVICE_ROLE_KEY` | Clave service role exclusivamente del backend |
| `MENU3D_PROVIDER` | `meshy` (único adaptador implementado actualmente) |
| `MESHY_API_KEY` | Clave de la cuenta Meshy que asumirá los costos |
| `MESHY_MODEL` | `meshy-7.1`, configurable según documentación y disponibilidad |
| `MENU3D_ASSET_HOSTS` | `assets.meshy.ai`; lista de hosts CDN exactos separados por comas, nunca comodines |
| `MENU3D_DAILY_LIMIT` | `10`, máximo de solicitudes nuevas por empresa en ventana de 24 horas |
| `MENU3D_COMPANY_BYTES` | `1073741824`, reserva máxima por empresa (1 GiB) |
| `SMARTRESTO_TEST_DATABASE_URL` | Base de pruebas independiente; nunca la operativa |

Usar enteros positivos para cuotas. `MAX_CONTENT_LENGTH` global se conserva; solo la carga de fotos del módulo admite un multipart de hasta 9 MiB. Cada foto está limitada a 2 MiB y cada GLB a 50 MiB.

Sin credenciales se responde con error explícito; no se activa una simulación ni se marca una tarea como completada. En este entorno faltaban `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `MESHY_API_KEY` y la base independiente de pruebas.

## Migración y Storage

Archivo: `migrations/20261124_menu3d.sql`. Es una migración de aplicación única, transaccional; no se ejecuta al iniciar Flask.

1. Revisar en staging el esquema real, las claves y defaults de IDs. La migración exige IDs integer/bigint y que `platos.id_plato` conserve generación por la base. Los nuevos recursos usan `GENERATED ALWAYS AS IDENTITY`; nunca `max(id)+1`.
2. Revisar las políticas existentes de `storage.objects`, los grants del rol PostgreSQL del servidor y los clientes existentes que pudieran usar el bucket.
3. Ejecutar el SQL completo con el propietario de la base mediante el editor SQL de Supabase o una conexión administrativa autorizada.
4. Verificar las tablas `platos_menu3d` y `platos_recursos3d`, sus restricciones, índices y RLS.
5. Verificar que `platos-media` sea privado y admita `image/jpeg`, `image/png`, `image/webp`, `model/gltf-binary`, hasta 50 MiB por objeto. La migración no cambia un bucket existente; aborta si es público. Si ya existe con otros límites o MIME, revisarlos manualmente.
6. Verificar la política restrictiva `menu3d_private_objects`: impide que políticas permisivas genéricas expongan este bucket a `anon` o `authenticated`.
7. Ejecutar el preflight de solo lectura: `python -m scripts.menu3d_check`.

No se crean políticas basadas en `auth.uid()`: los usuarios propios de Flask no son identidades Supabase Auth. Las nuevas tablas no conceden acceso directo a `anon`/`authenticated`. El servidor necesita el rol PostgreSQL existente con acceso efectivo (propietario o rol de servidor adecuado); no agregar `BYPASSRLS` a usuarios del navegador. La autorización por empresa ocurre en el backend antes de cada lectura o escritura privada. Service role no reemplaza esa autorización.

Estructura de objetos:

```
platos-media/empresas/{empresa}/restaurantes/{restaurante}/platos/{plato}/
  originales/{uuid}.{jpeg|png|webp}
  procesadas/{uuid}.jpeg
  modelos-3d/{id_recurso}.glb
```

La base almacena rutas y metadatos, nunca binarios ni URLs firmadas persistentes. Las rutas se construyen desde la propiedad consultada en BD. Las referencias de Storage no aceptan rutas arbitrarias.

Fotos/modelos públicos se entregan mediante enlaces firmados de 120 segundos tras verificar publicación del plato, restaurante publicado y no suspendido/rechazado, y aprobación del modelo. La imagen compartida es la copia optimizada del original. Los originales no tienen endpoint público. Al despublicar, nuevos accesos se deniegan; un enlace emitido previamente puede seguir vigente hasta 120 segundos. Las URLs enviadas a Meshy duran una hora.

La reserva es conservadora: cada versión ocupa sus fotos más una reserva de 50 MiB de GLB, incluso si el resultado pesa menos. Máximo 20 versiones por plato. Esto limita crecimiento y concurrencia sin carreras por empresa. La limpieza de versiones antiguas no es automática: conservar las referencias de versiones reutilizadas, respaldar y auditar antes de archivar. Las cargas fallidas intentan borrar los objetos subidos; tras una caída de proceso durante el upload, revisar objetos huérfanos contra las referencias de ambas columnas antes de eliminarlos. No eliminar automáticamente por prefijo ni solo por antigüedad.

## Procesamiento asíncrono

No se usan hilos ligados a la petición, Redis ni Celery. PostgreSQL mantiene la cola:

1. Una transacción registra `en_cola`, usuario, clave de idempotencia y fecha.
2. Un trabajador reclama una fila con `FOR UPDATE SKIP LOCKED` y un lease de 10 minutos.
3. Guarda `envio_iniciado` **antes** del POST pagado a Meshy y el ID externo inmediatamente después de recibirlo.
4. Consulta el progreso mediante GET. No mantiene abierta la petición HTTP del navegador.
5. Descarga únicamente desde los hosts CDN HTTPS autorizados, sin reenviar credenciales ni seguir redirecciones.
6. Verifica MIME, límites, cabecera GLB 2, longitud, chunks, buffers, accessors, referencias, escenas, ciclos, texturas y ausencia de URIs externas. Almacena el modelo privado y marca `completado`; no lo aprueba.
7. El empresario aprueba explícitamente. Solo existe un modelo aprobado y una generación activa por plato.

Estados visibles: `pendiente`, `en_cola`, `procesando`, `completado`, `fallido`, `rechazado`.

Los errores transitorios usan reintento exponencial, hasta seis fallos consecutivos. La consulta normal se repite aproximadamente cada 20 segundos; el navegador consulta la BD cada 10 segundos. Una tarea sin finalizar en 24 horas queda marcada para revisión y puede reanudarse conservando su ID externo.

**Envío incierto:** no puede garantizarse exactamente una llamada pagada si la red cae entre el POST y la respuesta, sin soporte de idempotencia del proveedor. Se bloquea el reenvío automático. Un operador debe localizar en la cuenta Meshy la tarea correspondiente, comprobar que sea la de esas fotografías y ejecutar:

```
python -m flask --app wsgi:app menu3d-recover ID_RECURSO ID_TAREA_EXISTENTE
```

Este comando valida que la tarea exista, la enlaza y registra la recuperación, sin iniciar otra generación. Si el operador no puede identificarla con certeza, no enlazar tareas ajenas ni resetear flags manualmente. El rechazo del proveedor o un modelo inválido requieren una nueva versión y nueva confirmación de costo.

No hay webhooks expuestos: se usa polling autenticado, por lo que no existe una entrada pública de webhooks sin firma.

El validador acepta mallas estáticas autocontenidas; rechaza geometría sparse, accessors de matrices o recursos externos. No se presenta como el validador completo de conformidad Khronos. Antes de ampliar formatos/extensiones, agregar su validación y pruebas. Los resultados que no cumplen quedan rechazados, nunca publicados.

## Ejecución local y despliegue

Con el entorno virtual activado y las dependencias instaladas:

```
python -m pip install -r requirements.txt
python -m scripts.menu3d_check
python -m flask --app wsgi:app run
```

En otro proceso con las mismas variables:

```
python -m flask --app wsgi:app menu3d-worker
```

Para ejecutar un solo ciclo (diagnóstico o scheduler):

```
python -m flask --app wsgi:app menu3d-worker --once
```

Producción: mantener el servidor WSGI existente y desplegar el trabajador como proceso separado supervisado (reinicio automático). Ambos deben usar el mismo código, DB y configuración. Las filas reclamadas se recuperan tras expirar el lease si el trabajador cae. Aplicar primero la migración, después el backend/frontend, después iniciar el trabajador. Configurar HTTPS, cookies seguras, límites del proxy compatibles con 9 MiB y salida HTTPS a Supabase, `api.meshy.ai` y los CDN aprobados. No usar `flask run` en producción.

La publicación depende de que el restaurante ya esté publicado mediante su flujo existente. La administración permite las empresas con membresías autorizadas; no sustituye el alta de empresas/restaurantes ni amplía permisos de roles. `ai.business` sigue requiriendo el plan y rol existentes, por defecto empresario con plan premium o administrador.

## Endpoints

Todas las mutaciones privadas requieren sesión, autorización y token `X-CSRFToken`. Los IDs de empresa enviados por el cliente no se usan para decidir propiedad.

| Método | Ruta | Función |
| --- | --- | --- |
| GET | `/ar/` | Directorio de restaurantes publicados |
| GET | `/ar/restaurantes/<rid>` | Carta pública |
| GET | `/ar/api/restaurantes/<rid>/menu` | Platos publicados, filtros y paginación |
| GET | `/ar/api/restaurantes/<rid>/categorias` | Categorías reales publicadas |
| GET | `/ar/api/platos/<pid>` | Detalle público |
| GET | `/ar/api/modelos/<id_plato>` | Compatibilidad: modelo aprobado o null |
| GET | `/ar/recursos/<id>/<foto o modelo>` | Referencia temporal autorizada pública |
| GET | `/ar/gestion` | Panel privado, selección de restaurante |
| GET | `/ar/api/gestion/restaurantes/<rid>` | Carta privada, métricas y capacidad de generar |
| POST | `/ar/api/gestion/restaurantes/<rid>/platos` | Crear plato |
| PUT | `/ar/api/gestion/platos/<pid>` | Editar datos del plato |
| POST | `/ar/api/gestion/platos/<pid>/fotografias` | Multipart `fotos`, de 1 a 4 archivos |
| GET | `/ar/api/gestion/platos/<pid>/recursos` | Historial de versiones |
| POST | `/ar/api/gestion/recursos/<id>/generar` | Confirmación + UUID de idempotencia, respuesta 202 |
| POST | `/ar/api/gestion/recursos/<id>/reintentar` | Reanudar consulta segura, misma operación |
| POST | `/ar/api/gestion/recursos/<id>/regenerar` | Crear versión pendiente usando las mismas fotos |
| GET | `/ar/api/gestion/recursos/<id>` | Estado persistido, sin llamar a Meshy |
| POST | `/ar/api/gestion/recursos/<id>/revision` | `{ "aprobado": true/false }` |
| POST | `/ar/api/gestion/platos/<pid>/publicacion` | `{ "publicado": true/false }` |
| GET | `/ar/gestion/recursos/<id>/<foto o modelo>` | Previsualización privada autorizada |

Filtros: `q`, `categoria`, `max_precio`, `disponible=1`, `recomendado=1`, `orden=nombre|precio_asc|precio_desc|recomendados`, `page`. JSON público incluye `success`, `platos`, `hay_mas`. Los errores de validación son 400; permisos 401/403; recurso no público 404; transición/conflicto 409; cuota 429; configuración/servicio faltante 503.

## Archivos y responsabilidades

| Archivo | Responsabilidad |
| --- | --- |
| `app/blueprints/ar/__init__.py` | HTML/API pública y privada, serialización, errores |
| `app/repositories/menu3d.py` | Proyecciones de carta, versiones, cola, leases, métricas |
| `app/services/menu3d.py` | Autorización, platos, fotos, cuotas, confirmación, publicación y auditoría |
| `app/services/menu3d_validation.py` | Imágenes, GLB y entradas del plato |
| `app/services/menu3d_storage.py` | Storage privado y enlaces firmados |
| `app/ai/image_to_3d.py` | Interfaz del proveedor y adaptador Meshy real |
| `app/services/menu3d_worker.py` | Trabajador asíncrono y recuperación operativa |
| `app/__init__.py` | Registro CLI y límite multipart antes de CSRF |
| `migrations/20261124_menu3d.sql` | Metadatos, recursos, índices, RLS y bucket |
| `app/templates/ar/index.html` | Directorio público |
| `app/templates/ar/menu.html` | Carta gastronómica pública |
| `app/templates/ar/manage.html` | Panel, editor, fotos y confirmación |
| `app/templates/ar/viewer.html` | Diálogo accesible compartido |
| `app/static/css/menu3d.css` | Diseño encapsulado, responsive, temas y movimiento reducido |
| `app/static/js/menu3d-common.js` | API/CSRF, tarjetas seguras y visor compartido |
| `app/static/js/menu3d-public.js` | Categorías, filtros, búsqueda, paginación y compartir |
| `app/static/js/menu3d-admin.js` | Editor, versiones, polling y aprobación |
| `app/templates/owner/dashboard.html` | Enlace al panel Menú 3D |
| `app/templates/business/show.html` | Enlace a la carta pública |
| `.env.example` | Configuración sin secretos |
| `requirements.txt` | Mínimo Flask 3.1 por límite multipart por petición |
| `scripts/menu3d_check.py` | Preflight de configuración, BD, RLS y Storage |
| `tests/test_menu3d.py` | Pruebas unitarias/HTTP aisladas |
| `tests/menu3d_frontend.cjs` | Lógica JS, CSRF, carga diferida y fallback |
| `tests/integration/test_menu3d_postgres.py` | Pruebas opt-in de cola, leases y restricciones SQL |
| `tests/e2e/menu3d_fixture.py` | Servidor exclusivo de QA, datos explícitamente ficticios |
| `tests/e2e/menu3d.spec.cjs` | Pruebas reproducibles en navegador |
| `docs/menu3d.md` | Esta guía y limitaciones de entrega |

No se modificó `base.html`, las pantallas de autenticación ni sus estilos como parte de este módulo. Los cambios simultáneos en esos archivos pertenecen al trabajo externo observado y se conservaron.

## Pruebas y pendientes

Ejecutar:

```
python -m pytest tests/test_menu3d.py -q
python -m pytest tests/integration/test_menu3d_postgres.py -q
node --test tests/frontend_qa.cjs tests/menu3d_frontend.cjs
python -m pytest tests -q
```

Para navegador, en un entorno con Playwright disponible como herramienta de desarrollo:

```
python -m tests.e2e.menu3d_fixture
npx playwright test tests/e2e/menu3d.spec.cjs
```

Instalar `@playwright/test` y su Chromium solo en el entorno de desarrollo/CI si no están presentes. La fixture escucha únicamente en loopback y muestra **SOLO PRUEBAS / QA**; no debe desplegarse como aplicación ni usarse para afirmar que Meshy funcionó. Su triángulo GLB solo comprueba la carga del visor, no representa un plato real.

Resultados observados:

- 74 pruebas nuevas Python aprobadas inicialmente (validación de archivos, autorización por empresa, CSRF, proveedor, Storage, cola, fallos, publicación y renderizado Jinja).
- 9 pruebas JavaScript aprobadas (3 existentes y 6 del módulo).
- 3 pruebas PostgreSQL omitidas por falta de una base independiente.
- Regresión inicial existente: 58 aprobadas y 8 fallidas por referencias CSS globales inexistentes, comenzando por `/static/css/theme-tokens.css`. El archivo correspondiente está archivado en `CSS ANTERIOR`, mientras la plantilla global apunta a la ruta anterior. No se movieron los estilos ni se alteraron los cambios simultáneos del usuario.
- La generación real y la carga real en Storage no se ejecutaron por falta de credenciales. No se hicieron cargos externos.
- No se ejecutó la migración ni se certificaron sus políticas en Supabase por fallo DNS de la conexión configurada.
- El servidor de QA arrancó, pero el acceso local fue bloqueado por permisos de socket; el navegador integrado agotó la conexión. Computer Use detuvo la alternativa de escritorio al no poder determinar la URL de Chrome con suficiente confianza. Las pruebas visuales/responsive y la interacción WebGL real quedan pendientes; la presencia de CSS responsive no constituye su aprobación.

Antes de producción: contrastar/aplicar migración en staging; verificar RLS, Storage y rol servidor; configurar secretos; ejecutar pruebas PostgreSQL y navegador; resolver las referencias globales CSS; realizar una generación real con fotos autorizadas y confirmación de costo; inspeccionar/aprobar ese resultado; comprobar que otra empresa y un usuario anónimo no puedan consultar recursos privados; observar recuperación del trabajador tras un reinicio. Esto es validación pendiente, no trabajo externo realizado.

## Fuentes oficiales consultadas

- Meshy Image to 3D: https://docs.meshy.ai/en/api/image-to-3d
- Meshy Multi-Image to 3D: https://docs.meshy.ai/en/api/multi-image-to-3d
- Meshy Task Lifecycle: https://docs.meshy.ai/en/api/task-lifecycle
- Supabase Storage REST: https://supabase.com/docs/reference/self-hosting-storage
- Supabase signed URLs: https://supabase.com/docs/reference/python/storage-from-createsignedurl
- Supabase Storage access control: https://supabase.com/docs/guides/storage/security/access-control
- Khronos glTF 2.0: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html

La integración usa POST `/openapi/v1/image-to-3d` o `/openapi/v1/multi-image-to-3d`, `image_url` o `image_urls`, respuesta `result`, y consulta GET del ID externo con `status`, `progress` y `model_urls.glb`. No se inventa una respuesta de generación en producción.
