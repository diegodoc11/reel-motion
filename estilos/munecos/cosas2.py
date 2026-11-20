# -*- coding: utf-8 -*-
"""Más dibujos del estilo MUÑECOS (look cartoon): monedas, engranajes, avión de papel, ojo, carrito,
cámara, megáfono, escudo, etiqueta de precio, documentos, perfiles, buscador, diana, lista, botón, luna, cama..."""
import math

import numpy as np

from cosas import (E, R, P, pieza, sombra, titulo, nota, chulo, lupa, laptop, persona, darker, RED, YELLOW, ORANGE, PINK,
                   WHITE, MENTA, AZUL, AZUL_C, CAFE, CAFE_C, VERDE, GRIS, GRIS_C, GRIS_O, OSCURO, PIEL, CREMA, DORADO)


def corazon_pts(x, y, r):
    t = np.linspace(0, 2 * np.pi, 80, endpoint=False)
    hx = 16 * np.sin(t) ** 3
    hy = -(13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t))
    return np.stack([x + hx * r / 16, y + hy * r / 16], 1)


def corazon(c, x, y, r=34, col=RED):
    pieza(c, corazon_pts(x, y, r), col, (r * 0.18, r * 0.2), w=max(4, r * 0.16))


def monedas(c, x, y, n=5, s=1.0):
    """pila de monedas con carita; y = piso"""
    sombra(c, x, y + 4, 95 * s, 16 * s)
    for k in range(n):
        yy = y - 14 * s - k * 22 * s
        pieza(c, E(x + (k % 2) * 6 * s, yy, 80 * s, 22 * s), DORADO, (0, 6), w=5.5)
    c.face(x, y - 60 * s - (n - 1) * 22 * s, 56 * s, 'happy', blush=False)


def moneda(c, x, y, r=40, rot=0):
    pieza(c, E(x, y, r, r * 0.9, rot), DORADO, (r * 0.2, r * 0.2), w=5)
    nota(c, '$', x, y + r * 0.42, r * 1.3, col='#a87a1d')


def engranaje(c, x, y, r=90, col=GRIS_C, dientes=9, fase=0.0):
    t = np.linspace(0, 2 * np.pi, dientes * 16, endpoint=False) + fase
    rr = r * (0.82 + 0.18 * (np.cos(t * dientes) > 0.1))
    pts = np.stack([x + np.cos(t) * rr, y + np.sin(t) * rr], 1)
    F = c.fill(pts, col, slop=1.5)
    c.shade(pts, darker(col), (r * 0.14, r * 0.16), clip=F)
    c.outline(pts, 6, 0.3, smooth=False)
    pieza(c, E(x, y, r * 0.3, r * 0.3), CREMA, None, w=5)


def avion(c, x, y, s=1.0, col=CREMA, rot=0.0, estela=True):
    """avión de papel; (x, y) = centro"""
    T = lambda pts: P(pts, x, y, s, rot)
    pieza(c, T([(-110, 10), (120, -50), (-20, 50)]), col, (6, 6), w=6)
    pieza(c, T([(-20, 50), (120, -50), (-30, 90)]), darker(col, 0.86), None, w=6)
    c.line(T([(-20, 50), (120, -50)]), 4, (2, 2), smooth=False)
    if estela:
        for k in range(5):
            u0 = k / 5
            c.line(T([(-150 - 260 * u0, 40 + 50 * u0), (-190 - 260 * u0, 54 + 50 * u0)]), 5, (2, 2), smooth=False)


def ojo(c, x, y, r=130, mirada=(0.25, 0.1)):
    """ojo vigilante; (x, y) = centro"""
    t = np.linspace(0, 2 * np.pi, 120, endpoint=False)
    pts = np.stack([x + np.cos(t) * r, y + np.sin(t) * r * 0.55 * np.where(np.sin(t) < 0, 1.0, 0.9)], 1)
    pieza(c, pts, CREMA, (0, 10), w=8)
    m = c.mask(pts)
    ix, iy = x + mirada[0] * r * 0.5, y + mirada[1] * r * 0.4
    c.fill(c.mask(E(ix, iy, r * 0.42, r * 0.42)) * m, AZUL, slop=1, knock=False)
    c.fill(c.mask(E(ix, iy, r * 0.2, r * 0.2)) * m, OSCURO, slop=0.5, knock=False)
    c.fill(c.mask(E(ix - r * 0.1, iy - r * 0.1, r * 0.07, r * 0.07)) * m, WHITE, slop=0, knock=False)
    c.outline(pts, 8, 0.3)
    for k in range(5):
        a = np.deg2rad(200 + k * 35)
        c.line([(x + np.cos(a) * r * 0.95, y + np.sin(a) * r * 0.62), (x + np.cos(a) * r * 1.18, y + np.sin(a) * r * 0.85)], 5, (2, 3), smooth=False)


def caja(c, x, y, w=90, col='#d8b07a'):
    """(x, y) = centro"""
    pieza(c, R(x - w / 2, y - w * 0.4, x + w / 2, y + w * 0.4, 6), col, (8, 8), w=5.5)
    c.line([(x - w / 2, y - w * 0.1), (x + w / 2, y - w * 0.1)], 3.5, (1, 1), smooth=False)
    c.line([(x, y - w * 0.4), (x, y + w * 0.4)], 3.5, (1, 1), smooth=False)


def carrito(c, x, y, s=1.0, cajas=True):
    """carrito de compras; y = piso"""
    sombra(c, x, y + 4, 150 * s, 18 * s)
    if cajas:
        caja(c, x - 40 * s, y - 250 * s, 90 * s, ORANGE)
        caja(c, x + 55 * s, y - 240 * s, 74 * s, '#d8b07a')
    c.line([(x - 190 * s, y - 250 * s), (x - 140 * s, y - 250 * s), (x - 105 * s, y - 90 * s), (x + 120 * s, y - 90 * s)], 9 * s, (2, 2), smooth=False)
    pts = [(x - 130 * s, y - 210 * s), (x + 150 * s, y - 210 * s), (x + 120 * s, y - 100 * s), (x - 105 * s, y - 100 * s)]
    c.outline(pts, 9 * s, 0.2, smooth=False)
    for k in range(1, 4):
        xx = x - 130 * s + k * 70 * s
        c.line([(xx, y - 208 * s), (xx - 8 * s, y - 102 * s)], 4 * s, (1, 1), smooth=False)
    for wx in (-80, 90):
        pieza(c, E(x + wx * s, y - 30 * s, 26 * s, 26 * s), OSCURO, None, w=5)


def camara(c, x, y, s=1.0):
    """cámara de video; (x, y) = centro del cuerpo"""
    for ox in (-70, 10):
        pieza(c, E(x + ox * s, y - 105 * s, 44 * s, 44 * s), GRIS_C, (6, 6), w=6)
        c.dot(x + ox * s, y - 105 * s, 7 * s)
    pieza(c, R(x - 120 * s, y - 70 * s, x + 60 * s, y + 70 * s, 18 * s), OSCURO, (10, 10), w=7)
    pieza(c, [(x + 60 * s, y - 20 * s), (x + 140 * s, y - 60 * s), (x + 140 * s, y + 60 * s), (x + 60 * s, y + 20 * s)], GRIS_O, (6, 6), w=6)
    pieza(c, E(x - 90 * s, y - 40 * s, 12 * s, 12 * s), RED, None, w=4)


def megafono(c, x, y, s=1.0, rot=15):
    T = lambda pts: P(pts, x, y, s, rot)
    pieza(c, T(R(-70, 30, -40, 100, 8)), OSCURO, None, w=5)
    pieza(c, T(R(-130, -36, -84, 36, 10)), GRIS_C, (4, 4), w=6)
    pieza(c, T([(-90, -40), (60, -110), (60, 110), (-90, 40)]), RED, (12, 12), w=7)
    pieza(c, T(E(60, 0, 26, 110)), '#c23b2e', None, w=6)
    for a in (-25, 0, 25):
        t = np.deg2rad(a)
        c.line(T([(110 + 10 * np.cos(t), 120 * np.sin(t)), (160 + 30 * np.cos(t), 170 * np.sin(t))]), 6, (2, 3), smooth=False)


def cuadro(c, x, y, w=220, h=170):
    """imagen (montaña y sol); (x, y) = centro"""
    pieza(c, R(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 14), CREMA, (8, 10), w=7)
    m = c.mask(R(x - w / 2 + 16, y - h / 2 + 16, x + w / 2 - 16, y + h / 2 - 16, 8))
    c.fill(m, AZUL_C, slop=0, knock=False)
    c.fill(c.mask([(x - w / 2 + 16, y + h / 2 - 16), (x - w * 0.12, y - h * 0.08), (x + w * 0.12, y + h * 0.16), (x + w * 0.26, y),
                   (x + w / 2 - 16, y + h / 2 - 16)]) * m, VERDE, slop=1, knock=False)
    c.fill(c.mask(E(x + w * 0.22, y - h * 0.18, 18, 18)) * m, YELLOW, slop=0, knock=False)
    c.outline(R(x - w / 2 + 16, y - h / 2 + 16, x + w / 2 - 16, y + h / 2 - 16, 8), 4, 0.2)


def escudo(c, x, y, s=1.0):
    """(x, y) = centro"""
    pts = [(x - 100 * s, y - 120 * s), (x, y - 150 * s), (x + 100 * s, y - 120 * s), (x + 92 * s, y + 10 * s), (x, y + 140 * s), (x - 92 * s, y + 10 * s)]
    pieza(c, pts, MENTA, (16, 16), w=8)
    chulo(c, x + 4 * s, y - 4 * s, 50 * s, col=CREMA, w=22 * s)


def etiqueta(c, x, y, texto='$', s=1.0, rot=-12, col=YELLOW):
    T = lambda pts: P(pts, x, y, s, rot)
    pieza(c, T([(-120, -55), (60, -55), (120, 0), (60, 55), (-120, 55)]), col, (8, 10), w=6.5)
    pieza(c, T(E(70, 0, 12, 12)), CREMA, None, w=4)
    nota(c, texto, *T([(-30, 22)])[0], 64 * s, rot=rot)


def documento(c, x, y, w=200, h=250, lineas=5, chulo_ok=False, rot=0.0):
    """(x, y) = centro"""
    T = lambda pts: P(pts, x, y, 1, rot)
    pieza(c, T([(-w / 2, -h / 2), (w / 2 - 50, -h / 2), (w / 2, -h / 2 + 50), (w / 2, h / 2), (-w / 2, h / 2)]), CREMA, (10, 12), w=6.5)
    c.line(T([(w / 2 - 50, -h / 2), (w / 2 - 50, -h / 2 + 50), (w / 2, -h / 2 + 50)]), 4.5, (1, 1), smooth=False)
    for k in range(lineas):
        yy = -h / 2 + 70 + k * (h - 100) / max(1, lineas - 1) * 0.8
        c.line(T([(-w / 2 + 28, yy), (w / 2 - 30 - (60 if k == lineas - 1 else 0), yy)]), 4, (2, 2), smooth=False)
    if chulo_ok: chulo(c, *T([(w * 0.25, h * 0.32)])[0], 42)


def perfil(c, x, y, w=250, h=150, col=PINK):
    """tarjeta de perfil; (x, y) = centro"""
    pieza(c, R(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 20), CREMA, (8, 10), w=6.5)
    pieza(c, E(x - w / 2 + 62, y, 40, 40), col, None, w=5)
    c.face(x - w / 2 + 62, y + 4, 44, 'smile', blush=False)
    for k, L in enumerate((0.9, 0.7, 0.8)):
        c.line([(x - w / 2 + 120, y - 34 + k * 32), (x - w / 2 + 120 + (w - 150) * L, y - 34 + k * 32)], 5, (2, 2), smooth=False)


def buscador(c, x, y, w=440, h=90):
    """barra de búsqueda; (x, y) = centro"""
    pieza(c, R(x - w / 2, y - h / 2, x + w / 2, y + h / 2, h / 2), CREMA, (8, 10), w=6.5)
    lupa(c, x + w / 2 - 60, y - 6, 18, rot=-45)
    c.line([(x - w / 2 + 40, y), (x + w / 2 - 120, y)], 5, (2, 2), smooth=False)


def diana(c, x, y, r=130):
    """(x, y) = centro"""
    for k, col in enumerate((RED, CREMA, RED, CREMA, RED)):
        rr = r * (1 - k * 0.19)
        c.fill(E(x, y, rr, rr), col, slop=1.5, knock=True)
        c.outline(E(x, y, rr, rr), 6 if k == 0 else 4, 0.3)
    c.line([(x + r * 1.4, y - r * 1.0), (x + 8, y - 6)], 9, (2, 2), smooth=False)
    pieza(c, [(x + r * 1.4, y - r * 1.0), (x + r * 1.55, y - r * 1.25), (x + r * 1.7, y - r * 1.05), (x + r * 1.55, y - r * 0.88)], YELLOW, None, w=5)


def lista(c, x, y, w=230, h=290, items=3):
    """lista de tareas en tabla; (x, y) = centro"""
    pieza(c, R(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 16), CAFE_C, (10, 12), w=6.5)
    pieza(c, R(x - w / 2 + 18, y - h / 2 + 30, x + w / 2 - 18, y + h / 2 - 18, 8), CREMA, None, w=5)
    pieza(c, R(x - 50, y - h / 2 - 16, x + 50, y - h / 2 + 22, 8), GRIS, None, w=5)
    for k in range(items):
        yy = y - h / 2 + 90 + k * 62
        pieza(c, R(x - w / 2 + 40, yy - 18, x - w / 2 + 76, yy + 18, 6), CREMA, None, w=4)
        c.line([(x - w / 2 + 96, yy), (x + w / 2 - 40, yy)], 5, (2, 2), smooth=False)


def boton(c, x, y, w=380, h=110, texto='APROBAR', col=VERDE):
    pieza(c, R(x - w / 2, y - h / 2, x + w / 2, y + h / 2, h / 2), col, (8, 12), w=7)
    titulo(c, texto, x, y + h * 0.2, h * 0.5, fill=CREMA, dcol=darker(col, 0.6))


def luna(c, x, y, r=80):
    m = c.mask(E(x, y, r, r)) * (1 - c.mask(E(x + r * 0.45, y - r * 0.25, r * 0.85, r * 0.85)))
    c.fill(m, YELLOW, slop=1)
    c.outline(E(x, y, r, r, a0=60, a1=290), 6, 0.2)


def ventana_noche(c, x, y, w=420, h=330):
    """ventana con cielo de noche, luna y estrellas; (x, y) = centro"""
    pieza(c, R(x - w / 2 - 18, y - h / 2 - 18, x + w / 2 + 18, y + h / 2 + 18, 16), CAFE_C, (8, 10), w=7)
    m = c.mask(R(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 8))
    c.fill(m, '#34407a', slop=0, knock=False)
    luna(c, x + w * 0.22, y - h * 0.12, 60)
    for (sx, sy) in ((-0.3, -0.25), (-0.1, 0.15), (-0.35, 0.25), (0.05, -0.32)):
        c.sparkle(x + sx * w, y + sy * h, 16, YELLOW)
    c.line([(x, y - h / 2), (x, y + h / 2)], 8, (2, 2), smooth=False)
    c.line([(x - w / 2, y), (x + w / 2, y)], 8, (2, 2), smooth=False)


def cama(c, x, y, s=1.0, mood='sleepy', camisa=AZUL):
    """cama con alguien durmiendo; y = piso"""
    sombra(c, x, y + 4, 280 * s, 22 * s)
    pieza(c, R(x - 280 * s, y - 230 * s, x - 240 * s, y, 8), CAFE, (6, 6), w=6)
    pieza(c, R(x + 240 * s, y - 150 * s, x + 280 * s, y, 8), CAFE, (6, 6), w=6)
    pieza(c, R(x - 250 * s, y - 120 * s, x + 250 * s, y - 50 * s, 12), CAFE_C, (8, 8), w=6)
    pieza(c, E(x - 160 * s, y - 150 * s, 70 * s, 34 * s), CREMA, (6, 6), w=6)
    pieza(c, E(x - 150 * s, y - 190 * s, 52 * s, 52 * s), PIEL, (8, 8), w=6)
    pieza(c, [(x - 200 * s, y - 210 * s), (x - 170 * s, y - 245 * s), (x - 110 * s, y - 240 * s), (x - 100 * s, y - 205 * s), (x - 150 * s, y - 225 * s)], OSCURO, None, w=5)
    c.face(x - 150 * s, y - 180 * s, 64 * s, mood, blush=False)
    pieza(c, [(x - 110 * s, y - 175 * s), (x + 250 * s, y - 165 * s), (x + 255 * s, y - 100 * s), (x - 110 * s, y - 110 * s)], camisa, (10, 10), w=6.5)
    for k in range(3):
        nota(c, 'z', x - 70 * s + k * 40 * s, y - 260 * s - k * 46 * s, (40 + 14 * k) * s, rot=-12)


def telefono(c, x, y, s=1.0, col=VERDE):
    """auricular sonando; (x, y) = centro"""
    pts = [(x - 90 * s, y - 60 * s), (x - 50 * s, y - 95 * s), (x - 20 * s, y - 55 * s), (x - 45 * s, y - 25 * s), (x + 25 * s, y + 45 * s),
           (x + 55 * s, y + 20 * s), (x + 95 * s, y + 50 * s), (x + 60 * s, y + 90 * s), (x - 70 * s, y + 10 * s)]
    pieza(c, pts, col, (8, 8), w=7)
    for rr in (120, 160):
        c.line(E(x - 10 * s, y - 10 * s, rr * s, rr * s, a0=-80, a1=-10), 6, (2, 3))


def nube_trabajo(c, x, y, r=150):
    """nube con una laptop encima; (x, y) = centro de la nube"""
    c.puff(x, y, r, fx=False, bumps=7)
    laptop(c, x, y - r * 0.95, r * 1.1, texto='')


def humano_cansado(c, x, y, s=0.6, camisa='#a9a39c'):
    return persona(c, x, y, s, camisa=camisa, pelo=GRIS_O, mood='sleepy', brazos=((-0.8, 0.45), (0.8, 0.45)))


def flecha_grande(c, x0, y0, x1, y1, col=VERDE):
    a = math.atan2(y1 - y0, x1 - x0); L = math.hypot(x1 - x0, y1 - y0)
    pts = P([(0, -22), (L - 70, -22), (L - 70, -60), (L, 0), (L - 70, 60), (L - 70, 22), (0, 22)], x0, y0, 1, -math.degrees(a))
    pieza(c, pts, col, (6, 8), w=6.5)


def calendario_mes(c, x, y, w=320, h=300, marcas=7):
    """calendario del mes con días marcados; (x, y) = centro"""
    pieza(c, R(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 16), CREMA, (12, 14), w=7)
    pieza(c, R(x - w / 2, y - h / 2, x + w / 2, y - h / 2 + 64, (16, 16, 0, 0)), RED, (6, 8), w=7)
    rr = np.random.default_rng(9)
    marcadas = set(rr.choice(20, marcas, replace=False).tolist())
    for k in range(20):
        cx = x - w / 2 + 34 + (k % 5) * (w - 68) / 4; cy = y - h / 2 + 100 + (k // 5) * 48
        if k in marcadas: chulo(c, cx, cy, 15, w=9)
        else: c.dot(cx, cy, 4)


def figura_plastilina(c, x, y, s=1.0):
    """muñeco de plastilina sobre una base; y = piso"""
    pieza(c, R(x - 110 * s, y - 50 * s, x + 110 * s, y, 12 * s), GRIS_C, (6, 8), w=6)
    pieza(c, E(x, y - 140 * s, 70 * s, 92 * s), ORANGE, (14, 14), w=7)
    pieza(c, E(x, y - 270 * s, 62 * s, 58 * s), '#f2a35e', (10, 10), w=7)
    for sx in (-1, 1):
        c.line([(x + sx * 60 * s, y - 160 * s), (x + sx * 110 * s, y - 210 * s)], 16 * s, (3, 3))
    c.face(x, y - 262 * s, 80 * s, 'happy')
    for (px, py) in ((-30, -120), (25, -150), (0, -95)):
        c.dot(x + px * s, y + py * s, 4 * s)
