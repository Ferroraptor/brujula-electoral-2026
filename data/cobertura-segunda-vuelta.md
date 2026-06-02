# Cobertura — Brújula Electoral 2026 · Segunda vuelta

**Fecha de consulta:** 2026-06-01
**Elección:** segunda vuelta, 21 de junio de 2026
**Entregable:** `public/propuestas-2026-segunda-vuelta.json` (Cepeda + De la Espriella)

> Documento de cobertura, no de análisis. No contiene rankings ni conclusiones.
> El corpus de primera vuelta (`public/propuestas-2026.json`, 12 candidatos) queda **intacto**
> y navegable en `/archivo`.

## Qué cambió respecto a primera vuelta

| Fuente | ¿Actualizó para 2ª vuelta? | Qué hicimos |
|---|---|---|
| **FEDe** | **Sí.** Sheet nuevo (`SHEET_ID=116rf6RK1l5kqredZKK47F55tif2GGw2474vKdZUPrFM`; el viejo quedó comentado en su `config.js`). Más propuestas, campos nuevos de candidato (`foto_url`, `educacion`, `color_hex`) y **dos pestañas nuevas** (`preguntas`, `posiciones`). | Refrescamos a `data/raw/fede2_csv/` y reconstruimos. |
| **Candidateados** | **No** (la data programática). Su home agregó un toggle "Segunda vuelta", pero el payload RSC sigue trayendo los 12 candidatos con conteos idénticos a 1ª vuelta (Cepeda 97, De la Espriella 29). | Reutilizamos la data de 1ª vuelta para los dos (avalado por el brief: los programas oficiales no cambiaron). |
| **Web** | Resultados oficiales de 1ª vuelta + apoyos. | Se guardan en `meta` (con fuente) y en `public/hitos.json` (con enlace). |

## Hallazgo importante (corrige un supuesto)

El brief asumía que FEDe **reduciría su panel a los dos finalistas**. No fue así: el sheet nuevo
**mantiene 5 candidatos** (cepeda, espriella, valencia, fajardo, lopez) en los mismos 5 sectores
(Seguridad, Salud, Energía, Tierras y Agro, Institucional), con panel de expertos ampliado.
El builder de 2ª vuelta **filtra a los dos finalistas**; no es bloqueante.

## Estado por candidato (entregable)

| id | Candidateados (1ª vuelta) | FEDe (2ª vuelta, visibles) | Banderas | Coment. expertos | Red flags | Foto |
|---|---|---|---|---|---|---|
| cepeda | 97 props (6 sectores) | 28 props (5 sectores) | 4 | 32 | 2 | ✅ self-hosted |
| espriella | 29 props (6 sectores) | 41 props (5 sectores) | 7 | 36 | 2 | ✅ self-hosted |

> Los conteos FEDe "visibles" (28 / 41) son menores que el total crudo del sheet (30 / 47) porque
> algunas filas vienen marcadas `visible≠si`; se respeta esa marca, igual que en 1ª vuelta.

## Bloque nuevo: `posiciones_fede` (matriz cara-a-cara)

FEDe agregó 19 preguntas (en 4 sectores: Seguridad, Salud, Energía, Tierras y Agro — **Institucional
no tiene preguntas**) con la respuesta de cada candidato. **Los 19 pares están completos** (ambos
respondieron las 19). Se guardan en `out["posiciones_fede"]`, ordenados por sector y por id de
pregunta, atribuidos a FEDe. Es contraste directo de alta calidad, no juicio propio.

## Perfiles del candidato (dos, ambos atribuidos)

- `bio` — perfil corto de **Candidateados** (tamaño de tarjeta).
- `biografia_fede` — perfil de **FEDe**, más detallado. Incluye hechos verificables sobre la
  trayectoria de cada candidato (p. ej., los casos que De la Espriella ha representado como abogado).
  **Es información factual, no caracterización cargada.** Mismo origen (FEDe) para ambos candidatos.
- `educacion` — formación académica (FEDe).
- `posicion_ideologica_autodescrita` = `""` para ambos: ninguna fuente la expone de forma textual y
  autodescrita; no se infiere (igual que en 1ª vuelta).

## Decisiones de imparcialidad (documentadas)

1. **Fuentes NO fusionadas.** Cada propuesta conserva su fuente real; las banderas de FEDe no se
   trasladan a propuestas de Candidateados.
2. **`constitucionalidad.nivel`** es el mismo mapeo mecánico y transparente del texto de FEDe
   (default `contestado`; `tumbado_por_corte` solo si cita fallo de la Corte). La explicación
   verbatim de FEDe queda en `detalle`.
3. **Sin bandera de fuente nombrada ⇒ `null`.** No se asume `sin_objecion`.
4. **Resultados y apoyos llevan fuente.** Los resultados de 1ª vuelta se atribuyen a la Registraduría;
   los apoyos se detallan con enlace en `hitos.json` bajo reglas estrictas de simetría.
5. **Fotos self-hosted.** Las fotos oficiales de FEDe (`img/cepeda.webp`, `img/espriella.webp`) se
   sirven localmente desde `public/img/` para respetar la CSP (`img-src 'self'`) sin hotlinking.

## Reproducibilidad

```bash
# 1) refrescar el sheet de 2ª vuelta a data/raw/fede2_csv/ (solo FEDe; Candidateados no cambió)
FEDE_SHEET_ID=116rf6RK1l5kqredZKK47F55tif2GGw2474vKdZUPrFM \
  FEDE_DIR="$(pwd)/data/raw/fede2_csv" \
  FEDE_TABS_EXTRA="preguntas,posiciones" \
  FEDE_ONLY=1 \
  python3 data/refresh_sources.py

# 2) reconstruir el corpus de 2ª vuelta (determinista, sin red)
python3 data/build_segunda_vuelta.py   # -> public/propuestas-2026-segunda-vuelta.json
```

No requiere red en el paso 2. El builder de 1ª vuelta (`build_propuestas.py`) y su corpus
(`propuestas-2026.json`) **no se tocan**.
