// reel-motion · MOTOR del estilo FANZINE: "una sola maqueta, muchas cámaras" (contrato de canvas de la skill javascript-animation) con look de IMPRESIÓN
// RISOGRÁFICA. Todo el video es UN mundo largo (una estación por frase, una al lado de la otra); la cámara viaja de
// estación en estación cuando el presentador cambia de frase. Cada tinta (azul, rosa, amarillo) se dibuja en su propia capa,
// se le pone grano, se desfasa un poquito (registro) y se multiplica sobre el papel: donde se cruzan salen colores
// nuevos, como en un fanzine. Contrato del render de la skill: window.draw(frame) es función pura del cuadro.
const W = 1080, H = 1920, FPS = 30;
const cv = document.getElementById('c'); cv.width = W; cv.height = H;
const MAIN = cv.getContext('2d');
let ctx = MAIN;

// ---------- tintas y papel ----------
const TINTAS = { azul: '#1D58C4', rosa: '#FF4BA6', amarillo: '#FFDD3C' };
const REG = { azul: [0, 0], rosa: [5, -3], amarillo: [-4, 3] };      // desfase de registro de cada tinta (px de pantalla)
const PAPEL = '#F3EEE3';
const FUENTE = (peso, size) => `${peso} ${size}px Bahnschrift, "Arial Narrow", Arial, sans-serif`;

// ---------- matemática (de templates/starter.html) ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const ease = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const easeOut = t => 1 - Math.pow(1 - clamp(t), 3);
const back = t => { t = clamp(t); const c = 1.7; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
const prog = (t, a, b) => clamp((t - a) / (b - a));
function hash2(a, b) { let n = Math.imul(a | 0, 374761393) + Math.imul(b | 0, 668265263); n = Math.imul(n ^ (n >>> 13), 1274126177); return ((n ^ (n >>> 16)) >>> 0) / 4294967295; }
function rng(seed) { let a = seed | 0; return () => { a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function resample(pts, step = 9, closed = false) { const out = [], P = closed ? [...pts, pts[0]] : pts; for (let i = 0; i < P.length - 1; i++) { const [x0, y0] = P[i], [x1, y1] = P[i + 1], n = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0) / step)); for (let k = 0; k < n; k++) out.push([lerp(x0, x1, k / n), lerp(y0, y1, k / n)]); } if (!closed) out.push(P[P.length - 1]); return out; }
function suave(pts, n = 10) { if (pts.length < 3) return resample(pts, 6); const out = []; for (let i = 0; i < pts.length - 1; i++) { const p0 = pts[Math.max(0, i - 1)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(pts.length - 1, i + 2)]; for (let k = 0; k < n; k++) { const t = k / n, t2 = t * t, t3 = t2 * t; out.push([0, 1].map(j => .5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3))); } } out.push(pts[pts.length - 1]); return out; }
const circulo = (cx, cy, r, ry = r) => { const n = Math.max(24, Math.round(Math.max(r, ry) * .5)), o = []; for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2; o.push([cx + Math.cos(a) * r, cy + Math.sin(a) * ry]); } return o; };
const caja = (x, y, w, h) => [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];
const hasta = (s, p) => { if (p >= 1) return s; const acc = [0]; for (let i = 1; i < s.length; i++) acc.push(acc[i - 1] + Math.hypot(s[i][0] - s[i - 1][0], s[i][1] - s[i - 1][1])); const L = acc[acc.length - 1] * p, out = [s[0]]; for (let i = 1; i < s.length; i++) { if (acc[i] <= L) out.push(s[i]); else { const f = (L - acc[i - 1]) / (acc[i] - acc[i - 1] || 1); out.push([lerp(s[i - 1][0], s[i][0], f), lerp(s[i - 1][1], s[i][1], f)]); break; } } return out; };

// ---------- capas de tinta, grano y trama (se crean una vez) ----------
const CAPAS = {};
for (const k of Object.keys(TINTAS)) { const c = document.createElement('canvas'); c.width = W; c.height = H; CAPAS[k] = { c, x: c.getContext('2d') }; }
function teja(seed, fn) { const c = document.createElement('canvas'); c.width = c.height = 512; fn(c.getContext('2d'), rng(seed)); return c; }
const TEJA_PAPEL = teja(7, (p, r) => { p.fillStyle = PAPEL; p.fillRect(0, 0, 512, 512); for (let i = 0; i < 9000; i++) { p.fillStyle = r() < .5 ? 'rgba(90,70,50,0.06)' : 'rgba(255,255,255,0.09)'; p.fillRect(r() * 512, r() * 512, 1 + r() * 1.5, 1 + r() * 1.5); } p.strokeStyle = 'rgba(120,95,70,0.07)'; for (let i = 0; i < 40; i++) { const x = r() * 512, y = r() * 512, a = r() * 6.28, l = 6 + r() * 22; p.beginPath(); p.moveTo(x, y); p.quadraticCurveTo(x + Math.cos(a) * l / 2 + 3, y + Math.sin(a) * l / 2, x + Math.cos(a) * l, y + Math.sin(a) * l); p.stroke(); } });
const TEJAS_GRANO = [11, 23, 37].map(s => teja(s, (g, r) => { g.fillStyle = '#000'; for (let i = 0; i < 6500; i++) { g.globalAlpha = .25 + r() * .6; g.fillRect(r() * 512, r() * 512, 1 + r() * 1.7, 1 + r() * 1.7); } for (let i = 0; i < 14; i++) { const x = r() * 512, y = r() * 512, rr = 20 + r() * 70, gr = g.createRadialGradient(x, y, 0, x, y, rr); gr.addColorStop(0, 'rgba(0,0,0,0.16)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.globalAlpha = 1; g.fillStyle = gr; g.fillRect(x - rr, y - rr, 2 * rr, 2 * rr); g.fillStyle = '#000'; } }));
const PAT = new Map();
function patron(x, img, key) { const k = key + (x === MAIN ? 'm' : Object.keys(CAPAS).find(n => CAPAS[n].x === x)); if (!PAT.has(k)) PAT.set(k, x.createPattern(img, 'repeat')); return PAT.get(k); }
const TRAMA_TILES = new Map();
function trama(nivel) {                                 // patrón de puntos (cobertura 0..1), girado 20° como una trama de imprenta
  const k = Math.round(clamp(nivel) * 10); if (k >= 10) return null;
  if (!TRAMA_TILES.has(k)) { const s = 10, c = document.createElement('canvas'); c.width = c.height = s; const g = c.getContext('2d'); g.fillStyle = '#000'; g.beginPath(); g.arc(s / 2, s / 2, Math.min(Math.sqrt(k / 10 * s * s / Math.PI), s * .7), 0, 7); g.fill(); TRAMA_TILES.set(k, c); }
  const p = ctx.createPattern(TRAMA_TILES.get(k), 'repeat'); p.setTransform(new DOMMatrix().rotate(20)); return p;
}

// ---------- dibujo dentro de una tinta (las funciones usan `ctx`, que apunta a la capa) ----------
function en(tinta, fn) { if (Array.isArray(tinta)) { tinta.forEach(k => en(k, fn)); return; } const prev = ctx; ctx = CAPAS[tinta].x; ctx.save(); fn(); ctx.restore(); ctx = prev; }   // una lista de tintas = sobreimpresión
function traza(pts, closed = true) { ctx.beginPath(); pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); if (closed) ctx.closePath(); }
function relleno(tinta, pts, nivel = 1) { en(tinta, () => { traza(pts); ctx.fillStyle = nivel >= 1 ? '#000' : trama(nivel); ctx.fill(); }); }
function linea(tinta, pts, w, p = 1, closed = false, nivel = 1) { if (p <= 0) return; en(tinta, () => { traza(hasta(closed ? [...pts, pts[0]] : pts, p), false); ctx.lineWidth = w; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.strokeStyle = nivel >= 1 ? '#000' : trama(nivel); ctx.stroke(); }); }
function borra(pts) { for (const k in CAPAS) { const x = CAPAS[k].x; x.save(); x.globalCompositeOperation = 'destination-out'; x.beginPath(); pts.forEach(([a, b], i) => (i ? x.lineTo(a, b) : x.moveTo(a, b))); x.closePath(); x.fillStyle = '#000'; x.fill(); x.restore(); } }
function letras(tinta, s, x, y, size, align = 'center', peso = 700) { en(tinta, () => { ctx.font = FUENTE(peso, size); ctx.textAlign = align; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = '#000'; ctx.fillText(s, x, y); }); }
function ancho(s, size, peso = 700) { MAIN.save(); MAIN.font = FUENTE(peso, size); const w = MAIN.measureText(s).width; MAIN.restore(); return w; }
function recorte(x0, y0, x1, y1, fn) { for (const k in CAPAS) { const x = CAPAS[k].x; x.save(); x.beginPath(); x.rect(x0, y0, x1 - x0, y1 - y0); x.clip(); } fn(); for (const k in CAPAS) CAPAS[k].x.restore(); }
function mover(dx, dy, fn) { for (const k in CAPAS) { CAPAS[k].x.save(); CAPAS[k].x.translate(dx, dy); } fn(); for (const k in CAPAS) CAPAS[k].x.restore(); }
function escalar(cx, cy, s, fn) { for (const k in CAPAS) { const x = CAPAS[k].x; x.save(); x.translate(cx, cy); x.scale(s, s); x.translate(-cx, -cy); } fn(); for (const k in CAPAS) CAPAS[k].x.restore(); }
function soloTinta(tinta, dx, dy, fn) { const x = CAPAS[tinta].x; x.save(); x.translate(dx, dy); fn(); x.restore(); }

// ---------- figuras: las siluetas de las láminas del #4 (DATOS.figs) separadas en tintas, con reserva ----------
function tintasDe(q, dom) {
  const t = q.tono, h = q.tinte || (t >= .2 && t < .75 ? dom : null);
  if (q.solo) return [];
  if (!h) return t < .2 ? [] : t >= .75 ? [['azul', 1]] : [['azul', .35]];
  const n = parseInt(h.slice(1), 16), r = n >> 16, g = (n >> 8) & 255, b = n & 255, mx = Math.max(r, g, b), mn = Math.min(r, g, b);
  let hue = 0; if (mx !== mn) { const d = mx - mn; hue = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4; hue = (hue * 60 + 360) % 360; }
  const oscuro = (r + g + b) / 3 < 95;
  if (oscuro) return [['azul', 1]];
  if (hue < 20 || hue >= 330) return [['rosa', 1]];                               // rojos
  if (hue < 45) return [['rosa', .8], ['amarillo', 1]];                           // naranjas y cafés
  if (hue < 70) return [['amarillo', 1]];                                         // amarillos
  if (hue < 170) return [['azul', .5], ['amarillo', 1]];                          // verdes = azul sobre amarillo
  if (hue < 260) return [['azul', t > .5 ? .8 : .45]];                            // azules
  return [['rosa', .6], ['azul', .5]];                                            // morados
}
const FIGCACHE = new Map();
function figuraPartes(nombre) {
  if (FIGCACHE.has(nombre)) return FIGCACHE.get(nombre);
  const partes = DATOS.figs[nombre].filter(q => !q.sombra), todos = partes.flatMap(q => q.pts);
  const xs = todos.map(p => p[0]), ys = todos.map(p => p[1]), cuenta = {};
  partes.forEach(q => { if (q.tinte && !q.solo) cuenta[q.tinte] = (cuenta[q.tinte] || 0) + 1; });
  const dom = Object.keys(cuenta).sort((a, b) => cuenta[b] - cuenta[a])[0];
  const v = { partes: partes.map(q => ({ pts: q.pts, solo: q.solo, tintas: tintasDe(q, dom), area: (Math.max(...q.pts.map(p => p[0])) - Math.min(...q.pts.map(p => p[0]))) * (Math.max(...q.pts.map(p => p[1])) - Math.min(...q.pts.map(p => p[1]))) })),
    cx: (Math.min(...xs) + Math.max(...xs)) / 2, cy: (Math.min(...ys) + Math.max(...ys)) / 2, h: Math.max(...ys) - Math.min(...ys), w: Math.max(...xs) - Math.min(...xs) };
  FIGCACHE.set(nombre, v); return v;
}
function figura(nombre, x, y, alto, p = 1) {
  const F = figuraPartes(nombre), s = alto / F.h, T = ([a, b]) => [x + (a - F.cx) * s, y + (b - F.cy) * s];
  const y0 = y - alto / 2 - 10, yc = y0 + (alto + 20) * easeOut(p), lag = (1 - easeOut(clamp(p * 1.4))) * 36;   // la impresión baja como el rodillo; el rosa llega tarde al registro
  const b = easeOut(clamp(p * 2.2)); if (b > 0) relleno('amarillo', circulo(x - alto * .08, y + alto * .05, F.w * s * .55 * b, alto * .5 * b), .3);
  recorte(-1e5, y0, 1e5, yc, () => {
    F.partes.forEach(q => {
      const pts = q.pts.map(T);
      if (q.solo) { if (q.area < 900) relleno('azul', pts); else linea('azul', pts, 3, 1, true); return; }
      borra(pts);
      q.tintas.forEach(([tinta, nivel]) => { if (tinta === 'rosa') soloTinta('rosa', lag, 0, () => relleno('rosa', pts, nivel)); else relleno(tinta, pts, nivel); });
      linea('azul', pts, 3.2, 1, true);
    });
  });
}
function recorteCirculo(cx, cy, r, fn) { for (const k in CAPAS) { const x = CAPAS[k].x; x.save(); x.beginPath(); x.arc(cx, cy, r, 0, Math.PI * 2); x.clip(); } fn(); for (const k in CAPAS) CAPAS[k].x.restore(); }
function persona(tipo, x, y, r, p = 1, tinta = 'rosa') {     // la silueta de perfil en azul, dentro de un círculo de color
  if (p <= 0) return; const z = back(p), G = DATOS.gente[tipo], s = r / 118, T = ([a, b]) => [x + a * .95 * s, y + (b * .95 + 4) * s];
  escalar(x, y, .4 + .6 * z, () => {
    borra(circulo(x, y, r + 3));
    relleno(tinta, circulo(x, y, r), tinta === 'amarillo' ? 1 : .6);
    recorteCirculo(x, y, r * .97, () => {
      G.partes.forEach(pp => relleno('azul', pp.map(T)));
      en('azul', () => { ctx.globalCompositeOperation = 'destination-out'; ctx.strokeStyle = '#000'; ctx.lineWidth = Math.max(3, 4 * s); ctx.lineCap = 'round'; ctx.lineJoin = 'round'; G.oro.forEach(l => { traza(l.map(T), false); ctx.stroke(); }); });
    });
    linea('azul', circulo(x, y, r), 4.5, 1, true);
  });
}

// ---------- piezas con su tiempo (las tomas las ponen en su estación) ----------
let ESTACIONES = [];
const pieza = (t, d, fn) => ({ t, d, fn });
// la palabra clave: tipo grande en azul que se imprime de arriba abajo; la copia rosa "entra en registro" desde la derecha; los números cuentan
function titulo(t, palabra, x, y, alto, o = {}) {
  const size = alto * 1.38, num = o.contar ? o.contar : null, d0 = o.desde || 0;
  return pieza(t - .05, .7, p => {
    const q = easeOut(clamp(p / .55)), r = easeOut(prog(p, .3, 1)), txt = num ? palabra.replace(String(num), String(Math.round(lerp(d0, num, easeOut(clamp(p / .8)))))) : palabra;
    const w = ancho(palabra, size), y0 = y - alto * .75;
    relleno('amarillo', caja(x - w / 2 - alto * .3, y - alto * .2, (w + alto * .6) * easeOut(prog(p, .2, .8)), alto * .55), .45);
    recorte(-1e5, y0 - alto, 1e5, y0 + (alto * 1.9) * q, () => letras('azul', txt, x, y + alto * .5, size));
    if (r > 0) soloTinta('rosa', (1 - r) * 45 + 9, 9, () => letras('rosa', txt, x, y + alto * .5, size));
  });
}
function etiqueta(t, texto, x, y, alto, o = {}) {                 // cinta amarilla con letras azules
  const size = alto * 1.25, w = ancho(texto, size, 600) + alto * 1.3, h = alto * 2.05;
  return pieza(t - .05, .45, p => { const q = easeOut(clamp(p / .5)); relleno(o.fondo || 'amarillo', caja(x - w / 2, y - h / 2, w * q, h)); if (p > .25) recorte(x - w / 2, y - h, x - w / 2 + w * easeOut(prog(p, .25, 1)), y + h, () => letras('azul', texto, x, y + size * .36, size, 'center', 600)); });
}
function nota(t, texto, x, y, alto, tinta = 'azul', o = {}) {     // tinta puede ser una lista: ['azul','amarillo'] imprime verde
  const size = alto * 1.3, w = ancho(texto, size, o.peso || 700);
  return pieza(t - .04, o.d || .45, p => recorte(-1e5, y - size * 1.2, x - w / 2 + (w + 20) * easeOut(p), y + size, () => [].concat(tinta).forEach(k => letras(k, texto, x, y + size * .36, size, 'center', o.peso || 700))));
}
// dónde queda un pedazo de un texto centrado (para tachar o encerrar una sola palabra)
function tramo(texto, parte, x, alto, peso = 700) { const size = alto * 1.3, w = ancho(texto, size, peso), i = texto.indexOf(parte), x0 = x - w / 2 + ancho(texto.slice(0, i), size, peso); return [x0, x0 + ancho(parte, size, peso)]; }
function icono(t, fig, x, y, alto, d = .6) { return pieza(t - .08, d, p => figura(fig, x, y, alto, p)); }
function gente(t, tipo, x, y, r, tinta = 'rosa') { return pieza(t - .06, .4, p => persona(tipo, x, y, r, p, tinta)); }
function trazo(t, pts, tinta = 'rosa', w = 7, d = .4, curva = true) { const s = curva && pts.length > 2 ? suave(pts) : pts; return pieza(t - .04, d, p => linea(tinta, s, w, easeOut(p))); }
function flecha(t, pts, tinta = 'rosa', w = 7, d = .45) {
  const s = suave(pts, 12);
  return pieza(t - .04, d, p => { linea(tinta, s, w, easeOut(clamp(p / .8))); if (p > .6) { const a = s[s.length - 1], b = s[Math.max(0, s.length - 6)], ang = Math.atan2(a[1] - b[1], a[0] - b[0]), L = w * 4.5 * back(prog(p, .6, 1)); relleno(tinta, [[a[0] + Math.cos(ang) * L * .4, a[1] + Math.sin(ang) * L * .4], [a[0] + Math.cos(ang + 2.5) * L, a[1] + Math.sin(ang + 2.5) * L], [a[0] + Math.cos(ang - 2.5) * L, a[1] + Math.sin(ang - 2.5) * L]]); } });
}
function lazo(t, cx, cy, rx, ry, tinta = 'rosa', d = .5) { const pts = []; for (let k = 0; k <= 50; k++) { const u = -1.9 + k / 50 * 6.7; pts.push([cx + Math.cos(u) * rx, cy + Math.sin(u) * ry]); } return pieza(t - .04, d, p => linea(tinta, pts, 7, ease(p))); }
function tachar(t, x0, x1, y, tinta = 'rosa', d = .3) { return pieza(t - .02, d, p => linea(tinta, [[x0, y + 3], [x1, y - 3]], 9, easeOut(p))); }
function tacha(t, x, y, r, tinta = 'rosa', ry = r) { const w = Math.max(9, Math.min(16, Math.min(r, ry) * .13)); return pieza(t - .02, .32, p => { linea(tinta, [[x - r, y - ry], [x + r, y + ry]], w, easeOut(clamp(p * 2))); if (p > .5) linea(tinta, [[x + r, y - ry], [x - r, y + ry]], w, easeOut(clamp(p * 2 - 1))); }); }
function chulo(t, x, y, r, tinta = 'azul') { return pieza(t - .02, .3, p => linea(tinta, [[x - r, y], [x - r * .3, y + r * .62], [x + r, y - r * .8]], Math.max(8, r * .24), easeOut(p))); }
function punteado(t, pts, tinta = 'rosa', d = .5, w = 5) { const s = suave(pts); return pieza(t - .04, d, p => en(tinta, () => { traza(hasta(s, ease(p)), false); ctx.setLineDash([16, 11]); ctx.lineWidth = w; ctx.lineCap = 'round'; ctx.strokeStyle = '#000'; ctx.stroke(); })); }
function insignia(t, texto, x, y, rot, tinta = 'rosa', alto = 40) {           // el sello de goma, en una sola tinta
  const size = alto * 1.25, w = ancho(texto, size) + alto * 1.2, h = alto * 1.9;
  return pieza(t - .08, .35, p => { if (p < .3) return; const z = 1.25 - .25 * easeOut(prog(p, .3, 1)); en(tinta, () => { ctx.translate(x, y); ctx.rotate(rot); ctx.scale(z, z); ctx.lineWidth = alto * .12; ctx.strokeStyle = '#000'; ctx.strokeRect(-w / 2, -h / 2, w, h); ctx.font = FUENTE(800, size); ctx.textAlign = 'center'; ctx.fillStyle = '#000'; ctx.fillText(texto, 0, size * .36); }); });
}
function pregunta(t, x, y, alto, tinta = 'rosa') { return pieza(t - .04, .35, p => escalar(x, y, back(p), () => letras(tinta, '?', x, y + alto * .5, alto * 1.4, 'center', 800))); }
function ejeNum(t, x0, x1, y, n = 10, tinta = 'azul', d = .5) { return pieza(t - .04, d, p => { linea(tinta, [[x0, y], [x1, y]], 4, easeOut(clamp(p / .7))); for (let k = 0; k <= n; k++) { const u = clamp((p - .2 - k / n * .5) / .2); if (u > 0) linea(tinta, [[x0 + (x1 - x0 - 30) * k / n, y - (k % 5 ? 10 : 18)], [x0 + (x1 - x0 - 30) * k / n, y + (k % 5 ? 10 : 18)]], 4, u); } if (p > .6) relleno(tinta, [[x1 + 6, y], [x1 - 20, y - 14], [x1 - 20, y + 14]]); }); }
function barra(t, x0, x1, yb, yt, tinta = 'rosa', d = .6, nivel = 1) { return pieza(t - .05, d, p => relleno(tinta, caja(x0, yb - (yb - yt) * easeOut(p), x1 - x0, (yb - yt) * easeOut(p)), nivel)); }
function medidor(tPista, tValor, cx, cy, r, valor) {     // la pista se imprime con una palabra y la aguja sube con otra
  const arco = (a0, a1, rr) => { const o = []; for (let k = 0; k <= 48; k++) { const a = a0 + (a1 - a0) * k / 48; o.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]); } return o; };
  const d = Math.max(.5, tValor - tPista + .9);
  return pieza(tPista - .05, d, p => {
    const tt = tPista - .05 + p * d;
    linea('azul', arco(Math.PI, Math.PI * 2, r), 30, easeOut(prog(tt, tPista - .05, tPista + .45)), false, .4);
    for (let k = 0; k <= 10; k++) { const a = Math.PI * (1 + k / 10), u = prog(tt, tPista + k * .03, tPista + .2 + k * .03); if (u > 0) linea('azul', [[cx + Math.cos(a) * r * .8, cy + Math.sin(a) * r * .8], [cx + Math.cos(a) * r * (k % 5 ? .7 : .64), cy + Math.sin(a) * r * (k % 5 ? .7 : .64)]], 5, u); }
    const v = valor * easeOut(prog(tt, tValor - .06, tValor + .7));
    if (v > 0) { linea('rosa', arco(Math.PI, Math.PI * (1 + v), r), 30, 1); linea('amarillo', arco(Math.PI, Math.PI * (1 + v), r), 30, 1); }
    if (tt > tValor - .06) { const a = Math.PI * (1 + v); linea('rosa', [[cx, cy], [cx + Math.cos(a) * r * .74, cy + Math.sin(a) * r * .74]], 11, 1); relleno('azul', circulo(cx, cy, 17)); }
  });
}
// un punto que aparece en t1 y viaja de x0 a x1 en t2
function punto(t1, t2, x0, x1, y, r = 15, tinta = 'rosa', dur = .6) { const d = t2 + dur - t1; return pieza(t1, d, p => { const tt = t1 + p * d, x = tt < t2 ? x0 : lerp(x0, x1, ease((tt - t2) / dur)); relleno(tinta, circulo(x, y, r * back(clamp(p * d / .25)))); }); }
// una llave (corchete) sobre un tramo, con su rótulo encima
function llave(t, x0, x1, y, texto = null, tinta = 'rosa', alto = 24) {
  const m = (x0 + x1) / 2, pts = [[x0, y], [x0, y - 16], [m - 16, y - 16], [m, y - 34], [m + 16, y - 16], [x1, y - 16], [x1, y]];
  return pieza(t - .04, .5, p => { linea(tinta, pts, 6, easeOut(clamp(p / .7))); if (texto && p > .45) recorte(-1e5, y - 34 - alto * 3, 1e5, y - 34 - alto * 3 + alto * 3 * easeOut(prog(p, .45, 1)), () => letras(tinta, texto, m, y - 46, alto * 1.3)); });
}
// ejes de una gráfica (origen abajo a la izquierda) con sus flechas
function ejes(t, x0, y0, x1, y1, tinta = 'azul', d = .5) { return pieza(t - .04, d, p => { const u = easeOut(clamp(p / .8)); linea(tinta, [[x0, y0], [x0, lerp(y0, y1, u)]], 5); linea(tinta, [[x0, y0], [lerp(x0, x1, u), y0]], 5); if (p > .7) { relleno(tinta, [[x0, y1 - 8], [x0 - 13, y1 + 16], [x0 + 13, y1 + 16]]); relleno(tinta, [[x1 + 8, y0], [x1 - 16, y0 - 13], [x1 - 16, y0 + 13]]); } }); }
// una curva (lista de puntos) que se traza; con dos tintas se sobreimprime (azul+amarillo = verde, rosa+amarillo = rojo)
function curva(t, pts, tintas = ['rosa'], w = 9, d = .6) { const s = resample(pts, 6); return pieza(t - .04, d, p => [].concat(tintas).forEach(k => linea(k, s, w, ease(p)))); }
function grafica(fn, a, b, x0, y0, sx, sy, n = 60) { const o = []; for (let k = 0; k <= n; k++) { const u = a + (b - a) * k / n; o.push([x0 + u * sx, y0 - fn(u) * sy]); } return o; }
// rayos alrededor de algo que aparece
function rayos(t, cx, cy, rx, ry, angulos, tinta = 'rosa', L = 70, w = 8) { return pieza(t - .04, .5, p => angulos.forEach((a, k) => { const u = easeOut(prog(p, k * .07, k * .07 + .45)); if (u > 0) linea(tinta, [[cx + Math.cos(a) * rx, cy + Math.sin(a) * ry], [cx + Math.cos(a) * (rx + L * u), cy + Math.sin(a) * (ry + L * u)]], w); })); }
// ondas de sonido (arcos que salen de un punto)
function ondas(t, cx, cy, tinta = 'azul', n = 3) { return pieza(t - .04, .6, p => { for (let k = 0; k < n; k++) { const u = easeOut(prog(p, k * .2, k * .2 + .5)); if (u <= 0) continue; const r = 50 + k * 45, o = []; for (let j = 0; j <= 20; j++) { const a = -.55 + 1.1 * j / 20; o.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); } linea(tinta, o, 7, u); } }); }
// una regla vertical (para "creció")
function regla(t, x, y0, y1, n = 13, tinta = 'azul') { return pieza(t - .04, .5, p => { linea(tinta, [[x, y1], [x, lerp(y1, y0, easeOut(clamp(p / .7)))]], 5); for (let k = 0; k <= n; k++) { const yy = lerp(y1, y0, k / n), u = prog(p, .15 + k / n * .5, .3 + k / n * .5); if (u > 0) linea(tinta, [[x, yy], [x + (k % 5 ? 16 : 28) * u, yy]], 4); } }); }

// ---------- más piezas (las usa Grok Bot) ----------
function cajaRedonda(x, y, w, h, r) { const o = [], seg = 7; for (const [cx, cy, a0] of [[x + w - r, y + r, -Math.PI / 2], [x + w - r, y + h - r, 0], [x + r, y + h - r, Math.PI / 2], [x + r, y + r, Math.PI]]) for (let k = 0; k <= seg; k++) { const a = a0 + k / seg * Math.PI / 2; o.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); } return o; }
const anchoBurbuja = (texto, alto) => ancho(texto, alto * 1.3) + alto * 1.6;
function burbuja(t, texto, x, y, alto = 36, o = {}) {           // globo de chat: papel con borde azul y colita
  const size = alto * 1.3, w = anchoBurbuja(texto, alto), h = alto * 2.1, c = cajaRedonda(x - w / 2, y - h / 2, w, h, h * .4);
  const cola = [[x - w * .3, y + h / 2 - 3], [x - w * .36, y + h / 2 + 24], [x - w * .14, y + h / 2 - 3]];
  return pieza(t - .05, .4, p => { const z = back(clamp(p / .7)); if (z <= 0) return; escalar(x, y, .5 + .5 * z, () => { borra(c); if (o.fondo) relleno(o.fondo, c, o.nivel || .3); linea('azul', c, 4.5, 1, true); borra(cola); linea('azul', cola, 4.5); letras(o.tinta || 'azul', texto, x, y + size * .36, size); }); });
}
function corazon(t, x, y, s, tinta = 'rosa') { const pts = []; for (let k = 0; k < 48; k++) { const u = k / 48 * Math.PI * 2; pts.push([x + s * Math.sin(u) ** 3, y - s * (13 * Math.cos(u) - 5 * Math.cos(2 * u) - 2 * Math.cos(3 * u) - Math.cos(4 * u)) / 16]); } return pieza(t - .04, .35, p => escalar(x, y, back(p), () => relleno(tinta, pts))); }
function nube(t, x, y, w, h) {                                    // círculos unidos: borde por fuera, trama por dentro
  const cs = [[-.3, .12], [-.1, -.12], [.15, -.16], [.32, .08], [.05, .18]].map(([dx, dy]) => [x + dx * w, y + dy * h, h * .42]);
  return pieza(t - .04, .45, p => escalar(x, y, .55 + .45 * back(p), () => { cs.forEach(([a, b, r]) => linea('azul', circulo(a, b, r), 9, 1, true)); cs.forEach(([a, b, r]) => borra(circulo(a, b, r - 4.5))); cs.forEach(([a, b, r]) => relleno('azul', circulo(a, b, r - 4.5), .18)); }));
}
function luna(t, x, y, r) { return pieza(t - .04, .4, p => escalar(x, y, back(p), () => { relleno('amarillo', circulo(x, y, r)); relleno('rosa', circulo(x, y, r), .3); en(['amarillo', 'rosa'], () => { ctx.globalCompositeOperation = 'destination-out'; traza(circulo(x + r * .45, y - r * .12, r * .85)); ctx.fillStyle = '#000'; ctx.fill(); }); })); }
function estrella(t, x, y, r, tinta = 'amarillo') { const pts = []; for (let k = 0; k < 8; k++) { const a = -Math.PI / 2 + k * Math.PI / 4, rr = k % 2 ? r * .34 : r; pts.push([x + Math.cos(a) * rr, y + Math.sin(a) * rr]); } return pieza(t - .04, .35, p => escalar(x, y, back(p), () => { relleno(tinta, pts); if (tinta === 'amarillo') linea('rosa', pts, 2.5, 1, true); })); }
function lupa(t, x, y, r) { return pieza(t - .04, .4, p => escalar(x, y, back(p), () => { borra(circulo(x, y, r)); relleno('azul', circulo(x, y, r), .2); linea('azul', circulo(x, y, r), Math.max(5, r * .14), 1, true); linea('azul', [[x + r * .74, y + r * .7], [x + r * 1.55, y + r * 1.5]], Math.max(8, r * .24)); linea('rosa', [[x + r * .98, y + r * .94], [x + r * 1.5, y + r * 1.45]], Math.max(4, r * .13)); })); }
function diana(t, x, y, r) { return pieza(t - .06, .5, p => [1, .78, .56, .34, .14].forEach((k, i) => { const u = back(prog(p, i * .1, i * .1 + .45)); if (u <= 0) return; const c = circulo(x, y, r * k * u); borra(c); if (i % 2 === 0) relleno(['rosa', 'amarillo'], c); })); }
function avion(t, ruta, d = .5, s = 1.1) {                        // avión de papel que vuela dejando su rastro punteado
  const R = suave(ruta, 14);
  return pieza(t - .04, d, p => {
    const parte = hasta(R, ease(p)); if (parte.length < 2) return;
    en('azul', () => { traza(parte, false); ctx.setLineDash([12, 10]); ctx.lineWidth = 3.5; ctx.strokeStyle = '#000'; ctx.stroke(); });
    const a = parte[parte.length - 1], b = parte[Math.max(0, parte.length - 4)], ang = Math.atan2(a[1] - b[1], a[0] - b[0]);
    const pts = [[34, 0], [-50, -32], [-28, 2], [-50, 32]].map(([px, py]) => [a[0] + (px * Math.cos(ang) - py * Math.sin(ang)) * s, a[1] + (px * Math.sin(ang) + py * Math.cos(ang)) * s]);
    borra(pts); relleno('rosa', pts, .5); linea('azul', pts, 3.5, 1, true); linea('azul', [pts[0], pts[2]], 2.5);
  });
}
function hoja(t, lineas, x, y, w, h, alto = 26) {                  // hoja de trabajo: título rosa y renglones azules que se escriben
  const c = cajaRedonda(x - w / 2, y - h / 2, w, h, 18), size = alto * 1.3, lh = alto * 1.8, y0 = y - (lineas.length - 1) * lh / 2;
  return pieza(t - .06, .5 + lineas.length * .12, p => { const z = easeOut(clamp(p / .4)); if (z <= 0) return; mover(0, (1 - z) * 50, () => { borra(c); relleno('amarillo', c, .22); linea('azul', c, 4, 1, true); lineas.forEach((l, i) => { const u = prog(p, .25 + i * .15, .45 + i * .15); if (u > 0) recorte(x - w / 2, -1e5, x - w / 2 + 26 + (w - 26) * easeOut(u), 1e5, () => letras(i === 0 ? 'rosa' : 'azul', l, x - w / 2 + 26, y0 + i * lh + size * .36, size, 'left')); }); }); });
}
function engranePts(cx, cy, r, n, ang) { const o = [], st = Math.PI * 2 / n; for (let k = 0; k < n; k++) { const c = ang + k * st; [[c - .36 * st, r * .8], [c - .2 * st, r], [c + .2 * st, r], [c + .36 * st, r * .8]].forEach(([a, rr]) => o.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr])); } return o; }
function engranes(t, cx, cy, s = 1, tGiro = null) {              // dos engranajes que se imprimen, giran despacio y dan un empujón con la palabra
  const r1 = 80 * s, r2 = 52 * s, x1 = cx - 45 * s, y1 = cy + 22 * s, x2 = x1 + 104 * s, y2 = y1 - 64 * s;
  return pieza(t - .06, 1000, p => {
    const e = p * 1000, tt = t - .06 + e, z = back(clamp(e / .45)); if (z <= 0) return;
    const giro = e * .5 + (tGiro != null ? ease(prog(tt, tGiro, tGiro + .7)) * Math.PI * .6 : 0);
    escalar(cx, cy, z, () => {
      const g1 = engranePts(x1, y1, r1, 10, -giro), g2 = engranePts(x2, y2, r2, 7, giro * 10 / 7 + .2);
      borra(g1); relleno('azul', g1, .5); linea('azul', g1, 4, 1, true); borra(circulo(x1, y1, r1 * .22)); linea('azul', circulo(x1, y1, r1 * .22), 4, 1, true);
      borra(g2); relleno(['rosa', 'amarillo'], g2); linea('azul', g2, 4, 1, true); borra(circulo(x2, y2, r2 * .25)); linea('azul', circulo(x2, y2, r2 * .25), 4, 1, true);
    });
  });
}
function viaje(t, texto, ruta, d = .95, alto = 24) {               // un papelito que viaja por una ruta y se queda al final
  const R = suave(ruta, 14), size = alto * 1.3, w = ancho(texto, size) + alto * 1.4, h = alto * 2;
  return pieza(t - .06, d, p => { const parte = hasta(R, ease(p)), [x, y] = parte[parte.length - 1], c = cajaRedonda(x - w / 2, y - h / 2, w, h, 10); borra(c); relleno('amarillo', c); linea('azul', c, 4, 1, true); letras('azul', texto, x, y + size * .36, size); });
}
function ficha(t, x, y, tipo, tinta, nom) {                       // tarjeta de perfil: avatar, nombre y dos renglones
  const c = cajaRedonda(x - 165, y - 75, 330, 150, 18);
  return pieza(t - .06, .45, p => { const z = easeOut(clamp(p / .6)); if (z <= 0) return; mover(0, (1 - z) * 40, () => { borra(c); linea('azul', c, 4, 1, true); persona(tipo, x - 105, y, 48, 1, tinta); letras('azul', nom, x + 40, y - 8, 30, 'center'); linea('azul', [[x - 40, y + 22], [x + 125, y + 22]], 9, 1, false, .45); linea('azul', [[x - 40, y + 48], [x + 75, y + 48]], 9, 1, false, .45); }); });
}

// ---------- el mundo: estaciones en fila y una carretera que las une ----------
const SEP = 1300;                                    // distancia entre estaciones (más que el ancho del cuadro)
const PANEO = [.25, .2];                             // la cámara arranca 0,25 s antes del corte y llega 0,2 s después
let CARRETERA = () => {};                            // lo que une a las estaciones (la define cada video)
function estacion(id, t0, piezas, marca = null) { ESTACIONES.push({ id, t0, piezas, marca, X: ESTACIONES.length * SEP }); }
function camara(t) {
  let i = 0; while (i + 1 < ESTACIONES.length && t >= ESTACIONES[i + 1].t0 - PANEO[0]) i++;
  const E = ESTACIONES[i], prev = ESTACIONES[Math.max(0, i - 1)], a = E.t0 - PANEO[0], b = E.t0 + PANEO[1];
  const fin = i + 1 < ESTACIONES.length ? ESTACIONES[i + 1].t0 - PANEO[0] : DUR;
  // frente = hasta dónde va pintada la carretera: avanza durante la frase (barra de progreso) y llega a la estación con la cámara
  if (i === 0) return { i, cx: E.X, cy: 960, k: 1 + .035 * ease(prog(t, 0, fin)), frente: E.X + 450 * prog(t, 0, fin) };
  const u = ease(prog(t, a, b)), viaje = prog(t, a, b) < 1;
  // mientras viaja: suelta el acercamiento que traía y se aleja un poquito (se ve la carretera); al llegar, vuelve a empujar despacio
  const k = viaje ? 1 + .035 * (1 - u) - .07 * Math.sin(Math.PI * prog(t, a, b)) : 1 + .035 * ease(prog(t, b, fin));
  return { i, cx: lerp(prev.X, E.X, u), cy: 960, k, frente: viaje ? lerp(prev.X + 450, E.X, u) : E.X + 450 * prog(t, b, fin) };
}
function draw(frame) {
  const t = frame / FPS, cam = camara(t);
  for (const k in CAPAS) { const x = CAPAS[k].x; x.setTransform(1, 0, 0, 1, 0, 0); x.globalCompositeOperation = 'source-over'; x.globalAlpha = 1; x.fillStyle = '#000'; x.strokeStyle = '#000'; x.setLineDash([]); x.clearRect(0, 0, W, H); x.translate(W / 2, H / 2); x.scale(cam.k, cam.k); x.translate(-cam.cx, -cam.cy); }
  const vx0 = cam.cx - W / 2 / cam.k - 50, vx1 = cam.cx + W / 2 / cam.k + 50, vy0 = cam.cy - H / 2 / cam.k - 50, vy1 = cam.cy + H / 2 / cam.k + 50;
  CARRETERA(t, vx0, vx1, cam);
  for (const E of ESTACIONES) {
    if (E.X + 600 < vx0 || E.X - 600 > vx1) continue;
    mover(E.X - 540, 0, () => { for (const q of E.piezas) if (t >= q.t) q.fn(q.d > 0 ? clamp((t - q.t) / q.d) : 1); });
  }
  // composición: papel (pegado al mundo) y cada tinta con su color, su grano y su desfase, multiplicadas
  MAIN.setTransform(1, 0, 0, 1, 0, 0); MAIN.globalCompositeOperation = 'source-over'; MAIN.globalAlpha = 1;
  MAIN.save(); MAIN.translate(W / 2, H / 2); MAIN.scale(cam.k, cam.k); MAIN.translate(-cam.cx, -cam.cy); MAIN.fillStyle = patron(MAIN, TEJA_PAPEL, 'papel'); MAIN.fillRect(vx0, vy0, vx1 - vx0, vy1 - vy0); MAIN.restore();
  let n = 0;
  for (const [nom, col] of Object.entries(TINTAS)) {
    const x = CAPAS[nom].x;
    x.setTransform(1, 0, 0, 1, 0, 0); x.globalCompositeOperation = 'source-in'; x.fillStyle = col; x.fillRect(0, 0, W, H);
    x.globalCompositeOperation = 'destination-out'; x.translate(W / 2, H / 2); x.scale(cam.k, cam.k); x.translate(-cam.cx, -cam.cy); x.fillStyle = patron(x, TEJAS_GRANO[n], 'grano' + n); x.fillRect(vx0, vy0, vx1 - vx0, vy1 - vy0);
    x.setTransform(1, 0, 0, 1, 0, 0); x.globalCompositeOperation = 'source-over';
    MAIN.globalCompositeOperation = 'multiply'; MAIN.drawImage(CAPAS[nom].c, REG[nom][0], REG[nom][1]); n++;
  }
  MAIN.globalCompositeOperation = 'source-over';
  const g = MAIN.createRadialGradient(W / 2, H * .42, W * .45, W / 2, H * .5, H * .7); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(70,50,30,0.12)'); MAIN.fillStyle = g; MAIN.fillRect(0, 0, W, H);
}
// ---------- palabras del presentador con su segundo ----------
const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9ñ]/g, '');
function tp(frase, despues = 0, fin = false) {
  const partes = frase.split(/\s+/).map(norm);
  for (let i = 0; i < WORDS.length; i++) { if (WORDS[i].s < despues - 1e-3) continue; let ok = true;
    for (let j = 0; j < partes.length; j++) { const w = WORDS[i + j]; if (!w) { ok = false; break; } const a = norm(w.w), b = norm(w.r), pp = partes[j]; if (!(a === pp || b === pp || (pp.length >= 4 && (a.startsWith(pp) || b.startsWith(pp))))) { ok = false; break; } }
    if (ok) return fin ? WORDS[i + partes.length - 1].e : WORDS[i].s; }
  throw new Error(`tp(): no encontré "${frase}" después de ${despues}`);
}
