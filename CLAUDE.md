# CLAUDE.md — Guía del proyecto

Generador de **carruseles de Instagram (1080×1350, 4:5)** para Claude Code. El usuario dicta un tema; la skill elige el tipo REPTINAC, escribe el copy persuasivo, gestiona fondos IA + scraping Apify + composiciones editoriales, y renderiza los 7–8 slides listos para publicar. Hermana de `/historias-ig` (formato 9:16) — comparten brief, fotos, logos y biblioteca de contenido vía junctions/hard links.

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
skill/carruseles.md             ← Cerebro de la skill (flujo, onboarding, reglas)
skill/biblioteca-contenido.md   ← 8 tipos REPTINAC (compartida con historias-ig via hard link)
scripts/generate.py             ← Motor de render (lee plan.json → PNG 1080×1350) + resolve_foto_path()
scripts/utils.py                ← Pipeline de imagen (load_bg cover|fit, fondos, texto)
scripts/scan_fotos.py           ← Cataloga fotos/ → catalogo.json
scripts/telegram_enviar.py      ← Envía set al celular + caption con --mensaje-final
scripts/compose_cta_bg.py       ← Compone fondo IA + screenshot como card → fotos/_compuestas/
scripts/compose_iglesia_vs_ia.py ← Ejemplo: cover split (2 cutouts + fondo dramático) → fotos/_compuestas/
scripts/kie_edit.py             ← Edita imágenes con nano-banana-pro (image-to-image)
scripts/buscar_imagenes.py      ← Scraper Apify (google-images-scraper) → fotos/_scraping/<query>/
scripts/check_kie.py            ← Health check de la API de Kie
config.json                     ← Marca + brief (privado, en .gitignore)
catalogo_detallado.json         ← Catálogo curado con arcos narrativos (gitignored — contiene historia personal)
fotos/                          ← FOTOS ORIGINALES (intactas)
  ├── _cutouts/                 ← Cutouts transparentes (rembg birefnet-general)
  ├── _compuestas/              ← Composiciones de scripts (compose_*.py)
  ├── _historicas/              ← Apify scraping seleccionado para uso editorial
  ├── _scraping/                ← Apify scraping crudo (todas las opciones por query)
  └── _deprecated/              ← Intentos fallidos / versiones obsoletas
logos/ fonts/ output/           (todos en .gitignore)
```

**Regla de carpetas:** las fotos de Diego viven en `fotos/` raíz. Todo lo que GENERA o DESCARGA la skill va a una subcarpeta con prefijo `_`. El motor tiene `resolve_foto_path()` que busca automáticamente en todas las subcarpetas — en el `plan.json` basta poner el nombre del archivo sin path.

## Flujo de generación
1. Leer `config.json` (marca + brief). Si no existe → onboarding (ver `skill/carruseles.md`).
2. Pedir **tema + objetivo**.
3. Leer `skill/biblioteca-contenido.md` y elegir **tipo REPTINAC** (priorizar los que brillan en carrusel: Transformación, Engagement Top N, Polarización, Autoridad, Niveles de Consciencia, Conversión).
4. Si existe `catalogo_detallado.json`, consultarlo para **identificar fotos del catálogo** que encajen con el tema (mapeo `_mapeo_uso_estrategico` y `_recomendaciones_por_tipo_REPTINAC`).
5. Si hace falta scraping (mockups reales, imágenes históricas), seguir protocolo Apify (validar query con usuario antes de scrapear).
6. Escribir el **plan.json** (un objeto por slide) y **mostrar el copy para aprobación**.
7. Tras el OK: `python scripts/generate.py --plan plan.json --proj-dir .`
8. Mostrar resultados y ofrecer envío por Telegram (`telegram_enviar.py` con `--mensaje-final caption.md`).

## Schema del plan (campos por slide)

### Básicos
- `tipo`: `hook` para slide 1, `cta` para último; descriptivo para intermedios (`refuerzo`, `puesto5`, `mito`, `ejemplo_*`, etc).
- `titulo`, `subtitulo`, `texto_extra`.
- `foto`: nombre de archivo (el motor resuelve la subcarpeta).
- `fondo_ia`: objeto `{prompt, model, cache_path}`. Modelo: `"google/nano-banana"` standard | `"nano-banana-pro"` premium.
- `texto_pos`: `"auto"` (default) | `"top"` | `"center"` | `"bottom"`.
- `text_y_top` / `text_y_bottom`: override de banda de texto (útil cuando una composición tiene cutouts que chocan con la banda automática).
- `etiqueta`: (solo hook) píldora superior. `null` = opt-out explícito (no dibujar). Ausente del slide = usar default del config.
- `palabras_clave`, `logos`, `cta_palabra`, `cta_verbo`.

### Modo híbrido (slide hook con foto cutout + fondo IA combinados)
- `foto_lado`: `"right"` (default) | `"left"`.
- `foto_escala`: 0.0–1.0 (default 0.85).
- `foto_offset`: pixels del borde lateral (default 60).

### Foto como fondo (modo cover|fit)
- `foto_modo`: `"cover"` (default, llena el lienzo) | `"fit"` (entra entera con padding negro).
- `foto_y_pos`: `"top"` | `"center"` | `"bottom"` (solo aplica en modo fit).
- `foto_darken`: 0.0–1.0 (default 0.55). Subir para fotos busy (screenshot, dashboard).
- `aplicar_gradient`: bool (default true). False cuando la foto ya viene con gradient pre-compuesto.

### Cutout sobrepuesto adicional (foto_cutout)
- `foto_cutout`: nombre de archivo (preferiblemente transparente — usar `rembg` con `birefnet-general`).
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
- **Resolución de paths:** `resolve_foto_path()` busca en `fotos/` → `_compuestas/` → `_cutouts/` → `_historicas/` → `_deprecated/` → `_scraping/*/`.
- **Chips de marca:** `logos:[...]` usa `logos/<slug>.png` si existe; si no, muestra el nombre como pill blanco.
- **CTA:** `Comenta [PALABRA] y te envío [recurso]`. Palabra en MAYÚSCULAS, 3–8 letras, sin acentos (regla flexible — Diego usa "AUTOMATIZAR" 11 letras o "SUPERPODER" 10).
- **Ejecutar siempre con** `python -X utf8` (la consola Windows puede no ser UTF-8).

## Pipeline avanzado

### Composiciones pre-hechas (compose_*.py)
Cuando el motor no alcanza para un layout específico, los scripts `compose_*.py` componen elementos manualmente y guardan el resultado en `fotos/_compuestas/`. Después se referencian normal en el plan.

- **`compose_cta_bg.py`** — genera fondo IA cinematográfico con `nano-banana-pro` y compone el screenshot de IG como banner full-width con sombra inferior para slides CTA con prueba social.
- **`compose_iglesia_vs_ia.py`** — ejemplo de cover split: 2 cutouts (Papa Leo XIV + Diego) sobre fondo cinematográfico dramático (catedral vs servidores). Reutilizable para covers tipo "X vs Diego".

### Edición de imágenes con IA (kie_edit.py)
`scripts/kie_edit.py` permite editar una imagen local con `nano-banana-pro` (image-to-image). Sube la imagen a un host público (catbox.moe → tmpfiles.org → 0x0.st con fallback) y llama al endpoint con `image_urls`.

⚠️ **Advertencia importante:** los modelos generativos pueden alterar caras, textos y números. Útil para edits simples sin contenido crítico. **NO sirve para preservar identidad/contenido exacto** — la IA "reimagina" en lugar de editar pixel-perfect. Lecciones de este proyecto:
- Intento dark mode del screenshot IG → la IA cambió el avatar y truncó textos
- Intento quitar lanyard del cutout → la IA cambió aspect ratio y reinterpretó la camisa

### Cutouts con rembg
Modelo por defecto: **`birefnet-general`** (~970MB, state-of-the-art 2024). Esencial para detalles finos como dedos apuntando. El modelo `u2net` (default de rembg) causa dedos semi-transparentes contra fondos oscuros.

```python
from rembg import remove, new_session
session = new_session("birefnet-general")
out = remove(input_bytes, session=session)
```

Guardar el resultado en `fotos/_cutouts/<nombre>.png`.

### Apify CLI (workflow de scraping)
Instalado vía npm. Para scraping de imágenes complementarias (mockups reales de productos, logos no incluidos en `logos/`, imágenes históricas). Login con `apify login -t <token>`. Comando base:

```bash
python scripts/buscar_imagenes.py \
  --proj-dir . \
  --query "<query específica>|<query alternativa>" \
  --label "<carpeta>" \
  --max 5
```

**Protocolo obligatorio** (documentado en `skill/carruseles.md`):
1. Mostrar copy completo PRIMERO (Regla de Oro)
2. Identificar qué slides necesitan imagen real explicativa (vs fondo IA conceptual)
3. Pedir validación al usuario antes de scrapear con queries específicas
4. Máximo 5 imágenes por query, `imageSize: large`
5. Descargar a `fotos/_scraping/<label>/` y mostrar opciones para elegir
6. Mover las seleccionadas a `fotos/_historicas/` con nombres descriptivos

## Relación con /historias-ig
Comparten brief y assets vía junctions/hard-links de Windows (configurados en setup inicial):
- **Junctions a carpetas:** `fotos/`, `logos/`, `fonts/`
- **Hard links a archivos:** `config.json`, `catalogo_detallado.json`, `.env`, `skill/biblioteca-contenido.md`

Editar el brief en uno → ambos lo ven. Las skills evolucionan independientes (scripts copiados, no linkeados).

## Catálogo de fotos curado (catalogo_detallado.json)
Archivo central que mapea cada foto del usuario con:
- **Contenido visual** (qué muestra)
- **Zona segura para texto** (🟢 fácil / 🟡 limitada / 🔴 difícil)
- **Vibe y mejor uso** (hook aspiracional / autoridad / humanización / etc.)
- **Arcos narrativos asociados** (cada foto pertenece a uno o más arcos de la historia personal del usuario)
- **Mapeo REPTINAC → fotos sugeridas** (qué fotos usar para cada tipo de contenido)
- **Frases marca** (banco de citas reutilizables del usuario)
- **Categorías y subcarpetas** (estructura de `fotos/_*`)

Este archivo es lo que permite que cuando el usuario diga *"hazme un carrusel sobre X"*, Claude pueda **identificar inmediatamente qué fotos del banco usar + qué frases del usuario integrar** sin tener que preguntar foto por foto.

## Claves
`KIE_AI_API_KEY` (fondos IA + edición), Apify (auto-cargado de `~/.apify/auth.json` después de `apify login`), Telegram (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`) en `.env` o `config.json`. Nunca subir secretos: `config.json`, `.env`, `catalogo_detallado.json`, `fotos/`, `logos/`, `output/` están en `.gitignore`.

## Comandos
`/carruseles` (genera) · `reconfigurar` · `fotos` · `ver` · `enviar` (Telegram).

## ⚠️ LIMITACIONES CONOCIDAS (lo que Claude NO puede hacer bien)

Esta skill produjo 3 carruseles publicables. Estas son las limitaciones honestas, documentadas tras múltiples iteraciones:

### Lo que SÍ funciona consistentemente
- **Split lateral (izq/derecha) con cutouts + fondo IA premium** — ej: Papa cutout izq + Diego cutout der + catedral/servidores
- **Cover híbrido nativo del motor** (foto cutout + fondo IA)
- **Fondos IA cinematográficos** con `nano-banana-pro` (atmósferas sin gente)
- **Composición editorial CTA** con screenshot IG + cutout apuntando
- **Apify scraping** para imágenes históricas/culturales clásicas (pinturas dominio público, ukiyo-e)
- **Cutouts con `birefnet-general`** (no `u2net` — bug del dedo fantasmal)

### Lo que NO funciona (Claude tiende a fallar)
- **Split vertical (arriba/abajo) con composiciones complejas** — los cuerpos se confunden, requiere 6+ iteraciones
- **Sobreponer elementos pequeños sobre caras** — Claude no tiene intuición visual del diseñador y mete stickers/iconos donde tapan caras
- **Image-to-image con `nano-banana-pro` para preservar identidad** — el modelo es generativo, no editor pixel-perfect. Cambia caras y textos
- **Asumir "le va a quedar bien" sin validar** — siempre aplicar el checklist post-render del skill brain

### Reglas operativas críticas
1. **REGLA SAGRADA**: NUNCA tapar la cara del sujeto con texto, logo, cutout, sticker. Antes de posicionar cualquier elemento sobrepuesto, identificar la zona de la cara y validar que no haya solape.
2. **REGLA DE VERSIONES APROBADAS**: cuando el usuario dice "me gustó" o "dejémoslo así", COPIAR la imagen a `fotos/_compuestas/<nombre>_aprobado.png` y referenciarla. NO regenerar.
3. **REGLA DE ORO**: NUNCA generar imágenes sin que el usuario apruebe el copy slide por slide.

Estas reglas están documentadas más en detalle en `skill/carruseles.md`.

---

## Lecciones de este proyecto (lo que aprendimos)
- ✅ **Modo ILUSTRATIVO de fondos IA (gran salto):** el `fondo_ia` debe ILUSTRAR lo que dice el texto del slide con un personaje/mascota consistente (ej. robotsitos Pixar con su herramienta: ícono de Instagram, megáfono, teléfono) y la mitad inferior despejada para el texto. Mucho más claro y vendedor que fondos genéricos. Guía completa en `skill/carruseles.md` → "Modo ILUSTRATIVO". Validado en el carrusel "Tu equipo de IAs / Imperio".
- ✅ **Cache de fondos IA** (`cache_path`) ahorra mucho dinero al iterar el mismo carrusel — un bug del cache_path costó $0.60 USD en regeneraciones innecesarias en el carrusel "Iglesia vs IA" (ya arreglado).
- ✅ **Apify funciona excelente para imágenes históricas clásicas** (pinturas dominio público, ukiyo-e, retratos de figuras públicas como el Papa). Resultados muy buenos con queries específicas + `maxResultsPerQuery: 4-5`.
- ✅ **`birefnet-general` resuelve el bug del dedo fantasmal** que tenía `u2net` con cutouts contra fondos oscuros.
- ✅ **Composiciones pre-hechas (`compose_*.py`)** son la mejor manera de lograr layouts que el motor no puede hacer (slide CTA con prueba social, cover split de 2 personas, etc.).
- ❌ **Image-to-image con `nano-banana-pro` NO sirve para preservar identidad/textos exactos** — el modelo reimagina en lugar de editar. Útil solo para edits simples.
- ❌ **Highlight de TextRun en docx-js** genera `w:highlightCs` inválido — usar color + bold + italic en su lugar.
- 💸 **Costo típico de un carrusel completo: ~$0.50 USD.** Iteración con cache: $0. Lección: usar `cache_path` religiosamente.
