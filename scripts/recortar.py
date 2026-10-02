# -*- coding: utf-8 -*-
"""
reel-motion · RECORTAR  — separa al presentador del fondo (video con transparencia).

    python recortar.py <carpeta_proyecto> [--escala 0.8] [--ratio 0.5]

    cut.mp4 (1080x1920)  ->  cutout.webm (VP9 con canal alfa, 864x1536)  +  _work/matte_check.jpg (MÍRALA antes de seguir)

Usa Robust Video Matting (red recurrente: el recorte no parpadea entre cuadros). Corre en la tarjeta gráfica si hay
(Windows: DirectML · Mac: CoreML · NVIDIA: CUDA) y si no, en el procesador. Un reel de 60 s tarda ~10 min con GPU.
El borde se limpia con: color de primer plano estimado (quita el halo del fondo) + filtro guiado + niveles.
"""
import sys, os, subprocess, json, time
import numpy as np, cv2, onnxruntime as ort

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(SKILL, 'modelos', 'rvm_resnet50_fp32.onnx')

def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

def sesion():
    if not os.path.exists(MODEL):
        alt = os.path.expanduser('~/.u2net/rvm/rvm_resnet50_fp32.onnx')
        if os.path.exists(alt): return _abrir(alt)
        raise SystemExit('Falta el modelo de recorte. Corre:  python scripts/instalar.py')
    return _abrir(MODEL)

def _abrir(path):
    disp = ort.get_available_providers()
    orden = [p for p in ('DmlExecutionProvider', 'CUDAExecutionProvider', 'CoreMLExecutionProvider') if p in disp] + ['CPUExecutionProvider']
    for i in range(len(orden)):
        try:
            so = ort.SessionOptions()
            if orden[i] == 'DmlExecutionProvider': so.enable_mem_pattern = False; so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            if orden[i] == 'CPUExecutionProvider': so.intra_op_num_threads = os.cpu_count() or 4
            s = ort.InferenceSession(path, sess_options=so, providers=[orden[i]] if orden[i] == 'CPUExecutionProvider' else [orden[i], 'CPUExecutionProvider'])
            # prueba con un cuadro negro: algunos aceleradores aceptan el modelo pero fallan al correrlo
            z = [np.zeros([1, 1, 1, 1], np.float32)] * 4
            s.run(None, {'src': np.zeros([1, 3, 1920, 1080], np.float32), 'r1i': z[0], 'r2i': z[1], 'r3i': z[2], 'r4i': z[3], 'downsample_ratio': np.array([0.5], np.float32)})
            print('recorte con:', orden[i].replace('ExecutionProvider', ''), flush=True)
            return s
        except Exception as e:
            print(f'  ({orden[i]} no sirvió aquí, pruebo el siguiente)', flush=True)
    raise SystemExit('No pude abrir el modelo de recorte con ningún acelerador ni con el procesador.')

def guiado(bgr, a):
    if hasattr(cv2, 'ximgproc'): return cv2.ximgproc.guidedFilter(bgr, a, 8, (0.02 * 255) ** 2)
    return a          # sin opencv-contrib: se salta el pulido del borde (queda un poco más blando)

def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith('-'): raise SystemExit(__doc__)
    P = os.path.abspath(sys.argv[1])
    ESC = float(arg('--escala', '0.8')); RATIO = float(arg('--ratio', '0.5')); CRF = arg('--crf', '18')
    SRC = os.path.join(P, arg('--src', 'cut.mp4')); OUT = os.path.join(P, arg('--out', 'cutout.webm'))
    if not os.path.exists(SRC): raise SystemExit('Falta cut.mp4: corre primero preparar.py')
    pr = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate,nb_frames',
                                    '-of', 'json', SRC], capture_output=True, text=True).stdout)['streams'][0]
    W, H = pr['width'], pr['height']; num, den = pr['r_frame_rate'].split('/'); FPS = float(num) / float(den)
    total = int(pr.get('nb_frames') or 0)
    OW, OH = int(round(W * ESC / 2) * 2), int(round(H * ESC / 2) * 2)
    print(f'{os.path.basename(SRC)}: {W}x{H} @ {FPS:g} fps ({total} cuadros) -> {os.path.basename(OUT)} {OW}x{OH}', flush=True)
    sess = sesion()
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', SRC, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', f'{FPS:g}', '-i', '-',
                            '-vf', f'scale={OW}:{OH}:flags=lanczos', '-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p', '-b:v', '0', '-crf', CRF,
                            '-deadline', 'good', '-cpu-used', '3', '-row-mt', '1', '-threads', str(min(12, os.cpu_count() or 4)), '-g', '15',
                            '-auto-alt-ref', '0', '-an', OUT], stdin=subprocess.PIPE)
    rec = [np.zeros([1, 1, 1, 1], np.float32)] * 4; dr = np.array([RATIO], np.float32)
    n = 0; t0 = time.time(); checks = []; tops = []; nb = W * H * 3; paso = max(1, int(FPS * 6))
    while True:
        buf = dec.stdout.read(nb)
        if len(buf) < nb: break
        bgr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        src = (bgr[..., ::-1].astype(np.float32) / 255.0).transpose(2, 0, 1)[None]
        fgr, pha, *rec = sess.run(None, {'src': np.ascontiguousarray(src), 'r1i': rec[0], 'r2i': rec[1], 'r3i': rec[2], 'r4i': rec[3], 'downsample_ratio': dr})
        a = np.clip(pha[0, 0], 0, 1)
        a = np.clip((guiado(bgr, a) - 0.20) / 0.60, 0, 1)                 # el borde se pega al borde real y se quitan halos
        fg = np.clip(fgr[0].transpose(1, 2, 0)[..., ::-1], 0, 1)          # color del primer plano "limpio" (BGR 0..1)
        am = a[..., None]
        ext = np.clip(cv2.GaussianBlur(fg * am, (0, 0), 6) / (cv2.GaussianBlur(a, (0, 0), 6)[..., None] + 1e-4), 0, 1)
        col = np.where(am > 0.98, fg, fg * am + ext * (1 - am))           # el color del sujeto se extiende hacia afuera (no se cuela el fondo)
        enc.stdin.write(np.dstack([(col * 255 + 0.5).astype(np.uint8), (a * 255 + 0.5).astype(np.uint8)]).tobytes())
        if n % 5 == 0:                                                     # tope de la cabeza (para encuadrar la tarjeta)
            filas = np.where((a > 0.5).sum(axis=1) > 20)[0]
            if len(filas): tops.append(int(filas[0]))
        if n % paso == int(FPS * 2) % paso:
            chk = col * am + np.array([0.11, 0.13, 0.85], np.float32) * (1 - am)
            checks.append(cv2.resize((chk * 255).astype(np.uint8), (W // 4, H // 4), interpolation=cv2.INTER_AREA))
        n += 1
        if n % 150 == 0:
            v = n / (time.time() - t0); falta = (total - n) / v / 60 if total else 0
            print(f'  {n}/{total or "?"} cuadros · {v:.1f} por segundo' + (f' · faltan ~{falta:.0f} min' if total else ''), flush=True)
    enc.stdin.close(); enc.wait(); dec.wait()
    if enc.returncode: raise SystemExit('ffmpeg falló al guardar cutout.webm (¿tu ffmpeg trae libvpx-vp9?).')
    print(f'OK {n} cuadros en {(time.time() - t0) / 60:.1f} min -> {OUT}', flush=True)
    if tops and os.path.basename(SRC) == 'cut.mp4':
        top = float(np.median(tops)) * 1920.0 / H
        json.dump({'top': round(top, 1), 'top_p10': round(float(np.percentile(tops, 10)) * 1920.0 / H, 1)}, open(os.path.join(P, 'silueta.json'), 'w'))
        print(f'tope de la cabeza: y≈{top:.0f} px -> silueta.json', flush=True)
    if checks:
        cols = 6; rows = (len(checks) + cols - 1) // cols
        sheet = np.full((rows * (H // 4), cols * (W // 4), 3), 255, np.uint8)
        for i, c in enumerate(checks):
            y, x = (i // cols) * (H // 4), (i % cols) * (W // 4); sheet[y:y + c.shape[0], x:x + c.shape[1]] = c
        os.makedirs(os.path.join(P, '_work'), exist_ok=True)
        cv2.imwrite(os.path.join(P, '_work', 'matte_check.jpg'), sheet, [cv2.IMWRITE_JPEG_QUALITY, 88])
        print('hoja de revisión -> _work/matte_check.jpg  (mírala: el sujeto debe verse completo sobre rojo, sin pedazos del fondo)', flush=True)


if __name__ == '__main__':
    main()
