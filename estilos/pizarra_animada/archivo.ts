// ARCHIVO · kit del estilo PIZARRA ANIMADA de reel-motion (motor AniDoodle, look "álbum de archivo") para reels explicativos.
// Sobre el kit de la lámina scrapbook (scrapbookKit.ts): una página de álbum envejecida por toma; tarjetas rasgadas
// que caen con su sombra y se pegan con cinta; grabados en buril (contorno + tramado que sigue la luz) hechos con
// cualquier silueta; siluetas de perfil para las personas (camafeos); máquina de escribir (con tildes, ñ, ¿ ¡ $ × @),
// letras recortadas tipo nota de rescate, bolígrafo rojo (flechas, lazos, chulos, tachones) y sellos de goma.
// Todo puro: rng(seed), sin reloj, sin filtros. Coordenadas lógicas 1080 x 1920.
import { Gfx, fractal, heart, rng, sample, tube, type Ctx, type Env, type Layer, type Medium, type P } from "./core";
import type { Shot } from "./film";
import { bounds, hatchRuns, inside, mix, resample, smooth } from "./gallery";
import { GLYPHS, advance, clamp01, cutLine, easeOut, engrave, fibres, glyph, handWrite, measure, occluder, path, rect, scissor, shadowOf, staged, tear, typed, type Cut, type Face, type Step } from "./scrapbookKit";

export { clamp01, easeOut, typed, handWrite, measure, staged, type Step };
export const INK = "#2a2019", NAVY = "#22335a", RED = "#b8322a", REDPEN = "#c23a2a", TEAL = "#4f8f8a", PINK = "#d9a5a0", MUSTARD = "#d6a13c", PARCH = "#e8d6b2", VERDE = "#3b7d4f", TIPO = "#221d1a";
export const PEN: Medium = { nib: 1, taper: 0.35, pressure: 0.35, retrace: false, wobble: 0.5, rough: 0.35 };
export const W = 1080, H = 1920, FPS = 30;

// ---------------------------------------------------------------- letras que faltan en la tabla (español)
type G = { l?: P[][]; c?: P[][]; w?: number };
const T = GLYPHS as Record<string, G>;
const circ = (cx: number, cy: number, r: number): P[] => Array.from({ length: 13 }, (_, i) => [cx + Math.cos((i / 12) * 6.283) * r, cy + Math.sin((i / 12) * 6.283) * r] as P);
const flip = (g: G): G => { const w = g.w ?? 4, f = (s: P[]) => s.map(([x, y]) => [w - x, 6 - y] as P); return { l: g.l?.map(f), c: g.c?.map(f), w }; };
const acute = (b: string, dx = 0): G => { const g = T[b], w = g.w ?? 4; return { ...g, l: [...(g.l ?? []), [[w / 2 - 0.3 + dx, -0.5], [w / 2 + 0.9 + dx, -1.7]]] }; };
T["Á"] = acute("A"); T["É"] = acute("E", -0.3); T["Í"] = acute("I", -0.4); T["Ó"] = acute("O"); T["Ú"] = acute("U");
T["Ñ"] = { ...T["N"], c: [[[0.4, -1.0], [1.1, -1.6], [2.1, -1.0], [2.9, -1.5], [3.6, -1.1]]] };
T["?"] = { c: [[[0.4, 1.3], [1.0, 0.2], [2.4, 0.05], [3.5, 0.9], [3.5, 2.1], [2.0, 3.1], [1.9, 4.3]]], l: [[[1.9, 5.5], [1.95, 5.95]]], w: 4 };
T["¿"] = flip(T["?"]);
T["!"] = { l: [[[1, 0], [1, 4.3]], [[1, 5.5], [1.05, 5.95]]], w: 2 };
T["¡"] = flip(T["!"]);
T["$"] = { c: T["S"].c, l: [[[2, -0.8], [2, 6.8]]], w: 4 };
T["×"] = { l: [[[0.5, 1.9], [3.3, 4.9]], [[3.3, 1.9], [0.5, 4.9]]], w: 3.8 };
T["%"] = { l: [[[0.2, 6], [3.8, 0]]], c: [circ(0.9, 1.1, 0.8), circ(3.1, 4.9, 0.8)], w: 4 };
T["@"] = { c: [[[3.6, 4.4], [3.9, 2.6], [3.2, 0.7], [1.8, 0.2], [0.5, 1.2], [0.1, 3.2], [0.7, 5.2], [2.2, 5.9], [3.6, 5.5]], circ(2.0, 3.1, 1.0)], l: [[[3.0, 2.0], [3.0, 4.2], [3.6, 4.4]]], w: 4.4 };
T['"'] = { l: [[[0.7, -0.2], [0.6, 1.5]], [[1.9, -0.2], [1.8, 1.5]]], w: 2.6 };
T["«"] = { l: [[[1.6, 1.8], [0.4, 3.2], [1.6, 4.6]], [[3.0, 1.8], [1.8, 3.2], [3.0, 4.6]]], w: 3.4 };
T["»"] = flip(T["«"]);
T["º"] = { c: [circ(1.2, 1.1, 0.9)], l: [[[0.3, 2.7], [2.1, 2.7]]], w: 2.6 };
T["→"] = { l: [[[0.2, 3.2], [4.6, 3.2]], [[3.2, 1.8], [4.6, 3.2], [3.2, 4.6]]], w: 4.8 };

// ---------------------------------------------------------------- tiempos
export type Word = { s: number; e: number; w: string; r: string };
const norm = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9ñ]/g, "");
/** segundo en que empieza la frase (como ft() de Python: prefijo de 4+ letras, buscando desde `despues`) */
export const tpOf = (WORDS: Word[]) => (frase: string, despues = 0, fin = false): number => {
  const partes = frase.split(/\s+/).map(norm);
  for (let i = 0; i < WORDS.length; i++) {
    if (WORDS[i].s < despues - 1e-3) continue;
    let ok = true;
    for (let j = 0; j < partes.length; j++) {
      const w = WORDS[i + j]; if (!w) { ok = false; break; }
      const a = norm(w.w), b = norm(w.r), p = partes[j];
      if (!(a === p || b === p || (p.length >= 4 && (a.startsWith(p) || b.startsWith(p))))) { ok = false; break; }
    }
    if (ok) return fin ? WORDS[i + partes.length - 1].e : WORDS[i].s;
  }
  throw new Error(`tp(): no encontré "${frase}" después de ${despues}`);
};

// ---------------------------------------------------------------- la página (una por toma)
export const pagina = (ctx: Ctx, env: Env, seed = 301) => {
  const r = rng(seed); ctx.setTransform(env.scale, 0, 0, env.scale, 0, 0);
  ctx.fillStyle = PARCH; ctx.fillRect(0, 0, W, H);
  for (let i = 0; i < 22; i++) { const x = r() * W, y = r() * H, R = 140 + r() * 320, gr = ctx.createRadialGradient(x, y, 0, x, y, R), col = r() < 0.55 ? "#f4e7c9" : "#caa874"; gr.addColorStop(0, col); gr.addColorStop(1, col + "00"); ctx.globalAlpha = 0.26; ctx.fillStyle = gr; ctx.fillRect(x - R, y - R, R * 2, R * 2); }
  const eg = (x0: number, y0: number, x1: number, y1: number) => { const gr = ctx.createLinearGradient(x0, y0, x1, y1); gr.addColorStop(0, "rgba(120,78,30,0.34)"); gr.addColorStop(1, "rgba(120,78,30,0)"); ctx.globalAlpha = 1; ctx.fillStyle = gr; ctx.fillRect(0, 0, W, H); };
  eg(0, 0, 60, 0); eg(W, 0, W - 70, 0); eg(0, 0, 0, 55); eg(0, H, 0, H - 90);
  ctx.globalAlpha = 0.2; ctx.strokeStyle = "#fff6df"; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(0, 1182); ctx.bezierCurveTo(300, 1178, 700, 1187, W, 1181); ctx.stroke();
  ctx.globalAlpha = 0.14; ctx.strokeStyle = "#7a5424"; ctx.lineWidth = 1.2; ctx.beginPath(); ctx.moveTo(0, 1184.5); ctx.bezierCurveTo(300, 1180.5, 700, 1189.5, W, 1183.5); ctx.stroke();
  const drift = (cx: number, cy: number, sx: number, sy: number, n: number, big: number) => { for (let i = 0; i < n; i++) { const x = cx + (r() + r() - 1) * sx, y = cy + (r() + r() - 1) * sy, s = (0.6 + r() * r() * big) * 2.2; ctx.globalAlpha = 0.16 + r() * 0.22; ctx.fillStyle = "#a4652a"; path(ctx, smooth(Array.from({ length: 7 }, (_, k) => { const a = (k / 7) * 6.28; return [x + Math.cos(a) * s * (0.8 + r() * 0.4), y + Math.sin(a) * s * (0.8 + r() * 0.4)] as P; }), true, 4)); ctx.fill(); if (s > 3) { ctx.globalAlpha *= 0.5; ctx.beginPath(); ctx.arc(x, y, s * 2.2, 0, 6.28); ctx.fill(); } } };
  drift(1045, 420, 28, 260, 40, 3); drift(50, 1150, 60, 70, 30, 4); drift(980, 70, 60, 30, 12, 2); drift(540, 1183, 200, 10, 14, 1.4);
  ctx.globalAlpha = 1;
  new Gfx(ctx, env, 0, PEN).paper("paper", 0.12); // el grano es del papel: viaja con la página
};
/** la viñeta es de la cámara, no del papel: va encima de todo, también mientras entra la página nueva */
export const vineta = (ctx: Ctx, env: Env) => { const g = new Gfx(ctx, env, 0, PEN); g.vignette("rgba(96,62,24,0.17)"); };

// ---------------------------------------------------------------- tarjetas, cinta, tiras escritas, letras recortadas, sellos
export type Card = { cx: number; cy: number; w: number; h: number; rot: number; color: string; seed: number; from: P; torn: number };
export const tarjeta = (cx: number, cy: number, w: number, h: number, rot = 0, seed = 1, color = "#f2eadb", from: P = [0, 70], torn = 2.4): Card => ({ cx, cy, w, h, rot, color, seed, from, torn });
export const toPage = (cd: Card, [x, y]: P, dx = 0, dy = 0): P => { const c = Math.cos(cd.rot), s = Math.sin(cd.rot); return [cd.cx + dx + x * c - y * s, cd.cy + dy + x * s + y * c]; };
export const cardXf = (c: Ctx, env: Env, cd: Card) => { c.setTransform(env.scale, 0, 0, env.scale, 0, 0); c.translate(cd.cx, cd.cy); c.rotate(cd.rot); };
const cardShape = (cd: Card) => tear(rect(cd.w, cd.h), cd.torn, cd.seed);
export const drawCard = (ctx: Ctx, env: Env, cd: Card, p: number, cintas = true) => {
  if (p <= 0) return;
  const e = easeOut(p), dx = cd.from[0] * (1 - e), dy = cd.from[1] * (1 - e), lift = 1 + 6 * (1 - e) * (1 - e);
  const g = new Gfx(ctx, env, 0, PEN), sh = cardShape(cd).map((q) => toPage(cd, q, dx, dy));
  shadowOf(g, [sh], [2.5 * lift, 4 * lift], 3 + 2.5 * lift, 0.34 / Math.sqrt(lift));
  ctx.setTransform(env.scale, 0, 0, env.scale, 0, 0);
  ctx.fillStyle = cd.color; path(ctx, sh); ctx.fill();
  fibres(ctx, sh, cd.color, cd.seed + 5, 0.8, 0.28);
  ctx.strokeStyle = mix(cd.color, "#7a5a30", 0.35); ctx.globalAlpha = 0.35; ctx.lineWidth = 1.2; path(ctx, sh); ctx.stroke(); ctx.globalAlpha = 1;
  if (cintas && p > 0.7) {
    const q = clamp01((p - 0.7) / 0.3);
    cinta(ctx, env, toPage(cd, [-cd.w / 2 + 18, -cd.h / 2 + 14]), -0.72 + cd.rot, Math.min(110, cd.w * 0.3), q, cd.seed + 40);
    cinta(ctx, env, toPage(cd, [cd.w / 2 - 18, -cd.h / 2 + 14]), 0.7 + cd.rot, Math.min(110, cd.w * 0.3), q, cd.seed + 41);
  }
};
export const cinta = (ctx: Ctx, env: Env, at: P, ang: number, len: number, p: number, seed: number) => {
  if (p <= 0) return; const r = rng(seed), L = len * easeOut(p), h = 32, c = Math.cos(ang), s = Math.sin(ang), Tf = ([x, y]: P): P => [at[0] + x * c - y * s, at[1] + x * s + y * c];
  const top: P[] = [], bot: P[] = []; for (let k = 0; k <= 5; k++) top.push([-len / 2 + (r() - 0.5) * 3, -h / 2 + (k * h) / 5]);
  const endX = -len / 2 + L; for (let k = 5; k >= 0; k--) bot.push([endX + (k % 2 ? 3 : -2) * (p >= 1 ? 1 : 0), -h / 2 + (k * h) / 5]);
  const sh = [...top, ...bot].map(Tf); ctx.setTransform(env.scale, 0, 0, env.scale, 0, 0);
  const g = new Gfx(ctx, env, 0, PEN); shadowOf(g, [sh], [1, 1.5], 1.5, 0.12); ctx.setTransform(env.scale, 0, 0, env.scale, 0, 0);
  ctx.globalAlpha = 0.5; ctx.fillStyle = "#efe0a8"; path(ctx, sh); ctx.fill();
  ctx.globalAlpha = 0.28; ctx.fillStyle = "#fffbe8"; path(ctx, ([[-len / 2 + 4, -h / 2 + 4], [endX - 4, -h / 2 + 4], [endX - 4, -h / 2 + 8], [-len / 2 + 4, -h / 2 + 9]] as P[]).map(Tf)); ctx.fill();
  ctx.globalAlpha = 1;
};

const TW: Face = { weight: 0.1, mono: 4.2, track: 0.9 };
export type Strip = { text: string; x: number; y: number; cap: number; rot: number; color: string; seed: number };
export const tira = (text: string, x: number, y: number, cap = 40, rot = 0, seed = 1, color = "#f7f2e8"): Strip => ({ text, x, y, cap, rot, color, seed });
const stripShape = (st: Strip): P[] => { const w = measure(st.text, st.cap, TW) + st.cap * 1.6, h = st.cap * 2.3; return tear(rect(w, h), 1.2, st.seed); };
/** tira de papel que cae y se escribe a máquina (p: la tira; n: letras ya escritas) */
export const drawStrip = (ctx: Ctx, env: Env, st: Strip, p: number, n = Infinity, color = TIPO) => {
  if (p <= 0) return; const e = easeOut(p), lift = 1 + 4 * (1 - e) * (1 - e), dy = -14 * (1 - e), c = Math.cos(st.rot), s = Math.sin(st.rot), Tf = ([x, y]: P): P => [st.x + x * c - y * s, st.y + dy + x * s + y * c], sh = stripShape(st).map(Tf);
  const g = new Gfx(ctx, env, 0, PEN); shadowOf(g, [sh], [1.5 * lift, 2.5 * lift], 1.5 + lift, 0.36 / Math.sqrt(lift));
  ctx.setTransform(env.scale, 0, 0, env.scale, 0, 0); ctx.fillStyle = st.color; path(ctx, sh); ctx.fill(); fibres(ctx, sh, st.color, st.seed, 0.6, 0.15);
  if (n > 0) { ctx.translate(st.x, st.y + dy); ctx.rotate(st.rot); const w = measure(st.text, st.cap, TW); typed(ctx, st.text, -w / 2, -st.cap / 2, st.cap, color, st.seed, n); }
};
/** texto a máquina directo sobre la página o una tarjeta, centrado en x */
export const escribir = (ctx: Ctx, env: Env, text: string, x: number, y: number, cap: number, p: number, seed = 1, color = TIPO, rot = 0) => {
  if (p <= 0) return; ctx.setTransform(env.scale, 0, 0, env.scale, 0, 0); ctx.translate(x, y); ctx.rotate(rot);
  const w = measure(text, cap, TW); typed(ctx, text, -w / 2, -cap / 2, cap, color, seed, p >= 1 ? Infinity : Math.floor(p * text.length + 0.999));
};

type Tile = { ch: string; x: number; y: number; cap: number; face: Face; bg: string; fg: string; rot: number; seed: number; news: boolean };
const FACES: Face[] = [{ weight: 0.2 }, { weight: 0.15, serif: 0.9 }, { weight: 0.12, outline: "" }, { weight: 0.14, slant: 0.22 }, { weight: 0.075, serif: 0.7, wide: 0.78 }, { weight: 0.17, wide: 1.25 }, { weight: 0.16, cap: "round", join: "round" }, { weight: 0.11, serif: 1.0, slant: 0.12 }];
const PAIRS: [string, string][] = [[NAVY, "#f3ead6"], [TEAL, "#1c1a18"], ["#f1e9d8", "#1c1a18"], [PINK, NAVY], [RED, "#f6ecd9"], [MUSTARD, "#1c1a18"], ["#d8d2c4", "#1c1a18"], ["#1d1b19", "#efe6d0"], ["#e9c9b4", RED]];
const gw = (ch: string, cap: number, face: Face) => ((T[ch]?.w ?? 4) * (face.wide ?? 1) + 6 * (face.slant ?? 0)) * (cap / 6);
/** palabra en letras recortadas, centrada en cx (los espacios dejan hueco) */
export const ransom = (word: string, cx: number, y0: number, capBase: number, seed: number): Tile[] => {
  const r = rng(seed), out: Tile[] = []; let x = 0, lastP = -1, lastF = -1;
  [...word].forEach((ch, i) => {
    if (ch === " ") { x += capBase * 0.55; return; }
    let pi = Math.floor(r() * PAIRS.length); if (pi === lastP) pi = (pi + 3) % PAIRS.length; let fi = Math.floor(r() * FACES.length); if (fi === lastF) fi = (fi + 2) % FACES.length; lastP = pi; lastF = fi;
    const [bg, fg] = PAIRS[pi], face = { ...FACES[fi] }; if (face.outline !== undefined) face.outline = bg;
    const cap = capBase * (0.84 + r() * 0.3), w = gw(ch, cap, face) + cap * (0.5 + r() * 0.25);
    out.push({ ch, x: x + w / 2, y: y0 + (r() - 0.5) * capBase * 0.22, cap, face, bg, fg, rot: (r() - 0.5) * 0.2, seed: seed * 10 + i, news: r() < 0.4 });
    x += w + 3 + r() * 6;
  });
  const off = cx - x / 2; out.forEach((t) => (t.x += off));
  return out;
};
const tileShape = (t: Tile): P[] => { const r = rng(t.seed), w = gw(t.ch, t.cap, t.face) + t.cap * 0.55, h = t.cap * (1.5 + r() * 0.2); return scissor([[-w / 2 + (r() - 0.5) * 4, -h / 2 + (r() - 0.5) * 4], [w / 2 + (r() - 0.5) * 4, -h / 2 + (r() - 0.5) * 4], [w / 2 + (r() - 0.5) * 4, h / 2 + (r() - 0.5) * 4], [-w / 2 + (r() - 0.5) * 4, h / 2 + (r() - 0.5) * 4]], t.seed, 0.8); };
export const drawTile = (ctx: Ctx, env: Env, t: Tile, p: number) => {
  if (p <= 0) return; const e = easeOut(p), lift = 1 + 5 * (1 - e) * (1 - e), dx = -6 * (1 - e), dy = -12 * (1 - e), rot = t.rot + 0.25 * (1 - e) * (t.seed % 2 ? 1 : -1);
  const c = Math.cos(rot), s = Math.sin(rot), Tf = ([x, y]: P): P => [t.x + dx + x * c - y * s, t.y + dy + x * s + y * c], sh = tileShape(t).map(Tf);
  const g = new Gfx(ctx, env, 0, PEN); shadowOf(g, [sh], [1.5 * lift, 2.5 * lift], 1.5 + lift, 0.4 / Math.sqrt(lift));
  ctx.setTransform(env.scale, 0, 0, env.scale, 0, 0); ctx.fillStyle = t.bg; path(ctx, sh); ctx.fill(); fibres(ctx, sh, t.bg, t.seed, 0.6, 0.18);
  ctx.translate(t.x + dx, t.y + dy); ctx.rotate(rot);
  if (t.news) { const r = rng(t.seed + 9), b = bounds(tileShape(t)); ctx.save(); path(ctx, tileShape(t)); ctx.clip(); ctx.globalAlpha = 0.3; ctx.fillStyle = t.fg; for (let y = b.y0 + 3; y < b.y1; y += 5) { let x = b.x0 + 2; while (x < b.x1) { const l = 3 + r() * 14; ctx.fillRect(x, y, l, 1.4); x += l + 3; } } ctx.restore(); ctx.globalAlpha = 0.8; ctx.fillStyle = t.bg; const ww = measure(t.ch, t.cap, t.face); ctx.fillRect(-ww / 2 - t.cap * 0.12, -t.cap * 0.62, ww + t.cap * 0.24, t.cap * 1.24); ctx.globalAlpha = 1; }
  glyph(ctx, t.ch, -gw(t.ch, t.cap, t.face) / 2, -t.cap / 2, t.cap, t.face, t.fg);
};
/** dibuja las letras recortadas una por una dentro de la ventana p (0..1): cada una cae en su turno */
export const drawRansom = (ctx: Ctx, env: Env, tiles: Tile[], p: number) => {
  const n = tiles.length, dd = Math.min(0.55, 2.4 / (n + 1.4));
  tiles.forEach((t, i) => drawTile(ctx, env, t, p >= 1 ? 1 : clamp01((p - (n > 1 ? ((1 - dd) * i) / (n - 1) : 0)) / dd)));
};

/** sello de goma: baja (p < 0.35 todavía en el aire), golpea y el entintado se asienta */
export const sello = (ctx: Ctx, env: Env, x: number, y: number, rot: number, big: string, small: string, p: number, color = RED, cap = 40) => {
  if (p < 0.35) return;
  const bigF: Face = { weight: 0.17, serif: 0.6, wide: 1.05, track: 1.5 }, smF: Face = { weight: 0.11, track: 1.6 };
  const tw = measure(big, cap, bigF), sw = small ? measure(small, cap * 0.42, smF) : 0, w = Math.max(tw, sw) + cap * 1.5, h = cap * (small ? 2.6 : 2.0);
  const g = new Gfx(ctx, env, 0, PEN), k = 1.1 - 0.1 * easeOut((p - 0.35) / 0.65);
  g.group("plain", () => {
    const c = g.cur; c.save(); c.translate(x, y); c.rotate(rot); c.scale(k, k);
    c.strokeStyle = color; c.lineWidth = cap * 0.12; c.strokeRect(-w / 2, -h / 2, w, h); c.lineWidth = cap * 0.045; c.strokeRect(-w / 2 + cap * 0.22, -h / 2 + cap * 0.22, w - cap * 0.44, h - cap * 0.44);
    let cx = -tw / 2; [...big].forEach((ch) => { glyph(c, ch, cx, small ? -h / 2 + cap * 0.42 : -cap / 2, cap, bigF, color); cx += advance(ch, bigF) * (cap / 6); });
    if (small) { const sc = cap * 0.42; cx = -sw / 2; [...small].forEach((ch) => { glyph(c, ch, cx, h / 2 - sc - cap * 0.38, sc, smF, color); cx += advance(ch, smF) * (sc / 6); }); }
    c.restore(); g.touch(x - w, y - w, x + w, y + w);
  }, { textures: ["risoSpeck", "risoMottle"], blend: "multiply", alpha: 0.88 });
};

// ---------------------------------------------------------------- bolígrafo (rojo, azul) y lápiz de color
export const pluma = (ctx: Ctx, env: Env) => new Gfx(ctx, env, 0, PEN);
export const trazo = (g: Gfx, pts: P[], color: string, w: number, p: number, seed: number, taper = 0.4, curva = true) => {
  if (p <= 0) return; g.pen(curva && pts.length > 2 ? smooth(pts, false, 8) : pts, { w, color, seed, wobble: 0.35, boil: 0, taper, opacity: 0.95, retrace: false, progress: p });
};
export const punteado = (g: Gfx, pts: P[], color: string, w: number, p: number, seed: number, on = 12, off = 9) => {
  const s0 = smooth(pts, false, 8); let L0 = 0; for (let i = 1; i < s0.length; i++) L0 += Math.hypot(s0[i][0] - s0[i - 1][0], s0[i][1] - s0[i - 1][1]);
  const s = resample(s0, Math.max(2, Math.round(L0 / 3))); let L = 0; const acc = [0]; for (let i = 1; i < s.length; i++) { L += Math.hypot(s[i][0] - s[i - 1][0], s[i][1] - s[i - 1][1]); acc.push(L); }
  const lim = L * p; let a = 0;
  while (a < lim) { const b = Math.min(a + on, lim), seg = s.filter((_, i) => acc[i] >= a && acc[i] <= b); if (seg.length > 1) g.pen(seg, { w, color, seed: seed + Math.floor(a), wobble: 0.2, boil: 0, taper: 0.2, opacity: 0.95, retrace: false }); a += on + off; }
};
export const flecha = (g: Gfx, pts: P[], color: string, w: number, p: number, seed: number) => {
  const s = smooth(pts, false, 10); trazo(g, s, color, w, clamp01(p / 0.85), seed, 0.3, false);
  if (p > 0.85) { const q = clamp01((p - 0.85) / 0.15), a = s[s.length - 1], b = s[Math.max(0, s.length - 8)], dx = a[0] - b[0], dy = a[1] - b[1], l = Math.hypot(dx, dy) || 1, ux = dx / l, uy = dy / l, hd = w * 7;
    g.pen([[a[0] - ux * hd - uy * hd * 0.6, a[1] - uy * hd + ux * hd * 0.6], a, [a[0] - ux * hd + uy * hd * 0.6, a[1] - uy * hd - ux * hd * 0.6]], { w, color, seed: seed + 3, wobble: 0.2, boil: 0, taper: 0.3, opacity: 0.95, retrace: false, progress: q }); }
};
export const lazo = (g: Gfx, cx: number, cy: number, rx: number, ry: number, color: string, w: number, p: number, seed: number) => {
  const pts: P[] = []; for (let k = 0; k <= 30; k++) { const u = -0.5 + (k / 30) * 6.9, rr = 1 + k * 0.004; pts.push([cx + Math.cos(u) * rx * rr, cy + Math.sin(u) * ry * rr]); }
  g.pen(pts, { w, color, seed, wobble: 0.6, boil: 0, taper: 0.6, opacity: 0.95, retrace: false, progress: p });
};
export const subraya = (g: Gfx, x0: number, x1: number, y: number, color: string, w: number, p: number, seed: number, ondas = false) => {
  const pts: P[] = []; for (let k = 0; k <= 16; k++) { const u = k / 16; pts.push([x0 + (x1 - x0) * u, y + (ondas ? Math.sin(u * 12.5) * 6 : (u - 0.5) * 4)]); }
  g.pen(pts, { w, color, seed, wobble: 0.3, boil: 0, taper: 0.5, opacity: 0.95, retrace: false, progress: p });
};
export const chulo = (g: Gfx, x: number, y: number, r: number, p: number, seed: number, color = VERDE) => {
  g.pen([[x - r, y - r * 0.05], [x - r * 0.32, y + r * 0.62], [x + r, y - r * 0.85]], { w: r * 0.16, color, seed, wobble: 0.3, boil: 0, taper: 0.4, opacity: 0.95, retrace: false, progress: p });
};
export const tacha = (g: Gfx, x: number, y: number, r: number, p: number, seed: number, color = REDPEN) => {
  const w = Math.max(3, r * 0.13);
  g.pen([[x - r, y - r], [x + r, y + r]], { w, color, seed, wobble: 0.4, boil: 0, taper: 0.4, opacity: 0.95, retrace: false, progress: clamp01(p * 2) });
  if (p > 0.5) g.pen([[x + r, y - r * 1.05], [x - r * 0.95, y + r]], { w, color, seed: seed + 1, wobble: 0.4, boil: 0, taper: 0.4, opacity: 0.95, retrace: false, progress: clamp01(p * 2 - 1) });
};
export const tachar = (g: Gfx, x0: number, x1: number, y: number, p: number, seed: number, color = REDPEN, w = 5) => {
  g.pen([[x0, y + 3], [(x0 + x1) / 2, y - 2], [x1, y + 2]], { w, color, seed, wobble: 0.4, boil: 0, taper: 0.3, opacity: 0.95, retrace: false, progress: p });
};
export const mano = (g: Gfx, text: string, x: number, y: number, cap: number, p: number, seed: number, color = REDPEN, w = 3.2) => {
  const est = [...text].reduce((a, ch) => a + ((T[ch]?.w ?? 4) * 0.92 + 1.1), 0) * (cap / 6); handWrite(g, text, x - est / 2, y - cap / 2, cap, color, seed, p, 0.2, w);
};

// ---------------------------------------------------------------- grabados en buril (cualquier silueta)
export type Parte = { pts: P[]; tono?: number; ang?: number; esp?: number; cruz?: number; tinte?: string; alfa?: number; borde?: number; wmax?: number; solo?: boolean };
export type Grabado = { cortes: Cut[]; tintes: { pts: P[]; color: string; alfa: number }[] };
/** contorno (más grueso del lado de la sombra) + tramado que engorda con el tono y se corta en las luces;
 *  las partes de adelante tapan las líneas de las de atrás (como el kit de la lámina). luz: hacia dónde está la lámpara */
export const grabar = (partes: Parte[], seed = 1, luz: P = [-0.55, -0.83]): Grabado => {
  const contornos: Cut[] = [], tramas: Cut[] = [], cruces: Cut[] = [], tintes: Grabado["tintes"] = [];
  partes.forEach((pt, i) => {
    const occ = partes.slice(i + 1).filter((q) => !q.solo).map((q) => occluder(q.pts));
    const b = bounds(pt.pts), cx = (b.x0 + b.x1) / 2, cy = (b.y0 + b.y1) / 2, R = Math.max(12, Math.hypot(b.x1 - b.x0, b.y1 - b.y0) / 2);
    const tono = pt.tono ?? 0.38, wmax = pt.wmax ?? 2.3, borde = pt.borde ?? 2.1;
    const tone = (x: number, y: number) => clamp01(tono + 0.42 * (((x - cx) * -luz[0] + (y - cy) * -luz[1]) / R));
    const ring = [...pt.pts, pt.pts[0]];
    contornos.push(cutLine(ring, (x, y) => { const nx = x - cx, ny = y - cy, l = Math.hypot(nx, ny) || 1, sh = Math.max(0, (nx * -luz[0] + ny * -luz[1]) / l); return borde * (0.7 + 0.9 * sh); }, occ, 2));
    if (pt.solo) return;
    const ang = pt.ang ?? 0.62, esp = pt.esp ?? 5.3;
    hatchRuns(b, ang, esp, (x, y) => inside(pt.pts, x, y), 2.5, seed + i * 7).forEach((run) => tramas.push(cutLine(run, (x, y) => { const t = tone(x, y); return t < 0.2 ? 0 : wmax * Math.pow((t - 0.2) / 0.8, 0.85); }, occ, 2)));
    const cz = pt.cruz ?? 0.62;
    if (cz < 1) hatchRuns(b, ang + 1.15, esp * 1.1, (x, y) => inside(pt.pts, x, y), 2.5, seed + i * 7 + 3).forEach((run) => cruces.push(cutLine(run, (x, y) => { const t = tone(x, y); return t < cz ? 0 : wmax * 0.85 * Math.pow((t - cz) / (1 - cz), 0.8); }, occ, 2)));
    if (pt.tinte) tintes.push({ pts: pt.pts, color: pt.tinte, alfa: pt.alfa ?? 0.38 });
  });
  return { cortes: [...contornos, ...tramas, ...cruces], tintes };
};
const cache = <V>(env: Env, key: string, fn: () => V): V => { let v = env.cache.get(key) as V | undefined; if (v === undefined) { v = fn(); env.cache.set(key, v); } return v; };
/** el grabado se corta línea por línea (contornos, tramado, cruces: p 0..0.78) y después se colorea a mano con una
 *  pasada de pincel de izquierda a derecha (0.7..1) */
export const drawGrabado = (ctx: Ctx, env: Env, key: string, partes: () => Parte[], x: number, y: number, s: number, rot: number, p: number, seed = 1) => {
  if (p <= 0) return; const gr = cache(env, `archivo:gr:${key}:${seed}`, () => grabar(partes(), seed));
  const xf = () => { ctx.setTransform(env.scale, 0, 0, env.scale, 0, 0); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); };
  const pt = clamp01((p - 0.7) / 0.3);
  if (pt > 0 && gr.tintes.length) {
    const b = bounds(gr.tintes.flatMap((t) => t.pts)); xf(); ctx.save(); ctx.beginPath(); ctx.rect(b.x0 - 12, b.y0 - 12, (b.x1 - b.x0 + 24) * (pt >= 1 ? 1 : easeOut(pt)), b.y1 - b.y0 + 24); ctx.clip();
    ctx.globalCompositeOperation = "multiply"; gr.tintes.forEach((t) => { ctx.globalAlpha = t.alfa; ctx.fillStyle = t.color; path(ctx, t.pts); ctx.fill(); });
    ctx.restore(); ctx.globalAlpha = 1; ctx.globalCompositeOperation = "source-over";
  }
  xf(); engrave(ctx, gr.cortes, clamp01(p / 0.78), INK, 0.16 / Math.max(0.5, s));
};
/** sombra proyectada en líneas horizontales (el piso del grabado) */
export const sombraSuelo = (x0: number, x1: number, y: number, filas = 4): Parte => ({ pts: [[x0, y - 3], [x1, y - 3], [x1 - 14, y + filas * 6], [x0 + 14, y + filas * 6]], tono: 0.55, ang: 0, esp: 6, cruz: 1, borde: 0.01 });

// ---------------------------------------------------------------- figuras (coordenadas locales, ~300 px)
const R2 = (x0: number, y0: number, x1: number, y1: number): P[] => [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];
const OV = (cx: number, cy: number, rx: number, ry: number, n = 36, a0 = 0): P[] => Array.from({ length: n }, (_, i) => { const a = a0 + (i / n) * 6.283; return [cx + Math.cos(a) * rx, cy + Math.sin(a) * ry] as P; });
const RR = (x0: number, y0: number, x1: number, y1: number, r: number): P[] => { const out: P[] = []; const cs: [number, number, number][] = [[x1 - r, y0 + r, -1.571], [x1 - r, y1 - r, 0], [x0 + r, y1 - r, 1.571], [x0 + r, y0 + r, 3.142]]; cs.forEach(([cx, cy, a0]) => { for (let k = 0; k <= 6; k++) { const a = a0 + (k / 6) * 1.571; out.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); } }); return out; };
const S = (pts: P[]) => smooth(pts, true, 6);

export const FIG: Record<string, () => Parte[]> = {
  // caballo de tiro de perfil (mirando a la derecha), de pie: pata trasera con babilla adelante y corvejón atrás,
  // mano casi recta con rodilla, cuello arqueado con crin, cabeza en cuña con hocico (referencia: lámina de anatomía equina)
  caballo: () => {
    const leg = (pts: P[], r0: number, r1: number): P[] => tube(pts, r0, r1, false);
    return [
      sombraSuelo(-170, 150, 4),
      { pts: leg([[-100, -116], [-80, -86], [-108, -54], [-112, -18], [-114, -2]], 17, 6.5), tono: 0.66, ang: 1.38 },
      { pts: leg([[60, -104], [66, -52], [70, -18], [72, -2]], 13, 6.5), tono: 0.66, ang: 1.38 },
      { pts: S([[-132, -152], [-150, -148], [-166, -120], [-174, -78], [-162, -40], [-150, -46], [-154, -86], [-144, -120], [-128, -134]]), tono: 0.62, ang: 1.25, tinte: "#6b4428", alfa: 0.3 },
      { pts: S([[70, -166], [36, -172], [-10, -158], [-60, -162], [-110, -172], [-138, -152], [-144, -118], [-128, -92], [-90, -84], [-40, -78], [10, -80], [52, -88], [80, -112], [88, -142]]), tono: 0.36, ang: 0.62, tinte: "#b9773b", alfa: 0.32 },
      { pts: S([[42, -164], [64, -196], [92, -230], [118, -252], [140, -240], [144, -212], [126, -186], [104, -160], [90, -138], [70, -146]]), tono: 0.34, ang: 1.0, tinte: "#b9773b", alfa: 0.32 },
      { pts: S([[114, -254], [132, -264], [150, -258], [172, -228], [194, -198], [201, -182], [193, -169], [175, -167], [157, -177], [141, -197], [128, -220]]), tono: 0.3, ang: 0.5, tinte: "#b9773b", alfa: 0.32 },
      { pts: [[124, -257], [129, -286], [141, -259]], tono: 0.45 },
      { pts: S([[38, -166], [58, -202], [86, -238], [114, -264], [126, -254], [100, -226], [76, -194], [58, -164]]), tono: 0.78, ang: 1.2, tinte: "#4a2e1c", alfa: 0.32 },
      { pts: leg([[-88, -122], [-64, -88], [-90, -54], [-92, -18], [-90, -2]], 21, 7), tono: 0.42, ang: 1.38 },
      { pts: leg([[44, -100], [48, -72], [50, -48], [51, -20], [53, -2]], 15, 7), tono: 0.42, ang: 1.38 },
      { pts: R2(-100, -9, -80, 2), tono: 0.85, solo: true }, { pts: R2(43, -9, 63, 2), tono: 0.85, solo: true },
      { pts: OV(158, -232, 4.5, 4, 10), tono: 0.95, solo: true }, { pts: OV(191, -186, 3, 2.5, 8), tono: 0.95, solo: true },
    ];
  },
  carro: () => {
    const rueda = (cx: number): Parte[] => [{ pts: OV(cx, -44, 44, 44), tono: 0.78, cruz: 0.7 }, { pts: OV(cx, -44, 30, 30), tono: 0.12, cruz: 1 },
      ...Array.from({ length: 10 }, (_, k): Parte => { const a = (k / 10) * 6.283, c = Math.cos(a), s = Math.sin(a); return { pts: [[cx + c * 9 - s * 1.2, -44 + s * 9 + c * 1.2], [cx + c * 29 - s * 1.6, -44 + s * 29 + c * 1.6], [cx + c * 29 + s * 1.6, -44 + s * 29 - c * 1.6], [cx + c * 9 + s * 1.2, -44 + s * 9 - c * 1.2]], tono: 0.7, solo: true, borde: 1.1 }; }),
      { pts: OV(cx, -44, 9, 9), tono: 0.7, solo: true }];
    return [
      sombraSuelo(-170, 180, 2),
      { pts: R2(-150, -128, 160, -82), tono: 0.42, tinte: "#b23a2c", alfa: 0.34 },
      { pts: R2(-140, -232, -12, -128), tono: 0.6, ang: 1.2, tinte: "#3a2a24", alfa: 0.2 },
      { pts: R2(-150, -246, 4, -230), tono: 0.75 },
      { pts: R2(-124, -214, -36, -150), tono: 0.08, cruz: 1, tinte: "#9fc3d8", alfa: 0.35 },
      { pts: R2(-12, -168, 132, -128), tono: 0.4, ang: 0.2, tinte: "#b23a2c", alfa: 0.34 },
      { pts: R2(132, -178, 156, -122), tono: 0.66 },
      { pts: S([[-150, -96], [-140, -126], [-96, -132], [-56, -120], [-48, -92]]), tono: 0.7 },
      { pts: S([[52, -92], [66, -124], [110, -132], [150, -120], [158, -92]]), tono: 0.7 },
      ...rueda(-96), ...rueda(104),
      { pts: OV(162, -152, 11, 11, 14), tono: 0.12, cruz: 1, tinte: "#e6c35a", alfa: 0.5 },
    ];
  },
  caracol: () => [
    sombraSuelo(-150, 150, 3),
    { pts: S([[-160, 0], [-140, -36], [40, -46], [80, -110], [120, -130], [150, -96], [126, -20], [104, 0]]), tono: 0.3, ang: 0.3, tinte: "#b9c98a", alfa: 0.35 },
    { pts: R2(108, -196, 116, -122), tono: 0.6, solo: true }, { pts: R2(134, -192, 142, -118), tono: 0.6, solo: true },
    { pts: OV(-30, -118, 98, 92), tono: 0.42, ang: 0.9, tinte: "#d98a3a", alfa: 0.36 },
    { pts: Array.from({ length: 60 }, (_, k) => { const t = (k / 59) * 4.2 * Math.PI, rr = 80 - k * 1.25; return [-30 + Math.cos(t) * rr, -118 + Math.sin(t) * rr * 0.94] as P; }), tono: 0.5, solo: true, borde: 1.4 },
    { pts: OV(112, -198, 7, 7, 10), tono: 0.9, solo: true }, { pts: OV(138, -194, 7, 7, 10), tono: 0.9, solo: true },
  ],
  reloj: () => {
    const out: Parte[] = [{ pts: R2(-8, -128, 8, -100), tono: 0.6 }, { pts: OV(0, -142, 16, 16, 18), tono: 0.55, solo: true }, { pts: OV(0, 0, 100, 100), tono: 0.5, ang: 0.8, tinte: "#c9a24a", alfa: 0.36 }, { pts: OV(0, 0, 84, 84), tono: 0.06, cruz: 1 }];
    for (let k = 0; k < 12; k++) { const a = (k / 12) * 6.283, r0 = k % 3 ? 72 : 62; out.push({ pts: [[Math.sin(a) * r0, -Math.cos(a) * r0], [Math.sin(a) * 80, -Math.cos(a) * 80], [Math.sin(a) * 80 + 0.5, -Math.cos(a) * 80], [Math.sin(a) * r0 + 0.5, -Math.cos(a) * r0]], tono: 0.9, solo: true, borde: k % 3 ? 1.6 : 2.6 }); }
    out.push({ pts: [[-4, 4], [-30, -40], [-26, -44], [4, -4]], tono: 0.9, solo: true, borde: 2.4 }, { pts: [[-3, 3], [52, -18], [54, -13], [3, 4]], tono: 0.9, solo: true, borde: 2 });
    return out;
  },
  celular: () => [
    { pts: RR(-96, -176, 96, 176, 28), tono: 0.66, ang: 0.8, tinte: "#2c3446", alfa: 0.25 },
    { pts: RR(-80, -146, 80, 150, 12), tono: 0.1, cruz: 1, tinte: "#a9d4e6", alfa: 0.42 },
    { pts: RR(-30, -166, 30, -154, 6), tono: 0.9, solo: true },
    { pts: S([[-50, -110], [-60, -60], [-56, -40]]), tono: 0.05, solo: true, borde: 0.8 },
  ],
  mundo: () => [
    { pts: OV(0, 0, 150, 150, 48), tono: 0.4, ang: 0.75, tinte: "#7fb3c9", alfa: 0.4 },
    { pts: S([[-110, -80], [-60, -118], [-20, -96], [-40, -50], [-90, -30], [-120, -50]]), tono: 0.6, ang: 0.3, tinte: "#8fae6a", alfa: 0.45 },
    { pts: S([[10, -60], [70, -84], [112, -40], [96, 30], [50, 60], [30, 20]]), tono: 0.6, ang: 0.3, tinte: "#8fae6a", alfa: 0.45 },
    { pts: S([[-70, 50], [-20, 40], [0, 96], [-40, 120], [-80, 90]]), tono: 0.6, ang: 0.3, tinte: "#8fae6a", alfa: 0.45 },
    { pts: OV(0, 0, 150, 40, 48), tono: 0.3, solo: true, borde: 1 }, { pts: OV(0, 0, 60, 150, 48), tono: 0.3, solo: true, borde: 1 },
  ],
  teclado: () => {
    const out: Parte[] = [{ pts: RR(-200, -70, 200, 70, 16), tono: 0.45, ang: 0.4, tinte: "#9a948c", alfa: 0.3 }];
    for (let row = 0; row < 3; row++) for (let col = 0; col < 10; col++) { if (row === 2 && col > 1 && col < 8) continue; const x = -178 + col * 36, y = -50 + row * 36; out.push({ pts: RR(x, y, x + 28, y + 26, 5), tono: 0.12, cruz: 1, esp: 7 }); }
    out.push({ pts: RR(-106, 22, 104, 48, 5), tono: 0.12, cruz: 1, esp: 7 });
    return out;
  },
  casete: () => [
    { pts: RR(-140, -88, 140, 88, 12), tono: 0.62, ang: 0.7, tinte: "#3a3a40", alfa: 0.2 },
    { pts: R2(-116, -70, 116, 14), tono: 0.08, cruz: 1, tinte: "#e8c86a", alfa: 0.45 },
    { pts: RR(-64, -34, 64, 6, 6), tono: 0.8 },
    { pts: OV(-40, -14, 18, 18, 20), tono: 0.1, cruz: 1 }, { pts: OV(40, -14, 18, 18, 20), tono: 0.1, cruz: 1 },
    { pts: [[-90, 88], [-70, 40], [70, 40], [90, 88]], tono: 0.5 },
  ],
  walkman: () => [
    { pts: S([[-70, -120], [-60, -190], [0, -214], [60, -190], [70, -120]]).slice(0, 25), tono: 0.7, solo: true, borde: 4 },
    { pts: OV(-74, -118, 18, 26, 18), tono: 0.6 }, { pts: OV(74, -118, 18, 26, 18), tono: 0.6 },
    { pts: RR(-80, -100, 80, 120, 14), tono: 0.42, ang: 0.8, tinte: "#5d8fd6", alfa: 0.36 },
    { pts: RR(-60, -78, 60, 4, 8), tono: 0.78 },
    { pts: RR(-44, -58, 44, -14, 6), tono: 0.1, cruz: 1, tinte: "#e8c86a", alfa: 0.45 },
    { pts: OV(-22, -36, 11, 11, 16), tono: 0.6, solo: true }, { pts: OV(22, -36, 11, 11, 16), tono: 0.6, solo: true },
    { pts: R2(-56, 30, -22, 56), tono: 0.15, cruz: 1 }, { pts: R2(-16, 30, 18, 56), tono: 0.15, cruz: 1 }, { pts: R2(24, 30, 58, 56), tono: 0.15, cruz: 1, tinte: "#c43a2a", alfa: 0.5 },
  ],
  tienda: () => {
    const out: Parte[] = [sombraSuelo(-180, 180, 3), { pts: R2(-160, -190, 160, 0), tono: 0.3, ang: 1.2, tinte: "#e9c9a0", alfa: 0.35 }];
    out.push({ pts: R2(-120, -290, 120, -238), tono: 0.08, cruz: 1 });
    for (let k = 0; k < 6; k++) { const x0 = -178 + k * 59.3; out.push({ pts: [[x0, -236], [x0 + 59.3, -236], [x0 + 59.3, -188], [x0 + 29.6, -170], [x0, -188]], tono: k % 2 ? 0.1 : 0.55, ang: 1.35, cruz: 1, tinte: k % 2 ? undefined : "#c43a2a", alfa: 0.45 }); }
    out.push({ pts: R2(50, -140, 120, 0), tono: 0.6, ang: 1.4, tinte: "#8a5a32", alfa: 0.3 }, { pts: R2(-130, -150, 20, -50), tono: 0.12, cruz: 1, tinte: "#a9d4e6", alfa: 0.3 }, { pts: [[-55, -150], [-55, -50], [-54, -50], [-54, -150]], tono: 0.9, solo: true }, { pts: [[-130, -100], [20, -100], [20, -99], [-130, -99]], tono: 0.9, solo: true });
    return out;
  },
  robot: () => [
    sombraSuelo(-90, 90, 2),
    { pts: R2(-50, -60, -24, 0), tono: 0.6 }, { pts: R2(24, -60, 50, 0), tono: 0.6 },
    { pts: R2(-92, -170, -66, -84), tono: 0.55 }, { pts: R2(66, -170, 92, -84), tono: 0.55 },
    { pts: RR(-68, -176, 68, -56, 14), tono: 0.42, ang: 0.8, tinte: "#8fb0c9", alfa: 0.36 },
    { pts: OV(0, -118, 18, 18, 18), tono: 0.15, cruz: 1, tinte: "#e8c86a", alfa: 0.55 },
    { pts: R2(-3, -296, 3, -262), tono: 0.8, solo: true }, { pts: OV(0, -300, 10, 10, 14), tono: 0.55, tinte: "#c43a2a", alfa: 0.5 },
    { pts: RR(-70, -264, 70, -180, 18), tono: 0.38, ang: 0.6, tinte: "#8fb0c9", alfa: 0.36 },
    { pts: OV(-28, -224, 13, 13, 16), tono: 0.92, solo: true }, { pts: OV(28, -224, 13, 13, 16), tono: 0.92, solo: true },
    { pts: S([[-26, -200], [0, -192], [26, -200]]), tono: 0.9, solo: true, borde: 2.2 },
  ],
  sobre: () => [
    { pts: R2(-130, -82, 130, 82), tono: 0.16, ang: 0.4, cruz: 1 },
    { pts: [[-130, -82], [0, 14], [130, -82], [130, -78], [0, 18], [-130, -78]], tono: 0.9, solo: true, borde: 1.6 },
    { pts: OV(0, 16, 16, 16, 16), tono: 0.6, tinte: "#c43a2a", alfa: 0.55 },
  ],
  calendario: () => {
    const out: Parte[] = [{ pts: RR(-130, -150, 130, 150, 10), tono: 0.14, cruz: 1, ang: 0.5 }, { pts: R2(-130, -150, 130, -86), tono: 0.6, ang: 0.3, tinte: "#c43a2a", alfa: 0.4 }];
    for (const x of [-70, 70]) out.push({ pts: RR(x - 8, -172, x + 8, -128, 6), tono: 0.55 });
    for (let r = 0; r < 4; r++) for (let c = 0; c < 5; c++) { const x = -112 + c * 46, y = -70 + r * 52; out.push({ pts: R2(x, y, x + 36, y + 40), tono: 0.05, solo: true, borde: 1 }); }
    return out;
  },
  laptop: () => [
    { pts: RR(-150, -200, 150, -8, 14), tono: 0.64, ang: 0.8 },
    { pts: R2(-130, -182, 130, -26), tono: 0.08, cruz: 1, tinte: "#a9d4e6", alfa: 0.36 },
    { pts: [[-30, -140], [40, -104], [-30, -68]], tono: 0.6, tinte: "#c43a2a", alfa: 0.5 },
    { pts: [[-190, 22], [-150, -8], [150, -8], [190, 22]], tono: 0.42 },
  ],
};

// ---------------------------------------------------------------- siluetas de perfil (camafeos) para la gente
export type Tipo = "nino" | "joven" | "adulto" | "mujer" | "abuelo";
const PERFIL: P[] = [[-30, 95], [-38, 60], [-55, 20], [-58, -15], [-40, -50], [-5, -64], [25, -54], [40, -32], [44, -12], [46, -4], [62, 12], [49, 18], [51, 26], [45, 31], [49, 36], [43, 44], [45, 55], [30, 62], [24, 75], [26, 95], [72, 112], [80, 140], [-80, 140], [-72, 112]];
const ORO = "#c9a24a", GAFAS: P[] = [[29, -15], [53, -15], [53, -3], [29, -3]];
/** la silueta (partes negras) y sus filetes dorados (como las siluetas "bronceadas" de 1820: el detalle que el negro esconde) */
export const silueta = (tipo: Tipo): { partes: P[][]; oro: P[][] } => {
  const base = smooth(PERFIL, true, 5);
  if (tipo === "nino") return { partes: [base.map(([x, y]) => [x * 0.92, y * 0.92 + 8] as P), smooth([[-62, -10], [-56, -54], [-10, -78], [36, -62], [52, -40], [90, -34], [92, -26], [44, -24], [-60, -12]], true, 5)], oro: [[[-58, -17], [-8, -25], [46, -29]], [[-14, -76], [-6, -50]]] };
  if (tipo === "joven") return { partes: [base, smooth([[-50, 10], [-66, -40], [-30, -82], [20, -80], [44, -50], [40, -44], [16, -70], [-26, -72], [-56, -36], [-42, 10]], true, 5)], oro: [OV(-14, 2, 15, 21, 20).concat([OV(-14, 2, 15, 21, 20)[0]]), [[-16, -19], [-27, -52], [-10, -79], [18, -80]]] };
  if (tipo === "mujer") return { partes: [base.map(([x, y]) => [x * 0.95, y] as P), smooth([[-52, -58], [-90, -70], [-104, -38], [-84, -10], [-50, -22]], true, 5)], oro: [OV(-6, 36, 5, 5, 12).concat([OV(-6, 36, 5, 5, 12)[0]]), [[-70, -62], [-60, -20]]] };
  if (tipo === "abuelo") return { partes: [base, smooth(GAFAS, true, 3)], oro: [[...GAFAS, GAFAS[0]], [[30, -10], [-12, -5]], [[-48, -40], [-30, -56], [-6, -60]]] };
  return { partes: [base, smooth([[-56, -8], [-63, -40], [-42, -67], [-4, -73], [28, -63], [37, -50], [10, -60], [-30, -58], [-50, -30], [-46, -6]], true, 5)], oro: [[[-12, 116], [24, 102], [50, 120]]] };
};
/** camafeo: óvalo de cartulina con doble filete y la silueta negra de perfil que se pega encima */
export const camafeo = (ctx: Ctx, env: Env, cx: number, cy: number, s: number, tipo: Tipo, p: number, seed = 1, rot = 0) => {
  if (p <= 0) return; const q1 = clamp01(p / 0.45), q2 = clamp01((p - 0.4) / 0.6);
  const e = easeOut(q1), lift = 1 + 5 * (1 - e) * (1 - e), dy = 40 * (1 - e), c = Math.cos(rot), sn = Math.sin(rot);
  const Tf = (dx0: number, dy0: number) => ([x, y]: P): P => [cx + dx0 + (x * c - y * sn) * s, cy + dy0 + (x * sn + y * c) * s];
  const ov = OV(0, 0, 112, 140, 60).map(Tf(0, dy)), g = new Gfx(ctx, env, 0, PEN);
  shadowOf(g, [ov], [2.5 * lift, 4 * lift], 3 + 2.5 * lift, 0.32 / Math.sqrt(lift));
  ctx.setTransform(env.scale, 0, 0, env.scale, 0, 0); ctx.fillStyle = "#f3ead8"; path(ctx, ov); ctx.fill(); fibres(ctx, ov, "#f3ead8", seed, 0.6, 0.2);
  ctx.strokeStyle = INK; ctx.globalAlpha = 0.8; ctx.lineWidth = 2.2 * s; path(ctx, OV(0, 0, 100, 128, 60).map(Tf(0, dy))); ctx.stroke(); ctx.lineWidth = 0.9 * s; path(ctx, OV(0, 0, 94, 122, 60).map(Tf(0, dy))); ctx.stroke(); ctx.globalAlpha = 1;
  if (q2 <= 0) return;
  const e2 = easeOut(q2), lift2 = 1 + 4 * (1 - e2) * (1 - e2), sy = dy - 20 * (1 - e2);
  const sil = silueta(tipo), loc = (pp: P[]) => pp.map(([x, y]) => [x * 0.95, y * 0.95 - 4] as P).map(Tf(0, sy));
  const clipOv = OV(0, 0, 93, 121, 60).map(Tf(0, dy)), parts = sil.partes.map(loc);
  ctx.save(); path(ctx, clipOv); ctx.clip();
  shadowOf(g, parts, [1.5 * lift2, 2.5 * lift2], 1.5 + lift2, 0.3 / Math.sqrt(lift2));
  ctx.setTransform(env.scale, 0, 0, env.scale, 0, 0); ctx.fillStyle = "#1d1a18"; parts.forEach((pp) => { path(ctx, pp); ctx.fill(); });
  if (q2 >= 1) { ctx.strokeStyle = ORO; ctx.lineWidth = 1.8 * s; ctx.lineCap = "round"; ctx.lineJoin = "round"; ctx.globalAlpha = 0.9; sil.oro.forEach((ln) => { path(ctx, loc(ln), false); ctx.stroke(); }); ctx.globalAlpha = 1; }
  ctx.restore();
};

// ---------------------------------------------------------------- dibujos a bolígrafo (diagramas)
/** medidor de pluma azul: arco, marcas y aguja que sube hasta `valor` */
export const medidor = (g: Gfx, cx: number, cy: number, r: number, valor: number, p: number, seed = 1) => {
  const arc = (rr: number, a0: number, a1: number): P[] => Array.from({ length: 24 }, (_, k) => { const a = a0 + (k / 23) * (a1 - a0); return [cx + Math.cos(a) * rr, cy - Math.sin(a) * rr] as P; });
  trazo(g, arc(r, Math.PI, 0), NAVY, 4.6, clamp01(p / 0.4), seed, 0.2, false);
  trazo(g, arc(r * 0.72, Math.PI, 0), NAVY, 2.4, clamp01(p / 0.4), seed + 1, 0.2, false);
  if (p > 0.3) for (let k = 0; k <= 10; k++) { const a = Math.PI * (1 - k / 10); trazo(g, [[cx + Math.cos(a) * r * 0.84, cy - Math.sin(a) * r * 0.84], [cx + Math.cos(a) * r, cy - Math.sin(a) * r]], k > 7 ? REDPEN : NAVY, k % 5 ? 2.4 : 4.2, clamp01((p - 0.3) * 4 - k * 0.1), seed + 3 + k, 0.1, false); }
  if (p > 0.55) { const v = valor * easeOut(clamp01((p - 0.55) / 0.45)), a = Math.PI * (1 - v); trazo(g, [[cx, cy], [cx + Math.cos(a) * r * 0.82, cy - Math.sin(a) * r * 0.82]], REDPEN, 6.5, 1, seed + 20, 0.3, false); lazo(g, cx, cy, 12, 12, REDPEN, 4, 1, seed + 21); }
};
export const regla = (ctx: Ctx, env: Env, x: number, y0: number, y1: number, p: number) => {
  if (p <= 0) return; const g = pluma(ctx, env);
  trazo(g, [[x, y1], [x, y0]], NAVY, 2.4, clamp01(p * 2), 7, 0.1, false);
  const n = Math.floor((y1 - y0) / 40); for (let k = 0; k <= n; k++) { const y = y1 - k * 40; if (p > 0.4 + k / (n * 2.2)) trazo(g, [[x, y], [x + (k % 2 ? 18 : 32), y]], NAVY, 1.8, 1, 30 + k, 0.1, false); }
};
export const celularPluma = (g: Gfx, x: number, y: number, s: number, p: number, seed: number, rot = 0) => {
  const c = Math.cos(rot), sn = Math.sin(rot), Tf = ([u, v]: P): P => [x + (u * c - v * sn) * s, y + (u * sn + v * c) * s];
  trazo(g, RR(-22, -40, 22, 40, 7).concat([RR(-22, -40, 22, 40, 7)[0]]).map(Tf), NAVY, 2.2, p, seed, 0.2, false);
  if (p > 0.6) trazo(g, RR(-15, -30, 15, 28, 3).concat([RR(-15, -30, 15, 28, 3)[0]]).map(Tf), NAVY, 1.2, clamp01((p - 0.6) / 0.4), seed + 1, 0.2, false);
};
export const signo = (g: Gfx, ch: string, x: number, y: number, cap: number, p: number, seed: number, color = REDPEN) => mano(g, ch, x, y, cap, p, seed, color, Math.max(3, cap * 0.08));

// ---------------------------------------------------------------- la toma: lista de pasos con tiempos en segundos
export type Elemento = { t: number; d: number; draw: (ctx: Ctx, env: Env, p: number) => void; id?: string };
/** arma un runner staged() para una toma: t en segundos ABSOLUTOS del video, t0 = inicio de la toma */
export const toma = (id: string, t0: number, els: Elemento[], seed = 301) => {
  const fr = (t: number) => Math.round((t - t0) * FPS);
  const steps: Step[] = [{ id: `${id}-pagina`, start: -1, end: 0, draw: (c, e) => pagina(c, e, seed) }];
  els.forEach((el, i) => { const a = Math.max(0, fr(el.t)), b = Math.max(a + 1, fr(el.t + el.d)); steps.push({ id: `${id}-${el.id ?? i}`, start: a, end: b, draw: (c, e, p) => el.draw(c, e, p) }); });
  return staged(id, steps);
};

// ---------------------------------------------------------------- más piezas a bolígrafo
/** nota musical a pluma: cabeza, plica, banderita */
export const notaMusical = (g: Gfx, x: number, y: number, s: number, p: number, seed: number, color = NAVY) => {
  if (p <= 0) return;
  const head: P[] = Array.from({ length: 13 }, (_, k) => { const a = (k / 12) * 6.7; return [x + Math.cos(a) * 9 * s, y + Math.sin(a) * 6.5 * s] as P; });
  trazo(g, head, color, 5 * s, clamp01(p * 3), seed, 0.2, false);
  if (p > 0.33) trazo(g, [[x + 8 * s, y - 2 * s], [x + 8.5 * s, y - 46 * s]], color, 3 * s, clamp01(p * 3 - 1), seed + 1, 0.2, false);
  if (p > 0.66) trazo(g, [[x + 8.5 * s, y - 46 * s], [x + 22 * s, y - 35 * s], [x + 21 * s, y - 22 * s]], color, 3 * s, clamp01(p * 3 - 2), seed + 2, 0.4);
};
/** barra de gráfico a pluma: contorno y rayado diagonal, crece desde la base */
export const barra = (ctx: Ctx, env: Env, x0: number, x1: number, yBase: number, yTop: number, p: number, color: string, seed: number) => {
  if (p <= 0) return; const yc = yBase - (yBase - yTop) * (p >= 1 ? 1 : easeOut(p)), g = pluma(ctx, env);
  ctx.save(); ctx.beginPath(); ctx.rect(x0, yc, x1 - x0, yBase - yc); ctx.clip();
  for (let k = 0, n = Math.ceil((yBase - yTop + (x1 - x0)) / 13); k < n; k++) { const y = yBase - k * 13; g.pen([[x0 - 4, y + 4], [x1 + 4, y - (x1 - x0) - 4]], { w: 2.2, color, seed: seed + k, wobble: 0.3, boil: 0, taper: 0.2, opacity: 0.85, retrace: false }); }
  ctx.restore(); ctx.setTransform(env.scale, 0, 0, env.scale, 0, 0);
  poli(g, [[x0, yBase], [x0, yc], [x1, yc], [x1, yBase]], color, 3.2, 1, seed + 99);
};
/** polilínea de tramos rectos (la pluma suaviza: cada tramo va aparte para que las esquinas queden en punta) */
export const poli = (g: Gfx, pts: P[], color: string, w: number, p: number, seed: number, taper = 0.15) => {
  if (p <= 0) return; const seg: number[] = []; let L = 0;
  for (let i = 0; i + 1 < pts.length; i++) { const l = Math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]); seg.push(l); L += l; }
  let left = (p >= 1 ? 1 : p) * L;
  for (let i = 0; i < seg.length && left > 0; i++) { g.pen([pts[i], pts[i + 1]], { w, color, seed: seed + i, wobble: 0.25, boil: 0, taper, opacity: 0.95, retrace: false, progress: Math.min(1, left / (seg[i] || 1)) }); left -= seg[i]; }
};
/** línea de tiempo a pluma azul con marcas y punta de flecha */
export const linea = (g: Gfx, x0: number, x1: number, y: number, p: number, seed: number, marcas = 10, color = NAVY) => {
  if (p <= 0) return; trazo(g, [[x0, y], [x0 + (x1 - x0) * 0.5, y + 2], [x1, y]], color, 3.2, clamp01(p / 0.6), seed, 0.1);
  for (let k = 0; k <= marcas; k++) { const q = clamp01((p - 0.25 - (k / marcas) * 0.5) / 0.15); if (q > 0) trazo(g, [[x0 + ((x1 - x0 - 30) * k) / marcas, y - (k % 5 ? 10 : 18)], [x0 + ((x1 - x0 - 30) * k) / marcas, y + (k % 5 ? 10 : 18)]], color, k % 5 ? 2 : 3, q, seed + 10 + k, 0.1, false); }
  if (p > 0.6) trazo(g, [[x1 - 22, y - 14], [x1, y], [x1 - 22, y + 14]], color, 3.2, clamp01((p - 0.6) / 0.25), seed + 50, 0.2, false);
};
// ---------------------------------------------------------------- más dibujos a pluma (Grok Bot y los que vengan)
const PO = { boil: 0, opacity: 0.95, retrace: false } as const;
export const corazon = (g: Gfx, x: number, y: number, s: number, p: number, seed: number, color = REDPEN) => { if (p > 0) g.pen(heart(x, y, s), { w: Math.max(3, s * 0.16), color, seed, wobble: 0.3, taper: 0.3, progress: p, closed: true, ...PO }); };
export const nube = (g: Gfx, cx: number, cy: number, rx: number, ry: number, p: number, seed: number, color = NAVY, w = 3.6) => {
  if (p <= 0) return; const n = 9, pts: P[] = [];
  for (let k = 0; k < n; k++) { const a0 = (k / n) * 6.283, a1 = ((k + 1) / n) * 6.283; for (let j = 0; j <= 6; j++) { const u = j / 6, a = a0 + (a1 - a0) * u, b = 1 + Math.sin(u * Math.PI) * 0.2; pts.push([cx + Math.cos(a) * rx * b, cy + Math.sin(a) * ry * b]); } }
  g.pen(pts, { w, color, seed, wobble: 0.3, taper: 0.3, progress: p, ...PO });
};
export const luna = (g: Gfx, cx: number, cy: number, r: number, p: number, seed: number, color = MUSTARD) => {
  if (p <= 0) return; const out: P[] = [];
  for (let k = 0; k <= 16; k++) { const a = 1.25 + (k / 16) * 3.78; out.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); }
  for (let k = 0; k <= 16; k++) { const a = 5.03 - (k / 16) * 3.78 + 0.0; out.push([cx + r * 0.42 + Math.cos(a) * r * 0.8, cy + Math.sin(a) * r * 0.86]); }
  g.pen(out, { w: 4.2, color, seed, wobble: 0.3, taper: 0.3, progress: p, ...PO });
};
export const estrella = (g: Gfx, x: number, y: number, r: number, p: number, seed: number, color = MUSTARD) => { const pts: P[] = []; for (let k = 0; k <= 8; k++) { const a = (k / 8) * 6.283 - Math.PI / 2, rr = k % 2 ? r * 0.3 : r; pts.push([x + Math.cos(a) * rr, y + Math.sin(a) * rr]); } poli(g, pts, color, 3.4, p, seed); };
export const diana = (g: Gfx, cx: number, cy: number, r: number, p: number, seed: number) => {
  [1, 0.66, 0.33].forEach((k, i) => { const q = clamp01(p * 3.2 - i * 0.9); if (q > 0) g.pen(OV(cx, cy, r * k, r * k, 30), { w: i === 2 ? 7 : 4.4, color: i === 2 ? REDPEN : NAVY, seed: seed + i, wobble: 0.3, taper: 0.2, progress: q, closed: true, ...PO }); });
  if (p > 0.75) flecha(g, [[cx + r * 1.25, cy - r * 0.9], [cx + r * 0.55, cy - r * 0.4], [cx + 6, cy - 4]], INK, 4, clamp01((p - 0.75) / 0.25), seed + 9);
};
export const avion = (g: Gfx, x: number, y: number, s: number, p: number, seed: number, rot = 0, color = NAVY) => {
  if (p <= 0) return; const c = Math.cos(rot), sn = Math.sin(rot), T = ([u, v]: P): P => [x + (u * c - v * sn) * s, y + (u * sn + v * c) * s];
  poli(g, ([[34, 0], [-50, -32], [-28, 2], [-50, 32], [34, 0]] as P[]).map(T), color, 3.4, clamp01(p * 1.4), seed);
  if (p > 0.6) poli(g, ([[-28, 2], [34, 0]] as P[]).map(T), color, 2.6, clamp01((p - 0.6) / 0.4), seed + 1);
};
export const lupa = (g: Gfx, x: number, y: number, r: number, p: number, seed: number, rot = 0.75, color = NAVY) => {
  if (p <= 0) return; g.pen(OV(x, y, r, r, 30), { w: 5.5, color, seed, wobble: 0.3, taper: 0.2, progress: clamp01(p * 1.5), closed: true, ...PO });
  if (p > 0.6) { const c = Math.cos(rot), s = Math.sin(rot); trazo(g, [[x + c * r * 1.05, y + s * r * 1.05], [x + c * r * 2.1, y + s * r * 2.1]], color, 11, clamp01((p - 0.6) / 0.4), seed + 1, 0.12, false); }
};
export const sobrePluma = (g: Gfx, x: number, y: number, w: number, h: number, p: number, seed: number, color = NAVY) => {
  if (p <= 0) return; poli(g, [[x - w / 2, y - h / 2], [x + w / 2, y - h / 2], [x + w / 2, y + h / 2], [x - w / 2, y + h / 2], [x - w / 2, y - h / 2]], color, 3.2, clamp01(p * 1.6), seed);
  if (p > 0.5) poli(g, [[x - w / 2, y - h / 2], [x, y + h * 0.12], [x + w / 2, y - h / 2]], color, 2.8, clamp01((p - 0.5) / 0.5), seed + 1);
};
export const etiqueta = (g: Gfx, x: number, y: number, s: number, p: number, seed: number, text = "$$", rot = -0.22) => {
  if (p <= 0) return; const c = Math.cos(rot), sn = Math.sin(rot), T = ([u, v]: P): P => [x + (u * c - v * sn) * s, y + (u * sn + v * c) * s];
  poli(g, ([[-80, -40], [52, -40], [92, 0], [52, 40], [-80, 40], [-80, -40]] as P[]).map(T), INK, 3.4, clamp01(p * 1.6), seed);
  if (p > 0.4) g.pen(OV(T([60, 0])[0], T([60, 0])[1], 8 * s, 8 * s, 14), { w: 2.6, color: INK, seed: seed + 1, wobble: 0.2, taper: 0.2, progress: clamp01((p - 0.4) * 3), closed: true, ...PO });
  if (p > 0.5) { const [tx, ty] = T([-14, 0]); mano(g, text, tx, ty, 46 * s, clamp01((p - 0.5) / 0.5), seed + 2, REDPEN, 4.2); }
};
/** hoja con texto a máquina (documento, lista, resumen): la tarjeta cae y las líneas se escriben; la primera va en rojo */
export const hojaTexto = (ctx: Ctx, env: Env, cd: Card, lineas: string[], p: number, cap = 26, caida = 0.35) => {
  if (p <= 0) return; drawCard(ctx, env, cd, clamp01(p / caida), false); if (p <= caida) return;
  const q = (p - caida) / (1 - caida), total = lineas.reduce((a, l) => a + [...l].length, 0); let left = q >= 1 ? Infinity : q * total;
  lineas.forEach((ln, i) => {
    const L = [...ln].length, n = left === Infinity ? Infinity : Math.max(0, Math.min(L, Math.floor(left + 0.999))); if (left !== Infinity) left -= L; if (n === 0) return;
    const [x, y] = toPage(cd, [-cd.w / 2 + 28, -cd.h / 2 + 46 + i * cap * 1.75]); ctx.setTransform(env.scale, 0, 0, env.scale, 0, 0); ctx.translate(x, y); ctx.rotate(cd.rot); typed(ctx, ln, 0, -cap / 2, cap, i === 0 ? RED : TIPO, cd.seed + i, n);
  });
};
/** ficha de perfil: tarjeta con un camafeo chico y el nombre a máquina */
export const perfil = (ctx: Ctx, env: Env, cd: Card, tipo: Tipo, nombre: string, p: number) => {
  if (p <= 0) return; drawCard(ctx, env, cd, clamp01(p / 0.4), false); if (p <= 0.3) return;
  const [mx, my] = toPage(cd, [-cd.w / 2 + 60, 0]); camafeo(ctx, env, mx, my, 0.44, tipo, clamp01((p - 0.3) / 0.45), cd.seed, cd.rot);
  if (p > 0.6) { const q = clamp01((p - 0.6) / 0.4), [tx, ty] = toPage(cd, [-cd.w / 2 + 122, -22]); ctx.setTransform(env.scale, 0, 0, env.scale, 0, 0); ctx.translate(tx, ty); ctx.rotate(cd.rot); typed(ctx, nombre, 0, -13, 26, TIPO, cd.seed + 3, q >= 1 ? Infinity : Math.ceil(q * nombre.length));
    const g = pluma(ctx, env); [0, 1].forEach((k) => { const [a, b] = [toPage(cd, [-cd.w / 2 + 122, 18 + k * 26]), toPage(cd, [cd.w / 2 - 30 - k * 50, 18 + k * 26])]; trazo(g, [a, b], "#9a8f80", 2.2, clamp01(q * 2 - k), cd.seed + 5 + k, 0.2, false); }); }
};
/** un papel que viaja por una ruta (la tarea que se pasan los agentes) y queda al final */
export const papelVolando = (ctx: Ctx, env: Env, ruta: P[], w: number, h: number, p: number, seed: number, texto = "") => {
  if (p <= 0) return; const s = resample(smooth(ruta, false, 10), 160), q = p >= 1 ? 1 : p * p * (3 - 2 * p), i = Math.min(s.length - 1, Math.round(q * (s.length - 1))), [x, y] = s[i];
  const vuelo = Math.sin(Math.PI * q), rot = Math.sin(q * 9) * 0.12 * vuelo - 0.04;
  drawCard(ctx, env, { cx: x, cy: y - 10 * vuelo, w, h, rot, color: "#fbf6ea", seed, from: [0, 0], torn: 1.6 }, 1 - 0.25 * vuelo, false);
  if (texto) escribir(ctx, env, texto, x, y - 10 * vuelo, Math.min(22, (w - 20) / (texto.length * 0.86)), 1, seed, TIPO, rot);
};

// ---------------------------------------------------------------- más láminas grabadas
const tintar = (parts: Parte[], de: string, a: string): Parte[] => parts.map((q) => (q.tinte === de ? { ...q, tinte: a } : q));
const flor = (cx: number, cy: number): Parte[] => [...[0, 1, 2, 3, 4].map((k): Parte => { const a = k * 1.2566 - 1.57; return { pts: OV(cx + Math.cos(a) * 12, cy + Math.sin(a) * 12, 9, 9, 12), tono: 0.1, cruz: 1, tinte: "#e88aa0", alfa: 0.6, borde: 1.4 }; }), { pts: OV(cx, cy, 7, 7, 10), tono: 0.5, tinte: "#e8c040", alfa: 0.6 }];
/** el robot-agente con color y accesorio (los de la skill muñecos: audífonos, casco, banda, flor) */
export const robotCon = (tinte: string, acc: "" | "audifonos" | "casco" | "banda" | "flor"): Parte[] => {
  let base = tintar(FIG.robot(), "#8fb0c9", tinte); const extra: Parte[] = [];
  if (acc === "casco" || acc === "audifonos") base = base.filter((q) => bounds(q.pts).y1 > -255);
  if (acc === "casco") extra.push({ pts: smooth([[-80, -254], [-72, -298], [-36, -324], [36, -324], [72, -298], [80, -254]], true, 5), tono: 0.34, ang: 0.5, tinte: "#e8c040", alfa: 0.55 }, { pts: R2(-100, -262, 100, -247), tono: 0.55, ang: 0.2, tinte: "#e8c040", alfa: 0.55 });
  if (acc === "audifonos") { const arc: P[] = []; for (let k = 0; k <= 16; k++) { const a = Math.PI + (k / 16) * Math.PI; arc.push([Math.cos(a) * 86, -222 + Math.sin(a) * 86]); } for (let k = 16; k >= 0; k--) { const a = Math.PI + (k / 16) * Math.PI; arc.push([Math.cos(a) * 75, -222 + Math.sin(a) * 75]); } extra.push({ pts: arc, tono: 0.72, ang: 1.2 }, { pts: RR(-98, -252, -66, -192, 10), tono: 0.62, tinte: "#2c2c30", alfa: 0.3 }, { pts: RR(66, -252, 98, -192, 10), tono: 0.62, tinte: "#2c2c30", alfa: 0.3 }); }
  if (acc === "banda") extra.push({ pts: R2(-72, -252, 72, -238), tono: 0.62, ang: 0.2, tinte: "#c43a2a", alfa: 0.55 });
  if (acc === "flor") extra.push(...flor(50, -262));
  return [...base, ...extra];
};
const gear = (cx: number, cy: number, r: number, n: number, rot = 0): P[] => { const out: P[] = [], d = 6.283 / n; for (let k = 0; k < n; k++) { const a0 = rot + k * d; ([[0, r], [0.14, r * 1.22], [0.4, r * 1.22], [0.54, r]] as [number, number][]).forEach(([f, rr]) => out.push([cx + Math.cos(a0 + f * d) * rr, cy + Math.sin(a0 + f * d) * rr])); } return out; };
const moneda = (cx: number, y: number, rx = 62, ry = 18, h = 14): Parte[] => {
  const bajo = Array.from({ length: 13 }, (_, i): P => { const a = (i / 12) * Math.PI; return [cx + Math.cos(a) * rx, y + Math.sin(a) * ry]; });
  const alto = Array.from({ length: 13 }, (_, i): P => { const a = Math.PI - (i / 12) * Math.PI; return [cx + Math.cos(a) * rx, y - h + Math.sin(a) * ry]; });
  return [{ pts: [...bajo, ...alto], tono: 0.58, ang: 1.5, esp: 4.4, cruz: 1, tinte: "#d9b44a", alfa: 0.42 }, { pts: OV(cx, y - h, rx, ry, 28), tono: 0.22, ang: 0.25, cruz: 1, tinte: "#ecd27a", alfa: 0.42 }];
};
Object.assign(FIG, {
  robotDots: () => robotCon("#8fb0c9", "banda"), robotMuse: () => robotCon("#e4b8a8", "flor"), robotGrok: () => robotCon("#f3a35a", "audifonos"), robotGrokCasco: () => robotCon("#f3a35a", "casco"),
  robotVerde: () => robotCon("#a6d0c3", ""), robotRosa: () => robotCon("#e4b8a8", ""), robotLila: () => robotCon("#c9b6e6", ""), robotAmarillo: () => robotCon("#f3d27a", ""),
  laptopOff: () => FIG.laptop().filter((q) => q.tinte !== "#c43a2a").map((q) => (q.tinte === "#a9d4e6" ? { ...q, tinte: "#1d2430", alfa: 0.55, tono: 0.72, cruz: 0.7 } : q)),
  engranajes: () => [{ pts: gear(-50, -40, 88, 10), tono: 0.42, ang: 0.7, tinte: "#9aa3ad", alfa: 0.35 }, { pts: OV(-50, -40, 24, 24, 20), tono: 0.08, cruz: 1 }, { pts: gear(84, 84, 56, 8, 0.2), tono: 0.42, ang: 0.7, tinte: "#e0a24a", alfa: 0.4 }, { pts: OV(84, 84, 16, 16, 16), tono: 0.08, cruz: 1 }],
  monedas: () => [sombraSuelo(-150, 150, 3), ...[0, 1, 2, 3, 4].flatMap((k) => moneda(-62, -8 - k * 16)), ...[0, 1, 2].flatMap((k) => moneda(70, -8 - k * 16))],
  corona: () => [{ pts: [[-130, 0], [-142, -118], [-84, -62], [-42, -150], [0, -72], [42, -150], [84, -62], [142, -118], [130, 0]], tono: 0.4, ang: 0.8, tinte: "#d9b44a", alfa: 0.45 }, { pts: R2(-134, -24, 134, 10), tono: 0.62, ang: 0.15, tinte: "#c9a24a", alfa: 0.42 }, ...([[-142, -126], [-42, -158], [42, -158], [142, -126]] as P[]).map(([x, y]): Parte => ({ pts: OV(x, y, 12, 12, 14), tono: 0.25, tinte: "#c43a2a", alfa: 0.55 })), { pts: OV(0, -7, 15, 11, 14), tono: 0.3, tinte: "#3a6ac4", alfa: 0.55 }],
  escudo: () => [{ pts: smooth([[-112, -150], [0, -176], [112, -150], [106, -40], [62, 50], [0, 96], [-62, 50], [-106, -40]], true, 6), tono: 0.45, ang: 0.8, tinte: "#5d8fd6", alfa: 0.38 }, { pts: smooth([[-82, -126], [0, -146], [82, -126], [77, -40], [44, 30], [0, 64], [-44, 30], [-77, -40]], true, 6), tono: 0.12, cruz: 1 }, { pts: [[-34, -44], [-8, -16], [40, -76], [50, -66], [-8, 6], [-44, -34]], tono: 0.85, tinte: "#3b7d4f", alfa: 0.6 }],
  telefono: () => [sombraSuelo(-150, 150, 2), { pts: smooth([[-124, 0], [-104, -92], [104, -92], [124, 0]], true, 4), tono: 0.6, ang: 0.75, tinte: "#2c2c30", alfa: 0.22 }, { pts: OV(0, -50, 46, 30, 28), tono: 0.1, cruz: 1, tinte: "#e9dfc9", alfa: 0.4 }, ...Array.from({ length: 10 }, (_, k): Parte => { const a = -2.6 + (k / 9) * 5.2; return { pts: OV(Math.cos(a) * 32, -50 + Math.sin(a) * 19, 4, 4, 8), tono: 0.8, solo: true, borde: 1.1 }; }), { pts: smooth([[-156, -110], [-146, -150], [-96, -162], [0, -150], [96, -162], [146, -150], [156, -110], [114, -102], [92, -126], [0, -120], [-92, -126], [-114, -102]], true, 4), tono: 0.66, ang: 0.3, tinte: "#2c2c30", alfa: 0.22 }],
  megafono: () => [{ pts: [[-104, -34], [62, -112], [62, 112], [-104, 34]], tono: 0.42, ang: 1.25, tinte: "#c43a2a", alfa: 0.38 }, { pts: OV(62, 0, 28, 112, 28), tono: 0.18, cruz: 1 }, { pts: RR(-150, -30, -100, 30, 8), tono: 0.62 }, { pts: RR(-112, 22, -84, 96, 8), tono: 0.62 }],
  camara: () => [{ pts: R2(-62, -130, 42, -88), tono: 0.62 }, { pts: RR(-150, -92, 150, 100, 14), tono: 0.6, ang: 0.6, tinte: "#2c2c30", alfa: 0.2 }, { pts: OV(10, 6, 74, 74, 32), tono: 0.72 }, { pts: OV(10, 6, 50, 50, 28), tono: 0.14, cruz: 1, tinte: "#7fb3c9", alfa: 0.42 }, { pts: OV(10, 6, 18, 18, 16), tono: 0.85, solo: true }, { pts: R2(92, -78, 132, -54), tono: 0.08, cruz: 1, tinte: "#e8c86a", alfa: 0.55 }],
  carrito: () => [sombraSuelo(-140, 130, 2), { pts: [[-124, -176], [134, -176], [104, -64], [-94, -64]], tono: 0.32, ang: 0, esp: 8, cruz: 0, tinte: "#9aa3ad", alfa: 0.3 }, { pts: [[-176, -206], [-124, -206], [-120, -196], [-168, -194]], tono: 0.7, solo: true }, { pts: [[-124, -206], [-94, -64], [-100, -62], [-130, -204]], tono: 0.7, solo: true }, { pts: [[-94, -64], [104, -64], [100, -50], [-90, -50]], tono: 0.6, solo: true }, { pts: OV(-66, -24, 20, 20, 18), tono: 0.75 }, { pts: OV(78, -24, 20, 20, 18), tono: 0.75 }],
  ojo: () => [{ pts: smooth([[-150, 0], [-80, -62], [0, -82], [80, -62], [150, 0], [80, 62], [0, 82], [-80, 62]], true, 6), tono: 0.1, cruz: 1, ang: 0.3 }, { pts: OV(0, 0, 58, 58, 32), tono: 0.5, ang: 0.9, tinte: "#5d8fd6", alfa: 0.45 }, { pts: OV(0, 0, 24, 24, 20), tono: 0.98, cruz: 0.1, esp: 3.2 }, { pts: OV(-18, -18, 9, 9, 12), tono: 0, cruz: 1, solo: true, borde: 1.2 }],
  plastilina: () => [sombraSuelo(-90, 90, 2), { pts: smooth([[-52, 0], [-58, -92], [-42, -142], [42, -142], [58, -92], [52, 0]], true, 5), tono: 0.36, ang: 0.8, tinte: "#e07a4a", alfa: 0.48 }, { pts: smooth([[-50, -120], [-92, -84], [-100, -60], [-84, -56], [-52, -88]], true, 5), tono: 0.4, tinte: "#e07a4a", alfa: 0.48 }, { pts: smooth([[50, -120], [96, -150], [104, -170], [88, -176], [50, -140]], true, 5), tono: 0.4, tinte: "#e07a4a", alfa: 0.48 }, { pts: OV(0, -192, 60, 56, 30), tono: 0.3, ang: 0.6, tinte: "#f0b080", alfa: 0.48 }, { pts: OV(-21, -198, 10, 12, 14), tono: 0.04, cruz: 1 }, { pts: OV(21, -198, 10, 12, 14), tono: 0.04, cruz: 1 }, { pts: OV(-19, -196, 4.5, 5.5, 10), tono: 0.95, solo: true, borde: 2.6 }, { pts: OV(23, -196, 4.5, 5.5, 10), tono: 0.95, solo: true, borde: 2.6 }, { pts: [[-22, -168], [0, -160], [22, -168], [20, -164], [0, -156], [-20, -164]], tono: 0.9, solo: true, borde: 1.6 }],
  cuadro: () => [{ pts: R2(-130, -110, 130, 110), tono: 0.55, ang: 0.6, tinte: "#8a5a32", alfa: 0.35 }, { pts: R2(-104, -84, 104, 84), tono: 0.06, cruz: 1, tinte: "#cfe3ee", alfa: 0.42 }, { pts: [[-104, 84], [-104, 22], [-42, -40], [8, 8], [50, -22], [104, 40], [104, 84]], tono: 0.46, ang: 0.4, tinte: "#8fae6a", alfa: 0.46 }, { pts: OV(56, -46, 18, 18, 18), tono: 0.06, cruz: 1, tinte: "#e8c040", alfa: 0.62 }],
} as Record<string, () => Parte[]>);

// ---------------------------------------------------------------- constructores de piezas con su tiempo (segundos del video)
export const el = (t: number, d: number, draw: Elemento["draw"]): Elemento => ({ t, d, draw });
export const penE = (t: number, d: number, fn: (g: Gfx, p: number) => void) => el(t, d, (c, e, p) => fn(pluma(c, e), p));
const MED: Record<string, { c: P; w: number; h: number }> = {};
export const medida = (fig: string) => { if (!MED[fig]) { const b = bounds(FIG[fig]().flatMap((q) => q.pts)); MED[fig] = { c: [(b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2], w: b.x1 - b.x0, h: b.y1 - b.y0 }; } return MED[fig]; };
const encaje = (fig: string, cd: Card, sMax: number) => { const m = medida(fig), s = Math.min(sMax, (cd.w - 70) / m.w, (cd.h - 70) / m.h); return { s, off: [-m.c[0] * s, -m.c[1] * s] as P }; };
/** tarjeta que cae y se pega con cinta; adentro el grabado se corta línea por línea y se colorea */
export const grab = (t: number, fig: string, cd: Card, sMax = 1.2, dCut = 0.78): Elemento[] => { const { s, off } = encaje(fig, cd, sMax); return [el(t - 0.1, 0.32, (c, e, p) => drawCard(c, e, cd, p)), el(t + 0.1, dCut, (c, e, p) => { const [x, y] = toPage(cd, off); drawGrabado(c, e, fig, FIG[fig], x, y, s, cd.rot, p, 7); })]; };
/** para lo que llega al final de una toma: la lámina ya impresa se pega de una vez */
export const pegada = (t: number, fig: string, cd: Card, sMax = 1.2): Elemento => { const { s, off } = encaje(fig, cd, sMax); return el(t - 0.1, 0.32, (c, e, p) => { drawCard(c, e, cd, p); if (p <= 0) return; const k = 1 - easeOut(p), [x, y] = toPage(cd, off, cd.from[0] * k, cd.from[1] * k); drawGrabado(c, e, fig, FIG[fig], x, y, s, cd.rot, 1, 7); }); };
/** grabado suelto sobre la página (sin tarjeta), centrado en (x, y) */
export const grabSuelto = (t: number, fig: string, x: number, y: number, s: number, d = 0.7, seed = 7) => el(t, d, (c, e, p) => { const m = medida(fig); drawGrabado(c, e, fig, FIG[fig], x - m.c[0] * s, y - m.c[1] * s, s, 0, p, seed); });
const ajusta = (word: string, cap: number) => { const n = [...word].filter((ch) => ch !== " ").length, sp = [...word].length - n; return Math.min(cap, (930 - 6 * n) / (1.42 * n + 0.55 * sp)); };
export const tituloT = (t: number, word: string, cx: number, y: number, cap: number, seed: number) => { const tiles = ransom(word, cx, y, ajusta(word, cap), seed); return { e: el(t - 0.06, 0.16 + 0.065 * tiles.length, (c, e, p) => drawRansom(c, e, tiles, p)), tiles }; };
/** la palabra clave en letras recortadas (el equivalente de la palabra roja de la pizarra) */
export const titulo = (t: number, word: string, cx: number, y: number, cap: number, seed: number) => tituloT(t, word, cx, y, cap, seed).e;
/** tira de papel que cae y se escribe a máquina */
export const tiraE = (t: number, text: string, x: number, y: number, cap: number, rot = 0, seed = 1, cps = 26): Elemento => {
  const st = tira(text, x, y, cap, rot, seed), drop = 0.16, n = [...text].length, dt = Math.max(0.12, n / cps), D = drop + dt;
  return el(t - 0.06, D, (c, e, p) => { const u = p * D; drawStrip(c, e, st, clamp01(u / drop), p >= 1 ? Infinity : Math.floor(clamp01((u - drop * 0.75) / dt) * n + 0.999)); });
};
export const tipoE = (t: number, text: string, x: number, y: number, cap: number, rot = 0, seed = 1, cps = 26) => el(t - 0.04, Math.max(0.1, [...text].length / cps), (c, e, p) => escribir(c, e, text, x, y, cap, p, seed, TIPO, rot));
export const selloE = (t: number, x: number, y: number, rot: number, big: string, color = RED, cap = 40, small = "") => el(t - 0.1, 0.32, (c, e, p) => sello(c, e, x, y, rot, big, small, p, color, cap));
export const camE = (t: number, x: number, y: number, s: number, tipo: Tipo, seed = 1) => el(t - 0.1, 0.5, (c, e, p) => camafeo(c, e, x, y, s, tipo, p, seed));
export const preg = (t: number, x: number, y: number, cap: number, color = REDPEN) => penE(t - 0.04, 0.3, (g, p) => signo(g, "?", x, y, cap, p, Math.round(x * 3 + y), color));
export const manoE = (t: number, text: string, x: number, y: number, cap: number, d = 0.45, color = REDPEN, w = 3.4) => penE(t - 0.04, d, (g, p) => mano(g, text, x, y, cap, p, 11 + text.length * 7, color, w));

// ---------------------------------------------------------------- montaje: una toma por página, la nueva entra desde la derecha
export const montaje = (pref: string, esc: Record<string, number>, orden: string[], tomas: Record<string, () => Elemento[]>, dur: number, slide = 11): Shot[] => {
  const F = (t: number) => Math.round(t * FPS), D = F(dur), fin = (i: number) => (i + 1 < orden.length ? esc[orden[i + 1]] : dur);
  const run = orden.map((n, i) => toma(`${pref}-${n}`, esc[n], tomas[n](), 300 + i * 13)), len = orden.map((n, i) => F(fin(i)) - F(esc[n]));
  const shot = (i: number) => (ctx: Ctx, local: number, env: Env) => {
    const DW = Math.round(env.W * env.scale), DH = Math.round(env.H * env.scale);
    if (i >= 2) env.cache.delete(`${pref}-${orden[i - 2]}:base:${DW}x${DH}`); // esa página ya no vuelve: libera su lienzo
    if (i === 0 || local >= slide) run[i](ctx, local, env);
    else {
      run[i - 1](ctx, len[i - 1] - 1, env);
      const key = `${pref}:hoja:${DW}x${DH}`; let L = env.cache.get(key) as Layer | undefined; if (!L) { L = env.canvas(DW, DH); env.cache.set(key, L); }
      run[i](L.ctx, local, env);
      const u = (local + 1) / slide, e = 1 - Math.pow(1 - u, 3), dx = Math.round(DW * (1 - e));
      ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = "source-over";
      if (dx > 0) { const sw = Math.round(54 * env.scale), gr = ctx.createLinearGradient(dx - sw, 0, dx, 0); gr.addColorStop(0, "rgba(70,45,20,0)"); gr.addColorStop(1, "rgba(70,45,20,0.34)"); ctx.fillStyle = gr; ctx.fillRect(dx - sw, 0, sw, DH); }
      if (DW - dx > 0) ctx.drawImage(L.canvas as CanvasImageSource, 0, 0, DW - dx, DH, dx, 0, DW - dx, DH);
    }
    vineta(ctx, env);
  };
  return orden.map((n, i) => ({ id: n, start: F(esc[n]), end: i + 1 < orden.length ? F(esc[orden[i + 1]]) : D, draw: shot(i) }));
};
void fractal; void sample; void INK;
