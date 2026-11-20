# -*- coding: utf-8 -*-
# =====================================================================================================
#  reel-motion · PLANTILLA ESTILO CARITAS  ("edítalo con reel-motion estilo caritas")
#  Caricatura pintada a pincel con acuarela (motor ClaudeAnimationBase: p5.js + p5.brush): Clawd, el muñequito naranja
#  de Claude, ACTÚA cada frase (pone caras, salta, corre, se duerme, celebra) entre objetos pintados. Sin textos: solo
#  se pintan cifras o UNA palabra clave gigante (13 AÑOS, ×6, ERA). Las líneas "hierven" a 12 dibujos por segundo y
#  cada toma entra con un brochazo. Presentador chico abajo a la derecha y subtítulo fantasma.
#  Las escenas van en escenas_caritas.js (copia de estilos/caritas/plantilla_escenas.js); los objetos pintados están
#  en estilos/caritas/props.js y props2.js; Clawd y sus 31 emociones vienen del motor (lee su ANIMATION_GUIDE.md).
#
#  QUÉ CAMBIAR: CORRECCIONES, ROJAS, TOMAS (ESC), SIN_BROCHAZO y GOLPES (y las escenas). Frases de ft('...') TAL CUAL
#  en words.json:  python build_caritas.py --guion
#  Comandos:  --fotos (una foto por toma, ~1 min) · --fotos 3s,12.5s · sin nada (pinta ~7-12 min por minuto de video
#  y monta) · --seguir (retoma un pintado que se cortó) · --componer (vuelve a montar sin pintar)
#  El ejemplo es el reel ERA (77 s): "13 años del caballo al carro… ¿cuánto falta para que todos usemos IA?"
# =====================================================================================================
import os
import sys

P = os.path.dirname(os.path.abspath(__file__))
_sk = os.path.join(P, '_work', 'skill.txt')
SKILL = open(_sk, encoding='utf-8').read().strip() if os.path.exists(_sk) else os.path.expanduser('~/.claude/skills/reel-motion')
sys.path.insert(0, os.path.join(SKILL, 'estilos')); sys.path.insert(0, os.path.join(SKILL, 'estilos', 'caritas'))
import componer as C  # noqa: E402
import caritas as CA  # noqa: E402

CORRECCIONES = {'i': 'IA', 'adaptó': 'adoptó', 'cassette': 'casete', 'cassettes': 'casetes'}
ROJAS = ('Trece', '1913,', 'smartphone.', 'siete', 'seis', 'tres', 'dos.', 'nietos.', 'natural.', 'teclados',
         'casetes', 'clientes', 'casete.', 'agentes', 'moda.', 'triunfen', 'quiebren.', 'ERA')
BPM, OFFSET = 110, 0.02          # tempo al que rebota Clawd (el de la música) y segundo de su primer golpe; 110 sirve casi siempre
r = C.Reel(P, estilo='caritas', correcciones=CORRECCIONES, rojas=ROJAS, musica='auto', volumen_musica=0.28, inicio_musica=24.0)
if '--guion' in sys.argv: r.guion(); sys.exit()
ft = r.ft

# ============================== TOMAS: dónde empieza cada escena (edita) ==============================
ESC = dict(A=0.0, B=ft('en', despues=ft('1913')) - 0.1, C=ft('Saltemos') - 0.12, D=ft('el', despues=ft('tenido')) - 0.12,
           E=ft('Desde ese punto') - 0.12, F=ft('ChatGPT') - 0.2, G=ft('llevamos') - 0.12, H=ft('¿Cuántos') - 0.12,
           I=ft('esto') + 0.5, J1=ft('Solo miremos') - 0.12, J2=ft('Hoy') - 0.12, K=ft('Porque') - 0.12,
           L=ft('natural') - 0.38, M=ft('muchacho') - 0.4, N=ft('niños', despues=ft('Walkman')) - 0.35,
           O=ft('El negocio') - 0.12, P=ft('instalar') - 0.12, Q=ft('Será') - 0.12, R=ft('Comenta') + 0.02)
# tomas que siguen en el mismo dibujo, sin brochazo (no suena el swipe). El brochazo en sí lo pone cada escena con transicion().
SIN_BROCHAZO = ('E', 'J2')
# golpes con "pop": cada cifra o palabra clave que se pinta
GOLPES = [ft('2007'), ft('siete'), ft('seis'), ft('dos'), ft('14'), ft('hoy mismo'), ft('ERA')]

# ============================== (no hace falta editar desde aquí) ==============================
d = CA.proyecto(r, ESC, 'escenas_caritas.js', bpm=BPM, offset=OFFSET)
if '--fotos' in sys.argv:
    i = sys.argv.index('--fotos'); seg = sys.argv[i + 1] if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('--') else None
    CA.fotos(r, d, ESC, seg); sys.exit()
if '--componer' not in sys.argv:
    CA.pintar(r, d, 'caritas_raw.mp4', seguir='--seguir' in sys.argv)
r.sfx = r.efectos_tomas(ESC, saltar=SIN_BROCHAZO, ganancia=0.08) + r.golpes(GOLPES)
r.subtitulos(fantasma='#A0978A')       # gris más oscuro que en otros estilos: sobre el piso beige el claro se pierde
r.audio(); r.componer('caritas_raw.mp4'); r.entregar()
