# v5 — Fichas agrupadas: duplicados entre Candidateados y FEDe

> Spec + ejecución. Rama `feat/v5-fichas-agrupadas` (PR #5).
> Estado: implementado, en revisión de Sergio en el preview.

## Problema (detectado por Sergio, 2026-06-11)

Ambas fuentes derivan del programa del candidato y documentan varias políticas
idénticas. En "Comparar por problema" quedaban una al lado de la otra:
- doble lectura para el elector,
- doble voto posible en Mi puntaje,
- asimetría visual: la versión FEDe trae análisis/comentarios y la de
  Candidateados se ve "pelada".

Medición (difflib por problema): ~12 pares evidentes en Cepeda y ~11 en
Espriella, varios con texto idéntico al 100%. Parejo entre candidatos →
tratable sin sesgo.

## Decisión (elegida por Sergio entre 3 opciones)

**Ficha agrupada.** Agrupar NO es fusionar:
- La versión FEDe es la principal (tiene fuente oficial + análisis).
- El texto de Candidateados queda visible y atribuido dentro de la ficha,
  en el expandible «Así la recoge Candidateados».
- Un solo voto por política.

Descartadas: referencia cruzada (no resuelve doble lectura/voto) y ocultar sin
más (pierde texto y atribución de Candidateados).

## Implementación

- **Build** (`build_segunda_vuelta.py`): `PROPUESTAS_AGRUPADAS` (cand_id →
  fede_id), curado a mano, solo pares inequívocos. Validación con assert:
  existencia + similitud mínima 0.45 (truena el build si los IDs posicionales
  se corren al re-congelar candidateados → obliga a re-curar). Emite
  `agrupada_con_fede` (en la gemela cand) y `tambien_candidateados` (resuelto,
  en la ficha FEDe). Nota metodológica en meta.
- **Front** (`index.html`):
  - `TWIN_OF` (cand→fede). `getSel`/`setSel` canonizan al id FEDe → un voto
    por política desde cualquier vista.
  - `propsFor` oculta la gemela cand SOLO si su ficha FEDe está en la misma
    vista (en Empleo/Educación, sin capa FEDe, la versión cand sigue sola).
  - `renderProp`: expandible `.also-cand` (estilo flag-expand + caja sepia).
  - `allProps` excluye gemelas → Mi puntaje sobre 207 propuestas únicas (230−23).
  - Migración localStorage **v6→v7**: selecciones sobre gemelas se trasladan a
    la canónica sin pisarla; el drop de espriella-cand solo aplica a pre-v6.

## Verificación

- Build determinista, 23 pares validados.
- `node --check` OK; headless: migración v7 correcta (traslado + no-pisar +
  descarte), duplicados ocultos en corrupción, voto único entre vistas
  (empleo→fiscal), expandible abre con texto atribuido, 360 px sin overflow,
  0 errores de consola.

## Regla aprendida (se suma a la del PR #4)

Cuando dos fuentes documentan la misma política, mostrarlas por separado no es
neutralidad: duplica lectura, infla el voto y hace ver "pelada" a la versión
sin análisis. Agrupar con doble atribución preserva "fuentes no se fusionan".
