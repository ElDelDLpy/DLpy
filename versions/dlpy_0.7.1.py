#!dlpy.py - siempre empezar el script con este mismo comentario.
# Cada edicion de este archivo sube la version: x.y.z donde Y y Z solo llegan hasta el 9 y X no tiene limites.
# Cada edicion mete el changelog en el py borrando los changelog que no sean de la version actual.
# Respetar entrga de archivos con dlpy_x.y.z.py (dar archivos con ese orden siempre de nombre siempre sustituyendo x y x con los números correspondientes).
# Conservar en todo momento los comentarios anteriores en el mismo orden sin importar las ediciones realizadas.

# ==== CHANGELOG ====
# ## 0.7.1
#
# - Cada tipo de mensaje tiene su propio símbolo (✓ correcto, ! aviso, ✕ error, ● información): se distinguen
#   también sin color. Antes los cuatro eran «●» y solo cambiaba el color.
# - Al cambiar de versión (subida o bajada) sale una sola tarjeta con lo ocurrido (versión, dónde quedó la
#   anterior y el reinicio de .dlpy_internal), en lugar de varios mensajes sueltos. Se quita el aviso de datos
#   incompatibles en cambios de versión mayor: cada versión ya empieza de cero.
# - Al terminar la descarga sale una tarjeta con el resultado (título, resolución, códec, tamaño, duración y
#   archivo), con el mismo marco que el encabezado.
# - Autoprueba nueva [T24] de los símbolos y las tarjetas.
# ==== FIN CHANGELOG ====

VERSION = "0.7.1"

# Índice de secciones (cada una empieza con una cabecera «# ──── Título ────»; busca el título):
#   Variables DLPY_* recordadas · Plataforma · Rutas · Compatibilidad nativa Apple · Interfaz · Terminal:
#   ancho y texto · Mensajes y debug · Comentarios inteligentes (humor según el uso) · Pantalla: banner,
#   títulos y listas · Barras y paneles de progreso · Terminal: teclado y cuenta regresiva · Utilidades ·
#   Formatos y pistas: etiquetas y selección · Post-proceso: pista predeterminada · Compatibilidad Apple:
#   conversión opcional · Bits, HDR y sondeo del video · Ya descargado: reutilizar o convertir · JSON /
#   índice · Enlace y portapapeles · Dependencias · Actualizaciones (Releases de GitHub) · YouTube: runtime de
#   JavaScript + yt-dlp-ejs · Rechazos recordados · Changelog y backup · Limpieza de almacenamiento ·
#   Control de versión · Releases de GitHub y backups
#   (listado) · Comparar versiones: huellas y diferencias · Fallos: historial y avisos · Pantalla de
#   versiones (--versions) · Recuperación tras un fallo · Caché de streams (24 h) · Reanudación de descargas ·
#   Limpieza de la carpeta interna · Entrega del archivo (Atajos) · Atajo de iOS (--2shortcuts) · Análisis
#   tolerante (equivalente al yt-dlp en bruto) · Error «no eres un bot» · Modo atajo (--scm / --scb) ·
#   Autoprueba · Funciones disponibles según el sistema · Principal
#
# Etiquetas para navegar: cada sección, cada tramo grande de main() y de selftest() lleva una «[X0]».
# En a-Shell: grep -n "\[G3\]" dlpy.py (o la búsqueda de tu editor). Mapa:
#   ÁREA A · NÚCLEO: [A1] Variables DLPY_* recordadas, [A2] Plataforma, [A3] Rutas, [A4] Compatibilidad nativa Apple, [A5] Interfaz
#   ÁREA B · TERMINAL Y PANTALLA: [B1] Terminal, [B2] Mensajes y debug, [B3] Comentarios inteligentes (hu, [B4] Pantalla, [B5] Barras y paneles de progreso, [B6] Terminal
#   ÁREA C · UTILIDADES Y FORMATOS: [C1] Utilidades, [C2] Formatos y pistas
#   ÁREA D · POST-PROCESO Y CONVERSIÓN: [D1] Post-proceso, [D2] Compatibilidad Apple, [D3] Bits, HDR y sondeo del video, [D4] Ya descargado
#   ÁREA E · ESTADO Y ENTRADA: [E1] JSON / índice, [E2] Enlace y portapapeles
#   ÁREA F · DEPENDENCIAS Y ACTUALIZACIÓN: [F1] Dependencias, [F2] Actualizaciones, [F3] YouTube, [F4] Rechazos recordados
#   ÁREA G · MANTENIMIENTO Y VERSIONES: [G1] Changelog y backup, [G2] Limpieza de almacenamiento, [G3] Control de versión, [G5] Releases de GitHub y backups, [G6] Comparar versiones, [G7] Fallos, [G8] Pantalla de versiones (--ver
#   ÁREA H · RECUPERACIÓN Y CACHÉ: [H1] Recuperación tras un fallo, [H2] Caché de streams (24 h), [H3] Reanudación de descargas, [H4] Limpieza de la carpeta inter
#   ÁREA I · ENTREGA Y ANÁLISIS: [I1] Entrega del archivo (Atajos), [I2] Atajo de iOS (--2shortcuts), [I3] Análisis tolerante (equivale, [I4] Error «no eres un bot»
#   ÁREA J · MODO ATAJO: [J1] Modo atajo (--scm / --scb)
#   ÁREA K · AUTOPRUEBA Y SISTEMA: [K1] Autoprueba, [K2] Funciones disponibles según 
#   ÁREA L · PRINCIPAL: [L1] Principal
#   main(): [M0a] modos especiales · [M0b] preparación · [M0c] actualización y dependencias · [M1] enlace y análisis ·
#           [M2] lista y elección · [M3] resumen · [M4] pistas, conversión y ya descargado · [M5] nombre y trabajo ·
#           [M6] descarga con yt-dlp · [M7] mover el resultado · [M8] registrar y entregar
#   selftest(): [T0]…[T24] (cada una antes de su grupo de pruebas; el código está dentro del texto SELFTEST_SRC)

import atexit
import math
import os
import re
import glob
import random
import site
import sys
import json
import time
import uuid
import shlex
import shutil
import threading
import unicodedata
import urllib.parse

# ╔════════════════════════════════════════════════════════════════════════════════╗
# ║ ÁREA A · NÚCLEO — entorno, plataforma, rutas, compatibilidad Apple, interfaz   ║
# ╚════════════════════════════════════════════════════════════════════════════════╝
# ─────────────────────── [A1] Variables DLPY_* recordadas ───────────────────────
ENV_NAME = "env.json"
INTERNAL_NAME = ".dlpy_internal"          # carpeta oculta dentro de dlpy_files
ENV_SKIP = {"DLPY_MOVED", "DLPY_ORIGIN", "DLPY_ACTION", "DLPY_ANDROID_ACTION", "DLPY_FORGET"}   # de una sola ejecución
ENV_STATE = {"path": None, "error": None}  # dónde se guardó y por qué falló


def _read_env_json(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str)
                    and k.startswith("DLPY_") and k not in ENV_SKIP}
    except (OSError, ValueError):
        pass
    return {}


def persist_env(env=None, path=None):
    """Las DLPY_* definidas se guardan en `path`; las no definidas se recuperan de ahí (en a-Shell las
    «export» se pierden entre sesiones). DLPY_FORGET=1 olvida lo guardado. Devuelve lo que quedó guardado.
    Crea la carpeta de `path` si falta; si no puede guardar, deja el motivo en ENV_STATE['error']."""
    env = os.environ if env is None else env
    path = path or ENV_FILE
    ENV_STATE["path"], ENV_STATE["error"] = path, None
    try:
        disk = _read_env_json(path)
        forget = (env.get("DLPY_FORGET") or "").strip().lower() not in ("", "0", "no", "false")
        merged = {} if forget else dict(disk)
        merged.update({k: v for k, v in env.items() if k.startswith("DLPY_") and k not in ENV_SKIP})
        for k, v in merged.items():
            if k not in env:
                env[k] = v
        if merged != disk:
            folder = os.path.dirname(path)
            if folder:
                os.makedirs(folder, exist_ok=True)
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(merged, fh, ensure_ascii=False, indent=1, sort_keys=True)
            os.replace(tmp, path)
        return merged
    except Exception as e:
        ENV_STATE["error"] = f"{type(e).__name__}: {e}"
        return {}


# ─────────────────────── [A2] Plataforma ───────────────────────
# DLpy solo corre en iOS (a-Shell).
PLATFORM = "ios"
IS_IOS = True
APPLE_MODE = True          # códecs nativos de Apple + conversión opcional
PLAT_LABEL = "Apple"
ANSI_OK = True             # a-Shell entiende las secuencias ANSI


def platform_name(env=None):
    """Texto corto para el banner: en qué app corre DLpy."""
    env = os.environ if env is None else env
    app = (env.get("APPNAME") or "").lower()
    return ("a-Shell mini" if "mini" in app else "a-Shell") + " · iOS"


def machine_name():
    try:
        import platform as _pl
        return _pl.machine() or "?"
    except Exception:
        return "?"


def env_file_path(home=None):
    """Dónde se guardan las DLPY_*: dentro de la carpeta oculta de dlpy_files (en a-Shell «~» es
    la raíz del contenedor y ahí no se puede escribir)."""
    home = home or os.path.expanduser("~")
    return os.path.join(home, "Documents", "dlpy_files", INTERNAL_NAME, ENV_NAME)


ENV_FILE = env_file_path()
if not any(a.lstrip("-\u2013\u2014").lower() == "selftest" for a in sys.argv[1:]):
    persist_env(path=ENV_FILE)


# ───────────────────────── [A3] Rutas ─────────────────────────
HOME = os.path.expanduser("~")
# Completadas + backups únicamente
FILES_DIR = os.path.join(HOME, "Documents", "dlpy_files")
DOWNLOAD_DIR = FILES_DIR      # las descargas terminadas viven en dlpy_files
SHORTCUTS_DIR = os.environ.get("SHORTCUTS") or os.path.join(HOME, "Library", "Shortcuts")
# Índice, estado, caché, trabajo temporal, changelog, variables DLPY_* (carpeta oculta dentro de dlpy_files)
INTERNAL_DIR = os.path.join(FILES_DIR, INTERNAL_NAME)
# .dlpy_internal/: env.json (variables DLPY_*), state/ (estado), script/ (copia y changelog), cache/streams/,
# work/ (descargas en curso) y delivery/<id>/ (copias de entrega al atajo).
# Se borra entera en cada subida o bajada de versión (reset_internal): cada versión empieza de cero.
STATE_DIR = os.path.join(INTERNAL_DIR, "state")
SCRIPT_DIR = os.path.join(INTERNAL_DIR, "script")
CACHE_DIR = os.path.join(INTERNAL_DIR, "cache")
INDEX_FILE = os.path.join(STATE_DIR, "index.json")
HISTORY_FILE = os.path.join(STATE_DIR, "downloads.json")      # todo lo descargado de cada video: {clave: [entrada, ...]}
CRASHES_JSON_FILE = os.path.join(INTERNAL_DIR, "crashes_dlpy.json")
LAST_FILE = os.path.join(STATE_DIR, "last_link.json")
VERSION_FILE = os.path.join(STATE_DIR, "version.json")
DOWNGRADE_FILE = os.path.join(STATE_DIR, "downgrades.json")   # bajadas de versión (historial y pendiente)
CHECK_FILE = os.path.join(STATE_DIR, "checks.json")
DEPS_STATE_FILE = os.path.join(STATE_DIR, "deps.json")      # rechazos recordados
RUNNING_FILE = os.path.join(STATE_DIR, "running.json")      # ejecución en curso
CRASH_FILE = os.path.join(STATE_DIR, "crash.json")          # último fallo
CRASH_LOG_FILE = os.path.join(STATE_DIR, "crash_log.json")  # historial de fallos (con huella del código)
RECOVERED_FILE = os.path.join(STATE_DIR, "recovered.json")  # versión recuperada tras un fallo
GOOD_FILE = os.path.join(STATE_DIR, "good_versions.json")   # versiones que ya terminaron bien
SHORTCUT_JSON = os.path.join(STATE_DIR, "shortcut_analysis.json")      # copia legible de la última salida
SNAPSHOT_FILE = os.path.join(SCRIPT_DIR, "script_snapshot.py")
CHANGELOG_FILE = os.path.join(SCRIPT_DIR, "changelog.md")
BACKUP_DIR = os.path.join(FILES_DIR, "backups")
STREAM_CACHE_DIR = os.path.join(CACHE_DIR, "streams")
WORK_ROOT = os.path.join(INTERNAL_DIR, "work")
DELIVERY_DIR = os.path.join(INTERNAL_DIR, "delivery")
# En FILES_DIR no se considera "descarga" lo que esté en backups/ ni el changelog
RESERVED = {"backups", "changelog.md"}
SCRIPT_PATH = os.path.abspath(__file__)
SHORTCUT_NAME = "DLpy"
MAX_NAME_BYTES = 120
INTERNAL_TTL = 24 * 3600          # entrega temporal al atajo
STREAM_CACHE_TTL = 24 * 3600      # reutilización de pistas/formatos
VER_DIR_RE = re.compile(r"^\d+\.\d+\.\d+(-\d+)?$")
VER_FILE_RE = re.compile(r"^dlpy_(\d+\.\d+\.\d+)\.py$")

# Bloque del changelog dentro del .py (tolerante con espacios, mayúsculas y CRLF)
CL_RE = re.compile(r"(?m)^#[ \t]*={3,}[ \t]*CHANGELOG[ \t]*={3,}[ \t]*\r?\n(.*?)"
                   r"^#[ \t]*={3,}[ \t]*FIN[ \t]+CHANGELOG[ \t]*={3,}[ \t]*(?:\r?\n|\Z)",
                   re.S | re.I)

# Extensiones que cuentan como «video» al borrar por límite de almacenamiento
VIDEO_EXTS = {"mp4", "m4v", "mov", "mkv", "webm", "avi", "flv", "wmv", "mpg", "mpeg",
              "ogv", "3gp", "ts", "mts", "m2ts"}

# Descargas «como tal» (para limpiar backups): video + audio + subtítulos e imágenes
AUDIO_EXTS = {"m4a", "mp3", "aac", "opus", "ogg", "oga", "wav", "flac", "aiff", "aif",
              "caf", "wma", "weba", "mka", "alac", "ac3", "eac3"}
EXTRA_EXTS = {"srt", "vtt", "ass", "lrc", "jpg", "jpeg", "png", "webp", "gif"}
DOWNLOAD_EXTS = VIDEO_EXTS | AUDIO_EXTS | EXTRA_EXTS

# (nombre en pip, módulo, obligatoria)
DEPENDENCIES = [("yt-dlp", "yt_dlp", True)]

# ─────────────── [A4] Compatibilidad nativa Apple ───────────────
APPLE_VCODEC = ("avc1", "h264", "hvc1", "hev1", "hevc")
APPLE_ACODEC = ("mp4a", "aac", "alac", "mp3", "ac-3", "ec-3", "ac3", "eac3", "flac")
APPLE_VEXT = ("mp4", "m4v", "mov")
APPLE_AEXT = ("m4a", "mp4", "mp3", "aac", "wav", "aiff", "caf", "flac")
GUESS_VEXT = APPLE_VEXT      # contenedores donde se asume avc1/mp4a si yt-dlp no da códecs


def has(codec):
    return bool(codec) and codec != "none"


def apple_audio(f):
    a = (f.get("acodec") or "").lower()
    return has(a) and a.startswith(APPLE_ACODEC) and f.get("ext") in APPLE_AEXT


def apple_video(f):
    v = (f.get("vcodec") or "").lower()
    if not (has(v) and v.startswith(APPLE_VCODEC) and f.get("ext") in APPLE_VEXT):
        return False
    a = (f.get("acodec") or "").lower()
    return (not has(a)) or a.startswith(APPLE_ACODEC)


# ───────────────────────── [A5] Interfaz ─────────────────────────
WAIT_SECONDS = 10
PHANTOM_SECS = 0.4        # un Enter vacío antes de este tiempo se considera fantasma
PHANTOM_BOOT = 1.0        # ... y también en el primer segundo de la ejecución
START_T = time.time()
DEBUG = os.environ.get("DLPY_DEBUG", "").strip().lower() not in ("", "0", "no", "false")
_env_color = os.environ.get("DLPY_COLOR")
if _env_color is not None:
    USE_COLOR = _env_color.strip().lower() not in ("0", "no", "false", "")
else:
    USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR") and ANSI_OK
CLR = "\r\x1b[2K" if sys.stdout.isatty() and ANSI_OK else "\r"
# Secuencia de clear_screen (DLPY_CLEAR=1..4; por defecto 3)
CLEAR_SEQS = {"1": "\x1b[3J\x1b[2J\x1b[H", "2": "\x1b[2J\x1b[3J\x1b[H",
              "3": "\x1bc", "4": "\x1b[2J\x1b[H"}
CLEAR_SEQ = CLEAR_SEQS.get(os.environ.get("DLPY_CLEAR", "3").strip(), CLEAR_SEQS["3"])


def early_clear():
    """Lo primero al abrir, borrar la consola (sin banner: ese sale tras clear_screen en main()),
    para no dejar a la vista el comando de lanzamiento ni restos anteriores mientras el script arranca.
    Solo en terminal interactivo; no en debug ni en las opciones que imprimen un informe."""
    try:
        if os.environ.get("DLPY_EARLYCLEAR", "1").strip().lower() in ("0", "no", "false", ""):
            return False
        if DEBUG or not (ANSI_OK and sys.stdout.isatty()):
            return False
        if any(a.lstrip("-\u2013\u2014").lower().split("=")[0] in ("selftest", "sistema", "perfil", "2shortcuts",
                                                                      "2shorcuts", "scm", "scb")
               for a in sys.argv[1:]):
            return False
        sys.stdout.write(CLEAR_SEQ)
        sys.stdout.flush()
        return True
    except Exception:
        return False


early_clear()

# ── [A5b] Estilo «Aurora» (el mismo de dlpy_test_panel.py) ──
# DLPY_TRUECOLOR=0: colores básicos · DLPY_ANIM=0: sin animación · DLPY_CLASSIC=1: barra «█░»
def _flag_env(name, default=True):
    v = os.environ.get(name)
    return default if v is None else v.strip().lower() not in ("0", "no", "false", "")


def _env_num(name, default, minimum=0.0):
    """Número de una variable de entorno. Si falta, no es un número finito («inf», «nan») o es menor que
    `minimum`, vale `default`: una variable mal escrita nunca debe impedir que el script arranque."""
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return default
    try:
        v = float(raw)
    except ValueError:
        return default
    return v if math.isfinite(v) and v >= minimum else default


TRUECOLOR = USE_COLOR and _flag_env("DLPY_TRUECOLOR", True)
ANIM = sys.stdout.isatty() and not DEBUG and _flag_env("DLPY_ANIM", True)
CLASSIC = _flag_env("DLPY_CLASSIC", False)
FILL, TIP, EMPTY = ("█", "", "░") if CLASSIC else ("━", "╸", "╌")
BAR_FILL, BAR_EMPTY = FILL, EMPTY

# nombre: (rgb, color básico de respaldo)
PALETTE = {"orange": ((255, 138, 61), "93"), "magenta": ((255, 61, 139), "95"),
           "mint": ((61, 220, 151), "92"), "amber": ((255, 196, 61), "93"),
           "gray": ((130, 130, 144), "2"), "track": ((58, 58, 70), "90"),
           "white": ((235, 235, 240), "0"), "red": ((255, 85, 102), "91")}
# nombres antiguos → paleta Aurora (así todo el script queda uniforme)
_ALIAS = {"green": "mint", "yellow": "amber", "blue": "orange", "cyan": "orange", "dim": "gray"}
FLAG_COLORS = {"apple": "mint", "orig": "amber", "default": "orange", "best": "magenta"}
FLAG_MARKS = {"apple": "✓", "orig": "◆", "default": "▸", "best": "★"}
FLAG_TEXT = {"apple": f"compatible {PLAT_LABEL}", "orig": "pista original", "default": "predeterminada",
             "best": "recomendada"}
ANIM_LIVE = ANIM and ANSI_OK        # animaciones que redibujan en su sitio


def paint(text, color, bold=None):
    """Pinta `text` con un color de la paleta. «bold» solo = negrita en blanco."""
    if not USE_COLOR or not text:
        return text
    if color == "bold":
        color, bold = "white", True
    rgb, basic = PALETTE[_ALIAS.get(color, color)]
    code = f"38;2;{rgb[0]};{rgb[1]};{rgb[2]}" if TRUECOLOR else basic
    return f"\x1b[{'1;' if bold else ''}{code}m{text}\x1b[0m"


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t + 0.5) for i in range(3))


def grad(text, a=0.0, b=1.0, phase=0.0):
    """Degradado naranja → magenta; con phase el color fluye (onda triangular)."""
    if not text or not USE_COLOR:
        return text
    n = len(text)
    if not TRUECOLOR:
        h = n // 2
        return paint(text[:h], "orange") + paint(text[h:], "magenta")
    out = []
    for i, ch in enumerate(text):
        u = a + (b - a) * (i / (n - 1) if n > 1 else 0.0)
        if phase:
            x = (u + phase) % 1.0
            u = 1 - abs(2 * x - 1)
        r, g, bl = mix(PALETTE["orange"][0], PALETTE["magenta"][0], u)
        out.append(f"\x1b[38;2;{r};{g};{bl}m{ch}")
    return "".join(out) + "\x1b[0m"


def dot(color):
    return paint("●", color)


def flag_mark(k):
    return paint(FLAG_MARKS[k], FLAG_COLORS[k])


_NUM_UNIT_RE = re.compile(r"^(\d+(?:\.\d+)?)(\s*)([A-Za-z]+)$")


def count_text(text, frac):
    """«89 MB» al 40 % → «36 MB»: escala el número y conserva decimales y unidad.
    Si el texto no es «número unidad» lo devuelve igual."""
    m = _NUM_UNIT_RE.match(str(text).strip())
    if not m:
        return text
    num, sp, unit = m.groups()
    dec = len(num.split(".")[1]) if "." in num else 0
    return f"{float(num) * max(0.0, min(1.0, frac)):.{dec}f}{sp}{unit}"


# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ ÁREA B · TERMINAL Y PANTALLA — ancho, mensajes, humor, banner, barras, teclado   ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝
# ───────────────────── [B1] Terminal: ancho y texto ─────────────────────
def rl_safe(prompt):
    """Si readline está activo, marca los códigos ANSI como no imprimibles (el cursor no se desfasa)."""
    if "readline" in sys.modules and "\x1b" in prompt:
        return _ANSI_RE.sub(lambda m: "\x01" + m.group(0) + "\x02", prompt)
    return prompt


def pstyle(prompt):
    """Prompts: la flecha «▸» siempre en naranja."""
    return prompt.replace("▸", paint("▸", "orange", True)) if "\x1b" not in prompt else prompt


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


def fit_text(text, width, ellipsis="…"):
    """Recorta texto plano a `width` columnas con «…» (nunca lo parte sin avisar)."""
    text = str(text)
    if dwidth(text) <= width:
        return text
    out, n = "", 0
    for ch in text:
        w = dwidth(ch)
        if n + w > width - 1:
            break
        out, n = out + ch, n + w
    return out + ellipsis


def wrap_text(text, width):
    """Ajuste de línea por palabras: corta solo en espacios (no en guiones), mide columnas
    reales y únicamente parte una palabra si ella sola no cabe. Devuelve una lista."""
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
    return lines or [""]


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
    """Mide el ancho REAL del terminal preguntándoselo: cursor al extremo derecho y
    «posición del cursor». APAGADA por defecto (cambia el modo del terminal y congelaba
    a-Shell); solo con DLPY_PROBE=1. Devuelve columnas o None;
    si no responde no se vuelve a intentar. refresh=True repite solo si ya funcionó."""
    flag = os.environ.get("DLPY_PROBE", "").strip()
    if os.name == "nt" or flag != "1":        # solo con DLPY_PROBE=1
        return None
    if _PROBE["tried"] and (_PROBE["cols"] is None or not refresh):
        return _PROBE["cols"]
    try:
        if not (sys.stdin.isatty() and sys.stdout.isatty()):
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


def _cols():
    """(columnas, medidas): medida con probe_cols o, si no, la que informa el entorno."""
    c = _PROBE["cols"]
    if c is None and not _PROBE["tried"] and ACTIVE_BAR is None:
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
        return max(20, int(os.environ.get("DLPY_WIDTH", "").strip()))
    except ValueError:
        return None


def _ioctl_cols():
    """Columnas según el propio terminal (ioctl TIOCGWINSZ), sin tocar su modo ni COLUMNS.
    None si no responde o el valor no es creíble."""
    for stream in (sys.stdout, sys.stderr, sys.stdin):
        try:
            c = os.get_terminal_size(stream.fileno()).columns
        except (OSError, ValueError, AttributeError):
            continue
        if 30 <= c <= 120:
            return c
    return None


def term_width():
    """Ancho para el texto: columnas - 1 (la última no se usa para que el terminal no
    salte de línea solo). Sin medición fiable se limita a 40;
    DLPY_WIDTH=N lo fuerza."""
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
    """Ancho de las líneas de una sola pieza (banner, separadores, barras): el mismo que
    usa el texto, con tope de 80 para que no se estiren en pantallas grandes."""
    forced = _forced_width()
    return forced if forced else max(20, min(term_width(), 80))


def nowrap(text):
    """Apaga el salto automático de línea mientras se escribe `text`."""
    return "\x1b[?7l" + text + "\x1b[?7h" if sys.stdout.isatty() and ANSI_OK else text


ACTIVE_BAR = None


_LAST_PULSE = [0.0]


# ───────────────────── [B2] Mensajes y debug ─────────────────────
def _pulse_line(color, text, mark=None):
    """El punto del aviso late dos veces (0.3 s) y luego queda fijo. Una ráfaga de avisos
    seguidos no se retrasa: solo late el primero de cada segundo."""
    now = time.time()
    if now - _LAST_PULSE[0] < 1.0:
        return
    _LAST_PULSE[0] = now
    sym = mark or "●"
    for i in range(4):
        sys.stdout.write(CLR + nowrap(paint(sym, color if i % 2 == 0 else "track") + " " + text))
        sys.stdout.flush()
        time.sleep(0.08)
    sys.stdout.write(CLR)


def _say(color, msg, mark=None, pulse=False):
    lines = wrap_text(msg, term_width() - 2)
    b = ACTIVE_BAR
    if b is not None and b.th:
        with b.lock:                      # borra la barra, imprime y deja que se redibuje
            b._erase()
            _say_lines(color, lines, mark)
    else:
        if pulse and ANIM_LIVE and USE_COLOR and len(lines) == 1:
            _pulse_line(color, lines[0], mark)
        _say_lines(color, lines, mark)


def _say_lines(color, lines, mark=None):
    print((paint(mark, color) if mark else dot(color)) + " " + lines[0])
    for ln in lines[1:]:
        print("  " + ln)


def m_ok(msg):
    _say("mint", msg, "✓")


def m_check(msg):
    """Línea de revisión superada: «✓ nombre versión · estado» (verde)."""
    _say("mint", msg, "✓")


def m_warn(msg):
    _say("amber", msg, "!", pulse=True)


def m_info(msg):
    _say("orange", msg)


def m_err(msg):
    _say("red", msg, "✕", pulse=True)


def note(text):
    """Texto de apoyo en gris, sangrado 2 columnas (como los subtítulos de dpt)."""
    for ln in wrap_text(text, term_width() - 2):
        print("  " + paint(ln, "gray"))


def hint(text):
    """Ayuda de un prompt: «▸ texto» (flecha naranja, texto gris). Lo que va entre llaves, como
    «{Enter = original}», sale resaltado en naranja y negrita: es lo que vale con Enter o al acabar
    la cuenta."""
    lines = wrap_text(text, term_width() - 2)
    on, out = False, []
    for ln in lines:
        seg = []
        for part in re.split(r"([{}])", ln):
            if part == "{":
                on = True
            elif part == "}":
                on = False
            elif part:
                seg.append(paint(part, "orange", True) if on else paint(part, "gray"))
        out.append("".join(seg))
    print(paint("▸", "orange") + " " + out[0])
    for ln in out[1:]:
        print("  " + ln)


def dbg(label, data=None):
    """Línea de depuración en bruto. No hace nada si DEBUG está apagado."""
    if not DEBUG:
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
    print(paint(f"[debug] {label}: {text}", "gray"))
    sys.stdout.flush()


def ignore(donde, err):
    """Anota en modo debug un error que se ignora a propósito (sin debug no hace nada)."""
    dbg(f"{donde}: ignorado", repr(err))


def pick(d, keys):
    """Subconjunto de un diccionario (para no volcar info enorme)."""
    d = d or {}
    return {k: d[k] for k in keys if k in d and d[k] is not None}


FMT_KEYS = ("format_id", "ext", "vcodec", "acodec", "height", "width", "fps", "tbr",
            "vbr", "abr", "filesize", "filesize_approx", "language", "format_note",
            "protocol", "container", "dynamic_range")
EV_KEYS = ("status", "postprocessor", "filename", "tmpfilename", "downloaded_bytes",
           "total_bytes", "total_bytes_estimate", "elapsed", "fragment_index",
           "fragment_count")


# ─────────── [B3] Comentarios inteligentes (humor según el uso) ───────────
# DLPY_ROAST=0 los apaga. Nunca interrumpen ni rompen una descarga.
ROAST = os.environ.get("DLPY_ROAST", "1").strip().lower() not in ("0", "no", "false")
PINNED = []              # comentarios que se repintan tras limpiar la pantalla
SESSION = {"adult": False}
DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

ADULT_HINTS = ("pornhub", "xvideos", "xnxx", "xhamster", "redtube", "youporn", "spankbang",
               "eporner", "tube8", "tnaflix", "beeg", "motherless", "chaturbate", "stripchat",
               "onlyfans", "fansly", "rule34", "hentai", "brazzers", "thisvid", "xtube",
               "cam4", "bongacams", "porn", "xxx")

ADULT_JOKES = [
    "Diviértete 🫣 Yo miro hacia otro lado. Mentira, ya vi todo.",
    "Modo incógnito no incluido. El historial de tu conciencia, tampoco.",
    "Descargando 'documentales'. Ajá. Muy educativo todo.",
    "Pasa. Esto queda entre tú, yo y tu iPhone.",
    "No juzgo. Bueno sí, pero con cariño y en silencio.",
    "Investigación académica, claramente. Cita tus fuentes.",
]
ADULT_LATE = [
    "Son las {h} y en un sitio adulto. No pregunto, pero lo anoto.",
    "{h}: Hora oficial de las decisiones cuestionables. Adelante.",
]
AGE_JOKES = [
    "Contenido +18 detectado. Seguro es por 'la trama'.",
    "Ese video exige ser mayor de edad. Tú verás qué tan mayor te sientes.",
]
SITE_JOKES = [
    (("youtube.com", "youtu.be"), [
        "YouTube. Qué original. Bajas lo que ya puedes ver gratis, pero así es el amor.",
        "Otro video de YouTube que 'vas a ver después'. Spoiler: no.",
    ]),
    (("tiktok.com",), [
        "TikTok: 15 segundos de contenido, 3 horas de tu vida.",
        "Descargando TikToks. Tu atención ya se despidió.",
    ]),
    (("twitter.com", "x.com", "t.co"), [
        "X/Twitter: descargando un video para discutir con un desconocido. Clásico.",
        "Un video de X. Seguro hay una pelea en los comentarios. Ve preparando palomitas.",
    ]),
    (("instagram.com", "facebook.com", "fb.watch"), [
        "Seguro te lo mandó tu tía.",
        "Un reel. Tu cerebro: 'solo uno más'. Mentira.",
    ]),
    (("twitch.tv",), [
        "Un VOD de Twitch. Qué optimismo creer que lo vas a ver completo.",
    ]),
    (("vimeo.com",), [
        "Vimeo. Hipster, pero respeto.",
    ]),
    (("reddit.com", "redd.it"), [
        "Ese video tiene 4 votos y 300 comentarios peleando. Ahí vas.",
    ]),
    (("soundcloud.com", "bandcamp.com"), [
        "Música descargada: piratería con estilo y buen gusto.",
    ]),
    (("dailymotion.com", "bilibili.com"), [
        "Sitio raro, gusto raro. Me gusta.",
    ]),
]
HOUR_JOKES = [
    (0, 5, [
        "Son las {h} y tú aquí descargando. Tu almohada ya presentó una denuncia.",
        "{h}: deberías dormir, pero claro, el video no se va a descargar solo.",
        "{h}: la hora en que se toman las peores decisiones y se guardan los mejores videos.",
        "Son las {h}. Mañana serás un zombi con excusas.",
    ]),
    (5, 7, [
        "{h}: ¿Madrugaste o nunca te dormiste? No me contestes.",
        "{h} y ya pidiendo videos. Ni el gallo te sigue el ritmo.",
    ]),
    (7, 12, [
        "{h}: Qué prioridades tan sólidas tienes para empezar el día.",
        "Mañana, {h}. Ese café necesita refuerzos si esto es lo primero que haces.",
    ]),
    (12, 15, [
        "{h}: hora de comer y tú descargando. Alimento para el alma, vacío para el estómago.",
        "Son las {h}. Tu estómago y yo te estamos mirando feo.",
    ]),
    (15, 19, [
        "{h}: La tarde perfecta para procrastinar con estilo.",
        "{h}: Seguro tenías pendientes. Yo no digo nada.",
    ]),
    (19, 24, [
        "{h}: Ya es tarde para ser productivo, pero justo a tiempo para esto.",
        "Son las {h}. Noche de maratón, supongo. Sin juzgar.",
    ]),
]
LIVE_JOKES = ["Es un directo. Descargar algo que no termina nunca: qué ambición."]
LONG_JOKES = [
    "{d} de video. Tienes vida, ¿verdad? … ¿verdad?",
    "{d}. Ni tu paciencia ni tu batería están preparadas para esto.",
]
SHORT_JOKES = [
    "{d} de video. Pensaste más tiempo que lo que dura.",
    "{d}. Hasta el anuncio previo dura más.",
]
AGAIN_JOKES = [
    "Ya lo tenías descargado. Memoria de pez, ¿eh?",
    "Este video ya vive en tu iPhone. Pero claro, repetir es de campeones.",
]
BIG_JOKES = [
    "{s}. Tu iPhone acaba de redactar su testamento.",
    "{s} de pura ambición. Tu almacenamiento ya está buscando abogado.",
]
K4_JOKES = ["4K en una pantalla de 6 pulgadas. Tus ojos no lo notarán; tu almacenamiento, sí."]
LOWRES_JOKES = [
    "Calidad bajísima. ¿Nostalgia del 2009 o fe ciega en tu imaginación?",
    "Eso se va a ver como un cuadro impresionista. Pero tú sabrás.",
]
AUDIO_JOKES = ["Solo audio. Ninguna cámara fue dañada en este proceso."]
DONE_JOKES = [
    "Listo. Ahora no lo verás nunca, igual que los otros {n}.",
    "Descargado. Se une a su nueva familia de {n} videos olvidados.",
    "Listo. Otro video que 'verás después'. Spoiler: no.",
    "Misión cumplida. Ahora a ignorarlo con elegancia.",
    "Hecho. Tu almacenamiento llora, pero en silencio.",
]
ADULT_DONE = [
    "Listo. Lo que pasa en a-Shell se queda en a-Shell 🤐",
    "Descarga lista. Recuerda: el volumen existe, los vecinos también.",
]
REUSE_JOKES = [
    "Entregado de nuevo. Tu espacio en disco te lo agradece; tu dignidad, no tanto.",
    "Reciclado con éxito. Tu memoria de pez agradece la ayuda.",
]
GENERIC_JOKES = [
    "No juzgo. Bueno sí, pero en silencio.",
    "Un día voy a cobrar comisión por cada video que descargas.",
    "Si descargar videos fuera un deporte, ya tendrías medalla.",
]
CANCEL_JOKES = [
    "Te arrepentiste. Pasa en las mejores familias.",
    "Cancelado. Hasta el video se sintió aliviado.",
    "Ctrl+C: el arte de rendirse a tiempo.",
]
STORAGE_JOKES = [
    "Tu almacenamiento grita ayuda. Tú: 'después'.",
    "Coleccionista de videos que nunca verás: aquí está tu factura.",
    "El iPhone pide piedad. Tú, más videos.",
]


def _clock():
    t = time.localtime()
    return f"{t.tm_hour % 12 or 12}:{t.tm_min:02d} {'a. m.' if t.tm_hour < 12 else 'p. m.'}", t


def _host(link):
    try:
        s = str(link).strip()
        return (urllib.parse.urlparse(s if "//" in s else "//" + s).hostname or "").lower()
    except (ValueError, AttributeError) as _ign:
        ignore("_host", _ign)
        return ""


def _host_is(host, domains):
    return any(host == d or host.endswith("." + d) for d in domains)


def is_adult(host, extractor=""):
    s = host + " " + str(extractor or "").lower()
    return any(h in s for h in ADULT_HINTS)


def _dur_text(sec):
    sec = int(sec)
    if sec >= 3600:
        return f"{sec // 3600} h {sec % 3600 // 60} min"
    if sec >= 60:
        return f"{sec // 60} min {sec % 60} s"
    return f"{sec} s"


def roast_say(text, pin=True):
    """Imprime un comentario (y opcionalmente lo fija para repintarlo tras limpiar)."""
    if not ROAST or not text:
        return
    try:
        _say("magenta", text)
        if pin:
            PINNED.append(text)
            del PINNED[:-4]
    except Exception as _ign:
        ignore("roast_say", _ign)


def show_pinned():
    if not ROAST:
        return
    for t in PINNED:
        try:
            _say("magenta", t)
        except Exception as _ign:
            ignore("show_pinned", _ign)


def blink_alert(text, times=5, delay=0.5):
    """Aviso rojo con el mismo punto parpadeante que las barras (● / vacío cada 0.5 s).
    Si el texto ocupa más de una línea no se anima (solo se imprime)."""
    if not ROAST:
        return
    try:
        lines = wrap_text(text, term_width() - 2)
        if len(lines) == 1 and sys.stdout.isatty() and USE_COLOR:
            for i in range(times):
                mark = dot("red") if i % 2 == 0 else " "
                sys.stdout.write(CLR + nowrap(mark + " " + paint(lines[0], "red")))
                sys.stdout.flush()
                time.sleep(delay)
            sys.stdout.write(CLR)
        _say_lines("red", [paint(ln, "red") for ln in lines])
        PINNED.append(text)
        del PINNED[:-4]
    except BaseException as _ign:
        ignore("blink_alert", _ign)


def hour_joke():
    txt, t = _clock()
    pool = next((p for a, b, p in HOUR_JOKES if a <= t.tm_hour < b), [])
    extra = []
    md = (t.tm_mon, t.tm_mday)
    if md == (12, 31):
        extra += ["31 de diciembre y descargando videos. Feliz año nuevo, crack 🥂"]
    if md == (1, 1):
        extra += ["Primero de enero y ya procrastinando. Vas con todo."]
    if md == (2, 14):
        extra += ["14 de febrero y aquí contigo, descargando. Qué romántico."]
    if md == (12, 25):
        extra += ["Navidad y tú con el teléfono. Tu familia lo está notando."]
    if t.tm_wday == 0 and 6 <= t.tm_hour < 13:
        extra += [f"Lunes, {txt}: ¿No deberías estar trabajando? Yo no vi nada."]
    if t.tm_wday in (4, 5) and t.tm_hour >= 21:
        extra += [f"{DAYS[t.tm_wday]} por la noche, {txt}: Planazo, todo un galán."]
    if t.tm_wday == 6 and t.tm_hour >= 18:
        extra += ["Domingo por la noche. Negando que mañana es lunes, ¿verdad?"]
    pool = list(pool) + extra * 2          # los días especiales pesan más
    return random.choice(pool).format(h=txt) if pool else ""


def roast_link(link):
    """Al pegar/recibir el enlace: hora y sitio."""
    if not ROAST:
        return
    try:
        host = _host(link)
        if is_adult(host):
            SESSION["adult"] = True
            txt, t = _clock()
            blink_alert("⚠ SITIO ADULTO DETECTADO ⚠")
            pool = ADULT_JOKES + (ADULT_LATE * 2 if t.tm_hour < 6 else [])
            roast_say(random.choice(pool).format(h=txt))
            return
        roast_say(hour_joke())
        for doms, pool in SITE_JOKES:
            if _host_is(host, doms):
                roast_say(random.choice(pool))
                break
    except Exception as _ign:
        ignore("roast_link", _ign)


def roast_info(info, link, old_file):
    """Tras analizar el video: contenido +18, duración, repetido."""
    if not ROAST:
        return
    try:
        host = _host(link)
        ext = info.get("extractor_key") or info.get("extractor") or ""
        picks = []
        if not SESSION["adult"] and is_adult(host, ext):
            SESSION["adult"] = True
            blink_alert("⚠ SITIO ADULTO DETECTADO ⚠")
            picks.append(random.choice(ADULT_JOKES).format(h=_clock()[0]))
        elif not SESSION["adult"] and (info.get("age_limit") or 0) >= 18:
            picks.append(random.choice(AGE_JOKES))
        dur = info.get("duration")
        if info.get("is_live"):
            picks.append(random.choice(LIVE_JOKES))
        elif dur and dur >= 3 * 3600:
            picks.append(random.choice(LONG_JOKES).format(d=_dur_text(dur)))
        elif dur and dur <= 15:
            picks.append(random.choice(SHORT_JOKES).format(d=_dur_text(dur)))
        if old_file:
            picks.append(random.choice(AGAIN_JOKES))
        for p in picks[:2]:
            roast_say(p)
    except Exception as _ign:
        ignore("roast_info", _ign)


def roast_choice(kind, fmt):
    """Tras elegir formato: tamaño, resolución, solo audio."""
    if not ROAST:
        return
    try:
        size = fmt.get("filesize") or fmt.get("filesize_approx") or 0
        h = fmt.get("height") or 0
        if size >= 2 * 1024 ** 3:
            roast_say(random.choice(BIG_JOKES).format(s=human_size(size)))
        elif kind == "v" and h >= 2160:
            roast_say(random.choice(K4_JOKES))
        elif kind == "v" and 0 < h <= 360:
            roast_say(random.choice(LOWRES_JOKES))
        elif kind == "a":
            roast_say(random.choice(AUDIO_JOKES))
    except Exception as _ign:
        ignore("roast_choice", _ign)


def roast_done(others, reused=False):
    """Al terminar (o al entregar uno ya descargado)."""
    if not ROAST:
        return
    try:
        if reused:
            pool = list(REUSE_JOKES)
        elif SESSION["adult"]:
            pool = list(ADULT_DONE)
        else:
            pool = [p for p in DONE_JOKES if "{n}" not in p or others >= 2]
            pool += GENERIC_JOKES
        print()
        roast_say(random.choice(pool).format(n=max(0, others)), pin=False)
    except Exception as _ign:
        ignore("roast_done", _ign)


def roast_cancel():
    roast_say(random.choice(CANCEL_JOKES), pin=False)


# ───────────────────── [B4] Pantalla: banner, títulos y listas ─────────────────────
def rule(title=None, w=None):
    """Línea de degradado a todo el ancho; con título: «━━ TÍTULO ━━━━…»."""
    w = w or safe_width()
    if not title:
        return grad(FILL * w)
    t = f" {fit_text(title, max(1, w - 6))} "
    return (grad(FILL * 2, 0, 0.12) + paint(t, "white", True)
            + grad(FILL * max(0, w - 2 - dwidth(t)), 0.12, 1))


def title_bar(left, right):
    """Cabecera «▍izquierda … derecha» a todo el ancho seguro."""
    w = safe_width()
    gap = max(1, w - 1 - dwidth(left) - dwidth(right))
    return paint("▍", "orange") + paint(left, "white", True) + " " * gap + right


def _fg(c):
    return f"\x1b[38;2;{c[0]};{c[1]};{c[2]}m"


def _bg(c):
    return f"\x1b[48;2;{c[0]};{c[1]};{c[2]}m"


def tri(x):
    """Onda triangular 0→1→0: el degradado va y vuelve sin saltos (como grad con phase)."""
    return 1 - abs(2 * (x % 1.0) - 1)


def smooth(x):
    """Entrada y salida suaves (0→1)."""
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def disk_fraction():
    """Fracción usada del almacenamiento del equipo (0–1) o None si no se puede leer.
    Se mide en «/» (en a-Shell da los valores reales del iPhone; las rutas de dentro del contenedor
    de la app daban otros) y se usa el «usado» que informa el sistema. Si «/» falla, las demás."""
    for path in ("/", FILES_DIR, HOME, os.getcwd()):
        try:
            u = shutil.disk_usage(path)
            if u.total > 0:
                return max(0.0, min(1.0, u.used / u.total))
        except (OSError, ValueError, NameError):
            continue
    return None


BEAT_ON = _flag_env("DLPY_BEAT", True)
BEAT_WARN, BEAT_CRIT_PHONE, BEAT_CRIT_MINE = 0.80, 0.92, 1.0     # umbrales del latido
BEAT_PERIOD = {"warn": 1.2, "crit": 0.7}                         # segundos por latido
BEAT_RGB = {"warn": PALETTE["amber"][0], "crit": PALETTE["red"][0]}


def scale_state(frac, kind):
    """«ok» / «warn» / «crit» de una escala de la barra. kind: «phone» (equipo) o «mine» (DLpy)."""
    if frac is None:
        return "ok"
    crit = BEAT_CRIT_PHONE if kind == "phone" else BEAT_CRIT_MINE
    return "crit" if frac >= crit else ("warn" if frac >= BEAT_WARN else "ok")


def beat_env(t, state):
    """Doble pulso «lub-dub» 0→1: dos picos por periodo (el segundo, más flojo)."""
    period = BEAT_PERIOD.get(state)
    if not period or t is None:
        return 0.0
    p = (t % period) / period
    return max(math.exp(-((p - 0.10) / 0.07) ** 2), 0.65 * math.exp(-((p - 0.30) / 0.07) ** 2))


def hot_rgb(state, t=None):
    """Color de una escala en alerta: apagado entre latidos, brillante en el pulso. Con t=None
    (o sin animación) color fijo."""
    base = BEAT_RGB[state]
    if t is None or not (BEAT_ON and ANIM_LIVE):
        return base
    return mix(mix(base, (30, 30, 36), 0.35), mix(base, (255, 255, 255), 0.45), beat_env(t, state))


def tint_text(text, state, t=None):
    """Etiqueta de una escala: gris si todo va bien; ámbar/rojo (con latido) si se llena."""
    if state == "ok" or not text:
        return paint(text, "gray")
    if not USE_COLOR:
        return text
    if TRUECOLOR:
        return _fg(hot_rgb(state, t)) + text + "\x1b[0m"
    return paint(text, "red" if state == "crit" else "amber")


def card_bar(n, phone, mine, t=None):
    """Una línea con dos escalas: «▀» arriba = equipo (texto), abajo = DLpy (fondo).
    Cada escala que pasa del 80 % se tiñe de ámbar o rojo y late (con t)."""
    o, m, trk, gray = (PALETTE[k][0] for k in ("orange", "magenta", "track", "gray"))
    sp, sm = scale_state(phone, "phone"), scale_state(mine, "mine")
    if not TRUECOLOR:
        k = int(n * min(1.0, mine) + 0.5)
        fill = grad(FILL * k) if sm == "ok" else paint(FILL * k, "red" if sm == "crit" else "amber")
        return fill + paint(EMPTY * (n - k), "track")
    hp = hot_rgb(sp, t) if sp != "ok" else None
    hm = hot_rgb(sm, t) if sm != "ok" else None
    out = ""
    for i in range(n):
        pos = (i + 0.5) / n
        top = (hp or gray) if phone is not None and pos <= phone else trk
        bot = (hm or mix(o, m, min(1.0, pos / mine))) if mine > 0 and pos <= mine else trk
        out += _fg(top) + _bg(bot) + "▀"
    return out + "\x1b[0m"


def bar_row(t=None):
    """La fila de la barra con sus etiquetas, para el instante t (None = fija)."""
    b = CARD["bar"]
    return ("  " + tint_text(b["left"], scale_state(b["phone"], "phone"), t)
            + card_bar(b["n"], b["phone"], b["mine"], t)
            + tint_text(b["right"], scale_state(b["mine"], "mine"), t))


def card_rows(inner):
    """Filas del interior de la tarjeta, cada una de `inner` columnas exactas."""
    state = (paint("DEBUG ACTIVO", "amber", True) if DEBUG else paint("debug off", "gray"))
    try:
        r = storage_report()
        _head, detail, over = storage_lines()
        mine = r["total"] / CLEAN_LIMIT if CLEAN_LIMIT > 0 else 0.0
    except Exception:
        detail, over, mine = [], False, 0.0
    phone = disk_fraction()
    left_t = paint("▍", "orange") + paint(f"DLpy v{VERSION}", "white", True)
    gap = max(1, inner - dwidth(left_t) - dwidth(state))
    rows = [left_t + " " * gap + state]
    where = fit_text(f"  {platform_name()} · {machine_name()}", inner)
    rows.append(paint(where, "gray") + " " * max(0, inner - dwidth(where)))
    left = f"iPhone {phone * 100:.0f}% " if phone is not None else ""
    right = f" DLpy {mine * 100:.0f}%"
    n = inner - 2 - len(left) - len(right)
    if n < 6:                                   # sin sitio para etiquetas: solo la barra
        left, right, n = "", "", inner - 2
    CARD["bar"] = {"idx": len(rows), "n": n, "left": left, "right": right, "phone": phone, "mine": mine}
    rows.append(bar_row())
    if over:                                    # el desglose solo si se pasa del límite
        for ln in detail:
            t = fit_text("  " + ln, inner)
            rows.append(paint(t, "gray") + " " * max(0, inner - dwidth(t)))
    return rows


def card_lines(t=None, env=1.0, lap=None, cached=False, head=None):
    """Tarjeta redondeada. El borde lleva el degradado naranja→magenta→naranja y, encima, un
    destello que lo recorre entero. t = segundos (None = fija); env 1→0 apaga el destello.
    cached=True reutiliza el ancho y el contenido del último cálculo (sin recorrer archivos)."""
    if cached and CARD["body"] is not None:
        w, body = CARD["w"], CARD["body"]
    else:
        w = max(30, min(safe_width(), 60))
        body = card_rows(w - 4)
        CARD["w"], CARD["body"] = w, body
    if t is not None and CARD["bar"]:
        body = list(body)
        body[CARD["bar"]["idx"]] = bar_row(t)       # la barra late: se redibuja con la hora
    h = len(body)
    perim = 2 * w + 2 * h
    span = max(14.0, perim * 0.30)
    if head is None:
        head = (t / (lap or BANNER_LAP) * perim) if t is not None else 0.0
    o, m, trk, white = (PALETTE[k][0] for k in ("orange", "magenta", "track", "white"))

    def col(pos):
        if not USE_COLOR:
            return ""
        if not TRUECOLOR:
            return "\x1b[" + PALETTE["orange" if tri(pos / perim) < 0.5 else "magenta"][1] + "m"
        base = mix(o, m, tri(pos / perim))
        if t is None or env <= 0:
            return _fg(base)
        d = (pos - head + perim / 2) % perim - perim / 2
        lit = 0.5 * (1 + math.cos(2 * math.pi * d / span)) if abs(d) < span / 2 else 0.0
        lit *= env
        dim = mix(base, trk, 0.40 * env)
        return _fg(mix(dim, mix(base, white, 0.60), lit))

    rs = "\x1b[0m" if USE_COLOR else ""
    top = "".join(col(i) + ch for i, ch in enumerate("╭" + "─" * (w - 2) + "╮")) + rs
    bottom = "".join(col(w + h + (w - 1 - j)) + ch
                     for j, ch in enumerate("╰" + "─" * (w - 2) + "╯")) + rs
    out = [top]
    for k, r in enumerate(body):
        out.append(col(2 * w + h + (h - 1 - k)) + "│" + rs + " " + r + " " + col(w + k) + "│" + rs)
    out.append(bottom)
    return out


def card_inner():
    """Columnas útiles dentro de una tarjeta (el mismo ancho que el encabezado, menos el marco)."""
    return max(30, min(safe_width(), 60)) - 4


def card_text_rows(text, inner, color="gray", bold=False, mark=None, mark_color="mint"):
    """Texto de una tarjeta ajustado a `inner` columnas. La primera línea puede llevar un símbolo
    («✓ Listo»); las demás (y las que no lo llevan) van sangradas 2 columnas."""
    out = []
    for i, ln in enumerate(wrap_text(text, max(8, inner - 2))):
        lead = (paint(mark, mark_color) + " ") if (mark and i == 0) else "  "
        out.append(lead + paint(ln, color, bold))
    return out


def static_card(rows):
    """Tarjeta redondeada fija, con el mismo borde de degradado naranja→magenta→naranja que el encabezado
    (sin destello). `rows`: líneas ya pintadas de como mucho card_inner() columnas; se rellenan a la derecha."""
    w = max(30, min(safe_width(), 60))
    inner = w - 4
    body = [r + " " * max(0, inner - dwidth(r)) for r in rows]
    h = len(body)
    perim = 2 * w + 2 * h
    o, m = PALETTE["orange"][0], PALETTE["magenta"][0]

    def col(pos):
        if not USE_COLOR:
            return ""
        if not TRUECOLOR:
            return "\x1b[" + PALETTE["orange" if tri(pos / perim) < 0.5 else "magenta"][1] + "m"
        return _fg(mix(o, m, tri(pos / perim)))

    rs = "\x1b[0m" if USE_COLOR else ""
    top = "".join(col(i) + ch for i, ch in enumerate("╭" + "─" * (w - 2) + "╮")) + rs
    bottom = "".join(col(w + h + (w - 1 - j)) + ch for j, ch in enumerate("╰" + "─" * (w - 2) + "╯")) + rs
    out = [top]
    for k, r in enumerate(body):
        out.append(col(2 * w + h + (h - 1 - k)) + "│" + rs + " " + r + " " + col(w + k) + "│" + rs)
    out.append(bottom)
    return out


CODEC_NAMES = {"avc1": "H.264", "avc3": "H.264", "h264": "H.264", "hvc1": "HEVC", "hev1": "HEVC", "hevc": "HEVC",
               "dvh1": "Dolby Vision", "dvhe": "Dolby Vision", "vp9": "VP9", "vp09": "VP9", "av01": "AV1", "av1": "AV1",
               "mp4a": "AAC", "aac": "AAC", "opus": "Opus", "ec-3": "E-AC-3", "eac3": "E-AC-3", "ac-3": "AC-3",
               "ac3": "AC-3", "flac": "FLAC", "alac": "ALAC", "mp3": "MP3", "vorbis": "Vorbis"}


def codec_name(codec):
    """«avc1.640028» → «H.264»; lo que no se conoce sale en mayúsculas; sin dato → ''."""
    c = str(codec or "").lower().split(".")[0]
    return CODEC_NAMES.get(c) or (c.upper() if c and c != "?" else "")


def clock_text(sec):
    """«1:02:05» o «3:35»; '' sin duración."""
    try:
        sec = int(sec)
    except (TypeError, ValueError):
        return ""
    if sec <= 0:
        return ""
    h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def result_card_rows(title, meta, size, duration, name, inner):
    """Líneas (pintadas) de la tarjeta final: «✓ Listo», título, datos técnicos y archivo."""
    meta = meta if isinstance(meta, dict) else {}
    head = "Listo" + (" · convertido" if meta.get("converted") else "")
    rows = card_text_rows(head, inner, "white", True, "✓", "mint")
    if title:
        rows += ["  " + paint(ln, "white") for ln in title_lines(str(title), inner - 2)]
    video = meta.get("video") or {}
    track = (meta.get("tracks") or [{}])[0]
    if video:
        bits = [video.get("res"), codec_name(video.get("codec"))]
    else:
        abr = track.get("abr")
        bits = [" ".join(x for x in (codec_name(track.get("codec")) or "audio", f"{abr} kbps" if abr else "") if x)]
    bits += [human_size(size) if size else "", clock_text(duration)]
    bits = [str(b) for b in bits if b]
    while len(bits) > 2 and dwidth(" · ".join(bits)) > inner - 2:
        bits.pop()                                  # primero cae la duración, luego el tamaño
    if bits:
        rows.append("  " + paint(fit_text(" · ".join(bits), inner - 2), "gray"))
    base, ext = os.path.splitext(str(name or ""))
    if base:
        lead = "dlpy_files/"
        rows.append("  " + paint(lead + fit_text(base, max(1, inner - 2 - len(lead) - dwidth(ext))) + ext, "gray"))
    return rows


def result_card(final, title, meta, duration):
    """Tarjeta con el resultado de la descarga. Nunca revienta: si falla, queda el aviso de siempre."""
    try:
        try:
            size = os.path.getsize(final)
        except OSError:
            size = 0
        print()
        for ln in static_card(result_card_rows(title, meta, size, duration, os.path.basename(final), card_inner())):
            print(ln)
    except Exception as _ign:
        ignore("result_card", _ign)
        m_ok("Descarga lista")


BANNER_LAP = 2.5          # segundos que tarda el destello en dar la vuelta al borde al arrancar
CARD_LAP = 5.0            # ídem mientras se descarga
_BANNER_INTRO = [True]    # el destello de arranque solo se ve en el primer banner de la ejecución
# Estado de la tarjeta: w/body = último contenido calculado (se reutiliza en cada cuadro);
# fresh = la tarjeta acaba de pintarse arriba del todo; live = el panel de descarga la anima.
CARD = {"w": None, "body": None, "fresh": False, "live": False, "t0": 0.0}
# TEST: hilo propio de la tarjeta. DLPY_CARDLIVE=0 lo apaga (queda lo de antes).
CARD_THREAD = _flag_env("DLPY_CARDLIVE", True)
CARD.update({"bar": None, "run": False, "th": None, "head": 0.0, "row": 0, "rows": 24, "rows_t": 0.0, "settled": False,
             "pin": False, "pin_rows": 0})
CARD_PIN = _flag_env("DLPY_CARDPIN", True)      # ancla la tarjeta con una región de desplazamiento


def card_paint(t=None, env=1.0, lap=None, head=None):
    """Repinta la tarjeta en las filas 1 a 5 sin mover el cursor (guardar/restaurar)."""
    lines = card_lines(t, env, lap, cached=True, head=head)
    seq = "\x1b7" + "".join(f"\x1b[{i + 1};1H{ln}" for i, ln in enumerate(lines)) + "\x1b8"
    sys.stdout.write("\x1b[?7l" + seq + "\x1b[?7h")
    sys.stdout.flush()


class _RowCounter:
    """Envoltura de sys.stdout que solo cuenta: saltos de línea y subidas de cursor desde el último
    clear_screen, para saber en qué fila está el cursor y no pintar la tarjeta si se desplazó.
    Todo lo demás lo delega tal cual."""

    def __init__(self, inner):
        self._inner = inner

    def write(self, text):
        n = self._inner.write(text)
        try:
            _count_rows(text)
        except Exception as _ign:
            ignore("row_counter", _ign)
        return n

    def writelines(self, lines):
        for ln in lines:
            self.write(ln)

    def flush(self):
        return self._inner.flush()

    def __getattr__(self, name):
        return getattr(self._inner, name)


_UP_RE = re.compile(r"\x1b\[(\d*)A")


def _count_rows(text):
    if not isinstance(text, str) or not text:
        return
    cut = max((text.rfind(q) for q in set(CLEAR_SEQS.values())), default=-1)
    if cut >= 0:                               # pantalla borrada: el cursor vuelve arriba
        CARD["row"], text = 0, text[cut:]
    ups = sum(int(m or 1) for m in _UP_RE.findall(text))
    low = (len(CARD["body"]) + 2) if CARD["body"] and CARD["fresh"] else 0   # bajo la tarjeta siempre
    CARD["row"] = max(low, CARD["row"] + text.count("\n") - ups)
    now = time.time()
    if now - CARD["rows_t"] > 0.5 and threading.current_thread() is threading.main_thread():
        CARD["rows_t"] = now                   # el alto se mide en el hilo principal (a-Shell)
        try:
            CARD["rows"] = shutil.get_terminal_size((80, 24)).lines
        except (OSError, ValueError):
            pass


def _card_ok():
    """¿Sigue la tarjeta arriba del todo (la pantalla no se desplazó)? Margen de 5 filas por lo que
    se escribe sin pasar por sys.stdout (el eco de input, el prompt de readline)."""
    return bool(CARD["fresh"] and CARD["body"] is not None
                and (CARD["pin"] or CARD["row"] + 5 <= CARD["rows"]))


def _card_pin(rows, restore=False):
    """Ancla la tarjeta: región de desplazamiento de la fila h+1 a la última.
    DECSTBM manda el cursor al inicio, así que se coloca bajo la tarjeta (o se restaura)."""
    h = len(CARD["body"] or ()) + 2
    if not CARD_PIN or rows < h + 4:
        return False
    seq = f"\x1b[{h + 1};{rows}r"
    seq = "\x1b7" + seq + "\x1b8" if restore else seq + f"\x1b[{h + 1};1H"
    sys.stdout.write(seq)
    sys.stdout.flush()
    CARD["pin_rows"] = rows
    return True


def _card_unpin():
    """Libera la región de desplazamiento sin mover el cursor."""
    if CARD["pin"]:
        CARD["pin"] = False
        try:
            sys.stdout.write("\x1b7\x1b[r\x1b8")
            sys.stdout.flush()
        except Exception as _ign:
            ignore("card_unpin", _ign)


def _card_loop():
    last = time.time()
    shown = None                               # None = aún no, True = animada, False = fija
    while CARD["run"]:
        time.sleep(0.1)
        now = time.time()
        dt, last = now - last, now
        try:
            ok = _card_ok()
            bar = globals().get("ACTIVE_BAR")
            lock = getattr(bar, "lock", None) or threading.RLock()
            if CARD["pin"] and CARD["rows"] != CARD["pin_rows"]:      # cambió el alto del terminal
                with lock:
                    CARD["pin"] = _card_pin(CARD["rows"], restore=True)
            if ok:
                age = now - CARD["t0"]
                lap = BANNER_LAP if age < BANNER_LAP else CARD_LAP
                w, h = CARD["w"], len(CARD["body"]) + 2
                CARD["head"] = (CARD["head"] + dt * (2 * w + 2 * h) / lap) % (2 * w + 2 * h)
                with lock:
                    card_paint(age, 1.0, lap, head=CARD["head"])
                shown = True
            elif shown:                        # se acerca el desplazamiento: queda fija y se calla
                with lock:
                    if CARD["row"] >= len(CARD["body"]) + 2 and CARD["fresh"]:
                        card_paint()
                shown = False
        except Exception as _ign:
            ignore("card_loop", _ign)
            CARD["run"] = False


def card_thread_start():
    """Arranca (o reanuda con el contenido nuevo) el hilo que anima la tarjeta."""
    if not (CARD_THREAD and ANIM_LIVE and TRUECOLOR and USE_COLOR):
        return False
    if not isinstance(sys.stdout, _RowCounter):
        sys.stdout = _RowCounter(sys.stdout)
    CARD["settled"] = False
    if CARD["th"] is None or not CARD["th"].is_alive():
        CARD["run"], CARD["t0"], CARD["head"] = True, time.time(), 0.0
        CARD["th"] = threading.Thread(target=_card_loop, daemon=True)
        CARD["th"].start()
        atexit.register(card_thread_stop)
    return True


def card_thread_stop():
    """Al salir: para el hilo y deja la tarjeta fija."""
    if CARD["settled"]:
        return
    CARD["settled"] = True
    CARD["run"] = False
    th = CARD["th"]
    if th is not None and th.is_alive() and th is not threading.current_thread():
        th.join(timeout=0.5)
    try:
        ok = _card_ok()
        _card_unpin()
        if ok:
            card_paint()
    except Exception as _ign:
        ignore("card_thread_stop", _ign)


def card_arm():
    """Activa la animación de la tarjeta durante la descarga si es seguro."""
    if CARD["th"] is not None and CARD["run"]:
        return                                 # ya la anima el hilo propio
    if CARD["live"] or not (CARD["fresh"] and CARD["body"] is not None
                            and ANIM_LIVE and TRUECOLOR and USE_COLOR):
        return
    try:
        rows = shutil.get_terminal_size((80, 24)).lines
    except (OSError, ValueError):
        rows = 24
    if rows < len(card_lines(cached=True)) + 16:         # sin alto: la pantalla se desplazaría
        return
    CARD["live"], CARD["t0"] = True, time.time()


def card_tick():
    """Un cuadro de la tarjeta viva; ante cualquier error la deja fija."""
    if not CARD["live"]:
        return
    try:
        card_paint(time.time() - CARD["t0"], 1.0, CARD_LAP)
    except Exception as _ign:
        CARD["live"] = False
        ignore("card_tick", _ign)


def card_settle():
    """Termina la animación: el destello se apaga en medio segundo y la tarjeta queda fija."""
    if not CARD["live"]:
        return
    CARD["live"] = False
    try:
        t0 = time.time()
        base = t0 - CARD["t0"]
        while True:
            k = (time.time() - t0) / 0.5
            if k >= 1:
                break
            card_paint(base + (time.time() - t0), 1.0 - smooth(k), CARD_LAP)
            time.sleep(1.0 / 16)
        card_paint()
    except Exception as _ign:
        ignore("card_settle", _ign)


def banner_plain():
    """Banner de antes (terminales de menos de 30 columnas)."""
    state = (paint("DEBUG ACTIVO", "amber", True) if DEBUG
             else paint("debug off", "gray"))
    print(title_bar(f"DLpy v{VERSION}", state))
    where = f"{platform_name()} · {machine_name()}"
    try:
        head, detail, over = storage_lines()
    except Exception:
        head, detail, over = "Espacio: ?", [], False
    col = "amber" if over else "gray"
    room_w = safe_width() - 2
    for cand in (head, head.replace("Espacio: ", "")):
        room = room_w - dwidth(cand) - 3
        if dwidth(where) <= room:
            break
    if room >= 8:
        print("  " + paint(fit_text(where, room), "gray") + paint(" · ", "gray") + paint(cand, col))
    else:
        print("  " + paint(fit_text(cand, room_w), col))
    if over:
        for ln in detail:
            print("  " + paint(ln, "gray"))
    print(rule())


def banner():
    """Encabezado en tarjeta: título + versión + estado de debug, dónde corre y la barra de espacio
    (equipo / DLpy). Se pinta tras cada clear_screen (y al arrancar) para que quede visible.
    El primer banner de la ejecución da una vuelta de destello al borde."""
    CARD["live"], CARD["fresh"], CARD["pin"] = False, False, False
    if safe_width() < 30:
        banner_plain()
        return
    if CARD_THREAD and ANIM_LIVE and TRUECOLOR and USE_COLOR:
        # TEST: la tarjeta sale ya y la anima un hilo propio; el arranque no bloquea
        if not isinstance(sys.stdout, _RowCounter):
            sys.stdout = _RowCounter(sys.stdout)
        CARD["row"] = 0
        _BANNER_INTRO[0] = False
        for ln in card_lines():
            print(ln)
        CARD["fresh"] = True
        try:
            CARD["rows"] = shutil.get_terminal_size((80, 24)).lines
        except (OSError, ValueError):
            pass
        CARD["pin"] = _card_pin(CARD["rows"])
        if CARD["th"] is None or not CARD["th"].is_alive():
            card_thread_start()
        return
    first, _BANNER_INTRO[0] = _BANNER_INTRO[0], False
    if not (first and ANIM_LIVE and TRUECOLOR):
        lines = card_lines()
        for ln in lines:
            print(ln)
        CARD["fresh"] = True
        return
    card_lines()                                      # calcula el contenido una sola vez
    n, t0 = 0, time.time()
    try:
        sys.stdout.write("\x1b[?25l")
        while True:
            now = time.time() - t0
            if now >= BANNER_LAP:
                break
            lines = card_lines(now, smooth((BANNER_LAP - now) / (BANNER_LAP * 0.4)) if now > BANNER_LAP * 0.6 else 1.0,
                               cached=True)
            sys.stdout.write("\x1b[?7l" + (f"\x1b[{n}A" if n else "")
                             + "".join("\r" + ln + "\x1b[K\n" for ln in lines) + "\x1b[?7h")
            sys.stdout.flush()
            n = len(lines)
            time.sleep(1.0 / 16)
    except KeyboardInterrupt:
        pass
    finally:
        lines = card_lines(cached=True)
        sys.stdout.write((f"\x1b[{n}A" if n else "") + "".join("\r" + ln + "\x1b[K\n" for ln in lines)
                         + "\x1b[?25h")
        sys.stdout.flush()
        CARD["fresh"] = True


def clear_screen():
    """Borra la consola y deja solo el banner (+ comentarios fijados).
    En debug no borra: imprime un separador para conservar lo ya mostrado."""
    if DEBUG:
        print()
        print(paint(EMPTY * min(safe_width(), 40), "track"))
        banner()
        show_pinned()
        return
    if ANSI_OK:
        sys.stdout.write(CLEAR_SEQ)
        sys.stdout.flush()
    else:
        os.system("cls" if os.name == "nt" else "clear")
    probe_cols(refresh=True)              # por si se giró el teléfono o cambió el tamaño
    banner()
    show_pinned()


def title_lines(title, width):
    """Líneas del título: como mucho 2; si sobra texto la segunda acaba en «…»."""
    lines = wrap_text(title, width)
    if len(lines) > 2:
        lines = [lines[0], fit_text(" ".join(lines[1:]), max(8, width - 1))]
    return lines


def show_title(title, sub=None):
    """«▍Título» en negrita blanca (máximo 2 líneas) y, opcional, subtítulo gris."""
    lines = title_lines(title, term_width() - 1)
    print(paint("▍", "orange") + paint(lines[0], "white", True))
    for ln in lines[1:]:
        print(" " + paint(ln, "white", True))
    if sub:
        note(sub)


def header(title, gap=True):
    if gap:
        print()
    print(rule(title))


def kv(label, value, flag=None):
    w = term_width()
    lead = f"{label}: "
    extra = 2 if flag else 0
    lines = wrap_text(str(value), max(8, w - len(lead) - extra))
    if flag:
        lines[-1] += " " + flag_mark(flag)
    print(paint(lead, "gray") + lines[0])
    for ln in lines[1:]:
        print(" " * len(lead) + ln)


def legend(keys):
    """«✓ compatible iPhone   ◆ pista original» (marca de color + texto gris)."""
    print("\n".join("  " + ln for ln in _legend_lines(keys)))


def _legend_lines(keys):
    w = term_width() - 2
    lines, cur, curlen = [], [], 0
    for k in keys:
        plain = "x " + FLAG_TEXT[k]
        colored = flag_mark(k) + " " + paint(FLAG_TEXT[k], "gray")
        add = len(plain) + (3 if cur else 0)
        if cur and curlen + add > w:
            lines.append("   ".join(cur))
            cur, curlen, add = [], 0, len(plain)
        cur.append(colored)
        curlen += add
    if cur:
        lines.append("   ".join(cur))
    return lines


ROW_PLAIN = {}      # n.º → texto plano de la fila impresa (para el destello al elegir)


def flash_row(n):
    """Repite la fila elegida en blanco un instante antes de limpiar la pantalla."""
    txt = ROW_PLAIN.get(n)
    if not (ANIM_LIVE and txt):
        return
    sys.stdout.write(nowrap(paint(fit_text(txt, term_width()), "white", True)) + "\n")
    sys.stdout.flush()
    time.sleep(0.15)


def print_rows(rows, flags, head=None):
    """rows: [{"n": int, "flags": set, "cols": [str, ...]}].
    Estilo dpt: « n  col · col … tamaño   ✓ ◆ » con el número en naranja y las marcas a la
    derecha. Elige la variante más cómoda que quepa sin saltar de línea: tabla alineada
    (columnas separadas por 2 espacios, luego por 1), línea compacta «a · b», «a·b» y con
    «con/sin audio» abreviado. Solo si ninguna cabe se parte la línea por palabras.
    Con animación las filas entran una a una y el tamaño de la tabla «cuenta» hasta
    su valor; ninguna animación cambia el ancho ni el número de líneas."""
    if not rows:
        return
    w = term_width()
    nw = max(len(str(r["n"])) for r in rows)
    pw = 1 + nw + 2                                   # « n  »
    fw = max(1, 2 * len(flags) - 1)                   # ancho de la columna de marcas
    ncol = len(rows[0]["cols"])
    allr = [r["cols"] for r in rows] + ([head] if head else [])
    widths = [max(dwidth(c[i]) for c in allr) for i in range(ncol)]
    budget = min(0.07, 0.8 / len(rows))                # animación total ≈ 0.8 s como máximo

    def prefix(r):               # ★ («b») o ▸ (predeterminada) ocupan el margen: no restan ancho
        return (flag_mark("best") if "best" in r["flags"]
                else flag_mark("default") if "default" in r["flags"] else " ") \
            + paint(f"{r['n']:>{nw}}", "orange", True) + "  "

    def marks(r):
        return " ".join(flag_mark(k) if k in r["flags"] else " " for k in flags)

    def pad(c, i):
        return c + " " * (widths[i] - dwidth(c))

    def line(r, body_vis, body):
        gap = max(1, w - pw - body_vis - fw - 1)
        return prefix(r) + body + " " * gap + marks(r)

    def emit(r, render, count=False):
        lines, counted = render(None), False
        ROW_PLAIN[r["n"]] = _ANSI_RE.sub("", lines[0]).rstrip()
        last = r["cols"][-1] if r["cols"] else ""
        if (count and ANIM_LIVE and len(lines) == 1
                and _NUM_UNIT_RE.match(str(last).strip())):
            for fr in (0.3, 0.65):                   # el tamaño sube hasta su valor
                sys.stdout.write("\r" + nowrap(render(count_text(last, fr))[0]))
                sys.stdout.flush()
                time.sleep(budget * 0.35)
            sys.stdout.write("\r")
            counted = True
        for ln in lines:
            print(ln)
        if ANIM:
            sys.stdout.flush()
            time.sleep(budget * (0.3 if counted else 1.0))

    for sep in ("  ", " "):                       # tabla alineada
        if pw + sum(widths) + len(sep) * (ncol - 1) + 1 + fw + 1 <= w:
            if head:
                print(" " * pw + paint(sep.join(pad(h, i) for i, h in enumerate(head)).rstrip(), "gray"))
            for r in rows:
                def render(ov, r=r, sep=sep):
                    cols = r["cols"] if ov is None else r["cols"][:-1] + [ov]
                    body = sep.join((pad(c, i) if i == 0 else paint(pad(c, i), "gray"))
                                    for i, c in enumerate(cols))
                    return [line(r, sum(widths) + len(sep) * (ncol - 1), body)]
                emit(r, render, count=True)
            return

    short = {"con audio": "c/audio", "sin audio": "s/audio"}
    variants = ((" · ", False), ("·", False), ("·", True))
    room = max(8, w - pw - fw - 2)
    texts = None
    for sep, abbr in variants:                    # línea compacta
        cand = [sep.join((short.get(c, c) if abbr else c) for c in r["cols"] if c)
                for r in rows]
        texts = cand
        if all(dwidth(t) <= room for t in cand):
            break
    for r, text in zip(rows, texts):
        def render(ov, r=r, text=text):
            lines = wrap_text(text, room)
            first = lines[0].split(" · ", 1) if " · " in lines[0] else [lines[0]]
            body = first[0] + (paint(" · " + first[1], "gray") if len(first) > 1 else "")
            out = [line(r, dwidth(lines[0]), body)]
            for ln in lines[1:]:
                out.append(" " * pw + paint(ln, "gray"))
            return out
        emit(r, render)


NESTED_IOS = False        # a-Shell: esta ejecución la lanzó runpy dentro del proceso de otra versión


def drain_pending_input(max_wait=0.08):
    """Descarta bytes ya pendientes en stdin (Enter residual al abrir desde Atajos).
    No cambia el modo del terminal: solo lee lo que ya está en el buffer."""
    if NESTED_IOS:
        return                            # recién actualizada en el mismo proceso: no se lee stdin
    try:
        import select
        fd = sys.stdin.fileno()
        end = time.time() + max_wait
        while time.time() < end:
            ready, _, _ = select.select([fd], [], [], max(0.0, end - time.time()))
            if not ready:
                break
            data = os.read(fd, 4096)
            if not data:
                break
    except Exception as _ign:
        ignore("drain_pending_input", _ign)


def split_prompt(prompt):
    """Parte un prompt largo por palabras (el terminal lo cortaría a media palabra).
    Devuelve (líneas previas, última línea); la última deja ≥10 columnas para escribir."""
    prompt = str(prompt)
    w = term_width()
    if dwidth(prompt) <= w - 10 and "\n" not in prompt:
        return [], prompt
    lines = wrap_text(prompt.rstrip(), w - 10)
    last = lines[-1] + (" " if prompt.endswith(" ") else "")
    return lines[:-1], last


def ask_line(prompt, phantom=True, plain=None):
    """input() robusto ante Enter fantasma (Atajos / a-Shell).
    1) Drena el buffer de stdin para no consumir un Enter residual como respuesta.
    2) Si aun así llega vacío en < PHANTOM_SECS, vuelve a pedir una sola vez.
    No toca el modo del terminal (cambiarlo congelaba a-Shell)."""
    note_prompt(plain or prompt)
    input_unlock()                   # sale una pregunta: se habilita la entrada
    drain_pending_input()
    pre, prompt = split_prompt(pstyle(prompt))
    for ln in pre:
        print(ln)
    prompt = rl_safe(prompt)
    t0 = time.time()
    r = input(prompt)
    CARD["row"] += 1                 # el Enter del input() no pasa por sys.stdout
    if phantom and not r.strip() and (time.time() - t0 < PHANTOM_SECS or time.time() - START_T < PHANTOM_BOOT):
        # Segunda oportunidad: se borra la línea del Enter fantasma y el prompt vuelve a salir en el
        # mismo renglón. Sin terminal interactivo input() lo muestra en una línea nueva.
        erase_input_line(prompt, r)
        r = input(prompt)
        CARD["row"] += 1
    return r


PROMPT = "▸ "
INPLACE = sys.stdout.isatty() and ANSI_OK and not DEBUG     # ¿se puede borrar una línea ya escrita?


def erase_seq(prompt, typed, cols):
    """Secuencia que, justo tras el Enter de un input(), sube sobre la línea escrita (prompt + texto;
    si no cupo en una fila, sobre todas) y la borra, dejando el cursor al inicio. Pura: la prueba --selftest."""
    plain = re.sub(r"[\x01\x02]", "", _ANSI_RE.sub("", str(prompt)))
    rows = max(1, -(-(dwidth(plain) + dwidth(typed)) // max(1, cols)))
    return "\x1b[1A\x1b[2K" * rows + "\r"


def erase_input_line(prompt, typed=""):
    """Borra la línea que acaba de ocupar un input() (prompt + `typed`) para volver a pedirla en el
    mismo sitio, sin líneas nuevas. True si lo hizo; False sin terminal interactivo o en debug."""
    if not INPLACE:
        return False
    try:
        sys.stdout.write(erase_seq(prompt, typed, term_width() + 1))
        sys.stdout.flush()
        return True
    except Exception as _ign:
        ignore("erase_input_line", _ign)
        return False


def retry_prompt(cur, typed, bad=None, warn=None):
    """Respuesta vacía o inválida: borra la línea escrita y devuelve el prompt para repetirla en el
    mismo sitio. `bad` es el prompt que sale tras una respuesta inválida (None = el mismo, para
    un Enter vacío). Sin terminal interactivo o en debug imprime `warn`, como antes, y deja `cur`."""
    if erase_input_line(cur, typed):
        return bad or cur
    if warn:
        m_warn(warn)
    return cur


def bad_prompt(why):
    """«✗ 1-12, b o q ▸ »: el prompt tras una opción inválida (la ayuda corta va en la misma línea)."""
    return paint("✗", "red", True) + " " + paint(why, "gray") + " " + paint("▸", "orange", True) + " "


# ───────────────────── [B5] Barras y paneles de progreso ─────────────────────
def speed_text(v):
    """Velocidad de bajada con el mismo formato en todas las barras."""
    return f"↓ {human_size(v)}/s"


def spaced(text):
    """«3.0MB/s» → «3.0 MB/s» (número y unidad separados, como en dpt)."""
    return re.sub(r"(\d)(B|KB|MB|GB|TB)\b", r"\1 \2", str(text))


def mmss(sec):
    sec = max(0, int(sec))
    return f"{sec // 60}:{sec % 60:02d}"


def size_pair(done, total):
    """«20/48 MB» (o GB si el total pasa de 1 GB)."""
    u, d = ("GB", 1024 ** 3) if total >= 1024 ** 3 else ("MB", 1024 ** 2)
    f = "{:.1f}" if d > 1024 ** 2 else "{:.0f}"
    return f"{f.format(done / d)}/{f.format(total / d)} {u}"


def track_str(n):
    return paint(EMPTY * n, "track") if n > 0 else ""


def tip_str(now):
    """Punta pulsante de la barra (╸)."""
    if not TIP:
        return ""
    if TRUECOLOR and ANIM and USE_COLOR:
        k = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(now * 5))
        r, g, b = (int(c * k) for c in PALETTE["magenta"][0])
        return f"\x1b[38;2;{r};{g};{b}m{TIP}\x1b[0m"
    return paint(TIP, "magenta")


def bar_str(w, frac, now, sweep=None, indet=False, warn=False):
    """Barra Aurora de `w` columnas: degradado que fluye, punta y pista. sweep = llenado
    final en menta; indet = segmento que rebota (sin porcentaje conocido)."""
    w = max(0, int(w))
    if sweep is not None:
        k = w if sweep >= 1 else int(w * sweep)
        return paint(FILL * k, "mint") + track_str(w - k)
    if indet:
        seg = max(3, w // 5)
        span = max(0, w - seg)
        period = max(1, 2 * span)
        k = int(now * 8) % period
        pos = k if k <= span else period - k
        return track_str(pos) + grad(FILL * seg) + track_str(w - seg - pos)
    f = int(w * max(0.0, min(1.0, frac)))
    if warn:                                   # velocidad < 50 %: la barra se tiñe de ámbar
        fill = paint(FILL * f, "amber") if f else ""
    else:
        fill = grad(FILL * f, 0.0, 1.0, (now * 0.4) % 1.0 if ANIM else 0.0) if f else ""
    rest = w - f
    t = ""
    if rest > 0 and frac < 1.0 and TIP:
        t, rest = (paint(TIP, "amber") if warn else tip_str(now)), rest - 1
    return fill + t + track_str(rest)


PCT_FLASH = 1.6          # segundos que dura el efecto del % al cambiar


def pct_text(ptxt, age):
    """El % recién cambiado: degradado que fluye y se apaga hacia blanco en PCT_FLASH s."""
    f = smooth(age / PCT_FLASH)
    n = max(1, len(ptxt) - 1)
    o, m, w = (PALETTE[k][0] for k in ("orange", "magenta", "white"))
    out = "".join(_fg(mix(mix(o, m, tri(i / n + age * 0.5)), w, f)) + ch for i, ch in enumerate(ptxt))
    return out + "\x1b[0m"


SPARK = "▁▂▃▄▅▆▇█"


def spark_str(hist, n):
    vals = hist[-n:]
    if not vals:
        return ""
    top, low = max(max(vals), 0.001), min(vals)
    if top - low < top * 0.02:                 # velocidad constante: línea media, no un bloque lleno
        return grad(SPARK[4] * len(vals))
    low = min(low, top * 0.6)                  # escala visible aunque la velocidad varíe poco
    return grad("".join(SPARK[min(7, int((v - low) / (top - low) * 7.999))] for v in vals))


class Bar:
    """Progreso en vivo, redibujado en su sitio por un hilo (≈7 fps).
    panel=True: panel de 3 líneas como dpt (etiqueta · paso · %, barra a todo el ancho,
    métricas con gráfica) que al terminar se colapsa a «✓ etiqueta … tamaño».
    panel=False: una sola línea «● etiqueta ━━╸╌╌ 0:03» para esperas cortas.
    Sin porcentaje conocido la barra rebota con el tiempo."""

    def __init__(self, panel=False):
        self.lock = threading.RLock()
        self.th = None
        self.run = False
        self.live = sys.stdout.isatty() and not DEBUG
        self.panel = bool(panel) and self.live and ANSI_OK
        self.drawn = 0                      # líneas que el panel tiene pintadas ahora
        self.last_len = 0                   # (una línea) columnas pintadas
        self.label, self.pct, self.tail = "", None, ""
        self.indet, self.hold, self.t0 = True, 0.0, 0.0
        self.wpaths, self.wtotal, self.wsamp, self.wspeed = [], 0, None, None
        self.hook_t, self.last_draw = 0.0, 0.0
        self.final_tail, self.final_size = "", ""
        self.step, self.sizes, self.engine = "", None, ""
        self.hist, self.chg, self.last_ip = [], 0.0, -1
        self.rows = 3                        # líneas del panel: 3 o más (gráfica de rows-4 filas)
        self.gr, self.cur, self.smo = [], 0.0, 0.0   # gráfica que se desplaza: una muestra por tick del hilo (≈7/s)
        self.sec = []                        # velocidad una vez por segundo (gráfica a todo el ancho)
        self.meta_top, self.meta_bot = "", ""   # datos del archivo: origen (arriba) y formato/tamaño (abajo)
        self.slow = False                    # velocidad caída (barra ámbar)
        self.w = safe_width()                # se mide en el hilo principal (en a-Shell el hilo
                                             # de la barra no ve el tamaño real del terminal)

    # ── ciclo de vida ──
    def start(self, label, indeterminate=True, tail=""):
        self.stop()
        self.w = safe_width()
        with self.lock:
            self.label, self.pct, self.tail = label, None, tail
            self.indet, self.hold, self.t0 = indeterminate, 0.0, time.time()
            self.wpaths, self.wtotal, self.wsamp, self.wspeed = [], 0, None, None
            self.hook_t = 0.0
            self.final_tail = self.final_size = ""
            self.step, self.sizes, self.engine = "", None, ""
            self.hist, self.chg, self.last_ip = [], 0.0, -1
            self.sec = []
            self.gr, self.cur, self.smo = [], 0.0, 0.0
            self.slow = False
        if not self.live:
            m_info(label + "...")
            return
        global ACTIVE_BAR
        ACTIVE_BAR = self
        if self.panel:
            card_arm()                         # la tarjeta del banner sigue viva
        self.run = True
        self.th = threading.Thread(target=self._loop, daemon=True)
        self.th.start()

    def set(self, label=None, pct=None, tail=None, indeterminate=None, val=None,
            sizes=None, step=None, engine=None):
        with self.lock:
            if label is not None:
                self.label = label
            if tail is not None:
                self.tail = tail
            if step is not None:
                self.step = step
            if engine is not None:
                self.engine = engine
            if sizes is not None:
                self.sizes = sizes
            if val is not None and val > 0:
                self.cur = val
                self.hist.append(val)
                del self.hist[:-240]
                _now = time.time()
                if not self.sec or _now - self.sec[-1][0] >= 1.0:
                    self.sec.append((_now, val))
                    del self.sec[:-1800]
            if pct is not None:
                self.indet = False
                if self.pct is not None and pct < self.pct - 0.05:
                    self.hold = time.time() + 1.5      # yt-dlp retrocedió: se ignora
                else:
                    self.pct = pct
                    if int(pct) != self.last_ip:
                        self.last_ip = int(pct)
                        if time.time() - self.chg >= PCT_FLASH + 0.3:     # sin parpadeo continuo
                            self.chg = time.time()
            if indeterminate is not None:
                self.indet = indeterminate

    def _erase(self):
        """Borra lo pintado (con `self.lock` tomado)."""
        if self.drawn:
            sys.stdout.write(f"\x1b[{self.drawn}A\r\x1b[J")
            self.drawn = 0
        elif self.last_len:
            sys.stdout.write(CLR)
        self.last_len = 0
        sys.stdout.flush()

    def stop(self, msg=None, level="ok", keep=False):
        global ACTIVE_BAR
        if self.th:
            self.run = False
            self.th.join(timeout=1)
            self.th = None
            if not keep:
                with self.lock:
                    self._erase()
        if ACTIVE_BAR is self and not keep:
            ACTIVE_BAR = None
        if msg:
            {"ok": m_ok, "warn": m_warn, "info": m_info, "err": m_err}[level](msg)

    def done(self, min_secs=0.0):
        """Congela el progreso como línea final y pasa a la siguiente línea.
        Si duró menos de min_secs solo se borra."""
        global ACTIVE_BAR
        was_live = self.th is not None
        elapsed = time.time() - self.t0
        with self.lock:
            label = self.label
            size = self.final_size or spaced(self.final_tail)
        quick = elapsed < min_secs
        self.stop(keep=was_live and self.panel and not quick)
        if quick:
            return
        if not was_live:
            m_ok(f"{label}: listo" + (f" ({size})" if size else ""))
            return
        if self.panel:                                   # la barra se llena de menta
            for k in range(1, 7):
                with self.lock:
                    self._paint(self._panel_lines(sweep=k / 6))
                time.sleep(0.04)
            time.sleep(0.15)
            with self.lock:
                self._erase()
            if ACTIVE_BAR is self:
                ACTIVE_BAR = None
        else:
            with self.lock:
                self._erase()
        line = self._done_line(label, size or mmss(elapsed))
        if ANIM_LIVE and was_live:                       # «·» → «○» → «✓»
            for mk, col in (("·", "gray"), ("○", "orange"), ("✓", "white")):
                sys.stdout.write("\r" + nowrap(self._done_line(label, size or mmss(elapsed), mk, col)) + "\x1b[K")
                sys.stdout.flush()
                time.sleep(0.06)
        sys.stdout.write("\r" + nowrap(line) + "\n")
        sys.stdout.flush()

    def _done_line(self, label, size, mark="✓", color="mint"):
        w = self.w
        label = label.replace("Convirtiendo", "Convertido", 1)
        left = f"{paint(mark, color)} {fit_text(label, max(4, w - dwidth(size) - 4))}"
        gap = max(1, w - dwidth(left) - dwidth(size))
        return left + " " * gap + paint(size, "gray")

    # ── dibujo ──
    def _state(self):
        now = time.time()
        with self.lock:
            return (now, self.label, self.pct, self.tail,
                    self.indet or self.pct is None, now < self.hold, self.step,
                    self.sizes, self.engine, list(self.hist), now - self.chg)

    def _slow(self, hist):
        """¿La velocidad cayó a menos de la mitad de la habitual? Sale de ámbar al pasar del
        70 % (histéresis). La habitual es el percentil 75 de las últimas muestras."""
        if len(hist) < 8:
            self.slow = False
            return False
        cur = sum(hist[-3:]) / 3.0
        prev = sorted(hist[-123:-3])
        ref = prev[len(prev) * 3 // 4] if prev else cur
        self.slow = cur < (0.7 if self.slow else 0.5) * ref
        return self.slow

    def _panel_lines(self, sweep=None):
        """[línea 1: etiqueta · paso · %, línea 2: barra, línea 3: métricas + gráfica]."""
        w = self.w
        (now, label, pct, tail, indet, holding, step, sizes, engine, hist,
         flash) = self._state()
        d = paint("●" if (int(now * 2) % 2 == 0 or not ANIM) else "○",
                  "amber" if holding else "orange")
        if sweep is not None:
            d, indet = paint("✓", "mint"), indet and pct is None
        slow = sweep is None and self._slow(hist)
        frac = 1.0 if sweep is not None else (0.0 if indet else (pct or 0.0) / 100.0)
        if indet and sweep is None:
            el = int(now - self.t0) if self.t0 else 0
            ptxt = f"{el // 60}:{el % 60:02d}".rjust(5)
            pcol = paint(ptxt, "gray")
        else:
            shown = frac * 100
            if sweep is not None and pct is not None and ANIM:     # el % sube hasta 100
                shown = pct + (100 - pct) * sweep
            ptxt = f"{shown:5.1f}%"
            pcol = ptxt
            if flash < PCT_FLASH and TRUECOLOR and ANIM and USE_COLOR and sweep is None:
                pcol = pct_text(ptxt, flash)
        right = (paint(step, "gray") + "  " if step else "") + pcol
        rw = dwidth(step) + (2 if step else 0) + dwidth(ptxt)
        left = d + " " + fit_text(label, max(4, w - rw - 4))
        l1 = left + " " * max(1, w - dwidth(left) - rw) + right
        l2 = bar_str(w, frac, now, sweep, indet=indet and sweep is None, warn=slow)
        # métricas
        segs = [x for x in re.split(r"\s{2,}", tail.strip()) if x] if tail else []
        parts = []
        for sg in segs:
            if sg.startswith("↓"):
                parts.append(paint("↓", "amber" if slow else "orange") + " " + spaced(sg[1:].strip()))
            elif sg.startswith("ETA"):
                parts.append(paint("◷", "orange") + " " + _eta_short(sg[3:].strip()))
            elif re.match(r"^\d+(\.\d+)?x$", sg):
                parts.append(paint("▸", "orange") + f" {sg[:-1]}×" + (f" {engine}" if engine else ""))
            else:
                parts.append(paint(spaced(sg), "gray"))
        if sizes and sizes[1]:
            parts.append(paint(size_pair(*sizes), "gray"))
        if sweep is not None:
            fin = count_text(self.final_size, sweep) if ANIM else self.final_size
            parts = [paint("✓", "mint") + " " + spaced(fin)] if self.final_size else [paint("✓", "mint")]
        base = "  ".join(parts)
        if self.rows >= 6 and sweep is None:
            return [l1, l2, base] + self._big_lines(w, now)
        room = w - dwidth(base) - 2
        l3 = base + (("  " + spark_str(hist, room)) if room >= 6 and hist and sweep is None else "")
        return [l1, l2, l3]

    def _big_lines(self, w, now):
        """Líneas 4+ del panel ampliado: origen, gráfica de velocidad de varias filas a TODO el ancho,
        resumen y datos del archivo."""
        with self.lock:
            allv = [v for _t, v in self.sec]
            top_txt, bot_txt = self.meta_top, self.meta_bot
        g = max(2, self.rows - 3 - (1 if top_txt else 0) - 1 - (1 if bot_txt else 0))
        out = [paint(fit_text(top_txt, w), "gray")] if top_txt else []
        n = len(allv)
        with self.lock:
            vis = self.gr[-w:]
        peak = max(max(vis) if vis else 0.0, max(allv) if allv else 0.0)   # escala = pico de toda la descarga
        cols = []
        if len(vis) >= 2 and peak > 0:
            cols = [0.0] * (w - len(vis)) + vis      # entra por la derecha y se desplaza a la izquierda
        for r in range(g):
            bot = g - 1 - r                                   # fila contada desde abajo
            cs = []
            for v in cols:
                fill = int(round(v / peak * g * 8)) - bot * 8
                cs.append(" " if fill <= 0 else SPARK[7] if fill >= 8 else SPARK[fill - 1])
            out.append(grad("".join(cs)) if cs else " " * w)
        if n >= 2:
            peak = max(allv)
            el = int(now - self.t0) if self.t0 else 0
            avg, lo = sum(allv) / n, min(allv)
            txt = (f"{el // 60}:{el % 60:02d} · máx {spaced(human_size(peak))}/s · "
                   f"prom {spaced(human_size(avg))}/s · mín {spaced(human_size(lo))}/s")
            if dwidth(txt) > w:
                txt = f"máx {spaced(human_size(peak))}/s · prom {spaced(human_size(avg))}/s"
            out.append(paint(fit_text(txt, w), "gray"))
        else:
            out.append(paint("midiendo velocidad…", "gray"))
        if bot_txt:
            out.append(paint(fit_text(bot_txt, w), "gray"))
        return out

    def _paint(self, lines):
        """Pinta las líneas en su sitio (con `self.lock` tomado)."""
        out = f"\x1b[{self.drawn}A" if self.drawn else ""
        out += "".join("\r" + ln + "\x1b[K\n" for ln in lines)
        if self.drawn > len(lines):
            out += "\x1b[J"                 # el panel se encogió (6 → 3 líneas): borra lo que sobra
        sys.stdout.write("\x1b[?7l" + out + "\x1b[?7h")
        sys.stdout.flush()
        self.drawn = len(lines)
        self.last_draw = time.time()

    def _line(self):
        """Versión de una línea: «● etiqueta ━━╸╌╌ 0:03» (o con porcentaje)."""
        w = self.w
        (now, label, pct, tail, indet, holding, _st, _sz, _en, _h, _fl) = self._state()
        d = (paint("●", "amber" if holding else "orange")
             if (int(now * 2) % 2 == 0 or not ANIM) else " ")
        if indet:
            el = int(now - self.t0) if self.t0 else 0
            right = f"{el // 60}:{el % 60:02d}"
        else:
            right = f"{pct:5.1f}%"
        lab = fit_text(label, max(4, w // 2))
        used = 2 + dwidth(lab) + 1 + 1 + len(right)
        bw = w - used
        bar = (bar_str(bw, (pct or 0) / 100.0, now, indet=indet) + " ") if bw >= 4 else ""
        return f"{d} {lab} {bar}{paint(right, 'gray')}", w

    def _draw(self):
        if self.panel:
            with self.lock:
                self._paint(self._panel_lines())
            return
        line, vis = self._line()
        with self.lock:
            sys.stdout.write("\r" + nowrap(line) + "\x1b[K\r")
            sys.stdout.flush()
            self.last_len = vis
            self.last_draw = time.time()

    def reset(self, label=None):
        """Reinicia la barra en modo indeterminado (otro intento / otra fase)."""
        self.w = safe_width()
        with self.lock:
            if label is not None:
                self.label = label
            self.pct, self.tail, self.indet = None, "", True
            self.final_tail = self.final_size = ""
            self.sizes, self.hist, self.engine = None, [], ""
            self.sec = []
            self.gr, self.cur, self.smo = [], 0.0, 0.0
            self.hold, self.t0 = 0.0, time.time()
            self.slow = False

    def watch(self, paths, total=0):
        """Archivos temporales a vigilar para calcular el avance si yt-dlp no lo informa."""
        with self.lock:
            self.wpaths = [p for p in (paths or []) if p]
            self.wtotal, self.wsamp, self.wspeed = total or 0, None, None

    def _poll(self):
        with self.lock:
            paths, total = self.wpaths, self.wtotal
            fresh = time.time() - self.hook_t < 1.5      # yt-dlp sí está avisando
        if not paths or fresh:
            return
        path = next((p for p in paths if os.path.isfile(p)), None)
        if not path:
            return
        try:
            size = os.path.getsize(path)
        except OSError as _ign:
            ignore("_poll", _ign)
            return
        if size <= 0:
            return
        now = time.time()
        if self.wsamp is None:
            self.wsamp = (now, size)
        elif now - self.wsamp[0] >= 1.0:
            if size >= self.wsamp[1]:
                self.wspeed = (size - self.wsamp[1]) / (now - self.wsamp[0])
            self.wsamp = (now, size)
        pct = size / total * 100 if total and size < total * 0.995 else None
        parts = []
        if self.wspeed:
            parts.append(speed_text(self.wspeed))
        if pct is None:                       # sin total fiable: el tamaño tras la velocidad
            parts.append(human_size(size))
        elif self.wspeed:
            eta = int((total - size) / self.wspeed)
            parts.append(f"ETA {eta // 60:02d}:{eta % 60:02d}")
        tail = "  ".join(parts)
        if pct is not None:
            self.set(pct=pct, tail=tail or None, val=self.wspeed,
                     sizes=(size, total) if total else None)
        else:
            self.set(tail=tail or None, indeterminate=True, val=self.wspeed)

    def kick(self):
        """Redibuja desde el hilo principal (al llegar un aviso de yt-dlp)."""
        if self.th and time.time() - self.last_draw > 0.12:
            self.w = safe_width()
            self._draw()

    def _loop(self):
        while self.run:
            self._poll()
            if self.rows >= 6 and self.cur > 0:     # muestra fija por tick → la gráfica se desplaza fluida
                with self.lock:
                    self.smo += (self.cur - self.smo) * 0.4
                    self.gr.append(self.smo)
                    del self.gr[:-400]
            self._draw()
            if self.panel and CARD["live"]:
                with self.lock:
                    card_tick()
            time.sleep(0.14)


def _eta_short(txt):
    """«00:12» → «0:12» (minutos sin cero a la izquierda, como dpt)."""
    m = re.match(r"^(\d+):(\d{2})$", txt.strip())
    return f"{int(m.group(1))}:{m.group(2)}" if m else txt


PP_NAMES = {
    "FFmpegMerger": "Uniendo", "MoveFiles": "Moviendo",
    "TrackFix": "Pistas", "FFmpegVideoRemuxer": "Remuxando",
    "FFmpegVideoConvertor": "Convirtiendo", "FFmpegMetadata": "Metadatos",
    "EmbedThumbnail": "Miniatura", "FFmpegFixupM4a": "Fix m4a",
    "FFmpegFixupStretched": "Proporción", "FFmpegFixupM3u8": "Fix m3u8",
    "FFmpegFixupDuration": "Duración", "FFmpegFixupTimestamp": "Tiempos",
    "FFmpegFixupDuplicateMoov": "Fix moov",
    "AppleConvert": "Convirtiendo",
}


def pp_label(name):
    if name in PP_NAMES:
        return PP_NAMES[name]
    words = re.sub(r"(?<!^)(?=[A-Z])", " ", (name or "").replace("FFmpeg", "")).strip()
    return words or "Procesando"


def stream_label(d):
    """Etiqueta de la barra de descarga. Prioriza dimensiones: en HLS y sitios
    que no rellenan vcodec un stream de video no debe pintarse como «Audio»."""
    info = d.get("info_dict") or {}
    h = info.get("height") or 0
    w = info.get("width") or 0
    res = str(info.get("resolution") or "")
    v = info.get("vcodec")
    # Video si hay tamaño, resolución tipo 1920x1080, o códec de video real
    if h or w or ("x" in res and "audio" not in res.lower()) or has(v):
        return res_label(info) if (h or w or res) else "Video"
    return info.get("language") or "Audio"


def progress_pct(d):
    """Porcentaje (0-100) del avance reportado por yt-dlp, o None si no se puede calcular.
    Orden: total en bytes, fragmentos (DASH/HLS) y por último el total estimado."""
    done = d.get("downloaded_bytes") or 0
    total = d.get("total_bytes")
    if total:
        return min(99.9, done / total * 100)
    fi, fc = d.get("fragment_index"), d.get("fragment_count")
    if fi and fc and fc > 1:
        return min(99.9, fi / fc * 100)
    est = d.get("total_bytes_estimate")
    if est and done < est * 0.995:             # un estimado ya superado no es fiable
        return done / est * 100
    return None


def panel_rows():
    """Líneas del panel de descarga: 12 (gráfica de 6 filas) si hay espacio, 9 (3 filas) o 3. La pantalla de
    descarga oculta el teclado. DLPY_BAR_ROWS=N (3 a 16) lo fuerza."""
    env = os.environ.get("DLPY_BAR_ROWS", "").strip()
    if env.isdecimal() and 3 <= int(env) <= 16:
        return int(env)
    try:
        free = ui_lines() - banner_height() - 8      # 8 ≈ nombre del archivo, comentarios y margen
    except Exception as _ign:
        ignore("panel_rows", _ign)
        return 3
    return 12 if free >= 9 else 9 if free >= 6 else 3


class DownloadUI:
    """Una barra por proceso: cada pista descargada y cada procesador de yt-dlp.
    Si se pasa vkey, cada stream terminado se guarda en la caché de 24 h."""

    def __init__(self, vkey=None, resumed=False):
        self.bar = Bar(panel=True)
        self.key = None
        self.total = 0            # pistas a descargar (para el «1/3» del panel)
        self.seen = 0
        self.vkey = vkey
        self.resumed = resumed
        self.meta_top = self.meta_bot = ""    # datos del archivo para el panel ampliado
        self._reset_speed()

    def _reset_speed(self):
        self._t0 = time.time()
        self._smp = None          # (instante, bytes) de la última muestra
        self._spd = None          # velocidad propia suavizada (B/s)
        self._maxb = 0
        self._base_b = 0          # bytes que ya había al reanudar (no cuentan en la velocidad)

    def _speed(self, d):
        """Velocidad de yt-dlp; si no la da, la calcula con los bytes descargados."""
        done = d.get("downloaded_bytes") or 0
        now = time.time()
        self._maxb = max(self._maxb, done)
        if self._smp is None:
            self._smp = (now, done)
        elif now - self._smp[0] >= 0.5 and done >= self._smp[1]:
            inst = (done - self._smp[1]) / (now - self._smp[0])
            self._spd = inst if self._spd is None else self._spd * 0.7 + inst * 0.3
            self._smp = (now, done)
        sp = d.get("speed")
        return sp if sp else self._spd

    def begin(self):
        self.bar.rows = panel_rows()
        self.bar.meta_top, self.bar.meta_bot = self.meta_top, self.meta_bot
        self.bar.start("Preparando")

    def hook(self, d):
        """Hook de progreso de yt-dlp: un fallo de la interfaz nunca debe abortar la descarga."""
        try:
            self._hook(d)
        except Exception as e:
            dbg("hook descarga: fallo de interfaz", f"{type(e).__name__}: {e}")

    def _hook(self, d):
        st, b = d.get("status"), self.bar
        key = d.get("filename") or (d.get("info_dict") or {}).get("format_id")
        if DEBUG and (st != "downloading" or key != self.key):
            ev = pick(d, EV_KEYS)
            ev["format_id"] = (d.get("info_dict") or {}).get("format_id")
            dbg("hook descarga", ev)
        if st == "downloading":
            if key != self.key:
                if b.th and self.key is not None:
                    b.done()
                lbl = stream_label(d)
                if b.th:
                    b.set(label=lbl, tail="")
                else:
                    b.start(lbl)
                self.seen += 1
                b.set(step=f"{self.seen}/{self.total}" if self.total > 1 and self.seen <= self.total
                      else "")
                with b.lock:
                    b.hist, b.sizes, b.pct, b.indet = [], None, None, True
                    b.sec = []
                self.key = key
                self._reset_speed()
                if self.resumed:
                    self._base_b = d.get("downloaded_bytes") or 0
                fn = d.get("filename") or ""
                b.watch([d.get("tmpfilename"), fn + ".part" if fn else None, fn],
                        (d.get("info_dict") or {}).get("filesize")
                        or (d.get("info_dict") or {}).get("filesize_approx") or 0)
            b.hook_t = time.time()             # yt-dlp está avisando: _poll no interviene
            pct = progress_pct(d)
            parts = []
            spd = self._speed(d)
            if spd:
                parts.append(speed_text(spd))
            if pct is None:                    # sin total: el tamaño tras la velocidad
                if d.get("downloaded_bytes"):
                    parts.append(human_size(d["downloaded_bytes"]))
            elif d.get("eta") is not None:
                eta = int(d["eta"])
                parts.append(f"ETA {eta // 60:02d}:{eta % 60:02d}")
            tail = "  ".join(parts) or None    # vacío: conserva el último texto
            tot = d.get("total_bytes") or d.get("total_bytes_estimate")
            sz = (d.get("downloaded_bytes") or 0, tot) if tot else None
            if pct is not None:
                b.set(pct=pct, tail=tail, val=spd, sizes=sz)
            else:
                b.set(tail=tail, val=spd, sizes=sz)
            b.kick()
        elif st == "finished" and self.key is not None and key == self.key:
            b.watch([], 0)
            size = d.get("total_bytes") or d.get("downloaded_bytes") or self._maxb
            if self._base_b and size - self._base_b > 0:
                size -= self._base_b
            secs = d.get("elapsed") or (time.time() - self._t0)
            if size:
                with b.lock:
                    b.final_size = spaced(human_size(size))
                    if secs and secs >= 0.05:
                        b.final_tail = speed_text(size / secs)
            b.set(pct=100.0, tail="")
            b.done()
            self.key = None
            # Cachear stream terminado (solo format_id simple; no el merge "137+140")
            if self.vkey:
                info = d.get("info_dict") or {}
                fid = str(info.get("format_id") or d.get("format_id") or "")
                path = d.get("filename") or d.get("tmpfilename")
                if fid and path and "+" not in fid:
                    save_stream_to_cache(self.vkey, fid, path)

    def pp_hook(self, d):
        """Hook de postproceso de yt-dlp: mismo criterio que `hook`."""
        try:
            self._pp_hook(d)
        except Exception as e:
            dbg("hook proceso: fallo de interfaz", f"{type(e).__name__}: {e}")

    def _pp_hook(self, d):
        st, b = d.get("status"), self.bar
        if DEBUG:
            dbg("hook proceso", pick(d, ("status", "postprocessor")))
        if st == "started":
            if b.th:
                b.done(min_secs=0.5)
            self.key = None
            name = str(d.get("postprocessor") or "")
            b.start(pp_label(name))
            if name == "FFmpegMerger":
                info = d.get("info_dict") or {}
                parts = [f.get("filepath") for f in (info.get("requested_formats") or [])
                         if f.get("filepath")]
                total = sum(os.path.getsize(x) for x in parts if os.path.exists(x))
                fp = info.get("filepath")
                if fp and total:
                    root, ext = os.path.splitext(fp)
                    b.watch([root + ".temp" + ext], total)
        elif st == "finished":
            b.done(min_secs=0.5)

    def finish(self):
        if self.bar.th:
            self.bar.done(min_secs=0.5)
        card_settle()

    def abort(self):
        self.bar.stop()
        card_settle()


# ───────────────────── [B6] Terminal: teclado y cuenta regresiva ─────────────────────
def hide_keyboard(settle=0.0):
    """iOS (a-Shell): baja el teclado. `settle` espera (s) a que el terminal tome su alto nuevo."""
    try:
        os.system("hideKeyboard >/dev/null 2>&1")
        if settle:
            time.sleep(settle)
    except Exception as _ign:
        ignore("hide_keyboard", _ign)


def countdown_supported():
    try:
        if not (sys.stdin.isatty() and sys.stdout.isatty()):
            return False
    except (OSError, ValueError, AttributeError) as _ign:
        ignore("countdown_supported", _ign)
        return False
    try:
        import termios, tty, select  # noqa: F401
        return True
    except ImportError as _ign:
        ignore("countdown_supported", _ign)
        return False


def _restore_tty(fd, old):
    """Restaura el terminal y fuerza eco, modo de línea y Enter (a-Shell no siempre
    respeta la restauración simple)."""
    import termios
    try:
        termios.tcsetattr(fd, termios.TCSANOW, old)
    except Exception as _ign:
        ignore("_restore_tty", _ign)
    try:
        cur = termios.tcgetattr(fd)
        cur[0] |= termios.ICRNL
        cur[3] |= termios.ECHO | termios.ICANON | termios.ISIG
        termios.tcsetattr(fd, termios.TCSANOW, cur)
    except Exception as _ign:
        ignore("_restore_tty", _ign)


INPUT_LOCK = {"fd": None, "old": None}
LOCK_INPUT = _flag_env("DLPY_LOCK", False)      # apagado: congelaba a-Shell


def input_lock():
    """iOS (a-Shell): desde el arranque hasta la primera pregunta el terminal queda sin eco ni línea
    (cbreak: el mismo modo de la cuenta regresiva), así un Enter fantasma o lo que se teclee no se
    escribe ni se guarda. Lo suelta input_unlock() al salir la primera pregunta."""
    if not LOCK_INPUT or NESTED_IOS or INPUT_LOCK["fd"] is not None:
        return False
    try:
        if not (sys.stdin.isatty() and sys.stdout.isatty()):
            return False
        import termios, tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        tty.setcbreak(fd, termios.TCSANOW)
    except Exception as _ign:
        ignore("input_lock", _ign)
        return False
    INPUT_LOCK.update(fd=fd, old=old)
    atexit.register(input_unlock, False)          # pase lo que pase, al salir el terminal queda normal
    return True


def input_unlock(drain=True):
    """Devuelve el terminal a su modo normal; antes descarta lo tecleado mientras estuvo bloqueado.
    Se llama al salir cada pregunta (no hace nada si ya está suelto)."""
    fd, old = INPUT_LOCK["fd"], INPUT_LOCK["old"]
    if fd is None:
        return False
    INPUT_LOCK.update(fd=None, old=None)
    if drain:
        drain_pending_input(0.1)
    _restore_tty(fd, old)
    return True


class _PosixKeys:
    """Teclado sin eco para la cuenta regresiva (a-Shell)."""

    def __init__(self):
        import termios, tty, select, codecs
        self.select = select
        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd, termios.TCSANOW)
        self.dec = codecs.getincrementaldecoder("utf-8")("ignore")

    def read(self, timeout):
        """Texto tecleado, o "" si venció `timeout`. EOFError si se cierra la entrada."""
        if not self.select.select([self.fd], [], [], timeout)[0]:
            return ""
        data = os.read(self.fd, 1024)
        if not data:
            raise EOFError
        return self.dec.decode(data)

    def close(self):
        _restore_tty(self.fd, self.old)


def note_prompt(prompt):
    """Anota en running.json la pregunta en curso (pista si el proceso se congela y se cierra a la
    fuerza). Solo si hay una ejecución vigilada; nunca falla."""
    try:
        if not os.path.isfile(RUNNING_FILE):
            return
        data = load_json(RUNNING_FILE)
        if not data:
            return
        text = re.sub(r"\s+", " ", _ANSI_RE.sub("", str(prompt))).strip()
        data["prompt"] = text[:100]
        data["prompt_time"] = int(time.time())
        save_json(RUNNING_FILE, data)
    except Exception as _ign:
        ignore("note_prompt", _ign)


def reexec_script():
    """Ejecuta SCRIPT_PATH (recién instalado o restaurado) dentro de este proceso. Antes deja
    todo limpio: salida vaciada, barra detenida, terminal en modo normal y Enter sobrante
    descartado. La versión nueva sabe (sys._dlpy_reexec) que no debe volver a buscar
    actualizaciones. Termina con SystemExit."""
    import runpy
    try:
        if ACTIVE_BAR is not None:
            ACTIVE_BAR.stop()
    except Exception as _ign:
        ignore("reexec_script", _ign)
    try:
        sys.stdout.flush()
        sys.stderr.flush()
    except Exception as _ign:
        ignore("reexec_script", _ign)
    # a-Shell: ni tcsetattr ni select sobre stdin aquí
    sys._dlpy_reexec = True
    runpy.run_path(SCRIPT_PATH, run_name="__main__")


def timed_input(prompt, seconds=WAIT_SECONDS, phantom=True, plain=None):
    """Cuenta regresiva. Devuelve None si vence sin escribir nada; si el usuario
    empieza a escribir, cancela la cuenta y devuelve la línea completa.
    La línea se edita a mano y el terminal NO vuelve al modo normal a mitad
    (cambiar de modo es lo que congelaba a-Shell)."""
    if not countdown_supported():
        return ask_line(prompt, phantom, plain)
    note_prompt(plain or prompt)
    input_unlock()                   # sale una pregunta: se habilita la entrada
    drain_pending_input()
    try:
        keys = _PosixKeys()
    except Exception as _ign:
        ignore("timed_input", _ign)
        return ask_line(prompt, phantom, plain)
    pre, prompt = split_prompt(pstyle(prompt))
    for ln in pre:
        print(ln)

    buf, typing, esc = [], seconds is None, False     # seconds=None: sin cuenta regresiva
    t_start = time.time()
    end, shown = time.time() + (seconds or 0), None

    def redraw():
        sys.stdout.write(CLR + prompt + "".join(buf))
        sys.stdout.flush()

    try:
        if typing:
            redraw()
        while True:
            if typing:
                timeout = None
            else:
                left = end - time.time()
                if left <= 0:
                    sys.stdout.write(CLR + prompt + paint("sin respuesta", "gray") + "\n")
                    sys.stdout.flush()
                    return None
                secs = int(left) + 1
                nb = safe_width() - dwidth(prompt) - len(str(secs)) - 5     # barra + « N s»
                nb = nb if nb >= 8 else 0
                f = int(nb * left / seconds) if nb else 0
                urg = (1.0 - max(0.0, min(1.0, left / seconds))) if ANIM else 0.0
                pulse = ANIM and secs <= 3 and int(left * 3) % 2 == 0     # late en los últimos 3 s
                key = (f, secs, int(urg * 10), pulse)
                if key != shown:
                    shown = key
                    # el degradado se acorta y pasa a magenta a medida que se agota
                    cd = (grad(FILL * f, 0.6 * urg, 1.0) + paint(EMPTY * (nb - f), "track")) if nb else ""
                    sys.stdout.write(CLR + nowrap(prompt + cd
                                                  + paint(f" {secs} s", "amber" if pulse else "gray", pulse)))
                    sys.stdout.flush()
                timeout = 0.1
            text = keys.read(timeout)
            if not text:
                continue
            for ch in text:
                if esc:                       # saltar secuencias de flechas, etc.
                    if ch.isalpha() or ch == "~":
                        esc = False
                    continue
                if ch == "\x1b":
                    esc = True
                elif ch in "\r\n":
                    if phantom and not buf and (time.time() - t_start < PHANTOM_SECS
                                                or time.time() - START_T < PHANTOM_BOOT):
                        continue                  # Enter fantasma
                    redraw()
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    return "".join(buf)
                elif ch == "\x03":
                    sys.stdout.write("\n")
                    raise KeyboardInterrupt
                elif ch == "\x04":
                    if not buf:
                        raise EOFError
                elif ch in ("\x7f", "\x08"):
                    if buf:
                        buf.pop()
                        typing = True
                        redraw()
                elif ord(ch) >= 32:
                    buf.append(ch)
                    typing = True
                    redraw()
    finally:
        keys.close()


# ╔═════════════════════════════════════════════════════════════════════════════╗
# ║ ÁREA C · UTILIDADES Y FORMATOS — helpers, etiquetas y selección de pistas   ║
# ╚═════════════════════════════════════════════════════════════════════════════╝
# ───────────────────────── [C1] Utilidades ─────────────────────────
def copy_file(src, dst):
    """Como shutil.copy2, pero el chmod/utime del destino es opcional
    (algunos sistemas de archivos los rechazan)."""
    shutil.copyfile(src, dst)
    try:
        st = os.stat(src)
        os.utime(dst, ns=(st.st_atime_ns, st.st_mtime_ns))
    except OSError:
        pass
    return dst


def move_file(src, dst):
    """Como shutil.move, pero copiando con copy_file cuando rename no basta
    (otro sistema de archivos). Devuelve el destino final."""
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src.rstrip(os.sep)))
    try:
        os.rename(src, dst)
        return dst
    except OSError:
        pass
    if os.path.isdir(src) and not os.path.islink(src):
        shutil.copytree(src, dst, copy_function=copy_file)
        shutil.rmtree(src)
    else:
        copy_file(src, dst)
        os.unlink(src)
    return dst


def yes(ans, default=True):
    ans = ans.strip().lower()
    if ans == "":
        return default
    return ans in ("s", "si", "sí", "y", "yes")


def parse_yn(ans, default=True):
    """True/False según la respuesta; Enter = default; None si no se entiende."""
    a = (ans or "").strip().lower()
    if a == "":
        return default
    if a in ("s", "si", "sí", "y", "yes"):
        return True
    if a in ("n", "no"):
        return False
    return None


YN_SUFFIX_RE = re.compile(r"\s*(?:\([sSyY]/[nN](?:/[a-zA-Z])?\))?\s*▸?\s*$")


def yn_prompt(msg, default=True, alt=None):
    """Texto de una pregunta s/n con el final unificado: «… (S/n) ▸ » si Enter = sí,
    «… (s/N) ▸ » si Enter = no, sin importar qué traiga ya `msg`. `alt` = (letra, etiqueta) añade una
    tercera respuesta: «(S/n/r)»."""
    base = YN_SUFFIX_RE.sub("", str(msg))
    return f"{base} {'(S/n' if default else '(s/N'}{'/' + alt[0] if alt else ''}) ▸ "


def yn_line(default=True, alt=None):
    """« [S] Sí  [n] No ▸ » (la letra de la opción por omisión va en mayúscula)."""
    def opt(key, label, on):               # la opción por omisión resalta; la otra queda en gris
        return (paint(f"[{key}]", "orange", True) + " " + paint(label, "white", True) if on
                else paint(f"[{key}] {label}", "gray"))
    extra = ("  " + paint(f"[{alt[0]}] {alt[1]}", "gray")) if alt else ""
    return (" " + opt("S" if default else "s", "Sí", default) + "  "
            + opt("n" if default else "N", "No", not default) + extra + " " + paint("▸", "orange", True) + " ")


def print_question(text):
    """«▍¿Pregunta?» en blanco y negrita (barra naranja), sin el final «(S/n) ▸»: el estilo de toda pregunta."""
    base = YN_SUFFIX_RE.sub("", str(text)).strip()
    for i, ln in enumerate(wrap_text(base, term_width() - 1)):
        print((paint("▍", "orange") if i == 0 else " ") + paint(ln, "white", True))


def ask_yn(prompt, default=True, seconds=False, alt=None):
    """Pregunta s/n y la repite hasta recibir una respuesta válida.
    Estilo dpt: «▍¿Pregunta?» y debajo « [S] Sí  [n] No ▸ » (con barra si hay cuenta).
    seconds=False: ask_line; seconds=None: timed_input sin cuenta; número: con cuenta.
    alt=(letra, etiqueta) admite una tercera respuesta (p. ej. ("r", "Remux")) que devuelve esa letra.
    Devuelve True/False, la letra de `alt`, o None si venció la cuenta regresiva.
    EOFError/KeyboardInterrupt se propagan a quien llama."""
    plain = yn_prompt(prompt, default, alt)
    print_question(prompt)
    line = yn_line(default, alt)
    cur = line
    while True:
        # Enter vacío = No es inofensivo: con (s/N) no se filtra el Enter «fantasma».
        ph = bool(default)
        r = (ask_line(cur, ph, plain) if seconds is False
             else timed_input(cur, seconds, ph, plain))
        if r is None:
            return None
        if alt and str(r).strip().lower() == alt[0].lower():
            return alt[0].lower()
        v = parse_yn(r, default)
        if v is not None:
            return v
        # inválida: se borra y se repite en el mismo renglón con «✗» en rojo
        cur = retry_prompt(cur, r, paint("✗", "red", True) + line[1:],
                           "Respuesta inválida: escribe s, n" + (f" o {alt[0]}." if alt else "."))


def ask(msg, default=True, seconds=False):
    """Pregunta s/n. seconds=número: cuenta regresiva y, si vence, se toma `default`."""
    try:
        r = ask_yn(msg, default, seconds=seconds)
    except (EOFError, KeyboardInterrupt):
        return False
    if r is None:
        m_info(f"Sin respuesta: se elige {'Sí' if default else 'No'}.")
        return bool(default)
    return bool(r)


def safe_name(title, max_bytes=MAX_NAME_BYTES):
    s = unicodedata.normalize("NFC", title or "video")
    s = re.sub(r"[\x00-\x1f\x7f]", "", s)
    s = re.sub(r'[\\/:*?"<>|]', "_", s)
    s = re.sub(r"\s+", " ", s).strip(" .").lstrip(".")
    if not s:
        s = "video"
    b = s.encode("utf-8")
    if len(b) > max_bytes:
        s = b[:max_bytes].decode("utf-8", "ignore").rstrip(" .")
    return s or "video"


def human_size(n):
    """«48 MB», «1.9 GB», «3.0 MB»: con un decimal por debajo de 10 y entero desde 10."""
    if not n:
        return "?"
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            if u == "B" or n >= 9.95:
                return f"{n:.0f} {u}"
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} TB"


def kbps_text(k):
    """«850 kbps», «2.1 Mbps»; None si no hay dato."""
    return fmt_kbps(k) if k else None


def fmt_kbps(k):
    k = float(k)
    return f"{k / 1000:.1f} Mbps" if k >= 1000 else f"{k:.0f} kbps"


def precise_size(n):
    """Como human_size pero con GB a 2 decimales y 0B explícito."""
    n = int(n or 0)
    if n < 1024:
        return f"{n}B"
    x = float(n)
    for u in ("KB", "MB", "GB"):
        x /= 1024
        if x < 1024 or u == "GB":
            return f"{x:.2f}{u}" if u == "GB" else f"{x:.1f}{u}"


def _size_text(n):
    return human_size(n) if n else "0B"


def ffmpeg_available():
    try:
        from yt_dlp.postprocessor import FFmpegPostProcessor
        if FFmpegPostProcessor().available:
            return True
    except Exception as _ign:
        ignore("ffmpeg_available", _ign)
    return bool(shutil.which("ffmpeg"))


# ───────────────────── [C2] Formatos y pistas: etiquetas y selección ─────────────────────
def mark_originals(audios):
    orig = {f["format_id"] for f in audios
            if "original" in (f.get("format_note") or "").lower()}
    if orig:
        return orig
    langs = {f.get("language") for f in audios if f.get("language")}
    if len(langs) > 1:
        prefs = [f.get("language_preference") for f in audios
                 if f.get("language_preference") is not None]
        if prefs:
            top = max(prefs)
            return {f["format_id"] for f in audios
                    if f.get("language_preference") == top}
    return set()


def abr_of(f):
    return f.get("abr") or f.get("tbr") or 0


def build_tracks(audios, orig_ids):
    groups = {}
    for f in audios:
        groups.setdefault(f.get("language") or "und", []).append(f)
    orig_lang = None
    for f in audios:
        if f["format_id"] in orig_ids:
            orig_lang = f.get("language") or "und"
            break
    tracks = []
    for lang, fs in groups.items():
        best = max(fs, key=lambda f: (apple_audio(f), abr_of(f)))
        tracks.append({"lang": lang, "fmt": best, "original": lang == orig_lang})
    tracks.sort(key=lambda t: (not t["original"], not apple_audio(t["fmt"]), t["lang"]))
    return tracks, orig_lang


def track_label(t):
    f = t["fmt"]
    note = (f.get("format_note") or "").split(",")[0].strip()
    note = re.sub(r"\s*\(default\)", "", note, flags=re.I)
    return note or t["lang"]


def format_tag(f):
    """Etiqueta de un formato SIN resolución conocida: su id si es corto y legible («hd», «sd»); si no, «?»."""
    res = str(f.get("resolution") or "").strip()
    if res and res.lower() not in ("unknown", "none", "?"):
        return res
    fid = str(f.get("format_id") or "")
    if re.fullmatch(r"\d{1,4}", fid):
        return "id" + fid                       # «1», «2», «3» → «id1», «id2», «id3»
    return fid if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,9}", fid) else "?"


def res_label(f):
    h = f.get("height")
    res = f"{h}p" if h else format_tag(f)
    fps = f.get("fps")
    if fps and fps > 30:
        res += f"{fps:.0f}"
    return res


AUDIO_HEAD = ["Fmt", "Códec", "Idioma", "Tamaño"]
VIDEO_HEAD = ["Res", "Fmt", "Códec", "Rango", "Audio", "Tamaño"]
TRACK_HEAD = ["Idioma", "Pista", "Formato"]


def audio_row(n, f, orig_ids):
    codec = (f.get("acodec") or "?").split(".")[0]
    abr = f.get("abr") or f.get("tbr")
    flags = set()
    if apple_audio(f):
        flags.add("apple")
    if f["format_id"] in orig_ids:
        flags.add("orig")
    return {"n": n, "flags": flags,
            "cols": [f.get("ext", "?"), f"{codec} {abr:.0f}k" if abr else codec,
                     f.get("language") or "",
                     human_size(f.get("filesize") or f.get("filesize_approx"))]}


AUDIO_ONLY_EXTS = ("m4a", "mp3", "aac", "wav", "aiff", "caf", "flac", "ogg", "opus", "weba")


def normalize_format(f):
    """yt-dlp deja vcodec/acodec en None cuando no conoce el códec (MP4 directos
    de algunos sitios). Sin esto el formato no se reconocía como video ni audio.
    Trabaja sobre una copia. Solo asume avc1/mp4a en contenedores Apple con
    indicios claros de video; en el resto usa «unknown» (no se marca compatible)."""
    f = dict(f)
    v, a = f.get("vcodec"), f.get("acodec")
    ext = (f.get("ext") or "").lower()
    audio_only = (v == "none" or f.get("resolution") == "audio only"
                  or (not v and not a and ext in AUDIO_ONLY_EXTS
                      and not f.get("height") and not f.get("width")))
    if audio_only:
        f["vcodec"] = "none"
        if not a:
            f["acodec"] = "unknown"
        return f
    if not v:
        # Conservador: solo adivinar códecs Apple si el contenedor es nativo y
        # hay resolución o bitrate de video. Si no, «unknown» → no compatible.
        looks_video = bool(f.get("height") or f.get("width") or f.get("vbr")
                           or f.get("tbr") or (f.get("resolution") and "x" in str(f.get("resolution"))))
        guess = ext in GUESS_VEXT and looks_video
        f["vcodec"] = "avc1" if guess else "unknown"
        f["_guess"] = True
        if not a:
            f["acodec"] = "mp4a" if guess else "unknown"
    return f


def video_row(n, f):
    return {"n": n, "flags": {"apple"} if apple_video(f) else set(),
            "cols": [res_label(f), f.get("ext", "?"),
                     (f.get("vcodec") or "?").split(".")[0] + ("?" if f.get("_guess") else ""),
                     range_label(f),
                     "con audio" if has(f.get("acodec")) else "sin audio",
                     human_size(f.get("filesize") or f.get("filesize_approx"))]}


UI_LINES = int(os.environ.get("DLPY_LINES", "26").strip() or 26) if os.environ.get("DLPY_LINES", "26").strip().isdecimal() else 26


def ui_lines():
    """Líneas de la interfaz, banner incluido: 26 siempre; DLPY_LINES=0 usa el alto del terminal."""
    if UI_LINES:
        return UI_LINES
    try:
        return shutil.get_terminal_size((80, 24)).lines
    except (OSError, ValueError):
        return 24


def pinned_lines():
    """Líneas que ocupan los comentarios fijados tras limpiar la pantalla."""
    if not ROAST:
        return 0
    try:
        return sum(len(wrap_text(t, max(8, term_width() - 2))) for t in PINNED)
    except Exception:
        return len(PINNED)


def banner_height():
    """Líneas ocupadas arriba: la tarjeta (5 si aún no hay) más los comentarios fijados."""
    body = CARD.get("body")
    return ((len(body) + 2) if (body and CARD.get("fresh")) else 5) + pinned_lines()


def list_cap(overhead=16):
    """Filas máximas de la lista de formatos dentro de las 26 líneas de la interfaz.
    `overhead` = líneas de la pantalla que no son filas (16 = caso más alto: título de 2 líneas).
    DLPY_ROWS=N lo fuerza; DLPY_ROWS=0 = sin tope."""
    env = os.environ.get("DLPY_ROWS", "").strip()
    if env.isdecimal():
        return int(env) or 10 ** 6
    return max(8, ui_lines() - overhead)


def visible_cap(overhead, lines=None):
    """Filas de una lista que caben en las 26 líneas de la interfaz. None solo con DLPY_ROWS=0."""
    env = os.environ.get("DLPY_ROWS", "").strip()
    if env.isdecimal():
        return int(env) or None
    return max(4, (ui_lines() if lines is None else lines) - overhead)


def audio_quality_keys(audios):
    """Calidad de cada audio: (idioma, grupo de bitrate). Mismo grupo = bitrate dentro de +12 %
    del más bajo del grupo (m4a 128k y opus 130k son la misma calidad)."""
    keys, by_lang = {}, {}
    for i, f in enumerate(audios):
        by_lang.setdefault(f.get("language") or "", []).append(i)
    for lang, idxs in by_lang.items():
        idxs.sort(key=lambda i: abr_of(audios[i]))
        base, grp = None, -1
        for i in idxs:
            a = abr_of(audios[i])
            if base is None or a > base * 1.12 + 1:
                base, grp = a, grp + 1
            keys[i] = (lang, grp)
    return [keys[i] for i in range(len(audios))]


def video_quality_keys(videos):
    """Calidad de cada video: resolución/fps y rango. Cuenta como rango distinto el HDR o más de
    8 bits; 8 bits / sin dato (lo normal en avc1 frente a vp9) es el mismo rango SDR."""
    def rng(f):
        bits = detect_bit_depth(f)
        return (detect_hdr(f) or "", bits if bits and bits > 8 else 0)
    return [(res_label(f), rng(f)) for f in videos]


def best_per_quality(rows, keys, rank, keep=None):
    """Índices de UNA fila por calidad: la mejor de su grupo según `rank(i)` (mayor = mejor); la
    fila `keep` (la de «b») gana en su grupo. Salen en el orden de la lista."""
    groups = {}
    for i, k in enumerate(keys):
        groups.setdefault(k, []).append(i)
    out = [keep if keep in g else max(g, key=rank) for g in groups.values()]
    return sorted(out)


def short_pick(rows, take, keep=None, uniq=None, first=False):
    """Índices de las filas de la lista corta: primero las compatibles con la plataforma (marca
    «apple»), las mejores (las últimas); si ninguna lo es, las mejores de todas. La fila `keep` (la de
    «b») siempre entra. Salen en el orden de la lista. `uniq`: solo se eligen entre esos índices
    (una fila por calidad); `keep` entra aunque no esté. `first`: listas de mejor a peor, se
    eligen las primeras en vez de las últimas."""
    cand = list(range(len(rows))) if uniq is None else [i for i in uniq if 0 <= i < len(rows)]
    pool = [i for i in cand if "apple" in rows[i]["flags"]] or cand
    take = max(0, take)
    idx = (pool[:take] if first else pool[-take:]) if take else []
    if keep is not None and 0 <= keep < len(rows) and keep not in idx:
        idx = [keep] + ((idx[:-1] if first else idx[1:]) if len(idx) >= take else idx)
    return sorted(idx)


def m_block(label, lines):
    """Bloque «✓ Etiqueta  línea» con las líneas siguientes sangradas (una sola marca)."""
    lead = len(label) + 4
    out = []
    for ln in lines:
        out += wrap_text(ln, max(8, term_width() - lead))
    print(paint("✓", "mint") + " " + paint(label, "white", True) + "  " + out[0])
    for ln in out[1:]:
        print(" " * lead + ln)


def drop_empty_cols(rows, head=None):
    """Quita las columnas vacías en TODAS las filas (así una columna opcional solo ocupa
    sitio si algún formato la usa). Devuelve (filas, encabezado) sin modificar los originales."""
    if not rows:
        return rows, head
    keep = [i for i in range(len(rows[0]["cols"])) if any(r["cols"][i] for r in rows)]
    out = [dict(r, cols=[r["cols"][i] for i in keep]) for r in rows]
    return out, ([head[i] for i in keep] if head else head)


def auto_best(audios, videos, orig_ids, can_merge, quiet=False):
    if videos:
        apple = [f for f in videos if apple_video(f)]
        if not apple:
            if not quiet:
                m_warn(f"No hay video compatible con {PLAT_LABEL}; se usará el mejor disponible.")
            apple = videos
        if not can_merge:
            with_audio = [f for f in apple if has(f.get("acodec"))]
            if with_audio:
                apple = with_audio
            elif not quiet:
                m_warn("Sin ffmpeg no se puede unir audio; el video quedará sin audio.")
        return "v", max(apple, key=lambda f: (f.get("height") or 0, f.get("tbr") or 0))
    best = max(audios, key=lambda f: (f["format_id"] in orig_ids, apple_audio(f), abr_of(f)))
    return "a", best


def track_row(n, t):
    f = t["fmt"]
    flags = set()
    if apple_audio(f):
        flags.add("apple")
    if t["original"]:
        flags.add("orig")
    return {"n": n, "flags": flags,
            "cols": [t["lang"], track_label(t),
                     f"{f.get('ext')} {(f.get('acodec') or '?').split('.')[0]} {abr_of(f):.0f}k"]}


def ask_default_track(tracks, original):
    """Devuelve (pista, sin_respuesta). sin_respuesta=True omite las pistas extra.
    iOS: si no caben todas con el teclado abierto salen las mejores y «m» muestra el resto."""
    trows = [track_row(i, t) for i, t in enumerate(tracks, 1)]
    for r, t in zip(trows, tracks):
        if t is original:
            r["flags"].add("default")            # ▸ en el margen: la que vale con Enter o al acabar la cuenta
    orig_i = next((i for i, t in enumerate(tracks) if t is original), None)
    keys = ["apple", "orig"]
    cd = countdown_supported()
    txt0 = "n.º · m más · {Enter = original}" + (f" · {WAIT_SECONDS} s" if cd else "")
    cap = visible_cap(banner_height() + 3 + len(_legend_lines(keys))
                      + len(wrap_text(txt0, term_width() - 2)) + 1)
    vis = short_pick(trows, cap, orig_i, None, True) if cap is not None and len(trows) > cap else None

    def draw(full):
        """Pantalla de pistas; devuelve True si quedan filas ocultas (se ven con «m»)."""
        if full:
            hide_keyboard(0.3)
        clear_screen()
        if full and CARD["pin"]:
            card_thread_stop()          # lista completa: se suelta el banner anclado para poder deslizar
        hid = vis is not None and not full
        header("ELEGIR PISTA PREDETERMINADA" + (f" · +{len(trows) - len(vis)} más" if hid else ""), gap=False)
        m_info("Se detectaron varios idiomas.")
        legend(keys)
        print_rows([trows[i] for i in vis] if hid else trows, keys, TRACK_HEAD)
        txt = "n.º · " + ("m más · " if hid else "") + "{Enter = original}"
        if cd and not full:
            txt += f" · {WAIT_SECONDS} s"
        hint(txt)
        return hid

    hid = draw(False)
    full = False
    cur = PROMPT
    while True:
        try:
            raw = timed_input(cur, None if full else WAIT_SECONDS)
        except (EOFError, KeyboardInterrupt):
            return original, True
        if raw is None:
            m_info("Sin respuesta: se usa la pista original.")
            return original, True
        typed, raw = raw, raw.strip()
        if not raw:
            return original, False
        if raw.lower() == "m" and hid:
            hid, full = draw(True), True
            cur = PROMPT
            continue
        if raw.isdecimal() and 1 <= int(raw) <= len(tracks):
            chosen = tracks[int(raw) - 1]
            m_ok(f"Predeterminada: {chosen['lang']} · {track_label(chosen)}")
            return chosen, False
        cur = retry_prompt(cur, typed, bad_prompt(f"1-{len(tracks)}" + (", m" if hid else "") + " o Enter"),
                           f"Opción inválida: escribe un número del 1 al {len(tracks)}"
                           + (", m" if hid else "") + " o Enter.")


def ask_extra_tracks(tracks, primary):
    others = [t for t in tracks if t is not primary]
    if not others:
        return [primary]
    print()
    try:
        r = ask_yn("¿Incluir pistas adicionales? (s/N) ▸ ", default=False, seconds=WAIT_SECONDS)
    except (EOFError, KeyboardInterrupt):
        return [primary]
    if not r:                                   # None (sin respuesta) o No
        return [primary]

    orows = [track_row(i, t) for i, t in enumerate(others, 1)]
    keys = ["apple", "orig"]
    txt0 = "n.º separados por espacio (ej. 1 2 4) · m más · {Enter = todas}"
    cap = visible_cap(banner_height() + 2 + len(_legend_lines(keys))
                      + len(wrap_text(txt0, term_width() - 2)) + 1)
    vis = short_pick(orows, cap, None, None, True) if cap is not None and len(orows) > cap else None

    def draw(full):
        if full:
            hide_keyboard(0.3)
        clear_screen()
        if full and CARD["pin"]:
            card_thread_stop()
        hid = vis is not None and not full
        header("ELEGIR PISTAS DE AUDIO ADICIONAL" + (f" · +{len(orows) - len(vis)} más" if hid else ""), gap=False)
        legend(keys)
        print_rows([orows[i] for i in vis] if hid else orows, keys, TRACK_HEAD)
        hint("n.º separados por espacio (ej. 1 2 4) · " + ("m más · " if hid else "") + "{Enter = todas}")
        return hid

    hid = draw(False)
    cur = PROMPT
    while True:
        try:
            typed = timed_input(cur, None)
            raw = typed.strip()
        except (EOFError, KeyboardInterrupt):
            return [primary]
        if not raw:
            chosen = others
            break
        if raw.lower() == "m" and hid:
            hid = draw(True)
            cur = PROMPT
            continue
        toks = [x for x in re.split(r"[\s,]+", raw) if x]
        bad = [x for x in toks if not (x.isdecimal() and 1 <= int(x) <= len(others))]
        if bad:
            cur = retry_prompt(cur, typed, bad_prompt(f"1-{len(others)}" + (", m" if hid else "")),
                               f"Opción inválida: {' '.join(bad)} (usa números del 1 al {len(others)}"
                               + (" o m" if hid else "") + ").")
            continue
        chosen = [others[int(x) - 1] for x in toks]
        break
    out = [primary]
    for t in chosen:
        if t not in out:
            out.append(t)
    return out


# ╔════════════════════════════════════════════════════════════════════════════════════════════════════════╗
# ║ ÁREA D · POST-PROCESO Y CONVERSIÓN — pista predeterminada, conversión Apple, bits/HDR, ya descargado   ║
# ╚════════════════════════════════════════════════════════════════════════════════════════════════════════╝
# ───────── [D1] Post-proceso: pista predeterminada ─────────
def _read_progress(pfile):
    """(segundos procesados, velocidad x) del archivo -progress de ffmpeg."""
    try:
        with open(pfile, "r", encoding="utf-8", errors="ignore") as fh:
            lines = fh.read().splitlines()
    except OSError as _ign:
        ignore("_read_progress", _ign)
        return None, None
    secs, speed = None, None
    for ln in reversed(lines):
        if secs is None and ln.startswith(("out_time_us=", "out_time_ms=")):
            try:
                secs = int(ln.split("=", 1)[1]) / 1e6
            except ValueError:
                pass
        elif speed is None and ln.startswith("speed="):
            try:
                speed = float(ln.split("=", 1)[1].strip().rstrip("x"))
            except ValueError:
                pass
        if secs is not None and speed is not None:
            break
    return secs, speed


def _read_progress_raw(pfile):
    """Último bloque completo de -progress, en bruto (clave=valor …)."""
    try:
        with open(pfile, "r", encoding="utf-8", errors="ignore") as fh:
            lines = fh.read().splitlines()
    except OSError as _ign:
        ignore("_read_progress_raw", _ign)
        return ""
    ends = [i for i, ln in enumerate(lines) if ln.startswith("progress=")]
    if not ends:
        return ""
    start = ends[-2] + 1 if len(ends) > 1 else 0
    return " ".join(lines[start:ends[-1] + 1])


def ffmpeg_progress(pp, src, dst, opts, duration, bar):
    """Ejecuta ffmpeg y dibuja el avance real en `bar`. Si no se puede lanzar
    directamente, usa pp.run_ffmpeg (sin porcentaje)."""
    import subprocess
    exe = getattr(pp, "executable", None) or shutil.which("ffmpeg") or "ffmpeg"
    pfile, efile = dst + ".progress", dst + ".err"
    cmd = [exe, "-y", "-hide_banner", "-loglevel", "info" if DEBUG else "error", "-nostats",
           "-progress", pfile, "-i", "file:" + src] + list(opts) + ["file:" + dst]
    for f in (pfile, efile):
        try:
            os.remove(f)
        except OSError as _ign:
            ignore("ffmpeg_progress", _ign)
    dbg("ffmpeg comando", shlex.join(cmd))
    errfh = None
    try:
        errfh = open(efile, "w", encoding="utf-8")
        proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=errfh)
    except Exception as e:
        if errfh is not None:
            try:
                errfh.close()
            except Exception as _ign:
                ignore("ffmpeg_progress", _ign)
        dbg("ffmpeg no se pudo lanzar; se usa run_ffmpeg de yt-dlp", repr(e))
        pp.run_ffmpeg(src, dst, opts)
        return
    t0 = time.time()
    epos, last_raw = [0], [0.0]

    def drain_err():
        """Debug: reenvía la salida de ffmpeg tal cual va llegando."""
        if not DEBUG:
            return
        try:
            with open(efile, "r", encoding="utf-8", errors="ignore") as fh:
                fh.seek(epos[0])
                chunk = fh.read()
                epos[0] = fh.tell()
        except OSError as _ign:
            ignore("drain_err", _ign)
            return
        if chunk:
            sys.stdout.write(paint(chunk, "gray"))
            sys.stdout.flush()

    try:
        while proc.poll() is None:
            drain_err()
            if DEBUG and time.time() - last_raw[0] >= 2.0:
                last_raw[0] = time.time()
                raw = _read_progress_raw(pfile)
                if raw:
                    dbg("ffmpeg progress", raw)
            secs, speed = _read_progress(pfile)
            if secs is not None:
                parts = []
                if duration:
                    if speed:
                        parts.append(f"{speed:.1f}x")
                        eta = int(max(0.0, duration - secs) / speed)
                        parts.append(f"ETA {eta // 60:02d}:{eta % 60:02d}")
                    bar.set(pct=min(99.9, secs / duration * 100), tail="  ".join(parts), val=speed)
                else:
                    if speed:
                        parts.append(f"{speed:.1f}x")
                    parts.append(f"t={int(secs) // 60:02d}:{int(secs) % 60:02d}")
                    bar.set(tail="  ".join(parts), indeterminate=True, val=speed)
            bar.kick()
            time.sleep(0.25)
    except BaseException:
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception as _ign:
            ignore("drain_err", _ign)
        raise
    finally:
        if errfh is not None:
            try:
                errfh.close()
            except Exception as _ign:
                ignore("drain_err", _ign)
    drain_err()
    ok = proc.returncode == 0
    dbg("ffmpeg salida", {"codigo": proc.returncode, "segundos": round(time.time() - t0, 1),
                          "bytes_salida": os.path.getsize(dst) if os.path.isfile(dst) else 0})
    err = ""
    try:
        err = read_text(efile).strip()[-300:]
    except Exception as _ign:
        ignore("ffmpeg_progress", _ign)
    for f in (pfile, efile):
        try:
            os.remove(f)
        except OSError as _ign:
            ignore("drain_err", _ign)
    if not ok:
        raise RuntimeError(err or f"ffmpeg terminó con código {proc.returncode}")
    bar.set(pct=100.0, tail="")


def make_track_pp(labels, bar=None):
    from yt_dlp.postprocessor import FFmpegPostProcessor

    class TrackFixPP(FFmpegPostProcessor):
        def run(self, info):
            dur = info.get("duration")
            path = info.get("filepath")
            if not path or not os.path.exists(path):
                return [], info
            root, ext = os.path.splitext(path)
            tmp = root + ".fix" + ext
            opts = ["-map", "0", "-c", "copy"]
            for i, label in enumerate(labels):
                opts += [f"-disposition:a:{i}", "default" if i == 0 else "0",
                         f"-metadata:s:a:{i}", f"title={label}"]
            dbg("ajuste de pistas", {"archivo": path, "etiquetas": labels, "duracion": dur})
            try:
                if bar is not None:
                    ffmpeg_progress(self, path, tmp, opts, dur, bar)
                else:
                    self.run_ffmpeg(path, tmp, opts)
                os.replace(tmp, path)
            except Exception as e:
                m_warn(f"No se pudo ajustar la pista predeterminada: {e}")
                if os.path.exists(tmp):
                    os.remove(tmp)
            return [], info

    return TrackFixPP()


# ───────── [D2] Compatibilidad Apple: conversión opcional ─────────
MP4_ACODEC = ("mp4a", "aac", "alac", "mp3", "ac-3", "ec-3", "ac3", "eac3")
HEVC_CODEC = ("hvc1", "hev1", "hevc")


def _short(codec):
    return (codec or "?").split(".")[0]


def apple_plan(kind, fmt, selected, merge_ext):
    """Qué haría falta para que el resultado final sea nativo en Apple.
    None si ya lo es; si no, un plan con lo que se recodifica o se remuxa.
    Si hay merge pero video + audios + contenedor resultante ya son
    compatibles, tampoco se ofrece conversión.
"""
    if kind == "a":
        if apple_audio(fmt):
            return None
        v, auds = None, [fmt]
    else:
        v = fmt
        if selected:
            auds = [t["fmt"] for t in selected]
        else:
            auds = [fmt] if has(fmt.get("acodec")) else []
        # Atajo: sin merge y el propio formato ya es Apple → nada que hacer
        if not merge_ext and apple_video(fmt) and (not auds or all(apple_audio(a) for a in auds)):
            return None
    ext = "m4a" if v is None else "mp4"
    cur = (merge_ext or fmt.get("ext") or "").lower()
    vcodec = ((v or {}).get("vcodec") or "").lower()
    venc = v is not None and not vcodec.startswith(APPLE_VCODEC)
    aenc = [not (f.get("acodec") or "").lower().startswith(MP4_ACODEC) for f in auds]
    remux = cur not in (APPLE_VEXT if v is not None else APPLE_AEXT)
    if not (venc or any(aenc) or remux):
        return None
    vbr = (v or {}).get("vbr") or (v or {}).get("tbr") or 4000
    bits = detect_bit_depth(v) if v is not None else None
    hdr = detect_hdr(v) if v is not None else None
    return {"ext": ext, "cur": cur or "?",
            "vsrc": _short(vcodec) if v is not None else None,
            "venc": venc,
            "hvc": v is not None and not venc and vcodec.startswith(HEVC_CODEC),
            "vbr": int(min(30000, max(500, vbr))),
            "asrc": [_short(f.get("acodec")) for f in auds], "aenc": aenc,
            "abr": 256 if any(abr_of(f) >= 200 for f in auds) else 192,
            "labels": [track_label(t) for t in selected] if (selected and v is not None) else [],
            "remux": remux,
            "height": (v or {}).get("height") or 0,
            "fps": (v or {}).get("fps") or 0,
            "bits": bits,          # None = no detectado; no se asume 10 por HDR
            "hdr": hdr,
            "out_bits": min(encode_bits(bits), 10)}   # profundidad de salida (la elige el usuario al convertir)


# ───────────────────── [D3] Bits, HDR y sondeo del video ─────────────────────
def detect_bit_depth(fmt):
    """Profundidad de bits del formato si se puede saber; None si no hay dato claro.
    No asume 10 solo por ser HDR."""
    if not fmt:
        return None
    for k in ("bit_depth", "bits"):
        try:
            n = int(fmt.get(k))
            if 6 <= n <= 16:
                return n
        except (TypeError, ValueError):
            pass
    blob = " ".join(str(fmt.get(k) or "") for k in
                    ("format_note", "format", "format_id", "vcodec")).lower()
    m = re.search(r"\b(6|8|9|10|12|14|16)\s*-?\s*bits?\b|\bmain(10|12)\b|\bp(10|12)\b|\bhip(10|12)\b", blob)
    if m:
        return int(next(g for g in m.groups() if g))
    return codec_bit_depth(fmt.get("vcodec"))


def encode_bits(bits):
    """Profundidad con la que se codifica un origen de `bits`: ≤8 → 8 (el mínimo de HEVC/H.264),
    9-10 → 10, 11 o más → 12 (lo máximo que hace x265)."""
    try:
        b = int(bits or 0)
    except (TypeError, ValueError):
        return 8
    return 8 if b <= 8 else 10 if b <= 10 else 12


def out_pix(bits):
    """pix_fmt de ffmpeg para codificar a `bits`."""
    return {8: "yuv420p", 10: "yuv420p10le", 12: "yuv420p12le"}[encode_bits(bits)]


def bits_choices(bits):
    """[(bits_salida, texto)] que se ofrecen al convertir un origen de más de 8 bits.
    Apple reproduce HEVC hasta 10 bits: con 11 o más la original es la 1.ª y la segura la 2.ª."""
    top = encode_bits(bits)
    out = []
    if top > 10:
        out.append((top, f"{top} bits"
                    + (f" (origen de {bits})" if bits != top else " (original)")
                    + " · Apple normalmente no lo reproduce"))
    out.append((10, "10 bits" + (" (original)" if bits in (9, 10) else "") + " · compatible con Apple"))
    out.append((8, "8 bits · más rápido, menos precisión de color"))
    return out


def codec_bit_depth(codec):
    """Profundidad de bits que declara la cadena del códec (RFC 6381), o None si no dice.
    VP9 vp09.PP.LL.BB / vp9.2 · AV1 av01.P.LLT.BB · HEVC hvc1/hev1.P… (perfil 2 = Main 10)
    · H.264 avc1.PPCCLL (High 10 / 4:2:2 / 4:4:4) · Dolby Vision dvh1/dvhe.PP.
    Los perfiles de H.264/HEVC admiten 10 bits pero podrían llevar 8: se marca por perfil."""
    c = (codec or "").strip().lower()
    if not c or c == "none":
        return None
    parts = c.split(".")
    head, rest = parts[0], parts[1:]

    def num(x):
        try:
            return int(x)
        except (TypeError, ValueError):
            return None

    if head in ("vp09", "vp9"):
        if len(rest) >= 3 and num(rest[2]) in (8, 10, 12):
            return num(rest[2])
        prof = num(rest[0]) if rest else None
        return 10 if prof in (2, 3) else 8 if prof in (0, 1) else None
    if head == "av01":
        return num(rest[2]) if len(rest) >= 3 and num(rest[2]) in (8, 10, 12) else None
    if head in ("hvc1", "hev1"):
        prof = rest[0].lstrip("abc") if rest else ""
        return 10 if num(prof) == 2 else 8 if num(prof) == 1 else None
    if head in ("dvh1", "dvhe"):
        prof = num(rest[0]) if rest else None
        return 10 if prof in (4, 5, 7, 8, 10) else 8 if prof == 9 else None
    if head in ("avc1", "avc3") and rest and re.fullmatch(r"[0-9a-f]{6}", rest[0]):
        prof = int(rest[0][:2], 16)
        return 10 if prof in (0x6E, 0x7A, 0xF4) else 8 if prof in (0x42, 0x4D, 0x58, 0x64) else None
    return None


def range_label(fmt):
    """Etiqueta corta del rango del video para la lista: «8b», «10b», «10b HDR10», «HDR10» o ""
    (los bits se muestran siempre que se conocen). Sin profundidad detectada solo se muestra el HDR."""
    bits = detect_bit_depth(fmt)
    parts = []
    if bits:
        parts.append(f"{bits}b")
    hdr = detect_hdr(fmt)
    if hdr:
        parts.append(hdr)
    return " ".join(parts)


def detect_hdr(fmt):
    """Etiqueta HDR legible si el formato lo declara; None si no / SDR."""
    if not fmt:
        return None
    dr = str(fmt.get("dynamic_range") or "").strip().upper()
    if dr and dr not in ("SDR", "NONE", "N/A"):
        return dr
    blob = " ".join(str(fmt.get(k) or "") for k in
                    ("format_note", "format")).lower()
    for tag in ("hdr10+", "hdr10", "hlg", "dolby vision", "dvhe", "hdr"):
        if tag in blob:
            return tag.upper().replace("DOLBY VISION", "DV")
    return None


def plan_summary(plan):
    parts = []
    if plan["venc"]:
        parts.append(f"video {plan['vsrc']} → HEVC")
    enc = sorted({s for s, e in zip(plan["asrc"], plan["aenc"]) if e})
    if enc:
        parts.append(f"audio {'/'.join(enc)} → AAC")
    if plan["remux"]:
        parts.append(f"contenedor {plan['cur']} → {plan['ext']}")
    bits = plan.get("bits")
    out_b = plan.get("out_bits") or 8
    if bits and plan["venc"] and out_b != bits:
        parts.append(f"{bits}-bit → {out_b}-bit")
    elif bits and bits >= 9:
        parts.append(f"{bits}-bit")
    elif plan.get("hdr"):
        parts.append(str(plan["hdr"]))
    return " · ".join(parts) or f"contenedor → {plan['ext']}"


# Umbral (s) bajo el cual se convierte sin preguntar. ~1 min en el iPhone.
CONVERT_QUICK_SECS = 60
# Velocidad de referencia: ~2.5× tiempo real a 1080p30 con hevc_videotoolbox.
CONVERT_BASE_SPEED = 2.5


def conv_scale(plan):
    """Coste relativo a 1080p30 (mínimo 0.15): crece con el cuadrado de la altura y con los fps."""
    h = float(plan.get("height") or 0) or 720.0
    fps = float(plan.get("fps") or 0) or 30.0
    return max(0.15, (h / 1080.0) ** 2 * (fps / 30.0))


def measured_conv_speed(index=None):
    """Velocidad de conversión REAL de este equipo: mediana de las últimas conversiones con recodificación
    guardadas en el índice («conv.speed» = segundos de video × coste relativo ÷ segundos que tardó). Sin historial
    vale CONVERT_BASE_SPEED."""
    try:
        idx = load_json(INDEX_FILE) if index is None else index
        rows = []
        for e in idx.values():
            cv = ((e or {}).get("meta") or {}).get("conv") or {}
            if cv.get("speed"):
                rows.append((e.get("date") or 0, float(cv["speed"])))
        rows.sort()
        vals = sorted(v for _, v in rows[-5:])
        if vals:
            return min(40.0, max(0.5, vals[len(vals) // 2]))
    except Exception as _ign:
        ignore("measured_conv_speed", _ign)
    return CONVERT_BASE_SPEED


def guess_duration(info, fmt=None):
    """Duración (s) del video: la del análisis; si falta, la del formato; si no, tamaño ÷ bitrate. None si nada."""
    for src in (info or {}, fmt or {}):
        try:
            d = float(src.get("duration") or 0)
            if d > 0:
                return d
        except (TypeError, ValueError):
            pass
    try:
        size = float((fmt or {}).get("filesize") or (fmt or {}).get("filesize_approx") or 0)
        kbps = float((fmt or {}).get("tbr") or (fmt or {}).get("vbr") or 0)
        if size > 0 and kbps > 0:
            return size * 8 / (kbps * 1000)
    except (TypeError, ValueError):
        pass
    return None


def convert_est_secs(plan, duration, speed=None):
    """Segundos estimados de conversión, o None si no se puede estimar.
    Sin recodificar video (solo remux/audio) ≈ 0. Con venc: duración × coste
    relativo a 1080p30 ÷ velocidad (CONVERT_BASE_SPEED o la medida en este equipo)."""
    if not plan.get("venc"):
        return 0.0
    try:
        dur = float(duration or 0)
    except (TypeError, ValueError):
        return None
    if dur <= 0:
        return None
    return dur * conv_scale(plan) / (speed or CONVERT_BASE_SPEED)


def convert_is_quick(plan, duration, limit=CONVERT_QUICK_SECS, speed=None):
    """True si la conversión debería acabar en ≤ limit segundos (o no hay venc)."""
    est = convert_est_secs(plan, duration, speed)
    return est is not None and est <= limit


def video_encoder_attempts(plan):
    """[(códec_corto, nombre_legible, opciones)] a probar en orden; la primera
    que funcione se queda. out_bits del plan (8, 10 o 12) elige el pix_fmt y el perfil.
    VideoToolbox solo hace 8 y 10 bits; con 12 se prueba x265 y, si no puede, se baja a 10 y a 8.
    El nombre se imprime como «Usando …»; la barra usa una etiqueta corta."""
    if not plan["venc"]:
        tag = ["-tag:v", "hvc1"] if plan.get("hvc") else []
        return [(None, "remux (sin recodificar video)", ["-c:v", "copy"] + tag)]
    b = f"{plan['vbr']}k"
    ob = encode_bits(plan.get("out_bits"))

    def vt_opts(bits):
        o = ["-c:v", "hevc_videotoolbox", "-b:v", b, "-allow_sw", "1",
             "-tag:v", "hvc1", "-pix_fmt", out_pix(bits)]
        return o + (["-profile:v", "main10"] if bits == 10 else [])

    def x265_opts(bits):
        o = ["-c:v", "libx265", "-preset", "veryfast", "-crf", "26",
             "-tag:v", "hvc1", "-pix_fmt", out_pix(bits)]
        return o + (["-x265-params", f"profile=main{bits}"] if bits > 8 else [])

    x264 = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
            "-pix_fmt", "yuv420p"]          # H.264 High 10 casi no se usa en Apple
    if ob == 12:
        return [("hevc", "x265 12 bits", x265_opts(12)),
                ("hevc", "VideoToolbox HEVC 10 bits", vt_opts(10)),
                ("hevc", "x265 10 bits", x265_opts(10)),
                ("h264", "x264", x264)]
    return [("hevc", "VideoToolbox HEVC", vt_opts(ob)),
            ("hevc", "x265", x265_opts(ob)),
            ("h264", "x264", x264)]


def apple_ffmpeg_opts(plan, vopts):
    opts = []
    if plan["vsrc"] is not None:
        opts += ["-map", "0:v:0"]
    opts += ["-map", "0:a?"]
    opts += vopts if plan["vsrc"] is not None else ["-vn"]
    # Regla general primero y las excepciones (copiar) después: gana la última
    opts += ["-c:a", "aac", "-b:a", f"{plan['abr']}k"]
    for i, enc in enumerate(plan["aenc"]):
        if not enc:
            opts += [f"-c:a:{i}", "copy"]
    # Nombre y pista predeterminada: ffmpeg no siempre los conserva al recodificar
    for i, label in enumerate(plan.get("labels") or []):
        opts += [f"-disposition:a:{i}", "default" if i == 0 else "0",
                 f"-metadata:s:a:{i}", f"title={label}",
                 f"-metadata:s:a:{i}", f"handler_name={label}"]
    opts += ["-movflags", "+faststart"]
    return opts


def pix_bits(pix):
    """Bits por componente de un pix_fmt de ffmpeg (yuv420p → 8, yuv420p10le → 10, p010le → 10),
    o None si no se reconoce."""
    p = (pix or "").strip().lower()
    m = re.search(r"(?:p|gbrp|gray|gbrap|yuva\d{3}p)(9|10|12|14|16)(?:le|be)?$", p) or \
        re.match(r"^p0?(10|12|16)(?:le|be)?$", p)
    if m:
        return int(m.group(1))
    if p.startswith(("yuv", "nv", "gbrp", "gray", "rgb", "bgr", "argb", "abgr", "rgba", "bgra")):
        return 8
    return None


def parse_ffmpeg_video(text):
    """Primer stream de video de la salida de «ffmpeg -i»: {codec, profile, pix_fmt, bits} o None."""
    line = next((ln for ln in (text or "").splitlines() if "Video:" in ln), None)
    if not line:
        return None
    body = line.split("Video:", 1)[1]
    m = re.match(r"\s*(\w+)(?:\s+\(([^)/]*)\))?", body)
    pm = re.search(r",\s*((?:yuvj?|nv|p0|gbrp|gray|rgb|bgr|argb|abgr|rgba|bgra)[a-z0-9_]*)", body)
    pix = pm.group(1) if pm else None
    out = {"codec": m.group(1) if m else None, "profile": (m.group(2) or None) if m else None,
           "pix_fmt": pix, "bits": pix_bits(pix)}
    km = re.search(r",\s*(\d+)\s*kb/s", body)
    if km:
        out["kbps"] = int(km.group(1))
    return out


def probe_video(exe, path, timeout=20):
    """Lee el video de `path`: {codec, profile, pix_fmt, bits} o None si no se pudo. Usa
    ffprobe (junto a ffmpeg o en el PATH) y, si no hay, «ffmpeg -i»."""
    import subprocess
    exe = exe or shutil.which("ffmpeg")
    cands = []
    if exe:
        d, n = os.path.split(exe)
        cands.append(os.path.join(d, n.lower().replace("ffmpeg", "ffprobe")) if d else None)
    cands.append(shutil.which("ffprobe"))
    for pr in dict.fromkeys(c for c in cands if c):
        try:
            r = subprocess.run([pr, "-v", "error", "-select_streams", "v:0", "-show_entries",
                                "stream=codec_name,profile,pix_fmt,bits_per_raw_sample,bit_rate", "-of", "json",
                                "file:" + path], capture_output=True, text=True, timeout=timeout)
            st = (json.loads(r.stdout or "{}").get("streams") or [None])[0]
            if st:
                bits = pix_bits(st.get("pix_fmt"))
                try:
                    bits = bits or int(st.get("bits_per_raw_sample"))
                except (TypeError, ValueError):
                    pass
                out = {"codec": st.get("codec_name"), "profile": st.get("profile"),
                       "pix_fmt": st.get("pix_fmt"), "bits": bits}
                try:
                    out["kbps"] = int(round(int(st.get("bit_rate")) / 1000.0))
                except (TypeError, ValueError):
                    pass
                return out
        except Exception as _ign:
            ignore("probe_video ffprobe", _ign)
    if exe:
        try:
            r = subprocess.run([exe, "-hide_banner", "-i", "file:" + path], capture_output=True,
                               text=True, timeout=timeout, stdin=subprocess.DEVNULL)
            return parse_ffmpeg_video(r.stderr)
        except Exception as _ign:
            ignore("probe_video ffmpeg", _ign)
    return None


def probe_stream_bits(exe, fmt, timeout=12):
    """Bits del stream de video de `fmt` leyendo su cabecera con ffmpeg (sin descargarlo).
    None si no hay ffmpeg, el formato no es un enlace http(s) o la lectura falla o tarda."""
    import subprocess
    url = str((fmt or {}).get("url") or "")
    if not exe or not url.lower().startswith(("http://", "https://")):
        return None
    cmd = [exe, "-hide_banner", "-nostdin"]
    hd = (fmt or {}).get("http_headers")
    if isinstance(hd, dict) and hd:
        cmd += ["-headers", "".join(f"{k}: {v}\r\n" for k, v in hd.items())]
    cmd += ["-i", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           stdin=subprocess.DEVNULL)
        return (parse_ffmpeg_video(r.stderr) or {}).get("bits")
    except Exception as _ign:
        ignore("probe_stream_bits", _ign)
        return None


def conversion_bits(plan, used, probed):
    """Bits del video convertido: lo leído del archivo; si no se pudo, lo deducido del encoder
    (x264 → 8; HEVC → lo pedido). None si no hubo video recodificado ni lectura."""
    if probed and probed.get("bits"):
        return probed["bits"]
    if not plan.get("venc") or plan.get("vsrc") is None:
        return None
    return 8 if used == "h264" else encode_bits(plan.get("out_bits"))


def bits_warning(want, got, used=None):
    """Aviso si se pidieron `want` bits (≥10) y el video quedó con menos; None si todo bien."""
    if not want or want < 10 or not got or got >= want:
        return None
    return (f"Se pidieron {want} bits pero el video quedó en {got} bits"
            + (" (x264 solo hace 8 bits)." if used == "h264" else "."))


def convert_done(plan, used):
    """Mensaje final de una conversión Apple, con la profundidad de bits real."""
    bits = conversion_bits(plan, used, plan.get("result"))
    parts = ([used.upper()] if used else []) + ([f"{bits} bits"] if bits else [])
    if plan.get("remux_forced"):
        m_ok(f"Remux a {plan['ext'].upper()}: video sin recodificar (puede no verse en Apple)")
        return
    m_ok(f"Convertido a {plan['ext'].upper()} compatible con Apple"
         + (f" ({' · '.join(parts)})" if parts else ""))
    if plan.get("venc"):
        w = bits_warning(plan.get("out_bits"), bits, used)
        if w:
            m_warn(w)


def apple_convert_file(pp, path, plan, dur, bar, out_path):
    """Convierte path → out_path probando los encoders en orden. Devuelve el
    códec de video usado (None si no hubo recodificación) o lanza RuntimeError.
    Antes de cada intento: «Usando …»; la barra queda genérica (Conv. / Remux)."""
    root, ext = os.path.splitext(out_path)
    tmp = root + ".apple" + ext
    if plan.get("venc") and plan.get("vsrc") is not None and not plan.get("bits"):
        real = probe_video(getattr(pp, "executable", None), path)     # nunca se pudo saber antes: se lee el archivo
        rb = (real or {}).get("bits")
        if rb:
            plan["bits"] = rb
            keep = min(encode_bits(rb), 10)
            if rb > 8:
                plan["out_bits"] = keep
                m_info(f"El archivo descargado es de {rb} bits: se conservan"
                       + (f" como {keep} bits (lo máximo que reproduce Apple)." if keep != rb else "."))
    if plan.get("vsrc") is not None:
        vsets = video_encoder_attempts(plan)
    else:
        vsets = [(None, "AAC (audio)", [])]
    err, used, ok = None, None, False
    prev_name = None
    t_start = time.time()
    plan.pop("engine", None)
    for vcodec, name, vopts in vsets:
        try:
            aopts = apple_ffmpeg_opts(plan, vopts)
            dbg("intento de conversión", {"video": vcodec, "name": name, "opciones": aopts})
            if prev_name:
                m_warn(f"{prev_name} no disponible; probando {name}")
            m_info(f"Usando {name}")
            if vcodec is None and not plan.get("venc") and plan.get("vsrc") is not None:
                bar_label = "Remux"
            elif vcodec is None:
                bar_label = "Convirtiendo · audio"
            else:
                ob = plan.get("out_bits")
                bar_label = "Convirtiendo · " + ("HEVC" if plan.get("venc") else "video") \
                    + (f" {ob} bits" if ob and ob > 8 else "")
            if bar is not None:
                bar.reset(bar_label)
                if vcodec is not None and plan.get("venc"):
                    bar.set(engine=name.split()[0])
                ffmpeg_progress(pp, path, tmp, aopts, dur, bar)
            else:
                pp.run_ffmpeg(path, tmp, aopts)
            if os.path.isfile(tmp) and os.path.getsize(tmp) > 0:
                used, ok = vcodec, True
                if vcodec is not None and plan.get("venc"):
                    plan["engine"] = name.split()[0]        # VideoToolbox / x265 / x264
                break
            err = "archivo vacío"
        except Exception as e:
            err = e
            dbg("intento fallido", {"video": vcodec, "name": name, "error": str(e)[-300:]})
        prev_name = name
        if os.path.exists(tmp):
            os.remove(tmp)
    if not ok:
        raise RuntimeError(str(err))
    plan["result"] = (probe_video(getattr(pp, "executable", None), tmp)
                      if plan.get("vsrc") is not None else None)
    dbg("video convertido", plan["result"])
    plan["secs"] = int(round(time.time() - t_start))
    try:                                  # velocidad real para estimar las próximas (solo con recodificación)
        real = time.time() - t_start
        if plan.get("venc") and dur and float(dur) > 0 and real >= 3:
            plan["speed"] = round(float(dur) * conv_scale(plan) / real, 2)
    except (TypeError, ValueError) as _ign:
        ignore("apple_convert_file", _ign)
    os.replace(tmp, out_path)
    return used


def conv_info(plan, used):
    """Datos de una conversión terminada para el índice (los comparten la descarga y la reconversión)."""
    d = {"venc": plan["venc"], "vcodec": used, "aenc": list(plan["aenc"]),
         "bits": conversion_bits(plan, used, plan.get("result"))}
    kb = (plan.get("result") or {}).get("kbps")
    if kb:
        d["vbr"] = kb
    if plan.get("engine"):
        d["engine"] = plan["engine"]
    if plan.get("secs") is not None:
        d["secs"] = plan["secs"]
    if plan.get("speed"):
        d["speed"] = plan["speed"]
    if plan.get("remux") and plan.get("cur"):
        d["cfrom"] = plan["cur"]
    if plan.get("remux_forced"):
        d["forced"] = True                      # el usuario pidió remux aunque el video no sea nativo en Apple
    if plan.get("abr"):
        d["abr"] = plan["abr"]                  # bitrate AAC con el que quedó el audio recodificado
    return d


def make_apple_pp(plan, state, bar=None):
    from yt_dlp.postprocessor import FFmpegPostProcessor

    class AppleConvertPP(FFmpegPostProcessor):
        def run(self, info):
            path = info.get("filepath")
            if not path or not os.path.exists(path):
                return [], info
            ext = plan["ext"]
            dest = os.path.splitext(path)[0] + "." + ext
            try:
                used = apple_convert_file(self, path, plan, info.get("duration"), bar, dest)
            except Exception as e:
                m_warn(f"No se pudo convertir a compatible Apple: {e}")
                return [], info
            info["filepath"] = dest
            info["ext"] = ext
            state.update(conv_info(plan, used), path=dest)
            return ([path] if dest != path else []), info

    return AppleConvertPP()


class _FfmpegShim:
    """Sustituto mínimo de un post-procesador para ffmpeg_progress fuera de yt-dlp."""

    def __init__(self):
        exe = None
        try:
            from yt_dlp.postprocessor import FFmpegPostProcessor
            exe = getattr(FFmpegPostProcessor(), "executable", None)
        except Exception as _ign:
            ignore("__init__", _ign)
        self.executable = exe or shutil.which("ffmpeg") or "ffmpeg"

    def run_ffmpeg(self, *a, **k):
        raise RuntimeError("no se pudo lanzar ffmpeg")


# ───────────────────── [D4] Ya descargado: reutilizar o convertir ─────────────────────
def reuse_downloaded(old_file, old_entry, index, key, title, info, kind, fmt, fmt_id,
                     selected, orig_ids, plan):
    """Aprovecha el archivo ya descargado. True si resolvió la petición (entregó
    el archivo); False si hay que descargar de nuevo.
    - Mismos parámetros (formato/pistas y misma decisión de conversión): pregunta «¿Descargar de nuevo?» (Sí por
      omisión) y, si no, se entrega tal cual. Otra elección: no pregunta y descarga.
    - Mismos streams, archivo sin convertir y ahora se pide convertir: se convierte ese archivo.
    - Si el archivo ya está convertido y ahora no se quiere conversión (o al
      revés y no queda el original), se fuerza re-descarga."""
    meta = (old_entry or {}).get("meta") or {}
    old_conv, want_conv = bool(meta.get("converted")), bool(plan)
    same_mode = conv_mode(meta) == conv_mode({}, plan or {})        # remux («r») ≠ conversión completa
    dbg("reutilizar", {"archivo": old_file, "format_id_antiguo": meta.get("format_id"),
                       "format_id_nuevo": fmt_id, "convertido_antes": old_conv,
                       "convertir_ahora": want_conv})
    if not old_file:
        return False
    if str(meta.get("format_id")) != str(fmt_id):
        return False                      # otra elección: se descarga sin preguntar
    if old_conv == want_conv and same_mode:
        # Misma elección que el archivo que ya tienes: aquí sí tiene sentido preguntar
        clear_screen()
        show_existing(old_file, old_entry, title=title)
        print()
        try:
            # seconds=None: mismo método de entrada (sin cuenta regresiva) que «¿Abrir otra vez?» y las demás
            # preguntas; con seconds=False usaba input() y en a-Shell se congelaba
            again = ask_yn("¿Descargar de nuevo? (S/n) ▸ ", default=True, seconds=None)
        except (EOFError, KeyboardInterrupt):
            m_info("Cancelado.")
            return True
        if again:
            m_info("Se descargará de nuevo.")
            return False
        m_ok("Se reutiliza el archivo ya descargado.")
        deliver_existing(old_file, old_entry, title)
        return True
    # Aquí old_conv != want_conv. Si ya estaba convertido y ahora se quiere el
    # original, no queda el archivo sin convertir: se vuelve a descargar.
    if old_conv or want_conv and not same_mode:
        return False

    m_info("Mismos streams ya descargados: se convierte ese archivo sin volver a bajarlo.")
    work_dir = os.path.join(WORK_ROOT, uuid.uuid4().hex[:12])
    os.makedirs(work_dir, exist_ok=True)
    out = os.path.join(work_dir, os.path.splitext(os.path.basename(old_file))[0]
                       + "." + plan["ext"])
    clear_screen()
    show_title(title)
    hide_keyboard()
    bar = Bar(panel=True)
    bar.start("Convirtiendo")
    try:
        used = apple_convert_file(_FfmpegShim(), old_file, plan, info.get("duration"), bar, out)
    except KeyboardInterrupt:
        bar.stop()
        cleanup_work(work_dir)
        m_err("Conversión cancelada.")
        return True
    except Exception as e:
        bar.stop()
        cleanup_work(work_dir)
        m_warn(f"No se pudo convertir el archivo existente: {e}")
        m_info("Se descargará de nuevo.")
        return False
    bar.done(min_secs=0.5)

    final = os.path.join(DOWNLOAD_DIR, os.path.basename(out))
    try:
        move_file(out, final)
        if os.path.abspath(final) != os.path.abspath(old_file):
            os.remove(old_file)
    except Exception as e:
        cleanup_work(work_dir)
        m_err(f"No se pudo guardar el archivo convertido: {e}")
        return True
    cleanup_work(work_dir)
    convert_done(plan, used)
    conv = conv_info(plan, used)
    index[key] = {"file": os.path.basename(final), "title": title,
                  "date": int(time.time()), "version": VERSION,
                  "meta": build_meta(kind, fmt, fmt_id, selected, orig_ids, final, conv, info)}
    try:
        save_json(INDEX_FILE, index)
    except Exception as e:
        m_warn(f"No se pudo guardar el índice: {e}")
    history_add(key, index[key])
    deliver(final, title)
    return True


def ask_keep_bits(plan, est, slow):
    """Pregunta si conservar los bits originales (origen de más de 8 bits) y avisa qué cambia.
    Pone plan['out_bits']. Devuelve el plan o None si se cancela."""
    bits, hdr = plan["bits"], plan.get("hdr")
    if not slow:                    # conversión rápida (≤ CONVERT_QUICK_SECS) = no se pregunta nada
        ch = bits_choices(bits)
        plan["out_bits"] = ch[1][0] if len(ch) == 3 else ch[0][0]      # la mayor que Apple reproduce (10)
        plan["asked_bits"] = False
        m_info(f"Conversión rápida (~{max(1, int(round(est or 0)))} s estimados): se convierte sin preguntar"
               f" y se conservan {plan['out_bits']} bits"
               + (f" (origen de {bits})." if bits != plan["out_bits"] else "."))
        return plan
    note(f"El video de origen es de {bits} bits" + (f" · {hdr}" if hdr else "") + ".")
    if est is not None and est > 0:
        note(f"Estimación ~{int(round(est))} s a 8 bits; con más bits tarda algo más.")
    choices = bits_choices(bits)
    low = ("Puede verse con bandas en cielos y degradados"
           + (f" y el {hdr} puede verse apagado." if hdr else "."))
    if len(choices) == 2:                       # 9 o 10 bits: sí / no
        keep = choices[0][0]
        note(f"Conservar {keep} bits: degradados suaves"
             + (f" y se mantiene el {hdr}" if hdr else "")
             + f"; los dispositivos Apple recientes lo reproducen bien. Tarda más"
             + (f" (un origen de {bits} bits se guarda como {keep})." if bits != keep else "."))
        note(f"A 8 bits: más rápido, pero pierde precisión de color. {low}")
        try:
            r = ask_yn(f"¿Conservar {keep} bits?", default=not slow, seconds=WAIT_SECONDS)
        except (EOFError, KeyboardInterrupt):
            m_info("Conversión cancelada; se descargará sin convertir.")
            return None
        yes = (not slow) if r is None else r
        plan["out_bits"] = keep if yes else 8
    else:                                       # 11 o más bits: tres opciones
        note("Apple reproduce HEVC de hasta 10 bits; con 12 el archivo puede no abrirse en Apple.")
        note(f"Con 10 bits se pierde algo de precisión de color; con 8 más. {low}")
        default_n = 2
        for n, (_, txt) in enumerate(choices, 1):
            on = n == default_n                 # la que vale con Enter o al acabar la cuenta
            print((paint("▸", "orange") if on else " ") + paint(f"{n}", "orange", True) + "  "
                  + (paint(txt, "white", True) if on else txt))
        hint(f"Opción 1-{len(choices)} · {{Enter = {default_n}}}")
        cur = PROMPT
        while True:
            try:
                raw = timed_input(cur, WAIT_SECONDS, True, f"Opción (Enter = {default_n}) ▸ ")
            except (EOFError, KeyboardInterrupt):
                m_info("Conversión cancelada; se descargará sin convertir.")
                return None
            typed = raw
            raw = default_n if raw is None or not str(raw).strip() else str(raw).strip()
            if str(raw).isdecimal() and 1 <= int(raw) <= len(choices):
                plan["out_bits"] = choices[int(raw) - 1][0]
                break
            cur = retry_prompt(cur, typed or "", bad_prompt(f"1-{len(choices)}"),
                               f"Escribe un número del 1 al {len(choices)}.")
    plan["asked_bits"] = True
    ob = plan["out_bits"]
    m_info(f"Se convertirá a {ob} bits." if ob != bits else f"Se conservarán {ob} bits.")
    return plan


def ask_apple_convert(plan, can_merge, duration=None, fmt=None):
    """Avisa de que no es nativo en Apple y pregunta (o convierte solo si es
    rápido: ≤ CONVERT_QUICK_SECS estimados, sin ninguna pregunta). Devuelve el plan o None. Si es lenta
    pregunta «¿Convertir?» y, con un video de más de 8 bits, si conservarlos."""
    clear_screen()
    header("COMPATIBILIDAD APPLE", gap=False)
    m_warn("Este resultado no es compatible con Apple.")
    if not can_merge:
        kv("Conversión", plan_summary(plan))
        m_info("No hay ffmpeg para convertir; se descargará tal cual.")
        return None
    if plan.get("venc") and not plan.get("bits") and fmt:
        note("Leyendo los bits del video de origen…")
        got = probe_stream_bits(_FfmpegShim().executable, fmt)
        if got:
            plan["bits"] = got
            plan["out_bits"] = min(encode_bits(got), 10)
    kv("Conversión", plan_summary(plan))
    speed = measured_conv_speed()
    est = convert_est_secs(plan, duration, speed)
    bits = plan.get("bits")
    slow = not convert_is_quick(plan, duration, speed=speed)
    dbg("estimación de conversión", {"duracion": duration, "velocidad": speed, "estimado_s": est,
                                     "rapida": not slow, "limite_s": CONVERT_QUICK_SECS})
    plan["asked_bits"] = False

    # Conversión lenta (> CONVERT_QUICK_SECS): SIEMPRE se pregunta «¿Convertir?» primero, también con
    # origen de más de 8 bits (así se puede rechazar antes de llegar a «¿Conservar N bits?»).
    if slow:
        if plan["venc"]:
            note("Recodificar el video a HEVC puede tardar bastante en el iPhone.")
            if est is not None:
                note(f"Estimación ~{int(round(est))} s (umbral de pregunta: {CONVERT_QUICK_SECS} s).")
            if not bits:
                note("No se pudieron detectar los bits del origen; si el archivo resulta tener más de 8 se "
                     "conservan (hasta 10)."
                     + (f" Origen {plan['hdr']}." if plan.get("hdr") else ""))
        if countdown_supported():
            hint(f"{{Enter = convertir}} · r = solo remux · {WAIT_SECONDS} s")
        try:
            r = ask_yn("¿Convertir? (S/n) ▸ ", default=True, seconds=WAIT_SECONDS,
                       alt=("r", "Remux") if plan.get("venc") else None)
        except (EOFError, KeyboardInterrupt):
            m_info("Conversión cancelada; se descargará sin convertir.")
            return None
        if r == "r":                  # remux = cambiar contenedor y audio, SIN recodificar el video
            plan["venc"] = False
            plan["remux_forced"] = True
            plan["asked_bits"] = False
            m_info("Remux: se cambia el contenedor y el audio; el video no se recodifica.")
            return plan
        if r is None:
            m_info("Sin respuesta: se convierte.")
        elif not r:
            return None

    # Recodificación con bits conocidos
    if plan.get("venc") and bits:
        if bits > 8:
            plan = ask_keep_bits(plan, est, slow)
            return plan
        plan["out_bits"] = 8
        note(f"Origen de {bits} bits: se guarda en 8"
             + (" (HEVC y H.264 no bajan de 8 bits; no se pierde nada)." if bits < 8 else "; no se pierde nada."))

    # Conversión rápida: sin preguntar
    if not slow:
        if est is not None and est > 0 and plan.get("venc"):
            m_info(f"Conversión rápida (~{max(1, int(round(est)))} s estimados): se convierte sin preguntar.")
        else:
            m_info("Conversión rápida (solo remux/audio): se convierte sin preguntar.")
        if plan.get("venc") and not bits:
            note("No se pudieron detectar los bits del origen; si el archivo resulta tener más de 8 se "
                 "conservan (hasta 10).")
    return plan


# ╔══════════════════════════════════════════════════════════════════════╗
# ║ ÁREA E · ESTADO Y ENTRADA — JSON, índice, enlace, portapapeles       ║
# ╚══════════════════════════════════════════════════════════════════════╝
# ───────────────────── [E1] JSON / índice ─────────────────────
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            return data if isinstance(data, dict) else {}
    except (OSError, ValueError) as _ign:
        ignore("load_json", _ign)
        return {}


def save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def video_key(info):
    ext = info.get("extractor_key") or info.get("extractor") or "generic"
    vid = info.get("id") or info.get("webpage_url") or ""
    return f"{ext}:{vid}"


def saved_dirs():
    """Carpetas donde puede estar una descarga terminada (destino actual primero)."""
    out = [DOWNLOAD_DIR]
    if os.path.abspath(FILES_DIR) != os.path.abspath(DOWNLOAD_DIR):
        out.append(FILES_DIR)
    return out


def find_saved(name):
    """Ruta de un archivo ya descargado (por nombre del índice) o None."""
    for d in saved_dirs():
        p = os.path.join(d, name)
        if os.path.isfile(p):
            return p
    return None


def indexed_files():
    """Archivos del índice que existen en DOWNLOAD_DIR y no cuelgan de FILES_DIR.
    Son lo único de Descargas que DLpy considera suyo."""
    if os.path.abspath(DOWNLOAD_DIR) == os.path.abspath(FILES_DIR):
        return []
    out = []
    vals = list(load_json(INDEX_FILE).values())
    for lst in load_json(HISTORY_FILE).values():
        vals += lst if isinstance(lst, list) else []
    for v in vals:
        if isinstance(v, dict) and v.get("file"):
            p = os.path.join(DOWNLOAD_DIR, v["file"])
            if os.path.isfile(p) and p not in out:
                out.append(p)
    return out


def history_for(key, index=None):
    """[(ruta, entrada)] de TODO lo descargado de ese video que sigue en disco. Une downloads.json con la
    entrada del índice, que cubre lo bajado antes de existir el historial. El índice solo guarda la última
    descarga de cada video; el historial guarda cada una (otra calidad, solo audio...)."""
    out, seen = [], set()
    entries = list(load_json(HISTORY_FILE).get(key) or [])
    idx = load_json(INDEX_FILE) if index is None else index
    if isinstance(idx.get(key), dict):
        entries.append(idx[key])
    for e in entries:
        if not (isinstance(e, dict) and e.get("file")) or e["file"] in seen:
            continue
        p = find_saved(e["file"])
        if p:
            seen.add(e["file"])
            out.append((p, e))
    return out


def history_add(key, entry):
    """Anota una descarga terminada en downloads.json. Quita las entradas del mismo archivo y las de archivos que
    ya no existen (una descarga repetida de la misma elección reemplaza a la anterior)."""
    try:
        data = load_json(HISTORY_FILE)
        keep = [e for e in (data.get(key) or [])
                if isinstance(e, dict) and e.get("file") and e["file"] != entry.get("file") and find_saved(e["file"])]
        keep.append(entry)
        data[key] = keep
        save_json(HISTORY_FILE, data)
    except Exception as _ign:
        ignore("history_add", _ign)


def conv_mode(meta, plan=None):
    """'' sin conversión · 'remux' (pedido con «r», video sin recodificar) · 'full' conversión normal."""
    if plan is not None:
        return "remux" if plan.get("remux_forced") else ("full" if plan else "")
    if not (meta or {}).get("converted"):
        return ""
    return "remux" if ((meta.get("conv") or {}).get("forced")) else "full"


def history_match(hist, fmt_id, want_conv=None):
    """(ruta, entrada) del historial con EXACTAMENTE esa elección de formato, o (None, None). Si hay varias
    (p. ej. original y convertido) prefiere la que coincide con `want_conv`."""
    hits = [(p, e) for p, e in hist if str(((e.get("meta") or {}).get("format_id"))) == str(fmt_id)]
    if not hits:
        return None, None
    if want_conv is not None:
        for p, e in hits:
            if conv_mode((e.get("meta") or {})) == want_conv:
                return p, e
    return hits[-1]


def lookup_downloaded(idx, key):
    entry = idx.get(key)
    if not isinstance(entry, dict) or not entry.get("file"):
        return None, None
    p = find_saved(entry["file"])
    return (p, entry) if p else (None, None)


def name_taken(base):
    prefix = base + "."
    for d in saved_dirs():
        if not os.path.isdir(d):
            continue
        for n in os.listdir(d):
            if n in RESERVED:
                continue
            if n.startswith(prefix) and not n.endswith((".part", ".ytdl", ".temp")) \
                    and os.path.isfile(os.path.join(d, n)):
                return True
    return False


def build_meta(kind, fmt, fmt_id, selected, orig_ids, final, conv=None, info=None):
    meta = {"kind": "video" if kind == "v" else "audio",
            "container": os.path.splitext(final)[1].lstrip("."),
            "format_id": fmt_id,
            "video": None,
            "tracks": []}
    if kind == "v":
        meta["video"] = {"res": res_label(fmt),
                         "codec": (fmt.get("vcodec") or "?").split(".")[0],
                         "apple": apple_video(fmt)}
        _b = detect_bit_depth(fmt)
        if _b:
            meta["video"]["bits"] = _b          # profundidad del origen (si se conoce)
    if selected:
        for i, t in enumerate(selected):
            f = t["fmt"]
            meta["tracks"].append({
                "lang": t["lang"], "label": track_label(t),
                "codec": (f.get("acodec") or "?").split(".")[0],
                "abr": round(abr_of(f)), "original": t["original"],
                "default": i == 0, "apple": apple_audio(f)})
    elif has(fmt.get("acodec")):
        meta["tracks"].append({
            "lang": fmt.get("language") or "und",
            "label": fmt.get("language") or "audio",
            "codec": (fmt.get("acodec") or "?").split(".")[0],
            "abr": round(abr_of(fmt)),
            "original": fmt["format_id"] in orig_ids,
            "default": True, "apple": apple_audio(fmt)})
    src = source_info(info)
    if src:
        meta["source"] = src                    # sitio y canal de donde se bajó
    vsrc_kbps = source_video_kbps(fmt) if kind == "v" else None
    if meta["video"] and vsrc_kbps and not conv:
        meta["video"]["vbr"] = vsrc_kbps
    if conv:
        meta["converted"] = True
        cv = {}
        if conv.get("forced"):
            cv["forced"] = True                 # remux pedido con «r»: video sin recodificar
        afrom = []
        if meta["video"]:
            if conv.get("venc"):
                cv["vfrom"] = meta["video"].get("codec")
                if meta["video"].get("bits"):
                    cv["bfrom"] = meta["video"]["bits"]
                meta["video"]["codec"] = conv.get("vcodec") or "hevc"
                meta["video"].pop("bits", None)     # recodificado: la del origen ya no vale
            if conv.get("bits"):
                meta["video"]["bits"] = conv["bits"]
            meta["video"]["apple"] = not conv.get("forced")
            if conv.get("venc"):
                to_k, est = conv.get("vbr"), False
                if not to_k:
                    to_k, est = estimate_video_kbps(final, info, meta["tracks"]), True
                if vsrc_kbps:
                    cv["vbr_from"] = vsrc_kbps
                if to_k:
                    cv["vbr_to"] = to_k
                    meta["video"]["vbr"] = to_k
                    if est:
                        cv["vbr_est"] = True
        aenc = conv.get("aenc") or []
        for i, t in enumerate(meta["tracks"]):
            if i < len(aenc) and aenc[i]:
                afrom.append(str(t.get("codec") or "?"))
                t["codec"] = "aac"
                if conv.get("abr"):
                    t["abr"] = int(conv["abr"])
            t["apple"] = True
        if afrom:
            cv["afrom"] = sorted(set(afrom))
        for k_in, k_out in (("engine", "engine"), ("secs", "secs"), ("speed", "speed"), ("cfrom", "cfrom")):
            if conv.get(k_in) not in (None, ""):
                cv[k_out] = conv[k_in]
        if cv:
            meta["conv"] = cv
    return meta


def source_info(info):
    """{'site', 'channel'} de donde se bajó el video (lo que se sepa), o {}."""
    if not isinstance(info, dict):
        return {}
    site = info.get("webpage_url_domain") or _host(info.get("webpage_url") or info.get("original_url") or "")
    site = re.sub(r"^www\.", "", str(site or "").strip())
    chan = str(info.get("channel") or info.get("uploader") or "").strip()
    out = {}
    if site:
        out["site"] = site
    if chan:
        out["channel"] = chan
    return out


def source_video_kbps(fmt):
    """Bitrate (kbps) del video de origen según el formato, o None."""
    try:
        v = fmt.get("vbr")
        if v:
            return int(round(float(v)))
        t = fmt.get("tbr")
        if t:
            a = float(fmt.get("abr") or 0) if has(fmt.get("acodec")) else 0.0
            k = float(t) - a
            return int(round(k)) if k > 0 else None
    except (TypeError, ValueError, AttributeError):
        pass
    return None


def estimate_video_kbps(path, info, tracks):
    """Bitrate (kbps) del video estimado con tamaño y duración del archivo menos el audio, o None."""
    try:
        dur = float((info or {}).get("duration") or 0)
        size = os.path.getsize(path)
        if dur <= 0 or size <= 0:
            return None
        total = size * 8 / 1000.0 / dur
        audio = sum(float(t.get("abr") or 0) for t in (tracks or []))
        k = total - audio
        return int(round(k)) if k > 0 else None
    except (TypeError, ValueError, OSError):
        return None


def bitrate_change(a, b, est=False):
    """«4.1 → 2.3 Mbps (−44 %)» a partir de dos bitrates en kbps."""
    a, b = float(a), float(b)
    pct = int(round((b - a) / a * 100)) if a else 0
    if a >= 1000 and b >= 1000:
        txt = f"{a / 1000:.1f} → {'~' if est else ''}{b / 1000:.1f} Mbps"
    elif a < 1000 and b < 1000:
        txt = f"{a:.0f} → {'~' if est else ''}{b:.0f} kbps"
    else:
        txt = f"{fmt_kbps(a)} → {'~' if est else ''}{fmt_kbps(b)}"
    tail = "sin cambio" if pct == 0 else (f"+{pct} %" if pct > 0 else f"−{abs(pct)} %")
    return f"{txt} ({tail})"


def kv_rows(rows):
    """Filas «etiqueta  valor» con las etiquetas alineadas (sin dos puntos). Una etiqueta vacía
    continúa la fila anterior. El valor se parte con sangrado si no cabe."""
    w = term_width()
    lw = max((len(l) for l, _ in rows), default=0)
    for label, value in rows:
        lines = wrap_text(str(value), max(8, w - lw - 3))
        print("  " + paint(label.ljust(lw), "gray") + " " + lines[0])
        for ln in lines[1:]:
            print(" " * (lw + 3) + ln)


def audio_rows(tracks, room=None):
    """Filas de audio: una con códec y bitrate y, si hay varias pistas, otra con los idiomas
    (◆ original, ▸ predeterminada). Devuelve (filas, hay_marcas). `room`: caracteres máximos de
    la fila de idiomas; si sobran se cortan con «+N»."""
    if not tracks:
        return [("Audio", "sin pistas de audio")], False
    codecs = sorted({str(t.get("codec") or "?") for t in tracks})
    abrs = [int(t["abr"]) for t in tracks if t.get("abr")]
    if abrs:
        rate = f"{min(abrs)}k" if min(abrs) == max(abrs) else f"{min(abrs)}-{max(abrs)}k"
    else:
        rate = ""
    codec = "/".join(codecs) + (f" {rate}" if rate else "")
    if len(tracks) == 1:
        return [("Audio", f"{tracks[0].get('lang') or 'und'} · {codec}")], False
    marks, toks = False, []
    for t in tracks:
        tok = str(t.get("lang") or "und")
        if t.get("original"):
            tok += "◆"
            marks = True
        if t.get("default"):
            tok += "▸"
            marks = True
        toks.append(tok)
    if room and len(" ".join(toks)) > room:
        keep = len(toks)
        while keep > 1 and len(" ".join(toks[:keep])) + len(f" +{len(toks) - keep}") > room:
            keep -= 1
        toks = toks[:keep] + [f"+{len(toks) - keep}"]
    return [("Audio", f"{len(tracks)} pistas · {codec}"), ("", " ".join(toks))], marks


def conv_rows(meta):
    """Filas «Convertido» y «Bitrate» de una descarga convertida (vacío si no se convirtió)."""
    if not meta.get("converted"):
        return []
    cv = meta.get("conv") or {}
    v = meta.get("video") or {}
    rows, first, second = [], [], []
    if cv.get("vfrom"):
        first.append(f"{cv['vfrom']} → {str(v.get('codec') or 'hevc').upper()}")
        bf, bt = cv.get("bfrom"), v.get("bits")
        if bf and bt:
            first.append(f"{bf} → {bt} bits" if bf != bt else f"{bt} bits")
    elif cv.get("cfrom"):
        first.append(f"contenedor {cv['cfrom']} → {meta.get('container') or '?'}")
    tail = [x for x in (str(cv["engine"]) if cv.get("engine") else None,
                        f"{cv['secs']} s" if cv.get("secs") is not None else None) if x]
    if cv.get("afrom"):                    # el audio solo si cabe en la misma línea (máx. 2 líneas)
        with_audio = ["audio " + "/".join(cv["afrom"]) + " → aac"] + tail
        if dwidth(" · ".join(with_audio)) <= term_width() - 13 or not tail:
            tail = with_audio
    second = tail
    if first:
        rows.append(("Convertido", " · ".join(first)))
    if second:
        rows.append(("Convertido" if not rows else "", " · ".join(second)))   # máx. 2 líneas
    if not rows:
        rows.append(("Convertido", "compatible Apple"))
    if cv.get("vbr_from") and cv.get("vbr_to"):
        rows.append(("Bitrate", bitrate_change(cv["vbr_from"], cv["vbr_to"], bool(cv.get("vbr_est")))))
    return rows


def show_existing(path, entry, title=None):
    """Resumen compacto del archivo ya descargado, con las etiquetas alineadas."""
    try:
        size = os.path.getsize(path)
    except OSError as _ign:
        ignore("show_existing", _ign)
        size = 0
    when = entry.get("date")
    when_s = time.strftime("%Y-%m-%d %H:%M", time.localtime(when)) if when else "?"
    header("YA DESCARGADO", gap=False)
    title = title or entry.get("title") or os.path.splitext(os.path.basename(path))[0]
    show_title(title)
    rows = []
    meta = entry.get("meta")
    base = os.path.basename(path)
    ext = os.path.splitext(path)[1].lstrip(".") or "?"
    marks, apple = False, False
    dash = "—"                                   # filas fijas; «—» si falta el dato
    if meta:
        vrow = ("Video", dash)
        v = meta.get("video")
        if v:
            vb = [str(x) for x in (v.get("res"), v.get("codec")) if x]
            if v.get("bits"):
                vb.append(f"{v['bits']} bits")
            vrow = ("Video", " · ".join(vb) or "?")
            apple = bool(v.get("apple"))
        elif meta.get("kind") == "video":
            vrow = ("Video", meta.get("container") or "?")
            apple = bool(meta.get("converted"))
        elif meta.get("kind") == "audio":
            vrow = ("Video", "solo audio")
        tracks = meta.get("tracks") or []
        arows, marks = audio_rows(tracks, 3 * max(8, term_width() - 13))
        if meta.get("kind") == "audio" and tracks:
            apple = all(t.get("apple") for t in tracks)
        rows += [vrow] + arows
    if os.path.splitext(base)[0] != safe_name(title):
        rows.append(("Nombre", base))
    rows.append(("Archivo", f"{ext} · {human_size(size)}"))
    fecha = f"{when_s} · v{entry.get('version', '?')}"
    dl = entry.get("delivered")
    if dl and time.strftime("%Y-%m-%d %H:%M", time.localtime(dl)) != when_s:
        fecha += " · entregado " + time.strftime("%Y-%m-%d %H:%M", time.localtime(dl))
    rows.append(("Fecha", fecha))
    if meta:
        src = meta.get("source") or {}
        rows.append(("Origen", " · ".join(x for x in (src.get("site"), src.get("channel")) if x) or dash))
        crows = conv_rows(meta)
        rows += crows if crows else [("Convertido", dash), ("Bitrate", dash)]
        if crows and not any(l == "Bitrate" for l, _v in crows):
            rows.append(("Bitrate", dash))
    kv_rows(rows)
    if not meta:
        m_info("Sin datos técnicos (versión anterior).")
        return
    if marks or apple:
        print()
    if marks:
        print("  " + paint("◆", "amber") + " " + paint("original", "gray") + "   "
              + paint("▸", "orange") + " " + paint("predeterminada", "gray"))
    if apple:
        print("  " + paint("✓", "mint") + " " + paint("Compatible con Apple", "gray"))


# ───────────────────── [E2] Enlace y portapapeles ─────────────────────
def clipboard_cmd():
    """Orden que imprime el portapapeles, o None. iOS pide permiso de pegado cada vez:
    solo se usa si se pide con DLPY_CLIPBOARD=1."""
    on = os.environ.get("DLPY_CLIPBOARD", "").strip().lower() not in ("", "0", "no", "false")
    return ["pbpaste"] if on and shutil.which("pbpaste") else None


def clipboard_link():
    """Enlace http(s) del portapapeles o None."""
    cmd = clipboard_cmd()
    if not cmd:
        return None
    out = run_cmd(cmd, timeout=4)
    t = (out or "").strip()
    return t if re.match(r"^https?://\S+$", t) else None


def get_link(cli_args):
    if cli_args:
        return cli_args[0]
    clip = clipboard_link()
    if clip:
        kv("Portapapeles", clip)
        try:
            r = ask_yn("¿Usarlo? (S/n) ▸ ", default=True, seconds=WAIT_SECONDS)
        except (EOFError, KeyboardInterrupt):
            return None
        if r is None:
            m_info("Sin respuesta: se elige Sí.")
            r = True
        if r:
            return clip
    last_data = load_json(LAST_FILE)
    last = last_data.get("link")
    if last:
        kv("Último enlace", last)
        last_title = str(last_data.get("title") or "").strip()
        if last_title:
            kv("Título", last_title)
        try:
            usar = ask_yn("¿Usarlo? (S/n) ▸ ", default=True)
        except (EOFError, KeyboardInterrupt):
            return None
        if usar:
            return last
    try:
        hint("Pega el enlace")
        link = ask_line(PROMPT, True, "Pega el enlace ▸ ").strip()
    except (EOFError, KeyboardInterrupt):
        return None
    return link or None


def shortcut_copy(text):
    """Copia `text` al portapapeles (pbcopy). Respaldo de --scm (--shortcutclip) y de --scb cuando
    el JSON no cabe en la URL."""
    tmp = os.path.join(WORK_ROOT, "shortcut_clip.json")
    try:
        os.makedirs(WORK_ROOT, exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(text)
        return os.system("pbcopy < " + shlex.quote(tmp)) == 0
    except OSError as _ign:
        ignore("shortcut_copy", _ign)
        return False
    finally:
        try:
            os.remove(tmp)
        except OSError as _ign:
            ignore("shortcut_copy", _ign)


# ╔════════════════════════════════════════════════════════════════════════════════════════════╗
# ║ ÁREA F · DEPENDENCIAS Y ACTUALIZACIÓN — pip, Releases de GitHub, JS de YouTube, rechazos   ║
# ╚════════════════════════════════════════════════════════════════════════════════════════════╝
# ───────────────────── [F1] Dependencias ─────────────────────
def pkg_version(pip_name):
    try:
        from importlib import metadata
        return metadata.version(pip_name)
    except Exception as _ign:
        ignore("pkg_version", _ign)
        return None


def refresh_paths():
    """Agrega a sys.path las carpetas de paquetes que pip pudo crear tras el arranque."""
    cands = []
    try:
        cands.append(site.getusersitepackages())
    except Exception as _ign:
        ignore("refresh_paths", _ign)
    cands += glob.glob(os.path.join(HOME, "Library", "lib", "python*", "site-packages"))
    cands += glob.glob(os.path.join(HOME, ".local", "lib", "python*", "site-packages"))
    for c in cands:
        if c and os.path.isdir(c) and c not in sys.path:
            site.addsitedir(c)


INSTALLED_OK = set()                   # módulos ya vistos instalados en esta ejecución (0.6.6)


def is_installed(module, fresh=False):
    """¿Se puede importar `module`? Recuerda los que sí durante la ejecución (refresh_paths + invalidate_caches
    cuestan ~10 ms cada vez); los que no están se vuelven a mirar siempre. fresh=True ignora lo recordado."""
    if module in INSTALLED_OK and not fresh:
        return True
    import importlib
    import importlib.util
    refresh_paths()
    importlib.invalidate_caches()
    try:
        ok = importlib.util.find_spec(module) is not None
    except Exception as _ign:
        ignore("is_installed", _ign)
        return False
    if ok:
        INSTALLED_OK.add(module)
    return ok


def latest_version(pip_name):
    import urllib.request
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{pip_name}/json", timeout=6) as r:
            return json.load(r)["info"]["version"]
    except Exception as _ign:
        ignore("latest_version", _ign)
        return None


def vtuple(v):
    """Tupla numérica de una versión, rellenada a tres números («1.0» = «1.0.0»); () si no hay números."""
    t = tuple(int(x) for x in re.findall(r"\d+", v or ""))
    return t + (0,) * (3 - len(t)) if t else t


DOWNGRADE_CAUSES = ("manual", "recuperacion", "externa")
DOWNGRADE_DELIBERATE = ("manual", "recuperacion")     # bajadas hechas a propósito desde DLpy


def version_move(stored, current):
    """Cambio entre la última versión que corrió (`stored`) y la actual: «nueva» (sin registro
    previo), «igual», «sube» o «baja» (downgrade). Compara números, no texto (0.10.0 > 0.9.9)."""
    if not stored:
        return "nueva"
    s, c = vtuple(stored), vtuple(current)
    return "igual" if s == c else "sube" if c > s else "baja"


def downgrade_span(stored, current):
    """Qué número cambió al bajar de `stored` a `current`: «mayor», «menor», «parche» o None."""
    s, c = vtuple(stored), vtuple(current)
    for i, name in enumerate(("mayor", "menor", "parche")):
        if (s[i] if i < len(s) else 0) != (c[i] if i < len(c) else 0):
            return name
    return None


# ─────────── [F2] Actualizaciones: solo Releases de GitHub ───────────
UPDATE_REPO = (os.environ.get("DLPY_UPDATE_REPO") or "ElDelDLpy/DLpy").strip().strip("/")
UPDATE_MAX_BYTES = 3 * 1024 * 1024


def remote_script_version(text):
    """Versión «x.y.z» de un dlpy.py descargado, o None si no parece uno válido."""
    if not text or not text.startswith("#!dlpy.py"):
        return None
    m = re.search(r'(?m)^VERSION = "(\d+\.\d+\.\d+)"[ \t]*$', text)
    return m.group(1) if m else None


_RAW_GH_RE = re.compile(r"^https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/?#]+)/([^?#]+)$")


GH_HOSTS = ("github.com", "api.github.com", "raw.githubusercontent.com", "objects.githubusercontent.com",
            "release-assets.githubusercontent.com")


def is_github_url(url):
    """¿El enlace es de GitHub (API, raw, descargas de Releases)?"""
    try:
        host = (urllib.parse.urlparse(url or "").hostname or "").lower()
    except ValueError:
        return False
    return host in GH_HOSTS or host.endswith(".githubusercontent.com")


def gh_notice(what):
    """Aviso de que DLpy se conecta a GitHub (una vez por operación, no por página ni por reintento)."""
    try:
        m_info(f"Conectando a GitHub · {what}")
    except Exception as _ign:
        ignore("gh_notice", _ign)


def fresh_bytes(url, timeout=5, limit=None):
    """Bytes de `url` sin pasar por cachés. Para enlaces raw de GitHub consulta primero la
    API del repositorio (contents?ref=rama, formato raw: lee lo último subido) y, si falla
    o está limitada, el enlace raw con un parámetro único que evita la caché del CDN.
    Otros enlaces se piden tal cual. None si todo falla."""
    import urllib.request
    import urllib.parse
    limit = limit or UPDATE_MAX_BYTES
    if is_github_url(url):
        gh_notice("descargando " + (os.path.basename(urllib.parse.urlparse(url).path) or "el archivo"))
    base = {"User-Agent": "DLpy-updater", "Cache-Control": "no-cache", "Pragma": "no-cache"}
    tries = []
    m = _RAW_GH_RE.match(url or "")
    if m:
        owner, repo, branch, path = m.groups()
        tries.append((f"https://api.github.com/repos/{owner}/{repo}/contents/"
                      f"{urllib.parse.quote(path)}?ref={urllib.parse.quote(branch)}",
                      dict(base, Accept="application/vnd.github.raw")))
        tries.append((f"{url}?_={int(time.time())}", base))
    else:
        tries.append((url, base))
    for u, headers in tries:
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=headers),
                                        timeout=timeout) as r:
                raw = r.read(limit + 1)
            if len(raw) <= limit:
                return raw
        except Exception as _ign:
            ignore("fresh_bytes", _ign)
    return None


def fetch_remote_script(timeout=5, url=None):
    """Texto del dlpy.py de `url` (el de un Release), o None si falla o no es un script válido."""
    if not url:
        return None
    try:
        raw = fresh_bytes(url, timeout)
        if raw is None:
            return None
        text = raw.decode("utf-8").replace("\r\n", "\n")
        if not remote_script_version(text):
            return None
        compile(text, "dlpy.py", "exec")          # descarga truncada o dañada
        return text
    except Exception as _ign:
        ignore("fetch_remote_script", _ign)
        return None


NO_UPDATES = {"on": False}            # --noupdates / --no-updates / DLPY_NO_UPDATE: esta ejecución no busca nada
LATE_UPDATES = {"on": False, "done": False}   # --shortcutpick: se busca al terminar la descarga
RELEASE_SAME = {"igual": False}       # ¿la instalada es idéntica al último Release? (lo fija check_update)
RELEASES = {"list": None}             # Releases leídos en esta ejecución (los guarda remote_releases): de ahí sale changelog.md
UPDATE_CHECKED = {"ok": False}        # ¿llegó a comprobarse la última versión (hubo red)?

# Búsqueda de actualizaciones una vez al día: fecha de la última comprobación por clave
# («script» = DLpy en GitHub, «deps» = dependencias) en state/checks.json.
CHECK_HOURS = _env_num("DLPY_CHECK_HOURS", 24.0, minimum=float("-inf"))      # ≤ 0 = comprobar siempre


def due_from(rec, sig=None, now=None, hours=None):
    """¿Toca comprobar? Sí si nunca se hizo, si pasaron `hours` horas (o el reloj fue hacia atrás) o si
    la firma `sig` cambió desde la última vez. Pura: la prueba --selftest."""
    now = time.time() if now is None else now
    hours = CHECK_HOURS if hours is None else hours
    if hours <= 0 or not isinstance(rec, dict):
        return True
    t = rec.get("t")
    if not isinstance(t, (int, float)) or not 0 <= now - t < hours * 3600:
        return True
    return sig is not None and rec.get("sig") != sig


def check_due(key, sig=None):
    return due_from(load_json(CHECK_FILE).get(key), sig)


def check_mark(key, sig=None):
    """Anota que `key` se comprobó ahora (y con qué firma)."""
    try:
        d = load_json(CHECK_FILE)
        d[key] = {"t": int(time.time()), "sig": sig}
        save_json(CHECK_FILE, d)
    except Exception as _ign:
        ignore("check_mark", _ign)


def script_sig():
    """Firma de este dlpy.py: versión y fecha del archivo. Si cambia (otra versión o editado), toca
    comprobar aunque no hayan pasado 24 h."""
    try:
        return f"{VERSION}:{int(os.path.getmtime(SCRIPT_PATH))}"
    except OSError as _ign:
        ignore("script_sig", _ign)
        return VERSION


def update_status(remote, local=None):
    """«nueva» (hay una más reciente en los Releases), «igual» o «local» (la local es más
    nueva que la del último Release: el autor puede tener una sin publicar)."""
    r, l = vtuple(remote), vtuple(VERSION if local is None else local)
    return "nueva" if r > l else "igual" if r == l else "local"


def release_notes_lines(notes, width):
    """Líneas de los release notes (Markdown simplificado) listas para imprimir: los títulos salen en naranja, las
    viñetas con «•», y se quitan **negritas**, `código` y [enlaces](url). Una sola línea en blanco entre bloques."""
    out, blank = [], True
    srcl, joinable = [], False             # una línea de texto tras una viñeta o párrafo sigue siendo suya
    for raw in norm_text(notes or "").split("\n"):
        t = raw.rstrip()
        if not t.strip():
            srcl.append("")
            joinable = False
        elif (joinable and t[:1] in (" ", "\t") and not re.match(r"^\s*#{1,6}\s+", t)
              and not re.match(r"^\s*[-*+]\s+", t)):
            srcl[-1] += " " + t.strip()
        else:
            srcl.append(t)
            joinable = not re.match(r"^\s*#{1,6}\s+", t)
    for raw in srcl:
        s = raw.rstrip()
        if not s.strip():
            if not blank:
                out.append("")
            blank = True
            continue
        blank = False
        s = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", s)
        s = re.sub(r"(\*\*|__)(.+?)\1", r"\2", s)
        s = s.replace("`", "")
        m = re.match(r"^\s*#{1,6}\s+(.*)$", s)
        if m:
            if out and out[-1] != "":
                out.append("")
            out += [paint(ln, "orange", True) for ln in wrap_text(m.group(1).strip(), width)]
            continue
        m = re.match(r"^(\s*)[-*+]\s+(.*)$", s)
        if m:
            ind = min(len(m.group(1).replace("\t", "  ")), 8)
            for i, ln in enumerate(wrap_text(m.group(2).strip(), max(8, width - ind - 2))):
                out.append(" " * ind + (paint("•", "orange") + " " if i == 0 else "  ") + ln)
            continue
        out += wrap_text(s.strip(), width)
    while out and out[-1] == "":
        out.pop()
    return out


def notes_limit():
    """Líneas de release notes que caben en la pantalla junto al banner y la pregunta."""
    return max(6, ui_lines() - banner_height() - 9)


def show_release_notes(ver, notes, date=None, limit=None, unavailable=None, tag=None):
    """Imprime los release notes de `ver`. Devuelve cuántas líneas quedaron sin mostrar (0 = se ve todo).
    `tag`: texto extra junto al título (p. ej. «se instalará»)."""
    print(paint("▍", "orange") + paint(f"Release notes · {ver}" + (f" · {date}" if date else ""), "white", True)
          + (paint(f" · {tag}", "orange") if tag else ""))
    lines = release_notes_lines(notes, max(8, term_width() - 4))
    if not lines:
        note(unavailable or "Este Release no trae release notes.")
        return 0
    shown = lines if limit is None else lines[:max(1, limit)]
    for ln in shown:
        print("  " + ln)
    if len(lines) > len(shown):
        note(f"(+{len(lines) - len(shown)} líneas más: «m»)")
    return len(lines) - len(shown)


def parse_install_answer(ans, more=False, default=True):
    """True = instalar, False = cancelar, «m» = ver las notas completas (solo si `more`), None = no se entiende.
    Enter vale `default` (Enter = instalar, salvo que la versión sea idéntica a una que falló)."""
    a = (ans or "").strip().lower()
    if a == "":
        return default
    if a in ("s", "si", "sí", "y", "yes", "i", "ok"):
        return True
    if a in ("n", "no", "0", "c", "cancelar"):
        return False
    if a == "m" and more:
        return "m"
    return None


def order_releases(rels):
    """Releases con su versión, del más nuevo al más viejo (los repetidos se quedan una vez)."""
    seen, out = set(), []
    for r in sorted((r for r in rels or [] if isinstance(r, dict) and r.get("ver")),
                    key=lambda x: vtuple(x["ver"]), reverse=True):
        if r["ver"] not in seen:
            seen.add(r["ver"])
            out.append(r)
    return out


def show_all_release_notes(rels, ver):
    """Los changelog de TODOS los Releases de GitHub, del más nuevo al más viejo; marca el de `ver`, la versión
    que se va a instalar."""
    for i, r in enumerate(order_releases(rels)):
        if i:
            print()
        show_release_notes(r["ver"], r.get("notes"), r.get("date"),
                           unavailable="Este Release no trae release notes.",
                           tag="se instalará" if r["ver"] == ver else None)


def show_notes_on_apply(ver, notes, date=None, hidden=0, viewed=False, unavailable=None):
    """Justo antes de aplicar una versión: si sus release notes se vieron recortadas (`hidden` > 0) y no se abrieron
    con «m», las muestra completas en una pantalla limpia y espera un momento proporcional a su largo (0.6.6)."""
    if hidden <= 0 or viewed:
        return
    try:
        hide_keyboard(0.3)
        clear_screen()
        if CARD["pin"]:
            card_thread_stop()
        header(f"CHANGELOG {ver} · se instalará", gap=False)
        shown = show_release_notes(ver, notes, date, unavailable=unavailable)
        time.sleep(2.0 + min(4.0, 0.04 * (hidden + max(0, shown))))
    except Exception as _ign:
        ignore("show_notes_on_apply", _ign)


def confirm_install(msg, ver, notes, date=None, seconds=False, default=True, unavailable=None, all_rels=None):
    """Muestra los release notes de `ver` (solo los de la versión que se instalará) y pregunta «▍¿…?» con
    « [S] Sí  [n] No ▸ » como todas las preguntas s/n (Enter = la predeterminada). «m» muestra en ese mismo menú los changelog de TODOS los Releases de GitHub
    (`all_rels`, por omisión los ya leídos en esta ejecución); sin ellos, «m» muestra completas las notas de `ver`
    si no cabían. seconds=número: cuenta regresiva y, si vence sin respuesta, se toma la predeterminada (Sí = instalar).
    default=False (versión idéntica a una que falló): Enter cancela, hay que escribir «s» y, si la cuenta vence, no se
    instala. True = instalar. Al instalar, si las notas no se vieron completas (no cabían y no se pulsó «m»), se
    muestran enteras antes de aplicar la versión (0.6.6)."""
    rels = order_releases(RELEASES["list"] if all_rels is None else all_rels)
    hidden = show_release_notes(ver, notes, date, limit=notes_limit(), unavailable=unavailable)

    q = msg if str(msg).lstrip().startswith("¿") else f"¿{msg}?"
    label = "Todos los changelog" if rels else "Ver todo"

    def line(more):
        return yn_line(default, ("m", label) if more else None)

    def plain(more):
        return yn_prompt(q, default, ("m", label) if more else None)

    can_more = bool(rels) or hidden > 0
    viewed = False                         # ¿ya se vieron las notas completas con «m»?
    print_question(q)
    cur = line(can_more)
    while True:
        more = can_more
        try:
            r = (ask_line(cur, True, plain(more)) if seconds is False
                 else timed_input(cur, seconds, True, plain(more)))
        except (EOFError, KeyboardInterrupt):
            return False
        if r is None:
            if not default:
                m_info("Sin respuesta: no se instala.")
                return False
            m_info("Sin respuesta: se instala.")
            show_notes_on_apply(ver, notes, date, hidden, viewed, unavailable)
            return True
        v = parse_install_answer(r, more, default)
        if v == "m":
            viewed = True
            hide_keyboard(0.3)
            clear_screen()
            if CARD["pin"]:
                card_thread_stop()
            if rels:
                header("CHANGELOG · GITHUB", gap=False)
                show_all_release_notes(rels, ver)
            else:
                header(f"RELEASE NOTES {ver}", gap=False)
                show_release_notes(ver, notes, date, unavailable=unavailable)
            can_more = False
            print_question(q)
            cur = line(False)
            continue
        if v is True:
            show_notes_on_apply(ver, notes, date, hidden, viewed, unavailable)
        if v is not None:
            return v
        cur = retry_prompt(cur, r, paint("✗", "red", True) + line(more)[1:],
                           "Respuesta inválida: escribe s, n" + (" o m." if more else "."))


def check_update(force=False, late=False):
    """Si el último Release de GitHub es más nuevo, muestra sus release notes y, con Enter, lo instala y lo ejecuta.
    Siempre deja una línea con el resultado (✓ si ya tienes la última).

    late=True: la respuesta por omisión es Sí (Enter o cuenta regresiva vencida; solo es No si es idéntica a una que
    falló) y, si se instala, NO se reejecuta (reiniciaría la descarga): la versión nueva se usa la próxima vez.

    Devuelve True si se ejecutó la versión nueva (quien llama debe terminar)."""
    cbar = Bar()
    cbar.start("Comprobando DLpy")
    try:
        rel = fetch_latest_release(timeout=8 if force else 5)      # la actualización sale solo de los Releases
    finally:
        cbar.stop()
    sync_changelog(fetch=False)                 # changelog.md ← release notes de los Releases recién leídos
    if not rel:
        m_warn(f"DLpy {VERSION} · no se pudo comprobar la última versión (Releases de GitHub)")
        return False
    remote, text = rel["ver"], rel["text"]
    UPDATE_CHECKED["ok"] = True                # hubo respuesta: cuenta como comprobada
    status = update_status(remote)
    rec = load_json(RECOVERED_FILE)
    crashed = rec.get("crashed")
    if crashed and vtuple(VERSION) > vtuple(crashed):
        clear_recovered()                  # ya pasaste la versión que falló
        rec, crashed = {}, None
    if status == "igual":
        try:
            mine = read_text(SCRIPT_PATH)
        except (OSError, ValueError) as _ign:
            ignore("check_update", _ign)
            mine = None
        same = compare_texts(text, mine) if mine is not None else None
        RELEASE_SAME["igual"] = (same == "igual")      # check_version lo usa para refrescar la copia guardada
        m_check(f"DLpy {VERSION} · última versión" + (" · idéntica al Release" if same == "igual" else ""))
        if same == "distinto":
            add, rem = diff_counts(diff_lines(text, mine, "Release", "instalada"))
            m_warn(f"{VERSION} · Release ≠ instalada (código distinto: -{rem} +{add} líneas)")
            note("Mismo número con código distinto: revisa cuál es el bueno.")
        return False
    if status == "local":
        m_info(f"DLpy {VERSION} · versión local más reciente que la del último Release ({remote})")
        return False
    hold = downgrade_hold()
    if hold and vtuple(remote) <= vtuple(hold):
        if not force:
            m_info(f"DLpy {VERSION} · bajaste a propósito desde la {hold}; no se ofrece la {remote} del Release")
            note(f"Cuando haya una versión más nueva que la {hold} se avisará. "
                 "Con --actualizar puedes instalarla de todos modos.")
            return False
        m_warn(f"La {remote} del Release no es más nueva que la {hold}, de la que bajaste a propósito.")
    match = (crash_match(remote, text) or (None,))[0]
    if skip_update_after_recovery(remote, crashed, match):
        if not force:
            m_info(f"DLpy {VERSION} · recuperada tras fallar la {crashed}; no se ofrece la {remote} del Release")
            note("Cuando haya una versión más nueva que la que falló se avisará. "
                 "Con --actualizar puedes instalarla de todos modos.")
            return False
        m_warn(f"La {remote} del Release es la que falló en este equipo.")
    else:
        m_info(f"Hay una versión nueva de DLpy: {VERSION} → {remote} (Release)")
    kind = show_crash_warning(remote, text)       # avisa si es idéntica a una que falló
    # a-Shell: esta pregunta va con input() normal (sin cbreak). Después la versión nueva corre en
    # este mismo proceso y cambiar el modo del terminal justo antes la congelaba.
    if late:
        go = confirm_install(f"Instalar la {remote} para la próxima vez", remote, rel["notes"], rel["date"],
                             seconds=WAIT_SECONDS, default=(kind != "igual"))
    else:
        go = confirm_install(f"Instalar la {remote} y ejecutarla ahora", remote, rel["notes"], rel["date"],
                             default=(kind != "igual"))
    if not go:
        note("Se volverá a preguntar en la próxima comprobación (cada 24 h) o con --actualizar.")
        return False
    try:
        write_text(SCRIPT_PATH, text)
    except Exception as e:
        m_warn(f"No se pudo instalar la actualización: {e}")
        return False
    clear_recovered()
    m_check(f"DLpy {remote} · instalada")
    if late:
        m_info(f"Se usará la {remote} la próxima vez que abras DLpy.")
        return False
    reexec_script()                                    # termina con SystemExit
    return True


def late_updates():
    """Con --shortcutpick las actualizaciones no se buscan al abrir sino aquí, tras la descarga y justo
    antes de entregar el archivo. La respuesta por omisión es Sí, también al acabar la cuenta regresiva, y una
    versión nueva de DLpy no se reejecuta (reiniciaría la descarga): se usa la próxima vez."""
    LATE_UPDATES["done"] = True
    if NO_UPDATES["on"]:
        return
    try:
        if check_due("script", script_sig()):
            check_update(late=True)
            if UPDATE_CHECKED["ok"]:
                check_mark("script", script_sig())
        if check_due("deps_late"):
            check_dependencies(late=True)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        ignore("late_updates", e)


def pip_args(pip_name, no_deps=None):
    """Argumentos de «pip» (sin el ejecutable): -U y --no-deps."""
    if no_deps is None:
        no_deps = True
    return ["install", "-U", pip_name] + (["--no-deps"] if no_deps else [])


def pip_run(args):
    """Lanza pip con `args`. Devuelve el código de salida. a-Shell ejecuta sus comandos dentro de
    la app, así que se usa su «pip» con os.system (argumentos entrecomillados)."""
    return os.system("pip " + " ".join(shlex.quote(a) for a in args))


def pip_install(pip_name):
    """Instala/actualiza `pip_name`. True si salió bien."""
    m_info(f"Instalando {pip_name}...")
    ok = pip_run(pip_args(pip_name)) == 0
    refresh_paths()
    return ok


# ─────────── [F3] YouTube: runtime de JavaScript + yt-dlp-ejs ───────────
# Desde yt-dlp 2025.11.12 YouTube completo necesita un runtime de JavaScript
# (deno, node, bun o quickjs) y el paquete yt-dlp-ejs en la versión exacta que
# fija esa versión de yt-dlp. Con «--no-deps» ese paquete no se
# instalaba nunca.
JS_REQUIRED_FROM = (2025, 11, 12)
JS_RUNTIMES = (("deno", "deno"), ("node", "node"), ("bun", "bun"), ("quickjs", "qjs"))
JS_INSTALL_HINT = "no hay un runtime de JavaScript conocido para a-Shell"


def ytdlp_needs_js(version=None):
    """¿Esta versión de yt-dlp ya exige runtime de JavaScript para YouTube?"""
    v = vtuple(version if version is not None else pkg_version("yt-dlp"))
    return bool(v) and v >= JS_REQUIRED_FROM


def js_runtime():
    """(nombre para --js-runtimes, ruta) del primer runtime que haya, o None."""
    for name, exe in JS_RUNTIMES:
        path = shutil.which(exe)
        if path:
            return name, path
    return None


def js_runtime_args(extra=None, version=None, runtime="auto"):
    """Banderas de yt-dlp para usar el runtime disponible. Solo deno viene activado
    por defecto; node/bun/quickjs hay que pedirlos. No pisa lo que ya puso el usuario."""
    extra = list(extra or [])
    if any(a.startswith(("--js-runtimes", "--no-js-runtimes")) for a in extra):
        return []
    if not ytdlp_needs_js(version):
        return []
    rt = js_runtime() if runtime == "auto" else runtime
    if not rt or rt[0] == "deno":
        return []
    return ["--js-runtimes", rt[0]]


def ejs_pin(requires=None):
    """Requisito exacto de yt-dlp-ejs que declara el yt-dlp instalado
    (p. ej. «yt-dlp-ejs==0.8.0») o None. `requires` solo se inyecta en pruebas."""
    if requires is None:
        try:
            from importlib import metadata
            requires = metadata.requires("yt-dlp") or []
        except Exception as _ign:
            ignore("ejs_pin", _ign)
            return None
    for line in requires:
        m = re.match(r"^\s*yt[-_]dlp[-_]ejs\s*(?:==\s*([\w.]+))?", line, re.I)
        if m:
            return "yt-dlp-ejs==" + m.group(1) if m.group(1) else "yt-dlp-ejs"
    return None


def check_js_components(force=False):
    """Si hay runtime de JavaScript, deja instalado yt-dlp-ejs en la versión que pide
    yt-dlp. Sin runtime no hace nada (instalarlo sería inútil; check_system_packages
    ya lo ofrece o lo muestra como faltante)."""
    if not ytdlp_needs_js() or not js_runtime():
        return
    pin = ejs_pin()
    if not pin:
        return
    want = pin.split("==", 1)[1] if "==" in pin else None
    cur = pkg_version("yt-dlp-ejs") if is_installed("yt_dlp_ejs") else None
    if cur and (not want or cur == want):
        m_check(f"yt-dlp-ejs {cur} · para YouTube")
        declined_clear("yt-dlp-ejs")
        return
    what = "yt-dlp-ejs" + (f" {want}" if want else "")
    if not force and load_json(DEPS_STATE_FILE).get("yt-dlp-ejs") == pin:
        m_warn(f"{what} · " + (f"tienes {cur}" if cur else "falta")
               + " (rechazado; --actualizar lo pregunta)")
        return
    m_warn(f"{what} · " + (f"tienes {cur}" if cur else "falta") + " (YouTube lo necesita)")
    if ask(f"¿Instalar {pin}? (S/n) ▸ ", seconds=WAIT_SECONDS):
        pip_install(pin)
        if is_installed("yt_dlp_ejs"):
            m_check(f"yt-dlp-ejs {pkg_version('yt-dlp-ejs') or ''} · instalado")
            declined_clear("yt-dlp-ejs")
        else:
            m_warn("No se pudo instalar yt-dlp-ejs; YouTube puede mostrar menos formatos.")
    else:
        declined_set("yt-dlp-ejs", pin)
        note("No se vuelve a preguntar por esta versión; --actualizar lo pregunta de nuevo.")


def warn_youtube_js(link):
    """Aviso único al pegar un enlace de YouTube si falta el runtime de JavaScript."""
    if not _host_is(_host(link), ("youtube.com", "youtu.be", "youtube-nocookie.com")):
        return
    if not ytdlp_needs_js() or js_runtime():
        return
    m_warn("YouTube necesita un runtime de JavaScript y no hay ninguno: pueden faltar formatos.")
    note("Instálalo con: " + JS_INSTALL_HINT)


# ─────────── [F4] Rechazos recordados ───────────
# En a-Shell ffmpeg viene integrado y no hay gestor de paquetes del sistema: solo se recuerda lo que
# se rechazó de pip / yt-dlp-ejs.


def declined_set(key, value=True):
    """Recuerda que dijiste «no» a `key` (valor: True, o la versión rechazada)."""
    d = load_json(DEPS_STATE_FILE)
    if d.get(key) == value:
        return
    d[key] = value
    try:
        save_json(DEPS_STATE_FILE, d)
    except Exception as _ign:
        ignore("declined_set", _ign)


def declined_clear(key):
    d = load_json(DEPS_STATE_FILE)
    if key not in d:
        return
    d.pop(key)
    try:
        save_json(DEPS_STATE_FILE, d)
    except Exception as _ign:
        ignore("declined_clear", _ign)


def check_dependencies(force=False, updates=True, late=False):
    """Revisa instalación y actualizaciones; cada cosa deja una línea ✓/●.
    Devuelve False si falta una obligatoria. Que estén instaladas se mira siempre; buscar versiones
    nuevas, los paquetes del sistema y yt-dlp-ejs solo si toca (una vez al día) o con force."""
    # updates=False (--noupdates o descarga de atajo): solo comprueba que estén instaladas.
    # late=True: pregunta con Sí por omisión (0.6.6), no apunta rechazos
    # permanentes y no toca los paquetes del sistema ni yt-dlp-ejs (eso lo hace una ejecución normal).
    key = "deps_late" if late else "deps"
    due = updates and (force or check_due(key))
    net_ok = True
    for pip_name, module, required in DEPENDENCIES:
        if not is_installed(module):
            m_warn(f"Falta la dependencia: {pip_name}" + (" (obligatoria)" if required else ""))
            wanted = ask(f"¿Instalar {pip_name}? (S/n) ▸ ", seconds=WAIT_SECONDS)
            if wanted:
                pip_install(pip_name)
            if not is_installed(module):
                if required:
                    if wanted:
                        m_err(f"No se detectó {pip_name} tras instalarlo.")
                        m_info("Si pip indicó éxito, vuelve a ejecutar DLpy; si no: pip install " + pip_name)
                    else:
                        m_err(f"{pip_name} es obligatoria: sin ella DLpy no puede continuar.")
                        m_info("Instálala con: pip install " + pip_name)
                    return False
                continue
            m_check(f"{pip_name} {pkg_version(pip_name) or ''} · instalado".replace("  ", " "))
            continue

        if not due:
            continue
        cur = pkg_version(pip_name)
        cbar = Bar()
        cbar.start(f"Comprobando {pip_name}")
        try:
            lat = latest_version(pip_name)
        finally:
            cbar.stop()
        if cur and lat and vtuple(lat) > vtuple(cur):
            if not force and load_json(DEPS_STATE_FILE).get(pip_name) == lat:
                m_warn(f"{pip_name} {cur} · hay una {lat} (rechazada; --actualizar la instala)")
            else:
                m_info(f"Actualización de {pip_name}: {cur} → {lat}")
                if ask(f"¿Actualizar {pip_name}? (S/n) ▸ ", default=True, seconds=WAIT_SECONDS):
                    pip_install(pip_name)
                    m_check(f"{pip_name} {pkg_version(pip_name) or '?'} · actualizada")
                    declined_clear(pip_name)
                elif late:
                    note("Se volverá a preguntar en la próxima comprobación (cada 24 h) o con --actualizar.")
                else:
                    declined_set(pip_name, lat)
                    note("No se vuelve a preguntar por esta versión; con --actualizar la instalas.")
        elif cur and lat:
            m_check(f"{pip_name} {cur} · última versión")
        else:
            net_ok = False                       # sin respuesta de PyPI: se reintenta al siguiente arranque
            m_warn(f"{pip_name} {cur or '?'} · no se pudo comprobar la última versión")
    if due:
        if not late:
            check_js_components(force)
        if net_ok:
            check_mark(key)
    return True


# ╔═════════════════════════════════════════════════════════════════════════════════════════════════════════╗
# ║ ÁREA G · MANTENIMIENTO Y VERSIONES — changelog, almacenamiento, versión, releases, fallos, --versions   ║
# ╚═════════════════════════════════════════════════════════════════════════════════════════════════════════╝
# ───────────────────── [G1] Changelog y backup ─────────────────────
def read_text(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def write_text(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)


def parse_sections(text):
    secs, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(\d+\.\d+\.\d+)\s*$", line)
        if m:
            cur = m.group(1)
            secs[cur] = []
        elif cur:
            secs[cur].append(line)
    return {k: "\n".join(v).strip("\n") for k, v in secs.items()}


def changelog_block_md(body):
    """Markdown de un bloque de changelog del .py: le quita el «# » de cada línea."""
    lines = [ln[2:] if ln.startswith("# ") else ln.lstrip("#") for ln in body.splitlines()]
    return "\n".join(lines).strip("\n")


def script_changelog_notes(version=None, src=None):
    """Notas de `version` (la actual por omisión) según el bloque CHANGELOG del propio .py, o None si no
    hay. Solo lee el script: nunca lo modifica."""
    try:
        src = read_text(SCRIPT_PATH) if src is None else src
    except (OSError, ValueError) as _ign:
        ignore("script_changelog_notes", _ign)
        return None
    m = CL_RE.search(src)
    if not m:
        return None
    return parse_sections(changelog_block_md(m.group(1))).get(version or VERSION) or None


def publish_changelog_to_files():
    """Copia el changelog actual a dlpy_files/changelog.md."""
    src = CHANGELOG_FILE
    if not os.path.isfile(src):
        return
    try:
        os.makedirs(FILES_DIR, exist_ok=True)
        dest = os.path.join(FILES_DIR, "changelog.md")
        copy_file(src, dest)
    except Exception as e:
        if DEBUG:
            m_warn(f"No se pudo copiar changelog a dlpy_files: {e}")


def changelog_md_from_releases(rels, ver=None, own=None):
    """Texto de changelog.md: los release notes de GitHub de la versión actual (`ver`, VERSION por omisión) y
    de TODAS las inferiores que tienen Release, el más nuevo arriba, cada uno bajo «## x.y.z». Las versiones
    más nuevas que la actual no entran. Si la actual no tiene Release (o no trae notas) usa `own`, su
    changelog dentro del script. Un Release sin notas sale como «(sin release notes)»."""
    ver = ver or VERSION
    cur = vtuple(ver)
    notes = {}
    for r in rels or []:
        v = (r or {}).get("ver")
        if v and v not in notes and vtuple(v) <= cur:
            notes[v] = (r.get("notes") or "").strip()
    if own and not notes.get(ver):
        notes[ver] = own.strip()
    out = "# Changelog DLpy\n\n"
    for v in sorted(notes, key=vtuple, reverse=True):
        out += f"## {v}\n\n{notes[v] or '(sin release notes)'}\n\n"
    return out.rstrip("\n") + "\n"


def sync_changelog(rels=None, fetch=True, timeout=5, announce=False):
    """changelog.md ← release notes de GitHub de la versión actual y las inferiores. Usa los Releases dados o
    los ya leídos en esta ejecución (RELEASES) y, con fetch=True y sin ninguno, los pide. True = se reescribió,
    False = ya estaba al día, None = no hay Releases que leer (sin red, sin Releases o ninguno de esta versión
    o anterior): se deja el changelog.md que haya."""
    if rels is None:
        rels = RELEASES["list"]
        if rels is None and fetch:
            rels = remote_releases(timeout)
    if not rels:
        return None
    text = changelog_md_from_releases(rels, own=script_changelog_notes())
    n = len(parse_sections(text))
    if not n:
        return None
    try:
        cur = read_text(CHANGELOG_FILE) if os.path.isfile(CHANGELOG_FILE) else None
        if cur != text:
            os.makedirs(os.path.dirname(CHANGELOG_FILE), exist_ok=True)
            write_text(CHANGELOG_FILE, text)
        publish_changelog_to_files()
    except (OSError, ValueError) as e:
        m_warn(f"No se pudo escribir el changelog: {e}")
        return None
    if cur != text and announce:
        m_ok(f"Changelog actualizado desde los Releases de GitHub ({n} versión/es)")
    return cur != text


def ensure_changelog():
    """Al abrir: deja changelog.md en dlpy_files. Si ahí no existe lo genera a partir de los Releases de GitHub (la
    versión actual y todas las inferiores); si existe pero no trae la sección de esta versión (recién instalada) lo regenera igual, una
    vez al día o al cambiar de versión. Sin red se queda con la copia interna, si la hay. No hace nada de red con
    --noupdates."""
    missing = not os.path.isfile(os.path.join(FILES_DIR, "changelog.md"))
    have = False
    try:
        have = os.path.isfile(CHANGELOG_FILE) and VERSION in parse_sections(read_text(CHANGELOG_FILE))
    except (OSError, ValueError) as _ign:
        ignore("ensure_changelog", _ign)
    if NO_UPDATES["on"] or not (missing or (not have and check_due("changelog", VERSION))):
        publish_changelog_to_files()
        return
    if sync_changelog(announce=True) is not None:
        check_mark("changelog", VERSION)
        if missing and os.path.isfile(os.path.join(FILES_DIR, "changelog.md")):
            m_ok("changelog.md generado en dlpy_files desde los Releases de GitHub")
    else:
        publish_changelog_to_files()


def _free_path(base):
    dest, k = base, 2
    while os.path.exists(dest):
        dest = f"{base}-{k}"
        k += 1
    return dest


def next_backup_dir(prev):
    return _free_path(os.path.join(BACKUP_DIR, prev))


def snapshot_changelog():
    """Changelog hasta la versión respaldada (changelog.md o el del snapshot)."""
    try:
        if os.path.isfile(CHANGELOG_FILE):
            return read_text(CHANGELOG_FILE)
        src = read_text(SNAPSHOT_FILE)
    except Exception as _ign:
        ignore("snapshot_changelog", _ign)
        return None
    m = CL_RE.search(src)
    if not m:
        return None
    return "# Changelog DLpy\n\n" + changelog_block_md(m.group(1)) + "\n"


def backup_script(prev, snapshot_version, dest, announce=True):
    """Copia el script anterior y su changelog dentro de dest. True si lo logró."""
    if not os.path.isfile(SNAPSHOT_FILE) or snapshot_version != prev:
        if announce:
            m_info("No hay copia del script anterior (se guardará una desde esta versión).")
        return False
    try:
        copy_file(SNAPSHOT_FILE, os.path.join(dest, f"dlpy_{prev}.py"))
        cl = snapshot_changelog()
        if cl:
            write_text(os.path.join(dest, "changelog.md"), cl)
        return True
    except Exception as e:
        m_warn(f"No se pudo guardar el backup del script: {e}")
        return False


def save_snapshot():
    try:
        tmp = SNAPSHOT_FILE + ".tmp"             # atómico: un corte a mitad no deja una copia truncada
        shutil.copyfile(SCRIPT_PATH, tmp)
        os.replace(tmp, SNAPSHOT_FILE)
    except Exception as _ign:
        ignore("save_snapshot", _ign)


def changelog_block_from_md(md_text):
    """Bloque «# ==== CHANGELOG ==== … # ==== FIN CHANGELOG ====» (comentarios de
    Python) reconstruido desde el texto de changelog.md, o None si no hay versiones."""
    secs = parse_sections(md_text or "")
    if not secs:
        return None
    out = ["# ==== CHANGELOG ===="]
    vers = sorted(secs, key=vtuple, reverse=True)
    for i, ver in enumerate(vers):
        out.append(f"# ## {ver}")
        out.append("#")
        for ln in secs[ver].splitlines():
            out.append(("# " + ln).rstrip())
        if i < len(vers) - 1:
            out.append("#")                  # separador entre versiones
    out.append("# ==== FIN CHANGELOG ====")
    return "\n".join(out) + "\n"


def insert_changelog_block(code, block):
    """Pone `block` donde lo tenía el script: justo tras los comentarios fijos del
    principio (el último es «# Conservar en todo momento…»)."""
    lines = code.splitlines(keepends=True)
    at = 1
    for i, ln in enumerate(lines[:12]):
        if ln.startswith("# Conservar en todo momento"):
            at = i + 1
            break
    if lines and not lines[at - 1].endswith("\n"):
        lines[at - 1] += "\n"
    return "".join(lines[:at]) + block + "".join(lines[at:])


def script_variants(live=None, snapshot=None, md=None):
    """(sin_changelog, con_changelog) del dlpy.py actual; con_changelog es None si
    no hay de dónde sacarlo. Los parámetros solo se inyectan en pruebas."""
    if live is None:
        live = read_text(SCRIPT_PATH)
    m = CL_RE.search(live)
    if m:                                    # el .py todavía trae su changelog
        return live[:m.start()] + live[m.end():], live
    if snapshot is None and os.path.isfile(SNAPSHOT_FILE):
        try:
            snapshot = read_text(SNAPSHOT_FILE)
        except OSError as _ign:
            ignore("script_variants", _ign)
    if snapshot and CL_RE.search(snapshot) and remote_script_version(snapshot) == VERSION:
        return live, snapshot                # copia completa de esta misma versión
    if md is None and os.path.isfile(CHANGELOG_FILE):
        try:
            md = read_text(CHANGELOG_FILE)
        except OSError as _ign:
            ignore("script_variants", _ign)
    block = changelog_block_from_md(md)
    return live, (insert_changelog_block(live, block) if block else None)


# ───────────────────── [G2] Limpieza de almacenamiento ─────────────────────
CLEAN_LIMIT = int(_env_num("DLPY_CLEAN_LIMIT_MB", 1024.0) * 1024 * 1024)      # «inf» ya no impide arrancar


def tree_size(path, seen=None):
    """Bytes de un archivo o carpeta. `seen` evita contar dos veces los enlaces duros."""
    seen = set() if seen is None else seen
    total = 0
    try:
        if os.path.islink(path):
            return 0
        if os.path.isfile(path):
            st = os.stat(path)
            key = (st.st_dev, st.st_ino)
            if key in seen:
                return 0
            seen.add(key)
            return st.st_size
        if os.path.isdir(path):
            for n in os.listdir(path):
                total += tree_size(os.path.join(path, n), seen)
    except OSError as _ign:
        ignore("tree_size", _ign)
    return total


def is_video_file(path):
    return os.path.splitext(path)[1].lstrip(".").lower() in VIDEO_EXTS


def is_download_file(path):
    return os.path.splitext(path)[1].lstrip(".").lower() in DOWNLOAD_EXTS


def download_files(root):
    """Descargas (cualquier tipo de medio) dentro de root y sus subcarpetas.
    Nunca incluye scripts, changelogs, índices ni otros archivos."""
    out = []
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted(n for n in dns if not os.path.islink(os.path.join(dp, n)))
        for n in sorted(fns):
            p = os.path.join(dp, n)
            if not os.path.islink(p) and is_download_file(n):
                out.append(p)
    return out


def video_files(root):
    """Videos dentro de root y todas sus subcarpetas (sin enlaces simbólicos)."""
    out = []
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted(n for n in dns if not n.startswith(".")
                        and not os.path.islink(os.path.join(dp, n)))
        for n in sorted(fns):
            p = os.path.join(dp, n)
            if (not n.startswith(".") and not os.path.islink(p)
                    and is_video_file(n)):
                out.append(p)
    return out


def prune_empty_dirs(root):
    """Quita subcarpetas vacías de root (no root ni backups/ en sí)."""
    for dp, dns, fns in os.walk(root, topdown=False):
        if dp == root or dp == BACKUP_DIR:
            continue
        if dp == INTERNAL_DIR or dp.startswith(INTERNAL_DIR + os.sep):
            continue                # la carpeta oculta del script no se toca
        try:
            os.rmdir(dp)            # solo funciona si está vacía
        except OSError as _ign:
            ignore("prune_empty_dirs", _ign)


def storage_groups():
    """Rutas que se pueden limpiar, por categoría."""
    dl, cache, bak = [], [], []
    if os.path.isdir(FILES_DIR):
        for n in sorted(os.listdir(FILES_DIR)):
            p = os.path.join(FILES_DIR, n)
            if is_data_entry(n) and os.path.isfile(p):
                if is_video_file(p):
                    dl.append(p)
            elif is_data_entry(n) and os.path.isdir(p) and not os.path.islink(p):
                dl += video_files(p)        # videos de las subcarpetas
    for p in indexed_files():               # Android: solo lo que DLpy descargó en Descargas
        if is_video_file(p) and p not in dl:
            dl.append(p)
    if os.path.isdir(BACKUP_DIR):
        bak += download_files(BACKUP_DIR)   # solo descargas, no scripts ni changelogs
    for p in (CACHE_DIR, WORK_ROOT):
        if os.path.isdir(p):
            cache.append(p)
    if os.path.isdir(DELIVERY_DIR):
        for n in sorted(os.listdir(DELIVERY_DIR)):
            p = os.path.join(DELIVERY_DIR, n)
            if os.path.isdir(p) and video_files(p):
                dl.append(p)       # copias de entrega al atajo (solo si contienen video)
    return {"dl": dl, "cache": cache, "bak": bak}


def storage_report():
    """Bytes por categoría + otros + total, sin contar dos veces los enlaces
    duros. El total coincide con el de check_storage."""
    groups = storage_groups()
    seen = set()
    r = {k: sum(tree_size(p, seen) for p in groups[k]) for k in ("dl", "cache", "bak")}
    # Lo que no cae en ninguna categoría (índice, snapshot, changelog…)
    r["other"] = tree_size(INTERNAL_DIR, seen) + tree_size(FILES_DIR, seen)
    r["other"] += sum(tree_size(p, seen) for p in indexed_files())     # audio y otros propios
    r["total"] = r["dl"] + r["cache"] + r["bak"] + r["other"]
    r["n_files"] = sum(1 for p in groups["dl"] if os.path.isfile(p))
    return r


def storage_lines():
    """(línea principal, líneas de detalle, ¿pasa el límite?) para el banner."""
    r = storage_report()
    total = r["total"]
    head = f"Espacio: {precise_size(total)} de {precise_size(CLEAN_LIMIT)}"
    if CLEAN_LIMIT > 0:
        head += f" ({total / CLEAN_LIMIT * 100:.0f}%)"
    parts = []
    if r["dl"]:
        parts.append(f"descargas {precise_size(r['dl'])} ({r['n_files']})")
    if r["cache"]:
        parts.append(f"caché {precise_size(r['cache'])}")
    if r["bak"]:
        parts.append(f"descargas en backups {precise_size(r['bak'])}")
    if r["other"]:
        parts.append(f"otros {precise_size(r['other'])}")
    detail, cur = [], ""            # une las partes sin cortarlas ni dejar «·» al final
    for part in parts:
        if cur and len(cur) + 3 + len(part) > safe_width():
            detail.append(cur)
            cur = part
        else:
            cur = cur + " · " + part if cur else part
    if cur:
        detail.append(cur)
    return head, detail, total > CLEAN_LIMIT


def prune_index():
    """Quita del índice las descargas cuyo archivo ya no existe."""
    idx = load_json(INDEX_FILE)
    gone = [k for k, v in idx.items()
            if not (isinstance(v, dict) and v.get("file") and find_saved(v["file"]))]
    for k in gone:
        idx.pop(k, None)
    if gone:
        try:
            save_json(INDEX_FILE, idx)
        except Exception as _ign:
            ignore("prune_index", _ign)
    try:                                   # historial: fuera lo que ya no está en disco
        hist = load_json(HISTORY_FILE)
        for k in list(hist):
            hist[k] = [e for e in (hist[k] or []) if isinstance(e, dict) and e.get("file") and find_saved(e["file"])]
            if not hist[k]:
                hist.pop(k)
        save_json(HISTORY_FILE, hist)
    except Exception as _ign:
        ignore("prune_index", _ign)
    return len(gone)


def remove_paths(paths):
    for p in paths:
        try:
            if os.path.isdir(p) and not os.path.islink(p):
                shutil.rmtree(p, ignore_errors=True)
            elif os.path.lexists(p):
                os.remove(p)
        except OSError as _ign:
            ignore("remove_paths", _ign)


def ensure_dirs():
    for d in (FILES_DIR, DOWNLOAD_DIR, BACKUP_DIR, INTERNAL_DIR, STATE_DIR, SCRIPT_DIR,
              STREAM_CACHE_DIR, WORK_ROOT, DELIVERY_DIR):
        os.makedirs(d, exist_ok=True)


def check_storage():
    """Si .dlpy_internal + dlpy_files superan el límite, ofrece limpiar."""
    seen = set()
    total = tree_size(INTERNAL_DIR, seen) + tree_size(FILES_DIR, seen)
    total += sum(tree_size(p, seen) for p in indexed_files())
    dbg("almacenamiento", {"total": total, "limite": CLEAN_LIMIT})
    if total <= CLEAN_LIMIT:
        return
    groups = storage_groups()
    sizes, seen = {}, set()            # tamaños en orden, sin repetir enlaces duros
    for k in ("dl", "cache", "bak"):
        sizes[k] = sum(tree_size(p, seen) for p in groups[k])
    n_files = sum(1 for p in groups["dl"] if os.path.isfile(p))
    header("ALMACENAMIENTO")
    m_warn(f"DLpy ocupa {human_size(total)} (límite {human_size(CLEAN_LIMIT)}).")
    roast_say(random.choice(STORAGE_JOKES), pin=False)
    kv("Videos descargados", f"{_size_text(sizes['dl'])} · {n_files} archivo(s)")
    kv("Caché y temporales", _size_text(sizes["cache"]))
    kv("Descargas en backups", f"{_size_text(sizes['bak'])} · {len(groups['bak'])} archivo(s)")
    ask_items = [
        ("dl", "videos descargados", "Solo se borran los videos de dlpy_files (y subcarpetas) y sus copias de entrega; audios y demás archivos se conservan."),
        ("cache", "caché y temporales", "Se vuelve a bajar lo que no esté en caché."),
        ("bak", "descargas de backups", "Solo se borran las descargas (video, audio…); scripts, changelogs e índices se conservan."),
    ]
    did = False
    for k, name, warn in ask_items:
        if not groups[k] or not sizes[k]:
            continue
        print()
        note(warn)
        if not ask(f"¿Borrar {name} ({_size_text(sizes[k])})? (s/N) ▸ ", default=False):
            continue
        remove_paths(groups[k])
        did = True
        if k in ("dl", "bak"):
            prune_empty_dirs(FILES_DIR)
        m_ok(f"Borrado: {name}")
        if k == "dl":
            n = prune_index()
            dbg("índice limpiado", n)
    if did:
        ensure_dirs()
        seen = set()
        now = tree_size(INTERNAL_DIR, seen) + tree_size(FILES_DIR, seen)
        now += sum(tree_size(p, seen) for p in indexed_files())
        m_ok(f"Liberado: {_size_text(max(0, total - now))} · ahora ocupa {_size_text(now)}")
    else:
        m_info("Sin cambios.")
    print()


# ───────────────────── [G3] Control de versión ─────────────────────
def is_data_entry(name):
    """Nombre que cuenta como descarga completada (no backups ni basura)."""
    return not (name.startswith(".") or name.endswith((".tmp", ".part", ".ytdl", ".temp"))
                or name in RESERVED)


def files_data_present():
    """Hay descargas o índice de la versión actual."""
    if os.path.isfile(INDEX_FILE):
        return True
    if not os.path.isdir(FILES_DIR):
        return False
    try:
        return any(is_data_entry(n) for n in os.listdir(FILES_DIR))
    except OSError as _ign:
        ignore("files_data_present", _ign)
        return False


def migrate_files_to_backup(dest):
    """Mueve descargas e índice de la versión actual a dest (al actualizar)."""
    moved = 0
    if os.path.isdir(FILES_DIR):
        for n in sorted(os.listdir(FILES_DIR)):
            if not is_data_entry(n):
                continue
            move_file(os.path.join(FILES_DIR, n), os.path.join(dest, n))
            moved += 1
    if os.path.isfile(INDEX_FILE):
        os.makedirs(os.path.join(dest, "_internal"), exist_ok=True)
        move_file(INDEX_FILE, os.path.join(dest, "_internal", "index.json"))
        moved += 1
    return moved


def internal_download_items():
    """Elementos de dlpy_internal (salvo state/ y script/) que contienen descargas."""
    items = []
    if not os.path.isdir(INTERNAL_DIR):
        return items
    for n in sorted(os.listdir(INTERNAL_DIR)):
        p = os.path.join(INTERNAL_DIR, n)
        if p in (STATE_DIR, SCRIPT_DIR) or os.path.islink(p):
            continue
        if os.path.isdir(p):
            if download_files(p):
                items.append(p)
        elif is_download_file(p):
            items.append(p)
    return items


def offer_internal_backup(dest):
    """Pregunta si mover también las descargas de dlpy_internal al backup.
    Devuelve cuántos elementos se movieron."""
    items = internal_download_items()
    if not items:
        return 0
    size = sum(tree_size(p, set()) for p in items)
    print()
    note(f"Quedan descargas en {INTERNAL_NAME} (entregas, caché, work…). "
         f"Al cambiar de versión esa carpeta se borra entera.")
    if not ask(f"¿Mover las descargas de {INTERNAL_NAME} ({_size_text(size)}) "
               f"a backups? Si no, se borrarán. (s/N) ▸ ", default=False):
        return 0
    base = os.path.join(dest, "_internal")
    os.makedirs(base, exist_ok=True)
    moved = 0
    for p in items:
        try:
            move_file(p, _free_path(os.path.join(base, os.path.basename(p))))
            moved += 1
        except OSError as e:
            m_warn(f"No se pudo mover {os.path.basename(p)}: {e}")
    ensure_dirs()
    if moved:
        m_ok(f"{INTERNAL_NAME}: {moved} elemento(s) movido(s) a backups.")
    return moved


def archive_previous(prev, snapshot_version, announce=True):
    """Todo lo de la versión anterior va a backups/<prev>/ (script, changelog, datos). Devuelve el nombre de la
    carpeta creada en backups/, True si no había nada que archivar o False si falló (no se debe seguir)."""
    has_script = os.path.isfile(SNAPSHOT_FILE) and snapshot_version == prev
    has_data = files_data_present()
    if not has_script and not has_data:
        return True
    dest = next_backup_dir(prev)
    try:
        os.makedirs(dest)
    except Exception as e:
        m_err(f"No se pudo crear {dest}: {e}")
        return False
    ok_script = backup_script(prev, snapshot_version, dest, announce)
    moved = 0
    if has_data:
        try:
            moved = migrate_files_to_backup(dest)
        except Exception as e:
            m_err(f"Error al mover datos: {e}")
            return False
    moved += offer_internal_backup(dest)
    if not ok_script and not moved:
        try:
            os.rmdir(dest)
        except OSError as _ign:
            ignore("archive_previous", _ign)
        return True
    return os.path.basename(dest)


def make_downgrade_record(stored, current, pending=None, now=None):
    """Registro de una bajada de `stored` a `current`. La causa viene de `pending` (lo anota
    install_recovered al instalar una versión más vieja) solo si apunta a esta versión; si no,
    el archivo se cambió fuera de DLpy: «externa»."""
    p = pending if isinstance(pending, dict) else {}
    causa = p.get("causa") if p.get("a") == current and p.get("causa") in DOWNGRADE_CAUSES else "externa"
    rec = {"de": stored, "a": current, "cuando": int(time.time() if now is None else now),
           "causa": causa, "salto": downgrade_span(stored, current)}
    if p.get("a") == current and p.get("hold") is False:
        rec["hold"] = False                  # eligió no quedarse en la versión vieja: no bloquea actualizar
    return rec


def downgrade_hold(version=None, data=None):
    """Versión de la que se bajó a propósito hasta `version` (la actual), o None. Mira la bajada
    pendiente y la última registrada; deja de valer sola cuando la versión instalada cambia."""
    ver = version or VERSION
    data = load_json(DOWNGRADE_FILE) if data is None else data
    cands = []
    if isinstance(data.get("pending"), dict):
        cands.append(data["pending"])
    hist = data.get("history")
    if isinstance(hist, list) and hist and isinstance(hist[-1], dict):
        cands.append(hist[-1])
    for r in cands:
        de = r.get("de")
        if (r.get("a") == ver and r.get("causa") in DOWNGRADE_DELIBERATE and r.get("hold") is not False
                and isinstance(de, str) and vtuple(de) > vtuple(ver)):
            return de
    return None


def mark_downgrade_pending(frm, to, causa, hold=True):
    """Anota que DLpy está a punto de instalar la `to` (más vieja que la `frm` en uso).
    hold=False: la persona no quiso quedarse en ella, así que no se bloquea la actualización."""
    try:
        data = load_json(DOWNGRADE_FILE)
        data["pending"] = {"de": frm, "a": to, "causa": causa, "cuando": int(time.time())}
        if not hold:
            data["pending"]["hold"] = False
        os.makedirs(STATE_DIR, exist_ok=True)
        save_json(DOWNGRADE_FILE, data)
    except Exception as _ign:
        ignore("mark_downgrade_pending", _ign)


DOWNGRADE_WHY = {"manual": "Instalada a propósito desde --versions.",
                 "recuperacion": "Recuperada tras un fallo.",
                 "externa": "El dlpy.py se reemplazó por uno más viejo fuera de DLpy "
                            "(copia manual, atajo o copia antigua)."}


def downgrade_notice(stored):
    """Registro de la bajada `stored` → VERSION (sin escribirlo a disco ni imprimir: lo cuenta la tarjeta
    de show_update_card)."""
    return make_downgrade_record(stored, VERSION, load_json(DOWNGRADE_FILE).get("pending"))


def update_card_rows(stored, current, down, archived, freed, inner):
    """Líneas (pintadas) de la tarjeta de un cambio de versión. `down`: registro de la bajada o None;
    `archived`: carpeta creada en backups/ (str) o True si no había nada que archivar; `freed`: bytes
    liberados al reiniciar .dlpy_internal, o None si no se pudo."""
    if down:
        rows = card_text_rows(f"Bajada de versión {stored} → {current}", inner, "white", True, "!", "amber")
        rows += card_text_rows(DOWNGRADE_WHY.get(down.get("causa"), DOWNGRADE_WHY["externa"]), inner)
    else:
        rows = card_text_rows(f"Actualizada {stored} → {current}", inner, "white", True, "✓", "mint")
    rows += card_text_rows(f"anterior en backups/{archived}" if isinstance(archived, str)
                           else "sin copia anterior que archivar", inner)
    if freed is None:
        rows += card_text_rows(f"no se pudo reiniciar {INTERNAL_NAME}", inner, "amber", False, "!", "amber")
    else:
        rows += card_text_rows("carpeta interna reiniciada", inner)
    return rows


def show_update_card(stored, down, archived, freed):
    """Una sola tarjeta con lo ocurrido al cambiar de versión (en vez de varios mensajes sueltos)."""
    try:
        lines = static_card(update_card_rows(stored, VERSION, down, archived, freed, card_inner()))
    except Exception as _ign:
        ignore("show_update_card", _ign)
        m_ok(f"Versión {stored} → {VERSION}")
        return
    print()
    for ln in lines:
        print(ln)
    print()


def downgrade_commit(rec):
    """Guarda `rec` en el historial (últimas 20) y descarta la bajada pendiente."""
    try:
        hist = load_json(DOWNGRADE_FILE).get("history")
        hist = [h for h in hist if isinstance(h, dict)] if isinstance(hist, list) else []
        os.makedirs(STATE_DIR, exist_ok=True)
        save_json(DOWNGRADE_FILE, {"history": (hist + [rec])[-20:]})
    except Exception as _ign:
        ignore("downgrade_commit", _ign)


def internal_dir_safe(internal=None, files=None):
    """True si `internal` es de verdad <files>/.dlpy_internal (carpeta real, no un enlace): solo eso se borra entero."""
    internal = INTERNAL_DIR if internal is None else internal
    files = FILES_DIR if files is None else files
    try:
        return (os.path.basename(internal) == INTERNAL_NAME
                and os.path.abspath(os.path.dirname(internal)) == os.path.abspath(files)
                and os.path.isdir(internal) and not os.path.islink(internal))
    except OSError:
        return False


def reset_internal(internal=None, files=None):
    """Cada subida o bajada de versión empieza de cero: borra .dlpy_internal entera (estado, variables DLPY_*,
    caché, work, entregas, copia del script y changelog) y la deja vacía. Lo de la versión anterior que importa
    (script, índice y descargas) ya se archivó en backups/ antes de llamar aquí. Se renombra a «.old» y se borra
    al final: si algo se corta, drop_internal_leftovers limpia el resto en el siguiente arranque. Devuelve los
    bytes liberados, o None si no se pudo (la carpeta se deja como estaba). No crea las subcarpetas: eso es de
    ensure_dirs."""
    internal = INTERNAL_DIR if internal is None else internal
    files = FILES_DIR if files is None else files
    old = internal + ".old"
    try:
        if not os.path.lexists(internal):
            os.makedirs(internal, exist_ok=True)
            return 0
        if not internal_dir_safe(internal, files):
            return None
        if os.path.isdir(old) and not os.path.islink(old):
            shutil.rmtree(old, ignore_errors=True)          # resto de un reinicio cortado
        size = tree_size(internal)
        os.replace(internal, old)
        try:
            os.makedirs(internal)
        except OSError:
            os.replace(old, internal)                       # no se pudo crear la nueva: se deja la de antes
            return None
        shutil.rmtree(old, ignore_errors=True)
        return size
    except OSError as _ign:
        ignore("reset_internal", _ign)
        return None


def drop_internal_leftovers():
    """Borra «.dlpy_internal.old»: resto de un reinicio que se cortó antes de terminar."""
    old = INTERNAL_DIR + ".old"
    try:
        if os.path.isdir(old) and not os.path.islink(old):
            shutil.rmtree(old, ignore_errors=True)
    except OSError as _ign:
        ignore("drop_internal_leftovers", _ign)


def check_version():
    state = load_json(VERSION_FILE)
    stored = state.get("version")

    if stored == VERSION:
        if not os.path.isfile(SNAPSHOT_FILE):
            save_snapshot()
            save_json(VERSION_FILE, {"version": VERSION, "snapshot_version": VERSION})
        elif state.get("snapshot_version") == VERSION:
            try:                              # misma versión: ¿igual que la copia guardada?
                snap_t, me_t = read_text(SNAPSHOT_FILE), read_text(SCRIPT_PATH)
            except (OSError, ValueError) as _ign:
                ignore("check_version", _ign)
                snap_t = me_t = ""
            if compare_texts(snap_t, me_t) == "distinto":
                add, rem = diff_counts(diff_lines(snap_t, me_t, "copia guardada", "instalada"))
                if RELEASE_SAME["igual"]:
                    # idéntica al Release: la copia guardada es la vieja; se reemplaza
                    save_snapshot()
                    m_ok(f"La {VERSION} instalada es idéntica al Release: copia guardada reemplazada "
                         f"(-{rem} +{add} líneas).")
                else:
                    m_warn(f"La {VERSION} instalada difiere de la copia guardada (-{rem} +{add} líneas): "
                           f"se editó sin subir la versión.")
        ensure_changelog()               # changelog.md ← release notes de GitHub (versión actual e inferiores)
        return True

    # ── Actualización (o primera instalación) ──
    prev = stored or "0.0.0"
    down = None
    if version_move(stored, VERSION) == "baja":
        down = downgrade_notice(stored)
    archived = archive_previous(prev, state.get("snapshot_version"), announce=bool(stored))
    if not archived:
        return False

    freed = 0
    if stored:                # subida o bajada: .dlpy_internal empieza de cero (ya se archivó lo importante)
        was_running = os.path.isfile(RUNNING_FILE)
        freed = reset_internal()
        if freed is not None:
            ensure_dirs()
            if was_running:
                mark_running()           # la ejecución en curso sigue vigilada (se borró con el resto)
        show_update_card(stored, down, archived, freed)
    save_snapshot()          # copia completa (con changelog) para futuros backups
    save_json(VERSION_FILE, {"version": VERSION, "snapshot_version": VERSION})
    ensure_changelog()       # changelog.md ← release notes de GitHub (versión actual e inferiores)
    if down:
        downgrade_commit(down)
    return True


# ───────────────────── [G5] Releases de GitHub y backups (listado) ─────────────────────
def repo_info(spec=None):
    """(dueño, repo) de «dueño/repo» (UPDATE_REPO por omisión), o None si no tiene esa forma."""
    m = re.match(r"^([\w.-]+)/([\w.-]+)$", (UPDATE_REPO if spec is None else spec) or "")
    return m.groups() if m else None


REL_PER_PAGE = 100          # Releases por página de la API de GitHub
REL_MAX_PAGES = 5           # hasta 500 Releases (changelog.md los usa todos)


def _releases_page(info, page, timeout):
    """Lista JSON de una página de /releases, o None si falla."""
    import urllib.request
    api = f"https://api.github.com/repos/{info[0]}/{info[1]}/releases?per_page={REL_PER_PAGE}&page={page}"
    req = urllib.request.Request(api, headers={
        "User-Agent": "DLpy-updater", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except Exception as _ign:
        ignore("remote_releases", _ign)
        return None


def _releases_data(timeout=8, pages=REL_MAX_PAGES):
    """(respuesta JSON de la API de GitHub para /releases con todas las páginas, info) o (None, info) si falla
    la primera. Sigue pidiendo páginas mientras vengan llenas."""
    info = repo_info()
    if not info:
        return None, None
    gh_notice(f"leyendo los Releases de {info[0]}/{info[1]} (versiones y changelog)")
    data = []
    for page in range(1, pages + 1):
        chunk = _releases_page(info, page, timeout)
        if not isinstance(chunk, list):
            if page == 1:
                return None, info
            break
        data += chunk
        if len(chunk) < REL_PER_PAGE:
            break
    return data, info


REL_TAG_RE = re.compile(r"^[vV]?(\d+\.\d+\.\d+)$")


def parse_releases(data, info):
    """[{ver, url, notes, date}] de la respuesta de la API de GitHub para /releases, del más nuevo al más viejo.
    La versión sale de la etiqueta («vX.Y.Z» o «X.Y.Z») o del nombre del archivo adjunto; el código, del adjunto
    «dlpy.py» o «dlpy_x.y.z.py» y, si el Release no trae ninguno, del dlpy.py de esa etiqueta. `notes` es el
    texto del Release (release notes) y `date` su fecha (AAAA-MM-DD). Ignora borradores y prereleases."""
    owner, repo = info
    out, seen = [], set()
    for it in data if isinstance(data, list) else []:
        if not isinstance(it, dict) or it.get("draft") or it.get("prerelease"):
            continue
        tag = str(it.get("tag_name") or "")
        m = REL_TAG_RE.match(tag)
        ver, url = (m.group(1) if m else None), None
        for a in it.get("assets") or []:
            if not isinstance(a, dict):
                continue
            name = str(a.get("name") or "")
            am = VER_FILE_RE.match(name)
            if (name == "dlpy.py" or am) and a.get("browser_download_url"):
                ver = ver or (am.group(1) if am else None)
                url = str(a["browser_download_url"])
                break
        if not ver or ver in seen:
            continue
        if not url:
            if not tag:
                continue
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/{urllib.parse.quote(tag)}/dlpy.py"
        seen.add(ver)
        out.append({"ver": ver, "url": url, "notes": norm_text(str(it.get("body") or "")).strip(),
                    "date": str(it.get("published_at") or it.get("created_at") or "")[:10]})
    out.sort(key=lambda x: vtuple(x["ver"]), reverse=True)
    return out


def remote_releases(timeout=8):
    """[{ver, url, notes, date}] de los Releases de GitHub, o None si no se pudieron leer. Guarda lo leído en
    RELEASES para que changelog.md salga de ahí sin pedirlo otra vez."""
    data, info = _releases_data(timeout)
    rels = parse_releases(data, info) if data is not None else None
    if rels is not None:
        RELEASES["list"] = rels
    return rels


def fetch_latest_release(timeout=5):
    """{ver, text, url, notes, date} del Release más nuevo con un dlpy.py válido, o None."""
    rels = remote_releases(timeout)
    for rel in (rels or [])[:3]:
        text = fetch_remote_script(timeout, rel["url"])
        real = remote_script_version(text) if text else None
        if real:
            return {"ver": real, "text": text, "url": rel["url"], "notes": rel["notes"], "date": rel["date"]}
    return None


def backup_versions():
    """[(versión, ruta)] de los backups que DLpy guarda solo al actualizar
    (dlpy_files/backups/<versión>/dlpy_<versión>.py). Sirven sin internet."""
    out = []
    try:
        for n in os.listdir(BACKUP_DIR):
            if not VER_DIR_RE.match(n):
                continue
            ver = n.split("-")[0]
            p = os.path.join(BACKUP_DIR, n, f"dlpy_{ver}.py")
            if os.path.isfile(p):
                out.append((ver, p))
    except OSError as _ign:
        ignore("backup_versions", _ign)
    return out


def release_rows(releases, backups=None):
    """Filas de la lista de --versions: los Releases, del más nuevo al más viejo. Solo si no hay Releases
    (sin red o sin publicar) se usan los backups de este equipo, para poder recuperarse tras un fallo."""
    rows = [{"ver": r["ver"], "src": "release", "ref": r["url"], "notes": r["notes"],
             "date": r.get("date") or "", "label": "Release"} for r in releases or []]
    if rows:
        return rows
    for ver, path in sorted(backups or [], key=lambda x: (vtuple(x[0]), os.path.basename(os.path.dirname(x[1]))),
                            reverse=True):
        d = os.path.basename(os.path.dirname(path))
        rows.append({"ver": ver, "src": "backup", "ref": path, "notes": None, "date": "",
                     "label": "backup" + (("-" + d.split("-", 1)[1]) if "-" in d else "")})
    return rows


# ─────────── [G6] Comparar versiones: huellas y diferencias ───────────
def norm_text(text):
    """Texto con saltos de línea \\n (para comparar sin que CRLF cuente como cambio)."""
    return (text or "").replace("\r\n", "\n").replace("\r", "\n")


def has_changelog(text):
    return bool(CL_RE.search(norm_text(text)))


def strip_changelog(text):
    """El código sin el bloque CHANGELOG (un Release o una copia vieja puede no traerlo)."""
    t = norm_text(text)
    m = CL_RE.search(t)
    return t[:m.start()] + t[m.end():] if m else t


def text_fingerprints(text):
    """(huella del archivo completo, huella del código sin changelog), SHA-256."""
    import hashlib
    n = norm_text(text)
    return (hashlib.sha256(n.encode("utf-8")).hexdigest(),
            hashlib.sha256(strip_changelog(n).encode("utf-8")).hexdigest())


def compare_texts(a, b):
    """'igual' · 'changelog' (mismo código, otro changelog) · 'distinto' (otro código).
    Si uno de los dos no trae changelog (el instalado) solo cuenta el código."""
    fa, ca = text_fingerprints(a)
    fb, cb = text_fingerprints(b)
    if ca != cb:
        return "distinto"
    if fa == fb or not has_changelog(a) or not has_changelog(b):
        return "igual"
    return "changelog"


def diff_lines(a_text, b_text, label_a, label_b, mode="distinto"):
    """Líneas de diff unificado. mode 'distinto' ignora el changelog; 'changelog' lo incluye."""
    import difflib
    a = strip_changelog(a_text) if mode == "distinto" else norm_text(a_text)
    b = strip_changelog(b_text) if mode == "distinto" else norm_text(b_text)
    return list(difflib.unified_diff(a.splitlines(), b.splitlines(),
                                     label_a, label_b, n=1, lineterm=""))


def diff_counts(lines):
    add = sum(1 for ln in lines if ln.startswith("+") and not ln.startswith("+++"))
    rem = sum(1 for ln in lines if ln.startswith("-") and not ln.startswith("---"))
    return add, rem


# ───────────────────── [G7] Fallos: historial y avisos ─────────────────────
# Fallos: historial en state/crash_log.json (crash.json solo guardaba el último)
def load_crashes():
    """[{version, code, error, time}] de todos los fallos guardados (más viejo primero).
    `code` = huella del código que falló (None si no se pudo calcular)."""
    log = load_json(CRASH_LOG_FILE).get("crashes")
    out = [c for c in log if isinstance(c, dict) and c.get("version")] if isinstance(log, list) else []
    last = load_json(CRASH_FILE)                     # solo el último
    if last.get("version") and not any(
            c.get("version") == last["version"] and c.get("time") == last.get("time") for c in out):
        out.append({"version": last["version"], "code": None,
                    "error": last.get("error") or "", "time": last.get("time") or 0})
    return out


def crashes_json_path():
    """Ruta del JSON de fallos: .dlpy_internal/crashes_dlpy.json, o DLPY_CRASHES_JSON si se define."""
    custom = os.environ.get("DLPY_CRASHES_JSON", "").strip()
    if custom:
        return os.path.expanduser(custom)
    return CRASHES_JSON_FILE


def export_crashes_json():
    """Escribe crashes_dlpy.json con las versiones que fallaron y la causa de cada fallo.
    Nunca revienta."""
    try:
        path = crashes_json_path()
        if not path:
            return
        by_ver = {}
        for c in load_crashes():
            by_ver.setdefault(c["version"], []).append({
                "fecha": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(c.get("time") or 0)),
                "causa": c.get("error") or "",
                "huella": c.get("code")})
        vers = sorted(by_ver, key=vtuple)
        data = {"actualizado": time.strftime("%Y-%m-%d %H:%M:%S"),
                "versiones_con_fallo": vers,
                "fallos": {v: by_ver[v] for v in vers}}
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        save_json(path, data)
    except Exception as _ign:
        ignore("export_crashes_json", _ign)


def record_crash(version, text, error, when=None):
    """Anota un fallo (con la huella del código que falló). Nunca revienta."""
    try:
        entry = {"version": version, "code": text_fingerprints(text)[1] if text else None,
                 "error": str(error)[:300], "time": int(when or time.time())}
        crashes = (load_crashes() + [entry])[-50:]
        os.makedirs(os.path.dirname(CRASH_LOG_FILE), exist_ok=True)
        save_json(CRASH_LOG_FILE, {"crashes": crashes})
    except Exception as _ign:
        ignore("record_crash", _ign)
    export_crashes_json()


def crash_match(ver, text, crashes=None):
    """None (nunca falló) · ('igual', fallo) el código es el MISMO que falló ·
    ('distinta', fallo) misma versión pero otro código · ('sin_huella', fallo)."""
    cs = [c for c in (load_crashes() if crashes is None else crashes) if c.get("version") == ver]
    if not cs:
        return None
    code = text_fingerprints(text)[1] if text else None
    if code:
        for c in reversed(cs):
            if c.get("code") == code:
                return ("igual", c)
        if any(c.get("code") for c in cs):
            return ("distinta", cs[-1])
    return ("sin_huella", cs[-1])


def crash_when(entry):
    try:
        return time.strftime("%d/%m %H:%M", time.localtime(int(entry.get("time") or 0)))
    except (OverflowError, OSError, ValueError):
        return "?"


def show_crash_warning(ver, text, crashes=None):
    """Avisa si la `ver` ya falló. Devuelve 'igual' / 'distinta' / 'sin_huella' / None."""
    hit = crash_match(ver, text, crashes)
    if not hit:
        return None
    kind, c = hit
    err = c.get("error") or ""
    if kind == "igual":
        m_err(f"La {ver} es IDÉNTICA a la que falló el {crash_when(c)}.")
        if err:
            note(f"Error: {err}")
    elif kind == "distinta":
        m_warn(f"La {ver} ya falló el {crash_when(c)}, pero este código es distinto "
               f"(puede que ya esté corregida).")
    else:
        m_warn(f"La {ver} ya falló el {crash_when(c)} (sin huella guardada: no se puede saber "
               f"si es el mismo código).")
    return kind


# ───────────────────── [G8] Pantalla de versiones (--versions) ─────────────────────
def _wrap_tokens(tokens, indent, width, sep="  "):
    """tokens = [(texto_plano, texto_pintado)] → líneas que caben en `width`."""
    lines, cur, curlen = [], [], 0
    for plain, painted in tokens:
        add = len(plain) + (len(sep) if cur else 0)
        if cur and indent + curlen + add > width:
            lines.append(" " * indent + sep.join(cur))
            cur, curlen, add = [], 0, len(plain)
        cur.append(painted)
        curlen += add
    if cur:
        lines.append(" " * indent + sep.join(cur))
    return lines


def format_version_rows(rows, cur, upd, crashes, width=None, start=1):
    """Líneas de la lista numerada de versiones (con colores si el terminal los admite)."""
    width = width or safe_width()
    count = {}
    for c in crashes:
        count[c["version"]] = count.get(c["version"], 0) + 1
    out = []
    for i, row in enumerate(rows, start):
        ver = row["ver"]
        head = f"{i}  {ver}"
        toks = [(head, paint(str(i), "orange", True) + "  " + paint(ver, "white", True))]
        extra = row.get("date") or (row.get("label") if row.get("src") == "backup" else "")
        if extra:
            toks.append((extra, paint(extra, "gray")))
        out += _wrap_tokens(toks, 2, width, " · ")
        flags = []
        if ver == cur:
            flags.append(("✓ actual", "green"))
        if upd and ver == upd:
            flags.append(("⬆ la de actualizar", "orange"))
        if ver in count:
            n = count[ver]
            flags.append(("✖ crasheó" + (f" ×{n}" if n > 1 else ""), "red"))
        if flags:
            out += _wrap_tokens([(t, paint(t, c)) for t, c in flags], 6, width)
    return out


def print_version_legend():
    note("✓ actual · ⬆ la de actualizar · ✖ crasheó")


def install_text(src, ver):
    """Texto válido (con versión y compilable) del origen, o None."""
    ref = src["ref"]
    if ref.startswith("http"):
        m_info(f"Descargando la {ver} desde {src['label']}...")
        return fetch_remote_script(timeout=20, url=ref)
    try:
        text = read_text(ref)
        return text if remote_script_version(text) and compile(text, "dlpy.py", "exec") else None
    except Exception as _ign:
        ignore("install_text", _ign)
        return None


# ╔════════════════════════════════════════════════════════════════════════════════════════════════╗
# ║ ÁREA H · RECUPERACIÓN Y CACHÉ — recuperación, caché de streams, reanudación, carpeta interna   ║
# ╚════════════════════════════════════════════════════════════════════════════════════════════════╝
# ───────────────────── [H1] Recuperación tras un fallo ─────────────────────
def skip_update_after_recovery(remote, crashed, match=None):
    """True si la versión del Release es la que falló (o más vieja que ella): no se ofrece.
    `match` = resultado de crash_match: con el mismo número pero otro código ('distinta')
    sí se ofrece, porque puede estar corregida."""
    if not crashed:
        return False
    if vtuple(remote) == vtuple(crashed) and match == "distinta":
        return False
    return vtuple(remote) <= vtuple(crashed)


def clear_recovered():
    try:
        if os.path.isfile(RECOVERED_FILE):
            os.remove(RECOVERED_FILE)
    except OSError as _ign:
        ignore("clear_recovered", _ign)


def parse_menu_choice(ans, n):
    """0 = no volver (vacío / 0 / n / no); 1..n = esa opción; None = no se entiende."""
    a = (ans or "").strip().lower()
    if a in ("", "0", "n", "no"):
        return 0
    if a.isdecimal() and 1 <= int(a) <= n:
        return int(a)
    return None


def good_versions():
    v = load_json(GOOD_FILE).get("versions")
    return [x for x in v if isinstance(x, str)] if isinstance(v, list) else []


def mark_good(version=None):
    """Anota que esta versión terminó una ejecución sin fallar."""
    try:
        v = version or VERSION
        good = good_versions()
        if v not in good:
            good.append(v)
            os.makedirs(STATE_DIR, exist_ok=True)
            save_json(GOOD_FILE, {"versions": good[-50:]})
    except Exception as _ign:
        ignore("mark_good", _ign)


def mark_running():
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        save_json(RUNNING_FILE, {"version": VERSION, "pid": os.getpid(), "time": int(time.time())})
    except Exception as _ign:
        ignore("mark_running", _ign)


def clear_running():
    try:
        if os.path.isfile(RUNNING_FILE):
            os.remove(RUNNING_FILE)
    except OSError as _ign:
        ignore("clear_running", _ign)


def abrupt_why(prev):
    """Texto del aviso tras un cierre inesperado; dice en qué pregunta estaba si se sabe."""
    ver = (prev or {}).get("version")
    where = (prev or {}).get("prompt")
    return (f"La ejecución anterior de la {ver} se cortó"
            + (f" en la pregunta «{where}»" if where else " sin terminar")
            + " y esa versión aún no había terminado bien.")


def should_offer_after_abrupt(prev, good):
    """Tras un cierre inesperado (sin traceback) solo se ofrece volver atrás si esa
    versión aún no había terminado bien ninguna ejecución (versión recién instalada)."""
    ver = (prev or {}).get("version")
    return bool(ver) and ver not in (good or [])


def install_recovered(ver, text, crashed, hold=True):
    """Reemplaza dlpy.py por `text` (versión `ver`). Antes guarda el actual en
    script/crash/. True si quedó instalada."""
    try:
        cdir = os.path.join(SCRIPT_DIR, "crash")
        os.makedirs(cdir, exist_ok=True)
        if os.path.isfile(SCRIPT_PATH):
            tag = "crash" if crashed else "antes"
            copy_file(SCRIPT_PATH, _free_path(os.path.join(cdir, f"dlpy_{VERSION}_{tag}.py")))
        write_text(SCRIPT_PATH, text)
    except Exception as e:
        m_err(f"No se pudo instalar la {ver}: {e}")
        return False
    if version_move(VERSION, ver) == "baja":          # downgrade a propósito: lo anota check_version al arrancar
        mark_downgrade_pending(VERSION, ver, "recuperacion" if crashed else "manual", hold)
    if crashed and hold:
        try:
            save_json(RECOVERED_FILE, {"crashed": crashed, "restored": ver, "time": int(time.time())})
        except Exception as _ign:
            ignore("install_recovered", _ign)
    return True


def offer_recovery(crashed, why):
    """Lista los Releases de GitHub (y, solo si no se pueden leer, los backups de este equipo) marcando actual, el
    que instalaría al actualizar y los fallos, y deja elegir uno: muestra sus release notes y Enter confirma la
    instalación. Si se instala, la ejecuta y termina (SystemExit). False si no se hizo nada.
    `crashed` = versión que falló (None en modo manual con --versions)."""
    cbar = Bar()
    cbar.start("Buscando versiones")
    try:
        releases = remote_releases()
    finally:
        cbar.stop()
    backups = backup_versions() if not releases else []
    if releases is None:
        m_warn("No se pudieron leer los Releases de GitHub" + (": uso los backups de este equipo." if backups else "."))
    elif not releases:
        m_warn("El repositorio no tiene Releases publicados" + (": uso los backups de este equipo." if backups else "."))
    rows = release_rows(releases, backups)
    if not rows:
        m_warn("No hay versiones para recuperar (Releases de GitHub o backups).")
        return False
    upd = rows[0]["ver"] if rows[0]["src"] == "release" else None
    shown = rows[:20]
    crashes = load_crashes()
    per = [format_version_rows([r], VERSION, upd, crashes, start=i) for i, r in enumerate(shown, 1)]
    legend_txt = "✓ actual · ⬆ la de actualizar · ✖ crasheó"

    def draw(full):
        """Pantalla de versiones dentro de las 26 líneas; True si quedan ocultas (se ven con «m»)."""
        if full:
            hide_keyboard(0.3)
        clear_screen()
        if full and CARD["pin"]:
            card_thread_stop()          # lista completa: se suelta el banner anclado para poder deslizar
        header("VERSIONES", gap=False)
        w = max(8, term_width() - 4)
        used = (banner_height() + 1 + 1 + 1                       # banner, cabecera, nota de «más», prompt
                + (len(wrap_text(why, w)) if why else 0)
                + (1 if upd is None else 0)
                + len(wrap_text(legend_txt, w)))
        k, tot = 0, 0
        for ls in per:
            if not full and k >= 1 and tot + len(ls) > ui_lines() - used:
                break
            tot += len(ls)
            k += 1
        if why:
            m_warn(why)
        if upd is None:
            note("Sin Releases a la vista: no se sabe cuál usaría al actualizar.")
        for ls in per[:k]:
            for ln in ls:
                print(ln)
        if k < len(per):
            note(f"(+{len(per) - k} más: «m»)")
        elif len(rows) > len(shown):
            note(f"(+{len(rows) - len(shown)} más antiguas sin mostrar)")
        print_version_legend()
        return k < len(per)

    def vplain(hid):
        return "¿Instalar? Nº · m más (Enter = no) ▸ " if hid else "¿Instalar alguna? Número (Enter = no) ▸ "

    def vprompt(hid):
        hint("¿Instalar alguna? n.º" + (" · m más" if hid else "") + " · {Enter = no}")
        return PROMPT

    hid = draw(False)
    cur = vprompt(hid)
    while True:
        try:
            ans = ask_line(cur, True, vplain(hid))
        except (EOFError, KeyboardInterrupt):
            return False
        if (ans or "").strip().lower() == "m" and hid:
            hid = draw(True)
            cur = vprompt(hid)
            continue
        n = parse_menu_choice(ans, len(shown))
        if n is None:
            cur = retry_prompt(cur, ans, bad_prompt(f"1-{len(shown)}" + (", m" if hid else "") + " o Enter"),
                               f"Escribe un número de 1 a {len(shown)}" + (" (o m)" if hid else "")
                               + " (o Enter para no volver).")
            continue
        break
    if n == 0:
        return False
    row = shown[n - 1]
    ver = row["ver"]
    if not confirm_install(f"Instalar la {ver}" + ("" if row["src"] == "release" else " (backup)"), ver,
                           row["notes"], row["date"], unavailable="Los backups no traen release notes."):
        return False
    text = install_text(row, ver)
    if not text:
        m_err(f"No se pudo obtener la {ver} (descarga fallida o archivo no válido).")
        return False
    try:
        if text_fingerprints(text)[1] == text_fingerprints(read_text(SCRIPT_PATH))[1]:
            m_info(f"La {ver} ({row['label']}) es idéntica a la instalada; no hay nada que cambiar.")
            return False
    except (OSError, ValueError) as _ign:
        ignore("offer_recovery", _ign)
    if show_crash_warning(ver, text) == "igual" and not ask(f"¿Instalar la {ver} igualmente?", default=False):
        return False
    down = version_move(VERSION, ver) == "baja"
    stay = True
    if down:                                  # versión más vieja: ¿bloquear actualizar hasta que salga otra?
        stay = ask(f"¿Quedarte en la {ver} hasta que salga una más nueva?", default=False)
    if not install_recovered(ver, text, crashed, stay):
        return False
    clear_running()
    m_check(f"DLpy {ver} · restaurada ({row['label']})")
    if not crashed and down:
        if stay:
            note(f"Bajaste de la {VERSION} a la {ver}. No se ofrecerá actualizar hasta que haya un Release con una "
                 f"versión más nueva que la {VERSION}; con --actualizar puedes volver a instalarla.")
        else:
            note(f"Bajaste de la {VERSION} a la {ver}. En el próximo arranque se volverá a ofrecer "
                 f"actualizar.")
    if crashed:
        if stay:
            note(f"Se recuperó la {ver} porque la {crashed} falló. Mientras no haya un Release con una versión "
                 f"más nueva que la {crashed} no se ofrecerá actualizar; con --actualizar puedes "
                 f"volver a instalarla.")
        else:
            note(f"Se recuperó la {ver} porque la {crashed} falló. En el próximo arranque se volverá "
                 f"a ofrecer actualizar.")
    reexec_script()                                       # termina con SystemExit
    return True


def handle_crash(err, tb):
    """Fallo no controlado: lo resume, lo guarda en state/crash.json y ofrece volver atrás."""
    m_err(f"DLpy {VERSION} falló: {type(err).__name__}: {err}")
    where = next((ln.strip() for ln in reversed(tb.splitlines()) if ln.strip().startswith("File ")), "")
    if where:
        note(where)
    if DEBUG:
        print(tb)
    try:
        text = read_text(SCRIPT_PATH)
    except (OSError, ValueError):
        text = None
    record_crash(VERSION, text, f"{type(err).__name__}: {err}")     # historial con huella
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        save_json(CRASH_FILE, {"version": VERSION, "error": f"{type(err).__name__}: {err}",
                               "time": int(time.time()), "traceback": tb[-4000:]})
    except Exception as _ign:
        ignore("handle_crash", _ign)
    try:
        offer_recovery(VERSION, f"La versión {VERSION} se cerró por un error.")
    except (EOFError, KeyboardInterrupt):
        pass
    except SystemExit:
        raise
    except Exception as e2:
        m_warn(f"No se pudo ofrecer la recuperación: {e2}")
    return 1


def run_guarded(entry):
    """Ejecuta entry() vigilando fallos: marca «en curso» mientras corre; si revienta con
    una excepción o la ejecución anterior quedó cortada, ofrece volver a una versión
    guardada. --selftest / --sistema / --perfil / --2shortcuts / --scm / --scb / --shortcutpick no se vigilan."""
    import traceback
    args = norm_args(sys.argv[1:])           # «—versions» (raya larga de iOS) = «--versions»
    if "--selftest" in args or "--sistema" in args or "--perfil" in args or wants_2shortcuts(args) or wants_scm(args) or wants_scb(args) \
            or _wants(args, "shortcutpick"):
        return entry()
    if "--versions" in args:                 # lista manual, sin que haya fallado nada
        clear_screen()
        offer_recovery(None, None)
        return 0
    nested = getattr(sys, "_dlpy_guarded", False)     # tras actualizar/restaurar (runpy)
    global NESTED_IOS
    NESTED_IOS = bool(nested)
    sys._dlpy_guarded = True
    try:
        if not nested:
            prev = load_json(RUNNING_FILE)
            if prev and should_offer_after_abrupt(prev, good_versions()):
                try:
                    pv = prev.get("version")
                    record_crash(pv, read_text(SCRIPT_PATH) if pv == VERSION else None,
                                 "cierre inesperado (sin traceback)"
                                 + (f" en la pregunta «{prev['prompt']}»" if prev.get("prompt") else ""),
                                 prev.get("time"))
                except (OSError, ValueError) as _ign:
                    ignore("run_guarded", _ign)
                clear_screen()
                offer_recovery(prev.get("version"), abrupt_why(prev))
        mark_running()
        try:
            rc = entry()
        except Exception as e:
            clear_running()
            return handle_crash(e, traceback.format_exc())
        except BaseException:                         # Ctrl-C / SystemExit: salida normal
            clear_running()
            mark_good()
            raise
        clear_running()
        mark_good()
        return rc
    finally:
        if not nested:
            try:
                del sys._dlpy_guarded
            except AttributeError as _ign:
                ignore("run_guarded", _ign)


# ───────────────────── [H2] Caché de streams (24 h) ─────────────────────
def _safe_cache_seg(s):
    """Segmento de ruta seguro para claves de caché."""
    s = re.sub(r"[^\w.\-+=]", "_", str(s or ""))
    return s[:80] or "x"


def stream_cache_paths(vkey, format_id):
    """(dir, path_sin_ext_base). El archivo real es path + '.' + ext."""
    d = os.path.join(STREAM_CACHE_DIR, _safe_cache_seg(vkey))
    base = os.path.join(d, _safe_cache_seg(format_id))
    return d, base


def cleanup_stream_cache():
    """Elimina entradas de stream_cache con más de STREAM_CACHE_TTL segundos."""
    if not os.path.isdir(STREAM_CACHE_DIR):
        return
    now = time.time()
    try:
        for root, dirs, files in os.walk(STREAM_CACHE_DIR, topdown=False):
            for n in files:
                p = os.path.join(root, n)
                try:
                    if now - os.path.getmtime(p) > STREAM_CACHE_TTL:
                        os.remove(p)
                except OSError as _ign:
                    ignore("cleanup_stream_cache", _ign)
            for n in dirs:
                p = os.path.join(root, n)
                try:
                    if not os.listdir(p):
                        os.rmdir(p)
                except OSError as _ign:
                    ignore("cleanup_stream_cache", _ign)
    except OSError as _ign:
        ignore("cleanup_stream_cache", _ign)


def get_cached_stream(vkey, format_id, expected_ext=None):
    """Devuelve ruta del stream en caché si existe, es reciente y (opcional) coincide la ext."""
    d, base = stream_cache_paths(vkey, format_id)
    if not os.path.isdir(d):
        return None
    candidates = []
    prefix = os.path.basename(base) + "."
    try:
        for n in os.listdir(d):
            if n.startswith(prefix) and not n.endswith((".part", ".ytdl", ".tmp", ".meta")):
                candidates.append(os.path.join(d, n))
    except OSError as _ign:
        ignore("get_cached_stream", _ign)
        return None
    if expected_ext:
        prefer = base + "." + expected_ext.lstrip(".")
        if prefer in candidates:
            candidates = [prefer]
        else:
            candidates = [c for c in candidates
                          if c.rsplit(".", 1)[-1].lower() == expected_ext.lstrip(".").lower()]
    now = time.time()
    for p in candidates:
        try:
            if now - os.path.getmtime(p) <= STREAM_CACHE_TTL and os.path.getsize(p) > 0:
                return p
        except OSError as _ign:
            ignore("get_cached_stream", _ign)
            continue
    return None


CACHE_STATS = {"saved": 0, "failed": 0}


def save_stream_to_cache(vkey, format_id, src_path):
    """Guarda (copia o enlace) un stream terminado en la caché de 24 h."""
    if not src_path or not os.path.isfile(src_path):
        return
    try:
        size = os.path.getsize(src_path)
        if size <= 0:
            return
    except OSError as _ign:
        ignore("save_stream_to_cache", _ign)
        return
    ext = os.path.splitext(src_path)[1].lstrip(".") or "bin"
    d, base = stream_cache_paths(vkey, format_id)
    try:
        os.makedirs(d, exist_ok=True)
        dest = base + "." + ext
        if os.path.abspath(src_path) == os.path.abspath(dest):
            return
        tmp = dest + ".tmp"
        try:
            os.link(src_path, tmp)
        except OSError as _ign:
            ignore("save_stream_to_cache", _ign)
            copy_file(src_path, tmp)
        os.replace(tmp, dest)
        CACHE_STATS["saved"] += 1
        if DEBUG:
            m_info(f"Caché stream {format_id}: {human_size(size)}")
    except Exception as e:
        CACHE_STATS["failed"] += 1
        if DEBUG:
            m_warn(f"No se pudo cachear stream {format_id}: {e}")


def seed_work_from_cache(work_dir, base_name, vkey, format_specs):
    """Coloca en work_dir los streams cacheados que yt-dlp reconocerá.
    - Varios formatos (merge): base.f{format_id}.ext
    - Un solo formato: base.ext (salida directa)
    format_specs: [(format_id, ext), ...]. Devuelve cuántos se reutilizaron."""
    reused = 0
    multi = len(format_specs) > 1
    for fid, ext in format_specs:
        cached = get_cached_stream(vkey, fid, ext)
        if not cached:
            continue
        if multi:
            target = os.path.join(work_dir, f"{base_name}.f{fid}.{ext}")
        else:
            target = os.path.join(work_dir, f"{base_name}.{ext}")
        try:
            if os.path.exists(target):
                continue
            try:
                os.link(cached, target)
            except OSError as _ign:
                ignore("seed_work_from_cache", _ign)
                copy_file(cached, target)
            reused += 1
            m_ok(f"Reutilizado de caché: formato {fid} ({human_size(os.path.getsize(target))})")
        except Exception as e:
            if DEBUG:
                m_warn(f"No se pudo sembrar {fid}: {e}")
            try:
                if os.path.exists(target):
                    os.remove(target)
            except OSError as _ign:
                ignore("seed_work_from_cache", _ign)
    return reused


def cleanup_work(work_dir):
    if work_dir and os.path.isdir(work_dir):
        shutil.rmtree(work_dir, ignore_errors=True)


# ─────────────────── [H3] Reanudación de descargas ───────────────────
RESUME_PREFIX = "resume-"
RESUME_META = "resume.json"
RESUME_MAX_FAILS = 3        # fallos seguidos sin avanzar antes de descartar el parcial


def resume_key(vkey, specs):
    """Nombre de carpeta estable para una descarga: mismo enlace + mismos formatos
    (format_id, ext, tamaño exacto) = misma carpeta. specs: [(format_id, ext, filesize)]."""
    import hashlib
    raw = json.dumps([str(vkey), [[str(f), str(e), int(sz or 0)] for f, e, sz in specs]])
    return RESUME_PREFIX + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def newest_mtime(path):
    """Fecha de modificación más reciente de la carpeta o de cualquier archivo dentro."""
    try:
        best = os.path.getmtime(path)
    except OSError:
        return 0
    if os.path.isdir(path):
        for r, _d, fs in os.walk(path):
            for n in fs:
                try:
                    best = max(best, os.path.getmtime(os.path.join(r, n)))
                except OSError as _ign:
                    ignore("newest_mtime", _ign)
    return best


def resume_data_bytes(work_dir):
    """Bytes de datos (parciales y pistas completas) dentro de la carpeta."""
    total = 0
    for r, _d, fs in os.walk(work_dir):
        for n in fs:
            if n == RESUME_META:
                continue
            try:
                total += os.path.getsize(os.path.join(r, n))
            except OSError as _ign:
                ignore("resume_data_bytes", _ign)
    return total


def read_resume_meta(work_dir):
    try:
        with open(os.path.join(work_dir, RESUME_META), encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def write_resume_meta(work_dir, meta):
    try:
        with open(os.path.join(work_dir, RESUME_META), "w", encoding="utf-8") as f:
            json.dump(meta, f)
    except OSError as _ign:
        ignore("write_resume_meta", _ign)


def prepare_resume_dir(rkey, base):
    """Crea o recupera work/<rkey>. Devuelve (work_dir, base, bytes_previos, descartado).
    Si había avance válido se reutiliza su nombre base (el .part lo lleva en el nombre)."""
    work_dir = os.path.join(WORK_ROOT, rkey)
    resumed, discarded = 0, False
    if os.path.isdir(work_dir):
        meta = read_resume_meta(work_dir)
        prev = resume_data_bytes(work_dir)
        if prev > 0 and meta.get("fails", 0) >= RESUME_MAX_FAILS:
            discarded = True
        elif prev > 0 and meta.get("base"):
            base, resumed = str(meta["base"]), prev
        if not resumed:
            shutil.rmtree(work_dir, ignore_errors=True)
    os.makedirs(work_dir, exist_ok=True)
    if not resumed:
        write_resume_meta(work_dir, {"base": base, "fails": 0})
    return work_dir, base, resumed, discarded


def keep_for_resume(work_dir, start_bytes, failed):
    """Conserva el avance tras cancelar o fallar. Devuelve los bytes guardados
    (0 si no había nada y la carpeta se borró). Un fallo sin avance suma al contador;
    si hubo avance, el contador vuelve a 0."""
    now = resume_data_bytes(work_dir)
    if now <= 0:
        cleanup_work(work_dir)
        return 0
    if failed:
        meta = read_resume_meta(work_dir)
        meta["fails"] = 0 if now > start_bytes else int(meta.get("fails", 0)) + 1
        write_resume_meta(work_dir, meta)
    return now


# ───────────────────── [H4] Limpieza de la carpeta interna ─────────────────────
def cleanup_internal():
    """Limpia entregas temporales, work/ y stream_cache caducados."""
    now = time.time()
    # work/<id> y delivery/<id>: cada elemento caduca con INTERNAL_TTL
    for base in (DELIVERY_DIR, WORK_ROOT):
        if not os.path.isdir(base):
            continue
        for d in os.listdir(base):
            p = os.path.join(base, d)
            if not os.path.isdir(p):
                continue
            try:
                if now - newest_mtime(p) > INTERNAL_TTL:
                    shutil.rmtree(p, ignore_errors=True)
            except OSError as _ign:
                ignore("cleanup_internal", _ign)
    cleanup_stream_cache()


# ╔════════════════════════════════════════════════════════════════════════════════════════════════════════╗
# ║ ÁREA I · ENTREGA Y ANÁLISIS — entrega por Atajos, --2shortcuts, análisis tolerante, «no eres un bot»   ║
# ╚════════════════════════════════════════════════════════════════════════════════════════════════════════╝
# ───────────────────── [I1] Entrega del archivo (Atajos) ─────────────────────
def settle_file(path, wait=6.0):
    """Antes de entregar: espera a que el archivo deje de crecer, lo fuerza a disco (fsync) y avisa si está
    vacío. Un convertido recién escrito por ffmpeg a veces no se abría en el atajo."""
    try:
        last, t0 = -1, time.time()
        while True:
            size = os.path.getsize(path)
            if size == last or time.time() - t0 > wait:
                break
            last = size
            time.sleep(0.4)
        fd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        if size <= 0:
            m_warn("El archivo a entregar está vacío.")
    except OSError as _ign:
        ignore("settle_file", _ign)


def unique_path(src):
    d = os.path.join(DELIVERY_DIR, uuid.uuid4().hex[:12])
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, os.path.basename(src))
    try:
        os.link(src, dst)
    except OSError as _ign:
        ignore("unique_path", _ign)
        copy_file(src, dst)
    return os.path.abspath(dst)


def run_cmd(args, timeout=8):
    """Ejecuta una orden externa sin que pueda colgar el script. Devuelve su salida o None si falla."""
    import subprocess
    try:
        r = subprocess.run(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True, timeout=timeout)
        return r.stdout if r.returncode == 0 else None
    except Exception as _ign:
        ignore("run_cmd", _ign)
        return None


def deliver(final, title):
    """Entrega el archivo (Atajos / app por defecto) y anota la hora en el índice."""
    if LATE_UPDATES["on"] and not LATE_UPDATES["done"]:
        late_updates()
    if _deliver_platform(final, title):
        mark_delivered(final)


def _deliver_platform(final, title):
    settle_file(final)                     # el convertido recién escrito: completo y en disco antes de avisar
    path = unique_path(final)
    m_info(f"Enviando a {SHORTCUT_NAME}...")
    dbg("entrega", {"origen": final, "copia": path, "titulo": title})
    url = shortcut_run_url({"file_path": path, "file_title": title})
    for n in range(3):                     # `open` puede fallar si iOS aún no devolvió el foco a a-Shell
        if n:
            time.sleep(1.5)
        if os.system("open " + shlex.quote(url)) == 0:
            return True
        dbg("entrega", f"open falló (intento {n + 1})")
    m_warn(f"No se pudo abrir el atajo «{SHORTCUT_NAME}»: el archivo está en dlpy_files.")
    return False


def mark_delivered(final, when=None):
    """Guarda en el índice la hora de la última entrega del archivo (clave «delivered»)."""
    try:
        index = load_json(INDEX_FILE)
        name = os.path.basename(final)
        hit = [e for e in index.values() if isinstance(e, dict) and e.get("file") == name]
        for e in hit:
            e["delivered"] = int(when or time.time())
        if hit:
            save_json(INDEX_FILE, index)
        hist = load_json(HISTORY_FILE)
        hh = [e for lst in hist.values() if isinstance(lst, list) for e in lst
              if isinstance(e, dict) and e.get("file") == name]
        for e in hh:
            e["delivered"] = int(when or time.time())
        if hh:
            save_json(HISTORY_FILE, hist)
    except Exception as _ign:
        ignore("mark_delivered", _ign)


def reopen_question():
    """Texto de la pregunta «¿Abrir otra vez…?»."""
    return "¿Abrir otra vez con Atajos? (S/n) ▸ "


def deliver_existing(old_file, old_entry, title):
    """Entrega un archivo ya descargado. Si ya se había entregado antes (índice con
    «delivered») pregunta si abrirlo otra vez; si nunca se entregó, lo manda directo.
    Devuelve True si lo entregó."""
    if (old_entry or {}).get("delivered"):
        try:
            if not ask_yn(reopen_question(), default=True, seconds=None):
                m_info("No se volvió a abrir.")
                return False
        except (EOFError, KeyboardInterrupt):
            return False
    deliver(old_file, title)
    return True


# ───────────────────── [I2] Atajo de iOS (--2shortcuts) ─────────────────────
def shortcut_run_url(data, name=None):
    """URL shortcuts:// que lanza el atajo con `data` (JSON) como texto de entrada."""
    payload = json.dumps(data, ensure_ascii=False)
    return ("shortcuts://run-shortcut?name=" + urllib.parse.quote(name or SHORTCUT_NAME)
            + "&input=text&text=" + urllib.parse.quote(payload, safe=""))


def shortcut_clip_url(name=None):
    """URL shortcuts:// que lanza el atajo con el portapapeles como entrada."""
    return ("shortcuts://run-shortcut?name=" + urllib.parse.quote(name or SHORTCUT_NAME)
            + "&input=clipboard")


def shortcut_text_url(text, name=None):
    """URL shortcuts:// que lanza el atajo con `text` tal cual como entrada."""
    return ("shortcuts://run-shortcut?name=" + urllib.parse.quote(name or SHORTCUT_NAME)
            + "&input=text&text=" + urllib.parse.quote(text, safe=""))


def wants_2shortcuts(args):
    """¿Se pidió --2shortcuts? Acepta «--2shorcuts» y rayas largas (– —) del teclado."""
    for a in args:
        if a.lstrip("-\u2013\u2014").lower() in ("2shortcuts", "2shorcuts") and a[:1] in "-\u2013\u2014":
            return True
    return False


def send_code_to_shortcut():
    """`--2shortcuts` (iOS): manda el dlpy.py actual al atajo, que lo reconoce por la
    primera línea (#!dlpy.py). Pregunta si va con o sin changelog."""
    ensure_dirs()
    clear_screen()                  # mismo encabezado que el resto del script
    try:
        plain, full = script_variants()
    except OSError as e:
        m_err(f"No se pudo leer el código: {e}")
        return 1
    if full is None:
        code, how = plain, "sin changelog"
        note("No hay changelog que añadir (changelog.md no existe todavía): va sin él.")
    elif ask("¿Con changelog? (s/N) ▸ ", default=False):
        code, how = full, "con changelog"
    else:
        code, how = plain, "sin changelog"
    size = human_size(len(code.encode("utf-8")))
    m_info(f"Enviando el código v{VERSION} ({how} · {size}) a {SHORTCUT_NAME}...")
    tmp = os.path.join(WORK_ROOT, "2shortcuts_dlpy.py")
    copied = False
    try:
        os.makedirs(WORK_ROOT, exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(code)
        copied = os.system("pbcopy < " + shlex.quote(tmp)) == 0
    except OSError as _ign:
        ignore("send_code_to_shortcut", _ign)
    finally:
        try:
            os.remove(tmp)
        except OSError as _ign:
            ignore("send_code_to_shortcut", _ign)
    if copied:
        url = shortcut_clip_url()
    else:
        url = shortcut_text_url(code)
        if len(url) > SC_URL_MAX:
            m_err("No se pudo usar el portapapeles y el código no cabe dentro del enlace.")
            return 1
        m_warn("No se pudo usar el portapapeles; el código va dentro del enlace.")
    dbg("2shortcuts", {"bytes": len(code.encode("utf-8")), "con_changelog": how, "url": url[:80]})
    os.system("open " + shlex.quote(url))
    return 0


# ───────────── [I3] Análisis tolerante (equivalente al yt-dlp en bruto) ─────────────
# Opciones de la CLI que no deben heredarse (las controla este script).
_CLI_DROP = ("postprocessors", "postprocessor_args", "paths", "logger", "progress_hooks",
             "postprocessor_hooks", "simulate", "skip_download", "listformats",
             "list_thumbnails", "forcejson", "dump_single_json", "dumpjson", "outtmpl",
             "format", "quiet", "no_warnings", "verbose", "noprogress", "consoletitle",
             "overwrites", "continuedl", "merge_output_format", "allow_multiple_audio_streams",
             "extract_flat", "playlist_items", "load_info_filename", "writeinfojson")


# ─────────────────── [I4] Error «no eres un bot» ───────────────────
def is_bot_error(e):
    t = str(e).lower()
    return "not a bot" in t or "sign in to confirm" in t


def explain_bot_error():
    """Avisa del error de «no eres un bot» (repetir el intento no ayuda)."""
    m_err("YouTube pide comprobar que no eres un bot; no se puede analizar este enlace.")
    note("Actualiza yt-dlp (pip install -U yt-dlp) o inténtalo más tarde.")


def cli_like_opts(yt_dlp, argv):
    """Opciones de YoutubeDL que produciría la CLI de yt-dlp con `argv` (mismos
    valores por defecto: reintentos, cabeceras, etc.). None si no se pueden
    construir (versión sin parse_options o banderas inválidas)."""
    try:
        o = dict(yt_dlp.parse_options(list(argv)).ydl_opts)
    except (Exception, SystemExit) as e:
        dbg("parse_options falló", str(e))
        return None
    for k in _CLI_DROP:
        o.pop(k, None)
    return o


def user_argv():
    """Banderas extra de yt-dlp en bruto (DLPY_YTDLP_ARGS)."""
    raw = os.environ.get("DLPY_YTDLP_ARGS", "").strip()
    try:
        mine = shlex.split(raw) if raw else []
    except ValueError as e:
        m_warn(f"DLPY_YTDLP_ARGS inválido: {e}")
        mine = []
    return mine + js_runtime_args(mine)


def probe_cli_json(link, extra, timeout=180):
    """Último recurso: ejecutable yt-dlp en bruto (-J). Devuelve el info o None."""
    exe = shutil.which("yt-dlp")
    if not exe:
        dbg("yt-dlp en bruto", "no hay ejecutable yt-dlp")
        return None
    import subprocess
    try:
        r = subprocess.run([exe, "-J", "--no-playlist", "--no-warnings"] + list(extra) + [link],
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True, timeout=timeout)
        if r.returncode != 0 or not r.stdout.strip():
            dbg("yt-dlp en bruto falló", (r.stderr or "").strip()[-400:])
            return None
        return json.loads(r.stdout)
    except Exception as e:
        dbg("yt-dlp en bruto falló", str(e))
        return None


ANALYSIS = {"stage": None}          # etapa del análisis que funcionó


def analyze_link(yt_dlp, link, quick=False):
    """Devuelve (info, base_opts). Prueba varias formas de analizar el enlace y
    se queda con la primera que funcione; base_opts se reutiliza al descargar.
    quick: tiempos cortos, dos etapas y yt-dlp en bruto con tope de 60 s."""
    extra = user_argv()
    std = {"quiet": True, "no_warnings": True, "noplaylist": True, "socket_timeout": 20}
    if DEBUG:
        std.update({"quiet": False, "no_warnings": False, "verbose": True})
    if quick:
        std.update({"socket_timeout": 10, "retries": 2, "extractor_retries": 1})
    if SCM["on"]:                       # --scm: sockets cortos para que un análisis abortado termine solo
        std.update({"socket_timeout": 2, "retries": 0, "extractor_retries": 0})
        if not getattr(yt_dlp.YoutubeDL, "_dlpy_abortable", False):
            _orig_urlopen = yt_dlp.YoutubeDL.urlopen

            def _urlopen(self, *a, **k):
                if SCM["abort"].is_set():
                    raise RuntimeError("análisis abortado")
                return _orig_urlopen(self, *a, **k)
            yt_dlp.YoutubeDL.urlopen = _urlopen
            yt_dlp.YoutubeDL._dlpy_abortable = True
    stages = [
        ("biblioteca", lambda: (cli_like_opts(yt_dlp, extra) or {}) if extra else {}, True),
        ("equivalente a CLI", lambda: cli_like_opts(yt_dlp, ["--no-playlist"] + extra), True),
        ("CLI sin --no-playlist", lambda: cli_like_opts(yt_dlp, extra), False),
    ]
    if quick:
        stages = stages[:2]
    last = None
    for i, (name, make, no_pl) in enumerate(stages):
        if SCM["abort"].is_set():
            raise RuntimeError("análisis abortado")
        base = make()
        if base is None:
            continue
        probe = {**base, **std}
        if not no_pl:
            probe.pop("noplaylist", None)
        if i:
            m_info(f"Reintentando análisis ({name})...")
        try:
            with yt_dlp.YoutubeDL(probe) as ydl:
                info = ydl.extract_info(link, download=False)
            if info:
                dbg("análisis", f"funcionó: {name}")
                ANALYSIS["stage"] = name
                return info, base
        except KeyboardInterrupt:
            raise
        except Exception as e:
            last = e
            dbg("análisis falló", f"{name}: {e}")
            if is_bot_error(e):
                raise          # repetir el análisis no ayuda
    m_info("Reintentando análisis (yt-dlp en bruto)...")
    info = probe_cli_json(link, extra, 60 if quick else 180)
    if info:
        dbg("análisis", "funcionó: yt-dlp en bruto (-J)")
        ANALYSIS["stage"] = "yt-dlp en bruto"
        base = cli_like_opts(yt_dlp, ["--no-playlist"] + extra) or {}
        return info, base
    raise last or RuntimeError("no se pudo analizar el enlace")


# Errores que justifican reanalizar el enlace (se evalúa sobre el texto en minúsculas).
_RETRY_RE = re.compile(r"not available|expired|forbidden|\bhttp error (?:403|410)\b")


def run_download(ydl, yt_dlp, info, link, fmt_id):
    """Descarga con el MISMO análisis que vio el usuario (así los format_id
    coinciden). Si falla porque el formato ya no existe o la URL caducó, vuelve
    a analizar el enlace y, como último recurso, usa el mejor equivalente."""
    import copy

    def clone():
        try:
            return copy.deepcopy(info)
        except Exception as _ign:
            ignore("clone", _ign)
            return dict(info)

    try:
        return ydl.process_ie_result(clone(), download=True)
    except yt_dlp.utils.DownloadError as e:
        dbg("fallo con el análisis previo", str(e))
        if not _RETRY_RE.search(str(e).lower()):
            raise
    m_info("Reanalizando el enlace...")
    try:
        return ydl.extract_info(link, download=True)
    except yt_dlp.utils.DownloadError as e:
        dbg("fallo tras reanalizar", str(e))
        if "not available" not in str(e).lower():
            raise
    m_warn("El formato elegido ya no está disponible; se usa el mejor equivalente.")
    ydl.params["format"] = f"{fmt_id}/bv*+ba/b"
    return ydl.extract_info(link, download=True)


# ╔══════════════════════════════════════════════════════════════════════╗
# ║ ÁREA J · MODO ATAJO — --scm / --scb / --shortcutpick                 ║
# ╚══════════════════════════════════════════════════════════════════════╝
# ───────────────────── [J1] Modo atajo (--scm / --scb) ─────────────────────
# --scm LINK: analiza el enlace SIN interfaz y escribe UN JSON (una línea, ASCII) con las listas que el atajo
# muestra: resolución + fps, pista predeterminada e idiomas adicionales (cuando aplica).
# --scb LINK: lo mismo, pero en primer plano (banner y barra) y AVISA al atajo «DLpy» con el JSON al terminar.
# --shortcutpick «v=ID,a=IDIOMA,x=IDIOMA+IDIOMA»: devuelve lo elegido; se descarga en el menú de siempre.
SHORTCUT_SCHEMA = 1
DASHES = "-\u2013\u2014"                       # raya normal, en y em (el teclado de iOS convierte «--» en «—»)
VALUE_FLAGS = {"shortcutpick"}                 # banderas con valor: «--bandera valor» o «--bandera=valor»
SC_URL_MAX = 30000                     # largo máximo de la URL shortcuts://; si pasa, el JSON va por el portapapeles
SC_TIMEOUT = _env_num("DLPY_SC_TIMEOUT", 90.0)     # tope del análisis para el atajo (s; 0 = sin tope)
# --scm corre en «Ejecutar comando» de a-Shell EN EXTENSIÓN y Atajos la corta a ~10 s (medido): el análisis
# tiene que responder antes. Se cuenta desde que arrancó el script; si no alcanza, devuelve «timeout».
SCM_T0 = time.time()
SCM_TIMEOUT = _env_num("DLPY_SCM_TIMEOUT", 5.0)
SCM = {"on": False, "abort": threading.Event(), "thread": None}     # estado de --scm
SCM_UNWIND = 2.0                       # s que se espera a que el hilo de análisis termine solo tras un timeout


def norm_args(args):
    """Las rayas largas que pone el teclado de iOS (– —) al principio de una bandera valen como «--»:
    «—scb» = «--scb»."""
    out = []
    for a in args:
        if a[:1] in ("\u2013", "\u2014") and a.lstrip(DASHES)[:1].isalpha():
            a = "--" + a.lstrip(DASHES)
        out.append(a)
    return out


def parse_cli(args):
    """(banderas, posicionales). «--x» → {"x": True}; «--x=v» → {"x": "v"}; las banderas de VALUE_FLAGS
    toman también el argumento siguiente. Lo que no empieza por «--» es posicional (el enlace)."""
    flags, pos, args, i = {}, [], list(args), 0
    while i < len(args):
        a = args[i]
        i += 1
        if not a.startswith("--"):
            pos.append(a)
            continue
        name, eq, val = a[2:].partition("=")
        name = name.lower()
        if not name:
            continue
        if name in VALUE_FLAGS:
            if not eq and i < len(args) and not args[i].startswith("--"):
                val, i = args[i], i + 1
            flags[name] = val
        else:
            flags[name] = val if eq else True
    return flags, pos


def _wants(args, name):
    return any(a[:1] in DASHES and a.lstrip(DASHES).lower().split("=")[0] == name for a in args)


def wants_scm(args):
    """¿Se pidió --scm? Acepta rayas largas («—scm»)."""
    return _wants(args, "scm")


def wants_scb(args):
    """¿Se pidió --scb? Acepta rayas largas («—scb»)."""
    return _wants(args, "scb")


def parse_shortcut_pick(raw):
    """Lo que devuelve el atajo: «v=137,a=es-US,x=en-US+pt-BR» (o JSON {"v":..,"a":..,"x":[..]}).
    v = format_id del video, «audio» (solo audio) o «best»; a = pista predeterminada (idioma);
    x = idiomas adicionales separados por «+». Devuelve {"v","a","x"} o None si no hay nada útil."""
    if raw is None or raw is True:
        return None
    text = str(raw).strip().strip("\"'")
    if not text:
        return None
    vals = {}
    if text.startswith("{"):
        try:
            data = json.loads(text)
        except ValueError:
            return None
        if not isinstance(data, dict):
            return None
        vals = {str(k).lower(): v for k, v in data.items()}
    else:
        for part in text.split(","):
            k, eq, v = part.partition("=")
            if eq:
                vals[k.strip().lower()] = v.strip()

    def one(*names):
        for n in names:
            if vals.get(n) is not None:
                s = urllib.parse.unquote(str(vals[n])).strip()
                if s:
                    return s
        return None

    xs = next((vals[n] for n in ("x", "extra", "extras") if n in vals), None)
    xs = list(xs) if isinstance(xs, (list, tuple)) else re.split(r"[+\s]+", str(xs or ""))
    xs = [urllib.parse.unquote(str(x)).strip() for x in xs]
    pick_ = {"v": one("v", "video"), "a": one("a", "audio", "track"), "x": [x for x in xs if x]}
    return pick_ if (pick_["v"] or pick_["a"] or pick_["x"]) else None


def split_formats(info):
    """(formatos, audios, videos) como los usa la lista de siempre (de peor a mejor calidad)."""
    formats = [normalize_format(f) for f in (info.get("formats") or [])
               if f.get("ext") != "mhtml" and "storyboard" not in (f.get("format_note") or "")]
    audios = [f for f in formats if has(f.get("acodec")) and not has(f.get("vcodec"))]
    videos = [f for f in formats if has(f.get("vcodec"))]
    audios.sort(key=abr_of)
    videos.sort(key=lambda f: (f.get("height") or 0, f.get("tbr") or 0))
    return formats, audios, videos


def shortcut_fps(f):
    try:
        v = float(f.get("fps") or 0)
    except (TypeError, ValueError):
        return 0
    return int(round(v)) if v > 0 else 0


def shortcut_quality_key(f):
    """Una entrada por resolución + fps (1080p 60fps y 1080p 30fps son distintas); el HDR o los más de
    8 bits cuentan aparte, como en la lista corta. Los códecs/contenedores de la misma calidad se funden."""
    bits = detect_bit_depth(f)
    return (f.get("height") or format_tag(f), shortcut_fps(f),
            detect_hdr(f) or "", bits if bits and bits > 8 else 0)


def shortcut_kbps(f):
    """Bitrate total en kbps (tbr, o vbr + abr) o None si el formato no lo informa."""
    try:
        v = float(f.get("tbr") or 0) or (float(f.get("vbr") or 0) + float(f.get("abr") or 0))
    except (TypeError, ValueError):
        return None
    return v if v > 0 else None


def size_estimate(kbps, secs):
    """«~12 MB»: tamaño aproximado = bitrate × duración. None si falta alguno de los dos."""
    try:
        if not kbps or not secs or float(secs) <= 0:
            return None
        return "~" + human_size(kbps * 1000 / 8 * float(secs))
    except (TypeError, ValueError):
        return None


def shortcut_video_name(f):
    """«1080p 60fps», «2160p 30fps HDR10»: resolución + fps (+ rango si no es SDR de 8 bits)."""
    h = f.get("height")
    s = f"{h}p" if h else format_tag(f)
    if shortcut_fps(f):
        s += f" {shortcut_fps(f)}fps"
    hdr, bits = detect_hdr(f), detect_bit_depth(f)
    if hdr:
        s += f" {hdr}"
    elif bits and bits > 8:
        s += f" {bits}b"
    return s


def shortcut_track_name(t):
    f = t["fmt"]
    name = track_label(t)
    if t["original"]:
        name = re.sub(r"\s*\boriginal\b\s*$", "", name, flags=re.I) or name       # ya se marca aparte
    lead = name if name == t["lang"] else f"{name} · {t['lang']}"
    abr = abr_of(f)
    tech = f"{f.get('ext') or '?'} {(f.get('acodec') or '?').split('.')[0]}" + (f" {abr:.0f}k" if abr else "")
    return lead + (" · original" if t["original"] else "") + f" · {tech}" + (" 🟢" if apple_audio(f) else "")


def shortcut_error(code, msg, link=None, elapsed=None):
    out = {"dlpy": "shortcutmode", "schema": SHORTCUT_SCHEMA, "ok": False, "status": "error", "version": VERSION,
           "link": link, "error_code": code, "error": msg}
    if elapsed is not None:
        out["elapsed"] = elapsed
    return out


SC_TITLE_MAX = 60                      # largo del título corto del menú de Atajos


def short_title(title, limit=SC_TITLE_MAX):
    """Título corto para el mensaje del menú de Atajos: sin el prefijo de estadísticas de redes
    («1.1M views · 7.6K reactions | …»), sin enlaces ni hashtags, en la primera frase si cabe y, si no, cortado en
    una palabra con «…». El título completo sigue en «title». Función pura."""
    t = re.sub(r"\s+", " ", str(title or "")).strip()
    t = re.sub(r"^[\d.,]+\s*[KMB]?\s*(?:views?|vistas|reproducciones|plays|likes)\b[^|]*\|\s*", "", t, flags=re.I)
    t = re.sub(r"https?://\S+", "", t)
    t = re.sub(r"\s*#\w+", "", t)
    t = re.sub(r"\s+", " ", t).strip(" |-·")
    first = re.split(r"(?<=[.!?])\s", t, maxsplit=1)[0].rstrip(".!? ")
    if 12 <= len(first) <= limit:
        return first
    if len(t) <= limit:
        return t or str(title or "video")[:limit]
    cut = t[:limit + 1]
    cut = cut[:cut.rfind(" ")] if " " in cut[:limit + 1] and cut.rfind(" ") > limit // 2 else t[:limit]
    return cut.rstrip(" ,;:.-·|") + "…"


def audio_desc(f):
    """«m4a mp4a 44k» (+ idioma si lo hay): lo que se baja de ese audio."""
    abr = abr_of(f)
    s = f"{f.get('ext') or '?'} {(f.get('acodec') or '?').split('.')[0]}" + (f" {abr:.0f}k" if abr else "")
    lang = f.get("language")
    return s + (f" {lang}" if lang else "")


def video_desc(f):
    """«1920p vp09», «id1 mp4 con audio»: resolución/etiqueta + códec (o contenedor si no hay códec)."""
    name = shortcut_video_name(f)
    vc = str(f.get("vcodec") or "unknown").split(".")[0]
    if vc.lower() in ("unknown", "?", "none", ""):
        return f"{name} {f.get('ext') or '?'}" + (" con audio" if has(f.get("acodec")) else "")
    return f"{name} {vc}"


def ytdlp_auto_pick(info, audios, videos):
    """Lo que bajaría yt-dlp con su formato por omisión «bv*+ba/b»: (video, audio|None) con los MISMOS objetos
    de las listas `videos` / `audios`; audio None si el formato elegido ya trae audio. None si el análisis no trae
    la selección (requested_formats / format_id) o no es un video. Función pura: sin red."""
    ids = []
    for x in (info.get("requested_formats") or []):
        ids.append(str(x.get("format_id")))
    if not ids and info.get("format_id"):
        ids = [p for p in str(info["format_id"]).split("+") if p]
    if not ids:
        return None
    vsel = next((f for i in ids for f in videos if str(f.get("format_id")) == i), None)
    if vsel is None:
        return None
    asel = None
    if not has(vsel.get("acodec")):
        asel = next((f for i in ids for f in audios if str(f.get("format_id")) == i), None)
    return vsel, asel


def build_shortcut_payload(info, link, can_merge, old_file=None, old_entry=None, history=None):
    """El JSON que lee el atajo. Listas paralelas con número delante («1 · 1080p 60fps …») para que el atajo
    saque el id con el número; sin diccionarios con etiquetas como clave (los puntos de «1.9 GB» romperían
    la búsqueda por clave de Atajos). Función pura: no toca disco ni red."""
    _formats, audios, videos = split_formats(info)
    if not audios and not videos:
        return shortcut_error("no_formats", "No se encontraron formatos.", link)
    orig_ids = mark_originals(audios)
    tracks, orig_lang = build_tracks(audios, orig_ids)
    multi_lang = len({t["lang"] for t in tracks if t["lang"] != "und"}) > 1
    bk, bf = auto_best(audios, videos, orig_ids, can_merge, quiet=True)
    can_tracks = bool(tracks) and bool(can_merge)

    groups = {}
    for f in videos:
        groups.setdefault(shortcut_quality_key(f), []).append(f)

    def rank(f):        # misma preferencia que la lista corta: con audio si no hay ffmpeg, compatible, bitrate
        return (has(f.get("acodec")) if not can_merge else False, bool(apple_video(f)),
                f.get("tbr") or 0)

    picked = [bf if bk == "v" and any(x is bf for x in g) else max(g, key=rank) for g in groups.values()]
    picked.sort(key=lambda f: (-(f.get("height") or 0), -shortcut_fps(f), bool(detect_hdr(f)),
                               -(shortcut_kbps(f) or 0), str(f.get("format_id"))))

    # la opción que coincide EXACTAMENTE con lo ya descargado se marca «· ya lo tienes»
    old_meta = (old_entry or {}).get("meta") or {} if old_file else {}
    old_kind = old_meta.get("kind")
    hist = list(history) if history is not None else ([(old_file, old_entry)] if old_file else [])
    got_video = {str(((e.get("meta") or {}).get("format_id") or "")).split("+")[0]
                 for _p, e in hist if ((e.get("meta") or {}).get("kind")) == "video"}
    got_audio = any(((e.get("meta") or {}).get("kind")) == "audio" for _p, e in hist)
    # idiomas que ya tienes en CUALQUIER archivo descargado de este video (solo audio o dentro de un video)
    got_langs = {str(tr.get("lang")) for _p, e in hist for tr in ((e.get("meta") or {}).get("tracks") or [])
                 if tr.get("lang")}

    v_items = []
    for f in picked:
        has_a = has(f.get("acodec"))
        size = f.get("filesize") or f.get("filesize_approx")
        kbps = shortcut_kbps(f)
        v_items.append({
            "id": str(f.get("format_id")), "name": shortcut_video_name(f), "height": f.get("height"),
            "fps": shortcut_fps(f) or None, "ext": f.get("ext"),
            "vcodec": ((f.get("vcodec") or "?").split(".")[0] if str(f.get("vcodec") or "unknown").lower()
                       not in ("unknown", "?")
                       else (f"{f.get('ext') or '?'} · con audio" if has_a else (f.get("ext") or "?"))),
            "range": range_label(f) or None, "hdr": detect_hdr(f), "size_bytes": size,
            "size": human_size(size) if size else None, "compatible": bool(apple_video(f)),
            "kbps": round(kbps) if kbps else None,
            "size_est": None if size else size_estimate(kbps, info.get("duration")),
            "audio": "included" if has_a else ("separate" if can_tracks else "none"),
            "audio_step": "none" if (has_a or not can_tracks or not multi_lang) else "full",
            "best": bk == "v" and f is bf,
            "have": str(f.get("format_id")) in got_video})
    extras_error = None
    try:
        got_ids = {str((e.get("meta") or {}).get("format_id") or "") for _p, e in hist}
        auto = ytdlp_auto_pick(info, audios, videos)
    except Exception as e:
        got_ids, auto, extras_error = set(), None, f"auto: {type(e).__name__}: {e}"
    if auto:
        av, aa = auto
        aid = "+".join([str(av.get("format_id"))] + ([str(aa.get("format_id"))] if aa else []))
        desc = video_desc(av) + (f" + {audio_desc(aa)}" if aa else "")
        v_items.append({
            "id": "ytdlp", "name": "yt-dlp auto", "height": av.get("height"), "fps": shortcut_fps(av) or None,
            "ext": av.get("ext"), "vcodec": desc, "range": range_label(av) or None, "hdr": detect_hdr(av),
            "size_bytes": None, "size": None,
            "compatible": bool(apple_video(av)) and (aa is None or bool(apple_audio(aa))),
            "audio": "separate" if aa else "included", "audio_step": "none", "best": False,
            "have": aid in got_ids,
            "auto": {"video_id": str(av.get("format_id")), "audio_id": str(aa.get("format_id")) if aa else None,
                     "video": video_desc(av), "audio": audio_desc(aa) if aa else None, "formato": aid}})
    solo_audio = ""
    if audios:
        try:
            _t = next((t for t in tracks if t["original"]), tracks[0] if tracks else None)
            solo_audio = audio_desc(_t["fmt"]) if _t else ""
        except Exception as e:
            extras_error = f"solo audio: {type(e).__name__}: {e}"
        v_items.append({
            "id": "audio", "name": "Solo audio", "height": None, "fps": None, "ext": None, "vcodec": None,
            "range": None, "hdr": None, "size_bytes": None, "size": None, "compatible": True, "audio": "only",
            "audio_step": "track" if multi_lang else "none", "best": bk == "a",
            "have": got_audio, "detail": solo_audio or None})

    def menu(n, it):
        # emojis en color (el menú de Atajos es texto plano, pero los emojis sí se ven en color)
        marks = ((" 🔊" if it.get("audio") == "included" else " 🔇" if it.get("audio") == "none" else "")
                 + (" 🟢" if it.get("compatible") and it["id"] != "audio" else "")
                 + (" ✅" if it.get("have") else ""))
        if it["id"] == "audio":
            return f"{n} · ♫ Solo audio" + (f" · {it['detail']}" if it.get("detail") else "") + marks
        if it["id"] == "ytdlp":
            same = next((o["n"] for o in v_items if o.get("n") and o["id"] == it["auto"]["video_id"]), None)
            return f"{n} · yt-dlp auto · {it['vcodec']}" + (f" (= {same})" if same else "") + marks
        vc = re.sub(r"\s*·\s*con audio$", "", str(it["vcodec"] or ""))      # «con audio» ya lo dice 🔊
        parts = [("★ " if it["best"] else "") + it["name"], vc]
        if not it.get("height") and it.get("kbps"):                         # sin resolución: el bitrate distingue
            parts.append(kbps_text(it["kbps"]))
        parts.append(it["size"] or it.get("size_est"))
        return f"{n} · " + " · ".join(p for p in parts if p) + marks

    for n, it in enumerate(v_items, 1):
        it["n"] = n
        it["label"] = menu(n, it)

    t_items = []
    for n, t in enumerate(tracks, 1):
        f = t["fmt"]
        got = str(t["lang"]) in got_langs
        t_items.append({"n": n, "id": t["lang"], "lang": t["lang"], "have": got,
                        "label": f"{n} · {shortcut_track_name(t)}" + (" ✅" if got else ""),
                        "format_id": str(f.get("format_id")), "ext": f.get("ext"),
                        "codec": (f.get("acodec") or "?").split(".")[0],
                        "abr": round(abr_of(f)) if abr_of(f) else None,
                        "original": bool(t["original"]), "compatible": bool(apple_audio(f))})
    t_labels = [it["label"] for it in t_items]
    extra_menu = {str(i): [lab for j, lab in enumerate(t_labels, 1) if j != i] for i in range(1, len(t_labels) + 1)}

    dur = info.get("duration")
    try:
        d = int(dur) if dur else None
    except (TypeError, ValueError):
        d = None
    dur_text = (f"{d // 3600}:{d % 3600 // 60:02d}:{d % 60:02d}" if d and d >= 3600
                else f"{d // 60}:{d % 60:02d}" if d is not None else None)
    old = ({"file": os.path.basename(old_file), "title": (old_entry or {}).get("title"),
            "date": (old_entry or {}).get("date"), "kind": old_kind, "format_id": old_meta.get("format_id")}
           if old_file else None)
    downloaded = [{"file": os.path.basename(pth), "kind": (e.get("meta") or {}).get("kind"),
                   "format_id": (e.get("meta") or {}).get("format_id"), "date": e.get("date")} for pth, e in hist]
    return {
        **({"extras_error": extras_error} if extras_error else {}),
        "dlpy": "shortcutmode", "schema": SHORTCUT_SCHEMA, "ok": True, "status": "ok", "version": VERSION, "platform": PLATFORM,
        "link": link, "title": info.get("title") or "video", "title_short": short_title(info.get("title")),
        "id": info.get("id"),
        "extractor": info.get("extractor_key") or info.get("extractor"),
        "uploader": info.get("uploader") or info.get("channel"), "duration": d, "duration_text": dur_text,
        "thumbnail": info.get("thumbnail"), "key": video_key(info), "already_downloaded": old, "downloaded": downloaded,
        "can_merge": bool(can_merge), "multi_lang": multi_lang, "original_lang": orig_lang,
        "prompt": " · ".join(x for x in (short_title(info.get("title")), dur_text) if x),
        "default_video": next((it["n"] for it in v_items if it["best"]), 1),
        "default_track": next((it["n"] for it in t_items if it["original"]), 1) if t_items else None,
        "video_labels": [it["label"] for it in v_items], "video_ids": [it["id"] for it in v_items],
        "video_audio_step": [it["audio_step"] for it in v_items],
        "track_labels": t_labels, "track_ids": [it["id"] for it in t_items], "extra_menu": extra_menu,
        "videos": v_items, "tracks": t_items,
        "pick_format": "v=<video_ids[n]>,a=<track_ids[n]>,x=<track_ids[n]>+<track_ids[m]>",
        "pick_example": "v=" + next((it["id"] for it in v_items if it["best"]), v_items[0]["id"])
                        + (f",a={t_items[0]['id']}" if t_items and multi_lang else ",a=")
                        + (f",x={t_items[1]['id']}" if len(t_items) > 1 and multi_lang else ",x=")}


def shortcut_collect(link):
    """Analiza `link` y devuelve el diccionario de salida (siempre uno, nunca lanza)."""
    t0 = time.time()

    def done(data):
        data["elapsed"] = round(time.time() - t0, 1)
        return data

    link = (link or clipboard_link() or "").strip()
    if not link:
        return done(shortcut_error("no_link", "No hay enlace: usa --scb LINK o --scm LINK."))
    try:
        import yt_dlp
    except Exception as e:                      # ImportError y cualquier fallo al cargarlo
        err = shortcut_error("no_ytdlp", f"yt-dlp no está instalado ({e}). Usa --scb: lo instala.", link)
        err["use_scb"] = True                   # --scm no instala (tarda más de 10 s); --scb sí
        return done(err)
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
    except OSError as _ign:
        ignore("shortcut_collect", _ign)
    ANALYSIS["stage"] = None
    try:
        info, _base = analyze_link(yt_dlp, link, quick=True)
    except KeyboardInterrupt:
        raise
    except Exception as e:
        return done(shortcut_error("bot" if is_bot_error(e) else "analyze",
                                   str(e).strip()[:400] or "error al analizar", link))
    if info.get("entries"):
        info = next((e for e in info["entries"] if e), info)
    old_file, old_entry = lookup_downloaded(load_json(INDEX_FILE), video_key(info))
    data = build_shortcut_payload(info, link, ffmpeg_available(), old_file, old_entry,
                                  history_for(video_key(info)))
    data["stage"] = ANALYSIS["stage"]
    return done(data)


def collect_with_timeout(link, secs=None, fn=None):
    """shortcut_collect con tope de tiempo (SC_TIMEOUT): si se pasa devuelve el error «timeout» en vez de
    dejar al atajo esperando. El análisis se hace en un hilo aparte (daemon: no frena la salida)."""
    fn = fn or shortcut_collect
    secs = SC_TIMEOUT if secs is None else secs
    box = {}

    def work():
        try:
            box["data"] = fn(link)
        except BaseException as e:
            box["data"] = shortcut_error("crash", f"{type(e).__name__}: {e}", link)

    t0 = time.time()
    th = threading.Thread(target=work, daemon=True)
    SCM["thread"] = th
    th.start()
    th.join(secs if secs and secs > 0 else None)
    if th.is_alive():
        return shortcut_error("timeout", f"El análisis tardó más de {secs:g} s.", link, round(time.time() - t0, 1))
    return box.get("data") or shortcut_error("crash", "el análisis no devolvió nada", link)


def write_shortcut_json(data):
    """Copia legible de la última salida (state/shortcut_analysis.json)."""
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(SHORTCUT_JSON, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    except OSError as _ign:
        ignore("write_shortcut_json", _ign)


def shortcut_mode(flags, pos):
    """`--scm LINK`: nada en pantalla salvo el JSON final (una línea). Termina SIEMPRE con código 0
    (un código ≠ 0 haría fallar la acción de Atajos); el fallo va en «ok»: false y «error»."""
    link = pos[0] if pos else None
    real_out, real_err = sys.stdout, sys.stderr
    sink = open(os.devnull, "w", encoding="utf-8")
    sys.stdout = sys.stderr = sink              # mensajes internos, yt-dlp, avisos: nada ensucia la salida
    SCM["on"] = True
    data = None
    try:
        left = max(1.0, SCM_TIMEOUT - (time.time() - SCM_T0)) if SCM_TIMEOUT > 0 else None
        data = collect_with_timeout(link, secs=left)
        if data and data.get("error_code") == "timeout":
            data["use_scb"] = True              # el atajo debe seguir con --scb (sin tope de tiempo)
            data["error"] = "El análisis tardó demasiado para --scm; usa --scb."
    except KeyboardInterrupt:
        data = shortcut_error("cancelled", "Cancelado.", link)
    except BaseException as e:
        data = shortcut_error("crash", f"{type(e).__name__}: {e}", link)
    finally:
        sys.stdout, sys.stderr = real_out, real_err
        if data_is_final(data):
            sink.close()                        # con «timeout» el hilo sigue vivo y podría escribir
    text = json.dumps(data, ensure_ascii=True, separators=(",", ":"))
    if not data_is_final(data):
        # «timeout»: el análisis sigue vivo en otro hilo. Se imprime el JSON YA y se le pide al hilo que pare
        # (abort + sockets de 2 s); se espera un poco a que termine solo y se sale normal. NO se usa os._exit:
        # en a-Shell mataba el proceso con el hilo dentro de ssl y daba «Fatal Python error … segmentation fault»
        real_out.write(text + "\n")
        real_out.flush()
        SCM["abort"].set()
        th = SCM.get("thread")
        if th is not None:
            th.join(SCM_UNWIND)
        return 0
    write_shortcut_json(data)
    if flags.get("shortcutclip"):
        shortcut_copy(text)
    real_out.write(text + "\n")
    real_out.flush()
    return 0


def data_is_final(data):
    return bool(data) and data.get("error_code") != "timeout"


def shortcut_send(data, name=None):
    """Abre shortcuts://run-shortcut?name=… con el JSON como entrada (sin «videos» ni «tracks»: el atajo no los
    usa y así la URL es corta). Si pasa de SC_URL_MAX viaja por el portapapeles. Devuelve «url» o «portapapeles»."""
    name = name or SHORTCUT_NAME
    slim = {k: v for k, v in data.items() if k not in ("videos", "tracks")}
    text = json.dumps(slim, ensure_ascii=True, separators=(",", ":"))
    url = ("shortcuts://run-shortcut?name=" + urllib.parse.quote(name)
           + "&input=text&text=" + urllib.parse.quote(text, safe=""))
    how = "url"
    if len(url) > SC_URL_MAX and shortcut_copy(text):
        url, how = shortcut_clip_url(name), "portapapeles"
    dbg("scb", {"via": how, "bytes": len(text), "url": url[:80]})
    os.system("open " + shlex.quote(url))
    return how


def shortcut_back(flags, pos):
    """`--scb LINK` (iOS): analiza en primer plano (sin el límite de espera de Atajos) y al acabar AVISA al atajo
    «DLpy» con el JSON (éxito o error), sin animaciones ni mensajes."""
    link = pos[0] if pos else None
    val = flags.get("scb")
    name = val.strip() if isinstance(val, str) and val.strip() else SHORTCUT_NAME
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
    except OSError as _ign:
        ignore("shortcut_back", _ign)
    # sin banner, barra ni mensajes: solo se crea el JSON y se abre el atajo con él
    try:
        if not is_installed("yt_dlp"):          # sin yt-dlp se instala aquí (en primer plano, sin tope)
            pip_install("yt-dlp")
            refresh_paths()
    except BaseException as _ign:
        ignore("shortcut_back", _ign)
    try:
        data = collect_with_timeout(link)
    except KeyboardInterrupt:
        data = shortcut_error("cancelled", "Cancelado.", link)
    write_shortcut_json(data)
    shortcut_send(data, name)
    return 0


def shortcut_find_track(tracks, key):
    """Pista por idioma (o por format_id), sin distinguir mayúsculas; None si no existe."""
    if not key:
        return None
    k = str(key).strip().lower()
    return next((t for t in tracks
                 if t["lang"].lower() == k or str(t["fmt"].get("format_id")).lower() == k), None)


def shortcut_resolve_video(pick_, audios, videos, tracks, orig_ids, can_merge, auto=None):
    """(tipo, formato) de lo que eligió el atajo, o None si no hay elección / ya no existe."""
    v = str((pick_ or {}).get("v") or "")
    if not v:
        return None
    if v.lower() == "best":
        return auto_best(audios, videos, orig_ids, can_merge, quiet=True)
    if v.lower() == "ytdlp":                       # lo que elegiría yt-dlp (bv*+ba/b)
        return ("v", auto[0]) if auto else None
    if v.lower() == "audio":
        t = shortcut_find_track(tracks, pick_.get("a")) or (tracks[0] if tracks else None)
        return ("a", t["fmt"]) if t else None
    f = next((x for x in videos if str(x.get("format_id")) == v), None)
    return ("v", f) if f else None


def shortcut_tracks(pick_, tracks, original):
    """(predeterminada, seleccionadas) según el atajo; sin «a» vale la original, sin «x» no hay adicionales."""
    primary = shortcut_find_track(tracks, pick_.get("a")) or original
    selected = [primary]
    for key in pick_.get("x") or []:
        t = shortcut_find_track(tracks, key)
        if t is not None and all(t is not s for s in selected):
            selected.append(t)
    return primary, selected


# ╔══════════════════════════════════════════════════════════════════════╗
# ║ ÁREA K · AUTOPRUEBA Y SISTEMA — --selftest y --sistema               ║
# ╚══════════════════════════════════════════════════════════════════════╝
# ───────────────────────── [K1] Autoprueba ─────────────────────────
# El cuerpo de selftest() vive en este texto y se compila solo con --selftest: así el arranque normal no compila
# unas 850 líneas de pruebas que casi nunca se usan (0.6.6). Para editarlo, busca las etiquetas [T0]…[T24].
SELFTEST_SRC = r'''def _selftest_run():
    """`python dlpy.py --selftest`: pruebas rápidas de funciones puras (sin disco ni red)."""
    import tempfile
    fails = []

    # [T0] Infraestructura de la prueba
    def check(nombre, obtenido, esperado):
        if obtenido != esperado:
            fails.append(nombre)
            print(f"✗ {nombre}: esperado {esperado!r}, obtenido {obtenido!r}")

    # [T1] Texto, terminal y pip
    check("wrap no corta palabras", wrap_text("Otro video de YouTube que 'vas a ver después'. Spoiler: no.", 30),
          ["Otro video de YouTube que 'vas", "a ver después'. Spoiler: no."])
    check("wrap guiones enteros", wrap_text("uno 4K-HDR-Video dos", 12), ["uno", "4K-HDR-Video", "dos"])
    check("wrap palabra larga", wrap_text("x" * 20, 8), ["x" * 8, "x" * 8, "x" * 4])
    check("wrap emoji 2 columnas", all(dwidth(x) <= 10 for x in wrap_text("🫣 hola 🫣 mundo 🫣 otra vez", 10)), True)
    check("dwidth ansi", dwidth("\x1b[92m●\x1b[0m ab"), 4)
    check("pip args sin --no-deps", pip_args("yt-dlp", no_deps=False), ["install", "-U", "yt-dlp"])
    check("pip args con --no-deps", pip_args("yt-dlp", no_deps=True), ["install", "-U", "yt-dlp", "--no-deps"])
    # [T2] Barras y paneles de progreso
    _bar = Bar(panel=True)
    _bar.label, _bar.indet, _bar.pct, _bar.step = "1440p60", False, 12.4, "1/3"
    for _w in (30, 39, 49, 62, 80):
        os.environ["DLPY_WIDTH"] = str(_w)
        _bar.w = _w
        _anchos = set()
        for _t in ("", "↓ 1.4MB/s", "↓ 11.1MB/s  ETA 00:30", "2.8x"):
            _bar.tail = _t
            _bar.hist = [1.0, 2.0, 3.0]
            _anchos |= {dwidth(x) for x in _bar._panel_lines()}
        _bar.indet = True
        _anchos |= {dwidth(x) for x in _bar._panel_lines()}
        check(f"panel cabe en {_w}", max(_anchos) <= _w, True)
        check(f"panel 3 líneas {_w}", len(_bar._panel_lines()), 3)
        _bar.indet = False
    os.environ.pop("DLPY_WIDTH", None)
    check("done_line ancho", dwidth(_bar._done_line("Video 1080p", "480 MB")), _bar.w)
    check("spaced", spaced("↓ 3.0MB/s"), "↓ 3.0 MB/s")
    check("size_pair", size_pair(20 * 1024 ** 2, 48 * 1024 ** 2), "20/48 MB")
    # [T3] Versiones
    check("vtuple normal", vtuple("1.10.2"), (1, 10, 2))
    check("vtuple fecha", vtuple("2025.01.05"), (2025, 1, 5))
    check("vtuple None", vtuple(None), ())
    check("vtuple relleno", vtuple("1.0") == vtuple("1.0.0"), True)
    check("version_move 1.0 = 1.0.0", version_move("1.0", "1.0.0"), "igual")
    check("vtuple orden", vtuple("1.10.0") > vtuple("1.9.9"), True)

    # [T4] Nombres, etiquetas y bits por formato
    check("safe_name prohibidos", safe_name('a/b:c*d?'), "a_b_c_d_")
    check("safe_name vacío", safe_name(""), "video")
    check("safe_name puntos", safe_name("...x..."), "x")
    largo = safe_name("é" * 100)
    check("safe_name bytes", len(largo.encode("utf-8")) <= MAX_NAME_BYTES, True)

    check("etiqueta video", stream_label({"info_dict": {"vcodec": "avc1", "height": 1080}}), "1080p")
    check("etiqueta video 60fps", stream_label({"info_dict": {"vcodec": "avc1", "height": 1080, "fps": 60}}), "1080p60")
    check("etiqueta video sin altura", stream_label({"info_dict": {"vcodec": "avc1"}}), "Video")
    check("etiqueta video sin códec", stream_label({"info_dict": {"vcodec": None, "height": 1080}}), "1080p")
    check("etiqueta video vcodec none+alto", stream_label({"info_dict": {"vcodec": "none", "height": 720, "fps": 30}}), "720p")
    check("etiqueta video resolución", stream_label({"info_dict": {"resolution": "1920x1080"}}), "1920x1080")
    check("etiqueta audio idioma", stream_label({"info_dict": {"vcodec": "none", "language": "es-US"}}), "es-US")
    check("etiqueta audio sin idioma", stream_label({"info_dict": {"vcodec": "none"}}), "Audio")
    check("bits 10 format_note", detect_bit_depth({"format_note": "10-bit hdr"}), 10)
    check("bits main10", detect_bit_depth({"vcodec": "vp09.00.51.08", "format": "main10"}), 10)
    check("bits bit_depth", detect_bit_depth({"bit_depth": 10}), 10)
    check("bits sin dato", detect_bit_depth({"format_note": "hdr", "dynamic_range": "HDR10"}), None)
    check("bits 8 no inventa", detect_bit_depth({"height": 1080, "vcodec": "vp9"}), None)
    for _c, _b in (("vp09.02.51.10", 10), ("vp09.00.51.08", 8), ("vp09.02.51.10.01.09.16.09.00", 10),
                   ("vp09.02.51", 10), ("vp9.2", 10), ("vp9", None),
                   ("av01.0.12M.10", 10), ("av01.0.08M.08", 8), ("av01.0.05M.12", 12), ("av01", None),
                   ("hvc1.2.4.L120.90", 10), ("hev1.2.4.L153.B0", 10), ("hvc1.1.6.L93.B0", 8), ("hvc1", None),
                   ("hvc1.4.10.L120", None), ("dvh1.08.06", 10), ("dvhe.05.06", 10), ("dvh1.09.01", 8),
                   ("avc1.640028", 8), ("avc1.4d401f", 8), ("avc1.6e0028", 10), ("avc1.7a001f", 10),
                   ("avc1.f4001f", 10), ("avc1.zzzzzz", None), ("none", None), (None, None), ("", None)):
        check("códec bits " + str(_c), codec_bit_depth(_c), _b)
    check("bits por códec", detect_bit_depth({"vcodec": "vp09.02.51.10"}), 10)
    # [T5] Fallos abruptos, ffmpeg, bits, bitrate y metadatos de conversión
    check("abrupt_why sin pregunta", abrupt_why({"version": "0.1.6"}),
          "La ejecución anterior de la 0.1.6 se cortó sin terminar y esa versión aún no había terminado bien.")
    check("abrupt_why con pregunta", abrupt_why({"version": "0.1.6", "prompt": "¿Instalar yt-dlp? (S/n) ▸"}),
          "La ejecución anterior de la 0.1.6 se cortó en la pregunta «¿Instalar yt-dlp? (S/n) ▸» y esa versión aún no había terminado bien.")
    _rf = os.path.join(tempfile.mkdtemp(), "running.json")
    _old_rf = globals()["RUNNING_FILE"]
    globals()["RUNNING_FILE"] = _rf
    try:
        note_prompt("sin archivo")
        check("note_prompt sin ejecución vigilada no crea", os.path.exists(_rf), False)
        save_json(_rf, {"version": "0.1.6", "pid": 1, "time": 5})
        note_prompt("  ¿Usarlo?\n (S/n) ▸ ")
        _d = load_json(_rf)
        check("note_prompt guarda texto limpio", _d.get("prompt"), "¿Usarlo? (S/n) ▸")
        check("note_prompt conserva versión y pid", (_d.get("version"), _d.get("pid")), ("0.1.6", 1))
        note_prompt("x" * 300)
        check("note_prompt recorta", len(load_json(_rf)["prompt"]), 100)
    finally:
        globals()["RUNNING_FILE"] = _old_rf
    for _p, _b in (("yuv420p", 8), ("yuv420p10le", 10), ("yuv422p10le", 10), ("yuv444p12le", 12), ("p010le", 10),
                   ("nv12", 8), ("yuvj420p", 8), ("gbrp10le", 10), ("yuv420p9le", 9), ("xyz", None), (None, None)):
        check("pix_bits " + str(_p), pix_bits(_p), _b)
    _l = ("  Stream #0:0[0x1](und): Video: hevc (Main 10) (hvc1 / 0x31637668), yuv420p10le(tv, progressive), "
          "160x90 [SAR 1:1 DAR 16:9], 17 kb/s, 10 fps\n  Stream #0:1: Audio: aac, 44100 Hz\n")
    check("parse ffmpeg 10 bits", parse_ffmpeg_video(_l),
          {"codec": "hevc", "profile": "Main 10", "pix_fmt": "yuv420p10le", "bits": 10, "kbps": 17})
    check("parse ffmpeg 8 bits", parse_ffmpeg_video("Stream #0:0: Video: h264 (High) (avc1 / 0x31637661), "
                                                    "yuv420p(tv, bt709), 1280x720")["bits"], 8)
    check("parse ffmpeg sin video", parse_ffmpeg_video("Stream #0:0: Audio: aac"), None)
    check("parse ffmpeg vacío", parse_ffmpeg_video(""), None)
    _pl = {"venc": True, "vsrc": "vp09", "out_bits": 10}
    check("bits: leídos mandan", conversion_bits(_pl, "hevc", {"bits": 8}), 8)
    check("bits: deducido x264", conversion_bits(_pl, "h264", None), 8)
    check("bits: deducido hevc pedido", conversion_bits(_pl, "hevc", None), 10)
    check("bits: hevc 8 pedido", conversion_bits(dict(_pl, out_bits=8), "hevc", None), 8)
    check("bits: remux sin lectura", conversion_bits({"venc": False, "vsrc": "hvc1"}, None, None), None)
    check("bits: audio", conversion_bits({"venc": False, "vsrc": None}, None, None), None)
    check("aviso 10→8 x264", bits_warning(10, 8, "h264"), "Se pidieron 10 bits pero el video quedó en 8 bits (x264 solo hace 8 bits).")
    check("aviso 10→8 otro", bits_warning(10, 8, "hevc"), "Se pidieron 10 bits pero el video quedó en 8 bits.")
    check("aviso: todo bien", bits_warning(10, 10, "hevc"), None)
    check("aviso: pidió 8", bits_warning(8, 8, "hevc"), None)
    check("aviso: sin dato", bits_warning(10, None, "hevc"), None)
    check("kbps cambio Mbps", bitrate_change(4100, 2300), "4.1 → 2.3 Mbps (−44 %)")
    check("kbps cambio kbps", bitrate_change(900, 1000), "900 kbps → 1.0 Mbps (+11 %)")
    check("kbps cambio estimado", bitrate_change(4000, 2000, True), "4.0 → ~2.0 Mbps (−50 %)")
    check("kbps cambio igual", bitrate_change(500, 500), "500 → 500 kbps (sin cambio)")
    check("kbps origen vbr", source_video_kbps({"vbr": 4100.4}), 4100)
    check("kbps origen tbr sin audio", source_video_kbps({"tbr": 3000, "acodec": "none"}), 3000)
    check("kbps origen tbr con audio", source_video_kbps({"tbr": 3000, "acodec": "mp4a", "abr": 128}), 2872)
    check("kbps origen nada", source_video_kbps({}), None)
    check("origen sitio/canal", source_info({"webpage_url_domain": "www.youtube.com", "channel": "Canal X"}),
          {"site": "youtube.com", "channel": "Canal X"})
    check("origen vacío", source_info(None), {})
    _mc = build_meta("v", {"format_id": "1", "vcodec": "vp09.02.51.10", "vbr": 4100, "height": 1080},
                     "1", None, set(), "a.mp4",
                     {"venc": True, "vcodec": "hevc", "aenc": [], "bits": 8, "vbr": 2300,
                      "engine": "VideoToolbox", "secs": 38}, {"webpage_url_domain": "youtube.com", "channel": "C"})
    check("meta conv", _mc["conv"], {"vfrom": "vp09", "bfrom": 10, "vbr_from": 4100, "vbr_to": 2300,
                                      "engine": "VideoToolbox", "secs": 38})
    check("meta source", _mc["source"], {"site": "youtube.com", "channel": "C"})
    check("filas conv", conv_rows(_mc), [("Convertido", "vp09 → HEVC · 10 → 8 bits"),
                                         ("", "VideoToolbox · 38 s"),
                                         ("Bitrate", "4.1 → 2.3 Mbps (−44 %)")])
    _ma = build_meta("v", {"format_id": "1", "vcodec": "avc1.640028"}, "1",
                     [{"lang": "en", "original": True, "fmt": {"format_id": "a", "acodec": "opus", "abr": 130}}],
                     {"a"}, "a.mp4", {"venc": False, "vcodec": None, "aenc": [True], "bits": None, "abr": 192})
    check("audio recodificado: códec y bitrate", (_ma["tracks"][0]["codec"], _ma["tracks"][0]["abr"]), ("aac", 192))
    check("audio recodificado: origen guardado", _ma["conv"]["afrom"], ["opus"])
    check("filas sin conv", conv_rows({"converted": False}), [])
    _tr = [{"lang": "en", "codec": "mp4a", "abr": 130, "original": True, "default": True},
           {"lang": "es", "codec": "mp4a", "abr": 128}]
    check("audio varias", audio_rows(_tr), ([("Audio", "2 pistas · mp4a 128-130k"), ("", "en◆▸ es")], True))
    check("audio una", audio_rows(_tr[:1]), ([("Audio", "en · mp4a 130k")], False))
    check("audio ninguna", audio_rows([]), ([("Audio", "sin pistas de audio")], False))
    check("meta bits origen", build_meta("v", {"format_id": "1", "vcodec": "vp09.02.51.10"}, "1", None, set(),
                                         "a.mp4")["video"]["bits"], 10)
    check("meta bits convertido", build_meta("v", {"format_id": "1", "vcodec": "vp09.02.51.10"}, "1", None, set(),
                                             "a.mp4", {"venc": True, "vcodec": "h264", "aenc": [], "bits": 8})["video"]["bits"], 8)
    check("meta bits recodificado sin lectura", "bits" in build_meta("v", {"format_id": "1", "vcodec": "vp09.02.51.10"}, "1",
          None, set(), "a.mp4", {"venc": True, "vcodec": "hevc", "aenc": [], "bits": None})["video"], False)
    # [T6] Sondeo con ffmpeg real, rango HDR, yt-dlp auto y encoders
    _ff = shutil.which("ffmpeg")
    if _ff:
        import subprocess as _sp
        _d = tempfile.mkdtemp()
        for _n, _px, _want in (("t8.mp4", "yuv420p", 8), ("t10.mp4", "yuv420p10le", 10)):
            _f = os.path.join(_d, _n)
            _enc = ["-c:v", "libx265", "-x265-params", "profile=main10:log-level=none"] if _want == 10 else ["-c:v", "libx264"]
            _r = _sp.run([_ff, "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=d=1:s=160x90:r=10"] + _enc
                         + ["-pix_fmt", _px, _f], capture_output=True)
            if _r.returncode == 0:
                check("probe real " + _n, (probe_video(_ff, _f) or {}).get("bits"), _want)
                _only = os.path.join(_d, "solo_ffmpeg")        # sin ffprobe: «ffmpeg -i»
                os.makedirs(_only, exist_ok=True)
                _lnk = os.path.join(_only, "ffmpeg")
                try:
                    os.symlink(_ff, _lnk)
                    _old = os.environ.get("PATH", "")
                    os.environ["PATH"] = _only
                    try:
                        check("probe real sin ffprobe " + _n, (probe_video(_lnk, _f) or {}).get("bits"), _want)
                    finally:
                        os.environ["PATH"] = _old
                except OSError as _ign:
                    ignore("selftest probe", _ign)
        shutil.rmtree(_d, ignore_errors=True)
    check("bits texto manda sobre códec", detect_bit_depth({"vcodec": "vp09.00.51.08", "format": "main10"}), 10)
    check("rango 10b HDR", range_label({"vcodec": "vp09.02.51.10", "dynamic_range": "HDR10"}), "10b HDR10")
    check("rango solo 10b", range_label({"vcodec": "hvc1.2.4.L120.90"}), "10b")
    _fa = {"format_id": "a1", "ext": "m4a", "vcodec": "none", "acodec": "mp4a.40.5", "abr": 44}
    _fv = {"format_id": "v1", "ext": "mp4", "vcodec": "vp09.00.40.08", "acodec": "none", "height": 1080}
    _au = ytdlp_auto_pick({"requested_formats": [_fv, _fa]}, [_fa], [_fv])
    check("yt-dlp auto elige video+audio", (_au[0]["format_id"], _au[1]["format_id"]) if _au else None, ("v1", "a1"))
    check("yt-dlp auto sin selección", ytdlp_auto_pick({}, [_fa], [_fv]), None)
    check("yt-dlp auto descripción", (video_desc(_fv), audio_desc(_fa)), ("1080p vp09", "m4a mp4a 44k"))
    check("rango solo HDR", range_label({"vcodec": "unknown", "dynamic_range": "HLG"}), "HLG")
    check("rango SDR 8b", range_label({"vcodec": "avc1.640028", "dynamic_range": "SDR"}), "8b")
    check("rango sin datos vacío", range_label({"vcodec": "avc1", "dynamic_range": "SDR"}), "")
    for _t, _w in (("8-bit", 8), ("6 bits", 6), ("12-bit hdr", 12), ("main12", 12), ("14 bits", 14), ("16bit", 16)):
        check("bits texto " + _t, detect_bit_depth({"format_note": _t}), _w)
    check("bits bit_depth 12", detect_bit_depth({"bit_depth": 12}), 12)
    for _b, _w in ((None, 8), (6, 8), (8, 8), (9, 10), (10, 10), (11, 12), (12, 12), (14, 12), (16, 12)):
        check(f"encode_bits {_b}", encode_bits(_b), _w)
    check("pix 12", out_pix(12), "yuv420p12le")
    check("opciones 10", [b for b, _ in bits_choices(10)], [10, 8])
    check("opciones 12", [b for b, _ in bits_choices(12)], [12, 10, 8])
    check("opciones 16", [b for b, _ in bits_choices(16)], [12, 10, 8])
    _a12 = video_encoder_attempts({"venc": True, "vbr": 4000, "out_bits": 12})
    check("encoders 12: primero x265 12", (_a12[0][1], "profile=main12" in _a12[0][2]), ("x265 12 bits", True))
    check("encoders 12: cae a 10 y 8", [a[1] for a in _a12[1:]], ["VideoToolbox HEVC 10 bits", "x265 10 bits", "x264"])
    _a10 = video_encoder_attempts({"venc": True, "vbr": 4000, "out_bits": 10})
    check("encoders 10: main10", ("main10" in " ".join(_a10[0][2]) or "profile=main10" in " ".join(_a10[1][2])), True)
    _a8 = video_encoder_attempts({"venc": True, "vbr": 4000, "out_bits": 8})
    check("encoders 8: yuv420p", "yuv420p" in _a8[0][2], True)
    # [T7] Columnas, sí/no y listas cortas
    _r = [{"n": 1, "flags": set(), "cols": ["1080p", "mp4", "avc1", "", "con audio", "5MB"]},
          {"n": 2, "flags": set(), "cols": ["720p", "mp4", "avc1", "", "sin audio", "3MB"]}]
    check("cols vacías se quitan", drop_empty_cols(_r, VIDEO_HEAD)[1], ["Res", "Fmt", "Códec", "Audio", "Tamaño"])
    check("cols vacías en filas", drop_empty_cols(_r, VIDEO_HEAD)[0][0]["cols"], ["1080p", "mp4", "avc1", "con audio", "5MB"])
    _r[1]["cols"][3] = "10b"
    check("col con dato se queda", drop_empty_cols(_r, VIDEO_HEAD)[1], VIDEO_HEAD)
    check("drop no muta", _r[0]["cols"][3], "")
    check("video_row con rango", video_row(1, {"height": 2160, "ext": "webm", "vcodec": "vp09.02.51.10",
                                               "acodec": "none", "dynamic_range": "HDR10"})["cols"][3], "10b HDR10")
    check("hdr dynamic_range", detect_hdr({"dynamic_range": "HDR10"}), "HDR10")
    check("hdr ninguno", detect_hdr({"format_note": "sdr"}), None)
    check("yes vacío/def", yes("", False), False)
    check("yes s", yes(" S "), True)
    check("yes n", yes("n"), False)
    check("parse_yn vacío/def", parse_yn("", False), False)
    check("parse_yn sí", parse_yn(" Sí "), True)
    check("parse_yn no", parse_yn("NO"), False)
    check("parse_yn inválido", parse_yn("x"), None)
    _sr = [{"flags": set()}, {"flags": {"apple"}}, {"flags": set()}, {"flags": {"apple"}}, {"flags": {"apple"}}]
    check("lista corta: compatibles", short_pick(_sr, 2), [3, 4])
    check("lista corta: caben todas", short_pick(_sr, 9), [1, 3, 4])
    check("lista corta: «b» siempre entra", short_pick(_sr, 2, 0), [0, 4])
    check("lista corta: sin compatibles", short_pick([{"flags": set()}] * 4, 2), [2, 3])
    check("lista corta: vacía", short_pick([], 3), [])
    check("lista corta: primeras (first)", short_pick(_sr, 1, None, None, True), [1])
    check("lista corta: first con «b» al final", short_pick(_sr, 2, 4, None, True), [1, 4])
    _rows_env = os.environ.pop("DLPY_ROWS", None)
    check("visible_cap con lines", visible_cap(12, 28), 16)
    check("visible_cap 26 líneas", visible_cap(12) if UI_LINES == 26 else 14, 14)
    check("visible_cap mínimo", visible_cap(12, 10), 4)
    check("list_cap 26 líneas", list_cap(16) if UI_LINES == 26 else 10, 10)
    check("list_cap con overhead", list_cap(10) >= 8, True)
    if _rows_env is not None:
        os.environ["DLPY_ROWS"] = _rows_env
    import tempfile as _tf
    # [T8] Variables DLPY_* y carpetas
    _ed = _tf.mkdtemp()
    _ep = os.path.join(_ed, "e.json")
    persist_env({"DLPY_COLOR": "1", "DLPY_ROWS": "12", "HOME": "x", "DLPY_MOVED": "1"}, _ep)
    _e = {}
    persist_env(_e, _ep)
    check("env: se recuperan las guardadas (sin las de una ejecución)", _e, {"DLPY_COLOR": "1", "DLPY_ROWS": "12"})
    _e = {"DLPY_COLOR": "0"}
    persist_env(_e, _ep)
    check("env: lo definido manda y se guarda", _e, {"DLPY_COLOR": "0", "DLPY_ROWS": "12"})
    _e = {}
    persist_env(_e, _ep)
    check("env: queda el último valor", _e.get("DLPY_COLOR"), "0")
    _e = {"DLPY_FORGET": "1"}
    persist_env(_e, _ep)
    check("env: FORGET olvida", _e, {"DLPY_FORGET": "1"})
    _e = {}
    persist_env(_e, _ep)
    check("env: tras olvidar no hay nada", _e, {})
    _ip = os.path.join(_ed, "nuevo", "carpeta", "env.json")        # crea la carpeta si falta
    persist_env({"DLPY_ROWS": "9", "OTRA": "x"}, _ip)
    check("env: crea la carpeta y guarda solo DLPY_*", (os.path.isfile(_ip), _read_env_json(_ip)),
          (True, {"DLPY_ROWS": "9"}))
    _blk = os.path.join(_ed, "bloqueado")
    with open(_blk, "w") as _f:
        _f.write("x")
    persist_env({"DLPY_COLOR": "1"}, os.path.join(_blk, "env.json"))      # «carpeta» que es un archivo
    check("env: el fallo queda anotado", bool(ENV_STATE["error"]), True)
    check("env: ruta iOS dentro de la carpeta oculta",
          env_file_path("/h"), os.path.join("/h", "Documents", "dlpy_files", ".dlpy_internal", "env.json"))
    check("internal oculta dentro de files", (os.path.dirname(INTERNAL_DIR) == FILES_DIR,
                                              os.path.basename(INTERNAL_DIR).startswith(".")), (True, True))
    check("archivos: qué cuenta como descarga en dlpy_files",
          [is_data_entry(n) for n in (INTERNAL_NAME, "backups", "changelog.md", "x.part",
                                      "x.ytdl", "x.tmp", "video.mp4", "audio.m4a", "Mi carpeta")],
          [False, False, False, False, False, False, True, True, True])
    shutil.rmtree(_ed, ignore_errors=True)
    # [T9] Calidad por fila, borrado de líneas y cuándo toca comprobar
    check("lista corta: solo únicas", short_pick(_sr, 9, None, [3, 4]), [3, 4])
    check("lista corta: «b» fuera de únicas entra", short_pick(_sr, 2, 0, [3, 4]), [0, 4])
    _vq = [{"height": 1080, "ext": "webm", "vcodec": "vp9"}, {"height": 1080, "ext": "mp4", "vcodec": "avc1"},
           {"height": 720, "ext": "mp4", "vcodec": "avc1"}, {"height": 1080, "fps": 60, "ext": "mp4", "vcodec": "avc1"}]
    _vk = video_quality_keys(_vq)
    check("calidad video: misma res = mismo grupo", _vk[0] == _vk[1] and _vk[1] != _vk[2] and _vk[3] != _vk[1], True)
    _vr = [{"flags": set()}, {"flags": {"apple"}}, {"flags": {"apple"}}, {"flags": {"apple"}}]
    check("una por calidad: gana la compatible", best_per_quality(_vr, _vk, lambda i: ("apple" in _vr[i]["flags"], i)),
          [1, 2, 3])
    check("una por calidad: «b» manda en su grupo", best_per_quality(_vr, _vk, lambda i: ("apple" in _vr[i]["flags"], i), 0),
          [0, 2, 3])
    _aq = audio_quality_keys([{"abr": 48, "language": "es"}, {"abr": 128, "language": "es"},
                              {"abr": 130, "language": "es"}, {"abr": 130, "language": "en"}, {"abr": 160, "language": "es"}])
    check("calidad audio: ±12 % y por idioma", (_aq[1] == _aq[2], _aq[2] != _aq[3], _aq[0] != _aq[1], _aq[4] != _aq[1]),
          (True, True, True, True))
    check("yn_line marca la opción", ("Sí" in _ANSI_RE.sub("", yn_line(True))) and ("[S]" in _ANSI_RE.sub("", yn_line(True))), True)
    check("yn_line (s/N)", "[N]" in _ANSI_RE.sub("", yn_line(False)), True)
    check("borrar 1 fila", erase_seq("▸ ", "x", 50), "\x1b[1A\x1b[2K\r")
    check("borrar con ANSI/readline", erase_seq("\x01\x1b[31m\x02▸\x01\x1b[0m\x02 ", "7", 50), "\x1b[1A\x1b[2K\r")
    check("borrar 2 filas", erase_seq("▸ ", "x" * 60, 50), "\x1b[1A\x1b[2K" * 2 + "\r")
    check("retry sin terminal: mismo prompt", retry_prompt("▸ ", "", None) if not INPLACE else "▸ ", "▸ ")
    check("toca: nunca hecho", due_from(None, None, 1000, 24), True)
    check("toca: reciente", due_from({"t": 1000, "sig": "a"}, "a", 1000 + 3600, 24), False)
    check("toca: pasaron 24 h", due_from({"t": 1000, "sig": "a"}, "a", 1000 + 24 * 3600, 24), True)
    check("toca: firma cambió", due_from({"t": 1000, "sig": "a"}, "b", 1000 + 60, 24), True)
    check("toca: sin firma", due_from({"t": 1000, "sig": None}, None, 1000 + 60, 24), False)
    check("toca: reloj hacia atrás", due_from({"t": 5000, "sig": "a"}, "a", 1000, 24), True)
    check("toca: 0 horas = siempre", due_from({"t": 1000, "sig": "a"}, "a", 1001, 0), True)
    check("nombre a-Shell", platform_name({"APPNAME": "a-Shell"}), "a-Shell · iOS")
    check("nombre a-Shell mini", platform_name({"APPNAME": "a-Shell-mini"}), "a-Shell mini · iOS")
    check("modo iOS", (PLATFORM, IS_IOS, APPLE_MODE), ("ios", True, True))
    check("safe_name CON no cambia", safe_name("CON"), "CON")
    # [T10] JavaScript, versión remota y capabilities
    check("ejs_pin fijo", ejs_pin(["brotli; extra == 'default'", "yt-dlp-ejs==0.8.0; extra == 'default'"]),
          "yt-dlp-ejs==0.8.0")
    check("ejs_pin sin versión", ejs_pin(["yt-dlp-ejs"]), "yt-dlp-ejs")
    check("ejs_pin ausente", ejs_pin(["brotli"]), None)
    check("remote_script_version ok", remote_script_version('#!dlpy.py x\nVERSION = "1.2.3"\n'), "1.2.3")
    check("remote_script_version html", remote_script_version('<html>VERSION = "1.2.3"</html>'), None)
    check("remote_script_version sin versión", remote_script_version("#!dlpy.py\nx = 1\n"), None)
    check("js requerido nuevo", ytdlp_needs_js("2025.11.12"), True)
    check("js requerido viejo", ytdlp_needs_js("2025.10.22"), False)
    check("js requerido vacío", ytdlp_needs_js(""), False)
    check("js args node", js_runtime_args([], "2026.03.17", ("node", "/x/node")), ["--js-runtimes", "node"])
    check("js args deno por defecto", js_runtime_args([], "2026.03.17", ("deno", "/x/deno")), [])
    check("js args sin runtime", js_runtime_args([], "2026.03.17", None), [])
    check("js args yt-dlp viejo", js_runtime_args([], "2025.01.01", ("node", "/x/node")), [])
    check("js args respeta al usuario", js_runtime_args(["--js-runtimes", "bun"], "2026.03.17", ("node", "/x/node")), [])
    _caps = capabilities()
    check("capabilities forma", all(len(c) == 3 and c[1] in ("ok", "no", "part", "na") and c[2] for c in _caps), True)
    check("capabilities cubre ffmpeg", any("ffmpeg" in c[0] for c in _caps), True)
    _pr = profile_rows()
    check("perfil: filas con etiqueta y milisegundos", all(isinstance(r[0], str) and (r[1] is None or r[1] >= 0) for r in _pr), True)
    _pt = preload_ytdlp()
    _pt.join(30)
    check("precarga de yt_dlp: el hilo termina sin reventar", _pt.is_alive(), False)
    check("perfil: mide al menos compilar y cargar", sum(1 for r in _pr if r[1] is not None) >= 2, True)
    # [T11] Reanudación, URLs de atajo, changelog en bloque y sí/no
    _sp = [("137", "mp4", 1000), ("140", "m4a", 50)]
    check("resume_key estable", resume_key("v", _sp), resume_key("v", list(_sp)))
    check("resume_key prefijo", resume_key("v", _sp).startswith(RESUME_PREFIX), True)
    check("resume_key otro formato", resume_key("v", _sp) != resume_key("v", [("136", "mp4", 1000), ("140", "m4a", 50)]), True)
    check("resume_key otro tamaño", resume_key("v", _sp) != resume_key("v", [("137", "mp4", 1001), ("140", "m4a", 50)]), True)
    check("resume_key otro video", resume_key("v", _sp) != resume_key("w", _sp), True)
    check("resume_key sin tamaño", resume_key("v", [("18", "mp4", None)]), resume_key("v", [("18", "mp4", 0)]))

    _u = shortcut_run_url({"file_path": "/a b/dlpy.py", "kind": "script"}, "DLpy")
    check("shortcut url inicio", _u.startswith("shortcuts://run-shortcut?name=DLpy&input=text&text="), True)
    check("shortcut url payload",
          json.loads(urllib.parse.unquote(_u.split("&text=", 1)[1])),
          {"file_path": "/a b/dlpy.py", "kind": "script"})
    check("shortcut clip url", shortcut_clip_url("DLpy"),
          "shortcuts://run-shortcut?name=DLpy&input=clipboard")
    _code = "#!dlpy.py - x\nprint('a&b %20')\n"
    check("shortcut text url", urllib.parse.unquote(shortcut_text_url(_code, "DLpy").split("&text=", 1)[1]), _code)
    _head = ("#!dlpy.py - x\n# a\n# b\n# Conservar en todo momento los comentarios.\n")
    _md = "# Changelog DLpy\n\n## 1.0.1\n\n- Dos.\n  sigue\n\n## 1.0.0\n\n- Uno.\n"
    _blk = changelog_block_from_md(_md)
    check("cl bloque", _blk, "# ==== CHANGELOG ====\n# ## 1.0.1\n#\n# - Dos.\n#   sigue\n#\n"
          "# ## 1.0.0\n#\n# - Uno.\n# ==== FIN CHANGELOG ====\n")
    check("cl bloque vacío", changelog_block_from_md("nada"), None)
    _body = '# DLpy\nVERSION = "' + VERSION + '"\n'
    _full = _head + _blk + _body
    check("variantes con bloque", script_variants(_full, "", ""), (_head + _body, _full))
    check("variantes snapshot", script_variants(_head + _body, _full, ""), (_head + _body, _full))
    check("variantes snapshot viejo", script_variants(_head + _body, _full.replace(VERSION, "0.0.0"), _md)[1], _full)
    check("variantes desde md", script_variants(_head + _body, "", _md)[1], _full)
    check("variantes sin fuente", script_variants(_head + _body, "", "")[1], None)
    check("yn sin sufijo", yn_prompt("¿Seguir?"), "¿Seguir? (S/n) ▸ ")
    check("yn sin sufijo no", yn_prompt("¿Seguir?", False), "¿Seguir? (s/N) ▸ ")
    check("yn sufijo repetido", yn_prompt("¿Seguir? (S/n) ▸ "), "¿Seguir? (S/n) ▸ ")
    check("yn sufijo distinto al default", yn_prompt("¿Borrar? (S/n) ▸ ", False), "¿Borrar? (s/N) ▸ ")
    check("yn solo flecha", yn_prompt("¿Seguir? ▸ "), "¿Seguir? (S/n) ▸ ")
    check("yn conserva paréntesis", yn_prompt("¿Instalar (3 MB)?"), "¿Instalar (3 MB)? (S/n) ▸ ")
    _nl = [_ANSI_RE.sub("", x) for x in release_notes_lines("- uno\n  dos\n  tres\n\n- cuatro\n## Título\nresto\n  sigue", 60)]
    check("notas: las líneas partidas a mano se unen", _nl, ["• uno dos tres", "", "• cuatro", "", "Título", "resto sigue"])
    import contextlib as _cx
    import io as _io
    with _cx.redirect_stdout(_io.StringIO()) as _qb:
        print_question("¿Instalar? (S/n) ▸ ")
    check("pregunta: «▍¿…?» sin el sufijo s/n", _ANSI_RE.sub("", _qb.getvalue()), "▍¿Instalar?\n")
    check("yn_line con tercera opción", _ANSI_RE.sub("", yn_line(True, ("m", "Todos"))), " [S] Sí  [n] No  [m] Todos ▸ ")
    check("yn multilínea", yn_prompt("¿Mover (1 MB) a backups? (s/N) ▸ ", False), "¿Mover (1 MB) a backups? (s/N) ▸ ")
    # [T12] Conversión rápida, update_status y --2shortcuts
    _remux = {"venc": False, "height": 1080, "fps": 30}
    _v1080 = {"venc": True, "height": 1080, "fps": 30}
    _v4k = {"venc": True, "height": 2160, "fps": 30}
    _v4kslow = {"venc": True, "height": 2160, "fps": 60}
    check("quick remux", convert_is_quick(_remux, 600), True)
    check("quick 1080 corto", convert_is_quick(_v1080, 30), True)
    check("quick 4k muy corto", convert_is_quick(_v4k, 10), True)
    check("quick 1080 largo no", convert_is_quick(_v1080, 300), False)
    check("quick 4k60 largo no", convert_is_quick(_v4kslow, 120), False)
    check("quick sin duración", convert_is_quick(_v1080, None), False)
    check("quick est remux", convert_est_secs(_remux, 100), 0.0)
    check("update_status nueva", update_status("9.9.9", "0.7.1"), "nueva")
    check("update_status igual", update_status("0.7.1", "0.7.1"), "igual")
    check("update_status local", update_status("0.6.5", "0.7.1"), "local")
    check("update_status 10 > 9", update_status("0.7.10", "0.7.9"), "nueva")
    check("2shortcuts flag", wants_2shortcuts(["--2shortcuts"]), True)
    check("2shortcuts typo", wants_2shortcuts(["--2shorcuts"]), True)
    check("2shortcuts raya larga", wants_2shortcuts(["\u20142shortcuts"]), True)
    check("2shortcuts no es enlace", wants_2shortcuts(["2shortcuts", "https://x.y/2shortcuts"]), False)
    check("2shortcuts otra bandera", wants_2shortcuts(["--sistema"]), False)
    # [T13] ── recuperación y «abrir otra vez» ──
    with tempfile.TemporaryDirectory() as _td:
        # mark_delivered / deliver_existing con índice y funciones de prueba
        _old = (globals()["INDEX_FILE"], globals()["deliver"], globals()["ask_yn"], globals()["m_info"])
        try:
            globals()["m_info"] = lambda *a, **k: None
            globals()["INDEX_FILE"] = os.path.join(_td, "index.json")
            save_json(globals()["INDEX_FILE"], {"k": {"file": "v.mp4"}, "o": {"file": "w.mp4"}})
            mark_delivered("/algo/v.mp4", 1234)
            _ix = load_json(globals()["INDEX_FILE"])
            check("mark_delivered marca", _ix["k"].get("delivered"), 1234)
            check("mark_delivered no toca otros", "delivered" in _ix["o"], False)
            _calls, _asked = [], []
            globals()["deliver"] = lambda f, t: _calls.append(f)
            globals()["ask_yn"] = lambda p, default=True, seconds=False: (_asked.append(p) or False)
            check("existente sin delivered: directo", deliver_existing("v.mp4", {}, "t"), True)
            check("existente sin delivered: sin pregunta", (len(_asked), len(_calls)), (0, 1))
            check("existente entregado: dice no", deliver_existing("v.mp4", {"delivered": 5}, "t"), False)
            check("existente entregado: pregunta y no entrega", (len(_asked), len(_calls)), (1, 1))
            globals()["ask_yn"] = lambda p, default=True, seconds=False: True
            check("existente entregado: dice sí", deliver_existing("v.mp4", {"delivered": 5}, "t"), True)
            check("existente entregado: entrega", len(_calls), 2)
        finally:
            (globals()["INDEX_FILE"], globals()["deliver"],
             globals()["ask_yn"], globals()["m_info"]) = _old
    # [T14] Releases, notas de versión y changelog.md
    _info = ("o", "r")
    check("repo_info", (repo_info("o/r"), repo_info("x"), repo_info("https://x/y/z"), repo_info("")),
          (("o", "r"), None, None, None))
    check("repo_info por omisión", repo_info(), repo_info(UPDATE_REPO))
    _rel = [{"tag_name": "v0.7.5", "body": "## Cambios\r\n- Uno\r\n", "published_at": "2026-10-01T10:00:00Z",
             "assets": [{"name": "dlpy.py", "browser_download_url": "https://h/dl/dlpy.py"}]},
            {"tag_name": "0.7.6", "body": None, "created_at": "2026-10-02T10:00:00Z", "assets": []},
            {"tag_name": "v0.7.7", "prerelease": True, "assets": []},
            {"tag_name": "v0.7.8", "draft": True, "assets": []},
            {"tag_name": "nightly", "assets": [{"name": "dlpy_0.7.9.py", "browser_download_url": "https://h/dl/dlpy_0.7.9.py"},
                                                {"name": "notas.txt", "browser_download_url": "https://h/dl/notas.txt"}]},
            {"tag_name": "v0.7.5", "assets": []}, {"tag_name": "beta"}, "x"]
    check("releases: orden, etiquetas, adjuntos, notas, sin borradores ni prereleases", parse_releases(_rel, _info),
          [{"ver": "0.7.9", "url": "https://h/dl/dlpy_0.7.9.py", "notes": "", "date": ""},
           {"ver": "0.7.6", "url": "https://raw.githubusercontent.com/o/r/0.7.6/dlpy.py", "notes": "", "date": "2026-10-02"},
           {"ver": "0.7.5", "url": "https://h/dl/dlpy.py", "notes": "## Cambios\n- Uno", "date": "2026-10-01"}])
    check("releases: respuesta inválida", (parse_releases(None, _info), parse_releases({"message": "limit"}, _info)), ([], []))
    _rr = release_rows(parse_releases(_rel, _info), [("0.1.0", "/b/0.1.0/dlpy_0.1.0.py")])
    check("filas: solo Releases (los backups no se mezclan)", [(r["ver"], r["src"], r["label"]) for r in _rr],
          [("0.7.9", "release", "Release"), ("0.7.6", "release", "Release"), ("0.7.5", "release", "Release")])
    _rb = release_rows([], [("0.1.0", "/b/0.1.0/dlpy_0.1.0.py"), ("0.1.0", "/b/0.1.0-2/dlpy_0.1.0.py"),
                            ("0.0.9", "/b/0.0.9/dlpy_0.0.9.py")])
    check("filas: sin Releases usa los backups", [(r["ver"], r["src"], r["label"]) for r in _rb],
          [("0.1.0", "backup", "backup-2"), ("0.1.0", "backup", "backup"), ("0.0.9", "backup", "backup")])
    check("filas: nada", release_rows(None, None), [])
    _svr = (globals()["remote_releases"], globals()["fetch_remote_script"])
    try:
        globals()["remote_releases"] = lambda *a, **k: [
            {"ver": "9.9.9", "url": "https://h/r", "notes": "N", "date": "2026-01-02"},
            {"ver": "9.9.8", "url": "https://h/r2", "notes": "", "date": ""}]
        globals()["fetch_remote_script"] = lambda timeout=5, url=None: '#!dlpy.py\nVERSION = "9.9.9"\n'
        check("último release", fetch_latest_release(),
              {"ver": "9.9.9", "text": '#!dlpy.py\nVERSION = "9.9.9"\n', "url": "https://h/r", "notes": "N", "date": "2026-01-02"})
        globals()["fetch_remote_script"] = lambda timeout=5, url=None: None
        check("último release: sin script válido", fetch_latest_release(), None)
        globals()["remote_releases"] = lambda *a, **k: None
        check("último release: sin red", fetch_latest_release(), None)
    finally:
        (globals()["remote_releases"], globals()["fetch_remote_script"]) = _svr
    check("fetch_remote_script sin url", fetch_remote_script(), None)
    _nl = [_ANSI_RE.sub("", ln) for ln in release_notes_lines(
        "## Cambios\r\n\r\n\r\n- **Uno** con `código` y [enlace](http://x)\n  - sub item\nTexto suelto\n", 40)]
    check("release notes: formato", _nl, ["Cambios", "", "• Uno con código y enlace", "  • sub item", "Texto suelto"])
    check("release notes: vacías", release_notes_lines("  \n\n", 40), [])
    check("release notes: ajustadas al ancho",
          all(len(_ANSI_RE.sub("", ln)) <= 20 for ln in release_notes_lines("- " + "palabra " * 10, 20)), True)
    check("instalar: Enter", parse_install_answer(""), True)
    check("instalar: n", (parse_install_answer("n"), parse_install_answer(" No ")), (False, False))
    check("instalar: s", parse_install_answer("S"), True)
    check("instalar: m solo si hay más", (parse_install_answer("m"), parse_install_answer("m", True)), (None, "m"))
    check("instalar: basura", parse_install_answer("hola"), None)
    check("instalar: Enter con default No", (parse_install_answer("", False, False), parse_install_answer("s", False, False)),
          (False, True))
    import contextlib
    import io
    _ti = globals()["timed_input"]
    try:
        globals()["timed_input"] = lambda *a, **k: None          # la cuenta regresiva vence sin respuesta
        with contextlib.redirect_stdout(io.StringIO()):
            _ci = (confirm_install("x", "9.9.9", "- a", seconds=1),
                   confirm_install("x", "9.9.9", "- a", seconds=1, default=False))
        check("instalar: cuenta vencida = Sí por omisión, No si la versión falló", _ci, (True, False))
    finally:
        globals()["timed_input"] = _ti
    _sh = []
    _o = (globals()["show_release_notes"], globals()["clear_screen"], globals()["hide_keyboard"], globals()["header"],
          globals()["time"].sleep)
    try:
        globals()["show_release_notes"] = lambda *a, **k: _sh.append("n") or 0
        globals()["clear_screen"] = globals()["hide_keyboard"] = lambda *a, **k: None
        globals()["header"] = lambda *a, **k: None
        globals()["time"].sleep = lambda *a: None
        show_notes_on_apply("9.9.9", "- a", None, 0, False)
        show_notes_on_apply("9.9.9", "- a", None, 5, True)
        check("notas al aplicar: nada si caben o ya se vieron con «m»", _sh, [])
        show_notes_on_apply("9.9.9", "- a", None, 5, False)
        check("notas al aplicar: completas si estaban recortadas", _sh, ["n"])
    finally:
        (globals()["show_release_notes"], globals()["clear_screen"], globals()["hide_keyboard"], globals()["header"],
         globals()["time"].sleep) = _o
    check("is_installed recuerda los positivos", (is_installed("json"), "json" in INSTALLED_OK, is_installed("json")),
          (True, True, True))
    check("releases ordenados (todos, sin repetir)",
          [r["ver"] for r in order_releases([{"ver": "0.7.5"}, {"ver": "0.10.0"}, {"ver": "0.7.5"}, {"ver": "0.7.6"}, {}, None])],
          ["0.10.0", "0.7.6", "0.7.5"])
    check("releases ordenados: vacío", order_releases(None), [])
    check("enlaces de GitHub", [is_github_url(u) for u in (
        "https://api.github.com/repos/a/b", "https://raw.githubusercontent.com/a/b/v1/dlpy.py",
        "https://github.com/a/b/releases/download/v1/dlpy.py", "https://pypi.org/x", "https://evilgithub.com/x", "")],
        [True, True, True, False, False, False])
    _rl = [{"ver": "0.7.5", "notes": "- Uno", "date": ""}, {"ver": "0.10.0", "notes": "", "date": ""},
           {"ver": "0.7.6", "notes": "## Cambios\n- Dos", "date": ""}]
    _ov_ver = VERSION
    globals()["VERSION"] = "0.10.0"              # changelog.md llega hasta la versión actual
    _clm = changelog_md_from_releases(_rl)
    _c76 = "# Changelog DLpy\n\n## 0.7.6\n\n## Cambios\n- Dos\n\n## 0.7.5\n\n- Uno\n"
    check("changelog.md: solo la actual y las inferiores", changelog_md_from_releases(_rl, "0.7.6"), _c76)
    check("changelog.md: la actual sin Release usa la del script",
          changelog_md_from_releases(_rl, "0.11.0", "- Propio"),
          "# Changelog DLpy\n\n## 0.11.0\n\n- Propio\n\n## 0.10.0\n\n(sin release notes)\n\n" + _c76.split("\n\n", 1)[1])
    check("changelog.md: Release sin notas usa la del script",
          changelog_md_from_releases(_rl, "0.10.0", "- Propio").split("\n\n")[1:3], ["## 0.10.0", "- Propio"])
    check("changelog.md: con notas en el Release no usa la del script", changelog_md_from_releases(_rl, "0.7.6", "- Propio"), _c76)
    check("changelog.md: todo más nuevo que la actual queda vacío",
          parse_sections(changelog_md_from_releases(_rl, "0.1.0")), {})
    check("changelog.md: de los release notes, el más nuevo arriba", _clm,
          "# Changelog DLpy\n\n## 0.10.0\n\n(sin release notes)\n\n## 0.7.6\n\n## Cambios\n- Dos\n\n## 0.7.5\n\n- Uno\n")
    check("changelog.md: se lee con parse_sections", parse_sections(_clm),
          {"0.10.0": "(sin release notes)", "0.7.6": "## Cambios\n- Dos", "0.7.5": "- Uno"})
    with tempfile.TemporaryDirectory() as _td:
        _oc = (globals()["CHANGELOG_FILE"], globals()["FILES_DIR"], RELEASES["list"])
        try:
            globals()["CHANGELOG_FILE"] = os.path.join(_td, "script", "changelog.md")
            globals()["FILES_DIR"] = os.path.join(_td, "files")
            RELEASES["list"] = None
            check("sync sin Releases: no toca nada", (sync_changelog(fetch=False), os.path.exists(globals()["CHANGELOG_FILE"])),
                  (None, False))
            check("sync escribe", sync_changelog(_rl), True)
            check("sync: archivo", read_text(globals()["CHANGELOG_FILE"]), _clm)
            check("sync: copia en dlpy_files", read_text(os.path.join(globals()["FILES_DIR"], "changelog.md")), _clm)
            check("sync: sin cambios", sync_changelog(_rl), False)
            RELEASES["list"] = _rl
            check("sync: usa los Releases ya leídos", sync_changelog(fetch=False), False)
            RELEASES["list"] = [{"ver": "0.7.6", "notes": "Nuevo", "date": ""}]
            check("sync: cambian las notas", (sync_changelog(fetch=False), parse_sections(read_text(globals()["CHANGELOG_FILE"]))),
                  (True, {"0.7.6": "Nuevo"}))
        finally:
            globals()["CHANGELOG_FILE"], globals()["FILES_DIR"], RELEASES["list"] = _oc
        _oe = (globals()["CHANGELOG_FILE"], globals()["FILES_DIR"], globals()["CHECK_FILE"], RELEASES["list"],
               NO_UPDATES["on"])
        try:
            globals()["CHANGELOG_FILE"] = os.path.join(_td, "e_script", "changelog.md")
            globals()["FILES_DIR"] = os.path.join(_td, "e_files")
            globals()["CHECK_FILE"] = os.path.join(_td, "e_checks.json")
            RELEASES["list"] = _rl
            NO_UPDATES["on"] = False
            _dest = os.path.join(globals()["FILES_DIR"], "changelog.md")
            ensure_changelog()
            check("ensure_changelog: lo genera si no existe en dlpy_files", read_text(_dest), _clm)
            os.remove(_dest)
            ensure_changelog()
            check("ensure_changelog: lo repone aunque ya se haya comprobado hoy", os.path.isfile(_dest), True)
            os.remove(_dest)
            globals()["CHANGELOG_FILE"] = os.path.join(_td, "e_none", "changelog.md")
            RELEASES["list"] = None
            NO_UPDATES["on"] = True
            ensure_changelog()
            check("ensure_changelog: con --noupdates y sin copia no inventa nada", os.path.isfile(_dest), False)
        finally:
            (globals()["CHANGELOG_FILE"], globals()["FILES_DIR"], globals()["CHECK_FILE"], RELEASES["list"],
             NO_UPDATES["on"]) = _oe
    globals()["VERSION"] = _ov_ver
    # [T15] Menú de recuperación y fallos abruptos
    check("menu vacío", parse_menu_choice("", 3), 0)
    check("menu n", parse_menu_choice(" N ", 3), 0)
    check("menu 2", parse_menu_choice("2", 3), 2)
    check("menu fuera de rango", parse_menu_choice("4", 3), None)
    check("menu texto", parse_menu_choice("hola", 3), None)
    check("abrupto versión nueva", should_offer_after_abrupt({"version": "0.7.6"}, ["0.7.5"]), True)
    check("abrupto versión buena", should_offer_after_abrupt({"version": "0.7.5"}, ["0.7.5"]), False)
    check("abrupto sin marca", should_offer_after_abrupt({}, []), False)
    with tempfile.TemporaryDirectory() as _td:
        _old_bd = globals()["BACKUP_DIR"]
        try:
            globals()["BACKUP_DIR"] = _td
            for _n, _f in (("0.7.4", "dlpy_0.7.4.py"), ("0.7.4-2", "dlpy_0.7.4.py"),
                           ("0.7.3", "otro.py"), ("junk", "dlpy_9.9.9.py")):
                os.makedirs(os.path.join(_td, _n))
                write_text(os.path.join(_td, _n, _f), "#!dlpy.py\n")
            check("backup_versions", sorted(v for v, _p in backup_versions()), ["0.7.4", "0.7.4"])
        finally:
            globals()["BACKUP_DIR"] = _old_bd
    # [T16] ── notas de la versión dentro del propio .py (solo lectura) ──
    _sc_src = "#!dlpy.py\n# ==== CHANGELOG ====\n# ## 1.0.1\n#\n# - Dos.\n#   sigue\n#\n# ==== FIN CHANGELOG ====\nx = 1\n"
    check("notas del script: la versión pedida", script_changelog_notes("1.0.1", _sc_src), "- Dos.\n  sigue")
    check("notas del script: otra versión", script_changelog_notes("9.9.9", _sc_src), None)
    check("notas del script: sin bloque", script_changelog_notes("1.0.1", "#!dlpy.py\nprint(1)\n"), None)
    check("markdown del bloque", changelog_block_md("# ## 1.0.1\n#\n# - Dos.\n#   sigue\n"), "## 1.0.1\n\n- Dos.\n  sigue")
    # [T17] ── huellas, comparación de orígenes y fallos ──
    _cl = "# ==== CHANGELOG ====\n# ## 1.0.0\n#\n# - a\n# ==== FIN CHANGELOG ====\n"
    _code = "#!dlpy.py\nVERSION = \"1.0.0\"\nprint(1)\n"
    _full = "#!dlpy.py\n" + _cl + "VERSION = \"1.0.0\"\nprint(1)\n"
    check("strip_changelog", strip_changelog(_full), _code)
    check("huella ignora CRLF", text_fingerprints(_full.replace("\n", "\r\n")), text_fingerprints(_full))
    check("huella código = sin changelog", text_fingerprints(_full)[1], text_fingerprints(_code)[1])
    check("compare igual", compare_texts(_full, _full), "igual")
    check("compare sin changelog = igual", compare_texts(_full, _code), "igual")
    check("compare código distinto", compare_texts(_full, _full.replace("print(1)", "print(2)")), "distinto")
    check("compare solo changelog", compare_texts(_full, _full.replace("# - a", "# - b")), "changelog")
    check("diff_counts", diff_counts(diff_lines("a\nb\n", "a\nc\nd\n", "x", "y")), (2, 1))
    with tempfile.TemporaryDirectory() as _td:
        # fallos: historial con huella
        _old_c = (globals()["CRASH_LOG_FILE"], globals()["CRASH_FILE"])
        try:
            globals()["CRASH_LOG_FILE"] = os.path.join(_td, "crash_log.json")
            globals()["CRASH_FILE"] = os.path.join(_td, "crash.json")
            check("sin fallos", crash_match("1.0.0", _full), None)
            record_crash("1.0.0", _full, "NameError: x", 1000)
            check("fallo idéntico", crash_match("1.0.0", _code)[0], "igual")
            check("fallo código distinto", crash_match("1.0.0", _full.replace("print(1)", "print(2)"))[0], "distinta")
            check("fallo otra versión", crash_match("1.0.1", _full), None)
            record_crash("1.0.2", None, "cierre inesperado", 1001)
            check("fallo sin huella", crash_match("1.0.2", _full)[0], "sin_huella")
            save_json(globals()["CRASH_FILE"], {"version": "0.9.0", "error": "viejo", "time": 5})
            check("fallo de crash.json", crash_match("0.9.0", _full)[0], "sin_huella")
            check("historial", [c["version"] for c in load_crashes()], ["1.0.0", "1.0.2", "0.9.0"])
            _lines = format_version_rows(
                [{"ver": "1.0.0", "src": "release", "date": "2026-10-01", "label": "Release"}],
                "1.0.0", "1.0.0", load_crashes(), 80)
            _txt = "\n".join(_lines)
            check("lista marca actual", "✓ actual" in _txt, True)
            check("lista marca actualizar", "⬆ la de actualizar" in _txt, True)
            check("lista marca crasheó", "✖ crasheó" in _txt, True)
            check("lista muestra la fecha", "2026-10-01" in _txt, True)
            check("lista de backups muestra su etiqueta",
                  "backup-2" in "\n".join(format_version_rows([{"ver": "1.0.0", "src": "backup", "label": "backup-2"}],
                                                              "0.0.1", None, [], 80)), True)
        finally:
            globals()["CRASH_LOG_FILE"], globals()["CRASH_FILE"] = _old_c
    check("tras recuperar: mismo número otro código", skip_update_after_recovery("0.7.6", "0.7.6", "distinta"), False)
    check("tras recuperar: mismo número mismo código", skip_update_after_recovery("0.7.6", "0.7.6", "igual"), True)
    check("tras recuperar: más vieja aunque distinta", skip_update_after_recovery("0.7.5", "0.7.6", "distinta"), True)
    check("tras recuperar: misma que falló", skip_update_after_recovery("0.7.6", "0.7.6"), True)
    check("tras recuperar: más vieja", skip_update_after_recovery("0.7.5", "0.7.6"), True)
    check("tras recuperar: más nueva avisa", skip_update_after_recovery("0.7.7", "0.7.6"), False)
    check("sin recuperación avisa", skip_update_after_recovery("0.7.7", None), False)
    check("downgrade: sin registro previo", version_move(None, "0.1.3"), "nueva")
    check("downgrade: igual", version_move("0.1.3", "0.1.3"), "igual")
    check("downgrade: sube", version_move("0.1.2", "0.1.3"), "sube")
    check("downgrade: baja", version_move("0.1.3", "0.1.2"), "baja")
    check("downgrade: compara números", version_move("0.9.9", "0.10.0"), "sube")
    check("downgrade: baja de mayor", version_move("1.0.0", "0.9.9"), "baja")
    check("downgrade: salto parche", downgrade_span("0.1.3", "0.1.2"), "parche")
    check("downgrade: salto menor", downgrade_span("0.2.0", "0.1.9"), "menor")
    check("downgrade: salto mayor", downgrade_span("1.0.0", "0.9.9"), "mayor")
    _pend = {"de": "0.1.3", "a": "0.1.1", "causa": "manual"}
    check("downgrade: causa pendiente", make_downgrade_record("0.1.3", "0.1.1", _pend, 5)["causa"], "manual")
    check("downgrade: pendiente de otra versión", make_downgrade_record("0.1.3", "0.1.0", _pend, 5)["causa"], "externa")
    check("downgrade: sin pendiente", make_downgrade_record("0.1.3", "0.1.1", None, 5),
          {"de": "0.1.3", "a": "0.1.1", "cuando": 5, "causa": "externa", "salto": "parche"})
    check("downgrade: causa inválida", make_downgrade_record("0.1.3", "0.1.1", dict(_pend, causa="x"), 5)["causa"], "externa")
    check("hold: pendiente a propósito", downgrade_hold("0.1.1", {"pending": _pend}), "0.1.3")
    check("hold: historial a propósito", downgrade_hold("0.1.1", {"history": [dict(_pend, causa="recuperacion")]}), "0.1.3")
    check("hold: externa no bloquea", downgrade_hold("0.1.1", {"history": [dict(_pend, causa="externa")]}), None)
    check("hold: versión distinta caduca", downgrade_hold("0.1.2", {"history": [_pend]}), None)
    check("hold: solo la última del historial", downgrade_hold("0.1.1", {"history": [_pend, {"de": "0.1.1", "a": "0.1.0", "causa": "manual"}]}), None)
    check("hold: dijo no quedarse", downgrade_hold("0.1.1", {"pending": dict(_pend, hold=False)}), None)
    check("hold: dijo no quedarse (historial)", downgrade_hold("0.1.1", {"history": [dict(_pend, hold=False)]}), None)
    check("downgrade: registro conserva hold=False", make_downgrade_record("0.1.3", "0.1.1", dict(_pend, hold=False), 5).get("hold"), False)
    check("hold: datos dañados", downgrade_hold("0.1.1", {"pending": "x", "history": [1]}), None)
    # [T18] Copiar/mover archivos, secciones y downgrade
    with tempfile.TemporaryDirectory() as _td:
        _a, _b = os.path.join(_td, "a.bin"), os.path.join(_td, "b.bin")
        with open(_a, "wb") as _f:
            _f.write(b"hola")
        copy_file(_a, _b)
        check("copy_file", open(_b, "rb").read(), b"hola")
        _c = os.path.join(_td, "c.bin")
        check("move_file ruta", move_file(_b, _c), _c)
        check("move_file borra origen", (os.path.exists(_b), open(_c, "rb").read()), (False, b"hola"))

    check("has none", has("none"), False)
    check("has avc1", has("avc1.4d401f"), True)

    f = {"format_id": "1", "ext": "mp4", "height": 720, "vcodec": None, "acodec": None}
    g = normalize_format(f)
    check("normalize no muta", f["vcodec"], None)
    check("normalize video apple", (g["vcodec"], g["acodec"], g.get("_guess")), ("avc1", "mp4a", True))
    h = normalize_format({"format_id": "2", "ext": "m4a", "vcodec": "none", "acodec": None})
    check("normalize audio", (h["vcodec"], h["acodec"]), ("none", "unknown"))

    texto = "## 0.4.4\n- a\n\n## 0.4.3\n- b\n"
    check("parse_sections", parse_sections(texto), {"0.4.4": "- a", "0.4.3": "- b"})

    check("mark_originals", mark_originals([
        {"format_id": "1", "format_note": "English (Original)"}, {"format_id": "2"}]), {"1"})

    v1 = {"format_id": "v1", "ext": "mp4", "vcodec": "avc1.4d", "acodec": "mp4a.40",
          "height": 720, "tbr": 1000}
    v2 = dict(v1, format_id="v2", height=1080, tbr=2000)
    check("auto_best video", auto_best([], [v1, v2], set(), True)[1]["format_id"], "v2")
    a1 = {"format_id": "a1", "ext": "m4a", "acodec": "mp4a.40.2", "abr": 128}
    a2 = {"format_id": "a2", "ext": "webm", "acodec": "opus", "abr": 160}
    # opus no es nativo en Apple: gana m4a
    check("auto_best audio", auto_best([a1, a2], [], set(), True), ("a", a1))

    for txt in ("unable to download video data: http error 403: forbidden",
                "requested format is not available", "http error 410: gone"):
        check("reintento sí: " + txt[:25], bool(_RETRY_RE.search(txt)), True)
    for txt in ("unable to download https://x.com/v/14032?id=4103",
                "http error 404: not found", "http error 4030"):
        check("reintento no: " + txt[:25], bool(_RETRY_RE.search(txt)), False)

    # [T19] líneas uniformes y animaciones
    check("count_text entero", count_text("48 MB", 0.5), "24 MB")
    check("count_text decimal", count_text("3.0 MB", 0.5), "1.5 MB")
    check("count_text sin número", count_text("?", 0.5), "?")
    check("count_text tope", count_text("48 MB", 3), "48 MB")
    check("título 2 líneas", len(title_lines("palabra " * 40, 30)), 2)
    check("título termina en …", title_lines("palabra " * 40, 30)[1].endswith("…"), True)
    check("título corto igual", title_lines("Hola mundo", 30), ["Hola mundo"])
    os.environ["DLPY_ROWS"] = "12"
    check("DLPY_ROWS fuerza el tope", list_cap(), 12)
    os.environ["DLPY_ROWS"] = "0"
    check("DLPY_ROWS=0 sin tope", list_cap() > 10 ** 5, True)
    check("latido: equipo 79 % ok", scale_state(0.79, "phone"), "ok")
    check("latido: equipo 80 % alerta", scale_state(0.80, "phone"), "warn")
    check("latido: equipo 92 % crítico", scale_state(0.92, "phone"), "crit")
    check("latido: DLpy 99 % alerta", scale_state(0.99, "mine"), "warn")
    check("latido: DLpy 100 % crítico", scale_state(1.0, "mine"), "crit")
    check("latido: sin dato = ok", scale_state(None, "phone"), "ok")
    check("latido: doble pulso en [0,1]", all(0 <= beat_env(i / 50, "crit") <= 1 for i in range(100)), True)
    check("latido: dos picos por periodo", beat_env(0.07, "crit") > 0.9 and beat_env(0.21, "crit") > 0.55
          and beat_env(0.5, "crit") < 0.1, True)
    check("latido: ok no late", beat_env(0.07, "ok"), 0.0)
    import collections as _col
    _U, _seen, _orig = _col.namedtuple("U", "total used free"), [], shutil.disk_usage
    shutil.disk_usage = lambda q: (_seen.append(q), _U(100, 25, 70))[1]
    try:
        _frac = disk_fraction()
    finally:
        shutil.disk_usage = _orig
    check("disco: se consulta «/» primero", _seen[:1], ["/"])
    check("disco: usado / total", _frac, 0.25)
    os.environ.pop("DLPY_ROWS", None)
    _cv = {"converted": True, "conv": {"vfrom": "vp09", "afrom": ["opus"], "engine": "x265", "secs": 9},
           "video": {"codec": "hevc", "bits": 10}}
    check("convertido ≤ 2 filas", len([1 for l, _v in conv_rows(_cv) if l in ("Convertido", "")]), 2)
    _hb = Bar()
    check("barra rápida no es lenta", _hb._slow([10.0] * 40), False)
    check("barra lenta (cae a <50 %)", _hb._slow([10.0] * 40 + [2.0] * 3), True)
    check("barra lenta sigue hasta 70 %", _hb._slow([10.0] * 40 + [6.0] * 3), True)
    check("barra recuperada", _hb._slow([10.0] * 40 + [9.0] * 3), False)
    check("barra con pocas muestras", _hb._slow([10.0, 1.0]), False)
    check("bar_str mismo ancho con aviso", dwidth(bar_str(20, 0.4, 0.0, warn=True)),
          dwidth(bar_str(20, 0.4, 0.0)))
    # [T20] ── Modo atajo ──
    check("norm_args raya larga", norm_args(["\u2014scm", "https://x.y/z?a=1", "\u2013\u2013shortcutpick", "v=1"]),
          ["--scm", "https://x.y/z?a=1", "--shortcutpick", "v=1"])
    check("norm_args no toca enlaces ni --", norm_args(["--selftest", "https://a.b", "-"]), ["--selftest", "https://a.b", "-"])
    check("parse_cli valor no es enlace", parse_cli(["--shortcutpick", "v=1,a=es", "https://a.b/c"]),
          ({"shortcutpick": "v=1,a=es"}, ["https://a.b/c"]))
    check("parse_cli scm + enlace", parse_cli(["--scm", "https://a.b/c", "--shortcutclip"]),
          ({"scm": True, "shortcutclip": True}, ["https://a.b/c"]))
    check("parse_cli =valor", parse_cli(["--shortcutpick=v=2"]), ({"shortcutpick": "v=2"}, []))
    check("wants_scm/scb", [wants_scm(["\u2014scm", "x"]), wants_scb(["--scb", "x"]), wants_scm(["scm"]), wants_scb(["--scm"]), wants_scm(["--shortcutpick", "v=1"])], [True, True, False, False, False])
    check("parse_cli --noupdates", parse_cli(["--noupdates", "https://a.b/c"]), ({"noupdates": True}, ["https://a.b/c"]))
    check("norm --noupdates raya larga", norm_args(["\u2014noupdates", "x"]), ["--noupdates", "x"])
    check("título corto: redes + frase", short_title("1.1M views · 7.6K reactions | Precision in motion: Capillary underfill "
          "dispensing. \U0001F916 #reels Mesmerizing robotics and fluid dynamics at work on the assembly line."),
          "Precision in motion: Capillary underfill dispensing")
    check("título corto: ya corto", short_title("Entrevista completa"), "Entrevista completa")
    check("título corto: largo sin punto", short_title("palabra " * 20)[-1], "…")
    check("título corto: tope", len(short_title("palabra " * 20)) <= SC_TITLE_MAX + 1, True)
    check("título corto: hashtags", short_title("Mi video #viral #fyp"), "Mi video")
    check("pick texto", parse_shortcut_pick("v=299,a=es-US,x=en-US+pt-BR"),
          {"v": "299", "a": "es-US", "x": ["en-US", "pt-BR"]})
    check("pick vacío en a y x", parse_shortcut_pick("v=137,a=,x="), {"v": "137", "a": None, "x": []})
    check("pick JSON", parse_shortcut_pick('{"v": "audio", "a": "en", "x": ["es", "fr"]}'),
          {"v": "audio", "a": "en", "x": ["es", "fr"]})
    check("pick basura", [parse_shortcut_pick(""), parse_shortcut_pick(None), parse_shortcut_pick("{mal")], [None, None, None])
    _fi = {"title": "Prueba", "id": "abc", "extractor_key": "Youtube", "duration": 3725, "formats": [
        {"format_id": "137", "ext": "mp4", "vcodec": "avc1.640028", "acodec": "none", "height": 1080, "fps": 30, "tbr": 4000},
        {"format_id": "299", "ext": "mp4", "vcodec": "avc1.64002a", "acodec": "none", "height": 1080, "fps": 60, "tbr": 6000},
        {"format_id": "248", "ext": "webm", "vcodec": "vp9", "acodec": "none", "height": 1080, "fps": 30, "tbr": 2500},
        {"format_id": "136", "ext": "mp4", "vcodec": "avc1.4d401f", "acodec": "none", "height": 720, "fps": 30, "tbr": 1500},
        {"format_id": "18", "ext": "mp4", "vcodec": "avc1.42001E", "acodec": "mp4a.40.2", "height": 360, "fps": 30, "tbr": 600},
        {"format_id": "140-0", "ext": "m4a", "vcodec": "none", "acodec": "mp4a.40.2", "abr": 129, "language": "es-US",
         "format_note": "Spanish (United States) original, medium"},
        {"format_id": "140-1", "ext": "m4a", "vcodec": "none", "acodec": "mp4a.40.2", "abr": 129, "language": "en-US",
         "format_note": "English (United States), medium"},
        {"format_id": "251-1", "ext": "webm", "vcodec": "none", "acodec": "opus", "abr": 130, "language": "en-US",
         "format_note": "English (United States), medium"}]}
    _sp = build_shortcut_payload(_fi, "https://x/y", True)
    _names = [v["name"] for v in _sp["videos"]]
    check("atajo: ok", _sp["ok"], True)
    check("atajo: status ok", _sp["status"], "ok")
    check("atajo: status error", [shortcut_error("x", "m")["status"], shortcut_error("x", "m")["ok"]], ["error", False])
    # [T21] ── Menú del atajo: formatos sin resolución, bitrate, tamaño aproximado y emojis ──
    _mf = {"duration": 30, "formats": [
        {"format_id": "1", "ext": "mp4", "vcodec": "unknown", "acodec": "unknown", "tbr": 850},
        {"format_id": "2", "ext": "mp4", "vcodec": "unknown", "acodec": "unknown", "tbr": 2100}]}
    _mp = build_shortcut_payload(_mf, "https://x/y", True)
    _ml = _mp["video_labels"]
    check("menú: sin resolución ordena por bitrate", [i["id"] for i in _mp["videos"]][:2], ["2", "1"])
    check("menú: bitrate + tamaño aprox + 🔊, sin «con audio»",
          _ml[0], "1 · ★ id2 · mp4 · 2.1 Mbps · ~7.5 MB 🔊")
    check("menú: kbps y size_est en el JSON", [_mp["videos"][1]["kbps"], _mp["videos"][1]["size_est"]], [850, "~3.0 MB"])
    check("menú: sin bitrate no hay tamaño aprox", size_estimate(None, 30), None)
    check("menú: kbps_text", [kbps_text(850), kbps_text(2100), kbps_text(None)], ["850 kbps", "2.1 Mbps", None])
    check("menú: etiquetas siguen empezando por el número", [l.split(" · ")[0] for l in _ml], ["1", "2"])
    check("menú: el JSON con emojis ida y vuelta",
          json.loads(json.dumps(_mp, ensure_ascii=True, separators=(",", ":")))["video_labels"], _ml)
    check("atajo: 1080p 60fps y 30fps, sin repetir", [_names.count("1080p 60fps"), _names.count("1080p 30fps")], [1, 1])
    check("atajo: orden mejor→peor y solo audio al final", [v["id"] for v in _sp["videos"]],
          ["299", "137", "136", "18", "audio"])
    check("atajo: listas paralelas", len(_sp["video_labels"]) == len(_sp["video_ids"]) == len(_sp["video_audio_step"]), True)
    check("atajo: etiquetas con número", [l.split(" · ")[0] for l in _sp["video_labels"]], ["1", "2", "3", "4", "5"])
    check("atajo: pasos de audio", _sp["video_audio_step"], ["full", "full", "full", "none", "track"])
    check("atajo: 2 idiomas, original primero", [_sp["multi_lang"], _sp["track_ids"], _sp["default_track"]],
          [True, ["es-US", "en-US"], 1])
    check("atajo: adicionales sin la elegida", _sp["extra_menu"], {"1": [_sp["track_labels"][1]], "2": [_sp["track_labels"][0]]})
    check("atajo: duración", _sp["duration_text"], "1:02:05")
    check("atajo: JSON ASCII de ida y vuelta", json.loads(json.dumps(_sp, ensure_ascii=True)), _sp)
    _sp2 = build_shortcut_payload(_fi, "https://x/y", False)
    check("atajo: sin ffmpeg no se pregunta audio", set(_sp2["video_audio_step"]) - {"track"}, {"none"})
    check("atajo: sin formatos", build_shortcut_payload({"formats": []}, "u", True)["error_code"], "no_formats")
    _fa, _au, _vi = split_formats(_fi)
    _tr, _ = build_tracks(_au, mark_originals(_au))
    check("atajo: resuelve video", shortcut_resolve_video({"v": "299"}, _au, _vi, _tr, set(), True)[1]["format_id"], "299")
    check("atajo: resuelve solo audio por idioma",
          shortcut_resolve_video({"v": "audio", "a": "en-US"}, _au, _vi, _tr, set(), True)[0:1], ("a",))
    check("atajo: formato que ya no existe", shortcut_resolve_video({"v": "zzz"}, _au, _vi, _tr, set(), True), None)
    _pr, _se = shortcut_tracks({"a": "en-US", "x": ["es-US", "xx", "en-US"]}, _tr, _tr[0])
    check("atajo: pistas elegidas", [_pr["lang"], [t["lang"] for t in _se]], ["en-US", ["en-US", "es-US"]])
    check("atajo: sin elección vale la original", shortcut_tracks({"a": None, "x": []}, _tr, _tr[0])[1], [_tr[0]])
    # [T22] ── Modo atajo: tope de tiempo y aviso ──
    global shortcut_copy, SC_URL_MAX
    check("tope de tiempo: devuelve timeout", collect_with_timeout("u", 0.05, lambda l: (time.sleep(0.4), {"ok": True})[1])["error_code"], "timeout")
    check("tope de tiempo: resultado a tiempo", collect_with_timeout("u", 2, lambda l: {"ok": True}), {"ok": True})
    check("tope de tiempo: fallo del análisis", collect_with_timeout("u", 2, lambda l: 1 / 0)["error_code"], "crash")
    _sent, _os_sys, _copy, _sc = [], os.system, shortcut_copy, SC_URL_MAX
    os.system = lambda c: (_sent.append(c), 0)[1]
    try:
        shortcut_copy = lambda t: True
        shortcut_send(_sp, "DLpy")
        _u = _sent[-1]
        check("scb: abre shortcuts:// hacia DLpy", _u.startswith("open 'shortcuts://run-shortcut?name=DLpy&input=text&text="), True)
        _body = json.loads(urllib.parse.unquote(_u.split("&text=")[1].rstrip("'")))
        check("scb: JSON sin videos/tracks y con el discriminador", ("videos" in _body, "tracks" in _body, _body["dlpy"]),
              (False, False, "shortcutmode"))
        check("scb: la entrada del atajo es compacta", urllib.parse.unquote(_u.split("&text=")[1]).startswith('{"dlpy":"shortcutmode"'), True)
        SC_URL_MAX = 100
        shortcut_send(_sp, "DLpy")
        check("scb: si no cabe en la URL va por el portapapeles", _sent[-1].endswith("input=clipboard'"), True)
    finally:
        os.system, shortcut_copy, SC_URL_MAX = _os_sys, _copy, _sc
    # [T23] ── Reinicio de .dlpy_internal al cambiar de versión ──
    _rt = tempfile.mkdtemp()
    try:
        _rf, _ri = os.path.join(_rt, "files"), os.path.join(_rt, "files", INTERNAL_NAME)
        for _sub, _name in (("state", "version.json"), ("script", "changelog.md"), ("work/abc", "v.part"), ("", "env.json")):
            os.makedirs(os.path.join(_ri, _sub), exist_ok=True)
            write_text(os.path.join(_ri, _sub, _name), "x")
        os.makedirs(_ri + ".old")                                   # resto de un reinicio cortado
        check("interna segura: carpeta propia", internal_dir_safe(_ri, _rf), True)
        check("interna segura: otro nombre", internal_dir_safe(os.path.join(_rf, "otra"), _rf), False)
        check("interna segura: otra ubicación", internal_dir_safe(_ri, os.path.join(_rt, "x")), False)
        _freed = reset_internal(_ri, _rf)
        check("reinicio: libera bytes", (_freed or 0) >= 4, True)
        check("reinicio: queda vacía", (os.path.isdir(_ri), os.listdir(_ri)), (True, []))
        check("reinicio: sin .old", os.path.exists(_ri + ".old"), False)
        check("reinicio: sin carpeta no falla", (shutil.rmtree(_ri), reset_internal(_ri, _rf), os.path.isdir(_ri))[1:], (0, True))
        _ro = os.path.join(_rf, "otra")
        os.makedirs(_ro)
        write_text(os.path.join(_ro, "a.txt"), "x")
        check("reinicio: no toca carpetas ajenas", (reset_internal(_ro, _rf), os.path.isfile(os.path.join(_ro, "a.txt"))), (None, True))
    finally:
        shutil.rmtree(_rt, ignore_errors=True)
    # [T24] ── Símbolos de mensaje y tarjetas (cambio de versión y resultado) ──
    _seen, _say_old = [], globals()["_say"]
    globals()["_say"] = lambda color, msg, mark=None, pulse=False: _seen.append((color, mark))
    try:
        m_ok("x"); m_warn("x"); m_err("x"); m_info("x"); m_check("x")
    finally:
        globals()["_say"] = _say_old
    check("mensajes: un símbolo por tipo", _seen,
          [("mint", "✓"), ("amber", "!"), ("red", "✕"), ("orange", None), ("mint", "✓")])
    _plain = lambda rows: [_ANSI_RE.sub("", r) for r in rows]
    _sc = static_card(["✓ Listo", "  texto"])
    _p, _w = _plain(_sc), max(30, min(safe_width(), 60))
    check("tarjeta fija: marco", (len(_p), _p[0][0], _p[0][-1], _p[-1][0], _p[-1][-1], _p[1][0], _p[1][-1]),
          (4, "╭", "╮", "╰", "╯", "│", "│"))
    check("tarjeta fija: mismo ancho en todas las líneas", {dwidth(x) for x in _p}, {_w})
    check("tarjeta final: vídeo",
          _plain(result_card_rows("Ejemplo de video largo", {"video": {"res": "1080p", "codec": "avc1.640028"}},
                                  412 * 1024 ** 2, 3725, "Ejemplo.mp4", 36)),
          ["✓ Listo", "  Ejemplo de video largo", "  1080p · H.264 · 412 MB · 1:02:05", "  dlpy_files/Ejemplo.mp4"])
    check("tarjeta final: audio convertido",
          _plain(result_card_rows("Canción", {"converted": True, "video": None, "tracks": [{"codec": "mp4a.40.2", "abr": 128}]},
                                  5 * 1024 ** 2, 215, "Canción.m4a", 36)),
          ["✓ Listo · convertido", "  Canción", "  AAC 128 kbps · 5.0 MB · 3:35", "  dlpy_files/Canción.m4a"])
    _long = _plain(result_card_rows("T " * 60, {"video": {"res": "2160p60", "codec": "vp09.00.50.08"}},
                                    9 * 1024 ** 3, 36000, "x" * 80 + ".mp4", 36))
    check("tarjeta final: nada pasa del ancho", max(dwidth(x) for x in _long) <= 36, True)
    check("tarjeta final: datos largos que sí caben", [x for x in _long if "2160p60" in x], ["  2160p60 · VP9 · 9.0 GB · 10:00:00"])
    check("tarjeta final: sin duración si no cabe",
          [x for x in _plain(result_card_rows("t", {"video": {"res": "2160p60", "codec": "vp09"}}, 9 * 1024 ** 3, 36000,
                                              "a.mp4", 30)) if "2160p60" in x], ["  2160p60 · VP9 · 9.0 GB"])
    check("tarjeta de actualización",
          _plain(update_card_rows("0.6.9", "0.7.1", None, "0.6.9", 441000, 36)),
          ["✓ Actualizada 0.6.9 → 0.7.1", "  anterior en backups/0.6.9", "  carpeta interna reiniciada"])
    check("tarjeta de bajada con fallo al reiniciar",
          _plain(update_card_rows("0.8.5", "0.7.1", {"causa": "recuperacion", "salto": "menor"}, True, None, 40)),
          ["! Bajada de versión 0.8.5 → 0.7.1", "  Recuperada tras un fallo.", "  sin copia anterior que archivar",
           "! no se pudo reiniciar .dlpy_internal"])
    check("códecs y duración", (codec_name("hvc1.1.6"), codec_name("zzz"), codec_name(None), clock_text(59), clock_text(None)),
          ("HEVC", "ZZZ", "", "0:59", ""))
    print(f"Autoprueba: {'OK' if not fails else str(len(fails)) + ' fallo(s)'}")
    return 1 if fails else 0'''


def selftest():
    """`python dlpy.py --selftest`: pruebas rápidas de funciones puras (sin disco ni red)."""
    ns = globals()
    exec(compile(SELFTEST_SRC, "dlpy.py[selftest]", "exec"), ns)
    return ns.pop("_selftest_run")()


# ─────────────── [K2] Funciones disponibles según el sistema ───────────────
def capabilities():
    """[(función, estado, motivo)] de lo que funciona en ESTE sistema, según lo que
    hay instalado. Estados: ok (funciona), no (no funciona), part (parcial), na (no
    aplica en este sistema)."""
    R = []

    def add(name, st, why):
        R.append((name, st, why))

    add("Analizar y descargar (yt-dlp)",
        "ok" if is_installed("yt_dlp") else "no",
        "yt-dlp está instalado." if is_installed("yt_dlp") else
        "Falta yt-dlp: DLpy ofrece instalarlo con pip (Python puro, no compila nada).")
    add("Unir audio y video (ffmpeg)", "ok",
        "ffmpeg viene integrado en a-Shell; DLpy no puede comprobarlo desde Python.")
    add("Convertir a formato nativo", "ok",
        "Recodifica a HEVC/AAC si el resultado no lo reproduce QuickTime/Fotos "
        "(usa VideoToolbox si ffmpeg lo trae; si no, libx265/libx264).")
    if ytdlp_needs_js():
        rt, ej = js_runtime(), is_installed("yt_dlp_ejs")
        if rt and ej:
            add("YouTube completo (runtime JS + yt-dlp-ejs)", "ok",
                f"Runtime «{rt[0]}» y yt-dlp-ejs instalados.")
        elif rt:
            add("YouTube completo (runtime JS + yt-dlp-ejs)", "part",
                f"Hay «{rt[0]}» pero falta yt-dlp-ejs: DLpy ofrece instalarlo al arrancar.")
        else:
            add("YouTube completo (runtime JS + yt-dlp-ejs)", "no",
                "Falta un runtime de JavaScript, y yt-dlp lo exige desde 2025.11.12: "
                + JS_INSTALL_HINT + ". Sin él YouTube puede mostrar menos formatos; "
                "otros sitios no se ven afectados.")
    add("Reanudar descargas cortadas", "ok", "Misma huella enlace+formato; caduca a las 24 h.")
    add("Caché de pistas (24 h)", "ok",
        "Usa enlaces duros y, si el disco no los admite (FAT/exFAT), copia el archivo.")
    add("Carpeta interna (oculta)", "ok", f"{INTERNAL_DIR} (estado, caché, script y variables DLPY_*).")
    if ENV_STATE["error"]:
        add("Variables DLPY_* recordadas", "no", f"No se guardan en {ENV_STATE['path']}: {ENV_STATE['error']}")
    elif ENV_STATE["path"]:
        add("Variables DLPY_* recordadas", "ok", f"Se guardan en {ENV_STATE['path']}.")
    add("Carpeta de descargas", "ok", f"{DOWNLOAD_DIR} (sandbox de a-Shell, visible en Archivos).")
    if clipboard_cmd():
        add("Ofrecer el enlace del portapapeles", "ok", "Con «pbpaste» (DLPY_CLIPBOARD=1).")
    else:
        add("Ofrecer el enlace del portapapeles", "na",
            "Desactivado a propósito: iOS pregunta «¿Permitir pegar?» en cada lectura. "
            "Actívalo con DLPY_CLIPBOARD=1.")
    add("Entregar el archivo al terminar", "part",
        f"Lanza tu atajo «{SHORTCUT_NAME}» con shortcuts://; si no lo creaste en Atajos, "
        "no pasa nada. Python no puede comprobarlo.")
    add("Notificación al terminar", "na", "a-Shell no puede notificar; el aviso lo da tu Atajo.")
    add("Compartir un enlace a DLpy", "part",
        "Solo mediante tu atajo de Atajos, que debe abrir a-Shell con el enlace.")
    if countdown_supported():
        add("Cuenta regresiva interactiva", "ok", "termios (modo sin eco).")
    else:
        add("Cuenta regresiva interactiva", "part",
            "La entrada no es un terminal (tubería o sin termios): se pregunta sin cuenta.")
    add("Colores y barras animadas", "ok" if (USE_COLOR and ANSI_OK) else "part",
        "ANSI activo." if (USE_COLOR and ANSI_OK) else
        "Sin colores (salida redirigida o NO_COLOR).")
    add("Ocultar el teclado", "ok", "hideKeyboard de a-Shell.")
    return R


def profile_rows():
    """[(etiqueta, milisegundos o None si no se pudo medir)]: lo que cuesta cada fase del arranque (--perfil)."""
    rows = []

    def add(label, fn):
        t0 = time.perf_counter()
        try:
            fn()
            rows.append((label, (time.perf_counter() - t0) * 1000))
        except Exception as _ign:
            ignore("profile_rows", _ign)
            rows.append((label, None))

    add("Compilar el script (en cada arranque)", lambda: compile(read_text(SCRIPT_PATH), SCRIPT_PATH, "exec"))
    rows.append(("Cargar el módulo (desde [A5])", (time.time() - START_T) * 1000))
    add("Leer el estado (version.json)", lambda: load_json(VERSION_FILE))
    add("Medir dlpy_files (barra del banner)", storage_report)
    add("Importar hashlib y difflib", lambda: (__import__("hashlib"), __import__("difflib")))
    add("Importar yt_dlp", lambda: __import__("yt_dlp"))
    return rows


def preload_ytdlp():
    """Importa yt_dlp en segundo plano (~170 ms en a-Shell) mientras se pide el enlace. Si falla no pasa nada
    aquí: el `import yt_dlp` normal de main() vuelve a intentarlo y da el error de siempre. Devuelve el hilo."""
    def _go():
        try:
            import yt_dlp  # noqa: F401
        except Exception as _ign:
            ignore("preload_ytdlp", _ign)
    t = threading.Thread(target=_go, name="dlpy-preload", daemon=True)
    t.start()
    return t


def print_profile():
    """`python dlpy.py --perfil`: cuánto tarda cada fase del arranque en ESTE equipo."""
    print(title_bar(f"DLpy v{VERSION}", paint("perfil", "gray")))
    print(rule())
    kv("Corre en", f"{platform_name()} · {machine_name()} · Python {sys.version.split()[0]}")
    rows = profile_rows()
    for label, ms in rows:
        kv(label, "no se pudo medir" if ms is None else f"{ms:.0f} ms")
    note("Cada medida es de esta ejecución (el disco y yt_dlp pueden estar ya en caché).")
    return 0


def print_capabilities():
    """`python dlpy.py --sistema`: qué funciona aquí y por qué."""
    print(title_bar(f"DLpy v{VERSION}", paint("sistema", "gray")))
    print(rule())
    kv("Corre en", f"{platform_name()} · {machine_name()} · Python {sys.version.split()[0]}")
    try:
        _env_cols = shutil.get_terminal_size((0, 0)).columns
    except Exception as _ign:
        ignore("print_capabilities", _ign)
        _env_cols = 0
    kv("Ancho", f"variable {_env_cols or '?'} · ioctl {_ioctl_cols() or '?'} · "
                f"medido {_PROBE['cols'] or '?'} · "
                f"texto {term_width()} · barras {safe_width()}")
    mark = {"ok": paint("✓", "mint"), "no": paint("✗", "red"),
            "part": paint("~", "amber"), "na": paint("–", "gray")}
    counts = {"ok": 0, "no": 0, "part": 0, "na": 0}
    for name, st, why in capabilities():
        counts[st] += 1
        print()
        print(f"{mark[st]} {paint(name, 'bold')}")
        for ln in wrap_text(why, max(20, term_width() - 3)):
            print("  " + paint(ln, "gray"))
    print()
    note(f"{counts['ok']} ✓ · {counts['part']} ~ · {counts['no']} ✗ · {counts['na']} – (no aplica)")
    return 0


# ╔══════════════════════════════════════════════════════════════════════╗
# ║ ÁREA L · PRINCIPAL — main()                                          ║
# ╚══════════════════════════════════════════════════════════════════════╝
# ───────────────────────── [L1] Principal ─────────────────────────
def main():
    # [M0a] Modos especiales: --selftest, --sistema, --2shortcuts, --scb, --scm (terminan aquí)
    sys.argv[1:] = norm_args(sys.argv[1:])      # «—scb» (raya larga del teclado) → «--scb»
    if "--selftest" in sys.argv[1:]:
        return selftest()
    if "--sistema" in sys.argv[1:]:
        return print_capabilities()
    if "--perfil" in sys.argv[1:]:
        return print_profile()
    if wants_2shortcuts(sys.argv[1:]):
        return send_code_to_shortcut()
    cli_flags, cli_args = parse_cli(sys.argv[1:])
    NO_UPDATES["on"] = bool(cli_flags.get("noupdates") or cli_flags.get("no-updates")
                            or os.environ.get("DLPY_NO_UPDATE"))
    LATE_UPDATES["on"] = cli_flags.get("shortcutpick") is not None and not NO_UPDATES["on"]
    if wants_scb(sys.argv[1:]):
        return shortcut_back(cli_flags, cli_args)         # analiza y avisa al atajo «DLpy» con el JSON
    if wants_scm(sys.argv[1:]):
        return shortcut_mode(cli_flags, cli_args)         # JSON en la salida y nada más
    spick = parse_shortcut_pick(cli_flags.get("shortcutpick"))      # lo que eligió el atajo
    input_lock()                    # iOS: entrada bloqueada hasta la primera pregunta

    # [M0b] Preparación: carpetas y límite de almacenamiento
    os.makedirs(FILES_DIR, exist_ok=True)
    drop_internal_leftovers()       # resto de un reinicio de .dlpy_internal que se cortó
    os.makedirs(INTERNAL_DIR, exist_ok=True)
    ensure_dirs()
    clear_screen()                  # banner arriba, sin restos de la ejecución anterior

    if ENV_STATE["error"]:
        m_warn(f"No se pudieron guardar las variables DLPY_* en {ENV_STATE['path']}")
        note(ENV_STATE["error"])
    check_storage()                 # antes de cualquier otro proceso
    # [M0c] Actualización del script, versión instalada y dependencias
    reexec = getattr(sys, "_dlpy_reexec", False)     # recién instalada por la anterior: ya se comprobó
    if "--actualizar" in sys.argv[1:]:
        if not reexec:
            check_update(force=True)
        if UPDATE_CHECKED["ok"] or reexec:
            check_mark("script", script_sig())
        return 0 if check_dependencies(force=True) else 1
    script_due = (not NO_UPDATES["on"] and not LATE_UPDATES["on"] and not reexec
                  and check_due("script", script_sig()))          # una vez al día
    if reexec:
        UPDATE_CHECKED["ok"] = True              # la versión anterior acaba de comprobar y la instaló
    if script_due:
        if check_update():
            return 0
    if not check_version():
        return 1
    if (script_due or reexec) and UPDATE_CHECKED["ok"]:
        check_mark("script", script_sig())
    export_crashes_json()           # .dlpy_internal/crashes_dlpy.json con las versiones que fallaron
    if not check_dependencies(updates=not (NO_UPDATES["on"] or LATE_UPDATES["on"])):
        return 1
    cleanup_internal()
    if DEBUG:
        try:
            env_cols = shutil.get_terminal_size((0, 0)).columns
        except Exception as _ign:
            ignore("main", _ign)
            env_cols = 0
        m_info(f"Ancho del terminal: variable={env_cols or '?'} · ioctl={_ioctl_cols() or '?'} · medido={_PROBE['cols'] or '?'}"
               f" · texto={term_width()} · barras={safe_width()}")
        dbg("entorno", {"python": sys.version.split()[0], "plataforma": sys.platform, "modo": PLATFORM,
                        "maquina": getattr(os.uname(), "machine", "?") if hasattr(os, "uname") else "?",
                        "script": SCRIPT_PATH, "ffmpeg": shutil.which("ffmpeg"),
                        "files": FILES_DIR, "descargas": DOWNLOAD_DIR,
                        "internal": INTERNAL_DIR, "env": dict(ENV_STATE)})

    # [M1] Enlace y análisis (1 · 1b)
    preload_ytdlp()                 # yt_dlp se carga en segundo plano mientras se pide el enlace

    # Antes de la primera pregunta: tirar Enter residual del lanzamiento por Atajos
    drain_pending_input(0.12)
    link = get_link(cli_args)
    if not link:
        m_err("Sin enlace.")
        return 1
    import yt_dlp                   # ya cargado por el hilo (o espera lo que falte)
    roast_link(link)
    warn_youtube_js(link)

    # 1) Extraer información
    bar = Bar()
    if DEBUG:
        m_info("Analizando enlace...")
    else:
        bar.start("Analizando enlace")
    try:
        info, base_opts = analyze_link(yt_dlp, link)
    except KeyboardInterrupt:
        bar.stop()
        print()
        m_err("Cancelado.")
        roast_cancel()
        return 1
    except Exception as e:
        bar.stop()
        if is_bot_error(e):
            explain_bot_error()
        else:
            m_err(f"Error al analizar: {e}")
        return 1
    bar.stop()
    if info.get("entries"):
        info = next((e for e in info["entries"] if e), info)

    try:
        save_json(LAST_FILE, {"link": link, "date": int(time.time()), "title": info.get("title") or ""})
    except Exception as _ign:
        ignore("main", _ign)

    title = info.get("title") or "video"
    key = video_key(info)
    index = load_json(INDEX_FILE)
    old_file, old_entry = lookup_downloaded(index, key)
    dbg("info", {"clave": key, "titulo": title, "id": info.get("id"),
                 "extractor": info.get("extractor_key"), "duracion": info.get("duration"),
                 "formatos": len(info.get("formats") or [])})
    dbg("ya descargado", {"archivo": old_file, "entrada": old_entry} if old_file else "no")
    roast_info(info, link, old_file)

    # 1b) Ya descargado: aquí NO se pregunta «¿Descargar de nuevo?»: se elige primero y reuse_downloaded
    # (paso 4c) pregunta solo si lo elegido es EXACTAMENTE lo que ya tienes.
    if old_file:
        dbg("ya descargado", {"archivo": old_file, "se pregunta": "después de elegir"})

    formats, audios, videos = split_formats(info)       # de peor a mejor calidad (misma lista que el atajo)
    dbg("formatos sin códec (supuestos)", [f.get("format_id") for f in formats if f.get("_guess")])

    if not audios and not videos:
        m_err("No se encontraron formatos.")
        return 1

    orig_ids = mark_originals(audios)
    tracks, orig_lang = build_tracks(audios, orig_ids)
    multi_lang = len({t["lang"] for t in tracks if t["lang"] != "und"}) > 1
    can_merge = ffmpeg_available()
    dbg("formatos", {"audio": len(audios), "video": len(videos), "ffmpeg": can_merge,
                     "ffmpeg_ruta": shutil.which("ffmpeg"), "idioma_original": orig_lang,
                     "originales": sorted(orig_ids)})
    dbg("pistas", [{"idioma": t["lang"], "format_id": t["fmt"].get("format_id"),
                    "original": t["original"], "apple": apple_audio(t["fmt"])}
                   for t in tracks])

    # [M2] 2-3) Con --shortcutpick el atajo ya eligió (resolución/fps o solo audio): se salta la lista.
    auto = ytdlp_auto_pick(info, audios, videos)         # (video, audio|None) que elegiría yt-dlp
    use_auto = False
    pre = shortcut_resolve_video(spick, audios, videos, tracks, orig_ids, can_merge, auto) if spick else None
    if pre is not None and spick and str(spick.get("v") or "").lower() == "ytdlp":
        use_auto = True
    if spick and spick.get("v") and pre is None:
        m_warn("El formato que eligió el atajo ya no está disponible: elige uno de la lista.")
    if pre is not None:
        kind, fmt = pre
        raw = "atajo"
    else:
        # 2) Listar: audio y luego video (de peor a mejor calidad). Con tope de filas según el
        #    alto del terminal: se ven las mejores y «m» muestra todas.
        a_rows = [audio_row(i, f, orig_ids) for i, f in enumerate(audios, 1)]
        v_rows = [video_row(i, f) for i, f in enumerate(videos, len(audios) + 1)]
        choices = {r["n"]: ("a", audios[i]) for i, r in enumerate(a_rows)}
        choices.update({r["n"]: ("v", videos[i]) for i, r in enumerate(v_rows)})
        bk, bf = auto_best(audios, videos, orig_ids, can_merge, quiet=True)
        best_n = next((k for k, (_kd, ff) in choices.items() if ff is bf), None)
        auto_n = None
        if auto:                                   # opción extra «yt-dlp auto» al final de la lista
            auto_n = len(audios) + len(videos) + 1
            choices[auto_n] = ("v", auto[0])
        auto_line = ("yt-dlp auto → " + video_desc(auto[0]) + (f" + {audio_desc(auto[1])}" if auto[1] else "")
                     if auto else "")
        a_flags, v_flags = ["apple", "orig"], ["apple"]
        for r in a_rows + v_rows:
            if r["n"] == best_n:
                r["flags"].add("best")
        n_head = (3 if a_rows else 0) + (2 if v_rows else 0)         # cabeceras + encabezados de columnas
        cap = list_cap(banner_height() + len(title_lines(title, term_width() - 1))
                       + len(_legend_lines(["apple", "orig"])) + n_head + (1 if auto else 0) + 1   # +1: la línea en blanco
                       + len(wrap_text("n.º · b ★ mejor · m más · q salir", term_width() - 2)) + 1)  # +1: prompt
        a_keep = best_n - 1 if bk == "a" and best_n else None
        v_keep = best_n - len(audios) - 1 if bk == "v" and best_n else None
        # lista corta: una sola fila por calidad, la mejor en soporte nativo
        a_uniq = best_per_quality(a_rows, audio_quality_keys(audios),
                                  lambda i: ("apple" in a_rows[i]["flags"], "orig" in a_rows[i]["flags"], abr_of(audios[i])),
                                  a_keep)
        v_uniq = best_per_quality(v_rows, video_quality_keys(videos),
                                  lambda i: ("apple" in v_rows[i]["flags"],
                                             videos[i].get("tbr") or 0),
                                  v_keep)
        a_pool = sum(1 for i in a_uniq if "apple" in a_rows[i]["flags"]) or len(a_uniq)   # compatibles
        v_pool = sum(1 for i in v_uniq if "apple" in v_rows[i]["flags"]) or len(v_uniq)
        a_take = min(a_pool, max(2, cap // 3))
        v_take = min(v_pool, cap - a_take)
        a_take = min(a_pool, cap - v_take)
        a_vis = short_pick(a_rows, a_take, a_keep, a_uniq)
        v_vis = short_pick(v_rows, v_take, v_keep, v_uniq)
        can_more = len(a_vis) < len(a_rows) or len(v_vis) < len(v_rows)

        def show_list(full):
            """Pantalla de la lista; devuelve True si quedan filas ocultas (se ven con «m»)."""
            if full:
                hide_keyboard(0.3)          # iOS: lista completa con el teclado abajo para poder deslizar
            clear_screen()
            if full and CARD["pin"]:
                card_thread_stop()          # lista completa: se suelta el banner anclado para poder deslizar
            show_title(title)
            legend(["apple", "orig"])
            ROW_PLAIN.clear()
            a_show = a_rows if full else [a_rows[i] for i in a_vis]
            v_show = v_rows if full else [v_rows[i] for i in v_vis]
            asx, vsx = len(a_rows) - len(a_show), len(v_rows) - len(v_show)
            if a_rows:
                header("AUDIO" + (f" · +{asx} más" if asx else ""))
                print_rows(a_show, a_flags, AUDIO_HEAD)
            if v_rows:
                header("VIDEO" + (f" · +{vsx} más" if vsx else ""), gap=False)
                rows, vhead = drop_empty_cols(v_show, VIDEO_HEAD)   # «Rango» solo si algún formato lo usa
                print_rows(rows, v_flags, vhead)
            if auto_n:
                print(paint(f"{auto_n:>3}", "orange", True) + "  " + paint(auto_line, "gray"))
            print()
            more = bool(asx or vsx)
            hint("n.º · b ★ mejor · " + ("m más · " if more else "") + "q salir")
            return more

        # 3) Elegir
        hidden = show_list(False)
        cur = PROMPT
        while True:
            try:
                typed = ask_line(cur)
                raw = typed.strip().lower()
            except (EOFError, KeyboardInterrupt):
                return 1
            if raw == "q":
                return 0
            if raw == "":
                cur = retry_prompt(cur, typed)          # Enter vacío / Enter fantasma: sin línea nueva
                continue
            if raw == "m" and hidden and can_more:
                hidden = show_list(True)
                cur = PROMPT
                continue
            if raw == "b":
                kind, fmt = auto_best(audios, videos, orig_ids, can_merge)
                flash_row(best_n)
                break
            if raw.isdecimal() and int(raw) in choices:
                kind, fmt = choices[int(raw)]
                use_auto = bool(auto_n and int(raw) == auto_n)
                if not use_auto:
                    flash_row(int(raw))
                break
            cur = retry_prompt(cur, typed, bad_prompt(f"1-{len(choices)}, b" + (", m" if hidden else "") + " o q"),
                               f"Opción inválida: escribe un número del 1 al {len(choices)}, b"
                               + (", m" if hidden else "") + " o q.")

    dbg("elegido", {"entrada": raw, "tipo": kind, "formato": pick(fmt, FMT_KEYS)})
    roast_choice(kind, fmt)

    # [M3] Resumen limpio tras la lista (evita teclado/prompt bajo decenas de filas)
    clear_screen()
    show_title(title)
    if kind == "v":
        bits = []
        bits.append(res_label(fmt) or "Video")
        if fmt.get("ext"):
            bits.append(str(fmt["ext"]))
        vc = (fmt.get("vcodec") or "?").split(".")[0]
        if fmt.get("_guess"):
            vc += "?"
        bits.append(vc)
        if range_label(fmt):
            bits.append(range_label(fmt))
        bits.append("con audio" if has(fmt.get("acodec")) else "sin audio")
        elegido = " · ".join(bits)
    else:
        bits = [str(fmt.get("ext") or "?"),
                (fmt.get("acodec") or "?").split(".")[0],
                f"{abr_of(fmt):.0f}k"]
        lang = fmt.get("language")
        if lang:
            bits.insert(0, str(lang))
        elegido = "audio · " + " · ".join(bits)

    # [M4] 4) Armar selección de pistas
    fmt_id, merge_ext = fmt["format_id"], None
    selected, audio_line = [], ""
    if kind == "v" and not has(fmt.get("acodec")):
        if not audios:
            m_warn("No hay audio disponible; se descargará solo el video.")
        elif not can_merge:
            m_warn("Este video no trae audio y no hay ffmpeg para unirlos.")
            m_info("Se descargará solo el video.")
        else:
            primary = next((t for t in tracks if t["original"]), tracks[0])
            auto_t = (next((t for t in tracks if str(t["fmt"].get("format_id")) == str(auto[1].get("format_id"))), None)
                      if use_auto and auto and auto[1] else None)
            if auto_t is not None:                 # «yt-dlp auto» lleva el audio que eligió yt-dlp, sin menús
                primary = auto_t
                selected = [primary]
            elif multi_lang and spick:
                primary, selected = shortcut_tracks(spick, tracks, primary)      # elegidas en el atajo
            elif multi_lang:
                primary, no_reply = ask_default_track(tracks, primary)
                selected = [primary] if no_reply else ask_extra_tracks(tracks, primary)
            else:
                selected = [primary]
            fmt_id = "+".join([fmt["format_id"]] + [t["fmt"]["format_id"] for t in selected])
            ok = fmt.get("ext") == "mp4" and all(
                t["fmt"].get("ext") in ("m4a", "mp4") for t in selected)
            merge_ext = "mp4" if ok else "mkv"
            audio_line = ("Audio: " + ", ".join(str(t["lang"]) for t in selected)
                          + (f" ({len(selected)} pistas)" if len(selected) > 1 else ""))
    elif kind == "v" and multi_lang:
        audio_line = "Audio: incluido; no admite pistas adicionales"

    m_block("Elegido", [elegido] + ([audio_line] if audio_line else []))

    # 4b) Si el resultado no es nativo en Apple, ofrecer convertirlo
    plan = apple_plan(kind, fmt, selected, merge_ext)
    dbg("selección", {"fmt_id": fmt_id, "merge_ext": merge_ext,
                      "pistas": [t["fmt"].get("format_id") for t in selected]})
    dbg("plan Apple", plan if plan else "no hace falta (ya es compatible)")
    if plan and use_auto:
        m_info("yt-dlp auto: se descarga tal cual, sin convertir.")
        plan = None                       # la opción de yt-dlp no pregunta ni convierte
    elif plan:
        plan = ask_apple_convert(plan, can_merge, guess_duration(info, fmt), fmt)
        dbg("conversión", "aceptada" if plan else "rechazada / no disponible")
    conv_state = {}

    # 4c) ¿Ya está descargado con estos mismos parámetros / streams? (se busca en TODO lo que bajaste de
    # este video, no solo en la última descarga; lo que sea otra elección se conserva y se descarga aparte)
    hist = history_for(key, index)
    old_file, old_entry = history_match(hist, fmt_id, conv_mode({}, plan or {}))
    if hist and not old_file:
        m_info("Ya tienes este video con otra calidad o audio: se guarda aparte.")
    if old_file and reuse_downloaded(old_file, old_entry, index, key, title, info, kind,
                                     fmt, fmt_id, selected, orig_ids, plan):
        roast_done(len(index) - 1, reused=True)
        return 0

    # [M5] 5) Nombre de archivo
    base = safe_name(title)
    if old_file:
        base = base + " (nuevo)"
    elif name_taken(base):
        suffix = f" [{re.sub(r'[^A-Za-z0-9_-]', '', str(info.get('id') or ''))[:20] or uuid.uuid4().hex[:6]}]"
        base = safe_name(base, MAX_NAME_BYTES - len(suffix.encode())) + suffix

    # Especificaciones de streams a (posible) reutilizar desde caché
    format_specs, resume_specs = [], []
    if "+" in str(fmt_id):
        for part in str(fmt_id).split("+"):
            # buscar ext del format_id en la lista de formatos
            match = next((f for f in formats if str(f.get("format_id")) == part), None)
            ext = (match.get("ext") if match else None) or "mp4"
            format_specs.append((part, ext))
            resume_specs.append((part, ext, (match or {}).get("filesize")))
    else:
        format_specs.append((str(fmt["format_id"]), fmt.get("ext") or "mp4"))
        resume_specs.append((str(fmt["format_id"]), fmt.get("ext") or "mp4", fmt.get("filesize")))

    # Trabajo temporal en internal (carpeta estable para poder reanudar);
    # el resultado final va a dlpy_files
    work_dir, base, resumed, discarded = prepare_resume_dir(resume_key(key, resume_specs), base)

    dbg("nombre / trabajo", {"base": base, "work_dir": work_dir, "specs": format_specs,
                             "reanudado": resumed})
    reused = seed_work_from_cache(work_dir, base, key, format_specs)
    start_bytes = resume_data_bytes(work_dir)
    dbg("caché de streams", {"reutilizados": reused})
    if reused:
        m_info(f"Caché de streams: {reused} archivo(s) reutilizado(s) (< 24 h)")

    ui = DownloadUI(vkey=key, resumed=bool(resumed))
    ui.total = len(format_specs)
    try:                                            # datos del archivo para el panel de descarga
        site = str(info.get("extractor_key") or info.get("extractor") or "").replace("Frontend", "")
        who = info.get("uploader") or info.get("channel")
        dur = info.get("duration")
        ui.meta_top = " · ".join([x for x in (site, str(who) if who else "", mmss(dur) if dur else "") if x])
        parts = [str(fmt.get("ext") or "")]
        if kind == "v":
            parts.append(video_desc(fmt))
            if selected:
                parts[-1] += " + " + audio_desc(selected[0]["fmt"])
        else:
            parts.append(audio_desc(fmt))
        szs = [fmt.get("filesize") or fmt.get("filesize_approx")] + [
            (t["fmt"].get("filesize") or t["fmt"].get("filesize_approx")) for t in (selected or [])]
        tot = sum(x for x in szs if x)
        if tot:
            parts.append(spaced(human_size(tot)))
        ui.meta_bot = " · ".join(x for x in parts if x)
    except Exception as _ign:
        ignore("meta panel", _ign)

    opts = {
        **base_opts,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "format": fmt_id,
        "outtmpl": os.path.join(work_dir.replace("%", "%%"), base.replace("%", "%%") + ".%(ext)s"),
        "continuedl": True,
        # False = no sobrescribir: si el intermedio ya está completo (caché), se salta
        "overwrites": False,
        "noprogress": True,
        "consoletitle": False,
        "progress_hooks": [ui.hook],
        "postprocessor_hooks": [ui.pp_hook],
    }
    if merge_ext:
        opts["merge_output_format"] = merge_ext
        opts["allow_multiple_audio_streams"] = True
    if DEBUG:
        # yt-dlp tal cual (verbose y progreso nativo), como fuera del script
        opts.update({"quiet": False, "no_warnings": False, "verbose": True,
                     "noprogress": False})
        dbg("opciones yt-dlp", {k: v for k, v in opts.items()
                                if k not in ("progress_hooks", "postprocessor_hooks")})

    # [M6] Descarga con yt-dlp (progreso, conversión y reanudación)
    clear_screen()
    hide_keyboard()
    m_info(f"Archivo: {base}")
    if resumed:
        m_ok(f"Reanudando: {human_size(resumed)} ya descargados")
    elif discarded:
        m_warn("Parcial descartado tras fallos repetidos; se empieza de cero.")
    ui.begin()
    final = None
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            if merge_ext and selected:
                ydl.add_post_processor(
                    make_track_pp([track_label(t) for t in selected], ui.bar),
                    when="post_process")
            if plan:
                ydl.add_post_processor(make_apple_pp(plan, conv_state, ui.bar),
                                       when="post_process")
            res = run_download(ydl, yt_dlp, info, link, fmt_id)
            rd = (res.get("requested_downloads") or [{}])[0]
            final = rd.get("filepath") or ydl.prepare_filename(res)
            if conv_state.get("path"):
                final = conv_state["path"]
            dbg("resultado yt-dlp", {"final": final, "convertido": conv_state or None,
                                     "descargas": [pick(x, ("filepath", "format_id", "ext",
                                                            "vcodec", "acodec"))
                                                   for x in (res.get("requested_downloads") or [])]})
    except KeyboardInterrupt:
        ui.abort()
        saved = keep_for_resume(work_dir, start_bytes, failed=False)
        m_err("Descarga cancelada.")
        if saved:
            m_info(f"Avance guardado ({human_size(saved)}): repite el mismo enlace y formato para reanudar.")
        roast_cancel()
        return 1
    except Exception as e:
        ui.abort()
        saved = keep_for_resume(work_dir, start_bytes, failed=True)
        m_err(f"Error al descargar: {e}")
        if saved:
            m_info(f"Avance guardado ({human_size(saved)}): al repetirlo se reanuda solo.")
        return 1
    ui.finish()
    if conv_state.get("path"):
        convert_done(plan, conv_state.get("vcodec"))

    if not final or not os.path.exists(final):
        cleanup_work(work_dir)
        m_err("No se encontró el archivo descargado.")
        return 1

    # [M7] Mover el resultado terminado a dlpy_files (solo procesos completados)
    dest_name = os.path.basename(final)
    dest_path = os.path.join(DOWNLOAD_DIR, dest_name)
    if os.path.abspath(final) != os.path.abspath(dest_path):
        try:
            if os.path.exists(dest_path):
                root, ext = os.path.splitext(dest_path)       # «video-2.mp4», no «video.mp4-2» (sin extensión no abre)
                n = 2
                while os.path.exists(f"{root}-{n}{ext}"):
                    n += 1
                dest_path = f"{root}-{n}{ext}"
            move_file(final, dest_path)
            final = dest_path
        except Exception as e:
            cleanup_work(work_dir)
            m_err(f"No se pudo guardar el archivo en {DOWNLOAD_DIR}: {e}")
            return 1

    cleanup_work(work_dir)
    dbg("movido a", final)

    # Reemplazar el archivo anterior y quitar el sufijo temporal
    if old_file and os.path.abspath(old_file) != os.path.abspath(final):
        try:
            os.remove(old_file)
        except OSError as _ign:
            ignore("main", _ign)
        _root, _ext = os.path.splitext(os.path.basename(final))      # solo el sufijo final del nombre, no el título
        clean = os.path.join(os.path.dirname(final), re.sub(r" \(nuevo\)(?=(?:-\d+)?$)", "", _root) + _ext)
        if clean != final and not os.path.exists(clean):
            os.replace(final, clean)
            final = clean

    # [M8] 6) Registrar (con datos técnicos) y enviar
    index = load_json(INDEX_FILE)         # se relee: durante la descarga el índice pudo cambiar (otra ejecución)
    index[key] = {"file": os.path.basename(final), "title": title,
                  "date": int(time.time()), "version": VERSION,
                  "meta": build_meta(kind, fmt, fmt_id, selected, orig_ids, final,
                                    conv_state or None, info)}
    dbg("índice", index[key])
    try:
        save_json(INDEX_FILE, index)
    except Exception as e:
        m_warn(f"No se pudo guardar el índice: {e}")
    history_add(key, index[key])          # downloads.json guarda cada descarga, no solo la última

    result_card(final, title, index[key]["meta"], info.get("duration"))
    roast_done(len(index) - 1)
    deliver(final, title)
    return 0


if __name__ == "__main__":
    sys.exit(run_guarded(main))
