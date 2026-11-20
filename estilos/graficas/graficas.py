# -*- coding: utf-8 -*-
"""Estilo GRÁFICAS: el look de 3Blue1Brown hecho con Manim (fondo oscuro con cuadrícula tenue, textos que se
escriben, contadores que suben, ejes y curvas que se trazan, figuras que se dibujan y se rellenan). El kit está en
kit.py; las escenas del reel van en <proyecto>/escenas_graficas.py (copia de plantilla_escenas.py).

    GR.rodar(r, ESC)                 # rueda el fondo animado -> <proyecto>/graficas_raw.mp4 (~2 min por minuto de video)
    GR.rodar(r, ESC, previa=True)    # versión chica 360x640 para revisar rápido -> _work/graficas_previa.mp4
    GR.fotos(video, '3s,12.5s', prefijo)
"""
import os
import shutil
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
ESTILOS = os.path.dirname(AQUI)
sys.path.insert(0, ESTILOS)
import motores as M  # noqa: E402
from componer import run  # noqa: E402


def rodar(r, esc, escenas='escenas_graficas.py', previa=False):
    if not os.path.exists(os.path.join(r.P, escenas)): raise SystemExit(f'no está {escenas} en el proyecto (copia estilos/graficas/plantilla_escenas.py)')
    tiempos = r.exportar_tiempos(esc, os.path.join(r.P, '_work', 'tiempos.json'))
    env = dict(os.environ, REEL_TIEMPOS=tiempos, REEL_MOTION_KIT=AQUI, PYTHONIOENCODING='utf-8')
    if previa: env['MANIM_PREVIA'] = '1'
    media = os.path.join(r.P, '_work', 'manim'); nombre = 'graficas_previa' if previa else 'graficas_raw'
    t = time.time()
    run([M.manim_python(), '-m', 'manim', 'render', '--progress_bar', 'none', '--media_dir', media, '-o', nombre, escenas, 'Reel'], cwd=r.P, env=env)
    src = os.path.join(media, 'videos', os.path.splitext(os.path.basename(escenas))[0], '640p30' if previa else '1920p30', nombre + '.mp4')
    dst = os.path.join(r.P, '_work', 'graficas_previa.mp4') if previa else os.path.join(r.P, 'graficas_raw.mp4')
    shutil.copyfile(src, dst)
    print(f'{"previa" if previa else "fondo animado"} -> {os.path.relpath(dst, r.P)} ({time.time() - t:.0f}s)')
    return dst


def fotos(video, segundos, prefijo):
    """fotos sueltas de un video ya rodado (la previa o el fondo) en esos segundos."""
    os.makedirs(os.path.dirname(prefijo), exist_ok=True)
    for v in segundos.split(','):
        s = float(v.strip().rstrip('s'))
        out = f'{prefijo}-{s:06.2f}.jpg'
        run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{s:.3f}', '-i', video, '-frames:v', '1', '-q:v', '3', out])
        print('foto', out)
