"""
compose_iglesia_vs_ia.py — Compone la cover del carrusel "Iglesia vs IA":
fondo cinematografico (catedral vs servidores IA) + Papa Leo XIV cutout
a la izquierda + Diego apuntando cutout a la derecha + gradient inferior
para el texto.

Salida: fotos/iglesia_vs_ia_cover.png (1080x1350)
"""

import argparse
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps


W, H = 1080, 1350


def make_drop_shadow(card: Image.Image, blur: int = 18, alpha_max: int = 160,
                     offset: tuple[int, int] = (8, 14)) -> Image.Image:
    """Sombra natural derivada del alpha del cutout."""
    if card.mode != "RGBA":
        return None
    alpha = card.split()[-1]
    shadow_alpha = alpha.point(lambda p: min(p, alpha_max))
    shadow_alpha = shadow_alpha.filter(ImageFilter.GaussianBlur(blur))
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    shadow.putalpha(shadow_alpha)
    return shadow


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proj-dir", required=True)
    ap.add_argument("--bg", default="output/carrusel_2026-05-27_1156/_bg_00.png",
                    help="Ruta relativa al fondo cinematografico")
    ap.add_argument("--papa", default="fotos/_cutouts/Papa Leo XIV cutout.png")
    ap.add_argument("--diego", default="fotos/_cutouts/Diego apuntando v2.png")
    ap.add_argument("--output", default="fotos/_compuestas/iglesia_vs_ia_cover.png")
    args = ap.parse_args()

    proj = Path(args.proj_dir).resolve()

    # 1) Cargar fondo y oscurecer
    bg_src = proj / args.bg
    if not bg_src.exists():
        raise FileNotFoundError(f"No encuentro {bg_src}")
    bg = ImageOps.exif_transpose(Image.open(bg_src)).convert("RGBA")
    factor = max(W / bg.width, H / bg.height)
    bg = bg.resize((round(bg.width * factor), round(bg.height * factor)), Image.LANCZOS)
    x = (bg.width - W) // 2
    y = (bg.height - H) // 2
    bg = bg.crop((x, y, x + W, y + H))

    # Veil sutil para que el fondo no compita con los cutouts
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 90))
    bg.alpha_composite(veil)

    # 2) Cargar cutouts y recortar bbox
    def load_cutout(path: Path, target_h: int) -> Image.Image:
        img = ImageOps.exif_transpose(Image.open(path)).convert("RGBA")
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        target_w = max(1, round(img.width * target_h / img.height))
        return img.resize((target_w, target_h), Image.LANCZOS)

    # Cutouts en posicion media: dejan ver la catedral/servidores arriba
    # (no totalmente oscurecidos como v3), y dejan ~360px arriba para texto.
    target_h = 620
    papa = load_cutout(proj / args.papa, target_h)
    diego = load_cutout(proj / args.diego, target_h)

    # 3) Posicionar: Papa izquierda, Diego derecha
    margin = 30
    papa_x = margin
    papa_y = 380  # cutouts comienzan en y=380 → texto cabe arriba en y=60-360
    diego_x = W - diego.width - margin
    diego_y = 380

    # 4) Sombras
    papa_shadow = make_drop_shadow(papa, blur=20, alpha_max=140, offset=(8, 14))
    diego_shadow = make_drop_shadow(diego, blur=20, alpha_max=140, offset=(-8, 14))

    if papa_shadow:
        bg.alpha_composite(papa_shadow, (papa_x + 8, papa_y + 14))
    bg.alpha_composite(papa, (papa_x, papa_y))

    if diego_shadow:
        bg.alpha_composite(diego_shadow, (diego_x - 8, diego_y + 14))
    bg.alpha_composite(diego, (diego_x, diego_y))

    # 5) Gradient superior SUTIL en la franja del texto (0-380px) — apenas
    # oscurece para que el copy se lea sobre el cielo y la catedral.
    grad_col = Image.new("L", (1, H), 0)
    for yy in range(H):
        if yy < 380:
            t = 1 - (yy / 380)
            v = int(140 * (t ** 0.7))
        else:
            v = 0
        grad_col.putpixel((0, yy), v)
    grad_alpha = grad_col.resize((W, H))
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grad.putalpha(grad_alpha)
    bg.alpha_composite(grad)

    # 6) Guardar
    dst = proj / args.output
    bg.convert("RGB").save(dst, "PNG", optimize=True)
    print(f"✓ composicion guardada: {dst}")
    print(f"  Papa: {papa.size} en ({papa_x}, {papa_y})")
    print(f"  Diego: {diego.size} en ({diego_x}, {diego_y})")


if __name__ == "__main__":
    main()
