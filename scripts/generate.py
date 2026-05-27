#!/usr/bin/env python3
"""
generate.py — Genera CARRUSELES de Instagram (4:5, 1080×1350) a partir de un plan.

Uso:
  python scripts/generate.py --plan plan.json [--proj-dir /ruta/proyecto]

Diferencias vs el motor de Historias (9:16):
  - Lienzo 1080×1350 (W,H se importan de utils.py — esta copia los tiene en 4:5).
  - SIN barra de progreso superior (Instagram ya muestra los puntitos del carrusel).
  - Bandas de texto más amplias (no hay UI de IG tapando bordes superior/inferior).
  - Fondos IA generados con aspect_ratio "4:5" en Kie.
  - Slides numerados con prefijo "carrusel_<fecha>" en output/.
  - Handle @marca solo en el slide CTA / cierre (igual que historias).

El plan.json tiene esta estructura:
{
  "slides": [
    {
      "numero": 1,
      "tipo": "hook",            // hook | problema | revelacion | beneficios | prueba | cta
      "titulo": "Texto grande",
      "subtitulo": "Texto secundario",
      "texto_extra": "Texto pequeño opcional",
      "foto": "nombre_foto.jpg", // null para fondo sólido o AI
      "fondo_ia": {              // null si no se usa Kie AI
        "prompt": "descripción del fondo a generar"
      },
      "palabras_clave": ["palabra1", "palabra2"], // se resaltan en color primario
      "cta_palabra": "KEYWORD"  // solo en slide tipo cta
    }
  ]
}
"""

import json
import os
import sys
import time
import threading
import urllib.request
from datetime import datetime
from pathlib import Path

# Asegurar imports del proyecto
PROJ_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJ_DIR / "scripts"))

from utils import (
    W, H, load_config, colors_from_config, font as _font,
    new_canvas, load_bg, gradient_overlay, draw_text,
    draw_pill, save,
    # progress_bar disponible en utils pero no se usa en carruseles (IG ya muestra puntitos).
)
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageOps


def _load_dotenv(proj_dir: Path):
    """Carga variables desde un archivo .env (sin dependencias externas)."""
    p = proj_dir / ".env"
    if not p.exists():
        return
    try:
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        pass


def font(proj_dir: Path, size: int, bold: bool = False):
    return _font(proj_dir, size, bold)


# ── Kie AI ─────────────────────────────────────────────────────────────────────

def kie_generate(prompt: str, api_key: str, model: str = "google/nano-banana") -> str | None:
    """Genera imagen con Kie AI y retorna la URL del resultado.

    model: "google/nano-banana" (std ~$0.02/img) | "nano-banana-2" o
    "nano-banana-pro" (premium ~$0.12/img). Los premium NO llevan prefijo.
    """
    payload = json.dumps({
        "model": model,
        "input": {
            "prompt": prompt + ", professional quality, no text",
            "aspect_ratio": "4:5",  # carrusel
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
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
        data = resp.get("data") or {}
        task_id = data.get("taskId")
        if not task_id:
            print(f"  ⚠️  Kie AI: {resp.get('msg', 'sin task_id')}")
            return None
    except Exception as e:
        print(f"  ⚠️  Kie AI error al crear tarea: {e}")
        return None

    # Polling
    for _ in range(60):
        time.sleep(3)
        try:
            poll = urllib.request.Request(
                f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            data = json.loads(urllib.request.urlopen(poll, timeout=15).read())
            inner = data.get("data") or {}
            state = inner.get("state")
            if state == "success":
                result_json = inner.get("resultJson", "{}")
                urls = json.loads(result_json).get("resultUrls", [])
                return urls[0] if urls else None
            if state in ("failed", "error"):
                print(f"  ⚠️  Kie AI tarea fallida: {inner.get('failMsg')}")
                return None
        except Exception as e:
            print(f"  ⚠️  Kie AI poll error: {e}")
    return None


def download_image(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://kie.ai/"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            dest.write_bytes(r.read())
        return True
    except Exception as e:
        print(f"  ⚠️  Error descargando imagen: {e}")
        return False


# ── Renderizado de slides ──────────────────────────────────────────────────────

def resolve_foto_path(proj_dir: Path, nombre: str) -> Path:
    """Resuelve la ruta de una foto buscando en la estructura organizada:
      fotos/                    ← fotos originales de Diego
      fotos/_cutouts/           ← cutouts generados con rembg
      fotos/_compuestas/        ← composiciones de scripts compose_*.py
      fotos/_historicas/        ← imagenes scrapeadas via Apify (seleccionadas)
      fotos/_scraping/.../<f>   ← descargas crudas Apify (cuando se busca recursivo)

    Si el nombre incluye separador (ej. "_cutouts/foo.png") respeta la subruta.
    Devuelve el primer match. Si no encuentra, devuelve fotos/<nombre>
    (fallback — el caller decide si manejar la ausencia).
    """
    fotos_dir = proj_dir / "fotos"
    # Si el path ya tiene separador, respetar
    if "/" in nombre or "\\" in nombre:
        return fotos_dir / nombre
    # Buscar en orden de prioridad
    for sub in (None, "_compuestas", "_cutouts", "_historicas", "_deprecated"):
        candidate = (fotos_dir / sub / nombre) if sub else (fotos_dir / nombre)
        if candidate.exists():
            return candidate
    # Buscar recursivo en _scraping/* (cada query tiene su carpeta)
    scraping = fotos_dir / "_scraping"
    if scraping.exists():
        for sub in scraping.iterdir():
            if sub.is_dir():
                candidate = sub / nombre
                if candidate.exists():
                    return candidate
    # Fallback (no existe) — caller maneja
    return fotos_dir / nombre


def _wrap_lines(draw, text, fnt, max_w):
    """Word-wrap que RESPETA los saltos de línea explícitos (\n).
    Cada párrafo separado por \n se wrap-ea de forma independiente — útil
    para listas verticales (ej. texto_extra con ✅ Item1\n✅ Item2)."""
    all_lines = []
    paragraphs = str(text).split("\n")
    for paragraph in paragraphs:
        words = paragraph.split()
        if not words:
            all_lines.append("")  # línea en blanco intencional
            continue
        lines, cur = [], []
        for w in words:
            test = " ".join(cur + [w])
            if draw.textbbox((0, 0), test, font=fnt)[2] > max_w and cur:
                lines.append(" ".join(cur)); cur = [w]
            else:
                cur.append(w)
        if cur:
            lines.append(" ".join(cur))
        all_lines.extend(lines)
    return all_lines


def draw_fitted_block(draw, proj_dir, blocks, y_top, y_bottom, max_w=950, anchor="center", center_x=None):
    """Dibuja varios bloques de texto centrados, escalando la fuente para que
    todo quepa dentro de [y_top, y_bottom]. blocks: lista de dicts con
    {text, size, bold, color, stroke, gap}.

    center_x: punto x sobre el que centrar el texto. Si es None, centra sobre
    todo el lienzo (W/2). Útil para layouts laterales (ej. cover híbrido con
    foto a un lado y texto en la mitad opuesta).
    """
    if center_x is None:
        center_x = W // 2
    blocks = [b for b in blocks if b.get("text")]
    scale = 1.0
    rendered, total = [], 0
    for _ in range(16):
        rendered, total = [], 0
        for b in blocks:
            s = max(22, int(b["size"] * scale))
            fnt = font(proj_dir, s, bold=b.get("bold", False))
            lines = _wrap_lines(draw, b["text"], fnt, max_w)
            lh = s + max(6, int(14 * scale))
            block_h = lh * len(lines)
            rendered.append((b, fnt, lines, lh))
            total += block_h + int(b.get("gap", 26) * scale)
        if total <= (y_bottom - y_top) or scale <= 0.5:
            break
        scale *= 0.92
    y = y_top + max(0, ((y_bottom - y_top) - total) // 2) if anchor == "center" else y_top
    for b, fnt, lines, lh in rendered:
        stroke = b.get("stroke", 0)
        for line in lines:
            bb = draw.textbbox((0, 0), line, font=fnt)
            x = center_x - (bb[2] - bb[0]) // 2
            draw.text((x + 3, y + 3), line, font=fnt, fill=(0, 0, 0, 170))
            draw.text((x, y), line, font=fnt, fill=b["color"],
                      stroke_width=stroke, stroke_fill=b["color"] if stroke else None)
            y += lh
        y += int(b.get("gap", 26) * scale)
    return y


def side_gradient_overlay(img, side="left", strength=0.70):
    """Oscurece un lado del lienzo gradualmente (de fuerte en el borde a 0 en el
    centro). Sirve para legibilidad de texto en covers híbridos donde la foto
    ocupa una mitad y el texto la otra.

    side: 'left' o 'right' — qué lado se oscurece.
    """
    row = Image.new("L", (W, 1), 0)
    px = row.load()
    for x in range(W):
        if side == "left":
            t = max(0.0, 1 - x / (W * 0.6))  # más oscuro a la izquierda, fade hasta 60% del ancho
        else:
            t = max(0.0, (x - W * 0.4) / (W * 0.6))  # más oscuro a la derecha
        px[x, 0] = int(255 * strength * (t ** 1.3))
    alpha = row.resize((W, H))
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    veil.putalpha(alpha)
    img.alpha_composite(veil)


def pick_text_band(img, pos="auto", has_foto=False):
    """Devuelve (y_top, y_bottom) donde colocar el texto.
    pos: 'top' | 'center' | 'bottom' | 'auto'.

    En 'auto' con foto, la lógica prioriza en este orden:
      1) Si el cutout (alpha variable) tiene mucho contenido en una banda
         → EVITAR esa banda (no tapar la cara/sujeto). Esto resuelve el caso
         clásico de un PNG transparente donde la persona ocupa el centro-arriba.
      2) Como criterio secundario / desempate, elegir la banda más oscura
         (mejor contraste para el texto).

    Carrusel 4:5 (H=1350): a diferencia de las historias, NO hay UI de IG
    tapando los bordes superior/inferior dentro de la imagen, así que las
    bandas pueden acercarse mucho más a las orillas (más respiro de diseño).
    """
    bands = {
        "top":    (60,  540),   # 4–40 % del alto
        "center": (370, 980),   # 27–73 %
        "bottom": (720, 1300),  # 53–96 %
    }
    if pos in bands:
        return bands[pos]
    if not has_foto:
        return bands["bottom"]

    from PIL import ImageStat

    def lum(y0, y1):
        return ImageStat.Stat(img.crop((0, y0, W, y1)).convert("L")).mean[0]

    def cutout_density(y0, y1):
        """Fracción 0–1 de la banda cubierta por el cutout (alpha > 0).
        Devuelve 0 si la imagen no es RGBA (foto normal con fondo)."""
        crop = img.crop((0, y0, W, y1))
        if crop.mode != "RGBA":
            return 0.0
        alpha = crop.split()[-1]
        return ImageStat.Stat(alpha).mean[0] / 255.0

    top_d = cutout_density(*bands["top"])
    bot_d = cutout_density(*bands["bottom"])

    # ── Prioridad 1: si el cutout claramente domina una banda, evítala ──
    # Umbral 0.30 = la banda contiene >30% de pixels opacos del sujeto.
    # Margen 0.15 = una banda tiene que tener bastante MENOS contenido para ganar
    # (si están parejas, no decidimos por aquí — caemos al luminosity).
    if max(top_d, bot_d) > 0.30:
        if top_d < bot_d - 0.15:
            return bands["top"]
        if bot_d < top_d - 0.15:
            return bands["bottom"]

    # ── Prioridad 2: luminosity (banda más oscura gana) ──
    return bands["top"] if lum(*bands["top"]) <= lum(*bands["bottom"]) else bands["bottom"]


def draw_badges(img, draw, proj_dir, names, y=130):
    """Chips de marca como protagonistas. Auto-escala al tamaño más grande
    posible (hasta ~3× lo anterior). Si son muchos, se acomodan en 2 filas
    para mantener el tamaño grande. Usa logos/<slug>.png si existe; si no,
    muestra el nombre en un chip blanco."""
    if not names:
        return
    max_w = 980

    def build_specs(items, h):
        gap = max(14, h // 8)
        pad = max(20, h // 3)
        fnt = font(proj_dir, max(26, int(h * 0.40)), bold=True)
        specs = []
        for name in items:
            slug = "".join(c for c in name.lower() if c.isalnum())
            lp = proj_dir / "logos" / f"{slug}.png"
            if lp.exists() and lp.stat().st_size > 1000:
                specs.append(("img", lp, name, int(h * 1.9), fnt))
            else:
                bb = draw.textbbox((0, 0), name, font=fnt)
                specs.append(("txt", None, name, (bb[2] - bb[0]) + pad * 2, fnt))
        return specs, gap

    def pack(specs, gap):
        rows = []
        cur, cur_w = [], 0
        for sp in specs:
            w = sp[3]
            if cur and cur_w + gap + w > max_w:
                rows.append((cur, cur_w))
                cur, cur_w = [sp], w
            else:
                cur_w = cur_w + gap + w if cur else w
                cur.append(sp)
        if cur:
            rows.append((cur, cur_w))
        return rows

    # Elegimos el h más grande que produzca <= 2 filas (chips grandes)
    chosen = None
    for h in (200, 180, 160, 140, 120, 100):
        specs, gap = build_specs(names, h)
        rows = pack(specs, gap)
        if len(rows) <= 2:
            chosen = (h, gap, rows)
            break
    if chosen is None:
        h_fallback = 90
        specs, gap = build_specs(names, h_fallback)
        chosen = (h_fallback, gap, pack(specs, gap))

    h, gap, rows = chosen
    cur_y = y
    for row, row_w in rows:
        x = (W - row_w) // 2
        for kind, path, name, w, fnt in row:
            draw.rounded_rectangle([x, cur_y, x + w, cur_y + h], radius=h // 2,
                                   fill=(255, 255, 255, 240))
            if kind == "txt":
                bb = draw.textbbox((0, 0), name, font=fnt)
                draw.text((x + (w - (bb[2] - bb[0])) // 2,
                           cur_y + (h - (bb[3] - bb[1])) // 2 - bb[1]),
                          name, font=fnt, fill=(12, 12, 16))
            else:
                try:
                    lg = Image.open(path).convert("RGBA")
                    lh = h - int(h * 0.22)
                    lw = int(lg.width * (lh / lg.height))
                    if lw > w - int(h * 0.3):
                        lw = w - int(h * 0.3)
                        lh = int(lg.height * (lw / lg.width))
                    lg = lg.resize((max(1, lw), max(1, lh)), Image.LANCZOS)
                    img.alpha_composite(lg, (x + (w - lw) // 2, cur_y + (h - lh) // 2))
                except Exception:
                    pass
            x += w + gap
        cur_y += h + 16


def render_slide(slide: dict, idx: int, total: int,
                 proj_dir: Path, cfg: dict, colors: dict,
                 kie_cache: dict, kie_key: str | None,
                 output_dir: Path) -> Path:

    tipo = slide.get("tipo", "hook")
    foto = slide.get("foto")
    fondo_ia = slide.get("fondo_ia")
    keywords = slide.get("palabras_clave", [])

    PRIMARY = colors["PRIMARY"]
    WHITE = colors["WHITE"]
    DIM = colors["DIM"]
    YELLOW = colors["YELLOW"]

    # ── Fondo ──────────────────────────────────────────────────────────────────
    fondo_ia_cached = (
        fondo_ia is not None
        and kie_key
        and fondo_ia.get("prompt", "") in kie_cache
    )
    # foto_lado se evalúa acá porque define el lado del gradiente de legibilidad
    foto_lado = slide.get("foto_lado", "right")  # right|left — sólo en modo híbrido
    modo_hibrido = bool(foto and fondo_ia_cached)

    if modo_hibrido:
        # Cover híbrido: fondo IA como base + foto cutout sobrepuesta a un lado.
        # El darken del fondo es más suave para que la imagen IA se aprecie.
        img = load_bg(kie_cache[fondo_ia["prompt"]], darken=0.30)
        # Sobreponer la foto cutout transparente
        foto_path = resolve_foto_path(proj_dir, foto)
        if foto_path.exists():
            cutout = ImageOps.exif_transpose(Image.open(foto_path)).convert("RGBA")
            escala = slide.get("foto_escala", 0.85)
            new_h = int(H * escala)
            new_w = max(1, int(cutout.width * new_h / cutout.height))
            cutout = cutout.resize((new_w, new_h), Image.LANCZOS)
            # Apoyar en el borde inferior, lado configurable. foto_offset empuja
            # la figura un poco hacia afuera del lienzo para que se "salga".
            foto_offset = slide.get("foto_offset", 60)
            if foto_lado == "right":
                x = W - new_w + foto_offset
            else:
                x = -foto_offset
            y = H - new_h
            img.alpha_composite(cutout, (x, y))
        # Oscurecer el lado opuesto a la foto para legibilidad del texto
        side_gradient_overlay(img, "left" if foto_lado == "right" else "right", strength=0.92)
    elif foto:
        foto_path = resolve_foto_path(proj_dir, foto)
        if foto_path.exists():
            # foto_darken: 0.55 default. Subir (0.65–0.80) cuando el contenido de
            # la foto es muy "busy" (screenshot, dashboard).
            # foto_modo: "cover" (default, llena el lienzo) | "fit" (entra entera
            # con padding negro). foto_y_pos: "top"|"center"|"bottom" (solo fit).
            darken = slide.get("foto_darken", 0.55)
            modo = slide.get("foto_modo", "cover")
            y_pos = slide.get("foto_y_pos", "center")
            img = load_bg(foto_path, darken=darken, modo=modo, y_pos=y_pos)
            # gradient_overlay tiene sentido sólo cuando la foto llena todo
            # (modo cover); en modo fit el padding ya es negro puro.
            # Se puede desactivar explícitamente con `aplicar_gradient: false`
            # cuando la foto ya viene pre-compuesta con su propio gradient.
            if modo == "cover" and slide.get("aplicar_gradient", True):
                gradient_overlay(img, "bottom", 0.70)
        else:
            print(f"  ⚠️  Foto no encontrada: {foto}, usando fondo sólido")
            img = new_canvas(colors)
    elif fondo_ia_cached:
        img = load_bg(kie_cache[fondo_ia["prompt"]], darken=0.50)
        gradient_overlay(img, "bottom", 0.65)
    else:
        img = new_canvas(colors)

    draw = ImageDraw.Draw(img)

    # ── (Sin barra de progreso) ────────────────────────────────────────────────
    # En carrusel, Instagram muestra sus propios puntitos de paginación debajo
    # de la imagen, así que omitimos la barra que sí usábamos en Historias.

    # ── Logos / chips de marca ───────────────────────────────────────────────────
    draw_badges(img, draw, proj_dir, slide.get("logos", []))

    # ── Contenido según tipo ───────────────────────────────────────────────────
    titulo = slide.get("titulo", "")
    subtitulo = slide.get("subtitulo", "")
    texto_extra = slide.get("texto_extra", "")

    if tipo == "hook":
        if modo_hibrido:
            # Cover híbrido: texto en mitad opuesta a la foto.
            # Si foto_lado == "right" → texto en mitad izquierda.
            # Si foto_lado == "left"  → texto en mitad derecha.
            if foto_lado == "right":
                text_cx = int(W * 0.25)   # ≈ 270
            else:
                text_cx = int(W * 0.75)   # ≈ 810
            text_maxw = 440
            # Etiqueta opcional con opt-out explícito (mismo patrón que el
            # branch clásico): null/"" en el slide = NO dibujar píldora;
            # ausente = usar default del config.
            if "etiqueta" in slide:
                etiqueta_val = slide.get("etiqueta")
            else:
                etiqueta_val = cfg.get("etiqueta_hook", "NUEVA HISTORIA")
            if etiqueta_val:
                draw_pill(
                    draw, etiqueta_val,
                    100, font(proj_dir, 30), PRIMARY, center_x=text_cx,
                )
            # Banda de texto generosa, layout fijo (sin pick_text_band).
            draw_fitted_block(
                draw, proj_dir,
                [
                    {"text": titulo,      "size": 56, "bold": True,  "color": WHITE,   "stroke": 1, "gap": 18},
                    {"text": subtitulo,   "size": 36, "bold": False, "color": PRIMARY, "stroke": 1, "gap": 14},
                    {"text": texto_extra, "size": 30, "bold": False, "color": DIM,     "gap": 0},
                ],
                y_top=240, y_bottom=1240, max_w=text_maxw, center_x=text_cx,
            )
        else:
            # Hook clásico (full-width, texto sobre foto o fondo IA solo).
            # Etiqueta (píldora superior): opcional con opt-out explícito.
            #  - "etiqueta" no está en el slide → default del config
            #  - "etiqueta" presente con null/"" → NO dibujar píldora
            #  - "etiqueta" con valor → dibujar ese valor
            if "etiqueta" in slide:
                etiqueta_val = slide.get("etiqueta")
            else:
                etiqueta_val = cfg.get("etiqueta_hook", "NUEVA HISTORIA")
            if etiqueta_val:
                draw_pill(draw, etiqueta_val, 120, font(proj_dir, 34), PRIMARY)
            y_top, y_bottom = pick_text_band(img, slide.get("texto_pos", "auto"), bool(foto))
            # Override de banda de texto: util cuando el slide tiene una
            # composicion pre-hecha y la banda automatica choca con cutouts.
            if "text_y_top" in slide:
                y_top = slide["text_y_top"]
            if "text_y_bottom" in slide:
                y_bottom = slide["text_y_bottom"]
            draw_fitted_block(draw, proj_dir, [
                {"text": titulo,    "size": 70, "bold": True,  "color": WHITE,   "stroke": 1, "gap": 20},
                {"text": subtitulo, "size": 50, "bold": False, "color": PRIMARY, "stroke": 1, "gap": 16},
                {"text": texto_extra, "size": 40, "bold": False, "color": DIM,   "gap": 0},
            ], y_top=y_top, y_bottom=y_bottom)

    elif tipo == "cta":
        cta_palabra = slide.get("cta_palabra", "PALABRA")
        cta_verbo = slide.get("cta_verbo") or (cfg.get("cta_formato") or "Responde").split()[0]
        nombre_marca = cfg.get("instagram_user") or cfg.get("nombre_marca", "@tumarca")
        # Si el CTA usa una foto de fondo (típicamente screenshot de perfil IG
        # como prueba social), aplicamos un velo con GRADIENT SUAVE desde la
        # mitad del lienzo, dejando el screenshot visible arriba y el CTA en
        # una zona oscura abajo.
        if foto:
            # Velo gradient progresivo (controlable con `cta_extra_veil: false`
            # cuando la foto ya viene con gradient pre-compuesto).
            if slide.get("cta_extra_veil", True):
                veil_col = Image.new("L", (1, H), 0)
                for yy in range(H):
                    if yy < 400:
                        v = 0
                    else:
                        t = (yy - 400) / (H - 400)
                        v = int(248 * (t ** 0.4))
                    veil_col.putpixel((0, yy), v)
                veil_alpha = veil_col.resize((W, H))
                veil_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                veil_img.putalpha(veil_alpha)
                img.alpha_composite(veil_img)

            # foto_cutout opcional: foto adicional (puede ser rectangular con
            # fondo o cutout transparente) que se sobrepone al lado del CTA
            # como refuerzo visual estilo polaroid.
            foto_cutout_name = slide.get("foto_cutout")
            cutout_present = False
            cta_zone_right = W
            if foto_cutout_name:
                cutout_path = resolve_foto_path(proj_dir, foto_cutout_name)
                if cutout_path.exists():
                    c_img = ImageOps.exif_transpose(Image.open(cutout_path)).convert("RGBA")
                    # Si es cutout transparente (RGBA con regiones vacías),
                    # recortar al bounding box del contenido — descarta el
                    # padding transparente exterior.
                    if c_img.mode == "RGBA":
                        bbox = c_img.getbbox()
                        if bbox:
                            c_img = c_img.crop(bbox)
                    target_h = slide.get("foto_cutout_h", 580)
                    target_w = max(1, int(c_img.width * target_h / c_img.height))
                    c_img = c_img.resize((target_w, target_h), Image.LANCZOS)

                    # foto_cutout_frame:
                    #   "none" (default desde ahora) → cutout transparente
                    #     directo sobre el slide con drop shadow natural
                    #     (estilo editorial/Skai, sin marco blanco).
                    #   "polaroid" → frame blanco rectangular tipo polaroid
                    #     (legacy, conservado por si se quiere ese look).
                    frame_style = slide.get("foto_cutout_frame", "none")
                    # Margenes laterales / inferiores del cutout, configurables
                    # por slide. Subir margen inferior a 0 para que el cutout
                    # llegue hasta el borde inferior del lienzo (full bleed).
                    margin_right = slide.get("foto_cutout_margin_right", 40)
                    margin_bottom = slide.get("foto_cutout_margin_bottom", 40)
                    fx = W - target_w - margin_right
                    fy = H - target_h - margin_bottom

                    if frame_style == "polaroid":
                        pad = 14
                        extra = 30
                        frame_w = target_w + pad * 2
                        frame_h = target_h + pad * 2 + extra
                        frame = Image.new("RGBA", (frame_w, frame_h), (255, 255, 255, 250))
                        frame.paste(c_img, (pad, pad))
                        shadow = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 90))
                        fx = W - frame_w - 40
                        fy = H - frame_h - 40
                        img.alpha_composite(shadow, (fx + 6, fy + 6))
                        img.alpha_composite(frame, (fx, fy))
                    else:
                        # Cutout directo sin marco. Sombra natural derivada
                        # de la silueta (alpha del cutout) — se posiciona
                        # ligeramente offset, blur fuerte, alpha sutil.
                        alpha = c_img.split()[-1]
                        shadow_alpha = alpha.point(lambda p: min(p, 140))
                        shadow_alpha = shadow_alpha.filter(ImageFilter.GaussianBlur(14))
                        shadow_img = Image.new("RGBA", c_img.size, (0, 0, 0, 0))
                        shadow_img.putalpha(shadow_alpha)
                        img.alpha_composite(shadow_img, (fx + 10, fy + 14))
                        img.alpha_composite(c_img, (fx, fy))
                    cta_zone_right = fx - 20
                    cutout_present = True

            # Geometría del CTA: si hay foto_cutout, comprimido a la izquierda.
            if cutout_present:
                cta_cx = cta_zone_right // 2 + 20
                cta_maxw = cta_zone_right - 40
                box_w = slide.get("cta_box_w", 360)
                title_size = slide.get("cta_title_size", 38)
                verbo_size = slide.get("cta_verbo_size", 32)
                kw_size = slide.get("cta_kw_size", 44)
                subt_size = slide.get("cta_subt_size", 30)
                handle_size = slide.get("cta_handle_size", 36)
            else:
                cta_cx = W // 2
                cta_maxw = W - 60
                box_w = slide.get("cta_box_w", 540)
                title_size = slide.get("cta_title_size", 50)
                verbo_size = slide.get("cta_verbo_size", 44)
                kw_size = slide.get("cta_kw_size", 54)
                subt_size = slide.get("cta_subt_size", 36)
                handle_size = slide.get("cta_handle_size", 40)

            # Render del CTA
            y = draw_fitted_block(draw, proj_dir, [
                {"text": titulo, "size": title_size, "bold": True, "color": WHITE, "stroke": 1, "gap": 0},
            ], y_top=730, y_bottom=860, max_w=cta_maxw, center_x=cta_cx, anchor="top")
            y += 12
            # Verbo + caja amarilla con palabra clave: opcionales.
            # Si cta_palabra es null/"" → CTA conversacional (sin caja amarilla
            # ni "Comenta"). Solo título + subtítulo + handle.
            if cta_palabra:
                cv_f = font(proj_dir, verbo_size)
                cv_w = draw.textlength(cta_verbo, font=cv_f)
                draw.text((cta_cx - int(cv_w) // 2, y), cta_verbo, font=cv_f, fill=DIM)
                y += verbo_size + 14
                box_h = int(box_w * 0.26)
                bx = cta_cx - box_w // 2
                draw.rounded_rectangle([bx, y, bx + box_w, y + box_h], radius=20,
                                       fill=(*YELLOW, 50), outline=YELLOW, width=3)
                kw_f = font(proj_dir, kw_size, bold=True)
                bb = draw.textbbox((0, 0), cta_palabra, font=kw_f)
                kx = cta_cx - (bb[2] - bb[0]) // 2
                draw.text((kx + 2, y + (box_h - kw_size) // 2 + 2), cta_palabra, font=kw_f, fill=(0, 0, 0, 120))
                draw.text((kx, y + (box_h - kw_size) // 2), cta_palabra, font=kw_f, fill=YELLOW,
                          stroke_width=2, stroke_fill=YELLOW)
                y += box_h + 22
            else:
                y += 30  # gap mínimo si no hay caja
            # cta_show_handle: false oculta el @marca al pie (cuando el
            # slide ya muestra el handle de otra forma, ej. via screenshot
            # de IG visible arriba).
            blocks = [
                {"text": subtitulo or "y te mando el tutorial completo.", "size": subt_size, "bold": False, "color": WHITE, "gap": 14},
            ]
            if slide.get("cta_show_handle", True):
                blocks.append({"text": nombre_marca, "size": handle_size, "bold": True, "color": PRIMARY, "gap": 0})
            else:
                # quitar el gap del subtítulo si no hay handle abajo
                blocks[0]["gap"] = 0
            draw_fitted_block(draw, proj_dir, blocks,
                              y_top=y, y_bottom=1310, max_w=cta_maxw, center_x=cta_cx, anchor="top")
        else:
            # Layout clásico full-canvas (sin foto de fondo).
            y = draw_fitted_block(draw, proj_dir, [
                {"text": titulo, "size": 64, "bold": True, "color": WHITE, "stroke": 1, "gap": 0},
            ], y_top=310, y_bottom=520, anchor="top")
            y += 24
            draw_text(draw, cta_verbo, y, font(proj_dir, 56), DIM)
            y += 84
            box_w, box_h = 580, 120
            bx = (W - box_w) // 2
            draw.rounded_rectangle([bx, y, bx + box_w, y + box_h], radius=24,
                                   fill=(*YELLOW, 40), outline=YELLOW, width=3)
            kw_f = font(proj_dir, 62, bold=True)
            bb = draw.textbbox((0, 0), cta_palabra, font=kw_f)
            kx = (W - (bb[2] - bb[0])) // 2
            draw.text((kx + 2, y + 26 + 2), cta_palabra, font=kw_f, fill=(0, 0, 0, 120))
            draw.text((kx, y + 26), cta_palabra, font=kw_f, fill=YELLOW,
                      stroke_width=2, stroke_fill=YELLOW)
            y += box_h + 36
            draw_fitted_block(draw, proj_dir, [
                {"text": subtitulo or "y te mando el tutorial completo.", "size": 52, "bold": False, "color": WHITE, "gap": 20},
                {"text": texto_extra, "size": 40, "bold": False, "color": DIM, "gap": 20},
                {"text": nombre_marca, "size": 46, "bold": True, "color": PRIMARY, "gap": 0},
            ], y_top=y, y_bottom=1300, anchor="top")

    else:
        # Slides genéricos: problema, revelacion, beneficios, prueba
        y_top, y_bottom = pick_text_band(img, slide.get("texto_pos", "auto"), bool(foto))
        draw_fitted_block(draw, proj_dir, [
            {"text": titulo,    "size": 68, "bold": True,  "color": WHITE,   "stroke": 1, "gap": 22},
            {"text": subtitulo, "size": 48, "bold": False, "color": PRIMARY, "stroke": 1, "gap": 18},
            {"text": texto_extra, "size": 40, "bold": False, "color": DIM,   "gap": 0},
        ], y_top=y_top, y_bottom=y_bottom)

    # ── Guardar ────────────────────────────────────────────────────────────────
    nombre = f"{idx:02d}-{tipo}.png"
    return save(img, output_dir, nombre)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, help="Ruta al plan.json")
    parser.add_argument("--proj-dir", default=".", help="Directorio raíz del proyecto")
    args = parser.parse_args()

    proj_dir = Path(args.proj_dir).resolve()
    _load_dotenv(proj_dir)
    cfg = load_config(proj_dir)
    colors = colors_from_config(cfg)

    plan = json.loads(Path(args.plan).read_text())
    slides = plan["slides"]
    total = len(slides)

    ts = datetime.now().strftime("%Y-%m-%d_%H%M")
    output_dir = proj_dir / "output" / f"carrusel_{ts}"
    output_dir.mkdir(parents=True, exist_ok=True)

    kie_key = cfg.get("kie_ai_key") or os.environ.get("KIE_AI_API_KEY")
    kie_cache: dict[str, Path] = {}

    # Pre-generar fondos AI en paralelo (o reusar de cache si está en disco).
    # Incluye también slides híbridos (foto + fondo_ia juntos).
    ai_slides = [(i, s) for i, s in enumerate(slides) if s.get("fondo_ia")]

    # Primero: cargar los que tienen cache_path (reuso, $0)
    for i, s in ai_slides:
        cp = s["fondo_ia"].get("cache_path")
        if cp:
            path = Path(cp) if Path(cp).is_absolute() else (proj_dir / cp)
            if path.exists():
                kie_cache[s["fondo_ia"]["prompt"]] = path
                print(f"  ♻️  Fondo IA slide {i+1} reusado de cache: {path.name}")

    # Luego: generar con Kie los que NO tienen cache_path
    remaining = [(i, s) for i, s in ai_slides
                 if s["fondo_ia"]["prompt"] not in kie_cache]
    if kie_key and remaining:
        print(f"\n→ Generando {len(remaining)} fondo(s) con IA en paralelo...")
        results: dict[int, str | None] = {}

        def gen(idx, slide):
            try:
                prompt = slide["fondo_ia"]["prompt"]
                model = slide["fondo_ia"].get("model", "google/nano-banana")
                url = kie_generate(prompt, kie_key, model=model)
                if url:
                    dest = output_dir / f"_bg_{idx:02d}.png"
                    if download_image(url, dest):
                        results[idx] = dest
                        print(f"  ✅ Fondo IA slide {idx+1} listo ({model})")
            except Exception as e:
                print(f"  ⚠️  Thread slide {idx+1} error: {e}")

        threads = [threading.Thread(target=gen, args=(i, s)) for i, s in remaining]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        for idx, slide in remaining:
            if idx in results:
                key = slide["fondo_ia"]["prompt"]
                kie_cache[key] = results[idx]

    print(f"\n→ Renderizando {total} slides...")
    for i, slide in enumerate(slides, 1):
        render_slide(slide, i, total, proj_dir, cfg, colors,
                     kie_cache, kie_key, output_dir)

    # Guardar copia del plan
    (output_dir / "plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False))

    print(f"\n✅ Carrusel generado en: {output_dir}")
    return str(output_dir)


if __name__ == "__main__":
    main()
