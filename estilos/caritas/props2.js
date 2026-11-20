// props2.js — más objetos pintados (p5.brush) del estilo CARITAS: engranes, laptop, calendario, megáfono, escudo, ojo… Mismas reglas que props.js.

function engrane(x, y, r, dientes, rot, col = COL.gray, key = 'eng') {
  boilSeed(key);
  const P = [];
  for (let i = 0; i < dientes * 4; i++) {
    const a = rot + i / (dientes * 4) * TAU, k = i % 4, rr = k === 1 || k === 2 ? r : r * .8;
    P.push([x + Math.cos(a) * rr, y + Math.sin(a) * rr]);
  }
  paint(P, { wash: col, ink: PAL.ink, sw: .9 });
  paint(ellPts(x, y, r * .3, r * .3, 14), { wash: COL.cream, ink: PAL.ink, sw: .6 });
}
function lluviaMonedas(x, y0, y1, t, t0, n = 7, key = 'lluvia') {   // monedas que caen desde t0 y se apilan
  for (let i = 0; i < n; i++) {
    const tc = t0 + i * .16; if (t < tc) continue;
    const k = easeIn(seg(t, tc, tc + .55)), px = x + (hash(i + 4) - .5) * 300, py = lerp(y0, y1 - (i % 3) * 26, k);
    moneda(px, py, 42, key + i);
  }
}
function laptop(x, y, s, encendida = 1, key = 'lap') {
  boilSeed(key);
  paint([[x - 120 * s, y], [x + 120 * s, y], [x + 140 * s, y + 18 * s], [x - 140 * s, y + 18 * s]], { wash: COL.grayLt, ink: PAL.ink, sw: .8 });
  paint(rrPts(x - 104 * s, y - 150 * s, 208 * s, 148 * s, 10 * s), { wash: COL.metal, ink: PAL.ink, sw: .9 });
  paint(rrPts(x - 90 * s, y - 138 * s, 180 * s, 122 * s, 6 * s), { wash: mixCol('#1E2230', COL.screenLt, encendida), ink: null });
  if (encendida > .5) for (let k = 0; k < 3; k++) inkLine([[x - 70 * s, y - 112 * s + k * 30 * s], [x + (30 - k * 20) * s, y - 112 * s + k * 30 * s]], .5, COL.metal, 'inkfine', 0);
}
function documento(x, y, s, rot = 0, key = 'doc') {
  boilSeed(key);
  push(); translate(x, y); rotate(rot);
  paint([[-60 * s, -80 * s], [30 * s, -80 * s], [60 * s, -50 * s], [60 * s, 80 * s], [-60 * s, 80 * s]], { wash: COL.cream, ink: PAL.ink, sw: .9 });
  for (let k = 0; k < 4; k++) inkLine([[-40 * s, -40 * s + k * 28 * s], [(k === 3 ? 10 : 40) * s, -40 * s + k * 28 * s]], .5, COL.gray, 'inkfine', 0);
  pop();
}
function tarjetaPerfil(x, y, s, col = PAL.violet, key = 'perfil') {
  boilSeed(key);
  paint(rrPts(x - 70 * s, y - 95 * s, 140 * s, 190 * s, 14 * s), { wash: COL.cream, ink: PAL.ink, sw: .9 });
  paint(ellPts(x, y - 35 * s, 30 * s, 30 * s, 16), { wash: col, ink: PAL.ink, sw: .6 });
  inkLine([[x - 40 * s, y + 25 * s], [x + 40 * s, y + 25 * s]], .6, COL.gray, 'inkfine', 0);
  inkLine([[x - 28 * s, y + 52 * s], [x + 28 * s, y + 52 * s]], .6, COL.gray, 'inkfine', 0);
}
function barraBusqueda(x, y, w, key = 'busq') {
  boilSeed(key);
  paint(rrPts(x - w / 2, y - 40, w, 80, 40), { wash: COL.cream, ink: PAL.ink, sw: 1 });
  lupa(x - w / 2 + 50, y - 6, 18, key + 'l');
}
function diana(x, y, r, key = 'diana') {
  boilSeed(key);
  paint(ellPts(x, y, r, r, 24), { wash: COL.cream, ink: PAL.ink, sw: 1 });
  paint(ellPts(x, y, r * .66, r * .66, 20), { wash: COL.red, ink: PAL.ink, sw: .7 });
  paint(ellPts(x, y, r * .33, r * .33, 16), { wash: COL.cream, ink: PAL.ink, sw: .6 });
}
function avionPapel(x, y, s, rot = 0, key = 'avion') {
  boilSeed(key);
  push(); translate(x, y); rotate(rot);
  paint([[-60 * s, -10 * s], [70 * s, -40 * s], [-10 * s, 40 * s], [-20 * s, 8 * s]], { wash: COL.screenLt, ink: PAL.ink, sw: .8 });
  inkLine([[-20 * s, 8 * s], [70 * s, -40 * s]], .6, PAL.ink, 'ink', 0);
  pop();
}
function luna(x, y, r, key = 'luna') {
  boilSeed(key);
  glow(x, y, r * 2.2, '#FFE9A8', .5);
  paint([...ellPts(x, y, r, r, 24).slice(5, 20), ...ellPts(x + r * .45, y - r * .2, r * .8, r * .8, 24).slice(14, 24).reverse()], { wash: COL.cream, fill: PAL.ochre, fillOp: 40, ink: PAL.ink, sw: .8, curv: .3 });
}
function calendario(x, y, s, marcas = 0, key = 'cal') {
  boilSeed(key);
  paint(rrPts(x - 110 * s, y - 100 * s, 220 * s, 200 * s, 14 * s), { wash: COL.cream, ink: PAL.ink, sw: 1 });
  paint(rrPts(x - 110 * s, y - 100 * s, 220 * s, 52 * s, 14 * s), { wash: COL.red, ink: PAL.ink, sw: .8 });
  for (let f = 0; f < 3; f++) for (let c = 0; c < 4; c++) {
    const i = f * 4 + c, cx = x - 72 * s + c * 48 * s, cy = y - 10 * s + f * 40 * s;
    paint(rectPts(cx - 14 * s, cy - 12 * s, 28 * s, 24 * s), { wash: i < marcas ? PAL.sap : mixCol(COL.cream, COL.grayLt, .5), ink: null });
  }
}
function carrito(x, y, s, t, key = 'carrito') {
  boilSeed(key);
  inkLine([[x - 130 * s, y - 150 * s], [x - 96 * s, y - 150 * s], [x - 60 * s, y - 40 * s], [x + 90 * s, y - 40 * s], [x + 120 * s, y - 120 * s], [x - 82 * s, y - 120 * s]], 1.4, PAL.ink, 'ink', 0);
  for (const wx of [-40, 70]) paint(ellPts(x + wx * s, y - 14 * s, 14 * s, 14 * s, 12), { wash: PAL.ink, ink: null });
}
function caja(x, y, s, col = COL.wood, key = 'caja') {
  boilSeed(key);
  paint(rectPts(x - 40 * s, y - 70 * s, 80 * s, 70 * s, 1), { wash: col, ink: PAL.ink, sw: .8 });
  inkLine([[x - 40 * s, y - 50 * s], [x + 40 * s, y - 50 * s]], .5, PAL.ink, 'inkfine', 0);
}
function camara(x, y, s, key = 'cam') {
  boilSeed(key);
  paint(rrPts(x - 90 * s, y - 60 * s, 180 * s, 120 * s, 16 * s), { wash: COL.metal, ink: PAL.ink, sw: 1 });
  paint([[x + 90 * s, y - 30 * s], [x + 150 * s, y - 60 * s], [x + 150 * s, y + 60 * s], [x + 90 * s, y + 30 * s]], { wash: COL.metal, ink: PAL.ink, sw: .9 });
  paint(ellPts(x - 10 * s, y, 34 * s, 34 * s, 16), { wash: COL.screen, ink: PAL.ink, sw: .7 });
  paint(ellPts(x + 60 * s, y - 38 * s, 9 * s, 9 * s, 8), { wash: COL.red, ink: null });
}
function megafono(x, y, s, key = 'mega') {
  boilSeed(key);
  paint([[x - 70 * s, y - 30 * s], [x + 50 * s, y - 80 * s], [x + 50 * s, y + 80 * s], [x - 70 * s, y + 30 * s]], { wash: COL.red, ink: PAL.ink, sw: 1 });
  paint(rrPts(x - 100 * s, y - 30 * s, 34 * s, 60 * s, 8 * s), { wash: COL.grayLt, ink: PAL.ink, sw: .8 });
  for (let k = 1; k <= 2; k++) inkLine([[x + 70 * s + k * 26 * s, y - 50 * s * k / 1.5], [x + 84 * s + k * 26 * s, y], [x + 70 * s + k * 26 * s, y + 50 * s * k / 1.5]], .9, PAL.ink, 'ink', .6);
}
function etiquetaPrecio(x, y, s, rot = 0, key = 'precio') {
  boilSeed(key);
  push(); translate(x, y); rotate(rot);
  paint([[-80 * s, -40 * s], [50 * s, -40 * s], [90 * s, 0], [50 * s, 40 * s], [-80 * s, 40 * s]], { wash: PAL.ochre, ink: PAL.ink, sw: .9 });
  paint(ellPts(56 * s, 0, 8 * s, 8 * s, 8), { wash: COL.cream, ink: PAL.ink, sw: .5 });
  pop();
}
function escudo(x, y, s, key = 'escudo') {
  boilSeed(key);
  paint([[x, y - 110 * s], [x + 90 * s, y - 76 * s], [x + 80 * s, y + 20 * s], [x, y + 100 * s], [x - 80 * s, y + 20 * s], [x - 90 * s, y - 76 * s]], { wash: PAL.teal, fill: COL.screenLt, fillOp: 60, ink: PAL.ink, sw: 1.1, curv: .2 });
}
function telefonoIcono(x, y, s, key = 'tel') {
  boilSeed(key);
  paint(ribbon([[x - 50 * s, y - 50 * s], [x - 30 * s, y + 10 * s], [x + 20 * s, y + 50 * s], [x + 50 * s, y + 40 * s]], 34 * s, 34 * s), { wash: COL.green, ink: PAL.ink, sw: .9 });
}
function ojo(x, y, s, t, key = 'ojo') {
  boilSeed(key);
  paint(through([[x - 90 * s, y], [x, y - 52 * s], [x + 90 * s, y], [x, y + 52 * s], [x - 90 * s, y]], 4), { wash: COL.cream, ink: PAL.ink, sw: 1 });
  paint(ellPts(x + 10 * Math.sin(t * 2) * s, y, 32 * s, 32 * s, 16), { wash: COL.blue, ink: PAL.ink, sw: .7 });
  paint(ellPts(x + 10 * Math.sin(t * 2) * s, y, 13 * s, 13 * s, 10), { wash: PAL.ink, ink: null });
}
function plastilina(x, y, s, t, key = 'plasti') {   // muñequito de plastilina (blando, se aplasta y estira)
  boilSeed(key);
  const sq = .08 * Math.sin(t * 5);
  paint(through([[x - 70 * s * (1 + sq), y], [x - 76 * s, y - 80 * s], [x - 40 * s, y - 150 * s * (1 - sq)], [x + 40 * s, y - 150 * s * (1 - sq)], [x + 76 * s, y - 80 * s], [x + 70 * s * (1 + sq), y], [x - 70 * s * (1 + sq), y]], 4),
        { wash: '#7FB3D9', fill: COL.blue, fillOp: 60, bleed: .1, tex: .6, ink: PAL.ink, sw: 1 });
  for (const d of [-1, 1]) {
    paint(ellPts(x + d * 26 * s, y - 92 * s, 16 * s, 18 * s, 12), { wash: COL.cream, ink: PAL.ink, sw: .5 });
    paint(ellPts(x + d * 26 * s, y - 88 * s, 7 * s, 8 * s, 8), { wash: PAL.ink, ink: null });
  }
  inkLine([[x - 20 * s, y - 52 * s], [x, y - 44 * s], [x + 20 * s, y - 52 * s]], .7, PAL.ink, 'ink', .6);
}
function lineaConexion(x0, y0, x1, y1, k, key = 'con') {
  if (k <= 0) return; boilSeed(key);
  inkLine([[x0, y0], [lerp(x0, x1, k), lerp(y0, y1, k)]], 1, COL.gray, 'ink', 0);
}
function listaTareas(x, y, s, key = 'lista') {
  boilSeed(key);
  paint(rectPts(x - 90 * s, y - 120 * s, 180 * s, 240 * s, 1), { wash: COL.cream, ink: PAL.ink, sw: .9 });
  for (let k = 0; k < 4; k++) {
    paint(rectPts(x - 66 * s, y - 86 * s + k * 52 * s, 24 * s, 24 * s), { wash: COL.cream, ink: PAL.ink, sw: .5 });
    inkLine([[x - 30 * s, y - 74 * s + k * 52 * s], [x + 64 * s, y - 74 * s + k * 52 * s]], .5, COL.gray, 'inkfine', 0);
  }
}
function boton(x, y, w, h, apretado, key = 'boton') {
  boilSeed(key);
  const d = apretado ? 8 : 0;
  paint(rrPts(x - w / 2, y - h / 2 + 12, w, h, h / 2), { wash: '#3E8A4F', ink: PAL.ink, sw: .9 });
  paint(rrPts(x - w / 2, y - h / 2 + d, w, h, h / 2), { wash: COL.green, ink: PAL.ink, sw: 1 });
}
