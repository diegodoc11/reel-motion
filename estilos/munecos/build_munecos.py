# -*- coding: utf-8 -*-
# =====================================================================================================
#  reel-motion · PLANTILLA ESTILO MUÑECOS  ("edítalo con reel-motion estilo muñecos")
#  Dibujo animado a mano (motor claude-drawing, look "cartoon"): cada frase es una hoja de dibujo; cada cosa entra en
#  el segundo de su palabra (boceto en lápiz azul -> tinta y color plano con sombra dura) y las líneas "hierven".
#  Objetos y personas con carita, títulos en Poppins. Presentador chico abajo a la derecha y subtítulo fantasma.
#  Las escenas van AQUÍ MISMO (función tomas(), en Python); los dibujos están en estilos/munecos/cosas.py y cosas2.py.
#     python build_munecos.py --guion        el guion con el segundo de cada frase
#     python build_munecos.py --revisar      hoja con el dibujo final de cada toma (rápido, sin video)
#     python build_munecos.py                dibujo animado + subtítulos + audio + borrador + hojas + copia liviana
#     python build_munecos.py --componer     sin volver a dibujar
#  El ejemplo es el reel ERA (77 s): "13 años del caballo al carro… ¿cuánto falta para que todos usemos IA?"
# =====================================================================================================
import os
import sys
import time

P = os.path.dirname(os.path.abspath(__file__))
_sk = os.path.join(P, '_work', 'skill.txt')
SKILL = open(_sk, encoding='utf-8').read().strip() if os.path.exists(_sk) else os.path.expanduser('~/.claude/skills/reel-motion')
sys.path.insert(0, os.path.join(SKILL, 'estilos')); sys.path.insert(0, os.path.join(SKILL, 'estilos', 'munecos'))
import componer as C  # noqa: E402
import cd  # noqa: E402
import cosas as K  # noqa: E402
from cosas import RED, YELLOW, ORANGE, AZUL, VERDE, LILA, GRIS_C, CREMA, OSCURO  # noqa: E402

CORRECCIONES = {'i': 'IA', 'adaptó': 'adoptó', 'cassette': 'casete', 'cassettes': 'casetes'}
ROJAS = ('Trece', '1913,', 'smartphone.', 'siete', 'seis', 'tres', 'dos.', 'nietos.', 'natural.', 'teclados',
         'casetes', 'clientes', 'casete.', 'agentes', 'moda.', 'triunfen', 'quiebren.', 'ERA')
r = C.Reel(P, estilo='munecos', correcciones=CORRECCIONES, rojas=ROJAS, musica='auto', volumen_musica=0.28, inicio_musica=24.0)
if '--guion' in sys.argv: r.guion(); sys.exit()
ft = r.ft

# ============================== TOMAS: dónde empieza cada hoja (edita) ==============================
ESC = dict(A=0.0, B=ft('en', despues=ft('1913')) - 0.1, C=ft('Saltemos') - 0.12, D=ft('el', despues=ft('tenido')) - 0.12,
           E=ft('Desde ese punto') - 0.12, F=ft('ChatGPT') - 0.2, G=ft('llevamos') - 0.12, H=ft('¿Cuántos') - 0.12,
           I=ft('esto') + 0.5, J1=ft('Solo miremos') - 0.12, J2=ft('Hoy') - 0.12, K=ft('Porque') - 0.12,
           L=ft('natural') - 0.38, M=ft('muchacho') - 0.4, N=ft('niños', despues=ft('Walkman')) - 0.35,
           O=ft('El negocio') - 0.12, P=ft('instalar') - 0.12, Q=ft('Será') - 0.12, R=ft('Comenta') + 0.02)
NOMBRES = list(ESC)


def kid(x, y=1100, s=0.66, **kw):
    kw.setdefault('camisa', RED); kw.setdefault('gorra', YELLOW)
    return lambda c: K.persona(c, x, y, s, **kw)


def preguntas(pts, size=110):
    return lambda c: [K.titulo(c, '?', x, y, size, fill=CREMA, dcol=AZUL, rot=rot) for (x, y, rot) in pts]


def tomas():
    T = {}

    def A(e):
        e.paso(ft('Trece'), lambda c: K.titulo(c, '13 AÑOS', 540, 330, 150), 'pop')
        e.paso(ft('caballo'), lambda c: K.caballo(c, 280, 920, 0.9))
        e.paso(ft('movernos', despues=ft('caballo')), lambda c: K.flecha(c, [(470, 720), (560, 700), (640, 720)]))
        e.paso(ft('carro'), lambda c: K.carro(c, 820, 920, 0.82))
        e.paso(ft('1900'), lambda c: K.nota(c, '1900', 280, 1040, 80))
        e.paso(ft('1913'), lambda c: K.nota(c, '1913', 820, 1040, 80))
    T['A'] = A

    def B(e):
        e.paso(ft('época'), lambda c: K.caracol(c, 470, 1010, 1.3, 'sleepy'))
        e.paso(ft('movían'), lambda c: K.reloj(c, 820, 560, 115, (4, 0), 'sleepy'))
        e.paso(ft('mucho', despues=ft('movían')), lambda c: [K.nota(c, 'z', 760 + 40 * k, 400 - 46 * k, 56 + 16 * k, rot=-10) for k in range(3)])
        e.paso(ft('despacio'), lambda c: K.titulo(c, 'MÁS DESPACIO', 540, 300, 104, fill=CREMA, dcol=AZUL), 'pop')
    T['B'] = B

    def C(e):
        def salto(c):
            import numpy as np
            for k in range(9):
                u0, u1 = k / 9, k / 9 + 0.06
                pts = [(110 + 300 * u, 1090 - 560 * u + 330 * u * u) for u in np.linspace(u0, u1, 4)]
                c.line(pts, 6, taper=(2, 2))
            c.puff(120, 1080, 46, fx=False, curl=False); c.puff(190, 1092, 32, fx=False, curl=False)
            K.persona(c, 430, 800, 1.0, camisa=AZUL, mood='happy', brazos=((-0.75, -0.95), (0.75, -0.95)))
            c.speed_lines((330, 830), (530, 830), angle=-90, n=5, length=(50, 110), width=5, fx=False)
        e.paso(ft('Saltemos'), salto)
        e.paso(ft('segundo'), lambda c: K.titulo(c, '2º SALTO', 540, 300, 128), 'pop')
        def zas(c):
            K.rayo(c, 830, 700, 1.25)
            c.burst(830, 980, 150, 70, ORANGE, spikes=12, fx=False)
            K.titulo(c, '¡ZAS!', 830, 1004, 64, fill=CREMA, dcol=RED)
        e.paso(ft('tecnológico'), zas)
    T['C'] = C

    def D(e):
        e.paso(ft('smartphone'), lambda c: K.celular(c, 540, 720, 300, 520, 'wow'))
        e.paso(ft('2007'), lambda c: K.titulo(c, '2007', 540, 320, 160), 'pop')
        e.paso(ft('aparece'), lambda c: (K.chispas(c, [(310, 520), (790, 560), (300, 900), (800, 930)], 30),
                                         c.pop_lines(540, 720, 300, 360, [20, 160, 200, 340], width=6, fx=False)))
        e.paso(ft('iPhone'), lambda c: K.nota(c, '¡el primer iPhone!', 540, 1080, 76))
    T['D'] = D

    def E_(e):
        def linea(c):
            c.line([(120, 1060), (960, 1060)], 6, taper=(4, 4))
            c.line([(940, 1040), (962, 1060), (940, 1080)], 6, taper=(2, 2), smooth=False)
            K.nota(c, '2007', 150, 1040, 64, anchor='l')
        e.paso(ft('punto'), linea)
        e.paso(ft('mundo', despues=ESC['E']), lambda c: K.mundo(c, 540, 720, 200, 'happy'))
        def celus(c):
            import numpy as np
            for k, a in enumerate((155, 118, 62, 25, 205, 335)):
                t = np.deg2rad(a)
                K.celular(c, 540 + np.cos(t) * 320, 720 - np.sin(t) * 250, 92, 160, 'happy', rot=(a - 90) * 0.25)
        e.paso(ft('smartphone', despues=ESC['E']), celus)
        e.paso(ft('siete'), lambda c: (K.titulo(c, '7 AÑOS', 540, 300, 150), K.nota(c, '2014', 930, 1040, 64, anchor='r')), 'pop')
    T['E'] = E_

    def F(e):
        e.paso(ft('ChatGPT'), lambda c: K.burbuja_ia(c, 640, 640, 360, 250, 'happy'))
        e.paso(ft('creciendo'), lambda c: (K.llamas(c, 455, 660, 200, 190),
                                           c.speed_lines((380, 560), (380, 760), angle=180, n=5, length=(90, 170), width=5, fx=False)))
        e.paso(ft('seis'), lambda c: K.titulo(c, '×6', 540, 330, 190), 'pop')
        e.paso(ft('iPhone', despues=ESC['F']), lambda c: (K.celular(c, 210, 960, 150, 270, 'sleepy'), K.nota(c, 'iPhone', 210, 1125, 56)))
    T['F'] = F

    def G(e):
        st = {}
        e.paso(ft('llevamos'), lambda c: st.update(v=K.torta(c, 540, 1060, 1.15)))
        e.paso(ft('tres'), lambda c: [K.vela(c, x, y, 1.0) for (x, y) in st['v']])
        e.paso(ft('años', despues=ft('tres')), lambda c: K.titulo(c, '3 AÑOS', 540, 330, 150), 'pop')
        e.paso(ft('generativa'), lambda c: (K.chispas(c, [(250, 560), (830, 520)], 32), K.nota(c, 'de IA generativa', 540, 470, 64)))
    T['G'] = G

    def H(e):
        e.paso(ft('¿Cuántos'), lambda c: K.calendario(c, 290, 560, 260, 290, '?'))
        e.paso(ft('crees'), preguntas([(470, 360, 12), (560, 300, -10)], 90))
        e.paso(ft('mundo', despues=ESC['H']), lambda c: K.mundo(c, 720, 660, 170, 'wow'))
        e.paso(ft('IA', despues=ESC['H']), lambda c: K.burbuja_ia(c, 880, 410, 190, 130, 'happy', etiqueta=None))
        e.paso(ft('dos'), lambda c: (c.burst(540, 1030, 360, 125, RED, spikes=16, fx=False), K.titulo(c, '2 AÑOS', 540, 1078, 140, fill=YELLOW, dcol=OSCURO)), 'pop')
    T['H'] = H

    def I(e):
        def abuelo(c):
            K.persona(c, 230, 1100, 0.95, camisa=LILA, pelo=GRIS_C, mood='sleepy', brazos=((-0.8, 0.5), (0.7, 0.45)))
            for (x, y, rr) in ((330, 690, 26), (380, 640, 38)):
                c.puff(x, y, rr, fx=False, curl=False)
            c.puff(620, 470, 240, fx=False, bumps=8)
        e.paso(ft('eso', despues=ft('esto')), abuelo)
        e.paso(ft('usarán'), lambda c: (K.nota(c, '"Eso lo usarán', 620, 450, 66), K.nota(c, 'mis nietos..."', 620, 530, 66)))
        e.paso(ft('nietos'), lambda c: K.equis(c, 620, 480, 200, w=34))
    T['I'] = I

    def J1(e):
        e.paso(ft('nivel'), lambda c: K.medidor(c, 470, 700, 250, 0.93))
        e.paso(ft('adopción'), lambda c: K.titulo(c, 'ADOPCIÓN', 540, 320, 120), 'pop')
        e.paso(ft('tienen'), kid(860, 1100, 0.88))
    T['J1'] = J1

    def J2(e):
        e.paso(ft('niño', despues=ESC['J2']), kid(185, 1100, 0.9))
        e.paso(ft('8'), lambda c: K.titulo(c, '8 AÑOS', 560, 300, 140), 'pop')
        e.paso(ft('pregúntale'), lambda c: K.globo_texto(c, 660, 530, 580, 150, 'Pregúntale a Google', 'izq', 58))
        e.paso(ft('Google'), lambda c: K.equis(c, 660, 530, 95, w=26))
        e.paso(ft('pregúntale', despues=ft('Google')), lambda c: K.globo_texto(c, 660, 790, 580, 150, 'Pregúntale a ChatGPT', 'izq', 58))
        e.paso(ft('ChatGPT', despues=ft('Google')), lambda c: K.chulo(c, 960, 760, 58))
    T['J2'] = J2

    def K_(e):
        def regla(c):
            K.pieza(c, K.R(90, 470, 150, 1100, 10), '#f3e1b8', (6, 6), w=6)
            for k in range(13):
                y = 1080 - k * 48
                c.line([(90, y), (90 + (40 if k % 2 == 0 else 24), y)], 3.5, (1, 1), smooth=False)
            K.persona(c, 330, 1100, 0.98, camisa=RED, gorra=YELLOW, mood='happy', brazos=((-0.85, 0.2), (0.6, -0.6)))
            K.flecha(c, [(200, 760), (200, 600)], w=6, head=26)
        e.paso(ft('creció'), regla)
        e.paso(ft('dudas'), preguntas([(530, 560, 10), (620, 470, -8)], 92))
        e.paso(ft('preguntas', despues=ft('dudas')), preguntas([(560, 700, -12), (680, 640, 14)], 80))
        e.paso(ft('ChatGPT', despues=ESC['K']), lambda c: K.burbuja_ia(c, 850, 560, 300, 210, 'happy'))
        e.paso(ft('Google', despues=ESC['K']), lambda c: (K.lupa(c, 820, 960, 70), K.equis(c, 820, 960, 85, w=24)))
    T['K'] = K_

    def L(e):
        e.base(lambda c: K.persona(c, 300, 1100, 0.86, camisa=RED, gorra=YELLOW, gafas=True, mood='smile', brazos=((-0.85, 0.2), (0.85, -0.7))))
        e.paso(ft('natural'), lambda c: K.titulo(c, 'NATURAL', 540, 300, 128), 'pop')
        e.paso(ft('entender'), preguntas([(300, 590, 8)], 100))
        e.paso(ft('teclados'), lambda c: (K.teclado(c, 760, 800, 400, 150, 'wow', rot=-8),
                                          c.pop_lines(760, 800, 250, 300, [30, 150, 210, 330], width=6, fx=False)))
    T['L'] = L

    def M(e):
        e.paso(ft('muchacho'), lambda c: K.persona(c, 280, 1100, 0.92, camisa=VERDE, pelo=OSCURO, mood='smile', audifonos=True,
                                                    brazos=((-0.85, 0.25), (0.85, 0.2))))
        e.paso(ft('14'), lambda c: K.titulo(c, '14 AÑOS', 560, 300, 140), 'pop')
        e.paso(ft('entiende'), preguntas([(290, 560, -8)], 100))
        e.paso(ft('cassettes'), lambda c: K.casete(c, 700, 620, 330, 'sleepy', cinta=True, rot=6))
        e.paso(ft('Walkman'), lambda c: K.walkman(c, 900, 960, 150, rot=10))
    T['M'] = M

    def N(e):
        def nino(c):
            K.persona(c, 150, 1100, 0.74, camisa=RED, gorra=YELLOW, mood='happy', brazos=((-0.8, 0.3), (0.8, -0.3)),
                      mano_der=lambda c, x, y: K.celular(c, x + 6, y - 24, 64, 112, cara=False))
        e.paso(ft('niños', despues=ESC['N']), nino)
        e.paso(ft('normal'), lambda c: K.chulo(c, 160, 640, 56))
        cel = lambda c, x, y: K.celular(c, x + 8, y - 28, 70, 122, cara=False)
        e.paso(ft('clientes'), lambda c: K.persona(c, 395, 1100, 0.88, camisa=AZUL, mood='happy', brazos=((-0.8, 0.3), (0.8, -0.3)), mano_der=cel))
        e.paso(ft('también'), lambda c: K.persona(c, 650, 1100, 0.88, camisa=LILA, estilo_pelo='largo', mood='smile', brazos=((-0.8, 0.3), (0.8, -0.3)), mano_der=cel))
        e.paso(ft('hacer'), lambda c: K.persona(c, 905, 1100, 0.88, camisa=ORANGE, mood='happy', brazos=((-0.8, 0.3), (0.8, -0.3)), mano_der=cel))
    T['N'] = N

    def O(e):
        e.paso(ft('negocio', despues=ESC['O']), lambda c: K.tienda(c, 500, 1090, 470, 450, 'sleepy', telas=True, pared='#e6d3b3'))
        def sin_ia(c):
            K.pieza(c, K.R(310, 420, 690, 500, 14), CREMA, (6, 8), w=6)
            K.nota(c, 'SIN IA', 500, 482, 66, col=RED)
        e.paso(ft('IA', despues=ESC['O']), sin_ia)
        e.paso(ft('sonar'), lambda c: K.nube_lluvia(c, 860, 360, 80))
        e.paso(ft('cassette', despues=ESC['O']), lambda c: K.casete(c, 880, 760, 210, 'sleepy', cinta=True, rot=-8))
    T['O'] = O

    def P_(e):
        e.paso(ft('agentes'), lambda c: K.robot(c, 215, 1100, 0.76))
        e.paso(ft('IA', despues=ESC['P']), lambda c: K.robot(c, 540, 1100, 0.76, col='#a6d0c3'))
        e.paso(ft('reemplazan'), lambda c: K.robot(c, 865, 1100, 0.76, col='#e4b8a8'))
        e.paso(ft('trabajo'), lambda c: K.papeles(c, 540, 650, 6, 0.9))
        e.paso(ft('lento'), lambda c: (K.caracol(c, 220, 650, 0.5, 'sleepy'), K.equis(c, 230, 570, 80, w=20)))
        e.paso(ft('caro'), lambda c: (K.bolsa_dinero(c, 850, 650, 0.6), K.equis(c, 850, 560, 80, w=20)))
        e.paso(ft('hoy', despues=ESC['P']), lambda c: K.titulo(c, 'HOY', 540, 320, 170), 'pop')
    T['P'] = P_

    def Q(e):
        e.paso(ft('separará'), lambda c: [c.line([(540, 380 + 60 * k), (541, 410 + 60 * k)], 7, (2, 2), smooth=False) for k in range(12)])
        e.paso(ft('triunfen'), lambda c: K.tienda(c, 285, 1090, 360, 400, 'happy', corona=True, brillo=True, toldo=(VERDE, CREMA)))
        e.paso(ft('quiebren'), lambda c: (K.tienda(c, 800, 1090, 360, 400, 'wow', grieta=True, telas=True, pared='#d9c7a6', toldo=('#9a8f87', CREMA)),
                                          K.nube_lluvia(c, 800, 470, 85)))
    T['Q'] = Q

    def R_(e):
        e.paso(ft('ERA'), lambda c: K.comentario(c, 540, 420, 880, 240, 'ERA'), 'pop')
        e.paso(ft('envío'), lambda c: (K.sobre(c, 290, 760, 270, 'happy', rot=10),
                                       c.speed_lines((140, 700), (140, 840), angle=180, n=4, length=(60, 120), width=5, fx=False)))
        e.paso(ft('clase'), lambda c: K.laptop(c, 730, 800, 420, 'CLASE'))
        e.paso(ft('instalarlas'), lambda c: (K.nota(c, '¡en tu negocio!', 540, 1100, 72), K.chispas(c, [(250, 1060), (830, 1060)], 26)))
    T['R'] = R_
    return T


class Revisa:
    def __init__(self, c): self.c = c
    def base(self, fn): fn(self.c)
    def paso(self, t, fn, modo='pinta'): fn(self.c)


class Lista:
    """recorre las tomas sin dibujar: solo anota cuándo hay letreros que entran con 'pop' (para el efecto de sonido)"""
    def base(self, fn): pass
    def paso(self, t, fn, modo='pinta'):
        if modo == 'pop': POPS.append(t)


def revisar(solo=None):
    L = cd.Lienzo()
    T = tomas(); imgs, nombres = [], []
    for k, n in enumerate(NOMBRES):
        if solo and n not in solo: continue
        t = time.time(); L.limpiar(100 + k)
        T[n](Revisa(L.c))
        imgs.append(L.fotos()[0][0]); nombres.append(n)
        print(f'{n}: {time.time() - t:.1f}s')
    cd.hoja_revision(imgs, nombres, os.path.join(P, '_work', 'fotos', 'munecos-revision.jpg'))


def dibujar():
    L = cd.Lienzo()
    T = tomas()
    rod = cd.Rodaje(os.path.join(P, 'munecos_raw.mp4'), r.DUR)
    t = time.time()
    for k, n in enumerate(NOMBRES):
        t0 = ESC[n]; t1 = ESC[NOMBRES[k + 1]] if k + 1 < len(NOMBRES) else r.DUR
        e = cd.Escena(L, n, t0, t1, 100 + k)
        T[n](e)
        rod.toma(e, t1)
        print(f'{n} ({t0:5.2f}-{t1:5.2f}s): {len(e.E) - 1} cosas · {time.time() - t:.0f}s')
        POPS.extend(x['t'] for x in e.E[1:] if x['modo'] == 'pop')
    rod.cerrar()
    print(f'dibujo animado listo en {time.time() - t:.0f}s')


POPS = []

if __name__ == '__main__':
    os.makedirs(os.path.join(P, '_work', 'fotos'), exist_ok=True)
    if '--revisar' in sys.argv:
        i = sys.argv.index('--revisar'); solo = sys.argv[i + 1].split(',') if len(sys.argv) > i + 1 else None
        revisar(solo); sys.exit()
    if '--componer' not in sys.argv: dibujar()
    else:
        T = tomas()
        for n in NOMBRES: T[n](Lista())
    r.sfx = [(ESC[k] - 0.05, 'swipe.wav', 0.07) for k in NOMBRES[1:]]
    r.sfx += [(t, 'pop.wav', 0.1) for t in POPS]
    r.subtitulos(fantasma='#A0978A'); r.audio(); r.componer('munecos_raw.mp4'); r.entregar()
