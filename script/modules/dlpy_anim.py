#!dlpy_anim.py
# -*- coding: utf-8 -*-
# 0.0.3: A 120 Hz. Los cuadros por segundo ya no son fijos (30): ANIM_FPS sale de DLPY_ANIMATION_FPS, de dlpy_anim.json (junto al modulo; lo escribe
#        `python dlpy_anim.py --fps 120`) o de configure(fps=...): 15–120, por defecto 30. El host no sabe nada de esto. Es EL reloj de toda la escena (se retiran SITE_FPS, CONV_FPS y SCENE_FPS, que eran el mismo numero con tres
#        nombres; solo queda aparte CONV_RUN_FPS = 12 mientras convierte, a proposito ligero). MOTOR UNICO: (1) el «ruido» de los glitch
#        (letras que se desordenan en intros, transformaciones y textos) se sembraba con el NUMERO DE CUADRO, asi que a 120 Hz habria ido 4
#        veces mas rapido y nervioso: ahora se siembra con un reloj propio de GLITCH_HZ = 30 por segundo, igual que se veia a 30 (a cualquier
#        fps); (2) el hilo mide cuanto tarda en pintar un cuadro (incluido el volcado a la terminal) y baja solo los cuadros por segundo para
#        no ocupar mas del 50 % del tiempo (FPS_DUTY): asi un fps alto nunca le quita CPU a la descarga ni atrasa la terminal; si el iPhone
#        no llega a 120, va a lo que llegue y sube de nuevo cuando el dibujo es ligero; (3) el reposo entre cuadros nunca baja de 1 ms.
#        Todo lo demas ya iba por tiempo (easing con dt, relojes ta·k, fases por segundos), asi que a 120 Hz solo se ve mas suave.
# 0.0.2: la escena MUESTRA LA CONVERSION. El dibujo «conv» (chips origen → destino, via de puntos que se llena con el % real, el codigo
#        de destino como titulo y el aviso «Espera mientras convierte…») venia de la 2.1.5 pero nadie lo activaba: con escena, ensure_apple
#        convertia en silencio. Nuevo para el host (API sigue en 1; un modulo viejo simplemente no los tiene y el host los salta):
#        AnimUI.conv_begin(path, streams, plan, final_ext, enc) / conv_progress(pct) / conv_end(ok=True) y sus puentes ux_conv_begin/progress/end.
#        conv_begin recibe los datos crudos del host y decide los chips aqui (conv_chips: VP9 -> H.264, MKV -> MP4, OPUS -> AAC, HEV1 -> HVC1).
#        conv_begin espera (scene_gate) a que el dibujo anterior se vea entero; un intento nuevo tras un fallo reinicia la via; conv_end(ok=True)
#        llena la via y el destino destella (CONV_END_HOLD); conv_end(ok=False) quita el dibujo sin destello.
# 0.0.1: primer modulo aparte (escena extraida de la 2.1.5 del DLpy original). Version propia: VERSION (esta) y API (entero
#        que sube cuando cambia lo que dlpy.py espera de este archivo; el host compara con su ANIM_API y, si no
#        coincide, usa su barra simple). Se retiran funciones sin uso (scene_wait_*, scene_brand/note/hold,
#        ux_pp_progress/hold/note/shape/wait_anim), el import shlex y ANIM_LIVE; la V del titulo muestra la version
#        del host (HOST_VERSION, via configure(version=...)) y no el texto "anim".
#        Entrada para el host: configure(tr=..., lang=..., version=...), available() y AnimUI(url, total, audio_only)
#        con begin / hook / pp_hook / end / abort. Todo lo demas es interno. Variables DLPY_ANIMATIONS_ENABLED,
#        DLPY_ANIMATION_LOOP_SECS, DLPY_COLOR_TRUECOLOR... se leen del entorno como en la 2.1.5.
"""DLpy - animaciones de la escena (modulo opcional)."""
import atexit
import math
import os
import re
import json
import sys
import time
import threading
import unicodedata
import shutil
import site
import urllib.parse
import urllib

VERSION = "0.0.3"       # version de este modulo
API = 1                 # contrato con dlpy.py (su ANIM_API): subir al cambiar AnimUI/configure/available

# ══════════════════════════════════════ PUENTE CON EL HOST (dlpy.py) ══════════════════════════════════════
# Lo que en la 2.1.5 vivía fuera de la escena (idiomas, preguntas, red, banner) aquí son stubs neutros.
# El host los sustituye con configure(); lo que no se sustituye no hace nada.
_HOST = {"tr": None, "lang": "es", "env": None}


def _tr(text, lang=None):
    f = _HOST.get("tr")
    if f is None or not isinstance(text, str) or not text:
        return text
    try:
        return f(text)
    except Exception:
        return text


def env_get(name, default=None):
    f = _HOST.get("env")
    if f is not None:
        try:
            v = f(name)
            if v is not None:
                return v
        except Exception:
            pass
    return os.environ.get(name, default)


def t(text, lang=None):
    return _tr(text)


def t_display(text, lang=None, _debug=True):
    return _tr(text)


def t_status(text, lang=None):
    return _tr(text)


def tr(text, lang=None, _debug=True):
    return _tr(text)


def sec_unit():
    return "s" if _HOST.get("lang", "es") == "es" else _tr("seg")


def loc_num(n, decimals=None):
    try:
        x = float(n)
    except (TypeError, ValueError):
        return str(n)
    if decimals is None:
        return ("%d" % int(x)) if x == int(x) else ("%.10g" % x)
    return ("%." + str(int(decimals)) + "f") % x


LANG = "es"
LANG_ID_MODE = "0"
LANG_NAMES = {}
LANG_SELECT_TEXT = {"es": "Seleccione idioma"}
LANG_SUMS = {}
PACK_LANGS = ()
UX_ENTER = {"es": "Enter"}
BOOT_T0 = time.time()
HOST_VERSION = VERSION  # lo que se muestra como "v..." en pantalla; el host lo reemplaza con configure(version=...)


def lang_mark_cells(cells):
    return cells


def lang_mark_color(output):
    return output


def lang_mark_register(plain):
    return None


def lang_pack_url(*a, **k):
    return ""


def lang_pack_sha_url(*a, **k):
    return ""


def device_label():
    return "a-Shell"


NET = {}
PREFETCH = {"on": False, "keys": [], "res": {}, "done": set(), "n": 0, "hosts": "", "t0": 0.0, "changed": False, "quiet_fail": False}


def net_level(now=None):
    return 0.0


def _wants(args, name):
    return False


def wants_scm(args=None):
    return False


def wants_scb(args=None):
    return False


def wants_atajo(args=None):
    return False


def ask(*a, **k):
    return ""


def clear_screen():
    if sys.stdout.isatty():
        sys.stdout.write("\x1b[2J\x1b[H")
        sys.stdout.flush()


def ui_lines():
    try:
        return term_rows()
    except (OSError, ValueError):
        return 24


def drain_pending_input(*a, **k):
    return None


def hide_keyboard(*a, **k):
    return None


def settle_terminal(*a, **k):
    return None


def _restore_tty(*a, **k):
    return None


def log_shortcutmode_diagnostic(*a, **k):
    return None


def log_shortcutmode_stderr(*a, **k):
    return None


def pip_args(*a, **k):
    return []


def pip_cmd(*a, **k):
    return ""


def repo_info(*a, **k):
    return None


def probe_stream_facts(*a, **k):
    return None


def stream_needs_probe(*a, **k):
    return False


class _FfmpegShim:
    executable = None


def configure(tr=None, lang=None, env=None, version=None, fps=None):
    """El host (dlpy.py) entrega su traductor tr(texto) -> texto, el idioma, su version y, si quiere, env(nombre) -> valor y los fps (15–120)."""
    global LANG, HOST_VERSION, ANIM_FPS
    if fps is not None:
        ANIM_FPS = fps_parse(fps, ANIM_FPS)
    if version:
        HOST_VERSION = str(version)
    if tr is not None:
        _HOST["tr"] = tr
    if lang:
        _HOST["lang"] = lang
        LANG = lang
    if env is not None:
        _HOST["env"] = env


CHIP_COLS = 8                       # 1.7.1: columnas de texto que caben en un chip (antes 6 caracteres)

_UX_CHIP_CACHE = {}

def ux_pick(*cands, room=None, fallback=None):
    """1.7.1: (índice, texto) del primer candidato (del más largo al más corto, en español canónico) que, YA TRADUCIDO, cabe en `room` columnas reales. Sin `room` toma el
    primero. Si ninguno cabe: `fallback` traducido (índice = len(cands)) o, sin él, el último recortado con «…»."""
    outs = [t_display(c) for c in cands]
    if room is None:
        return 0, outs[0]
    for i, s in enumerate(outs):
        if dwidth(s) <= room:
            return i, s
    if fallback is not None:
        return len(outs), t_display(fallback)
    return len(outs) - 1, fit_text(outs[-1], room)

def ux_text(*cands, room=None, fallback=None):
    """1.7.1: lo mismo que ux_pick pero solo el texto."""
    return ux_pick(*cands, room=room, fallback=fallback)[1]

def ux_chip(x, cols=None):
    """1.7.1: texto de un chip: en el idioma activo, en mayúsculas, solo caracteres que se ven y como mucho `cols` (CHIP_COLS) columnas reales («webm» → «WEBM», VIEJO → «OLD»)."""
    key = (LANG, str(x), cols)
    hit = _UX_CHIP_CACHE.get(key)
    if hit is not None:
        return hit
    s = t_display(" ".join(str(x or "").split()))
    # DLPY_TRANSLATION_DEBUG_MODE=mark: el chip se calcula en plano y al final se vuelve a colorear
    marked = "\x1b" in s
    s = _ANSI_RE.sub("", s).upper()
    if s.startswith("DOLBY"):
        s = "DV"
    s = "".join(ch for ch in s if ch.isprintable() and dwidth(ch) >= 1)
    out = clip_text(s, cols or CHIP_COLS).strip()
    if marked and out:
        out = lang_mark_color(out)
    if len(_UX_CHIP_CACHE) > 512:
        _UX_CHIP_CACHE.clear()
    _UX_CHIP_CACHE[key] = out
    return out

def ux_enter_key(lang=None):
    """1.7.1: cómo se llama la tecla Enter en el idioma activo (Enter · Entrée · Invio). 1.9.2: con DLPY_TRANSLATION_DEBUG_MODE=id/both sale el msgid («Enter»), no el nombre traducido;
    con both, en la escena, se anota para pintarlo en el color de mark."""
    if LANG_ID_MODE in ("id", "both"):
        _sc = globals().get("SCENE")
        if LANG_ID_MODE == "both" and USE_COLOR and _sc and _sc.get("on"):
            lang_mark_register("Enter")
        return "Enter"
    return UX_ENTER.get(lang or LANG, "Enter")

def ux_enter_names():
    """1.7.1: todos los nombres que puede tener la tecla Enter en una línea de opciones (para resaltarla en cualquier idioma)."""
    return set(UX_ENTER.values()) | {"Enter"}

HOME = os.path.expanduser("~")

FILES_DIR = os.path.join(HOME, "Documents", "dlpy_files")

SCRIPT_PATH = os.path.abspath(__file__)

SHORTCUT_NAME = "DLpy"

def has(codec):
    return bool(codec) and codec != "none"

DEBUG = env_get("DLPY_DEBUG_LOGGING", "").strip().lower() not in ("", "0", "no", "false")

_env_color = env_get("DLPY_COLOR_TRUECOLOR")

if _env_color is not None:
    USE_COLOR = _env_color.strip().lower() not in ("0", "no", "false", "")
else:
    USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")

RESET = "\x1b[0m"                 # quita colores y estilos

WRAP_OFF, WRAP_ON = "\x1b[?7l", "\x1b[?7h"          # apagar / encender el salto automático de línea

CURSOR_HIDE, CURSOR_SHOW = "\x1b[?25l", "\x1b[?25h"

HOME_CLEAR = "\x1b[2J\x1b[H"                         # pantalla en blanco y cursor arriba

def cur_to(row, col=1):
    """Mueve el cursor a la fila `row` y columna `col` (desde 1)."""
    return f"\x1b[{row};{col}H"

def send_key(view=False):
    """1.9.8: la CLAVE (en español) del estado del envío. La escena guarda la clave y la traduce al pintar (t_status); si se guardara ya traducida
    («Sending to…»), scene_motif_kind no la reconocería con otro idioma y el centro caía en D L P Y en vez del dibujo de envío."""
    return "Abriendo con view" if view else "Enviando a " + SHORTCUT_NAME

_ORIG_GTS = shutil.get_terminal_size

def _ioctl_first_size(fallback=(80, 24)):
    for _st in (sys.stdout, sys.stderr, sys.stdin):
        try:
            _sz = os.get_terminal_size(_st.fileno())
            if _sz.columns > 0 and _sz.lines > 0:
                return _sz
        except (OSError, ValueError, AttributeError):
            continue
    return _ORIG_GTS(fallback)

shutil.get_terminal_size = _ioctl_first_size

CLEAR_SEQS = {"1": "\x1b[3J\x1b[2J\x1b[H", "2": "\x1b[2J\x1b[3J\x1b[H",
              "3": "\x1bc", "4": HOME_CLEAR}

CLEAR_SEQ = CLEAR_SEQS.get(env_get("DLPY_CLEAR_MODE", "3").strip(), CLEAR_SEQS["3"])

def purge_seq(raw):
    """1.3.2: «ESC[3J» (vaciar el historial al borrar), salvo que DLPY_CLEAR_PURGE_SCROLLBACK valga 0 / no / false / off o esté vacía. Sin definir = se manda."""
    raw = "1" if raw is None else raw
    return "" if str(raw).strip().lower() in ("0", "no", "false", "off", "") else "\x1b[3J"

PURGE_SEQ = purge_seq(env_get("DLPY_CLEAR_PURGE_SCROLLBACK"))

CLEAR_MODE = (env_get("DLPY_CLEAR_MODE") or "auto").strip().lower()

def clear_mode_seq(mode, purge=None):
    """1.3.2:"""
    purge = PURGE_SEQ if purge is None else purge
    return {"home": "\x1b[H\x1b[2J" + purge + "\x1b[H", "down": "\x1b[H\x1b[J" + purge,
            "purge-first": purge + "\x1b[H\x1b[2J", "reset": "\x1bc"}.get(str(mode or "").strip().lower())

NATIVE_CLEAR = env_get("DLPY_CLEAR_USE_NATIVE", "1").strip().lower() not in ("0", "no", "false", "")

_NATIVE_CLEAR_BAD = [False]               # True si `clear` falló una vez: no se vuelve a intentar en esta ejecución

def _scm_run():
    """True si esta ejecución es --scm / --scb:"""
    try:
        return any(a[:1] in "-\u2013\u2014" and a.lstrip("-\u2013\u2014").lower().split("=")[0] in ("scm", "scb")
                   for a in sys.argv[1:])
    except Exception:
        return False

def early_clear_mode(early, clear_mode):
    """1.3.5:"""
    if str(clear_mode or "auto").strip().lower() != "auto":
        return None
    return (str(early or "").strip().lower() or "reset")

def scene_clear_mode():
    """1.6.6: el modo del borrado con que arranca la escena: el mismo del primer borrado (reset por omisión, o DLPY_CLEAR_FIRST_MODE / DLPY_CLEAR_MODE)."""
    return early_clear_mode(env_get("DLPY_CLEAR_FIRST_MODE"), CLEAR_MODE)

def sh_run(cmd):
    """1.8.7: único punto por donde DLpy lanza comandos de a-Shell (pip, view, open, pbcopy, trash, clear, hideKeyboard).
    No usa subprocess a propósito: en a-Shell (iOS) no hay fork/exec y esos comandos son internos del propio a-Shell, que solo os.system sabe ejecutar.
    Devuelve el código de salida real (0-255): si os.system devuelve el estado de espera (código × 256) se normaliza aquí, en un solo lugar."""
    rc = os.system(cmd)
    return rc >> 8 if rc > 255 else rc

def native_clear(fallback=None, mode=None):
    """ÚNICO punto de borrado de la consola:"""
    if _scm_run() or not sys.stdout.isatty():
        return False
    if ux_on():                            # 0.9.3: la escena de --shortcutpick es dueña de la pantalla: nadie la borra
        return False
    ok = False
    try:
        sys.stdout.flush()                 # lo pendiente de Python sale antes que el comando nativo
        # 1.3.2: DLPY_CLEAR_MODE distinto de «auto»: secuencia directa (ya lleva el historial)
        mseq = clear_mode_seq(mode or CLEAR_MODE)
        if mseq is not None:
            sys.stdout.write(mseq)
            sys.stdout.flush()
            return True
        if NATIVE_CLEAR and not _NATIVE_CLEAR_BAD[0]:
            ok = sh_run("clear") == 0
            if not ok:
                _NATIVE_CLEAR_BAD[0] = True
        if not ok:
            sys.stdout.write(CLEAR_SEQ if fallback is None else fallback)
            sys.stdout.flush()
            ok = True
        if PURGE_SEQ:                      # 1.2.3: y el historial, para que no reaparezca al crecer la ventana
            sys.stdout.write(PURGE_SEQ)
            sys.stdout.flush()
    except Exception:
        return False
    return ok

def _flag_env(name, default=True):
    v = env_get(name)
    return default if v is None else str(v).strip().lower() not in ("0", "no", "false", "")

TRUECOLOR = USE_COLOR and _flag_env("DLPY_COLOR_TRUECOLOR", True)

ANIM = sys.stdout.isatty() and not DEBUG and _flag_env("DLPY_ANIMATIONS_ENABLED", True)

PALETTE = {"orange": ((255, 138, 61), "93"), "magenta": ((255, 61, 139), "95"),
           "mint": ((61, 220, 151), "92"), "amber": ((255, 196, 61), "93"),
           "gray": ((130, 130, 144), "2"), "track": ((58, 58, 70), "90"),
           "white": ((235, 235, 240), "0"), "red": ((255, 85, 102), "91")}

_ALIAS = {"green": "mint", "yellow": "amber", "blue": "orange", "cyan": "orange", "dim": "gray"}

FLAG_COLORS = {"apple": "mint", "orig": "amber", "default": "orange", "best": "magenta",
               "cur": "mint", "upd": "orange", "saved": "mint", "bad": "red"}      # 2.0.0: cur/upd (versiones) · saved/bad (config)

FLAG_MARKS = {"apple": "✓", "orig": "◆", "default": "▸", "best": "★", "cur": "✓", "upd": "⬆", "saved": "●", "bad": "✗"}

FLAG_TEXT = {"apple": "compatible Apple", "orig": "pista original", "default": "predeterminada",
             "best": "recomendada"}


QUIET = {"on": False}                # 0.8.1: --shortcutpick sin animaciones hasta la intro del sitio

def scene_defaults():
    """1.4.1: el estado inicial de la escena, en un solo sitio (SCENE y scene_start lo usan; antes eran dos listas que se podían desalinear)."""
    return {"on": False, "stop": False, "th": None, "mute": None, "out": None, "geo": None, "a": None, "b": None,
            "name": "", "mode": "both", "mode_orig": "both", "title_raw": "", "t_title": None, "label": "", "pct": None, "frac": 0.0,
            "shown": 0.0, "lo": 0.0, "hi": 0.0, "rows": 24, "brand": False, "busy": False, "t_out": None, "k_out": None, "t_in": None, "resume": False,
            "aspect": None, "asp_shown": None, "res": None, "alabel": None, "vinfo": {}, "ainfo": {}, "count": 0, "conv": None, "ask": None, "ta": 0.0,
            "done": set(), "done_at": {}, "stream_total": 1, "stream_seen": 0, "type_totals": {}, "type_seen": {}, "last_error": None, "err_brand": False, "emute": None,
            "started": {}, "finished": {}, "last_finished": None, "pp_pct": None, "welcome": None,
            "check": None, "clean": 0, "send_to": None, "dl_done": None, "label_wall": None, "err": None, "link": None, "pip_line": None, "ana_raw": False,
            "skind": {}, "spct": {}, "slang": {}, "past_dl": False, "motivo": "", "gate_paid": None, "loop_paid": None, "site_t": None, "fast": False, "speed": None, "speed_last": None, "speed_peak": 0.0, "speed_t": None, "speed_end": None}      # 1.4.5: qué es y cuánto lleva cada pista, si ya empezó la descarga y el nombre del motivo del centro

SCENE = scene_defaults()

def quiet_set(on):
    """Apaga (True) o devuelve (False) las animaciones. Solo --shortcutpick lo usa, hasta justo antes de la intro."""
    QUIET["on"] = bool(on)

def ux_on():
    """1.5.7: ¿está viva la escena? (la UIM y el núcleo preguntan aquí, no a SCENE)."""
    return bool(SCENE["on"])

def paint(text, color, bold=None):
    """Pinta `text` con un color de la paleta. «bold» solo = negrita en blanco."""
    if not USE_COLOR or not text:
        return text
    if color == "bold":
        color, bold = "white", True
    rgb, basic = PALETTE[_ALIAS.get(color, color)]
    code = f"38;2;{rgb[0]};{rgb[1]};{rgb[2]}" if TRUECOLOR else basic
    return f"\x1b[{'1;' if bold else ''}{code}m{text}{RESET}"

BLACK, WHITE = (0, 0, 0), (255, 255, 255)

def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t + 0.5) for i in range(3))

GRAD_STEPS = 32

def mix6(a, b, k):
    """mix(a, b, k) con k acotado a 0–1 y en GRAD_STEPS pasos (1.9.7: 32; antes 6, con cortes visibles; el nombre se conserva)."""
    return mix(a, b, round(max(0.0, min(1.0, k)) * GRAD_STEPS) / float(GRAD_STEPS))

def flag_mark(k):
    return paint(FLAG_MARKS[k], FLAG_COLORS[k])

_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")

_PROBE = {"cols": None, "tried": False}

def dwidth(text):
    """Columnas que ocupa `text` en pantalla: sin códigos ANSI, emojis y CJK = 2."""
    n = 0
    for ch in _ANSI_RE.sub("", str(text)):
        if unicodedata.combining(ch) or ch in "\u200d\ufe0e\ufe0f":
            continue
        n += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return n

def text_cells(text):
    """Celdas visibles; omite ANSI sin perder los índices originales ni el ancho de CJK/emojis."""
    source = str(text)
    out, off, i = [], 0, 0
    while i < len(source):
        if source[i] == "\x1b":
            match = _ANSI_RE.match(source, i)
            if match:
                i = match.end()
                continue
        ch = source[i]
        if ch.isprintable():
            w = dwidth(ch)
            if w == 0:
                if out:
                    out[-1] = (out[-1][0], out[-1][1] + ch, out[-1][2], out[-1][3])
            else:
                out.append((i, ch, off, w))
                off += w
        i += 1
    return out

def _ansi_color_at(text, index, default):
    """Color SGR activo en un índice; permite que las marcas de traducción conserven su color en escenas por celdas."""
    active = default
    for match in _ANSI_RE.finditer(str(text)):
        if match.start() >= index:
            break
        raw = match.group(0)[2:-1]
        try:
            values = [int(x) if x else 0 for x in raw.split(";")]
        except ValueError:
            continue
        if not values or values[0] == 0:
            active = default
            continue
        if len(values) >= 5 and values[0] == 38 and values[1] == 2:
            active = tuple(max(0, min(255, n)) for n in values[2:5])
        elif values[0] == 38 and len(values) >= 3 and values[1] == 5:
            # Colores ANSI 256 habituales; la marca solo usa colores básicos/truecolor, pero conserva un fallback seguro.
            active = PALETTE["orange"][0] if values[2] in (208, 214, 220) else default
        elif values[0] in (2, 90):
            active = PALETTE["gray"][0]
        elif values[0] in (91, 31):
            active = PALETTE["red"][0]
        elif values[0] in (92, 32):
            active = PALETTE["mint"][0]
        elif values[0] in (93, 33):
            active = PALETTE["orange"][0]
        elif values[0] in (95, 35):
            active = PALETTE["magenta"][0]
        elif values[0] in (97, 37):
            active = PALETTE["white"][0]
    return active

def put_text(cells, x, y, text, color, bg=None, lo=None, hi=None, skip_space=True):
    """Escribe celdas visibles y conserva colores ANSI locales sin imprimir sus secuencias."""
    source = str(text)
    has_ansi = "\x1b" in source
    for i, s_, dx, w in text_cells(source):
        xx = x + dx
        if (skip_space and s_ == " ") or (lo is not None and xx < lo) or (hi is not None and xx + w > hi):
            continue
        base_col = color(i, s_) if callable(color) else color
        col = _ansi_color_at(source, i, base_col) if has_ansi else base_col
        cells[(xx, y)] = (s_, col, bg)
        if w == 2:
            cells[(xx + 1, y)] = ("", col, bg)
    return dwidth(source)

def clip_text(text, width):
    """1.7.0: el principio de `text` que cabe en `width` columnas (sin «…»)."""
    text = str(text)
    # con color (DLPY_TRANSLATION_DEBUG_MODE=mark): se conservan las secuencias y se cierra con RESET
    if "\x1b" in text:
        end, n = 0, 0
        for i, _s, _dx, w in text_cells(text):
            if n + w > width:
                break
            end, n = i + 1, n + w
        else:
            return text
        return text[:end] + RESET
    out, n = "", 0
    for _i, s_, _dx, w in text_cells(text):
        if n + w > width:
            break
        out, n = out + s_, n + w
    return out

def ansi_upper(text):
    """MAYÚSCULAS sin tocar las secuencias ANSI (un .upper() directo convertiría «\x1b[38;2;…m» en «…M» y se vería basura)."""
    parts, last = [], 0
    for m in _ANSI_RE.finditer(str(text)):
        parts.append(str(text)[last:m.start()].upper())
        parts.append(m.group(0))
        last = m.end()
    parts.append(str(text)[last:].upper())
    return "".join(parts)

def fit_text(text, width, ellipsis="…"):
    """Recorta texto plano a `width` columnas con «…» (nunca lo parte sin avisar). Con color ANSI al principio (mark) lo conserva."""
    text = str(text)
    if dwidth(text) <= width:
        return text
    if "\x1b" in text:
        head = _ANSI_RE.match(text)
        return (head.group(0) if head else "") + fit_text(_ANSI_RE.sub("", text), width, ellipsis) + RESET
    out, n = "", 0
    for ch in text:
        w = dwidth(ch)
        if n + w > width - 1:
            break
        out, n = out + ch, n + w
    return out + ellipsis

def wrap_text(text, width):
    """Ajuste de línea por palabras:"""
    width = max(8, int(width))
    lines = []
    for para in str(text).split("\n"):
        cur, curw = "", 0
        for word in para.split(" "):
            if not word:
                continue
            ww = dwidth(word)
            if ww > width:                    # palabra más larga que la línea: en trozos
                if cur:
                    lines.append(cur)
                chunk, cw = "", 0
                for ch in word:
                    w = dwidth(ch)
                    if cw + w > width:
                        lines.append(chunk)
                        chunk, cw = "", 0
                    chunk, cw = chunk + ch, cw + w
                cur, curw = chunk, cw
            elif not cur:
                cur, curw = word, ww
            elif curw + 1 + ww <= width:
                cur, curw = cur + " " + word, curw + 1 + ww
            else:
                lines.append(cur)
                cur, curw = word, ww
        lines.append(cur)
    lines = lines or [""]
    # el color que queda abierto al final de una línea se cierra y se reabre en la siguiente
    if "\x1b" in str(text):
        active, out = "", []
        for ln in lines:
            ln = active + ln
            for m in _ANSI_RE.finditer(ln):
                active = "" if m.group(0) in ("\x1b[0m", "\x1b[m") else m.group(0)
            out.append(ln + (RESET if active else ""))
        lines = out
    return lines

def _read_cpr(fd, timeout=0.35):
    """Espera «ESC [ fila ; columna R» (respuesta del terminal) y devuelve la columna."""
    import select
    buf, end = b"", time.time() + timeout
    while time.time() < end:
        if not select.select([fd], [], [], max(0.0, end - time.time()))[0]:
            break
        chunk = os.read(fd, 64)
        if not chunk:
            break
        buf += chunk
        m = re.search(rb"\x1b\[(\d+);(\d+)R", buf)
        if m:
            return int(m.group(2))
    return None

def probe_cols(refresh=False):
    """Mide el ancho REAL del terminal preguntándoselo:"""
    flag = env_get("DLPY_PROBE_TERMINAL_WIDTH_ENABLED", "").strip()
    if flag != "1":                           # solo con DLPY_PROBE_TERMINAL_WIDTH_ENABLED=1
        return None
    if _PROBE["tried"] and (_PROBE["cols"] is None or not refresh):
        return _PROBE["cols"]
    try:
        if not (tty_both()):
            return None
        import termios, tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
    except Exception as _ign:
        ignore("probe_cols", _ign)
        return None
    _PROBE["tried"] = True
    cols = None
    try:
        tty.setcbreak(fd, termios.TCSANOW)
        sys.stdout.write("\r\x1b[999C\x1b[6n\r")
        sys.stdout.flush()
        cols = _read_cpr(fd)
    except Exception as _ign:
        ignore("probe_cols", _ign)
    finally:
        _restore_tty(fd, old)
        if cols is None:
            drain_pending_input(0.1)        # por si la respuesta llega tarde
    _PROBE["cols"] = cols if cols and 20 <= cols <= 400 else None
    return _PROBE["cols"]

def term_rows():
    """Alto del terminal (24 si no se puede medir)."""
    return shutil.get_terminal_size((80, 24)).lines

def tty_both():
    """¿Hay terminal de verdad en la entrada y en la salida?"""
    return sys.stdin.isatty() and sys.stdout.isatty()

def _cols():
    """(columnas, medidas): medida con probe_cols o, si no, la que informa el entorno."""
    c = _PROBE["cols"]
    if c is None and not _PROBE["tried"] and RUNTIME["bar"] is None:
        c = probe_cols()
    if c:
        return c, True
    try:
        return shutil.get_terminal_size((80, 24)).columns, False
    except (OSError, ValueError) as _ign:
        ignore("term_width", _ign)
        return 80, False

def _forced_width():
    try:
        return max(20, int(env_get("DLPY_TERMINAL_WIDTH_COLS", "").strip()))
    except ValueError:
        return None

def _ioctl_cols():
    """Columnas según el propio terminal (ioctl TIOCGWINSZ), sin tocar su modo ni COLUMNS."""
    for stream in (sys.stdout, sys.stderr, sys.stdin):
        try:
            c = os.get_terminal_size(stream.fileno()).columns
        except (OSError, ValueError, AttributeError):
            continue
        if 30 <= c <= 120:
            return c
    return None

def term_width():
    """Ancho para el texto:"""
    forced = _forced_width()
    if forced:
        return forced
    cols, measured = _cols()
    w = cols - 1
    if not measured:
        cap = 40
        ic = _ioctl_cols()
        if ic:
            w, cap = ic - 1, 110              # el terminal sabe su ancho: se usa entero
        w = min(w, cap)
    return max(24, min(w, 110))

def safe_width():
    """Ancho de las líneas de una sola pieza (banner, separadores, barras):"""
    forced = _forced_width()
    return forced if forced else max(20, min(term_width(), 80))

RUNTIME = {"bar": None, "nested_ios": False}

DIAGNOSTICS = {"E": 0, "A": 0}

DIAGNOSTICS_ACTIVITY = {"E": 0.0, "A": 0.0}

DIAGNOSTICS_LOCK = threading.Lock()

DIAG_HOLD, DIAG_FADE = 1.2, 0.3  # mismo encendido y fundido que el icono N de la bottombar

def diagnostic_increment(kind, now=None):
    key = str(kind or "").upper()[:1]
    if key not in DIAGNOSTICS:
        return 0
    with DIAGNOSTICS_LOCK:
        DIAGNOSTICS[key] += 1
        DIAGNOSTICS_ACTIVITY[key] = time.time() if now is None else float(now)
        return DIAGNOSTICS[key]

def diagnostic_report(kind, msg=None):
    """Único punto de entrada de errores (E) y avisos (A): enciende el pulso de la bottombar y, con `msg`, lo anota en internal/logs.
    Todo lo que el usuario puede ver como error o aviso (m_err, m_warn, estados «No se pudo…» de la escena, stderr, yt-dlp, respuestas inválidas,
    excepciones sin capturar) pasa por aquí."""
    key = str(kind or "").upper()[:1]
    if key not in DIAGNOSTICS:
        return 0
    n = diagnostic_increment(key)
    if msg:
        try:
            log_shortcutmode_diagnostic("WARNING" if key == "A" else "ERROR", msg)
        except Exception as _ign:
            ignore('diagnóstico: registro', _ign)
    return n

def diagnostic_level(kind, now=None):
    """Intensidad del icono E/A: blanco al ocurrir y fundido gradual hasta el gris base."""
    key = str(kind or "").upper()[:1]
    if key not in DIAGNOSTICS_ACTIVITY:
        return 0.0
    now = time.time() if now is None else float(now)
    with DIAGNOSTICS_LOCK:
        last = DIAGNOSTICS_ACTIVITY[key]
    dt = now - last
    if last <= 0.0 or not (0.0 <= dt < DIAG_HOLD):
        return 0.0
    return max(0.0, min(1.0, (DIAG_HOLD - dt) / DIAG_FADE))

def dbg(label, data=None):
    """Línea de depuración en bruto. No hace nada si DEBUG está apagado.
    2.1.2: no escribe nada en modos JSON puro ni cuando stdout no es TTY (Atajos / a-Shell mini
    a menudo mezclan stderr+stdout y rompen el parseo del diccionario)."""
    if not DEBUG:
        return
    # Evitar contaminar la salida que lee el atajo (stdout o streams mezclados)
    try:
        args = sys.argv[1:]
        if wants_atajo(args) or wants_scm(args) or wants_scb(args) or _wants(args, "shortcutpick"):
            return
    except Exception:
        pass
    try:
        if not sys.stdout.isatty():
            return
    except Exception:
        return
    if data is None:
        text = ""
    elif isinstance(data, str):
        text = data
    else:
        try:
            text = json.dumps(data, ensure_ascii=False, default=str, sort_keys=True)
        except Exception:
            text = repr(data)
    sys.stderr.write(paint(f"[debug] {label}: {text}", "gray") + "\n")
    sys.stderr.flush()

def ignore(donde, err):
    """Anota en modo debug un error que se ignora a propósito (sin debug no hace nada)."""
    dbg(f"{donde}: ignorado", repr(err))

class quiet:
    """`with quiet("donde", OSError): ...` — ignora (y anota en debug, vía ignore) lo que el bloque lance del tipo dado (por omisión Exception)."""

    def __init__(self, donde, *tipos):
        self.donde, self.tipos = donde, tipos or (Exception,)

    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        if et is None or not issubclass(et, self.tipos):
            return False
        ignore(self.donde, ev)
        return True

SESSION = {"tag": None}

THEME = {"a": None, "b": None, "full": None}

def _host(link):
    try:
        s = str(link).strip()
        return (urllib.parse.urlparse(s if "//" in s else "//" + s).hostname or "").lower()
    except (ValueError, AttributeError) as _ign:
        ignore("_host", _ign)
        return ""

def _host_is(host, domains):
    return any(host == d or host.endswith("." + d) for d in domains)

SITE_GLITCH = "▒░#@%&$/\\|<>=+*"

GLITCH = _flag_env("DLPY_GLITCH_EFFECT_ENABLED", True)

def _rn(s):
    """Ruido determinista 0–1 (la intro se ve igual en cada ejecución)."""
    s = math.sin(s * 127.1) * 43758.5453
    return s - math.floor(s)

def _fg(c):
    return f"\x1b[38;2;{c[0]};{c[1]};{c[2]}m"

def _bg(c):
    return f"\x1b[48;2;{c[0]};{c[1]};{c[2]}m"

SITE_ANIM = _flag_env("DLPY_ANALYZE_ANIMATION_ENABLED", True)       # DLPY_ANALYZE_ANIMATION_ENABLED=0 la apaga

SITE_SECS = 2.0                                    # duración de la intro (s)

SITE_HOLD_AT = 0.58                                # punto de la intro (0–1) donde espera si el análisis sigue en curso

FPS_DEFAULT, FPS_MIN, FPS_MAX = 30, 15, 120      # 0.0.3: cuadros por segundo de la escena (por defecto 30; DLPY_ANIMATION_FPS o configure(fps=) hasta 120)

FPS_DUTY = 0.5                                   # 0.0.3: parte maxima del tiempo que el hilo puede pasar pintando; si no llega, baja los cuadros solos

GLITCH_HZ = 30                                   # 0.0.3: ritmo del ruido de los glitch, fijo (a 120 fps no se vuelve frenetico)

def fps_parse(raw, default=FPS_DEFAULT):
    """0.0.3: DLPY_ANIMATION_FPS → cuadros por segundo: un entero entre FPS_MIN y FPS_MAX; lo vacio o invalido da `default`."""
    try:
        v = float(str(raw or "").strip().replace(",", "."))
    except ValueError:
        return default
    return default if not math.isfinite(v) else int(max(FPS_MIN, min(FPS_MAX, round(v))))

def fps_file():
    """0.0.3: dlpy_anim.json junto a este modulo: donde el propio modulo guarda sus ajustes (el host no sabe de ellos)."""
    try:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "dlpy_anim.json")
    except NameError:
        return None

def fps_setting():
    """0.0.3: los cuadros por segundo elegidos: DLPY_ANIMATION_FPS del entorno o, si no esta, «fps» de dlpy_anim.json (lo escribe `python dlpy_anim.py --fps N`); si no, FPS_DEFAULT."""
    raw = env_get("DLPY_ANIMATION_FPS")
    if raw in (None, ""):
        try:
            with open(fps_file(), encoding="utf-8") as f:
                raw = json.load(f).get("fps")
        except Exception:
            raw = None
    return fps_parse(raw)

ANIM_FPS = fps_setting()      # EL reloj de la escena (0.0.3: antes SITE_FPS = CONV_FPS = SCENE_FPS = 30)

NOISE_FPS = 12

SITE_ICON = {"video": "►", "audio": "♪", "both": "►♪", "list": "≡►", "live": "●"}

SITE_THEMES = [
    (("youtube.com", "youtu.be"), "YouTube", "YT", "#ff0000", "#ff9aa4"),
    (("tiktok.com",), "TikTok", "TT", "#25f4ee", "#fe2c55"),
    (("instagram.com",), "Instagram", "IG", "#feda75", "#d62976"),
    (("twitter.com", "x.com", "t.co"), "X / Twitter", "X", "#e7e9ea", "#1d9bf0"),
    (("facebook.com", "fb.watch"), "Facebook", "FB", "#1877f2", "#6aa8ff"),
    (("twitch.tv",), "Twitch", "TW", "#9146ff", "#c9a8ff"),
    (("vimeo.com",), "Vimeo", "VM", "#1ab7ea", "#7fdcf5"),
    (("soundcloud.com",), "SoundCloud", "SC", "#ff5500", "#ffb184"),
    (("bandcamp.com",), "Bandcamp", "BC", "#1da0c3", "#8fe0f2"),
    (("reddit.com", "redd.it"), "Reddit", "RD", "#ff4500", "#ff9a70"),
    (("dailymotion.com", "dai.ly"), "Dailymotion", "DM", "#0066dc", "#7fb8ff"),
    (("bilibili.com", "bilibili.tv", "b23.tv"), "Bilibili", "BL", "#00a1d6", "#fb7299"),
    (("kick.com",), "Kick", "KK", "#53fc18", "#b6ff94"),
    (("rumble.com",), "Rumble", "RB", "#85c742", "#d2f0ac"),
    (("mixcloud.com",), "Mixcloud", "MX", "#5000ff", "#a98cff"),
    (("odysee.com",), "Odysee", "OD", "#ef1970", "#ff8fba"),
    (("vk.com", "vkvideo.ru"), "VK", "VK", "#0077ff", "#7db6ff"),
    (("pinterest.com", "pin.it"), "Pinterest", "PI", "#e60023", "#ff8a9a"),
    (("imgur.com",), "Imgur", "IM", "#1bb76e", "#8cf0c1"),
    (("linkedin.com",), "LinkedIn", "LI", "#0a66c2", "#7db7ee"),
    (("archive.org",), "Archive.org", "IA", "#c8c8d4", "#7a7a8c"),
    # 1.6.9: más sitios comunes de yt-dlp. Bluesky, Streamable, Telegram, Snapchat y Tumblr con fuente; el resto, colores de marca de alta confianza
    (("bsky.app", "bsky.social"), "Bluesky", "BS", "#0560ff", "#75afff"),
    (("streamable.com",), "Streamable", "SM", "#0f90fa", "#8ccbfd"),
    (("t.me", "telegram.org", "telegram.me"), "Telegram", "TG", "#26a5e4", "#8fd3f4"),
    (("snapchat.com",), "Snapchat", "SN", "#fffc00", "#fffa8a"),
    (("tumblr.com",), "Tumblr", "TB", "#529ecc", "#a9cfe6"),
    (("ok.ru", "odnoklassniki.ru"), "OK.ru", "OK", "#ee8208", "#f7bc7b"),
    (("newgrounds.com",), "Newgrounds", "NG", "#fda238", "#fecf9c"),
    (("bitchute.com",), "BitChute", "BT", "#ef4137", "#f7a39d"),
    (("peertube.tv", "joinpeertube.org"), "PeerTube", "PT", "#f1680d", "#f8b387"),
    (("loom.com",), "Loom", "LM", "#625df5", "#b0adfa"),
    (("ted.com",), "TED", "TD", "#e62b1e", "#f4968e"),
    (("crunchyroll.com",), "Crunchyroll", "CR", "#f47521", "#fab990"),
    (("naver.com",), "Naver", "NV", "#03c75a", "#80e3ac"),
    (("weibo.com", "weibo.cn"), "Weibo", "WB", "#e6162d", "#ff8200"),
    (("dropbox.com",), "Dropbox", "DB", "#0061ff", "#80b0ff"),
    (("threads.net", "threads.com"), "Threads", "TH", "#f3f5f7", "#8a8d91"),
    # 1.0.7: sitios con colores de marca propios; los demás usan un color derivado del nombre
    (("pornhub.com", "pornhub.org", "pornhubpremium.com"), "Pornhub", "PH", "#ff9000", "#ffd08a"),
    (("xvideos.com", "xvideos.es", "xvideos.red", "xvideos-india.xxx"), "XVideos", "XV", "#e5222e", "#ff9aa1"),
    (("xnxx.com", "xnxx.tv", "xnxx.es"), "XNXX", "XN", "#2f5bff", "#9db4ff"),
    (("xhamster.com", "xhamster.desi", "xhamster2.com", "xhamster3.com"), "xHamster", "XH", "#d6001c", "#ff8a98"),
    (("redtube.com",), "RedTube", "RT", "#ff1f1f", "#ff9b9b"),
    (("youporn.com",), "YouPorn", "YP", "#ff4d9a", "#ffa8cd"),
    (("spankbang.com",), "SpankBang", "SB", "#ee2b4b", "#ff9cae"),
    (("eporner.com",), "Eporner", "EP", "#e0457b", "#f7a4c1"),
    (("tube8.com",), "Tube8", "T8", "#f2a007", "#ffd98a"),
    (("tnaflix.com",), "TNAFlix", "TN", "#2ea3f2", "#9bd3fa"),
    (("beeg.com",), "Beeg", "BG", "#ff3d3d", "#ffa3a3"),
    (("motherless.com",), "Motherless", "ML", "#8a8a96", "#cfcfd8"),
    (("chaturbate.com",), "Chaturbate", "CB", "#f47321", "#fbb98f"),
    (("stripchat.com",), "Stripchat", "ST", "#d50046", "#ff8fae"),
    (("cam4.com",), "Cam4", "C4", "#00a3e0", "#8ad7f5"),
    (("bongacams.com",), "BongaCams", "BN", "#e3262d", "#ff9fa3"),
    (("onlyfans.com",), "OnlyFans", "OF", "#00aff0", "#8fdcf9"),
    (("fansly.com",), "Fansly", "FS", "#2e9bff", "#9fd0ff"),
    (("rule34.xxx", "rule34.paheal.net"), "Rule34", "R3", "#2fbf71", "#9be6bd"),
    (("brazzers.com",), "Brazzers", "BZ", "#f5c400", "#ffe88a"),
    (("thisvid.com",), "ThisVid", "TV", "#a855f7", "#d9b4fb"),
]

def _hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))

def site_theme(host, ext=""):
    """(nombre, sigla, color 1, color 2) del sitio. Los que no tienen diseño propio usan un color sacado del nombre."""
    for doms, name, sig, c1, c2 in SITE_THEMES:
        if _host_is(host, doms):
            return name, sig, _hex_rgb(c1), _hex_rgb(c2)
    import colorsys
    parts = [p for p in str(host).split(".") if p and p not in ("www", "m")]
    base = parts[-2] if len(parts) >= 2 else (parts[0] if parts else "")
    name = (str(ext or "").strip() or base or "Sitio")[:14]
    name = name[:1].upper() + name[1:]
    h = sum((i + 1) * ord(ch) for i, ch in enumerate(name.lower())) % 360

    def hls(hh, s, l):
        r, g_, b_ = colorsys.hls_to_rgb(hh / 360.0, l, s)
        return (int(r * 255), int(g_ * 255), int(b_ * 255))
    return name, name[:2].upper(), hls(h, 0.85, 0.60), hls((h + 40) % 360, 0.80, 0.76)

def site_mode(run):
    """Qué se baja: live, list, audio, both (video con audio) o video (sin audio)."""
    info = getattr(run, "info", None)
    # intro temprana (--shortcutpick): aún no hay análisis, manda lo que eligió el atajo
    if info is None:
        v = str((getattr(run, "spick", None) or {}).get("v") or "").lower()
        return "audio" if v in ("audio", "audio_best") else "both"
    if info.get("is_live"):
        return "live"
    if (info.get("n_entries") or 0) > 1:
        return "list"
    if getattr(run, "kind", None) == "a":
        return "audio"
    if getattr(run, "selected", None) or has((getattr(run, "fmt", None) or {}).get("acodec")):
        return "both"
    return "video"

def site_theme_apply(run):
    """Fija (una sola vez por ejecución)"""
    if THEME["full"] is not None:
        return THEME["full"]
    if not (SITE_ANIM and USE_COLOR and TRUECOLOR):
        return None
    info = getattr(run, "info", None) or {}
    full = site_theme(_host(run.link), info.get("extractor_key") or info.get("extractor") or "")
    THEME["full"], THEME["a"], THEME["b"] = full, full[2], full[3]
    return full

BOTH_BARS_ROWS = 5

BOTH_GAP, BOTH_EQW = 2, 9

MOTIF_ROWS = 5           # alto del motivo (filas)

SCENE_SWAP = 0.325

LOOP_SECS_DEFAULT, LOOP_SECS_MIN, LOOP_SECS_MAX = 1.0, 0.2, 3.0

def loop_secs_parse(raw, default=LOOP_SECS_DEFAULT):
    """1.6.4: DLPY_ANIMATION_LOOP_SECS → segundos del loop de las animaciones: un número entre LOOP_SECS_MIN y LOOP_SECS_MAX (coma o punto); lo vacío o inválido da `default`."""
    s = str(raw or "").strip().replace(",", ".")
    if not s:
        return default
    try:
        v = float(s)
    except ValueError:
        return default
    return default if not math.isfinite(v) else max(LOOP_SECS_MIN, min(LOOP_SECS_MAX, v))

LOOP_SECS = loop_secs_parse(env_get("DLPY_ANIMATION_LOOP_SECS"))

UX_BEAT = LOOP_SECS * 0.7

UX_SETTLE = LOOP_SECS * 0.3

UX_CYCLE = LOOP_SECS     # s de un ciclo de los dibujos que se repiten (envío, descarga, pulso)

UX_HOLD = LOOP_SECS

BADGE_ROW = MOTIF_ROWS

SCENE_STATUS_ROW = 4 + BADGE_ROW + 3                   # 1.8.2: +3 (antes +2) → más aire bajo tarjetas / dibujo

SCENE_TOP = 3                  # fila 1 = aire exterior · fila 2 = topbar seguro · fila 3 = inicio de la escena

CONV_FLOW = 5.0

CONV_KEY_FADE = 0.35     # 1.2.1: s que tarda en apagarse la tecla Enter al pasar de la pregunta a la conversión

CONV_RUN_FPS = 12

CONVERT_FAST_ANIM = _flag_env("DLPY_CONVERT_LIGHT_ANIMATION", True)

FAST_TICK = 1.0

CONV_FILL_RATE = 6.0

CONV_NOTICE = ("Espera mientras convierte · puede tardar · no cierres la app", "Espera mientras convierte · no cierres la app",
               "Espera · puede tardar · no cierres la app", "Espera · no cierres la app", "No cierres la app", "Espera…")    # 1.6.4: el aviso bajo el texto de estado, de más largo a más corto (cabe el primero que quepa)

_FAST_WAKE = threading.Event()

CONV_SPEED = 6.0         # celdas por segundo que avanzan los bloques de la escena de conversión

OLD_TONE = (136, 136, 150)

def video_shape(*srcs):
    """(aspecto ancho/alto, alto en px) del primer dict con medidas válidas; (None, None) si ninguno las trae."""
    for src in srcs:
        if not isinstance(src, dict):
            continue
        try:
            w, h = float(src.get("width") or 0), float(src.get("height") or 0)
            if w > 0 and h > 0:
                return w / h, int(h)
            ar = float(src.get("aspect_ratio") or 0)
            if ar > 0:
                return ar, (int(h) if h > 0 else None)
        except (TypeError, ValueError):
            continue
    return None, None

def site_frame_width(asp, room):
    """Ancho (columnas) del marco de video: 5 filas de alto, ancho IMPAR (9:16 → 7, 1:1 → 9, 16:9 → 17) para que el ► quede en la columna central."""
    try:
        asp = float(asp)
    except (TypeError, ValueError):
        asp = 0.0
    if not asp > 0:
        asp = 16 / 9.0
    asp = max(0.4, min(2.4, asp))
    # el impar más cercano: así el ► y las tarjetas caen en la columna central
    odd = 2 * int(round((MOTIF_ROWS * 2 * asp - 1) / 2.0)) + 1
    room = max(7, int(room))
    return max(7, min(odd, room if room % 2 else room - 1))

SCENE_BADGE_SECS = 0.5                              # s que tarda la etiqueta en resolverse cuando cambia

AUDIO_LABELS = {"m4a": "M4A", "mp3": "MP3", "opus": "OPUS", "ogg": "OGG", "oga": "OGG", "flac": "FLAC", "wav": "WAV",
                "aac": "AAC", "weba": "OPUS", "alac": "ALAC", "aiff": "AIFF"}

RES_LADDER = (144, 240, 360, 480, 720, 1080, 1440, 2160, 4320)

def res_badge(res, asp=None):
    """Resolución real del video, de largo IMPAR (para centrarse en el marco): 360, 480, 720, 1080p, 1440p, 2160p, 4320p."""
    try:
        h = float(res)
    except (TypeError, ValueError):
        return None
    if not h > 0:
        return None
    try:
        asp = float(asp)
    except (TypeError, ValueError):
        asp = 0.0
    w = h * (asp if asp > 0 else 16 / 9.0)
    eff = max(min(w, h), max(w, h) * 9 / 16.0)
    # 1.4.2: se muestra la resolución de verdad, no un cubo (360p ya no sale como 480p)
    near = [r for r in RES_LADDER if abs(eff - r) <= 0.06 * r]
    n = near[0] if near else int(round(min(9999, eff)))
    return "%d" % n if n < 1000 else "%dp" % n

def audio_label(*srcs):
    """Formato corto del primer dict que sea de SOLO audio (M4A, MP3, OPUS…); None si ninguno lo es."""
    for d in srcs:
        if not isinstance(d, dict):
            continue
        ac, vc = str(d.get("acodec") or "none").lower(), str(d.get("vcodec") or "none").lower()
        if ac in ("none", "") or vc not in ("none", ""):
            continue
        ext = str(d.get("ext") or "").lower()
        if ext in AUDIO_LABELS:
            return AUDIO_LABELS[ext]
        for pre, txt in (("opus", "OPUS"), ("mp4a", "AAC"), ("mp3", "MP3"), ("flac", "FLAC"), ("vorbis", "OGG")):
            if ac.startswith(pre):
                return txt
        if ext and ext != "webm":
            return ext.upper()[:4]
    return None

VINFO_SECS = 2.4                                    # 1.1.0: s que se queda cada dato del video en el centro del marco

VCODECS = ((("avc1", "h264"), "H.264"), (("hev1", "hvc1", "hevc", "h265"), "H.265"), (("vp09", "vp9"), "VP9"), (("vp08", "vp8"), "VP8"),
           (("av01", "av1"), "AV1"), (("mp4v",), "MP4"), (("theora",), "THEOR"))

def video_facts(*srcs):
    """{codec, fps, kbps} del video (lo que haya): el códec del primer dict con vcodec de verdad; fps y bitrate del primero que los traiga."""
    out = {}
    for d in srcs:
        if not isinstance(d, dict):
            continue
        vc = str(d.get("vcodec") or "none").lower()
        if str(d.get("vcodec") or "").lower() == "none":
            # 1.3.6: un stream de solo audio no aporta ni fps ni bitrate de video
            continue
        # 1.3.6: el códec supuesto no es un dato
        if "codec" not in out and vc not in ("none", "", "unknown") and not d.get("_guess"):
            out["codec"] = vc.split("+")[0]
        muxed = str(d.get("acodec") or "none").lower() not in ("none", "")
        for key, fields in (("fps", ("fps",)), ("kbps", ("vbr", "tbr"))):
            for fld in fields:
                try:
                    v = float(d.get(fld) or 0)
                except (TypeError, ValueError):
                    continue
                # 1.4.2: tbr de un stream con audio incluye el audio: se le resta, y sin abr no es dato
                if key == "kbps" and fld == "tbr" and muxed:
                    try:
                        v -= float(d.get("abr") or 0) if float(d.get("abr") or 0) > 0 else v
                    except (TypeError, ValueError):
                        v = 0
                if v > 0 and key not in out:
                    out[key] = v
    return out

def codec_label(vc):
    vc = str(vc or "").lower()
    if vc in ("", "none", "unknown"):
        return None
    for keys, txt in VCODECS:
        if any(vc.startswith(k) for k in keys):
            return txt
    return odd_label("".join(ch for ch in vc.split(".")[0] if ch.isalnum()).upper()[:4]) or None

def fps_label(fps, iw=None):
    """Cuadros por segundo en 5 caracteres: 30fps, 08fps, 120Hz (longitud impar, para centrarse)."""
    n = int(round(fps or 0))
    if n < 1 or n > 999:
        return None
    return ("%02dfps" % n) if n < 100 else ("%dHz" % n)

def kbps_label(kbps):
    """Bitrate en 5 caracteres: 066kb, 800kb, 4.5Mb, 012Mb."""
    k = float(kbps or 0)
    if k <= 0:
        return None
    if k < 999.5:
        return "%03dkb" % max(1, round(k))
    m = k / 1000.0
    return ("%.1fMb" % m) if m < 9.95 else ("%03dMb" % min(999, round(m)))

PH_VIDEO = {"res": "\u00bfRES?", "codec": "\u00bfCOD?", "fps": "\u00bfFPS?", "kbps": "\u00bfBIT?"}

PH_AUDIO = {"codec": "\u00bfCOD?", "kbps": "\u00bfBIT?", "hz": "\u00bfKHZ?"}

def ph_text(key):
    """1.7.2: el marcador de «no se pudo leer» en el idioma activo (siempre 5 columnas: impar, centrado). Lo pide al motor de texto como todo lo que dibuja una animación."""
    return ux_text(key)

def vinfo_labels(res, asp, vinfo=None):
    """Lista de etiquetas del video en el orden en que fluyen: resolución, códec, fps, bitrate (con ¿?  lo que no se sabe una vez leído el stream)."""
    vi = vinfo or {}
    ph = bool(vi.get("settled"))                       # ya se intentó leer el stream: lo que falta se marca
    cand = [res_badge(res, asp) or (ph_text(PH_VIDEO["res"]) if ph else None),
            (codec_label(vi.get("codec")) if vi.get("codec") else None) or (ph_text(PH_VIDEO["codec"]) if ph else None),
            (fps_label(vi.get("fps")) if vi.get("fps") else None) or (ph_text(PH_VIDEO["fps"]) if ph else None),
            (kbps_label(vi.get("kbps")) if vi.get("kbps") else None) or (ph_text(PH_VIDEO["kbps"]) if ph else None)]
    return [c for c in cand if c]

def odd_label(txt):
    """Etiqueta de longitud IMPAR (el ecualizador tiene un número impar de columnas): OPUS → OPU, FLAC → FLA."""
    txt = str(txt or "")
    return txt if len(txt) % 2 == 1 else (txt[:-1] if len(txt) > 2 else txt + "0")

def audio_facts(*srcs):
    """{codec, kbps, hz} del audio (acodec, abr y asr del primer dict que los traiga)."""
    out = {}
    for d in srcs:
        if not isinstance(d, dict):
            continue
        ac = str(d.get("acodec") or "none").lower()
        if str(d.get("acodec") or "").lower() == "none":
            continue                                    # 1.4.2: un stream sin audio no aporta bitrate ni muestreo
        # 1.3.6: el códec supuesto no es un dato
        if "codec" not in out and ac not in ("none", "", "unknown") and not d.get("_guess"):
            out["codec"] = ac
        for key, fld in (("kbps", "abr"), ("hz", "asr")):
            try:
                v = float(d.get(fld) or 0)
            except (TypeError, ValueError):
                continue
            if v > 0 and key not in out:
                out[key] = v
    return out

def abr_label(kbps):
    """Bitrate del audio en 5 caracteres: 096kb, 128kb, 320kb, 1.4Mb."""
    k = float(kbps or 0)
    if k <= 0:
        return None
    if k < 999.5:
        return "%03dkb" % round(k)
    # 1.7.5: antes topaba en 9.9Mb
    return ("%.1fMb" % (k / 1000.0)) if k < 9950 else ("%03dMb" % min(999, round(k / 1000.0)))

def asr_label(hz):
    """Frecuencia de muestreo en 5 caracteres: 44.1k, 48kHz, 08kHz."""
    k = float(hz or 0) / 1000.0
    if k <= 0:
        return None
    return ("%.1fk" % k) if abs(k - round(k)) > 0.05 else ("%02dkHz" % min(99, round(k)))

def acodec_label(ac):
    """Formato corto de un acodec de yt-dlp: opus → OPUS, mp4a.40.2 → AAC, ec-3 → EC3…; None si no hay."""
    ac = str(ac or "").lower()
    if ac in ("", "none", "unknown"):
        return None
    for pre, txt in (("opus", "OPUS"), ("mp4a", "AAC"), ("mp3", "MP3"), ("flac", "FLAC"), ("vorbis", "OGG"), ("ac-3", "AC3"), ("ec-3", "EC3")):
        if ac.startswith(pre):
            return txt
    return "".join(ch for ch in ac.split(".")[0] if ch.isalnum()).upper()[:4] or None

def audio_labels(alabel, ainfo=None):
    """Lista de etiquetas del audio en el orden en que fluyen: formato, bitrate, muestreo (todas de longitud impar)."""
    ai = ainfo or {}
    ph = bool(ai.get("settled"))                       # 1.3.6: ya se intentó leer el stream: lo que falta se marca
    cand = [odd_label(alabel) if alabel else (ph_text(PH_AUDIO["codec"]) if ph else None),
            abr_label(ai.get("kbps")) or (ph_text(PH_AUDIO["kbps"]) if ph else None), asr_label(ai.get("hz")) or (ph_text(PH_AUDIO["hz"]) if ph else None)]
    return [c for c in cand if c]

def flow_pick(labels, ta):
    """La etiqueta que toca en el instante ta (relativo al arranque de la rotación)."""
    return labels[int((ta or 0.0) / VINFO_SECS) % len(labels)] if labels else None

def badge_texts(mode, res=None, asp=None, alabel=None, count=0, vinfo=None, ta=None, ainfo=None):
    """Textos de las etiquetas por dibujo: v (dentro del marco del video), a (bajo el ecualizador), l (directo / lista)."""
    # relojes de rotación (arrancan cuando hay dato)
    tv, tau = (ta.get("v"), ta.get("a")) if isinstance(ta, dict) else (ta, ta)
    # 1.1.0: fluye por resolución / códec / fps / bitrate
    out = {"v": flow_pick(vinfo_labels(res, asp, vinfo), tv) or "►"}
    al = audio_labels(alabel or (acodec_label((ainfo or {}).get("codec")) if mode in ("audio", "both") else None), ainfo) \
        if (alabel or mode in ("audio", "both")) else []
    # 1.1.0: también en «video + audio» (bajo las barras)
    if al:
        out["a"] = flow_pick(al, tau)
    if mode == "live":
        out["l"] = "LIVE"
    elif mode == "list" and (count or 0) > 1:
        out["l"] = "\u00d7%d" % int(count)
    return out

def badge_cells(xc, y, text, p, ta, a, b, fd=1.0, room=12):
    """Etiqueta centrada en la columna xc, fila y:"""
    cells, n = {}, len(text or '')
    if not n:
        return cells
    g = lambda k: mix6(a, b, k)
    pad = 1 if room >= n + 2 else 0
    x0, fq = xc - n // 2, int(ta * NOISE_FPS)
    pulse = 0.5 + 0.5 * math.sin(ta * 2.2)
    bg = mix(BLACK, g(0.5), 0.30 * fd)
    for i in range(-pad, n + pad):
        if 0 <= i < n:
            if not GLITCH or p >= 1.0 or p > 0.15 + 0.25 * i:      # 1.7.2: sin glitch el texto sale directo
                ch, col = text[i], mix(g(0.5), (255, 255, 255), 0.55 + 0.25 * pulse)
            else:
                ch, col = SITE_GLITCH[int(_rn(fq * 7 + i * 3 + n) * len(SITE_GLITCH))], mix(BLACK, g(i / float(n)), 0.8)
        else:
            ch, col = " ", (255, 255, 255)
        cells[(x0 + i, y)] = (ch, mix(BLACK, col, fd), bg)
    return cells

def site_video_cells(left, top, fw, a, b, ta, fd, res=None, badge=None):
    """Marco de video de fw × MOTIF_ROWS:"""
    # 1.4.2: el ► queda SIEMPRE en el centro del marco y respira; la tarjeta que cambia (resolución, códec, fps…) va debajo del marco, como la del audio.
    cells = {}
    fw += 1 - fw % 2                                                 # ancho impar: el ► cae en la columna central
    ih, iw = MOTIF_ROWS - 2, fw - 2
    g = lambda k: mix6(a, b, k)

    def c(k):
        return mix(BLACK, g(k), fd)
    tq = ta                                                          # 1.9.8: reloj continuo (antes a 12 cuadros)
    # el marco: esquinas redondeadas y degradado del sitio
    for i in range(fw):
        k = i / float(max(1, fw - 1))
        cells[(left + i, top)] = ("╭" if i == 0 else "╮" if i == fw - 1 else "─", c(k), None)
        cells[(left + i, top + ih + 1)] = ("╰" if i == 0 else "╯" if i == fw - 1 else "─", c(k), None)
    for r in range(1, ih + 1):
        cells[(left, top + r)] = ("│", c(0), None)
        cells[(left + fw - 1, top + r)] = ("│", c(1), None)
    chunk = 3 if (res and res <= 360) else 2 if (res and res <= 480) else 1      # baja resolución: bloques gordos
    pulse = 0.5 + 0.5 * math.sin(ta * 2.2)
    for r in range(ih):
        for i in range(iw):
            k = i / float(max(1, iw - 1))
            xs = (i // chunk) * chunk
            v = (math.sin(xs * 0.55 + tq * 1.4) + math.sin(r * 1.3 - tq * 1.1) + math.sin((xs + r * 2) * 0.35 + tq * 0.8) + 3) / 6.0
            ch = "░▒▓█"[min(3, int(v * 4))]
            col = mix(BLACK, g(k), 0.30 + 0.70 * v)
            if i == iw // 2 and r == ih // 2:                         # ► que respira
                ch = "►"
                col = mix(g(0.5), (255, 255, 255), 0.55 + 0.25 * pulse)
            # 1.2.6: aire a los lados del ► (como un play real)
            elif r == ih // 2 and abs(i - iw // 2) == 1:
                ch = " "
            cells[(left + 1 + i, top + 1 + r)] = (ch, mix(BLACK, col, fd), None)
    # 1.4.2: la tarjeta bajo el marco, centrada en él (sin dato no hay tarjeta)
    if badge is not None and badge[0] != "►":
        cells.update(badge_cells(left + fw // 2, top + BADGE_ROW, badge[0], badge[1], ta, a, b, fd, fw))
    return cells

def site_scene(t, W, y0, a, b, name, mode, f=0, ta=None, vshape=None, badge=None):
    """Un cuadro de la intro:"""
    ta = t if ta is None else ta                # reloj de los movimientos (sigue corriendo aunque la intro espere)
    bd = badge or {}                             # 1.0.7: {"v"|"a"|"l": (texto, avance)}
    u = t / SITE_SECS
    cx = W // 2 + 1
    cells = {}

    def put(x, y, ch, fg, bg=None):
        cells[(int(round(x)), int(round(y)))] = (ch, fg, bg)
    # degradado en 6 pasos: menos cambios de color por fila = menos bytes
    g = lambda k: mix6(a, b, k)

    n = int(round(smooth(u / 0.30) * 14))
    for d in range(-n, n + 1):
        put(cx + d, y0, "─", g((d + 14) / 28.0))
    # chispas de glitch al arrancar (1.7.2: DLPY_GLITCH_EFFECT_ENABLED=0 las quita)
    if GLITCH and u < 0.45:
        for i in range(10):
            if _rn(f * 13 + i) < 0.5 * (1 - u / 0.45):
                put(cx + (_rn(f * 7 + i) - 0.5) * 34, y0 + _rn(f * 3 + i) * 4,
                    SITE_GLITCH[int(_rn(f + i * 5) * len(SITE_GLITCH))], g(_rn(i + f)))
    label = " ".join(name.upper())
    x0 = cx - len(label) // 2
    if u > 0.12:
        for i, ch in enumerate(label):
            if ch != " ":
                ok = u > 0.18 + i * 0.012 or not GLITCH
                put(x0 + i, y0 + 2, ch if ok else SITE_GLITCH[int(_rn(f + i) * len(SITE_GLITCH))],
                    g(i / float(len(label))) if ok else mix(g(0.5), BLACK, 0.5))
    if u > 0.28:
        fd = smooth((u - 0.28) / 0.2)
        tt, y = ta * 12.0, y0 + 4                  # 1.7.6: reloj continuo (antes a MOTIF_FPS)
        asp, res = vshape if vshape else (None, None)

        def c(k):
            return mix(BLACK, g(k), fd)

        def bar_h(i, cnt):
            return (math.sin(tt + i * 0.9) + math.sin(tt * 0.6 + i * 1.7) + 2) / 4

        def eq(yy, cnt, dim=False):
            for i in range(cnt):
                put(cx + 1 - cnt + i * 2, yy, "▁▂▃▄▅▆▇█"[int(round(bar_h(i, cnt) * 7))],
                    mix(BLACK, g(i / float(cnt)), fd * (0.3 if dim else 1.0)))

        def eq_tall(x, cnt, rows, top):                          # barras de varias filas, a la altura del marco
            for i in range(cnt):
                total = int(round(max(0.08, bar_h(i, cnt)) * rows * 8))
                for r in range(rows):
                    fill = total - (rows - 1 - r) * 8
                    if fill > 0:
                        put(x + i * 2, top + r, "█" if fill >= 8 else "▁▂▃▄▅▆▇"[fill - 1],
                            mix(BLACK, g(i / float(cnt)), fd))

        if mode == "audio":
            eq(y + 1, 12)
            eq(y + 2, 12, True)
            if bd.get("a"):
                cells.update(badge_cells(cx, y + 4, bd["a"][0], bd["a"][1], ta, a, b, fd))
        elif mode in ("video", "both"):
            eqw = BOTH_EQW                                       # 5 barras separadas de 2 en 2
            both = mode == "both"
            fw = site_frame_width(asp, (W - 4) - ((eqw + BOTH_GAP) if both else 0))
            left = cx - (fw + ((eqw + BOTH_GAP) if both else 0)) // 2
            cells.update(site_video_cells(left, y, fw, a, b, ta, fd, res, badge=bd.get("v")))
            if both:
                eq_tall(left + fw + BOTH_GAP, 5, BOTH_BARS_ROWS, y)
                # 1.1.0: la etiqueta del audio, centrada bajo las barras (1.4.2: en la fila de la del video)
                if bd.get("a"):
                    cells.update(badge_cells(left + fw + BOTH_GAP + 4, y + BADGE_ROW, bd["a"][0], bd["a"][1], ta, a, b, fd))
        elif mode == "list":
            for i in range(3):
                w = int(round(smooth((u - 0.28 - i * 0.08) / 0.2) * 16))
                put(cx - 10, y + i + 1, "●", c(i / 3.0))
                for j in range(w):
                    put(cx - 8 + j, y + i + 1, "▬", c((j + i * 4) / 24.0))
            if bd.get("l"):
                cells.update(badge_cells(cx, y + 4, bd["l"][0], bd["l"][1], ta, a, b, fd))
        else:                                                # live
            r = int(ta * 9) % 3
            pu = 0.6 + 0.4 * math.sin(ta * 18)
            put(cx, y + 2, "●", mix(BLACK, g(0.2), fd * pu))
            for s_ in (-1, 1):
                put(cx + s_ * (2 + r * 2), y + 2, "(" if s_ < 0 else ")", mix(BLACK, g(0.6), fd * (1 - r / 3.0)))
            if bd.get("l"):
                cells.update(badge_cells(cx, y + 4, bd["l"][0], bd["l"][1], ta, a, b, fd))
    k = max(0.0, min(1.0, (u - 0.6) / 0.4))
    if u >= 0.6:                                             # la escena se deshace mientras vuela la etiqueta
        for key in list(cells):
            if _rn(key[0] * 131 + key[1] * 7 + f * 0.37) < min(1.0, k * 1.6):
                del cells[key]
    return cells, k

SCENE_MORPH = 0.4                                   # s que tarda el texto de estado en cambiar

SCENE_TITLE_MORPH = 0.5                             # s que tarda el sitio en volverse el título del video

SCENE_BRAND = "DLPY"                                # el título durante las actualizaciones y el envío

def scene_mode_parse(raw):
    """1.3.2:"""
    s = str(raw or "").strip().lower().replace(",", ".")
    if s in ("real", "r", "ya", "now"):
        return ("real", None)
    try:
        v = float(s)
    except ValueError:
        return ("loop", None)
    return ("secs", min(60.0, v)) if math.isfinite(v) and v >= 0 else ("loop", None)

UX_SECS_DEFAULT = 2.0

UX_WAIT = ("wait", "espera", "esperar", "loop")

UX_NOW = ("real", "ya", "inmediato", "ahora", "now")

UX_SECS = ("segundos", "seg", "secs", "s")

def ux_mode_parse(raw, secs=None):
    """1.5.1: DLPY_SCENE_RHYTHM en una sola opción → el mismo (modo, segundos) de scene_mode_parse. «wait»: cada escena espera a que acabe su animación ·
    «real»: el transcurso real, cada animación entra conforme al proceso (haya terminado o no la anterior) · un NÚMERO: cada escena dura N s.
    1.7.1: lo vacío o inválido cae en wait (predeterminado; antes real). Siguen valiendo «espera», «ya», «segundos» (con `secs` = DLPY_UX_SECS) y el DLPY_SCENE_MODE de antes."""
    s_ = str(raw or "").strip().lower()
    if s_ in UX_WAIT:
        return ("loop", None)
    if s_ in UX_NOW:
        return ("real", None)
    if s_ in UX_SECS:
        mode = scene_mode_parse(secs if str(secs or "").strip() else UX_SECS_DEFAULT)
        return mode if mode[0] == "secs" else ("secs", UX_SECS_DEFAULT)
    mode = scene_mode_parse(s_)
    return mode      # 1.7.1: vacío o inválido = wait (predeterminado, igual que CONFIG_OPTIONS); real solo si se pide

SCENE_MODE = ux_mode_parse(env_get("DLPY_SCENE_RHYTHM"))

def topbar_parse(raw):
    """1.8.3: DLPY_TOP_BAR_FIELDS → tupla ordenada de campos ('D','T','V') o vacía si está apagada.
    0/off/no = oculta · 1/on/all = DTV · cualquier secuencia de D/T/V fija contenido y orden.
    1.9.4: la N (icono de red ⇅) ya no es de la franja superior: ahora es una letra de DLPY_BOTTOM_BAR_FIELDS."""
    s = str(raw if raw is not None else "").strip().lower()
    if s in ("", "0", "off", "no", "false", "none", "oculto", "hide", "hidden"):
        return ()
    if s in ("1", "on", "yes", "true", "all", "si", "sí", "s"):
        return ("D", "T", "V")
    order = []
    for ch in s.upper():
        if ch in ("D", "T", "V") and ch not in order:
            order.append(ch)
    return tuple(order)

def bottom_bar_parse(raw):
    """1.9.2: DLPY_BOTTOM_BAR_FIELDS → campos E (errores) y A (advertencias), en el orden solicitado.
    1.9.4: suma N (icono de red ⇅, que antes vivía en la franja superior); 1/on/all = EAN."""
    s = str(raw if raw is not None else "").strip().lower()
    if s in ("", "0", "off", "no", "false", "none", "oculto", "hide", "hidden"):
        return ()
    if s in ("1", "on", "yes", "true", "all", "si", "sí", "s"):
        return ("E", "A", "N")
    order = []
    for ch in s.upper():
        if ch in ("E", "A", "N") and ch not in order:
            order.append(ch)
    return tuple(order)

TOPBAR = topbar_parse(env_get("DLPY_TOP_BAR_FIELDS"))

BOTTOMBAR = bottom_bar_parse(env_get("DLPY_BOTTOM_BAR_FIELDS", "1"))   # activa por defecto (con la variable vacía o en 0 se apaga)

NET_ICON = "⇅"

TOPBAR_SEP = "  ·  "

TOPBAR_DROP = ("D", "T", "V")

BOTTOMBAR_DROP = ("N", "A", "E")

BOTTOMBAR_GLYPHS = {"E": "✕", "A": "!", "N": NET_ICON}

def topbar_line(now=None, width=None):
    """1.8.3: texto de la franja superior según TOPBAR (orden visual); `now` permite probar el reloj sin estado global.
    `width` es el ancho interior tras los márgenes."""
    if not TOPBAR:
        return ""
    now = time.time() if now is None else now
    secs = int(max(0.0, now - BOOT_T0))
    parts = []
    for k in TOPBAR:
        if k == "D":
            parts.append((k, device_label()))
        elif k == "T":
            parts.append((k, f"{secs // 60}:{secs % 60:02d}"))
        elif k == "V":
            parts.append((k, f"v{HOST_VERSION}"))
    if width is not None:
        for drop in TOPBAR_DROP:
            if len(parts) <= 1 or dwidth(TOPBAR_SEP.join(s_ for _k, s_ in parts)) <= width:
                break
            parts = [(k, s_) for k, s_ in parts if k != drop]
    return TOPBAR_SEP.join(s_ for _k, s_ in parts)

def topbar_visible(S):
    """¿Se dibuja la franja superior? Aparece en cuanto empieza a analizarse el enlace y, además, siempre que la escena
    ya no sea la de D L P Y (marca); durante D L P Y (comprobar actualizaciones, etc.) queda oculta."""
    if not TOPBAR:
        return False
    label = str(S.get("label") or "")
    if S.get("past_dl") or label.startswith(("Analizando", "Descargando")):
        return True
    return not S.get("brand")

def scene_topbar_cells(W, text, row=2, highlights=None):
    """Pinta una franja centrada, discreta y con margen lateral; solo los iconos activos se iluminan.
    La fila 1 queda libre para respetar el margen superior de iOS. N y E/A (franja inferior) usan el mismo fundido gris → blanco."""
    cells = {}
    text = str(text or "")
    if not text or W is None or W < 12 or dwidth(text) > W - 4:
        return cells
    x0 = max(2, (W // 2 + 1) - dwidth(text) // 2)
    base = SCENE_GRAY if SCENE_CALM else SCENE_DIM
    put_text(cells, x0, row, text, base, lo=2, hi=W - 1)
    for icon, amount in (highlights or {}).items():
        level = max(0.0, min(1.0, float(amount or 0.0)))
        pos = text.find(str(icon)) if level > 0.0 else -1
        if pos >= 0:
            put_text(cells, x0 + dwidth(text[:pos]), row, str(icon), mix6(base, SCENE_WHITE, level), lo=2, hi=W - 1)
    return cells

def topbar_cells(W):
    """1.9.2: ajusta la franja al ancho interior W-4 y deja dos columnas de protección a izquierda/derecha."""
    return scene_topbar_cells(W, topbar_line(width=None if W is None else W - 4), row=2)

def bottom_bar_line(width=None):
    """1.9.2: texto de la franja inferior (✕ errores · ! advertencias, sin cifras) y ajuste a la anchura disponible."""
    if not BOTTOMBAR:
        return ""
    # solo los iconos: el pulso avisa de cada evento (el contador interno sigue en DIAGNOSTICS)
    parts = [(k, BOTTOMBAR_GLYPHS[k]) for k in BOTTOMBAR]
    if width is not None:
        for drop in BOTTOMBAR_DROP:
            if len(parts) <= 1 or dwidth(TOPBAR_SEP.join(v for _k, v in parts)) <= width:
                break
            parts = [(k, v) for k, v in parts if k != drop]
    return TOPBAR_SEP.join(v for _k, v in parts)

def scene_bottom_bar_row(y0, extra_content=False):
    """Fila inferior: deja una fila libre bajo estado, aviso de conversión o pregunta con cuenta atrás."""
    return int(y0) + SCENE_STATUS_ROW + (3 if extra_content else 2)

def scene_bottom_bar_cells(W, row):
    """Franja inferior centrada y gris; E/A solo pasan a blanco al registrar un evento y la N (red) al conectar a internet; luego vuelven al gris."""
    if not BOTTOMBAR:
        return {}
    active = {BOTTOMBAR_GLYPHS[kind]: (net_level() if kind == "N" else diagnostic_level(kind)) for kind in BOTTOMBAR}
    return scene_topbar_cells(W, bottom_bar_line(width=None if W is None else W - 4),
                              row=row, highlights=active)

def bottom_bar_cells(W, row):
    return scene_bottom_bar_cells(W, row)

OUTRO = _flag_env("DLPY_SCENE_OUTRO_ENABLED", True)

SCENE_OUTRO_SECS = 0.9                              # s que tarda la escena en cerrarse hacia el centro

SCENE_LAG_MOTIF = 0.05

SCENE_LAG_LABEL = 0.18                              # 1.0.6: s que espera el texto de estado tras el título (cascada)

SCENE_BAR_RATE = 3.9

SCENE_ASP_RATE = 3.1                                # 1.0.6: suavizado de la proporción del marco (1/s)

SCENE_BUSY_RATE = 9.0                               # 1.0.6: fundido barrido de espera ↔ barra de progreso (1/s)

SCENE_WHITE, SCENE_GRAY, SCENE_DIM = (236, 236, 242), (154, 154, 168), (96, 96, 110)

SCENE_CALM = _flag_env("DLPY_TEXT_CALM_MODE", False)     # 1.4.4: 1 = sin ruido en los cambios de texto y texto tenue más claro

SCENE_PP = (("merg", "Uniendo pistas"), ("convert", "Convirtiendo"), ("remux", "Convirtiendo"),
            ("apple", "Convirtiendo"), ("track", "Ajustando pistas"))

class _SceneMute:
    """Envoltura de sys.stdout:"""

    def __init__(self, inner):
        self._inner = inner
        self.open = False

    def write(self, text):
        if self.open:
            return self._inner.write(text)
        return len(text) if text else 0

    def writelines(self, lines):
        for ln in lines:
            self.write(ln)

    def flush(self):
        if self.open:
            return self._inner.flush()
        return None

    def __getattr__(self, name):
        return getattr(self._inner, name)

class _SceneErrMute:
    """1.0.8:"""

    def __init__(self, inner):
        self._inner = inner
        self.open = False
        self._buf = ""
        self._lock = threading.Lock()

    def write(self, text):
        if self.open:
            return self._inner.write(text)
        if not text:
            return 0
        with self._lock:
            *lines, self._buf = (self._buf + str(text).replace("\r", "\n")).split("\n")
        for ln in lines:
            ln = _ANSI_RE.sub("", ln).strip()
            if ln:
                log_shortcutmode_stderr("stderr: " + ln)
        return len(text)

    def writelines(self, lines):
        for ln in lines:
            self.write(ln)

    def drain(self):
        """Lo que quedó sin salto de línea también va al log."""
        with self._lock:
            rest, self._buf = _ANSI_RE.sub("", self._buf).strip(), ""
        if rest:
            log_shortcutmode_stderr("stderr: " + rest)

    def flush(self):
        if self.open:
            return self._inner.flush()
        return None

    def __getattr__(self, name):
        return getattr(self._inner, name)

def frame_gap(t, fps):
    """1.9.8: s hasta el siguiente límite de cuadro de un reloj que lleva `t` s a `fps` cuadros por segundo (entre 1 ms y un cuadro; 0.0.3: antes 0,5 ms)."""
    fps = max(1.0, float(fps))
    return max(0.001, min(1.0 / fps, (math.floor(t * fps + 1e-9) + 1) / fps - t))

def scene_fps_cap(fps, cost):
    """0.0.3: los cuadros por segundo que el hilo puede sostener: `fps` si pintar un cuadro (`cost` s, media reciente) cabe en FPS_DUTY del tiempo; si no, los que
    quepan (nunca menos de 10). Asi 120 Hz no le quita CPU a la descarga ni llena la terminal: lo que no alcanza se baja solo y sube de nuevo cuando el dibujo es ligero."""
    if cost <= 0.0:
        return float(fps)
    return max(10.0, min(float(fps), FPS_DUTY / cost))

def scene_refresh_slice(st, ymax, fps, period=0.35):
    """1.9.8: repintado de seguridad repartido: invalida unas pocas filas por cuadro (en rotación) y todas en `period` s, en vez de borrar toda la pantalla de golpe."""
    n = max(1, int(math.ceil(ymax / max(1.0, period * fps))))
    cur = st.get("rcur", 1)
    for i in range(n):
        st["rows"].pop((cur - 1 + i) % max(1, ymax) + 1, None)
    st["rcur"] = (cur - 1 + n) % max(1, ymax) + 1
    return n

def scene_ease(cur, tgt, rate, dt):
    """1.0.6:"""
    dt = max(0.0, min(0.25, float(dt)))
    return cur + (tgt - cur) * (1.0 - math.exp(-rate * dt))

def scene_pp_text(name):
    """Texto de estado de un procesador de yt-dlp."""
    low = str(name or "").lower()
    for key, text in SCENE_PP:
        if key in low:
            # 1.6.9: las pistas que se unen, con sus códecs reales (los leídos del stream)
            if key == "merg":
                got = [codec_name((SCENE.get(k) or {}).get("codec")) for k in ("vinfo", "ainfo")]
                got = [g for g in got if g]
                if got:
                    return text + " · " + " + ".join(got)  # 1.9.8: la clave (la escena traduce al pintar); antes ya traducida y el dibujo no la reconocía con otro idioma
            return text  # 1.9.8: la clave en español; la escena la traduce al pintar (t_status)
    return "Finalizando"

STREAM_KINDS = {}

def stream_kinds(d):
    """1.3.6:"""
    info = (d or {}).get("info_dict") or {}
    k = STREAM_KINDS.get(str(info.get("format_id") or ""))
    if k:
        return k
    if info.get("height") or info.get("width") or has(info.get("vcodec")):
        return ("video", "audio") if has(info.get("acodec")) and has(info.get("vcodec")) else ("video",)
    return ("audio",)

def scene_kind(d):
    """«video» o «audio» según el stream que informa el hook de yt-dlp (1.3.6: un stream con los dos cuenta como video)."""
    return "video" if "video" in stream_kinds(d) else "audio"

def scene_cols(text, cx):
    """{columna:"""
    text = "".join(ch if ch.isprintable() else " " for ch in str(text))
    text = "".join(ch for ch in text if ch == " " or dwidth(ch) > 0)
    x = cx - dwidth(text) // 2
    out = {}
    for ch in text:
        w = dwidth(ch)
        if ch != " ":
            out[x] = ch
            if w == 2:
                out[x + 1] = "\0"
        x += w
    return out

FLOW_LEAVE, FLOW_LAND = 0.12, 0.86

FLOW_ROLES = (("line", "─│╭╮╰╯├┤┬┴┼━┃═║╔╗╚╝┌┐└┘▬"), ("shade", "░▒▓"), ("bar", "▁▂▃▄▅▆▇█▀▌▐"),
              ("dot", "●•·○◦∙()›"), ("mark", "►✓✗♪"))

FLOW_ROLE_OF = {ch: role for role, chars in FLOW_ROLES for ch in chars}

FLOW_LEAD = {"line": 0.0, "bar": 0.3, "shade": 0.45, "dot": 0.6, "mark": 0.8, "text": 1.0}

def flow_curve(x1, y1, x2, y2, n=48):
    """Curva cubic-bezier(x1, y1, x2, y2) en una tabla de n pasos; devuelve f(t) (t de 0 a 1, f(0) = 0, f(1) = 1). Cuesta lo mismo que una tabla."""
    def bz(s_, p1, p2):
        return 3 * (1 - s_) ** 2 * s_ * p1 + 3 * (1 - s_) * s_ * s_ * p2 + s_ ** 3
    xs, ys = [bz(i / 200.0, x1, x2) for i in range(201)], [bz(i / 200.0, y1, y2) for i in range(201)]
    tab, j = [], 0
    for i in range(n + 1):
        x = i / float(n)
        while j < 199 and xs[j + 1] < x:
            j += 1
        span = xs[j + 1] - xs[j]
        tab.append(ys[j] + (ys[j + 1] - ys[j]) * (0.0 if span <= 0 else max(0.0, min(1.0, (x - xs[j]) / span))))
    tab[0], tab[-1] = 0.0, 1.0

    def f(t):
        if t <= 0.0:
            return 0.0
        if t >= 1.0:
            return 1.0
        q = t * n
        i = int(q)
        return tab[i] + (tab[i + 1] - tab[i]) * (q - i)
    return f

FLOW_EASE = flow_curve(0.3, 0.0, 0.2, 1.0)         # arranca sin brusquedad y frena suave: lo que llega, llega asentado

MOTION_QUICK, MOTION_BASE, MOTION_SLOW = 0.2, 0.34, 0.6

def smooth(x):
    """Entrada y salida suaves (0→1). 1.7.6: una sola curva para toda la escena (FLOW_EASE, la del morph y la del carril; antes smoothstep) y, con ella, en la zona UX."""
    return FLOW_EASE(max(0.0, min(1.0, x)))

def flow_role(ch, dense=False):
    """Papel de una celda: line · shade · bar · dot · mark · text. Un █ pegado a otra celda en la fila es relleno (sombra), no una barra."""
    if dense and ch == "█":
        return "shade"
    return FLOW_ROLE_OF.get(ch, "text")

def _flow_pair(A, B):
    """Parejas (a, b) entre dos listas ya ordenadas: por cuantiles. Cubre TODAS las de A y TODAS las de B (la lista más larga se reparte)."""
    n, m = len(A), len(B)
    if n >= m:
        return [(A[i], B[i * m // n]) for i in range(n)]
    return [(A[j * n // m], B[j]) for j in range(m)]

def flow_plan(old, new):
    """FLIP, el «medir»: del dibujo viejo y del nuevo (dict celda → (glifo, color, fondo)) saca los actores (origen, destino, papel, tiempos).
    Pura y repetible. Se mide una vez por transición y se reutiliza en cada cuadro."""
    ko = sorted(k for k, c in old.items() if c[0] and dwidth(c[0]) == 1)
    kn = sorted(k for k, c in new.items() if c[0] and dwidth(c[0]) == 1)
    go, gn = {}, {}
    for keys, cells, grp in ((ko, old, go), (kn, new, gn)):
        for k in keys:
            dense = cells[k][0] == "█" and ((k[0] - 1, k[1]) in cells or (k[0] + 1, k[1]) in cells)
            grp.setdefault(flow_role(cells[k][0], dense), []).append(k)
    pairs, lo, ln = [], [], []
    # en este orden: el resultado no depende del azar de los conjuntos
    for role in FLOW_LEAD:
        A, B = go.get(role, []), gn.get(role, [])
        if A and B:
            pairs += [(s_, d_, role) for s_, d_ in _flow_pair(A, B)]
        else:
            lo += A
            ln += B
    # un papel que el otro dibujo no tiene: fluye hacia lo que haya (por cuantiles)
    if lo and kn:
        pairs += [(s_, kn[i * len(kn) // len(lo)], flow_role(old[s_][0])) for i, s_ in enumerate(sorted(lo))]
    if ln and ko:
        pairs += [(ko[j * len(ko) // len(ln)], d_, flow_role(new[d_][0])) for j, d_ in enumerate(sorted(ln))]
    xs = [k[0] for k in list(old) + list(new)] or [0]
    ys = [k[1] for k in list(old) + list(new)] or [0]
    mid, half = (min(xs) + max(xs)) / 2.0, max(1.0, (max(xs) - min(xs)) / 2.0)
    acts = []
    for (sx, sy), (dx, dy), role in pairs:
        dist = math.hypot(dx - sx, 2.0 * (dy - sy))           # una celda mide ~1×2
        rn = _rn(sx * 7.3 + sy * 3.1 + dx * 1.7 + dy * 5.9)
        stagger = 0.5 * min(1.0, abs(sx - mid) / half) + 0.2 * FLOW_LEAD[role] + 0.3 * rn
        dur = 0.5 + 0.12 * min(1.0, dist / 12.0)              # lo que viaja más lejos tarda un poco más
        arc = (1 if rn < 0.5 else -1) if dist >= 6.0 else 0
        acts.append((sx, sy, dx, dy, (1.0 - dur) * stagger, dur, arc, (sx, sy) != (dx, dy), flow_role(old[(sx, sy)][0]) == flow_role(new[(dx, dy)][0])))
    # el reparto de tiempos ocupa TODA la transición: lo último llega justo en p = 1
    if acts:
        end = max(t[4] + t[5] * (FLOW_LAND if t[7] else 0.65) for t in acts)
        acts = [(t[0], t[1], t[2], t[3], t[4] / end, t[5] / end) + t[6:] for t in acts]
    acts.sort(key=lambda t: (t[7], t[4]))                     # primero lo que se queda quieto, luego lo que viaja
    return {"old": dict(old), "new": dict(new), "acts": acts, "src": {(a_[0], a_[1]) for a_ in acts}, "dst": {(a_[2], a_[3]) for a_ in acts},
            "rows": (min(ys), max(ys))}

def _flow_noise(f, x, y, a, b):
    """Un carácter de ruido (el de siempre) para la celda (x, y)."""
    return (SITE_GLITCH[int(_rn(f + x * 5 + y * 3) * len(SITE_GLITCH))], mix(mix(a, b, 0.5), BLACK, 0.45), None)

def flow_frame(plan, old, new, p, f, a, b):
    """FLIP, el «reproducir»: el cuadro de la transición en p (0–1). `old` y `new` son los dibujos VIVOS de este cuadro (los del plan se usan
    solo si falta una celda). En 0 devuelve el viejo y en 1 el nuevo, tal cual."""
    if p <= 0.0:
        return dict(old)
    if p >= 1.0:
        return dict(new)
    po, pn, (ymin, ymax) = plan["old"], plan["new"], plan["rows"]
    wait, fly, land = {}, {}, {}
    # lo que el dibujo viejo tiene ahora y el plan no midió: se apaga con ruido
    for k, c in old.items():
        if k not in plan["src"]:
            th = 0.05 + 0.40 * _rn(k[0] * 3.7 + k[1] * 11.3)
            if p < th:
                wait[k] = c
            # 1.7.2: sin glitch la celda vieja se apaga directa
            elif GLITCH and p < th + 0.12 and c[0] and dwidth(c[0]) == 1:
                wait[k] = _flow_noise(f, k[0], k[1], a, b)
    # y lo que el nuevo tiene ahora y el plan no midió: entra con ruido
    for k, c in new.items():
        if k not in plan["dst"]:
            th = 0.55 + 0.33 * _rn(k[0] * 5.1 + k[1] * 2.3)
            if p >= th + (0.12 if GLITCH else 0.0):
                land[k] = c
            elif p >= th and c[0] and dwidth(c[0]) == 1:
                land[k] = _flow_noise(f, k[0], k[1], a, b)
    for sx, sy, dx, dy, delay, dur, arc, moves, keep in plan["acts"]:
        u = (p - delay) / dur
        co, cn = old.get((sx, sy)) or po[(sx, sy)], new.get((dx, dy)) or pn[(dx, dy)]
        if not moves:                                         # no cambia de sitio: se reescribe en su lugar
            if u <= 0.0:
                wait[(sx, sy)] = co
            elif u >= 1.0:
                land[(dx, dy)] = cn
            else:
                e = FLOW_EASE(u)
                if co[0] == cn[0]:
                    wait[(sx, sy)] = (cn[0], mix(co[1], cn[1], e), cn[2] if u >= 0.5 else co[2])
                # 1.7.2: sin glitch la vieja se queda hasta la mitad y entra la nueva
                elif u < (0.35 if GLITCH else 0.5):
                    wait[(sx, sy)] = co
                elif GLITCH and u < 0.65:
                    wait[(sx, sy)] = _flow_noise(f, sx, sy, a, b)
                else:
                    wait[(sx, sy)] = (cn[0], mix(co[1], cn[1], e), cn[2])
            continue
        if u <= FLOW_LEAVE:
            wait[(sx, sy)] = co
        elif u >= FLOW_LAND:
            land[(dx, dy)] = cn
        else:
            q = (u - FLOW_LEAVE) / (FLOW_LAND - FLOW_LEAVE)
            e = FLOW_EASE(q)
            xx = int(round(sx + (dx - sx) * e))
            yy = int(round(sy + (dy - sy) * e + arc * math.sin(math.pi * e)))
            glow = math.sin(math.pi * q)
            # mismo papel: viaja con su glifo
            ink = (co[0] if q < 0.5 else cn[0]) if keep else ("•" if (q < 0.1 or q > 0.9) else "·")
            fly[(xx, max(ymin, min(ymax, yy)))] = (ink, mix(mix(co[1], cn[1], e), WHITE, 0.35 * glow), None)
    out = dict(wait)
    out.update(fly)
    out.update(land)
    return out

def scene_flow_step(st, slot, old, new, p, f, a, b):
    """Un cuadro de la transición `slot` de la escena: el plan se mide en el primer cuadro con p > 0 y se reutiliza hasta que acaba
    (st[slot] = None al empezar otra). Si la transición se revierte a mitad, el mismo plan se recorre al revés (flow["rev"])."""
    if p <= 0.0:
        return dict(old)
    if p >= 1.0:
        return dict(new)
    fl = st.get(slot)
    if fl is None:
        fl = st[slot] = {"plan": flow_plan(old, new), "rev": False}
    if fl["rev"]:
        return flow_frame(fl["plan"], new, old, 1.0 - p, f, a, b)
    return flow_frame(fl["plan"], old, new, p, f, a, b)

_MORPH_MEMO = {}

def morph_slides(c0, c1):
    """1.4.2: [(x0, x1, carácter)]: los caracteres que el texto nuevo comparte con el viejo (tramos de 2 o más, o a ≤ 2 columnas) y que
    se deslizan a su sitio. Sin anchos dobles ni espacios. Repetible (se guarda el último resultado: el texto no cambia entre cuadros)."""
    key = (tuple(sorted(c0.items())), tuple(sorted(c1.items())))
    hit = _MORPH_MEMO.get(key)
    if hit is not None:
        return hit
    s0 = [(x, ch) for x, ch in sorted(c0.items()) if ch != "\0" and dwidth(ch) == 1]
    s1 = [(x, ch) for x, ch in sorted(c1.items()) if ch != "\0" and dwidth(ch) == 1]
    out = []
    if s0 and s1:
        import difflib
        sm = difflib.SequenceMatcher(None, [ch for _x, ch in s0], [ch for _x, ch in s1], autojunk=False)
        for i, j, n in sm.get_matching_blocks():
            for k in range(n):
                if n >= 2 or abs(s0[i + k][0] - s1[j + k][0]) <= 2:
                    out.append((s0[i + k][0], s1[j + k][0], s0[i + k][1]))
    if len(_MORPH_MEMO) > 16:
        _MORPH_MEMO.clear()
    _MORPH_MEMO[key] = out
    return out

def scene_morph(c0, c1, p, f):
    """Transición de un texto a otro (p de 0 a 1). 1.4.2: los caracteres que el texto nuevo comparte con el viejo se DESLIZAN a su sitio
    (kind 0 hasta la mitad, 2 después); el resto sale del ruido como antes."""
    out = {}
    # 1.4.4: modo calmado: el texto viejo se queda y el nuevo entra de golpe, sin ruido
    if SCENE_CALM and 0 < p < 1:
        src, kind = (c0, 0) if p < 0.5 else (c1, 2)
        return {x: ("" if ch == "\0" else ch, kind) for x, ch in src.items() if ch is not None}
    sl = morph_slides(c0, c1) if 0 < p < 1 else []
    gone, came = {x0 for x0, _x1, _ch in sl}, {x1 for _x0, x1, _ch in sl}
    c0r, c1r = {x: ch for x, ch in c0.items() if x not in gone}, {x: ch for x, ch in c1.items() if x not in came}
    for x in set(c0r) | set(c1r):
        a, b = c0r.get(x), c1r.get(x)
        xx = x - 1 if "\0" in (a, b) else x          # los caracteres anchos cambian juntos
        th = _rn(xx * 3.7) * 0.55
        if p <= 0 or p < th:
            ch, kind = a, 0
        elif GLITCH and p < th + 0.35 and p < 1:
            ch, kind = SITE_GLITCH[int(_rn(f + xx * 5) * len(SITE_GLITCH))], 1
        else:
            ch, kind = b, 2
        if ch is None:
            continue
        if ch == "\0":
            ch = " " if kind == 1 else ""
        out[x] = (ch, kind)
    e = FLOW_EASE(min(1.0, p / 0.85))
    for x0, x1, ch in sl:
        out[x0 + int(round((x1 - x0) * e))] = (ch, 0 if p < 0.5 else 2)
    return out

def scene_title_spec(S):
    """Qué muestra la línea del título:"""
    if S.get("brand"):
        return ("grad", " ".join(SCENE_BRAND))
    cv = S.get("conv")
    # 1.0.0: mientras convierte, el título es el códec («H E V C»)
    if cv and cv.get("end") is None and cv.get("codec"):
        return ("grad", " ".join(ch for ch in str(cv["codec"]).upper() if ch not in ". "))
    if S.get("title_raw"):
        return ("white", S["title_raw"])
    return ("grad", " ".join(str(S.get("name") or "").upper()))

def outro_ease(k):
    """1.9.8: curva del cierre / reapertura de la escena: mitad lineal, mitad la curva única (smooth); 0 y 1 fijos, nunca baja y no se pasa de 0–1."""
    k = max(0.0, min(1.0, float(k)))
    return 0.5 * k + 0.5 * smooth(k)

def scene_dissolve(cells, k, cx, W, a, b):
    """La escena se cierra hacia el centro (k de 0 a 1):"""
    if k <= 0:
        return cells
    out, half = {}, max(1.0, W / 2.0)
    for (x, y), c in cells.items():
        xx = x - 1 if c[0] == "" else x                              # la columna cubierta sigue a su carácter ancho
        edge = min(1.0, abs(xx - cx) / half)                         # 0 = centro … 1 = borde
        off = 0.08 + 0.52 * (1.0 - edge) + 0.30 * _rn(xx * 131 + y * 7 + 3.1)       # cuándo se apaga (0.08–0.9)
        if k >= off:
            continue
        # justo antes de apagarse pasa por ruido (1.7.2: DLPY_GLITCH_EFFECT_ENABLED=0 lo salta)
        if GLITCH and k >= off - 0.22:
            g = mix(a, b, max(0.0, min(1.0, (xx - 1) / float(max(1, W - 2)))))
            ch = SITE_GLITCH[int(_rn(xx * 17 + y * 5 + int(k * 40)) * len(SITE_GLITCH))]
            out[(x, y)] = ("" if c[0] == "" else ch, mix(BLACK, g, 0.55), None)
        else:
            out[(x, y)] = c
    return out

def scene_chip_text(x):
    """Texto de un chip de la escena de conversión: mayúsculas, en el idioma activo y como mucho CHIP_COLS columnas reales («webm» → «WEBM»). 1.7.1: lo resuelve ux_chip."""
    return ux_chip(x)

MOTIF_LABELS = (("check", ("Revisando",)), ("merge", ("Uniendo", "Ajustando")), ("save", ("Guardado",)),
                ("subst", ("Sustituyendo",)), ("clean", ("Limpiando",)), ("empty", ("Vaciando",)), ("download", ("Descargando",)))

def scene_motif_kind(S):
    """Qué dibujo ocupa el centro:"""
    label = str(S.get("label") or "")
    wl = S.get("welcome")
    if wl and wl.get("kind") in WELCOME_KINDS and not S.get("last_error"):
        # 1.2.9: primera ejecución / actualizado (mandan sobre D L P Y) (1.6.5: + versión anterior y misma versión)
        return wl["kind"]
    # 1.9.8: el envío (y «Abriendo con view») es su propio dibujo, con o sin D L P Y: D L P Y es solo del arranque y de las actualizaciones
    if label.startswith(("Enviando", "Abriendo")) and not S.get("last_error"):
        return "send"
    if S.get("brand"):
        return "dlpy"
    cv = S.get("conv")
    if cv and cv.get("end") is None:
        return "conv"
    if S.get("ask"):
        # 1.1.9: esperando el Enter de la conversión (1.4.2: o de sustituir un archivo)
        return "replace" if (S["ask"] or {}).get("kind") == "replace" else "ask"
    for kind, prefixes in MOTIF_LABELS:                               # 1.4.1: una tabla, no una cadena de «if»
        if label.startswith(prefixes):
            # 1.4.6: descarga, unión y guardado son tarjetas del mismo carril
            return "rail" if kind in RAIL_KINDS else kind
    # 1.4.5: tras la descarga el sitio no vuelve: queda el Pulso entre motivos
    return "idle" if S.get("past_dl") else None

def _conv_geo(W, src, dst):
    """1.2.1:"""
    src, dst = str(src or "?"), str(dst or "?")
    # 1.7.1: ancho real; con poco ancho los chips se acortan (antes siempre 6 caracteres)
    cols = CHIP_COLS
    while True:
        s_, d_ = clip_text(src, cols), clip_text(dst, cols)
        sw, dw = max(7, dwidth(s_) + 4), max(7, dwidth(d_) + 4)
        gap = min(17, max(7, W - 4 - sw - dw))
        if sw + gap + dw <= W - 3 or cols <= 3:
            break
        cols -= 1
    src, dst = s_, d_
    gap -= 1 - gap % 2
    return src, dst, sw, dw, gap

def scene_enter_chip(gap):
    """1.7.1: (texto, ancho) del chip de la tecla Enter en la vía: su nombre en el idioma activo si cabe en la vía; si no, «↵»."""
    ek = ux_enter_key()
    key = ek if gap >= dwidth(ek) + 8 else "↵"
    return key, dwidth(key) + 4

def _conv_near(heads, c, w):
    """1.2.1: cuánto está cerca de la celda `c` el paquete más próximo (1 encima, 0 a `w` celdas o más)."""
    return max([max(0.0, 1.0 - abs(h - c) / w) for h in heads] or [0.0])

def _conv_lane(cells, x0, y, gap, heads, p, g, skip=(), fade=1.0, whole=False):
    """1.2.1:"""
    j0 = gap // 2
    rank = {}
    for h in heads:
        sz = max(0, min(2, int(3.0 * h / float(max(1, gap)))))       # 0 chico · 1 mediano • 2 grande ●
        for n in range(3):
            jj = int(h) - n
            if 0 <= jj < gap and (jj not in rank or n < rank[jj][0]):
                rank[jj] = (n, sz)
    cnt = float(max(1, gap - j0))
    for j in range(gap):
        if j in skip:
            continue
        rk = rank.get(j)
        n = None if rk is None else rk[0]
        gl = None if rk is None else "·•●"[max(0, rk[1] - rk[0])]    # la cola es un tamaño menor en cada paso
        if whole and p is not None:                                  # 1.2.8: el avance recorre toda la vía
            kw_ = j / float(max(1, gap - 1))
            fw_ = max(0.0, min(1.0, p * gap - j)) * fade
            if n is not None:
                cells[(x0 + j, y)] = (gl, (mix(mix(OLD_TONE, g(kw_), kw_), WHITE, 0.55), mix(BLACK, mix(OLD_TONE, g(kw_), kw_), 0.85), mix(BLACK, mix(OLD_TONE, g(kw_), kw_), 0.55))[n], None)
            elif fw_ > 0.0:
                # punto chico y brillante: así el paquete (· • ●) se distingue
                cells[(x0 + j, y)] = ("·", mix(BLACK, mix(OLD_TONE, g(kw_), kw_), 0.35 + 0.65 * fw_), None)
            else:
                cells[(x0 + j, y)] = ("·", mix(BLACK, OLD_TONE, 0.35), None)
            continue
        if j < j0:                                                   # primera mitad: grises
            if n is None:
                cells[(x0 + j, y)] = ("·", mix(BLACK, OLD_TONE, 0.35), None)
            else:
                cells[(x0 + j, y)] = (gl, (mix(OLD_TONE, WHITE, 0.3), mix(BLACK, OLD_TONE, 0.8), mix(BLACK, OLD_TONE, 0.5))[n], None)
            continue
        # segunda mitad: refinados, con el degradado del sitio
        m = j - j0
        k = m / max(1.0, cnt - 1.0)
        f = 0.0 if p is None else max(0.0, min(1.0, p * cnt - m)) * fade
        if n is not None:
            cells[(x0 + j, y)] = (gl, (mix(g(k), WHITE, 0.55), mix(BLACK, g(k), 0.85), mix(BLACK, g(k), 0.55))[n], None)
        elif f > 0.0:
            cells[(x0 + j, y)] = ("•", mix(BLACK, g(k), 0.22 + 0.4 * f), None)
        else:
            cells[(x0 + j, y)] = ("·", mix(BLACK, OLD_TONE, 0.35), None)
    return cells

def scene_conv_cells(W, y0, a, b, lt, src, dst, pct=None, key_fade=None, fill=None, fast=False):
    """Escena de conversión (1.2.1), filas y0+5 … y0+7. 1.6.4: sin paquetes que cruzan la vía en loop (gastaban cuadros): los PUNTOS de la vía se
    pintan de origen a destino según el avance real (`fill`, de 0 a 1 y ya suavizado por quien dibuja; sin él, el `pct` de ffmpeg); al llegar a
    100 % la vía queda llena y el destino destella. Sin avance conocido la vía queda tenue (con `fast`, quieta; si no, un punto la recorre despacio).
    `fast` (convert_fast_anim) no usa el reloj: el mismo cuadro para el mismo avance."""
    cells = {}
    src, dst, sw, dw, gap = _conv_geo(W, src, dst)
    left, top = W // 2 + 1 - (sw + gap + dw) // 2, y0 + 5
    try:
        pc = None if pct is None else max(0.0, min(100.0, float(pct)))
    except (TypeError, ValueError):
        pc = None
    p = None if fill is None and pc is None else max(0.0, min(1.0, float(fill) if fill is not None else pc / 100.0))
    full = p is not None and p >= 0.999                              # 100 %: la vía se llena y el destino destella
    g = lambda k: mix6(a, b, k)

    dim = mix(BLACK, OLD_TONE, 0.55)
    x0, y = left + sw, top + 1
    dx = x0 + gap
    pp = 0.0 if p is None else p
    dedge = mix(dim, g(1.0), 0.25 + 0.75 * smooth(pp))
    dink = mix(OLD_TONE, SCENE_WHITE, min(1.0, 0.35 + 0.65 * smooth(pp)))
    if full and not fast:
        flash = 0.5 + 0.5 * math.sin(lt * 2.0 * math.pi / LOOP_SECS)   # 1.6.4: un destello completo por loop
        dedge, dink = mix(dedge, WHITE, 0.3 + 0.3 * flash), mix(dink, WHITE, 0.5 + 0.5 * flash)
    _scene_chip(cells, left, top, sw, src, dim, OLD_TONE)
    _scene_chip(cells, dx, top, dw, dst, dedge, dink)
    cells[(x0 - 1, y)] = ("│", mix(dim, OLD_TONE, 0.8 if pp > 0.0 else 0.0), None)            # el origen ya soltó datos
    # el destino, al estar lleno
    cells[(dx, y)] = ("│", mix(dedge, WHITE, 0.55 if full else 0.0), None)
    skip = set()
    # la tecla Enter de la pregunta se apaga en medio de la vía
    if key_fade is not None and key_fade > 0.0:
        ktxt, kw = scene_enter_chip(gap)
        g1 = max(1, (gap - kw) // 2)
        skip = set(range(g1, g1 + kw))
        kf = max(0.0, min(1.0, key_fade))
        _scene_chip(cells, x0 + g1, top, kw, ktxt, mix(BLACK, mix(dim, g(0.85), 0.6), kf), mix(BLACK, mix(OLD_TONE, SCENE_WHITE, 0.6), kf))
    lit = pp * gap                                                   # celdas encendidas (con parte decimal)
    # sin %: un punto recorre la vía una vez cada dos loops
    walker = None if (p is not None or fast) else int((lt / (2.0 * LOOP_SECS)) % 1.0 * gap)
    for j in range(gap):
        if j in skip:
            continue
        k = j / float(max(1, gap - 1))
        f = max(0.0, min(1.0, lit - j))                              # cuánto está encendida la celda j
        if walker is not None and j == walker:
            cells[(x0 + j, y)] = ("●", mix(g(k), WHITE, 0.6), None)
        elif walker is not None and j in (walker - 1, walker - 2) and j >= 0:
            cells[(x0 + j, y)] = ("•" if j == walker - 1 else "·", mix(BLACK, g(k), 0.7 if j == walker - 1 else 0.45), None)
        elif f >= 1.0:
            head = (not full) and j == int(lit - 1e-9) if lit > 0.0 else False
            cells[(x0 + j, y)] = ("●", mix(g(k), WHITE, 0.55), None) if head else ("•", mix(BLACK, g(k), 0.85), None)
        elif f > 0.0:
            # la cabeza: la celda que se está llenando
            cells[(x0 + j, y)] = ("●" if not full else "•", mix(g(k), WHITE, 0.55), None)
        else:
            cells[(x0 + j, y)] = ("·", mix(BLACK, OLD_TONE, 0.35), None)
    return cells

WAIT_REHEARSE = 5.5      # 1.2.1: s entre un ensayo y otro de la pregunta de convertir (un paquete cruza la tecla Enter)

def _subst_text(text, s, f):
    """1.4.2: el texto del chip viejo se deshace letra a letra (s de 0 a 1): letra → ruido → punto."""
    out = []
    for i, ch in enumerate(text):
        q = s * 1.6 - i * 0.12
        out.append(ch if q <= 0.0 else (SITE_GLITCH[int(_rn(f * 5 + i * 3) * len(SITE_GLITCH))] if GLITCH else ch) if q < 0.5 else "·")
    return "".join(out)

def scene_wait_conv_cells(W, y0, a, b, lt, src=None, dst=None, left=99.0, swap=False):
    """Pregunta de convertir (1.2.1), filas y0+5 … y0+7 (1.4.2: swap=True es la de sustituir un archivo: al llegar el paquete el viejo se deshace y el nuevo destella):"""
    cells = {}
    src, dst, sw, dw, gap = _conv_geo(W, src, dst)
    key, kw = scene_enter_chip(gap)
    g1 = max(1, (gap - kw) // 2)
    left_x, top = W // 2 + 1 - (sw + gap + dw) // 2, y0 + 5
    urgent = left <= 5.0
    breathe = 0.5 + 0.5 * math.sin(lt * 2.2)
    pulse = 0.5 + 0.5 * math.sin(lt * 7.0)
    g = lambda k: mix6(a, b, k)

    dim = mix(BLACK, OLD_TONE, 0.55)
    x0, y = left_x + sw, top + 1
    dx, kx = x0 + gap, x0 + g1
    hp = (lt % WAIT_REHEARSE) * CONV_FLOW                            # el ensayo: un paquete que recorre la vía
    heads = [hp] if hp < gap + 3 else []
    # la tecla se ilumina al pasar
    press = max(0.0, 1.0 - abs(hp - (g1 + kw / 2.0)) / (kw / 2.0 + 1.5)) if heads else 0.0
    out_hit, in_hit = _conv_near(heads, 0.0, 1.2), _conv_near(heads, float(gap), 1.2)
    dedge = mix(dim, g(1.0), 0.25 + 0.5 * in_hit)
    if swap:
        sk = 0.0 if hp <= gap else max(0.0, min(1.0, (hp - gap) / 6.0))                 # tras llegar el paquete: 0 → 1
        # y el viejo vuelve para el siguiente ensayo
        back = 1.0 if lt < WAIT_REHEARSE else min(1.0, (lt % WAIT_REHEARSE) / 0.45)
        gl = 4.0 * sk * (1.0 - sk)
        _scene_chip(cells, left_x, top, sw, _subst_text(src, sk, int(lt * 12)), mix(dim, BLACK, 0.55 * sk), mix(BLACK, OLD_TONE, (0.35 + 0.65 * back) * (1.0 - 0.7 * sk)))
        _scene_chip(cells, dx, top, dw, dst, mix(dedge, WHITE, 0.45 * gl), mix(mix(OLD_TONE, SCENE_WHITE, min(1.0, 0.6 + 0.4 * in_hit)), WHITE, 0.6 * gl))
    else:
        _scene_chip(cells, left_x, top, sw, src, dim, OLD_TONE)
        _scene_chip(cells, dx, top, dw, dst, dedge, mix(OLD_TONE, SCENE_WHITE, min(1.0, 0.6 + 0.4 * in_hit)))
    cells[(x0 - 1, y)] = ("│", mix(dim, OLD_TONE, 0.8 * out_hit), None)
    cells[(dx, y)] = ("│", mix(dedge, WHITE, 0.55 * in_hit), None)
    # tras la tecla, los puntos se encienden tras el paquete
    trail = max(0.0, min(1.0, (hp - gap // 2) / float(max(1, gap - gap // 2)))) if hp >= g1 + kw else 0.0
    # y se apagan al llegar
    gone = 1.0 if hp <= gap else max(0.0, 1.0 - (hp - gap) / 6.0)
    _conv_lane(cells, x0, y, gap, heads, trail, g, skip=set(range(g1, g1 + kw)), fade=gone)
    key_edge = mix((255, 176, 32), WHITE, 0.3 * pulse) if urgent else mix(dim, g(0.85), 0.35 + 0.35 * breathe + 0.3 * press)
    key_ink = mix((255, 176, 32), WHITE, 0.4 * pulse) if urgent else mix(OLD_TONE, SCENE_WHITE, 0.45 + 0.55 * max(press, 0.3 * breathe))
    _scene_chip(cells, kx, top, kw, key, key_edge, key_ink)
    return cells

SWAP_STREAM_SECS = UX_BEAT

def scene_subst_cells(W, y0, a, b, lt, src=None, dst=None):
    """1.4.2: escena de sustituir un archivo al guardar, filas y0+5 … y0+7: un paquete cruza de VIEJO a NUEVO, el viejo se deshace y el nuevo queda con el ✓."""
    cells = {}
    # 1.7.1: los rótulos salen del idioma activo
    src, dst, sw, dw, gap = _conv_geo(W, src or ux_chip("VIEJO"), dst or ux_chip("NUEVO"))
    left, top = W // 2 + 1 - (sw + gap + dw) // 2, y0 + 5
    g = lambda k: mix6(a, b, k)
    dim = mix(BLACK, OLD_TONE, 0.55)
    x0, y, dx = left + sw, top + 1, left + sw + gap
    # la cabeza del paquete recorre la vía y un poco más
    hp = lt / SWAP_STREAM_SECS * (gap + 3)
    heads = [hp] if hp < gap + 3 else []
    done = lt >= SWAP_STREAM_SECS
    sk = max(0.0, min(1.0, (hp - gap) / 6.0)) if hp > gap else 0.0
    k_done = smooth((lt - SWAP_STREAM_SECS) / UX_SETTLE)
    in_hit = _conv_near(heads, float(gap), 1.2)
    gl = 4.0 * sk * (1.0 - sk)
    _scene_chip(cells, left, top, sw, _subst_text(src, 1.0 if done else sk, int(lt * 12)), mix(dim, BLACK, 0.55 * max(sk, k_done)),
                mix(BLACK, OLD_TONE, 1.0 - 0.7 * max(sk, k_done)))
    dedge = mix(mix(dim, g(0.85), 0.35 + 0.65 * k_done), WHITE, 0.45 * gl)
    _scene_chip(cells, dx, top, dw, dst, dedge, mix(mix(OLD_TONE, SCENE_WHITE, min(1.0, 0.6 + 0.4 * max(in_hit, k_done))), WHITE, 0.6 * gl))
    cells[(x0 - 1, y)] = ("│", mix(dim, OLD_TONE, 0.8 * _conv_near(heads, 0.0, 1.2)), None)
    cells[(dx, y)] = ("│", mix(dedge, WHITE, 0.55 * in_hit), None)
    # sustituido: una línea y el punto de llegada en el medio (1.5.9: el ✓ va solo en el estado)
    if done:
        for j in range(gap):
            cells[(x0 + j, y)] = ("●", mix(SAVED_TONE, WHITE, 0.35 * (1.0 - k_done)), None) if j == gap // 2 \
                else ("─", mix(BLACK, g(j / float(max(1, gap - 1))), 0.3 * k_done + 0.15), None)
    else:
        _conv_lane(cells, x0, y, gap, heads, None, g)
    return cells

TYPE_DELAY_SECS, TYPE_DURATION_SECS, TYPE_RUN_SECS = 0.1, 0.6, 0.45

TYPE_STEP_SECS = TYPE_DELAY_SECS + TYPE_DURATION_SECS + TYPE_RUN_SECS

RUNNING_PREFIXES = ("comprobando", "instalando", "actualizando", "analizando")

def _dlpy_ctx(label):
    """1.3.3/1.9.2: contexto D L P Y: análisis, paquetes yt-dlp, GitHub, catálogos de idioma o arranque."""
    low = str(label or "").lower()
    if "idioma" in low or (SCENE.get("lang_code") and low.startswith("error")):
        return "language"
    if any(w in low for w in ("analiz", "análisis", "enlace", "límite de tiempo")):
        return "analyze"
    # 1.4.4: las comprobaciones en paralelo (DLpy + pip + yt-dlp a la vez)
    if "actualizaciones" in low or "comprobaciones" in low:
        return "check"
    if "yt-dlp" in low or "ytdlp" in low or "mutagen" in low or re.search(r"\bpip\b", low):
        return "ytdlp"
    if "dlpy" in low or "github" in low or "release" in low or "nueva versión" in low:
        return "github"
    return "boot"

def _dlpy_state(label):
    """1.3.3:"""
    low = str(label or "").lower().strip()
    if low.startswith("error") or "no se pudo" in low:
        return "fail"
    if low.startswith(RUNNING_PREFIXES):
        return "run"
    return "ok" if " · " in low else "run"

def _dlpy_pkg(label):
    """1.3.3: el paquete del texto de estado tal como lo pide pip («yt-dlp-ejs==0.8.0», «yt-dlp» o «pip»)."""
    m = re.search(r"yt-dlp-ejs(?:==[\w.]+)?|yt-dlp|mutagen|\bpip\b", str(label or "").lower())
    return m.group(0) if m else "pip"

def _dlpy_checking(low):
    """1.4.4: ¿el texto de estado habla de COMPROBAR un paquete (consulta a PyPI) y no de instalarlo (pip install)?"""
    return low.startswith("comprobando") or "última versión" in low or "no se pudo comprobar" in low

def _dlpy_local(low):
    """El texto de estado dice que solo se VERIFICÓ la versión instalada (sin consulta a PyPI ni pip install)."""
    return "para youtube" in low

def _dlpy_fit(cmd, room):
    """1.4.4: el comando cabe en `room` columnas sin perder lo importante: el enlace de extract_info(…) / yt-dlp -J se acorta por dentro,
    un GET deja «host/…/último-tramo» y lo demás conserva su principio y su final (--no-deps). Siempre con «…» donde se recorta."""
    if dwidth(cmd) <= room:
        return cmd
    m = re.match(r"^(extract_info\(|yt-dlp -J )(.*?)(\)?)$", cmd)
    if m:
        head, body, tail = m.groups()
        return head + fit_text(body, max(4, room - len(head) - len(tail))) + tail
    if cmd.startswith("GET "):
        host, _sep, path = cmd[4:].partition("/")
        if path:
            cand = f"GET {host}/…/{path.rstrip('/').rsplit('/', 1)[-1]}"
            if dwidth(cand) <= room:
                return cand
    tail = min(9, room // 3)
    out = cmd[:max(1, room - 1 - tail)] + "…" + cmd[len(cmd) - tail:]
    return out if dwidth(out) <= room else fit_text(cmd, room)       # 1.7.0: con caracteres anchos en el enlace

def _net_line(r, kind=None):
    """1.4.4: el resultado de una operación, en una línea: «200 · 0.4 s · 2026.10.21», «ok · 3.2 s» o la causa del fallo (+ qué pasa después)."""
    if not r:
        return None
    if not r.get("ok"):
        err = t_display(str(r.get("err") or "falló"))
        return f"{err} · {t_display('reintenta al abrir')}" if kind in ("get", "check") else err
    parts = [str(r["code"]) if r.get("code") else "ok", f"{loc_num(r.get('secs', 0.0), 1)} {sec_unit()}"]
    if r.get("val"):
        parts.append(str(r["val"]))
    return " · ".join(parts)

def _dlpy_footer(label, state, ver, name, room):
    """1.4.4: la línea bajo la cadena aSH → PY → DLPY: (texto, color). Mientras corre: el avance (pip en vivo, comprobaciones listas);
    al terminar: lo que de verdad pasó (código, tiempo, versión, o la causa del fallo). Sin datos: «DLpy <versión> · <nombre>» como siempre."""
    ctx, low = _dlpy_ctx(label), str(label or "").lower()
    base = SCENE_GRAY if SCENE_CALM else SCENE_DIM
    # 1.7.1: en boot no se escribe «boot» (la versión ya está)
    text, col = (f"DLpy {ver}" if name == "boot" else f"DLpy {ver} · {t_display(name)}"), base
    if state == "run":
        if ctx == "check" and PREFETCH.get("n"):
            text = f"{len(PREFETCH['done'])}/{PREFETCH['n']} {t_display('listas')}"
        elif ctx == "ytdlp" and not _dlpy_checking(low) and SCENE.get("pip_line"):
            text = str(SCENE["pip_line"])
    else:
        if ctx == "ytdlp":
            pkg = _dlpy_pkg(label).split("==", 1)[0]
            checking = _dlpy_checking(low)
            res = None if _dlpy_local(low) else _net_line(NET.get(pkg if checking else "pip:" + pkg), "get" if checking else None)
        elif ctx == "github":
            installing = low.startswith("instalando") or "instalada" in low or "no se pudo instalar" in low
            res = _net_line(NET.get("write" if installing else "DLpy"), None if installing else "get")
        elif ctx == "analyze":
            res = _net_line(NET.get("analyze"))
        elif ctx == "check":
            res = _net_line(NET.get("check"), "check")
        else:
            res = None
        if res:
            text, col = res, ((255, 110, 110) if state == "fail" else SCENE_GRAY)
    return fit_text(text, room), col

def _dlpy_topic(label):
    """1.3.3/1.9.2: nombre y comando de la operación real que representa la escena D L P Y."""
    low = str(label or "").lower()
    ctx = _dlpy_ctx(label)
    if ctx == "language":
        code = str(SCENE.get("lang_code") or "")
        asset = str(SCENE.get("lang_asset") or "mo")
        url = (lang_pack_sha_url(code) if asset == "sha256" else lang_pack_url(code)) if code in PACK_LANGS else None
        if url:
            parsed = urllib.parse.urlsplit(url)
            return "Idioma", "GET " + parsed.netloc + parsed.path
        return "Idioma", "GET raw.githubusercontent.com/…/" + (LANG_SUMS if asset == "sha256" else "dlpy_lang_<code>.mo")
    if ctx == "ytdlp":
        spec = _dlpy_pkg(label)
        pkg = spec.split("==", 1)[0]
        # verificación local de lo instalado («yt-dlp-ejs 0.8.0 · para YouTube»): no se instala nada
        if _dlpy_local(low):
            return pkg, f'metadata.version("{pkg}")'                    # lo que hace pkg_version, sin red y sin pip
        # 1.4.3: la petición real de latest_version (no «curl»)
        return pkg, (f"GET pypi.org/pypi/{pkg}/json" if _dlpy_checking(low) else pip_cmd(pip_args(spec)))
    # 1.4.4: las peticiones que salen a la vez (las mismas de arriba, en hilos)
    if ctx == "check":
        return "actualizaciones", "GET " + (PREFETCH.get("hosts") or "pypi.org · github.com")
    if ctx == "github":
        installing = low.startswith("instalando") or "instalada" in low or "no se pudo instalar" in low
        # 1.4.3: esa fase solo escribe el script ya descargado (write_text)
        if installing:
            return "GitHub", "write " + os.path.basename(SCRIPT_PATH)
        info = repo_info()
        return "GitHub", ("GET api.github.com/repos/%s/%s/releases" % info if info else "GET api.github.com/repos/…")
    if ctx == "analyze":
        # 1.4.3: la llamada real de analyze_link, con el enlace real
        link = re.sub(r"^https?://", "", str(SCENE.get("link") or "")) or "…"
        # 1.4.4: el último intento sí es el comando `yt-dlp -J <enlace>`
        if SCENE.get("ana_raw"):
            return "analizando", f"yt-dlp -J {link}"
        return "analizando", f"extract_info({link})"
    return "boot", "python dlpy.py"

def dlpy_type_time(ta, seen_at, enter_at):
    """1.3.3:"""
    return max(0.0, ta - max(seen_at, enter_at + SCENE_SWAP))

TYPE_WAIT_MAX_SECS = SITE_SECS + SCENE_SWAP + TYPE_STEP_SECS + 1.0

def scene_wait_step(old, limit=None, alive=None):
    """1.3.3:"""
    S = SCENE
    old = str(old or "")
    if not S["on"] or SCENE_MODE[0] == "real" or S.get("last_error") or not old or old.startswith(("Enviando", "Abriendo", "Error")):
        return False
    if scene_motif_kind(S) != "dlpy":
        return False
    th = S.get("th")
    if not (alive() if callable(alive) else (th is not None and th.is_alive())):
        return False
    end = time.time() + (TYPE_WAIT_MAX_SECS if limit is None else limit)
    while S.get("dl_done") != old and time.time() < end and S["on"] and not S.get("stop"):
        time.sleep(0.02)
    return S.get("dl_done") == old


def scene_gate(new_kind=None, limit=None):
    """1.5.9: la compuerta del modo UX «wait». Antes de que el flujo pase al siguiente proceso espera a que el dibujo que ocupa el centro se vea
    ENTERO: que haya terminado de entrar y que cierre su loop en curso (lo que dura de verdad la animación, sin pausas fijas ni tiempo extra; tope
    MOTIF_HOLD_MAX). Así una descarga corta ya no pasa sin que se alcance a ver su animación ni queda el centro vacío por un proceso prematuro.
    `new_kind`: el dibujo que va a entrar (si ya es el del centro no hay nada que esperar); None = proteger el que esté. No espera: fuera de «wait»
    (en «real» no se espera nada; con segundos mandan los segundos), sin escena, con error, sin hilo vivo (o si lo llama el propio hilo), con el
    Pulso en el centro (no es una animación de proceso), si el dibujo no entra en SCENE_SWAP + 1 s, ni si ya se esperó hace poco.
    1.8.1: el SITIO (el análisis del enlace: audio y video que se transforman en lo detectado) SÍ es una escena con su loop (_loop_site): antes se
    dejaba pasar de largo y esa transformación duraba muy poco. Mientras la intro corre (SCENE["mvis"] aún sin publicar) el centro es el sitio y se
    espera a que entre. Hacia D L P Y y las escenas de versión (UPDATE_KINDS) el sitio no retiene: la pantalla de actualización no tiene reglas de loop.
    Deja la marca que usa scene_motif para no retener el mismo loop otra vez. True si esperó."""
    S = SCENE
    if not S["on"] or SCENE_MODE[0] != "loop" or S.get("last_error"):
        return False
    th = S.get("th")
    if th is None or not th.is_alive() or th is threading.current_thread():
        return False
    t_in = time.time()
    end = t_in + SCENE_SWAP + 1.0
    mv = None
    while time.time() < end and S["on"] and not S.get("stop") and not S.get("last_error"):
        mv = S.get("mvis")
        # 1.8.1: sin publicar aún (la intro corre) el centro es el sitio (None)
        cur = mv[0] if mv else None
        if cur == "idle" or cur == new_kind or (cur is None and new_kind in UPDATE_KINDS):
            # el Pulso no es proceso · mismo dibujo · el sitio no retiene a D L P Y (1.8.1: antes ignoraba al sitio entero)
            return False
        gp = S.get("gate_paid")
        if mv and gp and gp[0] == cur and gp[1] == (mv[4] if len(mv) > 4 else None) and t_in - gp[2] < GATE_PAID_SECS:
            # este mismo dibujo ya se esperó hace un momento
            return False
        # ya entró y la medida es de este instante (no del cuadro anterior)
        if mv and mv[1] and mv[3] >= t_in:
            break
        time.sleep(0.02)
    else:
        return False
    rest = min(MOTIF_HOLD_MAX if limit is None else limit, max(0.0, float(mv[2] or 0.0) - max(0.0, time.time() - mv[3])))
    if rest > 0:
        time.sleep(rest)
    now = time.time()
    S["gate_paid"] = (mv[0], mv[4] if len(mv) > 4 else None, now)
    S["loop_paid"] = (mv[0], now)
    return rest > 0


def _dlpy_error_line():
    try:
        err = SCENE.get("last_error") if SCENE.get("on") else None
        if err:
            # 1.9.0: error propio localizado; los mensajes externos desconocidos quedan intactos
            return fit_text(t_status(str(err)), 48)
    except Exception as _ign:
        ignore('error de la escena', _ign)
    return None

def _dlpy_title_for_ctx(name):
    return f" a-Shell · {t_display(name)} "

def scene_dlpy_cells(W, y0, a, b, lt, ver, label="", tt=None):
    """Escena DLPY 1.0.3: boot aSH → PY → DLPY con comando contextual."""
    cells = {}
    # 1.3.3: hasta 40 · 1.4.4: hasta 52 (cabe «pip install -U yt-dlp-ejs==0.8.0 --no-deps»)
    fw = max(26, min(52, W - 4))
    inner = fw - 2
    left, top = W // 2 + 1 - fw // 2, y0 + 4
    ctx = _dlpy_ctx(label)
    # 1.3.3: run (teclea y gira) · ok / fail (ya ejecutado: ✓ / ✗)
    state = _dlpy_state(label)
    g = lambda k: mix6(a, b, k)

    for i in range(fw):
        k = i / float(fw - 1)
        first, last = i == 0, i == fw - 1
        cells[(left + i, top)] = ("╭" if first else "╮" if last else "─", g(k), None)
        cells[(left + i, top + 4)] = ("╰" if first else "╯" if last else "─", g(k), None)
    # 1.2.7: nombre y comando según el texto de estado
    name, cmd = _dlpy_topic(label)
    # 1.7.1: en boot el título lleva la versión, no la palabra «boot» · 1.7.0: con ancho real (ja/zh/ko = 2 columnas) y los espacios son huecos del marco
    title = " " + fit_text(_dlpy_title_for_ctx(str(ver) if name == "boot" else name).strip(), max(6, fw - 6)) + " "
    put_text(cells, left + 2, top, title, lambda i, ch: SCENE_WHITE if ch != " " else BLACK, skip_space=False)
    for r in (1, 2, 3):
        cells[(left, top + r)] = ("│", g(0.0), None)
        cells[(left + fw - 1, top + r)] = ("│", g(1.0), None)

    # 1.2.6: nunca se sale del marco (1.4.4: el recorte conserva lo importante y siempre dice «…»)
    cmd = _dlpy_fit(cmd, max(8, inner - 6))
    # 1.7.0: el comando por caracteres visibles y su ancho real
    cg, cw_ = text_cells(cmd), dwidth(cmd)
    # 1.2.7: tt = s a la vista del comando (1.3.3: desde que la escena se ve)
    t = (lt % 6.0) if tt is None else tt
    if state != "run":
        # 1.3.3: un resultado ya se ejecutó: el comando está entero y sin destello
        t = TYPE_DELAY_SECS + TYPE_DURATION_SECS + TYPE_RUN_SECS + 1.0
    n = int(max(0.0, min(1.0, (t - TYPE_DELAY_SECS) / TYPE_DURATION_SECS)) * len(cg) + 0.5)
    # < 0: tecleando; ≥ 0: Enter pulsado y ejecutando
    ran = t - (TYPE_DELAY_SECS + TYPE_DURATION_SECS)
    # el comando se ilumina al pulsar Enter y se apaga
    flash = max(0.0, 1.0 - ran / TYPE_RUN_SECS) if ran >= 0 else 0.0
    cells[(left + 2, top + 1)] = ("$", SCENE_GRAY, None)
    for k_, (i, s_, dx, w) in enumerate(cg[:n]):
        col = mix(mix(g(k_ / float(max(1, len(cg) - 1))), WHITE, 0.35), WHITE, 0.65 * flash)
        cells[(left + 4 + dx, top + 1)] = (s_, col, None)
        if w == 2:
            cells[(left + 5 + dx, top + 1)] = ("", col, None)
    if ran < 0:
        if n < len(cg) or int(lt * 2.5) % 2 == 0:
            cells[(left + 4 + (cg[n][2] if n < len(cg) else cw_), top + 1)] = ("▌", WHITE, None)
    # ejecutando: gira un indicador tras el comando
    elif state == "run":
        cells[(left + 5 + cw_, top + 1)] = ("|/-\\"[int(lt * 10) % 4], SCENE_DIM, None)
    # 1.3.3: terminó: ✓ (salió bien) o ✗ (falló), sin girar
    else:
        cells[(left + 5 + cw_, top + 1)] = ("✓", (120, 224, 150), None) if state == "ok" else ("✗", (255, 80, 80), None)

    link = " ─► " if inner >= 30 else " ► "
    part_a, part_py, part_dl = "aSH", "PY", "DLPY"
    chain = part_a + link + part_py + link + part_dl
    s0_a, e0_a = 0, len(part_a)
    s0_py = e0_a + len(link)
    e0_py = s0_py + len(part_py)
    s0_dl = e0_py + len(link)
    e0_dl = s0_dl + len(part_dl)
    nodes = ((s0_a, e0_a), (s0_py, e0_py), (s0_dl, e0_dl))

    focus = 1
    if ctx == "analyze":
        focus = 1
    elif ctx in ("github", "language"):
        focus = 2
    elif ctx == "ytdlp":
        focus = 1
    else:
        boot_phase = (lt % 9.0)
        focus = int(min(2, boot_phase // 1.6))

    base_speed = 0.42
    cycle = (lt * base_speed) % 1.0
    if cycle < 0.7:
        prog = cycle / 0.7
        head = prog * (len(chain) + 10) - 5
    else:
        dwell_prog = (cycle - 0.7) / 0.3
        center = (nodes[focus][0] + nodes[focus][1]) / 2.0
        head = center + math.sin(dwell_prog * math.pi * 2) * 0.6

    x0 = left + 1 + (inner - len(chain)) // 2
    boot_phase = (lt % 9.0)

    for i, ch in enumerate(chain):
        if ch == " ":
            continue
        is_a = s0_a <= i < e0_a
        is_py = s0_py <= i < e0_py
        is_dl = s0_dl <= i < e0_dl
        is_link = not (is_a or is_py or is_dl)
        d = head - i
        glow = max(0.0, 1.0 - abs(d) / 6.0) if abs(d) < 6 else 0.0
        boot_lit = 0.0
        if is_a:
            boot_lit = 1.0 if boot_phase >= 0.2 else max(0.0, boot_phase / 0.2)
        if is_py:
            boot_lit = 1.0 if boot_phase >= 1.7 else max(0.0, (boot_phase - 1.5) / 0.2) if boot_phase >= 1.5 else 0.0
            if boot_phase >= 4.5:
                boot_lit = 1.0
        if is_dl:
            boot_lit = 1.0 if boot_phase >= 3.2 else max(0.0, (boot_phase - 3.0) / 0.2) if boot_phase >= 3.0 else 0.0
            if boot_phase >= 4.5:
                boot_lit = 1.0
        if boot_phase >= 4.5:
            boot_lit = 1.0

        if is_link:
            base_col = g(i / float(max(1, len(chain)-1)))
            col = mix(base_col, WHITE, 0.3 + 0.4 * glow)
        elif is_a:
            base = (180, 180, 190)
            col = mix(BLACK, base, 0.35 + 0.65 * boot_lit)
            col = mix(col, WHITE, glow * 0.7)
        elif is_py:
            base = (55, 118, 171) if i == s0_py else (255, 212, 59)
            col = mix(BLACK, base, 0.3 + 0.7 * boot_lit)
            col = mix(col, WHITE, glow * 0.8)
        else:
            base = g(i / float(max(1, len(chain)-1)))
            col = mix(BLACK, base, 0.25 + 0.75 * boot_lit)
            if glow > 0.1:
                col = mix(col, WHITE, 0.6 + 0.4 * glow)
            if is_dl and focus == 2 and cycle >= 0.7:
                col = mix(col, WHITE, 0.5 + 0.3 * math.sin(lt * 6))

        cells[(x0 + i, top + 2)] = (ch, col, None)

    err_line = _dlpy_error_line()
    if err_line and SCENE.get("on") and SCENE.get("brand"):
        # 1.0.4: error integrado en D L P Y: muestra el error en lugar de la versión
        txt2 = fit_text(f"! {err_line}", max(8, inner - 2))      # 1.0.8: cabe dentro de la caja (antes pisaba el borde)
        put_text(cells, left + 1 + (inner - dwidth(txt2)) // 2, top + 3, txt2, (255, 80, 80), lo=left + 1, hi=left + fw - 1)      # 1.7.0: ancho real
        return cells

    # 1.4.4: el resultado real de lo que se ejecutó (o su avance en vivo)
    txt2, fcol = _dlpy_footer(label, state, ver, name, inner - 2)
    # 1.7.0: ancho real
    put_text(cells, left + 1 + (inner - dwidth(txt2)) // 2, top + 3, txt2, fcol, lo=left + 1, hi=left + fw - 1)
    return cells

SCENE_SEND_SECS = UX_HOLD

MERGE_SPEED = 4.0 / LOOP_SECS

SAVE_STREAM_SECS = UX_BEAT

SEND_CYCLE = UX_CYCLE

SEND_BASE = 1.6

SAVED_TONE = (120, 220, 140)                        # 1.1.3: el ✓ de «guardado»

def _scene_chip(cells, x0, top, w, text, edge, ink):
    """Un chip redondeado de tres filas (ancho w) con `text` centrado en la fila del medio, dentro de `cells`."""
    for i in range(w):
        first, last = i == 0, i == w - 1
        cells[(x0 + i, top)] = ("╭" if first else "╮" if last else "─", edge, None)
        cells[(x0 + i, top + 2)] = ("╰" if first else "╯" if last else "─", edge, None)
    cells[(x0, top + 1)] = ("│", edge, None)
    cells[(x0 + w - 1, top + 1)] = ("│", edge, None)
    pad = max(0, (w - 2 - dwidth(text)) // 2)
    put_text(cells, x0 + 1 + pad, top + 1, text, ink, lo=x0 + 1, hi=x0 + w - 1)      # 1.7.0: ancho real
    return cells

def scene_merge_cells(W, y0, a, b, lt):
    """Escena de unión, filas y0+5 … y0+7:"""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    # 1.7.2: las etiquetas salen del idioma activo (antes «VIDEO» / «AUDIO» fijos)
    lab_v, lab_a = ux_text("VIDEO"), ux_text("AUDIO")
    lw = max(5, dwidth(lab_v), dwidth(lab_a))
    lab = lw if room >= 22 + lw else 0                                # (antes 5 si room ≥ 27: es lo mismo con lw = 5)
    chip_w, merged = (7 if room >= 25 else 5), 4
    lane = max(3, min(9, room - lab - (1 if lab else 0) - 1 - merged - chip_w))
    total = lab + (1 if lab else 0) + lane + 1 + merged + chip_w
    left, top = W // 2 + 1 - total // 2, y0 + 5
    x0 = left + lab + (1 if lab else 0)
    ink = mix(BLACK, OLD_TONE, 0.8)
    if lab:
        put_text(cells, left, top, lab_v, ink, lo=left, hi=left + lab)
        put_text(cells, left, top + 2, lab_a, ink, lo=left, hi=left + lab)
    pulse = 0.5 + 0.5 * math.sin(lt * 6.0)
    for j in range(lane):
        k = j / float(max(1, lane - 1))
        ph = (j - lt * MERGE_SPEED) % 4.0
        if ph < 2.0:                                                  # un bloque de video con su cola
            cells[(x0 + j, top)] = ("█" if ph < 1.0 else "▓", mix(g(0.12), WHITE, 0.25 * k), None)
        else:
            cells[(x0 + j, top)] = ("─", mix(BLACK, g(0.12), 0.3), None)
        h = (math.sin((j - lt * MERGE_SPEED) * 1.3) + 1.0) / 2.0     # barras de audio que suben y bajan
        cells[(x0 + j, top + 2)] = ("▁▂▃▄▅▆▇█"[min(7, int(h * 8.0))], mix(g(0.88), WHITE, 0.25 * k), None)
    jx = x0 + lane
    jc = mix(g(0.5), WHITE, 0.45 + 0.35 * pulse)
    cells[(jx, top)], cells[(jx, top + 1)], cells[(jx, top + 2)] = ("╮", jc, None), ("├", jc, None), ("╯", jc, None)
    for j in range(merged):
        ph = (j - lt * MERGE_SPEED) % 4.0
        k = (j + 1) / float(merged + 1)
        cells[(jx + 1 + j, top + 1)] = (("█" if ph < 1.0 else "▓") if ph < 2.0 else "─", g(0.12 + 0.76 * k), None)
    cx0 = jx + 1 + merged
    _scene_chip(cells, cx0, top, chip_w, "", g(0.5), SCENE_WHITE)
    inner = chip_w - 2
    fill = int(lt * 3.0) % (inner + 1)                                # el archivo se va llenando una y otra vez
    for i in range(inner):
        cells[(cx0 + 1 + i, top + 1)] = ("▓", g(0.12 + 0.76 * i / float(max(1, inner - 1))), None) if i < fill \
            else ("░", mix(BLACK, OLD_TONE, 0.6), None)
    return cells

def scene_save_cells(W, y0, a, b, lt):
    """Escena de guardado, filas y0+5 … y0+7:"""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    name = os.path.basename(FILES_DIR) or "files"
    sw = 7
    if sw + 5 + dwidth(name) + 4 > room:
        name = "files"
    fw = dwidth(name) + 4
    gap = max(5, min(13, room - sw - fw))
    gap -= 1 - gap % 2
    left, top = W // 2 + 1 - (sw + gap + fw) // 2, y0 + 5
    k_saved = smooth((lt - SAVE_STREAM_SECS) / UX_SETTLE)                  # 0 = todavía guardando … 1 = guardado
    dim = mix(BLACK, OLD_TONE, 0.55)
    _scene_chip(cells, left, top, sw, "▓▓▓", mix(g(0.2), dim, k_saved), mix(SCENE_WHITE, OLD_TONE, k_saved))
    _scene_chip(cells, left + sw + gap, top, fw, name, mix(dim, g(0.85), k_saved), mix(OLD_TONE, SCENE_WHITE, k_saved))
    x0, y, mid = left + sw, top + 1, gap // 2
    for j in range(gap):
        k = j / float(max(1, gap - 1))
        # guardado: una línea y el punto de llegada en el medio (1.5.9: el ✓ va solo en el estado)
        if lt >= SAVE_STREAM_SECS:
            # 1.5.9: un punto de llegada (el ✓ va solo en el estado de la escena)
            if j == mid:
                cells[(x0 + j, y)] = ("●", mix(SAVED_TONE, WHITE, 0.35 * (1.0 - k_saved)), None)
            else:
                cells[(x0 + j, y)] = ("─", mix(BLACK, g(k), 0.3 * k_saved + 0.15), None)
            continue
        ph = (j - lt * CONV_SPEED * 1.4) % 5.0                        # bloques que se afinan camino de la carpeta
        if ph < 2.0:
            cells[(x0 + j, y)] = (("░▒▓█"[min(3, int(k * 3.0 + (0.0 if ph < 1.0 else 1.0)))]), mix(BLACK, g(0.2 + 0.7 * k), 0.55 + 0.45 * k), None)
        else:
            cells[(x0 + j, y)] = ("─", mix(BLACK, g(k), 0.25), None)
    return cells

CHECK_TONE = (255, 190, 90)                         # 1.2.5: ámbar de «esto hay que convertirlo»

CHECK_BLINKS = 2

CHECK_BLINK_STEP = LOOP_SECS / (CHECK_BLINKS * 2)

CHECK_BLINK_SECS = CHECK_BLINKS * 2 * CHECK_BLINK_STEP

CHECK_PULSE_SECS = LOOP_SECS

def _check_fit(rows, room):
    """(anchos de los chips, ancho total, largo máximo del texto) de la revisión para `room` columnas."""
    pad, lim = 4, 6
    while True:
        widths = [max(5, min(lim, dwidth(t)) + pad) for t, _n in rows]
        total = sum(widths) + len(rows) - 1
        if total <= room or (pad <= 2 and lim <= 3):
            return widths, total, lim
        if pad > 2:
            pad = 2
        else:
            lim -= 1

def check_blink_phase(rt):
    """1.6.1: parpadeo de la revisión al resolverse. `rt` = s desde que se determinó lo detectado. 1 = destello · 0 = apagón · None = ya pasó
    (o no hay veredicto): sigue el pulso de siempre. Empieza con un destello."""
    if rt is None or rt < 0 or rt >= CHECK_BLINK_SECS:
        return None
    return 1 if int(rt / CHECK_BLINK_STEP) % 2 == 0 else 0

def scene_check_cells(W, y0, a, b, lt, items=None, verdict=None, rt=None):
    """Escena de revisión (1.2.5), filas y0+5 … y0+7:"""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    rows = [(scene_chip_text(t) or "?", bool(n)) for t, n in (items or [])][:3] or [("?", False)] * 3
    widths, total, lim = _check_fit(rows, room)
    left, top = W // 2 + 1 - total // 2, y0 + 5
    dim = mix(BLACK, OLD_TONE, 0.55)
    period = 2.0 * total
    s = (lt * period / LOOP_SECS) % period                            # 1.6.3: ida y vuelta del haz = un loop
    pos = s if s < total else period - s                              # el haz va y viene
    x, n_ch = left, len(rows)
    for i, ((text, need), w) in enumerate(zip(rows, widths)):
        text = clip_text(text, lim)
        if verdict is None:
            near = max(0.0, 1.0 - abs(pos - (x - left + w / 2.0)) / (w / 2.0 + 3.0))
            edge = mix(dim, g(i / float(max(1, n_ch - 1))), 0.2 + 0.8 * near)
            ink = mix(OLD_TONE, SCENE_WHITE, 0.3 + 0.7 * near)
        else:
            base = CHECK_TONE if (verdict == "conv" and need) else SAVED_TONE
            pulse = 0.5 + 0.5 * math.sin(((rt - CHECK_BLINK_SECS) if rt is not None else 0.0) * 2.0 * math.pi / CHECK_PULSE_SECS)      # 1.6.2: el pulso arranca donde acaba el parpadeo (un ciclo completo = CHECK_PULSE_SECS)
            edge = mix(mix(BLACK, base, 0.85), WHITE, 0.25 * pulse)
            ink = mix(base, WHITE, 0.55 + 0.25 * pulse)
            # 1.6.1: al determinarse, los tres cuadros parpadean con su color de veredicto
            if check_blink_phase(rt) == 1:
                edge, ink = mix(base, WHITE, 0.6), WHITE
            elif check_blink_phase(rt) == 0:
                edge, ink = mix(BLACK, base, 0.3), mix(base, BLACK, 0.55)
        _scene_chip(cells, x, top, w, text, edge, ink)
        x += w + 1
    if verdict is None:
        bx = left + int(pos)
        for yy, ch in ((top, "━"), (top + 2, "━")):
            cells[(bx, yy)] = (ch, mix(g(0.5), WHITE, 0.5), None)
        if (bx, top + 1) not in cells:
            cells[(bx, top + 1)] = ("┃", mix(g(0.5), WHITE, 0.35), None)
    return cells

def scene_send_cells(W, y0, a, b, lt, dest="DLPY"):
    """Escena de envío, filas y0+5 … y0+7:"""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    dest = scene_chip_text(dest) or "DLPY"
    dw = max(7, dwidth(dest) + 4)
    track = max(9, min(21, room - dw - 5))
    total = 3 + track + dw
    left, top = W // 2 + 1 - total // 2, y0 + 5
    # 1.6.3: el dibujo sigue en su escala de 1,6 s; el ciclo dura SEND_CYCLE
    cyc = (lt % SEND_CYCLE) * (SEND_BASE / SEND_CYCLE)
    arrived = cyc >= 1.0
    flash = max(0.0, 1.0 - (cyc - 1.0) / 0.6) if arrived else 0.0
    dim = mix(BLACK, OLD_TONE, 0.55)
    # el archivo salió de su chip y vuelve para el siguiente ciclo
    gone = 0.12 < cyc < 1.45
    _scene_chip(cells, left, top, 3, "▓", dim if gone else g(0.15), OLD_TONE if gone else SCENE_WHITE)
    dx = left + 3 + track
    _scene_chip(cells, dx, top, dw, dest, mix(dim, mix(g(0.85), WHITE, 0.6 * flash), 1.0 if arrived else 0.0),
                SCENE_WHITE if arrived else OLD_TONE)
    p = smooth(cyc / 1.0)
    hx, y = p * (track - 1), top + 1
    for j in range(track):
        d = hx - j
        if cyc < 1.0 and -0.5 <= d < 0.5:
            cells[(left + 3 + j, y)] = ("●", mix(g(j / float(max(1, track - 1))), WHITE, 0.7), None)
        elif cyc < 1.0 and 0.5 <= d < 1.6:
            cells[(left + 3 + j, y)] = ("•", mix(BLACK, g(j / float(max(1, track - 1))), 0.85), None)
        elif cyc < 1.0 and 1.6 <= d < 3.2:
            cells[(left + 3 + j, y)] = ("·", mix(BLACK, g(j / float(max(1, track - 1))), 0.55), None)
        elif j % 2 == 0:
            cells[(left + 3 + j, y)] = ("·", mix(BLACK, OLD_TONE, 0.45), None)
    if arrived and flash > 0.0:                                       # la onda sale del chip hacia los lados
        r = int((cyc - 1.0) / 0.6 * 3.0)
        for sgn, ch, edge in ((-1, "(", dx - 1 - r), (1, ")", dx + dw + r)):
            if 1 <= edge <= W - 1:
                cells[(edge, y)] = (ch, mix(BLACK, g(0.85 if sgn > 0 else 0.5), 0.35 + 0.65 * flash), None)
    return cells

CLEAN_SPEED = 1.0 / LOOP_SECS

def _trash_chip(room):
    """1.7.2: (ancho de la barra, texto del chip) de la papelera de limpieza / vaciado: su nombre en el idioma activo si cabe (barra de 8); si no, la forma corta (barra de 5).
    Antes: «papelera» / «trash» fijos y medidos con len()."""
    i, name = ux_pick("papelera", room=room - 18, fallback="basura")
    return (8, name) if i == 0 else (5, fit_text(name, max(3, room - 15)))

def scene_clean_cells(W, y0, a, b, lt, n=0):
    """Escena de limpieza (1.1.5), filas y0+5 … y0+7:"""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    bw, name = _trash_chip(room)
    fw = dwidth(name) + 4
    gap = max(5, min(11, room - bw - fw - 1))
    total = bw + 1 + gap + fw
    left, top = W // 2 + 1 - total // 2, y0 + 5
    bx = left + bw + 1 + gap
    dim = mix(BLACK, OLD_TONE, 0.55)
    hit = 0.0
    for i in range(3):
        ph = ((lt * CLEAN_SPEED + i / 3.0) % 1.0) if n > 0 else 0.0
        # la barra se va gastando mientras suelta su bloque
        keep = bw if n <= 0 else max(1, int(round(bw * (1.0 - 0.9 * ph))))
        for j in range(bw):
            if j < keep:
                cells[(left + j, top + i)] = ("▬", mix(BLACK, OLD_TONE, 0.75 - 0.25 * j / float(bw)), None)
        if n > 0:
            px = int(ph * gap)
            k = px / float(max(1, gap - 1))
            cells[(left + bw + 1 + px, top + i)] = ("░▒▓█"[min(3, int(k * 3.99))], mix(BLACK, g(0.15 + 0.7 * k), 0.55 + 0.45 * k), None)
            if px >= 1:
                cells[(left + bw + px, top + i)] = ("░", mix(BLACK, g(k), 0.4), None)
            hit = max(hit, max(0.0, 1.0 - abs(ph - 0.97) / 0.12) if ph > 0.8 or ph < 0.05 else 0.0)
    _scene_chip(cells, bx, top, fw, name, mix(dim, g(0.85), (0.3 + 0.7 * hit) if n > 0 else 0.0),
                mix(OLD_TONE, SCENE_WHITE, (0.4 + 0.6 * hit) if n > 0 else 0.0))
    return cells

def scene_empty_cells(W, y0, a, b, lt, n=0):
    """Escena de vaciado (1.1.7), filas y0+5 … y0+7:"""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    bw, name = _trash_chip(room)
    fw = dwidth(name) + 4
    gap = max(5, min(11, room - bw - fw - 1))
    dist = bw + 1 + gap
    total = dist + fw
    left, top = W // 2 + 1 - total // 2, y0 + 5
    cx = left + fw
    dim = mix(BLACK, OLD_TONE, 0.55)
    hit = 0.0
    if n > 0:
        for i in range(3):
            ph = (lt * CLEAN_SPEED + i / 3.0) % 1.0
            px = int(ph * dist)
            k = px / float(max(1, dist - 1))
            ch = "█▓▒░"[min(3, int(k * 3.99))]
            if k < 0.97:
                cells[(cx + px, top + i)] = (ch, mix(BLACK, g(0.85 - 0.7 * k), 0.95 - 0.7 * k), None)
            if px >= 1 and k < 0.9:
                cells[(cx + px - 1, top + i)] = ("░", mix(BLACK, g(0.5 * (1.0 - k)), 0.35 * (1.0 - k)), None)
            hit = max(hit, max(0.0, 1.0 - ph / 0.12) if ph < 0.12 else 0.0)
    _scene_chip(cells, left, top, fw, name, mix(dim, g(0.85), (0.3 + 0.7 * hit) if n > 0 else 0.0),
                mix(OLD_TONE, SCENE_WHITE, (0.4 + 0.6 * hit) if n > 0 else 0.0))
    return cells

WELCOME_CYCLE = 2.0

WELCOME_BASE = 2.4

WELCOME_FLY = 1.1

WELCOME_ITEMS = ("carpetas", "estado", "listo")     # 1.2.9: los tres pasos de la primera ejecución

UPDATE_KINDS = ("dlpy", "first", "updated", "downgrade", "same", "ahead")

WELCOME_KINDS = ("first", "updated", "downgrade", "same", "ahead")

def scene_first_cells(W, y0, a, b, lt):
    """Escena de primera ejecución (1.2.9), filas y0+5 … y0+7:"""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    # 1.7.1: en el idioma activo (antes siempre «carpetas · estado · listo»)
    names = [t_display(n) for n in WELCOME_ITEMS]
    nw = max(dwidth(n) for n in names)                                  # ancho real (ja / zh / ko = 2 columnas)
    bl = max(6, min(14, room - nw - 4))
    total = nw + 1 + bl + 2
    left, top = W // 2 + 1 - total // 2, y0 + 5
    cyc = (lt % WELCOME_CYCLE) * (WELCOME_BASE / WELCOME_CYCLE)         # 1.6.3: en la escala de 2,4 s del dibujo
    dim = mix(BLACK, OLD_TONE, 0.35)
    for i, name in enumerate(names):
        t0 = 0.1 + 0.5 * i
        f = max(0.0, min(1.0, (cyc - t0) / 0.45))                       # 0 = sin empezar … 1 = terminado
        y = top + i
        ink = mix(OLD_TONE, SCENE_WHITE, 0.3 + 0.7 * smooth(f))
        put_text(cells, left, y, name, ink, lo=left, hi=left + nw)      # 1.7.1: put_text respeta el ancho real
        fill = int(f * bl + 0.5)
        for j in range(bl):
            if j < fill:
                head = f < 1.0 and j == fill - 1
                cells[(left + nw + 1 + j, y)] = ("━", mix(g(j / float(max(1, bl - 1))), WHITE, 0.6) if head else g(j / float(max(1, bl - 1))), None)
            else:
                cells[(left + nw + 1 + j, y)] = ("─", dim, None)
        if f >= 1.0:
            flash = max(0.0, 1.0 - (cyc - (t0 + 0.45)) / 0.3)
            cells[(left + nw + 2 + bl, y)] = ("✓", mix(SAVED_TONE, WHITE, 0.45 * flash), None)
    return cells

def scene_updated_cells(W, y0, a, b, lt, old="", new=""):
    """Escena de actualizado (1.2.9), filas y0+5 … y0+7:"""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    old, new = str(old or "").strip()[:7] or "?", str(new or "").strip()[:7] or "?"
    wo, wn = max(9, len(old) + 4), max(9, len(new) + 4)
    track = max(7, min(15, room - wo - wn))
    total = wo + track + wn
    left, top = W // 2 + 1 - total // 2, y0 + 5
    cyc = (lt % WELCOME_CYCLE) * (WELCOME_BASE / WELCOME_CYCLE)         # 1.6.3: en la escala de 2,4 s del dibujo
    arrived = cyc >= WELCOME_FLY
    k_in = smooth((cyc - WELCOME_FLY) / 0.25) if arrived else 0.0       # 0 = en camino … 1 = ya llegó
    pulse = max(0.0, 1.0 - (cyc - WELCOME_FLY) / 0.5) if arrived else 0.0
    dim = mix(BLACK, OLD_TONE, 0.55)
    _scene_chip(cells, left, top, wo, old, mix(g(0.2), dim, k_in), mix(SCENE_WHITE, OLD_TONE, k_in))
    _scene_chip(cells, left + wo + track, top, wn, new, mix(dim, mix(g(0.85), WHITE, 0.6 * pulse), k_in), mix(OLD_TONE, SCENE_WHITE, k_in))
    x0, y, mid = left + wo, top + 1, track // 2
    shift = int(cyc * 10.0)
    for j in range(track):
        k = j / float(max(1, track - 1))
        if arrived:
            if j == mid:
                cells[(x0 + j, y)] = ("✓", mix(SAVED_TONE, WHITE, 0.35 * pulse), None)
            else:
                cells[(x0 + j, y)] = ("─", mix(BLACK, g(k), 0.3 * k_in + 0.15), None)
        elif (j - shift) % 3 == 0:
            cells[(x0 + j, y)] = ("›", mix(BLACK, g(0.2 + 0.7 * k), 0.55 + 0.45 * k), None)
    return cells

def scene_downgrade_cells(W, y0, a, b, lt, old="", new=""):
    """Escena de versión anterior (1.6.5), filas y0+5 … y0+7: el espejo de scene_updated_cells. La versión que había (`old`) queda a la DERECHA y la de ahora
    (`new`) a la IZQUIERDA; los chevrones ‹ van de derecha a izquierda, en ámbar (el tono de «ojo»), y se hunden una fila por tramo (bajan). Al llegar, ✓ en el
    centro y la versión nueva destella. Mismo ciclo y misma escala que «actualizado» (WELCOME_CYCLE / WELCOME_BASE)."""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    old, new = str(old or "").strip()[:7] or "?", str(new or "").strip()[:7] or "?"
    wn, wo = max(9, len(new) + 4), max(9, len(old) + 4)
    track = max(7, min(15, room - wn - wo))
    total = wn + track + wo
    left, top = W // 2 + 1 - total // 2, y0 + 5
    cyc = (lt % WELCOME_CYCLE) * (WELCOME_BASE / WELCOME_CYCLE)         # en la escala de 2,4 s del dibujo
    arrived = cyc >= WELCOME_FLY
    k_in = smooth((cyc - WELCOME_FLY) / 0.25) if arrived else 0.0       # 0 = en camino … 1 = ya llegó
    pulse = max(0.0, 1.0 - (cyc - WELCOME_FLY) / 0.5) if arrived else 0.0
    dim = mix(BLACK, OLD_TONE, 0.55)
    _scene_chip(cells, left, top, wn, new, mix(dim, mix(CHECK_TONE, WHITE, 0.5 * pulse), k_in), mix(OLD_TONE, SCENE_WHITE, k_in))
    _scene_chip(cells, left + wn + track, top, wo, old, mix(g(0.2), dim, k_in), mix(SCENE_WHITE, OLD_TONE, k_in))
    x0, mid = left + wn, track // 2
    shift = int(cyc * 10.0)
    for j in range(track):
        # 0 = junto a la versión nueva (izquierda) … 1 = junto a la que había
        k = j / float(max(1, track - 1))
        if arrived:
            if j == mid:
                cells[(x0 + j, top + 1)] = ("✓", mix(CHECK_TONE, WHITE, 0.35 * pulse), None)
            else:
                cells[(x0 + j, top + 1)] = ("─", mix(BLACK, CHECK_TONE, 0.3 * k_in + 0.15), None)
        elif (j + shift) % 3 == 0:
            # arriba a la derecha, abajo a la izquierda
            cells[(x0 + j, top + 2 - int(k * 2.99))] = ("‹", mix(BLACK, CHECK_TONE, 0.55 + 0.45 * (1.0 - k)), None)
    return cells

def scene_ahead_cells(W, y0, a, b, lt, old="", new=""):
    """Escena de versión local adelantada (1.7.1), filas y0+5 … y0+7: la instalada (`new`, a la DERECHA) es MAYOR que la del último Release de GitHub (`old`, a la IZQUIERDA, tenue).
    Los chevrones › suben en diagonal (abajo a la izquierda → arriba a la derecha, el espejo de «Versión anterior») y, al llegar, ▲ en el centro mientras la versión local destella
    y se queda encendida. Mismo ciclo y escala que «actualizado» (WELCOME_CYCLE / WELCOME_BASE)."""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    old, new = clip_text(str(old or "").strip(), 7) or "?", clip_text(str(new or "").strip(), 7) or "?"
    wo, wn = max(9, dwidth(old) + 4), max(9, dwidth(new) + 4)
    track = max(7, min(15, room - wo - wn))
    total = wo + track + wn
    left, top = W // 2 + 1 - total // 2, y0 + 5
    cyc = (lt % WELCOME_CYCLE) * (WELCOME_BASE / WELCOME_CYCLE)         # en la escala de 2,4 s del dibujo
    arrived = cyc >= WELCOME_FLY
    k_in = smooth((cyc - WELCOME_FLY) / 0.25) if arrived else 0.0       # 0 = en camino … 1 = ya llegó
    pulse = max(0.0, 1.0 - (cyc - WELCOME_FLY) / 0.5) if arrived else 0.0
    dim = mix(BLACK, OLD_TONE, 0.55)
    _scene_chip(cells, left, top, wo, old, mix(dim, g(0.2), 0.35 * (1.0 - k_in)), mix(OLD_TONE, SCENE_WHITE, 0.25 * (1.0 - k_in)))      # el Release: tenue
    _scene_chip(cells, left + wo + track, top, wn, new, mix(mix(dim, g(0.85), 0.55 + 0.45 * k_in), WHITE, 0.6 * pulse), mix(OLD_TONE, SCENE_WHITE, 0.5 + 0.5 * k_in))    # la local: se enciende
    x0, mid = left + wo, track // 2
    shift = int(cyc * 10.0)
    for j in range(track):
        # 0 = junto al Release (izquierda) … 1 = junto a la versión local
        k = j / float(max(1, track - 1))
        if arrived:
            if j == mid:
                cells[(x0 + j, top + 1)] = ("▲", mix(SAVED_TONE, WHITE, 0.35 * pulse), None)
            else:
                cells[(x0 + j, top + 1)] = ("─", mix(BLACK, g(k), 0.3 * k_in + 0.15), None)
        elif (j - shift) % 3 == 0:
            cells[(x0 + j, top + int(round(2.0 - k * 2.0)))] = ("›", mix(BLACK, g(0.2 + 0.7 * k), 0.55 + 0.45 * k), None)      # abajo a la izquierda, arriba a la derecha
    return cells

def scene_same_cells(W, y0, a, b, lt, old="", new="", edited=False):
    """Escena de misma versión (1.6.5), filas y0+5 … y0+7: dos chips con la misma versión y, entre ellos, un puente ═ que un destello (un punto ●) recorre de lado a lado
    (comparando). En medio, «=» (el código es idéntico) o «≈» en ámbar (`edited`: misma versión con otro código). Cada vez que el destello toca un extremo, ese
    chip destella. Un ciclo (ida y vuelta) = WELCOME_CYCLE (escala WELCOME_BASE)."""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    old, new = str(old or "").strip()[:7] or "?", str(new or "").strip()[:7] or "?"
    wo, wn = max(9, len(old) + 4), max(9, len(new) + 4)
    track = max(7, min(15, room - wo - wn))
    total = wo + track + wn
    left, top = W // 2 + 1 - total // 2, y0 + 5
    cyc = (lt % WELCOME_CYCLE) * (WELCOME_BASE / WELCOME_CYCLE)         # en la escala de 2,4 s del dibujo
    ph = 2.0 * cyc / WELCOME_BASE                                       # 0 … 2: ida (0-1) y vuelta (1-2)
    pos = ph if ph <= 1.0 else 2.0 - ph                                 # 0 = izquierda … 1 = derecha
    sweep = pos * (track - 1)
    hit_l, hit_r = max(0.0, 1.0 - pos / 0.15), max(0.0, 1.0 - (1.0 - pos) / 0.15)
    dim = mix(BLACK, OLD_TONE, 0.55)
    tone = CHECK_TONE if edited else SAVED_TONE
    _scene_chip(cells, left, top, wo, old, mix(dim, mix(g(0.5), WHITE, 0.6), 0.45 + 0.55 * hit_l), mix(OLD_TONE, SCENE_WHITE, 0.6 + 0.4 * hit_l))
    _scene_chip(cells, left + wo + track, top, wn, new, mix(dim, mix(g(0.5), WHITE, 0.6), 0.45 + 0.55 * hit_r), mix(OLD_TONE, SCENE_WHITE, 0.6 + 0.4 * hit_r))
    x0, y, mid, near = left + wo, top + 1, track // 2, int(round(sweep))
    for j in range(track):
        glow = max(0.0, 1.0 - abs(j - sweep) / 2.5)
        if j == mid:
            cells[(x0 + j, y)] = ("≈" if edited else "=", mix(tone, WHITE, 0.5 * glow), None)
        # el destello: un punto que va y viene por el puente (se ve también sin color)
        elif j == near:
            cells[(x0 + j, y)] = ("●", mix(g(j / float(max(1, track - 1))), WHITE, 0.55), None)
        else:
            cells[(x0 + j, y)] = ("═", mix(BLACK, g(j / float(max(1, track - 1))), 0.25 + 0.75 * glow), None)
    return cells

DOWN_CYCLE = UX_CYCLE

DOWN_ROWS = 3                                       # 1.4.5: pistas que caben a la vez

DOWN_LABELS = {"video": "VIDEO", "audio": "AUDIO"}

PULSE_CYCLE = UX_CYCLE                                   # 1.4.5: s de un ciclo del Pulso (la onda cruza la línea)

def scene_down_rows(S):
    """1.4.5: [(etiqueta, avance 0-100 o None, estado)] de las pistas que se ven en «Descarga»; estado: «hecho», «activa» o «espera».
    Sale de lo que anota la escena (stream_total, stream_seen, skind, spct); lo que aún no empieza se adivina por el modo (video + audio)."""
    total = max(1, int(S.get("stream_total") or 1))
    seen = min(total, max(1, int(S.get("stream_seen") or 1)))
    kinds, pcts = S.get("skind") or {}, S.get("spct") or {}
    mode = S.get("mode_orig") or S.get("mode")
    first = min(max(1, seen - 1), max(1, total - DOWN_ROWS + 1))
    out = []
    for n in range(first, min(total, first + DOWN_ROWS - 1) + 1):
        k = kinds.get(n) or ("audio" if (mode == "audio" or (mode == "both" and n > 1)) else "video")
        pct = pcts.get(n)
        done = n < seen or (pct is not None and pct >= 100)
        out.append((t_display(DOWN_LABELS.get(k, "PISTA")), pct, "hecho" if done else ("activa" if n == seen else "espera")))
    return out

def scene_down_cells(W, y0, a, b, lt, rows):
    """Escena de descarga (1.4.5), filas y0+5 … y0+7: una fila por pista con su etiqueta, su vía y los paquetes ● • · que le llegan desde el
    final de la vía. 1.5.6: la vía de la pista activa no crece con el % (solo la cabeza y los paquetes; el avance lo lleva la regla de arriba);
    la hecha queda llena con su ✓ y la que espera, vacía. `rows` viene de scene_down_rows (su % ya no se usa aquí)."""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    rows = list(rows or [(t_display("VIDEO"), None, "activa")])[:DOWN_ROWS]
    # 1.7.0: la etiqueta traducida puede ser más ancha (ビデオ = 6 columnas)
    nw = max(5, min(8, max(dwidth(r_[0]) for r_ in rows)))
    bl = max(6, min(16, room - nw - 4))
    total = nw + 1 + bl + 2
    left, top = W // 2 + 1 - total // 2, y0 + 5
    ys = {1: (1,), 2: (0, 2)}.get(len(rows), (0, 1, 2))
    dim = mix(BLACK, OLD_TONE, 0.35)
    pulse = 0.5 + 0.5 * math.sin(lt * 4.0 * math.pi / DOWN_CYCLE)       # dos latidos por ciclo: el loop cierra limpio
    for i, ((label, pct, state), dy) in enumerate(zip(rows, ys)):
        y = top + dy
        ink = SCENE_WHITE if state == "activa" else mix(BLACK, OLD_TONE, 0.8 if state == "hecho" else 0.6)
        put_text(cells, left, y, label, ink, hi=left + nw)                  # 1.7.0: ancho real
        x0 = left + nw + 1
        if state == "hecho":
            fill = bl
        elif state == "espera":
            fill = 0
        else:
            # 1.5.6: sin avance en la vía (ni con total conocido): solo la cabeza, y los paquetes siguen llegando
            fill = 1
        for j in range(bl):
            k = j / float(max(1, bl - 1))
            if j < fill:
                head = state == "activa" and j == fill - 1
                col = mix(g(k), WHITE, 0.35 + 0.3 * pulse) if head else (mix(BLACK, g(k), 0.8) if state == "hecho" else g(k))
                cells[(x0 + j, y)] = ("━", col, None)
            else:
                cells[(x0 + j, y)] = ("─", dim, None)
        if state == "activa" and fill < bl:
            u = (lt / DOWN_CYCLE + i / 3.0) % 1.0
            span = bl - fill
            # sale del final de la vía y corre hacia la barra
            pj = int((bl - 1) - u * (span - 1) + 0.5) if span > 1 else fill
            for off, ch, mk in ((0, "●", None), (1, "•", 0.85), (2, "·", 0.55)):
                j = pj + off
                if fill <= j < bl:
                    kk = j / float(max(1, bl - 1))
                    cells[(x0 + j, y)] = (ch, mix(g(kk), WHITE, 0.7) if mk is None else mix(BLACK, g(kk), mk), None)
        if state == "hecho":
            cells[(x0 + bl + 1, y)] = ("✓", SAVED_TONE, None)
    return cells

def scene_idle_cells(W, y0, a, b, lt):
    """Pulso (1.4.5), fila y0+6: una línea fina de puntos con una onda del color del sitio que la cruza; es el reposo entre motivos."""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    n = max(9, min(21, room - 4))
    n -= 1 - n % 2                                                       # impar: el punto del medio cae en el centro
    left, y = W // 2 + 1 - n // 2, y0 + 6
    cyc = (lt % PULSE_CYCLE) / PULSE_CYCLE
    base = mix(BLACK, OLD_TONE, 0.35)
    for j in range(n):
        k = j / float(max(1, n - 1))
        near = max(0.0, 1.0 - abs(k - cyc) / 0.18)
        cells[(left + j, y)] = ("•" if near > 0.7 else "·", mix(base, g(k), near), None)
    return cells

def scene_site_center_cells(W, y0, a, b, ta, mode, asp, res, done, done_at, f, badge=None):
    """Centro del sitio. 1.0.3: ecualizador centrado. 1.4.2: devuelve siempre el dibujo ACTUAL (si una pista ya terminó, el de la que queda):
    el paso del uno al otro lo hace scene_motif con el motor de morph, una sola transición (`done_at` se conserva en la firma)."""
    cells = {}
    cx = W // 2 + 1
    g = lambda k: mix6(a, b, k)

    def bar_h(i, cnt, tt):
        return (math.sin(tt + i * 0.9) + math.sin(tt * 0.6 + i * 1.7) + 2) / 4

    tt = ta * 12.0                                    # 1.7.6: reloj continuo (antes a MOTIF_FPS)
    fd = 1.0
    bd = badge or {}                                  # 1.0.7: {"v"|"a"|"l": (texto, avance)}

    def video_cells_at(x_left, y_top, fw):
        return site_video_cells(x_left, y_top, fw, a, b, ta, fd, res, badge=bd.get("v"))

    def chip(key):                                    # la etiqueta bajo el dibujo (audio, directo, lista)
        v = bd.get(key)
        # 1.1.0: la de audio, justo en el centro del ecualizador
        return badge_cells(cx + (0 if key == "a" else 1), y + 4, v[0], v[1], ta, a, b, fd) if v else {}

    def audio_eq_cells_at(x_center, y_top, cnt=12):
        out = {}
        for i in range(cnt):
            bh = bar_h(i, cnt, tt)
            ch = "▁▂▃▄▅▆▇█"[int(round(bh * 7))]
            out[(x_center - cnt + i * 2, y_top)] = (ch, g(i / float(cnt)), None)
        return out

    def audio_tall_cells_at(x_left, y_top, cnt=5, rows=MOTIF_ROWS):
        out = {}
        for i in range(cnt):
            total = int(round(max(0.08, bar_h(i, cnt, tt)) * rows * 8))
            for r in range(rows):
                fill = total - (rows - 1 - r) * 8
                if fill > 0:
                    out[(x_left + i * 2, y_top + r)] = ("█" if fill >= 8 else "▁▂▃▄▅▆▇"[fill - 1], g(i / float(cnt)), None)
        return out

    y = y0 + 4

    if mode == "audio":
        # centrado real: cx+1 hace span -11..+11
        cells.update(audio_eq_cells_at(cx+1, y + 1, 12))
        for k, v in audio_eq_cells_at(cx+1, y + 2, 12).items():
            ch, col, _bg = v
            cells[k] = (ch, mix(BLACK, col, 0.3), None)
        cells.update(chip("a"))
        return cells
    if mode == "video":
        fw = site_frame_width(asp, W - 4)
        left = cx - fw // 2
        cells.update(video_cells_at(left, y, fw))
        return cells
    if mode == "both":
        gap, eqw = BOTH_GAP, BOTH_EQW
        fw = site_frame_width(asp, (W - 4) - (gap + eqw))
        both_w = fw + gap + eqw
        left_both = cx - both_w // 2

        both_cells = {}
        both_cells.update(video_cells_at(left_both, y, fw))
        both_cells.update(audio_tall_cells_at(left_both + fw + gap, y, 5, BOTH_BARS_ROWS))
        # 1.1.0: la etiqueta del audio, centrada bajo las barras
        if bd.get("a"):
            v_ = bd["a"]
            # 1.4.2: en la fila de la del video
            both_cells.update(badge_cells(left_both + fw + gap + 4, y + BADGE_ROW, v_[0], v_[1], ta, a, b, fd))

        video_only = video_cells_at(cx - fw // 2, y, fw)
        audio_only = {}
        audio_only.update(audio_eq_cells_at(cx+1, y + 1, 12))
        for k, v in audio_eq_cells_at(cx+1, y + 2, 12).items():
            ch, col, _bg = v
            audio_only[k] = (ch, mix(BLACK, col, 0.3), None)
        audio_only.update(chip("a"))

        done_video = "video" in done
        done_audio = "audio" in done
        if done_video and done_audio:
            return {}
        if done_video:
            # 1.4.2: sin transición propia: scene_motif hace el morph
            return audio_only
        if done_audio:
            return video_only
        return both_cells

    if mode == "list":
        for i in range(3):
            w = int(round(smooth(0.7) * 16))
            cells[(cx - 10, y + i + 1)] = ("●", g(i / 3.0), None)
            for j in range(w):
                cells[(cx - 8 + j, y + i + 1)] = ("▬", g((j + i * 4) / 24.0), None)
        cells.update(chip("l"))
        return cells
    r = int(ta * 9) % 3
    cells[(cx, y + 2)] = ("●", mix(BLACK, g(0.2), 0.6 + 0.4 * math.sin(ta * 18)), None)
    for s_ in (-1, 1):
        cells[(cx + s_ * (2 + r * 2), y + 2)] = ("(" if s_ < 0 else ")", mix(BLACK, g(0.6), 0.6 * (1 - r / 3.0)), None)
    cells.update(chip("l"))
    return cells

def scene_badge_texts(S, ta=None):
    """Textos de las etiquetas del dibujo del centro según lo que ya se sabe de lo que se baja (con ta, la del video fluye)."""
    return badge_texts(S.get("mode_orig") or S.get("mode"), S.get("res"), S.get("aspect"), S.get("alabel"), S.get("count"),
                       S.get("vinfo"), ta, S.get("ainfo"))

def scene_badge(S, st, ta):
    """{clave: (texto, avance)}: cuando un texto cambia (► → FHD, nada → M4A…) sale del ruido en SCENE_BADGE_SECS."""
    first, t0 = scene_badge_texts(S), st.setdefault("bdg_t0", {})
    # 1.1.0: la rotación arranca cuando aparece el primer dato (la resolución)
    for k in ("v", "a"):
        if k in first and first[k] != "►":
            t0.setdefault(k, ta)
        else:
            t0.pop(k, None)
    cur = scene_badge_texts(S, {k: ta - t0[k] for k in t0})
    mem, out = st.setdefault("bdg", {}), {}
    for k, txt in cur.items():
        m = mem.get(k)
        if m is None:
            m = mem[k] = [txt, None]
        elif m[0] != txt:
            m[0], m[1] = txt, ta
        out[k] = (txt, 1.0 if m[1] is None else max(0.0, min(1.0, (ta - m[1]) / SCENE_BADGE_SECS)))
    for k in [k for k in mem if k not in cur]:
        del mem[k]
    return out

class _MotifCtx:
    """Lo que un dibujo necesita de este cuadro: geometría, colores, tiempo, etiquetas y qué streams ya acabaron."""
    __slots__ = ("W", "y0", "a", "b", "ta", "f", "bdg", "done")

    def __init__(self, W, y0, a, b, ta, f, bdg, done):
        self.W, self.y0, self.a, self.b, self.ta, self.f, self.bdg, self.done = W, y0, a, b, ta, f, bdg, done

class _Motif:
    """Una fila del registro: draw(S, st, d, start) → celdas; loop(S, st, W, lt) → s que le faltan a su loop; real(S, st, lt) → tiempo del dibujo."""
    __slots__ = ("draw", "loop", "real", "light")

    def __init__(self, draw, loop=None, real=None, light=False):
        self.draw, self.loop, self.real, self.light = draw, loop, real, light

def _site_center(S, W, y0, ta, f, bdg, done, done_at):
    """1.4.1: el dibujo del sitio (marco, ecualizador, lista o directo); antes la misma llamada larga estaba escrita cuatro veces."""
    return scene_site_center_cells(W, y0, S["a"], S["b"], ta, S.get("mode_orig") or S.get("mode"), S.get("asp_shown") or S.get("aspect"),
                                   S.get("res"), done, done_at, f, badge=bdg)

def _draw_site(S, st, d, start):
    return _site_center(S, d.W, d.y0, d.ta, d.f, d.bdg, d.done, S.get("done_at") or {})

def _draw_dlpy(S, st, d, start):
    # 1.3.3: el texto de estado manda mientras D L P Y es lo actual…
    if S.get("brand"):
        lab = S.get("label") or ""
        st["dl_last"] = lab
    # …y al deshacerse el dibujo conserva su comando (no pasa a «python dlpy.py»)
    else:
        lab = st.get("dl_last") or S.get("label") or ""
    if st.get("dl_lab") != lab:
        st["dl_lab"], st["dl_seen"] = lab, d.ta                        # 1.3.3: cuándo vio la escena este texto
    enter = st["mt"] if (start == st["ms"] and st.get("mt") is not None) else start
    # el comando se teclea desde que se ve, no desde que cambió el texto
    tt = dlpy_type_time(d.ta, st["dl_seen"], enter)
    if S.get("brand") and tt >= (TYPE_STEP_SECS if _dlpy_state(lab) == "run" else 0.0):
        # ya se mostró entero: el flujo puede pasar al siguiente texto
        S["dl_done"] = lab
    return scene_dlpy_cells(d.W, d.y0, d.a, d.b, d.ta - start, HOST_VERSION, lab, tt)

def _draw_conv(S, st, d, start):
    src, dst, _t0 = st.get("cinfo") or (None, None, d.ta)
    # 1.2.8: empieza desde el principio
    t0 = st["mt"] if (start == st["ms"] and st.get("mt") is not None) else start
    kf = st.get("key_fade_t")
    kf = None if kf is None else 1.0 - (d.ta - kf) / CONV_KEY_FADE
    cv = S.get("conv") or {}
    pct, fast = cv.get("pct"), bool(S.get("fast"))
    tgt = 1.0 if cv.get("end") is not None else (None if pct is None else max(0.0, min(100.0, float(pct))) / 100.0)
    # 1.6.4: sin % conocido (o un encoder nuevo): la vía vuelve a empezar
    if tgt is None:
        st["conv_p"] = None
    # los puntos se llenan hacia el % real; en convert_fast_anim, de golpe (no hay cuadros entre uno y otro)
    else:
        prev = st.get("conv_p")
        cur = tgt if (prev is None or fast) else scene_ease(prev, tgt, CONV_FILL_RATE, max(0.0, d.ta - st.get("conv_pt", d.ta)))
        st["conv_p"] = tgt if abs(tgt - cur) < 0.003 else cur
    st["conv_pt"] = d.ta
    # 1.6.4: puntos que se pintan, no paquetes en loop
    return scene_conv_cells(d.W, d.y0, d.a, d.b, d.ta - t0, src, dst, pct, kf, fill=st["conv_p"], fast=fast)

def _draw_ask(S, st, d, start):                                       # 1.1.9
    ak = S.get("ask") or st.get("ask_last") or {}
    st["ask_last"] = ak
    left = max(0.0, float(ak.get("secs") or 0) - (time.time() - float(ak.get("t0") or time.time()))) if ak else 99.0
    return scene_wait_conv_cells(d.W, d.y0, d.a, d.b, d.ta - start, ak.get("src"), ak.get("dst"), left)

def _draw_replace(S, st, d, start):                                   # 1.4.2: la pregunta de sustituir un archivo
    ak = S.get("ask") or st.get("ask_last") or {}
    st["ask_last"] = ak
    left = max(0.0, float(ak.get("secs") or 0) - (time.time() - float(ak.get("t0") or time.time()))) if ak else 99.0
    return scene_wait_conv_cells(d.W, d.y0, d.a, d.b, d.ta - start, ak.get("src") or ux_chip("VIEJO"), ak.get("dst") or ux_chip("NUEVO"), left, swap=True)

def _draw_subst(S, st, d, start):                                      # 1.4.2: sustituyendo al guardar
    return scene_subst_cells(d.W, d.y0, d.a, d.b, d.ta - start)

def _draw_check(S, st, d, start):                                     # 1.2.5
    ck = S.get("check") or {}
    # 1.6.2: el parpadeo empieza en el primer cuadro que de verdad pinta el veredicto con el dibujo ya dentro (no cuando se llamó a scene_check)
    if ck.get("verdict") is not None and ck.get("t") is None:
        mv = S.get("mvis")
        if mv and mv[0] == "check" and mv[1]:
            ck["t"] = d.ta
    t_v = ck.get("t")                                                 # 1.6.1: cuándo se vio lo detectado (parpadeo)
    return scene_check_cells(d.W, d.y0, d.a, d.b, d.ta - start, ck.get("items"), ck.get("verdict"),
                             None if t_v is None else d.ta - t_v)

def _draw_merge(S, st, d, start):                                     # 1.1.3
    return scene_merge_cells(d.W, d.y0, d.a, d.b, scene_real_lt(S, st, "merge", d.ta - start))

def _draw_save(S, st, d, start):
    return scene_save_cells(d.W, d.y0, d.a, d.b, d.ta - start)

def _draw_clean(S, st, d, start):                                     # 1.1.5
    return scene_clean_cells(d.W, d.y0, d.a, d.b, d.ta - start, S.get("clean") or 0)

def _draw_empty(S, st, d, start):                                     # 1.1.7
    return scene_empty_cells(d.W, d.y0, d.a, d.b, d.ta - start, S.get("clean") or 0)

def _draw_send(S, st, d, start):
    # 1.3.4: el chip es el destino real (atajo o VIEW)
    return scene_send_cells(d.W, d.y0, d.a, d.b, d.ta - start, scene_chip_text(S.get("send_to") or SHORTCUT_NAME))

def _draw_first(S, st, d, start):                                     # 1.2.9
    return scene_first_cells(d.W, d.y0, d.a, d.b, d.ta - start)

def _draw_updated(S, st, d, start):
    wl = S.get("welcome") or st.get("welcome_last") or {}
    st["welcome_last"] = wl
    return scene_updated_cells(d.W, d.y0, d.a, d.b, d.ta - start, wl.get("old"), wl.get("new"))

def _draw_downgrade(S, st, d, start):                                 # 1.6.5
    wl = S.get("welcome") or st.get("welcome_last") or {}
    st["welcome_last"] = wl
    return scene_downgrade_cells(d.W, d.y0, d.a, d.b, d.ta - start, wl.get("old"), wl.get("new"))

def _draw_ahead(S, st, d, start):                                     # 1.7.1
    wl = S.get("welcome") or st.get("welcome_last") or {}
    st["welcome_last"] = wl
    return scene_ahead_cells(d.W, d.y0, d.a, d.b, d.ta - start, wl.get("old"), wl.get("new"))

def _draw_same(S, st, d, start):                                      # 1.6.5
    wl = S.get("welcome") or st.get("welcome_last") or {}
    st["welcome_last"] = wl
    return scene_same_cells(d.W, d.y0, d.a, d.b, d.ta - start, wl.get("old"), wl.get("new"), bool(wl.get("edited")))

def _draw_download(S, st, d, start):                                   # 1.4.5
    return scene_down_cells(d.W, d.y0, d.a, d.b, d.ta - start, scene_down_rows(S))

def _draw_idle(S, st, d, start):                                       # 1.4.5
    return scene_idle_cells(d.W, d.y0, d.a, d.b, d.ta - start)

RAIL_MAX, RAIL_GAP = 3, 2                           # tarjetas a la vez y columnas entre ellas

RAIL_KINDS = ("download", "merge", "save")           # los dibujos de 1.4.5 que ahora viven dentro del carril

RAIL_MOVE = 14.0

RAIL_EXIT_V0, RAIL_EXIT_ACC = 62.0, 170.0

RAIL_DONE_HOLD = 0.14

RAIL_FADE_IN = 0.15                                 # s que tarda en aparecer una tarjeta que entra (1.5.5: 0.3 → 0.15)

RAIL_TITLE_T = 0.5

RAIL_EXIT_T = 0.28

RAIL_EXIT_FADE = 0.35

RAIL_SPIN = 14.0                                    # celdas/s del destello que recorre el marco del video

RAIL_LABELS = {"video": "VIDEO", "audio": "AUDIO", "merge": "UNIÓN", "save": "GUARDADO"}

def rail_hold(mode=None, card=None):
    """1.4.8 / 1.8.2: s que se queda el ✓ antes de salir.
    Misma regla para todas las tarjetas (video, audio, unión, guardado): un destello corto y fuera,
    la misma física de salida. En «real» no espera; con segundos fijos respeta ese tope."""
    mode = mode or SCENE_MODE
    if mode[0] == "real":
        return 0.0
    if mode[0] == "secs":
        return min(10.0, float(mode[1]))
    # wait: hold corto fijo (como se percibe el ✓ del video al terminar, sin pausa larga)
    return RAIL_DONE_HOLD

def rail_width(W):
    """1.4.6: ancho fijo de una tarjeta: caben RAIL_MAX en la escena (entre 8 y 16 columnas)."""
    return max(8, min(16, (W - 4 - (RAIL_MAX - 1) * RAIL_GAP) // RAIL_MAX))

def rail_want(S):
    """1.4.6: las tarjetas que pide el estado de la escena, de izquierda a derecha: [{id, kind, pct, state}] con state «activa», «espera» o «hecho».
    1.4.9: UNA tarjeta por tipo de archivo (video · audio): reúne sus pistas; el % y el idioma son los de la pista en curso (idx de of). Unión y
    guardado, igual. Las pistas que aún no empiezan se adivinan por el modo. Pura."""
    label = str(S.get("label") or "")
    out = []
    if S.get("past_dl") or label.startswith("Descargando"):
        total = min(12, max(1, int(S.get("stream_total") or 1)))
        seen = min(total, max(1, int(S.get("stream_seen") or 1)))
        kinds, pcts = S.get("skind") or {}, S.get("spct") or {}
        mode = S.get("mode_orig") or S.get("mode")
        # el flujo ya pasó a otra cosa: todas las pistas están hechas
        left = not label.startswith("Descargando")
        langs, groups = S.get("slang") or {}, {}
        for n in range(1, total + 1):
            k = kinds.get(n) or ("audio" if (mode == "audio" or (mode == "both" and n > 1)) else "video")
            pct = pcts.get(n)
            done = left or n < seen or (pct is not None and pct >= 100)
            groups.setdefault(k, []).append({"n": n, "pct": pct, "done": done, "lang": langs.get(n)})
        # 1.4.9: el orden de aparición (la primera pista de cada tipo)
        for k, tr in groups.items():
            alld = all(t["done"] for t in tr)
            pos = next((i for i, t in enumerate(tr) if not t["done"]), len(tr) - 1)
            cur = tr[pos]
            started = any(t["n"] <= seen for t in tr)
            out.append({"id": k, "kind": k, "pct": cur["pct"], "state": "hecho" if alld else ("activa" if started else "espera"),
                        "lang": cur["lang"], "idx": pos + 1, "of": len(tr)})
    if label.startswith(("Uniendo", "Ajustando")):
        out.append({"id": "merge", "kind": "merge", "pct": S.get("pp_pct"), "state": "activa"})
    # 1.8.5: no hay tarjeta activa de guardado; no existe progreso real que representar.
    return out

def rail_title(c, cw):
    """1.4.9: el título de una tarjeta (la fila justo sobre el dibujo): «VIDEO», «AUDIO ES-US» (si no cabe, solo «ES-US»), sin idioma y con
    varias pistas «AUDIO 2». Cambia de pista en pista; el cambio se desliza (rail_title_draw)."""
    text = t_display(RAIL_LABELS.get(c.get("kind"), "PISTA"))
    if c.get("kind") != "audio":
        return text
    lang = str(c.get("lang") or "").upper()
    if lang:
        return (text + " " + lang) if dwidth(text) + 1 + dwidth(lang) <= cw else lang
    tag = str(int(c.get("idx") or 1))
    return (text + " " + tag) if int(c.get("of") or 1) > 1 and dwidth(text) + 1 + dwidth(tag) <= cw else text

def _rail_title_sync(c, w, cw, ta):
    """1.4.9: la tarjeta toma pista, idioma y orden de lo que pide el estado; si su título cambia, el viejo se queda para deslizarse fuera."""
    c["lang"], c["idx"], c["of"] = w.get("lang"), w.get("idx", 1), w.get("of", 1)
    text = rail_title(c, cw)
    if c.get("title") is None:
        c["title"] = text
    elif text != c["title"]:
        c["title_old"], c["title"], c["title_t"] = c["title"], text, ta

def _rail_finish(c, ta):
    if c["state"] != "hecho":
        c["state"], c["done_t"] = "hecho", ta
        if c["pct"] is not None:
            c["pct"] = 100.0

def _rail_exit(c, ta, side):
    c["exit"], c["exit_t"] = side, ta

def rail_step(S, st, W, ta, start):
    """1.4.6: pone al día el carril de este cuadro (entradas, salidas y posiciones) y lo devuelve. El estado vive en st["rail"]; se reinicia cuando el
    carril vuelve a ser el dibujo del centro (otro `start`)."""
    R = st.get("rail")
    if R is None or R["start"] != start:
        R = st["rail"] = {"start": start, "cards": [], "gone": set(), "t": None, "first": True, "move": False}
    dt = 0.0 if R["t"] is None else max(0.0, min(0.25, ta - R["t"]))
    R["t"] = ta
    cw = rail_width(W)
    want = rail_want(S)
    wid = {w["id"]: w for w in want}
    cards = R["cards"]
    # 1) lo que pide el estado, sobre las tarjetas que ya hay
    for c in cards:
        if c["exit"] or c["state"] == "hecho":
            continue
        w = wid.get(c["id"])
        if w is None:
            if c["state"] == "espera":
                _rail_exit(c, ta, "left")                        # ya no hace falta y nunca empezó: se va sin ceremonia
            else:
                _rail_finish(c, ta)
        elif w["state"] == "hecho":
            c["pct"] = w["pct"]
            _rail_title_sync(c, w, cw, ta)
            _rail_finish(c, ta)
        else:
            if w["state"] == "activa" and c["state"] == "espera":
                # 1.7.5: el instante en que se enciende (rail_tone_shift)
                c["act_t"] = ta
            c["pct"], c["state"] = w["pct"], w["state"]
            _rail_title_sync(c, w, cw, ta)
    # 2) el ✓ se ve un instante y la tarjeta sale por la derecha
    for c in cards:
        if not c["exit"] and c["state"] == "hecho" and ta - c["done_t"] >= rail_hold(card=c):
            # 1.5.5: lo terminado sale por la izquierda (antes por la derecha) · 1.8.2: hold adaptativo
            _rail_exit(c, ta, "left")
    live = [c for c in cards if not c["exit"]]
    known = {c["id"] for c in cards} | R["gone"]
    # 3) tarjetas nuevas: entran por la derecha; si no caben, la más antigua sale por la izquierda
    for w in want:
        if w["id"] in known or w["state"] == "hecho":
            continue
        if len(live) >= RAIL_MAX:
            if w["state"] != "activa":
                continue                                         # una que aún espera no desplaza a nadie
            victim = next((c for c in live if c["state"] != "activa"), live[0])
            _rail_exit(victim, ta, "left")
            live.remove(victim)
        c = {"id": w["id"], "kind": w["kind"], "pct": w["pct"], "state": w["state"], "lang": w.get("lang"), "idx": w.get("idx", 1), "of": w.get("of", 1), "title": None, "x": None, "tx": 0.0, "fade": 1.0 if R["first"] else 0.0,
             "exit": None, "exit_t": None, "done_t": None, "born": ta, "act_t": ta if w["state"] == "activa" else None}
        _rail_title_sync(c, w, cw, ta)
        cards.append(c)
        live.append(c)
        R["gone"].add(w["id"])
    n = len(live)
    left0 = W // 2 + 1 - (n * cw + max(0, n - 1) * RAIL_GAP) // 2
    for i, c in enumerate(live):
        c["tx"] = float(left0 + i * (cw + RAIL_GAP))
        if c["x"] is None:
            c["x"] = c["tx"] if R["first"] else float(W + 1)
    k, moving = 1.0 - math.exp(-RAIL_MOVE * dt), False
    for c in cards:                                              # 4) movimiento
        if c["exit"]:
            v = RAIL_EXIT_V0 + RAIL_EXIT_ACC * (ta - c["exit_t"])
            c["x"] += (1.0 if c["exit"] == "right" else -1.0) * v * dt
            moving = True
            continue
        gap_ = c["tx"] - c["x"]
        if abs(gap_) < 0.02:
            c["x"] = c["tx"]
        else:
            c["x"] += gap_ * k
            moving = True
        if c["fade"] < 1.0:
            c["fade"] = min(1.0, c["fade"] + dt / RAIL_FADE_IN)
            moving = True
        if c.get("title_t") is not None and ta - c["title_t"] < RAIL_TITLE_T:
            moving = True                                        # 1.4.9: el título que se desliza también pide cuadros
    R["cards"] = [c for c in cards if not ((c["exit"] == "right" and c["x"] >= W) or (c["exit"] == "left" and c["x"] + cw <= 0))]
    R["move"], R["first"] = moving, False
    return R

def rail_loop(S, st, W, lt):
    """1.4.6: s que le faltan al carril para quedar quieto (✓ de la tarjeta que acaba + su salida); el carril no se deshace antes (regla del loop).
    1.8.2: usa el hold adaptativo por tarjeta."""
    R = st.get("rail")
    if not R:
        return 0.0
    now, rem = R["t"] or 0.0, 0.0
    for c in R["cards"]:
        if c["exit"]:
            dist = (W - c["x"]) if c["exit"] == "right" else (c["x"] + rail_width(W))
            rem = max(rem, max(0.0, dist) / (RAIL_EXIT_V0 + RAIL_EXIT_ACC * 0.4))
        elif c["state"] == "hecho":
            rem = max(rem, max(0.0, c["done_t"] + rail_hold(card=c) - now) + RAIL_EXIT_T)
        else:
            rem = max(rem, rail_hold(card=c) + RAIL_EXIT_T)
        # 1.4.9: el título a medio deslizar termina antes de deshacer el carril
        if c.get("title_t") is not None:
            rem = max(rem, c["title_t"] + RAIL_TITLE_T - now)
    return rem

def style_label(put, x0, w, y, text, state, dx=0, fade=1.0):
    """1.4.8: la etiqueta de un proceso, centrada en las `w` columnas desde x0. 1.4.9: `dx` la corre y `fade` (0 a 1) la apaga; lo que queda
    fuera de las `w` columnas no se pinta (así el título se desliza dentro de su tarjeta)."""
    col = SCENE_WHITE if state == "activa" else mix(BLACK, OLD_TONE, 0.8 if state == "hecho" else 0.6)
    if fade < 0.999:
        col = mix(BLACK, col, max(0.0, fade))
    text = clip_text(text, w)
    tmp = {}
    # 1.7.0: ancho real (ja/zh/ko = 2 columnas)
    put_text(tmp, x0 + (w - dwidth(text)) // 2 + dx, y, text, col, lo=x0, hi=x0 + w)
    for (xx, yy), (ch, cc, _bg) in tmp.items():
        put(xx, yy, ch, cc)

def rail_title_draw(put, x0, cw, y, c, state, ta):
    """1.4.9: el título de la tarjeta; si la pista cambió, el viejo se va por la IZQUIERDA y el nuevo entra por la DERECHA (uno empuja al otro, con
    el mismo fundido y la misma curva que las tarjetas del carril), todo dentro de las `cw` columnas de la tarjeta."""
    text, old, t0 = rail_title(c, cw), c.get("title_old"), c.get("title_t")
    p = 1.0 if (old is None or t0 is None) else max(0.0, min(1.0, (ta - t0) / RAIL_TITLE_T))
    if p >= 1.0:
        style_label(put, x0, cw, y, text, state)
        return
    e = FLOW_EASE(p)
    style_label(put, x0, cw, y, old, state, dx=-int(round(e * cw)), fade=1.0 - e)
    style_label(put, x0, cw, y, text, state, dx=int(round((1.0 - e) * cw)), fade=e)

def style_status(put, x0, w, y, state, pct, lt, text=None):
    """1.4.8: el estado bajo el dibujo: ✓ · «espera» · (1.5.6: ya sin % ni puntos) solo el `text` que se pida mientras está activa."""
    if state == "hecho":
        line, col = "✓", SAVED_TONE
    elif state == "espera":
        line, col = text or t_display("espera"), mix(BLACK, OLD_TONE, 0.35)
    else:
        # 1.5.6: nunca un % (ni puntos de avance): solo el dato que se pida
        line, col = text or "", SCENE_GRAY
    line = clip_text(line, w)
    tmp = {}
    put_text(tmp, x0 + (w - dwidth(line)) // 2, y, line, col, lo=x0, hi=x0 + w)      # 1.7.0: ancho real
    for (xx, yy), (ch, cc, _bg) in tmp.items():
        put(xx, yy, ch, cc)

COMET_TAIL = 9.0

def comet_glow(head, idx, n, tail=COMET_TAIL):
    """1.7.6: brillo (0 a 1) de la celda `idx` de un recorrido de `n` celdas con el cometa en `head` (posición con decimales): la cabeza llega a 1 y la cola se apaga con
    curva cuadrática en `tail` celdas; la celda que está a punto de recibirlo se enciende antes (a menos de una celda), así el cometa no salta de celda en celda. Pura."""
    d = (head - idx) % n
    if d > n - 1.0:
        return d - (n - 1.0)
    return 0.0 if d >= tail else (1.0 - d / tail) ** 2

RAIL_TONE_T = MOTION_BASE

RAIL_FLASH = 0.85

def rail_tone_shift(cells, c, ta, ty):
    """1.7.5: transición de color de una tarjeta, con la curva del resto del carril (FLOW_EASE): al pasar de «espera» a «activa» sus tonos suben
    desde el apagado (antes saltaban de golpe) y al terminar un destello blanco-verde se asienta en el verde de «hecho»; el título pasa del
    blanco al gris apagado sin corte. Pura: devuelve las celdas con el color ya movido (la misma tabla si no hay transición en curso)."""
    state = c.get("state")
    t0 = c.get("act_t") if state == "activa" else c.get("done_t") if state == "hecho" else None
    if t0 is None:
        return cells
    k = max(0.0, min(1.0, (ta - t0) / RAIL_TONE_T))
    if k >= 1.0:
        return cells
    e = FLOW_EASE(k)
    glow = mix(SAVED_TONE, WHITE, 0.75)
    out = {}
    for pos, (ch, col, bg) in cells.items():
        if ch == " " or not ch:
            out[pos] = (ch, col, bg)
        elif state == "activa":
            out[pos] = (ch, mix(mix(BLACK, col, 0.3), col, e), bg)
        # el título: del blanco de «activa» al gris de «hecho»
        elif pos[1] == ty:
            out[pos] = (ch, mix(SCENE_WHITE, col, e), bg)
        else:
            out[pos] = (ch, mix(col, glow, RAIL_FLASH * (1.0 - e)), bg)
    return out

def rail_card_cells(c, y0, a, b, ta, cw, badge=None):
    """1.4.6: una tarjeta del carril en sus 6 filas (y0+4 … y0+9): etiqueta, dibujo de 3 filas, aire y texto de estado.
    1.8.2: el aire global bajo la tarjeta lo da SCENE_STATUS_ROW (más holgado)."""
    cells = {}
    g = lambda k: mix6(a, b, k)
    state, kind, pct = c["state"], c["kind"], c["pct"]
    # 1.7.5: la aparición sigue la curva del carril (antes, lineal)
    fd = FLOW_EASE(max(0.0, min(1.0, c["fade"])))
    if c["exit"] and state == "hecho":
        # 1.8.2: fundido más corto; lo terminado se apaga al irse
        fd *= 1.0 - 0.55 * FLOW_EASE(min(1.0, (ta - c["exit_t"]) / RAIL_EXIT_FADE))
    lt, x0, ty = max(0.0, ta - c["born"]), int(round(c["x"])), y0 + 4
    dim = mix(BLACK, OLD_TONE, 0.35)
    okd = mix(BLACK, SAVED_TONE, 0.8)

    def put(x, y, ch, col):
        cells[(x, y)] = (ch, col if fd >= 0.999 else mix(BLACK, col, fd), None)

    # 1.4.9: «AUDIO ES-US» → «AUDIO EN-US» deslizándose, pista a pista
    rail_title_draw(put, x0, cw, ty, c, state, ta)
    iw = min(11, cw if cw % 2 else cw - 1)
    ix = x0 + (cw - iw) // 2
    pulse = 0.5 + 0.5 * math.sin(lt * 6.0)
    if kind == "video":                                          # marco con un destello que lo recorre y el ► en medio
        per = [(i, 0, "╭" if i == 0 else "╮" if i == iw - 1 else "─") for i in range(iw)] + [(iw - 1, 1, "│")] \
            + [(i, 2, "╰" if i == 0 else "╯" if i == iw - 1 else "─") for i in range(iw - 1, -1, -1)] + [(0, 1, "│")]
        head = (lt * RAIL_SPIN) % len(per)
        for idx, (dx, dy, gl) in enumerate(per):
            # 1.9.7: el degradado va y vuelve (0 → 1 → 0) para que el marco, que es un lazo cerrado, no tenga costura en la esquina ╭
            k = 1.0 - abs(2.0 * idx / float(len(per)) - 1.0)
            if state == "activa":
                # 1.7.6: cabeza viva y cola larga que se apaga con curva (antes 6 celdas lineales)
                lit = comet_glow(head, idx, len(per))
                # 1.7.6: el marco activo, más claro (0.38 → 0.5)
                col = mix(mix(BLACK, g(k), 0.5), mix(g(k), WHITE, 0.6), lit)
            else:
                col = okd if state == "hecho" else dim
            put(ix + dx, ty + 1 + dy, gl, col)
        # 1.5.9: el ✓ va solo en la fila de estado (antes también aquí, repetido)
        put(ix + iw // 2, ty + 2, "►",
            okd if state == "hecho" else (mix(g(0.5), WHITE, 0.4 + 0.4 * pulse) if state == "activa" else dim))
    # 1.4.9: un solo dibujo para todas las pistas de audio: el ecualizador
    elif kind == "audio":
        base = okd if state == "hecho" else dim
        cnt = min(5, (iw + 1) // 2)
        bx = ix + (iw - (cnt * 2 - 1)) // 2
        tt = lt * 9.0                                          # 1.7.6: reloj continuo (antes a MOTIF_FPS)
        for i in range(cnt):
            if state == "activa":
                h = (math.sin(tt + i * 0.9) + math.sin(tt * 0.6 + i * 1.7) + 2) / 4
            elif state == "hecho":
                h = 1.0 - abs(i - (cnt - 1) / 2.0) / float(cnt)
            else:
                h = 0.0
            total = int(round(max(0.08, h) * 24))
            col = g(i / float(cnt)) if state == "activa" else base
            for r in range(3):
                fill = total - (2 - r) * 8
                if fill > 0:
                    put(bx + i * 2, ty + 1 + r, "█" if fill >= 8 else "▁▂▃▄▅▆▇"[fill - 1], col)
    # dos vías (video arriba, audio abajo) que se juntan en una
    elif kind == "merge":
        lane = (iw - 1) // 2
        merged = iw - 1 - lane
        jx = ix + lane
        for j in range(lane + 1 + merged):
            k = j / float(max(1, iw - 1))
            ph = (j - lt * MERGE_SPEED) % 4.0
            if j < lane:
                if state == "activa":
                    put(ix + j, ty + 1, ("█" if ph < 1.0 else "▓") if ph < 2.0 else "─", mix(g(0.12), WHITE, 0.25 * k) if ph < 2.0 else mix(BLACK, g(0.12), 0.3))
                    h = (math.sin((j - lt * MERGE_SPEED) * 1.3) + 1.0) / 2.0
                    put(ix + j, ty + 3, "▁▂▃▄▅▆▇█"[min(7, int(h * 8.0))], mix(g(0.88), WHITE, 0.25 * k))
                else:
                    put(ix + j, ty + 1, "─", dim)
                    put(ix + j, ty + 3, "─", dim)
            elif j > lane:
                if state == "activa":
                    put(ix + j, ty + 2, (("█" if ph < 1.0 else "▓") if ph < 2.0 else "─"), g(0.12 + 0.76 * k))
                else:
                    put(ix + j, ty + 2, "━" if state == "hecho" else "─", okd if state == "hecho" else dim)
        jc = mix(g(0.5), WHITE, 0.45 + 0.35 * pulse) if state == "activa" else (okd if state == "hecho" else dim)
        put(jx, ty + 1, "╮", jc)
        put(jx, ty + 2, "├", jc)
        put(jx, ty + 3, "╯", jc)
    else:                                                          # guardado: bloques que caen a la bandeja
        cols = [ix + 2, ix + iw // 2, ix + iw - 3] if iw >= 9 else [ix + 2, ix + iw - 3]
        for j in range(iw):
            put(ix + j, ty + 3, "╰" if j == 0 else "╯" if j == iw - 1 else "─", okd if state == "hecho" else dim)
        put(ix, ty + 2, "│", okd if state == "hecho" else dim)
        put(ix + iw - 1, ty + 2, "│", okd if state == "hecho" else dim)
        if state == "hecho":
            for j in range(1, iw - 1):
                put(ix + j, ty + 3, "━", okd)
            # 1.5.9: el archivo ya en la bandeja; el ✓ va solo en la fila de estado
            put(ix + iw // 2, ty + 2, "▓", okd)
        elif state == "activa":
            for i, cx_ in enumerate(cols):
                r = int((((lt * 1.6) + i / float(len(cols))) % 1.0) * 3.0)
                col = g(0.2 + 0.7 * i / float(max(1, len(cols) - 1)))
                if r < 2:
                    put(cx_, ty + 1 + r, "▒" if r == 0 else "▓", col)
                else:
                    put(cx_, ty + 3, "━", mix(col, WHITE, 0.4))
    # 1.5.6: sin barra de progreso ni % en la tarjeta (los lleva la regla de arriba y el % del final)
    txt = None
    if state == "activa":
        bt = (badge or {}).get("v" if kind == "video" else "a" if kind == "audio" else "")
        bt = bt[0] if bt and bt[0] and bt[0] != "►" else ""
        # 1.5.0: sin % (lo lleva la barra y el estado de la escena): solo el dato del archivo
        txt = bt if (bt and dwidth(bt) <= cw) else " "
    style_status(put, x0, cw, ty + 5, state, pct, lt, txt)
    # 1.7.5: se enciende al empezar y destella al terminar
    return rail_tone_shift(cells, c, ta, ty)

def scene_rail_cells(W, y0, a, b, cards, ta, badge=None):
    """1.4.6: todas las tarjetas del carril (las que salen, debajo) recortadas a la pantalla (columnas 1 … W-1)."""
    cells, cw = {}, rail_width(W)
    live = [(int(round(c_["x"])), int(round(c_["x"])) + cw) for c_ in cards if not c_["exit"]]
    for c in sorted(cards, key=lambda c_: 0 if c_["exit"] else 1):
        one = rail_card_cells(c, y0, a, b, ta, cw, badge)
        if c["exit"]:                                              # la que sale pasa POR DETRÁS de las que se quedan
            one = {k: v for k, v in one.items() if not any(l_ <= k[0] < r_ for l_, r_ in live)}
        cells.update(one)
    return {k: v for k, v in cells.items() if 1 <= k[0] < W}

def _draw_rail(S, st, d, start):                                       # 1.4.6
    R = rail_step(S, st, d.W, d.ta, start)
    if R["move"]:
        # mientras se deslizan, a tope de cuadros (scene_fps)
        st["rail_fast"] = d.ta + 0.2
    return scene_rail_cells(d.W, d.y0, d.a, d.b, R["cards"], d.ta, d.bdg)

CHROME_PARTS = {"conv": "ls", "subst": "ls", "check": "ls", "merge": "ls", "save": "ls", "clean": "ls", "empty": "ls", "send": "ls",
                "ask": "ls", "replace": "ls", "first": "l", "updated": "l", "downgrade": "l", "same": "l", "ahead": "l"}

def chrome_state(kind, S, st, lt):
    """1.4.8: (estado, avance) del proceso de un dibujo a todo ancho: la conversión y la unión llevan su % real, guardar y sustituir terminan
    solas, la revisión termina con su veredicto, la espera de Enter cuenta atrás y lo demás no tiene avance conocido."""
    if kind == "conv":
        return "activa", (S.get("conv") or {}).get("pct")
    if kind == "merge":
        return "activa", S.get("pp_pct")
    if kind == "save":
        return ("hecho", 100.0) if lt >= SAVE_STREAM_SECS else ("activa", None)
    if kind == "subst":
        return ("hecho", 100.0) if lt >= SWAP_STREAM_SECS else ("activa", None)
    if kind == "check":
        return ("hecho", 100.0) if (S.get("check") or {}).get("verdict") is not None else ("activa", None)
    if kind in ("ask", "replace"):
        ak = S.get("ask") or st.get("ask_last") or {}
        secs = float(ak.get("secs") or 0)
        left = max(0.0, secs - (time.time() - float(ak.get("t0") or time.time()))) if secs else 0.0
        return "espera", (left / secs * 100.0 if secs else None)
    return "activa", None

def scene_chrome(kind, cells, S, st, d, start):
    """1.4.8: pone al dibujo `kind` la etiqueta, la barra y el estado del estilo de la escena en las filas libres (y0+4, y0+8, y0+9)."""
    parts = CHROME_PARTS.get(kind)
    if not parts or not cells:
        return cells
    y0, cx = d.y0, d.W // 2 + 1
    lt = max(0.0, d.ta - start)
    state, pct = chrome_state(kind, S, st, lt)
    out = dict(cells)

    def put(x, y, ch, col):
        if (x, y) not in out and 1 <= x < d.W:
            out[(x, y)] = (ch, col, None)
    if "l" in parts:
        style_label(put, cx - 10, 21, y0 + 4, ansi_upper(t_display(MOTIF_NAMES.get(kind, kind))), state)  # 1.7.0
    # 1.5.6: ya no hay barra (parte «b»): el avance lo lleva la regla de arriba
    if "s" in parts:
        style_status(put, cx - 10, 21, y0 + 9, state, pct, lt, None)
    return out

def _cycle_left(per, lt):
    """1.4.1: s que faltan para que un dibujo de ciclo `per` vuelva a su inicio (0 si no tiene ciclo)."""
    return (-lt) % per if per else 0.0

def _loop_site(S, st, W, lt):
    """1.8.1: s que le faltan al SITIO (el análisis del enlace: audio y video que se transforman en lo detectado) para cerrar su loop de LOOP_SECS. Cuenta desde
    que el centro del sitio entra (`ms`) o desde que llegó lo detectado (S["site_t"], lo que anota scene_site_mark: título, resolución, formato…), lo que
    ocurra más tarde: así la transformación se ve entera. Recién empezado hay un loop completo; luego el que va en curso, como en cualquier dibujo con ciclo
    (si el proceso acaba con el loop a medias, se espera a que lo cierre). Pura: `lt` = s desde que entró el dibujo (la hora de este cuadro es ms + lt)."""
    ms = float(st.get("ms") or 0.0)
    t0 = S.get("site_t")
    start = ms if t0 is None else max(ms, float(t0))
    el = ms + lt - start
    return LOOP_SECS if el <= 0.0 else _cycle_left(LOOP_SECS, el)

def _loop_check(S, st, W, lt):
    ck = S.get("check") or {}
    if ck.get("verdict") is None:
        per = LOOP_SECS                                          # 1.6.3: el haz va y viene en un loop
    else:
        # 1.6.2: el loop de la resolución = parpadeo + UN pulso completo (el pulso arranca donde acaba el parpadeo)
        t_v, ta = ck.get("t"), S.get("ta")
        if t_v is None or ta is None:
            # aún sin pintar el veredicto: falta todo (1.6.3: el parpadeo ES el loop)
            return CHECK_BLINK_SECS
        rt = max(0.0, ta - t_v)
        if rt < CHECK_BLINK_SECS:
            return CHECK_BLINK_SECS - rt
        return _cycle_left(CHECK_PULSE_SECS, rt - CHECK_BLINK_SECS)
    return _cycle_left(per, lt)

def _loop_conv(S, st, W, lt):
    """1.6.4: la conversión ya no tiene loop mientras corre (los puntos se pintan con el avance real): solo al terminar queda un loop (CONV_END_HOLD)
    para ver la vía llena y el destino destellando."""
    end = (S.get("conv") or {}).get("end")
    return 0.0 if end is None else max(0.0, end + CONV_END_HOLD - (st.get("ms", 0.0) + lt))

def _real_merge(S, st, lt):
    pct = S.get("pp_pct")
    return lt if pct is None else max(0.0, min(100.0, float(pct))) / 100.0 * REAL_MERGE_CYCLES * 4.0 / MERGE_SPEED

MOTIFS = {
    "dlpy": _Motif(_draw_dlpy),
    # 1.6.4: puntos que se llenan con el % (antes paquetes en loop; sin `real`: no hay recorrido que medir)
    "conv": _Motif(_draw_conv, loop=_loop_conv),
    "ask": _Motif(_draw_ask),
    "replace": _Motif(_draw_replace),
    "subst": _Motif(_draw_subst, loop=lambda S, st, W, lt: max(0.0, SWAP_STREAM_SECS + UX_SETTLE - lt), light=True),
    "check": _Motif(_draw_check, loop=_loop_check),                   # 1.6.3: a 24 cuadros (el barrido de 0,5 s)
    "merge": _Motif(_draw_merge, loop=lambda S, st, W, lt: _cycle_left(4.0 / MERGE_SPEED, lt), real=_real_merge, light=True),
    "save": _Motif(_draw_save, loop=lambda S, st, W, lt: max(0.0, SAVE_STREAM_SECS + UX_SETTLE - lt), light=True),
    "clean": _Motif(_draw_clean, loop=lambda S, st, W, lt: _cycle_left(1.0 / CLEAN_SPEED, lt), light=True),
    "empty": _Motif(_draw_empty, loop=lambda S, st, W, lt: _cycle_left(1.0 / CLEAN_SPEED, lt), light=True),
    "send": _Motif(_draw_send, loop=lambda S, st, W, lt: _cycle_left(SEND_CYCLE, lt)),
    "first": _Motif(_draw_first, loop=lambda S, st, W, lt: _cycle_left(WELCOME_CYCLE, lt), light=True),
    "updated": _Motif(_draw_updated, loop=lambda S, st, W, lt: _cycle_left(WELCOME_CYCLE, lt), light=True),
    # 1.6.5
    "downgrade": _Motif(_draw_downgrade, loop=lambda S, st, W, lt: _cycle_left(WELCOME_CYCLE, lt), light=True),
    # 1.6.5
    "same": _Motif(_draw_same, loop=lambda S, st, W, lt: _cycle_left(WELCOME_CYCLE, lt), light=True),
    # 1.7.1
    "ahead": _Motif(_draw_ahead, loop=lambda S, st, W, lt: _cycle_left(WELCOME_CYCLE, lt), light=True),
    "download": _Motif(_draw_download, loop=lambda S, st, W, lt: _cycle_left(DOWN_CYCLE, lt), light=True),
    "idle": _Motif(_draw_idle, loop=lambda S, st, W, lt: _cycle_left(PULSE_CYCLE, lt), light=True),
    "rail": _Motif(_draw_rail, loop=rail_loop, light=True),                                  # 1.4.6
}

MOTIF_NAMES = {"site": "Sitio", "dlpy": "DLPY", "first": "Primera ejecución", "updated": "Novedad", "downgrade": "Retroceso", "same": "Igual", "ahead": "Adelanto", "check": "Revisando archivo", "ask": "Espera",
               "replace": "Sustituyendo", "conv": "Conversión", "subst": "Sustitución", "merge": "Unión", "save": "Guardado",
               "clean": "Limpieza", "empty": "Papelera", "send": "Envío", "download": "Descarga", "idle": "Pulso", "rail": "Carril"}

def motif_name(kind):
    """1.4.5: nombre del motivo `kind` (None = el del sitio)."""
    return t_display(MOTIF_NAMES.get(kind or "site", str(kind)))  # 1.7.0

MOTIF_HOLD_MAX = 4.0        # 1.2.8: tope (s) de la espera de un dibujo para terminar su loop

def motif_hold_secs(S, st, kind, ta, mode=None):
    """1.3.2:"""
    mode = mode or SCENE_MODE
    if mode[0] == "real":
        return 0.0
    if mode[0] == "secs":
        if kind in ("ask", "replace"):
            return 0.0
        t0 = st["mt"] if st.get("mt") is not None else st["ms"]
        return max(0.0, mode[1] - (ta - t0))
    return min(MOTIF_HOLD_MAX, motif_loop_left(S, st, kind, ta))

REAL_MERGE_CYCLES = 3        # 1.3.9: ciclos del dibujo de la unión entre 0 y 100 % en el modo real

def scene_real_lt(S, st, kind, lt):
    """1.3.9: con DLPY_SCENE_MODE=real el dibujo avanza con el avance real del proceso (conversión: % de ffmpeg; unión: % del archivo
    temporal): 0 % = inicio del recorrido y 100 % = recorrido completo. Sin porcentaje, o en otro modo, sigue el reloj (`lt`)."""
    m = MOTIFS.get(kind)
    return lt if (SCENE_MODE[0] != "real" or m is None or m.real is None) else m.real(S, st, lt)

def scene_dwell(secs, mode=None):
    """1.3.2: segundos de una pausa fija entre escenas: con un número en DLPY_SCENE_MODE vale ese número; con «loop» se queda `secs`;
    con «real» vale 0 (1.4.0: la escena dura lo que dura la operación, sin esperas inventadas)."""
    mode = mode or SCENE_MODE
    return mode[1] if mode[0] == "secs" else (0.0 if mode[0] == "real" else secs)

def motif_loop_left(S, st, kind, ta):
    """1.2.8: s que le faltan al dibujo `kind` para cerrar su loop en curso (0 si no tiene loop). Lee MOTIFS (1.4.1). 1.8.1: kind None = el sitio: su loop es _loop_site."""
    if kind is None:
        return _loop_site(S, st, S["geo"][0], ta - st["ms"])
    m = MOTIFS.get(kind)
    if m is None or m.loop is None:
        return 0.0
    # 1.6.3: desde donde cuenta el dibujo (es la `start` con que se pinta; con `mt`, que lleva SCENE_LAG_MOTIF de más, el loop se daba por cerrado 0,05 s antes)
    t0 = st["ms"]
    return m.loop(S, st, S["geo"][0], ta - t0)

GATE_PAID_SECS = max(1.5, LOOP_SECS + 0.5)

def motif_loop_paid(S, kind):
    """1.5.9: True (y se gasta la marca) si el flujo ya esperó, con scene_gate, el loop del dibujo `kind`: la escena lo cambia sin retenerlo otra vez."""
    lp = S.get("loop_paid")
    if lp and lp[0] == kind and time.time() - lp[1] < GATE_PAID_SECS:
        S["loop_paid"] = None
        return True
    return False

def scene_motif(S, st, cells, ta, hold, f):
    """Centro: sitio (con salida animada), conversión, DLPY boot, o (1.1.3) unión, guardado y envío."""
    W, _Hh, y0, _ymax = S["geo"]
    bdg = scene_badge(S, st, ta)
    a, b = S["a"], S["b"]
    cv = S.get("conv")
    if cv and cv.get("end") is None:
        st["cinfo"] = (cv.get("src"), cv.get("dst") or cv.get("codec"), cv.get("t0", 0.0))
    elif cv and ta - cv["end"] > SCENE_SWAP + 0.1 and st.get("mcur") != "conv":
        S["conv"] = None
    kind = scene_motif_kind(S)
    # 1.8.1: el dibujo con que arranca (el sitio) se inicia ANTES de decidir si se retiene: scene_stream marca past_dl antes de esperar en scene_gate y, sin esto, el primer cuadro ya pedía el Pulso y el sitio se saltaba sin verse
    if "mcur" not in st:
        st["mcur"] = st["mprev"] = kind if S.get("resume") else None
        st["mt"], st["ms"], st["msp"] = None, ta, ta
    # 1.2.8: el dibujo no se deshace hasta terminar su loop
    if "mcur" in st and kind != st["mcur"] and not S.get("last_error"):
        if st.get("hold_to") is None:
            # 1.8.1: el sitio no retiene a D L P Y ni a sus escenas de versión (la pantalla de actualización no tiene reglas de loop)
            _skip = motif_loop_paid(S, st["mcur"]) or (st["mcur"] is None and kind in UPDATE_KINDS)
            # 1.3.2: según DLPY_SCENE_MODE (loop · real · segundos) · 1.5.9: si el flujo ya esperó ese loop (scene_gate), no se espera dos veces
            st["hold_to"] = ta + (0.0 if _skip else motif_hold_secs(S, st, st["mcur"], ta))
        if ta < st["hold_to"]:
            kind = st["mcur"]
    else:
        st["hold_to"] = None

    if "site_done" not in st:
        st["site_done"] = set()
        st["site_done_at"] = {}
        st["site_prev_cells"] = {}
        st["site_trans_t"] = None

    cur_done = set(S.get("done") or [])
    if cur_done != st["site_done"]:
        st["site_prev_cells"] = _site_center(S, W, y0, ta, f, bdg, st["site_done"], st["site_done_at"])
        # 1.4.2: otra transición del sitio: el plan se vuelve a medir
        st["site_flow"] = None
        st["site_trans_t"] = ta
        st["site_done"] = set(cur_done)
        st["site_done_at"] = dict(S.get("done_at") or {})


    def prog():
        return 1.0 if st["mt"] is None else max(0.0, min(1.0, (ta - st["mt"]) / SCENE_SWAP))
    p = prog()
    if kind != st["mcur"]:
        if st["mt"] is not None and p < 1.0 and kind == st["mprev"]:
            st["mprev"], st["mcur"] = st["mcur"], kind
            st["msp"], st["ms"] = st["ms"], st["msp"]
            if st.get("flow"):
                st["flow"]["rev"] = not st["flow"]["rev"]                          # 1.4.2: vuelve por el mismo camino
            st["mt"] = ta - (1.0 - p) * SCENE_SWAP
        elif st["mcur"] == "ask" and kind == "conv" and p >= 1.0:
            # 1.2.1: de la pregunta a la conversión no hay ruido:
            st["mprev"], st["msp"] = kind, ta
            # los chips son los mismos y solo se apaga la tecla Enter
            st["mcur"], st["ms"], st["mt"] = kind, ta, None
            st["key_fade_t"] = ta
        else:
            st["mprev"], st["msp"] = st["mcur"], st["ms"]
            # 1.0.6: el título va primero, el centro lo sigue
            st["mcur"], st["ms"], st["mt"] = kind, ta, ta + SCENE_LAG_MOTIF
            # 1.4.2: transición nueva: el plan del morph se mide en su primer cuadro
            st["flow"] = None
        p = prog()
    # 1.4.5: el nombre del motivo que ocupa el centro
    S["motivo"] = motif_name(st["mcur"])
    S["mvis"] = (st["mcur"], p >= 1.0, motif_loop_left(S, st, st["mcur"], ta) if p >= 1.0 else None, time.time(), st["ms"])      # 1.5.9: + 5.º = qué «instancia» del dibujo es (cuándo empezó) · 1.5.5: qué dibujo hay, si ya entró, cuánto le falta a su loop y cuándo se midió
    if st["mcur"] is None and p >= 1.0:
        base = {k: v for k, v in cells.items() if y0 + 4 <= k[1] <= y0 + 4 + BADGE_ROW}
        if st["site_trans_t"] is not None:
            tp = max(0.0, min(1.0, (ta - st["site_trans_t"]) / SCENE_SWAP))
            if tp < 1.0:
                new_site = _site_center(S, W, y0, ta, f, bdg, cur_done, S.get("done_at") or {})
                # 1.4.2: morph, un plan por transición
                merged = scene_flow_step(st, "site_flow", st["site_prev_cells"], new_site, tp, f, a, b)
                for key in base:
                    del cells[key]
                cells.update(merged)
                return cells
            else:
                st["site_trans_t"] = None
        site_cells = _site_center(S, W, y0, ta, f, bdg, cur_done, S.get("done_at") or {})
        for key in base:
            del cells[key]
        cells.update(site_cells)
        return cells

    base = {k: v for k, v in cells.items() if y0 + 4 <= k[1] <= y0 + 4 + BADGE_ROW}

    d = _MotifCtx(W, y0, a, b, ta, f, bdg, cur_done)

    def layer(k, start):
        # 1.4.1: el registro (MOTIFS) decide cómo se pinta cada uno (1.4.8: y scene_chrome le pone el estilo común)
        return scene_chrome(k, (MOTIFS[k].draw if k in MOTIFS else _draw_site)(S, st, d, start), S, st, d, start)

    new = layer(st["mcur"], st["ms"])
    if p < 1.0:
        # 1.4.2: las celdas del dibujo viejo viajan al nuevo
        new = scene_flow_step(st, "flow", layer(st["mprev"], st["msp"]), new, p, f, a, b)
    for key in base:
        del cells[key]
    cells.update(new)
    return cells

def scene_fps(S, st, ta, hold):
    """Cuadros por segundo nominales: ANIM_FPS siempre, salvo la conversion corriendo (CONV_RUN_FPS, ligera). 0.0.3: un solo reloj (antes SITE/CONV/ANIM_FPS).
    Lo que de verdad se pinta lo limita scene_fps_cap segun lo que cueste cada cuadro."""
    if ta < hold or S.get("t_out") is not None or S.get("k_out") is not None or S.get("t_in") is not None or S.get("ask"):
        # 1.1.1: también mientras espera el Enter (texto animado)
        return ANIM_FPS
    if st.get("key_fade_t") is not None and 0 <= ta - st["key_fade_t"] < CONV_KEY_FADE + 0.1:
        # 1.2.1: la tecla Enter apagándose, a tope de cuadros
        return ANIM_FPS
    for m in (st.get("bdg") or {}).values():                         # 1.0.7: la etiqueta cambiando va a tope de cuadros
        if m[1] is not None and 0 <= ta - m[1] < SCENE_BADGE_SECS + 0.1:
            return ANIM_FPS
    for key, dur in (("mt", SCENE_SWAP), ("t", SCENE_MORPH), ("tt", SCENE_TITLE_MORPH), ("site_trans_t", SCENE_SWAP)):
        t0 = st.get(key)
        # 1.0.6: incluye la espera de la cascada
        if t0 is not None and -SCENE_LAG_LABEL <= ta - t0 < dur + 0.1 + SCENE_LAG_LABEL:
            return ANIM_FPS
    if ta < st.get("rail_fast", 0.0):                                # 1.4.6: tarjetas del carril deslizándose
        return ANIM_FPS
    _ck = S.get("check") or {}
    # 1.6.1: los cuadros parpadeando, a tope de cuadros (1.6.2: y mientras espera a pintarse el primero)
    if _ck.get("verdict") is not None and (_ck.get("t") is None or 0 <= ta - _ck["t"] < CHECK_BLINK_SECS + 0.1):
        return ANIM_FPS
    # 1.1.3: unión y guardado (1.1.5: y limpieza; 1.2.5: y revisión; 1.2.9: y arranque), como la conversión (1.4.1: la marca light de MOTIFS)
    if getattr(MOTIFS.get(scene_motif_kind(S)), "light", False):
        return ANIM_FPS
    if S.get("brand"):
        return ANIM_FPS
    cv = S.get("conv")
    # 1.2.1: la conversión, más ligera que el resto
    return CONV_RUN_FPS if (cv and cv.get("end") is None) else ANIM_FPS

def scene_fast(S, st, ta, hold, fps=None):
    """1.6.4: ¿la escena está en convert_fast_anim? Sí cuando DLPY_CONVERT_LIGHT_ANIMATION está activo, la conversión corre (sin terminar ni error), su dibujo ya ocupa
    el centro y no hay ninguna transformación en curso (intro, cambio de dibujo, de texto, de título o de etiqueta, tecla Enter apagándose…: lo
    mismo que hace subir scene_fps a tope). Entonces se detiene toda animación: el cuadro es estático y solo se vuelve a pintar cuando cambia
    algo (el % entero, el texto, el alto del terminal) o cada FAST_REFRESH s por si el terminal borró algo; el hilo duerme en _FAST_WAKE."""
    if not CONVERT_FAST_ANIM:
        return False
    cv = S.get("conv")
    if not cv or cv.get("end") is not None or S.get("last_error") or st.get("mcur") != "conv":
        return False
    return (scene_fps(S, st, ta, hold) if fps is None else fps) == CONV_RUN_FPS

FAST_REFRESH = 10.0

def scene_fast_key(S, rows, now):
    """1.6.4: lo que, al cambiar, obliga a repintar la escena en convert_fast_anim: el % entero, el texto, el alto del terminal y el repintado periódico."""
    pct = (S.get("conv") or {}).get("pct")
    return (None if pct is None else int(pct), S.get("label"), rows, int(now // FAST_REFRESH))

def scene_conv_notice(cells, y0, cx, W, fd=1.0):
    """1.6.4: el aviso de la conversión en la fila bajo el texto de estado: «Espera mientras convierte · puede tardar · no cierres la app» (se acorta
    según el ancho); «no cierres la app» va en ámbar. `fd` (0 a 1) lo funde al aparecer. Lo pone la escena mientras convierte (con o sin convert_fast_anim)."""
    room = max(8, W - 6)
    txt = ux_text(*CONV_NOTICE, room=room)  # 1.7.1: el motor de texto traduce y mide por el ancho real
    row, x0 = y0 + SCENE_STATUS_ROW + 1, cx - dwidth(txt) // 2
    hi = txt.lower().find(t_display("no cierres la app").lower())  # 1.7.0
    base = SCENE_GRAY if SCENE_CALM else SCENE_DIM
    nlen = len(t_display("no cierres la app"))

    def tone(i, _ch):
        col = (255, 176, 32) if (hi >= 0 and hi <= i < hi + nlen) else base  # 1.7.0
        return mix(BLACK, col, max(0.0, min(1.0, fd)))
    put_text(cells, x0, row, txt, tone, lo=1, hi=W)                          # 1.7.0: ancho real
    return cells

SPEED_CYCLE = LOOP_SECS

def scene_speed_cells(W, y0, a, b, lt, speed, peak, fade=1.0):
    """1.7.0: el medidor de velocidad en la fila de aire (y0 + SCENE_STATUS_ROW - 1), junto a las demás animaciones: ↓, 7 mini-barras que
    bailan con la velocidad real y el texto (12,3 MB/s). Pura: el cuadro en `lt` y en `lt + LOOP_SECS` es el mismo con la misma velocidad
    (el baile cierra el loop). Con velocidad 0 late con un pulso y muestra 0 B/s; con `fade` < 1 se apaga."""
    cells = {}
    if W is None or W < 20:
        return cells
    txt = speed_text(speed if speed else 0.0)
    bars, n = "", 7
    ph = (lt % SPEED_CYCLE) / SPEED_CYCLE if SPEED_CYCLE else 0.0
    base = max(0.0, min(1.0, (speed or 0.0) / peak)) if peak else 0.0
    for i in range(n):
        wave = 0.5 + 0.5 * math.sin(2.0 * math.pi * (ph + i / float(n)))
        lvl = int(round((base * 0.7 + wave * 0.3) * 7.0))
        bars += "▁▂▃▄▅▆▇█"[max(0, min(7, lvl))]
    line = bars + " " + txt
    row, cx = y0 + SCENE_STATUS_ROW - 1, W // 2 + 1
    x0 = cx - dwidth(line) // 2
    g = lambda k: mix6(a, b, k)
    put_text(cells, x0, row, line, lambda i, _ch: mix(BLACK, g(i / float(max(1, len(line)))), max(0.0, min(1.0, fade))), lo=1, hi=W)      # 1.7.0: ancho real
    return cells

RULE_CELLS = 29                                     # 1.7.6: celdas de la regla (de -14 a 14 desde el centro)

def bar_cover(i, shown, n=RULE_CELLS):
    """1.7.6: cuánto de la celda `i` (0 a n-1) cubre el avance `shown` (0 a 1): 0 = nada, 1 = entera; la del frente queda a medias, así la regla avanza sin saltos. Pura."""
    return max(0.0, min(1.0, float(shown) * n - i))

def bar_front(i, shown, n=RULE_CELLS):
    """1.7.6: fuerza (0 a 1) del destello del frente del avance en la celda `i`: máxima donde acaba lo cubierto, se apaga a ~2 celdas; 0 sin avance o con la barra llena. Pura."""
    p = float(shown) * n
    if p <= 0.0 or p >= n:
        return 0.0
    return max(0.0, 1.0 - abs(p - i - 0.5) / 2.0) ** 2

def scene_cells(S, st, tl, ta, f):
    """Un cuadro de la escena:"""
    W, Hh, y0, ymax = S["geo"]
    a, b, name, mode = S["a"], S["b"], S["name"], S["mode"]
    cells, _k = site_scene(tl, W, y0, a, b, name, mode, f, ta, (S.get("asp_shown") or S.get("aspect"), S.get("res")),
                           {k: (t_, 1.0) for k, t_ in scene_badge_texts(S).items()})
    hold = SITE_HOLD_AT * SITE_SECS
    if ta < hold:
        if topbar_visible(S):                                        # 1.8.8: la franja ya se ve en el sitio de entrada
            cells.update(topbar_cells(W))
        if BOTTOMBAR:
            cells.update(bottom_bar_cells(W, scene_bottom_bar_row(y0, False)))
        return cells
    cells = scene_motif(S, st, cells, ta, hold, f)                   # 1.0.3: sitio (con salida), conversión o DLPY boot
    # 1.9.2: topbar en fila 2 con la 1 libre; la franja inferior ocupa la fila reservada bajo el estado.
    if topbar_visible(S):
        cells.update(topbar_cells(W))
    cx = W // 2 + 1
    _sp = S.get("speed")
    _fd = 1.0
    # 1.7.0: la velocidad se apaga con fundido al terminar la pista
    if _sp is None and S.get("speed_end") is not None and time.time() - S["speed_end"] < 0.6:
        _sp, _fd = S.get("speed_last") or 0.0, 1.0 - 0.5 * (time.time() - S["speed_end"]) / 0.6
    if _sp is not None:
        _fd *= smooth((time.time() - (S.get("speed_t") or time.time())) / 0.4) if S.get("speed_t") else 1.0
        cells.update(scene_speed_cells(W, y0, a, b, ta, _sp, S.get("speed_peak") or 0.0, _fd))
    g = lambda k: mix6(a, b, k)

    for key in [k for k in cells if k[1] == y0 + 2]:                 # el nombre del sitio lo repinta la transición
        del cells[key]
    w = smooth((ta - hold) / 0.3)                                    # de la regla de la intro a la barra, sin saltos
    # el brillo del barrido (de -0.25 a 1.25 de la regla)
    pos = ((ta * 0.8) % 1.0) * 1.5 - 0.25
    # 1.0.6: barrido ↔ barra con fundido, sin corte de color
    want_b = 1.0 if S.get("busy") else 0.0
    # 1.6.4: convert_fast_anim: sin brillo que barre la regla (cuadro estático)
    if S.get("fast"):
        want_b = 0.0
    bw = scene_ease(st.get("bw", want_b), want_b, SCENE_BUSY_RATE, ta - st.get("bta", ta))
    st["bw"], st["bta"] = (want_b if (abs(bw - want_b) < 0.01 or S.get("fast")) else bw), ta
    bw = st["bw"]
    shown_bar = S["shown"]
    for d in range(-14, 15):                                         # la regla es la barra de progreso
        k = (d + 14) / 28.0
        lit = g(k)
        # barra de progreso (1.7.6: la celda del frente se enciende a medias, sin saltos)
        tone = mix(mix(lit, BLACK, 0.62), lit, bar_cover(d + 14, shown_bar))
        spark = bar_front(d + 14, shown_bar) * (1.0 - min(1.0, bw))
        # 1.7.6: el frente del avance, un destello que se asienta
        if spark > 0.0:
            tone = mix(tone, WHITE, 0.4 * spark)
        if bw > 0:                                                   # espera sin porcentaje: un brillo recorre la regla
            sweep = mix(mix(lit, BLACK, 0.55), lit, max(0.0, 1.0 - abs(k - pos) / 0.22))
            tone = sweep if bw >= 1.0 else mix(tone, sweep, bw)
        cells[(cx + d, y0)] = ("─", mix(lit, tone, w), None)
    site = ("grad", " ".join(name.upper()))
    if st.get("tcur") is None:                                       # al principio en pantalla está el nombre del sitio
        # (al volver de la lista, ya el del video)
        st["tprev"] = st["tcur"] = scene_title_spec(S) if S.get("resume") else site
        st["tt"] = None
    want = scene_title_spec(S)
    if want != st["tcur"]:                                           # cambió el título: el viejo se deshace en el nuevo
        mid = st["tt"] is not None and (ta - st["tt"]) / SCENE_TITLE_MORPH < 1.0 and bool(st.get("tshown"))
        # 1.0.6: a mitad de otra transformación, parte de lo que ya se ve
        st["tpcols"] = dict(st["tshown"]) if mid else None
        st["tprev"], st["tcur"], st["tt"] = st["tcur"], want, max(ta, hold)
    p = 1.0 if st["tt"] is None else (ta - st["tt"]) / SCENE_TITLE_MORPH

    def tcols(spec):
        txt = spec[1] if spec[0] == "grad" else fit_text(spec[1], max(8, W - 6))
        return scene_cols(txt, cx), spec[0], dwidth(txt)

    def tone_of(kind, n, x):
        return g((x - (cx - n // 2)) / float(max(1, n))) if kind == "grad" else SCENE_WHITE

    old, old_kind, old_n = tcols(st["tprev"])
    if st.get("tpcols"):
        old = st["tpcols"]
    new, new_kind, new_n = tcols(st["tcur"])
    tshown = {}
    for x, (ch, kind) in scene_morph(old, new, p, f).items():
        cells[(x, y0 + 2)] = (ch, tone_of(old_kind, old_n, x) if kind == 0 else mix(g(0.5), BLACK, 0.45) if kind == 1
                              else tone_of(new_kind, new_n, x), None)
        if ch != " ":
            tshown[x] = "\0" if ch == "" else ch
    st["tshown"] = tshown
    pct = S["pct"]
    room = max(8, W - 6 - (7 if pct is not None else 0))                           # el % siempre cabe
    lab = t_status(S["label"])  # 1.9.0: localiza el estado y conserva los datos dinámicos
    _dl = t_display("Descargando") + " "
    if dwidth(lab) > room and lab.startswith(_dl):         # terminal angosto: sin el verbo, para no perder el «2/3»
        _rest = lab[len(_dl):]
        lab = _rest[:1].upper() + _rest[1:]
    lab = fit_text(lab, room)
    # 1.0.8: error en rojo suave · 2.0.6: idioma aplicado en verde (mint de la ✓ del marco D L P Y)
    if S.get("last_error") and (lab.startswith("Error") or lab.startswith(t_display("Error"))):
        err_col = (255, 96, 96)
    elif S.get("label_ok"):
        err_col = (120, 224, 150)
    else:
        err_col = SCENE_GRAY
    full = lab + ("" if pct is None else " · %3d%%" % int(max(0, min(100, pct))))
    # cambió el proceso: el texto viejo se deshace en el nuevo
    if lab != st["lab"]:
        mid = st["lab"] is not None and (ta - st["t"]) / SCENE_MORPH < 1.0 and bool(st.get("lshown"))
        # 1.0.6: a mitad de otra transformación, parte de lo que ya se ve
        st["lpcols"] = dict(st["lshown"]) if mid else None
        # cascada: título → centro → texto
        lead = any(st.get(k_) is not None and 0 <= ta - st[k_] < 0.25 for k_ in ("tt", "mt"))
        st["prev"], st["t"], st["lab"] = st["full"], ta + (SCENE_LAG_LABEL if lead else 0.0), lab
    st["full"] = full
    if full:
        x_new = cx - dwidth(full) // 2
        tail = x_new + dwidth(lab) + 3
        shown = {}
        for x, (ch, kind) in scene_morph(st.get("lpcols") or scene_cols(st["prev"], cx), scene_cols(full, cx),
                                         (ta - st["t"]) / SCENE_MORPH, f).items():
            cells[(x, y0 + SCENE_STATUS_ROW)] = (ch, SCENE_DIM if kind == 0 else mix(g(0.5), BLACK, 0.45) if kind == 1
                                   else (g(0.45) if x >= tail and pct is not None else err_col), None)
            if ch != " ":
                shown[x] = "\0" if ch == "" else ch
        st["lshown"] = shown
    cvn = S.get("conv")
    # 1.6.4: el aviso mientras convierte
    if cvn and cvn.get("end") is None and st.get("mcur") == "conv" and not S.get("last_error"):
        if st.get("notice_t") is None:
            st["notice_t"] = ta
        cells = scene_conv_notice(cells, y0, cx, W, 1.0 if S.get("fast") else smooth((ta - st["notice_t"]) / 0.4))
    else:
        st["notice_t"] = None
    if S.get("ask"):                                                 # 1.1.1: pidiendo Enter para convertir
        cells = scene_ask_cells(cells, S["ask"], ta, y0, cx, W, g)
    if S.get("k_out") is not None:                                   # la salida: la escena se cierra hacia el centro
        cells = scene_dissolve(cells, outro_ease(S["k_out"]), cx, W, a, b)      # 1.9.8: el cierre y la reapertura aceleran y frenan suave
    if BOTTOMBAR:
        _notice_active = bool(cvn and cvn.get("end") is None and st.get("mcur") == "conv" and not S.get("last_error"))
        _extra_content = _notice_active or bool(S.get("ask"))
        cells.update(bottom_bar_cells(W, scene_bottom_bar_row(y0, _extra_content)))
    return cells

def scene_paint(out, cells, st, W, ymax):
    """Repinta solo las filas que cambiaron (los terminales de iOS no aguantan cuadros completos a 24 fps)."""
    # DLPY_TRANSLATION_DEBUG_MODE=mark/both: color de las traducciones (solo con la opción activa)
    cells = lang_mark_cells(cells)
    seq = [WRAP_OFF]
    for y in range(1, ymax + 1):
        parts, cur, skip = [], None, False
        for x in range(1, W):
            # 1.7.0: la segunda columna de un carácter ancho ya la cubre él (lo que haya ahí no se pinta)
            if skip:
                skip = False
                continue
            c = cells.get((x, y))
            key, ch = (c[1:], c[0]) if c else (None, " ")
            wide = bool(ch) and ch[0] >= "\u1100" and x < W - 1 and unicodedata.east_asian_width(ch[0]) in ("W", "F")
            if not ch or (ch[0] >= "\u1100" and not wide and unicodedata.east_asian_width(ch[0]) in ("W", "F")):
                # continuación huérfana (su carácter ancho ya no está) o ancho en la última columna: ocupa una columna
                ch = " "
            if key != cur:
                parts.append(RESET + _fg(key[0]) + (_bg(key[1]) if key[1] else "") if key else RESET)
                cur = key
            parts.append(ch)
            skip = wide
        row = "".join(parts) + RESET
        if row != st["rows"].get(y):
            st["rows"][y] = row
            seq.append(cur_to(y, 1) + row)
    if len(seq) > 1:
        seq.append(RESET + WRAP_ON)
        out.write("".join(seq))
        out.flush()

def scene_state():
    """Estado de dibujo de la escena (filas pintadas, etiqueta, texto y tiempos) vacío."""
    return {"rows": {}, "lab": None, "prev": "", "full": "", "t": 0.0, "tcur": None, "tprev": None, "tt": None}

def scene_loop():
    """Hilo de la escena: ANIM_FPS cuadros por segundo (o los que aguante, ver scene_fps_cap) hasta que SCENE["stop"]."""
    S = SCENE
    out, (W, _h, _y0, ymax) = S["out"], S["geo"]
    st = scene_state()
    hold = SITE_HOLD_AT * SITE_SECS
    # al volver de la lista no se repite la intro
    t0 = full_t = time.monotonic() - (hold + 0.4 if S.get("resume") else 0.0)
    rows_seen, last, fps, cost = S["rows"], -1, ANIM_FPS, 0.0      # cost: media (s) de lo que tarda pintar un cuadro
    # 1.0.6: instante del cuadro anterior (suavizado por tiempo)
    ft = time.monotonic()
    try:
        while not S["stop"]:
            now = time.monotonic()
            ta = now - t0
            S["ta"] = ta
            # 1.0.2: convirtiendo o DLPY: menos cuadros, menos CPU
            fps = scene_fps(S, st, ta, hold)
            # 1.6.4: convert_fast_anim: nada se anima mientras convierte
            S["fast"] = scene_fast(S, st, ta, hold, fps)
            fps = scene_fps_cap(fps, cost)                      # 0.0.3: a lo que el iPhone y la terminal sostienen (la comparacion con CONV_RUN_FPS ya se hizo)
            if S["fast"]:
                try:
                    _rn = term_rows()
                except (OSError, ValueError):
                    _rn = rows_seen
                fkey = scene_fast_key(S, _rn, now)
                # nada cambió: el hilo duerme hasta que algo cambie (o FAST_TICK)
                if fkey == st.get("fast_key"):
                    _FAST_WAKE.wait(FAST_TICK)
                    _FAST_WAKE.clear()
                    continue
                # primer cuadro de convert_fast_anim o repintado periódico: se pinta todo
                if (st.get("fast_key") or (None,) * 4)[3] != fkey[3]:
                    st["rows"].clear()
                # (el repintado periódico lo decide FAST_REFRESH, no los 0,35 s de abajo)
                st["fast_key"], last, full_t = fkey, -1, now
            else:
                st["fast_key"] = None
            f = int(ta * fps)
            if f != last:
                last = f
                try:
                    rows_now = term_rows()
                except (OSError, ValueError):
                    rows_now = rows_seen
                if rows_now != rows_seen:                            # cambió el alto: se limpia y se repinta todo
                    rows_seen, full_t = rows_now, now
                    st["rows"].clear()
                    # 1.2.3: también el historial (lo que el cambio de alto metió arriba)
                    out.write(HOME_CLEAR + PURGE_SEQ)
                # 1.9.8: refresco de seguridad repartido (unas filas por cuadro), no toda la pantalla de golpe cada 0,35 s
                elif not S["fast"]:
                    scene_refresh_slice(st, ymax, fps)
                fdt, ft = now - ft, now
                tgt = S.get("aspect") or 16 / 9.0                    # el marco de video cambia de proporción sin saltos
                # 1.6.4: convert_fast_anim: sin suavizados (el cuadro es el definitivo y no habrá otro hasta que algo cambie)
                if S["fast"]:
                    S["asp_shown"], S["shown"] = tgt, S["frac"]
                S["asp_shown"] = tgt if not S.get("asp_shown") else scene_ease(S["asp_shown"], tgt, SCENE_ASP_RATE, fdt)
                if abs(tgt - S["asp_shown"]) < 0.005:
                    S["asp_shown"] = tgt
                # la barra alcanza al avance sin saltos
                S["shown"] = scene_ease(S["shown"], S["frac"], SCENE_BAR_RATE, fdt)
                if abs(S["frac"] - S["shown"]) < 0.002:
                    S["shown"] = S["frac"]
                if S["t_out"] is not None:                           # se cierra hacia el centro
                    S["k_out"] = (now - S["t_out"]) / SCENE_OUTRO_SECS
                # vuelve a abrirse desde el centro (lo mismo, al revés)
                elif S.get("t_in") is not None:
                    k_in = 1.0 - (now - S["t_in"]) / SCENE_OUTRO_SECS
                    S["k_out"] = k_in if k_in > 0 else None
                    if k_in <= 0:
                        S["t_in"] = None
                else:
                    S["k_out"] = None
                _tp = time.perf_counter()
                # 0.0.3: el ruido de los glitch va a su propio reloj (GLITCH_HZ), no al numero de cuadro
                scene_paint(out, scene_cells(S, st, min(ta, hold), ta, int(ta * GLITCH_HZ)), st, W, ymax)
                _dt = time.perf_counter() - _tp
                cost = _dt if cost <= 0.0 else cost + (_dt - cost) * 0.1
            time.sleep(frame_gap(time.monotonic() - t0, fps))      # 1.9.8: hasta el siguiente límite de cuadro
    except Exception as _ign:
        S["err"] = f"{type(_ign).__name__}: {_ign}"      # 1.0.1: --scb lo anota en state/scb_debug.json
        ignore("scene_loop", _ign)
        # 2.1.5: con el hilo de dibujo muerto nadie repinta y _SceneMute se traga toda la salida: la pantalla quedaba congelada sin aviso.
        # La escena cede (igual que antes de una pregunta o de pip) y el flujo sigue en modo clásico, visible.
        with quiet("scene_loop stop"):
            scene_stop()

def scene_start(run, resume=False):
    """Arranca la escena (la intro del sitio y lo que sigue)."""
    S = SCENE
    if S["on"] or not SITE_ANIM:
        return False
    if not (ANIM and USE_COLOR and TRUECOLOR and sys.stdout.isatty() and not DEBUG):
        return False
    hide_keyboard()                          # el alto del terminal cambia al bajar el teclado: se mide ya estable
    settle_terminal()
    try:
        rows = term_rows()
    except (OSError, ValueError):
        return False
    sw = safe_width()
    W, Hh = sw + 1, min(rows, ui_lines())
    _scene_tail = 3 if BOTTOMBAR else 1
    if sw < 30 or Hh < max(16, SCENE_TOP + SCENE_STATUS_ROW + _scene_tail):
        return False
    name, sig, a, b = site_theme_apply(run) or site_theme(_host(run.link), "")
    mode = site_mode(run)
    fg = (0, 0, 0) if (0.3 * a[0] + 0.59 * a[1] + 0.11 * a[2]) > 150 else (255, 255, 255)
    # si la escena cede, el banner conserva la etiqueta
    SESSION["tag"] = (" " + sig + " " + SITE_ICON[mode] + " ", a, fg)
    y0 = SCENE_TOP        # 1.6.6: la escena va arriba de la consola, con una sola línea de aire
    # 1.0.1: --scb no usa el borrado nativo: lo hace aquí, ya seguro de que pinta
    if not native_clear(HOME_CLEAR, mode=scene_clear_mode()) and _scm_run():
        # 1.6.6: --scb también borra con el modo reset (ESC c, ya lleva el historial); sin modo, como antes
        _seq = clear_mode_seq(scene_clear_mode())
        sys.stdout.write(RESET + (_seq if _seq is not None else HOME_CLEAR + PURGE_SEQ))
        sys.stdout.flush()
    keep = {k: S[k] for k in ("title_raw", "label", "pct", "frac", "shown", "lo", "hi", "brand", "busy", "aspect", "res", "alabel", "vinfo", "ainfo", "count")} if resume else {}
    # sin envolturas anidadas
    mute = _SceneMute(sys.stdout._inner if isinstance(sys.stdout, _SceneMute) else sys.stdout)
    S.update(scene_defaults(), on=True, mute=mute, out=mute._inner, geo=(W, Hh, y0, min(Hh, y0 + SCENE_STATUS_ROW + (3 if BOTTOMBAR else 1))), a=a, b=b, name=name,
             # 1.3.2: «Preparando» también cuenta sus N s (1.4.1: lo demás, de scene_defaults)
             mode=mode, mode_orig=mode, label="Preparando", rows=rows, label_wall=time.time())
    S["aspect"], S["res"] = video_shape(getattr(run, "fmt", None), getattr(run, "info", None))
    S["asp_shown"] = S["aspect"]
    S["alabel"] = audio_label(getattr(run, "fmt", None))
    S["vinfo"] = video_facts(getattr(run, "fmt", None), getattr(run, "info", None))
    S["ainfo"] = audio_facts(getattr(run, "fmt", None), getattr(run, "info", None))
    S["count"] = 0
    if resume:
        S.update(keep, resume=True, t_in=time.monotonic())
        S["asp_shown"] = S["aspect"]
    sys.stdout = mute
    # 1.0.8: stderr al log
    emute = _SceneErrMute(sys.stderr._inner if isinstance(sys.stderr, _SceneErrMute) else sys.stderr)
    S["emute"], sys.stderr = emute, emute
    S["out"].write(CURSOR_HIDE + RESET)
    S["out"].flush()
    S["th"] = threading.Thread(target=scene_loop, daemon=True)
    S["th"].start()
    atexit.register(scene_stop)              # nunca queda el cursor oculto
    return True

def scene_min_wait(now=None, mode=None):
    """1.3.2:"""
    mode = mode or SCENE_MODE
    w = SCENE.get("label_wall")
    if mode[0] != "secs" or not w:
        return 0.0
    return max(0.0, mode[1] - ((time.time() if now is None else now) - w))

def scene_status(text, pct=None, frac=None):
    """El texto de estado (y, si se da, el avance de la regla:"""
    if not SCENE["on"]:
        return
    # 1.0.8: si el flujo siguió, el error era recuperable: la escena vuelve a lo suyo
    if SCENE.get("last_error"):
        SCENE["last_error"] = None
        if SCENE.get("err_brand"):
            SCENE["brand"], SCENE["err_brand"] = False, False
    new = str(text)
    if new != SCENE.get("label"):
        # «No se pudo …» / «Error …» que llegan solo como estado de la escena también avisan en la bottombar
        if _dlpy_state(new) == "fail":
            diagnostic_report("E", new)
        w, old = SCENE.get("label_wall"), str(SCENE.get("label") or "")
        # 1.3.3: el comando anterior termina de mostrarse (tecleado y ejecutado) en la escena
        if SCENE.get("brand") and w:
            scene_wait_step(old)
        # 1.5.9: modo «wait»: el dibujo del proceso que acaba se ve entero antes de pasar al siguiente
        scene_gate(scene_motif_kind(dict(SCENE, label=new)))
        # 1.3.2: DLPY_SCENE_MODE=<segundos>: el texto anterior se lee N s como mínimo
        rest = scene_min_wait()
        if rest > 0:
            time.sleep(rest)
        SCENE["label_wall"] = time.time()
        # 1.8.5: no se registra un inicio ficticio de guardado; «Guardado» solo llega
        # después de que _m_store confirme que el movimiento del archivo terminó.
        SCENE["dl_done"] = None                                   # 1.3.3: el texto nuevo aún no se ha mostrado
        # 1.6.4: otro texto: si la escena dormía en convert_fast_anim, lo pinta
        _FAST_WAKE.set()
    if new != SCENE.get("label"):
        SCENE["label_ok"] = False          # 2.0.6: el verde de «idioma aplicado» solo dura ese estado
    SCENE["label"], SCENE["pct"] = new, pct
    if frac is not None:
        SCENE["frac"] = max(SCENE["frac"], min(1.0, float(frac)))

def scene_site_mark():
    """1.8.1: lo detectado (título, proporción, resolución, formato, directo, lista, códec…) acaba de llegar a la escena: el sitio empieza a transformarse y su
    loop (_loop_site) cuenta desde aquí. Solo mientras el sitio es el dibujo (antes de la primera pista: después ya no vuelve). True si lo anotó."""
    S = SCENE
    if S["on"] and not S.get("past_dl"):
        S["site_t"] = float(S.get("ta") or 0.0)
        return True
    return False

def scene_title(title):
    """El título del video: el nombre del sitio se transforma en él."""
    if SCENE["on"]:
        new = " ".join(str(title or "").split())
        if new != SCENE.get("title_raw"):
            # 1.8.1: el título llegó: el sitio se transforma y su loop cuenta desde aquí
            scene_site_mark()
        SCENE["title_raw"] = new

def scene_lang(d):
    """Idioma de un stream de audio para el texto de la escena («es-US»), o None si no lo informa."""
    info = (d or {}).get("info_dict") or {}
    lang = " ".join(str(info.get("language") or "").split())
    return None if not lang or lang.lower() in ("none", "und", "unknown") else fit_text(lang, 12)

def scene_stream_label(kind, n, total, lang=None):
    """«Descargando audio es-US 2/3»:"""
    text = "Descargando " + kind
    if kind == "audio" and lang:
        text += " " + lang
    if total > 1:
        text += " %d/%d" % (n, total)
    return text

def _scene_bag(key, make=dict):
    """1.4.1: la «bolsa» (dict o set) de SCENE[key]; se crea si falta. Antes cada función repetía el «si es None, créala»."""
    v = SCENE.get(key)
    if v is None:
        v = SCENE[key] = make()
    return v

def _scene_mark_done(kind):
    try:
        k = str(kind or "").lower()
        if k not in ("video", "audio"):
            return
        done = _scene_bag("done", set)
        if k in done:
            return
        done.add(k)
        _scene_bag("done_at")[k] = SCENE.get("ta", 0.0)
    except Exception as _ign:
        ignore('escena: marcar done', _ign)

def scene_stream(kind, n, total, lang=None):
    """Empieza un stream: 1.0.5 fix - sale de escena cuando ya no queda más de ESE tipo, no del global."""
    if not SCENE["on"]:
        return
    total = max(1, total or 1)
    n = min(max(1, n), total)
    SCENE["lo"], SCENE["hi"] = 0.08 + 0.72 * (n - 1) / total, 0.08 + 0.72 * n / total
    SCENE["busy"] = False   # 1.7.0: ya hay pista real: la regla es la barra, no el barrido de espera
    SCENE["stream_total"] = total
    SCENE["stream_seen"] = n
    try:
        k = str(kind or "").lower()
        started = _scene_bag("started")
        started[k] = started.get(k, 0) + 1
        # 1.4.5: qué es y cuánto lleva cada pista (la fila de «Descarga»)
        _scene_bag("skind")[n] = k
        _scene_bag("spct")[n] = 0
        if lang:
            # 1.4.7: el idioma de cada pista (la tarjeta de audio lo muestra)
            _scene_bag("slang")[n] = lang
        # 1.4.5: desde aquí el sitio ya no vuelve (entre motivos queda el Pulso)
        SCENE["past_dl"] = True

        # si había un tipo terminado pendiente y ahora empieza otro distinto, ese tipo ya no volverá: marcarlo como terminado
        last = SCENE.get("last_finished")
        if last and last != k:
            _scene_mark_done(last)
            SCENE["last_finished"] = None

        _scene_bag("type_totals")[k] = total                       # para debug
    except Exception as _ign:
        ignore('escena: stream', _ign)
    scene_status(scene_stream_label(kind, n, total, lang), pct=0, frac=SCENE["lo"])

def scene_stream_done(kind):
    """1.0.5: solo marca done cuando realmente no queda más de ese tipo."""
    try:
        if not SCENE.get("on"):
            return
        k = str(kind or "").lower()
        if k not in ("video", "audio"):
            return
        finished = _scene_bag("finished")
        finished[k] = finished.get(k, 0) + 1
        SCENE["last_finished"] = k                                  # el último terminado queda pendiente…
        if int(SCENE.get("stream_seen") or 1) >= int(SCENE.get("stream_total") or 1):
            # …salvo si era el último stream global: done de inmediato
            _scene_mark_done(k)
            SCENE["last_finished"] = None
    except Exception as _ign:
        ignore('escena: stream terminado', _ign)

def scene_outro():
    """1.4.1: la escena se cierra hacia el centro y se espera a que el hilo pinte el cierre (con DLPY_SCENE_OUTRO_ENABLED=0 no hace nada). True si cerró.
    Antes lo repetían scene_error_end, scene_end y scene_list_enter."""
    if not OUTRO:
        return False
    SCENE["t_out"] = time.monotonic()
    time.sleep(SCENE_OUTRO_SECS + 0.12)
    return True


def scene_busy(on=True):
    """La regla deja de marcar un avance y barre de lado a lado (una espera sin porcentaje)."""
    if SCENE["on"]:
        SCENE["busy"] = bool(on)


def scene_progress(pct):
    """Avance (0-100) del stream en curso; sin total conocido el % se oculta."""
    if not SCENE["on"] or not SCENE["label"].startswith(("Descargando", "Preparando descarga")):
        return
    if SCENE["label"] == "Preparando descarga":
        # 1.7.0 (reparación): el primer avance ya es la descarga: la etiqueta se mueve aquí mismo, sin esperar a
        # que la puerta de la escena (scene_gate) deje pasar el cambio de dibujo; si no, el avance se tiraba y la
        # pantalla se quedaba en «Preparando descarga» aunque los bytes ya bajaran.
        SCENE["label"] = "Descargando"
        SCENE["busy"] = False
    n = int(SCENE.get("stream_seen") or 1)
    if pct is None:
        SCENE["pct"] = None
        _scene_bag("spct")[n] = None
        return
    SCENE["pct"] = pct
    _scene_bag("spct")[n] = pct                                     # 1.4.5
    SCENE["frac"] = max(SCENE["frac"], SCENE["lo"] + (SCENE["hi"] - SCENE["lo"]) * max(0.0, min(100.0, pct)) / 100.0)

def _site_sig():
    """1.8.1: lo que la escena sabe de lo detectado (proporción, resolución, formato, modo, cuenta, datos del video y del audio): si cambia, el sitio se transforma."""
    S = SCENE
    return repr((S.get("aspect"), S.get("res"), S.get("alabel"), S.get("mode_orig") or S.get("mode"), S.get("count"),
                 sorted((S.get("vinfo") or {}).items(), key=lambda kv: str(kv[0])), sorted((S.get("ainfo") or {}).items(), key=lambda kv: str(kv[0]))))

def scene_shape(*srcs):
    """1.0.0: la proporción y la resolución del video (width/height de un formato o del análisis) para el marco de la escena. 1.8.1: si con ello cambia lo detectado, el
    sitio se transforma y su loop cuenta desde aquí (scene_site_mark)."""
    if not SCENE["on"]:
        return
    _sig0 = _site_sig()
    asp, res = video_shape(*srcs)
    if asp:
        SCENE["aspect"], SCENE["res"] = asp, res
    al = audio_label(*srcs)
    if al:
        SCENE["alabel"] = al                           # 1.0.7: formato del audio para la etiqueta
    # 1.1.0: códec / fps / bitrate para la etiqueta que fluye
    SCENE.setdefault("vinfo", {}).update(video_facts(*srcs))
    SCENE.setdefault("ainfo", {}).update(audio_facts(*srcs))      # 1.1.0: bitrate / muestreo del audio
    dicts = [d for d in srcs if isinstance(d, dict)]
    if any(d.get("is_live") for d in dicts) and (SCENE.get("mode_orig") or SCENE.get("mode")) != "live":
        # 1.0.7: el análisis llegó después de abrir la escena: pasa al dibujo de directo
        SCENE["mode"] = SCENE["mode_orig"] = "live"
        tg = SESSION.get("tag")
        if tg:
            SESSION["tag"] = (" " + tg[0].strip().split(" ", 1)[0] + " " + SITE_ICON["live"] + " ", tg[1], tg[2])
    elif (SCENE.get("mode_orig") or SCENE.get("mode")) == "list":
        for d in dicts:
            try:
                n = int(d.get("n_entries") or 0)
            except (TypeError, ValueError):
                n = 0
            if n > 1:
                SCENE["count"] = n
    if _site_sig() != _sig0:
        scene_site_mark()                                  # 1.8.1: llegó algo nuevo de lo detectado

def scene_facts_apply(real):
    """1.3.6:"""
    if not SCENE["on"] or not real:
        return
    v, a = real.get("v"), real.get("a")
    if v:
        w, h = v.get("width"), v.get("height")
        if h and not SCENE.get("res"):
            SCENE["res"] = int(h)
        if w and h and not SCENE.get("aspect"):
            SCENE["aspect"] = w / float(h)
        vi = SCENE.setdefault("vinfo", {})
        for k, key in (("codec", "codec"), ("fps", "fps"), ("kbps", "kbps")):
            if v.get(key) and not vi.get(k):
                vi[k] = v[key]
    if a:
        ai = SCENE.setdefault("ainfo", {})
        for k in ("codec", "kbps", "hz"):
            if a.get(k) and not ai.get(k):
                ai[k] = a[k]

def scene_facts_settle(kinds):
    """1.3.6: ya se intentó conocer el stream (leído o no): desde aquí las etiquetas marcan lo que sigue sin saberse (RES? · COD? · BIT? …)."""
    if not SCENE["on"]:
        return
    if "video" in kinds:
        SCENE.setdefault("vinfo", {})["settled"] = True
    if "audio" in kinds:
        SCENE.setdefault("ainfo", {})["settled"] = True

CONV_END_HOLD = LOOP_SECS

def ask_est_text(est):
    """«~45 s», «~3 min» (la estimación de una conversión); '' si no se sabe."""
    try:
        e = float(est or 0)
    except (TypeError, ValueError):
        return ""
    if e <= 0:
        return ""
    return "~%d %s" % (round(e), sec_unit()) if e < 90 else "~%d %s" % (round(e / 60.0), t_display("min"))

def _ask_l1(room, kind=None):
    """1.7.1: (línea de opciones ya en el idioma activo, ¿es la variante con «Toca la pantalla»?). Se elige la primera que, traducida, cabe en `room` columnas reales."""
    # 1.4.2: sustituir un archivo: Enter sustituye, n conserva
    if kind == "replace":
        cands = ("Toca la pantalla · Enter sustituir · n conservar", "Enter sustituir · n conservar", "Enter sustituir · n no", "Enter sí · n no", "Enter · n")
    else:
        cands = ("Toca la pantalla · Enter convertir · r remux · n original", "Enter convertir · r remux · n original",
                 "Enter convertir · r remux · n no", "Enter sí · r remux · n no", "Enter · r · n")
    i, txt = ux_pick(*cands, room=room, fallback="Enter")
    return txt, i == 0

def scene_ask_lines(room, est, left, kind=None):
    """(línea 1, línea 2) en el idioma activo. 1.7.1: se traduce primero y se mide después (antes se medía en español)."""
    l1 = _ask_l1(room, kind)[0]
    n = "%d %s" % (max(0, int(math.ceil(left))), sec_unit())
    if kind == "replace":
        l2 = ux_text("sin respuesta se sustituye · " + n, n, room=room, fallback=n)
        return l1, l2
    et = ask_est_text(est)
    l2 = ux_text((et + " · " if et else "") + "sin respuesta se convierte · " + n, "sin respuesta se convierte · " + n,
                 (et + " · " if et else "") + n, n, room=room, fallback=n)
    return l1, l2

def ask_key_mask(text):
    """1.1.4: índices de las teclas (Enter, r, n) en una línea de opciones separadas por « · ». 1.7.1: Enter con el nombre que tenga en el idioma (Entrée, Invio…)."""
    mask, i, names = set(), 0, ux_enter_names()
    for seg in str(text).split(" · "):
        w = seg.split(" ")[0]
        if w in names or w in ("r", "n"):
            mask.update(range(i, i + len(w)))
        i += len(seg) + 3
    return mask

ASK_HINT_CYCLE = 4.8

def ask_hint_texts(room, kind=None):
    """1.2.0:"""
    a = ux_text("Toca la pantalla para abrir el teclado", "Toca para abrir el teclado", "Toca = teclado", room=room, fallback="")
    qs = ("¿Sustituir el archivo?", "¿Sustituir archivo?", "¿Sustituir?") if kind == "replace" else ("¿Convertir este video?", "¿Convertir ahora?", "¿Convertir?")
    b = ux_text(*qs, room=room, fallback=qs[-1])
    return a, b, 0  # 1.7.1: el motor de texto traduce y mide por el ancho real

def scene_ask_cells(cells, ask, ta, y0, cx, W, g):
    """1.1.1:"""
    # 1.4.2: sugerencia · opciones · cuenta: tres filas hacia abajo desde el aire bajo el dibujo
    r0 = y0 + SCENE_STATUS_ROW - 1
    for key in [k for k in cells if k[1] in (r0, r0 + 1, r0 + 2)]:
        del cells[key]
    # 1.7.1: la pregunta del idioma (DLPY_LANGUAGE=ask) tiene sus propias tres filas
    if ask.get("kind") == "lang":
        return scene_lang_cells(cells, ask, ta, y0, cx, W, g)
    left = max(0.0, ask["secs"] - (time.time() - ask["t0"]))
    l1, l2 = scene_ask_lines(max(8, W - 6), ask.get("est"), left, ask.get("kind"))
    fd = smooth((ta - ask["ta0"]) / 0.5)
    n = len(l1)
    pos = (ta * 16.0) % (n + 12) - 6                                 # el brillo recorre la línea
    pulse = 0.5 + 0.5 * math.sin(ta * 4.0)
    keys = ask_key_mask(l1)
    x0 = cx - dwidth(l1) // 2

    def tone1(i, _ch):
        glow = max(0.0, 1.0 - abs(i - pos) / 4.0)
        if i in keys:
            col = mix(g(0.5), WHITE, 0.6 + 0.4 * pulse)
        else:
            col = mix(mix(BLACK, g(i / float(max(1, n))), 0.75), WHITE, 0.75 * glow)
        return mix(BLACK, col, fd)
    put_text(cells, x0, r0 + 1, l1, tone1, lo=1, hi=W)                       # 1.7.0: ancho real
    room = max(8, W - 6)
    # 1.2.0: con el teclado bajado hay que tocar la pantalla (1.7.1: sin comparar texto en español)
    if not _ask_l1(max(8, W - 6), ask.get("kind"))[1]:
        ha, hb, hk = ask_hint_texts(room, ask.get("kind"))
        t = max(0.0, ta - ask["ta0"])
        ph, ca, cb = t % ASK_HINT_CYCLE, scene_cols(ha, cx), scene_cols(hb, cx)
        if ph < 1.9:
            p, c0, c1 = 0.0, ca, ca
        elif ph < 2.4:
            p, c0, c1 = (ph - 1.9) / 0.5, ca, cb
        elif ph < 4.3:
            p, c0, c1 = 1.0, cb, cb
        else:
            p, c0, c1 = (ph - 4.3) / 0.5, cb, ca
        key_x = set(range(min(cb), min(cb) + hk)) if cb else set()
        f = int(ta * 24)
        for x, (ch, kind) in scene_morph(c0, c1, p, f).items():
            if ch == "":
                continue
            if kind == 1:
                col = mix(g(0.5), BLACK, 0.45)
            elif x in key_x and c1 is cb and kind == 2 or (x in key_x and c0 is cb and kind == 0):
                col = mix(g(0.5), WHITE, 0.6 + 0.4 * pulse)           # «Enter» resaltado, como en la línea de opciones
            else:
                col = mix(SCENE_GRAY, WHITE, 0.3 * pulse)
            cells[(x, r0)] = (ch, mix(BLACK, col, fd), None)
    urgent = left <= 5.0
    x1 = cx - dwidth(l2) // 2
    cnt_at = len(l2) - len("%d s" % int(math.ceil(left)))

    def tone2(i, _ch):
        col = mix((255, 176, 32), WHITE, 0.3 * pulse) if urgent and i >= cnt_at else SCENE_DIM if i < cnt_at else SCENE_GRAY
        return mix(BLACK, col, fd)
    put_text(cells, x1, r0 + 2, l2, tone2, lo=1, hi=W)                       # 1.7.0: ancho real
    return cells

LANG_TITLE_HOLD, LANG_TITLE_MORPH = 1.5, 0.4

def scene_lang_cells(cells, ask, ta, y0, cx, W, g):
    """1.7.1: la pregunta del idioma, en las tres filas de siempre bajo el dibujo (las que usa scene_ask_cells):
    fila 1 = un punto por idioma (● el elegido) y, en los últimos 10 s, la cuenta · fila 2 = «Seleccione idioma» (donde va el texto de estado) en cada idioma, uno tras otro,
    con el mismo morph del texto · fila 3 = «‹ p   Nombre   n ›»: el idioma elegido en su propio idioma y las teclas para moverse (Enter acepta)."""
    r0 = y0 + SCENE_STATUS_ROW - 1
    codes, sel = ask["codes"], ask["sel"]
    n = len(codes)
    t = max(0.0, ta - ask["ta0"])
    fd = smooth(t / 0.5)
    pulse = 0.5 + 0.5 * math.sin(ta * 4.0)
    room = max(8, W - 6)
    flash = max(0.0, 1.0 - (time.time() - ask.get("tk", 0.0)) / 0.35)          # destello al mover la selección
    left = max(0.0, ask["secs"] - (time.time() - ask["t0"]))
    dots = " ".join("●" if i == sel else "○" for i in range(n))
    x0 = cx - dwidth(dots) // 2

    def tone_dot(i, _ch):
        on = i == 2 * sel
        return mix(BLACK, mix(g(0.5), WHITE, 0.55 + 0.3 * flash) if on else SCENE_DIM, fd)
    put_text(cells, x0, r0, dots, tone_dot, lo=1, hi=W)
    if left <= 10.0 and W >= len(dots) + 12:
        cnt = "%d s" % int(math.ceil(left))
        put_text(cells, x0 + dwidth(dots) + 2, r0, cnt, mix(BLACK, mix((255, 176, 32), WHITE, 0.3 * pulse) if left <= 5.0 else SCENE_GRAY, fd), lo=1, hi=W)
    cyc = LANG_TITLE_HOLD + LANG_TITLE_MORPH
    i, ph = int(t // cyc), t % cyc
    ca = scene_cols(fit_text(LANG_SELECT_TEXT.get(codes[i % n], LANG_SELECT_TEXT["es"]), room), cx)      # 2.1.5: .get (sin paquetes solo hay «es»)
    cb = scene_cols(fit_text(LANG_SELECT_TEXT.get(codes[(i + 1) % n], LANG_SELECT_TEXT["es"]), room), cx)
    p = 0.0 if ph < LANG_TITLE_HOLD else (ph - LANG_TITLE_HOLD) / LANG_TITLE_MORPH
    f = int(ta * 24)
    for x, (ch, kind) in scene_morph(ca, cb if p > 0 else ca, p, f).items():
        if ch == "":
            continue
        col = mix(g(0.5), BLACK, 0.45) if kind == 1 else mix(SCENE_GRAY, WHITE, 0.45 + 0.25 * pulse)
        cells[(x, r0 + 1)] = (ch, mix(BLACK, col, fd), None)
    name = LANG_NAMES.get(codes[sel], codes[sel])
    wl, gap = 3, 3
    total = wl + gap + dwidth(name) + gap + wl
    xs = cx - total // 2
    key_col = mix(BLACK, mix(g(0.5), WHITE, 0.35 + 0.45 * flash), fd)
    put_text(cells, xs, r0 + 2, "‹ p", key_col, lo=1, hi=W)
    put_text(cells, xs + wl + gap, r0 + 2, name, mix(BLACK, mix(g(sel / float(max(1, n - 1))), WHITE, 0.6 + 0.3 * flash), fd), lo=1, hi=W)
    put_text(cells, xs + wl + gap + dwidth(name) + gap, r0 + 2, "n ›", key_col, lo=1, hi=W)
    return cells

def scene_stop(clear=False, cursor=True):
    """Para la escena y devuelve stdout. clear=True: borra y deja el banner (lo que sale después se ve como siempre)."""
    S = SCENE
    if not S["on"]:
        return False
    S["stop"] = True
    _FAST_WAKE.set()                                   # 1.6.4: si la escena dormía en convert_fast_anim, despierta ya
    th = S["th"]
    if th is not None and th.is_alive() and th is not threading.current_thread():
        th.join(timeout=1.0)
    if S["mute"] is not None:
        S["mute"].open = True
    if S.get("emute") is not None:
        with quiet("scene_stop stderr"):
            S["emute"].drain()
        S["emute"].open = True
    S["on"] = False
    with quiet("scene_stop"):
        S["out"].write(RESET + WRAP_ON + (CURSOR_SHOW if cursor else ""))
        S["out"].flush()
    if clear:
        clear_screen()
    return True

SCENE_ERR_SECS = 2.6                                # 1.0.8: s que se deja leer el error en D L P Y antes de cerrar

def scene_error_end():
    """1.0.8:"""
    if not SCENE["on"] or not SCENE.get("last_error"):
        return False
    try:
        SCENE["brand"] = True
        time.sleep(SCENE_TITLE_MORPH + SCENE_LAG_LABEL + SCENE_ERR_SECS)
        scene_outro()
    except KeyboardInterrupt:
        pass
    return True

def scene_end(view=False):
    """1.3.4:"""
    if not SCENE["on"]:
        return False
    # 1.0.8: hubo un error: se lee en D L P Y y la escena se cierra
    if SCENE.get("last_error"):
        scene_error_end()
    else:
        # 1.5.9: lo que hubiera en el centro se ve entero antes del envío…
        scene_gate("send")
        # …y D L P Y no teclea ningún comando para el texto anterior (era el «Guardando» de más, ~1.7 s con el comando de arranque)
        SCENE["label_wall"] = None
        scene_busy(False)
        # 1.3.4: el chip y el texto dicen adónde va el archivo de verdad
        SCENE["send_to"] = "view" if view else None
        # 1.9.8: el envío NO es D L P Y (esa escena es solo del arranque y de las actualizaciones): el título sigue siendo el del video
        scene_status(send_key(view), frac=1.0)           # 1.9.8: la clave, no el texto traducido
        # 1.5.9: modo «wait»: el envío se ve entero (entrar + su ciclo), sin los segundos fijos de antes
        if SCENE_MODE[0] == "loop":
            _t_send = time.time()
            scene_gate()
            # el título termina de transformarse
            time.sleep(max(0.0, SCENE_TITLE_MORPH + 0.35 - (time.time() - _t_send)))
        else:
            # 1.1.3: el título, el texto y el cometa del envío se leen (1.3.2: N s con un número)
            time.sleep(max(SCENE_TITLE_MORPH + 0.35, scene_dwell(SCENE_SEND_SECS)))
        scene_outro()                                         # el hilo de la escena pinta el cierre
    scene_stop(cursor=False)
    if QUIET["on"]:
        quiet_set(False)
    with quiet("scene_end clear"):
        native_clear()
        sys.stdout.write(RESET + CURSOR_SHOW)
        sys.stdout.flush()
    return True

def scene_error_text(msg, limit=56):
    """1.0.8: el error en una línea corta para la escena: sin colores ni prefijos repetidos («Error al descargar: ERROR: …»)."""
    t = " ".join(_ANSI_RE.sub("", str(msg)).split())
    while True:
        t2 = re.sub(r"^(error(\s+al\s+\w+)?|\[?error\]?)\s*:\s*", "", t, flags=re.I)
        if t2 == t:
            break
        t = t2
    t = t or "Error"
    return t if len(t) <= limit else t[:max(1, limit - 1)].rstrip() + "…"

def scene_set_error(msg):
    """1.0.8:"""
    SCENE["last_error"] = scene_error_text(msg, 200)
    SCENE["brand"], SCENE["err_brand"] = True, True
    SCENE["label"], SCENE["pct"] = "Error: " + scene_error_text(msg, 56), None

def ux_download_begin():
    """La descarga se prepara."""
    if SCENE["on"]:
        SCENE["speed"], SCENE["speed_last"], SCENE["speed_peak"], SCENE["speed_t"], SCENE["speed_end"] = None, None, 0.0, None, None
        # 1.7.0: mientras yt-dlp aún no informó de ninguna pista, la regla barre: se ve que está vivo
        SCENE["busy"] = True
    scene_status("Preparando descarga", frac=0.08)

def ux_download_stream(d, seen, total):
    """Empieza una pista: la escena toma su forma (proporción), su tipo y su idioma, y se leen sus datos reales."""
    scene_shape(d.get("info_dict"))
    scene_stream(scene_kind(d), seen, total, scene_lang(d))
    ux_download_facts(d)

def ux_download_facts(d):
    """1.3.6 (movido aquí desde DownloadUI en 1.5.7): los datos reales del stream (resolución, fps, códec…) para el dibujo del centro; solo con escena."""
    with quiet("_facts"):
        if not SCENE["on"]:
            return
        info, kinds = (d.get("info_dict") or {}), stream_kinds(d)
        if not stream_needs_probe(info, kinds):
            scene_facts_settle(kinds)
            return

        def work():
            real = None
            with quiet("_facts"):
                real = probe_stream_facts(_FfmpegShim().executable, info)
            try:
                dbg("datos reales del stream", {"format_id": info.get("format_id"), "leido": real})
                scene_facts_apply(real)
            finally:
                scene_facts_settle(kinds)
        threading.Thread(target=work, daemon=True, name="dlpy-facts").start()

def ux_download_speed(spd):
    """1.7.0: la velocidad en curso (B/s) para la animación de velocidad de la escena; sin escena no guarda nada."""
    if not SCENE["on"]:
        return
    if spd is None or spd <= 0:
        SCENE["speed"] = 0.0          # 0: sigue esperando (la animación late), no se borra el pico
        return
    SCENE["speed"] = float(spd)
    SCENE["speed_peak"] = max(float(SCENE.get("speed_peak") or 0.0), float(spd))
    if SCENE.get("speed_t") is None:
        SCENE["speed_t"] = time.time()
    SCENE["speed_end"] = None

def ux_download_progress(pct):
    """El avance de la pista en curso (None si no hay total)."""
    scene_progress(pct)

def ux_download_stream_done(d):
    """La pista terminó (1.3.6: un stream con video y audio en uno da por hechos los dos)."""
    if SCENE["on"]:
        # 1.7.0: el medidor se apaga con fundido (0,6 s) desde la última velocidad
        SCENE["speed_last"] = SCENE.get("speed")
        SCENE["speed"] = None
        SCENE["speed_end"] = time.time()
        SCENE["busy"] = False
    scene_progress(100.0)
    try:
        for _k in stream_kinds(d):
            scene_stream_done(_k)
    except Exception as _ign:
        ignore('escena: cierre de streams', _ign)

def ux_pp_start(name):
    """Empieza un postproceso de yt-dlp (unir, convertir…): el texto de la escena y el avance de la unión a cero."""
    SCENE["pp_pct"] = None
    scene_status(scene_pp_text(name), frac=min(0.94, max(SCENE["frac"], 0.8) + 0.03))


CHIP_CODEC = {"h264": "H.264", "hevc": "HEVC", "vp9": "VP9", "vp8": "VP8", "av1": "AV1", "mpeg4": "MPEG-4", "mpeg2video": "MPEG-2",
              "aac": "AAC", "opus": "Opus", "vorbis": "Vorbis", "mp3": "MP3", "ac3": "AC-3", "eac3": "E-AC-3", "flac": "FLAC", "alac": "ALAC"}
ENC_DST = {"hevc_videotoolbox": "HEVC", "libx265": "HEVC", "libkvazaar": "HEVC", "libx264": "H.264", "h264_videotoolbox": "H.264"}


def conv_chips(path, streams, plan, final_ext, enc):
    """0.0.2: (origen, destino) de los chips: lo MAS pesado que cambia (video recodificado > audio > etiqueta > contenedor)."""
    vs = [x for x in streams if x["type"] == "video"][:1]
    au = [x for x in streams if x["type"] == "audio"]
    nm = lambda c: CHIP_CODEC.get(c, (c or "?").upper())
    if vs and enc in ENC_DST:
        return nm(vs[0]["codec"]), ENC_DST[enc]
    for a, m in zip(au, plan["a"]):
        if m != "copy":
            return nm(a["codec"]), "AAC"
    if vs and plan["tag"]:
        return (vs[0]["tag"] or "hev1").upper(), "HVC1"
    return (os.path.splitext(path)[1][1:] or "?").upper(), (final_ext[1:] or "?").upper()


def ux_conv_begin(src, dst, codec=None):
    """0.0.2: empieza la conversion: chips origen → destino, via de puntos sin % todavia y, de titulo, el codigo de destino.
    Primero espera (modo wait) a que el dibujo que ocupa el centro se vea entero; un intento nuevo tras un fallo reinicia la via sin esperar."""
    S = SCENE
    if not S["on"]:
        return
    prev = S.get("conv")
    if not (prev and prev.get("end") is None):
        scene_gate("conv")
    scene_busy(False)
    S["pp_pct"] = None
    S["conv"] = {"src": ux_chip(src) or "?", "dst": ux_chip(dst) or "?", "codec": ux_chip(codec or dst) or "",
                 "pct": None, "end": None, "t0": float(S.get("ta") or 0.0)}
    scene_status("Convirtiendo", frac=min(0.94, max(S["frac"], 0.8) + 0.03))
    _FAST_WAKE.set()


def ux_conv_progress(pct):
    """0.0.2: el % real de ffmpeg (None = sin dato: la via sigue tenue). Mueve la via, la regla y el texto de estado."""
    S = SCENE
    cv = S.get("conv") if S["on"] else None
    if not cv or cv.get("end") is not None:
        return
    try:
        p = None if pct is None else max(0.0, min(100.0, float(pct)))
    except (TypeError, ValueError):
        p = None
    old = cv.get("pct")
    cv["pct"] = p
    S["pct"] = p
    if p is not None:
        S["frac"] = max(S["frac"], min(0.97, 0.83 + 0.14 * p / 100.0))
    if (None if old is None else int(old)) != (None if p is None else int(p)):
        _FAST_WAKE.set()                       # convert_fast_anim: el cuadro solo se repinta cuando cambia el % entero


def ux_conv_end(ok=True):
    """0.0.2: ok → la via se llena y el destino destella (el dibujo cierra su loop); no ok → se quita sin destello."""
    S = SCENE
    cv = S.get("conv") if S["on"] else None
    if not cv or cv.get("end") is not None:
        return
    if ok:
        cv["pct"], S["pct"] = 100.0, 100.0
        cv["end"] = float(S.get("ta") or 0.0)
        S["frac"] = max(S["frac"], 0.97)
    else:
        S["conv"], S["pct"] = None, None
    _FAST_WAKE.set()


def ux_end(*a, **k):
    return scene_end(*a, **k)

def ux_error_end(*a, **k):
    return scene_error_end(*a, **k)


def ux_set_error(*a, **k):
    return scene_set_error(*a, **k)


def ux_start(*a, **k):
    return scene_start(*a, **k)

def ux_status(*a, **k):
    return scene_status(*a, **k)

def ux_stop(*a, **k):
    return scene_stop(*a, **k)

def ux_title(*a, **k):
    return scene_title(*a, **k)


CODEC_NAMES = {"avc1": "H.264", "avc3": "H.264", "h264": "H.264", "hvc1": "HEVC", "hev1": "HEVC", "hevc": "HEVC",
               "dvh1": "Dolby Vision", "dvhe": "Dolby Vision", "vp9": "VP9", "vp09": "VP9", "av01": "AV1", "av1": "AV1",
               "mp4a": "AAC", "aac": "AAC", "opus": "Opus", "prores": "ProRes", "ec-3": "E-AC-3", "eac3": "E-AC-3", "ac-3": "AC-3",
               "ac3": "AC-3", "flac": "FLAC", "alac": "ALAC", "mp3": "MP3", "vorbis": "Vorbis"}

def codec_name(codec):
    """«avc1.640028» → «H.264»; lo que no se conoce sale en mayúsculas; sin dato → ''."""
    c = str(codec or "").lower().split(".")[0]
    return CODEC_NAMES.get(c) or (c.upper() if c and c != "?" else "")

def kv(label, value, flag=None):
    label = t_display(label)  # 1.7.0
    value = t_display(value) if isinstance(value, str) else value
    w = term_width()
    lead = f"{label}: "
    extra = 2 if flag else 0
    lines = wrap_text(str(value), max(8, w - len(lead) - extra))
    if flag:
        lines[-1] += " " + flag_mark(flag)
    print(paint(lead, "gray") + lines[0])
    for ln in lines[1:]:
        print(" " * len(lead) + ln)

def speed_text(v):
    """Velocidad de bajada con el mismo formato en todas las barras."""
    return f"↓ {human_size(v)}/s"

def human_size(n):
    """«48 MB», «1.9 GB», «3.0 MB»: con un decimal por debajo de 10 y entero desde 10; decimal según idioma."""
    if not n:
        return "?"
    for u in ("B", "KB", "MB", "GB"):
        # 1.7.5: con 0 decimales 1023.5 ya se lee «1024»: pasa al siguiente escalón
        if n < 1023.5:
            if u == "B" or n >= 9.95:
                return f"{loc_num(n, 0)} {u}"
            return f"{loc_num(n, 1)} {u}"
        n /= 1024
    return f"{loc_num(n, 1)} TB"

APPLE_MARK = "\uf8ff"                  # manzana mordida (logo de Apple, solo se ve en dispositivos Apple)

APPLE_MARK_UNSURE = APPLE_MARK + "?"   # 1.6.9: códec sin determinar (normalmente nativo de Apple, sin comprobar)

FLAG_MARKS["logo"], FLAG_COLORS["logo"], FLAG_TEXT["logo"] = APPLE_MARK, "mint", FLAG_TEXT["apple"]

FLAG_MARKS["logo?"], FLAG_COLORS["logo?"], FLAG_TEXT["logo?"] = APPLE_MARK_UNSURE, "amber", FLAG_TEXT["apple"]


# ══════════════════════════════════════ ADAPTADOR PARA dlpy.py ══════════════════════════════════════
# dlpy.py solo habla con esto: AnimUI(...).begin() / .hook(d) / .pp_hook(d) / .end(...) / .abort().
# Es el equivalente reducido de DownloadUI de la 2.1.5 (sin Bar): los avisos van a la escena por el puente ux_*.
import types


def available():
    """¿Puede pintarse la escena en esta ejecución? (terminal real, color, animaciones activas)."""
    try:
        return bool(ANIM and USE_COLOR and TRUECOLOR and SITE_ANIM and sys.stdout.isatty() and not DEBUG)
    except Exception:
        return False


def _pct(d):
    tot = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
    done = d.get("downloaded_bytes") or 0
    if not tot:
        return None
    return max(0.0, min(100.0, done * 100.0 / tot))


class AnimUI:
    """Une los hooks de yt-dlp con la escena. Un fallo de la interfaz nunca aborta la descarga."""

    def __init__(self, url, total=1, audio_only=False, title=""):
        self.run = types.SimpleNamespace(link=url, info=None, kind="a" if audio_only else "v", selected=None,
                                         fmt={}, spick={"v": "audio" if audio_only else "video"}, title=title or "")
        self.total = max(1, int(total or 1))
        self.on = False
        self.seen = 0
        self.key = None
        self._started = False
        self._key_none = False
        self._titled = False
        self._reset_speed()

    # ---- velocidad estable (ventana de ~4 s), como DownloadUI._speed ----
    def _reset_speed(self):
        self._smp, self._spd, self._win = None, None, []

    def _speed(self, d):
        done = d.get("downloaded_bytes") or 0
        now = time.time()
        if self._smp is None:
            self._smp = (now, done)
        elif now - self._smp[0] >= 0.5 and done >= self._smp[1]:
            inst = (done - self._smp[1]) / (now - self._smp[0])
            self._spd = inst if self._spd is None else self._spd * 0.7 + inst * 0.3
            self._smp = (now, done)
        win = self._win
        if not win or now - win[-1][0] >= 0.25:
            if win and done < win[-1][1]:
                del win[:]
            win.append((now, done))
        while len(win) > 2 and now - win[0][0] > 4.0:
            del win[0]
        if len(win) >= 2 and win[-1][0] - win[0][0] >= 1.0:
            avg = (win[-1][1] - win[0][1]) / (win[-1][0] - win[0][0])
            if avg > 0:
                return avg
        sp = d.get("speed")
        return sp if sp else self._spd

    # ---- ciclo de vida ----
    def begin(self):
        """Arranca la escena. False = no hay escena (el host usa su barra simple)."""
        try:
            if not available():
                return False
            self.on = bool(ux_start(self.run))
            if self.on:
                ux_download_begin()
        except Exception:
            self.on = False
            _safe_stop()
        return self.on

    def hook(self, d):
        if not self.on:
            return
        try:
            self._hook(d)
        except Exception as e:
            dbg("anim: fallo en el hook de descarga", "%s: %s" % (type(e).__name__, e))

    def _hook(self, d):
        st = d.get("status")
        info = d.get("info_dict") or {}
        key = d.get("filename") or info.get("format_id")
        if st == "downloading":
            if self._started and self._key_none and key is not None:
                self.key, self._key_none = key, False
            if key != self.key or not self._started:
                self.seen += 1
                if not self._titled and info.get("title"):
                    ux_title(info.get("title"))
                    self._titled = True
                ux_download_stream(d, self.seen, self.total)
                self.key, self._started, self._key_none = key, True, key is None
                self._reset_speed()
            ux_download_progress(_pct(d))
            ux_download_speed(self._speed(d))
        elif st == "finished" and self.key is not None and key == self.key:
            ux_download_progress(100.0)
            ux_download_stream_done(d)
            self.key = None

    def pp_hook(self, d):
        if not self.on:
            return
        try:
            if d.get("status") == "started":
                self.key = None
                ux_pp_start(str(d.get("postprocessor") or ""))
        except Exception as e:
            dbg("anim: fallo en el hook de proceso", "%s: %s" % (type(e).__name__, e))

    # ---- conversion (0.0.2) ----
    def conv_begin(self, path, streams, plan, final_ext, enc):
        """Empieza (o reinicia tras un intento fallido) la escena de conversion. El host da lo crudo (archivo, pistas de ffprobe, plan,
        extension final y encoder del intento); los chips los decide conv_chips."""
        if self.on:
            try:
                src, dst = conv_chips(path, streams, plan, final_ext, enc)
                ux_conv_begin(src, dst)
            except Exception as e:
                dbg("anim: fallo al iniciar la conversión", "%s: %s" % (type(e).__name__, e))

    def conv_progress(self, pct):
        """% real de la conversion (0-100) o None si no hay dato."""
        if self.on:
            try:
                ux_conv_progress(pct)
            except Exception as e:
                dbg("anim: fallo en el avance de conversión", "%s: %s" % (type(e).__name__, e))

    def conv_end(self, ok=True):
        """Termina la conversion: ok=True llena la via; ok=False la quita."""
        if self.on:
            try:
                ux_conv_end(ok)
            except Exception as e:
                dbg("anim: fallo al cerrar la conversión", "%s: %s" % (type(e).__name__, e))

    def status(self, text, frac=None):
        if self.on:
            try:
                ux_status(text, frac=frac)
            except Exception:
                pass

    def end(self, ok=True, error="", send=True):
        """Cierra la escena. ok=False: el error se lee en D L P Y y se cierra. send=False: se cierra sin la animación de envío."""
        if not self.on:
            return
        self.on = False
        try:
            if not ok:
                ux_set_error(error or "Error")
                ux_error_end()
                ux_stop(clear=True)
            elif send:
                ux_status("Guardado", frac=1.0)
                ux_end()
            else:
                ux_stop(clear=True)
        except Exception as e:
            dbg("anim: fallo al cerrar", "%s: %s" % (type(e).__name__, e))
            _safe_stop()

    def abort(self):
        """Ctrl-C u otra salida anómala: la escena cede ya y el terminal queda limpio."""
        self.on = False
        _safe_stop()


def _safe_stop():
    try:
        ux_stop(clear=True)
    except Exception:
        pass


def _cli(argv):
    """0.0.3: `python dlpy_anim.py --fps` dice los cuadros por segundo; `--fps N` (15–120) los guarda en dlpy_anim.json junto a este modulo."""
    if len(argv) >= 2 and argv[1] == "--fps":
        if len(argv) == 2:
            return print("%d fps" % ANIM_FPS)
        try:
            n = float(argv[2].replace(",", "."))
        except ValueError:
            return print("Uso: python dlpy_anim.py --fps <%d-%d>" % (FPS_MIN, FPS_MAX))
        n = fps_parse(n)
        try:
            with open(fps_file(), "w", encoding="utf-8") as f:
                json.dump({"fps": n}, f)
            return print("✅ %d fps (se aplica la proxima vez que corra DLpy)" % n)
        except OSError as e:
            return print("⚠️ No se pudo guardar: %s" % e)
    print("DLpy - animaciones %s. Uso: python dlpy_anim.py --fps [%d-%d]" % (VERSION, FPS_MIN, FPS_MAX))


if __name__ == "__main__":
    _cli(sys.argv)
