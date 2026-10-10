"""Genera una animación estilo Matrix a partir del calendario de contribuciones."""
import os
import random
import re
import sys
import urllib.request

USER = os.environ.get("GH_USER", "allanze1x-spec")
OUT = sys.argv[1] if len(sys.argv) > 1 else "dist/matrix-contrib.svg"

req = urllib.request.Request(
    f"https://github.com/users/{USER}/contributions",
    headers={"User-Agent": "Mozilla/5.0 matrix-grid"},
)
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")

cells = {}
for tag in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", html):
    m_id = re.search(r'id="contribution-day-component-(\d+)-(\d+)"', tag)
    m_lv = re.search(r'data-level="(\d)"', tag)
    if m_id and m_lv:
        cells[(int(m_id.group(1)), int(m_id.group(2)))] = int(m_lv.group(1))
if not cells:
    sys.exit("No se encontraron celdas de contribución")

weeks = max(c for _, c in cells) + 1
CELL, GAP, PAD = 12, 3, 14
W = PAD * 2 + weeks * (CELL + GAP) - GAP
H = PAD * 2 + 7 * (CELL + GAP) - GAP
LEVELS = ["#0A1F0A", "#0E4429", "#006D32", "#26A641", "#39D353"]
GLYPHS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎ01"
rnd = random.Random(42)

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Contribuciones en estilo Matrix">',
    "<defs>",
    '<linearGradient id="drop" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#00FF41" stop-opacity="0"/>'
    '<stop offset=".85" stop-color="#00FF41" stop-opacity=".55"/>'
    '<stop offset="1" stop-color="#D7FFD9" stop-opacity="1"/></linearGradient>',
    "</defs>",
    f'<rect width="{W}" height="{H}" rx="10" fill="#000"/>',
]

for (row, col), level in sorted(cells.items()):
    x = PAD + col * (CELL + GAP)
    y = PAD + row * (CELL + GAP)
    svg.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{LEVELS[level]}">')
    if level:
        dur = round(rnd.uniform(1.6, 4.2), 2)
        begin = round(rnd.uniform(0, 4), 2)
        svg.append(
            f'<animate attributeName="opacity" values="1;.45;1;.8;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
        )
    svg.append("</rect>")

svg.append('<g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11" text-anchor="middle">')
grid_h = 7 * (CELL + GAP)
for col in range(weeks):
    x = PAD + col * (CELL + GAP)
    dur = round(rnd.uniform(2.2, 5.5), 2)
    begin = round(rnd.uniform(-5, 0), 2)
    tail = rnd.randint(30, 70)
    svg.append(f'<g><animateTransform attributeName="transform" type="translate" from="0 {-tail - 20}" to="0 {H + 10}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>')
    svg.append(f'<rect x="{x}" y="0" width="{CELL}" height="{tail}" rx="2" fill="url(#drop)" opacity=".75"/>')
    svg.append(f'<text x="{x + CELL / 2}" y="{tail + 9}" fill="#D7FFD9">{rnd.choice(GLYPHS)}</text>')
    svg.append("</g>")
svg.append("</g></svg>")

os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(svg))
print(f"{len(cells)} celdas, {weeks} semanas -> {OUT}")
