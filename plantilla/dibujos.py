# -*- coding: utf-8 -*-
"""Dibujos a línea para el estilo pizarra (trazos blancos que se dibujan solos). Cada función devuelve (svg, w, h):
el cuerpo para Z.dibujo(idp, svg, x, y, w, h, t). Coordenadas locales en px.
Para uno nuevo: copia uno parecido y arma el trazo con Z.L(path) (línea), Z.F(path) (relleno) y Z.C(cx, cy, r)."""
import math
from pizarra import L, F, C, ROJO, BLANCO

GR = '#8E9099'


def caballo():
    w, h = 540, 380
    s = (L('M120,178 C140,132 330,130 362,172 C374,204 342,226 300,226 L162,226 C128,226 108,204 120,178 Z') +
         L('M344,166 L402,92') + L('M398,86 L452,96 L458,118 L412,122 L392,104') +
         L('M162,226 L150,330') + L('M192,226 L198,330') + L('M292,226 L280,330') + L('M322,220 L338,330') +
         L('M120,182 C88,196 84,236 96,268') +
         L(C(250, 64, 24)) + L('M250,88 L256,160') + L('M253,110 L334,142') + L('M256,160 L288,198 L278,240'))
    return s, w, h


def carro():
    w, h = 540, 260
    s = (L('M40,176 L58,126 L160,114 L212,62 L362,62 L424,114 L484,124 L494,176 Z') +
         L('M222,74 L282,74 L282,112 L196,112 Z') + L('M298,74 L352,74 L398,112 L298,112 Z') +
         L(C(142, 184, 38)) + L(C(402, 184, 38)) + F(C(142, 184, 12)) + F(C(402, 184, 12)) +
         L('M470,140 L494,142', 6, ROJO))
    return s, w, h


def celular(w=200, h=360):
    s = (L(f'M30,8 h{w - 60} a22,22 0 0 1 22,22 v{h - 60} a22,22 0 0 1 -22,22 h-{w - 60} a22,22 0 0 1 -22,-22 v-{h - 60} a22,22 0 0 1 22,-22 Z') +
         F(f'M28,44 h{w - 56} v{h - 104} h-{w - 56} Z', '#26272d') + L(C(w / 2, h - 30, 11), 4))
    return s, w, h


def grafica(curvas, w=900, h=560, ejes=True):
    """curvas = [(d, color, grosor)]; ejes con flecha."""
    s = (L(f'M70,30 L70,{h - 60} L{w - 30},{h - 60}', 5, GR) + L(f'M58,46 L70,30 L82,46', 5, GR) + L(f'M{w - 46},{h - 72} L{w - 30},{h - 60} L{w - 46},{h - 48}', 5, GR)) if ejes else ''
    for d, color, g in curvas: s += L(d, g, color)
    return s, w, h


def reloj_arena(w=220, h=320):
    s = (L(f'M30,14 L{w - 30},14') + L(f'M30,{h - 14} L{w - 30},{h - 14}') +
         L(f'M44,14 C44,110 {w / 2 - 8},{h / 2 - 12} {w / 2 - 8},{h / 2} C{w / 2 - 8},{h / 2 + 12} 44,{h - 110} 44,{h - 14}') +
         L(f'M{w - 44},14 C{w - 44},110 {w / 2 + 8},{h / 2 - 12} {w / 2 + 8},{h / 2} C{w / 2 + 8},{h / 2 + 12} {w - 44},{h - 110} {w - 44},{h - 14}') +
         F(f'M60,{h - 20} C70,{h - 70} {w / 2 - 6},{h - 96} {w / 2},{h - 100} C{w / 2 + 6},{h - 96} {w - 70},{h - 70} {w - 60},{h - 20} Z', ROJO, 0.9) +
         F(f'M{w / 2 - 2},{h / 2 + 2} L{w / 2 + 2},{h / 2 + 2} L{w / 2 + 2},{h - 100} L{w / 2 - 2},{h - 100} Z', ROJO, 0.9))
    return s, w, h


def abuelo():
    w, h = 300, 430
    s = (L(C(120, 70, 36)) + L('M128,106 C150,150 160,190 158,250') + L('M150,150 L214,206 L232,214') +
         L('M232,150 L232,420', 6) + L('M220,150 C226,132 242,132 246,146', 6) +
         L('M158,250 L128,330 L132,410') + L('M158,250 L186,330 L178,410') +
         L('M100,60 L112,64 M128,64 L140,60', 3) + L('M106,88 Q120,80 134,88', 3))
    return s, w, h


def globo(w, h, cola='abajo_izq', color=BLANCO):
    r = 28
    if cola == 'abajo_izq':
        d = f'M{r},4 H{w - r} Q{w - 4},4 {w - 4},{r} V{h - 60 - r} Q{w - 4},{h - 60} {w - r},{h - 60} H120 L70,{h - 6} L84,{h - 60} H{r} Q4,{h - 60} 4,{h - 60 - r} V{r} Q4,4 {r},4 Z'
    else:
        d = f'M{r},4 H{w - r} Q{w - 4},4 {w - 4},{r} V{h - 60 - r} Q{w - 4},{h - 60} {w - r},{h - 60} H{w - 84} L{w - 70},{h - 6} L{w - 120},{h - 60} H{r} Q4,{h - 60} 4,{h - 60 - r} V{r} Q4,4 {r},4 Z'
    return L(d, 5, color), w, h


def teclado():
    w, h = 560, 210
    s = L('M14,14 H546 Q554,14 554,22 V190 Q554,198 546,198 H14 Q6,198 6,190 V22 Q6,14 14,14 Z')
    for fila, (x0, n, y) in enumerate(((30, 12, 34), (46, 11, 76), (62, 10, 118))):
        for k in range(n):
            x = x0 + k * 42
            s += L(f'M{x},{y} h30 v30 h-30 Z', 3.5)
    s += L('M150,160 h260 v26 h-260 Z', 3.5)
    return s, w, h


def casete():
    w, h = 440, 280
    s = (L('M14,14 H426 Q434,14 434,22 V258 Q434,266 426,266 H14 Q6,266 6,258 V22 Q6,14 14,14 Z') +
         L('M40,40 H400 V150 H40 Z', 4) + L(C(140, 112, 30)) + L(C(300, 112, 30)) +
         L('M170,112 H270', 4) + L('M110,266 L130,214 H310 L330,266', 4) +
         F('M44,44 H396 V70 H44 Z', ROJO, 0.85))
    return s, w, h


def walkman():
    w, h = 320, 440
    s = (L('M60,120 H260 Q272,120 272,132 V420 Q272,432 260,432 H60 Q48,432 48,420 V132 Q48,120 60,120 Z') +
         L('M78,150 H242 V300 H78 Z', 4) + L(C(124, 226, 22), 4) + L(C(196, 226, 22), 4) +
         L('M80,330 h40 v24 h-40 Z M140,330 h40 v24 h-40 Z M200,330 h40 v24 h-40 Z', 3.5) +
         L('M64,122 C64,30 256,30 256,122', 6) + F('M40,92 h30 v52 h-30 Z', ROJO, 0.9) + F('M250,92 h30 v52 h-30 Z', ROJO, 0.9))
    return s, w, h


def tienda():
    w, h = 520, 440
    zz = 'M40,140 ' + ' '.join(f'L{60 + 40 * k},{170 if k % 2 == 0 else 140}' for k in range(11)) + ' L480,140'
    s = (L('M60,140 V420 H460 V140') + L('M40,140 L80,70 H440 L480,140 Z') + L(zz, 5) +
         L('M210,420 V280 H310 V420', 5) + L('M90,220 H180 V320 H90 Z', 5) + L('M340,220 H430 V320 H340 Z', 5) +
         L('M150,24 H370 V62 H150 Z', 5))
    return s, w, h


def grieta():
    w, h = 520, 440
    s = (L('M260,40 L238,120 L280,180 L230,260 L276,330 L250,430', 8, ROJO) + L('M280,180 L340,210', 6, ROJO) + L('M230,260 L170,290', 6, ROJO))
    return s, w, h


def robot(w=240, h=330):
    s = (L(f'M{w / 2},20 V52') + L(C(w / 2, 14, 10), 5) + L(f'M50,52 H{w - 50} Q{w - 38},52 {w - 38},64 V136 Q{w - 38},148 {w - 50},148 H50 Q38,148 38,136 V64 Q38,52 50,52 Z') +
         F(C(90, 98, 14), ROJO) + F(C(w - 90, 98, 14), ROJO) + L(f'M84,126 H{w - 84}', 4) +
         L(f'M60,168 H{w - 60} V{h - 40} H60 Z') + L(f'M60,190 L18,250', 7) + L(f'M{w - 60},190 L{w - 18},250', 7) +
         L(f'M92,{h - 40} V{h - 6} M{w - 92},{h - 40} V{h - 6}', 7))
    return s, w, h


def trofeo():
    w, h = 260, 300
    s = (L('M60,30 H200 V90 Q200,170 130,180 Q60,170 60,90 Z') + L('M60,50 Q16,50 20,92 Q24,126 66,128', 5) +
         L('M200,50 Q244,50 240,92 Q236,126 194,128', 5) + L('M130,180 V232', 6) + L('M80,276 H180 L170,232 H90 Z', 5) +
         F('M64,34 H196 V60 H64 Z', '#FFC53D', 0.9))
    return s, w, h


def papeles():
    w, h = 300, 320
    s = ''
    for k in range(5):
        y = 230 - k * 34; x = 40 + (k % 2) * 14
        s += L(f'M{x},{y} L{x + 200},{y - 10} L{x + 210},{y + 40} L{x + 10},{y + 50} Z', 4)
    s += L('M150,40 C170,20 200,24 214,40', 4, GR)
    return s, w, h


def calendario(numero='3'):
    w, h = 300, 300
    s = (L('M30,50 H270 V280 H30 Z') + F('M32,52 H268 V100 H32 Z', ROJO, 0.9) + L('M90,30 V70 M210,30 V70', 7))
    return s, w, h


def flecha(w=200, h=120, color=BLANCO, arriba=False):
    if arriba:
        return L(f'M{w / 2},{h - 6} V12 M{w / 2 - 40},52 L{w / 2},12 L{w / 2 + 40},52', 8, color), w, h
    return L(f'M10,{h / 2} H{w - 16} M{w - 56},{h / 2 - 36} L{w - 16},{h / 2} L{w - 56},{h / 2 + 36}', 8, color), w, h


# ===================================================================================================== iconos (lote 16-nov, Grok Bot / Jevons)
def chat(w=220, h=180, puntos=True, color=BLANCO):
    s = L(f'M30,10 H{w - 30} Q{w - 10},10 {w - 10},30 V{h - 70} Q{w - 10},{h - 50} {w - 30},{h - 50} H90 L50,{h - 8} L60,{h - 50} H30 Q10,{h - 50} 10,{h - 70} V30 Q10,10 30,10 Z', 6, color)
    if puntos:
        cy = (h - 50) / 2 + 6
        s += F(C(w / 2 - 50, cy, 11), color) + F(C(w / 2, cy, 11), color) + F(C(w / 2 + 50, cy, 11), color)
    return s, w, h


def pregunta(w=200, h=180, signo='?', color=BLANCO):
    s, w, h = chat(w, h, puntos=False, color=color)
    return s, w, h


def lupa(w=200, h=200):
    s = L(C(82, 82, 62), 8) + L('M128,128 L188,188', 14) + L('M50,70 Q60,46 84,40', 5, GR)
    return s, w, h


def diana(w=220, h=220):
    s = L(C(110, 110, 96), 6) + L(C(110, 110, 62), 6) + F(C(110, 110, 26), ROJO) + L('M110,110 L200,20', 7) + L('M176,18 L204,16 L202,44', 6)
    return s, w, h


def sobre(w=240, h=170):
    s = L(f'M14,14 H{w - 14} V{h - 14} H14 Z') + L(f'M14,16 L{w / 2},{h * .58} L{w - 14},16') + L(f'M14,{h - 16} L{w * .4},{h * .5} M{w - 14},{h - 16} L{w * .6},{h * .5}', 5)
    return s, w, h


def carrito(w=260, h=220):
    s = (L('M10,30 H54 L88,150 H214 L240,62 H70', 7) + L(C(104, 188, 18), 6) + L(C(198, 188, 18), 6) +
         L('M100,96 H226', 5, GR))
    return s, w, h


def camara(w=270, h=190):
    s = (L('M14,40 Q14,24 30,24 H170 Q186,24 186,40 V150 Q186,166 170,166 H30 Q14,166 14,150 Z') + L('M186,78 L256,40 V150 L186,112', 7) +
         F('M78,64 L132,95 L78,126 Z', ROJO))
    return s, w, h


def megafono(w=260, h=220):
    s = (L('M30,86 H74 L196,22 V198 L74,134 H30 Z') + L('M74,86 V134', 5) + L('M60,134 L80,196 H108 L96,134', 6) +
         L('M216,70 Q240,110 216,150', 6, ROJO) + L('M232,46 Q270,110 232,174', 6, ROJO))
    return s, w, h


def laptop(w=320, h=230, apagada=False):
    s = (L('M50,20 H270 Q282,20 282,32 V170 H38 V32 Q38,20 50,20 Z') + L('M8,182 H312 L296,208 H24 Z', 6) +
         F('M54,36 H266 V156 H54 Z', '#050506' if apagada else '#26272d'))
    if not apagada:
        s += L('M80,70 H200 M80,100 H236 M80,130 H170', 5, GR)
    return s, w, h


def nube(w=420, h=240, color=BLANCO, grosor=6):
    d = (f'M90,{h - 30} Q20,{h - 30} 24,{h - 92} Q30,{h - 150} 96,{h - 146} Q110,{h - 222} 196,{h - 214} Q262,{h - 210} 280,{h - 150} '
         f'Q330,{h - 196} 372,{h - 150} Q410,{h - 110} 384,{h - 70} Q410,{h - 30} 340,{h - 30} Z')
    return L(d, grosor, color), w, h


def corazon(w=140, h=124):
    d = 'M70,118 C30,90 6,64 6,38 C6,18 22,6 40,6 C54,6 64,14 70,26 C76,14 86,6 100,6 C118,6 134,18 134,38 C134,64 110,90 70,118 Z'
    return L(d, 6, ROJO) + F(d, ROJO, 0.9), w, h


def avion(w=230, h=190):
    s = L('M14,92 L214,14 L176,176 L112,128 Z') + L('M112,128 L214,14', 5) + L('M112,128 L104,176 L136,142', 5)
    return s, w, h


def ojo(w=240, h=150):
    s = L(f'M14,{h / 2} Q{w / 2},-10 {w - 14},{h / 2} Q{w / 2},{h + 10} 14,{h / 2} Z') + L(C(w / 2, h / 2, 34), 6) + F(C(w / 2, h / 2, 16), ROJO)
    return s, w, h


def documento(w=180, h=230):
    s = (L(f'M20,12 H{w - 52} L{w - 16},48 V{h - 12} H20 Z') + L(f'M{w - 52},12 V48 H{w - 16}', 5) +
         L(f'M46,90 H{w - 46} M46,122 H{w - 46} M46,154 H{w - 70} M46,186 H{w - 60}', 5, GR))
    return s, w, h


def telefono(w=200, h=200):
    d = 'M52,22 L82,22 L96,64 L74,82 Q92,122 118,140 L136,118 L178,132 L178,162 Q178,182 158,182 Q78,176 24,104 Q16,86 18,62 Q20,22 52,22 Z'
    return L(d, 7), w, h


def engrane(w=200, h=200, dientes=8, color=BLANCO):
    cx, cy, r1, r2 = w / 2, h / 2, w * .30, w * .42
    pts = []
    for k in range(dientes * 2):
        a0 = math.pi * 2 * k / (dientes * 2); a1 = math.pi * 2 * (k + 1) / (dientes * 2)
        r = r2 if k % 2 == 0 else r1
        pts.append(f'{cx + r * math.cos(a0):.1f},{cy + r * math.sin(a0):.1f} {cx + r * math.cos(a1):.1f},{cy + r * math.sin(a1):.1f}')
    d = 'M' + ' L'.join(pts) + ' Z'
    return L(d, 6, color) + L(C(cx, cy, w * .12), 6, color), w, h


def etiqueta_precio(w=230, h=150):
    s = L('M60,14 H214 V136 H60 L14,75 Z') + L(C(56, 75, 10), 5) + L('M96,56 H184 M96,94 H160', 6, GR)
    return s, w, h


def plastilina(w=200, h=230):
    """muñequito de plastilina (cuerpo redondo, ojos grandes)."""
    s = (L('M100,30 C150,30 170,80 166,130 C162,190 138,214 100,214 C62,214 38,190 34,130 C30,80 50,30 100,30 Z') +
         F(C(78, 102, 15), BLANCO) + F(C(124, 102, 15), BLANCO) + F(C(80, 104, 6), '#111113') + F(C(122, 104, 6), '#111113') +
         L('M82,150 Q100,166 120,150', 5) + F('M58,60 C66,40 92,34 104,36 C90,46 74,52 58,60 Z', ROJO, 0.9))
    return s, w, h


def escudo(w=200, h=230):
    d = 'M100,14 L184,44 V110 Q184,176 100,216 Q16,176 16,110 V44 Z'
    return L(d, 7) + L('M60,116 L90,146 L144,88', 10, '#38D27A'), w, h


def enlace(x1, y1, x2, y2, w=1080, h=1100, color=GR):
    """línea suelta entre dos puntos (para conectar dibujos)."""
    return L(f'M{x1},{y1} L{x2},{y2}', 5, color), w, h


def humano(w=90, h=200, color=BLANCO):
    """persona mínima (cabeza + cuerpo) para filas de 'humanos'."""
    s = L(C(w / 2, 30, 22), 5, color) + L(f'M{w / 2},54 V130 M{w / 2},74 L{w / 2 - 30},112 M{w / 2},74 L{w / 2 + 30},112 M{w / 2},130 L{w / 2 - 22},192 M{w / 2},130 L{w / 2 + 22},192', 5, color)
    return s, w, h


def flecha_abajo(w=120, h=200, color=ROJO):
    return L(f'M{w / 2},10 V{h - 16} M{w / 2 - 40},{h - 56} L{w / 2},{h - 16} L{w / 2 + 40},{h - 56}', 9, color), w, h


def rayo(w=120, h=200, color=ROJO):
    d = f'M70,8 L18,112 H62 L44,192 L104,80 H60 Z'
    return L(d, 6, color) + F(d, color, 0.9), w, h


# ===================================================================================================== iconos (Trabajar menos / Jevons)
def reloj(w=220, h=220, hora=10.92, color=BLANCO):
    """reloj de pared; hora en decimal (10.92 = 10:55)."""
    cx, cy, r = w / 2, h / 2, w * .44
    s = L(C(cx, cy, r), 7, color)
    for k in range(12):
        a = math.pi * 2 * k / 12
        s += L(f'M{cx + math.sin(a) * r * .80:.1f},{cy - math.cos(a) * r * .80:.1f} L{cx + math.sin(a) * r * .92:.1f},{cy - math.cos(a) * r * .92:.1f}', 4, GR)
    hh = (hora % 12) / 12 * math.pi * 2; mm = (hora % 1) * math.pi * 2
    s += L(f'M{cx},{cy} L{cx + math.sin(hh) * r * .5:.1f},{cy - math.cos(hh) * r * .5:.1f}', 8, color)
    s += L(f'M{cx},{cy} L{cx + math.sin(mm) * r * .74:.1f},{cy - math.cos(mm) * r * .74:.1f}', 5, ROJO)
    return s, w, h


def maquina_vapor(w=520, h=330):
    """locomotora de vapor de 1800s."""
    s = (L('M70,120 H330 Q360,120 360,150 V230 H70 Z') + L('M330,120 V230', 5) + L('M360,70 H470 V230 H360', 6) + L('M384,96 H446 V150 H384 Z', 5) +
         L('M110,120 V64 H150 V120', 6) + L('M96,64 H164', 7) + L('M40,230 H500', 6) +
         L(C(130, 268, 38), 6) + L(C(240, 268, 38), 6) + L(C(420, 278, 28), 6) + L('M130,268 L240,268', 5, GR) +
         L('M40,230 L20,262 H60', 6) + F(C(130, 268, 10), BLANCO) + F(C(240, 268, 10), BLANCO))
    return s, w, h


def humo(w=260, h=160, color=GR):
    return (L('M30,140 Q10,110 40,96 Q40,60 80,64 Q100,34 136,52 Q170,30 196,62 Q236,62 230,100 Q250,126 220,140', 6, color)), w, h


def carbon(w=300, h=150):
    s = (F('M20,140 L60,90 L100,104 L130,60 L176,86 L210,64 L250,100 L284,140 Z', '#2a2b31') +
         L('M20,140 L60,90 L100,104 L130,60 L176,86 L210,64 L250,100 L284,140 Z', 5) + L('M60,90 L84,140 M130,60 L150,140 M210,64 L196,140', 4, GR))
    return s, w, h


def mancuerna(w=320, h=140):
    s = (L('M70,70 H250', 9) + L('M40,30 H70 V110 H40 Z', 7) + L('M250,30 H280 V110 H250 Z', 7) + L('M14,46 H40 V94 H14 Z', 6) + L('M280,46 H306 V94 H280 Z', 6))
    return s, w, h


def cartel(w=520, h=360):
    s = L(f'M20,20 H{w - 20} V{h - 120} H20 Z', 7) + L(f'M{w / 2 - 80},{h - 120} V{h - 10} M{w / 2 + 80},{h - 120} V{h - 10}', 7)
    return s, w, h


def revista(w=300, h=380):
    s = (L(f'M20,14 H{w - 20} V{h - 14} H20 Z') + F(f'M24,18 H{w - 24} V78 H24 Z', ROJO, 0.9) +
         L(f'M48,120 H{w - 48} M48,156 H{w - 48} M48,192 H{w - 90}', 7) + L(f'M48,250 H{w - 48} M48,282 H{w - 48} M48,314 H{w - 110}', 4, GR))
    return s, w, h


def edificio(w=300, h=380):
    s = L(f'M40,40 H{w - 40} V{h - 10} H40 Z')
    for fila in range(5):
        for col in range(3):
            x = 72 + col * 62; y = 70 + fila * 56
            s += L(f'M{x},{y} h34 v30 h-34 Z', 4, GR)
    s += L(f'M{w / 2 - 26},{h - 10} V{h - 70} H{w / 2 + 26} V{h - 10}', 5)
    return s, w, h


def plato(w=280, h=170):
    s = L('M60,90 a80,48 0 1,0 160,0 a80,48 0 1,0 -160,0', 6) + L('M96,90 a44,24 0 1,0 88,0 a44,24 0 1,0 -88,0', 4, GR) + L('M24,30 V150 M14,30 V70 M34,30 V70', 5) + L('M256,30 Q270,80 256,104 V150', 5)
    return s, w, h


def mesa(w=340, h=200):
    s = L('M40,80 H300 L320,120 H20 Z', 6) + L('M50,120 V190 M290,120 V190', 6) + L(C(90, 40, 22), 5) + L(C(170, 30, 22), 5) + L(C(250, 40, 22), 5)
    return s, w, h


def puerta(w=200, h=320):
    s = L(f'M30,20 H170 V{h - 10} H30 Z', 7) + L(f'M30,20 L120,48 V{h - 30} L30,{h - 10}', 6) + F(C(104, 170, 7), BLANCO)
    return s, w, h
