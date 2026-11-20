// render_canvas.mjs — rueda una página de canvas (window.draw(frame), window.FRAMES, window.FPS; opcional window.LISTO)
// a MP4 sin audio, o saca fotos sueltas para revisar. Reparte el video en tramos seguidos entre varias pestañas del
// navegador (cada una con su ffmpeg) y al final los pega: así rinde lo que da el computador.
//   node render_canvas.mjs pagina.html fondo.mp4 [--workers 3]
//   node render_canvas.mjs pagina.html fotos/x --stills 3s,12.5s,40        -> fotos/x-0090.jpg ...
// Usa Chrome si está instalado; si no, el Chromium de Playwright (npx playwright-core install chromium).
import { createRequire } from 'module';
import { resolve, dirname, join } from 'path';
import { spawn } from 'child_process';
import { writeFileSync, mkdirSync, rmSync, existsSync } from 'fs';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright-core');
const args = process.argv.slice(2), opt = (k) => { const i = args.indexOf(k); return i >= 0 ? (args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true) : null; };
const [pagina, salida] = args;
if (!pagina || !salida) { console.error('uso: node render_canvas.mjs pagina.html salida.mp4 [--workers N] | --stills 3s,12s'); process.exit(1); }
const browser = await chromium.launch({ channel: 'chrome' }).catch(() => chromium.launch());
async function abrir() {
  const p = await browser.newPage(); const errores = []; p.on('pageerror', (e) => errores.push(String(e)));
  await p.goto('file://' + resolve(pagina) + '?render');
  await p.waitForFunction(() => window.ERROR || (typeof window.draw === 'function' && window.FRAMES && window.LISTO !== false), null, { timeout: 180000 });
  const err = await p.evaluate(() => window.ERROR); if (err || errores.length) { console.error('error en la página:', err || '', errores.join('\n')); process.exit(1); }
  return p;
}
const grab = (p, f) => p.evaluate((f) => { window.draw(f); return document.querySelector('canvas').toDataURL('image/jpeg', 0.93).split(',')[1]; }, f);
const p0 = await abrir();
const { FRAMES, FPS, w, h } = await p0.evaluate(() => ({ FRAMES: window.FRAMES, FPS: window.FPS, w: document.querySelector('canvas').width, h: document.querySelector('canvas').height }));
if (opt('--stills')) {
  mkdirSync(dirname(resolve(salida)), { recursive: true });
  for (const v of String(opt('--stills')).split(',')) {
    const f = Math.min(FRAMES - 1, v.trim().endsWith('s') ? Math.round(parseFloat(v) * FPS) : Number(v)), t0 = Date.now();
    writeFileSync(`${salida}-${String(f).padStart(4, '0')}.jpg`, Buffer.from(await grab(p0, f), 'base64'));
    console.log(`foto ${f} (${(f / FPS).toFixed(2)} s) en ${Date.now() - t0} ms`);
  }
  await browser.close(); process.exit(0);
}
if (w % 2 || h % 2) { console.error(`el canvas mide ${w}x${h}: H.264 necesita ancho y alto pares`); process.exit(1); }
const N = Math.max(1, Number(opt('--workers') || 3));
const tmp = resolve(dirname(resolve(salida)), '_tramos'); if (existsSync(tmp)) rmSync(tmp, { recursive: true }); mkdirSync(tmp, { recursive: true });
const paso = Math.ceil(FRAMES / N), t0 = Date.now(); let hechos = 0;
async function tramo(k, p) {
  const a = k * paso, b = Math.min(FRAMES, a + paso); if (a >= b) return null;
  const out = join(tmp, `t${k}.mp4`);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', String(FPS), out]);
  const fin = new Promise((ok, mal) => ff.on('close', (c) => c === 0 ? ok() : mal(new Error('ffmpeg ' + c))));
  for (let f = a; f < b; f++) {
    const buf = Buffer.from(await grab(p, f), 'base64'); if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    if (++hechos % (FPS * 5) === 0) { const s = (Date.now() - t0) / 1000; console.log(`${hechos}/${FRAMES} cuadros · ${s.toFixed(0)} s · faltan ~${(s / hechos * (FRAMES - hechos) / 60).toFixed(1)} min`); }
  }
  ff.stdin.end(); await fin; return out;
}
const paginas = [p0]; for (let k = 1; k < N; k++) paginas.push(await abrir());
const tramos = (await Promise.all(paginas.map((p, k) => tramo(k, p)))).filter(Boolean);
writeFileSync(join(tmp, 'lista.txt'), tramos.map((t) => `file '${t.replace(/\\/g, '/')}'`).join('\n'));
await new Promise((ok, mal) => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', join(tmp, 'lista.txt'), '-c', 'copy', resolve(salida)]).on('close', (c) => c === 0 ? ok() : mal(new Error('concat ' + c))));
rmSync(tmp, { recursive: true });
console.log(`listo: ${FRAMES} cuadros en ${((Date.now() - t0) / 60000).toFixed(1)} min -> ${salida}`);
await browser.close();
