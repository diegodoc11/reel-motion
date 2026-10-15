# -*- coding: utf-8 -*-
# =====================================================================================================
#  reel-motion · PLANTILLA ESTILO NOCHE  ("edítalo con reel-motion estilo noche")
#  Fondo tinta con grilla que deriva + tarjeta roja con el presentador recortado (card)  <->  papel crema con grano y
#  borde rasgado (split). Un solo acento, cifras gigantes, entradas con golpe. Piezas en plantilla/noche.py.
#
#  QUÉ CAMBIAR: solo el bloque ESCENAS. Las frases de f('...') deben existir TAL CUAL en words.json
#  (míralas con:  python build.py --guion ). Cada escena empieza cuando se dice su primera palabra y termina donde
#  empieza la siguiente. El ejemplo de abajo es un reel real de 35 s ("En el chat de IA…") con 8 piezas distintas:
#     gancho · escalera · slam · nodos · comparar (en papel) · whatsapp · lista_tachada (en papel) · cta_sigueme
#  Más piezas (paso, riel, tarjeta_numerada, contador, bateria, checklist, sello, notas, titular, cta_palabra):
#  ver la tabla de SKILL.md ("Estilos: collage y noche") y las docstrings de plantilla/noche.py.
# =====================================================================================================
import sys, os
P = os.path.dirname(os.path.abspath(__file__))
_sk = os.path.join(P, '_work', 'skill.txt')
SKILL = open(_sk, encoding='utf-8').read().strip() if os.path.exists(_sk) else os.path.expanduser('~/.claude/skills/reel-motion')
sys.path.insert(0, os.path.join(SKILL, 'scripts')); sys.path.insert(0, os.path.join(SKILL, 'plantilla')); sys.path.insert(0, P)
import motor
motor.iniciar(P, correcciones={'ella': 'IA'}, colores={'acento': '#D11F1D'})   # palabras mal oídas -> bien escritas · color de marca
from motor import *
import noche as N
if '--guion' in sys.argv: guion(); sys.exit()               # imprime la transcripción con tiempos y sale

N.escenario()                                                # tinta + grilla + viñeta + marcas (va UNA vez)

# ============================== ESCENAS (edita desde aquí) ==============================
# 1 · GANCHO (card): titular palabra por palabra desde el cuadro 0 + escalera debajo
#     "En el chat de IA, tú pides algo, recibes una respuesta y sigues haciendo el trabajo."
t2 = f('Con un')                                             # ← primera palabra de la escena 2
N.gancho('En el chat de IA', hasta=t2, acento=(2,))
N.escalera('e1', f('tú pides'), t2, y0=400,
           pasos=[('Pides algo', f('pides')), ('Recibes una respuesta', f('recibes')), ('El trabajo lo haces tú', f('sigues'))])

# 2 · SLAM (card): "Con un agente, delegas el trabajo."  -> la losa se encoge a encabezado para la escena 3
t3 = f('El agente'); t4 = f('Es la')
N.slam('e2', f('agente') - 0.03, 'AGENTE', icono='bot', t1=t4, sub=[('Delegas el trabajo.', f('delegas'))],
       t_encoge=t3, acercar=1.07)

# 3 · NODOS (card): "El agente recibe un objetivo, lo entiende… decide… herramientas y sigue hasta lograr el resultado…"
N.nodos('e3', t3, t4, y0=366, bucle=f('sigue'),
        nodos=[('objetivo', 'diana', f('objetivo')), ('entiende', 'idea', f('entiende')), ('decide', 'decision', f('decide')),
               ('herramientas', 'herramienta', f('herramientas')), ('resultado', 'check', f('resultado'))],
        notas=[('&rsaquo; analizando lo que pasa', f('sabe'), f('decide')), ('hasta lograrlo', f('hasta lograr'), f('o hasta')),
               ('o hasta que te necesite', f('o hasta'), None)])

# 4 · COMPARAR en PAPEL (split con la toma real): "Es la diferencia entre preguntarle… y decirle… Y así es como trabajo hoy."
pp1 = N.papel('pp1')
t5 = f('El agente', t4)
N.a_split(t4 - 0.06, pp1)
t_ya = f('Y así')
N.comparar('e4', t4, None, titulo=('La diferencia:', f('diferencia')), escribir=True, en=pp1,
           malo=('PREGUNTARLE', '&iquest;C&oacute;mo hago esto?', f('preguntarle'), t_ya),
           bueno=('DECIRLE', 'Enc&aacute;rgate de esto por m&iacute;', f('decirle'), f('trabajo', t_ya),
                  'y solo me avisas si me necesitas', f('solo')))

# 5 · WHATSAPP (card): "El agente, por ejemplo, responde mis mensajes mientras yo estoy en otra cosa."
N.a_card(t5 - 0.18)
t6 = f('Y ese')
N.whatsapp('e5', t5 + 0.2, t6, nombre='Cliente', insignia='AGENTE IA',
           mensajes=[('in', 'Hola, &iquest;tienen cita para ma&ntilde;ana?', t5 + 0.45),
                     dict(lado='out', texto='&iexcl;Claro! Tengo 10 am o 3 pm', t=f('responde') + 0.24, escribe=f('responde') - 0.05, bot=True),
                     ('in', 'A las 3 pm, por favor', f('mensajes') - 0.03),
                     dict(lado='out', texto='Listo, tu cita qued&oacute; agendada', t=f('mientras') + 0.04, escribe=f('mensajes') + 0.26, bot=True),
                     ('in', '&iexcl;Mil gracias!', f('estoy') - 0.03),
                     dict(lado='out', texto='Con gusto. &iexcl;Te esperamos!', t=f('otra') - 0.2, escribe=f('estoy') + 0.2, bot=True)],
           fichas=[('Yo', f('yo', t5)), ('en otra cosa', f('en otra'))])

# 6 · LISTA TACHADA en PAPEL (split con el presentador recortado): "Y ese es el cambio cuando hablamos de agentes de IA."
pp2 = N.papel('pp2')
t7 = f('Y si')
N.a_split(t6 - 0.06, pp2, recorte=True)
N.lista_tachada('e6', t6, None, titulo='Ese es el cambio:', t_titulo=f('ese es'), en=pp2,
                items=[('Chat de IA', f('ese es') + 0.3, f('cambio'), 'chat'), ('Agentes de IA', f('agentes'), None, 'bot')])

# 7 · CIERRE (card): "Y si quieres aprender a ponerlos a trabajar en tu negocio, sígueme."
N.a_card(t7 - 0.2)
N.cta_sigueme('e7', t7, f('sígueme'), t_boton=t7 + 0.15, antetitulo='SI QUIERES APRENDER',
              lineas=[('Ponlos a trabajar', f('ponerlos')), ('en tu negocio', f('en tu'), 'ac')],
              usuario='@soydiegoosorio')                      # ← cambia por tu usuario
# ============================== fin de las escenas ==============================

subtitulos(desde=f('tú pides'), propios=('IA',), cambios=[('sígueme', 'SÍGUEME', t7)])   # el gancho no lleva subtítulos
N.cerrar(musica='auto', volumen_musica=0.28)                 # 'auto' = 1ª pista de <proyecto>/musica o de recursos/musica
