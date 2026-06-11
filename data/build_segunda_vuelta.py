#!/usr/bin/env python3
"""
Brújula Electoral 2026 — builder de SEGUNDA VUELTA (determinista).

Genera public/propuestas-2026-segunda-vuelta.json con la MISMA estructura del
corpus de primera vuelta (build_propuestas.py) pero SOLO para los dos finalistas
(Iván Cepeda y Abelardo de la Espriella), más:
  - campos nuevos de candidato del sheet FEDe de 2ª vuelta (educacion, foto, color_fede)
  - bloque `posiciones_fede`: matriz cara-a-cara (preguntas + respuesta de cada uno)
  - meta con resultados de 1ª vuelta y apoyos (datos con fuente)

Fuentes:
  - Candidateados: snapshot CONGELADO de 2ª vuelta en data/raw/candidateados_2v.json.
    Candidateados.com actualizó el programa de De la Espriella para 2ª vuelta (Cepeda no
    cambió). Se usa un archivo PROPIO de v5 —no el data/raw/candidateados_parsed.json que el
    cron de v4 pisa dos veces al día— para que la build de v5 sea estable y reproducible.
    Para re-congelar a una fecha nueva: cp candidateados_parsed.json candidateados_2v.json.
  - FEDe: sheet nuevo refrescado en data/raw/fede2_csv/ (SHEET_ID 116rf6...).

No infiere veredictos: texto fiel, cada bandera atribuida a FEDe. No fusiona fuentes.
NO toca public/propuestas-2026.json (corpus de 1ª vuelta) ni el pipeline v4.
Solo stdlib.
"""
import csv, json, re, os
from collections import defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(_HERE, "raw")
FEDE_DIR = os.path.join(RAW, "fede2_csv")
OUT = os.path.join(_HERE, "..", "public", "propuestas-2026-segunda-vuelta.json")
FECHA = "2026-06-09"
FECHA_ELECCION = "2026-06-21"
SHEET_FEDE = "116rf6RK1l5kqredZKK47F55tif2GGw2474vKdZUPrFM"

# Solo los dos finalistas.
SV_IDS = ["cepeda", "espriella"]

# --- mapeos (duplicados de build_propuestas.py a propósito: ese módulo ejecuta
#     su build de 1ª vuelta al importarse, así que no se puede importar sin efectos). ---
SLUG2ID = {
    "ivan-cepeda-castro":       "cepeda",
    "abelardo-de-la-espriella": "espriella",
}
FEDE_SECTOR = {
    "Seguridad":      "seguridad",
    "Salud":          "salud",
    "Energía":        "energia",
    "Tierras y Agro": "tierras_y_agro",
    "Institucional":  "institucional",
}
# nombre de sector FEDe -> clave canónica para las preguntas/posiciones
PREG_SECTOR = dict(FEDE_SECTOR)
SEMAFORO_LABEL = {"rojo": "Amenaza", "amarillo": "Alerta", "": ""}
CAND_SECTOR_ORDER = ["seguridad", "salud", "educacion", "empleo", "infraestructura", "corrupcion"]
FEDE_SECTOR_ORDER = ["seguridad", "salud", "energia", "tierras_y_agro", "institucional"]


def abbr(sec):
    return {"seguridad": "seg", "salud": "sal", "educacion": "edu", "empleo": "emp",
            "infraestructura": "inf", "corrupcion": "cor", "energia": "ene",
            "tierras_y_agro": "tie", "institucional": "ins"}[sec]


def clasificar_constitucionalidad(texto):
    """Mapeo MECÁNICO del texto de FEDe a un nivel del enum (igual que v4).
    Default 'contestado'; 'tumbado_por_corte' solo si cita fallo de la Corte."""
    t = texto.lower()
    if re.search(r"declar[óo]\s+inconstitucional|declar[óo]\s+inexequible|inexequib|"
                 r"corte constitucional.{0,60}(inconstitucional|tumb|declar[óo] nul)", t):
        return "tumbado_por_corte"
    return "contestado"


def load_csv(name):
    with open(os.path.join(FEDE_DIR, f"{name}.csv"), encoding="utf-8") as f:
        return list(csv.DictReader(f))


# --------------------------------------------------------------------------
cand = json.load(open(os.path.join(RAW, "candidateados_2v.json"), encoding="utf-8"))
cand_by_id = {SLUG2ID[c["slug"]]: c for c in cand if c["slug"] in SLUG2ID}

# Programa de 1ª vuelta de De la Espriella: snapshot del cron ANTERIOR a la
# reescritura (2026-06-06, git b34cdbe). Candidateados reemplazó su programa para
# 2ª vuelta (29->63) SIN continuidad textual (0/29 propuestas con match), así que
# se publican ambas versiones fieles, sin mapeo editorial entre ellas.
cand_1v = json.load(open(os.path.join(RAW, "candidateados_1v.json"), encoding="utf-8"))
FECHA_SNAPSHOT_1V = "2026-06-06"

fede_cands = {c["id"]: c for c in load_csv("candidatos")}
fede_props = load_csv("propuestas")
fede_expertos = {e["id"]: e for e in load_csv("expertos")}
fede_coment = load_csv("comentarios_expertos")
fede_redflags = load_csv("red_flags")
fede_resumen = load_csv("resumen_sectores")
fede_preguntas = load_csv("preguntas")
fede_posiciones = load_csv("posiciones")

# comentarios de expertos por propuesta_id
coment_by_prop = defaultdict(list)
for c in fede_coment:
    exp = fede_expertos.get(c["experto_id"], {})
    coment_by_prop[c["propuesta_id"]].append({
        "experto": exp.get("nombre", c["experto_id"]),
        "rol": exp.get("rol", ""),
        "comentario": c["comentario"],
        "fuente": "FEDe (comentarios_expertos)",
    })

# resumen de sector FEDe por (candidato, sector_canonico)
resumen_by = {}
for r in fede_resumen:
    sec = FEDE_SECTOR.get(r["sector"].strip())
    if sec:
        resumen_by[(r["candidato_id"], sec)] = r

# red flags por candidato (solo visibles)
rf_by = defaultdict(list)
for r in fede_redflags:
    if r.get("visible", "si") == "si":
        rf_by[r["candidato_id"]].append({
            "titulo": r["titulo"], "meta": r["meta"], "badge": r["badge"],
            "url_video": r["url_video"], "fuente": "FEDe (red_flags)",
        })

# propuestas FEDe agrupadas por (candidato, sector_canonico), solo visibles
fede_props_by = defaultdict(list)
for p in fede_props:
    if p.get("visible", "si") != "si":
        continue
    sec = FEDE_SECTOR.get(p["tema"].strip())
    if sec:
        fede_props_by[(p["candidato_id"], sec)].append(p)


def build_candidateados_blocks(cid):
    """Bloques de los 6 sectores de Candidateados (idénticos a v4)."""
    c = cand_by_id[cid]
    secs = c["card"]["sectors"]
    sectores = []
    for sec in CAND_SECTOR_ORDER:
        block = secs.get(sec)
        propuestas = []
        if block and block.get("hasContent"):
            for i, p in enumerate(block.get("proposals", []), 1):
                texto = p.get("complexBody") or p.get("mediumBody") or p.get("title") or ""
                propuestas.append({
                    "id": f"{cid}-{abbr(sec)}-cand-{i:02d}",
                    "titulo": p.get("title", ""),
                    "subtema": "",
                    "texto": texto.strip(),
                    "texto_resumen_medio": p.get("mediumBody", "").strip(),
                    "editado": False,
                    "fuente": "candidateados (agregador; texto derivado del programa/entrevistas del candidato)",
                    "tags_terceros": {"constitucionalidad": None, "viabilidad_senalada": None,
                                      "comentarios_expertos": []},
                })
        sectores.append({
            "sector": sec,
            "fuente_origen": "candidateados",
            "subtema": "",
            "resumen_fuente": (block.get("simpleParagraph", "").strip() if block else ""),
            "evaluacion_fede": None,
            "propuestas": propuestas,
            "nota": "" if propuestas else "sin propuesta documentada en esta fuente",
        })
    return sectores


def build_programa_1v():
    """Bloque `programa_1v` (solo Espriella): su programa de 1ª vuelta, reemplazado.
    Solo lectura en la UI: sin banderas FEDe ni selección de puntaje. Cepeda no
    lleva este bloque porque mantuvo su programa entre vueltas."""
    esp = next(c for c in cand_1v if c["slug"] == "abelardo-de-la-espriella")
    secs = esp["card"]["sectors"]
    sectores = []
    for sec in CAND_SECTOR_ORDER:
        block = secs.get(sec)
        propuestas = []
        if block and block.get("hasContent"):
            for i, p in enumerate(block.get("proposals", []), 1):
                texto = p.get("complexBody") or p.get("mediumBody") or p.get("title") or ""
                propuestas.append({
                    "id": f"espriella-{abbr(sec)}-cand1v-{i:02d}",
                    "titulo": p.get("title", ""),
                    "texto": texto.strip(),
                    "texto_resumen_medio": p.get("mediumBody", "").strip(),
                    "fuente": "candidateados (agregador; snapshot de 1ª vuelta)",
                })
        if propuestas:
            sectores.append({"sector": sec, "propuestas": propuestas})
    return {
        "fecha_snapshot": FECHA_SNAPSHOT_1V,
        "nota": ("Programa de 1ª vuelta, reemplazado: Candidateados adoptó el programa "
                 "reescrito de De la Espriella para 2ª vuelta (29->63 propuestas) sin "
                 "continuidad textual entre versiones. Se muestran ambas, sin mapeo editorial."),
        "fuente": f"candidateados (snapshot del {FECHA_SNAPSHOT_1V}, previo a la reescritura)",
        "sectores": sectores,
    }


def build_fede_blocks(cid):
    """Bloques de los 5 sectores FEDe (sheet de 2ª vuelta)."""
    sectores = []
    for sec in FEDE_SECTOR_ORDER:
        plist = fede_props_by.get((cid, sec), [])
        rs = resumen_by.get((cid, sec))
        propuestas = []
        for i, p in enumerate(plist, 1):
            tags = {"constitucionalidad": None, "viabilidad_senalada": None,
                    "comentarios_expertos": coment_by_prop.get(p["id"], [])}
            sem = p.get("semaforo", "").strip()
            if sem in ("rojo", "amarillo"):
                expl = p.get("alerta_explicacion", "").strip()
                tags["constitucionalidad"] = {
                    "nivel": clasificar_constitucionalidad(expl),
                    "bandera": SEMAFORO_LABEL[sem],
                    "detalle": expl,
                    "fuente": "FEDe — análisis al Estado de Derecho",
                }
            propuestas.append({
                "id": f"{cid}-{abbr(sec)}-fede-{i:02d}",
                "titulo": p.get("titulo", ""),
                "subtema": p.get("subtema", "").strip(),
                "texto": p.get("descripcion", "").strip(),
                "texto_resumen_medio": "",
                "editado": True,
                "fuente": (p.get("fuente", "").strip() or "FEDe"),
                "tags_terceros": tags,
            })
        evaluacion, resumen_txt = None, ""
        if rs:
            evaluacion = {
                "precision": rs.get("precision", "").strip(),
                "viabilidad": rs.get("viabilidad", "").strip(),
                "coherencia": rs.get("coherencia", "").strip(),
                "subtitulo": rs.get("subtitulo", "").strip(),
                "fuente": "FEDe (resumen_sectores)",
            }
            resumen_txt = rs.get("resumen", "").strip()
        sectores.append({
            "sector": sec,
            "fuente_origen": "fede",
            "subtema": "",
            "resumen_fuente": resumen_txt,
            "evaluacion_fede": evaluacion,
            "propuestas": propuestas,
            "nota": "" if propuestas else "sin propuesta documentada en esta fuente",
        })
    return sectores


# --------------------------------------------------------------------------
out = {"meta": {}, "candidatos": [], "posiciones_fede": []}

for cid in SV_IDS:
    cc = cand_by_id[cid]            # candidateados (perfil + sectores)
    fc = fede_cands.get(cid, {})    # FEDe (campos nuevos)
    sectores = build_candidateados_blocks(cid) + build_fede_blocks(cid)
    out["candidatos"].append({
        "id": cid,
        "nombre": cc["fullName"],
        "partido": cc.get("party", ""),
        "formula_vp": fc.get("formula_vp", "").strip(),
        "formula_vp_fuente": "FEDe (candidatos) / programa oficial",
        "posicion_ideologica_autodescrita": "",
        # `bio`: perfil corto de Candidateados (tamaño de tarjeta).
        # `biografia_fede`: perfil de FEDe, más detallado y factual (mismo origen
        # para ambos candidatos -> simétrico por construcción). Ambos atribuidos.
        "bio": cc.get("compareBio", "").strip(),
        "biografia_fede": fc.get("biografia", "").strip(),
        "educacion": fc.get("educacion", "").strip(),
        "foto": f"img/{cid}.webp",
        "color_fede": fc.get("color_hex", "").strip(),
        "programa_url": "",  # se completa abajo con la fuente FEDe más frecuente
        "cubierto_por": ["candidateados", "fede"],
        "notas": [],
        "red_flags_fede": rf_by.get(cid, []),
        "sectores": sectores,
        # programa de 1ª vuelta (solo Espriella; ver build_programa_1v)
        "programa_1v": build_programa_1v() if cid == "espriella" else None,
    })

# programa_url: el más frecuente entre las fuentes FEDe del candidato (como v4)
prog_url = defaultdict(lambda: defaultdict(int))
for p in fede_props:
    f = p.get("fuente", "").strip()
    if f.startswith("http"):
        prog_url[p["candidato_id"]][f] += 1
for c in out["candidatos"]:
    urls = prog_url.get(c["id"], {})
    c["programa_url"] = max(urls.items(), key=lambda kv: kv[1])[0] if urls else ""

# ---- posiciones_fede: matriz cara-a-cara (preguntas + respuestas de ambos) ----
preg_by_id = {p["id"]: p for p in fede_preguntas if p.get("visible", "si") == "si"}
resp_by = defaultdict(dict)  # pregunta_id -> {cid: respuesta}
for r in fede_posiciones:
    if r.get("visible", "si") != "si":
        continue
    if r["candidato_id"] in SV_IDS:
        resp_by[r["pregunta_id"]][r["candidato_id"]] = r["respuesta"].strip()

# Mapeo CURADO pregunta -> propuesta con bandera (ambas son de FEDe; conectamos
# dos salidas de FEDe sobre la MISMA política, no fusionamos fuentes distintas).
# Solo matches inequívocos (política idéntica). Los más generales o cross-sector
# se omiten a propósito; siguen visibles en "Comparar por problema".
POSICION_BANDERAS = {
    "pr001": {"cepeda": "cepeda-seg-fede-01", "espriella": "espriella-seg-fede-04"},
    "pr002": {"espriella": "espriella-seg-fede-03"},
    "pr004": {"espriella": "espriella-seg-fede-02"},
    "pr005": {"cepeda": "cepeda-sal-fede-01"},
    "pr014": {"espriella": "espriella-ene-fede-05"},
}

# Mapeo CURADO pregunta -> propuestas del programa de 1ª VUELTA de Espriella
# (candidateados_1v) sobre la MISMA política. Yuxtaposición sin veredicto: se
# muestra el texto fiel de entonces y el elector compara; NO afirmamos "cambió
# de posición" (ninguna fuente documenta el antes/después como cambio). Solo
# matches inequívocos; lista vacía => su programa de 1ª vuelta (Candidateados)
# no documentaba posición sobre ese punto, y la UI lo dice tal cual.
POSICION_PROGRAMA_1V = {
    "pr002": ["espriella-seg-cand1v-02"],  # fumigación aérea / cultivos
    "pr005": ["espriella-sal-cand1v-05"],  # EPS (1v: "las que no cumplan se liquidan")
    "pr006": ["espriella-sal-cand1v-01"],  # acceso a medicamentos
    "pr008": ["espriella-sal-cand1v-04", "espriella-sal-cand1v-01"],  # talento humano salud
    "pr010": ["espriella-emp-cand1v-01"],  # hidrocarburos
    "pr011": ["espriella-emp-cand1v-01"],  # fracking ("apoyo al fracking con responsabilidad")
}
# índice de propuestas con bandera, por id (para adjuntar el detalle atribuido)
flag_by_propid = {}
for c in out["candidatos"]:
    for s in c["sectores"]:
        for p in s["propuestas"]:
            b = p["tags_terceros"]["constitucionalidad"]
            if b:
                flag_by_propid[p["id"]] = {
                    "propuesta_id": p["id"],
                    "propuesta_titulo": p["titulo"],
                    "nivel": b["nivel"],
                    "bandera": b["bandera"],
                    "detalle": b["detalle"],
                    "fuente": b["fuente"],
                }

# índice de propuestas del programa de 1ª vuelta de Espriella (para resolver el mapeo)
prog1v_by_id = {}
for c in out["candidatos"]:
    if c.get("programa_1v"):
        for s in c["programa_1v"]["sectores"]:
            for p in s["propuestas"]:
                prog1v_by_id[p["id"]] = p
for pid, ids in POSICION_PROGRAMA_1V.items():
    for propid in ids:
        assert propid in prog1v_by_id, f"POSICION_PROGRAMA_1V: id inexistente {propid}"

posiciones = []
for pid, preg in preg_by_id.items():
    sec = PREG_SECTOR.get(preg["sector"].strip())
    respuestas = resp_by.get(pid, {})
    # solo si ambos respondieron (simetría)
    if all(cid in respuestas for cid in SV_IDS):
        # banderas relacionadas (curadas): solo si la propuesta existe y sigue marcada
        banderas = {}
        for cid, propid in POSICION_BANDERAS.get(pid, {}).items():
            if propid in flag_by_propid:
                banderas[cid] = flag_by_propid[propid]
        posiciones.append({
            "pregunta_id": pid,
            "sector": sec,
            "pregunta": preg["pregunta"].strip(),
            "respuestas": {cid: respuestas[cid] for cid in SV_IDS},
            # relación temática NUESTRA hacia una propuesta marcada por FEDe (no la marcó FEDe sobre esta respuesta)
            "banderas_relacionadas": banderas,
            # yuxtaposición (relación temática NUESTRA): qué decía el programa de
            # 1ª vuelta de Espriella sobre esta política; [] = sin posición documentada
            "programa_1v_espriella": [
                {"propuesta_id": p["id"], "titulo": p["titulo"], "texto": p["texto"], "fuente": p["fuente"]}
                for p in (prog1v_by_id[i] for i in POSICION_PROGRAMA_1V.get(pid, []))
            ],
            "fuente": "FEDe (preguntas / posiciones)",
        })
# orden por sector (orden FEDe) y luego por id de pregunta
sec_rank = {s: i for i, s in enumerate(FEDE_SECTOR_ORDER)}
posiciones.sort(key=lambda x: (sec_rank.get(x["sector"], 99), x["pregunta_id"]))
out["posiciones_fede"] = posiciones

# ---- meta ----
out["meta"] = {
    "proyecto": "Brújula Electoral 2026 — segunda vuelta",
    "vuelta": "segunda",
    "fecha_consulta": FECHA,
    "fecha_eleccion": FECHA_ELECCION,
    "sheet_fede": SHEET_FEDE,
    "fuentes_usadas": [
        "candidateados (snapshot de 2ª vuelta; programa de De la Espriella actualizado, Cepeda igual)",
        "fede (sheet de 2ª vuelta, 5 candidatos -> filtrado a 2)",
        "programa_oficial (vía fuente FEDe)",
        "Registraduría Nacional (resultados 1ª vuelta)",
    ],
    "candidatos_incluidos": SV_IDS,
    "resultados_primera_vuelta": {
        "fecha": "2026-05-31",
        "fuente": "Registraduría Nacional del Estado Civil (preconteo oficial)",
        "datos": {
            "espriella": {"votos": 10361499, "pct": "43,74%"},
            "cepeda": {"votos": 9688348, "pct": "40,90%"},
        },
        "nota": "Ninguno alcanzó la mayoría absoluta (50 %+1); por eso hay segunda vuelta.",
    },
    "apoyos": {
        "cepeda": [
            {"nombre": "Roy Barreras", "cargo": "excandidato presidencial",
             "fuente": "anuncio público (1-jun-2026)"},
        ],
        "espriella": [
            {"nombre": "Paloma Valencia", "cargo": "senadora, Centro Democrático",
             "fuente": "anuncio público (1-jun-2026)"},
        ],
    },
    "notas_metodologicas": [
        "Solo los dos finalistas de segunda vuelta (Cepeda, De la Espriella).",
        "Candidateados actualizó el programa de De la Espriella para 2ª vuelta (29->63 propuestas); Cepeda no cambió. Snapshot congelado en candidateados_2v.json.",
        "programa_1v (solo Espriella): su programa de 1ª vuelta (snapshot 2026-06-06, previo a la reescritura). 0/29 propuestas tienen continuidad textual con las 63 nuevas; por eso se muestran ambas versiones fieles SIN mapeo editorial entre ellas.",
        "posiciones_fede[].programa_1v_espriella: yuxtaposición curada (relación temática nuestra) entre cada pregunta y lo que el programa de 1ª vuelta de Espriella decía sobre esa política. Sin veredicto: no se afirma que 'cambió de posición' (ninguna fuente lo documenta); lista vacía = su programa de 1ª vuelta no documentaba posición sobre ese punto.",
        "FEDe sí actualizó (sheet nuevo) y mantiene 5 candidatos en su panel; aquí se filtra a 2.",
        "posiciones_fede: matriz cara-a-cara nueva de FEDe (preguntas con la respuesta de cada candidato). Atribuida a FEDe.",
        "Resultados y apoyos llevan fuente; los apoyos se detallan con enlace en hitos.json.",
        "Texto fiel; fuentes NO fusionadas; banderas/comentarios atribuidos a FEDe; sin bandera => constitucionalidad null.",
        "Se incluyen dos perfiles atribuidos por candidato: bio (Candidateados, corto) y biografia_fede (FEDe, detallado y factual). Mismo origen para ambos candidatos en cada campo.",
    ],
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---- resumen de cobertura para consola ----
print(f"OK -> {os.path.relpath(OUT)}")
for c in out["candidatos"]:
    nc = sum(len(s["propuestas"]) for s in c["sectores"] if s["fuente_origen"] == "candidateados")
    nf = sum(len(s["propuestas"]) for s in c["sectores"] if s["fuente_origen"] == "fede")
    fl = sum(1 for s in c["sectores"] for p in s["propuestas"] if p["tags_terceros"]["constitucionalidad"])
    cm = sum(len(p["tags_terceros"]["comentarios_expertos"]) for s in c["sectores"] for p in s["propuestas"])
    print(f"  {c['id']:10} cand={nc:3} fede={nf:3} banderas={fl:2} coment_exp={cm:3} "
          f"vp={'si' if c['formula_vp'] else 'NO'} foto={c['foto']} rf={len(c['red_flags_fede'])}")
print(f"  posiciones_fede: {len(out['posiciones_fede'])} preguntas cara-a-cara")
