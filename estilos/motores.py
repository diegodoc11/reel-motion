# -*- coding: utf-8 -*-
"""Dónde está el motor de cada estilo. Primero busca la skill ya instalada en ~/.claude/skills/<motor> y si no, la copia
que clona `estilos/instalar.py` en reel-motion/motores/<motor>. Si no está en ningún lado, dice qué correr."""
import glob
import os
import shutil
import sys

ESTILOS = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(ESTILOS)
MOTORES = os.path.join(SKILL, 'motores')
CLAUDE = os.path.join(os.path.expanduser('~'), '.claude', 'skills')
COMUN = os.path.join(ESTILOS, 'comun')

# motor -> (repositorio, archivo que lo identifica, estilos que lo usan)
REPOS = {
    'anidoodle': ('https://github.com/alexgreensh/anidoodle', os.path.join('engine', 'tools', 'render.mjs'), ('pizarra_animada', 'motion_design')),
    'claude-drawing': ('https://github.com/cloveric/claude-drawing-skill', os.path.join('lib', 'cartoon.py'), ('munecos',)),
    'handdraw-skill': ('https://github.com/ToBeWin/handdraw-skill', os.path.join('scripts', 'handdraw.mjs'), ('handdraw',)),
}
# qué necesita cada estilo
NECESITA = {
    'fanzine': ['node', 'comun'],
    'graficas': ['manim'],
    'pizarra_animada': ['node', 'anidoodle'],
    'motion_design': ['node', 'anidoodle'],
    'munecos': ['claude-drawing'],
    'handdraw': ['node', 'handdraw-skill'],
}


def _falta(que, estilo=None):
    est = estilo or '<estilo>'
    raise SystemExit(f'falta {que}. Instálalo una vez con:  python "{os.path.join(ESTILOS, "instalar.py")}" {est}')


def raiz(motor, estilo=None):
    """carpeta raíz del motor (la que contiene su archivo marca)."""
    repo, marca, _ = REPOS[motor]
    for c in (os.path.join(CLAUDE, motor), os.path.join(MOTORES, motor)):
        if not os.path.isdir(c): continue
        for base in [c] + sorted(glob.glob(os.path.join(c, '*'))) + sorted(glob.glob(os.path.join(c, '*', '*'))):
            if os.path.isfile(os.path.join(base, marca)): return base
    _falta(f'el motor {motor}', estilo)


def anidoodle_engine():
    return os.path.join(raiz('anidoodle', 'pizarra_animada'), 'engine')


def claude_drawing_lib():
    return os.path.join(raiz('claude-drawing', 'munecos'), 'lib')


def handdraw():
    return raiz('handdraw-skill', 'handdraw')


def manim_python():
    """el python que tiene Manim: REEL_MOTION_MANIM_PY, o el entorno que crea instalar.py en motores/manim/.venv."""
    env = os.environ.get('REEL_MOTION_MANIM_PY')
    if env and os.path.isfile(env): return env
    for py in (os.path.join(MOTORES, 'manim', '.venv', 'Scripts', 'python.exe'), os.path.join(MOTORES, 'manim', '.venv', 'bin', 'python')):
        if os.path.isfile(py): return py
    _falta('Manim', 'graficas')


def node():
    n = shutil.which('node')
    if not n: raise SystemExit('falta Node.js (https://nodejs.org, versión 18 o más nueva)')
    return n


def playwright_listo():
    if not os.path.isdir(os.path.join(COMUN, 'node_modules', 'playwright-core')): _falta('playwright-core (estilos/comun)', 'fanzine')
    return True


def entorno_playwright():
    """variables para que los motores de node encuentren el Chromium de Playwright (y Chrome si está instalado)."""
    env = dict(os.environ)
    if 'PLAYWRIGHT_BROWSERS_PATH' not in env:
        loc = os.environ.get('LOCALAPPDATA')
        cand = os.path.join(loc, 'ms-playwright') if loc else os.path.join(os.path.expanduser('~'), '.cache', 'ms-playwright')
        if sys.platform == 'darwin': cand = os.path.join(os.path.expanduser('~'), 'Library', 'Caches', 'ms-playwright')
        env['PLAYWRIGHT_BROWSERS_PATH'] = cand
    return env
