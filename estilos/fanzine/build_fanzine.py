# -*- coding: utf-8 -*-
# =====================================================================================================
#  reel-motion · PLANTILLA ESTILO FANZINE  ("edítalo con reel-motion estilo fanzine")
#  Impresión risográfica de 3 tintas (azul, rosa, amarillo) con grano y puntitos de imprenta; todo el video es UNA
#  maqueta larga: cada frase es una estación al lado de la otra y la cámara viaja de una a otra; abajo corre un camino
#  que las une (aquí, una línea de tiempo que se pinta de amarillo mientras hablas). Presentador chico abajo a la
#  derecha y subtítulo fantasma en tinta azul. Las escenas van en escenas_fanzine.js (copia de
#  estilos/fanzine/plantilla_escenas.js); aquí van las tomas, los golpes y la música.
#
#  QUÉ CAMBIAR: CORRECCIONES, ROJAS, TOMAS y GOLPES (y las escenas en escenas_fanzine.js). Las frases de ft('...')
#  deben existir TAL CUAL en words.json:  python build_fanzine.py --guion
#  Comandos:  python build_fanzine.py --fotos 3s,12.5s   (fotos rápidas)  ·  python build_fanzine.py   (rueda y monta)
#             python build_fanzine.py --componer          (solo vuelve a montar, sin volver a rodar el fondo)
#  El ejemplo es el reel ERA (77 s): "13 años del caballo al carro… ¿cuánto falta para que todos usemos IA?"
# =====================================================================================================
import os
import sys

P = os.path.dirname(os.path.abspath(__file__))
_sk = os.path.join(P, '_work', 'skill.txt')
SKILL = open(_sk, encoding='utf-8').read().strip() if os.path.exists(_sk) else os.path.expanduser('~/.claude/skills/reel-motion')
sys.path.insert(0, os.path.join(SKILL, 'estilos')); sys.path.insert(0, os.path.join(SKILL, 'estilos', 'fanzine'))
import componer as C  # noqa: E402
import fanzine as FZ  # noqa: E402

# palabras que whisper escribe mal (se corrigen en el subtítulo y en tp()/ft())
CORRECCIONES = {'i': 'IA', 'adaptó': 'adoptó', 'cassette': 'casete', 'cassettes': 'casetes'}
# palabras que se encienden en ROJO en el subtítulo (la palabra clave de cada frase)
ROJAS = ('Trece', '1913,', 'smartphone.', 'siete', 'seis', 'tres', 'dos.', 'nietos.', 'natural.', 'teclados',
         'casetes', 'clientes', 'casete.', 'agentes', 'moda.', 'triunfen', 'quiebren.', 'ERA')
r = C.Reel(P, estilo='fanzine', correcciones=CORRECCIONES, rojas=ROJAS, musica='auto', volumen_musica=0.28, inicio_musica=24.0)
if '--guion' in sys.argv: r.guion(); sys.exit()
ft = r.ft

# ============================== TOMAS: dónde empieza cada estación (edita) ==============================
ESC = dict(A=0.0, B=ft('en', despues=ft('1913')) - 0.1, C=ft('Saltemos') - 0.12, D=ft('el', despues=ft('tenido')) - 0.12,
           E=ft('Desde ese punto') - 0.12, F=ft('ChatGPT') - 0.2, G=ft('llevamos') - 0.12, H=ft('¿Cuántos') - 0.12,
           I=ft('esto') + 0.5, J1=ft('Solo miremos') - 0.12, J2=ft('Hoy') - 0.12, K=ft('Porque') - 0.12,
           L=ft('natural') - 0.38, M=ft('muchacho') - 0.4, N=ft('niños', despues=ft('Walkman')) - 0.35,
           O=ft('El negocio') - 0.12, P=ft('instalar') - 0.12, Q=ft('Será') - 0.12, R=ft('Comenta') + 0.02)
# golpes con "pop": cada palabra clave que se imprime y cada sello
hoy = ft('hoy', despues=ESC['P'])
GOLPES = [ft('Trece'), ft('segundo'), ft('2007'), ft('primer'), ft('siete'), ft('seis'), ft('años', despues=ft('tres')),
          ft('dos'), ft('adopción'), ft('8'), ft('creció'), ft('natural'), ft('14'), ft('normal'),
          ft('IA', despues=ESC['O']), ft('casete', despues=ESC['O']), hoy, ft('no', despues=hoy),
          ft('triunfen') + 0.3, ft('quiebren') + 0.2, ft('ERA')]

# ============================== (no hace falta editar desde aquí) ==============================
html = FZ.armar(r, ESC, 'escenas_fanzine.js', os.path.join('_work', 'fanzine.html'))
if '--fotos' in sys.argv:
    FZ.fotos(html, sys.argv[sys.argv.index('--fotos') + 1], os.path.join(P, '_work', 'fotos', 'fanzine')); sys.exit()
if '--componer' not in sys.argv:
    FZ.rodar(html, os.path.join(P, 'fanzine_raw.mp4'))
r.sfx = r.efectos_tomas(ESC, antes=0.22) + r.golpes(GOLPES)       # el viaje de la cámara arranca 0,25 s antes de cada estación
r.subtitulos(fantasma='#C9C0B2', tinta='#1D58C4', borde='#F3EEE3')
r.audio(); r.componer('fanzine_raw.mp4'); r.entregar()
