// escenas_caritas.js — las escenas del reel en estilo CARITAS (copia de estilos/caritas/plantilla_escenas.js).
// El ejemplo es el reel ERA (77 s): Clawd actúa cada frase. Cada toma es una función (t = segundo del video, lt = segundo
// dentro de la toma, dur = largo de la toma) y todas se registran al final con shots([[ESC.A, A], …]).
// ESC (inicio de cada toma) y WORDS vienen de tiempos.js (los escribe build_caritas.py); tp('palabra', desde) = segundo
// en que se dice. Clawd y sus emociones (clawd, emotions) son del motor; los objetos pintados están en props.js / props2.js.
(() => {
  const G = SUELO;
  const cam = (lt, zx = 0, zz = 0) => camBegin(540 + 12 * Math.sin(lt * .5) + zx, 960, 1 + .012 * lt + zz);

  // carro antiguo abierto: Clawd va sentado adentro (se pinta antes que la carrocería)
  function carroAbierto(x, y, s, t) {
    const bob = Math.abs(Math.sin(t * 9)) * 3 * s;
    boilSeed('carroA');
    paint(rrPts(x - 160 * s, y - 130 * s - bob, 320 * s, 78 * s, 24 * s), { wash: '#2F4A6E', fill: '#3E5F8A', fillOp: 90, bleed: .05, tex: .5, ink: PAL.ink, sw: 1.1 });
    paint([[x + 70 * s, y - 130 * s - bob], [x + 96 * s, y - 210 * s - bob], [x + 108 * s, y - 210 * s - bob], [x + 90 * s, y - 130 * s - bob]], { wash: COL.screenLt, washOp: 160, ink: PAL.ink, sw: .7 });
    paint(ellPts(x + 150 * s, y - 104 * s - bob, 11 * s, 11 * s, 12), { wash: PAL.ochre, ink: PAL.ink, sw: .6 });
    for (const wx of [-96, 100]) {
      boilSeed('carroR' + wx);
      const cx = x + wx * s, cy = y - 36 * s, r = 36 * s;
      paint(ellPts(cx, cy, r, r, 22), { wash: '#2B2233', ink: PAL.ink, sw: 1 });
      paint(ellPts(cx, cy, r * .55, r * .55, 16), { wash: COL.grayLt, ink: PAL.ink, sw: .6 });
      for (let k = 0; k < 3; k++) { const a = t * 10 + k * TAU / 3; inkLine([[cx, cy], [cx + Math.cos(a) * r * .5, cy + Math.sin(a) * r * .5]], .6, PAL.ink, 'inkfine', 0); }
    }
  }
  function polvo(x, y, k, key = 'polvo') {             // nube de polvo que tapa un cambio (k 0..1)
    if (k <= 0 || k >= 1) return; boilSeed(key);
    const r = 60 + 180 * easeOut(k), a = 255 * (1 - k * k);
    for (let i = 0; i < 6; i++) { const ang = i / 6 * TAU + k; paint(ellPts(x + Math.cos(ang) * r * .7, y + Math.sin(ang) * r * .35, r * .55, r * .4, 14, 2), { wash: COL.cream, washOp: a, ink: null }); }
  }
  function postes(t, v, key = 'postes') {              // postes que pasan: sensación de viaje
    for (let i = 0; i < 6; i++) {
      boilSeed(key + i);
      const x = ((i * 240 - t * v) % 1440 + 1440) % 1440 - 180;
      paint(rectPts(x - 9, G - 120, 18, 124, 1), { wash: COL.wood, ink: PAL.ink, sw: .6 });
      inkLine([[x - 120, G - 92], [x + 120, G - 96]], .5, COL.woodDk, 'inkfine', .2);
    }
  }

  // ---------------------------------------------------------------- A · 13 años: del caballo al carro
  function A(t, lt, dur) {
    const tCar = tp('carro');
    cam(lt);
    escenario('sepia', 'A');
    postes(t, t < tCar ? 260 : 520);
    if (t < tCar) {
      const s = 1.65, x = 450, bob = Math.sin(t * 2.6 * TAU * 2) * 5 * s;
      caballo(x, G, s, t);
      const lomo = G - 112 * s + bob - 44 * s;
      clawd(x - 8, lomo + 2 * 28 + 14, 28, { ...emotions(t, [[0, 'happy'], [tp('caballo'), 'excited']]), noLegs: true, noShadow: true, boilKey: 'jinete' });
    } else {
      const s = 1.5, x = 520, bob = Math.abs(Math.sin(t * 9)) * 3 * s;
      clawd(x - 70, G - 120 * s - bob + 2 * 30 + 8, 30, { ...emotions(t, [[0, 'excited'], [tp('1913'), 'proud']]), noLegs: true, noShadow: true, boilKey: 'chofer' });
      carroAbierto(x, G, s, t);
    }
    polvo(500, G - 160, seg(t, tCar - .22, tCar + .45), 'polvoA');
    numero('13 AÑOS', 540, 330, 190, PAL.clayDk, -1, t);
    camEnd();
    transicion(lt, dur, null, 'wipe', 'sepia', 'sepia');
  }

  // ---------------------------------------------------------------- B · todo se movía mucho más despacio
  function B(t, lt, dur) {
    cam(lt);
    escenario('sepia', 'B');
    reloj(800, 430, 175, t, .25, 'relojB');
    caracol(lerp(140, 300, seg(t, ESC.B, ESC.C)), G, 1.5, t, 'caracolB');
    clawd(680, G, 36, { ...emotions(t, [[0, 'bored'], [tp('movían'), 'sleepy']]), boilKey: 'clawdB' });
    camEnd();
    transicion(lt, dur, 'wipe', 'wipe', 'sepia', 'cielo');
  }

  // ---------------------------------------------------------------- C · saltemos para adelante: el 2º gran salto
  function C(t, lt, dur) {
    const t0 = tp('Saltemos'), t1 = t0 + .9, k = seg(t, t0, t1);
    camBegin(lerp(470, 610, ease(k)) + 10 * Math.sin(lt), 960, 1.02);
    escenario('cielo', 'C');
    const x = lerp(230, 800, ease(k)), hop = jump(t, t0, t1, 8);
    const mood = emotions(t, [[0, 'determined'], [t0 - .05, 'excited'], [tp('segundo'), 'starstruck']]);
    clawd(x, G, 34, { ...mood, view: k > 0 && k < 1 ? 'side' : (mood.view || 'front'), dy: (mood.dy || 0) + hop.dy, sq: (mood.sq || 0) + hop.sq, boilKey: 'clawdC' });
    for (let i = 0; i < 6; i++) chispa(820 + Math.cos(i) * 140, G - 120 + Math.sin(i * 2) * 80, 24, seg(t, t1 + i * .05, t1 + .6 + i * .05), 'chC' + i, PAL.ochre);
    const tTec = tp('tecnológico');                      // rayo: el salto tecnológico
    if (t > tTec - .1) {
      boilSeed('rayoC');
      const kk = backOut(seg(t, tTec - .1, tTec + .25)), cx = 300, cy = 420;
      glow(cx, cy, 160 * kk, '#FFD96A', .6);
      paint([[cx + 20 * kk, cy - 110 * kk], [cx - 50 * kk, cy + 10 * kk], [cx - 4 * kk, cy + 10 * kk], [cx - 30 * kk, cy + 110 * kk], [cx + 56 * kk, cy - 20 * kk], [cx + 8 * kk, cy - 20 * kk]], { wash: PAL.ochre, ink: PAL.ink, sw: 1 });
    }
    camEnd();
    transicion(lt, dur, 'wipe', 'wipe', 'cielo', 'cielo');
  }

  // ---------------------------------------------------------------- D · el smartphone: 2007, el primer iPhone
  function D(t, lt, dur) {
    const tCae = tp('smartphone') - .3, tLlega = tCae + .75;
    cam(lt);
    escenario('cielo', 'D');
    const x = 450, u = 38;
    const mood = emotions(t, [[0, 'neutral', { lookY: -.8 }], [tCae + .2, 'surprised', { lookY: -.9, lookX: .4 }], [tLlega + .1, 'happy'], [tp('aparece'), 'starstruck']]);
    if (t < tLlega) {
      const k = easeIn(seg(t, tCae, tLlega)), px = lerp(760, x + 6.2 * u, k), py = lerp(120, G - 7.6 * u, k);
      glow(px, py, 130, '#BFE3FF', .8);
      celular(px, py, 90, 150, k * 3, 1, 'celD');
      clawd(x, G, u, { ...mood, aR: lerp(.2, 1.1, seg(t, tCae + .3, tLlega)), boilKey: 'clawdD' });
    } else {
      glow(x + 6.2 * u, G - 7.6 * u, 150 + 20 * Math.sin(t * 5), '#BFE3FF', .7);
      clawd(x, G, u, { ...mood, aR: 1.1, armR: enMano(1), boilKey: 'clawdD' });
    }
    for (let i = 0; i < 5; i++) chispa(x + 6.2 * u + Math.cos(i * 1.3) * 120, G - 7.6 * u + Math.sin(i * 1.3) * 110, 20, seg(t, tLlega + i * .06, tLlega + .5 + i * .06), 'chD' + i, PAL.cream);
    numero('2007', 540, 330, 200, PAL.indigo, tp('2007'), t);
    camEnd();
    transicion(lt, dur, 'wipe', null, 'cielo');
  }

  // ---------------------------------------------------------------- E · todo el mundo con smartphone: 7 años
  function E(t, lt, dur) {
    const t0 = tp('todo el mundo');
    const z = kf(t, [[ESC.E, 1.55], [t0 - .4, 1.55], [t0 + .5, 1]]);
    camBegin(540, kf(t, [[ESC.E, 900], [t0 + .5, 960]]), z);
    escenario('cielo', 'E');
    const gente = [[540, G, 32, null, null], [175, G - 10, 19, 'rosy', 'beanie'], [905, G - 10, 19, 'gold', 'sweatband'], [345, G - 175, 15, 'green', 'bow'],
                   [735, G - 175, 15, 'blue', 'headphones'], [95, G - 195, 14, 'pale', 'top'], [985, G - 195, 14, '#C98A5B', 'flower']];
    gente.forEach(([x, y, u, tint, hat], i) => {
      const tc = t0 + i * .2, con = t > tc;
      const mood = emotions(t, [[0, i ? 'neutral' : 'happy'], [tc, 'happy']], { take: .6 });
      clawd(x, y, u, { ...mood, tint: tint || mood.tint, hat: hat || undefined, aR: con ? 1 : -.2, armR: con ? enMano(1) : undefined, seed: i * 3, boilKey: 'gente' + i });
    });
    numero('7 AÑOS', 540, 330, 190, PAL.indigo, tp('siete'), t);
    camEnd();
    transicion(lt, dur, 'flash', 'wipe', null, 'barro');
  }

  // ---------------------------------------------------------------- F · ChatGPT crece 6 veces más rápido que el iPhone
  function F(t, lt, dur) {
    const tC = tp('ChatGPT'), tV = tp('se', tp('velocidad'));
    cam(lt);
    escenario('calido', 'F');
    tallo(800, G, 920 * easeOut(seg(t, tC, tC + 1.4)), PAL.clay, PAL.clayDk, t, 'talloIA');
    tallo(250, G, 300 * ease(seg(t, tV, tV + 1.6)), COL.gray, '#77757F', t, 'talloCel');
    if (t > tV) { celular(250, G - 300 * ease(seg(t, tV, tV + 1.6)) - 70, 56, 96, .2, .6, 'celF'); }
    if (t > tC + .2) iaChat(800, G - 920 * easeOut(seg(t, tC, tC + 1.4)) - 80, 58, t, 'iaF');
    const mood = emotions(t, [[0, 'neutral'], [tC + .15, 'surprised', { lookY: -.9, lookX: .6 }], [tp('seis') + .3, 'starstruck', { lookY: -.7, lookX: .5 }]]);
    clawd(520, G, 30, { ...mood, boilKey: 'clawdF' });
    numero('×6', 330, 380, 240, PAL.clayDk, tp('seis'), t);
    camEnd();
    transicion(lt, dur, 'wipe', 'wipe', 'barro', 'oro');
  }

  // ---------------------------------------------------------------- G · apenas 3 años de IA generativa
  function G_(t, lt, dur) {
    const t3 = tp('tres');
    cam(lt);
    escenario('oro', 'G');
    torta(720, G, 1.5, 3, (t - t3) / .16, t, 'tortaG');
    clawd(300, G, 34, { ...emotions(t, [[0, 'happy', { lookX: .7 }], [t3 + .3, 'excited', { lookX: .6 }]]), hat: 'party', boilKey: 'clawdG' });
    camEnd();
    transicion(lt, dur, 'wipe', 'wipe', 'oro', 'cielo');
  }

  // ---------------------------------------------------------------- H · ¿cuántos años nos quedan? Yo creo que dos
  function H(t, lt, dur) {
    const tM = tp('mundo', tp('quedan'));
    cam(lt);
    escenario('cielo', 'H');
    if (t > tM - .3) mundo(800, 460 - 40 * (1 - backOut(seg(t, tM - .3, tM + .3))), 150 * backOut(seg(t, tM - .3, tM + .3)), t, 'mundoH');
    const mood = emotions(t, [[0, 'neutral'], [tp('¿Cuántos'), 'thinking'], [tp('quedan'), 'confused'], [tp('creo'), 'idea'], [tp('dos'), 'determined']]);
    clawd(400, G, 38, { ...mood, boilKey: 'clawdH' });
    numero('2', 800, 760, 320, PAL.clayDk, tp('dos') - .05, t);
    camEnd();
    transicion(lt, dur, 'wipe', 'wipe', 'cielo', 'sepia');
  }

  // ---------------------------------------------------------------- I · "eso lo usarán mis nietos" — no
  function I(t, lt, dur) {
    const tN = tp('nietos');
    cam(lt);
    escenario('sepia', 'I');
    const ax = 270;
    baston(ax + 7 * 30, G, 190, 'bastonI');
    clawd(ax, G, 30, { ...emotions(t, [[0, 'smug']]), tint: 'pale', hat: 'top', aR: -.3, boilKey: 'abuelo' });
    if (t > tp('eso lo usarán') - .3) {
      const k = backOut(seg(t, tp('eso lo usarán') - .3, tp('eso lo usarán') + .1));
      nube(660, 430, 2.0 * k, 'nubeI');
      boilSeed('burbI'); paint(ellPts(420, 700, 16 * k, 13 * k, 10), { wash: COL.cream, ink: PAL.ink, sw: .6 }); paint(ellPts(470, 620, 26 * k, 20 * k, 12), { wash: COL.cream, ink: PAL.ink, sw: .7 });
      for (let i = 0; i < 3; i++) clawd(545 + i * 115, 495, 10 * k, { ...feel('happy', t), seed: i, noShadow: true, boilKey: 'nieto' + i });
    }
    equis(660, 430, 190, seg(t, tN, tN + .3), 'xI');
    clawd(870, G, 28, { ...emotions(t, [[0, 'neutral'], [tN + .1, 'determined']]), boilKey: 'clawdI' });
    camEnd();
    transicion(lt, dur, 'wipe', 'wipe', 'sepia', 'verde');
  }

  // ---------------------------------------------------------------- J1 · el nivel de adopción de los niños
  function J1(t, lt, dur) {
    const tA = tp('adopción');
    cam(lt);
    escenario('verde', 'J1');
    medidor(540, 640, 285, kf(t, [[ESC.J1, .08], [tA, .08], [tA + .9, .95]], backOut), 'medJ');
    clawd(820, G, 21, { ...emotions(t, [[0, 'happy'], [tp('niños'), 'excited']]), hat: 'beanie', tint: 'rosy', boilKey: 'nino' });
    camEnd();
    transicion(lt, dur, 'wipe', null, 'verde');
  }

  // ---------------------------------------------------------------- J2 · un niño de 8 años: pregúntale a ChatGPT (no a Google)
  function J2(t, lt, dur) {
    const tP1 = tp('pregúntale'), tG = tp('Google'), tP2 = tp('pregúntale', tG), tC = tp('ChatGPT', tP2);
    cam(lt);
    escenario('verde', 'J2');
    const mood = emotions(t, [[0, 'happy'], [tG + .1, 'disgusted'], [tC + .1, 'excited']]);
    clawd(230, G, 23, { ...mood, hat: 'beanie', tint: 'rosy', boilKey: 'nino' });
    numero('8', 230, G - 300, 140, PAL.clayDk, tp('8'), t);
    if (t > tP1 - .15) { const k = backOut(seg(t, tP1 - .15, tP1 + .15)); globo(690, 430, 430 * k, 230 * k, -1, 'gloJ1'); if (k > .5) lupa(665, 415, 56, 'lupaJ'); }
    equis(690, 430, 125, seg(t, tG + .2, tG + .5), 'xJ');
    if (t > tP2 - .15) { const k = backOut(seg(t, tP2 - .15, tP2 + .15)); globo(690, 780, 430 * k, 230 * k, -1, 'gloJ2'); if (k > .5) iaChat(690, 780, 62, t, 'iaJ'); }
    chulo(920, 700, 56, seg(t, tC + .1, tC + .4), 'okJ');
    camEnd();
    transicion(lt, dur, null, 'wipe', null, 'verde');
  }

  // ---------------------------------------------------------------- K · creció con las respuestas en ChatGPT, no en Google
  function K(t, lt, dur) {
    const tCr = tp('creció'), tD = tp('dudas'), tC = tp('ChatGPT', tp('preguntas')), tG = tp('Google', tp('preguntas'));
    cam(lt);
    escenario('verde', 'K');
    const u = lerp(21, 33, backOut(seg(t, tCr, tCr + .8)));
    clawd(330, G, u, { ...emotions(t, [[0, 'happy'], [tCr, 'proud'], [tD, 'thinking'], [tC + .2, 'happy']]), hat: 'beanie', tint: 'rosy', boilKey: 'nino' });
    iaChat(800, 540, 86 + 9 * pulse(t), t, 'iaK');
    for (let i = 0; i < 5; i++) {                      // las dudas vuelan a la IA
      const t0 = tD + i * .18, k = seg(t, t0 + .8, t0 + 1.6);
      if (t < t0) continue;
      const p = arcPt([330 + (i - 2) * 70, G - 460], [800, 540], 170, ease(k));
      if (k < .98) emote('?', p[0], p[1], 42 * (1 - k * .6), seg(t, t0, t0 + .2), t - t0);
    }
    if (t > tG - .3) { const k = backOut(seg(t, tG - .3, tG)); lupa(790, 880, 52 * k, 'lupaK', COL.gray); equis(830, 920, 90, seg(t, tG + .1, tG + .4), 'xK'); }
    camEnd();
    transicion(lt, dur, 'wipe', 'wipe', 'verde', 'cielo');
  }

  // ---------------------------------------------------------------- L · para él es natural; no va a entender los teclados
  function L(t, lt, dur) {
    const tT = tp('teclados');
    cam(lt);
    escenario('cielo', 'L');
    const mood = emotions(t, [[0, 'happy'], [tp('natural'), 'cool'], [tT + .1, 'confused']]);
    clawd(300, G, 33, { ...mood, hat: 'beanie', tint: 'rosy', lookX: t > tT ? .8 : 0, boilKey: 'nino' });
    if (t > tT - .35) { const k = seg(t, tT - .35, tT + .05); teclado(770, lerp(300, G - 95, easeIn(k)) + (k >= 1 ? 6 * spring(t, tT + .05) : 0), 1.12, 'tecL'); }
    camEnd();
    transicion(lt, dur, 'wipe', 'wipe', 'cielo', 'rosa');
  }

  // ---------------------------------------------------------------- M · un muchacho de 14 no entiende los casetes y el Walkman
  function M(t, lt, dur) {
    const tC = tp('cassettes'), tW = tp('Walkman');
    cam(lt);
    escenario('rosa', 'M');
    const mood = emotions(t, [[0, 'cool'], [tp('entiende'), 'confused'], [tC + .2, 'suspicious', { lookX: .8 }], [tW + .2, 'confused', { lookX: .6 }]]);
    clawd(280, G, 33, { ...mood, hat: 'headphones', tint: 'gold', boilKey: 'teen' });
    numero('14', 280, G - 420, 150, PAL.violet, tp('14'), t);
    if (t > tC - .3) casete(770, 470 + 20 * Math.sin(t * 2), lerp(.2, 1.15, backOut(seg(t, tC - .3, tC + .1))), t, .1 * Math.sin(t * 3), 'casM');
    if (t > tW - .3) walkman(790, 890, lerp(.2, .95, backOut(seg(t, tW - .3, tW + .1))), t, 'walkM');
    camEnd();
    transicion(lt, dur, 'wipe', 'wipe', 'rosa', 'verde');
  }

  // ---------------------------------------------------------------- N · si para los niños es normal, para tus clientes también
  function N(t, lt, dur) {
    const tCl = tp('clientes');
    cam(lt);
    escenario('verde', 'N');
    clawd(150, G, 20, { ...emotions(t, [[0, 'happy']]), hat: 'beanie', tint: 'rosy', aR: 1, armR: enMano(1), boilKey: 'nino' });
    const cl = [[430, 25, 'blue', 'fedora'], [680, 28, null, 'top'], [935, 24, 'green', 'bow']];
    cl.forEach(([x, u, tint, hat], i) => {
      const w = stroll(t, tCl + i * .18, tCl + i * .18 + 1.0, x + 800, x, u);
      clawd(w.x, G, u, { ...emotions(t, [[0, 'neutral'], [tCl + i * .18 + .9, 'happy']], { take: .5 }), ...(t < tCl + i * .18 + .9 ? { view: 'side', flip: true, walk: w.walk, dy: w.dy } : {}),
        tint: tint || undefined, hat, aR: t > tCl + 1.3 + i * .1 ? 1 : -.2, armR: t > tCl + 1.3 + i * .1 ? enMano(1) : undefined, seed: i * 5, boilKey: 'cli' + i });
    });
    camEnd();
    transicion(lt, dur, 'wipe', 'wipe', 'verde', 'barro');
  }

  // ---------------------------------------------------------------- O · el negocio sin IA va a sonar a casete
  function O(t, lt, dur) {
    const tCa = tp('cassette', tp('sonar'));
    cam(lt);
    escenario('gris', 'O');
    tienda(560, G, 1.55, { polvo: true }, 'tiendaO');
    clawd(190, G, 27, { ...emotions(t, [[0, 'bored'], [tp('IA', tp('negocio')), 'sad']]), tint: 'blue', boilKey: 'tendero' });
    if (t > tCa - .3) {
      const k = backOut(seg(t, tCa - .3, tCa + .1));
      casete(850, 850, .65 * k, t * .3, -.2, 'casO');
      boilSeed('cintaO');
      paint(ribbon([[905, 875], [965, 950 + 10 * Math.sin(t * 4)], [915, 1010], [995, 1065]], 9, 9), { wash: '#5A4A3A', ink: null });
    }
    camEnd();
    transicion(lt, dur, 'wipe', 'wipe', 'barro', 'barro');
  }

  // ---------------------------------------------------------------- P · agentes IA que reemplazan el trabajo lento y caro: hoy mismo
  function P(t, lt, dur) {
    const tA = tp('agentes'), tT = tp('trabajo'), tH = tp('hoy mismo');
    cam(lt);
    escenario('calido', 'P');
    const ordenar = seg(t, tT + .4, tT + 1.6);
    papeles(880, G, 1.3, Math.round(lerp(9, 3, ordenar)), t * (1 - ordenar), 'papP');
    reloj(850, 450, 130, t, t < tT ? .3 : 6, 'relojP');
    [[160, 27], [405, 29], [650, 27]].forEach(([x, u], i) => {
      const t0 = tA + i * .15, w = stroll(t, t0, t0 + .7, x - 700, x, u);
      clawd(w.x, G, u, { ...emotions(t, [[0, 'determined'], [tH, 'proud']], { take: .6 }), ...(t < t0 + .7 ? { view: 'side', walk: w.walk, dy: w.dy } : {}),
        hat: 'hard', aR: t > tT + .3 ? .9 + .3 * Math.sin(t * 8 + i) : -.2, seed: i * 7, boilKey: 'agente' + i });
    });
    numero('HOY', 540, 330, 200, PAL.clayDk, tH, t);
    camEnd();
    transicion(lt, dur, 'wipe', 'wipe', 'barro', 'oro');
  }

  // ---------------------------------------------------------------- Q · triunfan las que la usan, quiebran las que no
  function Q(t, lt, dur) {
    const tT = tp('triunfen'), tQ = tp('quiebren');
    cam(lt);
    escenario('oro', 'Q');
    tienda(270, G - 40, .9, { brillo: seg(t, tT - .2, tT + .3) }, 'tiendaQ1');
    tienda(810, G - 40, .9, { polvo: true, grieta: seg(t, tQ, tQ + .3) }, 'tiendaQ2');
    clawd(270, G, 22, { ...emotions(t, [[0, 'hopeful'], [tT, 'proud']]), hat: t > tT ? 'crown' : undefined, boilKey: 'ganador' });
    clawd(810, G, 22, { ...emotions(t, [[0, 'nervous'], [tQ, 'cry']]), tint: t > tQ ? 'blue' : undefined, boilKey: 'perdedor' });
    camEnd();
    transicion(lt, dur, 'wipe', 'wipe', 'oro', 'barro');
  }

  // ---------------------------------------------------------------- R · CTA: comenta ERA y te envío la clase
  function R(t, lt, dur) {
    const tE = tp('ERA'), tEn = tp('envío'), tCl = tp('clase');
    camBegin(540, 960, 1 + .02 * lt);
    escenario('calido', 'R');
    pastilla(540, 420, 820, 160, 'pillR');
    boilSeed('avatarR'); paint(ellPts(210, 420, 50, 50, 16), { wash: PAL.clayLt, ink: PAL.ink, sw: .7 });
    numero('ERA', 300, 424, 130, PAL.clayDk, tE, t, { align: 'left' });
    if (t > tEn) { const k = seg(t, tEn, tEn + .7), p = arcPt([540, G - 300], [760, 470], 160, ease(k)); if (k < 1) sobre(p[0], p[1], .55, k, 'sobreR'); }
    if (t > tCl - .2) pantallaPlay(790, 760, lerp(.2, 1.15, backOut(seg(t, tCl - .2, tCl + .2))), 'playR');
    clawd(310, G, 36, { ...emotions(t, [[0, 'excited'], [tE, 'happy'], [tCl, 'excited'], [tp('negocio', tCl), 'love']]), aL: kf(t, [[ESC.R, -.2], [tE - .2, 1.3], [tE + 1, .4]]), boilKey: 'clawdR' });
    camEnd();
    transicion(lt, dur, 'wipe', null, 'barro');
  }

  shots([[ESC.A, A], [ESC.B, B], [ESC.C, C], [ESC.D, D], [ESC.E, E], [ESC.F, F], [ESC.G, G_], [ESC.H, H], [ESC.I, I],
         [ESC.J1, J1], [ESC.J2, J2], [ESC.K, K], [ESC.L, L], [ESC.M, M], [ESC.N, N], [ESC.O, O], [ESC.P, P], [ESC.Q, Q], [ESC.R, R]]);
})();
