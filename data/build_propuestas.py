#!/usr/bin/env python3
"""
Brújula Electoral 2026 — builder determinista.
Fusiona Candidateados (amplia, 12 candidatos) + FEDe (profunda, atribuida, 5 candidatos)
en un único JSON. No infiere veredictos: copia texto fiel y atribuye cada bandera a su fuente.
"""
import csv, json, re, os
from collections import defaultdict

# Paths relativos a la ubicación del script (data/), no al cwd.
_HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(_HERE, "raw")
OUT = os.path.join(_HERE, "..", "public", "propuestas-2026.json")
FECHA = "2026-05-28"

# ---- mapeo slug Candidateados -> id canónico + id FEDe -------------------
SLUG2ID = {
    "paloma-valencia-laserna": "valencia",
    "ivan-cepeda-castro":       "cepeda",
    "claudia-lopez-hernandez":  "lopez",
    "santiago-botero-jaramillo":"botero",
    "abelardo-de-la-espriella": "espriella",
    "mauricio-lizcano-arango":  "lizcano",
    "miguel-uribe-londono":     "uribe",
    "sondra-macollins":         "macollins",
    "roy-barreras-montealegre": "barreras",
    "carlos-caicedo-omar":      "caicedo",
    "gustavo-matamoros-camacho":"matamoros",
    "sergio-fajardo-valderrama":"fajardo",
}
# candidatos cubiertos por FEDe (mismo id canónico)
FEDE_IDS = {"valencia","cepeda","lopez","espriella","fajardo"}

# sector FEDe (tema) -> clave canónica de sector
FEDE_SECTOR = {
    "Seguridad":      "seguridad",
    "Salud":          "salud",
    "Energía":        "energia",
    "Tierras y Agro": "tierras_y_agro",
    "Institucional":  "institucional",
}
SEMAFORO_LABEL = {"rojo": "Amenaza", "amarillo": "Alerta", "": ""}

def load_csv(name):
    with open(f"{RAW}/fede_csv/{name}.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def clasificar_constitucionalidad(texto):
    """Mapeo MECÁNICO y transparente del texto de FEDe a un nivel del enum.
    No es juicio propio: la explicación verbatim de FEDe queda siempre en `detalle`.
    Default para toda bandera = 'contestado' (FEDe objeta). Solo se eleva a
    'tumbado_por_corte' si la explicación cita explícitamente fallo de la Corte."""
    t = texto.lower()
    if re.search(r"declar[óo]\s+inconstitucional|declar[óo]\s+inexequible|inexequib|"
                 r"corte constitucional.{0,60}(inconstitucional|tumb|declar[óo] nul)", t):
        return "tumbado_por_corte"
    return "contestado"

def abbr(sec):
    return {"seguridad":"seg","salud":"sal","educacion":"edu","empleo":"emp",
            "infraestructura":"inf","corrupcion":"cor","energia":"ene",
            "tierras_y_agro":"tie","institucional":"ins"}[sec]

# --------------------------------------------------------------------------
cand = json.load(open(f"{RAW}/candidateados_parsed.json", encoding="utf-8"))
vp   = json.load(open(f"{RAW}/vp_web.json", encoding="utf-8"))

fede_cands = {c["id"]: c for c in load_csv("candidatos")}
fede_props = load_csv("propuestas")
fede_expertos = {e["id"]: e for e in load_csv("expertos")}
fede_coment = load_csv("comentarios_expertos")
fede_redflags = load_csv("red_flags")
fede_resumen = load_csv("resumen_sectores")

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

# red flags por candidato
rf_by = defaultdict(list)
for r in fede_redflags:
    if r.get("visible","si") == "si":
        rf_by[r["candidato_id"]].append({
            "titulo": r["titulo"], "meta": r["meta"], "badge": r["badge"],
            "url_video": r["url_video"], "fuente": "FEDe (red_flags)",
        })

# programa_url más frecuente por candidato FEDe (de propuestas.fuente)
prog_url = defaultdict(lambda: defaultdict(int))
for p in fede_props:
    f = p["fuente"].strip()
    if f.startswith("http"):
        prog_url[p["candidato_id"]][f] += 1
def best_prog(cid):
    if cid in prog_url and prog_url[cid]:
        return max(prog_url[cid].items(), key=lambda kv: kv[1])[0]
    return ""

# propuestas FEDe agrupadas por (candidato, sector_canonico)
fede_props_by = defaultdict(list)
for p in fede_props:
    if p.get("visible","si") != "si":
        continue
    sec = FEDE_SECTOR.get(p["tema"].strip())
    if sec:
        fede_props_by[(p["candidato_id"], sec)].append(p)

# notas factuales a nivel candidato (con fuente)
NOTAS = {
    "caicedo": [{
        "nota": "Carlos Caicedo se retiró de la contienda para sumarse a Iván Cepeda; "
                "su candidatura permanece en el tarjetón pero sus votos no se cuentan ni se suman a otra campaña.",
        "fuente": "El Espectador (elecciones-colombia-2026), consulta 2026-05-28",
    }],
}

CAND_SECTOR_ORDER = ["seguridad","salud","educacion","empleo","infraestructura","corrupcion"]

# --------------------------------------------------------------------------
out = {"meta": {}, "candidatos": []}

for c in cand:
    cid = SLUG2ID[c["slug"]]
    es_fede = cid in FEDE_IDS
    sectores = []

    # ---- bloques Candidateados (los 6 sectores) ----
    secs = c["card"]["sectors"]
    for sec in CAND_SECTOR_ORDER:
        block = secs.get(sec)
        propuestas = []
        if block and block.get("hasContent"):
            for i, p in enumerate(block.get("proposals", []), 1):
                texto = p.get("complexBody") or p.get("mediumBody") or p.get("title") or ""
                propuestas.append({
                    "id": f"{cid}-{abbr(sec)}-cand-{i:02d}",
                    "titulo": p.get("title",""),
                    "subtema": "",
                    "texto": texto.strip(),
                    "texto_resumen_medio": p.get("mediumBody","").strip(),
                    "editado": False,
                    "fuente": "candidateados (agregador; texto derivado del programa/entrevistas del candidato)",
                    "tags_terceros": {"constitucionalidad": None, "viabilidad_senalada": None,
                                      "comentarios_expertos": []},
                })
        sectores.append({
            "sector": sec,
            "fuente_origen": "candidateados",
            "subtema": "",
            "resumen_fuente": (block.get("simpleParagraph","").strip() if block else ""),
            "evaluacion_fede": None,
            "propuestas": propuestas,
            "nota": "" if propuestas else "sin propuesta documentada en esta fuente",
        })

    # ---- bloques FEDe (5 sectores), solo si el candidato está en FEDe ----
    if es_fede:
        for sec in ["seguridad","salud","energia","tierras_y_agro","institucional"]:
            plist = fede_props_by.get((cid, sec), [])
            rs = resumen_by.get((cid, sec))
            propuestas = []
            for i, p in enumerate(plist, 1):
                tags = {"constitucionalidad": None, "viabilidad_senalada": None,
                        "comentarios_expertos": coment_by_prop.get(p["id"], [])}
                sem = p.get("semaforo","").strip()
                if sem in ("rojo","amarillo"):
                    label = SEMAFORO_LABEL[sem]
                    expl = p.get("alerta_explicacion","").strip()
                    tags["constitucionalidad"] = {
                        "nivel": clasificar_constitucionalidad(expl),
                        "detalle": f"[FEDe semáforo: {label}] {expl}",
                        "fuente": f"FEDe (semáforo {label} al Estado de Derecho)",
                    }
                propuestas.append({
                    "id": f"{cid}-{abbr(sec)}-fede-{i:02d}",
                    "titulo": p.get("titulo",""),
                    "subtema": p.get("subtema","").strip(),
                    "texto": p.get("descripcion","").strip(),
                    "texto_resumen_medio": "",
                    "editado": True,
                    "fuente": (p.get("fuente","").strip() or "FEDe") + " | vía FEDe",
                    "tags_terceros": tags,
                })
            evaluacion = None
            resumen_txt = ""
            if rs:
                evaluacion = {
                    "precision": rs.get("precision","").strip(),
                    "viabilidad": rs.get("viabilidad","").strip(),
                    "coherencia": rs.get("coherencia","").strip(),
                    "subtitulo": rs.get("subtitulo","").strip(),
                    "fuente": "FEDe (resumen_sectores)",
                }
                resumen_txt = rs.get("resumen","").strip()
            sectores.append({
                "sector": sec,
                "fuente_origen": "fede",
                "subtema": "",
                "resumen_fuente": resumen_txt,
                "evaluacion_fede": evaluacion,
                "propuestas": propuestas,
                "nota": "" if propuestas else "sin propuesta documentada en esta fuente",
            })

    fc = fede_cands.get(cid, {})
    out["candidatos"].append({
        "id": cid,
        "nombre": c["fullName"],
        "partido": c.get("party",""),
        "formula_vp": vp.get(cid,{}).get("formula_vp",""),
        "formula_vp_fuente": vp.get(cid,{}).get("src",""),
        "posicion_ideologica_autodescrita": "",
        "programa_url": best_prog(cid),
        "bio": c.get("compareBio","").strip(),
        "cubierto_por": ["candidateados"] + (["fede"] if es_fede else []),
        "notas": NOTAS.get(cid, []),
        "red_flags_fede": rf_by.get(cid, []),
        "sectores": sectores,
    })

out["meta"] = {
    "proyecto": "Brújula Electoral 2026 — extracción de propuestas",
    "fecha_consulta": FECHA,
    "fuentes_usadas": ["candidateados", "fede", "programa_oficial (vía fuente FEDe)", "web (fórmulas VP)"],
    "candidatos_incluidos": [c["id"] for c in out["candidatos"]],
    "sectores_candidateados": CAND_SECTOR_ORDER,
    "sectores_fede": ["seguridad","salud","energia","tierras_y_agro","institucional"],
    "candidatos_en_fede": sorted(FEDE_IDS),
    "notas_metodologicas": [
        "Texto fiel: candidateados es agregador secundario; FEDe trae descripción editada (editado=true) con URL de fuente oficial.",
        "Fuentes NO fusionadas: cada propuesta conserva su fuente; las banderas de FEDe no se trasladan a propuestas de candidateados.",
        "subtema vive a nivel de propuesta (FEDe lo provee así); más fiel que el esquema original con subtema a nivel de bloque.",
        "constitucionalidad.nivel es un mapeo mecánico del texto de FEDe (default 'contestado'; 'tumbado_por_corte' solo si cita fallo de la Corte). La explicación verbatim de FEDe queda en detalle.",
        "Sin bandera de una fuente nombrada => constitucionalidad/viabilidad = null. No se asume 'sin_objecion'.",
        "viabilidad_senalada queda null: ninguna fuente consultada entrega alerta de viabilidad por-propuesta; la evaluación FEDe de viabilidad es por-sector (campo evaluacion_fede).",
    ],
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

# ---- resumen de cobertura para consola ----
print(f"OK -> {os.path.relpath(OUT)}")
tot_cand = tot_fede = flagged = coments = 0
for c in out["candidatos"]:
    nc = sum(len(s["propuestas"]) for s in c["sectores"] if s["fuente_origen"]=="candidateados")
    nf = sum(len(s["propuestas"]) for s in c["sectores"] if s["fuente_origen"]=="fede")
    fl = sum(1 for s in c["sectores"] for p in s["propuestas"] if p["tags_terceros"]["constitucionalidad"])
    cm = sum(len(p["tags_terceros"]["comentarios_expertos"]) for s in c["sectores"] for p in s["propuestas"])
    tot_cand+=nc; tot_fede+=nf; flagged+=fl; coments+=cm
    print(f"  {c['id']:10} cand={nc:3} fede={nf:3} banderas={fl:2} coment_exp={cm:3} vp={'si' if c['formula_vp'] else 'NO'}")
print(f"TOTAL: candidateados={tot_cand} fede={tot_fede} banderas_constitucionalidad={flagged} comentarios_expertos={coments}")
