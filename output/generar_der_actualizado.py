from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "src" / "com" / "municipio" / "turnos" / "relacion_entidad_actualizada.png"

W, H = 1600, 1000
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

try:
    font_title = ImageFont.truetype("arial.ttf", 34)
    font_head = ImageFont.truetype("arial.ttf", 22)
    font = ImageFont.truetype("arial.ttf", 18)
    font_small = ImageFont.truetype("arial.ttf", 15)
except OSError:
    font_title = ImageFont.load_default()
    font_head = ImageFont.load_default()
    font = ImageFont.load_default()
    font_small = ImageFont.load_default()

CARD = "#1f2937"
HEADER = "#111827"
LINE = "#111827"
TEXT = "#f9fafb"
MUTED = "#d1d5db"
ACCENT = "#2563eb"


def draw_table(x, y, w, title, rows):
    row_h = 42
    h = 54 + row_h * len(rows)
    d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=CARD, outline="#0f172a", width=2)
    d.rounded_rectangle([x, y, x + w, y + 54], radius=10, fill=HEADER)
    d.text((x + 18, y + 16), title, fill=TEXT, font=font_head)
    cy = y + 54
    for name, typ, marker in rows:
        d.line([x, cy, x + w, cy], fill="#374151", width=1)
        mark_color = "#fbbf24" if marker == "PK" else "#60a5fa" if marker == "FK" else "#9ca3af"
        d.ellipse([x + 16, cy + 14, x + 28, cy + 26], fill=mark_color)
        text_x = x + 40
        if marker:
            d.text((x + 36, cy + 12), marker, fill=MUTED, font=font_small)
            text_x = x + 70
        d.text((text_x, cy + 11), name, fill=TEXT, font=font)
        d.text((x + w - 130, cy + 12), typ, fill=MUTED, font=font_small)
        cy += row_h
    return x, y, x + w, y + h


def connector(start, end, start_label, end_label, rel):
    sx, sy = start
    ex, ey = end
    midx = (sx + ex) // 2
    d.line([sx, sy, midx, sy, midx, ey, ex, ey], fill=LINE, width=3)
    d.text((sx + 8 if sx < ex else sx - 42, sy - 28), start_label, fill=ACCENT, font=font_head)
    d.text((ex - 42 if sx < ex else ex + 8, ey - 28), end_label, fill=ACCENT, font=font_head)
    d.text((midx + 8, min(sy, ey) + abs(sy - ey) // 2 - 12), rel, fill="#374151", font=font_small)


d.text((W // 2 - 420, 40), "Modelo Entidad-Relacion - Sistema Municipal de Turnos", fill="#111827", font=font_title)
d.text((W // 2 - 285, 86), "Cardinalidad orientada desde la entidad 1 hacia la entidad N", fill="#374151", font=font)

ciudadanos = draw_table(1050, 170, 420, "ciudadanos", [
    ("id_ciudadano", "int4", "PK"),
    ("dni", "varchar unique", ""),
    ("nombre_completo", "varchar", ""),
    ("email", "varchar", ""),
    ("telefono", "varchar", ""),
    ("mayor_65", "bool", ""),
])

servicios = draw_table(1050, 610, 420, "servicios", [
    ("id_servicio", "int4", "PK"),
    ("nombre_servicio", "varchar", ""),
    ("es_arancelado", "bool", ""),
    ("costo_base", "numeric", ""),
])

turnos = draw_table(590, 365, 410, "turnos", [
    ("id_turno", "int4", "PK"),
    ("id_ciudadano", "int4", "FK"),
    ("id_servicio", "int4", "FK"),
    ("fecha_hora", "timestamp", ""),
    ("estado", "varchar", ""),
])

pagos = draw_table(110, 350, 420, "pagos", [
    ("id_pago", "int4", "PK"),
    ("id_turno", "int4 unique", "FK"),
    ("monto_original", "numeric", ""),
    ("descuento_aplicado", "numeric", ""),
    ("monto_final", "numeric", ""),
    ("fecha_pago", "timestamp", ""),
    ("estado_pago", "varchar", ""),
])

connector((ciudadanos[0], ciudadanos[1] + 125), (turnos[2], turnos[1] + 95), "1", "N", "solicita")
connector((servicios[0], servicios[1] + 95), (turnos[2], turnos[1] + 140), "1", "N", "corresponde a")
connector((turnos[0], turnos[1] + 110), (pagos[2], pagos[1] + 90), "1", "0..1", "genera")

d.text((110, 900), "Reglas: un ciudadano puede solicitar varios turnos; un servicio puede estar en varios turnos; solo los turnos arancelados generan pago.", fill="#374151", font=font)
d.text((110, 930), "El pago ya no elimina el turno: actualiza estado_pago = Pagado y estado del turno = Pagado.", fill="#374151", font=font)

img.save(OUTPUT)
print(OUTPUT)
