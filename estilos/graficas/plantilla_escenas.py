# -*- coding: utf-8 -*-
# =====================================================================================================
#  reel-motion · ESCENAS del estilo GRÁFICAS (Manim). Ejemplo: el reel ERA (1:17). Lenguaje de 3Blue1Brown: la línea
#  numérica con un punto que avanza, contadores que suben, curvas de crecimiento, un medidor con aguja, dos curvas
#  que se separan. Las tomas (ESC) y los tiempos los pone build_graficas.py; esto lo rueda él (no se corre solo).
#  g.en(t, dur, fn) = una animación en el segundo t · g.limpiar(ESC['B']) = cambio de toma · tp('frase') = segundo.
# =====================================================================================================
import os
import sys

sys.path.insert(0, os.environ['REEL_MOTION_KIT'])          # estilos/graficas de la skill (lo pone build_graficas.py)
from kit import *  # noqa: F401,F403


def numero_titulo(g, t, num, palabra, x, y, alto, inicio=0, prefijo='', color=AMARILLO, d=0.8):
    """el número sube como contador y la palabra se escribe al lado; devuelve (número final, palabra)."""
    n_fin = texto(f'{prefijo}{num}', alto, color)
    w = texto(palabra, alto, WHITE) if palabra else None
    grupo = VGroup(n_fin, w).arrange(RIGHT, buff=U(alto * 0.35)) if w else VGroup(n_fin)
    grupo.move_to(P(x, y))
    c = n_fin.get_center()
    tr = ValueTracker(inicio)
    mob = always_redraw(lambda: texto(f'{prefijo}{int(round(tr.get_value()))}', alto, color).move_to(c))

    def fn():
        g.s.add(mob)
        an = [tr.animate.set_value(num)]
        if w:
            an.append(Write(w))

        def despues():
            g.s.remove(mob, tr)
            g.s.add(n_fin)
        return an, despues
    g.en(t, d, fn)
    return n_fin, w


def linea_numerica(x0, x1, y, a, b, paso=1, color=GRIS):
    nl = NumberLine(x_range=[a, b, paso], length=U(x1 - x0), color=color, include_tip=True, tip_length=U(22), stroke_width=4,
                    include_numbers=False, tick_size=U(9))
    nl.move_to(P((x0 + x1) / 2, y))
    return nl


class Reel(Scene):
    def construct(self):
        g = Guion(self)
        tp, ESC = g.tp, g.ESC
        g.fijos.append(fondo(self))
        dib = lambda t, m, d=0.9: g.en(t - 0.08, d, lambda: [DrawBorderThenFill(m)])
        esc = lambda t, m, d=0.7: g.en(t - 0.04, d, lambda: [Write(m)])
        sube = lambda t, m, d=0.45: g.en(t - 0.04, d, lambda: [FadeIn(m, shift=UP * 0.25)])
        traza = lambda t, m, d=0.6: g.en(t - 0.04, d, lambda: [Create(m)])
        crece = lambda t, m, d=0.4: g.en(t - 0.04, d, lambda: [GrowFromCenter(m)])

        # ---------------- A · 13 años: del caballo al carro, 1900 → 1913
        numero_titulo(g, tp('Trece'), 13, 'AÑOS', 540, 270, 110)
        dib(tp('caballo'), figura('caballo', 290, 640, 230))
        traza(tp('movernos', tp('caballo')), CurvedArrow(P(440, 520), P(650, 540), angle=-1.1, color=ROJO, stroke_width=6), 0.5)
        dib(tp('carro'), figura('carro', 795, 665, 190))
        nl = linea_numerica(150, 940, 905, 1900, 1913)
        traza(tp('desde', tp('carro')), nl, 0.5)
        x00, x13 = nl.n2p(1900), nl.n2p(1913)
        sube(tp('1900'), texto('1900', 32, WHITE).move_to(x00 + DOWN * U(48)))
        punto = Dot(x00, radius=U(15), color=AMARILLO)
        crece(tp('1900') + 0.15, punto, 0.3)
        g.en(tp('hasta', tp('1900')), 0.6, lambda: [punto.animate.move_to(x13)])
        sube(tp('1913'), texto('1913', 32, WHITE).move_to(x13 + DOWN * U(48)))
        llave = Brace(Line(x00, x13), direction=UP, color=AMARILLO, buff=U(20))
        g.en(tp('1913') + 0.25, 0.4, lambda llave=llave: [GrowFromCenter(llave), FadeIn(texto('13 AÑOS', 30, AMARILLO).next_to(llave, UP, buff=U(8)))])

        # ---------------- B · época más despacio
        g.limpiar(ESC['B'])
        dib(tp('época'), figura('caracol', 330, 690, 180))
        dib(tp('movían'), figura('reloj', 790, 570, 230))
        via = Line(P(140, 960), P(940, 960), color=GRIS, stroke_width=4)
        lento = Dot(P(140, 960), radius=U(13), color=AMARILLO)
        g.en(tp('mucho', tp('movían')) - 0.1, 0.3, lambda: [Create(via), GrowFromCenter(lento)])
        g.en(tp('más', tp('mucho')) - 0.06, 0.6, lambda: [lento.animate(rate_func=linear).move_to(P(300, 960)), Write(texto('MÁS DESPACIO', 72, WHITE, 540, 300))])

        # ---------------- C · el segundo salto
        g.limpiar(ESC['C'])
        nl = linea_numerica(110, 970, 880, 0, 10)
        traza(tp('Saltemos') - 0.02, nl, 0.5)
        sube(tp('Saltemos') + 0.2, texto('1913', 32, WHITE, 150, 935))
        salto = CurvedArrow(P(150, 860), P(900, 860), angle=-1.45, color=AMARILLO, stroke_width=7)
        traza(tp('para', ESC['C']), salto, 0.7)
        preg = texto('?', 90, AMARILLO, 905, 760)
        esc(tp('adelante') + 0.18, preg, 0.4)
        s2 = VGroup(texto('SALTO', 100, WHITE), texto('2', 100, AMARILLO)).arrange(RIGHT, buff=U(30)).move_to(P(540, 290))
        esc(tp('segundo'), s2, 0.7)
        sube(tp('tecnológico'), texto('TECNOLÓGICO', 46, GRIS, 540, 440))
        g.en(tp('hemos') - 0.02, 0.5, lambda preg=preg: [Circumscribe(preg, color=AMARILLO)])

        # ---------------- D · 2007, el primer iPhone
        g.limpiar(ESC['D'])
        cel = figura('celular', 540, 700, 380)
        dib(tp('smartphone'), cel, 1.0)
        numero_titulo(g, tp('2007'), 2007, '', 540, 290, 120, inicio=1990)
        rayos = VGroup(*[Line(P(540 + np.cos(a) * 250, 700 + np.sin(a) * 270), P(540 + np.cos(a) * 320, 700 + np.sin(a) * 340), color=AMARILLO, stroke_width=6)
                         for a in (-2.6, -2.0, -1.15, -0.55, 0.55, 1.15, 2.0, 2.6)])
        g.en(tp('aparece') - 0.04, 0.45, lambda: [LaggedStart(*[Create(r) for r in rayos], lag_ratio=0.15)])
        g.en(tp('primer') - 0.04, 0.45, lambda: [Write(caja(texto('PRIMER IPHONE', 34, ROJO), ROJO, -0.08).move_to(P(760, 990)))])

        # ---------------- E · 7 años hasta que todos tuvieron smartphone
        g.limpiar(ESC['E'])
        nl = linea_numerica(110, 970, 1010, 2007, 2014)
        traza(tp('Desde', ESC['E']) - 0.02, nl, 0.7)
        sube(tp('punto'), texto('2007', 32, WHITE).move_to(nl.n2p(2007) + DOWN * U(50)))
        dib(tp('mundo', ESC['E']), figura('mundo', 540, 650, 300))
        celus = VGroup(*[RoundedRectangle(width=U(46), height=U(82), corner_radius=U(8), color=AZUL, stroke_width=4).set_fill(AZUL, 0.35)
                         .move_to(P(540 + np.cos(np.radians(a)) * 335, 660 - np.sin(np.radians(a)) * 240)).rotate((a - 90) * 0.004)
                         for a in (155, 118, 62, 25, 205, 335)])
        g.en(tp('smartphone', ESC['E']) - 0.04, 0.6, lambda: [LaggedStart(*[GrowFromCenter(c_) for c_ in celus], lag_ratio=0.2)])
        numero_titulo(g, tp('siete'), 7, 'AÑOS', 540, 280, 110)
        llave = Brace(Line(nl.n2p(2007), nl.n2p(2014)), direction=UP, color=AMARILLO, buff=U(16))
        g.en(tp('años', tp('siete')), 0.45, lambda nl=nl, llave=llave: [FadeIn(texto('2014', 32, WHITE).move_to(nl.n2p(2014) + DOWN * U(50) + LEFT * U(20))), GrowFromCenter(llave)])

        # ---------------- F · ChatGPT crece 6 veces más rápido que el iPhone
        g.limpiar(ESC['F'])
        ax = Axes(x_range=[0, 10, 1], y_range=[0, 10, 1], x_length=U(760), y_length=U(520),
                  axis_config={'color': GRIS, 'stroke_width': 4, 'include_tip': True, 'tip_length': U(22), 'include_ticks': False}).move_to(P(560, 800))
        g.en(tp('ChatGPT') - 0.1, 0.5, lambda ax=ax: [Create(ax), FadeIn(texto('TIEMPO', 24, GRIS).next_to(ax.x_axis, DOWN, buff=U(14))),
                                               FadeIn(texto('USUARIOS', 24, GRIS).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=U(14)))])
        cg = ax.plot(lambda x: min(9.6, 0.02 * x ** 3.3), x_range=[0, 6.4], color=AMARILLO, stroke_width=7)
        g.en(tp('creciendo') - 0.06, 0.7, lambda ax=ax, cg=cg: [Create(cg), FadeIn(texto('CHATGPT', 28, AMARILLO).next_to(ax.c2p(6.4, 9.6), RIGHT, buff=U(10)))])
        numero_titulo(g, tp('seis'), 6, '', 540, 290, 120, inicio=1, prefijo='×')
        sube(tp('velocidad'), texto('VELOCIDAD DE ADOPCIÓN', 30, GRIS, 560, 430))
        ip = ax.plot(lambda x: 0.0035 * x ** 3.3, x_range=[0, 10], color=AZUL, stroke_width=7)
        g.en(tp('iPhone', ESC['F']) - 0.06, 0.4, lambda ax=ax, ip=ip: [Create(ip), FadeIn(texto('IPHONE', 28, AZUL).next_to(ax.c2p(10, 6.9), UP, buff=U(10)))])

        # ---------------- G · llevamos apenas 3 años de IA generativa
        g.limpiar(ESC['G'])
        dib(tp('llevamos'), figura('calendario', 300, 710, 300))
        palitos = VGroup(*[Line(P(710 + k * 64, 600), P(722 + k * 64, 860), color=AMARILLO, stroke_width=12) for k in range(3)])
        g.en(tp('tres') - 0.06, 0.42, lambda: [LaggedStart(*[Create(p_) for p_ in palitos], lag_ratio=0.35)])
        numero_titulo(g, tp('años', tp('tres')) - 0.04, 3, 'AÑOS', 540, 290, 110)
        sube(tp('IA', ESC['G']), texto('DE IA GENERATIVA', 44, WHITE, 560, 1040))

        # ---------------- H · ¿cuántos años faltan? 2
        g.limpiar(ESC['H'])
        esc(tp('¿Cuántos'), texto('¿CUÁNTOS AÑOS?', 64, WHITE, 540, 285), 0.6)
        g.en(tp('crees') - 0.04, 0.35, lambda: [FadeIn(texto('?', 70, AMARILLO, 905, 425), scale=1.6), FadeIn(texto('?', 90, AMARILLO, 978, 372), scale=1.6)])
        dib(tp('mundo', ESC['H']), figura('mundo', 540, 650, 300))
        sube(tp('IA', ESC['H']), caja(texto('IA', 40, TEAL), TEAL).move_to(P(712, 505)))
        traza(tp('todo', tp('IA', ESC['H'])), Circle(radius=U(240), color=AZUL, stroke_width=5).move_to(P(540, 650)), 0.5)
        sube(tp('creo'), texto('YO CREO', 32, GRIS, 230, 935))
        n2, _ = numero_titulo(g, tp('dos') - 0.02, 2, 'AÑOS', 640, 1062, 96)
        g.en(tp('sea') - 0.1, 0.42, lambda n2=n2: [Create(Circle(radius=U(80), color=ROJO, stroke_width=6).move_to(n2.get_center()))])

        # ---------------- I · "eso lo usarán mis nietos"
        g.limpiar(ESC['I'])
        crece(ESC['I'] + 0.12, persona('abuelo', 540, 520, 150, MORADO), 0.45)
        c1 = texto('"ESO LO USARÁN', 44, WHITE, 540, 790)
        c2 = texto('MIS NIETOS"', 44, WHITE, 560, 890)
        sube(tp('eso', ESC['I']), c1)
        sube(tp('mis', ESC['I']), c2)
        g.en(tp('nietos') - 0.1, 0.3, lambda: [Create(Cross(VGroup(c1, c2), stroke_color=ROJO, stroke_width=12))])

        # ---------------- J1 · el nivel de adopción de los niños
        g.limpiar(ESC['J1'])
        cen, R = P(540, 830), U(275)
        pista = Arc(radius=R, start_angle=PI, angle=-PI, arc_center=cen, color='#2C3442', stroke_width=26)
        marcas = VGroup(*[Line(cen + R * 0.80 * np.array([np.cos(PI - k * PI / 10), np.sin(PI - k * PI / 10), 0]),
                               cen + R * (0.68 if k % 5 else 0.62) * np.array([np.cos(PI - k * PI / 10), np.sin(PI - k * PI / 10), 0]), color=GRIS, stroke_width=4) for k in range(11)])
        g.en(tp('miremos') - 0.04, 0.6, lambda: [Create(pista), LaggedStart(*[Create(m) for m in marcas], lag_ratio=0.08)])
        nivel = ValueTracker(0)
        arco = always_redraw(lambda: Arc(radius=R, start_angle=PI, angle=-PI * max(1e-3, nivel.get_value()), arc_center=cen, color=AMARILLO, stroke_width=26))
        aguja = always_redraw(lambda: Line(cen, cen + R * 0.74 * np.array([np.cos(PI - PI * nivel.get_value()), np.sin(PI - PI * nivel.get_value()), 0]), color=ROJO, stroke_width=9))
        eje = Dot(cen, radius=U(16), color=WHITE)

        def mide():
            self.add(arco, aguja, eje)

            def fija():
                a2, n2_ = arco.copy().clear_updaters(), aguja.copy().clear_updaters()
                self.remove(arco, aguja, nivel)
                self.add(a2, n2_, eje)
            return [nivel.animate.set_value(0.93), FadeIn(texto('NIVEL', 34, GRIS, 540, 890))], fija
        g.en(tp('nivel') - 0.06, 0.8, mide)
        esc(tp('adopción'), texto('ADOPCIÓN', 92, WHITE, 540, 290), 0.6)
        crece(tp('tienen'), persona('nino', 190, 1000, 100, AMARILLO))

        # ---------------- J2 · un niño de 8 años: pregúntale a ChatGPT
        g.limpiar(ESC['J2'])
        g2 = tp('Google', ESC['J2']); c2t = tp('ChatGPT', g2)
        crece(tp('niño', ESC['J2']), persona('nino', 190, 640, 120, AMARILLO))
        numero_titulo(g, tp('8'), 8, 'AÑOS', 600, 285, 100)
        sube(tp('pregúntale'), texto('PREGÚNTALE A GOOGLE', 34, WHITE, 660, 640))
        traza(g2 + 0.04, tachon(772, 958, 640), 0.3)
        sube(tp('pregúntale', g2), texto('PREGÚNTALE A CHATGPT', 34, WHITE, 660, 860))
        traza(c2t + 0.02, chulo(268, 860, 42), 0.3)
        traza(c2t + 0.28, Line(P(760, 900), P(968, 900), color=AMARILLO, stroke_width=6), 0.3)

        # ---------------- K · creció con ChatGPT, no con Google
        g.limpiar(ESC['K'])
        esc(tp('creció'), texto('CRECIÓ', 92, WHITE, 600, 285), 0.6)
        regla = NumberLine(x_range=[0, 13, 1], length=U(620), rotation=PI / 2, color=GRIS, include_numbers=False, include_tip=False, tick_size=U(12), stroke_width=4).move_to(P(110, 785))
        traza(tp('creció') + 0.16, regla, 0.5)
        crece(tp('creció') + 0.26, persona('nino', 330, 800, 125, AMARILLO))
        traza(tp('con', tp('creció')), Arrow(P(205, 1080), P(205, 680), buff=0, color=ROJO, stroke_width=7), 0.4)
        g.en(tp('dudas') - 0.04, 0.4, lambda: [FadeIn(texto('?', 70, AMARILLO, 520, 600), scale=1.6), FadeIn(texto('?', 92, AMARILLO, 600, 520), scale=1.6)])
        g.en(tp('preguntas', tp('dudas')) - 0.04, 0.4, lambda: [FadeIn(texto('?', 62, AZUL, 545, 760), scale=1.6), FadeIn(texto('?', 80, AZUL, 632, 700), scale=1.6)])
        ck = tp('ChatGPT', ESC['K'])
        sube(ck, texto('CHATGPT', 44, WHITE, 800, 880))
        traza(ck + 0.3, chulo(600, 880, 36), 0.3)
        sube(tp('no', ck), texto('GOOGLE', 44, WHITE, 800, 1020))
        traza(tp('Google', ESC['K']) + 0.02, tachon(700, 902, 1020), 0.3)

        # ---------------- L · natural: no van a entender los teclados
        g.limpiar(ESC['L'])
        esc(tp('natural'), texto('NATURAL', 100, WHITE, 540, 290), 0.6)
        for k, (tipo, col) in enumerate((('nino', AMARILLO), ('mujer', ROJO), ('joven', AZUL))):
            crece(tp('generación') - 0.06 + k * 0.14, persona(tipo, 290 + k * 250, 640, 82, col), 0.4)
        g.en(tp('entender') - 0.04, 0.4, lambda: [LaggedStart(*[FadeIn(texto('?', 60, AMARILLO, 290 + k * 250, 478), scale=1.6) for k in range(3)], lag_ratio=0.3)])
        dib(tp('teclados'), figura('teclado', 540, 960, 150))

        # ---------------- M · un muchacho de 14 no entiende los casetes
        g.limpiar(ESC['M'])
        crece(tp('muchacho'), persona('joven', 230, 660, 120, AZUL))
        numero_titulo(g, tp('14'), 14, 'AÑOS', 600, 285, 100)
        g.en(tp('entiende') - 0.04, 0.3, lambda: [FadeIn(texto('?', 72, AMARILLO, 400, 530), scale=1.6)])
        dib(tp('casetes', ESC['M']), figura('casete', 700, 670, 200))
        traza(tp('en', tp('casetes', ESC['M'])), Arrow(P(650, 800), P(570, 890), buff=0, color=ROJO, stroke_width=6), 0.3)
        dib(tp('Walkman'), figura('walkman', 430, 1000, 280))

        # ---------------- N · para los niños es normal; para tus clientes también
        g.limpiar(ESC['N'])
        crece(tp('niños', ESC['N']), persona('nino', 200, 560, 105, AMARILLO))
        esc(tp('normal'), texto('NORMAL', 100, WHITE, 560, 285), 0.6)
        traza(tp('normal') + 0.25, chulo(336, 470, 44), 0.3)
        sube(tp('tus'), texto('TUS CLIENTES', 46, WHITE, 640, 700))
        for tipo, col, x, w in (('adulto', VERDE, 420, 'clientes'), ('mujer', ROJO, 640, 'también'), ('abuelo', MORADO, 860, 'va')):
            t_ = tp(w, ESC['N']) if w != 'va' else tp('va', tp('también', ESC['N']))
            crece(t_, persona(tipo, x, 930, 88, col))

        # ---------------- O · el negocio sin IA va a sonar a casete
        g.limpiar(ESC['O'])
        dib(tp('negocio', ESC['O']), figura('tienda', 520, 700, 340))
        g.en(tp('IA', ESC['O']) - 0.06, 0.4, lambda: [GrowFromCenter(caja(texto('SIN IA', 58, ROJO), ROJO, -0.12).move_to(P(520, 470)))])
        ondas = VGroup(*[Arc(radius=U(50 + k * 45), start_angle=-0.55, angle=1.1, arc_center=P(780, 700), color=AZUL, stroke_width=6) for k in range(3)])
        g.en(tp('sonar') - 0.06, 0.5, lambda: [LaggedStart(*[Create(o) for o in ondas], lag_ratio=0.3)])
        esc(tp('casete', ESC['O']), texto('CASETE', 100, WHITE, 540, 270), 0.6)
        dib(tp('casete', ESC['O']) + 0.25, figura('casete', 740, 1015, 160), 0.6)

        # ---------------- P · agentes que reemplazan el trabajo lento y caro: hoy
        g.limpiar(ESC['P'])
        hoy = tp('hoy', ESC['P'])
        for k, (x, w) in enumerate(((215, tp('agentes')), (540, tp('IA', ESC['P'])), (865, tp('reemplazan')))):
            dib(w, figura('robot', x, 880, 250), 0.6)
            sube(w + 0.3, texto(f'AGENTE 0{k + 1}', 24, GRIS, x, 1060), 0.3)
        sube(tp('lento') - 0.06, texto('LENTO', 46, WHITE, 300, 560), 0.3)
        traza(tp('lento') + 0.2, tachon(232, 368, 560), 0.25)
        sube(tp('caro') - 0.06, texto('CARO', 46, WHITE, 780, 560), 0.3)
        traza(tp('caro') + 0.2, tachon(720, 840, 560), 0.25)
        esc(hoy, texto('HOY', 140, AMARILLO, 540, 290), 0.5)
        g.en(tp('no', hoy) - 0.06, 0.4, lambda: [GrowFromCenter(caja(texto('NO ES MODA', 44, ROJO), ROJO, -0.06).move_to(P(540, 690)))])

        # ---------------- Q · separará a las que triunfen de las que quiebren (dos curvas que se separan)
        g.limpiar(ESC['Q'])
        ax = Axes(x_range=[0, 10, 1], y_range=[-5, 5, 1], x_length=U(780), y_length=U(560),
                  axis_config={'color': GRIS, 'stroke_width': 4, 'include_tip': True, 'tip_length': U(22), 'include_ticks': False}).move_to(P(540, 780))
        g.en(tp('separará') - 0.06, 0.45, lambda ax=ax: [Create(ax)])
        tramo = ax.plot(lambda x: 0.0 * x, x_range=[0, 4], color=WHITE, stroke_width=7)
        traza(tp('separará') + 0.3, tramo, 0.35)
        sube(tp('empresas'), texto('EMPRESAS', 70, WHITE, 540, 285))
        sub = ax.plot(lambda x: 0.12 * (x - 4) ** 2.1, x_range=[4, 10], color=VERDE, stroke_width=7)
        g.en(tp('triunfen') - 0.06, 0.6, lambda ax=ax, sub=sub: [Create(sub), FadeIn(texto('TRIUNFAN', 34, VERDE).next_to(ax.c2p(10, 5.1), LEFT, buff=U(10)))])
        baj = ax.plot(lambda x: -0.12 * (x - 4) ** 2.1, x_range=[4, 10], color=ROJO, stroke_width=7)
        g.en(tp('quiebren') - 0.06, 0.45, lambda ax=ax, baj=baj: [Create(baj), FadeIn(texto('QUIEBRAN', 34, ROJO).next_to(ax.c2p(10, -5.1), LEFT, buff=U(10)))])

        # ---------------- R · comenta ERA
        g.limpiar(ESC['R'])
        sube(ESC['R'] + 0.04, texto('COMENTA', 34, GRIS, 540, 176), 0.3)
        esc(tp('ERA'), texto('ERA', 160, AMARILLO, 540, 370), 0.6)
        dib(tp('envío'), figura('sobre', 300, 760, 170))
        dib(tp('clase'), figura('laptop', 750, 790, 210))
        sube(tp('clase') + 0.5, texto('CLASE', 34, WHITE, 750, 940), 0.3)
        esc(tp('instalarlas'), texto('¡EN TU NEGOCIO!', 52, AMARILLO, 540, 1090), 0.8)
        traza(tp('negocio', tp('instalarlas')), Line(P(270, 1135), P(810, 1135), color=AMARILLO, stroke_width=6), 0.4)

        g.correr()
