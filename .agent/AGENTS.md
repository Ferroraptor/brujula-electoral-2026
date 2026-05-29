# Brújula Electoral 2026 — Contexto para Agente (handoff)

> Memoria del producto para retomar el trabajo en otra sesión. Vivís dentro de
> `~/Workspace/brujula-electoral-2026/`. Léeme primero.

## Qué es
Comparador **imparcial** de propuestas de los 12 candidatos presidenciales de Colombia 2026.
**Proyecto personal e independiente de Sergio Ferro** (NO marca PerfectaMente). Sitio estático.

- **En vivo:** <https://brujula-electoral.ferroraptor.com/> (dominio custom)
- **Default Azure:** `yellow-beach-0d1a32b0f.7.azurestaticapps.net`
- **Repo:** github.com/Ferroraptor/brujula-electoral-2026 (público)
- **Contacto público:** hello@ferroraptor.com

## Identidad / git
- Commits **a título personal de Sergio Ferro** (`sferrod@gmail.com`), **sin** `Co-Authored-By`.
  NO usar `git daimon` aquí (es público y personal, no PerfectaMente).
- Refrescos automáticos los commitea `github-actions[bot]`.

## Arquitectura (sin build tooling — HTML+JSON+woff2 estáticos a propósito)
```
public/                  # lo único que sirve Azure SWA
  index.html             # artefacto único; CSS+JS inline; corpus por fetch
  propuestas-2026.json   # corpus (~873 KB), 12 candidatos / 616 propuestas
  fonts/ (Fraunces+Public Sans woff2, OFL) · favicon.svg · og-image.png · robots.txt
  staticwebapp.config.json   # OJO: va DENTRO de public/ (SWA lo lee desde app_location)
data/                    # NO se despliega
  build_propuestas.py    # determinista: data/raw/ -> public/propuestas-2026.json
  refresh_sources.py     # re-fetch FEDe + Candidateados (defensivo, solo stdlib)
  raw/                   # candidateados_parsed.json, fede_csv/, vp_web.json
  cobertura.md           # qué quedó completo / vacíos / decisiones de imparcialidad
.github/workflows/
  azure-static-web-apps-yellow-beach-0d1a32b0f.yml  # deploy (auto-generado por Azure, on push)
  update-data.yml        # cron datos (lo escribimos nosotros)
```

## Fuentes de datos (corte inicial 2026-05-28)
- **Candidateados** (RSC de Next.js): 12 candidatos, 6 sectores, 415 propuestas. Se parsea el payload `self.__next_f`.
- **FEDe** (Google Sheet público, 7 pestañas, `SHEET_ID=1joLt-JrQuf4HLfSubQYa0Jjd10DG7fk47DC0niaL2Jw`): 5 candidatos, 5 sectores, 201 propuestas con URL oficial, 19 banderas Alerta/Amenaza, 171 comentarios de 12 expertos.
- **vp_web.json**: fórmulas VP (web search). Estático, no se auto-refresca.

## Reglas de imparcialidad (NO romper)
- Texto fiel; **fuentes no se fusionan** (cada propuesta lleva su fuente real).
- Banderas/comentarios son **juicios atribuidos a FEDe**, no veredictos neutros.
- Sin bandera de fuente nombrada ⇒ `constitucionalidad: null` (no asumir "sin objeción").
- Principio de UI: **mostrar la crítica concreta (subtítulo de FEDe), esconder la etiqueta abstracta** (ratings secundarios).
- No etiquetar a un candidato con términos cargados que no sean suyos ni de fuente citada
  (ej. se quitó "Seguridad Democrática 2.0" de Espriella; el "3.0" de Valencia se dejó porque es textual de FEDe).

## Flujos de trabajo
- **Regenerar corpus:** `python3 data/build_propuestas.py` (no requiere red).
- **Refrescar fuentes a mano:** `python3 data/refresh_sources.py` luego rebuild.
- **Correr local:** `python3 -m http.server 8000 -d public` → http://localhost:8000 (`file://` bloquea fetch).
- **Editar la UI:** `public/index.html` es el canónico (editar ahí directo).
  `data/index_v_4_4.html` + `data/_transform_html.py` fueron migración one-time, NO re-correr.
- **Deploy:** push a `main` dispara el workflow de Azure. El cron despliega explícito
  (un push con `GITHUB_TOKEN` no dispara otros workflows).
- **Cron de datos** (`update-data.yml`): 12:00 y 18:00 Colombia (`0 17,23 * * *` UTC).
  Refresca → rebuild → commit SOLO si cambió → deploy. `gh workflow run update-data.yml` para probar.

## Verificación (cómo probamos)
- No hay Playwright instalado; se usa `npm i playwright-core` temporal + el Chromium en
  `~/Library/Caches/ms-playwright/chromium-1208/...`, o Chrome headless (`--dump-dom`, `--screenshot`).
- Tras editar JS: extraer el `<script>` y `node --check`.
- Mobile: auditar overflow a 360/390px; ya se arreglaron URLs largas (`overflow-wrap:anywhere`),
  grid de Comparar (minmax 240px + scroll-x) y badge de subtema (apila <=560px).

## Pendientes / ideas (cuando se retome)
- "Cosillas visuales" en mobile que Sergio quería pulir (pedir screenshots puntuales).
- Posible notificación (email/Slack) si `refresh_sources.py` falla la validación de una fuente.
- Si se monta otro dominio: actualizar `og:url`, `og:image` y `<link rel="canonical">` en `public/index.html`.
