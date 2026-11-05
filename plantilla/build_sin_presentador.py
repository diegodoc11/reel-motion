# -*- coding: utf-8 -*-
# =====================================================================================================
#  reel-motion · PLANTILLA SIN PRESENTADOR  ("hazme un video animado sobre…", sin grabarte)
#  Video 100 % animado con voz en off: estilo recrear en paleta oscura (negro, naranja y blanco), subtítulos centrados
#  abajo, piezas de plantilla/recrear.py. Antes de este build se corre scripts/sin_presentador.py (voz + tiempos).
#
#  Guion de ejemplo (guárdalo en guion.txt y corre:  python scripts/sin_presentador.py <proyecto> --texto guion.txt):
#     Tu negocio necesita agentes de IA. Un agente cuesta entre 25 y 50 dólares al mes. Y hace el trabajo de
#     cuatro personas, diez veces más rápido. Sígueme para más.
#
#  QUÉ CAMBIAR: colores (abajo), el encabezado y el bloque ESCENAS. Las palabras de f('...') deben existir tal cual en
#  words.json (python build.py --guion). Escribe las cifras en el guion como quieras verlas (25, 2.000): así salen.
#     PY build.py --guion      PY build.py --no-audio      PY build.py
# =====================================================================================================
import sys, os
P = os.path.dirname(os.path.abspath(__file__))
_sk = os.path.join(P, '_work', 'skill.txt')
SKILL = open(_sk, encoding='utf-8').read().strip() if os.path.exists(_sk) else os.path.expanduser('~/.claude/skills/reel-motion')
sys.path.insert(0, os.path.join(SKILL, 'scripts')); sys.path.insert(0, os.path.join(SKILL, 'plantilla')); sys.path.insert(0, P)
import motor
AC, NEG, BLA = '#FF6B1A', '#0B0B0B', '#F4F1EC'            # ← colores de marca (acento, fondo, texto)
motor.iniciar(P, colores={'acento': AC, 'tinta': BLA, 'fondo': NEG})
from motor import *
import recrear as R
if '--guion' in sys.argv: guion(); sys.exit()
ft = R.ft

R.escenario(informe='INFORME', tema='AGENTES DE IA', caso='CASO &middot; TU NEGOCIO', usuario='', cap_ancho=1080)
I('#cam', opacity=0)                                       # sin presentador: no hay persona en la esquina
I('#rvigL', opacity=0.07)                                  # el foco claro del estilo, casi apagado sobre fondo oscuro
R.CAP_Y = 1470                                             # subtítulos centrados abajo, a lo ancho
R.CLARO.update({'--pg': NEG, '--gl': '#1C1C1C', '--cb': '#161616', '--cl': BLA, '--tx': '#FFFFFF', '--mu': '#A3A3A3', '--pr': AC,
                '--cf': '#171717', '--ck': BLA, '--pb': '#FFFFFF', '--pt': NEG, '--sh': 'rgba(0,0,0,.55)'})
R.PLANO.update({'--pg': AC, '--gl': '#FF8A4A', '--cb': NEG, '--cl': NEG, '--tx': '#FFFFFF', '--mu': '#FFD3B8', '--pr': AC,
                '--cf': '#FFFFFF', '--ck': NEG, '--pb': NEG, '--pt': '#FFFFFF', '--sh': 'rgba(0,0,0,.28)'})

# ============================== ESCENAS (edita desde aquí) ==============================
# 1 · GANCHO desde el cuadro 0 (la portada): "Tu negocio necesita agentes de IA."
t2 = f('Un')                                               # empieza la escena 2
R.add('<div class="sgan" id="sgan">Tu negocio necesita<br><b>agentes de IA</b></div>')
I('#sgan', opacity=1); FT('#sgan b', ft('agentes'), 0.35, {'scale': 1.25}, {'scale': 1}, 'back.out(2)'); fx(ft('agentes'), 'thump', 0.25)
R.outo('#sgan', t2)

# 2 · "Un agente cuesta entre 25 y 50 dólares al mes."  → tarjeta de precio
t3 = f('Y', t2)
R.tarjeta_precio('tp', 520, 'AGENTE DE IA', 'TRABAJA LAS 24 HORAS', '$25&ndash;50', t2, t_precio=ft('25'),
                 chips=(('AL MES', ft('mes'), ''),), acento=True, t1=t3)

# 3 · "Y hace el trabajo de cuatro personas, diez veces más rápido."  → contador + sello
t4 = f('Sígueme')
R.contador('cn', 470, 'PERSONAS QUE REEMPLAZA', (0, 4, ''), t3, ft('trabajo'), ft('personas') + 0.3, t1=t4)
R.sello('sl', '10X', ft('diez'), y=820)
R.outo('#sl', t4)

# 4 · CIERRE: "Sígueme para más."
R.titulo('tt', ['TU NEGOCIO', 'NO ESPERA'], t4, y=470)
R.boton('bt', 'S&Iacute;GUEME PARA M&Aacute;S &rarr;', ft('más', t4), y=1010)

# subtítulos (desde que termina el gancho) · audio
R.subtitulos(desde=t2, propios=('IA',))
CSS = '''
.sgan{position:absolute;left:0;width:1080px;top:560px;text-align:center;z-index:40;font:900 92px "IT";color:#fff;letter-spacing:-.03em;line-height:1.02}
.sgan b{display:inline-block;color:var(--pr)}
'''
R.cerrar(musica='auto', volumen_musica=0.28, css_extra=CSS)
