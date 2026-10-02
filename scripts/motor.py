# -*- coding: utf-8 -*-
"""
reel-motion · MOTOR
====================
Todo lo que un build.py necesita para armar un reel de motion graphics con el presentador recortado:

  - palabras con tiempos (words.json) y buscador de frases  ->  f('frase')
  - zona segura bajo la cara (face.json)                    ->  bajo_barbilla(t0, t1)
  - línea de tiempo GSAP (listas init / tw) con atajos      ->  I, S, T, FT, win, pop, rise, leave, typed, steps…
  - escenario: fondos + cámara con 3 encuadres              ->  escenario(), ir_a('card' | 'full' | 'split', t)
  - piezas: papel rasgado, mascota, X dibujada, texto a mano, máquina de escribir, contadores
  - subtítulos palabra por palabra                          ->  subtitulos()
  - audio: voz limpia + música con ducking + efectos        ->  (dentro de cerrar())
  - ensamblar index.html para HyperFrames                   ->  cerrar()

Uso en un build.py (ver plantilla/build.py):

    import sys, os
    P = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, RUTA_A_SCRIPTS)          # carpeta scripts/ de la skill
    import motor
    motor.iniciar(P, correcciones={'cloud': 'Claude'})
    from motor import *                         # DESPUÉS de iniciar(): trae DUR, WD, f, I, T, parts…
    escenario()
    ...escenas...
    subtitulos()
    cerrar(musica='mi-pista.mp3')

Reglas del lienzo (1080x1920): nada sobre la cara; titulares en y 280-750 (encuadre 'card'); subtítulos en CAP_Y;
animar solo transform / opacity / clip-path (HyperFrames no admite animar top/left).
"""
import json, os, re, sys, html, math, random, shutil, subprocess, statistics

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(SKILL, 'recursos')
W, H = 1080, 1920

# ---------------- paleta (se cambia con iniciar(..., colores={'acento': '#0A7CFF'}) ) ----------------
RED = '#D11F1D'      # color de acento (tarjeta, palabra activa, CTA)
INK = '#0D1216'      # negro de los titulares
OFF = '#E8E8E1'      # fondo claro
BLUE = '#3354E4'     # segundo color de tarjeta
TERRA = '#D97757'    # terracota (logo Claude, mascota)
XRED = '#C2363C'     # rojo de las X y del texto a mano

# ---------------- encuadres de la cámara (#cam, transform-origin 0 0) ----------------
# card  = presentador RECORTADO a 0.8 sobre una tarjeta de color de 756 px; arriba quedan ~470 px para titulares
# full  = toma real a pantalla completa (tarjetas flotantes van bajo la barbilla)
# split = panel de "papel" arriba (PAPER_H px) y la toma real debajo
CARD_X, CARD_Y, CARD_W = 162, 759, 756
CAM = {'card': dict(x=90, y=529, scale=0.8, clipPath='inset(287.5px 45px 181.25px 90px)'),
       'full': dict(x=0, y=0, scale=1, clipPath='inset(0px 0px 0px 0px)'),
       'split': dict(x=0, y=405, scale=1, clipPath='inset(0px 0px 0px 0px)')}
PAPER_H = 780        # alto del papel en el encuadre 'split'
GROUND = 722         # "piso" dibujado dentro del papel (donde se paran la mascota y las monedas)
CAP_Y = 1530         # centro de la línea de subtítulos (bajo la barbilla en los 3 encuadres, encima de la interfaz de Instagram)
# OJO: iniciar() recalcula CAM['card'], CAM['split'] y CAP_Y según dónde está la cabeza del presentador (ver _encuadrar)

FONTS = [('IT', 700, 'intertight-700'), ('IT', 800, 'intertight-800'), ('IT', 900, 'intertight-900'), ('Inter', 500, 'inter-500'),
         ('Inter', 600, 'inter-600'), ('Inter', 700, 'inter-700'), ('JBM', 400, 'jetbrainsmono-400'), ('JBM', 500, 'jetbrainsmono-500'),
         ('JBM', 600, 'jetbrainsmono-600'), ('JBM', 700, 'jetbrainsmono-700'), ('PFI', 900, 'playfairdisplay-900i'), ('PFI', 800, 'playfairdisplay-800i'),
         ('PF', 900, 'playfairdisplay-900'), ('Caveat', 700, 'caveat-700'), ('Poppins', 800, 'poppins-800'), ('Poppins', 900, 'poppins-900'),
         ('Mont', 800, 'montserrat-800'), ('Mont', 900, 'montserrat-900')]

# ---------------- estado del reel (lo llena iniciar()) ----------------
P = None; DUR = 0.0; CUT = None; WD = []; FACE = None
rnd = random.Random(1)
init, tw, parts, sfx, caps = [], [], [], [], []
ESTADO = 'card'; PAPEL = None; SPLIT_OK = True
DO_AUDIO = '--no-audio' not in sys.argv
_n_caps = 0; _n_grupos = 0


# =====================================================================================================
#  PALABRAS
# =====================================================================================================
def norm(s):
    return re.sub(r'[^\wáéíóúñü%]', '', s.lower())

def cargar_palabras(proj, correcciones=None, separar_y=True):
    """words.json -> lista de {'text','start','end'}. correcciones = {'cloud': 'Claude'} (palabra mal oída -> correcta)."""
    Wd = json.load(open(os.path.join(proj, 'words.json'), encoding='utf-8'))
    out = []
    for w in Wd:
        t = w['text']
        # whisper pega la "Y" a la palabra siguiente ("Yyo") -> separar
        if separar_y and re.match(r'^Y[a-záéíóúñ]', t) and t.lower() not in ('ya', 'yo', 'yoga'):
            mid = w['start'] + 0.08
            out.append({'text': 'Y', 'start': w['start'], 'end': mid}); out.append({**w, 'text': t[1:], 'start': mid}); continue
        out.append(dict(w))
    for w in out:
        for a, b in (correcciones or {}).items():
            limpio = re.sub(r'[^\wáéíóúñü]', '', w['text'])
            if limpio.lower() == a.lower():
                w['text'] = re.sub(re.escape(limpio), b, w['text'], flags=re.I)
    return out

def f(frase, despues=0.0):
    """segundo en que EMPIEZA la primera aparición de `frase` (una o varias palabras) después de `despues`."""
    ws = [norm(x) for x in frase.split()]
    for i in range(len(WD)):
        if WD[i]['start'] < despues: continue
        if [norm(x['text']) for x in WD[i:i + len(ws)]] == ws:
            return WD[i]['start']
    raise SystemExit(f'FRASE NO ENCONTRADA en words.json: "{frase}" (después de {despues:.2f}s). Revisa cómo quedó escrita en la transcripción.')

def fe(frase, despues=0.0):
    """segundo en que TERMINA la frase."""
    ws = [norm(x) for x in frase.split()]
    for i in range(len(WD)):
        if WD[i]['start'] < despues: continue
        if [norm(x['text']) for x in WD[i:i + len(ws)]] == ws:
            return WD[i + len(ws) - 1]['end']
    raise SystemExit(f'FRASE NO ENCONTRADA en words.json: "{frase}"')

def guion():
    """imprime la transcripción con tiempos, 8 palabras por renglón (para planear las escenas)."""
    for i in range(0, len(WD), 8):
        print(f"{WD[i]['start']:6.2f}  " + ' '.join(x['text'] for x in WD[i:i + 8]))


# =====================================================================================================
#  CARA (zona segura)
# =====================================================================================================
class Cara:
    def __init__(self, proj):
        F = json.load(open(os.path.join(proj, 'face.json')))
        self.tr = [dict(x) for x in F['track'] if x.get('ok') and 150 <= x['w'] <= 620]
        if not self.tr: raise SystemExit('face.json no tiene detecciones de cara: revisa el video (¿se ve la cara de frente?)')
        self.cx = statistics.median([x['x'] + x['w'] / 2 for x in self.tr]); self.cy = statistics.median([x['y'] + x['h'] / 2 for x in self.tr])
        self.chin_med = statistics.median([x['chin'] for x in self.tr])
        ch = sorted(x['chin'] for x in self.tr); self.chin_p90 = ch[int(len(ch) * 0.9)] if len(ch) > 4 else ch[-1]
        # tope de la cabeza (pelo incluido): lo mide recortar.py sobre el recorte real; si no está, se estima con la caja de la cara
        self.top = statistics.median([x['y'] - 0.32 * x['h'] for x in self.tr])
        sil = os.path.join(proj, 'silueta.json')
        if os.path.exists(sil):
            try: self.top = float(json.load(open(sil))['top'])
            except Exception: pass

    def zona(self, t0, t1, margen=40):
        """(x0, y0, x1, y1) de la cabeza entre t0 y t1 en el encuadre 'full' (toma real), con margen."""
        s = [x for x in self.tr if t0 - 0.3 <= x['t'] <= t1 + 0.3] or self.tr
        return (int(min(x['x'] for x in s) - margen), int(min(x['y'] - 0.34 * x['h'] for x in s) - margen),
                int(max(x['x'] + x['w'] for x in s) + margen), int(max(x['chin'] for x in s) + margen))

    def chin(self, t0, t1):
        s = sorted(x['chin'] for x in self.tr if t0 - 0.3 <= x['t'] <= t1 + 0.3)
        if not s: return self.chin_med
        return s[int(len(s) * 0.9) if len(s) > 4 else -1]          # percentil 90 (ignora un cuadro raro)

    def safe_top(self, t0, t1, zoom=1.0, margin=40, lo=1000, hi=1230):
        c = self.cy + (self.chin(t0, t1) - self.cy) * zoom
        return int(min(hi, max(lo, c + margin)))

def bajo_barbilla(t0, t1):
    """y (px) donde puede EMPEZAR una tarjeta flotante en el encuadre 'full' sin tocar la cara entre t0 y t1."""
    return FACE.safe_top(t0, t1, 1.0)

def zona_cara(t0, t1, margen=40):
    """(x0, y0, x1, y1): rectángulo de la cabeza en el encuadre 'full' entre t0 y t1. Nada gráfico debe entrar ahí."""
    return FACE.zona(t0, t1, margen)

def esquivar_cara(cx, cy, w, h, zona):
    """Si una pieza de w x h centrada en (cx, cy) pisa la zona de la cara, la corre hacia el lado más cercano
    (izquierda/derecha; si quedaría demasiado afuera de la pantalla, hacia arriba/abajo). Devuelve el nuevo (cx, cy)."""
    x0, y0, x1, y1 = zona
    if cx + w / 2 <= x0 or cx - w / 2 >= x1 or cy + h / 2 <= y0 or cy - h / 2 >= y1: return cx, cy
    nx = (x0 - w / 2) if cx < (x0 + x1) / 2 else (x1 + w / 2)
    if nx - w / 2 >= -w * 0.35 and nx + w / 2 <= W + w * 0.35: return int(nx), cy          # puede salirse hasta un 35 % de la pantalla
    return cx, int(y0 - h / 2 if cy < (y0 + y1) / 2 else y1 + h / 2)

def _encuadrar():
    """Ajusta los encuadres 'card' y 'split' y la línea de subtítulos a CÓMO se grabó este presentador
    (cada quien se graba distinto: más cerca o más lejos, más arriba, corrido a un lado)."""
    global CAP_Y, SPLIT_OK
    top = FACE.top; alto = max(120.0, FACE.chin_p90 - top)                                 # alto de la cabeza (pelo -> barbilla)
    s = round(min(1.0, max(0.8, 520.0 / alto)), 3)                                          # si se grabó lejos, la tarjeta lo acerca (máx. 1.0)
    tx = round(min(CARD_X, max(CARD_X + CARD_W - W * s, W / 2 - s * FACE.cx)))             # cara centrada en la tarjeta
    ty = round(min(CARD_Y, max(H - H * s, CARD_Y + 84 - s * top)))                          # pelo ~84 px bajo el borde de la tarjeta
    CAM['card'] = dict(x=tx, y=ty, scale=s, clipPath='inset(%gpx %gpx %gpx %gpx)' % (
        round((CARD_Y - ty) / s, 2), round(W - (CARD_X + CARD_W - tx) / s, 2), round(H - (H - ty) / s, 2), round((CARD_X - tx) / s, 2)))
    ty2 = round(max(0, PAPER_H + 17 - top))                                                 # la cabeza asoma justo bajo el papel
    CAM['split'] = dict(x=0, y=ty2, scale=1, clipPath='inset(0px 0px 0px 0px)')
    bajo_card = ty + s * FACE.chin_p90; bajo_split = ty2 + FACE.chin_p90                    # barbilla en pantalla en cada encuadre
    SPLIT_OK = bajo_split + 75 <= 1610
    CAP_Y = int(min(1610, max(1530, bajo_card + 75, bajo_split + 75 if SPLIT_OK else 0)))
    if not SPLIT_OK:
        print("  (aviso) la cara ocupa mucho cuadro: NO uses el encuadre 'split' en este video (la cabeza no cabe entre el papel y los "
              "subtítulos). Arma el reel con 'card' y 'full'. Para la próxima: grabar un poco más lejos (cabeza y pecho).")
    if bajo_card + 75 > 1610:
        print("  (aviso) cara MUY grande: en 'card' los subtítulos quedan cerca de la boca. Súbelos con subtitulos(y=...) solo si hay dónde.")

def tarjeta_en_camara():
    """(izq, arriba, der, abajo) de la tarjeta en coordenadas de #cam (para dibujar dentro de la cámara algo que calce con la tarjeta)."""
    c = CAM['card']; s = c['scale']
    return ((CARD_X - c['x']) / s, (CARD_Y - c['y']) / s, (CARD_X + CARD_W - c['x']) / s, (H - c['y']) / s)


# =====================================================================================================
#  LÍNEA DE TIEMPO (GSAP)
# =====================================================================================================
_js = lambda d: json.dumps(d, ensure_ascii=False)

def I(el, **p):
    """estado inicial (gsap.set antes de la línea de tiempo)."""
    init.append(f'gsap.set("{el}",{_js(p)});')

def S(el, t, **p):
    """cambio instantáneo en el segundo t."""
    tw.append(f'tl.set("{el}",{_js(p)},{max(0, t):.3f});')

def T(el, t, dur, ease='power2.out', **p):
    """animación hacia los valores p, empezando en t y durando dur."""
    p = dict(p, duration=round(dur, 3), ease=ease); tw.append(f'tl.to("{el}",{_js(p)},{max(0, t):.3f});')

def FT(el, t, dur, a, b, ease='power2.out'):
    """animación de a -> b (para golpes que se repiten sobre el mismo elemento: saltos, destellos)."""
    b = dict(b, duration=round(dur, 3), ease=ease, immediateRender=False); tw.append(f'tl.fromTo("{el}",{_js(a)},{_js(b)},{max(0, t):.3f});')

def win(el, t0, t1=None):
    """el elemento solo se ve entre t0 y t1."""
    if t0 <= 0: I(el, opacity=1)
    else: I(el, opacity=0); S(el, t0, opacity=1)
    if t1 is not None and t1 < DUR: S(el, t1, opacity=0)

def fx(t, nombre, g):
    """efecto de sonido: pop, whoosh, swipe, click, ding, thump (recursos/sfx). g = volumen 0-1."""
    sfx.append((max(0, t), nombre + '.wav', g))

def pop(el, t, sc=0.4, dur=0.3, ease='back.out(2)', snd='pop', g=0.2):
    """aparece con rebote."""
    I(el, opacity=0, scale=sc); T(el, t, dur, ease, opacity=1, scale=1)
    if snd: fx(t, snd, g)

def rise(el, t, dur=0.36):
    """línea de titular que sube desde detrás de su máscara (el elemento debe ir dentro de .ln > .in)."""
    I(el, yPercent=115); T(el, t, dur, 'power3.out', yPercent=0)

def leave(el, t, dur=0.16):
    """sale hacia arriba desvaneciéndose, terminando en t."""
    T(el, t - dur, dur, 'power2.in', opacity=0, y=-34)

def typed(idp, text, t, cps=30, snd=0.07, cls=''):
    """máquina de escribir: devuelve el HTML (una letra por span) y programa su aparición desde t a cps letras/seg."""
    out = ''
    for i, c in enumerate(text):
        out += f'<span class="ch {cls}" id="{idp}{i}">{html.escape(c) if c != " " else "&nbsp;"}</span>'
        I(f'#{idp}{i}', opacity=0); S(f'#{idp}{i}', t + i / cps, opacity=1)
        if snd and i % 3 == 0: fx(t + i / cps, 'click', snd)
    return out

def steps(idp, values, t0, t1, cls=''):
    """contador: los valores se reemplazan uno a uno entre t0 y t1 (el último se queda). Devuelve el HTML."""
    out = ''; n = len(values)
    for i, v in enumerate(values):
        a = t0 + (t1 - t0) * i / n; b = t0 + (t1 - t0) * (i + 1) / n
        out += f'<span class="stp {cls}" id="{idp}{i}">{v}</span>'
        I(f'#{idp}{i}', opacity=0); S(f'#{idp}{i}', a, opacity=1)
        if i < n - 1: S(f'#{idp}{i}', b, opacity=0)
    return out

def flash(t, a=0.3):
    FT('#flash', t, 0.18, {'opacity': a}, {'opacity': 0}, 'power1.out')


# =====================================================================================================
#  PIEZAS
# =====================================================================================================
def logo_svg(nombre, color):
    s = open(os.path.join(REC, 'logos', nombre + '.svg'), encoding='utf-8').read()
    return s.replace('<svg ', f'<svg fill="{color}" ', 1)

LOGO = logo_svg('claude', '#fff')
def cc(cls=''):
    """cuadrito terracota con el logo de Claude."""
    return f'<span class="cc {cls}">{LOGO}</span>'

def mascot(idp):
    """mascota (cajita terracota con patas). Caras: n normal, h feliz, w preocupada -> mood(idp, t, 'h')."""
    return (f'<svg viewBox="0 0 160 130" id="{idp}">'
            '<g fill="#B85A3A" stroke="#2A1710" stroke-width="5" stroke-linejoin="round">'
            '<rect x="34" y="94" width="14" height="26" rx="5"/><rect x="55" y="94" width="14" height="26" rx="5"/>'
            '<rect x="91" y="94" width="14" height="26" rx="5"/><rect x="112" y="94" width="14" height="26" rx="5"/>'
            f'<rect id="{idp}al" x="6" y="48" width="24" height="20" rx="6"/><rect id="{idp}ar" x="130" y="48" width="24" height="20" rx="6"/>'
            '<rect x="22" y="14" width="116" height="88" rx="12" fill="#C4623D"/></g>'
            f'<g id="{idp}n" fill="#2A1710"><ellipse cx="62" cy="54" rx="6.5" ry="9.5"/><ellipse cx="98" cy="54" rx="6.5" ry="9.5"/></g>'
            f'<g id="{idp}h" fill="none" stroke="#2A1710" stroke-width="6" stroke-linecap="round"><path d="M52 59 Q62 44 72 59"/><path d="M88 59 Q98 44 108 59"/></g>'
            f'<g id="{idp}w"><ellipse cx="60" cy="52" rx="11" ry="12" fill="#fff" stroke="#2A1710" stroke-width="4"/><ellipse cx="96" cy="52" rx="11" ry="12" fill="#fff" stroke="#2A1710" stroke-width="4"/>'
            '<circle cx="55" cy="54" r="4.5" fill="#2A1710"/><circle cx="91" cy="54" r="4.5" fill="#2A1710"/>'
            '<path d="M126 22 q7 12 0 18 q-7 -6 0 -18z" fill="#9CC8E8" stroke="#2A1710" stroke-width="3"/></g></svg>')

def mood(idp, t, m):
    for k in 'nhw': S(f'#{idp}{k}', t, opacity=1 if k == m else 0)

def mascot_init(idp, m='n'):
    for k in 'nhw': I(f'#{idp}{k}', opacity=1 if k == m else 0)

def jag(y0, amp, step, seed, w=W):
    r = random.Random(seed); pts = []; x = 0.0
    while x < w:
        pts.append((round(x, 1), round(y0 + r.uniform(-amp, amp), 1))); x += r.uniform(step * .45, step * 1.4)
    pts.append((w, round(y0 + r.uniform(-amp, amp), 1)))
    return pts

def blob(cx, cy, rx, ry, seed, n=46, j=.085):
    r = random.Random(seed); pts = []
    for i in range(n):
        a = 2 * math.pi * i / n; k = 1 + r.uniform(-j, j) + .05 * math.sin(3 * a + seed)
        pts.append(f'{cx + rx * k * math.cos(a):.1f},{cy + ry * k * math.sin(a):.1f}')
    return 'M' + ' L'.join(pts) + 'Z'

def paper_svg(seed):
    """fondo del panel de papel (encuadre 'split'): borde rasgado + manchas de color. seed distinto = papel distinto."""
    e1 = jag(PAPER_H - 12, 9, 26, seed); e2 = jag(PAPER_H + 6, 9, 22, seed + 5)
    d1 = 'M0,0 L%d,0 ' % W + ' '.join(f'L{x},{y}' for x, y in reversed(e1)) + ' Z'
    d2 = 'M0,0 L%d,0 ' % W + ' '.join(f'L{x},{y}' for x, y in reversed(e2)) + ' Z'
    lt = jag(468, 20, 70, seed + 9)
    d3 = 'M0,%d ' % (PAPER_H + 30) + ' '.join(f'L{x},{y}' for x, y in lt) + f' L{W},{PAPER_H + 30} Z'
    return (f'<svg class="psvg" width="{W}" height="{PAPER_H + 40}" viewBox="0 0 {W} {PAPER_H + 40}">'
            f'<defs><clipPath id="pc{seed}"><path d="{d1}"/></clipPath></defs>'
            f'<path d="{d2}" fill="#FCFCF7"/><g clip-path="url(#pc{seed})"><rect width="{W}" height="{PAPER_H + 40}" fill="#EFEDDD"/>'
            f'<path d="{blob(150, 372, 280, 246, seed + 2)}" fill="#E9DDD0"/><path d="{d3}" fill="#F7F5EC"/>'
            f'<path d="{blob(940, 96, 232, 200, seed + 3)}" fill="#CB8473"/></g></svg>')

X_SVG = ('<svg class="xs" viewBox="0 0 50 50"><path class="x1" d="M8 9 L42 41"/><path class="x2" d="M41 8 L9 42"/></svg>')

def draw_x(sel, t, g=0.3):
    """dibuja una X (dos trazos) con golpe. sel = selector del contenedor que tiene {X_SVG}."""
    I(f'{sel} .x1', strokeDasharray=50, strokeDashoffset=50); I(f'{sel} .x2', strokeDasharray=50, strokeDashoffset=50)
    T(f'{sel} .x1', t, 0.11, 'none', strokeDashoffset=0); T(f'{sel} .x2', t + 0.12, 0.11, 'none', strokeDashoffset=0)
    fx(t, 'thump', g)

def handwrite(sel, t, dur=0.42, snd=0.12, pen=None):
    """revela un texto de izquierda a derecha, como si se escribiera (pen = id del lápiz que acompaña el trazo)."""
    I(sel, clipPath='inset(-10% 100% -10% 0%)'); T(sel, t, dur, 'none', clipPath='inset(-10% 0% -10% 0%)')
    if snd: fx(t, 'swipe', snd)
    if pen:
        I(pen, xPercent=-100, opacity=0); S(pen, t, opacity=1); T(pen, t, dur, 'none', xPercent=0); S(pen, t + dur + 0.02, opacity=0)

def serif(idp, text):
    """titular serif itálico con lápiz (para handwrite('#id', t, pen='#idp'))."""
    return f'<span class="hwrap"><span class="wr" id="{idp}">{text}</span><i class="penw" id="{idp}p"><i class="pen"></i></i></span>'


# =====================================================================================================
#  ESCENARIO Y CÁMARA
# =====================================================================================================
def cam_to(estado, t, dur, ease='power3.inOut'):
    T('#cam', t, dur, ease, **CAM[estado])

def escenario(inicio='card', codigo_fondo=''):
    """fondos (uno por estilo) + cámara con la toma real, los rellenos de la tarjeta y el recorte con alfa.
    inicio = encuadre con el que arranca el reel. codigo_fondo = texto de código decorativo para el fondo 'código'."""
    global ESTADO
    ESTADO = inicio
    L_, T_, R_, B_ = [int(round(v)) for v in tarjeta_en_camara()]              # la tarjeta, vista desde dentro de la cámara
    brush = ('M%s Z' % ' L'.join(f'{x:.1f},{y:.1f}' for x, y in
             [(L_ + 6 + rnd.uniform(0, 26), y) for y in range(B_ + 21, T_ + 43, -70)] +
             [(x, T_ + 30 + rnd.uniform(-26, 30)) for x in range(L_ + 20, R_ - 5, 46)] +
             [(R_ - 5 - rnd.uniform(0, 30), y) for y in range(T_ + 43, B_ + 22, 70)]))
    parts.append(f'''
<div class="bg" id="bgsz"></div>
<div class="bg" id="bgbl"></div>
<div class="bg" id="bgpa"><svg width="{W}" height="{H}" viewBox="0 0 {W} {H}"><path d="{blob(920, 150, 260, 220, 4)}" fill="#CB8473"/><path d="{blob(140, 830, 330, 300, 6)}" fill="#E7DCCF"/><path d="M0,1010 {' '.join(f'L{x},{y}' for x, y in jag(1010, 26, 80, 12))} L{W},{H} L0,{H} Z" fill="#F6F5EE"/></svg></div>
<div class="bg" id="bgcd"><pre>{html.escape(codigo_fondo)}</pre></div>
<div class="bg" id="bgpp"><i></i></div>
<div class="bg" id="bgdk"></div>
<div class="bg" id="bgcr"></div>
<div id="fx" data-layout-allow-overflow><div id="cam" data-layout-allow-overflow>
  <video id="v" class="clip" data-start="0" data-duration="{DUR}" data-media-start="0" data-track-index="0" src="cut.mp4" muted playsinline></video>
  <div class="fill" id="fillA"></div><div class="fill" id="fillB"></div><div class="fill" id="fillC"></div>
  <svg class="fill" id="brush" viewBox="0 0 {W} {H}"><path d="{brush}" fill="#D27366"/></svg>
  <video id="cutv" class="clip" data-start="0" data-duration="{DUR}" data-media-start="0" data-track-index="1" src="cutout.webm" muted playsinline></video>
</div></div>
<div id="bpf"><i class="dim"></i><b>756 px</b></div>
<div id="cdf"></div>
<div id="flash"></div>''')
    I('#cam', **CAM[inicio])
    if inicio == 'card': I('#v', opacity=0)
    else: I('#fillA', opacity=0); I('#cutv', opacity=0)
    for b_ in ('bgbl', 'bgpa', 'bgcd', 'bgpp', 'bgdk', 'bgcr'): I('#' + b_, opacity=0)
    I('#fillB', clipPath='inset(100% 0% 0% 0%)'); I('#fillC', opacity=0); I('#brush', opacity=0)
    I('#bpf', opacity=0); I('#cdf', opacity=0); I('#flash', opacity=0)

def ir_a(estado, t, papel=None, sonido=True):
    """Cambia de encuadre en el segundo t ('card' | 'full' | 'split').
    papel = selector del panel de papel que ENTRA cuando vas a 'split' (ej. '#pp1'); al salir de 'split' se retira solo.
    Devuelve cuánto dura la transición (para saber desde cuándo ya está quieto el encuadre)."""
    global ESTADO, PAPEL
    a = ESTADO; fuera = -(PAPER_H + 60); dur = 0.4
    if estado == 'split' and not SPLIT_OK: print(f"  (aviso) ir_a('split', {t:.2f}): en este video la cara es muy grande para 'split' (los subtítulos pueden tapar la boca).")
    if a == estado and estado != 'split': return 0
    if a == 'card' and estado == 'full':
        S('#v', t, opacity=1); T('#fillA', t + 0.03, 0.26, 'power1.inOut', opacity=0); cam_to('full', t, 0.36); S('#cutv', t + 0.36, opacity=0); dur = 0.36
    elif a == 'full' and estado == 'card':
        S('#cutv', t, opacity=1); cam_to('card', t, 0.4); T('#fillA', t + 0.16, 0.22, 'power1.out', opacity=1); S('#v', t + 0.42, opacity=0); dur = 0.42
    elif a == 'full' and estado == 'split':
        I(papel, y=fuera); T(papel, t, 0.34, 'power3.out', y=0); T('#cam', t, 0.34, 'power3.out', **CAM['split']); dur = 0.34
    elif a == 'card' and estado == 'split':
        S('#bgcr', t, opacity=1)
        S('#v', t, opacity=1); T('#fillA', t, 0.2, 'power1.out', opacity=0); cam_to('split', t, 0.4); S('#cutv', t + 0.4, opacity=0)
        I(papel, y=fuera); T(papel, t + 0.12, 0.34, 'power3.out', y=0); dur = 0.46
    elif a == 'split' and estado == 'card':
        T(PAPEL, t, 0.26, 'power2.in', y=fuera); S('#cutv', t, opacity=1); S('#bgcr', t + 0.1, opacity=0)
        cam_to('card', t + 0.03, 0.4); T('#fillA', t + 0.2, 0.22, 'power1.out', opacity=1); S('#v', t + 0.45, opacity=0); dur = 0.45
    elif a == 'split' and estado == 'full':
        T(PAPEL, t, 0.26, 'power2.in', y=fuera); cam_to('full', t, 0.36); dur = 0.36
    elif a == 'split' and estado == 'split':
        T(PAPEL, t, 0.24, 'power2.in', y=fuera); I(papel, y=fuera); T(papel, t + 0.2, 0.34, 'power3.out', y=0); dur = 0.54
    if sonido: fx(t, 'whoosh', 0.3)
    ESTADO = estado
    if estado == 'split': PAPEL = papel
    return dur


# =====================================================================================================
#  PIEZAS LISTAS (atajos de alto nivel para el encuadre 'card'; con esto ya sale un reel completo)
# =====================================================================================================
def _clase_titular(lineas):
    largo = max(len(re.sub(r'<[^>]+>|&[a-z]+;', 'x', l)) for l in lineas)
    return 'h1' if largo <= 13 else ('h1 h1s' if largo <= 19 else 'h2')

def gancho(frase, hasta, saltos=(), acento=(), etiqueta='', marca=''):
    """Titular del gancho en la zona de titulares: cada palabra aparece en el instante en que se dice.
    frase   : las primeras palabras del video TAL COMO están en words.json (sin puntuación), ej. 'Estas animaciones que estás viendo'
    hasta   : segundo en que el titular se va
    saltos  : índices de palabra tras los que hay salto de línea, ej. (1, 4)  ·  acento: índices de palabras en color
    etiqueta: texto pequeño arriba a la derecha  ·  marca: texto junto al logo (vacío = sin logo)."""
    ws = frase.split(); t = 0.0; html_ = ''
    for i, w in enumerate(ws):
        tw_ = f(w, t); t = tw_ + 0.01
        html_ += f'<span class="{"ac" if i in acento else ""}" id="gk{i}">{html.escape(w)}</span>' + ('<br>' if i in saltos else ' ')
        if i > 0: I(f'#gk{i}', opacity=0); S(f'#gk{i}', tw_ - 0.03, opacity=1)
    tag = f'<div class="tag">{cc()}<b>{html.escape(marca)}</b></div>' if marca else ''
    lab = f'<div class="lab">{html.escape(etiqueta)}</div>' if etiqueta else ''
    parts.append(f'<div class="hk hk-sz" id="gk">{tag}{lab}<div class="ttl">{html_}</div></div>')
    win('#gk', 0, hasta)

def cabecera(idp, t0, t1, lineas, antetitulo='', top=334):
    """Titular sobre la tarjeta: antetítulo (a máquina) + líneas que SUBEN cuando se dicen.
    lineas = [(texto, segundo, color)]  con color '' | 'red' | 'blu'.  t0 = entra el bloque · t1 = sale (None = se queda).
    El tamaño se ajusta solo: hasta 13 letras por línea = grande; hasta 19 = mediano; más = pequeño (máx. ~24)."""
    eb = f'<div class="eb" style="left:78px;top:282px">{typed(idp + "e", antetitulo, t0 + 0.02, 40, 0)}</div>' if antetitulo else ''
    ln = ''.join(f'<div class="ln"><span class="in {c}" id="{idp}l{i}">{tx}</span></div>' for i, (tx, _, c) in enumerate(lineas))
    parts.append(f'<div class="hd" id="{idp}">{eb}<div class="{_clase_titular([l[0] for l in lineas])}" style="left:74px;top:{top}px">{ln}</div></div>')
    win('#' + idp, t0)
    for i, (_, t, _) in enumerate(lineas):
        rise(f'#{idp}l{i}', t - 0.03); fx(t - 0.03, 'pop' if i else 'swipe', 0.16)
    if t1 is not None: leave('#' + idp, t1)

def lista(idp, t0, t1, items, antetitulo='', top=350):
    """Lista de fichas sobre la tarjeta: cada ítem aparece UNO POR UNO cuando se dice.  items = [(texto, segundo)] (máx. 4, ≤ 24 letras)."""
    eb = f'<div class="eb" style="left:78px;top:282px">{typed(idp + "e", antetitulo, t0 + 0.02, 40, 0)}</div>' if antetitulo else ''
    rows = ''.join(f'<div class="bchip li" id="{idp}i{i}" style="left:78px;top:{top + i * 96}px">{tx}</div>' for i, (tx, _) in enumerate(items))
    parts.append(f'<div class="hd" id="{idp}">{eb}{rows}</div>')
    win('#' + idp, t0)
    for i, (_, t) in enumerate(items):
        I(f'#{idp}i{i}', clipPath='inset(0% 100% 0% 0%)'); T(f'#{idp}i{i}', t - 0.03, 0.26, 'power2.out', clipPath='inset(0% 0% 0% 0%)'); fx(t - 0.03, 'pop', 0.18)
    if t1 is not None: leave('#' + idp, t1)

def numero(idp, t0, t1, cifra, t_cifra, rotulos=(), antetitulo=''):
    """Dato gigante sobre la tarjeta (ej. '<u>+</u>7', '3%', '$0', '10x') con 1-2 rótulos cortos a su derecha.  rotulos = [(texto, segundo)].
    La cifra se achica sola para caber (ideal: 2-3 caracteres). <u>…</u> = signo pequeño delante."""
    eb = f'<div class="eb" style="left:78px;top:282px">{typed(idp + "e", antetitulo, t0 + 0.02, 44, 0)}</div>' if antetitulo else ''
    plano = re.sub(r'<[^>]+>', '', re.sub(r'<u>.*?</u>', '+', cifra))
    ancho = sum({'%': .9, 'M': .85, 'W': .85, '.': .28, ',': .28, '+': .36, '1': .45}.get(c, .6) for c in plano)
    fs = min(440, int(520 / max(ancho, .6)))
    col = ''.join(f'<div class="{"h1" if i == 0 else "h2"}"><div class="ln"><span class="in" id="{idp}r{i}">{tx}</span></div></div>' for i, (tx, _) in enumerate(rotulos[:2]))
    parts.append(f'<div class="hd" id="{idp}">{eb}<div class="nrow" style="left:60px;top:330px"><div class="nmask"><div class="big7" id="{idp}n" style="font-size:{fs}px">{cifra}</div></div>'
                 f'<div class="ncol" style="margin-top:{int(fs * 0.16)}px">{col}</div></div></div>')
    win('#' + idp, t0); I(f'#{idp}n', yPercent=105); T(f'#{idp}n', t_cifra - 0.08, 0.42, 'power3.out', yPercent=0); fx(t_cifra - 0.08, 'thump', 0.3)
    for i, (_, t) in enumerate(rotulos[:2]): rise(f'#{idp}r{i}', t - 0.02, 0.3)
    if t1 is not None: leave('#' + idp, t1)

def cta(idp, t0, palabra, t_palabra, apoyo='', t_apoyo=None, antetitulo='', verbo='Comenta', t_verbo=None):
    """Cierre: verbo ('Comenta') + caja de color con la PALABRA clave (golpe) + línea de apoyo. Se queda hasta el final."""
    t_verbo = t0 + 0.1 if t_verbo is None else t_verbo
    eb = f'<div class="eb rd" style="left:78px;top:282px">{typed(idp + "e", antetitulo, t0 + 0.02, 40, 0)}</div>' if antetitulo else ''
    sub = f'<div class="vsub" id="{idp}p" style="top:676px">{apoyo}</div>' if apoyo else ''
    parts.append(f'<div class="hd" id="{idp}">{eb}<div class="h1 ctr" style="top:322px"><div class="ln"><span class="in" id="{idp}k">{verbo}</span></div></div>'
                 f'<div class="vbox" id="{idp}v" style="top:462px"><b>{palabra}</b></div>{sub}</div>')
    win('#' + idp, t0); rise(f'#{idp}k', t_verbo - 0.04); fx(t_verbo - 0.04, 'pop', 0.2)
    I(f'#{idp}v', opacity=0, scale=1.7, rotation=-9, xPercent=-50); T(f'#{idp}v', t_palabra - 0.03, 0.2, 'power3.out', opacity=1, scale=1, rotation=-2.5)
    fx(t_palabra - 0.03, 'thump', 0.4); fx(t_palabra + 0.02, 'ding', 0.3)
    if apoyo:
        t_apoyo = t_palabra + 0.5 if t_apoyo is None else t_apoyo
        I(f'#{idp}p', opacity=0, y=24); T(f'#{idp}p', t_apoyo - 0.05, 0.22, 'power2.out', opacity=1, y=0); fx(t_apoyo - 0.05, 'pop', 0.16)


# =====================================================================================================
#  SUBTÍTULOS  (palabra por palabra; la que se está diciendo va en el color de acento)
# =====================================================================================================
def _partir_frase(ws, maxw=3, maxc=21):
    tx = lambda g: ' '.join(x['text'] for x in g)
    groups = []; cur = []
    for w in ws:
        if cur and (len(cur) >= maxw or len(tx(cur + [w])) > maxc): groups.append(cur); cur = []
        cur.append(w)
    if cur: groups.append(cur)
    if len(groups) >= 2 and len(groups[-1]) == 1 and len(groups[-2]) == 3 and len(tx(groups[-2][-1:] + groups[-1])) <= maxc:
        groups[-1] = groups[-2][-1:] + groups[-1]; groups[-2] = groups[-2][:-1]      # no dejar una palabra huérfana
    return groups

def subtitulos(desde=0.0, hasta=None, propios=('Claude', 'Code', 'Opus'), cambios=None, huecos=(), y=None):
    """Subtítulos de 1-3 palabras en una sola línea (CAP_Y).
    desde / hasta : tramo que lleva subtítulos (el gancho normalmente NO: el titular ya es el texto).
    propios       : nombres propios (llevan mayúscula pero NO inician frase; whisper en modo palabra no pone puntos).
    cambios       : [(palabra, reemplazo, desde_segundo)] p. ej. [('video', 'VIDEO', t_cta)] para resaltar la palabra clave.
    huecos        : [(t0, t1)] tramos SIN subtítulos (p. ej. mientras suena un clip que ya trae su texto)."""
    global _n_caps, _n_grupos
    hasta = DUR if hasta is None else hasta; y = CAP_Y if y is None else y
    words = [dict(w) for w in WD if desde - 0.02 <= w['start'] < hasta and not any(a <= w['start'] < b for a, b in huecos)]
    for i, w in enumerate(words):
        if norm(w['text']) == 'aún' and i + 1 < len(words) and norm(words[i + 1]['text']) == 'así': w['text'] = 'aun'
        for pal, rep, t0 in (cambios or []):
            if norm(w['text']) == norm(pal) and w['start'] >= t0: w['text'] = rep
    mayus = {rep for _, rep, _ in (cambios or [])}
    def inicia_frase(w):
        t = w['text'].strip('¿¡,.')
        return t[:1].isupper() and t not in propios and t not in mayus
    chunks = []; sent = []
    for i, w in enumerate(words):
        sent.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        corte_hueco = nxt is not None and any(w['start'] < a <= nxt['start'] for a, _ in huecos)
        if w['text'][-1:] in '.?!,' or nxt is None or inicia_frase(nxt) or corte_hueco: chunks += _partir_frase(sent); sent = []
    for k, ch in enumerate(chunks):
        nxt = chunks[k + 1][0]['start'] if k + 1 < len(chunks) else DUR
        hide = min(ch[-1]['end'] + 0.3, nxt - 0.03)
        for j, w in enumerate(ch):
            a = max(0, w['start'] - 0.03); b = (ch[j + 1]['start'] - 0.03) if j + 1 < len(ch) else hide
            if b - a < 0.05: continue
            sp = ''.join(f'<span class="{"on" if i == j else ""}">{html.escape(x["text"].strip(",."))}</span>' for i, x in enumerate(ch[:j + 1]))
            caps.append(f'<div class="cap" id="k{_n_caps}" style="top:{y - 34}px">{sp}</div>')
            I(f'#k{_n_caps}', opacity=0); S(f'#k{_n_caps}', a, opacity=1); S(f'#k{_n_caps}', b, opacity=0); _n_caps += 1
    _n_grupos += len(chunks)
    return chunks


# =====================================================================================================
#  AUDIO
# =====================================================================================================
def _run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])
    return r

def _buscar_musica(nombre):
    if not nombre: return None
    if nombre == 'auto':        # primera pista que haya en <proyecto>/musica o en recursos/musica de la skill
        import glob
        for d in (os.path.join(P, 'musica'), os.path.join(REC, 'musica')):
            for ext in ('mp3', 'wav', 'm4a', 'ogg', 'flac'):
                g = sorted(glob.glob(os.path.join(d, '*.' + ext)))
                if g: return g[0]
        print('  (aviso) sin música: no hay pistas en <proyecto>/musica ni en recursos/musica de la skill. El reel sale con voz y efectos.')
        return None
    for c in (nombre, os.path.join(P, nombre), os.path.join(P, 'musica', nombre), os.path.join(REC, 'musica', nombre)):
        if os.path.isfile(c): return c
    print(f'  (aviso) no encontré la música "{nombre}": el reel sale solo con voz y efectos. Ponla en recursos/musica/ o en la carpeta del proyecto.')
    return None

def mezclar_audio(dur, musica=None, inicio_musica=0.0, volumen_musica=0.28, out='final_audio.wav'):
    """voz limpia (pasa-altos + presencia + compresor + -16 LUFS) + música nivelada con ducking suave + efectos -> final_audio.wav (-14 LUFS)."""
    wk = os.path.join(P, '_work'); voice = os.path.join(P, 'voice.wav')
    _run(['ffmpeg', '-y', '-v', 'error', '-i', os.path.join(wk, 'voice_raw.wav'), '-af',
          'highpass=f=85,equalizer=f=3000:width_type=q:w=1.2:g=3,acompressor=threshold=-20dB:ratio=3:attack=10:release=200:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=11',
          '-ar', '48000', '-ac', '1', voice])
    ins = ['-i', voice]; fc = []; mixes = ['[0:a]']; k0 = 1
    mus = _buscar_musica(musica)
    if mus:
        lvl = os.path.join(wk, 'music_lvl.wav')
        _run(['ffmpeg', '-y', '-v', 'error', '-ss', str(inicio_musica), '-stream_loop', '-1', '-i', mus, '-t', f'{dur:.3f}', '-af',
              f'loudnorm=I=-14:TP=-1.5:LRA=7,afade=t=in:d=0.4,afade=t=out:st={dur - 1.4:.3f}:d=1.3', '-ar', '48000', '-ac', '2', lvl])
        ins += ['-i', lvl]
        fc += [f'[1:a]volume={volumen_musica}[m]', '[0:a]asplit=2[v1][vsc]',
               '[m][vsc]sidechaincompress=threshold=0.10:ratio=3:attack=15:release=320:makeup=1[duck]']
        mixes = ['[v1]', '[duck]']; k0 = 2
    for k, (t, fn, g) in enumerate(sfx):
        ins += ['-i', os.path.join(REC, 'sfx', fn)]
        ms = max(0, int(round(t * 1000)))
        fc.append(f'[{k + k0}:a]volume={g},adelay={ms}|{ms}[s{k}]'); mixes.append(f'[s{k}]')
    fc.append(f'{"".join(mixes)}amix=inputs={len(mixes)}:duration=first:normalize=0,atrim=0:{dur:.3f}[mx]')
    fc.append('[mx]loudnorm=I=-14:TP=-1.5:LRA=11[out]')
    script = os.path.join(wk, 'fc_audio.txt'); open(script, 'w', encoding='utf-8').write(';\n'.join(fc))
    fin = ['-map', '[out]', '-ar', '48000', '-ac', '2', os.path.join(P, out)]
    r = subprocess.run(['ffmpeg', '-y', '-v', 'error', *ins, '-/filter_complex', script, *fin], capture_output=True, text=True)
    if r.returncode: _run(['ffmpeg', '-y', '-v', 'error', *ins, '-filter_complex_script', script, *fin])      # ffmpeg anterior a la 7
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', os.path.join(P, out), '-af', 'volumedetect', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    mv = re.search(r'mean_volume: (\S+)', r).group(1); mx = re.search(r'max_volume: (\S+)', r).group(1)
    print(f'audio OK -> {out} | media {mv} dB, pico {mx} dB | efectos {len(sfx)} | música: {os.path.basename(mus) if mus else "no"}')


# =====================================================================================================
#  CAPTURAS REALES (para polaroids / tarjetas que muestran escenas del propio reel)
# =====================================================================================================
def capturas_provisionales(TH):
    """TH = [(segundo, y0)]. Crea assets/th1.jpg… (y una copia th1b.jpg…) con cuadros del crudo, provisionales, si aún no existen."""
    os.makedirs(os.path.join(P, 'assets'), exist_ok=True)
    for i, (t_, y0) in enumerate(TH):
        th = os.path.join(P, 'assets', f'th{i + 1}.jpg')
        if not os.path.exists(th):
            _run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{t_:.2f}', '-i', os.path.join(P, 'cut.mp4'), '-frames:v', '1',
                  '-vf', 'crop=880:1040:100:240,scale=440:520', th])
        shutil.copy(th, th[:-4] + 'b.jpg')          # copia con otro nombre: el mismo archivo no debe usarse en dos <img> (HyperFrames avisa)

def capturas_reales(TH):
    """reemplaza assets/thN.jpg por capturas de las escenas YA armadas (se usa con: python build.py --no-audio --thumbs)."""
    import glob
    from PIL import Image
    tmp = os.path.join(P, '_work', 'thumbs'); shutil.rmtree(tmp, ignore_errors=True)
    uniq = sorted(set(round(t_, 2) for t_, _ in TH))
    subprocess.run('npx hyperframes snapshot . --at ' + ','.join(str(u) for u in uniq) + ' --no-end --timeout 60000 -o _work/thumbs',
                   shell=True, cwd=P, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shots = {round(float(os.path.basename(g).split('-at-')[1][:-5]), 2): g for g in glob.glob(os.path.join(tmp, 'frame-*.png'))}
    for i, (t_, y0) in enumerate(TH):
        key = min(shots, key=lambda k: abs(k - t_))
        im = Image.open(shots[key]).convert('RGB').crop((0, y0, 1080, y0 + 1276)).resize((440, 520), Image.LANCZOS)
        im.save(os.path.join(P, 'assets', f'th{i + 1}.jpg'), quality=90)
        im.save(os.path.join(P, 'assets', f'th{i + 1}b.jpg'), quality=90)
    print('miniaturas actualizadas con las escenas reales:', len(TH))


# =====================================================================================================
#  INICIAR / CERRAR
# =====================================================================================================
def iniciar(proyecto, correcciones=None, semilla=1, colores=None):
    """Carga el proyecto preparado (cut.mp4, cutout.webm, words.json, face.json, cutmap.json). Llamar ANTES de `from motor import *`.
    correcciones : palabras que whisper oyó mal -> cómo se escriben, ej. {'cloud': 'Claude'}
    colores      : colores de marca, solo los que quieras cambiar:
                   {'acento': '#D11F1D', 'tinta': '#0D1216', 'fondo': '#E8E8E1', 'segundo': '#3354E4'}
                   acento = tarjeta, palabra activa de los subtítulos y CTA · tinta = titulares · fondo = fondo claro · segundo = 2º color de tarjeta
    semilla      : cambia el azar de las piezas (confeti, bordes de papel…)"""
    global P, DUR, CUT, WD, FACE, rnd, ESTADO, PAPEL, _n_caps, _n_grupos, RED, INK, OFF, BLUE
    for k, v in (colores or {}).items():
        if k == 'acento': RED = v
        elif k == 'tinta': INK = v
        elif k == 'fondo': OFF = v
        elif k == 'segundo': BLUE = v
        else: raise SystemExit(f"colores: no conozco '{k}' (usa acento, tinta, fondo, segundo)")
    P = os.path.abspath(proyecto)
    for need in ('cut.mp4', 'cutout.webm', 'words.json', 'face.json', 'cutmap.json'):
        if not os.path.exists(os.path.join(P, need)):
            raise SystemExit(f'Falta {need} en {P}. Corre primero scripts/preparar.py y scripts/recortar.py (ver SKILL.md).')
    CUT = json.load(open(os.path.join(P, 'cutmap.json'))); DUR = round(CUT['dur'], 3)
    WD = cargar_palabras(P, correcciones); FACE = Cara(P); rnd = random.Random(semilla)
    _encuadrar()
    for l in (init, tw, parts, sfx, caps): l.clear()
    ESTADO = 'card'; PAPEL = None; _n_caps = 0; _n_grupos = 0

def cerrar(musica=None, inicio_musica=0.0, volumen_musica=0.28, capturas=None, css_extra='', resumen=''):
    """Mezcla el audio, copia las fuentes y escribe index.html.  Banderas del build:  --no-audio  (no remezcla)  ·  --thumbs  (capturas reales)."""
    if DO_AUDIO or not os.path.exists(os.path.join(P, 'final_audio.wav')): mezclar_audio(DUR, musica, inicio_musica, volumen_musica)
    os.makedirs(os.path.join(P, 'fonts'), exist_ok=True)
    for _, _, fn in FONTS: shutil.copy(os.path.join(REC, 'fonts', fn + '.woff2'), os.path.join(P, 'fonts', fn + '.woff2'))
    css = ''.join(f'@font-face{{font-family:"{fam}";font-weight:{wt};font-display:block;src:url("fonts/{fn}.woff2") format("woff2");}}\n' for fam, wt, fn in FONTS)
    hoja = os.path.join(P, 'style.css')
    if not os.path.exists(hoja): hoja = os.path.join(SKILL, 'plantilla', 'style.css')
    css += open(hoja, encoding='utf-8').read() + css_extra
    for a, b in (('__W__', str(W)), ('__H__', str(H)), ('__RED__', RED), ('__INK__', INK), ('__OFF__', OFF), ('__BLUE__', BLUE), ('__TERRA__', TERRA),
                 ('__XRED__', XRED), ('__CX__', str(CARD_X)), ('__CY__', str(CARD_Y)), ('__CW__', str(CARD_W)), ('__PH__', str(PAPER_H)), ('__GR__', str(GROUND))):
        css = css.replace(a, b)
    doc = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
{css}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
{''.join(parts)}
{''.join(caps)}
<audio id="aud" data-start="0" data-duration="{DUR}" data-media-start="0" data-track-index="2" src="final_audio.wav" data-volume="1"></audio>
</div>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<script>const tl=gsap.timeline({{paused:true}});window.__timelines={{"main":tl}};
{chr(10).join(init)}
{chr(10).join(tw)}
</script></body></html>'''
    open(os.path.join(P, 'index.html'), 'w', encoding='utf-8').write(doc)
    print(f'OK index.html | {DUR}s | subtítulos {_n_caps} estados en {_n_grupos} grupos | efectos {len(sfx)}' + (f' | {resumen}' if resumen else ''))
    if capturas and '--thumbs' in sys.argv: capturas_reales(capturas)
