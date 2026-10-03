---
name: reel-motion
description: >-
  Convierte un video VERTICAL de una persona hablando a cámara en un reel de MOTION GRAPHICS hecho 100 % con
  código: RECORTA al presentador del fondo y lo monta sobre una tarjeta de color, con titulares que aparecen
  palabra por palabra, terminales, papel rasgado, collage, contadores, polaroids, mascota, subtítulos, música y
  efectos, todo sincronizado con lo que dice (HyperFrames + GSAP). Úsala cuando pidan "anima este video",
  "edítalo con animaciones / motion graphics", "ponme recortado sobre un fondo de color", "hazlo como el reel de
  las animaciones hechas con código", "estilo animador", o invoquen /reel-motion. NO es para dejar el video
  real a pantalla completa con zooms, b-roll y subtítulos (eso es video-ad-editing), NI para crear un video
  animado SIN presentador a partir de un guion (eso es anuncios-animados o video-explainer).
---

# reel-motion — el presentador recortado dentro de un diseño animado

**Qué entrega:** un MP4 vertical 1080×1920 donde TODO lo que se ve alrededor del presentador es diseño animado
hecho con código (HTML + GSAP renderizado con HyperFrames). El presentador se separa de su fondo real (video con
transparencia) y vive en una tarjeta de color; cada titular, ficha, número o dibujo entra en el instante exacto en
que se dice la palabra.

**Cuál skill de video usar** (no confundirlas):

| Skill | El presentador | Úsala cuando |
|---|---|---|
| **reel-motion** (esta) | Grabado y **recortado** dentro de un diseño | "anímalo", "motion graphics", "recortado sobre color" |
| video-ad-editing | Grabado, **a pantalla completa** con su fondo real | "edítame este video": zooms, b-roll, subtítulos, badges |
| anuncios-animados / video-explainer | **No hay** presentador grabado | parten de un guion o un tema: voz IA + ilustraciones |
| hyperframes (oficial) | — | el motor que renderiza; dudas de bajo nivel de composición o CLI |

**Entrada que necesita:** un video vertical (9:16) de UNA persona hablando a cámara, cara de frente. Sirve grabado
con celular. Mejor resultado: fondo sencillo, buena luz, encuadre de cabeza y pecho (la barbilla hacia la mitad
del cuadro). Videos horizontales o sin cara: esta skill no aplica; dilo y propón otra.

Rutas en este documento: `SKILL` = la carpeta de esta skill (donde está este archivo). `PY` = el Python propio de
la skill (lo crea el instalador). `P` = la carpeta del proyecto del reel.

---

## 0. Instalación (una sola vez por computador)

```bash
python "SKILL/scripts/instalar.py"
```

(`--verificar` solo revisa, sin crear ni descargar nada.) Crea `SKILL/.venv`, instala las librerías, descarga el modelo
de recorte (103 MB, a `SKILL/modelos/`) y el de transcripción (3 GB, a `SKILL/modelos/` o reutiliza el de
`~/.cache/hyperframes/whisper/models/`) y
revisa que existan `ffmpeg`, `npx` (Node 20+) y `whisper-cli` / `whisper-server` (whisper.cpp), y deja listo
HyperFrames con su navegador. Si algo dice
`[FALTA]`, instálalo tú con el comando que el propio instalador imprime (Windows: `scoop install ffmpeg
whisper-cpp nodejs-lts` · Mac: `brew install ffmpeg whisper-cpp node`) y vuelve a correrlo hasta que diga
"Listo para usar". Opciones: `--modelo-whisper medium` (1.5 GB, para computadores lentos).

Desde ahí usa SIEMPRE el Python de la skill:

- Windows: `PY = "SKILL/.venv/Scripts/python.exe" -X utf8` (con `/` también funciona en Git Bash y PowerShell)
- Mac / Linux: `PY = "SKILL/.venv/bin/python"`

Rutas con espacios SIEMPRE entre comillas. Si `SKILL/.venv` no existe, corre el instalador antes de cualquier
otra cosa (no instales librerías en el Python global).

## 1. Qué preguntarle al usuario (una sola ronda, solo lo que falte)

1. **El video** (ruta). Si pasa varios, uno por proyecto.
2. **Llamado a la acción**: normalmente el video ya lo dice ("comenta VIDEO"); solo pregunta si no hay ninguno.
3. **Color de marca** (por defecto rojo `#D11F1D`) → `colores={'acento': '#...'}`.
4. **Música**: la skill NO trae música (derechos de autor). Usa la pista que el usuario indique o la primera que
   haya en `SKILL/recursos/musica/` (`musica='auto'`). Sin pista, el reel sale con voz y efectos y se avisa.
5. **Fotos propias**, solo si el guion las menciona ("mis fotos", "mis resultados"): muéstrale opciones y que elija.

No preguntes nada técnico. Encuadres, piezas, tiempos y fuentes los decides tú.

## 2. Flujo de trabajo

Todos los comandos se corren tal cual; los pasos 2.1 y 2.3 tardan (minutos): córrelos en segundo plano y avisa.

### 2.1 Preparar el proyecto

```bash
PY "SKILL/scripts/preparar.py" "<video>" "<P>"        # P = <carpeta de trabajo>/reels/<nombre-corto>
```

Deja en `P`: `source.mp4`, `cut.mp4` (1080×1920, 30 fps, sin silencios largos; HDR de iPhone convertido a SDR),
`words.json` (cada palabra con su segundo exacto), `face.json` (dónde está la cara), `cutmap.json`, `style.css`,
`minis.py`, y al final imprime el **guion con tiempos**. Opciones: `--idioma en|pt|…` (por defecto `es`),
`--modelo medium`, `--sin-silencios`. Tarda ~5-10 min por minuto de video.

Lee los avisos: si dice que la cara ocupa mucho cuadro, arma el reel solo con los encuadres `card` y `full`.
El guion impreso sale SIN corregir: anota ya los nombres que whisper oyó mal ("Cloud" → "Claude") para `correcciones=`.

### 2.2 Buscar equivocaciones (obligatorio)

```bash
PY "SKILL/scripts/frases.py" "<P>"
```

La transcripción normal ESCONDE las repeticiones (whisper las junta). Este script transcribe frase por frase el
crudo y las deja ver (~1 min por cada 30 s de video). Lee la lista completa:

- Todo se lee de corrido → no hay nada que cortar; sigue.
- Hay un arranque en falso o una frase repetida ("Ask… ¿Cómo se…? Ask Claude Council") → quita la toma MALA y deja
  la buena: escribe `P/_work/cortes.json` = `[[inicio, fin], …]` en segundos del CRUDO (desde el inicio de la
  frase mala hasta el inicio de la buena) y vuelve a correr `preparar.py` (reusa lo que ya transcribió). Luego
  relee el guion impreso y confirma que la frase quedó una sola vez y completa.

**Cuidado con los falsos positivos:** un tramo muy corto (menos de 1 s) o un nombre en otro idioma sale mal
transcrito al aislarlo ("Ask" → "As…", "Claude Council" → "¿Cómo se…?"). Eso NO es una equivocación. Solo corta
cuando la MISMA frase aparece dos veces o queda claramente a medias, y compara siempre con el guion completo que
imprimió `preparar.py`. Después de cortar, si falta una palabra que antes estaba: el corte estuvo mal; bórralo.

Recorta al presentador SOLO cuando los cortes ya sean definitivos (si cambian, hay que recortar de nuevo).

### 2.3 Recortar al presentador

```bash
PY "SKILL/scripts/recortar.py" "<P>"
```

Genera `cutout.webm` (el presentador con transparencia) y `silueta.json`. Usa la tarjeta gráfica si hay; tarda
~10 min por minuto de video con GPU (bastante más sin ella). **Abre y mira `P/_work/matte_check.jpg`**: el presentador
debe verse completo sobre rojo, sin pedazos del fondo ni huecos. Si se cuelan objetos del fondo o faltan manos:
`--ratio 0.4` o `--ratio 0.6` y compara.

### 2.4 Plan de escenas (antes de escribir código)

Parte el guion en **escenas de 2 a 6 segundos, una idea por escena**, y escribe la tabla en `P/_work/plan.md`:

| # | Frase (palabras exactas de words.json) | Encuadre | Pieza | Qué se ve y cuándo entra cada cosa |
|---|---|---|---|---|

Cómo elegir (ver §3 y §5): el gancho siempre con titular desde el segundo 0; `card` es la base; cambia de
encuadre cada 2-3 escenas; no repitas la misma pieza dos veces seguidas; los números van gigantes; las listas
aparecen ítem por ítem; el cierre es el CTA con la palabra clave.

### 2.5 Construir

Copia una plantilla a `P/build.py`:

- `SKILL/plantilla/build_minimo.py` → punto de partida recomendado: un reel completo solo con el encuadre `card`
  y 5 piezas (`gancho`, `cabecera`, `lista`, `numero`, `cta`). Cambias el bloque ESCENAS y ya funciona.
- `SKILL/plantilla/build.py` → el reel de referencia completo (59 s, 9 escenas, los 3 encuadres y todas las
  recetas). Copia de ahí las recetas que necesites (§5); no lo uses entero para otro guion.

```bash
cd "<P>"                   # los comandos de build, lint, snapshot y render se corren DENTRO de la carpeta del proyecto
PY build.py --guion        # palabras con sus tiempos, YA con las correcciones aplicadas (f() busca el texto corregido); no necesita el recorte
PY build.py                # arma index.html + mezcla el audio (final_audio.wav)
PY build.py --no-audio     # igual pero sin remezclar (rápido, para iterar lo visual)
```

Regla de oro: **ningún tiempo se escribe a mano.** Todo sale de `f('palabra o frase')` = segundo en que se dice.

### 2.6 Revisar ANTES de mostrar (obligatorio)

```bash
npx hyperframes lint .                                                        # debe dar 0 errores
npx hyperframes snapshot . --at 1.2,4.8,9.5 --no-end --timeout 60000 -o snaps   # un segundo por escena
```

(El aviso `composition_file_too_large` es normal.) Elige para cada escena un segundo ~0.5 s después de que entró
su último elemento, abre `snaps/contact-sheet*.jpg` (una hoja por cada 9 cuadros) y **míralas**. Mira también +0.2 s y
+0.45 s después de cada `ir_a()` (ahí es donde se montan las cosas). Lista de control:

- [ ] Nada tapa la cara ni la boca (ni piezas ni subtítulos).
- [ ] Todo el texto cabe: nada cortado por el borde derecho ni montado sobre otra cosa.
- [ ] Cada escena tiene su pieza visible (no hay escenas "vacías" solo con la tarjeta).
- [ ] Los subtítulos no chocan con ninguna pieza.
- [ ] Ortografía y tildes; nombres propios bien escritos (`correcciones=`).

Corrige y repite hasta que pase. No muestres nada sin haber mirado tú las capturas.

### 2.7 Borrador para aprobación

```bash
npx hyperframes render . --fps 30 --quality draft --sdr --output renders/borrador.mp4
PY "SKILL/scripts/hoja.py" renders/borrador.mp4 _work/rev.jpg 0 <duración> 0.5 12 160
```

(`hoja.py <video> <salida> inicio fin paso columnas ancho_de_celda`; para más de 30 s haz dos hojas, p. ej. 0-20 y 20-40,
para que el texto se lea.) Mira `_work/rev.jpg` (un cuadro cada 0.5 s con su segundo): ¿cada cosa entra cuando se
dice?, ¿hay saltos raros? El render del borrador tarda ~6 min por minuto de video y necesita internet la primera vez
(HyperFrames descarga GSAP).
Entrégale el borrador al usuario y ajusta lo que pida. Para ver en vivo sin renderizar: `npx hyperframes preview`.
**No exportes el final sin que el usuario apruebe el borrador.**

### 2.8 Final

```bash
npx hyperframes render . --fps 60 --quality high --crf 16 --sdr --output renders/<nombre>-FINAL.mp4
```

Verifica antes de decir "listo": `ffprobe` (1080×1920, 60 fps, con audio, duración = la del borrador) y una hoja
con `hoja.py` del final. Extras útiles:

```bash
# copia liviana para subir a redes (~40 MB por minuto; Instagram y TikTok recomprimen menos)
ffmpeg -y -i renders/<nombre>-FINAL.mp4 -c:v libx264 -preset slow -b:v 5500k -maxrate 7500k -bufsize 11000k -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart renders/<nombre>-REDES.mp4
# portada: captura del gancho con el titular completo y los ojos abiertos
npx hyperframes snapshot . --at <segundo> --no-end --timeout 60000 -o _work/portada
```

Si el usuario pide además el texto de la publicación: gancho en la primera línea, 3-4 viñetas, llamado a la
acción con la palabra clave, firma y 4-6 hashtags, en su voz (directa, sin frases de relleno).

---

## 3. El lienzo (1080×1920) y los 3 encuadres

La interfaz de Instagram/TikTok tapa arriba (0-250), abajo (1650-1920) y la columna derecha de botones
(x > 940 entre y 1000 y 1650). Nada importante ahí.

| Encuadre | Qué se ve | Dónde van los gráficos |
|---|---|---|
| `card` (base) | Presentador **recortado** sobre una tarjeta de color (x 162-918, desde y 759 hasta abajo) | **Zona de titulares: x 78-1002, y 262-740**, dentro de un `<div class="hd">` |
| `full` | La toma real a pantalla completa | Tarjeta flotante que empieza en `bajo_barbilla(t0, t1)` (alto máx. ≈ 330 px) · collage ALREDEDOR de la cara (`zona_cara` + `esquivar_cara`) |
| `split` | Panel de papel arriba (0-780) + la toma real debajo | Dentro del papel: x 74-1006, y 200-722 (el "piso" está en `GROUND`) |

- Se cambia con `ir_a('card' | 'full' | 'split', t)`; para `split` se pasa el panel: `ir_a('split', t, papel='#pp1')`.
- La cámara se **ajusta sola** a cómo se grabó cada persona (más cerca, más lejos, corrida a un lado): `iniciar()`
  calcula la posición de la tarjeta y la línea de subtítulos (`CAP_Y`, ≈1530). No toques esos números a mano.
- **Subtítulos**: una sola línea en `CAP_Y`, igual en todo el video. El gancho no lleva subtítulos (el titular ya
  es el texto): `subtitulos(desde=t_fin_del_gancho)`.
- **Nunca nada sobre la cara.** En `full` y `split` verifica con las capturas.

## 4. El motor (`SKILL/scripts/motor.py`)

Encabezado fijo de todo `build.py` (el orden importa: `iniciar()` va ANTES del `from motor import *`):

```python
import sys, os
P = os.path.dirname(os.path.abspath(__file__))
_sk = os.path.join(P, '_work', 'skill.txt')                                            # lo escribe preparar.py
SKILL = open(_sk, encoding='utf-8').read().strip() if os.path.exists(_sk) else os.path.expanduser('~/.claude/skills/reel-motion')
sys.path.insert(0, os.path.join(SKILL, 'scripts')); sys.path.insert(0, P)
import motor
motor.iniciar(P, correcciones={'cloud': 'Claude'}, colores={'acento': '#D11F1D'})
from motor import *
escenario('card')
# … escenas …
subtitulos(desde=t_fin_gancho, cambios=[('video', 'VIDEO', t_cta)])
cerrar(musica='auto', volumen_musica=0.28)
```

| Función | Para qué |
|---|---|
| `f('frase', despues=0)` / `fe('frase')` | segundo en que EMPIEZA / TERMINA la frase (palabras tal cual `words.json`; `despues` = buscar a partir de ese segundo) |
| `guion()` | imprime la transcripción con tiempos |
| `escenario(inicio='card', codigo_fondo='')` | fondos + cámara. Va una sola vez, antes de las escenas |
| `ir_a(encuadre, t, papel=None)` | cambia de encuadre en `t`; devuelve cuánto dura la transición |
| `bajo_barbilla(t0, t1)` | y donde puede empezar una tarjeta flotante en `full` |
| `zona_cara(t0, t1)` · `esquivar_cara(cx, cy, w, h, zona)` | rectángulo de la cabeza en `full` · corre una pieza que lo pise |
| `parts.append(html)` | agrega HTML al reel (cada elemento animado necesita `id` único) |
| `I(sel, **p)` | estado inicial · `S(sel, t, **p)` cambio instantáneo en `t` |
| `T(sel, t, dur, ease, **p)` | animar hacia `p` · `FT(sel, t, dur, desde, hasta, ease)` golpe repetible (saltos, destellos) |
| `win(sel, t0, t1)` | visible solo entre `t0` y `t1` |
| `pop(sel, t)` · `rise(sel, t)` · `leave(sel, t)` | entra con rebote · línea que sube tras su máscara (`.ln > .in`) · sale hacia arriba |
| `typed(id, texto, t, cps)` | máquina de escribir (devuelve el HTML) |
| `steps(id, valores, t0, t1)` | contador que cambia de valor (devuelve el HTML) |
| `handwrite(sel, t, pen=None)` · `serif(id, texto)` | texto que se "escribe" · titular serif con lápiz |
| `draw_x(sel, t)` + `X_SVG` | X dibujada a mano (tachar) |
| `mascot(id)` · `mood(id, t, 'n'|'h'|'w')` · `mascot_init(id)` | mascota y su cara (normal / feliz / preocupada) |
| `paper_svg(semilla)` | fondo del panel de papel para `split` |
| `fx(t, 'pop'|'whoosh'|'swipe'|'click'|'ding'|'thump', volumen)` | efecto de sonido |
| `flash(t)` | destello blanco de un cuadro |
| `gancho · cabecera · lista · numero · cta` | piezas listas para `card` (firmas abajo) |
| `subtitulos(desde, hasta, propios, cambios, huecos)` | subtítulos palabra por palabra |
| `capturas_provisionales(TH)` | miniaturas de escenas del propio reel (para polaroids) |
| `cerrar(musica, inicio_musica, volumen_musica, css_extra)` | mezcla audio + escribe `index.html`. Siempre al final |

**Las 5 piezas listas** (todas van en la zona de titulares del encuadre `card`; `t1=None` = se queda hasta el final; los
textos admiten HTML y entidades como `&iacute;`; el antetítulo se escribe a máquina):

| Pieza | Firma | Límites |
|---|---|---|
| `gancho(frase, hasta, saltos=(), acento=(), etiqueta='', marca='')` | palabras del inicio TAL CUAL `words.json`; `saltos` = índices tras los que hay salto de línea; `acento` = índices en color | 2-3 líneas de ≤ 18 letras |
| `cabecera(idp, t0, t1, lineas=[(texto, t, color)], antetitulo='', top=334)` | cada línea sube en su segundo; color `''`, `'red'` o `'blu'` | 1-3 líneas; ≤ 13 letras = grande, ≤ 19 = mediano, ≤ 24 = pequeño |
| `lista(idp, t0, t1, items=[(texto, t)], antetitulo='', top=350)` | fichas negras una por una | ≤ 4 ítems de ≤ 24 letras |
| `numero(idp, t0, t1, cifra, t_cifra, rotulos=[(texto, t)], antetitulo='')` | cifra gigante (`'3%'`, `'$0'`, `'<u>+</u>7'`) + rótulos a la derecha | cifra de 2-4 caracteres; ≤ 2 rótulos de ≤ 7 letras |
| `cta(idp, t0, palabra, t_palabra, apoyo='', t_apoyo=None, antetitulo='', verbo='Comenta', t_verbo=None)` | "Comenta" + caja roja con la PALABRA + línea de apoyo; se queda hasta el final | palabra ≤ 8 letras |

Las piezas avisan en consola si lo último que entra se ve menos de 0.45 s antes de salir: en ese caso deja el bloque
más tiempo (`t1` más tarde) o adelanta la entrada. Un `idp` es cualquier texto corto único (`'e3'`).
Para el patrón "deja X, usa Y" (comparaciones) usa la receta 1b del ejemplo completo (fichas tachadas) o `lista`
con `<s>…</s>` para tachar lo viejo y la última ficha en rojo.

Clases CSS listas (`plantilla/style.css`, se copia a `P/style.css` y ahí la puedes ampliar): `.hd` contenedor de
la zona de titulares · `.eb` antetítulo en mono (`.rd` rojo, `.dk` oscuro) · `.h1` titular gigante (≤13 letras),
`.h1.h1s` mediano (≤19), `.h2` (≤24) · `.ln > .in` línea con máscara para `rise` · `.red` `.blu` color ·
`.bchip` ficha negra · `.chip` etiqueta pequeña · `.term` terminal (`.tbar`, `.tb`, `.tl`, `.row`, `.tot`) ·
`.paper` panel de papel (`.ser` serif, `.hw` manuscrita, `.pol` polaroid, `.coin`, `.msc`) · `.qc` tarjeta
flotante · `.big7` número gigante · `.hbar` barra · `.grid` cuadrícula · `.vbox` caja del CTA · `.cap` subtítulos.

## 5. Recetas (están en `SKILL/plantilla/build.py`, numeradas igual)

| # | Receta | Encuadre | Úsala para |
|---|---|---|---|
| 1 | Gancho de estilos: el mismo titular en 5 estilos en 1.7 s | card | abrir mostrando "esto es diseño" |
| 1b | Iconos tachados → logo grande + titular | card | "no necesité X, Y, Z" |
| 2 | Terminal con filas y total | card | costos, pasos, comandos |
| 3 | Terminal flotante con cronómetro + collage de mini diseños | full | "en menos de N minutos", "todo esto" |
| 4 | Papel: titular serif escrito + palabras tachadas + polaroids + mascota + confeti | split | confesión, antes/después |
| 5 | Cambio de estilo en vivo (color, tipografía, fondo) + abanico de fotos | card | "puedes cambiar…", fotos propias |
| 6 | Papel con pila de monedas (objeción y respuesta) | split | "¿es caro?" |
| 7a-7e | Número gigante · barra de 24 h · titular 2 líneas · 0 %→N % con cuadrícula | card | datos y cifras |
| 8 | Tarjeta flotante con contador (cotización) | full | reto, comparación de precio |
| 9 | Oferta + CTA "Comenta PALABRA" con mascota | card | cierre |

`plantilla/minis.py` trae 16 mini diseños CSS (`M.zas()`, `M.vid()`, `M.ofe()`…) para collages y tarjetas, y los
iconos de herramientas (`M.TOOLS`). Fotos del usuario: `PY "SKILL/scripts/foto.py" <imagen> <P> <nombre>` →
`assets/foto-<nombre>.jpg`; la receta 5 usa hasta 4.

Crear una pieza nueva: HTML con posiciones absolutas dentro de `.hd` (card), `.paper` (split) o suelta con
`z-index` 25-30 (full) + `I()` para esconderla + `T()`/`pop()`/`rise()` en `f('palabra') - 0.03`. Mira cómo lo
hace la receta más parecida y copia su estructura.

## 6. Reglas de diseño (lo que hace que se vea profesional)

1. **Sincronía**: cada elemento entra cuando se DICE su palabra (`f('palabra') - 0.03`), no antes ni en bloque.
2. **Una idea por escena**, titulares de máximo 5 palabras. El texto en pantalla RESUME (palabra clave, cifra),
   no repite el subtítulo.
3. **Ritmo**: algo cambia cada 2-4 s. Lo anterior sale ~0.15 s antes de que entre lo nuevo (`leave`).
4. **Variedad**: alterna encuadres y piezas; al menos 3 cambios de encuadre cada 30 s en la versión completa.
5. **Color**: un acento + tinta + fondo claro. El segundo color solo para un golpe de énfasis.
6. **Sonido**: `pop` en entradas, `whoosh` en cambios de encuadre (lo pone `ir_a`), `ding` en la revelación,
   `thump` en cifras grandes. Volúmenes bajos (0.12-0.30). La música va por debajo de la voz (0.25-0.30).
7. **Listas una por una**, nunca todas de golpe.
8. **CTA**: la palabra clave en la caja grande y en MAYÚSCULAS también en el subtítulo (`cambios=`).

## 7. Reglas técnicas y errores comunes

- Animar SOLO `x`, `y`, `scale`, `rotation`, `opacity`, `clipPath`, `xPercent`, `yPercent`, `strokeDashoffset`.
  Nunca `top`/`left`/`width`/`height` (HyperFrames los rechaza). La posición base va en el `style`.
- Para centrar algo que se anima: `xPercent=-50` con `left:50%`, no `transform: translate()` en CSS.
- Golpes repetidos sobre el mismo elemento: `FT()` (ya lleva `immediateRender:false`), no dos `T()` encadenados.
- `f()` falla con "FRASE NO ENCONTRADA" → la palabra está escrita distinto en `words.json`: mira `--guion`. Si
  se repite en el video, usa `f('palabra', despues=t_anterior)`.
- whisper escribe mal nombres propios → `correcciones={'cloud': 'Claude', 'chayipiti': 'ChatGPT'}`.
- Tildes y eñes: directo en UTF-8 o como entidades HTML; el archivo debe guardarse en UTF-8.
- `--no-audio` no remezcla: si cambiaste efectos, música o tiempos, corre `build.py` SIN esa bandera antes de
  renderizar (el primer build de un proyecto siempre mezcla). `lint` con `audio_src_not_found` = falta esa mezcla.
- `snapshot` se queda sin tiempo → sube `--timeout 90000` y pide menos segundos por llamada.
- No dejes otros `.html` con `data-composition-id` en la carpeta del proyecto (copias de `index.html`).
- Windows: `python -X utf8`; no uses `drawtext` de ffmpeg para rotular (usa `hoja.py`).
- Si cambian los cortes después de recortar: `preparar.py` borra `cutout.webm`; hay que correr `recortar.py` otra vez.

## 8. Qué entregar

1. El borrador (`renders/borrador.mp4`) y, tras el OK, el final (`renders/<nombre>-FINAL.mp4`) verificado.
2. Dos líneas: qué se hizo y qué puede cambiar el usuario (color, música, textos, fotos).
3. Nunca publiques ni subas nada por tu cuenta: publicar es decisión del usuario.

Créditos y licencias: ver `README.md`.
