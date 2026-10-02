# -*- coding: utf-8 -*-
# =====================================================================================================
#  reel-motion · PLANTILLA / EJEMPLO COMPLETO
#  Reel real de 59 s ("Estas animaciones que estás viendo en pantalla…", @soydiegoosorio). Todo el video es motion
#  graphics hecho con código; el presentador va RECORTADO sobre una tarjeta de color.
#
#  CÓMO ADAPTARLO A OTRO VIDEO
#    1. Deja igual el ENCABEZADO (hasta escenario()) y el CIERRE (subtitulos() + cerrar()).
#    2. Reescribe las ESCENAS: cada escena = una frase del guion. Para cada una decide el encuadre
#       ('card' recortado + titular · 'full' toma real + tarjeta flotante · 'split' papel arriba) y qué pieza la ilustra.
#    3. Los tiempos NUNCA se escriben a mano: salen de f('palabra o frase') -> segundo en que se dice.
#    4. Corre:  python build.py --no-audio   (rápido, sin remezclar)  ·  python build.py   (con audio)
#  Cada bloque de abajo es una RECETA reutilizable (están listadas en SKILL.md).
# =====================================================================================================
import sys, os, glob
P = os.path.dirname(os.path.abspath(__file__))
_sk = os.path.join(P, '_work', 'skill.txt')        # lo escribe preparar.py: dónde está instalada la skill
SKILL = open(_sk, encoding='utf-8').read().strip() if os.path.exists(_sk) else os.path.expanduser('~/.claude/skills/reel-motion')
sys.path.insert(0, os.path.join(SKILL, 'scripts')); sys.path.insert(0, P)
import motor
motor.iniciar(P, correcciones={'cloud': 'Claude'}, semilla=8597)      # correcciones: palabra mal oída por whisper -> correcta
from motor import *                                                    # (después de iniciar)
import minis as M                                                      # mini diseños CSS (collage, tarjetas de muestra)

escenario('card', codigo_fondo='\n'.join([M.CODE_TXT] * 7))

# =====================================================================================================
#  1 · GANCHO: el mismo titular en 5 estilos en 1.7 s  ("Estas animaciones que estás viendo en pantalla")
#      RECETA "gancho de estilos": cada palabra aparece cuando se dice; en cada cambio de palabra clave cambia
#      el fondo (#bgXX), el relleno de la tarjeta y el contorno del recorte (filter sobre #fx).
# =====================================================================================================
tB = f('animaciones') - 0.03; tC = f('que estás') - 0.03; tD = f('viendo') - 0.03; tE = f('pantalla') - 0.04; tF = f('fueron') - 0.03
HW = [('Estas', 0.0), ('animaciones', tB), ('que', tC), ('estás', f('estás') - 0.02), ('viendo', tD), ('en', f('en pantalla') - 0.02), ('pantalla', tE)]
STY = [('sz', '01 · suizo', 0.0, tB), ('bl', '02 · plano técnico', tB, tC), ('pa', '03 · acuarela', tC, tD),
       ('cd', '04 · código', tD, tE), ('pp', '05 · pop', tE, tF)]
for k, lab, a, b in STY:
    ws = ''
    for i, (wtxt, wt) in enumerate(HW):
        cls = 'ac' if wtxt in ('animaciones', 'pantalla') else ''
        ws += f'<span class="{cls}" id="hk{k}{i}">{wtxt}</span>' + ('<br>' if i in (1, 4) else ' ')
        if wt > a + 0.001: I(f'#hk{k}{i}', opacity=0); S(f'#hk{k}{i}', wt, opacity=1)
    parts.append(f'<div class="hk hk-{k}" id="hk{k}"><div class="tag">{cc()}<b>Claude Code</b></div><div class="lab">{lab}</div><div class="ttl">{ws}</div></div>')
    win(f'#hk{k}', a, b)
# fondos / relleno de la tarjeta / contorno del recorte por estilo
win('#bgbl', tB, tC); win('#bgpa', tC, tD); win('#bgcd', tD, tE); win('#bgpp', tE, tF)
S('#fillA', tB, opacity=0); S('#fillA', tF, opacity=1)
win('#brush', tC, tD); win('#fillC', tD, tE); win('#bpf', tB, tC); win('#cdf', tD, tE)
S('#fx', tB, filter='drop-shadow(0px 0px 16px rgba(150,195,255,0.95)) drop-shadow(0px 0px 3px rgba(215,232,255,0.9))')
S('#fx', tC, filter='none')
S('#fx', tD, filter='drop-shadow(0px 0px 22px rgba(232,137,79,0.6))')
S('#fx', tE, filter='drop-shadow(7px 0px 0px #fff) drop-shadow(-7px 0px 0px #fff) drop-shadow(0px 7px 0px #fff) drop-shadow(0px -7px 0px #fff)')
S('#fx', tF, filter='none')
for t_ in (tB, tC, tD, tE): fx(t_, 'swipe', 0.2)
flash(tF, 0.14); fx(tF, 'whoosh', 0.28)

# ---- 1b · RECETA "iconos tachados" -> "logo grande + titular"   ("fueron hechas con inteligencia artificial")
t_he = f('hechas'); t_ia = f('inteligencia'); t_art = f('artificial'); t_no = f('No tuve')
tiles = ''
TL0 = tF + 0.01; TX0 = t_he + 0.04; TSTEP = 0.05; XSTEP = 0.1
for i, (lab, bgc, fgc, glyph) in enumerate(M.TOOLS):
    tiles += (f'<div class="tool" id="tool{i}"><div class="ti" style="background:{bgc};color:{fgc}"><svg viewBox="0 0 24 24">{glyph}</svg></div>'
              f'<small>{lab}</small><span class="tx" id="toolx{i}">{X_SVG}</span></div>')
    pop(f'#tool{i}', TL0 + i * TSTEP, sc=0.3, dur=0.22, ease='back.out(2.4)', snd='pop' if i % 2 == 0 else None, g=0.13)
    draw_x(f'#toolx{i}', TX0 + i * XSTEP, 0.2)
parts.append(f"""<div class="hd" id="h1a">
  <div class="tag" style="left:78px;top:246px">{cc()}<b>Claude Code</b></div>
  <div class="eb" style="left:78px;top:318px">{typed('h1ae', 'NO NECESITÉ NADA DE ESTO', tF + 0.02, 70, 0)}</div>
  <div class="tools" id="tools" style="left:78px;top:372px">{tiles}<i class="mk" id="mk"><i></i></i></div>
</div>""")
win('#h1a', tF)
I('#mk', opacity=0, x=78, y=-34); S('#mk', TX0 - 0.03, opacity=1)
for i in range(len(M.TOOLS)):
    T('#mk', TX0 + i * XSTEP, 0.05, 'power1.out', x=i * 158 + 78, y=52)
    T('#mk', TX0 + i * XSTEP + 0.055, 0.035, 'power1.in', y=-34)
S('#mk', TX0 + len(M.TOOLS) * XSTEP + 0.16, opacity=0)
TLOGO = t_ia + 0.26
T('#h1a', TLOGO - 0.14, 0.16, 'power2.in', x=-1100, opacity=0); fx(TLOGO - 0.14, 'swipe', 0.2)
parts.append(f"""<div class="hd" id="h1b">
  <div class="blg" id="blg"><i class="ring" id="ring"></i>{cc('big')}<b>Claude Code</b></div>
  <div class="h1" style="left:74px;top:462px"><span class="ln"><span class="in" id="h1ba">Hechas con&nbsp;</span></span><span class="ln"><span class="in red" id="h1bb">IA.</span></span></div>
</div>""")
win('#h1b', TLOGO); I('#blg', scale=0.5, opacity=0, transformOrigin='0% 50%'); T('#blg', TLOGO, 0.3, 'back.out(1.8)', scale=1, opacity=1); fx(TLOGO, 'pop', 0.24)
I('#ring', opacity=0, scale=0.7)
FT('#ring', TLOGO + 0.06, 0.6, {'opacity': 0.9, 'scale': 0.7}, {'opacity': 0, 'scale': 2.7}, 'power2.out')
rise('#h1ba', TLOGO + 0.12, 0.26); rise('#h1bb', t_art + 0.04, 0.26); fx(t_art + 0.04, 'ding', 0.22)
leave('#h1b', t_no - 0.06)

# =====================================================================================================
#  2 · RECETA "terminal con filas y total"   ("No tuve que pagar un peso para generarlas")
#      Va en el encuadre 'card', en la zona de titulares (y 262-702). Cada fila entra al decirse su palabra.
# =====================================================================================================
t_pg = f('pagar'); t_ps = f('peso'); t_pa = f('para generarlas'); t_ge = f('generarlas'); t_so = f('Solo')
T1 = t_no - 0.1
parts.append(f'''<div class="term" id="t1" style="left:78px;top:262px;width:924px;height:440px">
  <div class="tbar"><i></i><i></i><i></i><span>costo.sh</span><em>en vivo</em></div>
  <div class="tb">
    <div class="tl"><span class="pr">&#10095;</span>{typed('t1a', 'claude', T1 + 0.2, 34, 0.08, 'or')}{typed('t1b', ' --costo', T1 + 0.2 + 6 / 34, 34, 0.08)}</div>
    <div class="row" id="t1r1"><span>editor de video</span><i></i><b>$0</b></div>
    <div class="row" id="t1r2"><span>animador</span><i></i><b>$0</b></div>
    <div class="dv" id="t1d"></div>
    <div class="tot"><span id="t1t">total</span><b id="t1z">$0</b></div>
  </div></div>''')
I('#t1', opacity=0, scale=0.9, y=-46); T('#t1', T1, 0.3, 'power3.out', opacity=1, scale=1, y=0); fx(T1, 'whoosh', 0.22)
for el, t_ in (('#t1r1', t_pg), ('#t1r2', t_ps)):
    I(el, opacity=0, x=-18); T(el, t_, 0.2, 'power2.out', opacity=1, x=0); fx(t_, 'pop', 0.14)
I('#t1d', scaleX=0, transformOrigin='0% 50%'); T('#t1d', t_pa, 0.25, 'power2.out', scaleX=1)
I('#t1t', opacity=0); S('#t1t', t_pa + 0.05, opacity=1)
pop('#t1z', t_ge, sc=0.2, dur=0.34, ease='back.out(2.6)', snd='ding', g=0.28)
T('#t1', t_so - 0.24, 0.14, 'power2.in', opacity=0, scale=0.94)

# =====================================================================================================
#  3 · TOMA COMPLETA + RECETA "terminal flotante con cronómetro" + RECETA "collage"
#      ("Solo le di una instrucción a Claude Code… y en menos de 5 minutos ya tenía todas estas animaciones")
# =====================================================================================================
X1 = t_so - 0.2
ir_a('full', X1)                                    # tarjeta -> pantalla completa
t_in = f('instrucción'); t_cl = f('Claude Code'); t_mo = f('modelo'); t_op = f('Opus'); t_en = f('en menos'); t_ya = f('ya tenía'); t_te = f('tenía')
t_yn = f('Y no,'); T2Y = bajo_barbilla(X1, t_yn)   # la tarjeta flotante empieza debajo de la barbilla
tvals = ['00:%02d' % s for s in (0, 3, 8, 15, 24, 35, 48)] + ['01:04', '01:25', '01:49', '02:16', '02:49', '03:20', '03:58', '04:21', '04:37', '04:48', '04:54', '04:58', '04:59']
TM0, TM1 = t_en + 0.05, t_ya - 0.08
parts.append(f'''<div class="term t2" id="t2" style="left:72px;top:{T2Y}px;width:936px;height:326px">
  <div class="tbar"><i></i><i></i><i></i><span>claude code</span><em>en vivo</em></div>
  <div class="tb">
    <div class="tl"><span class="pr">&#10095;</span>{typed('t2a', '1 instrucción', f('una instrucción') - 0.02, 26, 0.08)}<span class="ent" id="t2e">&nbsp;&#8629;</span></div>
    <div class="tl2"><span class="or" id="t2c"><i class="ast">{LOGO}</i>Claude Code</span><span class="gr" id="t2m">&nbsp;&nbsp;&middot;&nbsp;modelo&nbsp;</span><span class="cr" id="t2o">Opus 5.5</span></div>
    <div class="tim" id="t2t"><u>&#9684;</u><span class="tn">{steps('t2n', tvals, TM0, TM1)}</span><i class="bar"><i id="t2bar"></i></i></div>
    <div class="tl3"><span id="t2ok">&#10003;&nbsp; animaciones listas</span><em id="t2lt">menos de 5 min</em></div>
  </div></div>''')
I('#t2', opacity=0, y=40, scale=0.96); T('#t2', X1 + 0.3, 0.28, 'power3.out', opacity=1, y=0, scale=1)
I('#t2e', opacity=0); S('#t2e', t_in + 0.5, opacity=1)
for el, t_ in (('#t2c', t_cl), ('#t2m', t_mo), ('#t2o', t_op)):
    I(el, opacity=0); T(el, t_, 0.14, 'power1.out', opacity=1)
fx(t_cl, 'pop', 0.16); fx(t_op, 'pop', 0.16)
I('#t2t', opacity=0); S('#t2t', TM0 - 0.02, opacity=1); I('#t2lt', opacity=0); S('#t2lt', TM0 - 0.02, opacity=1)
I('#t2bar', scaleX=0, transformOrigin='0% 50%'); T('#t2bar', TM0, TM1 - TM0, 'power1.in', scaleX=1)
for i in range(9): fx(TM0 + i * (TM1 - TM0) / 9, 'click', 0.06)
I('#t2ok', opacity=0); T('#t2ok', t_ya, 0.12, 'power1.out', opacity=1); fx(t_ya, 'ding', 0.26)

# collage: 16 mini diseños saltan a su sitio ALREDEDOR de la cara (ninguno la pisa: ventana libre x 300-820, y 400-1060)
MS = mascot('mc')
COL = [  # (pieza, centro x, centro y, ancho final, rotación) — en orden de aparición
    (M.pct(), 952, 958, 232, -2), (M.est(), 152, 902, 292, -2), (M.dos(), 950, 640, 212, 3), (M.syn(), 140, 650, 250, 2),
    (M.cst(), 955, 262, 240, -2), (M.vid(), 158, 408, 300, -3), (M.dia(), 745, 150, 215, 4), (M.den(), 500, 168, 236, 2),
    (M.ofe(), 200, 122, 400, -3), (M.zas(), 952, 1512, 196, 3), (M.pla(), 136, 1500, 208, -2), (M.hia(), 800, 1722, 300, 3),
    (M.neg(), 438, 1668, 330, 2), (M.acu(MS), 128, 1730, 236, -3), (M.con(), 962, 1822, 190, 4), (M.app(), 500, 1858, 360, -1)]
c_html = ''
C0 = t_ya + 0.04; C_STEP = 0.05
ZC = zona_cara(t_ya, t_yn, 30)                    # con otro presentador la cara está en otro sitio: las piezas se corren solas
for i, ((h_, bw, bh), cx, cy, fw, rot) in enumerate(COL):
    sc = fw / bw
    cx, cy = esquivar_cara(cx, cy, fw, bh * sc, ZC)
    c_html += f'<div class="cl" id="cl{i}" style="left:{cx - bw / 2:.0f}px;top:{cy - bh / 2:.0f}px;width:{bw}px;height:{bh}px">{h_}</div>'
    # nace pequeña, un poco hacia el centro (sin entrar a la zona de la cara), y salta a su sitio
    I(f'#cl{i}', opacity=0, x=round((540 - cx) * 0.22), y=round((760 - cy) * 0.22), scale=sc * 0.15, rotation=rot + rnd.choice([-1, 1]) * rnd.uniform(25, 60))
    S(f'#cl{i}', C0 + i * C_STEP, opacity=1)
    T(f'#cl{i}', C0 + i * C_STEP, 0.36, 'back.out(1.5)', x=0, y=0, scale=sc, rotation=rot)
    if i % 2 == 0: fx(C0 + i * C_STEP, 'pop', 0.13)
parts.append(f'<div id="col">{c_html}</div>')
fx(C0, 'whoosh', 0.3)
mascot_init('mc', 'h')

# =====================================================================================================
#  4 · RECETA "papel": titular serif escrito a mano + palabras tachadas + polaroids + mascota + confeti
#      ("Y no, yo no sé de diseño ni de animación y aun así pude lograr este tipo de resultados")
# =====================================================================================================
X2 = t_yn - 0.1                                    # completa -> papel
for i in range(len(COL)): T(f'#cl{i}', X2 - 0.2 + (i % 4) * 0.012, 0.15, 'power2.in', scale=0, opacity=0)
fx(X2 - 0.2, 'swipe', 0.2); S('#col', X2, opacity=0); T('#t2', X2 - 0.12, 0.12, 'power1.in', opacity=0)
t_dis = f('diseño'); t_ani = f('animación'); t_pu = f('pude'); t_lo = f('lograr'); t_es = f('este tipo'); t_re = f('resultados'); t_pd = f('Puedo')
conf = ''
for i in range(22):
    col_ = rnd.choice(['#D11F1D', '#14161d', '#CB8473', '#F2B83B', '#D11F1D', '#14161d'])
    sz = rnd.choice([10, 12, 14, 18, 22])
    conf += f'<i class="cf" id="cf{i}" style="width:{sz}px;height:{sz}px;background:{col_}"></i>'
    ang_x = rnd.uniform(-760, 130); ang_y = rnd.uniform(-560, -90)
    I(f'#cf{i}', opacity=0, x=0, y=0)
    FT(f'#cf{i}', t_re + rnd.uniform(0, 0.12), 0.75, {'opacity': 1, 'x': 0, 'y': 0, 'scale': 1}, {'x': ang_x, 'y': ang_y, 'scale': 0.6}, 'power3.out')
    T(f'#cf{i}', t_re + 0.6, 0.3, 'power1.in', opacity=0)
pol4 = ''
for i, (x_, y_, r_) in enumerate([(74, 402, -4), (308, 410, 2.5), (542, 404, -2)]):
    pol4 += f'<div class="pol" id="p4{i}" style="left:{x_}px;top:{y_}px"><i class="tape"></i><div class="ph"><img src="assets/th{i + 1}.jpg"></div></div>'
    t_ = (t_pu, t_lo, t_es)[i]
    I(f'#p4{i}', opacity=0, y=-70, rotation=r_ + 14, scale=1.15); T(f'#p4{i}', t_, 0.32, 'back.out(1.6)', opacity=1, y=0, rotation=r_, scale=1); fx(t_, 'pop', 0.2)
parts.append(f'''<div class="paper" id="pp1">{paper_svg(21)}<i class="gline"></i>
  <div class="ser" style="left:80px;top:218px">{serif('s4h', 'No soy dise&ntilde;ador.')}</div>
  <div class="hw" style="left:98px;top:326px"><span id="s4a">dise&ntilde;o</span><span id="s4ax">{X_SVG}</span></div>
  <div class="hw" style="left:356px;top:326px"><span id="s4b">animaci&oacute;n</span><span id="s4bx">{X_SVG}</span></div>
  {pol4}
  <div class="msc" id="ms1" style="left:836px;top:{GROUND - 126}px">{mascot('m1')}</div>
  <div id="cfs" style="left:900px;top:{GROUND - 100}px">{conf}</div>
</div>''')
ir_a('split', X2, papel='#pp1')
handwrite('#s4h', f('yo no sé') - 0.12, 0.46, pen='#s4hp')
handwrite('#s4a', t_dis - 0.1, 0.2, 0); draw_x('#s4ax', t_dis + 0.12)
handwrite('#s4b', t_ani - 0.1, 0.24, 0); draw_x('#s4bx', t_ani + 0.16)
mascot_init('m1', 'n')
for t_ in (t_dis + 0.3, t_ani + 0.4): FT('#ms1', t_, 0.12, {'y': 0}, {'y': -8, 'yoyo': True, 'repeat': 1}, 'power1.out')
mood('m1', t_re, 'h'); FT('#ms1', t_re, 0.2, {'y': 0}, {'y': -46, 'yoyo': True, 'repeat': 1}, 'power2.out'); fx(t_re, 'ding', 0.26)

# =====================================================================================================
#  5 · RECETA "cambio de estilo en vivo" + RECETA "abanico de fotos"
#      ("Puedo cambiar los colores, la tipografía, agregar mis imágenes, el diseño, lo que yo quiera")
# =====================================================================================================
X3 = t_pd - 0.2
ir_a('card', X3)                                    # papel -> tarjeta
t_col = f('colores'); t_tip = f('tipografía'); t_img = f('imágenes'); t_ds2 = f('diseño', t_img); t_qui = f('quiera'); t_dg = f('Diego')
# Fotos REALES del presentador al decir "agregar mis imágenes": assets/foto-<nombre>.jpg (600x620; créalas con scripts/foto.py).
# El abanico se acomoda solo según cuántas sean (1 a 4). Si no hay fotos, usa las capturas del propio reel.
PHOTOS = [a.split('=')[1] for a in sys.argv if a.startswith('--fotos=')]
PHOTOS = PHOTOS[0].split(',') if PHOTOS else [os.path.basename(g)[5:-4] for g in sorted(glob.glob(os.path.join(P, 'assets', 'foto-*.jpg')))][:4]
IMGS = [f'assets/foto-{k}.jpg' for k in PHOTOS] or ['assets/th1b.jpg', 'assets/th3b.jpg']      # sin fotos: capturas del propio reel
LAY = {1: (300, [(724, 300, 4)]),
       2: (222, [(690, 190, -6), (838, 452, 5)]),
       3: (232, [(640, 188, -7), (838, 212, 6), (786, 498, -4)]),
       4: (196, [(650, 188, -6), (858, 204, 5), (700, 440, 4), (866, 466, -5)])}
pw_, slots = LAY[len(IMGS)]
pol5 = ''
for i, (src_, (x_, y_, r_)) in enumerate(zip(IMGS, slots)):
    ps_ = pw_ - 20; ph_ = round(ps_ * 620 / 600)
    pol5 += (f'<div class="pol lf" id="p5{i}" style="left:{x_}px;top:{y_}px;width:{pw_}px;height:{10 + ph_ + round(pw_ * .2)}px"><i class="tape"></i>'
             f'<div class="ph" style="height:{ph_}px"><img src="{src_}"></div></div>')
    I(f'#p5{i}', opacity=0, scale=0.3, rotation=r_ - 20); T(f'#p5{i}', t_img + i * 0.16, 0.32, 'back.out(1.8)', opacity=1, scale=1, rotation=r_); fx(t_img + i * 0.16, 'pop', 0.2)
chips = ''.join(f'<span class="chip" id="ch{i}">{c}</span>' for i, c in enumerate(['COLORES', 'TIPOGRAF&Iacute;A', 'IM&Aacute;GENES', 'DISE&Ntilde;O']))
parts.append(f'''<div class="hd" id="h5">
  <div class="eb" style="left:78px;top:282px">{typed('h5e', 'Y LO CAMBIAS TODO', t_pd - 0.02, 40, 0)}</div>
  <div class="h1" id="h5s" style="left:74px;top:334px"><div class="ln"><span class="in" id="h5a">Tu video,</span></div>
    <div class="ln"><span class="in" id="h5b"><span class="red" id="h5r">tu estilo.</span><span class="blu ov" id="h5u">tu estilo.</span></span></div></div>
  <div class="hser" id="h5f" style="left:76px;top:330px"><span class="dk" id="h5fd">Tu video,</span><span class="lt ov" id="h5fl">Tu video,</span><br><span class="blu" id="h5fb">tu estilo.</span><span class="red ov2" id="h5fr">tu estilo.</span></div>
  <div class="chips" style="left:78px;top:624px">{chips}</div>
  {pol5}
</div>''')
win('#h5', X3 + 0.1); rise('#h5a', t_pd + 0.02); rise('#h5b', f('cambiar') - 0.02)
I('#h5u', opacity=0); I('#h5f', opacity=0); I('#h5fl', opacity=0); I('#h5fr', opacity=0)
# colores: la tarjeta pasa de rojo a azul (barrido de abajo hacia arriba)
T('#fillB', t_col - 0.03, 0.3, 'power2.inOut', clipPath='inset(0% 0% 0% 0%)'); S('#h5u', t_col + 0.1, opacity=1); S('#h5r', t_col + 0.1, opacity=0); fx(t_col - 0.03, 'swipe', 0.26)
# tipografía: el titular cambia a serif itálica
T('#h5s', t_tip - 0.02, 0.1, 'power1.in', opacity=0); T('#h5f', t_tip + 0.04, 0.14, 'power1.out', opacity=1); fx(t_tip, 'pop', 0.2)
# diseño: fondo oscuro
T('#bgdk', t_ds2 - 0.02, 0.22, 'power1.out', opacity=1); S('#h5fl', t_ds2 + 0.06, opacity=1); S('#h5fd', t_ds2 + 0.06, opacity=0); fx(t_ds2, 'thump', 0.26)
for i, t_ in enumerate((t_col, t_tip, t_img, t_ds2)):
    I(f'#ch{i}', opacity=0, scale=0.6); T(f'#ch{i}', t_ + 0.05, 0.2, 'back.out(2)', opacity=1, scale=1)
# "lo que yo quiera": vuelve el rojo
T('#fillB', t_qui - 0.04, 0.28, 'power2.inOut', clipPath='inset(0% 0% 100% 0%)'); S('#h5fr', t_qui + 0.1, opacity=1); S('#h5fb', t_qui + 0.1, opacity=0); fx(t_qui - 0.04, 'swipe', 0.22)

# =====================================================================================================
#  6 · RECETA "papel con pila de monedas" (objeción + respuesta)
#      ("Diego, pero esto me va a salir carísimo… Bueno, no… Opus 5.5… relativamente barato…")
# =====================================================================================================
X4 = t_dg - 0.14                                   # tarjeta -> papel
leave('#h5', X4 + 0.04, 0.14); S('#bgdk', X4, opacity=0)
t_car = f('carísimo'); t_con = f('consumir'); t_muc = f('muchísimos'); t_tok = f('tokens'); t_bno = f('no,', t_tok); t_op2 = f('Opus', t_tok)
t_55 = f('5.5', t_tok); t_bar = f('barato'); t_mej = f('mejores'); t_yo = f('Yo llevo')
coins = ''
def coin(cid, x_, k, t_):
    global coins
    y_ = GROUND - 46 - k * 24
    coins += f'<div class="coin" id="{cid}" style="left:{x_}px;top:{y_}px"><i></i><b>T</b></div>'
    I(f'#{cid}', opacity=0, y=-(260 + k * 16)); S(f'#{cid}', t_, opacity=1); T(f'#{cid}', t_, 0.26, 'bounce.out', y=0)
    fx(t_ + 0.1, 'click', 0.12)
for g_, (x_, t_) in enumerate([(106, t_con + 0.5), (350, t_con + 0.7)]): coin(f'cg{g_}', x_, 0, t_)      # sueltas en el piso
for k in range(10): coin(f'cs{k}', 228 + rnd.choice([-7, -3, 0, 4, 8]), k, t_con + k * 0.125)             # la pila alta
coin('cg2', 456, 0, t_con + 1.1)
coin('co0', 600, 0, t_op2 - 0.02); coin('co1', 604, 1, t_op2 + 0.12)                                       # pila chiquita (Opus 5.5)
parts.append(f'''<div class="paper" id="pp2">{paper_svg(37)}<i class="gline"></i>
  <div class="ser" style="left:80px;top:218px">{serif('s6h', '&iquest;Car&iacute;simo?')}<span class="bigx" id="s6x">{X_SVG}</span></div>
  <div class="hw red2" style="left:104px;top:392px"><span id="s6l">much&iacute;simos tokens</span></div>
  <div class="hw gry" style="left:150px;top:392px"><span id="s6l2">modelos top</span></div>
  {coins}
  <div class="ser sm" id="s6o" style="left:548px;top:{GROUND - 204}px">Opus 5.5<svg class="ul" viewBox="0 0 200 16"><path id="s6u" d="M4 9 Q50 2 100 8 T196 7"/></svg></div>
  <div class="hw grn" style="left:566px;top:{GROUND - 286}px"><span id="s6b">barato &#10003;</span></div>
  <div class="msc" id="ms2" style="left:836px;top:{GROUND - 126}px">{mascot('m2')}</div>
</div>''')
ir_a('split', X4, papel='#pp2')
handwrite('#s6h', t_car - 0.08, 0.44, pen='#s6hp')
handwrite('#s6l', t_muc - 0.05, 0.5, 0)
mascot_init('m2', 'n'); mood('m2', t_con + 0.9, 'w')
FT('#ms2', t_con + 0.9, 0.07, {'x': 0}, {'x': 7, 'yoyo': True, 'repeat': 5}, 'none')
draw_x('#s6x', t_bno - 0.04, 0.36); mood('m2', t_bno + 0.3, 'n')
I('#s6o', opacity=0, scale=0.5); T('#s6o', t_op2, 0.28, 'back.out(2)', opacity=1, scale=1); fx(t_op2, 'pop', 0.2)
mood('m2', t_55, 'h'); FT('#ms2', t_55, 0.18, {'y': 0}, {'y': -38, 'yoyo': True, 'repeat': 1}, 'power2.out'); fx(t_55, 'ding', 0.24)
I('#s6u', strokeDasharray=200, strokeDashoffset=200); T('#s6u', t_bar - 0.05, 0.28, 'power1.out', strokeDashoffset=0)
handwrite('#s6b', t_bar, 0.3, 0.14)
I('#s6l2', opacity=0); T('#s6l', t_mej - 0.05, 0.14, 'power1.in', opacity=0); T('#s6l2', t_mej + 0.06, 0.16, 'power1.out', opacity=1)

# =====================================================================================================
#  7 · RECETAS de DATOS sobre la tarjeta: "número gigante", "barra de 24 h", "titular de 2 líneas", "0% -> N% con cuadrícula"
#      ("Yo llevo más de una semana usándolo literal todo el día y no se me ha acabado el uso. De hecho… 3% de mi uso")
# =====================================================================================================
X5 = t_yo - 0.2
ir_a('card', X5)                                    # papel -> tarjeta
t_una = f('una semana'); t_sem = f('semana'); t_usa = f('usándolo'); t_lit = f('literal'); t_tod = f('todo el'); t_dia = f('día')
t_yns = f('Y no se'); t_aca = f('acabado'); t_dh = f('De hecho'); t_an2 = f('animaciones', t_dh); t_cmp = f('complejas'); t_csm = f('consumió')
t_3 = f('3%'); t_mi = f('mi uso'); t_ab = f('Ahora bien')
# 7a: número gigante (+7 días de uso)
parts.append(f'''<div class="hd" id="h7a">
  <div class="eb" style="left:78px;top:282px">{typed('h7ae', 'MÁS DE UNA SEMANA · OPUS 5.5', t_yo + 0.02, 44, 0)}</div>
  <div class="nmask" style="left:60px;top:330px;width:560px;height:420px"><div class="big7" id="h7n"><u>+</u>7</div></div>
  <div class="h1" style="left:560px;top:400px"><div class="ln"><span class="in" id="h7d">d&iacute;as</span></div></div>
  <div class="h2" style="left:566px;top:540px"><div class="ln"><span class="in" id="h7u">de uso</span></div></div>
</div>''')
win('#h7a', X5 + 0.1); I('#h7n', yPercent=105); T('#h7n', t_una - 0.08, 0.42, 'power3.out', yPercent=0); fx(t_una - 0.08, 'thump', 0.3)
rise('#h7d', t_sem - 0.02, 0.3); rise('#h7u', t_usa - 0.02, 0.3)
leave('#h7a', t_lit - 0.03)
# 7b: titular + barra que se llena (literal todo el día)
ticks = ''.join(f'<b style="left:{i * 25}%">{h_}</b>' for i, h_ in enumerate(['00', '06', '12', '18', '24']))
parts.append(f'''<div class="hd" id="h7b">
  <div class="eb" style="left:78px;top:282px">LITERAL</div>
  <div class="h1" style="left:74px;top:350px"><div class="ln"><span class="in" id="h7t">Todo el d&iacute;a.</span></div></div>
  <div class="hbar" style="left:78px;top:548px"><i id="h7f"></i><div class="tk">{ticks}</div></div>
</div>''')
win('#h7b', t_lit - 0.02); rise('#h7t', t_tod - 0.04)
I('#h7f', scaleX=0, transformOrigin='0% 50%'); T('#h7f', t_tod, max(0.5, t_yns - t_tod - 0.08), 'power1.inOut', scaleX=0.96); fx(t_tod, 'swipe', 0.2)
leave('#h7b', t_yns - 0.02)
# 7c: titular de 2 líneas (la segunda en rojo)
parts.append('''<div class="hd" id="h7c">
  <div class="eb" style="left:78px;top:282px">L&Iacute;MITE DE USO</div>
  <div class="h1" style="left:74px;top:340px"><div class="ln"><span class="in" id="h7y">Y no se</span></div><div class="ln"><span class="in red" id="h7z">acab&oacute;.</span></div></div>
</div>''')
win('#h7c', t_yns - 0.01); rise('#h7y', t_yns + 0.02); rise('#h7z', t_aca - 0.03); fx(t_aca - 0.03, 'pop', 0.2)
leave('#h7c', t_dh - 0.02)
# 7d: antetítulo + titular
parts.append(f'''<div class="hd" id="h7d2">
  <div class="eb dk" style="left:78px;top:282px">{typed('h7de', 'LA MÁS PESADA QUE HE HECHO', t_dh + 0.02, 40, 0)}</div>
  <div class="h1" id="h7dh" style="left:74px;top:340px"><div class="ln"><span class="in" id="h7p"><span style="margin-right:.14em">1</span>animaci&oacute;n</span></div><div class="ln"><span class="in red" id="h7q">compleja</span></div></div>
</div>''')
win('#h7d2', t_dh); rise('#h7p', t_an2 - 0.04); rise('#h7q', t_cmp - 0.03); fx(t_cmp - 0.03, 'pop', 0.18)
leave('#h7dh', t_csm - 0.02)
# 7e: 0% -> 3% + cuadrícula de 100
cells = ''
G0, G1 = t_csm + 0.02, t_3 - 0.1
for i in range(100):
    cells += f'<i id="gc{i}"></i>'
    I(f'#gc{i}', opacity=0); S(f'#gc{i}', G0 + (G1 - G0) * (i // 10) / 10 + (i % 10) * 0.012, opacity=1)
for i in range(3): S(f'#gc{i}', t_3 + 0.06 + i * 0.09, backgroundColor=RED)
parts.append(f'''<div class="hd" id="h7e">
  <div class="pcn" style="left:66px;top:352px"><span class="gy" id="pc0">0%</span>{steps('pcs', ['1%', '2%', '3%'], t_3, t_3 + 0.27, 'rd')}</div>
  <div class="grid" style="left:662px;top:380px">{cells}</div>
  <div class="eb rd" style="left:662px;top:708px"><span id="h7l">3 DE 100</span></div>
  <div class="eb" style="left:846px;top:708px">{typed('h7m', 'DE MI USO', t_mi - 0.1, 30, 0)}</div>
</div>''')
win('#h7e', t_csm - 0.01); I('#pc0', opacity=0, y=40); T('#pc0', t_csm, 0.24, 'power3.out', opacity=1, y=0); S('#pc0', t_3, opacity=0)
I('#h7l', opacity=0); S('#h7l', t_3 + 0.3, opacity=1); fx(t_3, 'ding', 0.3)
for i in range(8): fx(G0 + i * (G1 - G0) / 8, 'click', 0.05)

# =====================================================================================================
#  8 · RECETA "tarjeta flotante con contador" (cotización)
#      ("Ahora bien, si se te hace caro, contrata a un animador y dime cuánto te cobra")
# =====================================================================================================
X6 = t_ab - 0.18                                   # tarjeta -> completa
leave('#h7e', X6 + 0.06, 0.12); leave('#h7d2', X6 + 0.06, 0.12)
ir_a('full', X6)
t_hac = f('hace caro'); t_ctr = f('contrata'); t_dim = f('dime'); t_cua = f('cuánto'); t_arm = f('Armé')
QY = bajo_barbilla(X6, t_arm)
nums = ['$53.117', '$36.798', '$21.838', '$03.130', '$91.061', '$09.633', '$88.024', '$64.326', '$47.905']
parts.append(f'''<div class="qc" id="qc" style="top:{QY}px">
  <div class="q1" id="q1">{typed('q1c', '¿Caro?', t_hac - 0.2, 14, 0.12)}</div>
  <div class="q2" id="q2"><div class="eb">COTIZACI&Oacute;N &middot; ANIMADOR PROFESIONAL</div><div class="qn">{steps('qn', nums, t_ctr - 0.03, t_dim - 0.03)}</div></div>
  <div class="q2" id="q3"><div class="eb">COTIZACI&Oacute;N &middot; ANIMADOR PROFESIONAL</div><div class="qn red">$???</div><div class="eb dk">{typed('q3c', 'DIME CUÁNTO TE COBRA', t_cua - 0.05, 34, 0.06)}</div></div>
</div>''')
I('#qc', opacity=0, y=36); T('#qc', t_hac - 0.5, 0.24, 'power3.out', opacity=1, y=0); fx(t_hac - 0.5, 'pop', 0.16)
I('#q2', opacity=0); I('#q3', opacity=0)
S('#q1', t_ctr - 0.02, opacity=0); S('#q2', t_ctr - 0.02, opacity=1); S('#q2', t_dim - 0.03, opacity=0); S('#q3', t_dim - 0.03, opacity=1)
for i in range(len(nums)): fx(t_ctr + i * (t_dim - 0.03 - t_ctr) / len(nums), 'click', 0.09)
FT('#q3 .qn', t_dim - 0.03, 0.22, {'scale': 1.25}, {'scale': 1}, 'back.out(2.5)'); fx(t_dim - 0.03, 'thump', 0.3)

# =====================================================================================================
#  9 · RECETA "oferta" + RECETA "CTA Comenta PALABRA"
#      ("Armé una skill de Claude que edita los videos… comenta VIDEO y te la paso por privado")
# =====================================================================================================
X7 = t_arm - 0.2                                   # completa -> tarjeta
T('#qc', X7 - 0.02, 0.12, 'power1.in', opacity=0)
ir_a('card', X7)
t_sk = f('skill'); t_ed = f('edita'); t_pro = f('profesional'); t_aut = f('automática'); t_anu = f('anuncios'); t_cnt = f('contenidos')
t_si = f('Si quieres'); t_cm = f('comenta'); t_vi = f('video', t_cm); t_pas = f('paso'); t_pri = f('privado')
(o_h, ow, oh) = M.ofe(300, 168, 'ANUNCIOS'); (v_h, vw, vh) = M.vid(300, 168, 'Contenido')
parts.append(f'''<div class="hd" id="h9">
  <div class="eb rd" style="left:78px;top:282px">{typed('h9e', 'SKILL DE CLAUDE · EDICIÓN AUTOMÁTICA', t_arm + 0.04, 40, 0)}</div>
  <div class="h1 h1s" style="left:74px;top:334px"><div class="ln"><span class="in" id="h9a">Edita tus videos</span></div><div class="ln"><span class="in red" id="h9b">como un profesional</span></div></div>
  <div class="bchip" id="h9c" style="left:78px;top:582px">+ en autom&aacute;tico</div>
  <div class="mc2" id="h9m1" style="left:516px;top:566px">{o_h}</div>
  <div class="mc2" id="h9m2" style="left:730px;top:580px">{v_h}</div>
</div>''')
win('#h9', X7 + 0.1); rise('#h9a', t_ed - 0.04); fx(t_ed - 0.04, 'swipe', 0.15); rise('#h9b', t_pro - 0.05); fx(t_pro - 0.05, 'pop', 0.18)
I('#h9c', clipPath='inset(0% 100% 0% 0%)'); T('#h9c', t_aut - 0.03, 0.26, 'power2.out', clipPath='inset(0% 0% 0% 0%)'); fx(t_aut - 0.03, 'pop', 0.2)
I('#h9m1', opacity=0, scale=0.3, rotation=-16); T('#h9m1', t_anu - 0.03, 0.3, 'back.out(1.8)', opacity=1, scale=1, rotation=-4); fx(t_anu - 0.03, 'pop', 0.2)
I('#h9m2', opacity=0, scale=0.3, rotation=16); T('#h9m2', t_cnt - 0.03, 0.3, 'back.out(1.8)', opacity=1, scale=1, rotation=3); fx(t_cnt - 0.03, 'pop', 0.2)
leave('#h9', t_si - 0.01)
# mascota sentada en la esquina de la tarjeta
parts.append(f'<div class="msc m3" id="ms3" style="left:{CARD_X + 6}px;top:{CARD_Y - 96}px">{mascot("m3")}</div>')
mascot_init('m3', 'h'); I('#ms3', opacity=0, y=60, scale=0.6); T('#ms3', t_sk, 0.3, 'back.out(2.2)', opacity=1, y=0, scale=1); fx(t_sk, 'pop', 0.22)
FT('#ms3', t_aut + 0.1, 0.16, {'y': 0}, {'y': -30, 'yoyo': True, 'repeat': 1}, 'power2.out')
# cierre: Comenta VIDEO
parts.append(f'''<div class="hd" id="h9z">
  <div class="eb rd" style="left:78px;top:282px">{typed('h9q', '¿QUIERES QUE TE LA ENVÍE?', t_si + 0.02, 40, 0)}</div>
  <div class="h1 ctr" style="top:322px"><div class="ln"><span class="in" id="h9k">Comenta</span></div></div>
  <div class="vbox" id="h9v" style="top:462px"><b>VIDEO</b></div>
  <div class="vsub" id="h9p" style="top:676px">y te la paso por privado &darr;</div>
</div>''')
win('#h9z', t_si); rise('#h9k', t_cm - 0.04); fx(t_cm - 0.04, 'pop', 0.2)
I('#h9v', opacity=0, scale=1.7, rotation=-9, xPercent=-50); T('#h9v', t_vi - 0.03, 0.2, 'power3.out', opacity=1, scale=1, rotation=-2.5)
fx(t_vi - 0.03, 'thump', 0.4); fx(t_vi + 0.02, 'ding', 0.3)
I('#h9p', opacity=0, y=24); T('#h9p', t_pas - 0.05, 0.22, 'power2.out', opacity=1, y=0); fx(t_pas - 0.05, 'pop', 0.16)
T('#ms3', t_cm - 0.06, 0.3, 'power2.inOut', x=-36, y=-62)
FT('#ms3', t_vi + 0.05, 0.16, {'y': -62}, {'y': -98, 'yoyo': True, 'repeat': 1}, 'power2.out')

# =====================================================================================================
#  CIERRE (déjalo igual): subtítulos + capturas para las polaroids + audio + index.html
# =====================================================================================================
subtitulos(desde=tF - 0.01,                         # el gancho no lleva subtítulos: el titular YA es el texto
           cambios=[('video', 'VIDEO', t_cm)])      # la palabra clave del CTA va en mayúsculas
TH = [(t_ge + 0.5, 180), (t_55 + 1.0, 60), (t_3 + 0.7, 200)]     # polaroids = escenas reales de este reel: (segundo, y del recorte)
capturas_provisionales(TH)                                       # luego:  python build.py --no-audio --thumbs
cerrar(musica='auto', inicio_musica=2.0, volumen_musica=0.28, capturas=TH,      # 'auto' = 1ª pista de <proyecto>/musica o recursos/musica
       css_extra=M.MINI_CSS, resumen=f'terminal y={T2Y} | cotización y={QY}')
