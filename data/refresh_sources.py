#!/usr/bin/env python3
"""
Refresca las fuentes crudas en data/raw/ (para el cron diario):
  - FEDe: 7 pestañas del Google Sheet público (export CSV vía gviz)
  - Candidateados: parseo del payload RSC (self.__next_f) del home Next.js

Defensivo: si una fuente falla o cambia de estructura, NO sobrescribe el archivo
existente (conserva el dato bueno) y reporta el fallo. Solo stdlib (sin pip).
No toca vp_web.json (metadato estático de fórmulas VP).
"""
import re, json, os, sys, csv, io, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

# ---- FEDe Google Sheet ----------------------------------------------------
# Parametrizable por entorno para refrescar el sheet de segunda vuelta sin tocar
# el pipeline de primera vuelta. Defaults = sheet/dir de primera vuelta (v4).
#   FEDE_SHEET_ID    sobreescribe el sheet (default: el de v4)
#   FEDE_DIR         carpeta destino de los CSV (default: raw/fede_csv)
#   FEDE_TABS_EXTRA  pestañas adicionales separadas por coma (ej. "preguntas,posiciones")
FEDE_SHEET_ID = os.environ.get("FEDE_SHEET_ID", "1joLt-JrQuf4HLfSubQYa0Jjd10DG7fk47DC0niaL2Jw")
FEDE_DIR = os.environ.get("FEDE_DIR", os.path.join(RAW, "fede_csv"))
FEDE_TABS = ["candidatos", "propuestas", "expertos", "comentarios_expertos",
             "red_flags", "resumen_sectores", "sectores"]
_extra = [t.strip() for t in os.environ.get("FEDE_TABS_EXTRA", "").split(",") if t.strip()]
FEDE_TABS = FEDE_TABS + [t for t in _extra if t not in FEDE_TABS]
# columna que debe aparecer en el encabezado de cada pestaña (validación anti-basura)
FEDE_REQUIRED_COL = {
    "candidatos": "formula_vp", "propuestas": "semaforo", "expertos": "rol",
    "comentarios_expertos": "propuesta_id", "red_flags": "badge",
    "resumen_sectores": "viabilidad", "sectores": "sector",
    "preguntas": "pregunta", "posiciones": "respuesta",
}
CAND_URL = "https://www.candidateados.com"


def fetch(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def write_if_valid(path, content, validate):
    """Escribe solo si validate(content) pasa; si no, conserva el archivo viejo."""
    ok, msg = validate(content)
    if not ok:
        print(f"  ! {os.path.basename(path)}: validación falló ({msg}) — conservo el archivo previo")
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return True


# ---- FEDe -----------------------------------------------------------------
def refresh_fede():
    os.makedirs(FEDE_DIR, exist_ok=True)
    base = f"https://docs.google.com/spreadsheets/d/{FEDE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet="
    ok_tabs = 0
    for tab in FEDE_TABS:
        try:
            content = fetch(base + tab)
        except Exception as e:
            print(f"  ! FEDe/{tab}: fetch falló ({e}) — conservo el previo")
            continue

        def validate(c, tab=tab):
            # debe parsear como CSV y traer la columna esperada + >=1 fila de datos
            try:
                rows = list(csv.reader(io.StringIO(c)))
            except Exception as e:
                return False, f"no parsea CSV: {e}"
            if len(rows) < 2:
                return False, "menos de 2 filas"
            header = [h.strip().lower() for h in rows[0]]
            if FEDE_REQUIRED_COL[tab] not in header:
                return False, f"falta columna '{FEDE_REQUIRED_COL[tab]}' (¿respuesta no-CSV?)"
            return True, ""

        if write_if_valid(os.path.join(FEDE_DIR, f"{tab}.csv"), content, validate):
            ok_tabs += 1
    print(f"  FEDe: {ok_tabs}/{len(FEDE_TABS)} pestañas actualizadas")
    return ok_tabs == len(FEDE_TABS)


# ---- Candidateados (RSC) --------------------------------------------------
def parse_candidateados(html):
    pushes = re.findall(r'self\.__next_f\.push\((\[.*?\])\)', html, re.DOTALL)
    flight = []
    for p in pushes:
        try:
            arr = json.loads(p)
            if len(arr) >= 2 and isinstance(arr[1], str):
                flight.append(arr[1])
        except Exception:
            pass
    stream = "".join(flight)
    marker = '"card":{"sectors"'
    mi = stream.find(marker)
    if mi < 0:
        raise ValueError("marcador 'card.sectors' no encontrado (¿cambió la estructura RSC?)")
    ci = stream.rfind('"candidates":[', 0, mi)
    if ci < 0:
        raise ValueError("array 'candidates' no encontrado")
    arr_start = stream.index('[', ci + len('"candidates"'))
    depth = 0; in_str = False; esc = False; end = None
    for j in range(arr_start, len(stream)):
        c = stream[j]
        if in_str:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': in_str = False
        else:
            if c == '"': in_str = True
            elif c == '[': depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    end = j + 1; break
    if end is None:
        raise ValueError("el array 'candidates' no cierra")
    data = json.loads(stream[arr_start:end])
    return data


def refresh_candidateados():
    path = os.path.join(RAW, "candidateados_parsed.json")
    try:
        html = fetch(CAND_URL)
        data = parse_candidateados(html)
    except Exception as e:
        print(f"  ! Candidateados: fetch/parse falló ({e}) — conservo el previo")
        return False
    # validación: lista de candidatos con la forma esperada
    if not isinstance(data, list) or len(data) < 8:
        print(f"  ! Candidateados: {len(data) if isinstance(data,list) else 'no-lista'} candidatos (esperaba >=8) — conservo el previo")
        return False
    if not all(isinstance(c, dict) and c.get("slug") and c.get("card", {}).get("sectors") for c in data):
        print("  ! Candidateados: candidatos sin slug/card.sectors — conservo el previo")
        return False
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Candidateados: {len(data)} candidatos actualizados")
    return True


if __name__ == "__main__":
    print("Refrescando fuentes…")
    a = refresh_fede()
    # FEDE_ONLY=1 evita re-fetchear Candidateados (útil al refrescar el sheet de
    # segunda vuelta: Candidateados no cambió y vive en otro path).
    if os.environ.get("FEDE_ONLY") == "1":
        if not a:
            print("FEDe no se pudo actualizar.", file=sys.stderr)
            sys.exit(1)
        print("Listo (solo FEDe).")
        sys.exit(0)
    b = refresh_candidateados()
    if not a and not b:
        print("Ninguna fuente se pudo actualizar.", file=sys.stderr)
        sys.exit(1)
    print("Listo.")
