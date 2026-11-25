"""
Instala los 22 CSS de SmartResto en app/static/css/.
Ejecutar: python scripts\instalar_css.py
"""
from pathlib import Path

CSS_DIR = Path(__file__).parent.parent / "app" / "static" / "css"
CSS_DIR.mkdir(parents=True, exist_ok=True)

FILES = {}

# ============================================================
# 1. theme-tokens.css
# ============================================================
FILES["theme-tokens.css"] = r"""/* Canonical design tokens: dark without any OS media query. */
:root {
  --theme-shadow-rgb: 9 17 22;
  --theme-bg: #14191d;
  --theme-surface: #1d252b;
  --theme-elevated: #29333b;
  --theme-text: #f2f6f8;
  --theme-muted: #c3ced5;
  --theme-border: #81939f;
  --theme-accent: #a6dfc6;
  --theme-accent-bg: #233b34;
  --theme-success: #a6dfc6;
  --theme-success-bg: #233b34;
  --theme-warning: #f2d08b;
  --theme-warning-bg: #3c3424;
  --theme-danger: #ffb9bb;
  --theme-danger-bg: #402c32;
  --theme-info: #b7d8ff;
  --theme-info-bg: #283748;
  --theme-focus: #f2d08b;
  --theme-shadow: #09111666;
  --theme-edge: #c3ced51a;
  --theme-overlay: #10171de6;
  --theme-chart-1: #a6dfc6;
  --theme-chart-2: #b7d8ff;
  --theme-chart-3: #f2d08b;
  --theme-chart-4: #ffb9bb;
  --theme-chart-5: #d6c6ff;
  --theme-chart-6: #a7dce2;
  --theme-map-background: #e7eef1;
  --theme-map-control-text: #263238;
  --theme-map-control-bg: rgba(255, 255, 255, .9);
  --theme-brand-primary: #245447;
  --theme-brand-secondary: #d8a65d;
  color-scheme: dark;
}
[data-theme="light"] {
  --theme-shadow-rgb: 24 36 44;
  --theme-bg: #f3f5f6;
  --theme-surface: #ffffff;
  --theme-elevated: #e6ecef;
  --theme-text: #18242c;
  --theme-muted: #41515d;
  --theme-border: #667b88;
  --theme-accent: #17533f;
  --theme-accent-bg: #dcece5;
  --theme-success: #17533f;
  --theme-success-bg: #dcece5;
  --theme-warning: #674500;
  --theme-warning-bg: #f4ead4;
  --theme-danger: #852737;
  --theme-danger-bg: #fae4e8;
  --theme-info: #214d78;
  --theme-info-bg: #e1ecf9;
  --theme-focus: #674500;
  --theme-shadow: #18242c26;
  --theme-edge: #ffffffb3;
  --theme-overlay: #e6eceff2;
  --theme-chart-1: #17533f;
  --theme-chart-2: #214d78;
  --theme-chart-3: #674500;
  --theme-chart-4: #852737;
  --theme-chart-5: #584182;
  --theme-chart-6: #23535b;
  --theme-brand-primary: #245447;
  --theme-brand-secondary: #d8a65d;
  color-scheme: light;
}
:root { --theme-photo-bg:#111; --theme-photo-text:#fff; --theme-photo-rgb:0 0 0; --theme-promo-bg:#a34813; }
"""

# ============================================================
# 2. responsive-tokens.css
# ============================================================
FILES["responsive-tokens.css"] = r""":root {
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;
  --space-2xl: 3rem;
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.375rem;
  --text-2xl: 1.75rem;
  --text-display: 2.5rem;
  --sr-radius-card: 20px;
  --sr-depth-0: 0 1px 2px rgb(0 0 0 / 4%);
  --sr-depth-1: 0 2px 6px rgb(0 0 0 / 6%), 0 4px 12px rgb(0 0 0 / 4%);
  --sr-depth-2: 0 8px 24px rgb(0 0 0 / 8%);
}
"""

# ============================================================
# 3. shell.css (lo que me pasaste, copiado íntegro)
# ============================================================
FILES["shell.css"] = r"""/* Shared colour, type and interaction tokens. */
.private-account { position: relative; flex: none; }
body.sr-private .sr-header { z-index: 1550; }
body .sr-header, body .sr-top, body .sr-actions { overflow: visible; }
body .private-account-menu { max-width: calc(100vw - 32px); box-sizing: border-box; }
.private-account-menu a { min-height: 44px; box-sizing: border-box; touch-action: manipulation; }
@media (max-width: 360px) { body .sr-top [data-theme-label] { display: none; } }
.private-account-menu { position: absolute; right: 0; top: calc(100% + 8px); width: min(224px, calc(100vw - 32px)); padding: 6px; border: 1px solid var(--theme-border); background: var(--theme-surface); border-radius: 8px; z-index: 110; }
.private-account-menu[hidden] { display: none; }
.private-account-menu a { display: block; padding: 10px; color: var(--theme-text); text-decoration: none; border-radius: 6px; }
.private-account-menu a:hover { background: var(--theme-elevated); }
:root {
  --sr-bg: var(--theme-bg); --sr-surface: var(--theme-surface); --sr-text: var(--theme-success); --sr-muted: var(--theme-muted); --sr-brand: var(--theme-accent);
  --sr-line: var(--theme-border); --sr-accent: var(--theme-accent); --sr-tint: var(--theme-elevated); --sr-ink: var(--theme-success); --sr-focus: var(--theme-focus);
  --font-main:"DM Sans",system-ui,sans-serif; --font-heading: var(--font-main); --sr-display:"DM Serif Text",Georgia,serif;
  --primary: var(--sr-brand); --secondary: var(--sr-brand); --primary-dark: var(--theme-accent); --secondary-dark: var(--theme-accent); --primary-light: var(--sr-tint);
  --dark: var(--sr-text); --gray: var(--sr-muted); --light-gray: var(--sr-line); --white: var(--sr-surface);
  --bg-primary: var(--sr-bg); --bg-secondary: var(--sr-surface); --text-primary: var(--sr-text); --text-secondary: var(--sr-muted);
  --sr-gutter: clamp(16px,4vw,76px); --sr-rail: 218px; --sr-header: 70px; --radius: 14px;
  color-scheme:light; scroll-padding-top:calc(var(--sr-header) + 12px);
}
:root[data-theme=dark] {
  color-scheme:dark; --sr-bg: var(--theme-bg); --sr-surface: var(--theme-surface); --sr-text: var(--theme-text); --sr-muted: var(--theme-muted); --sr-brand: var(--theme-accent);
  --sr-line: var(--theme-border); --sr-accent: var(--theme-accent); --sr-tint: var(--theme-elevated); --sr-ink: var(--theme-success); --sr-focus: var(--theme-focus);
  --primary-dark: var(--theme-accent); --secondary-dark: var(--theme-accent);
}
*,*::before,*::after{box-sizing:border-box}
body{background: var(--sr-bg);color: var(--theme-text);font-family:var(--font-main);margin:0}
button,input,select,textarea{font:inherit}
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible,textarea:focus-visible{outline: 3px solid var(--sr-focus);outline-offset:3px}
.sr-only,.sr-compact .sr-private .sr-sidebar .sr-group,.sr-compact .sr-private .sr-sidebar a span,.sr-compact .sr-private .sr-sidebar form span{position:absolute;clip-path:inset(50%);width:1px;height:1px;overflow:hidden;white-space:nowrap}
.sr-header{position:sticky;top:0;z-index:1550;background: var(--sr-bg);border-bottom: 1px solid var(--sr-line)}
.sr-top{height:var(--sr-header);max-width:1700px;margin:auto;padding:0 var(--sr-gutter);display:flex;align-items:center;gap:clamp(var(--space-sm),2vw,var(--space-lg))}
.sr-logo,.sr-logo:hover{display:inline-flex;align-items:center;gap:var(--space-sm);min-height:44px;color: var(--theme-text);font-size:clamp(20px,2vw,27px);font-weight:750;letter-spacing:-1.4px;text-decoration:none;white-space:nowrap}
.sr-mark{background: var(--theme-success-bg);color: var(--theme-success);display:grid;place-items:center;border-radius: 50%;width:32px;height:32px;font-size:var(--text-xl);line-height:1}
.sr-public-links,.sr-actions{display:flex;align-items:center;gap:clamp(var(--space-xs),2vw,var(--space-lg))}
.sr-public-links{margin:auto}.sr-public-links a,.sr-login,.sr-footer a{color: var(--theme-text);text-decoration:none}
.sr-public-links a,.sr-login{display:inline-flex;align-items:center;min-height:44px;font-weight:600;font-size:var(--text-sm)}
.sr-actions{margin-left:auto;gap:var(--space-xs)}.sr-login{padding:0 var(--space-sm)}
.sr-icon,.sr-account{position:relative;display:inline-grid;place-items:center;flex:none;min-height:44px;min-width:44px;background: transparent;color: var(--theme-text);border: 1px solid transparent;border-radius: 50%;font-size:var(--text-lg);cursor:pointer;text-decoration:none}
.sr-icon:hover,.sr-account{background: var(--sr-tint)}.sr-count{position:absolute;right:0;top:1px;background: var(--theme-accent-bg);color:var(--theme-text);border-radius: 1em;padding:0 var(--space-xs);font-size:var(--text-xs)}
.sr-button,.sr-finder button{display:inline-flex;justify-content:center;align-items:center;gap:var(--space-sm);background: var(--theme-accent-bg);border: 0;color:var(--theme-text);padding:var(--space-sm) var(--space-md);border-radius: 30px;min-height:44px;font-weight:700;text-decoration:none;cursor:pointer}
.sr-signup{font-size:var(--text-sm)}.sr-menu-button,.sr-sidebar{display:none}.sr-backdrop[hidden]{display:none}.sr-backdrop{position:fixed;inset:0;background: var(--theme-surface);z-index:1800;border: 0}
.sr-drawer-open{overflow:hidden}.sr-sidebar{padding:var(--space-sm);flex-direction:column;gap:0.1875rem;background: var(--sr-surface);border-right: 1px solid var(--sr-line);overflow:auto;transition:width .24s ease,transform .24s ease}
.sr-sidebar a,.sr-sidebar form button{display:flex;align-items:center;gap:var(--space-md);min-height:44px;border: 0;width:100%;font-size:var(--text-sm);text-decoration:none;text-align:left;padding:var(--space-sm) var(--space-sm);background: transparent;color: var(--theme-text);border-radius: 10px;cursor:pointer}
.sr-sidebar i{width:18px;text-align:center}.sr-sidebar a:hover,.sr-sidebar [aria-current=page],.sr-sidebar form button:hover{background: var(--sr-tint);font-weight:700}
.sr-group{color: var(--theme-muted);font-size:var(--text-xs);margin:12px 10px 1px}.sr-side-top{display:flex;align-items:center;justify-content:space-between}.sr-side-top .sr-group{margin:0 10px}.sr-collapse{font-size:var(--text-xl)}
.sr-drawer-open .sr-sidebar{display:flex;position:fixed;inset:0 auto 0 0;width:min(300px,86vw);z-index:1900}
.sr-private .sr-menu-button{display:grid}
@media(min-width:1100px){
 .sr-private .sr-menu-button,.sr-private .sr-public-links{display:none}.sr-private .sr-sidebar{display:flex;position:fixed;inset:var(--sr-header) auto 0 0;width:var(--sr-rail);z-index:1400}
 .sr-private #main-content,.sr-private .sr-footer{margin-left:var(--sr-rail);transition:margin-left .24s ease}
 .sr-compact{--sr-rail: 70px}
 :root:not(.sr-compact){--sr-rail:250px}
}
.sr-hero,.sr-paths,.sr-explore,.sr-below,.sr-info{width:min(calc(100% - 2 * var(--sr-gutter)),1480px);margin-inline:auto}
.sr-hero{margin-top:clamp(16px,2.8vw,42px);display:grid;grid-template-columns:1fr 1.04fr;min-height:clamp(390px,37vw,580px);overflow:hidden;border-radius: 26px;background: var(--theme-success-bg);color: var(--theme-text)}
.sr-hero-copy{padding:clamp(var(--space-lg),4.5vw,var(--space-2xl));align-self:center}
.sr-location{font-size:var(--text-xs);font-weight:700;letter-spacing:.08em;text-transform:uppercase;display:flex;align-items:center;gap:var(--space-sm)}.sr-location span{color: var(--theme-success);font-size:var(--text-xs)}
.sr-hero h1,.sr-explore h2,.sr-below h2,.sr-info h1{font-family:var(--sr-display);font-weight:400;line-height:1.02;letter-spacing:-.044em}
.sr-hero h1{font-size:clamp(48px,5.4vw,88px);color: inherit;margin:18px 0}.sr-hero h1 em{color: var(--theme-success);font-weight:400}
.sr-hero-copy>p{max-width:42ch;line-height:1.5;font-size:clamp(15px,1.25vw,19px);margin:12px 0 20px;color: var(--theme-success)}.sr-hero-copy>.sr-welcome{margin-bottom:0}
.sr-finder{display:flex;align-items:center;gap:var(--space-sm);background: var(--theme-surface);border-radius: 30px;padding:var(--space-xs) var(--space-xs) var(--space-xs) var(--space-md);max-width:510px}
.sr-finder>span{color: var(--theme-success);font-size:var(--text-xl)}.sr-finder input{border: 0;background: transparent;color: var(--theme-success);min-width:0;flex:1;font-size:var(--text-sm);min-height:44px}.sr-finder input::placeholder{color: var(--theme-text)}.sr-finder button{background: var(--theme-success-bg);color: var(--theme-success);padding-inline:var(--space-md)}
.sr-hero-link{display:inline-flex;align-items:center;gap:var(--space-sm);color: var(--theme-success);text-decoration:none;min-height:44px;font-size:var(--text-sm);font-weight:600}
.sr-art{position:relative;margin:0;isolation:isolate;background: var(--theme-success-bg);min-width:0}.sr-art picture,.sr-art img{width:100%;height:100%;display:block}.sr-art img{position:absolute;inset:0;object-fit:cover}
.sr-art figcaption{position:absolute;bottom:18px;right:20px;color: var(--theme-text);background: var(--theme-success-bg);border-radius: 20px;padding:var(--space-xs) var(--space-sm);font-size:var(--text-xs);letter-spacing:.025em}.sr-art figcaption span{color: var(--theme-success);padding:0 0.1875rem}
.sr-paths{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--space-md);margin-block:18px 36px}.sr-paths>a,.sr-paths>button{display:flex;align-items:center;gap:var(--space-md);color: var(--theme-text);background: var(--sr-tint);border: 1px solid var(--sr-line);border-radius: 13px;font-size:clamp(14px,1.3vw,18px);font-weight:600;text-decoration:none;padding:var(--space-sm) var(--space-md);cursor:pointer;text-align:left}.sr-paths b{margin-left:auto}.sr-path-icon{display:grid;place-items:center;background: var(--sr-surface);width:38px;height:38px;border-radius: 50%;font-size:var(--text-xl);color: var(--theme-accent)}
.sr-explore h2,.sr-below h2{font-size:clamp(30px,3vw,47px);margin:0 0 18px;color: var(--theme-text)}
.sr-search-grid{display:grid;grid-template-columns:1.6fr 1fr 1fr .85fr auto;gap:var(--space-sm);align-items:end}
.sr-search-grid label{display:grid;gap:var(--space-xs);font-size:var(--text-sm);color: var(--theme-muted);font-weight:600;min-width:0}
.sr-search-grid input,.sr-search-grid select{background: var(--sr-surface);min-width:0;width:100%;border: 1px solid var(--sr-line);border-radius: 9px;padding:var(--space-sm) var(--space-sm);color: var(--theme-text);min-height:44px}
.sr-below>section{margin:clamp(32px,5vw,72px) 0}.sr-section-title{display:flex;align-items:baseline;justify-content:space-between;gap:var(--space-sm)}.sr-below a:not(.sr-button),.sr-info>a:not(.sr-button){color: var(--theme-accent)}
.sr-food-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:var(--space-md)}.sr-food-grid article,.sr-food-grid blockquote{margin:0;padding:var(--space-md);border: 1px solid var(--sr-line);border-radius: 14px;background: var(--sr-surface);overflow-wrap:anywhere}.sr-food-grid img{width:100%;height:170px;object-fit:cover;border-radius: 10px;margin-bottom:10px}.sr-food-grid small{color: var(--theme-muted)}.sr-food-grid h3{margin:8px 0}
.sr-business{display:flex;align-items:center;justify-content:space-between;gap:var(--space-md);background: var(--sr-tint);padding:clamp(var(--space-lg),4vw,var(--space-2xl));border-radius: 20px}.sr-business p{max-width:50ch}
.sr-below details{border-top: 1px solid var(--sr-line);padding:var(--space-sm) 0}.sr-below summary{cursor:pointer;min-height:44px;align-content:center;padding:var(--space-sm) 0;font-weight:600}.sr-below details p{max-width:75ch;padding:var(--space-xs) 0 var(--space-md);color: var(--theme-muted)}
.sr-info{max-width:740px;padding-block:var(--space-xl)}.sr-info h1{font-size:clamp(42px,5vw,72px);margin-block:24px}.sr-info h2{margin-block:24px 6px}.sr-info p{margin-block:10px 24px;line-height:1.65}
.sr-footer{display:grid;grid-template-columns:1.35fr repeat(3,1fr);gap:var(--space-md);padding:var(--space-xl) var(--sr-gutter);border-top: 1px solid var(--sr-line);background: var(--sr-tint);color: var(--theme-text);font-size:var(--text-sm)}.sr-footer nav{display:flex;flex-direction:column;align-items:flex-start}.sr-footer nav a{display:flex;align-items:center;min-height:44px}.sr-footer strong{margin:10px 0}.sr-footer a:hover,.sr-public-links a:hover{text-decoration:underline}.sr-private .sr-footer{display:flex;align-items:center;justify-content:space-between;padding-block:var(--space-md);flex-wrap:wrap}.sr-private .sr-footer nav:not(:last-child),.sr-private .sr-footer nav strong,.sr-private .sr-footer>div p{display:none}.sr-private .sr-footer nav:last-child{flex-direction:row;flex-wrap:wrap;align-items:center;gap:var(--space-sm)}
#main-content .filter-section{position:relative;top:auto;margin:14px auto;padding:var(--space-xs) 0;background: transparent;width:min(calc(100% - 2 * var(--sr-gutter)),1480px);z-index:1}
#main-content .main-layout{width:min(calc(100% - 2 * var(--sr-gutter)),1480px);margin:auto;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);border: 1px solid var(--sr-line);border-radius: 18px;height:clamp(400px,65vh,760px);background: var(--sr-surface)}
#main-content .results-column{background: var(--sr-surface);min-width:0}#main-content .view-btn,.filter-chip,.close-modal{min-height:44px}.view-btn{min-width:44px}
[data-theme=dark] :is(.restaurant-card,.auth-card,.modal-content,.market-card,.market-shell,.form-input,.detail-container,.owner-dashboard,.dropdown-menu,.results-column){background: var(--sr-surface);color: var(--theme-text)}
[data-theme=dark] :is(.restaurant-card h3,.restaurant-card p,.results-header h2,.auth-card h1,.auth-card h2,.modal-content h2){color: var(--theme-text)}
@media(max-width:767px){
 .sr-compact .sr-private .sr-sidebar a span,.sr-compact .sr-private .sr-sidebar form span,.sr-compact .sr-private .sr-sidebar .sr-group{position:static;clip-path:none;width:auto;height:auto;overflow:visible}
}
@media(max-width:800px){
 .sr-menu-button{display:grid}.sr-public-links{display:none}.sr-top{gap:var(--space-xs)}.sr-search-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.sr-search-grid button{justify-self:start}
 .sr-footer{grid-template-columns:repeat(2,1fr)}#main-content .main-layout{display:flex;flex-direction:column;height:auto}.main-layout .map-column{order:0;height:320px;flex:none}.main-layout .results-column{order:1;max-height:65vh;overflow:auto}
}
@media(max-width:640px){
 :root{--sr-header: 60px}.sr-top{padding-inline:var(--space-sm)}.sr-actions{gap:0}.sr-login{padding:0 var(--space-xs)}.sr-signup{display:none}.sr-message-link{display:none}
 .sr-hero{grid-template-columns:1fr;border-radius: 18px}.sr-hero-copy{padding:var(--space-lg) var(--space-md) var(--space-md)}.sr-hero h1{font-size:clamp(48px,12vw,68px);margin-block:12px}
 .sr-art{height:clamp(165px,41vw,245px)}.sr-art img{object-position:50% 55%}.sr-art figcaption{bottom:10px;right:12px}
 .sr-paths{gap:var(--space-xs);margin:12px auto 28px}.sr-paths>a,.sr-paths>button{padding:var(--space-sm) var(--space-xs);gap:var(--space-xs);flex-direction:column;align-items:center;text-align:center;font-size:var(--text-xs);line-height:1.3}.sr-paths b{display:none}.sr-path-icon{width:30px;height:30px;font-size:var(--text-xl)}
 .sr-business{display:block}.sr-business .sr-button{margin-top:15px}.sr-section-title{flex-wrap:wrap}
}
@media(max-width:375px){.sr-footer{grid-template-columns:1fr}.sr-finder{padding-left:var(--space-sm);gap:0.125rem}.sr-finder button{padding-inline:var(--space-sm)}.sr-logo{gap:var(--space-xs)}.sr-mark{width:26px;height:26px;font-size:var(--text-xl)}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;animation-duration:.01ms!important;transition-duration:.01ms!important}}
@media(max-width:340px){.sr-top{gap:var(--space-xs);padding-inline:var(--space-xs)}.sr-private .sr-logo{font-size:var(--text-lg)}.sr-private .sr-footer{padding-inline:var(--space-sm)}}
body.sr-private .sr-sidebar {
  box-sizing: border-box; flex-direction: column; gap: 2px;
  padding: 12px; background: var(--theme-surface);
  border-right: 1px solid var(--theme-border); overflow-y: auto; overflow-x: hidden;
  overscroll-behavior: contain; box-shadow: none;
}
body.sr-private .sr-sidebar :is(a, summary, form button) {
  box-sizing: border-box; display: flex; align-items: center; gap: 10px;
  width: 100%; min-width: 0; min-height: 38px; margin: 0;
  padding: 8px 10px; border: 0; border-radius: 6px;
  font: 500 13px/1.4 var(--font-main, system-ui, sans-serif);
  letter-spacing: normal; text-transform: none; text-decoration: none;
  color: var(--theme-text); background: transparent; cursor: pointer;
}
body.sr-private .sr-sidebar :is(a, summary, form button) > span {
  min-width: 0; overflow: hidden !important; text-overflow: ellipsis;
  white-space: nowrap !important;
}
body.sr-private .sr-sidebar svg { width: 18px; height: 18px; flex: 0 0 18px; }
body.sr-private .sr-nav-section { border: 0; min-width: 0; flex-shrink: 0; }
body.sr-private .sr-nav-section summary { list-style: none; }
body.sr-private .sr-nav-section summary::-webkit-details-marker { display: none; }
body.sr-private .sr-nav-section summary::marker { content: ''; }
body.sr-private .sr-section-chevron { margin-left: auto; transition: transform 140ms ease; }
body.sr-private .sr-nav-section[open] > summary .sr-section-chevron { transform: rotate(180deg); }
body.sr-private .sr-section-links { padding: 2px 0 4px 12px; }
body.sr-private .sr-sidebar :is(a,summary,form button):hover { background: var(--theme-elevated); }
body.sr-private .sr-sidebar :is([aria-current=page],.sr-section-active) {
  background: var(--theme-accent-bg); color: var(--theme-accent); font-weight: 600; box-shadow: none;
}
body.sr-private .sr-sidebar :is(a,summary,button):focus-visible {
  outline: 2px solid var(--theme-focus); outline-offset: -2px;
}
body.sr-private .sr-sidebar .sr-group { font: 600 11px/1.4 var(--font-main, system-ui, sans-serif); letter-spacing: .06em; text-transform: uppercase; margin: 18px 10px 6px; }
body.sr-private .sr-side-top { flex-shrink: 0; min-height: 38px; margin-bottom: 8px; }
body.sr-private .sr-side-top .sr-group { margin: 0 10px; }
body.sr-private .sr-sidebar .sr-collapse { display: inline-flex !important; align-items: center; justify-content: center; padding: 6px; flex: 0 0 32px; }
body.sr-private .sr-collapse-arrow { display: none; }
body.sr-private .sr-collapse-close { display: block; }
body.sr-private .saas-sidebar-footer { margin-top: auto; padding-top: 12px; border-top: 1px solid var(--theme-border); }
@media (min-width:1100px) {
  body.sr-private .sr-sidebar { display: flex; position: fixed; inset: var(--sr-header) auto 0 0 !important; width: 248px !important; transform: none !important; z-index: 102; }
  body.sr-private #main-content { margin-left: 248px !important; width: auto !important; }
  body.sr-private .sr-footer { margin-left: 248px; }
  body.sr-private .sr-menu-button { display: inline-flex !important; }
  body.sr-private .sr-collapse-arrow { display: block; transform: rotate(180deg); }
  body.sr-private .sr-collapse-close { display: none; }
  .sr-compact body.sr-private .sr-sidebar { width: 64px !important; padding: 8px; }
  .sr-compact body.sr-private #main-content { margin-left: 64px !important; }
  .sr-compact body.sr-private .sr-footer { margin-left: 64px; }
  .sr-compact body.sr-private .sr-sidebar :is(a span,form span,.sr-group,.sr-section-label) {
    position: absolute !important; width: 1px !important; height: 1px !important;
    clip-path: inset(50%) !important; overflow: hidden !important; white-space: nowrap !important;
  }
  .sr-compact body.sr-private .sr-sidebar :is(a,summary,form button) { justify-content: center; padding: 9px; }
  .sr-compact body.sr-private .sr-section-chevron { display: none; }
  .sr-compact body.sr-private .sr-side-top { justify-content: center; }
  .sr-compact body.sr-private .sr-section-links { padding: 0; }
  .sr-compact body.sr-private .sr-collapse-arrow { transform: none; }
}
@media (max-width:1099px) {
  body.sr-private #main-content { margin-left: 0 !important; width: 100% !important; }
  body.sr-private .sr-sidebar { display: none; }
  body.sr-private .sr-menu-button { display: inline-flex !important; }
  .sr-drawer-open body.sr-private .sr-sidebar { display: flex; position: fixed; inset: 0 auto 0 0 !important; width: min(288px,88vw) !important; transform: none !important; z-index: 1900; }
  .sr-drawer-open body.sr-private .sr-backdrop { display: block; position: fixed; inset: 0; z-index: 1800; background: var(--theme-bg); opacity: .8; }
  .sr-compact body.sr-private .sr-sidebar :is(a span,form span,.sr-group,.sr-section-label) { position: static !important; clip-path: none !important; width: auto !important; height: auto !important; }
}
@media (min-width: 768px) {
  .sr-private #main-content {
    width: calc(100% - var(--sr-rail));
    max-width: none;
  }
}
"""

# ============================================================
# 4. forest-home.css
# ============================================================
FILES["forest-home.css"] = r"""/* SmartResto editorial discovery. Scoped to the homepage, leaving operational panels intact. */
body.sr-discover { --forest-display:'Lora',Georgia,serif; --forest-border: color-mix(in srgb,var(--sr-line) 65%,var(--sr-bg)); --sr-gutter: clamp(16px,2.6vw,44px); font-size:var(--text-sm); }
body.sr-discover .forest-shell { width:min(calc(100% - 2 * var(--sr-gutter)),1440px); margin:0 auto 40px; }
body.sr-discover :is(.forest-shell h1,.forest-shell h2,.forest-shell h3) { font-family:var(--forest-display); letter-spacing:-.035em; font-weight:600; }
body.sr-discover :is(.forest-shell h2) { font-size:clamp(23px,2vw,29px); line-height:1.2; margin:0; }
body.sr-discover :is(.forest-shell p) { margin:0; }
body.sr-discover button { cursor:pointer; }
body.sr-discover .sr-header { background: color-mix(in srgb,var(--sr-bg) 96%,transparent); }
body.sr-discover .sr-top { max-width:1240px; height:68px; padding-inline:var(--space-md); }
body.sr-discover .sr-logo { font-size:var(--text-xl); letter-spacing:-1px; color: var(--theme-accent); }
body.sr-discover .sr-mark { width:36px; height:36px; }
body.sr-discover .sr-public-links { gap:var(--space-lg); }
body.sr-discover .sr-public-links a { position:relative; font-size:var(--text-sm); font-weight:500; min-height:68px; }
body.sr-discover .sr-public-links a[aria-current=page]::after { content:''; position:absolute; bottom:7px; height:2px; left:0; right:0; background: var(--theme-accent-bg); border-radius: 2px; }
body.sr-discover .sr-signup { border-radius: 100px; }
body.sr-discover .forest-search { position:relative; margin:12px auto 16px; max-width:1170px; }
body.sr-discover .forest-search-row { display:flex; align-items:center; gap:var(--space-sm); min-height:48px; }
body.sr-discover .forest-city { color: var(--theme-text); display:flex; align-items:center; gap:var(--space-sm); min-height:44px; padding:0 var(--space-md) 0 var(--space-sm); border-right: 1px solid var(--forest-border); text-decoration:none; white-space:nowrap; }
body.sr-discover .forest-city .fa-chevron-down { margin-left:20px; font-size:var(--text-xs); }
body.sr-discover .forest-query { display:flex; flex:1; min-width:0; align-items:center; gap:var(--space-sm); }
body.sr-discover .forest-query input { width:100%; min-width:0; min-height:44px; border: 0!important; background: transparent!important; font-size:var(--text-sm); padding:var(--space-sm); }
body.sr-discover .forest-search-submit { display:grid; place-items:center; min-width:62px; min-height:44px; border-radius: 100px; border: 0; background: var(--forest-control-face) var(--theme-accent-bg); color: var(--theme-text); font-size:var(--text-base); box-shadow: var(--forest-control); }
body.sr-discover .forest-ai-search { display:flex; align-items:center; justify-content:center; gap:var(--space-sm); min-height:44px; border: 1px solid var(--sr-brand); background: var(--forest-face); color: var(--theme-accent); border-radius: 100px; padding:var(--space-sm) var(--space-md); font-size:var(--text-sm); white-space:nowrap; box-shadow: var(--forest-relief); }
body.sr-discover .forest-filters { border: 0; padding:0; margin:0; }
body.sr-discover .forest-filters > summary { display:none; }
body.sr-discover .forest-filter-fields { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:var(--space-md); padding:var(--space-lg); margin-top:12px; border: 1px solid var(--forest-border); background: var(--sr-surface); border-radius: 18px; box-shadow: var(--sr-depth-1); }
body.sr-discover .forest-filter-fields label { display:grid; gap:var(--space-xs); font-size:var(--text-sm); font-weight:600; min-width:0; }
body.sr-discover .forest-filter-fields :is(input,select) { min-width:0; width:100%; min-height:44px; }
body.sr-discover .forest-filter-quick { display:flex; gap:var(--space-sm); flex-wrap:wrap; grid-column:1/-1; }
body.sr-discover .forest-reset { border: 0; background: transparent; padding:var(--space-sm) var(--space-sm); min-height:44px; color: var(--theme-muted); text-decoration:underline; }
body.sr-discover .forest-hero { display:grid; grid-template-columns:38% 62%; position:relative; isolation:isolate; min-height:278px; border-radius: 20px; overflow:hidden; background: var(--forest-hero-face); color: var(--theme-text); box-shadow: var(--forest-hero-depth); }
body.sr-discover .forest-hero-copy { padding:var(--space-lg) var(--space-md) var(--space-lg) clamp(var(--space-lg),6vw,var(--space-2xl)); align-self:center; position:relative; z-index:2; }
body.sr-discover .forest-hero-copy::before { content:''; position:absolute; pointer-events:none; z-index:-1; inset:0; opacity:.2; background: url('../images/citrus-study.svg') left center / 160px auto no-repeat; }
body.sr-discover .forest-campaign { display:flex; align-items:center; gap:var(--space-sm); font-size:var(--text-xs); font-weight:600; color: var(--theme-warning); }
body.sr-discover .forest-campaign span { display:block; width:7px; height:7px; border-radius: 50%; background: var(--theme-warning-bg); }
body.sr-discover .forest-hero h1 { color: inherit; font-size:clamp(32px,3.15vw,47px); line-height:1.07; margin:10px 0 12px; font-weight:500; }
body.sr-discover .forest-hero-copy > p:not(.forest-campaign) { font-size:var(--text-sm); line-height:1.6; margin-bottom:17px; color: var(--theme-text); }
body.sr-discover .forest-light-button { display:inline-flex; align-items:center; justify-content:center; gap:var(--space-md); border: 0; border-radius: 100px; min-height:44px; background: var(--forest-cream-face); color: var(--theme-success); padding:var(--space-sm) var(--space-lg); font-size:var(--text-sm); font-weight:600; text-decoration:none; box-shadow: var(--forest-cream-edge); }
body.sr-discover .forest-hero-actions { display:flex; flex-wrap:wrap; gap:var(--space-sm) var(--space-md); align-items:center; }
body.sr-discover .forest-hero-personal { display:inline-flex; gap:var(--space-sm); min-height:44px; padding-inline:var(--space-sm); align-items:center; border: 1px solid var(--theme-border); border-radius: 100px; background: var(--forest-control-face); color: var(--theme-warning); font-size:var(--text-sm); font-weight:700; text-decoration:none; }
body.sr-discover .forest-hero-personal:hover { text-decoration:underline; }
body.sr-discover .forest-hero-photo { position:relative; margin-left:-30px; border-radius: 150px 0 0 150px / 55% 0 0 55%; overflow:hidden; }
body.sr-discover .forest-hero-photo img { position:absolute; width:100%; height:100%; object-fit:cover; object-position:50% 54%; }
body.sr-discover .forest-hero-photo::after {
  content:''; position:absolute; inset:0; border-radius: inherit; pointer-events:none;
  box-shadow: inset 2px 0 var(--theme-shadow), inset 0 -14px 26px -18px var(--theme-shadow);
}
body.sr-discover .forest-categories { display:flex; align-items:stretch; margin:14px auto 26px; width:94%; border: 1px solid var(--forest-border); border-radius: 100px; min-height:52px; padding:var(--space-xs) var(--space-sm); background: var(--forest-face); box-shadow: var(--forest-relief); overflow-x:auto; scrollbar-width:thin; }
body.sr-discover .forest-categories :is(button,a) { display:flex; align-items:center; justify-content:center; gap:var(--space-sm); flex:1 0 auto; min-height:44px; padding:var(--space-xs) var(--space-md); margin:0; border: 0; border-radius: 100px; background: transparent; color: var(--theme-text); font-size:var(--text-sm); font-weight:500; text-decoration:none; white-space:nowrap; }
body.sr-discover .forest-categories :is(button,a) + :is(button,a) { position:relative; }
body.sr-discover .forest-categories :is(button,a) + :is(button,a)::before { content:''; width:1px; height:19px; background: var(--forest-border); position:absolute; left:0; }
body.sr-discover .forest-categories i { font-size:var(--text-lg); color: var(--theme-accent); }
body.sr-discover .forest-categories .active { background: var(--sr-tint); color: var(--theme-accent); }
body.sr-discover .filter-chip { border: 1px solid var(--forest-border); color: var(--theme-text); background: var(--sr-surface); font-size:var(--text-sm); }
body.sr-discover .filter-chip.active { background: var(--sr-tint); border-color: var(--sr-brand); color: var(--theme-accent); }
body.sr-discover .forest-section-heading { display:flex; justify-content:space-between; align-items:center; gap:var(--space-md); margin-bottom:14px; }
body.sr-discover .forest-section-heading p { color: var(--theme-muted); margin-top:5px; line-height:1.5; }
body.sr-discover :is(.forest-outline,.forest-text-link) { display:inline-flex; align-items:center; justify-content:center; gap:var(--space-sm); min-height:44px; color: var(--theme-accent); text-decoration:none; font-size:var(--text-xs); white-space:nowrap; }
body.sr-discover .forest-outline { border: 1px solid var(--sr-brand); border-radius: 100px; background: transparent; padding:var(--space-sm) var(--space-md); }
body.sr-discover .forest-results-toolbar { display:flex; align-items:center; justify-content:space-between; gap:var(--space-sm); margin-bottom:12px; }
body.sr-discover #resultsCount { color: var(--theme-muted); font-size:var(--text-xs); }
body.sr-discover .forest-view-switch { display:flex; align-items:center; gap:var(--space-xs); }
body.sr-discover :is(.forest-view,.forest-filter-toggle) { min-height:44px; border: 0; border-radius: 100px; background: transparent; color: var(--theme-muted); padding:var(--space-xs) var(--space-sm); font-size:var(--text-xs); display:inline-flex; align-items:center; justify-content:center; gap:var(--space-xs); }
body.sr-discover .forest-view.active { background: var(--sr-tint); color: var(--theme-accent); }
body.sr-discover .forest-filter-toggle { border: 1px solid var(--forest-border); }
body.sr-discover #main-content .main-layout { display:block; width:100%; margin:0; border: 0; border-radius: 0; height:auto; overflow:visible; background: transparent; }
body.sr-discover #main-content .results-column { background: transparent; padding:0; overflow:visible; max-height:none; height:auto; }
body.sr-discover #main-content .results-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:var(--space-md); padding:0; }
body.sr-discover #main-content .map-column { position:relative; height:440px; margin-top:20px; border-radius: 20px; overflow:hidden; border: 1px solid var(--forest-border); width:100%; background: var(--sr-tint); }
body.sr-discover #main-content .map-column[hidden] { display:none; }
body.sr-discover #main-content .map-container { height:100%; width:100%; }
body.sr-discover #geo-status { position:absolute; bottom:16px; left:16px; max-width:calc(100% - 85px); padding:var(--space-xs) var(--space-sm); border-radius: 10px; background: var(--sr-surface); color: var(--theme-text); z-index:1000; }
body.sr-discover #geo-status:empty { display:none; }
body.sr-discover #main-content .restaurant-card.rc { display:flex; flex-direction:column; min-width:0; border: 1px solid var(--forest-border); border-radius: 20px; background: var(--forest-face) var(--sr-surface); box-shadow: var(--forest-relief); overflow:hidden; transform:none; transition:box-shadow .2s ease; }
body.sr-discover #main-content .restaurant-card.rc:is(:hover,:focus-within) { transform:none; box-shadow: var(--forest-lift); }
body.sr-discover #main-content .restaurant-card.rc .card-image { height:286px; min-height:286px; position:relative; width:100%; overflow:hidden; background: var(--sr-tint); }
body.sr-discover #main-content .restaurant-card.rc .card-image img { display:block; width:100%; height:100%; object-fit:cover; transform:none; }
body.sr-discover #main-content .restaurant-card.rc .card-image::after {
  content:''; position:absolute; inset:0; pointer-events:none;
  box-shadow: inset 0 1px var(--theme-shadow), inset 0 -18px 28px -22px var(--theme-shadow);
}
body.sr-discover #main-content .restaurant-card.rc .card-content { padding:var(--space-md) var(--space-md); min-width:0; }
body.sr-discover #main-content .restaurant-card.rc h3 { font-size:var(--text-xl); line-height:1.2; margin:0 0 9px; color: var(--theme-text); }
body.sr-discover #main-content .restaurant-card.rc .card-location { display:flex; align-items:center; gap:var(--space-sm); margin:0 0 8px; font-size:var(--text-xs); line-height:1.5; color: var(--theme-muted); }
body.sr-discover #main-content .restaurant-card.rc .card-location i { color: var(--theme-accent); font-size:var(--text-xs); }
body.sr-discover #main-content .restaurant-card.rc .forest-card-meta { display:flex; align-items:center; gap:var(--space-sm); justify-content:space-between; margin-bottom:8px; flex-wrap:wrap; }
body.sr-discover #main-content .restaurant-card.rc .rating { display:inline-flex; align-items:center; gap:var(--space-xs); background: transparent; color: var(--theme-text); font-size:var(--text-sm); padding:0; border-radius: 0; }
body.sr-discover #main-content .restaurant-card.rc .rating i { color: var(--theme-warning); }
body.sr-discover #main-content .restaurant-card.rc .rating small { font-size:var(--text-xs); color: var(--theme-muted); font-weight:400; }
body.sr-discover .forest-status { font-size:var(--text-xs); display:inline-flex; align-items:center; gap:var(--space-xs); }
body.sr-discover .forest-status::before { content:''; width:5px; height:5px; border-radius: 50%; background: currentColor; }
body.sr-discover .forest-status.is-open { color: var(--theme-success); }
body.sr-discover .forest-status.is-closed { color: var(--theme-muted); }
body.sr-discover .forest-hours { font-size:var(--text-xs); color: var(--theme-muted); }
body.sr-discover #main-content .restaurant-card.rc .card-price { font-size:var(--text-xs); color: var(--theme-muted); margin:0 0 9px; line-height:1.5; }
body.sr-discover #main-content .restaurant-card.rc .card-price strong { color: var(--theme-text); font-size:var(--text-sm); }
body.sr-discover .forest-card-bottom { display:flex; align-items:center; justify-content:space-between; gap:var(--space-sm); flex-wrap:wrap; }
body.sr-discover #main-content .restaurant-card.rc .card-tags { display:flex; align-items:center; gap:var(--space-xs); margin:0; flex-wrap:wrap; }
body.sr-discover #main-content .restaurant-card.rc .tag { border-radius: 100px; padding:var(--space-xs) var(--space-sm); font-size:var(--text-xs); background: var(--sr-tint); color: var(--theme-text); }
body.sr-discover #main-content .restaurant-card.rc .card-link { display:inline-flex; align-items:center; justify-content:center; gap:var(--space-sm); min-height:44px; border: 0; padding:0; margin:0; font-size:var(--text-xs); color: var(--theme-accent); text-decoration:none; }
body.sr-discover #main-content .restaurant-card.rc .fav-btn { position:absolute; top:12px; right:12px; z-index:2; width:44px; height:44px; border: 1px solid var(--theme-border); background: var(--theme-surface)!important; border-radius: 50%; color: var(--theme-success); display:grid; place-items:center; box-shadow: 0 2px 7px var(--theme-shadow); padding:0; }
body.sr-discover #main-content .restaurant-card.rc .fav-btn i { color: var(--theme-success)!important; font-size:var(--text-lg); }
body.sr-discover #main-content .restaurant-card.rc .fav-btn[aria-pressed=true] i { color: var(--theme-danger)!important; }
body.sr-discover .forest-promo-badge { position:absolute; left:14px; top:14px; display:flex; align-items:center; gap:var(--space-xs); background: var(--theme-success-bg); color: var(--theme-text); font-size:var(--text-xs); border-radius: 100px; padding:var(--space-xs) var(--space-sm); }
body.sr-discover .forest-photo-missing { display:flex; width:100%; height:100%; align-items:center; justify-content:center; flex-direction:column; gap:var(--space-md); color: var(--theme-muted); }
body.sr-discover .forest-photo-missing i { font-size:var(--text-2xl); }
body.sr-discover .forest-image-unavailable::before { content:'Fotografía no disponible'; position:absolute; inset:0; display:grid; place-items:center; color: var(--theme-muted); }
body.sr-discover :is(.forest-offers,.forest-recommendation,.forest-nearby,.forest-home-kitchen,.forest-business) { margin-top:32px; }
body.sr-discover .forest-promo-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:var(--space-md); }
body.sr-discover .forest-promo { display:flex; align-items:center; position:relative; isolation:isolate; min-height:130px; overflow:hidden; border-radius: 16px; background: var(--theme-success-bg); color: var(--theme-text); text-decoration:none; padding:var(--space-md) var(--space-lg); box-shadow: var(--forest-hero-depth); }
body.sr-discover .forest-promo img { position:absolute; width:42%; height:100%; object-fit:cover; inset:0 0 0 auto; z-index:-2; }
body.sr-discover .forest-promo > div { width:58%; padding-right:var(--space-sm); }
body.sr-discover .forest-promo::before { content:''; position:absolute; inset:0 42% 0 0; z-index:-1; background:var(--theme-success-bg); }
body.sr-discover .forest-promo h3 { font-size:var(--text-xl); color: inherit; line-height:1.12; margin:0 0 6px; max-width:17ch; }
body.sr-discover .forest-promo p { font-size:var(--text-xs); color: var(--theme-text); margin-bottom:9px; }
body.sr-discover .forest-promo span { display:inline-flex; border-radius: 100px; background: var(--forest-control-face) var(--theme-warning-bg); color: var(--theme-warning); font-size:var(--text-xs); padding:var(--space-xs) var(--space-sm); box-shadow: var(--forest-control); }
body.sr-discover .forest-recommendation { display:flex; align-items:center; gap:var(--space-md); position:relative; padding:var(--space-md) var(--space-lg); min-height:102px; background: var(--forest-face) var(--sr-surface); border: 1px solid var(--forest-border); border-radius: 20px; box-shadow: var(--forest-relief); }
body.sr-discover .forest-chef { width:130px; height:115px; object-fit:contain; margin:-26px 0 -14px; align-self:end; }
body.sr-discover .forest-recommendation-copy { flex:1; min-width:230px; }
body.sr-discover .forest-recommendation h2 { font-size:var(--text-xl); }
body.sr-discover .forest-recommendation p { font-size:var(--text-xs); margin-top:6px; }
body.sr-discover #forest-craving-form { display:flex; flex:1.5; align-items:center; gap:var(--space-sm); min-width:0; }
body.sr-discover #forest-craving { border-radius: 100px; width:100%; min-width:0; padding:var(--space-sm) var(--space-md); min-height:46px; background: var(--sr-surface); border: 1px solid var(--forest-border); font-size:var(--text-xs); box-shadow: var(--forest-recess); }
body.sr-discover #forest-recommend { display:flex; align-items:center; justify-content:center; gap:var(--space-sm); min-height:46px; padding:var(--space-sm) var(--space-lg); background: var(--forest-control-face) var(--theme-accent-bg); color: var(--theme-text); border: 0; border-radius: 100px; font-size:var(--text-xs); font-weight:700; box-shadow: var(--forest-control); }
body.sr-discover :is(.forest-search-submit,#forest-recommend):active { box-shadow: var(--forest-recess); }
body.sr-discover #forest-recommend i { color: var(--theme-warning); }
body.sr-discover :is(.forest-nearby,.forest-home-kitchen) { display:flex; align-items:center; justify-content:space-between; gap:var(--space-lg); padding:var(--space-lg) var(--space-lg); border: 1px solid var(--forest-border); border-radius: 18px; background: var(--forest-face) var(--sr-surface); box-shadow: var(--forest-relief); }
body.sr-discover :is(.forest-nearby > div,.forest-home-kitchen-copy) { display:flex; align-items:center; gap:var(--space-md); }
body.sr-discover :is(.forest-nearby,.forest-home-kitchen) h2 { font-size:var(--text-xl); }
body.sr-discover :is(.forest-nearby,.forest-home-kitchen) p { color: var(--theme-muted); font-size:var(--text-xs); margin-top:6px; }
body.sr-discover .forest-compact-icon { display:grid; place-items:center; flex-shrink:0; width:48px; height:48px; border-radius: 16px; background: var(--forest-control-face) var(--sr-tint); color: var(--theme-accent); font-size:var(--text-lg); box-shadow: var(--forest-control); }
body.sr-discover .forest-business { display:flex; align-items:center; justify-content:space-between; gap:var(--space-lg); min-height:118px; background: var(--forest-hero-face); border-radius: 18px; color: var(--theme-text); padding:var(--space-md) var(--space-lg); overflow:hidden; box-shadow: var(--forest-hero-depth); }
body.sr-discover .forest-business img { width:185px; height:110px; object-fit:contain; margin:-10px 0; }
body.sr-discover .forest-business > div { flex:1; }
body.sr-discover .forest-business h2 { color: inherit; font-size:clamp(23px,2vw,30px); margin:0; }
body.sr-discover .forest-business p { font-family:var(--forest-display); font-size:clamp(21px,1.8vw,27px); color: var(--theme-warning); line-height:1.3; margin-top:3px; }
body.sr-discover .forest-business .forest-light-button { flex-shrink:0; }
body.sr-discover .forest-extras { width:min(calc(100% - 2 * var(--sr-gutter)),1440px); margin:0 auto 36px; }
body.sr-discover .forest-extras h2 { font-family:var(--forest-display); font-size:var(--text-xl); }
body.sr-discover .forest-extras section { margin-top:32px; }
body.sr-discover .forest-extras details { border-top: 1px solid var(--forest-border); padding:var(--space-sm) 0; }
body.sr-discover .forest-extras summary { cursor:pointer; min-height:44px; display:list-item; align-content:center; font-weight:600; }
body.sr-discover .forest-extras details p { max-width:75ch; color: var(--theme-muted); }
body.sr-discover .sr-footer { margin-block:0; margin-right:0; background: transparent; }
body.sr-discover .empty-state { grid-column:1/-1; padding:var(--space-xl) var(--space-md); border: 1px dashed var(--sr-line); border-radius: 18px; text-align:center; }
body.sr-discover .empty-state p { margin:10px 0 18px; color: var(--theme-muted); }
@media(min-width:1600px) { body.sr-discover .forest-hero { min-height:290px; } }
@media(max-width:1199px) {
  body.sr-discover #main-content .results-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
  body.sr-discover .forest-hero-copy { padding-left:var(--space-lg); }
  body.sr-discover .forest-hero { grid-template-columns:43% 57%; }
  body.sr-discover .forest-categories { width:100%; }
  body.sr-discover .forest-categories :is(button,a) { padding-inline:var(--space-sm); }
  body.sr-discover .forest-recommendation { flex-wrap:wrap; }
  body.sr-discover #forest-craving-form { flex:1 1 100%; }
  body.sr-discover .forest-chef { width:110px; height:100px; }
  body.sr-discover .forest-business { gap:var(--space-md); }
  body.sr-discover .forest-business img { width:130px; }
  body.sr-discover .forest-business .forest-light-button { padding-inline:var(--space-md); font-size:var(--text-xs); }
}
@media(max-width:900px) {
  body.sr-discover .sr-public-links { gap:var(--space-md); }
  body.sr-discover .sr-public-links a { font-size:var(--text-xs); }
  body.sr-discover .sr-top { padding-inline:var(--space-md); gap:var(--space-md); }
  body.sr-discover .forest-hero h1 { font-size:var(--text-2xl); }
  body.sr-discover .forest-hero-copy > p:not(.forest-campaign) { font-size:var(--text-xs); }
  body.sr-discover .forest-desktop-break { display:none; }
  body.sr-discover .forest-promo-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
  body.sr-discover .forest-promo:last-child { grid-column:1/-1; }
  body.sr-discover .forest-business { flex-wrap:wrap; }
  body.sr-discover .forest-business .forest-light-button { margin-left:148px; }
}
@media(max-width:800px) {
  body.sr-discover .forest-search-row { flex-wrap:wrap; gap:var(--space-sm); }
  body.sr-discover .forest-city { order:0; flex:1; border: 0; min-height:36px; padding:0; font-size:var(--text-xs); }
  body.sr-discover .forest-ai-search { order:1; min-height:44px; font-size:var(--text-xs); padding:var(--space-sm) var(--space-md); }
  body.sr-discover .forest-query { order:2; flex:1 1 calc(100% - 70px); background: var(--sr-surface); border: 1px solid var(--forest-border); border-radius: 100px; padding-left:var(--space-md); }
  body.sr-discover .forest-search-submit { order:3; min-width:52px; }
  body.sr-discover .forest-hero { min-height:285px; grid-template-columns:49% 51%; }
  body.sr-discover .forest-hero-copy { padding:var(--space-lg); }
  body.sr-discover .forest-hero h1 { font-size:var(--text-2xl); }
  body.sr-discover .forest-hero-photo { margin-left:-10px; border-radius: 90px 0 0 90px / 55% 0 0 55%; }
  body.sr-discover .forest-section-heading { align-items:flex-start; }
  body.sr-discover .forest-result-actions .forest-outline { font-size:var(--text-xs); padding-inline:var(--space-sm); white-space:normal; text-align:center; }
  body.sr-discover .forest-filter-fields { grid-template-columns:1fr; }
  body.sr-discover :is(.forest-nearby,.forest-home-kitchen) { flex-wrap:wrap; gap:var(--space-md); padding:var(--space-md); }
}
@media(max-width:599px) {
  body.sr-discover .sr-top { height:60px; padding-inline:var(--space-sm); gap:var(--space-xs); }
  body.sr-discover .sr-logo { font-size:var(--text-xl); gap:var(--space-xs); }
  body.sr-discover .sr-mark { width:30px; height:30px; }
  body.sr-discover .sr-actions .sr-favorites-link { display:none; }
  body.sr-discover .sr-actions #themeToggle { min-width:36px; }
  body.sr-discover .sr-login { font-size:var(--text-xs); }
  body.sr-discover .forest-search { margin:8px 0 14px; }
  body.sr-discover .forest-hero { grid-template-columns:1fr; border-radius: 20px; }
  body.sr-discover .forest-hero-copy { padding:var(--space-lg); }
  body.sr-discover .forest-hero h1 { font-size:clamp(31px,8.3vw,44px); }
  body.sr-discover .forest-hero-copy > p:not(.forest-campaign) { font-size:var(--text-sm); }
  body.sr-discover .forest-hero-photo { margin-left:0; border-radius: 55% 55% 0 0 / 12% 12% 0 0; height:180px; }
  body.sr-discover .forest-hero-photo img { object-position:50% 52%; }
  body.sr-discover .forest-categories { border-radius: 16px; padding:var(--space-xs); margin:12px 0 24px; }
  body.sr-discover .forest-categories :is(button,a) { font-size:var(--text-xs); padding-inline:var(--space-md); }
  body.sr-discover .forest-categories i { font-size:var(--text-base); }
  body.sr-discover .forest-section-heading { flex-wrap:wrap; gap:var(--space-sm); }
  body.sr-discover .forest-section-heading h2 { font-size:var(--text-xl); }
  body.sr-discover .forest-section-heading p { font-size:var(--text-xs); }
  body.sr-discover .forest-result-actions .forest-outline { min-height:44px; padding:var(--space-sm) var(--space-md); }
  body.sr-discover .forest-results-toolbar { flex-wrap:wrap; gap:var(--space-xs); }
  body.sr-discover .forest-view-switch { margin-left:auto; }
  body.sr-discover .forest-view { padding:var(--space-xs) var(--space-sm); font-size:var(--text-xs); }
  body.sr-discover .forest-filter-toggle { padding:var(--space-xs) var(--space-sm); }
  body.sr-discover .forest-filter-toggle span { display:none; }
  body.sr-discover #main-content .results-grid { grid-template-columns:minmax(0,1fr); gap:var(--space-md); }
  body.sr-discover #main-content .restaurant-card.rc .card-image { height:310px; min-height:310px; }
  body.sr-discover #main-content .restaurant-card.rc h3 { font-size:var(--text-xl); }
  body.sr-discover .forest-promo-grid { grid-template-columns:minmax(0,1fr); gap:var(--space-sm); }
  body.sr-discover .forest-promo { min-height:134px; }
  body.sr-discover .forest-promo:last-child { grid-column:auto; }
  body.sr-discover .forest-recommendation { padding:var(--space-md); gap:var(--space-sm); }
  body.sr-discover .forest-chef { width:82px; height:84px; margin:-20px 0 0 -8px; }
  body.sr-discover .forest-recommendation-copy { min-width:0; }
  body.sr-discover .forest-recommendation h2 { font-size:var(--text-xl); }
  body.sr-discover .forest-recommendation p { font-size:var(--text-xs); }
  body.sr-discover #forest-craving-form { flex-wrap:wrap; gap:var(--space-sm); }
  body.sr-discover #forest-craving { min-height:46px; }
  body.sr-discover #forest-recommend { width:100%; }
  body.sr-discover :is(.forest-nearby,.forest-home-kitchen) { padding:var(--space-md); }
  body.sr-discover :is(.forest-nearby,.forest-home-kitchen) h2 { font-size:var(--text-xl); }
  body.sr-discover .forest-compact-icon { width:38px; height:38px; border-radius: 12px; font-size:var(--text-base); }
  body.sr-discover :is(.forest-nearby > div,.forest-home-kitchen-copy) { gap:var(--space-sm); }
  body.sr-discover .forest-business { padding:var(--space-md); gap:var(--space-sm); }
  body.sr-discover .forest-business img { width:95px; height:90px; }
  body.sr-discover .forest-business h2 { font-size:var(--text-xl); }
  body.sr-discover .forest-business p { font-size:var(--text-lg); }
  body.sr-discover .forest-business .forest-light-button { margin:8px 0 0; width:100%; font-size:var(--text-xs); padding-inline:var(--space-sm); }
  body.sr-discover #main-content .map-column { height:360px; }
  body.sr-discover .forest-extras h2 { font-size:var(--text-xl); }
  body.sr-discover .sr-footer { padding:var(--space-lg) var(--space-md); }
}
@media(prefers-reduced-motion:reduce) { body.sr-discover * { scroll-behavior:auto!important; transition:none!important; animation:none!important; } }
@media(min-width:1100px) {
  body.sr-discover .sr-sidebar { display:none; }
  body.sr-discover #main-content { width:100%; max-width:none; margin-left:0; margin-right:0; }
  .sr-drawer-open body.sr-discover .sr-sidebar { display:flex; }
}
body.sr-discover .forest-drawer-theme { display:flex; align-items:center; justify-content:flex-start; gap:var(--space-md); width:100%; border-radius: 12px; padding:var(--space-sm) var(--space-sm); margin-top:12px; }
body.sr-discover .forest-drawer-theme::after { content:'Cambiar tema'; font-size:var(--text-sm); }
@media(min-width:1100px) {
  body.sr-discover:not([data-role=guest]) .sr-menu-button { display:grid; }
  .sr-drawer-open body.sr-discover .sr-sidebar :is(a span,form span,.sr-group) { position:static; clip-path:none; width:auto; height:auto; overflow:visible; white-space:normal; }
}
body .sr-map-dialog #main-map.leaflet-container { position:relative!important; overflow:hidden!important; background:var(--theme-map-background); }
body .sr-map-dialog #main-map .leaflet-pane { position:absolute!important; left:0!important; top:0!important; }
body .sr-map-dialog #main-map .leaflet-tile-pane { z-index:200!important; }
body .sr-map-dialog #main-map img.leaflet-tile { display:block!important; width:256px!important; height:256px!important; max-width:none!important; max-height:none!important; object-fit:initial!important; opacity:1!important; visibility:visible!important; }
body .sr-map-dialog #main-map .leaflet-control-attribution { z-index:1000!important; color:var(--theme-map-control-text)!important; background:var(--theme-map-control-bg)!important; }
"""

# ============================================================
# 5. forest-depth.css
# ============================================================
FILES["forest-depth.css"] = r"""/* Directional lighting, contact shadows and raised edges for shared surfaces. */
:root {
  --forest-light-edge: var(--theme-shadow);
  --forest-shadow:var(--theme-shadow-rgb);
  --forest-face: linear-gradient(155deg, var(--sr-surface) 38%, color-mix(in srgb, var(--sr-surface) 78%, var(--sr-tint)));
  --forest-relief: inset 0 1px var(--forest-light-edge), 0 2px 4px rgb(var(--forest-shadow) / 5%), 0 14px 30px -18px rgb(var(--forest-shadow) / 29%);
  --forest-lift: inset 0 1px var(--forest-light-edge), 0 4px 8px rgb(var(--forest-shadow) / 7%), 0 20px 38px -19px rgb(var(--forest-shadow) / 36%);
  --forest-recess: inset 0 2px 5px rgb(var(--forest-shadow) / 12%), 0 1px var(--forest-light-edge);
  --forest-control-face: linear-gradient(150deg, var(--theme-surface), transparent 52%, var(--theme-surface));
  --forest-control: inset 0 1px var(--theme-text), inset 0 -2px var(--theme-text), 0 5px 12px -6px rgb(var(--forest-shadow) / 45%);
  --forest-cream-face: linear-gradient(165deg, var(--theme-surface) 16%, var(--theme-warning-bg));
  --forest-cream-edge: inset 0 1px var(--theme-shadow), inset 0 -2px var(--theme-shadow), 0 5px 12px var(--theme-shadow);
  --forest-hero-face: radial-gradient(ellipse at 83% 0%, var(--theme-warning-bg), transparent 54%), linear-gradient(142deg, var(--theme-success-bg), var(--theme-success-bg) 53%, var(--theme-success-bg));
  --forest-hero-depth: inset 0 1px var(--theme-shadow), inset 0 -2px var(--theme-shadow), 0 24px 42px -24px rgb(var(--forest-shadow) / 55%);
}
:root[data-theme="dark"] {
  --forest-light-edge: var(--theme-shadow);
  --forest-shadow:var(--theme-shadow-rgb);
}
body .sr-header {
  box-shadow: inset 0 1px var(--forest-light-edge), 0 7px 19px -14px rgb(var(--forest-shadow) / 56%);
}
body .sr-mark {
  box-shadow: var(--forest-control);
}
body .sr-sidebar {
  background-image: linear-gradient(145deg, var(--forest-light-edge), transparent 145px);
  box-shadow: inset -1px 0 var(--forest-light-edge), 10px 0 24px -22px rgb(var(--forest-shadow) / 57%);
}
body:is([data-role="business_owner"], [data-role="admin"]) .sr-sidebar {
  --forest-light-edge: var(--theme-shadow);
  background-image: linear-gradient(145deg, var(--forest-light-edge), transparent 145px);
}
body .sr-sidebar [aria-current="page"] {
  background-image: var(--forest-control-face);
  box-shadow: inset 3px 0 var(--sr-brand), var(--forest-relief);
}
body .sr-mobile-nav {
  box-shadow: inset 0 1px var(--forest-light-edge), 0 -9px 24px -17px rgb(var(--forest-shadow) / 45%);
}
body .sr-mobile-nav [aria-current="page"] {
  background-image: var(--forest-control-face);
  box-shadow: var(--forest-relief);
}
body .sr-footer {
  box-shadow: inset 0 1px var(--forest-light-edge), 0 -8px 30px -25px rgb(var(--forest-shadow) / 42%);
}
body :is(.sr-signup, .ax-submit, .market-hero .market-link, .sr-campaign .sr-button, .mgr-hero > a, .radar-primary) {
  background-image: var(--forest-control-face);
  box-shadow: var(--forest-control);
}
body :is(.sr-signup, .ax-submit, .market-hero .market-link, .sr-campaign .sr-button, .mgr-hero > a, .radar-primary):active:not(:disabled) {
  box-shadow: inset 0 2px 5px var(--theme-shadow);
}
body :is(.sr-campaign-hero, .sr-offers-hero, .market-hero, .mgr .mgr-hero, .ax-food-host) {
  background: var(--forest-hero-face);
  color: var(--theme-text);
  box-shadow: var(--forest-hero-depth);
}
body .market-hero {
  padding:clamp(var(--space-md), 3.6vw, var(--space-xl));
  border-radius: var(--sr-radius-card);
}
body .market-shell:has(> .market-filters) .market-hero {
  background-color: var(--theme-success-bg);
  background-image: linear-gradient(90deg, var(--theme-surface) 5%, var(--theme-overlay) 38%, var(--theme-overlay) 60%, var(--theme-overlay) 90%), url('../images/forest/food-inspiration.webp');
  background-position: center, center 47%;
  background-size: cover;
}
body .market-hero > div { min-width: 0; }
body .market-hero h1 { color: inherit; }
body .market-hero :is(h1, p) { text-shadow: 0 2px 8px var(--theme-shadow); }
body .market-shell .market-hero a { color: var(--theme-text); }
body .market-shell .market-hero a.market-link {
  background: var(--forest-cream-face);
  color: var(--theme-success);
  box-shadow: var(--forest-cream-edge);
  text-decoration: none;
}
body .market-shell .market-hero a.market-link:hover { text-decoration: underline; }
body .market-hero > strong { color: var(--theme-warning); }
body .market-shell .market-filters {
  border: 1px solid var(--sr-line);
  background-image: var(--forest-face);
  box-shadow: var(--forest-relief);
}
body .market-shell :is(input:not([type="checkbox"]):not([type="hidden"]), select, textarea) {
  box-shadow: var(--forest-recess);
}
body .market-shell :is(.market-form, .market-filters, .market-inline) button:not(.secondary) {
  background-image: var(--forest-control-face);
  box-shadow: var(--forest-control);
}
body .market-shell :is(.market-form, .market-filters, .market-inline) button:active:not(:disabled) {
  box-shadow: var(--forest-recess);
}
body #main-content :is(
  .market-panel, .market-offer, .mgr-card, .mgr-metric, .profile-sidebar, .profile-form-container,
  .owner-sidebar, .booking-card, .detail-card, .admin-card, .notification-item, .radar-panel, .radar-candidate,
  .sr-plan, .sr-business-bento > article
) {
  background-image: var(--forest-face);
  box-shadow: var(--forest-relief);
}
body #main-content .sr-business-bento > article:first-child {
  background-image: linear-gradient(145deg, color-mix(in srgb, var(--theme-accent-bg) 13%, var(--sr-tint)), var(--sr-tint));
}
:root body.sr-auth #main-content .ax-card {
  background-image: var(--forest-face);
  box-shadow: var(--forest-lift);
}
body #main-content :is(.market-photo, .sr-editorial-slides, .detail-container .main-image) {
  box-shadow: var(--forest-relief);
}
@media (max-width: 700px) {
  body .market-shell:has(> .market-filters) .market-hero {
    background-image: linear-gradient(90deg, var(--theme-overlay), var(--theme-overlay)), url('../images/forest/food-inspiration.webp');
  }
}
body:not(.sr-discover) #main-content .restaurant-card {
  background-image: var(--forest-face);
  box-shadow: var(--forest-relief);
}
body:not(.sr-discover) #main-content .restaurant-card:focus-within,
body #main-content .market-offer:focus-within {
  box-shadow: var(--forest-lift);
}
@media (hover: hover) and (pointer: fine) {
  body:not(.sr-discover) #main-content .restaurant-card:hover,
  body #main-content .market-offer:hover {
    box-shadow: var(--forest-lift);
  }
}
body .catalog-shell {
  --cat-ink: var(--theme-text);
  --cat-muted: var(--theme-muted);
  --cat-faint: var(--theme-muted);
  --cat-bg: var(--theme-bg);
  --cat-panel: var(--theme-surface);
  --cat-panel-solid: var(--theme-surface);
  --cat-line: var(--theme-border);
  --cat-accent: var(--theme-accent);
  --cat-accent-deep: var(--theme-accent);
  --cat-accent-soft: var(--theme-elevated);
  --cat-shadow: inset 0 1px var(--theme-shadow), 0 15px 28px -18px var(--theme-shadow);
  --cat-inset: inset 0 1px var(--theme-shadow), inset 0 -2px var(--theme-shadow);
  background: radial-gradient(ellipse at 7% 0%, var(--theme-warning-bg), transparent 42%), radial-gradient(ellipse at 98% 22%, var(--theme-success-bg), transparent 46%), var(--cat-bg);
}
body .catalog-shell[data-theme="dark"] {
  --cat-ink: var(--theme-text);
  --cat-muted: var(--theme-muted);
  --cat-faint: var(--theme-muted);
  --cat-bg: var(--theme-bg);
  --cat-panel: var(--theme-surface);
  --cat-panel-solid: var(--theme-surface);
  --cat-line: var(--theme-border);
  --cat-accent: var(--theme-accent);
  --cat-accent-deep: var(--theme-accent);
  --cat-accent-soft: var(--theme-elevated);
  --cat-shadow: inset 0 1px var(--theme-shadow), 0 16px 33px -19px var(--theme-shadow);
  --cat-inset: inset 0 1px var(--theme-shadow), inset 0 -2px var(--theme-shadow);
  background: radial-gradient(ellipse at 7% 0%, var(--theme-surface), transparent 42%), radial-gradient(ellipse at 98% 22%, var(--theme-success-bg), transparent 46%), var(--cat-bg);
}
body .catalog-shell[data-theme="dark"] .catalog-eyebrow { color: var(--theme-accent); }
body .catalog-atmosphere--one {
  background: linear-gradient(145deg, var(--cat-panel-solid), var(--theme-accent-bg));
  box-shadow: 18px 24px 48px rgb(var(--forest-shadow) / 13%), var(--cat-inset);
}
body .catalog-atmosphere--two {
  background: linear-gradient(145deg, color-mix(in srgb, var(--theme-accent-bg) 24%, var(--cat-panel-solid)), var(--theme-accent-bg));
  box-shadow: 10px 18px 38px rgb(var(--forest-shadow) / 12%), var(--cat-inset);
}
body .catalog-metric-card--dark {
  background: var(--forest-hero-face);
  border-color: var(--theme-border);
  color: var(--theme-text);
  box-shadow: var(--forest-hero-depth);
}
body .catalog-metric-card--dark .catalog-metric-icon {
  background: var(--theme-success-bg);
  color: var(--theme-warning);
  box-shadow: var(--forest-control);
}
body .catalog-button--primary {
  background: linear-gradient(145deg, var(--theme-success-bg), var(--theme-success-bg));
  color: var(--theme-text);
  box-shadow: var(--forest-control);
}
"""

# ============================================================
# 6. components.css
# ============================================================
FILES["components.css"] = r"""/* Restaurant Card */
.restaurant-card { border-radius: 12px; overflow: hidden; transition: transform 0.2s; }
.card-image { position: relative; aspect-ratio: 4/3; border-radius: 12px; overflow: hidden; }
.card-image img { width: 100%; height: 100%; object-fit: cover; }
.promo-badge { position: absolute; top: 12px; left: 12px; background: var(--theme-surface); padding:var(--space-xs) var(--space-sm); border-radius: 4px; font-size:var(--text-xs); font-weight: 700; box-shadow: 0 2px 4px var(--theme-shadow); }
.fav-btn { position: absolute; top: 12px; right: 12px; background: transparent; border: none; color: var(--theme-text); cursor: pointer; text-shadow: 0 0 4px var(--theme-shadow); }
.card-content { padding:var(--space-sm) 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.card-header h3 { font-size:var(--text-base); font-weight: 600; }
.rating { display: flex; align-items: center; gap:var(--space-xs); font-size:var(--text-sm); }
.rating .material-icons { font-size:var(--text-base); color: var(--theme-text); }
.district { color: var(--theme-text); font-size:var(--text-sm); }
.price { font-weight: 600; margin-top: 4px; }
.tags { display: flex; gap:var(--space-sm); margin-top: 8px; }
.tag { font-size:var(--text-xs); background: var(--theme-surface); padding:0.125rem var(--space-sm); border-radius: 4px; color: var(--theme-text); }
.ia-justification { margin-top: 12px; background: var(--theme-surface); color: var(--theme-success); padding:var(--space-sm); border-radius: 8px; font-size:var(--text-sm); display: flex; align-items: center; gap:var(--space-xs); }
.ia-justification .material-icons { font-size:var(--text-lg); }
.user-btn { display: flex; align-items: center; gap:var(--space-sm); padding:var(--space-xs) var(--space-xs) var(--space-xs) var(--space-sm); border: 1px solid var(--theme-border); border-radius: 21px; background: var(--theme-surface); cursor: pointer; transition: box-shadow 0.2s; }
.user-btn:hover { box-shadow: 0 2px 4px var(--theme-shadow); }
.account-circle { color: var(--theme-text); font-size:var(--text-2xl); }
.dropdown { position: relative; display: inline-block; }
.dropdown-content { display: none; position: absolute; right: 0; background-color: var(--theme-surface); min-width: 240px; box-shadow: 0 2px 16px var(--theme-shadow); border-radius: 12px; padding:var(--space-sm) 0; z-index: 1; margin-top: 8px; }
.dropdown-content a { color: var(--theme-text); padding:var(--space-sm) var(--space-md); display: block; font-size:var(--text-sm); }
.dropdown-content a:hover { background-color: var(--theme-surface); }
.dropdown:hover .dropdown-content { display: block; }
"""

# ============================================================
# 7. discovery.css
# ============================================================
FILES["discovery.css"] = r"""/* Radar SmartResto: planos cartográficos, porcelana cálida y relieve suave. */
.radar{max-width:1480px;margin:28px auto 70px;padding:0 var(--space-lg);color: var(--sr-text,var(--theme-success));--radar-surface: var(--sr-surface,var(--theme-surface));--radar-ink: var(--sr-text,var(--theme-success));--radar-accent: var(--theme-accent);--radar-subtle: color-mix(in srgb,var(--radar-surface) 92%,var(--theme-success))}
.radar-heading,.radar-section-heading{display:flex;align-items:center;justify-content:space-between;gap:var(--space-lg);margin-bottom:26px}
.radar-heading h1,.radar-claim-page h1{font-size:clamp(30px,4vw,48px);line-height:1.1;letter-spacing:-1.5px;margin:8px 0 14px}
.radar p{line-height:1.6}
.radar-kicker{font-size:var(--text-sm);color: var(--theme-accent);font-weight:600;margin:0}
.radar-workspace{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(310px,1fr);gap:var(--space-lg);margin-bottom:30px}
.radar-territory{background: var(--radar-surface);border: 1px solid var(--sr-line,var(--theme-border));border-radius: 24px;overflow:hidden;box-shadow: var(--sr-depth-1)}
.radar-map-heading{padding:var(--space-lg) var(--space-lg);display:flex;justify-content:space-between;align-items:center;gap:var(--space-md)}
.radar-map-heading h2,.radar-control h2{font-size:var(--text-xl);letter-spacing:-.5px;margin:0 0 8px}
.radar-map-heading p{font-size:var(--text-sm);margin:0;color: var(--sr-muted,var(--theme-text))}
.radar-location{font-size:var(--text-xs);background: var(--radar-subtle);padding:var(--space-sm) var(--space-sm);border-radius: 12px;white-space:nowrap}
.radar-map{height:330px;background: linear-gradient(150deg,var(--theme-success-bg),var(--theme-surface));z-index:0}
.radar-map-foot{padding:var(--space-md) var(--space-lg);font-size:var(--text-xs);color: var(--sr-muted,var(--theme-text));display:flex;justify-content:space-between;gap:var(--space-sm)}
.radar-control{padding:var(--space-lg) var(--space-lg);border-radius: 26px;border: 1px solid color-mix(in srgb,var(--radar-accent) 20%,var(--radar-surface));background: radial-gradient(ellipse at 90% 10%,color-mix(in srgb,var(--theme-accent-bg) 12%,transparent),transparent 65%),var(--radar-surface);box-shadow: var(--sr-depth-2)}
.radar-emblem{width:142px;height:110px;color: var(--theme-accent);filter:drop-shadow(0 12px 10px var(--theme-overlay))}
.radar-control>small{display:block;margin:14px 0;color: var(--sr-muted,var(--theme-text));font-size:var(--text-xs);line-height:1.6}
.radar-counts{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--space-sm);border-top: 1px solid var(--sr-line,var(--theme-border));padding-top:var(--space-md);margin-top:22px}
.radar-counts strong{font-size:var(--text-2xl);display:block}
.radar-counts span{font-size:var(--text-xs)}
.radar button,.radar input,.radar textarea,.radar select,dialog button,dialog textarea{font:inherit}
.radar-primary,.radar-secondary{display:inline-flex;align-items:center;justify-content:center;gap:var(--space-sm);border-radius: 12px;min-height:44px;padding:var(--space-sm) var(--space-md);text-decoration:none;cursor:pointer;border: 1px solid transparent;font-weight:600;font-size:var(--text-sm);transition:box-shadow .18s,background .18s}
.radar-primary{background: linear-gradient(145deg,var(--theme-success-bg),var(--theme-success-bg));color: var(--theme-text);box-shadow: 0 7px 14px var(--theme-shadow),inset 0 1px 0 var(--theme-shadow)}
.radar-primary:hover{box-shadow: 0 9px 20px var(--theme-shadow)}
.radar-secondary{color: var(--theme-text);background: var(--radar-surface);border-color: var(--sr-line,var(--theme-border));box-shadow: inset 0 1px 0 var(--theme-shadow),0 2px 5px var(--theme-shadow)}
.radar button:disabled{opacity:.6;cursor:wait}
.radar input,.radar select,.radar textarea,dialog textarea{width:100%;border: 1px solid var(--sr-line,var(--theme-border));background: var(--radar-surface,var(--theme-surface));color: var(--radar-ink,var(--theme-success));border-radius: 11px;padding:var(--space-sm);min-height:44px;box-sizing:border-box}
.radar-filters{display:flex;gap:var(--space-sm)}
.radar-filters input{min-width:210px}
.radar-section-heading h2{font-size:var(--text-xl);margin:0 0 8px}
.radar-section-heading p{margin:0;font-size:var(--text-sm);color: var(--sr-muted,var(--theme-text))}
.radar-candidates{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--space-md)}
.radar-candidate{background: var(--radar-surface);border: 1px solid var(--sr-line,var(--theme-border));border-radius: 19px;padding:var(--space-lg);box-shadow: var(--sr-depth-0),0 8px 20px var(--theme-shadow)}
.radar-candidate[hidden]{display:none}
.radar-candidate-top{display:flex;justify-content:space-between;gap:var(--space-sm);align-items:center}
.radar-type{font-size:var(--text-xs);color: var(--sr-muted,var(--theme-text))}
.radar-badge{display:inline-flex;border-radius: 8px;padding:var(--space-xs) var(--space-sm);font-size:var(--text-xs);background: var(--radar-subtle);color: var(--theme-text)}
.radar-badge.pending_review,.radar-badge.claim_pending{background: var(--theme-warning-bg);color: var(--theme-warning)}
.radar-badge.duplicate,.radar-badge.rejected{background: var(--theme-danger-bg);color: var(--theme-danger)}
.radar-badge.approved,.radar-badge.claimed{background: var(--theme-success-bg);color: var(--theme-success)}
.radar-candidate h3{font-size:var(--text-xl);margin:16px 0 6px;letter-spacing:-.4px}
.radar-candidate p{font-size:var(--text-sm)}
.radar-completeness{margin:20px 0 14px}
.radar-completeness>span{display:flex;justify-content:space-between;font-size:var(--text-xs)}
.radar-completeness meter{display:block;width:100%;height:12px;margin:8px 0;accent-color: var(--radar-accent)}
.radar-completeness small{font-size:var(--text-xs);color: var(--sr-muted,var(--theme-text))}
.radar-warning{color: var(--theme-warning);font-size:var(--text-xs)}
.radar details{border-top: 1px solid var(--sr-line,var(--theme-border));margin:18px 0;padding-top:var(--space-md)}
.radar summary{cursor:pointer;font-size:var(--text-sm);font-weight:600;min-height:32px}
.radar-evidence div{display:grid;grid-template-columns:110px minmax(0,1fr);gap:var(--space-sm);margin:14px 0;font-size:var(--text-xs)}
.radar-evidence dt{color: var(--sr-muted,var(--theme-text))}
.radar-evidence dd{margin:0;overflow-wrap:anywhere}
.radar-evidence small,.radar-evidence q{display:block;margin-top:6px;color: var(--sr-muted,var(--theme-text))}
.radar-reference{display:block;font-size:var(--text-xs);margin:10px 0;color: var(--theme-accent);overflow-wrap:anywhere}
.radar-candidate-actions{display:flex;gap:var(--space-sm);flex-wrap:wrap;margin-top:22px}
.radar-empty{grid-column:1/-1;text-align:center;padding:var(--space-xl) var(--space-md);border: 1px dashed var(--sr-line,var(--theme-border));border-radius: 20px;background: var(--radar-surface)}
.radar-empty svg{width:76px;stroke: var(--theme-accent);stroke-width:2;fill: none}
.radar-empty p{max-width:600px;margin:auto;font-size:var(--text-sm)}
.radar-bottom-grid{display:grid;grid-template-columns:1fr 1fr;gap:var(--space-lg);margin:30px 0}
.radar-panel{background: var(--radar-surface);border: 1px solid var(--sr-line,var(--theme-border));border-radius: 20px;padding:var(--space-lg);box-shadow: var(--sr-depth-1)}
.radar-panel h2{font-size:var(--text-xl);margin:0 0 12px}
.radar-panel p{font-size:var(--text-sm)}
.radar-source,.radar-run,.radar-claim{padding:var(--space-md) 0;border-bottom: 1px solid var(--sr-line,var(--theme-border))}
.radar-source strong,.radar-source span,.radar-run>span{display:block;margin-bottom:8px}
.radar-source span,.radar-run>span{font-size:var(--text-xs);color: var(--sr-muted,var(--theme-text))}
.radar-source button{margin:8px 8px 0 0}
.radar label{display:block;font-size:var(--text-sm);margin:16px 0 7px}
.radar label input,.radar label textarea,.radar label select{margin-top:8px}
.radar-checkbox{display:flex!important;align-items:center;gap:var(--space-sm)}
.radar-checkbox input{width:18px;min-height:18px}
.radar-footnote{font-size:var(--text-xs)!important;color: var(--sr-muted,var(--theme-text))}
.radar-status{padding:var(--space-md) var(--space-md);border-radius: 12px;background: var(--radar-subtle);margin:22px 0;overflow-wrap:anywhere}
.radar-status.error{background: var(--theme-surface);color: var(--theme-danger)}
.radar pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:var(--text-xs)}
.radar-claim-page{max-width:820px;margin-top:50px}
.radar-claim-page .radar-panel{padding:var(--space-xl)}
.radar-provider-attribution{font-size:var(--text-lg)!important;font-weight:700;color: var(--theme-text)}
.radar-marker{width:22px;height:22px;border: 4px solid var(--theme-border);background: var(--theme-success-bg);border-radius: 50%;box-shadow: 0 6px 12px var(--theme-shadow)}
.radar-marker-duplicate{background: var(--theme-warning-bg)}
#radarDecision,#radarInvitation{border: 1px solid var(--sr-line,var(--theme-border));border-radius: 24px;padding:var(--space-lg);width:min(540px,calc(100vw - 36px));background: var(--sr-surface,var(--theme-surface));color: var(--sr-text,var(--theme-success));box-shadow: 0 32px 90px var(--theme-shadow)}
dialog::backdrop{background: var(--theme-surface);backdrop-filter:blur(5px)}
.radar-dialog-close{float:right;border: 0;background: none;font-size:var(--text-xl);cursor:pointer;color: inherit}
dialog textarea{display:block;margin:12px 0 20px;background: var(--sr-surface,var(--theme-surface));color: inherit}
dialog p{font-size:var(--text-sm);line-height:1.6}
.radar :focus-visible,dialog :focus-visible{outline: 3px solid var(--theme-success);outline-offset:3px}
[data-theme=dark] .radar{--radar-accent: var(--theme-accent);--radar-surface: var(--sr-surface,var(--theme-success-bg))}
[data-theme=dark] .radar-warning{color: var(--theme-warning)}
[data-theme=dark] .radar-map{filter:brightness(.82)}
[data-theme=dark] .radar-panel,[data-theme=dark] .radar-candidate{box-shadow: 0 12px 25px var(--theme-shadow)}
[data-theme=dark] .radar-badge{filter:brightness(.9)}
@media(max-width:1100px){.radar-workspace{grid-template-columns:1.2fr 1fr}.radar-map-heading{flex-wrap:wrap}.radar-heading{align-items:flex-start;flex-direction:column}.radar-section-heading{align-items:flex-start;flex-wrap:wrap}}
@media(max-width:760px){.radar{padding:0 var(--space-md);margin-top:22px}.radar-workspace,.radar-bottom-grid,.radar-candidates{grid-template-columns:1fr}.radar-control{padding:var(--space-lg)}.radar-emblem{float:right;width:115px}.radar-map{height:280px}.radar-map-foot{flex-direction:column}.radar-filters{width:100%;flex-direction:column}.radar-candidate{padding:var(--space-md)}.radar-primary,.radar-secondary{font-size:var(--text-xs)}.radar-evidence div{grid-template-columns:1fr}.radar-claim-page .radar-panel{padding:var(--space-lg)}.radar-heading h1{letter-spacing:-.8px}}
@media(prefers-reduced-motion:reduce){.radar *{transition:none!important;animation:none!important}}
.radar .sr-only{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border: 0!important}
"""

# ============================================================
# 8. interface.css
# ============================================================
FILES["interface.css"] = r"""/* 60% canvas, 30% surfaces, 10% accents. Icons keep their glyph fonts. */
:root {
  --sr-bg: var(--theme-bg); --sr-surface: var(--theme-surface); --sr-tint: var(--theme-elevated); --sr-line: var(--theme-border);
  --sr-text: var(--theme-text); --sr-muted: var(--theme-muted); --sr-brand: var(--theme-accent); --sr-focus: var(--theme-focus);
  --sr-accent: var(--theme-accent); --sr-ink: var(--theme-danger); --sr-on-brand: var(--theme-text);
  --sr-hero: var(--theme-surface); --sr-glow: var(--theme-elevated); --sr-display:"DM Sans",system-ui,sans-serif;
  --font-main: var(--sr-display); --font-heading: var(--sr-display);
}
:root[data-theme=dark] {
  --sr-bg: var(--theme-bg); --sr-surface: var(--theme-surface); --sr-tint: var(--theme-elevated); --sr-line: var(--theme-border);
  --sr-text: var(--theme-text); --sr-muted: var(--theme-muted); --sr-brand: var(--theme-accent); --sr-focus: var(--theme-focus);
  --sr-accent: var(--theme-accent); --sr-ink: var(--theme-text); --sr-on-brand: var(--theme-danger);
  --sr-hero: var(--theme-surface); --sr-glow: var(--theme-elevated);
}
*, *::before, *::after {scrollbar-width:none}
*::-webkit-scrollbar {display:none}
.sr-dragging, .sr-dragging * {user-select:none!important;cursor:grabbing!important;scroll-behavior:auto!important}
@media(min-width:1100px){
  body .sr-sidebar{display:flex;position:fixed;inset:var(--sr-header) auto 0 0;width:var(--sr-rail);z-index:1400;box-sizing:border-box}
  body #main-content,body .sr-footer{margin-left:var(--sr-rail)}
  body .sr-menu-button{display:none}
  .sr-compact .sr-sidebar :is(a span,form span,.sr-group){position:absolute;clip-path:inset(50%);width:1px;height:1px;overflow:hidden;white-space:nowrap}
}
"""

# ============================================================
# 9. public-navigation.css
# ============================================================
FILES["public-navigation.css"] = r"""/* Public pages use the full viewport; the system rail belongs to private panels. */
html body.sr-public-site #main-content,
html body.sr-public-site .sr-footer {
  margin-inline: 0 !important;
  width: 100% !important;
  max-width: none !important;
}
html body.sr-public-site { --sr-rail: 0px; }
.sr-public-menu { display: none; }
html body.sr-public-site .sr-menu-button { display: none !important; }
@media (max-width: 1099px) {
  html body.sr-public-site .sr-menu-button { display: inline-grid !important; }
  html body.sr-public-site .sr-public-links { display: none !important; }
  html body.sr-public-site .sr-top { padding-inline: clamp(8px, 2vw, 24px); gap: 8px; }
  .sr-drawer-open body.sr-public-site .sr-public-menu {
    display: flex;
    flex-direction: column;
    position: fixed;
    inset: calc(var(--sr-header) + 8px) max(8px, env(safe-area-inset-right)) auto auto;
    width: min(420px, calc(100vw - 16px));
    max-height: calc(100dvh - var(--sr-header) - 24px);
    overflow: auto;
    padding: 12px;
    border: 1px solid var(--sr-line);
    border-radius: 20px;
    background: var(--sr-surface);
    color: var(--sr-text);
    box-shadow: 0 20px 60px var(--theme-shadow);
    z-index: 1900;
  }
  .sr-public-menu-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; padding-left: 12px; }
  .sr-public-menu a { display: flex; align-items: center; gap: 12px; min-height: 48px; padding: 10px 12px; border-radius: 12px; color: var(--sr-text); text-decoration: none; }
  .sr-public-menu a:hover, .sr-public-menu a[aria-current=page] { background: var(--sr-tint); }
  .sr-public-menu svg { flex: none; }
}
@media (max-width: 480px) {
  html body.sr-public-site .sr-logo { font-size: 20px !important; gap: 6px; letter-spacing: -.7px; }
  html body.sr-public-site .sr-mark { width: 28px; height: 28px; }
  html body.sr-public-site .sr-actions { gap: 0; }
  html body.sr-public-site .sr-favorites-link,
  html body.sr-public-site .sr-message-link,
  html body.sr-public-site .sr-signup,
  html body.sr-public-site .sr-login { display: none !important; }
}
"""

# ============================================================
# 10. layout-system.css
# ============================================================
FILES["layout-system.css"] = r"""/* Reusable page compositions. */
.layout-bento{--layout-gap:var(--space-md,1rem);display:grid;grid-template-columns:repeat(var(--layout-columns,4),minmax(0,1fr));gap:var(--layout-gap);align-items:stretch;min-width:0}
.layout-gap-sm{--layout-gap:var(--space-sm,.75rem)}.layout-gap-md{--layout-gap:var(--space-md,1rem)}.layout-gap-lg{--layout-gap:var(--space-lg,1.5rem)}
.layout-bento>[data-layout-span="2x1"]{grid-column:span 2}.layout-bento>[data-layout-span="1x2"]{grid-row:span 2}.layout-bento>[data-layout-span="2x2"]{grid-column:span 2;grid-row:span 2}
.layout-split{--layout-ratio:1fr 1fr;display:grid;grid-template-columns:var(--layout-ratio);align-items:stretch;min-width:0}
.layout-split-40-60{--layout-ratio:2fr 3fr}.layout-split-60-40{--layout-ratio:3fr 2fr}
.layout-visual-left>[data-layout-side="visual"]{grid-column:1;grid-row:1}.layout-visual-left>[data-layout-side="content"]{grid-column:2;grid-row:1}
.layout-visual-right>[data-layout-side="visual"]{grid-column:2;grid-row:1}.layout-visual-right>[data-layout-side="content"]{grid-column:1;grid-row:1}
.layout-masonry{--layout-gap:var(--space-md,1rem);columns:var(--layout-columns,3);column-gap:var(--layout-gap);min-width:0}.layout-masonry>*{display:inline-block;vertical-align:top;width:100%;margin:0 0 var(--layout-gap);break-inside:avoid}
.layout-masonry img,.layout-masonry video{display:block;width:100%;height:auto;max-width:100%}
.layout-full-bleed{position:relative;width:100%;max-width:none;margin-inline:calc(50% - 50vw);overflow:hidden}
.layout-editorial{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:clamp(var(--space-lg,1.5rem),6vw,var(--space-2xl,4rem));align-items:center;min-width:0}
.layout-observe [data-layout-reveal]{opacity:0;transform:translateY(12px);transition:opacity .42s ease,transform .42s ease}.layout-observe [data-layout-reveal].is-visible{opacity:1;transform:none}
@media(max-width:900px){.layout-bento{grid-template-columns:repeat(2,minmax(0,1fr))}.layout-masonry{columns:2}}
@media(max-width:600px){.layout-bento{grid-template-columns:repeat(2,minmax(0,1fr))}.layout-masonry{columns:1}.layout-split,.layout-editorial{grid-template-columns:minmax(0,1fr)}}
@media(prefers-reduced-motion:reduce){.layout-observe [data-layout-reveal],.layout-observe [data-layout-reveal].is-visible{opacity:1;transform:none;transition:none}}
"""

# ============================================================
# 11. responsive-layout.css
# ============================================================
FILES["responsive-layout.css"] = r"""/* Break long content and keep app surfaces inside the viewport. */
html, body { max-width: 100%; }
body { overflow-x: clip; }
:where(.row, .grid, .toolbar, .form-row, .stats-grid) { min-width: 0; }
:where(.row, .toolbar, .form-row) { flex-wrap: wrap; }
:where(.grid, .stats-grid) { grid-template-columns: repeat(auto-fit, minmax(min(100%, 15rem), 1fr)); }
:where(pre, code, .text-break) { overflow-wrap: anywhere; }
:where(.table-responsive, .table-container, .table-wrapper) { display: block; overflow-x: auto; }
body :is(.table-responsive, .table-container, .table-wrapper, .mgr-table) { min-width: 0; max-width: 100%; overscroll-behavior-inline: contain; }
body.sr-private > #main-content {
  width: auto;
  max-width: none;
  min-width: 0;
  align-self: stretch;
  margin-inline: 0;
}
@media (min-width: 1100px) {
  body.sr-private > #main-content { margin-left: var(--sr-rail); }
}
body :is(form, fieldset, .sr-filter-fields, .market-form, .profile-form) { min-inline-size: 0; }
body form > *, body .sr-filter-fields > * { min-width: 0; }
body :is(input, select, textarea) { min-width: 0; max-width: 100%; box-sizing: border-box; }
body :is(.mgr, .market-shell, .admin-container, .owner-content, .catalog-workspace) { min-width: 0; max-width: 100%; }
body :is(.pager, .pagination, .form-actions, .admin-header, .um-toolbar) { flex-wrap: wrap; }
body :is(.stat-card, .stat-label, .market-offer, .market-panel) { min-width: 0; overflow-wrap: anywhere; }
body .sr-map-dialog { position:fixed; inset:0; margin:auto; box-sizing:border-box; width:calc(100% - 24px); max-width:960px; max-height:calc(100vh - 24px); max-height:calc(100dvh - 24px); padding:16px; overflow:auto; overscroll-behavior:contain; border:1px solid var(--sr-border); border-radius:20px; background:var(--sr-surface); color:var(--theme-text); }
body .sr-map-dialog[open] { display:flex; flex-wrap:wrap; gap:12px; }
body .sr-map-dialog > button { min-height:44px; max-width:100%; padding:0 16px; border:1px solid #d6e0e5; border-radius:12px; background:#fff; color:#344650; font-family:inherit; font-size:14px; font-weight:600; line-height:1.2; white-space:normal; box-shadow:0 2px 7px rgba(29,48,58,.08); cursor:pointer; }
body .sr-map-dialog #main-map { position:absolute; inset:0; display:block; width:100%; height:100%; min-width:0; overflow:hidden; border-radius:inherit; background:#e7eef1; }
@media(max-width:479px) {
  body .stats-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  body .pager .page-size { max-width: 100%; }
}
@media (max-width: 767px) {
  body :is(input, select, textarea) { font-size: 16px !important; }
}
@media (max-width: 639px) {
  :where(.dashboard-grid, .content-grid, .two-column, .split-layout) { grid-template-columns: minmax(0, 1fr) !important; }
}
html[data-theme="dark"] body .sr-map-dialog {
  border-color:#354650; background:#111a20; color:#f0f6f8;
  box-shadow:0 28px 80px rgba(0,0,0,.6);
}
html[data-theme="dark"] body .sr-map-dialog > button:not(:nth-of-type(2)) {
  border-color:#435660; background:#25343c; color:#f3f7f8;
}
html[data-theme="dark"] body .sr-map-dialog > button:not(:nth-of-type(2)):hover { background:#30434d; }
html[data-theme="dark"] body .sr-map-dialog > button:nth-of-type(2) {
  border-color:#5be0d5; background:#5be0d5; color:#092b2e;
}
html[data-theme="dark"] body .sr-map-dialog > button:nth-of-type(2):hover { background:#7cebe2; }
"""

# ============================================================
# 12. adaptive-experience.css
# ============================================================
FILES["adaptive-experience.css"] = r"""/* Footer definitivo SmartResto */
body footer.sr-footer.sr-unified-footer {
    display: block !important;
    position: relative !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 34px 24px 16px !important;
    box-sizing: border-box !important;
    background: var(--sr-surface, var(--theme-surface)) !important;
    color: var(--theme-text);
    border-top: 1px solid var(--sr-line);
}
body footer.sr-unified-footer *,
body footer.sr-unified-footer *::before,
body footer.sr-unified-footer *::after { box-sizing: border-box !important; }
@media (min-width: 768px) {
    body.sr-discover footer.sr-unified-footer {
        margin-left: var(--sr-rail, 250px) !important;
        width: calc(100% - var(--sr-rail, 250px)) !important;
    }
    body.sr-auth footer.sr-unified-footer { margin-left: 0 !important; width: 100% !important; }
}
body footer.sr-unified-footer > .sr-footer-grid {
    display: grid !important;
    width: 100% !important;
    max-width: 1180px !important;
    margin: 0 auto !important;
    padding: 0 !important;
    grid-template-columns: minmax(0, 1.15fr) repeat(3, minmax(0, 1fr)) !important;
    align-items: start !important;
    justify-content: center !important;
    align-content: start !important;
    column-gap: 30px !important;
    row-gap: 20px !important;
}
body footer.sr-unified-footer .sr-footer-grid > * { min-width: 0 !important; max-width: 100% !important; }
body footer.sr-unified-footer .sr-footer-brand { display: flex !important; flex-direction: column !important; align-items: flex-start !important; justify-content: flex-start !important; width: 100% !important; gap: 7px !important; margin: 0 !important; padding: 0 !important; text-align: left !important; }
body footer.sr-unified-footer .sr-logo { display: inline-block !important; width: fit-content; max-width: 100%; margin: 0 0 5px !important; padding: 0 !important; color: var(--theme-accent) !important; font-size: 27px !important; font-weight: 800 !important; line-height: 1.2 !important; text-decoration: none !important; }
body footer.sr-unified-footer .sr-footer-brand p { max-width: 260px !important; margin: 0 !important; padding: 0 !important; font-size: 13px !important; line-height: 1.5 !important; text-align: left !important; }
body footer.sr-unified-footer .sr-footer-brand > a:not(.sr-logo) { display: block !important; margin: 0 !important; padding: 0 !important; font-size: 13px !important; line-height: 1.5 !important; text-align: left !important; }
body footer.sr-unified-footer .sr-footer-grid > nav { display: flex !important; flex-direction: column !important; align-items: flex-start !important; justify-content: flex-start !important; align-content: flex-start !important; width: 100% !important; height: auto !important; min-height: 0 !important; gap: 8px !important; margin: 0 !important; padding: 0 !important; text-align: left !important; }
body footer.sr-unified-footer .sr-footer-grid > nav strong { display: block !important; width: auto !important; height: auto !important; min-height: 0 !important; margin: 0 0 5px !important; padding: 0 !important; font-size: 14px !important; font-weight: 750 !important; line-height: 1.4 !important; text-align: left !important; }
body footer.sr-unified-footer .sr-footer-grid > nav a { display: block !important; position: static !important; width: fit-content !important; max-width: 100% !important; height: auto !important; min-height: 0 !important; margin: 0 !important; padding: 2px 0 !important; font-size: 13px !important; font-weight: 400 !important; line-height: 1.45 !important; text-align: left !important; text-decoration: none !important; overflow-wrap: anywhere !important; word-break: normal !important; transform: none !important; transition: color .2s ease; }
body footer.sr-unified-footer .sr-footer-grid > nav a + a { margin-top: 0 !important; }
body footer.sr-unified-footer .sr-footer-grid > nav > * { flex: 0 0 auto !important; }
body footer.sr-unified-footer a:hover { color: var(--theme-accent) !important; }
body footer.sr-unified-footer .sr-socials { display: flex !important; flex-direction: row !important; flex-wrap: wrap !important; justify-content: flex-start !important; align-items: center !important; width: 100% !important; gap: 8px 12px !important; margin: 7px 0 0 !important; padding: 0 !important; }
body footer.sr-unified-footer .sr-socials a { display: inline-block !important; width: auto !important; margin: 0 !important; padding: 0 !important; font-size: 12px !important; }
body footer.sr-unified-footer > .sr-footer-bottom { display: flex !important; width: 100% !important; max-width: 1180px !important; margin: 24px auto 0 !important; padding: 12px 0 0 !important; flex-direction: row !important; flex-wrap: wrap !important; justify-content: center !important; align-items: center !important; gap: 6px 18px !important; border-top: 1px solid var(--sr-line); text-align: center !important; color: var(--theme-muted); }
body footer.sr-unified-footer .sr-footer-bottom span { display: block !important; width: auto !important; height: auto !important; margin: 0 !important; padding: 0 !important; font-size: 11px !important; line-height: 1.5 !important; text-align: center !important; overflow-wrap: anywhere; }
@media (min-width: 1101px) and (max-width: 1199px) {
    body footer.sr-unified-footer > .sr-footer-grid { max-width: 900px !important; grid-template-columns: repeat(2, minmax(0, 1fr)) !important; column-gap: 35px !important; row-gap: 20px !important; }
    body footer.sr-unified-footer .sr-footer-brand { grid-column: 1 / -1; align-items: center !important; text-align: center !important; }
    body footer.sr-unified-footer .sr-footer-brand p, body footer.sr-unified-footer .sr-footer-brand > a:not(.sr-logo) { text-align: center !important; }
    body footer.sr-unified-footer .sr-footer-grid > nav { align-items: center !important; text-align: center !important; }
    body footer.sr-unified-footer .sr-footer-grid > nav strong, body footer.sr-unified-footer .sr-footer-grid > nav a { text-align: center !important; }
    body footer.sr-unified-footer nav[aria-label="Ayuda y transparencia"] { grid-column: 1 / -1; max-width: 380px !important; margin-inline: auto !important; }
}
@media (min-width: 701px) and (max-width: 1100px) {
    body footer.sr-unified-footer { padding: 27px 22px 16px !important; }
    body footer.sr-unified-footer > .sr-footer-grid { max-width: 680px !important; grid-template-columns: repeat(2, minmax(0, 1fr)) !important; column-gap: 28px !important; row-gap: 18px !important; }
    body footer.sr-unified-footer .sr-footer-brand { grid-column: 1 / -1; align-items: center !important; text-align: center !important; gap: 5px !important; }
    body footer.sr-unified-footer .sr-logo { font-size: 24px !important; }
    body footer.sr-unified-footer .sr-footer-brand p, body footer.sr-unified-footer .sr-footer-brand > a:not(.sr-logo) { text-align: center !important; }
    body footer.sr-unified-footer .sr-footer-grid > nav { align-items: center !important; justify-content: flex-start !important; gap: 7px !important; text-align: center !important; }
    body footer.sr-unified-footer .sr-footer-grid > nav strong, body footer.sr-unified-footer .sr-footer-grid > nav a { text-align: center !important; }
    body footer.sr-unified-footer nav[aria-label="Ayuda y transparencia"] { grid-column: 1 / -1; width: 100% !important; max-width: 380px !important; margin: 0 auto !important; }
    body footer.sr-unified-footer > .sr-footer-bottom { max-width: 680px !important; margin-top: 19px !important; }
}
@media (min-width: 521px) and (max-width: 700px) {
    body footer.sr-unified-footer { padding: 24px 18px 15px !important; }
    body footer.sr-unified-footer > .sr-footer-grid { max-width: 540px !important; column-gap: 18px !important; row-gap: 16px !important; }
    body footer.sr-unified-footer .sr-footer-grid > nav { gap: 6px !important; }
    body footer.sr-unified-footer .sr-footer-grid > nav a { font-size: 12px !important; }
}
@media (max-width: 520px) {
    body footer.sr-footer.sr-unified-footer { padding: 25px 16px calc(17px + env(safe-area-inset-bottom)) !important; }
    body footer.sr-unified-footer > .sr-footer-grid { display: grid !important; width: 100% !important; max-width: 390px !important; grid-template-columns: minmax(0, 1fr) !important; gap: 18px !important; margin-inline: auto !important; }
    body footer.sr-unified-footer .sr-footer-brand { grid-column: 1 / -1; align-items: center !important; text-align: center !important; }
    body footer.sr-unified-footer .sr-logo { font-size: 23px !important; }
    body footer.sr-unified-footer .sr-footer-brand p, body footer.sr-unified-footer .sr-footer-brand > a:not(.sr-logo) { text-align: center !important; }
    body footer.sr-unified-footer .sr-footer-grid > nav { grid-column: 1 / -1; align-items: center !important; justify-content: flex-start !important; gap: 7px !important; text-align: center !important; }
    body footer.sr-unified-footer .sr-footer-grid > nav strong, body footer.sr-unified-footer .sr-footer-grid > nav a { text-align: center !important; }
    body footer.sr-unified-footer .sr-footer-grid > nav a { font-size: 13px !important; }
    body footer.sr-unified-footer > .sr-footer-bottom { max-width: 390px !important; flex-direction: column !important; margin-top: 19px !important; padding-top: 12px !important; gap: 5px !important; }
    body footer.sr-unified-footer .sr-footer-bottom span { width: 100% !important; font-size: 11px !important; }
}
@media (max-width: 380px) {
    body footer.sr-footer.sr-unified-footer { padding-inline: 12px !important; }
    body footer.sr-unified-footer > .sr-footer-grid { gap: 16px !important; }
    body footer.sr-unified-footer .sr-logo { font-size: 21px !important; }
    body footer.sr-unified-footer .sr-footer-brand p, body footer.sr-unified-footer .sr-footer-brand > a:not(.sr-logo) { font-size: 12px !important; }
    body footer.sr-unified-footer .sr-footer-grid > nav { gap: 6px !important; }
    body footer.sr-unified-footer .sr-footer-grid > nav a { font-size: 12px !important; }
    body footer.sr-unified-footer .sr-footer-bottom span { font-size: 10px !important; }
}
@media (max-width: 320px) {
    body footer.sr-footer.sr-unified-footer { padding-inline: 10px !important; }
    body footer.sr-unified-footer .sr-footer-grid { gap: 14px !important; }
    body footer.sr-unified-footer .sr-footer-grid > nav strong { font-size: 12px !important; }
    body footer.sr-unified-footer .sr-footer-grid > nav a { font-size: 11px !important; }
}
@media (prefers-reduced-motion: reduce) {
    body footer.sr-unified-footer a { transition: none !important; }
}
"""

# ============================================================
# 13. premium-system.css (base mínima, faltante)
# ============================================================
FILES["premium-system.css"] = r"""/* Sistema premium 3D soft. Sombras multicapa y bordes suaves. */
:root {
  --premium-shadow-1: 0 1px 2px rgb(var(--theme-shadow-rgb) / .04), 0 2px 4px rgb(var(--theme-shadow-rgb) / .04);
  --premium-shadow-2: 0 4px 8px rgb(var(--theme-shadow-rgb) / .06), 0 8px 16px rgb(var(--theme-shadow-rgb) / .06);
  --premium-shadow-3: 0 8px 16px rgb(var(--theme-shadow-rgb) / .08), 0 16px 32px rgb(var(--theme-shadow-rgb) / .08);
  --premium-shadow-float: 0 12px 24px rgb(var(--theme-shadow-rgb) / .10), 0 24px 48px rgb(var(--theme-shadow-rgb) / .10);
  --premium-radius-sm: 10px;
  --premium-radius-md: 16px;
  --premium-radius-lg: 24px;
}
.premium-card {
  background: var(--theme-surface);
  border: 1px solid var(--theme-border);
  border-radius: var(--premium-radius-md);
  box-shadow: var(--premium-shadow-2);
  transition: transform .2s ease, box-shadow .2s ease;
}
.premium-card:hover { transform: translateY(-2px); box-shadow: var(--premium-shadow-3); }
"""

# ============================================================
# 14. theme-components.css
# ============================================================
FILES["theme-components.css"] = r"""/* Componentes con tokens del tema. */
.theme-card { background: var(--theme-surface); color: var(--theme-text); border: 1px solid var(--theme-border); border-radius: 12px; padding: 16px; }
.theme-btn { display: inline-flex; align-items: center; gap: 8px; padding: 8px 16px; border-radius: 8px; font-weight: 600; text-decoration: none; cursor: pointer; border: 0; }
.theme-btn-primary { background: var(--theme-accent-bg); color: var(--theme-text); }
.theme-btn-secondary { background: var(--theme-elevated); color: var(--theme-text); }
.theme-badge { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 600; background: var(--theme-elevated); color: var(--theme-text); }
.theme-badge-success { background: var(--theme-success-bg); color: var(--theme-success); }
.theme-badge-warning { background: var(--theme-warning-bg); color: var(--theme-warning); }
.theme-badge-danger { background: var(--theme-danger-bg); color: var(--theme-danger); }
"""

# ============================================================
# 15. internal-workspace.css
# ============================================================
FILES["internal-workspace.css"] = r"""/* Presentation layer: authenticated internal shell only. */
@layer visualContract {
  body.sr-workspace { font-size: 13px !important; }
  body.sr-workspace :is(h1,h1 span,h1 i,h1 em,h1 strong) { font-size: 22px !important; line-height: 1.35 !important; letter-spacing: -.02em; }
  body.sr-workspace :is(h2,h3) { font-size: 14px !important; line-height: 1.5 !important; }
  body.sr-workspace :is(p,label,input,select,textarea,button) { font-size: 13px !important; }
}
body.sr-workspace {
  --workspace-gap: 16px;
  --workspace-radius: 8px;
  --sr-header: 54px;
  --sr-rail: 232px;
  font-variant-numeric: tabular-nums;
}
.sr-workspace #main-content { min-width: 0; padding: 24px 32px; background: var(--theme-bg); }
.sr-workspace #main-content > :is(section,div,header,main) { min-width: 0; max-width: 1280px; margin-inline: auto; }
.sr-workspace .sr-workspace-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 0 0 14px; margin-bottom: 24px; border: 0; border-bottom: 1px solid var(--theme-border); }
.sr-workspace .sr-workspace-crumbs { display: flex; flex-wrap: wrap; gap: 6px; font-size: 12px; color: var(--theme-muted); }
.sr-workspace .sr-workspace-crumbs strong { font-weight: 500; color: var(--theme-text); }
.sr-workspace .sr-workspace-kicker { font-size: 11px; letter-spacing: .06em; font-weight: 500; color: var(--theme-muted); margin: 6px 0 0; }
.sr-workspace .sr-workspace-tools { display: flex; flex-wrap: wrap; gap: 8px; }
.sr-workspace .sr-workspace-tools a { padding: 6px 10px; border: 1px solid var(--theme-border); border-radius: 6px; font-size: 12px; color: var(--theme-text); text-decoration: none; }
.sr-workspace :is(.card,.menu-section,.menu-controls,.dish-item,.review-dish-card,.intro-review,.empty-state,.sr-info,.owner-dialog,.owner-toast,.market-note,.market-map,.sr-note,.sr-plan,.sr-table,.copilot-preview,.intelligence-scope,.restaurant-card,.market-card,.bs-preview-card,.catalog-product-card,.catalog-draft-card,.catalog-empty) { border: 1px solid var(--theme-border); border-radius: 8px; background-color: var(--theme-surface); box-shadow: none !important; }
.sr-workspace :is(.card,.menu-section,.menu-controls,.intro-review,.empty-state,.sr-info,.owner-dialog,.copilot-preview,.intelligence-scope,.catalog-empty) { padding: 16px 20px; }
@media (min-width:1100px) {
  .sr-compact body.sr-private.sr-workspace .sr-sidebar { width: 232px !important; padding: 12px; }
  .sr-compact body.sr-private.sr-workspace #main-content { margin-left: 232px !important; }
}
@media (max-width:1099px) {
  .sr-workspace #main-content { margin-left: 0 !important; padding: 24px; }
}
@media (max-width:699px) {
  .sr-workspace #main-content { padding: 16px; }
  .sr-workspace .sr-workspace-header { align-items: flex-start; flex-direction: column; gap: 12px; }
}
"""

# ============================================================
# 16. admin-precision.css
# ============================================================
FILES["admin-precision.css"] = r"""/* Final ADMIN layer. */
.sr-admin-precision { font-variant-numeric: tabular-nums; }
.sr-admin-precision #main-content { min-width: 0; }
.sr-admin-precision #main-content > * { min-width: 0; }
.sr-admin-precision :is(.admin-container,.cat-admin,.sr-info) { width: 100%; max-width: 1280px; margin: 0 auto; padding: 0; background: transparent; }
.sr-admin-precision :is(.admin-header,.cat-head,.radar-section-heading) { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.sr-admin-precision :is(.admin-header,.cat-head) { margin: 0 0 20px; padding: 0 0 16px; border-bottom: 1px solid var(--theme-border); }
.sr-admin-precision :is(.stats-grid,.charts-grid,.mgr-grid,.radar-bottom-grid,.market-grid,.moderation-grid) { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 16px; }
.sr-admin-precision :is(.chart-card,.recent-activity,.cat-form,.ai-import,.um-modal,.card,.site-settings-form,.radar-control,.radar-territory,.radar-inbox,.moderation-card,.review-card,.moderation-section) { background: var(--theme-surface) !important; border: 1px solid var(--theme-border) !important; border-radius: 8px !important; padding: 16px 20px; min-width: 0; }
.sr-admin-precision :is(.table-container,.cat-table-wrap,.mgr-table,.mgr-chart-values,.admin-scroll) { max-width: 100%; overflow-x: auto; overscroll-behavior-inline: contain; scrollbar-gutter: stable; }
.sr-admin-precision table { min-width: 580px; }
.sr-admin-precision td { overflow-wrap: anywhere; max-width: 340px; vertical-align: middle; }
.sr-admin-precision :is(.admin-filters,.um-toolbar,.cat-grid,.form-row,.site-settings-form,.radar-filters) { display: grid; grid-template-columns: repeat(auto-fit,minmax(min(100%,240px),1fr)); gap: 16px; min-width: 0; }
.sr-admin-precision :is(.form-group,.um-field,.mgr-settings label,.site-settings-form label) { display: grid; gap: 6px; min-width: 0; }
.sr-admin-precision :is(.service-mode-options,.radar-workspace) { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 12px; }
.sr-admin-precision :is(.form-actions,.radar-candidate-actions,.header-right,.um-stats,.time-group) { display: flex; flex-wrap: wrap; gap: 8px; min-width: 0; }
@media (max-width: 900px) {
  .sr-admin-precision :is(.radar-workspace,.admin-form .form-section) { grid-template-columns: minmax(0,1fr); }
}
@media (max-width: 600px) {
  .sr-admin-precision :is(.charts-grid,.mgr-grid,.mgr-dashboard-charts,.radar-candidates,.radar-bottom-grid,.market-grid,.moderation-grid,.service-mode-options) { grid-template-columns: minmax(0,1fr); }
  .sr-admin-precision :is(.chart-card,.cat-form,.ai-import,.site-settings-form,.radar-control,.radar-inbox) { padding: 16px; }
}
@media (prefers-reduced-motion: reduce) {
  .sr-admin-precision *, .sr-admin-precision *::before, .sr-admin-precision *::after { animation: none !important; transition: none !important; }
}
"""

# ============================================================
# 17. saas-private.css
# ============================================================
FILES["saas-private.css"] = r"""/* Loaded last, exclusively for authenticated internal views. */
.sr-saas-private .private-account { position: relative; }
.sr-saas-private .private-account-menu { position: absolute; right: 0; top: calc(100% + 8px); width: 224px; padding: 6px; border: 1px solid var(--theme-border); background: var(--theme-surface); border-radius: 8px; z-index: 110; }
.sr-saas-private .private-account-menu a { display: block; padding: 10px; color: var(--theme-text); text-decoration: none; border-radius: 6px; }
.sr-saas-private .private-account-menu a:hover { background: var(--theme-elevated); }
.sr-saas-private .sr-header { height: 54px; border-bottom: 1px solid var(--theme-border); background: var(--theme-surface); z-index: 100; }
.sr-saas-private .sr-menu-button { display: inline-flex !important; }
.sr-saas-private .sr-sidebar { position: fixed; border-right: 1px solid var(--theme-border); z-index: 102; overflow-y: auto; overflow-x: hidden; }
.sr-saas-private .sr-top .theme-toggle { width: auto; white-space: nowrap; }
.sr-saas-private .sr-favorites-link { display: none; }
@media(min-width:1100px) {
  .sr-saas-private .sr-sidebar .sr-collapse { display: inline-flex !important; }
  .sr-compact .sr-saas-private .sr-sidebar { width: 64px !important; padding: 8px; }
  .sr-compact .sr-saas-private #main-content { margin-left: 64px !important; }
}
@media(max-width:1099px) {
  .sr-drawer-open .sr-saas-private .sr-sidebar { width: min(280px,85vw) !important; transform: none !important; top: 0 !important; bottom: 0; }
  .sr-drawer-open .sr-saas-private .sr-backdrop { display: block; position: fixed; inset: 0; z-index: 101; background: var(--theme-bg); opacity: .8; }
}
@media(max-width:699px) {
  .sr-saas-private .sr-top [data-theme-label], .sr-saas-private .saas-context { display: none; }
}
body.sr-saas-private {
  --sr-header: 54px; --sr-rail: 232px; --workspace-radius: 8px;
  --font-main: 'Manrope', system-ui, sans-serif;
  --font-heading: var(--font-main); --sr-display: var(--font-main);
  --sr-text: var(--theme-text); --sr-gutter: 24px;
  background: var(--theme-bg); color: var(--theme-text);
  font-size: 13px; font-variant-numeric: tabular-nums;
}
.sr-saas-private :is(.sr-header,.sr-sidebar,.sr-mark,.sr-icon,.sr-account,.theme-toggle,.private-account-menu,.sr-workspace-header,.mgr-hero,.mgr-card,.mgr-metric,.stat-card,.market-panel,.catalog-panel,.catalog-metric-card,.bs-panel,.bs-preview-card,.bs-action-card,.sr-service-card,.sr-table-card,.radar-panel,.radar-candidate,.radar-empty,.profile-sidebar,.profile-form-container,.saas-panel,.card,.chart-card,.recent-activity,.admin-filters,.admin-form,.um-modal,.owner-dialog,.owner-toast,.restaurant-card,.dish-item,.review-dish-card,.m-card,.m-section,.m-stat,.m-toolbar,.m-row,.m-status-note,button,input,select,textarea) {
  box-shadow: none !important; text-shadow: none !important; backdrop-filter: none !important;
}
.sr-saas-private [hidden] { display: none !important; }
.sr-saas-private :is(h1,h2,h3) { font-family: var(--font-main); color: var(--theme-text); }
.sr-saas-private h1 { font-size: 22px !important; font-weight: 600 !important; letter-spacing: -.02em; line-height: 1.35 !important; max-width: none !important; margin: 0 0 6px; }
.sr-saas-private :is(h2,h3) { font-size: 14px !important; font-weight: 500; line-height: 1.5; }
.sr-saas-private p { font-size: 13px; color: var(--theme-muted); line-height: 1.6; }
.sr-saas-private .sr-top { height: 54px; max-width: none; padding: 0 20px; gap: 16px; }
.sr-saas-private .sr-logo { font-size: 15px; font-weight: 600; letter-spacing: -.02em; min-height: 32px; }
.sr-saas-private .sr-mark { width: 28px; height: 28px; border: 1px solid var(--theme-border); border-radius: 6px; background: var(--theme-elevated); }
.sr-saas-private .saas-context { padding-left: 16px; border-left: 1px solid var(--theme-border); color: var(--theme-text); text-decoration: none; }
.sr-saas-private .saas-global-links { display: flex; gap: 20px; margin-left: auto; }
.sr-saas-private .saas-global-links a { color: var(--theme-muted); text-decoration: none; }
.sr-saas-private .sr-actions { margin-left: 0; }
.sr-saas-private :is(.sr-icon,.sr-account) { min-height: 32px; min-width: 32px; width: 32px; height: 32px; border-radius: 6px; }
.sr-saas-private .sr-account { border-radius: 999px; }
.sr-saas-private .sr-sidebar { width: 232px !important; padding: 12px; background: var(--theme-surface); gap: 2px; }
.sr-saas-private .sr-sidebar :is(a,form button) { min-height: 34px; padding: 7px 10px; font-size: 13px; font-weight: 500; gap: 10px; border-radius: 6px; }
.sr-saas-private .sr-group { font-size: 11px; font-weight: 500; letter-spacing: .06em; text-transform: uppercase; margin: 20px 10px 6px; }
.sr-saas-private .sr-nav-section { border: 0; }
.sr-saas-private .sr-nav-section summary { font-size: 11px; letter-spacing: .06em; text-transform: uppercase; padding: 10px; color: var(--theme-muted); }
.sr-saas-private .sr-section-links { padding: 0; }
.sr-saas-private .saas-sidebar-footer { margin-top: auto; padding-top: 16px; border-top: 1px solid var(--theme-border); }
.sr-saas-private .sr-footer, .sr-saas-private .sr-mobile-nav { display: none !important; }
.sr-saas-private #main-content { width: auto !important; max-width: none !important; min-width: 0; padding: 24px 32px; background: var(--theme-bg); }
.sr-saas-private #main-content > :is(section,div,header) { max-width: 1280px; margin-inline: auto; }
.sr-saas-private .sr-workspace-header { border: 0; border-bottom: 1px solid var(--theme-border); border-radius: 0; padding: 0 0 14px; margin-bottom: 24px; background: transparent; }
.sr-saas-private .sr-workspace-kicker { font-size: 11px; font-weight: 500; color: var(--theme-muted); }
.sr-saas-private .sr-workspace-tools > a:not(.sr-workspace-avatar) { padding: 6px 10px; font-size: 12px; border-radius: 6px; font-weight: 500; }
.sr-saas-private :is(.mgr,.market-shell,.catalog-shell,.bs-editor-shell,.sr-service,.radar,.profile-container,.copilot-page) { width: 100% !important; max-width: 1280px !important; margin: 0 auto; padding: 0; background: transparent; border: 0; }
.sr-saas-private :is(.catalog-atmosphere,.catalog-pulse,.bs-eyebrow-dot,.mgr-metric::before,.intelligence-hero::before,.intelligence-hero::after) { display: none; }
.sr-saas-private :is(.catalog-eyebrow,.bs-eyebrow,.bs-kicker,.radar-kicker,.copilot-kicker) { font-size: 11px; letter-spacing: .06em; font-weight: 500; color: var(--theme-muted); }
.sr-saas-private :is(.mgr-card,.mgr-metric,.stat-card,.market-panel,.catalog-panel,.catalog-metric-card,.bs-panel,.bs-preview-card,.bs-action-card,.sr-service-card,.sr-table-card,.radar-panel,.radar-candidate,.radar-empty,.profile-sidebar,.profile-form-container,.saas-panel) { background: var(--theme-surface) !important; color: var(--theme-text); border: 1px solid var(--theme-border); border-radius: 8px !important; padding: 16px 20px; }
.sr-saas-private :is(.mgr-metric dd,.stat-value,.catalog-metric-card strong) { font-size: 26px; font-weight: 600; line-height: 1.4; }
.sr-saas-private :is(.mgr-filter,.market-form,.sr-service-form) { display: grid; grid-template-columns: repeat(auto-fit,minmax(min(100%,220px),1fr)); gap: 16px; align-items: end; padding: 16px 20px; margin: 0 0 20px; background: var(--theme-surface); border: 1px solid var(--theme-border); border-radius: 8px; }
.sr-saas-private label { font-size: 13px; font-weight: 500; color: var(--theme-text); }
.sr-saas-private :is(input:not([type=checkbox]):not([type=radio]):not([type=hidden]):not([type=color]),select,textarea) { min-width: 0; max-width: 100%; width: 100%; min-height: 36px; padding: 8px 12px; font-size: 13px; color: var(--theme-text); background: var(--theme-elevated); border: 1px solid var(--theme-border); border-radius: 6px; }
.sr-saas-private textarea { min-height: 80px; resize: vertical; }
.sr-saas-private :is(button,.sr-button,.catalog-button,.bs-button,.radar-primary,.mgr-hero>a) { min-height: 34px; border: 1px solid var(--theme-border); border-radius: 6px; padding: 6px 12px; font-size: 13px; }
"""

# ============================================================
# 18. copilot-wake.css
# ============================================================
FILES["copilot-wake.css"] = r"""/* Authenticated utility dock; no document flow or header space. */
#sr-controls-open { position: fixed; right: env(safe-area-inset-right, 0px); top: 45%; z-index: 1560; width: 32px; min-height: 48px; display: grid; place-items: center; padding: 4px; border: 1px solid var(--theme-border); border-right: 0; border-radius: 12px 0 0 12px; color: var(--theme-text); background: color-mix(in srgb, var(--theme-surface) 65%, transparent); cursor: pointer; touch-action: manipulation; }
.sr-drawer-open #sr-controls-open { visibility: hidden; }
#sr-controls-drawer { position: fixed; inset: calc(var(--sr-header, 70px) + env(safe-area-inset-top, 0px) + 12px) max(8px, env(safe-area-inset-right, 0px)) calc(80px + env(safe-area-inset-bottom, 0px)) auto; margin: 0; width: min(350px, calc(100vw - 16px)); max-width: calc(100vw - 16px); max-height: calc(100dvh - var(--sr-header, 70px) - 110px); height: fit-content; overflow: auto; overscroll-behavior: contain; box-sizing: border-box; padding: 20px; border: 1px solid var(--theme-border); border-radius: 16px; color: var(--theme-text); background: var(--theme-surface); font: inherit; z-index: 2000; }
#sr-controls-drawer:not([open]) { display: none; }
#sr-controls-drawer::backdrop { background: color-mix(in srgb, var(--theme-bg) 45%, transparent); }
#sr-controls-drawer .sr-controls-heading { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
#sr-controls-drawer h2 { font-size: 18px; margin: 0; }
#sr-controls-drawer h3 { font-size: 14px; margin: 0 0 12px; }
#sr-controls-drawer section { margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--theme-border); }
#sr-controls-drawer button { min-height: 44px; padding: 8px 12px; color: inherit; background: var(--theme-elevated); border: 1px solid var(--theme-border); border-radius: 8px; cursor: pointer; touch-action: manipulation; }
#sr-wake label { display: flex; align-items: center; gap: 8px; min-height: 44px; margin-bottom: 8px; }
#sr-wake input { width: 20px; height: 20px; }
#sr-wake p, #sr-audio-controls [role=status] { display: block; margin: 12px 0; font-size: 13px; }
#sr-wake small { display: block; font-size: 12px; line-height: 1.5; }
#sr-controls-drawer :focus-visible, #sr-controls-open:focus-visible { outline: 2px solid var(--theme-accent); outline-offset: 3px; }
"""

# ============================================================
# 19. auth.css
# ============================================================
FILES["auth.css"] = r"""/* SmartResto · Experiencia de autenticación 3D soft realism. */
body.sr-auth .sr-footer,
body.sr-auth .sr-sidebar,
body.sr-auth .sr-backdrop { display: none; }
body.sr-auth #main-content { margin: 0 !important; padding:0; }
body.sr-auth { background: var(--sr-bg); overflow-x: hidden; }
body.sr-auth .ai-fab,
body.sr-auth .ai-chat,
body.sr-auth #aiFab,
body.sr-auth #aiChat { display: none !important; }
body.sr-auth input::-ms-reveal, body.sr-auth input::-ms-clear { display: none; }
.ax-stage {
  --ax-ease: cubic-bezier(0.76, 0, 0.24, 1);
  --ax-dur: 820ms;
  --ax-px: 0;
  --ax-py: 0;
  position: relative;
  overflow: hidden;
  min-height: calc(100vh - var(--sr-header));
  min-height: calc(100dvh - var(--sr-header));
  background: linear-gradient(to right, var(--sr-hero) 50%, var(--sr-bg) 50%);
  perspective: 1400px;
}
.ax-forms { position: relative; z-index: 2; width: 100%; min-height: inherit; display: flex; flex-direction: column; justify-content: center; padding:clamp(var(--space-md), 4vh, var(--space-xl)) clamp(var(--space-md), 4vw, var(--space-2xl)); box-sizing: border-box; background: var(--sr-bg); transition: transform var(--ax-dur) var(--ax-ease); will-change: transform; }
.ax-panes { display: grid; position: relative; }
.ax-pane { position: relative; grid-area: 1 / 1; transition: transform var(--ax-dur) var(--ax-ease), opacity calc(var(--ax-dur) * 0.72) ease, visibility 0s linear var(--ax-dur); }
.ax-stage[data-mode="login"] .ax-pane-register,
.ax-stage[data-mode="register"] .ax-pane-login { position: absolute; inset: 0; opacity: 0; visibility: hidden; pointer-events: none; }
.ax-stage[data-mode="login"] .ax-pane-register { transform: translateX(56px) rotateY(-4deg); }
.ax-stage[data-mode="register"] .ax-pane-login { transform: translateX(-56px) rotateY(4deg); }
.ax-visual { position: absolute; inset: 0; width: 40%; height: auto; min-height: inherit; z-index: 1; transition: transform var(--ax-dur) var(--ax-ease); will-change: transform; }
.ax-flashes { margin: 0 auto 14px; width: min(100%, 460px); display: grid; gap:var(--space-sm); }
.ax-flash { margin: 0; padding:var(--space-sm) var(--space-md); border-radius: 12px; font-size:var(--text-sm); line-height: 1.4; border: 1px solid var(--sr-line); background: var(--sr-surface); color: var(--theme-text); }
.ax-flash-success { border-color: color-mix(in srgb, var(--sr-brand) 45%, var(--sr-line)); background: color-mix(in srgb, var(--theme-accent-bg) 26%, var(--sr-surface)); }
.ax-flash-error, .ax-flash-warning { border-color: color-mix(in srgb, var(--sr-brand) 60%, var(--sr-line)); background: color-mix(in srgb, var(--theme-accent-bg) 12%, var(--sr-surface)); }
.ax-card { width: min(100%, 460px); margin-inline: auto; padding:clamp(var(--space-lg), 3.4vh, var(--space-xl)) clamp(var(--space-md), 2.6vw, var(--space-xl)); border-radius: 24px; background: var(--sr-surface); border: 1px solid color-mix(in srgb, var(--sr-line) 62%, var(--sr-surface)); box-shadow: 0 1px 0 color-mix(in srgb, var(--sr-surface) 90%, transparent) inset, 0 24px 60px -34px color-mix(in srgb, var(--sr-ink) 55%, transparent), 0 6px 18px -12px color-mix(in srgb, var(--sr-ink) 30%, transparent); animation: ax-enter 700ms var(--ax-ease) both; }
@keyframes ax-enter { from { opacity: 0; transform: translateY(18px) scale(0.985); } to { opacity: 1; transform: none; } }
.ax-eyebrow { display: flex; align-items: center; gap:var(--space-sm); margin: 0 0 14px; color: var(--theme-accent); font-weight: 700; font-size:var(--text-sm); letter-spacing: 0.02em; }
.ax-mark { display: inline-grid; place-items: center; width: 28px; height: 28px; border-radius: 9px; background: var(--sr-tint); color: var(--theme-accent); font-size:var(--text-base); }
.ax-title { margin: 0 0 8px; color: var(--theme-text); font-weight: 750; letter-spacing: -0.03em; line-height: 1.1; }
.ax-subtitle { margin: 0 0 22px; color: var(--theme-muted); font-size:var(--text-base); line-height: 1.5; }
.ax-form { display: grid; gap:var(--space-md); }
.ax-field { display: grid; gap:var(--space-xs); }
.ax-label { font-size:var(--text-sm); font-weight: 650; color: var(--theme-text); }
.ax-control { position: relative; display: flex; align-items: center; background: color-mix(in srgb, var(--sr-tint) 42%, var(--sr-surface)); border: 1.5px solid var(--sr-line); border-radius: 14px; transition: border-color 220ms ease, box-shadow 220ms ease, background 220ms ease, transform 220ms ease; }
.ax-control:focus-within { border-color: var(--sr-brand); background: var(--sr-surface); box-shadow: 0 0 0 4px color-mix(in srgb, var(--sr-brand) 16%, transparent), 0 8px 20px -14px color-mix(in srgb, var(--sr-brand) 60%, transparent); transform: translateY(-1px); }
.ax-control:has(input[aria-invalid="true"]) { border-color: var(--sr-brand); }
.ax-lead { flex: none; width: 19px; height: 19px; margin-left: 14px; color: var(--theme-muted); transition: color 220ms ease, transform 220ms ease; }
.ax-control:focus-within .ax-lead { color: var(--theme-accent); transform: scale(1.08); }
body.sr-auth .ax-control input, body.sr-auth .ax-control select { width: 100%; min-width: 0; border: 0; background: transparent; color: var(--theme-text); padding:var(--space-md) var(--space-md) var(--space-md) var(--space-sm); font-size:var(--text-base); font-family: inherit; min-height: 48px; border-radius: 14px; outline: none; }
body.sr-auth .ax-control input::placeholder { color:var(--theme-text); }
.ax-control-select select { appearance: none; cursor: pointer; padding-right:var(--space-xl); }
.ax-control-select::after { content: ""; position: absolute; right: 16px; width: 9px; height: 9px; border-right: 2px solid var(--sr-muted); border-bottom: 2px solid var(--sr-muted); transform: rotate(45deg) translateY(-3px); pointer-events: none; }
.ax-otp { letter-spacing: 0.4em; font-variant-numeric: tabular-nums; }
.ax-eye { flex: none; display: grid; place-items: center; width: 40px; height: 40px; margin-right: 5px; border: 0; border-radius: 11px; background: transparent; color: var(--theme-muted); cursor: pointer; }
.ax-eye:hover { color: var(--theme-accent); background: var(--sr-tint); }
.ax-eye svg { width: 20px; height: 20px; }
.ax-eye svg[hidden] { display: none; }
.ax-hint { margin: 0; font-size:var(--text-sm); color: var(--theme-muted); line-height: 1.4; }
.ax-error { margin: 0; font-size:var(--text-sm); font-weight: 600; color: var(--theme-accent); line-height: 1.4; }
.ax-error[hidden] { display: none; }
.ax-strength { display: flex; gap:var(--space-xs); margin-top: 2px; }
.ax-strength span { height: 5px; flex: 1; border-radius: 4px; background: var(--sr-tint); }
.ax-totp { border: 1px dashed var(--sr-line); border-radius: 14px; padding:var(--space-xs) var(--space-md); background: color-mix(in srgb, var(--sr-tint) 30%, var(--sr-surface)); }
.ax-totp summary { display: flex; align-items: center; gap:var(--space-sm); min-height: 44px; cursor: pointer; font-size:var(--text-sm); font-weight: 600; color: var(--theme-muted); list-style: none; }
.ax-submit { position: relative; display: inline-flex; align-items: center; justify-content: center; gap:var(--space-sm); width: 100%; min-height: 50px; margin-top: 4px; padding:var(--space-md) var(--space-md); border: 0; border-radius: 15px; cursor: pointer; background: var(--theme-accent-bg); color: var(--theme-text); font-size:var(--text-base); font-weight: 700; }
.ax-submit:hover { transform: translateY(-2px); filter: brightness(1.06); }
.ax-submit:disabled { cursor: wait; filter: saturate(0.7) brightness(0.96); transform: none; }
.ax-spinner { display: none; width: 17px; height: 17px; border-radius: 50%; border: 2.5px solid color-mix(in srgb, var(--sr-on-brand) 35%, transparent); border-top-color: var(--sr-on-brand); animation: ax-spin 700ms linear infinite; }
.ax-submit.is-loading .ax-spinner { display: inline-block; }
@keyframes ax-spin { to { transform: rotate(360deg); } }
.ax-links { display: flex; justify-content: center; margin-top: 2px; }
.ax-link { font-size:var(--text-sm); font-weight: 600; color: var(--theme-accent); text-decoration: none; }
.ax-link:hover { text-decoration: underline; }
.ax-switch { margin: 20px 0 0; text-align: center; font-size:var(--text-sm); color: var(--theme-muted); }
.ax-switch a { color: var(--theme-accent); font-weight: 700; text-decoration: none; }
.ax-visual { --ax-panel-text: var(--theme-text); background: radial-gradient(ellipse at 88% 8%, color-mix(in srgb, var(--sr-glow) 75%, transparent), transparent 55%), radial-gradient(ellipse at 12% 96%, color-mix(in srgb, var(--sr-brand) 42%, transparent), transparent 52%), var(--sr-hero); color: var(--theme-text); overflow: hidden; display: flex; flex-direction: column; justify-content: flex-end; }
.ax-visual::after { content: ""; position: absolute; inset: 0; pointer-events: none; background: linear-gradient(118deg, transparent 30%, color-mix(in srgb, var(--theme-accent-bg) 14%, transparent) 38%, transparent 48%); }
.ax-food-host { position: absolute; inset: 0; width: 100%; min-height: 100%; overflow: hidden; isolation: isolate; background: radial-gradient(ellipse at 50% 48%, color-mix(in srgb, var(--sr-glow) 30%, transparent), transparent 58%), radial-gradient(ellipse at 42% 100%, color-mix(in srgb, var(--sr-brand) 34%, transparent), transparent 55%), linear-gradient(145deg, var(--sr-hero), var(--sr-bg)); }
.ax-food-canvas { position: absolute; inset: 0; z-index: 1; display: grid; place-items: center; min-width: 0; overflow: hidden; pointer-events: none; }
.ax-food-canvas img[data-scene-fallback] { position: relative; z-index: 1; display: block; width: min(72%, 460px); max-height: 62vh; aspect-ratio: 1; object-fit: cover; object-position: center; border: 1px solid color-mix(in srgb, var(--sr-accent) 24%, transparent); border-radius: 50%; box-shadow: 0 34px 80px -30px color-mix(in srgb, var(--sr-ink) 78%, transparent); transform: translateY(3vh); }
.ax-food-canvas canvas { position: absolute; inset: 0; z-index: 2; display: block; width: 100% !important; height: 100% !important; opacity: 0; pointer-events: none; transition: opacity 420ms ease; }
.ax-food-host[data-scene-state="ready"] .ax-food-canvas canvas { opacity: 1; }
.ax-food-host[data-scene-state="ready"] .ax-food-canvas img[data-scene-fallback] { opacity: 0; }
.ax-food-caption { position: absolute; z-index: 4; left: clamp(18px, 2.8vw, 38px); bottom: clamp(18px, 3vh, 30px); width: min(calc(100% - 36px), 370px); padding: 18px 20px; border: 1px solid color-mix(in srgb, var(--sr-accent) 24%, var(--sr-line)); border-radius: 20px; background: color-mix(in srgb, var(--sr-surface) 84%, transparent); color: var(--theme-text); backdrop-filter: blur(14px); }
.ax-food-caption h3 { margin: 0 0 6px; color: var(--theme-text); font-size: clamp(19px, 1.65vw, 24px); font-weight: 750; line-height: 1.15; }
.ax-food-caption p { margin: 0; color: var(--theme-muted); font-size: 13px; line-height: 1.45; }
.ax-stage[data-mode="login"] .ax-promo[data-promo="register"],
.ax-stage[data-mode="register"] .ax-promo[data-promo="login"] { opacity: 0; transform: translateY(14px); pointer-events: none; }
.ax-chip { position: absolute; display: flex; align-items: center; gap:var(--space-sm); padding:var(--space-sm) var(--space-md); border-radius: 16px; background: color-mix(in srgb, var(--sr-hero) 55%, transparent); border: 1px solid color-mix(in srgb, var(--sr-accent) 26%, transparent); backdrop-filter: blur(12px); color: var(--theme-text); }
.ax-chip strong { display: block; font-size:var(--text-sm); font-weight: 700; line-height: 1.25; }
.ax-chip small { display: block; font-size:var(--text-xs); opacity: .78; line-height: 1.3; }
@media (max-width: 1099px) {
  .ax-chip-flavors, .ax-garnish-citrus { display: none; }
}
@media (max-width: 899px) {
  body.sr-auth .ax-stage { display: flex !important; flex-direction: column !important; perspective: none !important; background: var(--sr-bg) !important; min-height: 100dvh !important; padding:0 !important; }
  body.sr-auth .ax-visual, body.sr-auth .ax-scene, body.sr-auth .ax-promos, body.sr-auth .ax-food-host, body.sr-auth .ax-food-canvas { display: none !important; }
  body.sr-auth .ax-forms { width: 100% !important; transform: none !important; min-height: 0 !important; padding:var(--space-lg) var(--space-md) var(--space-xl) !important; order: 1 !important; }
}
@media (max-width: 480px) {
  .ax-card { padding:var(--space-lg) var(--space-md); border-radius: 19px; }
}
@media (prefers-reduced-motion: reduce) {
  .ax-stage, .ax-stage *, .ax-stage *::before, .ax-stage *::after { animation: none !important; transition: none !important; }
}
:root[data-theme="dark"] .ax-card { border-color: var(--sr-line); box-shadow: 0 24px 60px -34px color-mix(in srgb, var(--theme-shadow) 70%, transparent), 0 1px 0 color-mix(in srgb, var(--sr-surface) 60%, transparent) inset; }
:root[data-theme="dark"] .ax-control { background: color-mix(in srgb, var(--sr-tint) 55%, var(--sr-surface)); }
@layer visualContract {
  body.sr-auth .ax-title { font-size: clamp(26px, 2.6vw, 34px) !important; line-height: 1.1 !important; }
  body.sr-auth .ax-eyebrow { font-size:var(--text-sm) !important; }
  body.sr-auth .ax-subtitle { font-size:var(--text-base) !important; }
  body.sr-auth .ax-label { font-size:var(--text-sm) !important; }
  body.sr-auth .ax-hint, body.sr-auth .ax-error { font-size:var(--text-sm) !important; }
  body.sr-auth .ax-flash { font-size:var(--text-sm) !important; }
  body.sr-auth .ax-switch, body.sr-auth .ax-link { font-size:var(--text-sm) !important; }
  body.sr-auth .ax-control input, body.sr-auth .ax-control select { font-size:var(--text-base) !important; }
  body.sr-auth .ax-submit { font-size:var(--text-base) !important; border-radius: 15px; }
}
.sr-auth-home-link { position: fixed; top: max(16px, env(safe-area-inset-top)); left: auto; right: max(16px, env(safe-area-inset-right)); z-index: 2000; display: inline-flex; align-items: center; gap:var(--space-sm); min-height: 44px; padding:var(--space-sm) var(--space-md); border-radius: 100px; border: 1px solid var(--sr-line); background: color-mix(in srgb, var(--sr-surface) 88%, transparent); color: var(--theme-text); font-size:var(--text-sm); font-weight: 600; text-decoration: none; backdrop-filter: blur(10px); }
.sr-auth-home-link:hover { border-color: var(--sr-brand); background: var(--sr-surface); transform: translateY(-1px); }
body.sr-auth .ax-stage { padding-top:var(--space-2xl); }
"""

# ============================================================
# 20. business-sites.css
# ============================================================
FILES["business-sites.css"] = r"""/* Business sites · portal premium 3D soft realism. No photographic assets are bundled here. */
:root { --bs-ink: var(--theme-success); --bs-muted: var(--theme-muted); --bs-paper: var(--theme-bg); --bs-card: var(--theme-surface); --bs-line: var(--theme-border); --bs-shadow: 0 24px 70px var(--theme-shadow); --bs-soft-shadow: 0 10px 30px var(--theme-shadow); --bs-radius: 22px; --bs-primary: var(--theme-accent); --bs-secondary: var(--theme-accent); --bs-display:"DM Serif Display",Georgia,serif; --bs-sans:"DM Sans",system-ui,sans-serif; }
[data-theme="dark"] { --bs-ink: var(--theme-text); --bs-muted: var(--theme-muted); --bs-paper: var(--theme-bg); --bs-card: var(--theme-surface); --bs-line: var(--theme-border); --bs-shadow: 0 24px 70px var(--theme-shadow); --bs-soft-shadow: 0 10px 30px var(--theme-shadow); }
.bs-editor-shell { width:min(1540px,calc(100% - 2 * clamp(18px,4vw,72px))); margin:0 auto; padding:clamp(var(--space-lg),5vw,var(--space-2xl)) 0 var(--space-2xl); }
.bs-editor-header { display:flex; justify-content:space-between; align-items:flex-end; gap:var(--space-lg); margin-bottom:34px; }
.bs-button,.bs-public-button { display:inline-flex; align-items:center; justify-content:center; gap:var(--space-sm); min-height:44px; border: 0; border-radius: 999px; padding:var(--space-sm) var(--space-md); font-weight:700; font-size:var(--text-sm); text-decoration:none; cursor:pointer; }
.bs-button-primary,.bs-public-button { background: var(--theme-accent-bg); color: var(--theme-text); }
.bs-panel,.bs-action-card,.bs-preview-card { border: 1px solid var(--bs-line); border-radius: var(--bs-radius); background: var(--bs-card); box-shadow: var(--bs-soft-shadow); }
.bs-panel { padding:clamp(var(--space-md),3vw,var(--space-lg)); }
.bs-public-site { --bs-display:"DM Serif Display",Georgia,serif; --bs-sans:"DM Sans",system-ui,sans-serif; margin:0; color: var(--theme-text); background: var(--theme-surface); font-family:var(--bs-sans); }
.bs-public-hero { width:min(1380px,calc(100% - 2 * clamp(20px,5vw,82px))); min-height:min(720px,calc(100vh - 100px)); margin:12px auto 0; border-radius: 30px; overflow:hidden; display:grid; grid-template-columns:1.03fr .97fr; position:relative; isolation:isolate; color: var(--theme-text); background: var(--theme-accent-bg); }
.bs-hero-copy { align-self:center; padding:clamp(var(--space-xl),7vw,var(--space-2xl)); position:relative; z-index:2; }
.bs-hero-copy h1 { max-width:9ch; font:400 clamp(58px,7.7vw,124px)/.88 var(--bs-display); letter-spacing:-.065em; margin:25px 0; }
.bs-public-button { background: var(--theme-accent-bg); color: var(--theme-success); }
@media (max-width:800px) {
  .bs-public-hero { grid-template-columns:1fr; min-height:660px; }
  .bs-hero-copy { align-self:start; padding:var(--space-2xl) var(--space-xl) var(--space-lg); }
}
"""

# ============================================================
# 21. service.css
# ============================================================
FILES["service.css"] = r"""/* Salón, carta QR, cola y fidelización. Solo tokens del tema activo. */
.sr-service{max-width:1180px;margin:0 auto;padding:1.25rem clamp(1rem,4vw,3rem) 4rem;color:var(--theme-text);font-family:var(--font-main,Arial),sans-serif}
.sr-service h1,.sr-service h2,.sr-service h3{color:var(--theme-text);line-height:1.18;margin:.2em 0}
.sr-service h1{font-size:clamp(1.9rem,4.6vw,3.1rem);letter-spacing:-.04em}
.sr-service h2{font-size:1.35rem;margin-top:1.6em}
.sr-service p{line-height:1.55;margin:.5em 0}
.sr-service a{color:var(--theme-accent);text-underline-offset:3px}
.sr-service-nav{display:flex;flex-wrap:wrap;gap:.75rem 1.2rem;align-items:center;border-bottom:1px solid var(--sr-line);padding:.6rem 0 1rem;margin-bottom:1rem}
.sr-service-nav a:first-child{font-weight:700;margin-right:auto}
.sr-service-hero{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:end;gap:1rem;margin:1rem 0 1.4rem}
.sr-chip{display:inline-flex;align-items:center;gap:.35rem;border:1px solid var(--sr-line);border-radius:999px;padding:.28rem .7rem;font-size:.8rem;font-weight:650;background:var(--sr-tint);color:var(--theme-text)}
.sr-service-grid{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr))}
.sr-service-card{border:1px solid var(--sr-line);border-radius:14px;background:var(--sr-surface);padding:1.1rem}
.sr-service-stats{display:grid;gap:.8rem;grid-template-columns:repeat(auto-fit,minmax(min(100%,150px),1fr));margin:1rem 0}
.sr-service-stats div{border-left:3px solid var(--sr-brand);padding:.7rem 1rem;background:var(--sr-tint)}
.sr-service-stats strong{display:block;font-size:1.5rem}
.sr-service-form{display:grid;gap:.85rem;grid-template-columns:repeat(auto-fit,minmax(min(100%,190px),1fr));align-items:end;margin:1rem 0}
.sr-service button{border:0;border-radius:8px;padding:.7rem 1rem;font:inherit;font-weight:650;background:var(--theme-accent-bg);color:var(--theme-text);cursor:pointer;min-height:44px}
.sr-service input:not([type=checkbox]):not([type=hidden]),.sr-service select,.sr-service textarea{border:1px solid var(--sr-muted);border-radius:8px;background:var(--sr-surface);padding:.62rem;width:100%;font:inherit;color:var(--theme-text)}
.sr-service .sr-plan{position:relative;min-height:260px;border:1px solid var(--sr-line);border-radius:14px;background:var(--sr-tint);overflow:hidden}
.sr-service .sr-plan .sr-table{position:absolute;width:96px;min-height:84px;transform:translate(-50%,-50%);border:1px solid var(--sr-line);border-radius:12px;background:var(--sr-surface);padding:.45rem;text-align:center;font-size:.78rem}
.sr-service table{width:100%;border-collapse:collapse}
.sr-service th,.sr-service td{text-align:left;padding:.55rem;border-bottom:1px solid var(--sr-line);font-size:.9rem}
@media(max-width:620px){
  .sr-service .sr-service-form{grid-template-columns:1fr}
  .sr-service-nav{font-size:.9rem}
}
"""

# ============================================================
# 22. profile-responsive.css
# ============================================================
FILES["profile-responsive.css"] = r"""/* Profile responsive. */
.profile-container { max-width: 1080px; margin: 0 auto; padding: 24px; }
.profile-header { display: flex; align-items: center; gap: 24px; flex-wrap: wrap; margin-bottom: 24px; }
.profile-content { display: grid; grid-template-columns: 280px 1fr; gap: 24px; }
@media (max-width: 900px) {
  .profile-content { grid-template-columns: 1fr; }
}
"""

# ============================================================
# 23. main.css (base mínima por si falta)
# ============================================================
FILES["main.css"] = r"""/* Main base styles. */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Text&family=Lora:wght@400;500;600&family=Manrope:wght@400;500;600;700&display=swap');
html { scroll-behavior: smooth; }
body { font-family: 'DM Sans', system-ui, -apple-system, sans-serif; -webkit-font-smoothing: antialiased; }
"""

# ============================================================
# Copiar todos
# ============================================================
def main():
    print(f"📁 Instalando CSS en: {CSS_DIR}\n")
    for name, content in FILES.items():
        path = CSS_DIR / name
        path.write_text(content, encoding="utf-8")
        size = len(content)
        print(f"✅ {name:<32} ({size:,} bytes)")
    print(f"\n🎉 {len(FILES)} archivos CSS instalados en {CSS_DIR}")

if __name__ == "__main__":
    main()