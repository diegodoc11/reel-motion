# -*- coding: utf-8 -*-
"""
reel-motion · ESTILO NOCHE  (plantilla/noche.py + plantilla/noche.css)
======================================================================
El segundo estilo de la skill (el primero, "collage", es el de plantilla/build.py). Sale de tres reels que gustaron
mucho y lo generaliza en piezas reutilizables:

  card  = fondo TINTA con grano + grilla que deriva + viñeta + marcas de corte; el presentador recortado sobre la
          tarjeta de color (encuadre estándar del motor: tarjeta en y 759, presentador a 0.8)
  split = panel de PAPEL crema con grano, puntos de cuaderno y borde rasgado; debajo, el presentador
  un solo acento (el color de marca), cifras gigantes, entradas con golpe (back.out / expo.out) + pop / thump

Uso (reel completo de ejemplo: plantilla/build_noche.py):

    sys.path.insert(0, os.path.join(SKILL, 'scripts')); sys.path.insert(0, os.path.join(SKILL, 'plantilla')); sys.path.insert(0, P)
    import motor
    motor.iniciar(P, correcciones={...}, colores={'acento': '#D11F1D'})
    from motor import *
    import noche as N
    N.escenario()                                     # en vez de escenario('card')
    N.gancho('Primeras palabras del video', hasta=f('...'))
    pp = N.papel('pp1')                               # panel de papel para el encuadre split
    N.a_split(f('...'), pp)  ·  N.a_card(f('...'))    # cambios de encuadre (en vez de ir_a)
    N.checklist('e3', t0, t1, items=[...], en=pp)     # en=pp -> la pieza va DENTRO del papel
    subtitulos(desde=..., cambios=[...])
    N.cerrar(musica='auto')                           # en vez de cerrar(): agrega el papel y el CSS del estilo

Convenciones de TODAS las piezas
  idp      texto corto y único por pieza: letras y números ('e1', 'e2'…). Los ids internos son idp + '-' + sufijo.
  t0 / t1  segundo en que entra el bloque / en que TERMINA de salir (None = se queda; dentro del papel se va con él).
  textos   admiten HTML y entidades (&aacute;, &iquest;, <br>). Los tiempos SIEMPRE salen de f('palabra').
  en       None = zona de gráficos del encuadre card (x 78-1002, y 262-740)  ·  un panel de N.papel() = dentro del papel.
Las piezas se ajustan solas al largo del texto (bajan de tamaño hasta 40 px) y avisan en consola si algo no cabe
o si lo último que entra se ve menos de 0.45 s.
"""
import os, re, math, html, random, colorsys
import motor
from motor import I, S, T, FT, win, fx, typed, flash, rise, jag

AQUI = os.path.dirname(os.path.abspath(__file__))
ZX0, ZY0, ZX1, ZY1 = 78, 262, 1002, 740            # zona de gráficos del encuadre card (en el papel vale la misma)
ZW, ZH = ZX1 - ZX0, ZY1 - ZY0                        # 924 x 478
X_PASO = 390                                         # con la pestaña de paso() visible, lo demás va de x 390 a 1002

PALETA = {'fondo': '#0E1013',        # tinta del fondo
          'panel': '#1A1D22',        # tarjetas oscuras sobre la tinta
          'crema': '#F3F0E8',        # texto sobre la tinta
          'gris': '#9EA3AB',         # antetítulos
          'gris2': '#C9CCD1',        # texto secundario
          'tinta_papel': '#16181C'}  # texto sobre el papel
# El acento sale de motor.iniciar(..., colores={'acento': '#...'}). Para cambiar la tinta: N.PALETA['fondo'] = '#121216'

_IDS = set(); _PANELES = []; _RIELES = []; _PASOS = []; _CAMBIOS = []
_EST = {'sombra': False, 'recorte': False, 'zoom': False, 'gancho': 0}


# =====================================================================================================
#  COLOR Y MEDIDAS
# =====================================================================================================
def _rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def _hex(rgb):
    return '#%02X%02X%02X' % tuple(max(0, min(255, int(round(c)))) for c in rgb)

def _tono(h, dl=0.0, ds=0.0):
    """mismo color con más/menos luz (dl) y saturación (ds), en HLS."""
    r, g, b = [c / 255 for c in _rgb(h)]; hh, l, s = colorsys.rgb_to_hls(r, g, b)
    return _hex([c * 255 for c in colorsys.hls_to_rgb(hh, max(0, min(1, l + dl)), max(0, min(1, s + ds)))])

def acento():          return motor.RED                     # rellenos (tarjeta, cajas, pestañas)
def acento_claro():    return _tono(motor.RED, 0.07, 0.05)  # texto en acento SOBRE LA TINTA (se lee mejor)
def acento_oscuro():   return _tono(motor.RED, -0.02, 0.0)  # texto en acento SOBRE EL PAPEL

def _plano(s):
    return html.unescape(re.sub(r'<[^>]+>', '', str(s)))

# ancho de cada letra en em (letter-spacing 0), MEDIDO en Chrome con las fuentes de recursos/fonts
_MEDIDAS = {
    'it9': [('→—', 1), ('0D', .71), ('1', .43), ('2bdgpq', .62), ('35', .65), ('4', .68), ('689Z+×&', .67), ('7cekvyé?¿', .58),
            (' ', .18), ('axzá', .57), ('f', .38), ('hnuúñüP', .63), ('ijlíIÍ', .27), ('m', .92), ('oóEÉ"', .6), ('r', .41),
            ('sFJ', .56), ('t/', .39), ('w', .85), ('AOQVÁÓ', .77), ('BRS$#', .64), ('CG', .75), ('H', .73), ('K', .69), ('L', .55),
            ('M', .91), ('NUÚÑ', .7), ('T«»', .66), ('W@', 1.07), ('XY', .74), (".:;¡'·", .35), (',', .37), ('!()', .36), ('%', .87),
            ('-', .45), ('*', .59), ('↓', .93), ('…', .76), ('–', .5)],
    'it8': [('→—', 1), ('0', .68), ('1', .41), ('2bdghnpquúñü', .61), ('3B»', .64), ('4+×&', .66), ('5RS$«#', .63), ('689TZ', .65),
            ('7axáF"*', .56), (' ', .19), ('cekvyé', .57), ('f/', .37), ('ijlíIÍ', .26), ('mM', .9), ('oóEÉ', .59), ('r', .39),
            ('szJ?¿', .55), ('t', .38), ('w', .83), ('AGVÁ', .74), ('C', .73), ('DNUÚÑ', .7), ('HY', .72), ('K', .67), ('L', .54),
            ('OQÓ…', .76), ('P', .62), ('W', 1.04), ('X', .71), (".:;!¡'·", .33), (',', .34), ('%', .85), ('()', .35), ('-', .44),
            ('@', 1.03), ('↓', .93), ('–', .5)],
    'cav': [('→', 1), ('0123478abñ$+×–', .45), ('5', .43), ('6FP', .47), ('9á', .44), (' "', .24), ('cgorx*', .36), ('dÍ', .4),
            ('ezé/()-', .33), ('fJ', .31), ('hUYÚ', .48), ('i!¡', .21), ('j', .23), ('kpq', .38), ('lí·', .19), ('m', .58), ('nT', .46),
            ('styó', .35), ('uúü?¿', .37), ('v', .34), ('wBXZ', .52), ('A', .51), ('CQSV', .49), ('D…', .59), ('E', .53),
            ('GKORÁÓ↓', .5), ('HNÑ—', .57), ('IL', .41), ('M', .73), ('W', .72), ('É', .55), ('.,:;', .2), ('%', .6), ('«', .65),
            ('»', .71), ("'", .12), ('&#', .56), ('@', .64)],
    'int': [('%@→—', 1), ('0BT&*', .66), ('1', .42), ('2bdpq', .62), ('3689#', .64), ('4+×', .67), ('5hnouóúñüEÉ', .61), ('7cJ', .58),
            (' ', .25), ('akxzáL', .57), ('eéF', .59), ('f', .39), ('g«»', .63), ('ijlí', .26), ('m', .9), ('r', .41), ('s', .55),
            ('t()', .37), ('vy', .6), ('w', .84), ('AVÁ', .73), ('CUÚ', .74), ('DX', .72), ('GH', .75), ('IÍ', .28), ('K', .7),
            ('M', .92), ('NÑ', .76), ('OQÓ', .77), ('PRSZ$', .65), ('W', 1.02), ('Y', .71), ('.,:!¡·', .32), (";'", .33), ('?¿', .54),
            ('/', .38), ('-', .47), ('"', .52), ('↓', .88), ('…', .96), ('–', .5)],
}
_TABLAS = {k: {c: w for cs, w in v for c in cs} for k, v in _MEDIDAS.items()}

def _ancho(s, fs, tracking=-0.04, fuente='it9'):
    """ancho en px de un texto: fuente 'it9' (Inter Tight 900, titulares y cifras) · 'it8' (800) · 'cav' (Caveat) ·
    'int' (Inter, chat) · 'mono' (JetBrains Mono). tracking = letter-spacing en em."""
    t = _plano(s)
    if fuente == 'mono': return len(t) * fs * (0.6 + tracking)
    tb = _TABLAS[fuente]
    return sum(tb.get(c, 0.62) + tracking for c in t) * fs

def _cabe(s, fs_max, ancho_max, fs_min=40, tracking=-0.04, fuente='it9', quien=''):
    """mayor tamaño (<= fs_max) con el que `s` cabe en `ancho_max` px; avisa si ni con fs_min cabe."""
    w = _ancho(s, 100, tracking, fuente) / 100
    if w <= 0: return fs_max
    fs = int(min(fs_max, ancho_max / w))
    if fs < fs_min:
        print(f'  (aviso) {quien}: "{_plano(s)}" no cabe en {ancho_max:.0f} px ni a {fs_min} px. Acórtalo o pártelo con <br>.')
        return fs_min
    return fs

def _aviso(idp, t_ultimo, t1):
    if t1 is not None and t1 - t_ultimo < 0.45:
        print(f'  (aviso) {idp}: lo último entra en {t_ultimo:.2f}s y el bloque sale en {t1:.2f}s (se ve {t1 - t_ultimo:.2f}s). '
              f'Déjalo más tiempo (t1 más tarde) o adelántalo.')

def _id(idp):
    if not re.match(r'^[A-Za-z][A-Za-z0-9_]*$', idp):
        raise SystemExit(f"noche: idp '{idp}' no sirve: usa letras y números, sin guiones ni espacios (ej. 'e3')")
    if idp in _IDS: raise SystemExit(f"noche: el idp '{idp}' está repetido: cada pieza necesita uno distinto")
    _IDS.add(idp)
    return idp


# =====================================================================================================
#  ICONOS (trazo; 24x24 salvo los marcados con 120)  ->  icono('robot', 64, '#fff')
# =====================================================================================================
def _engrane_d(cx=60, cy=60, ro=52, ri=40, n=8):
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        for da, r in ((-0.27, ri), (-0.15, ro), (0.15, ro), (0.27, ri)):
            aa = a + da * 2 * math.pi / n; pts.append((cx + r * math.cos(aa), cy + r * math.sin(aa)))
    return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + ' Z'

ICONOS = {   # nombre: (caja del viewBox, trazos, relleno)
    'chat': (24, '<path d="M20.5 11.6a8.6 8.6 0 0 1-12.5 7.6L3.4 20.6l1.5-4.5A8.6 8.6 0 1 1 20.5 11.6z"/>', False),
    'bot': (24, '<rect x="4" y="8" width="16" height="12" rx="3.5"/><path d="M12 4.6V8"/><circle cx="12" cy="3.4" r="1.4"/>'
                '<path d="M1.8 12.8v3.4M22.2 12.8v3.4"/><circle cx="9" cy="14" r="1.6" fill="currentColor" stroke="none"/>'
                '<circle cx="15" cy="14" r="1.6" fill="currentColor" stroke="none"/>', False),
    'robot': (24, '<rect x="4.5" y="8" width="15" height="11" rx="3"/><path d="M12 4.5V8"/><circle cx="12" cy="3.6" r="1.1"/>'
                  '<circle cx="9.3" cy="13" r="1.3"/><circle cx="14.7" cy="13" r="1.3"/><path d="M9.5 16.3h5M2.5 12.5v3M21.5 12.5v3"/>', False),
    'persona': (24, '<circle cx="12" cy="8" r="4.2"/><path d="M3.8 21.2c0-4.6 3.7-7.4 8.2-7.4s8.2 2.8 8.2 7.4"/>', False),
    'documento': (24, '<path d="M6 2.8h8.2L19 7.6v13.6H6z"/><path d="M14 2.8v5h5"/><path d="M9 12.4h7M9 16.4h7"/>', False),
    'diana': (24, '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.4" fill="currentColor"/>', False),
    'idea': (24, '<path d="M9 18.2h6M10 21.4h4"/><path d="M8.3 14.6a6.3 6.3 0 1 1 7.4 0c-.8.7-1.4 1.6-1.4 2.9H9.7c0-1.3-.6-2.2-1.4-2.9z"/>', False),
    'decision': (24, '<path d="M12 21.6v-8.2"/><path d="M12 13.4L6.4 7.8"/><path d="M12 13.4l5.6-5.6"/><path d="M4.8 11.6V6.2h5.4"/><path d="M19.2 11.6V6.2h-5.4"/>', False),
    'herramienta': (24, '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.7 2.7-2.1-2.1 2.8-2.6z"/>', False),
    'check': (24, '<path d="M4.6 12.6l4.9 4.9L19.4 7.4"/>', False),
    'bucle': (24, '<path d="M20 12a8 8 0 1 1-2.4-5.7"/><path d="M20 3.6v5h-5"/>', False),
    'campana': (24, '<path d="M6 16.4V11a6 6 0 0 1 12 0v5.4l2 2.1H4z"/><path d="M10 21.4h4"/>', False),
    'chispa': (24, '<path d="M12 2.6l2.1 6.3 6.3 2.1-6.3 2.1-2.1 6.3-2.1-6.3-6.3-2.1 6.3-2.1z"/>', False),
    'flecha': (24, '<path d="M3 12h17"/><path d="M14 5.6l6.4 6.4-6.4 6.4"/>', False),
    'reloj': (24, '<circle cx="12" cy="12" r="9"/><path d="M12 7v5.2l3.2 2"/>', False),
    'correo': (24, '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6.5l8.5 6.5 8.5-6.5"/>', False),
    'calendario': (24, '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>', False),
    'etiqueta': (24, '<path d="M3 12.2V4h8.2L21 13.8 13.8 21z"/><circle cx="7.6" cy="8.6" r="1.5"/>', False),
    'birrete': (24, '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c0 1.6 2.7 3 6 3s6-1.4 6-3v-5"/><path d="M22 9v6"/>', False),
    'ubicacion': (24, '<path d="M12 21.5s-6.5-6-6.5-11.5a6.5 6.5 0 0 1 13 0c0 5.5-6.5 11.5-6.5 11.5z"/><circle cx="12" cy="10" r="2.4"/>', False),
    'alerta': (24, '<path d="M12 3.5L2.5 20h19z"/><path d="M12 10v4.5M12 17.3v.1"/>', False),
    'portapapeles': (24, '<rect x="5" y="4" width="14" height="17" rx="2.2"/><path d="M9 4.2V3h6v1.2"/><path d="M12 9.5v6M9 12.5h6"/>', False),
    'pesa': (24, '<path d="M6.5 7v10M3.5 9.5v5M17.5 7v10M20.5 9.5v5M6.5 12h11"/>', False),
    'sofa': (24, '<path d="M5 11V8.5A2.5 2.5 0 0 1 7.5 6h9A2.5 2.5 0 0 1 19 8.5V11"/><path d="M3 12.5a1.8 1.8 0 0 1 3.6 0V15h10.8v-2.5a1.8 1.8 0 0 1 3.6 0V17a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17z"/><path d="M5.5 18.5V20M18.5 18.5V20"/>', False),
    'repetir': (24, '<path d="M17 2.5l3 3-3 3"/><path d="M4 11V9.5a4 4 0 0 1 4-4h12"/><path d="M7 21.5l-3-3 3-3"/><path d="M20 13v1.5a4 4 0 0 1-4 4H4"/>', False),
    'carro': (24, '<path d="M3 16.5V13l2.2-4.2A2 2 0 0 1 7 7.7h7.6a2 2 0 0 1 1.5.7L19.5 12H21v4.5"/><circle cx="7.5" cy="16.8" r="2.1"/><circle cx="16.8" cy="16.8" r="2.1"/><path d="M9.6 16.8h5.1M3 12.5h16"/>', False),
    'timon': (24, '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2.6"/><path d="M3.4 10.6l6.1 1M20.6 10.6l-6.1 1M12 14.6V21"/>', False),
    'colegio': (24, '<path d="M2.5 21h19M4.5 21V10.5L12 5.5l7.5 5V21"/><path d="M9.8 21v-5.2h4.4V21"/><path d="M12 5.5V2.2h3.2"/><path d="M7.5 13h1.5M15 13h1.5"/>', False),
    'certificado': (24, '<rect x="3" y="3.5" width="18" height="12.5" rx="1.6"/><path d="M7 7.5h10M7 10.5h6"/><circle cx="16.5" cy="15.8" r="2.8"/><path d="M15 18.2L14.4 22l2.1-1.1 2.1 1.1-.6-3.8"/>', False),
    'huella': (24, '<ellipse cx="6.8" cy="10.2" rx="1.8" ry="2.3"/><ellipse cx="10.4" cy="6.4" rx="1.8" ry="2.3"/><ellipse cx="14.8" cy="6.6" rx="1.8" ry="2.3"/><ellipse cx="18.2" cy="10.6" rx="1.8" ry="2.3"/><path d="M8.6 17.3c0-2.9 1.6-5.1 3.6-5.1s3.6 2.2 3.6 5.1c0 1.9-1.6 2.9-3.6 2.2-2 .7-3.6-.3-3.6-2.2z"/>', False),
    'impresora': (24, '<path d="M7 8.5V3h10v5.5"/><rect x="3" y="8.5" width="18" height="8.5" rx="2"/><path d="M7 14h10v7H7z"/><path d="M17.5 11.5h.5"/>', False),
    'rayo': (24, '<path d="M13.2 2L4.5 13.6h6.3L9.9 22l8.6-11.6h-6.3z"/>', True),
    'estrella': (24, '<path d="M12 2.8l2.8 5.8 6.3.9-4.6 4.4 1.1 6.3L12 17.2l-5.6 3 1.1-6.3L2.9 9.5l6.3-.9z"/>', True),
    'tienda': (120, '<path d="M14 46 L24 16 H96 L106 46"/><path d="M22 58 V104 H98 V58"/><path d="M36 104 V74 H56 V104"/><rect x="66" y="70" width="22" height="18" rx="2"/>', False),
    'lupa': (120, '<circle cx="50" cy="50" r="31"/><path d="M73 73 L102 102"/>', False),
    'megafono': (120, '<path d="M18 50 L74 24 V96 L18 70 Z"/><path d="M18 50 H10 V70 H18"/><path d="M30 74 L40 104 H54 L46 78"/><path d="M86 46 Q96 60 86 74"/><path d="M96 36 Q112 60 96 84"/>', False),
    'mundo': (120, '<circle cx="60" cy="60" r="42"/><ellipse cx="60" cy="60" rx="18" ry="42"/><path d="M18 60 H102 M25 39 H95 M25 81 H95"/>', False),
    'pluma': (120, '<path d="M60 14 L90 62 L60 106 L30 62 Z"/><circle cx="60" cy="64" r="8"/><path d="M60 14 V56"/>', False),
    'edificio': (120, '<rect x="28" y="16" width="64" height="90" rx="3"/><path d="M42 32 h12 M66 32 h12 M42 50 h12 M66 50 h12 M42 68 h12 M66 68 h12"/><path d="M52 106 V88 H68 V106"/>', False),
    'capas': (120, '<rect x="18" y="20" width="84" height="22" rx="5"/><rect x="18" y="49" width="84" height="22" rx="5"/><rect x="18" y="78" width="84" height="22" rx="5"/>', False),
    'engrane': (120, f'<path d="{_engrane_d()}"/><circle cx="60" cy="60" r="15"/>', False),
    'dinero': (24, '<rect x="2.5" y="6" width="19" height="12" rx="2"/><circle cx="12" cy="12" r="2.8"/><path d="M6 9.5v.1M18 14.5v.1"/>', False),
    'grafica': (24, '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 6-7"/><path d="M15 7h5v5"/>', False),
}

def icono(nombre, tam=48, color='currentColor', grosor=2.2, cls='', idp=''):
    """SVG de un icono de ICONOS. color = cualquier color CSS ('currentColor' = el color del texto donde va)."""
    if nombre not in ICONOS: raise SystemExit(f"noche: el icono '{nombre}' no existe. Hay: {', '.join(sorted(ICONOS))}")
    vb, d, lleno = ICONOS[nombre]
    i_ = f' id="{idp}"' if idp else ''; c_ = f' class="{cls}"' if cls else ''
    st = '' if color == 'currentColor' else f' style="color:{color}"'
    if lleno: return f'<svg{i_}{c_} width="{tam}" height="{tam}" viewBox="0 0 {vb} {vb}" fill="{color}"{st}>{d}</svg>'
    return (f'<svg{i_}{c_} width="{tam}" height="{tam}" viewBox="0 0 {vb} {vb}" fill="none" stroke="{color}" '
            f'stroke-width="{grosor * vb / 24:g}" stroke-linecap="round" stroke-linejoin="round"{st}>{d}</svg>')

_svgico = icono       # alias: dentro de las piezas el parámetro `icono` tapa a la función


# =====================================================================================================
#  ATAJOS DE ANIMACIÓN (golpes)
# =====================================================================================================
def entra(sel, t, dur=0.36, ease='expo.out', y=36, x=0, escala=None, rot=None, snd='pop', g=0.16, origen=None):
    """aparece con golpe: desde y/x desplazado, escala y giro opcionales."""
    a = {'opacity': 0}; b = {'opacity': 1}
    if y: a['y'] = y; b['y'] = 0
    if x: a['x'] = x; b['x'] = 0
    if escala is not None: a['scale'] = escala; b['scale'] = 1
    if rot is not None: a['rotation'] = rot[0]; b['rotation'] = rot[1]
    if origen: a['transformOrigin'] = origen
    I(sel, **a); T(sel, t, dur, ease, **b)
    if snd: fx(t, snd, g)

def sacude(sel, t, a=9):
    """sacudida horizontal de 6 cuadros."""
    FT(sel, t, 0.035, {'x': -a}, {'x': a, 'yoyo': True, 'repeat': 5}, 'none'); S(sel, t + 0.22, x=0)

def golpe(sel, t, s0=1.9, r0=0.0, r1=0.0, dur=0.32, snd='thump', g=0.3, sh=8):
    """entra GRANDE y cae a su tamaño (expo.out) + thump + sacudida (sh=0 sin sacudida)."""
    I(sel, opacity=0, scale=s0, rotation=r0); T(sel, t, dur, 'expo.out', opacity=1, scale=1, rotation=r1)
    if snd: fx(t, snd, g)
    if sh: sacude(sel, t + dur + 0.01, sh)

def sube(sel, t, snd='swipe', g=0.14, dur=0.36):
    """línea que sube tras su máscara (.ln > .in) + sonido."""
    rise(sel, t, dur)
    if snd: fx(t, snd, g)

def sale(sel, t, dur=0.16, y=-34):
    """sale hacia arriba desvaneciéndose, TERMINANDO en t."""
    T(sel, t - dur, dur, 'power2.in', opacity=0, y=y)

def dibuja(sel, t, dur=0.3, ease='power1.inOut', snd=None, g=0.14):
    """trazo SVG que se dibuja (el path debe tener pathLength="100": los hace _svgp)."""
    I(sel, strokeDasharray=100, strokeDashoffset=100, opacity=0); S(sel, t, opacity=1); T(sel, t, dur, ease, strokeDashoffset=0)
    if snd: fx(t, snd, g)

def barre(sel, t, dur=0.34, snd='swipe', g=0.13):
    """se revela de izquierda a derecha (clip)."""
    I(sel, clipPath='inset(-20% 100% -20% 0%)'); T(sel, t, dur, 'power3.out', clipPath='inset(-20% 0% -20% 0%)')
    if snd: fx(t, snd, g)

def escribe(sel, t, dur=0.4, snd=0.12):
    """texto que se escribe a mano (revelado de izquierda a derecha con sonido de trazo)."""
    motor.handwrite(sel, t, dur, snd)

def linea(lid, texto, cls=''):
    """una línea con máscara para sube()/rise()."""
    return f'<div class="ln"><span class="in {cls}" id="{lid}">{texto}</span></div>'

def zoom(t, escala, dur=0.6, ease='power2.inOut'):
    """acerca / aleja SOLO el presentador recortado, alrededor de su cara (la tarjeta no cambia). 1.0 = normal."""
    if not _EST['zoom']:
        I('#cutv', transformOrigin=f'{motor.FACE.cx:.0f}px {motor.FACE.cy:.0f}px'); _EST['zoom'] = True
    T('#cutv', t, dur, ease, scale=escala)

def _seq(pid, items):
    """[(texto, segundo, clase)] -> cada valor se ve desde su segundo hasta el siguiente (el último se queda)."""
    o = ''
    for i, it in enumerate(items):
        v, t_ = it[0], it[1]; c = it[2] if len(it) > 2 else ''
        o += f'<span class="stp {c}" id="{pid}{i}">{v}</span>'
        I(f'#{pid}{i}', opacity=0); S(f'#{pid}{i}', t_, opacity=1)
        if i + 1 < len(items): S(f'#{pid}{i}', items[i + 1][1], opacity=0)
    return o


# --------- trazos "a mano" (SVG con pathLength=100 para dibuja()) ---------
def _elipse_d(cx, cy, rx, ry, semilla=1, vueltas=1.1):
    r = random.Random(semilla); n = 44; pts = []; a0 = r.uniform(-2.5, -2.0)
    for i in range(n + 1):
        a = a0 + 2 * math.pi * vueltas * i / n
        k = 1 + 0.035 * math.sin(3 * a + semilla) + r.uniform(-0.012, 0.012) + 0.05 * i / n
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)

def _rect_d(x, y, w, h, semilla=1, j=3.0):
    r = random.Random(semilla)
    p = [(x + r.uniform(-j, j), y + r.uniform(-j, j)), (x + w + r.uniform(-j, j), y + r.uniform(-j, j)),
         (x + w + r.uniform(-j, j), y + h + r.uniform(-j, j)), (x + r.uniform(-j, j), y + h + r.uniform(-j, j))]
    d = f'M{p[0][0]:.1f},{p[0][1]:.1f}'
    for i in range(1, 5):
        a = p[i - 1]; b = p[i % 4]
        d += f' Q{(a[0] + b[0]) / 2 + r.uniform(-j, j):.1f},{(a[1] + b[1]) / 2 + r.uniform(-j, j):.1f} {b[0]:.1f},{b[1]:.1f}'
    return d + f' L{p[0][0] + 9:.1f},{p[0][1] - 1.5:.1f}'

def _linea_d(x0, y0, x1, y1, semilla=1, comba=6):
    r = random.Random(semilla)
    return f'M{x0:.1f},{y0:.1f} Q{(x0 + x1) / 2:.1f},{(y0 + y1) / 2 + r.uniform(-comba, comba):.1f} {x1:.1f},{y1:.1f}'

def _svgp(pid, d, w, h, grosor=6, cls='', color='currentColor'):
    return (f'<svg class="{cls}" width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}" style="overflow:visible">'
            f'<path id="{pid}" pathLength="100" d="{d}" fill="none" stroke="{color}" stroke-width="{grosor}" '
            f'stroke-linecap="round" stroke-linejoin="round"/></svg>')

def _equis(pid, w, h, grosor=16, pad=12, cls='', color='currentColor'):
    return (f'<svg class="{cls}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="overflow:visible">'
            f'<path id="{pid}a" pathLength="100" d="M{pad} {pad} L{w - pad} {h - pad}" fill="none" stroke="{color}" stroke-width="{grosor}" stroke-linecap="round"/>'
            f'<path id="{pid}b" pathLength="100" d="M{w - pad} {pad} L{pad} {h - pad}" fill="none" stroke="{color}" stroke-width="{grosor}" stroke-linecap="round"/></svg>')

def _dibuja_equis(pid, t, g=0.3, d=0.12):
    dibuja(f'#{pid}a', t, d, 'none'); dibuja(f'#{pid}b', t + d, d, 'none')
    if g: fx(t, 'thump', g)

CHECK_D = 'M8 30 L24 46 L56 10'
TICKS = ('<svg class="ntick" viewBox="0 0 24 16" width="40" height="27" fill="none" stroke="#3FA9E0" stroke-width="2.4" '
         'stroke-linecap="round" stroke-linejoin="round"><path d="M1.6 8.6l3.8 3.8L13.4 3.6"/><path d="M10 12.4l.2.2L18.4 3.6"/></svg>')


# =====================================================================================================
#  TEXTURAS (se generan una vez en <proyecto>/assets)
# =====================================================================================================
def _grano():
    """assets/ngrano-l.png (motas claras, para la tinta) y ngrano-d.png (motas oscuras, para la tarjeta y el papel)."""
    import numpy as np
    from PIL import Image
    os.makedirs(os.path.join(motor.P, 'assets'), exist_ok=True)
    for nombre, rgb, sem in (('ngrano-l', (255, 255, 255), 7), ('ngrano-d', (0, 0, 0), 8)):
        fn = os.path.join(motor.P, 'assets', nombre + '.png')
        if os.path.exists(fn): continue
        a = np.clip(np.random.default_rng(sem).normal(9.5, 7.6, (320, 320)), 0, 26).astype(np.uint8)
        im = np.zeros((320, 320, 4), np.uint8); im[..., :3] = rgb; im[..., 3] = a
        Image.fromarray(im, 'RGBA').save(fn, optimize=True)

def _papel_png(pid, semilla):
    """papel crema 1080x830: grano + fibras + puntos de cuaderno + borde rasgado con antialias. Uno por panel
    (HyperFrames no quiere el mismo archivo en dos <img>)."""
    rel = f'assets/npapel-{pid}-{semilla}.png'; fn = os.path.join(motor.P, rel)
    if os.path.exists(fn): return rel
    import numpy as np, cv2
    from PIL import Image, ImageDraw
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    rg = np.random.default_rng(semilla); Wp, Hp = motor.W, 830
    img = np.empty((Hp, Wp, 3), np.float32); img[:] = (242, 237, 225)
    low = cv2.resize(rg.standard_normal((Hp // 70 + 3, Wp // 70 + 3)).astype(np.float32), (Wp, Hp), interpolation=cv2.INTER_CUBIC)
    img += low[..., None] * np.array([2.8, 2.6, 2.2], np.float32)
    img += cv2.GaussianBlur(rg.standard_normal((Hp, Wp)).astype(np.float32), (0, 0), 0.7)[..., None] * 5.0
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8)).convert('RGBA')
    ov = Image.new('RGBA', (Wp, Hp), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for _ in range(220):                                                         # fibras
        x = rg.uniform(0, Wp); y = rg.uniform(0, Hp); L_ = rg.uniform(8, 34); a = rg.uniform(0, math.pi)
        d.line([(x, y), (x + L_ * math.cos(a), y + L_ * math.sin(a))], fill=(120, 104, 82, int(rg.uniform(8, 22))), width=1)
    for yy in range(18, Hp, 36):                                                 # cuaderno punteado
        for xx in range(18, Wp, 36):
            d.ellipse([xx - 1.7, yy - 1.7, xx + 1.7, yy + 1.7], fill=(40, 34, 28, 34))
    im = Image.alpha_composite(im, ov)
    K = 4                                                                        # borde rasgado (4x para suavizar)
    e1 = jag(motor.PAPER_H - 12, 9, 26, semilla); e2 = jag(motor.PAPER_H + 5, 9, 22, semilla + 5)
    m1 = Image.new('L', (Wp * K, Hp * K), 0); m2 = Image.new('L', (Wp * K, Hp * K), 0)
    ImageDraw.Draw(m1).polygon([(0, 0), (Wp * K, 0)] + [(x * K, y * K) for x, y in reversed(e1)], fill=255)
    ImageDraw.Draw(m2).polygon([(0, 0), (Wp * K, 0)] + [(x * K, y * K) for x, y in reversed(e2)], fill=255)
    m1 = m1.resize((Wp, Hp), Image.LANCZOS); m2 = m2.resize((Wp, Hp), Image.LANCZOS)
    out = Image.composite(im, Image.new('RGBA', (Wp, Hp), (251, 249, 243, 255)), m1); out.putalpha(m2)
    out.save(fn, optimize=True)
    return rel


# =====================================================================================================
#  ESCENARIO, PAPEL Y CAMBIOS DE ENCUADRE
# =====================================================================================================
def escenario(marcas=True, sombra=False, deriva=108):
    """Fondo del estilo (va UNA vez, antes de las escenas; reemplaza a escenario('card')): tinta con grano, grilla doble
    que deriva despacio, foco suave, viñeta y marcas de corte en las esquinas de la zona de gráficos.
    El reel arranca en 'card'. sombra=True agrega una sombra dura crema detrás de la tarjeta."""
    motor.escenario('card')
    _grano()
    mk = ''.join(f'<i class="nmk nm{k}"></i>' for k in (1, 2, 3, 4)) if marcas else ''
    motor.parts.append(f'<div id="nkit"><div id="nkgrid"></div><div id="nkspot"></div><div id="nkvig"></div>{mk}</div>'
                       + ('<div id="nksh"></div>' if sombra else '') + '<div id="nkbot"></div>')
    T('#nkgrid', 0, motor.DUR, 'none', y=deriva)
    I('#nkbot', opacity=0)
    _EST['sombra'] = sombra

class Papel:
    """Panel de papel para el encuadre split. Las piezas entran a él con en=<este panel>."""
    def __init__(self, pid, semilla):
        self.pid = pid; self.sel = '#' + pid; self.hijos = []
        self.img = _papel_png(pid, semilla)
        I(self.sel, y=-(motor.PAPER_H + 60))                     # escondido arriba hasta que a_split() lo baje
        _PANELES.append(self)
    def add(self, h): self.hijos.append(h)
    def html(self):
        return f'<div class="paper npap" id="{self.pid}"><img class="npimg" src="{self.img}" alt="">{"".join(self.hijos)}</div>'

def papel(pid='pp1', semilla=None):
    """Crea un panel de papel (uno por cada tramo en split; cada uno con su propia textura).
    pid = id del panel ('pp1', 'pp2'…) · semilla = otra forma del borde rasgado."""
    _id(pid)
    return Papel(pid, semilla if semilla is not None else 11 + 12 * len(_PANELES))

def a_split(t, panel, recorte=False):
    """Cambia al encuadre split en el segundo t: el panel de papel baja y el presentador queda debajo.
    recorte=False -> debajo se ve la toma REAL con su fondo (como ir_a('split') del motor).
    recorte=True  -> debajo sigue el presentador RECORTADO sobre la tinta con grilla (más 'noche').
    Desde split, a_split(t, otro_panel) cambia de papel. Devuelve cuánto dura la transición."""
    sel = panel.sel if isinstance(panel, Papel) else panel
    antes = motor.ESTADO; rec_antes = _EST['recorte'] and antes == 'split'
    if antes == 'full': raise SystemExit("noche: a_split() desde 'full' no está soportado (el estilo noche usa card y split)")
    if recorte and antes == 'card':
        fuera = -(motor.PAPER_H + 60)
        T('#fillA', t, 0.16, 'power1.in', opacity=0)
        T('#cam', t + 0.04, 0.5, 'power3.inOut', **motor.CAM['split'])
        I(sel, y=fuera); T(sel, t + 0.1, 0.5, 'expo.out', y=0)
        fx(t, 'whoosh', 0.3); motor.ESTADO = 'split'; motor.PAPEL = sel; d = 0.6
        if not motor.SPLIT_OK: print(f"  (aviso) a_split({t:.2f}): en este video la cara es muy grande para 'split'.")
    else:
        d = motor.ir_a('split', t, papel=sel)
    if recorte:
        if antes == 'split' and not rec_antes:                    # papel con toma real -> papel con recorte
            S('#cutv', t + 0.2, opacity=1); S('#v', t + 0.24, opacity=0); S('#nkit', t + 0.2, opacity=1)
        T('#nkbot', t + 0.2, 0.3, 'power1.out', opacity=1)
    else:
        if rec_antes:                                              # papel con recorte -> papel con toma real
            S('#v', t + 0.2, opacity=1); S('#cutv', t + 0.24, opacity=0); T('#nkbot', t + 0.2, 0.2, 'power1.in', opacity=0)
        S('#nkit', t + (0.2 if antes == 'split' else 0), opacity=0)
    if _EST['sombra']: S('#nksh', t, opacity=0)
    _EST['recorte'] = recorte
    _CAMBIOS.append((t, 'split'))
    return d

def a_card(t):
    """Vuelve al encuadre card (tarjeta con el presentador recortado) en el segundo t. Devuelve cuánto dura."""
    rec = _EST['recorte'] and motor.ESTADO == 'split'
    d = motor.ir_a('card', t)
    S('#nkit', t + 0.1, opacity=1)
    if rec: T('#nkbot', t, 0.25, 'power1.in', opacity=0)
    if _EST['sombra']: S('#nksh', t + 0.42, opacity=1)
    _EST['recorte'] = False
    _CAMBIOS.append((t, 'card'))
    return d

def tapar(x, y, w, h, hasta=0.1):
    """Tapa con el color de la tarjeta un rectángulo de la pantalla hasta el segundo `hasta`. Para la mancha que a veces
    trae el recorte en los primeros cuadros (el modelo tarda unos cuadros en 'agarrar' al presentador): mírala en la
    captura del segundo 0 y tápala, p. ej. N.tapar(162, 759, 190, 230)."""
    k = sum(1 for p in motor.parts if 'class="ntapa"' in p)
    motor.parts.append(f'<div class="ntapa" id="ntapa{k}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"></div>')
    S(f'#ntapa{k}', hasta, opacity=0)

def _poner(h, en=None):
    if en is None: motor.parts.append(h)
    elif isinstance(en, Papel): en.add(h)
    else: raise SystemExit('noche: en= tiene que ser None (zona de la tarjeta) o un panel creado con N.papel()')

def _bloque(idp, inner, t0, t1=None, en=None, dur_sale=0.16):
    _poner(f'<div class="nz" id="{idp}">{inner}</div>', en)
    win('#' + idp, t0)
    if t1 is not None: sale('#' + idp, t1, dur_sale)


# =====================================================================================================
#  PIEZAS
# =====================================================================================================
def gancho(frase, hasta, saltos=(), acento=(), antetitulo='', caja=None, idp='ngk'):
    """Titular del gancho: cada palabra salta en el instante en que se dice (la primera ya está en el cuadro 0).
    frase   : las primeras palabras del video TAL CUAL words.json (puedes escribirlas con tildes y signos)
    hasta   : segundo en que el titular se va (normalmente la primera palabra de la escena 2)
    saltos  : índices de palabra tras los que hay salto de línea, ej. (2, 5) · acento: índices en color de acento
    antetitulo : línea mono arriba (a máquina) · caja = (texto, segundo): caja roja con golpe debajo del titular.
    Tamaño automático (máx. 80 px). Para un gancho con cifra o batería, pon contador()/bateria() debajo."""
    _id(idp)
    ws = frase.split(); tiempos = []; t = 0.0
    for w in ws:
        tw_ = motor.f(w, t); tiempos.append(tw_); t = tw_ + 0.01
    lineas = []; cur = []
    for i in range(len(ws)):
        cur.append(i)
        if i in saltos: lineas.append(cur); cur = []
    if cur: lineas.append(cur)
    fs = min(_cabe(' '.join(ws[j] for j in L), 80, ZW, 56, -0.045, quien='gancho') for L in lineas)
    lh = round(fs * 1.08); y0 = 336 if antetitulo else 290
    h = f'<div class="ney" style="left:78px;top:276px">{typed(idp + "-e", antetitulo, 0.05, 44, 0)}</div>' if antetitulo else ''
    for k, L in enumerate(lineas):
        pal = ' '.join(f'<span class="nwd {"nac" if i in acento else ""}" id="{idp}-w{i}">{ws[i]}</span>' for i in L)
        h += f'<div class="nt80" style="left:78px;top:{y0 + k * lh}px;font-size:{fs}px">{pal}</div>'
    for i, t_ in enumerate(tiempos):
        if i == 0 and t_ < 0.25: continue                                      # la primera palabra ya está en el cuadro 0
        I(f'#{idp}-w{i}', opacity=0, y=26); T(f'#{idp}-w{i}', max(0, t_ - 0.03), 0.24, 'back.out(2)', opacity=1, y=0)
        if i in acento: fx(t_ - 0.03, 'pop', 0.16)
    ultimo = tiempos[-1]
    if caja:
        top = y0 + len(lineas) * lh + 26
        h += _caja_html(f'{idp}-c', caja[0], top)
        golpe(f'#{idp}-c', caja[1] - 0.03, s0=1.5, r0=-6, r1=-1.5, g=0.3, sh=7); ultimo = caja[1]
    _bloque(idp, h, 0, hasta)
    _aviso(idp, ultimo, hasta)
    _EST['gancho'] = hasta

def _caja_html(cid, texto, top, x=78, fs_max=140, ancho=ZW, alto_max=None):
    """caja roja con texto blanco (para golpes). Se achica sola para caber de ancho (y de alto si alto_max)."""
    fs = _cabe(texto, fs_max, ancho - 72, 48, -0.04, quien='caja')
    if alto_max: fs = max(40, min(fs, int((alto_max - 38) / 1.0)))
    return f'<div class="nbox" id="{cid}" style="left:{x}px;top:{top}px"><b style="font-size:{fs}px">{texto}</b></div>'

def titular(idp, t0, t1, lineas, antetitulo='', t_antetitulo=None, caja=None, x=78, y=None, tam=None, en=None):
    """Antetítulo (a máquina) + 1-3 líneas que SUBEN cuando se dicen + caja roja opcional con golpe.
    lineas = [(texto, segundo, color)] con color '' (crema) · 'ac' (acento) · 'g2' (gris).
    caja   = (texto, segundo): la palabra clave en caja roja (ej. ('DISTINTO.', f('distinto'))).
    x      = margen izquierdo (X_PASO = 390 si va junto a la pestaña de paso()). Tamaño automático 56-80 px."""
    _id(idp)
    ancho = ZX1 - x
    fs = tam or min(_cabe(l[0], 80, ancho, 56, -0.045, quien=idp) for l in lineas)
    lh = round(fs * 1.1); y0 = y if y is not None else (336 if antetitulo else 290)
    h = ''
    if antetitulo:
        t_a = t0 + 0.04 if t_antetitulo is None else t_antetitulo
        h += f'<div class="ney" style="left:{x}px;top:{y0 - 60}px">{typed(idp + "-e", antetitulo, t_a, 44, 0.03)}</div>'
    for i, l in enumerate(lineas):
        c = {'ac': 'nac', 'g2': 'ng2'}.get(l[2] if len(l) > 2 else '', '')
        h += f'<div class="nt80" style="left:{x}px;top:{y0 + i * lh}px;font-size:{fs}px">{linea(f"{idp}-l{i}", l[0], c)}</div>'
    ultimo = max(l[1] for l in lineas)
    if caja:
        top = y0 + len(lineas) * lh + 26
        h += _caja_html(f'{idp}-c', caja[0], top, x, 140, ancho, alto_max=ZY1 - top)
        ultimo = max(ultimo, caja[1])
    _bloque(idp, h, t0, t1, en)
    for i, l in enumerate(lineas): sube(f'#{idp}-l{i}', l[1] - 0.03, 'swipe' if i == 0 else 'pop', 0.15)
    if caja: golpe(f'#{idp}-c', caja[1] - 0.03, s0=2.2, r0=-9, r1=-2, g=0.34, sh=9); flash(caja[1] - 0.01, 0.16)
    _aviso(idp, ultimo, t1)

def slam(idp, t, texto, icono=None, t1=None, sub=(), t_encoge=None, acercar=None, destello=0.22, en=None):
    """SLAM: la palabra en una losa roja ENORME (con sombra dura crema) que cae de 2.3x + destello + sacudida + thump.
    sub       = [(texto, segundo)] líneas debajo de la losa (suben cuando se dicen)
    t_encoge  = segundo en que la losa se encoge a encabezado (arriba a la izquierda) para dejar sitio a la siguiente
                pieza (p. ej. nodos(..., y0=366)); las líneas sub salen ahí.
    acercar   = escala de un zoom del presentador en el golpe (ej. 1.07; vuelve a 1 al encoger o salir)."""
    _id(idp)
    ic = _svgico(icono, 150, PALETA['crema'], 2.0) if icono else ''
    fs = _cabe(texto, 172, 900 - 70 - (176 if icono else 0), 72, -0.055, quien=idp)
    h = f'<div class="nslab" id="{idp}-s">{ic}<b style="font-size:{fs}px">{texto}</b></div>'
    for i, s_ in enumerate(sub):
        fs2 = _cabe(s_[0], 72, ZW, 48, -0.04, quien=idp)
        h += f'<div class="nt80" style="left:90px;top:{526 + i * 96}px;font-size:{fs2}px">{linea(f"{idp}-u{i}", s_[0], "nac" if len(s_) > 2 and s_[2] == "ac" else "")}</div>'
    _bloque(idp, h, t - 0.02, None, en)
    I(f'#{idp}-s', opacity=0, scale=2.3); T(f'#{idp}-s', t, 0.3, 'expo.out', opacity=1, scale=1)
    FT(f'#{idp}-s', t + 0.1, 0.04, {'x': 0}, {'x': 9, 'yoyo': True, 'repeat': 5}, 'none')
    fx(t, 'thump', 0.44)
    if destello: flash(t + 0.02, destello)
    if acercar: zoom(t, acercar, 0.35, 'expo.out')
    for i, s_ in enumerate(sub): sube(f'#{idp}-u{i}', s_[1] - 0.03, 'pop', 0.16)
    if t_encoge is not None:
        for i in range(len(sub)): sale(f'#{idp}-u{i}', t_encoge - 0.02, 0.18, 30)
        S(f'#{idp}-s', t_encoge - 0.08, transformOrigin='0% 0%')
        T(f'#{idp}-s', t_encoge - 0.06, 0.42, 'power3.inOut', x=78 - 90, y=262 - 270, scale=0.42); fx(t_encoge - 0.06, 'swipe', 0.16)
        if acercar: zoom(t_encoge, 1.0, 0.8)
    if t1 is not None:
        T('#' + idp, t1 - 0.22, 0.22, 'power3.in', x=-1150, opacity=0); fx(t1 - 0.22, 'whoosh', 0.24)
        if acercar and t_encoge is None: zoom(t1, 1.0, 0.6)
    _aviso(idp, max([t] + [s_[1] for s_ in sub]), t_encoge if t_encoge is not None else t1)

def contador(idp, t0, t1, desde, hasta, t_ini, t_fin, prefijo='', sufijo='', t_sufijo=None, antetitulo='', t_antetitulo=None,
             pasos=8, barra=True, caja=None, rotulo=None, en=None):
    """Cifra GIGANTE (hasta 200 px) que cuenta de `desde` a `hasta` entre t_ini y t_fin (frena al final, con clics) +
    barra que se llena + golpe al llegar.  Ej.: contador('e2', t0, t1, 0, 5000, f('5 mil'), f('dólares'), prefijo='$', sufijo='/mes')
    sufijo  : texto pequeño junto a la cifra ('/mes', '%') que sube en t_sufijo (por defecto al terminar de contar)
    caja    = (texto, segundo): caja roja con golpe debajo ('HARÍA EXACTAMENTE ESTO ↓')  ·  rotulo = (texto, segundo): línea debajo
    Si cuenta hacia abajo hasta 0, el 0 queda en acento y la cifra se sacude. Números con punto de miles (5.000)."""
    _id(idp)
    vals = _serie(desde, hasta, pasos)
    txts = [prefijo + _miles(v) for v in vals]
    w_suf = _ancho(sufijo, 80, -0.045) + 20 if sufijo else 0
    fs = min(_cabe(tx, 200, ZW - w_suf - 16, 90, -0.055, quien=idp) for tx in txts)
    times = [t_ini] + [t_ini + (t_fin - t_ini) * k / (len(vals) - 1) for k in range(1, len(vals))] if len(vals) > 1 else [t_fin]
    cae_a_cero = hasta == 0 and desde > 0
    items = [(tx, times[k], 'nac' if (cae_a_cero and k == len(vals) - 1) else '') for k, tx in enumerate(txts)]
    h = ''
    if antetitulo:
        t_a = t0 + 0.02 if t_antetitulo is None else t_antetitulo
        h += f'<div class="ney" style="left:78px;top:276px">{typed(idp + "-e", antetitulo, t_a, 44, 0.03)}</div>'
    wfin = _ancho(txts[-1], fs, -0.055)
    h += f'<div class="nfig" id="{idp}-f" style="left:62px;top:330px;width:{int(wfin + 40)}px;height:{int(fs * 0.95)}px;font-size:{fs}px">{_seq(idp + "-v", items)}</div>'
    if sufijo:
        h += f'<div class="nt80" style="left:{int(62 + wfin + 18)}px;top:{int(330 + fs * 0.825 - 71)}px">{linea(idp + "-x", sufijo)}</div>'
    if barra: h += f'<div class="nbarra" style="left:78px;top:548px;width:924px"><i id="{idp}-b"></i></div>'
    ultimo = t_fin
    if caja:
        h += _caja_html(idp + '-c', caja[0], 614, fs_max=62)
        ultimo = max(ultimo, caja[1])
    elif rotulo:
        fs3 = _cabe(rotulo[0], 64, ZW, 44, -0.035, quien=idp)
        h += f'<div class="nt64" style="left:78px;top:{606 if barra else 560}px;font-size:{fs3}px">{linea(idp + "-r", rotulo[0])}</div>'
        ultimo = max(ultimo, rotulo[1])
    _bloque(idp, h, t0, t1, en)
    I(f'#{idp}-f', transformOrigin='0% 60%')
    for k in range(1, len(vals)):
        if k % 2 == 1 or k == len(vals) - 1: fx(times[k], 'click', 0.06)
    FT(f'#{idp}-f', t_fin + 0.02, 0.3, {'scale': 1.1}, {'scale': 1}, 'back.out(2.4)'); fx(t_fin + 0.02, 'thump', 0.3)
    if cae_a_cero: sacude(f'#{idp}-f', t_fin + 0.05, 10)
    if barra:
        I(f'#{idp}-b', scaleX=1 if desde > hasta else 0, transformOrigin='0% 50%')
        T(f'#{idp}-b', t_ini, max(0.2, t_fin - t_ini), 'power1.in' if desde <= hasta else 'power1.out', scaleX=0 if desde > hasta else 1)
    if sufijo:
        ts = t_fin + 0.12 if t_sufijo is None else t_sufijo
        sube(f'#{idp}-x', ts - 0.03, 'pop', 0.15); ultimo = max(ultimo, ts)
    if caja:
        golpe(f'#{idp}-c', caja[1] - 0.03, s0=1.5, r0=-6, r1=-1.5, g=0.28, sh=7)
    elif rotulo:
        sube(f'#{idp}-r', rotulo[1] - 0.03, 'pop', 0.14)
    _aviso(idp, ultimo, t1)

def _serie(a, b, n):
    out = []
    for k in range(n + 1):
        x = k / n; v = a + (b - a) * (1 - (1 - x) ** 2)                          # frena al final
        if k < n:
            d = abs(b - a); q = 100 if d >= 2000 else (10 if d >= 200 else 1)
            v = round(v / q) * q
        else: v = b
        out.append(v)
    res = [out[0]]
    for v in out[1:]:
        if v != res[-1]: res.append(v)
    return res

def _miles(v):
    return f'{int(round(v)):,}'.replace(',', '.')

def bateria(idp, t0, t1, t_llena, t_vacia, t_cero, etiqueta='', y=486, en=None):
    """Batería de 10 segmentos: se llena en t_llena (100 %), se vacía entre t_vacia y t_cero y queda en 0 % en acento
    con sacudida. Ocupa ~220 px de alto desde `y`: ponla DEBAJO de un titular o del gancho (que van en y 280-470).
    Ej.: 'perdiera todo lo que sé de IA' -> bateria('e1b', 0, t1, f('inteligencia'), f('tuviera'), f('cero'), 'INTELIGENCIA ARTIFICIAL')"""
    _id(idp)
    up = [t_llena + 0.08 + i * 0.03 for i in range(10)]
    dn = [t_vacia + (t_cero - t_vacia) * k / 10 for k in range(1, 11)]
    pct = _seq(idp + '-p', [(f'{10 * (i + 1)}%', up[i]) for i in range(10)] + [(f'{100 - 10 * k}%', dn[k - 1], 'nac' if k == 10 else '') for k in range(1, 11)])
    segs = ''.join(f'<i class="nsg"><b id="{idp}-g{i}"></b></i>' for i in range(10))
    lab = f'<div class="ney" style="left:0;top:0">{typed(idp + "-e", etiqueta, t_llena, 42, 0.03)}</div>' if etiqueta else ''
    h = (f'<div class="nbat" id="{idp}-b" style="left:78px;top:{y}px">{lab}<div class="nbcase">{segs}</div>'
         f'<i class="nbcr" id="{idp}-r"></i><i class="nbtip"></i><i class="nbtip nbtr" id="{idp}-t"></i><div class="nbpct">{pct}</div></div>')
    _bloque(idp, h, t0, t1, en)
    for i in range(10):
        I(f'#{idp}-g{i}', opacity=0); S(f'#{idp}-g{i}', up[i], opacity=1)
        if i % 3 == 0: fx(up[i], 'click', 0.06)
    for k in range(1, 11):
        S(f'#{idp}-g{10 - k}', dn[k - 1], opacity=0)
        if k % 2 == 0: fx(dn[k - 1], 'click', 0.07)
    I(f'#{idp}-r', opacity=0); S(f'#{idp}-r', t_cero, opacity=1); I(f'#{idp}-t', opacity=0); S(f'#{idp}-t', t_cero, opacity=1)
    sacude(f'#{idp}-b', t_cero, 11); fx(t_cero, 'thump', 0.32)
    _aviso(idp, t_cero, t1)

def paso(idp, n, total, t, t_sale, lineas=(), antetitulo='', caja=None, hasta=None, pausas=()):
    """Columna vertebral para guiones de PASOS: pestaña roja 'PASO n' (cifra 200 px + 'DE total' + barras) que entra con
    golpe en t, con su titular a la derecha (lineas, x 390-1002); en t_sale vuela a la esquina y queda la píldora
    '• PASO n / total' arriba a la derecha hasta `hasta` (None = hasta el siguiente paso() o el final del video).
    lineas = [(texto, segundo, color)] como en titular() · caja = (texto, segundo) caja roja bajo las líneas
    pausas = [(t_a, t_b)] tramos en que la píldora se esconde. Con la píldora visible deja libre x 760-1002 · y 262-322."""
    _id(idp)
    bars = ''.join(f'<i class="{"on" if k == n else ("dn" if k < n else "")}"></i>' for k in range(1, total + 1))
    motor.parts.append(f'<div class="ntab" id="{idp}"><i class="ngl"></i><b class="ntp">PASO</b><b class="ntn" id="{idp}-n">{n}</b>'
                       f'<b class="ntd">DE {total}</b><div class="ntb">{bars}</div></div>'
                       f'<div class="npil" id="{idp}-p"><i></i><span>PASO {n} / {total}</span></div>')
    I(f'#{idp}', opacity=0, scale=1.7, rotation=-8, transformOrigin='50% 50%')
    T(f'#{idp}', t, 0.34, 'expo.out', opacity=1, scale=1, rotation=0); fx(t, 'thump', 0.32); fx(t + 0.01, 'whoosh', 0.12)
    FT(f'#{idp}-n', t + 0.22, 0.26, {'scale': 1.22}, {'scale': 1}, 'back.out(2.6)')
    S(f'#{idp}', t_sale, transformOrigin='0% 0%')
    T(f'#{idp}', t_sale, 0.34, 'power3.inOut', x=650, y=-38, scale=0.16, opacity=0); fx(t_sale, 'swipe', 0.13)
    I(f'#{idp}-p', opacity=0, scale=0.4)
    T(f'#{idp}-p', t_sale + 0.12, 0.3, 'back.out(2.2)', opacity=1, scale=1); fx(t_sale + 0.12, 'pop', 0.14)
    for a, b in pausas:
        T(f'#{idp}-p', a - 0.16, 0.16, 'power2.in', opacity=0, scale=0.7); T(f'#{idp}-p', b, 0.3, 'back.out(2.2)', opacity=1, scale=1)
    if lineas: titular(idp + 'x', t, t_sale + 0.02, lineas, antetitulo, t + 0.3, caja=caja, x=X_PASO, y=362 if antetitulo else 330)
    _PASOS.append({'sel': f'#{idp}-p', 't': t, 'hasta': hasta, 'listo': t_sale + 0.43})

def _cerrar_pasos():
    ps = sorted(_PASOS, key=lambda p: p['t'])
    for i, p in enumerate(ps):
        fin = p['hasta'] if p['hasta'] is not None else (ps[i + 1]['t'] - 0.05 if i + 1 < len(ps) else None)
        if fin is not None and fin < motor.DUR:
            a = max(fin - 0.16, p['listo'])                     # nunca encima de su entrada
            T(p['sel'], a, max(0.08, fin - a), 'power2.in', opacity=0, scale=0.7)

class Riel:
    """Riel de progreso 01…N en la columna izquierda (x 16-150, junto a la tarjeta). Lo crea riel()."""
    def __init__(self, idp, total, t, iconos, t_fin):
        self.idp = idp; self.total = total; self.t = t; self.t_fin = t_fin
        self.y0 = motor.CARD_Y + 25; self.dy = min(86, (1630 - 72 - self.y0) / max(1, total - 1))
        it = ''
        for i in range(1, total + 1):
            ic = iconos[i - 1] if iconos and i - 1 < len(iconos) else None
            caras = ''
            for cls, col, cid in (('nrf', 'rgba(255,255,255,.45)', ''), ('nrd', PALETA['tinta_papel'], f'{idp}-d{i}'), ('nrc', '#fff', f'{idp}-c{i}')):
                svg = _svgico(ic, 40, col, 2.0) if ic else ''
                caras += f'<div class="{cls}"' + (f' id="{cid}"' if cid else '') + f'><b>{i:02d}</b>{svg}</div>'
            sin = '' if ic else ' nsin'
            it += f'<div class="nrt{sin}" id="{idp}-{i}" style="top:{round(self.y0 + self.dy * (i - 1))}px">{caras}</div>'
            I(f'#{idp}-d{i}', opacity=0); I(f'#{idp}-c{i}', opacity=0)
        motor.parts.append(f'<div class="nriel" id="{idp}">{it}</div>')
        for i in range(1, total + 1): entra(f'#{idp}-{i}', t + (i - 1) * 0.035, 0.32, 'back.out(2.4)', y=0, escala=0.3, snd=None)
        self.listo = {i: t + (i - 1) * 0.035 + 0.33 for i in range(1, total + 1)}     # fin de la entrada de cada casilla
        fx(t, 'swipe', 0.14)
        I('#' + idp, x=0)
        if t_fin is not None: sale('#' + idp, t_fin, 0.2)
        _RIELES.append(self)

    def casilla(self, i):
        """centro (x, y) de la casilla i (1…N) en pantalla."""
        return 83, round(self.y0 + self.dy * (i - 1) + 36)

    def actual(self, i, t):
        """la casilla i se pone en acento (la que se está contando)."""
        S(f'#{self.idp}-c{i}', t, opacity=1); FT(f'#{self.idp}-{i}', max(t, self.listo[i]), 0.4, {'scale': 1.22}, {'scale': 1}, 'back.out(2.5)')
        self.listo[i] = max(t, self.listo[i]) + 0.41

    def hecho(self, i, t, sonido=True):
        """la casilla i queda en papel (hecha)."""
        S(f'#{self.idp}-d{i}', t, opacity=1); S(f'#{self.idp}-c{i}', t, opacity=0)
        FT(f'#{self.idp}-{i}', max(t, self.listo[i]), 0.36, {'scale': 1.28}, {'scale': 1}, 'back.out(2.5)')
        self.listo[i] = max(t, self.listo[i]) + 0.37
        if sonido: fx(t, 'click', 0.12)

    def completo(self, t):
        """destello en cadena de todas las casillas (para el cierre: 'ya van las N')."""
        for i in range(1, self.total + 1):
            FT(f'#{self.idp}-c{i}', t + (i - 1) * 0.05, 0.45, {'opacity': 1}, {'opacity': 0}, 'power1.in')
        fx(t, 'swipe', 0.14); fx(t + 0.05 * self.total, 'ding', 0.22)

def riel(idp, total, t, iconos=None, t_fin=None):
    """Riel de progreso 01→N a la izquierda de la tarjeta (solo se ve en card: en split se esconde solo).
    iconos = lista de nombres de ICONOS (uno por casilla, opcional). Úsalo con tarjeta_numerada(..., riel=R):
    cada tarjeta vuela a su casilla al terminar. R.actual(i, t) · R.hecho(i, t) · R.completo(t)."""
    _id(idp)
    return Riel(idp, total, t, iconos, t_fin)

def _aplicar_rieles():
    for r in _RIELES:
        for t, k in sorted(_CAMBIOS):
            if t < r.t or (r.t_fin is not None and t >= r.t_fin): continue
            if k == 'split': T('#' + r.idp, t, 0.2, 'power2.in', opacity=0, x=-50)
            else: T('#' + r.idp, t + 0.32, 0.3, 'power2.out', opacity=1, x=0)


# --------- chat estilo WhatsApp (núcleo de whatsapp() y de tarjeta_numerada(chat=…)) ---------
def _lineas(texto, maxpx, fs=40):
    """parte un texto de chat en renglones de <= maxpx (Inter a fs px); si trae <br> respeta tus cortes."""
    if '<br>' in texto or '\n' in texto: return [x.strip() for x in re.split(r'<br\s*/?>|\n', texto)]
    out = []; cur = ''
    for w in texto.split(' '):
        prueba = (cur + ' ' + w).strip()
        if cur and _ancho(prueba, fs, 0, 'int') > maxpx: out.append(cur); cur = w
        else: cur = prueba
    if cur: out.append(cur)
    return out

def _msg(m):
    if isinstance(m, dict): return dict(m)
    d = {'lado': m[0], 'texto': m[1], 't': m[2]}
    if len(m) > 3: d['escribe'] = m[3]
    return d

class _Chat:
    def __init__(self, pid, ancho, alto_cuerpo, tam=40):
        self.pid = pid; self.w = ancho; self.hb = alto_cuerpo; self.lh = 46; self.pad = 26; self.gap = 12
        self.maxpx = ancho - 44 - 48 - 10                         # márgenes y relleno de la burbuja
        self.items = []; self.encima = []; self.y = 14; self.scroll = 0; self.t_scroll = -9; self.k = 0; self.ultimo = 0

    def _scroll_a(self, fondo, t):
        need = max(0, fondo + 14 - self.hb)
        if need > self.scroll + 0.5:
            t = max(t, self.t_scroll + 0.005)                     # nunca encima del scroll anterior
            T(f'#{self.pid}-sc', t, 0.26, 'power2.out', y=-need); self.scroll = need; self.t_scroll = t + 0.26

    def escribiendo(self, t0, t1, out=False):
        k = self.k; self.k += 1; tid = f'{self.pid}-y{k}'
        self.items.append(f'<div class="nwt{" out" if out else ""}" id="{tid}" style="top:{self.y}px"><i id="{tid}a"></i><i id="{tid}b"></i><i id="{tid}c"></i></div>')
        self._scroll_a(self.y + 66, t0)
        I('#' + tid, opacity=0, scale=0.6, transformOrigin='100% 0%' if out else '0% 0%')
        T('#' + tid, t0, 0.2, 'back.out(2)', opacity=1, scale=1); S('#' + tid, t1 - 0.01, opacity=0)
        reps = max(1, int(round((t1 - t0 - 0.1) / 0.36)))
        for j, s_ in enumerate('abc'):
            FT(f'#{tid}{s_}', t0 + 0.04 + j * 0.09, 0.18, {'y': 0}, {'y': -10, 'yoyo': True, 'repeat': reps * 2 - 1}, 'sine.inOut')
        fx(t0 + 0.02, 'click', 0.07)

    def mensaje(self, lado, texto, t, escribe=None, bot=False, rayo=None, check=None):
        out = lado in ('out', 'der', 'derecha', 'yo')
        if escribe is not None and escribe < t - 0.15: self.escribiendo(escribe, t, out)
        libre = self.maxpx - (46 if bot else 0) - (50 if (out if check is None else check) else 0) - (60 if rayo is not None else 0)
        ls = _lineas(texto, libre)
        k = self.k; self.k += 1; bid = f'{self.pid}-m{k}'
        h = self.pad + self.lh * len(ls)
        pre = _svgico('bot', 36, acento(), 2.2, 'nwbot') if bot else ''
        tick = TICKS if (out if check is None else check) else ''
        blt = f'<span class="nbolt" id="{bid}z">{_svgico("rayo", 28, "#fff")}</span>' if rayo is not None else ''
        self.items.append(f'<div class="nwm{" out" if out else ""}" id="{bid}" style="top:{self.y}px">{pre}<span>{"<br>".join(ls)}</span>{tick}{blt}</div>')
        self._scroll_a(self.y + h, t)
        I('#' + bid, opacity=0, scale=0.6, transformOrigin='100% 0%' if out else '0% 0%')
        T('#' + bid, t, 0.3, 'back.out(1.8)', opacity=1, scale=1); fx(t, 'pop', 0.12 if out else 0.17)
        if rayo is not None:
            I(f'#{bid}z', scale=0, rotation=-40); T(f'#{bid}z', rayo, 0.36, 'back.out(3)', scale=1, rotation=0); fx(rayo, 'click', 0.13)
        self.y += h + self.gap; self.ultimo = max(self.ultimo, t, rayo or 0)
        if max(_ancho(x, 40, 0, 'int') for x in ls) > libre + 8:
            print(f'  (aviso) chat {self.pid}: "{_plano(max(ls, key=len))}" es larga para la burbuja; pártela con <br> o acórtala.')
        return bid

    def html(self, cabecera):
        return (f'{cabecera}<div class="nwb" style="height:{self.hb}px"><div class="nws" id="{self.pid}-sc">{"".join(self.items)}</div>'
                f'{"".join(self.encima)}</div>')

def whatsapp(idp, t0, t1, mensajes, nombre='Cliente', insignia='AGENTE IA', inicial=None, icono_contacto=None,
             fichas=(), alto=None, en=None):
    """Chat de WhatsApp que se escribe solo: cada burbuja (texto 40 px) salta en su segundo, con 'escribiendo…' antes si
    lo pides, y la conversación hace scroll sola cuando se llena. Llena la zona (924 px de ancho).
    mensajes = [(lado, texto, segundo)] o [(lado, texto, segundo, segundo_escribiendo)] o dicts con
               lado ('in' = recibido, a la izquierda · 'out' = enviado, a la derecha, con doble check), texto, t,
               escribe (segundo en que aparece 'escribiendo…'), bot=True (robot en acento delante),
               rayo=segundo (rayo rojo = 'mensaje automático').  Los textos largos se parten solos (o usa <br>).
    insignia = píldora en acento en la cabecera ('' = sin píldora) · fichas = [(texto, segundo)] etiquetas que se pegan
    debajo del chat (encima del borde de la tarjeta, ej. ('Yo ☕', t), ('en otra cosa', t))."""
    _id(idp)
    alto = alto or (420 if fichas else 478); hh = 94
    ch = _Chat(idp + '-c', ZW, alto - hh)
    for m in mensajes: ch.mensaje(**_msg(m))
    av = _svgico(icono_contacto, 40, '#075E54', 2.2) if icono_contacto else f'<span>{inicial or _plano(nombre)[:1].upper()}</span>'
    ins = f'<span class="nwag"><i id="{idp}-pd"></i><span>{insignia}</span></span>' if insignia else ''
    cab = f'<div class="nwh" style="height:{hh}px"><div class="nwav">{av}</div><b>{nombre}</b>{ins}</div>'
    h = f'<div class="nwa" id="{idp}-w" style="left:78px;top:262px;width:{ZW}px;height:{alto}px">{ch.html(cab)}</div>'
    x = 78; ultimo = ch.ultimo
    for i, fi in enumerate(fichas):
        fs = 56 if i == 0 else 50
        h += f'<div class="nchip{" n2" if i % 2 else ""}" id="{idp}-f{i}" style="left:{x}px;top:{262 + alto + 16}px;font-size:{fs}px"><span>{fi[0]}</span></div>'
        x += int(_ancho(fi[0], fs, -0.03) + 56 + 24)
        ultimo = max(ultimo, fi[1])
    if x > 1010: print(f'  (aviso) {idp}: las fichas no caben en una fila; acórtalas.')
    _bloque(idp, h, t0 - 0.02, None, en)
    entra(f'#{idp}-w', t0, 0.42, 'back.out(1.6)', y=50, escala=0.84, snd='pop', g=0.24)
    if insignia: FT(f'#{idp}-pd', t0 + 0.6, 0.45, {'opacity': 1}, {'opacity': 0.2, 'yoyo': True, 'repeat': 6}, 'sine.inOut')
    for i, fi in enumerate(fichas):
        entra(f'#{idp}-f{i}', fi[1] - 0.03, 0.32, 'back.out(2.4)', y=20, escala=0.4, rot=(-16 if i % 2 == 0 else 14, -4 if i % 2 == 0 else 3), g=0.22)
    if t1 is not None:
        T('#' + idp, t1 - 0.22, 0.22, 'power3.in', x=-1150, opacity=0); fx(t1 - 0.22, 'whoosh', 0.24)
    _aviso(idp, ultimo, t1)

def tarjeta_numerada(idp, n, total, t0, t1, titulo, t_titulo, antetitulo='', t_antetitulo=None, icono=None, t_icono=None,
                     sub='', t_sub=None, chat=None, t_chat=None, nombre_chat='WhatsApp', icono_chat=None,
                     ficha=None, sello=None, riel=None):
    """Tarjeta de papel numerada (para listas tipo 'N cosas'): número GIGANTE (200 px) + icono en círculo (170 px) +
    'n/total' con segmentos (el actual se llena mientras dura) + antetítulo + título (78 px) + subtítulo.
    chat   = mensajes como en whatsapp(): en t_chat la tarjeta se reacomoda (número y título arriba, más chicos) y
             sube un chat de WhatsApp dentro de ella.
    ficha  = (texto, segundo[, icono]) etiqueta roja con golpe arriba a la derecha (ej. '24 H ANTES')
    sello  = (texto, segundo) sello encima (ej. 'VENDIDO')
    riel   = un riel(): al terminar (t1) la tarjeta se encoge y VUELA a su casilla. t1 = cuando entra la siguiente."""
    _id(idp); c = '#' + idp
    segw = max(10, int((354 - 6 * (total - 1)) / total))
    segs = ''.join(f'<i class="dn" style="width:{segw}px"></i>' if j < n - 1 else
                   (f'<i style="width:{segw}px"><b id="{idp}-sf"></b></i>' if j == n - 1 else f'<i style="width:{segw}px"></i>') for j in range(total))
    ic = _svgico(icono, 96, '#fff', 1.9) if icono else _svgico('rayo', 96, '#fff')
    fs_t = _cabe(titulo, 78, 860, 56, -0.045, quien=idp)
    w_t = _ancho(titulo, fs_t, -0.045)
    esc_t = min(56 / fs_t, 450 / max(1, w_t))                      # en la fase 2 el título va a la derecha del número
    if chat and fs_t * esc_t < 40: print(f'  (aviso) {idp}: el título es largo; con el chat queda a {fs_t * esc_t:.0f} px. Acórtalo.')
    sub_h = (f'<div class="ncsub" id="{idp}-h">' + _svgico('chat', 46, '#6B675F', 2.2) + f'<span>{sub}</span></div>') if sub else ''
    chat_h = ''
    if chat:
        ch = _Chat(idp + '-c', 888, 236)
        for m in chat: ch.mensaje(**_msg(m))
        av = _svgico(icono_chat or icono or 'chat', 30, PALETA['tinta_papel'], 2.1)
        cab = f'<div class="nwh" style="height:64px"><div class="nwav">{av}</div><b>{nombre_chat}</b></div>'
        chat_h = f'<div class="nwa nemb" id="{idp}-w">' + ch.html(cab) + '</div>'
    extra = ''
    if ficha:
        fic = _svgico(ficha[2], 46, '#fff', 2.4) if len(ficha) > 2 and ficha[2] else ''
        extra += f'<div class="nchip nrd" id="{idp}-k" style="left:548px;top:132px;font-size:46px;height:74px">{fic}<span>{ficha[0]}</span></div>'
    if sello:
        extra += f'<div class="nsello" id="{idp}-z" style="left:300px;top:266px;font-size:84px">{sello[0]}</div>'
    motor.parts.append(f'''<div class="ncard" id="{idp}">
  <div class="ncn" id="{idp}-n"><span id="{idp}-ni">{n:02d}</span></div>
  <div class="ncl" id="{idp}-l"><div class="ncli" id="{idp}-li">{ic}</div></div>
  <div class="ncpg" id="{idp}-g">{n}/{total}</div>
  <div class="ncsg" id="{idp}-s">{segs}</div>
  <div class="nceb" id="{idp}-e"><span id="{idp}-ei">{antetitulo}</span></div>
  <div class="nctt" id="{idp}-t" style="font-size:{fs_t}px"><div class="ln"><span class="in" id="{idp}-ti">{titulo}</span></div></div>
  {sub_h}{chat_h}{extra}
</div>''')
    I(c, opacity=0, y=80, scale=0.93); T(c, t0, 0.55, 'expo.out', opacity=1, y=0, scale=1); fx(t0, 'whoosh', 0.2)
    I(f'#{idp}-ni', opacity=0, scale=1.9); T(f'#{idp}-ni', t0 + 0.02, 0.5, 'expo.out', opacity=1, scale=1); fx(t0 + 0.02, 'thump', 0.3)
    if antetitulo: barre(f'#{idp}-ei', (t0 + 0.2 if t_antetitulo is None else t_antetitulo) - 0.03)
    rise(f'#{idp}-ti', t_titulo - 0.03, 0.4); fx(t_titulo - 0.03, 'pop', 0.15)
    ti = (t_titulo + 0.15 if t_icono is None else t_icono) - 0.03
    I(f'#{idp}-li', opacity=0, scale=0.2); T(f'#{idp}-li', ti, 0.5, 'back.out(2.4)', opacity=1, scale=1); fx(ti, 'pop', 0.2)
    if sub:
        ts = (t_titulo + 0.25 if t_sub is None else t_sub) - 0.03
        I(f'#{idp}-h', opacity=0, x=-20); T(f'#{idp}-h', ts, 0.32, 'power3.out', opacity=1, x=0)
    I(f'#{idp}-sf', scaleX=0, transformOrigin='0% 50%'); T(f'#{idp}-sf', t0, max(0.3, t1 - t0), 'none', scaleX=1)
    ultimo = max(t_titulo, ti)
    if chat:
        tm = t_chat if t_chat is not None else t_titulo + 1.0
        E = 'power3.inOut'; D = 0.5
        T(f'#{idp}-n', tm, D, E, x=-4, y=4, scale=0.6)
        T(f'#{idp}-l', tm, D, E, x=-548, y=8, scale=0.4941)
        T(f'#{idp}-e', tm, D, E, x=256, y=-204, scale=0.952)
        T(f'#{idp}-t', tm, D, E, x=258, y=-208, scale=round(esc_t, 4))
        T(f'#{idp}-s', tm, D, E, x=-270, y=44, scale=0.7)
        T(f'#{idp}-g', tm, D, E, x=452, y=-4)
        if sub: T(f'#{idp}-h', max(tm, ts + 0.33), 0.18, 'power1.in', opacity=0)
        I(f'#{idp}-w', opacity=0, y=120); T(f'#{idp}-w', tm + 0.1, 0.6, 'expo.out', opacity=1, y=0); fx(tm, 'swipe', 0.16)
        ultimo = max(ultimo, ch.ultimo)
    if ficha:
        golpe(f'#{idp}-k', ficha[1] - 0.03, s0=2.0, r0=-16, r1=-6, dur=0.42, g=0.3, sh=0); ultimo = max(ultimo, ficha[1])
    if sello:
        golpe(f'#{idp}-z', sello[1] - 0.03, s0=2.3, r0=-21, r1=-9, dur=0.4, g=0.4, sh=0); fx(sello[1] + 0.03, 'ding', 0.26)
        ultimo = max(ultimo, sello[1])
    if riel is not None:
        riel.actual(n, t0)
        cx, cy = riel.casilla(n); ts = t1 - 0.3
        T(c, ts, 0.24, 'power2.in', x=cx - 540, scale=0.145)          # primero a la izquierda (nunca cruza la cara)…
        T(c, ts + 0.13, 0.24, 'power2.in', y=cy - 501)                 # …y luego baja a su casilla
        S(c, ts + 0.38, opacity=0); fx(ts, 'whoosh', 0.18)
        riel.hecho(n, ts + 0.36)
    else:
        T(c, t1 - 0.18, 0.18, 'power2.in', opacity=0, scale=0.9, y=-30)
    _aviso(idp, ultimo, t1 - (0.3 if riel is not None else 0))

def checklist(idp, t0, t1, items, titulo='', t_titulo=None, marca=None, en=None):
    """Lista de casillas dibujadas a mano: al entrar se dibujan todas vacías; cada ítem se escribe cuando se dice y se
    marca con ✓ en acento 0.2 s después. Hasta 5 ítems de ≤ 24 letras. Luce mejor en el papel (en=pp).
    titulo = línea manuscrita arriba · marca = (texto, segundo): palabra encerrada a mano al lado del título (ej. 'HOY')."""
    _id(idp)
    n = len(items)
    if not 1 <= n <= 5: raise SystemExit(f'noche.checklist {idp}: van de 1 a 5 ítems (tiene {n})')
    top0 = 344 if titulo else 284
    dy = min(96, (ZY1 - top0 - 70) / (n - 1)) if n > 1 else 0
    fs = min(_cabe(tx, 56 if n <= 4 else 52, ZW - 90, 40, -0.03, quien=idp) for tx, _ in items)
    h = ''
    if titulo:
        h += f'<div class="ncv" style="left:82px;top:262px;font-size:60px"><span id="{idp}-h">{titulo}</span></div>'
        if marca:
            xm = int(82 + _ancho(titulo, 60, 0, 'cav') + 40)
            wm = int(_ancho(marca[0], 76, -0.03) + 50)
            h += (f'<div class="nhoy" id="{idp}-m" style="left:{xm}px;top:256px">{marca[0]}'
                  f'{_svgp(idp + "-o", _elipse_d(wm / 2, 46, wm / 2 + 10, 46, 5), wm, 92, 6, "nsvac")}</div>')
            if xm + wm > 1010: print(f'  (aviso) {idp}: el título + la marca no caben; acorta el título.')
    for i, (tx, _) in enumerate(items):
        y = round(top0 + i * dy)
        h += (f'<div class="nchk" style="left:78px;top:{y}px;height:{min(96, max(74, dy))}px">'
              f'{_svgp(f"{idp}-b{i}", _rect_d(4, 4, 48, 48, 20 + i, 2.5), 56, 56, 4.5, "nbx nsvtx")}'
              f'{_svgp(f"{idp}-k{i}", "M10 30 L24 46 L54 6", 56, 56, 8, "nbx nsvac")}'
              f'<span class="nctx" id="{idp}-t{i}" style="font-size:{fs}px">{tx}</span>'
              f'<i class="nrule" id="{idp}-r{i}" style="top:{min(96, max(74, dy)) - 6}px"></i></div>')
    _bloque(idp, h, t0, t1, en)
    if titulo: escribe(f'#{idp}-h', (t0 + 0.2 if t_titulo is None else t_titulo) - 0.03, 0.62)
    for i in range(n):
        dibuja(f'#{idp}-b{i}', t0 + 0.35 + i * 0.07, 0.22)
        I(f'#{idp}-r{i}', scaleX=0, transformOrigin='0% 50%'); T(f'#{idp}-r{i}', t0 + 0.37 + i * 0.07, 0.34, 'power2.out', scaleX=1)
    fx(t0 + 0.35, 'swipe', 0.14)
    if marca:
        I(f'#{idp}-m', opacity=0, scale=0.5); T(f'#{idp}-m', marca[1] - 0.03, 0.26, 'back.out(2.6)', opacity=1, scale=1); fx(marca[1] - 0.03, 'pop', 0.18)
        dibuja(f'#{idp}-o', marca[1] + 0.08, 0.32, snd='swipe', g=0.12)
    for i, (tx, t_) in enumerate(items):
        escribe(f'#{idp}-t{i}', t_ - 0.04, 0.34, 0.1)
        dibuja(f'#{idp}-k{i}', t_ + 0.2, 0.16, 'power1.out'); fx(t_ + 0.2, 'pop', 0.15)
    _aviso(idp, max([t_ + 0.2 for _, t_ in items] + ([marca[1]] if marca else [])), t1)

def escalera(idp, t0, t1, pasos, t_tacha=None, ultimo_acento=True, titulo='', t_titulo=None, y0=None, en=None):
    """Escalera de 2-5 pasos numerados (número en círculo dibujado a mano, cada fila un poco más a la derecha) que
    aparecen cuando se dicen; el último en acento. t_tacha = segundo en que se TACHAN todos (el orden equivocado).
    pasos = [(texto, segundo)] o [(texto, segundo_numero, segundo_texto)].  titulo = línea manuscrita arriba.
    y0 = dónde empieza la primera fila (p. ej. 400 para dejar arriba el gancho de 1 línea). En la tinta o en el papel."""
    _id(idp)
    n = len(pasos)
    if not 2 <= n <= 5: raise SystemExit(f'noche.escalera {idp}: van de 2 a 5 pasos (tiene {n})')
    top0 = y0 if y0 is not None else (344 if titulo else 272)
    dy = min(122, (ZY1 - top0 - 84) / (n - 1)); dx = 76 if n <= 4 else 58
    h = f'<div class="ncv" style="left:82px;top:262px"><span id="{idp}-h">{titulo}</span></div>' if titulo else ''
    anchos = []
    for i, p in enumerate(pasos):
        x = 80 + i * dx; y = round(top0 + i * dy)
        fs = _cabe(p[0], 64, 1004 - (x + 102), 40, -0.035, quien=idp)
        w = _ancho(p[0], fs, -0.035) + 16; anchos.append(w)
        ult = 'nult' if (ultimo_acento and i == n - 1) else ''
        h += (f'<div class="nesc {ult}" style="left:{x}px;top:{y}px"><div class="nnc">{_svgp(f"{idp}-o{i}", _elipse_d(42, 42, 38, 36, 7 + i), 84, 84, 5)}'
              f'<b id="{idp}-d{i}">{i + 1}</b></div>'
              f'<span class="nrtx" id="{idp}-t{i}" style="font-size:{fs}px">{p[0]}'
              f'{_svgp(f"{idp}-k{i}", _linea_d(-8, fs * 0.62, w, fs * 0.47, 3 + i, 7), w, 60, max(8, round(fs * 0.17)), "nstrk nsvac")}</span></div>')
    _bloque(idp, h, t0, t1, en)
    if titulo: escribe(f'#{idp}-h', (t0 + 0.15 if t_titulo is None else t_titulo) - 0.03, 0.5)
    ultimo = 0
    for i, p in enumerate(pasos):
        tn = p[1]; tt = p[2] if len(p) > 2 else p[1] + 0.06
        dibuja(f'#{idp}-o{i}', tn - 0.03, 0.3)
        I(f'#{idp}-d{i}', opacity=0, scale=0.5); T(f'#{idp}-d{i}', tn, 0.26, 'back.out(2.4)', opacity=1, scale=1); fx(tn, 'pop', 0.14)
        escribe(f'#{idp}-t{i}', tt - 0.04, 0.34); ultimo = max(ultimo, tt)
        I(f'#{idp}-k{i}', opacity=0)
    if t_tacha is not None:
        for i in range(n): dibuja(f'#{idp}-k{i}', t_tacha - 0.02 + i * 0.1, 0.16, 'power1.out')
        fx(t_tacha - 0.02, 'thump', 0.26); fx(t_tacha + 0.2, 'swipe', 0.14); ultimo = max(ultimo, t_tacha + 0.1 * n)
    _aviso(idp, ultimo, t1)

def lista_tachada(idp, t0, t1, items, titulo='', t_titulo=None, en=None):
    """'Olvídate de…': tarjetas con icono que entran cuando se nombran y se TACHAN (raya en acento + ✗) cuando toca.
    items = [(texto, segundo_entra, segundo_tacha)] o con icono: (texto, t_entra, t_tacha, 'mundo'); t_tacha=None = la
    que se salva (queda rellena en acento + ding: sirve para 'deja X, usa Y'). 4 ítems = cuadrícula 2x2; 1-3 = filas.
    Textos de 1-2 líneas (<br>) de ≤ 14 letras por línea."""
    _id(idp)
    n = len(items)
    if not 1 <= n <= 4: raise SystemExit(f'noche.lista_tachada {idp}: van de 1 a 4 ítems (tiene {n})')
    top = 350 if titulo else 284
    h = ''
    if titulo:
        fst = _cabe(titulo, 64, ZW, 48, -0.035, quien=idp)
        h += f'<div class="nt64" style="left:78px;top:268px;font-size:{fst}px">{linea(idp + "-h", titulo)}</div>'
    rej = n == 4
    for i, it in enumerate(items):
        tx, te, tt = it[0], it[1], it[2]; ic = it[3] if len(it) > 3 else None
        if rej: x = 78 + (i % 2) * 472; y = top + (i // 2) * 200; w = 452; hh = 188
        else:
            hh = min(150, int((ZY1 - top - (n - 1) * 16) / n)); x = 78; y = top + i * (hh + 16); w = ZW
        lns = re.split(r'<br\s*/?>', tx)
        lx = 150 if ic else 34
        fs = min(_cabe(l, 52 if rej else 66, w - lx - (90 if not rej else 24), 40, -0.03, quien=idp) for l in lns)
        lh = round(fs * 1.02); ty = round((hh - lh * len(lns)) / 2)
        stk = '' if tt is None else ''.join(f'<i class="nlts" id="{idp}-k{i}{j}" style="top:{round(lh * (j + 0.52))}px"></i>' for j in range(len(lns)))
        ti = 96 if rej else 84
        ico = (f'<div class="nlti" style="left:28px;top:{round((hh - ti) / 2)}px">' + _svgico(ic, ti, 'currentColor', 2.0) + '</div>') if ic else ''
        xb = (92, hh - 76) if (rej and ic) else (w - 86, round((hh - 56) / 2))
        xx = (f'<div class="nltx" id="{idp}-x{i}" style="left:{xb[0]}px;top:{xb[1]}px">' + _equis(f'{idp}-xx{i}', 30, 30, 7, 3, color='#fff') + '</div>') if tt is not None else ''
        salva = ' nsalva' if tt is None else ''
        h += (f'<div class="nltc{salva}" id="{idp}-c{i}" style="left:{x}px;top:{y}px;width:{w}px;height:{hh}px">{ico}'
              f'<b class="nltl" style="left:{lx}px;top:{ty}px;font-size:{fs}px;line-height:{lh}px">{tx}{stk}</b>{xx}</div>')
    _bloque(idp, h, t0, t1, en)
    if titulo: sube(f'#{idp}-h', (t0 + 0.05 if t_titulo is None else t_titulo) - 0.03, 'swipe', 0.15)
    ultimo = 0
    for i, it in enumerate(items):
        tx, te, tt = it[0], it[1], it[2]; nl = len(re.split(r'<br\s*/?>', tx))
        entra(f'#{idp}-c{i}', te - 0.03, 0.34, 'back.out(1.6)', y=50, escala=0.85, snd='pop', g=0.16); ultimo = max(ultimo, te)
        if tt is None:
            FT(f'#{idp}-c{i}', te + 0.34, 0.3, {'scale': 1.06}, {'scale': 1}, 'back.out(2.4)'); fx(te + 0.34, 'ding', 0.2); continue
        for j in range(nl):
            I(f'#{idp}-k{i}{j}', scaleX=0); T(f'#{idp}-k{i}{j}', tt + j * 0.09, 0.18, 'power2.out', scaleX=1)
        fx(tt, 'swipe', 0.16)
        I(f'#{idp}-x{i}', opacity=0, scale=0.3); T(f'#{idp}-x{i}', tt + 0.12, 0.28, 'back.out(3)', opacity=1, scale=1); fx(tt + 0.12, 'thump', 0.2)
        _dibuja_equis(f'{idp}-xx{i}', tt + 0.16, 0, 0.07)
        if len(it) > 3 and it[3]: T(f'#{idp}-c{i} .nlti', tt + 0.2, 0.2, 'power1.out', opacity=0.3)
        ultimo = max(ultimo, tt + 0.3)
    _aviso(idp, ultimo, t1)

def nodos(idp, t0, t1, nodos, bucle=None, notas=(), titulo=None, y0=None, final_ok=True, en=None):
    """Cadena de 2-6 nodos (un proceso, un agente, un embudo): al entrar se ven apagados; cada uno se ENCIENDE cuando se
    dice (con estallido y flecha) y el último queda en acento (final_ok). Con 4-6 nodos van en 2 filas en zigzag.
    nodos  = [(etiqueta, icono, segundo)]  (etiqueta ≤ 9 letras si son 3 por fila; ≤ 14 si son 2)
    bucle  = segundo en que una línea en acento vuelve del último al primero + icono que gira ('hasta lograrlo')
    notas  = [(texto, segundo_entra, segundo_sale)] línea corta entre las filas (o debajo) — una a la vez
    titulo = (texto, segundo) encabezado de 64 px arriba; si va debajo de un slam encogido usa y0=366 sin titulo."""
    _id(idp)
    nn = len(nodos)
    if not 2 <= nn <= 6: raise SystemExit(f'noche.nodos {idp}: van de 2 a 6 nodos (tiene {nn})')
    filas = [list(range(nn))] if nn <= 3 else [list(range(math.ceil(nn / 2))), list(range(math.ceil(nn / 2), nn))]
    HN, GY, GX = 150, 70, 60
    alto = HN * len(filas) + GY * (len(filas) - 1)
    if y0 is None: y0 = 366 if titulo else int(ZY0 + (ZH - alto - (90 if len(filas) == 1 and (notas or bucle) else 0)) / 2)
    pos = {}
    for r, fila in enumerate(filas):
        m = len(fila); w = (ZW - GX * (m - 1)) / m
        for j, i in enumerate(fila):
            jj = j if r == 0 else m - 1 - j                               # la 2ª fila corre de derecha a izquierda
            pos[i] = (round(78 + jj * (w + GX)), y0 + r * (HN + GY), round(w))
    CV = {'d': '<path d="M8.5 4l8 8-8 8"/>', 'b': '<path d="M4 8.5l8 8 8-8"/>', 'i': '<path d="M15.5 4l-8 8 8 8"/>'}
    h = ''
    if titulo: h += f'<div class="nt64" style="left:78px;top:266px">{linea(idp + "-h", titulo[0])}</div>'
    if bucle is not None:
        if len(filas) == 2:
            ya = y0 + HN / 2; yb = y0 + HN + GY + HN / 2; xl = pos[nn - 1][0]
            d = f'M{xl} {yb:.0f} H50 Q36 {yb:.0f} 36 {yb - 14:.0f} V{ya + 14:.0f} Q36 {ya:.0f} 50 {ya:.0f} H{pos[0][0] - 10}'
            cab = f'M{pos[0][0] - 21} {ya - 13:.0f} L{pos[0][0] - 6} {ya:.0f} L{pos[0][0] - 21} {ya + 13:.0f}'
            li = (2, round((ya + yb) / 2 - 34))
        else:
            yb = y0 + HN; xa = pos[0][0] + pos[0][2] / 2; xz = pos[nn - 1][0] + pos[nn - 1][2] / 2
            d = f'M{xz:.0f} {yb + 6} V{yb + 40} Q{xz:.0f} {yb + 54} {xz - 14:.0f} {yb + 54} H{xa + 14:.0f} Q{xa:.0f} {yb + 54} {xa:.0f} {yb + 40} V{yb + 16}'
            cab = f'M{xa - 13:.0f} {yb + 29} L{xa:.0f} {yb + 14} L{xa + 13:.0f} {yb + 29}'
            li = (round((xa + xz) / 2 - 34), yb + 20)
        h += (f'<svg class="nloop" viewBox="0 0 1080 860"><path id="{idp}-lp" pathLength="100" d="{d}"/><path id="{idp}-lh" d="{cab}"/></svg>'
              f'<div class="nlpi" id="{idp}-li" style="left:{li[0]}px;top:{li[1]}px">{_svgico("bucle", 42, PALETA["crema"], 2.8, idp=idp + "-ls")}</div>')
    for i, (lab, icn, _) in enumerate(nodos):
        x, y, w = pos[i]; ok = final_ok and i == nn - 1
        fs = _cabe(lab, 52, w - 36, 40, -0.035, quien=idp)
        h += (f'<div class="nnd" id="{idp}-n{i}" style="left:{x}px;top:{y}px;width:{w}px">'
              f'<div class="nndm">{_svgico(icn, 66, "currentColor", 2.0)}</div><div class="nndn">{i + 1}</div>'
              f'<div class="nndl{" nok" if ok else ""}" id="{idp}-l{i}">{_svgico(icn, 58, "currentColor", 2.4)}<span style="font-size:{fs}px">{lab}</span>'
              f'<div class="nndn">{i + 1}</div></div><div class="nndb" id="{idp}-b{i}"></div></div>')
    chev = []
    for i in range(nn - 1):
        (x1, y1, w1), (x2, y2, w2) = pos[i], pos[i + 1]
        if y1 == y2 and x2 > x1: k = 'd'; cx = x1 + w1 + 8; cy = y1 + HN / 2 - 22
        elif y1 == y2: k = 'i'; cx = x2 + w2 + 8; cy = y1 + HN / 2 - 22
        else: k = 'b'; cx = (max(x1, x2) + min(x1 + w1, x2 + w2)) / 2 - 22; cy = y1 + HN + GY / 2 - 22
        h += f'<svg class="nchv" id="{idp}-c{i}" style="left:{cx:.0f}px;top:{cy:.0f}px" viewBox="0 0 24 24">{CV[k]}</svg>'
        chev.append(f'#{idp}-c{i}')
    ny = (y0 + HN + (GY - 52) / 2) if len(filas) == 2 else (y0 + HN + (96 if bucle is not None else 26))
    for k, nt in enumerate(notas):
        h += f'<div class="nndt" id="{idp}-t{k}" style="left:{120 if len(filas) == 2 else 78}px;top:{ny:.0f}px"><span>{nt[0]}</span></div>'
    _bloque(idp, h, t0, t1, en)
    if titulo: sube(f'#{idp}-h', titulo[1] - 0.03, 'swipe', 0.15)
    for i in range(nn): entra(f'#{idp}-n{i}', t0 + 0.3 + i * 0.06, 0.3, 'back.out(1.7)', y=16, escala=0.72, snd=None)
    fx(t0 + 0.3, 'pop', 0.14)
    for c_ in chev: I(c_, opacity=0); T(c_, t0 + 0.55, 0.2, 'power1.out', opacity=0.28)
    ultimo = 0
    for i, (lab, icn, t_) in enumerate(nodos):
        ok = final_ok and i == nn - 1
        if i > 0:
            T(chev[i - 1], t_ - 0.2, 0.16, 'power2.out', opacity=1)
            FT(chev[i - 1], t_ - 0.18, 0.12, {'scale': 1}, {'scale': 1.35, 'yoyo': True, 'repeat': 1}, 'power2.out')
        I(f'#{idp}-l{i}', opacity=0, scale=1.2); T(f'#{idp}-l{i}', t_ - 0.03, 0.32, 'back.out(2.2)', opacity=1, scale=1)
        I(f'#{idp}-b{i}', opacity=0); FT(f'#{idp}-b{i}', t_ - 0.03, 0.5, {'opacity': 0.95, 'scale': 1}, {'opacity': 0, 'scale': 1.28}, 'power2.out')
        fx(t_ - 0.03, 'thump' if ok else 'pop', 0.32 if ok else 0.22)
        if ok: fx(t_, 'ding', 0.28)
        ultimo = max(ultimo, t_)
    if bucle is not None:
        I(f'#{idp}-lp', strokeDasharray=100, strokeDashoffset=100); I(f'#{idp}-lh', opacity=0)
        T(f'#{idp}-lp', bucle - 0.03, 0.45, 'power2.inOut', strokeDashoffset=0); S(f'#{idp}-lh', bucle + 0.4, opacity=1); fx(bucle - 0.03, 'swipe', 0.22)
        entra(f'#{idp}-li', bucle + 0.02, 0.3, 'back.out(2.4)', y=0, escala=0.3, snd=None)
        I(f'#{idp}-ls', transformOrigin='50% 50%')
        FT(f'#{idp}-ls', bucle + 0.2, 0.9, {'rotation': 0}, {'rotation': 360, 'repeat': 2}, 'none')
        for i in range(nn):
            FT(f'#{idp}-n{i}', bucle + 0.12 + i * 0.08, 0.24, {'scale': 1.07}, {'scale': 1}, 'power2.out')
        ultimo = max(ultimo, bucle + 0.4)
    for k, nt in enumerate(notas):
        entra(f'#{idp}-t{k}', nt[1] - 0.03, 0.3, 'back.out(2)', y=18, escala=0.6, snd='pop', g=0.16, origen='0% 50%')
        if len(nt) > 2 and nt[2] is not None: sale(f'#{idp}-t{k}', nt[2], 0.14, -26)
        ultimo = max(ultimo, nt[1])
    if len(filas) == 1 and notas and any(len(nt) < 3 or nt[2] is None for nt in notas[:-1]):
        print(f'  (aviso) {idp}: las notas se ponen una encima de otra: dales segundo de salida.')
    _aviso(idp, ultimo, t1)

def comparar(idp, t0, t1, malo, bueno, titulo=None, vs=False, escribir=False, en=None):
    """Dos tarjetas apiladas: la de ARRIBA es lo que NO (se tacha con raya + ✗) y la de ABAJO, en acento, lo que SÍ (✓).
    malo  = (etiqueta, texto, segundo_entra, segundo_tacha)   ej. ('NO NECESITAS', 'Saberlo todo', f('No'), f('todo'))
    bueno = (etiqueta, texto, segundo_entra, segundo_ok) o con línea extra (…, sub, segundo_sub)
    titulo = (texto, segundo) encabezado arriba · vs = sello 'VS' entre las dos · escribir = los textos se escriben a
    máquina (para frases dichas, ej. '¿Cómo hago esto?'). Textos de ≤ 22 letras (el sub ≤ 34)."""
    _id(idp)
    e1, x1, ta, tx = malo[:4]
    e2, x2, tb, tk = bueno[:4]; sb = bueno[4] if len(bueno) > 4 else ''; tsb = bueno[5] if len(bueno) > 5 else tk
    if titulo: y1, h1, y2, h2 = 346, 168, 532, 200            # termina en y 732 (sobre el papel, antes del borde rasgado)
    else: y1, h1, y2, h2 = 300, 190, 514, 216
    f1 = _cabe(x1, 80, 720, 44, -0.045, quien=idp); f2 = _cabe(x2, 72 if sb else 80, 720, 44, -0.045, quien=idp)
    if sb: f2 = min(f2, h2 - 64 - 60)
    w1 = _ancho(x1, f1, -0.045)
    ty1 = round(62 + max(0, (h1 - 62 - f1) / 2)); ty2 = 64 if sb else round(62 + max(0, (h2 - 62 - f2) / 2))
    def txt(pid, s, t_):
        return typed(pid, s, t_ - 0.03, 24, 0.07) if escribir else linea(pid, s)
    h = ''
    if titulo:
        h += f'<div class="nt64" style="left:78px;top:264px">{linea(idp + "-h", titulo[0])}</div>'
    h += (f'<div class="ncmp nmal" id="{idp}-a" style="left:78px;top:{y1}px;height:{h1}px">'
          f'<div class="ney" style="left:34px;top:20px">{typed(idp + "-ea", e1, ta + 0.05, 34, 0.03)}</div>'
          f'<div class="ncmt" style="left:32px;top:{ty1}px;font-size:{f1}px">{txt(idp + "-ta", x1, ta)}</div>'
          f'<i class="nsbar" id="{idp}-s" style="left:22px;top:{round(ty1 + f1 * 0.5)}px;width:{round(min(720, w1) + 20)}px"></i>'
          f'<div class="nko" id="{idp}-x" style="left:780px;top:{round((h1 - 110) / 2)}px">{_equis(idp + "-xx", 54, 54, 9, 4, "nsvac")}</div></div>')
    sub_h = f'<div class="ncms" style="left:34px;top:{round(ty2 + f2 * 1.04 + 8)}px">{txt(idp + "-u", sb, tsb)}</div>' if sb else ''
    h += (f'<div class="ncmp nbien" id="{idp}-b" style="left:78px;top:{y2}px;height:{h2}px">'
          f'<div class="ney" style="left:34px;top:20px">{typed(idp + "-eb", e2, tb + 0.05, 30, 0.03)}</div>'
          f'<div class="ncmt" style="left:32px;top:{ty2}px;font-size:{f2}px">{txt(idp + "-tb", x2, tb)}</div>{sub_h}'
          f'<div class="nokc" id="{idp}-v" style="left:780px;top:{round((h2 - 110) / 2)}px">{_svgp(idp + "-vv", CHECK_D, 64, 56, 10, "nsvok")}</div></div>')
    if vs: h += f'<div class="nvs" id="{idp}-vs" style="left:906px;top:{round((y1 + h1 + y2) / 2 - 48)}px">VS</div>'
    _bloque(idp, h, t0, t1, en)
    if titulo: sube(f'#{idp}-h', titulo[1] - 0.03, 'swipe', 0.15)
    entra(f'#{idp}-a', ta - 0.03, 0.4, 'expo.out', y=60, snd='whoosh', g=0.14)
    if not escribir: sube(f'#{idp}-ta', ta + 0.12, 'pop', 0.14)
    I(f'#{idp}-s', scaleX=0, transformOrigin='0% 50%'); T(f'#{idp}-s', tx - 0.02, 0.2, 'power2.out', scaleX=1); fx(tx - 0.02, 'swipe', 0.16)
    entra(f'#{idp}-x', tx + 0.1, 0.3, 'back.out(2.4)', y=0, escala=0.4, snd='thump', g=0.24); _dibuja_equis(idp + '-xx', tx + 0.16, 0, 0.08)
    T(f'#{idp}-a', tx + 0.25, 0.3, 'power1.out', opacity=0.62)
    entra(f'#{idp}-b', tb - 0.03, 0.42, 'back.out(1.5)', y=70, snd='whoosh', g=0.16)
    if not escribir:
        sube(f'#{idp}-tb', tb + 0.12, 'pop', 0.16)
        if sb: sube(f'#{idp}-u', tsb - 0.03, 'pop', 0.14)
    entra(f'#{idp}-v', tk - 0.03, 0.3, 'back.out(2.4)', y=0, escala=0.4, snd='ding', g=0.24); dibuja(f'#{idp}-vv', tk + 0.04, 0.18)
    FT(f'#{idp}-b', tk + 0.05, 0.3, {'scale': 1.03}, {'scale': 1}, 'power2.out')
    if vs:
        entra(f'#{idp}-vs', tb + 0.2, 0.3, 'back.out(2.6)', y=0, escala=0.3, rot=(-25, 0), snd='pop', g=0.16)
        T(f'#{idp}-vs', tk - 0.03, 0.16, 'power2.in', opacity=0, scale=0.4)
    _aviso(idp, max(tx, tk, tsb), t1)

def sello(idp, texto, t, x=None, y=430, rot=-6, tam=100, giro=False, t1=None, en=None):
    """Sello de goma con golpe: texto en acento con borde grueso que cae girando + thump + ding + sacudida.
    x=None = centrado. giro=True = entra dando media vuelta (para 'AL REVÉS', 'NO'). Sobre papel o sobre la tinta."""
    _id(idp)
    fs = _cabe(texto, tam, ZW - 100, 44, -0.03, quien=idp)
    pos = f'left:{x}px' if x is not None else 'left:540px'
    _bloque(idp, f'<div class="nsello" id="{idp}-s" style="{pos};top:{y}px;font-size:{fs}px">{texto}</div>', t - 0.02, t1, en)
    if x is None: I(f'#{idp}-s', xPercent=-50)
    if giro:
        I(f'#{idp}-s', opacity=0, scale=1.9, rotation=rot + 178); T(f'#{idp}-s', t - 0.03, 0.44, 'expo.out', opacity=1, scale=1, rotation=rot)
        fx(t - 0.03, 'whoosh', 0.2); fx(t + 0.12, 'thump', 0.34); sacude(f'#{idp}-s', t + 0.42, 8)
    else:
        I(f'#{idp}-s', opacity=0, scale=1.8, rotation=rot - 10); T(f'#{idp}-s', t - 0.03, 0.34, 'expo.out', opacity=1, scale=1, rotation=rot)
        fx(t - 0.03, 'thump', 0.34); sacude(f'#{idp}-s', t + 0.32, 8)
    fx(t + 0.05, 'ding', 0.2)
    _aviso(idp, t, t1)

def notas(idp, t0, t1, notas, y=384, en=None):
    """1-3 notas de papel con cinta que se PEGAN de golpe (ej. CLIENTE 1 · 2 · 3; ANTES / DESPUÉS).
    notas = [(rotulo, valor, segundo)]  valor = cifra o palabra corta (≤ 4 letras a 200 px; más largo se achica)."""
    _id(idp)
    n = len(notas)
    if not 1 <= n <= 3: raise SystemExit(f'noche.notas {idp}: van de 1 a 3 notas (tiene {n})')
    x0 = round(540 - (n * 270 + (n - 1) * 55) / 2); rots = (-5, 3, -2.5)
    h = ''
    for i, (rot_, val, _) in enumerate(notas):
        fs = _cabe(val, 200, 240, 60, -0.055, quien=idp)
        h += (f'<div class="npost" id="{idp}-n{i}" style="left:{x0 + i * 325}px;top:{y}px"><i class="ntape"></i>'
              f'<b class="ney">{rot_}</b><b class="nfig" style="font-size:{fs}px;top:{round(104 + (200 - fs) * 0.45)}px">{val}</b></div>')
    _bloque(idp, h, t0, t1, en)
    for i, (_, _, t_) in enumerate(notas):
        r = rots[i]
        I(f'#{idp}-n{i}', opacity=0, scale=1.45, rotation=r + (14 if i % 2 else -14), y=-70)
        T(f'#{idp}-n{i}', t_ - 0.03, 0.3, 'back.out(1.5)', opacity=1, scale=1, rotation=r, y=0)
        fx(t_ + 0.07, 'thump', 0.24); fx(t_ - 0.03, 'whoosh', 0.1)
    _aviso(idp, max(t_ for _, _, t_ in notas), t1)

def cta_sigueme(idp, t0, t_sigueme, lineas=(), antetitulo='', t_antetitulo=None, usuario='', boton='S&Iacute;GUEME',
                t_boton=None):
    """Cierre 'Sígueme': antetítulo (a máquina) + 1-2 líneas (ej. 'Tu agencia' / 'con IA.' en acento) + botón rojo
    GIGANTE con golpe + @usuario. Si el botón entra antes de que diga 'sígueme' (t_boton < t_sigueme - 0.45), un cursor
    lo TOCA justo en t_sigueme. Se queda hasta el final.  lineas = [(texto, segundo, color)] · usuario = '@tu_usuario'."""
    _id(idp)
    tb = (t_sigueme if t_boton is None else t_boton) - 0.03
    h = ''
    if antetitulo:
        ta = t0 + 0.3 if t_antetitulo is None else t_antetitulo
        h += f'<div class="ney" style="left:78px;top:276px">{typed(idp + "-e", antetitulo, ta, 48, 0.03)}</div>'
    fsl = min([_cabe(l[0], 80, ZW, 56, -0.045, quien=idp) for l in lineas] or [80])
    for i, l in enumerate(lineas):
        c = 'nac' if len(l) > 2 and l[2] == 'ac' else ''
        h += f'<div class="nt80" style="left:78px;top:{330 + i * 88}px;font-size:{fsl}px">{linea(f"{idp}-l{i}", l[0], c)}</div>'
    yb = 330 + len(lineas) * 88 + 14 if lineas else 380
    fsb = min(124 if lineas else 150, _cabe(boton, 150, ZW - 84, 60, -0.04, quien=idp))
    wb = _ancho(boton, fsb, -0.04) + 84; hb = fsb + 40
    h += f'<div class="nsbox" id="{idp}-b" style="left:78px;top:{yb}px"><b style="font-size:{fsb}px">{boton}</b></div>'
    if usuario: h += f'<div class="nhdl" id="{idp}-u" style="left:84px;top:{yb + hb + 14}px">{usuario}</div>'
    cursor = t_sigueme - tb > 0.45
    if cursor:
        px, py = 78 + wb * 0.78, yb + hb * 0.6
        h += (f'<div class="nrip" id="{idp}-r" style="left:{px - 60:.0f}px;top:{py - 60:.0f}px"></div>'
              f'<svg class="ncur" id="{idp}-k" style="left:{px - 12:.0f}px;top:{py - 6:.0f}px" viewBox="0 0 24 24" fill="#F3F0E8" '
              f'stroke="#121216" stroke-width="1.5" stroke-linejoin="round"><path d="M3 1.6v18.2l4.8-4.5 3.3 7.1 3.4-1.5-3.3-7h6.6z"/></svg>')
    if yb + hb + (70 if usuario else 0) > ZY1 + 30: print(f'  (aviso) {idp}: el cierre se sale de la zona; usa una sola línea o acórtalas.')
    _bloque(idp, h, t0, None)
    for i, l in enumerate(lineas): sube(f'#{idp}-l{i}', l[1] - 0.03, 'pop' if i == 0 else 'swipe', 0.16)
    golpe(f'#{idp}-b', tb, s0=1.9, r0=-9, r1=-2.5, g=0.4, sh=7); fx(tb + 0.05, 'ding', 0.28)
    if usuario: entra(f'#{idp}-u', tb + 0.3, 0.26, 'power3.out', y=20, snd=None)
    if cursor:
        I(f'#{idp}-k', opacity=0, x=230, y=190); T(f'#{idp}-k', t_sigueme - 0.52, 0.4, 'power3.out', opacity=1, x=0, y=0)
        FT(f'#{idp}-k', t_sigueme - 0.05, 0.2, {'scale': 0.8}, {'scale': 1}, 'back.out(3)')
        FT(f'#{idp}-b', t_sigueme - 0.03, 0.32, {'scale': 0.92}, {'scale': 1}, 'back.out(3)')
        I(f'#{idp}-r', opacity=0); FT(f'#{idp}-r', t_sigueme - 0.03, 0.45, {'opacity': 0.9, 'scale': 0.2}, {'opacity': 0, 'scale': 1.6}, 'power2.out')
        fx(t_sigueme - 0.05, 'click', 0.32); fx(t_sigueme, 'thump', 0.26)

def cta_palabra(idp, t0, palabra, t_palabra, verbo='Comenta', t_verbo=None, apoyo='', t_apoyo=None, antetitulo=''):
    """Cierre 'Comenta PALABRA': verbo (80 px) + la PALABRA en caja roja gigante con golpe + línea de apoyo.
    Se queda hasta el final. Pon la palabra también en MAYÚSCULAS en los subtítulos: subtitulos(cambios=[…])."""
    _id(idp)
    tv = t0 + 0.1 if t_verbo is None else t_verbo
    h = f'<div class="ney nac" style="left:78px;top:276px">{typed(idp + "-e", antetitulo, t0 + 0.04, 44, 0.03)}</div>' if antetitulo else ''
    h += f'<div class="nt80" style="left:78px;top:330px">{linea(idp + "-v", verbo)}</div>'
    fs = _cabe(palabra, 150, ZW - 84, 70, -0.04, quien=idp)
    h += f'<div class="nsbox" id="{idp}-b" style="left:78px;top:432px"><b style="font-size:{fs}px">{palabra}</b></div>'
    if apoyo:
        fa = _cabe(apoyo, 52, ZW, 40, -0.03, quien=idp)
        h += f'<div class="nt56" style="left:78px;top:{432 + fs + 40 + 22}px;font-size:{fa}px">{linea(idp + "-a", apoyo)}</div>'
    _bloque(idp, h, t0, None)
    sube(f'#{idp}-v', tv - 0.04, 'pop', 0.2)
    golpe(f'#{idp}-b', t_palabra - 0.03, s0=1.8, r0=-9, r1=-2.5, g=0.4, sh=7); fx(t_palabra + 0.02, 'ding', 0.3)
    if apoyo: sube(f'#{idp}-a', (t_palabra + 0.5 if t_apoyo is None else t_apoyo) - 0.05, 'pop', 0.16)


# =====================================================================================================
#  CIERRE
# =====================================================================================================
def css():
    """CSS del estilo con la paleta y el acento ya puestos (lo usa cerrar())."""
    fn = os.path.join(motor.P, 'noche.css')
    if not os.path.exists(fn): fn = os.path.join(AQUI, 'noche.css')
    s = open(fn, encoding='utf-8').read()
    r, g, b = _rgb(acento())
    for k, v in (('@AC@', acento()), ('@AL@', acento_claro()), ('@AD@', acento_oscuro()), ('@ACR@', f'{r},{g},{b}'),
                 ('@FO@', PALETA['fondo']), ('@PA@', PALETA['panel']), ('@CR@', PALETA['crema']), ('@GY@', PALETA['gris']),
                 ('@G2@', PALETA['gris2']), ('@PK@', PALETA['tinta_papel'])):
        s = s.replace(k, v)
    return s

def _limpiar_sfx():
    """efectos discretos: fuera los pop/swipe/click que caen encima de otro efecto (< 0.1 s) y un punto menos de volumen."""
    ok = []; last = -9.0
    for t, fn, g in sorted(motor.sfx, key=lambda e: e[0]):
        if fn in ('pop.wav', 'swipe.wav', 'click.wav') and t - last < 0.1: continue
        if fn == 'swipe.wav': g *= 0.75
        if fn == 'pop.wav': g *= 0.85
        ok.append((t, fn, round(g, 3)))
        if g >= 0.06: last = t
    motor.sfx[:] = ok

def cerrar(musica='auto', inicio_musica=0.0, volumen_musica=0.28, css_extra='', resumen='', limpiar_efectos=True, capturas=None):
    """Reemplaza a cerrar() del motor: mete los paneles de papel, cierra píldoras y rieles, limpia efectos encimados,
    agrega el CSS del estilo y escribe index.html + final_audio.wav. Siempre al final del build."""
    for p in _PANELES: motor.parts.append(p.html())
    _cerrar_pasos(); _aplicar_rieles()
    if limpiar_efectos: _limpiar_sfx()
    cambios = ' · '.join(f'{k} {t:.2f}' for t, k in sorted(_CAMBIOS))
    motor.cerrar(musica=musica, inicio_musica=inicio_musica, volumen_musica=volumen_musica, capturas=capturas,
                 css_extra=css() + css_extra, resumen=(resumen + ' | ' if resumen else '') + f'noche: {cambios or "solo card"}')
