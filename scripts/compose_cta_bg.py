"""
compose_cta_bg.py — Genera fondo cinematográfico con Kie (nano-banana-pro)
y compone el screenshot de IG como "tarjeta flotante" con drop shadow encima.

Resultado: fotos/Screen Instagram editorial.png — listo para usarse como
`foto` del slide CTA en el plan (modo cover).

Uso:
  python scripts/compose_cta_bg.py --proj-dir <ruta>
"""

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps


W, H = 1080, 1350


def _load_dotenv(proj_dir: Path):
    p = proj_dir / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def kie_generate(prompt: str, api_key: str, model: str = "nano-banana-pro") -> str | None:
    payload = json.dumps({
        "model": model,
        "input": {
            "prompt": prompt + ", professional quality, no text",
            "aspect_ratio": "4:5",
            "resolution": "1K",
            "output_format": "png",
        },
    }).encode()
    req = urllib.request.Request(
        "https://api.kie.ai/api/v1/jobs/createTask",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    data = resp.get("data") or {}
    task_id = data.get("taskId")
    if not task_id:
        print(f"  Kie error: {resp.get('msg')}")
        return None
    for _ in range(120):  # nano-banana-pro puede tardar 3-5 min
        time.sleep(3)
        poll = urllib.request.Request(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        info = json.loads(urllib.request.urlopen(poll, timeout=15).read())
        inner = info.get("data") or {}
        state = inner.get("state")
        if state == "success":
            urls = json.loads(inner.get("resultJson", "{}")).get("resultUrls", [])
            return urls[0] if urls else None
        if state in ("failed", "error"):
            print(f"  Kie fail: {inner.get('failMsg')}")
            return None
    return None


def download_image(url: str, dest: Path):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://kie.ai/"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        dest.write_bytes(r.read())


def cover_crop(im: Image.Image, w: int, h: int) -> Image.Image:
    factor = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * factor), round(im.height * factor)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def make_drop_shadow(card: Image.Image, blur: int = 22, alpha_max: int = 180,
                     offset: tuple[int, int] = (0, 18)) -> tuple[Image.Image, tuple[int, int]]:
    """Devuelve (sombra_RGBA, offset_relativo_al_card). La sombra es del mismo
    tamaño que el card; se compone con offset (x, y)."""
    # Máscara: silueta del card (alpha o todo opaco si es RGB)
    if card.mode == "RGBA":
        mask = card.split()[-1]
    else:
        mask = Image.new("L", card.size, 255)
    mask = mask.point(lambda p: min(p, alpha_max))
    mask = mask.filter(ImageFilter.GaussianBlur(blur))
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    shadow.putalpha(mask)
    return shadow, offset


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proj-dir", default=".")
    args = ap.parse_args()
    proj = Path(args.proj_dir).resolve()
    _load_dotenv(proj)

    fotos_dir = proj / "fotos"
    screen_src = fotos_dir / "Screen Instagram.PNG"
    if not screen_src.exists():
        sys.exit(f"❌ no encuentro {screen_src}")

    # 1) Generar fondo IA cinematográfico
    cfg = json.loads((proj / "config.json").read_text(encoding="utf-8"))
    kie_key = cfg.get("kie_ai_key") or os.environ.get("KIE_AI_API_KEY")
    if not kie_key:
        sys.exit("❌ no hay KIE_AI_API_KEY")

    prompt = (
        "luxury modern penthouse rooftop at golden hour evening, warm orange and "
        "amber city lights bokeh in the background, sophisticated minimalist "
        "atmosphere, premium editorial mood, soft warm gradient lighting, "
        "depth of field, cinematic magazine cover quality, photorealistic, "
        "absolutely no people no text, atmospheric background only"
    )
    print("→ Generando fondo cinematográfico con nano-banana-pro...")
    url = kie_generate(prompt, kie_key, "nano-banana-pro")
    if not url:
        sys.exit("❌ Kie no devolvió URL")
    bg_path = fotos_dir / "_editorial_bg.png"
    download_image(url, bg_path)
    print(f"  ✓ fondo descargado: {bg_path.name}")

    # 2) Cargar fondo y cubrir 1080x1350
    bg = ImageOps.exif_transpose(Image.open(bg_path)).convert("RGBA")
    bg = cover_crop(bg, W, H)

    # Veil sutil para que el fondo cinematográfico SE VEA pero no compita.
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 70))
    bg.alpha_composite(veil)

    # 3) Preparar el screenshot como "banner" full-width (extremo a extremo).
    # Sin bordes redondeados (más impactante, ocupa toda la pantalla horizontal).
    screen = ImageOps.exif_transpose(Image.open(screen_src)).convert("RGBA")
    card_w = W  # full width
    card_h = round(screen.height * card_w / screen.width)
    card = screen.resize((card_w, card_h), Image.LANCZOS)

    # Sombra inferior del banner para separarlo del fondo (sólo abajo, sutil)
    shadow_h = 60
    shadow_band = Image.new("L", (1, shadow_h), 0)
    for yy in range(shadow_h):
        t = yy / shadow_h
        shadow_band.putpixel((0, yy), int(180 * (1 - t)))
    shadow_band = shadow_band.resize((W, shadow_h))
    shadow_img = Image.new("RGBA", (W, shadow_h), (0, 0, 0, 0))
    shadow_img.putalpha(shadow_band)

    # Posicionar el banner pegado al borde superior (full bleed top + lateral),
    # así no queda un borde del fondo asomándose arriba.
    cx = 0
    cy = 0
    bg.alpha_composite(card, (cx, cy))
    # Sombra justo debajo del banner
    bg.alpha_composite(shadow_img, (0, cy + card_h))

    # Gradient inferior fuerte para zona del CTA — sale más oscuro
    grad_start = cy + card_h + 40
    grad_col = Image.new("L", (1, H), 0)
    for yy in range(H):
        if yy < grad_start:
            v = 0
        else:
            t = (yy - grad_start) / (H - grad_start)
            v = int(210 * (t ** 0.6))
        grad_col.putpixel((0, yy), v)
    grad_alpha = grad_col.resize((W, H))
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grad.putalpha(grad_alpha)
    bg.alpha_composite(grad)

    # Guardar
    dst = fotos_dir / "Screen Instagram editorial.png"
    bg.convert("RGB").save(dst, "PNG", optimize=True)
    print(f"✓ composición guardada: {dst}")


if __name__ == "__main__":
    main()
