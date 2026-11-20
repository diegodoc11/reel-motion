# -*- coding: utf-8 -*-
"""reel-motion · motor del estilo MUÑECOS (claude-drawing, look "cartoon": dibujo animado a mano).

Cada toma es UNA hoja de dibujo animado (papel crema, lápiz azul, tinta de pincel, color plano con sombra dura).
Cada cosa se dibuja en el segundo de su palabra: primero aparece su boceto en lápiz azul y enseguida la tinta y el
color. Las líneas "hierven" (se vuelven a calcar 8 veces por segundo, como la animación hecha a mano). Entre tomas
entra una hoja nueva deslizándose sobre la anterior. La voz, el subtítulo fantasma, el presentador recortado y la
música los pone estilos/componer.py.

    L = Lienzo()                       # una sola hoja reutilizada: el papel es idéntico en todas las tomas
    e = Escena(L, 'A', t0, t1, seed)   # hoja nueva
    e.paso(t, lambda c: ..., 'pinta')  # c = Cartoon; 'pinta' (lápiz -> color), 'pop' (crece con rebote), 'fade'
"""
import os
import subprocess
import sys
import time

import numpy as np
from PIL import Image, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
import motores  # noqa: E402
sys.path.insert(0, motores.claude_drawing_lib())          # el motor claude-drawing (MIT): lib/cartoon.py
import cartoon as CT  # noqa: E402
from cartoon import Cartoon  # noqa: E402

FUENTES = os.path.join(os.path.dirname(os.path.dirname(AQUI)), 'recursos', 'fonts')
CT._FONT_CANDIDATES['poppins'] = [(os.path.join(FUENTES, 'poppins-900.woff2'), 0)]
CT._FONT_CANDIDATES['poppins8'] = [(os.path.join(FUENTES, 'poppins-800.ttf'), 0)]
CT._FONT_CANDIDATES['caveat'] = [(os.path.join(FUENTES, 'caveat-700.woff2'), 0)]

W, H, FPS = 1080, 1920, 30
BOIL_FPS = 8                       # las líneas se vuelven a calcar 8 veces por segundo
PENCIL = CT.hexc(CT.PENCIL)
INKC = CT.hexc(CT.INK)
A0, A1 = 0.14, 0.26                # una cosa empieza a dibujarse 0.14 s antes de su palabra y termina 0.26 s después
HOJA = 0.36                        # lo que tarda en entrar la hoja nueva


def ease_out(u):
    return 1 - (1 - u) ** 3


def back_out(u, k=1.9):
    u = u - 1
    return 1 + (k + 1) * u ** 3 + k * u ** 2


class Lienzo:
    """una hoja Cartoon 1080x1920 que se limpia en cada toma (mismo papel, misma semilla de 'hervido')."""

    def __init__(self, seed=11, boil=1.6, nboil=3):
        t = time.time()
        self.c = Cartoon(W, H, seed=seed, boil=boil)
        self.nboil = nboil
        self.warps = [self._prep_warp(k) for k in range(1, nboil + 1)]
        print(f'hoja lista ({time.time() - t:.1f}s)')

    def _prep_warp(self, k):
        c = self.c
        fx, fy = c._field(k, c.boil)
        x = np.clip(c.XX + fx, 0, W - 1.001); y = np.clip(c.YY + fy, 0, H - 1.001)
        x0 = x.astype(np.int32); y0 = y.astype(np.int32)
        return (y0 * W + x0).ravel(), (x - x0).astype(np.float32).ravel(), (y - y0).astype(np.float32).ravel()

    def _warp(self, IA, wp):
        idx, wx, wy = wp
        f = IA.ravel()
        a = f[idx]; b = f[idx + 1]; cc = f[idx + W]; d = f[idx + W + 1]
        return ((a * (1 - wx) + b * wx) * (1 - wy) + (cc * (1 - wx) + d * wx) * wy).reshape(H, W)

    def limpiar(self, seed):
        c = self.c
        c.paint, c.ink, c.pencil, c.cover = {}, {}, {}, {}
        c.created = []; c._all, c._map = None, {}; c.stages = []
        c.rng = np.random.default_rng(seed)

    def capas(self):
        """lo mismo que Cartoon.composite pero devuelve (fondo sin tinta, tinta, lápiz) para hervir solo la tinta."""
        c = self.c
        covers = [(c._prio(g), cv) for g, cv in c.cover.items()]

        def knocked(g, arr, which):
            for pg, cv in covers:
                if c._prio(g) < pg:
                    k = 1 - cv[which]
                    arr = arr * (k[..., None] if arr.ndim == 3 else k)
            return arr

        PC = np.zeros((H, W, 3), np.float32); PA = np.zeros((H, W), np.float32)
        for g in sorted(c.paint, key=lambda g: (c._prio(g), c.created.index(g))):
            pc, pa = knocked(g, c.paint[g][0], 0), knocked(g, c.paint[g][1], 0)
            PC = PC * (1 - pa[..., None]) + pc; PA = PA * (1 - pa) + pa
        IA = np.zeros((H, W), np.float32)
        for g, ia in c.ink.items():
            IA = 1 - (1 - IA) * (1 - knocked(g, ia, 1))
        R = np.zeros((H, W), np.float32)
        for g, rb in c.pencil.items():
            R = 1 - (1 - R) * (1 - rb)
        out = c.paperc * (1 - (R * 0.3)[..., None] * (1 - PENCIL))
        out = out * (1 - PA[..., None]) + PC
        out = out * (1 + (c.grain - 1) * (1 - 0.55 * PA))[..., None]
        return out, IA, R

    def fotos(self):
        base, IA, R = self.capas()
        imgs = []
        for wp in self.warps:
            ia = self._warp(IA, wp)[..., None]
            imgs.append((np.clip(base * (1 - ia) + INKC * ia, 0, 1) * 255).astype(np.uint8))
        return imgs, R


class Escena:
    def __init__(self, L, nombre, t0, t1, seed, corte=False):
        self.L, self.nombre, self.t0, self.t1, self.corte = L, nombre, t0, t1, corte
        L.limpiar(seed)
        self.c = L.c
        imgs, R = L.fotos()
        self.E = [dict(t=t0, imgs=imgs, modo='base', D=None)]
        self.R = R

    def base(self, fn):
        """lo que ya está en la hoja cuando entra (sin animación)"""
        fn(self.c)
        imgs, R = self.L.fotos()
        self.E[0]['imgs'] = imgs; self.R = R

    def paso(self, t, fn, modo='pinta'):
        R0 = self.R
        fn(self.c)
        imgs, R = self.L.fotos()
        D = None
        if modo == 'pinta':
            D = (np.clip((R - R0) / np.maximum(1e-3, 1 - R0), 0, 1) * 255).astype(np.uint8)
            if D.max() < 20: modo = 'fade'; D = None          # sin boceto (letras, notas): aparece con fundido
        self.E.append(dict(t=t, imgs=imgs, modo=modo, D=D))
        self.R = R

    def ventanas(self):
        """[inicio, fin) de la entrada de cada cosa, sin solaparse (si dos palabras van muy juntas, la 2.ª espera)."""
        fin = self.t0
        for e in self.E[1:]:
            s = max(e['t'] - A0, fin)
            f = max(e['t'] + A1, s + 0.16)
            e['s'], e['f'] = s, f
            fin = f
        if len(self.E) > 1 and self.E[-1]['f'] > self.t1 + 0.05:
            print(f'  ojo toma {self.nombre}: la última cosa termina en {self.E[-1]["f"]:.2f}s y la toma acaba en {self.t1:.2f}s')

    def cuadro(self, tau, j):
        E = self.E
        k = 0
        for i in range(1, len(E)):
            if tau >= E[i]['s']: k = i
        if k == 0: return E[0]['imgs'][j]
        e, prev = E[k], E[k - 1]['imgs'][j]
        if tau >= e['f']: return e['imgs'][j]
        u = (tau - e['s']) / max(1e-3, e['f'] - e['s'])
        if e['modo'] == 'pinta':
            boceto = prev.astype(np.float32) * (1 - (e['D'].astype(np.float32) / 255 * 0.9)[..., None] * (1 - PENCIL))
            if u < 0.4:
                v = ease_out(u / 0.4)
                return (prev * (1 - v) + boceto * v).astype(np.uint8)
            v = (u - 0.4) / 0.6
            v = v * v * (3 - 2 * v)
            return (boceto * (1 - v) + e['imgs'][j].astype(np.float32) * v).astype(np.uint8)
        if e['modo'] == 'pop':
            return self._pop(prev, k, j, u)
        v = u * u * (3 - 2 * u)
        return (prev.astype(np.float32) * (1 - v) + e['imgs'][j].astype(np.float32) * v).astype(np.uint8)

    def _pop(self, prev, k, j, u):
        e = self.E[k]
        if 'pm' not in e:
            d = np.abs(e['imgs'][0].astype(np.int16) - self.E[k - 1]['imgs'][0].astype(np.int16)).max(2)
            m = (d > 10).astype(np.float32)
            ys, xs = np.nonzero(m)
            if not len(ys): e['pm'] = None
            else:
                y0, y1, x0, x1 = max(0, ys.min() - 8), min(H, ys.max() + 9), max(0, xs.min() - 8), min(W, xs.max() + 9)
                mm = Image.fromarray((m[y0:y1, x0:x1] * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))
                e['pm'] = (y0, y1, x0, x1, mm)
        if e['pm'] is None: return e['imgs'][j]
        y0, y1, x0, x1, mm = e['pm']
        s = max(0.05, back_out(min(1.0, u)) * 0.45 + 0.55) if u < 1 else 1.0
        h, w = y1 - y0, x1 - x0
        nw, nh = max(2, int(w * s)), max(2, int(h * s))
        spr = Image.fromarray(e['imgs'][j][y0:y1, x0:x1]).resize((nw, nh), Image.BILINEAR)
        msk = mm.resize((nw, nh), Image.BILINEAR)
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        out = Image.fromarray(prev)
        alpha = Image.fromarray((np.asarray(msk, np.float32) * min(1.0, u * 3)).astype(np.uint8))
        out.paste(spr, (cx - nw // 2, cy - nh // 2), alpha)
        return np.asarray(out)


class Rodaje:
    """junta las tomas en un video sin audio (30 fps): hoja que entra + cosas que se dibujan + líneas que hierven."""

    def __init__(self, salida, dur):
        self.salida, self.dur = salida, dur
        self.n = int(round(dur * FPS))
        self.i = 0
        self.prev_last = None
        self.p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                                   '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15', '-pix_fmt', 'yuv420p', salida],
                                  stdin=subprocess.PIPE)
        sh = np.linspace(0, 1, 46, dtype=np.float32)
        self.sombra = (1 - 0.34 * sh ** 2)[None, :, None]             # sombra que la hoja nueva echa sobre la vieja

    def toma(self, esc, t1):
        esc.ventanas()
        while self.i < self.n and self.i / FPS < t1:
            tau = self.i / FPS
            j = int(tau * BOIL_FPS) % len(esc.E[0]['imgs'])
            img = esc.cuadro(tau, j)
            u = (tau - esc.t0) / HOJA
            if self.prev_last is not None and u < 1 and not esc.corte:
                x = int(round(W * (1 - ease_out(max(0.0, u)))))
                if x > 0:
                    img2 = self.prev_last[j].copy()
                    img2[:, x:] = img[:, :W - x]
                    a, b = max(0, x - 46), x
                    if b > a: img2[:, a:b] = (img2[:, a:b].astype(np.float32) * self.sombra[:, 46 - (b - a):]).astype(np.uint8)
                    img = img2
            self.p.stdin.write(np.ascontiguousarray(img).tobytes())
            self.i += 1
        self.prev_last = esc.E[-1]['imgs']

    def cerrar(self):
        while self.i < self.n:
            self.p.stdin.write(np.ascontiguousarray(self.prev_last[0]).tobytes()); self.i += 1
        self.p.stdin.close(); self.p.wait()
        if self.p.returncode: raise SystemExit('falló ffmpeg del dibujo')


def hoja_revision(imgs, nombres, salida, cols=6, ancho=300):
    """estado final de cada toma en una sola imagen (revisión rápida antes de rodar)"""
    from PIL import ImageDraw, ImageFont
    alto = int(ancho * H / W)
    filas = (len(imgs) + cols - 1) // cols
    hoja = Image.new('RGB', (cols * (ancho + 6) + 6, filas * (alto + 6) + 6), 'white')
    f = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf' if os.path.exists(r'C:\Windows\Fonts\segoeuib.ttf') else os.path.join(FUENTES, 'poppins-800.ttf'), 22)
    for k, (im, n) in enumerate(zip(imgs, nombres)):
        t = Image.fromarray(im).resize((ancho, alto), Image.LANCZOS)
        d = ImageDraw.Draw(t); d.rectangle([0, 0, 8 + 13 * len(n), 30], fill='black'); d.text((5, 2), n, font=f, fill='white')
        hoja.paste(t, (6 + (k % cols) * (ancho + 6), 6 + (k // cols) * (alto + 6)))
    hoja.save(salida, quality=88)
    print('hoja de revisión ->', salida)
