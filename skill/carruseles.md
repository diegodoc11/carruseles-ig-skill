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

### 🎨 Modo ILUSTRATIVO (preferido): que la imagen CUENTE lo que dice el texto

Por defecto, **el `fondo_ia` debe ILUSTRAR el texto del slide**, no ser un fondo genérico. Antes de escribir cada prompt, **LEE el texto del slide** y conviértelo en una escena concreta que lo ejemplifique.

1. **Personaje/estilo consistente en TODO el carrusel.** Elige una mascota o estilo que encaje con el tema y repítelo en los 8 slides (ej. para "equipo de IAs": *robotsitos blancos estilo Pixar, ojos/acentos naranja*). La consistencia es lo que lo hace ver pro.
2. **Cada slide ilustra su idea** (lee el texto → acción/objeto): "IA de contenido" → robot con ícono de Instagram · "IA de anuncios" → robot con megáfono · "captación" → robot armando una landing/VSL · "seguimiento" → robot con teléfono en una llamada · "equipo de IAs" → varios robots con badge · "empresa con empleados" → robots en computadores (oficina).
3. **Deja SIEMPRE la mitad inferior despejada** (el texto va abajo, `texto_pos: "bottom"`). Cierra el prompt con: `..., the lower half a clean solid dark empty area reserved for text, no text, no words, no letters`.
4. **Personajes ilustrados SÍ, humanos realistas NO.** Pide el personaje explícito; el `no text, no words, no letters` evita que el modelo escriba (el texto lo pone el motor).
5. **Modelo:** slides 1-2 con `nano-banana-pro` (escenas con varios personajes salen mucho mejor en premium); slides 3+ con `google/nano-banana`.

**Plantilla:** `[estilo render] of [personaje consistente] [acción que ilustra el texto], [props del concepto], deep black background with warm orange accents, the lower half a clean solid dark empty area reserved for text, no text, no words, no letters`

**Ejemplo validado (slide "IA de anuncios"):** `Pixar-style 3D render of a single cute friendly rounded white robot with a glowing orange visor face holding a megaphone, several small glowing advertisement screens floating around it in the upper half, cinematic studio lighting, deep black background with warm orange accents, the lower half a clean solid dark empty area reserved for text, no text, no words, no letters`

> El modo **atmosférico** clásico (escena sin personajes) sigue válido para el slide CTA o como alternativa, pero el **modo ilustrativo es el preferido** en slides de valor/explicativos. Validado en el carrusel "Tu equipo de IAs / Imperio".

### 📸 REGLA — al menos UNA foto real de la marca por carrusel

El modo ilustrativo es genial, pero **NUNCA entregues un carrusel 100% ilustraciones/fondos sin una sola foto de la persona de la marca** (Diego): pierde la conexión humana — es un error. Incluye su foto en al menos un slide que encaje (portada, el slide de "yo"/diferenciación, autoridad o el cierre), aplicando la Regla Sagrada (texto abajo, cara despejada). Antes de entregar, **verifica que el carrusel tenga ≥1 foto real suya.**

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

## 🧭 LO QUE FUNCIONA vs LO QUE NO (lecciones reales del proyecto)

Este proyecto produjo 3 carruseles publicables. Esta sección documenta lo que funcionó al primer intento vs lo que requirió 6+ iteraciones (señal de que NO es el approach correcto).

### ✅ LO QUE FUNCIONA (usar SIEMPRE)

1. **Split LATERAL (izq/derecha) con cutouts limpios + fondo IA premium**
   - Ejemplo: carrusel "Iglesia vs IA" slide 1 (Papa cutout izq + Diego cutout der + fondo IA "catedral vs servidores")
   - Se aprobó en 2 iteraciones
   - Script: `compose_iglesia_vs_ia.py` (reusable cambiando paths)

2. **Cover híbrido del motor** (foto cutout + fondo IA premium)
   - El motor de `generate.py` lo hace nativamente con `foto` + `fondo_ia` (`modo_hibrido` true)
   - Foto cutout va a un lado (`foto_lado`), fondo IA llena el resto, texto en mitad opuesta
   - Más rápido que las composiciones manuales

3. **Fondos IA cinematográficos con nano-banana-pro** (slides 1 y 2)
   - Prompts atmosféricos sin gente ni texto: "cinematic editorial photo of X, dramatic lighting, premium magazine quality, lower third clear for text overlay, no people, no text"
   - Funciona muy bien para slides 1 y 2 (los más importantes)

4. **Composición editorial CTA** (screenshot IG + cutout apuntando + caja palabra clave)
   - `compose_cta_bg.py` para el fondo
   - El motor del CTA con `foto_cutout` sobrepuesto sin frame
   - Cutout debe ser "Diego apuntando v2" (apunta al screenshot → autoridad)

5. **Apify scraping para imágenes históricas/culturales clásicas**
   - Pinturas de dominio público, ukiyo-e, retratos de figuras públicas
   - Resultados consistentes con queries específicas

6. **Cutouts con rembg `birefnet-general`** (no `u2net`)
   - Detalles finos como dedos apuntando salen perfectos

### ❌ LO QUE NO FUNCIONA (evitar)

1. **Split VERTICAL (arriba/abajo) con composiciones complejas**
   - Intenté "Diego con hot dogs sepia arriba + Diego con BMW abajo" en el carrusel JARVIS
   - Resultado: 6+ iteraciones, nunca quedó profesional
   - Cuando ambas mitades tienen un sujeto humano, los cuerpos se alinean visualmente y CONFUNDEN al lector
   - **Mejor alternativa cuando hay arco antes/después**: split LATERAL (como Papa vs Diego), o usar UNA SOLA FOTO completa + texto encima

2. **Sobreponer elementos pequeños sobre fotos donde hay caras**
   - Intenté sobreponer Iron Man en la esquina superior derecha del slide hot dogs y TAPÓ la cara de Diego
   - Hay que validar EXHAUSTIVAMENTE que no haya solape con cara
   - **Mejor alternativa**: posicionar en padding negro inferior/superior, o esquina OPUESTA a la cara del sujeto principal

3. **Image-to-image con nano-banana-pro para preservar identidad**
   - Intentamos: convertir screenshot IG a dark mode → cambió la cara
   - Intentamos: quitar lanyard VIP de cutout → reinterpretó la camisa + cambió cara
   - **Conclusión**: el modelo es generativo, no editor pixel-perfect. NO sirve para edits con contenido crítico

4. **Asumir que Claude "ve como diseñador"**
   - Claude puede generar layouts técnicamente correctos pero perder la intuición visual del diseñador profesional
   - **Solución**: aplicar EXPLÍCITAMENTE el checklist post-render (sección abajo) en cada slide, leyendo el PNG con Read tool

5. **Empezar a "mejorar" un slide ya aprobado**
   - Pasó con el slide 1 de JARVIS: la v1 estaba aprobada (carrusel_1550), después iteré 6 veces innecesariamente
   - **Solución**: cuando el usuario aprueba algo, COPIAR la imagen a `_compuestas/<nombre>_aprobado.png` y referenciarla en el plan. No regenerar.

### 📐 WORKFLOW VALIDADO (sigue siempre este orden)

1. **Identificar tipo REPTINAC** (consultar `biblioteca-contenido.md`)
2. **Mostrar copy completo PRIMERO** (Regla de Oro — esperar OK explícito)
3. **Identificar fotos del catálogo** que encajen (consultar `catalogo_detallado.json`)
4. **Para slide 1**: usar cover híbrido SIEMPRE (cutout + fondo IA premium)
5. **Para slide 2**: refuerzo con fondo IA premium o foto fuerte del catálogo
6. **Slides 3-7**: fotos del catálogo o fondos IA standard (`google/nano-banana` $0.02)
7. **Slide CTA**: composición editorial con screenshot IG + cutout apuntando + caja palabra clave
8. **Renderizar todo**
9. **CHECKLIST POST-RENDER OBLIGATORIO** (sección abajo) — leer cada PNG y validar
10. **Si pasa el checklist → mandar a Telegram con caption + hashtags**
11. **Si el usuario aprueba un slide → marcarlo como aprobado** (copiar a `_compuestas/_aprobado/`)
12. **Si el usuario pide iterar otro → NO tocar los ya aprobados**

### 💰 Costo típico aplicando este workflow

- 2 fondos IA premium nano-banana-pro: $0.24
- 5 fondos IA standard google/nano-banana: $0.10
- 1 composición editorial: $0.12
- **Total carrusel completo: ~$0.46 USD**

Iterar el mismo carrusel cuesta $0 si se usa `cache_path` religiosamente.

---

## 🔮 SKILL HERMANA FUTURA: `carruseles-premium` (todo con nano-banana-pro)

Diego va a crear una skill hermana que usa `nano-banana-pro` para TODOS los slides + genera el texto incrustado en la imagen (no con motor PIL). Más cara (~$1.20 por carrusel) pero más cinematográfica.

**Cuándo usar `/carruseles` (esta skill, económica):**
- Producción regular semanal
- Carruseles donde el copy cambia rápido (iterar texto sin gastar IA)
- Cuando la marca tipográfica importa (Space Grotesk consistente)

**Cuándo usar `/carruseles-premium` (la futura, cara):**
- Lanzamientos importantes
- Casos donde se necesita una composición que el motor no puede hacer
- Sin importar costo

Esta skill (la económica) seguirá siendo la default para Diego. La premium es para ocasiones especiales.

---

## 🔖 REGLA — VERSIONES APROBADAS NO SE TOCAN

Cuando el usuario aprueba un slide (dice "me gustó", "queda bien", "dejémoslo así"), **MARCAR INMEDIATAMENTE esa versión como aprobada** copiándola a `fotos/_compuestas/<descriptivo>_aprobado.png` y referenciándola en el plan.

**Si el usuario pide iterar OTRO slide después**, NO regenerar el slide aprobado — usar `cache_path` o referencia directa al archivo aprobado.

Errores históricos del proyecto:
- ❌ Slide 1 del carrusel JARVIS: aprobado en versión 1 (carrusel_1550), después regenerado 6 veces hasta que el usuario tuvo que recordar dónde estaba la versión que sí le gustaba.

**Cuando el usuario diga "dejémoslo así" o "me gustó":**
1. Copiar el archivo a `fotos/_compuestas/<nombre>_aprobado.png`
2. Actualizar plan.json para apuntar a esa imagen como `foto` directa
3. Vaciar `titulo`/`subtitulo`/`texto_extra` si la imagen ya tiene texto incrustado
4. NO volver a generar/componer esa versión salvo que el usuario lo pida explícitamente

---

## 🚨 REGLA SAGRADA — NO TAPAR LA CARA

**ABSOLUTAMENTE NUNCA un texto, logo, cutout, sticker, polaroid o cualquier elemento puede tapar la cara del sujeto (Diego u otra persona) en un slide.** Si Claude renderiza un slide y un elemento tapa una cara, es un BUG crítico que se debe arreglar antes de mandar a aprobación.

### Cómo evitarlo

1. **Antes de posicionar cualquier elemento sobrepuesto** (Iron Man, polaroid, cutout adicional, logo grande):
   - Identificar visualmente la zona de la cara del sujeto principal en la foto base
   - Calcular si el elemento sobrepuesto va a solapar con esa zona
   - Si sí: reposicionar a una zona libre (esquina inferior, padding negro, lateral opuesto)

2. **Zonas seguras típicas** para sobreponer elementos sin tapar caras:
   - Padding negro inferior (modo fit con foto landscape)
   - Padding negro superior (cuando el texto está abajo)
   - Esquina opuesta a la cara (si la cara está arriba-derecha, sobreponer abajo-izquierda)

3. **Después de renderizar**, OBLIGATORIO mirar el slide y confirmar:
   - ¿Veo la cara del sujeto completamente?
   - ¿Algún elemento decorativo le pasa por la frente, ojos, nariz, boca?
   - Si sí → reposicionar y re-renderizar antes de mandar al usuario

### Bugs históricos de este tipo en el proyecto

- ❌ Texto del slide 5 (resultado BMW) caía sobre la cara de Diego apoyado en el BMW → arreglado con `texto_pos: "bottom"`
- ❌ Texto del slide 8 (cierre emocional) tapaba la cara de Diego.PNG → arreglado con `texto_pos: "bottom"`
- ❌ Iron Man cutout sobrepuesto en slide 1 (hot dogs) tapaba la cara de Diego → arreglado moviendo a esquina inferior derecha en padding negro

**Esta regla aplica también a textos**, no solo a elementos visuales. Cuando uses `texto_pos: "auto"`, verificar el resultado y ajustar a `"top"`/`"bottom"` si el motor eligió mal.

---

## 🎨 REVISIÓN POST-RENDER (rol diseñador profesional)

**OBLIGATORIO:** después de renderizar el carrusel, antes de mandarlo a Telegram, Claude tiene que **abrir cada slide PNG con la Read tool y revisarlo como diseñador profesional** aplicando este checklist:

### Checklist por slide

1. **Composición narrativa**
   - Si es un "antes/después": ¿la persona aparece en AMBAS mitades? (No carrito vs persona — eso rompe la narrativa)
   - ¿La foto del slide cuenta visualmente lo que dice el copy? (Ej. si el texto habla de libertad, ¿la foto muestra eso?)

2. **No tapar caras**
   - ¿El texto cae sobre la cara del sujeto? Si sí → cambiar `texto_pos` a `bottom` o usar `text_y_top/bottom` custom
   - Bug recurrente: `texto_pos: "auto"` con foto cover puede elegir mal

3. **Cover crop / fit decisions**
   - Si la foto es landscape y el sujeto está a un lado, cover crop puede DEJARLO FUERA
   - Verificar: ¿el sujeto principal está visible después del cover crop?
   - Si no: usar `foto_modo: "fit"` o hacer cutout y posicionar manualmente

4. **Contraste de texto**
   - Texto blanco sobre fondo claro = ilegible. Texto naranja sobre fondo naranja = bajo contraste.
   - Si el slide tiene cutouts/composición con gradient, verificar que el texto caiga sobre zona oscura

5. **Cutouts correctos**
   - ¿Estoy usando el cutout adecuado para el slide? (apuntando hacia arriba para CTA con screenshot, sorpresa para cierre emocional, etc.)
   - Diego apuntando v2 = para CTAs con autoridad (apunta al screenshot)
   - Diego.PNG = para slides de sorpresa/curiosidad

6. **Lista vertical legible**
   - Si hay lista (items con bullets), ¿está VERTICAL una debajo de otra? (No una línea con puntos)
   - Bullet "•" funciona. ✅/✓ NO funcionan (Space Grotesk no los tiene → cuadrado fallback feo)

7. **Logos correctos**
   - ¿El logo que aparece es el correcto? (Verificar manualmente — el slug puede mapear a archivo equivocado)
   - Quitar logos si dominan visualmente y compiten con el copy

### Si encuentras algún problema

1. Reportar al usuario qué viste y qué propones
2. NO mandar a Telegram hasta que el problema esté arreglado
3. Iterar: ajustar plan / composición / motor → re-render → revisar de nuevo

### Lecciones aprendidas del proyecto

- ❌ Si el texto cae sobre la cara: `texto_pos: "bottom"` o ajustar bandas
- ❌ Si la persona se sale del cover crop: usar cutout + composición manual
- ❌ Si emojis ✅/✓ se ven como cuadrados: cambiar a "•" o "→" (Latin Extended)
- ❌ Si el "antes/después" muestra carrito vs persona: hacer cutout de la persona y poner persona en AMBAS mitades
- ✅ Cover híbrido (foto cutout + fondo IA) funciona muy bien para slide 1
- ✅ Composiciones pre-hechas (`compose_*.py`) son la solución cuando el motor no puede hacer el layout

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
