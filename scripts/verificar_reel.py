# -*- coding: utf-8 -*-
"""
reel-motion · VERIFICAR  — chequeos objetivos del borrador que al ojo se le pasan (correr ANTES de mostrarlo):
    python verificar_reel.py <carpeta_proyecto> [--video renders/borrador.mp4]
  1. PORTADA: el cuadro 0 (es la portada en Instagram y el cuadro del bucle) debe tener gráficos en la zona de arriba,
     no solo la tarjeta vacía ni una palabra suelta.
  2. MÚSICA HASTA EL FINAL: el último medio segundo no debe quedar en silencio (el motor desvanece la música 1.4 s
     antes de DUR; si la voz termina tarde, se oye un hueco).
  3. CORTES/HUECOS DE MÚSICA: ningún tramo de la pista nivelada (_work/music_lvl.wav) cae a silencio a mitad del reel.
Sale con código 1 si falla la 1 o la 2. Imprime en español qué mirar y en qué segundo.
"""
import sys, os, subprocess, json, re
import numpy as np
from PIL import Image

proj = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
video = os.path.join(proj, sys.argv[sys.argv.index('--video') + 1] if '--video' in sys.argv else 'renders/borrador.mp4')
if not os.path.exists(video): sys.exit(f'no existe {video}')
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video], capture_output=True, text=True).stdout.strip())
tmp = os.path.join(proj, '_work', 'verificar'); os.makedirs(tmp, exist_ok=True)
fallas = []; avisos = []

def cuadro(t, nombre):
    out = os.path.join(tmp, nombre)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', video, '-frames:v', '1', out], check=True)
    return np.asarray(Image.open(out).convert('RGB')).astype(np.int32)

def vol(ss, to, src=video):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-ss', f'{ss:.3f}', '-to', f'{to:.3f}', '-i', src, '-af', 'volumedetect', '-vn', '-f', 'null', '-'], capture_output=True, text=True).stderr
    m = re.search(r'mean_volume: (-?[\d.]+)', r); return float(m.group(1)) if m else -99.0

# 1. portada: cuántos píxeles "claros" hay en la zona de gráficos (y 262-740) del cuadro 0 frente a un cuadro a 1.5 s
f0 = cuadro(0.0, 'f0.png'); f1 = cuadro(min(1.5, dur - 0.1), 'f1.png')
def claros(f): z = f[262:740, 78:1002]; return float((z.max(-1) > 170).mean())
c0, c1 = claros(f0), claros(f1)
if c0 < 0.012 or (c1 > 0 and c0 < 0.35 * c1):
    fallas.append(f'PORTADA: el cuadro 0 casi no tiene gráficos arriba ({c0*100:.1f}% de píxeles claros; a 1.5 s hay {c1*100:.1f}%). '
                  f'Pon el titular del gancho completo desde el cuadro 0 (I(..., opacity=1) y que la animación palabra por palabra arranque en 0.02).')
# 2. música hasta el final
fin = vol(dur - 0.5, dur); medio = vol(dur * 0.4, dur * 0.6)
if fin < medio - 9:
    fallas.append(f'MÚSICA AL FINAL: los últimos 0.5 s suenan a {fin:.1f} dB frente a {medio:.1f} dB en la mitad: hay un hueco de silencio en el cierre. '
                  f'Alarga la cola de la voz (apad) o acorta el fundido de la música (afade st=DUR-0.3) para que llegue al último cuadro.')
# 3. cortes de música a mitad
mus = os.path.join(proj, '_work', 'music_lvl.wav')
if os.path.exists(mus):
    t = 0.5
    while t < dur - 1.5:
        v = vol(t, t + 0.5, mus)
        if v < -45: avisos.append(f'MÚSICA: silencio en la pista entre {t:.1f} y {t + 0.5:.1f} s (mueve inicio_musica o cambia de pista).')
        t += 0.5
print(f'verificar_reel · {os.path.basename(video)} · {dur:.2f} s')
for x in fallas: print('  ✗', x)
for x in avisos: print('  ⚠', x)
if not fallas and not avisos: print('  ✓ portada con gráficos, música hasta el final, sin cortes en la pista.')
sys.exit(1 if fallas else 0)
