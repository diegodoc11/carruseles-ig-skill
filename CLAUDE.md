# CLAUDE.md — Guía del proyecto

Generador de **carruseles de Instagram (1080×1350, 4:5)** para Claude Code. El usuario dicta un tema; la skill elige el tipo REPTINAC, escribe el copy persuasivo y renderiza los 7–8 slides listos para publicar. Hermana de `/historias-ig` (formato 9:16) — comparten brief, fotos, logos y biblioteca de contenido vía junctions/hard links.

## ⚠️ Regla de oro
**Nunca generes imágenes sin que el usuario apruebe el copy exacto de cada slide.** Muestra el copy (título, subtítulo, texto extra, CTA, etiqueta) slide por slide, espera el OK explícito, y solo entonces ejecuta `generate.py`. Cada fondo IA con `google/nano-banana` cuesta ~$0.02; con `nano-banana-pro` ~$0.12 → gastar sin aprobación quema dinero real.

## 🎯 Particularidades del formato carrusel
1. **Slide 1 = portada** — gancho visual + copy más fuerte. Si no para el scroll, todo el carrusel muere.
2. **Slide 2 = segundo hook** — Instagram lo re-impresiona a quienes ya vieron tu carrusel. Necesita su propio gancho (refuerzo de promesa, dolor, sueño). NUNCA arrancar el ranking en slide 2.
3. **Último slide convierte** — CTA con palabra clave → DM.
4. **Slide 1 y 2 con `nano-banana-pro`** (premium). Slides 3+ con `google/nano-banana` standard.
5. **Sin barra de progreso** — Instagram ya muestra los puntitos.
6. **7–8 slides default** (rango sano 5–10).
7. El motor **NUNCA tapa la cara** en cutouts transparentes — `pick_text_band` detecta contenido del alpha channel.

## Estructura
```
skill/carruseles.md           ← Cerebro de la skill (flujo, onboarding, reglas)
skill/biblioteca-contenido.md ← 8 tipos REPTINAC (compartida con historias-ig via hard link)
scripts/generate.py           ← Motor de render (lee plan.json → PNG 1080×1350)
scripts/utils.py              ← Pipeline de imagen (load_bg cover|fit, fondos, texto)
scripts/scan_fotos.py         ← Cataloga fotos/ → catalogo.json
scripts/telegram_enviar.py    ← Envía set al celular vía bot de Telegram
scripts/compose_cta_bg.py     ← Compone fondo IA + screenshot como card flotante
scripts/kie_edit.py           ← Edita imágenes con nano-banana-pro (image-to-image)
config.json                   ← Marca + brief (privado, en .gitignore)
fotos/ logos/ fonts/ output/  (todos en .gitignore)
```

## Flujo de generación
1. Leer `config.json` (marca + brief). Si no existe → onboarding (ver `skill/carruseles.md`).
2. Pedir **tema + objetivo**.
3. Leer `skill/biblioteca-contenido.md` y elegir **tipo REPTINAC** (priorizar los que brillan en carrusel: Transformación, Engagement Top N, Polarización, Autoridad, Niveles de Consciencia, Conversión).
4. Escanear fotos (`scan_fotos.py`); consultar `catalogo_detallado.json` si existe.
5. Escribir el **plan.json** (un objeto por slide) y **mostrar el copy para aprobación**.
6. Tras el OK: `python scripts/generate.py --plan plan.json --proj-dir .`
7. Mostrar resultados y ofrecer envío por Telegram (`telegram_enviar.py`).

## Schema del plan (campos por slide)

### Básicos
- `tipo`: `hook` para slide 1, `cta` para último; descriptivo para intermedios (`refuerzo`, `puesto5`, `mito`, etc).
- `titulo`, `subtitulo`, `texto_extra`.
- `foto`: nombre de archivo en `fotos/` (o `null`).
- `fondo_ia`: objeto `{prompt, model, cache_path}`. Modelo: `"google/nano-banana"` standard | `"nano-banana-pro"` premium.
- `texto_pos`: `"auto"` (default) | `"top"` | `"center"` | `"bottom"`.
- `etiqueta` (hook), `palabras_clave`, `logos`, `cta_palabra`, `cta_verbo`.

### Modo híbrido (slide hook con foto cutout + fondo IA combinados)
- `foto_lado`: `"right"` (default) | `"left"`.
- `foto_escala`: 0.0–1.0 (default 0.85).
- `foto_offset`: pixels del borde lateral (default 60).

### Foto como fondo (modo cover|fit)
- `foto_modo`: `"cover"` (default, llena el lienzo) | `"fit"` (entra entera con padding negro).
- `foto_y_pos`: `"top"` | `"center"` | `"bottom"` (solo aplica en modo fit).
- `foto_darken`: 0.0–1.0 (default 0.55). Subir para fotos busy (screenshots, dashboards).
- `aplicar_gradient`: bool (default true). False cuando la foto ya viene con gradient pre-compuesto.

### Cutout sobrepuesto adicional (foto_cutout)
- `foto_cutout`: nombre de archivo en `fotos/` (preferiblemente transparente — usar `rembg` con `birefnet-general`).
- `foto_cutout_h`: alto en píxeles (default 580).
- `foto_cutout_margin_right`: margen al borde derecho (default 40).
- `foto_cutout_margin_bottom`: margen al borde inferior (default 40, usar 0 para full bleed).
- `foto_cutout_frame`: `"none"` (default, cutout directo con sombra natural) | `"polaroid"` (marco blanco rectangular).

### CTA personalizable
- `cta_box_w`: ancho de la caja amarilla (default 360 con cutout, 540 sin).
- `cta_title_size`, `cta_verbo_size`, `cta_kw_size`, `cta_subt_size`, `cta_handle_size`: tamaños configurables.
- `cta_show_handle`: bool (default true). False cuando el handle ya está visible vía screenshot/cutout.
- `cta_extra_veil`: bool (default true). False cuando la foto base ya viene oscurecida.

## Convenciones del motor
- **Lienzo:** carrusel 1080×1350 (4:5). Texto: título blanco, subtítulo en color primario, extra en gris.
- **Autoajuste:** `draw_fitted_block` escala el texto para caber en una banda.
- **Colocación inteligente:** `pick_text_band` detecta contenido del cutout transparente y evita esa zona.
- **Fondos:** foto real (modo cover|fit) → IA Kie (`google/nano-banana` ~$0.02; `nano-banana-pro` ~$0.12) → sólido.
- **Cache de fondos IA:** `fondo_ia.cache_path: "output/.../bg_NN.png"` reusa sin gastar Kie.
- **Chips de marca:** `logos:[...]` usa `logos/<slug>.png` si existe; si no, muestra el nombre como pill blanco.
- **CTA:** `Comenta [PALABRA] y te envío [recurso]`. Palabra en MAYÚSCULAS, 3–8 letras, sin acentos (esta regla se puede romper si el usuario insiste — Diego usa "AUTOMATIZAR", 10 letras).
- **Ejecutar siempre con** `python -X utf8` (la consola Windows puede no ser UTF-8).

## Pipeline avanzado

### Composiciones pre-hechas (compose_cta_bg.py)
Para slides editoriales (típicamente el CTA con prueba social), `scripts/compose_cta_bg.py` genera un fondo IA con `nano-banana-pro` y pega el screenshot de IG como banner full-width con sombra inferior. Resultado se guarda como `fotos/Screen Instagram editorial.png` y se usa con `foto_modo: "cover"`, `aplicar_gradient: false`, `cta_extra_veil: false`.

### Edición de imágenes con IA (kie_edit.py)
`scripts/kie_edit.py` permite editar una imagen local con `nano-banana-pro` (image-to-image). Sube la imagen a un host público (catbox.moe → tmpfiles.org → 0x0.st con fallback) y llama al endpoint con `image_urls`. **Advertencia:** los modelos generativos pueden alterar caras, textos y números — útil para edits simples, NO para preservar identidad/contenido crítico.

### Cutouts con rembg
Modelo por defecto: `birefnet-general` (~970MB, state-of-the-art). Esencial para detalles finos como dedos apuntando. El modelo `u2net` (default de rembg) causa dedos semi-transparentes contra fondos oscuros.
```python
from rembg import remove, new_session
session = new_session("birefnet-general")
out = remove(input_bytes, session=session)
```

### Apify CLI (futuro)
Instalado vía npm. Para scraping de imágenes complementarias (mockups reales de productos, logos no incluidos en `logos/`). Login con `apify login -t <token>`. Comando base:
```powershell
echo '{"queries":["meta ads manager dashboard"],"maxResultsPerQuery":5,"imageSize":"large"}' | apify call hooli/google-images-scraper --silent --output-dataset
```
Protocolo: pedir validación a Diego ANTES de scrapear, máximo 5 imágenes/query, alta resolución, descargar a `fotos/` con nombres descriptivos.

## Relación con /historias-ig
Comparten brief y assets vía junctions/hard-links de Windows (configurados en setup inicial):
- **Junctions a carpetas:** `fotos/`, `logos/`, `fonts/`
- **Hard links a archivos:** `config.json`, `catalogo_detallado.json`, `.env`, `skill/biblioteca-contenido.md`

Editar el brief en uno → ambos lo ven. Las skills evolucionan independientes (scripts copiados, no linkeados).

## Claves
`KIE_AI_API_KEY` (fondos IA + edición), `APIFY_API_TOKEN` (scraping), Telegram (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`) en `.env` o `config.json`. Nunca subir secretos: `config.json`, `.env`, `fotos/`, `logos/`, `output/` están en `.gitignore`.

## Comandos
`/carruseles` (genera) · `reconfigurar` · `fotos` · `ver` · `enviar` (Telegram).
