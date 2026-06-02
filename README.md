# Brújula Electoral 2026

Comparador imparcial de propuestas para las elecciones presidenciales de Colombia 2026, con cada propuesta citada a su fuente, banderas constitucionales y comentarios de expertos atribuidos a quien los emite.

Proyecto **personal e independiente de Sergio Ferro**. No representa a ninguna campaña, partido ni organización. Es información cívica, no una recomendación de voto.

El sitio tiene **dos caras**:

| Ruta | Versión | Contenido |
|---|---|---|
| **`/`** | **v5 · Segunda vuelta** (default) | Cepeda vs De la Espriella, frente a frente, con selector personal. |
| **`/archivo`** · `/primera-vuelta` | **v4 · Primera vuelta** (archivo) | Los 12 candidatos · 616 propuestas, intacto. |

---

## v5 — Segunda vuelta (21 de junio de 2026)

Tras la primera vuelta (31-may), la página principal pasa a ser el comparador frontal de los dos finalistas. Seis secciones:

1. **Cara a cara** — los dos candidatos lado a lado: resultado de primera vuelta, fórmula vicepresidencial, apoyos recibidos, dos perfiles atribuidos (Candidateados y FEDe) y enlace al programa.
2. **Comparar por problema** — el núcleo. Para cada uno de los **8 problemas del país** (triangulados de cinco encuestadoras + fuentes estructurales) se muestran las propuestas de cada candidato en columnas espejo. Cada propuesta tiene un **selector personal** (👍 Me convence / 👎 No me convence / 🤷 No estoy seguro) que se guarda **solo en tu dispositivo** (`localStorage`, clave `brujula-2026-selections-v5`). Donde una columna no tiene información, se dice de forma explícita (un vacío no debe leerse como favoritismo).
3. **Posiciones** — matriz **frente a frente** de FEDe: la misma pregunta con la respuesta de cada candidato, en un acordeón por tema (Seguridad, Salud, Energía, Tierras y agro).
4. **Mi puntaje** — agrega tus selecciones por candidato y por problema. **Nunca recomienda voto**: tabula, no concluye.
5. **Hitos verificables** — cronología de hechos con fuente y enlace (ver reglas de curaduría abajo).
6. **Cómo decidir** — preguntas para pensar mejor la decisión, incluido el voto en blanco.

**Principios que no se rompen:** no se recomienda voto; no hay contadores de "popularidad" entre usuarios; no hay analítica ni rastreo; el mensaje de respeto al voto del otro aparece en el header, en Mi puntaje y en Cómo decidir; **simetría de trato** — donde falta información de un candidato, se declara explícitamente en vez de dejar un hueco.

### Datos de segunda vuelta

- **FEDe** actualizó su plataforma (sheet nuevo `116rf6…`): mantiene 5 candidatos en su panel; aquí se **filtra a los dos finalistas**. Aporta propuestas, banderas, comentarios de expertos y la nueva matriz de posiciones.
- **Candidateados** no cambió su data programática para 2ª vuelta → se **reusa la de primera vuelta** (los programas oficiales no cambiaron).
- Corpus: [`public/propuestas-2026-segunda-vuelta.json`](public/propuestas-2026-segunda-vuelta.json). Builder determinista: [`data/build_segunda_vuelta.py`](data/build_segunda_vuelta.py). Cobertura y decisiones: [`data/cobertura-segunda-vuelta.md`](data/cobertura-segunda-vuelta.md).

### Reglas de curaduría de hitos (`public/hitos.json`)

Estrictas, a propósito:

- **Solo hechos verificables** con fuente, fecha y enlace. Nada de rumores.
- **Lenguaje neutro:** "X declaró Y" / "Z anunció apoyo a W"; nunca "X criticó duramente Y" ni "Z se vio fortalecido".
- **Simetría obligatoria:** mismo número de hitos *propios* por candidato. Si no se puede, la asimetría se muestra de forma explícita (no se esconde).
- **Ventana móvil de 14 días** desde `lastUpdated`.
- **Curaduría manual, sin scraping** en vivo. Baja frecuencia, alta calidad.
- Categorías: `resultado`, `apoyo`, `debate`, `judicial`, `propuesta`.

Actualizar un hito es editar el JSON; no hay que tocar el HTML.

---

## v4 — Primera vuelta (archivo, en `/archivo`)

Comparador de los **12 candidatos** · **616 propuestas**. Queda intacto como archivo histórico. Cuatro vistas:

1. **Candidatos** — propuestas por candidato y sector, con texto fiel y fuente.
2. **Comparar** — propuestas lado a lado.
3. **¿Quién atiende qué?** — capa de análisis interpretativo propio (rúbrica transparente) que cruza propuestas con los problemas del país.
4. **Problemas del país** — datos estructurales y de encuestas (promedios simples entre encuestadoras).

> Sitio estático de una sola página (HTML + JSON + fuentes self-hosted). Sin backend, sin tracking, sin cookies.

## Fuentes de datos de primera vuelta · corte 28 de mayo de 2026

| Fuente | Aporte |
|---|---|
| **[Candidateados](https://www.candidateados.com)** | 12 candidatos · 6 sectores · 415 propuestas (extraídas parseando el payload RSC de su app Next.js). |
| **[FEDe](https://propuestascandidatos.fedecolombia.org)** | 5 candidatos · 5 sectores · 201 propuestas con URL de fuente oficial, 19 banderas Alerta/Amenaza, 171 comentarios de 12 expertos nombrados. |
| Web | Fórmulas vicepresidenciales y nota de retiro de Caicedo. |

Detalle de cobertura y vacíos en [`data/cobertura.md`](data/cobertura.md).

## Imparcialidad

- **Texto fiel**: cada propuesta conserva su fuente; las fuentes no se fusionan.
- Las banderas **"Alerta/Amenaza"** son juicios de **FEDe** (lente del Estado de Derecho), **no veredictos neutros**. Los comentarios son opiniones atribuidas a expertos nombrados.
- La capa "¿Quién atiende qué?" es análisis interpretativo propio con rúbrica explícita.
- **Verifica en las fuentes originales antes de decidir tu voto.**

¿Error o feedback? → **hello@ferroraptor.com**

---

## Estructura del repo

```
public/                                  # lo único que sirve Azure SWA
  index.html                             # v5 · segunda vuelta (default /)
  propuestas-2026-segunda-vuelta.json    # corpus v5 (Cepeda + De la Espriella + posiciones)
  hitos.json                             # cronología verificable (curaduría manual)
  img/                                   # fotos oficiales self-hosted (cepeda/espriella .webp)
  archivo/index.html                     # v4 · primera vuelta (ruta /archivo)
  propuestas-2026.json                   # corpus v4 servido (~873 KB) — INTACTO
  fonts/                                 # Fraunces + Public Sans (OFL, self-hosted)
  favicon.svg · og-image.png · robots.txt
  staticwebapp.config.json               # headers, caché, MIME, rutas /archivo, SPA fallback
                                         # (vive dentro de public/ = raíz del contenido desplegado)
data/                                    # NO se despliega — fuente reproducible
  raw/                                   # insumos crudos (Candidateados + CSVs FEDe + VP)
  raw/fede2_csv/                         # sheet FEDe de 2ª vuelta (9 pestañas)
  build_propuestas.py                    # builder v4 (determinista)
  build_segunda_vuelta.py                # builder v5 (determinista, 2 candidatos + posiciones)
  refresh_sources.py                     # re-fetch FEDe/Candidateados (parametrizable por env)
  cobertura.md · cobertura-segunda-vuelta.md
.github/workflows/                       # CI/CD Azure SWA (workflow auto-generado por Azure)
```

## Regenerar el corpus

Los JSON servidos se reconstruyen de forma **determinista** desde `data/raw/` (solo stdlib de Python 3, sin red en el paso de build):

```bash
# v4 · primera vuelta
python3 data/build_propuestas.py            # -> public/propuestas-2026.json

# v5 · segunda vuelta — refrescar el sheet FEDe nuevo y reconstruir
FEDE_SHEET_ID=116rf6RK1l5kqredZKK47F55tif2GGw2474vKdZUPrFM \
  FEDE_DIR="$(pwd)/data/raw/fede2_csv" \
  FEDE_TABS_EXTRA="preguntas,posiciones" FEDE_ONLY=1 \
  python3 data/refresh_sources.py           # refresca data/raw/fede2_csv/ (solo FEDe)
python3 data/build_segunda_vuelta.py        # -> public/propuestas-2026-segunda-vuelta.json
```

`build_segunda_vuelta.py` no toca el corpus de primera vuelta. Los **hitos** se editan a mano en `public/hitos.json` (ver reglas de curaduría arriba).

## Correr local

`file://` bloquea `fetch`, así que hay que levantar un servidor:

```bash
python3 -m http.server 8000 -d public
# abrir http://localhost:8000
```

## Deploy (Azure Static Web Apps · tier Free)

1. Recurso **Static Web App** creado vía Azure Portal conectado a este repo (rama `main`). Nombre: `yellow-beach-0d1a32b0f`.
2. Azure generó su propio workflow (`.github/workflows/azure-static-web-apps-yellow-beach-0d1a32b0f.yml`) e inyectó el secret `AZURE_STATIC_WEB_APPS_API_TOKEN_YELLOW_BEACH_0D1A32B0F`. `app_location: ./public`.
3. **Dominio público**: <https://brujula-electoral.ferroraptor.com/> (dominio custom sobre el default `yellow-beach-0d1a32b0f.7.azurestaticapps.net`). Los meta `og:url`/`og:image` y el `<link rel="canonical">` apuntan al dominio custom para evitar contenido duplicado en SEO.
4. `git push` a `main` dispara build + deploy automáticamente.

> Nota: `staticwebapp.config.json` vive en `public/` (no en la raíz del repo) porque SWA solo lo lee desde la raíz del contenido desplegado (`app_location`). En la raíz del repo se ignoraría.

## Notas técnicas

- **Sin build tooling** (ni Vite ni webpack ni npm): es HTML + JSON + woff2 estáticos a propósito.
- **CSP con `'unsafe-inline'` en script**: concesión consciente porque el HTML usa handlers `onclick=` inline. El sitio es estático y no procesa input de usuario, así que no hay vector XSS. Para endurecer: refactorizar a `addEventListener` y quitar `'unsafe-inline'`.
- `index.html` pesa ~58 KB (CSS + JS del template; el corpus de 870 KB va aparte). Gzip ≈ 17 KB.

## Licencias

- Fuentes **Fraunces** y **Public Sans**: SIL Open Font License (OFL) — redistribución permitida.
- Textos de propuestas: pertenecen a sus fuentes originales (campañas, Candidateados, FEDe). Aquí se citan con atribución.
