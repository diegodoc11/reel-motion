# -*- coding: utf-8 -*-
"""Reemplazo mínimo del módulo pizarra (el estilo HyperFrames): solo lo que plantilla/dibujos.py necesita (L, F, C y colores).
Así los dibujos de la pizarra se reutilizan en HandDraw sin tocar la skill reel-motion."""
ROJO = '#E5322D'; BLANCO = '#F4F4F2'; GRIS = '#4C4D54'; MU = '#8E9099'


def L(d, w=6, color=BLANCO, extra=''):
    return f'<path class="ln" d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{extra}/>'


def F(d, color=BLANCO, op=1.0, extra=''):
    return f'<path class="rel" d="{d}" fill="{color}" opacity="{op}"{extra}/>'


def C(cx, cy, r):
    return f'M{cx - r},{cy} a{r},{r} 0 1,0 {2 * r},0 a{r},{r} 0 1,0 {-2 * r},0'
