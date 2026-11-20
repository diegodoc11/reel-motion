// reel-motion · ESCENAS del estilo MOTION DESIGN (motor AniDoodle). Ejemplo: el reel ERA (1:17). Es la MISMA lista de
// escenas que la pizarra animada (mismas funciones: titulo, grab, tarjeta, sello...); cambia el kit: movimiento.ts.
import type { Gfx } from "./core";
import type { Film } from "./film";
import { DUR, ESC, WORDS } from "./reelTiempos";
import {
  FPS, NAVY, RED, REDPEN, VERDE, barra, camE, chulo, clamp01, el, flecha, grab, lazo, linea, mano, medidor, notaMusical, pegada, penE,
  preg, punteado, regla, selloE, signo, subraya, tacha, tachar, tarjeta, tiraE, tipoE, titulo, tituloT, tpOf, trazo, celularPluma, montaje,
  type Elemento,
} from "./movimiento";

const F = (t: number) => Math.round(t * FPS), DURATION = F(DUR), tp = tpOf(WORDS), pen = penE;
const rayitos = (g: Parameters<typeof trazo>[0], cx: number, cy: number, rx: number, ry: number, p: number, seed: number) => {
  [-2.6, -2.0, -1.15, -0.55, 0.55, 1.15, 2.0, 2.6].forEach((a, k) => { const q = clamp01(p * 2 - k * 0.12); if (q <= 0) return; const c = Math.cos(a), s = Math.sin(a); trazo(g, [[cx + c * rx, cy + s * ry], [cx + c * (rx + 60), cy + s * (ry + 60)]], REDPEN, 5, q, seed + k, 0.4, false); });
};

const TOMAS: Record<string, () => Elemento[]> = {
  A: () => {
    const cH = tarjeta(290, 690, 420, 350, -0.05, 11), cC = tarjeta(795, 745, 440, 350, 0.06, 12);
    return [
      titulo(0.06, "13 AÑOS", 540, 270, 124, 3),
      pen(tp("tardamos") - 0.02, 0.55, (g, p) => subraya(g, 330, 750, 398, REDPEN, 5, p, 21, true)),
      ...grab(tp("caballo"), "caballo", cH),
      pen(tp("movernos", tp("caballo")) - 0.04, 0.42, (g, p) => flecha(g, [[455, 488], [548, 438], [642, 505]], REDPEN, 5, p, 31)),
      ...grab(tp("carro"), "carro", cC),
      tiraE(tp("1900"), "1900", 290, 940, 46, -0.04, 41),
      tiraE(tp("1913"), "1913", 795, 995, 46, 0.03, 42),
      pen(tp("1913") + 0.32, 0.45, (g, p) => punteado(g, [[372, 968], [540, 1078], [706, 1018]], REDPEN, 3.5, p, 51)),
    ];
  },
  B: () => {
    const cS = tarjeta(330, 760, 450, 330, -0.04, 13), cR = tarjeta(790, 570, 330, 370, 0.07, 14);
    return [
      ...grab(tp("época"), "caracol", cS),
      ...grab(tp("movían"), "reloj", cR),
      pen(tp("mucho", tp("movían")) - 0.04, 0.5, (g, p) => [[452, 552, 34], [500, 502, 44], [552, 446, 56]].forEach(([x, y, cap], k) => signo(g, "Z", x, y, cap, clamp01(p * 3 - k), 61 + k, NAVY))),
      tiraE(tp("más", tp("mucho")) - 0.08, "MÁS DESPACIO", 540, 285, 54, -0.02, 43, 30),
      pen(tp("despacio") + 0.1, 0.36, (g, p) => subraya(g, 262, 818, 330, REDPEN, 4.5, p, 71, true)),
    ];
  },
  C: () => [
    pen(tp("Saltemos") - 0.06, 0.55, (g, p) => linea(g, 110, 970, 880, p, 81)),
    tipoE(tp("Saltemos") + 0.2, "1913", 150, 936, 34, 0, 82),
    pen(tp("para", ESC.C) - 0.06, 0.6, (g, p) => flecha(g, [[150, 850], [320, 610], [540, 548], [760, 615], [900, 840]], REDPEN, 5, p, 83)),
    pen(tp("adelante") + 0.18, 0.3, (g, p) => signo(g, "?", 900, 755, 72, p, 84)),
    titulo(tp("segundo"), "SALTO 2", 540, 285, 116, 5),
    tiraE(tp("tecnológico"), "TECNOLÓGICO", 540, 452, 46, 0.02, 44, 30),
    pen(tp("hemos") - 0.02, 0.34, (g, p) => subraya(g, 330, 750, 486, REDPEN, 4.5, p, 85)),
  ],
  D: () => {
    const cP = tarjeta(540, 700, 380, 480, 0.03, 15);
    return [
      ...grab(tp("smartphone"), "celular", cP, 1.3),
      titulo(tp("2007"), "2007", 540, 285, 140, 7),
      pen(tp("aparece") - 0.04, 0.4, (g, p) => rayitos(g, 540, 700, 245, 295, p, 91)),
      selloE(tp("primer"), 760, 985, -0.1, "PRIMER IPHONE", RED, 36),
    ];
  },
  E: () => {
    const cM = tarjeta(540, 660, 380, 380, -0.03, 16);
    const pos = [155, 118, 62, 25, 205, 335].map((a) => { const r = (a * Math.PI) / 180; return [540 + Math.cos(r) * 335, 660 - Math.sin(r) * 240, (a - 90) * 0.004] as [number, number, number]; });
    return [
      pen(tp("Desde", ESC.E) - 0.02, 0.7, (g, p) => linea(g, 110, 970, 1010, p, 101)),
      tipoE(tp("punto") + 0.2, "2007", 150, 1064, 34, 0, 102),
      ...grab(tp("mundo", ESC.E), "mundo", cM),
      pen(tp("smartphone", ESC.E) - 0.04, 0.6, (g, p) => pos.forEach(([x, y, r], k) => celularPluma(g, x, y, 1.0, clamp01(p * 2.2 - k * 0.24), 110 + k, r))),
      titulo(tp("siete"), "7 AÑOS", 540, 280, 120, 9),
      tipoE(tp("años", tp("siete")), "2014", 930, 1064, 34, 0, 103),
      pen(tp("Ahora") - 0.1, 0.4, (g, p) => punteado(g, [[160, 985], [540, 922], [925, 985]], REDPEN, 3.5, p, 104)),
    ];
  },
  F: () => [
    pen(tp("ChatGPT") - 0.1, 0.45, (g, p) => { trazo(g, [[170, 540], [170, 1050]], NAVY, 3.2, clamp01(p * 2), 121, 0.1, false); trazo(g, [[170, 1050], [960, 1050]], NAVY, 3.2, clamp01(p * 2 - 1), 122, 0.1, false); }),
    tipoE(tp("ChatGPT") + 0.14, "CHATGPT", 640, 1102, 32, 0, 123),
    el(tp("creciendo") - 0.06, 0.65, (c, e, p) => barra(c, e, 570, 710, 1048, 560, p, REDPEN, 124)),
    pen(tp("creciendo") + 0.16, 0.36, (g, p) => flecha(g, [[785, 1000], [792, 800], [786, 600]], REDPEN, 5, p, 125)),
    titulo(tp("seis"), "×6", 540, 290, 150, 11),
    tiraE(tp("velocidad") - 0.08, "VELOCIDAD DE ADOPCIÓN", 560, 456, 30, -0.015, 45, 34),
    el(tp("iPhone", ESC.F) - 0.06, 0.4, (c, e, p) => barra(c, e, 290, 430, 1048, 966, p, NAVY, 126)),
    tipoE(tp("iPhone", ESC.F) + 0.1, "IPHONE", 360, 1102, 32, 0, 127),
  ],
  G: () => [
    ...grab(tp("llevamos"), "calendario", tarjeta(310, 720, 400, 420, -0.05, 17)),
    pen(tp("tres") - 0.06, 0.42, (g, p) => [0, 1, 2].forEach((k) => trazo(g, [[700 + k * 64, 590], [712 + k * 64, 860]], REDPEN, 9, clamp01(p * 3 - k), 131 + k, 0.4, false))),
    titulo(tp("años", tp("tres")) - 0.04, "3 AÑOS", 540, 290, 120, 13),
    tiraE(tp("IA", ESC.G) - 0.04, "DE IA GENERATIVA", 560, 1040, 44, 0.02, 46, 34),
  ],
  H: () => {
    const cM = tarjeta(540, 650, 360, 360, 0.04, 18), dos = tituloT(tp("dos") - 0.02, "2 AÑOS", 640, 1062, 96, 15);
    return [
      tiraE(tp("¿Cuántos") - 0.02, "¿CUÁNTOS AÑOS?", 540, 285, 54, -0.02, 47, 30),
      preg(tp("crees"), 905, 425, 70), preg(tp("crees") + 0.18, 978, 372, 90),
      ...grab(tp("mundo", ESC.H), "mundo", cM),
      tiraE(tp("IA", ESC.H) - 0.04, "IA", 700, 500, 44, 0.12, 48),
      pen(tp("todo", tp("IA", ESC.H)) - 0.04, 0.5, (g, p) => lazo(g, 540, 650, 242, 234, REDPEN, 4.5, p, 141)),
      tiraE(tp("creo") - 0.04, "YO CREO", 230, 932, 34, -0.04, 49),
      dos.e,
      pen(tp("sea") - 0.1, 0.42, (g, p) => lazo(g, dos.tiles[0].x, 1062, 78, 92, REDPEN, 5, p, 142)),
    ];
  },
  I: () => [
    camE(ESC.I + 0.12, 540, 520, 1.15, "abuelo", 151),
    tiraE(tp("eso", ESC.I) - 0.04, "«ESO LO USARÁN", 540, 795, 42, -0.03, 50, 32),
    tiraE(tp("mis", ESC.I) - 0.04, "MIS NIETOS»", 560, 905, 42, 0.02, 51, 32),
    pen(tp("nietos") - 0.1, 0.3, (g, p) => tacha(g, 550, 850, 170, p, 152)),
  ],
  J1: () => [
    pen(tp("miremos") - 0.04, 1.2, (g, p) => medidor(g, 540, 830, 275, 0.93, p, 161)),
    tipoE(tp("nivel") + 0.3, "NIVEL", 540, 880, 34, 0, 162),
    titulo(tp("adopción") - 0.04, "ADOPCIÓN", 540, 290, 96, 17),
    camE(tp("tienen") - 0.04, 190, 1000, 0.86, "nino", 163),
  ],
  J2: () => {
    const g2 = tp("Google", ESC.J2), c2 = tp("ChatGPT", g2);
    return [
      camE(tp("niño", ESC.J2) - 0.04, 190, 640, 0.95, "nino", 171),
      titulo(tp("8"), "8 AÑOS", 600, 285, 110, 19),
      tiraE(tp("pregúntale") - 0.04, "PREGÚNTALE A GOOGLE", 660, 640, 34, -0.02, 52, 40),
      pen(g2 + 0.04, 0.3, (g, p) => tachar(g, 772, 952, 642, p, 172, REDPEN, 6)),
      tiraE(tp("pregúntale", g2) - 0.04, "PREGÚNTALE A CHATGPT", 660, 860, 34, 0.015, 53, 40),
      pen(c2 + 0.02, 0.3, (g, p) => chulo(g, 268, 860, 42, p, 173)),
      pen(c2 + 0.28, 0.35, (g, p) => subraya(g, 760, 965, 892, REDPEN, 4.5, p, 174)),
    ];
  },
  K: () => [
    titulo(tp("creció") - 0.04, "CRECIÓ", 600, 285, 100, 31),
    el(tp("creció") + 0.12, 0.6, (c, e, p) => regla(c, e, 110, 450, 1100, p)),
    camE(tp("creció") + 0.22, 330, 800, 0.95, "nino", 181),
    pen(tp("con", tp("creció")) - 0.04, 0.4, (g, p) => flecha(g, [[205, 1075], [210, 880], [205, 690]], REDPEN, 5, p, 182)),
    preg(tp("dudas"), 520, 600, 70), preg(tp("dudas") + 0.18, 600, 520, 92),
    preg(tp("preguntas", tp("dudas")), 545, 760, 62, NAVY), preg(tp("preguntas", tp("dudas")) + 0.18, 632, 700, 80, NAVY),
    tiraE(tp("ChatGPT", ESC.K) - 0.04, "CHATGPT", 800, 880, 44, 0.03, 58),
    pen(tp("ChatGPT", ESC.K) + 0.3, 0.3, (g, p) => chulo(g, 588, 880, 38, p, 183)),
    tiraE(tp("no", tp("ChatGPT", ESC.K)) - 0.04, "GOOGLE", 800, 1020, 44, -0.03, 59),
    pen(tp("Google", ESC.K) + 0.02, 0.3, (g, p) => tachar(g, 690, 912, 1022, p, 184, REDPEN, 7)),
  ],
  L: () => [
    titulo(tp("natural") - 0.04, "NATURAL", 540, 290, 104, 21),
    camE(tp("generación") - 0.06, 290, 640, 0.66, "nino", 191),
    camE(tp("generación") + 0.08, 540, 640, 0.66, "mujer", 192),
    camE(tp("generación") + 0.22, 790, 640, 0.66, "joven", 193),
    preg(tp("entender"), 290, 478, 60), preg(tp("entender") + 0.12, 540, 478, 60), preg(tp("entender") + 0.24, 790, 478, 60),
    ...grab(tp("teclados"), "teclado", tarjeta(540, 960, 480, 230, -0.03, 22)),
  ],
  M: () => [
    camE(tp("muchacho") - 0.06, 230, 660, 0.95, "joven", 201),
    titulo(tp("14"), "14 AÑOS", 600, 285, 110, 23),
    preg(tp("entiende"), 400, 530, 72),
    ...grab(tp("casetes", ESC.M), "casete", tarjeta(700, 670, 380, 280, 0.05, 24)),
    pen(tp("en", tp("casetes", ESC.M)) - 0.02, 0.32, (g, p) => flecha(g, [[650, 830], [612, 875], [566, 902]], REDPEN, 4.5, p, 202)),
    ...grab(tp("Walkman"), "walkman", tarjeta(430, 1000, 290, 300, -0.06, 25)),
  ],
  N: () => [
    camE(tp("niños", ESC.N) - 0.06, 200, 560, 0.85, "nino", 211),
    titulo(tp("normal") - 0.04, "NORMAL", 560, 285, 100, 25),
    pen(tp("normal") + 0.25, 0.3, (g, p) => chulo(g, 336, 470, 44, p, 212)),
    tiraE(tp("tus") - 0.04, "TUS CLIENTES", 640, 700, 46, -0.02, 60),
    camE(tp("clientes"), 420, 930, 0.72, "adulto", 213),
    camE(tp("también", ESC.N), 640, 930, 0.72, "mujer", 214),
    camE(tp("va", tp("también", ESC.N)), 860, 930, 0.72, "abuelo", 215),
  ],
  O: () => [
    ...grab(tp("negocio", ESC.O), "tienda", tarjeta(520, 700, 470, 430, -0.03, 26)),
    selloE(tp("IA", ESC.O), 520, 470, -0.12, "SIN IA", RED, 62),
    pen(tp("sonar") - 0.06, 0.6, (g, p) => [[815, 720], [878, 655], [945, 600]].forEach(([x, y], k) => notaMusical(g, x, y, 1.25, clamp01(p * 2.2 - k * 0.5), 221 + k))),
    titulo(tp("casete", ESC.O) - 0.04, "CASETE", 540, 270, 110, 33),
    ...grab(tp("casete", ESC.O) + 0.22, "casete", tarjeta(730, 1015, 320, 230, 0.06, 27)),
  ],
  P: () => {
    const cards = [215, 540, 865].map((x, k) => tarjeta(x, 880, 260, 330, [-0.05, 0.02, 0.06][k], 28 + k)), when = [tp("agentes"), tp("IA", ESC.P), tp("reemplazan")], hoy = tp("hoy", ESC.P);
    return [
      ...cards.flatMap((cd, k) => grab(when[k], "robot", cd, 0.95, 0.62)),
      ...cards.map((cd, k) => tipoE(when[k] + 0.32, `AGENTE 0${k + 1}`, cd.cx, 1082, 26, 0, 231 + k)),
      tiraE(tp("lento") - 0.08, "LENTO", 300, 560, 46, -0.04, 54),
      pen(tp("lento") + 0.2, 0.25, (g, p) => tachar(g, 228, 376, 562, p, 232, REDPEN, 7)),
      tiraE(tp("caro") - 0.08, "CARO", 780, 560, 46, 0.04, 55),
      pen(tp("caro") + 0.2, 0.25, (g, p) => tachar(g, 716, 848, 562, p, 233, REDPEN, 7)),
      titulo(hoy - 0.04, "HOY", 540, 290, 150, 27),
      selloE(tp("no", hoy), 540, 690, -0.08, "NO ES MODA", RED, 46),
    ];
  },
  Q: () => {
    const cW = tarjeta(800, 740, 420, 420, 0.04, 31), cL = tarjeta(280, 740, 420, 420, -0.05, 32);
    return [
      pen(tp("separará") - 0.06, 0.55, (g, p) => punteado(g, [[540, 400], [541, 760], [540, 1130]], REDPEN, 5, p, 241, 18, 12)),
      tiraE(tp("empresas") - 0.06, "EMPRESAS", 540, 285, 54, -0.02, 56, 30),
      ...grab(tp("triunfen"), "tienda", cW, 0.9, 0.7),
      selloE(tp("triunfen") + 0.42, 800, 600, -0.12, "TRIUNFA", VERDE, 46),
      pegada(tp("las", tp("triunfen")), "tienda", cL, 0.9),
      selloE(tp("quiebren") - 0.02, 280, 640, 0.14, "QUIEBRA", RED, 46),
    ];
  },
  R: () => [
    tiraE(ESC.R + 0.04, "COMENTA", 540, 176, 36, -0.02, 57, 30),
    titulo(tp("ERA") - 0.04, "ERA", 540, 368, 170, 29),
    ...grab(tp("envío"), "sobre", tarjeta(300, 760, 360, 270, 0.08, 33)),
    ...grab(tp("clase"), "laptop", tarjeta(750, 790, 420, 320, -0.04, 34)),
    tipoE(tp("clase") + 0.5, "CLASE", 750, 988, 34, -0.04, 251),
    pen(tp("instalarlas") - 0.04, 0.8, (g, p) => mano(g, "¡EN TU NEGOCIO!", 540, 1090, 50, p, 252, REDPEN, 4)),
    pen(tp("negocio", tp("instalarlas")), 0.4, (g, p) => subraya(g, 272, 808, 1134, REDPEN, 4.5, p, 253, true)),
  ],
};

const ORDEN = Object.keys(ESC).sort((a, b) => ESC[a] - ESC[b]);
export const motionDesign: Film = {
  // sin partitura: las escenas cambian con la voz, no con un compás. bpm 1800 = rejilla de 1 cuadro
  meta: { title: "motionDesign", W: 1080, H: 1920, fps: FPS, bpm: 1800, durationFrames: DURATION },
  assets: { images: {} },
  shots: montaje("eraM", ESC, ORDEN, TOMAS, DUR),
};
void RED; void VERDE; void NAVY; void (null as unknown as Gfx); void el;
