# -*- coding: utf-8 -*-
"""Estilo HANDDRAW: pizarra de papel crema donde los íconos de línea de colores se dibujan trazo a trazo, los textos se
escriben letra por letra y cada escena se limpia para la siguiente. Motor: handdraw-skill (MIT, Remotion), que rueda
un project.json. SIN la mano que dibuja (distrae): se esconde desde los propios dibujos, sin tocar el motor.

    import handdraw as HD
    r = HD.Reel(P, correcciones=..., rojas=..., titulo='TU NOMBRE')   # = componer.Reel + escenas de HandDraw
    r.escena(t0)                          # escena nueva (la anterior se desvanece)
    r.dib(id, D.caballo(), cx, cy, t)     # dibujo a línea que se traza solo (D = plantilla/dibujos.py, I = iconos.py)
    r.txt(id, 'TEXTO', cx, cy, fs, t)     # texto que se escribe letra por letra (cy = centro de la tinta)
    r.caja(id, x, y, w, h, t)             # tarjeta / forma
    r.guardar(); r.render_handdraw()      # project.json + fondo animado handdraw_raw.mp4
"""
import hashlib
import json
import os
import sys
import time

from PIL import ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
ESTILOS = os.path.dirname(AQUI)
SKILL = os.path.dirname(ESTILOS)
sys.path.insert(0, AQUI)                                  # pizarra.py mínimo (L, F, C) para reutilizar los dibujos de la pizarra
sys.path.insert(0, ESTILOS)
sys.path.append(os.path.join(SKILL, 'plantilla'))         # dibujos.py del estilo pizarra (los mismos dibujos, recoloreados)
import componer as C  # noqa: E402
import motores as M  # noqa: E402
import iconos as I  # noqa: E402

W, H, FPS = C.W, C.H, C.FPS
TINTA = '#172033'
# la letra con la que HandDraw escribe los textos (Microsoft YaHei en Windows); para medir y centrar
_YAHEI = r'C:\Windows\Fonts\msyhbd.ttc'
FUENTE = _YAHEI if os.path.exists(_YAHEI) else os.path.join(SKILL, 'recursos', 'fonts', 'poppins-800.ttf')
# sin la mano: el motor la pinta como un <svg viewBox="0 0 170 120"> girado -18°; un <style> dentro de cualquier dibujo
# la esconde (el CSS de un SVG en línea vale para toda la página). Sin título, también se esconde la cabecera.
SIN_MANO = 'svg[viewBox="0 0 170 120"][style*="-18deg"]{display:none!important}'
SIN_CABECERA = 'div[style*="letter-spacing: 0.13em"],div[style*="background: rgb(20, 184, 166)"]{display:none!important}'
_FONTS = {}


def ancho_texto(texto, fs):
    """ancho visual (px) de una línea en la letra de HandDraw (bold 700, letter-spacing .045em)."""
    f = _FONTS.get(fs) or _FONTS.setdefault(fs, ImageFont.truetype(FUENTE, fs))
    return f.getlength(texto) + 0.045 * fs * max(0, len(texto) - 1)


def y_para_centro(lineas, fs, cy):
    """y de la caja de texto de HandDraw para que la tinta quede centrada en cy (line-height 1.48)."""
    f = _FONTS.get(fs) or _FONTS.setdefault(fs, ImageFont.truetype(FUENTE, fs))
    b0 = f.getbbox(lineas[0]); b1 = f.getbbox(lineas[-1])
    top = 0.08 * fs + b0[1]; bot = 0.08 * fs + (len(lineas) - 1) * 1.48 * fs + b1[3]
    return cy - (top + bot) / 2


class Reel(C.Reel):
    def __init__(self, P, titulo='', manito=False, **kw):
        super().__init__(P, estilo='handdraw', **kw)
        self.titulo, self.manito = titulo, manito
        self.escenas = []; self.assets = {}
        os.makedirs(os.path.join(P, '_work', 'handdraw', 'assets'), exist_ok=True)

    # ------------------------------------------------------------------------------------------- escenas y piezas
    def escena(self, t0, nombre=None, fade=0.3, camara=None):
        t0 = 0.0 if not self.escenas else round(t0 * FPS) / FPS
        self.escenas.append(dict(t0=t0, nombre=nombre or f'e{len(self.escenas) + 1:02d}', fade=fade, camara=camara, objs=[]))

    def _obj(self, o):
        self.escenas[-1]['objs'].append(o); return o

    def dib(self, idp, icono, cx, cy, t, dur=0.6, escala=1.0, color='azul', acento='rojo', grosor=1.6, centro=True,
            mover=None, rotar=None, crecer=None, aparecer=None, secuencial=True, sonido=True, resaltar=None):
        """dibujo a línea (SVG) centrado en (cx, cy) que se traza solo. mover=(dx, dy, t, dur) · rotar=(grados, t, dur) ·
        crecer=(desde, t, dur) · aparecer=(t, dur) en vez de trazo (fade) · resaltar=t (brillo cálido)."""
        body, w0, h0 = icono
        svg, w0, h0 = I.hd(body, w0, h0, color=color, acento=acento, grosor=grosor, secuencial=secuencial)
        css = ('' if self.manito else SIN_MANO) + ('' if self.titulo else SIN_CABECERA)
        if css: svg = svg.replace('>', f'><style>{css}</style>', 1)
        nombre = f'{idp}_{hashlib.md5(svg.encode()).hexdigest()[:6]}.svg'
        self.assets[nombre] = svg
        w, h = round(w0 * escala), round(h0 * escala)
        x, y = (cx - w / 2, cy - h / 2) if centro else (cx, cy)
        an = []
        if aparecer: an.append(dict(type='fade', t=aparecer[0], dur=aparecer[1]))
        else:
            an.append(dict(type='draw', t=t, dur=dur))
            if sonido: self.sfx.append((t, 'swipe.wav', 0.06))
        if mover: an.append(dict(type='move', t=mover[2], dur=mover[3], x=mover[0], y=mover[1]))
        if rotar: an.append(dict(type='rotate', t=rotar[1], dur=rotar[2], to=rotar[0]))
        if crecer: an.append(dict(type='scale', t=crecer[1], dur=crecer[2], **{'from': crecer[0]}, to=1))
        if resaltar is not None: an.append(dict(type='highlight', t=resaltar, dur=0.3))
        return self._obj(dict(id=idp, kind='svg', asset=nombre, x=round(x), y=round(y), width=w, height=h, anims=an, t=t))

    def txt(self, idp, texto, cx, cy, fs, t, dur=None, centro=True, escribir=True, crecer=None, resaltar=None, mover=None):
        """texto que se escribe letra por letra. cx = centro (o borde izquierdo si centro=False); cy = centro de la tinta."""
        lineas = texto.split('\n')
        y = y_para_centro(lineas, fs, cy)
        wv = max(ancho_texto(l, fs) for l in lineas)
        x = cx - wv / 2 if centro else cx
        if centro and len(lineas) > 1:   # HandDraw alinea a la izquierda: se centra cada línea con espacios al inicio
            sp = ancho_texto('  ', fs) - ancho_texto(' ', fs)
            texto = '\n'.join(' ' * max(0, round((wv - ancho_texto(l, fs)) / 2 / sp)) + l for l in lineas)
        an = []
        if escribir:
            d = dur if dur else min(0.9, max(0.3, 0.045 * len(texto)))
            an.append(dict(type='write', t=t, dur=d))
        if crecer: an.append(dict(type='scale', t=crecer[1], dur=crecer[2], **{'from': crecer[0]}, to=1))
        if resaltar is not None: an.append(dict(type='highlight', t=resaltar, dur=0.3))
        if mover: an.append(dict(type='move', t=mover[2], dur=mover[3], x=mover[0], y=mover[1]))
        if not an: an.append(dict(type='fade', t=t, dur=0.25))
        return self._obj(dict(id=idp, kind='text', text=texto, x=round(x), y=round(y), width=round(wv + fs), height=fs, anims=an, t=t))

    def caja(self, idp, x, y, w, h, t, fill='#ffffff', stroke='#dbe4ee', radius=32, dur=0.35, forma='card', crecer=None,
             label=None, label_color=None, sonido=True):
        an = [dict(type='fade', t=t, dur=dur)]
        if crecer: an.append(dict(type='scale', t=crecer[1], dur=crecer[2], **{'from': crecer[0]}, to=1))
        o = dict(id=idp, kind='shape', shape=forma, x=round(x), y=round(y), width=round(w), height=round(h), fill=fill,
                 stroke=stroke, strokeWidth=4, radius=radius, anims=an, t=t)
        if label: o['label'] = label; o['labelColor'] = label_color or TINTA
        if sonido: self.sfx.append((t, 'pop.wav', 0.07))
        return self._obj(o)

    # ------------------------------------------------------------------------------------------- project.json
    def guardar(self):
        esc = self.escenas
        fins = [e['t0'] for e in esc[1:]] + [self.DUR]
        scenes = []; avisos = []
        for e, t1 in zip(esc, fins):
            dur = round(t1 - e['t0'], 4)
            if dur <= 0.2: raise SystemExit(f'escena {e["nombre"]} dura {dur}s')
            if len(e['objs']) > 8: raise SystemExit(f'escena {e["nombre"]} tiene {len(e["objs"])} piezas (máximo 8 por escena)')
            objs = []
            for o in e['objs']:
                anims = []
                for a in o['anims']:
                    if a['t'] < e['t0'] - 0.15:      # casi siempre = ft() encontró la palabra equivocada (otra más atrás)
                        avisos.append(f'{e["nombre"]}/{o["id"]}: {a["type"]} pedido en {a["t"]:.2f}s, antes de su escena ({e["t0"]:.2f}s)')
                    st = round(max(0.0, a['t'] - e['t0']), 3); d = round(a['dur'], 3)
                    if st >= dur - 0.04:
                        avisos.append(f'{e["nombre"]}/{o["id"]}: {a["type"]} empieza fuera de su escena ({a["t"]:.2f}s)'); st = max(0, dur - 0.3)
                    d = round(min(d, dur - st - 0.001), 3)
                    aa = {k: v for k, v in a.items() if k not in ('t', 'dur')}
                    aa.update(start=st, duration=max(d, 0.04)); anims.append(aa)
                oo = {k: v for k, v in o.items() if k not in ('anims', 't')}; oo['animations'] = anims
                objs.append(oo)
            dr = sorted([(a['start'], a['start'] + a['duration'], o['id']) for o in objs for a in o['animations'] if a['type'] == 'draw'])
            for (a0, a1, i0), (b0, b1, i1) in zip(dr, dr[1:]):
                if b0 < a1 - 0.12: avisos.append(f'{e["nombre"]}: {i0} y {i1} se dibujan a la vez ({e["t0"] + b0:.2f}s)')
            sc = dict(id=e['nombre'], duration=dur, objects=objs)
            if e['fade'] and len(scenes): sc['transition'] = dict(type='fade', duration=min(e['fade'], dur * 0.24))
            if e['camara']: sc['camera'] = e['camara']
            scenes.append(sc)
        proj = dict(version=1, project=dict(title=self.titulo or ' ', width=W, height=H, fps=FPS, background='#fffdf8'), scenes=scenes)
        d = os.path.join(self.P, '_work', 'handdraw')
        for n, svg in self.assets.items():
            open(os.path.join(d, 'assets', n), 'w', encoding='utf-8').write(svg)
        json.dump(proj, open(os.path.join(d, 'project.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        tot = sum(s['duration'] for s in scenes)
        print(f'project.json: {len(scenes)} escenas, {sum(len(s["objects"]) for s in scenes)} piezas, {tot:.2f}s (video {self.DUR:.2f}s)')
        for a in avisos: print('  aviso:', a)
        return proj

    # ------------------------------------------------------------------------------------------- render
    def render_handdraw(self, salida='handdraw_raw.mp4'):
        sk = M.handdraw(); d = os.path.join(self.P, '_work', 'handdraw'); pj = os.path.join(d, 'project.json'); out = os.path.join(self.P, salida)
        cli = os.path.join(sk, 'scripts', 'handdraw.mjs')
        C.run([M.node(), cli, 'validate', pj], cwd=sk)
        t = time.time()
        C.run([M.node(), cli, 'render', pj, '--output', out, '--assets', os.path.join(d, 'assets')], cwd=sk)
        print(f'HandDraw rodó {salida} en {time.time() - t:.0f}s')
        return out
