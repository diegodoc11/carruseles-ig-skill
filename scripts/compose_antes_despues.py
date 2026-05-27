"""
compose_antes_despues.py — Cover ANTES/DESPUÉS para slide 1 del carrusel
"De hot dogs a Jarvis", layout VERTICAL stacked con transición sepia → color.

Estructura visual:
  ┌──────────────────────────────┐
  │  TEXTO SLIDE                 │  banda arriba con veil oscuro
  │                              │
  │  [Diego con hot dogs cutout] │  mitad SUPERIOR — sepia
  │   (sobre cielo+montañas+lago │  (crop superior del paisaje original)
  │    en sepia)                 │
  │                              │
  │  ~~~ gradient transición ~~~ │  sepia → color
  │                              │
  │  [Diego con BMW + paisaje]   │  mitad INFERIOR — color natural
  │   (crop inferior del paisaje │  (Diego + BMW + césped)
  │    original)                 │
  └──────────────────────────────┘

La foto base es "con el bmw de paseo.JPEG" — Diego al lado del BMW negro
con lago de fondo. La separamos en dos crops para que el cutout de hot dogs
NO se solape con la figura de Diego con BMW.
"""

import argparse
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps


W, H = 1080, 1350


def apply_sepia(im: Image.Image, intensity: float = 1.0) -> Image.Image:
    """Convierte una imagen a sepia. `intensity` 0.0-1.0 mezcla con el original."""
    rgb = im.convert("RGB")
    gray = rgb.convert("L")
    sepia_rgb = Image.merge("RGB", [
        gray.point(lambda p: min(255, int(p * 1.08))),
        gray.point(lambda p: min(255, int(p * 0.92))),
        gray.point(lambda p: min(255, int(p * 0.65))),
    ])
    sepia_rgba = sepia_rgb.convert("RGBA")
    if im.mode == "RGBA":
        sepia_rgba.putalpha(im.split()[-1])
    if intensity >= 1.0:
        return sepia_rgba
    return Image.blend(im.convert("RGBA"), sepia_rgba, intensity)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proj-dir", required=True)
    ap.add_argument("--paisaje_bmw", default="fotos/con el bmw de paseo.JPEG",
                    help="Foto Diego con BMW + paisaje (lago/montañas)")
    ap.add_argument("--hotdogs_cutout", default="fotos/_cutouts/Diego con hotdogs.png")
    ap.add_argument("--output", default="fotos/_compuestas/antes_despues_hotdogs_bmw.png")
    args = ap.parse_args()

    proj = Path(args.proj_dir).resolve()

    # ───────────────────────────────────────────────────────────────────────
    # 1) Cargar foto original Diego+BMW+paisaje (~1536x2048)
    # ───────────────────────────────────────────────────────────────────────
    paisaje = ImageOps.exif_transpose(Image.open(proj / args.paisaje_bmw)).convert("RGBA")
    pw, ph = paisaje.size
    print(f"  paisaje original: {pw}x{ph}")

    # ───────────────────────────────────────────────────────────────────────
    # 2) Crop SUPERIOR: solo cielo + montañas + lago (SIN BMW ni Diego)
    #    Aprox y=0 hasta y=ph*0.45 (mitad alta) → paisaje puro
    # ───────────────────────────────────────────────────────────────────────
    top_crop = paisaje.crop((0, 0, pw, int(ph * 0.50)))
    top_resized = top_crop.resize((W, 720), Image.LANCZOS)
    top_sepia = apply_sepia(top_resized, intensity=1.0)
    # Veil oscuro adicional sobre la sepia
    top_veil = Image.new("RGBA", (W, 720), (20, 10, 5, 90))
    top_sepia.alpha_composite(top_veil)

    # ───────────────────────────────────────────────────────────────────────
    # 3) Crop INFERIOR: Diego + BMW + césped (color natural)
    #    y=ph*0.40 hasta el final → Diego y el auto bien visibles
    # ───────────────────────────────────────────────────────────────────────
    bottom_crop = paisaje.crop((0, int(ph * 0.40), pw, ph))
    bottom_resized = bottom_crop.resize((W, 800), Image.LANCZOS)

    # ───────────────────────────────────────────────────────────────────────
    # 4) Canvas: pegar bottom primero (y=550 hasta y=1350), después top con
    #    máscara alpha que se desvanece en la zona de overlap
    # ───────────────────────────────────────────────────────────────────────
    canvas = Image.new("RGBA", (W, H), (10, 5, 5, 255))
    canvas.paste(bottom_resized, (0, H - 800))  # bottom va de y=550 a y=1350

    # Crear máscara alpha para el top: opaco arriba, se desvanece de y=540 a y=720
    top_alpha_col = Image.new("L", (1, 720), 255)
    fade_start = 520
    fade_len = 200
    for y in range(720):
        if y < fade_start:
            v = 255
        elif y < fade_start + fade_len:
            t = (y - fade_start) / fade_len
            v = int(255 * (1 - t) ** 1.2)
        else:
            v = 0
        top_alpha_col.putpixel((0, y), v)
    top_alpha_mask = top_alpha_col.resize((W, 720))

    # Aplicar la máscara al alpha del top
    top_with_mask = top_sepia.copy()
    top_with_mask.putalpha(top_alpha_mask)
    canvas.alpha_composite(top_with_mask, (0, 0))

    # ───────────────────────────────────────────────────────────────────────
    # 5) Cutout Diego con HOT DOGS (sepia) en la mitad superior, centrado.
    #    Va en y=120-540 → NO se solapa con Diego+BMW (que está y=550+)
    # ───────────────────────────────────────────────────────────────────────
    hotdogs = ImageOps.exif_transpose(Image.open(proj / args.hotdogs_cutout)).convert("RGBA")
    bbox = hotdogs.getbbox()
    if bbox:
        hotdogs = hotdogs.crop(bbox)
    # Tintar sepia (con un poco de color original conservado)
    hotdogs_sepia = apply_sepia(hotdogs, intensity=0.75)

    target_h = 440   # ocupa hasta y=560 aprox, dentro de la zona sepia
    target_w = int(hotdogs_sepia.width * target_h / hotdogs_sepia.height)
    hotdogs_sepia = hotdogs_sepia.resize((target_w, target_h), Image.LANCZOS)
    # ALINEAR A LA IZQUIERDA: Diego con BMW está a la derecha en el bottom →
    # poner Diego con hot dogs a la IZQUIERDA arriba crea diagonal visual
    # "antes → después" más limpia.
    h_x = 70
    h_y = 120
    # Sombra
    alpha = hotdogs_sepia.split()[-1]
    sh_alpha = alpha.point(lambda p: min(p, 110)).filter(ImageFilter.GaussianBlur(16))
    shadow = Image.new("RGBA", hotdogs_sepia.size, (0, 0, 0, 0))
    shadow.putalpha(sh_alpha)
    canvas.alpha_composite(shadow, (h_x + 6, h_y + 10))
    canvas.alpha_composite(hotdogs_sepia, (h_x, h_y))

    # ───────────────────────────────────────────────────────────────────────
    # 6) Veil oscuro en la BANDA SUPERIOR para que el texto del slide se lea
    # ───────────────────────────────────────────────────────────────────────
    tv_col = Image.new("L", (1, H), 0)
    for y in range(H):
        if y < 80:
            v = 200
        elif y < 240:
            t = 1 - (y - 80) / 160
            v = int(200 * (t ** 0.6))
        else:
            v = 0
        tv_col.putpixel((0, y), v)
    tv_alpha = tv_col.resize((W, H))
    tv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tv.putalpha(tv_alpha)
    canvas.alpha_composite(tv)

    # ───────────────────────────────────────────────────────────────────────
    # 7) Guardar
    # ───────────────────────────────────────────────────────────────────────
    dst = proj / args.output
    dst.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(dst, "PNG", optimize=True)
    print(f"✓ guardado: {dst}")
    print(f"  Layout vertical SIN overlap entre Diego-hot-dogs y Diego-BMW:")
    print(f"    • y=0–500   Cielo+montañas SEPIA + cutout hot dogs")
    print(f"    • y=520–720 Transición gradient sepia → color")
    print(f"    • y=550–1350 Foto original (Diego + BMW + paisaje natural)")


if __name__ == "__main__":
    main()
