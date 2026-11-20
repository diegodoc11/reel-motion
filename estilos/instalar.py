# -*- coding: utf-8 -*-
"""Instala (una sola vez por computador) los motores de los estilos con motor propio y verifica que funcionen.

    python estilos/instalar.py fanzine            # o: graficas, pizarra_animada, motion_design, munecos, handdraw, caritas, todos
    python estilos/instalar.py todos --verificar  # solo revisa, no instala nada

Qué instala cada estilo (todo gratis, todo en tu computador):
  fanzine          playwright-core en estilos/comun (y el Chromium de Playwright si no tienes Chrome)
  graficas         Manim en un entorno propio: reel-motion/motores/manim/.venv
  pizarra_animada  motor AniDoodle (Apache-2.0): clon en reel-motion/motores/anidoodle + npm install
  motion_design    el mismo motor AniDoodle
  munecos          motor claude-drawing (MIT): clon en reel-motion/motores/claude-drawing
  handdraw         motor handdraw-skill (MIT, Remotion): clon en reel-motion/motores/handdraw-skill + npm install
  caritas          motor ClaudeAnimationBase (MIT, p5.js + p5.brush): clon en reel-motion/motores/claude-animation-base
                   + npm install (pinta en Chrome; si no lo tienes, usa el Chromium de Playwright)
Si ya tienes esas skills en ~/.claude/skills, se usan esas (no se clona nada).
"""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motores as M  # noqa: E402

MANIM_VERSION = '0.22.1'
VERIFICAR = '--verificar' in sys.argv


def sh(cmd, cwd=None, env=None):
    print('   $', ' '.join(str(c) for c in cmd))
    r = subprocess.run(cmd, cwd=cwd, env=env, shell=(os.name == 'nt' and str(cmd[0]).lower() in ('npm', 'npx')))
    if r.returncode: raise SystemExit(f'falló: {" ".join(str(c) for c in cmd)}')


def ok(msg): print('  ✓', msg)


def falta(msg):
    print('  ✗', msg)
    if VERIFICAR: return False
    return True


def basicos(necesita_node):
    if not shutil.which('ffmpeg'): raise SystemExit('falta ffmpeg (lo instala scripts/instalar.py de reel-motion)')
    ok('ffmpeg')
    if necesita_node:
        if not shutil.which('node'): raise SystemExit('falta Node.js 18+ (https://nodejs.org)')
        v = subprocess.run(['node', '--version'], capture_output=True, text=True).stdout.strip()
        ok(f'node {v}')


def comun():
    nm = os.path.join(M.COMUN, 'node_modules', 'playwright-core')
    if os.path.isdir(nm): ok('playwright-core (estilos/comun)')
    elif falta('playwright-core'): sh(['npm', 'install', '--no-audit', '--no-fund'], cwd=M.COMUN)
    # navegador: Chrome instalado, o el Chromium de Playwright
    chrome = any(os.path.exists(p) for p in (r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                                               '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome'))
    env = M.entorno_playwright(); hay_chromium = os.path.isdir(env['PLAYWRIGHT_BROWSERS_PATH']) and any(d.startswith('chromium') for d in os.listdir(env['PLAYWRIGHT_BROWSERS_PATH']))
    if chrome or hay_chromium: ok('navegador para rodar (Chrome o Chromium de Playwright)')
    elif falta('navegador'): sh([os.path.join(M.COMUN, 'node_modules', '.bin', 'playwright-core' + ('.cmd' if os.name == 'nt' else '')), 'install', 'chromium'], cwd=M.COMUN, env=env)


def manim():
    try:
        py = M.manim_python(); r = subprocess.run([py, '-c', 'import manim; print(manim.__version__)'], capture_output=True, text=True)
        if r.returncode == 0: ok(f'Manim {r.stdout.strip()}'); return
    except SystemExit:
        pass
    if not falta('Manim'): return
    d = os.path.join(M.MOTORES, 'manim'); os.makedirs(d, exist_ok=True)
    sh([sys.executable, '-m', 'venv', os.path.join(d, '.venv')])
    py = os.path.join(d, '.venv', 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(d, '.venv', 'bin', 'python')
    sh([py, '-m', 'pip', 'install', '--upgrade', 'pip', '-q'])
    sh([py, '-m', 'pip', 'install', f'manim=={MANIM_VERSION}', '-q'])
    ok('Manim instalado')


def repo(nombre):
    url, marca, _ = M.REPOS[nombre]
    try:
        base = M.raiz(nombre); ok(f'{nombre} ({base})')
    except SystemExit:
        if not falta(f'motor {nombre}'): return None
        os.makedirs(M.MOTORES, exist_ok=True)
        sh(['git', 'clone', '--depth', '1', url, os.path.join(M.MOTORES, nombre)])
        base = M.raiz(nombre)
    # dependencias de node del motor
    nodo = {'anidoodle': os.path.join(base, 'engine'), 'handdraw-skill': base, 'claude-animation-base': base}.get(nombre)
    if nodo and not os.path.isdir(os.path.join(nodo, 'node_modules')):
        if falta(f'dependencias de {nombre}'): sh(['npm', 'install', '--no-audit', '--no-fund'], cwd=nodo)
    elif nodo: ok(f'dependencias de {nombre}')
    if nombre == 'handdraw-skill':                      # handdraw se compila una vez después de npm install
        if os.path.isdir(os.path.join(base, 'packages', 'renderer', 'dist')): ok('handdraw-skill compilado')
        elif falta('compilar handdraw-skill'): sh(['npm', 'run', 'build'], cwd=base)
    return base


def estilo(e):
    print(f'\n== {e}')
    nec = M.NECESITA[e]
    basicos('node' in nec)
    for n in nec:
        if n == 'node': continue
        if n == 'comun': comun()
        elif n == 'manim': manim()
        else: repo(n)
    if e in ('pizarra_animada', 'motion_design', 'handdraw', 'caritas'): comun()      # también ruedan con Chrome/Chromium


if __name__ == '__main__':
    pedidos = [a for a in sys.argv[1:] if not a.startswith('--')] or ['todos']
    lista = list(M.NECESITA) if pedidos == ['todos'] else pedidos
    for e in lista:
        if e not in M.NECESITA: raise SystemExit(f'estilo desconocido: {e} (opciones: {", ".join(M.NECESITA)}, todos)')
        estilo(e)
    print('\nlisto' + (' (solo verificación)' if VERIFICAR else ''))
