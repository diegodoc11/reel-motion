# -*- coding: utf-8 -*-
# =====================================================================================================
#  reel-motion · PLANTILLA ESTILO GRÁFICAS  ("edítalo con reel-motion estilo gráficas")
#  El look de 3Blue1Brown (Manim): fondo oscuro con cuadrícula tenue, títulos que se escriben solos, números que suben
#  como contador, líneas de tiempo, curvas que se trazan, medidores, dos curvas que se separan. Brilla con números,
#  fechas y comparaciones. Presentador chico abajo a la derecha y subtítulo fantasma en blanco.
#  Las escenas van en escenas_graficas.py (copia de estilos/graficas/plantilla_escenas.py); aquí van las tomas, los
#  golpes y la música.
#
#  QUÉ CAMBIAR: CORRECCIONES, ROJAS, TOMAS y GOLPES (y las escenas). Las frases de ft('...') deben existir TAL CUAL en
#  words.json:  python build_graficas.py --guion
#  Comandos:  python build_graficas.py --previa            (versión chica 360x640, rápida, para revisar)
#             python build_graficas.py --fotos 3s,12.5s    (fotos de la previa, o del fondo si ya está rodado)
#             python build_graficas.py                     (rueda en 1080x1920 y monta) · --componer (solo monta)
#  El ejemplo es el reel ERA (77 s): "13 años del caballo al carro… ¿cuánto falta para que todos usemos IA?"
# =====================================================================================================
import os
import sys

P = os.path.dirname(os.path.abspath(__file__))
_sk = os.path.join(P, '_work', 'skill.txt')
SKILL = open(_sk, encoding='utf-8').read().strip() if os.path.exists(_sk) else os.path.expanduser('~/.claude/skills/reel-motion')
sys.path.insert(0, os.path.join(SKILL, 'estilos')); sys.path.insert(0, os.path.join(SKILL, 'estilos', 'graficas'))
import componer as C  # noqa: E402
import graficas as GR  # noqa: E402

CORRECCIONES = {'i': 'IA', 'adaptó': 'adoptó', 'cassette': 'casete', 'cassettes': 'casetes'}
ROJAS = ('Trece', '1913,', 'smartphone.', 'siete', 'seis', 'tres', 'dos.', 'nietos.', 'natural.', 'teclados',
         'casetes', 'clientes', 'casete.', 'agentes', 'moda.', 'triunfen', 'quiebren.', 'ERA')
r = C.Reel(P, estilo='graficas', correcciones=CORRECCIONES, rojas=ROJAS, musica='auto', volumen_musica=0.28, inicio_musica=24.0)
if '--guion' in sys.argv: r.guion(); sys.exit()
ft = r.ft

# ============================== TOMAS: dónde empieza cada página (edita) ==============================
ESC = dict(A=0.0, B=ft('en', despues=ft('1913')) - 0.1, C=ft('Saltemos') - 0.12, D=ft('el', despues=ft('tenido')) - 0.12,
           E=ft('Desde ese punto') - 0.12, F=ft('ChatGPT') - 0.2, G=ft('llevamos') - 0.12, H=ft('¿Cuántos') - 0.12,
           I=ft('esto') + 0.5, J1=ft('Solo miremos') - 0.12, J2=ft('Hoy') - 0.12, K=ft('Porque') - 0.12,
           L=ft('natural') - 0.38, M=ft('muchacho') - 0.4, N=ft('niños', despues=ft('Walkman')) - 0.35,
           O=ft('El negocio') - 0.12, P=ft('instalar') - 0.12, Q=ft('Será') - 0.12, R=ft('Comenta') + 0.02)
# golpes con "pop": cada contador y cada palabra clave
hoy = ft('hoy', despues=ESC['P'])
GOLPES = [ft('Trece'), ft('segundo'), ft('2007'), ft('primer'), ft('siete'), ft('seis'), ft('años', despues=ft('tres')),
          ft('dos'), ft('adopción'), ft('8'), ft('creció'), ft('natural'), ft('14'), ft('normal'),
          ft('IA', despues=ESC['O']), ft('casete', despues=ESC['O']), hoy, ft('no', despues=hoy),
          ft('triunfen') + 0.42, ft('quiebren') - 0.02, ft('ERA')]

# ============================== (no hace falta editar desde aquí) ==============================
if '--previa' in sys.argv:
    v = GR.rodar(r, ESC, previa=True)
    GR.fotos(v, '3s,12s,22s,35s,50s,64s,75s', os.path.join(P, '_work', 'fotos', 'graficas')); sys.exit()
if '--fotos' in sys.argv:
    prev = os.path.join(P, '_work', 'graficas_previa.mp4'); raw = os.path.join(P, 'graficas_raw.mp4')
    GR.fotos(prev if os.path.exists(prev) else raw, sys.argv[sys.argv.index('--fotos') + 1], os.path.join(P, '_work', 'fotos', 'graficas')); sys.exit()
if '--componer' not in sys.argv:
    GR.rodar(r, ESC)
r.sfx = r.efectos_tomas(ESC) + r.golpes(GOLPES)
r.subtitulos(fantasma='#7A8291', tinta='#FFFFFF', borde='#0E1116')
r.audio(); r.componer('graficas_raw.mp4'); r.entregar()
