from pathlib import Path

ASSETS = Path("assets")
GEN = ASSETS / "generated"
GEN.mkdir(parents=True, exist_ok=True)


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def background_svg() -> str:
    return """<svg xmlns='http://www.w3.org/2000/svg' width='3840' height='2160' viewBox='0 0 3840 2160'>
  <defs>
    <linearGradient id='bg' x1='0' y1='0' x2='0' y2='1'>
      <stop offset='0%' stop-color='#d9f3ff'/>
      <stop offset='100%' stop-color='#00479d'/>
    </linearGradient>
  </defs>
  <rect width='3840' height='2160' fill='url(#bg)'/>
  <g fill='none' stroke='#ffffff' stroke-width='8' opacity='0.45'>
    <path d='M100 1900 Q900 1500 1700 1900'/>
    <path d='M2140 1900 Q2940 1500 3740 1900'/>
    <circle cx='450' cy='400' r='140'/>
    <circle cx='950' cy='470' r='110'/>
    <circle cx='1450' cy='420' r='90'/>
    <circle cx='3200' cy='420' r='120'/>
  </g>
</svg>"""


def bottle_svg(label: str, accent: str, level: int) -> str:
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='1400' height='2000' viewBox='0 0 1400 2000'>
  <rect x='80' y='60' width='1240' height='1880' rx='80' fill='#ffffff' fill-opacity='0.9' stroke='{accent}' stroke-width='14'/>
  <rect x='350' y='260' width='700' height='1390' rx='120' fill='#e3f6ff' stroke='#00479d' stroke-width='14'/>
  <rect x='370' y='{level}' width='660' height='{1630-level}' rx='90' fill='{accent}' fill-opacity='0.85'/>
  <ellipse cx='700' cy='240' rx='120' ry='60' fill='#00a8e8' stroke='#00479d' stroke-width='8'/>
  <text x='700' y='1780' text-anchor='middle' font-size='88' font-family='Verdana' fill='#00479d'>{label}</text>
</svg>"""


def logo_svg() -> str:
    return """<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='1200' viewBox='0 0 1200 1200'>
  <rect width='1200' height='1200' fill='#f5fbff'/>
  <circle cx='600' cy='600' r='510' fill='#e6f6ff' stroke='#00479d' stroke-width='16'/>
  <path d='M140 840 Q600 280 1060 840' fill='none' stroke='#00a8e8' stroke-width='30'/>
  <path d='M140 940 Q600 380 1060 940' fill='none' stroke='#00a8e8' stroke-width='30'/>
  <text x='600' y='600' text-anchor='middle' font-size='180' font-family='Verdana' font-weight='700' fill='#ec0f7e'>Lupita</text>
  <text x='600' y='730' text-anchor='middle' font-size='96' font-family='Verdana' font-weight='700' fill='#00479d'>Agua Purificada</text>
  <text x='600' y='830' text-anchor='middle' font-size='52' font-family='Verdana' fill='#13a86f'>Logo base para kiosko</text>
</svg>"""


if __name__ == "__main__":
    write(GEN / "fondo_kiosko_4k.svg", background_svg())
    write(GEN / "garrafon_full_hd.svg", bottle_svg("Garrafón completo", "#00a8e8", 360))
    write(GEN / "garrafon_half_hd.svg", bottle_svg("Medio garrafón", "#13a86f", 820))
    write(GEN / "garrafon_gallon_hd.svg", bottle_svg("Galón", "#ec0f7e", 1180))
    write(ASSETS / "logo_principal.svg", logo_svg())
    print("SVG assets generated")
