# Cobertura — Brújula Electoral 2026

**Fecha de consulta:** 2026-05-28
**Entregable:** `propuestas-2026.json` (873 KB, 12 candidatos, 616 propuestas)

> Documento de cobertura, no de análisis. No contiene rankings ni conclusiones.

## Fuentes efectivamente usadas

| Fuente | Método de extracción | Qué aportó |
|---|---|---|
| **Candidateados** (`candidateados.com`) | App Router Next.js. Datos embebidos en el payload RSC (`self.__next_f`) del HTML inicial; decodificado y parseado a JSON. **No se necesitó browser headless.** | 12 candidatos · 6 sectores · 415 propuestas con 3 niveles de profundidad (simple/medio/complejo) + bio + perfil. |
| **FEDe** (`propuestascandidatos.fedecolombia.org`) | App JS plano que lee un Google Sheet público vía export CSV (`gviz/tq?out:csv`). Se descargaron las 7 pestañas. | 5 candidatos · 5 sectores · 201 propuestas con **URL de fuente oficial**, 19 banderas Alerta/Amenaza con explicación, 171 comentarios de 12 expertos nombrados, evaluación por sector (precisión/viabilidad/coherencia), 4 red flags. |
| **Web (WebSearch)** | Búsqueda puntual de fórmulas vicepresidenciales. | Fórmula VP de los 7 candidatos no cubiertos por FEDe + nota de retiro de Caicedo. |

## Estado por candidato

| id | Candidateados | FEDe (atribución) | Fórmula VP | Notas |
|---|---|---|---|---|
| valencia | 58 props (6 sec) | ✅ 61 props · 4 banderas · 48 coment. | ✅ FEDe | completo |
| cepeda | 97 props (6 sec) | ✅ 28 props · 4 banderas · 32 coment. | ✅ FEDe | completo |
| lopez | 35 props (6 sec) | ✅ 28 props · 3 banderas · 25 coment. | ✅ FEDe | completo |
| espriella | 29 props (6 sec) | ✅ 42 props · 7 banderas · 37 coment. | ✅ FEDe | completo |
| fajardo | 70 props (6 sec) | ✅ 42 props · 1 bandera · 29 coment. | ✅ FEDe | completo |
| botero | 8 props (5/6 sec) | ❌ no cubierto por FEDe | ✅ web | sin capa de atribución |
| lizcano | 23 props (4/6 sec) | ❌ no cubierto por FEDe | ✅ web | sin capa de atribución |
| uribe | 26 props (6 sec) | ❌ no cubierto por FEDe | ✅ web | sin capa de atribución |
| macollins | 33 props (6 sec) | ❌ no cubierto por FEDe | ✅ web | sin capa de atribución |
| barreras | 26 props (6 sec) | ❌ no cubierto por FEDe | ✅ web | sin capa de atribución |
| matamoros | 9 props (5/6 sec) | ❌ no cubierto por FEDe | ✅ web | sin capa de atribución |
| caicedo | **1 prop** (1/6 sec) | ❌ no cubierto por FEDe | ✅ web | **se retiró de la contienda** (sigue en tarjetón, votos no se cuentan; fuente: El Espectador). Explica la escasez de propuestas documentadas. |

## Vacíos explícitos (no rellenados, por imparcialidad)

1. **Capa de atribución (banderas + expertos) solo existe para 5 candidatos.** FEDe únicamente analiza a valencia, cepeda, lopez, espriella y fajardo. Para los otros 7 **no hay** banderas de constitucionalidad ni comentarios de expertos en las fuentes consultadas → sus `tags_terceros` quedan en `null`/vacío. Esta asimetría es de las fuentes, no de la extracción: la profundidad de búsqueda fue la misma para todos.
2. **`posicion_ideologica_autodescrita` vacía para los 12.** Ninguna fuente la expone de forma textual y autodescrita; no se infirió.
3. **`viabilidad_senalada` = `null` por propuesta.** Ninguna fuente consultada entrega alerta de viabilidad fiscal/legal *por propuesta*. La evaluación de viabilidad de FEDe es *por sector* y se guardó en `evaluacion_fede` (con su rating de precisión/viabilidad/coherencia, atribuido a FEDe).
4. **Sectores asimétricos entre fuentes.** Candidateados usa 6 sectores (seguridad, salud, educación, empleo, infraestructura, corrupción); FEDe usa 5 (seguridad, salud, energía, tierras y agro, institucional). Solo coinciden seguridad y salud. No se forzó equivalencia entre `corrupción` (Candidateados) e `institucional` (FEDe): se mantienen separados.
5. **Programas oficiales no archivados.** Se conservan las URLs (`programa_url` y campo `fuente` de cada propuesta FEDe) pero no se descargaron los PDF como respaldo local.
6. **Fuentes de verificación (El Tiempo, Razón Pública, La Silla Vacía, El Espectador) no minadas exhaustivamente.** Solo se usó WebSearch para fórmulas VP y el retiro de Caicedo. No se añadieron alertas de viabilidad de estos medios para no introducir asimetría (no cubren a los 12 por igual). Es la extensión natural pendiente si se quiere reforzar la capa de viabilidad atribuida.
7. **Cobertura de "14 candidatos oficiales".** La Registraduría reporta 14 fórmulas inscritas para el 31-may-2026; Candidateados y FEDe rastrean 12. El JSON cubre esos 12.

## Decisiones de estructura (documentadas)

- **Fuentes NO fusionadas.** Cada propuesta conserva su fuente real. Las banderas de FEDe **no** se trasladan a propuestas de Candidateados (hacerlo exigiría emparejar textos entre fuentes = inferencia). Por eso cada candidato tiene bloques de sector separados por `fuente_origen` (`candidateados` / `fede`).
- **`subtema` a nivel de propuesta** (no de bloque, como en el esquema base): FEDe provee subtema por propuesta y así es más fiel. Candidateados no trae subtema → `""`.
- **`texto` fiel.** Candidateados: `editado=false` (se copia su texto verbatim; aun así Candidateados es un *agregador secundario*, marcado en `fuente`). FEDe: `editado=true` (la `descripcion` es una síntesis de FEDe; el texto original está en la URL de `fuente`).
- **`constitucionalidad.nivel`** es un **mapeo mecánico y transparente** del texto de FEDe: default `contestado` para toda bandera; se eleva a `tumbado_por_corte` solo si la explicación cita explícitamente un fallo de la Corte. La explicación verbatim de FEDe queda siempre en `detalle` y `fuente`. Resultado: 18 `contestado` + 1 `tumbado_por_corte` (Cepeda, Ley de Paz Total, C-036/2025).
- **Sin bandera de fuente nombrada ⇒ `null`.** No se asume `sin_objecion`: ausencia de bandera ≠ aval.

## Reproducibilidad

```
raw/                      # insumos crudos
  candidateados_parsed.json  # 12 candidatos parseados del RSC
  fede_csv/*.csv             # 7 pestañas del Google Sheet de FEDe
  vp_web.json                # fórmulas VP (FEDe + web)
build_propuestas.py       # builder determinista (sin red): raw/ -> propuestas-2026.json
propuestas-2026.json      # entregable
```

Ejecutar: `python3 build_propuestas.py` (no requiere red; trabaja sobre `raw/`).
