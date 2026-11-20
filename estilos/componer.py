# -*- coding: utf-8 -*-
"""reel-motion · ESTILOS CON MOTOR PROPIO · lo común a los 6 (handdraw, muñecos, pizarra animada, motion design,
gráficas, fanzine).

Cada estilo dibuja el FONDO ANIMADO (1080x1920, 30 fps, sin audio) con su propio motor, en el segundo exacto de cada
palabra. Este módulo le pone encima todo lo demás, igual en los 6:
  voz real · música (bajada sola cuando hablas) · efectos (swipe en cada cambio de toma, pop en cada golpe) ·
  subtítulo fantasma (la frase en gris y cada palabra se enciende al decirla, la palabra clave en rojo) ·
  el presentador recortado CHICO abajo a la derecha · hojas de revisión cada 1 s · copia liviana para el celular.

Lee el proyecto que dejan scripts/preparar.py y scripts/recortar.py: words.json, cutmap.json, voice.wav, face.json,
silueta.json y cutout.webm.

    import componer as C
    r = C.Reel(P, estilo='fanzine', correcciones={...}, rojas=('Trece', 'casete'), musica='auto')
    ft = r.ft                                  # ft('frase', despues=s) -> segundo en que empieza la frase
    ESC = dict(A=0.0, B=ft('Saltemos') - 0.12, ...)   # inicio de cada toma (cada cuadro nuevo)
    r.exportar_tiempos(ESC, os.path.join(P, '_work', 'tiempos.json'))   # palabras + tomas para el motor
    ... el motor rueda P/<estilo>_raw.mp4 ...
    r.sfx = r.efectos_tomas(ESC) + r.golpes([ft('Trece'), ft('2007')])
    r.subtitulos(); r.audio(); r.componer(raw='<estilo>_raw.mp4'); r.entregar()
"""
import json
import os
import re
import statistics
import subprocess
import sys
import time
import unicodedata

from PIL import ImageFont

ESTILOS = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(ESTILOS)
REC = os.path.join(SKILL, 'recursos')
SFX = os.path.join(REC, 'sfx')
W, H, FPS = 1080, 1920, 30
TINTA = '#172033'
ROJO = '#E5322D'

# letra del subtítulo: Microsoft YaHei Bold en Windows; en Mac/Linux, Poppins (viene en la skill)
_YAHEI = r'C:\Windows\Fonts\msyhbd.ttc'
_POPPINS = os.path.join(REC, 'fonts', 'poppins-800.ttf')
if os.path.exists(_YAHEI):
    FUENTE_SUB, NOMBRE_SUB, DIR_FUENTES = _YAHEI, 'Microsoft YaHei', None
else:
    FUENTE_SUB, NOMBRE_SUB, DIR_FUENTES = _POPPINS, 'Poppins', os.path.join(REC, 'fonts')
_SEGOE = r'C:\Windows\Fonts\segoeuib.ttf'
FUENTE_HOJAS = _SEGOE if os.path.exists(_SEGOE) else _POPPINS


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9ñ]', '', s)


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', **kw)
    if r.returncode:
        print(r.stdout[-3000:]); print(r.stderr[-3000:])
        raise SystemExit(f'falló: {os.path.basename(str(cmd[0]))} ({r.returncode})')
    return r


def _ff(ruta):
    """ruta para los filtros de ffmpeg (Windows: barras normales y ':' escapado)."""
    return ruta.replace('\\', '/').replace(':', '\\:')


_FONTS = {}


def ancho_texto(texto, fs, fuente=None):
    """ancho visual (px) de una línea en la letra del subtítulo."""
    f = fuente or FUENTE_SUB
    k = (f, fs)
    fo = _FONTS.get(k) or _FONTS.setdefault(k, ImageFont.truetype(f, fs))
    return fo.getlength(texto) + 0.045 * fs * max(0, len(texto) - 1)


def buscar_musica(nombre, P):
    """'auto' = primera pista de <proyecto>/musica o de recursos/musica de la skill; o un nombre/ruta; None = sin música."""
    if not nombre: return None
    import glob
    if nombre == 'auto':
        for d in (os.path.join(P, 'musica'), os.path.join(REC, 'musica')):
            for ext in ('mp3', 'wav', 'm4a', 'ogg', 'flac'):
                g = sorted(glob.glob(os.path.join(d, '*.' + ext)))
                if g: return g[0]
        print('  (aviso) sin música: no hay pistas en <proyecto>/musica ni en recursos/musica. Sale con voz y efectos.')
        return None
    for c in (nombre, os.path.join(P, nombre), os.path.join(P, 'musica', nombre), os.path.join(REC, 'musica', nombre)):
        if os.path.isfile(c): return c
    print(f'  (aviso) no encontré la música "{nombre}": sale con voz y efectos.')
    return None


class Reel:
    def __init__(self, P, estilo, nombre=None, correcciones=None, rojas=(), musica='auto', volumen_musica=0.28, inicio_musica=0.0,
                 dur=None, cabeza=(826, 1258), alto_cabeza=262, referencia=None):
        self.P = P; self.estilo = estilo; self.nombre = nombre or os.path.basename(os.path.normpath(P))
        for f in ('words.json', 'cutmap.json', 'voice.wav', 'face.json', 'silueta.json', 'cutout.webm'):
            if not os.path.exists(os.path.join(P, f)):
                raise SystemExit(f'falta {f} en el proyecto: corre primero scripts/preparar.py y scripts/recortar.py (SKILL.md §2.1-2.3)')
        self.WD = json.load(open(os.path.join(P, 'words.json'), encoding='utf-8'))
        corr = {norm(k): v for k, v in (correcciones or {}).items()}
        for w in self.WD:
            k = norm(w['text']); w['raw'] = w['text']
            if k in corr:
                pre = re.match(r'^[¿¡"“]*', w['text']).group(0); pos = re.search(r'[.,;:?!"”]*$', w['text']).group(0)
                w['text'] = pre + corr[k] + pos
        cm = json.load(open(os.path.join(P, 'cutmap.json')))
        self.DUR = round((dur or cm['dur']) * FPS) / FPS
        self.rojas = {norm(r) for r in rojas}
        self.musica = buscar_musica(musica, P); self.vol, self.ini_mus = volumen_musica, inicio_musica
        self.referencia = referencia                # video de comparación (opcional): lado a lado y fotos pareadas
        self.cabeza, self.alto_cabeza = cabeza, alto_cabeza
        self.sfx = []
        for d in ('_work', 'renders'): os.makedirs(os.path.join(P, d), exist_ok=True)

    # ------------------------------------------------------------------------------------------- tiempos
    def ft(self, frase, despues=0.0, fin=False):
        """segundo en que empieza (o termina, fin=True) la frase/palabra, buscando desde `despues`."""
        partes = [norm(p) for p in frase.split()]
        for i, w in enumerate(self.WD):
            if w['start'] < despues - 0.001: continue
            ok = True
            for j, p in enumerate(partes):
                if i + j >= len(self.WD): ok = False; break
                ww = self.WD[i + j]
                if not (norm(ww['text']) == p or norm(ww['raw']) == p or (len(p) >= 4 and (norm(ww['text']).startswith(p) or norm(ww['raw']).startswith(p)))):
                    ok = False; break
            if ok:
                return self.WD[i + len(partes) - 1]['end'] if fin else w['start']
        raise SystemExit(f'no encontré "{frase}" después de {despues:.2f}s (mira el guion con --guion)')

    def guion(self):
        """imprime el guion con el segundo de cada frase (para escoger las palabras de ft())."""
        line = []; t0 = None
        for i, w in enumerate(self.WD):
            if t0 is None: t0 = w['start']
            line.append(w['text'])
            if w['text'][-1:] in '.?!,' and len(line) >= 5 or len(line) >= 12 or i == len(self.WD) - 1:
                print(f'{t0:6.2f}  ' + ' '.join(line)); line = []; t0 = None

    def exportar_tiempos(self, esc, ruta, formato='json'):
        """palabras con su segundo (WORDS: s, e, w = corregida, r = original), inicio de cada toma (ESC) y DUR, para el motor."""
        words = [{'s': round(w['start'], 3), 'e': round(w['end'], 3), 'w': w['text'], 'r': w['raw']} for w in self.WD]
        esc = {k: round(v, 3) for k, v in esc.items()}
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        if formato == 'ts':
            txt = ('// generado por estilos/componer.py: palabras con su segundo (WORDS), inicio de cada toma (ESC)\n'
                   f'export const WORDS: {{ s: number; e: number; w: string; r: string }}[] = {json.dumps(words, ensure_ascii=False)};\n'
                   f'export const ESC: Record<string, number> = {json.dumps(esc)};\nexport const DUR = {self.DUR};\n')
            open(ruta, 'w', encoding='utf-8').write(txt)
        else:
            json.dump({'WORDS': words, 'ESC': esc, 'DUR': self.DUR}, open(ruta, 'w', encoding='utf-8'), ensure_ascii=False)
        return ruta

    def efectos_tomas(self, esc, saltar=(), antes=0.05, ganancia=0.07, sonido='swipe.wav'):
        """un swipe en cada cambio de toma (menos la primera y las de `saltar`, que siguen en el mismo cuadro)."""
        return [(v - antes, sonido, ganancia) for k, v in list(esc.items())[1:] if k not in saltar]

    def golpes(self, tiempos, ganancia=0.1, sonido='pop.wav'):
        """un pop en cada golpe (palabra clave que entra, sello, contador)."""
        return [(t, sonido, ganancia) for t in tiempos]

    # ------------------------------------------------------------------------------------------- subtítulo fantasma (ASS)
    def subtitulos(self, x=54, y=1230, ancho=590, fs=46, fantasma='#C4BDB0', tinta=None, borde='#FFFDF8', roja=ROJO):
        """subtítulo abajo a la izquierda (al lado del presentador): fondo claro -> valores por defecto;
        fondo oscuro -> fantasma='#7A8291', tinta='#FFFFFF', borde='#0E1116'."""
        def col(hexa):
            hexa = hexa.lstrip('#'); return f'&H00{hexa[4:6]}{hexa[2:4]}{hexa[0:2]}'.upper()

        def nfilas(ws):
            filas, fila = 0, []
            for w in ws:
                prueba = ' '.join(z['text'].upper() for z in fila + [w])
                if fila and ancho_texto(prueba, fs) > ancho: filas += 1; fila = [w]
                else: fila.append(w)
            return filas + (1 if fila else 0)
        grupos, cur = [], []
        for w in self.WD:
            if cur and (nfilas(cur + [w]) > 2 or w['start'] - cur[-1]['end'] > 0.6):
                grupos.append(cur); cur = []
            cur.append(w)
            if w['text'][-1:] in '.?!:': grupos.append(cur); cur = []
        if cur: grupos.append(cur)

        def ts(t):
            t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
            return f'{h}:{m:02d}:{s:05.2f}'
        lines = ['[Script Info]', 'ScriptType: v4.00+', f'PlayResX: {W}', f'PlayResY: {H}', 'WrapStyle: 2', 'ScaledBorderAndShadow: yes', '',
                 '[V4+ Styles]',
                 'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
                 f'Style: K,{NOMBRE_SUB},{fs},{col(tinta or TINTA)},{col(fantasma)},{col(borde)},&H00000000,-1,0,0,0,100,100,1,0,1,3,0,7,0,0,0,1',
                 '', '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
        for gi, g in enumerate(grupos):
            t0 = g[0]['start'] - 0.05
            t1 = grupos[gi + 1][0]['start'] - 0.05 if gi + 1 < len(grupos) else self.DUR
            t1 = min(t1, g[-1]['end'] + 1.2) if gi + 1 < len(grupos) else t1
            palabras = [w['text'].upper() for w in g]
            filas, fila = [], []
            for k, p in enumerate(palabras):
                prueba = ' '.join(palabras[i] for i in fila + [k])
                if fila and ancho_texto(prueba, fs) > ancho: filas.append(fila); fila = [k]
                else: fila.append(k)
            if fila: filas.append(fila)
            # libass enciende cada palabra (\k) al EMPEZAR su duración: cada palabra dura hasta que empieza la siguiente
            g0 = max(1, round((g[0]['start'] - t0) * 100))
            partes = [f'{{\\pos({x},{y})}}{{\\k{g0}}}']
            for fi, fila in enumerate(filas):
                for j, k in enumerate(fila):
                    w = g[k]
                    sig = g[k + 1]['start'] if k + 1 < len(g) else w['end'] + 0.3
                    dk = max(1, round((sig - w['start']) * 100))
                    es_roja = norm(w['text']) in self.rojas or norm(w['raw']) in self.rojas
                    c = '\\1c' + col(roja if es_roja else (tinta or TINTA))
                    partes.append(f'{"" if j == 0 else " "}{{\\k{dk}{c}}}{palabras[k]}')
                if fi < len(filas) - 1: partes.append('\\N')
            lines.append(f'Dialogue: 0,{ts(t0)},{ts(t1)},K,,0,0,0,,' + ''.join(partes))
        open(os.path.join(self.P, '_work', 'subs.ass'), 'w', encoding='utf-8-sig').write('\n'.join(lines) + '\n')
        print(f'subtítulos: {len(grupos)} grupos')

    # ------------------------------------------------------------------------------------------- audio
    def audio(self, out='_work/final_audio.wav'):
        wk = os.path.join(self.P, '_work'); voz = os.path.join(self.P, 'voice.wav'); dur = self.DUR
        ins = ['-i', voz]; fc = []; mixes = ['[0:a]']; k0 = 1
        if self.musica:
            lvl = os.path.join(wk, 'music_lvl.wav'); tv = self.WD[-1]['end'] + 0.02
            run(['ffmpeg', '-y', '-v', 'error', '-ss', str(self.ini_mus), '-stream_loop', '-1', '-i', self.musica, '-t', f'{dur:.3f}', '-af',
                 f"loudnorm=I=-14:TP=-1.5:LRA=7,afade=t=in:d=0.4,volume='if(gte(t,{tv:.2f}),2.3,1)':eval=frame,afade=t=out:st={dur - 0.17:.3f}:d=0.15",
                 '-ar', '48000', '-ac', '2', lvl])
            ins += ['-i', lvl]
            fc += [f'[1:a]volume={self.vol}[m]', '[0:a]asplit=2[v1][vsc]',
                   '[m][vsc]sidechaincompress=threshold=0.10:ratio=3:attack=15:release=320:makeup=1[duck]']
            mixes = ['[v1]', '[duck]']; k0 = 2
        for k, (t, fn, g) in enumerate(sorted(self.sfx)):
            ins += ['-i', os.path.join(SFX, fn)]; ms = max(0, int(round(t * 1000)))
            fc.append(f'[{k + k0}:a]volume={g},adelay={ms}|{ms}[s{k}]'); mixes.append(f'[s{k}]')
        fc.append(f'{"".join(mixes)}amix=inputs={len(mixes)}:duration=first:normalize=0,atrim=0:{dur:.3f}[mx]')
        fc.append('[mx]loudnorm=I=-14:TP=-1.5:LRA=11[out]')
        script = os.path.join(wk, 'fc_audio.txt'); open(script, 'w', encoding='utf-8').write(';\n'.join(fc))
        run(['ffmpeg', '-y', '-v', 'error', *ins, '-/filter_complex', script, '-map', '[out]', '-ar', '48000', '-ac', '2', os.path.join(self.P, out)])
        print(f'audio: voz + {"música" if self.musica else "sin música"} + {len(self.sfx)} efectos')

    # ------------------------------------------------------------------------------------------- composición
    def presentador(self):
        """presentador chico abajo a la derecha (escala ~0.42, cabeza en x≈826), con el torso tocando el borde."""
        F = json.load(open(os.path.join(self.P, 'face.json')))
        tr = [x for x in F['track'] if x.get('ok') and 150 <= x['w'] <= 620] or [x for x in F['track'] if x.get('ok')]
        mx = statistics.median([x['x'] + x['w'] / 2 for x in tr]); my = statistics.median([x['y'] + x['h'] / 2 for x in tr]); mw = statistics.median([x['w'] for x in tr])
        b = [x for x in tr if abs(x['x'] + x['w'] / 2 - mx) < 0.7 * mw and abs(x['y'] + x['h'] / 2 - my) < 0.9 * mw and 0.55 * mw < x['w'] < 1.6 * mw]
        if len(b) >= 5: tr = b
        cx = statistics.median([x['x'] + x['w'] / 2 for x in tr]); ch = sorted(x['chin'] for x in tr); p90 = ch[int(len(ch) * 0.9)]
        top = float(json.load(open(os.path.join(self.P, 'silueta.json')))['top'])
        s = round(min(0.7, max(0.42, self.alto_cabeza / max(120.0, p90 - top))), 3)
        ww, hh = round(W * s), round(H * s)
        if ww % 2: ww += 1
        if hh % 2: hh += 1
        tx = round(self.cabeza[0] - s * cx); ty = H - hh
        cabeza_top = ty + s * top; crop = max(0, round(cabeza_top - 55 - ty))
        return dict(s=s, w=ww, h=hh, x=tx, y=ty, crop=crop, cabeza_top=round(cabeza_top))

    def borrador_ruta(self):
        return os.path.join(self.P, 'renders', f'{self.nombre}-{self.estilo}-borrador.mp4')

    def componer(self, raw, salida=None):
        raw = raw if os.path.isabs(raw) else os.path.join(self.P, raw)
        if not os.path.exists(raw): raise SystemExit(f'no está el fondo animado {raw}: rueda primero el estilo')
        salida = salida or self.borrador_ruta()
        p = self.presentador(); cut = os.path.join(self.P, 'cutout.webm')
        sub = f"subtitles='{_ff(os.path.join(self.P, '_work', 'subs.ass'))}'" + (f":fontsdir='{_ff(DIR_FUENTES)}'" if DIR_FUENTES else '')
        fc = (f'[1:v]scale={p["w"]}:{p["h"]}:flags=lanczos,format=yuva420p,crop={p["w"]}:{p["h"] - p["crop"]}:0:{p["crop"]}[d];'
              f'[0:v][d]overlay={p["x"]}:{p["y"] + p["crop"]}:format=auto:eof_action=repeat[v1];'
              f'[v1]{sub},format=yuv420p[v]')
        t = time.time()
        run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-c:v', 'libvpx-vp9', '-i', cut, '-i', os.path.join(self.P, '_work', 'final_audio.wav'),
             '-filter_complex', fc, '-map', '[v]', '-map', '2:a', '-t', f'{self.DUR:.3f}', '-r', str(FPS),
             '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', salida])
        print(f'borrador -> renders/{os.path.basename(salida)} ({time.time() - t:.0f}s) · presentador: escala {p["s"]}, cabeza arriba en y={p["cabeza_top"]}')
        return salida

    # ------------------------------------------------------------------------------------------- revisión y entregables
    def hojas(self, video=None, cada=1.0, cols=5, filas=2, ancho=324, sub='hojas'):
        """una foto por segundo (en t+0,5), 10 por hoja, para revisar ANTES de mostrar (SKILL.md §1f)."""
        video = video or self.borrador_ruta()
        d = os.path.join(self.P, sub); os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            if f.endswith('.jpg'): os.remove(os.path.join(d, f))
        alto = round(ancho * 16 / 9); n = cols * filas
        vf = (f"fps=1/{cada},scale={ancho}:{alto},drawtext=fontfile='{_ff(FUENTE_HOJAS)}':text='%{{eif\\:t*{cada}\\:d}}s':x=8:y=8:fontsize=26:"
              f"fontcolor=white:box=1:boxcolor=0x000000AA:boxborderw=6,tile={cols}x{filas}:padding=4:color=white")
        run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf', vf, '-q:v', '3', os.path.join(d, 'hoja_%02d.jpg')])
        hs = sorted(f for f in os.listdir(d) if f.endswith('.jpg'))
        print(f'hojas: {len(hs)} en {sub}/ ({n} s por hoja)')
        return [os.path.join(d, h) for h in hs]

    def liviana(self, video=None, salida=None):
        video = video or self.borrador_ruta()
        salida = salida or os.path.join(self.P, 'renders', f'{self.nombre}-{self.estilo}-VISTA.mp4')
        run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow', '-crf', '29',
             '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', salida])
        print(f'copia liviana -> renders/{os.path.basename(salida)} ({os.path.getsize(salida) / 1e6:.1f} MB)')
        return salida

    def lado_a_lado(self, video=None, salida=None, etiqueta_ref='REFERENCIA'):
        """el video de referencia (otra versión del mismo reel) a la izquierda y este a la derecha, mismo segundo."""
        if not self.referencia: return None
        video = video or self.borrador_ruta()
        salida = salida or os.path.join(self.P, 'renders', f'{self.nombre}-lado-a-lado.mp4')
        f = _ff(FUENTE_HOJAS)
        fc = ('[0:v]fps=30,scale=540:960:flags=lanczos,setsar=1[a];[1:v]fps=30,scale=540:960:flags=lanczos,setsar=1[b];[a][b]hstack=2,'
              f"pad=1080:1032:0:72:color=0x111113,drawtext=fontfile='{f}':text='{etiqueta_ref}':x=(540-tw)/2:y=20:fontsize=30:fontcolor=white,"
              f"drawtext=fontfile='{f}':text='{self.estilo.upper()}':x=540+(540-tw)/2:y=20:fontsize=30:fontcolor=0xFDE047[v]")
        run(['ffmpeg', '-y', '-v', 'error', '-i', self.referencia, '-i', video, '-filter_complex', fc, '-map', '[v]', '-map', '1:a',
             '-t', f'{self.DUR:.3f}', '-c:v', 'libx264', '-preset', 'medium', '-crf', '27', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k',
             '-movflags', '+faststart', salida])
        print(f'lado a lado -> renders/{os.path.basename(salida)} ({os.path.getsize(salida) / 1e6:.1f} MB)')
        return salida

    def entregar(self):
        """hojas de revisión + copia liviana (+ lado a lado si hay referencia). El borrador NO es el final."""
        self.hojas(); self.liviana(); self.lado_a_lado()
