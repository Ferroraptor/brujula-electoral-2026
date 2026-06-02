# Brújula Electoral v5 — Segunda vuelta (Cepeda vs De la Espriella)

This ExecPlan is a living document. The sections **Progress**, **Surprises & Discoveries**,
**Decision Log**, and **Outcomes & Retrospective** must be kept up to date as work proceeds.

---

## Purpose / Big Picture

Hoy el sitio (`https://brujula-electoral.ferroraptor.com/`) es **v4**: un comparador de los 12
candidatos de primera vuelta. La primera vuelta ya pasó (31-may-2026). El **21 de junio** hay
segunda vuelta entre **Iván Cepeda** (Pacto Histórico) y **Abelardo de la Espriella** (Defensores
de la Patria).

Tras este cambio, quien entre a `/` verá **v5**: una herramienta enfocada en contrastar **solo a
los dos finalistas**, con un selector personal (👍/👎/🤷) que se guarda en su dispositivo y un
"Mi puntaje" que **agrega sus selecciones sin nunca recomendar voto**. La v4 queda intacta y
navegable en `/archivo` (y `/primera-vuelta`) como archivo histórico.

Comportamiento observable al terminar:
1. `GET /` → nuevo `index.html` v5 con header de segunda vuelta, contador a 21-jun, 5 secciones.
2. `GET /archivo` → la v4 actual, intacta, con un banner discreto "Estás viendo el archivo de
   primera vuelta. [Ver segunda vuelta →]".
3. El selector 👍/👎/🤷 persiste en `localStorage` (`brujula-2026-selections-v5`) tras refrescar.
4. "Mi puntaje" calcula agregados correctos por candidato y por problema, sin recomendar voto.
5. `public/propuestas-2026-segunda-vuelta.json` (cepeda+espriella, con propuestas, análisis FEDe y
   matriz de posiciones) y `public/hitos.json` cargan vía `fetch` sin errores de consola.
6. `public/propuestas-2026.json` (v4) sigue **byte-idéntico**.

## Progress

**Milestone 1 — Datos de segunda vuelta**
- [x] Parametrizar `data/refresh_sources.py` (sheet/ output) sin romper el pipeline v4.
- [x] Refrescar el sheet nuevo de FEDe a `data/raw/fede2_csv/` (7+2 pestañas).
- [x] Escribir `data/build_segunda_vuelta.py` (reusa lógica del builder v4, solo 2 candidatos +
      bloque de posiciones FEDe).
- [x] Generar `public/propuestas-2026-segunda-vuelta.json` y verificar estructura.
- [x] Descargar fotos oficiales a `public/img/` (cepeda.webp, espriella.webp).
- [x] `data/cobertura-segunda-vuelta.md` con decisiones de imparcialidad.

**Milestone 2 — Archivar v4**
- [x] Mover `public/index.html` → `public/archivo/index.html`.
- [x] Banner discreto en el archivo + corregir rutas de fetch del corpus (`/propuestas-2026.json`).
- [x] Rutas SWA para `/archivo` y `/primera-vuelta`.

**Milestone 3 — Sitio v5 (`public/index.html` nuevo)**
- [x] Esqueleto: header global (kicker, título, contador, mensaje de respeto, selector de vuelta).
- [x] `public/hitos.json` (seed simétrico) + sección Hitos verificables.
- [x] Sección 1 — Cara a cara (dos cards con foto/iniciales, resultado 1ª vuelta, VP, apoyos, CTA).
- [x] Sección 2 — Comparar por problema (8 problemas, columnas espejo, selector localStorage,
      acordeón FEDe, resumen sectorial, capa de posiciones).
- [x] Sección 3 — Mi puntaje (estado vacío + agregación + texto reflexivo).
- [x] Sección 5 — Cómo decidir (texto reflexivo + voto en blanco + cierre de respeto).
- [x] Selector: persistencia localStorage, mutuamente excluyente, "Limpiar selecciones", aviso.

**Milestone 4 — Config, SEO, calidad, entrega**
- [x] `public/staticwebapp.config.json`: rutas + caché de nuevos JSON, sin tocar CSP.
- [x] Meta/OG/canonical de v5; v4 archivo con su canonical a `/archivo`.
- [x] Quality checks del brief (grep prohibidos, simetría, respeto ×3, persistencia, móvil).
- [x] `README.md` actualizado (v5 + reglas de curaduría de hitos).
- [x] Branch + commits (Sergio Ferro, sin Co-Authored-By) + PR a `main` + avisar.

## Surprises & Discoveries

- **Observación:** El brief asumía que FEDe se reducía a 2 candidatos para segunda vuelta.
  **Evidencia:** El `config.js` en vivo de FEDe usa nuevo `SHEET_ID=116rf6RK1l5kqredZKK47F55tif2GGw2474vKdZUPrFM`
  pero la pestaña `candidatos` sigue trayendo **5** (cepeda, espriella, valencia, fajardo, lopez).
  **Implicación:** Filtramos a 2 en el builder; no es bloqueante.
- **Observación:** Candidateados NO actualizó la data programática de los dos candidatos.
  **Evidencia:** El payload RSC en vivo trae 12 candidatos con conteos idénticos a v4 (cepeda 97,
  espriella 29). Solo agregó un toggle de UI "Segunda vuelta". **Implicación:** Reutilizamos la data
  de primera vuelta de Candidateados para ambos (avalado por el brief).
- **Observación:** FEDe agregó dos pestañas nuevas: `preguntas` (19) y `posiciones` (38) = una
  matriz cara-a-cara donde cada candidato responde la misma pregunta por sector. **Implicación:**
  Se incorpora como capa extra "Posiciones frente a frente" (decisión aprobada por el usuario).
- **Observación:** FEDe expone `foto_url` oficial por candidato (img/cepeda.webp, img/espriella.webp).
  **Evidencia:** Descarga directa devuelve WebP válido (52KB / 42KB). **Implicación:** Se self-hostean
  en `public/img/` (decisión del usuario: "lo de las fotos sí aguanta, hazlo también").

## Decision Log

- **Decisión:** Dos archivos HTML (v5 en `public/index.html`, v4 en `public/archivo/index.html`),
  no un router cliente. **Rationale:** Azure SWA sirve estáticos; dos HTML es lo más simple, no
  expande CSP, y deja la v4 literalmente intacta. **Fecha/Autor:** 2026-06-01 / Sergio (vía agente).
- **Decisión:** Iniciales **y** fotos oficiales self-hosted en las cards de Cara a cara (foto con
  fallback a iniciales si falla la carga). **Rationale:** El usuario lo pidió explícitamente; las
  fotos suben legibilidad. Self-host respeta `img-src 'self'`. **Fecha/Autor:** 2026-06-01 / Sergio.
- **Decisión:** Incorporar la matriz `posiciones` de FEDe como capa extra. **Rationale:** Contraste
  directo de alta calidad, atribuido a FEDe; el brief no la conocía. **Fecha/Autor:** 2026-06-01 / Sergio.
- **Decisión:** El builder de segunda vuelta es un **script nuevo** (`data/build_segunda_vuelta.py`),
  no una bifurcación del v4. **Rationale:** Mantiene `build_propuestas.py` y `propuestas-2026.json`
  (v4) intactos y reproducibles; el riesgo de romper el archivo es cero. **Fecha/Autor:** 2026-06-01.
- **Decisión:** Reusar fielmente los helpers de render de v4 (`renderProp`, `fuenteLink`,
  `fedeFlagText`, `escapeHTML`, `PROBLEMS`, `PROBLEM_SECTORS`). **Rationale:** Consistencia visual y
  de imparcialidad ya auditada; menos superficie de bug. **Fecha/Autor:** 2026-06-01.

## Outcomes & Retrospective

**Estado: implementación completa, lista para PR (2026-06-01).** Los 4 milestones quedaron hechos y
verificados localmente con QA interactivo (Playwright sobre el Chromium cacheado):

- Contador: 20 días (correcto: 1-jun → 21-jun).
- Cara a cara: 2 cards simétricas, fotos cargan, resultados/VP/apoyos/perfil/CTA OK.
- Selector: 👍/👎/🤷 mutuamente excluyente, persiste en `localStorage` tras reload (verificado).
- Mi puntaje: "Has evaluado 2 de 195 propuestas (1%)", agregación por candidato y problema correcta,
  texto reflexivo presente, no recomienda voto.
- Posiciones frente a frente: 4 preguntas en seguridad (correcto); 0 en corrupción↔institucional
  (correcto, ese sector no tiene preguntas).
- Hitos: 6 hitos, simetría verificada (2 propios por candidato + 2 comunes), fuentes con URL real.
- Móvil 390px: overflow horizontal = 0; columnas apilan.
- `/archivo`: v4 intacta (12 candidatos, 616 props), banner discreto, corpus carga sin error.
- Strings prohibidos: grep vacío. Mensaje de respeto en 3 lugares. Cero errores JS en consola.
- `propuestas-2026.json` (v4) byte-idéntico (git diff vacío).

**Pendiente (requiere push/infra):** PR a `main`, Lighthouse sobre el preview de SWA, prueba en
dispositivo móvil real, y revisión de Sergio antes del merge.

**Lección / discovery:** el supuesto del brief sobre FEDe (reducción a 2 candidatos) era incorrecto;
verificar fuentes en vivo antes de planear evitó construir sobre una premisa falsa. La matriz
`posiciones` (no anticipada) resultó un valor agregado real.

---

## Context and Orientation

**El proyecto** es un sitio cívico estático **sin build tooling** (HTML + JSON + woff2 servidos tal
cual por Azure Static Web Apps). No hay npm, ni bundler, ni framework. Trabajamos en
`/Users/sferrod/Workspace/brujula-electoral-2026/`.

Archivos clave (rutas completas):
- `public/index.html` — **v4 actual** (906 líneas, CSS+JS inline). Será movido a `public/archivo/`.
- `public/propuestas-2026.json` — corpus v4 (873 KB, 12 candidatos, 616 propuestas). **Intocable.**
- `public/staticwebapp.config.json` — headers de seguridad (incluye CSP con `'unsafe-inline'` en
  script, concesión consciente por los `onclick=` inline), caché, MIME, fallback SPA.
- `data/build_propuestas.py` — builder determinista v4: `data/raw/` → `public/propuestas-2026.json`.
- `data/refresh_sources.py` — re-fetch defensivo de FEDe (Google Sheet vía gviz CSV) + Candidateados
  (parsing del payload RSC `self.__next_f`). Solo stdlib.
- `data/raw/` — insumos: `candidateados_parsed.json`, `fede_csv/*.csv`, `vp_web.json`.
- `data/cobertura.md` — documento de cobertura/imparcialidad v4.
- `.github/workflows/update-data.yml` — cron diario (refresca→rebuild→commit-si-cambió→deploy).

**Términos:**
- **FEDe** = Fundación para el Estado de Derecho. Analiza programas con lente constitucionalista;
  sus banderas (Alerta/Amenaza) y comentarios son **juicios atribuidos**, no veredictos neutros.
- **Candidateados** = agregador secundario que publica propuestas por candidato/sector.
- **gviz CSV** = endpoint público de Google Sheets que exporta una pestaña como CSV.
- **Selector** = los tres botones 👍 Me convence / 👎 No me convence / 🤷 No estoy seguro por propuesta.

**Estructura del corpus v4** (la que debe replicar segunda vuelta) — top-level `{meta, candidatos}`;
cada candidato: `{id, nombre, partido, formula_vp, formula_vp_fuente, posicion_ideologica_autodescrita,
programa_url, bio, cubierto_por[], notas[], red_flags_fede[], sectores[]}`. Cada sector:
`{sector, fuente_origen ('candidateados'|'fede'), subtema, resumen_fuente, evaluacion_fede, propuestas[], nota}`.
Cada propuesta: `{id, titulo, subtema, texto, texto_resumen_medio, editado, fuente, tags_terceros:
{constitucionalidad, viabilidad_senalada, comentarios_expertos[]}}`.

**Reglas de imparcialidad (NO romper):** texto fiel; fuentes no se fusionan; banderas/comentarios
atribuidos a FEDe; sin bandera ⇒ `constitucionalidad: null`; mostrar la crítica concreta y esconder
la etiqueta abstracta; no etiquetar a un candidato con términos cargados que no sean suyos o de
fuente citada.

**Datos verificados en vivo (2026-06-01):**
- FEDe sheet nuevo `116rf6RK1l5kqredZKK47F55tif2GGw2474vKdZUPrFM`. Pestañas:
  `candidatos` (cols nuevas: foto_url, educacion, color_hex), `propuestas` (cepeda 30, espriella 47),
  `comentarios_expertos` (172), `expertos` (12), `red_flags` (4), `resumen_sectores` (25),
  `sectores`, **`preguntas` (19: id,sector,pregunta,orden,visible)**, **`posiciones`
  (38: id,pregunta_id,candidato_id,respuesta,visible)**.
- Candidateados RSC: cepeda 97 props (6 sectores), espriella 29 props (6 sectores). Sin cambios.
- Resultados oficiales primera vuelta: **De la Espriella 43,74 % (10.361.499)**, **Cepeda 40,90 %
  (9.688.348)**. Ninguno alcanzó 50 %+1.
- Apoyos seed: Cepeda ← Roy Barreras; De la Espriella ← Paloma Valencia.

## Plan of Work

### Milestone 1 — Datos de segunda vuelta

1. **`data/refresh_sources.py`** — parametrizar para soportar el sheet nuevo sin romper v4:
   - Aceptar variables de entorno `FEDE_SHEET_ID` (default = sheet v4) y `FEDE_DIR` (default
     `raw/fede_csv`) y `FEDE_TABS` extendible. Mantener el comportamiento por defecto idéntico.
   - Añadir `preguntas` y `posiciones` a la lista de pestañas cuando se refresca el sheet nuevo,
     con su `FEDE_REQUIRED_COL` (`preguntas`→`pregunta`, `posiciones`→`respuesta`).
   - Comando de uso: `FEDE_SHEET_ID=116rf6… FEDE_DIR=raw/fede2_csv python3 data/refresh_sources.py`
     (solo FEDe; Candidateados ya está fresco y no cambió).
2. **Descargar** las 7+2 pestañas del sheet nuevo a `data/raw/fede2_csv/`.
3. **`data/build_segunda_vuelta.py`** (script nuevo, reusa funciones de `build_propuestas.py`):
   - Importar/duplicar las utilidades deterministas (`clasificar_constitucionalidad`, `abbr`,
     `FEDE_SECTOR`, `SEMAFORO_LABEL`, `SLUG2ID`) — preferible `import` para no duplicar lógica.
   - Construir **solo** cepeda y espriella: bloques Candidateados (de `candidateados_parsed.json`,
     idénticos a v4) + bloques FEDe (del `fede2_csv/`).
   - Campos de candidato nuevos desde el sheet: `educacion`, `foto` (ruta local `img/<id>.webp`),
     `color_hex` (informativo; el sitio usa su propia paleta), `partido`, `formula_vp`,
     `biografia` (atribuida a FEDe).
   - **Bloque nuevo `posiciones`** a nivel meta o por candidato: parsear `preguntas` + `posiciones`
     a una estructura `{sector, pregunta, respuestas:{cepeda, espriella}}` (solo visibles, solo
     ambos candidatos presentes). Guardar en `out["posiciones_fede"]` (lista ordenada por
     `sector` y `orden`).
   - `meta` con `fecha_consulta`, `fuentes_usadas`, `resultados_primera_vuelta` (votos+%),
     `apoyos` (seed), `candidatos_incluidos: ["cepeda","espriella"]`, `sheet_fede`, notas.
   - Resultado: `public/propuestas-2026-segunda-vuelta.json`.
4. **Fotos:** descargar `cepeda.webp`/`espriella.webp` a `public/img/`.
5. **`data/cobertura-segunda-vuelta.md`** documentando: FEDe mantiene 5 (filtramos 2), Candidateados
   sin cambios (reuso 1ª vuelta), posiciones incorporadas, fotos self-hosted, simetría de datos.

### Milestone 2 — Archivar v4

1. `git mv public/index.html public/archivo/index.html`.
2. En `public/archivo/index.html`:
   - El fetch usa `'./propuestas-2026.json'` → cambiarlo a `'/propuestas-2026.json'` (ruta absoluta)
     para que cargue desde la raíz aunque la página viva en `/archivo/`.
   - Insertar banner discreto arriba del `<header>`: "Estás viendo el archivo de primera vuelta.
     [Ver segunda vuelta →]" (link a `/`).
   - Ajustar `<link rel="canonical">`/`og:url` a `/archivo`.
3. El corpus `propuestas-2026.json` se queda en `public/` (raíz) — no se mueve.

### Milestone 3 — Sitio v5 (`public/index.html` nuevo)

Construir un único `index.html` nuevo, mismo enfoque que v4 (CSS+JS inline, `onclick=` permitido por
la CSP existente, sin librerías). Reusar el sistema de diseño v4 (fuentes Fraunces/Public Sans,
paleta, `.prop`, `.fede-box`, modal, etc.) copiando el CSS base relevante. Vistas como tabs (igual
patrón que v4). Estructura:

- **Header global:** kicker `Elecciones presidenciales · Colombia 2026 · Segunda vuelta`, `<h1>`,
  **contador** `días hasta el 21 de junio` (cálculo en JS: `Math.ceil((Date(2026-06-21) - hoy)/día)`),
  **mensaje de respeto** prominente (no en footer), selector `[Segunda vuelta]` (activo) /
  `[Primera vuelta · archivo →]` (link a `/archivo`).
- **Tabs:** Cara a cara · Comparar por problema · Mi puntaje · Hitos · Cómo decidir.
- **Sección 1 — Cara a cara:** dos `.cara-card` espejo. Cada una: foto (`<img src="img/<id>.webp">`
  con `onerror` → iniciales) , nombre + partido, **resultado 1ª vuelta** (votos absolutos + %),
  fórmula VP, **badges de apoyos**, frase descriptiva **atribuida** (de la bio FEDe, marcada como
  "Descripción de FEDe"), link a programa oficial, CTA `Ver propuestas →` (cambia a tab Comparar con
  ese candidato resaltado). Debajo, centrado: card `Vota en blanco — explorar opción` → ancla a
  "Cómo decidir".
- **Sección 2 — Comparar por problema:** chips de los 8 problemas (scroll-x en móvil). Por problema:
  cabecera con **dato de percepción ciudadana** (de `PROBLEMS` de v4). Dos columnas espejo
  **Cepeda | De la Espriella**. Al inicio de cada columna, si el problema mapea a un sector FEDe,
  el **resumen FEDe sectorial** (`evaluacion_fede`). Cada propuesta = card con: título+texto (reusar
  `renderProp`), **selector 👍/👎/🤷** (3 botones excluyentes, refleja estado de localStorage),
  acordeón "Ver análisis FEDe", fuente con link. Mapping problema→sector (del brief):
  ```
  corrupcion↔institucional · seguridad↔seguridad · salud↔salud · empleo↔(sin FEDe)
  pobreza↔tierras_y_agro(parcial) · educacion↔(sin FEDe) · fiscal↔institucional(parcial)
  infra↔energia(parcial)
  ```
  Donde no hay sector FEDe, decirlo explícito (no rellenar). **Capa extra "Posiciones frente a
  frente":** para el sector FEDe del problema, listar las `preguntas`/`posiciones` con la respuesta
  de ambos lado a lado. Aviso de privacidad ("Tus selecciones se guardan solo en tu dispositivo…")
  + botón "Limpiar mis selecciones" (con confirm).
- **Sección 3 — Mi puntaje:** si `selections` vacío → estado vacío con CTA. Si hay ≥1: agregados
  globales ("Has evaluado N de M (X%)"), por candidato (convencen/no/indecisas), desglose por
  problema, y **texto reflexivo crítico** (verbatim del brief) que NO recomienda voto; cierre con
  mensaje de respeto.
- **Sección 4 — Hitos verificables:** lee `public/hitos.json`, ordena por fecha desc, ventana 14
  días desde `lastUpdated`, render neutro, **verificación de simetría** (mismo nº por candidato o
  aviso visible de la asimetría).
- **Sección 5 — Cómo decidir:** texto reflexivo (5 bloques del brief) + voto en blanco + cierre de
  respeto.

**Selector — modelo de estado** (`localStorage` key `brujula-2026-selections-v5`):
```js
{ "version":"v5", "lastUpdated":"<ISO>", "selections": { "<proposal_id>": "like"|"dislike"|"unsure" } }
```
Funciones: `loadSel()`, `saveSel()`, `setSel(id, val)` (toggle/exclusivo), `clearSel()`. Manejo de
errores si `localStorage` está bloqueado (try/catch, degradar a memoria + aviso).

**`public/hitos.json`** seed (simétrico; estructura del brief): resultados (ambos), apoyo Cepeda←Roy
Barreras + apoyo Espriella←Paloma Valencia, emplazamiento a debate (Cepeda) + propuesta de debate
(Espriella). Cada hito con fuente + URL real (sourcing con WebSearch para URLs verificables).

### Milestone 4 — Config, SEO, calidad, entrega

1. `public/staticwebapp.config.json`:
   - `routes`: añadir `/archivo` y `/primera-vuelta` → `rewrite: /archivo/index.html`; caché para
     `propuestas-2026-segunda-vuelta.json` y `hitos.json` (max-age 300) e `img/*` (largo).
   - **No tocar CSP** (sigue `img-src 'self' data:` — las fotos son self-hosted; OK).
   - Mantener `navigationFallback` a `/index.html`.
2. Meta/OG/canonical de v5 (`/`); el archivo apunta su canonical a `/archivo`.
3. Quality checks (ver Validation).
4. `README.md`: sección v5, rutas, reglas de curaduría de hitos, nuevo pipeline de datos.
5. Branch `feat/v5-segunda-vuelta`, commits atómicos (autor Sergio Ferro, sin Co-Authored-By),
   `gh pr create` a `main`, recoger preview URL de SWA, avisar para revisión.

## Concrete Steps

```bash
cd /Users/sferrod/Workspace/brujula-electoral-2026
git checkout -b feat/v5-segunda-vuelta

# M1 — datos
mkdir -p data/raw/fede2_csv public/img
FEDE_SHEET_ID=116rf6RK1l5kqredZKK47F55tif2GGw2474vKdZUPrFM \
  FEDE_DIR="$(pwd)/data/raw/fede2_csv" \
  FEDE_TABS_EXTRA="preguntas,posiciones" \
  python3 data/refresh_sources.py            # esperado: "FEDe: 9/9 pestañas actualizadas"
python3 data/build_segunda_vuelta.py          # esperado: OK -> public/propuestas-2026-segunda-vuelta.json
curl -sL -A "Mozilla/5.0" https://propuestascandidatos.fedecolombia.org/img/cepeda.webp    -o public/img/cepeda.webp
curl -sL -A "Mozilla/5.0" https://propuestascandidatos.fedecolombia.org/img/espriella.webp -o public/img/espriella.webp

# M2 — archivar v4 (corpus se queda en raíz)
mkdir -p public/archivo && git mv public/index.html public/archivo/index.html
# (editar fetch a ruta absoluta + banner + canonical)

# M3/M4 — construir public/index.html v5, hitos.json, config, README

# Validación
python3 -m http.server 8000 -d public         # abrir http://localhost:8000 y /archivo
grep -rEi "te recomendamos votar|deberías votar|el ganador es|el mejor candidato" public/  # vacío
# node --check sobre el <script> extraído de cada index.html
python3 -c "import json;[json.load(open('public/'+f)) for f in ['propuestas-2026.json','propuestas-2026-segunda-vuelta.json','hitos.json']];print('JSON OK')"
git diff --stat HEAD -- public/propuestas-2026.json   # debe estar vacío (v4 intacto)
```

## Validation and Acceptance

Levantar `python3 -m http.server 8000 -d public` y verificar:
1. **`/`** muestra v5: header con contador correcto a 21-jun, 5 tabs, mensaje de respeto visible.
2. **Cara a cara**: dos cards simétricas (Espriella 43,74 % / 10.361.499; Cepeda 40,90 % / 9.688.348),
   foto cargando (o iniciales si falla), badges de apoyo, CTA funcional.
3. **Comparar**: marcar 👍 en una propuesta de Cepeda y 👎 en una de Espriella; **refrescar** →
   el estado persiste. Cada problema muestra su dato de percepción; donde no hay FEDe, se dice.
4. **Mi puntaje**: con 0 selecciones → estado vacío. Con selecciones → "Has evaluado N de M",
   agregados por candidato y por problema correctos, texto que NO recomienda voto.
5. **Hitos**: orden desc, simetría por candidato, links abren fuente.
6. **`/archivo`** y **`/primera-vuelta`**: cargan la v4 completa (12 candidatos, 616 props) sin
   errores de consola, con banner discreto.
7. **Consola limpia**: sin errores de fetch; los 3 JSON cargan.
8. **Strings prohibidos**: el grep sale vacío.
9. **Mensaje de respeto** en ≥3 lugares (header, cierre de Mi puntaje, cierre de Cómo decidir).
10. **v4 intacto**: `git diff` de `public/propuestas-2026.json` vacío.
11. **Lighthouse** (en preview de PR): ≥90 en a11y/perf/best-practices.
12. **Móvil** (360/390 px): sin overflow horizontal; chips scrollables; cards apilan.

## Idempotence and Recovery

- `refresh_sources.py` es defensivo: si una pestaña falla validación, conserva la previa.
- `build_segunda_vuelta.py` es determinista: re-ejecutarlo regenera el mismo JSON desde `raw/`.
- `git mv` del index v4 es reversible (`git mv` de vuelta). El corpus v4 nunca se toca.
- Todo el trabajo va en branch `feat/v5-segunda-vuelta`; `main` no se modifica hasta el merge.

## Artifacts and Notes

- FEDe `posiciones` ejemplo de fila: `{id, pregunta_id, candidato_id, respuesta, visible}`; se cruza
  con `preguntas` `{id, sector, pregunta, orden, visible}` por `pregunta_id`.
- Colores de candidato en v4: cepeda `#B5634A`, espriella `#5A5A8C` (se mantienen por consistencia).
- Mensaje de respeto (verbatim del brief) y textos reflexivos de "Mi puntaje" y "Cómo decidir" van
  copiados fielmente del brief.

## Interfaces and Dependencies

- **Sin dependencias nuevas.** Python 3 stdlib (datos), HTML/CSS/JS vanilla (sitio).
- **Azure SWA** (deploy) — `staticwebapp.config.json` dentro de `public/`.
- **Fuentes de datos:** FEDe (Google Sheet gviz CSV, sheet `116rf6…`), Candidateados (RSC, sin
  cambios), web (resultados oficiales + apoyos, vía WebSearch para URLs de hitos).
- **Git:** branch `feat/v5-segunda-vuelta`; commits como Sergio Ferro `sferrod@gmail.com`, **sin**
  `Co-Authored-By`, **sin** `git daimon` (repo público personal).
