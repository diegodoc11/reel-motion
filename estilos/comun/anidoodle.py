# -*- coding: utf-8 -*-
"""Lo común de los estilos que dibuja el motor AniDoodle (pizarra animada y motion design).

AniDoodle (Apache-2.0, https://github.com/alexgreensh/anidoodle) pinta cada cuadro con una función pura en TypeScript.
Cada reel arma un "proyecto enlazado" en <proyecto>/_work/anidoodle/: usa el motor instalado sin copiarlo y le pone
delante sus propios módulos (el kit del estilo, los tiempos del reel y las escenas).

    d = AD.proyecto(r, ESC, film='pizarraAnimada', kits=[...], escenas='escenas_pizarra_animada.ts')
    AD.fotos(r, d, 'pizarraAnimada', '3s,12.5s')         # hoja con fotos sueltas (segundos) para revisar
    AD.rodar(r, d, 'pizarraAnimada', 'pizarra_animada_raw.mp4')
"""
import math
import os
import shutil
import sys
import time

COMUN = os.path.dirname(os.path.abspath(__file__))
ESTILOS = os.path.dirname(COMUN)
sys.path.insert(0, ESTILOS)
import motores as M  # noqa: E402
from componer import run  # noqa: E402


def proyecto(r, esc, film, kits, escenas):
    """crea (la primera vez) o actualiza el proyecto enlazado y le copia kit + tiempos + escenas del reel."""
    src_esc = escenas if os.path.isabs(escenas) else os.path.join(r.P, escenas)
    if not os.path.exists(src_esc): raise SystemExit(f'no está {escenas} en el proyecto (copia la plantilla_escenas.ts del estilo)')
    engine = M.anidoodle_engine(); d = os.path.join(r.P, '_work', 'anidoodle')
    if not os.path.exists(os.path.join(d, 'anidoodle-project.json')) or not os.path.exists(os.path.join(d, 'src', 'hosts', f'page-{film}.ts')):
        run([M.node(), os.path.join(engine, 'tools', 'scaffold.mjs'), d, '--linked', '--film', film, '--format', '9x16',
             '--duration', str(math.ceil(r.DUR)), '--fps', '30'], env=M.entorno_playwright())
    # el motor busca playwright en node_modules del proyecto: se enlaza el de estilos/comun (no se instala dos veces)
    nm = os.path.join(d, 'node_modules')
    if not os.path.exists(nm):
        M.playwright_listo()
        if os.name == 'nt': run(['cmd', '/c', 'mklink', '/J', nm, os.path.join(COMUN, 'node_modules')])
        else: os.symlink(os.path.join(COMUN, 'node_modules'), nm, target_is_directory=True)
    cc = os.path.join(d, 'src', 'canvas-core'); os.makedirs(cc, exist_ok=True)
    for k in kits: shutil.copyfile(k, os.path.join(cc, os.path.basename(k)))
    r.exportar_tiempos(esc, os.path.join(cc, 'reelTiempos.ts'), formato='ts')
    shutil.copyfile(src_esc, os.path.join(cc, f'{film}.ts'))
    host = os.path.join(d, 'src', 'hosts', f'page-{film}.ts')
    open(host, 'w', encoding='utf-8').write(f'import {{ {film} }} from "../canvas-core/{film}";\nimport {{ mountFilm }} from "./page";\nmountFilm({film});\n')
    return d


def fotos(r, d, film, segundos, salida=None):
    """una hoja con fotos sueltas (segundos '3s,12.5s' o cuadros '90,375') para revisar sin rodar todo."""
    fr = ','.join(str(round(float(v.strip()[:-1]) * 30)) if v.strip().endswith('s') else v.strip() for v in segundos.split(','))
    salida = salida or os.path.join(r.P, '_work', 'fotos', f'{film}.png'); os.makedirs(os.path.dirname(salida), exist_ok=True)
    run([M.node(), os.path.join(M.anidoodle_engine(), 'tools', 'still.mjs'), film, '--frames', fr, '--sheet', salida], cwd=d, env=M.entorno_playwright())
    print(f'fotos -> {os.path.relpath(salida, r.P)}')
    return salida


def rodar(r, d, film, raw, workers=2):
    """rueda el fondo animado completo (sin audio). Un estilo de AniDoodle a la vez: dos renders juntos ahogan el PC."""
    out = raw if os.path.isabs(raw) else os.path.join(r.P, raw); t = time.time()
    run([M.node(), os.path.join(M.anidoodle_engine(), 'tools', 'render.mjs'), film, '--workers', str(workers), '--out', out], cwd=d, env=M.entorno_playwright())
    print(f'fondo animado -> {os.path.relpath(out, r.P)} ({(time.time() - t) / 60:.1f} min)')
    return out
