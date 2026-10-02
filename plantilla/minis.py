# -*- coding: utf-8 -*-
# Mini piezas de diseño hechas 100% en HTML/CSS (los "ejemplos de animaciones" que salen en el collage,
# las polaroids y las tarjetas de muestra). Cada función devuelve (html, ancho, alto) a su tamaño base.
import random

MINI_CSS = r'''
.mn{position:relative;overflow:hidden;border-radius:16px;box-shadow:0 14px 34px rgba(0,0,0,.42);border:5px solid #fbfbf8;background:#fff}
.mn>*{position:absolute}
/* ¡ZAS! */
.zas{background:#fff}
.zas .rays{inset:-60%;background:repeating-conic-gradient(from 0deg,#111 0deg 2.2deg,transparent 2.2deg 9deg);opacity:.9}
.zas .hole{left:50%;top:50%;width:230px;height:150px;margin:-75px 0 0 -115px;background:radial-gradient(closest-side,#fff 72%,rgba(255,255,255,0) 100%)}
.zas b{left:0;right:0;top:50%;margin-top:-58px;text-align:center;font-family:"Poppins";font-weight:900;font-style:italic;font-size:92px;line-height:1;color:#111;transform:rotate(-8deg);letter-spacing:-.03em}
/* 2x1 */
.dos{background:#FBF3E4}
.dos small{left:0;right:0;top:20px;text-align:center;font-family:"JBM";font-weight:600;font-size:13px;letter-spacing:.2em;color:#9a8f7c}
.dos .ic{left:50%;top:58px;width:92px;height:92px;margin-left:-46px;border:6px solid #D8342A;border-radius:50%}
.dos .ic i{position:absolute;left:50%;top:16px;width:8px;height:54px;margin-left:-4px;background:#D8342A;border-radius:4px}
.dos .ic i:before,.dos .ic i:after{content:"";position:absolute;top:0;width:5px;height:22px;background:#D8342A;border-radius:3px}
.dos .ic i:before{left:-11px}.dos .ic i:after{left:14px}
.dos b{left:0;right:0;top:176px;text-align:center;font-family:"IT";font-weight:900;font-size:86px;line-height:1;color:#D8342A;letter-spacing:-.05em}
.dos span{left:0;right:0;top:272px;text-align:center;font-family:"IT";font-weight:800;font-size:27px;line-height:1.12;color:#2a211a}
.dos em{left:50%;top:380px;width:150px;margin-left:-75px;text-align:center;font-style:normal;font-family:"Inter";font-weight:700;font-size:17px;color:#fff;background:#D8342A;border-radius:20px;padding:9px 0}
/* SYNTH */
.syn{background:linear-gradient(180deg,#1c0b3d 0%,#3a1170 42%,#7b1fa2 58%,#12062b 58.2%,#12062b 100%)}
.syn b{left:0;right:0;top:22px;text-align:center;font-family:"IT";font-weight:900;font-size:34px;letter-spacing:.16em;color:#fff}
.syn .sun{left:50%;top:92px;width:170px;height:170px;margin-left:-85px;border-radius:50%;background:linear-gradient(180deg,#FFE259 0%,#FF8A3D 45%,#FF3D81 100%)}
.syn .sun:after{content:"";position:absolute;inset:0;border-radius:50%;background:repeating-linear-gradient(180deg,transparent 0 16px,#3a1170 16px 22px);-webkit-mask:linear-gradient(180deg,transparent 45%,#000 55%)}
.syn .grid{left:-40%;right:-40%;top:58%;bottom:0;background:repeating-linear-gradient(90deg,transparent 0 38px,rgba(255,80,200,.9) 38px 41px),repeating-linear-gradient(180deg,transparent 0 26px,rgba(255,80,200,.9) 26px 29px);transform:perspective(220px) rotateX(58deg);transform-origin:50% 0}
/* GRAN ESTRENO */
.est{background:#0E1730}
.est .ry{inset:-80%;background:repeating-conic-gradient(from 0deg,rgba(214,186,110,.22) 0deg .5deg,transparent .5deg 9deg)}
.est .fr{inset:10px;border:2px solid #C9AE66;border-radius:8px}.est .fr2{inset:17px;border:1px solid rgba(201,174,102,.6);border-radius:5px}
.est small{left:0;right:0;top:27%;text-align:center;font-family:"Mont";font-weight:800;font-size:.86em;letter-spacing:.34em;color:#D6BA6E}
.est b{left:0;right:0;top:41%;text-align:center;font-family:"Mont";font-weight:900;font-size:1.72em;letter-spacing:.09em;color:#EFE2B4;line-height:1}
.est .dv{left:50%;top:67%;width:26%;margin-left:-13%;height:2px;background:#C9AE66}
.est em{left:0;right:0;top:74%;text-align:center;font-style:normal;font-family:"JBM";font-weight:500;font-size:.4em;letter-spacing:.2em;color:#D6BA6E}
/* plano técnico */
.pla{background:#1E498D;background-image:linear-gradient(rgba(255,255,255,.12) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.12) 1px,transparent 1px);background-size:22px 22px}
.pla b{left:22px;top:20px;font-family:"JBM";font-weight:500;font-size:38px;line-height:1.05;color:#fff}.pla b u{text-decoration:none;color:#9CC2FF}
.pla i{left:22px;right:22px;top:118px;bottom:-30px;border:2px dashed rgba(255,255,255,.75)}
/* Tu app */
.app{background:#EEF0F6}
.app .ph{left:5%;top:9%;width:21%;bottom:9%;border:.22em solid #14161d;border-radius:.6em;background:#fff;overflow:hidden}
.app .ph u{position:absolute;left:0;right:0;top:0;height:22%;background:#3354E4;text-decoration:none;color:#fff;font-family:"Inter";font-weight:700;font-size:.34em;padding:.5em .7em}
.app .ph s{position:absolute;bottom:38%;width:12%;background:#3354E4;border-radius:2px 2px 0 0;text-decoration:none}
.app .ph q{position:absolute;left:14%;bottom:12%;width:38%;height:11%;border-radius:1em;background:#3354E4}.app .ph q:after{content:"";position:absolute;right:6%;top:12%;width:42%;height:76%;border-radius:50%;background:#fff}
.app b{left:34%;top:18%;font-family:"IT";font-weight:900;font-size:1.56em;letter-spacing:-.05em;color:#14161d;line-height:1}
.app span{left:34%;top:51%;font-family:"Inter";font-weight:500;font-size:.4em;color:#6a6f7d;white-space:nowrap}
.app em{left:34%;top:66%;font-style:normal;font-family:"Inter";font-weight:700;font-size:.38em;color:#14161d;background:#fff;border-radius:.7em;padding:.55em .9em;box-shadow:0 2px 8px rgba(0,0,0,.12);white-space:nowrap}
.app em:before{content:"✓";display:inline-block;width:1.4em;height:1.4em;line-height:1.4em;text-align:center;border-radius:50%;background:#3354E4;color:#fff;margin-right:.5em;font-size:.9em}
/* porcentaje */
.pct{background:#E8E8E1}
.pct b{left:16px;top:10px;font-family:"IT";font-weight:900;font-size:150px;letter-spacing:-.06em;color:#D11F1D;line-height:1}
.pct .g{left:20px;top:190px;width:232px;height:170px;background-image:linear-gradient(#E8E8E1 3px,transparent 3px),linear-gradient(90deg,#E8E8E1 3px,transparent 3px);background-size:23.2px 17px;background-color:#c9c9c2}
.pct .r{left:20px;top:190px;width:69px;height:17px;background:#D11F1D;border-right:3px solid #E8E8E1}
/* Videos */
.vid{background:#0e0e0e}
.vid .sc{inset:0;background:repeating-linear-gradient(180deg,rgba(255,255,255,.07) 0 6%,transparent 6% 12%);-webkit-mask:linear-gradient(90deg,transparent 30%,#000 75%)}
.vid small{left:6%;top:9%;font-family:"JBM";font-weight:700;font-size:.4em;color:#fff;letter-spacing:.05em}.vid small:before{content:"";display:inline-block;width:.75em;height:.75em;border-radius:50%;background:#E0261F;margin-right:.5em}
.vid b{left:7%;top:28%;font-family:"PFI";font-weight:900;font-size:1.9em;color:#fff;line-height:1}
.vid .hd{right:17%;top:30%;width:13%;aspect-ratio:1;border-radius:50%;background:#242424}
.vid .bd{right:8.5%;top:58%;width:30%;height:60%;border-radius:50% 50% 0 0;background:#242424}
.vid .pb{left:6%;right:6%;bottom:11%;height:.09em;background:#3a3a3a}.vid .pb i{position:absolute;left:0;top:0;bottom:0;width:26%;background:#E0261F}
.vid .pb i:after{content:"";position:absolute;right:-.22em;top:-.17em;width:.44em;height:.44em;border-radius:50%;background:#E0261F}
.vid em{right:6%;bottom:17%;font-style:normal;font-family:"JBM";font-weight:500;font-size:.36em;color:#cfcfcf}
/* costo $0 */
.cst{background:#0D0F1D}
.cst small{left:20px;top:22px;font-family:"JBM";font-weight:500;font-size:19px;color:#E8894F;white-space:nowrap}.cst small u{text-decoration:none;color:#cfcbb5}
.cst span{left:20px;top:150px;font-family:"JBM";font-weight:600;font-size:22px;color:#cfcbb5}
.cst b{left:0;right:0;top:200px;text-align:center;font-family:"IT";font-weight:900;font-size:150px;letter-spacing:-.04em;color:#E8894F;line-height:1;text-shadow:0 0 34px rgba(232,137,79,.75)}
/* Tu negocio */
.neg{background:#3C8375}
.neg .hill{left:-10%;right:-10%;bottom:-62%;height:100%;border-radius:50%;background:#2F6E62}
.neg .sun{right:7%;top:9%;width:13%;aspect-ratio:1;border-radius:50%;background:#F6C443}
.neg b{left:6%;top:20%;font-family:"PFI";font-weight:900;font-size:1.36em;color:#F3EBD3;line-height:1;white-space:nowrap}
.neg span{left:7%;top:57%;font-family:"Caveat";font-weight:700;font-size:.62em;color:#d9eadf;white-space:nowrap}
.neg .sh{right:9%;bottom:0;width:28%;height:52%;background:#F3EBD3}
.neg .aw{right:6.5%;bottom:50%;width:33%;height:17%;background:repeating-linear-gradient(90deg,#D8342A 0 12.5%,#fff 12.5% 25%);border-radius:0 0 30% 30%/0 0 60% 60%}
.neg .dr{right:19%;bottom:0;width:8.5%;height:34%;background:#9B5B3C}
.neg em{right:13%;bottom:69%;font-style:normal;font-family:"JBM";font-weight:700;font-size:.3em;color:#fff;background:#D8342A;padding:.25em .7em;border-radius:.3em;transform:rotate(-4deg)}
/* Hecho con IA (rojo) */
.hia{background:#D11F1D}
.hia pre{left:14px;top:150px;right:10px;font-family:"JBM";font-weight:400;font-size:13px;line-height:1.5;color:rgba(255,255,255,.34);white-space:pre}
.hia b{left:22px;top:22px;font-family:"IT";font-weight:900;font-size:62px;letter-spacing:-.05em;line-height:1.02;color:#fff}.hia b u{text-decoration:none;color:#14161d}
/* dental */
.den{background:#fff}
.den svg{left:50%;top:26px;width:110px;height:110px;margin-left:-55px}
.den b{left:0;right:0;top:146px;text-align:center;font-family:"IT";font-weight:900;font-size:92px;letter-spacing:-.05em;color:#18A07E;line-height:1}
.den span{left:0;right:0;top:246px;text-align:center;font-family:"IT";font-weight:800;font-size:30px;line-height:1.1;color:#16332c}
.den small{left:0;right:0;top:326px;text-align:center;font-family:"Inter";font-weight:500;font-size:14px;color:#7b8a85}
.den em{left:50%;top:362px;width:190px;margin-left:-95px;text-align:center;font-style:normal;font-family:"Inter";font-weight:700;font-size:17px;color:#fff;background:#18A07E;border-radius:22px;padding:10px 0}
/* 7 días */
.dia{background:#E8E8E1}
.dia b{left:14px;top:-6px;font-family:"IT";font-weight:900;font-size:214px;letter-spacing:-.06em;color:#D11F1D;line-height:1}
.dia span{left:128px;top:44px;font-family:"IT";font-weight:900;font-size:50px;letter-spacing:-.05em;color:#14161d;line-height:1}
.dia small{left:130px;top:102px;font-family:"IT";font-weight:700;font-size:32px;letter-spacing:-.04em;color:#14161d}
.dia i{left:22px;right:22px;top:236px;height:16px;background:#c9c9c2}.dia i:after{content:"";position:absolute;left:0;top:0;bottom:0;width:82%;background:#14161d}
/* OFERTA */
.ofe{background:linear-gradient(100deg,#EA1D77 0%,#F2553F 45%,#F6A23A 78%,#F6C443 100%)}
.ofe .dt{inset:0;background:radial-gradient(rgba(255,255,255,.2) 1.6px,transparent 2px);background-size:17px 17px}
.ofe b{left:6.5%;top:25%;font-family:"Poppins";font-weight:900;font-size:1.86em;color:#fff;line-height:1;letter-spacing:-.01em;text-shadow:.045em .06em 0 rgba(160,20,90,.55)}
.ofe .st{right:5.5%;top:11%;width:25%;aspect-ratio:1;background:#F9E04B;clip-path:polygon(50% 0%,58% 12%,71% 5%,74% 19%,89% 17%,86% 31%,100% 36%,91% 47%,100% 58%,87% 64%,90% 79%,76% 78%,72% 92%,60% 85%,50% 100%,40% 85%,28% 92%,24% 78%,10% 79%,13% 64%,0% 58%,9% 47%,0% 36%,14% 31%,11% 17%,26% 19%,29% 5%,42% 12%)}
.ofe .st u{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;text-decoration:none;font-family:"IT";font-weight:900;font-size:.62em;color:#1b0a18;letter-spacing:-.03em;transform:rotate(-6deg)}
.ofe em{left:6.5%;bottom:13%;font-style:normal;font-family:"Poppins";font-weight:800;font-size:.44em;color:#fff;background:#1b0a22;border-radius:2em;padding:.5em 1.5em}
/* contadores */
.con{background:#fff}
.con small{left:0;right:0;top:20px;text-align:center;font-family:"JBM";font-weight:600;font-size:11px;letter-spacing:.24em;color:#3354E4}
.con .cal{left:50%;top:52px;width:86px;height:112px;margin-left:-43px;border:6px solid #3354E4;border-radius:14px}
.con .cal:before{content:"";position:absolute;left:10px;right:10px;top:10px;height:22px;border-radius:5px;background:#3354E4}
.con .cal:after{content:"";position:absolute;left:11px;right:11px;top:44px;bottom:12px;background:radial-gradient(#3354E4 4.2px,transparent 4.8px);background-size:17.3px 16px}
.con b{left:0;right:0;top:178px;text-align:center;font-family:"IT";font-weight:900;font-size:84px;letter-spacing:-.05em;color:#3354E4;line-height:1}
.con span{left:0;right:0;top:268px;text-align:center;font-family:"IT";font-weight:800;font-size:26px;line-height:1.1;color:#14161d}
/* acuarela + mascota */
.acu{background:#EBEDDC}
.acu .b1{right:-18%;top:-12%;width:66%;height:44%;border-radius:47% 53% 60% 40%/55% 45% 55% 45%;background:#CB8473}
.acu .b2{left:-22%;top:36%;width:74%;height:42%;border-radius:55% 45% 40% 60%/50% 60% 40% 50%;background:#EADFD2}
.acu b{left:20px;top:26px;font-family:"PFI";font-weight:900;font-size:46px;color:#1a1a1a;line-height:1}
.acu .ms svg{position:absolute;inset:0;width:100%;height:100%}
.acu .ms{left:50%;bottom:34px;width:150px;margin-left:-75px;height:122px}
'''

CODE_TXT = '''const escena = nueva("gancho")
for (const estilo of ESTILOS) {
  pintar(fondo, estilo)
  escribir(titulo, estilo.fuente)
  recortar(diego, mascara[t])
}
render(t) -> canvas -> ffmpeg
// 0 cuadros de IA de video
const video = canvas.dibujar(t)
componer(voz, subtitulos)'''

TOOTH = ('<svg viewBox="0 0 100 100"><path d="M50 22c-8-9-30-10-33 9-2 13 5 22 7 35 2 12 3 22 9 22 7 0 5-20 17-20s10 20 17 20c6 0 7-10 9-22 2-13 9-22 7-35-3-19-25-18-33-9z" '
         'fill="none" stroke="#18A07E" stroke-width="6" stroke-linejoin="round"/></svg>')


def zas():   return '<div class="mn zas" style="width:320px;height:340px"><i class="rays"></i><i class="hole"></i><b>¡ZAS!</b></div>', 320, 340
def dos():   return ('<div class="mn dos" style="width:240px;height:440px"><small>LA BRASA</small><i class="ic"><i></i></i><b>2x1</b>'
                     '<span>en hamburguesas<br>los martes</span><em>Reserva &rarr;</em></div>'), 240, 440
def syn():   return '<div class="mn syn" style="width:320px;height:400px"><b>SYNTH</b><i class="sun"></i><i class="grid"></i></div>', 320, 400
def est(w=420, h=240):
    return (f'<div class="mn est" style="width:{w}px;height:{h}px;font-size:{h / 6.3:.1f}px"><i class="ry"></i><i class="fr"></i><i class="fr2"></i>'
            '<small>GRAN</small><b>ESTRENO</b><i class="dv"></i><em>PROMOCIONES &middot; S&Aacute;B 8 PM</em></div>'), w, h
def pla():   return '<div class="mn pla" style="width:320px;height:190px"><b>plano<br><u>t&eacute;cnico</u></b><i></i></div>', 320, 190
def app(w=400, h=190):
    bars = ''.join(f'<s style="left:{14 + 21 * i}%;height:{hh}%"></s>' for i, hh in enumerate([16, 26, 21, 34]))
    return (f'<div class="mn app" style="width:{w}px;height:{h}px;font-size:{h / 3.9:.1f}px"><i class="ph"><u>Mi app</u>{bars}<q></q></i>'
            '<b>Tu app</b><span>demo animada, lista para tiendas</span><em>Nueva versi&oacute;n disponible</em></div>'), w, h
def pct():   return '<div class="mn pct" style="width:280px;height:400px"><b>3%</b><i class="g"></i><i class="r"></i></div>', 280, 400
def vid(w=480, h=240, title='Videos'):
    big = title == 'Videos'
    ttl = '<b>Videos</b>' if big else f'<b style="font-size:1.42em;top:33%">{title}</b>'
    sil = '<i class="hd"></i><i class="bd"></i>' if big else ''
    return (f'<div class="mn vid" style="width:{w}px;height:{h}px;font-size:{h / 5.2:.1f}px"><i class="sc"></i><small>REC</small>{ttl}'
            f'{sil}<i class="pb"><i></i></i><em>00:02</em></div>'), w, h
def cst():   return ('<div class="mn cst" style="width:300px;height:400px"><small>&#10095; claude <u>--costo</u></small><span>total</span><b>$0</b></div>'), 300, 400
def neg(w=360, h=190):
    return (f'<div class="mn neg" style="width:{w}px;height:{h}px;font-size:{h / 4.3:.1f}px"><i class="hill"></i><i class="sun"></i><b>Tu negocio</b>'
            '<span>hecho a mano&hellip; en c&oacute;digo</span><i class="sh"></i><i class="dr"></i><i class="aw"></i><em>ABIERTO</em></div>'), w, h
def hia():   return (f'<div class="mn hia" style="width:320px;height:290px"><pre>{CODE_TXT}</pre><b>Hecho<br>con <u>IA.</u></b></div>'), 320, 290
def den():   return (f'<div class="mn den" style="width:300px;height:430px">{TOOTH}<b>30%</b><span>en limpieza<br>dental</span>'
                     '<small>Solo este mes &middot; agenda hoy</small><em>Agenda tu cita &rarr;</em></div>'), 300, 430
def dia():   return '<div class="mn dia" style="width:260px;height:290px"><b>7</b><span>d&iacute;as</span><small>de uso</small><i></i></div>', 260, 290
def ofe(w=420, h=240, pill='ANUNCIOS'):
    return (f'<div class="mn ofe" style="width:{w}px;height:{h}px;font-size:{h / 4.6:.1f}px"><i class="dt"></i><b>OFERTA</b>'
            f'<i class="st"><u>-40%</u></i><em>{pill}</em></div>'), w, h
def con():   return ('<div class="mn con" style="width:260px;height:360px"><small>CONTADORES</small><i class="cal"></i><b>-50%</b>'
                     '<span>en tu<br>contabilidad</span></div>'), 260, 360
def acu(mascot_svg):
    return (f'<div class="mn acu" style="width:300px;height:400px"><i class="b1"></i><i class="b2"></i><b>acuarela</b><i class="ms">{mascot_svg}</i></div>'), 300, 400

# herramientas que NO hicieron falta (iconos propios, trazo simple): (rótulo, fondo, color del trazo, svg 24x24)
_S = 'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
TOOLS = [
    ('EDITOR', '#C8F03C', '#15171c', f'<g {_S}><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M20 4 8.1 15.9M14.5 14.5 20 20M8.1 8.1 12 12"/></g>'),
    ('ANIMADOR', '#2D6BFF', '#ffffff', f'<g {_S}><circle cx="12" cy="8" r="4"/><path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1"/></g>'),
    ('DISE&Ntilde;ADOR', '#15171c', '#ffffff', f'<g {_S}><path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="M2 2l7.6 7.6"/><circle cx="11" cy="11" r="2"/></g>'),
    ('PLANTILLAS', '#ffffff', '#15171c', f'<g {_S}><rect x="3" y="3" width="18" height="7" rx="1.5"/><rect x="3" y="14" width="9" height="7" rx="1.5"/><rect x="16" y="14" width="5" height="7" rx="1.5"/></g>'),
    ('PROGRAMAS', '#FF7A3D', '#ffffff', f'<g {_S}><rect x="2" y="4" width="20" height="16" rx="2.5"/><path d="M2 9h20M6 6.6h.01M9 6.6h.01"/></g>'),
]
