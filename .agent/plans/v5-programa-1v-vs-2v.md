# v5 — Vista comparada: programa de 1ª vs 2ª vuelta de De la Espriella

> Spec + plan de implementación. Rama `feat/v5-espriella-programa-2v` (PR #4).
> Estado: en ejecución.

## Contexto y motivación

Candidateados reescribió el programa de De la Espriella para 2ª vuelta
(29 → 63 propuestas en los 6 sectores). El cambio en sí es **información
electoral valiosa**: el elector debe poder ver lo último Y identificar
fácilmente que cambió respecto a 1ª vuelta. Cepeda no cambió su programa.

**Hallazgo que define el diseño:** 0 de las 29 propuestas de 1ª vuelta tienen
continuidad textual con las 63 nuevas (0 títulos idénticos; mejor similitud de
cuerpo: 0.46 con difflib). No es una ampliación, es una **reescritura total**.
Un diff mecánico es imposible y un mapeo "esta equivale a esta" sería juicio
editorial nuestro (inventar relaciones). Decisión: **mostrar las dos versiones
fieles, sin mapeo** — cero inferencia, consistente con las reglas de
imparcialidad del proyecto.

## Decisión de producto (validada con Sergio)

- Vista **comparada** de ambas versiones, dentro de la columna de Espriella en
  "Comparar por problema" (única vista donde se renderizan propuestas).
- **Híbrido con toggle**: vista predeterminada = comparada (2ª vuelta completa
  arriba + 1ª vuelta como bloque de archivo compacto debajo); un segmented
  control permite cambiar a "solo programa actual".
- Vara de calidad: UX limpia y satisfactoria (transiciones suaves, sin saltos
  de layout, jerarquía visual clara, preferencia recordada).

## Datos (build)

1. **Congelar** el programa de 1ª vuelta en `data/raw/candidateados_1v.json`,
   extraído de git `b34cdbe:data/raw/candidateados_parsed.json` (snapshot del
   cron 2026-06-06, anterior al cambio de programa; 29 propuestas verificadas:
   seguridad 4, empleo 11, salud 6, educación 3, infraestructura 1, corrupción 4).
2. `build_segunda_vuelta.py`: emitir en el candidato `espriella` un bloque
   nuevo `programa_1v`:
   - misma estructura de sectores candidateados (orden `CAND_SECTOR_ORDER`),
   - ids `espriella-<abbr>-cand1v-NN`,
   - campos: `titulo`, `texto`, `texto_resumen_medio`, `fuente` (candidateados,
     snapshot 1ª vuelta 2026-06-06),
   - **sin** `tags_terceros` poblados (read-only: sin banderas FEDe, sin puntaje).
   - Cepeda NO lleva `programa_1v` (su programa no cambió); la simetría se
     resuelve con copy, no con datos duplicados.
3. `meta.notas_metodologicas`: nota explicando la reescritura (29→63, sin
   continuidad textual, por eso se muestran ambas versiones sin mapeo).

## UI (`public/index.html`)

En `renderProblem`, dentro de la columna de Espriella, sobre sus propuestas
candidateados:

```
⟳ Programa reescrito para 2ª vuelta (29 → 63 propuestas)
Vista: [● 1ª vs 2ª] [○ Solo actual]
■ 2ª vuelta — programa actual (N)     ← tarjetas vivas (puntaje, FEDe)
□ 1ª vuelta — reemplazado (M)         ← tarjetas compactas de archivo
```

- **Aviso** sobrio (no alerta roja), una sola vez por columna.
- **Segmented control** con el lenguaje visual existente (radios, tipografía,
  `aria-pressed`); etiquetas «1ª vs 2ª» / «Solo actual»; conteos en el
  encabezado, no en los botones.
- **Bloque de archivo**: tarjetas atenuadas (sepia sutil, borde punteado),
  título + «ver texto» expandible; sin botones de puntaje ni capa FEDe.
  Solo las propuestas de 1ª vuelta de los sectores mapeados al problema
  (`PROBLEM_SECTORS[problema].cand`), igual que las actuales.
- **Transición**: colapso/expansión animada (~200 ms, `grid-template-rows`
  o `max-height` + fade), respetando `prefers-reduced-motion`. Sin saltos.
- **Persistencia**: preferencia de vista en `localStorage`
  (`brujula_v5_vista_programa`), sincronizada entre problemas y sesiones.
- **Simetría**: en la columna de Cepeda, línea sobria «Programa sin cambios
  entre vueltas». Solo en problemas donde Espriella muestra su aviso.
- **Copy desactualizado**: corregir "Fuentes" (`index.html` ~línea 477) que
  dice "los programas oficiales no cambiaron" — ya es falso.
- Móvil: misma mecánica (la columna ya es single-column); auditar a 360/390 px.

## Lo que NO se hace (a propósito)

- No hay mapeo propuesta↔propuesta entre versiones (sería inferencia nuestra).
- No se tocan: propuestas FEDe, posiciones, puntaje, Cepeda (salvo la línea de
  simetría), pipeline v4, corpus de 1ª vuelta (`propuestas-2026.json`).
- Las propuestas de 1ª vuelta NO son seleccionables en "Mi puntaje" (programa
  reemplazado; votar por propuestas retiradas confundiría el puntaje).

## Verificación

1. `python3 data/build_segunda_vuelta.py` determinista; diff del JSON solo
   agrega `programa_1v` + nota metodológica.
2. Extraer `<script>` de index.html → `node --check`.
3. Servir local (`python3 -m http.server 8000 -d public`) y verificar con
   Chrome headless / screenshot: toggle, ambas vistas, móvil 360 px.
4. Revisión visual final de Sergio en el preview del PR #4.

## Progreso

- [x] Spec validado con Sergio (2026-06-11)
- [x] Congelar `candidateados_1v.json` + build `programa_1v` (29 props, determinista)
- [x] UI: aviso + toggle + bloque archivo + simetría + copy fuentes
- [x] Verificación: `node --check` OK; Chromium headless: toggle colapsa/expande,
      preferencia persiste entre problemas y sesiones, archivo expandible,
      sin overflow a 360 px, 0 errores de consola
- [ ] Push a PR #4 y revisión visual de Sergio en el preview

## Decision Log

- **Lado a lado → apilado dentro de la columna**: las propuestas solo se
  renderizan por problema en columnas por candidato; dos sub-columnas no caben
  (ni en móvil). "Lado a lado" se materializa como bloque de archivo compacto
  bajo el programa vigente, con toggle.
- **Default = vista comparada**: decisión explícita de Sergio (que el cambio
  sea visible de entrada); un clic la quita y se recuerda la preferencia.
- **Sin mapeo editorial**: elegido por Sergio entre 3 opciones (mapeo curado /
  solo resumen / lado a lado). Cero juicio nuestro.

## Surprises & Discoveries

- El programa nuevo es reescritura total (0/29 con continuidad textual).
- v5 no tiene vista "programa por candidato": todo pasa por
  `PROBLEM_SECTORS` en "Comparar por problema".
- El copy de Fuentes quedó desactualizado al adoptar el programa de 2ª vuelta.
