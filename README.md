# 🎠 Carruseles IG Skill — Claude Code

> Genera **carruseles de Instagram profesionales (1080×1350, 4:5)** con un solo comando. Le dictas el tema, Claude elige la estructura narrativa REPTINAC, escribe el copy persuasivo con tu marca, genera fondos cinematográficos con IA, busca imágenes históricas en Apify cuando hace falta, y arma los 7–8 slides listos para publicar — junto con caption + 30 hashtags listos para copiar.

Skill creada y mantenida por **[Diego Osorio (@soydiegoosorio)](https://instagram.com/soydiegoosorio)**.

Hermana de [`historias-ig-skill`](https://github.com/diegodoc11/historias-ig-skill) (formato 9:16) — comparten brief, fotos y logos, pero cada una tiene su motor optimizado para su formato.

---

## ✨ ¿Qué hace?

A partir de un **tema + objetivo**, en una sola conversación con Claude obtienes:

1. **Elección automática del tipo REPTINAC** entre 8 fórmulas validadas (Engagement, Polarización, Transformación, Autoridad, Niveles de Consciencia, Conversión…)
2. **Copy persuasivo aplicado slide por slide** con la Capa de Persuasión: 4 ángulos (dolor · automatización · beneficio · resultado), especificidad numérica, antes/después, foco en el lector
3. **Slide 1 (cubierta) + Slide 2 (segundo hook) premium** con `nano-banana-pro` — porque Instagram re-impresiona la slide 2 a quienes ya pasaron por el carrusel
4. **Fondos IA cinematográficos** o **scraping Apify** según el tema (mockups de productos, imágenes históricas, etc.)
5. **Cutouts de personas con `rembg birefnet-general`** (state-of-the-art para detalles finos como dedos apuntando)
6. **Caption del post + 30 hashtags** listos para copiar a Instagram
7. **Envío directo a tu celular por Telegram** para publicar desde el móvil sin pasar por la nube

---

## 🆕 Features avanzadas (lo que la hace distinta a otras skills de IG)

| Feature | Qué resuelve |
|---|---|
| **Modo híbrido cover** (foto cutout + fondo IA) | Slide 1 con tu cara a un lado y un fondo cinematográfico al otro — look magazine editorial |
| **Modo "fit" con padding** (`foto_modo: "fit"`) | Para screenshots/dashboards que no encajan en 4:5 sin recortarse de los lados |
| **`pick_text_band` con detección de cara** | El motor analiza el alpha channel del cutout y NUNCA pone texto encima del sujeto |
| **`text_y_top` / `text_y_bottom` override** | Cuando una composición pre-hecha necesita banda de texto custom |
| **Composiciones pre-hechas** (`compose_*.py`) | Slide CTA con screenshot IG + cutout flotante. Cover split (2 personas confrontadas + fondo dramático) |
| **Apify CLI integrado** (`buscar_imagenes.py`) | Scraping de imágenes históricas/explicativas con workflow validado: máx 5 por query, alta resolución, presenta opciones para elegir |
| **Image-to-image con `kie_edit.py`** | Edita fotos con `nano-banana-pro` subiéndolas a un host público temporal |
| **Cache de fondos IA** (`cache_path`) | Reusa generaciones previas → iterar el mismo carrusel cuesta $0 |
| **Etiqueta de hook con opt-out** (`etiqueta: null`) | Quita la píldora superior cuando el slide no la necesita |
| **`resolve_foto_path()`** | El motor encuentra fotos en `fotos/_cutouts/`, `_compuestas/`, `_historicas/`, etc. — `plan.json` siempre refiere por nombre |
| **Catálogo curado con arcos narrativos** | 81 fotos clasificadas con su historia, zona segura de texto y mapeo REPTINAC |

---

## 📋 Requisitos

- [Claude Code](https://claude.com/claude-code) instalado
- **Python 3.10+** con `Pillow`, `requests`, `rembg[cpu]` (~970MB para el modelo birefnet la primera vez)
- **Node.js 18+** (para Apify CLI y el motor de Word de lead magnets, si los usas)
- macOS, Linux o **Windows** (probado en Windows nativo)
- *(Opcional)* Cuenta de [Kie AI](https://kie.ai) — fondos con IA, modelos `google/nano-banana` (~$0.02/img) y `nano-banana-pro` premium (~$0.12/img)
- *(Opcional)* Cuenta de [Apify](https://apify.com) — para scraping de imágenes complementarias (créditos gratis iniciales)
- *(Opcional)* Un bot de [Telegram](https://telegram.org) para recibir los sets en tu celular

---

## ⚡ Instalación

### Opción A — con Claude Code (recomendado)

Abre Claude Code, pega esto y envíalo:

```
Clona https://github.com/diegodoc11/carruseles-ig-skill.git en ~/carruseles-ig
y corre el setup automáticamente según mi sistema operativo
```

Cuando termine, **cierra y vuelve a abrir Claude Code** para que detecte la skill.

### Opción B — manual

```bash
git clone https://github.com/diegodoc11/carruseles-ig-skill.git ~/carruseles-ig
cd ~/carruseles-ig

# Dependencias Python
pip install Pillow requests "rembg[cpu]"

# Dependencias Node (para Apify CLI)
npm install -g apify-cli
```

Copia `.env.example` a `.env` y llena tus claves. Después reinicia Claude Code.

### Junctions a `historias-ig` (Windows, opcional)

Si ya tienes [`historias-ig-skill`](https://github.com/diegodoc11/historias-ig-skill) y quieres compartir brief y assets:

```powershell
$src = "$HOME\historias-ig"
$dst = "$HOME\carruseles-ig"
New-Item -ItemType Junction -Path "$dst\fonts" -Target "$src\fonts"
New-Item -ItemType Junction -Path "$dst\fotos" -Target "$src\fotos"
New-Item -ItemType Junction -Path "$dst\logos" -Target "$src\logos"
New-Item -ItemType HardLink -Path "$dst\config.json"             -Target "$src\config.json"
New-Item -ItemType HardLink -Path "$dst\catalogo_detallado.json" -Target "$src\catalogo_detallado.json"
New-Item -ItemType HardLink -Path "$dst\.env"                    -Target "$src\.env"
```

---

## 🔧 Configuración paso a paso

### 1) Kie AI (fondos con IA) — opcional pero muy recomendado

1. Crea cuenta en [https://kie.ai](https://kie.ai) (te da créditos gratis iniciales)
2. Copia tu API key
3. Pégala en `.env`:
   ```
   KIE_AI_API_KEY=tu_clave_aqui
   ```

### 2) Apify (scraping de imágenes) — opcional

1. Crea cuenta en [https://apify.com](https://apify.com)
2. Copia tu API token de [console.apify.com/account/integrations](https://console.apify.com/account/integrations)
3. Login local:
   ```bash
   apify login -t apify_api_TU_TOKEN
   ```

### 3) Telegram (recibir sets en tu celular) — opcional

1. En Telegram, abre **@BotFather**, comando `/newbot`, copia el **token**
2. Pégalo en `.env`:
   ```
   TELEGRAM_BOT_TOKEN=tu_token
   ```
3. Escríbele "hola" a tu bot. Después obtén tu chat_id:
   ```bash
   python scripts/telegram_enviar.py --proj-dir . --get-chat-id
   ```
4. Pégalo en `.env`:
   ```
   TELEGRAM_CHAT_ID=tu_chat_id
   ```

---

## 🎬 Uso

```
/carruseles
```

**La primera vez** te hace preguntas sobre tu marca (avatar, dolores del nicho, oferta, tono…). Después solo dile el **tema + objetivo** del día y genera el set en `output/`.

### Comandos auxiliares

| Comando | Qué hace |
|---|---|
| `/carruseles` | Genera el carrusel del día |
| `/carruseles reconfigurar` | Cambia los datos de tu marca |
| `/carruseles fotos` | Re-escanea tus fotos disponibles |
| `/carruseles ver` | Abre la última carpeta de output |
| `/carruseles enviar` | Manda el último set a tu Telegram |

### Flujo dentro de la conversación

```
Tú        : "carrusel sobre por qué la mayoría fracasa con IA"
Claude    : Lee tu brief → elige tipo REPTINAC (probablemente Polarización)
            Propone estructura de 7-8 slides
            Te muestra el COPY EXACTO de cada slide
            ⚠️ Espera tu aprobación ANTES de generar imágenes (Regla de Oro)
Tú        : "aprobado" o "cambia X en slide N"
Claude    : Identifica qué fotos del catálogo encajan
            Si hace falta scrapear con Apify, te pide validación
            Genera fondos IA con nano-banana-pro (slides 1-2) o nano-banana (resto)
            Renderiza los 8 PNGs a 1080×1350
            Escribe caption + 30 hashtags
            Manda todo a tu Telegram
```

---

## 📁 Estructura del proyecto

```
carruseles-ig/
├── fotos/                        ← FOTOS ORIGINALES tuyas (gitignored)
│   ├── _cutouts/                 ← Cutouts transparentes (rembg birefnet)
│   ├── _compuestas/              ← Composiciones de scripts (compose_*.py)
│   ├── _historicas/              ← Apify scraping seleccionado para usar
│   ├── _scraping/                ← Apify scraping crudo (todas las opciones)
│   └── _deprecated/              ← Intentos fallidos / versiones obsoletas
├── logos/                        ← Logos de marcas (Claude, Meta, Apify...) — gitignored
├── fonts/                        ← Space Grotesk
├── output/                       ← Los carruseles generados aparecen aquí
├── scripts/
│   ├── generate.py               ← Motor de generación (lee plan.json → 8 PNGs)
│   ├── utils.py                  ← Pipeline de imagen (load_bg cover|fit, fuentes, texto)
│   ├── scan_fotos.py             ← Escanea y cataloga tus fotos
│   ├── telegram_enviar.py        ← Envía un set + caption a Telegram
│   ├── compose_cta_bg.py         ← Compone fondo IA + screenshot IG como card editorial
│   ├── compose_iglesia_vs_ia.py  ← Ejemplo: cover split (2 cutouts confrontados + fondo dramático)
│   ├── kie_edit.py               ← Edita imágenes con nano-banana-pro (image-to-image)
│   ├── buscar_imagenes.py        ← Scraper Apify (google-images-scraper)
│   └── check_kie.py              ← Health check de la API de Kie
├── skill/
│   ├── carruseles.md             ← Cerebro de la skill (flujo, reglas, particularidades)
│   └── biblioteca-contenido.md   ← 8 tipos REPTINAC (compartida con historias-ig)
├── .env                          ← Tus claves (NO se sube a git)
├── config.json                   ← Tu brief de marca (gitignored)
├── catalogo_detallado.json       ← Catálogo curado con arcos narrativos (gitignored)
├── CLAUDE.md                     ← Guía técnica del proyecto
└── README.md                     ← Este archivo
```

> 🔒 **Privacidad:** `.env`, `config.json`, `catalogo_detallado.json`, `fotos/`, `logos/` y `output/` están en `.gitignore`. Tus claves, brief, fotos personales y carruseles generados **nunca** se suben a GitHub.

---

## 🎯 Particularidades del formato carrusel

La skill aplica automáticamente estas leyes del formato:

1. **El slide 1 decide.** Si no para el scroll, todo lo demás muere. Visual + copy muy fuerte.
2. **El slide 2 es el segundo hook.** Instagram lo re-impresiona a usuarios que ya pasaron por el carrusel — necesita su propio gancho (refuerzo de promesa, dolor, sueño). NO arrancar el ranking ahí.
3. **El último slide convierte.** CTA con palabra clave → DM.
4. **Sin barra de progreso interna.** Instagram ya muestra los puntitos del carrusel.
5. **Densidad de texto MAYOR que en historias.** La gente se queda más tiempo en cada slide.
6. **Save-worthy gana.** El algoritmo premia guardados y compartidos.
7. **Slide 1 + 2 con `nano-banana-pro`** (premium). Slides 3+ con `google/nano-banana` standard.
8. **El motor NUNCA tapa la cara** en cutouts transparentes (detección automática del alpha).

---

## 🪄 Sobre los cutouts (quitar fondo a fotos)

La skill usa **`rembg birefnet-general`** (state-of-the-art 2024, descarga ~970MB la primera vez).

**¿Por qué no usar el modelo default `u2net`?** Tiene un bug conocido: los **dedos delgados** salen semi-transparentes contra fondos oscuros. Síntoma: dedo "fantasmal" que deja ver el fondo a través. `birefnet-general` arregla esto.

```python
from rembg import remove, new_session
session = new_session("birefnet-general")
with open("foto.jpg", "rb") as f:
    out = remove(f.read(), session=session)
```

Resultado va a `fotos/_cutouts/<nombre>.png` y se usa con `foto_cutout: "<nombre>.png"` en el plan.

---

## 🔍 Sobre el scraping con Apify (imágenes complementarias)

Cuando un slide necesita una imagen **real explicativa** (un mockup de Claude Code, una pintura histórica, un dashboard real…), la skill usa **Apify** con el actor `hooli/google-images-scraper`.

### Protocolo obligatorio (definido en `skill/carruseles.md`)

1. **Primero el copy completo** — Regla de Oro se aplica también aquí
2. **Identificar qué slides necesitan imagen real** vs cuáles funcionan con fondo IA conceptual
3. **Pedir validación a Diego** antes de scrapear: *"Para el slide N propongo scrapear con query X. ¿Procedo?"*
4. **Queries específicas, no genéricas:** `Galileo Galilei trial Inquisition 1633 historical painting` (no `galileo`)
5. **Máximo 5 imágenes por query**, `imageSize: large`
6. **Descargar a `fotos/_scraping/<query>/`** y mostrar opciones para elegir

```bash
python scripts/buscar_imagenes.py \
  --proj-dir . \
  --query "Pope Francis official portrait Vatican|Pope Leo XIV official portrait" \
  --label "papa" \
  --max 4
```

---

## 💰 Costos típicos por carrusel

| Concepto | Costo |
|---|---|
| 2 fondos IA premium (slides 1+2 con `nano-banana-pro`) | ~$0.24 USD |
| 5 fondos IA standard (slides 3-7 con `google/nano-banana`) | ~$0.10 USD |
| 1 composición editorial (`compose_cta_bg.py`) | ~$0.12 USD |
| Apify scraping (4-5 queries) | ~$0.00 (créditos gratis iniciales) |
| **Total carrusel completo** | **~$0.46 USD** |

**Reutilización con `cache_path`:** iterar el mismo carrusel cuesta **$0** (reusa fondos generados previamente).

### Recarga de créditos Kie sugerida

| Si recargas… | Te alcanza para… |
|---|---|
| $5 USD | ~3-4 carruseles completos |
| $10 USD | ~7-8 carruseles |
| $20 USD | 1 mes de contenido (15+ carruseles) |

---

## ⚠️ Limitaciones honestas (qué funciona y qué no)

Esta skill ha producido carruseles publicables, pero NO es magia. Después de iterar 3 carruseles distintos, estas son las limitaciones reales:

### ✅ Lo que la skill hace MUY BIEN (úsala así)
- **Slide 1 con cover híbrido**: cutout tuyo a un lado + fondo IA cinematográfico al otro
- **Slide 2 con fondo IA premium**: refuerzo de hook con `nano-banana-pro`
- **Slides 3-7 con fotos del catálogo** + datos persuasivos
- **Slide CTA editorial**: screenshot IG + cutout apuntando + caja con palabra clave
- **Caption + 30 hashtags** automáticos coherentes con el carrusel
- **Apify scraping** para imágenes históricas/culturales clásicas

### ❌ Lo que tiende a fallar (evita pedirlo así)
- **Split vertical (foto arriba + foto abajo)** con personas en ambas mitades → los cuerpos se confunden y Claude no logra el balance visual al primer intento. Mejor split LATERAL (izq/der).
- **Sobreponer stickers/iconos pequeños sobre tu cara** → Claude no tiene intuición de diseñador y mete elementos donde tapan caras. Hay que validar SLIDE por SLIDE después de renderizar.
- **Editar fotos con IA** (quitar un objeto, cambiar a dark mode, etc.) → los modelos generativos reinterpretan en lugar de editar pixel-perfect. Mejor usar Photoshop / Photopea / la app del celular.

### 🎯 Cómo obtener el mejor resultado
1. **Aprueba el COPY antes que las imágenes** (Regla de Oro de la skill)
2. **Cuando un slide te guste, dile "aprobado"** — la skill marca esa versión y NO la toca
3. **Si algo NO te convence visualmente**, dilo CLARO ("muévelo a la esquina inferior", "no tapes mi cara", etc.) — Claude no lo ve solo
4. **Para slide 1 usa siempre cover híbrido** con cutout + fondo IA premium — es el approach con mejor track record

---

## 🚨 Aprendizajes importantes (lecciones de este proyecto)

### Lo que NO funciona

- ❌ **Image-to-image con `nano-banana-pro` para preservar identidad** — la IA "reimagina" la imagen en lugar de editar pixel-perfect. Resultados: caras alteradas, textos truncados, números cambiados. Solo úsalo para edits simples sin contenido crítico.
- ❌ **El modelo `u2net` de rembg para dedos** — bug del alpha en bordes finos contra fondos oscuros. Usar siempre `birefnet-general`.
- ❌ **Highlight en TextRun de docx-js** — genera elemento `w:highlightCs` inválido en el schema XML. Usar color + bold + italic en su lugar.

### Lo que SÍ funciona

- ✅ **Fondos IA cinematográficos premium para slides 1 y 2** — `nano-banana-pro` brilla cuando se le pide ambiente/atmósfera (cityscape, ruinas, catedral) sin elementos que tenga que "respetar".
- ✅ **Apify para imágenes históricas clásicas** — pinturas de dominio público, ukiyo-e, retratos de figuras históricas. Resultados muy buenos.
- ✅ **`cache_path` en el plan.json** — ahorra dinero al iterar.
- ✅ **Composiciones pre-hechas (`compose_*.py`)** — control total del layout cuando el motor no alcanza (slide CTA editorial, cover split).
- ✅ **`birefnet-general` para cutouts** — calidad state-of-the-art con dedos definidos, pelo limpio.

---

## 🪟 Notas para Windows

- Usa **siempre** `python -X utf8` cuando ejecutes scripts (la consola Windows no es UTF-8 por defecto).
- Si "Python no encontrado" aunque lo tengas instalado, desactiva los *alias de la Microsoft Store*: Configuración → Aplicaciones → Alias de ejecución de aplicaciones → apaga `python.exe` y `python3.exe`.
- Junctions/hard-links se crean con `New-Item -ItemType Junction|HardLink` (no requiere admin en Windows 10+).

---

## 🙏 Créditos

Creada y mantenida por **[Diego Osorio — @soydiegoosorio](https://instagram.com/soydiegoosorio)**.

Esta skill es parte de un stack de herramientas con IA que usa Diego (más de **209 mil seguidores** en Instagram, **+$1 Millón USD vendidos**, **+$300K invertidos** en negocios). Junto con [`historias-ig-skill`](https://github.com/diegodoc11/historias-ig-skill) y las otras automatizaciones, le permite producir contenido como un equipo de 10 trabajando solo unas horas al día.

> *"No soy el más inteligente. La IA me dio superpoderes."* — Diego

Si esta skill te sirve, sígueme en [@soydiegoosorio](https://instagram.com/soydiegoosorio) para más automatizaciones con IA, guías paso a paso y mi comunidad **Imperio** donde están las plantillas listas para usar. 🚀
