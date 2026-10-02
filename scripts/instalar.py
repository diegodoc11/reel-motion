# -*- coding: utf-8 -*-
"""
reel-motion · INSTALAR  (se corre UNA sola vez; se puede repetir sin problema)

    python instalar.py [--modelo-whisper large-v3 | medium] [--sin-whisper]

  1. crea un entorno de Python propio dentro de la skill (.venv) con lo necesario (numpy, pillow, opencv, onnxruntime)
  2. descarga el modelo de recorte de personas (Robust Video Matting, 103 MB)
  3. revisa que estén: ffmpeg, Node.js (npx), whisper.cpp (whisper-cli / whisper-server), deja listo HyperFrames
     y descarga el modelo de whisper si falta (3 GB)
Al final imprime la ruta del Python que debes usar para los demás scripts.
"""
import sys, os, shutil, subprocess, urllib.request, platform

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIN = platform.system() == 'Windows'; MAC = platform.system() == 'Darwin'
VENV = os.path.join(SKILL, '.venv')
PY = os.path.join(VENV, 'Scripts', 'python.exe') if WIN else os.path.join(VENV, 'bin', 'python')
RVM_URL = 'https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_resnet50_fp32.onnx'
WH_URL = 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-{m}.bin'
como = lambda win, mac, lin: win if WIN else (mac if MAC else lin)
ok, falta = [], []

def bajar(url, destino, nombre):
    os.makedirs(os.path.dirname(destino), exist_ok=True); tmp = destino + '.parte'
    print(f'  descargando {nombre}…', flush=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'reel-motion'})) as r, open(tmp, 'wb') as f:
        total = int(r.headers.get('Content-Length') or 0); leido = 0; marca = 0
        while True:
            b = r.read(1 << 20)
            if not b: break
            f.write(b); leido += len(b)
            if total and leido * 10 // total > marca: marca = leido * 10 // total; print(f'    {marca * 10}%', flush=True)
    os.replace(tmp, destino)

def main():
    print('reel-motion · instalación en', SKILL)
    if sys.version_info < (3, 10): raise SystemExit('Necesitas Python 3.10 o más nuevo.')

    # 1) entorno de Python
    if not os.path.exists(PY):
        print('creando entorno de Python (.venv)…', flush=True)
        subprocess.run([sys.executable, '-m', 'venv', VENV], check=True)
    print('instalando librerías (puede tardar unos minutos la primera vez)…', flush=True)
    r = subprocess.run([PY, '-m', 'pip', 'install', '--quiet', '--disable-pip-version-check', '-r', os.path.join(SKILL, 'requirements.txt')])
    (ok if r.returncode == 0 else falta).append('librerías de Python' + ('' if r.returncode == 0 else ' (pip falló: revisa tu conexión y vuelve a correr)'))

    # 2) modelo de recorte
    rvm = os.path.join(SKILL, 'modelos', 'rvm_resnet50_fp32.onnx')
    if not os.path.exists(rvm):
        try: bajar(RVM_URL, rvm, 'modelo de recorte (103 MB)')
        except Exception as e: falta.append(f'modelo de recorte ({e}). Descárgalo a mano de {RVM_URL} y ponlo en {rvm}')
    if os.path.exists(rvm): ok.append('modelo de recorte')

    # 3) programas
    for exe, nombre, ayuda in (('ffmpeg', 'ffmpeg', como('scoop install ffmpeg', 'brew install ffmpeg', 'sudo apt install ffmpeg')),
                               ('npx', 'Node.js 20+ (npx)', como('scoop install nodejs-lts', 'brew install node', 'https://nodejs.org')),
                               ('whisper-cli', 'whisper.cpp (whisper-cli)', como('scoop install whisper-cpp', 'brew install whisper-cpp', 'https://github.com/ggml-org/whisper.cpp')),
                               ('whisper-server', 'whisper.cpp (whisper-server)', como('scoop install whisper-cpp', 'brew install whisper-cpp', 'https://github.com/ggml-org/whisper.cpp'))):
        if shutil.which(exe) or (WIN and shutil.which(exe + '.cmd')): ok.append(nombre)
        else: falta.append(f'{nombre}  ->  instálalo con:  {ayuda}')

    # 3b) HyperFrames (el que renderiza): se baja solo con npx la primera vez, junto con su navegador
    if shutil.which('npx') or (WIN and shutil.which('npx.cmd')):
        print('preparando HyperFrames (la primera vez descarga el paquete y su navegador)…', flush=True)
        try:
            v = subprocess.run('npx --yes hyperframes --version', shell=True, capture_output=True, text=True, timeout=600)
            nav = subprocess.run('npx --yes hyperframes browser ensure', shell=True, capture_output=True, text=True, timeout=900)
            if v.returncode == 0 and nav.returncode == 0: ok.append('HyperFrames ' + (v.stdout.strip().splitlines() or ['?'])[-1])
            else: falta.append('HyperFrames no quedó listo. Corre a mano:  npx --yes hyperframes browser ensure')
        except Exception as e:
            falta.append(f'HyperFrames ({e}). Corre a mano:  npx --yes hyperframes browser ensure')

    # 4) modelo de whisper
    if '--sin-whisper' not in sys.argv:
        m = sys.argv[sys.argv.index('--modelo-whisper') + 1] if '--modelo-whisper' in sys.argv else 'large-v3'
        cands = [os.path.join(SKILL, 'modelos', f'ggml-{m}.bin'), os.path.expanduser(f'~/.cache/hyperframes/whisper/models/ggml-{m}.bin')]
        if not any(os.path.exists(c) for c in cands):
            try: bajar(WH_URL.format(m=m), cands[0], f'modelo de whisper {m} (~{"3 GB" if "large" in m else "1.5 GB"})')
            except Exception as e: falta.append(f'modelo de whisper ({e}). Descárgalo de {WH_URL.format(m=m)} a {cands[0]}')
        if any(os.path.exists(c) for c in cands): ok.append(f'modelo de whisper {m}')

    # 5) acelerador para el recorte
    try:
        prov = subprocess.run([PY, '-c', 'import onnxruntime as o; print(",".join(o.get_available_providers()))'], capture_output=True, text=True).stdout.strip()
        gpu = [p.replace('ExecutionProvider', '') for p in prov.split(',') if p not in ('CPUExecutionProvider', 'AzureExecutionProvider') and p]
        ok.append('recorte acelerado con ' + '/'.join(gpu) if gpu else 'recorte por procesador (más lento, funciona igual)')
    except Exception: pass

    print('\n=========== RESULTADO ===========')
    for x in ok: print('  [ok]    ', x)
    for x in falta: print('  [FALTA] ', x)
    print('\nPython para los scripts de la skill:\n  ' + PY)
    print('\nListo para usar.' if not falta else '\nArregla lo que dice FALTA y vuelve a correr este instalador.')
    sys.exit(1 if falta else 0)


if __name__ == '__main__':
    main()
