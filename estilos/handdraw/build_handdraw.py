# -*- coding: utf-8 -*-
# =====================================================================================================
#  reel-motion · PLANTILLA ESTILO HANDDRAW  ("edítalo con reel-motion estilo handdraw")
#  Pizarra de papel crema: íconos de línea de colores que se trazan solos (SIN mano que dibuja), textos que se
#  escriben letra por letra y escenas que se limpian. Limpio y claro: datos y procesos. Motor: handdraw-skill.
#  Las escenas van AQUÍ MISMO (Python): r.escena(t0) · r.dib(id, dibujo, cx, cy, t) · r.txt(id, 'TEXTO', cx, cy, fs, t)
#  · r.caja(...). Dibujos: D = plantilla/dibujos.py (los de la pizarra) e I = estilos/handdraw/iconos.py. Máximo 8 piezas
#  por escena y una sola cosa dibujándose a la vez (guardar() avisa).
#     python build_handdraw.py --guion       el guion con el segundo de cada frase
#     python build_handdraw.py --solo-json   solo arma el project.json (revisa los avisos)
#     python build_handdraw.py               rueda (~1,4 s por segundo de video) y monta · --componer (solo monta)
#  Zona de dibujo: y 180-1150 (arriba el título, al medio el dibujo, abajo el rótulo); el subtítulo va en y 1230 y el
#  presentador abajo a la derecha. El ejemplo es el reel ERA (77 s).
# =====================================================================================================
import os
import sys

P = os.path.dirname(os.path.abspath(__file__))
_sk = os.path.join(P, '_work', 'skill.txt')
SKILL = open(_sk, encoding='utf-8').read().strip() if os.path.exists(_sk) else os.path.expanduser('~/.claude/skills/reel-motion')
sys.path.insert(0, os.path.join(SKILL, 'estilos', 'handdraw'))
import handdraw as HD  # noqa: E402
import iconos as I  # noqa: E402
import dibujos as D  # noqa: E402

CORRECCIONES = {'i': 'IA', 'adaptó': 'adoptó', 'cassette': 'casete', 'cassettes': 'casetes'}
ROJAS = ('Trece', '1913,', 'smartphone.', 'siete', 'seis', 'tres', 'dos.', 'nietos.', 'natural.', 'teclados',
         'casetes', 'clientes', 'casete.', 'agentes', 'moda.', 'triunfen', 'quiebren.', 'ERA')
# titulo='TU NOMBRE' pone un rótulo chico arriba a la izquierda; vacío = sin rótulo
r = HD.Reel(P, titulo='', correcciones=CORRECCIONES, rojas=ROJAS, musica='auto', volumen_musica=0.28, inicio_musica=24.0)
ft = r.ft
if '--guion' in sys.argv: r.guion(); sys.exit()

# ------------------------------------------------------------------ 1. 13 años: del caballo al carro (1900 -> 1913)
r.escena(0)
r.txt('t13', '13 AÑOS', 540, 290, 180, 0.0, escribir=False, crecer=(1.08, 0.0, 0.5))           # portada desde el cuadro 0
r.dib('cab', D.caballo(), 300, 600, ft('caballo') - 0.3, dur=0.7, escala=1.0, color='cafe')
r.dib('fl', I.flecha_curva(), 690, 560, ft('a', despues=ft('caballo') + 0.1), dur=0.35, escala=0.75, color='gris')
r.dib('car', D.carro(), 800, 800, ft('carro') - 0.3, dur=0.55, escala=0.78, color='azul')
r.dib('lt', I.linea_tiempo(), 540, 1000, ft('desde'), dur=0.45, color='tinta')
r.txt('a19', '1900', 165, 1085, 66, ft('1900'))
r.txt('a13', '1913', 915, 1085, 66, ft('1913'))
r.dib('cm1', I.circulo_marca(270, 140), 915, 1085, ft('1913') + 0.35, dur=0.35, color='rojo')

# ------------------------------------------------------------------ 2. todo se movía mucho más despacio
r.escena(ft('en', despues=ft('1913')) - 0.1)
r.dib('rel', D.reloj_arena(), 245, 610, ft('época') - 0.15, dur=0.6, escala=1.25, color='ambar')
r.dib('car2', I.caracol(), 730, 640, ft('movían') - 0.3, dur=0.85, escala=1.75, color='verde')
r.dib('res2', I.resaltador(800, 112), 540, 988, ft('despacio') + 0.05, dur=0.3, sonido=False)
r.txt('des', 'MUCHO MÁS DESPACIO', 540, 982, 74, ft('mucho'), dur=0.7)

# ------------------------------------------------------------------ 3. saltemos para adelante: el 2º gran salto
r.escena(ft('Saltemos') - 0.12)
r.dib('ms', I.mono_salta(), 205, 930, ft('Saltemos'), dur=0.45, escala=1.6, color='tinta',
      mover=(470, -10, ft('Saltemos') + 0.5, 0.75))
r.dib('arc', I.flecha_curva(700, 300), 540, 690, ft('Saltemos') + 0.47, dur=0.42, escala=1.2, color='rojo')
r.txt('seg', 'EL 2º GRAN SALTO', 540, 300, 96, ft('El', despues=ft('adelante')), dur=0.7)
r.dib('ray', D.rayo(), 930, 470, ft('tecnológico') - 0.1, dur=0.35, escala=1.1, color='ambar', acento='ambar')

# ------------------------------------------------------------------ 4. el smartphone: 2007, el primer iPhone
r.escena(ft('el', despues=ft('tenido')) - 0.12)
r.dib('cel', I.iphone(), 540, 715, ft('smartphone') - 0.3, dur=0.55, escala=1.5, color='tinta')
r.txt('a07', '2007', 540, 290, 160, ft('2007'), dur=0.4)
r.dib('d1', I.destello(), 780, 520, ft('aparece'), dur=0.25, escala=1.0, color='ambar', acento='ambar')
r.dib('d2', I.destello(), 300, 610, ft('aparece') + 0.25, dur=0.25, escala=0.75, color='ambar', acento='ambar', sonido=False)
r.txt('ip', 'EL PRIMER IPHONE', 540, 1070, 70, ft('primer'), dur=0.6)

# ------------------------------------------------------------------ 5. todo el mundo con smartphone: 7 años
r.escena(ft('Desde ese punto') - 0.12)
r.txt('anio', '2007  →  2014', 540, 1030, 66, ft('Desde ese punto'), dur=2.1)
for k, x in enumerate((120, 330, 540, 750, 960)):
    r.dib(f'p{k}', I.persona(celular=True), x, 760, ft('todo el mundo') + k * 0.22, dur=0.3, escala=0.82, color='azul',
          sonido=(k % 2 == 0))
r.txt('s7', '7 AÑOS', 540, 300, 190, ft('siete'), dur=0.45)
r.dib('sub7', I.subrayado(560, 60), 540, 420, ft('años', despues=ft('siete')), dur=0.3, color='rojo')

# ------------------------------------------------------------------ 6. ChatGPT crece 6 veces más rápido que el iPhone
r.escena(ft('Ahora mira') - 0.12)
CRV_I = 'M80,480 C300,470 520,420 620,330 C700,250 760,180 860,150'
CRV_C = 'M80,480 C160,470 210,380 250,250 C285,140 320,90 420,60'
r.dib('ejes', D.grafica([]), 540, 730, ft('Ahora mira'), dur=0.5, color='tinta')
r.dib('cc', I.curva(CRV_C, 900, 560, 10), 540, 730, ft('ChatGPT') + 0.06, dur=0.8, color='rojo', sonido=False)
r.txt('lc', 'ChatGPT', 665, 505, 52, ft('creciendo'), dur=0.4)
r.txt('x6', '×6', 540, 290, 210, ft('seis'), dur=0.3)
r.dib('cm6', I.circulo_marca(360, 240), 540, 290, ft('veces'), dur=0.35, color='rojo')
r.dib('ci', I.curva(CRV_I, 900, 560, 8), 540, 730, ft('se', despues=ft('velocidad')), dur=0.7, color='gris', sonido=False)
r.txt('li', 'iPhone', 870, 548, 48, ft('iPhone', despues=ft('velocidad')), dur=0.35)

# ------------------------------------------------------------------ 7. apenas 3 años de IA generativa
r.escena(ft('llevamos') - 0.12)
r.txt('ape', 'APENAS', 540, 290, 120, ft('apenas'), dur=0.4)
r.dib('cal', D.calendario(), 540, 690, ft('llevamos'), dur=0.5, escala=1.6, color='tinta')
r.txt('n3', '3', 540, 754, 270, ft('tres'), dur=0.2)
r.txt('gen', 'AÑOS DE IA GENERATIVA', 540, 1050, 66, ft('años', despues=ft('tres')), dur=0.6)

# ------------------------------------------------------------------ 8. ¿cuántos años nos quedan? Yo creo que dos
r.escena(ft('¿Cuántos') - 0.12)
r.dib('mp', I.mono_piensa(), 250, 800, ft('¿Cuántos'), dur=0.6, escala=1.9, color='tinta')
for k, (x, y) in enumerate(((520, 560), (650, 455), (780, 560))):
    r.dib(f'q{k}', I.pregunta_signo(), x, y, ft('quedan') - 0.15 + k * 0.25, dur=0.25, escala=0.85, color='rojo', sonido=(k == 0))
r.dib('mun', I.mundo(), 800, 880, ft('mundo', despues=ft('quedan')) - 0.2, dur=0.5, escala=1.4, color='azul')
r.txt('dos', '2 AÑOS', 540, 290, 180, ft('dos') - 0.12, dur=0.35)
r.dib('cm2', I.circulo_marca(880, 330), 540, 290, ft('dos') + 0.3, dur=0.3, color='rojo')

# ------------------------------------------------------------------ 9. "eso lo usarán mis nietos" — no
r.escena(ft('esto') - 0.12)
r.dib('abu', D.abuelo(), 240, 830, ft('esto'), dur=0.6, escala=1.35, color='tinta')
r.dib('glo', D.globo(620, 300), 700, 520, ft('eso lo usarán') - 0.15, dur=0.35, color='gris')
r.txt('nie', 'ESO LO USARÁN\nMIS NIETOS', 700, 490, 58, ft('eso lo usarán'), dur=0.75)
r.dib('xn', I.tachar(560, 250), 700, 490, ft('nietos'), dur=0.25, color='rojo')

# ------------------------------------------------------------------ 10. el nivel de adopción de los niños
r.escena(ft('Solo miremos') - 0.12)
r.dib('med', I.medidor(), 540, 720, ft('miremos'), dur=0.5, escala=2.2, color='tinta')
r.txt('niv', 'NIVEL DE ADOPCIÓN', 540, 290, 86, ft('nivel'), dur=0.6)
r.dib('agu', I.aguja(), 540, 887, ft('adopción'), dur=0.25, escala=2.2, color='tinta', rotar=(150, ft('adopción') + 0.3, 0.8))
r.dib('nin', I.nino(), 935, 1010, ft('niños') - 0.24, dur=0.35, escala=1.3, color='tinta')

# ------------------------------------------------------------------ 11. un niño de 8 años: pregúntale a ChatGPT (no a Google)
r.escena(ft('Hoy') - 0.12)
t2p = ft('pregúntale', despues=ft('Google'))
r.dib('kid', I.nino(), 175, 860, ft('niño', despues=ft('Hoy')) - 0.2, dur=0.45, escala=1.9, color='tinta')
r.txt('k8', '8 AÑOS', 175, 1100, 60, ft('8'), dur=0.3)
r.dib('g1', D.globo(680, 250), 690, 470, ft('pregúntale') - 0.15, dur=0.3, color='gris')
r.txt('t1', 'PREGÚNTALE A GOOGLE', 690, 435, 46, ft('pregúntale'), dur=0.6)
r.dib('x1', I.tachar(600, 160), 690, 435, ft('Google') + 0.2, dur=0.25, color='rojo')
r.dib('g2', D.globo(680, 250), 690, 800, t2p - 0.14, dur=0.3, color='verde')
r.txt('t2', 'PREGÚNTALE A CHATGPT', 690, 765, 46, t2p, dur=0.6)
r.dib('ok', I.check(), 1000, 670, ft('ChatGPT', despues=t2p) + 0.15, dur=0.25, escala=1.1, color='verde')

# ------------------------------------------------------------------ 12. creció con las respuestas en ChatGPT, no en Google
r.escena(ft('Porque') - 0.12)
r.dib('kid2', I.nino(), 175, 830, ft('Porque'), dur=0.4, escala=1.6, color='tinta', crecer=(0.55, ft('creció'), 0.7))
r.dib('qd', I.pregunta_signo(), 345, 520, ft('dudas') - 0.1, dur=0.3, escala=1.1, color='gris')
r.dib('fl12', D.flecha(), 505, 640, ft('preguntas'), dur=0.3, escala=1.0, color='tinta')
r.dib('vc', I.ventana_chat(), 800, 620, ft('ChatGPT', despues=ft('preguntas')) - 0.25, dur=0.45, escala=1.05, color='tinta')
r.txt('cg', 'CHATGPT', 800, 830, 52, ft('ChatGPT', despues=ft('preguntas')), dur=0.4)
r.dib('bb', I.barra_busqueda(), 560, 1010, ft('no', despues=ft('preguntas')), dur=0.35, escala=1.1, color='gris')
r.txt('tg', 'GOOGLE', 600, 1010, 50, ft('en', despues=ft('no', despues=ft('preguntas'))), dur=0.35)
r.dib('xg', I.tachar(580, 150), 560, 1010, ft('Google', despues=ft('preguntas')) + 0.22, dur=0.25, color='rojo')

# ------------------------------------------------------------------ 13. para él es natural: no va a entender los teclados
r.escena(ft('natural') - 0.38)
r.dib('resn', I.resaltador(800, 130), 540, 322, ft('natural') + 0.4, dur=0.3, sonido=False)
r.txt('nat', 'NATURAL', 540, 290, 180, ft('natural'), dur=0.4)
r.dib('nin13', I.nino(), 185, 820, ft('Esa generación') + 0.26, dur=0.4, escala=1.7, color='tinta')
r.dib('tec', D.teclado(), 690, 800, ft('teclados') - 0.3, dur=0.55, escala=1.15, color='tinta')
r.dib('qt', I.pregunta_signo(), 690, 570, ft('teclados') + 0.2, dur=0.25, escala=1.2, color='rojo')

# ------------------------------------------------------------------ 14. un muchacho de 14 no entiende los casetes y el Walkman
r.escena(ft('muchacho') - 0.4)
r.dib('mu', I.muchacho(), 195, 800, ft('muchacho') - 0.2, dur=0.45, escala=1.65, color='tinta')
r.txt('m14', '14 AÑOS', 195, 1085, 60, ft('14'), dur=0.3)
r.dib('q14', I.pregunta_signo(), 370, 520, ft('entiende'), dur=0.25, escala=1.0, color='rojo')
r.dib('cas', D.casete(), 745, 560, ft('cassettes') - 0.25, dur=0.55, escala=1.15, color='tinta')
r.dib('wal', D.walkman(), 745, 950, ft('Walkman') - 0.26, dur=0.5, escala=0.9, color='tinta')

# ------------------------------------------------------------------ 15. si para los niños es normal, para tus clientes también
r.escena(ft('niños', despues=ft('Walkman')) - 0.35)
r.dib('nin15', I.nino(), 190, 770, ft('niños', despues=ft('Walkman')) - 0.2, dur=0.4, escala=1.6, color='tinta')
r.txt('nor', 'ES NORMAL', 215, 1020, 54, ft('es normal'), dur=0.4)
r.dib('fl15', D.flecha(), 405, 770, ft('para tus'), dur=0.25, escala=1.0, color='gris')
for k, x in enumerate((595, 775, 955)):
    r.dib(f'cl{k}', I.persona(), x, 770, ft('clientes') + k * 0.2, dur=0.3, escala=0.76, color='azul', sonido=(k == 0))
r.txt('tc', 'TUS CLIENTES', 540, 300, 100, ft('clientes'), dur=0.55)

# ------------------------------------------------------------------ 16. el negocio sin IA va a sonar a casete
r.escena(ft('El negocio') - 0.12)
r.dib('tie', D.tienda(), 540, 690, ft('negocio') - 0.12, dur=0.7, escala=1.4, color='tinta')
r.txt('sin', 'SIN IA', 540, 442, 44, ft('no', despues=ft('negocio')), dur=0.3)
r.txt('son', 'SUENA A CASETE', 470, 1085, 66, ft('sonar'), dur=0.55)
r.dib('cas16', D.casete(), 935, 1080, ft('cassette', despues=ft('sonar')) - 0.22, dur=0.35, escala=0.5, color='gris')
r.dib('gri', D.grieta(), 540, 690, ft('cassette', despues=ft('sonar')) + 0.04, dur=0.22, escala=1.4, color='rojo')

# ------------------------------------------------------------------ 17. agentes IA que reemplazan el trabajo lento y caro: hoy mismo
r.escena(ft('instalar') - 0.12)
r.dib('rb', D.robot(), 810, 670, ft('instalar'), dur=0.55, escala=1.25, color='azul')
r.txt('ag', 'AGENTES IA', 810, 950, 60, ft('agentes'), dur=0.45)
r.dib('fl17', D.flecha(), 545, 680, ft('reemplazan'), dur=0.3, escala=1.0, color='rojo')
r.dib('pap', D.papeles(), 250, 660, ft('trabajo') - 0.2, dur=0.45, escala=1.2, color='gris')
r.txt('lc', 'LENTO Y CARO', 270, 950, 60, ft('lento'), dur=0.5)
r.dib('xh', I.tachar(360, 360), 260, 660, ft('humanos') + 0.1, dur=0.25, color='rojo')
r.txt('hoy', 'HOY MISMO', 540, 290, 140, ft('hoy mismo'), dur=0.45)
r.txt('moda', 'NO ES MODA', 540, 1075, 60, ft('no', despues=ft('hoy mismo')), dur=0.5)

# ------------------------------------------------------------------ 18. separará a las empresas que triunfen de las que quiebren
r.escena(ft('Será') - 0.12)
r.dib('div', I.linea_vertical(), 540, 760, ft('Será'), dur=0.4, color='gris')
r.dib('tieL', D.tienda(), 280, 650, ft('separará'), dur=0.35, escala=0.75, color='azul')
r.dib('tieR', D.tienda(), 800, 650, ft('separará') + 0.4, dur=0.3, escala=0.75, color='gris')
r.dib('tro', D.trofeo(), 280, 330, ft('triunfen') + 0.02, dur=0.45, escala=0.85, color='ambar')
r.txt('tri', 'TRIUNFAN', 280, 1000, 66, ft('triunfen'), dur=0.45)
r.dib('gri18', D.grieta(), 800, 650, ft('quiebren'), dur=0.22, escala=0.75, color='rojo')
r.txt('qui', 'QUIEBRAN', 800, 1000, 66, ft('quiebren'), dur=0.4)
r.dib('fd', D.flecha_abajo(), 800, 330, ft('quiebren') + 0.12, dur=0.22, escala=0.9, color='rojo')

# ------------------------------------------------------------------ 19. CTA: comenta ERA y te envío la clase
r.escena(ft('Comenta') + 0.02)
r.txt('com', 'COMENTA', 540, 290, 130, ft('Comenta') + 0.05, dur=0.35)
r.dib('box', I.comentario(), 540, 570, ft('Comenta') + 0.15, dur=0.45, color='tinta')
r.txt('era', 'ERA', 240, 572, 90, ft('ERA'), dur=0.25, centro=False)
r.dib('subE', I.subrayado(240, 50), 340, 640, ft('ERA') + 0.3, dur=0.3, color='rojo')
r.dib('cls', I.clase(), 540, 860, ft('clase') - 0.22, dur=0.5, escala=1.3, color='tinta')
r.txt('tcl', 'TE ENVÍO LA CLASE', 540, 1100, 60, ft('envío'), dur=0.6)

# =====================================================================================================
r.guardar()
if '--solo-json' in sys.argv: sys.exit()
if '--componer' not in sys.argv: r.render_handdraw()
r.subtitulos(); r.audio(); r.componer('handdraw_raw.mp4'); r.entregar()
