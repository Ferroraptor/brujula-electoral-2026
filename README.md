# Brújula Electoral 2026

Comparador imparcial de las propuestas de los **12 candidatos** a la presidencia de Colombia 2026 — **616 propuestas** con su fuente citada, banderas constitucionales y comentarios de expertos atribuidos a quien los emite.

Proyecto **personal e independiente de Sergio Ferro**. No representa a ninguna campaña, partido ni organización. Es información cívica, no una recomendación de voto.

---

## Qué es

Un sitio estático de una sola página (HTML + JSON + fuentes self-hosted). Sin backend, sin tracking, sin cookies. Cuatro vistas:

1. **Candidatos** — propuestas por candidato y sector, con texto fiel y fuente.
2. **Comparar** — propuestas lado a lado.
3. **¿Quién atiende qué?** — capa de análisis interpretativo propio (rúbrica transparente) que cruza propuestas con los problemas del país.
4. **Problemas del país** — datos estructurales y de encuestas (promedios simples entre encuestadoras).

## Fuentes de datos · corte 28 de mayo de 2026

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

¿Error o feedback? → **sferrod@gmail.com**

---

## Estructura del repo

```
public/                     # lo único que sirve Azure SWA
  index.html                # artefacto (corpus cargado vía fetch)
  propuestas-2026.json      # corpus servido (~873 KB)
  fonts/                    # Fraunces + Public Sans (OFL, self-hosted)
  favicon.svg · og-image.png · robots.txt
  staticwebapp.config.json  # headers de seguridad, caché, MIME, SPA fallback
                            # (debe vivir dentro de public/ = raíz del contenido desplegado)
data/                       # NO se despliega — fuente reproducible
  raw/                      # insumos crudos (scrape + CSVs de FEDe + VP)
  build_propuestas.py       # builder determinista
  cobertura.md              # qué quedó completo / con vacíos
.github/workflows/          # CI/CD Azure SWA (workflow auto-generado por Azure)
```

## Regenerar el corpus

El JSON servido se reconstruye de forma **determinista** desde `data/raw/`:

```bash
python3 data/build_propuestas.py        # -> public/propuestas-2026.json
```

No requiere red ni dependencias externas (solo stdlib de Python 3).

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
