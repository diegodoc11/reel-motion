// reel-motion · ESCENAS del estilo FANZINE. Ejemplo: el reel ERA (1:17). Una estación por frase, una al lado de la otra; la cámara viaja de una a otra.
// ESC (dónde empieza cada estación) lo pone build_fanzine.py; tp("frase") = segundo en que se dice (words.json).

// la carretera: una línea de tiempo que corre por debajo de todas las estaciones y se va pintando de amarillo
CARRETERA = (t, vx0, vx1, cam) => {
  const y = 1172, a = Math.max(vx0, -700), b = Math.min(vx1, ESTACIONES[ESTACIONES.length - 1].X + 700);
  const hecho = Math.min(b, cam.frente);
  if (hecho > a) relleno('amarillo', caja(a, y - 11, hecho - a, 22));
  linea('azul', [[a, y], [b, y]], 4);
  for (let x = Math.ceil(a / 65) * 65; x < b; x += 65) linea('azul', [[x, y - 9], [x, y + 9]], 3);
  for (const E of ESTACIONES) {
    if (E.X < a - 200 || E.X > b + 200) continue;
    relleno('rosa', circulo(E.X, y, 14)); linea('azul', circulo(E.X, y, 14), 3.5, 1, true);
    if (E.marca) { const w = ancho(E.marca, 30) + 26; borra(caja(E.X + 26, y - 21, w, 42)); relleno('azul', caja(E.X + 26, y - 21, w, 42)); en('azul', () => { ctx.globalCompositeOperation = 'destination-out'; ctx.font = FUENTE(700, 30); ctx.textAlign = 'left'; ctx.fillText(E.marca, E.X + 39, y + 11); }); }
  }
};

// ---------------- A · 13 años: del caballo al carro, 1900 → 1913
{
  const x00 = 150, x13 = 900, t19 = tp('1900'), t13 = tp('1913');
  estacion('A', ESC.A, [
    titulo(tp('Trece'), '13 AÑOS', 540, 270, 110, { contar: 13 }),
    icono(tp('caballo'), 'caballo', 290, 640, 230),
    flecha(tp('movernos', tp('caballo')), [[440, 540], [545, 470], [650, 545]], 'rosa', 8),
    icono(tp('carro'), 'carro', 795, 665, 190),
    ejeNum(tp('desde', tp('carro')), 120, 960, 905, 13, 'azul'),
    nota(t19, '1900', x00, 965, 26),
    punto(t19 + .15, tp('hasta', t19), x00, x13, 905, 15, 'rosa'),
    nota(t13, '1913', x13, 965, 26),
    llave(t13 + .25, x00, x13, 868, '13 AÑOS', 'rosa', 22),
  ], '1900');
}
// ---------------- B · en esa época, más despacio
{
  const tm = tp('mucho', tp('movían'));
  estacion('B', ESC.B, [
    icono(tp('época'), 'caracol', 330, 690, 180),
    icono(tp('movían'), 'reloj', 790, 570, 230),
    trazo(tm - .1, [[140, 960], [940, 960]], 'azul', 5, .3, false),
    pieza(tm - .1, 2.6, p => relleno('rosa', circulo(140 + 300 * p, 960, 14 * back(clamp(p * 8))))),
    titulo(tp('más', tm) - .06, 'MÁS DESPACIO', 540, 300, 72),
  ]);
}
// ---------------- C · el segundo salto
{
  const ts = tp('Saltemos'), qx = 905;
  estacion('C', ESC.C, [
    ejeNum(ts - .02, 110, 970, 880, 10, 'azul'),
    nota(ts + .2, '1913', 150, 940, 26),
    flecha(tp('para', ESC.C), [[150, 850], [525, 560], [900, 850]], 'rosa', 9, .7),
    pregunta(tp('adelante') + .18, qx, 745, 90),
    titulo(tp('segundo'), 'SALTO 2', 540, 290, 100),
    etiqueta(tp('tecnológico'), 'TECNOLÓGICO', 540, 445, 30),
    lazo(tp('hemos') - .02, qx, 730, 72, 84, 'azul'),
  ]);
}
// ---------------- D · 2007, el primer iPhone
estacion('D', ESC.D, [
  icono(tp('smartphone'), 'celular', 540, 700, 380, 1.0),
  titulo(tp('2007'), '2007', 540, 290, 120, { contar: 2007, desde: 1990 }),
  rayos(tp('aparece'), 540, 700, 250, 270, [-2.6, -2.0, -1.15, -.55, .55, 1.15, 2.0, 2.6], 'rosa', 70, 9),
  insignia(tp('primer'), 'PRIMER IPHONE', 760, 1000, -.08, 'rosa', 34),
], '2007');
// ---------------- E · 7 años hasta que todos tuvieron smartphone
{
  const x0 = 120, x1 = 900, ts = tp('años', tp('siete'));
  const celus = [155, 118, 62, 25, 205, 335].map(a => [540 + Math.cos(a * Math.PI / 180) * 335, 660 - Math.sin(a * Math.PI / 180) * 240]);
  estacion('E', ESC.E, [
    ejeNum(tp('Desde', ESC.E) - .02, 110, 970, 1010, 7, 'azul', .7),
    nota(tp('punto'), '2007', x0, 1070, 26),
    punto(tp('punto') + .15, tp('hasta', ESC.E), x0, x1, 1010, 15, 'rosa', Math.max(.6, ts - tp('hasta', ESC.E))),
    icono(tp('mundo', ESC.E), 'mundo', 540, 650, 300),
    pieza(tp('smartphone', ESC.E) - .04, .8, p => celus.forEach(([x, y], k) => { const u = back(prog(p, k * .1, k * .1 + .4)); if (u > 0) escalar(x, y, u, () => { const r = caja(x - 23, y - 41, 46, 82); borra(r); relleno('azul', r, .45); linea('azul', r, 4, 1, true); relleno('azul', circulo(x, y + 30, 4)); }); })),
    titulo(tp('siete'), '7 AÑOS', 540, 280, 110, { contar: 7 }),
    nota(ts, '2014', x1, 1070, 26),
    llave(ts, x0, x1, 975, null, 'rosa'),
  ], '2014');
}
// ---------------- F · ChatGPT crece 6 veces más rápido que el iPhone
{
  const X0 = 190, Y0 = 1060, SX = 74, SY = 52;
  estacion('F', ESC.F, [
    ejes(tp('ChatGPT') - .1, X0, Y0, 950, 540),
    nota(tp('ChatGPT') + .2, 'TIEMPO', 870, 1100, 20),
    nota(tp('ChatGPT') + .3, 'USUARIOS', 300, 560, 20),
    curva(tp('creciendo') - .06, grafica(x => Math.min(9.6, .02 * x ** 3.3), 0, 6.4, X0, Y0, SX, SY), ['rosa'], 10, .7),
    nota(tp('creciendo') + .4, 'CHATGPT', 700, 545, 28, 'rosa'),
    titulo(tp('seis'), '×6', 540, 290, 120, { contar: 6, desde: 1 }),
    etiqueta(tp('velocidad'), 'VELOCIDAD DE ADOPCIÓN', 560, 435, 22),
    curva(tp('que', tp('velocidad')) - .06, grafica(x => .0035 * x ** 3.3, 0, 10, X0, Y0, SX, SY), ['azul'], 10, .6),
    nota(tp('que', tp('velocidad')) + .45, 'IPHONE', 880, 640, 28),
  ]);
}
// ---------------- G · llevamos apenas 3 años de IA generativa
{
  const tt = tp('tres');
  estacion('G', ESC.G, [
    icono(tp('llevamos'), 'calendario', 300, 710, 300),
    ...[0, 1, 2].map(k => trazo(tt - .06 + k * .14, [[720 + k * 70, 600], [732 + k * 70, 860]], 'rosa', 16, .2, false)),
    titulo(tp('años', tt) - .04, '3 AÑOS', 540, 290, 110, { contar: 3 }),
    etiqueta(tp('IA', ESC.G) - .3, 'DE IA GENERATIVA', 560, 1045, 30),
  ]);
}
// ---------------- H · ¿cuántos años faltan? 2
{
  const td = tp('dos') - .02, [a2, b2] = [640 - ancho('2 AÑOS', 96 * 1.38) / 2, 640 - ancho('2 AÑOS', 96 * 1.38) / 2 + ancho('2', 96 * 1.38)];
  estacion('H', ESC.H, [
    titulo(tp('¿Cuántos'), '¿CUÁNTOS AÑOS?', 540, 285, 64),
    pregunta(tp('crees') - .04, 905, 430, 70), pregunta(tp('crees') + .08, 975, 380, 90, 'azul'),
    icono(tp('mundo', ESC.H), 'mundo', 540, 650, 300),
    etiqueta(tp('IA', ESC.H), 'IA', 740, 505, 34),
    lazo(tp('todo', tp('IA', ESC.H)), 540, 655, 245, 235, 'azul'),
    nota(tp('creo'), 'YO CREO', 230, 940, 26),
    titulo(td, '2 AÑOS', 640, 1060, 96, { contar: 2 }),
    lazo(tp('sea') - .1, (a2 + b2) / 2, 1062, 70, 78, 'rosa'),
  ]);
}
// ---------------- I · "eso lo usarán mis nietos"
estacion('I', ESC.I, [
  gente(ESC.I + .12, 'abuelo', 540, 520, 150, 'rosa'),
  nota(tp('eso', ESC.I), '"ESO LO USARÁN', 540, 790, 40),
  nota(tp('mis', ESC.I), 'MIS NIETOS"', 560, 890, 40),
  tacha(tp('nietos') - .22, 545, 840, 300, 'rosa', 95),
]);
// ---------------- J1 · el nivel de adopción de los niños
estacion('J1', ESC.J1, [
  medidor(tp('miremos'), tp('nivel'), 540, 840, 275, .93),
  nota(tp('nivel') + .2, 'NIVEL', 540, 905, 26),
  titulo(tp('adopción'), 'ADOPCIÓN', 540, 290, 92),
]);
// ---------------- J2 · un niño de 8 años: pregúntale a ChatGPT
{
  const g2 = tp('Google', ESC.J2), c2 = tp('ChatGPT', g2), L1 = 'PREGÚNTALE A GOOGLE', L2 = 'PREGÚNTALE A CHATGPT';
  const [gx0, gx1] = tramo(L1, 'GOOGLE', 660, 34), [cx0, cx1] = tramo(L2, 'CHATGPT', 660, 34);
  estacion('J2', ESC.J2, [
    gente(ESC.J2 + .2, 'nino', 190, 650, 120, 'amarillo'),
    titulo(tp('8'), '8 AÑOS', 600, 285, 100, { contar: 8 }),
    nota(tp('pregúntale'), L1, 660, 640, 34),
    tachar(g2 + .04, gx0 - 8, gx1 + 8, 640),
    nota(tp('pregúntale', g2), L2, 660, 860, 34),
    chulo(c2 + .02, 270, 860, 42),
    trazo(c2 + .25, [[cx0, 910], [cx1, 910]], 'rosa', 8, .3, false),
  ]);
}
// ---------------- K · creció con ChatGPT, no con Google
{
  const ck = tp('ChatGPT', ESC.K), [gx0, gx1] = tramo('GOOGLE', 'GOOGLE', 800, 36);
  estacion('K', ESC.K, [
    titulo(tp('creció'), 'CRECIÓ', 600, 285, 92),
    regla(tp('creció') + .16, 110, 480, 1100, 13),
    gente(tp('creció') + .26, 'nino', 330, 800, 125, 'amarillo'),
    flecha(tp('con', tp('creció')), [[205, 1080], [205, 880], [205, 690]], 'rosa', 8),
    pregunta(tp('dudas') - .04, 520, 600, 70), pregunta(tp('dudas') + .06, 600, 520, 92),
    pregunta(tp('preguntas', tp('dudas')) - .04, 545, 760, 62, 'azul'), pregunta(tp('preguntas', tp('dudas')) + .06, 632, 700, 80, 'azul'),
    nota(ck, 'CHATGPT', 800, 880, 36),
    chulo(ck + .3, 600, 880, 36),
    nota(tp('no', ck), 'GOOGLE', 800, 1020, 36),
    tachar(tp('Google', ESC.K) + .02, gx0 - 10, gx1 + 10, 1020),
  ]);
}
// ---------------- L · natural: no van a entender los teclados
{
  const tg = tp('generación') - .06, te = tp('entender') - .04;
  estacion('L', ESC.L, [
    titulo(tp('natural'), 'NATURAL', 540, 290, 100),
    ...[['nino', 'amarillo'], ['mujer', 'rosa'], ['joven', 'azul']].map(([tipo, c], k) => gente(tg + k * .14, tipo, 290 + k * 250, 640, 82, c)),
    ...[0, 1, 2].map(k => pregunta(te + k * .12, 290 + k * 250, 480, 60)),
    icono(tp('teclados'), 'teclado', 540, 960, 150),
  ]);
}
// ---------------- M · un muchacho de 14 no entiende los casetes
{
  const tc = tp('casetes', ESC.M);
  estacion('M', ESC.M, [
    gente(tp('muchacho'), 'joven', 230, 660, 120, 'rosa'),
    titulo(tp('14'), '14 AÑOS', 600, 285, 100, { contar: 14 }),
    pregunta(tp('entiende') - .04, 400, 530, 72),
    icono(tc, 'casete', 700, 670, 200),
    flecha(tp('en', tc), [[650, 800], [610, 850], [570, 890]], 'rosa', 7),
    icono(tp('Walkman'), 'walkman', 430, 990, 260),
  ]);
}
// ---------------- N · para los niños es normal; para tus clientes también
estacion('N', ESC.N, [
  gente(tp('niños', ESC.N), 'nino', 200, 560, 105, 'amarillo'),
  titulo(tp('normal'), 'NORMAL', 560, 285, 100),
  chulo(tp('normal') + .25, 336, 470, 44),
  etiqueta(tp('tus'), 'TUS CLIENTES', 640, 705, 34),
  gente(tp('clientes', ESC.N), 'adulto', 420, 930, 88, 'amarillo'),
  gente(tp('también', ESC.N), 'mujer', 640, 930, 88, 'rosa'),
  gente(tp('va', tp('también', ESC.N)), 'abuelo', 860, 930, 88, 'azul'),
]);
// ---------------- O · el negocio sin IA va a sonar a casete
{
  const tc = tp('casete', ESC.O);
  estacion('O', ESC.O, [
    icono(tp('negocio', ESC.O), 'tienda', 520, 700, 340),
    insignia(tp('IA', ESC.O) - .06, 'SIN IA', 520, 470, -.12, 'rosa', 50),
    ondas(tp('sonar') - .06, 780, 700, 'azul'),
    titulo(tc, 'CASETE', 540, 270, 100),
    icono(tc + .25, 'casete', 760, 1010, 160),
  ]);
}
// ---------------- P · agentes que reemplazan el trabajo lento y caro: hoy
{
  const hoy = tp('hoy', ESC.P), [l0, l1] = tramo('LENTO', 'LENTO', 300, 36), [c0, c1] = tramo('CARO', 'CARO', 780, 36);
  estacion('P', ESC.P, [
    ...[[215, tp('agentes')], [540, tp('IA', ESC.P)], [865, tp('reemplazan')]].flatMap(([x, w], k) => [icono(w, 'robot', x, 880, 250, .6), nota(w + .3, `AGENTE 0${k + 1}`, x, 1062, 20)]),
    nota(tp('lento') - .06, 'LENTO', 300, 560, 36), tachar(tp('lento') + .2, l0 - 10, l1 + 10, 560),
    nota(tp('caro') - .06, 'CARO', 780, 560, 36), tachar(tp('caro') + .2, c0 - 10, c1 + 10, 560),
    titulo(hoy, 'HOY', 540, 290, 140),
    insignia(tp('no', hoy) - .06, 'NO ES MODA', 540, 700, -.06, 'rosa', 44),
  ], 'HOY');
}
// ---------------- Q · separará a las que triunfen de las que quiebren (dos curvas que se separan)
{
  const ts = tp('separará'), X0 = 150, Y0 = 790, SX = 78, SY = 56;
  estacion('Q', ESC.Q, [
    ejes(ts - .06, X0, 1080, 950, 480),
    curva(ts + .3, [[X0, Y0], [X0 + 4 * SX, Y0]], ['azul'], 10, .35),
    titulo(tp('empresas'), 'EMPRESAS', 540, 285, 70),
    curva(tp('triunfen') - .06, grafica(x => .12 * (x - 4) ** 2.1, 4, 10, X0, Y0, SX, SY), ['azul', 'amarillo'], 11, .6),
    nota(tp('triunfen') + .3, 'TRIUNFAN', 760, 470, 32, ['azul', 'amarillo']),
    curva(tp('de', tp('triunfen')) - .06, grafica(x => -.12 * (x - 4) ** 2.1, 4, 10, X0, Y0, SX, SY), ['rosa', 'amarillo'], 11, .55),
    nota(tp('de', tp('triunfen')) + .25, 'QUIEBRAN', 760, 1120, 32, ['rosa', 'amarillo']),
  ]);
}
// ---------------- R · comenta ERA
{
  const tc = tp('clase'), ti = tp('instalarlas');
  estacion('R', ESC.R, [
    nota(ESC.R + .04, 'COMENTA', 540, 180, 30),
    titulo(tp('ERA'), 'ERA', 540, 375, 160),
    icono(tp('envío'), 'sobre', 300, 760, 170),
    icono(tc, 'laptop', 750, 790, 210),
    nota(tc + .5, 'CLASE', 750, 945, 28),
    titulo(ti, '¡EN TU NEGOCIO!', 540, 1060, 52),
    trazo(tp('negocio', ti), [[250, 1118], [830, 1118]], 'rosa', 8, .4, false),
  ], 'ERA');
}
