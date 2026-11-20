// MOVIMIENTO · kit del estilo MOTION DESIGN de reel-motion (motor AniDoodle: "hace que cualquier animación se vea súper profesional").
// Mismas piezas y mismos nombres que archivo.ts (titulo, tiraE, grab, selloE, camE, penE...), así las tomas de
// ERA y Grok Bot se reutilizan tal cual; cambia cómo se ven y cómo se mueven, con un lenguaje de movimiento fijo
// (skill motion-art-direction):
//   entrada  cubic-bezier(0.16, 1, 0.3, 1)   0,4 s  (unidad base; lo grande 0,8 s, lo chico 0,2 s)
//   salida   cubic-bezier(0.7, 0, 0.84, 0)   0,3 s  (la escena anterior sube y se va)
//   mover    cubic-bezier(0.65, 0, 0.35, 1)
//   golpe    cubic-bezier(0.34, 1.56, 0.64, 1)  solo para el protagonista (palabra clave, insignia, ícono)
//   escalonado 30 ms por letra, 60 ms por grupo · una sola transición (empujar hacia arriba) · fondo vivo pero discreto
// Tipografía real (Poppins ExtraBold e Inter SemiBold como trazos: tipos.ts), íconos planos con contorno hechos con
// las mismas siluetas de las láminas del #4, fondo claro con manchas de color que se mueven despacio.
import { Gfx, heart, type Ctx, type Env, type Layer, type P } from "./core";
import type { Shot } from "./film";
import { bounds, mix, resample, smooth } from "./gallery";
import { staged, type Step } from "./scrapbookKit";
import { FIG, PEN, silueta, tarjeta, tpOf, type Card, type Parte, type Tipo } from "./archivo";
import { TIPOS } from "./tipos";

export { tarjeta, tpOf, type Card, type Tipo };
export const FPS = 30, W = 1080, H = 1920;
export const INK = "#141414", PAPEL = "#F6F4EF", BLANCO = "#FFFFFF", GRIS = "#D9D5CC";
export const AZUL = "#2F5BFF", CORAL = "#FF5A3C", AMARILLO = "#FFC531", MENTA = "#14B86A", VIOLETA = "#7A5CFF", ROJO = "#E5322D";
// los nombres que usan las tomas (vienen de archivo.ts)
export const RED = ROJO, REDPEN = ROJO, NAVY = AZUL, VERDE = MENTA, MUSTARD = AMARILLO;
const PALETA = [AZUL, CORAL, AMARILLO, MENTA, VIOLETA];

// ---------------------------------------------------------------- curvas
const bezier = (x1: number, y1: number, x2: number, y2: number) => {
  const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx, cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
  const sx = (t: number) => ((ax * t + bx) * t + cx) * t, sy = (t: number) => ((ay * t + by) * t + cy) * t, dx = (t: number) => (3 * ax * t + 2 * bx) * t + cx;
  return (x: number) => { if (x <= 0) return 0; if (x >= 1) return 1; let t = x; for (let i = 0; i < 10; i++) { const e = sx(t) - x, d = dx(t); if (Math.abs(e) < 1e-7 || Math.abs(d) < 1e-7) break; t -= e / d; } return sy(Math.min(1, Math.max(0, t))); };
};
export const entra = bezier(0.16, 1, 0.3, 1), sale = bezier(0.7, 0, 0.84, 0), mueve = bezier(0.65, 0, 0.35, 1), golpe = bezier(0.34, 1.56, 0.64, 1);
export const clamp01 = (v: number) => (v <= 0 ? 0 : v >= 1 ? 1 : v);
const seg = (p: number, D: number, t0: number, d: number) => clamp01((p * D - t0) / d); // progreso de un tramo [t0, t0+d] (s) dentro de una pieza de D s
const base = (c: Ctx, env: Env) => c.setTransform(env.scale, 0, 0, env.scale, 0, 0);

// ---------------------------------------------------------------- tipografía real
export type Fuente = "poppins" | "inter";
const P2D = new Map<string, Path2D>();
const gpath = (f: Fuente, ch: string) => { const k = f + ch; let p = P2D.get(k); if (!p) { const g = TIPOS[f].glyphs[ch] ?? TIPOS[f].glyphs["?"]; p = new Path2D(g[1]); P2D.set(k, p); } return p; };
const adv = (f: Fuente, ch: string) => TIPOS[f].glyphs[ch]?.[0] ?? TIPOS[f].upm * 0.5;
export const capDe = (size: number, f: Fuente = "poppins") => (TIPOS[f].cap / TIPOS[f].upm) * size;
const disponer = (s: string, size: number, f: Fuente, track: number) => { const k = size / TIPOS[f].upm; let x = 0; const out: { ch: string; x: number; w: number }[] = []; for (const ch of s) { const w = adv(f, ch) * k; out.push({ ch, x, w }); x += w + track; } return { out, w: Math.max(0, x - track) }; };
export const ancho = (s: string, size: number, f: Fuente = "poppins", track = 0) => disponer(s, size, f, track).w;
const letra = (c: Ctx, f: Fuente, ch: string, x: number, y: number, size: number) => { if (ch === " ") return; const k = size / TIPOS[f].upm; c.save(); c.translate(x, y); c.scale(k, -k); c.fill(gpath(f, ch)); c.restore(); };
/** texto quieto (y = línea base) */
export const texto = (c: Ctx, env: Env, s: string, x: number, y: number, size: number, color: string, f: Fuente = "poppins", align: "l" | "c" | "r" = "c", track = 0) => {
  const { out, w } = disponer(s, size, f, track), x0 = align === "c" ? x - w / 2 : align === "r" ? x - w : x;
  base(c, env); c.fillStyle = color; out.forEach((g) => letra(c, f, g.ch, x0 + g.x, y, size));
};
/** letras que suben desde una línea invisible, una tras otra (30 ms); los números ruedan como contador.
 *  p 0..1 de la pieza, D = su duración en segundos. Devuelve el centro de cada letra. */
export const textoSube = (c: Ctx, env: Env, s: string, x: number, y: number, size: number, color: string, p: number, D: number, f: Fuente = "poppins", align: "l" | "c" | "r" = "c", track = 0, contador = false) => {
  const { out, w } = disponer(s, size, f, track), x0 = align === "c" ? x - w / 2 : align === "r" ? x - w : x, cap = capDe(size, f);
  if (p <= 0) return out;
  const n = out.length, st = 0.03, ld = Math.max(0.18, Math.min(0.42, D - st * (n - 1)));
  base(c, env); c.save(); c.beginPath(); c.rect(x0 - size, y - cap * 1.5, w + size * 2, cap * 1.5 + size * 0.34); c.clip(); c.fillStyle = color;
  out.forEach((g, i) => {
    const q = p >= 1 ? 1 : entra(clamp01((p * D - i * st) / ld)); if (q <= 0) return;
    const dgt = contador && /[0-9]/.test(g.ch);
    if (!dgt) { letra(c, f, g.ch, x0 + g.x, y + (1 - q) * cap * 1.55, size); return; }
    const d = +g.ch, v = q * (10 + d), a = Math.floor(v), fr = v - a, lh = cap * 1.75;
    c.save(); c.beginPath(); c.rect(x0 + g.x - size * 0.1, y - cap * 1.12, g.w + size * 0.2, cap * 1.12 + size * 0.12); c.clip();
    [[a % 10, -fr * lh], [(a + 1) % 10, (1 - fr) * lh]].forEach(([dd, dy]) => { if (Math.abs(dy) >= lh * 0.98) return; const ch = String(dd), cw = adv(f, ch) * size / TIPOS[f].upm; letra(c, f, ch, x0 + g.x + (g.w - cw) / 2, y + dy, size); });
    c.restore();
  });
  c.restore();
  return out.map((g) => ({ ...g, x: x0 + g.x }));
};

// ---------------------------------------------------------------- formas
const rr = (c: Ctx, x: number, y: number, w: number, h: number, r: number) => { const q = Math.min(r, w / 2, h / 2); c.beginPath(); c.moveTo(x + q, y); c.arcTo(x + w, y, x + w, y + h, q); c.arcTo(x + w, y + h, x, y + h, q); c.arcTo(x, y + h, x, y, q); c.arcTo(x, y, x + w, y, q); c.closePath(); };
const sombra = (c: Ctx, blur = 28, dy = 10, a = 0.16) => { c.shadowColor = `rgba(20,20,40,${a})`; c.shadowBlur = blur; c.shadowOffsetX = 0; c.shadowOffsetY = dy; };
const sinSombra = (c: Ctx) => { c.shadowColor = "rgba(0,0,0,0)"; c.shadowBlur = 0; c.shadowOffsetY = 0; };
const pathDe = (c: Ctx, pts: P[], close = true) => { c.beginPath(); pts.forEach(([x, y], i) => (i ? c.lineTo(x, y) : c.moveTo(x, y))); if (close) c.closePath(); };
const largo = (s: P[]) => { const acc = [0]; for (let i = 1; i < s.length; i++) acc.push(acc[i - 1] + Math.hypot(s[i][0] - s[i - 1][0], s[i][1] - s[i - 1][1])); return acc; };
const hasta = (s: P[], p: number): P[] => { if (p >= 1) return s; const acc = largo(s), L = acc[acc.length - 1] * p, out: P[] = [s[0]]; for (let i = 1; i < s.length; i++) { if (acc[i] <= L) out.push(s[i]); else { const f = (L - acc[i - 1]) / (acc[i] - acc[i - 1] || 1); out.push([s[i - 1][0] + (s[i][0] - s[i - 1][0]) * f, s[i - 1][1] + (s[i][1] - s[i - 1][1]) * f]); break; } } return out; };
const trazar = (c: Ctx, pts: P[], color: string, w: number, p: number) => { if (p <= 0 || pts.length < 2) return; const s = hasta(pts, p); c.strokeStyle = color; c.lineWidth = w; c.lineCap = "round"; c.lineJoin = "round"; pathDe(c, s, false); c.stroke(); };
const hsl = (hex: string) => { const n = parseInt(hex.slice(1), 16), r = (n >> 16) / 255, g = ((n >> 8) & 255) / 255, b = (n & 255) / 255, mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2; let h = 0, s = 0; if (mx !== mn) { const d = mx - mn; s = l > 0.5 ? d / (2 - mx - mn) : d / (mx + mn); h = mx === r ? (g - b) / d + (g < b ? 6 : 0) : mx === g ? (b - r) / d + 2 : (r - g) / d + 4; h /= 6; } return [h, s, l]; };
const dehsl = (h: number, s: number, l: number) => { const f = (n: number) => { const k = (n + h * 12) % 12, a = s * Math.min(l, 1 - l); return Math.round(255 * (l - a * Math.max(-1, Math.min(k - 3, 9 - k, 1)))).toString(16).padStart(2, "0"); }; return `#${f(0)}${f(8)}${f(4)}`; };
const vivo = (hex: string) => { const [h, s, l] = hsl(hex); return dehsl(h, Math.min(1, s * 1.35 + 0.08), Math.min(0.72, Math.max(0.25, l * 1.1))); };
const oscuro = (hex: string, k: number) => mix(hex, "#1b1b22", Math.max(0, Math.min(0.6, k)));

// ---------------------------------------------------------------- íconos planos (las siluetas de las láminas del #4)
type Pieza = { pts: P[]; fill: string | null; stroke: boolean; c: P; sombra: boolean };
const ICONOS = new Map<string, Pieza[]>();
const piezas = (fig: string): Pieza[] => {
  let v = ICONOS.get(fig); if (v) return v;
  const cuenta = new Map<string, number>(); FIG[fig]().forEach((q: Parte) => { if (q.tinte && !q.solo) cuenta.set(q.tinte, (cuenta.get(q.tinte) ?? 0) + 1); });
  const dom = [...cuenta.entries()].sort((a, b) => b[1] - a[1])[0]?.[0];
  v = FIG[fig]().map((q: Parte): Pieza => {
    const b = bounds(q.pts), c: P = [(b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2], area = (b.x1 - b.x0) * (b.y1 - b.y0), t = q.tono ?? 0.38;
    if (q.borde !== undefined && q.borde < 0.05) return { pts: q.pts, fill: null, stroke: false, c, sombra: true };
    if (q.solo) return area < 900 ? { pts: q.pts, fill: INK, stroke: false, c, sombra: false } : { pts: q.pts, fill: null, stroke: true, c, sombra: false };
    const fill = q.tinte ? vivo(q.tinte) : t < 0.2 ? BLANCO : t >= 0.75 ? "#2B2B30" : dom ? oscuro(vivo(dom), (t - 0.3) * 0.55) : t < 0.45 ? "#EFEBE4" : "#C6C0B5";
    return { pts: q.pts, fill, stroke: true, c, sombra: false };
  });
  ICONOS.set(fig, v); return v;
};
const MED = new Map<string, { c: P; w: number; h: number }>();
export const medida = (fig: string) => { let m = MED.get(fig); if (!m) { const b = bounds(FIG[fig]().flatMap((q) => q.pts)); m = { c: [(b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2], w: b.x1 - b.x0, h: b.y1 - b.y0 }; MED.set(fig, m); } return m; };
/** el ícono se arma: cada pieza aparece en su lugar con un golpecito, de atrás hacia adelante */
export const icono = (c: Ctx, env: Env, fig: string, x: number, y: number, s: number, p: number, k = 1) => {
  if (p <= 0) return; const ps = piezas(fig), n = ps.length;
  ps.forEach((q, i) => {
    const u = p >= 1 ? 1 : clamp01((p - (i / Math.max(1, n)) * 0.5) / 0.5); if (u <= 0) return; const z = golpe(u);
    base(c, env); c.translate(x, y); c.scale(s * k, s * k); c.translate(q.c[0], q.c[1]); c.scale(0.4 + 0.6 * z, 0.4 + 0.6 * z); c.translate(-q.c[0], -q.c[1]); c.globalAlpha = clamp01(u * 3);
    if (q.sombra) { const b = bounds(q.pts), gr = c.createRadialGradient(q.c[0], b.y0 + 4, 2, q.c[0], b.y0 + 4, (b.x1 - b.x0) / 2); gr.addColorStop(0, "rgba(20,20,40,0.16)"); gr.addColorStop(1, "rgba(20,20,40,0)"); c.fillStyle = gr; c.save(); c.translate(q.c[0], b.y0 + 4); c.scale(1, 0.12); c.translate(-q.c[0], -(b.y0 + 4)); c.beginPath(); c.arc(q.c[0], b.y0 + 4, (b.x1 - b.x0) / 2, 0, Math.PI * 2); c.fill(); c.restore(); c.globalAlpha = 1; return; }
    pathDe(c, q.pts); if (q.fill) { c.fillStyle = q.fill; c.fill(); }
    if (q.stroke) { c.strokeStyle = INK; c.lineWidth = 3.4 / (s * k); c.lineJoin = "round"; c.lineCap = "round"; c.stroke(); }
    c.globalAlpha = 1;
  });
};
const encaje = (fig: string, cd: Card, sMax: number) => { const m = medida(fig), s = Math.min(sMax, (cd.w - 80) / m.w, (cd.h - 80) / m.h); return { s, x: cd.cx - m.c[0] * s, y: cd.cy - m.c[1] * s }; };
/** la tarjeta blanca (como un ícono de app) entra con un golpecito */
const baldosa = (c: Ctx, env: Env, cd: Card, p: number) => { if (p <= 0) return; const z = golpe(clamp01(p)), k = 0.86 + 0.14 * z; base(c, env); c.translate(cd.cx, cd.cy + (1 - entra(clamp01(p))) * 30); c.scale(k, k); c.globalAlpha = clamp01(p * 4); sombra(c); c.fillStyle = cd.color === "#f2eadb" || !cd.color ? BLANCO : cd.color; rr(c, -cd.w / 2, -cd.h / 2, cd.w, cd.h, 34); c.fill(); sinSombra(c); c.globalAlpha = 1; };

// ---------------------------------------------------------------- piezas con su tiempo (segundos del video)
export type Elemento = { t: number; d: number; draw: (ctx: Ctx, env: Env, p: number) => void; id?: string };
export type Lapiz = { c: Ctx; env: Env };
let ACENTO = AZUL; // color de la escena que se está armando (lo pone montaje antes de construir cada toma)
export const el = (t: number, d: number, draw: Elemento["draw"]): Elemento => ({ t, d, draw });
export const penE = (t: number, d: number, fn: (g: Lapiz, p: number) => void) => el(t, d, (c, e, p) => { base(c, e); fn({ c, env: e }, p); });
export const grab = (t: number, fig: string, cd: Card, sMax = 1.2, dCut = 0.78): Elemento[] => { const { s, x, y } = encaje(fig, cd, sMax); return [el(t - 0.1, 0.4, (c, e, p) => baldosa(c, e, cd, p)), el(t + 0.02, Math.max(0.45, dCut * 0.7), (c, e, p) => icono(c, e, fig, x, y, s, p))]; };
export const pegada = (t: number, fig: string, cd: Card, sMax = 1.2): Elemento => { const { s, x, y } = encaje(fig, cd, sMax); return el(t - 0.1, 0.45, (c, e, p) => { baldosa(c, e, cd, p); icono(c, e, fig, x, y + (1 - entra(clamp01(p))) * 30, s, 1, 0.86 + 0.14 * golpe(clamp01(p))); }); };
export const grabSuelto = (t: number, fig: string, x: number, y: number, s: number, d = 0.7) => el(t, Math.max(0.45, d), (c, e, p) => { const m = medida(fig); icono(c, e, fig, x - m.c[0] * s, y - m.c[1] * s, s, p); });
/** la palabra clave: letras grandes que suben una tras otra (los números ruedan) y una barra de color que se pinta detrás */
export const tituloT = (t: number, word: string, cx: number, y: number, cap: number, seed: number) => {
  let size = cap * 1.3; const w0 = ancho(word, size, "poppins", size * 0.01); if (w0 > 960) size *= 960 / w0;
  const capPx = capDe(size), yb = y + capPx / 2, n = [...word].length, D = Math.max(0.75, 0.45 + 0.03 * n), color = ACENTO, w = ancho(word, size, "poppins", size * 0.01);
  const tiles = disponer(word, size, "poppins", size * 0.01).out.map((g) => ({ x: cx - w / 2 + g.x + g.w / 2, y }));
  return { tiles, e: el(t - 0.06, D, (c, e, p) => {
    const q = mueve(seg(p, D, 0.12, 0.42)); if (q > 0) { base(c, e); c.fillStyle = mix(color, "#ffffff", 0.42); const x0 = cx - w / 2 - size * 0.16; c.fillRect(x0, yb - capPx * 0.62, (w + size * 0.32) * q, capPx * 0.62 + size * 0.14); }
    textoSube(c, e, word, cx, yb, size, INK, p, D, "poppins", "c", size * 0.01, true);
  }) };
};
export const titulo = (t: number, word: string, cx: number, y: number, cap: number, seed: number) => tituloT(t, word, cx, y, cap, seed).e;
/** etiqueta: una pastilla blanca que aparece y el texto sube adentro */
export const tiraE = (t: number, text: string, x: number, y: number, cap: number, rot = 0, seed = 1, cps = 26): Elemento => {
  const size = cap * 0.92, f: Fuente = "inter", tw = ancho(text, size, f, size * 0.03), h = size * 1.95, pw = tw + size * 1.5, D = 0.5 + Math.min(0.4, [...text].length * 0.018);
  void rot; void seed; void cps;
  return el(t - 0.06, D, (c, e, p) => {
    const a = entra(seg(p, D, 0, 0.3)); if (a <= 0) return;
    base(c, e); c.translate(x, y); c.scale(0.9 + 0.1 * a, 0.9 + 0.1 * a); c.globalAlpha = clamp01(a * 2); sombra(c, 22, 7, 0.14); c.fillStyle = BLANCO; rr(c, -pw / 2, -h / 2, pw, h, h / 2); c.fill(); sinSombra(c); c.globalAlpha = 1;
    textoSube(c, e, text, x, y + capDe(size, f) / 2, size, INK, seg(p, D, 0.08, D - 0.08), D - 0.08, f, "c", size * 0.03);
  });
};
export const tipoE = (t: number, text: string, x: number, y: number, cap: number, rot = 0, seed = 1, cps = 26) => { void rot; void seed; void cps; const size = cap * 0.95, D = 0.45; return el(t - 0.04, D, (c, e, p) => textoSube(c, e, text, x, y + capDe(size, "inter") / 2, size, INK, p, D, "inter", "c", size * 0.03)); };
/** insignia: borde y letras del color, entra con golpe (el sello del #4, en limpio) */
export const selloE = (t: number, x: number, y: number, rot: number, big: string, color = RED, cap = 40, small = "") => {
  void small; const size = cap * 1.0, tw = ancho(big, size, "poppins", size * 0.04), w = tw + size * 1.1, h = size * 1.75, D = 0.5;
  return el(t - 0.06, D, (c, e, p) => {
    const u = seg(p, D, 0, 0.42); if (u <= 0) return; const z = golpe(u), k = 0.55 + 0.45 * z;
    base(c, e); c.translate(x, y); c.rotate(rot * z); c.scale(k, k); c.globalAlpha = clamp01(u * 4);
    sombra(c, 18, 6, 0.12); c.fillStyle = mix(color, "#ffffff", 0.88); rr(c, -w / 2, -h / 2, w, h, 16); c.fill(); sinSombra(c);
    c.strokeStyle = color; c.lineWidth = size * 0.11; rr(c, -w / 2, -h / 2, w, h, 16); c.stroke();
    c.fillStyle = color; const k2 = size / TIPOS.poppins.upm; let cx = -tw / 2; for (const ch of big) { if (ch !== " ") { c.save(); c.translate(cx, capDe(size) / 2); c.scale(k2, -k2); c.fill(gpath("poppins", ch)); c.restore(); } cx += adv("poppins", ch) * k2 + size * 0.04; }
    c.globalAlpha = 1;
  });
};
const COLOR_TIPO: Record<Tipo, string> = { nino: AMARILLO, joven: AZUL, mujer: CORAL, abuelo: VIOLETA, adulto: MENTA };
/** avatar: círculo de color con la silueta de perfil (las del #4) y un aro blanco */
export const avatar = (c: Ctx, env: Env, x: number, y: number, s: number, tipo: Tipo, p: number) => {
  if (p <= 0) return; const z = golpe(clamp01(p)), k = 0.5 + 0.5 * z, r = 118 * s, sil = silueta(tipo);
  base(c, env); c.translate(x, y); c.scale(k, k); c.globalAlpha = clamp01(p * 4);
  sombra(c, 24, 8, 0.15); c.fillStyle = BLANCO; c.beginPath(); c.arc(0, 0, r + 7 * s, 0, Math.PI * 2); c.fill(); sinSombra(c);
  c.fillStyle = COLOR_TIPO[tipo]; c.beginPath(); c.arc(0, 0, r, 0, Math.PI * 2); c.fill();
  c.save(); c.beginPath(); c.arc(0, 0, r, 0, Math.PI * 2); c.clip(); c.scale(0.95 * s, 0.95 * s); c.translate(0, 8); c.fillStyle = INK; sil.partes.forEach((pp) => { pathDe(c, pp); c.fill(); });
  c.strokeStyle = "rgba(255,255,255,0.85)"; c.lineWidth = 2.2 / s; c.lineCap = "round"; sil.oro.forEach((ln) => { pathDe(c, ln, false); c.stroke(); }); c.restore();
  c.globalAlpha = 1;
};
export const camE = (t: number, x: number, y: number, s: number, tipo: Tipo, seed = 1) => { void seed; return el(t - 0.06, 0.45, (c, e, p) => avatar(c, e, x, y, s, tipo, p)); };
export const signo = (g: Lapiz, ch: string, x: number, y: number, cap: number, p: number, seed: number, color = REDPEN) => {
  void seed; if (p <= 0) return; const size = cap * 1.25, z = golpe(clamp01(p)), w = adv("poppins", ch) * size / TIPOS.poppins.upm;
  base(g.c, g.env); g.c.translate(x, y); g.c.rotate((1 - z) * -0.35); g.c.scale(0.4 + 0.6 * z, 0.4 + 0.6 * z); g.c.globalAlpha = clamp01(p * 4); g.c.fillStyle = color; letra(g.c, "poppins", ch, -w / 2, capDe(size) / 2, size); g.c.globalAlpha = 1;
};
export const preg = (t: number, x: number, y: number, cap: number, color = REDPEN) => penE(t - 0.04, 0.4, (g, p) => signo(g, "?", x, y, cap, p, 1, color));
export const mano = (g: Lapiz, text: string, x: number, y: number, cap: number, p: number, seed: number, color = REDPEN, w = 3.4) => { void seed; void w; const size = cap * 1.2; textoSube(g.c, g.env, text, x, y + capDe(size) / 2, size, color, p, 0.6, "poppins", "c", size * 0.01); };
export const manoE = (t: number, text: string, x: number, y: number, cap: number, d = 0.45, color = REDPEN, w = 3.4) => penE(t - 0.04, Math.max(0.5, d), (g, p) => mano(g, text, x, y, cap, p, 1, color, w));

// ---------------------------------------------------------------- trazos limpios (las anotaciones del #4)
export const trazo = (g: Lapiz, pts: P[], color: string, w: number, p: number, seed: number, taper = 0.4, curva = true) => { void seed; void taper; trazar(g.c, curva && pts.length > 2 ? smooth(pts, false, 10) : pts, color, w * 1.25, entra(clamp01(p))); };
export const poli = (g: Lapiz, pts: P[], color: string, w: number, p: number, seed: number) => { void seed; trazar(g.c, pts, color, w * 1.25, entra(clamp01(p))); };
export const flecha = (g: Lapiz, pts: P[], color: string, w: number, p: number, seed: number) => {
  void seed; if (p <= 0) return; const s = smooth(pts, false, 12), q = entra(clamp01(p / 0.8)), ww = w * 1.35; trazar(g.c, s, color, ww, q);
  if (p > 0.55) { const z = golpe(clamp01((p - 0.55) / 0.45)), a = s[s.length - 1], b = s[Math.max(0, s.length - 6)], ang = Math.atan2(a[1] - b[1], a[0] - b[0]), L = ww * 4.2 * z; base(g.c, g.env); g.c.fillStyle = color; g.c.translate(a[0], a[1]); g.c.rotate(ang); g.c.beginPath(); g.c.moveTo(L * 0.35, 0); g.c.lineTo(-L * 0.8, -L * 0.55); g.c.lineTo(-L * 0.8, L * 0.55); g.c.closePath(); g.c.fill(); base(g.c, g.env); }
};
export const lazo = (g: Lapiz, cx: number, cy: number, rx: number, ry: number, color: string, w: number, p: number, seed: number) => { void seed; const pts: P[] = []; for (let k = 0; k <= 48; k++) { const u = -1.9 + (k / 48) * 6.6; pts.push([cx + Math.cos(u) * rx, cy + Math.sin(u) * ry]); } trazar(g.c, pts, color, w * 1.3, mueve(clamp01(p))); };
export const subraya = (g: Lapiz, x0: number, x1: number, y: number, color: string, w: number, p: number, seed: number, ondas = false) => { void seed; const pts: P[] = []; for (let k = 0; k <= 24; k++) { const u = k / 24; pts.push([x0 + (x1 - x0) * u, y + (ondas ? Math.sin(u * 12.5) * 5 : 0)]); } trazar(g.c, pts, color, w * 1.5, entra(clamp01(p))); };
export const chulo = (g: Lapiz, x: number, y: number, r: number, p: number, seed: number, color = VERDE) => { void seed; trazar(g.c, [[x - r, y - r * 0.02], [x - r * 0.3, y + r * 0.62], [x + r, y - r * 0.8]], color, Math.max(6, r * 0.24), entra(clamp01(p))); };
export const tacha = (g: Lapiz, x: number, y: number, r: number, p: number, seed: number, color = REDPEN) => { void seed; const w = Math.max(7, r * 0.12); trazar(g.c, [[x - r, y - r], [x + r, y + r]], color, w, entra(clamp01(p * 2))); if (p > 0.5) trazar(g.c, [[x + r, y - r], [x - r, y + r]], color, w, entra(clamp01(p * 2 - 1))); };
export const tachar = (g: Lapiz, x0: number, x1: number, y: number, p: number, seed: number, color = REDPEN, w = 5) => { void seed; trazar(g.c, [[x0, y], [x1, y]], color, w * 1.3, entra(clamp01(p))); };
export const punteado = (g: Lapiz, pts: P[], color: string, w: number, p: number, seed: number, on = 12, off = 9) => { void seed; g.c.setLineDash([on, off]); trazar(g.c, resample(smooth(pts, false, 10), 120), color, w * 1.2, mueve(clamp01(p))); g.c.setLineDash([]); };
export const linea = (g: Lapiz, x0: number, x1: number, y: number, p: number, seed: number, marcas = 10, color = INK) => {
  void seed; if (p <= 0) return; trazar(g.c, [[x0, y], [x1 - 6, y]], color, 5, entra(clamp01(p / 0.6)));
  for (let k = 0; k <= marcas; k++) { const u = clamp01((p - 0.2 - (k / marcas) * 0.5) / 0.2); if (u <= 0) continue; const x = x0 + ((x1 - x0 - 30) * k) / marcas, z = golpe(u), r = (k % 5 ? 6 : 10) * z; base(g.c, g.env); g.c.fillStyle = k % 5 ? color : CORAL; g.c.beginPath(); g.c.arc(x, y, r, 0, Math.PI * 2); g.c.fill(); }
  if (p > 0.6) { const z = golpe(clamp01((p - 0.6) / 0.3)), L = 22 * z; base(g.c, g.env); g.c.fillStyle = color; g.c.beginPath(); g.c.moveTo(x1 + 4, y); g.c.lineTo(x1 - L, y - L * 0.6); g.c.lineTo(x1 - L, y + L * 0.6); g.c.closePath(); g.c.fill(); }
};
export const medidor = (g: Lapiz, cx: number, cy: number, r: number, valor: number, p: number, seed: number) => {
  void seed; if (p <= 0) return; const c = g.c, a0 = Math.PI, q = entra(clamp01(p / 0.45));
  base(c, g.env); c.lineCap = "round"; c.strokeStyle = GRIS; c.lineWidth = 34; c.beginPath(); c.arc(cx, cy, r, a0, a0 + Math.PI * q); c.stroke();
  const v = valor * entra(clamp01((p - 0.35) / 0.65)); if (v > 0) { c.strokeStyle = CORAL; c.beginPath(); c.arc(cx, cy, r, a0, a0 + Math.PI * v); c.stroke(); }
  for (let k = 0; k <= 10; k++) { const u = clamp01((p - 0.25 - k * 0.025) / 0.15); if (u <= 0) continue; const a = a0 + Math.PI * (k / 10), r0 = r - 40, r1 = r - (k % 5 ? 54 : 66); trazar(c, [[cx + Math.cos(a) * r0, cy + Math.sin(a) * r0], [cx + Math.cos(a) * (r0 + (r1 - r0) * u), cy + Math.sin(a) * (r0 + (r1 - r0) * u)]], INK, k % 5 ? 3 : 5, 1); }
  if (p > 0.35) { const a = a0 + Math.PI * v; base(c, g.env); trazar(c, [[cx, cy], [cx + Math.cos(a) * (r - 70), cy + Math.sin(a) * (r - 70)]], INK, 9, 1); c.fillStyle = INK; c.beginPath(); c.arc(cx, cy, 16, 0, Math.PI * 2); c.fill(); }
};
export const regla = (c: Ctx, env: Env, x: number, y0: number, y1: number, p: number) => {
  if (p <= 0) return; base(c, env); const q = entra(clamp01(p * 1.6)); c.fillStyle = mix(AMARILLO, "#ffffff", 0.35); sombra(c, 14, 4, 0.12); rr(c, x - 22, y1 - (y1 - y0) * q, 44, (y1 - y0) * q, 10); c.fill(); sinSombra(c);
  const n = Math.floor((y1 - y0) / 40); for (let k = 0; k <= n; k++) { const y = y1 - k * 40; if (y < y1 - (y1 - y0) * q + 8) continue; trazar(c, [[x - 22, y], [x - 22 + (k % 2 ? 14 : 26), y]], INK, 3, 1); }
};
export const barra = (c: Ctx, env: Env, x0: number, x1: number, yBase: number, yTop: number, p: number, color: string, seed: number) => {
  void seed; if (p <= 0) return; const yc = yBase - (yBase - yTop) * entra(clamp01(p)); base(c, env); sombra(c, 16, 6, 0.12); c.fillStyle = color === REDPEN ? CORAL : color; rr(c, x0, yc, x1 - x0, yBase - yc, 12); c.fill(); sinSombra(c);
  c.fillStyle = "rgba(255,255,255,0.22)"; c.fillRect(x0 + 10, yc + 10, 10, Math.max(0, yBase - yc - 20));
};
export const celularPluma = (g: Lapiz, x: number, y: number, s: number, p: number, seed: number, rot = 0) => {
  void seed; if (p <= 0) return; const z = golpe(clamp01(p)), c = g.c; base(c, g.env); c.translate(x, y); c.rotate(rot); c.scale(s * (0.4 + 0.6 * z), s * (0.4 + 0.6 * z)); c.globalAlpha = clamp01(p * 4);
  c.fillStyle = INK; rr(c, -24, -42, 48, 84, 10); c.fill(); c.fillStyle = mix(AZUL, "#ffffff", 0.55); rr(c, -18, -34, 36, 66, 5); c.fill(); c.globalAlpha = 1;
};
export const notaMusical = (g: Lapiz, x: number, y: number, s: number, p: number, seed: number, color = NAVY) => {
  void seed; if (p <= 0) return; const z = golpe(clamp01(p)), c = g.c; base(c, g.env); c.translate(x, y - (1 - entra(clamp01(p))) * 30); c.scale(s * z, s * z); c.globalAlpha = clamp01(p * 3); c.fillStyle = color;
  c.beginPath(); c.ellipse(0, 0, 11, 8, -0.4, 0, Math.PI * 2); c.fill(); c.fillRect(7, -46, 5, 46); c.beginPath(); c.moveTo(12, -46); c.quadraticCurveTo(30, -36, 24, -18); c.quadraticCurveTo(24, -30, 12, -34); c.closePath(); c.fill(); c.globalAlpha = 1;
};
export const corazon = (g: Lapiz, x: number, y: number, s: number, p: number, seed: number, color = REDPEN) => { void seed; if (p <= 0) return; const z = golpe(clamp01(p)), c = g.c; base(c, g.env); c.translate(x, y); c.scale(0.3 + 0.7 * z, 0.3 + 0.7 * z); c.translate(-x, -y); c.globalAlpha = clamp01(p * 4); c.fillStyle = color === REDPEN ? CORAL : color; pathDe(c, smooth(heart(x, y, s), true, 6)); c.fill(); c.globalAlpha = 1; };
export const nube = (g: Lapiz, cx: number, cy: number, rx: number, ry: number, p: number, seed: number, color = NAVY, w = 3.6) => {
  void seed; void w; if (p <= 0) return; const z = entra(clamp01(p)), c = g.c, pts: P[] = [];
  for (let k = 0; k < 9; k++) { const a0 = (k / 9) * 6.283, a1 = ((k + 1) / 9) * 6.283; for (let j = 0; j <= 6; j++) { const u = j / 6, a = a0 + (a1 - a0) * u, b = 1 + Math.sin(u * Math.PI) * 0.18; pts.push([cx + Math.cos(a) * rx * b, cy + Math.sin(a) * ry * b]); } }
  base(c, g.env); c.translate(cx, cy); c.scale(0.85 + 0.15 * z, 0.85 + 0.15 * z); c.translate(-cx, -cy); c.globalAlpha = clamp01(p * 2.5); c.fillStyle = mix(color, "#ffffff", 0.86); pathDe(c, pts); c.fill(); c.strokeStyle = mix(color, "#ffffff", 0.35); c.lineWidth = 4; c.setLineDash([2, 12]); c.lineCap = "round"; c.stroke(); c.setLineDash([]); c.globalAlpha = 1;
};
export const luna = (g: Lapiz, cx: number, cy: number, r: number, p: number, seed: number, color = MUSTARD) => { void seed; if (p <= 0) return; const z = golpe(clamp01(p)), c = g.c; base(c, g.env); c.translate(cx, cy); c.rotate((1 - z) * -0.8); c.scale(z, z); c.fillStyle = color; c.beginPath(); c.arc(0, 0, r, 0.95, 5.33, false); c.arc(r * 0.45, -r * 0.1, r * 0.82, 4.9, 1.38, true); c.closePath(); c.fill(); };
export const estrella = (g: Lapiz, x: number, y: number, r: number, p: number, seed: number, color = MUSTARD) => { void seed; if (p <= 0) return; const z = golpe(clamp01(p)), c = g.c, pts: P[] = []; for (let k = 0; k < 8; k++) { const a = (k / 8) * 6.283 - Math.PI / 2, q = k % 2 ? r * 0.3 : r; pts.push([Math.cos(a) * q, Math.sin(a) * q]); } base(c, g.env); c.translate(x, y); c.rotate((1 - z) * 1.2); c.scale(z, z); c.fillStyle = color; pathDe(c, smooth(pts, true, 3)); c.fill(); };
export const diana = (g: Lapiz, cx: number, cy: number, r: number, p: number, seed: number) => {
  void seed; if (p <= 0) return; const c = g.c; [1, 0.78, 0.56, 0.34, 0.14].forEach((k, i) => { const u = clamp01((p - i * 0.09) / 0.35); if (u <= 0) return; const z = golpe(u); base(c, g.env); c.fillStyle = i % 2 ? BLANCO : CORAL; if (i === 0) sombra(c, 20, 6, 0.14); c.beginPath(); c.arc(cx, cy, r * k * z, 0, Math.PI * 2); c.fill(); sinSombra(c); });
  if (p > 0.6) flecha(g, [[cx + r * 1.3, cy - r * 1.1], [cx + r * 0.6, cy - r * 0.5], [cx + 4, cy - 3]], INK, 5, clamp01((p - 0.6) / 0.4), 1);
};
export const avion = (g: Lapiz, x: number, y: number, s: number, p: number, seed: number, rot = 0, color = NAVY) => {
  void seed; void color; if (p <= 0) return; const q = entra(clamp01(p)), c = g.c, dx = -Math.cos(rot) * 120 * (1 - q), dy = -Math.sin(rot) * 120 * (1 - q);
  base(c, g.env); c.translate(x + dx, y + dy); c.rotate(rot); c.scale(s, s); c.globalAlpha = clamp01(p * 3); sombra(c, 12, 5, 0.14); c.fillStyle = BLANCO; pathDe(c, [[34, 0], [-50, -32], [-28, 2], [-50, 32]]); c.fill(); sinSombra(c); c.strokeStyle = INK; c.lineWidth = 3.2 / s; c.lineJoin = "round"; c.stroke(); trazar(c, [[-28, 2], [34, 0]], INK, 2.6 / s, 1); c.globalAlpha = 1;
};
export const lupa = (g: Lapiz, x: number, y: number, r: number, p: number, seed: number, rot = 0.75, color = NAVY) => {
  void seed; void color; if (p <= 0) return; const z = golpe(clamp01(p)), c = g.c, co = Math.cos(rot), si = Math.sin(rot); base(c, g.env); c.translate(x, y); c.scale(0.4 + 0.6 * z, 0.4 + 0.6 * z); c.translate(-x, -y); c.globalAlpha = clamp01(p * 3);
  c.fillStyle = "rgba(47,91,255,0.12)"; c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.fill(); c.strokeStyle = INK; c.lineWidth = 9; c.stroke(); trazar(c, [[x + co * r * 1.08, y + si * r * 1.08], [x + co * r * 2.05, y + si * r * 2.05]], INK, 15, 1); c.globalAlpha = 1;
};
export const sobrePluma = (g: Lapiz, x: number, y: number, w: number, h: number, p: number, seed: number, color = NAVY) => { void seed; void color; if (p <= 0) return; const z = golpe(clamp01(p)), c = g.c; base(c, g.env); c.translate(x, y); c.scale(z, z); c.globalAlpha = clamp01(p * 3); c.fillStyle = BLANCO; rr(c, -w / 2, -h / 2, w, h, 6); c.fill(); c.strokeStyle = INK; c.lineWidth = 3; c.stroke(); trazar(c, [[-w / 2 + 4, -h / 2 + 4], [0, h * 0.1], [w / 2 - 4, -h / 2 + 4]], INK, 3, 1); c.globalAlpha = 1; };
export const etiqueta = (g: Lapiz, x: number, y: number, s: number, p: number, seed: number, text = "$$", rot = -0.22) => {
  void seed; if (p <= 0) return; const z = golpe(clamp01(p)), c = g.c; base(c, g.env); c.translate(x, y); c.rotate(rot); c.scale(s * z, s * z); c.globalAlpha = clamp01(p * 3);
  sombra(c, 16, 5, 0.14); c.fillStyle = AMARILLO; pathDe(c, [[-80, -40], [52, -40], [92, 0], [52, 40], [-80, 40]]); c.fill(); sinSombra(c); c.fillStyle = BLANCO; c.beginPath(); c.arc(60, 0, 9, 0, Math.PI * 2); c.fill();
  const size = 54; c.fillStyle = INK; let cx = -14 - ancho(text, size) / 2; for (const ch of text) { letra(c, "poppins", ch, cx, capDe(size) / 2, size); cx += adv("poppins", ch) * size / TIPOS.poppins.upm; } c.globalAlpha = 1;
};
/** hoja con texto (documento, lista, resumen): la tarjeta entra y las líneas suben una tras otra; la primera en rojo */
export const hojaTexto = (c: Ctx, env: Env, cd: Card, lineas: string[], p: number, cap = 26, caida = 0.35) => {
  if (p <= 0) return; baldosa(c, env, { ...cd, color: BLANCO }, clamp01(p / caida)); if (p <= caida * 0.6) return;
  const D = 0.9; lineas.forEach((ln, i) => { const q = clamp01((p - caida * 0.6 - i * 0.1) / 0.4); const f: Fuente = i === 0 ? "poppins" : "inter", size = i === 0 ? cap * 1.0 : cap * 0.98; textoSube(c, env, ln, cd.cx - cd.w / 2 + 30, cd.cy - cd.h / 2 + 52 + i * cap * 1.8, size, i === 0 ? ROJO : INK, q, D * 0.4, f, "l", size * 0.02); });
};
export const perfil = (c: Ctx, env: Env, cd: Card, tipo: Tipo, nombre: string, p: number) => {
  if (p <= 0) return; baldosa(c, env, { ...cd, color: BLANCO }, clamp01(p / 0.4)); if (p <= 0.25) return;
  avatar(c, env, cd.cx - cd.w / 2 + 64, cd.cy, 0.4, tipo, clamp01((p - 0.25) / 0.4));
  const q = clamp01((p - 0.45) / 0.55); textoSube(c, env, nombre, cd.cx - cd.w / 2 + 122, cd.cy - 8, 27, INK, q, 0.4, "inter", "l");
  base(c, env); c.fillStyle = GRIS; [0, 1].forEach((k) => { const u = entra(clamp01(q * 2 - k * 0.4)); rr(c, cd.cx - cd.w / 2 + 122, cd.cy + 14 + k * 24, (cd.w - 160 - k * 50) * u, 11, 5.5); c.fill(); });
};
export const papelVolando = (c: Ctx, env: Env, ruta: P[], w: number, h: number, p: number, seed: number, texto = "") => {
  void seed; if (p <= 0) return; const s = resample(smooth(ruta, false, 10), 160), q = mueve(clamp01(p)), i = Math.min(s.length - 1, Math.round(q * (s.length - 1))), [x, y] = s[i], vuelo = Math.sin(Math.PI * q);
  base(c, env); c.translate(x, y - 14 * vuelo); c.rotate(Math.sin(q * 9) * 0.1 * vuelo); c.globalAlpha = clamp01(p * 5); sombra(c, 16 + 20 * vuelo, 6 + 12 * vuelo, 0.16); c.fillStyle = BLANCO; rr(c, -w / 2, -h / 2, w, h, 12); c.fill(); sinSombra(c);
  c.fillStyle = mix(AZUL, "#ffffff", 0.2); c.fillRect(-w / 2, -h / 2 + 8, 6, h - 16);
  if (texto) { const size = Math.min(26, (w - 30) / (texto.length * 0.7)); const tw = ancho(texto, size, "inter"); c.fillStyle = INK; const k = size / TIPOS.inter.upm; let cx = -tw / 2; for (const ch of texto) { if (ch !== " ") { c.save(); c.translate(cx, capDe(size, "inter") / 2); c.scale(k, -k); c.fill(gpath("inter", ch)); c.restore(); } cx += adv("inter", ch) * k; } }
  c.globalAlpha = 1;
};

// ---------------------------------------------------------------- fondo: papel claro con manchas de color que se mueven despacio
const fondo = (c: Ctx, env: Env, a: string, b: string, t: number) => {
  c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1; c.globalCompositeOperation = "source-over"; base(c, env);
  c.fillStyle = PAPEL; c.fillRect(0, 0, W, H);
  const manchas: [string, number, number, number, number][] = [[a, 0.30, 180, 360, 760], [b, 0.20, 930, 820, 680], [a, 0.16, 520, 1520, 820], ["#ffffff", 0.55, 760, 220, 520]];
  manchas.forEach(([col, al, x0, y0, r], k) => { const x = x0 + Math.sin(t * 0.21 + k * 1.7) * 70, y = y0 + Math.cos(t * 0.17 + k * 2.3) * 90, gr = c.createRadialGradient(x, y, 0, x, y, r); const n = parseInt(col.slice(1), 16); const rgb = `${n >> 16},${(n >> 8) & 255},${n & 255}`; gr.addColorStop(0, `rgba(${rgb},${al})`); gr.addColorStop(1, `rgba(${rgb},0)`); c.fillStyle = gr; c.fillRect(0, 0, W, H); });
};
const grano = (c: Ctx, env: Env) => { const g = new Gfx(c, env, 0, PEN); g.paper("paper", 0.05); };
const pinta = (col: string, k: number) => PALETA[(PALETA.indexOf(col) + k) % PALETA.length];

// ---------------------------------------------------------------- montaje: una escena por toma; la anterior sube y se va
export const montaje = (pref: string, esc: Record<string, number>, orden: string[], tomas: Record<string, () => Elemento[]>, dur: number, salida = 9): Shot[] => {
  const F = (t: number) => Math.round(t * FPS), D = F(dur), fin = (i: number) => (i + 1 < orden.length ? esc[orden[i + 1]] : dur);
  const acentos = orden.map((_, i) => PALETA[i % PALETA.length]);
  const run = orden.map((n, i) => {
    ACENTO = acentos[i];
    const t0 = esc[n], fr = (t: number) => Math.round((t - t0) * FPS), steps: Step[] = [{ id: `${pref}-${n}-0`, start: -1, end: 0, draw: () => {} }];
    tomas[n]().forEach((e, k) => { const a = Math.max(0, fr(e.t)), b = Math.max(a + 1, fr(e.t + e.d)); steps.push({ id: `${pref}-${n}-${k}`, start: a, end: b, draw: (c, env, p) => e.draw(c, env, p) }); });
    return staged(`${pref}-${n}`, steps);
  });
  const len = orden.map((n, i) => F(fin(i)) - F(esc[n]));
  const capa = (env: Env, key: string) => { const DW = Math.round(env.W * env.scale), DH = Math.round(env.H * env.scale), k = `${pref}:${key}:${DW}x${DH}`; let L = env.cache.get(k) as Layer | undefined; if (!L) { L = env.canvas(DW, DH); env.cache.set(k, L); } L.ctx.setTransform(1, 0, 0, 1, 0, 0); L.ctx.globalAlpha = 1; L.ctx.globalCompositeOperation = "source-over"; L.ctx.clearRect(0, 0, DW, DH); return L; };
  const camara = (local: number, n: number) => 1 + 0.028 * mueve(clamp01(local / Math.max(1, n)));
  const pon = (ctx: Ctx, env: Env, L: Layer, k: number, dy: number, alpha: number) => { const s = env.scale; ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = alpha; ctx.translate(540 * s, (700 + dy) * s); ctx.scale(k, k); ctx.translate(-540 * s, -700 * s); ctx.drawImage(L.canvas as CanvasImageSource, 0, 0); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; };
  const shot = (i: number) => (ctx: Ctx, local: number, env: Env) => {
    const DW = Math.round(env.W * env.scale), DH = Math.round(env.H * env.scale), t = (F(esc[orden[i]]) + local) / FPS;
    if (i >= 2) env.cache.delete(`${pref}-${orden[i - 2]}:base:${DW}x${DH}`); // esa escena ya no vuelve
    const mezcla = i === 0 ? 1 : mueve(clamp01(local / 14)), a = i === 0 ? acentos[0] : mix(acentos[i - 1], acentos[i], mezcla), b = i === 0 ? pinta(acentos[0], 2) : mix(pinta(acentos[i - 1], 2), pinta(acentos[i], 2), mezcla);
    fondo(ctx, env, a, b, t);
    if (i > 0 && local < salida) { const A = capa(env, "antes"); run[i - 1](A.ctx, len[i - 1] - 1, env); const q = sale(clamp01((local + 1) / salida)); pon(ctx, env, A, camara(len[i - 1], len[i - 1]), -150 * q, 1 - q); }
    const B = capa(env, "ahora"); run[i](B.ctx, local, env); pon(ctx, env, B, camara(local, len[i]), 0, 1);
    grano(ctx, env);
  };
  return orden.map((n, i) => ({ id: n, start: F(esc[n]), end: i + 1 < orden.length ? F(esc[orden[i + 1]]) : D, draw: shot(i) }));
};
