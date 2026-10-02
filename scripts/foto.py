# -*- coding: utf-8 -*-
"""
reel-motion · FOTO  — prepara una foto del presentador para las polaroids del reel.

    python foto.py <imagen> <carpeta_proyecto> <nombre> [x0,y0,x1,y1]

    -> <proyecto>/assets/foto-<nombre>.jpg (600x620). El recorte opcional va en FRACCIONES de la foto (0 a 1):
       0,0.1,1,0.8 = todo el ancho, del 10 % al 80 % del alto. Sin recorte: se centra sola.
El build usa todas las assets/foto-*.jpg (hasta 4) en la receta "abanico de fotos".
"""
import sys, os
from PIL import Image, ImageOps

def main():
    if len(sys.argv) < 4: raise SystemExit(__doc__)
    src, P, nombre = sys.argv[1], os.path.abspath(sys.argv[2]), sys.argv[3]
    im = ImageOps.exif_transpose(Image.open(src)).convert('RGB'); w, h = im.size
    if len(sys.argv) > 4:
        x0, y0, x1, y1 = [float(v) for v in sys.argv[4].split(',')]
        im = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
    im = ImageOps.fit(im, (600, 620), Image.LANCZOS, centering=(0.5, 0.4))
    os.makedirs(os.path.join(P, 'assets'), exist_ok=True)
    out = os.path.join(P, 'assets', f'foto-{nombre}.jpg'); im.save(out, quality=92); print(out)


if __name__ == '__main__':
    main()
