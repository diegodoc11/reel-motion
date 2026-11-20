# -*- coding: utf-8 -*-
"""Lo del estilo caritas: Clawd (el muñequito naranja de Claude) pintado a pincel con acuarela, actuando cada frase.

Motor: ClaudeAnimationBase de John Heibel (MIT, https://github.com/JohnHeibel/ClaudeAnimationBase): p5.js + p5.brush
pintando en Chrome sin ventana. Cada reel arma su carpeta de trabajo en <proyecto>/_work/caritas/ con una copia del motor
(el lienzo pasado a vertical 1080x1920), los objetos pintados del estilo (props.js, props2.js), los tiempos del reel y
sus escenas. node_modules es un enlace al del motor: no se instala dos veces.

    d = CA.proyecto(r, ESC, 'escenas_caritas.js', bpm=110, offset=0.02)
    CA.fotos(r, d, ESC)                   # hoja con una foto por toma (o segundos: '3s,12.5s'), ~1 min, sin video
    CA.pintar(r, d, 'caritas_raw.mp4')    # todos los cuadros (12 dibujos por segundo) con 4 Chrome a la vez + video

Para ver una toma moviéndose: abre <proyecto>/_work/caritas/studio.html en Chrome (barra para adelantar).
"""
import glob
import json
import math
import os
import shutil
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
ESTILOS = os.path.dirname(AQUI)
sys.path.insert(0, ESTILOS)
import motores as M  # noqa: E402
from componer import run  # noqa: E402

FPS = 12                    # dibujos por segundo ("en dos", como la animación a mano); el borrador sale a 30
MOTOR = ('render.mjs', 'src/clawd.js', 'src/timeline.js', 'src/sheets.js')       # se copian tal cual
VERTICAL = ('const W = 1920, H = 1080;', 'const W = 1080, H = 1920;')           # el único cambio al motor

STUDIO = '''<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>caritas · reel-motion</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Permanent+Marker&display=block">
<style>
  html, body { margin: 0; background: #1b1820; color: #eee; font: 13px system-ui, sans-serif; }
  main { padding: 12px; display: grid; gap: 8px; }
  #out { width: min(100%, 540px); aspect-ratio: 9 / 16; height: auto; background: #F3EBDC; }
  .p5Canvas { display: none !important; }
  .bar { display: flex; gap: 10px; align-items: center; max-width: 540px; }
  #scrub { flex: 1; }
  #tt { font-variant-numeric: tabular-nums; min-width: 190px; }
</style>
<script src="node_modules/p5/lib/p5.min.js"></script>
<script src="node_modules/p5.brush/dist/p5.brush.js"></script>
</head>
<body>
<main>
  <canvas id="out" width="1080" height="1920"></canvas>
  <div class="bar"><input id="scrub" type="range" min="0" max="11" step="0.0417" value="0"><span id="tt">loading…</span></div>
</main>
<!-- motor (ClaudeAnimationBase, MIT) -->
<script src="src/config.js"></script>
<script src="src/core.js"></script>
<script src="src/clawd.js"></script>
<script src="src/timeline.js"></script>
<script src="src/sheets.js"></script>
<!-- estilo caritas: objetos pintados, tiempos del reel y sus escenas -->
<script src="src/props.js"></script>
<script src="src/props2.js"></script>
<script src="src/tiempos.js"></script>
<script src="src/escenas.js"></script>
<script>
  // studio.html?loop=emotions (o views) muestra las hojas de emociones / vistas de Clawd en vez del video.
  const q = new URLSearchParams(location.search).get('loop'); if (q && LOOPS[q]) window.LOOP = LOOPS[q];
</script>
</body>
</html>
'''


def chrome():
    """Chrome instalado (o CHROME_PATH), y si no hay, el Chromium de Playwright (lo instala `estilos/instalar.py caritas`)."""
    cands = [os.environ.get('CHROME_PATH'),
             r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
             os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
             '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser']
    base = M.entorno_playwright()['PLAYWRIGHT_BROWSERS_PATH']
    for pat in ('chromium-*/chrome-win*/chrome.exe', 'chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium',
                'chromium-*/chrome-mac*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing', 'chromium-*/chrome-linux*/chrome'):
        cands += sorted(glob.glob(os.path.join(base, pat)), reverse=True)
    for c in cands:
        if c and os.path.isfile(c): return c
    M._falta('Chrome (o el Chromium de Playwright)', 'caritas')


def proyecto(r, esc, escenas, bpm=110, offset=0.0):
    """crea o actualiza <proyecto>/_work/caritas: motor en vertical + objetos del estilo + tiempos + escenas del reel."""
    src_esc = escenas if os.path.isabs(escenas) else os.path.join(r.P, escenas)
    if not os.path.exists(src_esc): raise SystemExit(f'no está {escenas} en el proyecto (copia ahí estilos/caritas/plantilla_escenas.js con ese nombre)')
    kit = M.clawd_kit(); nm_kit = os.path.join(kit, 'node_modules')
    if not all(os.path.isdir(os.path.join(nm_kit, p)) for p in ('p5', 'p5.brush', 'puppeteer-core')):
        M._falta('las dependencias del motor de caritas (npm install)', 'caritas')
    d = os.path.join(r.P, '_work', 'caritas'); src = os.path.join(d, 'src'); os.makedirs(src, exist_ok=True)
    for f in MOTOR: shutil.copyfile(os.path.join(kit, *f.split('/')), os.path.join(d, *f.split('/')))
    core = open(os.path.join(kit, 'src', 'core.js'), encoding='utf-8', newline='').read()
    if VERTICAL[0] not in core: raise SystemExit(f'el motor de caritas cambió: no encontré "{VERTICAL[0]}" en {os.path.join(kit, "src", "core.js")}')
    open(os.path.join(src, 'core.js'), 'w', encoding='utf-8', newline='').write(core.replace(*VERTICAL))
    for f in ('props.js', 'props2.js'): shutil.copyfile(os.path.join(AQUI, f), os.path.join(src, f))
    shutil.copyfile(src_esc, os.path.join(src, 'escenas.js'))
    open(os.path.join(src, 'config.js'), 'w', encoding='utf-8').write(
        '// generado por estilos/caritas/caritas.py (bpm = tempo al que rebota Clawd; offset = segundo del primer golpe)\n'
        f'const PROJECT = {{ duration: {r.DUR}, bpm: {bpm}, offset: {offset} }};\n')
    words = [{'s': round(w['start'], 3), 'e': round(w['end'], 3), 'w': w['text'], 'r': w['raw']} for w in r.WD]
    open(os.path.join(src, 'tiempos.js'), 'w', encoding='utf-8').write(
        '// generado por estilos/caritas/caritas.py: palabras con su segundo (WORDS) e inicio de cada toma (ESC)\n'
        f'const WORDS = {json.dumps(words, ensure_ascii=False)};\n'
        f'const ESC = {json.dumps({k: round(v, 3) for k, v in esc.items()})};\n')
    open(os.path.join(d, 'studio.html'), 'w', encoding='utf-8').write(STUDIO)
    nm = os.path.join(d, 'node_modules')
    if os.path.lexists(nm) and not os.path.exists(nm): os.rmdir(nm) if os.name == 'nt' else os.remove(nm)    # enlace roto
    if not os.path.exists(nm):
        if os.name == 'nt': run(['cmd', '/c', 'mklink', '/J', nm, nm_kit])
        else: os.symlink(nm_kit, nm, target_is_directory=True)
    return d


def _tiempos_tomas(r, esc, k=0.75):
    """un segundo dentro de cada toma (al 75 %: lejos de los brochazos de entrada y salida)."""
    ks = list(esc.values()) + [r.DUR]
    return [round(a + k * (b - a), 2) for a, b in zip(ks, ks[1:])]


def fotos(r, d, esc=None, segundos=None, salida=None, cols=4, ancho=270):
    """hoja de revisión sin video: una foto por toma, o los segundos pedidos ('3s,12.5s'). ~3 s por foto."""
    ts = [float(v.strip().rstrip('s')) for v in segundos.split(',') if v.strip()] if segundos else _tiempos_tomas(r, esc)
    salida = salida or os.path.join(r.P, '_work', 'fotos', 'caritas.jpg'); os.makedirs(os.path.dirname(salida), exist_ok=True)
    from PIL import Image, ImageStat
    for intento in range(2):                     # si Chrome perdió la tarjeta de video, la hoja sale negra: otra vez
        run([M.node(), 'render.mjs', '--sheet=' + ','.join(f'{t:.2f}' for t in ts), f'--cols={cols}', f'--w={ancho}', f'--out={salida}',
             f'--chrome={chrome()}'], cwd=d)
        if ImageStat.Stat(Image.open(salida).convert('L')).mean[0] > 60: break
        print('  la hoja salió oscura (Chrome perdió la tarjeta de video)' + ('; otra vez…' if not intento else ': córrela de nuevo'), flush=True)
    print(f'fotos -> {os.path.relpath(salida, r.P)} ({len(ts)}: ' + ', '.join(f'{t:.1f}s' for t in ts) + ')')
    return salida


def _negro(ruta):
    """True si la imagen salió negra entera: pasa cuando Chrome pierde la tarjeta de video ("CONTEXT_LOST_WEBGL" en el
    log). Un cuadro bueno de caritas siempre tiene papel claro."""
    from PIL import Image
    try:
        im = Image.open(ruta); im.draft('L', (135, 240))
        return im.convert('L').getextrema()[1] < 16
    except Exception:
        return True


def _lanzar(d, tramos, ch, ronda):
    """un Chrome por tramo (a, b en segundos). Arrancan con 3 s de diferencia: juntos, alguno puede perder la tarjeta."""
    ps = []
    for k, (i, a, b) in enumerate(tramos):
        if k: time.sleep(3)
        log = open(os.path.join(d, 'out', f'pintar_{i}' + (f'_otra{ronda}' if ronda else '') + '.log'), 'w')
        ps.append((i, subprocess.Popen([M.node(), 'render.mjs', '--frames', '--workers=1', f'--fps={FPS}', f'--range={a:.5f}:{b:.5f}', f'--chrome={ch}'],
                                       cwd=d, stdout=log, stderr=subprocess.STDOUT), log))
    caidos = [i for i, p, _ in ps if p.wait() != 0]
    for _, _, log in ps: log.close()
    return caidos


def pintar(r, d, raw, procesos=4, seguir=False, rondas=3):
    """pinta todos los cuadros con VARIOS Chrome a la vez (cada uno su tramo) y los une en el fondo animado (sin audio).
    p5.brush pinta por un solo canal de video por Chrome: con 1 se atasca, con 4 rinde ~100 cuadros por minuto y más no
    ayuda. Nunca dos reels de caritas a la vez (con 10 Chrome un computador se apagó). seguir=True retoma lo ya pintado.
    Al final revisa cada cuadro: los que salieron negros (Chrome perdió la tarjeta de video) se vuelven a pintar solos."""
    frames = os.path.join(d, 'out', 'frames')
    if not seguir: shutil.rmtree(frames, ignore_errors=True)
    os.makedirs(frames, exist_ok=True)
    def borrar_negros():
        malos = [f for f in os.listdir(frames) if f.endswith('.jpg') and _negro(os.path.join(frames, f))]
        for f in malos: os.remove(os.path.join(frames, f))
        return malos

    negros = borrar_negros() if seguir else []   # al retomar, los cuadros negros de antes también se vuelven a pintar
    n = math.ceil(r.DUR * FPS); ch = chrome(); t = time.time()                 # n: la misma cuenta que render.mjs
    print(f'pintando {n} cuadros con {procesos} Chrome (~{n / 100:.0f}-{n / 70:.0f} min si el computador está libre)…', flush=True)
    for ronda in range(rondas + 1):
        hay = {int(f[1:6]) for f in os.listdir(frames) if f.endswith('.jpg') and f[1:6].isdigit()}
        faltan = [k for k in range(n) if k not in hay]
        if not faltan: break
        if ronda == rondas:
            raise SystemExit(f'después de {rondas} intentos siguen faltando {len(faltan)} cuadros: cierra lo que esté usando la tarjeta de '
                             'video (juegos, otro render, videos) y corre otra vez con --seguir')
        if ronda: print(f'  faltan {len(faltan)} cuadros' + (f' ({len(negros)} salieron negros: Chrome perdió la tarjeta de video)' if negros else '')
                        + '; se vuelven a pintar…', flush=True)
        # lo que falta se reparte en partes iguales entre los Chrome (render.mjs se salta los cuadros que ya están)
        grupos = [g for g in (faltan[j * len(faltan) // procesos:(j + 1) * len(faltan) // procesos] for j in range(procesos)) if g]
        caidos = _lanzar(d, [(j, g[0] / FPS, (g[-1] + 1) / FPS) for j, g in enumerate(grupos)], ch, ronda)
        if caidos: raise SystemExit(f'falló el pintado en los tramos {caidos} (mira _work/caritas/out/pintar_N.log); con --seguir retoma lo ya pintado')
        negros = borrar_negros()
    out = raw if os.path.isabs(raw) else os.path.join(r.P, raw)
    run([M.node(), 'render.mjs', '--encode', f'--out={out}', f'--fps={FPS}', f'--chrome={ch}'], cwd=d)
    print(f'fondo animado -> {os.path.relpath(out, r.P)} ({n} cuadros en {(time.time() - t) / 60:.1f} min)')
    return out
