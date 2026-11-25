# Comparativa de migración del sistema web — Fase 1

Fecha de revisión: 24 de noviembre de 2026 (America/Lima).

## 1. Objetivo, fuentes y límites

- **Diseño:** `C:/Users/DELL/SistemaRestaurante2.0/prototipo`.
- **Funcionalidad de referencia:** `C:/Users/DELL/RecomenRestaurant`.
- **Destino:** `C:/Users/DELL/SistemaRestaurante2.0`.
- **Alcance de implementación futura:** HTML, CSS, JavaScript y blueprints/rutas del sistema web. Esta fase únicamente entrega este documento; no implementa ni corrige código.
- **Excluido:** sitio público, sus páginas de descubrimiento, ficha comercial pública, landing, páginas informativas y presentación pública de Menú 3D. Se inventarían sus rutas para reconocer dependencias y evitar intervenirlas. Las acciones autenticadas de comensales, operación empresarial y administración pertenecen al sistema, incluso cuando están mezcladas en un blueprint llamado `public` o `main`.
- **Dependencias fuera del alcance:** modelos, repositorios, servicios, esquema SQL, migraciones, workers, integraciones externas y cambios del `.env`. Se leen para entender contratos y se señalan como bloqueos; no se propone modificarlos como parte implícita del trabajo web.

El README del prototipo lo identifica como sitio público multipágina. **`prototipo/ecosistema-demo.html` es la referencia principal del sistema interno**, porque contiene navegación y pantallas para comensal, empresario y administrador. `ingresar.html` y `registrarse.html` sirven de referencia secundaria para acceso; el resto del sitio público no se rediseña en esta migración.

### Método y nivel de verificación

Inventario extraído mediante AST de Python, incluyendo prefijos de registro, métodos explícitos, funciones y llamadas a `render_template` (también helpers del mismo archivo). No se importaron las aplicaciones ni se arrancaron servicios; no se usaron credenciales, bases operativas o proveedores externos. La comparación visual es de estructura HTML y reglas CSS/JS, **no una certificación de equivalencia por capturas de navegador**.

Los conteos son declaraciones de ruta: GET y POST separados pueden producir dos filas para una URL. No incluyen HEAD/OPTIONS automáticos ni la ruta `static` que Flask añade automáticamente. Una función puede servir varias rutas. Los decoradores de autenticación no cambian el endpoint.

Se detectaron cambios concurrentes respecto de la revisión anterior: el nuevo proyecto ya contiene `.env`, configuración de ejemplo para Menú 3D, migraciones y un módulo de gestión 3D. Este documento usa la lectura actual; las cifras y errores anteriores no se presentan como resultados nuevos. No se ejecutó nuevamente la suite durante esta fase.

## 2. Resumen comparativo

| Dimensión | Anterior | Nuevo | Implicación |
| --- | --- | --- | --- |
| Blueprints registrados | 26 | 12 | La cantidad mide superficie, no calidad ni porcentaje de avance. |
| Declaraciones de ruta | 274 | 80 | Incluye sistema, público y límites compartidos. |
| Persistencia | Documentos JSONB y tablas de plataforma | Repositorios relacionales; servicios específicos de Menú 3D | No copiar controladores que dependan de las colecciones antiguas sin un contrato adaptado. |
| Pantallas internas | Flujos amplios por rol | Paneles básicos; gestión 3D más desarrollada | Adoptar diseño del prototipo sin importar sus datos de demostración. |
| Contrato visual | Interfaz anterior con varios subsistemas | Base compartida con sitio público y estilos heredados | Aislar la futura presentación privada para no afectar trabajo público. |
| Variables de integración | Correo, SMS, IA administrativa, anclaje, etc. | Varias declaradas sin consumidor; 3D depende de variables adicionales | Una variable presente no demuestra que la integración funcione. |

## 3. Estado funcional del sistema

**Leyenda:** ✅ existe en el código para la capacidad acotada indicada; ⚠️ incompleta o con diferencias de contrato/experiencia; ❌ no se encontró un flujo web equivalente. Ninguna marca implica validación de producción. Un modelo o un GET aislado no equivale a una funcionalidad completa.

Los módulos públicos se registran en los anexos, pero no cuentan como trabajo autorizado. Los editores privados que publican contenido se marcan como frontera compartida.

| Capacidad | Estado | Evidencia / correspondencia | Brecha concreta | Dependencia / alcance |
| --- | --- | --- | --- | --- |
| Acceso y registro básico | ✅ | auth.login/register → auth.login_form/login_submit/register_form/register_submit | Existen formularios y sesiones. No implica paridad del alta empresarial ni seguridad avanzada. | Web; revisar mensajes, redirecciones y contrato de roles. |
| Recuperación de cuenta y segundo factor | ❌ | Anterior: views/auth.py, utils/account_security.py; nuevo: auth.recover_form | /auth/recover solo vuelve a renderizar login; no hay flujo equivalente de código, cambio de contraseña o 2FA. | Requiere servicio/modelo de seguridad y proveedor; fuera del alcance web. |
| Límite de intentos y revocación de sesiones | ⚠️ | Anterior: protection.allow_attempt y auth_epoch; nuevo: fresh_session_user | El nuevo revalida cuenta/rol, pero no reproduce esos mecanismos del anterior. | Control transversal y almacenamiento requieren revisión fuera del alcance. |
| Perfil y fotografía del usuario | ❌ | Anterior: auth.profile/update_profile/profile_photo; nuevo: public.api_user, auth.api_whoami | Hay consulta de identidad, no una pantalla ni actualización equivalente de perfil. | Pantalla/ruta dentro; persistencia de cambios y archivos requiere contrato previo. |
| Favoritos | ⚠️ | Anterior: auth.favorites/toggle_favorite; nuevo: public.api_favorites | Solo se identifica lectura; faltan flujo de agregar/quitar y vista personal equivalente. | Revisar capacidades disponibles en modelo antes de implementar rutas. |
| Historial de recomendaciones y preferencias | ⚠️ | Anterior: recommendations, recommendation_history; nuevo: discovery.api_recommend/public.api_search_history | Existe recomendación simplificada y lectura de búsquedas; no equivalencia con feedback, contexto e historial personalizado. | No modificar descubrimiento público; delimitar espacio autenticado. |
| Notificaciones | ⚠️ | Anterior: comunicacion, main.mark_notification_read; nuevo: public.api_notifications | GET disponible; falta bandeja y acciones de lectura/gestión equivalentes. | Contrato de lectura y mutaciones pendiente. |
| Mensajería y reclamos | ❌ | Anterior: views/communication.py; sin blueprint equivalente | Faltan conversaciones, adjuntos, casos y sus acciones. | Persistencia/servicios fuera del alcance; web depende de ellos. |
| Reservas personales | ❌ | Anterior: main.reserve, loyalty.reservations/cancel_reservation | Sin rutas equivalentes de reservar/cancelar/consultar reservas personales. | Modelo y reglas requeridos fuera del alcance. |
| Carrito, compra, cupón y recompensa | ❌ | Anterior: market.cart/add_cart/buy/apply_coupon/cart_reward | Nuevo market tiene índice y consultas, no el flujo transaccional. | Reglas de stock, importes e idempotencia no se resuelven solo con UI. |
| Consulta de pedidos | ⚠️ | Anterior: market.orders; nuevo: market.api_mis_pedidos, public.api_user_orders/api_order | Existen datos de lectura; falta recorrido personal equivalente y estados presentados al usuario. | HTML/JS y normalización de respuesta necesarios. |
| Pago, constancia, repetición y cancelación de pedido | ❌ | Anterior: market.pay/receipt/reorder/cancel | No se encontraron rutas equivalentes en nuevo. | Requiere contrato transaccional y de pago, fuera del alcance. |
| Reseñas verificadas y reclamos de compra | ⚠️ | Anterior: market.verified_review/claim, main.add_review; nuevo: public.api_reviews | Solo lectura de reseñas; faltan operaciones y verificación de compra equivalentes. | Depende de reglas y persistencia. |
| Panel de empresario | ⚠️ | Anterior: owner.dashboard; nuevo: owner.dashboard/api_resumen | Lista restaurantes, plan y resumen de reseñas; no tablero de ventas, alertas, stock y operaciones del prototipo. | No inventar métricas faltantes; presentar estados sin datos. |
| Gestión de platos y publicación | ⚠️ | Anterior: owner y catalog; nuevo: ar.manage/create_dish/edit_dish/publish | Hay alta, edición y publicación mediante gestión 3D; faltan equivalencias de catálogo completo, menú diario y eliminación. | Reutilizar el flujo actual 3D; no crear un segundo CRUD paralelo. |
| Generación, revisión e historial de recursos 3D | ✅ | Nuevo: ar.upload/history/generate/regenerate/review/status | El nuevo ya contiene el flujo privado por fotografías, tarea, revisión y publicación. No se probó proveedor real. | Servicio, worker, almacenamiento y variables son dependencias externas al alcance web. |
| Menú diario y disponibilidad | ⚠️ | Anterior: owner.save_daily_menu/update_menu_type/toggle_dish_availability | Nuevo edita disponibilidad de plato en 3D y lee menús, sin gestión diaria equivalente. | Definir contrato de fecha, estado y disponibilidad. |
| Importación de Excel/Word/fotografía con previsualización | ⚠️ | Anterior: catalog y owner.import_menu_preview/apply; nuevo: owner.api_ai_dish_from_photo | Borrador por foto existente; faltan importación de documentos, plantillas y confirmación masiva. | Extracción/importación son dependencias de servicios fuera del alcance. |
| Auditoría de menú por IA | ⚠️ | Anterior: owner.audit_restaurant_menu/suggest_menu_dish_correction; nuevo: owner.api_ai_audit_menu | Existe API de auditoría; falta la experiencia de revisión y corrección equivalente. | Mejorar contrato de errores y resultado antes de conectar acciones. |
| Negocio, sucursales y equipo | ⚠️ | Anterior: admin, companies, platform, business_access; nuevo: public.api_company/api_user_companies | Consultas y contexto de empresa existentes; faltan gestión y permisos desde interfaces completas. | No asumir que disponer de repositorio equivale a CRUD autorizado. |
| Activación empresarial y suscripciones | ❌ | Anterior: companies, business_access; nuevo: company_nav_allowed | No hay flujo web equivalente; company_nav_allowed aún devuelve True. Menú 3D usa comprobaciones específicas de permiso. | Reglas de suscripción y verificación requieren trabajo fuera del alcance. |
| Editor privado de sitio y marca | ❌ | Anterior: sites.editor/site_api/logo/publish; nuevo: business.show público | Falta editor privado equivalente. | Frontera compartida: no modificar renderizado público ni publicación sin coordinar contrato. |
| Mesas, QR y sesiones | ⚠️ | Anterior: salon; nuevo: salon.index/api_mesas | Vista mínima y respuesta de mesas vacía, con nota de migración pendiente. | Tablas/servicios de mesa fuera del alcance; bloqueo para completar el flujo. |
| Pedidos en mesa, atención y cuenta dividida | ❌ | Anterior: salon.place_table_order/request_waiter/divide/staff_pay_share | No hay rutas equivalentes. | Mantener importes en unidades consistentes y validación de propiedad. |
| Cocina/KDS | ⚠️ | Anterior: market.desk/manage_order; nuevo: kitchen.index/api_pedidos | API lista pendientes; plantilla contiene título y texto, sin tablero ni actualización de estado. | El texto “tiempo real” no está respaldado por el template actual. |
| Cola, turnos, aforo y limpieza | ❌ | Anterior: flow y salon.staff_clean | No hay blueprint flow ni operaciones equivalentes. | Depende de sesiones y medición; no usar números del prototipo. |
| Inventario, adicionales, lotes y producción | ❌ | Anterior: market.inventory/configure_addon, logic.inventory_lots, home_kitchen.prepare | Sin flujos web equivalentes. | Almacén, reservas de stock y cálculo son dependencias fuera del alcance. |
| Puntos, clientes y beneficios | ⚠️ | Anterior: loyalty; nuevo: loyalty.index/api_saldo | El nuevo devuelve puntos=0/nivel=bronce con aviso de pendiente. | No presentar saldo provisional como real; falta soporte de datos. |
| Despensa, recetas y planificación personal | ⚠️ | Anterior: home_kitchen; nuevo: pantry.index/api_despensa | Devuelve items=[] y nota de migración pendiente. | La página es un contenedor, no funcionalidad completa. |
| Promociones y campañas | ⚠️ | Anterior: admin.add_promotion, market.configure_coupon, ecosystem.campaign; nuevo: public.api_promotions | Consulta disponible; gestión privada no equivalente. | Campañas y cupones requieren contrato de negocio. |
| Administración de usuarios y restaurantes | ⚠️ | Anterior: admin.users/manage_user/restaurants/manage_restaurant; nuevo: admin.dashboard/api_stats | Nuevo panel resume empresas y administradores; no consola CRUD/moderación equivalente. | Los scripts heredados no sustituyen rutas y formularios. |
| Moderación y centro de confianza | ⚠️ | Anterior: admin.moderation_dashboard y trust_center; nuevo: public.api_moderation/api_audit | Lectura de registros, sin cola de revisión y resolución equivalentes. | Revisión y auditoría transaccional requieren servicios. |
| Radar administrativo y reclamación de negocios | ⚠️ | Anterior: discovery/commercial_radar/business_access; nuevo: public.api_discovery_sources/api_discovery_due | Solo lectura de fuentes/pendientes; discovery nuevo es búsqueda pública y no sustituye radar. | El nombre del blueprint no determina equivalencia. |
| Analítica operativa y global | ⚠️ | Anterior: admin.analytics_api/bi_overview_api e intelligence; nuevo: admin.api_stats/owner.api_resumen | Métricas básicas; faltan tableros, filtros y agregados equivalentes. | Servicios de indicadores fuera del alcance; evitar datos demostrativos. |
| Copiloto con acciones preparadas y confirmación | ❌ | Anterior: copilot.prepare_action/confirm_action/chat | Nuevo copilot.js llama a recomendaciones; no hay protocolo equivalente de acciones. | Mantener separación entre sugerencia y operación autorizada. |
| Auditoría y anclaje de integridad | ⚠️ | Anterior: trust_center y utilidades; nuevo: public.api_audit y ANCHOR_STORE | Consulta de auditoría no equivale a firma/anclaje. | Criptografía, contratos y jobs fuera del alcance; no copiar claves. |
| Navegación privada por rol y estados responsive | ⚠️ | Prototipo: sidebar/roleHeader/mobileNav; nuevo: base.html y partials | Navegación parcial, sin estructura privada equivalente del prototipo. | Resolver mediante layout privado aislado; no tocar CSS público global. |

## 4. Diferencias HTML, CSS y JavaScript con el prototipo

### 4.1 Contrato visual de referencia y diferencia actual

| Elemento | Prototipo interno (`ecosistema-demo.html`) | Nuevo | Trabajo web futuro |
| --- | --- | --- | --- |
| Estructura | shell(): .layout > sidebar + main; topbar y contenido | base.html utiliza header compartido, main-content y footer | Crear o seleccionar una base privada separada; no alterar el layout público. |
| Sidebar | Columna 252px, sticky, 100vh, grupos de navegación por rol | Partials nav_owner/nav_admin con enlaces básicos; base no reproduce shell() | Jerarquía, estado activo y menú móvil accesible ligados a permisos reales. |
| Cabecera | Topbar 70px; búsqueda, contexto, acciones y avatar | internal_workspace_header muestra migas; no el conjunto de controles | Recrear estructura; cada acción requiere endpoint o estado pendiente explícito. |
| Lienzo y espaciado | Contenido 26px, ancho máximo 1500px, grids con gap 14px | No hay contrato privado equivalente cargado de forma aislada | Tokens privados para tamaño, espaciado y densidad. |
| Paleta | --bg #0e1520; --panel #151f2d; --panel2 #1b2838; --text #eef5f7; --muted #9bacbb; --teal #56d6c0; --gold #e8bd72 | theme_head solicita theme-tokens.css y responsive-tokens.css en rutas inexistentes | Definir contrato privado; no restaurar masivamente CSS anterior sobre el sitio público. |
| Tipografía | Inter/system-ui, base 14px/1.5; títulos Georgia/serif | base.html solicita DM Sans, DM Serif Text, Lora y Manrope | Alinear tipografía del sistema con el prototipo y comprobar carga/fallback. |
| Tarjetas y controles | Radio general 18px; botones 11px, padding 10px 14px; cards con borde/sombra | Paneles owner/admin usan una card básica y listas | Componentes privados coherentes: KPIs, tablas, badges y formularios. |
| Panel empresarial | 4 KPIs, actividad de ventas, alertas y acciones | Lista de restaurantes, plan y reseñas | Falta estructura de tablero; mostrar vacío/no disponible cuando no exista métrica real. |
| Panel administrador | KPIs globales, distribución, cola y moderación | Conteos y lista de empresas | Faltan tablas operativas, filtros, indicadores y acciones. |
| Pantallas de comensal | Inicio propio, pedidos, favoritos, historial, recetas, puntos, perfil | No existe espacio personal equivalente completo | Separar experiencia autenticada de explorar el sitio público. |
| Salón y cocina | Representaciones operativas, estados, tablas/cards | Plantillas de salón/cocina mínimas | Construir estructura visual una vez definidos los contratos operativos. |
| 3D privado | Referencia general de catálogo/menú; no flujo técnico completo del proveedor | ar/manage.html dispone de dialogs, tabla/grid, paginación y confirmación | Conservar flujo existente y adaptar solo presentación privada; no tocar ar público. |
| Responsive | Breakpoints 1100px, 760px y 390px; sidebar y navegación móvil | private-shell.js usa 1100px; mobile_navigation se excluye cuando sr_private | No basta coincidir un breakpoint: falta navegación privada móvil equivalente. |
| Temas | Prototipo interno oscuro con tokens propios | JS permite tema claro/oscuro con hojas de tokens ausentes | Oscuro como referencia; validar estados claros solo si se conserva esa capacidad. |
| Animación y accesibilidad | Transiciones .2s y componentes/modal demostrativos | base.html desactiva ciertas animaciones globalmente; hay helpers de accesibilidad parciales | Aplicar reduced-motion, foco, Escape, aria y validación sin copiar modales demo tal cual. |

### 4.2 Diferencias JavaScript y contrato de interacción

- El prototipo usa `state`, `setRole`, `go`, `routeContent` y `render` para generar pantallas. **No es autenticación**: el selector de rol no debe habilitar permisos reales en el destino. Solo se reutiliza la representación visual, nunca sus cifras, arrays, éxitos simulados o confirmaciones ficticias.
- En el nuevo, las páginas se sirven con Jinja y los módulos JS operan sobre IDs específicos. Deben conservarse la validación del servidor, CSRF y el contexto de empresa al conectar los componentes del prototipo.
- `app/static/js/admin.js` solicita `/admin/api/analytics` y operaciones sobre `/admin/restaurant/<id>`; el nuevo solo registra `/admin/` y `/admin/api/stats` para ese blueprint. Es código heredado sin contrato equivalente; verificar además si se carga antes de considerar que el fallo afecta una pantalla activa.
- `app/static/js/copilot.js` envía a `/descubrir/api/recommend`; no reproduce `/api/copilot/actions` ni la confirmación de acciones del anterior. No renombrar recomendaciones como copiloto operativo.
- `private-shell.js` busca `#sr-navigation`, `.sr-menu-button` y `.sr-backdrop`. La futura plantilla debe ofrecer esos elementos o adaptar el controlador: copiar únicamente CSS no completa el menú.
- `security.js` intercepta `fetch` same-origin para añadir CSRF y escapa texto. Conservar esas garantías; unificar helpers para evitar doble manejo de envíos, errores y estado de sesión.
- `menu3d-admin.js` y sus dialogs son flujo nuevo existente. Evitar una segunda implementación del alta/edición de platos en otra pantalla.
- Notificaciones, búsqueda, shell y responsive tienen módulos separados. Inventariar cargas por página y retirar duplicidades solo dentro del sistema; el sitio público comparte varios archivos.
- No sustituir las rutas públicas desde JS ni mantener URLs del anterior como cadenas literales. Para las futuras páginas privadas, inyectar URLs del servidor mediante `url_for`/atributos de configuración y acordar los formatos JSON.

### 4.3 Referencias a recursos ausentes en las plantillas actuales

Comprobación estática de argumentos literales `filename=...`. No implica que todas las referencias se rendericen en cada ruta. Se incluyen referencias públicas como advertencia de frontera, no como autorización para corregirlas.

| Recurso ausente | Plantillas que lo referencian | Tratamiento |
| --- | --- | --- |
| css/theme-tokens.css | app/templates/500.html, app/templates/partials/theme_head.html | Compartido/público: coordinar; aislar su efecto en la futura base privada. |
| css/shell.css | app/templates/500.html | Compartido/público: coordinar; aislar su efecto en la futura base privada. |
| manifest.json | app/templates/base.html | Compartido/público: coordinar; aislar su efecto en la futura base privada. |
| js/auth/food-scene.js | app/templates/business_plans.html | Compartido/público: coordinar; aislar su efecto en la futura base privada. |
| assets/img/brand-mark.svg | app/templates/offline.html | Compartido/público: coordinar; aislar su efecto en la futura base privada. |
| css/business-sites.css | app/templates/business/show.html | Compartido/público: coordinar; aislar su efecto en la futura base privada. |
| css/responsive-tokens.css | app/templates/partials/theme_head.html | Compartido/público: coordinar; aislar su efecto en la futura base privada. |

### 4.4 Fronteras que no deben modificarse indirectamente

`app/templates/base.html`, `partials/header.html`, `partials/footer.html`, `partials/theme_head.html`, `app/static/css/main.css`, `site.css`, `header.css`, `shell.js`, `theme.js` y el service worker son compartidos o públicos. No reemplazarlos para conseguir el aspecto privado.

La clasificación `sr_private` de `base.html` omite `ar`: `/ar/gestion` es una pantalla privada que hereda presentación pública y no activa `private-shell.js`. La futura solución debe distinguir endpoint privado, sin reclasificar todo `ar`, pues también contiene menús públicos.

Los HTML del prototipo público no tienen blueprints. Inventario de páginas estáticas (solo referencia; sin lógica transferible):

| Página del prototipo | Uso en esta fase |
| --- | --- |
| accesibilidad.html | Sitio público excluido |
| ayuda.html | Sitio público excluido |
| como-funciona.html | Sitio público excluido |
| comunidad.html | Sitio público excluido |
| contacto.html | Sitio público excluido |
| cookies.html | Sitio público excluido |
| descubrir.html | Sitio público excluido |
| ecosistema-demo.html | Referencia interna por roles |
| experiencias.html | Sitio público excluido |
| index.html | Sitio público excluido |
| ingresar.html | Referencia secundaria de acceso |
| menu-3d.html | Sitio público excluido |
| mercado.html | Sitio público excluido |
| negocios.html | Sitio público excluido |
| nosotros.html | Sitio público excluido |
| offline.html | Sitio público excluido |
| privacidad.html | Sitio público excluido |
| registrarse.html | Referencia secundaria de acceso |
| terminos.html | Sitio público excluido |

## 5. Variables de entorno y puntos de aplicación

Se registran **solo nombres, presencia y referencias de código**. No se incluyen valores, credenciales, correos, hosts privados, tokens ni cadenas de conexión. Tener una clave declarada no acredita que sea válida, que el proveedor esté activo o que exista saldo.

### 5.1 Mapa de aplicación

| Variables | Dónde se aplican / situación | Implicación para el sistema web |
| --- | --- | --- |
| SECRET_KEY | Sesiones y CSRF, mediante Config/create_app | Solo servidor; nunca exponer a Jinja/JS. |
| APP_ENV, FLASK_DEBUG, FLASK_TESTING | Arranque y validación de entorno | No usar pruebas para ocultar errores de integración ni activar debug en producción. |
| FLASK_APP, FLASK_ENV, FLASK_RUN_HOST, FLASK_RUN_PORT | CLI de Flask / .flaskenv | Variables de lanzador; ausencia de referencia Python no significa que no se utilicen. Verificar versión/arranque, fuera de la UI. |
| DATA_BACKEND, DATABASE_URL, DATABASE_SSLMODE, SMARTRESTO_REQUIRED_TABLES | Config y app/db/connection.py | Disponibilidad del sistema y esquema requerido; ninguna consulta SQL desde el navegador. |
| DATABASE_POOL_MAX, DATABASE_POOL_TIMEOUT, DATABASE_CONNECT_TIMEOUT, DATABASE_STATEMENT_TIMEOUT_MS, DATABASE_LOCK_TIMEOUT_MS | Conexión y límites PostgreSQL | Afectan latencia y 503; web debe tratar errores y reintentos, no cambiar estas opciones. |
| SESSION_COOKIE_SECURE, SESSION_COOKIE_SAMESITE, SESSION_LIFETIME_SECONDS | Sesión Flask | Acceso, expiración, redirección y mensajes; depende de HTTPS/despliegue. |
| WTF_CSRF_ENABLED, WTF_CSRF_TIME_LIMIT | Flask-WTF y formularios/fetch | Token en formularios y X-CSRFToken en mutaciones; no desactivar para migrar. |
| TRUSTED_PROXY_COUNT | ProxyFix | Afecta IP/host/esquema; revisar despliegue antes de rate limits o enlaces absolutos. |
| MAX_CONTENT_LENGTH, PROFILE_IMAGE_STORAGE | Límite de request y almacenamiento de imágenes | Validación cliente coherente con límite real del servidor; 413 con mensaje útil. |
| AI_BASE_URL, OPENROUTER_API_KEY, AI_MODEL, AI_VISION_MODEL, AI_TIMEOUT | app/ai/client.py y flujos de foto/recomendación/auditoría | Clave solo servidor; UI debe distinguir no configurado, pendiente, error y respuesta simulada. |
| ADMIN_AI_BASE_URL, ADMIN_AI_MODEL, ADMIN_AI_TIMEOUT | Declaradas en nuevo .env, sin referencias en app inspeccionada | Falta integración administrativa equivalente; no asumir que cambian owner/api/ai. |
| SECURITY_EMAIL_PROVIDER, SECURITY_FROM_EMAIL, RESEND_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER | Declaradas en nuevo .env, sin consumidor en app inspeccionada | Recuperación y avisos requieren servicio fuera del alcance antes de conectar formularios. |
| SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD | Alternativa documentada en .env.example anterior | No trasladar por defecto: primero elegir el contrato de envío y proveedor habilitado. |
| SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY | app/services/menu3d_storage.py; solo en ejemplo nuevo durante la lectura | Gestión 3D necesita almacenamiento servidor. No equivalen a DATABASE_URL ni se pueden enviar al cliente. |
| MENU3D_PROVIDER, MESHY_API_KEY, MESHY_MODEL, MENU3D_ASSET_HOSTS | Proveedor/validación 3D; presentes en .env.example nuevo | Habilitación, generación y confianza en URLs; consumidor exacto en tabla individual. Integración/worker fuera del alcance. |
| MENU3D_DAILY_LIMIT, MENU3D_COMPANY_BYTES | app/services/menu3d.py | Cuotas de uso; la UI debe presentar el rechazo sin eludir validación servidor. |
| ANCHOR_STORE | Declarada en nuevo .env sin referencia en app inspeccionada | No demuestra integridad o anclaje activo. No crear indicadores de verificación ficticios. |
| ANCHOR_PSEUDONYM_SECRET, ANCHOR_MODE, CHAIN_RPC_URL, CHAIN_ID, ANCHOR_CONTRACT, ANCHOR_PRIVATE_KEY, ANCHOR_CONTRACT_METHOD, AUDIT_SIGNING_KEY, INTEGRITY_AUTO_ENABLED, INTEGRITY_INTERVAL_SECONDS, INTEGRITY_BATCH_SIZE | Declaraciones del anterior; no equivalencia nueva | Dependen de utilidades/jobs/infraestructura fuera de alcance; no copiar secretos. |
| AI_API_KEY, AI_IMAGE_MODEL | Variables del ejemplo anterior | Confirmar consumidor; no adoptar alias antiguos ni prometer generación de imágenes por declararlos. |

### 5.2 Inventario individual y referencias

La columna de referencias identifica coincidencias del nombre en el código de aplicación inspeccionado, no certifica su ejecución. Se limita a cuatro ubicaciones por variable para legibilidad. «No encontrada» significa que no hay consumidor identificado en esa aplicación; las variables CLI son una excepción explícita. `.env.example` no se carga automáticamente como `.env`.

| Variable | Declaración anterior | Declaración nueva | Referencias nuevas / alternativa anterior |
| --- | --- | --- | --- |
| ADMIN_AI_BASE_URL | .env, .env.example | .env | No encontrada en nuevo; anterior: utils/llm_provider.py:40 |
| ADMIN_AI_MODEL | .env, .env.example | .env | No encontrada en nuevo; anterior: utils/llm_provider.py:41 |
| ADMIN_AI_TIMEOUT | .env, .env.example | .env | No encontrada en nuevo; anterior: utils/llm_provider.py:57 |
| AI_API_KEY | .env.example | — | No encontrada en nuevo; anterior: utils/kitchen_assistant.py:45; utils/llm_provider.py:36 |
| AI_BASE_URL | .env, .env.example | .env | app/ai/client.py:27 |
| AI_IMAGE_MODEL | .env.example | — | No encontrada en nuevo |
| AI_MODEL | .env, .env.example | .env | app/ai/client.py:29 |
| AI_TIMEOUT | .env, .env.example | .env | app/ai/client.py:31 |
| AI_VISION_MODEL | .env, .env.example | .env | app/ai/client.py:30 |
| ANCHOR_CONTRACT | .env | — | No encontrada en nuevo; anterior: utils/anchor_job.py:29; utils/anchor_job.py:30 |
| ANCHOR_CONTRACT_METHOD | .env | — | No encontrada en nuevo |
| ANCHOR_MODE | .env | — | No encontrada en nuevo; anterior: utils/anchor_job.py:8; utils/anchor_job.py:30 |
| ANCHOR_PRIVATE_KEY | .env | — | No encontrada en nuevo |
| ANCHOR_PSEUDONYM_SECRET | .env | — | No encontrada en nuevo; anterior: utils/blockchain_anchor.py:21; utils/blockchain_anchor.py:24 |
| ANCHOR_STORE | .env | .env | No encontrada en nuevo; anterior: utils/anchor_store.py:4; utils/anchor_store.py:150 |
| APP_ENV | — | .env | app/config.py:98; app/config.py:100; app/config.py:106; app/config.py:110 |
| AUDIT_SIGNING_KEY | .env | — | No encontrada en nuevo |
| CHAIN_ID | .env | — | No encontrada en nuevo |
| CHAIN_RPC_URL | .env | — | No encontrada en nuevo; anterior: utils/anchor_job.py:29; utils/anchor_job.py:30 |
| DATABASE_CONNECT_TIMEOUT | .env.example | .env | app/config.py:147; app/db/connection.py:269 |
| DATABASE_LOCK_TIMEOUT_MS | .env.example | .env | app/config.py:149; app/db/connection.py:242 |
| DATABASE_POOL_MAX | .env.example | .env | app/config.py:145; app/db/connection.py:276 |
| DATABASE_POOL_TIMEOUT | .env.example | .env | app/config.py:146; app/db/connection.py:277 |
| DATABASE_SSLMODE | .env, .env.example | .env | app/config.py:53; app/config.py:71; app/config.py:139; app/config.py:142 |
| DATABASE_STATEMENT_TIMEOUT_MS | .env.example | .env | app/config.py:148; app/db/connection.py:238 |
| DATABASE_URL | .env, .env.example | .env | app/config.py:55; app/config.py:59; app/config.py:61; app/config.py:63 |
| DATA_BACKEND | .env, .env.example | .env | app/config.py:138; app/config.py:177; app/config.py:178; app/db/connection.py:170 |
| FLASK_APP | — | .flaskenv | No encontrada en nuevo |
| FLASK_DEBUG | .env, .env.example | .env | app/config.py:99; app/config.py:161 |
| FLASK_ENV | — | .flaskenv | No encontrada en nuevo |
| FLASK_RUN_HOST | — | .flaskenv | No encontrada en nuevo |
| FLASK_RUN_PORT | — | .flaskenv | No encontrada en nuevo |
| FLASK_TESTING | — | .env | app/config.py:100; app/db/connection.py:57 |
| INTEGRITY_AUTO_ENABLED | .env | — | No encontrada en nuevo |
| INTEGRITY_BATCH_SIZE | .env | — | No encontrada en nuevo |
| INTEGRITY_INTERVAL_SECONDS | .env | — | No encontrada en nuevo |
| MAX_CONTENT_LENGTH | — | .env | app/config.py:104 |
| MENU3D_ASSET_HOSTS | — | .env.example | app/ai/image_to_3d.py:68 |
| MENU3D_COMPANY_BYTES | — | .env.example | app/services/menu3d.py:104; app/services/menu3d.py:162 |
| MENU3D_DAILY_LIMIT | — | .env.example | app/services/menu3d.py:143 |
| MENU3D_PROVIDER | — | .env.example | app/ai/image_to_3d.py:90 |
| MESHY_API_KEY | — | .env.example | app/ai/image_to_3d.py:26; app/ai/image_to_3d.py:28 |
| MESHY_MODEL | — | .env.example | app/ai/image_to_3d.py:39 |
| OPENROUTER_API_KEY | .env, .env.example | .env | app/ai/client.py:6; app/ai/client.py:28 |
| PROFILE_IMAGE_STORAGE | — | .env | app/config.py:135; app/config.py:174; app/config.py:175 |
| RESEND_API_KEY | .env, .env.example | .env | No encontrada en nuevo; anterior: utils/security_delivery.py:14; utils/security_delivery.py:35 |
| SECRET_KEY | .env, .env.example | .env | app/config.py:101; app/config.py:165; app/config.py:167; app/config.py:169 |
| SECURITY_EMAIL_PROVIDER | .env, .env.example | .env | No encontrada en nuevo; anterior: utils/security_delivery.py:13; utils/security_delivery.py:25 |
| SECURITY_FROM_EMAIL | .env, .env.example | .env | No encontrada en nuevo; anterior: utils/security_delivery.py:14; utils/security_delivery.py:26 |
| SESSION_COOKIE_SAMESITE | — | .env | app/config.py:113; app/config.py:119; app/config.py:171; app/config.py:172 |
| SESSION_COOKIE_SECURE | .env, .env.example | .env | app/config.py:110; app/config.py:117; app/config.py:162; app/config.py:163 |
| SESSION_LIFETIME_SECONDS | — | .env | app/config.py:115 |
| SMARTRESTO_REQUIRED_TABLES | — | .env | app/db/connection.py:352; app/db/connection.py:361; app/db/connection.py:369 |
| SMTP_HOST | .env.example | — | No encontrada en nuevo; anterior: utils/security_delivery.py:14; utils/security_delivery.py:29 |
| SMTP_PASSWORD | .env.example | — | No encontrada en nuevo; anterior: utils/security_delivery.py:14; utils/security_delivery.py:33 |
| SMTP_PORT | .env.example | — | No encontrada en nuevo; anterior: utils/security_delivery.py:27 |
| SMTP_USERNAME | .env.example | — | No encontrada en nuevo; anterior: utils/security_delivery.py:14; utils/security_delivery.py:33 |
| SUPABASE_SERVICE_ROLE_KEY | — | .env.example | app/services/menu3d_storage.py:17; app/services/menu3d_storage.py:20 |
| SUPABASE_URL | — | .env.example | app/services/menu3d_storage.py:16; app/services/menu3d_storage.py:20 |
| TRUSTED_PROXY_COUNT | — | .env | app/config.py:132; app/__init__.py:33 |
| TWILIO_ACCOUNT_SID | .env, .env.example | .env | No encontrada en nuevo; anterior: utils/security_delivery.py:12; utils/security_delivery.py:21 |
| TWILIO_AUTH_TOKEN | .env, .env.example | .env | No encontrada en nuevo; anterior: utils/security_delivery.py:12; utils/security_delivery.py:23 |
| TWILIO_FROM_NUMBER | .env, .env.example | .env | No encontrada en nuevo; anterior: utils/security_delivery.py:12; utils/security_delivery.py:23 |
| WTF_CSRF_ENABLED | — | .env | app/config.py:122 |
| WTF_CSRF_TIME_LIMIT | — | .env | app/config.py:124; app/config.py:125 |

### 5.3 Inconsistencias de configuración a resolver fuera de esta fase

- El `.env.example` nuevo documenta el módulo 3D, pero no reproduce la configuración base de sesiones, PostgreSQL e IA que el arranque necesita. No es una plantilla completa de instalación.
- El `.env` nuevo repite `DATABASE_POOL_MAX`, `DATABASE_POOL_TIMEOUT`, `DATABASE_CONNECT_TIMEOUT`, `DATABASE_STATEMENT_TIMEOUT_MS`, `DATABASE_LOCK_TIMEOUT_MS` y `PROFILE_IMAGE_STORAGE`. Consolidar en una futura tarea de configuración; no deducir precedencia ni efectividad a partir del orden sin comprobar el cargador y las variables del proceso.
- Las claves de Supabase Storage/Meshy están en el ejemplo, no en el `.env` inspeccionado. Podrían inyectarse mediante el entorno del proceso; no se comprobó esa posibilidad ni la conectividad.
- La UI privada 3D permite 1–4 fotos de hasta 2 MB cada una. El valor por defecto de `MAX_CONTENT_LENGTH` en Config es 2 MB para toda la solicitud. Debe comprobarse el límite efectivo y el overhead multipart antes de anunciar 4 fotos; no se cambia `.env` ni el servicio en esta fase.
- También existen opciones leídas por código que no necesariamente aparecen en estos archivos, como `SMARTRESTO_TEST_DATABASE_URL` y `SMARTRESTO_TEST_SCHEMA`. Son de pruebas/aislamiento, nunca controles del usuario final.

## 6. Riesgos, duplicidades y mejoras en lugar de copia literal

| Prioridad | Hallazgo / evidencia | Recomendación y límite |
| --- | --- | --- |
| Alta | Base y recursos compartidos entre privado y público; sr_private excluye ar.manage | Separar layout y recursos privados. Cualquier edición compartida exige coordinación con la persona responsable del sitio público. |
| Alta | Anterior usa app_records/JSONB e identificadores uid/rid/id; nuevo usa id_usuario/id_restaurante/id_empresa y repositorios relacionales | Definir contratos de payload, identidad y autorización. No copiar SQL/servicios del anterior dentro de blueprints. |
| Alta | Reglas de pedido no son equivalentes a pantallas: estado pending frente a estados como Entregado/Cancelado; precios frente a importes en centavos | Documentar unidades y transiciones; no convertir por intuición. Bloqueo de servicios/datos fuera de alcance. |
| Alta | Plantillas de salón, puntos y despensa anuncian operaciones que el backend deja pendientes | Mostrar disponibilidad honesta; no conectar un botón a un mock que aparente operación real. |
| Alta | app/core/nav.py mantiene lista manual de endpoints y company_nav_allowed devuelve True | Usar contratos de navegación y permisos reales; validar servidor en cada mutación. core está fuera del alcance actual: informar dependencia antes de editarlo. |
| Alta | Nuevo app/db/connection.py consulta Config/entorno para TESTING y no necesariamente current_app.config | Corregir aislamiento en tarea de datos/pruebas; no ejecutar integración sobre la base operativa. Hallazgo de revisión anterior aún visible en el código. |
| Alta | Anterior test/conftest.py: service_db ejecuta DELETE FROM public.app_records pese a usar esquema QA | No copiar ni ejecutar esa fixture sin corregir y validar aislamiento. El nombre public explícito puede saltarse search_path. Es una dependencia de pruebas, no cambio web autorizado. |
| Alta | Nuevo app/ai/client.py: _safe_json puede devolver lista/número y call_json usa parsed.get; fallback expande mock_payload opcional | Validar estructura de salida y normalizar payload. El cliente IA está fuera del alcance web; rutas deben mostrar errores coherentes mientras tanto. |
| Media | JS admin heredado solicita rutas inexistentes; copilot.js es recomendador y no acciones confirmadas | Inventario por carga real y contrato. Migrar comportamiento, no nombres ni archivos completos sin revisar. |
| Media | Dos generaciones visuales: CSS ANTERIOR, CSS público nuevo, módulos 3D y shell | No reactivar todas las hojas antiguas. Tokens privados y componentes aislados con carga por página. |
| Media | Anterior tiene owner y catalog para gestión/importación; nuevo ya añade CRUD privado ar | Unificar experiencia sobre el flujo actual que corresponda; evitar operaciones duplicadas y divergentes. |
| Media | auth.logout nuevo admite GET y POST; anterior solo POST | Planificar salida POST+CSRF y actualizar enlaces privados; no romper header público compartido. |
| Media | owner.dashboard calcula promedio simple por restaurante | Si el indicador pretende ser promedio de todas las reseñas, ponderar por cantidad. Acordar significado del KPI antes de migrarlo. |
| Media | Recomendador nuevo arma catálogo limitado a 10 restaurantes × 5 platos | No prometer cobertura completa ni personalización equivalente. El límite debe explicitarse/solucionarse en servicio fuera del alcance. |
| Media | Anterior models/loyalty.py carga sesiones y filtra en Python | No copiar patrón a tablas nuevas; filtros/agregaciones en repositorio son tarea aparte. |
| Media | URL /owner/dashboard cambia a /owner/; /puntos a /recompensas/; /home/ a /mi-cocina/ | Actualizar URLs del sistema y definir compatibilidad cuando sea necesaria; no trasladar enlaces duros del anterior. |
| Media | README anterior referencia guías locales ausentes; README nuevo vacío | Este documento no sustituye documentación de despliegue ni prueba que las guías antiguas estén vigentes. |
| Media | Cambios concurrentes en ambos árboles y trabajo público en curso | Antes de una futura fase, releer los archivos implicados y acordar ownership. No revertir ni sobrescribir cambios ajenos. |

## 7. Dependencias fuera de alcance y criterios para una fase posterior

No se pueden completar mesas, stock, pagos, fidelización, despensa, recuperación o mensajería únicamente agregando HTML/JS si faltan contratos y persistencia. Esos cambios se deben comunicar y autorizar como ampliación de alcance, no ocultar dentro de rutas.

Secuencia sugerida, **sin ejecutarla en esta fase**:

1. Delimitar layout privado y sus recursos, preservando el sitio público y las rutas públicas de 3D.
2. Acordar matriz de permisos, endpoints y formatos de datos para las funciones que ya tienen soporte backend.
3. Integrar pantallas privadas existentes (paneles y gestión 3D) con componentes del prototipo y estados vacíos/error reales.
4. Resolver por separado las dependencias de modelos/servicios/esquema señaladas; recién después incorporar el resto de flujos.
5. Verificar cada recorrido por rol: sesión, empresa, validación, CSRF, error de red, duplicación de envío y móvil/teclado. Las pruebas de integración requieren entorno aislado comprobado.

Criterios de aceptación para el sistema futuro: ninguna regresión pública; ninguna cifra demo presentada como real; enlaces privados resolubles; acciones autorizadas por servidor; estado de carga/error explícito; misma funcionalidad acordada del anterior; apariencia alineada con la referencia interna del prototipo. Los criterios no se declaran cumplidos ahora.

## 8. Inventario de blueprints

**S:** sistema web (incluye autenticación y operaciones de comensales). **P:** público, excluido de cambios. **M:** frontera mixta; revisar uso antes de modificar. **T:** transversal/infraestructura. La clasificación indica ownership de migración, no garantiza que la ruta exija login.

### Proyecto anterior

| Blueprint | Prefijo de registro | Declaraciones | Distribución de alcance |
| --- | --- | --- | --- |
| main | (sin prefijo) | 23 | P: 17, S: 6 |
| auth | /auth | 11 | S: 11 |
| admin | /admin | 30 | S: 30 |
| owner | /owner | 15 | S: 15 |
| ai | (sin prefijo) | 2 | M: 2 |
| market | /mercado | 37 | P: 3, S: 34 |
| ecosystem | /experiencias | 16 | M: 16 |
| comunicacion | /bandeja | 16 | S: 16 |
| platform | /api/platform | 4 | S: 2, T: 2 |
| business_access | (sin prefijo) | 3 | S: 3 |
| discovery | (sin prefijo) | 16 | S: 16 |
| commercial_radar | (sin prefijo) | 4 | S: 4 |
| sites | (sin prefijo) | 10 | M: 7, P: 3 |
| catalog | (sin prefijo) | 14 | P: 2, S: 12 |
| recommendation_history | (sin prefijo) | 1 | S: 1 |
| recommendations | (sin prefijo) | 4 | M: 4 |
| food_experience | (sin prefijo) | 1 | M: 1 |
| intelligence | (sin prefijo) | 2 | S: 2 |
| copilot | (sin prefijo) | 4 | S: 4 |
| trust_center | (sin prefijo) | 4 | S: 4 |
| salon | (sin prefijo) | 25 | S: 25 |
| flow | (sin prefijo) | 12 | S: 12 |
| loyalty | (sin prefijo) | 6 | S: 6 |
| home_kitchen | /home | 6 | S: 6 |
| admin_ai | /admin/api/ai | 3 | S: 3 |
| companies | (sin prefijo) | 5 | S: 5 |

### Proyecto nuevo

| Blueprint | Prefijo de registro | Declaraciones | Distribución de alcance |
| --- | --- | --- | --- |
| public | (sin prefijo) | 28 | P: 12, S: 16 |
| auth | /auth | 7 | S: 7 |
| discovery | /descubrir | 4 | M: 1, P: 3 |
| business | /negocio | 2 | P: 2 |
| owner | /owner | 4 | S: 4 |
| admin | /admin | 2 | S: 2 |
| salon | /salon | 2 | S: 2 |
| kitchen | /kitchen | 2 | S: 2 |
| market | /mercado | 3 | P: 2, S: 1 |
| loyalty | /recompensas | 2 | S: 2 |
| pantry | /mi-cocina | 2 | S: 2 |
| ar | /ar | 20 | P: 7, S: 13 |

## 9. Inventario completo de rutas

Cada fila incluye URL, endpoint Flask, método, función/ubicación y plantilla. `—` significa que no se encontró `render_template` en la función ni en helpers locales recorridos: puede ser JSON, redirección, descarga u otro tipo de respuesta. Las expresiones de plantilla no literales se muestran tal como aparecen en el código. Los renderizados indirectos entre módulos o decoradores pueden añadir otras plantillas en ejecución.

La columna función enlaza al archivo fuente; el número después de `:` es la línea observada. Las ubicaciones son una instantánea y pueden cambiar con ediciones concurrentes. Plantillas de errores globales y respuestas de decoradores no se repiten en cada fila.

### 9.1 RecomenRestaurant

#### admin

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/admin/analytics` | GET | `admin.analytics_page` | `analytics_page` — [views/admin.py:818](C:/Users/DELL/RecomenRestaurant/views/admin.py:818) | `admin/analytics.html` |
| S | `/admin/api/analytics` | GET | `admin.analytics_api` | `analytics_api` — [views/admin.py:878](C:/Users/DELL/RecomenRestaurant/views/admin.py:878) | — |
| S | `/admin/api/bi/overview` | GET | `admin.bi_overview_api` | `bi_overview_api` — [views/admin.py:950](C:/Users/DELL/RecomenRestaurant/views/admin.py:950) | — |
| S | `/admin/api/categories` | POST | `admin.create_dynamic_category` | `create_dynamic_category` — [views/admin.py:515](C:/Users/DELL/RecomenRestaurant/views/admin.py:515) | — |
| S | `/admin/api/performance` | GET | `admin.performance_metrics` | `performance_metrics` — [views/admin.py:170](C:/Users/DELL/RecomenRestaurant/views/admin.py:170) | — |
| S | `/admin/api/stats` | GET | `admin.stats_api` | `stats_api` — [views/admin.py:1152](C:/Users/DELL/RecomenRestaurant/views/admin.py:1152) | — |
| S | `/admin/categories` | GET | `admin.categories` | `categories` — [views/admin.py:1105](C:/Users/DELL/RecomenRestaurant/views/admin.py:1105) | `admin/categories.html` |
| S | `/admin/category` | POST | `admin.new_category` | `new_category` — [views/admin.py:1113](C:/Users/DELL/RecomenRestaurant/views/admin.py:1113) | — |
| S | `/admin/category/<int:id>` | DELETE | `admin.delete_category` | `delete_category` — [views/admin.py:1136](C:/Users/DELL/RecomenRestaurant/views/admin.py:1136) | — |
| S | `/admin/configuracion-sitio` | GET, POST | `admin.website_settings` | `website_settings` — [views/admin.py:1609](C:/Users/DELL/RecomenRestaurant/views/admin.py:1609) | `admin/website_settings.html` |
| S | `/admin/controles` | GET, POST | `admin.controls` | `controls` — [views/admin.py:304](C:/Users/DELL/RecomenRestaurant/views/admin.py:304) | `admin/controls.html` |
| S | `/admin/dashboard` | GET | `admin.dashboard` | `dashboard` — [views/admin.py:209](C:/Users/DELL/RecomenRestaurant/views/admin.py:209) | `admin/dashboard.html` |
| S | `/admin/moderation` | GET | `admin.moderation_dashboard` | `moderation_dashboard` — [views/admin.py:1181](C:/Users/DELL/RecomenRestaurant/views/admin.py:1181) | `admin/moderation.html` |
| S | `/admin/moderation/auto-filter` | POST | `admin.auto_filter_restaurants` | `auto_filter_restaurants` — [views/admin.py:1461](C:/Users/DELL/RecomenRestaurant/views/admin.py:1461) | — |
| S | `/admin/moderation/restaurant/<int:id>/history` | GET | `admin.restaurant_moderation_history` | `restaurant_moderation_history` — [views/admin.py:1388](C:/Users/DELL/RecomenRestaurant/views/admin.py:1388) | — |
| S | `/admin/moderation/restaurant/<int:id>/notify-owner` | POST | `admin.notify_restaurant_owner` | `notify_restaurant_owner` — [views/admin.py:1413](C:/Users/DELL/RecomenRestaurant/views/admin.py:1413) | — |
| S | `/admin/moderation/restaurant/<int:id>/review` | POST | `admin.review_restaurant` | `review_restaurant` — [views/admin.py:1275](C:/Users/DELL/RecomenRestaurant/views/admin.py:1275) | — |
| S | `/admin/operaciones` | GET | `admin.operations` | `operations` — [views/admin.py:269](C:/Users/DELL/RecomenRestaurant/views/admin.py:269) | `admin/operations.html` |
| S | `/admin/operaciones/<int:oid>` | GET | `admin.operation_detail` | `operation_detail` — [views/admin.py:291](C:/Users/DELL/RecomenRestaurant/views/admin.py:291) | `admin/operation_detail.html` |
| S | `/admin/restaurant/<int:id>` | GET, PUT, DELETE | `admin.manage_restaurant` | `manage_restaurant` — [views/admin.py:716](C:/Users/DELL/RecomenRestaurant/views/admin.py:716) | — |
| S | `/admin/restaurant/<int:id>/edit` | GET | `admin.edit_restaurant` | `edit_restaurant` — [views/admin.py:650](C:/Users/DELL/RecomenRestaurant/views/admin.py:650) | `admin/restaurant_form.html` |
| S | `/admin/restaurant/<int:id>/promo` | POST | `admin.add_promotion` | `add_promotion` — [views/admin.py:769](C:/Users/DELL/RecomenRestaurant/views/admin.py:769) | — |
| S | `/admin/restaurant/<int:id>/update` | POST | `admin.update_restaurant` | `update_restaurant` — [views/admin.py:683](C:/Users/DELL/RecomenRestaurant/views/admin.py:683) | — |
| S | `/admin/restaurant/analyze-file` | POST | `admin.analyze_restaurant_upload` | `analyze_restaurant_upload` — [views/admin.py:412](C:/Users/DELL/RecomenRestaurant/views/admin.py:412) | — |
| S | `/admin/restaurant/import-excel` | POST | `admin.restaurant_excel_import` | `restaurant_excel_import` — [views/admin.py:387](C:/Users/DELL/RecomenRestaurant/views/admin.py:387) | `admin/restaurant_import_preview.html` |
| S | `/admin/restaurant/new` | GET, POST | `admin.new_restaurant` | `new_restaurant` — [views/admin.py:560](C:/Users/DELL/RecomenRestaurant/views/admin.py:560) | `admin/restaurant_form.html` |
| S | `/admin/restaurant/template.xlsx` | GET | `admin.restaurant_excel_template` | `restaurant_excel_template` — [views/admin.py:377](C:/Users/DELL/RecomenRestaurant/views/admin.py:377) | — |
| S | `/admin/restaurants` | GET | `admin.restaurants` | `restaurants` — [views/admin.py:325](C:/Users/DELL/RecomenRestaurant/views/admin.py:325) | `admin/restaurants.html`, `owner/restaurants.html` |
| S | `/admin/user/<int:id>` | GET, PUT, DELETE | `admin.manage_user` | `manage_user` — [views/admin.py:988](C:/Users/DELL/RecomenRestaurant/views/admin.py:988) | — |
| S | `/admin/users` | GET | `admin.users` | `users` — [views/admin.py:977](C:/Users/DELL/RecomenRestaurant/views/admin.py:977) | `admin/users.html` |

#### admin_ai

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/admin/api/ai/analyze` | POST | `admin_ai.analyze_text` | `analyze_text` — [views/admin_ai_routes.py:60](C:/Users/DELL/RecomenRestaurant/views/admin_ai_routes.py:60) | — |
| S | `/admin/api/ai/health` | GET | `admin_ai.health` | `health` — [views/admin_ai_routes.py:54](C:/Users/DELL/RecomenRestaurant/views/admin_ai_routes.py:54) | — |
| S | `/admin/api/ai/moderation-query` | POST | `admin_ai.moderation_query` | `moderation_query` — [views/admin_ai_routes.py:154](C:/Users/DELL/RecomenRestaurant/views/admin_ai_routes.py:154) | — |

#### ai

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| M | `/api/ai/chat` | POST | `ai.chat` | `chat` — [views/ai_routes.py:315](C:/Users/DELL/RecomenRestaurant/views/ai_routes.py:315) | — |
| M | `/api/ai/interpret` | POST | `ai.interpret` | `interpret` — [views/ai_routes.py:127](C:/Users/DELL/RecomenRestaurant/views/ai_routes.py:127) | — |

#### auth

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/auth/api/favorites` | GET | `auth.get_favorites_api` | `get_favorites_api` — [views/auth.py:452](C:/Users/DELL/RecomenRestaurant/views/auth.py:452) | — |
| S | `/auth/api/favorites/toggle` | POST | `auth.toggle_favorite` | `toggle_favorite` — [views/auth.py:402](C:/Users/DELL/RecomenRestaurant/views/auth.py:402) | — |
| S | `/auth/favorites` | GET | `auth.favorites` | `favorites` — [views/auth.py:241](C:/Users/DELL/RecomenRestaurant/views/auth.py:241) | `favorites.html` |
| S | `/auth/login` | GET, POST | `auth.login` | `login` — [views/auth.py:19](C:/Users/DELL/RecomenRestaurant/views/auth.py:19) | `login.html` |
| S | `/auth/logout` | POST | `auth.logout` | `logout` — [views/auth.py:197](C:/Users/DELL/RecomenRestaurant/views/auth.py:197) | — |
| S | `/auth/profile` | GET | `auth.profile` | `profile` — [views/auth.py:209](C:/Users/DELL/RecomenRestaurant/views/auth.py:209) | `auth/profile.html`, `auth/profile_owner.html` |
| S | `/auth/profile/photo/<kind>` | GET | `auth.profile_photo` | `profile_photo` — [views/auth.py:272](C:/Users/DELL/RecomenRestaurant/views/auth.py:272) | — |
| S | `/auth/profile/update` | POST | `auth.update_profile` | `update_profile` — [views/auth.py:289](C:/Users/DELL/RecomenRestaurant/views/auth.py:289) | `template` |
| S | `/auth/recuperar` | GET, POST | `auth.recover` | `recover` — [views/auth.py:152](C:/Users/DELL/RecomenRestaurant/views/auth.py:152) | `auth/recovery.html` |
| S | `/auth/register` | GET, POST | `auth.register` | `register` — [views/auth.py:54](C:/Users/DELL/RecomenRestaurant/views/auth.py:54) | `register.html` |
| S | `/auth/seguridad` | GET, POST | `auth.account_security` | `account_security` — [views/auth.py:125](C:/Users/DELL/RecomenRestaurant/views/auth.py:125) | `auth/security.html` |

#### business_access

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/admin/verificacion-empresarial` | GET, POST | `business_access.review` | `review` — [views/business_access.py:67](C:/Users/DELL/RecomenRestaurant/views/business_access.py:67) | `admin/business_verifications.html` |
| S | `/owner/acceso/<int:rid>` | GET, POST | `business_access.access` | `access` — [views/business_access.py:20](C:/Users/DELL/RecomenRestaurant/views/business_access.py:20) | `owner/business_access.html` |
| S | `/owner/acceso/<int:rid>/verificacion` | POST | `business_access.submit_verification` | `submit_verification` — [views/business_access.py:40](C:/Users/DELL/RecomenRestaurant/views/business_access.py:40) | — |

#### catalog

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| P | `/catalog-media/<int:media_id>` | GET | `catalog.media` | `media` — [views/catalog.py:123](C:/Users/DELL/RecomenRestaurant/views/catalog.py:123) | — |
| P | `/catalog/qr/<token>` | GET | `catalog.table_menu` | `table_menu` — [views/catalog.py:166](C:/Users/DELL/RecomenRestaurant/views/catalog.py:166) | — |
| S | `/owner/api/catalog/<int:rid>` | GET | `catalog.catalog_api` | `catalog_api` — [views/catalog.py:36](C:/Users/DELL/RecomenRestaurant/views/catalog.py:36) | — |
| S | `/owner/api/catalog/<int:rid>/draft` | POST | `catalog.draft` | `draft` — [views/catalog.py:45](C:/Users/DELL/RecomenRestaurant/views/catalog.py:45) | — |
| S | `/owner/api/catalog/<int:rid>/drafts/<int:draft_id>` | PUT | `catalog.update_draft` | `update_draft` — [views/catalog.py:55](C:/Users/DELL/RecomenRestaurant/views/catalog.py:55) | — |
| S | `/owner/api/catalog/<int:rid>/drafts/<int:draft_id>/confirm` | POST | `catalog.confirm` | `confirm` — [views/catalog.py:63](C:/Users/DELL/RecomenRestaurant/views/catalog.py:63) | — |
| S | `/owner/api/catalog/<int:rid>/import-preview` | POST | `catalog.import_preview` | `import_preview` — [views/catalog.py:148](C:/Users/DELL/RecomenRestaurant/views/catalog.py:148) | — |
| S | `/owner/api/catalog/<int:rid>/imports/<import_id>/confirm` | POST | `catalog.import_confirm` | `import_confirm` — [views/catalog.py:158](C:/Users/DELL/RecomenRestaurant/views/catalog.py:158) | — |
| S | `/owner/api/catalog/<int:rid>/photo` | POST | `catalog.photo` | `photo` — [views/catalog.py:86](C:/Users/DELL/RecomenRestaurant/views/catalog.py:86) | — |
| S | `/owner/api/catalog/<int:rid>/products/<int:product_id>/availability` | PATCH | `catalog.availability` | `availability` — [views/catalog.py:73](C:/Users/DELL/RecomenRestaurant/views/catalog.py:73) | — |
| S | `/owner/api/catalog/<int:rid>/voice` | POST | `catalog.voice` | `voice` — [views/catalog.py:107](C:/Users/DELL/RecomenRestaurant/views/catalog.py:107) | — |
| S | `/owner/catalog` | GET | `catalog.dashboard` | `dashboard` — [views/catalog.py:24](C:/Users/DELL/RecomenRestaurant/views/catalog.py:24) | `catalog/dashboard.html` |
| S | `/owner/catalog/<int:rid>/template.xlsx` | GET | `catalog.template` | `template` — [views/catalog.py:138](C:/Users/DELL/RecomenRestaurant/views/catalog.py:138) | — |
| S | `/owner/catalog/tables/<int:table_id>/qr.svg` | GET | `catalog.table_qr` | `table_qr` — [views/catalog.py:184](C:/Users/DELL/RecomenRestaurant/views/catalog.py:184) | — |

#### commercial_radar

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/admin/api/radar-comercial` | GET | `commercial_radar.listing` | `listing` — [views/commercial_radar.py:31](C:/Users/DELL/RecomenRestaurant/views/commercial_radar.py:31) | — |
| S | `/admin/api/radar-comercial/<int:pid>/<action>` | POST | `commercial_radar.action` | `action` — [views/commercial_radar.py:47](C:/Users/DELL/RecomenRestaurant/views/commercial_radar.py:47) | — |
| S | `/admin/api/radar-comercial/discover` | POST | `commercial_radar.discover` | `discover` — [views/commercial_radar.py:41](C:/Users/DELL/RecomenRestaurant/views/commercial_radar.py:41) | — |
| S | `/admin/radar-comercial` | GET | `commercial_radar.dashboard` | `dashboard` — [views/commercial_radar.py:24](C:/Users/DELL/RecomenRestaurant/views/commercial_radar.py:24) | `admin/commercial_radar.html` |

#### companies

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/activar-empresa` | GET, POST | `companies.activate` | `activate` — [views/companies.py:148](C:/Users/DELL/RecomenRestaurant/views/companies.py:148) | `company_activate.html` |
| S | `/admin/empresas` | GET, POST | `companies.admin_companies` | `admin_companies` — [views/companies.py:44](C:/Users/DELL/RecomenRestaurant/views/companies.py:44) | `admin/companies.html` |
| S | `/admin/empresas/activacion/<int:uid>` | POST | `companies.activation_link` | `activation_link` — [views/companies.py:111](C:/Users/DELL/RecomenRestaurant/views/companies.py:111) | `admin/company_activation.html` |
| S | `/admin/usuarios-conectados` | GET | `companies.connected` | `connected` — [views/companies.py:34](C:/Users/DELL/RecomenRestaurant/views/companies.py:34) | `admin/company_presence.html` |
| S | `/owner/suscripciones` | GET | `companies.owner_subscriptions` | `owner_subscriptions` — [views/companies.py:101](C:/Users/DELL/RecomenRestaurant/views/companies.py:101) | `owner/subscriptions.html` |

#### comunicacion

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/bandeja/` | GET | `comunicacion.inbox` | `inbox` — [views/communication.py:45](C:/Users/DELL/RecomenRestaurant/views/communication.py:45) | `communication/inbox.html` |
| S | `/bandeja/mensajes/<int:tid>` | GET | `comunicacion.thread` | `thread` — [views/communication.py:111](C:/Users/DELL/RecomenRestaurant/views/communication.py:111) | `communication/thread.html` |
| S | `/bandeja/mensajes/<int:tid>/archivo/<int:mid>` | GET | `comunicacion.file` | `file` — [views/communication.py:142](C:/Users/DELL/RecomenRestaurant/views/communication.py:142) | — |
| S | `/bandeja/mensajes/<int:tid>/leer` | POST | `comunicacion.seen` | `seen` — [views/communication.py:130](C:/Users/DELL/RecomenRestaurant/views/communication.py:130) | — |
| S | `/bandeja/mensajes/<int:tid>/responder` | POST | `comunicacion.reply` | `reply` — [views/communication.py:123](C:/Users/DELL/RecomenRestaurant/views/communication.py:123) | — |
| S | `/bandeja/notificaciones` | GET | `comunicacion.notifications` | `notifications` — [views/communication.py:255](C:/Users/DELL/RecomenRestaurant/views/communication.py:255) | `communication/notifications.html` |
| S | `/bandeja/notificaciones/<int:nid>/<action>` | POST | `comunicacion.notification_action` | `notification_action` — [views/communication.py:277](C:/Users/DELL/RecomenRestaurant/views/communication.py:277) | — |
| S | `/bandeja/notificaciones/feed` | GET | `comunicacion.notification_feed` | `notification_feed` — [views/communication.py:286](C:/Users/DELL/RecomenRestaurant/views/communication.py:286) | — |
| S | `/bandeja/notificaciones/leer` | POST | `comunicacion.read_notifications` | `read_notifications` — [views/communication.py:265](C:/Users/DELL/RecomenRestaurant/views/communication.py:265) | — |
| S | `/bandeja/nueva` | POST | `comunicacion.start` | `start` — [views/communication.py:77](C:/Users/DELL/RecomenRestaurant/views/communication.py:77) | — |
| S | `/bandeja/pendientes` | GET | `comunicacion.unread_counts` | `unread_counts` — [views/communication.py:34](C:/Users/DELL/RecomenRestaurant/views/communication.py:34) | — |
| S | `/bandeja/reclamos` | GET | `comunicacion.cases` | `cases` — [views/communication.py:159](C:/Users/DELL/RecomenRestaurant/views/communication.py:159) | `communication/cases.html` |
| S | `/bandeja/reclamos/<int:cid>` | GET | `comunicacion.case_detail` | `case_detail` — [views/communication.py:179](C:/Users/DELL/RecomenRestaurant/views/communication.py:179) | `communication/case.html` |
| S | `/bandeja/reclamos/<int:cid>/actualizar` | POST | `comunicacion.update_case` | `update_case` — [views/communication.py:227](C:/Users/DELL/RecomenRestaurant/views/communication.py:227) | — |
| S | `/bandeja/reclamos/<int:cid>/analizar` | POST | `comunicacion.analyze_case` | `analyze_case` — [views/communication.py:189](C:/Users/DELL/RecomenRestaurant/views/communication.py:189) | `communication/case.html` |
| S | `/bandeja/reclamos/<int:cid>/archivo` | GET | `comunicacion.case_file` | `case_file` — [views/communication.py:220](C:/Users/DELL/RecomenRestaurant/views/communication.py:220) | — |

#### copilot

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/api/copilot/actions` | POST | `copilot.prepare_action` | `prepare_action` — [views/copilot.py:217](C:/Users/DELL/RecomenRestaurant/views/copilot.py:217) | — |
| S | `/api/copilot/actions/<int:aid>/confirm` | POST | `copilot.confirm_action` | `confirm_action` — [views/copilot.py:236](C:/Users/DELL/RecomenRestaurant/views/copilot.py:236) | — |
| S | `/api/copilot/chat` | POST | `copilot.chat` | `chat` — [views/copilot.py:124](C:/Users/DELL/RecomenRestaurant/views/copilot.py:124) | — |
| S | `/copilot` | GET | `copilot.page` | `page` — [views/copilot.py:120](C:/Users/DELL/RecomenRestaurant/views/copilot.py:120) | `copilot.html` |

#### discovery

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/admin/api/discovery/candidates` | GET | `discovery.candidates` | `candidates` — [views/discovery.py:76](C:/Users/DELL/RecomenRestaurant/views/discovery.py:76) | — |
| S | `/admin/api/discovery/candidates/<int:candidate_id>/invite` | POST | `discovery.invite` | `invite` — [views/discovery.py:135](C:/Users/DELL/RecomenRestaurant/views/discovery.py:135) | — |
| S | `/admin/api/discovery/candidates/<int:candidate_id>/review` | POST | `discovery.review` | `review` — [views/discovery.py:126](C:/Users/DELL/RecomenRestaurant/views/discovery.py:126) | — |
| S | `/admin/api/discovery/claims/<int:claim_id>/review` | POST | `discovery.review_claim` | `review_claim` — [views/discovery.py:145](C:/Users/DELL/RecomenRestaurant/views/discovery.py:145) | — |
| S | `/admin/api/discovery/export/osm` | GET | `discovery.export_osm` | `export_osm` — [views/discovery.py:63](C:/Users/DELL/RecomenRestaurant/views/discovery.py:63) | — |
| S | `/admin/api/discovery/google` | POST | `discovery.google` | `google` — [views/discovery.py:153](C:/Users/DELL/RecomenRestaurant/views/discovery.py:153) | — |
| S | `/admin/api/discovery/runs` | POST | `discovery.start_run` | `start_run` — [views/discovery.py:117](C:/Users/DELL/RecomenRestaurant/views/discovery.py:117) | — |
| S | `/admin/api/discovery/sources` | GET | `discovery.sources` | `sources` — [views/discovery.py:86](C:/Users/DELL/RecomenRestaurant/views/discovery.py:86) | — |
| S | `/admin/api/discovery/sources` | POST | `discovery.add_source` | `add_source` — [views/discovery.py:93](C:/Users/DELL/RecomenRestaurant/views/discovery.py:93) | — |
| S | `/admin/api/discovery/sources/<int:source_id>` | PATCH | `discovery.pause_source` | `pause_source` — [views/discovery.py:100](C:/Users/DELL/RecomenRestaurant/views/discovery.py:100) | — |
| S | `/admin/discovery` | GET | `discovery.dashboard` | `dashboard` — [views/discovery.py:49](C:/Users/DELL/RecomenRestaurant/views/discovery.py:49) | `discovery/dashboard.html` |
| S | `/admin/discovery/google-lookup` | GET | `discovery.google_page` | `google_page` — [views/discovery.py:56](C:/Users/DELL/RecomenRestaurant/views/discovery.py:56) | `discovery/google.html` |
| S | `/api/discovery/claims` | POST | `discovery.claim` | `claim` — [views/discovery.py:173](C:/Users/DELL/RecomenRestaurant/views/discovery.py:173) | — |
| S | `/api/discovery/invitations/preview` | POST | `discovery.preview` | `preview` — [views/discovery.py:166](C:/Users/DELL/RecomenRestaurant/views/discovery.py:166) | — |
| S | `/owner/discovery` | GET | `discovery.owner_space` | `owner_space` — [views/discovery.py:186](C:/Users/DELL/RecomenRestaurant/views/discovery.py:186) | `discovery/owner.html` |
| S | `/reclamar` | GET | `discovery.claim_page` | `claim_page` — [views/discovery.py:160](C:/Users/DELL/RecomenRestaurant/views/discovery.py:160) | `discovery/claim.html` |

#### ecosystem

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| M | `/experiencias/` | GET | `ecosystem.home` | `home` — [views/ecosystem.py:49](C:/Users/DELL/RecomenRestaurant/views/ecosystem.py:49) | `ecosystem/home.html` |
| M | `/experiencias/ciudad` | GET | `ecosystem.city` | `city` — [views/ecosystem.py:241](C:/Users/DELL/RecomenRestaurant/views/ecosystem.py:241) | `ecosystem/city.html` |
| M | `/experiencias/contexto` | POST | `ecosystem.context` | `context` — [views/ecosystem.py:65](C:/Users/DELL/RecomenRestaurant/views/ecosystem.py:65) | — |
| M | `/experiencias/escena` | GET | `ecosystem.food_scene` | `food_scene` — [views/ecosystem.py:24](C:/Users/DELL/RecomenRestaurant/views/ecosystem.py:24) | — |
| M | `/experiencias/grupos` | GET, POST | `ecosystem.groups` | `groups` — [views/ecosystem.py:100](C:/Users/DELL/RecomenRestaurant/views/ecosystem.py:100) | `ecosystem/groups.html` |
| M | `/experiencias/grupos/<int:gid>` | GET, POST | `ecosystem.group` | `group` — [views/ecosystem.py:145](C:/Users/DELL/RecomenRestaurant/views/ecosystem.py:145) | `ecosystem/group.html` |
| M | `/experiencias/grupos/unirse` | POST | `ecosystem.join_group` | `join_group` — [views/ecosystem.py:114](C:/Users/DELL/RecomenRestaurant/views/ecosystem.py:114) | — |
| M | `/experiencias/interaccion/<int:oid>` | POST | `ecosystem.interaction` | `interaction` — [views/ecosystem.py:327](C:/Users/DELL/RecomenRestaurant/views/ecosystem.py:327) | — |
| M | `/experiencias/modelos/<int:oid>` | GET | `ecosystem.dish_model` | `dish_model` — [views/ecosystem.py:319](C:/Users/DELL/RecomenRestaurant/views/ecosystem.py:319) | — |
| M | `/experiencias/modelos/<int:oid>/metadata` | GET | `ecosystem.dish_model_metadata` | `dish_model_metadata` — [views/ecosystem.py:358](C:/Users/DELL/RecomenRestaurant/views/ecosystem.py:358) | — |
| M | `/experiencias/negocio/<int:rid>` | GET | `ecosystem.business` | `business` — [views/ecosystem.py:175](C:/Users/DELL/RecomenRestaurant/views/ecosystem.py:175) | `ecosystem/business.html` |
| M | `/experiencias/negocio/<int:rid>/campana` | POST | `ecosystem.campaign` | `campaign` — [views/ecosystem.py:205](C:/Users/DELL/RecomenRestaurant/views/ecosystem.py:205) | — |
| M | `/experiencias/negocio/<int:rid>/modelo` | POST | `ecosystem.upload_model` | `upload_model` — [views/ecosystem.py:281](C:/Users/DELL/RecomenRestaurant/views/ecosystem.py:281) | — |
| M | `/experiencias/publicaciones` | GET, POST | `ecosystem.publications` | `publications` — [views/ecosystem.py:253](C:/Users/DELL/RecomenRestaurant/views/ecosystem.py:253) | `ecosystem/publications.html` |
| M | `/experiencias/recompensas` | GET | `ecosystem.rewards` | `rewards` — [views/ecosystem.py:346](C:/Users/DELL/RecomenRestaurant/views/ecosystem.py:346) | `ecosystem/rewards.html` |
| M | `/experiencias/scan` | GET, POST | `ecosystem.scan` | `scan` — [views/ecosystem.py:78](C:/Users/DELL/RecomenRestaurant/views/ecosystem.py:78) | `ecosystem/scan.html`, `ecosystem/scan_result.html` |

#### flow

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/cola/<int:rid>` | GET | `flow.public` | `public` — [views/flow.py:40](C:/Users/DELL/RecomenRestaurant/views/flow.py:40) | `flow/public.html` |
| S | `/cola/<int:rid>` | POST | `flow.take_turn` | `take_turn` — [views/flow.py:51](C:/Users/DELL/RecomenRestaurant/views/flow.py:51) | — |
| S | `/cola/<int:rid>/estado.json` | GET | `flow.public_status` | `public_status` — [views/flow.py:70](C:/Users/DELL/RecomenRestaurant/views/flow.py:70) | — |
| S | `/cola/<int:rid>/turno/<int:qid>/cancelar` | POST | `flow.cancel_turn` | `cancel_turn` — [views/flow.py:61](C:/Users/DELL/RecomenRestaurant/views/flow.py:61) | — |
| S | `/salon/<int:rid>/aforo.json` | GET | `flow.occupancy` | `occupancy` — [views/flow.py:153](C:/Users/DELL/RecomenRestaurant/views/flow.py:153) | — |
| S | `/salon/<int:rid>/cola` | GET | `flow.desk` | `desk` — [views/flow.py:77](C:/Users/DELL/RecomenRestaurant/views/flow.py:77) | `flow/desk.html` |
| S | `/salon/<int:rid>/cola/<int:qid>/ausente` | POST | `flow.absent` | `absent` — [views/flow.py:134](C:/Users/DELL/RecomenRestaurant/views/flow.py:134) | — |
| S | `/salon/<int:rid>/cola/<int:qid>/cancelar` | POST | `flow.cancel_staff` | `cancel_staff` — [views/flow.py:126](C:/Users/DELL/RecomenRestaurant/views/flow.py:126) | — |
| S | `/salon/<int:rid>/cola/<int:qid>/llamar` | POST | `flow.call` | `call` — [views/flow.py:110](C:/Users/DELL/RecomenRestaurant/views/flow.py:110) | — |
| S | `/salon/<int:rid>/cola/<int:qid>/sentar` | POST | `flow.sit` | `sit` — [views/flow.py:118](C:/Users/DELL/RecomenRestaurant/views/flow.py:118) | — |
| S | `/salon/<int:rid>/cola/configurar` | POST | `flow.configure` | `configure` — [views/flow.py:100](C:/Users/DELL/RecomenRestaurant/views/flow.py:100) | — |
| S | `/salon/<int:rid>/cola/qr.svg` | GET | `flow.entry_qr` | `entry_qr` — [views/flow.py:142](C:/Users/DELL/RecomenRestaurant/views/flow.py:142) | — |

#### food_experience

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| M | `/api/food-experience` | GET | `food_experience.food_experience` | `food_experience` — [views/food_experience.py:12](C:/Users/DELL/RecomenRestaurant/views/food_experience.py:12) | — |

#### home_kitchen

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/home/` | GET | `home_kitchen.index` | `index` — [views/home_kitchen.py:35](C:/Users/DELL/RecomenRestaurant/views/home_kitchen.py:35) | `home_kitchen.html` |
| S | `/home/<collection>/<int:item_id>/remove` | POST | `home_kitchen.remove` | `remove` — [views/home_kitchen.py:82](C:/Users/DELL/RecomenRestaurant/views/home_kitchen.py:82) | — |
| S | `/home/pantry` | POST | `home_kitchen.pantry_save` | `pantry_save` — [views/home_kitchen.py:51](C:/Users/DELL/RecomenRestaurant/views/home_kitchen.py:51) | — |
| S | `/home/plan` | POST | `home_kitchen.plan_save` | `plan_save` — [views/home_kitchen.py:88](C:/Users/DELL/RecomenRestaurant/views/home_kitchen.py:88) | — |
| S | `/home/prepare` | POST | `home_kitchen.prepare` | `prepare` — [views/home_kitchen.py:98](C:/Users/DELL/RecomenRestaurant/views/home_kitchen.py:98) | — |
| S | `/home/recipes` | POST | `home_kitchen.recipe_save` | `recipe_save` — [views/home_kitchen.py:62](C:/Users/DELL/RecomenRestaurant/views/home_kitchen.py:62) | — |

#### intelligence

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/api/inteligencia` | GET | `intelligence.api` | `api` — [views/intelligence.py:62](C:/Users/DELL/RecomenRestaurant/views/intelligence.py:62) | — |
| S | `/inteligencia` | GET | `intelligence.dashboard` | `dashboard` — [views/intelligence.py:58](C:/Users/DELL/RecomenRestaurant/views/intelligence.py:58) | `intelligence.html` |

#### loyalty

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/mis-reservas` | GET | `loyalty.reservations` | `reservations` — [views/loyalty.py:49](C:/Users/DELL/RecomenRestaurant/views/loyalty.py:49) | `loyalty/wallet.html` |
| S | `/mis-reservas/<int:reservation_id>/cancelar` | POST | `loyalty.cancel_reservation` | `cancel_reservation` — [views/loyalty.py:58](C:/Users/DELL/RecomenRestaurant/views/loyalty.py:58) | — |
| S | `/owner/puntos/<int:rid>` | GET | `loyalty.customers` | `customers` — [views/loyalty.py:72](C:/Users/DELL/RecomenRestaurant/views/loyalty.py:72) | `loyalty/customers.html` |
| S | `/puntos` | GET | `loyalty.wallet_page` | `wallet_page` — [views/loyalty.py:16](C:/Users/DELL/RecomenRestaurant/views/loyalty.py:16) | `loyalty/wallet.html` |
| S | `/puntos/cumpleanos` | POST | `loyalty.birthday` | `birthday` — [views/loyalty.py:27](C:/Users/DELL/RecomenRestaurant/views/loyalty.py:27) | — |
| S | `/puntos/preferencias` | POST | `loyalty.preferences` | `preferences` — [views/loyalty.py:39](C:/Users/DELL/RecomenRestaurant/views/loyalty.py:39) | — |

#### main

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| P | `/` | GET | `main.index` | `index` — [views/main.py:111](C:/Users/DELL/RecomenRestaurant/views/main.py:111) | `index.html` |
| P | `/api/catalog/<int:restaurant_id>/map` | GET | `main.business_map` | `business_map` — [views/main.py:898](C:/Users/DELL/RecomenRestaurant/views/main.py:898) | — |
| P | `/api/catalog/compare` | GET | `main.compare_catalog` | `compare_catalog` — [views/main.py:862](C:/Users/DELL/RecomenRestaurant/views/main.py:862) | — |
| P | `/api/catalog/products/<int:product_id>` | GET | `main.product_card` | `product_card` — [views/main.py:885](C:/Users/DELL/RecomenRestaurant/views/main.py:885) | — |
| P | `/api/categories` | GET | `main.api_categories` | `api_categories` — [views/main.py:545](C:/Users/DELL/RecomenRestaurant/views/main.py:545) | — |
| P | `/api/dishes/search` | GET | `main.search_dishes` | `search_dishes` — [views/main.py:821](C:/Users/DELL/RecomenRestaurant/views/main.py:821) | — |
| S | `/api/notifications` | GET | `main.get_notifications` | `get_notifications` — [views/main.py:765](C:/Users/DELL/RecomenRestaurant/views/main.py:765) | — |
| S | `/api/notifications/<int:notification_id>/read` | POST | `main.mark_notification_read` | `mark_notification_read` — [views/main.py:789](C:/Users/DELL/RecomenRestaurant/views/main.py:789) | — |
| S | `/api/notifications/read-all` | POST | `main.mark_all_notifications_read` | `mark_all_notifications_read` — [views/main.py:805](C:/Users/DELL/RecomenRestaurant/views/main.py:805) | — |
| P | `/api/restaurant/<int:restaurant_id>/analyze` | POST | `main.api_analyze_restaurant` | `api_analyze_restaurant` — [views/main.py:527](C:/Users/DELL/RecomenRestaurant/views/main.py:527) | — |
| P | `/api/restaurant/<int:restaurant_id>/evaluate` | GET | `main.api_evaluate_restaurant` | `api_evaluate_restaurant` — [views/main.py:508](C:/Users/DELL/RecomenRestaurant/views/main.py:508) | — |
| P | `/api/restaurants/nearby` | GET | `main.api_nearby_restaurants` | `api_nearby_restaurants` — [views/main.py:556](C:/Users/DELL/RecomenRestaurant/views/main.py:556) | — |
| P | `/api/restaurants/top-rated` | GET | `main.api_top_rated` | `api_top_rated` — [views/main.py:611](C:/Users/DELL/RecomenRestaurant/views/main.py:611) | — |
| S | `/api/reviews` | POST | `main.add_review` | `add_review` — [views/main.py:677](C:/Users/DELL/RecomenRestaurant/views/main.py:677) | — |
| S | `/api/save-location` | POST | `main.save_location` | `save_location` — [views/main.py:633](C:/Users/DELL/RecomenRestaurant/views/main.py:633) | — |
| P | `/api/search` | POST | `main.search` | `search` — [views/main.py:320](C:/Users/DELL/RecomenRestaurant/views/main.py:320) | — |
| P | `/api/trust/verify/<int:review_id>` | GET | `main.verify_anchor` | `verify_anchor` — [views/main.py:741](C:/Users/DELL/RecomenRestaurant/views/main.py:741) | — |
| P | `/explorar` | GET | `main.explore_catalog` | `explore_catalog` — [views/main.py:856](C:/Users/DELL/RecomenRestaurant/views/main.py:856) | `catalog/explore.html` |
| P | `/informacion/<section>` | GET | `main.information` | `information` — [views/main.py:928](C:/Users/DELL/RecomenRestaurant/views/main.py:928) | `information.html` |
| P | `/ofertas` | GET | `main.offers` | `offers` — [views/main.py:153](C:/Users/DELL/RecomenRestaurant/views/main.py:153) | `offers.html` |
| P | `/para-negocios` | GET | `main.business_plans` | `business_plans` — [views/main.py:170](C:/Users/DELL/RecomenRestaurant/views/main.py:170) | `business_plans.html` |
| P | `/restaurant/<int:restaurant_id>` | GET | `main.detail` | `detail` — [views/main.py:175](C:/Users/DELL/RecomenRestaurant/views/main.py:175) | `404.html`, `500.html`, `detail.html` |
| S | `/restaurant/<int:restaurant_id>/reserve` | POST | `main.reserve` | `reserve` — [views/main.py:252](C:/Users/DELL/RecomenRestaurant/views/main.py:252) | — |

#### market

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| P | `/mercado/` | GET | `market.browse` | `browse` — [views/market.py:57](C:/Users/DELL/RecomenRestaurant/views/market.py:57) | `market/browse.html` |
| S | `/mercado/carrito` | GET | `market.cart` | `cart` — [views/market.py:185](C:/Users/DELL/RecomenRestaurant/views/market.py:185) | `market/cart.html` |
| S | `/mercado/carrito` | POST | `market.add_cart` | `add_cart` — [views/market.py:157](C:/Users/DELL/RecomenRestaurant/views/market.py:157) | — |
| S | `/mercado/carrito/cupon` | POST | `market.apply_coupon` | `apply_coupon` — [views/market.py:256](C:/Users/DELL/RecomenRestaurant/views/market.py:256) | — |
| S | `/mercado/carrito/recompensa` | POST | `market.cart_reward` | `cart_reward` — [views/market.py:246](C:/Users/DELL/RecomenRestaurant/views/market.py:246) | — |
| S | `/mercado/carrito/vaciar` | POST | `market.clear_cart` | `clear_cart` — [views/market.py:268](C:/Users/DELL/RecomenRestaurant/views/market.py:268) | — |
| S | `/mercado/cocina/<int:rid>` | GET | `market.desk` | `desk` — [views/market_kitchen.py:111](C:/Users/DELL/RecomenRestaurant/views/market_kitchen.py:111) | `market/kitchen.html` |
| S | `/mercado/cocina/<int:rid>/acreditar` | POST | `market.submit_evidence` | `submit_evidence` — [views/market_trust.py:16](C:/Users/DELL/RecomenRestaurant/views/market_trust.py:16) | — |
| S | `/mercado/cocina/<int:rid>/adicional` | POST | `market.configure_addon` | `configure_addon` — [views/market_kitchen.py:154](C:/Users/DELL/RecomenRestaurant/views/market_kitchen.py:154) | — |
| S | `/mercado/cocina/<int:rid>/configurar` | POST | `market.configure` | `configure` — [views/market_kitchen.py:116](C:/Users/DELL/RecomenRestaurant/views/market_kitchen.py:116) | — |
| S | `/mercado/cocina/<int:rid>/copiloto` | POST | `market.copilot` | `copilot` — [views/market_kitchen.py:372](C:/Users/DELL/RecomenRestaurant/views/market_kitchen.py:372) | `market/kitchen.html` |
| S | `/mercado/cocina/<int:rid>/cupon` | POST | `market.configure_coupon` | `configure_coupon` — [views/market_kitchen.py:179](C:/Users/DELL/RecomenRestaurant/views/market_kitchen.py:179) | — |
| S | `/mercado/cocina/<int:rid>/foto` | POST | `market.photo` | `photo` — [views/market_kitchen.py:357](C:/Users/DELL/RecomenRestaurant/views/market_kitchen.py:357) | `market/kitchen.html` |
| S | `/mercado/cocina/<int:rid>/inventario` | POST | `market.inventory` | `inventory` — [views/market_kitchen.py:204](C:/Users/DELL/RecomenRestaurant/views/market_kitchen.py:204) | — |
| S | `/mercado/cocina/<int:rid>/oferta` | POST | `market.publish` | `publish` — [views/market_kitchen.py:267](C:/Users/DELL/RecomenRestaurant/views/market_kitchen.py:267) | — |
| S | `/mercado/cocina/<int:rid>/oferta/<int:oid>/disponibilidad` | POST | `market.pause_offer` | `pause_offer` — [views/market_kitchen.py:342](C:/Users/DELL/RecomenRestaurant/views/market_kitchen.py:342) | — |
| S | `/mercado/cocina/<int:rid>/pedido/<int:oid>` | POST | `market.manage_order` | `manage_order` — [views/market_kitchen.py:408](C:/Users/DELL/RecomenRestaurant/views/market_kitchen.py:408) | — |
| S | `/mercado/cocina/<int:rid>/reserva/<int:reservation_id>` | POST | `market.confirm_reservation` | `confirm_reservation` — [views/market_kitchen.py:428](C:/Users/DELL/RecomenRestaurant/views/market_kitchen.py:428) | — |
| S | `/mercado/cocina/<int:rid>/simular` | POST | `market.simulate` | `simulate` — [views/market_kitchen.py:383](C:/Users/DELL/RecomenRestaurant/views/market_kitchen.py:383) | `market/kitchen.html` |
| S | `/mercado/comprar` | POST | `market.buy` | `buy` — [views/market.py:274](C:/Users/DELL/RecomenRestaurant/views/market.py:274) | — |
| S | `/mercado/confianza` | GET | `market.trust` | `trust` — [views/market_trust.py:30](C:/Users/DELL/RecomenRestaurant/views/market_trust.py:30) | `market/trust.html` |
| S | `/mercado/confianza/<int:cid>` | POST | `market.resolve` | `resolve` — [views/market_trust.py:76](C:/Users/DELL/RecomenRestaurant/views/market_trust.py:76) | — |
| S | `/mercado/confianza/<int:cid>/documento` | GET | `market.evidence` | `evidence` — [views/market_trust.py:67](C:/Users/DELL/RecomenRestaurant/views/market_trust.py:67) | — |
| S | `/mercado/confianza/senal/<int:rid>` | POST | `market.open_signal` | `open_signal` — [views/market_trust.py:54](C:/Users/DELL/RecomenRestaurant/views/market_trust.py:54) | — |
| S | `/mercado/consultar` | POST | `market.consult` | `consult` — [views/market.py:126](C:/Users/DELL/RecomenRestaurant/views/market.py:126) | — |
| S | `/mercado/interaccion` | POST | `market.interaction` | `interaction` — [views/market.py:294](C:/Users/DELL/RecomenRestaurant/views/market.py:294) | — |
| P | `/mercado/oferta/<int:oid>` | GET | `market.offer_detail` | `offer_detail` — [views/market.py:216](C:/Users/DELL/RecomenRestaurant/views/market.py:216) | `market/dish.html` |
| P | `/mercado/oferta/<int:oid>/foto` | GET | `market.offer_photo` | `offer_photo` — [views/market.py:231](C:/Users/DELL/RecomenRestaurant/views/market.py:231) | — |
| S | `/mercado/pagos/<int:rid>/notificar` | POST | `market.payment_notification` | `payment_notification` — [views/market.py:369](C:/Users/DELL/RecomenRestaurant/views/market.py:369) | — |
| S | `/mercado/pedidos` | GET | `market.orders` | `orders` — [views/market.py:304](C:/Users/DELL/RecomenRestaurant/views/market.py:304) | `market/orders.html` |
| S | `/mercado/pedidos/<int:oid>/cancelar` | POST | `market.cancel` | `cancel` — [views/market.py:441](C:/Users/DELL/RecomenRestaurant/views/market.py:441) | — |
| S | `/mercado/pedidos/<int:oid>/constancia` | GET | `market.receipt` | `receipt` — [views/market.py:409](C:/Users/DELL/RecomenRestaurant/views/market.py:409) | — |
| S | `/mercado/pedidos/<int:oid>/pagar` | POST | `market.pay` | `pay` — [views/market.py:354](C:/Users/DELL/RecomenRestaurant/views/market.py:354) | — |
| S | `/mercado/pedidos/<int:oid>/reclamo` | POST | `market.claim` | `claim` — [views/market.py:451](C:/Users/DELL/RecomenRestaurant/views/market.py:451) | — |
| S | `/mercado/pedidos/<int:oid>/repetir` | POST | `market.reorder` | `reorder` — [views/market.py:327](C:/Users/DELL/RecomenRestaurant/views/market.py:327) | — |
| S | `/mercado/pedidos/<int:oid>/valorar` | POST | `market.verified_review` | `verified_review` — [views/market.py:481](C:/Users/DELL/RecomenRestaurant/views/market.py:481) | — |
| S | `/mercado/preferencias` | POST | `market.preferences` | `preferences` — [views/market.py:108](C:/Users/DELL/RecomenRestaurant/views/market.py:108) | — |

#### owner

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/owner/dashboard` | GET | `owner.dashboard` | `dashboard` — [views/owner.py:158](C:/Users/DELL/RecomenRestaurant/views/owner.py:158) | `owner/dashboard.html` |
| S | `/owner/dish/<int:dish_id>/delete` | DELETE | `owner.delete_dish` | `delete_dish` — [views/owner.py:966](C:/Users/DELL/RecomenRestaurant/views/owner.py:966) | — |
| S | `/owner/dish/<int:dish_id>/toggle-availability` | POST | `owner.toggle_dish_availability` | `toggle_dish_availability` — [views/owner.py:997](C:/Users/DELL/RecomenRestaurant/views/owner.py:997) | — |
| S | `/owner/dish/<int:dish_id>/update` | PUT | `owner.update_dish` | `update_dish` — [views/owner.py:849](C:/Users/DELL/RecomenRestaurant/views/owner.py:849) | — |
| S | `/owner/dish/add` | POST | `owner.add_dish` | `add_dish` — [views/owner.py:750](C:/Users/DELL/RecomenRestaurant/views/owner.py:750) | — |
| S | `/owner/generate_menu` | POST | `owner.generate_menu` | `generate_menu` — [views/owner.py:1038](C:/Users/DELL/RecomenRestaurant/views/owner.py:1038) | — |
| S | `/owner/menu/<int:restaurant_id>` | GET | `owner.menu_management` | `menu_management` — [views/owner.py:183](C:/Users/DELL/RecomenRestaurant/views/owner.py:183) | `owner/menu_management.html` |
| S | `/owner/menu/<int:restaurant_id>/audit` | POST | `owner.audit_restaurant_menu` | `audit_restaurant_menu` — [views/owner.py:269](C:/Users/DELL/RecomenRestaurant/views/owner.py:269) | — |
| S | `/owner/menu/<int:restaurant_id>/audit/suggestion` | POST | `owner.suggest_menu_dish_correction` | `suggest_menu_dish_correction` — [views/owner.py:338](C:/Users/DELL/RecomenRestaurant/views/owner.py:338) | — |
| S | `/owner/menu/<int:restaurant_id>/import` | POST | `owner.import_menu_preview` | `import_menu_preview` — [views/owner.py:465](C:/Users/DELL/RecomenRestaurant/views/owner.py:465) | `owner/menu_import_preview.html` |
| S | `/owner/menu/<int:restaurant_id>/import/apply` | POST | `owner.import_menu_apply` | `import_menu_apply` — [views/owner.py:519](C:/Users/DELL/RecomenRestaurant/views/owner.py:519) | `owner/menu_import_preview.html` |
| S | `/owner/menu/<int:restaurant_id>/template/<file_format>` | GET | `owner.download_menu_template` | `download_menu_template` — [views/owner.py:435](C:/Users/DELL/RecomenRestaurant/views/owner.py:435) | — |
| S | `/owner/restaurant/<int:restaurant_id>/dishes` | GET | `owner.get_restaurant_dishes` | `get_restaurant_dishes` — [views/owner.py:1250](C:/Users/DELL/RecomenRestaurant/views/owner.py:1250) | — |
| S | `/owner/restaurant/<int:restaurant_id>/menu_type` | PUT | `owner.update_menu_type` | `update_menu_type` — [views/owner.py:1213](C:/Users/DELL/RecomenRestaurant/views/owner.py:1213) | — |
| S | `/owner/save_daily_menu` | POST | `owner.save_daily_menu` | `save_daily_menu` — [views/owner.py:1124](C:/Users/DELL/RecomenRestaurant/views/owner.py:1124) | — |

#### platform

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| T | `/api/platform/health` | GET | `platform.health` | `health` — [views/platform.py:25](C:/Users/DELL/RecomenRestaurant/views/platform.py:25) | — |
| T | `/api/platform/manifest` | GET | `platform.manifest` | `manifest` — [views/platform.py:18](C:/Users/DELL/RecomenRestaurant/views/platform.py:18) | — |
| S | `/api/platform/me` | GET | `platform.me` | `me` — [views/platform.py:59](C:/Users/DELL/RecomenRestaurant/views/platform.py:59) | — |
| S | `/api/platform/me/profile` | PATCH | `platform.update_me_profile` | `update_me_profile` — [views/platform.py:86](C:/Users/DELL/RecomenRestaurant/views/platform.py:86) | — |

#### recommendation_history

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/api/recomendaciones/historial` | GET, POST | `recommendation_history.history` | `history` — [views/recommendation_history.py:21](C:/Users/DELL/RecomenRestaurant/views/recommendation_history.py:21) | — |

#### recommendations

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| M | `/api/recomendaciones` | GET | `recommendations.api` | `api` — [views/recommendations.py:265](C:/Users/DELL/RecomenRestaurant/views/recommendations.py:265) | — |
| M | `/api/recomendaciones/contexto` | POST | `recommendations.location` | `location` — [views/recommendations.py:270](C:/Users/DELL/RecomenRestaurant/views/recommendations.py:270) | — |
| M | `/api/recomendaciones/interaccion` | POST | `recommendations.interaction` | `interaction` — [views/recommendations.py:298](C:/Users/DELL/RecomenRestaurant/views/recommendations.py:298) | — |
| M | `/recomendaciones` | GET | `recommendations.index` | `index` — [views/recommendations.py:260](C:/Users/DELL/RecomenRestaurant/views/recommendations.py:260) | `recommendations.html` |

#### salon

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/mesa/<token>` | GET | `salon.menu` | `menu` — [views/salon.py:122](C:/Users/DELL/RecomenRestaurant/views/salon.py:122) | `salon/menu.html` |
| S | `/mesa/<token>/abrir` | POST | `salon.open_table` | `open_table` — [views/salon.py:151](C:/Users/DELL/RecomenRestaurant/views/salon.py:151) | — |
| S | `/mesa/<token>/carrito` | GET | `salon.table_cart` | `table_cart` — [views/salon.py:221](C:/Users/DELL/RecomenRestaurant/views/salon.py:221) | `salon/cart.html` |
| S | `/mesa/<token>/carrito` | POST | `salon.add_to_cart` | `add_to_cart` — [views/salon.py:187](C:/Users/DELL/RecomenRestaurant/views/salon.py:187) | — |
| S | `/mesa/<token>/dividir` | POST | `salon.divide` | `divide` — [views/salon.py:302](C:/Users/DELL/RecomenRestaurant/views/salon.py:302) | — |
| S | `/mesa/<token>/estado.json` | GET | `salon.session_status` | `session_status` — [views/salon.py:334](C:/Users/DELL/RecomenRestaurant/views/salon.py:334) | — |
| S | `/mesa/<token>/pedido` | POST | `salon.place_table_order` | `place_table_order` — [views/salon.py:253](C:/Users/DELL/RecomenRestaurant/views/salon.py:253) | — |
| S | `/mesa/<token>/quitar` | POST | `salon.remove_line` | `remove_line` — [views/salon.py:243](C:/Users/DELL/RecomenRestaurant/views/salon.py:243) | — |
| S | `/mesa/<token>/sesion` | GET | `salon.session_page` | `session_page` — [views/salon.py:272](C:/Users/DELL/RecomenRestaurant/views/salon.py:272) | `salon/session.html` |
| S | `/mesa/<token>/solicitar` | POST | `salon.request_waiter` | `request_waiter` — [views/salon.py:292](C:/Users/DELL/RecomenRestaurant/views/salon.py:292) | — |
| S | `/mesa/<token>/unirme` | POST | `salon.join_table` | `join_table` — [views/salon.py:173](C:/Users/DELL/RecomenRestaurant/views/salon.py:173) | — |
| S | `/mesa/<token>/valorar` | POST | `salon.review_table` | `review_table` — [views/salon.py:319](C:/Users/DELL/RecomenRestaurant/views/salon.py:319) | — |
| S | `/owner/salon` | GET | `salon.manage_default` | `manage_default` — [views/salon.py:346](C:/Users/DELL/RecomenRestaurant/views/salon.py:346) | — |
| S | `/owner/salon/<int:rid>` | GET | `salon.manage` | `manage` — [views/salon.py:356](C:/Users/DELL/RecomenRestaurant/views/salon.py:356) | `salon/manage.html` |
| S | `/owner/salon/<int:rid>/mesa` | POST | `salon.create_table` | `create_table` — [views/salon.py:365](C:/Users/DELL/RecomenRestaurant/views/salon.py:365) | — |
| S | `/owner/salon/<int:rid>/mesa/<int:table_id>` | POST | `salon.edit_table` | `edit_table` — [views/salon.py:374](C:/Users/DELL/RecomenRestaurant/views/salon.py:374) | — |
| S | `/owner/salon/<int:rid>/mesa/<int:table_id>/qr.svg` | GET | `salon.table_qr` | `table_qr` — [views/salon.py:387](C:/Users/DELL/RecomenRestaurant/views/salon.py:387) | — |
| S | `/salon` | GET | `salon.desk_default` | `desk_default` — [views/salon.py:401](C:/Users/DELL/RecomenRestaurant/views/salon.py:401) | — |
| S | `/salon/<int:rid>` | GET | `salon.desk` | `desk` — [views/salon.py:418](C:/Users/DELL/RecomenRestaurant/views/salon.py:418) | `salon/desk.html` |
| S | `/salon/<int:rid>/abrir` | POST | `salon.staff_open` | `staff_open` — [views/salon.py:444](C:/Users/DELL/RecomenRestaurant/views/salon.py:444) | — |
| S | `/salon/<int:rid>/estado.json` | GET | `salon.desk_status` | `desk_status` — [views/salon.py:497](C:/Users/DELL/RecomenRestaurant/views/salon.py:497) | — |
| S | `/salon/<int:rid>/sesion/<int:session_id>/cerrar` | POST | `salon.staff_close` | `staff_close` — [views/salon.py:456](C:/Users/DELL/RecomenRestaurant/views/salon.py:456) | — |
| S | `/salon/<int:rid>/sesion/<int:session_id>/limpiar` | POST | `salon.staff_clean` | `staff_clean` — [views/salon.py:467](C:/Users/DELL/RecomenRestaurant/views/salon.py:467) | — |
| S | `/salon/<int:rid>/sesion/<int:session_id>/parte/<int:number>` | POST | `salon.staff_pay_share` | `staff_pay_share` — [views/salon.py:486](C:/Users/DELL/RecomenRestaurant/views/salon.py:486) | — |
| S | `/salon/<int:rid>/solicitud/<int:request_id>` | POST | `salon.staff_resolve` | `staff_resolve` — [views/salon.py:478](C:/Users/DELL/RecomenRestaurant/views/salon.py:478) | — |

#### sites

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| P | `/negocio/<slug>` | GET | `sites.public_page` | `public_page` — [views/business_sites.py:197](C:/Users/DELL/RecomenRestaurant/views/business_sites.py:197) | `sites/public.html` |
| P | `/negocio/<slug>/sucursal/<int:branch_id>` | GET | `sites.branch_page` | `branch_page` — [views/business_sites.py:209](C:/Users/DELL/RecomenRestaurant/views/business_sites.py:209) | `sites/public.html` |
| M | `/owner/api/sites/<int:rid>` | GET, PUT | `sites.site_api` | `site_api` — [views/business_sites.py:65](C:/Users/DELL/RecomenRestaurant/views/business_sites.py:65) | — |
| M | `/owner/api/sites/<int:rid>/ai` | POST | `sites.ai` | `ai` — [views/business_sites.py:154](C:/Users/DELL/RecomenRestaurant/views/business_sites.py:154) | — |
| M | `/owner/api/sites/<int:rid>/logo` | POST | `sites.logo` | `logo` — [views/business_sites.py:102](C:/Users/DELL/RecomenRestaurant/views/business_sites.py:102) | — |
| M | `/owner/api/sites/<int:rid>/publish` | POST | `sites.publish` | `publish` — [views/business_sites.py:86](C:/Users/DELL/RecomenRestaurant/views/business_sites.py:86) | — |
| M | `/owner/api/sites/<int:rid>/unpublish` | POST | `sites.unpublish` | `unpublish` — [views/business_sites.py:94](C:/Users/DELL/RecomenRestaurant/views/business_sites.py:94) | — |
| M | `/owner/sites` | GET | `sites.editor` | `editor` — [views/business_sites.py:52](C:/Users/DELL/RecomenRestaurant/views/business_sites.py:52) | `sites/editor.html` |
| M | `/owner/sites/<int:rid>/preview` | GET | `sites.preview` | `preview` — [views/business_sites.py:226](C:/Users/DELL/RecomenRestaurant/views/business_sites.py:226) | `sites/public.html` |
| P | `/portal-media/<int:media_id>` | GET | `sites.media` | `media` — [views/business_sites.py:112](C:/Users/DELL/RecomenRestaurant/views/business_sites.py:112) | — |

#### trust_center

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/admin/api/confianza` | GET | `trust_center.api` | `api` — [views/trust_center.py:42](C:/Users/DELL/RecomenRestaurant/views/trust_center.py:42) | — |
| S | `/admin/confianza` | GET | `trust_center.dashboard` | `dashboard` — [views/trust_center.py:40](C:/Users/DELL/RecomenRestaurant/views/trust_center.py:40) | `admin/trust_center.html` |
| S | `/admin/confianza/revisar/<kind>/<int:identifier>` | POST | `trust_center.review_content` | `review_content` — [views/trust_center.py:47](C:/Users/DELL/RecomenRestaurant/views/trust_center.py:47) | — |
| S | `/admin/confianza/sitio/<int:rid>` | GET | `trust_center.site_preview` | `site_preview` — [views/trust_center.py:71](C:/Users/DELL/RecomenRestaurant/views/trust_center.py:71) | — |

### 9.2 SistemaRestaurante2.0

#### (app)

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| T | `/health` | GET | `health_check` | `health_check` — [app/__init__.py:65](C:/Users/DELL/SistemaRestaurante2.0/app/__init__.py:65) | — |
| T | `/ready` | GET | `readiness_check` | `readiness_check` — [app/__init__.py:69](C:/Users/DELL/SistemaRestaurante2.0/app/__init__.py:69) | — |

#### admin

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/admin/` | GET | `admin.dashboard` | `dashboard` — [app/blueprints/admin/__init__.py:17](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/admin/__init__.py:17) | `admin/dashboard.html` |
| S | `/admin/api/stats` | GET | `admin.api_stats` | `api_stats` — [app/blueprints/admin/__init__.py:31](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/admin/__init__.py:31) | — |

#### ar

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| P | `/ar/` | GET | `ar.index` | `index` — [app/blueprints/ar/__init__.py:80](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:80) | `ar/index.html` |
| S | `/ar/api/gestion/platos/<int:pid>` | PUT | `ar.edit_dish` | `edit_dish` — [app/blueprints/ar/__init__.py:169](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:169) | — |
| S | `/ar/api/gestion/platos/<int:pid>/fotografias` | POST | `ar.upload` | `upload` — [app/blueprints/ar/__init__.py:177](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:177) | — |
| S | `/ar/api/gestion/platos/<int:pid>/publicacion` | POST | `ar.publish` | `publish` — [app/blueprints/ar/__init__.py:218](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:218) | — |
| S | `/ar/api/gestion/platos/<int:pid>/recursos` | GET | `ar.history` | `history` — [app/blueprints/ar/__init__.py:183](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:183) | — |
| S | `/ar/api/gestion/recursos/<int:resource_id>` | GET | `ar.status` | `status` — [app/blueprints/ar/__init__.py:197](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:197) | — |
| S | `/ar/api/gestion/recursos/<int:resource_id>/generar` | POST | `ar.generate` | `generate` — [app/blueprints/ar/__init__.py:191](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:191) | — |
| S | `/ar/api/gestion/recursos/<int:resource_id>/regenerar` | POST | `ar.regenerate` | `regenerate` — [app/blueprints/ar/__init__.py:204](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:204) | — |
| S | `/ar/api/gestion/recursos/<int:resource_id>/reintentar` | POST | `ar.generate` | `generate` — [app/blueprints/ar/__init__.py:191](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:191) | — |
| S | `/ar/api/gestion/recursos/<int:resource_id>/revision` | POST | `ar.review` | `review` — [app/blueprints/ar/__init__.py:210](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:210) | — |
| S | `/ar/api/gestion/restaurantes/<int:rid>` | GET | `ar.managed_menu` | `managed_menu` — [app/blueprints/ar/__init__.py:153](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:153) | — |
| S | `/ar/api/gestion/restaurantes/<int:rid>/platos` | POST | `ar.create_dish` | `create_dish` — [app/blueprints/ar/__init__.py:162](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:162) | — |
| P | `/ar/api/modelos/<int:id_plato>` | GET | `ar.api_modelo` | `api_modelo` — [app/blueprints/ar/__init__.py:114](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:114) | — |
| P | `/ar/api/platos/<int:pid>` | GET | `ar.detail` | `detail` — [app/blueprints/ar/__init__.py:104](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:104) | — |
| P | `/ar/api/restaurantes/<int:rid>/categorias` | GET | `ar.categories` | `categories` — [app/blueprints/ar/__init__.py:98](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:98) | — |
| P | `/ar/api/restaurantes/<int:rid>/menu` | GET | `ar.public_menu` | `public_menu` — [app/blueprints/ar/__init__.py:91](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:91) | — |
| S | `/ar/gestion` | GET | `ar.manage` | `manage` — [app/blueprints/ar/__init__.py:142](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:142) | `ar/manage.html` |
| S | `/ar/gestion/recursos/<int:resource_id>/<kind>` | GET | `ar.private_asset` | `private_asset` — [app/blueprints/ar/__init__.py:227](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:227) | — |
| P | `/ar/recursos/<int:resource_id>/<kind>` | GET | `ar.public_asset` | `public_asset` — [app/blueprints/ar/__init__.py:122](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:122) | — |
| P | `/ar/restaurantes/<int:rid>` | GET | `ar.menu` | `menu` — [app/blueprints/ar/__init__.py:86](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/ar/__init__.py:86) | `ar/menu.html` |

#### auth

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/auth/api/whoami` | GET | `auth.api_whoami` | `api_whoami` — [app/blueprints/auth/__init__.py:123](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/auth/__init__.py:123) | — |
| S | `/auth/login` | GET | `auth.login_form` | `login_form` — [app/blueprints/auth/__init__.py:18](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/auth/__init__.py:18) | `auth/login.html` |
| S | `/auth/login` | POST | `auth.login_submit` | `login_submit` — [app/blueprints/auth/__init__.py:28](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/auth/__init__.py:28) | `auth/login.html` |
| S | `/auth/logout` | GET, POST | `auth.logout` | `logout` — [app/blueprints/auth/__init__.py:111](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/auth/__init__.py:111) | — |
| S | `/auth/recover` | GET | `auth.recover_form` | `recover_form` — [app/blueprints/auth/__init__.py:118](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/auth/__init__.py:118) | `auth/login.html` |
| S | `/auth/register` | GET | `auth.register_form` | `register_form` — [app/blueprints/auth/__init__.py:60](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/auth/__init__.py:60) | `auth/register.html` |
| S | `/auth/register` | POST | `auth.register_submit` | `register_submit` — [app/blueprints/auth/__init__.py:67](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/auth/__init__.py:67) | `auth/register.html` |

#### business

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| P | `/negocio/<int:restaurante_id>` | GET | `business.show` | `show` — [app/blueprints/business/__init__.py:16](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/business/__init__.py:16) | `business/show.html` |
| P | `/negocio/<int:restaurante_id>/api/menu` | GET | `business.api_menu` | `api_menu` — [app/blueprints/business/__init__.py:35](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/business/__init__.py:35) | — |

#### discovery

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| P | `/descubrir/` | GET | `discovery.index` | `index` — [app/blueprints/discovery/__init__.py:13](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/discovery/__init__.py:13) | `discovery/index.html` |
| P | `/descubrir/api/map` | GET | `discovery.api_map` | `api_map` — [app/blueprints/discovery/__init__.py:59](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/discovery/__init__.py:59) | — |
| M | `/descubrir/api/recommend` | POST | `discovery.api_recommend` | `api_recommend` — [app/blueprints/discovery/__init__.py:80](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/discovery/__init__.py:80) | — |
| P | `/descubrir/api/restaurants` | GET | `discovery.api_restaurants` | `api_restaurants` — [app/blueprints/discovery/__init__.py:18](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/discovery/__init__.py:18) | — |

#### kitchen

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/kitchen/` | GET | `kitchen.index` | `index` — [app/blueprints/kitchen/__init__.py:17](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/kitchen/__init__.py:17) | `kitchen/index.html` |
| S | `/kitchen/api/pedidos` | GET | `kitchen.api_pedidos` | `api_pedidos` — [app/blueprints/kitchen/__init__.py:25](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/kitchen/__init__.py:25) | — |

#### loyalty

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/recompensas/` | GET | `loyalty.index` | `index` — [app/blueprints/loyalty/__init__.py:14](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/loyalty/__init__.py:14) | `loyalty/index.html` |
| S | `/recompensas/api/saldo` | GET | `loyalty.api_saldo` | `api_saldo` — [app/blueprints/loyalty/__init__.py:20](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/loyalty/__init__.py:20) | — |

#### market

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| P | `/mercado/` | GET | `market.index` | `index` — [app/blueprints/market/__init__.py:15](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/market/__init__.py:15) | `market/index.html` |
| S | `/mercado/api/mis-pedidos` | GET | `market.api_mis_pedidos` | `api_mis_pedidos` — [app/blueprints/market/__init__.py:27](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/market/__init__.py:27) | — |
| P | `/mercado/api/restaurantes` | GET | `market.api_restaurantes` | `api_restaurantes` — [app/blueprints/market/__init__.py:21](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/market/__init__.py:21) | — |

#### owner

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/owner/` | GET | `owner.dashboard` | `dashboard` — [app/blueprints/owner/__init__.py:19](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/owner/__init__.py:19) | `owner/dashboard.html` |
| S | `/owner/api/ai/audit-menu/<int:restaurante_id>` | POST | `owner.api_ai_audit_menu` | `api_ai_audit_menu` — [app/blueprints/owner/__init__.py:111](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/owner/__init__.py:111) | — |
| S | `/owner/api/ai/dish-from-photo` | POST | `owner.api_ai_dish_from_photo` | `api_ai_dish_from_photo` — [app/blueprints/owner/__init__.py:69](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/owner/__init__.py:69) | — |
| S | `/owner/api/resumen` | GET | `owner.api_resumen` | `api_resumen` — [app/blueprints/owner/__init__.py:44](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/owner/__init__.py:44) | — |

#### pantry

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/mi-cocina/` | GET | `pantry.index` | `index` — [app/blueprints/pantry/__init__.py:14](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/pantry/__init__.py:14) | `pantry/index.html` |
| S | `/mi-cocina/api/despensa` | GET | `pantry.api_despensa` | `api_despensa` — [app/blueprints/pantry/__init__.py:20](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/pantry/__init__.py:20) | — |

#### public

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| P | `/` | GET | `public.home` | `home` — [app/blueprints/public/__init__.py:148](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:148) | `public/home.html` |
| S | `/api/ai-decisions/<int:id_decision>` | GET | `public.api_ai_decision` | `api_ai_decision` — [app/blueprints/public/__init__.py:452](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:452) | — |
| S | `/api/audit/<int:id_evento>` | GET | `public.api_audit` | `api_audit` — [app/blueprints/public/__init__.py:510](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:510) | — |
| P | `/api/categorias` | GET | `public.api_categorias` | `api_categorias` — [app/blueprints/public/__init__.py:324](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:324) | — |
| S | `/api/company/<int:empresa_id>` | GET | `public.api_company` | `api_company` — [app/blueprints/public/__init__.py:272](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:272) | — |
| S | `/api/discovery/due` | GET | `public.api_discovery_due` | `api_discovery_due` — [app/blueprints/public/__init__.py:501](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:501) | — |
| S | `/api/discovery/sources` | GET | `public.api_discovery_sources` | `api_discovery_sources` — [app/blueprints/public/__init__.py:492](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:492) | — |
| S | `/api/groups/<int:id_grupo>` | GET | `public.api_group` | `api_group` — [app/blueprints/public/__init__.py:522](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:522) | — |
| P | `/api/market-kitchen/<int:id_cocina>` | GET | `public.api_market_kitchen` | `api_market_kitchen` — [app/blueprints/public/__init__.py:550](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:550) | — |
| P | `/api/market-kitchens` | GET | `public.api_market_kitchens` | `api_market_kitchens` — [app/blueprints/public/__init__.py:541](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:541) | — |
| S | `/api/me` | GET | `public.api_me` | `api_me` — [app/blueprints/public/__init__.py:236](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:236) | — |
| S | `/api/moderations/<int:id_moderacion>` | GET | `public.api_moderation` | `api_moderation` — [app/blueprints/public/__init__.py:464](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:464) | — |
| S | `/api/order/<int:pedido_id>` | GET | `public.api_order` | `api_order` — [app/blueprints/public/__init__.py:433](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:433) | — |
| P | `/api/restaurant/<int:restaurante_id>` | GET | `public.api_restaurant` | `api_restaurant` — [app/blueprints/public/__init__.py:297](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:297) | — |
| P | `/api/restaurant/<int:restaurante_id>/menu` | GET | `public.api_restaurant_menu` | `api_restaurant_menu` — [app/blueprints/public/__init__.py:312](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:312) | — |
| P | `/api/restaurant/<int:restaurante_id>/menus` | GET | `public.api_menus` | `api_menus` — [app/blueprints/public/__init__.py:346](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:346) | — |
| S | `/api/restaurant/<int:restaurante_id>/orders` | GET | `public.api_restaurant_orders` | `api_restaurant_orders` — [app/blueprints/public/__init__.py:421](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:421) | — |
| P | `/api/restaurant/<int:restaurante_id>/promotions` | GET | `public.api_promotions` | `api_promotions` — [app/blueprints/public/__init__.py:371](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:371) | — |
| P | `/api/restaurant/<int:restaurante_id>/reviews` | GET | `public.api_reviews` | `api_reviews` — [app/blueprints/public/__init__.py:358](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:358) | — |
| P | `/api/restaurants/published` | GET | `public.api_restaurants_published` | `api_restaurants_published` — [app/blueprints/public/__init__.py:333](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:333) | — |
| S | `/api/user/<int:user_id>` | GET | `public.api_user` | `api_user` — [app/blueprints/public/__init__.py:252](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:252) | — |
| S | `/api/user/<int:user_id>/companies` | GET | `public.api_user_companies` | `api_user_companies` — [app/blueprints/public/__init__.py:284](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:284) | — |
| S | `/api/user/<int:user_id>/favorites` | GET | `public.api_favorites` | `api_favorites` — [app/blueprints/public/__init__.py:383](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:383) | — |
| S | `/api/user/<int:user_id>/notifications` | GET | `public.api_notifications` | `api_notifications` — [app/blueprints/public/__init__.py:392](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:392) | — |
| S | `/api/user/<int:user_id>/orders` | GET | `public.api_user_orders` | `api_user_orders` — [app/blueprints/public/__init__.py:409](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:409) | — |
| S | `/api/user/<int:user_id>/search-history` | GET | `public.api_search_history` | `api_search_history` — [app/blueprints/public/__init__.py:479](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:479) | — |
| P | `/offline` | GET | `public.offline` | `offline` — [app/blueprints/public/__init__.py:191](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:191) | `offline.html` |
| P | `/sw.js` | GET | `public.service_worker` | `service_worker` — [app/blueprints/public/__init__.py:207](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/public/__init__.py:207) | — |

#### salon

| Alcance | URL | Método | Endpoint | Función y archivo | Plantilla(s) |
| --- | --- | --- | --- | --- | --- |
| S | `/salon/` | GET | `salon.index` | `index` — [app/blueprints/salon/__init__.py:16](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/salon/__init__.py:16) | `salon/index.html` |
| S | `/salon/api/mesas` | GET | `salon.api_mesas` | `api_mesas` — [app/blueprints/salon/__init__.py:24](C:/Users/DELL/SistemaRestaurante2.0/app/blueprints/salon/__init__.py:24) | — |

## 10. Cierre de Fase 1

Entregado: inventario de rutas y blueprints, matriz funcional, diferencias de HTML/CSS/JS, mapa de variables sin valores, riesgos y dependencias fuera del alcance.

No se modificó código de aplicación, sitio público, prototipo, `.env`, base de datos ni servicios. No se ejecutaron llamadas a proveedores ni migraciones. Las comprobaciones fueron estáticas y de documentación. **La fase termina aquí; no se inició implementación.**
