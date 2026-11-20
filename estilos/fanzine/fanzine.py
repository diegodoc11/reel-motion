# -*- coding: utf-8 -*-
"""Estilo FANZINE: impresión risográfica de 3 tintas (azul, rosa, amarillo) y UNA sola maqueta larga que la cámara
recorre: cada frase es una estación al lado de la otra y por debajo corre un camino que las une. Motor propio en
JavaScript (motor.js, canvas): una página con window.draw(frame) que se rueda con estilos/comun/render_canvas.mjs.

    html = FZ.armar(r, ESC, 'escenas_fanzine.js', '_work/fanzine.html')   # motor + datos + escenas en una página
    FZ.fotos(html, '3s,12.5s', '_work/fotos/f')                          # fotos rápidas para revisar
    FZ.rodar(html, 'fanzine_raw.mp4')                                     # el fondo animado (sin audio)
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ESTILOS = os.path.dirname(AQUI)
sys.path.insert(0, ESTILOS)
import motores as M  # noqa: E402
from componer import run  # noqa: E402

RENDER = os.path.join(ESTILOS, 'comun', 'render_canvas.mjs')


def armar(r, esc, escenas, salida):
    """arma la página única: figuras de las láminas + palabras con su segundo + tomas + motor + escenas."""
    esc_js = os.path.join(r.P, escenas) if not os.path.isabs(escenas) else escenas
    if not os.path.exists(esc_js): raise SystemExit(f'no está {esc_js} (copia estilos/fanzine/plantilla_escenas.js al proyecto)')
    datos = json.load(open(r.exportar_tiempos(esc, os.path.join(r.P, '_work', 'tiempos.json')), encoding='utf-8'))
    figs = json.load(open(os.path.join(ESTILOS, 'comun', 'figuras.json'), encoding='utf-8'))
    motor = open(os.path.join(AQUI, 'motor.js'), encoding='utf-8').read()
    escenas_txt = open(esc_js, encoding='utf-8').read()
    frames = round(datos['DUR'] * 30)
    html = f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>{r.nombre} · fanzine</title>
<style>html,body{{margin:0;background:#1b1b1b;height:100%}}canvas{{display:block;height:100vh;width:auto;margin:0 auto}}</style>
</head><body><canvas id="c" width="1080" height="1920"></canvas>
<script>
const DATOS = {json.dumps(figs, ensure_ascii=False, separators=(',', ':'))};
const WORDS = {json.dumps(datos['WORDS'], ensure_ascii=False, separators=(',', ':'))};
const ESC = {json.dumps(datos['ESC'])};
const DUR = {datos['DUR']};
</script>
<script>
{motor}
</script>
<script>
try {{
{escenas_txt}
}} catch (e) {{ window.ERROR = 'escenas: ' + e.message; }}
</script>
<script>
window.FPS = FPS; window.FRAMES = {frames}; window.draw = draw; window.CUES = ESTACIONES.map(e => e.t0);
if (!location.search.includes('render')) {{            // vista previa: abre la página en el navegador y corre en tiempo real
  const t0 = performance.now();
  const loop = () => {{ const f = Math.floor((performance.now() - t0) / 1000 * FPS) % window.FRAMES; draw(f); requestAnimationFrame(loop); }};
  loop();
}}
</script>
</body></html>
'''
    salida = os.path.join(r.P, salida) if not os.path.isabs(salida) else salida
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    open(salida, 'w', encoding='utf-8').write(html)
    print(f'página -> {os.path.relpath(salida, r.P)} ({frames} cuadros)')
    return salida


def fotos(html, segundos, prefijo):
    """fotos sueltas en esos segundos (p. ej. '3s,12.5s,40s') para revisar sin rodar todo."""
    M.playwright_listo()
    os.makedirs(os.path.dirname(prefijo), exist_ok=True)
    print(run([M.node(), RENDER, html, prefijo, '--stills', segundos], env=M.entorno_playwright()).stdout.strip())


def rodar(html, raw, workers=3):
    """rueda el fondo animado completo a MP4 (sin audio)."""
    M.playwright_listo()
    print(run([M.node(), RENDER, html, raw, '--workers', str(workers)], env=M.entorno_playwright()).stdout.strip().splitlines()[-1])
    return raw
