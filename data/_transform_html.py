#!/usr/bin/env python3
"""Transforma index_v_4_4.html -> public/index.html para deploy en Azure SWA.
[MIGRACIÓN ONE-TIME] public/index.html ya es el archivo canónico; editarlo ahí directamente.
No re-correr salvo que quieras regenerar desde el original (sobrescribe ediciones manuales).
Idempotente sobre el fuente; verifica que cada reemplazo ocurra exactamente 1 vez."""
import re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
SRC  = os.path.join(HERE, "index_v_4_4.html")  # original; migración one-time
DST  = os.path.join(ROOT, "public", "index.html")

# Placeholder de dominio: NO hay dominio personal definido aún.
# Reemplazar tras crear el recurso Azure SWA (ver README, sección Deploy).
SITE = "https://REEMPLAZAR-DOMINIO"

html = open(SRC, encoding="utf-8").read()

def sub_once(pattern, repl, text, label, flags=0, literal=False):
    if literal:
        n = text.count(pattern)
        if n != 1:
            sys.exit(f"[FATAL] '{label}': se esperaba 1 ocurrencia, hay {n}")
        return text.replace(pattern, repl)
    new, n = re.subn(pattern, repl, text, flags=flags)
    if n != 1:
        sys.exit(f"[FATAL] '{label}': se esperaba 1 sustitución, hubo {n}")
    return new

# ---------------------------------------------------------------- 1. FUENTES
font_links = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Public+Sans:wght@400;500;600&display=swap" rel="stylesheet">'
)
font_face = """<style>
  @font-face { font-family: 'Fraunces'; font-weight: 400; font-display: swap; src: url('./fonts/fraunces-400.woff2') format('woff2'); }
  @font-face { font-family: 'Fraunces'; font-weight: 500; font-display: swap; src: url('./fonts/fraunces-500.woff2') format('woff2'); }
  @font-face { font-family: 'Fraunces'; font-weight: 600; font-display: swap; src: url('./fonts/fraunces-600.woff2') format('woff2'); }
  @font-face { font-family: 'Public Sans'; font-weight: 400; font-display: swap; src: url('./fonts/public-sans-400.woff2') format('woff2'); }
  @font-face { font-family: 'Public Sans'; font-weight: 500; font-display: swap; src: url('./fonts/public-sans-500.woff2') format('woff2'); }
  @font-face { font-family: 'Public Sans'; font-weight: 600; font-display: swap; src: url('./fonts/public-sans-600.woff2') format('woff2'); }
</style>"""
html = sub_once(font_links, font_face, html, "font links", literal=True)

# ------------------------------------------------ 2. META / OG / FAVICON
title_tag = "<title>Brújula Electoral 2026 · Corpus completo</title>"
meta_block = title_tag + f"""
<meta name="description" content="Comparador imparcial de propuestas para las elecciones presidenciales de Colombia 2026. 12 candidatos, 616 propuestas, banderas constitucionales y comentarios de expertos atribuidos a su fuente.">
<meta name="theme-color" content="#F6F2E9">
<link rel="icon" type="image/svg+xml" href="./favicon.svg">
<meta property="og:type" content="website">
<meta property="og:title" content="Brújula Electoral 2026">
<meta property="og:description" content="Compara las propuestas de los 12 candidatos presidenciales sin paráfrasis, con sus fuentes citadas.">
<!-- TODO deploy: reemplazar REEMPLAZAR-DOMINIO por el dominio real antes de compartir en redes -->
<meta property="og:image" content="{SITE}/og-image.png">
<meta property="og:url" content="{SITE}/">
<meta name="twitter:card" content="summary_large_image">"""
html = sub_once(title_tag, meta_block, html, "meta block", literal=True)

# --------------------------------------------- 3. ELIMINAR data-blob JSON
html = sub_once(
    r'<script type="application/json" id="data-blob">.*?</script>\s*',
    '', html, "data-blob removal", flags=re.DOTALL)

# ------------------------------------ 4. ENVOLVER JS EN IIFE ASYNC + fetch
raw_line = 'const RAW = JSON.parse(document.getElementById("data-blob").textContent);'
iife_open = """(async function init(){
  let RAW;
  try {
    const resp = await fetch('./propuestas-2026.json', {cache: 'force-cache'});
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    RAW = await resp.json();
  } catch (e) {
    document.body.innerHTML = `<div style="padding:40px;text-align:center;font-family:system-ui">No se pudo cargar el corpus de propuestas.<br><small style="color:#888">${e.message}</small></div>`;
    return;
  }
  // Exponer a window las funciones llamadas por handlers onclick inline (hoisted).
  window.closeModal = closeModal;
  window.showProps  = showProps;
  window.showFlags  = showFlags;"""
html = sub_once(raw_line, iife_open, html, "RAW->IIFE", literal=True)

# cerrar la IIFE justo antes del único </script> restante
html = sub_once("</script>", "})();\n</script>", html, "IIFE close", literal=True)

# ------------------------------------------------ 5. FOOTER (atribución)
old_disc = ('  <div class="disc"><b>Aviso.</b> Las banderas “Alerta/Amenaza” son juicios de FEDe '
            '(con lente del Estado de Derecho), no veredictos neutros. Los comentarios de expertos son '
            'opiniones atribuidas. La vista “Problemas del país” usa promedios simples entre '
            'encuestadoras con la misma pregunta; verifica en las fuentes originales antes de decidir tu voto.</div>')
new_disc = """  <div class="disc">
    <b>Proyecto personal e independiente de Sergio Ferro.</b> Datos extraídos el 28 de mayo de 2026 de Candidateados y FEDe; programas oficiales registrados ante el CNE. La capa “¿Quién atiende qué?” es análisis interpretativo propio con rúbrica transparente; las banderas y comentarios son juicios atribuidos a FEDe y sus expertos, no veredictos neutros. La vista “Problemas del país” usa promedios simples entre encuestadoras con la misma pregunta. Verifica en las fuentes originales antes de decidir tu voto.
    <br><small>¿Encontraste un error o tienes feedback? Escríbeme a <a href="mailto:sferrod@gmail.com">sferrod@gmail.com</a></small>
  </div>"""
html = sub_once(old_disc, new_disc, html, "footer disc", literal=True)

os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8").write(html)
size = os.path.getsize(DST)
print(f"OK -> public/index.html  ({size/1024:.1f} KB)")
# sanity
assert "data-blob" not in html, "data-blob aún presente"
assert "fonts.googleapis" not in html, "links a Google Fonts aún presentes"
assert html.count("})();\n</script>") == 1
print("checks: sin data-blob ✓ · sin googleapis ✓ · IIFE cerrada ✓")
