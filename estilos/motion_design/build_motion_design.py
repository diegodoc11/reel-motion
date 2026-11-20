# -*- coding: utf-8 -*-
# =====================================================================================================
#  reel-motion · PLANTILLA ESTILO MOTION DESIGN  ("edítalo con reel-motion estilo motion design")
#  Motion graphics profesional (motor AniDoodle): fondo claro con manchas de color suaves, títulos en Poppins con barra
#  de color, números que suben como odómetro, íconos planos que se arman pieza por pieza, pastillas, insignias y
#  avatares; cada escena sale empujada hacia arriba. Fuerte en números y datos. Presentador chico abajo a la derecha.
#  Es la MISMA lista de escenas que la pizarra animada (mismas funciones); cambia el kit (movimiento.ts).
#  Las escenas van en escenas_motion_design.ts (copia de estilos/motion_design/plantilla_escenas.ts).
#
#  QUÉ CAMBIAR: CORRECCIONES, ROJAS, TOMAS y GOLPES (y las escenas). Frases de ft('...') TAL CUAL en words.json:
#  python build_motion_design.py --guion
#  Comandos:  --fotos 3s,12.5s (hoja de fotos, ~1 min) · sin nada (rueda ~4-5 min por minuto de video y monta) · --componer
#  El ejemplo es el reel ERA (77 s): "13 años del caballo al carro… ¿cuánto falta para que todos usemos IA?"
# =====================================================================================================
import os
import sys

P = os.path.dirname(os.path.abspath(__file__))
_sk = os.path.join(P, '_work', 'skill.txt')
SKILL = open(_sk, encoding='utf-8').read().strip() if os.path.exists(_sk) else os.path.expanduser('~/.claude/skills/reel-motion')
sys.path.insert(0, os.path.join(SKILL, 'estilos')); sys.path.insert(0, os.path.join(SKILL, 'estilos', 'comun'))
import componer as C  # noqa: E402
import anidoodle as AD  # noqa: E402

CORRECCIONES = {'i': 'IA', 'adaptó': 'adoptó', 'cassette': 'casete', 'cassettes': 'casetes'}
ROJAS = ('Trece', '1913,', 'smartphone.', 'siete', 'seis', 'tres', 'dos.', 'nietos.', 'natural.', 'teclados',
         'casetes', 'clientes', 'casete.', 'agentes', 'moda.', 'triunfen', 'quiebren.', 'ERA')
r = C.Reel(P, estilo='motion-design', correcciones=CORRECCIONES, rojas=ROJAS, musica='auto', volumen_musica=0.28, inicio_musica=24.0)
if '--guion' in sys.argv: r.guion(); sys.exit()
ft = r.ft

# ============================== TOMAS: dónde empieza cada escena (edita) ==============================
ESC = dict(A=0.0, B=ft('en', despues=ft('1913')) - 0.1, C=ft('Saltemos') - 0.12, D=ft('el', despues=ft('tenido')) - 0.12,
           E=ft('Desde ese punto') - 0.12, F=ft('ChatGPT') - 0.2, G=ft('llevamos') - 0.12, H=ft('¿Cuántos') - 0.12,
           I=ft('esto') + 0.5, J1=ft('Solo miremos') - 0.12, J2=ft('Hoy') - 0.12, K=ft('Porque') - 0.12,
           L=ft('natural') - 0.38, M=ft('muchacho') - 0.4, N=ft('niños', despues=ft('Walkman')) - 0.35,
           O=ft('El negocio') - 0.12, P=ft('instalar') - 0.12, Q=ft('Será') - 0.12, R=ft('Comenta') + 0.02)
# golpes con "pop": cada palabra clave y cada insignia
hoy = ft('hoy', despues=ESC['P'])
GOLPES = [ft('Trece'), ft('segundo'), ft('2007'), ft('primer'), ft('siete'), ft('seis'), ft('años', despues=ft('tres')),
          ft('dos'), ft('adopción'), ft('8'), ft('creció'), ft('natural'), ft('14'), ft('normal'),
          ft('IA', despues=ESC['O']), ft('casete', despues=ESC['O']), hoy, ft('no', despues=hoy),
          ft('triunfen') + 0.42, ft('quiebren') - 0.02, ft('ERA')]

# ============================== (no hace falta editar desde aquí) ==============================
E = os.path.join(SKILL, 'estilos')
KITS = [os.path.join(E, 'pizarra_animada', 'archivo.ts'), os.path.join(E, 'motion_design', 'movimiento.ts'), os.path.join(E, 'motion_design', 'tipos.ts')]
d = AD.proyecto(r, ESC, 'motionDesign', KITS, 'escenas_motion_design.ts')
if '--fotos' in sys.argv:
    AD.fotos(r, d, 'motionDesign', sys.argv[sys.argv.index('--fotos') + 1]); sys.exit()
if '--componer' not in sys.argv:
    AD.rodar(r, d, 'motionDesign', 'motion_design_raw.mp4')
r.sfx = r.efectos_tomas(ESC) + r.golpes(GOLPES)
r.subtitulos(fantasma='#9C9AA3')
r.audio(); r.componer('motion_design_raw.mp4'); r.entregar()
