# -*- coding: utf-8 -*-
"""
reel-motion · ESTILO PIZARRA — el presentador recortado CHICO abajo a la derecha y, arriba, una pizarra negra donde cada
frase se explica con monigotes y dibujos a línea:

  · fondo casi negro con cuadrícula fina, polvo flotante y un foco suave detrás del presentador
  · KARAOKE FANTASMA en la zona media izquierda: la frase entera aparece en gris y cada palabra se enciende en blanco
    cuando se dice (es el subtítulo; las palabras clave se encienden en rojo)
  · la palabra clave GIGANTE en rojo arriba (con resplandor) y frases cortas en blanco o en cursiva fina
  · MONIGOTES blancos que ACTÚAN la frase (brazos y piernas articulados que se mueven) y DIBUJOS a línea que se trazan
    solos (strokeDashoffset): gráficas, objetos, flechas, globos de diálogo (catálogo en dibujos.py)
  · un solo acento: rojo · cierre con la caja de comentarios de Instagram + burbuja azul

Uso (después de motor.iniciar y `import recrear as R`; plantilla completa en build_pizarra.py):
    import pizarra as Z
    import dibujos as D
    Z.escenario(firma='TU NOMBRE')
    Z.mono('m1', x, y, alto, pose='parado', t=..., t1=...)      # monigote
    Z.dibujo('d1', Z.L('M0 0 L100 0') + ..., x, y, w, h, t, t1=...)
    Z.grande('g1', 'CASI', t, t1)                              # palabra clave roja gigante
    Z.karaoke(desde=0, rojas=('casete', 'era'))
    Z.cerrar(musica=...)
"""
import random, html, re, math
import motor
import recrear as R
from motor import I, S, T, FT, fx, flash

add = motor.parts.append
ROJO = '#E5322D'; BLANCO = '#F4F4F2'; GRIS = '#4C4D54'; MU = '#8E9099'
_N = [0]


def _nid(base):
    _N[0] += 1
    return f'{base}{_N[0]}'


# ===================================================================================================== escenario
def escenario(firma='', cabeza_y=1258, cabeza_x=826, alto_cabeza=262):
    """fondo negro con cuadrícula fina + polvo + foco; el presentador recortado abajo a la derecha.
    `firma` = tu nombre en letras chicas arriba (vacío = sin firma)."""
    R.escenario(informe='', tema='', caso='', usuario='', cabeza_y=cabeza_y, cabeza_x=cabeza_x, alto_cabeza=alto_cabeza)
    R.CLARO.update({'--pg': '#111113', '--gl': 'rgba(255,255,255,.045)', '--cb': '#1B1B1F', '--cl': BLANCO, '--tx': BLANCO,
                    '--mu': MU, '--pr': ROJO, '--cf': '#1B1B1F', '--ck': BLANCO, '--pb': BLANCO, '--pt': '#111113',
                    '--sh': 'rgba(0,0,0,.6)'})
    I('#rvigL', opacity=1)
    rnd = random.Random(7); pts = ''
    for _ in range(48):
        x = rnd.uniform(20, 1060); y = rnd.uniform(260, 1900); s = rnd.choice([3, 3, 4, 5])
        c = ROJO if rnd.random() < 0.18 else '#D8D8D8'; a = rnd.uniform(0.12, 0.45)
        pts += f'<i style="left:{x:.0f}px;top:{y:.0f}px;width:{s}px;height:{s}px;background:{c};opacity:{a:.2f}"></i>'
    add(f'<div id="pzpolvo">{pts}</div>' + (f'<div class="pzfirma">{firma}</div>' if firma else ''))
    FT('#pzpolvo', 0, motor.DUR, {'y': 0}, {'y': -110}, 'none')


# ===================================================================================================== textos
def _sale(sel, t, t1, entrada=0.3):
    """sale en t1, pero nunca antes de que termine su entrada (si se pisan, la pieza queda pegada en pantalla)."""
    if t1 is not None: R.outo(sel, max(t1, t + entrada + 0.2))


def _esc(t):
    return html.escape(t, quote=False)


def karaoke(desde=0.0, hasta=None, x=54, y=1232, ancho=570, fs=42, rojas=(), max_chars=36, mayus=True, reemplazos=None):
    """subtítulo fantasma: la frase completa en gris, cada palabra se pone blanca (o roja si está en `rojas`) al
    decirla. Va en la zona media izquierda (a la izquierda del presentador). `reemplazos` = {'palabra': 'COMO SE VE'}."""
    rojas = {motor.norm(r) for r in rojas}; reemplazos = {motor.norm(k): v for k, v in (reemplazos or {}).items()}
    ws = [w for w in motor.WD if w['start'] >= desde - 0.01 and (hasta is None or w['start'] < hasta)]
    grupos, cur, n = [], [], 0
    for w in ws:
        tx = w['text']
        if cur and (n + len(tx) > max_chars or w['start'] - cur[-1]['end'] > 0.6):
            grupos.append(cur); cur, n = [], 0
        cur.append(w); n += len(tx) + 1
        if tx[-1:] in '.?!:': grupos.append(cur); cur, n = [], 0
    if cur: grupos.append(cur)
    for gi, g in enumerate(grupos):
        gid = _nid('kg')
        t0 = g[0]['start'] - 0.08
        t1 = (grupos[gi + 1][0]['start'] - 0.08) if gi + 1 < len(grupos) else (hasta or motor.DUR)
        spans = ''
        for wi, w in enumerate(g):
            k = motor.norm(w['text'])
            vis = reemplazos.get(k, w['text'])
            vis = vis.upper() if mayus else vis
            cls = ' r' if k in rojas else ''
            spans += f'<span class="kw{cls}">{_esc(vis)}<i id="{gid}_{wi}">{_esc(vis)}</i></span> '
        add(f'<div class="pzk" id="{gid}" style="left:{x}px;top:{y}px;width:{ancho}px;font-size:{fs}px">{spans}</div>')
        I('#' + gid, opacity=0); S('#' + gid, max(0, t0), opacity=1); S('#' + gid, t1, opacity=0)
        for wi, w in enumerate(g):
            I(f'#{gid}_{wi}', opacity=0); S(f'#{gid}_{wi}', max(0, w['start'] - 0.03), opacity=1)


def grande(idp, texto, t, t1=None, y=380, fs=150, color=ROJO, golpe=True):
    """la palabra clave gigante (roja, condensada, con resplandor), centrada arriba."""
    add(f'<div class="pzg" id="{idp}" style="top:{y}px;font-size:{fs}px;color:{color}"><span>{texto}</span></div>')
    I('#' + idp, xPercent=-50)
    R.pin('#' + idp, t, sc=1.5 if golpe else 0.8, dur=0.22, ease='power3.out', snd='thump' if golpe else 'pop', g=0.2)
    _sale('#' + idp, t, t1, 0.22)


def frase(idp, texto, t, t1=None, x=540, y=330, fs=44, color=BLANCO, cursiva=False, ancho=940, alinear='center'):
    """frase corta arriba (blanca en mayúsculas, o en cursiva fina gris/blanca)."""
    cls = 'pzc' if cursiva else 'pzf'
    izq = x - ancho / 2 if alinear == 'center' else x
    add(f'<div class="{cls}" id="{idp}" style="left:{izq:.0f}px;top:{y}px;width:{ancho}px;font-size:{fs}px;color:{color};text-align:{alinear}">{texto}</div>')
    R.up('#' + idp, t, dy=26, g=0.08)
    _sale('#' + idp, t, t1, 0.32)


def rotulo(idp, texto, t, x, y, t1=None, fs=30, color=BLANCO, fondo=None, centro=True):
    """etiqueta pequeña (en mayúsculas) pegada a un dibujo; con fondo = píldora."""
    st = f'left:{x}px;top:{y}px;font-size:{fs}px;color:{color}' + (f';background:{fondo};padding:6px 16px 7px;border-radius:30px' if fondo else '')
    add(f'<div class="pzr" id="{idp}" style="{st}">{texto}</div>')
    if centro: I('#' + idp, xPercent=-50)
    R.pin('#' + idp, t, sc=0.6, g=0.1)
    _sale('#' + idp, t, t1, 0.28)


# ===================================================================================================== dibujos a línea
def L(d, w=6, color=BLANCO, extra=''):
    """trazo que se dibuja solo."""
    return f'<path class="ln" d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{extra}/>'


def F(d, color=BLANCO, op=1.0, extra=''):
    """relleno que aparece después de los trazos."""
    return f'<path class="rel" d="{d}" fill="{color}" opacity="{op}"{extra}/>'


def C(cx, cy, r):
    """círculo como trazo."""
    return f'M{cx - r},{cy} a{r},{r} 0 1,0 {2 * r},0 a{r},{r} 0 1,0 {-2 * r},0'


def dibujo(idp, cuerpo, x, y, w, h, t, t1=None, dur=0.7, orden=None, centro=False, sonido=True):
    """svg de w×h px en (x, y); sus trazos (L) se dibujan en orden entre t y t+dur y luego aparecen los rellenos (F)."""
    k = [0]
    def _id(m):
        k[0] += 1
        return f'id="{idp}_{k[0]}" class="ln" pathLength="1"'
    cuerpo = re.sub(r'class="ln"', _id, cuerpo)
    nln = k[0]
    r = [0]
    def _rid(m):
        r[0] += 1
        return f'id="{idp}_f{r[0]}" class="rel"'
    cuerpo = re.sub(r'class="rel"', _rid, cuerpo)
    izq = x - w / 2 if centro else x
    add(f'<svg class="pzd" id="{idp}" viewBox="0 0 {w} {h}" style="left:{izq:.0f}px;top:{y:.0f}px;width:{w}px;height:{h}px">{cuerpo}</svg>')
    I('#' + idp, opacity=0); S('#' + idp, t, opacity=1)
    paso = dur / max(1, nln)
    for i in range(1, nln + 1):
        I(f'#{idp}_{i}', strokeDashoffset=1)
        FT(f'#{idp}_{i}', t + (i - 1) * paso * 0.75, max(0.12, paso * 1.5), {'strokeDashoffset': 1}, {'strokeDashoffset': 0}, 'power1.inOut')
    for i in range(1, r[0] + 1):
        I(f'#{idp}_f{i}', opacity=0); T(f'#{idp}_f{i}', t + dur * 0.8, 0.25, 'power1.out', opacity=1)
    if sonido: fx(t, 'swipe', 0.07)
    _sale('#' + idp, t, t1, 0.1)


def tachar(idp, x, y, w, h, t, t1=None, color=ROJO):
    """X roja dibujada encima de algo."""
    dibujo(idp, L(f'M10,10 L{w - 10},{h - 10}', 10, color) + L(f'M{w - 10},10 L10,{h - 10}', 10, color), x, y, w, h, t, t1, dur=0.28, sonido=False)
    fx(t, 'thump', 0.16)


def check(idp, x, y, t, t1=None, tam=90, color='#38D27A'):
    dibujo(idp, L(f'M{tam * .12},{tam * .55} L{tam * .42},{tam * .82} L{tam * .9},{tam * .2}', 12, color), x, y, tam, tam, t, t1, dur=0.25, sonido=False)
    fx(t, 'ding', 0.12)


# ===================================================================================================== monigote articulado
POSES = {   # (hombro, codo) por brazo y (cadera, rodilla) por pierna, en grados: 0 = hacia abajo; + = hacia afuera
    'parado':    dict(la=(16, 6), ra=(16, 6), ll=(9, 0), rl=(9, 0)),
    'brazos':    dict(la=(150, 10), ra=(150, 10), ll=(12, 0), rl=(12, 0)),          # brazos arriba (celebra)
    'jarras':    dict(la=(40, -95), ra=(40, -95), ll=(12, 0), rl=(12, 0)),          # manos en la cintura
    'señala':    dict(la=(14, 6), ra=(92, 0), ll=(9, 0), rl=(9, 0)),                # señala a la derecha de la pantalla
    'señala_i':  dict(la=(92, 0), ra=(14, 6), ll=(9, 0), rl=(9, 0)),                # señala a la izquierda de la pantalla
    'piensa':    dict(la=(16, 6), ra=(30, -150), ll=(9, 0), rl=(9, 0)),             # mano en la barbilla
    'triste':    dict(la=(6, 2), ra=(6, 2), ll=(5, 0), rl=(5, 0)),
    'duda':      dict(la=(55, -100), ra=(55, -100), ll=(10, 0), rl=(10, 0)),        # brazos abiertos, palmas arriba
    'camina_a':  dict(la=(24, -10), ra=(-24, -18), ll=(-22, 8), rl=(22, 0)),
    'camina_b':  dict(la=(-24, -18), ra=(24, -10), ll=(22, 0), rl=(-22, 8)),
    'salta':     dict(la=(140, 20), ra=(140, 20), ll=(35, -60), rl=(35, -60)),
    'sentado':   dict(la=(20, -40), ra=(20, -40), ll=(85, -85), rl=(85, -85)),
    'celular':   dict(la=(16, 6), ra=(25, -125), ll=(9, 0), rl=(9, 0)),             # sostiene algo frente a la cara
}


def mono(idp, x, y, alto=320, pose='parado', cara='feliz', color=BLANCO, t=0.0, t1=None, traza=True, grosor=None):
    """monigote de alto px con los pies en (x, y). Partes animables: #idp (todo), #idp_la/_ra (brazos), _laf/_raf
    (antebrazos), _ll/_rl (piernas), _llf/_rlf (canillas). Caras: feliz, serio, triste, sorpresa, enojado, guiño."""
    g = grosor or max(5, round(alto * 0.024))
    cab = alto * 0.25; cuello = alto * 0.25; tronco = alto * 0.33
    brazo, ante = alto * 0.17, alto * 0.16; muslo, canilla = alto * 0.21, alto * 0.20
    ancho = alto * 0.7
    cx = ancho / 2; hy = cuello + alto * 0.05; cad = cuello + tronco
    p = POSES[pose]

    def barra(sid, largo, hijo=''):
        return f'<div class="pzl" id="{sid}" style="width:{g}px;height:{largo:.0f}px;margin-left:{-g / 2:.1f}px;background:{color};border-radius:{g}px">{hijo}</div>'

    def ext(sid, l1, l2):
        return barra(sid, l1, f'<div class="pzj" style="top:{l1 - g / 2:.0f}px;left:{g / 2:.1f}px">' + barra(sid + 'f', l2 + g / 2) + '</div>')

    caras = ''
    for nombre, boca in (('feliz', 'M-13,6 Q0,18 13,6'), ('serio', 'M-11,10 L11,10'), ('triste', 'M-12,14 Q0,3 12,14'),
                         ('sorpresa', 'M-6,10 a6,7 0 1,0 12,0 a6,7 0 1,0 -12,0'), ('enojado', 'M-12,13 Q0,6 12,13'), ('guino', 'M-12,7 Q0,17 12,7')):
        cejas = ('<path d="M-17,-15 L-6,-10 M17,-15 L6,-10" stroke="%s" stroke-width="3.4" stroke-linecap="round"/>' % color) if nombre == 'enojado' else (
                 '<path d="M-17,-11 L-6,-15 M17,-11 L6,-15" stroke="%s" stroke-width="3.4" stroke-linecap="round"/>' % color if nombre == 'triste' else '')
        ojos = ('<circle cx="-9" cy="-4" r="3.6" fill="%s"/>' % color) + ('<path d="M5,-4 L13,-4" stroke="%s" stroke-width="3.4" stroke-linecap="round"/>' % color
                                                                          if nombre == 'guino' else '<circle cx="9" cy="-4" r="3.6" fill="%s"/>' % color)
        caras += (f'<g id="{idp}_c{nombre}" opacity="{1 if nombre == cara else 0}">{cejas}{ojos}'
                  f'<path d="{boca}" stroke="{color}" stroke-width="3.4" fill="none" stroke-linecap="round"/></g>')
    sh = 'filter:drop-shadow(0 0 6px rgba(255,255,255,.28))'
    add(f'''<div class="pzm" id="{idp}" style="left:{x - cx:.0f}px;top:{y - alto:.0f}px;width:{ancho:.0f}px;height:{alto:.0f}px;{sh}">
  <div class="pzj" id="{idp}_t" style="left:{cx:.1f}px;top:{cuello:.0f}px">{barra(idp + '_tr', tronco)}</div>
  <div class="pzj" style="left:{cx:.1f}px;top:{hy:.0f}px">{ext(idp + '_la', brazo, ante)}</div>
  <div class="pzj" style="left:{cx:.1f}px;top:{hy:.0f}px">{ext(idp + '_ra', brazo, ante)}</div>
  <div class="pzj" style="left:{cx:.1f}px;top:{cad:.0f}px">{ext(idp + '_ll', muslo, canilla)}</div>
  <div class="pzj" style="left:{cx:.1f}px;top:{cad:.0f}px">{ext(idp + '_rl', muslo, canilla)}</div>
  <div class="pzh" id="{idp}_h" style="left:{cx - cab / 2:.0f}px;top:0px;width:{cab:.0f}px;height:{cab:.0f}px;border:{g}px solid {color}">
    <svg viewBox="-30 -30 60 60" style="position:absolute;left:{-g}px;top:{-g}px;width:{cab:.0f}px;height:{cab:.0f}px">{caras}</svg></div>
</div>''')
    # la pose: + = hacia afuera. Brazo izquierdo de la pantalla gira +, el derecho −
    pose_a(idp, None, p)
    I('#' + idp, opacity=0)
    if traza:
        S('#' + idp, t, opacity=1)
        for sid in ('_h', '_t', '_la', '_ra', '_ll', '_rl'):
            pass
        FT(f'#{idp}_h', t, 0.22, {'scale': 0}, {'scale': 1}, 'back.out(2)')
        for k, sid in enumerate(('_tr', '_la', '_ra', '_ll', '_rl')):
            FT(f'#{idp}{sid}', t + 0.08 + k * 0.05, 0.2, {'scaleY': 0}, {'scaleY': 1}, 'power2.out')
        fx(t, 'pop', 0.1)
    else:
        R.pin('#' + idp, t, sc=0.7, g=0.1)
    _sale('#' + idp, t, t1, 0.4)


def pose_a(idp, t, pose, dur=0.28, ease='back.out(1.6)'):
    """cambia de pose (dict de POSES o su nombre) en t (t=None = estado inicial)."""
    p = POSES[pose] if isinstance(pose, str) else pose
    signo = {'la': 1, 'ra': -1, 'll': 1, 'rl': -1}
    for parte, (a1, a2) in p.items():
        s = signo[parte]
        if t is None:
            I(f'#{idp}_{parte}', rotation=s * a1); I(f'#{idp}_{parte}f', rotation=s * a2)
        else:
            T(f'#{idp}_{parte}', t, dur, ease, rotation=s * a1); T(f'#{idp}_{parte}f', t, dur, ease, rotation=s * a2)


def cara(idp, t, nueva, antes=None):
    """cambia la cara en t."""
    for nombre in ('feliz', 'serio', 'triste', 'sorpresa', 'enojado', 'guino'):
        S(f'#{idp}_c{nombre}', t, opacity=1 if nombre == nueva else 0)


def caminar(idp, t0, t1, dx, paso=0.26):
    """camina dx px entre t0 y t1 balanceando brazos y piernas."""
    T('#' + idp, t0, t1 - t0, 'none', x=dx)
    t = t0; k = 0
    while t < t1 - 0.05:
        pose_a(idp, t, 'camina_a' if k % 2 == 0 else 'camina_b', dur=paso * 0.9, ease='sine.inOut'); t += paso; k += 1
    pose_a(idp, t1, 'parado', dur=0.2)


def rebote(idp, t, alto=40, veces=1, dur=0.36):
    """salto en el sitio."""
    for k in range(veces):
        FT('#' + idp, t + k * dur, dur, {'y': 0}, {'y': 0}, 'none')
        T('#' + idp, t + k * dur, dur / 2, 'power2.out', y=-alto); T('#' + idp, t + k * dur + dur / 2, dur / 2, 'power2.in', y=0)


# ===================================================================================================== citas y listas
def escrito(idp, desde, hasta, t_entra, t1, x=60, y=300, ancho=960, fs=38, rojas=(), titulo='', comillas=True, fondo=True, mayus=False):
    """cita literal que se ESCRIBE palabra por palabra mientras se dice (palabras de motor.WD entre `desde` y `hasta`,
    en segundos). Con fondo = tarjeta oscura con un antetítulo rojo (`titulo`)."""
    rojas = {motor.norm(r) for r in rojas}
    ws = [w for w in motor.WD if desde - 0.05 <= w['start'] <= hasta + 0.05]
    sp = ''
    for k, w in enumerate(ws):
        tx = w['text']
        if k == 0: tx = tx[:1].upper() + tx[1:]
        if mayus: tx = tx.upper()
        if comillas and k == 0: tx = '&ldquo;' + tx
        if comillas and k == len(ws) - 1: tx = tx + '&rdquo;'
        cls = ' class="r"' if motor.norm(w['text']) in rojas else ''
        sp += f'<span id="{idp}w{k}"{cls}>{tx}</span> '
    cab = f'<div class="pzeh">{titulo}</div>' if titulo else ''
    add(f'<div class="pze{" pzef" if fondo else ""}" id="{idp}" style="left:{x}px;top:{y}px;width:{ancho}px">{cab}<div class="pzet" style="font-size:{fs}px">{sp}</div></div>')
    R.pin('#' + idp, t_entra, sc=0.85, g=0.1)
    if t1 is not None: R.outo('#' + idp, t1)
    for k, w in enumerate(ws):
        I(f'#{idp}w{k}', opacity=0); S(f'#{idp}w{k}', w['start'] - 0.03, opacity=1)
    return ws


def lista(idp, items, x, y, t1, fs=40, paso=76, ancho=900, color=BLANCO):
    """lista con casillas dibujadas a mano: items = [(texto, t_entra, t_check o None)]. Cada renglón entra con su
    palabra; la casilla se marca con ✓ verde en t_check (None = queda vacía: tareas que se acumulan)."""
    for k, (tx, t, tc) in enumerate(items):
        yy = y + k * paso
        dibujo(f'{idp}b{k}', L('M6,6 H50 V50 H6 Z', 5, color), x, yy, 56, 56, t, t1, dur=0.25, sonido=False)
        add(f'<div class="pzli" id="{idp}t{k}" style="left:{x + 76}px;top:{yy + 2}px;width:{ancho - 76}px;font-size:{fs}px;color:{color}">{tx}</div>')
        R.desde(f'#{idp}t{k}', t, dx=-30, g=0.08)
        if t1 is not None: R.outo(f'#{idp}t{k}', t1)
        if tc is not None:
            dibujo(f'{idp}c{k}', L('M8,30 L26,50 L62,6', 9, '#38D27A'), x + 2, yy - 8, 70, 60, tc, t1, dur=0.2, sonido=False)
            fx(tc, 'ding', 0.08)


# ===================================================================================================== cierre
def cta_comentario(palabra, t, t_palabra, t_burbuja, texto_burbuja='Te escribo por DM &#128233;', titulo='COMENTA', y=470):
    """la caja de comentarios de Instagram con la palabra escrita + burbuja azul (el cierre del estilo).
    t = cuando aparece · t_palabra = cuando dice la PALABRA (se escribe letra a letra) · t_burbuja = la burbuja."""
    add(f'''<div class="pzcta" id="pzcta"><div class="pzct">{titulo}</div>
  <div class="pzcb"><i></i><span id="pzcw">{''.join(f'<b id="pzl{k}">{c}</b>' for k, c in enumerate(palabra))}</span><em id="pzpub">Publicar</em></div>
  <div class="pzbub" id="pzbub">{texto_burbuja}</div></div>''')
    I('#pzcta', opacity=0); S('#pzcta', t, opacity=1)
    R.up('#pzcta .pzct', t, dy=36, g=0.1)
    R.pin('#pzcta .pzcb', t + 0.08, sc=0.7, g=0.12)
    for k in range(len(palabra)):
        I(f'#pzl{k}', opacity=0); S(f'#pzl{k}', t_palabra + k * 0.05, opacity=1)
    fx(t_palabra, 'click', 0.12)
    FT('#pzpub', t_burbuja - 0.14, 0.22, {'scale': 1}, {'scale': 1.25}, 'back.out(3)')
    R.pin('#pzbub', t_burbuja, sc=0.5, rot=(-8, -2), snd='ding', g=0.18)


CSS = '''
.pze{position:absolute;box-sizing:border-box}
.pzef{padding:22px 30px 26px;border-radius:26px;background:#1B1B1F;border:3px solid #34363d;box-shadow:0 18px 40px rgba(0,0,0,.45)}
.pzeh{font-family:"IT";font-weight:800;font-size:24px;letter-spacing:.12em;color:#E5322D;margin-bottom:10px;text-transform:uppercase}
.pzet{font-family:"IT";font-weight:800;line-height:1.22;color:#F4F4F2}
.pzet .r{color:#E5322D}
.pzli{position:absolute;font-family:"IT";font-weight:900;line-height:1.1;text-transform:uppercase;letter-spacing:-.005em}
#rgrid{background-size:54px 54px !important;background-position:0 0 !important;background-image:linear-gradient(var(--gl) 1.5px,transparent 1.5px),linear-gradient(90deg,var(--gl) 1.5px,transparent 1.5px) !important}
#rvigL{background:radial-gradient(circle at 76% 84%,rgba(255,255,255,.10),rgba(255,255,255,0) 34%),radial-gradient(ellipse 80% 60% at 50% 45%,rgba(255,255,255,.035),rgba(0,0,0,0) 70%) !important}
#pzpolvo{position:absolute;left:0;top:0;width:1080px;height:2100px}
#pzpolvo i{position:absolute;border-radius:50%}
.pzfirma{left:0;top:250px;width:1080px;text-align:center;font-family:"IT";font-weight:700;font-size:17px;letter-spacing:.42em;color:rgba(255,255,255,.32)}
.pzk{position:absolute;font-family:"IT";font-weight:900;line-height:1.16;letter-spacing:-.01em;text-align:left}
.pzk .kw{position:relative;display:inline-block;color:#46474e;margin-right:.24em}
.pzk .kw i{position:absolute;left:0;top:0;font-style:normal;color:#F4F4F2;white-space:nowrap}
.pzk .kw.r i{color:#E5322D;text-shadow:0 0 18px rgba(229,50,45,.55)}
.pzg{position:absolute;left:540px;font-family:"IT";font-weight:900;letter-spacing:-.045em;line-height:.92;white-space:nowrap;text-align:center;text-transform:uppercase;text-shadow:0 0 30px rgba(229,50,45,.55),0 0 2px rgba(229,50,45,.9)}
.pzg span{display:inline-block;transform:scaleX(.86)}
.pzf{position:absolute;font-family:"IT";font-weight:900;letter-spacing:-.01em;line-height:1.12;text-transform:uppercase}
.pzc{position:absolute;font-family:"PFI";font-style:italic;font-weight:400;line-height:1.1}
.pzr{position:absolute;font-family:"IT";font-weight:800;letter-spacing:.06em;text-transform:uppercase;white-space:nowrap}
.pzd{position:absolute;overflow:visible}
.pzd .ln{stroke-dasharray:1}
.pzm{position:absolute}
.pzj{position:absolute;width:0;height:0}
.pzl{position:absolute;left:0;top:0;transform-origin:50% 0%}
.pzh{position:absolute;border-radius:50%;box-sizing:border-box;background:#111113}
.pzcta{position:absolute;left:0;top:0;width:1080px;height:1200px}
.pzct{position:absolute;left:0;top:330px;width:1080px;text-align:center;font-family:"IT";font-weight:900;font-size:96px;letter-spacing:-.04em;color:#F4F4F2}
.pzcb{position:absolute;left:110px;top:470px;width:860px;height:124px;border-radius:62px;background:#1E1F24;border:3px solid #34363d;box-shadow:0 18px 40px rgba(0,0,0,.5)}
.pzcb i{position:absolute;left:24px;top:25px;width:74px;height:74px;border-radius:50%;background:linear-gradient(135deg,#f9ce34,#ee2a7b,#6228d7)}
.pzcb span{position:absolute;left:126px;top:20px;font-family:"IT";font-weight:900;font-size:68px;letter-spacing:.02em;color:#F4F4F2}
.pzcb span b{font-weight:900}
.pzcb em{position:absolute;right:40px;top:40px;font-family:"IT";font-style:normal;font-weight:800;font-size:38px;color:#3897F0}
.pzbub{position:absolute;left:450px;top:640px;padding:22px 34px;border-radius:34px 34px 8px 34px;background:#0A84FF;color:#fff;font-family:"IT";font-weight:800;font-size:44px;white-space:nowrap;box-shadow:0 12px 30px rgba(10,132,255,.4)}
'''


def cerrar(musica, volumen_musica=0.24, inicio_musica=0.0, css_extra='', subir_al_final=2.3):
    # la música llega hasta el último cuadro y sube al terminar la voz (si no, verificar_reel.py marca hueco al final)
    if subir_al_final:
        _run0 = motor._run
        _tv = motor.WD[-1]['end'] + 0.02                      # sube apenas termina la voz y solo se apaga en los últimos 0.15 s
        sub = f"volume='if(gte(t,{_tv:.2f}),{subir_al_final},1)':eval=frame,afade=t=out:st={motor.DUR - 0.17:.3f}:d=0.15"
        motor._run = lambda cmd: _run0([re.sub(r'afade=t=out:st=[\d.]+:d=1\.3', sub, c) for c in cmd])
    R.cerrar(musica=musica, volumen_musica=volumen_musica, inicio_musica=inicio_musica, css_extra=CSS + css_extra,
             fade_corto=not subir_al_final)
