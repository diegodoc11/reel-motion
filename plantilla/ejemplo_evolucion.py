# -*- coding: utf-8 -*-
# EJEMPLO (no plantilla): reel "La evolución más importante de la IA" (35 s, estilo noche). Es el borrador que el usuario
# prefirió en una prueba a ciegas porque "explica visualmente lo que voy diciendo, palabra por palabra": órdenes escritas
# en la barra de mensaje de cada tarjeta con su palabra, tarjetas que vuelan al riel, tachado/check sincronizados, sin
# subtítulos cuando la cara llena la tarjeta. Léelo para copiar la FORMA de pensar cada frase; los f() son de ese guion.
# ------------------------------------------------------------------------------------------------------------------
# =====================================================================================================
#  reel-motion · ESTILO NOCHE · A-solo-evo (34.97 s)
#  "La evolución más importante de la IA no es que responda mejor, es que ya puede hacer cosas por ti…"
#  Plan escena por escena: _work/plan.md
#  Ojo: Diego dice cada orden ("respóndeme esto"…) en una toma pegada a la cámara (5 cortes duros, medidos sobre
#  el recorte cuadro a cuadro). En esos tramos la cara llena la tarjeta: SIN subtítulos (le taparían la barbilla);
#  la orden se escribe palabra por palabra en la barra de mensaje de la tarjeta de cada etapa.
# =====================================================================================================
import sys, os, re
P = os.path.dirname(os.path.abspath(__file__))
_sk = os.path.join(P, '_work', 'skill.txt')
SKILL = open(_sk, encoding='utf-8').read().strip() if os.path.exists(_sk) else os.path.expanduser('~/.claude/skills/reel-motion')
sys.path.insert(0, os.path.join(SKILL, 'scripts')); sys.path.insert(0, os.path.join(SKILL, 'plantilla')); sys.path.insert(0, P)
import motor
motor.iniciar(P, correcciones={'cloud': 'Claude', 'guía': 'IA', 'respóndame': 'respóndeme'}, colores={'acento': '#D11F1D'})
from motor import *
import noche as N
if '--guion' in sys.argv: guion(); sys.exit()

MUSICA = r'C:\Users\LAPTOP\Documents\Claude practicas\Editor Videos\_music\funk-amp-breakbeat-541097.mp3'

# Tomas pegadas a la cámara (cuadros 182-212, 260-301, 345-395, 428-472, 516-561 de cut.mp4 a 30 fps)
ACERCAMIENTOS = [(182, 212), (260, 301), (345, 395), (428, 472), (516, 561)]
HUECOS = [(a / 30 - 0.03, (b + 1) / 30) for a, b in ACERCAMIENTOS]

# ---------------- iconos propios (trazo 24x24, como los de noche.py) ----------------
N.ICONOS['enchufe'] = (24, '<path d="M9 2.6v4.6M15 2.6v4.6"/><path d="M5.8 7.2h12.4v3.4a6.2 6.2 0 0 1-12.4 0z"/><path d="M12 16.8v4.6"/>', False)
N.ICONOS['navegador'] = (24, '<rect x="2.6" y="4" width="18.8" height="16" rx="2.6"/><path d="M2.6 8.8h18.8"/>'
                              '<path d="M5.8 6.4h.1M8.4 6.4h.1M11 6.4h.1"/><path d="M10 11.8l6 2.3-2.6 1.1-1.1 2.6z"/>', False)
N.ICONOS['terminal'] = (24, '<rect x="2.6" y="4" width="18.8" height="16" rx="2.6"/><path d="M6.8 9.4l3 2.6-3 2.6"/><path d="M12.4 15.2h4.8"/>', False)
N.ICONOS['enviar'] = (24, '<path d="M12 19V5.6"/><path d="M5.9 11.6L12 5.4l6.1 6.2"/>', False)
N.ICONOS['mano'] = (24, '<path d="M7.6 15.2V6.4a1.4 1.4 0 0 1 2.8 0v4.8"/><path d="M10.4 11V4.4a1.4 1.4 0 0 1 2.8 0V11"/>'
                         '<path d="M13.2 11V5.6a1.4 1.4 0 0 1 2.8 0v5.8"/><path d="M16 11.6V8.4a1.4 1.4 0 0 1 2.8 0v5.4c0 4.4-2.9 7.8-7 7.8'
                         '-2.6 0-4.2-1.1-5.6-3l-2.7-3.7a1.4 1.4 0 0 1 2.2-1.7l1.9 2.4"/>', False)

AC = N.acento(); R_, G_, B_ = N._rgb(AC)
CSS = f'''
.netp .ncn span{{font-size:176px}}
.nett{{position:absolute;font-family:"IT";font-weight:900;letter-spacing:-.045em;line-height:1.05;color:#111318;white-space:nowrap}}
.nprm{{position:absolute;border-radius:30px;background:#15181D;box-shadow:inset 0 0 0 2px rgba(255,255,255,.06)}}
.nprm>*{{position:absolute}}
.nprl{{background-color:#F3F0E8;background-image:url(assets/ngrano-d.png);background-size:320px 320px;box-shadow:0 18px 40px rgba(0,0,0,.45)}}
.nprt{{left:36px;font-family:"Inter";font-weight:600;font-size:50px;line-height:60px;color:#F3F0E8;white-space:nowrap}}
.nprl .nprt{{color:#111318}}
.nprt .nw{{display:inline-block}}
.nprc{{left:34px;width:5px;height:46px;border-radius:3px;background:{AC};display:block}}
.nprs{{right:22px;width:76px;height:76px;border-radius:50%;background:rgba(255,255,255,.12);display:flex;align-items:center;justify-content:center}}
.nprs i{{position:absolute;left:0;top:0;width:76px;height:76px;border-radius:50%;background:{AC};display:flex;align-items:center;justify-content:center;box-shadow:0 8px 18px rgba({R_},{G_},{B_},.45)}}
.nqc{{position:absolute;border-radius:28px;background:#FBF8F0;border:2px solid rgba(22,24,28,.10);box-shadow:0 14px 30px rgba(0,0,0,.14)}}
.nqc>*{{position:absolute}}
.nqc.nqr{{background:{AC};border-color:{AC};box-shadow:0 20px 44px rgba({R_},{G_},{B_},.3)}}
.nqi{{left:26px;width:110px;height:110px;border-radius:50%;border:4px dashed rgba(22,24,28,.22)}}
.nqr .nqi{{border-color:rgba(255,255,255,.5)}}
.nqi i{{position:absolute;left:-4px;top:-4px;width:110px;height:110px;border-radius:50%;background:#16191E;display:flex;align-items:center;justify-content:center}}
.nqr .nqi i{{background:#fff}}
.nqt{{font-family:"IT";font-weight:800;letter-spacing:-.035em;line-height:1.08;color:#16181C;white-space:nowrap}}
.nqr .nqt{{color:#fff}}
'''

def palabras_ln(pid, palabras, cls=''):
    """palabras con máscara (span.ln > span.in) para que cada una SUBA cuando se dice."""
    return ' '.join(f'<span class="ln"><span class="in {cls}" id="{pid}{i}">{w}</span></span>' for i, (w, _) in enumerate(palabras))

def subir_palabras(pid, palabras, g=0.13):
    for i, (_, t) in enumerate(palabras): N.sube(f'#{pid}{i}', t - 0.03, 'pop' if i else 'swipe', g)

def cursor(sel, t_a, t_b):
    """cursor de la barra de mensaje: parpadea desde t_a y se apaga en t_b (cuando entra la primera palabra)."""
    I(sel, opacity=0)
    if t_b - t_a > 0.25:
        r = max(0, int((t_b - t_a) / 0.3) - 1)
        FT(sel, t_a, 0.3, {'opacity': 1}, {'opacity': 0.1, 'yoyo': True, 'repeat': r}, 'power1.inOut')
    S(sel, t_b, opacity=0)

# ---------------- riel de etapas (columna izquierda): cada casilla aparece cuando su tarjeta llega ----------------
ICO_ETAPA = ['chat', 'enchufe', 'navegador', 'documento', 'terminal']
SLOT_Y0, SLOT_DY = motor.CARD_Y + 25, 86

def slot_centro(n):
    return 83, SLOT_Y0 + (n - 1) * SLOT_DY + 36

def riel_etapas(t_fin):
    it = ''
    for i in range(1, 6):
        ic = ICO_ETAPA[i - 1]
        it += (f'<div class="nrt" id="rl-{i}" style="top:{SLOT_Y0 + (i - 1) * SLOT_DY}px">'
               f'<div class="nrd"><b>{i:02d}</b>{N.icono(ic, 40, N.PALETA["tinta_papel"], 2.0)}</div>'
               f'<div class="nrc" id="rl-c{i}"><b>{i:02d}</b>{N.icono(ic, 40, "#fff", 2.0)}</div></div>')
        I(f'#rl-{i}', opacity=0, scale=0.3); I(f'#rl-c{i}', opacity=0)
    motor.parts.append(f'<div class="nriel" id="rl">{it}</div>')
    T('#rl', t_fin - 0.22, 0.2, 'power2.in', opacity=0, x=-50)          # sale junto con el slam, antes del cambio a papel

def casilla(i, t, destello=True):
    T(f'#rl-{i}', t, 0.32, 'back.out(2.4)', opacity=1, scale=1); fx(t, 'pop', 0.16)
    if destello: FT(f'#rl-c{i}', t, 0.5, {'opacity': 1}, {'opacity': 0}, 'power1.in')

# ---------------- tarjeta de etapa (base: tarjeta_numerada de noche.py) + barra de mensaje ----------------
def etapa(idp, n, total, t_in, t_out, titulo, icono, comando, t_send):
    """titulo = [(palabra, t)] · comando = [[(palabra, t)…], [(palabra, t)…]] (1-2 renglones) · t_out = empieza a volar a su casilla."""
    N._id(idp); c = '#' + idp
    segw = int((354 - 6 * (total - 1)) / total)
    segs = ''.join(f'<i class="dn" style="width:{segw}px"></i>' if j < n - 1 else
                   (f'<i style="width:{segw}px"><b id="{idp}-sf"></b></i>' if j == n - 1 else f'<i style="width:{segw}px"></i>') for j in range(total))
    fs_t = N._cabe(' '.join(w for w, _ in titulo), 84, 860, 56, -0.045, quien=idp)
    k = 0; lns = []
    for ln_ in comando:
        ws = []
        for w, _ in ln_:
            ws.append(f'<span class="nw" id="{idp}-w{k}">{w}</span>'); k += 1
        lns.append(' '.join(ws))
        if N._ancho(' '.join(w for w, _ in ln_), 50, 0, 'int') > 690: print(f'  (aviso) {idp}: renglón largo en la barra')
    BH = 164; tt = round((BH - 60 * len(comando)) / 2) - 2
    barra = (f'<div class="nprm" id="{idp}-p" style="left:30px;top:290px;width:864px;height:{BH}px">'
             f'<i class="nprc" id="{idp}-k" style="top:{tt + 7}px"></i>'
             f'<div class="nprt" style="top:{tt}px">{"<br>".join(lns)}</div>'
             f'<div class="nprs" id="{idp}-s" style="top:{round((BH - 76) / 2)}px">{N.icono("enviar", 40, "rgba(255,255,255,.45)", 2.6)}'
             f'<i id="{idp}-sv">{N.icono("enviar", 40, "#fff", 2.6)}</i></div></div>')
    motor.parts.append(f'''<div class="ncard netp" id="{idp}">
  <div class="ncn"><span id="{idp}-ni">{n:02d}</span></div>
  <div class="ncl"><div class="ncli" id="{idp}-li">{N.icono(icono, 96, '#fff', 1.9)}</div></div>
  <div class="ncpg">{n}/{total}</div>
  <div class="ncsg">{segs}</div>
  <div class="nett" style="left:30px;top:176px;font-size:{fs_t}px">{palabras_ln(idp + '-t', titulo)}</div>
  {barra}
</div>''')
    # entrada con golpe
    if n == 1: I(c, opacity=0, y=80, scale=0.93); T(c, t_in, 0.55, 'expo.out', opacity=1, y=0, scale=1)
    else: I(c, opacity=0, x=170, scale=0.95); T(c, t_in, 0.5, 'expo.out', opacity=1, x=0, scale=1)   # entra por la derecha: la anterior se va a la izquierda
    fx(t_in, 'whoosh', 0.16)
    I(f'#{idp}-ni', opacity=0, scale=1.9); T(f'#{idp}-ni', t_in + 0.02, 0.5, 'expo.out', opacity=1, scale=1); fx(t_in + 0.02, 'thump', 0.26)
    I(f'#{idp}-sf', scaleX=0, transformOrigin='0% 50%'); T(f'#{idp}-sf', t_in, max(0.3, t_out - t_in), 'none', scaleX=1)
    # nombre de la etapa (palabra por palabra) + icono
    subir_palabras(idp + '-t', titulo, 0.15)
    ti = titulo[0][1] + 0.1
    I(f'#{idp}-li', opacity=0, scale=0.2); T(f'#{idp}-li', ti, 0.5, 'back.out(2.4)', opacity=1, scale=1); fx(ti, 'pop', 0.16)
    # la orden se escribe palabra por palabra en la barra
    t_w0 = comando[0][0][1]
    cursor(f'#{idp}-k', t_in + 0.4, t_w0 - 0.03)
    k = 0; ultimo = 0
    for ln_ in comando:
        for _, t in ln_:
            I(f'#{idp}-w{k}', opacity=0, y=14); T(f'#{idp}-w{k}', t - 0.03, 0.18, 'power2.out', opacity=1, y=0); fx(t - 0.03, 'click', 0.05)
            k += 1; ultimo = max(ultimo, t)
    I(f'#{idp}-sv', opacity=0, scale=0.3); T(f'#{idp}-sv', t_send, 0.26, 'back.out(2.6)', opacity=1, scale=1)
    FT(f'#{idp}-s', t_send, 0.3, {'scale': 1.25}, {'scale': 1}, 'back.out(2.6)'); fx(t_send, 'click', 0.2)
    # vuela a su casilla del riel (primero a la izquierda, luego baja: nunca cruza la cara)
    cx, cy = slot_centro(n)
    T(c, t_out, 0.24, 'power2.in', x=cx - 540, scale=0.145)
    T(c, t_out + 0.13, 0.24, 'power2.in', y=cy - 501)
    S(c, t_out + 0.38, opacity=0); fx(t_out, 'whoosh', 0.16)
    casilla(n, t_out + 0.36, destello=(n < total))
    N._aviso(idp, ultimo, t_out)

def barra_clara(pid, palabras, top, alto=132):
    """barra de mensaje crema (sobre la tinta) con su texto palabra por palabra, raya de tachado y ✗."""
    tt = round((alto - 60) / 2)
    ws = ' '.join(f'<span class="nw" id="{pid}-w{i}">{w}</span>' for i, (w, _) in enumerate(palabras))
    wt = N._ancho(' '.join(w for w, _ in palabras), 50, 0, 'int')
    return (f'<div class="nprm nprl" id="{pid}" style="left:78px;top:{top}px;width:924px;height:{alto}px">'
            f'<i class="nprc" id="{pid}-k" style="top:{tt + 7}px"></i>'
            f'<div class="nprt" style="top:{tt}px">{ws}</div>'
            f'<i class="nsbar" id="{pid}-s" style="left:22px;top:{tt + 28}px;width:{round(wt + 30)}px;background:{AC}"></i>'
            f'<div class="nko" id="{pid}-x" style="left:{924 - 26 - 84}px;top:{round((alto - 84) / 2)}px;width:84px;height:84px;border-color:{AC}">'
            f'{N._equis(pid + "-xx", 40, 40, 8, 3, "nsvok")}</div></div>')

def tarjeta_pregunta(pid, top, lineas, icono, t_icono, roja=False, t_ok=None, alto=176):
    """tarjeta con una pregunta de 2 renglones que sube palabra por palabra + icono en círculo que salta en su palabra."""
    todas = [p for ln_ in lineas for p in ln_]
    libre = 924 - 160 - (150 if t_ok is not None else 34)
    fs = min(N._cabe(' '.join(w for w, _ in ln_), 60, libre, 44, -0.035, 'it8', quien=pid) for ln_ in lineas)
    tt = round((alto - fs * 1.08 * len(lineas)) / 2)
    k = 0; rs = []
    for ln_ in lineas:
        rs.append(' '.join(f'<span class="ln"><span class="in" id="{pid}-w{k + i}">{w}</span></span>' for i, (w, _) in enumerate(ln_))); k += len(ln_)
    col = AC if roja else '#F3F0E8'
    ok = (f'<div class="nokc" id="{pid}-v" style="left:{924 - 34 - 110}px;top:{round((alto - 110) / 2)}px">'
          f'{N._svgp(pid + "-vv", N.CHECK_D, 64, 56, 10, "nsvok")}</div>') if t_ok is not None else ''
    h = (f'<div class="nqc{" nqr" if roja else ""}" id="{pid}" style="left:78px;top:{top}px;width:924px;height:{alto}px">'
         f'<div class="nqi" style="top:{round((alto - 110) / 2)}px"><i id="{pid}-i">{N.icono(icono, 64, col, 2.2)}</i></div>'
         f'<div class="nqt" style="left:160px;top:{tt}px;font-size:{fs}px">{"<br>".join(rs)}</div>{ok}</div>')
    def animar():
        N.entra(f'#{pid}', todas[0][1] - 0.06, 0.4, 'back.out(1.5)', y=60, escala=0.9, snd='whoosh', g=0.15)
        for i, (_, t) in enumerate(todas): N.sube(f'#{pid}-w{i}', t - 0.03, 'pop' if i else None, 0.12)
        I(f'#{pid}-i', opacity=0, scale=0.2); T(f'#{pid}-i', t_icono - 0.03, 0.4, 'back.out(2.6)', opacity=1, scale=1); fx(t_icono - 0.03, 'pop', 0.2)
        if t_ok is not None:
            N.entra(f'#{pid}-v', t_ok, 0.3, 'back.out(2.4)', y=0, escala=0.4, snd='ding', g=0.24); N.dibuja(f'#{pid}-vv', t_ok + 0.06, 0.18)
            FT(f'#{pid}', t_ok + 0.05, 0.3, {'scale': 1.03}, {'scale': 1}, 'power2.out')
    return h, animar

N.escenario()
N.tapar(162, 832, 84, 70, hasta=0.03)                # mancha del recorte SOLO en el cuadro 0 (x 114-220, y 844-889)

# ============================== ESCENAS ==============================
# 1 · GANCHO (card): "La evolución más importante de la IA no es que responda mejor, es que ya puede hacer cosas por ti."
t_c1 = f('Primero') - 0.03
N.gancho('La evolución más importante de la IA', hasta=t_c1, saltos=(2,), acento=(1,))
N._id('g2')
w_rm = N._ancho('Responde mejor', 64, -0.035, 'it8')
g2 = (f'<div class="nt64" style="left:78px;top:486px;color:#9EA3AB">{N.linea("g2-r", "Responde mejor")}</div>'
      f'<i class="nsbar" id="g2-s" style="left:68px;top:516px;width:{round(w_rm + 22)}px"></i>'
      f'<div class="nko" id="g2-x" style="left:{round(78 + w_rm + 36)}px;top:477px;width:84px;height:84px">{N._equis("g2-xx", 40, 40, 8, 3, "nsvac")}</div>'
      + N._caja_html('g2-c', 'HACE COSAS POR TI', 584))
N._bloque('g2', g2, 0, t_c1)
N.sube('#g2-r', f('responda') - 0.03, 'swipe', 0.15)
t_mj = f('mejor')
I('#g2-s', scaleX=0, transformOrigin='0% 50%'); T('#g2-s', t_mj - 0.02, 0.22, 'power2.out', scaleX=1); fx(t_mj - 0.02, 'swipe', 0.16)
N.entra('#g2-x', t_mj + 0.12, 0.3, 'back.out(2.4)', y=0, escala=0.4, snd='thump', g=0.22); N._dibuja_equis('g2-xx', t_mj + 0.16, 0, 0.08)
N.golpe('#g2-c', f('hacer') - 0.03, s0=1.6, r0=-7, r1=-1.5, g=0.32, sh=7); flash(f('hacer') - 0.01, 0.14)

# 2-6 · LAS 5 ETAPAS (card): tarjeta numerada + barra de mensaje; cada una vuela a su casilla del riel
t_spA = f('La IA', 19) - 0.06                       # entra el papel 1
riel_etapas(t_spA)
etapa('c1', 1, 5, t_c1, f('Después'), [('El', f('el chat')), ('chat', f('chat'))], 'chat',
      [[('Resp&oacute;ndeme', f('respóndeme')), ('esto', f('esto'))]], t_send=f('esto') + 0.22)
etapa('c2', 2, 5, f('Después') + 0.2, f('Después', 10) + 0.04, [('Conectores', f('conectores'))], 'enchufe',
      [[('Ve', f('ve y')), ('y', f('y busca')), ('busca', f('busca')), ('la', f('la información')), ('informaci&oacute;n', f('información'))],
       [('por', f('por mí')), ('m&iacute;', f('mí'))]], t_send=f('mí') + 0.2)
etapa('c3', 3, 5, f('Después', 10) + 0.24, f('Ahora') + 0.16, [('Claude', f('Claude')), ('en', f('en Chrome')), ('Chrome', f('Chrome'))], 'navegador',
      [[('Haz', f('haz esa')), ('esa', f('esa tarea')), ('tarea', f('tarea')), ('dentro', f('dentro'))],
       [('del', f('del navegador')), ('navegador', f('navegador')), ('web', f('web'))]], t_send=f('web') + 0.2)
etapa('c4', 4, 5, f('Ahora') + 0.36, f('luego') + 0.07, [('Cowork', f('Cowork'))], 'documento',
      [[('Hazme', f('hazme este')), ('este', f('este trabajo')), ('trabajo', f('trabajo'))],
       [('en', f('en un documento')), ('un', f('un documento')), ('documento', f('documento'))]], t_send=f('documento') + 0.2)
etapa('c5', 5, 5, f('luego') + 0.27, f('Te das') + 0.04, [('Claude', f('Claude Code')), ('Code', f('Code'))], 'terminal',
      [[('Hazme', f('hazme la')), ('la', f('la automatización')), ('automatizaci&oacute;n', f('automatización'))],
       [('que', f('que necesito')), ('necesito', f('necesito'))]], t_send=f('necesito') + 0.2)

# 7 · SLAM (card): "¿Te das cuenta de lo que está pasando?" + las 5 casillas del riel destellan en cadena
N.slam('s7', f('cuenta') - 0.03, '&iquest;TE DAS CUENTA?', t1=t_spA, acercar=1.06,
       sub=[('De responder a <span class="nac">hacer.</span>', f('lo que', 19))])
t_ch = f('de lo que') + 0.08
for i in range(1, 6): FT(f'#rl-c{i}', t_ch + (i - 1) * 0.06, 0.45, {'opacity': 1}, {'opacity': 0}, 'power1.in')
fx(t_ch, 'swipe', 0.14); fx(t_ch + 0.3, 'ding', 0.2)

# 8 · COMPARACIÓN en PAPEL (split, toma real): "La IA dejó de ser un lugar donde vas a hacer preguntas y ahora es la que hace el trabajo."
pp1 = N.papel('pp1')
N.a_split(t_spA, pp1)
N._id('k8')
tit8 = [('La', f('La IA', 19)), ('IA', f('IA', 20)), ('dej&oacute;', f('dejó')), ('de', f('de ser')), ('ser', f('ser', 20.5))]
malo = [('Un', f('un lugar')), ('lugar', f('lugar')), ('donde', f('donde')), ('preguntas', f('preguntas'))]
bueno = [('Hace', f('hace')), ('el', f('el trabajo')), ('trabajo', f('trabajo', 23.5))]
t_tacha8 = f('y ahora'); t_ahora = f('ahora', 22); t_ok8 = f('trabajo', 23.5) + 0.06
y1, h1, y2, h2 = 346, 168, 532, 200
f1 = N._cabe(' '.join(w for w, _ in malo), 80, 720, 44, -0.045, quien='k8'); w1 = N._ancho(' '.join(w for w, _ in malo), f1, -0.045)
f2 = N._cabe(' '.join(w for w, _ in bueno), 84, 720, 44, -0.045, quien='k8')
ty1 = round((h1 - f1 * 1.04) / 2); ty2 = round(62 + max(0, (h2 - 62 - f2) / 2))
k8 = (f'<div class="nt64" style="left:78px;top:264px">{palabras_ln("k8-h", tit8)}</div>'
      f'<div class="ncmp nmal" id="k8-a" style="left:78px;top:{y1}px;height:{h1}px">'
      f'<div class="ncmt" style="left:32px;top:{ty1}px;font-size:{f1}px">{palabras_ln("k8-m", malo)}</div>'
      f'<i class="nsbar" id="k8-s" style="left:22px;top:{round(ty1 + f1 * 0.5)}px;width:{round(min(720, w1) + 20)}px"></i>'
      f'<div class="nko" id="k8-x" style="left:780px;top:{round((h1 - 110) / 2)}px">{N._equis("k8-xx", 54, 54, 9, 4, "nsvac")}</div></div>'
      f'<div class="ncmp nbien" id="k8-b" style="left:78px;top:{y2}px;height:{h2}px">'
      f'<div class="ney" style="left:34px;top:20px">{typed("k8-eb", "AHORA", t_ahora + 0.02, 30, 0.03)}</div>'
      f'<div class="ncmt" style="left:32px;top:{ty2}px;font-size:{f2}px">{palabras_ln("k8-g", bueno)}</div>'
      f'<div class="nokc" id="k8-v" style="left:780px;top:{round((h2 - 110) / 2)}px">{N._svgp("k8-vv", N.CHECK_D, 64, 56, 10, "nsvok")}</div></div>')
N._bloque('k8', k8, t_spA, None, en=pp1)
subir_palabras('k8-h', tit8, 0.15)
N.entra('#k8-a', malo[0][1] - 0.06, 0.4, 'expo.out', y=60, snd='whoosh', g=0.14)
subir_palabras('k8-m', malo, 0.13)
I('#k8-s', scaleX=0, transformOrigin='0% 50%'); T('#k8-s', t_tacha8 - 0.02, 0.2, 'power2.out', scaleX=1); fx(t_tacha8 - 0.02, 'swipe', 0.16)
N.entra('#k8-x', t_tacha8 + 0.1, 0.3, 'back.out(2.4)', y=0, escala=0.4, snd='thump', g=0.24); N._dibuja_equis('k8-xx', t_tacha8 + 0.16, 0, 0.08)
T('#k8-a', t_tacha8 + 0.25, 0.3, 'power1.out', opacity=0.62)
N.entra('#k8-b', t_ahora - 0.03, 0.42, 'back.out(1.5)', y=70, snd='whoosh', g=0.16)
subir_palabras('k8-g', bueno, 0.15)
N.entra('#k8-v', t_ok8 - 0.03, 0.3, 'back.out(2.4)', y=0, escala=0.4, snd='ding', g=0.24); N.dibuja('#k8-vv', t_ok8 + 0.04, 0.18)
FT('#k8-b', t_ok8 + 0.05, 0.3, {'scale': 1.03}, {'scale': 1}, 'power2.out')

# 9 · LA PREGUNTA (card): "Por eso la pregunta más importante para tu negocio ya no es ¿qué prompt debo aprender?"
t_c9 = f('la pregunta') - 0.03
N.a_card(t_c9)
t_spB = f('sino') + 0.01                              # entra el papel 2
N._id('q9')
q9w = [('&iquest;Qu&eacute;', f('qué prompt')), ('prompt', f('prompt')), ('debo', f('debo')), ('aprender?', f('aprender', 27))]
q9 = (f'<div class="nt80" style="left:78px;top:284px">{N.linea("q9-l0", "La pregunta")}</div>'
      f'<div class="nt80" style="left:78px;top:372px">{N.linea("q9-l1", "m&aacute;s importante", "nac")}</div>'
      f'<div class="nt56" style="left:80px;top:470px">{N.linea("q9-l2", "para tu negocio", "ng2")}</div>'
      + barra_clara('q9-p', q9w, 566))
N._bloque('q9', q9, t_c9, t_spB + 0.1)
N.sube('#q9-l0', f('pregunta') - 0.03, 'swipe', 0.15)
N.sube('#q9-l1', f('más importante', 24) - 0.03, 'pop', 0.16)
N.sube('#q9-l2', f('para tu') - 0.03, 'pop', 0.14)
t_ya = f('ya no es') - 0.03
N.entra('#q9-p', t_ya, 0.4, 'back.out(1.6)', y=40, escala=0.9, snd='whoosh', g=0.16)
cursor('#q9-p-k', t_ya + 0.3, q9w[0][1] - 0.03)
for i, (_, t) in enumerate(q9w):
    I(f'#q9-p-w{i}', opacity=0, y=14); T(f'#q9-p-w{i}', t - 0.03, 0.18, 'power2.out', opacity=1, y=0); fx(t - 0.03, 'click', 0.05)
t_tacha9 = q9w[-1][1] + 0.15
I('#q9-p-s', scaleX=0, transformOrigin='0% 50%'); T('#q9-p-s', t_tacha9, 0.2, 'power2.out', scaleX=1); fx(t_tacha9, 'swipe', 0.16)
N.entra('#q9-p-x', t_tacha9 + 0.1, 0.3, 'back.out(2.4)', y=0, escala=0.4, snd='thump', g=0.26); N._dibuja_equis('q9-p-xx', t_tacha9 + 0.14, 0, 0.08)
N.sacude('#q9-p', t_tacha9 + 0.12, 7)
N._aviso('q9', t_tacha9 + 0.1, t_spB + 0.1)

# 10 · DOS PREGUNTAS en PAPEL (split, recorte sobre la tinta): "sino qué parte de mi negocio todavía depende de mis manos y qué puedo delegar en una IA."
pp2 = N.papel('pp2')
N.a_split(t_spB, pp2, recorte=True)
N._id('q10')
Q1 = [[('&iquest;Qu&eacute;', f('que parte')), ('parte', f('parte')), ('de', f('de mi negocio')), ('mi', f('mi negocio')), ('negocio', f('negocio', 29))],
      [('depende', f('depende')), ('de', f('de mis')), ('mis', f('mis')), ('manos?', f('manos'))]]
Q2 = [[('&iquest;Qu&eacute;', f('que puedo')), ('puedo', f('puedo')), ('delegar', f('delegar'))],
      [('en', f('en una')), ('una', f('una IA')), ('IA?', f('IA', 32.5))]]
hq1, anim_q1 = tarjeta_pregunta('q1', 352, Q1, 'mano', f('manos'))
hq2, anim_q2 = tarjeta_pregunta('q2', 548, Q2, 'bot', f('IA', 32.5), roja=True, t_ok=f('IA', 32.5) + 0.08)
N._bloque('q10', f'<div class="ncv" style="left:82px;top:262px;font-size:64px"><span id="q10-h">Sino:</span></div>' + hq1 + hq2, t_spB, None, en=pp2)
N.escribe('#q10-h', t_spB + 0.08, 0.5)
anim_q1(); anim_q2()

# 11 · CIERRE (card): "Y sígueme si quieres aprender a automatizar."
t_cta = f('Y sígueme') - 0.03
N.a_card(t_cta)
N.cta_sigueme('e11', t_cta, f('sígueme'), t_boton=f('sígueme') + 0.12, antetitulo='SI QUIERES APRENDER A', t_antetitulo=f('quieres') - 0.03,
              lineas=[('automatizar', f('automatizar'), 'ac')], usuario='@soydiegoosorio')
# ============================== fin de las escenas ==============================

subtitulos(desde=f('no es'), propios=('IA', 'Claude', 'Chrome', 'Cowork', 'Code'), huecos=HUECOS,
           cambios=[('sígueme', 'SÍGUEME', t_cta), ('que', 'qué', f('sino'))])
# en las tomas pegadas a la cámara no queda ningún subtítulo encendido (el que venía de antes se apaga en el corte)
_on = {}; _off = {}
for s_ in motor.tw:
    m_ = re.match(r'tl\.set\("#subt(\d+)",\{"opacity":\s*(\d)\},([\d.]+)\);', s_)
    if m_: (_on if m_.group(2) == '1' else _off)[int(m_.group(1))] = float(m_.group(3))
for k_, a_ in _on.items():
    for h0, _ in HUECOS:
        if a_ < h0 < _off.get(k_, motor.DUR): S(f'#subt{k_}', h0, opacity=0)

N.cerrar(musica=MUSICA, inicio_musica=69.75, volumen_musica=0.26, css_extra=CSS)
