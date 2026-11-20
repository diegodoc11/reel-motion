// props.js — objetos y ayudas pintadas (p5.brush) del estilo CARITAS de reel-motion (motor ClaudeAnimationBase).
// Todo es función pura del tiempo. Cada objeto llama boilSeed(key) para que su línea "hierva" sin temblar.
// Lienzo vertical 1080x1920: la acción vive en y 180-1150; el piso (y > SUELO) queda claro para el subtítulo y el presentador.

const SUELO = 1080;
const COL = {
  sepia: '#DCC6A2', sepiaDk: '#A9875F', horse: '#A06E48', horseDk: '#61412B', metal: '#5B6680', screen: '#2F3646',
  screenLt: '#BFE3F2', leaf: '#6E9F58', leafDk: '#4C7A3C', cake: '#F3CF9F', icing: '#FBF4EA', candle: '#E27A92',
  gray: '#9C9AA6', grayLt: '#CFCCD3', wood: '#B8875A', woodDk: '#7E5A3A', red: '#D24B44', gold: '#E8AA38',
  blue: '#5B8DD6', green: '#5DAE6B', cream: '#FFF5E2'
};

// ---------- tiempos: segundo en que el presentador dice una palabra (WORDS viene de tiempos.js) ----------
const normW = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]/g, '');
function tp(frase, despues = 0, fin = false) {
  const partes = frase.split(/\s+/).map(normW);
  for (let i = 0; i < WORDS.length; i++) {
    if (WORDS[i].s < despues - 1e-3) continue;
    let ok = true;
    for (let j = 0; j < partes.length; j++) {
      const w = WORDS[i + j]; if (!w) { ok = false; break; }
      const a = normW(w.w), b = normW(w.r), p = partes[j];
      if (!(a === p || b === p || (p.length >= 4 && (a.startsWith(p) || b.startsWith(p))))) { ok = false; break; }
    }
    if (ok) return fin ? WORDS[i + partes.length - 1].e : WORDS[i].s;
  }
  console.error('tp(): no encontré "' + frase + '" después de ' + despues);
  return despues;
}

// ---------- escenario: papel + manchas de acuarela + piso claro ----------
const TONOS = {
  sepia: [COL.sepia, PAL.ochre, '#EADCC3'], cielo: [PAL.sky, PAL.teal, '#DDE8D3'], calido: [PAL.clayLt, PAL.ochre, '#EEDFC8'],
  gris: [COL.grayLt, COL.gray, '#DEDAD5'], rosa: [PAL.rose, PAL.violet, '#EEDDD8'], verde: [PAL.sap, PAL.teal, '#DCE7CF'],
  oro: [PAL.ochre, PAL.clayLt, '#F0E2C2'], atardecer: [PAL.violet, PAL.rose, '#E5DAD8']
};
function escenario(tono = 'cielo', key = 'esc', piso = true) {
  const T = TONOS[tono] || TONOS.cielo;
  boilSeed(key + 'bg');
  paint(rectPts(-300, -300, W + 600, H + 600), { wash: PAL.paper, ink: null });
  paint(ellPts(540, 600, 640, 480, 30, 20), { fill: T[0], fillOp: 75, bleed: .3, tex: .6, ink: null });
  paint(ellPts(200, 300, 260, 160, 24, 14), { fill: T[1], fillOp: 42, bleed: .3, tex: .5, ink: null });
  paint(ellPts(900, 860, 280, 190, 24, 14), { fill: T[1], fillOp: 30, bleed: .3, tex: .5, ink: null });
  if (!piso) return;
  boilSeed(key + 'piso');
  paint(rectPts(-300, SUELO, W + 600, H - SUELO + 300, 3), { wash: T[2], fill: mixCol(T[2], T[1], .25), fillOp: 70, bleed: .05, tex: .6, ink: null });
  inkLine([[-300, SUELO + 2], [540, SUELO - 4], [W + 300, SUELO + 4]], 1, PAL.ink, 'ink', .5);
}

// ---------- transiciones (pantalla, fuera de la cámara) ----------
const WIPES = { barro: [PAL.clay, PAL.clayLt], sepia: [COL.sepiaDk, COL.sepia], cielo: [PAL.sky, '#C7E4F2'], verde: ['#9CC48A', '#C9DFB8'],
  oro: [PAL.ochre, '#F3D79A'], rosa: [PAL.rose, '#F2C9D3'] };
// entra: 'wipe' | 'flash' | null ; sale: 'wipe' | null. colores: llave de WIPES (el mismo a los dos lados del corte).
function transicion(lt, dur, entra, sale, cIn = 'barro', cOut = 'barro') {
  flushLetters();
  boilSeed('transicion');
  if (entra === 'wipe' && lt < .3) brushWipe(.5 + lt / .6, WIPES[cIn]);
  if (entra === 'flash' && lt < .25) flash(1 - lt / .25, PAL.cream);
  if (sale === 'wipe' && lt > dur - .3) brushWipe((lt - (dur - .3)) / .6, WIPES[cOut]);
}

// ---------- marcas sueltas ----------
function equis(x, y, r, k = 1, key = 'x') {          // X roja que se dibuja (k 0..1)
  if (k <= 0) return; boilSeed(key);
  const a = clamp(k * 2), b = clamp(k * 2 - 1);
  inkLine([[x - r, y - r], [lerp(x - r, x + r, a), lerp(y - r, y + r, a)]], 2.4, COL.red, 'ink', 0);
  if (b > 0) inkLine([[x + r, y - r], [lerp(x + r, x - r, b), lerp(y - r, y + r, b)]], 2.4, COL.red, 'ink', 0);
}
function chulo(x, y, r, k = 1, key = 'ok') {
  if (k <= 0) return; boilSeed(key);
  const P = [[x - r, y], [x - r * .3, y + r * .7], [x + r, y - r * .8]], q = clamp(k);
  const pts = q < .4 ? [P[0], [lerp(P[0][0], P[1][0], q / .4), lerp(P[0][1], P[1][1], q / .4)]] : [P[0], P[1], [lerp(P[1][0], P[2][0], (q - .4) / .6), lerp(P[1][1], P[2][1], (q - .4) / .6)]];
  inkLine(pts, 2.6, COL.green, 'ink', 0);
}
function flecha(x0, y0, x1, y1, k = 1, col = PAL.ink, key = 'fl', sw = 1.8) {
  if (k <= 0) return; boilSeed(key);
  const xe = lerp(x0, x1, k), ye = lerp(y0, y1, k), a = Math.atan2(ye - y0, xe - x0), h = 26;
  inkLine([[x0, y0], [(x0 + xe) / 2, (y0 + ye) / 2 - 10], [xe, ye]], sw, col, 'ink', .5);
  if (k > .6) inkLine([[xe - h * Math.cos(a - .5), ye - h * Math.sin(a - .5)], [xe, ye], [xe - h * Math.cos(a + .5), ye - h * Math.sin(a + .5)]], sw, col, 'ink', 0);
}
function chispa(x, y, r, k, key = 'sp', col = PAL.cream) {   // destello que aparece y se va (k 0..1)
  if (k <= 0 || k >= 1) return; boilSeed(key);
  paint(starPts(x, y, r * backOut(k) * (1 - k * .5), .25, 4, k * 2), { wash: col, washOp: 255 * (1 - k * k), ink: PAL.ink, sw: .5 });
}
function numero(txt, x, y, size, col, t0, t, o = {}) {      // letrero pintado (solo números o una palabra clave)
  if (t < t0) return;
  letter(txt, x, y, size, col, { pop: seg(t, t0, t0 + .35), stroke: PAL.cream, ...o });
}

// ---------- objetos ----------
function caballo(x, y, s, t, galope = 1, key = 'cab') {
  boilSeed(key);
  const ph = t * 2.6 * galope, bob = Math.sin(ph * TAU * 2) * 5 * s * galope, by = y - 112 * s + bob;
  const cola = Math.sin(ph * TAU * 2 + 1) * 10 * s;
  paint(ribbon([[x - 92 * s, by - 20 * s], [x - 128 * s, by + 8 * s], [x - 140 * s, by + 52 * s + cola]], 22 * s, 6 * s), { wash: COL.horseDk, ink: PAL.ink, sw: .8 });
  const pata = (lx, fase, lejos) => {
    const a = Math.sin(ph * TAU + fase) * .5 * galope;
    const cad = [x + lx * s, by + 24 * s], rod = [cad[0] + Math.sin(a) * 30 * s, cad[1] + 36 * s];
    const cas = [rod[0] + Math.sin(a * .4 - .15) * 22 * s, Math.min(y, rod[1] + 40 * s)];
    paint(ribbon([cad, rod, cas], 17 * s, 12 * s), { wash: lejos ? COL.horseDk : COL.horse, ink: PAL.ink, sw: .7 });
  };
  pata(-60, .5, true); pata(58, 0, true);
  paint(ellPts(x, by, 98 * s, 44 * s, 24, 1), { wash: COL.horse, ink: PAL.ink, sw: 1 });
  const cuello = [[x + 55 * s, by - 26 * s], [x + 98 * s, by - 92 * s], [x + 126 * s, by - 112 * s], [x + 160 * s, by - 100 * s],
                  [x + 166 * s, by - 80 * s], [x + 136 * s, by - 74 * s], [x + 112 * s, by - 30 * s], [x + 84 * s, by + 8 * s]];
  paint(cuello, { wash: COL.horse, ink: PAL.ink, sw: 1, curv: .35 });
  paint([[x + 112 * s, by - 112 * s], [x + 118 * s, by - 138 * s], [x + 128 * s, by - 110 * s]], { wash: COL.horseDk, ink: PAL.ink, sw: .7 });   // oreja
  paint(ribbon([[x + 104 * s, by - 106 * s], [x + 84 * s, by - 72 * s], [x + 62 * s, by - 40 * s]], 16 * s, 8 * s), { wash: COL.horseDk, ink: null });   // crin
  paint(ellPts(x + 138 * s, by - 98 * s, 4.5 * s, 4.5 * s, 8), { wash: PAL.ink, ink: null });
  pata(-40, 0, false); pata(78, .5, false);
}

function carro(x, y, s, t, mov = 1, key = 'car') {      // carro antiguo de lado, mirando a la derecha
  boilSeed(key);
  const bob = Math.abs(Math.sin(t * 9 * mov)) * 3 * s;
  paint(rrPts(x - 150 * s, y - 128 * s - bob, 300 * s, 70 * s, 22 * s), { wash: '#2F4A6E', fill: '#3E5F8A', fillOp: 90, bleed: .05, tex: .5, ink: PAL.ink, sw: 1.1 });
  paint(rrPts(x - 90 * s, y - 196 * s - bob, 150 * s, 74 * s, 16 * s), { wash: '#26394F', ink: PAL.ink, sw: 1 });
  paint(rrPts(x - 76 * s, y - 186 * s - bob, 56 * s, 50 * s, 8 * s), { wash: COL.screenLt, washOp: 220, ink: PAL.ink, sw: .6 });
  paint(rrPts(x - 12 * s, y - 186 * s - bob, 58 * s, 50 * s, 8 * s), { wash: COL.screenLt, washOp: 220, ink: PAL.ink, sw: .6 });
  paint(ellPts(x + 142 * s, y - 104 * s - bob, 11 * s, 11 * s, 12), { wash: PAL.ochre, ink: PAL.ink, sw: .6 });
  for (const wx of [-88, 96]) {
    boilSeed(key + 'r' + wx);
    const cx = x + wx * s, cy = y - 34 * s, r = 34 * s;
    paint(ellPts(cx, cy, r, r, 22), { wash: '#2B2233', ink: PAL.ink, sw: 1 });
    paint(ellPts(cx, cy, r * .55, r * .55, 16), { wash: COL.grayLt, ink: PAL.ink, sw: .6 });
    for (let k = 0; k < 3; k++) { const a = t * 10 * mov + k * TAU / 3; inkLine([[cx, cy], [cx + Math.cos(a) * r * .5, cy + Math.sin(a) * r * .5]], .6, PAL.ink, 'inkfine', 0); }
  }
}

function caracol(x, y, s, t, key = 'snail') {
  boilSeed(key);
  const st = Math.sin(t * 2) * 4 * s;
  paint(ribbon([[x - 70 * s, y - 8 * s], [x + 10 * s, y - 12 * s], [x + 70 * s, y - 26 * s], [x + 92 * s, y - 70 * s + st]], 30 * s, 22 * s), { wash: '#C9B27A', ink: PAL.ink, sw: .8 });
  for (const d of [-1, 1]) {
    const tip = [x + (98 + d * 14) * s, y - 118 * s + st];
    inkLine([[x + 92 * s, y - 84 * s + st], tip], .8, PAL.ink, 'ink', .3);
    paint(ellPts(tip[0], tip[1], 6 * s, 6 * s, 8), { wash: PAL.ink, ink: null });
  }
  paint(ellPts(x - 8 * s, y - 70 * s, 62 * s, 58 * s, 26, 1), { wash: COL.gold, fill: PAL.clayLt, fillOp: 90, bleed: .1, tex: .6, ink: PAL.ink, sw: 1 });
  const esp = []; for (let i = 0; i <= 26; i++) { const a = i * .55, r = 52 * s * (1 - i / 30); esp.push([x - 8 * s + Math.cos(a) * r, y - 70 * s + Math.sin(a) * r * .95]); }
  inkLine(esp, .9, PAL.ink, 'ink', .5);
}

function reloj(x, y, r, t, vel = 1, key = 'reloj') {
  boilSeed(key);
  paint(ellPts(x, y, r, r, 30, 1), { wash: COL.cream, ink: PAL.ink, sw: 1.2 });
  for (let k = 0; k < 12; k++) { const a = k / 12 * TAU; inkLine([[x + Math.cos(a) * r * .78, y + Math.sin(a) * r * .78], [x + Math.cos(a) * r * .9, y + Math.sin(a) * r * .9]], .7, PAL.ink, 'inkfine', 0); }
  const m = t * vel * TAU / 6 - Math.PI / 2, h = t * vel * TAU / 72 - Math.PI / 2 + 1.2;
  inkLine([[x, y], [x + Math.cos(h) * r * .5, y + Math.sin(h) * r * .5]], 1.6, PAL.ink, 'ink', 0);
  inkLine([[x, y], [x + Math.cos(m) * r * .74, y + Math.sin(m) * r * .74]], 1.1, COL.red, 'ink', 0);
  paint(ellPts(x, y, r * .07, r * .07, 8), { wash: PAL.ink, ink: null });
}

function celular(x, y, w, h, rot = 0, luz = 1, key = 'cel') {
  boilSeed(key);
  push(); translate(x, y); rotate(rot);
  paint(rrPts(-w / 2, -h / 2, w, h, w * .18), { wash: COL.screen, ink: PAL.ink, sw: .9 });
  paint(rrPts(-w * .38, -h * .4, w * .76, h * .72, w * .08), { wash: mixCol(COL.screen, COL.screenLt, luz), ink: null });
  paint(ellPts(0, h * .4, w * .07, w * .07, 8), { wash: COL.grayLt, ink: null });
  pop();
}
// celular para la mano de Clawd (armR / armL)
const enMano = (luz = 1) => (u, sw) => celular(u * .9, -u * .6, u * 1.25, u * 2.1, -.15, luz, 'celmano');

function tallo(x, base, h, col, colDk, t, key = 'tallo', hojas = true) {   // tallo que crece (h en px)
  if (h < 6) return; boilSeed(key);
  const n = Math.max(3, Math.floor(h / 70)), P = [];
  for (let i = 0; i <= n; i++) { const k = i / n; P.push([x + Math.sin(k * 5 + t * 1.5) * 18 * k, base - h * k]); }
  paint(ribbon(P, 26, 10), { wash: col, ink: PAL.ink, sw: .8 });
  if (hojas) for (let i = 1; i < n; i++) {
    const [px, py] = P[i], d = i % 2 ? 1 : -1;
    paint(ellPts(px + d * 34, py - 6, 32, 14, 14, 0, d * -.5), { wash: col, fill: colDk, fillOp: 70, ink: PAL.ink, sw: .6 });
  }
  const top = P[P.length - 1];
  paint(ellPts(top[0], top[1] - 6, 16, 22, 12), { wash: colDk, ink: PAL.ink, sw: .7 });
}

function torta(x, y, s, velas, encendidas, t, key = 'torta') {
  boilSeed(key);
  paint(rrPts(x - 120 * s, y - 120 * s, 240 * s, 120 * s, 18 * s), { wash: COL.cake, fill: PAL.clayLt, fillOp: 60, bleed: .05, tex: .5, ink: PAL.ink, sw: 1 });
  const glas = [[x - 124 * s, y - 112 * s]]; for (let i = 0; i <= 10; i++) glas.push([x - 120 * s + i * 24 * s, y - 120 * s + (i % 2 ? 26 : 12) * s]);
  glas.push([x + 124 * s, y - 112 * s], [x + 120 * s, y - 128 * s], [x - 120 * s, y - 128 * s]);
  paint(glas, { wash: COL.icing, ink: PAL.ink, sw: .8 });
  for (let i = 0; i < velas; i++) {
    boilSeed(key + 'v' + i);
    const vx = x + (i - (velas - 1) / 2) * 70 * s;
    paint(rrPts(vx - 11 * s, y - 210 * s, 22 * s, 82 * s, 6 * s), { wash: COL.candle, ink: PAL.ink, sw: .7 });
    const k = clamp(encendidas - i);
    if (k > 0) {
      const fl = 1 + .12 * Math.sin(t * 22 + i);
      glow(vx, y - 232 * s, 70 * s * k, '#FFC766', .9);
      paint(ellPts(vx, y - 232 * s, 10 * s * k, 20 * s * k * fl, 12), { wash: PAL.ochre, fill: COL.cream, fillOp: 140, ink: PAL.ink, sw: .5 });
    }
  }
}

function mundo(x, y, r, t, key = 'mundo') {
  boilSeed(key);
  paint(ellPts(x, y, r, r, 32, 1), { wash: PAL.sky, fill: PAL.teal, fillOp: 60, bleed: .05, tex: .5, ink: PAL.ink, sw: 1.1 });
  const tierras = [[0, -.35, .34, .2], [1.6, .15, .3, .26], [3.1, -.1, .26, .3], [4.4, .4, .22, .16]];
  for (const [a0, yy, rw, rh] of tierras) {
    const a = a0 + t * .8, c = Math.cos(a);
    if (c < .05) continue;
    boilSeed(key + a0);
    paint(ellPts(x + Math.sin(a) * r * .72, y + yy * r, rw * r * c, rh * r, 14, 1), { wash: PAL.sap, ink: null });
  }
  inkLine([[x - r, y], [x + r, y]], .4, PAL.ink, 'inkfine', 0);
}

function nube(x, y, s, key = 'nube', col = COL.cream) {      // nube de pensamiento o de cómputo
  boilSeed(key);
  const B = [[-60, 10, 52], [-10, -18, 62], [52, 4, 50], [10, 26, 56]];
  for (const [dx, dy, r] of B) paint(ellPts(x + dx * s, y + dy * s, r * s, r * s * .82, 18, 1), { wash: col, ink: null });
  paint(ellPts(x, y + 4 * s, 112 * s, 62 * s, 26, 2), { wash: col, ink: PAL.ink, sw: .8 });
}

function medidor(x, y, r, k, key = 'med') {          // semicírculo verde→rojo; k 0..1 = aguja
  boilSeed(key);
  const cols = [COL.green, PAL.ochre, COL.red];
  for (let i = 0; i < 3; i++) {
    const P = []; for (let j = 0; j <= 8; j++) { const a = Math.PI + (i + j / 8) / 3 * Math.PI; P.push([x + Math.cos(a) * r, y + Math.sin(a) * r]); }
    paint(ribbon(P, r * .22), { wash: cols[i], ink: PAL.ink, sw: .6 });
  }
  const a = Math.PI + clamp(k) * Math.PI;
  boilSeed(key + 'ag');
  paint(ribbon([[x, y], [x + Math.cos(a) * r * .86, y + Math.sin(a) * r * .86]], r * .1, r * .02), { wash: PAL.ink, ink: null });
  paint(ellPts(x, y, r * .1, r * .1, 10), { wash: PAL.ink, ink: null });
}

function globo(x, y, w, h, colaX = -1, key = 'glo', col = COL.cream) {   // globo de diálogo (sin texto)
  boilSeed(key);
  const tx = x + colaX * w * .28;
  paint([[tx - 22, y + h / 2 - 6], [tx + colaX * 20, y + h / 2 + 46], [tx + 26, y + h / 2 - 6]], { wash: col, ink: PAL.ink, sw: .8 });
  paint(rrPts(x - w / 2, y - h / 2, w, h, Math.min(w, h) * .3), { wash: col, ink: PAL.ink, sw: 1 });
}
function lupa(x, y, r, key = 'lupa', col = PAL.ink) {
  boilSeed(key);
  paint(ellPts(x, y, r, r, 20), { wash: COL.screenLt, washOp: 120, ink: col, sw: 1.2 });
  paint(ribbon([[x + r * .7, y + r * .7], [x + r * 1.6, y + r * 1.6]], r * .32, r * .26), { wash: col, ink: null });
}
function iaChat(x, y, r, t, key = 'ia') {             // ícono de "chat con IA": burbuja con destello
  boilSeed(key);
  paint(starPts(x, y, r * (1 + .06 * Math.sin(t * 6)), .32, 4, t * .5), { wash: PAL.clay, ink: PAL.ink, sw: .8 });
  paint(starPts(x + r * .9, y - r * .8, r * .4, .32, 4), { wash: PAL.ochre, ink: PAL.ink, sw: .5 });
}

function teclado(x, y, s, key = 'tec') {
  boilSeed(key);
  paint(rrPts(x - 210 * s, y - 70 * s, 420 * s, 140 * s, 14 * s), { wash: COL.grayLt, ink: PAL.ink, sw: 1 });
  for (let f = 0; f < 3; f++) for (let c = 0; c < 9 - (f === 2 ? 1 : 0); c++) {
    const kx = x - 186 * s + c * 42 * s + f * 14 * s, ky = y - 52 * s + f * 36 * s;
    paint(rrPts(kx, ky, 34 * s, 28 * s, 5 * s), { wash: COL.cream, ink: PAL.ink, sw: .45 });
  }
}

function casete(x, y, s, t, rot = 0, key = 'cas') {
  boilSeed(key);
  push(); translate(x, y); rotate(rot);
  paint(rrPts(-150 * s, -95 * s, 300 * s, 190 * s, 14 * s), { wash: '#44465A', ink: PAL.ink, sw: 1 });
  paint(rrPts(-126 * s, -76 * s, 252 * s, 52 * s, 8 * s), { wash: PAL.rose, ink: PAL.ink, sw: .6 });
  paint(rrPts(-90 * s, -12 * s, 180 * s, 62 * s, 10 * s), { wash: COL.cream, washOp: 200, ink: PAL.ink, sw: .6 });
  for (const d of [-1, 1]) {
    const cx = d * 56 * s, cy = 18 * s;
    paint(ellPts(cx, cy, 22 * s, 22 * s, 14), { wash: COL.cream, ink: PAL.ink, sw: .6 });
    for (let k = 0; k < 3; k++) { const a = t * 6 + k * TAU / 3; inkLine([[cx, cy], [cx + Math.cos(a) * 18 * s, cy + Math.sin(a) * 18 * s]], .5, PAL.ink, 'inkfine', 0); }
  }
  pop();
}
function walkman(x, y, s, t, key = 'walk') {
  boilSeed(key);
  paint(rrPts(x - 95 * s, y - 140 * s, 190 * s, 280 * s, 18 * s), { wash: COL.blue, fill: PAL.indigo, fillOp: 70, bleed: .05, tex: .5, ink: PAL.ink, sw: 1 });
  paint(rrPts(x - 70 * s, y - 110 * s, 140 * s, 110 * s, 10 * s), { wash: COL.screenLt, washOp: 200, ink: PAL.ink, sw: .6 });
  for (const d of [-1, 1]) {
    const cx = x + d * 34 * s, cy = y - 55 * s;
    paint(ellPts(cx, cy, 15 * s, 15 * s, 12), { wash: COL.cream, ink: PAL.ink, sw: .5 });
    const a = t * 5; inkLine([[cx, cy], [cx + Math.cos(a) * 12 * s, cy + Math.sin(a) * 12 * s]], .5, PAL.ink, 'inkfine', 0);
  }
  for (let k = 0; k < 3; k++) paint(rrPts(x - 66 * s + k * 48 * s, y + 30 * s, 36 * s, 28 * s, 6 * s), { wash: COL.grayLt, ink: PAL.ink, sw: .5 });
  inkLine([[x - 60 * s, y - 140 * s], [x - 120 * s, y - 210 * s], [x - 40 * s, y - 250 * s]], .9, PAL.ink, 'ink', .6);
}

function tienda(x, y, s, o = {}, key = 'tienda') {     // o: { polvo, grieta 0..1, brillo 0..1, col }
  boilSeed(key);
  const col = o.col || (o.polvo ? COL.grayLt : '#F2D9B8'), top = y - 330 * s;
  if (o.brillo) glow(x, y - 170 * s, 300 * s * o.brillo, '#FFD96A', .7 * o.brillo);
  paint(rectPts(x - 170 * s, top + 70 * s, 340 * s, 260 * s, 2), { wash: col, fill: mixCol(col, PAL.ink, .15), fillOp: 50, bleed: .05, tex: .5, ink: PAL.ink, sw: 1.1 });
  const toldo = o.polvo ? [COL.gray, COL.grayLt] : [COL.red, COL.cream];
  for (let k = 0; k < 6; k++) {
    boilSeed(key + 't' + k);
    const x0 = x - 190 * s + k * 63.3 * s;
    paint([[x0, top], [x0 + 63.3 * s, top], [x0 + 63.3 * s, top + 64 * s], [x0 + 31.6 * s, top + 84 * s], [x0, top + 64 * s]], { wash: toldo[k % 2], ink: PAL.ink, sw: .6 });
  }
  boilSeed(key + 'p');
  paint(rrPts(x - 50 * s, y - 150 * s, 100 * s, 150 * s, 10 * s), { wash: o.polvo ? COL.gray : COL.woodDk, ink: PAL.ink, sw: .8 });
  paint(rrPts(x - 150 * s, y - 210 * s, 80 * s, 80 * s, 8 * s), { wash: o.polvo ? '#B9B5BC' : COL.screenLt, ink: PAL.ink, sw: .7 });
  paint(rrPts(x + 70 * s, y - 210 * s, 80 * s, 80 * s, 8 * s), { wash: o.polvo ? '#B9B5BC' : COL.screenLt, ink: PAL.ink, sw: .7 });
  if (o.polvo) {                                       // telarañas
    boilSeed(key + 'tela');
    for (const [cx, cy, d] of [[x - 170 * s, top + 70 * s, 1], [x + 170 * s, top + 70 * s, -1]])
      for (let i = 1; i <= 3; i++) inkLine([[cx, cy + i * 18 * s], [cx + d * i * 9 * s, cy + i * 10 * s], [cx + d * i * 18 * s, cy]], .35, PAL.ink, 'inkfine', .5);
  }
  if (o.grieta > 0) {
    boilSeed(key + 'gr');
    const G = [[x + 10 * s, top + 84 * s], [x - 20 * s, top + 140 * s], [x + 26 * s, top + 196 * s], [x - 14 * s, top + 256 * s], [x + 16 * s, y]];
    const n = Math.max(2, Math.ceil(G.length * clamp(o.grieta)));
    inkLine(G.slice(0, n), 1.8, PAL.ink, 'ink', 0);
  }
}

function papeles(x, y, s, n = 6, t = 0, key = 'pap') {
  for (let i = 0; i < n; i++) {
    boilSeed(key + i);
    const yy = y - i * 22 * s, rot = (hash(i + 3) - .5) * .25 + Math.sin(t * 3 + i) * .02;
    push(); translate(x + (hash(i) - .5) * 20 * s, yy); rotate(rot);
    paint(rectPts(-90 * s, -12 * s, 180 * s, 24 * s, 1), { wash: COL.cream, ink: PAL.ink, sw: .6 });
    pop();
  }
}

function pastilla(x, y, w, h, key = 'pill', col = COL.cream) {    // caja de comentario / botón
  boilSeed(key);
  paint(rrPts(x - w / 2, y - h / 2, w, h, h / 2), { wash: col, ink: PAL.ink, sw: 1.1 });
}
function sobre(x, y, s, rot = 0, key = 'sobre') {
  boilSeed(key);
  push(); translate(x, y); rotate(rot);
  paint(rectPts(-80 * s, -52 * s, 160 * s, 104 * s, 1), { wash: COL.cream, ink: PAL.ink, sw: .9 });
  inkLine([[-80 * s, -52 * s], [0, 10 * s], [80 * s, -52 * s]], .8, PAL.ink, 'ink', 0);
  pop();
}
function pantallaPlay(x, y, s, key = 'play') {
  boilSeed(key);
  paint(rrPts(x - 130 * s, y - 85 * s, 260 * s, 170 * s, 14 * s), { wash: COL.screen, ink: PAL.ink, sw: 1 });
  paint([[x - 30 * s, y - 42 * s], [x + 46 * s, y], [x - 30 * s, y + 42 * s]], { wash: COL.red, ink: PAL.ink, sw: .7 });
  inkLine([[x - 40 * s, y + 85 * s], [x - 60 * s, y + 120 * s]], .8, PAL.ink, 'ink', 0);
  inkLine([[x + 40 * s, y + 85 * s], [x + 60 * s, y + 120 * s]], .8, PAL.ink, 'ink', 0);
}
function trofeo(x, y, s, key = 'trofeo') {
  boilSeed(key);
  paint([[x - 70 * s, y - 230 * s], [x + 70 * s, y - 230 * s], [x + 54 * s, y - 140 * s], [x, y - 110 * s], [x - 54 * s, y - 140 * s]], { wash: COL.gold, fill: PAL.cream, fillOp: 60, ink: PAL.ink, sw: 1, curv: .3 });
  paint(rectPts(x - 12 * s, y - 112 * s, 24 * s, 60 * s), { wash: COL.gold, ink: PAL.ink, sw: .7 });
  paint(rrPts(x - 54 * s, y - 56 * s, 108 * s, 40 * s, 8 * s), { wash: COL.woodDk, ink: PAL.ink, sw: .8 });
  for (const d of [-1, 1]) inkLine([[x + d * 70 * s, y - 220 * s], [x + d * 108 * s, y - 200 * s], [x + d * 70 * s, y - 160 * s]], 1, PAL.ink, 'ink', .7);
}
function moneda(x, y, r, key = 'mon') {
  boilSeed(key);
  paint(ellPts(x, y, r, r, 20), { wash: COL.gold, fill: PAL.cream, fillOp: 50, ink: PAL.ink, sw: .8 });
  inkLine([[x + r * .35, y - r * .45], [x - r * .3, y - r * .3], [x + r * .3, y + r * .2], [x - r * .35, y + r * .45]], .8, PAL.clayDk, 'ink', .6);
}
function baston(x, y, h, key = 'baston') {
  boilSeed(key);
  paint(ribbon([[x, y], [x + 4, y - h], [x + 22, y - h - 26], [x + 40, y - h - 6]], 12, 10), { wash: COL.wood, ink: PAL.ink, sw: .7 });
}
