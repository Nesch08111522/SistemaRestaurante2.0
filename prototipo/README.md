# SmartResto — Sitio público multipágina (prototipo)

## Qué contiene

- Sitio público multipágina: Inicio, Descubrir, Mercado, Menú 3D, Experiencias, Para negocios, Ingresar y Registrarse.
- Páginas de soporte y confianza: Sobre SmartResto, Cómo funciona, Centro de ayuda, Contacto, Comunidad, Accesibilidad, Términos, Privacidad y Cookies.
- Footer compartido con navegación, enlaces legales, redes sociales de demostración y formulario de novedades.
- Componentes responsive para escritorio, tablet y móvil.
- Interacciones de demostración: filtros de catálogo, favoritos, carrito, visor de plato con rotación CSS 3D, controles de porción, turno de espera simulado, formularios, FAQ, preferencias de cookies y mensajes de estado.
- PWA inicial: manifest, iconos y Service Worker con App Shell público y fallback offline.
- `ecosistema-demo.html`: conserva el prototipo anterior con vistas por rol (comensal, empresario y administrador).

## Ejecutar en Windows / PowerShell

1. Descomprime la carpeta `smartresto_web_publico`.
2. Abre PowerShell dentro de esa carpeta.
3. Ejecuta:

```powershell
python -m http.server 8000
```

4. Abre `http://localhost:8000/` en Chrome o Edge.
5. Para probar la PWA, usa localhost o despliega bajo HTTPS; abrir directamente `index.html` con `file://` no permite registrar el Service Worker.

## Importante: alcance del prototipo

Este proyecto es un prototipo de frontend estático. Los formularios, filtros, carrito, turnos y controles 3D utilizan datos locales/de demostración. No autentica usuarios reales ni crea pedidos reales. Todavía no está conectado con Flask, Supabase/PostgreSQL, OpenRouter, mapas API, pasarela de pagos, Web Push ni blockchain.

Las fotos se cargan desde Unsplash y Google Fonts; por tanto, se necesita internet para visualizar esos recursos externos. El App Shell almacena páginas y recursos públicos propios, no datos privados ni respuestas de API.

La vista 3D es una representación CSS de concepto, no un modelo alimentario GLB calibrado. La realidad aumentada real necesita activos 3D medidos, HTTPS y soporte de cámara/WebXR.

Las páginas de Términos, Privacidad y Cookies son esqueletos preliminares, no documentos legales finales. Los enlaces sociales son marcadores para configurar las cuentas oficiales. Los precios comerciales se muestran como “Consultar” porque los importes y límites definitivos no están cerrados.

## Estructura

```text
smartresto_web_publico/
├── index.html
├── descubrir.html
├── mercado.html
├── menu-3d.html
├── experiencias.html
├── negocios.html
├── ingresar.html
├── registrarse.html
├── nosotros.html
├── como-funciona.html
├── ayuda.html
├── contacto.html
├── comunidad.html
├── accesibilidad.html
├── terminos.html
├── privacidad.html
├── cookies.html
├── offline.html
├── ecosistema-demo.html
├── manifest.webmanifest
├── sw.js
└── assets/
    ├── css/site.css
    ├── js/site.js
    └── img/
```
