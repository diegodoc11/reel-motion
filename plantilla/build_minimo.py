# -*- coding: utf-8 -*-
# =====================================================================================================
#  reel-motion · PLANTILLA MÍNIMA  (empieza por aquí)
#  Un reel completo con solo 5 tipos de pieza, todo en el encuadre 'card' (presentador recortado sobre la tarjeta):
#     gancho()   titular que aparece palabra por palabra
#     cabecera() antetítulo + titular de 1-3 líneas
#     lista()    fichas que aparecen una por una
#     numero()   dato gigante con rótulos
#     cta()      "Comenta PALABRA"
#  + subtítulos palabra por palabra + música + efectos.
#
#  QUÉ CAMBIAR: solo el bloque ESCENAS. Las frases entre comillas de f('...') deben existir TAL CUAL en words.json
#  (míralas con:  python build.py --guion ). Cada escena empieza cuando se dice su primera palabra y termina donde
#  empieza la siguiente. Cuando esto ya se vea bien, sube de nivel con las recetas de plantilla/build.py
#  (terminal, papel, collage, tarjeta flotante, cambio de color…).
# =====================================================================================================
import sys, os
P = os.path.dirname(os.path.abspath(__file__))
_sk = os.path.join(P, '_work', 'skill.txt')
SKILL = open(_sk, encoding='utf-8').read().strip() if os.path.exists(_sk) else os.path.expanduser('~/.claude/skills/reel-motion')
sys.path.insert(0, os.path.join(SKILL, 'scripts')); sys.path.insert(0, P)
import motor
motor.iniciar(P, correcciones={'cloud': 'Claude'})        # palabras que whisper oyó mal -> como deben escribirse
from motor import *
if '--guion' in sys.argv: guion(); sys.exit()             # imprime la transcripción con tiempos y sale

escenario('card')

# ============================== ESCENAS (edita desde aquí) ==============================
# 1 · GANCHO: las primeras palabras del video, tal como están en words.json (máx. ~18 letras por línea)
t1 = f('fueron hechas')                                   # ← primera palabra de la escena 2
gancho('Estas animaciones que estás viendo en pantalla', hasta=t1, saltos=(1, 4), acento=(1, 6), marca='Claude Code')

# 2 · TITULAR: antetítulo + líneas que suben cuando se dicen ('red' = color de acento)
t2 = f('No tuve')
cabecera('e2', t1, t2, antetitulo='SIN EDITOR · SIN ANIMADOR',
         lineas=[('Hechas con', f('hechas'), ''), ('inteligencia artificial', f('inteligencia'), 'red')])

# 3 · NÚMERO gigante con rótulos
t3 = f('Solo le di')
numero('e3', t2, t3, '$0', f('peso'), antetitulo='LO QUE PAGUÉ', rotulos=[('pesos', f('para generarlas'))])

# 4 · LISTA: cada ficha aparece cuando se nombra
t4 = f('Y no,')
lista('e4', t3, t4, antetitulo='ASÍ DE SIMPLE',
      items=[('1 instrucci&oacute;n', f('instrucción')), ('Claude Code + Opus 5.5', f('Claude Code')), ('Menos de 5 minutos', f('5 minutos'))])

# 5 · TITULAR
t5 = f('Puedo')
cabecera('e5', t4, t5, antetitulo='NO SOY DISEÑADOR',
         lineas=[('Y aun as&iacute;', f('aún así'), ''), ('logr&eacute; esto', f('lograr'), 'red')])

# 6 · LISTA
t6 = f('Diego')
lista('e6', t5, t6, antetitulo='PUEDO CAMBIAR',
      items=[('Los colores', f('colores')), ('La tipograf&iacute;a', f('tipografía')), ('Mis im&aacute;genes', f('imágenes')), ('El dise&ntilde;o', f('diseño', t5))])

# 7 · objeción y respuesta: dos TITULARES seguidos
t7 = f('Bueno'); t8 = f('Yo llevo')
cabecera('e7', t6, t7, antetitulo='LA DUDA DE SIEMPRE', lineas=[('&iquest;Me sale', f('salir'), ''), ('car&iacute;simo?', f('carísimo'), 'red')])
cabecera('e8', t7, t8, antetitulo='MODELO OPUS 5.5', lineas=[('No.', f('no,', t7), 'red'), ('Es barato', f('barato'), '')])

# 8 · dos NÚMEROS seguidos
t9 = f('De hecho'); t10 = f('Ahora bien')
numero('e9', t8, t9, '<u>+</u>7', f('una semana'), antetitulo='USÁNDOLO TODO EL DÍA', rotulos=[('d&iacute;as', f('semana')), ('de uso', f('usándolo'))])
numero('e10', t9, t10, '3%', f('3%'), antetitulo='LA ANIMACIÓN MÁS PESADA', rotulos=[('del uso', f('de mi'))])

# 9 · TITULARES
t11 = f('Armé'); t12 = f('Si quieres')
cabecera('e11', t10, t11, antetitulo='¿SE TE HACE CARO?', lineas=[('Cotiza', f('contrata'), ''), ('un animador', f('animador'), 'red')])
cabecera('e12', t11, t12, antetitulo='SKILL DE CLAUDE', lineas=[('Edita tus videos', f('edita'), ''), ('en autom&aacute;tico', f('automática'), 'red')])

# 10 · CIERRE
cta('e13', t12, 'VIDEO', f('video', t12), apoyo='y te la paso por privado &darr;', t_apoyo=f('paso', t12),
    antetitulo='¿QUIERES QUE TE LA ENVÍE?', t_verbo=f('comenta', t12))
# ============================== fin de las escenas ==============================

subtitulos(desde=t1, cambios=[('video', 'VIDEO', t12)])   # el gancho no lleva subtítulos; la palabra clave va en mayúsculas
cerrar(musica='auto', volumen_musica=0.28)                # 'auto' = 1ª pista de <proyecto>/musica o de recursos/musica · None = sin música
