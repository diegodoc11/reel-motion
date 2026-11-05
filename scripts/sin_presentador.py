# -*- coding: utf-8 -*-
"""
reel-motion · SIN PRESENTADOR — prepara un proyecto para un video 100 % animado, sin grabarte.

    python sin_presentador.py <carpeta_proyecto> --texto guion.txt [--voz <voice_id>] [--velocidad 1.0] [--cola 2.0]
    python sin_presentador.py <carpeta_proyecto> --audio mi_voz.mp3 [--idioma es] [--cola 2.0]

--texto  : genera la voz en off con ElevenLabs (con el tiempo exacto de cada palabra). La llave se lee de la variable de
           entorno ELEVENLABS_API_KEY o de un archivo .env (en la carpeta del proyecto o en ~/.config/reel-motion/.env)
           con la línea  ELEVENLABS_API_KEY=sk_...   Nunca la pegues en el chat.
           --voz: el id de cualquier voz de tu biblioteca de ElevenLabs (por defecto una voz prediseñada que habla español
           con el modelo multilingüe). --velocidad 0.9-1.2 (1.1 suena más ágil para redes).
--audio  : usa tu propia voz grabada (o de otra herramienta) y saca los tiempos con whisper (como preparar.py).
--cola   : segundos que el video sigue después de la última palabra (para el botón del cierre). Por defecto 2.

Deja en el proyecto lo mismo que preparar.py + recortar.py, pero sin persona: words.json, cutmap.json, face.json de
relleno, cut.mp4 negro, cutout.webm transparente, _work/voice_raw.wav (voz + cola), style.css, minis.py y la ruta de la
skill. Siguiente paso: copia plantilla/build_sin_presentador.py a <proyecto>/build.py y cambia las escenas (SKILL.md §1d).
"""
import base64, json, os, shutil, subprocess, sys, urllib.error, urllib.request
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOZ_POR_DEFECTO = 'EXAVITQu4vr4xnSDxMaL'          # "Sarah": voz prediseñada de ElevenLabs (habla español con eleven_multilingual_v2)


def arg(nombre, defecto=None):
    return sys.argv[sys.argv.index(nombre) + 1] if nombre in sys.argv else defecto


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: raise SystemExit('ERROR al correr: ' + ' '.join(map(str, cmd[:6])) + ' …\n' + (r.stderr or r.stdout)[-1500:])


def llave(P):
    k = os.environ.get('ELEVENLABS_API_KEY', '').strip()
    if k: return k
    for env in (os.path.join(P, '.env'), os.path.expanduser('~/.config/reel-motion/.env')):
        if os.path.isfile(env):
            for linea in open(env, encoding='utf-8'):
                if linea.strip().startswith('ELEVENLABS_API_KEY='):
                    return linea.split('=', 1)[1].strip().strip('"').strip("'")
    raise SystemExit('Falta la llave de ElevenLabs. Crea el archivo ~/.config/reel-motion/.env con la línea\n'
                     '    ELEVENLABS_API_KEY=sk_...\n(o la variable de entorno ELEVENLABS_API_KEY). Nunca la pegues en el chat.')


def voz_elevenlabs(P, texto, voz, velocidad):
    """texto -> _work/vo.mp3 + palabras con su tiempo (de los tiempos por letra que devuelve ElevenLabs)."""
    body = {'text': texto, 'model_id': 'eleven_multilingual_v2',
            'voice_settings': {'stability': 0.4, 'similarity_boost': 0.85, 'style': 0.35, 'use_speaker_boost': True, 'speed': velocidad}}
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{voz}/with-timestamps?output_format=mp3_44100_128',
                                 data=json.dumps(body).encode('utf-8'), headers={'xi-api-key': llave(P), 'Content-Type': 'application/json'})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=240))
    except urllib.error.HTTPError as e:
        raise SystemExit(f'ElevenLabs respondió {e.code}: ' + e.read()[:400].decode('utf-8', 'replace') +
                         '\n(401 = llave mala · 402/403 = sin créditos o la voz no está en tu plan · 404 = id de voz que no existe)')
    open(os.path.join(P, '_work', 'vo.mp3'), 'wb').write(base64.b64decode(d['audio_base64']))
    a = d['alignment']; json.dump(a, open(os.path.join(P, '_work', 'vo_align.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    ws, cur = [], None
    for c, s, e in zip(a['characters'], a['character_start_times_seconds'], a['character_end_times_seconds']):
        if c.isspace():
            if cur: ws.append(cur); cur = None
            continue
        if cur is None: cur = {'text': c, 'start': round(s, 3), 'end': round(e, 3)}
        else: cur['text'] += c; cur['end'] = round(e, 3)
    if cur: ws.append(cur)
    return ws, os.path.join(P, '_work', 'vo.mp3')


def voz_grabada(P, audio, idioma):
    """audio propio -> palabras con su tiempo (whisper, igual que preparar.py)."""
    sys.path.insert(0, os.path.join(SKILL, 'scripts'))
    from preparar import whisper_palabras
    a16 = os.path.join(P, '_work', 'vo16.wav')
    run(['ffmpeg', '-y', '-v', 'error', '-i', audio, '-ac', '1', '-ar', '16000', a16])
    ws = whisper_palabras(a16, os.path.join(P, '_work', 'wvoz'), arg('--modelo', 'large-v3'), idioma)
    return [{'text': w['text'], 'start': w['start'], 'end': w['end']} for w in ws], audio


def main():
    if len(sys.argv) < 3 or sys.argv[1].startswith('-'): print(__doc__); sys.exit(1)
    P = os.path.abspath(sys.argv[1]); os.makedirs(os.path.join(P, '_work'), exist_ok=True)
    cola = float(arg('--cola', 2.0))
    if arg('--texto'):
        t = arg('--texto'); texto = open(t, encoding='utf-8').read().strip() if os.path.isfile(t) else t
        ws, audio = voz_elevenlabs(P, texto, arg('--voz', VOZ_POR_DEFECTO), float(arg('--velocidad', 1.0)))
    elif arg('--audio'):
        ws, audio = voz_grabada(P, os.path.abspath(arg('--audio')), arg('--idioma', 'es'))
    else:
        raise SystemExit('Falta --texto guion.txt (voz con ElevenLabs) o --audio mi_voz.mp3 (voz propia). Mira: python sin_presentador.py')
    if not ws: raise SystemExit('No salieron palabras: revisa el texto o el audio.')
    json.dump(ws, open(os.path.join(P, 'words.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    DUR = round(ws[-1]['end'] + cola, 3)
    json.dump({'keep': [[0, DUR]], 'dur': DUR, 'sin_presentador': True}, open(os.path.join(P, 'cutmap.json'), 'w'), indent=0)
    # cara de relleno: el motor necesita una "cara" para calcular encuadres; aquí no se usa (la cámara va oculta)
    json.dump({'W': 1080, 'H': 1920, 'step': 1, 'track': [{'t': float(k), 'ok': True, 'x': 390, 'y': 520, 'w': 300, 'h': 360, 'chin': 900}
                                                          for k in range(int(DUR) + 1)]}, open(os.path.join(P, 'face.json'), 'w'), indent=0)
    run(['ffmpeg', '-y', '-v', 'error', '-i', audio, '-af', f'apad=whole_dur={DUR}', '-t', str(DUR), '-ar', '48000', '-ac', '1',
         os.path.join(P, '_work', 'voice_raw.wav')])
    run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', f'color=c=black:s=1080x1920:r=30:d={DUR}', '-c:v', 'libx264', '-preset', 'veryfast',
         '-crf', '35', '-pix_fmt', 'yuv420p', os.path.join(P, 'cut.mp4')])
    run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', f'color=c=0x00000000:s=270x480:r=30:d={DUR},format=yuva420p', '-c:v', 'libvpx-vp9',
         '-pix_fmt', 'yuva420p', '-b:v', '30k', '-auto-alt-ref', '0', os.path.join(P, 'cutout.webm')])
    open(os.path.join(P, '_work', 'skill.txt'), 'w', encoding='utf-8').write(SKILL.replace('\\', '/'))
    for fn in ('style.css', 'minis.py'):
        if not os.path.exists(os.path.join(P, fn)): shutil.copy(os.path.join(SKILL, 'plantilla', fn), os.path.join(P, fn))
    print(f'\nLISTO  {P}\n  duración {DUR} s ({len(ws)} palabras + {cola} s de cierre) · cut.mp4 negro · cutout.webm vacío · sin cara que esquivar\n')
    print('GUION con tiempos (segundo · palabras):')
    for i in range(0, len(ws), 8): print(f"  {ws[i]['start']:6.2f}  " + ' '.join(w['text'] for w in ws[i:i + 8]))
    print('\nSiguiente: copia plantilla/build_sin_presentador.py a build.py, cambia las escenas y corre build.py (SKILL.md §1d).')


if __name__ == '__main__':
    main()
