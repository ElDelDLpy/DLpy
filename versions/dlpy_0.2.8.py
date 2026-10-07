#!dlpy.py - siempre empezar el script con este mismo comentario.
# Cada edicion de este archivo sube la version: x.y.z donde Y y Z solo llegan hasta el 9 y X no tiene limites.
# Cada edicion mete el changelog en el py.
# Conservar en todo momento los comentarios anteriores en el mismo orden sin importar las ediciones realizadas.
# DLpy - descargador para a-Shell mini basado en yt-dlp
# Uso: python dlpy.py [LINK]
#   Sin LINK: ofrece usar el último enlace.
#   --selftest: ejecuta pruebas rápidas de funciones puras y sale.
#   --sistema: muestra en qué corre y qué funciones están disponibles (y por qué).
#   --actualizar: busca ahora una versión nueva en GitHub (ver 0.0.1) y sale.
#   --2shortcuts: (iOS) manda este dlpy.py tal cual a tu atajo «DLpy» y sale (ver 0.0.1).
#     (desde 0.0.1 también revisa las dependencias y vuelve a preguntar lo rechazado.)
#   --versiones: lista las versiones guardadas en versions/ de GitHub y deja instalar una (0.0.1).
#   DLPY_TRUECOLOR=0: colores básicos; DLPY_ANIM=0: sin animación; DLPY_CLASSIC=1: barra «█░» (0.2.3).
#   DLPY_DEV=1: muestra «DEV» en el banner y, en a-Shell, copia el snapshot a ~/Documents/dlpy_<versión>.py (0.0.1).
#   DLPY_WIDTH=N: fuerza el ancho en columnas; DLPY_PROBE=0 apaga la medición del ancho (0.0.4).
#   DLPY_PROBE=1: activa la medición del ancho (desde 0.0.5 viene apagada: congelaba a-Shell).
#   DLPY_CHECK_HOURS=N: cada cuántas horas busca actualizaciones (24 por omisión; 0 = en cada arranque) (0.2.7).
#   DLPY_SETTLE=0: sin la pausa inicial de 0,25 s al abrir desde Atajos en iOS (0.2.7).
# Corre en iOS (a-Shell), Android (Termux), Linux, macOS y Windows (ver 0.0.1).

VERSION = "0.2.8"

# Índice de secciones (cada una empieza con una cabecera «# ──── Título ────»; busca el título):
#   Plataforma · Rutas · Compatibilidad nativa Apple · Interfaz (estilo Aurora) · Terminal: ancho y texto ·
#   Mensajes y debug · Comentarios inteligentes · Pantalla: banner, títulos y listas · Barras y paneles de
#   progreso · Terminal: teclado y cuenta regresiva · Utilidades · Formatos y pistas · Post-proceso ·
#   Compatibilidad Apple: conversión · Bits, HDR y sondeo · Ya descargado · JSON / índice · Enlace y
#   portapapeles · Dependencias · Actualizaciones desde GitHub · YouTube: runtime de JavaScript ·
#   Dependencias del sistema · Changelog y backup · Limpieza de almacenamiento · Control de versión ·
#   DEV · Versiones en GitHub y en backups · Comparar versiones · Fallos · Pantalla de versiones ·
#   Recuperación tras un fallo · Caché de streams · Reanudación de descargas · Limpieza interna ·
#   Entrega del archivo · Atajo de iOS · Análisis tolerante · Error «no eres un bot» · Autoprueba ·
#   Funciones disponibles según el sistema · Principal

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
import textwrap
import threading
import unicodedata
import urllib.parse

# ─────────────────────── Plataforma ───────────────────────
PLATFORMS = ("ios", "android", "macos", "linux", "windows")


def detect_platform(env=None, plat=None):
    """Modo de ejecución: «ios» (a-Shell), «android» (Termux), «macos», «linux» o
    «windows». BSD y otros Unix usan el modo «linux». env/plat solo se inyectan en
    las pruebas; DLPY_PLATFORM=<modo> fuerza uno."""
    real = env is None
    env = os.environ if env is None else env
    forced = (env.get("DLPY_PLATFORM") or "").strip().lower()
    if forced in PLATFORMS:
        return forced
    plat = (sys.platform if plat is None else plat) or ""
    home = env.get("HOME") or ""
    if (env.get("TERMUX_VERSION") or "com.termux" in (env.get("PREFIX") or "")
            or "com.termux" in home or plat.startswith("android")
            or (real and hasattr(sys, "getandroidapilevel"))):
        return "android"
    if plat.startswith(("ios", "ipados")):
        return "ios"
    if plat == "darwin":
        # a-Shell corre en un Python «darwin»: se distingue por su entorno y su sandbox
        machine = ""
        if real and hasattr(os, "uname"):
            machine = os.uname().machine.lower()
        if ("a-shell" in (env.get("APPNAME") or "").lower()
                or "/var/mobile/" in home or "/containers/data/application/" in home.lower()
                or machine.startswith(("iphone", "ipad"))
                or (real and shutil.which("hideKeyboard"))):
            return "ios"
        return "macos"
    if plat.startswith(("win", "cygwin", "msys")):
        return "windows"
    return "linux"


def is_wsl(env=None):
    """Linux dentro de Windows (WSL). Con env inyectado solo mira WSL_DISTRO_NAME."""
    real = env is None
    env = os.environ if env is None else env
    if env.get("WSL_DISTRO_NAME") or env.get("WSL_INTEROP"):
        return True
    if real and sys.platform.startswith("linux"):
        try:
            with open("/proc/version", "r", encoding="utf-8", errors="ignore") as fh:
                return "microsoft" in fh.read().lower()
        except OSError:
            return False
    return False


def platform_name(mode=None, env=None):
    """Texto corto para el banner: en qué sistema corre DLpy."""
    real = env is None
    env = os.environ if env is None else env
    mode = mode or PLATFORM
    try:
        if mode == "ios":
            app = (env.get("APPNAME") or "").lower()
            return ("a-Shell mini" if "mini" in app else "a-Shell") + " · iOS"
        if mode == "android":
            ver = env.get("TERMUX_VERSION")
            return ("Termux " + ver if ver else "Termux") + " · Android"
        if mode == "macos":
            import platform as _pl
            ver = _pl.mac_ver()[0].split(".")[0] if real else ""
            return "macOS" + (" " + ver if ver else "")
        if mode == "windows":
            build = getattr(sys, "getwindowsversion", lambda: None)() if real else None
            n = "11" if build is not None and build.build >= 22000 else \
                ("10" if build is not None else "")
            return "Windows" + (" " + n if n else "")
        name = "Linux"
        if is_wsl(env):
            name += " · WSL"
        distro = env.get("WSL_DISTRO_NAME") or ""
        if real and not distro:
            try:
                with open("/etc/os-release", "r", encoding="utf-8", errors="ignore") as fh:
                    m = re.search(r'(?m)^NAME="?([^"\n]+)"?', fh.read())
                distro = m.group(1) if m else ""
            except OSError:
                distro = ""
        if sys.platform.startswith(("freebsd", "openbsd", "netbsd", "dragonfly")) and real:
            name = sys.platform.rstrip("0123456789").capitalize()
        return name + (" · " + distro if distro else "")
    except Exception:
        return mode


def machine_name():
    try:
        import platform as _pl
        return _pl.machine() or "?"
    except Exception:
        return "?"


PLATFORM = detect_platform()
IS_ANDROID = PLATFORM == "android"
IS_IOS = PLATFORM == "ios"
IS_MAC = PLATFORM == "macos"
IS_LINUX = PLATFORM == "linux"
IS_WINDOWS = PLATFORM == "windows"
IS_DESKTOP = PLATFORM in ("macos", "linux", "windows")
APPLE_MODE = PLATFORM in ("ios", "macos")     # códecs nativos de Apple + conversión opcional
PLAT_LABEL = {"ios": "Apple", "macos": "Apple", "android": "Android",
              "linux": "Linux", "windows": "Windows"}[PLATFORM]


def enable_windows_ansi():
    """Windows: activa las secuencias ANSI de la consola (colores, barras). Fuera
    de Windows no hace nada. Devuelve False si la consola no las admite."""
    if os.name != "nt":
        return True
    try:
        import ctypes
        k32 = ctypes.windll.kernel32
        ok = True
        for std in (-11, -12):                         # stdout, stderr
            h = k32.GetStdHandle(std)
            mode = ctypes.c_uint32()
            if k32.GetConsoleMode(h, ctypes.byref(mode)):
                ok = bool(k32.SetConsoleMode(h, mode.value | 0x0004)) and ok
        return ok
    except Exception:
        return False


def force_utf8_output():
    """Barras, puntos y flechas son Unicode: evita UnicodeEncodeError en consolas
    cp1252 (Windows) o con locale C."""
    for stream in (sys.stdout, sys.stderr):
        try:
            enc = (getattr(stream, "encoding", "") or "").lower().replace("-", "")
            if enc != "utf8":
                stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


ANSI_OK = enable_windows_ansi()
force_utf8_output()


def desktop_downloads_dir(mode=None, env=None, home=None):
    """Carpeta Descargas del escritorio: XDG en Linux (XDG_DOWNLOAD_DIR o
    user-dirs.dirs), carpeta conocida de Windows y ~/Downloads en el resto."""
    mode = mode or PLATFORM
    real = env is None
    env = os.environ if env is None else env
    home = home or os.path.expanduser("~")
    custom = env.get("XDG_DOWNLOAD_DIR")
    if mode == "linux":
        if custom:
            return custom
        cfg = os.path.join(env.get("XDG_CONFIG_HOME") or os.path.join(home, ".config"),
                           "user-dirs.dirs")
        try:
            with open(cfg, "r", encoding="utf-8", errors="ignore") as fh:
                m = re.search(r'(?m)^XDG_DOWNLOAD_DIR=(?:"([^"\n]*)"|(\S+))', fh.read())
            if m:
                path = (m.group(1) or m.group(2)).replace("$HOME", home)
                if path and os.path.abspath(path) != os.path.abspath(home):
                    return path
        except OSError:
            pass
    elif mode == "windows" and real and os.name == "nt":
        try:
            import winreg
            key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
                path, _ = winreg.QueryValueEx(k, "{374DE290-123F-4565-9164-ACA4A8AF4A5B}")
            path = os.path.expandvars(path)
            if path and "%" not in path:
                return path
        except (OSError, ImportError):
            pass
    return os.path.join(home, "Downloads")


def copy_file(src, dst):
    """Como shutil.copy2, pero el chmod/utime del destino es opcional: el
    almacenamiento compartido de Android los rechaza (EPERM)."""
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


def _writable_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
        return os.access(path, os.W_OK)
    except OSError:
        return False


def _early_say(color, msg):
    """Mensaje con el mismo punto de color que m_info/m_ok/m_warn, para usar antes de que
    existan los ayudantes de la interfaz (se llama al importar, en Android)."""
    env = os.environ.get("DLPY_COLOR")
    on = (env.strip().lower() not in ("0", "no", "false", "") if env is not None
          else sys.stdout.isatty() and not os.environ.get("NO_COLOR") and ANSI_OK)
    tc = os.environ.get("DLPY_TRUECOLOR", "1").strip().lower() not in ("0", "no", "false", "")
    rgb = {"green": (61, 220, 151), "yellow": (255, 196, 61), "blue": (255, 138, 61)}[color]
    code = f"38;2;{rgb[0]};{rgb[1]};{rgb[2]}" if tc else {"green": "92", "yellow": "93", "blue": "93"}[color]
    print((f"\x1b[{code}m●\x1b[0m" if on else "●") + " " + msg)


def ensure_storage_access(shared_root, download_dir):
    """Android: pide el permiso de almacenamiento con termux-setup-storage (solo una
    vez si se rechaza) y espera a que aparezca ~/storage/shared. Usa print porque
    corre antes de definir la interfaz. Devuelve True si Descargas quedó escribible."""
    import subprocess
    def ok():
        return os.path.isdir(shared_root) and _writable_dir(download_dir)
    marker = os.path.join(HOME, ".dlpy", "storage_asked")
    if ok():
        try:
            os.remove(marker)
        except OSError:
            pass
        return True
    if (os.environ.get("DLPY_NO_STORAGE_SETUP") or "--selftest" in sys.argv[1:]
            or os.path.exists(marker) or not shutil.which("termux-setup-storage")):
        return False
    try:
        os.makedirs(os.path.dirname(marker), exist_ok=True)
        with open(marker, "w") as f:
            f.write(str(int(time.time())))
    except OSError:
        pass
    _early_say("blue", "DLpy necesita acceso al almacenamiento: acepta el permiso de Android...")
    try:
        subprocess.run(["termux-setup-storage"], stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
    except (OSError, subprocess.SubprocessError):
        pass
    end = time.time() + 45
    while time.time() < end:
        if ok():
            try:
                os.remove(marker)
            except OSError:
                pass
            _early_say("green", "Acceso concedido.")
            return True
        time.sleep(0.5)
    _early_say("yellow", "No se concedió el acceso al almacenamiento; se usará ~/dlpy_files.")
    return False


# ───────────────────────── Rutas ─────────────────────────
HOME = os.path.expanduser("~")
SHARED_OK = True                  # Android: ¿hay almacenamiento compartido?
if IS_ANDROID:
    # Completadas + backups: Descargas/DLpy (visible en la galería y otras apps)
    _shared_root = os.path.join(HOME, "storage", "shared")   # lo crea termux-setup-storage
    if not os.environ.get("DLPY_DOWNLOAD_DIR") and not os.environ.get("DLPY_FILES_DIR"):
        ensure_storage_access(_shared_root, os.path.join(_shared_root, "Download"))
    # Descargas terminadas: la carpeta Descargas de Android. Lo demás de DLpy
    # (backups, changelog) va en Descargas/DLpy para no mezclarlo con tus archivos.
    DOWNLOAD_DIR = os.environ.get("DLPY_DOWNLOAD_DIR") or os.path.join(_shared_root, "Download")
    FILES_DIR = os.environ.get("DLPY_FILES_DIR") or os.path.join(DOWNLOAD_DIR, "DLpy")
    _custom = os.environ.get("DLPY_DOWNLOAD_DIR") or os.environ.get("DLPY_FILES_DIR")
    if (not _custom and not os.path.isdir(_shared_root)) \
            or not _writable_dir(DOWNLOAD_DIR) or not _writable_dir(FILES_DIR):
        SHARED_OK = False
        FILES_DIR = DOWNLOAD_DIR = os.path.join(HOME, "dlpy_files")
    OLD_DATA_DIR = os.path.join(HOME, ".dlpy", "sin_legado")      # no hay legado en Android
    SHORTCUTS_DIR = os.environ.get("DLPY_HOME") or os.path.join(HOME, ".dlpy")
elif IS_DESKTOP:
    # Linux / macOS / Windows: como Android. Descargas terminadas en la carpeta
    # Descargas del sistema; backups y changelog en Descargas/DLpy.
    DOWNLOAD_DIR = os.environ.get("DLPY_DOWNLOAD_DIR") or desktop_downloads_dir(PLATFORM, None, HOME)
    FILES_DIR = os.environ.get("DLPY_FILES_DIR") or os.path.join(DOWNLOAD_DIR, "DLpy")
    _probe = "--selftest" not in sys.argv[1:] and "--sistema" not in sys.argv[1:]
    if _probe and (not _writable_dir(DOWNLOAD_DIR) or not _writable_dir(FILES_DIR)):
        SHARED_OK = False
        FILES_DIR = DOWNLOAD_DIR = os.path.join(HOME, "dlpy_files")
    OLD_DATA_DIR = os.path.join(HOME, ".dlpy", "sin_legado")      # no hay legado en escritorio
    SHORTCUTS_DIR = os.environ.get("DLPY_HOME") or os.path.join(HOME, ".dlpy")
else:
    # Completadas + backups únicamente
    FILES_DIR = os.path.join(HOME, "Documents", "dlpy_files")
    DOWNLOAD_DIR = FILES_DIR      # iOS: las descargas terminadas viven en dlpy_files
    OLD_DATA_DIR = os.path.join(HOME, "Documents", "dlpy_data")  # legado → migrar
    SHORTCUTS_DIR = os.environ.get("SHORTCUTS") or os.path.join(HOME, "Library", "Shortcuts")
# Índice, estado, caché, trabajo temporal, changelog
INTERNAL_DIR = os.path.join(SHORTCUTS_DIR, "dlpy_internal")
# dlpy_internal/: state/ (estado), script/ (copia y changelog), cache/streams/,
# work/ (descargas en curso) y delivery/<id>/ (copias de entrega al atajo)
STATE_DIR = os.path.join(INTERNAL_DIR, "state")
SCRIPT_DIR = os.path.join(INTERNAL_DIR, "script")
CACHE_DIR = os.path.join(INTERNAL_DIR, "cache")
INDEX_FILE = os.path.join(STATE_DIR, "index.json")
LAST_FILE = os.path.join(STATE_DIR, "last_link.json")
VERSION_FILE = os.path.join(STATE_DIR, "version.json")
DOWNGRADE_FILE = os.path.join(STATE_DIR, "downgrades.json")   # bajadas de versión (historial y pendiente)
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

# Bloque del changelog dentro del .py (tolerante con espacios, mayúsculas y CRLF)
CL_RE = re.compile(r"(?m)^#[ \t]*={3,}[ \t]*CHANGELOG[ \t]*={3,}[ \t]*\r?\n(.*?)"
                   r"^#[ \t]*={3,}[ \t]*FIN[ \t]+CHANGELOG[ \t]*={3,}[ \t]*(?:\r?\n|\Z)",
                   re.S | re.I)
CL_OPEN_RE = re.compile(r"(?m)^#[ \t]*={3,}[ \t]*CHANGELOG[ \t]*={3,}[ \t]*$", re.I)

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

# ─────────────── Compatibilidad nativa Apple ───────────────
APPLE_VCODEC = ("avc1", "h264", "hvc1", "hev1", "hevc")
APPLE_ACODEC = ("mp4a", "aac", "alac", "mp3", "ac-3", "ec-3", "ac3", "eac3", "flac")
APPLE_VEXT = ("mp4", "m4v", "mov")
APPLE_AEXT = ("m4a", "mp4", "mp3", "aac", "wav", "aiff", "caf", "flac")
GUESS_VEXT = APPLE_VEXT      # contenedores donde se asume avc1/mp4a si yt-dlp no da códecs
if not APPLE_MODE:
    # En Android, Linux y Windows «compatible» = reproducible de forma nativa (sin AV1: depende del chip)
    APPLE_VCODEC = ("avc1", "h264", "vp9", "vp09", "hvc1", "hev1", "hevc")
    APPLE_ACODEC = ("mp4a", "aac", "opus", "vorbis", "mp3", "flac")
    APPLE_VEXT = ("mp4", "m4v", "webm", "mkv", "3gp")
    APPLE_AEXT = ("m4a", "mp4", "mp3", "aac", "opus", "ogg", "webm", "flac", "wav", "mka")


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


# ───────────────────────── Interfaz ─────────────────────────
WAIT_SECONDS = 10
PHANTOM_SECS = 0.4        # un Enter vacío antes de este tiempo se considera fantasma
PHANTOM_BOOT = 3.0        # ... y también en los primeros segundos de la ejecución (0.2.8)
START_T = time.time()
DEBUG = os.environ.get("DLPY_DEBUG", "").strip().lower() not in ("", "0", "no", "false")
# DLPY_DEV=1: modo desarrollo (en a-Shell copia el snapshot a ~/Documents/dlpy_<versión>.py y lo muestra en el banner)
DEV = os.environ.get("DLPY_DEV", "").strip().lower() not in ("", "0", "no", "false")
_env_color = os.environ.get("DLPY_COLOR")
if _env_color is not None:
    USE_COLOR = _env_color.strip().lower() not in ("0", "no", "false", "")
else:
    USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR") and ANSI_OK
CLR = "\r\x1b[2K" if sys.stdout.isatty() and ANSI_OK else "\r"
# Secuencia de clear_screen (DLPY_CLEAR=1..4; por defecto 3, ver changelog 0.0.1)
CLEAR_SEQS = {"1": "\x1b[3J\x1b[2J\x1b[H", "2": "\x1b[2J\x1b[3J\x1b[H",
              "3": "\x1bc", "4": "\x1b[2J\x1b[H"}
CLEAR_SEQ = CLEAR_SEQS.get(os.environ.get("DLPY_CLEAR", "3").strip(), CLEAR_SEQS["3"])

# ── Estilo «Aurora» (el mismo de dlpy_test_panel.py) ──
# DLPY_TRUECOLOR=0: colores básicos · DLPY_ANIM=0: sin animación · DLPY_CLASSIC=1: barra «█░»
def _flag_env(name, default=True):
    v = os.environ.get(name)
    return default if v is None else v.strip().lower() not in ("0", "no", "false", "")


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
ANIM_LIVE = ANIM and ANSI_OK        # animaciones que redibujan en su sitio (0.2.4)


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
    """«89 MB» al 40 % → «36 MB»: escala el número y conserva decimales y unidad (0.2.4).
    Si el texto no es «número unidad» lo devuelve igual."""
    m = _NUM_UNIT_RE.match(str(text).strip())
    if not m:
        return text
    num, sp, unit = m.groups()
    dec = len(num.split(".")[1]) if "." in num else 0
    return f"{float(num) * max(0.0, min(1.0, frac)):.{dec}f}{sp}{unit}"


# ───────────────────── Terminal: ancho y texto ─────────────────────
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
    if os.name == "nt" or flag != "1":        # desde 0.0.5 solo con DLPY_PROBE=1
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
    salte de línea solo). Sin medición fiable se limita (iOS 40, Android 60);
    DLPY_WIDTH=N lo fuerza."""
    forced = _forced_width()
    if forced:
        return forced
    cols, measured = _cols()
    w = cols - 1
    if not measured:
        cap = 60 if IS_ANDROID else 40 if IS_IOS else 110
        if IS_IOS:
            ic = _ioctl_cols()
            if ic:
                w, cap = ic - 1, 110          # el terminal sabe su ancho: se usa entero
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


def plat_text(s):
    """Adapta los textos con iPhone / a-Shell fuera de iOS."""
    s = str(s)
    if IS_ANDROID:
        s = s.replace("a-Shell", "Termux").replace("iPhone", "teléfono")
    elif IS_DESKTOP:
        s = s.replace("a-Shell", "la terminal").replace("iPhone", "equipo")
    return s


_LAST_PULSE = [0.0]


# ───────────────────── Mensajes y debug ─────────────────────
def _pulse_line(color, text, mark=None):
    """El punto del aviso late dos veces (0.3 s) y luego queda fijo. Una ráfaga de avisos
    seguidos no se retrasa: solo late el primero de cada segundo (0.2.4)."""
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
    lines = wrap_text(plat_text(msg), term_width() - 2)
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
    _say("mint", msg)


def m_check(msg):
    """Línea de revisión superada: «✓ nombre versión · estado» (verde)."""
    _say("mint", msg, "✓")


def m_warn(msg):
    _say("amber", msg, pulse=True)


def m_info(msg):
    _say("orange", msg)


def m_err(msg):
    _say("red", msg, pulse=True)


def note(text):
    """Texto de apoyo en gris, sangrado 2 columnas (como los subtítulos de dpt)."""
    for ln in wrap_text(plat_text(text), term_width() - 2):
        print("  " + paint(ln, "gray"))


def hint(text):
    """Ayuda de un prompt: «▸ texto» (flecha naranja, texto gris)."""
    lines = wrap_text(plat_text(text), term_width() - 2)
    print(paint("▸", "orange") + " " + paint(lines[0], "gray"))
    for ln in lines[1:]:
        print("  " + paint(ln, "gray"))


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


# ─────────── Comentarios inteligentes (humor según el uso) ───────────
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
        lines = wrap_text(plat_text(text), term_width() - 2)
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


# ───────────────────── Pantalla: banner, títulos y listas ─────────────────────
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
    """Fracción usada del almacenamiento del equipo (0–1) o None si no se puede leer (0.2.6).
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
BEAT_WARN, BEAT_CRIT_PHONE, BEAT_CRIT_MINE = 0.80, 0.92, 1.0     # umbrales del latido (0.2.6)
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
    """Una línea con dos escalas: «▀» arriba = equipo (texto), abajo = DLpy (fondo) (0.2.6).
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
    """La fila de la barra con sus etiquetas, para el instante t (None = fija) (0.2.6)."""
    b = CARD["bar"]
    return ("  " + tint_text(b["left"], scale_state(b["phone"], "phone"), t)
            + card_bar(b["n"], b["phone"], b["mine"], t)
            + tint_text(b["right"], scale_state(b["mine"], "mine"), t))


def card_rows(inner):
    """Filas del interior de la tarjeta, cada una de `inner` columnas exactas (0.2.6)."""
    dev = "DEV · " if DEV else ""
    state = (paint(dev + "DEBUG ACTIVO", "amber", True) if DEBUG else paint(dev + "debug off", "gray"))
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
    left = f"{plat_text('iPhone')} {phone * 100:.0f}% " if phone is not None else ""
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
    destello que lo recorre entero. t = segundos (None = fija); env 1→0 apaga el destello (0.2.6).
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


BANNER_LAP = 2.5          # segundos que tarda el destello en dar la vuelta al borde al arrancar (0.2.6)
CARD_LAP = 5.0            # ídem mientras se descarga (0.2.6)
_BANNER_INTRO = [True]    # el destello de arranque solo se ve en el primer banner de la ejecución
# Estado de la tarjeta: w/body = último contenido calculado (se reutiliza en cada cuadro);
# fresh = la tarjeta acaba de pintarse arriba del todo; live = el panel de descarga la anima.
CARD = {"w": None, "body": None, "fresh": False, "live": False, "t0": 0.0}
# TEST (0.2.6): hilo propio de la tarjeta. DLPY_CARDLIVE=0 lo apaga (queda lo de antes).
CARD_THREAD = _flag_env("DLPY_CARDLIVE", True)
CARD.update({"bar": None, "run": False, "th": None, "head": 0.0, "row": 0, "rows": 24, "rows_t": 0.0, "settled": False,
             "pin": False, "pin_rows": 0})
CARD_PIN = _flag_env("DLPY_CARDPIN", True)      # ancla la tarjeta con una región de desplazamiento


def card_paint(t=None, env=1.0, lap=None, head=None):
    """Repinta la tarjeta en las filas 1 a 5 sin mover el cursor (guardar/restaurar) (0.2.6)."""
    lines = card_lines(t, env, lap, cached=True, head=head)
    seq = "\x1b7" + "".join(f"\x1b[{i + 1};1H{ln}" for i, ln in enumerate(lines)) + "\x1b8"
    sys.stdout.write("\x1b[?7l" + seq + "\x1b[?7h")
    sys.stdout.flush()


class _RowCounter:
    """Envoltura de sys.stdout que solo cuenta: saltos de línea y subidas de cursor desde el último
    clear_screen, para saber en qué fila está el cursor y no pintar la tarjeta si se desplazó (0.2.6).
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
    """Ancla la tarjeta: región de desplazamiento de la fila h+1 a la última (0.2.6).
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
    """Arranca (o reanuda con el contenido nuevo) el hilo que anima la tarjeta (0.2.6, test)."""
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
    """Al salir: para el hilo y deja la tarjeta fija (0.2.6)."""
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
    """Activa la animación de la tarjeta durante la descarga si es seguro (0.2.6)."""
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
    """Un cuadro de la tarjeta viva; ante cualquier error la deja fija (0.2.6)."""
    if not CARD["live"]:
        return
    try:
        card_paint(time.time() - CARD["t0"], 1.0, CARD_LAP)
    except Exception as _ign:
        CARD["live"] = False
        ignore("card_tick", _ign)


def card_settle():
    """Termina la animación: el destello se apaga en medio segundo y la tarjeta queda fija (0.2.6)."""
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
    dev = "DEV · " if DEV else ""
    state = (paint(dev + "DEBUG ACTIVO", "amber", True) if DEBUG
             else paint(dev + "debug off", "gray"))
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
    El primer banner de la ejecución da una vuelta de destello al borde (0.2.6)."""
    CARD["live"], CARD["fresh"], CARD["pin"] = False, False, False
    if safe_width() < 30:
        banner_plain()
        return
    if CARD_THREAD and ANIM_LIVE and TRUECOLOR and USE_COLOR:
        # TEST (0.2.6): la tarjeta sale ya y la anima un hilo propio; el arranque no bloquea
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
    """Líneas del título: como mucho 2; si sobra texto la segunda acaba en «…» (0.2.4)."""
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
    print("\n".join("  " + ln for ln in lines))


ROW_PLAIN = {}      # n.º → texto plano de la fila impresa (para el destello al elegir, 0.2.4)


def flash_row(n):
    """Repite la fila elegida en blanco un instante antes de limpiar la pantalla (0.2.4)."""
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
    Con animación (0.2.4) las filas entran una a una y el tamaño de la tabla «cuenta» hasta
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

    def prefix(r):               # ★ (la fila que elige «b») ocupa el margen: no resta ancho
        return (flag_mark("best") if "best" in r["flags"] else " ") \
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
        if IS_DESKTOP and not sys.stdin.isatty():
            return                        # tubería o archivo: son las respuestas, no se tocan
        if os.name == "nt":
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getwch()
            return
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
    drain_pending_input()
    pre, prompt = split_prompt(pstyle(prompt))
    for ln in pre:
        print(ln)
    prompt = rl_safe(prompt)
    t0 = time.time()
    r = input(prompt)
    CARD["row"] += 1                 # el Enter del input() no pasa por sys.stdout (0.2.6)
    if phantom and not r.strip() and (time.time() - t0 < PHANTOM_SECS or time.time() - START_T < PHANTOM_BOOT):
        # Segunda oportunidad: se borra la línea del Enter fantasma y el prompt vuelve a salir en el
        # mismo renglón (0.2.7). Sin terminal interactivo input() lo muestra en una línea nueva.
        erase_input_line(prompt, r)
        r = input(prompt)
        CARD["row"] += 1
    return r


PROMPT = "▸ "
INPLACE = sys.stdout.isatty() and ANSI_OK and not DEBUG     # ¿se puede borrar una línea ya escrita? (0.2.7)


def erase_seq(prompt, typed, cols):
    """Secuencia que, justo tras el Enter de un input(), sube sobre la línea escrita (prompt + texto;
    si no cupo en una fila, sobre todas) y la borra, dejando el cursor al inicio. Pura: la prueba --selftest."""
    plain = re.sub(r"[\x01\x02]", "", _ANSI_RE.sub("", str(prompt)))
    rows = max(1, -(-(dwidth(plain) + dwidth(typed)) // max(1, cols)))
    return "\x1b[1A\x1b[2K" * rows + "\r"


def erase_input_line(prompt, typed=""):
    """Borra la línea que acaba de ocupar un input() (prompt + `typed`) para volver a pedirla en el
    mismo sitio, sin líneas nuevas (0.2.7). True si lo hizo; False sin terminal interactivo o en debug."""
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
    mismo sitio (0.2.7). `bad` es el prompt que sale tras una respuesta inválida (None = el mismo, para
    un Enter vacío). Sin terminal interactivo o en debug imprime `warn`, como antes, y deja `cur`."""
    if erase_input_line(cur, typed):
        return bad or cur
    if warn:
        m_warn(warn)
    return cur


def bad_prompt(why):
    """«✗ 1-12, b o q ▸ »: el prompt tras una opción inválida (la ayuda corta va en la misma línea)."""
    return paint("✗", "red", True) + " " + paint(why, "gray") + " " + paint("▸", "orange", True) + " "


# ───────────────────── Barras y paneles de progreso ─────────────────────
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
    if warn:                                   # velocidad < 50 %: la barra se tiñe de ámbar (0.2.4)
        fill = paint(FILL * f, "amber") if f else ""
    else:
        fill = grad(FILL * f, 0.0, 1.0, (now * 0.4) % 1.0 if ANIM else 0.0) if f else ""
    rest = w - f
    t = ""
    if rest > 0 and frac < 1.0 and TIP:
        t, rest = (paint(TIP, "amber") if warn else tip_str(now)), rest - 1
    return fill + t + track_str(rest)


PCT_FLASH = 1.6          # segundos que dura el efecto del % al cambiar (0.2.6)


def pct_text(ptxt, age):
    """El % recién cambiado: degradado que fluye y se apaga hacia blanco en PCT_FLASH s (0.2.6)."""
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
        self.slow = False                    # velocidad caída (barra ámbar, 0.2.4)
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
            self.slow = False
        if not self.live:
            m_info(label + "...")
            return
        global ACTIVE_BAR
        ACTIVE_BAR = self
        if self.panel:
            card_arm()                         # la tarjeta del banner sigue viva (0.2.6)
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
                self.hist.append(val)
                del self.hist[:-240]
            if pct is not None:
                self.indet = False
                if self.pct is not None and pct < self.pct - 0.05:
                    self.hold = time.time() + 1.5      # yt-dlp retrocedió: se ignora
                else:
                    self.pct = pct
                    if int(pct) != self.last_ip:
                        self.last_ip = int(pct)
                        if time.time() - self.chg >= PCT_FLASH + 0.3:     # sin parpadeo continuo (0.2.6)
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
        if ANIM_LIVE and was_live:                       # «·» → «○» → «✓» (0.2.4)
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
        70 % (histéresis). La habitual es el percentil 75 de las últimas muestras (0.2.4)."""
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
            if sweep is not None and pct is not None and ANIM:     # el % sube hasta 100 (0.2.4)
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
        room = w - dwidth(base) - 2
        l3 = base + (("  " + spark_str(hist, room)) if room >= 6 and hist and sweep is None else "")
        return [l1, l2, l3]

    def _paint(self, lines):
        """Pinta las líneas en su sitio (con `self.lock` tomado)."""
        out = f"\x1b[{self.drawn}A" if self.drawn else ""
        out += "".join("\r" + ln + "\x1b[K\n" for ln in lines)
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
        self.bar.start("Preparando")

    def hook(self, d):
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


# ───────────────────── Terminal: teclado y cuenta regresiva ─────────────────────
def hide_keyboard():
    if not IS_IOS:
        return
    try:
        os.system("hideKeyboard >/dev/null 2>&1")
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
        if os.name == "nt":
            import msvcrt  # noqa: F401
        else:
            import termios, tty, select  # noqa: F401
        return True
    except ImportError as _ign:          # p. ej. modo windows forzado en otro sistema
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


class _PosixKeys:
    """Teclado sin eco para la cuenta regresiva (iOS, Android, Linux, macOS)."""

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


class _WinKeys:
    """Teclado de la consola de Windows (msvcrt), sin eco."""

    def __init__(self):
        import msvcrt
        self.m = msvcrt

    def read(self, timeout):
        end = None if timeout is None else time.time() + timeout
        out = []
        while True:
            while self.m.kbhit():
                ch = self.m.getwch()
                if ch in ("\x00", "\xe0"):        # tecla especial (flechas…): 2.º código
                    self.m.getwch()
                    continue
                out.append(ch)
            if out:
                return "".join(out)
            if end is not None and time.time() >= end:
                return ""
            time.sleep(0.02)

    def close(self):
        pass


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
    if not IS_IOS:                         # a-Shell: ni tcsetattr ni select sobre stdin aquí
        try:
            if os.name != "nt" and sys.stdin.isatty():
                import termios
                fd = sys.stdin.fileno()
                _restore_tty(fd, termios.tcgetattr(fd))
        except Exception as _ign:
            ignore("reexec_script", _ign)
        drain_pending_input(0.15)
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
    drain_pending_input()
    try:
        keys = _WinKeys() if os.name == "nt" else _PosixKeys()
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
                    # el degradado se acorta y pasa a magenta a medida que se agota (0.2.4)
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


# ───────────────────────── Utilidades ─────────────────────────
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


YN_SUFFIX_RE = re.compile(r"\s*(?:\([sSyY]/[nN]\))?\s*▸?\s*$")


def yn_prompt(msg, default=True):
    """Texto de una pregunta s/n con el final unificado: «… (S/n) ▸ » si Enter = sí,
    «… (s/N) ▸ » si Enter = no, sin importar qué traiga ya `msg`."""
    base = YN_SUFFIX_RE.sub("", str(msg))
    return f"{base} {'(S/n)' if default else '(s/N)'} ▸ "


def yn_line(default=True):
    """« [S] Sí  [n] No ▸ » (la letra de la opción por omisión va en mayúscula)."""
    return (" " + paint("[S]" if default else "[s]", "orange", True) + " Sí  "
            + paint("[n]" if default else "[N]", "orange", True) + " No " + paint("▸", "orange", True) + " ")


def ask_yn(prompt, default=True, seconds=False):
    """Pregunta s/n y la repite hasta recibir una respuesta válida.
    Estilo dpt: «▍¿Pregunta?» y debajo « [S] Sí  [n] No ▸ » (con barra si hay cuenta).
    seconds=False: ask_line; seconds=None: timed_input sin cuenta; número: con cuenta.
    Devuelve True/False, o None si venció la cuenta regresiva.
    EOFError/KeyboardInterrupt se propagan a quien llama."""
    plain = yn_prompt(prompt, default)
    base = YN_SUFFIX_RE.sub("", str(prompt)).strip()
    for i, ln in enumerate(wrap_text(plat_text(base), term_width() - 1)):
        print((paint("▍", "orange") if i == 0 else " ") + paint(ln, "white", True))
    line = yn_line(default)
    cur = line
    while True:
        # Enter vacío = No es inofensivo: con (s/N) no se filtra el Enter «fantasma».
        ph = bool(default)
        r = (ask_line(cur, ph, plain) if seconds is False
             else timed_input(cur, seconds, ph, plain))
        if r is None:
            return None
        v = parse_yn(r, default)
        if v is not None:
            return v
        # inválida: se borra y se repite en el mismo renglón con «✗» en rojo (0.2.7)
        cur = retry_prompt(cur, r, paint("✗", "red", True) + line[1:], "Respuesta inválida: escribe s o n.")


WIN_RESERVED_RE = re.compile(r"^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\..*)?$", re.I)


def safe_name(title, max_bytes=MAX_NAME_BYTES, windows=None):
    s = unicodedata.normalize("NFC", title or "video")
    s = re.sub(r"[\x00-\x1f\x7f]", "", s)
    s = re.sub(r'[\\/:*?"<>|]', "_", s)
    s = re.sub(r"\s+", " ", s).strip(" .").lstrip(".")
    if not s:
        s = "video"
    if (IS_WINDOWS if windows is None else windows) and WIN_RESERVED_RE.match(s):
        s = "_" + s                    # CON, NUL, COM1… no se pueden usar como nombre
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


def ffmpeg_available():
    try:
        from yt_dlp.postprocessor import FFmpegPostProcessor
        if FFmpegPostProcessor().available:
            return True
    except Exception as _ign:
        ignore("ffmpeg_available", _ign)
    return bool(shutil.which("ffmpeg"))


# ───────────────────── Formatos y pistas: etiquetas y selección ─────────────────────
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


def res_label(f):
    h = f.get("height")
    res = f"{h}p" if h else (f.get("resolution") or "?")
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


def list_cap():
    """Filas máximas de la lista de formatos según el alto del terminal (0.2.4).
    DLPY_ROWS=N lo fuerza; DLPY_ROWS=0 = sin tope."""
    env = os.environ.get("DLPY_ROWS", "").strip()
    if env.isdigit():
        return int(env) or 10 ** 6
    try:
        lines = shutil.get_terminal_size((80, 24)).lines
    except (OSError, ValueError):
        lines = 24
    return max(8, lines - 16)          # la tarjeta del banner ocupa 5 líneas (0.2.6)


def visible_start(n, take, keep=None):
    """Índice desde el que se muestran las últimas `take` de `n` filas; la fila `keep`
    (la que elige «b») nunca se oculta (0.2.4)."""
    start = max(0, n - take)
    if keep is not None and 0 <= keep < start:
        start = keep
    return start


def m_block(label, lines):
    """Bloque «✓ Etiqueta  línea» con las líneas siguientes sangradas (una sola marca) (0.2.4)."""
    lead = len(label) + 4
    out = []
    for ln in lines:
        out += wrap_text(plat_text(ln), max(8, term_width() - lead))
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
        if not APPLE_MODE:  # misma altura: h264 (decodifica en cualquier chip) antes que vp9/hevc
            return "v", max(apple, key=lambda f: (
                f.get("height") or 0,
                (f.get("vcodec") or "").lower().startswith(("avc1", "h264")),
                f.get("tbr") or 0))
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
    """Devuelve (pista, sin_respuesta). sin_respuesta=True omite las pistas extra."""
    clear_screen()
    header("ELEGIR PISTA PREDETERMINADA", gap=False)
    m_info("Se detectaron varios idiomas.")
    legend(["apple", "orig"])
    print_rows([track_row(i, t) for i, t in enumerate(tracks, 1)], ["apple", "orig"], TRACK_HEAD)
    txt = "n.º · Enter = original"
    if countdown_supported():
        txt += f" · {WAIT_SECONDS} s"
    hint(txt)
    cur = PROMPT
    while True:
        try:
            raw = timed_input(cur)
        except (EOFError, KeyboardInterrupt):
            return original, True
        if raw is None:
            m_info("Sin respuesta: se usa la pista original.")
            return original, True
        typed, raw = raw, raw.strip()
        if not raw:
            return original, False
        if raw.isdigit() and 1 <= int(raw) <= len(tracks):
            chosen = tracks[int(raw) - 1]
            m_ok(f"Predeterminada: {chosen['lang']} · {track_label(chosen)}")
            return chosen, False
        cur = retry_prompt(cur, typed, bad_prompt(f"1-{len(tracks)} o Enter"),
                           f"Opción inválida: escribe un número del 1 al {len(tracks)} o Enter.")


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

    clear_screen()
    header("ELEGIR PISTAS DE AUDIO ADICIONAL", gap=False)
    legend(["apple", "orig"])
    print_rows([track_row(i, t) for i, t in enumerate(others, 1)], ["apple", "orig"], TRACK_HEAD)
    hint("n.º separados por espacio (ej. 1 2 4) · Enter = todas")
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
        toks = [x for x in re.split(r"[\s,]+", raw) if x]
        bad = [x for x in toks if not (x.isdigit() and 1 <= int(x) <= len(others))]
        if bad:
            cur = retry_prompt(cur, typed, bad_prompt(f"1-{len(others)}"),
                               f"Opción inválida: {' '.join(bad)} (usa números del 1 al {len(others)}).")
            continue
        chosen = [others[int(x) - 1] for x in toks]
        break
    out = [primary]
    for t in chosen:
        if t not in out:
            out.append(t)
    return out


# ───────── Post-proceso: pista predeterminada ─────────
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


# ───────── Compatibilidad Apple: conversión opcional ─────────
MP4_ACODEC = ("mp4a", "aac", "alac", "mp3", "ac-3", "ec-3", "ac3", "eac3")
HEVC_CODEC = ("hvc1", "hev1", "hevc")


def _short(codec):
    return (codec or "?").split(".")[0]


def apple_plan(kind, fmt, selected, merge_ext):
    """Qué haría falta para que el resultado final sea nativo en Apple.
    None si ya lo es; si no, un plan con lo que se recodifica o se remuxa.
    Si hay merge pero video + audios + contenedor resultante ya son
    compatibles, tampoco se ofrece conversión.
    Fuera de iOS/macOS nunca se convierte (se reproduce casi todo de forma nativa)."""
    if not APPLE_MODE:
        return None
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


# ───────────────────── Bits, HDR y sondeo del video ─────────────────────
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


def convert_est_secs(plan, duration):
    """Segundos estimados de conversión, o None si no se puede estimar.
    Sin recodificar video (solo remux/audio) ≈ 0. Con venc: duración × coste
    relativo a 1080p30 / CONVERT_BASE_SPEED (más alto o más fps → más lento)."""
    if not plan.get("venc"):
        return 0.0
    try:
        dur = float(duration or 0)
    except (TypeError, ValueError):
        return None
    if dur <= 0:
        return None
    h = float(plan.get("height") or 0) or 720.0
    fps = float(plan.get("fps") or 0) or 30.0
    scale = (h / 1080.0) ** 2 * (fps / 30.0)
    return dur * max(0.15, scale) / CONVERT_BASE_SPEED


def convert_is_quick(plan, duration, limit=CONVERT_QUICK_SECS):
    """True si la conversión debería acabar en ≤ limit segundos (o no hay venc)."""
    est = convert_est_secs(plan, duration)
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
    if plan.get("remux") and plan.get("cur"):
        d["cfrom"] = plan["cur"]
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


# ───────────────────── Ya descargado: reutilizar o convertir ─────────────────────
def reuse_downloaded(old_file, old_entry, index, key, title, info, kind, fmt, fmt_id,
                     selected, orig_ids, plan):
    """Aprovecha el archivo ya descargado. True si resolvió la petición (entregó
    el archivo); False si hay que descargar de nuevo.
    - Mismos parámetros (formato/pistas y misma decisión de conversión): se entrega tal cual.
    - Mismos streams, archivo sin convertir y ahora se pide convertir: se convierte ese archivo.
    - Si el archivo ya está convertido y ahora no se quiere conversión (o al
      revés y no queda el original), se fuerza re-descarga."""
    meta = (old_entry or {}).get("meta") or {}
    old_conv, want_conv = bool(meta.get("converted")), bool(plan)
    dbg("reutilizar", {"archivo": old_file, "format_id_antiguo": meta.get("format_id"),
                       "format_id_nuevo": fmt_id, "convertido_antes": old_conv,
                       "convertir_ahora": want_conv})
    if not old_file or str(meta.get("format_id")) != str(fmt_id):
        return False
    if old_conv == want_conv:
        m_ok("Mismos parámetros: se reutiliza el archivo ya descargado.")
        deliver_existing(old_file, old_entry, title)
        return True
    # Aquí old_conv != want_conv. Si ya estaba convertido y ahora se quiere el
    # original, no queda el archivo sin convertir: se vuelve a descargar.
    if old_conv:
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
    deliver(final, title)
    return True


def ask_keep_bits(plan, est, slow):
    """Pregunta si conservar los bits originales (origen de más de 8 bits) y avisa qué cambia.
    Pone plan['out_bits']. Devuelve el plan o None si se cancela."""
    bits, hdr = plan["bits"], plan.get("hdr")
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
        for n, (_, txt) in enumerate(choices, 1):
            print(" " + paint(f"{n}", "orange", True) + "  " + txt)
        default_n = 2
        cur = f"Opción (Enter = {default_n}) ▸ "
        while True:
            try:
                raw = timed_input(cur, WAIT_SECONDS)
            except (EOFError, KeyboardInterrupt):
                m_info("Conversión cancelada; se descargará sin convertir.")
                return None
            typed = raw
            raw = default_n if raw is None or not str(raw).strip() else str(raw).strip()
            if str(raw).isdigit() and 1 <= int(raw) <= len(choices):
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
    rápido). Devuelve el plan o None. Si hay que recodificar un video de más de 8 bits
    SIEMPRE pregunta si conservarlos (también en conversiones rápidas)."""
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
    est = convert_est_secs(plan, duration)
    bits = plan.get("bits")
    slow = not convert_is_quick(plan, duration)
    plan["asked_bits"] = False

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

    if plan["venc"]:
        note("Recodificar el video a HEVC puede tardar bastante en el iPhone.")
        if est is not None:
            note(f"Estimación ~{int(round(est))} s (umbral de pregunta: {CONVERT_QUICK_SECS} s).")
        if not bits:
            note("No se pudieron detectar los bits del origen; si el archivo resulta tener más de 8 se "
                 "conservan (hasta 10)."
                 + (f" Origen {plan['hdr']}." if plan.get("hdr") else ""))
    if countdown_supported():
        hint(f"Enter = convertir · {WAIT_SECONDS} s")
    try:
        r = ask_yn("¿Convertir? (S/n) ▸ ", default=True, seconds=WAIT_SECONDS)
    except (EOFError, KeyboardInterrupt):
        m_info("Conversión cancelada; se descargará sin convertir.")
        return None
    if r is None:
        m_info("Sin respuesta: se convierte.")
        return plan
    return plan if r else None


# ───────────────────── JSON / índice ─────────────────────
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
        out.append(FILES_DIR)       # 0.0.1 en Android guardaba aquí
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
    for v in load_json(INDEX_FILE).values():
        if isinstance(v, dict) and v.get("file"):
            p = os.path.join(DOWNLOAD_DIR, v["file"])
            if os.path.isfile(p) and p not in out:
                out.append(p)
    return out


def lookup_downloaded(idx, key):
    entry = idx.get(key)
    if not entry or not entry.get("file"):
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
            meta["video"]["apple"] = True
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
        for k_in, k_out in (("engine", "engine"), ("secs", "secs"), ("cfrom", "cfrom")):
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


def fmt_kbps(k):
    k = float(k)
    return f"{k / 1000:.1f} Mbps" if k >= 1000 else f"{k:.0f} kbps"


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


def audio_rows(tracks):
    """Filas de audio: una con códec y bitrate y, si hay varias pistas, otra con los idiomas
    (◆ original, ▸ predeterminada). Devuelve (filas, hay_marcas)."""
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
        rows.append(("Convertido" if not rows else "", " · ".join(second)))   # 0.2.4: máx. 2 líneas
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
    dash = "—"                                   # 0.2.4: filas fijas; «—» si falta el dato
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
        arows, marks = audio_rows(tracks)
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


# ───────────────────── Enlace y portapapeles ─────────────────────
def clipboard_cmd():
    """Orden que imprime el portapapeles de este sistema, o None si no hay."""
    which = shutil.which
    if IS_ANDROID:
        return ["termux-clipboard-get"] if which("termux-clipboard-get") else None
    if IS_IOS:
        # iOS pide permiso de pegado cada vez: solo si se pide con DLPY_CLIPBOARD=1
        on = os.environ.get("DLPY_CLIPBOARD", "").strip().lower() not in ("", "0", "no", "false")
        return ["pbpaste"] if on else None
    if IS_MAC:
        return ["pbpaste"] if which("pbpaste") else None
    ps = which("powershell") or which("pwsh") or which("powershell.exe")
    if IS_WINDOWS or (IS_LINUX and is_wsl() and ps):
        return [ps, "-NoProfile", "-Command", "Get-Clipboard"] if ps else None
    if which("wl-paste") and os.environ.get("WAYLAND_DISPLAY"):
        return ["wl-paste", "--no-newline"]
    if os.environ.get("DISPLAY"):
        if which("xclip"):
            return ["xclip", "-selection", "clipboard", "-o"]
        if which("xsel"):
            return ["xsel", "-b", "-o"]
    return None


def clipboard_link():
    """Enlace http(s) del portapapeles o None."""
    cmd = clipboard_cmd()
    if not cmd:
        return None
    out = termux_run(cmd, timeout=4)
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
        link = ask_line("Pega el enlace ▸ ").strip()
    except (EOFError, KeyboardInterrupt):
        return None
    return link or None


# ───────────────────── Dependencias ─────────────────────
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


def is_installed(module):
    import importlib
    import importlib.util
    refresh_paths()
    importlib.invalidate_caches()
    try:
        return importlib.util.find_spec(module) is not None
    except Exception as _ign:
        ignore("is_installed", _ign)
        return False


def latest_version(pip_name):
    import urllib.request
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{pip_name}/json", timeout=6) as r:
            return json.load(r)["info"]["version"]
    except Exception as _ign:
        ignore("latest_version", _ign)
        return None


def vtuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


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


# ─────────── Actualizaciones desde GitHub ───────────
UPDATE_URL = (os.environ.get("DLPY_UPDATE_URL")
              or "https://raw.githubusercontent.com/ElDelDLpy/DLpy/main/dlpy.py")
UPDATE_STATE_FILE = os.path.join(STATE_DIR, "update.json")
UPDATE_MAX_BYTES = 3 * 1024 * 1024


def remote_script_version(text):
    """Versión «x.y.z» de un dlpy.py descargado, o None si no parece uno válido."""
    if not text or not text.startswith("#!dlpy.py"):
        return None
    m = re.search(r'(?m)^VERSION = "(\d+\.\d+\.\d+)"[ \t]*$', text)
    return m.group(1) if m else None


_RAW_GH_RE = re.compile(r"^https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/?#]+)/([^?#]+)$")


def fresh_bytes(url, timeout=5, limit=None):
    """Bytes de `url` sin pasar por cachés. Para enlaces raw de GitHub consulta primero la
    API del repositorio (contents?ref=rama, formato raw: lee lo último subido) y, si falla
    o está limitada, el enlace raw con un parámetro único que evita la caché del CDN.
    Otros enlaces se piden tal cual. None si todo falla."""
    import urllib.request
    import urllib.parse
    limit = limit or UPDATE_MAX_BYTES
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
    """Texto del dlpy.py del repositorio (o del `url` dado), o None si falla o no es
    un script válido."""
    try:
        raw = fresh_bytes(url or UPDATE_URL, timeout)
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


def sync_origin_copy(text, origin=None, script_path=None):
    """Android: guarda también el código nuevo en la carpeta desde la que se abrió
    DLpy (la de antes de moverse a ~). Devuelve la ruta escrita o None si no aplica."""
    origin = origin or os.environ.get("DLPY_ORIGIN")
    script_path = script_path or SCRIPT_PATH
    if not origin or os.path.abspath(origin) == os.path.abspath(script_path):
        return None
    try:
        if not os.path.isdir(os.path.dirname(origin)):
            return None
        write_text(origin, text)
        return origin
    except OSError as e:
        m_warn(f"No se pudo actualizar también {origin}: {e}")
        return None


GITHUB_SAME = {"igual": False}        # ¿la instalada es idéntica a GitHub? (lo fija check_update)
UPDATE_CHECKED = {"ok": False}        # ¿llegó a comprobarse la última versión (hubo red)? (0.2.7)

# Búsqueda de actualizaciones una vez al día (0.2.7): fecha de la última comprobación por clave
# («script» = DLpy en GitHub, «deps» = dependencias) en state/checks.json.
CHECK_FILE = os.path.join(STATE_DIR, "checks.json")
try:
    CHECK_HOURS = float(os.environ.get("DLPY_CHECK_HOURS", "24").strip())
except ValueError:
    CHECK_HOURS = 24.0


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
    """«nueva» (hay una más reciente en GitHub), «igual» o «local» (la local es más
    nueva que la de GitHub: el autor puede tener una sin subir)."""
    r, l = vtuple(remote), vtuple(VERSION if local is None else local)
    return "nueva" if r > l else "igual" if r == l else "local"


def check_update(force=False):
    """Si el repositorio tiene una versión más nueva, pregunta, la instala y la ejecuta.
    Siempre deja una línea con el resultado (✓ si ya tienes la última).

    Devuelve True si se ejecutó la versión nueva (quien llama debe terminar)."""
    cbar = Bar()
    cbar.start("Comprobando DLpy")
    try:
        text = fetch_remote_script(timeout=8 if force else 5)
    finally:
        cbar.stop()
    remote = remote_script_version(text)
    if not remote:
        m_warn(f"DLpy {VERSION} · no se pudo comprobar la última versión")
        return False
    UPDATE_CHECKED["ok"] = True                # hubo respuesta: cuenta como comprobada (0.2.7)
    status = update_status(remote)
    rec = load_json(RECOVERED_FILE)
    crashed = rec.get("crashed")
    if crashed and vtuple(VERSION) > vtuple(crashed):
        clear_recovered()                  # ya pasaste la versión que falló
        rec, crashed = {}, None
    if status == "igual":
        row = origins_row(remote, text, github=False, backups=False)   # solo main ↔ instalada (sin versions/)
        st = row_state(row_diffs(row))
        GITHUB_SAME["igual"] = (st == "igual")      # check_version lo usa para refrescar la copia guardada
        m_check(f"DLpy {VERSION} · última versión" + (" · idéntica a GitHub" if st == "igual" else ""))
        if st not in (None, "igual"):
            report_row(row, show_diff=False)
            note("Mismo número con código distinto en algún origen: revisa cuál es el bueno.")
        return False
    if status == "local":
        m_info(f"DLpy {VERSION} · versión local más reciente que la de GitHub ({remote})")
        return False
    hold = downgrade_hold()
    if hold and vtuple(remote) <= vtuple(hold):
        if not force:
            m_info(f"DLpy {VERSION} · bajaste a propósito desde la {hold}; no se ofrece la {remote} de GitHub")
            note(f"Cuando haya una versión más nueva que la {hold} se avisará. "
                 "Con --actualizar puedes instalarla de todos modos.")
            return False
        m_warn(f"La {remote} de GitHub no es más nueva que la {hold}, de la que bajaste a propósito.")
    match = (crash_match(remote, text) or (None,))[0]
    if skip_update_after_recovery(remote, crashed, match):
        if not force:
            m_info(f"DLpy {VERSION} · recuperada tras fallar la {crashed}; no se ofrece la {remote} de GitHub")
            note("Cuando haya una versión más nueva que la que falló se avisará. "
                 "Con --actualizar puedes instalarla de todos modos.")
            return False
        m_warn(f"La {remote} de GitHub es la que falló en este equipo.")
    else:
        m_info(f"Hay una versión nueva de DLpy: {VERSION} → {remote}")
    kind = show_crash_warning(remote, text)       # avisa si es idéntica a una que falló
    # a-Shell: esta pregunta va con input() normal (sin cbreak). Después la versión nueva corre en
    # este mismo proceso y cambiar el modo del terminal justo antes la congelaba.
    if not ask(f"¿Instalar la {remote} y ejecutarla ahora? (S/n) ▸ ", default=(kind != "igual"),
               seconds=False if IS_IOS else WAIT_SECONDS):
        note("Se volverá a preguntar en la próxima comprobación (cada 24 h) o con --actualizar.")
        return False
    try:
        write_text(SCRIPT_PATH, text)
    except Exception as e:
        m_warn(f"No se pudo instalar la actualización: {e}")
        return False
    clear_recovered()
    m_check(f"DLpy {remote} · instalada")
    copied = sync_origin_copy(text)
    if copied:
        m_check(f"Código actualizado también en {copied}")
    reexec_script()                                    # termina con SystemExit
    return True


def pip_args(pip_name, no_deps=None):
    """Argumentos de «pip» (sin el ejecutable): -U y, en iOS/Android, --no-deps (0.2.5)."""
    if no_deps is None:
        no_deps = IS_ANDROID or IS_IOS
    return ["install", "-U", pip_name] + (["--no-deps"] if no_deps else [])


def pip_run(args):
    """Lanza pip con `args`. Devuelve el código de salida o None si no se pudo lanzar (0.2.5).
    iOS: a-Shell ejecuta sus comandos dentro de la app, así que se mantiene su «pip» con os.system
    (argumentos entrecomillados). Android y escritorio: subprocess sin shell (vale en Windows)."""
    if IS_IOS:
        return os.system("pip " + " ".join(shlex.quote(a) for a in args))
    import subprocess
    try:
        return subprocess.call([sys.executable or "python3", "-m", "pip"] + args)
    except OSError as _ign:
        ignore("pip_install", _ign)
        return None


def pip_install(pip_name):
    """Instala/actualiza `pip_name`. True si salió bien. Reintenta con --break-system-packages
    (PEP 668: Termux reciente y el Python del sistema en Linux/Homebrew); iOS no lo necesita."""
    m_info(f"Instalando {pip_name}...")
    ok = False
    for extra in ([], ["--break-system-packages"]):
        rc = pip_run(pip_args(pip_name) + extra)
        if rc is None:
            break
        if rc == 0:
            ok = True
            break
        if IS_IOS:
            break
    refresh_paths()
    return ok


def ffmpeg_hint():
    return {"android": "pkg install ffmpeg", "macos": "brew install ffmpeg",
            "windows": "winget install Gyan.FFmpeg  (o https://ffmpeg.org/download.html)",
            "linux": "sudo apt install ffmpeg  (o el gestor de tu distribución)",
            "ios": "a-Shell lo incluye"}[PLATFORM]


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


# ─────────── YouTube: runtime de JavaScript + yt-dlp-ejs ───────────
# Desde yt-dlp 2025.11.12 YouTube completo necesita un runtime de JavaScript
# (deno, node, bun o quickjs) y el paquete yt-dlp-ejs en la versión exacta que
# fija esa versión de yt-dlp. Con «--no-deps» (iOS/Android) ese paquete no se
# instalaba nunca.
JS_REQUIRED_FROM = (2025, 11, 12)
JS_RUNTIMES = (("deno", "deno"), ("node", "node"), ("bun", "bun"), ("quickjs", "qjs"))
JS_INSTALL_HINT = {"android": "pkg install nodejs", "macos": "brew install deno",
                   "windows": "winget install DenoLand.Deno", "linux": "sudo apt install nodejs  (o deno.com)",
                   "ios": "no hay un runtime de JavaScript conocido para a-Shell"}


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
    note("Instálalo con: " + JS_INSTALL_HINT[PLATFORM])


# ─────────── Dependencias del sistema por plataforma ───────────
# Lo que DLpy necesita fuera de pip según dónde corre: ffmpeg, un runtime de
# JavaScript para YouTube y (solo Android) termux-api. Se revisa siempre y lo que
# falta se instala con UNA sola pregunta, con el gestor de cada sistema.
DEPS_STATE_FILE = os.path.join(STATE_DIR, "deps.json")      # rechazos recordados
SYS_PKGS = {
    "ffmpeg": {"android": "ffmpeg", "macos": "ffmpeg", "windows": "Gyan.FFmpeg",
               "linux": "ffmpeg", "dnf": "ffmpeg-free"},
    "js": {"android": "nodejs", "macos": "deno", "windows": "DenoLand.Deno", "linux": "nodejs"},
    "termux-api": {"android": "termux-api"},
}
JS_LABELS = {"deno": "Deno", "node": "Node.js", "bun": "Bun", "quickjs": "QuickJS"}


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


def system_install_cmds(keys, platform=None, which=None, root=None):
    """Órdenes (lista de listas) que instalan `keys` con el gestor del sistema, o
    None si no hay gestor / nada que instalar. Los parámetros solo se inyectan en
    pruebas."""
    platform = platform or PLATFORM
    which = which or shutil.which

    def pkgs(mgr=None):
        out = []
        for k in keys:
            d = SYS_PKGS.get(k, {})
            n = d.get(mgr) or d.get(platform)
            if n and n not in out:
                out.append(n)
        return out

    if platform == "android":
        p = pkgs()
        return [["pkg", "install", "-y"] + p] if p and which("pkg") else None
    if platform == "macos":
        p = pkgs()
        return [["brew", "install"] + p] if p and which("brew") else None
    if platform == "windows":
        if not which("winget"):
            return None
        return [["winget", "install", "--id", n, "-e", "--accept-package-agreements",
                 "--accept-source-agreements"] for n in pkgs()] or None
    if platform == "linux":
        if root is None:
            root = hasattr(os, "geteuid") and os.geteuid() == 0
        sudo = [] if root else (["sudo"] if which("sudo") else None)
        if sudo is None:
            return None
        for exe, args in (("apt-get", ["apt-get", "install", "-y"]),
                          ("dnf", ["dnf", "install", "-y"]),
                          ("pacman", ["pacman", "-S", "--noconfirm"]),
                          ("zypper", ["zypper", "--non-interactive", "install"]),
                          ("apk", ["apk", "add"])):
            if which(exe):
                p = pkgs(exe)
                return [sudo + args + p] if p else None
    return None


def system_keys():
    """Qué necesita DLpy del sistema en ESTA plataforma."""
    keys = ["ffmpeg"]
    if not IS_IOS and ytdlp_needs_js():
        keys.append("js")
    if IS_ANDROID:
        keys.append("termux-api")
    return keys


def system_state(key):
    """(instalado, nombre, detalle) de una dependencia del sistema."""
    if key == "ffmpeg":
        if IS_IOS:
            return True, "ffmpeg", "integrado en a-Shell"
        return bool(shutil.which("ffmpeg")), "ffmpeg", ("instalado" if shutil.which("ffmpeg")
                                                        else "falta (unir audio y video)")
    if key == "js":
        rt = js_runtime()
        if rt:
            return True, JS_LABELS.get(rt[0], rt[0]), "JavaScript para YouTube"
        return False, "Runtime de JavaScript", "falta (YouTube)"
    ok = bool(shutil.which("termux-notification"))
    return ok, "termux-api", ("instalado" if ok else "falta (notificaciones y portapapeles)")


def system_hint(key):
    if key == "ffmpeg":
        return ffmpeg_hint()
    if key == "js":
        return JS_INSTALL_HINT[PLATFORM]
    return "pkg install termux-api"


def check_system_packages(force=False):
    """Línea ✓ por cada dependencia del sistema; ofrece instalar las que faltan
    con una sola pregunta (y recuerda el «no», salvo con force)."""
    declined = load_json(DEPS_STATE_FILE)
    missing = []
    for key in system_keys():
        ok, name, detail = system_state(key)
        if ok:
            m_check(f"{name} · {detail}")
            declined_clear(key)
        else:
            missing.append((key, name, detail))
    ask_now = []
    for key, name, detail in missing:
        if declined.get(key) and not force:
            m_warn(f"{name} · falta, rechazado (--actualizar lo pregunta)")
        else:
            m_warn(f"{name} · {detail}")
            ask_now.append((key, name))
    if not ask_now:
        return
    keys = [k for k, _n in ask_now]
    cmds = system_install_cmds(keys)
    if not cmds:
        for key, name in ask_now:
            note(f"{name}: instálalo con {system_hint(key)}")
        return
    shown = " && ".join(" ".join(c) for c in cmds)
    names = ", ".join(n for _k, n in ask_now)
    if not ask(f"¿Instalar {names} con «{shown}»? (S/n) ▸ ", seconds=WAIT_SECONDS):
        for key in keys:
            declined_set(key)
        note("No se vuelve a preguntar; con --actualizar lo pregunta de nuevo.")
        return
    import subprocess
    for c in cmds:
        try:
            subprocess.call(c)
        except OSError as e:
            m_warn(f"No se pudo lanzar el instalador: {e}")
    failed = False
    for key, name in ask_now:
        ok, name2, detail = system_state(key)
        if ok:
            m_check(f"{name2} · instalado")
            declined_clear(key)
        else:
            failed = True
            m_warn(f"{name} · no se pudo instalar")
            note(f"Instálalo con: {system_hint(key)}")
    if "termux-api" in keys and shutil.which("termux-notification"):
        note("Además necesitas la app Termux:API (F-Droid); el script no puede instalarla.")
    if failed and IS_WINDOWS:
        note("Si winget terminó bien, cierra y abre la terminal para que Windows encuentre lo instalado.")


def check_dependencies(force=False):
    """Revisa instalación y actualizaciones; cada cosa deja una línea ✓/●.
    Devuelve False si falta una obligatoria. Que estén instaladas se mira siempre; buscar versiones
    nuevas, los paquetes del sistema y yt-dlp-ejs solo si toca (una vez al día, 0.2.7) o con force."""
    due = force or check_due("deps")
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
                if ask(f"¿Actualizar {pip_name}? (S/n) ▸ ", seconds=WAIT_SECONDS):
                    pip_install(pip_name)
                    m_check(f"{pip_name} {pkg_version(pip_name) or '?'} · actualizada")
                    declined_clear(pip_name)
                else:
                    declined_set(pip_name, lat)
                    note("No se vuelve a preguntar por esta versión; con --actualizar la instalas.")
        elif cur and lat:
            m_check(f"{pip_name} {cur} · última versión")
        else:
            net_ok = False                       # sin respuesta de PyPI: se reintenta al siguiente arranque
            m_warn(f"{pip_name} {cur or '?'} · no se pudo comprobar la última versión")
    if due:
        check_system_packages(force)
        check_js_components(force)
        if net_ok:
            check_mark("deps")
    return True


# ───────────────────── Changelog y backup ─────────────────────
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


def changelog_block(src):
    """(inicio, fin, cuerpo, cerrado) del bloque de changelog de `src`, o None si no hay.
    Con marcador de fin usa CL_RE. Sin él (bloque abierto) toma las líneas «#» que siguen
    a «# ==== CHANGELOG ====» hasta la primera de texto suelto («# Texto») o que no sea
    comentario, para que el changelog salga igual del script."""
    m = CL_RE.search(src)
    if m:
        return m.start(), m.end(), m.group(1), True
    o = CL_OPEN_RE.search(src)
    if not o:
        return None
    lines = src[o.end():].splitlines(keepends=True)
    taken, used = [], 0
    for i, ln in enumerate(lines):
        t = ln.rstrip("\r\n")
        if i == 0 and not t.strip():
            used += len(ln)               # resto de la línea del marcador
            continue
        if not t.startswith("#") or re.match(r"^# [^\s#=-]", t):
            break
        taken.append(t)
        used += len(ln)
    return o.start(), o.end() + used, "\n".join(taken) + "\n", False


def extract_changelog():
    """Saca el changelog del .py, lo agrega a changelog.md y lo quita del script."""
    try:
        src = read_text(SCRIPT_PATH)
    except Exception as _ign:
        ignore("extract_changelog", _ign)
        return
    blk = changelog_block(src)
    if not blk:
        return
    b_start, b_end, body, closed = blk
    if not closed:
        m_warn("El changelog del script no tiene marcador de fin "
               "(# ==== FIN CHANGELOG ====); se tomó hasta la primera línea que no es del changelog.")
    lines = []
    for ln in body.splitlines():
        if ln.startswith("# "):
            lines.append(ln[2:])
        else:
            lines.append(ln.lstrip("#"))
    new = parse_sections("\n".join(lines))

    try:
        existing = parse_sections(read_text(CHANGELOG_FILE)) if os.path.isfile(CHANGELOG_FILE) else {}
        added = [k for k in new if k not in existing]
        for k, v in new.items():
            if k not in existing or k == VERSION:      # la versión actual se refresca
                existing[k] = v
        out = "# Changelog DLpy\n\n"
        for k in sorted(existing, key=vtuple, reverse=True):
            out += f"## {k}\n\n{existing[k]}\n\n"
        write_text(CHANGELOG_FILE, out.rstrip("\n") + "\n")
        publish_changelog_to_files()
    except Exception as e:
        m_warn(f"No se pudo escribir el changelog: {e}")
        return

    try:
        stripped = src[:b_start] + src[b_end:]
        write_text(SCRIPT_PATH, stripped)
        m_ok(f"Changelog guardado en {CHANGELOG_FILE}"
             + (f" (+{len(added)} versión/es nueva/s)" if added else ""))
    except Exception as e:
        m_warn(f"Changelog guardado, pero no se pudo limpiar el script: {e}")


def changelog_pending():
    """True si el .py todavía trae su bloque de changelog por extraer."""
    try:
        return changelog_block(read_text(SCRIPT_PATH)) is not None
    except Exception as _ign:
        ignore("changelog_pending", _ign)
        return False


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
    lines = [ln[2:] if ln.startswith("# ") else ln.lstrip("#")
             for ln in m.group(1).splitlines()]
    return "# Changelog DLpy\n\n" + "\n".join(lines).strip("\n") + "\n"


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
        shutil.copyfile(SCRIPT_PATH, SNAPSHOT_FILE)
    except Exception as _ign:
        ignore("save_snapshot", _ign)


# ───────────────────── Limpieza de almacenamiento ─────────────────────
try:
    CLEAN_LIMIT = int(float(os.environ.get("DLPY_CLEAN_LIMIT_MB", "1024")) * 1024 * 1024)
except ValueError:
    CLEAN_LIMIT = 1024 * 1024 * 1024


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
            if VER_DIR_RE.match(n) and os.path.isdir(p):
                bak += download_files(p)    # carpetas de versión legadas: solo descargas
            elif is_data_entry(n) and os.path.isfile(p):
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


def _size_text(n):
    return human_size(n) if n else "0B"


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


def _move_legacy(src, dst):
    """Mueve src → dst. Si dst ya existe, conserva el nuevo y descarta el viejo."""
    if not os.path.lexists(src):
        return False
    try:
        if os.path.lexists(dst):
            if os.path.isdir(dst) and os.path.isdir(src):
                for n in os.listdir(src):
                    _move_legacy(os.path.join(src, n), os.path.join(dst, n))
                shutil.rmtree(src, ignore_errors=True)
            else:
                remove_paths([src])
            return True
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        move_file(src, dst)
        return True
    except OSError as e:
        if DEBUG:
            m_warn(f"No se pudo migrar {src}: {e}")
        return False


def migrate_internal_layout():
    """Estructura anterior de dlpy_internal → state/, script/, cache/, delivery/."""
    if not os.path.isdir(INTERNAL_DIR):
        return
    moved = 0
    for name, dst in (("index.json", INDEX_FILE), ("last_link.json", LAST_FILE),
                      ("version.json", VERSION_FILE),
                      ("script_snapshot.py", SNAPSHOT_FILE),
                      ("changelog.md", CHANGELOG_FILE)):
        moved += _move_legacy(os.path.join(INTERNAL_DIR, name), dst)
    moved += _move_legacy(os.path.join(INTERNAL_DIR, "stream_cache"), STREAM_CACHE_DIR)
    hash_re = re.compile(r"^[0-9a-f]{12}$")
    for n in sorted(os.listdir(INTERNAL_DIR)):
        p = os.path.join(INTERNAL_DIR, n)
        if hash_re.match(n) and os.path.isdir(p) and not os.path.islink(p):
            moved += _move_legacy(p, os.path.join(DELIVERY_DIR, n))
    if moved:
        m_info(f"dlpy_internal reorganizada: {moved} elemento(s) movido(s).")


def check_storage():
    """Si dlpy_internal + dlpy_files superan el límite, ofrece limpiar."""
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


# ───────────────────── Control de versión ─────────────────────
def is_data_entry(name):
    """Nombre que cuenta como descarga completada (no backups ni basura)."""
    return not (name.startswith(".") or name.endswith(".tmp") or name in RESERVED
                or VER_DIR_RE.match(name))


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
    note("Quedan descargas en dlpy_internal (entregas, caché, work…).")
    if not ask(f"¿Mover también las descargas de dlpy_internal ({_size_text(size)}) "
               f"a backups? (s/N) ▸ ", default=False):
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
        m_ok(f"dlpy_internal: {moved} elemento(s) movido(s) a backups.")
    return moved


def migrate_legacy_dlpy_data():
    """Una sola vez: mueve ~/Documents/dlpy_data → dlpy_files + internals."""
    if not os.path.isdir(OLD_DATA_DIR):
        return
    m_info("Migrando dlpy_data → dlpy_files / dlpy_internal...")
    moved = 0
    try:
        os.makedirs(FILES_DIR, exist_ok=True)
        os.makedirs(BACKUP_DIR, exist_ok=True)
        for n in sorted(os.listdir(OLD_DATA_DIR)):
            src = os.path.join(OLD_DATA_DIR, n)
            if n == "changelog.md" and os.path.isfile(src):
                if not os.path.isfile(CHANGELOG_FILE):
                    move_file(src, CHANGELOG_FILE)
                    moved += 1
                else:
                    os.remove(src)
                continue
            if n == "backups" and os.path.isdir(src):
                for bn in os.listdir(src):
                    move_file(os.path.join(src, bn),
                                _free_path(os.path.join(BACKUP_DIR, bn)))
                    moved += 1
                try:
                    os.rmdir(src)
                except OSError as _ign:
                    ignore("migrate_legacy_dlpy_data", _ign)
                continue
            if VER_DIR_RE.match(n) and os.path.isdir(src):
                move_file(src, _free_path(os.path.join(BACKUP_DIR, n)))
                moved += 1
                continue
            if is_data_entry(n):
                dest = os.path.join(FILES_DIR, n)
                if os.path.exists(dest):
                    dest = _free_path(dest)
                move_file(src, dest)
                moved += 1
        try:
            # vaciar restos y borrar carpeta legada si queda vacía
            for n in list(os.listdir(OLD_DATA_DIR)):
                p = os.path.join(OLD_DATA_DIR, n)
                if os.path.isdir(p):
                    shutil.rmtree(p, ignore_errors=True)
                else:
                    os.remove(p)
            os.rmdir(OLD_DATA_DIR)
        except OSError as _ign:
            ignore("migrate_legacy_dlpy_data", _ign)
        if moved:
            m_ok(f"Migración lista: {moved} elemento(s)")
        else:
            m_info("dlpy_data estaba vacío; eliminado.")
    except Exception as e:
        m_warn(f"Migración parcial de dlpy_data: {e}")


def tidy_data():
    """Ordena FILES_DIR: carpetas de versión y scripts sueltos → backups/."""
    moved = 0
    try:
        if not os.path.isdir(FILES_DIR):
            return
        for n in sorted(os.listdir(FILES_DIR)):
            p = os.path.join(FILES_DIR, n)
            if os.path.isdir(p) and VER_DIR_RE.match(n):
                os.makedirs(BACKUP_DIR, exist_ok=True)
                move_file(p, _free_path(os.path.join(BACKUP_DIR, n)))
                moved += 1
        if os.path.isdir(BACKUP_DIR):
            for n in sorted(os.listdir(BACKUP_DIR)):
                m = re.match(r"^dlpy_(\d+\.\d+\.\d+)(-\d+)?\.py$", n)
                p = os.path.join(BACKUP_DIR, n)
                if m and os.path.isfile(p):
                    dest = _free_path(os.path.join(BACKUP_DIR, m.group(1) + (m.group(2) or "")))
                    os.makedirs(dest)
                    move_file(p, os.path.join(dest, f"dlpy_{m.group(1)}.py"))
                    moved += 1
    except Exception as e:
        m_warn(f"No se pudo ordenar dlpy_files: {e}")
    if moved:
        m_ok(f"dlpy_files ordenada: {moved} elemento(s) movido(s) a backups/")


def archive_previous(prev, snapshot_version, announce=True):
    """Todo lo de la versión anterior va a backups/<prev>/ (script, changelog, datos)."""
    has_script = os.path.isfile(SNAPSHOT_FILE) and snapshot_version == prev
    has_data = files_data_present()
    if not has_script and not has_data:
        if announce:
            m_info("No hay copia del script anterior (se guardará una desde esta versión).")
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
    m_ok(f"Versión {prev} archivada en backups/{os.path.basename(dest)}/")
    return True


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


def downgrade_notice(stored):
    """Avisa de la bajada `stored` → VERSION y devuelve su registro (sin escribirlo a disco)."""
    rec = make_downgrade_record(stored, VERSION, load_json(DOWNGRADE_FILE).get("pending"))
    m_warn(f"Bajada de versión: {stored} → {VERSION}")
    note({"manual": "Instalada a propósito desde --versiones.",
          "recuperacion": "Recuperada tras un fallo.",
          "externa": "El dlpy.py se reemplazó por uno más viejo fuera de DLpy "
                     "(copia manual, atajo o copia antigua)."}[rec["causa"]])
    if rec["salto"] == "mayor":
        note(f"Cambió el número mayor: los datos guardados por la {stored} pueden no ser "
             f"compatibles con la {VERSION}.")
    return rec


def downgrade_commit(rec):
    """Guarda `rec` en el historial (últimas 20) y descarta la bajada pendiente."""
    try:
        hist = load_json(DOWNGRADE_FILE).get("history")
        hist = [h for h in hist if isinstance(h, dict)] if isinstance(hist, list) else []
        os.makedirs(STATE_DIR, exist_ok=True)
        save_json(DOWNGRADE_FILE, {"history": (hist + [rec])[-20:]})
    except Exception as _ign:
        ignore("downgrade_commit", _ign)


def check_version():
    migrate_legacy_dlpy_data()
    tidy_data()
    state = load_json(VERSION_FILE)
    stored = state.get("version")

    if stored == VERSION:
        if not os.path.isfile(SNAPSHOT_FILE):
            save_snapshot()
            save_json(VERSION_FILE, {"version": VERSION, "snapshot_version": VERSION})
        elif state.get("snapshot_version") == VERSION:
            _TEXT_CACHE.clear()               # misma versión: ¿igual que la copia guardada?
            snap = {"origin": "backup", "ref": SNAPSHOT_FILE, "sha": None, "label": "copia guardada"}
            me = {"origin": "instalada", "ref": SCRIPT_PATH, "sha": None, "label": "instalada"}
            if compare_sources(snap, me) == "distinto":
                add, rem = diff_counts(diff_lines(source_text(snap), source_text(me),
                                                  "copia guardada", "instalada"))
                if GITHUB_SAME["igual"]:
                    # idéntica a GitHub: la copia guardada es la vieja; se reemplaza (y dev_sync_version
                    # refresca después Documents/dlpy_<versión>.py desde ella)
                    save_snapshot()
                    m_ok(f"La {VERSION} instalada es idéntica a GitHub: copia guardada reemplazada "
                         f"(-{rem} +{add} líneas).")
                else:
                    m_warn(f"La {VERSION} instalada difiere de la copia guardada (-{rem} +{add} líneas): "
                           f"se editó sin subir la versión.")
            _TEXT_CACHE.clear()
        if changelog_pending():          # misma versión pero el .py trae changelog
            extract_changelog()
        publish_changelog_to_files()
        return True

    # ── Actualización (o primera instalación) ──
    prev = stored or "0.0.0"
    down = None
    if version_move(stored, VERSION) == "baja":
        down = downgrade_notice(stored)
    elif stored:
        m_info(f"Actualización detectada: {stored} → {VERSION}")
    if not archive_previous(prev, state.get("snapshot_version"), announce=bool(stored)):
        extract_changelog()      # el changelog sale del .py aunque falle el backup (snapshot intacto)
        return False

    save_snapshot()          # copia completa (con changelog) para futuros backups
    extract_changelog()      # changelog.md y limpieza del .py
    save_json(VERSION_FILE, {"version": VERSION, "snapshot_version": VERSION})
    if down:
        downgrade_commit(down)
    return True


# ───────────────────── DEV: snapshot a Documents (a-Shell) ─────────────────────
VER_FILE_RE = re.compile(r"^dlpy_(\d+\.\d+\.\d+)\.py$")
RUNNING_FILE = os.path.join(STATE_DIR, "running.json")      # ejecución en curso
CRASH_FILE = os.path.join(STATE_DIR, "crash.json")          # último fallo
CRASH_LOG_FILE = os.path.join(STATE_DIR, "crash_log.json")  # historial de fallos (con huella del código)
RECOVERED_FILE = os.path.join(STATE_DIR, "recovered.json")  # versión recuperada tras un fallo
GOOD_FILE = os.path.join(STATE_DIR, "good_versions.json")   # versiones que ya terminaron bien


def dev_copy_to_documents(text, home=None, script_path=None, version=None):
    """Copia `text` a ~/Documents/dlpy_<versión>.py. ('copiada'|'igual'|'mismo'|'error', ruta):
    'mismo' = ese archivo es el propio script en ejecución (no se pisa)."""
    dest = os.path.join(home or HOME, "Documents", f"dlpy_{version or VERSION}.py")
    try:
        me = script_path or SCRIPT_PATH
        if os.path.abspath(dest) == os.path.abspath(me) or (
                os.path.exists(dest) and os.path.exists(me) and os.path.samefile(dest, me)):
            return "mismo", dest
        if os.path.isfile(dest) and read_text(dest) == text:
            return "igual", dest
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        write_text(dest, text)
        return "copiada", dest
    except (OSError, ValueError) as e:
        ignore("dev_copy_to_documents", e)
        return "error", dest


def dev_sync_version():
    """Con DLPY_DEV=1 y solo en a-Shell (iOS): copia el snapshot actual (con su changelog)
    a ~/Documents/dlpy_<versión>.py. Sin DLPY_DEV, o en otra plataforma, no toca nada."""
    if not DEV:
        return
    if not IS_IOS:
        dbg("dev", f"snapshot a Documents/dlpy_{VERSION}.py: solo en a-Shell (iOS)")
        return
    try:
        src = SCRIPT_PATH
        if (os.path.isfile(SNAPSHOT_FILE)
                and load_json(VERSION_FILE).get("snapshot_version") == VERSION):
            src = SNAPSHOT_FILE
        text = read_text(src)
    except Exception as e:
        m_warn(f"DEV: no se pudo leer el script: {e}")
        return
    state, dest = dev_copy_to_documents(text)
    if state == "copiada":
        m_ok(f"DEV · snapshot {VERSION} copiado a Documents/dlpy_{VERSION}.py")
    elif state == "error":
        m_warn(f"DEV: no se pudo copiar el snapshot a Documents/dlpy_{VERSION}.py")
    else:
        dbg("dev", f"Documents/dlpy_{VERSION}.py {'ya está al día' if state == 'igual' else 'es este mismo script: no se copia'}")


# ───────────────────── Versiones en GitHub y en backups (listado) ─────────────────────
def github_repo_info(url=None):
    """(dueño, repo, rama) del enlace raw.githubusercontent.com de actualización, o None."""
    m = re.match(r"https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/", url or UPDATE_URL)
    return m.groups() if m else None


def parse_versions_listing(data, info):
    """[(versión, url_raw)] de la respuesta de la API de GitHub para versions/, de la más
    nueva a la más vieja. Ignora lo que no sea dlpy_x.y.z.py."""
    owner, repo, branch = info
    out = []
    for it in data if isinstance(data, list) else []:
        if not isinstance(it, dict):
            continue
        m = VER_FILE_RE.match(str(it.get("name") or ""))
        if m and it.get("type", "file") == "file":
            out.append((m.group(1), f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/versions/{it['name']}"))
    out.sort(key=lambda x: vtuple(x[0]), reverse=True)
    return out


def _listing_data(timeout=8, url=None):
    """(respuesta JSON de la API de GitHub para versions/, info) o (None, info) si falla."""
    info = github_repo_info(url)
    if not info:
        return None, None
    import urllib.request
    api = (f"https://api.github.com/repos/{info[0]}/{info[1]}/contents/versions"
           f"?ref={urllib.parse.quote(info[2])}")
    req = urllib.request.Request(api, headers={
        "User-Agent": "DLpy-updater", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r), info
    except Exception as _ign:
        ignore("remote_versions", _ign)
        return None, info


def parse_listing_shas(data):
    """{versión: hash git} de la respuesta de la API (sirve para comparar sin descargar)."""
    out = {}
    for it in data if isinstance(data, list) else []:
        if isinstance(it, dict):
            m = VER_FILE_RE.match(str(it.get("name") or ""))
            if m and it.get("sha"):
                out[m.group(1)] = str(it["sha"])
    return out


def remote_versions(timeout=8, url=None):
    """Versiones guardadas en versions/ del repositorio de GitHub, o None si no se pudo leer."""
    data, info = _listing_data(timeout, url)
    return parse_versions_listing(data, info) if data is not None else None


def remote_versions_full(timeout=8, url=None):
    """((versión, url) …, {versión: hash git}) de versions/ en GitHub, o None."""
    data, info = _listing_data(timeout, url)
    if data is None:
        return None
    return parse_versions_listing(data, info), parse_listing_shas(data)


def backup_versions():
    """[(versión, ruta)] de los backups que DLpy guarda solo al actualizar
    (dlpy_files/backups/<versión>/dlpy_<versión>.py). Sirven sin DLPY_DEV ni internet."""
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


def merge_versions(*sources):
    """Une listas [(versión, origen)]: una entrada por versión (gana la primera fuente
    que la tenga, p. ej. GitHub antes que los backups), de la más
    nueva a la más vieja."""
    seen = {}
    for lst in sources:
        for ver, src in lst or []:
            seen.setdefault(ver, src)
    return sorted(seen.items(), key=lambda x: vtuple(x[0]), reverse=True)


# ─────────── Comparar versiones: huellas y diferencias ───────────
def norm_text(text):
    """Texto con saltos de línea \\n (para comparar sin que CRLF cuente como cambio)."""
    return (text or "").replace("\r\n", "\n").replace("\r", "\n")


def has_changelog(text):
    return bool(CL_RE.search(norm_text(text)))


def strip_changelog(text):
    """El código sin el bloque CHANGELOG (el dlpy.py instalado ya no lo trae)."""
    t = norm_text(text)
    m = CL_RE.search(t)
    return t[:m.start()] + t[m.end():] if m else t


def text_fingerprints(text):
    """(huella del archivo completo, huella del código sin changelog), SHA-256."""
    import hashlib
    n = norm_text(text)
    return (hashlib.sha256(n.encode("utf-8")).hexdigest(),
            hashlib.sha256(strip_changelog(n).encode("utf-8")).hexdigest())


def git_blob_sha(data):
    """Hash que usa git (y la API de GitHub) para un archivo: sirve para saber si dos
    archivos son idénticos sin descargar el de GitHub."""
    import hashlib
    h = hashlib.sha1(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


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


ORIGIN_ORDER = ("github", "main", "backup", "instalada")
ORIGIN_LABEL = {"github": "GitHub", "main": "GitHub main",
                "backup": "backup", "instalada": "instalada"}
SELECTABLE = ("github", "main", "backup")      # la instalada no se «instala»
_TEXT_CACHE = {}


def collect_versions(gh=None, shas=None, main=None, backups=None, installed=None):
    """[{'ver', 'srcs': [{'origin', 'ref', 'sha', 'label'}]}] de la más nueva a la más
    vieja. Una misma versión junta TODOS sus orígenes (GitHub versions/, la de
    actualización `main`, backups e instalada) para poder compararlos."""
    table = {}

    def add(ver, origin, ref, sha=None, label=None):
        table.setdefault(ver, []).append(
            {"origin": origin, "ref": ref, "sha": sha, "label": label or ORIGIN_LABEL[origin]})

    for ver, ref in gh or []:
        add(ver, "github", ref, (shas or {}).get(ver))
    if main:
        add(main[0], "main", main[1], main[2] if len(main) > 2 else None)
    for ver, ref in sorted(backups or [], key=lambda x: os.path.basename(os.path.dirname(x[1]))):
        d = os.path.basename(os.path.dirname(ref))
        add(ver, "backup", ref, label="backup" + (("-" + d.split("-", 1)[1]) if "-" in d else ""))
    if installed:
        add(installed[0], "instalada", installed[1])
    return [{"ver": v, "srcs": sorted(table[v], key=lambda s: ORIGIN_ORDER.index(s["origin"]))}
            for v in sorted(table, key=vtuple, reverse=True)]


def fetch_raw_text(url, timeout=20):
    """Texto de `url` sin validarlo como script (sirve para comparar una versión rota)."""
    try:
        raw = fresh_bytes(url, timeout)
        if raw is None:
            return None
        return norm_text(raw.decode("utf-8"))
    except Exception as _ign:
        ignore("fetch_raw_text", _ign)
        return None


def source_text(src, timeout=20):
    """Texto de un origen (disco o GitHub), con caché; None si no se pudo leer."""
    ref = src["ref"]
    if ref not in _TEXT_CACHE:
        if ref.startswith("http"):
            _TEXT_CACHE[ref] = fetch_raw_text(ref, timeout)
        else:
            try:
                _TEXT_CACHE[ref] = norm_text(read_text(ref))
            except (OSError, ValueError) as _ign:
                ignore("source_text", _ign)
                _TEXT_CACHE[ref] = None
    return _TEXT_CACHE[ref]


def source_sha(src):
    """Hash git del origen si se conoce sin descargar (GitHub lo da; el local se calcula)."""
    if src.get("sha"):
        return src["sha"]
    if not src["ref"].startswith("http"):
        try:
            with open(src["ref"], "rb") as fh:
                src["sha"] = git_blob_sha(fh.read())
        except OSError as _ign:
            ignore("source_sha", _ign)
    return src.get("sha")


def compare_sources(a, b):
    """'igual' · 'changelog' · 'distinto', o None si alguno no se pudo leer. Primero
    compara hashes (sin descargar); solo si difieren lee los textos."""
    sa, sb = source_sha(a), source_sha(b)
    if sa and sb and sa == sb:
        return "igual"
    ta, tb = source_text(a), source_text(b)
    if ta is None or tb is None:
        return None
    return compare_texts(ta, tb)


def row_diffs(row):
    """[(origen_base, otro, estado)]: cada origen frente al primero de la versión."""
    srcs = row["srcs"]
    return [(srcs[0], s, compare_sources(srcs[0], s)) for s in srcs[1:]]


def row_state(diffs):
    """None (un solo origen) · 'distinto' · 'changelog' · '?' · 'igual'."""
    st = [d[2] for d in diffs]
    if not st:
        return None
    for k in ("distinto", "changelog"):
        if k in st:
            return k
    return "?" if None in st else "igual"


def group_sources(srcs):
    """Agrupa los orígenes instalables y legibles de una versión por contenido idéntico
    (huella completa: el changelog también cuenta). [[src, ...], ...], GitHub primero."""
    groups = []
    for s in srcs:
        if s["origin"] not in SELECTABLE or source_text(s) is None:
            continue
        for g in groups:
            if compare_sources(g[0], s) == "igual":
                g.append(s)
                break
        else:
            groups.append([s])
    return groups


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


def print_diff(a_text, b_text, label_a, label_b, mode="distinto", limit=24):
    """Muestra con colores qué cambia: rojo = lo del primero, verde = lo del segundo."""
    lines = diff_lines(a_text, b_text, label_a, label_b, mode)
    add, rem = diff_counts(lines)
    what = "código" if mode == "distinto" else "changelog"
    print(paint(f"{label_a} vs {label_b} · {what}: ", "bold")
          + paint(f"-{rem} ", "red") + paint(f"+{add}", "mint"))
    w = term_width() - 1
    for ln in lines[:limit]:
        if ln.startswith(("---", "+++")):
            print(paint(ln[:w], "gray"))
        elif ln.startswith("@@"):
            print(paint(ln[:w], "orange"))
        elif ln.startswith("-"):
            print(paint(ln[:w], "red"))
        elif ln.startswith("+"):
            print(paint(ln[:w], "mint"))
        else:
            print(paint(ln[:w], "gray"))
    if len(lines) > limit:
        note(f"… +{len(lines) - limit} líneas más")
    print(paint(f"- {label_a}", "red") + "   " + paint(f"+ {label_b}", "mint"))


# ───────────────────── Fallos: historial y avisos ─────────────────────
# Fallos: historial en state/crash_log.json (crash.json solo guardaba el último)
def load_crashes():
    """[{version, code, error, time}] de todos los fallos guardados (más viejo primero).
    `code` = huella del código que falló (None si no se pudo calcular o es de 0.0.1)."""
    log = load_json(CRASH_LOG_FILE).get("crashes")
    out = [c for c in log if isinstance(c, dict) and c.get("version")] if isinstance(log, list) else []
    last = load_json(CRASH_FILE)                     # 0.0.1: solo el último
    if last.get("version") and not any(
            c.get("version") == last["version"] and c.get("time") == last.get("time") for c in out):
        out.append({"version": last["version"], "code": None,
                    "error": last.get("error") or "", "time": last.get("time") or 0})
    return out


def crashes_json_path():
    """Ruta del JSON de fallos para el usuario: ~/Documents/crashes_dlpy.json en a-Shell (iOS),
    o DLPY_CRASHES_JSON si se define. None si no aplica."""
    custom = os.environ.get("DLPY_CRASHES_JSON", "").strip()
    if custom:
        return os.path.expanduser(custom)
    docs = os.path.join(HOME, "Documents")
    return os.path.join(docs, "crashes_dlpy.json") if IS_IOS and os.path.isdir(docs) else None


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


# ───────────────────── Pantalla de versiones y orígenes ─────────────────────
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


def format_version_rows(rows, cur, upd, crashes, diffs_by_ver, width=None):
    """Líneas de la lista numerada de versiones (con colores si el terminal los admite)."""
    width = width or safe_width()
    count = {}
    for c in crashes:
        count[c["version"]] = count.get(c["version"], 0) + 1
    out = []
    for i, row in enumerate(rows, 1):
        ver = row["ver"]
        head = f"{i}  {ver}"
        toks = [(head, paint(str(i), "orange", True) + "  " + paint(ver, "white", True))]
        for s in row["srcs"]:
            toks.append((s["label"], paint(s["label"], "orange" if s["origin"] in ("github", "main") else "gray")))
        out += _wrap_tokens(toks, 2, width, " · ")
        flags = []
        if ver == cur:
            flags.append(("✓ actual", "green"))
        if upd and ver == upd:
            flags.append(("⬆ la de actualizar", "orange"))
        if ver in count:
            n = count[ver]
            flags.append(("✖ crasheó" + (f" ×{n}" if n > 1 else ""), "red"))
        diffs = diffs_by_ver.get(ver) or []
        st = row_state(diffs)
        if st == "igual":
            flags.append(("= idénticas", "green"))
        for a, b, e in diffs:
            if e == "distinto":
                flags.append((f"≠ {a['label']} vs {b['label']}: código", "yellow"))
            elif e == "changelog":
                flags.append((f"≠ {a['label']} vs {b['label']}: changelog", "yellow"))
            elif e is None:
                flags.append((f"? {a['label']} vs {b['label']}", "dim"))
        out += _wrap_tokens([(t, paint(t, c)) for t, c in flags], 6, width)
    return out


def print_version_legend():
    note("✓ actual · ⬆ la de actualizar · ✖ crasheó · ≠ difiere · = idénticas")


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


def pick_source(row):
    """Origen a instalar de una versión. Si GitHub y un backup tienen archivos
    DISTINTOS enseña qué cambia y pregunta de cuál; si son iguales no pregunta
    (gana GitHub, luego backup). None = cancelar / sin origen."""
    groups = group_sources(row["srcs"])
    if not groups:
        m_err(f"La {row['ver']} no se pudo leer en ningún origen.")
        return None
    if len(groups) == 1:
        return groups[0][0]
    ver = row["ver"]
    m_warn(f"La {ver} no es igual en todos los sitios:")
    base_text = source_text(groups[0][0])
    for g in groups[1:3]:
        mode = compare_texts(base_text, source_text(g[0]))
        print_diff(base_text, source_text(g[0]), groups[0][0]["label"], g[0]["label"], mode)
    shown = groups[:9]
    for n, g in enumerate(shown, 1):
        print(" " + paint(f"{n}", "orange", True) + "  " + " · ".join(s["label"] for s in g))
    cur = f"¿De dónde instalar la {ver}? Número (Enter = cancelar) ▸ "
    while True:
        try:
            ans = ask_line(cur)
        except (EOFError, KeyboardInterrupt):
            return None
        n = parse_menu_choice(ans, len(shown))
        if n is None:
            cur = retry_prompt(cur, ans, bad_prompt(f"1-{len(shown)} o Enter"),
                               f"Escribe un número de 1 a {len(shown)} (o Enter para cancelar).")
            continue
        return shown[n - 1][0] if n else None


def origins_row(ver, main_text=None, with_installed=None, github=True, backups=True):
    """Fila con TODOS los orígenes de `ver`: la de actualización (`main`, si se da su
    texto), versions/ de GitHub, backups y la instalada (si es la actual).
    Es la misma fila y la misma comparación que usa la lista de versiones."""
    _TEXT_CACHE.clear()
    full = remote_versions_full(timeout=6) if github else None
    gh, shas = full if full else ([], {})
    main = None
    if main_text:
        _TEXT_CACHE[UPDATE_URL] = main_text
        main = (ver, UPDATE_URL, git_blob_sha(main_text.encode("utf-8")))
    inst = (VERSION, SCRIPT_PATH) if (ver == VERSION if with_installed is None else with_installed) else None
    rows = collect_versions([x for x in gh if x[0] == ver], shas, main,
                            [x for x in backup_versions() if x[0] == ver] if backups else [], inst)
    return rows[0] if rows else {"ver": ver, "srcs": []}


def report_row(row, show_diff=True):
    """Cuenta cómo salió la comparación de los orígenes de una versión (igual que la
    lista): idénticas, solo changelog o código distinto (con el diff en colores).
    Devuelve row_state."""
    ver = row["ver"]
    diffs = row_diffs(row)
    st = row_state(diffs)
    labels = " · ".join(s["label"] for s in row["srcs"])
    shown_hint = False
    if st == "igual":
        m_check(f"{ver} · {labels}: idénticas")
    elif st is None:
        note(f"La {ver} solo está en {labels}: no hay con qué compararla.")
    for a, b, e in diffs:
        if e in ("distinto", "changelog"):
            add, rem = diff_counts(diff_lines(source_text(a), source_text(b), a["label"], b["label"], e))
            m_warn(f"{ver} · {a['label']} ≠ {b['label']} "
                   f"({'código distinto' if e == 'distinto' else 'solo cambia el changelog'}: -{rem} +{add} líneas)")
            if show_diff:
                print_diff(source_text(a), source_text(b), a["label"], b["label"], e, limit=12)
            else:
                shown_hint = True
        elif e is None:
            note(f"{ver} · no se pudo comparar {a['label']} con {b['label']}.")
    if shown_hint:
        note("Diff con colores: --versiones y elige esa versión.")
    return st


# ───────────────────── Recuperación tras un fallo ─────────────────────
def skip_update_after_recovery(remote, crashed, match=None):
    """True si la versión de GitHub es la que falló (o más vieja que ella): no se ofrece.
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
    if a.isdigit() and 1 <= int(a) <= n:
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
    sync_origin_copy(text)
    if version_move(VERSION, ver) == "baja":          # downgrade a propósito: lo anota check_version al arrancar
        mark_downgrade_pending(VERSION, ver, "recuperacion" if crashed else "manual", hold)
    if crashed and hold:
        try:
            save_json(RECOVERED_FILE, {"crashed": crashed, "restored": ver, "time": int(time.time())})
        except Exception as _ign:
            ignore("install_recovered", _ign)
    return True


def offer_recovery(crashed, why):
    """Lista TODAS las versiones (GitHub versions/, la de actualización, backups
    y la instalada) marcando actual, la que instalaría al actualizar, fallos y
    diferencias entre orígenes de una misma versión, y deja elegir una. Si se instala,
    la ejecuta y termina (SystemExit). False si no se hizo nada.
    `crashed` = versión que falló (None en modo manual con --versiones)."""
    _TEXT_CACHE.clear()
    cbar = Bar()
    cbar.start("Buscando versiones")
    try:
        full = remote_versions_full()
        main_text = fetch_remote_script(timeout=8)
    finally:
        cbar.stop()
    remote, shas = full if full else (None, {})
    main_ver = remote_script_version(main_text)
    main = None
    if main_ver:
        _TEXT_CACHE[UPDATE_URL] = main_text
        main = (main_ver, UPDATE_URL, git_blob_sha(main_text.encode("utf-8")))
    backups = backup_versions()
    if remote is None and backups:
        m_warn("No se pudo leer GitHub: uso las versiones guardadas en este equipo.")
    rows = collect_versions(remote, shas, main, backups, (VERSION, SCRIPT_PATH))
    if not any(s["origin"] in SELECTABLE for r in rows for s in r["srcs"]):
        m_warn("No hay versiones guardadas para recuperar (versions/ de GitHub o backups).")
        return False
    shown = rows[:20]
    cbar = Bar()
    cbar.start("Comparando versiones")
    try:
        diffs_by_ver = {r["ver"]: row_diffs(r) for r in shown}
    finally:
        cbar.stop()
    header("VERSIONES")
    if why:
        m_warn(why)
    if main is None:
        note("Sin conexión: no se sabe cuál usaría al actualizar.")
    for ln in format_version_rows(shown, VERSION, main_ver, load_crashes(), diffs_by_ver):
        print(ln)
    if len(rows) > len(shown):
        note(f"(+{len(rows) - len(shown)} más antiguas sin mostrar)")
    print_version_legend()
    cur = "¿Instalar alguna? Número (Enter = no) ▸ "
    while True:
        try:
            ans = ask_line(cur)
        except (EOFError, KeyboardInterrupt):
            return False
        n = parse_menu_choice(ans, len(shown))
        if n is None:
            cur = retry_prompt(cur, ans, bad_prompt(f"1-{len(shown)} o Enter"),
                               f"Escribe un número de 1 a {len(shown)} (o Enter para no volver).")
            continue
        break
    if n == 0:
        return False
    row = shown[n - 1]
    ver = row["ver"]
    src = pick_source(row)                    # pregunta GitHub/local solo si difieren
    if not src:
        return False
    text = install_text(src, ver)
    if not text:
        m_err(f"No se pudo obtener la {ver} (descarga fallida o archivo no válido).")
        return False
    try:
        if text_fingerprints(text)[1] == text_fingerprints(read_text(SCRIPT_PATH))[1]:
            m_info(f"La {ver} de {src['label']} es idéntica a la instalada; no hay nada que cambiar.")
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
    m_check(f"DLpy {ver} · restaurada ({src['label']})")
    if not crashed and down:
        if stay:
            note(f"Bajaste de la {VERSION} a la {ver}. No se ofrecerá actualizar hasta que GitHub tenga una "
                 f"versión más nueva que la {VERSION}; con --actualizar puedes volver a instalarla.")
        else:
            note(f"Bajaste de la {VERSION} a la {ver}. En el próximo arranque se volverá a ofrecer "
                 f"actualizar.")
    if crashed:
        if stay:
            note(f"Se recuperó la {ver} porque la {crashed} falló. Mientras GitHub no tenga una versión "
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
    guardada. --selftest / --sistema / --2shortcuts no se vigilan."""
    import traceback
    args = sys.argv[1:]
    if "--selftest" in args or "--sistema" in args or wants_2shortcuts(args):
        return entry()
    if "--versiones" in args:                # lista manual, sin que haya fallado nada
        clear_screen()
        offer_recovery(None, None)
        return 0
    nested = getattr(sys, "_dlpy_guarded", False)     # tras actualizar/restaurar (runpy)
    global NESTED_IOS
    NESTED_IOS = bool(nested and IS_IOS)
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


# ───────────────────── Caché de streams (24 h) ─────────────────────
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
        if DEBUG or not IS_IOS:
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


# ─────────────────── Reanudación de descargas ───────────────────
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


# ───────────────────── Limpieza de la carpeta interna ─────────────────────
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


# ───────────────────── Entrega del archivo (iOS, Android y escritorio) ─────────────────────
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


def termux_run(args, timeout=8):
    """Ejecuta un comando de Termux:API sin que pueda colgar el script."""
    import subprocess
    try:
        r = subprocess.run(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True, timeout=timeout)
        return r.stdout if r.returncode == 0 else None
    except Exception as _ign:
        ignore("termux_run", _ign)
        return None


def android_open(final):
    """Abre el archivo con la app de Android que lo reproduzca (termux-open).
    Devuelve True si el sistema aceptó abrirlo."""
    import mimetypes
    exe = shutil.which("termux-open")
    if not exe:
        m_warn("No se puede abrir solo: falta termux-open (pkg install termux-tools).")
        return False
    mime = mimetypes.guess_type(final)[0]
    tries = []
    if mime:
        tries.append([exe, "--view", "--content-type", mime, final])
    tries.append([exe, final])
    for cmd in tries:
        dbg("abrir android", cmd)
        if termux_run(cmd, timeout=10) is not None:
            return True
    return False


def deliver_android(final, title):
    """Equivalente Android del Atajo: el archivo ya está en su carpeta final;
    se avisa la ruta, se registra en la galería, se notifica y se abre."""
    shown = final.replace(HOME, "~", 1) if final.startswith(HOME) else final
    dbg("entrega android", {"archivo": final, "titulo": title})
    m_ok(f"Guardado en: {shown}")
    if shutil.which("termux-media-scan"):
        termux_run(["termux-media-scan", final])
    if shutil.which("termux-notification"):
        termux_run(["termux-notification", "--id", "dlpy", "--title", "DLpy · descarga lista",
                    "--content", str(title)[:120],
                    "--action", "termux-open " + shlex.quote(final)])
    action = delivery_action()
    if action == "share" and shutil.which("termux-share"):
        termux_run(["termux-share", "-a", "send", final], timeout=10)
    elif action in ("none", "no", "0", "off", "false"):
        return
    elif action != "share":
        if android_open(final):
            m_info("Abriendo en Android...")
        else:
            m_warn("No se pudo abrir el archivo solo.")
            note("Si Termux estaba en segundo plano: Ajustes ▸ Apps ▸ Termux ▸ "
                 "Mostrar sobre otras apps. También puedes tocar la notificación.")


def has_display():
    """¿Hay un entorno gráfico donde abrir archivos y notificar?"""
    if IS_WINDOWS or IS_MAC:
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def delivery_action():
    """open (por defecto), share o none. DLPY_ANDROID_ACTION se sigue aceptando."""
    return (os.environ.get("DLPY_ACTION") or os.environ.get("DLPY_ANDROID_ACTION")
            or "open").strip().lower()


def desktop_open(path, reveal=False):
    """Abre `path` con la app por defecto (o su carpeta con reveal=True).
    Devuelve (True, "") o (False, motivo)."""
    import subprocess
    if IS_WINDOWS:
        try:
            if reveal:
                subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
            else:
                os.startfile(path)                     # noqa: P204 (solo existe en Windows)
            return True, ""
        except (OSError, AttributeError) as e:
            return False, str(e)
    if IS_MAC:
        cmd = ["open", "-R", path] if reveal else ["open", path]
    else:
        if not has_display():
            return False, "no hay pantalla gráfica (SSH o servidor)"
        exe = shutil.which("xdg-open") or (shutil.which("wslview") if is_wsl() else None)
        if not exe:
            return False, "falta xdg-open (paquete xdg-utils)"
        cmd = [exe, os.path.dirname(path) if reveal else path]
    dbg("abrir escritorio", cmd)
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, start_new_session=True)
    except OSError as e:
        return False, str(e)
    try:
        code = proc.wait(timeout=1.5)         # si sigue vivo, la app ya se abrió
    except subprocess.TimeoutExpired:
        return True, ""
    return (code == 0), ("el sistema devolvió código %s" % code if code else "")


def desktop_notify(title, text):
    """Notificación del escritorio si el sistema la ofrece. True si se envió."""
    import subprocess
    title, text = str(title)[:120], str(text)[:200]
    if IS_MAC and shutil.which("osascript"):
        def q(s):
            return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
        return termux_run(["osascript", "-e",
                           f"display notification {q(text)} with title {q(title)}"]) is not None
    if IS_LINUX and has_display() and shutil.which("notify-send"):
        return termux_run(["notify-send", title, text]) is not None
    if IS_WINDOWS:
        ps = shutil.which("powershell") or shutil.which("pwsh")
        if not ps:
            return False
        script = ("Add-Type -AssemblyName System.Windows.Forms,System.Drawing;"
                  "$n=New-Object System.Windows.Forms.NotifyIcon;"
                  "$n.Icon=[System.Drawing.SystemIcons]::Information;$n.Visible=$true;"
                  "$n.ShowBalloonTip(5000,$env:DLPY_N_T,$env:DLPY_N_B,"
                  "[System.Windows.Forms.ToolTipIcon]::Info);Start-Sleep 6;$n.Dispose()")
        try:
            subprocess.Popen([ps, "-NoProfile", "-WindowStyle", "Hidden", "-Command", script],
                             env={**os.environ, "DLPY_N_T": title, "DLPY_N_B": text},
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            return True
        except OSError as _ign:
            ignore("desktop_notify", _ign)
    return False


def deliver_desktop(final, title):
    """Equivalente de escritorio del Atajo / Termux: el archivo ya está en su carpeta
    final; se avisa la ruta, se notifica y se abre con la app por defecto."""
    shown = final.replace(HOME, "~", 1) if final.startswith(HOME) and not IS_WINDOWS else final
    dbg("entrega escritorio", {"archivo": final, "titulo": title, "modo": PLATFORM})
    m_ok(f"Guardado en: {shown}")
    desktop_notify("DLpy · descarga lista", title)
    action = delivery_action()
    if action in ("none", "no", "0", "off", "false"):
        return
    ok, why = desktop_open(final, reveal=(action == "share"))
    if ok:
        m_info("Abriendo la carpeta..." if action == "share" else "Abriendo con la app por defecto...")
    else:
        m_info("No se abrió solo" + (f": {why}" if why else "") + ".")


def deliver(final, title):
    """Entrega el archivo (Atajos / app por defecto) y anota la hora en el índice."""
    _deliver_platform(final, title)
    mark_delivered(final)


def _deliver_platform(final, title):
    if IS_ANDROID:
        return deliver_android(final, title)
    if IS_DESKTOP:
        return deliver_desktop(final, title)
    path = unique_path(final)
    m_info(f"Enviando a {SHORTCUT_NAME}...")
    dbg("entrega", {"origen": final, "copia": path, "titulo": title})
    os.system("open " + shlex.quote(shortcut_run_url({"file_path": path, "file_title": title})))


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
    except Exception as _ign:
        ignore("mark_delivered", _ign)


def reopen_question():
    """Texto de la pregunta «¿Abrir otra vez…?» según la plataforma."""
    return (f"¿Abrir otra vez con Atajos? (S/n) ▸ " if IS_IOS
            else "¿Abrir otra vez el archivo? (S/n) ▸ ")


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


# ───────────────────── Atajo de iOS (--2shortcuts) ─────────────────────
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


def send_code_to_shortcut():
    """`--2shortcuts` (iOS): manda el dlpy.py actual al atajo, que lo reconoce por la
    primera línea (#!dlpy.py). Pregunta si va con o sin changelog."""
    if not IS_IOS:
        m_warn("--2shortcuts solo aplica en iOS (a-Shell): usa tu atajo de Atajos.")
        return 1
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
        m_warn("No se pudo usar el portapapeles; el código va dentro del enlace.")
        url = shortcut_text_url(code)
    dbg("2shortcuts", {"bytes": len(code.encode("utf-8")), "con_changelog": how, "url": url[:80]})
    os.system("open " + shlex.quote(url))
    return 0


# ───────────── Análisis tolerante (equivalente al yt-dlp en bruto) ─────────────
# Opciones de la CLI que no deben heredarse (las controla este script).
_CLI_DROP = ("postprocessors", "postprocessor_args", "paths", "logger", "progress_hooks",
             "postprocessor_hooks", "simulate", "skip_download", "listformats",
             "list_thumbnails", "forcejson", "dump_single_json", "dumpjson", "outtmpl",
             "format", "quiet", "no_warnings", "verbose", "noprogress", "consoletitle",
             "overwrites", "continuedl", "merge_output_format", "allow_multiple_audio_streams",
             "extract_flat", "playlist_items", "load_info_filename", "writeinfojson")


# ─────────────────── Error «no eres un bot» ───────────────────
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


def probe_cli_json(link, extra):
    """Último recurso: ejecutable yt-dlp en bruto (-J). Devuelve el info o None."""
    exe = shutil.which("yt-dlp")
    if not exe:
        dbg("yt-dlp en bruto", "no hay ejecutable yt-dlp")
        return None
    import subprocess
    try:
        r = subprocess.run([exe, "-J", "--no-playlist", "--no-warnings"] + list(extra) + [link],
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True, timeout=180)
        if r.returncode != 0 or not r.stdout.strip():
            dbg("yt-dlp en bruto falló", (r.stderr or "").strip()[-400:])
            return None
        return json.loads(r.stdout)
    except Exception as e:
        dbg("yt-dlp en bruto falló", str(e))
        return None


def analyze_link(yt_dlp, link):
    """Devuelve (info, base_opts). Prueba varias formas de analizar el enlace y
    se queda con la primera que funcione; base_opts se reutiliza al descargar."""
    extra = user_argv()
    std = {"quiet": True, "no_warnings": True, "noplaylist": True, "socket_timeout": 20}
    if DEBUG:
        std.update({"quiet": False, "no_warnings": False, "verbose": True})
    stages = [
        ("biblioteca", lambda: (cli_like_opts(yt_dlp, extra) or {}) if extra else {}, True),
        ("equivalente a CLI", lambda: cli_like_opts(yt_dlp, ["--no-playlist"] + extra), True),
        ("CLI sin --no-playlist", lambda: cli_like_opts(yt_dlp, extra), False),
    ]
    last = None
    for i, (name, make, no_pl) in enumerate(stages):
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
                return info, base
        except KeyboardInterrupt:
            raise
        except Exception as e:
            last = e
            dbg("análisis falló", f"{name}: {e}")
            if is_bot_error(e):
                raise          # repetir el análisis no ayuda
    m_info("Reintentando análisis (yt-dlp en bruto)...")
    info = probe_cli_json(link, extra)
    if info:
        dbg("análisis", "funcionó: yt-dlp en bruto (-J)")
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


# ───────────────────────── Autoprueba ─────────────────────────
def selftest():
    """`python dlpy.py --selftest`: pruebas rápidas de funciones puras (sin disco ni red)."""
    import tempfile
    fails = []

    def check(nombre, obtenido, esperado):
        if obtenido != esperado:
            fails.append(nombre)
            print(f"✗ {nombre}: esperado {esperado!r}, obtenido {obtenido!r}")

    check("wrap no corta palabras", wrap_text("Otro video de YouTube que 'vas a ver después'. Spoiler: no.", 30),
          ["Otro video de YouTube que 'vas", "a ver después'. Spoiler: no."])
    check("wrap guiones enteros", wrap_text("uno 4K-HDR-Video dos", 12), ["uno", "4K-HDR-Video", "dos"])
    check("wrap palabra larga", wrap_text("x" * 20, 8), ["x" * 8, "x" * 8, "x" * 4])
    check("wrap emoji 2 columnas", all(dwidth(x) <= 10 for x in wrap_text("🫣 hola 🫣 mundo 🫣 otra vez", 10)), True)
    check("dwidth ansi", dwidth("\x1b[92m●\x1b[0m ab"), 4)
    check("pip args escritorio", pip_args("yt-dlp", no_deps=False), ["install", "-U", "yt-dlp"])
    check("pip args móvil", pip_args("yt-dlp", no_deps=True), ["install", "-U", "yt-dlp", "--no-deps"])
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
    check("vtuple normal", vtuple("1.10.2"), (1, 10, 2))
    check("vtuple fecha", vtuple("2025.01.05"), (2025, 1, 5))
    check("vtuple None", vtuple(None), ())
    check("vtuple orden", vtuple("1.10.0") > vtuple("1.9.9"), True)

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
    check("plat termux env", detect_platform({"TERMUX_VERSION": "0.118"}, "linux"), "android")
    check("plat termux prefix", detect_platform({"PREFIX": "/data/data/com.termux/files/usr"}, "linux"), "android")
    check("plat termux home", detect_platform({"HOME": "/data/data/com.termux/files/home"}, "linux"), "android")
    check("plat android sys", detect_platform({}, "android"), "android")
    check("plat a-shell", detect_platform({"APPNAME": "a-Shell"}, "darwin"), "ios")
    check("plat ios sys", detect_platform({}, "ios"), "ios")
    check("plat linux", detect_platform({}, "linux"), "linux")
    check("plat bsd", detect_platform({}, "freebsd14"), "linux")
    check("plat windows", detect_platform({}, "win32"), "windows")
    check("plat cygwin", detect_platform({}, "cygwin"), "windows")
    check("plat macos", detect_platform({"HOME": "/Users/ana"}, "darwin"), "macos")
    check("plat ios sandbox", detect_platform(
        {"HOME": "/private/var/mobile/Containers/Data/Application/AB12/Documents"}, "darwin"), "ios")
    check("plat forzada macos", detect_platform({"DLPY_PLATFORM": "macos"}, "linux"), "macos")
    check("plat forzada windows", detect_platform({"DLPY_PLATFORM": "Windows"}, "linux"), "windows")
    check("plat forzada inválida", detect_platform({"DLPY_PLATFORM": "beos"}, "linux"), "linux")
    check("nombre ios", platform_name("ios", {"APPNAME": "a-Shell-mini"}), "a-Shell mini · iOS")
    check("nombre android", platform_name("android", {"TERMUX_VERSION": "0.118"}), "Termux 0.118 · Android")
    check("nombre linux", platform_name("linux", {}), "Linux")
    check("nombre wsl", platform_name("linux", {"WSL_DISTRO_NAME": "Ubuntu"}), "Linux · WSL · Ubuntu")
    check("nombre macos", platform_name("macos", {}), "macOS")
    check("nombre windows", platform_name("windows", {}), "Windows")
    with tempfile.TemporaryDirectory() as _xd:
        os.makedirs(os.path.join(_xd, ".config"))
        with open(os.path.join(_xd, ".config", "user-dirs.dirs"), "w") as _f:
            _f.write('XDG_DOWNLOAD_DIR="$HOME/Descargas"\n')
        check("descargas linux xdg", desktop_downloads_dir("linux", {}, _xd), os.path.join(_xd, "Descargas"))
        check("descargas linux env", desktop_downloads_dir("linux", {"XDG_DOWNLOAD_DIR": "/x/d"}, _xd), "/x/d")
        check("descargas linux defecto", desktop_downloads_dir("linux", {}, _xd + "/otro"),
              os.path.join(_xd, "otro", "Downloads"))
        check("descargas macos", desktop_downloads_dir("macos", {}, _xd), os.path.join(_xd, "Downloads"))
        check("descargas windows", desktop_downloads_dir("windows", {}, _xd), os.path.join(_xd, "Downloads"))
    check("modo coherente", (IS_ANDROID, IS_IOS, IS_MAC, IS_LINUX, IS_WINDOWS).count(True), 1)
    check("modo apple", APPLE_MODE, PLATFORM in ("ios", "macos"))
    check("safe_name CON", safe_name("CON", windows=True), "_CON")
    check("safe_name nul.txt", safe_name("nul.txt", windows=True), "_nul.txt")
    check("safe_name com1", safe_name("com1", windows=True), "_com1")
    check("safe_name console ok", safe_name("console", windows=True), "console")
    check("safe_name CON fuera de windows", safe_name("CON", windows=False), "CON")
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
    check("plat forzada ios", detect_platform({"DLPY_PLATFORM": "ios", "TERMUX_VERSION": "1"}, "linux"), "ios")
    check("plat forzada android", detect_platform({"DLPY_PLATFORM": "android"}, "darwin"), "android")
    _sp = [("137", "mp4", 1000), ("140", "m4a", 50)]
    check("resume_key estable", resume_key("v", _sp), resume_key("v", list(_sp)))
    check("resume_key prefijo", resume_key("v", _sp).startswith(RESUME_PREFIX), True)
    check("resume_key otro formato", resume_key("v", _sp) != resume_key("v", [("136", "mp4", 1000), ("140", "m4a", 50)]), True)
    check("resume_key otro tamaño", resume_key("v", _sp) != resume_key("v", [("137", "mp4", 1001), ("140", "m4a", 50)]), True)
    check("resume_key otro video", resume_key("v", _sp) != resume_key("w", _sp), True)
    check("resume_key sin tamaño", resume_key("v", [("18", "mp4", None)]), resume_key("v", [("18", "mp4", 0)]))

    check("root_move_target fuera", root_move_target("/sdcard/Download/x.py", "/h/u"), "/h/u/dlpy.py")
    check("root_move_target raíz", root_move_target("/h/u/otro.py", "/h/u"), None)
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
    check("yn multilínea", yn_prompt("¿Mover (1 MB) a backups? (s/N) ▸ ", False), "¿Mover (1 MB) a backups? (s/N) ▸ ")
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
    # ── 0.0.1: recuperación y «abrir otra vez» ──
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
    _info = ("o", "r", "main")
    check("github_repo_info raw", github_repo_info("https://raw.githubusercontent.com/o/r/main/dlpy.py"), _info)
    check("github_repo_info otro host", github_repo_info("https://example.com/dlpy.py"), None)
    _listing = [{"name": "dlpy_0.7.5.py", "type": "file"}, {"name": "dlpy_0.7.10.py", "type": "file"},
                {"name": "README.md", "type": "file"}, {"name": "dlpy_0.7.4_abc1234.py", "type": "file"},
                {"name": "dlpy_0.7.3.py", "type": "dir"}, "basura"]
    check("listado versiones", parse_versions_listing(_listing, _info), [
        ("0.7.10", "https://raw.githubusercontent.com/o/r/main/versions/dlpy_0.7.10.py"),
        ("0.7.5", "https://raw.githubusercontent.com/o/r/main/versions/dlpy_0.7.5.py")])
    check("listado no lista", parse_versions_listing({"message": "Not Found"}, _info), [])
    check("menu vacío", parse_menu_choice("", 3), 0)
    check("menu n", parse_menu_choice(" N ", 3), 0)
    check("menu 2", parse_menu_choice("2", 3), 2)
    check("menu fuera de rango", parse_menu_choice("4", 3), None)
    check("menu texto", parse_menu_choice("hola", 3), None)
    check("abrupto versión nueva", should_offer_after_abrupt({"version": "0.7.6"}, ["0.7.5"]), True)
    check("abrupto versión buena", should_offer_after_abrupt({"version": "0.7.5"}, ["0.7.5"]), False)
    check("abrupto sin marca", should_offer_after_abrupt({}, []), False)
    check("merge_versions gana la primera", merge_versions([("0.7.5", "gh"), ("0.7.6", "gh")],
          [("0.7.5", "alt"), ("0.7.4", "alt")], None, [("0.7.4", "bk"), ("0.7.3", "bk")]),
          [("0.7.6", "gh"), ("0.7.5", "gh"), ("0.7.4", "alt"), ("0.7.3", "bk")])
    check("merge_versions vacío", merge_versions(None, []), [])
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
    # ── 0.0.1: changelog_block (cerrado, abierto y sin changelog) ──
    _cb = changelog_block("#!dlpy.py\n# ==== CHANGELOG ====\n# ## 1.0.0\n#\n# - a\n# ==== FIN CHANGELOG ====\nx = 1\n")
    check("changelog_block cerrado", (_cb[3], "# - a" in _cb[2]), (True, True))
    _src = "#!dlpy.py\n# ==== CHANGELOG ====\n# ## 1.0.0\n#\n# - a\n#   sigue\n# DLpy - desc\nVERSION = 1\n"
    _cb = changelog_block(_src)
    check("changelog_block abierto + comentarios", (_cb[3], _src[:_cb[0]] + _src[_cb[1]:]),
          (False, "#!dlpy.py\n# DLpy - desc\nVERSION = 1\n"))
    _src2 = "#!dlpy.py\n# ==== CHANGELOG ====\n# ## 1.0.0\n# - a\nprint(1)\n"
    _cb = changelog_block(_src2)
    check("changelog_block abierto + código", _src2[:_cb[0]] + _src2[_cb[1]:], "#!dlpy.py\nprint(1)\n")
    check("changelog_block sin changelog", changelog_block("#!dlpy.py\nprint(1)\n"), None)
    # ── 0.0.1: huellas, comparación de orígenes, fallos y copia a Documents ──
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
    check("git_blob_sha vacío", git_blob_sha(b""), "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391")
    check("git_blob_sha hello", git_blob_sha(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")
    check("listado shas", parse_listing_shas([{"name": "dlpy_0.7.5.py", "sha": "abc"},
          {"name": "x.txt", "sha": "d"}, {"name": "dlpy_0.7.4.py"}, "basura"]), {"0.7.5": "abc"})
    _rows = collect_versions([("0.7.7", "https://h/0.7.7"), ("0.7.6", "https://h/0.7.6")], {"0.7.7": "s1"},
                             ("0.7.8", "https://h/main", "s2"),
                             [("0.7.6", "/b/0.7.6/dlpy_0.7.6.py"), ("0.7.6", "/b/0.7.6-2/dlpy_0.7.6.py")],
                             ("0.7.7", "/me/dlpy.py"))
    check("collect orden", [r["ver"] for r in _rows], ["0.7.8", "0.7.7", "0.7.6"])
    check("collect orígenes 0.7.7", [s_["label"] for s_ in _rows[1]["srcs"]], ["GitHub", "instalada"])
    check("collect backups", [s_["label"] for s_ in _rows[2]["srcs"]], ["GitHub", "backup", "backup-2"])
    check("collect main", [s_["origin"] for s_ in _rows[0]["srcs"]], ["main"])
    check("row_state vacío", row_state([]), None)
    check("row_state peor gana", row_state([(0, 0, "igual"), (0, 0, "distinto")]), "distinto")
    check("row_state changelog", row_state([(0, 0, "igual"), (0, 0, "changelog")]), "changelog")
    check("row_state ?", row_state([(0, 0, None), (0, 0, "igual")]), "?")
    check("row_state igual", row_state([(0, 0, "igual")]), "igual")
    check("diff_counts", diff_counts(diff_lines("a\nb\n", "a\nc\nd\n", "x", "y")), (2, 1))
    with tempfile.TemporaryDirectory() as _td:
        _TEXT_CACHE.clear()
        _pa, _pb, _pc = (os.path.join(_td, n) for n in ("a.py", "b.py", "c.py"))
        write_text(_pa, _full)
        write_text(_pb, _full)
        write_text(_pc, _full.replace("print(1)", "print(2)"))
        _sa, _sb, _sc = ({"origin": o, "ref": r, "sha": None, "label": o} for o, r in
                         (("github", _pa), ("backup", _pb), ("main", _pc)))
        check("compare_sources igual", compare_sources(_sa, _sb), "igual")
        check("compare_sources distinto", compare_sources(_sa, _sc), "distinto")
        check("compare_sources ilegible", compare_sources(_sa, {"origin": "backup", "ref": os.path.join(_td, "no.py"),
              "sha": None, "label": "x"}), None)
        check("group_sources", [[s_["origin"] for s_ in g] for g in group_sources([_sa, _sb, _sc])],
              [["github", "backup"], ["main"]])
        check("group_sources ignora instalada", group_sources([dict(_sa, origin="instalada")]), [])
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
            check("fallo de crash.json (0.0.1)", crash_match("0.9.0", _full)[0], "sin_huella")
            check("historial", [c["version"] for c in load_crashes()], ["1.0.0", "1.0.2", "0.9.0"])
            _lines = format_version_rows(
                [{"ver": "1.0.0", "srcs": [dict(_sa, label="GitHub"), dict(_sc, label="backup")]}],
                "1.0.0", "1.0.0", load_crashes(), {"1.0.0": [(_sa, _sc, "distinto")]}, 80)
            _txt = "\n".join(_lines)
            check("lista marca actual", "✓ actual" in _txt, True)
            check("lista marca actualizar", "⬆ la de actualizar" in _txt, True)
            check("lista marca crasheó", "✖ crasheó" in _txt, True)
            check("lista marca difiere", "≠ github vs main: código" in _txt, True)
        finally:
            globals()["CRASH_LOG_FILE"], globals()["CRASH_FILE"] = _old_c
        # DEV: snapshot a Documents/dlpy_<versión>.py
        _home = os.path.join(_td, "home")
        _dd = os.path.join(_home, "Documents", f"dlpy_{VERSION}.py")
        check("docs copia", dev_copy_to_documents("x\n", _home, "/otro/dlpy.py")[0], "copiada")
        check("docs nombre con versión", dev_copy_to_documents("x\n", _home, "/otro/dlpy.py")[1], _dd)
        check("docs contenido", read_text(_dd), "x\n")
        check("docs igual", dev_copy_to_documents("x\n", _home, "/otro/dlpy.py")[0], "igual")
        check("docs cambia", dev_copy_to_documents("y\n", _home, "/otro/dlpy.py")[0], "copiada")
        check("docs otra versión", os.path.basename(dev_copy_to_documents("w\n", _home, "/otro/dlpy.py", "9.9.9")[1]),
              "dlpy_9.9.9.py")
        check("docs no pisa el propio script", dev_copy_to_documents("z\n", _home, _dd)[0], "mismo")
        check("docs propio intacto", read_text(_dd), "y\n")
    _TEXT_CACHE.clear()
    check("tras recuperar: mismo número otro código", skip_update_after_recovery("0.7.6", "0.7.6", "distinta"), False)
    check("tras recuperar: mismo número mismo código", skip_update_after_recovery("0.7.6", "0.7.6", "igual"), True)
    check("tras recuperar: más vieja aunque distinta", skip_update_after_recovery("0.7.5", "0.7.6", "distinta"), True)
    _sv = (globals()["remote_versions_full"], globals()["backup_versions"])
    _msgs = []
    _ov = {k: globals()[k] for k in ("m_check", "m_warn", "note", "print_diff")}
    try:
        globals()["remote_versions_full"] = lambda *a, **k: ([("9.9.9", "https://h/9.9.9")], {"9.9.9": "zz"})
        globals()["backup_versions"] = lambda *a, **k: []
        _r = origins_row("9.9.9", "#!dlpy.py\nx\n")
        check("origins_row nueva", [s_["label"] for s_ in _r["srcs"]], ["GitHub", "GitHub main"])
        check("origins_row instalada solo si es la actual", [s_["origin"] for s_ in origins_row(VERSION)["srcs"]], ["instalada"])
        for _k in ("m_check", "m_warn", "note"):
            globals()[_k] = (lambda k: lambda m: _msgs.append((k, m)))(_k)
        globals()["print_diff"] = lambda *a, **k: _msgs.append(("diff", a[2] + "|" + a[3]))
        _TEXT_CACHE.clear()
        _TEXT_CACHE.update({"https://h/9.9.9": "#!dlpy.py\nx\n", UPDATE_URL: "#!dlpy.py\nx\n"})
        _r["srcs"][0]["sha"] = "zz"
        _r["srcs"][1]["sha"] = "zz"
        check("report_row idénticas", (report_row(_r), _msgs[-1][0]), ("igual", "m_check"))
        _TEXT_CACHE[UPDATE_URL] = "#!dlpy.py\ny\n"
        _r["srcs"][1]["sha"] = "otro"
        _msgs.clear()
        check("report_row distinto", report_row(_r), "distinto")
        check("report_row dice qué difiere", [m for k, m in _msgs if k == "m_warn"],
              ["9.9.9 · GitHub ≠ GitHub main (código distinto: -1 +1 líneas)"])
        check("report_row muestra diff", [m for k, m in _msgs if k == "diff"], ["GitHub|GitHub main"])
        _msgs.clear()
        check("report_row un origen", report_row({"ver": "1.0.0", "srcs": _r["srcs"][1:]}), None)
        check("report_row un origen avisa", _msgs[-1][0], "note")
    finally:
        (globals()["remote_versions_full"], globals()["backup_versions"]) = _sv
        globals().update(_ov)
        _TEXT_CACHE.clear()
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
    _all = ["ffmpeg", "js", "termux-api"]
    _has = lambda *names: (lambda x: "/bin/" + x if x in names else None)
    check("sys_cmds android", system_install_cmds(_all, "android", _has("pkg")),
          [["pkg", "install", "-y", "ffmpeg", "nodejs", "termux-api"]])
    check("sys_cmds android sin pkg", system_install_cmds(_all, "android", _has()), None)
    check("sys_cmds macos", system_install_cmds(_all, "macos", _has("brew")),
          [["brew", "install", "ffmpeg", "deno"]])
    check("sys_cmds macos solo termux-api", system_install_cmds(["termux-api"], "macos", _has("brew")), None)
    check("sys_cmds windows", [c[3] for c in system_install_cmds(_all, "windows", _has("winget"))],
          ["Gyan.FFmpeg", "DenoLand.Deno"])
    check("sys_cmds linux dnf", system_install_cmds(_all, "linux", _has("dnf"), True),
          [["dnf", "install", "-y", "ffmpeg-free", "nodejs"]])
    check("sys_cmds linux apt sudo", system_install_cmds(["ffmpeg"], "linux", _has("apt-get", "sudo"), False),
          [["sudo", "apt-get", "install", "-y", "ffmpeg"]])
    check("sys_cmds linux sin sudo", system_install_cmds(["ffmpeg"], "linux", _has("apt-get"), False), None)
    check("sys_cmds ios", system_install_cmds(_all, "ios", _has("pkg", "brew")), None)
    with tempfile.TemporaryDirectory() as _td:
        _o = os.path.join(_td, "dlpy.py")
        check("origin_copy escribe", sync_origin_copy("#!dlpy.py\nx\n", _o, "/h/u/dlpy.py"), _o)
        check("origin_copy contenido", read_text(_o), "#!dlpy.py\nx\n")
        check("origin_copy mismo archivo", sync_origin_copy("x", _o, _o), None)
        check("origin_copy sin carpeta", sync_origin_copy("x", os.path.join(_td, "no", "dlpy.py"), "/h/u/dlpy.py"), None)
        check("origin_copy sin origen", sync_origin_copy("x", "", "/h/u/dlpy.py"), None)

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
    # Apple: opus no es nativo (gana m4a); resto: ambos valen y gana el de más bitrate
    check("auto_best audio", auto_best([a1, a2], [], set(), True), ("a", a1 if APPLE_MODE else a2))
    if not APPLE_MODE:
        vp = dict(v1, format_id="vp", ext="webm", vcodec="vp9", acodec="none", height=1080, tbr=3000)
        h2 = dict(v1, format_id="h2", acodec="none", height=1080, tbr=2000)
        check("auto_best h264", auto_best([], [vp, h2], set(), True)[1]["format_id"], "h2")

    for txt in ("unable to download video data: http error 403: forbidden",
                "requested format is not available", "http error 410: gone"):
        check("reintento sí: " + txt[:25], bool(_RETRY_RE.search(txt)), True)
    for txt in ("unable to download https://x.com/v/14032?id=4103",
                "http error 404: not found", "http error 4030"):
        check("reintento no: " + txt[:25], bool(_RETRY_RE.search(txt)), False)

    # 0.2.4: líneas uniformes y animaciones
    check("count_text entero", count_text("48 MB", 0.5), "24 MB")
    check("count_text decimal", count_text("3.0 MB", 0.5), "1.5 MB")
    check("count_text sin número", count_text("?", 0.5), "?")
    check("count_text tope", count_text("48 MB", 3), "48 MB")
    check("título 2 líneas", len(title_lines("palabra " * 40, 30)), 2)
    check("título termina en …", title_lines("palabra " * 40, 30)[1].endswith("…"), True)
    check("título corto igual", title_lines("Hola mundo", 30), ["Hola mundo"])
    check("ventana todas", visible_start(10, 10), 0)
    check("ventana últimas", visible_start(10, 4), 6)
    check("ventana con ★ oculta", visible_start(10, 4, 2), 2)
    check("ventana con ★ visible", visible_start(10, 4, 8), 6)
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
    print(f"Autoprueba: {'OK' if not fails else str(len(fails)) + ' fallo(s)'}")
    return 1 if fails else 0


# ─────────────── Funciones disponibles según el sistema ───────────────
def capabilities():
    """[(función, estado, motivo)] de lo que funciona en ESTE sistema, según lo que
    hay instalado. Estados: ok (funciona), no (no funciona), part (parcial), na (no
    aplica en este sistema)."""
    R = []
    which = shutil.which

    def add(name, st, why):
        R.append((name, st, why))

    add("Analizar y descargar (yt-dlp)",
        "ok" if is_installed("yt_dlp") else "no",
        "yt-dlp está instalado." if is_installed("yt_dlp") else
        "Falta yt-dlp: DLpy ofrece instalarlo con pip (Python puro, no compila nada).")
    if IS_IOS:
        add("Unir audio y video (ffmpeg)", "ok",
            "ffmpeg viene integrado en a-Shell; DLpy no puede comprobarlo desde Python.")
    elif which("ffmpeg"):
        add("Unir audio y video (ffmpeg)", "ok", f"ffmpeg encontrado en {which('ffmpeg')}.")
    else:
        add("Unir audio y video (ffmpeg)", "no",
            "No hay ffmpeg: sin él solo se bajan formatos con audio incluido. "
            "DLpy ofrece instalarlo (" + ffmpeg_hint() + ").")
    if APPLE_MODE:
        if IS_IOS or which("ffmpeg"):
            add("Convertir a formato nativo", "ok",
                "Recodifica a HEVC/AAC si el resultado no lo reproduce QuickTime/Fotos "
                "(usa VideoToolbox si ffmpeg lo trae; si no, libx265/libx264).")
        else:
            add("Convertir a formato nativo", "no", "Necesita ffmpeg.")
    else:
        add("Convertir a formato nativo", "na",
            f"No hace falta: {PLAT_LABEL} reproduce h264/vp9/hevc y aac/opus sin convertir; "
            "«mejor formato» prefiere h264 por compatibilidad.")
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
                + JS_INSTALL_HINT[PLATFORM] + ". Sin él YouTube puede mostrar menos formatos; "
                "otros sitios no se ven afectados.")
    add("Reanudar descargas cortadas", "ok", "Misma huella enlace+formato; caduca a las 24 h.")
    add("Caché de pistas (24 h)", "ok",
        "Usa enlaces duros y, si el disco no los admite (FAT/exFAT), copia el archivo.")
    dest = DOWNLOAD_DIR
    if IS_IOS:
        add("Carpeta de descargas", "ok", f"{dest} (sandbox de a-Shell, visible en Archivos).")
    elif SHARED_OK:
        add("Carpeta de descargas", "ok", f"{dest} (backups y changelog en {FILES_DIR}).")
    elif IS_ANDROID:
        add("Carpeta de descargas", "part",
            f"Sin permiso de almacenamiento: se guarda en {dest}. Ejecuta termux-setup-storage.")
    else:
        add("Carpeta de descargas", "part",
            f"No se puede escribir en la carpeta Descargas: se guarda en {dest}.")
    cmd = clipboard_cmd()
    if cmd:
        add("Ofrecer el enlace del portapapeles", "ok", f"Con «{os.path.basename(cmd[0])}».")
    elif IS_IOS:
        add("Ofrecer el enlace del portapapeles", "na",
            "Desactivado a propósito: iOS pregunta «¿Permitir pegar?» en cada lectura. "
            "Actívalo con DLPY_CLIPBOARD=1.")
    elif IS_ANDROID:
        add("Ofrecer el enlace del portapapeles", "no",
            "Falta Termux:API (la app de F-Droid + «pkg install termux-api»).")
    elif IS_LINUX:
        add("Ofrecer el enlace del portapapeles", "no",
            "Falta wl-paste, xclip o xsel, o no hay sesión gráfica (SSH).")
    else:
        add("Ofrecer el enlace del portapapeles", "no", "No se encontró la orden del portapapeles.")
    if IS_IOS:
        add("Entregar el archivo al terminar", "part",
            f"Lanza tu atajo «{SHORTCUT_NAME}» con shortcuts://; si no lo creaste en Atajos, "
            "no pasa nada. Python no puede comprobarlo.")
    elif IS_ANDROID:
        ok = bool(which("termux-open"))
        add("Entregar el archivo al terminar", "ok" if ok else "no",
            "Abre con el reproductor de Android (termux-open)." if ok else
            "Falta termux-open (pkg install termux-tools).")
    else:
        opener = {"macos": "open", "windows": "os.startfile"}.get(PLATFORM)
        if IS_LINUX:
            opener = which("xdg-open") or (which("wslview") if is_wsl() else None)
        if not has_display():
            add("Entregar el archivo al terminar", "no",
                "No hay pantalla gráfica (SSH/servidor): el archivo se guarda pero no se abre.")
        elif not opener:
            add("Entregar el archivo al terminar", "no", "Falta xdg-open (paquete xdg-utils).")
        else:
            add("Entregar el archivo al terminar", "ok",
                f"Se abre con la app por defecto ({os.path.basename(opener)}).")
    if IS_IOS:
        add("Notificación al terminar", "na",
            "a-Shell no puede notificar; el aviso lo da tu Atajo.")
    elif IS_ANDROID:
        ok = bool(which("termux-notification"))
        add("Notificación al terminar", "ok" if ok else "no",
            "Con Termux:API." if ok else "Falta Termux:API (app + «pkg install termux-api»).")
    elif IS_MAC:
        add("Notificación al terminar", "ok" if which("osascript") else "no",
            "Con osascript." if which("osascript") else "Falta osascript.")
    elif IS_WINDOWS:
        ps = bool(which("powershell") or which("pwsh"))
        add("Notificación al terminar", "ok" if ps else "no",
            "Globo de la bandeja con PowerShell." if ps else "Falta PowerShell.")
    else:
        ok = has_display() and bool(which("notify-send"))
        add("Notificación al terminar", "ok" if ok else "no",
            "Con notify-send." if ok else
            "Falta notify-send (libnotify-bin) o no hay sesión gráfica.")
    if IS_ANDROID:
        ok = bool(which("termux-media-scan"))
        add("Aparecer en la galería", "ok" if ok else "no",
            "Escanea el archivo (termux-media-scan)." if ok else
            "Falta termux-media-scan (pkg install termux-api).")
    else:
        add("Aparecer en la galería", "na",
            "Solo existe en Android; en el resto el archivo se ve en su carpeta.")
    if IS_ANDROID:
        add("Compartir un enlace a DLpy", "ok",
            "~/bin/termux-url-opener: compartes el enlace a Termux desde cualquier app.")
    elif IS_IOS:
        add("Compartir un enlace a DLpy", "part",
            "Solo mediante tu atajo de Atajos, que debe abrir a-Shell con el enlace.")
    else:
        add("Compartir un enlace a DLpy", "no",
            "Un escritorio no tiene «compartir a»: pega el enlace o pásalo como argumento.")
    if countdown_supported():
        add("Cuenta regresiva interactiva", "ok",
            "msvcrt (consola de Windows)." if os.name == "nt" else "termios (modo sin eco).")
    else:
        add("Cuenta regresiva interactiva", "part",
            "La entrada no es un terminal (tubería o sin termios/msvcrt): se pregunta sin cuenta.")
    add("Colores y barras animadas", "ok" if (USE_COLOR and ANSI_OK) else "part",
        "ANSI activo." if (USE_COLOR and ANSI_OK) else
        "Sin colores (salida redirigida, NO_COLOR o consola sin ANSI).")
    if IS_IOS:
        add("Ocultar el teclado", "ok", "hideKeyboard de a-Shell.")
    else:
        add("Ocultar el teclado", "na", "No hay teclado en pantalla que ocultar.")
    return R


def print_capabilities():
    """`python dlpy.py --sistema`: qué funciona aquí y por qué."""
    print(title_bar(f"DLpy v{VERSION}", paint("sistema", "gray")))
    print(rule())
    kv("Corre en", f"{platform_name()} · {machine_name()} · Python {sys.version.split()[0]}")
    kv("Modo", PLATFORM + (" (forzado con DLPY_PLATFORM)" if os.environ.get("DLPY_PLATFORM") else ""))
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


# ───────────────────────── Principal ─────────────────────────
URL_OPENER_MARK = "# DLpy termux-url-opener"


def write_url_opener(force=False):
    """Crea ~/bin/termux-url-opener. Devuelve (estado, ruta): «creado»,
    «existe» (ya era el de DLpy), «ajeno» (hay otro y no se toca) o «error:…»."""
    bindir = os.path.join(HOME, "bin")
    path = os.path.join(bindir, "termux-url-opener")
    bash = os.path.join(os.environ.get("PREFIX") or "/data/data/com.termux/files/usr", "bin", "bash")
    body = (f"#!{bash}\n{URL_OPENER_MARK}\n"
            f"exec {shlex.quote(sys.executable)} {shlex.quote(SCRIPT_PATH)} \"$1\"\n")
    try:
        os.makedirs(bindir, exist_ok=True)
        if os.path.isfile(path):
            old = read_text(path)
            if URL_OPENER_MARK not in old:
                if not force:
                    return "ajeno", path
                copy_file(path, path + ".bak")
            elif old == body:
                return "existe", path
        write_text(path, body)
        os.chmod(path, 0o755)
    except OSError as e:
        return f"error: {e}", path
    return "creado", path


def ensure_url_opener():
    """Primera ejecución en Android: deja listo «compartir enlace → Termux»."""
    st, path = write_url_opener()
    if st == "creado":
        m_ok("Compartir a Termux activado: comparte un enlace desde cualquier app a Termux.")
    elif st == "ajeno":
        m_warn("Ya hay un ~/bin/termux-url-opener que no es de DLpy; no se tocó.")
        note("Para reemplazarlo (con copia .bak): python dlpy.py --instalar-android")
    elif st.startswith("error"):
        dbg("url-opener", st)


def setup_android():
    """Crea ~/bin/termux-url-opener: compartir un enlace a Termux abre DLpy."""
    if not IS_ANDROID:
        m_warn("--instalar-android solo aplica en Termux (Android).")
        return 1
    st, path = write_url_opener(force=True)
    if st.startswith("error"):
        m_err(f"No se pudo crear {path}: {st[7:]}")
        return 1
    m_ok(f"Listo: {path}")
    note("Comparte un enlace desde cualquier app a Termux y se abrirá DLpy con él.")
    if not SHARED_OK:
        m_warn("Falta el almacenamiento compartido: ejecuta termux-setup-storage.")
    return 0


def root_move_target(script_path, home):
    """Destino en la raíz de Termux (~/dlpy.py) o None si el script ya está en ella."""
    folder = os.path.dirname(os.path.realpath(script_path))
    if folder == os.path.realpath(home):
        return None
    return os.path.join(home, "dlpy.py")


def relocate_to_root():
    """Android: va a la raíz (~), mueve ahí el script si estaba en otra carpeta y
    lo vuelve a ejecutar desde ahí con los mismos argumentos."""
    try:
        os.chdir(HOME)
    except OSError as _ign:
        ignore("relocate_to_root", _ign)
    if os.environ.get("DLPY_NO_MOVE") or os.environ.get("DLPY_MOVED"):
        return
    dst = root_move_target(SCRIPT_PATH, HOME)
    if not dst:
        return
    tmp = dst + ".tmp"
    try:
        copy_file(SCRIPT_PATH, tmp)
        os.replace(tmp, dst)
    except OSError as e:
        m_warn(f"No se pudo mover DLpy a ~ ({e}); sigue ejecutándose donde está.")
        try:
            os.remove(tmp)
        except OSError as _ign:
            ignore("relocate_to_root", _ign)
        return
    try:
        os.remove(SCRIPT_PATH)
    except OSError as _ign:
        ignore("relocate_to_root", _ign)
    # El atajo de «compartir a Termux» apuntaba a la ruta vieja
    opener = os.path.join(HOME, "bin", "termux-url-opener")
    try:
        if os.path.isfile(opener):
            txt = read_text(opener)
            if URL_OPENER_MARK in txt and shlex.quote(SCRIPT_PATH) in txt:
                write_text(opener, txt.replace(shlex.quote(SCRIPT_PATH), shlex.quote(dst)))
    except OSError as _ign:
        ignore("relocate_to_root", _ign)
    os.environ["DLPY_MOVED"] = "1"
    os.environ["DLPY_ORIGIN"] = SCRIPT_PATH      # carpeta de origen: se actualiza junto con ~/dlpy.py
    card_thread_stop()                           # libera la región de desplazamiento (0.2.6)
    try:
        os.execv(sys.executable, [sys.executable, dst] + sys.argv[1:])
    except OSError as e:
        m_warn(f"Se movió a {dst} pero no se pudo reiniciar ({e}); vuelve a ejecutarlo desde ~.")
        sys.exit(1)


def main():
    if "--selftest" in sys.argv[1:]:
        return selftest()
    if "--sistema" in sys.argv[1:]:
        return print_capabilities()
    if wants_2shortcuts(sys.argv[1:]):
        return send_code_to_shortcut()
    if IS_ANDROID:
        relocate_to_root()
    if "--instalar-android" in sys.argv[1:]:
        return setup_android()
    cli_args = [a for a in sys.argv[1:] if not a.startswith("--")]

    os.makedirs(INTERNAL_DIR, exist_ok=True)
    migrate_internal_layout()       # estructura anterior → state/ script/ cache/ delivery/
    ensure_dirs()
    clear_screen()                  # banner arriba, sin restos de la ejecución anterior
    if IS_ANDROID:
        ensure_url_opener()
    if IS_ANDROID and not SHARED_OK:
        m_warn("Sin acceso al almacenamiento compartido: se guarda en ~/dlpy_files.")
        note("Ejecuta termux-setup-storage y reinicia Termux para usar Descargas/DLpy.")
    elif IS_DESKTOP and not SHARED_OK:
        m_warn("No se puede escribir en la carpeta Descargas: se guarda en ~/dlpy_files.")
        note("Revisa sus permisos o define DLPY_DOWNLOAD_DIR con otra carpeta.")

    check_storage()                 # antes de cualquier otro proceso
    reexec = getattr(sys, "_dlpy_reexec", False)     # recién instalada por la anterior: ya se comprobó
    if "--actualizar" in sys.argv[1:]:
        if not reexec:
            check_update(force=True)
        if UPDATE_CHECKED["ok"] or reexec:
            check_mark("script", script_sig())
        return 0 if check_dependencies(force=True) else 1
    script_due = (not os.environ.get("DLPY_NO_UPDATE") and not reexec
                  and check_due("script", script_sig()))          # una vez al día (0.2.7)
    if reexec:
        UPDATE_CHECKED["ok"] = True              # la versión anterior acaba de comprobar y la instaló
    if script_due:
        if IS_IOS and not NESTED_IOS and sys.stdin.isatty() and _flag_env("DLPY_SETTLE", True):
            time.sleep(0.25)                     # deja pasar lo que llega solo al abrir desde Atajos
        if check_update():
            return 0
    if not check_version():
        return 1
    if (script_due or reexec) and UPDATE_CHECKED["ok"]:
        check_mark("script", script_sig())       # después de check_version: puede reescribir el .py (changelog)
    export_crashes_json()           # iOS: ~/Documents/crashes_dlpy.json con las versiones que fallaron
    dev_sync_version()              # solo con DLPY_DEV=1 en a-Shell: copia el snapshot a ~/Documents/dlpy_<versión>.py
    if not check_dependencies():
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
                        "internal": INTERNAL_DIR})

    import yt_dlp

    # Antes de la primera pregunta: tirar Enter residual del lanzamiento por Atajos
    drain_pending_input(0.12)
    link = get_link(cli_args)
    if not link:
        m_err("Sin enlace.")
        return 1
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

    # 1b) Ya descargado: mostrar datos y preguntar si continúa
    if old_file:
        show_existing(old_file, old_entry, title=title)
        print()
        try:
            de_nuevo = ask_yn("¿Descargar de nuevo? (s/N) ▸ ", default=False)
        except (EOFError, KeyboardInterrupt):
            return 1
        if not de_nuevo:
            roast_done(len(index) - 1, reused=True)
            deliver_existing(old_file, old_entry, title)
            return 0

    formats = [normalize_format(f) for f in (info.get("formats") or [])
               if f.get("ext") != "mhtml" and "storyboard" not in (f.get("format_note") or "")]
    dbg("formatos sin códec (supuestos)", [f.get("format_id") for f in formats if f.get("_guess")])
    audios = [f for f in formats if has(f.get("acodec")) and not has(f.get("vcodec"))]
    videos = [f for f in formats if has(f.get("vcodec"))]
    audios.sort(key=abr_of)            # de peor a mejor calidad
    videos.sort(key=lambda f: (f.get("height") or 0, f.get("tbr") or 0))

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

    # 2) Listar: audio y luego video (de peor a mejor calidad). Con tope de filas según el
    #    alto del terminal: se ven las mejores y «m» muestra todas (0.2.4).
    a_rows = [audio_row(i, f, orig_ids) for i, f in enumerate(audios, 1)]
    v_rows = [video_row(i, f) for i, f in enumerate(videos, len(audios) + 1)]
    choices = {r["n"]: ("a", audios[i]) for i, r in enumerate(a_rows)}
    choices.update({r["n"]: ("v", videos[i]) for i, r in enumerate(v_rows)})
    bk, bf = auto_best(audios, videos, orig_ids, can_merge, quiet=True)
    best_n = next((k for k, (_kd, ff) in choices.items() if ff is bf), None)
    a_flags, v_flags = ["apple", "orig"], ["apple"]
    for r in a_rows + v_rows:
        if r["n"] == best_n:
            r["flags"].add("best")
    cap = list_cap()
    a_take = min(len(a_rows), max(2, cap // 3))
    v_take = min(len(v_rows), cap - a_take)
    a_take = min(len(a_rows), cap - v_take)
    a_keep = best_n - 1 if bk == "a" and best_n else None
    v_keep = best_n - len(audios) - 1 if bk == "v" and best_n else None
    a_start = visible_start(len(a_rows), a_take, a_keep)
    v_start = visible_start(len(v_rows), v_take, v_keep)
    can_more = bool(a_start or v_start)

    def show_list(full):
        """Pantalla de la lista; devuelve True si quedan filas ocultas (se ven con «m»)."""
        clear_screen()
        if full and CARD["pin"]:
            card_thread_stop()          # lista completa: se suelta el banner anclado para poder deslizar (0.2.8)
        show_title(title)
        legend(["apple", "orig"])
        ROW_PLAIN.clear()
        asx, vsx = (0, 0) if full else (a_start, v_start)
        if a_rows:
            header("AUDIO" + (f" · +{asx} más" if asx else ""))
            print_rows(a_rows[asx:], a_flags, AUDIO_HEAD)
        if v_rows:
            header("VIDEO" + (f" · +{vsx} más" if vsx else ""), gap=False)
            rows, vhead = drop_empty_cols(v_rows[vsx:], VIDEO_HEAD)   # «Rango» solo si algún formato lo usa
            print_rows(rows, v_flags, vhead)
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
            cur = retry_prompt(cur, typed)          # Enter vacío / Enter fantasma: sin línea nueva (0.2.7)
            continue
        if raw == "m" and hidden and can_more:
            hidden = show_list(True)
            cur = PROMPT
            continue
        if raw == "b":
            kind, fmt = auto_best(audios, videos, orig_ids, can_merge)
            flash_row(best_n)
            break
        if raw.isdigit() and int(raw) in choices:
            kind, fmt = choices[int(raw)]
            flash_row(int(raw))
            break
        cur = retry_prompt(cur, typed, bad_prompt(f"1-{len(choices)}, b" + (", m" if hidden else "") + " o q"),
                           f"Opción inválida: escribe un número del 1 al {len(choices)}, b"
                           + (", m" if hidden else "") + " o q.")

    dbg("elegido", {"entrada": raw, "tipo": kind, "formato": pick(fmt, FMT_KEYS)})
    roast_choice(kind, fmt)

    # Resumen limpio tras la lista (evita teclado/prompt bajo decenas de filas)
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

    # 4) Armar selección de pistas
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
            if multi_lang:
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
    if plan:
        plan = ask_apple_convert(plan, can_merge, info.get("duration"), fmt)
        dbg("conversión", "aceptada" if plan else "rechazada / no disponible")
    conv_state = {}

    # 4c) ¿Ya está descargado con estos mismos parámetros / streams?
    if old_file and reuse_downloaded(old_file, old_entry, index, key, title, info, kind,
                                     fmt, fmt_id, selected, orig_ids, plan):
        roast_done(len(index) - 1, reused=True)
        return 0

    # 5) Nombre de archivo
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

    opts = {
        **base_opts,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "format": fmt_id,
        "outtmpl": os.path.join(work_dir, base.replace("%", "%%") + ".%(ext)s"),
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
    if not IS_IOS and (CACHE_STATS["saved"] or CACHE_STATS["failed"]):
        m_info(f"Caché de streams (24 h): {CACHE_STATS['saved']} pista(s) guardada(s)"
               + (f", {CACHE_STATS['failed']} con error" if CACHE_STATS["failed"] else ""))
    if conv_state.get("path"):
        convert_done(plan, conv_state.get("vcodec"))

    if not final or not os.path.exists(final):
        cleanup_work(work_dir)
        m_err("No se encontró el archivo descargado.")
        return 1

    # Mover el resultado terminado a dlpy_files (solo procesos completados)
    dest_name = os.path.basename(final)
    dest_path = os.path.join(DOWNLOAD_DIR, dest_name)
    if os.path.abspath(final) != os.path.abspath(dest_path):
        try:
            if os.path.exists(dest_path):
                dest_path = _free_path(dest_path)
            move_file(final, dest_path)
            final = dest_path
        except Exception as e:
            cleanup_work(work_dir)
            m_err(f"No se pudo guardar el archivo en {DOWNLOAD_DIR}: {e}")
            return 1

    cleanup_work(work_dir)
    dbg("movido a", final)
    m_ok("Descarga lista")

    # Reemplazar el archivo anterior y quitar el sufijo temporal
    if old_file and os.path.abspath(old_file) != os.path.abspath(final):
        try:
            os.remove(old_file)
        except OSError as _ign:
            ignore("main", _ign)
        clean = final.replace(" (nuevo)", "")
        if clean != final and not os.path.exists(clean):
            os.replace(final, clean)
            final = clean

    # 6) Registrar (con datos técnicos) y enviar
    index[key] = {"file": os.path.basename(final), "title": title,
                  "date": int(time.time()), "version": VERSION,
                  "meta": build_meta(kind, fmt, fmt_id, selected, orig_ids, final,
                                    conv_state or None, info)}
    dbg("índice", index[key])
    try:
        save_json(INDEX_FILE, index)
    except Exception as e:
        m_warn(f"No se pudo guardar el índice: {e}")

    roast_done(len(index) - 1)
    deliver(final, title)
    return 0


if __name__ == "__main__":
    sys.exit(run_guarded(main))
