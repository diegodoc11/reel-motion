# -*- coding: utf-8 -*-
# =====================================================================================================
#  reel-motion · PLANTILLA ESTILO PIZARRA  ("edítalo con reel-motion estilo pizarra")
#  El presentador recortado CHICO abajo a la derecha; arriba, una pizarra negra con cuadrícula donde CADA FRASE se
#  explica: monigotes que actúan, dibujos a línea que se trazan solos, la palabra clave gigante en rojo y el subtítulo
#  fantasma (la frase en gris y cada palabra se enciende al decirla). Piezas en plantilla/pizarra.py (import pizarra as Z)
#  y dibujos en plantilla/dibujos.py (import dibujos as D).
#
#  QUÉ CAMBIAR: el bloque ESCENAS. Las frases de ft('...') deben existir TAL CUAL en words.json (python build.py --guion).
#  El ejemplo es un reel real de 77 s: "13 años del caballo al carro… ¿cuánto falta para que todos usemos IA?"
#     1 13 AÑOS + caballo → carro  2 reloj de arena  3 EL 2º GRAN SALTO + iPhone 2007  4 monigotes con celular (7 AÑOS)
#     5 gráfica ChatGPT vs iPhone (×6)  6 calendario 3  7 abuelo + ESO LO USARÁN MIS NIETOS  8 NIVEL DE ADOPCIÓN
#     9 niño de 8 años + globos  10 teclado / casete / walkman  11 tienda SIN IA que se agrieta  12 robots AGENTES IA
#     13 HOY MISMO  14 trofeo vs grieta  15 cierre "comenta ERA"
# =====================================================================================================
import sys, os
P = os.path.dirname(os.path.abspath(__file__))
_sk = os.path.join(P, '_work', 'skill.txt')
SKILL = open(_sk, encoding='utf-8').read().strip() if os.path.exists(_sk) else os.path.expanduser('~/.claude/skills/reel-motion')
sys.path.insert(0, os.path.join(SKILL, 'scripts')); sys.path.insert(0, os.path.join(SKILL, 'plantilla')); sys.path.insert(0, P)
import motor
motor.iniciar(P, correcciones={'guía': 'IA', 'i': 'IA', 'adaptó': 'adoptó', 'cassette': 'casete', 'cassette.': 'casete.', 'chatgpt': 'ChatGPT'},
              colores={'acento': '#E5322D', 'tinta': '#F4F4F2', 'fondo': '#111113'})
for _w in motor.WD:                                   # ortografía en español: casete / casetes
    _w['text'] = _w['text'].replace('cassettes', 'casetes').replace('Cassettes', 'Casetes').replace('cassette', 'casete')
from motor import *
import recrear as R
import pizarra as Z
import dibujos as D
if '--guion' in sys.argv: guion(); sys.exit()
ft = R.ft
Z.escenario(firma='TU NOMBRE')                         # ← tu nombre (o firma='' para no ponerla)
ROJO = Z.ROJO; GR = '#8E9099'


def dib(idp, fn, x, y, t, t1=None, dur=0.7, escala=1.0, centro=True, **kw):
    s, w, h = fn(**kw) if kw else fn()
    if escala != 1.0:
        s = f'<g transform="scale({escala})">{s}</g>'; w, h = round(w * escala), round(h * escala)
    Z.dibujo(idp, s, x, y, w, h, t, t1, dur=dur, centro=centro)
    return w, h


# ============================== ESCENAS (edita desde aquí) ==============================
# ------------------------------------------------------------------ 1. del caballo al carro en 13 años
tS = ft('Saltemos')
Z.add('<div class="pzg" id="g13" style="top:330px;font-size:170px;color:#E5322D"><span>13 A&Ntilde;OS</span></div>')
I('#g13', xPercent=-50, opacity=1)                                    # portada: está desde el cuadro 0
FT('#g13', 0.0, 0.5, {'scale': 1.08}, {'scale': 1.0}, 'power2.out')
T('#g13', ft('pasar') - 0.2, 0.3, 'power2.inOut', scale=0.55, y=-62)
dib('cab', D.caballo, 540, 560, ft('pasar'), ft('carro') + 0.05, dur=0.9)
dib('car', D.carro, 540, 640, ft('carro'), ft('época'), dur=0.55)
FT('#car', ft('carro') + 0.5, 1.6, {'x': 0}, {'x': 70}, 'power1.inOut')
# línea de tiempo 1900 → 1913
Z.dibujo('lt1', Z.L('M20,40 H760', 6, GR) + Z.L('M20,20 V60', 6) + Z.L('M760,20 V60', 6), 160, 960, 780, 80, ft('1900'), ft('época'), dur=0.5)
Z.rotulo('a1900', '1900', ft('1900'), 180, 1050, t1=ft('época'), fs=40)
Z.rotulo('a1913', '1913', ft('1913'), 920, 1050, t1=ft('época'), fs=40, color=ROJO)
# "las cosas se movían mucho más despacio": reloj de arena que se llena despacio
dib('ra1', D.reloj_arena, 540, 560, ft('época'), tS, dur=0.6)
Z.frase('fdes', 'mucho m&aacute;s <span style="color:#E5322D">despacio</span>', ft('despacio'), tS, y=930, fs=58, cursiva=True)
T('#g13', ft('época') - 0.2, 0.2, 'power1.in', opacity=0)

# ------------------------------------------------------------------ 2. saltemos para adelante
tSeg = ft('segundo')
Z.mono('m1', 250, 1050, alto=300, pose='parado', cara='feliz', t=tS, t1=ft('smartphone') + 0.1)
Z.dibujo('lt2', Z.L('M20,40 H860', 6, GR), 110, 1050, 880, 80, tS, ft('smartphone') + 0.1, dur=0.4)
Z.frase('fseg', 'EL <span style="color:#E5322D">2&ordm;</span> GRAN SALTO', tSeg, ft('smartphone'), y=380, fs=74)
Z.pose_a('m1', tSeg + 0.1, 'señala_i', dur=0.25)
Z.pose_a('m1', tS + 0.25, 'salta', dur=0.18)
T('#m1', tS + 0.3, 0.55, 'power2.inOut', x=560)
T('#m1', tS + 0.3, 0.27, 'power2.out', y=-150); T('#m1', tS + 0.57, 0.28, 'power2.in', y=0)
Z.pose_a('m1', tS + 0.86, 'brazos', dur=0.2)
fx(tS + 0.3, 'whoosh', 0.16)

# ------------------------------------------------------------------ 3. el smartphone: 2007, el primer iPhone
tDesde = ft('Desde ese punto')
dib('cel', D.celular, 540, 520, ft('smartphone'), tDesde, dur=0.5)
Z.grande('g07', '2007', ft('2007'), tDesde, y=900, fs=150)
Z.rotulo('rip', 'EL PRIMER IPHONE', ft('iPhone'), 540, 1080, t1=tDesde, fs=36, fondo='#E5322D')

# ------------------------------------------------------------------ 4. todo el mundo con smartphone: 7 años
tAhora = ft('Ahora mira')
xs = [150, 330, 510, 690, 870]
for k, x in enumerate(xs):
    Z.mono(f'p{k}', x, 1000, alto=230, pose='parado', cara='feliz', t=ft('todo el mundo', despues=tDesde) + k * 0.12, t1=tAhora)
    Z.pose_a(f'p{k}', ft('smartphone', despues=tDesde) + k * 0.1, 'celular', dur=0.22)
    Z.dibujo(f'pc{k}', Z.F('M4,4 H34 V58 H4 Z', '#E5322D') + Z.L('M4,4 H34 V58 H4 Z', 4), x + 4, 790, 40, 62,
             ft('smartphone', despues=tDesde) + k * 0.1 + 0.18, tAhora, dur=0.2, sonido=False)
Z.grande('g7', '7 A&Ntilde;OS', ft('siete'), tAhora, y=430, fs=170)

# ------------------------------------------------------------------ 5. ChatGPT crece 6 veces más rápido
tLlev = ft('y llevamos')
crv_i = 'M80,480 C300,470 520,420 620,330 C700,250 760,180 860,150'
crv_c = 'M80,480 C160,470 210,380 250,250 C285,140 320,90 420,60'
Z.dibujo('gr', D.grafica([])[0], 90, 520, 900, 560, tAhora, tLlev, dur=0.4)          # los ejes entran con "Ahora mira"
Z.dibujo('gri', Z.L(crv_i, 8, GR), 90, 520, 900, 560, ft('ChatGPT') + 0.3, tLlev, dur=0.9, sonido=False)
Z.rotulo('ri', 'IPHONE', ft('ChatGPT') + 0.9, 850, 610, t1=tLlev, fs=30, color=GR)
Z.dibujo('grc', Z.L(crv_c, 10, ROJO), 90, 520, 900, 560, ft('creciendo'), tLlev, dur=0.7, sonido=False)
Z.rotulo('rc', 'CHATGPT', ft('creciendo') + 0.6, 560, 560, t1=tLlev, fs=34, color=ROJO)
Z.grande('g6', '&times;6', ft('seis'), tLlev, y=330, fs=180)

# ------------------------------------------------------------------ 6. apenas 3 años de IA generativa
tCu = ft('¿Cuántos años')
dib('cal', D.calendario, 540, 540, tLlev, tCu, dur=0.5)
Z.add('<div class="pzg" id="n3" style="top:650px;font-size:210px;color:#F4F4F2;text-shadow:none"><span>3</span></div>')
I('#n3', xPercent=-50); R.pin('#n3', ft('tres'), sc=1.6, g=0.18, snd='thump'); R.outo('#n3', tCu)
Z.frase('fgen', 'a&ntilde;os de IA generativa', ft('tres') + 0.2, tCu, y=930, fs=54, cursiva=True)

# ------------------------------------------------------------------ 7. ¿cuántos años nos quedan? Yo creo que dos
tOsea = ft('O sea')
Z.mono('mq', 380, 1060, alto=330, pose='piensa', cara='serio', t=tCu, t1=tOsea)
for k, (x, y, rot) in enumerate(((560, 560, -12), (650, 470, 8), (740, 560, -6))):
    Z.add(f'<div class="pzg" id="q{k}" style="top:{y}px;left:{x}px;font-size:120px;color:#E5322D;text-shadow:0 0 22px rgba(229,50,45,.55)"><span>?</span></div>')
    I(f'#q{k}', rotation=rot)
    R.pin(f'#q{k}', ft('quedan', despues=tCu) + k * 0.16 - 0.3, sc=0.4, snd='pop', g=0.1); R.outo(f'#q{k}', ft('dos', despues=tCu))
Z.grande('g2', '2', ft('unos', despues=tCu), ft('esto', despues=tOsea), y=420, fs=280)
Z.cara('mq', ft('dos', despues=tCu), 'sorpresa'); Z.pose_a('mq', ft('dos', despues=tCu), 'brazos', dur=0.2)

# ------------------------------------------------------------------ 8. "eso lo usarán mis nietos" — NO
tSolo = ft('Solo miremos')
dib('abu', D.abuelo, 300, 600, tOsea + 0.1, tSolo, dur=0.6)
dib('gl1', D.globo, 560, 470, ft('eso lo usarán'), tSolo, dur=0.35, w=470, h=230)
Z.frase('fnie', 'ESO LO USAR&Aacute;N<br>MIS NIETOS', ft('eso lo usarán') + 0.35, tSolo, x=560, y=505, fs=44, ancho=430)
Z.tachar('xnie', 345, 470, 430, 170, ft('nietos') + 0.25, tSolo)

# ------------------------------------------------------------------ 9. un niño de 8 años: pregúntale a ChatGPT
tPorq = ft('Porque creció')
Z.mono('kid', 270, 1060, alto=240, pose='parado', cara='feliz', t=tSolo + 0.1, t1=ft('teclados') - 0.1)
Z.frase('fadop', 'NIVEL DE <span style="color:#E5322D">ADOPCI&Oacute;N</span>', ft('adopción'), ft('pregúntale'), y=380, fs=66)
Z.rotulo('r8', '8 A&Ntilde;OS', ft('8'), 270, 1080, t1=tPorq, fs=32, fondo='#E5322D')
dib('gb1', D.globo, 430, 470, ft('pregúntale'), ft('pregúntale', despues=ft('Google')), dur=0.3, w=560, h=200, cola='abajo_izq')
Z.frase('fg', 'PREG&Uacute;NTALE A GOOGLE', ft('pregúntale') + 0.1, ft('pregúntale', despues=ft('Google')), x=430, y=518, fs=42, ancho=540)
Z.tachar('xg', 170, 470, 520, 150, ft('Google') + 0.3, ft('pregúntale', despues=ft('Google')))
t2p = ft('pregúntale', despues=ft('Google'))
dib('gb2', D.globo, 430, 700, t2p, tPorq + 0.4, dur=0.3, w=560, h=200)
Z.frase('fc', 'PREG&Uacute;NTALE A <span style="color:#E5322D">CHATGPT</span>', t2p + 0.1, tPorq + 0.4, x=430, y=748, fs=42, ancho=540)
Z.check('ok1', 730, 680, ft('ChatGPT', despues=t2p) + 0.25, tPorq + 0.4)
Z.cara('kid', ft('ChatGPT', despues=t2p), 'guino')

# ------------------------------------------------------------------ 10. creció con eso: para él es natural
tEsa = ft('Esa generación')
for k, (x, y) in enumerate(((470, 600), (600, 520), (730, 600), (560, 700), (690, 690))):
    Z.add(f'<div class="pzr" id="dq{k}" style="left:{x}px;top:{y}px;font-size:70px;color:#8E9099">?</div>')
    R.pin(f'#dq{k}', ft('dudas') + k * 0.08, sc=0.4, snd='pop' if k % 2 == 0 else None, g=0.08)
    T(f'#dq{k}', ft('ChatGPT', despues=ft('dudas')) - 0.1, 0.3, 'power2.in', x=640 - x, y=640 - y, opacity=0, scale=0.3)
dib('bot', D.globo, 470, 520, ft('ChatGPT', despues=ft('dudas')) + 0.15, tEsa, dur=0.3, w=380, h=210, color='#E5322D')
Z.frase('fbot', 'CHATGPT', ft('ChatGPT', despues=ft('dudas')) + 0.25, tEsa, x=470, y=565, fs=56, ancho=380, color='#E5322D')
Z.grande('gnat', 'NATURAL', ft('natural'), tEsa, y=360, fs=150)

# ------------------------------------------------------------------ 11. no van a entender los teclados (como los casetes)
tYsi = ft('Y si para los niños')
dib('tec', D.teclado, 540, 560, ft('teclados'), ft('muchacho'), dur=0.55)
Z.add('<div class="pzg" id="qt" style="top:440px;left:880px;font-size:150px;color:#E5322D"><span>?</span></div>')
R.pin('#qt', ft('teclados') + 0.4, sc=0.4, g=0.12); R.outo('#qt', ft('muchacho'))
Z.mono('teen', 250, 1060, alto=300, pose='duda', cara='serio', t=ft('muchacho'), t1=tYsi)
Z.rotulo('r14', '14 A&Ntilde;OS', ft('14'), 250, 1080, t1=tYsi, fs=32, fondo='#E5322D')
dib('cas', D.casete, 680, 520, ft('casetes'), ft('clientes') - 0.1, dur=0.45)
dib('wal', D.walkman, 680, 780, ft('Walkman') - 0.2, ft('clientes') - 0.1, dur=0.4, escala=0.8)
Z.add('<div class="pzg" id="qc" style="top:300px;left:250px;font-size:130px;color:#E5322D"><span>?</span></div>')
R.pin('#qc', ft('entiende') - 0.1, sc=0.4, g=0.12); R.outo('#qc', tYsi)

# ------------------------------------------------------------------ 12. tus clientes también: el negocio sin IA suena a casete
tPor = ft('Por eso')
Z.mono('n2', 220, 1060, alto=220, pose='parado', cara='feliz', t=tYsi, t1=ft('negocio', despues=tYsi))
for k, x in enumerate((470, 640, 810)):
    Z.mono(f'cl{k}', x, 1060, alto=300, pose='parado', cara='feliz', t=ft('clientes') + k * 0.12, t1=ft('negocio', despues=tYsi))
Z.rotulo('rcl', 'TUS CLIENTES', ft('clientes') + 0.3, 640, 620, t1=ft('negocio', despues=tYsi), fs=40, fondo='#E5322D')
tNeg = ft('negocio', despues=tYsi)
dib('tie', D.tienda, 540, 560, tNeg, ft('importancia'), dur=0.6)
Z.rotulo('rsin', 'SIN IA', tNeg + 0.4, 540, 588, t1=ft('importancia'), fs=34)
dib('cas2', D.casete, 540, 700, ft('casete', despues=tNeg) - 0.1, ft('importancia'), dur=0.4, escala=0.7)
dib('grt', D.grieta, 540, 560, ft('casete', despues=tNeg) + 0.1, ft('importancia'), dur=0.3)

# ------------------------------------------------------------------ 13. instalar agentes que reemplazan lo lento y caro: hoy mismo
tSera = ft('Será')
dib('pap', D.papeles, 300, 600, ft('trabajo'), tSera, dur=0.5)
Z.rotulo('rlc', 'LENTO Y CARO', ft('lento'), 300, 940, t1=tSera, fs=36, color=GR)
Z.tachar('xpap', 150, 600, 300, 320, ft('caro') + 0.2, tSera)
dib('rb1', D.robot, 720, 560, ft('agentes'), tSera, dur=0.55)
Z.rotulo('rag', 'AGENTES IA', ft('agentes') + 0.3, 720, 920, t1=tSera, fs=36, fondo='#E5322D')
Z.grande('ghoy', 'HOY MISMO', ft('hoy mismo'), tSera, y=360, fs=130)
Z.frase('fmod', 'no es moda', ft('moda') - 0.3, tSera, y=1010, fs=56, cursiva=True)

# ------------------------------------------------------------------ 14. separará a las que triunfen de las que quiebren
tCom = ft('Comenta')
dib('tro', D.trofeo, 290, 520, ft('triunfen'), tCom + 0.3, dur=0.5)
dib('fl1', D.flecha, 290, 850, ft('triunfen') + 0.3, tCom + 0.3, dur=0.3, arriba=True, color='#38D27A')
Z.rotulo('rtri', 'TRIUNFAN', ft('triunfen') + 0.2, 290, 990, t1=tCom + 0.3, fs=40, color='#38D27A')
dib('tie2', D.tienda, 780, 520, ft('de las que', despues=ft('triunfen')), tCom + 0.3, dur=0.45, escala=0.6)
dib('grt2', D.grieta, 780, 520, ft('quiebren'), tCom + 0.3, dur=0.25, escala=0.6)
dib('fl2', D.flecha, 780, 850, ft('quiebren'), tCom + 0.3, dur=0.3, arriba=False, color='#E5322D')
I('#fl2', rotation=90)
Z.rotulo('rqui', 'QUIEBRAN', ft('quiebren'), 780, 990, t1=tCom + 0.3, fs=40, color='#E5322D')
Z.frase('fsep', 'LA <span style="color:#E5322D">IA</span> SEPARA A LAS EMPRESAS', ft('separará'), tCom, y=360, fs=50)

# ------------------------------------------------------------------ 15. CTA: comenta ERA
Z.cta_comentario('ERA', tCom, ft('ERA'), ft('clase'), texto_burbuja='Te env&iacute;o la clase &#128233;')

Z.karaoke(desde=0.0, rojas=('Trece', '1913,', 'smartphone.', 'siete', 'seis', 'tres', 'dos.', 'nietos.', 'natural.', 'teclados',
                             'casetes', 'clientes', 'casete.', 'agentes', 'moda.', 'triunfen', 'quiebren.', 'ERA'))
Z.cerrar(musica='auto', volumen_musica=0.28, inicio_musica=24.0)
