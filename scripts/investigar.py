# -*- coding: utf-8 -*-
"""
reel-motion · INVESTIGAR  (estilo recrear)  — saca los cuadros clave del VIDEO VIRAL que se va a recrear.

    python investigar.py <video_o_enlace> <P> [--cada 0.5] [--max 60]

<video_o_enlace> : archivo de video (mp4/mov/webm) o enlace (YouTube, TikTok, Instagram, X…; usa yt-dlp).
<P>              : carpeta del proyecto del reel. Deja todo en P/_work/viral/:
                     viral.mp4         el video (copiado o descargado)
                     hoja.jpg          hoja de contacto: un cuadro cada --cada segundos con su segundo (mírala)
                     cortes.jpg        los cuadros donde la imagen CAMBIA de golpe (cambios de plano / el momento clave)
                     cuadros/NN-ss.png cada cuadro de cortes.jpg suelto, por si hay que mirar uno grande
                     notas.md          plantilla para anotar QUÉ pasó, el gesto icónico y qué objetos hay que dibujar

Lo que sigue lo haces tú (el agente): mira hoja.jpg y cortes.jpg, describe en notas.md el hecho en 3-5 pasos
("el carro rueda → sube la rampa → da media vuelta → sale volando"), decide qué objeto(s) dibujar y con qué
recorrido, y recién ahí escribe la escena 1 del build (R.objeto / R.carro + R.recorrido). No se pega NUNCA el video
viral en el reel: se RECREA en dibujo (sin problema de derechos y se ve como análisis, no como repost).
"""
import os, sys, re, json, shutil, subprocess

def run(cmd, **k):
    return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', **k)

def duracion(fn):
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', fn])
    return float(json.loads(r.stdout)['format']['duration'])

def descargar(url, out):
    try:
        import yt_dlp
    except ImportError:
        raise SystemExit('Falta yt-dlp en el entorno de la skill: corre  python scripts/instalar.py  (o pip install yt-dlp) y vuelve a intentar.')
    opts = {'outtmpl': out, 'format': 'bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]/b', 'merge_output_format': 'mp4',
            'quiet': True, 'no_warnings': True, 'noplaylist': True}
    with yt_dlp.YoutubeDL(opts) as y:
        y.download([url])
    if not os.path.exists(out):
        raise SystemExit('No pude descargar el video. Descárgalo tú (o guárdalo desde el celular) y pásame el archivo.')

def hoja(video, out, t0, t1, paso, cols=8, cw=220):
    """hoja de contacto con el segundo de cada cuadro (misma lógica de hoja.py)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    r = run([sys.executable, '-X', 'utf8', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hoja.py'),
             video, out, f'{t0:.2f}', f'{t1:.2f}', f'{paso:.3f}', str(cols), str(cw)])
    if r.returncode != 0: print(r.stdout, r.stderr)

def cortes(video, carpeta, umbral=0.28, maximo=24):
    """segundos donde la imagen cambia de golpe (cambio de plano o el momento clave)."""
    r = run(['ffmpeg', '-v', 'info', '-i', video, '-vf', f"select='gt(scene,{umbral})',showinfo", '-vsync', 'vfr', '-f', 'null', '-'])
    ts = [float(m) for m in re.findall(r'pts_time:\s*([\d.]+)', r.stderr)]
    ts = [0.0] + [t for t in ts if t > 0.3]
    if len(ts) > maximo:                                    # demasiados cortes (video muy movido): quédate con los más repartidos
        paso = len(ts) / maximo; ts = [ts[int(i * paso)] for i in range(maximo)]
    os.makedirs(carpeta, exist_ok=True)
    for i, t in enumerate(ts):
        run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{t:.3f}', '-i', video, '-frames:v', '1', '-vf', 'scale=540:-2', os.path.join(carpeta, f'{i:02d}-{t:06.2f}s.png')])
    return ts

def montar(carpeta, out, cols=4):
    from PIL import Image, ImageDraw
    fns = sorted(f for f in os.listdir(carpeta) if f.endswith('.png'))
    if not fns: return
    ims = [Image.open(os.path.join(carpeta, f)).convert('RGB') for f in fns]
    w = max(i.width for i in ims); h = max(i.height for i in ims); filas = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * (w + 8) + 8, filas * (h + 34) + 8), (24, 24, 24)); d = ImageDraw.Draw(sheet)
    for k, (im, fn) in enumerate(zip(ims, fns)):
        x = 8 + (k % cols) * (w + 8); y = 8 + (k // cols) * (h + 34)
        sheet.paste(im, (x, y + 26)); d.text((x + 4, y + 6), fn.replace('.png', '').replace('-', '  ·  '), fill=(255, 255, 255))
    sheet.save(out, quality=88)

NOTAS = """# Qué pasó en el video viral (llénalo ANTES de dibujar nada)

Fuente: {fuente}
Duración: {dur:.1f} s · cuadros clave en cortes.jpg · todo el video en hoja.jpg

## El hecho, en 3-5 pasos (lo que la gente vio)
1.
2.
3.

## El gesto icónico (el momento que todos recuerdan; es lo que se recrea en la escena 1)
-

## Objetos que hay que dibujar (SVG plano, trazo + relleno; nada de caras reconocibles ni logos oficiales)
- objeto:            · qué hace (rueda / sube / vuela / cae / se abre…):            · recorrido:

## Datos del caso para las piezas de negocio (precios, cifras, nombres de versiones, fechas)
-

## Qué dice el presentador en cada paso (frase exacta de words.json → qué se ve)
| frase | pieza | qué se ve |
|---|---|---|
"""

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) < 2: raise SystemExit(__doc__)
    src, P = args[0], os.path.abspath(args[1])
    cada = float(sys.argv[sys.argv.index('--cada') + 1]) if '--cada' in sys.argv else 0.5
    maximo = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 60
    wk = os.path.join(P, '_work', 'viral'); os.makedirs(wk, exist_ok=True)
    video = os.path.join(wk, 'viral.mp4')
    if re.match(r'https?://', src):
        print(f'descargando {src} …', flush=True); descargar(src, video)
    else:
        if not os.path.exists(src): raise SystemExit(f'No existe: {src}')
        shutil.copy(src, video)
    dur = duracion(video)
    print(f'viral.mp4: {dur:.1f} s')
    paso = max(cada, dur / maximo)
    hoja(video, os.path.join(wk, 'hoja.jpg'), 0.0, dur - 0.05, paso)
    print(f'hoja.jpg: un cuadro cada {paso:.2f} s')
    ts = cortes(video, os.path.join(wk, 'cuadros'))
    montar(os.path.join(wk, 'cuadros'), os.path.join(wk, 'cortes.jpg'))
    print(f'cortes.jpg: {len(ts)} cuadros clave en ' + ', '.join(f'{t:.1f}' for t in ts) + ' s')
    with open(os.path.join(wk, 'notas.md'), 'w', encoding='utf-8') as f:
        f.write(NOTAS.format(fuente=src, dur=dur))
    print(f'notas.md: plantilla para describir el hecho -> {wk}')
    print('\nAhora MIRA hoja.jpg y cortes.jpg, llena notas.md y recién después dibuja la recreación (escena 1 del build).')

if __name__ == '__main__':
    main()
