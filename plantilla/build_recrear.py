# -*- coding: utf-8 -*-
# =====================================================================================================
#  reel-motion · PLANTILLA ESTILO RECREAR  ("edítalo con reel-motion estilo recrear")
#  Un HECHO VIRAL recreado como animación plana + el análisis de negocio como infografía tipo informe.
#  Fondo claro con cuadrícula → MODO PLANO AZUL cuando se analiza → claro otra vez. Presentador chico abajo a la
#  derecha; subtítulos a su izquierda. Piezas en plantilla/recrear.py.
#
#  QUÉ CAMBIAR: el bloque ESCENAS. Las frases de f('...') deben existir TAL CUAL en words.json (python build.py --guion).
#  El ejemplo es el reel real de 61 s "El carro volador de Tesla no está a la venta" (producto señuelo):
#     1 recreación del hecho (rampa + carro que sale volando)  2 carro rojo  3 tarjetas de precio  4 modo plano
#     5 píldora  6 contador + pantallas EN VIVO  7 tachado  8 claro + píldora  9 barra razonable↔costoso
#     10-14 menús ANTES/DESPUÉS + burbujas + resaltado  15 dos objetos  16 título + sello  17 botón SÍGUEME
#  La RECREACIÓN (escena 1) es lo único que se dibuja a mano en cada reel: el objeto del caso (aquí un carro) y su
#  recorrido (aquí media vuelta por una rampa). Antes de dibujarla, mira los cuadros del video viral
#  (scripts/investigar.py) y copia el gesto icónico tal cual pasó.
# =====================================================================================================
import sys, os
P = os.path.dirname(os.path.abspath(__file__))
_sk = os.path.join(P, '_work', 'skill.txt')
SKILL = open(_sk, encoding='utf-8').read().strip() if os.path.exists(_sk) else os.path.expanduser('~/.claude/skills/reel-motion')
sys.path.insert(0, os.path.join(SKILL, 'scripts')); sys.path.insert(0, os.path.join(SKILL, 'plantilla')); sys.path.insert(0, P)
import motor
motor.iniciar(P, correcciones={'cloud': 'Claude', 'trust': 'Thrust', 'rocket': 'Rocket', 'performance': 'Performance', 'tesla': 'Tesla'},
              colores={'acento': '#D11F1D', 'tinta': '#161616', 'fondo': '#E4E4E2'})
from motor import *
import recrear as R
if '--guion' in sys.argv: guion(); sys.exit()
ft = R.ft                                                     # ft('palabra') = f('palabra') - 0.03 (entra CON la palabra)

R.escenario(informe='INFORME', tema='SE&Ntilde;UELO', caso='CASO &middot; EL LLAMATIVO', usuario='@soydiegoosorio')   # ← tu usuario

# ============================== ESCENAS (edita desde aquí) ==============================
# 1 · RECREACIÓN DEL HECHO: "El carro volador de Tesla no está a la venta."
#     Lo que pasó en el video viral: el carro rueda, sube por una rampa que da media vuelta y sale volando con propulsores.
t_esta = f('Está ahí'); t_tres = f('Tres versiones'); t_rock = ft('Rocket', t_tres - 0.1)
CX, CY, RR = 760, 760, 210                                    # centro y radio de la vuelta (lado derecho del escenario)
R.trazo('rampa', f'M 120 {CY + RR} L {CX} {CY + RR} A {RR} {RR} 0 0 0 {CX} {CY - RR} L 560 {CY - RR}', piso=CY + RR + 56, t1=f('Rocket'))
c1 = R.carro('c1')
y_piso = CY + RR - 34
R.recorrido(c1, 0.02, [(0.0, 165, y_piso, 0), (0.55, CX, y_piso, 0)]                       # rueda por el piso
            + R.media_vuelta(CX, CY, RR, dur=0.75)                                            # sube la rampa (180°)
            + R.curva(CX, CY - RR - 34, 430, 560, dur=0.6, arco=-60, rot0=-180, rot1=-360))   # sale volando y se endereza
fx(0.02, 'swipe', 0.12); fx(0.57, 'whoosh', 0.22); fx(1.3, 'whoosh', 0.2)
S(c1, 1.92, rotation=0)
R.propulsores('c1', 1.25, f('Rocket')); R.flota(c1, 1.95, f('Rocket'), base=560)
R.etiqueta('et1', 'NO EST&Aacute; A LA VENTA', ft('no está') if f('no está') > 1.0 else 1.9, x=190, y=400, golpe=True, t1=f('Rocket'))

# 2 · "Está ahí para vender el que sí se conduce."  → el carro rojo entra rodando por el piso
c2 = R.carro('c2', acento=True, propulsores=False)
R.entra_rodando(c2, ft('vender'), y=CY + RR + 12)
R.etiqueta('et2', 'EL QUE S&Iacute; SE VENDE', ft('se conduce'), x=230, y=1070, oscuro=True, t1=t_rock)
R.outo(c1, t_rock); R.outo(c2, t_rock)

# 3 · "Tres versiones. Rocket… Thrust… Performance…"  → tres tarjetas de precio, una por una
t_pero = ft('pero')
for pid, top, w, nombre, sub, precio, t_pre, chips, ac in (
        ('p1', 372, 'Rocket', 'ROCKET', 'LISTO PARA VOLAR', 'SIN PRECIO', ft('sin precio'), (('VUELA', 'vuela', 'ce'), ('SOLO POR INVITACI&Oacute;N', 'invitación', '')), False),
        ('p2', 560, 'Thrust', 'THRUST', 'LISTO PARA CORRER', '$250.000', ft('250'), (('RESERVA', 'reserva', ''), ('EDICI&Oacute;N LIMITADA', 'limitada', 'am')), False),
        ('p3', 748, 'Performance', 'PERFORMANCE', 'LISTO PARA CONDUCIR', '$50.000', ft('50', t_tres), (('CONDUCE', 'conduce', ''), ('RESERVA', 'reservar', 've')), True)):
    t_ = ft(w, t_tres - 0.1)
    R.tarjeta_precio(pid, top, nombre, sub, precio, t_, t_precio=t_pre, icono=R.carro_html(pid + 'c', acento=ac), t1=t_pero,
                     chips=[(tx, ft(pal, t_), col) for tx, pal, col in chips])

# 4 · "Vamos a analizarlo."  → MODO PLANO AZUL
R.plano(ft('Vamos'))

# 5 · "…pero cumple dos funciones. Primero: atraer la atención."
t_seg = f('Segundo'); t_primero = f('Primero')
R.pildora('pi1', 'FUNCI&Oacute;N 1 &middot; ATRAER LA ATENCI&Oacute;N', ft('cumple'), t1=t_seg)

# 6 · "Millones de personas vieron un carro flotar al bajar de una rampa."  → contador + 6 pantallas EN VIVO
t_mill = ft('Millones')
R.contador('cn', 450, 'VISTAS', (0, 1_000_000, '+'), t_primero + 0.15, t_mill, t_mill + 1.4, t1=t_seg)
for ti, cid in R.pantallas('lv', t_mill + 0.25, t1=t_seg,
                           celdas=[(c, R.carro_vivo_html(f'lvc{i}')) for i, c in enumerate(('2.1M', '890K', '1.3M', '640K', '2.8M', '1.1M'))]):
    i = int(cid[-1]); R.propulsores(f'lvc{i}', ti + 0.1, t_seg); R.flota(f'#lvc{i}', ti + 0.1, t_seg, amp=4, per=0.7)

# 7 · "Ningún anuncio habría podido comprar esa atención."  → PUBLICIDAD $$$ tachado
t_ning = ft('Ningún')
R.tachar('tx', 'PUBLICIDAD &nbsp;$$$', t_ning, (ft('comprar', t_ning), ft('atención', t_ning)), y=1066, t1=t_seg)

# 8 · "Segundo: cambiar la percepción del precio."  → vuelve a CLARO + píldora + el carro que vuela arriba
R.claro(ft('Segundo'))
t_marcas = f('Las marcas'); t_lado = ft('percepción')
R.pildora('pi2', 'FUNCI&Oacute;N 2 &middot; CAMBIAR LA PERCEPCI&Oacute;N', ft('cambiar'), t1=t_marcas)
c3 = R.carro('c3'); R.aparece(c3, t_lado, 540, 600); R.propulsores('c3', t_lado + 0.1, t_marcas); R.flota(c3, t_lado + 0.45, t_marcas, base=600)
R.nota('no1', 'EL REFERENTE VUELA', ft('precio', t_lado), y=482, t1=t_marcas)
R.outo(c3, t_marcas)

# 9 · "pagar 50 mil dólares por uno que se conduce empieza a parecer razonable."  → barra + indicador que se desliza
R.barra('ba', 770, '$50.000', ft('pagar'), ft('empieza'), ft('razonable'), objeto_html=R.carro_html('bac', acento=True), t1=t_marcas)

# 10-14 · "Las marcas pequeñas también pueden hacer esto…"  → menús ANTES / DESPUÉS (pastelería → mentoría)
t_ment = ft('mentoría'); t_ofer = ft('tu oferta'); t_tu = f('Tu producto')
mA = R.menu('mA', 96, 'ANTES', [('Pastel de cumplea&ntilde;os', 'PARA 12 PERSONAS', '$45'), ('Cupcake', 'UNIDAD', '$4')], ft('marcas'),
            t_items=(ft('también'), ft('pueden')))
mB = R.menu('mB', 554, 'DESPU&Eacute;S', [('Pastel de cumplea&ntilde;os', 'PARA 12 PERSONAS', '$45'), ('Cupcake', 'UNIDAD', '$4')], ft('Agrega'), dx=80)
mB.llena('Pastel para 200', 'CASI NADIE LO COMPRA', '$1.900', ft('Un pastel'), chip=('EXTREMO', ft('invitados'), 'am'))
mC = R.menu('mC', 96, 'ANTES', [('Sesi&oacute;n individual', '1 HORA', '$300'), ('Sesi&oacute;n grupal', 'POR PERSONA', '$49')], t_ment, entra=False)
mD = R.menu('mD', 554, 'DESPU&Eacute;S', [('Sesi&oacute;n individual', '1 HORA', '$300'), ('Sesi&oacute;n grupal', 'POR PERSONA', '$49')], t_ment, entra=False)
mD.llena('Mentor&iacute;a', 'VIP &middot; SOLO CON SOLICITUD', 'Consultar', t_ment + 0.2, chip=('SOLO ALTO NIVEL', ft('solo empresarios'), 'am', True))
R.cambia_menus([mA, mB], [mC, mD], t_ment)
R.burbuja('bu1', '&iquest;Esto por solicitud?', ft('la gente'), 110, 1056, t1=t_ofer)
R.burbuja('bu2', '&iquest;Qui&eacute;n entra ah&iacute;?', ft('hablar'), 560, 1056, t1=t_ofer, rot=(5, 2))
mC.resalta(0, t_ofer, 'y'); mD.resalta(0, ft('decisión'), 'g'); mD.chip(0, 'DECISI&Oacute;N INTELIGENTE', ft('inteligente'))
mC.sale(t_tu); mD.sale(t_tu)

# 15 · "Tu producto más vendido necesita una opción extravagante a su lado."  → los dos objetos, uno en el piso y otro volando
t_esa = f('esa es')
R.piso('ps2', 912, ft('Tu producto'), t1=t_esa)
c5 = R.carro('c5', acento=True, propulsores=False); R.aparece(c5, ft('más vendido'), 300, 860)
R.etiqueta('et3', 'M&Aacute;S VENDIDO', ft('vendido') + 0.1, x=150, y=960, oscuro=True, t1=t_esa)
c6 = R.carro('c6'); R.aparece(c6, ft('extravagante'), 740, 640); R.propulsores('c6', ft('extravagante') + 0.1, t_esa); R.flota(c6, ft('extravagante') + 0.45, t_esa, base=640)
R.nota('no2', 'LLAMA LA ATENCI&Oacute;N', ft('a su lado'), y=470, x=560, t1=t_esa)
R.outo(c5, t_esa); R.outo(c6, t_esa)

# 16 · "Esa es la estrategia del producto señuelo."  → título + sello
t_sig = f('Sígueme')
R.titulo('tt', ['PRODUCTO', 'SE&Ntilde;UELO'], ft('esa es'), sub='LA PSICOLOG&Iacute;A DETR&Aacute;S DE LO QUE COMPRAMOS')
R.sello('se', 'SE&Ntilde;UELO', ft('señuelo', f('estrategia')))
# 17 · "Sígueme para más estrategias como esta."
R.boton('bt', 'S&Iacute;GUEME PARA M&Aacute;S &rarr;', ft('Sígueme'))
# ============================== fin de las escenas ==============================

R.subtitulos(desde=t_esta, propios=('Tesla', 'Rocket', 'Thrust', 'Performance'), cambios=[('sígueme', 'SÍGUEME', t_sig)])
R.cerrar(musica='auto', inicio_musica=12.0, volumen_musica=0.26)        # 'auto' = 1ª pista de <proyecto>/musica o de recursos/musica
