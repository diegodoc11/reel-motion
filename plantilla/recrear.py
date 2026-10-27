# -*- coding: utf-8 -*-
"""
reel-motion · ESTILO RECREAR  (plantilla/recrear.py + plantilla/recrear.css)
=========================================================================
El tercer estilo de la skill. Nace del reel "El carro volador de Tesla no está a la venta" (oct 2026): un HECHO REAL
que fue tendencia (el carro de Tesla subiendo una rampa y saliendo volando) se RECREA como animación plana, limpia,
mientras el presentador explica la estrategia de negocio que hay detrás. La pantalla se ve como un INFORME:

  · fondo claro con cuadrícula + encabezado tipo reporte ("INFORME SEÑUELO · CASO · EL LLAMATIVO") + rótulos mono
  · el presentador recortado CHICO, abajo a la derecha; los subtítulos a su izquierda
  · los 2/3 de arriba son un ESCENARIO: ahí pasa la recreación y luego las piezas de infografía de negocio
  · dos modos: CLARO (qué pasó) ↔ PLANO AZUL (por qué funciona). Un solo tween repinta todo (variables CSS)
  · un acento (el color de marca) + verde para "lo razonable / la decisión correcta"

Uso (reel completo de ejemplo: plantilla/build_recrear.py):

    sys.path.insert(0, os.path.join(SKILL, 'scripts')); sys.path.insert(0, os.path.join(SKILL, 'plantilla')); sys.path.insert(0, P)
    import motor
    motor.iniciar(P, correcciones={...}, colores={'acento': '#D11F1D', 'tinta': '#161616', 'fondo': '#E4E4E2'})
    from motor import *
    import recrear as R
    R.escenario(informe='INFORME', tema='SEÑUELO', caso='CASO · EL LLAMATIVO', usuario='@tuusuario')
    ...recreación del hecho (R.objeto / R.carro + R.recorrido + R.flota)...
    R.plano(f('Vamos a analizarlo'))      # modo plano azul
    ...piezas de negocio (R.tarjeta_precio, R.contador, R.barra, R.menu…)...
    R.claro(f('Segundo'))
    R.subtitulos(desde=f('...'), cambios=[('sígueme', 'SÍGUEME', t)])
    R.cerrar(musica='auto')

Convenciones (las mismas del estilo noche):
  idp      texto corto y único por pieza ('e1', 'e2'…). Los ids internos son idp + sufijo.
  t / t1   segundo en que entra / en que TERMINA de salir (None = se queda). Los tiempos SIEMPRE salen de f('palabra').
  textos   admiten HTML y entidades (&aacute;, &ntilde;, <br>).
  x, y     posición en px dentro del lienzo 1080×1920. El escenario útil va de y 330 a 1170 (debajo del encabezado,
           encima del presentador). La zona x 470-1080 · y 1170-1920 es del presentador: nada ahí.
"""
import os, re, math, html, colorsys
import motor
from motor import I, S, T, FT, win, fx, flash, steps

AQUI = os.path.dirname(os.path.abspath(__file__))
ZX0, ZY0, ZX1, ZY1 = 60, 330, 1020, 1170          # escenario (zona de gráficos): debajo del encabezado, encima del presentador
CAP_Y = 1395                                       # línea de subtítulos (a la izquierda del presentador)
CAP_W = 700

# modo PLANO AZUL (se puede retocar: R.PLANO['--pg'] = '#0B1F3A')
PLANO = {'--pg': '#0C2746', '--gl': '#1D4C7C', '--cb': '#10355E', '--cl': '#7EC8FF', '--tx': '#EAF4FF', '--mu': '#9CC4E8', '--pr': '#7EE2FF',
         '--cf': '#0E2E55', '--ck': '#9FD4FF', '--pb': '#EAF4FF', '--pt': '#10355E', '--sh': 'rgba(0,0,0,.45)'}
CLARO = {}                                         # lo llena escenario() con los colores de motor.iniciar(colores=…)

_IDS = set(); _EST = {'plano': False, 'cambios': []}

CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5 10 17.5 19.5 7"/></svg>'
CURSOR = '<svg viewBox="0 0 24 24"><path d="M5 3l14 9-6 1.5L16 20l-2.5 1.5L10 15l-5 4z" fill="#fff" stroke="#161616" stroke-width="1.6" stroke-linejoin="round"/></svg>'


# =====================================================================================================
#  AYUDAS
# =====================================================================================================
def _rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def _hex(rgb):
    return '#%02X%02X%02X' % tuple(max(0, min(255, int(round(c)))) for c in rgb)

def _tono(h, dl=0.0, ds=0.0):
    r, g, b = [c / 255 for c in _rgb(h)]; hh, l, s = colorsys.rgb_to_hls(r, g, b)
    return _hex([c * 255 for c in colorsys.hls_to_rgb(hh, max(0, min(1, l + dl)), max(0, min(1, s + ds)))])

def _id(idp):
    if not re.match(r'^[A-Za-z][A-Za-z0-9_]*$', idp):
        raise SystemExit(f"recrear: idp '{idp}' no sirve: usa letras y números, sin guiones ni espacios (ej. 'e3')")
    if idp in _IDS: raise SystemExit(f"recrear: el idp '{idp}' está repetido: cada pieza necesita uno distinto")
    _IDS.add(idp); return idp

def _miles(v):
    return f'{int(v):,}'.replace(',', '.')

def add(h):
    """agrega HTML al escenario (#rz). Úsalo para piezas propias; cada elemento animado necesita id único."""
    motor.parts.append(h)

def ft(frase, despues=0.0):
    """f() menos 0.03 s: el instante en que algo debe ENTRAR para que se vea con la palabra."""
    return motor.f(frase, despues) - 0.03

# --- movimientos (todos con fromTo e immediateRender:false: se pueden repetir sobre el mismo elemento) ---
def pin(el, t, sc=0.5, dur=0.28, ease='back.out(2.2)', snd='pop', g=0.16, rot=None, y=None):
    """aparece con rebote (pop). rot=(desde, hasta) grados · y=desplazamiento inicial en px."""
    a = {'opacity': 0, 'scale': sc}; b = {'opacity': 1, 'scale': 1}
    if rot is not None: a['rotation'] = rot[0]; b['rotation'] = rot[1]
    if y is not None: a['y'] = y; b['y'] = 0
    I(el, opacity=0); FT(el, t, dur, a, b, ease)
    if snd: fx(t, snd, g)

def slam(el, t, sc=2.0, rot=(-9, 0), snd='thump', g=0.26):
    """cae de golpe desde grande (sello, etiqueta clave)."""
    pin(el, t, sc=sc, dur=0.24, ease='power3.out', snd=snd, g=g, rot=rot)

def up(el, t, dy=60, dur=0.32, snd='swipe', g=0.1):
    """sube desde abajo desvaneciéndose hacia dentro."""
    I(el, opacity=0); FT(el, t, dur, {'opacity': 0, 'y': dy}, {'opacity': 1, 'y': 0}, 'power3.out')
    if snd: fx(t, snd, g)

def desde(el, t, dx=0, dy=0, dur=0.36, snd='swipe', g=0.12):
    """entra deslizándose desde (dx, dy) px hasta su sitio."""
    I(el, opacity=0); FT(el, t, dur, {'opacity': 0, 'x': dx, 'y': dy}, {'opacity': 1, 'x': 0, 'y': 0}, 'expo.out')
    if snd: fx(t, snd, g)

def out(el, t, dur=0.18, dy=-30):
    """sale hacia arriba desvaneciéndose, TERMINANDO en t."""
    T(el, t - dur, dur, 'power2.in', opacity=0, y=dy)

def outo(el, t, dur=0.18):
    """sale solo con opacidad (para objetos que se mueven o flotan: no pisa su y)."""
    T(el, t - dur, dur, 'power2.in', opacity=0)

def cv(sel, t, dur, **vars_):
    """anima variables CSS (p. ej. --pg) de un elemento: así se repinta todo el estilo de una vez."""
    motor.tw.append(f'tl.to("{sel}",{motor._js(dict(vars_, duration=round(dur, 3), ease="power2.inOut"))},{max(0, t):.3f});')

def keyframes(sel, t, kfs):
    """recorrido cuadro a cuadro: kfs = [(dur, {'x':…, 'y':…, 'rotation':…}), …] → un solo tween con keyframes."""
    ks = ','.join(motor._js(dict(p, duration=round(d, 3), ease='none')) for d, p in kfs)
    motor.tw.append(f'tl.to("{sel}",{{keyframes:[{ks}]}},{max(0, t):.3f});')

def pulso(el, t, escala=1.05, dur=0.12):
    """latido corto (cuando una cifra llega, cuando se toca un botón)."""
    motor.tw.append(f'tl.fromTo("{el}",{{scale:1}},{{scale:{escala},duration:{dur},ease:"power2.out",yoyo:true,repeat:1,immediateRender:false}},{max(0, t):.3f});')

def vibra(el, t, grados=1.2, veces=9, dur=0.08):
    """vibración leve (un carro que llega rodando, algo que se asienta)."""
    motor.tw.append(f'tl.to("{el}",{{rotation:{-grados},duration:{dur},ease:"sine.inOut",repeat:{veces},yoyo:true}},{max(0, t):.3f});')


# =====================================================================================================
#  ESCENARIO · PRESENTADOR EN LA ESQUINA · MODOS CLARO / PLANO
# =====================================================================================================
def escenario(informe='INFORME', tema='', caso='', usuario='', cabeza_y=1225, cabeza_x=812, alto_cabeza=250, cap_ancho=700):
    """Fondo del estilo (va UNA vez, antes de las escenas; reemplaza a escenario('card')): cuadrícula clara + foco +
    encabezado tipo informe ("INFORME SEÑUELO · CASO · EL LLAMATIVO") + usuario; el presentador recortado queda CHICO
    abajo a la derecha (cabeza en cabeza_x, cabeza_y; alto_cabeza px) y los subtítulos a su izquierda.
    Devuelve dict(x, y, scale) del presentador por si una pieza propia necesita esquivarlo."""
    global CAP_W
    motor.escenario('card')
    I('#fillA', opacity=0); I('#bgsz', opacity=0)                           # ni tarjeta ni fondo del motor
    motor.parts.append('<div class="bg" id="rgrid"></div><div class="bg" id="rvigL"></div><div class="bg" id="rvigB"></div>')
    I('#rvigB', opacity=0)
    F = motor.FACE
    alto = max(120.0, F.chin_p90 - F.top); s = round(min(0.7, max(0.42, alto_cabeza / alto)), 3)
    tx = round(cabeza_x - s * F.cx); ty = round(cabeza_y - s * F.top)
    clip_top = cabeza_y - 55; clip_izq = max(0, cabeza_x - 342)
    clip = 'inset(%gpx %gpx 0px %gpx)' % (round(max(0, (clip_top - ty) / s), 1), 0, round(max(0, (clip_izq - tx) / s), 1))
    I('#cam', x=tx, y=ty, scale=s, clipPath=clip)
    CAP_W = cap_ancho
    print(f'  presentador: escala {s} · cabeza en y≈{cabeza_y} · x≈{cabeza_x} · subtítulos en y {CAP_Y} (ancho {CAP_W})')
    # colores del modo claro a partir de la marca (motor.iniciar(colores=…))
    off, ink, red = motor.OFF, motor.INK, motor.RED
    CLARO.update({'--pg': off, '--gl': _tono(off, -0.07), '--cb': _tono(off, 0.09), '--cl': ink, '--tx': ink, '--mu': _tono(ink, 0.35, -0.1),
                  '--pr': red, '--cf': '#FFFFFF', '--ck': ink, '--pb': ink, '--pt': '#FFFFFF', '--sh': 'rgba(0,0,0,.14)'})
    hd = ''
    if informe or tema or caso:
        hd = f'<div class="rhd rmono"><span><b>{informe}</b>&nbsp; {tema}</span><span>{caso}</span></div>'
    us = f'<div class="ruser rmono">{usuario}</div>' if usuario else ''
    motor.parts.append(f'<div id="rz">{hd}{us}')
    return dict(x=tx, y=ty, scale=s)

def modo(t, plano, dur=0.5):
    """cambia entre CLARO y PLANO AZUL en el segundo t (whoosh + destello)."""
    cv('#root', t, dur, **(PLANO if plano else CLARO))
    T('#rvigB', t, dur, 'power2.inOut', opacity=1 if plano else 0); T('#rvigL', t, dur, 'power2.inOut', opacity=0 if plano else 1)
    fx(t, 'whoosh', 0.3); flash(t + 0.05, 0.18)
    _EST['plano'] = plano; _EST['cambios'].append((t, 'plano' if plano else 'claro'))

def plano(t):
    """MODO PLANO AZUL: úsalo cuando el guion pasa de 'qué pasó' a 'por qué funciona' ("vamos a analizarlo")."""
    modo(t, True)

def claro(t):
    """vuelve al MODO CLARO ("segundo…", "ahora en tu negocio…")."""
    modo(t, False)


# =====================================================================================================
#  RECREACIÓN DEL HECHO: objetos dibujados, recorridos, flotar, propulsores, trazos
# =====================================================================================================
def objeto(idp, svg, cls='', acento=False):
    """Un objeto dibujado (SVG) con su origen en el CENTRO: se mueve con x/y/rotation. `svg` es el <svg> completo con
    su propio style (left/top negativos = la mitad del ancho/alto). Clases del trazo: .body (relleno var(--cf), trazo
    var(--ck)) · .glass · .wh / .rim (ruedas). acento=True pinta el .body con el color de marca."""
    _id(idp)
    add(f'<div class="robj {cls} {"ac" if acento else ""}" id="{idp}">{svg}</div>')
    return '#' + idp

def carro(idp, acento=False, propulsores=True):
    """El objeto de ejemplo (del reel de Tesla): carro de perfil mirando a la derecha, 260×104, con propulsores azules
    opcionales (R.propulsores los prende). acento=True = el carro 'normal' en color de marca."""
    th = f'<i class="rthr a" id="{idp}ta"></i><i class="rthr b" id="{idp}tb"></i>' if propulsores else ''
    svg = (th + '<svg viewBox="0 0 260 104">'
           '<path class="body" d="M14 66 L26 46 Q56 40 92 36 L118 14 Q150 6 190 12 L222 38 Q248 42 254 56 L256 70 Q256 80 246 80 L18 80 Q10 78 14 66 Z"/>'
           '<path class="glass" d="M100 38 L122 20 Q150 13 184 18 L212 38 Z"/>'
           '<path d="M148 20 L148 38" stroke="#161616" stroke-width="3"/>'
           '<circle class="wh" cx="64" cy="80" r="17"/><circle class="rim" cx="64" cy="80" r="7"/>'
           '<circle class="wh" cx="206" cy="80" r="17"/><circle class="rim" cx="206" cy="80" r="7"/></svg>')
    return objeto(idp, svg, cls='rcar', acento=acento)

def carro_html(idp, acento=False):
    """el mismo carro pero como HTML suelto (para meterlo DENTRO de una tarjeta de precio o una pantalla)."""
    return (f'<div class="robj rcar {"ac" if acento else ""}" id="{idp}"><svg viewBox="0 0 260 104">'
            '<path class="body" d="M14 66 L26 46 Q56 40 92 36 L118 14 Q150 6 190 12 L222 38 Q248 42 254 56 L256 70 Q256 80 246 80 L18 80 Q10 78 14 66 Z"/>'
            '<path class="glass" d="M100 38 L122 20 Q150 13 184 18 L212 38 Z"/><path d="M148 20 L148 38" stroke="#161616" stroke-width="3"/>'
            '<circle class="wh" cx="64" cy="80" r="17"/><circle class="rim" cx="64" cy="80" r="7"/>'
            '<circle class="wh" cx="206" cy="80" r="17"/><circle class="rim" cx="206" cy="80" r="7"/></svg></div>')

def carro_vivo_html(idp):
    """carro con propulsores para una pantalla 'en vivo' (R.pantallas); préndelos con R.propulsores(idp, t0, t1)."""
    return (f'<div class="robj rcar" id="{idp}"><i class="rthr a" id="{idp}ta"></i><i class="rthr b" id="{idp}tb"></i><svg viewBox="0 0 260 104">'
            '<path class="body" d="M14 66 L26 46 Q56 40 92 36 L118 14 Q150 6 190 12 L222 38 Q248 42 254 56 L256 70 Q256 80 246 80 L18 80 Q10 78 14 66 Z"/>'
            '<path class="glass" d="M100 38 L122 20 Q150 13 184 18 L212 38 Z"/><path d="M148 20 L148 38" stroke="#161616" stroke-width="3"/>'
            '<circle class="wh" cx="64" cy="80" r="17"/><circle class="rim" cx="64" cy="80" r="7"/>'
            '<circle class="wh" cx="206" cy="80" r="17"/><circle class="rim" cx="206" cy="80" r="7"/></svg></div>')

def recorrido(sel, t, tramos):
    """El objeto recorre una ruta: tramos = [(dur, x, y, rotacion), …] (el primero con dur 0 = punto de partida).
    Se dibuja en línea recta entre puntos: para curvas usa muchos puntos (ver R.media_vuelta / R.curva)."""
    I(sel, x=tramos[0][1], y=tramos[0][2], rotation=tramos[0][3])
    keyframes(sel, t, [(d, dict(x=round(x), y=round(y), rotation=round(r))) for d, x, y, r in tramos])

def media_vuelta(cx, cy, r, dur, dentro=34, n=22, desde_abajo=True):
    """Puntos de media circunferencia (como el carro subiendo la rampa del Tesla): desde abajo (cx, cy+r) por la
    DERECHA hasta arriba (cx, cy-r), girando 180°. dentro = cuánto va el objeto por dentro del trazo. Devuelve tramos."""
    out_ = []
    for i in range(1, n + 1):
        th = math.pi * i / n
        x = cx + (r - dentro) * math.sin(th); y = cy + (r - dentro) * math.cos(th)
        out_.append((dur / n, x, y, -180 * i / n))
    return out_

def curva(x0, y0, x1, y1, dur, arco=-60, rot0=0, rot1=0, n=12):
    """Puntos de una curva suave de (x0,y0) a (x1,y1) con una comba `arco` (negativo = hacia arriba) y giro de rot0 a rot1."""
    out_ = []
    for i in range(1, n + 1):
        u = i / n; e = 1 - (1 - u) ** 2
        out_.append((dur / n, x0 + (x1 - x0) * e, y0 + (y1 - y0) * u + arco * math.sin(math.pi * u), rot0 + (rot1 - rot0) * e))
    return out_

def trazo(idp, d, piso=None, t0=0.0, t1=None):
    """Línea punteada del recorrido (rampa, pista, ruta) como path SVG `d` en coordenadas del lienzo; piso = y de una
    línea de suelo opcional. Visible de t0 a t1."""
    _id(idp)
    p = f'<path class="piso" d="M 60 {piso} L 1020 {piso}"/>' if piso is not None else ''
    add(f'<svg class="rtrazo" id="{idp}" style="left:0;top:0" width="1080" height="1920" viewBox="0 0 1080 1920">{p}<path d="{d}"/></svg>')
    win('#' + idp, t0, t1)

def piso(idp, y, t0, t1=None):
    """solo la línea de suelo."""
    _id(idp)
    add(f'<svg class="rtrazo" id="{idp}" style="left:0;top:0" width="1080" height="1920" viewBox="0 0 1080 1920"><path class="piso" d="M 60 {y} L 1020 {y}"/></svg>')
    if t0 <= 0: I('#' + idp, opacity=1)
    else: I('#' + idp, opacity=0); T('#' + idp, t0, 0.2, 'power2.out', opacity=1)
    if t1 is not None: out('#' + idp, t1)

def flota(sel, t0, t1, base=0, amp=9, per=0.9):
    """el objeto flota (sube y baja amp px desde base) entre t0 y t1. Termina en la base: el objeto debe salir con outo()."""
    t1 = t1 - 0.3; n = max(1, int((t1 - t0) / (per / 2)))
    if n % 2 == 0: n -= 1
    motor.tw.append(f'tl.fromTo("{sel}",{{y:{base}}},{{y:{base + amp},duration:{per / 2:.3f},ease:"sine.inOut",repeat:{n},yoyo:true,immediateRender:false}},{max(0, t0):.3f});')

def propulsores(idp, t0, t1):
    """los propulsores de un carro (R.carro / R.carro_vivo_html) titilan entre t0 y t1."""
    for k in ('ta', 'tb'):
        el = f'#{idp}{k}'
        I(el, opacity=0, scaleY=0.3)
        T(el, t0, 0.22, 'power2.out', opacity=1, scaleY=1)
        motor.tw.append(f'tl.to("{el}",{{scaleY:0.72,opacity:0.8,duration:0.09,ease:"sine.inOut",repeat:{max(1, int((t1 - t0 - 0.3) / 0.09))},yoyo:true}},{t0 + 0.25:.3f});')
        S(el, t1, opacity=0)

def entra_rodando(sel, t, y, x_desde=1260, x_hasta=350, dur=0.9):
    """un objeto entra rodando por el piso (desde fuera del cuadro a la derecha) y se asienta con una vibración."""
    I(sel, x=x_desde, y=y, opacity=1)
    T(sel, t, dur, 'power3.out', x=x_hasta); fx(t, 'swipe', 0.14); vibra(sel, t)

def aparece(sel, t, x, y, escala=0.6):
    """un objeto aparece en su sitio con rebote (para los que no recorren nada)."""
    I(sel, x=x, y=y, opacity=0, scale=escala)
    T(sel, t, 0.4, 'back.out(1.6)', opacity=1, scale=1); fx(t, 'pop', 0.18)


# =====================================================================================================
#  RÓTULOS: etiqueta · píldora · nota
# =====================================================================================================
def etiqueta(idp, texto, t, x, y, oscuro=False, t1=None, golpe=False):
    """etiqueta mono en caja roja (oscuro=True: tinta) pegada a algo: "NO ESTÁ A LA VENTA", "MÁS VENDIDO".
    golpe=True cae de golpe (slam) en vez de pop."""
    _id(idp)
    add(f'<div class="rtag rmono {"osc" if oscuro else ""}" id="{idp}" style="left:{x}px;top:{y}px">{texto}</div>')
    if golpe: slam('#' + idp, t, sc=1.6, rot=(-8, -3))
    else: pin('#' + idp, t, y=20)
    if t1 is not None: out('#' + idp, t1)

def pildora(idp, texto, t, y=372, t1=None):
    """píldora centrada de sección: "FUNCIÓN 1 · ATRAER LA ATENCIÓN"."""
    _id(idp)
    add(f'<div class="rpill rmono" id="{idp}" style="top:{y}px">{texto}</div>')
    I('#' + idp, xPercent=-50); pin('#' + idp, t, sc=0.7, y=-20)
    if t1 is not None: out('#' + idp, t1)

def nota(idp, texto, t, y, x=None, t1=None):
    """nota celeste (dato de apoyo): "EL REFERENTE VUELA", "LLAMA LA ATENCIÓN". x=None = centrada."""
    _id(idp)
    if x is None:
        add(f'<div class="rnota rmono" id="{idp}" style="left:50%;top:{y}px">{texto}</div>'); I('#' + idp, xPercent=-50)
    else:
        add(f'<div class="rnota rmono" id="{idp}" style="left:{x}px;top:{y}px">{texto}</div>')
    pin('#' + idp, t, sc=0.7, y=12)
    if t1 is not None: out('#' + idp, t1)


# =====================================================================================================
#  PIEZAS DE NEGOCIO
# =====================================================================================================
def tarjeta_precio(idp, top, nombre, sub, precio, t, t_precio=None, chips=(), icono='', acento=False, t1=None):
    """Tarjeta horizontal 840×160: icono/objeto a la izquierda, NOMBRE + subtítulo mono, PRECIO grande a la derecha y
    chips debajo. chips = [(texto, t, color)] con color '' (tinta) · 'am' (ámbar) · 've' (verde) · 'ce' (celeste).
    t_precio = cuándo cae el precio (thump); None = con la tarjeta. icono = HTML (p. ej. R.carro_html(idp+'c'))."""
    _id(idp)
    ch = ''.join(f'<span class="rchip {c}" id="{idp}h{i}">{tx}</span>' for i, (tx, _, c) in enumerate(chips))
    ic = f'<div class="ric">{icono}</div>' if icono else ''
    add(f'<div class="rpc" id="{idp}" style="top:{top}px">{ic}<div class="rn"><b>{nombre}</b><small>{sub}</small></div>'
        f'<div class="rp"><b id="{idp}p">{precio}</b><div class="rchips">{ch}</div></div></div>')
    desde('#' + idp, t, dx=120, snd='pop', g=0.2)
    for i, (_, tc, _) in enumerate(chips):
        I(f'#{idp}h{i}', opacity=0); FT(f'#{idp}h{i}', tc, 0.2, {'opacity': 0, 'scale': 0.6}, {'opacity': 1, 'scale': 1}, 'back.out(2)'); fx(tc, 'click', 0.14)
    if t_precio is not None:
        I(f'#{idp}p', opacity=0); FT(f'#{idp}p', t_precio, 0.22, {'opacity': 0, 'scale': 1.5}, {'opacity': 1, 'scale': 1}, 'power3.out'); fx(t_precio, 'thump', 0.22)
    if t1 is not None: out('#' + idp, t1)

def contador(idp, top, rotulo, valores, t, t_ini, t_fin, t1=None):
    """Caja "VISTAS  0 → 1.000.000+": valores = lista de textos, o (desde, hasta) enteros (+ sufijo opcional como 3er
    elemento: (0, 1000000, '+')). Cuenta entre t_ini y t_fin con un ding y un latido al llegar."""
    _id(idp)
    if isinstance(valores, tuple):
        a, b = valores[0], valores[1]; suf = valores[2] if len(valores) > 2 else ''
        pasos = [a] + [a + (b - a) * (1 - (1 - k / 9) ** 2.2) for k in range(1, 9)] + [b]
        vals = [_miles(v) for v in pasos[:-1]] + [_miles(b) + suf]
    else:
        vals = list(valores)
    add(f'<div class="rcnt" id="{idp}" style="top:{top}px"><small>{rotulo}</small><b>{steps(idp + "v", vals, t_ini, t_fin)}</b></div>')
    desde('#' + idp, t, dy=40, snd='pop', g=0.18); fx(t_fin, 'ding', 0.25); pulso('#' + idp, t_fin)
    if t1 is not None: out('#' + idp, t1)

def pantallas(idp, t, celdas, top=632, cols=3, etiqueta='EN VIVO', paso=0.16, t1=None, left=120, ancho=292, alto=210):
    """Cuadrícula de 'pantallas' que se encienden una por una (transmisiones, tiendas, cuentas que repiten lo mismo).
    celdas = [(cifra_arriba_derecha, html_interior), …]; el interior va en 256×190 (p. ej. R.carro_vivo_html(idp+'c0')).
    Devuelve [(t_encendido, id)] por celda, para prender propulsores o flotar lo de adentro."""
    _id(idp); res = []
    for i, (cifra, inner) in enumerate(celdas):
        x = left + (i % cols) * ancho; y = top + (i // cols) * alto; cid = f'{idp}p{i}'
        add(f'<div class="rlive" id="{cid}" style="left:{x}px;top:{y}px"><i>{etiqueta}</i><em>{cifra}</em><div class="rin">{inner}</div></div>')
        ti = t + i * paso; pin('#' + cid, ti, sc=0.7, snd='click', g=0.12); res.append((ti, cid))
        if t1 is not None: out('#' + cid, t1)
    return res

def tachar(idp, texto, t, t_x, y, t1=None):
    """Caja mono con el texto ("PUBLICIDAD $$$") que se tacha con dos trazos rojos: t_x = (t_primer_trazo, t_segundo)."""
    _id(idp)
    add(f'<div class="rads rmono" id="{idp}" style="top:{y}px">{texto}<svg viewBox="0 0 400 120" preserveAspectRatio="none">'
        f'<path id="{idp}x1" d="M14 12 L386 108"/><path id="{idp}x2" d="M386 12 L14 108"/></svg></div>')
    I('#' + idp, xPercent=-50); pin('#' + idp, t, sc=0.7, y=20)
    for k, tt in ((f'#{idp}x1', t_x[0]), (f'#{idp}x2', t_x[1])):
        I(k, strokeDasharray=400, strokeDashoffset=400); T(k, tt, 0.18, 'power2.in', strokeDashoffset=0); fx(tt, 'swipe', 0.18)
    if t1 is not None: out('#' + idp, t1)

def barra(idp, y, valor, t, t_desliza, t_ok, izq='RAZONABLE', der='COSTOSO', objeto_html='', x_desde=230, x_hasta=-150, t1=None):
    """Barra verde↔roja (RAZONABLE – COSTOSO) con un indicador encima (precio + palito + objeto) que se DESLIZA de un
    lado al otro en t_desliza→t_ok y recibe un check verde en t_ok. objeto_html = lo que cuelga del indicador
    (p. ej. R.carro_html(idp+'c', acento=True)). x_desde/x_hasta = corrimiento del grupo (0 = centro)."""
    _id(idp)
    add(f'<div class="rgrp" id="{idp}g" style="left:0;top:0;width:0;height:0">'
        f'<div class="rprice" id="{idp}p" style="left:540px;top:{y}px">{valor}<span class="rok" id="{idp}ok">{CHECK}</span></div>'
        f'<div class="rpole" id="{idp}l" style="left:538px;top:{y + 106}px"></div>'
        f'<div style="left:540px;top:{y + 170}px" id="{idp}o">{objeto_html}</div></div>')
    add(f'<div class="rbar" id="{idp}b" style="top:{y + 208}px"></div>'
        f'<div class="rbl v" id="{idp}i" style="left:110px;top:{y + 266}px">{izq}</div><div class="rbl r" id="{idp}d" style="right:110px;top:{y + 266}px">{der}</div>')
    I(f'#{idp}p', xPercent=-50); pin(f'#{idp}p', t, sc=1.5, snd='thump', g=0.25); I(f'#{idp}ok', opacity=0)
    I(f'#{idp}l', scaleY=0, transformOrigin='50% 0'); T(f'#{idp}l', t + 0.15, 0.2, 'power2.out', scaleY=1)
    I(f'#{idp}o', opacity=0); T(f'#{idp}o', t + 0.3, 0.3, 'power2.out', opacity=1)
    I(f'#{idp}g', x=x_desde)
    desde(f'#{idp}b', t + 0.1, dy=30, snd='swipe', g=0.12); pin(f'#{idp}i', t + 0.3, snd=None); pin(f'#{idp}d', t + 0.3, snd=None)
    T(f'#{idp}g', t_desliza, max(0.5, t_ok - t_desliza + 0.25), 'power2.inOut', x=x_hasta); fx(t_desliza, 'swipe', 0.16)
    pin(f'#{idp}ok', t_ok + 0.12, sc=0.3, snd='ding', g=0.3)
    if t1 is not None:
        for el in (f'#{idp}p', f'#{idp}l', f'#{idp}b', f'#{idp}i', f'#{idp}d'): out(el, t1)
        outo(f'#{idp}o', t1)


class Menu:
    """Menú de precios (ANTES / DESPUÉS) con un hueco punteado arriba que se puede llenar con la 'opción extrema'."""
    def __init__(self, idp, left, titulo, items, top, hueco):
        self.idp = idp; self.sel = '#' + idp; self.n = len(items); self.hueco = hueco
        it = ''.join(f'<div class="rit" id="{idp}i{i}"><div class="rfx g" id="{idp}g{i}"></div><div class="rfx y" id="{idp}y{i}"></div>'
                     f'<b>{b}</b><small>{s_}</small><em>{p}</em><span class="rchip ve big" id="{idp}c{i}"></span></div>' for i, (b, s_, p) in enumerate(items))
        sl = f'<div class="rslot" id="{idp}s"><div class="rin" id="{idp}sin"></div></div>' if hueco else ''
        add(f'<div class="rmenu" id="{idp}" style="left:{left}px;top:{top}px"><h4>{titulo}</h4>{sl}{it}</div>')
        for i in range(self.n): I(f'#{idp}g{i}', opacity=0); I(f'#{idp}y{i}', opacity=0); I(f'#{idp}c{i}', opacity=0)
        if hueco: I(f'#{idp}sin', opacity=0)
    def item(self, i, t):
        """el ítem i aparece en t (si los quieres uno por uno; si no, salen con el menú)."""
        I(f'#{self.idp}i{i}', opacity=0); T(f'#{self.idp}i{i}', t, 0.2, 'power2.out', opacity=1); fx(t, 'click', 0.12)
    def llena(self, nombre, sub, precio, t, chip=None):
        """el hueco se llena con la opción extrema. chip = (texto, t, color, arriba) p. ej. ('EXTREMO', t2, 'am', False)."""
        if not self.hueco: raise SystemExit(f'recrear: el menú {self.idp} no tiene hueco (hueco=True)')
        ch = ''
        if chip:
            ch = f'<span class="rchip {chip[2]} {"arriba" if len(chip) > 3 and chip[3] else ""}" id="{self.idp}sc">{chip[0]}</span>'
        _RELLENOS.append((f'{self.idp}sin', f'<b>{nombre}</b><small>{sub}</small><em>{precio}</em>{ch}'))
        T(f'#{self.idp}sin', t, 0.25, 'power2.out', opacity=1); fx(t, 'pop', 0.2); pulso(f'#{self.idp}s', t, 1.06, 0.14)
        if chip:
            I(f'#{self.idp}sc', opacity=0); pin(f'#{self.idp}sc', chip[1], sc=0.5, snd='click', g=0.14)
    def resalta(self, i, t, color='g'):
        """resalta el ítem i: 'g' verde (la decisión inteligente) · 'y' ámbar (lo que ahora se ve barato)."""
        T(f'#{self.idp}{color}{i}', t, 0.2, 'power2.out', opacity=1); fx(t, 'click', 0.14)
    def chip(self, i, texto, t, color='ve'):
        """chip en la esquina del ítem i ("DECISIÓN INTELIGENTE")."""
        _RELLENOS.append((f'{self.idp}c{i}', texto)); _CLASES.append((f'{self.idp}c{i}', color))
        pin(f'#{self.idp}c{i}', t, sc=0.5, snd='ding', g=0.3)
    def sale(self, t): out(self.sel, t)

_RELLENOS = []; _CLASES = []

def menu(idp, left, titulo, items, t, top=392, hueco=True, dx=-80, t_items=(), entra=True):
    """Menú 430 px de ancho: items = [(nombre, sub_mono, precio)] (2 caben con hueco). Entra deslizándose desde dx.
    t_items = [t, t] para que cada ítem aparezca con su palabra. entra=False si lo va a meter R.cambia_menus().
    Devuelve un Menu: .llena() .resalta() .chip() .sale()."""
    _id(idp)
    m = Menu(idp, left, titulo, items, top, hueco)
    if entra: desde(m.sel, t, dx=dx, snd='pop', g=0.2)
    else: I(m.sel, opacity=0)
    for i, ti in enumerate(t_items): m.item(i, ti)
    return m

def cambia_menus(salen, entran, t):
    """los menús `salen` suben y desaparecen, los `entran` suben a su sitio (cambio de ejemplo: pastelería → mentoría)."""
    for m in salen: T(m.sel, t - 0.16, 0.16, 'power2.in', opacity=0, y=-30)
    for m in entran: I(m.sel, opacity=0, y=40); T(m.sel, t, 0.3, 'power3.out', opacity=1, y=0)
    fx(t, 'whoosh', 0.2)

def burbuja(idp, texto, t, x, y, t1=None, rot=(-6, -3)):
    """burbuja de comentario con cola arriba ("¿Esto por solicitud?"): lo que la gente dice."""
    _id(idp)
    add(f'<div class="rbub" id="{idp}" style="left:{x}px;top:{y}px">{texto}</div>')
    pin('#' + idp, t, sc=0.5, rot=rot)
    if t1 is not None: out('#' + idp, t1)

def titulo(idp, lineas, t, sub='', y=560):
    """título gigante centrado de cierre (2 líneas) + subtítulo mono: la ESTRATEGIA con nombre."""
    _id(idp)
    s = f'<small>{sub}</small>' if sub else ''
    add(f'<div class="rttl" id="{idp}" style="top:{y}px">{"<br>".join(lineas)}{s}</div>')
    up('#' + idp, t, dy=50, snd='pop', g=0.2)

def sello(idp, texto, t, y=398):
    """sello de goma rojo que cae de golpe sobre el título ("SEÑUELO")."""
    _id(idp)
    add(f'<div class="rstamp" id="{idp}" style="top:{y}px">{texto}</div>')
    I('#' + idp, xPercent=-50); slam('#' + idp, t, sc=2.4, rot=(-20, -9), g=0.4)

def boton(idp, texto, t, y=1030, click=0.35):
    """botón oscuro centrado con cursor ("SÍGUEME PARA MÁS →") que se 'toca' click s después."""
    _id(idp)
    add(f'<div class="rbtn" id="{idp}" style="top:{y}px">{texto}<span class="rcur">{CURSOR}</span></div>')
    I('#' + idp, xPercent=-50); pin('#' + idp, t, sc=0.6, snd='pop', g=0.2)
    pulso('#' + idp, t + click, 0.94, 0.1); fx(t + click, 'click', 0.2)


# =====================================================================================================
#  SUBTÍTULOS Y CIERRE
# =====================================================================================================
def subtitulos(desde=0.0, hasta=None, propios=(), cambios=None, huecos=()):
    """subtítulos del motor pero a la izquierda del presentador (y 1395, ancho CAP_W)."""
    motor.subtitulos(desde=desde, hasta=hasta, propios=tuple(propios) + ('Claude',), cambios=cambios, huecos=huecos, y=CAP_Y)

def css():
    fn = os.path.join(motor.P, 'recrear.css')
    if not os.path.exists(fn): fn = os.path.join(AQUI, 'recrear.css')
    s = open(fn, encoding='utf-8').read().replace('@AC@', motor.RED).replace('@CAPW@', str(CAP_W))
    vars_ = ''.join(f'{k}:{v};' for k, v in CLARO.items())
    return f'#root{{{vars_}}}\n' + s

def _rellenar(doc):
    """mete el contenido de los huecos y chips (se escriben al final para que el HTML quede en orden)."""
    for cid, inner in _RELLENOS:
        doc = re.sub(rf'(<(?:div|span)[^>]*id="{cid}"[^>]*>)(</(?:div|span)>)', lambda m: m.group(1) + inner + m.group(2), doc, count=1)
    for cid, cls in _CLASES:
        doc = doc.replace(f'class="rchip ve big" id="{cid}"', f'class="rchip {cls} big" id="{cid}"', 1)
    return doc

def cerrar(musica='auto', inicio_musica=0.0, volumen_musica=0.26, css_extra='', resumen='', fade_corto=True, capturas=None):
    """Reemplaza a cerrar() del motor: cierra el escenario, agrega el CSS del estilo (con los colores de marca) y escribe
    index.html + final_audio.wav. fade_corto=True: la música llega hasta el último cuadro (fundido de 0.3 s, no 1.3 s;
    lo exige verificar_reel.py)."""
    motor.parts.append('</div>')                                             # /rz
    motor.parts[:] = [_rellenar(p) for p in motor.parts]
    if fade_corto:
        _run0 = motor._run
        def _run_fade(cmd):
            return _run0([re.sub(r'afade=t=out:st=[\d.]+:d=1\.3', f'afade=t=out:st={motor.DUR - 0.35:.3f}:d=0.3', c) for c in cmd])
        motor._run = _run_fade
    cambios = ' · '.join(f'{k} {t:.2f}' for t, k in _EST['cambios'])
    motor.cerrar(musica=musica, inicio_musica=inicio_musica, volumen_musica=volumen_musica, capturas=capturas,
                 css_extra=css() + css_extra, resumen=(resumen + ' | ' if resumen else '') + f'recrear: {cambios or "solo claro"}')
