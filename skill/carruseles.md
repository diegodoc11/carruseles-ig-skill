# /carruseles — Generador de Carruseles de Instagram (4:5)

Genera **carruseles de Instagram (1080×1350)** eligiendo el **tipo de contenido** y la **estructura persuasiva** más adecuados al objetivo del día, usando la Biblioteca de Contenido. Hermana de `/historias-ig` (formato 9:16); comparte brief, fotos y logos pero tiene motor y cerebro propios.

**Directorio del proyecto:** `{{PROJ_DIR}}`
**Biblioteca de contenido:** `{{PROJ_DIR}}/skill/biblioteca-contenido.md`

---

## 🎯 PARTICULARIDADES DEL FORMATO CARRUSEL

Antes de planear copy, ten estas leyes en mente:

1. **La portada decide.** El slide 1 tiene que pegar muy fuerte (gancho + visual). Si no, no deslizan y todo lo demás muere.
2. **El slide 2 es el SEGUNDO hook.** Instagram lo usa para re-impresiones: a quienes ya vieron tu carrusel les vuelve a aparecer la slide 2 como recordatorio. Tiene que tener su propio gancho de curiosidad, refuerzo de promesa, dolor o sueño. NO lo trates como un slide más de desarrollo.
3. **El último slide convierte.** Siempre CTA con palabra clave → DM. Es ahí donde se cobra el alcance.
4. **Save-worthy gana.** El algoritmo de IG premia guardados y compartidos más que likes. Cada slide debe sumar valor: nada de relleno.
5. **Densidad permitida MAYOR que en historias.** La gente se queda más tiempo en cada slide del carrusel → puedes escribir más texto sin ser "muro".
6. **Sin barra de progreso interna.** Instagram ya muestra los puntitos abajo; el motor de carrusel los omite a propósito.
7. **7–8 slides por defecto** (rango sano 5–10). Estructura típica: cubierta + (slide 2 de refuerzo opcional) + 5 contenido + CTA.
8. **Slide 1 y 2 con `nano-banana-pro`** (modelo premium, ~$0.12/img) porque son los más vistos. Los slides 3+ con `google/nano-banana` standard (~$0.02/img) está bien.
9. **El motor NUNCA tapa la cara con texto** en fotos cutout transparentes: `pick_text_band` detecta el contenido del alpha channel y elige la banda con menos contenido del sujeto. Si esto falla, fuerza `texto_pos: "bottom"` (o "top") en el slide.

---

## FLUJO PRINCIPAL

### Al invocar `/carruseles`

**Paso 1 — Verificar configuración**

Lee `{{PROJ_DIR}}/config.json`. Si no existe, ejecuta el **ONBOARDING** (ver abajo). Si existe (caso normal en este proyecto: viene hard-linkeado de `historias-ig`), salta al paso 2.

**Paso 2 — Pedir tema y objetivo**

Pregunta al usuario en un solo mensaje:
> "¿Cuál es el tema del carrusel? ¿Y qué objetivo buscas?"
>
> Objetivo — elige uno:
> - **Enseñar algo accionable (paso a paso, guardable)** — Transformación
> - **Alcance / ranking / Top N** — Engagement
> - **Romper un mito / diferenciarme** — Polarización
> - **Posicionarme con un caso o datos** — Autoridad
> - **Mover hacia la compra** — Niveles de Consciencia
> - **Vender / resolver objeciones** — Conversión
> - **Libre** — Claude elige el tipo

Si el usuario no especifica objetivo, infiérelo del tema.

> 📌 **Nota:** Los tipos Relacionamiento e Interacción 1×1 también funcionan en carrusel, pero brillan más en historias. Si el usuario los pide, sugiere honestamente: "esto suele rendir más como historia, ¿lo hacemos en `/historias-ig` o forzamos carrusel?"

**Paso 3 — Elegir el tipo de contenido (Biblioteca)**

**Lee `{{PROJ_DIR}}/skill/biblioteca-contenido.md`.** Con el tema + objetivo, usa la tabla "objetivo → tipo" para elegir el **tipo REPTINAC**. Toma de ahí su **estructura slide-por-slide**, su **ángulo de persuasión** y su **mecánica de interacción/CTA**.

Presenta al usuario:
> "Voy a usar **[TIPO]** ([para qué sirve]). Estructura: [flujo en una línea]. Slides: 7 (cubierta + 5 contenido + CTA). ¿Continuamos? ¿O ajustamos el número de slides?"

Si pide otro tipo, ofrece 2–3 alternativas justificadas.

**Paso 4 — Escanear fotos disponibles**

```bash
python {{PROJ_DIR}}/scripts/scan_fotos.py --proj-dir {{PROJ_DIR}}
```
Para elegir fotos que NO tapen elementos importantes, consulta `{{PROJ_DIR}}/catalogo_detallado.json` si existe (describe contenido y zona de texto segura de cada foto).

**Paso 5 — Crear el plan de slides**

Sigue la estructura del tipo elegido en la biblioteca y **APLICA SIEMPRE la Capa de Persuasión** (sección 🧨 de `biblioteca-contenido.md`):

- Cada slide debe pegar ≥3 de los **4 ángulos**: dolor · automatización · beneficio · resultado concreto.
- **Especificidad numérica** (3×, 60s, +100K, +1M USD) en vez de "más" / "mejor".
- **Antes/Después** (Halbert): contrasta el "antes manual" con el "ahora automático".
- **Foco en el lector** ("tu negocio", "TU competencia"), no solo en el autor.
- **Reescribe siempre el primer borrador descriptivo.** Nunca presentes copy plano al usuario; pásalo antes por el checklist.

**Reglas específicas del carrusel:**

- **Slide 1 (cubierta/hook):** título corto y de impacto (≤8 palabras idealmente). El visual debe ser el más fuerte de todo el carrusel. Esta es la única decisión que importa para el alcance.
- **Slides 2 a N-1 (cuerpo):** desarrollo del tipo REPTINAC. Cada uno con un punto claro, no dos. Puedes ser más denso que en historias.
- **Slide final (cta):** lead magnet con palabra clave → DM. CTA explícito. Aquí va el handle `@usuario` como cierre.
- **Cohesión visual:** alterna fotos y fondos IA para variedad, pero mantén la paleta consistente (mismo color primario).

**Schema del plan (campos por slide):**

- `tipo`: `hook` para el primero, `cta` para el último; nombres descriptivos para los intermedios (`paso1`, `mito`, `dato`, `caso`, `objecion`, `refuerzo`, etc.).
- `titulo`: frase de impacto (el motor ajusta el tamaño automáticamente).
- `subtitulo`: elaboración (color primario de la marca).
- `texto_extra`: detalle secundario o cita (gris tenue).
- `foto`: archivo de `catalogo.json` que encaje (zona de texto despejada), o `null`.
- `fondo_ia`: objeto con:
  - `prompt`: descripción del fondo en inglés (oscuro + color de marca, zona despejada para el texto). El motor fija `aspect_ratio: "4:5"` automáticamente.
  - `model`: opcional. `"google/nano-banana"` standard (~$0.02/img, default) | `"nano-banana-pro"` o `"nano-banana-2"` premium (~$0.12/img). **Usa premium en slides 1 y 2.**
  - `cache_path`: opcional. Ruta relativa a un PNG ya generado (ej. `"output/carrusel_xxx/_bg_00.png"`). Si existe, el motor lo reusa sin gastar Kie. Útil para iterar.
- `texto_pos`: `"auto"` (recomendado) | `"top"` | `"center"` | `"bottom"`. En `"auto"` con foto cutout transparente, el motor evita la zona del sujeto automáticamente.
- `etiqueta`: (solo hook) etiqueta personalizada de la píldora superior.
- `palabras_clave`: 1–3 palabras clave del slide (referencia).
- `logos`: lista opcional de marcas (`["Meta","Claude","Retell AI",...]`) que se renderizan como chips arriba.
- `cta_palabra`: solo en `cta` — MAYÚSCULAS, 3–8 letras, sin acentos, temática.
- `cta_verbo`: solo en `cta` — "Comenta" / "Responde" (si se omite, usa el de config).

**Opciones avanzadas — Cover híbrido (foto cutout + fondo IA combinados):**

Si un slide tipo `hook` tiene AMBOS `foto` y `fondo_ia`, el motor activa **modo híbrido**: usa el fondo IA como base y sobrepone la foto cutout transparente a un lado, con el texto en la mitad opuesta y un gradiente oscuro para legibilidad. Útil para covers estilo magazine.

- `foto_lado`: `"right"` (default) | `"left"` — en qué mitad va la foto.
- `foto_escala`: 0.0–1.0 (default `0.85`) — qué porcentaje del alto del lienzo ocupa la foto. Recomendado **`0.85` para figuras pequeñas/medias** o **`0.95–1.0` para que la figura domine y se sienta más personal**.
- `foto_offset`: pixels que la foto sale del borde lateral (default `60`). Subir si quieres que la figura se "salga" del lienzo.

Regla práctica: si quieres que **la cara del personaje sea protagonista** y el texto convive a un lado, usa `foto_escala ≥ 0.85` con un `foto_offset` mayor (180–250). Si quieres un **layout más simétrico tipo dos columnas**, usa `foto_escala ≈ 0.65` con offset bajo.

**Formato del plan JSON:**
```json
{
  "tipo_contenido": "Transformación (paso a paso)",
  "objetivo": "enseñar accionable",
  "slides": [
    {
      "numero": 1, "tipo": "hook",
      "etiqueta": "GUÍA RÁPIDA",
      "titulo": "Cómo automatizar tu primera venta con IA en 60 minutos",
      "subtitulo": "Sin saber código. Sin gastar en herramientas caras.",
      "texto_extra": "Guárdalo antes de tu próxima campaña.",
      "foto": "Diego.PNG", "fondo_ia": null,
      "texto_pos": "auto",
      "palabras_clave": ["60 minutos"]
    },
    {
      "numero": 7, "tipo": "cta",
      "titulo": "¿Quieres la plantilla completa?",
      "subtitulo": "Te mando el flujo paso a paso por DM.",
      "texto_extra": "Los negocios del futuro no se crean con herramientas del pasado.",
      "foto": null, "fondo_ia": null,
      "cta_palabra": "AUTOMATIZA", "cta_verbo": "Comenta"
    }
  ]
}
```

**⚠️ REGLA DE ORO — aprobar el copy antes de generar imágenes:**

Muestra al usuario el **copy EXACTO de cada slide** (título, subtítulo, texto extra, CTA, etiqueta) en texto legible, **slide por slide**. **Espera su aprobación explícita.** NUNCA ejecutes `generate.py` hasta que el usuario apruebe el copy. Si pide cambios, ajústalos y vuelve a mostrar el copy completo. Generar sin copy aprobado desperdicia créditos de Kie AI (cada fondo IA cuesta dinero real).

**Paso 6 — Guardar el plan y generar**

```bash
python {{PROJ_DIR}}/scripts/generate.py --plan {{PROJ_DIR}}/plan.json --proj-dir {{PROJ_DIR}}
```

El motor:
1. Pre-genera fondos IA en paralelo (Kie AI, `aspect_ratio: "4:5"`).
2. Renderiza los 7 slides a 1080×1350.
3. Guarda en `{{PROJ_DIR}}/output/carrusel_<fecha>/`.

**Paso 7 — Mostrar resultados y publicar**

Muestra el slide 1 (cubierta) y el último (CTA). Si el usuario aprueba el set, ofrece **enviarlo a su celular por Telegram** para subirlo desde IG:
```bash
python {{PROJ_DIR}}/scripts/telegram_enviar.py --proj-dir {{PROJ_DIR}}
```

> 📌 **Cómo subir el carrusel a IG:** desde el teléfono, abre IG → "+" → carrusel → selecciona los slides EN ORDEN (01, 02, ..., 07). Verifica el orden antes de publicar.

---

## TIPOS REPTINAC QUE BRILLAN EN CARRUSEL

(Los 8 tipos completos están en `biblioteca-contenido.md`. Estos son los que **mejor calzan** en el formato 4:5):

| Tipo | Por qué funciona en carrusel | Estructura típica (7 slides) |
|---|---|---|
| **Transformación** | Paso a paso = guardable. Algoritmo lo premia. | Hook → contexto → paso 1 → paso 2 → paso 3 → resultado → CTA |
| **Engagement (Top N)** | Ranking = ganas atención slide a slide. | Hook → puesto 5 → 4 → 3 → 2 → 1 → CTA |
| **Polarización** | Mito desmontado con argumento extendido. | Hook (mito) → por qué se cree → la verdad → prueba → consecuencia → tu postura → CTA |
| **Autoridad** | Caso con datos = espacio para mostrar números. | Hook (resultado) → contexto → problema → solución → datos → lección → CTA |
| **Niveles de Consciencia** | Problem-Aware / Solution-Aware en slides separados. | Hook (síntoma) → dolor → diagnóstico → solución → diferenciación → prueba → CTA |
| **Conversión** | Comparativa / objeciones / antes-después. | Hook (oferta) → para quién → objeción 1 → objeción 2 → caso → garantía → CTA |

Relacionamiento e Interacción 1×1 funcionan mejor en historias por su naturaleza efímera/conversacional.

---

## REGLAS DE CTA

- Formato: `[Verbo] [PALABRA] y te [envío/mando] [recurso concreto]`.
- Palabra clave: una sola, MAYÚSCULAS, 3–8 caracteres, sin acentos, temática (no "INFO"/"HOLA").
- Nunca: "link en bio", "mándame DM", "Call to Action".
- En carrusel, el **lead magnet** (PDF, plantilla, checklist, audio) eleva la conversión: dilo explícito.
- El handle `@usuario` aparece como cierre en el slide CTA (no en cada slide).

## REGLAS DE FONDOS

Orden de prioridad por slide:
1. **Foto real** del catálogo que encaje (zona de texto despejada — ver `catalogo_detallado.json`).
2. **Fondo IA** (Kie AI) con prompt en inglés, estilo oscuro + color de marca, zona despejada. El motor envía `aspect_ratio: "4:5"`.
3. **Fondo sólido** — último recurso (típico en el slide CTA para que el texto domine).

La **cubierta (slide 1)** lleva el visual más impactante del carrusel. El texto se coloca solo en la zona despejada (`texto_pos: "auto"`).

---

## ONBOARDING (primer uso) — Brief de Marca

Si no existe `config.json`, construye el **brief**. *(En este proyecto el config.json viene hard-linkeado desde `historias-ig`, así que esto solo se ejecuta si se instala la skill en una máquina nueva.)*

Ofrece dos modos:
> "¿Llenamos tu brief en modo **LIBRE** (me cuentas tu negocio y tu historia como a un amigo, yo extraigo lo demás y solo te pregunto lo que falte) o **ESTRUCTURADO** (sección por sección)?"

### A. Identidad (siempre)
1. **Nombre de marca/negocio** → `nombre_marca`
2. **¿A qué se dedica? (1-2 oraciones)** → `descripcion_negocio`
3. **Tu nombre** → `nombre_usuario`
4. **Usuario de Instagram** → `instagram_user` (agrega @ si falta)
5. **Colores de marca:** a) hex (fondo + primario) · b) por defecto (oscuro-cyan) · c) `oscuro-cyan` (#08080F/#00E5FF) | `oscuro-naranja` (#0D0A08/#FF6B35) | `oscuro-verde` (#080F09/#00E676) | `claro-profesional` (#F8F9FA/#1A1A2E) → `colores`
6. **¿Kie AI?** Si sí, agregar `KIE_AI_API_KEY` en `{{PROJ_DIR}}/.env`.
7. **CTA habitual** (ej: "Comenta [PALABRA] y te envío [algo]") → `cta_formato`
8. **Etiqueta del hook por defecto** (ej: "GUÍA RÁPIDA") → `etiqueta_hook`

### B. Brief estratégico (para copy ultra-personalizado)
9. **Avatar / cliente ideal:** quién es (demografía + psicografía), su situación actual y qué quiere lograr → `avatar`
10. **Mapa de dolores (4 niveles)** → `dolores`:
    - **externo:** el problema visible/práctico.
    - **interno:** cómo lo hace sentir (frustración, miedo, vergüenza).
    - **relacional:** cómo afecta su estatus/relaciones.
    - **filosófico:** la injusticia profunda. *Debe pasar el Test de Amenaza Concreta:* ¿qué le pasa, en cuánto tiempo, si no lo resuelve? (concreto, no abstracto).
11. **Deseos / transformación buscada** → `deseos`
12. **Banco de auto-aplicación:** 3–8 momentos en que lo que vendes te ayudó a ti mismo → `banco_auto_aplicacion` (lista)
13. **Creencias del nicho:** mitos populares, verdades incómodas, prácticas saturadas con las que no estás de acuerdo (para Polarización) → `creencias_nicho` (lista)
14. **Oferta principal + ticket:** qué vendes y rango de precio (low <$300 / mid $300–$1.000 / high >$1.000) → `oferta`
15. **Tono/voz:** frases que repites, registro (cercano/técnico), qué evitar → `tono`

Si el usuario tiene poco tiempo, captura mínimo: identidad (A) + avatar + dolores + 3 momentos de banco. El resto se puede completar después con `/carruseles reconfigurar`.

Crear `{{PROJ_DIR}}/config.json` con el mismo schema que `/historias-ig` (el brief es compartido).

> 📌 **Uso del brief al crear contenido (Paso 5):** Polarización → usa `creencias_nicho`; Niveles de Consciencia → usa `dolores`; Conversión → usa `oferta` + reglas de precio; Autoridad → usa credenciales/casos; siempre habla al `avatar` con su `tono`.

Luego escanea fotos (Paso 4). Si no hay fotos, indica agregarlas en `{{PROJ_DIR}}/fotos/`.

---

## 📁 ESTRUCTURA DE LA CARPETA `fotos/`

```
fotos/                  ← FOTOS ORIGINALES de Diego (intactas, no tocar)
├── _cutouts/           ← Cutouts transparentes (rembg)
├── _compuestas/        ← Composiciones de scripts (compose_*.py)
├── _historicas/        ← Apify scraping seleccionado para uso editorial
├── _scraping/          ← Apify scraping crudo (todas las opciones por query)
│   ├── papa/
│   ├── otomano/
│   └── ...
└── _deprecated/        ← Intentos fallidos / versiones obsoletas
```

**Regla de oro:** las fotos de Diego viven en `fotos/` raíz. Todo lo que GENERA o DESCARGA la skill va a una subcarpeta con prefijo `_`. Nunca mezclar.

**En el `plan.json`** basta con poner el **nombre del archivo** (sin path). El motor tiene `resolve_foto_path()` que busca automáticamente en todas las subcarpetas en este orden:
1. `fotos/` (originales)
2. `fotos/_compuestas/`
3. `fotos/_cutouts/`
4. `fotos/_historicas/`
5. `fotos/_deprecated/`
6. `fotos/_scraping/*/`

Si necesitas forzar una ubicación específica, pasa el path con separador: `"foto": "_deprecated/Diego apuntando.png"`.

**Cuando agregues archivos:**
- Cutout nuevo con rembg → guardar en `fotos/_cutouts/`
- Composición de script → guardar en `fotos/_compuestas/`
- Imagen Apify seleccionada para un carrusel → mover de `_scraping/` a `_historicas/` con nombre descriptivo (ej: `historico galileo inquisicion.jpg`)

---

## 🪄 CUTOUTS (quitar fondo a fotos)

Para crear cutouts transparentes de personas/objetos usamos la librería `rembg`.

### Reglas

- **Modelo por defecto: `birefnet-general`** — state-of-the-art (modelo ~970MB, se descarga la primera vez). Esencial para detalles finos: dedos apuntando, pelo, bordes contra fondos oscuros.
- ❌ El modelo `u2net` (default de rembg) tiene bug conocido: los **dedos delgados** salen semi-transparentes contra fondos oscuros porque el algoritmo no genera alpha=255 en bordes finos. Síntoma: dedo "fantasmal" que deja ver el fondo a través.
- Para cutouts simples (objetos grandes, sin detalles finos), `u2net` está OK y es más rápido.

### Comando

```python
from rembg import remove, new_session
session = new_session("birefnet-general")
with open("foto.jpg", "rb") as f:
    out = remove(f.read(), session=session)
with open("cutout.png", "wb") as f:
    f.write(out)
```

### Después del cutout

- El motor (`pick_text_band`) detecta automáticamente el contenido del cutout transparente y evita esa zona con el texto.
- `getbbox()` recorta el padding transparente exterior — se aplica automáticamente en `generate.py`.

---

## 🔍 BÚSQUEDA DE IMÁGENES COMPLEMENTARIAS (Apify CLI)

Cuando un slide necesita una imagen real explicativa (un producto, una marca, un dashboard concreto que no se puede generar con IA porque tiene que ser EL real), usamos `apify-cli` con `hooli/google-images-scraper`.

### Protocolo OBLIGATORIO antes de scrapear

1. **Primero, mostrar el copy COMPLETO** de cada slide del carrusel — aplica la Regla de Oro normal.
2. **Identificar cuáles slides necesitan imagen explicativa real** (no fondo IA conceptual). Ejemplos:
   - Mockup específico de Claude Code, Meta Ads Manager, Wisprflow → imagen real
   - Logo de marca → imagen real (si no está en `logos/` ya)
   - Captura de pantalla de algún producto → imagen real
   - Ambiente abstracto / vibe / fondo → fondo IA (NO scraping)
3. **Pedir validación a Diego** antes de scrapear:
   > "Para el slide N (#Tool), propongo scrapear con la query `<query>`. ¿Procedo o ajustamos?"
4. **Sugerir queries específicas** — no genéricas. Ejemplos:
   - ❌ `claude` → muy genérico, devuelve cualquier cosa
   - ✅ `Claude AI Anthropic interface screenshot 2024` → específico
   - ✅ `Meta Ads Manager dashboard premium dark mode` → específico

### Reglas del scraping

- **Máximo 5 imágenes por query** (`maxResultsPerQuery: 5`).
- **No imágenes pequeñas** — el actor de Apify permite filtros de tamaño; usar mínimo `large` o `xlarge` para que tengan resolución decente.
- **Descargar a `fotos/`** con nombre descriptivo (no el hash de Apify).
- **No commitear las imágenes** (gitignored — son contenido de terceros, derechos no claros).

### Comando base

```powershell
echo '{"queries": ["<query específica>"], "maxResultsPerQuery": 5, "imageSize": "large"}' | apify call hooli/google-images-scraper --silent --output-dataset
```

Después del dataset, descargar las 5 URLs y mostrarlas a Diego para que elija cuál(es) usar. NUNCA usar la primera automáticamente.

---

## COMANDOS DE UTILIDAD

- **`/carruseles reconfigurar`** → borra `config.json` y rehace el onboarding.
- **`/carruseles fotos`** → re-escanea la carpeta de fotos.
- **`/carruseles ver`** → abre la última carpeta de output.
- **`/carruseles enviar`** → manda el último set a tu celular por Telegram.

---

## NOTAS TÉCNICAS

- **Formato:** 1080×1350 (4:5). Lienzo definido en `{{PROJ_DIR}}/scripts/utils.py`.
- **Fuentes:** Space Grotesk (en `{{PROJ_DIR}}/fonts/`, compartida con `/historias-ig`).
- **Texto:** autoajuste de tamaño (`draw_fitted_block`) + colocación inteligente (`pick_text_band`).
- **Kie AI:** modelo económico `google/nano-banana` por defecto (~$0.02/img). `nano-banana-2` para ocasiones especiales (~$0.12/img).
- **Telegram:** envía el set al celular para publicarlo (creds en `.env` y `config.json`).
- **Hermana:** `/historias-ig` (proyecto `historias-ig/`, formato 9:16). Comparten `config.json`, `fotos/`, `logos/`, `fonts/`, `catalogo_detallado.json` y `biblioteca-contenido.md` vía junctions/hard-links de Windows.
