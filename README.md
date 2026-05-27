# 🎠 Carruseles IG Skill — Claude Code

> Genera **carruseles de Instagram profesionales (1080×1350, 4:5)** con un solo comando en Claude Code. Le dictas el tema, Claude elige la estructura narrativa REPTINAC, escribe el copy persuasivo, genera los fondos con IA y arma los 7–8 slides listos para publicar.

Skill creada y mantenida por **[Diego Osorio (@soydiegoosorio)](https://instagram.com/soydiegoosorio)**.

Hermana de [`historias-ig-skill`](https://github.com/diegodoc11/historias-ig-skill) (formato 9:16) — comparten brief, fotos y logos, pero cada una tiene su propio motor optimizado para su formato.

---

## ✨ ¿Qué hace?

A partir de un tema, genera **7–8 slides 4:5 listos para publicar** con:

- 🧠 **Estructura narrativa** elegida automáticamente entre 8 tipos REPTINAC (Engagement, Polarización, Transformación, Autoridad, etc.).
- 🎯 **Slide 1 + Slide 2 con doble gancho** — el slide 1 es la portada que para el scroll, el slide 2 es el segundo gancho que IG re-impresiona a quienes ya pasaron por tu carrusel.
- ✍️ **Copy persuasivo** con 4 ángulos (dolor · automatización · beneficio · resultado concreto), foco en el lector, especificidad numérica.
- 🖼️ **Fondos** generados con IA (Kie AI) — `google/nano-banana` económico para el ranking, **`nano-banana-pro` premium** para los slides 1 y 2 críticos.
- 🪄 **Cutouts editoriales** con `rembg birefnet-general` (state-of-the-art para detalles finos como dedos apuntando).
- 🎨 Tipografía Space Grotesk con tus colores de marca, consistente en TODOS los slides.
- 🔑 **Palabra clave de CTA** lista para tu automatización de DMs.
- 📲 **Envío a Telegram** para subir desde el celular sin pasar por la nube.

---

## 🆕 Mejoras únicas de esta skill (vs `historias-ig-skill`)

| Feature | Detalle |
|---|---|
| **Modo híbrido cover** | Slide 1 con foto cutout a un lado + fondo IA al otro, texto sobre gradient — look magazine editorial. |
| **Modo "fit" con padding** | Para screenshots que no encajan en 4:5 sin recortarse de los lados (`foto_modo: "fit"`). |
| **Cutout sin frame + sombra natural** | Sobreposición editorial estilo Skai (vs polaroid rectangular). |
| **Composiciones pre-hechas** | `compose_cta_bg.py` integra fondo IA cinematográfico + screenshot como card flotante. |
| **Image-to-image editing** | `kie_edit.py` para editar fotos con `nano-banana-pro` (sube a host público + llama API). |
| **Detección automática de cara** | `pick_text_band` analiza el canal alpha del cutout y evita la zona del sujeto. |
| **Tamaños de CTA configurables** | `cta_title_size`, `cta_box_w`, `cta_kw_size`, etc. ajustables por slide. |
| **Cache de fondos IA** | `cache_path` reusa generaciones previas sin gastar Kie. |
| **Apify CLI integrado** | Para scraping de imágenes reales complementarias (mockups, logos faltantes). |

---

## 📋 Requisitos

- [Claude Code](https://claude.com/claude-code) instalado
- **Python 3.10+** con `Pillow`, `requests`, `rembg[cpu]`
- **Node.js** (para Apify CLI vía npm)
- macOS, Linux o **Windows** (probado nativo)
- *(Opcional)* Cuenta de [Kie AI](https://kie.ai) para fondos con IA (sin Kie funciona con fondos sólidos)
- *(Opcional)* Un bot de [Telegram](https://telegram.org) para recibir los sets en tu celular
- *(Opcional)* Cuenta de [Apify](https://apify.com) para scraping de imágenes complementarias

---

## ⚡ Instalación

### Opción A — con Claude Code (recomendado)

Abre Claude Code, pega esto y envíalo:

```
Clona https://github.com/diegodoc11/carruseles-ig-skill.git en ~/carruseles-ig y corre el setup automáticamente según mi sistema operativo
```

Cuando termine, **cierra y vuelve a abrir Claude Code** para que detecte el skill.

### Opción B — manual

```bash
git clone https://github.com/diegodoc11/carruseles-ig-skill.git ~/carruseles-ig
cd ~/carruseles-ig
pip install Pillow requests "rembg[cpu]"
npm install -g apify-cli
```

Reinicia Claude Code para que aparezca el comando `/carruseles`.

### Junctions a `historias-ig` (Windows, opcional)

Si ya tienes [`historias-ig-skill`](https://github.com/diegodoc11/historias-ig-skill) instalado y quieres compartir el brief y los assets:

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

Editar el brief en cualquiera de los dos proyectos lo actualiza en el otro automáticamente.

---

## 🔧 Configuración

### Kie AI (fondos con IA)
Copia `.env.example` a `.env` y agrega tu clave:
```
KIE_AI_API_KEY=tu_clave_aqui
```

### Apify (scraping de imágenes complementarias)
```bash
apify login -t apify_api_TU_TOKEN
```
El token se guarda en `~/.apify/auth.json`.

### Telegram (recibir los sets en tu celular)
1. En Telegram, crea un bot con **@BotFather** (`/newbot`) y copia el **token**.
2. Pégalo en `.env`:
   ```
   TELEGRAM_BOT_TOKEN=tu_token_aqui
   ```
3. Escríbele "hola" a tu bot y obtén tu *chat id*:
   ```bash
   python scripts/telegram_enviar.py --proj-dir . --get-chat-id
   ```
4. Pega el chat id en `.env` (`TELEGRAM_CHAT_ID=...`).

---

## 🎬 Uso

```
/carruseles
```

La **primera vez** te hace preguntas sobre tu marca (si no comparte config con `historias-ig`). Después, solo dile el **tema + objetivo** del día y genera el set en `output/`.

| Comando | Qué hace |
|---|---|
| `/carruseles` | Genera el carrusel del día |
| `/carruseles reconfigurar` | Cambia los datos de tu marca |
| `/carruseles fotos` | Re-escanea tus fotos disponibles |
| `/carruseles ver` | Abre la última carpeta de output |
| `/carruseles enviar` | Manda el último set a tu Telegram |

---

## 📁 Estructura

```
carruseles-ig/
├── fotos/               ← Pon aquí tus fotos (JPG, PNG, WEBP) — gitignored
├── logos/               ← Logos de marcas (Claude, Meta, etc) — gitignored
├── fonts/               ← Space Grotesk — gitignored
├── output/              ← Los carruseles generados aparecen aquí
├── scripts/
│   ├── generate.py            ← Motor de generación (lee plan.json → 8 PNGs)
│   ├── utils.py               ← Pipeline de imagen (load_bg cover|fit, fuentes, texto)
│   ├── scan_fotos.py          ← Escanea y cataloga tus fotos
│   ├── telegram_enviar.py     ← Envía un set a tu celular vía Telegram
│   ├── compose_cta_bg.py      ← Compone fondo IA premium + screenshot como card flotante
│   └── kie_edit.py            ← Edita imágenes con nano-banana-pro (image-to-image)
├── skill/
│   ├── carruseles.md          ← El skill de Claude Code (cerebro)
│   └── biblioteca-contenido.md← 8 tipos REPTINAC (compartida con historias-ig vía hard link)
├── .env                       ← Tus claves (NO se sube a git)
├── config.json                ← Tu configuración de marca (gitignored)
├── CLAUDE.md                  ← Guía técnica del proyecto
└── README.md                  ← Este archivo
```

> 🔒 **Privacidad:** `.env`, `config.json`, `fotos/`, `logos/` y `output/` están en `.gitignore`. Tus claves, marca y fotos **nunca** se suben a GitHub.

---

## 🎯 Particularidades del formato carrusel (vs historias)

Carruseles tienen reglas de diseño distintas a historias. La skill las aplica automáticamente:

1. **Sin barra de progreso interna** — Instagram ya muestra los puntitos del carrusel debajo.
2. **Slide 1 = portada** decide si la gente desliza o no. Visual + copy muy fuerte.
3. **Slide 2 = segundo hook** — IG lo re-impresiona a usuarios que ya vieron tu carrusel como recordatorio. Tiene que ser su propio gancho de curiosidad/refuerzo (no arrancar el ranking ahí).
4. **Densidad de texto permitida MAYOR** — la gente se queda más tiempo en cada slide.
5. **Save-worthy gana** — el algoritmo de IG premia guardados y compartidos. Cada slide debe sumar valor.
6. **El motor NUNCA tapa la cara** en cutouts transparentes — analiza el alpha channel y elige una banda libre.

---

## 💰 Costos típicos por carrusel

| Concepto | Costo |
|---|---|
| 5 fondos IA standard (`google/nano-banana`) | ~$0.10 USD |
| 2 fondos IA premium para slide 1 y 2 (`nano-banana-pro`) | ~$0.24 USD |
| 1 composición editorial (`compose_cta_bg.py`) | ~$0.12 USD |
| **Total típico carrusel completo** | **~$0.46 USD** |

Reusar fondos previos con `cache_path` = $0. La skill automáticamente reusa caches cuando aplica.

---

## 🪟 Nota para Windows

- Usa **siempre** `python -X utf8` cuando ejecutes scripts (la consola Windows no es UTF-8 por defecto).
- Si "Python no encontrado" aunque lo tengas instalado, desactiva los *alias de la Microsoft Store*: **Configuración → Aplicaciones → Alias de ejecución de aplicaciones →** apaga `python.exe` y `python3.exe`. O instala Python desde [python.org](https://python.org) marcando "Add to PATH".
- Junctions/hard-links se crean con `New-Item -ItemType Junction|HardLink` (no requiere admin en Windows 10+).

---

## 🙏 Créditos

Creada y mantenida por **[Diego Osorio — @soydiegoosorio](https://instagram.com/soydiegoosorio)**.

Esta skill es parte de un stack de herramientas que uso para gestionar mi marca personal en Instagram (209k seguidores). Junto con [`historias-ig-skill`](https://github.com/diegodoc11/historias-ig-skill) y mis otras automatizaciones con IA, me permite producir contenido como un equipo de 10 trabajando solo unas horas al día.

Si esta skill te sirve, sígueme en [@soydiegoosorio](https://instagram.com/soydiegoosorio) para más automatizaciones con IA y guías paso a paso. 🚀
