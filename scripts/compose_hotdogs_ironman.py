"""
compose_hotdogs_ironman.py — Cover slide 1 del carrusel Jarvis:
foto auténtica de Diego con el carrito de hot dogs (modo fit con padding) +
cutout de Iron Man en la esquina superior derecha (como "JARVIS observa").

Da peso visual a la palabra "JARVIS" del subtítulo sin tapar la cara de Diego
ni el carrito de salchichas.

Salida: fotos/_compuestas/hotdogs_con_ironman.png
"""

import argparse
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps


W, H = 1080, 1350


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proj-dir", required=True)
    ap.add_argument("--hotdogs", default="fotos/Diego con hotdogs.png")
    ap.add_argument("--ironman", default="fotos/_cutouts/Iron Man.png")
    ap.add_argument("--output", default="fotos/_compuestas/hotdogs_con_ironman.png")
    args = ap.parse_args()

    proj = Path(args.proj_dir).resolve()

    # ───────────────────────────────────────────────────────────────────────
    # 1) Canvas negro 1080x1350
    # ───────────────────────────────────────────────────────────────────────
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))

    # ───────────────────────────────────────────────────────────────────────
    # 2) Foto Diego con hot dogs en modo "fit" centrada
    # ───────────────────────────────────────────────────────────────────────
    hotdogs = ImageOps.exif_transpose(Image.open(proj / args.hotdogs)).convert("RGBA")
    factor = min(W / hotdogs.width, H / hotdogs.height)
    new_w = round(hotdogs.width * factor)
    new_h = round(hotdogs.height * factor)
    hotdogs_fit = hotdogs.resize((new_w, new_h), Image.LANCZOS)
    foto_x = (W - new_w) // 2
    foto_y = (H - new_h) // 2
    canvas.paste(hotdogs_fit, (foto_x, foto_y))
    print(f"  foto hot dogs: {new_w}x{new_h} en ({foto_x}, {foto_y})")

    # Darken sutil sobre la foto (mismo efecto que foto_darken=0.35 del motor)
    darken = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * 0.30)))
    canvas.alpha_composite(darken)

    # ───────────────────────────────────────────────────────────────────────
    # 3) Iron Man cutout en la ESQUINA INFERIOR DERECHA del slide.
    # IMPORTANTE: va en el PADDING NEGRO INFERIOR (debajo de la foto) para
    # NO TAPAR la cara de Diego (que está en la mitad derecha de la foto).
    # foto_y + new_h = donde termina la foto. Iron Man va de ahí hacia abajo.
    # ───────────────────────────────────────────────────────────────────────
    ironman = ImageOps.exif_transpose(Image.open(proj / args.ironman)).convert("RGBA")
    bbox = ironman.getbbox()
    if bbox:
        ironman = ironman.crop(bbox)
    # Tamaño que quepa cómodamente en el padding inferior (281 px disponibles)
    target_h = 250
    target_w = int(ironman.width * target_h / ironman.height)
    ironman = ironman.resize((target_w, target_h), Image.LANCZOS)
    # Posicionar en el padding inferior, esquina derecha
    foto_bottom = foto_y + new_h  # y donde termina la foto
    im_x = W - target_w - 30      # margen 30 desde el borde derecho
    im_y = foto_bottom + 10        # 10 px debajo del fin de la foto
    # Sombra natural
    alpha = ironman.split()[-1]
    sh_alpha = alpha.point(lambda p: min(p, 160)).filter(ImageFilter.GaussianBlur(18))
    shadow = Image.new("RGBA", ironman.size, (0, 0, 0, 0))
    shadow.putalpha(sh_alpha)
    canvas.alpha_composite(shadow, (im_x + 6, im_y + 10))
    canvas.alpha_composite(ironman, (im_x, im_y))
    print(f"  iron man: {target_w}x{target_h} en ({im_x}, {im_y})")

    # ───────────────────────────────────────────────────────────────────────
    # 4) Guardar (RGB para evitar problemas en motor downstream)
    # ───────────────────────────────────────────────────────────────────────
    dst = proj / args.output
    dst.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(dst, "PNG", optimize=True)
    print(f"✓ guardado: {dst}")


if __name__ == "__main__":
    main()
