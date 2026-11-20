# -*- coding: utf-8 -*-
"""Dibujos del estilo MUÑECOS de reel-motion (look cartoon, motor claude-drawing): objetos con carita, gente de goma, letreros.
Todas las funciones reciben c (Cartoon) y dibujan de atrás hacia adelante (cada relleno tapa lo que hay detrás).
(x, y) es el punto donde la cosa toca el piso, salvo que se diga otra cosa; s es la escala."""
import numpy as np

import cd  # noqa: F401  (registra las fuentes)
from cartoon import Cartoon, darker, WHITE, RED, YELLOW, PINK, ORANGE, INK

E, R, P = Cartoon.ellipse_pts, Cartoon.rrect_pts, Cartoon.place

MENTA, MENTA_C, MENTA_O = '#7fcbb9', '#b6e5d9', '#4f9f90'
AZUL, AZUL_C, AZUL_O = '#6aa9e9', '#bfe0f6', '#3f6fb5'
CAFE, CAFE_C, CAFE_O = '#c07f45', '#e0a86f', '#7d4b26'
VERDE, VERDE_O = '#8cc56b', '#5f9b4b'
GRIS, GRIS_C, GRIS_O = '#b8b3ad', '#dcd8d2', '#77716b'
OSCURO = '#3b3640'
PIEL, PIEL_O = '#f6c9a0', '#dd9f74'
CREMA, PAPEL_O = '#fff7e6', '#e3d6bd'
LILA = '#b79be0'
DORADO = '#f6c544'


def sh(col, dx=14, dy=16):
    return (darker(col), dx, dy)


def pieza(c, pts, col, d=(14, 16), d2=None, w=7.0, slop=None, gaps=0):
    return c.shape(pts, col, shade=(darker(col), d[0], d[1]) if d else None,
                   shade2=(darker(col, 0.62), d2[0], d2[1]) if d2 else None, width=w, slop=slop, gaps=gaps)


def sombra(c, x, y, rx, ry=None):
    ry = ry or rx * 0.18
    c.fill(E(x, y, rx, ry), PAPEL_O, slop=0, wander=0.6, knock=False)
    c.hatch(E(x + rx * 0.05, y + ry * 0.1, rx * 0.86, ry * 0.62), angle=-60, spacing=13, width=2.3)


def titulo(c, s, x, y, size, fill=YELLOW, dcol=RED, rot=0.0, font='poppins'):
    c.letter(s, x, y, size, fill=fill, depth=(6, 9), depth_colour=dcol, font=font, anchor='m', rot=rot)


def nota(c, s, x, y, size=64, col=INK, rot=0.0, anchor='m', bold=0):
    return c.note(s, x, y, size, colour=col, font='caveat', anchor=anchor, rot=rot, bold=bold)


def equis(c, x, y, r, col=RED, w=24):
    c.glint([(x - r, y - r), (x, y), (x + r, y + r)], w, colour=col, taper=(r * 0.2, r * 0.3))
    c.glint([(x + r, y - r * 1.05), (x, y), (x - r * 0.95, y + r)], w, colour=col, taper=(r * 0.2, r * 0.3))


def chulo(c, x, y, r, col='#3faa55', w=26):
    c.glint([(x - r, y - r * 0.05), (x - r * 0.32, y + r * 0.62), (x + r, y - r * 0.85)], w, colour=col, taper=(r * 0.15, r * 0.4), smooth=False)


def flecha(c, pts, w=7, head=34):
    c.arrow(pts, width=w, head=head, spread=32)


def chispas(c, pts, r=26, col=YELLOW):
    for (x, y) in pts:
        c.sparkle(x, y, r, col)


# ------------------------------------------------------------------------------------------------ animales y gente
def caballo(c, x, y, s=1.0, mood='happy'):
    sombra(c, x - 10 * s, y + 4, 175 * s, 26 * s)
    for lx, col in ((-95, CAFE_O), (60, CAFE_O)):                  # patas de atrás (lejanas)
        pieza(c, R(x + (lx + 22) * s, y - 185 * s, x + (lx + 52) * s, y - 14 * s, 12 * s), col, (6, 8), w=6)
        pieza(c, R(x + (lx + 18) * s, y - 26 * s, x + (lx + 56) * s, y, 6 * s), OSCURO, None, w=5)
    cola = [(x - 150 * s, y - 250 * s), (x - 205 * s, y - 225 * s), (x - 222 * s, y - 150 * s), (x - 196 * s, y - 120 * s),
            (x - 190 * s, y - 175 * s), (x - 160 * s, y - 215 * s)]
    pieza(c, cola, CAFE_O, (6, 6), w=6)
    cuerpo = E(x - 15 * s, y - 225 * s, 155 * s, 78 * s)
    pieza(c, cuerpo, CAFE, (24, 18), w=8)
    for lx in (-125, 30):                                          # patas cercanas
        pieza(c, R(x + lx * s, y - 190 * s, x + (lx + 36) * s, y - 14 * s, 12 * s), CAFE, (8, 6), w=6.5)
        pieza(c, R(x + (lx - 4) * s, y - 28 * s, x + (lx + 40) * s, y, 6 * s), OSCURO, None, w=5)
    cuello = [(x + 70 * s, y - 280 * s), (x + 118 * s, y - 380 * s), (x + 195 * s, y - 368 * s), (x + 150 * s, y - 230 * s)]
    pieza(c, cuello, CAFE, (16, 10), w=7)
    crin = [(x + 64 * s, y - 286 * s), (x + 92 * s, y - 360 * s), (x + 118 * s, y - 440 * s), (x + 140 * s, y - 400 * s),
            (x + 110 * s, y - 330 * s), (x + 96 * s, y - 280 * s)]
    pieza(c, crin, CAFE_O, (5, 5), w=6)
    for ex in (-34, 34):
        pieza(c, [(x + (160 + ex) * s, y - 470 * s), (x + (160 + ex * 1.5) * s, y - 525 * s), (x + (160 + ex * 0.3) * s, y - 480 * s)], CAFE, (4, 6), w=5.5)
    cab = E(x + 160 * s, y - 418 * s, 66 * s, 78 * s)
    pieza(c, cab, CAFE, (14, 14), w=7.5)
    hoc = E(x + 160 * s, y - 360 * s, 50 * s, 34 * s)
    pieza(c, hoc, CAFE_C, (8, 8), w=6)
    for nx in (-18, 18): c.dot(x + (160 + nx) * s, y - 360 * s, 5 * s)
    c.face(x + 160 * s, y - 432 * s, 82 * s, mood, blush=True)


def persona(c, x, y, s=1.0, camisa=AZUL, pelo=OSCURO, mood='happy', piel=PIEL, pantalon=OSCURO, gorra=None,
            gafas=False, audifonos=False, brazos=((-0.9, 0.2), (0.9, 0.2)), estilo_pelo='corto', mano_der=None):
    """persona de goma: y = piso. brazos = posición de las manos (relativa al tamaño), mano_der = función(c, x, y)."""
    sombra(c, x, y + 4, 92 * s, 18 * s)
    hx, hy = x, y - 330 * s
    for lx in (-30, 30):                                            # piernas
        c.line([(x + lx * s, y - 140 * s), (x + lx * 1.1 * s, y - 24 * s)], 15 * s, taper=(2, 2), press=0.05)
        pieza(c, E(x + (lx * 1.15 + 10) * s, y - 14 * s, 30 * s, 16 * s), OSCURO, None, w=5)
    hombros = [(x - 70 * s, y - 250 * s), (x + 70 * s, y - 250 * s)]
    manos = [(x + bx * 130 * s, y - 250 * s + by * 130 * s) for bx, by in brazos]
    for (p0, p1, th) in ((hombros[0], manos[0], -1), (hombros[1], manos[1], 1)):
        c.arm(p0, p1, bend=0.25 * th, width=7 * s, hand=22 * s, thumb=th)
    cuerpo = R(x - 78 * s, y - 268 * s, x + 78 * s, y - 120 * s, (40 * s, 40 * s, 18 * s, 18 * s))
    pieza(c, cuerpo, camisa, (18, 10), w=7)
    pieza(c, R(x - 74 * s, y - 150 * s, x + 74 * s, y - 112 * s, 12 * s), pantalon, None, w=6)
    if estilo_pelo == 'largo':
        pieza(c, R(hx - 82 * s, hy - 60 * s, hx + 82 * s, hy + 85 * s, 50 * s), pelo, None, w=6)
    cab = E(hx, hy, 72 * s, 72 * s)
    pieza(c, cab, piel, (12, 14), w=7)
    for ex in (-1, 1):
        pieza(c, E(hx + ex * 72 * s, hy + 8 * s, 14 * s, 18 * s), piel, None, w=5)
    if gorra:
        pieza(c, [(hx - 74 * s, hy - 14 * s), (hx - 70 * s, hy - 60 * s), (hx, hy - 84 * s), (hx + 70 * s, hy - 60 * s),
                  (hx + 74 * s, hy - 14 * s)], gorra, (8, 8), w=6.5)
        pieza(c, R(hx + 20 * s, hy - 26 * s, hx + 128 * s, hy - 8 * s, 9 * s), gorra, (4, 6), w=6)
    else:
        top = [(hx - 74 * s, hy - 4 * s), (hx - 70 * s, hy - 52 * s), (hx - 20 * s, hy - 86 * s), (hx + 44 * s, hy - 80 * s),
               (hx + 78 * s, hy - 40 * s), (hx + 70 * s, hy - 14 * s), (hx + 30 * s, hy - 38 * s), (hx - 34 * s, hy - 34 * s)]
        pieza(c, top, pelo, (6, 8), w=6)
    c.face(hx, hy + 14 * s, 92 * s, mood)
    if gafas:
        for ex in (-1, 1):
            pieza(c, R(hx + ex * 34 * s - 28 * s, hy - 2 * s, hx + ex * 34 * s + 28 * s, hy + 30 * s, 10 * s), OSCURO, None, w=5)
        c.line([(hx - 8 * s, hy + 8 * s), (hx + 8 * s, hy + 8 * s)], 5 * s, taper=(1, 1))
        c.glint([(hx - 50 * s, hy + 4 * s), (hx - 40 * s, hy + 2 * s)], 5 * s)
    if audifonos:
        c.line(E(hx, hy - 10 * s, 86 * s, 86 * s, a0=190, a1=350), 13 * s, taper=(2, 2))
        for ex in (-1, 1):
            pieza(c, R(hx + ex * 86 * s - 20 * s, hy - 22 * s, hx + ex * 86 * s + 20 * s, hy + 36 * s, 14 * s), RED, (6, 6), w=6)
    if mano_der: mano_der(c, *manos[1])
    return dict(cabeza=(hx, hy), manos=manos)


# ------------------------------------------------------------------------------------------------ máquinas
def carro(c, x, y, s=1.0, mood='happy', col=RED):
    sombra(c, x, y + 4, 250 * s, 24 * s)
    ruedas = [(x - 150 * s, y - 68 * s), (x + 150 * s, y - 68 * s)]
    pieza(c, R(x - 205 * s, y - 330 * s, x - 25 * s, y - 165 * s, (30 * s, 30 * s, 4, 4)), OSCURO, (8, 8), w=7)
    pieza(c, R(x - 180 * s, y - 305 * s, x - 50 * s, y - 210 * s, 14 * s), AZUL_C, (6, 6), w=5)
    pieza(c, R(x - 25 * s, y - 248 * s, x + 205 * s, y - 165 * s, (14 * s, 26 * s, 4, 4)), col, (14, 12), w=7)
    pieza(c, R(x + 196 * s, y - 252 * s, x + 226 * s, y - 160 * s, 8 * s), GRIS, (4, 4), w=6)
    pieza(c, R(x - 235 * s, y - 175 * s, x + 238 * s, y - 100 * s, 22 * s), col, (16, 14), w=7.5)
    for (wx, wy) in ruedas:
        pieza(c, E(wx, wy, 70 * s, 70 * s), OSCURO, None, w=7)
        pieza(c, E(wx, wy, 42 * s, 42 * s), CREMA, (6, 6), w=5)
        for a in range(0, 180, 30):
            t = np.deg2rad(a)
            c.line([(wx - np.cos(t) * 38 * s, wy - np.sin(t) * 38 * s), (wx + np.cos(t) * 38 * s, wy + np.sin(t) * 38 * s)], 3.4 * s, (2, 2), smooth=False)
        c.dot(wx, wy, 8 * s)
    pieza(c, E(x + 230 * s, y - 225 * s, 22 * s, 22 * s), YELLOW, (4, 4), w=5)
    c.glint([(x - 200 * s, y - 160 * s), (x - 90 * s, y - 162 * s)], 7 * s)
    c.face(x + 80 * s, y - 214 * s, 74 * s, mood)


def celular(c, x, y, w=210, h=380, mood='wow', rot=0.0, cara=True, pantalla=AZUL_C):
    """(x, y) = centro"""
    body = P(R(-w / 2, -h / 2, w / 2, h / 2, w * 0.16), x, y, 1, rot)
    pieza(c, body, OSCURO, (10, 10), w=7)
    scr = P(R(-w / 2 + 16, -h / 2 + 34, w / 2 - 16, h / 2 - 34, w * 0.07), x, y, 1, rot)
    c.fill(scr, pantalla, slop=1.5, knock=False)
    c.outline(scr, 4, 0.2)
    c.line(P([(-w * 0.12, -h / 2 + 18), (w * 0.12, -h / 2 + 18)], x, y, 1, rot), 6, (2, 2), smooth=False)
    c.glint(P([(-w / 2 + 30, -h / 2 + 60), (-w / 2 + 30, -h / 2 + 140)], x, y, 1, rot), 8)
    if cara: c.face(*P([(0, 10)], x, y, 1, rot)[0], w * 0.6, mood, rot=rot)


def reloj(c, x, y, r=110, hora=(4, 0), mood='sleepy', col=RED):
    """(x, y) = centro"""
    pieza(c, E(x, y, r, r), col, (14, 14), w=8)
    dial = E(x, y, r * 0.78, r * 0.78)
    c.fill(dial, CREMA, slop=2, knock=False)
    c.outline(dial, 4.5, 0.2)
    for k in range(12):
        t = np.deg2rad(90 - k * 30); r0 = r * (0.56 if k % 3 == 0 else 0.63)
        c.line([(x + np.cos(t) * r0, y - np.sin(t) * r0), (x + np.cos(t) * r * 0.7, y - np.sin(t) * r * 0.7)], 4.5 if k % 3 == 0 else 3, (2, 2), smooth=False)
    hh, mm = hora
    for ang, L, w in ((90 - (hh % 12 + mm / 60) * 30, 0.36, 8), (90 - mm * 6, 0.52, 6)):
        t = np.deg2rad(ang)
        c.line([(x, y), (x + np.cos(t) * r * L, y - np.sin(t) * r * L)], w, (2, 6), smooth=False)
    c.dot(x, y, 7)
    if mood: c.face(x, y + r * 0.3, r * 0.62, mood, blush=False)
    for bx in (-1, 1):
        pieza(c, E(x + bx * r * 0.62, y - r * 0.95, r * 0.24, r * 0.2), col, (4, 4), w=6)


def mundo(c, x, y, r=170, mood='happy'):
    globo = E(x, y, r, r)
    F = c.fill(globo, '#5aa7e0', slop=2)
    m = c.mask(globo)
    for (cx, cy, rx, ry, rt) in ((-0.45, -0.35, 0.42, 0.3, 20), (0.35, 0.05, 0.34, 0.46, -15), (-0.2, 0.55, 0.3, 0.2, 5)):
        c.fill(c.mask(E(x + cx * r, y + cy * r, rx * r, ry * r, rt)) * m, VERDE, slop=2, knock=False)
    c.shade(globo, '#3f7fbf', (r * 0.22, r * 0.2), clip=F)
    c.outline(globo, 8, 0.35)
    c.glint(E(x, y, r * 0.8, r * 0.8, a0=200, a1=245), 10)
    c.face(x, y + r * 0.08, r * 0.95, mood)


def burbuja_ia(c, x, y, w=330, h=230, mood='happy', col=MENTA, etiqueta='ChatGPT', acc=None, chispa=True, et_size=64):
    """(x, y) = centro del globo de chat con cara. acc: 'audifonos', 'casco', 'banda', 'flor'"""
    if acc == 'audifonos':
        c.line(E(x, y - h * 0.08, w * 0.56, h * 0.78, a0=195, a1=345), 15, taper=(2, 2))
    cola = [(x - w * 0.3, y + h * 0.38), (x - w * 0.42, y + h * 0.78), (x - w * 0.08, y + h * 0.42)]
    pieza(c, cola, col, (6, 6), w=7)
    cuerpo = R(x - w / 2, y - h / 2, x + w / 2, y + h / 2, h * 0.42)
    pieza(c, cuerpo, col, (18, 16), w=8)
    c.glint([(x - w * 0.36, y - h * 0.18), (x - w * 0.25, y - h * 0.36)], 10)
    c.face(x, y + h * 0.04, h * 0.7, mood)
    if acc == 'audifonos':
        for sx in (-1, 1):
            pieza(c, R(x + sx * w * 0.5 - 24, y - h * 0.22, x + sx * w * 0.5 + 24, y + h * 0.2, 18), OSCURO, (6, 6), w=6)
    elif acc == 'casco':
        pieza(c, [(x - w * 0.36, y - h * 0.42), (x - w * 0.3, y - h * 0.78), (x, y - h * 0.92), (x + w * 0.3, y - h * 0.78), (x + w * 0.36, y - h * 0.42)], YELLOW, (10, 8), w=7)
        pieza(c, R(x - w * 0.48, y - h * 0.5, x + w * 0.48, y - h * 0.38, 8), YELLOW, (4, 6), w=6)
    elif acc == 'banda':
        pieza(c, R(x - w * 0.44, y - h * 0.44, x + w * 0.44, y - h * 0.3, 10), RED, (4, 4), w=6)
    elif acc == 'flor':
        fx, fy = x + w * 0.36, y - h * 0.42
        for k in range(5):
            t = np.deg2rad(k * 72)
            pieza(c, E(fx + np.cos(t) * 22, fy + np.sin(t) * 22, 17, 17), CREMA, None, w=4.5)
        pieza(c, E(fx, fy, 13, 13), YELLOW, None, w=4.5)
    if chispa and acc is None: c.sparkle(x + w * 0.46, y - h * 0.5, 30, YELLOW)
    if etiqueta: nota(c, etiqueta, x, y + h * 0.5 + 76 * et_size / 64, et_size)


def llamas(c, x, y, L=170, ang=180):
    """fuego de cohete que sale de (x, y) hacia el ángulo ang (180 = a la izquierda)"""
    for k, (col, sc) in enumerate(((ORANGE, 1.0), (YELLOW, 0.62), (WHITE, 0.3))):
        pts = P([(0, -48 * sc), (L * 0.55 * sc, -30 * sc), (L * sc, 0), (L * 0.55 * sc, 30 * sc), (0, 48 * sc)], x, y, 1, ang)
        c.fill(pts, col, slop=2, knock=k == 0)
        if k == 0: c.outline(pts, 6, 0.2)


def torta(c, x, y, s=1.0, mood='happy'):
    """devuelve las posiciones (x, y) de las 3 velas"""
    sombra(c, x, y + 6, 230 * s, 26 * s)
    pieza(c, E(x, y - 6 * s, 225 * s, 36 * s), CREMA, (0, 10), w=6)
    pieza(c, R(x - 175 * s, y - 210 * s, x + 175 * s, y - 20 * s, 24 * s), '#f39aa8', (26, 14), w=8)
    goteo = [(x - 182 * s, y - 214 * s)] + [(x + (-182 + k * 26) * s, y - (214 - (34 if k % 2 else 6)) * s) for k in range(1, 15)] + \
            [(x + 182 * s, y - 214 * s), (x + 182 * s, y - 238 * s), (x - 182 * s, y - 238 * s)]
    pieza(c, goteo, CREMA, (6, 8), w=6.5)
    rr = np.random.default_rng(3)
    for _ in range(14):
        px, py = x + rr.uniform(-150, 150) * s, y - rr.uniform(40, 150) * s
        if abs(px - x) < 70 * s and py < y - 70 * s: continue
        c.fill(R(px - 8 * s, py - 3 * s, px + 8 * s, py + 3 * s, 3), [YELLOW, MENTA, AZUL][rr.integers(3)], slop=0.5, knock=False)
    c.face(x, y - 110 * s, 110 * s, mood)
    return [(x + dx * s, y - 238 * s) for dx in (-100, 0, 100)]


def vela(c, x, y, s=1.0):
    pieza(c, R(x - 13 * s, y - 92 * s, x + 13 * s, y + 4, 6 * s), AZUL_C, (4, 4), w=5)
    for k in range(3):
        c.line([(x - 13 * s, y - (20 + 26 * k) * s), (x + 13 * s, y - (34 + 26 * k) * s)], 4 * s, (1, 1), smooth=False)
    c.line([(x, y - 92 * s), (x + 2, y - 108 * s)], 4 * s, (1, 2), smooth=False)
    fl = [(x, y - 168 * s), (x + 22 * s, y - 128 * s), (x, y - 106 * s), (x - 22 * s, y - 128 * s)]
    c.fill(fl, ORANGE, slop=1.5)
    c.fill([(x, y - 150 * s), (x + 11 * s, y - 126 * s), (x, y - 112 * s), (x - 11 * s, y - 126 * s)], YELLOW, slop=0.5, knock=False)
    c.outline(fl, 5, 0.2)


def calendario(c, x, y, w=300, h=330, texto='?', col_texto=RED):
    """(x, y) = centro"""
    pieza(c, R(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 18), CREMA, (12, 14), w=7)
    pieza(c, R(x - w / 2, y - h / 2, x + w / 2, y - h / 2 + 78, (18, 18, 0, 0)), RED, (6, 8), w=7)
    for rx in (-0.28, 0.28):
        pieza(c, R(x + rx * w - 10, y - h / 2 - 30, x + rx * w + 10, y - h / 2 + 20, 8), GRIS, (3, 3), w=5)
    titulo(c, texto, x, y + h * 0.33, h * 0.42, fill=CREMA, dcol=col_texto)


def medidor(c, x, y, r=230, valor=0.9):
    """(x, y) = centro de la base del medio círculo; valor 0..1"""
    zonas = ((VERDE, 180, 120), (YELLOW, 120, 60), (RED, 60, 0))
    for col, a0, a1 in zonas:
        t = np.deg2rad(np.linspace(a0, a1, 30))
        pts = np.vstack([np.stack([x + np.cos(t) * r, y - np.sin(t) * r], 1), np.stack([x + np.cos(t[::-1]) * r * 0.55, y - np.sin(t[::-1]) * r * 0.55], 1)])
        pieza(c, pts, col, (6, 6), w=6)
    base = R(x - r - 20, y, x + r + 20, y + 44, 14)
    pieza(c, base, GRIS, (6, 8), w=6)
    t = np.deg2rad(180 - 180 * valor)
    c.line([(x, y), (x + np.cos(t) * r * 0.92, y - np.sin(t) * r * 0.92)], 13, (4, 18), smooth=False)
    pieza(c, E(x, y, 26, 26), OSCURO, None, w=6)


def lupa(c, x, y, r=90, rot=-40):
    """(x, y) = centro del vidrio"""
    t = np.deg2rad(rot)
    d = np.array([np.cos(t), -np.sin(t)])
    p0 = np.array([x, y]) + d * r * 0.95; p1 = np.array([x, y]) + d * r * 2.1
    c.line([tuple(p0), tuple(p1)], 26, (2, 2), smooth=False)
    vid = E(x, y, r, r)
    c.fill(vid, AZUL_C, slop=2)
    c.outline(E(x, y, r, r), 14, 0.2)
    c.glint(E(x, y, r * 0.68, r * 0.68, a0=200, a1=250), 9)


def globo_texto(c, x, y, w, h, texto, cola='izq', size=56, col=CREMA):
    """(x, y) = centro; cola hacia abajo a la izquierda o derecha"""
    sx = -1 if cola == 'izq' else 1
    pieza(c, [(x + sx * w * 0.18, y + h * 0.4), (x + sx * w * 0.32, y + h * 0.82), (x + sx * w * 0.02, y + h * 0.45)], col, None, w=6)
    pieza(c, R(x - w / 2, y - h / 2, x + w / 2, y + h / 2, h * 0.38), col, (10, 12), w=7)
    nota(c, texto, x, y + size * 0.3, size)


def teclado(c, x, y, w=420, h=150, mood='wow', rot=0.0):
    """(x, y) = centro"""
    pieza(c, P(R(-w / 2, -h / 2, w / 2, h / 2, 22), x, y, 1, rot), GRIS_C, (12, 12), w=7)
    for row in range(3):
        for col in range(9):
            kx = -w / 2 + 28 + col * (w - 56) / 8.4; ky = -h / 2 + 30 + row * 38
            if row == 2 and 2 <= col <= 6:
                if col == 2: pieza(c, P(R(kx - 14, ky - 13, kx + 4 * (w - 56) / 8.4 + 14, ky + 13, 6), x, y, 1, rot), CREMA, None, w=3.5)
                continue
            pieza(c, P(R(kx - 14, ky - 13, kx + 14, ky + 13, 6), x, y, 1, rot), CREMA, None, w=3.5)
    c.face(*P([(0, -h / 2 - 60)], x, y, 1, rot)[0], 110, mood)


def casete(c, x, y, w=330, mood='sleepy', cinta=False, rot=0.0):
    """(x, y) = centro"""
    h = w * 0.64
    T = lambda pts: P(pts, x, y, 1, rot)
    pieza(c, T(R(-w / 2, -h / 2, w / 2, h / 2, 18)), OSCURO, (10, 12), w=7)
    pieza(c, T(R(-w / 2 + 24, -h / 2 + 22, w / 2 - 24, h * 0.18, 12)), YELLOW, (6, 6), w=5)
    pieza(c, T(R(-w * 0.3, -h * 0.02, w * 0.3, h * 0.16, 10)), GRIS_C, None, w=4)
    for sx in (-1, 1):
        pieza(c, T(E(sx * w * 0.19, h * 0.07, w * 0.07, w * 0.07)), CREMA, None, w=4)
    pieza(c, T([(-w * 0.32, h / 2), (-w * 0.24, h * 0.28), (w * 0.24, h * 0.28), (w * 0.32, h / 2)]), GRIS_O, None, w=5)
    c.face(*T([(0, -h * 0.17)])[0], w * 0.3, mood, rot=rot)
    if cinta:
        rr = np.random.default_rng(5)
        pts = [tuple(T([(w * 0.1, h * 0.5)])[0])]
        for k in range(9):
            pts.append((pts[-1][0] + rr.uniform(-60, 70), pts[-1][1] + rr.uniform(20, 55)))
        c.line(pts, 6, (4, 10))


def walkman(c, x, y, w=210, rot=0.0):
    """(x, y) = centro"""
    h = w * 1.35
    T = lambda pts: P(pts, x, y, 1, rot)
    pieza(c, T(R(-w / 2, -h / 2, w / 2, h / 2, 20)), AZUL, (12, 12), w=7)
    pieza(c, T(R(-w / 2 + 20, -h / 2 + 30, w / 2 - 20, h * 0.12, 12)), OSCURO, None, w=5)
    for sx in (-1, 1):
        pieza(c, T(E(sx * w * 0.18, -h * 0.12, w * 0.08, w * 0.08)), GRIS_C, None, w=4)
    for k in range(3):
        pieza(c, T(R(-w / 2 + 22 + k * (w - 44) / 3 + 4, h * 0.24, -w / 2 + 22 + (k + 1) * (w - 44) / 3 - 4, h * 0.4, 6)), [RED, GRIS_C, GRIS_C][k], None, w=4)
    c.line(T([(w * 0.3, -h / 2), (w * 0.5, -h / 2 - 60), (w * 0.2, -h / 2 - 120)]), 6, (4, 8))


def tienda(c, x, y, w=420, h=420, mood='happy', toldo=(RED, CREMA), pared='#f6d7a7', telas=False, grieta=False,
           corona=False, letrero=None, brillo=False):
    """(x, y) = piso, centro"""
    sombra(c, x, y + 6, w * 0.62, 24)
    pieza(c, R(x - w / 2, y - h, x + w / 2, y, 10), pared, (20, 14), w=8)
    pieza(c, R(x - w / 2 - 20, y - h - 30, x + w / 2 + 20, y - h + 10, 10), GRIS_O, (6, 6), w=6)
    n = 6; ww = (w + 40) / n
    for k in range(n):
        x0 = x - w / 2 - 20 + k * ww
        pts = [(x0, y - h + 10), (x0 + ww, y - h + 10), (x0 + ww, y - h + 80), (x0 + ww * 0.5, y - h + 104), (x0, y - h + 80)]
        c.fill(pts, toldo[k % 2], slop=1.5, knock=True)
    c.outline([(x - w / 2 - 20, y - h + 10), (x + w / 2 + 20, y - h + 10), (x + w / 2 + 20, y - h + 80)] +
              [(x + w / 2 + 20 - ww * (k + 0.5), y - h + (104 if k % 1 == 0 else 80)) for k in range(n)] + [(x - w / 2 - 20, y - h + 80)], 7, 0.3)
    pieza(c, R(x + w * 0.12, y - h * 0.5, x + w * 0.4, y, 8), CAFE, (8, 8), w=6)
    c.dot(x + w * 0.16, y - h * 0.24, 6)
    win = R(x - w * 0.42, y - h * 0.62, x + w * 0.04, y - h * 0.18, 12)
    pieza(c, win, AZUL_C if not telas else GRIS_C, (10, 10), w=6.5)
    c.face(x - w * 0.19, y - h * 0.38, w * 0.3, mood)
    if letrero:
        pieza(c, R(x - w * 0.36, y - h - 110, x + w * 0.36, y - h - 40, 14), CREMA, (6, 8), w=6)
        nota(c, letrero, x, y - h - 56, 54)
    if telas:
        for (cx, cy, sx) in ((x - w / 2 + 6, y - h + 120, 1), (x + w / 2 - 6, y - h + 120, -1)):
            for k in range(4):
                t = np.deg2rad(k * 30)
                c.line([(cx, cy), (cx + sx * np.cos(t) * 90, cy + np.sin(t) * 90)], 2.2, (1, 1), smooth=False, rough=False)
            for rr in (30, 55, 80):
                c.line([(cx + sx * rr, cy), (cx + sx * rr * 0.87, cy + rr * 0.5), (cx + sx * rr * 0.5, cy + rr * 0.87)], 2, (1, 1), rough=False)
    if grieta:
        c.line([(x - w * 0.05, y - h + 110), (x + w * 0.04, y - h * 0.72), (x - w * 0.06, y - h * 0.6), (x + w * 0.05, y - h * 0.46),
                (x - w * 0.02, y - h * 0.3)], 7, (2, 10), smooth=False)
    if corona:
        cx, cy = x, y - h - 40
        pts = [(cx - 100, cy), (cx - 110, cy - 90), (cx - 55, cy - 40), (cx, cy - 110), (cx + 55, cy - 40), (cx + 110, cy - 90), (cx + 100, cy)]
        pieza(c, pts, DORADO, (8, 8), w=7)
        for jx in (-60, 0, 60): pieza(c, E(cx + jx, cy - 20, 11, 11), RED, None, w=4)
    if brillo:
        chispas(c, [(x - w / 2 - 40, y - h * 0.7), (x + w / 2 + 50, y - h * 0.5), (x + w / 2 + 20, y - h - 60)], 30)


def robot(c, x, y, s=1.0, mood='happy', casco=True, col='#9fb7d6', brazos=((-0.9, 0.1), (0.9, 0.1)), mano_der=None):
    """agente IA: y = piso"""
    sombra(c, x, y + 4, 95 * s, 18 * s)
    for lx in (-32, 32):
        c.line([(x + lx * s, y - 110 * s), (x + lx * s, y - 22 * s)], 16 * s, taper=(2, 2), press=0.04)
        pieza(c, R(x + (lx - 26) * s, y - 26 * s, x + (lx + 26) * s, y, 10 * s), OSCURO, None, w=5)
    hombros = [(x - 70 * s, y - 200 * s), (x + 70 * s, y - 200 * s)]
    manos = [(x + bx * 130 * s, y - 200 * s + by * 130 * s) for bx, by in brazos]
    for (p0, p1, th) in ((hombros[0], manos[0], -1), (hombros[1], manos[1], 1)):
        c.arm(p0, p1, bend=0.2 * th, width=7 * s, hand=21 * s, thumb=th)
    pieza(c, R(x - 78 * s, y - 230 * s, x + 78 * s, y - 100 * s, 24 * s), col, (16, 12), w=7)
    pieza(c, E(x, y - 165 * s, 22 * s, 22 * s), YELLOW, None, w=5)
    c.line([(x, y - 330 * s), (x, y - 380 * s)], 6 * s, (2, 2), smooth=False)
    pieza(c, E(x, y - 392 * s, 16 * s, 16 * s), RED, None, w=5)
    cab = R(x - 92 * s, y - 345 * s, x + 92 * s, y - 228 * s, 34 * s)
    pieza(c, cab, col, (14, 12), w=7.5)
    pieza(c, R(x - 72 * s, y - 330 * s, x + 72 * s, y - 244 * s, 24 * s), MENTA_C, (6, 6), w=5)
    c.face(x, y - 284 * s, 92 * s, mood)
    if casco:
        pieza(c, [(x - 96 * s, y - 336 * s), (x - 80 * s, y - 388 * s), (x, y - 414 * s), (x + 80 * s, y - 388 * s), (x + 96 * s, y - 336 * s)], YELLOW, (10, 8), w=7)
        pieza(c, R(x - 118 * s, y - 348 * s, x + 118 * s, y - 330 * s, 9 * s), YELLOW, (4, 6), w=6)
    if mano_der: mano_der(c, *manos[1])
    return dict(manos=manos)


def papeles(c, x, y, n=6, s=1.0):
    """pila de papeles; y = piso"""
    rr = np.random.default_rng(int(x) % 97)
    for k in range(n):
        yy = y - k * 30 * s
        pts = P(R(-110 * s, -16 * s, 110 * s, 16 * s, 5), x + rr.uniform(-14, 14) * s, yy - 16 * s, 1, rr.uniform(-6, 6))
        pieza(c, pts, CREMA, (0, 6), w=5)


def bolsa_dinero(c, x, y, s=1.0):
    sombra(c, x, y + 4, 120 * s, 20 * s)
    pts = [(x - 40 * s, y - 210 * s), (x - 70 * s, y - 175 * s), (x - 125 * s, y - 90 * s), (x - 110 * s, y - 10 * s), (x + 110 * s, y - 10 * s),
           (x + 125 * s, y - 90 * s), (x + 70 * s, y - 175 * s), (x + 40 * s, y - 210 * s)]
    pieza(c, pts, '#d9b47a', (18, 14), w=7.5)
    pieza(c, [(x - 60 * s, y - 250 * s), (x, y - 205 * s), (x + 60 * s, y - 250 * s), (x + 30 * s, y - 196 * s), (x - 30 * s, y - 196 * s)], '#d9b47a', (4, 4), w=6)
    c.line([(x - 52 * s, y - 196 * s), (x + 52 * s, y - 196 * s)], 9 * s, (2, 2))
    titulo(c, '$', x, y - 50 * s, 120 * s, fill=VERDE, dcol=VERDE_O)


def comentario(c, x, y, w=820, h=230, texto='ERA'):
    """(x, y) = centro de la caja de comentario (tipo Instagram)"""
    pieza(c, R(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 40), CREMA, (14, 16), w=7)
    pieza(c, E(x - w / 2 + 90, y, 52, 52), PINK, (6, 6), w=6)
    c.face(x - w / 2 + 90, y + 6, 54, 'happy', blush=False)
    nota(c, '@tu_usuario', x - w / 2 + 170, y - h * 0.18, 44, col='#6b6370', anchor='l')
    titulo(c, texto, x + 80, y + h * 0.33, h * 0.6, fill=YELLOW, dcol=RED)


def sobre(c, x, y, w=280, mood='happy', rot=0.0):
    """(x, y) = centro"""
    h = w * 0.66
    T = lambda pts: P(pts, x, y, 1, rot)
    pieza(c, T(R(-w / 2, -h / 2, w / 2, h / 2, 12)), CREMA, (10, 12), w=7)
    c.line(T([(-w / 2 + 6, -h / 2 + 8), (0, h * 0.12), (w / 2 - 6, -h / 2 + 8)]), 6, (2, 2), smooth=False)
    c.face(*T([(0, h * 0.24)])[0], w * 0.34, mood, rot=rot)


def laptop(c, x, y, w=420, texto='CLASE'):
    """(x, y) = centro de la pantalla"""
    h = w * 0.62
    pieza(c, R(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 18), OSCURO, (10, 10), w=7)
    pieza(c, R(x - w / 2 + 18, y - h / 2 + 18, x + w / 2 - 18, y + h / 2 - 18, 10), AZUL_C, None, w=4.5)
    pieza(c, [(x - w * 0.62, y + h / 2 + 40), (x - w * 0.5, y + h / 2), (x + w * 0.5, y + h / 2), (x + w * 0.62, y + h / 2 + 40)], GRIS_C, (6, 8), w=6)
    tri = [(x - 30, y - 44), (x + 46, y), (x - 30, y + 44)]
    pieza(c, E(x + 6, y, 70, 70), RED, (6, 6), w=6)
    c.fill(tri, CREMA, slop=1, knock=False)
    nota(c, texto, x, y + h / 2 - 34, 46, col=OSCURO)


def nube_lluvia(c, x, y, r=90):
    c.puff(x, y, r, colour='#a8b3c4', shadow='#7f8aa0', fx=False)
    for k in range(5):
        xx = x - r * 0.8 + k * r * 0.4
        c.line([(xx, y + r * 0.7), (xx - 12, y + r * 1.25)], 5, (2, 4), smooth=False)


def rayo(c, x, y, s=1.0):
    pts = [(x - 20 * s, y - 120 * s), (x + 60 * s, y - 120 * s), (x + 15 * s, y - 20 * s), (x + 65 * s, y - 20 * s),
           (x - 40 * s, y + 130 * s), (x - 5 * s, y + 20 * s), (x - 55 * s, y + 20 * s)]
    pieza(c, pts, YELLOW, (8, 8), w=7, slop=1.5)


def caracol(c, x, y, s=1.0, mood='sleepy'):
    """y = piso"""
    sombra(c, x, y + 4, 170 * s, 20 * s)
    body = [(x - 165 * s, y), (x - 140 * s, y - 40 * s), (x + 60 * s, y - 50 * s), (x + 100 * s, y - 120 * s), (x + 150 * s, y - 135 * s),
            (x + 175 * s, y - 95 * s), (x + 150 * s, y - 20 * s), (x + 120 * s, y)]
    for ex in (128, 160):
        c.line([(x + ex * s, y - 128 * s), (x + (ex + 8) * s, y - 210 * s)], 7 * s, (2, 2))
        pieza(c, E(x + (ex + 8) * s, y - 214 * s, 13 * s, 13 * s), '#cfe0a8', None, w=5)
    pieza(c, body, '#cfe0a8', (12, 10), w=7)
    shell = E(x - 30 * s, y - 128 * s, 108 * s, 100 * s)
    pieza(c, shell, '#f5a54a', (20, 18), w=8)
    t = np.linspace(0, 4.4 * np.pi, 80)
    rad = np.linspace(86, 8, 80) * s
    c.line(np.stack([x - 30 * s + np.cos(t) * rad, y - 128 * s + np.sin(t) * rad * 0.93], 1), 6, (6, 4))
    c.face(x + 142 * s, y - 92 * s, 52 * s, mood, blush=True)
