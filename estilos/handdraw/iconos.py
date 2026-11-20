# -*- coding: utf-8 -*-
"""reel-motion · íconos del estilo HANDDRAW (estilo de handdraw-skill: línea gruesa de UN color por ícono, puntas redondas, sobre papel crema).

- Reutiliza los dibujos del estilo pizarra (plantilla/dibujos.py) y suma íconos nuevos.
- hd(cuerpo, w, h, color) convierte un dibujo en un SVG listo para HandDraw:
    * recolorea (blanco -> color del ícono, gris -> versión clara, rojo -> acento),
    * pathLength=1000 en cada trazo (la animación `draw` de HandDraw usa stroke-dasharray 1000),
    * ORDEN DE TRAZO: cada trazo se dibuja en su turno (contorno primero, detalles después) usando la variable
      --draw-progress que HandDraw ya pone en cada dibujo. No se toca el motor de HandDraw.
    * los rellenos aparecen al final del trazo (no de golpe al inicio).
"""
import math
import re

from pizarra import L, F, C, ROJO, BLANCO
import dibujos as D

PAL = dict(azul='#2563EB', morado='#7C3AED', naranja='#EA580C', verde='#16A34A', rosa='#DB2777', teal='#0F766E',
           rojo='#E5322D', gris='#64748B', tinta='#172033', ambar='#D97706', cafe='#92400E', cielo='#0284C7')
CLARO = dict(azul='#93C5FD', morado='#C4B5FD', naranja='#FDBA74', verde='#86EFAC', rosa='#F9A8D4', teal='#5EEAD4',
             rojo='#FCA5A5', gris='#CBD5E1', tinta='#94A3B8', ambar='#FCD34D', cafe='#D6B48A', cielo='#7DD3FC')
TINTE = dict(azul='#DBEAFE', morado='#EDE9FE', naranja='#FFEDD5', verde='#DCFCE7', rosa='#FCE7F3', teal='#CCFBF1',
             rojo='#FEE2E2', gris='#E2E8F0', tinta='#E2E8F0', ambar='#FEF3C7', cafe='#F5E6D3', cielo='#E0F2FE')
AMARILLO_MARCADOR = '#FDE047'


# ===================================================================================================== largo de un trazo
_TOK = re.compile(r'[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?')


def _arco(x1, y1, rx, ry, fi, fa, fs, x2, y2):
    """largo aproximado de un arco SVG (conversión a centro, SVG 1.1 F.6.5)."""
    if rx == 0 or ry == 0: return math.hypot(x2 - x1, y2 - y1)
    rx, ry = abs(rx), abs(ry); p = math.radians(fi)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p = math.cos(p) * dx + math.sin(p) * dy; y1p = -math.sin(p) * dx + math.cos(p) * dy
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1: rx *= math.sqrt(lam); ry *= math.sqrt(lam)
    num = rx ** 2 * ry ** 2 - rx ** 2 * y1p ** 2 - ry ** 2 * x1p ** 2; den = rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2
    co = math.sqrt(max(0, num / den)) if den else 0
    if fa == fs: co = -co
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    def ang(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy); return a
    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dt > 0: dt -= 2 * math.pi
    elif fs and dt < 0: dt += 2 * math.pi
    return abs(dt) * (rx + ry) / 2


def largo(d):
    toks = _TOK.findall(d); i = 0; x = y = sx = sy = 0.0; cmd = None; tot = 0.0; lc = None
    def num():
        nonlocal i
        v = float(toks[i]); i += 1; return v
    while i < len(toks):
        if re.match(r'[A-Za-z]', toks[i]): cmd = toks[i]; i += 1
        if cmd in 'Zz':
            tot += math.hypot(sx - x, sy - y); x, y = sx, sy; lc = None
            if i < len(toks) and not re.match(r'[A-Za-z]', toks[i]): cmd = 'L'
            continue
        rel = cmd.islower(); c = cmd.upper()
        try:
            if c == 'M':
                nx, ny = num(), num()
                if rel: nx += x; ny += y
                x, y, sx, sy = nx, ny, nx, ny; cmd = 'l' if rel else 'L'; lc = None
            elif c == 'L':
                nx, ny = num(), num()
                if rel: nx += x; ny += y
                tot += math.hypot(nx - x, ny - y); x, y = nx, ny; lc = None
            elif c == 'H':
                nx = num() + (x if rel else 0); tot += abs(nx - x); x = nx; lc = None
            elif c == 'V':
                ny = num() + (y if rel else 0); tot += abs(ny - y); y = ny; lc = None
            elif c in 'CSQT':
                if c == 'C': pts = [num(), num(), num(), num(), num(), num()]
                elif c == 'S': pts = [num(), num(), num(), num()]
                elif c == 'Q': pts = [num(), num(), num(), num()]
                else: pts = [num(), num()]
                if rel: pts = [v + (x if k % 2 == 0 else y) for k, v in enumerate(pts)]
                if c == 'S':
                    c1 = (2 * x - lc[0], 2 * y - lc[1]) if lc else (x, y); P = [(x, y), c1, (pts[0], pts[1]), (pts[2], pts[3])]
                elif c == 'T':
                    q = (2 * x - lc[0], 2 * y - lc[1]) if lc else (x, y); P = [(x, y), q, (pts[0], pts[1])]
                elif c == 'C': P = [(x, y), (pts[0], pts[1]), (pts[2], pts[3]), (pts[4], pts[5])]
                else: P = [(x, y), (pts[0], pts[1]), (pts[2], pts[3])]
                prev = P[0]
                for k in range(1, 17):
                    t = k / 16
                    if len(P) == 4:
                        px = (1 - t) ** 3 * P[0][0] + 3 * (1 - t) ** 2 * t * P[1][0] + 3 * (1 - t) * t ** 2 * P[2][0] + t ** 3 * P[3][0]
                        py = (1 - t) ** 3 * P[0][1] + 3 * (1 - t) ** 2 * t * P[1][1] + 3 * (1 - t) * t ** 2 * P[2][1] + t ** 3 * P[3][1]
                    else:
                        px = (1 - t) ** 2 * P[0][0] + 2 * (1 - t) * t * P[1][0] + t ** 2 * P[2][0]
                        py = (1 - t) ** 2 * P[0][1] + 2 * (1 - t) * t * P[1][1] + t ** 2 * P[2][1]
                    tot += math.hypot(px - prev[0], py - prev[1]); prev = (px, py)
                lc = P[-2]; x, y = P[-1]
            elif c == 'A':
                rx, ry, fi, fa, fs, nx, ny = num(), num(), num(), num(), num(), num(), num()
                if rel: nx += x; ny += y
                tot += _arco(x, y, rx, ry, fi, int(fa), int(fs), nx, ny); x, y = nx, ny; lc = None
            else:
                i += 1
        except (IndexError, ValueError):
            break
    return max(tot, 1.0)


# ===================================================================================================== conversión a SVG de HandDraw
_EL = re.compile(r'<path class="(ln|rel)" ([^>]*?)/>')


def _attr(s, k):
    m = re.search(rf'\b{k}="([^"]*)"', s); return m.group(1) if m else None


def hd(cuerpo, w, h, color='azul', acento='rojo', grosor=1.6, secuencial=True, final=0.9):
    """(svg, w, h) listo para assets/ de HandDraw. `color` = nombre de PAL o '#hex'."""
    c1 = PAL.get(color, color); c2 = PAL.get(acento, acento)
    cl = CLARO.get(color, '#CBD5E1'); ti = TINTE.get(color, '#E2E8F0')
    mapa = {'#F4F4F2': c1, BLANCO: c1, '#8E9099': cl, '#4C4D54': cl, ROJO: c2, '#E5322D': c2, '#38D27A': PAL['verde'],
            '#FFC53D': '#F59E0B', '#26272d': ti, '#26272D': ti, '#050506': '#CBD5E1', '#111113': c1, '#D8D8D8': cl}
    els = _EL.findall(cuerpo)
    trazos = [(k, a) for k, a in els if k == 'ln']
    largos = [largo(_attr(a, 'd') or '') * float(_attr(a, 'data-esc') or 1) for k, a in trazos]
    tot = sum(largos) or 1.0
    # ventana de cada trazo: proporcional a su largo (mínimo 5 %), en orden, con un poco de solape
    cuotas = [max(l / tot, 0.05) for l in largos]; sc = sum(cuotas) or 1.0
    cuotas = [q / sc * final for q in cuotas]
    estado = dict(acc=0.0, j=0)

    def conv(m):                       # reemplaza cada trazo/relleno en su lugar (se conservan los <g transform> de los grupos)
        k, a = m.group(1), m.group(2)
        st = _attr(a, 'stroke'); fi = _attr(a, 'fill'); sw = _attr(a, 'stroke-width'); op = _attr(a, 'opacity')
        d = _attr(a, 'd')
        if k == 'ln':
            q = cuotas[estado['j']]; estado['j'] += 1
            a0 = estado['acc'] if secuencial else 0.0; ww = (q * 1.18) if secuencial else final
            estado['acc'] += q
            col = mapa.get(st, st) if st else c1
            extra = ''
            so = _attr(a, 'stroke-opacity')
            if so: extra += f' stroke-opacity="{so}"'
            # el trazo queda invisible (opacidad 0) hasta que empieza su turno: si no, la punta redonda asoma como un puntito
            estilo = (f'stroke-dashoffset:calc(1000 * (1 - clamp(0, (var(--draw-progress) - {a0:.4f}) / {max(ww, 0.02):.4f}, 1)));'
                      f'opacity:clamp(0, calc((var(--draw-progress) - {a0:.4f}) * 300), 1)')
            g = float(sw or 6) * (grosor if col != AMARILLO_MARCADOR else 1.0)
            return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{g:.1f}" stroke-linecap="round" '
                    f'stroke-linejoin="round" pathLength="1000"{extra} style="{estilo}"/>')
        col = mapa.get(fi, fi) if fi else c1
        o = float(op or 1)
        # el relleno aparece cuando ya se trazó lo que lo rodea (según su lugar en el orden)
        t_rel = min(final - 0.08, max(0.0, estado['acc'] - 0.02)) if secuencial else final - 0.08
        return (f'<path d="{d}" fill="{col}" stroke="none" '
                f'style="opacity:calc({o:.2f} * clamp(0, (var(--draw-progress) - {t_rel:.3f}) / 0.14, 1))"/>')
    cuerpo2 = _EL.sub(conv, cuerpo)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" fill="none">' + cuerpo2 + '</svg>')
    return svg, w, h


def grupo(items, w, h):
    """varios íconos en un solo dibujo (se trazan uno tras otro). items = [(icono, cx, cy, escala), ...]."""
    s = ''
    for (body, iw, ih), cx, cy, e in items:
        body = body.replace('<path class="ln" ', f'<path class="ln" data-esc="{e}" ')
        s += f'<g transform="translate({cx - iw * e / 2:.1f},{cy - ih * e / 2:.1f}) scale({e})">{body}</g>'
    return s, w, h


# ===================================================================================================== íconos nuevos
def caracol():
    w, h = 320, 210
    s = (L('M206,160 C222,96 182,40 130,42 C76,44 50,96 72,134 C94,170 152,168 166,130 C178,96 142,76 120,92 C100,106 112,136 136,128') +
         L('M20,182 Q36,164 66,172 L238,172 Q284,172 288,132 Q290,100 266,96 Q244,94 242,120 L238,158') +
         L('M266,98 L280,58 M250,98 L244,58', 5) + L(C(281, 52, 7), 5) + L(C(243, 52, 7), 5))
    return s, w, h


def persona(w=240, h=260, celular=False):
    s = L(C(120, 70, 40), 8) + L('M44,236 C51,176 84,148 120,148 C156,148 189,176 196,236', 8)
    if celular:
        s += L('M150,170 h40 v62 h-40 Z', 6, ROJO) + L('M160,220 h20', 4, ROJO)
    return s, w, h


def mono_salta(w=200, h=220):
    s = (L(C(100, 36, 24)) + L('M100,60 L100,128') + L('M100,78 L62,40 M100,78 L138,40') +
         L('M100,128 L68,150 L82,190 M100,128 L134,152 L124,192') + F(C(84, 30, 4.5)) + F(C(116, 30, 4.5)) + L('M90,44 Q100,52 110,44', 4))
    return s, w, h


def mono_piensa(w=200, h=260):
    s = (L(C(100, 40, 28)) + L('M100,68 V160') + L('M100,92 L136,118 L118,70') + L('M100,92 L70,140') +
         L('M100,160 L78,246 M100,160 L122,246') + F(C(90, 36, 4.5)) + F(C(112, 36, 4.5)) + L('M90,54 H112', 4))
    return s, w, h


def nino(w=150, h=200):
    s = (L(C(75, 42, 28)) + L('M75,70 V130') + L('M75,86 L46,116 M75,86 L104,116') + L('M75,130 L56,190 M75,130 L94,190') +
         F(C(64, 38, 4.5)) + F(C(86, 38, 4.5)) + L('M64,54 Q75,62 86,54', 4) + L('M52,22 Q75,4 98,22', 5))
    return s, w, h


def muchacho(w=170, h=260):
    s = (L(C(85, 50, 28)) + L('M56,40 Q85,8 114,40 L140,46', 6) + L('M85,78 V160') + L('M85,96 L56,140 M85,96 L114,140') +
         L('M85,160 L64,246 M85,160 L106,246') + F(C(74, 50, 4.5)) + F(C(96, 50, 4.5)) + L('M76,66 H94', 4))
    return s, w, h


def pregunta_signo(w=150, h=170):
    s = L('M40,54 C40,22 70,10 92,16 C120,24 124,56 104,72 C88,84 78,92 78,116', 12) + F(C(78, 148, 9), BLANCO)
    return s, w, h


def tachar(w=200, h=200, g=12):
    return L(f'M12,12 L{w - 12},{h - 12}', g, ROJO) + L(f'M{w - 12},12 L12,{h - 12}', g, ROJO), w, h


def check(w=120, h=100, g=14):
    return L('M14,54 L44,84 L106,16', g, '#38D27A'), w, h


def circulo_marca(w=300, h=180, g=8):
    d = (f'M{w * .86:.0f},{h * .2:.0f} C{w * .62:.0f},{h * .02:.0f} {w * .12:.0f},{h * .06:.0f} {w * .05:.0f},{h * .46:.0f} '
         f'C{w * .0:.0f},{h * .86:.0f} {w * .5:.0f},{h * .99:.0f} {w * .86:.0f},{h * .86:.0f} C{w * 1.0:.0f},{h * .76:.0f} {w * .99:.0f},{h * .32:.0f} {w * .7:.0f},{h * .12:.0f}')
    return L(d, g, ROJO), w, h


def subrayado(w=400, h=50, g=10):
    return L(f'M12,{h * .62:.0f} C{w * .3:.0f},{h * .3:.0f} {w * .7:.0f},{h * .42:.0f} {w - 12},{h * .28:.0f}', g, ROJO), w, h


def resaltador(w=500, h=90):
    return L(f'M{h * .3:.0f},{h * .55:.0f} L{w - h * .3:.0f},{h * .45:.0f}', h * .78, AMARILLO_MARCADOR, ' stroke-opacity="0.75"'), w, h


def linea_tiempo(w=820, h=80):
    s = L(f'M20,40 H{w - 20}', 7) + L('M20,18 V62', 7) + L(f'M{w - 20},18 V62', 7, ROJO) + L(f'M{w / 2:.0f},28 V52', 5)
    return s, w, h


def flecha_curva(w=320, h=170, color=BLANCO):
    s = (L(f'M16,{h - 22} C{w * .28:.0f},{-h * .18:.0f} {w * .7:.0f},{-h * .12:.0f} {w - 34},{h - 40}', 8, color) +
         L(f'M{w - 78},{h - 58} L{w - 34},{h - 40} L{w - 30},{h - 88}', 8, color))
    return s, w, h


def medidor(w=320, h=200):
    s = L('M40,176 A120,120 0 0 1 280,176', 9)
    for k in range(7):
        a = math.pi * (1 - k / 6)
        x1, y1 = 160 + math.cos(a) * 100, 176 - math.sin(a) * 100; x2, y2 = 160 + math.cos(a) * 84, 176 - math.sin(a) * 84
        s += L(f'M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}', 5, ROJO if k >= 5 else '#8E9099')
    return s, w, h


def aguja(w=240, h=240):
    return L('M120,120 L34,120', 9, ROJO) + L(C(120, 120, 12), 7), w, h


def barra_busqueda(w=560, h=120):
    s = L(f'M60,14 H{w - 60} C{w - 22},14 {w - 8},40 {w - 8},60 C{w - 8},82 {w - 22},106 {w - 60},106 H60 C22,106 8,82 8,60 C8,40 22,14 60,14 Z', 7)
    s += L(C(62, 58, 18), 6) + L('M76,72 L92,88', 7)
    return s, w, h


def ventana_chat(w=440, h=330):
    s = (L(f'M30,14 H{w - 30} Q{w - 14},14 {w - 14},30 V{h - 30} Q{w - 14},{h - 14} {w - 30},{h - 14} H30 Q14,{h - 14} 14,{h - 30} V30 Q14,14 30,14 Z', 7) +
         L(f'M14,66 H{w - 14}', 5) + L(C(44, 40, 8), 4) + L(C(70, 40, 8), 4) +
         L(f'M{w - 190},96 H{w - 44} Q{w - 36},96 {w - 36},104 V132 Q{w - 36},140 {w - 44},140 H{w - 190} Q{w - 198},140 {w - 198},132 V104 Q{w - 198},96 {w - 190},96 Z', 5, '#8E9099') +
         L(f'M52,166 H{w - 120} Q{w - 112},166 {w - 112},174 V258 Q{w - 112},266 {w - 120},266 H52 Q44,266 44,258 V174 Q44,166 52,166 Z', 5, ROJO) +
         L(f'M68,196 H{w - 150} M68,222 H{w - 170} M68,246 H{w - 210}', 4, ROJO))
    return s, w, h


def destello(w=100, h=100):
    d = f'M{w / 2},4 Q{w * .56:.0f},{h * .44:.0f} {w - 4},{h / 2} Q{w * .56:.0f},{h * .56:.0f} {w / 2},{h - 4} Q{w * .44:.0f},{h * .56:.0f} 4,{h / 2} Q{w * .44:.0f},{h * .44:.0f} {w / 2},4 Z'
    return L(d, 6, ROJO) + F(d, ROJO, 0.9), w, h


def comentario(w=900, h=150):
    s = (L(f'M80,20 H{w - 80} C{w - 34},20 {w - 10},46 {w - 10},75 C{w - 10},104 {w - 34},130 {w - 80},130 H80 C34,130 10,104 10,75 C10,46 34,20 80,20 Z', 7) +
         L(C(82, 75, 32), 5, '#8E9099') + L(C(82, 64, 10), 4, '#8E9099') + L('M62,98 C66,84 98,84 102,98', 4, '#8E9099'))
    return s, w, h


def clase(w=320, h=240):
    s = (L('M20,20 H300 V180 H20 Z', 7) + L('M120,206 H200 M160,180 V206', 6) +
         L('M136,70 L196,100 L136,130 Z', 6, ROJO) + F('M136,70 L196,100 L136,130 Z', ROJO, 0.9))
    return s, w, h


def moneda(w=180, h=180):
    cx, cy = w / 2, h / 2
    s = (L(C(cx, cy, 76), 8) +
         L(f'M{cx + 22},{cy - 26} C{cx + 10},{cy - 40} {cx - 32},{cy - 38} {cx - 32},{cy - 14} C{cx - 32},{cy + 8} {cx + 32},{cy - 4} {cx + 32},{cy + 20} '
           f'C{cx + 32},{cy + 44} {cx - 12},{cy + 44} {cx - 28},{cy + 30}', 8, ROJO) + L(f'M{cx},{cy - 52} V{cy + 54}', 7, ROJO))
    return s, w, h


def iphone(w=200, h=360):
    s, w, h = D.celular(w, h)
    return s, w, h


def personas_celular():
    return persona(celular=True)


def tienda(w=520, h=440):
    return D.tienda()


def nietos_globo(w=470, h=230):
    return D.globo(w, h)


def mundo(w=200, h=200):
    s = (L(C(100, 100, 84), 7) + L('M16,100 H184', 5) + L('M100,16 C56,50 56,150 100,184 C144,150 144,50 100,16', 5) +
         L('M32,58 Q100,76 168,58', 4) + L('M32,142 Q100,124 168,142', 4))
    return s, w, h


def linea_vertical(w=24, h=600):
    return L(f'M12,12 V{h - 12}', 7), w, h


def curva(d, w, h, g=9):
    """una curva suelta (para gráficas: va en el mismo marco que los ejes)."""
    return L(d, g), w, h


# ===================================================================================================== íconos Grok Bot
def luna(w=160, h=160):
    return L('M110,18 C58,26 28,70 34,110 C42,150 96,170 138,140 C96,144 64,112 68,74 C70,46 88,26 110,18 Z', 7), w, h


def corona(w=300, h=230):
    s = (L('M34,186 L22,64 L92,126 L150,34 L208,126 L278,64 L266,186 Z', 8) + L('M30,212 H270', 8) +
         F(C(22, 58, 13), ROJO) + F(C(150, 28, 13), ROJO) + F(C(278, 58, 13), ROJO))
    return s, w, h


def reclamo(w=220, h=180):
    s, w, h = D.chat(w, h, puntos=False)
    s += (L('M66,52 C66,34 82,28 96,30 C112,34 114,52 102,62 C94,68 90,72 90,84', 8, ROJO) + F(C(90, 104, 7), ROJO) +
          L('M148,34 V82', 9, ROJO) + F(C(148, 104, 7), ROJO))
    return s, w, h


def perfiles(w=440, h=200):
    s = ''
    for x0 in (10, 160, 310):
        s += (L(f'M{x0 + 14},10 H{x0 + 106} Q{x0 + 120},10 {x0 + 120},24 V176 Q{x0 + 120},190 {x0 + 106},190 H{x0 + 14} Q{x0},190 {x0},176 V24 Q{x0},10 {x0 + 14},10 Z', 6) +
              L(C(x0 + 60, 70, 26), 6) + L(f'M{x0 + 24},130 H{x0 + 96} M{x0 + 34},156 H{x0 + 86}', 5, '#8E9099'))
    return s, w, h


def responder(w=220, h=170):
    return L('M82,26 L22,78 L82,130', 9) + L('M26,78 H128 C182,78 204,110 204,156', 9), w, h


def burbujas_dm(w=320, h=280):
    s = (L('M130,20 H286 Q300,20 300,34 V78 Q300,92 286,92 H130 Q116,92 116,78 V34 Q116,20 130,20 Z', 6, '#8E9099') +
         L('M140,56 H272', 5, '#8E9099') +
         L('M34,120 H220 Q234,120 234,134 V194 Q234,208 220,208 H34 Q20,208 20,194 V134 Q20,120 34,120 Z', 6, ROJO) +
         L('M42,150 H210 M42,178 H170', 5, ROJO) +
         L('M130,226 H286 Q300,226 300,240 V256 Q300,270 286,270 H130 Q116,270 116,256 V240 Q116,226 130,226 Z', 6, '#8E9099'))
    return s, w, h


def fila(icono, n, paso, esc=1.0):
    body, iw, ih = icono
    w = round(paso * (n - 1) + iw * esc); h = round(ih * esc)
    return grupo([(icono, iw * esc / 2 + k * paso, h / 2, esc) for k in range(n)], w, h)


def dos_personas(w=640, h=270):
    s, _, _ = grupo([(persona(), 130, 140, 0.95), (persona(), 510, 140, 0.95)], w, h)
    s += L('M262,120 H378 M350,100 L378,120 L350,140 M290,100 L262,120 L290,140', 6, ROJO)
    return s, w, h


def sobres(w=300, h=230):
    return grupo([(D.sobre(), 110, 90, 0.8), (D.sobre(), 190, 140, 0.8)], w, h)


def raya(w=760, h=50, g=10):
    return L(f'M12,{h / 2 + 2:.0f} L{w - 12},{h / 2 - 2:.0f}', g, ROJO), w, h


def conexiones():
    """las 3 líneas entre los robots del triángulo (marco 900x700, igual que robots_triangulo)."""
    return L('M392,258 L218,418', 6) + L('M508,258 L682,418', 6) + L('M246,560 H654', 6), 900, 700


def robots_triangulo():
    return grupo([(D.robot(), 450, 150, 0.6), (D.robot(), 150, 520, 0.6), (D.robot(), 750, 520, 0.6)], 900, 700)


def sobres_triangulo():
    return grupo([(D.sobre(), 560, 110, 0.36), (D.sobre(), 262, 480, 0.36), (D.sobre(), 862, 480, 0.36)], 900, 700)
