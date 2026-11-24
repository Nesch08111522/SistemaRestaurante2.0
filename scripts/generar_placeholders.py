"""
Genera placeholders SVG premium para imágenes faltantes de SmartResto.
Se ven como diseños editoriales, no como imágenes rotas.
"""
from pathlib import Path

BASE = Path(__file__).parent.parent / "app" / "static" / "images"

# Paleta brand
VERDE = "#245447"
VERDE_OSCURO = "#1a3d33"
VERDE_CLARO = "#3d7a63"
DORADO = "#D8A65D"
DORADO_CLARO = "#e8c78a"
CREMA = "#f5efdc"
ARENA = "#e8dcc4"

TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
  <defs>
    <radialGradient id="bgGrad" cx="30%" cy="30%" r="80%">
      <stop offset="0%" stop-color="{bg1}"/>
      <stop offset="100%" stop-color="{bg2}"/>
    </radialGradient>
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{accent1}"/>
      <stop offset="100%" stop-color="{accent2}"/>
    </linearGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="20" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect width="800" height="600" fill="url(#bgGrad)"/>
  <circle cx="200" cy="150" r="120" fill="url(#accentGrad)" opacity="0.25" filter="url(#glow)"/>
  <circle cx="650" cy="450" r="180" fill="url(#accentGrad)" opacity="0.18" filter="url(#glow)"/>
  <ellipse cx="400" cy="300" rx="220" ry="180" fill="{overlay}" opacity="0.08"/>
  <g opacity="0.9">
    <path d="M 340 280 Q 400 200 460 280 Q 480 320 440 360 Q 400 380 360 360 Q 320 320 340 280 Z"
          fill="url(#accentGrad)" opacity="0.35"/>
    <ellipse cx="400" cy="300" rx="60" ry="40" fill="url(#accentGrad)" opacity="0.6"/>
  </g>
  <text x="400" y="520" text-anchor="middle" fill="{text}" font-family="Georgia, serif" font-size="24" opacity="0.7" font-style="italic">{label}</text>
  <text x="400" y="550" text-anchor="middle" fill="{text}" font-family="system-ui, sans-serif" font-size="13" opacity="0.45" letter-spacing="2">{sublabel}</text>
</svg>"""

PLACEHOLDERS = [
    ("auth/lomo.webp", VERDE_OSCURO, VERDE_CLARO, DORADO, DORADO_CLARO, CREMA, CREMA, "Lomo saltado", "COCINA PERUANA"),
    ("auth/ceviche.webp", "#1a4d5c", "#2d7a8a", "#D8A65D", "#e8c78a", CREMA, CREMA, "Ceviche norteño", "SABOR MARINO"),
    ("auth/dessert.webp", "#3d2a1a", "#6b4a2a", "#D8A65D", "#f5d99e", CREMA, CREMA, "Café y postre", "MOMENTO DULCE"),
    ("auth/signature.webp", "#2a4d33", "#4a7a4d", "#D8A65D", "#e8c78a", CREMA, CREMA, "Causa de autor", "COCINA DE AUTOR"),
    ("forest/food-inspiration.webp", VERDE_OSCURO, VERDE_CLARO, DORADO, DORADO_CLARO, CREMA, CREMA, "Inspiración", "SABORES DEL NORTE"),
    ("forest/marine-inspiration.webp", "#1a4d5c", "#2d7a8a", DORADO, DORADO_CLARO, CREMA, CREMA, "Del mar", "FRESCURA NORTEÑA"),
    ("forest/creole-inspiration.webp", "#4d2a1a", "#7a3a2a", DORADO, DORADO_CLARO, CREMA, CREMA, "Criollo", "SABORES DE SIEMPRE"),
    ("forest/chef-reference.webp", VERDE_OSCURO, VERDE_CLARO, DORADO, DORADO_CLARO, CREMA, CREMA, "Chef", "SMARTRESTO"),
    ("forest/shop-reference.webp", "#3d2a1a", "#6b4a2a", DORADO, DORADO_CLARO, CREMA, CREMA, "Negocio", "TU COCINA AQUÍ"),
    ("ceviche.webp", "#1a4d5c", "#2d7a8a", DORADO, DORADO_CLARO, CREMA, CREMA, "Ceviche", "COCINA PERUANA"),
    ("ceviche-small.webp", "#1a4d5c", "#2d7a8a", DORADO, DORADO_CLARO, CREMA, CREMA, "Ceviche", "COCINA PERUANA"),
]

def main():
    for path_str, bg1, bg2, acc1, acc2, overlay, text, label, sublabel in PLACEHOLDERS:
        dest = BASE / path_str.replace(".webp", ".svg").replace(".jpg", ".svg")
        dest.parent.mkdir(parents=True, exist_ok=True)
        content = TEMPLATE.format(
            bg1=bg1, bg2=bg2, accent1=acc1, accent2=acc2,
            overlay=CREMA, text=text, label=label, sublabel=sublabel,
        )
        # Si el original es .webp, generamos también un .webp "vacío" para no romper el HTML existente
        # Pero mejor renombramos en los templates a .svg. Guardamos como .svg:
        svg_dest = dest
        svg_dest.write_text(content, encoding="utf-8")
        print(f"✅ {svg_dest.relative_to(BASE.parent.parent)}")

    # Logo
    logo = BASE / "brand" / "logo.svg"
    logo.parent.mkdir(parents=True, exist_ok=True)
    logo.write_text("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <defs>
    <linearGradient id="lg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#245447"/>
      <stop offset="100%" stop-color="#3d7a63"/>
    </linearGradient>
  </defs>
  <circle cx="100" cy="100" r="90" fill="url(#lg)"/>
  <circle cx="100" cy="100" r="70" fill="none" stroke="#D8A65D" stroke-width="2" opacity="0.5"/>
  <path d="M 70 70 Q 100 50 130 70 Q 140 100 130 130 Q 100 150 70 130 Q 60 100 70 70 Z"
        fill="#D8A65D" opacity="0.8"/>
  <text x="100" y="115" text-anchor="middle" fill="#245447" font-family="Georgia, serif" font-size="42" font-weight="bold">S</text>
</svg>""", encoding="utf-8")
    print(f"✅ {logo.relative_to(BASE.parent.parent)}")

    # Citrus study
    citrus = BASE / "citrus-study.svg"
    citrus.write_text("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <g opacity="0.4">
    <circle cx="100" cy="100" r="80" fill="none" stroke="#D8A65D" stroke-width="1"/>
    <circle cx="100" cy="100" r="60" fill="none" stroke="#D8A65D" stroke-width="1"/>
    <circle cx="100" cy="100" r="40" fill="none" stroke="#D8A65D" stroke-width="1"/>
    <line x1="100" y1="20" x2="100" y2="180" stroke="#D8A65D" stroke-width="1"/>
    <line x1="20" y1="100" x2="180" y2="100" stroke="#D8A65D" stroke-width="1"/>
    <line x1="40" y1="40" x2="160" y2="160" stroke="#D8A65D" stroke-width="1"/>
    <line x1="160" y1="40" x2="40" y2="160" stroke="#D8A65D" stroke-width="1"/>
  </g>
</svg>""", encoding="utf-8")
    print(f"✅ {citrus.relative_to(BASE.parent.parent)}")

if __name__ == "__main__":
    main()