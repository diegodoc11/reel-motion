# -*- coding: utf-8 -*-
# =====================================================================================================
#  reel-motion · KIT del estilo GRÁFICAS (Manim, "animaciones de matemáticas para enseñar con números", look
#  3Blue1Brown). Fondo oscuro con cuadrícula tenue, textos que se ESCRIBEN (Write), contadores que suben,
#  ejes y curvas que se trazan, figuras que se dibujan y se rellenan (DrawBorderThenFill) y objetos que se
#  TRANSFORMAN. Cada cosa entra en el segundo exacto de su palabra (words.json) con un guion de eventos absolutos.
#  Sin LaTeX: todo el texto es Text() con Poppins ExtraBold (recursos/fonts de la skill) registrada aquí.
#  Coordenadas de diseño en píxeles (1080x1920, y hacia abajo) -> P(x, y).
# =====================================================================================================
import json
import os
import unicodedata

import manimpango
import numpy as np
from manim import *  # noqa: F401,F403

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(AQUI))
manimpango.register_font(os.path.join(SKILL, 'recursos', 'fonts', 'poppins-800.ttf'))
config.pixel_width, config.pixel_height = (360, 640) if os.environ.get("MANIM_PREVIA") else (1080, 1920)  # previa rápida
config.frame_height, config.frame_width = 16.0, 9.0
config.frame_rate = 30
FONDO = '#0E1116'
config.background_color = FONDO
AZUL, TEAL, AMARILLO, ROJO, VERDE, MORADO, NARANJA, GRIS = '#58C4DD', '#5CD0B3', '#F7D96F', '#FC6255', '#83C167', '#B189D4', '#FF862F', '#8A8F98'
FUENTE = 'Poppins'
DATOS = json.load(open(os.path.join(SKILL, 'estilos', 'comun', 'figuras.json'), encoding='utf-8'))   # siluetas de las láminas
FPS = 30


def P(x, y):
    """punto de diseño (px, y hacia abajo) -> coordenadas de Manim (unidades, y hacia arriba)."""
    return np.array([(x - 540) / 120.0, (960 - y) / 120.0, 0.0])


def U(v):
    return v / 120.0


def q(x):
    """redondea una duración al cuadro (así el reloj de Manim y el video no se separan)."""
    return max(1, round(x * FPS)) / FPS


# ---------------------------------------------------------------- texto
_REF = {}


def texto(s, alto, color=WHITE, x=None, y=None):
    """texto en Poppins con la ALTURA DE MAYÚSCULA en px (como en los otros estilos)."""
    if 'h' not in _REF:
        _REF['h'] = Text('H', font=FUENTE, font_size=48).height
    t = Text(s, font=FUENTE, font_size=48, color=color)
    t.scale(U(alto) / _REF['h'])
    if x is not None:
        t.move_to(P(x, y))
    return t


def numero_que_sube(objetivo, alto, color, x, y, sufijo='', prefijo=''):
    """contador: devuelve (tracker, mobject que se redibuja). El número sube de 0 al objetivo."""
    tr = ValueTracker(0)
    mob = always_redraw(lambda: texto(f'{prefijo}{int(round(tr.get_value()))}{sufijo}', alto, color, x, y))
    return tr, mob


# ---------------------------------------------------------------- figuras (las mismas siluetas del #4) y gente
def _hsl(hexa):
    import colorsys
    h = hexa.lstrip('#'); r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    return hh, ss, ll


def _vivo(hexa):
    import colorsys
    hh, ss, ll = _hsl(hexa)
    r, g, b = colorsys.hls_to_rgb(hh, min(0.7, max(0.42, ll * 1.15)), min(1, ss * 1.3 + 0.1))
    return '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))


def figura(nombre, x, y, alto):
    """VGroup de polígonos con contorno blanco y relleno de color, centrado en (x, y), de `alto` px."""
    partes = DATOS['figs'][nombre]
    todos = [p for q_ in partes if not q_['sombra'] for p in q_['pts']]
    xs, ys = [p[0] for p in todos], [p[1] for p in todos]
    cx, cy, h = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(ys) - min(ys)
    s = alto / h
    cuenta = {}
    for q_ in partes:
        if q_['tinte'] and not q_['solo']:
            cuenta[q_['tinte']] = cuenta.get(q_['tinte'], 0) + 1
    dom = max(cuenta, key=cuenta.get) if cuenta else None
    g = VGroup()
    for q_ in partes:
        if q_['sombra']:
            continue
        pts = [P(x + (a - cx) * s, y + (b - cy) * s) for a, b in q_['pts']]
        poly = Polygon(*pts)
        xs2, ys2 = [p[0] for p in q_['pts']], [p[1] for p in q_['pts']]
        area = (max(xs2) - min(xs2)) * (max(ys2) - min(ys2))
        if q_['solo']:
            if area < 900:
                poly.set_fill(WHITE, 1).set_stroke(WHITE, 1)
            else:
                poly.set_fill(opacity=0).set_stroke(WHITE, 2.5)
        else:
            t = q_['tono']
            if q_['tinte']:
                fill = _vivo(q_['tinte'])
            elif t < 0.2:
                fill = '#EDEDED'
            elif t >= 0.75:
                fill = '#262A33'
            elif dom:
                fill = interpolate_color(ManimColor(_vivo(dom)), ManimColor('#1b1d24'), min(0.6, max(0.0, (t - 0.3) * 0.6))).to_hex()
            else:
                fill = '#4A505C'
            poly.set_fill(fill, 0.95).set_stroke(WHITE, 2.6)
        g.add(poly)
    return g


def persona(tipo, x, y, r, color):
    """avatar: aro de color con la silueta blanca de perfil recortada al círculo."""
    datos = DATOS['gente'][tipo]
    aro = Circle(radius=U(r)).move_to(P(x, y)).set_fill(FONDO, 1).set_stroke(color, 6)
    s = r / 118.0
    sil = VGroup()
    for parte in datos['partes']:
        pts = [P(x + a * 0.95 * s, y + (b * 0.95 + 4) * s) for a, b in parte]
        try:
            sil.add(Intersection(Polygon(*pts), Circle(radius=U(r) * 0.97).move_to(P(x, y))).set_fill(WHITE, 1).set_stroke(width=0))
        except Exception:
            sil.add(Polygon(*pts).set_fill(WHITE, 1).set_stroke(width=0))
    for linea in datos['oro']:   # los detalles (gafas, gorra, audífonos) en el color del fondo, sobre la silueta blanca
        pts = [P(x + a * 0.95 * s, y + (b * 0.95 + 4) * s) for a, b in linea]
        sil.add(VMobject().set_points_as_corners(pts).set_stroke(FONDO, 3.5).set_fill(opacity=0))
    return VGroup(aro, sil)


def chulo(x, y, r, color=VERDE):
    return VMobject().set_points_as_corners([P(x - r, y), P(x - r * 0.3, y + r * 0.62), P(x + r, y - r * 0.8)]).set_stroke(color, max(6, r * 0.22)).set_fill(opacity=0)


def tachon(x0, x1, y, color=ROJO, w=8):
    return Line(P(x0, y), P(x1, y), color=color, stroke_width=w)


def caja(mob, color, rot=0.0):
    """texto con un rectángulo alrededor (la insignia), opcionalmente girado."""
    g = VGroup(mob, SurroundingRectangle(mob, color=color, buff=U(16), stroke_width=6, corner_radius=U(10)))
    return g.rotate(rot) if rot else g


# ---------------------------------------------------------------- guion: eventos en segundos absolutos del video
def _norm(s):
    s = unicodedata.normalize('NFD', s)
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower().translate({ord(c): None for c in '¿?¡!.,;:"«»()'}).replace(' ', '')


class Guion:
    def __init__(self, scene, tiempos=None):
        # palabras con su segundo y tomas: los escribe build_graficas.py en <proyecto>/_work/tiempos.json
        d = json.load(open(tiempos or os.environ['REEL_TIEMPOS'], encoding='utf-8'))
        self.s, self.W, self.ESC, self.DUR = scene, d['WORDS'], d['ESC'], d['DUR']
        self.ev = []
        self.fijos = []

    def tp(self, frase, despues=0.0, fin=False):
        partes = [_norm(p) for p in frase.split()]
        for i, w in enumerate(self.W):
            if w['s'] < despues - 1e-3:
                continue
            ok = True
            for j, p in enumerate(partes):
                if i + j >= len(self.W):
                    ok = False; break
                a, b = _norm(self.W[i + j]['w']), _norm(self.W[i + j]['r'])
                if not (a == p or b == p or (len(p) >= 4 and (a.startswith(p) or b.startswith(p)))):
                    ok = False; break
            if ok:
                return self.W[i + len(partes) - 1]['e'] if fin else w['s']
        raise SystemExit(f'tp(): no encontré "{frase}" después de {despues}')

    def en(self, t, d, fn):
        """fn() -> lista de animaciones, o (lista, después) con una función que corre al terminar."""
        self.ev.append((max(0.0, t), d, fn))

    def limpiar(self, t):
        """cambio de toma: lo que hay en pantalla sube y se va (0,3 s)."""
        def fn():
            vivos = [m for m in self.s.mobjects if m not in self.fijos]
            return [FadeOut(Group(*vivos), shift=UP * 0.7)] if vivos else []
        self.en(t, 0.3, fn)

    def correr(self):
        ev = sorted(self.ev, key=lambda e: e[0])
        i = 0
        while i < len(ev):
            t = ev[i][0]; j = i + 1
            while j < len(ev) and ev[j][0] - t < 0.07:
                j += 1
            grupo = ev[i:j]
            ahora = self.s.renderer.time
            if t - ahora >= 1 / FPS:
                self.s.wait(q(t - ahora))
            sig = ev[j][0] if j < len(ev) else self.DUR
            rt = q(max(0.1, min(max(g[1] for g in grupo), sig - self.s.renderer.time - 0.02)))
            anims, despues = [], []
            for g in grupo:
                r = g[2]()
                if isinstance(r, tuple):
                    anims += r[0]; despues.append(r[1])
                else:
                    anims += r
            if anims:
                self.s.play(*anims, run_time=rt)
            for f in despues:
                f()
            i = j
        resto = self.DUR - self.s.renderer.time
        if resto >= 1 / FPS:
            self.s.wait(q(resto))


def fondo(scene):
    """cuadrícula tenue de fondo (la hoja de 3Blue1Brown), quieta todo el video."""
    plano = NumberPlane(x_range=[-5, 5, 1], y_range=[-9, 9, 1], x_length=10, y_length=18,
                        background_line_style={'stroke_color': '#3A4A66', 'stroke_width': 1.4, 'stroke_opacity': 0.35},
                        axis_config={'stroke_opacity': 0})
    scene.add(plano)
    return plano
