#!dlpy.py - siempre empezar el script con este mismo comentario.
# Cada edicion de este archivo sube la version: x.y.z donde Y y Z solo llegan hasta el 9 y X no tiene limites.
# Cada edicion mete el changelog en el py borrando los changelog que no sean de la version actual.
# Respetar entrga de archivos con dlpy_x.y.z.py (siempre dar archivos con ese orden de nombre sustituyendo "X.Y.Z" con los números correspondientes).
# Respetar el flujo de escena (shortcutmode) con coherencia visual, flujo de animacion, transiciones, etc.
# La animación de la escena D L P Y (comando tecleado, título del marco y pie) siempre debe coincidir con el texto de estado que se ve (p. ej. «Comprobando pip» ↔ pip), nunca con comandos de muestra sueltos que ciclan por tiempo; al añadir una fase o paquete nuevo, añadirlo también a _dlpy_topic.
# Ninguna escena (dibujo del centro) se deshace en la siguiente hasta terminar su loop en curso, aunque el proceso ya haya terminado (motif_loop_left); al añadir una escena con loop, darle su cuenta ahí. La conversión siempre empieza desde el principio (los paquetes salen del origen).
# Conservar en todo momento, tal cual y en el mismo orden, los comentarios escritos anteriormente (la cabeza del script: desde la primera línea hasta el índice y el mapa de etiquetas), sin importar las ediciones realizadas; solo el changelog se renueva, según la regla 3.
# Cada edición revisa si hace falta actualizar también el selftest (pruebas para lo nuevo o lo cambiado), la configuración (CONFIG_OPTIONS y --config) y las escenas (dibujo, texto de estado y tiempos; la espera entre escenas la gobierna DLPY_SCENE_MODE: loop · real · segundos), y lo hace cuando sea necesario.
# La escena D L P Y (comando, título, pie y marca ✓/✗) debe ser real conforme a lo que el script está ejecutando en ese momento: el comando se teclea cuando ya se ve y el flujo espera a que se haya mostrado, no a un reloj; cada edición la revisa y la actualiza siempre que aplique (fase, paquete, comando o texto de estado nuevo o cambiado) y, si algo cambia ahí, también su prueba en el selftest.
# ==== FIN REGLAS ====

# ==== CHANGELOG ====
# ## 1.5.6
#
# - Las animaciones ya no llevan barras de progreso ni porcentajes: solo animaciones y sus sub animaciones. El avance lo llevan la regla de arriba y
#   el % del final. Se quitó la barra (y0+8) de todas las escenas de ancho completo y de las tarjetas del carril, style_bar y los % / puntos de
#   avance del estado (style_status: queda ✓, «espera» o el dato del archivo); la vía de la conversión y de la Descarga (DLPY_SCENE_RAIL=0) ya no
#   se llena con el avance, solo van los paquetes, y al llegar la conversión a 100 % la vía se llena y el destino destella.
# - Selftest: las pruebas de barra y % ahora comprueban que no hay barra ni % en ninguna escena ni tarjeta.
# - Heredado de 1.5.5: la revisión del archivo respeta el modo UX (wait: espera solo a que acabe la animación; real: directo; segundos: esa pausa;
#   SCENE["mvis"], scene_wait_motif, scene_wait_anim); las tarjetas del carril terminadas salen por la izquierda; entrada y salida de tarjetas y cambio
#   de dibujo del centro al doble de velocidad (RAIL_MOVE, RAIL_EXIT_*, RAIL_FADE_IN, RAIL_EXIT_T, SCENE_SWAP, SCENE_LAG_MOTIF).
# ==== FIN CHANGELOG ====

VERSION = "1.5.6"

# Índice de secciones (cada una empieza con una cabecera «# ──── Título ────»; busca el título):
#   Variables DLPY_* recordadas · Plataforma · Rutas · Compatibilidad nativa Apple · Interfaz · Terminal:
#   ancho y texto · Mensajes y debug · Escena continua de --shortcutpick · Comentarios inteligentes (humor según el uso) · Pantalla: banner,
#   títulos y listas · Barras y paneles de progreso · Terminal: teclado y cuenta regresiva · Utilidades ·
#   Formatos y pistas: etiquetas y selección · Post-proceso: pista predeterminada · Compatibilidad Apple:
#   conversión opcional · Bits, HDR y sondeo del video · Ya descargado: reutilizar o convertir · JSON /
#   índice · Enlace y portapapeles · Dependencias · Actualizaciones (Releases de GitHub) · YouTube: runtime de
#   JavaScript + yt-dlp-ejs · Rechazos recordados · Changelog y backup · Limpieza de almacenamiento ·
#   Control de versión · Releases de GitHub y backups
#   (listado) · Comparar versiones: huellas y diferencias · Fallos: historial y avisos · Pantalla de
#   versiones (--versions) · Recuperación tras un fallo · Caché de streams (24 h) · Reanudación de descargas (con menú de pendientes) ·
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
#   ÁREA H · RECUPERACIÓN Y CACHÉ: [H1] Recuperación tras un fallo, [H2] Caché de streams (24 h), [H3] Reanudación de descargas y menú de pendientes, [H4] Limpieza de la carpeta inter
#   ÁREA I · ENTREGA Y ANÁLISIS: [I1] Entrega del archivo (Atajos), [I2] Atajo de iOS (--2shortcuts), [I3] Análisis tolerante (equivale, [I4] Error «no eres un bot»
#   ÁREA J · MODO ATAJO: [J1] Modo atajo (--scm / --scb)
#   ÁREA K · AUTOPRUEBA Y SISTEMA: [K1] Autoprueba, [K2] Funciones disponibles según 
#   ÁREA L · PRINCIPAL: [L1] Principal
#   main(): [M0a] modos especiales · [M0b] preparación · [M0c] actualización y dependencias · [M1] enlace y análisis ·
#           [M2] lista y elección · [M3] resumen · [M4] pistas, conversión y ya descargado · [M5] nombre y trabajo ·
#           [M6] descarga con yt-dlp · [M7] mover el resultado · [M8] registrar y entregar
#   selftest(): [T0]…[T27] (cada una antes de su grupo de pruebas; cada grupo es una función _st_t*; main(): una función _m_* por paso)

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

BOOT_T0 = time.time()                  # 1.2.2: lo primero tras los imports: --scm cuenta su tope de tiempo desde aquí

# ╔════════════════════════════════════════════════════════════════════════════════╗
# ║ ÁREA A · NÚCLEO — entorno, plataforma, rutas, compatibilidad Apple, interfaz   ║
# ╚════════════════════════════════════════════════════════════════════════════════╝
# ─────────────────────── [A1] Variables DLPY_* recordadas ───────────────────────
ENV_NAME = "env.json"                     # 1.3.0: el archivo antiguo (dentro de .dlpy_internal); ahora solo se lee para migrar
CONFIG_NAME = "dlpy_config.json"          # 1.3.0: la configuración vive en dlpy_files, fuera de .dlpy_internal
INTERNAL_NAME = ".dlpy_internal"          # carpeta oculta dentro de dlpy_files
ENV_SKIP = {"DLPY_FORGET", "DLPY_NOVERIFY"}   # de una sola ejecución
ENV_STATE = {"path": None, "error": None, "migrated": 0}  # dónde se guardó, por qué falló y cuántas se trajeron del env.json antiguo


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


def write_text(path, text, mkdir=False):
    """Escribe `text` en `path` de forma atómica (archivo temporal + os.replace):"""
    folder = os.path.dirname(path)
    if mkdir and folder:
        os.makedirs(folder, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)


def save_json(path, data, mkdir=False, **kw):
    """Guarda `data` como JSON (atómico, ver write_text); `kw` pasa a json.dumps (p. ej. sort_keys=True)."""
    write_text(path, json.dumps(data, ensure_ascii=False, indent=1, **kw), mkdir)


def persist_env(env=None, path=None, legacy=None):
    """Las DLPY_* definidas se guardan en `path`; las no definidas se recuperan de ahí (en a-Shell las «export»"""
    env = os.environ if env is None else env
    path = path or ENV_FILE
    ENV_STATE["path"], ENV_STATE["error"], ENV_STATE["migrated"] = path, None, 0
    try:
        disk = _read_env_json(path)
        base = disk
        if legacy and not os.path.isfile(path):
            base = _read_env_json(legacy)
            ENV_STATE["migrated"] = len(base)
        forget = (env.get("DLPY_FORGET") or "").strip().lower() not in ("", "0", "no", "false")
        merged = {} if forget else dict(base)
        merged.update({k: v for k, v in env.items() if k.startswith("DLPY_") and k not in ENV_SKIP})
        for k, v in merged.items():
            if k not in env:
                env[k] = v
        if merged != disk:
            save_json(path, merged, mkdir=True, sort_keys=True)
        return merged
    except Exception as e:
        ENV_STATE["error"] = f"{type(e).__name__}: {e}"
        return {}


# ─────────────────────── [A2] Plataforma ───────────────────────
# DLpy solo corre en iOS (a-Shell).
PLATFORM = "ios"
PLAT_LABEL = "Apple"


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
    """Dónde se guardan las DLPY_*:"""
    home = home or os.path.expanduser("~")
    return os.path.join(home, "Documents", "dlpy_files", CONFIG_NAME)


def legacy_env_file_path(home=None):
    """El env.json de antes de la 1.3.0 (dentro de .dlpy_internal): solo se lee, una vez, para traerlo al archivo nuevo."""
    home = home or os.path.expanduser("~")
    return os.path.join(home, "Documents", "dlpy_files", INTERNAL_NAME, ENV_NAME)


ENV_FILE = env_file_path()
LEGACY_ENV_FILE = legacy_env_file_path()
if not any(a.lstrip("-\u2013\u2014").lower() == "selftest" for a in sys.argv[1:]):
    persist_env(path=ENV_FILE, legacy=LEGACY_ENV_FILE)


# 1.3.0: opciones conocidas (para «--config --opciones»): (nombre, valor por omisión, qué hace). Las de una sola ejecución (DLPY_FORGET,
# DLPY_NOVERIFY) no se guardan y no salen aquí.
CONFIG_OPTIONS = (
    ("DLPY_DEBUG", "", "1 = modo depuración"),
    ("DLPY_LOGKEEP", "20", "cuántos logs de depuración se conservan"),
    ("DLPY_ROWS", "auto", "alto de pantalla que usa DLpy"),
    ("DLPY_LINES", "26", "líneas que ocupa la interfaz"),
    ("DLPY_WIDTH", "auto", "ancho fijo del texto en columnas (mínimo 20)"),
    ("DLPY_TRUECOLOR", "1", "0 = colores básicos"),
    ("DLPY_ANIM", "1", "0 = sin animaciones"),
    ("DLPY_CLASSIC", "0", "1 = barra «█░»"),
    ("DLPY_SITEANIM", "1", "0 = sin la animación del sitio"),
    ("DLPY_SCENE", "1", "0 = --shortcutpick vuelve a intro + panel + tarjeta"),
    ("DLPY_SCENE_PIP", "1", "0 = pip siempre cede la escena (escribe directo al terminal)"),
    ("DLPY_SCENE_FLOW", "1", "0 = el cambio de dibujo del centro vuelve a ser la disolución en ruido (1 = las celdas viajan al dibujo nuevo, morph)"),
    ("DLPY_SCENE_RAIL", "1", "0 = descarga, unión y guardado vuelven a ser tres dibujos sueltos (1 = tarjetas en un carril de hasta 3: entran por la derecha y salen por la izquierda, ya las desplace otra o haya terminado su proceso)"),
    ("DLPY_SCENE_CALM", "0", "1 = escena D L P Y calmada: los textos cambian sin ruido y el texto tenue se ve más claro (más fácil de leer en el iPhone)"),
    ("DLPY_UX", "wait", "UX de la escena, una sola opción: wait = cada escena espera a que acabe su animación antes de pasar a la siguiente · real = el transcurso real: mete cada animación conforme al proceso, haya terminado o no la anterior (la conversión y la unión avanzan con su avance real) · un número (p. ej. 3 o 2.5) = los segundos que dura cada escena (de 0 a 60)"),
    ("DLPY_EARLYINTRO", "1", "0 = la intro sale justo antes de la descarga"),
    ("DLPY_SOFTCLEAR", "1", "0 = clear_screen borra con native_clear() (parpadea)"),
    ("DLPY_PURGE", "1", "0 = al borrar la consola no se vacía el historial (ESC[3J); con 1 no reaparece texto de sesiones anteriores"),
    ("DLPY_EARLYCLEARMODE", "reset", "primer borrado al arrancar: reset (el clear 3 de la 0.3.6, borra también lo de versiones anteriores) · auto · home · down · purge-first; luego todo es softclear"),
    ("DLPY_CLEARMODE", "auto", "cómo se limpia la consola: auto (`clear` nativo) · home · down · purge-first · reset; prueba cuál va sin deslizar con --cleartest"),
    ("DLPY_OUTRO", "1", "0 = antes del atajo solo se limpia la consola"),
    ("DLPY_OUTROHOLD", "1.2", "segundos con la pantalla a la vista antes del atajo"),
    ("DLPY_VIEW", "shortcut", "cómo se abre el archivo al terminar: shortcut = se entrega al atajo «DLpy» · view = el comando `view` de a-Shell (--view lo fija solo para esa ejecución)"),
    ("DLPY_ROAST", "1", "0 = sin comentarios de humor"),
    ("DLPY_CLIPBOARD", "", "1 = leer el enlace del portapapeles (iOS pide permiso cada vez)"),
    ("DLPY_UPDATES", "1", "cada cuánto busca actualizaciones del script y de sus dependencias (pip, yt-dlp, yt-dlp-ejs): un número = la espera en días entre una revisión y otra (1 = cada día, predeterminado · 0.5 = cada 12 h · 7 = cada semana) · on = en cada arranque · 0 u off = nunca (--actualizar sigue funcionando)"),
    ("DLPY_UPDATE_REPO", "ElDelDLpy/DLpy", "repositorio de GitHub de donde salen los Releases"),
    ("DLPY_CLEAN_LIMIT_MB", "1024", "límite de almacenamiento en MB"),
    ("DLPY_SC_TIMEOUT", "90", "tope del análisis para el atajo en segundos (0 = sin tope)"),
    ("DLPY_SCM_TIMEOUT", "5", "tope de --scm en segundos"),
    ("DLPY_SCM_HARD", "8", "segundos a los que --scm debería haber terminado (0 = sin tope)"),
    ("DLPY_YTDLP_ARGS", "", "argumentos extra para yt-dlp"),
)
CONFIG_KEY_RE = re.compile(r"^DLPY_[A-Z0-9_]+$")


def config_key(raw):
    """1.3.0: «rows» / «dlpy_rows» / «DLPY_ROWS» → «DLPY_ROWS»; None si no es un nombre válido."""
    k = str(raw or "").strip().upper().replace("-", "_")
    if not k.startswith("DLPY_"):
        k = "DLPY_" + k
    return k if CONFIG_KEY_RE.match(k) else None


def config_write(data, path=None):
    """1.3.0: guarda `data` (solo DLPY_* de texto) en el archivo de configuración, de forma atómica. Crea la carpeta si falta."""
    path = path or ENV_FILE
    save_json(path, {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str) and k.startswith("DLPY_") and k not in ENV_SKIP},
              mkdir=True, sort_keys=True)


def config_edit(items, path=None):
    """1.3.0:"""
    path = path or ENV_FILE
    data = _read_env_json(path)
    changes, errors = [], []
    for raw in items:
        name, eq, val = str(raw).partition("=")
        key = config_key(name)
        if key is None:
            errors.append(f"«{raw}»: nombre no válido (usa NOMBRE=valor)")
            continue
        if not eq:
            errors.append(f"«{raw}»: falta «=» (NOMBRE=valor guarda · NOMBRE= borra)")
            continue
        if key in ENV_SKIP:
            errors.append(f"{key}: es de una sola ejecución y no se guarda (usa export)")
            continue
        old, val = data.get(key), val.strip()
        if val:
            data[key] = val
        else:
            data.pop(key, None)
        new = val or None
        if old != new:
            changes.append((key, old, new))
    if changes:
        config_write(data, path)
    return changes, errors


# ───────────────────────── [A3] Rutas ─────────────────────────
HOME = os.path.expanduser("~")
# Completadas + backups únicamente
FILES_DIR = os.path.join(HOME, "Documents", "dlpy_files")
# Índice, estado, caché, trabajo temporal y changelog (carpeta oculta dentro de dlpy_files). 1.3.0: las variables DLPY_* ya no van aquí:
# están en dlpy_files/dlpy_config.json, que no se borra al cambiar de versión.
INTERNAL_DIR = os.path.join(FILES_DIR, INTERNAL_NAME)
# .dlpy_internal/: state/ (estado), script/ (copia y changelog), cache/streams/,
# work/ (descargas en curso) y delivery/<id>/ (copias de entrega al atajo).
# Se borra entera en cada subida o bajada de versión (reset_internal): cada versión empieza de cero.
STATE_DIR = os.path.join(INTERNAL_DIR, "state")
SCRIPT_DIR = os.path.join(INTERNAL_DIR, "script")
CACHE_DIR = os.path.join(INTERNAL_DIR, "cache")
INDEX_FILE = os.path.join(STATE_DIR, "index.json")
SHORTCUT_PICKS_FILE = os.path.join(STATE_DIR, "shortcut_picks.json")   # 1.5.4: de cada video, los formatos del JSON del atajo (id, resolución, fps…) para respaldar la elección
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
BACKUP_DIR = os.path.join(FILES_DIR, "backups")  # 0.9.9: ya no se usa, solo compat
TRASH_DIR = os.path.join(FILES_DIR, "trash")
TRASH_INTERNAL = os.path.join(INTERNAL_DIR, "trash")
SHORTCUTMODE_LOG = os.path.join(FILES_DIR, "shortcutmode.log")  # 1.0.4: errores sin romper escena
TRASH_DAYS = 10.0
TRASH_SECS = int(TRASH_DAYS * 86400)
TRASH_EXPIRE_DAYS = 30.0
TRASH_EXPIRE_SECS = int(TRASH_EXPIRE_DAYS * 86400)

CONSERVE_DOWNLOADS = True

STREAM_CACHE_DIR = os.path.join(CACHE_DIR, "streams")
WORK_ROOT = os.path.join(INTERNAL_DIR, "work")
DELIVERY_DIR = os.path.join(INTERNAL_DIR, "delivery")
# En FILES_DIR no se considera "descarga" lo que esté en backups/ ni el changelog
RESERVED = {"backups", "changelog.md", "logs", "trash", CONFIG_NAME}   # 1.1.6: trash no es una descarga
SCRIPT_PATH = os.path.abspath(__file__)
SHORTCUT_NAME = "DLpy"
MAX_NAME_BYTES = 120
INTERNAL_TTL = 24 * 3600          # entrega temporal al atajo
STREAM_CACHE_TTL = 24 * 3600      # reutilización de pistas/formatos
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
DEPENDENCIES = [("pip", "pip", False), ("yt-dlp", "yt_dlp", True)]      # 1.2.6: pip va primero para que yt-dlp se instale ya con el pip nuevo

# ─────────────── [A4] Compatibilidad nativa Apple ───────────────
APPLE_VCODEC = ("avc1", "h264", "hvc1", "hev1", "hevc", "h265")      # 1.2.4: «h265» (como lo declaran algunos sitios) es HEVC: ya no se recodifica
APPLE_ACODEC = ("mp4a", "aac", "alac", "mp3", "ac-3", "ec-3", "ac3", "eac3", "flac")
APPLE_VEXT = ("mp4", "m4v", "mov")
APPLE_AEXT = ("m4a", "mp4", "mp3", "aac", "wav", "aiff", "caf", "flac")


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
    USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
# ──── Secuencias de terminal y tiempos de espera con nombre (0.9.2) ────
# Secuencias ANSI de control (cursor, borrado, color). Los valores son los de siempre; solo tienen nombre.
RESET = "\x1b[0m"                 # quita colores y estilos
WRAP_OFF, WRAP_ON = "\x1b[?7l", "\x1b[?7h"          # apagar / encender el salto automático de línea
CURSOR_HIDE, CURSOR_SHOW = "\x1b[?25l", "\x1b[?25h"
ERASE_EOL, ERASE_BELOW = "\x1b[K", "\x1b[J"         # borrar hasta el final de la línea / hasta el final de la pantalla
HOME_CLEAR = "\x1b[2J\x1b[H"                         # pantalla en blanco y cursor arriba


def cur_to(row, col=1):
    """Mueve el cursor a la fila `row` y columna `col` (desde 1)."""
    return f"\x1b[{row};{col}H"


def cur_up(n):
    """Sube el cursor `n` filas."""
    return f"\x1b[{n}A"


# Pausas (segundos) de las animaciones y de las esperas; el nombre dice para qué es cada una.
POLL_TERM = 0.1          # esperar a que el terminal dé un tamaño válido
SITE_IDLE = 0.01         # respiro entre cuadros de la escena de un sitio
PANEL_TICK = 0.14        # refresco del panel de descarga
KEYBOARD_POLL = 0.05     # esperar el alto nuevo al bajar el teclado
FFMPEG_TICK = 0.25       # refresco de la barra de ffmpeg
FILE_POLL = 0.4          # esperar a que el archivo deje de crecer
OPEN_RETRY = 1.5         # reintento de `open` al entregar al atajo
VIEW_RUN = {"mode": None}   # 1.3.4: --view fija el modo de vista solo para esta ejecución (None = el de DLPY_VIEW)
VIEW_WORDS = {"view": "view", "vista": "view", "ashell": "view", "a-shell": "view", "v": "view",
              "shortcut": "shortcut", "shortcuts": "shortcut", "atajo": "shortcut", "atajos": "shortcut"}


def view_mode(raw=None):
    """1.3.4:"""
    if raw is True:
        return "view"
    if raw is None:
        raw = VIEW_RUN.get("mode")
        if raw is None:
            raw = os.environ.get("DLPY_VIEW")
    return VIEW_WORDS.get(str(raw or "").strip().lower(), "shortcut")


def send_label(view=False):
    """1.3.4: el texto de estado del cierre de la escena: lo que de verdad va a pasar con el archivo (atajo o view)."""
    return "Abriendo con view" if view else "Enviando a " + SHORTCUT_NAME
CLR = "\r\x1b[2K" if sys.stdout.isatty() else "\r"
# 0.8.9: el tamaño del terminal se mide con el ioctl (el real). shutil.get_terminal_size prefiere COLUMNS/LINES del entorno,
# que en un Atajo pueden venir desfasados; solo se usan si el ioctl no responde.
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

# Secuencia de respaldo de clear_screen (DLPY_CLEAR=1..4; por defecto 3). Solo se usa si el `clear` nativo falla.
CLEAR_SEQS = {"1": "\x1b[3J\x1b[2J\x1b[H", "2": "\x1b[2J\x1b[3J\x1b[H",
              "3": "\x1bc", "4": HOME_CLEAR}
CLEAR_SEQ = CLEAR_SEQS.get(os.environ.get("DLPY_CLEAR", "3").strip(), CLEAR_SEQS["3"])
# 1.2.3: «ESC[3J» borra también el historial de desplazamiento (scrollback). Sin él, el borrado solo limpia lo visible y, cuando la
# ventana de a-Shell cambia de alto (teclado, ventana de Atajos), el terminal vuelve a meter arriba las líneas viejas de sesiones
# anteriores. DLPY_PURGE=0 lo desactiva.
# 1.3.2: es intencional (a-Shell conserva texto entre sesiones): sigue activo por omisión.


def purge_seq(raw):
    """1.3.2: «ESC[3J» (vaciar el historial al borrar), salvo que DLPY_PURGE valga 0 / no / false / off o esté vacía. Sin definir = se manda."""
    raw = "1" if raw is None else raw
    return "" if str(raw).strip().lower() in ("0", "no", "false", "off", "") else "\x1b[3J"


PURGE_SEQ = purge_seq(os.environ.get("DLPY_PURGE"))

# 1.3.2: DLPY_CLEARMODE elige cómo se limpia TODA la consola (siempre incluye vaciar el historial salvo DLPY_PURGE=0). «auto» = como siempre
# (`clear` nativo de a-Shell + vaciar historial). Los demás mandan una secuencia directa; si con «auto» tienes que deslizar tras borrar,
# prueba con «python dlpy.py --cleartest», que los enseña uno a uno y guarda el que elijas.
CLEAR_MODES = (
    ("auto", "como siempre: `clear` nativo de a-Shell + vaciar historial"),
    ("home", "cursor arriba, borrar pantalla, vaciar historial y cursor arriba (ESC[H ESC[2J ESC[3J ESC[H)"),
    ("down", "cursor arriba y borrar hacia abajo, sin empujar nada al historial (ESC[H ESC[J ESC[3J)"),
    ("purge-first", "vaciar el historial primero y borrar después (ESC[3J ESC[H ESC[2J)"),
    ("reset", "reinicio total del terminal (ESC c; en a-Shell puede dejar la consola en negro)"),
)
CLEAR_MODE = (os.environ.get("DLPY_CLEARMODE") or "auto").strip().lower()


def clear_mode_seq(mode, purge=None):
    """1.3.2:"""
    purge = PURGE_SEQ if purge is None else purge
    return {"home": "\x1b[H\x1b[2J" + purge + "\x1b[H", "down": "\x1b[H\x1b[J" + purge,
            "purge-first": purge + "\x1b[H\x1b[2J", "reset": "\x1bc"}.get(str(mode or "").strip().lower())
# 0.8.9: borrado nativo de a-Shell (comando `clear`); DLPY_NATIVECLEAR=0 lo desactiva y usa CLEAR_SEQ
NATIVE_CLEAR = os.environ.get("DLPY_NATIVECLEAR", "1").strip().lower() not in ("0", "no", "false", "")
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


def native_clear(fallback=None, mode=None):
    """ÚNICO punto de borrado de la consola:"""
    if _scm_run() or not sys.stdout.isatty():
        return False
    _sc = globals().get("SCENE")
    if _sc and _sc.get("on"):              # 0.9.3: la escena de --shortcutpick es dueña de la pantalla: nadie la borra
        return False
    ok = False
    try:
        sys.stdout.flush()                 # lo pendiente de Python sale antes que el comando nativo
        mseq = clear_mode_seq(mode or CLEAR_MODE)  # 1.3.2: DLPY_CLEARMODE distinto de «auto»: secuencia directa (ya lleva el historial)
        if mseq is not None:
            sys.stdout.write(mseq)
            sys.stdout.flush()
            return True
        if NATIVE_CLEAR and not _NATIVE_CLEAR_BAD[0]:
            ok = os.system("clear") == 0
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


def wait_terminal_ready(timeout=3.0, force=False):
    """Desde un Atajo, a-Shell arranca el script antes de que su ventana tenga tamaño (ioctl 53x0, LINES=0)"""
    try:
        if not sys.stdout.isatty() or (_scm_run() and not force):
            return False
        end = time.monotonic() + timeout
        prev = None
        while True:
            cur = None
            for _st in (sys.stdout, sys.stderr, sys.stdin):
                try:
                    _sz = os.get_terminal_size(_st.fileno())
                except (OSError, ValueError, AttributeError):
                    continue
                cur = (_sz.columns, _sz.lines)
                break
            if cur is None:
                return False                       # este terminal no informa de su tamaño: no hay nada que esperar
            if cur[0] >= 20 and cur[1] >= 5 and cur == prev:
                return True
            if time.monotonic() >= end:
                return False
            prev = cur if (cur[0] >= 20 and cur[1] >= 5) else None
            time.sleep(POLL_TERM)
    except Exception:
        return False


def early_clear():
    """Lo primero al abrir, borrar la consola (sin banner:"""
    try:
        if os.environ.get("DLPY_EARLYCLEAR", "1").strip().lower() in ("0", "no", "false", ""):
            return False
        if DEBUG or not sys.stdout.isatty() or _scm_run():
            return False
        if any(a.lstrip("-\u2013\u2014").lower().split("=")[0] in ("selftest", "sistema", "perfil", "2shortcuts",
                                                                      "2shorcuts", "scm", "scb")
               for a in sys.argv[1:]):
            return False
        # 1.3.5: como en 0.3.6, el primer borrado es el completo (ESC c: reinicia el terminal y limpia también lo que dejaron las versiones
        # anteriores). Después clear_screen() usa el softclear (sin parpadeo). DLPY_EARLYCLEARMODE=auto|home|down|purge-first|reset;
        # si se define DLPY_CLEARMODE propio, manda ese.
        return native_clear(mode=early_clear_mode(os.environ.get("DLPY_EARLYCLEARMODE"), CLEAR_MODE))
    except Exception:
        return False


wait_terminal_ready()
early_clear()

# ── [A5b] Estilo «Aurora» (el mismo de dlpy_test_panel.py) ──
# DLPY_TRUECOLOR=0: colores básicos · DLPY_ANIM=0: sin animación · DLPY_CLASSIC=1: barra «█░»
def _flag_env(name, default=True):
    v = os.environ.get(name)
    return default if v is None else v.strip().lower() not in ("0", "no", "false", "")


def _env_num(name, default, minimum=0.0):
    """Número de una variable de entorno."""
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return default
    try:
        v = float(raw)
    except ValueError:
        return default
    return v if math.isfinite(v) and v >= minimum else default


# ── Log de debug: con DLPY_DEBUG todo lo que sale en pantalla se copia a dlpy_files/logs/dlpy_debug_<fecha>.log ──
DEBUG_LOG = {"path": None, "fh": None, "lock": threading.Lock()}
_LOG_ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[78=>cDEHMNOZ]")


def _log_line(tag, line):
    fh = DEBUG_LOG["fh"]
    if fh is None:
        return
    with DEBUG_LOG["lock"]:
        fh.write(f"[{time.strftime('%H:%M:%S')} +{time.time() - START_T:8.3f}s] {tag}{line}\n")
        fh.flush()


class _LogTee:
    """Envoltura de sys.stdout / sys.stderr:"""

    def __init__(self, inner, tag):
        self._inner, self._tag, self._buf = inner, tag, ""

    def write(self, text):
        n = self._inner.write(text)
        with quiet("log_tee"):
            if isinstance(text, str) and text:
                parts = _LOG_ANSI.sub("", text).replace("\r\n", "\n").split("\n")
                for i, part in enumerate(parts):
                    self._buf += part
                    if i < len(parts) - 1:                       # hubo salto de línea: se vuelca
                        line = next((x for x in reversed(self._buf.split("\r")) if x), "")
                        self._buf = ""
                        _log_line(self._tag, line)
        return n

    def writelines(self, lines):
        for ln in lines:
            self.write(ln)

    def flush(self):
        return self._inner.flush()

    def __getattr__(self, name):
        return getattr(self._inner, name)


def debug_log_start():
    """Abre el log (solo con DEBUG). Devuelve la ruta o None. Nunca impide que el script arranque."""
    try:
        if not DEBUG or not _flag_env("DLPY_DEBUGLOG", True):
            return None
        if any(a.lstrip("-\u2013\u2014").lower().split("=")[0] == "selftest" for a in sys.argv[1:]):
            return None
        d = os.path.join(FILES_DIR, "logs")
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, "dlpy_debug_" + time.strftime("%Y%m%d_%H%M%S") + ".log")
        DEBUG_LOG["fh"] = open(path, "w", encoding="utf-8", errors="replace")
        DEBUG_LOG["path"] = path
        with quiet("debug_log_start", OSError):
            keep = int(_env_num("DLPY_LOGKEEP", 20, 1))
            old = sorted(n for n in os.listdir(d) if n.startswith("dlpy_debug_") and n.endswith(".log"))[:-keep]
            for n in old:
                os.remove(os.path.join(d, n))
        _log_line("", f"DLpy v{VERSION} · log de debug · {time.strftime('%Y-%m-%d %H:%M:%S %z')}")
        _log_line("", f"plataforma: {sys.platform} · Python {sys.version.split()[0]} · {os.name}")
        _log_line("", "argumentos: " + json.dumps(sys.argv[1:], ensure_ascii=False))
        env = {k: v for k, v in sorted(os.environ.items()) if k.startswith("DLPY_")}
        _log_line("", "variables DLPY_*: " + json.dumps(env, ensure_ascii=False))
        sys.stdout = _LogTee(sys.stdout, "")
        sys.stderr = _LogTee(sys.stderr, "! ")
        atexit.register(debug_log_close)
        return path
    except Exception as _ign:
        DEBUG_LOG["fh"] = None
        return None


def debug_log_close():
    """Al salir: cierra el archivo y avisa de dónde quedó (no en --scm / --scb: su salida es el JSON del atajo)."""
    fh, path = DEBUG_LOG["fh"], DEBUG_LOG["path"]
    if fh is None:
        return
    try:
        for stream in (sys.stdout, sys.stderr):              # lo que quedó sin salto de línea
            buf = getattr(stream, "_buf", "")
            if buf:
                _log_line(getattr(stream, "_tag", ""), buf)
        _log_line("", "── fin del log ──")
        with DEBUG_LOG["lock"]:
            DEBUG_LOG["fh"] = None
            fh.close()
        if not (wants_scm(sys.argv[1:]) or wants_scb(sys.argv[1:])):
            rel = os.path.relpath(path, os.path.dirname(FILES_DIR)) if FILES_DIR else path
            inner = getattr(sys.stdout, "_inner", sys.stdout)
            inner.write(f"\n[debug] Log guardado: {rel}\n")
            inner.flush()
    except Exception as _ign:
        DEBUG_LOG["fh"] = None


TRUECOLOR = USE_COLOR and _flag_env("DLPY_TRUECOLOR", True)
ANIM = sys.stdout.isatty() and not DEBUG and _flag_env("DLPY_ANIM", True)
CLASSIC = _flag_env("DLPY_CLASSIC", False)
FILL, TIP, EMPTY = ("█", "", "░") if CLASSIC else ("━", "╸", "╌")

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
ANIM_LIVE = ANIM                    # animaciones que redibujan en su sitio
CLEAN_LATE = {"on": False}             # 0.8.2: limpieza de archivos antiguos pospuesta al final de la descarga
QUIET = {"on": False}                # 0.8.1: --shortcutpick sin animaciones hasta la intro del sitio
# 0.9.3: escena continua de --shortcutpick (se define más abajo, junto a la intro del sitio). Aquí solo el estado, para que
# _say / native_clear / DownloadUI lo consulten sin importar el orden de las definiciones.
def scene_defaults():
    """1.4.1: el estado inicial de la escena, en un solo sitio (SCENE y scene_start lo usan; antes eran dos listas que se podían desalinear)."""
    return {"on": False, "stop": False, "th": None, "mute": None, "out": None, "geo": None, "a": None, "b": None,
            "name": "", "mode": "both", "mode_orig": "both", "title_raw": "", "t_title": None, "label": "", "pct": None, "frac": 0.0,
            "shown": 0.0, "lo": 0.0, "hi": 0.0, "rows": 24, "brand": False, "busy": False, "t_out": None, "k_out": None, "t_in": None, "resume": False,
            "aspect": None, "asp_shown": None, "res": None, "alabel": None, "vinfo": {}, "ainfo": {}, "count": 0, "conv": None, "ask": None, "ta": 0.0,
            "done": set(), "done_at": {}, "stream_total": 1, "stream_seen": 0, "type_totals": {}, "type_seen": {}, "last_error": None, "err_brand": False, "emute": None,
            "started": {}, "finished": {}, "last_finished": None, "pp_pct": None, "welcome": None,
            "check": None, "clean": 0, "send_to": None, "dl_done": None, "label_wall": None, "err": None, "link": None, "pip_line": None, "ana_raw": False,
            "skind": {}, "spct": {}, "slang": {}, "past_dl": False, "motivo": ""}      # 1.4.5: qué es y cuánto lleva cada pista, si ya empezó la descarga y el nombre del motivo del centro


SCENE = scene_defaults()


def quiet_set(on):
    """Apaga (True) o devuelve (False) las animaciones. Solo --shortcutpick lo usa, hasta justo antes de la intro."""
    global ANIM_LIVE
    QUIET["on"] = bool(on)
    ANIM_LIVE = False if on else ANIM


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


def mix6(a, b, k):
    """mix(a, b, k) con k acotado a 0–1 y en 6 pasos (menos cambios de color por fila = menos bytes)."""
    return mix(a, b, round(max(0.0, min(1.0, k)) * 6) / 6.0)


def grad(text, a=0.0, b=1.0):
    """Degradado naranja → magenta en 12 tonos: un código de color por tramo, no por letra (menos bytes por línea)."""
    if not text or not USE_COLOR:
        return text
    n = len(text)
    if not TRUECOLOR:
        h = n // 2
        return paint(text[:h], "orange") + paint(text[h:], "magenta")
    cols = theme_rgb()
    out, last = [], None
    for i, ch in enumerate(text):
        c = mix(cols[0], cols[1], round((a + (b - a) * (i / (n - 1) if n > 1 else 0.0)) * 11) / 11.0)
        if c != last:
            out.append(f"\x1b[38;2;{c[0]};{c[1]};{c[2]}m")
            last = c
        out.append(ch)
    return "".join(out) + RESET


def dot(color):
    return paint("●", color)


def flag_mark(k):
    return paint(FLAG_MARKS[k], FLAG_COLORS[k])


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
    """Mide el ancho REAL del terminal preguntándoselo:"""
    flag = os.environ.get("DLPY_PROBE", "").strip()
    if flag != "1":                           # solo con DLPY_PROBE=1
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


def nowrap(text):
    """Apaga el salto automático de línea mientras se escribe `text`."""
    return WRAP_OFF + text + WRAP_ON if sys.stdout.isatty() else text


ACTIVE_BAR = None


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


def _say(color, msg, mark=None):
    # 1.0.4: con escena activa los errores no rompen la animación, van a shortcutmode.log y se integran en D L P Y
    if SCENE["on"]:
        if color != "red":
            dbg("escena: aviso omitido", msg)
            return
        # error en escena: loguear y pasar a D L P Y en vez de cortar
        try:
            log_shortcutmode_error(msg)
        except Exception:
            pass
        try:
            scene_set_error(msg)             # 1.0.8: D L P Y con el error (texto limpio)
            # no detener la escena, solo mostrar D L P Y
            dbg("escena: error integrado en D L P Y", msg)
            return
        except Exception as _ign:
            try:
                ignore("scene error integrate", _ign)
            except Exception:
                pass
            # fallback antiguo: parar
            try:
                scene_stop(clear=True)
            except Exception:
                pass
    lines = wrap_text(msg, term_width() - 2)
    # también loguear errores aunque no haya escena (para shortcutmode.log)
    if color == "red":
        try:
            log_shortcutmode_error(msg)
        except Exception:
            pass
    b = ACTIVE_BAR
    if b is not None and b.th:
        with b.lock:
            b._erase()
            _say_lines(color, lines, mark)
    else:
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
    _say("amber", msg, "!")


def m_info(msg):
    _say("orange", msg)


def m_err(msg):
    _say("red", msg, "✕")


def note(text):
    """Texto de apoyo en gris, sangrado 2 columnas (como los subtítulos de dpt)."""
    for ln in wrap_text(text, term_width() - 2):
        print("  " + paint(ln, "gray"))


def hint(text):
    """Ayuda de un prompt:"""
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


debug_log_start()                          # 0.8.6: con DLPY_DEBUG, el log también va a dlpy_files/logs/


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
SESSION = {"adult": False, "tag": None}
# 0.7.8: colores del sitio para la pantalla de descarga (los fija site_theme_apply; None = naranja→magenta de siempre)
THEME = {"a": None, "b": None, "full": None}


def theme_rgb():
    """(color 1, color 2) del degradado: los del sitio si hay tema (también los adultos); si no, naranja→magenta."""
    if THEME["a"] and THEME["b"]:
        return THEME["a"], THEME["b"]
    return PALETTE["orange"][0], PALETTE["magenta"][0]
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
    with quiet("roast_say"):
        _say("magenta", text)
        if pin:
            PINNED.append(text)
            del PINNED[:-4]


def show_pinned():
    if not ROAST:
        return
    for t in PINNED:
        with quiet("show_pinned"):
            _say("magenta", t)


# Sitio adulto (1.0.7): ya NO tiene animación, etiqueta ni interfaz propias. Pasa por la misma intro y la misma escena
# que todos los sitios (con sus colores en SITE_THEMES) y la animación sigue a lo que se descarga. Aquí solo se anota
# que es adulto para los comentarios (chistes); nada de esto toca lo que se ve.
def adult_alert():
    """Sitio adulto detectado (una sola vez por ejecución): solo se anota para los comentarios."""
    SESSION["adult"] = True


# ───────────────────── Sitios populares: intro de 1 s y etiqueta del banner ─────────────────────
# Antes de la pantalla de descarga sale una intro mínima con los colores del sitio y una forma según lo que se
# baja (video, audio, video+audio, lista o en vivo). La etiqueta (« YT ►♪ ») vuela a la esquina del borde de la
# tarjeta y queda ahí: es el mismo sitio donde el banner la pinta tras el clear_screen de la descarga.
SITE_ANIM = _flag_env("DLPY_SITEANIM", True)       # DLPY_SITEANIM=0 la apaga
SITE_SECS = 2.0                                    # duración de la intro (s)
SITE_HOLD_AT = 0.58                                # punto de la intro (0–1) donde espera si el análisis sigue en curso
SITE_HOLD_MAX = 20.0                               # tope de la espera (s)
SITE_FPS = 24
SITE_GLITCH = "▒░#@%&$/\\|<>=+*"
SITE_ICON = {"video": "►", "audio": "♪", "both": "►♪", "list": "≡►", "live": "●"}
SITE_THEMES = [
    (("youtube.com", "youtu.be"), "YouTube", "YT", "#ff2b3d", "#ff9aa4"),
    (("tiktok.com",), "TikTok", "TT", "#25f4ee", "#fe2c55"),
    (("instagram.com",), "Instagram", "IG", "#feda75", "#d62976"),
    (("twitter.com", "x.com"), "X / Twitter", "X", "#e7e9ea", "#1d9bf0"),
    (("facebook.com", "fb.watch"), "Facebook", "FB", "#1877f2", "#6aa8ff"),
    (("twitch.tv",), "Twitch", "TW", "#9146ff", "#c9a8ff"),
    (("vimeo.com",), "Vimeo", "VM", "#1ab7ea", "#7fdcf5"),
    (("soundcloud.com",), "SoundCloud", "SC", "#ff5500", "#ffb184"),
    (("bandcamp.com",), "Bandcamp", "BC", "#1da0c3", "#8fe0f2"),
    (("reddit.com", "redd.it"), "Reddit", "RD", "#ff4500", "#ff9a70"),
    (("dailymotion.com", "dai.ly"), "Dailymotion", "DM", "#0a7cff", "#7fb8ff"),
    (("bilibili.com", "b23.tv"), "Bilibili", "BL", "#00a1d6", "#fb7299"),
    (("kick.com",), "Kick", "KK", "#53fc18", "#b6ff94"),
    (("rumble.com",), "Rumble", "RB", "#85c742", "#d2f0ac"),
    (("mixcloud.com",), "Mixcloud", "MX", "#7a4dff", "#c1a8ff"),
    (("odysee.com",), "Odysee", "OD", "#ef1970", "#ff8fba"),
    (("vk.com", "vkvideo.ru"), "VK", "VK", "#0077ff", "#7db6ff"),
    (("pinterest.com", "pin.it"), "Pinterest", "PI", "#e60023", "#ff8a9a"),
    (("imgur.com",), "Imgur", "IM", "#1bb76e", "#8cf0c1"),
    (("linkedin.com",), "LinkedIn", "LI", "#0a66c2", "#7db7ee"),
    (("archive.org",), "Archive.org", "IA", "#c8c8d4", "#7a7a8c"),
    # 1.0.7: los sitios adultos tienen sus colores, como el resto (los que no están aquí usan el color sacado del nombre)
    (("pornhub.com",), "Pornhub", "PH", "#ff9000", "#ffd08a"),
    (("xvideos.com",), "XVideos", "XV", "#e5222e", "#ff9aa1"),
    (("xnxx.com",), "XNXX", "XN", "#2f5bff", "#9db4ff"),
    (("xhamster.com", "xhamster.desi", "xhamster2.com", "xhamster3.com"), "xHamster", "XH", "#ff5a2b", "#ffb393"),
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
    (("bongacams.com",), "BongaCams", "BC", "#e3262d", "#ff9fa3"),
    (("onlyfans.com",), "OnlyFans", "OF", "#00aff0", "#8fdcf9"),
    (("fansly.com",), "Fansly", "FS", "#2e9bff", "#9fd0ff"),
    (("rule34.xxx", "rule34.paheal.net"), "Rule34", "R3", "#2fbf71", "#9be6bd"),
    (("brazzers.com",), "Brazzers", "BZ", "#f5c400", "#ffe88a"),
    (("thisvid.com",), "ThisVid", "TV", "#a855f7", "#d9b4fb"),
]


def _rn(s):
    """Ruido determinista 0–1 (la intro se ve igual en cada ejecución)."""
    s = math.sin(s * 127.1) * 43758.5453
    return s - math.floor(s)


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
    if info is None:                          # intro temprana (--shortcutpick): aún no hay análisis, manda lo que eligió el atajo
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


def reset_site_state():
    """Entre dos descargas seguidas (menú de pendientes): la siguiente vuelve a elegir tema y etiqueta."""
    SESSION["adult"], SESSION["tag"] = False, None
    THEME["a"] = THEME["b"] = THEME["full"] = None


def early_site_intro(run):
    """--shortcutpick:"""
    try:
        if getattr(run, "spick", None) is None or not _flag_env("DLPY_EARLYINTRO", True):
            return                           # DLPY_EARLYINTRO=0: la intro sale justo antes de la descarga
        args = getattr(run, "cli_args", None) or []
        if not args or not str(args[0]).strip():
            return
        link = str(args[0]).strip()
        run.link = link
        if scene_start(run):                 # 0.9.3: la intro sigue como escena viva hasta enviar el archivo al atajo
            run.site_shown = True
            return
        was_quiet = QUIET["on"]
        if was_quiet:
            quiet_set(False)                 # la intro es la única animación permitida
        try:
            if site_intro(run):
                run.site_shown = True
        finally:
            if was_quiet:
                quiet_set(True)
    except KeyboardInterrupt:
        raise
    except Exception as _ign:
        ignore("early_site_intro", _ign)


# ── Motivo de video / audio (1.0.0) y dibujos del centro (1.0.2) ──
# El video ya no es una barra: es un marco cuya proporción sale del video (vertical, cuadrado u horizontal; una celda del terminal
# mide ~1×2) con una imagen «viva» dentro y un ► que respira; con resolución baja (≤480p) la imagen es de bloques gordos.
# 1.0.2: ese es el dibujo del sitio; el centro de la escena tiene otros dos (la conversión y DLPY, más abajo, junto a
# scene_motif) y cada uno se mueve solo mientras es el que se ve y a su propio ritmo, para no saturar la terminal.
MOTIF_FPS = 12           # cuadros por segundo del dibujo del video/audio
BOTH_BARS_ROWS = 5          # alto de las barras junto al marco (1.4.2: el del marco; las dos tarjetas van en la fila de debajo)
BOTH_GAP, BOTH_EQW = 2, 9      # video + audio: hueco entre el marco y las barras y ancho de las 5 barras (18 + 2 + 9 = 29 = la regla)
MOTIF_ROWS = 5           # alto del motivo (filas)
SCENE_SWAP = 0.325       # (1.5.5: 0.65 → 0.325, el doble de rápido) s que tarda un dibujo del centro en volverse otro (1.4.2: 0.55 → 0.65, el viaje de las celdas necesita un poco más)
BADGE_ROW = MOTIF_ROWS   # 1.4.2: fila (desde lo alto del dibujo) de la tarjeta que cambia: justo DEBAJO del marco del video
# Filas de la escena (desde la regla de arriba, y0): regla 0 · título 2 · dibujo del centro 4 … 8 · tarjeta 9 · UNA FILA EN BLANCO (10) · texto de estado 11.
# Todo lo que se agregue debajo del dibujo (preguntas, avisos) cuelga de SCENE_STATUS_ROW, nunca de un número suelto, y SCENE_ROWS es el alto total
# (para centrar la escena en la pantalla).
SCENE_STATUS_ROW = 4 + BADGE_ROW + 2                   # el dibujo empieza en y0+4; la tarjeta va BADGE_ROW filas más abajo; luego el aire y el texto
SCENE_ROWS = SCENE_STATUS_ROW + 2
CONV_FPS = 12            # cuadros por segundo de la escena mientras convierte
CONV_FLOW, CONV_PACK = 5.0, 6.0   # 1.2.1: celdas por segundo y separación (celdas) de los paquetes ● • · que cruzan la vía de la conversión
CONV_KEY_FADE = 0.35     # 1.2.1: s que tarda en apagarse la tecla Enter al pasar de la pregunta a la conversión
CONV_RUN_FPS = 8         # 1.2.1: cuadros por segundo del dibujo de conversión mientras ffmpeg trabaja (ligero, para no quitarle CPU)
DLPY_FPS = 15            # cuadros por segundo de la escena DLPY
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
    odd = 2 * int(round((MOTIF_ROWS * 2 * asp - 1) / 2.0)) + 1       # el impar más cercano: así el ► y las tarjetas caen en la columna central
    room = max(7, int(room))
    return max(7, min(odd, room if room % 2 else room - 1))


# 1.0.7: etiqueta dentro del dibujo del centro. En vez del ► del video va la resolución corta (SD, HD, FHD, 2K, 4K, 8K); el resto
# de tipos llevan lo mismo bajo su dibujo: audio → formato (M4A, MP3, OPUS…), directo → LIVE, lista → ×N. Mientras no se sabe el
# dato se queda el ► (video) o nada, y al conocerse la etiqueta cambia con el mismo ruido (glitch) que el título y el texto.
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
    near = [r for r in RES_LADDER if abs(eff - r) <= 0.06 * r]      # 1.4.2: se muestra la resolución de verdad, no un cubo (360p ya no sale como 480p)
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
            continue                                   # 1.3.6: un stream de solo audio no aporta ni fps ni bitrate de video
        if "codec" not in out and vc not in ("none", "", "unknown") and not d.get("_guess"):    # 1.3.6: el códec supuesto no es un dato
            out["codec"] = vc.split("+")[0]
        muxed = str(d.get("acodec") or "none").lower() not in ("none", "")
        for key, fields in (("fps", ("fps",)), ("kbps", ("vbr", "tbr"))):
            for fld in fields:
                try:
                    v = float(d.get(fld) or 0)
                except (TypeError, ValueError):
                    continue
                if key == "kbps" and fld == "tbr" and muxed:           # 1.4.2: tbr de un stream con audio incluye el audio: se le resta, y sin abr no es dato
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


PH_VIDEO = {"res": "\u00bfRES?", "codec": "\u00bfCOD?", "fps": "\u00bfFPS?", "kbps": "\u00bfBIT?"}     # lo que no se pudo determinar (5 caracteres: impar, centrado)
PH_AUDIO = {"codec": "\u00bfCOD?", "kbps": "\u00bfBIT?", "hz": "\u00bfKHZ?"}


def vinfo_labels(res, asp, vinfo=None):
    """Lista de etiquetas del video en el orden en que fluyen: resolución, códec, fps, bitrate (con ¿?  lo que no se sabe una vez leído el stream)."""
    vi = vinfo or {}
    ph = bool(vi.get("settled"))                       # ya se intentó leer el stream: lo que falta se marca
    cand = [res_badge(res, asp) or (PH_VIDEO["res"] if ph else None),
            (codec_label(vi.get("codec")) if vi.get("codec") else None) or (PH_VIDEO["codec"] if ph else None),
            (fps_label(vi.get("fps")) if vi.get("fps") else None) or (PH_VIDEO["fps"] if ph else None),
            (kbps_label(vi.get("kbps")) if vi.get("kbps") else None) or (PH_VIDEO["kbps"] if ph else None)]
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
        if "codec" not in out and ac not in ("none", "", "unknown") and not d.get("_guess"):    # 1.3.6: el códec supuesto no es un dato
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
    return ("%03dkb" % round(k)) if k < 999.5 else ("%.1fMb" % min(9.9, k / 1000.0))


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
    cand = [odd_label(alabel) if alabel else (PH_AUDIO["codec"] if ph else None),
            abr_label(ai.get("kbps")) or (PH_AUDIO["kbps"] if ph else None), asr_label(ai.get("hz")) or (PH_AUDIO["hz"] if ph else None)]
    return [c for c in cand if c]


def flow_pick(labels, ta):
    """La etiqueta que toca en el instante ta (relativo al arranque de la rotación)."""
    return labels[int((ta or 0.0) / VINFO_SECS) % len(labels)] if labels else None


def badge_texts(mode, res=None, asp=None, alabel=None, count=0, vinfo=None, ta=None, ainfo=None):
    """Textos de las etiquetas por dibujo: v (dentro del marco del video), a (bajo el ecualizador), l (directo / lista)."""
    tv, tau = (ta.get("v"), ta.get("a")) if isinstance(ta, dict) else (ta, ta)    # relojes de rotación (arrancan cuando hay dato)
    out = {"v": flow_pick(vinfo_labels(res, asp, vinfo), tv) or "►"}              # 1.1.0: fluye por resolución / códec / fps / bitrate
    al = audio_labels(alabel or (acodec_label((ainfo or {}).get("codec")) if mode in ("audio", "both") else None), ainfo) \
        if (alabel or mode in ("audio", "both")) else []
    if al:                                                                        # 1.1.0: también en «video + audio» (bajo las barras)
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
    x0, fq = xc - n // 2, int(ta * MOTIF_FPS)
    pulse = 0.5 + 0.5 * math.sin(ta * 2.2)
    bg = mix(BLACK, g(0.5), 0.30 * fd)
    for i in range(-pad, n + pad):
        if 0 <= i < n:
            if p >= 1.0 or p > 0.15 + 0.25 * i:
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
    tq = int(ta * MOTIF_FPS) / float(MOTIF_FPS)
    for i in range(fw):                                              # el marco: esquinas redondeadas y degradado del sitio
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
            elif r == ih // 2 and abs(i - iw // 2) == 1:              # 1.2.6: aire a los lados del ► (como un play real)
                ch = " "
            cells[(left + 1 + i, top + 1 + r)] = (ch, mix(BLACK, col, fd), None)
    if badge is not None and badge[0] != "►":                        # 1.4.2: la tarjeta bajo el marco, centrada en él (sin dato no hay tarjeta)
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
    g = lambda k: mix6(a, b, k)                                    # degradado en 6 pasos: menos cambios de color por fila = menos bytes

    n = int(round(smooth(u / 0.30) * 14))
    for d in range(-n, n + 1):
        put(cx + d, y0, "─", g((d + 14) / 28.0))
    if u < 0.45:                                             # chispas de glitch al arrancar
        for i in range(10):
            if _rn(f * 13 + i) < 0.5 * (1 - u / 0.45):
                put(cx + (_rn(f * 7 + i) - 0.5) * 34, y0 + _rn(f * 3 + i) * 4,
                    SITE_GLITCH[int(_rn(f + i * 5) * len(SITE_GLITCH))], g(_rn(i + f)))
    label = " ".join(name.upper())
    x0 = cx - len(label) // 2
    if u > 0.12:
        for i, ch in enumerate(label):
            if ch != " ":
                ok = u > 0.18 + i * 0.012
                put(x0 + i, y0 + 2, ch if ok else SITE_GLITCH[int(_rn(f + i) * len(SITE_GLITCH))],
                    g(i / float(len(label))) if ok else mix(g(0.5), BLACK, 0.5))
    if u > 0.28:
        fd = smooth((u - 0.28) / 0.2)
        tt, y = float(int(ta * MOTIF_FPS)) * 12.0 / MOTIF_FPS, y0 + 4
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
                if bd.get("a"):                                  # 1.1.0: la etiqueta del audio, centrada bajo las barras (1.4.2: en la fila de la del video)
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


def site_wait():
    """True mientras sigue en curso un análisis del enlace en segundo plano (--scm / --scb): la intro espera."""
    try:
        th = SCM.get("thread")
        return bool(th is not None and th.is_alive())
    except Exception as _ign:
        ignore("site_wait", _ign)
        return False


def site_intro(run):
    """Intro de SITE_SECS antes de la pantalla de descarga:"""
    if not SITE_ANIM:
        return False
    if not (ANIM_LIVE and USE_COLOR and TRUECOLOR and sys.stdout.isatty() and not DEBUG):
        return False
    hide_keyboard()                          # el alto del terminal cambia al bajar el teclado: se mide ya estable
    settle_terminal()
    try:
        rows = term_rows()
    except (OSError, ValueError):
        return False
    sw = safe_width()                        # el mismo ancho útil que la tarjeta y el banner (en --scm/--shortcutpick
    W, Hh = sw + 1, min(rows, ui_lines())    # las columnas de shutil no coinciden con lo que se ve)
    if sw < 30 or Hh < 16:
        return False
    info = getattr(run, "info", None) or {}
    name, sig, a, b = (site_theme_apply(run)
                       or site_theme(_host(run.link), info.get("extractor_key") or info.get("extractor") or ""))
    mode = site_mode(run)
    vshape = video_shape(getattr(run, "fmt", None), info)
    bdg = {k: (t_, 1.0) for k, t_ in badge_texts(mode, vshape[1], vshape[0], audio_label(getattr(run, "fmt", None)),
                                                 info.get("n_entries"), ainfo=audio_facts(getattr(run, "fmt", None), info)).items()}
    tag = " " + sig + " " + SITE_ICON[mode] + " "
    fg = (0, 0, 0) if (0.3 * a[0] + 0.59 * a[1] + 0.11 * a[2]) > 150 else (255, 255, 255)
    y0 = max(2, (Hh - SCENE_ROWS) // 2)
    ymax = min(Hh, y0 + SCENE_STATUS_ROW + 1)
    cx = W // 2 + 1
    tx = len(f"DLpy v{VERSION}") + 3         # columna donde el encabezado pone la etiqueta: «▍DLpy vX » y luego ella
    try:
        card = [r + " " * max(0, banner_width() - dwidth(r)) for r in banner_rows(banner_width())]
    except Exception as _ign:
        ignore("site_intro card", _ign)
        card = []
    st = {"rows": {}, "rev": 0}

    def sgr(key):
        return RESET + _fg(key[0]) + (_bg(key[1]) if key[1] else "")

    def draw(cells, k, u):
        sx, sy = cx - len(tag) / 2.0, y0 + SCENE_STATUS_ROW
        e = smooth((k - 0.15) / 0.85)
        px, py = int(round(sx + (tx - sx) * e)), int(round(sy + (1 - sy) * e))
        tcells = {}
        if u >= 0.5:                         # la etiqueta: sale del centro y termina en su sitio del encabezado
            tbg = mix((0, 0, 0), a, smooth((u - 0.5) / 0.1))
            for n, ch in enumerate(tag):
                tcells[(max(1, px) + n, py)] = (ch, fg, tbg)
        allc = dict(cells)
        allc.update(tcells)
        rev0 = st["rev"]
        rev1 = min(len(card), int(math.ceil(min(1.0, (k - 0.3) / 0.5) * len(card)))) if (card and k > 0.3) else rev0
        out, wrote = [WRAP_OFF], set()
        for y in range(1, ymax + 1):         # filas completas desde la columna 1 (filas enteras, sin depender del cuadro anterior)
            parts, cur = [], None
            for x in range(1, W):
                c = allc.get((x, y))
                key, ch = (c[1:], c[0]) if c else (None, " ")
                if key != cur:
                    parts.append(sgr(key) if key else RESET)
                    cur = key
                parts.append(ch)
            row = "".join(parts) + RESET
            if row != st["rows"].get(y):     # solo se reenvían las filas que cambiaron
                st["rows"][y] = row
                wrote.add(y)
                out.append(cur_to(y, 1) + row)
        redo = [r for r in range(1, rev1 + 1) if r in wrote or r > rev0]
        for r in redo:                       # el encabezado va encima de las filas que se reescribieron
            out.append(cur_to(r, 1) + card[r - 1] + RESET)
        for (x, y), (ch, f_, b_) in tcells.items():            # la etiqueta, siempre por encima del encabezado
            if y in redo and 1 <= x < W:
                out.append(cur_to(y, x) + sgr((f_, b_)) + ch)
        out.append(RESET + WRAP_ON)
        st["rev"] = rev1
        sys.stdout.write("".join(out))
        sys.stdout.flush()

    now = time.monotonic()
    last_now, tl, ta, waited, last, done = now, 0.0, 0.0, 0.0, -1, False
    full_t, rows_seen = now, rows

    def repaint_all(clear):
        """El terminal pudo redibujarse (teclado de iOS, cambio de alto): se reenvía toda la pantalla."""
        st["rows"].clear()
        st["rev"] = 0
        if clear:
            native_clear(HOME_CLEAR)
    try:
        native_clear(HOME_CLEAR)
        sys.stdout.write(CURSOR_HIDE + RESET)
        while not done:
            now = time.monotonic()
            dt, last_now = now - last_now, now
            ta += dt
            if tl >= SITE_HOLD_AT * SITE_SECS and waited < SITE_HOLD_MAX and site_wait():
                waited += dt                 # análisis en curso: la línea de tiempo espera, la escena sigue viva
                tl = SITE_HOLD_AT * SITE_SECS
            else:
                tl += dt
            done = tl >= SITE_SECS
            tl = min(tl, SITE_SECS)
            f = int(ta * SITE_FPS)
            if f != last or done:
                last = f
                try:
                    rows_now = term_rows()
                except (OSError, ValueError):
                    rows_now = rows_seen
                if rows_now != rows_seen:            # cambió el alto: se limpia y se repinta todo
                    rows_seen, full_t = rows_now, now
                    repaint_all(True)
                elif now - full_t >= 0.35:           # refresco completo periódico (por si el terminal borró algo)
                    full_t = now
                    repaint_all(False)
                cells, k = site_scene(tl, W, y0, a, b, name, mode, f, ta, vshape, bdg)
                draw(cells, k, tl / SITE_SECS)
            if not done:
                time.sleep(SITE_IDLE)
        SESSION["tag"] = (tag, a, fg)
    finally:
        sys.stdout.write(RESET + WRAP_ON + CURSOR_SHOW)
        sys.stdout.flush()
    return True


# ───────────────────── Escena continua de --shortcutpick (0.9.3) ─────────────────────
# Con --shortcutpick la intro del sitio no se deshace: sigue como una escena viva que NO imprime líneas nuevas.
# El nombre del sitio se transforma (glitch) en el título del video; debajo va UN solo texto con el proceso en curso
# (analizando, descargando con %, uniendo, guardando, enviando); la regla de arriba hace de barra de progreso y el glifo
# (video / audio) sigue en movimiento. Al final: «Enviando a DLpy», la disolución de siempre (outro_clear) y el atajo.
# Un hilo pinta la escena; mientras tanto stdout está silenciado (_SceneMute) para que ningún mensaje, barra, banner o
# tarjeta del resto del script la pise. Un error (m_err), una pregunta pendiente o pip la cortan y todo sale como antes.
# 0.9.4: las actualizaciones se buscan dentro de la escena (título «D L P Y», regla que barre, texto de lo que hace, sin preguntas)
# y la salida es propia: «Enviando a DLpy» y la escena se cierra hacia el centro (scene_dissolve) antes de borrar la pantalla.
# 1.0.2: el centro de la escena cambia de dibujo según lo que pasa (el del sitio, la escena de conversión o la escena DLPY): ver
# scene_motif. Los cambios usan el mismo ruido que el título y el texto, y la escena solo sube a 24 cuadros mientras algo se transforma.
# 1.1.3: el centro tiene tres dibujos más según el paso (unión, guardado y envío): ver scene_merge_cells, scene_save_cells y scene_send_cells.
# 1.2.9: dos más para el arranque: «Primera ejecución» (scene_first_cells) y «Actualizado» (scene_updated_cells); ver scene_welcome.
# 1.4.2: el paso de un dibujo del centro a otro es un morph (las celdas viajan; ver «Motor de morph del centro») y la tarjeta del video va bajo el marco.
SCENE_ON = _flag_env("DLPY_SCENE", True)           # DLPY_SCENE=0: --shortcutpick vuelve a intro + panel + tarjeta
SCENE_MORPH = 0.4                                   # s que tarda el texto de estado en cambiar
SCENE_TITLE_MORPH = 0.5                             # s que tarda el sitio en volverse el título del video
SCENE_BRAND = "DLPY"                                # el título durante las actualizaciones y el envío
SCENE_DWELL = 0.9                                   # s que se deja leer un resultado de la búsqueda de actualizaciones


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


UX_SECS_DEFAULT = 2.0                                # 1.4.8: segundos por escena si piden «segundos» sin número (nombre antiguo)
UX_WAIT = ("wait", "espera", "esperar", "loop")      # 1.5.1: nombres de los tres modos de DLPY_UX (el primero de cada fila es el de la configuración; los demás, los de antes)
UX_NOW = ("real", "ya", "inmediato", "ahora", "now")
UX_SECS = ("segundos", "seg", "secs", "s")


def ux_mode_parse(raw, secs=None):
    """1.5.1: DLPY_UX en una sola opción → el mismo (modo, segundos) de scene_mode_parse. «wait»: cada escena espera a que acabe su animación ·
    «real»: el transcurso real, cada animación entra conforme al proceso (haya terminado o no la anterior) · un NÚMERO: cada escena dura N s.
    Lo inválido cae en wait. Siguen valiendo «espera», «ya», «segundos» (con `secs` = DLPY_UX_SECS) y el DLPY_SCENE_MODE de antes."""
    s_ = str(raw or "").strip().lower()
    if s_ in UX_WAIT:
        return ("loop", None)
    if s_ in UX_NOW:
        return ("real", None)
    if s_ in UX_SECS:
        mode = scene_mode_parse(secs if str(secs or "").strip() else UX_SECS_DEFAULT)
        return mode if mode[0] == "secs" else ("secs", UX_SECS_DEFAULT)
    return scene_mode_parse(s_)


SCENE_MODE = ux_mode_parse(os.environ.get("DLPY_UX") or os.environ.get("DLPY_SCENE_MODE"), os.environ.get("DLPY_UX_SECS"))   # DLPY_UX=wait | real | <segundos>; DLPY_SCENE_MODE=loop | real | <segundos> sigue valiendo
SCENE_OUTRO_SECS = 0.9                              # s que tarda la escena en cerrarse hacia el centro
SCENE_LAG_MOTIF = 0.05                              # (1.5.5: 0.10 → 0.05) 1.0.6: s que espera el dibujo del centro tras el título (cascada)
SCENE_LAG_LABEL = 0.18                              # 1.0.6: s que espera el texto de estado tras el título (cascada)
SCENE_BAR_RATE = 3.9                                # 1.0.6: suavizado de la regla (1/s; equivale a 0.15 por cuadro a 24 fps)
SCENE_ASP_RATE = 3.1                                # 1.0.6: suavizado de la proporción del marco (1/s)
SCENE_BUSY_RATE = 9.0                               # 1.0.6: fundido barrido de espera ↔ barra de progreso (1/s)
SCENE_PIP = _flag_env("DLPY_SCENE_PIP", True)       # DLPY_SCENE_PIP=0: pip siempre cede la escena (escribe directo al terminal)
SCENE_WHITE, SCENE_GRAY, SCENE_DIM = (236, 236, 242), (154, 154, 168), (96, 96, 110)
SCENE_CALM = _flag_env("DLPY_SCENE_CALM", False)     # 1.4.4: 1 = sin ruido en los cambios de texto y texto tenue más claro
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
                log_shortcutmode_error("stderr: " + ln)
        return len(text)

    def writelines(self, lines):
        for ln in lines:
            self.write(ln)

    def drain(self):
        """Lo que quedó sin salto de línea también va al log."""
        with self._lock:
            rest, self._buf = _ANSI_RE.sub("", self._buf).strip(), ""
        if rest:
            log_shortcutmode_error("stderr: " + rest)

    def flush(self):
        if self.open:
            return self._inner.flush()
        return None

    def __getattr__(self, name):
        return getattr(self._inner, name)


def scene_ease(cur, tgt, rate, dt):
    """1.0.6:"""
    dt = max(0.0, min(0.25, float(dt)))
    return cur + (tgt - cur) * (1.0 - math.exp(-rate * dt))


def scene_pp_text(name):
    """Texto de estado de un procesador de yt-dlp."""
    low = str(name or "").lower()
    for key, text in SCENE_PP:
        if key in low:
            return text
    return "Finalizando"


STREAM_KINDS = {}      # 1.3.6: format_id → ("video",) / ("audio",) / ("video", "audio"), de la lista de formatos ya analizada


def format_kinds(f):
    """1.3.6: qué trae un formato (ya normalizado): video, audio o los dos en uno. Pura."""
    f = f or {}
    out = []
    if has(f.get("vcodec")) or f.get("height") or f.get("width"):
        out.append("video")
    if has(f.get("acodec")):
        out.append("audio")
    return tuple(out)


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


# ── Motor de morph del centro (1.4.2) ──
# Un dibujo del centro ya no se deshace en ruido para que salga otro: sus celdas VIAJAN al siguiente.
#   · FLIP (First · Last · Invert · Play): se mide el dibujo viejo y el nuevo UNA vez (flow_plan) y cada cuadro solo interpola (flow_frame).
#   · Papeles: cada celda es línea, sombra, barra, punto, marca o texto. Un papel se reparte sobre el mismo papel del otro dibujo (container
#     transform): el marco del video pasa a ser el borde de los chips, el relleno pasa a ser la vía de puntos, las letras viajan a las letras.
#   · Dentro de un papel el reparto es por cuantiles de x: ordenado contra ordenado es el transporte óptimo en 1D (sin cruces). El lado con
#     más celdas se reparte entre las del otro: una celda se divide en varias o varias se juntan en una; nada queda sin pareja.
#   · Coreografía: el contenedor (líneas) sale primero y el contenido lo sigue; del centro hacia afuera; lo que viaja más tarda más; el
#     escalonado es corto para no alargar lo que se percibe (SCENE_SWAP lo acota todo).
#   · Cada celda viaja por un arco de una fila con la curva (0.3, 0, 0.2, 1). Si conserva su papel (línea → línea, letra → letra) viaja con
#     su propio glifo y lo cambia a medio camino; si cambia de papel se condensa en un punto (•), viaja y se expande en el glifo nuevo.
#     Las que no cambian de sitio se reescriben con el ruido de siempre. En p = 0 el cuadro es exactamente el viejo y en p = 1 el nuevo.
#   · Lo que el dibujo vivo agrega o quita después de medir el plan (barras que suben, tarjetas) sale / entra con ruido en su momento.
FLOW_ON = _flag_env("DLPY_SCENE_FLOW", True)      # DLPY_SCENE_FLOW=0: el cambio de dibujo vuelve a ser la disolución en ruido (scene_noise_cells)
FLOW_LEAVE, FLOW_LAND = 0.12, 0.86                # u (avance propio de la celda) en que sale de su sitio y llega al nuevo
FLOW_ROLES = (("line", "─│╭╮╰╯├┤┬┴┼━┃═║╔╗╚╝┌┐└┘▬"), ("shade", "░▒▓"), ("bar", "▁▂▃▄▅▆▇█▀▌▐"),
              ("dot", "●•·○◦∙()›"), ("mark", "►✓✗♪"))
FLOW_ROLE_OF = {ch: role for role, chars in FLOW_ROLES for ch in chars}
FLOW_LEAD = {"line": 0.0, "bar": 0.3, "shade": 0.45, "dot": 0.6, "mark": 0.8, "text": 1.0}      # quién sale antes: el contenedor y luego el contenido


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
    for role in FLOW_LEAD:                                    # en este orden: el resultado no depende del azar de los conjuntos
        A, B = go.get(role, []), gn.get(role, [])
        if A and B:
            pairs += [(s_, d_, role) for s_, d_ in _flow_pair(A, B)]
        else:
            lo += A
            ln += B
    if lo and kn:                                             # un papel que el otro dibujo no tiene: fluye hacia lo que haya (por cuantiles)
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
    if acts:                                                  # el reparto de tiempos ocupa TODA la transición: lo último llega justo en p = 1
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
    for k, c in old.items():                                  # lo que el dibujo viejo tiene ahora y el plan no midió: se apaga con ruido
        if k not in plan["src"]:
            th = 0.05 + 0.40 * _rn(k[0] * 3.7 + k[1] * 11.3)
            if p < th:
                wait[k] = c
            elif p < th + 0.12 and c[0] and dwidth(c[0]) == 1:
                wait[k] = _flow_noise(f, k[0], k[1], a, b)
    for k, c in new.items():                                  # y lo que el nuevo tiene ahora y el plan no midió: entra con ruido
        if k not in plan["dst"]:
            th = 0.55 + 0.33 * _rn(k[0] * 5.1 + k[1] * 2.3)
            if p >= th + 0.12:
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
                elif u < 0.35:
                    wait[(sx, sy)] = co
                elif u < 0.65:
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
            ink = (co[0] if q < 0.5 else cn[0]) if keep else ("•" if (q < 0.1 or q > 0.9) else "·")      # mismo papel: viaja con su glifo
            fly[(xx, max(ymin, min(ymax, yy)))] = (ink, mix(mix(co[1], cn[1], e), WHITE, 0.35 * glow), None)
    out = dict(wait)
    out.update(fly)
    out.update(land)
    return out


def scene_noise_cells(old, new, p, f, a, b):
    """Un dibujo del centro se deshace en otro con ruido (p de 0 a 1). Es el cambio de antes de la 1.4.2; DLPY_SCENE_FLOW=0 lo vuelve a usar."""
    out = {}
    keys = set(old) | set(new)
    if not keys:
        return out
    xs = [k[0] for k in keys]
    mid_x, half = (min(xs) + max(xs)) / 2.0, max(1.0, (max(xs) - min(xs)) / 2.0)
    for key in keys:
        edge = min(1.0, abs(key[0] - mid_x) / half)                  # 1.0.6: 0 = centro … 1 = borde: se deshace desde el centro
        th = (0.62 * edge + 0.38 * _rn(key[0] * 3.7 + key[1] * 11.3)) * 0.55
        if p <= 0 or p < th:
            c = old.get(key)
        elif p < th + 0.35 and p < 1:
            c = (SITE_GLITCH[int(_rn(f + key[0] * 5 + key[1] * 3) * len(SITE_GLITCH))], mix(mix(a, b, 0.5), BLACK, 0.45), None)
        else:
            c = new.get(key)
        if c is not None:
            out[key] = c
    return out


def scene_swap_cells(old, new, p, f, a, b):
    """Un dibujo del centro se vuelve otro (p de 0 a 1), sin estado: mide y reproduce en la misma llamada. La escena viva usa
    scene_flow_step (mide una vez por transición); con DLPY_SCENE_FLOW=0 es scene_noise_cells."""
    if not FLOW_ON:
        return scene_noise_cells(old, new, p, f, a, b)
    if p <= 0.0:
        return dict(old)
    if p >= 1.0:
        return dict(new)
    return flow_frame(flow_plan(old, new), old, new, p, f, a, b)


def scene_flow_step(st, slot, old, new, p, f, a, b):
    """Un cuadro de la transición `slot` de la escena: el plan se mide en el primer cuadro con p > 0 y se reutiliza hasta que acaba
    (st[slot] = None al empezar otra). Si la transición se revierte a mitad, el mismo plan se recorre al revés (flow["rev"])."""
    if not FLOW_ON:
        return scene_noise_cells(old, new, p, f, a, b)
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
    if SCENE_CALM and 0 < p < 1:                              # 1.4.4: modo calmado: el texto viejo se queda y el nuevo entra de golpe, sin ruido
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
        elif p < th + 0.35 and p < 1:
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
    if cv and cv.get("end") is None and cv.get("codec"):      # 1.0.0: mientras convierte, el título es el códec («H E V C»)
        return ("grad", " ".join(ch for ch in str(cv["codec"]).upper() if ch not in ". "))
    if S.get("title_raw"):
        return ("white", S["title_raw"])
    return ("grad", " ".join(str(S.get("name") or "").upper()))


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
        if k >= off - 0.22:                                          # justo antes de apagarse pasa por ruido
            g = mix(a, b, max(0.0, min(1.0, (xx - 1) / float(max(1, W - 2)))))
            ch = SITE_GLITCH[int(_rn(xx * 17 + y * 5 + int(k * 40)) * len(SITE_GLITCH))]
            out[(x, y)] = ("" if c[0] == "" else ch, mix(BLACK, g, 0.55), None)
        else:
            out[(x, y)] = c
    return out


# ── Los tres dibujos del centro de la escena (1.0.3) ──
# El centro (5 filas bajo el título, 6 con la tarjeta del video) muestra uno de tres dibujos y pasa de uno a otro en SCENE_SWAP (1.4.2: sus celdas viajan; antes, ruido que se disuelve):
#   · el del sitio (marco de video, ecualizador, lista o directo) mientras descarga; si son dos pistas (both) y una termina,
#     su dibujo se deshace y el que queda se desliza al centro (0.55 s);
#   · la escena de conversión, solo mientras convierte;
#   · la escena DLPY, con el título «D L P Y»: boot aSH → PY → DLPY con comando contextual.
def scene_chip_text(x):
    """Texto de un chip de la escena de conversión: mayúsculas, solo caracteres de una columna y como mucho 6 («webm» → «WEBM»)."""
    t = " ".join(str(x or "").split()).upper()
    if t.startswith("DOLBY"):
        t = "DV"
    t = "".join(ch for ch in t if ch.isprintable() and dwidth(ch) == 1)
    return t[:6].strip()


# 1.4.1: qué texto de estado pide qué dibujo (1.2.5 revisión · 1.1.3 unión y guardado · 1.1.5 limpieza · 1.1.7 papelera). El resto de
# dibujos lo decide el estado (D L P Y, envío, conversión, pregunta, arranque); todos viven en MOTIFS, más abajo.
MOTIF_LABELS = (("check", ("Revisando",)), ("merge", ("Uniendo", "Ajustando")), ("save", ("Guardando",)),
                ("subst", ("Sustituyendo",)), ("clean", ("Limpiando",)), ("empty", ("Vaciando",)), ("download", ("Descargando",)))


def scene_motif_kind(S):
    """Qué dibujo ocupa el centro:"""
    label = str(S.get("label") or "")
    wl = S.get("welcome")
    if wl and wl.get("kind") in ("first", "updated") and not S.get("last_error"):
        return wl["kind"]                                             # 1.2.9: primera ejecución / actualizado (mandan sobre D L P Y)
    if S.get("brand"):
        return "send" if (label.startswith(("Enviando", "Abriendo")) and not S.get("last_error")) else "dlpy"      # 1.3.4: «Abriendo con view» también
    cv = S.get("conv")
    if cv and cv.get("end") is None:
        return "conv"
    if S.get("ask"):
        return "replace" if (S["ask"] or {}).get("kind") == "replace" else "ask"      # 1.1.9: esperando el Enter de la conversión (1.4.2: o de sustituir un archivo)
    for kind, prefixes in MOTIF_LABELS:                               # 1.4.1: una tabla, no una cadena de «if»
        if label.startswith(prefixes):
            return "rail" if (SCENE_RAIL and kind in RAIL_KINDS) else kind      # 1.4.6: descarga, unión y guardado son tarjetas del mismo carril
    return "idle" if S.get("past_dl") else None                       # 1.4.5: tras la descarga el sitio no vuelve: queda el Pulso entre motivos


def _conv_geo(W, src, dst):
    """1.2.1:"""
    src, dst = str(src or "?")[:6], str(dst or "?")[:6]
    sw, dw = max(7, len(src) + 4), max(7, len(dst) + 4)
    gap = min(17, max(7, W - 4 - sw - dw))
    gap -= 1 - gap % 2
    return src, dst, sw, dw, gap


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
                cells[(x0 + j, y)] = ("·", mix(BLACK, mix(OLD_TONE, g(kw_), kw_), 0.35 + 0.65 * fw_), None)      # punto chico y brillante: así el paquete (· • ●) se distingue
            else:
                cells[(x0 + j, y)] = ("·", mix(BLACK, OLD_TONE, 0.35), None)
            continue
        if j < j0:                                                   # primera mitad: grises
            if n is None:
                cells[(x0 + j, y)] = ("·", mix(BLACK, OLD_TONE, 0.35), None)
            else:
                cells[(x0 + j, y)] = (gl, (mix(OLD_TONE, WHITE, 0.3), mix(BLACK, OLD_TONE, 0.8), mix(BLACK, OLD_TONE, 0.5))[n], None)
            continue
        m = j - j0                                                   # segunda mitad: refinados, con el degradado del sitio
        k = m / max(1.0, cnt - 1.0)
        f = 0.0 if p is None else max(0.0, min(1.0, p * cnt - m)) * fade
        if n is not None:
            cells[(x0 + j, y)] = (gl, (mix(g(k), WHITE, 0.55), mix(BLACK, g(k), 0.85), mix(BLACK, g(k), 0.55))[n], None)
        elif f > 0.0:
            cells[(x0 + j, y)] = ("•", mix(BLACK, g(k), 0.22 + 0.4 * f), None)
        else:
            cells[(x0 + j, y)] = ("·", mix(BLACK, OLD_TONE, 0.35), None)
    return cells


def scene_conv_cells(W, y0, a, b, lt, src, dst, pct=None, key_fade=None):
    """Escena de conversión (1.2.1), filas y0+5 … y0+7:"""
    cells = {}
    src, dst, sw, dw, gap = _conv_geo(W, src, dst)
    left, top = W // 2 + 1 - (sw + gap + dw) // 2, y0 + 5
    try:
        pc = None if pct is None else max(0.0, min(100.0, float(pct)))
    except (TypeError, ValueError):
        pc = None
    p = 1.0 if (pc is not None and pc >= 99.9) else None            # 1.5.6: sin avance en la vía: solo los paquetes; al llegar a 100 % la vía se llena y el destino destella
    g = lambda k: mix6(a, b, k)

    dim = mix(BLACK, OLD_TONE, 0.55)
    x0, y = left + sw, top + 1
    dx = x0 + gap
    heads, h = [], lt * CONV_FLOW                                    # 1.2.8: los paquetes salen del origen (al empezar no hay ninguno a medio camino)
    if h >= gap + 3:
        h -= (int((h - gap - 3) / CONV_PACK) + 1) * CONV_PACK
    while h >= 0.0:                                                  # cabezas a CONV_PACK celdas una de otra
        if h < gap + 3:
            heads.append(h)
        h -= CONV_PACK
    out_hit, in_hit = _conv_near(heads, 0.0, 1.2), _conv_near(heads, float(gap), 1.2)
    dedge = mix(dim, g(1.0), 0.25 if p is None else p)
    dink = mix(OLD_TONE, SCENE_WHITE, min(1.0, 0.35 + (0.25 if p is None else p)))
    if p is not None and p >= 0.999:                                 # 100 %: el destino destella
        flash = 0.5 + 0.5 * math.sin(lt * 9.0)
        dedge, dink = mix(dedge, WHITE, 0.3 + 0.3 * flash), mix(dink, WHITE, 0.5 + 0.5 * flash)
    _scene_chip(cells, left, top, sw, src, dim, OLD_TONE)
    _scene_chip(cells, dx, top, dw, dst, dedge, dink)
    cells[(x0 - 1, y)] = ("│", mix(dim, OLD_TONE, 0.8 * out_hit), None)         # el origen late al soltar un paquete
    cells[(dx, y)] = ("│", mix(dedge, WHITE, 0.55 * in_hit), None)              # el destino, al recibirlo
    skip = set()
    if key_fade is not None and key_fade > 0.0:                      # la tecla Enter de la pregunta se apaga en medio de la vía
        kw = len("Enter" if gap >= 13 else "↵") + 4
        g1 = max(1, (gap - kw) // 2)
        skip = set(range(g1, g1 + kw))
        kf = max(0.0, min(1.0, key_fade))
        _scene_chip(cells, x0 + g1, top, kw, "Enter" if gap >= 13 else "↵", mix(BLACK, mix(dim, g(0.85), 0.6), kf), mix(BLACK, mix(OLD_TONE, SCENE_WHITE, 0.6), kf))
    _conv_lane(cells, x0, y, gap, heads, p, g, skip=skip, whole=True)     # 1.2.8: el avance va en la vía, no en los bordes de abajo
    return cells


WAIT_REHEARSE = 5.5      # 1.2.1: s entre un ensayo y otro de la pregunta de convertir (un paquete cruza la tecla Enter)


def _subst_text(text, s, f):
    """1.4.2: el texto del chip viejo se deshace letra a letra (s de 0 a 1): letra → ruido → punto."""
    out = []
    for i, ch in enumerate(text):
        q = s * 1.6 - i * 0.12
        out.append(ch if q <= 0.0 else SITE_GLITCH[int(_rn(f * 5 + i * 3) * len(SITE_GLITCH))] if q < 0.5 else "·")
    return "".join(out)


def scene_wait_conv_cells(W, y0, a, b, lt, src=None, dst=None, left=99.0, swap=False):
    """Pregunta de convertir (1.2.1), filas y0+5 … y0+7 (1.4.2: swap=True es la de sustituir un archivo: al llegar el paquete el viejo se deshace y el nuevo destella):"""
    cells = {}
    src, dst, sw, dw, gap = _conv_geo(W, src, dst)
    key = "Enter" if gap >= 13 else "↵"
    kw = len(key) + 4
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
    press = max(0.0, 1.0 - abs(hp - (g1 + kw / 2.0)) / (kw / 2.0 + 1.5)) if heads else 0.0     # la tecla se ilumina al pasar
    out_hit, in_hit = _conv_near(heads, 0.0, 1.2), _conv_near(heads, float(gap), 1.2)
    dedge = mix(dim, g(1.0), 0.25 + 0.5 * in_hit)
    if swap:
        sk = 0.0 if hp <= gap else max(0.0, min(1.0, (hp - gap) / 6.0))                 # tras llegar el paquete: 0 → 1
        back = 1.0 if lt < WAIT_REHEARSE else min(1.0, (lt % WAIT_REHEARSE) / 0.45)      # y el viejo vuelve para el siguiente ensayo
        gl = 4.0 * sk * (1.0 - sk)
        _scene_chip(cells, left_x, top, sw, _subst_text(src, sk, int(lt * 12)), mix(dim, BLACK, 0.55 * sk), mix(BLACK, OLD_TONE, (0.35 + 0.65 * back) * (1.0 - 0.7 * sk)))
        _scene_chip(cells, dx, top, dw, dst, mix(dedge, WHITE, 0.45 * gl), mix(mix(OLD_TONE, SCENE_WHITE, min(1.0, 0.6 + 0.4 * in_hit)), WHITE, 0.6 * gl))
    else:
        _scene_chip(cells, left_x, top, sw, src, dim, OLD_TONE)
        _scene_chip(cells, dx, top, dw, dst, dedge, mix(OLD_TONE, SCENE_WHITE, min(1.0, 0.6 + 0.4 * in_hit)))
    cells[(x0 - 1, y)] = ("│", mix(dim, OLD_TONE, 0.8 * out_hit), None)
    cells[(dx, y)] = ("│", mix(dedge, WHITE, 0.55 * in_hit), None)
    trail = max(0.0, min(1.0, (hp - gap // 2) / float(max(1, gap - gap // 2)))) if hp >= g1 + kw else 0.0     # tras la tecla, los puntos se encienden tras el paquete
    gone = 1.0 if hp <= gap else max(0.0, 1.0 - (hp - gap) / 6.0)                                          # y se apagan al llegar
    _conv_lane(cells, x0, y, gap, heads, trail, g, skip=set(range(g1, g1 + kw)), fade=gone)
    key_edge = mix((255, 176, 32), WHITE, 0.3 * pulse) if urgent else mix(dim, g(0.85), 0.35 + 0.35 * breathe + 0.3 * press)
    key_ink = mix((255, 176, 32), WHITE, 0.4 * pulse) if urgent else mix(OLD_TONE, SCENE_WHITE, 0.45 + 0.55 * max(press, 0.3 * breathe))
    _scene_chip(cells, kx, top, kw, key, key_edge, key_ink)
    return cells


SWAP_STREAM_SECS = 0.9                              # 1.4.2: s que cruza el paquete de VIEJO a NUEVO al sustituir; después queda sustituido (✓)


def scene_subst_cells(W, y0, a, b, lt, src="VIEJO", dst="NUEVO"):
    """1.4.2: escena de sustituir un archivo al guardar, filas y0+5 … y0+7: un paquete cruza de VIEJO a NUEVO, el viejo se deshace y el nuevo queda con el ✓."""
    cells = {}
    src, dst, sw, dw, gap = _conv_geo(W, src, dst)
    left, top = W // 2 + 1 - (sw + gap + dw) // 2, y0 + 5
    g = lambda k: mix6(a, b, k)
    dim = mix(BLACK, OLD_TONE, 0.55)
    x0, y, dx = left + sw, top + 1, left + sw + gap
    hp = lt / SWAP_STREAM_SECS * (gap + 3)                           # la cabeza del paquete recorre la vía y un poco más
    heads = [hp] if hp < gap + 3 else []
    done = lt >= SWAP_STREAM_SECS
    sk = max(0.0, min(1.0, (hp - gap) / 6.0)) if hp > gap else 0.0
    k_done = smooth((lt - SWAP_STREAM_SECS) / 0.35)
    in_hit = _conv_near(heads, float(gap), 1.2)
    gl = 4.0 * sk * (1.0 - sk)
    _scene_chip(cells, left, top, sw, _subst_text(src, 1.0 if done else sk, int(lt * 12)), mix(dim, BLACK, 0.55 * max(sk, k_done)),
                mix(BLACK, OLD_TONE, 1.0 - 0.7 * max(sk, k_done)))
    dedge = mix(mix(dim, g(0.85), 0.35 + 0.65 * k_done), WHITE, 0.45 * gl)
    _scene_chip(cells, dx, top, dw, dst, dedge, mix(mix(OLD_TONE, SCENE_WHITE, min(1.0, 0.6 + 0.4 * max(in_hit, k_done))), WHITE, 0.6 * gl))
    cells[(x0 - 1, y)] = ("│", mix(dim, OLD_TONE, 0.8 * _conv_near(heads, 0.0, 1.2)), None)
    cells[(dx, y)] = ("│", mix(dedge, WHITE, 0.55 * in_hit), None)
    if done:                                                         # sustituido: una línea y el ✓ en el medio
        for j in range(gap):
            cells[(x0 + j, y)] = ("✓", mix(SAVED_TONE, WHITE, 0.35 * (1.0 - k_done)), None) if j == gap // 2 \
                else ("─", mix(BLACK, g(j / float(max(1, gap - 1))), 0.3 * k_done + 0.15), None)
    else:
        _conv_lane(cells, x0, y, gap, heads, None, g)
    return cells


DLPY_TYPE_AT, DLPY_TYPE_SECS, DLPY_RUN_SECS = 0.1, 0.6, 0.45      # 1.2.7: la escena D L P Y teclea rápido (0,6 s) y «ejecuta» (Enter + 0,45 s) cada comando
DLPY_STEP_SECS = DLPY_TYPE_AT + DLPY_TYPE_SECS + DLPY_RUN_SECS   # y el texto de estado no pasa al siguiente hasta que termina (scene_status)


DLPY_RUNNING = ("comprobando", "instalando", "actualizando", "analizando")     # 1.3.3: textos de un proceso que sigue en curso


def _dlpy_ctx(label):
    """1.3.3: de qué trata la escena D L P Y según el texto de estado: «analyze» (análisis del enlace, también los de --scb), «ytdlp» (pip y\n    yt-dlp: la fase de paquetes), «github» (DLpy y sus Releases) o «boot». Vale también para los resultados («· última versión»)."""
    low = str(label or "").lower()
    if any(w in low for w in ("analiz", "análisis", "enlace", "límite de tiempo")):
        return "analyze"
    if "actualizaciones" in low or "comprobaciones" in low:      # 1.4.4: las comprobaciones en paralelo (DLpy + pip + yt-dlp a la vez)
        return "check"
    if "yt-dlp" in low or "ytdlp" in low or re.search(r"\bpip\b", low):
        return "ytdlp"
    if "dlpy" in low or "github" in low or "release" in low or "nueva versión" in low:
        return "github"
    return "boot"


def _dlpy_state(label):
    """1.3.3:"""
    low = str(label or "").lower().strip()
    if low.startswith("error") or "no se pudo" in low:
        return "fail"
    if low.startswith(DLPY_RUNNING):
        return "run"
    return "ok" if " · " in low else "run"


def _dlpy_pkg(label):
    """1.3.3: el paquete del texto de estado tal como lo pide pip («yt-dlp-ejs==0.8.0», «yt-dlp» o «pip»)."""
    m = re.search(r"yt-dlp-ejs(?:==[\w.]+)?|yt-dlp|\bpip\b", str(label or "").lower())
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
    if len(cmd) <= room:
        return cmd
    m = re.match(r"^(extract_info\(|yt-dlp -J )(.*?)(\)?)$", cmd)
    if m:
        head, body, tail = m.groups()
        return head + fit_text(body, max(4, room - len(head) - len(tail))) + tail
    if cmd.startswith("GET "):
        host, _sep, path = cmd[4:].partition("/")
        if path:
            cand = f"GET {host}/…/{path.rstrip('/').rsplit('/', 1)[-1]}"
            if len(cand) <= room:
                return cand
    tail = min(9, room // 3)
    return cmd[:max(1, room - 1 - tail)] + "…" + cmd[len(cmd) - tail:]


def _net_line(r, kind=None):
    """1.4.4: el resultado de una operación, en una línea: «200 · 0.4 s · 2026.10.21», «ok · 3.2 s» o la causa del fallo (+ qué pasa después)."""
    if not r:
        return None
    if not r.get("ok"):
        err = str(r.get("err") or "falló")
        return f"{err} · reintenta al abrir" if kind in ("get", "check") else err
    parts = [str(r["code"]) if r.get("code") else "ok", f"{r.get('secs', 0.0):.1f} s"]
    if r.get("val"):
        parts.append(str(r["val"]))
    return " · ".join(parts)


def _dlpy_footer(label, state, ver, name, room):
    """1.4.4: la línea bajo la cadena aSH → PY → DLPY: (texto, color). Mientras corre: el avance (pip en vivo, comprobaciones listas);
    al terminar: lo que de verdad pasó (código, tiempo, versión, o la causa del fallo). Sin datos: «DLpy <versión> · <nombre>» como siempre."""
    ctx, low = _dlpy_ctx(label), str(label or "").lower()
    base = SCENE_GRAY if SCENE_CALM else SCENE_DIM
    text, col = f"DLpy {ver} · {name}", base
    if state == "run":
        if ctx == "check" and PREFETCH.get("n"):
            text = f"{len(PREFETCH['done'])}/{PREFETCH['n']} listas"
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
    """1.3.3:"""
    low = str(label or "").lower()
    ctx = _dlpy_ctx(label)
    if ctx == "ytdlp":
        spec = _dlpy_pkg(label)
        pkg = spec.split("==", 1)[0]
        if _dlpy_local(low):                                            # verificación local de lo instalado («yt-dlp-ejs 0.8.0 · para YouTube»): no se instala nada
            return pkg, f'metadata.version("{pkg}")'                    # lo que hace pkg_version, sin red y sin pip
        return pkg, (f"GET pypi.org/pypi/{pkg}/json" if _dlpy_checking(low) else pip_cmd(pip_args(spec)))     # 1.4.3: la petición real de latest_version (no «curl»)
    if ctx == "check":                                                  # 1.4.4: las peticiones que salen a la vez (las mismas de arriba, en hilos)
        return "actualizaciones", "GET " + (PREFETCH.get("hosts") or "pypi.org · github.com")
    if ctx == "github":
        installing = low.startswith("instalando") or "instalada" in low or "no se pudo instalar" in low
        if installing:                                                  # 1.4.3: esa fase solo escribe el script ya descargado (write_text)
            return "GitHub", "write " + os.path.basename(SCRIPT_PATH)
        info = repo_info()
        return "GitHub", ("GET api.github.com/repos/%s/%s/releases" % info if info else "GET api.github.com/repos/…")
    if ctx == "analyze":
        link = re.sub(r"^https?://", "", str(SCENE.get("link") or "")) or "…"      # 1.4.3: la llamada real de analyze_link, con el enlace real
        if SCENE.get("ana_raw"):                                        # 1.4.4: el último intento sí es el comando `yt-dlp -J <enlace>`
            return "analizando", f"yt-dlp -J {link}"
        return "analizando", f"extract_info({link})"
    return "boot", "python dlpy.py"


def dlpy_type_time(ta, seen_at, enter_at):
    """1.3.3:"""
    return max(0.0, ta - max(seen_at, enter_at + SCENE_SWAP))


DLPY_WAIT_MAX = SITE_SECS + SCENE_SWAP + DLPY_STEP_SECS + 1.0      # 1.3.3: tope de espera: la intro, el cambio del dibujo, un paso y un respiro


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
    end = time.time() + (DLPY_WAIT_MAX if limit is None else limit)
    while S.get("dl_done") != old and time.time() < end and S["on"] and not S.get("stop"):
        time.sleep(0.02)
    return S.get("dl_done") == old


def scene_wait_motif(kind, loop=False, limit=None):
    """1.5.5: espera (modo UX «wait»/«loop» y segundos; nunca en «real») a que el dibujo `kind` ocupe el centro y haya terminado de entrar
    (SCENE["mvis"], que publica scene_motif) y, con `loop`, a que cierre el loop en curso (solo en «wait»). Tope: SCENE_SWAP + 1 s (entrada) o
    MOTIF_HOLD_MAX (loop). True si lo vio; False si no hay escena, hubo error, el hilo no está vivo o se acabó el tope."""
    S = SCENE
    if not S["on"] or SCENE_MODE[0] == "real" or S.get("last_error") or (loop and SCENE_MODE[0] != "loop"):
        return False
    th = S.get("th")
    if th is None or not th.is_alive():
        return False
    t_in = time.time()
    end = t_in + (limit if limit is not None else (MOTIF_HOLD_MAX if loop else SCENE_SWAP + 1.0))
    while time.time() < end and S["on"] and not S.get("stop") and not S.get("last_error"):
        mv = S.get("mvis")
        if mv and mv[0] == kind and mv[1] and (not loop or (mv[2] or 0.0) <= 0.05 and mv[3] >= t_in):      # con loop: una medida NUEVA (no la del cuadro anterior al cambio de estado)
            return True
        time.sleep(0.02)
    return False


def scene_wait_anim(kind, secs):
    """1.5.5: lo que espera el flujo por la animación `kind` según el modo UX. «wait»: a que el dibujo se vea y cierre su loop en curso, y nada
    más (sin pausas fijas) · segundos: esos `secs` (scene_hold) · «real»: nada, el proceso sigue haya terminado o no la animación."""
    if SCENE_MODE[0] == "loop":
        if scene_wait_motif(kind):
            scene_wait_motif(kind, loop=True)
        return
    scene_hold(secs)


def _dlpy_error_line():
    try:
        err = SCENE.get("last_error") if SCENE.get("on") else None
        if err:
            return str(err)[:48]
    except Exception:
        pass
    return None


def _dlpy_title_for_ctx(name):
    return f" a-Shell · {name} "


def scene_dlpy_cells(W, y0, a, b, lt, ver, label="", tt=None):
    """Escena DLPY 1.0.3: boot aSH → PY → DLPY con comando contextual."""
    cells = {}
    fw = max(26, min(52, W - 4))                                          # 1.3.3: hasta 40 · 1.4.4: hasta 52 (cabe «pip install -U yt-dlp-ejs==0.8.0 --no-deps»)
    inner = fw - 2
    left, top = W // 2 + 1 - fw // 2, y0 + 4
    ctx = _dlpy_ctx(label)
    state = _dlpy_state(label)                                            # 1.3.3: run (teclea y gira) · ok / fail (ya ejecutado: ✓ / ✗)
    g = lambda k: mix6(a, b, k)

    for i in range(fw):
        k = i / float(fw - 1)
        first, last = i == 0, i == fw - 1
        cells[(left + i, top)] = ("╭" if first else "╮" if last else "─", g(k), None)
        cells[(left + i, top + 4)] = ("╰" if first else "╯" if last else "─", g(k), None)
    name, cmd = _dlpy_topic(label)                                        # 1.2.7: nombre y comando según el texto de estado
    title = _dlpy_title_for_ctx(name)
    for i, ch in enumerate(title):
        if ch.strip():
            cells[(left + 2 + i, top)] = (ch, SCENE_WHITE if ch != " " else BLACK, None)
    for r in (1, 2, 3):
        cells[(left, top + r)] = ("│", g(0.0), None)
        cells[(left + fw - 1, top + r)] = ("│", g(1.0), None)

    cmd = _dlpy_fit(cmd, max(8, inner - 6))                               # 1.2.6: nunca se sale del marco (1.4.4: el recorte conserva lo importante y siempre dice «…»)
    t = (lt % 6.0) if tt is None else tt                                  # 1.2.7: tt = s a la vista del comando (1.3.3: desde que la escena se ve)
    if state != "run":
        t = DLPY_TYPE_AT + DLPY_TYPE_SECS + DLPY_RUN_SECS + 1.0           # 1.3.3: un resultado ya se ejecutó: el comando está entero y sin destello
    n = int(max(0.0, min(1.0, (t - DLPY_TYPE_AT) / DLPY_TYPE_SECS)) * len(cmd) + 0.5)
    ran = t - (DLPY_TYPE_AT + DLPY_TYPE_SECS)                             # < 0: tecleando; ≥ 0: Enter pulsado y ejecutando
    flash = max(0.0, 1.0 - ran / DLPY_RUN_SECS) if ran >= 0 else 0.0     # el comando se ilumina al pulsar Enter y se apaga
    cells[(left + 2, top + 1)] = ("$", SCENE_GRAY, None)
    for i in range(n):
        if i < len(cmd):
            cells[(left + 4 + i, top + 1)] = (cmd[i], mix(mix(g(i / float(max(1, len(cmd) - 1))), WHITE, 0.35), WHITE, 0.65 * flash), None)
    if ran < 0:
        if n < len(cmd) or int(lt * 2.5) % 2 == 0:
            cells[(left + 4 + n, top + 1)] = ("▌", WHITE, None)
    elif state == "run":                                                   # ejecutando: gira un indicador tras el comando
        cells[(left + 5 + len(cmd), top + 1)] = ("|/-\\"[int(lt * 10) % 4], SCENE_DIM, None)
    else:                                                                  # 1.3.3: terminó: ✓ (salió bien) o ✗ (falló), sin girar
        cells[(left + 5 + len(cmd), top + 1)] = ("✓", (120, 224, 150), None) if state == "ok" else ("✗", (255, 80, 80), None)

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
    elif ctx == "github":
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
        for i, ch in enumerate(txt2[:inner]):
            if ch != " ":
                cells[(left + 1 + (inner - len(txt2)) // 2 + i, top + 3)] = (ch, (255, 80, 80), None)
        # versión en línea superior si hay error? mantenemos versión arriba
        ver_txt = f"DLpy {ver}"
        for i, ch in enumerate(ver_txt):
            if ch != " ":
                # pequeño en esquina
                pass
        return cells

    txt2, fcol = _dlpy_footer(label, state, ver, name, inner - 2)        # 1.4.4: el resultado real de lo que se ejecutó (o su avance en vivo)
    for i, ch in enumerate(txt2):
        if ch != " ":
            cells[(left + 1 + (inner - len(txt2)) // 2 + i, top + 3)] = (ch, fcol, None)
    return cells


# ── Tres dibujos más del centro (1.1.3): unión, guardado y envío ──
# Mismas reglas que la conversión: tres filas (y0+5 … y0+7), colores del degradado del sitio, funciones puras que dependen solo de `lt`
# (segundos desde que empezó el dibujo) y entradas / salidas con el morph de scene_flow_step (1.4.2; antes el ruido de scene_swap_cells).
SCENE_SAVE_SECS = 1.5                               # 1.1.3: s que se deja ver «Guardando» antes de seguir
SCENE_SEND_SECS = 1.25                              # 1.1.3: s que se deja ver «Enviando…» antes de cerrar la escena (antes 0.85)
MERGE_SPEED = 5.0                                   # 1.1.3: celdas por segundo que avanzan los bloques de la unión
SAVE_STREAM_SECS = 0.8                              # 1.1.3: s que fluyen los bloques hacia la carpeta; después queda guardado
SEND_CYCLE = 1.6                                    # 1.1.3: s de un ciclo del envío (vuelo del cometa + onda al llegar)
SAVED_TONE = (120, 220, 140)                        # 1.1.3: el ✓ de «guardado»


def _scene_chip(cells, x0, top, w, text, edge, ink):
    """Un chip redondeado de tres filas (ancho w) con `text` centrado en la fila del medio, dentro de `cells`."""
    for i in range(w):
        first, last = i == 0, i == w - 1
        cells[(x0 + i, top)] = ("╭" if first else "╮" if last else "─", edge, None)
        cells[(x0 + i, top + 2)] = ("╰" if first else "╯" if last else "─", edge, None)
    cells[(x0, top + 1)] = ("│", edge, None)
    cells[(x0 + w - 1, top + 1)] = ("│", edge, None)
    pad = (w - 2 - len(text)) // 2
    for i, ch in enumerate(text):
        if ch != " ":
            cells[(x0 + 1 + pad + i, top + 1)] = (ch, ink, None)
    return cells


def scene_merge_cells(W, y0, a, b, lt):
    """Escena de unión, filas y0+5 … y0+7:"""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    lab = 5 if room >= 27 else 0
    chip_w, merged = (7 if room >= 25 else 5), 4
    lane = max(3, min(9, room - lab - (1 if lab else 0) - 1 - merged - chip_w))
    total = lab + (1 if lab else 0) + lane + 1 + merged + chip_w
    left, top = W // 2 + 1 - total // 2, y0 + 5
    x0 = left + lab + (1 if lab else 0)
    ink = mix(BLACK, OLD_TONE, 0.8)
    for i, ch in enumerate("VIDEO" if lab else ""):
        cells[(left + i, top)] = (ch, ink, None)
    for i, ch in enumerate("AUDIO" if lab else ""):
        cells[(left + i, top + 2)] = (ch, ink, None)
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
    if sw + 5 + len(name) + 4 > room:
        name = "files"
    fw = len(name) + 4
    gap = max(5, min(13, room - sw - fw))
    gap -= 1 - gap % 2
    left, top = W // 2 + 1 - (sw + gap + fw) // 2, y0 + 5
    k_saved = smooth((lt - SAVE_STREAM_SECS) / 0.35)                  # 0 = todavía guardando … 1 = guardado
    dim = mix(BLACK, OLD_TONE, 0.55)
    _scene_chip(cells, left, top, sw, "▓▓▓", mix(g(0.2), dim, k_saved), mix(SCENE_WHITE, OLD_TONE, k_saved))
    _scene_chip(cells, left + sw + gap, top, fw, name, mix(dim, g(0.85), k_saved), mix(OLD_TONE, SCENE_WHITE, k_saved))
    x0, y, mid = left + sw, top + 1, gap // 2
    for j in range(gap):
        k = j / float(max(1, gap - 1))
        if lt >= SAVE_STREAM_SECS:                                    # guardado: una línea y el ✓ en el medio
            if j == mid:
                cells[(x0 + j, y)] = ("✓", mix(SAVED_TONE, WHITE, 0.35 * (1.0 - k_saved)), None)
            else:
                cells[(x0 + j, y)] = ("─", mix(BLACK, g(k), 0.3 * k_saved + 0.15), None)
            continue
        ph = (j - lt * CONV_SPEED * 1.4) % 5.0                        # bloques que se afinan camino de la carpeta
        if ph < 2.0:
            cells[(x0 + j, y)] = (("░▒▓█"[min(3, int(k * 3.0 + (0.0 if ph < 1.0 else 1.0)))]), mix(BLACK, g(0.2 + 0.7 * k), 0.55 + 0.45 * k), None)
        else:
            cells[(x0 + j, y)] = ("─", mix(BLACK, g(k), 0.25), None)
    return cells


CHECK_SPEED = 15.0                                  # 1.2.5: celdas por segundo del barrido de la revisión del archivo
CHECK_TONE = (255, 190, 90)                         # 1.2.5: ámbar de «esto hay que convertirlo»


def _check_fit(rows, room):
    """(anchos de los chips, ancho total, largo máximo del texto) de la revisión para `room` columnas."""
    pad, lim = 4, 6
    while True:
        widths = [max(5, min(lim, len(t)) + pad) for t, _n in rows]
        total = sum(widths) + len(rows) - 1
        if total <= room or (pad <= 2 and lim <= 3):
            return widths, total, lim
        if pad > 2:
            pad = 2
        else:
            lim -= 1


def scene_check_cells(W, y0, a, b, lt, items=None, verdict=None):
    """Escena de revisión (1.2.5), filas y0+5 … y0+7:"""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    rows = [(scene_chip_text(t) or "?", bool(n)) for t, n in (items or [])][:3] or [("?", False)] * 3
    widths, total, lim = _check_fit(rows, room)
    left, top = W // 2 + 1 - total // 2, y0 + 5
    dim = mix(BLACK, OLD_TONE, 0.55)
    pulse = 0.5 + 0.5 * math.sin(lt * 6.0)
    period = 2.0 * total
    s = (lt * CHECK_SPEED) % period
    pos = s if s < total else period - s                              # el haz va y viene
    x, n_ch = left, len(rows)
    for i, ((text, need), w) in enumerate(zip(rows, widths)):
        text = text[:lim]
        if verdict is None:
            near = max(0.0, 1.0 - abs(pos - (x - left + w / 2.0)) / (w / 2.0 + 3.0))
            edge = mix(dim, g(i / float(max(1, n_ch - 1))), 0.2 + 0.8 * near)
            ink = mix(OLD_TONE, SCENE_WHITE, 0.3 + 0.7 * near)
        else:
            base = CHECK_TONE if (verdict == "conv" and need) else SAVED_TONE
            edge = mix(mix(BLACK, base, 0.85), WHITE, 0.25 * pulse)
            ink = mix(base, WHITE, 0.55 + 0.25 * pulse)
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
    dw = max(7, len(dest) + 4)
    track = max(9, min(21, room - dw - 5))
    total = 3 + track + dw
    left, top = W // 2 + 1 - total // 2, y0 + 5
    cyc = lt % SEND_CYCLE
    arrived = cyc >= 1.0
    flash = max(0.0, 1.0 - (cyc - 1.0) / 0.6) if arrived else 0.0
    dim = mix(BLACK, OLD_TONE, 0.55)
    gone = 0.12 < cyc < 1.45                                          # el archivo salió de su chip y vuelve para el siguiente ciclo
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


SCENE_CLEAN_SECS = 1.4                              # 1.1.5: s que se deja ver «Limpiando» antes de seguir
CLEAN_SPEED = 0.9                                   # 1.1.5: ciclos por segundo de los archivos que caen a la papelera


def scene_clean_cells(W, y0, a, b, lt, n=0):
    """Escena de limpieza (1.1.5), filas y0+5 … y0+7:"""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    bw, name = (8, "papelera") if room >= 26 else (5, "trash")
    fw = len(name) + 4
    gap = max(5, min(11, room - bw - fw - 1))
    total = bw + 1 + gap + fw
    left, top = W // 2 + 1 - total // 2, y0 + 5
    bx = left + bw + 1 + gap
    dim = mix(BLACK, OLD_TONE, 0.55)
    hit = 0.0
    for i in range(3):
        ph = ((lt * CLEAN_SPEED + i / 3.0) % 1.0) if n > 0 else 0.0
        keep = bw if n <= 0 else max(1, int(round(bw * (1.0 - 0.9 * ph))))      # la barra se va gastando mientras suelta su bloque
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

    bw, name = (8, "papelera") if room >= 26 else (5, "trash")
    fw = len(name) + 4
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


SCENE_WELCOME_SECS = 2.3                            # 1.2.9: s que se deja ver «Primera ejecución» / «Actualizado» (un loop menos el retraso del dibujo)
WELCOME_CYCLE = 2.4                                 # 1.2.9: s de un ciclo de ambos dibujos (motif_loop_left usa esta cuenta)
WELCOME_FLY = 1.1                                   # 1.2.9: s que tardan los chevrones en cruzar la vía antes de llegar a la versión nueva
WELCOME_ITEMS = ("carpetas", "estado", "listo")     # 1.2.9: los tres pasos de la primera ejecución


def scene_first_cells(W, y0, a, b, lt):
    """Escena de primera ejecución (1.2.9), filas y0+5 … y0+7:"""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    nw = max(len(n) for n in WELCOME_ITEMS)
    bl = max(6, min(14, room - nw - 4))
    total = nw + 1 + bl + 2
    left, top = W // 2 + 1 - total // 2, y0 + 5
    cyc = lt % WELCOME_CYCLE
    dim = mix(BLACK, OLD_TONE, 0.35)
    for i, name in enumerate(WELCOME_ITEMS):
        t0 = 0.1 + 0.5 * i
        f = max(0.0, min(1.0, (cyc - t0) / 0.45))                       # 0 = sin empezar … 1 = terminado
        y = top + i
        ink = mix(OLD_TONE, SCENE_WHITE, 0.3 + 0.7 * smooth(f))
        for c, ch in enumerate(name):
            if ch != " ":
                cells[(left + c, y)] = (ch, ink, None)
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
    cyc = lt % WELCOME_CYCLE
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


# ── Descarga y Pulso (1.4.5) ──
# «Descarga» entra cuando empieza a bajar la primera pista y se queda mientras dure; «Pulso» es el reposo entre motivos una vez que
# la descarga empezó (el sitio ya no vuelve). Mismas reglas que los demás: filas y0+5 … y0+7, funciones puras de `lt`.
DOWN_CYCLE = 1.3                                    # 1.4.5: s de un ciclo de la descarga (a cada pista le cruza un paquete ● • ·)
DOWN_ROWS = 3                                       # 1.4.5: pistas que caben a la vez
DOWN_LABELS = {"video": "VIDEO", "audio": "AUDIO"}
PULSE_CYCLE = 1.6                                   # 1.4.5: s de un ciclo del Pulso (la onda cruza la línea)


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
        out.append((DOWN_LABELS.get(k, "PISTA"), pct, "hecho" if done else ("activa" if n == seen else "espera")))
    return out


def scene_down_cells(W, y0, a, b, lt, rows):
    """Escena de descarga (1.4.5), filas y0+5 … y0+7: una fila por pista con su etiqueta, su barra (se llena con el avance real) y los
    paquetes ● • · que le llegan desde el final de la vía; al terminar la pista queda el ✓. `rows` viene de scene_down_rows."""
    cells = {}
    room = W - 4
    g = lambda k: mix6(a, b, k)

    rows = list(rows or [("VIDEO", None, "activa")])[:DOWN_ROWS]
    nw = 5
    bl = max(6, min(16, room - nw - 4))
    total = nw + 1 + bl + 2
    left, top = W // 2 + 1 - total // 2, y0 + 5
    ys = {1: (1,), 2: (0, 2)}.get(len(rows), (0, 1, 2))
    dim = mix(BLACK, OLD_TONE, 0.35)
    pulse = 0.5 + 0.5 * math.sin(lt * 4.0 * math.pi / DOWN_CYCLE)       # dos latidos por ciclo: el loop cierra limpio
    for i, ((label, pct, state), dy) in enumerate(zip(rows, ys)):
        y = top + dy
        ink = SCENE_WHITE if state == "activa" else mix(BLACK, OLD_TONE, 0.8 if state == "hecho" else 0.6)
        for c, ch in enumerate(label[:nw]):
            cells[(left + c, y)] = (ch, ink, None)
        x0 = left + nw + 1
        if state == "hecho":
            fill = bl
        elif state == "espera":
            fill = 0
        else:
            fill = 1                                                      # 1.5.6: sin avance en la vía (ni con total conocido): solo la cabeza, y los paquetes siguen llegando
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
            pj = int((bl - 1) - u * (span - 1) + 0.5) if span > 1 else fill   # sale del final de la vía y corre hacia la barra
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

    tt = float(int(ta * MOTIF_FPS)) * 12.0 / MOTIF_FPS
    fd = 1.0
    bd = badge or {}                                  # 1.0.7: {"v"|"a"|"l": (texto, avance)}

    def video_cells_at(x_left, y_top, fw):
        return site_video_cells(x_left, y_top, fw, a, b, ta, fd, res, badge=bd.get("v"))

    def chip(key):                                    # la etiqueta bajo el dibujo (audio, directo, lista)
        v = bd.get(key)
        return badge_cells(cx + (0 if key == "a" else 1), y + 4, v[0], v[1], ta, a, b, fd) if v else {}   # 1.1.0: la de audio, justo en el centro del ecualizador

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
        if bd.get("a"):                                          # 1.1.0: la etiqueta del audio, centrada bajo las barras
            v_ = bd["a"]
            both_cells.update(badge_cells(left_both + fw + gap + 4, y + BADGE_ROW, v_[0], v_[1], ta, a, b, fd))     # 1.4.2: en la fila de la del video

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
            return audio_only                                    # 1.4.2: sin transición propia: scene_motif hace el morph
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
    for k in ("v", "a"):                                            # 1.1.0: la rotación arranca cuando aparece el primer dato (la resolución)
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


# ── Registro de dibujos del centro (1.4.1) ──
# Cada dibujo del centro es UNA fila de MOTIFS: cómo se pinta (draw), cuánto le falta a su loop (loop), cómo avanza con el proceso real
# en DLPY_SCENE_MODE=real (real) y si va a CONV_FPS (light). Antes esos cuatro datos estaban repartidos en cinco funciones
# (scene_motif, motif_loop_left, scene_real_lt, scene_fps, scene_motif_kind) y añadir un dibujo obligaba a tocarlas todas.
# Dibujo nuevo = su función *_cells + su draw + su fila aquí + su nombre en MOTIF_NAMES + su texto en MOTIF_LABELS (o su condición en scene_motif_kind).
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
    if S.get("brand"):                                                 # 1.3.3: el texto de estado manda mientras D L P Y es lo actual…
        lab = S.get("label") or ""
        st["dl_last"] = lab
    else:                                                              # …y al deshacerse el dibujo conserva su comando (no pasa a «python dlpy.py»)
        lab = st.get("dl_last") or S.get("label") or ""
    if st.get("dl_lab") != lab:
        st["dl_lab"], st["dl_seen"] = lab, d.ta                        # 1.3.3: cuándo vio la escena este texto
    enter = st["mt"] if (start == st["ms"] and st.get("mt") is not None) else start
    tt = dlpy_type_time(d.ta, st["dl_seen"], enter)                    # el comando se teclea desde que se ve, no desde que cambió el texto
    if S.get("brand") and tt >= (DLPY_STEP_SECS if _dlpy_state(lab) == "run" else 0.0):
        S["dl_done"] = lab                                             # ya se mostró entero: el flujo puede pasar al siguiente texto
    return scene_dlpy_cells(d.W, d.y0, d.a, d.b, d.ta - start, VERSION, lab, tt)


def _draw_conv(S, st, d, start):
    src, dst, _t0 = st.get("cinfo") or (None, None, d.ta)
    t0 = st["mt"] if (start == st["ms"] and st.get("mt") is not None) else start      # 1.2.8: empieza desde el principio (los paquetes salen del origen al verse)
    kf = st.get("key_fade_t")
    kf = None if kf is None else 1.0 - (d.ta - kf) / CONV_KEY_FADE
    return scene_conv_cells(d.W, d.y0, d.a, d.b, scene_real_lt(S, st, "conv", d.ta - t0), src, dst, (S.get("conv") or {}).get("pct"), kf)   # 1.2.1: con el % de ffmpeg


def _draw_ask(S, st, d, start):                                       # 1.1.9
    ak = S.get("ask") or st.get("ask_last") or {}
    st["ask_last"] = ak
    left = max(0.0, float(ak.get("secs") or 0) - (time.time() - float(ak.get("t0") or time.time()))) if ak else 99.0
    return scene_wait_conv_cells(d.W, d.y0, d.a, d.b, d.ta - start, ak.get("src"), ak.get("dst"), left)


def _draw_replace(S, st, d, start):                                   # 1.4.2: la pregunta de sustituir un archivo
    ak = S.get("ask") or st.get("ask_last") or {}
    st["ask_last"] = ak
    left = max(0.0, float(ak.get("secs") or 0) - (time.time() - float(ak.get("t0") or time.time()))) if ak else 99.0
    return scene_wait_conv_cells(d.W, d.y0, d.a, d.b, d.ta - start, ak.get("src") or "VIEJO", ak.get("dst") or "NUEVO", left, swap=True)


def _draw_subst(S, st, d, start):                                      # 1.4.2: sustituyendo al guardar
    return scene_subst_cells(d.W, d.y0, d.a, d.b, d.ta - start)


def _draw_check(S, st, d, start):                                     # 1.2.5
    ck = S.get("check") or {}
    return scene_check_cells(d.W, d.y0, d.a, d.b, d.ta - start, ck.get("items"), ck.get("verdict"))


def _draw_merge(S, st, d, start):                                     # 1.1.3
    return scene_merge_cells(d.W, d.y0, d.a, d.b, scene_real_lt(S, st, "merge", d.ta - start))


def _draw_save(S, st, d, start):
    return scene_save_cells(d.W, d.y0, d.a, d.b, d.ta - start)


def _draw_clean(S, st, d, start):                                     # 1.1.5
    return scene_clean_cells(d.W, d.y0, d.a, d.b, d.ta - start, S.get("clean") or 0)


def _draw_empty(S, st, d, start):                                     # 1.1.7
    return scene_empty_cells(d.W, d.y0, d.a, d.b, d.ta - start, S.get("clean") or 0)


def _draw_send(S, st, d, start):
    return scene_send_cells(d.W, d.y0, d.a, d.b, d.ta - start, scene_chip_text(S.get("send_to") or SHORTCUT_NAME))     # 1.3.4: el chip es el destino real (atajo o VIEW)


def _draw_first(S, st, d, start):                                     # 1.2.9
    return scene_first_cells(d.W, d.y0, d.a, d.b, d.ta - start)


def _draw_updated(S, st, d, start):
    wl = S.get("welcome") or st.get("welcome_last") or {}
    st["welcome_last"] = wl
    return scene_updated_cells(d.W, d.y0, d.a, d.b, d.ta - start, wl.get("old"), wl.get("new"))


def _draw_download(S, st, d, start):                                   # 1.4.5
    return scene_down_cells(d.W, d.y0, d.a, d.b, d.ta - start, scene_down_rows(S))


def _draw_idle(S, st, d, start):                                       # 1.4.5
    return scene_idle_cells(d.W, d.y0, d.a, d.b, d.ta - start)


# ── Carril de tarjetas (1.4.6) ──
# Una sola escena de la apertura al cierre: los procesos del flujo (VIDEO, AUDIO, UNIÓN, GUARDADO) son tarjetas en un carril de hasta
# RAIL_MAX a la vez. Una tarjeta nueva entra por la derecha y empuja a las demás; si no cabe, la más antigua sale por la IZQUIERDA.
# Una tarjeta cuyo proceso terminó se queda un instante con su ✓ y sale también por la IZQUIERDA (1.5.5; antes salía por la derecha). Las tarjetas ya presentes en el primer cuadro
# del carril no se deslizan: el motor de morph las lleva desde el dibujo anterior (el marco del video y el ecualizador del sitio).
# DLPY_SCENE_RAIL=0 devuelve la Descarga / Unión / Guardado de la 1.4.5.
SCENE_RAIL = _flag_env("DLPY_SCENE_RAIL", True)
RAIL_MAX, RAIL_GAP = 3, 2                           # tarjetas a la vez y columnas entre ellas
RAIL_KINDS = ("download", "merge", "save")           # los dibujos de 1.4.5 que ahora viven dentro del carril
RAIL_MOVE = 14.0                                    # 1/s: suavizado de las tarjetas al entrar y al recolocarse (1.5.5: 7 → 14, el doble de rápido)
RAIL_EXIT_V0, RAIL_EXIT_ACC = 40.0, 140.0           # celdas/s al salir (arranca y acelera) (1.5.5: el doble)
RAIL_DONE_HOLD = 0.75                               # s que se ve el ✓ de una tarjeta antes de salir por la izquierda (modo «espera»; «ya» = 0; «segundos» = N)
RAIL_FADE_IN = 0.15                                 # s que tarda en aparecer una tarjeta que entra (1.5.5: 0.3 → 0.15)
RAIL_TITLE_T = 0.5                                  # 1.4.9: s que tarda el título de una tarjeta en deslizarse al de la pista siguiente
RAIL_EXIT_T = 0.4                                   # s que se calculan para que una tarjeta termine de salir (para el loop) (1.5.5: 0.8 → 0.4)
RAIL_SPIN = 14.0                                    # celdas/s del destello que recorre el marco del video
RAIL_LABELS = {"video": "VIDEO", "audio": "AUDIO", "merge": "UNIÓN", "save": "GUARDADO"}


def rail_hold(mode=None):
    """1.4.8: s que se queda el ✓ de una tarjeta antes de salir, según el modo de UX (espera · ya · segundos)."""
    mode = mode or SCENE_MODE
    return 0.0 if mode[0] == "real" else (min(10.0, mode[1]) if mode[0] == "secs" else RAIL_DONE_HOLD)


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
        left = not label.startswith("Descargando")                 # el flujo ya pasó a otra cosa: todas las pistas están hechas
        langs, groups = S.get("slang") or {}, {}
        for n in range(1, total + 1):
            k = kinds.get(n) or ("audio" if (mode == "audio" or (mode == "both" and n > 1)) else "video")
            pct = pcts.get(n)
            done = left or n < seen or (pct is not None and pct >= 100)
            groups.setdefault(k, []).append({"n": n, "pct": pct, "done": done, "lang": langs.get(n)})
        for k, tr in groups.items():                                # 1.4.9: el orden de aparición (la primera pista de cada tipo)
            alld = all(t["done"] for t in tr)
            pos = next((i for i, t in enumerate(tr) if not t["done"]), len(tr) - 1)
            cur = tr[pos]
            started = any(t["n"] <= seen for t in tr)
            out.append({"id": k, "kind": k, "pct": cur["pct"], "state": "hecho" if alld else ("activa" if started else "espera"),
                        "lang": cur["lang"], "idx": pos + 1, "of": len(tr)})
    if label.startswith(("Uniendo", "Ajustando")):
        out.append({"id": "merge", "kind": "merge", "pct": S.get("pp_pct"), "state": "activa"})
    if label.startswith("Guardando"):
        out.append({"id": "save", "kind": "save", "pct": None, "state": "activa"})
    return out


def rail_title(c, cw):
    """1.4.9: el título de una tarjeta (la fila justo sobre el dibujo): «VIDEO», «AUDIO ES-US» (si no cabe, solo «ES-US»), sin idioma y con
    varias pistas «AUDIO 2». Cambia de pista en pista; el cambio se desliza (rail_title_draw)."""
    text = RAIL_LABELS.get(c.get("kind"), "PISTA")
    if c.get("kind") != "audio":
        return text
    lang = str(c.get("lang") or "").upper()
    if lang:
        return (text + " " + lang) if len(text) + 1 + len(lang) <= cw else lang
    tag = str(int(c.get("idx") or 1))
    return (text + " " + tag) if int(c.get("of") or 1) > 1 and len(text) + 1 + len(tag) <= cw else text


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
    for c in cards:                                              # 1) lo que pide el estado, sobre las tarjetas que ya hay
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
            c["pct"], c["state"] = w["pct"], w["state"]
            _rail_title_sync(c, w, cw, ta)
    for c in cards:                                              # 2) el ✓ se ve un instante y la tarjeta sale por la derecha
        if not c["exit"] and c["state"] == "hecho" and ta - c["done_t"] >= rail_hold():
            _rail_exit(c, ta, "left")                            # 1.5.5: lo terminado sale por la izquierda (antes por la derecha)
    live = [c for c in cards if not c["exit"]]
    known = {c["id"] for c in cards} | R["gone"]
    for w in want:                                               # 3) tarjetas nuevas: entran por la derecha; si no caben, la más antigua sale por la izquierda
        if w["id"] in known or w["state"] == "hecho":
            continue
        if len(live) >= RAIL_MAX:
            if w["state"] != "activa":
                continue                                         # una que aún espera no desplaza a nadie
            victim = next((c for c in live if c["state"] != "activa"), live[0])
            _rail_exit(victim, ta, "left")
            live.remove(victim)
        c = {"id": w["id"], "kind": w["kind"], "pct": w["pct"], "state": w["state"], "lang": w.get("lang"), "idx": w.get("idx", 1), "of": w.get("of", 1), "title": None, "x": None, "tx": 0.0, "fade": 1.0 if R["first"] else 0.0,
             "exit": None, "exit_t": None, "done_t": None, "born": ta}
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
    """1.4.6: s que le faltan al carril para quedar quieto (✓ de la tarjeta que acaba + su salida); el carril no se deshace antes (regla del loop)."""
    R = st.get("rail")
    if not R:
        return 0.0
    now, rem = R["t"] or 0.0, 0.0
    for c in R["cards"]:
        if c["exit"]:
            dist = (W - c["x"]) if c["exit"] == "right" else (c["x"] + rail_width(W))
            rem = max(rem, max(0.0, dist) / (RAIL_EXIT_V0 + RAIL_EXIT_ACC * 0.4))
        elif c["state"] == "hecho":
            rem = max(rem, max(0.0, c["done_t"] + rail_hold() - now) + RAIL_EXIT_T)
        else:
            rem = max(rem, rail_hold() + RAIL_EXIT_T)
        if c.get("title_t") is not None:                         # 1.4.9: el título a medio deslizar termina antes de deshacer el carril
            rem = max(rem, c["title_t"] + RAIL_TITLE_T - now)
    return rem


# ── Estilo visual de la escena (1.4.8) ──
# Toda escena (tarjeta del carril o dibujo a todo el ancho) se lee igual, de arriba abajo, en las mismas filas del centro (y0+4 … y0+9):
#   · fila 0 — ETIQUETA: el nombre del proceso en mayúsculas (VIDEO, CONVERSIÓN, ENVÍO…), centrada.
#   · filas 1-3 — el DIBUJO del proceso (3 filas): su propio dibujo, pero siempre con los mismos tonos.
#   · fila 4 — (1.5.6) vacía: las escenas ya no llevan barra de progreso; el avance lo lleva la regla de arriba.
#   · fila 5 — ESTADO: «espera» o ✓ (1.5.6: nunca un % ni puntos de avance), o el dato del archivo que se pida.
# Tres estados, tres tonos: «espera» = gris apagado · «activa» = los colores del sitio (degradado) con blanco · «hecho» = verde con ✓.
# Etiqueta y estado salen de style_label · style_status (las usan las tarjetas del carril y scene_chrome, que los pone a las
# escenas de ancho completo), así que un cambio de estilo se hace en un solo sitio. D L P Y (la ventana a-Shell) y el Pulso (reposo) quedan como están.
def style_label(put, x0, w, y, text, state, dx=0, fade=1.0):
    """1.4.8: la etiqueta de un proceso, centrada en las `w` columnas desde x0. 1.4.9: `dx` la corre y `fade` (0 a 1) la apaga; lo que queda
    fuera de las `w` columnas no se pinta (así el título se desliza dentro de su tarjeta)."""
    col = SCENE_WHITE if state == "activa" else mix(BLACK, OLD_TONE, 0.8 if state == "hecho" else 0.6)
    if fade < 0.999:
        col = mix(BLACK, col, max(0.0, fade))
    text = str(text)[:w]
    for i, ch in enumerate(text):
        x = x0 + (w - len(text)) // 2 + i + dx
        if ch != " " and x0 <= x < x0 + w:
            put(x, y, ch, col)


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
        line, col = text or "espera", mix(BLACK, OLD_TONE, 0.35)
    else:
        line, col = text or "", SCENE_GRAY                          # 1.5.6: nunca un % (ni puntos de avance): solo el dato que se pida
    line = line[:w]
    for i, ch in enumerate(line):
        if ch != " ":
            put(x0 + (w - len(line)) // 2 + i, y, ch, col)


def rail_card_cells(c, y0, a, b, ta, cw, badge=None):
    """1.4.6: una tarjeta del carril en sus 6 filas (y0+4 … y0+9): etiqueta, dibujo de 3 filas, barra con el avance real y texto de estado."""
    cells = {}
    g = lambda k: mix6(a, b, k)
    state, kind, pct = c["state"], c["kind"], c["pct"]
    fd = max(0.0, min(1.0, c["fade"]))
    if c["exit"] and state == "hecho":
        fd *= 1.0 - 0.5 * min(1.0, (ta - c["exit_t"]) / 0.6)           # lo terminado se apaga al irse (1.5.5: ahora por la izquierda)
    lt, x0, ty = max(0.0, ta - c["born"]), int(round(c["x"])), y0 + 4
    dim = mix(BLACK, OLD_TONE, 0.35)
    ok = SAVED_TONE
    okd = mix(BLACK, SAVED_TONE, 0.8)

    def put(x, y, ch, col):
        cells[(x, y)] = (ch, col if fd >= 0.999 else mix(BLACK, col, fd), None)

    rail_title_draw(put, x0, cw, ty, c, state, ta)                # 1.4.9: «AUDIO ES-US» → «AUDIO EN-US» deslizándose, pista a pista
    iw = min(11, cw if cw % 2 else cw - 1)
    ix = x0 + (cw - iw) // 2
    pulse = 0.5 + 0.5 * math.sin(lt * 6.0)
    if kind == "video":                                          # marco con un destello que lo recorre y el ► en medio
        per = [(i, 0, "╭" if i == 0 else "╮" if i == iw - 1 else "─") for i in range(iw)] + [(iw - 1, 1, "│")] \
            + [(i, 2, "╰" if i == 0 else "╯" if i == iw - 1 else "─") for i in range(iw - 1, -1, -1)] + [(0, 1, "│")]
        head = (lt * RAIL_SPIN) % len(per)
        for idx, (dx, dy, gl) in enumerate(per):
            k = idx / float(len(per) - 1)
            if state == "activa":
                lit = max(0.0, 1.0 - ((head - idx) % len(per)) / 6.0)
                col = mix(mix(BLACK, g(k), 0.38), mix(g(k), WHITE, 0.55), lit)
            else:
                col = okd if state == "hecho" else dim
            put(ix + dx, ty + 1 + dy, gl, col)
        put(ix + iw // 2, ty + 2, "✓" if state == "hecho" else "►",
            ok if state == "hecho" else (mix(g(0.5), WHITE, 0.4 + 0.4 * pulse) if state == "activa" else dim))
    elif kind == "audio":                                        # 1.4.9: un solo dibujo para todas las pistas de audio: el ecualizador
        base = okd if state == "hecho" else dim
        cnt = min(5, (iw + 1) // 2)
        bx = ix + (iw - (cnt * 2 - 1)) // 2
        tt = int(lt * MOTIF_FPS) / float(MOTIF_FPS) * 9.0
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
    elif kind == "merge":                                        # dos vías (video arriba, audio abajo) que se juntan en una
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
            put(ix + iw // 2, ty + 2, "✓", ok)
        elif state == "activa":
            for i, cx_ in enumerate(cols):
                r = int((((lt * 1.6) + i / float(len(cols))) % 1.0) * 3.0)
                col = g(0.2 + 0.7 * i / float(max(1, len(cols) - 1)))
                if r < 2:
                    put(cx_, ty + 1 + r, "▒" if r == 0 else "▓", col)
                else:
                    put(cx_, ty + 3, "━", mix(col, WHITE, 0.4))
    txt = None                                                    # 1.5.6: sin barra de progreso ni % en la tarjeta (los lleva la regla de arriba y el % del final)
    if state == "activa":
        bt = (badge or {}).get("v" if kind == "video" else "a" if kind == "audio" else "")
        bt = bt[0] if bt and bt[0] and bt[0] != "►" else ""
        txt = bt if (bt and len(bt) <= cw) else " "                 # 1.5.0: sin % (lo lleva la barra y el estado de la escena): solo el dato del archivo
    style_status(put, x0, cw, ty + 5, state, pct, lt, txt)
    return cells


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
        st["rail_fast"] = d.ta + 0.2                                  # mientras se deslizan, a tope de cuadros (scene_fps)
    return scene_rail_cells(d.W, d.y0, d.a, d.b, R["cards"], d.ta, d.bdg)


# Escenas a todo ancho con el estilo de la escena (1.4.8): qué partes lleva cada una (l = etiqueta · b = barra · s = estado). D L P Y y Pulso, ninguna.
CHROME_PARTS = {"conv": "ls", "subst": "ls", "check": "ls", "merge": "ls", "save": "ls", "clean": "ls", "empty": "ls", "send": "ls",
                "ask": "ls", "replace": "ls", "first": "l", "updated": "l"}


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
        style_label(put, cx - 10, 21, y0 + 4, MOTIF_NAMES.get(kind, kind).upper(), state)
    if "s" in parts:                                                # 1.5.6: ya no hay barra (parte «b»): el avance lo lleva la regla de arriba
        style_status(put, cx - 10, 21, y0 + 9, state, pct, lt, None)
    return out


def _cycle_left(per, lt):
    """1.4.1: s que faltan para que un dibujo de ciclo `per` vuelva a su inicio (0 si no tiene ciclo)."""
    return (-lt) % per if per else 0.0


def _loop_check(S, st, W, lt):
    ck = S.get("check") or {}
    if ck.get("verdict") is None:
        rows = [(scene_chip_text(t) or "?", bool(n)) for t, n in (ck.get("items") or [])][:3] or [("?", False)] * 3
        per = 2.0 * _check_fit(rows, W - 4)[1] / CHECK_SPEED
    else:
        per = 2.0 * math.pi / 6.0
    return _cycle_left(per, lt)


def _real_conv(S, st, lt):
    pct = (S.get("conv") or {}).get("pct")
    if pct is None:
        return lt
    src, dst, _t = st.get("cinfo") or (None, None, 0.0)
    return max(0.0, min(100.0, float(pct))) / 100.0 * _conv_geo(S["geo"][0], src, dst)[4] / CONV_FLOW


def _real_merge(S, st, lt):
    pct = S.get("pp_pct")
    return lt if pct is None else max(0.0, min(100.0, float(pct))) / 100.0 * REAL_MERGE_CYCLES * 4.0 / MERGE_SPEED


MOTIFS = {
    "dlpy": _Motif(_draw_dlpy),
    "conv": _Motif(_draw_conv, loop=lambda S, st, W, lt: conv_loop_left(W, *(st.get("cinfo") or (None, None, 0.0))[:2], lt) + CONV_END_HOLD,
                   real=_real_conv),
    "ask": _Motif(_draw_ask),
    "replace": _Motif(_draw_replace),
    "subst": _Motif(_draw_subst, loop=lambda S, st, W, lt: max(0.0, SWAP_STREAM_SECS + 0.35 - lt), light=True),
    "check": _Motif(_draw_check, loop=_loop_check, light=True),
    "merge": _Motif(_draw_merge, loop=lambda S, st, W, lt: _cycle_left(4.0 / MERGE_SPEED, lt), real=_real_merge, light=True),
    "save": _Motif(_draw_save, loop=lambda S, st, W, lt: max(0.0, SAVE_STREAM_SECS + 0.35 - lt), light=True),
    "clean": _Motif(_draw_clean, loop=lambda S, st, W, lt: _cycle_left(1.0 / CLEAN_SPEED, lt), light=True),
    "empty": _Motif(_draw_empty, loop=lambda S, st, W, lt: _cycle_left(1.0 / CLEAN_SPEED, lt), light=True),
    "send": _Motif(_draw_send, loop=lambda S, st, W, lt: _cycle_left(SEND_CYCLE, lt)),
    "first": _Motif(_draw_first, loop=lambda S, st, W, lt: _cycle_left(WELCOME_CYCLE, lt), light=True),
    "updated": _Motif(_draw_updated, loop=lambda S, st, W, lt: _cycle_left(WELCOME_CYCLE, lt), light=True),
    "download": _Motif(_draw_download, loop=lambda S, st, W, lt: _cycle_left(DOWN_CYCLE, lt), light=True),
    "idle": _Motif(_draw_idle, loop=lambda S, st, W, lt: _cycle_left(PULSE_CYCLE, lt), light=True),
    "rail": _Motif(_draw_rail, loop=rail_loop, light=True),                                  # 1.4.6
}

# 1.4.5: el nombre de cada motivo (lo que entra al centro de la escena). «site» no está en MOTIFS: es el dibujo con que arranca (kind None).
MOTIF_NAMES = {"site": "Sitio", "dlpy": "DLPY", "first": "Estreno", "updated": "Novedad", "check": "Revisión", "ask": "Espera",
               "replace": "Relevo", "conv": "Conversión", "subst": "Sustitución", "merge": "Unión", "save": "Guardado",
               "clean": "Limpieza", "empty": "Papelera", "send": "Envío", "download": "Descarga", "idle": "Pulso", "rail": "Carril"}


def motif_name(kind):
    """1.4.5: nombre del motivo `kind` (None = el del sitio)."""
    return MOTIF_NAMES.get(kind or "site", str(kind))


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
    """1.2.8: s que le faltan al dibujo `kind` para cerrar su loop en curso (0 si no tiene loop). Lee MOTIFS (1.4.1)."""
    m = MOTIFS.get(kind)
    if m is None or m.loop is None:
        return 0.0
    t0 = st["mt"] if st.get("mt") is not None else st["ms"]          # desde que se ve el dibujo
    return m.loop(S, st, S["geo"][0], ta - t0)


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
    if "mcur" in st and kind != st["mcur"] and not S.get("last_error"):       # 1.2.8: el dibujo no se deshace hasta terminar su loop
        if st.get("hold_to") is None:
            st["hold_to"] = ta + motif_hold_secs(S, st, st["mcur"], ta)     # 1.3.2: según DLPY_SCENE_MODE (loop · real · segundos)
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
        st["site_flow"] = None                                                   # 1.4.2: otra transición del sitio: el plan se vuelve a medir
        st["site_trans_t"] = ta
        st["site_done"] = set(cur_done)
        st["site_done_at"] = dict(S.get("done_at") or {})

    if "mcur" not in st:
        st["mcur"] = st["mprev"] = kind if S.get("resume") else None
        st["mt"], st["ms"], st["msp"] = None, ta, ta

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
            st["mprev"], st["msp"] = kind, ta                                     # 1.2.1: de la pregunta a la conversión no hay ruido:
            st["mcur"], st["ms"], st["mt"] = kind, ta, None                       # los chips son los mismos y solo se apaga la tecla Enter
            st["key_fade_t"] = ta
        else:
            st["mprev"], st["msp"] = st["mcur"], st["ms"]
            st["mcur"], st["ms"], st["mt"] = kind, ta, ta + SCENE_LAG_MOTIF       # 1.0.6: el título va primero, el centro lo sigue
            st["flow"] = None                                                     # 1.4.2: transición nueva: el plan del morph se mide en su primer cuadro
        p = prog()
    S["motivo"] = motif_name(st["mcur"])                                   # 1.4.5: el nombre del motivo que ocupa el centro
    S["mvis"] = (st["mcur"], p >= 1.0, motif_loop_left(S, st, st["mcur"], ta) if p >= 1.0 else None, time.time())      # 1.5.5: qué dibujo hay, si ya entró, cuánto le falta a su loop y cuándo se midió
    if st["mcur"] is None and p >= 1.0:
        base = {k: v for k, v in cells.items() if y0 + 4 <= k[1] <= y0 + 4 + BADGE_ROW}
        if st["site_trans_t"] is not None:
            tp = max(0.0, min(1.0, (ta - st["site_trans_t"]) / SCENE_SWAP))
            if tp < 1.0:
                new_site = _site_center(S, W, y0, ta, f, bdg, cur_done, S.get("done_at") or {})
                merged = scene_flow_step(st, "site_flow", st["site_prev_cells"], new_site, tp, f, a, b)      # 1.4.2: morph, un plan por transición
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
        return scene_chrome(k, (MOTIFS[k].draw if k in MOTIFS else _draw_site)(S, st, d, start), S, st, d, start)      # 1.4.1: el registro (MOTIFS) decide cómo se pinta cada uno (1.4.8: y scene_chrome le pone el estilo común)

    new = layer(st["mcur"], st["ms"])
    if p < 1.0:
        new = scene_flow_step(st, "flow", layer(st["mprev"], st["msp"]), new, p, f, a, b)             # 1.4.2: las celdas del dibujo viejo viajan al nuevo
    for key in base:
        del cells[key]
    cells.update(new)
    return cells


def scene_fps(S, st, ta, hold):
    """Cuadros por segundo: a tope en intro/cierre/transformaciones; si no, CONV_FPS o DLPY_FPS. 1.0.3: también a tope durante salida de tipo."""
    if ta < hold or S.get("t_out") is not None or S.get("k_out") is not None or S.get("t_in") is not None or S.get("ask"):
        return SITE_FPS                                              # 1.1.1: también mientras espera el Enter (texto animado)
    if st.get("key_fade_t") is not None and 0 <= ta - st["key_fade_t"] < CONV_KEY_FADE + 0.1:
        return SITE_FPS                                              # 1.2.1: la tecla Enter apagándose, a tope de cuadros
    for m in (st.get("bdg") or {}).values():                         # 1.0.7: la etiqueta cambiando va a tope de cuadros
        if m[1] is not None and 0 <= ta - m[1] < SCENE_BADGE_SECS + 0.1:
            return SITE_FPS
    for key, dur in (("mt", SCENE_SWAP), ("t", SCENE_MORPH), ("tt", SCENE_TITLE_MORPH), ("site_trans_t", SCENE_SWAP)):
        t0 = st.get(key)
        if t0 is not None and -SCENE_LAG_LABEL <= ta - t0 < dur + 0.1 + SCENE_LAG_LABEL:     # 1.0.6: incluye la espera de la cascada
            return SITE_FPS
    if ta < st.get("rail_fast", 0.0):                                # 1.4.6: tarjetas del carril deslizándose
        return SITE_FPS
    if getattr(MOTIFS.get(scene_motif_kind(S)), "light", False):   # 1.1.3: unión y guardado (1.1.5: y limpieza; 1.2.5: y revisión; 1.2.9: y arranque), como la conversión (1.4.1: la marca light de MOTIFS)
        return CONV_FPS
    if S.get("brand"):
        return DLPY_FPS
    cv = S.get("conv")
    return CONV_RUN_FPS if (cv and cv.get("end") is None) else SITE_FPS      # 1.2.1: la conversión, más ligera que el resto


def scene_cells(S, st, tl, ta, f):
    """Un cuadro de la escena:"""
    W, Hh, y0, ymax = S["geo"]
    a, b, name, mode = S["a"], S["b"], S["name"], S["mode"]
    cells, _k = site_scene(tl, W, y0, a, b, name, mode, f, ta, (S.get("asp_shown") or S.get("aspect"), S.get("res")),
                           {k: (t_, 1.0) for k, t_ in scene_badge_texts(S).items()})
    hold = SITE_HOLD_AT * SITE_SECS
    if ta < hold:
        return cells
    cells = scene_motif(S, st, cells, ta, hold, f)                   # 1.0.3: sitio (con salida), conversión o DLPY boot
    cx = W // 2 + 1
    g = lambda k: mix6(a, b, k)

    for key in [k for k in cells if k[1] == y0 + 2]:                 # el nombre del sitio lo repinta la transición
        del cells[key]
    w = smooth((ta - hold) / 0.3)                                    # de la regla de la intro a la barra, sin saltos
    pos = ((ta * 0.8) % 1.0) * 1.5 - 0.25                            # el brillo del barrido (de -0.25 a 1.25 de la regla)
    want_b = 1.0 if S.get("busy") else 0.0                           # 1.0.6: barrido ↔ barra con fundido, sin corte de color
    bw = scene_ease(st.get("bw", want_b), want_b, SCENE_BUSY_RATE, ta - st.get("bta", ta))
    st["bw"], st["bta"] = (want_b if abs(bw - want_b) < 0.01 else bw), ta
    bw = st["bw"]
    for d in range(-14, 15):                                         # la regla es la barra de progreso
        k = (d + 14) / 28.0
        lit = g(k)
        tone = lit if k <= S["shown"] else mix(lit, BLACK, 0.62)     # barra de progreso
        if bw > 0:                                                   # espera sin porcentaje: un brillo recorre la regla
            sweep = mix(mix(lit, BLACK, 0.55), lit, max(0.0, 1.0 - abs(k - pos) / 0.22))
            tone = sweep if bw >= 1.0 else mix(tone, sweep, bw)
        cells[(cx + d, y0)] = ("─", mix(lit, tone, w), None)
    site = ("grad", " ".join(name.upper()))
    if st.get("tcur") is None:                                       # al principio en pantalla está el nombre del sitio
        st["tprev"] = st["tcur"] = scene_title_spec(S) if S.get("resume") else site     # (al volver de la lista, ya el del video)
        st["tt"] = None
    want = scene_title_spec(S)
    if want != st["tcur"]:                                           # cambió el título: el viejo se deshace en el nuevo
        mid = st["tt"] is not None and (ta - st["tt"]) / SCENE_TITLE_MORPH < 1.0 and bool(st.get("tshown"))
        st["tpcols"] = dict(st["tshown"]) if mid else None           # 1.0.6: a mitad de otra transformación, parte de lo que ya se ve
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
    lab = S["label"]
    if dwidth(lab) > room and lab.startswith("Descargando "):         # terminal angosto: sin el verbo, para no perder el «2/3»
        lab = lab[12:13].upper() + lab[13:]
    lab = fit_text(lab, room)
    err_col = (255, 96, 96) if (S.get("last_error") and lab.startswith("Error")) else SCENE_GRAY   # 1.0.8: el error en rojo suave
    full = lab + ("" if pct is None else " · %3d%%" % int(max(0, min(100, pct))))
    if lab != st["lab"]:                                             # cambió el proceso: el texto viejo se deshace en el nuevo
        mid = st["lab"] is not None and (ta - st["t"]) / SCENE_MORPH < 1.0 and bool(st.get("lshown"))
        st["lpcols"] = dict(st["lshown"]) if mid else None           # 1.0.6: a mitad de otra transformación, parte de lo que ya se ve
        lead = any(st.get(k_) is not None and 0 <= ta - st[k_] < 0.25 for k_ in ("tt", "mt"))   # cascada: título → centro → texto
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
    if S.get("ask"):                                                 # 1.1.1: pidiendo Enter para convertir
        cells = scene_ask_cells(cells, S["ask"], ta, y0, cx, W, g)
    if S.get("k_out") is not None:                                   # la salida: la escena se cierra hacia el centro
        cells = scene_dissolve(cells, S["k_out"], cx, W, a, b)
    return cells


def scene_paint(out, cells, st, W, ymax):
    """Repinta solo las filas que cambiaron (los terminales de iOS no aguantan cuadros completos a 24 fps)."""
    seq = [WRAP_OFF]
    for y in range(1, ymax + 1):
        parts, cur = [], None
        for x in range(1, W):
            c = cells.get((x, y))
            key, ch = (c[1:], c[0]) if c else (None, " ")
            if key != cur:
                parts.append(RESET + _fg(key[0]) + (_bg(key[1]) if key[1] else "") if key else RESET)
                cur = key
            parts.append(ch)
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
    """Hilo de la escena: 24 cuadros por segundo hasta que SCENE["stop"]."""
    S = SCENE
    out, (W, _h, _y0, ymax) = S["out"], S["geo"]
    st = scene_state()
    hold = SITE_HOLD_AT * SITE_SECS
    t0 = full_t = time.monotonic() - (hold + 0.4 if S.get("resume") else 0.0)    # al volver de la lista no se repite la intro
    rows_seen, last, fps = S["rows"], -1, SITE_FPS
    ft = time.monotonic()                                                # 1.0.6: instante del cuadro anterior (suavizado por tiempo)
    try:
        while not S["stop"]:
            now = time.monotonic()
            ta = now - t0
            S["ta"] = ta
            fps = scene_fps(S, st, ta, hold)                               # 1.0.2: convirtiendo o DLPY: menos cuadros, menos CPU
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
                    out.write(HOME_CLEAR + PURGE_SEQ)       # 1.2.3: también el historial (lo que el cambio de alto metió arriba)
                elif now - full_t >= 0.35:                           # refresco completo periódico (por si el terminal borró algo)
                    full_t = now
                    st["rows"].clear()
                fdt, ft = now - ft, now
                tgt = S.get("aspect") or 16 / 9.0                    # el marco de video cambia de proporción sin saltos
                S["asp_shown"] = tgt if not S.get("asp_shown") else scene_ease(S["asp_shown"], tgt, SCENE_ASP_RATE, fdt)
                if abs(tgt - S["asp_shown"]) < 0.005:
                    S["asp_shown"] = tgt
                S["shown"] = scene_ease(S["shown"], S["frac"], SCENE_BAR_RATE, fdt)   # la barra alcanza al avance sin saltos
                if abs(S["frac"] - S["shown"]) < 0.002:
                    S["shown"] = S["frac"]
                if S["t_out"] is not None:                           # se cierra hacia el centro
                    S["k_out"] = (now - S["t_out"]) / SCENE_OUTRO_SECS
                elif S.get("t_in") is not None:                      # vuelve a abrirse desde el centro (lo mismo, al revés)
                    k_in = 1.0 - (now - S["t_in"]) / SCENE_OUTRO_SECS
                    S["k_out"] = k_in if k_in > 0 else None
                    if k_in <= 0:
                        S["t_in"] = None
                else:
                    S["k_out"] = None
                scene_paint(out, scene_cells(S, st, min(ta, hold), ta, f), st, W, ymax)
            time.sleep(SITE_IDLE if fps >= SITE_FPS else 0.5 / fps)
    except Exception as _ign:
        S["err"] = f"{type(_ign).__name__}: {_ign}"      # 1.0.1: --scb lo anota en state/scb_debug.json
        ignore("scene_loop", _ign)


def scene_start(run, resume=False):
    """Arranca la escena (la intro del sitio y lo que sigue)."""
    S = SCENE
    if S["on"] or not (SCENE_ON and SITE_ANIM):
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
    if sw < 30 or Hh < 16:
        return False
    name, sig, a, b = site_theme_apply(run) or site_theme(_host(run.link), "")
    mode = site_mode(run)
    fg = (0, 0, 0) if (0.3 * a[0] + 0.59 * a[1] + 0.11 * a[2]) > 150 else (255, 255, 255)
    SESSION["tag"] = (" " + sig + " " + SITE_ICON[mode] + " ", a, fg)     # si la escena cede, el banner conserva la etiqueta
    y0 = max(2, (Hh - SCENE_ROWS) // 2)
    if not native_clear(HOME_CLEAR) and _scm_run():      # 1.0.1: --scb no usa el borrado nativo: lo hace aquí, ya seguro de que pinta
        sys.stdout.write(RESET + HOME_CLEAR + PURGE_SEQ)
        sys.stdout.flush()
    keep = {k: S[k] for k in ("title_raw", "label", "pct", "frac", "shown", "lo", "hi", "brand", "busy", "aspect", "res", "alabel", "vinfo", "ainfo", "count")} if resume else {}
    mute = _SceneMute(sys.stdout._inner if isinstance(sys.stdout, _SceneMute) else sys.stdout)   # sin envolturas anidadas
    S.update(scene_defaults(), on=True, mute=mute, out=mute._inner, geo=(W, Hh, y0, min(Hh, y0 + SCENE_STATUS_ROW + 1)), a=a, b=b, name=name,
             mode=mode, mode_orig=mode, label="Preparando", rows=rows, label_wall=time.time())     # 1.3.2: «Preparando» también cuenta sus N s (1.4.1: lo demás, de scene_defaults)
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
    emute = _SceneErrMute(sys.stderr._inner if isinstance(sys.stderr, _SceneErrMute) else sys.stderr)   # 1.0.8: stderr al log
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
    if SCENE.get("last_error"):                         # 1.0.8: si el flujo siguió, el error era recuperable: la escena vuelve a lo suyo
        SCENE["last_error"] = None
        if SCENE.get("err_brand"):
            SCENE["brand"], SCENE["err_brand"] = False, False
    new = str(text)
    if new != SCENE.get("label"):
        w, old = SCENE.get("label_wall"), str(SCENE.get("label") or "")
        if SCENE.get("brand") and w:                              # 1.3.3: el comando anterior termina de mostrarse (tecleado y ejecutado) en la escena
            scene_wait_step(old)
        rest = scene_min_wait()                                   # 1.3.2: DLPY_SCENE_MODE=<segundos>: el texto anterior se lee N s como mínimo
        if rest > 0:
            time.sleep(rest)
        SCENE["label_wall"] = time.time()
        SCENE["dl_done"] = None                                   # 1.3.3: el texto nuevo aún no se ha mostrado
    SCENE["label"], SCENE["pct"] = new, pct
    if frac is not None:
        SCENE["frac"] = max(SCENE["frac"], min(1.0, float(frac)))


def scene_title(title):
    """El título del video: el nombre del sitio se transforma en él."""
    if SCENE["on"]:
        SCENE["title_raw"] = " ".join(str(title or "").split())


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
    except Exception:
        pass


def scene_stream(kind, n, total, lang=None):
    """Empieza un stream: 1.0.5 fix - sale de escena cuando ya no queda más de ESE tipo, no del global."""
    if not SCENE["on"]:
        return
    total = max(1, total or 1)
    n = min(max(1, n), total)
    SCENE["lo"], SCENE["hi"] = 0.08 + 0.72 * (n - 1) / total, 0.08 + 0.72 * n / total
    SCENE["stream_total"] = total
    SCENE["stream_seen"] = n
    try:
        k = str(kind or "").lower()
        started = _scene_bag("started")
        started[k] = started.get(k, 0) + 1
        _scene_bag("skind")[n] = k                                  # 1.4.5: qué es y cuánto lleva cada pista (la fila de «Descarga»)
        _scene_bag("spct")[n] = 0
        if lang:
            _scene_bag("slang")[n] = lang                           # 1.4.7: el idioma de cada pista (la tarjeta de audio lo muestra)
        SCENE["past_dl"] = True                                     # 1.4.5: desde aquí el sitio ya no vuelve (entre motivos queda el Pulso)

        # si había un tipo terminado pendiente y ahora empieza otro distinto, ese tipo ya no volverá: marcarlo como terminado
        last = SCENE.get("last_finished")
        if last and last != k:
            _scene_mark_done(last)
            SCENE["last_finished"] = None

        _scene_bag("type_totals")[k] = total                       # para debug
    except Exception:
        pass
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
            _scene_mark_done(k)                                     # …salvo si era el último stream global: done de inmediato
            SCENE["last_finished"] = None
    except Exception:
        pass


def scene_outro():
    """1.4.1: la escena se cierra hacia el centro y se espera a que el hilo pinte el cierre (con DLPY_OUTRO=0 no hace nada). True si cerró.
    Antes lo repetían scene_error_end, scene_end y scene_list_enter."""
    if not OUTRO:
        return False
    SCENE["t_out"] = time.monotonic()
    time.sleep(SCENE_OUTRO_SECS + 0.12)
    return True


def scene_brand(on=True):
    """El título pasa a «D L P Y» (actualizaciones y envío); con on=False vuelve al del video."""
    if SCENE["on"]:
        SCENE["brand"] = bool(on)
        SCENE["err_brand"] = False


def scene_busy(on=True):
    """La regla deja de marcar un avance y barre de lado a lado (una espera sin porcentaje)."""
    if SCENE["on"]:
        SCENE["busy"] = bool(on)


def scene_note(text, hold=0.0):
    """Estado de la fase de actualizaciones:"""
    if not SCENE["on"]:
        return False
    scene_brand()
    scene_busy()
    scene_status(text)
    if hold:
        time.sleep(scene_dwell(hold))
    return True


def scene_hold(secs):
    """1.1.3: deja ver la escena `secs` segundos (guardado, envío). No espera si no hay escena o si hubo un error. True si esperó."""
    if not SCENE["on"] or SCENE.get("last_error"):
        return False
    time.sleep(max(0.0, float(scene_dwell(secs))))
    return True


def welcome_kind(stored, version):
    """1.2.9: qué escena de arranque toca: «first» (no hay versión guardada), «updated» (la guardada es otra) o None (misma versión)."""
    if not stored:
        return "first"
    return None if stored == version else "updated"


def code_change(stored_hash, cur_hash):
    """1.3.2:"""
    if not cur_hash:
        return None
    if not stored_hash:
        return "first"
    return None if stored_hash == cur_hash else "edited"


def scene_welcome(kind, old=None, new=None, down=False, edited=False):
    """1.2.9:"""
    S = SCENE
    if kind not in ("first", "updated") or not S["on"] or S.get("last_error"):
        return False
    if kind == "first":
        text = f"Primera ejecución · DLpy {new or VERSION}"
    elif edited:                                                      # 1.3.2: misma versión, otro código (los chips llevan la versión; el hash va en el texto)
        text = "Cambió el hash · edición detectada"
    else:
        text = f"{'Versión anterior' if down else 'Actualizado'} · {old or '?'} → {new or VERSION}"
    prev = {k: S.get(k) for k in ("brand", "busy", "err_brand", "label", "pct")}      # 1.3.1: cómo estaba la escena antes
    S["welcome"] = {"kind": kind, "old": old, "new": new or VERSION}
    try:
        scene_brand()
        scene_busy()
        scene_status(text)
        return scene_hold(SCENE_WELCOME_SECS)
    finally:
        S["welcome"] = None
        if not S.get("last_error"):               # 1.3.1: se devuelve todo a como estaba (si no, D L P Y se quedaba para el resto del flujo)
            S["brand"], S["busy"], S["err_brand"] = bool(prev["brand"]), bool(prev["busy"]), bool(prev["err_brand"])
            S["label"], S["pct"] = prev["label"] or "", prev["pct"]


def scene_progress(pct):
    """Avance (0-100) del stream en curso; sin total conocido el % se oculta."""
    if not SCENE["on"] or not SCENE["label"].startswith("Descargando"):
        return
    n = int(SCENE.get("stream_seen") or 1)
    if pct is None:
        SCENE["pct"] = None
        _scene_bag("spct")[n] = None
        return
    SCENE["pct"] = pct
    _scene_bag("spct")[n] = pct                                     # 1.4.5
    SCENE["frac"] = max(SCENE["frac"], SCENE["lo"] + (SCENE["hi"] - SCENE["lo"]) * max(0.0, min(100.0, pct)) / 100.0)


def scene_shape(*srcs):
    """1.0.0: la proporción y la resolución del video (width/height de un formato o del análisis) para el marco de la escena."""
    if not SCENE["on"]:
        return
    asp, res = video_shape(*srcs)
    if asp:
        SCENE["aspect"], SCENE["res"] = asp, res
    al = audio_label(*srcs)
    if al:
        SCENE["alabel"] = al                           # 1.0.7: formato del audio para la etiqueta
    SCENE.setdefault("vinfo", {}).update(video_facts(*srcs))      # 1.1.0: códec / fps / bitrate para la etiqueta que fluye
    SCENE.setdefault("ainfo", {}).update(audio_facts(*srcs))      # 1.1.0: bitrate / muestreo del audio
    dicts = [d for d in srcs if isinstance(d, dict)]
    if any(d.get("is_live") for d in dicts) and (SCENE.get("mode_orig") or SCENE.get("mode")) != "live":
        SCENE["mode"] = SCENE["mode_orig"] = "live"    # 1.0.7: el análisis llegó después de abrir la escena: pasa al dibujo de directo
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


def scene_convert(codec, label="Convirtiendo", src=None, dst=None):
    """1.0.2:"""
    if not SCENE["on"]:
        return
    cv = SCENE.get("conv")
    if cv and cv.get("end") is None:                         # otro intento (otro encoder): el destino cambia, el origen es el mismo
        cv["codec"], cv["dst"], cv["pct"] = str(codec or ""), scene_chip_text(dst or codec), None
        if src:
            cv["src"] = scene_chip_text(src)
    else:
        SCENE["conv"] = {"codec": str(codec or ""), "t0": SCENE.get("ta", 0.0), "end": None, "pct": None,
                         "src": scene_chip_text(src), "dst": scene_chip_text(dst or codec)}
    scene_status(label)


CONV_END_HOLD = 0.2         # 1.2.8: s que se deja ver el paquete ya en el destino antes de pasar a la escena siguiente


def conv_loop_left(W, src, dst, lt):
    """1.2.8:"""
    gap = _conv_geo(W, src, dst)[4]
    h = lt * CONV_FLOW
    if h >= gap:
        h -= (int((h - gap) / CONV_PACK) + 1) * CONV_PACK
    return (gap - h) / CONV_FLOW


def scene_convert_end():
    """Termina la conversión: el avance pasa a 100 % y el dibujo queda hasta terminar su loop (motif_loop_left, en scene_motif)."""
    cv = SCENE.get("conv")
    if SCENE["on"] and cv and cv.get("end") is None:
        scene_conv_progress(100)
        cv["end"] = SCENE.get("ta", 0.0)


def scene_check(items=None, verdict=None, label=None):
    """1.2.5:"""
    if not SCENE["on"]:
        return
    SCENE["check"] = {"items": items, "verdict": verdict}
    scene_status(label or ("Revisando archivo" if verdict is None else
                           "Revisando · ya es compatible" if verdict == "ok" else "Revisando · hay que convertir"))


def scene_check_end():
    """Cierra la revisión: el dibujo se deshace en el del paso que sigue (convertir o guardar), que pone su propio texto."""
    if not SCENE["on"]:
        return
    SCENE["check"] = None
    if str(SCENE.get("label") or "").startswith("Revisando"):
        scene_status("Finalizando")


def scene_conv_progress(pct):
    """1.2.1:"""
    if not SCENE["on"]:
        return
    cv = SCENE.get("conv")
    if not cv or cv.get("end") is not None:
        return
    if pct is None:
        cv["pct"], SCENE["pct"] = None, None
        return
    try:
        p = max(0.0, min(100.0, float(pct)))
    except (TypeError, ValueError):
        return
    p = max(p, cv.get("pct") or 0.0)
    cv["pct"], SCENE["pct"] = p, p
    SCENE["frac"] = max(SCENE["frac"], min(0.94, 0.8 + 0.14 * p / 100.0))


SCENE_ASK_SECS = 20                                 # 1.1.1: s que espera el Enter de una conversión larga


def ask_est_text(est):
    """«~45 s», «~3 min» (la estimación de una conversión); '' si no se sabe."""
    try:
        e = float(est or 0)
    except (TypeError, ValueError):
        return ""
    if e <= 0:
        return ""
    return "~%d s" % round(e) if e < 90 else "~%d min" % round(e / 60.0)


def scene_ask_lines(room, est, left, kind=None):
    """(línea 1, línea 2)"""
    if kind == "replace":                                             # 1.4.2: sustituir un archivo: Enter sustituye, n conserva
        l1 = next((t for t in ("Toca la pantalla · Enter sustituir · n conservar", "Enter sustituir · n conservar", "Enter sustituir · n no",
                               "Enter sí · n no", "Enter · n") if len(t) <= room), "Enter")
        n = "%d s" % max(0, int(math.ceil(left)))
        l2 = next((t for t in ("sin respuesta se sustituye · " + n, n) if len(t) <= room), n)
        return l1, l2
    l1 = next((t for t in ("Toca la pantalla · Enter convertir · r remux · n original", "Enter convertir · r remux · n original",
                           "Enter convertir · r remux · n no", "Enter sí · r remux · n no", "Enter · r · n") if len(t) <= room), "Enter")
    et, n = ask_est_text(est), "%d s" % max(0, int(math.ceil(left)))
    l2 = next((t for t in ((et + " · " if et else "") + "sin respuesta se convierte · " + n, "sin respuesta se convierte · " + n,
                           (et + " · " if et else "") + n, n) if len(t) <= room), n)
    return l1, l2


def ask_key_mask(text):
    """1.1.4: índices de las teclas (Enter, r, n) en una línea de opciones separadas por « · »."""
    mask, i = set(), 0
    for seg in str(text).split(" · "):
        w = seg.split(" ")[0]
        if w in ("Enter", "r", "n"):
            mask.update(range(i, i + len(w)))
        i += len(seg) + 3
    return mask


ASK_HINT_CYCLE = 4.8                                 # 1.2.0: s que dura el ciclo «Toca la pantalla…» ⇄ «¿Convertir este video?» (1.2.1)


def ask_hint_texts(room, kind=None):
    """1.2.0:"""
    a = next((t for t in ("Toca la pantalla para abrir el teclado", "Toca para abrir el teclado", "Toca = teclado") if len(t) <= room), "")
    qs = ("¿Sustituir el archivo?", "¿Sustituir archivo?", "¿Sustituir?") if kind == "replace" else ("¿Convertir este video?", "¿Convertir ahora?", "¿Convertir?")
    b = next((t for t in qs if len(t) <= room), qs[-1])
    return a, b, 0


def scene_ask_cells(cells, ask, ta, y0, cx, W, g):
    """1.1.1:"""
    r0 = y0 + SCENE_STATUS_ROW - 1                                   # 1.4.2: sugerencia · opciones · cuenta: tres filas hacia abajo desde el aire bajo el dibujo
    for key in [k for k in cells if k[1] in (r0, r0 + 1, r0 + 2)]:
        del cells[key]
    left = max(0.0, ask["secs"] - (time.time() - ask["t0"]))
    l1, l2 = scene_ask_lines(max(8, W - 6), ask.get("est"), left, ask.get("kind"))
    fd = smooth((ta - ask["ta0"]) / 0.5)
    n = len(l1)
    pos = (ta * 16.0) % (n + 12) - 6                                 # el brillo recorre la línea
    pulse = 0.5 + 0.5 * math.sin(ta * 4.0)
    keys = ask_key_mask(l1)
    x0 = cx - n // 2
    for i, ch in enumerate(l1):
        if ch == " ":
            continue
        glow = max(0.0, 1.0 - abs(i - pos) / 4.0)
        if i in keys:
            col = mix(g(0.5), WHITE, 0.6 + 0.4 * pulse)
        else:
            col = mix(mix(BLACK, g(i / float(max(1, n))), 0.75), WHITE, 0.75 * glow)
        cells[(x0 + i, r0 + 1)] = (ch, mix(BLACK, col, fd), None)
    room = max(8, W - 6)
    if not l1.startswith("Toca la pantalla"):                         # 1.2.0: con el teclado bajado hay que tocar la pantalla
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
    x1 = cx - len(l2) // 2
    for i, ch in enumerate(l2):
        if ch != " ":
            col = mix((255, 176, 32), WHITE, 0.3 * pulse) if urgent and i >= len(l2) - len("%d s" % int(math.ceil(left))) \
                else SCENE_DIM if i < len(l2) - len("%d s" % int(math.ceil(left))) else SCENE_GRAY
            cells[(x1 + i, r0 + 2)] = (ch, mix(BLACK, col, fd), None)
    return cells


def scene_ask_enter(est=None, secs=None, src=None, dst=None, kind=None):
    """1.1.1:"""
    S = SCENE
    if not S["on"] or not countdown_supported():
        return None
    try:
        keys = _PosixKeys()
    except Exception as _ign:
        ignore("scene_ask_enter", _ign)
        return None
    secs = float(secs or SCENE_ASK_SECS)
    result, busy_prev = False, S.get("busy")
    try:
        input_unlock()
        drain_pending_input()
        note_prompt("Enter sustituir · n conservar (escena)" if kind == "replace" else "Enter convertir · r remux · n original (escena)")
        t_w, hold = time.time(), SITE_HOLD_AT * SITE_SECS
        while S["on"] and S.get("ta", 0.0) < hold and time.time() - t_w < 6.0:       # primero termina la intro
            time.sleep(0.05)
        if not S["on"]:
            return None
        t0 = time.time()
        S["busy"] = True                                              # la regla de arriba late mientras se espera
        S["ask"] = {"est": est, "secs": secs, "t0": t0, "ta0": S.get("ta", 0.0),
                    "src": scene_chip_text(src) if src else None, "dst": scene_chip_text(dst) if dst else None, "kind": kind}
        done = False
        while not done and S["on"] and time.time() - t0 < secs:
            for ch in keys.read(0.1):
                if ch in "\r\n":
                    if time.time() - t0 < PHANTOM_SECS or time.time() - START_T < PHANTOM_BOOT:
                        continue                                      # Enter fantasma
                    result, done = True, True
                    break
                if ch in "rR" and kind != "replace":                   # 1.1.4: solo remux (no aplica al sustituir)
                    result, done = "r", True
                    break
                if ch in "nN":
                    done = True
                    break
                if ch == "\x03":
                    raise KeyboardInterrupt
                if ch == "\x04":
                    raise EOFError
        if not done and S["on"]:
            result = True                                             # 1.2.0: sin respuesta (se acabó la cuenta) = la predeterminada: convertir (1.4.2: o sustituir)
        if not S["on"] and not result:
            return None
        return result
    finally:
        S["ask"] = None
        S["busy"] = busy_prev
        with quiet("scene_ask_enter close"):
            keys.close()


def scene_questions():
    """Antes:"""
    return False


def scene_stop(clear=False, cursor=True):
    """Para la escena y devuelve stdout. clear=True: borra y deja el banner (lo que sale después se ve como siempre)."""
    S = SCENE
    if not S["on"]:
        return False
    S["stop"] = True
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
    if SCENE.get("last_error"):                               # 1.0.8: hubo un error: se lee en D L P Y y la escena se cierra
        scene_error_end()
    else:
        scene_brand()
        scene_busy(False)
        SCENE["send_to"] = "view" if view else None            # 1.3.4: el chip y el texto dicen adónde va el archivo de verdad
        scene_status(send_label(view), frac=1.0)
        time.sleep(max(SCENE_TITLE_MORPH + 0.35, scene_dwell(SCENE_SEND_SECS)))   # 1.1.3: el título, el texto y el cometa del envío se leen (1.3.2: N s con un número)
        scene_outro()                                         # el hilo de la escena pinta el cierre
    scene_stop(cursor=False)
    if QUIET["on"]:
        quiet_set(False)
    with quiet("scene_end clear"):
        native_clear()
        sys.stdout.write(RESET + CURSOR_SHOW)
        sys.stdout.flush()
    return True


# ───────────────────── Lista «Ver todos» con el estilo de la escena (0.9.5) ─────────────────────
# La lista completa (o la corta, si el formato del atajo ya no existe) hay que verla y deslizarla, así que la escena no puede
# pintarla: cede. Pero cede con su propio lenguaje: el texto cambia a «Ver todos», la escena se cierra hacia el centro, la lista abre con
# la regla de degradado del sitio, el título del video en blanco que se transforma y el estado en gris; números, flechas y marcas
# toman el color del sitio. Al elegir, la escena vuelve a abrirse desde el centro y sigue la descarga.
SCENE_LIST_SECS = 0.45                              # s que tarda en entrar la cabecera de la lista


def scene_list_top_cells(S, W, title, status, p, f):
    """Cabecera de la lista en el estilo de la escena (p de 0 a 1):"""
    a, b, cx = S['a'], S['b'], W // 2 + 1
    cells = {}
    opened = smooth(p / 0.6)
    for d in range(-14, 15):
        if abs(d) / 14.0 <= opened:
            cells[(cx + d, 1)] = ("─", mix(a, b, round((d + 14) / 28.0 * 6) / 6.0), None)
    for y, text, tone, p0 in ((2, fit_text(title, max(8, W - 6)), SCENE_WHITE, 0.15),
                              (3, fit_text(status, max(8, W - 6)), SCENE_GRAY, 0.35)):
        for x, (ch, kind) in scene_morph({}, scene_cols(text, cx), max(0.0, min(1.0, (p - p0) / 0.65)), f).items():
            cells[(x, y)] = (ch, tone if kind == 2 else mix(mix(a, b, 0.5), BLACK, 0.45), None)
    return cells


def scene_list_top(title, status, animate=True):
    """Pinta la cabecera de la lista (3 filas) y deja el cursor en la fila 5, listo para imprimir el resto."""
    S = SCENE
    out, st = sys.stdout, {"rows": {}}
    W = safe_width() + 1
    with quiet("scene_list_top"):
        n = max(1, int(SCENE_LIST_SECS * SITE_FPS)) if (animate and ANIM and USE_COLOR and TRUECOLOR) else 0
        for i in range(n + 1):
            scene_paint(out, scene_list_top_cells(S, W, title, status, i / float(max(1, n)), i), st, W, 3)
            if i < n:
                time.sleep(1.0 / SITE_FPS)
        out.write(RESET + cur_to(5, 1))
        out.flush()


def scene_list_enter(status):
    """La escena cede su pantalla a la lista:"""
    S = SCENE
    if not (S["on"] and S.get("a")):
        return None
    back = {"label": S["label"], "pct": S["pct"], "quiet": QUIET["on"]}
    scene_busy(False)
    scene_status(status)
    time.sleep(SCENE_MORPH + 0.2)                         # el texto termina de transformarse y se lee
    scene_outro()                                         # el hilo de la escena pinta el cierre
    scene_stop()
    if back["quiet"]:
        quiet_set(False)                                  # la lista sí anima sus filas
    native_clear()
    return back


def scene_list_leave(run, back):
    """Tras elegir:"""
    if back is None:
        return False
    if back["quiet"]:
        quiet_set(True)
    SCENE.update(label=back["label"], pct=back["pct"])
    try:
        return scene_start(run, resume=True)
    except Exception as _ign:
        ignore("scene_list_leave", _ign)
        return False


def card_tab():
    """(texto pintado, columnas) de la pestaña del borde superior de la tarjeta: la del sitio (también los adultos); None si no hay."""
    tg = SESSION.get("tag")
    if tg and USE_COLOR and TRUECOLOR:
        return _bg(tg[1]) + _fg(tg[2]) + tg[0] + RESET, len(tg[0])
    return None


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
    with quiet("roast_link"):
        host = _host(link)                   # la etiqueta del sitio NO se borra aquí: puede venir de la intro temprana;
                                             # entre descargas la reinicia reset_site_state
        if is_adult(host):
            adult_alert()                    # 1.0.7: solo se anota (los chistes); la interfaz es la misma de todos
            if ROAST:
                txt, t = _clock()
                pool = ADULT_JOKES + (ADULT_LATE * 2 if t.tm_hour < 6 else [])
                roast_say(random.choice(pool).format(h=txt))
            return
        if not ROAST:
            return
        roast_say(hour_joke())
        for doms, pool in SITE_JOKES:
            if _host_is(host, doms):
                roast_say(random.choice(pool))
                break


def roast_info(info, link, old_file):
    """Tras analizar el video: contenido +18, duración, repetido."""
    with quiet("roast_info"):
        host = _host(link)
        ext = info.get("extractor_key") or info.get("extractor") or ""
        if not SESSION["adult"] and is_adult(host, ext):
            adult_alert()                    # el enlace no lo delató, el extractor sí
            if ROAST:
                roast_say(random.choice(ADULT_JOKES).format(h=_clock()[0]))
        if not ROAST:
            return
        picks = []
        if not SESSION["adult"] and (info.get("age_limit") or 0) >= 18:
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


def roast_choice(kind, fmt):
    """Tras elegir formato: tamaño, resolución, solo audio."""
    if not ROAST:
        return
    with quiet("roast_choice"):
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


def roast_done(others, reused=False):
    """Al terminar (o al entregar uno ya descargado)."""
    if not ROAST:
        return
    with quiet("roast_done"):
        if reused:
            pool = list(REUSE_JOKES)
        elif SESSION["adult"]:
            pool = list(ADULT_DONE)
        else:
            pool = [p for p in DONE_JOKES if "{n}" not in p or others >= 2]
            pool += GENERIC_JOKES
        print()
        roast_say(random.choice(pool).format(n=max(0, others)), pin=False)


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


def smooth(x):
    """Entrada y salida suaves (0→1)."""
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def disk_fraction():
    """Fracción usada del almacenamiento del equipo (0–1)"""
    for path in ("/", FILES_DIR, HOME, os.getcwd()):
        try:
            u = shutil.disk_usage(path)
            if u.total > 0:
                return max(0.0, min(1.0, u.used / u.total))
        except (OSError, ValueError, NameError):
            continue
    return None


SCALE_WARN, SCALE_CRIT_PHONE, SCALE_CRIT_MINE = 0.80, 0.92, 1.0     # umbrales de las escalas de la barra
SCALE_COLOR = {"ok": "gray", "warn": "amber", "crit": "red"}
BANNER = {"h": 3}                                                  # líneas que ocupa el encabezado (para repartir la pantalla)


def scale_state(frac, kind):
    """«ok» / «warn» / «crit» de una escala de la barra. kind: «phone» (equipo) o «mine» (DLpy)."""
    if frac is None:
        return "ok"
    crit = SCALE_CRIT_PHONE if kind == "phone" else SCALE_CRIT_MINE
    return "crit" if frac >= crit else ("warn" if frac >= SCALE_WARN else "ok")


def storage_bar(n, phone, mine):
    """Dos escalas en una línea:"""
    o, m, trk, gray = (PALETTE[k][0] for k in ("orange", "magenta", "track", "gray"))
    sp, sm = scale_state(phone, "phone"), scale_state(mine, "mine")
    if not TRUECOLOR:
        k = int(n * min(1.0, mine) + 0.5)
        return (grad(FILL * k) if sm == "ok" else paint(FILL * k, SCALE_COLOR[sm])) + paint(EMPTY * (n - k), "track")
    hp = PALETTE[SCALE_COLOR[sp]][0] if sp != "ok" else gray
    hm = PALETTE[SCALE_COLOR[sm]][0] if sm != "ok" else None
    out, last = [], None
    for i in range(n):
        pos = (i + 0.5) / n
        top = hp if phone is not None and pos <= phone else trk
        bot = (hm or mix6(o, m, pos / mine)) if mine > 0 and pos <= mine else trk
        if (top, bot) != last:
            out.append(_fg(top) + _bg(bot))
            last = (top, bot)
        out.append("▀")
    return "".join(out) + RESET


def banner_width():
    """Ancho del encabezado y de los bloques de texto fijos: el ancho seguro, entre 20 y 60 columnas."""
    return max(20, min(safe_width(), 60))


def banner_rows(w):
    """Líneas del encabezado, cada una de `w` columnas como mucho:"""
    state = paint("DEBUG ACTIVO", "amber", True) if DEBUG else paint("debug off", "gray")
    try:
        r = storage_report()
        _head, detail, over = storage_lines()
        mine = r["total"] / CLEAN_LIMIT if CLEAN_LIMIT > 0 else 0.0
    except Exception:
        detail, over, mine = [], False, 0.0
    phone = disk_fraction()
    tab = card_tab()
    left = paint("▍", "orange") + paint(f"DLpy v{VERSION}", "white", True) + ((" " + tab[0]) if tab else "")
    rows = [left + " " * max(1, w - dwidth(left) - dwidth(state)) + state,
            paint(fit_text(f"  {platform_name()} · {machine_name()}", w), "gray")]
    lab, rt = (f"iPhone {phone * 100:.0f}% " if phone is not None else ""), f" DLpy {mine * 100:.0f}%"
    n = w - 2 - len(lab) - len(rt)
    if n < 6:                                   # sin sitio para etiquetas: solo la barra
        lab, rt, n = "", "", w - 2
    rows.append("  " + paint(lab, SCALE_COLOR[scale_state(phone, "phone")]) + storage_bar(n, phone, mine)
                + paint(rt, SCALE_COLOR[scale_state(mine, "mine")]))
    if over:
        rows += [paint(fit_text("  " + ln, w), "gray") for ln in detail]
    return rows


def card_inner():
    """Columnas útiles de un bloque de texto fijo (resultado, cambio de versión): el ancho del encabezado."""
    return banner_width()


def card_text_rows(text, inner, color="gray", bold=False, mark=None, mark_color="mint"):
    """Texto de una tarjeta ajustado a `inner` columnas."""
    out = []
    for i, ln in enumerate(wrap_text(text, max(8, inner - 2))):
        lead = (paint(mark, mark_color) + " ") if (mark and i == 0) else "  "
        out.append(lead + paint(ln, color, bold))
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
        rows += [paint("▍", "orange") + " " + paint(ln, "white", True) for ln in title_lines(str(title), inner - 2)]
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
        for ln in result_card_rows(title, meta, size, duration, os.path.basename(final), card_inner()):
            print(ln)
    except Exception as _ign:
        ignore("result_card", _ign)
        m_ok("Descarga lista")


def banner():
    """Encabezado fijo de 3 líneas; se pinta tras cada clear_screen (y al arrancar). Sin animación, hilo ni región anclada."""
    rows = banner_rows(banner_width())
    BANNER["h"] = len(rows)
    print("\n".join(rows))


def clear_screen():
    """Borra la consola y deja solo el banner (+ comentarios fijados)."""
    if DEBUG:
        print()
        print(paint(EMPTY * min(safe_width(), 40), "track"))
        banner()
        show_pinned()
        return
    if SOFTCLEAR and sys.stdout.isatty() and clear_mode_seq(CLEAR_MODE) is None:     # 1.3.2: con un DLPY_CLEARMODE propio se borra con él
        _soft_clear_screen()
        return
    native_clear()
    probe_cols(refresh=True)              # por si se giró el teléfono o cambió el tamaño
    banner()
    show_pinned()


SOFTCLEAR = _flag_env("DLPY_SOFTCLEAR", True)  # DLPY_SOFTCLEAR=0: clear_screen borra con native_clear() (parpadea)


class _SoftEOL:
    """Envoltura temporal de sys.stdout:"""

    def __init__(self, inner):
        self._inner = inner
        self.buf = []
        self._owner = threading.current_thread()

    def write(self, text):
        if threading.current_thread() is not self._owner:
            return 0                           # otro hilo (barra de progreso) repinta lo viejo: se descarta
        if isinstance(text, str) and text:
            self.buf.append(text.replace("\n", ERASE_EOL + "\n"))
        return len(text) if text else 0

    def writelines(self, lines):
        for ln in lines:
            self.write(ln)

    def flush(self):
        return None                            # nada sale hasta el final

    def __getattr__(self, name):
        return getattr(self._inner, name)


def _soft_clear_screen():
    """clear_screen sin parpadeo:"""
    real = sys.stdout
    soft = _SoftEOL(real)
    sys.stdout = soft
    ok = False
    try:
        probe_cols(refresh=True)
        banner()
        show_pinned()
        ok = True
    finally:
        sys.stdout = real                       # quita la envoltura
    body = "".join(soft.buf)
    with quiet("soft_clear"):
        # ESC[r suelta la región de desplazamiento anterior; el banner la vuelve a fijar si hace falta
        real.write("\x1b[?2026h\x1b[r\x1b[0m\x1b[H" + body + "\x1b[J" + PURGE_SEQ + "\x1b[?2026l")
        real.flush()
    return ok


OUTRO = _flag_env("DLPY_OUTRO", True)          # DLPY_OUTRO=0: antes del atajo solo se limpia la consola (sin deshacerse)
OUTRO_SECS = 0.7                               # lo que tarda en deshacerse la pantalla
OUTRO_STEPS = 10                               # cuadros: solo se reenvían las celdas que cambian (los terminales de iOS no aguantan más)
try:
    OUTRO_HOLD = max(0.0, float(os.environ.get("DLPY_OUTROHOLD", "1.2")))    # segundos con la pantalla a la vista
except ValueError:
    OUTRO_HOLD = 1.2


def outro_clear():
    """Lo último antes de enviar el archivo al atajo:"""
    if DEBUG or not sys.stdout.isatty():
        return False
    try:
        sw, rows = safe_width(), term_rows()
        if OUTRO and ANIM_LIVE and USE_COLOR and TRUECOLOR and sw >= 30 and rows >= 8:
            time.sleep(OUTRO_HOLD)
            a, b = theme_rgb()
            cells = []
            for y in range(1, rows + 1):
                for x in range(1, sw + 1):
                    blank = 0.1 + 0.9 * _rn(x * 131 + y * 7 + 3.1)           # cuándo se apaga
                    noisy = _rn(x * 53 + y * 29 + 1.7) < 0.5                # ¿pasa antes por ruido?
                    cells.append((x, y, blank, max(0.0, blank - 0.28) if noisy else None))
            state = {}
            t0 = time.monotonic()
            try:
                sys.stdout.write(CURSOR_HIDE + WRAP_OFF)
                for i in range(1, OUTRO_STEPS + 1):
                    k = i / float(OUTRO_STEPS)
                    out, row_y, next_x = [], None, None
                    for x, y, blank, noise in cells:
                        new = 2 if k >= blank else (1 if (noise is not None and k >= noise) else 0)
                        if new == state.get((x, y), 0):
                            continue
                        state[(x, y)] = new
                        if (y, x) != (row_y, next_x):                      # salto de cursor solo si no sigue a la celda anterior
                            out.append(cur_to(y, x))
                        row_y, next_x = y, x + 1
                        if new == 1:
                            g = mix(a, b, (x - 1) / float(max(1, sw - 1)))
                            out.append(_fg(mix(BLACK, g, 0.55)) + SITE_GLITCH[int(_rn(x * 17 + y * 5 + i) * len(SITE_GLITCH))])
                        else:
                            out.append(RESET + " ")
                    out.append(RESET)
                    sys.stdout.write("".join(out))
                    sys.stdout.flush()
                    wait = t0 + OUTRO_SECS * i / OUTRO_STEPS - time.monotonic()
                    if wait > 0:
                        time.sleep(wait)
            finally:
                sys.stdout.write(RESET + WRAP_ON + CURSOR_SHOW)
                sys.stdout.flush()
        native_clear()
        sys.stdout.write(RESET + CURSOR_SHOW)
        sys.stdout.flush()
        return True
    except KeyboardInterrupt:
        raise
    except Exception as _ign:
        ignore("outro_clear", _ign)
        return False


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


def file_title(name):
    """Bloque del archivo que se va a guardar:"""
    header("ARCHIVO", gap=False)
    lines = wrap_text(str(name), term_width() - 1)
    if len(lines) > 3:
        lines = lines[:2] + [fit_text(" ".join(lines[2:]), max(8, term_width() - 2))]
    print(paint("▍", "orange") + paint(lines[0], "white", True))
    for ln in lines[1:]:
        print(" " + paint(ln, "white", True))


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


def print_rows(rows, flags, head=None):
    """rows:"""
    if not rows:
        return
    w = term_width()
    nw = max(len(str(r["n"])) for r in rows)
    pw = 1 + nw + 2                                   # « n  »
    fw = max(1, 2 * len(flags) - 1)                   # ancho de la columna de marcas
    ncol = len(rows[0]["cols"])
    allr = [r["cols"] for r in rows] + ([head] if head else [])
    widths = [max(dwidth(c[i]) for c in allr) for i in range(ncol)]

    def prefix(r):               # ★ («b») o ▸ (predeterminada) ocupan el margen: no restan ancho
        return (flag_mark("best") if "best" in r["flags"]
                else flag_mark("default") if "default" in r["flags"] else " ") \
            + paint(f"{r['n']:>{nw}}", "orange", True) + "  "

    def line(r, body_vis, body):
        gap = max(1, w - pw - body_vis - fw - 1)
        return prefix(r) + body + " " * gap + " ".join(flag_mark(k) if k in r["flags"] else " " for k in flags)

    for sep in ("  ", " "):                       # tabla alineada
        if pw + sum(widths) + len(sep) * (ncol - 1) + 1 + fw + 1 <= w:
            def pad(c, i):
                return c + " " * (widths[i] - dwidth(c))
            if head:
                print(" " * pw + paint(sep.join(pad(h, i) for i, h in enumerate(head)).rstrip(), "gray"))
            for r in rows:
                body = sep.join((pad(c, i) if i == 0 else paint(pad(c, i), "gray")) for i, c in enumerate(r["cols"]))
                print(line(r, sum(widths) + len(sep) * (ncol - 1), body))
            return

    short = {"con audio": "c/audio", "sin audio": "s/audio"}
    room = max(8, w - pw - fw - 2)
    texts = None
    for sep, abbr in ((" · ", False), ("·", False), ("·", True)):     # línea compacta
        texts = [sep.join((short.get(c, c) if abbr else c) for c in r["cols"] if c) for r in rows]
        if all(dwidth(t) <= room for t in texts):
            break
    for r, text in zip(rows, texts):
        lines = wrap_text(text, room)
        first = lines[0].split(" · ", 1) if " · " in lines[0] else [lines[0]]
        body = first[0] + (paint(" · " + first[1], "gray") if len(first) > 1 else "")
        print(line(r, dwidth(lines[0]), body))
        for ln in lines[1:]:
            print(" " * pw + paint(ln, "gray"))


NESTED_IOS = False        # a-Shell: esta ejecución la lanzó runpy dentro del proceso de otra versión


def drain_pending_input(max_wait=0.08):
    """Descarta bytes ya pendientes en stdin (Enter residual al abrir desde Atajos)."""
    if NESTED_IOS:
        return                            # recién actualizada en el mismo proceso: no se lee stdin
    with quiet("drain_pending_input"):
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


def split_prompt(prompt):
    """Parte un prompt largo por palabras (el terminal lo cortaría a media palabra)."""
    prompt = str(prompt)
    w = term_width()
    if dwidth(prompt) <= w - 10 and "\n" not in prompt:
        return [], prompt
    lines = wrap_text(prompt.rstrip(), w - 10)
    last = lines[-1] + (" " if prompt.endswith(" ") else "")
    return lines[:-1], last


def ask_line(prompt, phantom=True, plain=None):
    """input()"""
    note_prompt(plain or prompt)
    cursor_show()
    input_unlock()                   # sale una pregunta: se habilita la entrada
    drain_pending_input()
    pre, prompt = split_prompt(pstyle(prompt))
    for ln in pre:
        print(ln)
    prompt = rl_safe(prompt)
    t0 = time.time()
    r = input(prompt)
    if phantom and not r.strip() and (time.time() - t0 < PHANTOM_SECS or time.time() - START_T < PHANTOM_BOOT):
        # Segunda oportunidad: se borra la línea del Enter fantasma y el prompt vuelve a salir en el
        # mismo renglón. Sin terminal interactivo input() lo muestra en una línea nueva.
        erase_input_line(prompt, r)
        r = input(prompt)
    return r


PROMPT = "▸ "
INPLACE = sys.stdout.isatty() and not DEBUG     # ¿se puede borrar una línea ya escrita?


def erase_seq(prompt, typed, cols):
    """Secuencia que, justo tras el Enter de un input(), sube sobre la línea escrita (prompt + texto; si no cupo en una fila, sobre to…"""
    plain = re.sub(r"[\x01\x02]", "", _ANSI_RE.sub("", str(prompt)))
    rows = max(1, -(-(dwidth(plain) + dwidth(typed)) // max(1, cols)))
    return "\x1b[1A\x1b[2K" * rows + "\r"


def erase_input_line(prompt, typed=""):
    """Borra la línea que acaba de ocupar un input()"""
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
    """Respuesta vacía o inválida:"""
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


def bar_str(w, frac, now, indet=False, warn=False):
    """Barra Aurora de `w` columnas:"""
    w = max(0, int(w))
    if indet:
        seg = max(3, w // 5)
        span = max(0, w - seg)
        period = max(1, 2 * span)
        k = int(now * 8) % period
        pos = k if k <= span else period - k
        return track_str(pos) + grad(FILL * seg) + track_str(w - seg - pos)
    f = int(w * max(0.0, min(1.0, frac)))
    fill = (paint(FILL * f, "amber") if warn else grad(FILL * f)) if f else ""
    rest = w - f
    t = ""
    if rest > 0 and frac < 1.0 and TIP:
        t, rest = paint(TIP, "amber" if warn else "magenta"), rest - 1
    return fill + t + track_str(rest)


_CURSOR = {"hidden": False, "atexit": False}


def cursor_hide():
    """Oculta el cursor mientras un panel se redibuja (solo en terminal y sin debug). Al salir siempre vuelve."""
    with quiet("cursor_hide"):
        if _CURSOR["hidden"] or DEBUG or not sys.stdout.isatty():
            return
        _CURSOR["hidden"] = True
        if not _CURSOR["atexit"]:
            _CURSOR["atexit"] = True
            atexit.register(cursor_show)
        sys.stdout.write(CURSOR_HIDE)
        sys.stdout.flush()


def cursor_show():
    """Devuelve el cursor (no hace nada si no estaba oculto)."""
    if not _CURSOR["hidden"]:
        return
    _CURSOR["hidden"] = False
    with quiet("cursor_show"):
        sys.stdout.write(CURSOR_SHOW)
        sys.stdout.flush()


class Bar:
    """Progreso en vivo, redibujado en su sitio por un hilo (≈7 fps)."""

    def __init__(self, panel=False):
        self.lock = threading.RLock()
        self.th = None
        self.run = False
        self._panel_req = bool(panel)
        self.live = self.panel = False
        self._refresh_live()
        self.drawn = 0                      # líneas que el panel tiene pintadas ahora
        self.last_len = 0                   # (una línea) columnas pintadas
        self.label, self.pct, self.tail = "", None, ""
        self.indet, self.hold, self.t0 = True, 0.0, 0.0
        self.wpaths, self.wtotal, self.wsamp, self.wspeed = [], 0, None, None
        self.hook_t, self.last_draw = 0.0, 0.0
        self.final_tail, self.final_size = "", ""
        self.step, self.sizes, self.engine = "", None, ""
        self.hist = []                       # velocidades recientes (para detectar una caída)
        self.slow = False                    # velocidad caída (barra ámbar)
        self.w = safe_width()                # se mide en el hilo principal (en a-Shell el hilo
                                             # de la barra no ve el tamaño real del terminal)

    def _refresh_live(self):
        """Vivo/panel según el estado ACTUAL (la barra de la descarga se crea mientras --shortcutpick aún va en silencio, pero se usa ya c…"""
        self.live = sys.stdout.isatty() and not DEBUG and not QUIET["on"]
        self.panel = self._panel_req and self.live

    # ── ciclo de vida ──
    def start(self, label, indeterminate=True, tail=""):
        self.stop()
        self._refresh_live()
        self.w = safe_width()
        with self.lock:
            self.label, self.pct, self.tail = label, None, tail
            self.indet, self.hold, self.t0 = indeterminate, 0.0, time.time()
            self.wpaths, self.wtotal, self.wsamp, self.wspeed = [], 0, None, None
            self.hook_t = 0.0
            self.final_tail = self.final_size = ""
            self.step, self.sizes, self.engine = "", None, ""
            self.hist = []
            self.slow = False
        if not self.live:
            m_info(label + "...")
            return
        global ACTIVE_BAR
        ACTIVE_BAR = self
        cursor_hide()
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
            if indeterminate is not None:
                self.indet = indeterminate

    def _erase(self):
        """Borra lo pintado (con `self.lock` tomado)."""
        if self.drawn:
            sys.stdout.write(cur_up(self.drawn) + "\r" + ERASE_BELOW)
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
        if not keep and ACTIVE_BAR is None:
            cursor_show()
        if msg:
            {"ok": m_ok, "warn": m_warn, "info": m_info, "err": m_err}[level](msg)

    def done(self, min_secs=0.0):
        """Borra la barra y deja la línea final «✓ etiqueta … tamaño». Si duró menos de min_secs solo se borra."""
        was_live = self.th is not None
        elapsed = time.time() - self.t0
        with self.lock:
            label = self.label
            size = self.final_size or spaced(self.final_tail)
        self.stop()
        if elapsed < min_secs:
            return
        if not was_live:
            m_ok(f"{label}: listo" + (f" ({size})" if size else ""))
            return
        sys.stdout.write("\r" + nowrap(self._done_line(label, size or mmss(elapsed))) + "\n")
        sys.stdout.flush()

    def _done_line(self, label, size):
        w = self.w
        label = label.replace("Convirtiendo", "Convertido", 1)
        left = f"{paint('✓', 'mint')} {fit_text(label, max(4, w - dwidth(size) - 4))}"
        return left + " " * max(1, w - dwidth(left) - dwidth(size)) + paint(size, "gray")

    # ── dibujo ──
    def _state(self):
        now = time.time()
        with self.lock:
            return (now, self.label, self.pct, self.tail,
                    self.indet or self.pct is None, now < self.hold, self.step,
                    self.sizes, self.engine, list(self.hist))

    def _slow(self, hist):
        """¿La velocidad cayó a menos de la mitad de la habitual?"""
        if len(hist) < 8:
            self.slow = False
            return False
        cur = sum(hist[-3:]) / 3.0
        prev = sorted(hist[-123:-3])
        ref = prev[len(prev) * 3 // 4] if prev else cur
        self.slow = cur < (0.7 if self.slow else 0.5) * ref
        return self.slow

    def _panel_lines(self):
        """[línea 1: etiqueta · paso · %, línea 2: barra, línea 3: métricas]."""
        w = self.w
        now, label, pct, tail, indet, holding, step, sizes, engine, hist = self._state()
        slow = self._slow(hist)
        frac = 0.0 if indet else (pct or 0.0) / 100.0
        ptxt = mmss(now - self.t0 if self.t0 else 0).rjust(5) if indet else f"{frac * 100:5.1f}%"
        right = (paint(step, "gray") + "  " if step else "") + (paint(ptxt, "gray") if indet else ptxt)
        rw = dwidth(step) + (2 if step else 0) + dwidth(ptxt)
        left = paint("●", "amber" if holding else "orange") + " " + fit_text(label, max(4, w - rw - 4))
        l1 = left + " " * max(1, w - dwidth(left) - rw) + right
        parts = []
        for sg in ([x for x in re.split(r"\s{2,}", tail.strip()) if x] if tail else []):
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
        return [l1, bar_str(w, frac, now, indet=indet, warn=slow), "  ".join(parts)]

    def _paint(self, lines):
        """Pinta las líneas en su sitio (con `self.lock` tomado)."""
        out = cur_up(self.drawn) if self.drawn else ""
        out += "".join("\r" + ln + ERASE_EOL + "\n" for ln in lines)
        if self.drawn > len(lines):
            out += ERASE_BELOW                 # el panel se encogió: borra lo que sobra
        sys.stdout.write(WRAP_OFF + out + WRAP_ON)
        sys.stdout.flush()
        self.drawn = len(lines)
        self.last_draw = time.time()

    def _line(self):
        """Versión de una línea: «● etiqueta ━━╸╌╌ 0:03» (o con porcentaje)."""
        w = self.w
        now, label, pct, _tail, indet, holding = self._state()[:6]
        right = mmss(now - self.t0 if self.t0 else 0) if indet else f"{pct:5.1f}%"
        lab = fit_text(label, max(4, w // 2))
        bw = w - (2 + dwidth(lab) + 1 + 1 + len(right))
        bar = (bar_str(bw, (pct or 0) / 100.0, now, indet=indet) + " ") if bw >= 4 else ""
        return f"{paint('●', 'amber' if holding else 'orange')} {lab} {bar}{paint(right, 'gray')}", w

    def _draw(self):
        if self.panel:
            with self.lock:
                self._paint(self._panel_lines())
            return
        line, vis = self._line()
        with self.lock:
            sys.stdout.write("\r" + nowrap(line) + ERASE_EOL + "\r")
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
        if SCENE["on"] and total and self.label == pp_label("FFmpegMerger"):
            SCENE["pp_pct"] = 100.0 if pct is None else pct                 # 1.3.9: la unión real, para el dibujo del modo real
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
            time.sleep(PANEL_TICK)


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
    """Etiqueta de la barra de descarga."""
    info = d.get("info_dict") or {}
    h = info.get("height") or 0
    w = info.get("width") or 0
    res = str(info.get("resolution") or "")
    v = info.get("vcodec")
    # Video si hay tamaño, resolución tipo 1920x1080, o códec de video real
    if h or w or ("x" in res and "audio" not in res.lower()) or has(v):
        return res_label(info) if (h or w or res) else "Video"
    if "video" in STREAM_KINDS.get(str(info.get("format_id") or ""), ()):       # 1.3.6: «sd» / «hd» sin datos en el hook: es video
        tag = format_tag(info)
        return tag if tag != "?" else "Video"
    return info.get("language") or "Audio"


def progress_pct(d):
    """Porcentaje (0-100)"""
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
    """Una barra por proceso:"""

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
        self._win = []            # ventana de (instante, bytes) de los últimos ~4 s: velocidad promedio estable

    def _speed(self, d):
        """Velocidad ESTABLE:"""
        done = d.get("downloaded_bytes") or 0
        now = time.time()
        self._maxb = max(self._maxb, done)
        if self._smp is None:
            self._smp = (now, done)
        elif now - self._smp[0] >= 0.5 and done >= self._smp[1]:
            inst = (done - self._smp[1]) / (now - self._smp[0])
            self._spd = inst if self._spd is None else self._spd * 0.7 + inst * 0.3
            self._smp = (now, done)
        win = self._win
        if not win or now - win[-1][0] >= 0.25:
            if win and done < win[-1][1]:          # el contador retrocedió (reintento): ventana nueva
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

    def _facts(self, d):
        """1.3.6:"""
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

    def begin(self):
        scene_status("Preparando descarga", frac=0.08)
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
                scene_shape(d.get("info_dict"))
                scene_stream(scene_kind(d), self.seen, self.total, scene_lang(d))
                self._facts(d)
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
            scene_progress(pct)
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
            scene_progress(100.0)
            try:
                for _k in stream_kinds(d):                 # 1.3.6: un stream con video y audio en uno da por hechos los dos
                    scene_stream_done(_k)
            except Exception:
                pass
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
            SCENE["pp_pct"] = None
            name = str(d.get("postprocessor") or "")
            scene_status(scene_pp_text(name), frac=min(0.94, max(SCENE["frac"], 0.8) + 0.03))
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

    def abort(self):
        self.bar.stop()


# ───────────────────── [B6] Terminal: teclado y cuenta regresiva ─────────────────────
def hide_keyboard(settle=0.0):
    """iOS (a-Shell): baja el teclado. `settle` espera (s) a que el terminal tome su alto nuevo."""
    with quiet("hide_keyboard"):
        os.system("hideKeyboard >/dev/null 2>&1")
        if settle:
            time.sleep(settle)


def settle_terminal(max_wait=1.5, calm=0.25):
    """iOS (a-Shell):"""
    def rows_now():
        try:
            return term_rows()
        except (OSError, ValueError):
            return None
    with quiet("settle_terminal"):
        t0 = time.time()
        last = rows_now()
        since = t0
        while time.time() - t0 < max_wait:
            time.sleep(KEYBOARD_POLL)
            cur = rows_now()
            if cur != last:
                last, since = cur, time.time()
            elif time.time() - since >= calm:
                break


def countdown_supported():
    try:
        if not (tty_both()):
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
    """Restaura el terminal y fuerza eco, modo de línea y Enter (a-Shell no siempre respeta la restauración simple)."""
    import termios
    with quiet("_restore_tty"):
        termios.tcsetattr(fd, termios.TCSANOW, old)
    with quiet("_restore_tty"):
        cur = termios.tcgetattr(fd)
        cur[0] |= termios.ICRNL
        cur[3] |= termios.ECHO | termios.ICANON | termios.ISIG
        termios.tcsetattr(fd, termios.TCSANOW, cur)


INPUT_LOCK = {"fd": None, "old": None}
LOCK_INPUT = _flag_env("DLPY_LOCK", False)      # apagado: congelaba a-Shell


def input_lock():
    """iOS (a-Shell):"""
    if not LOCK_INPUT or NESTED_IOS or INPUT_LOCK["fd"] is not None:
        return False
    try:
        if not (tty_both()):
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
    """Devuelve el terminal a su modo normal; antes descarta lo tecleado mientras estuvo bloqueado."""
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
    """Anota en running.json la pregunta en curso (pista si el proceso se congela y se cierra a la fuerza)."""
    with quiet("note_prompt"):
        if not os.path.isfile(RUNNING_FILE):
            return
        data = load_json(RUNNING_FILE)
        if not data:
            return
        text = re.sub(r"\s+", " ", _ANSI_RE.sub("", str(prompt))).strip()
        data["prompt"] = text[:100]
        data["prompt_time"] = int(time.time())
        save_json(RUNNING_FILE, data)


def reexec_script():
    """Ejecuta SCRIPT_PATH (recién instalado o restaurado)"""
    import runpy
    with quiet("reexec_script"):
        if ACTIVE_BAR is not None:
            ACTIVE_BAR.stop()
    with quiet("reexec_script"):
        sys.stdout.flush()
        sys.stderr.flush()
    # a-Shell: ni tcsetattr ni select sobre stdin aquí
    sys._dlpy_reexec = True
    runpy.run_path(SCRIPT_PATH, run_name="__main__")


def timed_input(prompt, seconds=WAIT_SECONDS, phantom=True, plain=None):
    """Cuenta regresiva."""
    if not countdown_supported():
        return ask_line(prompt, phantom, plain)
    note_prompt(plain or prompt)
    cursor_show()
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
                key = (f, secs, int(urg * 10))
                if key != shown:
                    shown = key
                    # el degradado se acorta y pasa a magenta a medida que se agota
                    cd = (grad(FILL * f, 0.6 * urg, 1.0) + paint(EMPTY * (nb - f), "track")) if nb else ""
                    sys.stdout.write(CLR + nowrap(prompt + cd
                                                  + paint(f" {secs} s", "amber" if secs <= 3 else "gray")))
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
    """Como shutil.copy2, pero el chmod/utime del destino es opcional (algunos sistemas de archivos los rechazan)."""
    shutil.copyfile(src, dst)
    try:
        st = os.stat(src)
        os.utime(dst, ns=(st.st_atime_ns, st.st_mtime_ns))
    except OSError:
        pass
    return dst


def move_file(src, dst):
    """Como shutil.move, pero copiando con copy_file cuando rename no basta (otro sistema de archivos)."""
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
    """Texto de una pregunta s/n con el final unificado:"""
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
    """Pregunta s/n y la repite hasta recibir una respuesta válida."""
    if QUIET["on"]:                          # 0.8.2: --shortcutpick no pregunta antes de la descarga: respuesta predeterminada
        return bool(default)
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


def ffmpeg_available():
    with quiet("ffmpeg_available"):
        from yt_dlp.postprocessor import FFmpegPostProcessor
        if FFmpegPostProcessor().available:
            return True
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


def acodec_short(f):
    """«mp4a.40.2» → «mp4a» (el códec de audio de un formato, «?» si no lo trae)."""
    return (f.get("acodec") or "?").split(".")[0]


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
    codec = acodec_short(f)
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
    """yt-dlp deja vcodec/acodec en None cuando no conoce el códec (MP4 directos de algunos sitios)."""
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
        guess = ext in APPLE_VEXT and looks_video
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
        return term_rows()
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
    """Líneas ocupadas arriba: el encabezado más los comentarios fijados."""
    return BANNER["h"] + pinned_lines()


def list_cap(overhead=16):
    """Filas máximas de la lista de formatos dentro de las 26 líneas de la interfaz."""
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
    """Calidad de cada audio:"""
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
    """Calidad de cada video:"""
    def rng(f):
        bits = detect_bit_depth(f)
        return (detect_hdr(f) or "", bits if bits and bits > 8 else 0)
    return [(res_label(f), rng(f)) for f in videos]


def best_per_quality(rows, keys, rank, keep=None):
    """Índices de UNA fila por calidad:"""
    groups = {}
    for i, k in enumerate(keys):
        groups.setdefault(k, []).append(i)
    out = [keep if keep in g else max(g, key=rank) for g in groups.values()]
    return sorted(out)


def short_pick(rows, take, keep=None, uniq=None, first=False):
    """Índices de las filas de la lista corta:"""
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
    """Quita las columnas vacías en TODAS las filas (así una columna opcional solo ocupa sitio si algún formato la usa)."""
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
                     f"{f.get('ext')} {acodec_short(f)} {abr_of(f):.0f}k"]}


def ask_default_track(tracks, original):
    """Devuelve (pista, sin_respuesta)."""
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
    """Ejecuta ffmpeg y dibuja el avance real en `bar`."""
    import subprocess
    exe = getattr(pp, "executable", None) or shutil.which("ffmpeg") or "ffmpeg"
    pfile, efile = dst + ".progress", dst + ".err"
    cmd = [exe, "-y", "-hide_banner", "-loglevel", "info" if DEBUG else "error", "-nostats",
           "-progress", pfile, "-i", "file:" + src] + list(opts) + ["file:" + dst]
    for f in (pfile, efile):
        with quiet("ffmpeg_progress", OSError):
            os.remove(f)
    dbg("ffmpeg comando", shlex.join(cmd))
    errfh = None
    try:
        errfh = open(efile, "w", encoding="utf-8")
        proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=errfh)
    except Exception as e:
        if errfh is not None:
            with quiet("ffmpeg_progress"):
                errfh.close()
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
                    _pc = min(99.9, secs / duration * 100)
                    bar.set(pct=_pc, tail="  ".join(parts), val=speed)
                    scene_conv_progress(_pc)                       # 1.2.1: el mismo % en la escena de conversión
                else:
                    if speed:
                        parts.append(f"{speed:.1f}x")
                    parts.append(f"t={int(secs) // 60:02d}:{int(secs) % 60:02d}")
                    bar.set(tail="  ".join(parts), indeterminate=True, val=speed)
                    scene_conv_progress(None)
            bar.kick()
            time.sleep(FFMPEG_TICK)
    except BaseException:
        with quiet("drain_err"):
            proc.terminate()
            proc.wait(timeout=3)
        raise
    finally:
        if errfh is not None:
            with quiet("drain_err"):
                errfh.close()
    drain_err()
    ok = proc.returncode == 0
    dbg("ffmpeg salida", {"codigo": proc.returncode, "segundos": round(time.time() - t0, 1),
                          "bytes_salida": os.path.getsize(dst) if os.path.isfile(dst) else 0})
    err = ""
    with quiet("ffmpeg_progress"):
        err = read_text(efile).strip()[-300:]
    for f in (pfile, efile):
        with quiet("drain_err", OSError):
            os.remove(f)
    if not ok:
        raise RuntimeError(err or f"ffmpeg terminó con código {proc.returncode}")
    bar.set(pct=100.0, tail="")
    scene_conv_progress(100.0)


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
HEVC_CODEC = ("hvc1", "hev1", "hevc", "h265")


def _short(codec):
    return (codec or "?").split(".")[0]


def apple_plan(kind, fmt, selected, merge_ext):
    """Qué haría falta para que el resultado final sea nativo en Apple."""
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
    """Profundidad de bits del formato si se puede saber; None si no hay dato claro."""
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
    """Profundidad con la que se codifica un origen de `bits`:"""
    try:
        b = int(bits or 0)
    except (TypeError, ValueError):
        return 8
    return 8 if b <= 8 else 10 if b <= 10 else 12


def out_pix(bits):
    """pix_fmt de ffmpeg para codificar a `bits`."""
    return {8: "yuv420p", 10: "yuv420p10le", 12: "yuv420p12le"}[encode_bits(bits)]


def bits_choices(bits, hdr=None):
    """[(bits_salida, texto)] que se ofrecen al convertir un origen de más de 8 bits."""
    top = encode_bits(bits)
    out = []
    if top > 10:
        out.append((top, f"{top} bits"
                    + (f" (origen de {bits})" if bits != top else " (original)")
                    + " · Apple normalmente no lo reproduce"))
    out.append((10, "10 bits" + (" (original)" if bits in (9, 10) else "") + " · compatible con Apple"))
    out.append((8, "8 bits · SDR con tone mapping (más lento)" if hdr else "8 bits · más rápido, menos precisión de color"))
    return out


def codec_bit_depth(codec):
    """Profundidad de bits que declara la cadena del códec (RFC 6381), o None si no dice."""
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
    """Etiqueta corta del rango del video para la lista:"""
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
    tm = (plan.get("hdr_mode") == "tonemap") if "hdr_mode" in plan else bool(plan.get("hdr")) and encode_bits(plan.get("out_bits")) <= 8
    return max(0.15, (h / 1080.0) ** 2 * (fps / 30.0) * (3.0 if tm else 1.0))      # 1.2.1: el tone mapping (HDR → SDR) cuesta ~3×


def measured_conv_speed(index=None):
    """Velocidad de conversión REAL de este equipo:"""
    with quiet("measured_conv_speed"):
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
    """Segundos estimados de conversión, o None si no se puede estimar."""
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


HDR_TAGS = {"pq": ("bt2020", "smpte2084", "bt2020nc"), "hlg": ("bt2020", "arib-std-b67", "bt2020nc")}
SDR_TAGS = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]
_FILTERS = {}


def hdr_kind(plan, probed=None):
    """1.2.1:"""
    trc = str((probed or {}).get("color_transfer") or "").lower()
    if trc == "smpte2084":
        return "pq"
    if trc == "arib-std-b67":
        return "hlg"
    if trc and trc not in ("unknown", "unspecified"):
        return None                                          # el archivo dice SDR (bt709, …) aunque el análisis dijera otra cosa
    lab = str(plan.get("hdr") or "").upper()
    if not lab:
        return None
    return "hlg" if "HLG" in lab else "pq"


def hdr_mode(plan):
    """«keep» (el HDR se conserva: salida de 10 bits o más), «tonemap» (sale a 8 bits: se pasa a SDR) o None (no es HDR)."""
    if not plan.get("hdr_kind"):
        return None
    return "keep" if encode_bits(plan.get("out_bits")) >= 10 else "tonemap"


def tonemap_filter(kind):
    """Filtro de ffmpeg que pasa HDR (PQ o HLG, BT.2020)"""
    tin = "arib-std-b67" if kind == "hlg" else "smpte2084"
    return (f"zscale=tin={tin}:pin=bt2020:min=bt2020nc:rin=tv:t=linear:npl=100,format=gbrpf32le,"
            "zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p")


def ffmpeg_has_filters(exe, names=("zscale", "tonemap")):
    """True si este ffmpeg trae todos los filtros `names` (se lee una sola vez por ffmpeg)."""
    import subprocess
    exe = exe or shutil.which("ffmpeg")
    if not exe:
        return False
    if exe not in _FILTERS:
        have = set()
        with quiet("ffmpeg_has_filters"):
            r = subprocess.run([exe, "-hide_banner", "-filters"], capture_output=True, text=True, timeout=15,
                               stdin=subprocess.DEVNULL)
            for ln in (r.stdout or "").splitlines():
                parts = ln.split()
                if len(parts) >= 2:
                    have.add(parts[1])
        _FILTERS[exe] = have
    return all(n in _FILTERS[exe] for n in names)


def hdr_prepare(plan, real, exe):
    """1.2.1:"""
    plan.pop("hdr_mode", None)
    plan["hdr_kind"] = hdr_kind(plan, real)
    if not plan["hdr_kind"]:
        return
    mode = hdr_mode(plan)
    if mode == "tonemap" and not ffmpeg_has_filters(exe):
        m_warn("Este ffmpeg no trae zscale/tonemap: el HDR se conserva en 10 bits (a 8 bits sin tone mapping se vería apagado).")
        plan["out_bits"], mode = 10, "keep"
    plan["hdr_mode"] = mode
    if mode == "keep":
        m_info("HDR detectado: se conserva con sus etiquetas de color (BT.2020 · " + ("HLG" if plan["hdr_kind"] == "hlg" else "PQ") + ").")
    else:
        m_info("HDR detectado: se pasa a SDR (BT.709) con tone mapping; tarda más.")


def video_encoder_attempts(plan):
    """[(códec_corto, nombre_legible, opciones)] a probar en orden; la primera que funcione se queda."""
    if not plan["venc"]:
        tag = ["-tag:v", "hvc1"] if plan.get("hvc") else []
        return [(None, "remux (sin recodificar video)", ["-c:v", "copy"] + tag)]
    b = f"{plan['vbr']}k"
    ob = encode_bits(plan.get("out_bits"))
    mode, kind = plan.get("hdr_mode"), plan.get("hdr_kind")
    vf, tags, xp = [], [], []
    if mode == "keep" and kind in HDR_TAGS:
        pr, tr, mx = HDR_TAGS[kind]
        tags, xp = ["-color_primaries", pr, "-color_trc", tr, "-colorspace", mx], [f"colorprim={pr}", f"transfer={tr}", f"colormatrix={mx}"]
    elif mode == "tonemap" and kind:
        ob, vf, tags = 8, ["-vf", tonemap_filter(kind)], list(SDR_TAGS)
    else:
        mode = None
    sfx = " HDR" if mode == "keep" else " SDR" if mode == "tonemap" else ""

    def vt_opts(bits):
        o = vf + ["-c:v", "hevc_videotoolbox", "-b:v", b, "-allow_sw", "1",
                  "-tag:v", "hvc1", "-pix_fmt", out_pix(bits)] + tags
        return o + (["-profile:v", "main10"] if bits == 10 else [])

    def x265_opts(bits):
        o = vf + ["-c:v", "libx265", "-preset", "veryfast", "-crf", "26",
                  "-tag:v", "hvc1", "-pix_fmt", out_pix(bits)] + tags
        ps = ([f"profile=main{bits}"] if bits > 8 else []) + xp
        return o + (["-x265-params", ":".join(ps)] if ps else [])

    x264 = vf + ["-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                 "-pix_fmt", "yuv420p"] + tags          # H.264 High 10 casi no se usa en Apple
    if ob == 12:
        sets = [("hevc", "x265 12 bits", x265_opts(12)),
                ("hevc", "VideoToolbox HEVC 10 bits", vt_opts(10)),
                ("hevc", "x265 10 bits", x265_opts(10))]
        return sets + ([("h264", "x264", x264)] if mode is None else [])
    sets = [("hevc", "VideoToolbox HEVC" + sfx, vt_opts(ob)),
            ("hevc", "x265" + sfx, x265_opts(ob))]
    return sets + ([("h264", "x264" + sfx, x264)] if mode != "keep" else [])


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
    """Bits por componente de un pix_fmt de ffmpeg (yuv420p → 8, yuv420p10le → 10, p010le → 10), o None si no se reconoce."""
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
    tm = re.search(r"smpte2084|arib-std-b67", body)               # 1.2.1: «yuv420p10le(tv, bt2020nc/bt2020/smpte2084, …)»
    if tm:
        out["color_transfer"] = tm.group(0)
    return out


def probe_video(exe, path, timeout=20):
    """Lee el video de `path`:"""
    import subprocess
    exe = exe or shutil.which("ffmpeg")
    cands = []
    if exe:
        d, n = os.path.split(exe)
        cands.append(os.path.join(d, n.lower().replace("ffmpeg", "ffprobe")) if d else None)
    cands.append(shutil.which("ffprobe"))
    for pr in dict.fromkeys(c for c in cands if c):
        with quiet("probe_video ffprobe"):
            r = subprocess.run([pr, "-v", "error", "-select_streams", "v:0", "-show_entries",
                                "stream=codec_name,profile,pix_fmt,bits_per_raw_sample,bit_rate,color_space,color_transfer,color_primaries,color_range", "-of", "json",
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
                for _ck in ("color_space", "color_transfer", "color_primaries", "color_range"):    # 1.2.1: el color real (HDR)
                    if st.get(_ck):
                        out[_ck] = st[_ck]
                try:
                    out["kbps"] = int(round(int(st.get("bit_rate")) / 1000.0))
                except (TypeError, ValueError):
                    pass
                return out
    if exe:
        with quiet("probe_video ffmpeg"):
            r = subprocess.run([exe, "-hide_banner", "-i", "file:" + path], capture_output=True,
                               text=True, timeout=timeout, stdin=subprocess.DEVNULL)
            return parse_ffmpeg_video(r.stderr)
    return None


def probe_stream_bits(exe, fmt, timeout=12):
    """Bits del stream de video de `fmt` leyendo su cabecera con ffmpeg (sin descargarlo)."""
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


def parse_ffmpeg_facts(text):
    """1.3.6: «ffmpeg -i» → {"v": {codec, width, height, fps, kbps} | None, "a": {codec, hz, kbps} | None} (solo lo que aparezca). Pura."""
    out = {"v": None, "a": None}
    for ln in (text or "").splitlines():
        if "Stream #" not in ln:
            continue
        if "Video:" in ln and out["v"] is None and "attached pic" not in ln:
            body = ln.split("Video:", 1)[1]
            m = re.match(r"\s*(\w+)", body)
            v = {"codec": m.group(1).lower() if m else None}
            sz = re.search(r"[,\s](\d{2,5})x(\d{2,5})(?=[\s,\[]|$)", body)
            if sz and int(sz.group(1)) >= 16 and int(sz.group(2)) >= 16:
                v["width"], v["height"] = int(sz.group(1)), int(sz.group(2))
            fm = re.search(r"(\d+(?:\.\d+)?)\s*fps", body)
            if fm:
                v["fps"] = float(fm.group(1))
            km = re.search(r",\s*(\d+)\s*kb/s", body)
            if km:
                v["kbps"] = int(km.group(1))
            out["v"] = v
        elif "Audio:" in ln and out["a"] is None:
            body = ln.split("Audio:", 1)[1]
            m = re.match(r"\s*(\w+)", body)
            a = {"codec": m.group(1).lower() if m else None}
            hm = re.search(r"(\d+)\s*Hz", body)
            if hm:
                a["hz"] = int(hm.group(1))
            km = re.search(r",\s*(\d+)\s*kb/s", body)
            if km:
                a["kbps"] = int(km.group(1))
            out["a"] = a
    return out if (out["v"] or out["a"]) else None


def probe_stream_facts(exe, fmt, timeout=12):
    """1.3.6:"""
    import subprocess
    url = str((fmt or {}).get("url") or "")
    if not exe or not url.lower().startswith(("http://", "https://")):
        return None
    cmd = [exe, "-hide_banner", "-nostdin", "-probesize", "3000000", "-analyzeduration", "3000000"]
    hd = (fmt or {}).get("http_headers")
    if isinstance(hd, dict) and hd:
        cmd += ["-headers", "".join(f"{k}: {v}\r\n" for k, v in hd.items())]
    cmd += ["-i", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        return parse_ffmpeg_facts(r.stderr)
    except Exception as _ign:
        ignore("probe_stream_facts", _ign)
        return None


def stream_needs_probe(info, kinds):
    """1.3.6: ¿falta algo que la escena enseña (resolución, códec, bitrate) en lo que yt-dlp informó de este stream? Pura."""
    info = info or {}

    def real(c):
        return bool(c) and str(c).lower() not in ("none", "unknown", "?")
    if "video" in kinds and not (real(info.get("vcodec")) and info.get("height") and (info.get("vbr") or info.get("tbr"))):
        return True
    if "audio" in kinds and not (real(info.get("acodec")) and (info.get("abr") or info.get("tbr"))):
        return True
    return False


# ── 1.2.5: revisar el archivo descargado antes de convertir ──
REAL_VCODECS = ("h264", "hevc")                                         # nombres de ffprobe que Apple reproduce en mp4/m4v/mov
REAL_ACODECS = ("aac", "alac", "mp3", "ac3", "eac3")                    # audio que cabe en mp4/m4v/mov y Apple reproduce
REAL_FMT_VIDEO, REAL_FMT_AUDIO = ("mp4", "mov"), ("mp4", "mov", "mp3", "wav", "flac", "aiff", "caf", "aac")


def parse_ffmpeg_media(text):
    """Salida de «ffmpeg -i» → {"v": {codec, tag} | None, "a": [códecs], "fmt": «mov,mp4,m4a,3gp,3g2,mj2» | None}."""
    text = text or ""
    fm = re.search(r"Input #0,\s*(.+?),\s*from\b", text)
    out = {"v": None, "a": [], "fmt": fm.group(1).strip() if fm else None}
    for ln in text.splitlines():
        if "Video:" in ln and out["v"] is None and "attached pic" not in ln:
            body = ln.split("Video:", 1)[1]
            m = re.match(r"\s*(\w+)", body)
            tg = re.search(r"\((\w{4}) / 0x", body)
            if m:
                out["v"] = {"codec": m.group(1).lower(), "tag": tg.group(1).lower() if tg else None}
        elif "Audio:" in ln:
            m = re.match(r"\s*(\w+)", ln.split("Audio:", 1)[1])
            if m:
                out["a"].append(m.group(1).lower())
    return out


def probe_file(exe, path, timeout=20):
    """Lee el archivo descargado:"""
    import subprocess
    exe = exe or shutil.which("ffmpeg")
    cands = []
    if exe:
        d, n = os.path.split(exe)
        cands.append(os.path.join(d, n.lower().replace("ffmpeg", "ffprobe")) if d else None)
    cands.append(shutil.which("ffprobe"))
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    for pr in dict.fromkeys(c for c in cands if c):
        with quiet("probe_file ffprobe"):
            r = subprocess.run([pr, "-v", "error", "-show_entries", "stream=codec_type,codec_name,codec_tag_string,disposition:format=format_name",
                                "-of", "json", "file:" + path], capture_output=True, text=True, timeout=timeout)
            j = json.loads(r.stdout or "{}")
            sts, fmt = j.get("streams") or [], (j.get("format") or {}).get("format_name")
            if sts or fmt:
                out = {"v": None, "a": [], "fmt": fmt, "ext": ext}
                for s in sts:
                    if s.get("codec_type") == "audio":
                        out["a"].append(str(s.get("codec_name") or "?").lower())
                    elif s.get("codec_type") == "video" and out["v"] is None and not (s.get("disposition") or {}).get("attached_pic"):
                        out["v"] = {"codec": str(s.get("codec_name") or "?").lower(), "tag": str(s.get("codec_tag_string") or "").lower() or None}
                return out
    if exe:
        with quiet("probe_file ffmpeg"):
            r = subprocess.run([exe, "-hide_banner", "-i", "file:" + path], capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
            out = parse_ffmpeg_media(r.stderr)
            if out["v"] or out["a"] or out["fmt"]:
                out["ext"] = ext
                return out
    return None


def real_container_ok(real, video):
    """¿El contenedor real (extensión y, si se leyó, formato) es de los que Apple abre para video (mp4/m4v/mov) o audio?"""
    ext = (real or {}).get("ext") or ""
    names = {x.strip() for x in str((real or {}).get("fmt") or "").split(",") if x.strip()}
    ok_ext = ext in (APPLE_VEXT if video else APPLE_AEXT)
    ok_fmt = bool(names & set(REAL_FMT_VIDEO if video else REAL_FMT_AUDIO)) if names else True
    return ok_ext and ok_fmt


def real_audio_ok(codec, video):
    c = str(codec or "").lower()
    return c in REAL_ACODECS or (not video and (c == "flac" or c.startswith("pcm_")))


def refine_plan(plan, real):
    """Ajusta `plan` (lo que se predijo con los datos del sitio)"""
    video = plan.get("vsrc") is not None
    if not real or (video and not real.get("v")) or (not video and not real.get("a")):
        return plan, [], None
    forced = bool(plan.get("remux_forced"))                          # el usuario pidió remux: el video no se recodifica pase lo que pase
    vc = ((real.get("v") or {}).get("codec") or "") if video else ""
    tag = (real.get("v") or {}).get("tag") if video else None
    venc = video and not forced and vc not in REAL_VCODECS
    retag = video and vc == "hevc" and tag == "hev1"                 # HEVC con etiqueta que Apple no abre: basta un remux con hvc1
    auds = list(real.get("a") or [])
    aenc = [not real_audio_ok(c, video) for c in auds]
    cont_ok = real_container_ok(real, video)
    items = []
    if video:
        items.append((codec_name(vc) or vc or "?", venc or retag))
    items.append((codec_name(auds[0]) or auds[0] if auds else "—", any(aenc)))
    items.append(((real.get("ext") or "?"), not cont_ok))
    if not (venc or any(aenc) or retag or not cont_ok):
        return None, ["ya compatible"], items
    new = dict(plan)
    changes = []

    def put(k, v):
        if new.get(k) != v:
            changes.append(f"{k}: {new.get(k)!r} → {v!r}")
            new[k] = v
    put("venc", venc)
    put("aenc", aenc)
    put("remux", retag or not cont_ok)
    put("cur", real.get("ext") or plan.get("cur"))
    if video:
        put("vsrc", _short(vc))
        put("hvc", (not venc) and vc == "hevc")
    put("asrc", [_short(c) for c in auds])
    if new.get("labels") and len(new["labels"]) > len(auds):
        put("labels", list(new["labels"])[:len(auds)])
    if not venc:
        new.pop("ask_enter", None)                                   # sin recodificar video no hay conversión larga que preguntar
    return new, changes, items


def check_download(pp, path, plan):
    """1.2.5:"""
    scene_check()
    try:
        real = probe_file(getattr(pp, "executable", None), path)
    except Exception as _ign:
        ignore("check_download", _ign)
        real = None
    new, changes, items = refine_plan(plan, real)
    dbg("revisión del archivo", {"real": real, "cambios": changes})
    if items is None:
        scene_check_end()
        m_info("No se pudo leer el archivo: se sigue el plan de conversión de antes.")
        return True
    scene_wait_anim("check", 1.1)                                    # 1.5.5: el haz termina su recorrido (wait) · N s (segundos) · nada (real)
    if new is None:
        scene_check(items, "ok")
        m_ok("El archivo descargado ya es compatible con Apple: se guarda sin convertir.")
        scene_wait_anim("check", 1.0)                                # 1.5.5: el pulso verde termina su ciclo y sigue el proceso
        scene_check_end()
        return False
    scene_check(items, "conv")
    plan.clear()
    plan.update(new)
    if changes:
        m_info("Revisado el archivo real: " + plan_summary(plan))
    scene_wait_anim("check", 0.9)                                    # 1.5.5: idem con el pulso ámbar
    scene_check_end()
    return True


def conversion_bits(plan, used, probed):
    """Bits del video convertido:"""
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
    parts += ["HDR conservado"] if plan.get("hdr_mode") == "keep" else ["HDR → SDR"] if plan.get("hdr_mode") == "tonemap" else []
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
    """Convierte path → out_path probando los encoders en orden."""
    root, ext = os.path.splitext(out_path)
    tmp = root + ".apple" + ext
    exe = getattr(pp, "executable", None)
    for _k in ("hdr_kind", "hdr_mode"):
        plan.pop(_k, None)
    if plan.get("venc") and plan.get("vsrc") is not None:
        real = probe_video(exe, path)                                 # se lee el archivo: bits y color (HDR) reales
        rb = (real or {}).get("bits")
        if rb and not plan.get("bits"):                               # nunca se pudo saber antes
            plan["bits"] = rb
            keep = min(encode_bits(rb), 10)
            if rb > 8:
                plan["out_bits"] = keep
                m_info(f"El archivo descargado es de {rb} bits: se conservan"
                       + (f" como {keep} bits (lo máximo que reproduce Apple)." if keep != rb else "."))
        hdr_prepare(plan, real, exe)
    err, used, ok = None, None, False
    t_start = time.time()
    plan.pop("engine", None)

    def run_sets(vsets):
        nonlocal err, used, ok
        prev_name = None
        for vcodec, name, vopts in vsets:
            try:
                aopts = apple_ffmpeg_opts(plan, vopts)
                dbg("intento de conversión", {"video": vcodec, "name": name, "opciones": aopts})
                if prev_name:
                    m_warn(f"{prev_name} no disponible; probando {name}")
                m_info(f"Usando {name}")
                if vcodec is None and not plan.get("venc") and plan.get("vsrc") is not None:
                    bar_label, scene_codec = "Remux", "REMUX"
                    scene_from, scene_to = plan.get("cur"), plan.get("ext")            # WEBM → MP4
                elif vcodec is None:
                    bar_label, scene_codec = "Convirtiendo · audio", "AAC"
                    afrom = [x for x, e in zip(plan.get("asrc") or [], plan.get("aenc") or []) if e] or (plan.get("asrc") or [])
                    scene_from, scene_to = (codec_name(afrom[0]) if afrom else None), "AAC"
                else:
                    ob = plan.get("out_bits")
                    cname = codec_name(vcodec) or "video"
                    bar_label = "Convirtiendo · " + cname + (f" {ob} bits" if ob and ob > 8 else "")
                    scene_codec = cname
                    scene_from, scene_to = codec_name(plan.get("vsrc")), cname
                scene_convert(scene_codec, ("Convirtiendo · " + name.split()[0]) if vcodec is not None else bar_label, scene_from, scene_to)
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

    if plan.get("vsrc") is not None:
        vsets = video_encoder_attempts(plan)
    else:
        vsets = [(None, "AAC (audio)", [])]
    run_sets(vsets)
    if not ok and plan.get("hdr_mode") == "tonemap":                  # 1.2.1: sin tone mapping que valga, el HDR se conserva
        m_warn("El tone mapping no funcionó: se conserva el HDR en 10 bits.")
        plan["hdr_mode"], plan["out_bits"] = "keep", 10
        run_sets(video_encoder_attempts(plan))
    scene_convert_end()
    if not ok:
        raise RuntimeError(str(err))
    plan["result"] = (probe_video(exe, tmp) if plan.get("vsrc") is not None else None)
    dbg("video convertido", plan["result"])
    plan["secs"] = int(round(time.time() - t_start))
    with quiet("apple_convert_file", TypeError, ValueError):                                  # velocidad real para estimar las próximas (solo con recodificación)
        real_t = time.time() - t_start
        if plan.get("venc") and dur and float(dur) > 0 and real_t >= 3:
            plan["speed"] = round(float(dur) * conv_scale(plan) / real_t, 2)
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


def convert_confirmed(plan):
    """1.1.2:"""
    est = plan.pop("ask_enter", None)
    if est is None or not plan.get("venc"):
        return True
    try:
        ok = scene_ask_enter(est, src=codec_name(plan.get("vsrc")) or plan.get("cur"), dst="HEVC")
    except EOFError:
        ok = False
    if ok == "r":
        plan["venc"] = False
        plan["remux_forced"] = True
        plan["asked_bits"] = False
        m_info("Remux: se cambia el contenedor y el audio; el video no se recodifica.")
        return True
    if ok is False:
        m_info("Se conserva el original: el archivo se guarda sin convertir.")
        return False
    return True


def replace_confirmed():
    """1.4.2: «¿Descargar de nuevo?» dentro de la escena (como la de convertir): True = sustituir, False = conservar el que ya tienes,
    None = no hay escena o el terminal no admite teclas sueltas (se hace la pregunta de siempre)."""
    try:
        return scene_ask_enter(src="VIEJO", dst="NUEVO", kind="replace")
    except EOFError:
        return False


def make_apple_pp(plan, state, bar=None):
    from yt_dlp.postprocessor import FFmpegPostProcessor

    class AppleConvertPP(FFmpegPostProcessor):
        def run(self, info):
            path = info.get("filepath")
            if not path or not os.path.exists(path):
                return [], info
            ext = plan["ext"]
            dest = os.path.splitext(path)[0] + "." + ext
            if not check_download(self, path, plan):        # 1.2.5: se lee el archivo real; si ya es compatible no se convierte
                return [], info
            if not convert_confirmed(plan):                 # 1.1.2: la escena pide Enter justo antes de convertir
                return [], info
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
        with quiet("__init__"):
            from yt_dlp.postprocessor import FFmpegPostProcessor
            exe = getattr(FFmpegPostProcessor(), "executable", None)
        self.executable = exe or shutil.which("ffmpeg") or "ffmpeg"

    def run_ffmpeg(self, *a, **k):
        raise RuntimeError("no se pudo lanzar ffmpeg")


# ───────────────────── [D4] Ya descargado: reutilizar o convertir ─────────────────────
def reuse_downloaded(old_file, old_entry, index, key, title, info, kind, fmt, fmt_id,
                     selected, orig_ids, plan):
    """Aprovecha el archivo ya descargado."""
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
        if SCENE["on"]:                                              # 1.4.2: con la escena viva se contesta en ella (Enter sustituye · n conserva)
            ans = replace_confirmed()
            if ans is not None:
                if ans:
                    m_info("Se descargará de nuevo.")
                    return False
                m_ok("Se reutiliza el archivo ya descargado.")
                deliver_existing(old_file, old_entry, title)
                return True
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

    final = os.path.join(FILES_DIR, os.path.basename(out))
    try:
        move_file(out, final)
        if os.path.abspath(final) != os.path.abspath(old_file):
            os.remove(old_file)
        drop_deliveries(os.path.basename(old_file))     # su entrega anterior (sin convertir) ya no vale
        drop_deliveries(os.path.basename(final))
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
    """Pregunta si conservar los bits originales (origen de más de 8 bits)"""
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
    choices = bits_choices(bits, hdr)
    low = (f"Puede verse con bandas; el {hdr} se pasa a SDR con tone mapping (tarda ~3 veces más) y pierde el brillo extra del HDR."
           if hdr else "Puede verse con bandas en cielos y degradados.")
    if len(choices) == 2:                       # 9 o 10 bits: sí / no
        keep = choices[0][0]
        note(f"Conservar {keep} bits: degradados suaves"
             + (f" y se mantiene el {hdr}" if hdr else "")
             + "; los dispositivos Apple recientes lo reproducen bien. Tarda más"
             + (f" (un origen de {bits} bits se guarda como {keep})." if bits != keep else "."))
        note(f"A 8 bits: {'SDR' if hdr else 'más rápido'}, pero pierde precisión de color. {low}")
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
    m_info((f"Se convertirá a SDR de {ob} bits con tone mapping." if hdr and ob <= 8 else f"Se convertirá a {ob} bits.") if ob != bits
           else f"Se conservarán {ob} bits.")
    return plan


def ask_apple_convert(plan, can_merge, duration=None, fmt=None):
    """Avisa de que no es nativo en Apple y pregunta (o convierte solo si es rápido:"""
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
            r = None
            ask_scene = bool(SCENE["on"] and plan.get("venc") and est is not None and countdown_supported())   # 1.1.1: conversión que se sabe que tarda
            if ask_scene:                                              # 1.1.2: el Enter se pide justo antes de convertir (convert_confirmed)
                plan["ask_enter"] = est
                m_info(f"Conversión larga (~{int(round(est))} s): la escena preguntará justo antes de convertir (Enter convertir · r remux · n conservar original).")
                r = True
            else:
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


def video_key(info):
    ext = info.get("extractor_key") or info.get("extractor") or "generic"
    vid = info.get("id") or info.get("webpage_url") or ""
    return f"{ext}:{vid}"


def find_saved(name):
    """Ruta de un archivo ya descargado (por nombre del índice) o None."""
    p = os.path.join(FILES_DIR, name)
    return p if os.path.isfile(p) else None


def history_for(key, index=None, hist_data=None):
    """[(ruta, entrada)] de TODO lo descargado de ese video que sigue en disco."""
    out, seen = [], set()
    entries = list((load_json(HISTORY_FILE) if hist_data is None else hist_data).get(key) or [])
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
    """Anota una descarga terminada en downloads.json."""
    with quiet("history_add"):
        data = load_json(HISTORY_FILE)
        keep = [e for e in (data.get(key) or [])
                if isinstance(e, dict) and e.get("file") and e["file"] != entry.get("file") and find_saved(e["file"])]
        keep.append(entry)
        data[key] = keep
        save_json(HISTORY_FILE, data)


def conv_mode(meta, plan=None):
    """'' sin conversión · 'remux' (pedido con «r», video sin recodificar) · 'full' conversión normal."""
    if plan is not None:
        return "remux" if plan.get("remux_forced") else ("full" if plan else "")
    if not (meta or {}).get("converted"):
        return ""
    return "remux" if ((meta.get("conv") or {}).get("forced")) else "full"


def history_match(hist, fmt_id, want_conv=None):
    """(ruta, entrada)"""
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
                "codec": acodec_short(f),
                "abr": round(abr_of(f)), "original": t["original"],
                "default": i == 0, "apple": apple_audio(f)})
    elif has(fmt.get("acodec")):
        meta["tracks"].append({
            "lang": fmt.get("language") or "und",
            "label": fmt.get("language") or "audio",
            "codec": acodec_short(fmt),
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
    """Filas «etiqueta valor»"""
    w = term_width()
    lw = max((len(l) for l, _ in rows), default=0)
    for label, value in rows:
        lines = wrap_text(str(value), max(8, w - lw - 3))
        print("  " + paint(label.ljust(lw), "gray") + " " + lines[0])
        for ln in lines[1:]:
            print(" " * (lw + 3) + ln)


def audio_rows(tracks, room=None):
    """Filas de audio:"""
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
    """Orden que imprime el portapapeles, o None."""
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
    """Copia `text` al portapapeles (pbcopy)."""
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
        with quiet("shortcut_copy", OSError):
            os.remove(tmp)


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
    with quiet("refresh_paths"):
        cands.append(site.getusersitepackages())
    cands += glob.glob(os.path.join(HOME, "Library", "lib", "python*", "site-packages"))
    cands += glob.glob(os.path.join(HOME, ".local", "lib", "python*", "site-packages"))
    for c in cands:
        if c and os.path.isdir(c) and c not in sys.path:
            site.addsitedir(c)


INSTALLED_OK = set()                   # módulos ya vistos instalados en esta ejecución (0.6.6)


def is_installed(module, fresh=False):
    """¿Se puede importar `module`?"""
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


NET = {}          # 1.4.4: lo último que hizo cada operación de las fases de actualización: clave → {ok, secs, code, val, err}. La escena D L P Y lo enseña.
GH_LAST = {"code": None, "err": None}     # 1.4.4: respuesta de la última página de /releases (código HTTP o causa del fallo)


def net_err_text(e):
    """1.4.4: la causa de un fallo de red en pocas palabras («timeout», «sin red», «HTTP 403»…)."""
    import socket
    import urllib.error
    if isinstance(e, urllib.error.HTTPError):
        return f"HTTP {e.code}"
    reason = getattr(e, "reason", e)
    if isinstance(e, (socket.timeout, TimeoutError)) or isinstance(reason, (socket.timeout, TimeoutError)) or "timed out" in str(reason).lower():
        return "timeout"
    if isinstance(e, urllib.error.URLError):
        return "sin red"
    if isinstance(e, ValueError):
        return "respuesta inválida"
    return type(e).__name__


def net_set(key, t0, ok, code=None, val=None, err=None):
    NET[key] = {"ok": bool(ok), "secs": max(0.0, time.time() - t0), "code": code, "val": val, "err": err}


def latest_version(pip_name, timeout=6):
    import urllib.request
    t0 = time.time()
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{pip_name}/json", timeout=timeout) as r:
            code = getattr(r, "status", None) or r.getcode()
            ver = json.load(r)["info"]["version"]
        net_set(pip_name, t0, True, code, ver)
        return ver
    except Exception as _ign:
        ignore("latest_version", _ign)
        net_set(pip_name, t0, False, err=net_err_text(_ign))
        return None


def vtuple(v):
    """Tupla numérica de una versión, rellenada a tres números («1.0» = «1.0.0»); () si no hay números."""
    t = tuple(int(x) for x in re.findall(r"\d+", v or ""))
    return t + (0,) * (3 - len(t)) if t else t


DOWNGRADE_CAUSES = ("manual", "recuperacion", "externa")
DOWNGRADE_DELIBERATE = ("manual", "recuperacion")     # bajadas hechas a propósito desde DLpy


def version_move(stored, current):
    """Cambio entre la última versión que corrió (`stored`)"""
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
    with quiet("gh_notice"):
        m_info(f"Conectando a GitHub · {what}")


def fresh_bytes(url, timeout=5, limit=None):
    """Bytes de `url` sin pasar por cachés."""
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
        with quiet("fresh_bytes"):
            with urllib.request.urlopen(urllib.request.Request(u, headers=headers),
                                        timeout=timeout) as r:
                raw = r.read(limit + 1)
            if len(raw) <= limit:
                return raw
    return None


RELEASE_HASH = {}                     # url del script → {"sha_url", "digest", "body"}: lo que publica su Release (lo llena parse_releases)
VERIFY = {}                           # url del script → "ok" | "none" | "bad" | "off": resultado de la última verificación
SHA_HEX_RE = re.compile(r"\b([0-9a-fA-F]{64})\b")
SHA_BODY_RE = re.compile(r"(?is)sha-?256.{0,300}?\b([0-9a-f]{64})\b")


def release_hash_info(item, asset_name=None):
    """Hash que publica un Release (`item` = su JSON de la API)"""
    out = {}
    assets = [a for a in (item.get("assets") or []) if isinstance(a, dict)]
    want = (asset_name or "dlpy.py") + ".sha256"
    for a in assets:
        if str(a.get("name") or "") == want and a.get("browser_download_url"):
            out["sha_url"] = str(a["browser_download_url"])
        if asset_name and a.get("name") == asset_name:
            d = str(a.get("digest") or "").lower()
            if d.startswith("sha256:") and re.fullmatch(r"[0-9a-f]{64}", d[7:]):
                out["digest"] = d[7:]
    m = SHA_BODY_RE.search(str(item.get("body") or ""))
    if m:
        out["body"] = m.group(1).lower()
    return out


def published_sha(url, timeout=5):
    """(SHA-256 que publica el Release de `url`, fuente)"""
    info = RELEASE_HASH.get(url) or {}
    if info.get("sha_url"):
        raw = fresh_bytes(info["sha_url"], timeout, limit=4096)
        m = SHA_HEX_RE.search(raw.decode("utf-8", "replace")) if raw else None
        if m:
            return m.group(1).lower(), "adjunto .sha256"
    if info.get("digest"):
        return info["digest"], "digest de GitHub"
    if info.get("body"):
        return info["body"], "notas del Release"
    return None, None


def verify_download(url, raw, timeout=5):
    """Compara el SHA-256 de los bytes descargados con el que publica el Release."""
    import hashlib
    if (os.environ.get("DLPY_NOVERIFY") or "").strip().lower() not in ("", "0", "no", "false"):
        VERIFY[url] = "off"
        return "off"
    want, src = published_sha(url, timeout)
    if not want:
        VERIFY[url] = "none"
        return "none"
    got = hashlib.sha256(raw).hexdigest()
    if got == want:
        VERIFY[url] = "ok"
        return "ok"
    VERIFY[url] = "bad"
    dbg("SHA-256 no coincide", f"{url} · {src}")
    m_err("SHA-256 no coincide: el archivo descargado no es el que publicó el Release; no se instala.")
    note(f"Esperado ({src}): {want}")
    note(f"Obtenido: {got}")
    return "bad"


def fetch_remote_script(timeout=5, url=None):
    """Texto del dlpy.py de `url` (el de un Release), o None si falla, no es un script válido o su SHA-256 no coincide."""
    if not url:
        return None
    try:
        raw = fresh_bytes(url, timeout)
        if raw is None:
            return None
        if verify_download(url, raw, timeout) == "bad":
            return None
        text = raw.decode("utf-8").replace("\r\n", "\n")
        if not remote_script_version(text):
            return None
        compile(text, "dlpy.py", "exec")          # descarga truncada o dañada
        return text
    except Exception as _ign:
        ignore("fetch_remote_script", _ign)
        return None


NO_UPDATES = {"on": False}            # --noupdates / --no-updates / DLPY_UPDATES=0: esta ejecución no busca nada (ni el script ni sus dependencias)
LATE_UPDATES = {"on": False, "done": False}   # --shortcutpick: se busca al terminar la descarga
RELEASE_SAME = {"igual": False}       # ¿la instalada es idéntica al último Release? (lo fija check_update)
RELEASES = {"list": None}             # Releases leídos en esta ejecución (los guarda remote_releases): de ahí sale changelog.md
UPDATE_CHECKED = {"ok": False}        # ¿llegó a comprobarse la última versión (hubo red)?

# Búsqueda de actualizaciones (1.4.4: UNA sola variable, DLPY_UPDATES, para el script y para sus dependencias): fecha de la última
# comprobación por clave («script» = DLpy en GitHub, «deps» = pip / yt-dlp / yt-dlp-ejs) en state/checks.json.
UPDATES_ALWAYS = -1.0                 # valor interno de «on» (en cada arranque)
UPDATES_DEFAULT = 1.0                 # 1.5.2: predeterminado: una vez al día (24 h)


def parse_updates(raw):
    """1.5.2: DLPY_UPDATES: «on» (o «siempre», «always») = -1, en cada arranque · un número = la espera en DÍAS (0 u «off» = nunca) · vacío, negativo o
    texto raro = 1 día (el predeterminado)."""
    t = str(raw or "").strip().lower().replace(",", ".")
    if t in ("on", "siempre", "always", "s", "a"):
        return UPDATES_ALWAYS
    if t in ("off", "nunca", "never", "no"):
        return 0.0
    try:
        v = float(t)
    except ValueError:
        return UPDATES_DEFAULT
    return v if math.isfinite(v) and v >= 0 else UPDATES_DEFAULT


def _updates_from_env():
    """DLPY_UPDATES; sin ella, las dos variables de la 1.4.3 (DLPY_NO_UPDATE → nunca · DLPY_CHECK_HOURS → horas / 24) para no cambiar a nadie el comportamiento."""
    raw = os.environ.get("DLPY_UPDATES")
    if raw is not None and raw.strip():
        return parse_updates(raw)
    if (os.environ.get("DLPY_NO_UPDATE") or "").strip():
        return 0.0
    hours = _env_num("DLPY_CHECK_HOURS", -1.0, minimum=float("-inf"))
    return hours / 24.0 if hours > 0 else UPDATES_DEFAULT


UPDATE_DAYS = _updates_from_env()


def update_every_text(days=None):
    """Cada cuánto se busca, en palabras («en cada arranque», «cada día», «cada 3 días», «nunca»)."""
    d = UPDATE_DAYS if days is None else days
    return "en cada arranque" if d < 0 else "nunca" if d == 0 else "cada día" if d == 1 else f"cada {d:g} días"


def due_from(rec, sig=None, now=None, hours=None):
    """¿Toca comprobar?"""
    now = time.time() if now is None else now
    if hours is None:                                   # 1.4.4: de DLPY_UPDATES (días): nunca → no toca · siempre → toca
        if UPDATE_DAYS == 0:
            return False
        hours = 0 if UPDATE_DAYS < 0 else UPDATE_DAYS * 24.0
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
    with quiet("check_mark"):
        d = load_json(CHECK_FILE)
        d[key] = {"t": int(time.time()), "sig": sig}
        save_json(CHECK_FILE, d)


def script_sig():
    """Firma de este dlpy.py:"""
    try:
        return f"{VERSION}:{int(os.path.getmtime(SCRIPT_PATH))}"
    except OSError as _ign:
        ignore("script_sig", _ign)
        return VERSION


def update_status(remote, local=None):
    """«nueva»"""
    r, l = vtuple(remote), vtuple(VERSION if local is None else local)
    return "nueva" if r > l else "igual" if r == l else "local"


def release_notes_lines(notes, width):
    """Líneas de los release notes (Markdown simplificado)"""
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
    """Imprime los release notes de `ver`."""
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
    """True = instalar, False = cancelar, «m»"""
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
    """Los changelog de TODOS los Releases de GitHub, del más nuevo al más viejo; marca el de `ver`, la versión que se va a instalar."""
    for i, r in enumerate(order_releases(rels)):
        if i:
            print()
        show_release_notes(r["ver"], r.get("notes"), r.get("date"),
                           unavailable="Este Release no trae release notes.",
                           tag="se instalará" if r["ver"] == ver else None)


def show_notes_on_apply(ver, notes, date=None, hidden=0, viewed=False, unavailable=None):
    """Justo antes de aplicar una versión:"""
    if hidden <= 0 or viewed:
        return
    with quiet("show_notes_on_apply"):
        hide_keyboard(0.3)
        clear_screen()
        header(f"CHANGELOG {ver} · se instalará", gap=False)
        shown = show_release_notes(ver, notes, date, unavailable=unavailable)
        time.sleep(2.0 + min(4.0, 0.04 * (hidden + max(0, shown))))


def confirm_install(msg, ver, notes, date=None, seconds=False, default=True, unavailable=None, all_rels=None):
    """Muestra los release notes de `ver` (solo los de la versión que se instalará)"""
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


def show_verify(url):
    """Una línea con el resultado de la verificación SHA-256 de la descarga de `url`."""
    st = VERIFY.get(url)
    if st == "ok":
        m_check("SHA-256 verificado")
    elif st == "none":
        note("Sin SHA-256: este Release no publica hash, no se pudo verificar la descarga.")
    elif st == "off":
        m_warn("SHA-256 sin verificar (DLPY_NOVERIFY=1)")


# ── Comprobaciones en paralelo (1.4.4) ──
# Al arrancar, las búsquedas de DLpy (GitHub) y de pip / yt-dlp (PyPI) salen A LA VEZ en hilos y el flujo recoge sus resultados;
# si todo está al día, la escena lo resume en una sola línea («Todo al día · 3 comprobaciones · 0.9 s») en vez de tres pasos con espera.
PREFETCH_MAX = 14.0           # s máximos de espera a que respondan todas
PREFETCH = {"on": False, "keys": [], "res": {}, "done": set(), "n": 0, "hosts": "", "t0": 0.0, "changed": False, "quiet_fail": False}


def _pf_work(key, fn):
    try:
        PREFETCH["res"][key] = fn()
    except Exception as e:
        ignore("prefetch " + key, e)
        PREFETCH["res"][key] = None
        net_set(key, PREFETCH["t0"], False, err=net_err_text(e))
    finally:
        PREFETCH["done"].add(key)


def prefetch_hosts(keys):
    """1.4.4: los servidores de las peticiones en paralelo, tal como los teclea la escena («pypi.org x2 · github.com»)."""
    pypi = sum(1 for k in keys if k != "DLpy")
    parts = ([("pypi.org" if pypi == 1 else f"pypi.org x{pypi}")] if pypi else []) + (["github.com"] if "DLpy" in keys else [])
    return " · ".join(parts)


def prefetch_phase(script_due, deps_due):
    """1.4.4: lanza a la vez las comprobaciones que toquen (DLpy, pip, yt-dlp) y espera a todas. False si no hay al menos dos
    (con una sola, el paso de siempre es igual de rápido)."""
    PREFETCH.update({"on": False, "keys": [], "res": {}, "done": set(), "n": 0, "hosts": "", "t0": 0.0, "changed": False, "quiet_fail": False})
    if NO_UPDATES["on"] or not (script_due or deps_due):
        return False
    jobs = []
    if script_due:
        jobs.append(("DLpy", lambda: fetch_latest_release(timeout=5)))
    if deps_due:
        for pip_name, module, _req in DEPENDENCIES:
            if is_installed(module):
                jobs.append((pip_name, lambda n=pip_name: latest_version(n)))
    if len(jobs) < 2:
        return False
    keys = [k for k, _fn in jobs]
    PREFETCH.update({"on": True, "keys": list(keys), "n": len(keys), "hosts": prefetch_hosts(keys), "t0": time.time()})
    for k, fn in jobs:
        threading.Thread(target=_pf_work, args=(k, fn), daemon=True).start()
    bar = None
    if not scene_note("Comprobando actualizaciones"):         # dentro de la escena el texto de estado hace de barra
        bar = Bar()
        bar.start("Comprobando actualizaciones")
    try:
        end = time.time() + PREFETCH_MAX
        while len(PREFETCH["done"]) < len(keys) and time.time() < end:
            time.sleep(0.02)
    finally:
        if bar:
            bar.stop()
    for k in keys:
        if k not in PREFETCH["done"]:                          # no respondió a tiempo: cuenta como fallo
            PREFETCH["res"][k] = None
            net_set(k, PREFETCH["t0"], False, err="timeout")
    bad = [k for k in keys if not (NET.get(k) or {}).get("ok")]
    net_set("check", PREFETCH["t0"], not bad, val=f"{len(keys)} GET", err=(f"{len(bad)} de {len(keys)} con error" if bad else None))
    if len(bad) == len(keys) and scene_note("No se pudo comprobar actualizaciones", SCENE_DWELL):
        PREFETCH["quiet_fail"] = True                          # ya se dijo una vez: los pasos de cada una no repiten el ✗
    return True


def prefetch_summary():
    """1.4.4: si todo salió bien y no hubo nada que actualizar, un solo resumen en la escena."""
    P = PREFETCH
    chk = NET.get("check") or {}
    if P["on"] and SCENE["on"] and chk.get("ok") and not P["changed"]:
        scene_note(f"Todo al día · {P['n']} comprobaciones · {chk['secs']:.1f} s", SCENE_DWELL)
    P["on"] = False


def check_update(force=False, late=False):
    """Si el último Release de GitHub es más nuevo, muestra sus release notes y, con Enter, lo instala y lo ejecuta."""
    pre = PREFETCH["on"] and "DLpy" in PREFETCH["keys"] and not force and not late      # 1.4.4: ya la pidió prefetch_phase, en paralelo
    if pre:
        PREFETCH["keys"].remove("DLpy")
        rel = PREFETCH["res"].get("DLpy")
    else:
        cbar = Bar()
        if not scene_note("Comprobando DLpy"):      # 0.9.4: dentro de la escena el texto de estado hace de barra
            cbar.start("Comprobando DLpy")
        try:
            rel = fetch_latest_release(timeout=8 if force else 5)      # la actualización sale solo de los Releases
        finally:
            cbar.stop()
    sync_changelog(fetch=False)                 # changelog.md ← release notes de los Releases recién leídos
    if not rel:
        if not PREFETCH["quiet_fail"]:
            scene_note("No se pudo comprobar DLpy", SCENE_DWELL)
        m_warn(f"DLpy {VERSION} · no se pudo comprobar la última versión (Releases de GitHub)")
        return False
    remote, text = rel["ver"], rel["text"]
    UPDATE_CHECKED["ok"] = True                # hubo respuesta: cuenta como comprobada
    status = update_status(remote)
    if status == "nueva":
        PREFETCH["changed"] = True
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
        if not pre:                              # 1.4.4: en paralelo, el resumen final lo dice por todos
            scene_note(f"DLpy {VERSION} · última versión", SCENE_DWELL)
        m_check(f"DLpy {VERSION} · última versión" + (" · idéntica al Release" if same == "igual" else ""))
        if same == "distinto":
            add, rem = diff_counts(diff_lines(text, mine, "Release", "instalada"))
            m_warn(f"{VERSION} · Release ≠ instalada (código distinto: -{rem} +{add} líneas)")
            note("Mismo número con código distinto: revisa cuál es el bueno.")
        return False
    if status == "local":
        if not pre:
            scene_note(f"DLpy {VERSION} · versión local", SCENE_DWELL)
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
        scene_note(f"Nueva versión de DLpy · {VERSION} → {remote}", SCENE_DWELL)
    if SCENE["on"]:
        kind = (crash_match(remote, text) or (None,))[0]     # dentro de la escena no se pintan avisos ni release notes
    else:
        show_verify(rel["url"])
        kind = show_crash_warning(remote, text)   # avisa si es idéntica a una que falló
    # a-Shell: esta pregunta va con input() normal (sin cbreak). Después la versión nueva corre en
    # este mismo proceso y cambiar el modo del terminal justo antes la congelaba.
    if SCENE["on"]:                            # 0.9.4: sin preguntas en la escena: la respuesta por omisión de siempre
        go = (kind != "igual")
        if not go:
            scene_note(f"DLpy {remote} · idéntica a la que falló", SCENE_DWELL)
    elif late:
        go = confirm_install(f"Instalar la {remote} para la próxima vez", remote, rel["notes"], rel["date"],
                             seconds=WAIT_SECONDS, default=(kind != "igual"))
    else:
        go = confirm_install(f"Instalar la {remote} y ejecutarla ahora", remote, rel["notes"], rel["date"],
                             default=(kind != "igual"))
    if not go:
        note(f"Se volverá a preguntar en la próxima comprobación ({update_every_text()}) o con --actualizar.")
        return False
    scene_note(f"Instalando DLpy {remote}", 0.5)
    _t_w = time.time()
    try:
        write_text(SCRIPT_PATH, text)
        net_set("write", _t_w, True)
    except Exception as e:
        net_set("write", _t_w, False, err=type(e).__name__)
        scene_note(f"No se pudo instalar DLpy {remote}", SCENE_DWELL)
        m_warn(f"No se pudo instalar la actualización: {e}")
        return False
    clear_recovered()
    scene_note(f"DLpy {remote} · instalada", SCENE_DWELL)
    m_check(f"DLpy {remote} · instalada")
    if late:
        m_info(f"Se usará la {remote} la próxima vez que abras DLpy.")
        return False
    reexec_script()                                    # termina con SystemExit
    return True


def late_updates():
    """Con --shortcutpick las actualizaciones no se buscan al abrir sino aquí, tras la descarga y justo antes de entregar el archivo."""
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


def pip_cmd(args):
    """1.3.3: el comando de pip tal como se lanza (con argumentos entrecomillados). pip_run lo ejecuta y la escena D L P Y lo teclea: es el mismo."""
    return "pip " + " ".join(shlex.quote(a) for a in args)


_ANSI_PIP = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


def pip_line_clean(raw):
    """1.4.4: una línea de la salida de pip lista para la escena: sin colores ni barras de progreso, en una sola línea corta."""
    t = _ANSI_PIP.sub("", str(raw or "")).replace("\r", " ")
    t = "".join(ch for ch in t if ch.isprintable() and ch not in "━╸╺─█▏▎▍▌▋▊▉")
    return " ".join(t.split())[:90]


def _pip_tail(log, stop):
    """1.4.4: mientras pip corre, deja en SCENE["pip_line"] la última línea que escribió (Collecting…, Downloading…, Installing…)."""
    while not stop.is_set():
        with quiet("pip_tail", OSError, ValueError):
            with open(log, "rb") as fh:
                fh.seek(0, os.SEEK_END)
                fh.seek(max(0, fh.tell() - 600))
                lines = [pip_line_clean(x) for x in fh.read().decode("utf-8", "replace").replace("\r", "\n").split("\n")]
            lines = [x for x in lines if x]
            if lines:
                SCENE["pip_line"] = lines[-1]
        stop.wait(0.2)


def pip_run(args):
    """Lanza pip con `args`."""
    cmd = pip_cmd(args)
    pkg = next((a for a in args if a != "install" and not a.startswith("-")), "pip").split("==", 1)[0]
    t0 = time.time()
    if SCENE["on"]:
        SCENE["cmd"] = cmd                  # 1.2.6: el comando que corre (1.3.3: la escena teclea el mismo, de pip_cmd(pip_args(…)))
    if SCENE["on"] and SCENE_PIP:           # 0.9.4: dentro de la escena pip escribe a un archivo para no pisarla
        log = os.path.join(STATE_DIR, "pip_scene.log")
        stop = threading.Event()
        with quiet("pip_run escena"):
            if os.path.exists(log):
                os.remove(log)
            threading.Thread(target=_pip_tail, args=(log, stop), daemon=True).start()     # 1.4.4: la última línea de pip se ve en la escena
            try:
                rc = os.system(cmd + " > " + shlex.quote(log) + " 2>&1")
            finally:
                stop.set()
                SCENE["pip_line"] = None
            net_set("pip:" + pkg, t0, rc == 0, val=None, err=None if rc == 0 else f"pip falló ({rc >> 8 if rc > 255 else rc})")
            if os.path.exists(log):
                with quiet("pip_run log", OSError, ValueError):
                    dbg("pip (escena)", read_text(log)[-400:])
                    os.remove(log)
                return rc
    scene_stop(clear=True)                  # 0.9.3: pip escribe directo en el terminal: la escena cede
    rc = os.system(cmd)
    net_set("pip:" + pkg, t0, rc == 0, err=None if rc == 0 else f"pip falló ({rc >> 8 if rc > 255 else rc})")
    return rc


def pip_install(pip_name):
    """Instala/actualiza `pip_name`."""
    m_info(f"Instalando {pip_name}...")
    PREFETCH["changed"] = True
    if SCENE["on"] and pip_name.split("==", 1)[0].lower() not in str(SCENE.get("label") or "").lower():
        scene_note(f"Instalando {pip_name}")   # 1.3.3: la escena habla de lo que corre de verdad (--scb instalaba yt-dlp con otro texto)
    try:
        rc = pip_run(pip_args(pip_name))
    except Exception as e:
        ignore("pip_install", e)
        m_warn(f"No se pudo lanzar pip para {pip_name}: {type(e).__name__}")
        return False
    finally:
        SCENE.pop("cmd", None)                          # 1.2.6: terminó: la escena vuelve a sus comandos de muestra
        refresh_paths()
    if rc != 0:
        code = rc >> 8 if rc > 255 else rc             # os.system puede devolver el estado de espera (código × 256)
        dbg("pip_install falló", {"paquete": pip_name, "codigo": code})
        m_warn(f"pip terminó con error (código {code}) al instalar {pip_name}.")
        return False
    return True


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
    """Banderas de yt-dlp para usar el runtime disponible."""
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
    """Requisito exacto de yt-dlp-ejs que declara el yt-dlp instalado."""
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
    """Si hay runtime de JavaScript, deja instalado yt-dlp-ejs en la versión que pide yt-dlp."""
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
    with quiet("declined_set"):
        save_json(DEPS_STATE_FILE, d)


def declined_clear(key):
    d = load_json(DEPS_STATE_FILE)
    if key not in d:
        return
    d.pop(key)
    with quiet("declined_clear"):
        save_json(DEPS_STATE_FILE, d)


def check_dependencies(force=False, updates=True, late=False):
    """Revisa instalación y actualizaciones; cada cosa deja una línea ✓/●."""
    # updates=False (--noupdates o descarga de atajo): solo comprueba que estén instaladas.
    # late=True: pregunta con Sí por omisión (0.6.6), no apunta rechazos
    # permanentes y no toca los paquetes del sistema ni yt-dlp-ejs (eso lo hace una ejecución normal).
    key = "deps_late" if late else "deps"
    due = updates and (force or check_due(key))
    net_ok = True
    for pip_name, module, required in DEPENDENCIES:
        if not is_installed(module):
            if SCENE["on"]:                              # 1.1.5: sin preguntas en la escena (Sí por omisión): se instala dentro de ella
                scene_note(f"Instalando {pip_name}")
                wanted = True
            else:
                scene_stop(clear=True)                   # 0.9.4: esto sí hay que preguntarlo: la escena cede
                m_warn(f"Falta la dependencia: {pip_name}" + (" (obligatoria)" if required else ""))
                wanted = ask(f"¿Instalar {pip_name}? (S/n) ▸ ", seconds=WAIT_SECONDS)
            if wanted:
                pip_install(pip_name)
            if not is_installed(module):
                if wanted:
                    scene_note(f"No se pudo instalar {pip_name}", SCENE_DWELL)     # 1.3.3: ✗ en la escena (sin escena no hace nada)
                if required:
                    if wanted:
                        m_err(f"No se detectó {pip_name} tras instalarlo.")
                        m_info("Si pip indicó éxito, vuelve a ejecutar DLpy; si no: pip install " + pip_name)
                    else:
                        m_err(f"{pip_name} es obligatoria: sin ella DLpy no puede continuar.")
                        m_info("Instálala con: pip install " + pip_name)
                    return False
                continue
            scene_note(f"{pip_name} {pkg_version(pip_name) or ''} · instalado".replace("  ", " "), SCENE_DWELL)     # 1.3.3: ✓ en la escena
            m_check(f"{pip_name} {pkg_version(pip_name) or ''} · instalado".replace("  ", " "))
            continue

        if not due:
            continue
        cur = pkg_version(pip_name)
        pre = PREFETCH["on"] and pip_name in PREFETCH["keys"] and not late      # 1.4.4: ya la pidió prefetch_phase, en paralelo
        if pre:
            PREFETCH["keys"].remove(pip_name)
            lat = PREFETCH["res"].get(pip_name)
        else:
            cbar = Bar()
            if not scene_note(f"Comprobando {pip_name}"):    # 0.9.4: dentro de la escena el texto de estado hace de barra
                cbar.start(f"Comprobando {pip_name}")
            try:
                lat = latest_version(pip_name)
            finally:
                cbar.stop()
        if cur and lat and vtuple(lat) > vtuple(cur):
            PREFETCH["changed"] = True
            if not force and load_json(DEPS_STATE_FILE).get(pip_name) == lat:
                m_warn(f"{pip_name} {cur} · hay una {lat} (rechazada; --actualizar la instala)")
            else:
                m_info(f"Actualización de {pip_name}: {cur} → {lat}")
                if scene_note(f"Actualizando {pip_name} → {lat}", 0.5):     # sin preguntas en la escena: Sí por omisión
                    wanted = True
                else:
                    wanted = ask(f"¿Actualizar {pip_name}? (S/n) ▸ ", default=True, seconds=WAIT_SECONDS)
                if wanted:
                    done = pip_install(pip_name)
                    if SCENE["on"]:
                        scene_note(f"{pip_name} {pkg_version(pip_name) or '?'} · actualizada" if done
                                   else f"No se pudo actualizar {pip_name}", SCENE_DWELL)
                    m_check(f"{pip_name} {pkg_version(pip_name) or '?'} · actualizada")
                    declined_clear(pip_name)
                elif late:
                    note(f"Se volverá a preguntar en la próxima comprobación ({update_every_text()}) o con --actualizar.")
                else:
                    declined_set(pip_name, lat)
                    note("No se vuelve a preguntar por esta versión; con --actualizar la instalas.")
        elif cur and lat:
            if not pre:
                scene_note(f"{pip_name} {cur} · última versión", SCENE_DWELL)
            m_check(f"{pip_name} {cur} · última versión")
        else:
            net_ok = False                       # sin respuesta de PyPI: se reintenta al siguiente arranque
            if not PREFETCH["quiet_fail"]:
                scene_note(f"No se pudo comprobar {pip_name}", SCENE_DWELL)
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
    """Notas de `version` (la actual por omisión)"""
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
    """Texto de changelog.md:"""
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
    """changelog.md ← release notes de GitHub de la versión actual y las inferiores."""
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
    """Al abrir:"""
    missing = not os.path.isfile(os.path.join(FILES_DIR, "changelog.md"))
    have = False
    with quiet("ensure_changelog", OSError, ValueError):
        have = os.path.isfile(CHANGELOG_FILE) and VERSION in parse_sections(read_text(CHANGELOG_FILE))
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


def save_snapshot():
    with quiet("save_snapshot"):
        tmp = SNAPSHOT_FILE + ".tmp"             # atómico: un corte a mitad no deja una copia truncada
        shutil.copyfile(SCRIPT_PATH, tmp)
        os.replace(tmp, SNAPSHOT_FILE)


def changelog_block_from_md(md_text):
    """Bloque «# ==== CHANGELOG ==== … # ==== FIN CHANGELOG ====»"""
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
    """Pone `block` donde lo tenía el script:"""
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
    """(sin_changelog, con_changelog)"""
    if live is None:
        live = read_text(SCRIPT_PATH)
    m = CL_RE.search(live)
    if m:                                    # el .py todavía trae su changelog
        return live[:m.start()] + live[m.end():], live
    if snapshot is None and os.path.isfile(SNAPSHOT_FILE):
        with quiet("script_variants", OSError):
            snapshot = read_text(SNAPSHOT_FILE)
    if snapshot and CL_RE.search(snapshot) and remote_script_version(snapshot) == VERSION:
        return live, snapshot                # copia completa de esta misma versión
    if md is None and os.path.isfile(CHANGELOG_FILE):
        with quiet("script_variants", OSError):
            md = read_text(CHANGELOG_FILE)
    block = changelog_block_from_md(md)
    return live, (insert_changelog_block(live, block) if block else None)


# ───────────────────── [G2] Limpieza de almacenamiento ─────────────────────
CLEAN_LIMIT = int(_env_num("DLPY_CLEAN_LIMIT_MB", 1024.0) * 1024 * 1024)      # «inf» ya no impide arrancar


def tree_size(path, seen=None):
    """Bytes de un archivo o carpeta. `seen` evita contar dos veces los enlaces duros."""
    seen = set() if seen is None else seen
    total = 0
    with quiet("tree_size", OSError):
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
    return total


def is_video_file(path):
    return os.path.splitext(path)[1].lstrip(".").lower() in VIDEO_EXTS


def is_download_file(path):
    return os.path.splitext(path)[1].lstrip(".").lower() in DOWNLOAD_EXTS


def download_files(root):
    """Descargas (cualquier tipo de medio)"""
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
        with quiet("prune_empty_dirs", OSError):
            os.rmdir(dp)            # solo funciona si está vacía


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
    """Bytes por categoría + otros + total, sin contar dos veces los enlaces duros."""
    groups = storage_groups()
    seen = set()
    r = {k: sum(tree_size(p, seen) for p in groups[k]) for k in ("dl", "cache", "bak")}
    # Lo que no cae en ninguna categoría (índice, snapshot, changelog…)
    r["other"] = tree_size(INTERNAL_DIR, seen) + tree_size(FILES_DIR, seen)
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
        with quiet("prune_index"):
            save_json(INDEX_FILE, idx)
    with quiet("prune_index"):                                   # historial: fuera lo que ya no está en disco
        hist = load_json(HISTORY_FILE)
        for k in list(hist):
            hist[k] = [e for e in (hist[k] or []) if isinstance(e, dict) and e.get("file") and find_saved(e["file"])]
            if not hist[k]:
                hist.pop(k)
        save_json(HISTORY_FILE, hist)
    return len(gone)


def remove_paths(paths):
    for p in paths:
        with quiet("remove_paths", OSError):
            if os.path.isdir(p) and not os.path.islink(p):
                shutil.rmtree(p, ignore_errors=True)
            elif os.path.lexists(p):
                os.remove(p)


def ensure_dirs():
    # 0.9.9: BACKUP_DIR ya no se crea (sistema eliminado), se crea trash
    for d in (FILES_DIR, INTERNAL_DIR, STATE_DIR, SCRIPT_DIR, STREAM_CACHE_DIR, WORK_ROOT, DELIVERY_DIR, TRASH_DIR):
        try:
            os.makedirs(d, exist_ok=True)
        except OSError:
            pass


def check_storage():
    """0.9.9: solo avisa, conserva descargas."""
    if CONSERVE_DOWNLOADS:
        with quiet("check_storage 0.9.9"):
            seen = set()
            total = tree_size(INTERNAL_DIR, seen) + tree_size(FILES_DIR, seen)
            if total > CLEAN_LIMIT:
                m_warn(f"Almacenamiento {human_size(total)} supera límite {human_size(CLEAN_LIMIT)} pero se conserva (DLPY_CONSERVE=1).")
                dbg("almacenamiento conservado", {"total": total, "limite": CLEAN_LIMIT})
        return
    return


def ask_clean(msg, default=False, alt=None):
    """Pregunta s/n de toda limpieza, con el estilo de las demás («▍Pregunta»"""
    try:
        r = ask_yn(msg, default, alt=alt)
    except (EOFError, KeyboardInterrupt):
        return False
    return bool(default) if r is None else r


def _own_dates():
    """{ruta:"""
    entries = list(load_json(INDEX_FILE).values())
    for lst in load_json(HISTORY_FILE).values():
        entries += lst if isinstance(lst, list) else []
    out = {}
    for e in entries:
        if not (isinstance(e, dict) and e.get("file")):
            continue
        p = find_saved(e["file"])
        if not p:
            continue
        d = e.get("date")
        out[p] = max(out.get(p) or 0, d) if isinstance(d, (int, float)) else out.get(p)
    return out


def _scan_downloads():
    """Descargas sueltas en dlpy_files y sus subcarpetas (sin carpetas ocultas, backups, enlaces ni otros archivos)."""
    out = []
    if not os.path.isdir(FILES_DIR):
        return out
    for n in sorted(os.listdir(FILES_DIR)):
        p = os.path.join(FILES_DIR, n)
        if not is_data_entry(n) or os.path.islink(p):
            continue
        if os.path.isfile(p) and is_download_file(n):
            out.append(p)
        elif os.path.isdir(p):
            out += download_files(p)
    return out


def old_downloads(now=None, secs=None):
    """[(ruta, edad en segundos, bytes)] de lo descargado o convertido hace más de `secs` (un mes), lo más viejo primero."""
    now = time.time() if now is None else now
    secs = TRASH_SECS if secs is None else secs
    dates = _own_dates()
    paths = list(dates) + [p for p in _scan_downloads() if p not in dates]
    rows, seen = [], set()
    for p in paths:
        if p in seen or os.path.islink(p) or not os.path.isfile(p):
            continue
        seen.add(p)
        try:
            st = os.stat(p)
        except OSError as _ign:
            ignore("old_downloads", _ign)
            continue
        when = max(dates.get(p) or 0, st.st_mtime) if dates.get(p) else st.st_mtime
        if now - when > secs:
            rows.append((p, now - when, st.st_size))
    rows.sort(key=lambda r: -r[1])
    return rows


def _move_to_ios_trash(path: str) -> bool:
    with quiet("ios_trash"):
        if os.path.exists(path):
            rc = os.system(f"trash {shlex.quote(path)} >/dev/null 2>&1")
            if rc == 0 and not os.path.exists(path):
                return True
    return False

def log_shortcutmode_error(msg):
    """1.0.4: escribe el error en dlpy_files/shortcutmode.log con fecha, sin romper la escena."""
    try:
        os.makedirs(FILES_DIR, exist_ok=True)
        line = time.strftime("%Y-%m-%d %H:%M:%S") + " - " + str(msg).replace(chr(10), " ").replace(chr(13), " ").strip()[:800] + chr(10)
        with open(SHORTCUTMODE_LOG, "a", encoding="utf-8", errors="replace") as fh:
            fh.write(line)
    except Exception as _ign:
        try:
            dbg("shortcutmode.log fallo", repr(_ign))
        except Exception:
            pass


def ensure_trash():
    # 1.0.4: migra .trash -> trash si existe (no oculta)
    with quiet("ensure_trash migrate"):
        old_hidden = os.path.join(FILES_DIR, ".trash")
        if os.path.isdir(old_hidden) and os.path.abspath(old_hidden) != os.path.abspath(TRASH_DIR):
            os.makedirs(TRASH_DIR, exist_ok=True)
            try:
                for n in os.listdir(old_hidden):
                    s = os.path.join(old_hidden, n)
                    d = os.path.join(TRASH_DIR, n)
                    if not os.path.exists(d):
                        try:
                            os.rename(s, d)
                        except OSError:
                            try:
                                if os.path.isdir(s):
                                    shutil.copytree(s, d)
                                    shutil.rmtree(s, ignore_errors=True)
                                else:
                                    shutil.copy2(s, d)
                                    os.remove(s)
                            except OSError:
                                pass
            except OSError:
                pass
            # si quedó vacío, borrar carpeta oculta
            try:
                if not os.listdir(old_hidden):
                    os.rmdir(old_hidden)
            except OSError:
                pass

    for d in (TRASH_DIR, TRASH_INTERNAL):
        try:
            os.makedirs(d, exist_ok=True)
        except OSError:
            pass
    for d in (TRASH_DIR, TRASH_INTERNAL):
        if os.path.isdir(d):
            return d
    return TRASH_DIR

def move_to_trash(path: str) -> bool:
    if not os.path.exists(path) or os.path.islink(path):
        return False
    if _move_to_ios_trash(path):
        dbg("trash ios", path)
        return True
    trash = ensure_trash()
    try:
        dest = os.path.join(trash, os.path.basename(path))
        base, ext = os.path.splitext(dest)
        k = 2
        while os.path.exists(dest):
            dest = f"{base}-{k}{ext}"
            k += 1
        dest = move_file(path, dest) or dest
        with quiet("trash utime", OSError):
            os.utime(dest, None)                  # 1.1.6: los 30 días de la papelera cuentan desde que entra
        dbg("trash movido", {"origen": path, "destino": dest})
        return True
    except Exception as e:
        ignore("move_to_trash", e)
        return False

def trash_expired(now=None, secs=None):
    now = time.time() if now is None else now
    secs = TRASH_EXPIRE_SECS if secs is None else secs
    out = []
    for base in (TRASH_DIR, TRASH_INTERNAL):
        if not os.path.isdir(base):
            continue
        with quiet("trash_expired", OSError):
            for n in os.listdir(base):
                p = os.path.join(base, n)
                if not os.path.isfile(p) and not os.path.isdir(p):
                    continue
                try:
                    age = now - os.path.getmtime(p)
                except OSError:
                    continue
                if age >= secs:
                    out.append((p, age))
    return out

TRASH_STAMP_FILE = os.path.join(STATE_DIR, "trash_stamp.json")


def migrate_trash_dates():
    """1.1.8: una sola vez, lo que ya estaba en la papelera (sin marca de entrada) empieza a contar sus 30 días desde hoy."""
    try:
        if os.path.isfile(TRASH_STAMP_FILE):
            return 0
        n = 0
        for base in (TRASH_DIR, TRASH_INTERNAL):
            if os.path.isdir(base):
                for name in os.listdir(base):
                    with quiet("migrate_trash_dates", OSError):
                        os.utime(os.path.join(base, name), None)
                        n += 1
        os.makedirs(STATE_DIR, exist_ok=True)
        save_json(TRASH_STAMP_FILE, {"hecho": int(time.time()), "version": VERSION})
        return n
    except Exception as _ign:
        ignore("migrate_trash_dates", _ign)
        return 0


def clean_label(verb, moved=None, gone=0, narrow=None):
    """1.1.8: texto de la escena de limpieza con lo movido y lo borrado: «Limpiando · 3 movidos · 2 borrados». Con poco ancho, abreviado."""
    narrow = (term_width() - 6 < 38) if narrow is None else narrow
    parts = []
    if moved is not None:
        parts.append(f"{moved}" + ("↓" if narrow else (" movido" if moved == 1 else " movidos")))
    if gone:
        parts.append(f"{gone}" + ("×" if narrow else (" borrado" if gone == 1 else " borrados")))
    return verb + (" · " + " · ".join(parts) if parts else "")


def clean_trash():
    n = 0
    for p, age in trash_expired():
        with quiet("clean_trash", OSError):
            if os.path.isdir(p):
                shutil.rmtree(p, ignore_errors=True)
            else:
                os.remove(p)
            if not os.path.exists(p):
                n += 1
                if SCENE["on"]:
                    dbg("trash borrado", {"archivo": os.path.basename(p), "dias": int(age // 86400)})   # 1.1.7: en la escena no se imprime
                    continue
                m_info(f"Trash: {os.path.basename(p)} borrado: {int(age//86400)} d en papelera (límite {TRASH_EXPIRE_DAYS:g}).")
    return n


def clean_old():
    """0.9.9: descargas con >10 días se mueven a trash (no se borran directo)."""
    if not os.path.isdir(FILES_DIR):
        return 0
    now = time.time()
    rows = old_downloads(now, TRASH_SECS)
    dbg("clean_old 0.9.9 trash", len(rows))
    if not rows:
        return 0
    ensure_trash()
    in_scene = bool(SCENE["on"])
    gone = int(SCENE.get("trash_gone") or 0)                      # 1.1.8: lo ya borrado de la papelera en este arranque
    if in_scene:                                                  # 1.1.5: la limpieza se ve en la escena (dibujo «clean»), no en el shell
        SCENE["clean"] = len(rows)
        scene_status(clean_label("Limpiando", len(rows), gone))
    moved = 0
    for p, age, size in rows:
        if move_to_trash(p):
            moved += 1
    if moved:
        prune_empty_dirs(FILES_DIR)
        prune_index()
        m_ok(f"Movidos a papelera: {moved} archivo(s) de más de {TRASH_DAYS:g} días. Se borrarán tras {TRASH_EXPIRE_DAYS:g} días en trash.")
    if in_scene:
        SCENE["clean"] = moved
        scene_status(clean_label("Limpiando", moved, gone))
        scene_hold(SCENE_CLEAN_SECS)                              # se alcanza a ver caer los archivos antes de seguir
    return moved


def expired_backups(now=None, secs=None):
    """0.9.9: sin backups."""
    return []


def expire_backups():
    """0.9.9: sin backups."""
    return 0


def is_data_entry(name):
    """Nombre que cuenta como descarga completada (no backups ni basura)."""
    return not (name.startswith(".") or name.endswith((".tmp", ".part", ".ytdl", ".temp"))
                or name in RESERVED)


def archive_previous(prev, snapshot_version, announce=True):
    """0.9.9: sin backups. Solo borra .dlpy_internal entero y conserva dlpy_files. Restaura terminal handling original."""
    dbg("archive_previous 0.9.9", f"borrando {INTERNAL_DIR}, conservando {FILES_DIR}")
    try:
        if os.path.isdir(INTERNAL_DIR):
            shutil.rmtree(INTERNAL_DIR, ignore_errors=True)
        ensure_dirs()
        ensure_trash()
        m_info(f"Actualización {prev} -> {VERSION}: {INTERNAL_NAME} reiniciado, descargas conservadas.")
    except Exception as e:
        m_warn(f"No se pudo reiniciar {INTERNAL_NAME}: {e}")
        return False
    return True


def make_downgrade_record(stored, current, pending=None, now=None):
    """Registro de una bajada de `stored` a `current`."""
    p = pending if isinstance(pending, dict) else {}
    causa = p.get("causa") if p.get("a") == current and p.get("causa") in DOWNGRADE_CAUSES else "externa"
    rec = {"de": stored, "a": current, "cuando": int(time.time() if now is None else now),
           "causa": causa, "salto": downgrade_span(stored, current)}
    if p.get("a") == current and p.get("hold") is False:
        rec["hold"] = False                  # eligió no quedarse en la versión vieja: no bloquea actualizar
    return rec


def downgrade_hold(version=None, data=None):
    """Versión de la que se bajó a propósito hasta `version` (la actual), o None."""
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
    """Anota que DLpy está a punto de instalar la `to` (más vieja que la `frm` en uso)."""
    with quiet("mark_downgrade_pending"):
        data = load_json(DOWNGRADE_FILE)
        data["pending"] = {"de": frm, "a": to, "causa": causa, "cuando": int(time.time())}
        if not hold:
            data["pending"]["hold"] = False
        os.makedirs(STATE_DIR, exist_ok=True)
        save_json(DOWNGRADE_FILE, data)


DOWNGRADE_WHY = {"manual": "Instalada a propósito desde --versions.",
                 "recuperacion": "Recuperada tras un fallo.",
                 "externa": "El dlpy.py se reemplazó por uno más viejo fuera de DLpy "
                            "(copia manual, atajo o copia antigua)."}


def downgrade_notice(stored):
    """Registro de la bajada `stored` → VERSION (sin escribirlo a disco ni imprimir:"""
    return make_downgrade_record(stored, VERSION, load_json(DOWNGRADE_FILE).get("pending"))


def update_card_rows(stored, current, down, archived, freed, inner):
    """Líneas (pintadas)"""
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
        lines = update_card_rows(stored, VERSION, down, archived, freed, card_inner())
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
    with quiet("downgrade_commit"):
        hist = load_json(DOWNGRADE_FILE).get("history")
        hist = [h for h in hist if isinstance(h, dict)] if isinstance(hist, list) else []
        os.makedirs(STATE_DIR, exist_ok=True)
        save_json(DOWNGRADE_FILE, {"history": (hist + [rec])[-20:]})


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
    """Cada subida o bajada de versión empieza de cero:"""
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
    with quiet("drop_internal_leftovers", OSError):
        if os.path.isdir(old) and not os.path.islink(old):
            shutil.rmtree(old, ignore_errors=True)


def script_code_hash():
    """1.3.2: SHA-256 del código de este dlpy.py sin el changelog (la misma huella que usa compare_texts), o None si no se pudo leer."""
    try:
        return text_fingerprints(read_text(SCRIPT_PATH))[1]
    except (OSError, ValueError) as _ign:
        ignore("script_code_hash", _ign)
        return None


def show_edit_card(old_h, new_h):
    """1.3.2:"""
    dbg("hash del código", f"{(old_h or '')[:7]} → {(new_h or '')[:7]}")
    try:
        if scene_welcome("updated", VERSION, VERSION, edited=True):
            return
    except KeyboardInterrupt:
        raise
    except Exception as _ign:
        ignore("show_edit_card", _ign)
    try:
        rows = card_text_rows(f"Edición detectada · {VERSION}", card_inner(), "white", True, "✓", "mint")
        rows += card_text_rows("Cambió el hash · misma versión", card_inner())
        lines = rows
    except Exception as _ign:
        ignore("show_edit_card", _ign)
        m_ok(f"{VERSION} · edición detectada (cambió el hash, misma versión)")
        return
    print()
    for ln in lines:
        print(ln)
    print()


def check_version():
    state = load_json(VERSION_FILE)
    stored = state.get("version")
    cur_hash = script_code_hash()

    if stored == VERSION:
        if not os.path.isfile(SNAPSHOT_FILE):
            save_snapshot()
            state = {"version": VERSION, "snapshot_version": VERSION, "code_hash": cur_hash}
            save_json(VERSION_FILE, state)
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
        change = code_change(state.get("code_hash"), cur_hash)      # 1.3.2: misma versión, ¿otro código?
        if change:
            old_hash = state.get("code_hash")
            with quiet("check_version", OSError):
                save_json(VERSION_FILE, dict(state, code_hash=cur_hash))
            if change == "edited":
                show_edit_card(old_hash, cur_hash)
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
    save_json(VERSION_FILE, {"version": VERSION, "snapshot_version": VERSION, "code_hash": cur_hash})
    ensure_changelog()       # changelog.md ← release notes de GitHub (versión actual e inferiores)
    if down:
        downgrade_commit(down)
    try:                     # 1.2.9: dentro de la escena, «Primera ejecución» o «Actualizado» (fuera de ella ya salió la tarjeta)
        scene_welcome(welcome_kind(stored, VERSION), stored, VERSION, down=bool(down))
    except KeyboardInterrupt:
        raise
    except Exception as _ign:
        ignore("scene_welcome", _ign)
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
            GH_LAST["code"], GH_LAST["err"] = getattr(r, "status", None) or r.getcode(), None
            return json.load(r)
    except Exception as _ign:
        ignore("remote_releases", _ign)
        GH_LAST["code"], GH_LAST["err"] = None, net_err_text(_ign)
        return None


def _releases_data(timeout=8, pages=REL_MAX_PAGES):
    """(respuesta JSON de la API de GitHub para /releases con todas las páginas, info)"""
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
    """[{ver, url, notes, date}] de la respuesta de la API de GitHub para /releases, del más nuevo al más viejo."""
    owner, repo = info
    out, seen = [], set()
    for it in data if isinstance(data, list) else []:
        if not isinstance(it, dict) or it.get("draft") or it.get("prerelease"):
            continue
        tag = str(it.get("tag_name") or "")
        m = REL_TAG_RE.match(tag)
        ver, url = (m.group(1) if m else None), None
        aname = None
        for a in it.get("assets") or []:
            if not isinstance(a, dict):
                continue
            name = str(a.get("name") or "")
            am = VER_FILE_RE.match(name)
            if (name == "dlpy.py" or am) and a.get("browser_download_url"):
                ver = ver or (am.group(1) if am else None)
                url, aname = str(a["browser_download_url"]), name
                break
        if not ver or ver in seen:
            continue
        if not url:
            if not tag:
                continue
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/{urllib.parse.quote(tag)}/dlpy.py"
        seen.add(ver)
        hinfo = release_hash_info(it, aname)
        if hinfo:
            RELEASE_HASH[url] = hinfo
        out.append({"ver": ver, "url": url, "notes": norm_text(str(it.get("body") or "")).strip(),
                    "date": str(it.get("published_at") or it.get("created_at") or "")[:10]})
    out.sort(key=lambda x: vtuple(x["ver"]), reverse=True)
    return out


def remote_releases(timeout=8):
    """[{ver, url, notes, date}] de los Releases de GitHub, o None si no se pudieron leer."""
    data, info = _releases_data(timeout)
    rels = parse_releases(data, info) if data is not None else None
    if rels is not None:
        RELEASES["list"] = rels
    return rels


def fetch_latest_release(timeout=5):
    """{ver, text, url, notes, date} del Release más nuevo con un dlpy.py válido, o None."""
    t0 = time.time()
    rels = remote_releases(timeout)
    for rel in (rels or [])[:3]:
        text = fetch_remote_script(timeout, rel["url"])
        real = remote_script_version(text) if text else None
        if real:
            net_set("DLpy", t0, True, GH_LAST["code"], real)
            return {"ver": real, "text": text, "url": rel["url"], "notes": rel["notes"], "date": rel["date"]}
    net_set("DLpy", t0, False, err=(GH_LAST["err"] or "sin Release válido") if not rels else "sin Release válido")
    return None


def backup_versions():
    """0.9.9: sin backups."""
    return []


def release_rows(releases, backups=None):
    """Filas de la lista de --versions:"""
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
    """'igual' · 'changelog' (mismo código, otro changelog)"""
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
    """[{version, code, error, time}] de todos los fallos guardados (más viejo primero)."""
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
    """Escribe crashes_dlpy.json con las versiones que fallaron y la causa de cada fallo."""
    with quiet("export_crashes_json"):
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


def record_crash(version, text, error, when=None):
    """Anota un fallo (con la huella del código que falló). Nunca revienta."""
    with quiet("record_crash"):
        entry = {"version": version, "code": text_fingerprints(text)[1] if text else None,
                 "error": str(error)[:300], "time": int(when or time.time())}
        crashes = (load_crashes() + [entry])[-50:]
        os.makedirs(os.path.dirname(CRASH_LOG_FILE), exist_ok=True)
        save_json(CRASH_LOG_FILE, {"crashes": crashes})
    export_crashes_json()


def crash_match(ver, text, crashes=None):
    """None (nunca falló)"""
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
    """True si la versión del Release es la que falló (o más vieja que ella):"""
    if not crashed:
        return False
    if vtuple(remote) == vtuple(crashed) and match == "distinta":
        return False
    return vtuple(remote) <= vtuple(crashed)


def clear_recovered():
    with quiet("clear_recovered", OSError):
        if os.path.isfile(RECOVERED_FILE):
            os.remove(RECOVERED_FILE)


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
    with quiet("mark_good"):
        v = version or VERSION
        good = good_versions()
        if v not in good:
            good.append(v)
            os.makedirs(STATE_DIR, exist_ok=True)
            save_json(GOOD_FILE, {"versions": good[-50:]})


def mark_running():
    with quiet("mark_running"):
        os.makedirs(STATE_DIR, exist_ok=True)
        save_json(RUNNING_FILE, {"version": VERSION, "pid": os.getpid(), "time": int(time.time())})


def clear_running():
    with quiet("clear_running", OSError):
        if os.path.isfile(RUNNING_FILE):
            os.remove(RUNNING_FILE)


def abrupt_why(prev):
    """Texto del aviso tras un cierre inesperado; dice en qué pregunta estaba si se sabe."""
    ver = (prev or {}).get("version")
    where = (prev or {}).get("prompt")
    return (f"La ejecución anterior de la {ver} se cortó"
            + (f" en la pregunta «{where}»" if where else " sin terminar")
            + " y esa versión aún no había terminado bien.")


def should_offer_after_abrupt(prev, good):
    """Tras un cierre inesperado (sin traceback)"""
    ver = (prev or {}).get("version")
    return bool(ver) and ver not in (good or [])


def install_recovered(ver, text, crashed, hold=True):
    """Reemplaza dlpy.py por `text` (versión `ver`)."""
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
        with quiet("install_recovered"):
            save_json(RECOVERED_FILE, {"crashed": crashed, "restored": ver, "time": int(time.time())})
    return True


def _recovery_rows():
    """Busca los Releases de GitHub (y, solo si no se pueden leer, los backups de este equipo)"""
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
    return rows


def _pick_version(rows, why):
    """Muestra las versiones (marcando actual, la de actualizar y los fallos)"""
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
            return None
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
    return shown[n - 1] if n else None


def _install_version(row, crashed):
    """Confirma e instala la versión `row` (release notes, aviso de fallos, bajar de versión)."""
    ver = row["ver"]
    if not confirm_install(f"Instalar la {ver}" + ("" if row["src"] == "release" else " (backup)"), ver,
                           row["notes"], row["date"], unavailable="Los backups no traen release notes."):
        return None
    text = install_text(row, ver)
    if not text:
        m_err(f"No se pudo obtener la {ver} (descarga fallida, archivo no válido o SHA-256 que no coincide).")
        return None
    if str(row.get("ref", "")).startswith("http"):
        show_verify(row["ref"])
    with quiet("offer_recovery", OSError, ValueError):
        if text_fingerprints(text)[1] == text_fingerprints(read_text(SCRIPT_PATH))[1]:
            m_info(f"La {ver} ({row['label']}) es idéntica a la instalada; no hay nada que cambiar.")
            return None
    if show_crash_warning(ver, text) == "igual" and not ask(f"¿Instalar la {ver} igualmente?", default=False):
        return None
    down = version_move(VERSION, ver) == "baja"
    stay = True
    if down:                                  # versión más vieja: ¿bloquear actualizar hasta que salga otra?
        stay = ask(f"¿Quedarte en la {ver} hasta que salga una más nueva?", default=False)
    if not install_recovered(ver, text, crashed, stay):
        return None
    return ver, down, stay


def _recovery_notes(ver, down, stay, crashed):
    """Avisos tras restaurar: qué pasará con las actualizaciones."""
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


def offer_recovery(crashed, why):
    """Lista los Releases de GitHub (y, solo si no se pueden leer, los backups de este equipo)"""
    rows = _recovery_rows()
    if not rows:
        return False
    row = _pick_version(rows, why)
    if row is None:
        return False
    done = _install_version(row, crashed)
    if done is None:
        return False
    ver, down, stay = done
    clear_running()
    m_check(f"DLpy {ver} · restaurada ({row['label']})")
    _recovery_notes(ver, down, stay, crashed)
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
    with quiet("handle_crash"):
        os.makedirs(STATE_DIR, exist_ok=True)
        save_json(CRASH_FILE, {"version": VERSION, "error": f"{type(err).__name__}: {err}",
                               "time": int(time.time()), "traceback": tb[-4000:]})
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
    """Ejecuta entry()"""
    import traceback
    args = norm_args(sys.argv[1:])           # «—versions» (raya larga de iOS) = «--versions»
    if "--selftest" in args or "--sistema" in args or "--perfil" in args or _wants(args, "config") or _wants(args, "cleartest") or wants_2shortcuts(args) or wants_scm(args) or wants_scb(args) \
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
                with quiet("run_guarded", OSError, ValueError):
                    pv = prev.get("version")
                    record_crash(pv, read_text(SCRIPT_PATH) if pv == VERSION else None,
                                 "cierre inesperado (sin traceback)"
                                 + (f" en la pregunta «{prev['prompt']}»" if prev.get("prompt") else ""),
                                 prev.get("time"))
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
            with quiet("run_guarded", AttributeError):
                del sys._dlpy_guarded


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
    with quiet("cleanup_stream_cache", OSError):
        for root, dirs, files in os.walk(STREAM_CACHE_DIR, topdown=False):
            for n in files:
                p = os.path.join(root, n)
                with quiet("cleanup_stream_cache", OSError):
                    if now - os.path.getmtime(p) > STREAM_CACHE_TTL:
                        os.remove(p)
            for n in dirs:
                p = os.path.join(root, n)
                with quiet("cleanup_stream_cache", OSError):
                    if not os.listdir(p):
                        os.rmdir(p)


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
    """Coloca en work_dir los streams cacheados que yt-dlp reconocerá."""
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
            with quiet("seed_work_from_cache", OSError):
                if os.path.exists(target):
                    os.remove(target)
    return reused


def cleanup_work(work_dir):
    if work_dir and os.path.isdir(work_dir):
        shutil.rmtree(work_dir, ignore_errors=True)


# ─────────────────── [H3] Reanudación de descargas ───────────────────
RESUME_PREFIX = "resume-"
RESUME_META = "resume.json"
RESUME_MAX_FAILS = 3        # fallos seguidos sin avanzar antes de descartar el parcial


def resume_key(vkey, specs):
    """Nombre de carpeta estable para una descarga:"""
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
                with quiet("newest_mtime", OSError):
                    best = max(best, os.path.getmtime(os.path.join(r, n)))
    return best


def resume_data_bytes(work_dir):
    """Bytes de datos (parciales y pistas completas) dentro de la carpeta."""
    total = 0
    for r, _d, fs in os.walk(work_dir):
        for n in fs:
            if n == RESUME_META:
                continue
            with quiet("resume_data_bytes", OSError):
                total += os.path.getsize(os.path.join(r, n))
    return total


def read_resume_meta(work_dir):
    try:
        with open(os.path.join(work_dir, RESUME_META), encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def write_resume_meta(work_dir, meta):
    with quiet("write_resume_meta", OSError):
        with open(os.path.join(work_dir, RESUME_META), "w", encoding="utf-8") as f:
            json.dump(meta, f)


def prepare_resume_dir(rkey, base):
    """Crea o recupera work/<rkey>."""
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
    """Conserva el avance tras cancelar o fallar."""
    now = resume_data_bytes(work_dir)
    if now <= 0:
        cleanup_work(work_dir)
        return 0
    if failed:
        meta = read_resume_meta(work_dir)
        meta["fails"] = 0 if now > start_bytes else int(meta.get("fails", 0)) + 1
        write_resume_meta(work_dir, meta)
    return now


# ── Menú de descargas pendientes (0.7.8) ──
def resume_pick(run):
    """Elección de esta descarga en el formato de --shortcutpick (v = format_id, a = pista principal, x = extras):"""
    fmt = run.fmt
    if run.kind == "a":
        return {"v": "audio", "a": str(fmt.get("format_id")), "x": []}
    sel = list(run.selected or [])
    return {"v": str(fmt.get("format_id")),
            "a": str(sel[0]["fmt"].get("format_id")) if sel else None,
            "x": [str(t["fmt"].get("format_id")) for t in sel[1:]]}


def resume_total(run):
    """Tamaño total esperado (bytes, 0 si no se sabe): el formato elegido más las pistas de audio que se unen."""
    fmts = [run.fmt] + [t["fmt"] for t in (run.selected or [])]
    return int(sum((f.get("filesize") or f.get("filesize_approx") or 0) for f in fmts))


def remember_resume(work_dir, run):
    """Guarda en resume.json lo necesario para reanudar desde el menú: enlace, título, elección y tamaño."""
    with quiet("remember_resume"):
        meta = read_resume_meta(work_dir)
        meta.update({"link": run.link, "title": run.title, "pick": resume_pick(run), "total": resume_total(run)})
        write_resume_meta(work_dir, meta)


def resume_candidates(skip_link=None, now=None):
    """Descargas cortadas que el menú puede reanudar (con enlace y elección guardados), la más reciente primero."""
    now = time.time() if now is None else now
    out = []
    try:
        names = sorted(os.listdir(WORK_ROOT))
    except OSError:
        return out
    for n in names:
        p = os.path.join(WORK_ROOT, n)
        if not (n.startswith(RESUME_PREFIX) and os.path.isdir(p)):
            continue
        meta, got = read_resume_meta(p), resume_data_bytes(p)
        link, pick_ = meta.get("link"), meta.get("pick")
        if got <= 0 or not link or not isinstance(pick_, dict) or int(meta.get("fails", 0) or 0) >= RESUME_MAX_FAILS:
            continue
        if skip_link and str(link) == str(skip_link):
            continue
        out.append({"dir": p, "link": str(link), "title": str(meta.get("title") or meta.get("base") or "video"),
                    "pick": pick_, "bytes": got, "total": int(meta.get("total") or 0),
                    "age": max(0.0, now - newest_mtime(p))})
    out.sort(key=lambda r: r["age"])
    return out


def parse_resume_choice(raw, n):
    """Respuesta del menú → (acción, índices desde 0):"""
    s = str(raw or "").strip().lower()
    if not s or s in ("n", "no", "ninguna", "ninguno"):
        return "none", []
    mode = "run"
    m = re.match(r"^d(?:escartar|escartadas?)?\s*(.*)$", s)
    if m:
        mode, s = "discard", m.group(1).strip()
    if s in ("t", "todas", "todos", "todo"):
        return mode, list(range(n))
    idx = []
    for tok in re.split(r"[,\s]+", s):
        if not tok:
            continue
        g = re.fullmatch(r"(\d+)(?:-(\d+))?", tok)
        if not g:
            return "bad", []
        a = int(g.group(1))
        b = int(g.group(2)) if g.group(2) else a
        if a > b:
            a, b = b, a
        if a < 1 or b > n:
            return "bad", []
        idx += range(a - 1, b)
    return (mode, sorted(set(idx))) if idx else ("bad", [])


def _resume_age(sec):
    m = int(sec // 60)
    return f"{max(1, m)} min" if m < 90 else f"{m // 60} h"


def _resume_row(n, it):
    """«  1  Título del video      120 MB / 400 MB · 3 h»: nombre recortado, datos en gris."""
    size = human_size(it["bytes"]) + (f" / {human_size(it['total'])}" if it["total"] > it["bytes"] else "")
    info = f"{size} · {_resume_age(it['age'])}"
    room = max(8, term_width() - 1 - 5 - dwidth(info) - 2)
    name = fit_text(it["title"], room)
    return f"{n:>3}  " + name + " " * (room - dwidth(name)) + "  " + paint(info, "gray")


def resume_menu(items):
    """Pantalla de descargas pendientes. Devuelve las elegidas para reanudar ([] = ninguna). «D» las descarta."""
    items = list(items)
    while items:
        clear_screen()
        header("DESCARGAS PENDIENTES", gap=False)
        m_info(f"{len(items)} sin terminar (caducan a las 24 h).")
        for n, it in enumerate(items, 1):
            print(_resume_row(n, it))
        hint("T todas · n.º (1 3 · 1-3) · D n.º descartar · {Enter = ninguna}")
        while True:
            try:
                raw = ask_line(PROMPT)
            except (EOFError, KeyboardInterrupt):
                return []
            act, idx = parse_resume_choice(raw, len(items))
            if act == "bad":
                m_warn(f"Opción inválida: T, números del 1 al {len(items)}, D n.º o Enter.")
                continue
            break
        if act == "none":
            return []
        if act == "run":
            return [items[i] for i in idx]
        remove_paths([items[i]["dir"] for i in idx])         # discard
        m_ok(f"Descartadas: {len(idx)}")
        items = [it for i, it in enumerate(items) if i not in idx]
    return []


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
            with quiet("cleanup_internal", OSError):
                if now - newest_mtime(p) > INTERNAL_TTL:
                    shutil.rmtree(p, ignore_errors=True)
    cleanup_stream_cache()


# ╔════════════════════════════════════════════════════════════════════════════════════════════════════════╗
# ║ ÁREA I · ENTREGA Y ANÁLISIS — entrega por Atajos, --2shortcuts, análisis tolerante, «no eres un bot»   ║
# ╚════════════════════════════════════════════════════════════════════════════════════════════════════════╝
# ───────────────────── [I1] Entrega del archivo (Atajos) ─────────────────────
def settle_file(path, wait=6.0):
    """Antes de entregar:"""
    with quiet("settle_file", OSError):
        last, t0 = -1, time.time()
        while True:
            size = os.path.getsize(path)
            if size == last or time.time() - t0 > wait:
                break
            last = size
            time.sleep(FILE_POLL)
        fd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        if size <= 0:
            m_warn("El archivo a entregar está vacío.")


DOT_SAFE = "\u2024"                       # «․» (punto de enumeración): se ve como un punto pero no cuenta como extensión


def delivery_name(name):
    """Nombre del archivo en la entrega temporal:"""
    stem, ext = os.path.splitext(name)
    return stem.replace(".", DOT_SAFE) + ext


def delivery_title(title):
    """Título que se manda al atajo, sin puntos (mismo motivo que delivery_name). Función pura."""
    return str(title or "").replace(".", DOT_SAFE)


def drop_deliveries(name):
    """Borra las entregas temporales anteriores de un archivo con ese nombre (delivery/<id>/<name>)."""
    n = 0
    with quiet("drop_deliveries", OSError):
        if not os.path.isdir(DELIVERY_DIR):
            return 0
        for d in os.listdir(DELIVERY_DIR):
            p = os.path.join(DELIVERY_DIR, d)
            if os.path.isdir(p) and not os.path.islink(p) and (os.path.lexists(os.path.join(p, name))
                                                               or os.path.lexists(os.path.join(p, delivery_name(name)))):
                shutil.rmtree(p, ignore_errors=True)
                n += 1
    return n


def unique_path(src):
    name = os.path.basename(src)
    drop_deliveries(name)                   # solo queda la entrega actual con ese nombre
    name = delivery_name(name)              # sin puntos en el nombre: Atajos los tomaría por la extensión
    d = os.path.join(DELIVERY_DIR, uuid.uuid4().hex[:12])
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, name)
    try:
        os.link(src, dst)
    except OSError as _ign:
        ignore("unique_path", _ign)
        copy_file(src, dst)
    try:                                    # la copia tiene que ser el archivo de ahora (mismo archivo o mismo tamaño)
        ok = os.path.samefile(src, dst) or os.path.getsize(src) == os.path.getsize(dst)
    except OSError as _ign:
        ignore("unique_path", _ign)
        ok = False
    if not ok:                              # no era el mismo archivo ni del mismo tamaño: copia nueva
        if os.path.lexists(dst):
            os.remove(dst)
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
    if SCENE["on"] and scene_questions():
        scene_stop(clear=True)             # 0.9.3: hay algo que preguntar: la escena cede y sale como siempre (1.1.5: scene_questions ya es siempre False)
    if CLEAN_LATE["on"]:
        CLEAN_LATE["on"] = False
        try:
            clean_old()                       # 0.8.2: la pregunta pospuesta de --shortcutpick
        except KeyboardInterrupt:
            pass
        except Exception as _ign:
            ignore("clean_old late", _ign)
    if LATE_UPDATES["on"] and not LATE_UPDATES["done"]:
        late_updates()
    cleared = scene_end(view=(view_mode() == "view"))      # 0.9.4: «Enviando a DLpy» (1.3.4: o «Abriendo con view»), la escena se cierra hacia el centro y borra la pantalla
    if not cleared:
        cleared = outro_clear()            # 0.8.5: sin escena, lo último de todo: la consola se deshace como la intro
    if _deliver_platform(final, title, quiet=cleared):
        mark_delivered(final)


def _deliver_view(final, quiet=False):
    """1.3.4:"""
    if not quiet:
        m_info("Abriendo con view...")
    cmd = "view " + shlex.quote(final)
    dbg("entrega", {"origen": final, "modo": "view", "comando": cmd})
    for n in range(2):
        if n:
            time.sleep(OPEN_RETRY)
        if os.system(cmd) == 0:
            return True
        dbg("entrega", f"view falló (intento {n + 1})")
    m_warn("No se pudo abrir con view: el archivo está en dlpy_files.")
    return False


def _deliver_platform(final, title, quiet=False):
    settle_file(final)                     # el convertido recién escrito: completo y en disco antes de avisar
    if view_mode() == "view":              # 1.3.4: modo de vista
        return _deliver_view(final, quiet)
    path = unique_path(final)
    if not quiet:                          # con la consola ya limpia no se escribe nada antes de abrir el atajo
        m_info(f"Enviando a {SHORTCUT_NAME}...")
    dbg("entrega", {"origen": final, "copia": path, "titulo": title})
    url = shortcut_run_url({"file_path": path, "file_title": delivery_title(title)})
    for n in range(3):                     # `open` puede fallar si iOS aún no devolvió el foco a a-Shell
        if n:
            time.sleep(OPEN_RETRY)
        if os.system("open " + shlex.quote(url)) == 0:
            return True
        dbg("entrega", f"open falló (intento {n + 1})")
    m_warn(f"No se pudo abrir el atajo «{SHORTCUT_NAME}»: el archivo está en dlpy_files.")
    return False


def mark_delivered(final, when=None):
    """Guarda en el índice la hora de la última entrega del archivo (clave «delivered»)."""
    with quiet("mark_delivered"):
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


def reopen_question():
    """Texto de la pregunta «¿Abrir otra vez…?»."""
    return "¿Abrir otra vez con Atajos? (S/n) ▸ "


def deliver_existing(old_file, old_entry, title):
    """Entrega un archivo ya descargado."""
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
    """`--2shortcuts` (iOS):"""
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
        with quiet("send_code_to_shortcut", OSError):
            os.remove(tmp)
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
    """Opciones de YoutubeDL que produciría la CLI de yt-dlp con `argv` (mismos valores por defecto:"""
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


def analyze_link(yt_dlp, link, quick=False, argv=None):
    """Devuelve (info, base_opts)."""
    SCENE["link"] = link                      # 1.4.3: la escena D L P Y teclea este enlace en extract_info(…)
    extra = list(argv) if argv is not None else user_argv()
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
        _sc_mark("opts")
        _t_o = time.time()
        base = make()
        _sc_add("opts", time.time() - _t_o)
        if base is None:
            continue
        probe = {**base, **std}
        if not no_pl:
            probe.pop("noplaylist", None)
        if i:
            m_info(f"Reintentando análisis ({name})...")
        _sc_mark("net")
        _t_n = time.time()
        try:
            with yt_dlp.YoutubeDL(probe) as ydl:
                info = ydl.extract_info(link, download=False)
            _sc_add("net", time.time() - _t_n)
            if info:
                dbg("análisis", f"funcionó: {name}")
                ANALYSIS["stage"] = name
                net_set("analyze", _t_n, True, None, str(info.get("extractor_key") or info.get("extractor") or "") or None)
                return info, base
        except KeyboardInterrupt:
            raise
        except Exception as e:
            _sc_add("net", time.time() - _t_n)
            last = e
            net_set("analyze", _t_n, False, err=net_err_text(e))
            dbg("análisis falló", f"{name}: {e}")
            if is_bot_error(e):
                raise          # repetir el análisis no ayuda
    m_info("Reintentando análisis (yt-dlp en bruto)...")
    _sc_mark("bruto")
    SCENE["ana_raw"] = True                   # 1.4.4: este paso sí es `yt-dlp -J <enlace>`: la escena teclea ese comando
    _t_raw = time.time()
    info = probe_cli_json(link, extra, 60 if quick else 180)
    if info:
        net_set("analyze", _t_raw, True, None, str(info.get("extractor_key") or info.get("extractor") or "") or None)
    if info:
        dbg("análisis", "funcionó: yt-dlp en bruto (-J)")
        ANALYSIS["stage"] = "yt-dlp en bruto"
        base = cli_like_opts(yt_dlp, ["--no-playlist"] + extra) or {}
        return info, base
    raise last or RuntimeError("no se pudo analizar el enlace")


# Errores que justifican reanalizar el enlace (se evalúa sobre el texto en minúsculas).
_RETRY_RE = re.compile(r"not available|expired|forbidden|\bhttp error (?:403|410)\b")


def run_download(ydl, yt_dlp, info, link, fmt_id):
    """Descarga con el MISMO análisis que vio el usuario (así los format_id coinciden)."""
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
    b = ACTIVE_BAR
    if b is not None and b.th:
        b.reset("Reanalizando el enlace")      # dentro del panel: imprimir encima de él lo dejaba pegado
    else:
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
# Ver más: si la lista corta oculta formatos, su última fila es «▸ Ver todos (+N)» (id «more»); v=more abre en el script
# la lista completa (all_video_* trae la misma lista para un menú nativo si caben en SC_ALL_MAX).
SHORTCUT_SCHEMA = 1
DASHES = "-\u2013\u2014"                       # raya normal, en y em (el teclado de iOS convierte «--» en «—»)
VALUE_FLAGS = {"shortcutpick"}                 # banderas con valor: «--bandera valor» o «--bandera=valor»
SC_ALL_MAX = 40                        # más formatos que esto: la lista completa NO va en el JSON (se ve en el script con v=more)
SC_MORE_IDS = ("more", "all", "todos", "ver_todos")    # lo que devuelve el atajo (v=…) al elegir «Ver todos»
SC_URL_MAX = 30000                     # largo máximo de la URL shortcuts://; si pasa, el JSON va por el portapapeles
SC_TIMEOUT = _env_num("DLPY_SC_TIMEOUT", 90.0)     # tope del análisis para el atajo (s; 0 = sin tope)
# --scm corre en «Ejecutar comando» de a-Shell EN EXTENSIÓN y Atajos la corta a ~10 s (medido): el análisis
# tiene que responder antes. Se cuenta desde que arrancó el script (BOOT_T0, justo tras los imports); si no alcanza,
# devuelve «timeout». 1.2.1: tope de 7 s (antes 5) y la espera final se acorta para que el proceso termine antes de
# SCM_HARD (así Atajos recibe siempre el JSON y no el corte de ~10 s).
SCM_TIMEOUT = _env_num("DLPY_SCM_TIMEOUT", 5.0)          # 1.2.7: 5 s (antes 7)
SCM_HARD = _env_num("DLPY_SCM_HARD", 8.0)          # s (desde BOOT_T0) a los que el proceso debería haber terminado; 0 = sin tope.
# OJO: BOOT_T0 va tras compilar el script (~1 s en iPhone, no se cuenta): 8,0 aquí ≈ 9 s reales frente al corte de ~10 s de Atajos
SCM = {"on": False, "abort": threading.Event(), "thread": None}     # estado de --scm
SCM_UNWIND = 2.0                       # s que se espera (como máximo) a que el hilo de análisis termine solo tras un timeout
SC_TIMING = {}                         # 1.2.1: segundos por fase (boot, prep, imp, opts, net, ff, build, total): va en el JSON («timing»)
SC_PHASE = [""]                        # fase en curso; si hay timeout, el JSON dice en cuál se quedó («phase»)


def _sc_mark(phase):
    SC_PHASE[0] = phase


def _sc_add(name, secs):
    SC_TIMING[name] = round(SC_TIMING.get(name, 0.0) + secs, 2)


def _scm_unwind():
    """Segundos que se esperan al hilo tras un timeout: SCM_UNWIND, pero sin pasar de SCM_HARD (mínimo 0,2 s)."""
    if SCM_HARD <= 0:
        return SCM_UNWIND
    return max(0.2, min(SCM_UNWIND, SCM_HARD - (time.time() - BOOT_T0)))


def norm_args(args):
    """Las rayas largas que pone el teclado de iOS (– —)"""
    out = []
    for a in args:
        if a[:1] in ("\u2013", "\u2014") and a.lstrip(DASHES)[:1].isalpha():
            a = "--" + a.lstrip(DASHES)
        out.append(a)
    return out


def parse_cli(args):
    """(banderas, posicionales)."""
    flags, pos, args, i = {}, [], list(args), 0
    while i < len(args):
        a = args[i]
        i += 1
        lead = len(a) - len(a.lstrip(DASHES))
        if lead >= 2 or (lead == 1 and a[0] in "\u2013\u2014" and len(a) > 1):
            a = "--" + a[lead:]                  # «—flag» / «–flag» (iOS convierte «--») = «--flag»
        if not a.startswith("--"):
            pos.append(a)
            continue
        name, eq, val = a[2:].partition("=")
        name = name.lower()
        if not name:
            continue
        if name in VALUE_FLAGS:
            if not eq and i < len(args) and not args[i].startswith(("--", "\u2014", "\u2013")):
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
    """Lo que devuelve el atajo:"""
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


APPLE_MARK = "\uf8ff"                  # manzana mordida (logo de Apple, solo se ve en dispositivos Apple)


def shortcut_fps(f):
    try:
        v = float(f.get("fps") or 0)
    except (TypeError, ValueError):
        return 0
    return int(round(v)) if v > 0 else 0


def shortcut_quality_key(f):
    """Una entrada por resolución + fps (1080p 60fps y 1080p 30fps son distintas); el HDR o los más de 8 bits cuentan aparte, como en…"""
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


def k_label(f):
    """«2K», «4K», «8K», «16K»"""
    try:
        h, w = int(f.get("height") or 0), int(f.get("width") or 0)
    except (TypeError, ValueError):
        return None
    m = min(h, w) if (h and w) else h
    for lim, name in ((8000, "16K"), (4000, "8K"), (2000, "4K"), (1400, "2K")):
        if m >= lim:
            return name
    return None


def shortcut_video_name(f):
    """«1080p 60fps», «4K 2160p 30fps HDR10»: (K) resolución + fps (+ rango si no es SDR de 8 bits)."""
    h = f.get("height")
    s = f"{h}p" if h else format_tag(f)
    k = k_label(f)
    if k:
        s = f"{k} {s}"
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
    tech = f"{f.get('ext') or '?'} {acodec_short(f)}" + (f" {abr:.0f}k" if abr else "")
    return lead + (" · original" if t["original"] else "") + f" · {tech}" + (f" {APPLE_MARK}" if apple_audio(f) else "")


def best_audio(audios, orig_ids=()):
    """El audio de mejor calidad:"""
    pool = [f for f in audios if f.get("format_id") in orig_ids] or list(audios)
    return max(pool, key=lambda f: (abr_of(f), apple_audio(f)), default=None)


def shortcut_audio_items(audios, orig_ids, duration=None):
    """Todos los audios para el JSON:"""
    best = best_audio(audios, orig_ids)
    order = sorted(audios, key=lambda f: (f.get("format_id") not in orig_ids, str(f.get("language") or ""),
                                          -abr_of(f), not apple_audio(f), str(f.get("format_id"))))
    out = []
    for n, f in enumerate(order, 1):
        abr = abr_of(f)
        size = f.get("filesize") or f.get("filesize_approx")
        size_t = human_size(size) if size else size_estimate(abr, duration)
        lang = f.get("language") or ""
        is_best = f is best
        tech = f"{f.get('ext') or '?'} {acodec_short(f)}" + (f" {abr:.0f}k" if abr else "")
        parts = [("★ " if is_best else "") + (lang or "audio"), tech, size_t]
        orig = f.get("format_id") in orig_ids
        if orig:
            parts.insert(2, "original")
        label = f"{n} · " + " · ".join(p for p in parts if p) + (f" {APPLE_MARK}" if apple_audio(f) else "")
        out.append({"n": n, "id": str(f.get("format_id")), "label": label, "lang": lang or None,
                    "ext": f.get("ext"), "codec": acodec_short(f),
                    "abr": round(abr) if abr else None, "size_bytes": size, "size": human_size(size) if size else None,
                    "size_est": None if size else size_t, "original": orig, "compatible": bool(apple_audio(f)),
                    "best": is_best})
    return out


def shortcut_error(code, msg, link=None, elapsed=None):
    out = {"dlpy": "shortcutmode", "schema": SHORTCUT_SCHEMA, "ok": False, "status": "error", "version": VERSION,
           "link": link, "error_code": code, "error": msg}
    if elapsed is not None:
        out["elapsed"] = elapsed
    return out


SC_TITLE_MAX = 60                      # largo del título corto del menú de Atajos


def short_title(title, limit=SC_TITLE_MAX):
    """Título corto para el mensaje del menú de Atajos:"""
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
    s = f"{f.get('ext') or '?'} {acodec_short(f)}" + (f" {abr:.0f}k" if abr else "")
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
    """Lo que bajaría yt-dlp con su formato por omisión «bv*+ba/b»:"""
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


def _sc_pick_videos(videos, bk, bf, can_merge):
    """Un video por calidad (la mejor opción de cada grupo), de mayor a menor resolución."""
    groups = {}
    for f in videos:
        groups.setdefault(shortcut_quality_key(f), []).append(f)

    def rank(f):        # misma preferencia que la lista corta: con audio si no hay ffmpeg, compatible, bitrate
        return (has(f.get("acodec")) if not can_merge else False, bool(apple_video(f)),
                f.get("tbr") or 0)

    picked = [bf if bk == "v" and any(x is bf for x in g) else max(g, key=rank) for g in groups.values()]
    return _sc_sort_videos(picked)


def _sc_sort_videos(vs):
    """Orden del menú del atajo: de mayor a menor resolución, fps y bitrate."""
    return sorted(vs, key=lambda f: (-(f.get("height") or 0), -shortcut_fps(f), bool(detect_hdr(f)),
                                     -(shortcut_kbps(f) or 0), str(f.get("format_id"))))


def _sc_history(old_file, old_entry, history):
    """Lo ya descargado de este video:"""
    old_meta = (old_entry or {}).get("meta") or {} if old_file else {}
    hist = list(history) if history is not None else ([(old_file, old_entry)] if old_file else [])
    got_video = {str(((e.get("meta") or {}).get("format_id") or "")).split("+")[0]
                 for _p, e in hist if ((e.get("meta") or {}).get("kind")) == "video"}
    got_audio = any(((e.get("meta") or {}).get("kind")) == "audio" for _p, e in hist)
    # idiomas que ya tienes en CUALQUIER archivo descargado de este video (solo audio o dentro de un video)
    got_langs = {str(tr.get("lang")) for _p, e in hist for tr in ((e.get("meta") or {}).get("tracks") or [])
                 if tr.get("lang")}
    return old_meta, hist, got_video, got_audio, got_langs


def _sc_video_item(f, info, bk, bf, can_tracks, multi_lang, got_video):
    """Entrada de la lista de videos del atajo para un formato."""
    has_a = has(f.get("acodec"))
    size = f.get("filesize") or f.get("filesize_approx")
    kbps = shortcut_kbps(f)
    return {
        "id": str(f.get("format_id")), "name": shortcut_video_name(f), "height": f.get("height"),
        "fps": shortcut_fps(f) or None, "ext": f.get("ext"),
        "vcodec": ((f.get("vcodec") or "?").split(".")[0] if str(f.get("vcodec") or "unknown").lower()
                   not in ("unknown", "?")
                   else (f"{f.get('ext') or '?'} · con audio" if has_a else (f.get("ext") or "?"))),
        "k": k_label(f), "range": range_label(f) or None, "hdr": detect_hdr(f), "size_bytes": size,
        "size": human_size(size) if size else None, "compatible": bool(apple_video(f)),
        "kbps": round(kbps) if kbps else None,
        "size_est": None if size else size_estimate(kbps, info.get("duration")),
        "audio": "included" if has_a else ("separate" if can_tracks else "none"),
        "audio_step": "none" if (has_a or not can_tracks or not multi_lang) else "full",
        "best": bk == "v" and f is bf,
        "have": str(f.get("format_id")) in got_video}


def _sc_auto_item(info, audios, videos, hist):
    """Opción «yt-dlp auto»: (entrada o None, extras_error)."""
    try:
        got_ids = {str((e.get("meta") or {}).get("format_id") or "") for _p, e in hist}
        auto = ytdlp_auto_pick(info, audios, videos)
    except Exception as e:
        return None, f"auto: {type(e).__name__}: {e}"
    if not auto:
        return None, None
    av, aa = auto
    aid = "+".join([str(av.get("format_id"))] + ([str(aa.get("format_id"))] if aa else []))
    desc = video_desc(av) + (f" + {audio_desc(aa)}" if aa else "")
    return {
        "id": "ytdlp", "name": "yt-dlp auto", "height": av.get("height"), "fps": shortcut_fps(av) or None,
        "ext": av.get("ext"), "vcodec": desc, "k": k_label(av), "range": range_label(av) or None, "hdr": detect_hdr(av),
        "size_bytes": None, "size": None,
        "compatible": bool(apple_video(av)) and (aa is None or bool(apple_audio(aa))),
        "audio": "separate" if aa else "included", "audio_step": "none", "best": False,
        "have": aid in got_ids,
        "auto": {"video_id": str(av.get("format_id")), "audio_id": str(aa.get("format_id")) if aa else None,
                 "video": video_desc(av), "audio": audio_desc(aa) if aa else None, "formato": aid}}, None


def _sc_audio_items(audios, tracks, orig_ids, bk, multi_lang, got_audio, extras_error):
    """Opciones «Solo audio»"""
    if not audios:
        return [], extras_error
    items = []
    solo_audio = ""
    _ba = _ap = None
    try:
        _ba = best_audio(audios, orig_ids)                        # el de mejor calidad, sea Apple o no
        _t = next((t for t in tracks if t["original"]), tracks[0] if tracks else None)
        _ap = _t["fmt"] if _t else None                           # el de siempre: compatible con Apple si lo hay
        if _ba is not None and (_ap is None or (apple_audio(_ba) and not apple_audio(_ap))
                                or not any(apple_audio(f) for f in audios)):
            _ap = _ba                                             # sin audios Apple: una sola opción, la mejor
        solo_audio = audio_desc(_ap) if _ap else ""
    except Exception as e:
        extras_error = f"solo audio: {type(e).__name__}: {e}"
    _ap_ok = _ap is not None and bool(apple_audio(_ap))
    _same = _ba is None or _ap is None or _ba is _ap or (apple_audio(_ba) and _ap_ok)
    items.append({
        "id": "audio", "name": "Solo audio", "height": None, "fps": None, "ext": None, "vcodec": None,
        "range": None, "hdr": None, "size_bytes": None, "size": None,
        "compatible": _ap_ok, "audio": "only",
        "audio_step": "track" if multi_lang else "none", "best": bk == "a",
        "have": got_audio, "detail": solo_audio or None})
    if not _same:                      # el mejor no es el compatible con Apple: opción aparte (se pregunta convertir)
        items.append({
            "id": "audio_best", "name": "Solo audio (mejor)", "height": None, "fps": None, "ext": None,
            "vcodec": None, "range": None, "hdr": None, "size_bytes": None, "size": None,
            "compatible": bool(apple_audio(_ba)), "audio": "only",
            "audio_step": "track" if multi_lang else "none", "best": False, "ask_convert": True,
            "have": False, "detail": audio_desc(_ba)})
    return items, extras_error


def _sc_menu_label(n, it, v_items, audio_is_best):
    """Texto del menú de Atajos para la opción `it` (número, nombre y marcas 🔊 🔇 Apple ✅)."""
    # emojis en color (el menú de Atajos es texto plano, pero los emojis sí se ven en color)
    marks = ((" 🔊" if it.get("audio") == "included" else " 🔇" if it.get("audio") == "none" else "")
             + (f" {APPLE_MARK}" if it.get("compatible") else "")
             + (" ✅" if it.get("have") else ""))
    if it["id"] in ("audio", "audio_best"):
        two = any(o["id"] == "audio_best" for o in v_items)      # hay dos: Apple y mejor
        head = ("Solo audio · Apple" if it["id"] == "audio" else "★ Solo audio · mejor") if two else (
            "★ Solo audio · mejor" if audio_is_best else "Solo audio")
        return f"{n} · ♫ {head}" + (f" · {it['detail']}" if it.get("detail") else "") + marks
    if it["id"] == "ytdlp":
        same = next((o["n"] for o in v_items if o.get("n") and o["id"] == it["auto"]["video_id"]), None)
        return f"{n} · yt-dlp auto · {it['vcodec']}" + (f" (= {same})" if same else "") + marks
    vc = re.sub(r"\s*·\s*con audio$", "", str(it["vcodec"] or ""))      # «con audio» ya lo dice 🔊
    parts = [("★ " if it["best"] else "") + it["name"], vc]
    if not it.get("height") and it.get("kbps"):                         # sin resolución: el bitrate distingue
        parts.append(kbps_text(it["kbps"]))
    parts.append(it["size"] or it.get("size_est"))
    return f"{n} · " + " · ".join(p for p in parts if p) + marks


def _sc_track_items(tracks, got_langs):
    """Pistas de audio del video (para elegir la predeterminada y las extra)."""
    t_items = []
    for n, t in enumerate(tracks, 1):
        f = t["fmt"]
        got = str(t["lang"]) in got_langs
        t_items.append({"n": n, "id": t["lang"], "lang": t["lang"], "have": got,
                        "label": f"{n} · {shortcut_track_name(t)}" + (" ✅" if got else ""),
                        "format_id": str(f.get("format_id")), "ext": f.get("ext"),
                        "codec": acodec_short(f),
                        "abr": round(abr_of(f)) if abr_of(f) else None,
                        "original": bool(t["original"]), "compatible": bool(apple_audio(f))})
    return t_items


def _sc_duration(dur):
    """(segundos enteros o None, texto «m:ss» / «h:mm:ss» o None)."""
    try:
        d = int(dur) if dur else None
    except (TypeError, ValueError):
        d = None
    dur_text = (f"{d // 3600}:{d % 3600 // 60:02d}:{d % 60:02d}" if d and d >= 3600
                else f"{d // 60}:{d % 60:02d}" if d is not None else None)
    return d, dur_text


def _sc_number(items, audio_is_best):
    """Numera `items` (1…n) y les pone su etiqueta de menú."""
    for n, it in enumerate(items, 1):
        it["n"] = n
        it["label"] = _sc_menu_label(n, it, items, audio_is_best)


def _sc_view_all(info, videos, v_items, bk, bf, can_tracks, multi_lang, got_video, audio_is_best):
    """«Ver todos»:"""
    all_items = []
    more_n = len(videos) - sum(1 for it in v_items if it["id"] not in ("ytdlp", "audio", "audio_best"))
    if more_n <= 0:
        return all_items, more_n
    if len(videos) <= SC_ALL_MAX:            # con cientos de formatos el menú de iOS iría lento: solo v=more
        all_items = [_sc_video_item(f, info, bk, bf, can_tracks, multi_lang, got_video)
                     for f in _sc_sort_videos(videos)]
        all_items += [dict(it) for it in v_items if it["id"] in ("ytdlp", "audio", "audio_best")]
        _sc_number(all_items, audio_is_best)
    # última fila de la lista que el atajo ya muestra: al elegirla devuelve v=more y el script abre la lista completa
    n_more = len(v_items) + 1
    v_items.append({"id": "more", "name": "Ver todos", "height": None, "fps": None, "ext": None, "vcodec": None,
                    "range": None, "hdr": None, "size_bytes": None, "size": None, "compatible": False,
                    "audio": "none", "audio_step": "none", "best": False, "have": False, "more": True,
                    "n": n_more, "label": f"{n_more} \u00b7 \u25b8 Ver todos (+{more_n})"})
    return all_items, more_n


def _sc_previous(old_file, old_entry, old_meta, hist):
    """(la copia ya descargada o None, lista de descargas anteriores) para el JSON del atajo."""
    old = ({"file": os.path.basename(old_file), "title": (old_entry or {}).get("title"),
            "date": (old_entry or {}).get("date"), "kind": old_meta.get("kind"), "format_id": old_meta.get("format_id")}
           if old_file else None)
    downloaded = [{"file": os.path.basename(pth), "kind": (e.get("meta") or {}).get("kind"),
                   "format_id": (e.get("meta") or {}).get("format_id"), "date": e.get("date")} for pth, e in hist]
    return old, downloaded


def _sc_pick_example(v_items, t_items, multi_lang):
    """Ejemplo de la elección que devuelve el atajo: v=<mejor video>,a=<pista>,x=<pista extra>."""
    return ("v=" + next((it["id"] for it in v_items if it["best"]), v_items[0]["id"])
            + (f",a={t_items[0]['id']}" if t_items and multi_lang else ",a=")
            + (f",x={t_items[1]['id']}" if len(t_items) > 1 and multi_lang else ",x="))


def build_shortcut_payload(info, link, can_merge, old_file=None, old_entry=None, history=None):
    """El JSON que lee el atajo."""
    _formats, audios, videos = split_formats(info)
    if not audios and not videos:
        return shortcut_error("no_formats", "No se encontraron formatos.", link)
    orig_ids = mark_originals(audios)
    tracks, orig_lang = build_tracks(audios, orig_ids)
    multi_lang = len({t["lang"] for t in tracks if t["lang"] != "und"}) > 1
    bk, bf = auto_best(audios, videos, orig_ids, can_merge, quiet=True)
    can_tracks = bool(tracks) and bool(can_merge)

    picked = _sc_pick_videos(videos, bk, bf, can_merge)
    old_meta, hist, got_video, got_audio, got_langs = _sc_history(old_file, old_entry, history)

    v_items = [_sc_video_item(f, info, bk, bf, can_tracks, multi_lang, got_video) for f in picked]
    auto_item, extras_error = _sc_auto_item(info, audios, videos, hist)
    if auto_item:
        v_items.append(auto_item)
    a_extra, extras_error = _sc_audio_items(audios, tracks, orig_ids, bk, multi_lang, got_audio, extras_error)
    v_items.extend(a_extra)

    audio_is_best = bool(audios) and not any(o["id"] == "audio_best" for o in v_items)
    _sc_number(v_items, audio_is_best)
    all_items, more_n = _sc_view_all(info, videos, v_items, bk, bf, can_tracks, multi_lang, got_video, audio_is_best)

    t_items = _sc_track_items(tracks, got_langs)
    t_labels = [it["label"] for it in t_items]
    a_items = shortcut_audio_items(audios, orig_ids, info.get("duration"))
    extra_menu = {str(i): [lab for j, lab in enumerate(t_labels, 1) if j != i] for i in range(1, len(t_labels) + 1)}

    d, dur_text = _sc_duration(info.get("duration"))
    old, downloaded = _sc_previous(old_file, old_entry, old_meta, hist)
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
        "has_more": more_n > 0, "more_count": max(0, more_n), "more_id": "more",
        "more_label": f"\u25b8 Ver todos (+{more_n})" if more_n > 0 else None,
        "all_in_script": more_n > 0 and not all_items,
        "all_video_labels": [it["label"] for it in all_items], "all_video_ids": [it["id"] for it in all_items],
        "all_video_audio_step": [it["audio_step"] for it in all_items],
        "all_default_video": next((it["n"] for it in all_items if it["best"]), 1) if all_items else None,
        "track_labels": t_labels, "track_ids": [it["id"] for it in t_items], "extra_menu": extra_menu,
        "audio_labels": [it["label"] for it in a_items], "audio_ids": [it["id"] for it in a_items],
        "default_audio": next((it["n"] for it in a_items if it["best"]), None),
        "ask_convert": any(it["best"] and not it["compatible"] for it in a_items),
        "videos": v_items, "tracks": t_items, "audios": a_items, "all_videos": all_items,
        "pick_format": "v=<video_ids[n]>,a=<track_ids[n]>,x=<track_ids[n]>+<track_ids[m]>"
                       " (con v=audio, a=<audio_ids[n]> elige ese audio exacto; v=more abre la lista completa)",
        "pick_example": _sc_pick_example(v_items, t_items, multi_lang)}


def _sc_prepare(box):
    """1.2.1:"""
    t0 = time.time()
    with quiet("_sc_prepare argv"):
        box["argv"] = user_argv()
    with quiet("_sc_prepare json"):
        box["index"] = load_json(INDEX_FILE)
        box["history"] = load_json(HISTORY_FILE)
    _sc_add("prep", time.time() - t0)


def shortcut_collect(link):
    """Analiza `link` y devuelve el diccionario de salida (siempre uno, nunca lanza)."""
    t0 = time.time()

    def done(data):
        data["elapsed"] = round(time.time() - t0, 1)
        return data

    link = (link or clipboard_link() or "").strip()
    if not link:
        return done(shortcut_error("no_link", "No hay enlace: usa --scb LINK o --scm LINK."))
    prep, pth = {}, None
    if SCM["on"]:
        pth = threading.Thread(target=_sc_prepare, args=(prep,), name="dlpy-scm-prep", daemon=True)
        pth.start()
    _sc_mark("import")
    _t_i = time.time()
    try:
        import yt_dlp
    except Exception as e:                      # ImportError y cualquier fallo al cargarlo
        err = shortcut_error("no_ytdlp", f"yt-dlp no está instalado ({e}). Usa --scb: lo instala.", link)
        err["use_scb"] = True                   # --scm no instala (tarda más de 10 s); --scb sí
        return done(err)
    _sc_add("imp", time.time() - _t_i)
    ff = {}

    def _probe_ffmpeg():
        _t = time.time()
        with quiet("shortcut_collect ffmpeg"):
            ff["ok"] = bool(ffmpeg_available())
        _sc_add("ff", time.time() - _t)
    fth = threading.Thread(target=_probe_ffmpeg, name="dlpy-ffmpeg", daemon=True)
    fth.start()                                 # mientras la red responde (antes se sondeaba después, en serie)
    if not SCM["on"]:                           # --scm no escribe en disco: no necesita la carpeta de estado
        with quiet("shortcut_collect", OSError):
            os.makedirs(STATE_DIR, exist_ok=True)
    if pth is not None:
        pth.join()
    ANALYSIS["stage"] = None
    try:
        info, _base = analyze_link(yt_dlp, link, quick=True, argv=prep.get("argv"))
    except KeyboardInterrupt:
        raise
    except Exception as e:
        return done(shortcut_error("bot" if is_bot_error(e) else "analyze",
                                   str(e).strip()[:400] or "error al analizar", link))
    if info.get("entries"):
        info = next((e for e in info["entries"] if e), info)
    _sc_mark("build")
    _t_b = time.time()
    key = video_key(info)
    idx = prep["index"] if "index" in prep else load_json(INDEX_FILE)
    old_file, old_entry = lookup_downloaded(idx, key)
    fth.join(3.0)                               # casi siempre ya terminó; si no, el respaldo es el mismo de ffmpeg_available
    can_merge = ff["ok"] if "ok" in ff else bool(shutil.which("ffmpeg"))
    data = build_shortcut_payload(info, link, can_merge, old_file, old_entry,
                                  history_for(key, idx, prep.get("history")))
    with quiet("shortcut_remember"):
        shortcut_remember(key, data)                    # 1.5.4: la lista del JSON se guarda: si el id cambia en la descarga, se conserva la calidad
    _sc_add("build", time.time() - _t_b)
    data["stage"] = ANALYSIS["stage"]
    return done(data)


def collect_with_timeout(link, secs=None, fn=None):
    """shortcut_collect con tope de tiempo (SC_TIMEOUT):"""
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
    with quiet("write_shortcut_json", OSError):
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(SHORTCUT_JSON, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)


def shortcut_mode(flags, pos):
    """`--scm LINK`:"""
    link = pos[0] if pos else None
    real_out, real_err = sys.stdout, sys.stderr
    sink = open(os.devnull, "w", encoding="utf-8")
    sys.stdout = sys.stderr = sink              # mensajes internos, yt-dlp, avisos: nada ensucia la salida
    SCM["on"] = True
    SC_TIMING["boot"] = round(time.time() - BOOT_T0, 2)     # desde los imports hasta aquí (definiciones, dlpy_config.json…)
    data = None
    try:
        left = max(1.0, SCM_TIMEOUT - (time.time() - BOOT_T0)) if SCM_TIMEOUT > 0 else None
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
    if isinstance(data, dict):                  # 1.2.1: dónde se fue el tiempo (y, si hubo timeout, en qué fase se quedó)
        SC_TIMING["total"] = round(time.time() - BOOT_T0, 2)
        data["timing"] = dict(SC_TIMING)
        if not data_is_final(data):
            data["phase"] = SC_PHASE[0]
    text = json.dumps(data, ensure_ascii=True, separators=(",", ":"))
    if not data_is_final(data):
        # «timeout»: el análisis sigue vivo en otro hilo. Se imprime el JSON YA y se le pide al hilo que pare
        # (abort + sockets de 2 s); se espera un poco a que termine solo y se sale normal. NO se usa os._exit:
        # en a-Shell mataba el proceso con el hilo dentro de ssl y daba «Fatal Python error … segmentation fault».
        # 1.2.1: la espera se acorta (_scm_unwind) para que el proceso termine antes de SCM_HARD
        real_out.write(text + "\n")
        real_out.flush()
        SCM["abort"].set()
        th = SCM.get("thread")
        if th is not None:
            th.join(_scm_unwind())
        return 0
    if flags.get("shortcutclip"):
        shortcut_copy(text)
    real_out.write(text + "\n")
    real_out.flush()
    # 1.2.1: --scm solo genera el JSON: la copia legible en disco (state/shortcut_analysis.json) ya no se escribe,
    # salvo con DLPY_DEBUG o DLPY_SCM_SAVE=1 (y entonces va DESPUÉS de imprimir, no antes)
    if DEBUG or _flag_env("DLPY_SCM_SAVE", False):
        write_shortcut_json(data)
    return 0


def data_is_final(data):
    return bool(data) and data.get("error_code") != "timeout"


def shortcut_send(data, name=None):
    """Abre shortcuts://run-shortcut?name=… con el JSON como entrada (sin «videos», «tracks»"""
    name = name or SHORTCUT_NAME
    slim = {k: v for k, v in data.items() if k not in ("videos", "tracks", "audios", "all_videos")}
    text = json.dumps(slim, ensure_ascii=True, separators=(",", ":"))
    url = ("shortcuts://run-shortcut?name=" + urllib.parse.quote(name)
           + "&input=text&text=" + urllib.parse.quote(text, safe=""))
    how = "url"
    if len(url) > SC_URL_MAX and shortcut_copy(text):
        url, how = shortcut_clip_url(name), "portapapeles"
    dbg("scb", {"via": how, "bytes": len(text), "url": url[:80]})
    os.system("open " + shlex.quote(url))
    return how


SCB_NOTES = ("El análisis rápido se quedó sin tiempo", "Seguimos sin límite de tiempo", "Analizando enlace · puede tardar más")


def scb_clear():
    """--scb nunca usa native_clear (la consola es del atajo): borra con la secuencia directa."""
    with quiet("scb_clear"):
        if sys.stdout.isatty():
            sys.stdout.write(RESET + "\x1b[2J" + PURGE_SEQ + "\x1b[H" + CURSOR_SHOW)      # 1.3.2: el historial solo con DLPY_PURGE=1 · 1.0.1: sin «ESC c» (reinicio total): en a-Shell dejaba la consola en negro
            sys.stdout.flush()


def scb_diag(**kw):
    """1.0.1: deja en state/scb_debug.json por qué la escena de --scb arrancó o no (si vuelve a verse en negro, ese archivo lo dice)."""
    with quiet("scb_diag"):
        os.makedirs(STATE_DIR, exist_ok=True)
        path, data = os.path.join(STATE_DIR, "scb_debug.json"), {}
        try:
            with open(path, encoding="utf-8") as fh:             # se suma a lo anotado antes en esta ejecución
                data = json.load(fh)
        except (OSError, ValueError):
            data = {}
        if kw.get("tries") is not None:                          # el arranque de la escena empieza un registro nuevo
            data = {}
        data.update(kw)
        data["t"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=1, default=str)


def scb_scene_start(link):
    """Arranca la escena de --scb con el aviso en palabras sencillas."""
    try:
        if not link:
            return False
        from types import SimpleNamespace
        run = SimpleNamespace(link=str(link), info={}, spick=None)
        started, tries = False, 0
        for tries in (1, 2):                    # desde Atajos la ventana mide 53x0 los primeros ~2 s: se espera y se reintenta
            wait_terminal_ready(timeout=3.0, force=True)
            if scene_start(run):
                started = True
                break
        try:
            rows = term_rows()
        except (OSError, ValueError):
            rows = None
        scb_diag(scene=started, tries=tries, tty=sys.stdout.isatty(), color=USE_COLOR, truecolor=TRUECOLOR,
                 anim=ANIM, debug=DEBUG, rows=rows, width=safe_width(), ui_lines=ui_lines())
        if not started:
            return False
        scene_note(SCB_NOTES[0], hold=SCENE_DWELL + 0.5)
        scene_note(SCB_NOTES[1], hold=SCENE_DWELL + 0.3)
        return True
    except Exception as _ign:
        ignore("scb_scene_start", _ign)
        scb_diag(scene=False, error=f"{type(_ign).__name__}: {_ign}")
        return False


def shortcut_back(flags, pos):
    """`--scb LINK` (iOS):"""
    link = pos[0] if pos else None
    val = flags.get("scb")
    name = val.strip() if isinstance(val, str) and val.strip() else SHORTCUT_NAME
    with quiet("shortcut_back", OSError):
        os.makedirs(STATE_DIR, exist_ok=True)
    # sin banner, barra ni mensajes: solo se crea el JSON y se abre el atajo con él
    scene = scb_scene_start(link)               # 0.9.6: animación y aviso (si la terminal la admite)
    with quiet("shortcut_back", BaseException):
        if not is_installed("yt_dlp"):          # sin yt-dlp se instala aquí (en primer plano, sin tope)
            pip_install("yt-dlp")
            if scene:                           # 1.3.3: la escena cuenta cómo salió (✓ / ✗) antes de seguir con el análisis
                scene_note(f"yt-dlp {pkg_version('yt-dlp') or ''} · instalado".replace("  ", " ") if is_installed("yt_dlp", fresh=True)
                           else "No se pudo instalar yt-dlp", SCENE_DWELL)
    try:
        if scene:
            scene_note(SCB_NOTES[2])
        data = collect_with_timeout(link)
    except KeyboardInterrupt:
        data = shortcut_error("cancelled", "Cancelado.", link)
    write_shortcut_json(data)
    CLEAN_LATE["on"] = True
    if SCENE["on"] and scene_questions():       # hay algo que preguntar (archivos viejos): la escena cede (1.1.5: ya no; la limpieza corre en la escena)
        scene_stop()
        scb_clear()
    with quiet("shortcut_back"):
        clean_old()                             # al final del trabajo, antes de pasar al atajo
    if scene:
        scb_diag(scene=True, scene_alive=bool(SCENE["th"] is not None and SCENE["th"].is_alive()), scene_error=SCENE.get("err"),
                 json_ok=bool(data and data.get("ok", True)))
    if scene and SCENE["on"] and isinstance(data, dict) and data.get("ok") is False:     # 1.0.8: el análisis falló: se indica en D L P Y
        log_shortcutmode_error(f"{data.get('error_code') or 'error'}: {data.get('error') or ''}")
        scene_set_error(data.get("error") or "Error")
    if scene_end():                             # «Enviando a DLpy» (o el error en D L P Y) y la escena se cierra hacia el centro
        scb_clear()
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
    if v.lower() in ("audio", "audio_best"):
        k = str((pick_ or {}).get("a") or "").strip().lower()
        exact = next((f for f in audios if str(f.get("format_id")).lower() == k), None) if k else None
        if exact is not None:                      # format_id exacto de la lista «audios»
            return ("a", exact)
        if v.lower() == "audio_best":              # el de mejor calidad (del idioma pedido), sea Apple o no
            langs = [f for f in audios if k and str(f.get("language") or "und").lower() == k]
            f = best_audio(langs, ()) if langs else best_audio(audios, orig_ids)
            return ("a", f) if f is not None else None
        t = shortcut_find_track(tracks, pick_.get("a")) or (tracks[0] if tracks else None)
        return ("a", t["fmt"]) if t else None
    f = next((x for x in videos if str(x.get("format_id")) == v), None)
    return ("v", f) if f else None


SC_PICKS_MAX = 40


def shortcut_remember(key, data, path=None):
    """1.5.4: guarda de los formatos del JSON del atajo (videos y all_videos) lo que identifica su calidad, por video (los 40 más recientes)."""
    path = path or SHORTCUT_PICKS_FILE
    items, seen = [], set()
    for it in list(data.get("videos") or []) + list(data.get("all_videos") or []):
        i_ = str(it.get("id"))
        if i_ in seen or i_ in ("more", "ytdlp", "audio", "audio_best") or not it.get("height"):
            continue
        seen.add(i_)
        items.append({"id": i_, "height": it.get("height"), "fps": it.get("fps"), "hdr": bool(it.get("hdr")),
                      "compatible": bool(it.get("compatible"))})
    if not key or not items:
        return False
    db = load_json(path)
    db = db if isinstance(db, dict) else {}
    db[str(key)] = {"t": time.time(), "items": items}
    for old in sorted(db, key=lambda k_: (db[k_] or {}).get("t", 0))[:max(0, len(db) - SC_PICKS_MAX)]:
        db.pop(old, None)
    save_json(path, db, mkdir=True)
    return True


def shortcut_remembered(key, v, path=None):
    """1.5.4: lo guardado del formato `v` de ese video (id, resolución, fps, HDR, compatible) o None."""
    db = load_json(path or SHORTCUT_PICKS_FILE)
    ent = db.get(str(key)) if isinstance(db, dict) else None
    return next((it for it in ((ent or {}).get("items") or []) if str(it.get("id")) == str(v)), None)


def shortcut_similar_video(item, videos):
    """1.5.4: de `videos`, el más parecido a lo que se eligió (resolución, fps, HDR y compatibilidad, en ese orden); None si no hay datos o videos."""
    if not item or not item.get("height") or not videos:
        return None
    h, fps = int(item.get("height") or 0), int(item.get("fps") or 0)
    return min(videos, key=lambda f: (abs(int(f.get("height") or 0) - h), abs(shortcut_fps(f) - fps) if fps else 0,
                                      bool(detect_hdr(f)) != bool(item.get("hdr")), bool(apple_video(f)) != bool(item.get("compatible")),
                                      -(f.get("tbr") or 0)))


def shortcut_fallback_video(v, audios, videos, orig_ids, can_merge, item=None):
    """1.5.3: el format_id `v` del atajo ya no existe en esta consulta: (tipo, formato, cómo) del mismo formato con otra escritura (sin mayúsculas ni
    signos, o el mismo número con/sin letras; solo si es uno solo) o, 1.5.4, el más parecido al que se eligió (`item`, lo guardado del JSON) o, si
    no hay datos, el mejor compatible. None si no hay nada que ofrecer."""
    norm = lambda x: re.sub(r"[^a-z0-9]", "", str(x or "").lower())
    num = lambda x: re.sub(r"\D", "", str(x or ""))
    for key, label in ((norm, "mismo id"), (num, "mismo número")):
        k = key(v)
        if label == "mismo número" and len(k) < 4:
            continue
        hits = [f for f in videos if k and key(f.get("format_id")) == k]
        if len(hits) == 1:
            return ("v", hits[0], label)
    sim = shortcut_similar_video(item, videos)
    if sim is not None:
        same = int(sim.get("height") or 0) == int(item.get("height") or 0) and (not item.get("fps") or shortcut_fps(sim) == int(item["fps"]))
        return ("v", sim, "misma calidad" if same else "calidad más parecida")
    if not videos and not audios:
        return None
    kind, fmt = auto_best(audios, videos, orig_ids, can_merge, quiet=True)
    return (kind, fmt, "mejor compatible")


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
# Las pruebas son funciones normales (0.7.3): una por grupo [T1]…[T28] (T7–T9 y T20–T22 van juntas porque comparten
# variables) en vez de un texto compilado con exec: así editores, linters y tracebacks las ven. Cada grupo recibe
# check(nombre, obtenido, esperado). Para editarlas, busca las etiquetas [T0]…[T28] o los nombres _st_t*.
def _st_t1(check):
    """[T1] Texto, terminal y pip"""
    check("wrap no corta palabras", wrap_text("Otro video de YouTube que 'vas a ver después'. Spoiler: no.", 30),
          ["Otro video de YouTube que 'vas", "a ver después'. Spoiler: no."])
    check("wrap guiones enteros", wrap_text("uno 4K-HDR-Video dos", 12), ["uno", "4K-HDR-Video", "dos"])
    check("wrap palabra larga", wrap_text("x" * 20, 8), ["x" * 8, "x" * 8, "x" * 4])
    check("wrap emoji 2 columnas", all(dwidth(x) <= 10 for x in wrap_text("🫣 hola 🫣 mundo 🫣 otra vez", 10)), True)
    check("dwidth ansi", dwidth("\x1b[92m●\x1b[0m ab"), 4)
    check("pip args sin --no-deps", pip_args("yt-dlp", no_deps=False), ["install", "-U", "yt-dlp"])
    check("pip args con --no-deps", pip_args("yt-dlp", no_deps=True), ["install", "-U", "yt-dlp", "--no-deps"])


def _st_t2(check):
    """[T2] Barras y paneles de progreso"""
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


def _st_t3(check):
    """[T3] Versiones"""
    check("vtuple normal", vtuple("1.10.2"), (1, 10, 2))
    check("vtuple fecha", vtuple("2025.01.05"), (2025, 1, 5))
    check("vtuple None", vtuple(None), ())
    check("vtuple relleno", vtuple("1.0") == vtuple("1.0.0"), True)
    check("version_move 1.0 = 1.0.0", version_move("1.0", "1.0.0"), "igual")
    check("vtuple orden", vtuple("1.10.0") > vtuple("1.9.9"), True)


def _st_t4(check):
    """[T4] Nombres, etiquetas y bits por formato"""
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
    check("tema de sitio conocido", site_theme("www.youtube.com")[:2], ("YouTube", "YT"))
    check("tema de sitio genérico", site_theme("dumpert.nl", "Dumpert")[:2], ("Dumpert", "DU"))
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


def _st_t5(check):
    """[T5] Fallos abruptos, ffmpeg, bits, bitrate y metadatos de conversión"""
    import tempfile
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


def _st_t6(check):
    """[T6] Sondeo con ffmpeg real, rango HDR, yt-dlp auto y encoders"""
    import tempfile
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
                with quiet("selftest probe", OSError):
                    os.symlink(_ff, _lnk)
                    _old = os.environ.get("PATH", "")
                    os.environ["PATH"] = _only
                    try:
                        check("probe real sin ffprobe " + _n, (probe_video(_lnk, _f) or {}).get("bits"), _want)
                    finally:
                        os.environ["PATH"] = _old
        shutil.rmtree(_d, ignore_errors=True)
    # 1.2.5: revisar el archivo real antes de convertir (puro, sin ffmpeg)
    _pl = {"ext": "mp4", "cur": "mkv", "vsrc": "vp09", "venc": True, "hvc": False, "asrc": ["opus"], "aenc": [True], "remux": True,
           "abr": 192, "labels": ["es", "en"], "ask_enter": 90}
    _ok = {"v": {"codec": "h264", "tag": "avc1"}, "a": ["aac"], "fmt": "mov,mp4,m4a,3gp,3g2,mj2", "ext": "mp4"}
    check("refine 1.2.5: el sitio decía vp9+opus pero el archivo es h264+aac en mp4 → no se convierte", refine_plan(_pl, _ok)[0], None)
    _n1 = refine_plan(_pl, dict(_ok, a=["opus"], ext="mkv", fmt="matroska,webm"))[0]
    check("refine 1.2.5: video bueno + audio opus en mkv → sin recodificar video, solo audio y contenedor",
          (_n1["venc"], _n1["aenc"], _n1["remux"], _n1["cur"], _n1["vsrc"], "ask_enter" in _n1, _n1["labels"]),
          (False, [True], True, "mkv", "h264", False, ["es"]))
    _n2 = refine_plan(_pl, dict(_ok, v={"codec": "hevc", "tag": "hev1"}))[0]
    check("refine 1.2.5: HEVC con etiqueta hev1 en mp4 → solo remux con hvc1", (_n2["venc"], _n2["remux"], _n2["hvc"], _n2["aenc"]), (False, True, True, [False]))
    check("refine 1.2.5: HEVC hvc1 en mp4 con aac ya es compatible", refine_plan(_pl, dict(_ok, v={"codec": "hevc", "tag": "hvc1"}))[0], None)
    _n3 = refine_plan(_pl, dict(_ok, v={"codec": "vp9", "tag": None}, ext="webm", fmt="matroska,webm"))[0]
    check("refine 1.2.5: vp9 de verdad sigue recodificándose (y conserva ask_enter)", (_n3["venc"], _n3["vsrc"], _n3["ask_enter"]), (True, "vp9", 90))
    check("refine 1.2.5: remux forzado no vuelve a recodificar", refine_plan(dict(_pl, venc=False, remux_forced=True), dict(_ok, v={"codec": "vp9", "tag": None}, ext="webm"))[0]["venc"], False)
    check("refine 1.2.5: sin lectura, o sin el video esperado, el plan queda igual y sin chips",
          (refine_plan(_pl, None)[0] is _pl, refine_plan(_pl, None)[2], refine_plan(_pl, dict(_ok, v=None))[0] is _pl), (True, None, True))
    _pa = {"ext": "m4a", "cur": "webm", "vsrc": None, "venc": False, "asrc": ["opus"], "aenc": [True], "remux": True, "abr": 192}
    check("refine 1.2.5: audio solo — aac en m4a no se convierte, opus en webm sí; flac en .flac tampoco",
          (refine_plan(_pa, {"v": None, "a": ["aac"], "fmt": "mov,mp4,m4a,3gp,3g2,mj2", "ext": "m4a"})[0],
           refine_plan(_pa, {"v": None, "a": ["opus"], "fmt": "matroska,webm", "ext": "webm"})[0]["aenc"],
           refine_plan(_pa, {"v": None, "a": ["flac"], "fmt": "flac", "ext": "flac"})[0]), (None, [True], None))
    check("refine 1.2.5: ffmpeg -i también se lee (video, etiqueta, audio y contenedor)",
          parse_ffmpeg_media("Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'x.mp4':\n  Stream #0:0[0x1](und): Video: hevc (Main) (hev1 / 0x31766568), yuv420p, 160x90\n"
                             "  Stream #0:1[0x2](und): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo\n"),
          {"v": {"codec": "hevc", "tag": "hev1"}, "a": ["aac"], "fmt": "mov,mp4,m4a,3gp,3g2,mj2"})
    _sh2 = dict(SCENE)
    try:
        SCENE.update(on=True, label="x", pct=None, frac=0.0, last_error=None)
        scene_check()
        _c0 = (SCENE["label"], SCENE["check"], scene_motif_kind({"label": SCENE["label"]}))
        scene_check([("H.264", False), ("AAC", True), ("MKV", True)], "conv")
        _c1 = (SCENE["label"], SCENE["check"]["verdict"])
        scene_check_end()
        _c2 = (SCENE["check"], scene_motif_kind({"label": SCENE["label"]}))
        check("escena 1.2.5: revisión — estado, dibujo del centro y cierre",
              (_c0, _c1, _c2), (("Revisando archivo", {"items": None, "verdict": None}, "check"), ("Revisando · hay que convertir", "conv"), (None, None)))
    finally:
        SCENE.clear()
        SCENE.update(_sh2)
    _sh3, _smw = dict(SCENE), SCENE_MODE
    _thw = threading.Thread(target=time.sleep, args=(2.0,), daemon=True)
    _thw.start()
    try:
        SCENE.update(on=True, label="x", last_error=None, stop=False, th=_thw)
        globals()["SCENE_MODE"] = ("loop", None)
        _w = []
        _fut = time.time() + 1e6                                          # una medida «nueva» (posterior a la llamada)
        for _mv, _lp in ((("check", True, 0.0, _fut), False), (("check", False, None, _fut), False), (("conv", True, 0.0, _fut), False),
                         (("check", True, 0.5, _fut), True), (("check", True, 0.0, _fut), True), (("check", True, 0.0, 0.0), True)):
            SCENE["mvis"] = _mv
            _w.append(scene_wait_motif("check", loop=_lp, limit=0.1))
        SCENE["mvis"] = ("check", True, 0.0, _fut)
        globals()["SCENE_MODE"] = ("real", None)
        _w.append(scene_wait_motif("check", limit=0.1))
        globals()["SCENE_MODE"] = ("secs", 2.0)
        _w.append(scene_wait_motif("check", loop=True, limit=0.1))
        globals()["SCENE_MODE"] = ("loop", None)
        SCENE["th"] = None
        _w.append(scene_wait_motif("check", limit=0.1))
        check("escena 1.5.5: scene_wait_motif espera a que el dibujo esté visible y (con loop) a que cierre su ciclo con una medida nueva; no espera en «real», en segundos con loop ni sin hilo",
              _w, [True, False, False, False, True, False, False, False, False])
        SCENE["th"] = _thw
        _tm = []
        for _md, _mv in ((("real", None), ("check", False, None, 0.0)), (("secs", 0.0), ("check", False, None, 0.0)), (("loop", None), ("check", True, 0.0, _fut))):
            globals()["SCENE_MODE"], SCENE["mvis"] = _md, _mv
            _t0w = time.time()
            scene_wait_anim("check", 5.0 if _md[0] == "real" else 0.0)
            _tm.append(time.time() - _t0w < 0.5)
        check("escena 1.5.5: scene_wait_anim no mete pausas fijas (real: nada · segundos: lo pedido · wait: solo lo que le falta a la animación)", _tm, [True, True, True])
    finally:
        globals()["SCENE_MODE"] = _smw
        SCENE.clear()
        SCENE.update(_sh3)
    check("escena 1.2.5: la revisión manda sobre unión/guardado, pero no sobre la conversión ni D L P Y",
          [scene_motif_kind(x) for x in ({"label": "Revisando archivo"}, {"label": "Revisando", "conv": {"end": None}}, {"label": "Revisando", "brand": True})],
          ["check", "conv", "dlpy"])
    check("escena 1.2.5: la revisión va a CONV_FPS", scene_fps({"label": "Revisando archivo"}, {}, 20.0, SITE_HOLD_AT * SITE_SECS), CONV_FPS)
    _ra, _rb = (255, 120, 80), (80, 120, 255)
    _k0, _k1 = scene_check_cells(60, 6, _ra, _rb, 0.2), scene_check_cells(60, 6, _ra, _rb, 0.5)
    _kt = lambda cs, y: "".join(cs[(x, y)][0] if (x, y) in cs else " " for x in range(1, 70)).strip()
    _its = [("H.264", False), ("AAC", True), ("MKV", True)]
    _kv = scene_check_cells(60, 6, _ra, _rb, 1.0, _its, "conv")
    check("revisión 1.2.5: tres chips en tres filas (con «?» antes de leer), repetible, el haz se mueve",
          ({y for (_x, y) in _k0} >= {11, 12, 13}, _kt(_k0, 12).count("?") == 3, _k0 == scene_check_cells(60, 6, _ra, _rb, 0.2), _k0 != _k1,
           all(t in _kt(_kv, 12) for t in ("H.264", "AAC", "MKV"))), (True, True, True, True, True))
    _kok = scene_check_cells(60, 6, _ra, _rb, 1.0, _its, "ok")
    check("revisión 1.2.5: con veredicto no hay haz y el ámbar solo marca lo que hay que convertir",
          ("━" in "".join(c[0] for c in _k0.values()), "━" in "".join(c[0] for c in _kv.values()),
           len({_kv[(x, 11)][1] for (x, y) in _kv if y == 11}) > 1, len({_kok[(x, 11)][1] for (x, y) in _kok if y == 11}) == 1),
          (True, False, True, True))
    check("revisión 1.2.5: cabe en 31 columnas con textos largos, y con un solo chip (audio)",
          (all(1 <= x < 31 for (x, _y) in scene_check_cells(31, 6, _ra, _rb, 0.7, [("DOLBY", True), ("EC-3", True), ("WEBM", True)], "conv")),
           all(1 <= x < 31 for (x, _y) in scene_check_cells(31, 6, _ra, _rb, 0.7)),
           len(scene_check_cells(31, 6, _ra, _rb, 0.7, [("AAC", False)], "ok")) > 0), (True, True, True))
    _ff2 = shutil.which("ffmpeg")
    if _ff2 and shutil.which("ffprobe"):
        import subprocess as _sp2
        _d2 = tempfile.mkdtemp()
        _src = ["-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=d=1:s=160x90:r=10", "-f", "lavfi", "-i", "sine=d=1"]
        _cases = (("a.mp4", ["-c:v", "libx264", "-c:a", "aac"], None),
                  ("b.mkv", ["-c:v", "libx264", "-c:a", "libvorbis"], "conv"),
                  ("c.mp4", ["-c:v", "libx265", "-tag:v", "hev1", "-c:a", "aac"], "conv"))
        for _n, _args, _want in _cases:
            _f = os.path.join(_d2, _n)
            if _sp2.run([_ff2] + _src + _args + ["-shortest", _f], capture_output=True).returncode != 0:
                continue
            _pr = probe_file(_ff2, _f)
            _plan = dict(_pl, vsrc="vp09", venc=True)
            _got = None if refine_plan(_plan, _pr)[0] is None else "conv"
            check("probe_file + refine 1.2.5 con ffmpeg real " + _n, _got, _want)
        shutil.rmtree(_d2, ignore_errors=True)
    check("bits texto manda sobre códec", detect_bit_depth({"vcodec": "vp09.00.51.08", "format": "main10"}), 10)
    check("rango 10b HDR", range_label({"vcodec": "vp09.02.51.10", "dynamic_range": "HDR10"}), "10b HDR10")
    check("rango solo 10b", range_label({"vcodec": "hvc1.2.4.L120.90"}), "10b")
    check("h265 es HEVC: nativo en mp4 y sin recodificar el video",
          (apple_video({"vcodec": "h265", "acodec": "mp4a.40.2", "ext": "mp4"}),
           apple_plan("v", {"vcodec": "h265", "acodec": "mp4a.40.2", "ext": "mp4"}, [], None),
           apple_plan("v", {"vcodec": "h265", "acodec": "mp4a.40.2", "ext": "mkv"}, [], None)["venc"],
           apple_plan("v", {"vcodec": "h265", "acodec": "mp4a.40.2", "ext": "mkv"}, [], None)["hvc"]), (True, None, False, True))
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
    # 1.2.1: HDR al convertir
    check("hdr: tipo por el color del archivo o, si no dice, por la etiqueta",
          (hdr_kind({}, {"color_transfer": "smpte2084"}), hdr_kind({}, {"color_transfer": "arib-std-b67"}), hdr_kind({"hdr": "HDR10"}, None),
           hdr_kind({"hdr": "HLG"}, {"color_transfer": "unknown"}), hdr_kind({"hdr": "HDR10"}, {"color_transfer": "bt709"}), hdr_kind({}, None)),
          ("pq", "hlg", "pq", "hlg", None, None))
    check("hdr: conservar con 10 bits o más, tone mapping a 8, nada si no es HDR",
          (hdr_mode({"hdr_kind": "pq", "out_bits": 10}), hdr_mode({"hdr_kind": "pq", "out_bits": 12}), hdr_mode({"hdr_kind": "hlg", "out_bits": 8}),
           hdr_mode({"out_bits": 10})), ("keep", "keep", "tonemap", None))
    _ak = video_encoder_attempts({"venc": True, "vbr": 4000, "out_bits": 10, "hdr_kind": "pq", "hdr_mode": "keep"})
    check("encoders HDR conservado: etiquetas BT.2020 + PQ en todos, main10 y sin x264",
          ([a[1] for a in _ak], all("smpte2084" in " ".join(a[2]) and "bt2020nc" in a[2] for a in _ak), "main10" in " ".join(_ak[1][2])),
          (["VideoToolbox HEVC HDR", "x265 HDR"], True, True))
    _at = video_encoder_attempts({"venc": True, "vbr": 4000, "out_bits": 10, "hdr_kind": "hlg", "hdr_mode": "tonemap"})
    check("encoders HDR→SDR: filtro con arib-std-b67, 8 bits, etiquetas BT.709 y x264 al final",
          ([a[1] for a in _at], all("tonemap=tonemap=hable" in " ".join(a[2]) and "arib-std-b67" in " ".join(a[2]) and "yuv420p" in a[2]
                                    and "bt709" in a[2] for a in _at), "yuv420p10le" in " ".join(" ".join(a[2]) for a in _at)),
          (["VideoToolbox HEVC SDR", "x265 SDR", "x264 SDR"], True, False))
    _a12h = video_encoder_attempts({"venc": True, "vbr": 4000, "out_bits": 12, "hdr_kind": "pq", "hdr_mode": "keep"})
    check("encoders HDR 12 bits: x265 12, VideoToolbox 10 y x265 10, sin x264 y con etiquetas",
          ([a[1] for a in _a12h], all("smpte2084" in " ".join(a[2]) for a in _a12h)),
          (["x265 12 bits", "VideoToolbox HEVC 10 bits", "x265 10 bits"], True))
    check("hdr: el tone mapping cuesta 3× y la pregunta de bits lo dice",
          (conv_scale({"height": 1080, "fps": 30, "hdr": "HDR10", "out_bits": 8}), conv_scale({"height": 1080, "fps": 30, "hdr": "HDR10", "out_bits": 10}),
           conv_scale({"height": 1080, "fps": 30, "hdr_mode": "tonemap"}), "tone mapping" in bits_choices(10, "HDR10")[-1][1],
           "tone mapping" in bits_choices(10)[-1][1]), (3.0, 1.0, 3.0, True, False))
    check("hdr: el filtro de tone mapping pasa a BT.709 8 bits", ("tonemap=tonemap=hable" in tonemap_filter("pq"), "tin=smpte2084" in tonemap_filter("pq"),
                                                                    "tin=arib-std-b67" in tonemap_filter("hlg"), tonemap_filter("pq").endswith("format=yuv420p")),
          (True, True, True, True))
    check("hdr: ffmpeg -i también da la transferencia",
          (parse_ffmpeg_video("Stream #0:0: Video: hevc (Main 10), yuv420p10le(tv, bt2020nc/bt2020/smpte2084, progressive), 160x90, 17 kb/s") or {}).get("color_transfer"),
          "smpte2084")


def _st_t7_t9(check):
    """[T7] Columnas, sí/no y listas cortas · [T8] Variables DLPY_* y carpetas · [T9] Calidad por fila, borrado de líneas y cuándo toca comprobar"""
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
    persist_env({"DLPY_COLOR": "1", "DLPY_ROWS": "12", "HOME": "x"}, _ep)
    _e = {}
    persist_env(_e, _ep)
    check("env: se recuperan las guardadas", _e, {"DLPY_COLOR": "1", "DLPY_ROWS": "12"})
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
    check("env 1.3.0: ruta iOS en dlpy_files (fuera de la carpeta oculta) y la antigua solo para migrar",
          (env_file_path("/h"), legacy_env_file_path("/h"), os.path.dirname(env_file_path("/h")) == os.path.dirname(INTERNAL_DIR.replace(HOME, "/h"))),
          (os.path.join("/h", "Documents", "dlpy_files", "dlpy_config.json"),
           os.path.join("/h", "Documents", "dlpy_files", ".dlpy_internal", "env.json"), True))
    # 1.3.0: migración del env.json antiguo, edición con --config y supervivencia al reinicio de .dlpy_internal
    _cf, _lg = os.path.join(_ed, "files", CONFIG_NAME), os.path.join(_ed, "files", INTERNAL_NAME, ENV_NAME)
    os.makedirs(os.path.dirname(_lg))
    with open(_lg, "w", encoding="utf-8") as _f:
        json.dump({"DLPY_ROWS": "7"}, _f)
    _e = {}
    persist_env(_e, _cf, _lg)
    check("config 1.3.0: sin archivo nuevo se trae lo del env.json antiguo y se guarda en el nuevo",
          (_e, _read_env_json(_cf), ENV_STATE["migrated"]), ({"DLPY_ROWS": "7"}, {"DLPY_ROWS": "7"}, 1))
    with open(_lg, "w", encoding="utf-8") as _f:
        json.dump({"DLPY_ROWS": "9", "DLPY_COLOR": "1"}, _f)
    _e = {}
    persist_env(_e, _cf, _lg)
    check("config 1.3.0: con archivo nuevo ya no se vuelve a migrar", (_e, ENV_STATE["migrated"]), ({"DLPY_ROWS": "7"}, 0))
    config_write({}, _cf)
    _e = {}
    persist_env(_e, _cf, _lg)
    check("config 1.3.0: un archivo nuevo vacío (borrado a propósito) tampoco migra", _e, {})
    check("config 1.3.0: nombres (con o sin DLPY_, minúsculas, guiones) y los no válidos",
          [config_key(x) for x in ("rows", "dlpy_rows", "DLPY_ROWS", "scene-pip", "", "  ", "a b", "ñ")],
          ["DLPY_ROWS", "DLPY_ROWS", "DLPY_ROWS", "DLPY_SCENE_PIP", None, None, None, None])
    _ch, _er = config_edit(["rows=5", "DLPY_COLOR=1", "scene=0"], _cf)
    check("config 1.3.0: --config NOMBRE=valor guarda", (_ch, _er, _read_env_json(_cf)),
          ([("DLPY_ROWS", None, "5"), ("DLPY_COLOR", None, "1"), ("DLPY_SCENE", None, "0")], [],
           {"DLPY_ROWS": "5", "DLPY_COLOR": "1", "DLPY_SCENE": "0"}))
    _ch, _er = config_edit(["rows=5", "color="], _cf)
    check("config 1.3.0: lo igual no cuenta como cambio y NOMBRE= borra", (_ch, _er, _read_env_json(_cf)),
          ([("DLPY_COLOR", "1", None)], [], {"DLPY_ROWS": "5", "DLPY_SCENE": "0"}))
    _ch, _er = config_edit(["sin_igual", "ñ=1", "DLPY_FORGET=1", "NOVERIFY=1"], _cf)
    check("config 1.3.0: errores (sin «=», nombre no válido, de una sola ejecución) y el archivo no cambia",
          (_ch, len(_er), _read_env_json(_cf)), ([], 4, {"DLPY_ROWS": "5", "DLPY_SCENE": "0"}))
    _ri2 = os.path.join(_ed, "files", INTERNAL_NAME)
    os.makedirs(os.path.join(_ri2, "state"), exist_ok=True)
    with open(os.path.join(_ri2, "state", "version.json"), "w", encoding="utf-8") as _f:
        _f.write("{}")
    reset_internal(_ri2, os.path.join(_ed, "files"))
    check("config 1.3.0: el reinicio de .dlpy_internal (cada cambio de versión) no toca la configuración",
          (os.listdir(_ri2), _read_env_json(_cf)), ([], {"DLPY_ROWS": "5", "DLPY_SCENE": "0"}))
    check("config 1.3.0: dlpy_config.json no cuenta como descarga", (is_data_entry(CONFIG_NAME), CONFIG_NAME in RESERVED), (False, True))
    import io as _io, contextlib as _cl
    _sv_env, _out = globals()["ENV_FILE"], _io.StringIO()
    try:
        globals()["ENV_FILE"] = os.path.join(_ed, "cmd", CONFIG_NAME)
        with _cl.redirect_stdout(_out):
            _r1 = print_config(["--config", "rows=3", "DLPY_SCENE_PIP=0"])
            _t1 = _out.getvalue()
            _r2 = print_config(["--config", "--opciones"])
            _t2 = _out.getvalue()[len(_t1):]
            _r3 = print_config(["--config", "x"])
            _r4 = print_config(["--config", "--olvidar"])
        _after = _read_env_json(globals()["ENV_FILE"])
    finally:
        globals()["ENV_FILE"] = _sv_env
    check("config 1.3.0: --config guarda y lo muestra; --opciones lista las conocidas marcando las guardadas; un error da 1; --olvidar vacía",
          (_r1, "DLPY_ROWS = 3" in _t1, "DLPY_SCENE_PIP" in _t1, _r2, "DLPY_YTDLP_ARGS" in _t2, "●" in _t2, _r3, _r4, _after),
          (0, True, True, 0, True, True, 1, 0, {}))
    _rw = config_rows({"DLPY_ROWS": "3", "DLPY_RARA": "x"})
    check("config 1.3.2: filas del menú (conocidas + guardadas ajenas) y lo que significa lo escrito",
          (len(_rw), _rw[2][3], _rw[-1][0], _rw[-1][3],
           [config_choice(v, _rw) for v in ("", "q", "L", "o", "3", "rows", "dlpy_rows", "rows=5", "0", str(len(_rw) + 1), "zzz")]),
          (len(CONFIG_OPTIONS) + 1, "3", "DLPY_RARA", "x",
           [("quit",), ("quit",), ("list",), ("forget",), ("pick", _rw[2][0]), ("pick", "DLPY_ROWS"), ("pick", "DLPY_ROWS"), ("set", "rows=5"),
            ("bad", f"1-{len(_rw)}"), ("bad", f"1-{len(_rw)}"), ("bad", "nº, nombre, NOMBRE=valor, l, o o q")]))
    _sv_env, _sv_ask, _out = globals()["ENV_FILE"], globals()["ask_line"], _io.StringIO()
    _ans = iter(["2", "7", "rows=3", "zzz", "3", "-", "2", "", "q"])
    try:
        globals()["ENV_FILE"] = os.path.join(_ed, "cmd2", CONFIG_NAME)
        globals()["ask_line"] = lambda prompt, phantom=True, plain=None: next(_ans)
        with _cl.redirect_stdout(_out):
            _ri = config_interactive()
        _ci = _read_env_json(globals()["ENV_FILE"])
    finally:
        globals()["ENV_FILE"], globals()["ask_line"] = _sv_env, _sv_ask
    check("config 1.3.2: el menú interactivo elige por número, guarda, acepta NOMBRE=valor, borra con «-», deja con Enter y sale con q",
          (_ri, _ci, "DLPY_LOGKEEP = 7" in _out.getvalue(), "DLPY_ROWS = 3" in _out.getvalue(), "DLPY_ROWS borrada" in _out.getvalue(), "Sin cambios" in _out.getvalue()),
          (0, {"DLPY_LOGKEEP": "7"}, True, True, True, True))
    check("config 1.3.0: las opciones conocidas son DLPY_* válidas, sin repetir y sin las de una sola ejecución",
          (all(config_key(n) == n for n, _d, _t in CONFIG_OPTIONS), len({n for n, _d, _t in CONFIG_OPTIONS}) == len(CONFIG_OPTIONS),
           any(n in ENV_SKIP for n, _d, _t in CONFIG_OPTIONS)), (True, True, False))
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
    check("modo iOS", PLATFORM, "ios")
    check("safe_name CON no cambia", safe_name("CON"), "CON")


def _st_t10(check):
    """[T10] JavaScript, versión remota y capabilities"""
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


def _st_t11(check):
    """[T11] Reanudación, URLs de atajo, changelog en bloque y sí/no"""
    _sp = [("137", "mp4", 1000), ("140", "m4a", 50)]
    check("resume_key estable", resume_key("v", _sp), resume_key("v", list(_sp)))
    check("resume_key prefijo", resume_key("v", _sp).startswith(RESUME_PREFIX), True)
    check("resume_key otro formato", resume_key("v", _sp) != resume_key("v", [("136", "mp4", 1000), ("140", "m4a", 50)]), True)
    check("resume_key otro tamaño", resume_key("v", _sp) != resume_key("v", [("137", "mp4", 1001), ("140", "m4a", 50)]), True)
    check("resume_key otro video", resume_key("v", _sp) != resume_key("w", _sp), True)
    check("resume_key sin tamaño", resume_key("v", [("18", "mp4", None)]), resume_key("v", [("18", "mp4", 0)]))

    _vm = (VIEW_RUN["mode"], os.environ.get("DLPY_VIEW"))
    try:
        VIEW_RUN["mode"] = None
        os.environ.pop("DLPY_VIEW", None)
        _m1 = [view_mode(), view_mode(True), view_mode("VIEW"), view_mode("ashell"), view_mode("Vista"), view_mode("atajo"), view_mode("zzz"), view_mode("")]
        os.environ["DLPY_VIEW"] = "view"
        _m2 = (view_mode(), view_mode("shortcut"))
        VIEW_RUN["mode"] = "shortcut"                                   # --view=shortcut manda sobre DLPY_VIEW
        _m3 = view_mode()
        _pc = parse_cli(["--view", "https://x.y/z"])
        _pd = parse_cli(["--view=shortcut"])
        _m4 = ((_pc[0].get("view"), _pc[1]), (_pd[0].get("view"), _pd[1]))
    finally:
        VIEW_RUN["mode"] = _vm[0]
        if _vm[1] is None:
            os.environ.pop("DLPY_VIEW", None)
        else:
            os.environ["DLPY_VIEW"] = _vm[1]
    check("modo de vista 1.3.4: shortcut por omisión; view con «view», «vista», «ashell», «--view» a secas; lo desconocido es shortcut; --view manda sobre DLPY_VIEW",
          (_m1, _m2, _m3, _m4),
          (["shortcut", "view", "view", "view", "view", "shortcut", "shortcut", "shortcut"], ("view", "shortcut"), "shortcut",
           ((True, ["https://x.y/z"]), ("shortcut", []))))
    _cmds, _os_sys, _settle, _retry, _vm2 = [], os.system, globals()["settle_file"], globals()["OPEN_RETRY"], VIEW_RUN["mode"]
    try:
        _rc = [0]
        os.system = lambda c: (_cmds.append(c) or _rc[0])
        globals()["settle_file"] = lambda p: None
        globals()["OPEN_RETRY"] = 0.0
        VIEW_RUN["mode"] = "view"
        _d1 = (_deliver_platform("/x/a b.mp4", "T", quiet=True), list(_cmds))
        _cmds.clear()
        _rc[0] = 256
        _d2 = (_deliver_platform("/x/a b.mp4", "T", quiet=True), len(_cmds))
    finally:
        os.system, globals()["settle_file"], globals()["OPEN_RETRY"], VIEW_RUN["mode"] = _os_sys, _settle, _retry, _vm2
    check("modo de vista 1.3.4: view lanza «view <archivo>» (entrecomillado, sin copia de entrega ni atajo) y, si falla, reintenta una vez y lo dice",
          (_d1, _d2), ((True, ["view '/x/a b.mp4'"]), (False, 2)))
    check("modo de vista 1.3.4: la escena de cierre dice lo real: «Abriendo con view» con chip VIEW; con el atajo, «Enviando a DLpy»",
          (send_label(True), send_label(False), [scene_motif_kind(x) for x in ({"label": "Abriendo con view", "brand": True},
                                                                              {"label": "Abriendo con view", "brand": True, "last_error": "x"},
                                                                              {"label": "Abriendo con view"})],
           scene_chip_text("view"), any(o[0] == "DLPY_VIEW" for o in CONFIG_OPTIONS)),
          ("Abriendo con view", "Enviando a " + SHORTCUT_NAME, ["send", "dlpy", None], "VIEW", True))
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


def _st_t12(check):
    """[T12] Conversión rápida, update_status y --2shortcuts"""
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


def _st_t13(check):
    """[T13] ── recuperación y «abrir otra vez» ──"""
    import tempfile
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


def _st_t14(check):
    """[T14] Releases, notas de versión y changelog.md"""
    import tempfile
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
    _h = "ab" * 32
    _it = {"body": "## X\nSHA-256 (`dlpy.py`):\n\n```\n" + _h + "\n```", "assets": [
        {"name": "dlpy.py", "browser_download_url": "https://h/dl/dlpy.py", "digest": "sha256:" + "cd" * 32},
        {"name": "dlpy.py.sha256", "browser_download_url": "https://h/dl/dlpy.py.sha256"}]}
    check("hash del Release: adjunto, digest y notas", release_hash_info(_it, "dlpy.py"),
          {"sha_url": "https://h/dl/dlpy.py.sha256", "digest": "cd" * 32, "body": _h})
    check("hash del Release: ninguno", release_hash_info({"body": "nada", "assets": []}, "dlpy.py"), {})
    check("terminal: constantes con los valores de siempre",
          [RESET, WRAP_OFF, WRAP_ON, CURSOR_HIDE, CURSOR_SHOW, ERASE_EOL, ERASE_BELOW, HOME_CLEAR,
           cur_to(3, 7), cur_to(5), cur_up(2)],
          ["\x1b[0m", "\x1b[?7l", "\x1b[?7h", "\x1b[?25l", "\x1b[?25h", "\x1b[K", "\x1b[J",
           "\x1b[2J\x1b[H", "\x1b[3;7H", "\x1b[5;1H", "\x1b[2A"])
    _pr, _pm, _pd, _pw, _pi = (globals()["pip_run"], globals()["refresh_paths"], globals()["m_warn"],
                               globals()["m_info"], globals()["dbg"])
    _wr, _calls = [], []
    try:
        globals()["refresh_paths"] = lambda *a, **k: _calls.append("refresh")
        globals()["m_warn"] = lambda msg, *a, **k: _wr.append(msg)
        globals()["m_info"] = lambda *a, **k: None
        globals()["dbg"] = lambda *a, **k: None
        globals()["pip_run"] = lambda args: 0
        check("pip_install: éxito", [pip_install("x"), _wr], [True, []])
        globals()["pip_run"] = lambda args: 256
        check("pip_install: error (estado de espera 256 = código 1)", [pip_install("x"), len(_wr), "código 1" in _wr[-1]],
              [False, 1, True])
        globals()["pip_run"] = lambda args: 2
        check("pip_install: error con código directo", [pip_install("x"), "código 2" in _wr[-1]], [False, True])

        def _boom(args):
            raise OSError("sin pip")
        globals()["pip_run"] = _boom
        check("pip_install: no se puede lanzar", [pip_install("x"), "OSError" in _wr[-1]], [False, True])
        check("pip_install: siempre refresca las rutas", _calls.count("refresh"), 4)
    finally:
        (globals()["pip_run"], globals()["refresh_paths"], globals()["m_warn"], globals()["m_info"],
         globals()["dbg"]) = (_pr, _pm, _pd, _pw, _pi)
    check("hash del Release: digest mal formado", release_hash_info(
        {"assets": [{"name": "dlpy.py", "digest": "sha256:xyz"}]}, "dlpy.py"), {})
    _ov, _ofb, _env = dict(RELEASE_HASH), globals()["fresh_bytes"], os.environ.pop("DLPY_NOVERIFY", None)
    _oe, _on = globals()["m_err"], globals()["note"]
    try:
        globals()["m_err"] = lambda *a, **k: None
        globals()["note"] = lambda *a, **k: None
        _raw = b"#!dlpy.py\nVERSION = \"1.2.3\"\n"
        import hashlib as _hl
        _good = _hl.sha256(_raw).hexdigest()
        RELEASE_HASH.clear()
        check("verificar: sin hash publicado", verify_download("u0", _raw), "none")
        RELEASE_HASH["u1"] = {"body": _good}
        check("verificar: coincide (notas)", verify_download("u1", _raw), "ok")
        RELEASE_HASH["u2"] = {"body": "0" * 64}
        check("verificar: no coincide", verify_download("u2", _raw), "bad")
        globals()["fresh_bytes"] = lambda url, timeout=5, limit=None: (_good + "  dlpy.py\n").encode()
        RELEASE_HASH["u3"] = {"sha_url": "https://h/x.sha256", "digest": "0" * 64, "body": "0" * 64}
        check("verificar: el adjunto .sha256 manda sobre digest y notas", verify_download("u3", _raw), "ok")
        globals()["fresh_bytes"] = lambda url, timeout=5, limit=None: None
        check("verificar: sin adjunto cae al digest", verify_download("u3", _raw), "bad")
        os.environ["DLPY_NOVERIFY"] = "1"
        check("verificar: DLPY_NOVERIFY", verify_download("u2", _raw), "off")
        os.environ.pop("DLPY_NOVERIFY", None)
        check("DLPY_NOVERIFY no se recuerda", "DLPY_NOVERIFY" in ENV_SKIP, True)
        _srv = globals()["fresh_bytes"]
        globals()["fresh_bytes"] = lambda url, timeout=5, limit=None: _raw
        check("fetch_remote_script rechaza un hash que no coincide", fetch_remote_script(url="u2"), None)
        check("fetch_remote_script acepta uno que coincide", fetch_remote_script(url="u1"), _raw.decode())
    finally:
        RELEASE_HASH.clear()
        RELEASE_HASH.update(_ov)
        globals()["fresh_bytes"], globals()["m_err"], globals()["note"] = _ofb, _oe, _on
        if _env is not None:
            os.environ["DLPY_NOVERIFY"] = _env
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


def _st_t15(check):
    """[T15] Menú de recuperación y fallos abruptos - 0.9.9 sin backups"""
    check("menu vacío", parse_menu_choice("", 3), 0)
    check("menu n", parse_menu_choice(" N ", 3), 0)
    check("menu 2", parse_menu_choice("2", 3), 2)
    check("menu fuera de rango", parse_menu_choice("4", 3), None)
    check("menu texto", parse_menu_choice("hola", 3), None)
    check("abrupto versión nueva", should_offer_after_abrupt({"version": "0.7.6"}, ["0.7.5"]), True)
    check("abrupto versión buena", should_offer_after_abrupt({"version": "0.7.5"}, ["0.7.5"]), False)
    check("abrupto sin marca", should_offer_after_abrupt({}, []), False)
    check("backup_versions eliminado", backup_versions(), [])
    check("expired_backups eliminado", expired_backups(), [])
    check("expire_backups eliminado", expire_backups(), 0)


def _st_t16(check):
    """[T16] ── notas de la versión dentro del propio .py (solo lectura) ──"""
    _sc_src = "#!dlpy.py\n# ==== CHANGELOG ====\n# ## 1.0.1\n#\n# - Dos.\n#   sigue\n#\n# ==== FIN CHANGELOG ====\nx = 1\n"
    check("notas del script: la versión pedida", script_changelog_notes("1.0.1", _sc_src), "- Dos.\n  sigue")
    check("notas del script: otra versión", script_changelog_notes("9.9.9", _sc_src), None)
    check("notas del script: sin bloque", script_changelog_notes("1.0.1", "#!dlpy.py\nprint(1)\n"), None)
    check("markdown del bloque", changelog_block_md("# ## 1.0.1\n#\n# - Dos.\n#   sigue\n"), "## 1.0.1\n\n- Dos.\n  sigue")


def _st_t17(check):
    """[T17] ── huellas, comparación de orígenes y fallos ──"""
    import tempfile
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


def _st_t18(check):
    """[T18] Copiar/mover archivos, secciones y downgrade"""
    import tempfile
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


def _st_t19(check):
    """[T19] líneas uniformes y animaciones"""
    check("título 2 líneas", len(title_lines("palabra " * 40, 30)), 2)
    check("título termina en …", title_lines("palabra " * 40, 30)[1].endswith("…"), True)
    check("título corto igual", title_lines("Hola mundo", 30), ["Hola mundo"])
    os.environ["DLPY_ROWS"] = "12"
    check("DLPY_ROWS fuerza el tope", list_cap(), 12)
    os.environ["DLPY_ROWS"] = "0"
    check("DLPY_ROWS=0 sin tope", list_cap() > 10 ** 5, True)
    check("escala: equipo 79 % ok", scale_state(0.79, "phone"), "ok")
    check("escala: equipo 80 % alerta", scale_state(0.80, "phone"), "warn")
    check("escala: equipo 92 % crítico", scale_state(0.92, "phone"), "crit")
    check("escala: DLpy 99 % alerta", scale_state(0.99, "mine"), "warn")
    check("escala: DLpy 100 % crítico", scale_state(1.0, "mine"), "crit")
    check("escala: sin dato = ok", scale_state(None, "phone"), "ok")
    _sa = SESSION["adult"]
    try:
        SESSION["adult"] = False
        check("adulto: dominios", (is_adult("www.pornhub.com"), is_adult("youtube.com")), (True, False))
        SESSION["adult"] = True
        _cl = banner_rows(banner_width())
        check("adulto: el encabezado cabe en su ancho", max(dwidth(r) for r in _cl) <= banner_width(), True)
        check("adulto: el encabezado no lleva etiqueta +18 propia", "+18" in _ANSI_RE.sub("", _cl[0]), False)
        check("adulto: ya no existe la animación/etiqueta propia", [n in globals() for n in ("adult_intro", "adult_scene", "adult_badge", "ADULT_BADGE")], [False] * 4)
        _ths = [site_theme(h) for h in ("www.pornhub.com", "xvideos.com", "es.xhamster.com", "sitio-xxx-raro.com")]
        check("adulto: tienen nombre, sigla y colores del sitio (los conocidos y los desconocidos)",
              all(len(t) == 4 and t[2] != t[3] and all(0 <= v <= 255 for v in t[2] + t[3]) for t in _ths), True)
        check("adulto: los conocidos usan su tema propio", [t[0] for t in _ths[:3]], ["Pornhub", "XVideos", "xHamster"])
    finally:
        SESSION["adult"] = _sa
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


def _st_t20_t22(check):
    """[T20] ── Modo atajo ── · [T21] ── Menú del atajo: formatos sin resolución, bitrate, tamaño aproximado y emojis ── · [T22] ── Modo atajo: tope de tiempo y aviso ──"""
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
    check("atajo: orden mejor→peor, solo audio y «Ver todos» al final", [v["id"] for v in _sp["videos"]],
          ["299", "137", "136", "18", "audio", "more"])
    check("atajo: listas paralelas", len(_sp["video_labels"]) == len(_sp["video_ids"]) == len(_sp["video_audio_step"]), True)
    check("atajo: etiquetas con número", [l.split(" · ")[0] for l in _sp["video_labels"]], ["1", "2", "3", "4", "5", "6"])
    check("atajo: pasos de audio", _sp["video_audio_step"], ["full", "full", "full", "none", "track", "none"])
    check("ver todos: hay más (el vp9 1080p30 estaba oculto)", [_sp["has_more"], _sp["more_count"], _sp["more_label"]],
          [True, 1, "\u25b8 Ver todos (+1)"])
    check("ver todos: lista completa con el formato oculto y numerada",
          [_sp["all_video_ids"], [l.split(" · ")[0] for l in _sp["all_video_labels"]]],
          [["299", "137", "248", "136", "18", "audio"], ["1", "2", "3", "4", "5", "6"]])
    check("ver todos: listas paralelas y mejor marcado",
          [len(_sp["all_video_labels"]) == len(_sp["all_video_ids"]) == len(_sp["all_video_audio_step"]),
           _sp["all_default_video"], _sp["more_id"] in SC_MORE_IDS], [True, 1, True])
    _mp0 = build_shortcut_payload({"formats": [_fi["formats"][0], _fi["formats"][5]]}, "u", True)
    check("ver todos: sin ocultos no aparece", [_mp0["has_more"], _mp0["more_label"], _mp0["all_video_ids"]],
          [False, None, []])
    check("ver todos: última fila del menú del atajo", [_sp["video_ids"][-1], _sp["video_labels"][-1], _sp["video_ids"][-1] == _sp["more_id"]],
          ["more", "6 \u00b7 \u25b8 Ver todos (+1)", True])
    _big = {"duration": 60, "formats": [{"format_id": f"v{i}", "ext": "mp4", "vcodec": f"avc{i}", "acodec": "none",
                                         "height": 1080, "fps": 30, "tbr": 1000 + i} for i in range(120)]}
    _bp = build_shortcut_payload(_big, "u", True)
    check("ver todos: con cientos de formatos el JSON no crece (solo v=more)",
          [_bp["has_more"], _bp["more_count"], _bp["all_in_script"], _bp["all_video_ids"], len(_bp["video_ids"]),
           _bp["video_ids"][-1]], [True, 119, True, [], 2, "more"])
    check("ver todos: sin ocultos no hay fila extra", [_mp0["video_ids"][-1] != "more", _mp0["all_in_script"]], [True, False])
    check("ver todos: v=more se reconoce y no es un formato",
          [parse_shortcut_pick("v=more")["v"] in SC_MORE_IDS,
           shortcut_resolve_video({"v": "more"}, [], [], [], set(), True)], [True, None])
    check("atajo: 2 idiomas, original primero", [_sp["multi_lang"], _sp["track_ids"], _sp["default_track"]],
          [True, ["es-US", "en-US"], 1])
    check("atajo: adicionales sin la elegida", _sp["extra_menu"], {"1": [_sp["track_labels"][1]], "2": [_sp["track_labels"][0]]})
    check("atajo: duración", _sp["duration_text"], "1:02:05")
    check("audios: listados todos, en paralelo", [len(_sp["audio_labels"]), len(_sp["audio_ids"]), len(_sp["audios"])], [3, 3, 3])
    check("audios: el original primero, el mejor con ★", [_sp["audio_ids"][0], _sp["audios"][0]["best"], _sp["default_audio"]],
          ["140-0", True, 1])
    check("audios: solo uno marcado y la etiqueta lo dice", [sum(a["best"] for a in _sp["audios"]), _sp["audio_labels"][0].startswith("1 · ★ ")],
          [1, True])
    check("audios: gana el de mayor bitrate aunque no sea de Apple",
          best_audio([{"format_id": "a", "ext": "webm", "acodec": "opus", "abr": 130},
                      {"format_id": "b", "ext": "m4a", "acodec": "mp4a.40.2", "abr": 129}])["format_id"], "a")
    check("audios: a igual bitrate gana el de Apple",
          best_audio([{"format_id": "a", "ext": "webm", "acodec": "opus", "abr": 130},
                      {"format_id": "b", "ext": "m4a", "acodec": "mp4a.40.2", "abr": 130}])["format_id"], "b")
    _mo = build_shortcut_payload({"formats": [
          {"format_id": "a", "ext": "webm", "vcodec": "none", "acodec": "opus", "abr": 160},
          {"format_id": "b", "ext": "m4a", "vcodec": "none", "acodec": "mp4a.40.2", "abr": 128}]}, "u", True)
    check("solo audio: Apple y mejor por separado", [_mo["video_ids"], _mo["videos"][-1]["ask_convert"]],
          [["audio", "audio_best"], True])
    check("solo audio: etiquetas Apple / mejor", [_mo["video_labels"][0], _mo["video_labels"][1]],
          ["1 \u00b7 \u266b Solo audio \u00b7 Apple \u00b7 m4a mp4a 128k \uf8ff", "2 \u00b7 \u266b \u2605 Solo audio \u00b7 mejor \u00b7 webm opus 160k"])
    check("solo audio: mejor resuelve opus, Apple resuelve m4a",
          [shortcut_resolve_video({"v": "audio_best"}, *(lambda f: (f[1], f[2], build_tracks(f[1], set())[0]))(split_formats({"formats": [
              {"format_id": "a", "ext": "webm", "vcodec": "none", "acodec": "opus", "abr": 160},
              {"format_id": "b", "ext": "m4a", "vcodec": "none", "acodec": "mp4a.40.2", "abr": 128}]})), set(), True)[1]["format_id"],
           shortcut_resolve_video({"v": "audio"}, *(lambda f: (f[1], f[2], build_tracks(f[1], set())[0]))(split_formats({"formats": [
              {"format_id": "a", "ext": "webm", "vcodec": "none", "acodec": "opus", "abr": 160},
              {"format_id": "b", "ext": "m4a", "vcodec": "none", "acodec": "mp4a.40.2", "abr": 128}]})), set(), True)[1]["format_id"]],
          ["a", "b"])
    check("audios: ask_convert si el mejor no es de Apple", [_sp["ask_convert"], _sp["default_audio"]], [False, 1])
    check("audios: ask_convert true con opus mejor", build_shortcut_payload({"formats": [
          {"format_id": "a", "ext": "webm", "vcodec": "none", "acodec": "opus", "abr": 160},
          {"format_id": "b", "ext": "m4a", "vcodec": "none", "acodec": "mp4a.40.2", "abr": 128}]}, "u", True)["ask_convert"], True)
    check("audios: mucho más bitrate gana al compatible",
          best_audio([{"format_id": "a", "ext": "webm", "acodec": "opus", "abr": 160},
                      {"format_id": "b", "ext": "m4a", "acodec": "mp4a.40.2", "abr": 48}])["format_id"], "a")
    check("audios: sin audios", [best_audio([]), shortcut_audio_items([], set())], [None, []])
    check("manzana mordida en lugar del punto verde", ["\U0001f7e2" in "".join(_sp["video_labels"] + _sp["track_labels"] + _sp["audio_labels"]),
          "\uf8ff" in "".join(_sp["video_labels"] + _sp["audio_labels"])], [False, True])
    check("atajo: JSON ASCII de ida y vuelta", json.loads(json.dumps(_sp, ensure_ascii=True)), _sp)
    _sp2 = build_shortcut_payload(_fi, "https://x/y", False)
    check("atajo: sin ffmpeg no se pregunta audio", set(_sp2["video_audio_step"]) - {"track"}, {"none"})
    check("atajo: sin formatos", build_shortcut_payload({"formats": []}, "u", True)["error_code"], "no_formats")
    _fa, _au, _vi = split_formats(_fi)
    _tr, _ = build_tracks(_au, mark_originals(_au))
    check("atajo: resuelve video", shortcut_resolve_video({"v": "299"}, _au, _vi, _tr, set(), True)[1]["format_id"], "299")
    check("atajo: solo audio por format_id exacto",
          shortcut_resolve_video({"v": "audio", "a": "251-1"}, _au, _vi, _tr, set(), True)[1]["format_id"], "251-1")
    check("atajo: resuelve solo audio por idioma",
          shortcut_resolve_video({"v": "audio", "a": "en-US"}, _au, _vi, _tr, set(), True)[0:1], ("a",))
    check("atajo: formato que ya no existe", shortcut_resolve_video({"v": "zzz"}, _au, _vi, _tr, set(), True), None)
    _fv = [{"format_id": "1234v", "height": 720, "vcodec": "avc1", "acodec": "none", "ext": "mp4"},
           {"format_id": "5678v", "height": 1080, "vcodec": "avc1", "acodec": "none", "ext": "mp4"},
           {"format_id": "HD", "height": 480, "vcodec": "avc1", "acodec": "aac", "ext": "mp4"}]
    _fb = lambda v_, vs_=_fv: (lambda r_: None if r_ is None else (r_[1]["format_id"], r_[2]))(shortcut_fallback_video(v_, [], vs_, set(), True))
    _vf = [{"format_id": "a1", "height": 720, "fps": 30, "vcodec": "avc1", "acodec": "none", "ext": "mp4", "tbr": 1500},
           {"format_id": "a2", "height": 1080, "fps": 30, "vcodec": "avc1", "acodec": "none", "ext": "mp4", "tbr": 3000},
           {"format_id": "a3", "height": 1080, "fps": 60, "vcodec": "avc1", "acodec": "none", "ext": "mp4", "tbr": 4500}]
    import tempfile as _tmpf
    _tf = os.path.join(_tmpf.mkdtemp(prefix="dlpy_t_"), "p.json")
    _ok = shortcut_remember("fb:1", {"videos": [{"id": "x720", "height": 720, "fps": 30, "compatible": True}, {"id": "more", "height": None}],
                                     "all_videos": [{"id": "x1080", "height": 1080, "fps": 60, "hdr": False, "compatible": True}, {"id": "x720", "height": 720}]}, _tf)
    _it = shortcut_remembered("fb:1", "x1080", _tf)
    check("atajo 1.5.4: se guarda la lista del JSON (sin «more» ni duplicados) y se recupera lo elegido; id o video desconocido → None",
          (_ok, _it, shortcut_remembered("fb:1", "zzz", _tf), shortcut_remembered("otro", "x1080", _tf), len(load_json(_tf)["fb:1"]["items"])),
          (True, {"id": "x1080", "height": 1080, "fps": 60, "hdr": False, "compatible": True}, None, None, 2))
    _rs = lambda h_, f_, vs_=_vf: (lambda r_: (r_[1]["format_id"], r_[2]))(shortcut_fallback_video("zz", [], vs_, set(), True, {"id": "q", "height": h_, "fps": f_, "hdr": False, "compatible": True}))
    check("atajo 1.5.4: sin el id, la calidad elegida se conserva (misma resolución y fps, o la más cercana); sin datos, el mejor compatible",
          [_rs(1080, 60), _rs(1080, 30), _rs(720, 30), _rs(1440, 60), _rs(700, 30), shortcut_fallback_video("zz", [], _vf, set(), True)[2]],
          [("a3", "misma calidad"), ("a2", "misma calidad"), ("a1", "misma calidad"), ("a3", "calidad más parecida"), ("a1", "calidad más parecida"), "mejor compatible"])
    check("atajo 1.5.3: id que cambió → mismo id con otra escritura, mismo número, o el mejor compatible; nunca la lista",
          [_fb("hd"), _fb("1234"), _fb("1234_x"), _fb("999"), _fb("12"), _fb("zzz", [dict(_fv[0], format_id="1234v"), dict(_fv[0], format_id="1234-1")]), _fb("zzz", [])],
          [("HD", "mismo id"), ("1234v", "mismo número"), ("1234v", "mismo número"), ("5678v", "mejor compatible"), ("5678v", "mejor compatible"),
           ("1234v", "mejor compatible"), None])
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
        check("scb: JSON sin videos/tracks/audios y con el discriminador",
              ("videos" in _body, "tracks" in _body, "audios" in _body, "audio_labels" in _body, _body["dlpy"]),
              (False, False, False, True, "shortcutmode"))
        check("scb: la entrada del atajo es compacta", urllib.parse.unquote(_u.split("&text=")[1]).startswith('{"dlpy":"shortcutmode"'), True)
        SC_URL_MAX = 100
        shortcut_send(_sp, "DLpy")
        check("scb: si no cabe en la URL va por el portapapeles", _sent[-1].endswith("input=clipboard'"), True)
    finally:
        os.system, shortcut_copy, SC_URL_MAX = _os_sys, _copy, _sc


def _st_t23(check):
    """[T23] ── Reinicio de .dlpy_internal al cambiar de versión ──"""
    import tempfile
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


def _st_t24(check):
    """[T24] ── Símbolos de mensaje y tarjetas (cambio de versión y resultado) ──"""
    _seen, _say_old = [], globals()["_say"]
    globals()["_say"] = lambda color, msg, mark=None: _seen.append((color, mark))
    try:
        m_ok("x"); m_warn("x"); m_err("x"); m_info("x"); m_check("x")
    finally:
        globals()["_say"] = _say_old
    check("mensajes: un símbolo por tipo", _seen,
          [("mint", "✓"), ("amber", "!"), ("red", "✕"), ("orange", None), ("mint", "✓")])
    _plain = lambda rows: [_ANSI_RE.sub("", r) for r in rows]
    _bw, _br = banner_width(), _plain(banner_rows(banner_width()))
    check("encabezado: 3 líneas fijas que caben", (len(_br) >= 3, max(dwidth(x) for x in _br) <= _bw), (True, True))
    check("encabezado: título y versión", _br[0].startswith(f"▍DLpy v{VERSION}"), True)
    check("encabezado: la barra de espacio mide lo previsto", dwidth(_ANSI_RE.sub("", storage_bar(20, 0.5, 0.25))), 20)
    check("encabezado: alto registrado", (banner_height() >= 3, card_inner()), (True, _bw))
    check("grad: un código por tramo, no por letra", grad("x" * 60).count("[38;2;") <= 12, True)
    check("tarjeta final: vídeo",
          _plain(result_card_rows("Ejemplo de video largo", {"video": {"res": "1080p", "codec": "avc1.640028"}},
                                  412 * 1024 ** 2, 3725, "Ejemplo.mp4", 36)),
          ["✓ Listo", "▍ Ejemplo de video largo", "  1080p · H.264 · 412 MB · 1:02:05", "  dlpy_files/Ejemplo.mp4"])
    check("tarjeta final: audio convertido",
          _plain(result_card_rows("Canción", {"converted": True, "video": None, "tracks": [{"codec": "mp4a.40.2", "abr": 128}]},
                                  5 * 1024 ** 2, 215, "Canción.m4a", 36)),
          ["✓ Listo · convertido", "▍ Canción", "  AAC 128 kbps · 5.0 MB · 3:35", "  dlpy_files/Canción.m4a"])
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


def _st_t25(check):
    """[T25] 0.9.9: limpieza 10 días -> trash"""
    import tempfile
    g = globals()
    names = ("FILES_DIR", "INTERNAL_DIR", "STATE_DIR", "INDEX_FILE", "HISTORY_FILE", "TRASH_DIR", "DELIVERY_DIR")
    saved = {k: g[k] for k in names}
    tmp = tempfile.mkdtemp(prefix="dlpy_t25_")
    try:
        files = os.path.join(tmp, "dlpy_files")
        g["FILES_DIR"] = files
        g["INTERNAL_DIR"] = os.path.join(files, ".dlpy_internal")
        g["STATE_DIR"] = os.path.join(g["INTERNAL_DIR"], "state")
        g["INDEX_FILE"] = os.path.join(g["STATE_DIR"], "index.json")
        g["HISTORY_FILE"] = os.path.join(g["STATE_DIR"], "downloads.json")
        g["TRASH_DIR"] = os.path.join(files, ".trash")
        g["DELIVERY_DIR"] = os.path.join(g["INTERNAL_DIR"], "delivery")
        for d in (g["STATE_DIR"], g["TRASH_DIR"], os.path.join(files, "sub")):
            os.makedirs(d)
        now, day = time.time(), 86400
        def mk(rel, days, size=10):
            p = os.path.join(files, rel)
            with open(p, "wb") as fh:
                fh.write(b"x" * size)
            os.utime(p, (now - days * day, now - days * day))
            return p
        mk("viejo.mp4", 15)
        mk("nuevo.mp4", 5)
        mk("convertido.m4a", 15)
        mk("suelto.mp3", 12)
        mk("sub/otro.mp4", 11)
        mk("notas.txt", 50)
        mk(".dlpy_internal/x.mp4", 60)
        save_json(g["INDEX_FILE"], {
            "a:1": {"file": "viejo.mp4", "date": int(now - 15 * day)},
            "a:2": {"file": "nuevo.mp4", "date": int(now - 5 * day)},
            "a:3": {"file": "convertido.m4a", "date": int(now - 2 * day)}})
        rows = old_downloads(now)
        check("antiguos 0.9.9: solo >10 días", [os.path.relpath(r[0], files) for r in rows], ["viejo.mp4", "suelto.mp3", os.path.join("sub", "otro.mp4")])
        check("antiguos: edad", [int(r[1] // day) for r in rows], [15, 12, 11])
        check("antiguos: umbral 13d", [os.path.basename(r[0]) for r in old_downloads(now, 13 * day)], ["viejo.mp4"])
        check("clean_old mueve a trash", clean_old() > 0, True)
        check("files sin viejos", "viejo.mp4" not in os.listdir(files), True)
        check("trash contiene", len(os.listdir(g["TRASH_DIR"])) >= 3, True)
        mk("escena.mp4", 20)                                       # 1.1.5: con escena, la limpieza no la cede y la deja en «Limpiando»
        _sc5, _hold5 = dict(SCENE), SCENE_CLEAN_SECS
        try:
            globals()["SCENE_CLEAN_SECS"] = 0.0
            SCENE.update(on=True, label="Descargando video", last_error=None, pct=None, brand=False, conv=None)
            _n5 = clean_old()
            check("clean_old 1.1.5: dentro de la escena no la cede y deja el dibujo de limpieza",
                  (_n5 > 0, SCENE["on"], SCENE["label"].startswith("Limpiando"), scene_motif_kind(SCENE), SCENE.get("clean") == _n5),
                  (True, True, True, "clean", True))
        finally:
            SCENE.clear()
            SCENE.update(_sc5)
            globals()["SCENE_CLEAN_SECS"] = _hold5
        cv = os.path.join(files, "Charla.mp4")
        with open(cv, "w") as fh:
            fh.write("ORIGINAL")
        d1 = unique_path(cv)
        tmp_cv = cv + ".tmp"
        with open(tmp_cv, "w") as fh:
            fh.write("CONVERTIDO!")
        os.replace(tmp_cv, cv)
        check("entrega: vieja sigue", open(d1).read(), "ORIGINAL")
        d2 = unique_path(cv)
        with open(d2) as fh:
            check("entrega: nueva convertida", fh.read(), "CONVERTIDO!")
        check("entrega: vieja no existe", (os.path.exists(d1), len(os.listdir(g["DELIVERY_DIR"]))), (False, 1))
        with open(os.path.join(files, "Otra.mp4"), "w") as fh:
            fh.write("x")
        unique_path(os.path.join(files, "Otra.mp4"))
        check("entrega: otros no se tocan", len(os.listdir(g["DELIVERY_DIR"])), 2)
        check("entrega: puntos no cuentan",
              [delivery_name("Video by qrcode.i.mp4"), delivery_name("Charla.mp4"), delivery_title("Video by qrcode.i"),
               os.path.splitext(delivery_name("a.b.c.mp4"))[1]],
              ["Video by qrcode\u2024i.mp4", "Charla.mp4", "Video by qrcode\u2024i", ".mp4"])
        import io as _io
        _fh0, _buf0 = DEBUG_LOG["fh"], _io.StringIO()
        DEBUG_LOG["fh"] = _buf0
        try:
            _out0, _err0 = _io.StringIO(), _io.StringIO()
            _t1, _t2 = _LogTee(_out0, ""), _LogTee(_err0, "! ")
            _t1.write("\x1b[31mrojo\x1b[0m\n50%\r80%\r100%\nsin salto")
            _t1.write(" ni fin\n\x1b[2K\x1b[Hlimpio\r\n")
            _t2.write("Traceback x\n")
            _got = [l.split("] ", 1)[1] for l in _buf0.getvalue().splitlines()]
        finally:
            DEBUG_LOG["fh"] = _fh0
        check("log debug", [_got, _out0.getvalue().startswith("\x1b[31mrojo")],
              [["rojo", "100%", "sin salto ni fin", "limpio", "! Traceback x"], True])
        check("log: logs no cuenta", [is_data_entry("logs"), is_data_entry("Charla.mp4")], [False, True])
        check("drop_deliveries", (drop_deliveries("Charla.mp4"), len(os.listdir(g["DELIVERY_DIR"]))), (1, 1))
    finally:
        for k, v in saved.items():
            g[k] = v
        shutil.rmtree(tmp, ignore_errors=True)


def _st_t26(check):
    """[T26] 0.9.9: sin backups, con trash (10d -> trash, 30d en trash -> borrado)"""
    import tempfile
    from types import SimpleNamespace as NS
    g = globals()
    check("menú: Enter = ninguna", parse_resume_choice("", 3), ("none", []))
    check("menú: T = todas", parse_resume_choice("T", 3), ("run", [0, 1, 2]))
    check("menú: números y rango", parse_resume_choice("1, 3 2-3", 4), ("run", [0, 1, 2]))
    check("menú: descartar", [parse_resume_choice("d 2", 3), parse_resume_choice("D t", 2)],
          [("discard", [1]), ("discard", [0, 1])])
    check("menú: inválidas", [parse_resume_choice(x, 3)[0] for x in ("0", "4", "abc", "d", "2-9")], ["bad"] * 5)
    check("modo temprano: audio / con audio", [site_mode(NS(spick={"v": "audio"})), site_mode(NS(spick={"v": "137"}))],
          ["audio", "both"])
    check("modo con análisis sigue igual", site_mode(NS(info={"is_live": True})), "live")
    saved_t, saved_a = dict(THEME), SESSION["adult"]
    try:
        THEME.update({"a": None, "b": None, "full": None})
        check("tema: sin sitio, naranja→magenta", theme_rgb(), (PALETTE["orange"][0], PALETTE["magenta"][0]))
        THEME.update({"a": (1, 2, 3), "b": (4, 5, 6)})
        SESSION["adult"] = False
        check("tema: colores del sitio", theme_rgb(), ((1, 2, 3), (4, 5, 6)))
        SESSION["adult"] = True
        check("tema: el sitio adulto también usa sus colores", theme_rgb(), ((1, 2, 3), (4, 5, 6)))
        SESSION["adult"] = False
        reset_site_state()
        check("reset del tema", (THEME["a"], THEME["full"], SESSION["tag"]), (None, None, None))
    finally:
        THEME.update(saved_t)
        SESSION["adult"] = saved_a
    saved = {k: g[k] for k in ("WORK_ROOT", "TRASH_DIR", "FILES_DIR")}
    tmp = tempfile.mkdtemp(prefix="dlpy_t26_")
    try:
        g["WORK_ROOT"] = os.path.join(tmp, "work")
        g["TRASH_DIR"] = os.path.join(tmp, "trash")
        g["FILES_DIR"] = os.path.join(tmp, "files")
        for d in (g["WORK_ROOT"], g["TRASH_DIR"], g["FILES_DIR"]):
            os.makedirs(d)
        now, day = time.time(), 86400
        def mk_old(name, days):
            p = os.path.join(g["FILES_DIR"], name)
            with open(p, "w") as fh:
                fh.write("x")
            os.utime(p, (now - days*day, now - days*day))
            return p
        mk_old("nuevo.mp4", 1)
        old_file = mk_old("viejo.mp4", 11)
        check("trash: detecta viejo >10d", len(old_downloads(now, TRASH_SECS)), 1)
        check("trash: move_to_trash", move_to_trash(old_file), True)
        check("trash: viejo ya no está en files", os.path.exists(old_file), False)
        check("trash: está en trash", len(os.listdir(g["TRASH_DIR"])), 1)
        trash_file = os.path.join(g["TRASH_DIR"], os.listdir(g["TRASH_DIR"])[0])
        os.utime(trash_file, (now - 31*day, now - 31*day))
        check("trash: detecta expirado >30d", len(trash_expired(now)), 1)
        check("trash: clean_trash borra", clean_trash(), 1)
        check("trash: queda vacío", os.listdir(g["TRASH_DIR"]), [])
        # 1.1.8: lo que ya estaba en la papelera (fecha vieja) empieza a contar sus 30 días una sola vez desde hoy
        _old_stamp, g["TRASH_STAMP_FILE"] = g["TRASH_STAMP_FILE"], os.path.join(tmp, "trash_stamp.json")
        _pre = os.path.join(g["TRASH_DIR"], "previo.mp4")
        with open(_pre, "w") as fh:
            fh.write("x")
        os.utime(_pre, (now - 90 * day, now - 90 * day))
        check("1.1.8: migración: sin marca expiraría", len(trash_expired(now)), 1)
        check("1.1.8: migración: marca lo que había", migrate_trash_dates(), 1)
        check("1.1.8: migración: ya no expira y no se repite", (len(trash_expired(now)), migrate_trash_dates()), (0, 0))
        os.remove(_pre)
        g["TRASH_STAMP_FILE"] = _old_stamp
        # 1.1.6: un archivo viejo recién movido no expira; y trash dentro de FILES_DIR no se escanea como descarga
        g["TRASH_DIR"] = os.path.join(g["FILES_DIR"], "trash")
        os.makedirs(g["TRASH_DIR"], exist_ok=True)
        f2 = mk_old("otro.mp4", 40)
        check("1.1.6: move_to_trash de un archivo de 40 d", move_to_trash(f2), True)
        check("1.1.6: recién movido no expira en la papelera", len(trash_expired(now)), 0)
        inside = os.path.join(g["TRASH_DIR"], os.listdir(g["TRASH_DIR"])[0])
        os.utime(inside, (now - 15*day, now - 15*day))
        check("1.1.6: trash dentro de dlpy_files no cuenta como descarga", [p for p in _scan_downloads() if os.sep + "trash" + os.sep in p], [])
        check("1.1.6: clean_old no reprocesa la papelera", len(old_downloads(now, TRASH_SECS)), 0)
        shutil.rmtree(g["TRASH_DIR"], ignore_errors=True)
        g["TRASH_DIR"] = os.path.join(tmp, "trash")
        check("backups eliminados: backup_versions vacío", backup_versions(), [])
        check("backups eliminados: expired_backups vacío", expired_backups(), [])
        check("backups eliminados: expire_backups 0", expire_backups(), 0)
        g2 = {k: g[k] for k in ("INTERNAL_DIR", "FILES_DIR")}
        tmp2 = tempfile.mkdtemp(prefix="dlpy_t26b_")
        try:
            g["INTERNAL_DIR"] = os.path.join(tmp2, "internal")
            g["FILES_DIR"] = os.path.join(tmp2, "files")
            os.makedirs(g["INTERNAL_DIR"])
            os.makedirs(g["FILES_DIR"])
            with open(os.path.join(g["INTERNAL_DIR"], "x.tmp"), "w") as fh:
                fh.write("x")
            with open(os.path.join(g["FILES_DIR"], "video.mp4"), "w") as fh:
                fh.write("x")
            check("0.9.9 archive_previous conserva files", archive_previous("0.9.8", "0.9.8"), True)
            check("0.9.9 internal borrado y recreado", os.path.isdir(g["INTERNAL_DIR"]), True)
            check("0.9.9 files conservado", os.path.exists(os.path.join(g["FILES_DIR"], "video.mp4")), True)
        finally:
            for k,v in g2.items():
                g[k]=v
            shutil.rmtree(tmp2, ignore_errors=True)
    finally:
        for k, v in saved.items():
            g[k] = v
        shutil.rmtree(tmp, ignore_errors=True)


def _st_t27(check):
    """[T27] ── 0.9.3/0.9.4: escena continua de --shortcutpick (textos, transiciones, silencio de stdout, pistas, título y cierre) ──"""
    import io
    check("escena: procesos de yt-dlp", [scene_pp_text(x) for x in ("FFmpegMerger", "AppleConvert", "FFmpegVideoRemuxer",
                                                                      "TrackFix", "FFmpegMetadata", "")],
          ["Uniendo pistas", "Convirtiendo", "Convirtiendo", "Ajustando pistas", "Finalizando", "Finalizando"])
    check("escena: stream de video o de audio", [scene_kind({"info_dict": {"height": 1080}}),
                                                  scene_kind({"info_dict": {"vcodec": "avc1.64"}}),
                                                  scene_kind({"info_dict": {"vcodec": "none", "acodec": "mp4a"}}),
                                                  scene_kind({})], ["video", "video", "audio", "audio"])
    cols = scene_cols("Hola mundo", 20)
    check("escena: texto centrado sin espacios", (min(cols), max(cols), 25 in cols), (15, 24, False))
    wide = scene_cols("a日b", 20)
    check("escena: carácter ancho deja su columna cubierta", sorted(wide.items()), [(18, "a"), (19, "日"), (20, "\0"), (21, "b")])
    c0, c1 = scene_cols("YOUTUBE", 20), scene_cols("Pan casero", 20)
    start, end = scene_morph(c0, c1, 0.0, 3), scene_morph(c0, c1, 1.0, 3)
    check("escena: la transición empieza en el viejo y acaba en el nuevo",
          ("".join(v[0] for _x, v in sorted(start.items())), "".join(v[0] for _x, v in sorted(end.items()))),
          ("YOUTUBE", "Pancasero"))
    mid = scene_morph(c0, c1, 0.5, 3)
    check("escena: a mitad de camino hay ruido y es repetible", (any(v[1] == 1 for v in mid.values()), mid),
          (True, scene_morph(c0, c1, 0.5, 3)))
    wend = scene_morph(scene_cols("x", 20), wide, 1.0, 0)
    check("escena: el ancho final no cambia (la columna cubierta no escribe nada)",
          sum(dwidth(v[0]) for v in wend.values()), dwidth("a日b"))
    real, mute = io.StringIO(), None
    mute = _SceneMute(real)
    mute.write("no sale")
    mute.open = True
    mute.write("sale")
    check("escena: stdout silenciado hasta abrirlo", real.getvalue(), "sale")
    check("escena: sin escena los avisos y el texto no cambian", (SCENE["on"], scene_status("x"), scene_title("t"),
                                                                  scene_progress(5.0), scene_stop()),
          (False, None, None, None, False))
    # 0.9.4: etiqueta de pista (varios audios/idiomas), título «D L P Y», cierre y barrido de la regla
    check("escena: etiqueta de pista con varias pistas",
          [scene_stream_label("video", 1, 3), scene_stream_label("audio", 2, 3, "es-US"), scene_stream_label("audio", 3, 3, "en-US"),
           scene_stream_label("audio", 2, 3), scene_stream_label("audio", 1, 1, "es"), scene_stream_label("video", 1, 1)],
          ["Descargando video 1/3", "Descargando audio es-US 2/3", "Descargando audio en-US 3/3", "Descargando audio 2/3",
           "Descargando audio es", "Descargando video"])
    check("escena: idioma del stream", [scene_lang({"info_dict": {"language": "es-US"}}), scene_lang({"info_dict": {"language": "und"}}),
                                         scene_lang({"info_dict": {}}), scene_lang({})], ["es-US", None, None, None])
    S = {"geo": (60, 24, 6, 17), "a": (255, 140, 0), "b": (220, 40, 180), "name": "YouTube", "mode": "video", "title_raw": "Pan casero",
         "brand": False, "busy": False, "label": "Descargando audio es-US 2/3", "pct": 45, "shown": 0.5, "k_out": None}
    st = scene_state()

    def row(cells, y):
        return "".join(cells[(x, y)][0] if (x, y) in cells else " " for x in range(1, 61)).strip()

    t = SITE_HOLD_AT * SITE_SECS
    scene_cells(S, st, t, t + 0.01, 1)                                  # primer cuadro tras la intro: el sitio
    c = scene_cells(S, st, t, t + 2.0, 50)
    check("escena: el título del video", row(c, 8), "Pan casero")
    check("escena: texto de pista y %", row(c, 17), "Descargando audio es-US 2/3 ·  45%")
    S["brand"] = True
    scene_cells(S, st, t, t + 2.1, 51)
    scene_cells(S, st, t, t + 3.0, 79)                                  # 1.4.6: el carril termina su ✓ y su salida (≈ 1.6 s) antes de soltar el centro
    scene_cells(S, st, t, t + 4.0, 79)
    c = scene_cells(S, st, t, t + 5.0, 80)
    check("escena: el título pasa a D L P Y", row(c, 8), "D L P Y")
    check("escena DLPY: el centro pasa a ser la ventana a-Shell con el comando, la cadena y la versión",
          ("a-Shell" in row(c, 10), "$" in row(c, 11), all(w in row(c, 12) for w in ("aSH", "PY", "DLPY")),
           ("DLpy " + VERSION) in row(c, 13)), (True, True, True, True))
    S["brand"], S["label"] = False, "Analizando enlace"                  # 1.4.5: sin «Descargando», el centro vuelve al sitio
    scene_cells(S, st, t, t + 5.1, 81)
    c = scene_cells(S, st, t, t + 6.0, 100)
    check("escena: y puede volver al título del video", row(c, 8), "Pan casero")
    check("escena DLPY: al volver, el centro es otra vez el marco del video", ("a-Shell" in row(c, 10), "╭" in row(c, 10)), (False, True))
    S["label"], S["pct"], S["geo"] = "Descargando audio es-US 2/3", 45, (38, 24, 6, 17)
    st2 = {"rows": {}, "lab": None, "prev": "", "full": "", "t": 0.0, "tcur": None, "tprev": None, "tt": None}
    scene_cells(S, st2, t, t + 5.0, 140)
    cn = scene_cells(S, st2, t, t + 6.0, 170)
    check("escena: terminal angosto conserva idioma, 2/3 y %", "".join(cn[(x, 17)][0] if (x, 17) in cn else " " for x in range(1, 38)).strip(),
          "Audio es-US 2/3 ·  45%")
    S["label"], S["pct"], S["geo"] = "Comprobando " + "x" * 80, None, (60, 24, 6, 17)
    c = scene_cells(S, st, t, t + 6.0, 150)
    check("escena: un texto largo se recorta y cabe", 0 < len(row(c, 17)) <= 54, True)
    a0 = scene_cells(dict(S, busy=True), st, t, t + 6.0, 150)
    a1 = scene_cells(dict(S, busy=True), st, t, t + 6.5, 156)
    check("escena: el barrido de la regla se mueve", [a0[(x, 6)][1] for x in range(17, 46)] != [a1[(x, 6)][1] for x in range(17, 46)], True)
    # 1.0.0: marco de video según la proporción y título = códec (1.0.2: sin haz; la conversión tiene su propia escena)
    check("video: proporción y alto del primer dato válido",
          [video_shape({"width": 1080, "height": 1920}), video_shape({"height": 720}, {"width": 1280, "height": 720}),
           video_shape(None, {"aspect_ratio": 1.5}), video_shape({}, None)],
          [(1080 / 1920.0, 1920), (1280 / 720.0, 720), (1.5, None), (None, None)])
    check("video: ancho del marco vertical / cuadrado / horizontal / sin dato / angosto",
          [site_frame_width(9 / 16.0, 40), site_frame_width(1.0, 40), site_frame_width(16 / 9.0, 40), site_frame_width(None, 40),
           site_frame_width(16 / 9.0, 12)], [7, 9, 17, 17, 11])
    fv, fh = site_video_cells(10, 4, 18, (255, 0, 0), (0, 0, 255), 3.0, 1.0), site_video_cells(10, 4, 6, (255, 0, 0), (0, 0, 255), 3.0, 1.0)
    check("video: el marco ocupa fw × 5 celdas y el vertical es más estrecho que alto",
          (len(fv), len(fh), {y for (_x, y) in fh} == set(range(4, 9)), max(x for (x, _y) in fh) - min(x for (x, _y) in fh) + 1),
          (95, 35, True, 7))
    check("video: el marco es repetible (sin azar entre llamadas)",
          site_video_cells(10, 4, 18, (255, 0, 0), (0, 0, 255), 3.0, 1.0, 360),
          site_video_cells(10, 4, 18, (255, 0, 0), (0, 0, 255), 3.0, 1.0, 360))
    check("video: el ► respira en el centro del marco",
          site_video_cells(10, 4, 18, (255, 0, 0), (0, 0, 255), 3.0, 1.0)[(19, 6)][0], "►")
    cvS = dict(S, conv={"codec": "HEVC", "t0": 0.0, "end": None}, brand=False)
    check("escena: al convertir el título es el códec; terminada vuelve el del video; D L P Y manda",
          (scene_title_spec(cvS), scene_title_spec(dict(cvS, conv={"codec": "H.264", "t0": 0.0, "end": 1.0})),
           scene_title_spec(dict(cvS, brand=True)), scene_title_spec(dict(cvS, conv={"codec": "H.264", "t0": 0.0, "end": None}))),
          (("grad", "H E V C"), ("white", "Pan casero"), ("grad", "D L P Y"), ("grad", "H 2 6 4")))
    stc = {"rows": {}, "lab": None, "prev": "", "full": "", "t": 0.0, "tcur": None, "tprev": None, "tt": None}
    cvS["label"], cvS["pct"] = "Convirtiendo · VideoToolbox", None
    scene_cells(cvS, stc, t, t + 0.01, 1)
    cc = scene_cells(cvS, stc, t, t + 3.0, 80)
    check("escena: convirtiendo, el cuadro tiene el marco y el texto del motor",
          ("╭" in {v[0] for v in cc.values()}, row(cc, 17)), (True, "Convirtiendo · VideoToolbox"))
    cvE = dict(S, conv={"codec": "HEVC", "t0": 0.0, "end": 1.0})
    for _dt in (5.0, 9.5, 10.0, 10.5):                                    # 1.2.8: el dibujo espera su loop antes de irse (y luego se retira)
        scene_cells(cvE, stc, t, t + _dt, 120)
    check("escena: la animación de conversión se retira sola tras su salida", cvE["conv"], None)
    check("escena: sin escena, convertir no hace nada", (scene_convert("HEVC"), scene_convert_end(), SCENE["conv"]), (None, None, None))
    check("escena de conversión: el centro tiene el chip de destino, y el título sigue siendo el códec",
          ("HEVC" in row(cc, 12), "?" in row(cc, 12), "a-Shell" in row(cc, 10), "H E V C" == row(cc, 8)), (True, True, False, True))
    # 1.0.2: escena de conversión, escena DLPY y transición entre los dibujos del centro
    ra, rb = (255, 0, 0), (0, 0, 255)

    def rowtxt(cs, y):
        return "".join(cs[(x, y)][0] if (x, y) in cs else " " for x in range(1, 70)).strip()
    c1, c2 = scene_conv_cells(60, 6, ra, rb, 1.0, "VP9", "HEVC"), scene_conv_cells(60, 6, ra, rb, 1.2, "VP9", "HEVC")
    check("conversión: origen a la izquierda, destino a la derecha y tres filas de alto",
          ("VP9" in rowtxt(c1, 12), "HEVC" in rowtxt(c1, 12), rowtxt(c1, 12).find("VP9") < rowtxt(c1, 12).find("HEVC"),
           {y for (_x, y) in c1} == {11, 12, 13}), (True, True, True, True))
    check("conversión: solo se mueve la fila central (los chips no se repintan)",
          sorted({y for (x, y) in set(c1) | set(c2) if c1.get((x, y)) != c2.get((x, y))}), [12])
    check("conversión: repetible y cabe en 31 columnas con los textos más largos",
          (c1 == scene_conv_cells(60, 6, ra, rb, 1.0, "VP9", "HEVC"),
           max(x for (x, _y) in scene_conv_cells(31, 6, ra, rb, 1.0, "DOLBY", "H.264")) < 31,
           max(x for (x, _y) in scene_conv_cells(31, 6, ra, rb, 1.0, "ABCDEFGH", "ABCDEFGH")) < 31), (True, True, True))
    check("conversión: textos de los chips", [scene_chip_text("webm"), scene_chip_text("Dolby Vision"), scene_chip_text(None),
                                              scene_chip_text("H.264"), scene_chip_text("日本語")], ["WEBM", "DV", "", "H.264", ""])
    # 1.2.1: la nueva escena de conversión (con %) y su avance
    pa0, pa4, pa10 = (scene_conv_cells(31, 6, ra, rb, 1.0, "VP9", "HEVC", v) for v in (0, 42, 100))
    _nb = lambda cs: sum(sum(v[1]) for (_x, _y), v in cs.items() if _y == 12 and v[0] == "·")      # 1.2.8: el avance enciende los puntos · de toda la vía
    check("conversión 1.2.1 (1.5.6): sin % ni avance en la vía (con 0 % y 42 % es el mismo dibujo; solo al llegar a 100 % se llena) y cabe en 31 columnas",
          (not any("%" in rowtxt(c, y) for c in (pa0, pa4, pa10) for y in (11, 12, 13)), _nb(pa0) == _nb(pa4) < _nb(pa10),
           max(x for (x, _y) in pa10) < 31, min(x for (x, _y) in pa10) >= 1), (True, True, True, True))
    _gl = lambda lt: "".join(v[0] for _k, v in sorted(scene_conv_cells(60, 6, ra, rb, lt, "VP9", "HEVC", None).items()) if _k[1] == 12)[7:-7]
    _fr = [_gl(0.05 * i) for i in range(0, 80)]
    _gp = _conv_geo(60, "VP9", "HEVC")[4]
    _lf = [conv_loop_left(60, "VP9", "HEVC", t) for t in (0.0, 0.5, 4.0, 5.2, 6.4)]
    check("conversión 1.2.8: al empezar el primer paquete tarda gap/CONV_FLOW en llegar; luego llega uno cada CONV_PACK/CONV_FLOW s",
          (round(_lf[0], 6) == round(_gp / CONV_FLOW, 6), all(0.0 < x <= _gp / CONV_FLOW + 1e-9 for x in _lf), _lf[0] > _lf[1],
           round(_lf[2], 6) == round(_lf[3], 6) == round(_lf[4], 6)), (True, True, True, True))
    _Sx = {"geo": (60, 24, 6, 17), "check": {"items": None, "verdict": None}}
    _Tx = {"mt": None, "ms": 0.0, "cinfo": ("VP9", "HEVC", 0.0)}
    _ll = {k: motif_loop_left(_Sx, _Tx, k, 0.3) for k in ("conv", "merge", "save", "clean", "empty", "check", "send", "ask", None, "dlpy")}
    check("escena 1.2.8: cada dibujo con loop sabe cuánto falta para terminarlo; el sitio, DLPY y la pregunta no esperan",
          (all(_ll[k] > 0 for k in ("conv", "merge", "save", "clean", "empty", "check", "send")), _ll["ask"], _ll[None], _ll["dlpy"],
           round(_ll["merge"], 6), round(_ll["send"], 6), round(_ll["save"], 6)), (True, 0.0, 0.0, 0.0, 0.5, 1.3, 0.85))
    # 1.2.9: escenas «Primera ejecución» y «Actualizado»
    wf0, wf1, wf2 = (scene_first_cells(60, 6, ra, rb, lt) for lt in (0.05, 1.0, 2.0))
    wu0, wu1 = (scene_updated_cells(60, 6, ra, rb, lt, "1.2.8", "1.2.9") for lt in (0.5, 1.8))
    _ck = lambda cs: sum(1 for v in cs.values() if v[0] == "✓")
    check("escena 1.2.9: el centro es «first» / «updated» con S['welcome'] (D L P Y no manda; un error sí; sin welcome nada cambia)",
          [scene_motif_kind(x) for x in ({"label": "x", "brand": True, "welcome": {"kind": "first"}},
                                         {"label": "x", "brand": True, "welcome": {"kind": "updated"}},
                                         {"label": "x", "brand": True, "welcome": {"kind": "first"}, "last_error": "e"},
                                         {"label": "x", "brand": True, "welcome": {"kind": "zzz"}},
                                         {"label": "Guardando", "welcome": None})],
          ["first", "updated", "dlpy", "dlpy", "rail"])
    check("primera ejecución 1.2.9: tres pasos (carpetas · estado · listo) en tres filas y se marcan con ✓ uno a uno",
          (rowtxt(wf2, 11).startswith("carpetas"), rowtxt(wf2, 12).startswith("estado"), rowtxt(wf2, 13).startswith("listo"),
           {y for (_x, y) in wf2} == {11, 12, 13}, _ck(wf0), _ck(wf1), _ck(wf2)), (True, True, True, True, 0, 1, 3))
    check("primera ejecución 1.2.9: repetible, se mueve, se repite cada ciclo y cabe en 31 columnas",
          (wf1 == scene_first_cells(60, 6, ra, rb, 1.0), wf0 != wf1,
           scene_first_cells(60, 6, ra, rb, 0.5) == scene_first_cells(60, 6, ra, rb, 0.5 + WELCOME_CYCLE),
           max(x for (x, _y) in scene_first_cells(31, 6, ra, rb, 2.0)) < 31, min(x for (x, _y) in scene_first_cells(31, 6, ra, rb, 2.0)) >= 1),
          (True, True, True, True, True))
    check("actualizado 1.2.9: versión anterior a la izquierda, nueva a la derecha; en camino van chevrones › y al llegar un ✓",
          (rowtxt(wu0, 12).find("1.2.8") < rowtxt(wu0, 12).find("1.2.9"), "›" in rowtxt(wu0, 12), "✓" in rowtxt(wu0, 12),
           "✓" in rowtxt(wu1, 12), "›" in rowtxt(wu1, 12), {y for (_x, y) in wu0} == {11, 12, 13}),
          (True, True, False, True, False, True))
    check("actualizado 1.2.9: repetible, se mueve, se repite cada ciclo, sin versión pone «?» y cabe en 31 columnas con versiones largas",
          (wu0 == scene_updated_cells(60, 6, ra, rb, 0.5, "1.2.8", "1.2.9"), wu0 != wu1,
           scene_updated_cells(60, 6, ra, rb, 0.5, "1.2.8", "1.2.9") == scene_updated_cells(60, 6, ra, rb, 0.5 + WELCOME_CYCLE, "1.2.8", "1.2.9"),
           "?" in rowtxt(scene_updated_cells(60, 6, ra, rb, 0.5), 12),
           max(x for (x, _y) in scene_updated_cells(31, 6, ra, rb, 0.5, "12.34.56.78", "98.76.54.32")) < 31,
           min(x for (x, _y) in scene_updated_cells(31, 6, ra, rb, 0.5, "12.34.56.78", "98.76.54.32")) >= 1),
          (True, True, True, True, True, True))
    check("escena 1.2.9: primera ejecución y actualizado tienen loop (un ciclo) y no se deshacen hasta terminarlo",
          (round(motif_loop_left(_Sx, _Tx, "first", 0.3), 6), round(motif_loop_left(_Sx, _Tx, "updated", 0.3), 6),
           round(motif_loop_left(_Sx, _Tx, "first", 0.3 + WELCOME_CYCLE), 6), SCENE_WELCOME_SECS < WELCOME_CYCLE),
          (round(WELCOME_CYCLE - 0.3, 6), round(WELCOME_CYCLE - 0.3, 6), round(WELCOME_CYCLE - 0.3, 6), True))
    check("escena 1.2.9: qué escena de arranque toca (sin versión guardada = primera; otra = actualizado; igual = ninguna)",
          [welcome_kind(None, "1.2.9"), welcome_kind("", "1.2.9"), welcome_kind("1.2.8", "1.2.9"), welcome_kind("1.3.0", "1.2.9"),
           welcome_kind("1.2.9", "1.2.9")], ["first", "first", "updated", "updated", None])
    _wk = ("on", "welcome", "label", "label_wall", "brand", "busy", "err_brand", "pct", "last_error")
    _sv, _secs, _hold0 = {k: SCENE.get(k) for k in _wk}, SCENE_WELCOME_SECS, globals()["scene_hold"]
    _seen = []
    try:
        globals()["SCENE_WELCOME_SECS"] = 0.0
        globals()["scene_hold"] = lambda secs: (_seen.append((SCENE["label"], SCENE["brand"], SCENE["busy"], (SCENE["welcome"] or {}).get("kind"))) or True)
        SCENE.update(on=True, welcome=None, label="Preparando", label_wall=None, brand=False, busy=False, err_brand=False, pct=None, last_error=None)
        _w = []
        for _a in (("updated", "1.2.8", "1.2.9", False), ("updated", "1.3.0", "1.2.9", True), ("first", None, None, False), ("zzz", None, None, False)):
            _w.append((scene_welcome(*_a), SCENE["label"], SCENE["brand"], SCENE["busy"], SCENE["welcome"]))
        SCENE.update(brand=True, busy=True, label="Comprobando DLpy")                 # ya en el título D L P Y: se respeta
        _w.append((scene_welcome("first"), SCENE["label"], SCENE["brand"], SCENE["busy"]))
        SCENE.update(brand=False, busy=False, label="Preparando", last_error="x")      # con un error no se toca
        _w.append((scene_welcome("first"), SCENE["label"]))
        SCENE.update(on=False, last_error=None)
        _w.append(scene_welcome("first"))
    finally:
        globals()["SCENE_WELCOME_SECS"], globals()["scene_hold"] = _secs, _hold0
        SCENE.update(_sv)
    check("escena 1.2.9/1.3.1: scene_welcome pone el texto de estado y D L P Y mientras dura, y al terminar lo deja todo como estaba (no se queda en D L P Y)",
          (_seen, _w),
          ([("Actualizado · 1.2.8 → 1.2.9", True, True, "updated"), ("Versión anterior · 1.3.0 → 1.2.9", True, True, "updated"),
            (f"Primera ejecución · DLpy {VERSION}", True, True, "first"), (f"Primera ejecución · DLpy {VERSION}", True, True, "first")],
           [(True, "Preparando", False, False, None), (True, "Preparando", False, False, None), (True, "Preparando", False, False, None),
            (False, "Preparando", False, False, None), (True, "Comprobando DLpy", True, True), (False, "Preparando"), False]))
    _cl = "# ==== CHANGELOG ====\n# ## 9.9.9\n# ==== FIN CHANGELOG ====\n"
    check("1.3.2: el hash del código ignora el changelog y detecta un cambio de código con la misma versión",
          (text_fingerprints("a = 1\n" + _cl)[1] == text_fingerprints("a = 1\n" + _cl.replace("9.9.9", "1.0.0"))[1],
           text_fingerprints("a = 1\n" + _cl)[1] == text_fingerprints("a = 2\n" + _cl)[1],
           [code_change(None, "h1"), code_change("", "h1"), code_change("h1", "h1"), code_change("h1", "h2"),
            code_change("h1", None), code_change(None, None)]),
          (True, False, ["first", "first", None, "edited", None, None]))
    _Tm = {"mt": 10.0, "ms": 9.0}                                       # 1.3.2: DLPY_SCENE_MODE
    _smr, _sx = SCENE_MODE, {"geo": (60, 24, 6, 17), "conv": {"pct": 50.0}, "pp_pct": 100.0}
    try:
        _gap = _conv_geo(60, "mkv", "mp4")[4]
        globals()["SCENE_MODE"] = ("real", None)
        _rl = (scene_real_lt(_sx, {"cinfo": ("mkv", "mp4", 0.0)}, "conv", 9.9), scene_real_lt(dict(_sx, conv={"pct": None}), {}, "conv", 9.9),
               scene_real_lt(dict(_sx, conv={"pct": 100.0}), {"cinfo": ("mkv", "mp4", 0.0)}, "conv", 0.0),
               round(scene_real_lt(_sx, {}, "merge", 9.9), 6), scene_real_lt(dict(_sx, pp_pct=None), {}, "merge", 9.9), scene_real_lt(_sx, {}, "save", 0.7))
        globals()["SCENE_MODE"] = ("loop", None)
        _rl += (scene_real_lt(_sx, {}, "conv", 9.9),)
    finally:
        globals()["SCENE_MODE"] = _smr
    check("escena 1.3.9: modo real: el dibujo avanza con el % real (conversión: llega al destino al 100 %; unión: 3 ciclos; sin % o sin real, el reloj)",
          _rl, (_gap * 0.5 / CONV_FLOW, 9.9, _gap / CONV_FLOW, round(3 * 4.0 / MERGE_SPEED, 6), 9.9, 0.7, 9.9))
    check("escena 1.3.2: DLPY_SCENE_MODE (loop · real · segundos) se interpreta y lo inválido cae en loop",
          [scene_mode_parse(v) for v in (None, "", "loop", "real", "Real", "2", "1,5", "0", "-1", "abc", "nan", "inf", "999")],
          [("loop", None), ("loop", None), ("loop", None), ("real", None), ("real", None), ("secs", 2.0), ("secs", 1.5), ("secs", 0.0),
           ("loop", None), ("loop", None), ("loop", None), ("loop", None), ("secs", 60.0)])
    check("escena 1.3.2: cuánto espera un dibujo (loop = lo que falte de su loop, real = nada, número = lo que falte para N s a la vista; «ask» nunca)",
          (round(motif_hold_secs(_Sx, _Tm, "send", 10.2, ("loop", None)), 6), motif_hold_secs(_Sx, _Tm, "send", 10.2, ("real", None)),
           round(motif_hold_secs(_Sx, _Tm, "send", 11.0, ("secs", 3.0)), 6), motif_hold_secs(_Sx, _Tm, "send", 14.0, ("secs", 3.0)),
           motif_hold_secs(_Sx, _Tm, "ask", 10.2, ("secs", 3.0)), round(motif_hold_secs(_Sx, {"mt": None, "ms": 5.0}, None, 6.0, ("secs", 2.0)), 6)),
          (round((-0.2) % SEND_CYCLE, 6), 0.0, 2.0, 0.0, 0.0, 1.0))
    check("borrado 1.3.2: DLPY_PURGE manda «ESC[3J» por omisión y no con 0 / no / false / off / vacía",
          [purge_seq(v) for v in (None, "", "0", "no", "false", "OFF", "1", "sí", "abc")],
          ["\x1b[3J", "", "", "", "", "", "\x1b[3J", "\x1b[3J", "\x1b[3J"])
    check("borrado 1.3.2: DLPY_CLEARMODE (auto = nativo; home / down / purge-first / reset = secuencia con el historial; sin historial si DLPY_PURGE=0)",
          ([clear_mode_seq(m, "P") for m in ("auto", "", "zzz", "home", "Down", "purge-first", "reset")], clear_mode_seq("home", ""),
           [n for n, _t in CLEAR_MODES]),
          ([None, None, None, "\x1b[H\x1b[2JP\x1b[H", "\x1b[H\x1b[JP", "P\x1b[H\x1b[2J", "\x1bc"], "\x1b[H\x1b[2J\x1b[H",
            ["auto", "home", "down", "purge-first", "reset"]))
    check("borrado 1.3.5: el primer borrado al arrancar es el clear 3 (reset) salvo DLPY_EARLYCLEARMODE o un DLPY_CLEARMODE propio",
          ([early_clear_mode(e, c) for e, c in ((None, "auto"), ("", "auto"), ("home", "auto"), (" Down ", "auto"), (None, "home"), ("home", "reset"))],
           clear_mode_seq(early_clear_mode(None, "auto"), "P")),
          (["reset", "reset", "home", "down", None, None], "\x1bc"))
    _sk = dict(STREAM_KINDS)
    try:
        STREAM_KINDS.clear()
        _fb = {"info_dict": {"format_id": "sd", "ext": "mp4"}}
        _k0 = (scene_kind(_fb), stream_kinds(_fb), stream_label(_fb))
        STREAM_KINDS["sd"], STREAM_KINDS["hd"], STREAM_KINDS["a1"] = ("video", "audio"), ("video", "audio"), ("audio",)
        _k1 = (scene_kind(_fb), stream_kinds(_fb), stream_label(_fb), scene_kind({"info_dict": {"format_id": "a1"}}),
               stream_kinds({"info_dict": {"format_id": "x", "height": 720, "vcodec": "avc1", "acodec": "mp4a"}}))
    finally:
        STREAM_KINDS.clear()
        STREAM_KINDS.update(_sk)
    check("escena 1.3.6: «sd» / «hd» sin datos en el hook son video (y audio) si la lista de formatos lo dice; sin lista, lo de siempre",
          (_k0, _k1, [format_kinds(f) for f in (normalize_format({"format_id": "sd", "ext": "mp4", "tbr": 500}), {"vcodec": "none", "acodec": "opus"},
                                                  {"vcodec": "avc1", "acodec": "none"}, {})]),
          (("audio", ("audio",), "Audio"), ("video", ("video", "audio"), "sd", "audio", ("video", "audio")),
           [("video", "audio"), ("audio",), ("video",), ()]))
    _ft = parse_ffmpeg_facts("  Stream #0:0[0x1](und): Video: h264 (High) (avc1 / 0x31637661), yuv420p(tv, bt709, progressive), 1280x720 [SAR 1:1 DAR 16:9], "
                             "1129 kb/s, 29.97 fps, 29.97 tbr, 90k tbn (default)\n  Stream #0:1[0x2](und): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, "
                             "stereo, fltp, 128 kb/s (default)")
    check("lectura ffmpeg 1.3.6: video (códec, tamaño, fps, bitrate) y audio (códec, Hz, bitrate); sin streams, None",
          (_ft, parse_ffmpeg_facts("nada"), parse_ffmpeg_facts(None)),
          ({"v": {"codec": "h264", "width": 1280, "height": 720, "fps": 29.97, "kbps": 1129}, "a": {"codec": "aac", "hz": 44100, "kbps": 128}}, None, None))
    check("datos reales 1.3.6: se pide leer solo si falta resolución, códec o bitrate",
          [stream_needs_probe(i, k) for i, k in (({"vcodec": "avc1", "height": 720, "tbr": 900}, ("video",)), ({"vcodec": None}, ("video", "audio")),
                                                  ({"acodec": "opus", "abr": 130}, ("audio",)), ({"acodec": "opus"}, ("audio",)),
                                                  ({"vcodec": "avc1", "height": 720, "tbr": 900, "acodec": "mp4a"}, ("video", "audio")))],
          [False, True, False, True, False])
    check("etiquetas 1.3.6: los datos que no se supieron salen marcados solo tras intentar leerlos; el códec supuesto no cuenta como dato",
          (vinfo_labels(None, None, {}), vinfo_labels(None, None, {"settled": True}), vinfo_labels(720, 16 / 9.0, {"settled": True, "codec": "h264", "kbps": 900}),
           audio_labels(None, {}), audio_labels(None, {"settled": True}), audio_labels("AAC", {"settled": True, "kbps": 128, "hz": 44100}),
           video_facts({"vcodec": "avc1", "_guess": True, "tbr": 500}), audio_facts({"acodec": "mp4a", "_guess": True}),
           video_facts({"vcodec": "none", "tbr": 130}, {"vcodec": "avc1", "tbr": 900})),
          ([], ["\u00bfRES?", "\u00bfCOD?", "\u00bfFPS?", "\u00bfBIT?"], ["720", "H.264", "\u00bfFPS?", "900kb"], [], ["\u00bfCOD?", "\u00bfBIT?", "\u00bfKHZ?"], ["AAC", "128kb", "44.1k"],
           {"kbps": 500.0}, {}, {"codec": "avc1", "kbps": 900.0}))
    _ss = {k: SCENE.get(k) for k in ("on", "res", "aspect", "vinfo", "ainfo")}
    try:
        SCENE.update(on=True, res=None, aspect=None, vinfo={}, ainfo={})
        scene_facts_apply(parse_ffmpeg_facts("Stream #0:0: Video: h264 (High), yuv420p, 640x360, 500 kb/s, 25 fps\nStream #0:1: Audio: aac (LC), 48000 Hz, stereo, fltp, 96 kb/s"))
        _ap = (SCENE["res"], round(SCENE["aspect"], 3), dict(SCENE["vinfo"]), dict(SCENE["ainfo"]))
        scene_facts_apply({"v": {"codec": "vp9", "height": 1080, "width": 1920}})       # no pisa lo que ya había
        _ap2 = (SCENE["res"], SCENE["vinfo"].get("codec"))
        scene_facts_settle(("video", "audio"))
        _st = (SCENE["vinfo"].get("settled"), SCENE["ainfo"].get("settled"))
    finally:
        SCENE.update(_ss)
    check("escena 1.3.6: lo leído rellena resolución, proporción y etiquetas sin pisar lo que ya había; al terminar se marcan como intentados",
          (_ap, _ap2, _st),
          ((360, 1.778, {"codec": "h264", "fps": 25.0, "kbps": 500}, {"codec": "aac", "hz": 48000, "kbps": 96}), (360, "h264"), (True, True)))
    _lw = SCENE.get("label_wall")
    try:
        SCENE["label_wall"] = 100.0
        _mw = (round(scene_min_wait(101.0, ("secs", 3.0)), 6), scene_min_wait(105.0, ("secs", 3.0)), scene_min_wait(101.0, ("loop", None)),
               scene_min_wait(101.0, ("real", None)))
        SCENE["label_wall"] = None
        _mw += (scene_min_wait(101.0, ("secs", 3.0)),)
    finally:
        SCENE["label_wall"] = _lw
    check("escena 1.3.2: con segundos, el texto de estado se lee N s como mínimo aunque su proceso ya haya acabado (lo que falte; 0 sin texto o en loop / real)",
          _mw, (2.0, 0.0, 0.0, 0.0, 0.0))
    check("escena 1.3.2: las pausas fijas valen N con un número, lo suyo con loop y 0 con real",
          (scene_dwell(0.9, ("secs", 3.0)), scene_dwell(0.9, ("loop", None)), scene_dwell(0.9, ("real", None)), scene_dwell(0.9, ("secs", 0.0))),
          (3.0, 0.9, 0.0, 0.0))
    check("conversión 1.2.8: al empezar no hay paquetes a medio camino (solo uno saliendo del origen)",
          (sum(1 for (_x, _y), v in scene_conv_cells(60, 6, ra, rb, 0.05, "VP9", "HEVC", None).items() if _y == 12 and v[0] in "•●"),
           sum(1 for (_x, _y), v in scene_conv_cells(60, 6, ra, rb, -0.5, "VP9", "HEVC", None).items() if _y == 12 and v[0] in "•●")), (0, 0))
    check("conversión 1.2.8: el paquete crece al cruzar la vía (· chico al salir, • mediano a mitad, ● grande al llegar)",
          (any("●" in x for x in _fr), any("•" in x and "●" not in x for x in _fr), _fr[0][:3].count("●") == 0), (True, True, True))
    check("conversión 1.2.1: sin recuadro ni compuerta en medio de la vía (ni giratoria ni bloque)",
          [any(ch in rowtxt(c, 12) for ch in "▘▝▗▖▮█▓▒░") for c in (pa0, pa4, pa10, c1, c2)], [False] * 5)
    q1, q2 = (scene_conv_cells(60, 6, ra, rb, lt, "VP9", "HEVC", 42) for lt in (1.0, 2.0))
    check("conversión 1.2.1: la vía son puntos •; sin avance no hay %; con avance solo cambia la fila de la vía",
          ("•" in rowtxt(q2, 12), "%" not in rowtxt(c1, 13), sorted({y for (x, y) in set(q1) | set(q2) if q1.get((x, y)) != q2.get((x, y))}),
           q1 == scene_conv_cells(60, 6, ra, rb, 1.0, "VP9", "HEVC", 42), len(q1) < 80), (True, True, [12], True, True))
    check("conversión 1.2.1: el destino se enciende con el avance",
          pa0[(max(x for (x, y) in pa0 if y == 11), 11)] != pa10[(max(x for (x, y) in pa10 if y == 11), 11)], True)
    _sv = {k: SCENE.get(k) for k in ("on", "conv", "pct", "frac")}
    try:
        SCENE.update(on=True, conv={"codec": "HEVC", "t0": 0.0, "end": None, "pct": None}, pct=None, frac=0.0)
        scene_conv_progress(40.0)
        scene_conv_progress(30.0)
        _r1 = (SCENE["conv"]["pct"], SCENE["pct"], round(SCENE["frac"], 3))
        scene_conv_progress(None)
        _r2 = (SCENE["conv"]["pct"], SCENE["pct"])
        SCENE["conv"]["end"] = 1.0
        scene_conv_progress(90.0)
        _r3 = SCENE["conv"]["pct"]
    finally:
        SCENE.update(_sv)
    check("conversión 1.2.1: el avance nunca retrocede, None lo oculta y terminada la conversión ya no cambia",
          (_r1, _r2, _r3), ((40.0, 40.0, 0.856), (None, None), None))
    d0, d3, d5 = (scene_dlpy_cells(60, 6, ra, rb, lt, "1.2.3", "boot") for lt in (0.0, 3.0, 5.5))
    check("DLPY: ventana a-Shell con la cadena aSH ► PY ► DLPY boot, la versión y cinco filas",
          ("a-Shell" in rowtxt(d3, 10), all(w in rowtxt(d3, 12) for w in ("aSH", "PY", "DLPY")), "DLpy 1.2.3" in rowtxt(d3, 13),
           {y for (_x, y) in d3} == set(range(10, 15))), (True, True, True, True))
    check("DLPY 1.2.7: el comando empieza vacío, se teclea rápido (0,7 s), se ejecuta y se queda (sin borrarse)",
          tuple("python dlpy.py" in rowtxt(scene_dlpy_cells(60, 6, ra, rb, 3.0, "1.2.3", "boot", tt), 11) for tt in (0.0, 0.4, 0.8, 1.2, 5.0)),
          (False, False, True, True, True))
    check("DLPY 1.2.7: tras el Enter gira el indicador y el paso dura DLPY_STEP_SECS",
          ("|" in rowtxt(scene_dlpy_cells(60, 6, ra, rb, 0.0, "1.2.3", "boot", 0.9), 11), DLPY_STEP_SECS), (True, 1.15))
    _th = threading.Thread(target=time.sleep, args=(3.0,), daemon=True)      # 1.3.3: un hilo de escena «vivo»
    _th.start()
    _sm = SCENE_MODE
    try:
        SCENE.update(on=True, brand=True, label="Comprobando pip", label_wall=time.time(), last_error=None, frac=0.0, pct=None, dl_done=None, th=_th, welcome=None, stop=False)
        _tm = threading.Timer(0.3, lambda: SCENE.__setitem__("dl_done", "Comprobando pip"))
        _tm.start()
        _t0 = time.time()
        scene_status("Actualizando pip")
        _dt = time.time() - _t0
        _w1 = (0.25 <= _dt < 1.5, SCENE.get("label"), SCENE.get("dl_done"))
        SCENE.update(dl_done=None, label="Comprobando pip")
        _t0 = time.time()
        _w2 = (scene_wait_step("Comprobando pip", limit=0.2), 0.15 <= time.time() - _t0 < 1.0)           # la escena no lo mostró: tope
        SCENE["dl_done"] = "Comprobando pip"
        _w3 = scene_wait_step("Comprobando pip", limit=0.2)                                               # ya mostrado: no espera
        globals()["SCENE_MODE"] = ("real", None)
        SCENE["dl_done"] = None
        _t0 = time.time()
        _w4 = (scene_wait_step("Comprobando pip", limit=0.5), time.time() - _t0 < 0.1)                    # real: cambia al instante
        globals()["SCENE_MODE"] = _sm
        SCENE.update(brand=False)
        _t0 = time.time()
        _w5 = (scene_wait_step("Comprobando pip", limit=0.5), time.time() - _t0 < 0.1)                    # si D L P Y no es lo que se ve, no espera
        SCENE.update(brand=True, th=None)
        _t0 = time.time()
        _w6 = (scene_wait_step("Comprobando pip", limit=0.5), time.time() - _t0 < 0.1)                    # sin hilo de escena vivo, no espera
        SCENE.update(th=_th, last_error="x")
        _w7 = scene_wait_step("Comprobando pip", limit=0.5)                                               # tras un error, tampoco
    finally:
        globals()["SCENE_MODE"] = _sm
        SCENE.update(on=False, brand=False, label="", label_wall=None, th=None, dl_done=None, last_error=None)
    check("DLPY 1.3.3: scene_status espera a que la ESCENA haya mostrado el comando anterior (no a un reloj) y el texto cambia después",
          _w1, (True, "Actualizando pip", None))
    check("DLPY 1.3.3: la espera tiene tope, no espera si ya se mostró, con real, si D L P Y no es lo visible, sin hilo vivo ni tras un error",
          (_w2, _w3, _w4, _w5, _w6, _w7), ((False, True), True, (False, True), (False, True), (False, True), False))
    check("DLPY: repetible, el destello se mueve y cabe en 31 columnas",
          (d3 == scene_dlpy_cells(60, 6, ra, rb, 3.0, "1.2.3", "boot"), scene_dlpy_cells(60, 6, ra, rb, 3.0, "1", "boot") != scene_dlpy_cells(60, 6, ra, rb, 3.5, "1", "boot"),
           max(x for (x, _y) in scene_dlpy_cells(31, 6, ra, rb, 1.0, "1.0.3", "boot")) < 31), (True, True, True))
    da = scene_dlpy_cells(60, 6, ra, rb, 2.0, "1.0.3", "Analizando enlace")
    dg = scene_dlpy_cells(60, 6, ra, rb, 2.0, "1.0.3", "Comprobando DLpy")
    dy = scene_dlpy_cells(60, 6, ra, rb, 2.0, "1.0.3", "Comprobando yt-dlp")
    check("DLPY 1.2.7: comando y nombre salen del texto de estado",
          [_dlpy_topic(x) for x in ("Comprobando pip", "Actualizando pip → 26.0", "Comprobando yt-dlp", "Instalando yt-dlp-ejs", "Comprobando DLpy", "Analizando enlace")],
          [("pip", "GET pypi.org/pypi/pip/json"), ("pip", "pip install -U pip --no-deps"), ("yt-dlp", "GET pypi.org/pypi/yt-dlp/json"),
           ("yt-dlp-ejs", "pip install -U yt-dlp-ejs --no-deps"), ("GitHub", f"GET api.github.com/repos/{UPDATE_REPO}/releases"), ("analizando", "extract_info(…)")])
    _ts = ("Instalando yt-dlp", "yt-dlp 2026.1.1 · instalado", "No se pudo instalar yt-dlp", "Instalando yt-dlp-ejs==0.8.0", "yt-dlp 2026.1.1 · actualizada",
           "yt-dlp 2026.1.1 · última versión", "No se pudo comprobar pip", "No se pudo actualizar yt-dlp")
    check("DLPY 1.3.3: el comando es el REAL: pip install sale de pip_args (el mismo que lanza pip_run) y comprobar es la consulta a PyPI; los resultados dicen lo mismo que el proceso",
          ([_dlpy_topic(x) for x in _ts], pip_cmd(pip_args("yt-dlp")), pip_cmd(["install", "-U", "a==1"])),
          ([("yt-dlp", "pip install -U yt-dlp --no-deps"), ("yt-dlp", "pip install -U yt-dlp --no-deps"), ("yt-dlp", "pip install -U yt-dlp --no-deps"),
            ("yt-dlp-ejs", "pip install -U yt-dlp-ejs==0.8.0 --no-deps"), ("yt-dlp", "pip install -U yt-dlp --no-deps"),
            ("yt-dlp", "GET pypi.org/pypi/yt-dlp/json"), ("pip", "GET pypi.org/pypi/pip/json"), ("yt-dlp", "pip install -U yt-dlp --no-deps")],
           "pip install -U yt-dlp --no-deps", "pip install -U a==1"))
    _tg = ("Comprobando DLpy", "DLpy 1.3.2 · última versión", "DLpy 1.3.2 · versión local", "Nueva versión de DLpy · 1.3.2 → 1.3.3", "DLpy 1.3.3 · idéntica a la que falló",
           "No se pudo comprobar DLpy", "Instalando DLpy 1.3.3", "DLpy 1.3.3 · instalada", "No se pudo instalar DLpy 1.3.3")
    check("DLPY 1.3.3: los textos de DLpy (resultados incluidos) y los de --scb ya no caen en «python dlpy.py»",
          ([_dlpy_topic(x)[1] for x in _tg], [_dlpy_topic(x) for x in SCB_NOTES], _dlpy_topic("Preparando"), _dlpy_topic("")),
          ([f"GET api.github.com/repos/{UPDATE_REPO}/releases"] * 6 + ["write " + os.path.basename(SCRIPT_PATH)] * 3,
           [("analizando", "extract_info(…)")] * 3, ("boot", "python dlpy.py"), ("boot", "python dlpy.py")))
    _lk = SCENE.get("link")
    SCENE["link"] = "https://www.youtube.com/watch?v=abc"
    try:
        check("DLPY 1.4.3: el análisis teclea la llamada real con el enlace real (sin el esquema)", _dlpy_topic("Analizando enlace"),
              ("analizando", "extract_info(www.youtube.com/watch?v=abc)"))
    finally:
        SCENE["link"] = _lk

    # ── 1.4.4: DLPY_UPDATES (una sola variable), resultados reales en la escena, comprobaciones en paralelo, modo calmado ──
    import socket as _sk
    import urllib.error as _ue
    import urllib.request as _ur
    check("1.5.2: parse_updates: on / siempre / always = en cada arranque; número = días (decimales y coma); 0 / off = nunca; vacío, negativo o texto raro = 1 día",
          [parse_updates(x) for x in ("on", "ON", "siempre", "always", "off", "nunca", "0", "0.5", "1", "3", "7", "1,5", "", None, "abc", "-1", "-5")],
          [-1.0, -1.0, -1.0, -1.0, 0.0, 0.0, 0.0, 0.5, 1.0, 3.0, 7.0, 1.5, 1.0, 1.0, 1.0, 1.0, 1.0])
    _ud = UPDATE_DAYS
    try:
        _dd = {}
        for _lab, _days in (("nunca", 0.0), ("siempre", -1.0), ("1 día", 1.0), ("medio día", 0.5)):
            globals()["UPDATE_DAYS"] = _days
            _dd[_lab] = (due_from(None), due_from({"t": 1000, "sig": "a"}, "a", 1000 + 3600), due_from({"t": 1000, "sig": "a"}, "a", 1000 + 13 * 3600),
                         due_from({"t": 1000, "sig": "a"}, "a", 1000 + 25 * 3600), due_from({"t": 1000, "sig": "a"}, "b", 1000 + 60))
    finally:
        globals()["UPDATE_DAYS"] = _ud
    check("1.4.4: due_from con DLPY_UPDATES: 0 nunca toca (ni con firma nueva) · siempre toca siempre · N días toca al pasar N días",
          _dd,
          {"nunca": (False,) * 5, "siempre": (True,) * 5, "1 día": (True, False, False, True, True), "medio día": (True, False, True, True, True)})
    check("1.4.4: update_every_text", [update_every_text(x) for x in (-1.0, 0.0, 1.0, 3.0, 0.5)],
          ["en cada arranque", "nunca", "cada día", "cada 3 días", "cada 0.5 días"])
    _keep = {k: os.environ.get(k) for k in ("DLPY_UPDATES", "DLPY_NO_UPDATE", "DLPY_CHECK_HOURS")}
    _res = []
    try:
        for _env in ({}, {"DLPY_UPDATES": "7"}, {"DLPY_UPDATES": "0"}, {"DLPY_UPDATES": "on", "DLPY_NO_UPDATE": "1"}, {"DLPY_NO_UPDATE": "1"},
                     {"DLPY_CHECK_HOURS": "48"}, {"DLPY_CHECK_HOURS": "0"}, {"DLPY_UPDATES": "2", "DLPY_CHECK_HOURS": "48"}):
            for k in _keep:
                os.environ.pop(k, None)
            os.environ.update(_env)
            _res.append(_updates_from_env())
    finally:
        for k, v in _keep.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v
    check("1.5.2: DLPY_UPDATES manda; sin ella, las variables de la 1.4.3 siguen valiendo (NO_UPDATE = nunca · CHECK_HOURS / 24); por omisión, 1 día",
          _res, [1.0, 7.0, 0.0, -1.0, 0.0, 2.0, 1.0, 2.0])
    _names = [o[0] for o in CONFIG_OPTIONS]
    check("1.5.2: --config tiene UNA variable de actualizaciones (1 día por omisión) y la de modo calmado",
          ("DLPY_UPDATES" in _names, "DLPY_CHECK_HOURS" in _names, "DLPY_NO_UPDATE" in _names, "DLPY_SCENE_CALM" in _names,
           [o[1] for o in CONFIG_OPTIONS if o[0] == "DLPY_UPDATES"], "script y de sus dependencias" in [o[2] for o in CONFIG_OPTIONS if o[0] == "DLPY_UPDATES"][0]),
          (True, False, False, True, ["1"], True))
    check("1.4.4: net_err_text: HTTP · timeout · sin red · respuesta inválida",
          [net_err_text(x) for x in (_ue.HTTPError("u", 403, "m", {}, None), _sk.timeout(), _ue.URLError(_sk.timeout()), _ue.URLError("x"), ValueError("j"), KeyError("k"))],
          ["HTTP 403", "timeout", "timeout", "sin red", "respuesta inválida", "KeyError"])

    class _Resp:
        status = 200

        def __init__(self, data):
            self.data = data

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self, *a):
            return self.data
    _uo = _ur.urlopen
    try:
        _ur.urlopen = lambda *a, **k: _Resp(b'{"info": {"version": "9.9.9"}}')
        _v1 = latest_version("zz-test")
        _n1 = dict(NET["zz-test"])
        _ur.urlopen = lambda *a, **k: (_ for _ in ()).throw(_ue.URLError("sin dns"))
        _v2 = latest_version("zz-test")
        _n2 = dict(NET["zz-test"])
    finally:
        _ur.urlopen = _uo
        NET.pop("zz-test", None)
    check("1.4.4: latest_version anota código, versión y tiempo; si falla devuelve None y anota la causa",
          (_v1, _n1["ok"], _n1["code"], _n1["val"], _v2, _n2["ok"], _n2["err"]), ("9.9.9", True, 200, "9.9.9", None, False, "sin red"))
    check("1.4.4: _net_line: éxito (código · tiempo · versión) y fallo (causa + qué pasa)",
          (_net_line({"ok": True, "secs": 0.44, "code": 200, "val": "2026.10.21"}, "get"), _net_line({"ok": True, "secs": 3.2, "code": None, "val": None}),
           _net_line({"ok": False, "err": "timeout"}, "get"), _net_line({"ok": False, "err": "pip falló (1)"}), _net_line(None)),
          ("200 · 0.4 s · 2026.10.21", "ok · 3.2 s", "timeout · reintenta al abrir", "pip falló (1)", None))
    check("1.4.4: _dlpy_fit: lo que cabe no se toca; GET deja host/…/último; extract_info(…) acorta el enlace y cierra; pip conserva el final; siempre «…»",
          (_dlpy_fit("GET pypi.org/pypi/pip/json", 32), _dlpy_fit("GET api.github.com/repos/ElDelDLpy/DLpy/releases", 32),
           _dlpy_fit("extract_info(www.youtube.com/watch?v=abcdefghijk)", 32), _dlpy_fit("yt-dlp -J www.youtube.com/watch?v=abcdefghijk", 30),
           _dlpy_fit("pip install -U yt-dlp-ejs==0.8.0 --no-deps", 32)),
          ("GET pypi.org/pypi/pip/json", "GET api.github.com/…/releases", "extract_info(www.youtube.com/w…)", "yt-dlp -J www.youtube.com/wat…", "pip install -U yt-dlp-…--no-deps"))
    check("1.4.4: pip_line_clean quita colores y barras de progreso y deja una línea corta",
          (pip_line_clean("\x1b[32mDownloading\x1b[0m yt_dlp-2026.whl (3.0 MB)"), pip_line_clean("  ━━━━━╸ 1.2/3.0 MB\r"), len(pip_line_clean("x" * 300))),
          ("Downloading yt_dlp-2026.whl (3.0 MB)", "1.2/3.0 MB", 90))
    _nets, _pf, _sp = dict(NET), dict(PREFETCH), SCENE.get("pip_line")
    try:
        NET.clear()
        NET.update({"yt-dlp": {"ok": True, "secs": 0.44, "code": 200, "val": "2026.10.21", "err": None},
                    "pip": {"ok": False, "secs": 6.0, "code": None, "val": None, "err": "timeout"},
                    "pip:yt-dlp": {"ok": True, "secs": 3.2, "code": None, "val": None, "err": None},
                    "DLpy": {"ok": True, "secs": 1.0, "code": 200, "val": "1.4.4", "err": None},
                    "write": {"ok": True, "secs": 0.0, "code": None, "val": None, "err": None},
                    "analyze": {"ok": True, "secs": 2.1, "code": None, "val": "Youtube", "err": None},
                    "check": {"ok": True, "secs": 0.9, "code": None, "val": "3 GET", "err": None}})
        _ft = lambda lab: _dlpy_footer(lab, _dlpy_state(lab), "1.4.4", "x", 36)
        SCENE["pip_line"] = "Downloading yt_dlp-2026.whl"
        _run_pip = _dlpy_footer("Instalando yt-dlp", "run", "1.4.4", "yt-dlp", 36)[0]
        SCENE["pip_line"] = None
        PREFETCH.update({"n": 3, "done": {"pip"}})
        _run_chk = _dlpy_footer("Comprobando actualizaciones", "run", "1.4.4", "actualizaciones", 36)[0]
        check("1.4.4: el pie de la escena dice lo que de verdad pasó (código · tiempo · versión), la causa si falló y el avance en vivo mientras corre",
              [_ft("yt-dlp 2026.10.21 · última versión")[0], _ft("No se pudo comprobar pip")[0], _ft("yt-dlp 2026.10.21 · actualizada")[0], _ft("DLpy 1.4.3 · última versión")[0],
               _ft("DLpy 1.4.4 · instalada")[0], _ft("Todo al día · 3 comprobaciones · 0.9 s")[0], _run_pip, _run_chk,
               _dlpy_footer("Instalando yt-dlp", "run", "1.4.4", "yt-dlp", 36)[0], _dlpy_footer("Preparando", "run", "1.4.4", "boot", 36)[0]],
              ["200 · 0.4 s · 2026.10.21", "timeout · reintenta al abrir", "ok · 3.2 s", "200 · 1.0 s · 1.4.4", "ok · 0.0 s", "ok · 0.9 s · 3 GET",
               "Downloading yt_dlp-2026.whl", "1/3 listas", "DLpy 1.4.4 · yt-dlp", "DLpy 1.4.4 · boot"])
        _sr = SCENE.get("ana_raw"), SCENE.get("link")
        try:
            SCENE["link"], SCENE["ana_raw"] = "https://youtu.be/abc", False
            _a1 = _dlpy_topic("Analizando enlace")[1]
            SCENE["ana_raw"] = True
            _a2 = _dlpy_topic("Analizando enlace")[1]
        finally:
            SCENE["ana_raw"], SCENE["link"] = _sr
        check("1.4.4: análisis: la escena teclea la llamada real con el enlace real, y el paso en bruto teclea `yt-dlp -J <enlace>`",
              (_a1, _a2), ("extract_info(youtu.be/abc)", "yt-dlp -J youtu.be/abc"))
    finally:
        NET.clear()
        NET.update(_nets)
        PREFETCH.clear()
        PREFETCH.update(_pf)
        SCENE["pip_line"] = _sp
    check("1.4.4: texto de estado de las comprobaciones en paralelo → escena «check» con su comando y su estado",
          [(_dlpy_ctx(x), _dlpy_state(x)) for x in ("Comprobando actualizaciones", "Todo al día · 3 comprobaciones · 0.9 s", "No se pudo comprobar actualizaciones")],
          [("check", "run"), ("check", "ok"), ("check", "fail")])
    _n3 = dict(NET)
    try:
        NET["pip:yt-dlp-ejs"] = {"ok": True, "secs": 3.2, "code": None, "val": None, "err": None}
        _lj = "yt-dlp-ejs 0.8.0 · para YouTube"
        check("1.4.4: una verificación local de yt-dlp-ejs no se muestra como pip install ni toma el resultado de una instalación anterior",
              (_dlpy_topic(_lj), _dlpy_state(_lj), _dlpy_footer(_lj, "ok", "1.4.4", "yt-dlp-ejs", 36)[0], _dlpy_topic("Instalando yt-dlp-ejs==0.8.0")[1]),
              (("yt-dlp-ejs", 'metadata.version("yt-dlp-ejs")'), "ok", "DLpy 1.4.4 · yt-dlp-ejs", "pip install -U yt-dlp-ejs==0.8.0 --no-deps"))
    finally:
        NET.clear()
        NET.update(_n3)
    _hs = PREFETCH.get("hosts")
    try:
        PREFETCH["hosts"] = prefetch_hosts(["DLpy", "pip", "yt-dlp"])
        _tp = _dlpy_topic("Comprobando actualizaciones")
    finally:
        PREFETCH["hosts"] = _hs
    check("1.4.4: prefetch_hosts y el comando de la escena en paralelo",
          (prefetch_hosts(["DLpy", "pip", "yt-dlp"]), prefetch_hosts(["pip"]), prefetch_hosts(["DLpy"]), _tp),
          ("pypi.org x2 · github.com", "pypi.org", "github.com", ("actualizaciones", "GET pypi.org x2 · github.com")))

    # prefetch_phase: salen a la vez, el tiempo total es el del más lento (no la suma), y se anota cada resultado
    _stub = {k: globals()[k] for k in ("is_installed", "latest_version", "fetch_latest_release", "scene_note", "Bar")}
    _nets2, _pf2, _so, _notes = dict(NET), dict(PREFETCH), SCENE["on"], []

    class _NoBar:
        def start(self, *a, **k):
            pass

        def stop(self, *a, **k):
            pass

    def _slow(v, secs=0.25):
        def f(*a, **k):
            time.sleep(secs)
            return v
        return f
    try:
        NET.clear()
        globals().update({"is_installed": lambda m: True, "Bar": _NoBar, "scene_note": lambda t, hold=0.0: (_notes.append(t) or True)})
        globals()["latest_version"] = lambda n, timeout=6: (time.sleep(0.25), NET.__setitem__(n, {"ok": True, "secs": 0.25, "code": 200, "val": "1.0", "err": None}), "1.0")[2]
        globals()["fetch_latest_release"] = lambda timeout=5: (time.sleep(0.25), NET.__setitem__("DLpy", {"ok": True, "secs": 0.25, "code": 200, "val": "9.9.9", "err": None}), {"ver": "9.9.9"})[2]
        SCENE["on"] = True
        _t0 = time.time()
        _go = prefetch_phase(True, True)
        _el = time.time() - _t0
        _r1 = (_go, _el < 0.6, sorted(PREFETCH["res"]), PREFETCH["res"]["DLpy"], PREFETCH["n"], NET["check"]["ok"], NET["check"]["val"], _notes[:], PREFETCH["quiet_fail"])
        prefetch_summary()
        _r1 += (_notes[-1].startswith("Todo al día · 3 comprobaciones · "), PREFETCH["on"])
        _notes.clear()
        PREFETCH["changed"] = True
        PREFETCH["on"] = True
        prefetch_summary()
        _r1 += (_notes[:],)
        _notes.clear()
        globals()["latest_version"] = lambda n, timeout=6: (_ for _ in ()).throw(_ue.URLError("x"))
        globals()["fetch_latest_release"] = lambda timeout=5: (_ for _ in ()).throw(_ue.URLError("x"))
        NET.clear()
        _go2 = prefetch_phase(True, True)
        _r2 = (_go2, [NET[k]["err"] for k in ("DLpy", "pip", "yt-dlp")], NET["check"]["ok"], NET["check"]["err"], _notes[:], PREFETCH["quiet_fail"])
        _notes.clear()
        _go3 = prefetch_phase(True, False)
        _r3 = (_go3, PREFETCH["on"], _notes[:])
        globals()["PREFETCH_MAX"] = 0.1
        globals()["latest_version"] = _slow("1.0", 0.6)
        globals()["fetch_latest_release"] = _slow({"ver": "1"}, 0.6)
        NET.clear()
        prefetch_phase(True, True)
        _r4 = ([NET[k]["err"] for k in ("DLpy", "pip", "yt-dlp")], NET["check"]["err"])
    finally:
        globals().update(_stub)
        globals()["PREFETCH_MAX"] = 14.0
        SCENE["on"] = _so
        NET.clear()
        NET.update(_nets2)
        PREFETCH.clear()
        PREFETCH.update(_pf2)
    check("1.4.4: comprobaciones en paralelo: salen a la vez (tardan lo del más lento), resumen «Todo al día» y nada de resumen si hubo algo que actualizar",
          _r1, (True, True, ["DLpy", "pip", "yt-dlp"], {"ver": "9.9.9"}, 3, True, "3 GET", ["Comprobando actualizaciones"], False, True, False, []))
    check("1.4.4: si todas fallan: causa en cada una, un solo aviso en la escena y los pasos de cada una no lo repiten; con una sola comprobación no hay paralelo; con tope vencido cuenta como timeout",
          (_r2, _r3, _r4),
          ((True, ["sin red", "sin red", "sin red"], False, "3 de 3 con error", ["Comprobando actualizaciones", "No se pudo comprobar actualizaciones"], True),
           (False, False, []), (["timeout", "timeout", "timeout"], "3 de 3 con error")))

    # pip_run anota cómo terminó
    _os_sys, _pn = os.system, dict(NET)
    try:
        os.system = lambda c: 0
        pip_run(["install", "-U", "zz-pkg", "--no-deps"])
        _p1 = dict(NET["pip:zz-pkg"])
        os.system = lambda c: 256
        pip_run(["install", "-U", "zz-pkg==1", "--no-deps"])
        _p2 = dict(NET["pip:zz-pkg"])
    finally:
        os.system = _os_sys
        NET.clear()
        NET.update(_pn)
    check("1.4.4: pip_run anota si pip salió bien o con qué código falló", (_p1["ok"], _p2["ok"], _p2["err"]), (True, False, "pip falló (1)"))

    # modo calmado: el cambio de texto no pasa por ruido
    _calm = SCENE_CALM
    try:
        globals()["SCENE_CALM"] = True
        _c0, _c1 = {0: "a", 1: "b"}, {0: "c"}
        _m = [scene_morph(_c0, _c1, p, 1.0) for p in (0.3, 0.7)]
    finally:
        globals()["SCENE_CALM"] = _calm
    check("1.4.4: modo calmado: el texto viejo se queda y el nuevo entra de golpe (sin ruido)", _m,
          [{0: ("a", 0), 1: ("b", 0)}, {0: ("c", 2)}])
    check("DLPY 1.3.3: estado run / ok / fail según el texto (un proceso en curso, su resultado o su fallo; «Analizando enlace · puede tardar más» sigue en curso)",
          [_dlpy_state(x) for x in ("Instalando yt-dlp", "Comprobando pip", "Actualizando pip → 26.0", "Analizando enlace · puede tardar más", "Preparando",
                                    "yt-dlp 2026.1.1 · instalado", "DLpy 1.3.2 · última versión", "Nueva versión de DLpy · 1.3.2 → 1.3.3",
                                    "No se pudo instalar yt-dlp", "Error: HTTP Error 403", "")],
          ["run"] * 5 + ["ok"] * 3 + ["fail", "fail", "run"])
    _dr, _do, _df = (scene_dlpy_cells(60, 6, ra, rb, 3.0, "1.3.3", x, 0.2) for x in ("Instalando yt-dlp", "yt-dlp 2026.1.1 · instalado", "No se pudo instalar yt-dlp"))
    _rt = lambda c: "".join(c[(x, 11)][0] for x in range(1, 61) if (x, 11) in c)
    check("DLPY 1.3.3: en curso el comando apenas se teclea (tt 0,2 s); un resultado ya lo muestra entero con ✓ / ✗ y sin indicador giratorio",
          ("pip install -U yt-dlp --no-deps" in _rt(_dr), "pip install -U yt-dlp --no-deps✓" in _rt(_do), "pip install -U yt-dlp --no-deps✗" in _rt(_df),
           any(ch in _rt(_do) + _rt(_df) for ch in "|/-\\") and False),
          (False, True, True, False))
    check("DLPY 1.3.3: el marco crece hasta 52 columnas para el comando de pip entero y en terminales estrechas sigue dentro de sus columnas",
          (max(x for (x, y) in scene_dlpy_cells(60, 6, ra, rb, 3.0, "1.3.3", "Instalando yt-dlp", 5.0) if y == 10) - min(x for (x, y) in scene_dlpy_cells(60, 6, ra, rb, 3.0, "1.3.3", "Instalando yt-dlp", 5.0) if y == 10) + 1,
           max(x for (x, _y) in scene_dlpy_cells(31, 6, ra, rb, 3.0, "1.3.3", "Instalando yt-dlp-ejs==0.8.0", 5.0)) < 31,
           "…" in "".join(v[0] for v in scene_dlpy_cells(31, 6, ra, rb, 3.0, "1.3.3", "Instalando yt-dlp-ejs==0.8.0", 5.0).values())),
          (52, True, True))
    check("DLPY 1.3.3: el comando corre desde que se ve: nada mientras la intro o el cambio de dibujo lo tapan, y si el texto cambia después cuenta desde que la escena lo vio",
          (dlpy_type_time(5.0, 1.0, 5.0), dlpy_type_time(5.0 + SCENE_SWAP, 1.0, 5.0), round(dlpy_type_time(6.0, 1.0, 5.0), 6), round(dlpy_type_time(9.0, 8.0, 2.0), 6)),
          (0.0, 0.0, round(1.0 - SCENE_SWAP, 6), 1.0))
    _txt = lambda c: "".join(v[0] for _k, v in sorted(c.items(), key=lambda kv: (kv[0][1], kv[0][0])))
    check("DLPY 1.2.7: «Comprobando pip» no teclea yt-dlp y el título dice pip",
          ("yt-dlp" in _txt(scene_dlpy_cells(60, 6, ra, rb, 3.0, "1.2.7", "Comprobando pip")), "a-Shell·pip" in _txt(scene_dlpy_cells(60, 6, ra, rb, 3.0, "1.2.7", "Comprobando pip")).replace(" ", "").replace("─", "")), (False, True))
    check("DLPY 1.0.3: boot contextual (analizando, github, yt-dlp) cambia comando y título",
          ("a-Shell" in rowtxt(da, 10), "a-Shell" in rowtxt(dg,10), "a-Shell" in rowtxt(dy,10)), (True, True, True))
    o_, n_ = {(5, 5): ("a", ra, None)}, {(5, 5): ("b", rb, None), (6, 5): ("c", rb, None)}
    mids = [scene_swap_cells(o_, n_, q / 10.0, 3, ra, rb) for q in range(1, 10)]
    check("transición del centro: en 0 el viejo, en 1 el nuevo, a mitad hay ruido y es repetible",
          (scene_swap_cells(o_, n_, 0.0, 3, ra, rb) == o_, scene_swap_cells(o_, n_, 1.0, 3, ra, rb) == n_,
           any(v[0] in SITE_GLITCH for m in mids for v in m.values()),
           mids == [scene_swap_cells(o_, n_, q / 10.0, 3, ra, rb) for q in range(1, 10)]), (True, True, True, True))
    check("escena: qué dibujo ocupa el centro (D L P Y manda; al terminar la conversión, el del sitio)",
          [scene_motif_kind({"brand": True, "conv": {"end": None}}), scene_motif_kind({"conv": {"end": None}}),
           scene_motif_kind({"conv": {"end": 1.0}}), scene_motif_kind({})], ["dlpy", "conv", None, None])
    # 1.1.3: escenas de unión, guardado y envío
    def _rt(cs, y):
        return "".join(cs[(x, y)][0] if (x, y) in cs else " " for x in range(1, 70)).strip()
    check("escena 1.1.3: el dibujo del centro según el texto de estado (D L P Y > conversión > unión > guardado)",
          [scene_motif_kind(x) for x in ({"label": "Uniendo pistas"}, {"label": "Ajustando pistas"}, {"label": "Guardando"},
                                         {"label": "Descargando video"}, {"label": "Uniendo pistas", "conv": {"end": None}},
                                         {"label": "Guardando", "brand": True}, {"label": "Enviando a DLpy", "brand": True},
                                         {"label": "Enviando a DLpy"}, {"label": "Enviando a DLpy", "brand": True, "last_error": "x"})],
          ["rail", "rail", "rail", "rail", "conv", "dlpy", "send", None, "dlpy"])
    m1, m2 = scene_merge_cells(60, 6, ra, rb, 1.0), scene_merge_cells(60, 6, ra, rb, 1.2)
    check("unión: VIDEO arriba, AUDIO abajo, el empalme ╮ ├ ╯ y tres filas de alto",
          ("VIDEO" in _rt(m1, 11), "AUDIO" in _rt(m1, 13), "╮" in _rt(m1, 11), "├" in _rt(m1, 12), "╯" in _rt(m1, 13),
           {y for (_x, y) in m1} == {11, 12, 13}), (True, True, True, True, True, True))
    check("unión: repetible, se mueve y cabe en 31 columnas (con y sin etiquetas)",
          (m1 == scene_merge_cells(60, 6, ra, rb, 1.0), m1 != m2,
           max(x for (x, _y) in scene_merge_cells(31, 6, ra, rb, 1.0)) < 31,
           max(x for (x, _y) in scene_merge_cells(31, 6, ra, rb, 2.3)) < 31, min(x for (x, _y) in scene_merge_cells(31, 6, ra, rb, 1.0)) >= 1),
          (True, True, True, True, True))
    sv0, sv1 = scene_save_cells(60, 6, ra, rb, 0.3), scene_save_cells(60, 6, ra, rb, SAVE_STREAM_SECS + 0.5)
    check("guardado: el archivo, la carpeta y, al llegar, el ✓ (antes del final no hay ✓)",
          ("▓▓▓" in _rt(sv0, 12), os.path.basename(FILES_DIR) in _rt(sv0, 12), "✓" in _rt(sv0, 12), "✓" in _rt(sv1, 12),
           {y for (_x, y) in sv1} == {11, 12, 13}), (True, True, False, True, True))
    check("guardado: repetible, se mueve mientras guarda, cabe en 31 columnas y con «files» si falta sitio",
          (sv0 == scene_save_cells(60, 6, ra, rb, 0.3), sv0 != scene_save_cells(60, 6, ra, rb, 0.5),
           max(x for (x, _y) in scene_save_cells(31, 6, ra, rb, 0.3)) < 31, max(x for (x, _y) in scene_save_cells(31, 6, ra, rb, 1.8)) < 31,
           "files" in _rt(scene_save_cells(31, 6, ra, rb, 0.3), 12)), (True, True, True, True, True))
    se0, se1 = scene_send_cells(60, 6, ra, rb, 0.5, "DLPY"), scene_send_cells(60, 6, ra, rb, 1.2, "DLPY")
    check("envío: el chip del atajo, el cometa en vuelo (●) y la onda al llegar",
          ("DLPY" in _rt(se0, 12), "●" in _rt(se0, 12), "●" in _rt(se1, 12), "(" in _rt(se1, 12) and ")" in _rt(se1, 12),
           "(" in _rt(se0, 12), {y for (_x, y) in se0} == {11, 12, 13}), (True, True, False, True, False, True))
    check("envío: ciclo que se repite, repetible, se mueve y cabe en 31 columnas",
          (scene_send_cells(60, 6, ra, rb, 0.5) == scene_send_cells(60, 6, ra, rb, 0.5 + SEND_CYCLE), se0 == scene_send_cells(60, 6, ra, rb, 0.5, "DLPY"),
           se0 != scene_send_cells(60, 6, ra, rb, 0.7), max(x for (x, _y) in scene_send_cells(31, 6, ra, rb, 1.1, "ABCDEFGH")) < 31,
           min(x for (x, _y) in scene_send_cells(31, 6, ra, rb, 1.1)) >= 1), (True, True, True, True, True))
    check("escena 1.1.3: unión y guardado van a CONV_FPS; el envío, a DLPY_FPS; la conversión manda sobre la unión y va a CONV_RUN_FPS (1.2.1)",
          [scene_fps({"label": "Uniendo pistas"}, {}, 20.0, SITE_HOLD_AT * SITE_SECS), scene_fps({"label": "Guardando"}, {}, 20.0, SITE_HOLD_AT * SITE_SECS),
           scene_fps({"label": "Enviando a DLpy", "brand": True}, {}, 20.0, SITE_HOLD_AT * SITE_SECS),
           scene_fps({"label": "Uniendo pistas", "conv": {"end": None}}, {}, 20.0, SITE_HOLD_AT * SITE_SECS)],
          [CONV_FPS, CONV_FPS, DLPY_FPS, CONV_RUN_FPS])
    _sh = dict(SCENE)
    try:
        SCENE.update(on=False)
        t_ = time.monotonic()
        check("escena 1.1.3: sin escena (o con error) scene_hold no espera", scene_hold(5.0), False)
        SCENE.update(on=True, last_error="x")
        check("escena 1.1.3: con un error scene_hold no espera", (scene_hold(5.0), time.monotonic() - t_ < 1.0), (False, True))
    finally:
        SCENE.clear()
        SCENE.update(_sh)
    # 1.1.3: la unión entra y sale del centro con el mismo iris, sin saltos
    sg = {"geo": (60, 24, 6, 17), "a": ra, "b": rb, "brand": False, "conv": None, "label": "Uniendo pistas", "done": set()}
    stg = {"mcur": None, "mprev": None, "mt": None, "ms": 0.0, "msp": 0.0, "site_done": set(), "site_done_at": {}, "site_prev_cells": {}, "site_trans_t": None}
    for q, tt_ in enumerate((2.0, 2.3, 2.9)):
        scene_motif(sg, stg, {(30, 11): ("x", ra, None)}, tt_, 1.16, q)
    check("escena 1.1.3: «Uniendo pistas» toma el centro (1.4.6: como tarjeta del carril)", stg["mcur"], "rail")
    sg["label"] = "Guardando"
    scene_motif(sg, stg, {}, 3.0, 1.16, 7)
    check("escena 1.4.6: de la unión al guardado el centro sigue siendo el mismo carril: ni morph ni espera de loop", (stg["mcur"], stg["hold_to"]), ("rail", None))
    scene_motif(sg, stg, {}, 4.0, 1.16, 8)
    check("escena 1.4.6: sin otro dibujo de por medio (la unión y el guardado son tarjetas, no cambian el centro)", (stg["mcur"], stg["mprev"]), ("rail", None))
    # 1.1.5: la limpieza va dentro de la escena (sin caer al shell)
    check("escena 1.1.5: «Limpiando» tiene su dibujo (conversión > limpieza; D L P Y manda) y ya no queda nada que preguntar",
          ([scene_motif_kind(x) for x in ({"label": "Limpiando · 3 a la papelera"}, {"label": "Limpiando · 3", "brand": True},
                                          {"label": "Limpiando · 3", "conv": {"end": None}}, {"label": "Descargando video"})],
           scene_questions()), (["clean", "dlpy", "conv", "rail"], False))
    cl1, cl2 = scene_clean_cells(60, 6, ra, rb, 0.3, 3), scene_clean_cells(60, 6, ra, rb, 0.6, 3)
    check("limpieza: archivos a la izquierda, la papelera a la derecha y tres filas de alto",
          ("▬" in _rt(cl1, 11), "papelera" in _rt(cl1, 12), _rt(cl1, 12).find("▬") < _rt(cl1, 12).find("papelera"),
           {y for (_x, y) in cl1} == {11, 12, 13}), (True, True, True, True))
    check("limpieza: repetible, se mueve, cabe en 31 columnas y sin archivos queda quieta",
          (cl1 == scene_clean_cells(60, 6, ra, rb, 0.3, 3), cl1 != cl2, max(x for (x, _y) in scene_clean_cells(31, 6, ra, rb, 0.4, 5)) < 31,
           min(x for (x, _y) in scene_clean_cells(31, 6, ra, rb, 0.4, 5)) >= 1,
           scene_clean_cells(60, 6, ra, rb, 0.3, 0) == scene_clean_cells(60, 6, ra, rb, 1.7, 0)), (True, True, True, True, True))
    ce1, ce2 = scene_empty_cells(60, 6, ra, rb, 0.3, 3), scene_empty_cells(60, 6, ra, rb, 0.6, 3)
    check("escena 1.1.7: «Vaciando» tiene su dibujo (el de limpieza es otro; conversión y D L P Y mandan)",
          [scene_motif_kind(x) for x in ({"label": "Vaciando · 3 de la papelera"}, {"label": "Vaciando · 3", "brand": True},
                                         {"label": "Vaciando · 3", "conv": {"end": None}}, {"label": "Limpiando · 3 a la papelera"})],
          ["empty", "dlpy", "conv", "clean"])
    check("vaciado: la papelera a la izquierda, sale en tres filas, repetible, se mueve y cabe en 31 columnas",
          ("papelera" in _rt(ce1, 12), {y for (_x, y) in ce1} == {11, 12, 13}, ce1 == scene_empty_cells(60, 6, ra, rb, 0.3, 3), ce1 != ce2,
           max(x for (x, _y) in scene_empty_cells(31, 6, ra, rb, 0.4, 5)) < 31, min(x for (x, _y) in scene_empty_cells(31, 6, ra, rb, 0.4, 5)) >= 1),
          (True, True, True, True, True, True))
    check("vaciado: sin archivos queda quieto; no se superpone con el dibujo de limpieza",
          (scene_empty_cells(60, 6, ra, rb, 0.3, 0) == scene_empty_cells(60, 6, ra, rb, 1.7, 0), ce1 != scene_clean_cells(60, 6, ra, rb, 0.3, 3)), (True, True))
    check("escena 1.1.8: texto con lo movido y lo borrado",
          [clean_label("Limpiando", 3, 2, False), clean_label("Limpiando", 1, 1, False), clean_label("Limpiando", 3, 0, False),
           clean_label("Vaciando", None, 2, False), clean_label("Limpiando", 12, 3, True)],
          ["Limpiando · 3 movidos · 2 borrados", "Limpiando · 1 movido · 1 borrado", "Limpiando · 3 movidos",
           "Vaciando · 2 borrados", "Limpiando · 12↓ · 3×"])
    check("escena 1.1.8: el texto largo cabe en 25 columnas abreviado",
          dwidth(clean_label("Limpiando", 99, 99, True)) <= 31 - 6, True)
    cw1 = scene_wait_conv_cells(60, 6, ra, rb, 0.4, "VP9", "HEVC", 15.0)
    check("escena 1.1.9: esperando el Enter el centro es «ask» (conversión y D L P Y mandan) y lo demás no cambia",
          [scene_motif_kind(x) for x in ({"label": "Convirtiendo", "ask": {"secs": 20}}, {"label": "x", "ask": {"secs": 20}, "brand": True},
                                         {"label": "x", "ask": {"secs": 20}, "conv": {"end": None}}, {"label": "x", "ask": None})],
          ["ask", "dlpy", "conv", None])
    _w = _rt(cw1, 12)
    check("espera 1.2.0: origen → bloques → tecla Enter → destino en tres filas, repetible, se mueve y cabe en 31 columnas",
          ({y for (_x, y) in cw1} == {11, 12, 13}, 0 <= _w.find("VP9") < _w.find("Enter") < _w.find("HEVC"), "·" in _w and "░" not in _w,
           cw1 == scene_wait_conv_cells(60, 6, ra, rb, 0.4, "VP9", "HEVC", 15.0), cw1 != scene_wait_conv_cells(60, 6, ra, rb, 1.9, "VP9", "HEVC", 15.0),
           max(x for (x, _y) in scene_wait_conv_cells(31, 6, ra, rb, 0.4, "VP9", "HEVC", 3.0)) < 31,
           min(x for (x, _y) in scene_wait_conv_cells(31, 6, ra, rb, 0.4, "VP9", "HEVC", 3.0)) >= 1,
           "↵" in _rt(scene_wait_conv_cells(31, 6, ra, rb, 0.4, "VP9", "HEVC", 3.0), 12)), (True,) * 8)
    check("espera 1.2.0: se distingue de la conversión, el ensayo enciende el destino y los últimos 5 s cambian de color; sin formatos no falla",
          (cw1 != scene_conv_cells(60, 6, ra, rb, 0.4, "VP9", "HEVC"),
           scene_wait_conv_cells(60, 6, ra, rb, 2.8, "VP9", "HEVC", 15.0) != scene_wait_conv_cells(60, 6, ra, rb, 0.4, "VP9", "HEVC", 15.0),
           scene_wait_conv_cells(60, 6, ra, rb, 0.4, "VP9", "HEVC", 3.0) != cw1, bool(scene_wait_conv_cells(60, 6, ra, rb, 0.4, None, None))),
          (True,) * 4)
    _al = []
    for _W in (31, 40, 60, 80):
        _ww, _cc = scene_wait_conv_cells(_W, 6, ra, rb, 0.4, "VP9", "HEVC", 15.0), scene_conv_cells(_W, 6, ra, rb, 0.4, "VP9", "HEVC")
        _ex = lambda cs, ch: [x for (x, y), v in cs.items() if y == 11 and v[0] == ch]
        _al.append((_ex(_cc, "╭")[0] in _ex(_ww, "╭"), _ex(_cc, "╭")[-1] in _ex(_ww, "╭"), _ex(_cc, "╮")[-1] in _ex(_ww, "╮")))
    check("escena 1.2.1: la espera del Enter y la conversión ponen los chips de origen y de destino en el mismo sitio (a 31, 40, 60 y 80 columnas)",
          _al, [(True, True, True)] * 4)
    # 1.2.1: la pregunta de convertir «precarga» la animación de la conversión
    _wq = scene_wait_conv_cells(60, 6, ra, rb, 5.3, "VP9", "HEVC", 15.0)          # a los 5.3 s del ciclo ya no hay paquete ni estela
    _cq = scene_conv_cells(60, 6, ra, rb, 0.4, "VP9", "HEVC")
    _lane = lambda cs, w: "".join(cs[(x, 12)][0] for x in range(1, 70) if (x, 12) in cs and cs[(x, 12)][0] in "·•●")
    _kx = [x for (x, y), v in _wq.items() if y == 11 and v[0] == "╭"]
    _lx = [x for (x, y), v in _wq.items() if y == 12 and v[0] in "·"]
    check("pregunta 1.2.1: misma vía de puntos que la conversión, con la tecla Enter en el centro exacto de la vía y sin nada más",
          (set(_lane(_wq, 60)) == {"·"}, set(_lane(_cq, 60)) <= {"·", "•", "●"}, len(_kx) == 3,
           len(_kx) == 3 and abs((sorted(_kx)[1] + 4) - (sorted(_kx)[0] + 7 + sorted(_kx)[2] - 1) / 2.0) <= 0.5,
           not any(ch in _rt(_wq, 12) for ch in "▘▝▗▖░▒▓█")), (True,) * 5)
    _pk = [scene_wait_conv_cells(60, 6, ra, rb, t, "VP9", "HEVC", 15.0) for t in (0.3, 1.0, 1.8, 2.6, 3.4)]
    check("pregunta 1.2.1: en el ensayo un paquete recorre la vía y sale refinado, y el destino se enciende al llegar",
          (any("●" in _rt(c, 12) for c in _pk), len({tuple(sorted(c.items())) for c in _pk}) == 5,
           _pk[3][(max(x for (x, y) in _pk[3] if y == 11), 11)] != _wq[(max(x for (x, y) in _wq if y == 11), 11)] or
           any(c[(max(x for (x, y) in c if y == 11), 11)] != _wq[(max(x for (x, y) in _wq if y == 11), 11)] for c in _pk)), (True, True, True))
    _f1, _f0 = scene_conv_cells(60, 6, ra, rb, 0.1, "VP9", "HEVC", None, 0.9), scene_conv_cells(60, 6, ra, rb, 0.1, "VP9", "HEVC", None, 0.0)
    _f9 = scene_conv_cells(60, 6, ra, rb, 0.1, "VP9", "HEVC", None, 0.9)
    _fl = [scene_conv_cells(60, 6, ra, rb, t, "VP9", "HEVC", 100) for t in (0.0, 0.2)]
    _st = scene_wait_conv_cells(60, 6, ra, rb, 3.0, "VP9", "HEVC", 15.0)
    check("1.2.1: la tecla Enter se apaga al pasar a la conversión (y sin fade no hay tecla), el destino destella al 100 % y el ensayo deja estela",
          ("Enter" in _rt(_f1, 12), "Enter" not in _rt(_f0, 12), _f1 != scene_conv_cells(60, 6, ra, rb, 0.1, "VP9", "HEVC", None, 0.3),
           _fl[0] != _fl[1], "•" in _rt(_st, 12), scene_fps({"conv": {"end": None}}, {"key_fade_t": 10.0}, 10.1, 5.0), scene_fps({"conv": {"end": None}}, {"key_fade_t": 10.0}, 11.0, 5.0)),
          (True, True, True, True, True, SITE_FPS, CONV_RUN_FPS))
    # 1.4.2: sustituir un archivo existente (pregunta en la escena como la de convertir + animación al guardar)
    _r0, _r1 = scene_wait_conv_cells(60, 6, ra, rb, 1.0, "VIEJO", "NUEVO", 15.0, swap=True), scene_wait_conv_cells(60, 6, ra, rb, 4.6, "VIEJO", "NUEVO", 15.0, swap=True)
    _r2 = scene_wait_conv_cells(60, 6, ra, rb, 1.0, "VIEJO", "NUEVO", 15.0)
    check("1.4.2: la pregunta de sustituir: chips VIEJO → NUEVO con Enter en la vía; al llegar el paquete el viejo se deshace; no cambia la de convertir",
          ("VIEJO" in _rt(_r0, 12), "NUEVO" in _rt(_r0, 12), "Enter" in _rt(_r0, 12), "VIEJO" not in _rt(_r1, 12), "NUEVO" in _rt(_r1, 12), _r1 != scene_wait_conv_cells(60, 6, ra, rb, 4.6, "VIEJO", "NUEVO", 15.0),
           _r2 == scene_wait_conv_cells(60, 6, ra, rb, 1.0, "VIEJO", "NUEVO", 15.0, swap=False)), (True,) * 7)
    check("1.4.2: respuestas de sustituir: Enter sustituye, n conserva y sin respuesta se sustituye; textos y marcas de teclas",
          (scene_ask_lines(60, None, 14.2, "replace"), scene_ask_lines(20, None, 3, "replace"), ask_hint_texts(60, "replace")[1], ask_hint_texts(60)[1],
           sorted(ask_key_mask("Enter sustituir · n conservar"))[:5], sorted(ask_key_mask("Enter sustituir · n conservar"))[-1:],
           scene_motif_kind({"label": "x", "ask": {"kind": "replace"}}), scene_motif_kind({"label": "x", "ask": {"kind": None}}),
           scene_motif_kind({"label": "Sustituyendo"}), SCENE["on"] or scene_ask_enter(kind="replace"), replace_confirmed()),
          (("Toca la pantalla · Enter sustituir · n conservar", "sin respuesta se sustituye · 15 s"), ("Enter sí · n no", "3 s"),
           "¿Sustituir el archivo?", "¿Convertir este video?", [0, 1, 2, 3, 4], [18], "replace", "ask", "subst", None, None))
    _w0, _w1 = scene_subst_cells(60, 6, ra, rb, 0.2), scene_subst_cells(60, 6, ra, rb, SWAP_STREAM_SECS + 0.5)
    check("1.4.2: al guardar sustituyendo: el paquete cruza, el viejo se deshace y queda el ✓ con NUEVO",
          ("VIEJO" in _rt(_w0, 12), "✓" not in _rt(_w0, 12), "VIEJO" not in _rt(_w1, 12), "NUEVO" in _rt(_w1, 12), "✓" in _rt(_w1, 12),
           MOTIFS["subst"].draw({}, {}, _MotifCtx(60, 6, ra, rb, 4.0, 3, {}, set()), 4.0) == scene_subst_cells(60, 6, ra, rb, 0.0),
           motif_loop_left({"geo": (60, 24, 6, 17)}, {"ms": 0.0, "mt": None}, "subst", 0.3) == max(0.0, SWAP_STREAM_SECS + 0.35 - 0.3)), (True,) * 7)
    _dd2 = _MotifCtx(60, 6, ra, rb, 5.0, 3, {"v": ("1080p", 1.0), "a": ("AAC", 1.0)}, set())
    _S2 = {"geo": (60, 24, 6, 17), "a": ra, "b": rb, "mode": "both", "mode_orig": "both", "aspect": 16 / 9.0, "res": 1080, "ask": {"secs": 20, "t0": time.time(), "src": "VIEJO", "dst": "NUEVO"},
           "conv": None, "label": "x", "clean": 3, "check": {"items": None, "verdict": None}}
    _rows = {k: {y for (_x, y) in m.draw(_S2, {"ms": 4.0, "mt": None, "cinfo": ("VP9", "HEVC", 4.0)}, _dd2, 4.0)} for k, m in MOTIFS.items() if k not in ("dlpy", "send", "first", "updated", "rail")}
    check("1.4.2: ningún dibujo del centro invade la fila en blanco ni el texto de estado (todos dentro de y0+4 … y0+9); el estado va en y0+11",
          (all(r and max(r) <= 6 + 4 + BADGE_ROW and min(r) >= 6 + 4 for r in _rows.values()), SCENE_STATUS_ROW - (4 + BADGE_ROW), SCENE_ROWS), (True, 2, SCENE_STATUS_ROW + 2))
    check("escena 1.1.7: el vaciado va a CONV_FPS",
          scene_fps({"label": "Vaciando · 2 de la papelera"}, {}, 20.0, SITE_HOLD_AT * SITE_SECS), CONV_FPS)
    check("escena 1.1.5: la limpieza va a CONV_FPS",
          scene_fps({"label": "Limpiando · 2 a la papelera"}, {}, 20.0, SITE_HOLD_AT * SITE_SECS), CONV_FPS)
    hq, stq = SITE_HOLD_AT * SITE_SECS, {"mt": 10.0, "t": 0.0, "tt": None}
    check("escena: cuadros por segundo (intro, transiciones y cierre a tope; convirtiendo y DLPY, menos)",
          [scene_fps({}, {}, 0.5, hq), scene_fps({"brand": True}, stq, 10.3, hq), scene_fps({"brand": True}, stq, 20.0, hq),
           scene_fps({"conv": {"end": None}}, stq, 20.0, hq), scene_fps({"conv": {"end": None}, "k_out": 0.2}, stq, 20.0, hq),
           scene_fps({"conv": {"end": 3.0}}, stq, 20.0, hq)], [SITE_FPS, SITE_FPS, DLPY_FPS, CONV_RUN_FPS, SITE_FPS, SITE_FPS])
    # ── 1.4.1: registro de dibujos (MOTIFS), estado unificado, bolsas de streams y cierre ──
    _kn = {"dlpy", "conv", "ask", "replace", "subst", "check", "merge", "save", "clean", "empty", "send", "first", "updated", "download", "idle", "rail"}
    _sn = {scene_motif_kind(x) for x in ({"label": "Revisando archivo"}, {"label": "Uniendo pistas"}, {"label": "Ajustando pistas"},
                                         {"label": "Guardando"}, {"label": "Sustituyendo"}, {"label": "x", "ask": {"kind": "replace"}},
                                         {"label": "Limpiando · 3"}, {"label": "Vaciando · 3"}, {"label": "x", "brand": True},
                                         {"label": "Enviando a DLpy", "brand": True}, {"conv": {"end": None}},
                                         {"label": "Convirtiendo", "ask": {"secs": 20}}, {"label": "x", "brand": True, "welcome": {"kind": "first"}},
                                         {"label": "x", "brand": True, "welcome": {"kind": "updated"}},
                                         {"label": "Descargando video"}, {"label": "Preparando", "past_dl": True})}
    check("escena 1.4.1: MOTIFS tiene una fila por dibujo, cada estado cae en una y lo demás no pide dibujo",
          (set(MOTIFS) == _kn, _sn == (_kn - set(RAIL_KINDS)) | {"rail"}, all(callable(m.draw) for m in MOTIFS.values()), scene_motif_kind({"label": "Preparando"})),
          (True, True, True, None))
    check("escena 1.4.1: solo unión, guardado, limpieza, papelera, revisión, arranque, descarga y pulso van a CONV_FPS (marca light)",
          {k for k, m in MOTIFS.items() if m.light}, {"merge", "save", "subst", "clean", "empty", "check", "first", "updated", "download", "idle", "rail"})
    # ── 1.4.5: una sola escena: «Descarga», «Pulso» y los nombres de los motivos ──
    _Sd = {"stream_total": 3, "stream_seen": 2, "skind": {1: "video", 2: "audio"}, "spct": {1: 100.0, 2: 40.0}, "mode_orig": "both"}
    check("escena 1.4.5: filas de Descarga: la bajada queda «hecho», la actual «activa» con su % real y la que falta «espera» (se adivina por el modo)",
          scene_down_rows(_Sd), [("VIDEO", 100.0, "hecho"), ("AUDIO", 40.0, "activa"), ("AUDIO", None, "espera")])
    check("escena 1.4.5: con una sola pista: una fila activa; sin % (total desconocido) sigue activa; con 100 % pasa a hecho",
          (scene_down_rows({}), scene_down_rows({"stream_total": 1, "stream_seen": 1, "spct": {1: None}, "skind": {1: "audio"}}),
           scene_down_rows({"stream_total": 1, "stream_seen": 1, "spct": {1: 100.0}})),
          ([("VIDEO", None, "activa")], [("AUDIO", None, "activa")], [("VIDEO", 100.0, "hecho")]))
    _w5 = scene_down_rows({"stream_total": 5, "stream_seen": 4, "mode_orig": "audio"})
    check("escena 1.4.5: con más de 3 pistas la ventana (3 filas) sigue a la activa",
          (len(_w5), [r[2] for r in _w5], len(scene_down_rows({"stream_total": 5, "stream_seen": 1})),
           [r[2] for r in scene_down_rows({"stream_total": 5, "stream_seen": 1})]),
          (3, ["hecho", "activa", "espera"], 3, ["activa", "espera", "espera"]))
    _r3 = scene_down_rows(_Sd)
    dc1, dc2 = scene_down_cells(60, 6, ra, rb, 0.3, _r3), scene_down_cells(60, 6, ra, rb, 0.6, _r3)
    check("escena 1.4.5: Descarga: etiquetas por fila, ✓ solo en la pista hecha, tres filas de alto, repetible y se mueve",
          ("VIDEO" in _rt(dc1, 11), "AUDIO" in _rt(dc1, 12), "✓" in _rt(dc1, 11), "✓" not in _rt(dc1, 12), "✓" not in _rt(dc1, 13),
           {y for (_x, y) in dc1} == {11, 12, 13}, dc1 == scene_down_cells(60, 6, ra, rb, 0.3, _r3), dc1 != dc2,
           scene_down_cells(60, 6, ra, rb, 0.3, _r3) == scene_down_cells(60, 6, ra, rb, 0.3 + DOWN_CYCLE, _r3)), (True,) * 9)
    _nb = lambda cs, y: sum(1 for (_x, yy), v in cs.items() if yy == y and v[0] == "━")
    check("escena 1.4.5 (1.5.6): Descarga: la vía de la pista activa no crece con el % (solo paquetes) y no pasa de la vía; hecha, queda llena y sin paquete",
          (_nb(scene_down_cells(60, 6, ra, rb, 0.3, [("VIDEO", 10.0, "activa")]), 12) == _nb(scene_down_cells(60, 6, ra, rb, 0.3, [("VIDEO", 90.0, "activa")]), 12),
           _nb(scene_down_cells(60, 6, ra, rb, 0.3, [("VIDEO", 100.0, "hecho")]), 12),
           "●" in _rt(scene_down_cells(60, 6, ra, rb, 0.3, [("VIDEO", 10.0, "activa")]), 12),
           "●" in _rt(scene_down_cells(60, 6, ra, rb, 0.3, [("VIDEO", 100.0, "hecho")]), 12)), (True, 16, True, False))
    check("escena 1.4.5: Descarga cabe en 31 columnas (con 1, 2 y 3 pistas) y nunca sale de y0+5 … y0+7",
          (all(max(x for (x, _y) in scene_down_cells(31, 6, ra, rb, t_, _r3[:n_])) < 31 and min(x for (x, _y) in scene_down_cells(31, 6, ra, rb, t_, _r3[:n_])) >= 1
               for n_ in (1, 2, 3) for t_ in (0.1, 0.7, 1.2)),
           all({y for (_x, y) in scene_down_cells(31, 6, ra, rb, 0.5, _r3[:n_])} <= {11, 12, 13} for n_ in (1, 2, 3)),
           {y for (_x, y) in scene_down_cells(31, 6, ra, rb, 0.5, _r3[:1])}, {y for (_x, y) in scene_down_cells(31, 6, ra, rb, 0.5, _r3[:2])}),
          (True, True, {12}, {11, 13}))
    ip1, ip2 = scene_idle_cells(60, 6, ra, rb, 0.3), scene_idle_cells(60, 6, ra, rb, 0.8)
    check("escena 1.4.5: Pulso: una sola fila, centrada, repetible, se mueve, cierra su ciclo y cabe en 31 columnas",
          ({y for (_x, y) in ip1} == {12}, ip1 == scene_idle_cells(60, 6, ra, rb, 0.3), ip1 != ip2,
           scene_idle_cells(60, 6, ra, rb, 0.3) == scene_idle_cells(60, 6, ra, rb, 0.3 + PULSE_CYCLE),
           max(x for (x, _y) in scene_idle_cells(31, 6, ra, rb, 0.4)) < 31, min(x for (x, _y) in scene_idle_cells(31, 6, ra, rb, 0.4)) >= 1,
           (min(x for (x, _y) in ip1) + max(x for (x, _y) in ip1)) // 2 == 60 // 2 + 1), (True,) * 7)
    check("escena 1.4.5: cada motivo tiene su nombre (sin repetir, uno por fila de MOTIFS y el del sitio) y motif_name(None) es el del sitio",
          (set(MOTIF_NAMES) == set(MOTIFS) | {"site"}, len(set(MOTIF_NAMES.values())) == len(MOTIF_NAMES), motif_name(None), motif_name("download"),
           motif_name("idle"), motif_name("conv")), (True, True, "Sitio", "Descarga", "Pulso", "Conversión"))
    check("escena 1.4.5: «Descargando…» pide Descarga; D L P Y, la conversión y la espera mandan; sin descarga empezada no hay Pulso",
          [scene_motif_kind(x) for x in ({"label": "Descargando audio 2/2"}, {"label": "Descargando video", "brand": True},
                                         {"label": "Descargando video", "conv": {"end": None}}, {"label": "Descargando video", "ask": {"secs": 5}},
                                         {"label": "Analizando"}, {"label": "Analizando", "past_dl": True}, {"label": "Uniendo pistas", "past_dl": True})],
          ["rail", "dlpy", "conv", "ask", None, "idle", "rail"])
    _sv6 = dict(SCENE)
    try:
        SCENE.update(scene_defaults())
        SCENE.update(on=True, ta=2.0, label="Preparando descarga")
        scene_progress(10.0)                                          # sin «Descargando» no se anota nada
        _p0 = (dict(SCENE["spct"]), SCENE["past_dl"])
        scene_stream("video", 1, 2)
        scene_progress(40.0)
        scene_stream("audio", 2, 2, "es-US")
        scene_progress(None)
        _p1 = (dict(SCENE["skind"]), dict(SCENE["spct"]), SCENE["past_dl"], SCENE["label"])
        scene_progress(100.0)
        _p2 = dict(SCENE["spct"])
    finally:
        SCENE.clear()
        SCENE.update(_sv6)
    check("escena 1.4.5: scene_stream y scene_progress anotan qué es y cuánto lleva cada pista (y que la descarga ya empezó)",
          (_p0, _p1, _p2), (({}, False), ({1: "video", 2: "audio"}, {1: 40.0, 2: None}, True, "Descargando audio es-US 2/2"), {1: 40.0, 2: 100.0}))
    sj = {"geo": (60, 24, 6, 17), "a": ra, "b": rb, "brand": False, "conv": None, "label": "Preparando descarga", "done": set(), "mode_orig": "both",
          "stream_total": 2, "stream_seen": 0}
    stj = {"mcur": None, "mprev": None, "mt": None, "ms": 0.0, "msp": 0.0, "site_done": set(), "site_done_at": {}, "site_prev_cells": {}, "site_trans_t": None}
    scene_motif(sj, stj, {}, 2.0, 1.16, 1)
    _j0 = (stj["mcur"], sj["motivo"])
    sj.update(label="Descargando video 1/2", stream_seen=1, skind={1: "video"}, spct={1: 5.0}, past_dl=True)
    for q, tt_ in enumerate((3.0, 3.3, 3.9)):
        scene_motif(sj, stj, {}, tt_, 1.16, 2 + q)
    _j1 = (stj["mcur"], stj["mprev"], sj["motivo"])
    sj.update(label="Uniendo pistas")
    scene_motif(sj, stj, {}, 4.0, 1.16, 9)
    scene_motif(sj, stj, {}, 4.0 + MOTIF_HOLD_MAX + 1.0, 1.16, 10)
    _j2 = (stj["mcur"], stj["mprev"], sj["motivo"])
    sj.update(label="Analizando", conv=None)
    scene_motif(sj, stj, {}, 20.0, 1.16, 11)
    scene_motif(sj, stj, {}, 20.0 + MOTIF_HOLD_MAX + 1.0, 1.16, 12)
    _j3 = (stj["mcur"], sj["motivo"])
    check("escena 1.4.5: una sola escena: el sitio sale y entra Descarga, de ahí a Unión y, sin otro motivo, queda el Pulso (el sitio ya no vuelve)",
          (_j0, _j1, _j2, _j3), ((None, "Sitio"), ("rail", None, "Carril"), ("rail", None, "Carril"), ("idle", "Pulso")))
    _Sl, _Tl = {"geo": (60, 24, 6, 17)}, {"ms": 0.0, "mt": None}
    check("escena 1.4.1: el loop de cada dibujo sale del registro (sin loop = 0)",
          {k: round(motif_loop_left(_Sl, _Tl, k, 0.3), 6) for k in ("ask", "dlpy", "send", "merge", "first", "updated", "clean", "empty", "save", "download", "idle", None)},
          {"ask": 0.0, "dlpy": 0.0, "send": round((-0.3) % SEND_CYCLE, 6), "merge": round((-0.3) % (4.0 / MERGE_SPEED), 6),
           "first": round((-0.3) % WELCOME_CYCLE, 6), "updated": round((-0.3) % WELCOME_CYCLE, 6),
           "clean": round((-0.3) % (1.0 / CLEAN_SPEED), 6), "empty": round((-0.3) % (1.0 / CLEAN_SPEED), 6),
           "save": round(max(0.0, SAVE_STREAM_SECS + 0.35 - 0.3), 6), "download": round((-0.3) % DOWN_CYCLE, 6),
           "idle": round((-0.3) % PULSE_CYCLE, 6), None: 0.0})
    _dd = _MotifCtx(60, 6, ra, rb, 5.0, 3, {}, set())
    _sd = {"clean": 3, "send_to": None, "welcome": {"kind": "updated", "old": "1.2.8", "new": "1.2.9"}}
    check("escena 1.4.1: el registro pinta igual que las funciones *_cells (guardado, limpieza, papelera, envío, primera ejecución, actualizado)",
          (MOTIFS["save"].draw(_sd, {}, _dd, 4.0) == scene_save_cells(60, 6, ra, rb, 1.0),
           MOTIFS["clean"].draw(_sd, {}, _dd, 4.0) == scene_clean_cells(60, 6, ra, rb, 1.0, 3),
           MOTIFS["empty"].draw(_sd, {}, _dd, 4.0) == scene_empty_cells(60, 6, ra, rb, 1.0, 3),
           MOTIFS["send"].draw(_sd, {}, _dd, 4.0) == scene_send_cells(60, 6, ra, rb, 1.0, scene_chip_text(SHORTCUT_NAME)),
           MOTIFS["first"].draw(_sd, {}, _dd, 4.0) == scene_first_cells(60, 6, ra, rb, 1.0),
           MOTIFS["updated"].draw(_sd, {}, _dd, 4.0) == scene_updated_cells(60, 6, ra, rb, 1.0, "1.2.8", "1.2.9")),
          (True, True, True, True, True, True))
    _d1, _d2 = scene_defaults(), scene_defaults()
    check("escena 1.4.1: scene_defaults da estado nuevo cada vez (sin compartir sets ni dicts) y cubre todas las claves de SCENE",
          (_d1 == _d2, _d1["done"] is not _d2["done"], _d1["vinfo"] is not _d2["vinfo"], _d1["started"] is not _d2["started"], set(SCENE) <= set(_d1)),
          (True, True, True, True, True))
    _sv4 = dict(SCENE)
    try:
        SCENE.update(on=True, done=None, done_at=None, finished=None, last_finished=None, stream_total=2, stream_seen=1, ta=3.0)
        scene_stream_done("video")                                  # 1 de 2: queda pendiente
        _r1 = (set(SCENE.get("done") or ()), SCENE["last_finished"])
        SCENE.update(stream_seen=2)
        scene_stream_done("audio")                                  # el último: done de inmediato
        _r2 = (set(SCENE["done"]), SCENE["last_finished"], dict(SCENE["done_at"]), dict(SCENE["finished"]))
        _bag = _scene_bag("type_seen")
        _r3 = (_scene_bag("type_seen") is _bag, isinstance(_scene_bag("zzz_bolsa", set), set))
    finally:
        SCENE.clear()
        SCENE.update(_sv4)
    check("escena 1.4.1: las bolsas de los streams (pendiente, done inmediato, done_at, finished) y _scene_bag reutiliza la existente",
          (_r1, _r2, _r3), (((set(), "video")), ({"audio"}, None, {"audio": 3.0}, {"video": 1, "audio": 1}), (True, True)))
    _sv5, _o5, _os5 = dict(SCENE), OUTRO, SCENE_OUTRO_SECS
    try:
        globals()["SCENE_OUTRO_SECS"] = 0.0
        SCENE["t_out"] = None
        globals()["OUTRO"] = False
        _q0 = (scene_outro(), SCENE["t_out"])
        globals()["OUTRO"] = True
        _q1 = (scene_outro(), SCENE["t_out"] is not None)
    finally:
        globals()["OUTRO"], globals()["SCENE_OUTRO_SECS"] = _o5, _os5
        SCENE.clear()
        SCENE.update(_sv5)
    check("escena 1.4.1: scene_outro cierra la escena solo con DLPY_OUTRO activo", (_q0, _q1), ((False, None), (True, True)))
    sm = {"geo": (60, 24, 6, 17), "a": ra, "b": rb, "brand": True, "conv": None}
    stm = {}
    for q, tt_ in enumerate((2.0, 2.1, 2.2)):                    # entra DLPY y a mitad vuelve el sitio: marcha atrás sin saltos (1.5.5: tiempos al doble de velocidad)
        scene_motif(sm, stm, {(30, 11): ("x", ra, None)}, tt_, 1.16, q)
    sm["brand"] = False
    scene_motif(sm, stm, {(30, 11): ("x", ra, None)}, 2.25, 1.16, 9)
    check("escena: si D L P Y se apaga a mitad de la transición, vuelve atrás desde donde iba",
          (stm["mcur"], stm["mprev"], round(1.0 - (2.25 - 2.0 - SCENE_LAG_MOTIF) / SCENE_SWAP, 3) == round((2.25 - stm["mt"]) / SCENE_SWAP, 3)), (None, "dlpy", True))
    # 1.0.6: flujo visual: suavizado por tiempo, iris desde el centro, cascada título → centro → texto y cambios sin saltos
    check("escena 1.0.6: el suavizado depende del tiempo, no de los cuadros (1 cuadro de 1/12 s = 2 de 1/24 s)",
          (round(scene_ease(0.0, 1.0, SCENE_BAR_RATE, 1 / 12.0), 6) == round(scene_ease(scene_ease(0.0, 1.0, SCENE_BAR_RATE, 1 / 24.0), 1.0, SCENE_BAR_RATE, 1 / 24.0), 6),
           scene_ease(0.3, 0.3, 5.0, 0.1), scene_ease(0.0, 1.0, 5.0, 0.0), scene_ease(0.0, 1.0, 5.0, 99.0) < 1.0), (True, 0.3, 0.0, True))
    wo = {(x, 5): ("a", ra, None) for x in range(10, 31)}
    wn = {(x, 5): ("b", rb, None) for x in range(10, 31)}
    wm = scene_swap_cells(wo, wn, 0.4, 3, ra, rb)
    changed = lambda m: sorted(x for (x, _y), v in m.items() if v[0] != "a")
    ch_x = changed(wm)
    check("transición del centro 1.0.6: abre desde el medio (lo que ya cambió está más cerca del centro que lo que no)",
          (len(ch_x) > 0, sum(abs(x - 20) for x in ch_x) / len(ch_x) < sum(abs(x - 20) for x in range(10, 31)) / 21.0,
           scene_swap_cells(wo, wn, 0.0, 3, ra, rb) == wo, scene_swap_cells(wo, wn, 1.0, 3, ra, rb) == wn, scene_swap_cells({}, {}, 0.5, 3, ra, rb)),
          (True, True, True, True, {}))
    sc = {"geo": (60, 24, 6, 17), "a": ra, "b": rb, "name": "YouTube", "mode": "video", "title_raw": "Pan casero", "brand": False,
          "busy": False, "label": "Analizando enlace", "pct": 10, "shown": 0.2, "k_out": None, "conv": None}
    sk = {"rows": {}, "lab": None, "prev": "", "full": "", "t": 0.0, "tcur": None, "tprev": None, "tt": None}
    t0_ = SITE_HOLD_AT * SITE_SECS
    scene_cells(sc, sk, t0_, t0_ + 0.01, 1)
    scene_cells(sc, sk, t0_, t0_ + 3.0, 60)                                # todo en reposo
    sc["brand"], sc["label"], sc["pct"] = True, "Comprobando DLpy", None  # cambian a la vez título, centro y texto
    scene_cells(sc, sk, t0_, t0_ + 3.1, 62)
    check("escena 1.0.6: en cascada, el centro y el texto esperan al título",
          (sk["tt"], round(sk["mt"] - 3.1 - t0_, 3), round(sk["t"] - 3.1 - t0_, 3)), (t0_ + 3.1, SCENE_LAG_MOTIF, SCENE_LAG_LABEL))
    sd = {"geo": (60, 24, 6, 17), "a": ra, "b": rb, "name": "YouTube", "mode": "video", "title_raw": "", "brand": False,
          "busy": False, "label": "Preparando", "pct": None, "shown": 0.2, "k_out": None, "conv": None}
    skd = {"rows": {}, "lab": None, "prev": "", "full": "", "t": 0.0, "tcur": None, "tprev": None, "tt": None}
    scene_cells(sd, skd, t0_, t0_ + 0.01, 1)
    scene_cells(sd, skd, t0_, t0_ + 3.0, 60)
    sd["brand"], sd["busy"], sd["label"], sd["dl_done"] = True, True, "Instalando yt-dlp", None     # como con yt-dlp desinstalado (scene_note)
    scene_cells(sd, skd, t0_, t0_ + 3.1, 61)
    _en = skd["mt"]
    _row = lambda c: "".join(c[(x, 11)][0] for x in range(1, 61) if (x, 11) in c)
    _full = "pip install -U yt-dlp --no-deps"
    _ca = scene_cells(sd, skd, t0_, _en + 0.1, 62)                                              # el dibujo apenas empieza a aparecer
    _cb = scene_cells(sd, skd, t0_, _en + SCENE_SWAP + DLPY_TYPE_AT + 0.25, 63)                 # ya se ve y se está tecleando
    _d1 = sd.get("dl_done")
    _cc = scene_cells(sd, skd, t0_, _en + SCENE_SWAP + DLPY_STEP_SECS + 0.05, 64)               # tecleado y ejecutado
    check("escena 1.3.3: con yt-dlp desinstalado el comando se teclea a la vista (no ya tecleado al aparecer) y solo entonces el flujo puede seguir",
          (_full in _row(_ca), 0 < len(_row(_cb).replace(" ", "")) and _full not in _row(_cb), _full in _row(_cc), _d1, sd.get("dl_done")),
          (False, True, True, None, "Instalando yt-dlp"))
    sd["label"], sd["busy"] = "yt-dlp 2026.1.1 · instalado", False
    scene_cells(sd, skd, t0_, _en + SCENE_SWAP + DLPY_STEP_SECS + 0.2, 65)
    _ce = scene_cells(sd, skd, t0_, _en + SCENE_SWAP + DLPY_STEP_SECS + 0.3, 66)
    check("escena 1.3.3: el resultado deja el mismo comando con ✓ (sin volver a teclearlo) y se da por mostrado al instante",
          (_full + "✓" in _row(_ce), sd.get("dl_done")), (True, "yt-dlp 2026.1.1 · instalado"))
    sd["brand"] = False
    sd["label"] = "Descargando video"
    scene_cells(sd, skd, t0_, _en + 9.0, 67)
    _cf = scene_cells(sd, skd, t0_, _en + 9.0 + SCENE_LAG_MOTIF + SCENE_SWAP / 2, 68)           # el dibujo D L P Y se deshace
    check("escena 1.3.3: al deshacerse D L P Y conserva su comando (no pasa a «python dlpy.py»)",
          ("python dlpy.py" in _row(_cf).replace("  ", " "), "dlpy.py" in "".join(v[0] for v in _cf.values())), (False, False))
    c0 = scene_cells(sc, sk, t0_, t0_ + 3.1 + SCENE_LAG_LABEL / 2, 63)
    check("escena 1.0.6: durante la espera el texto sigue siendo el viejo (nada parpadea)",
          "".join(c0[(x, 17)][0] for x in range(1, 61) if (x, 17) in c0).replace(" ", "").startswith("Analizandoenlace"), True)
    scene_cells(sc, sk, t0_, t0_ + 3.1 + SCENE_LAG_LABEL + 0.2, 70)          # el texto va a mitad de su transformación
    seen_mid = dict(sk["lshown"])
    sc["label"] = "Analizando enlace"                                       # y vuelve a cambiar sin que termine
    scene_cells(sc, sk, t0_, t0_ + 3.1 + SCENE_LAG_LABEL + 0.25, 71)
    check("escena 1.0.6: un cambio a mitad de transformación parte de lo que ya se ve, no del texto completo anterior",
          (sk["lpcols"] == seen_mid, bool(seen_mid)), (True, True))
    scene_cells(sc, sk, t0_, t0_ + 9.0, 300)
    check("escena 1.0.6: al terminar queda el último texto completo", "".join(ch for ch in sk["lshown"].values()), "".join(ch for ch in "Analizando enlace" if ch != " "))
    sb = dict(sc, busy=False, brand=False, shown=0.5)
    skb = {"rows": {}, "lab": None, "prev": "", "full": "", "t": 0.0, "tcur": None, "tprev": None, "tt": None}
    ruler = lambda cs: [cs[(x, 6)][1] for x in range(17, 46)]
    r_bar = ruler(scene_cells(sb, skb, t0_, t0_ + 5.0, 100))
    sb["busy"] = True
    r_mid = ruler(scene_cells(sb, skb, t0_, t0_ + 5.05, 101))
    r_swp = ruler(scene_cells(sb, skb, t0_, t0_ + 6.0, 130))
    sb["busy"] = False
    r_back = ruler(scene_cells(sb, skb, t0_, t0_ + 6.05, 131))
    for q in range(40):                                                     # el fundido de vuelta termina en cuadros de 0.05 s
        r_end = ruler(scene_cells(sb, skb, t0_, t0_ + 6.10 + 0.05 * q, 132 + q))
    check("escena 1.0.6: la regla pasa de la barra al barrido y vuelve con fundido (ni corte ni se queda a medias)",
          (r_mid != r_bar, r_mid != r_swp, skb["bw"] == 0.0, r_back != r_end,
           r_end == ruler(scene_cells(dict(sb, busy=False), {"rows": {}, "lab": None, "prev": "", "full": "", "t": 0.0, "tcur": None, "tprev": None, "tt": None}, t0_, t0_ + 8.0, 190))),
          (True, True, True, True, True))
    base = {(x, 8): (ch, (200, 200, 200), None) for x, ch in enumerate("ABCDEFGH日", 20)}
    base[(29, 8)] = ("日", (1, 1, 1), None)
    base[(30, 8)] = ("", (1, 1, 1), None)
    check("escena: cierre en k=0 no toca nada y en k=1 no deja nada",
          (scene_dissolve(base, 0.0, 30, 60, (255, 0, 0), (0, 0, 255)) == base, scene_dissolve(base, 1.0, 30, 60, (255, 0, 0), (0, 0, 255))),
          (True, {}))
    ends = []
    for k in (0.2, 0.4, 0.6, 0.8):
        d = scene_dissolve(base, k, 30, 60, (255, 0, 0), (0, 0, 255))
        ends.append(len(d))
        check("escena: cierre k=%.1f el ancho nunca cambia" % k, ((29, 8) in d) == ((30, 8) in d), True)
    check("escena: el cierre va quitando celdas", ends == sorted(ends, reverse=True) and ends[0] > ends[-1], True)
    # 0.9.5: cabecera de la lista «Ver todos» en el estilo de la escena
    Sl = {"a": (255, 140, 0), "b": (220, 40, 180)}
    h1 = scene_list_top_cells(Sl, 60, "Pan casero", "Ver todos · 7 formatos", 1.0, 5)
    check("lista escena: regla de 29 celdas con degradado, título blanco y estado gris",
          ([x for (x, y) in h1 if y == 1] == list(range(17, 46)), h1[(17, 1)][1], h1[(45, 1)][1],
           "".join(h1[(x, 2)][0] for x in range(1, 61) if (x, 2) in h1), "".join(h1[(x, 3)][0] for x in range(1, 61) if (x, 3) in h1),
           h1[(31, 2)][1] == SCENE_WHITE, [h1[k][1] for k in h1 if k[1] == 3][0] == SCENE_GRAY),
          (True, (255, 140, 0), (220, 40, 180), "Pancasero", "Vertodos·7formatos", True, True))
    h0 = scene_list_top_cells(Sl, 60, "Pan casero", "Ver todos", 0.0, 0)
    check("lista escena: al empezar solo hay un punto de la regla (el centro), sin texto", list(h0), [(31, 1)])
    hm = scene_list_top_cells(Sl, 60, "Pan casero", "Ver todos", 0.3, 4)
    check("lista escena: a mitad la regla es más corta y es repetible",
          (len([k for k in hm if k[1] == 1]) < 29, hm == scene_list_top_cells(Sl, 60, "Pan casero", "Ver todos", 0.3, 4)), (True, True))
    check("lista escena: el título largo se recorta y cabe", max(x for (x, y) in scene_list_top_cells(Sl, 40, "x" * 90, "e", 1.0, 0) if y == 2) < 40, True)
    check("scb: avisos cortos que caben en 50 columnas", [dwidth(x) <= 44 for x in SCB_NOTES], [True, True, True])
    check("scb: sin enlace no hay escena", [scb_scene_start(None), scb_scene_start("")], [False, False])
    # 1.0.8: los errores (stderr de yt-dlp, etc.) van a shortcutmode.log y se indican en la escena D L P Y
    check("error en escena: texto corto y limpio", [scene_error_text("Error al descargar: ERROR: unable to download video data: HTTP Error 403: Forbidden"),
                                                     scene_error_text("\x1b[0;31mERROR:\x1b[0m   video no disponible"), scene_error_text("x" * 100, 20)],
          ["unable to download video data: HTTP Error 403: Forbidden", "video no disponible", "x" * 19 + "\u2026"])
    import io
    import tempfile
    _tmp_log = os.path.join(tempfile.mkdtemp(prefix="dlpy_t27_"), "shortcutmode.log")
    _old_log = globals()["SHORTCUTMODE_LOG"]
    globals()["SHORTCUTMODE_LOG"] = _tmp_log
    _real_err = io.StringIO()
    _em = _SceneErrMute(_real_err)
    try:
        _em.write("\x1b[0;31mERROR:\x1b[0m unable to download video data: HTTP Error 403: Forbidden\nsegunda")
        _em.write(" linea\n\n")
        _em.write("sin salto")
        _em.drain()
        _logged = open(_tmp_log, encoding="utf-8").read().splitlines()
        check("stderr en escena: nada llega a la pantalla y todo queda en shortcutmode.log",
              (_real_err.getvalue(), [ln.split(" - ", 1)[1] for ln in _logged]),
              ("", ["stderr: ERROR: unable to download video data: HTTP Error 403: Forbidden", "stderr: segunda linea", "stderr: sin salto"]))
        _em.open = True
        _em.write("ya abierta\n")
        check("stderr: con la escena cerrada pasa tal cual", _real_err.getvalue(), "ya abierta\n")
    finally:
        globals()["SHORTCUTMODE_LOG"] = _old_log
    _so2 = dict(SCENE)
    try:
        SCENE.update(on=True, brand=False, err_brand=False, last_error=None, label="Descargando audio", pct=51, frac=0.5)
        scene_set_error("Error al descargar: ERROR: HTTP Error 403: Forbidden")
        check("error en escena: pasa a D L P Y con el error en el texto",
              (SCENE["brand"], SCENE["label"], SCENE["pct"], SCENE["last_error"]), (True, "Error: HTTP Error 403: Forbidden", None, "HTTP Error 403: Forbidden"))
        scene_status("Descargando audio", pct=3)
        check("error recuperable: si el flujo sigue, la escena vuelve a lo suyo", (SCENE["brand"], SCENE["last_error"], SCENE["label"]), (False, None, "Descargando audio"))
        scene_set_error("fatal")
        scene_brand(True)
        scene_status("Enviando", frac=1.0)
        check("error: «Enviando» no pierde el D L P Y que ya pidió", SCENE["brand"], True)
        SCENE.update(on=True, last_error=None)
        check("sin error no hay cierre de error", scene_error_end(), False)
    finally:
        SCENE.clear()
        SCENE.update(_so2)
    # 1.0.7: la resolución corta (y el formato de audio, LIVE, ×N) dentro del dibujo, con el mismo flujo de la escena
    check("etiqueta: resolución corta", [res_badge(h, 16 / 9.0) for h in (240, 480, 720, 1080, 1440, 2160, 4320)],
          ["240", "480", "720", "1080p", "1440p", "2160p", "4320p"])
    check("etiqueta 1.4.2: la resolución es la real (360 no sale como 480, 540 tampoco) y siempre de largo impar",
          [res_badge(h, 16 / 9.0) for h in (144, 360, 540, 1078, 1200)], ["144", "360", "540", "1080p", "1200p"])
    check("etiqueta: vertical y cine miden por el lado que manda", [res_badge(1920, 9 / 16.0), res_badge(1280, 9 / 16.0), res_badge(804, 1920 / 804.0)],
          ["1080p", "720", "1080p"])
    check("etiqueta: sin dato no hay resolución", [res_badge(None), res_badge(0), res_badge("x")], [None, None, None])
    check("etiqueta: formato de audio", [audio_label({"acodec": "mp4a.40.2", "vcodec": "none", "ext": "m4a"}),
                                         audio_label({"acodec": "opus", "vcodec": "none", "ext": "webm"}),
                                         audio_label({"acodec": "mp4a.40.2", "vcodec": "avc1", "ext": "mp4"}), audio_label(None, {})],
          ["M4A", "OPUS", None, None])
    # 1.1.0: la etiqueta del video fluye por resolución / códec / fps / bitrate, todo de longitud par
    _vi = video_facts({"vcodec": "avc1.640028", "fps": 29.97, "vbr": 4500.0}, {"vcodec": "vp9", "tbr": 900})
    check("fluye: datos del video", _vi, {"codec": "avc1.640028", "fps": 29.97, "kbps": 4500.0})
    check("fluye: abreviaturas", [codec_label(c) for c in ("avc1.640028", "hvc1.1.6", "vp9", "vp09.00.40.08", "av01.0.08M.08", "vc1", "none")],
          ["H.264", "H.265", "VP9", "VP9", "AV1", "VC1", None])
    check("fluye: fps y bitrate (5 caracteres)", (fps_label(29.97), fps_label(120), fps_label(8), kbps_label(66), kbps_label(800), kbps_label(4500), kbps_label(12000)),
          ("30fps", "120Hz", "08fps", "066kb", "800kb", "4.5Mb", "012Mb"))
    _all = [vinfo_labels(h, a_, _vi) for h in (480, 1080) for a_ in (9 / 16.0, 1.0, 16 / 9.0)]
    check("fluye: todas de longitud impar (centradas en el marco impar) y caben en él", all(len(t) % 2 == 1 and len(t) <= site_frame_width(asp_, 99) - 2
                                                                  for ls, asp_ in zip(_all, (9 / 16.0, 1.0, 16 / 9.0) * 2) for t in ls), True)
    check("fluye: rota con el tiempo y sin datos queda el ►",
          ([badge_texts("video", 1080, 16 / 9.0, vinfo=_vi, ta=VINFO_SECS * i)["v"] for i in range(5)], badge_texts("video", vinfo={})["v"]),
          (["1080p", "H.264", "30fps", "4.5Mb", "1080p"], "►"))
    # 1.1.0: el audio fluye (formato → bitrate → muestreo) con etiquetas impares; la rotación arranca en el primer dato
    _ai = audio_facts({"abr": 128.0, "asr": 44100})
    check("audio fluye: datos y etiquetas", (_ai, [odd_label(x) for x in ("M4A", "OPUS", "FLAC", "AIFF", "OGG")], abr_label(96), abr_label(320), abr_label(1411),
                                              asr_label(44100), asr_label(48000), asr_label(8000)),
          ({"kbps": 128.0, "hz": 44100.0}, ["M4A", "OPU", "FLA", "AIF", "OGG"], "096kb", "320kb", "1.4Mb", "44.1k", "48kHz", "08kHz"))
    check("audio fluye: rota por formato, bitrate y muestreo, todas impares",
          ([badge_texts("audio", alabel="M4A", ainfo=_ai, ta={"a": VINFO_SECS * i})["a"] for i in range(4)],
           all(len(t) % 2 == 1 for t in audio_labels("OPUS", _ai))), (["M4A", "128kb", "44.1k", "M4A"], True))
    check("audio: códec desde acodec y etiqueta también en video+audio",
          (acodec_label("mp4a.40.2"), acodec_label("opus"), acodec_label("none"), audio_facts({"acodec": "opus", "abr": 96})["codec"],
           badge_texts("both", 1080, 16 / 9.0, ainfo={"codec": "mp4a.40.2", "kbps": 128.0})["a"], badge_texts("video", 1080, 16 / 9.0).get("a")),
          ("AAC", "OPUS", None, "opus", "AAC", None))
    _bw = scene_site_center_cells(60, 6, (255, 140, 0), (220, 40, 180), 3.0, "both", 16 / 9.0, 1080, set(), {}, 5, badge={"v": ("1080p", 1.0), "a": ("AAC", 1.0)})
    _cx = 60 // 2 + 1
    check("video+audio: ocupa justo las columnas de la regla y las dos tarjetas van en la misma fila, bajo el marco y las barras (1.4.2)",
          (min(c for c, r in _bw), max(c for c, r in _bw), "".join(_bw.get((c, 15), (" ",))[0] for c in range(_cx + 8, _cx + 12)).strip(),
           "".join(_bw.get((c, 15), (" ",))[0] for c in range(_cx - 14, _cx + 4)).strip(), max(r for c, r in _bw)),
          (_cx - 14, _cx + 13, "AAC", "1080p", 15))
    # 1.1.1: la escena pide Enter para convertir lo que tarda
    check("pedir Enter: estimación en texto", [ask_est_text(x) for x in (None, 0, 45, 89, 90, 200)], ["", "", "~45 s", "~89 s", "~2 min", "~3 min"])
    check("pedir Enter: líneas según el ancho",
          (scene_ask_lines(42, 200, 17.2), scene_ask_lines(30, 200, 3.0), scene_ask_lines(20, None, 9.0)),
          (("Enter convertir · r remux · n original", "~3 min · sin respuesta se convierte · 18 s"),
           ("Enter sí · r remux · n no", "~3 min · 3 s"),
           ("Enter · r · n", "9 s")))
    check("pedir Enter 1.1.4: con sitio de sobra, la primera fila avisa de tocar la pantalla y la segunda lleva la estimación",
          (scene_ask_lines(70, 200, 17.2), scene_ask_lines(5, 200, 1.0)),
          (("Toca la pantalla · Enter convertir · r remux · n original", "~3 min · sin respuesta se convierte · 18 s"), ("Enter", "1 s")))
    check("pedir Enter 1.1.4: las teclas resaltadas son Enter, r y n (y nada más)",
          ({scene_ask_lines(42, 0, 5)[0][i] for i in ask_key_mask(scene_ask_lines(42, 0, 5)[0])} == {"E", "n", "t", "e", "r"},
           sorted(ask_key_mask("Enter · r · n")), ask_key_mask("Toca la pantalla")),
          (True, [0, 1, 2, 3, 4, 8, 12], set()))
    _ac = scene_ask_cells({(5, 12): ("x", (1, 1, 1), None), (6, 6): ("y", (1, 1, 1), None)}, {"est": 200, "secs": 20, "t0": time.time(), "ta0": 0.0}, 3.0, 6, 25, 48,
                          lambda k: (200, 100, 50))
    _r1 = "".join(_ac[(x, 17)][0] for x in range(0, 60) if (x, 17) in _ac)
    _r2 = "".join(_ac[(x, 18)][0] for x in range(0, 60) if (x, 18) in _ac)
    check("pedir Enter: ocupa las dos filas del estado, centrado, y respeta lo demás",
          (_r1, _r2.startswith("~3min·sinrespuestaseconvierte"), (5, 12) in _ac, (6, 6) in _ac, abs((min(x for x, y in _ac if y == 17) + max(x for x, y in _ac if y == 17)) / 2 - 25) <= 1),
          ("Enterconvertir·rremux·noriginal", True, True, True, True))
    check("pedir Enter 1.2.0: la ayuda fluye de «Toca la pantalla…» a «¿Convertir este video?» según el ancho",
          (ask_hint_texts(60), ask_hint_texts(30), ask_hint_texts(20), ask_hint_texts(9)),
          (("Toca la pantalla para abrir el teclado", "¿Convertir este video?", 0), ("Toca para abrir el teclado", "¿Convertir este video?", 0),
           ("Toca = teclado", "¿Convertir ahora?", 0), ("", "¿Convertir?", 0)))
    def _hx(tt):
        _c = scene_ask_cells({}, {"est": 200, "secs": 20, "t0": time.time(), "ta0": 0.0}, tt, 6, 25, 48, lambda k: (200, 100, 50))
        return "".join(v[0] for (x, y), v in sorted(_c.items()) if y == 16)
    check("pedir Enter 1.2.0: la línea de ayuda dice «Toca…» al principio, «¿Convertir este video?» después (sin repetir «Enter») y vuelve",
          (_hx(0.5), _hx(3.2), _hx(5.3)), ("Tocalapantallaparaabrirelteclado", "¿Convertireste video?".replace(" ", ""), "Tocalapantallaparaabrirelteclado"))
    _cs, _real = [], globals()["scene_ask_enter"]
    try:
        globals()["scene_ask_enter"] = lambda est, secs=None, **_kw: (_cs.append(est), _ans[0])[1]       # noqa: E731
        _ans = [False]
        _p1, _p2, _p3 = {"venc": True, "ask_enter": 200}, {"venc": True, "ask_enter": 200}, {"venc": True}
        _r1_ = convert_confirmed(_p1)
        _ans[0] = True
        _r2_ = convert_confirmed(_p2)
        _r3_ = convert_confirmed(_p3)
        _ans[0] = None
        _r4_ = convert_confirmed({"venc": True, "ask_enter": 200})
        check("Enter antes de convertir: sin Enter no se convierte; con Enter, sin plan marcado o sin escena sí",
              ((_r1_, _r2_, _r3_, _r4_), _cs, "ask_enter" in _p1), ((False, True, True, True), [200, 200, 200], False))
        _ans[0] = "r"                                    # 1.1.4: «r» en la escena = solo remux, sin recodificar el video
        _p5 = {"venc": True, "ask_enter": 200, "out_bits": 10}
        _r5_ = convert_confirmed(_p5)
        check("Enter antes de convertir 1.1.4: «r» hace remux (el plan deja de recodificar y queda marcado)",
              (_r5_, _p5.get("venc"), _p5.get("remux_forced"), "ask_enter" in _p5), (True, False, True, False))
    finally:
        globals()["scene_ask_enter"] = _real
    _so_a = dict(SCENE)
    try:
        SCENE.update(on=False)
        check("pedir Enter: sin escena no pregunta (se hace como siempre)", scene_ask_enter(200), None)
    finally:
        SCENE.clear()
        SCENE.update(_so_a)
    _Sx, _stx = {"mode": "video", "mode_orig": "video", "res": 1080, "aspect": 16 / 9.0, "alabel": None, "count": 0,
                 "vinfo": {"codec": "avc1", "fps": 30}}, {}
    check("fluye: arranca en la resolución aunque el reloj ya vaya adelantado",
          [scene_badge(_Sx, _stx, 100.0 + VINFO_SECS * i + (0.1 if i else 0.0))["v"][0] for i in range(3)], ["1080p", "H.264", "30fps"])
    check("etiqueta: textos por tipo", (badge_texts("video", 1080, 16 / 9.0), badge_texts("video"), badge_texts("audio", alabel="MP3"),
                                        badge_texts("live"), badge_texts("list", count=12)),
          ({"v": "1080p"}, {"v": "►"}, {"v": "►", "a": "MP3"}, {"v": "►", "l": "LIVE"}, {"v": "►", "l": "\u00d712"}))
    _vc = site_video_cells(10, 5, 18, (255, 0, 0), (0, 0, 255), 3.0, 1.0, 1080, badge=("1080", 1.0))
    check("etiqueta 1.4.2: la resolución va DEBAJO del marco (fila 10) y el ► se queda en su sitio",
          ("".join(_vc[(x, 5 + BADGE_ROW)][0] for x in range(17, 21)), _vc[(19, 7)][0], max(y for (_x, y) in _vc), min(x for (x, y) in _vc if y == 10) >= 10),
          ("1080", "►", 10, True))
    check("etiqueta 1.4.2: sin dato no hay tarjeta (solo el marco) y el ► respira igual",
          (max(y for (_x, y) in site_video_cells(10, 5, 18, (255, 0, 0), (0, 0, 255), 3.0, 1.0, 1080, badge=("►", 1.0))),
           max(y for (_x, y) in site_video_cells(10, 5, 18, (255, 0, 0), (0, 0, 255), 3.0, 1.0, 1080))), (9, 9))
    _cen = []
    for _asp in (9 / 16.0, 1.0, 4 / 3.0, 16 / 9.0, 21 / 9.0, None):
        for _room in (99, 29, 18):
            _fw = site_frame_width(_asp, _room)
            for _lab in (res_badge(1080, _asp or 16 / 9.0), PH_VIDEO["res"], PH_VIDEO["codec"], PH_VIDEO["fps"], PH_VIDEO["kbps"], "H.264", "AV1"):
                _cc = site_video_cells(10, 4, _fw, (255, 0, 0), (0, 0, 255), 3.0, 1.0, 1080, badge=(_lab, 1.0))
                _play = [x for (x, y), v in _cc.items() if v[0] == "\u25ba"]
                _txt = sorted(x for (x, y), v in _cc.items() if y == 4 + BADGE_ROW and v[0] != " ")
                _cen.append(_fw % 2 == 1 and _play == [10 + _fw // 2] and _txt[0] + _txt[-1] == 2 * (10 + _fw // 2))
    check("1.4.2: el \u25ba y la tarjeta de abajo quedan exactamente en la columna central del marco (cualquier aspecto y espacio)", all(_cen), True)
    check("etiqueta: sin dato queda el ► que respira", any(v[0] == "►" for v in site_video_cells(10, 5, 18, (255, 0, 0), (0, 0, 255), 3.0, 1.0, 1080).values()), True)
    _bc = badge_cells(30, 12, "LIVE", 0.0, 1.0, (255, 0, 0), (0, 0, 255))
    check("etiqueta: al cambiar sale del ruido y luego queda el texto", ("LIVE" in "".join(v[0] for v in _bc.values()),
          "".join(v[0] for _, v in sorted(badge_cells(30, 12, "LIVE", 1.0, 1.0, (255, 0, 0), (0, 0, 255)).items())).strip()), (False, "LIVE"))
    _St = {"mode": "video", "mode_orig": "video", "res": None, "aspect": None, "alabel": None, "count": 0}
    _sb = {}
    check("etiqueta: primero ►, sin transición", scene_badge(_St, _sb, 5.0), {"v": ("►", 1.0)})
    _St.update(res=1080, aspect=16 / 9.0)
    check("etiqueta: al conocerse la resolución empieza a resolverse", scene_badge(_St, _sb, 6.0), {"v": ("1080p", 0.0)})
    check("etiqueta: y termina asentada", scene_badge(_St, _sb, 6.0 + SCENE_BADGE_SECS + 0.1), {"v": ("1080p", 1.0)})
    check("escena: la etiqueta cambiando va a tope de cuadros", scene_fps(_St, {"bdg": {"v": ["1080", 6.0]}}, 6.2, 99.0), SITE_FPS)
    _so, _tg = dict(SCENE), SESSION.get("tag")
    try:
        SCENE.update(on=True, mode="both", mode_orig="both", alabel=None, count=0)
        SESSION["tag"] = (" YT ►♪ ", (1, 2, 3), (255, 255, 255))
        scene_shape({"is_live": True, "width": 1280, "height": 720})
        check("directo: la escena pasa al dibujo de directo y la etiqueta del banner lo refleja",
              (SCENE["mode"], SCENE["mode_orig"], SESSION["tag"][0], scene_badge_texts(SCENE).get("l"), scene_badge_texts(SCENE).get("v")),
              ("live", "live", " YT ● ", "LIVE", "720"))
        scene_shape({"acodec": "mp4a.40.2", "vcodec": "none", "ext": "m4a"})
        check("audio: el formato llega a la escena", SCENE["alabel"], "M4A")
    finally:
        SCENE.clear()
        SCENE.update(_so)
        SESSION["tag"] = _tg
    for _mode, _kw in (("video", {}), ("both", {}), ("audio", {"a": ("M4A", 1.0)}), ("live", {"l": ("LIVE", 1.0)}), ("list", {"l": ("\u00d73", 1.0)})):
        _cc = scene_site_center_cells(60, 6, (255, 140, 0), (220, 40, 180), 3.0, _mode, 16 / 9.0, 1080, set(), {}, 5,
                                      badge={"v": ("1080", 1.0), **_kw})
        check("etiqueta: el dibujo «%s» cabe en su zona" % _mode, all(10 <= r <= 10 + BADGE_ROW - 1 + (1 if _mode in ("video", "both") else 0) and 1 <= c < 60 for (c, r) in _cc) and len(_cc) > 5, True)
        if _kw:
            check("etiqueta: «%s» lleva su texto bajo el dibujo" % _mode,
                  "".join(v[0] for (c, r), v in sorted(_cc.items()) if r == 14 and v[2] is not None).strip(), list(_kw.values())[0][0])
    check("lista escena: sin escena no cede ni vuelve", (scene_list_enter("Ver todos"), scene_list_leave(None, None)), (None, False))
    edge, mid = (3, 8), (30, 8)
    dd = scene_dissolve({edge: ("x", (9, 9, 9), None), mid: ("y", (9, 9, 9), None)}, 0.3, 30, 60, (255, 0, 0), (0, 0, 255))
    check("escena: el borde se apaga antes que el centro", (edge not in dd or dd[edge][0] != "x", dd.get(mid, ("",))[0]), (True, "y"))


def _st_t27_limpieza(check):
    """[T27] ── 1.3.7: limpieza de código (quiet, mix6, escritura atómica, term_rows, tty_both, acodec_short, scene_state) ──"""
    import tempfile

    def _q(*tipos, exc=ValueError):
        with quiet("prueba", *tipos):
            raise exc("x")
        return "siguió"

    def _sale(*tipos, exc=ValueError):
        try:
            return _q(*tipos, exc=exc)
        except BaseException as e:
            return type(e).__name__
    check("quiet: sin tipos ignora cualquier Exception y el flujo sigue", _q(), "siguió")
    check("quiet: con tipos ignora solo esos (los demás se propagan)", (_sale(ValueError), _sale(OSError), _sale(OSError, ValueError)),
          ("siguió", "ValueError", "siguió"))
    check("quiet: no se traga Ctrl-C ni SystemExit", (_sale(exc=KeyboardInterrupt), _sale(exc=SystemExit)), ("KeyboardInterrupt", "SystemExit"))
    check("quiet: BaseException solo si se pide", _sale(BaseException, exc=KeyboardInterrupt), "siguió")
    with quiet("prueba"):
        pass
    check("colores: BLACK y WHITE", (BLACK, WHITE), ((0, 0, 0), (255, 255, 255)))
    check("mix6: acota a 0–1", (mix6(BLACK, WHITE, -3), mix6(BLACK, WHITE, 9)), (BLACK, WHITE))
    check("mix6: 6 pasos (0.4 cae en 2/6)", (mix6(BLACK, WHITE, 0.4), mix6(BLACK, WHITE, 0.5)), (mix(BLACK, WHITE, 2 / 6.0), mix(BLACK, WHITE, 0.5)))
    with tempfile.TemporaryDirectory() as _td:
        _f, _g = os.path.join(_td, "a", "b", "c.json"), os.path.join(_td, "t.txt")
        try:
            save_json(_f, {"b": 1})
            _sin = "creó"
        except OSError:
            _sin = "falló"
        save_json(_f, {"b": "ñ", "a": 2}, mkdir=True, sort_keys=True)
        write_text(_g, "uno")
        write_text(_g, "dos")
        check("escritura atómica: sin mkdir no crea la carpeta; con mkdir sí, JSON ordenado y sin ñ escapada",
              (_sin, read_text(_f)), ("falló", '{\n "a": 2,\n "b": "ñ"\n}'))
        check("escritura atómica: reemplaza y no deja .tmp", (read_text(_g), os.path.exists(_g + ".tmp"), os.path.exists(_f + ".tmp")),
              ("dos", False, False))
    check("term_rows: un entero positivo", (type(term_rows()), term_rows() > 0), (int, True))
    _si, _so = sys.stdin, sys.stdout

    class _Tty:
        def __init__(self, v):
            self.v = v

        def isatty(self):
            return self.v
        write = flush = lambda self, *a: None
    try:
        got = []
        for _a, _b in ((True, True), (True, False), (False, True), (False, False)):
            sys.stdin, sys.stdout = _Tty(_a), _Tty(_b)
            got.append(tty_both())
    finally:
        sys.stdin, sys.stdout = _si, _so
    check("tty_both: solo con terminal en la entrada y en la salida", got, [True, False, False, False])
    check("acodec_short: quita el perfil, «?» si falta", [acodec_short({"acodec": "mp4a.40.2"}), acodec_short({"acodec": "opus"}),
                                                          acodec_short({"acodec": None}), acodec_short({})], ["mp4a", "opus", "?", "?"])
    _s1, _s2 = scene_state(), scene_state()
    _s1["rows"]["x"] = 1
    check("scene_state: vacío y nuevo en cada llamada", (_s2["rows"], _s2["lab"], _s2["prev"], _s2["t"], sorted(_s2)),
          ({}, None, "", 0.0, sorted(["rows", "lab", "prev", "full", "t", "tcur", "tprev", "tt"])))


def _st_t28_morph(check):
    """[T28] ── 1.4.2: motor de morph del centro (curva, papeles, plan, cuadros), texto deslizante y tarjeta del video bajo el marco ──"""
    ra, rb = (255, 140, 0), (220, 40, 180)
    _f = flow_curve(0.3, 0.0, 0.2, 1.0)
    _ys = [_f(i / 20.0) for i in range(21)]
    check("morph: la curva va de 0 a 1, sube siempre y frena al final", (_ys[0], _ys[-1], all(y2 >= y1 for y1, y2 in zip(_ys, _ys[1:])),
                                                                         _ys[10] > 0.5, _ys[19] - _ys[18] < _ys[3] - _ys[2]), (0.0, 1.0, True, True, True))
    check("morph: papeles de las celdas (un █ pegado a otra celda es relleno, suelto es barra)",
          ([flow_role(c) for c in "╭─│░▓▁●·►✓a日"], flow_role("█"), flow_role("█", True)),
          (["line", "line", "line", "shade", "shade", "bar", "dot", "dot", "mark", "mark", "text", "text"], "bar", "shade"))
    _ok = True
    for n, m in ((3, 7), (7, 3), (5, 5), (1, 4), (4, 1)):
        A, B = list(range(n)), list(range(m))
        pr = _flow_pair(A, B)
        _ok = _ok and {x for x, _y in pr} == set(A) and {y for _x, y in pr} == set(B) and all(
            pr[i][0] <= pr[i + 1][0] and pr[i][1] <= pr[i + 1][1] for i in range(len(pr) - 1))
    check("morph: el reparto por cuantiles cubre todo el origen y todo el destino y no se cruza", _ok, True)
    vid = scene_site_center_cells(46, 6, ra, rb, 3.0, "video", 16 / 9.0, 1080, set(), {}, 5, badge={"v": ("1080", 1.0)})
    cnv = scene_conv_cells(46, 6, ra, rb, 0.5, "webm", "mp4", 40)
    plan = flow_plan(vid, cnv)
    check("morph: el plan cubre cada celda del dibujo viejo (origen) y del nuevo (destino), sin sobrar ninguna y repetible",
          (plan["src"] == {k for k, c in vid.items() if c[0] and dwidth(c[0]) == 1}, plan["dst"] == {k for k, c in cnv.items() if c[0] and dwidth(c[0]) == 1},
           plan["acts"] == flow_plan(vid, cnv)["acts"], abs(max(t[4] + t[5] * (FLOW_LAND if t[7] else 0.65) for t in plan["acts"]) - 1.0) < 1e-9, min(t[4] for t in plan["acts"]) >= 0.0),
          (True, True, True, True, True))
    mids = [flow_frame(plan, vid, cnv, q / 20.0, 7 + q, ra, rb) for q in range(1, 20)]
    ymin, ymax = plan["rows"]
    check("morph: en 0 es exactamente el dibujo viejo y en 1 el nuevo; a mitad es repetible",
          (flow_frame(plan, vid, cnv, 0.0, 3, ra, rb) == vid, flow_frame(plan, vid, cnv, 1.0, 3, ra, rb) == cnv,
           mids[9] == flow_frame(plan, vid, cnv, 0.5, 16, ra, rb), mids[9] != vid and mids[9] != cnv), (True, True, True, True))
    check("morph: cada cuadro intermedio queda dentro de las filas de los dos dibujos y con celdas de una columna",
          (all(ymin <= y <= ymax for m in mids for (_x, y) in m), all(len(c) == 3 and dwidth(c[0]) == 1 for m in mids for c in m.values()),
           all(len(m) > 10 for m in mids)), (True, True, True))
    check("morph: lo que conserva su papel viaja con su glifo (hay líneas del marco en vuelo fuera de su sitio y del destino)",
          any(c[0] in "─│" and k not in vid and k not in cnv for m in mids for k, c in m.items()), True)
    # una celda que se divide en dos y dos que se juntan en una
    o2, n2 = {(5, 5): ("a", ra, None)}, {(5, 5): ("a", ra, None), (9, 5): ("b", rb, None)}
    p2 = flow_plan(o2, n2)
    check("morph: una celda que se divide en dos (y al revés) no deja a ninguna sin pareja",
          (p2["src"], p2["dst"], flow_plan(n2, o2)["src"], flow_plan(n2, o2)["dst"], flow_frame(p2, o2, n2, 1.0, 0, ra, rb) == n2),
          ({(5, 5)}, {(5, 5), (9, 5)}, {(5, 5), (9, 5)}, {(5, 5)}, True))
    # el dibujo vivo cambia después de medir: lo nuevo entra con ruido y al final es exacto
    live = dict(n2)
    live[(7, 6)] = ("c", rb, None)
    check("morph: una celda que aparece tras medir el plan entra más tarde y el cuadro 1 es el vivo",
          ((7, 6) in flow_frame(p2, o2, live, 0.3, 0, ra, rb), (7, 6) in flow_frame(p2, o2, live, 0.95, 0, ra, rb), flow_frame(p2, o2, live, 1.0, 0, ra, rb) == live),
          (False, True, True))
    # estado: el plan se mide una vez por transición y la reversa recorre el mismo camino
    stf = {}
    f1 = scene_flow_step(stf, "flow", vid, cnv, 0.4, 5, ra, rb)
    pl = stf["flow"]["plan"]
    f2 = scene_flow_step(stf, "flow", vid, cnv, 0.6, 6, ra, rb)
    stf["flow"]["rev"] = True
    f3 = scene_flow_step(stf, "flow", cnv, vid, 0.6, 5, ra, rb)                  # revertida: el «nuevo» es el viejo y en 0.6 se vuelve a ver el cuadro de 0.4
    check("morph: el plan se mide una vez, no cambia entre cuadros y la reversa pasa por el mismo cuadro",
          (stf["flow"]["plan"] is pl, f1 != f2, f3 == f1, scene_flow_step({}, "flow", vid, cnv, 0.0, 1, ra, rb) == vid, scene_flow_step({}, "flow", vid, cnv, 1.0, 1, ra, rb) == cnv),
          (True, True, True, True, True))
    _fo = globals()["FLOW_ON"]
    try:
        globals()["FLOW_ON"] = False
        off = scene_swap_cells(vid, cnv, 0.4, 5, ra, rb)
        check("morph: con DLPY_SCENE_FLOW=0 el cambio vuelve a ser el ruido de antes", (off == scene_noise_cells(vid, cnv, 0.4, 5, ra, rb),
              scene_flow_step({}, "flow", vid, cnv, 0.4, 5, ra, rb) == off), (True, True))
    finally:
        globals()["FLOW_ON"] = _fo
    check("morph: DLPY_SCENE_FLOW está en la configuración, encendida por omisión",
          [(n, v) for n, v, _t in CONFIG_OPTIONS if n == "DLPY_SCENE_FLOW"], [("DLPY_SCENE_FLOW", "1")])
    # texto: lo que se comparte se desliza, lo demás sale del ruido
    c0, c1 = scene_cols("Descargando video", 30), scene_cols("Descargando audio 2", 30)
    sl = morph_slides(c0, c1)
    check("texto: los tramos compartidos se emparejan (en orden, sin cruzarse) y una letra suelta lejana no",
          (len(sl) >= 11, all(a_[0] < b_[0] and a_[1] < b_[1] for a_, b_ in zip(sl, sl[1:])), sl == morph_slides(c0, c1),
           morph_slides(scene_cols("abc", 10), scene_cols("xyzc", 30)) == []), (True, True, True, True))
    t0_, t1_ = scene_morph(c0, c1, 0.0, 3), scene_morph(c0, c1, 1.0, 3)
    tm = scene_morph(c0, c1, 0.5, 3)
    check("texto: en 0 el viejo, en 1 el nuevo, a mitad las letras compartidas no hacen ruido y el resto sí",
          ("".join(v[0] for _x, v in sorted(t0_.items())), "".join(v[0] for _x, v in sorted(t1_.items())), tm == scene_morph(c0, c1, 0.5, 3),
           any(v[1] == 1 for v in tm.values()), sum(1 for v in tm.values() if v[1] != 1) >= 11),
          ("Descargandovideo", "Descargandoaudio2", True, True, True))
    sl0 = morph_slides(scene_cols("Hola mundo", 20), scene_cols("Hola mundo!!", 20))
    shift = {x0: x1 for x0, x1, _c in sl0}
    q1 = scene_morph(scene_cols("Hola mundo", 20), scene_cols("Hola mundo!!", 20), 0.3, 3)
    check("texto: la letra que cambia de columna pasa por columnas intermedias (se desliza, no salta)",
          (len(shift) == 9, all(x1 - x0 in (-1, 0, 1) for x0, x1 in shift.items()), all(v[1] != 1 for v in q1.values() if v[0] in "Hola")), (True, True, True))
    # tarjeta del video bajo el marco
    chips = site_video_cells(10, 4, 18, ra, rb, 3.0, 1.0, 1080, badge=("FHD", 0.6))
    check("tarjeta 1.4.2: la del video sale del marco (ni dentro ni sobre el ►) y las del audio y del video comparten fila en «video + audio»",
          (all(chips[(x, 6)][0] != "F" for x in range(11, 27)), chips[(19, 6)][0], {y for (_x, y), v in chips.items() if v[2] is not None},
           {y for (_x, y), v in scene_site_center_cells(60, 6, ra, rb, 3.0, "both", 16 / 9.0, 1080, set(), {}, 5,
                                                         badge={"v": ("1080", 1.0), "a": ("AAC", 1.0)}).items() if v[2] is not None}),
          (True, "►", {9}, {15}))
    both = scene_site_center_cells(60, 6, ra, rb, 3.0, "both", 16 / 9.0, 1080, set(), {}, 5, badge={"v": ("1080", 1.0), "a": ("AAC", 1.0)})
    bars = {y for (x, y), v in both.items() if x > 40 and v[2] is None}
    check("«video + audio»: las barras miden lo que el marco (5 filas) y una pista terminada deja solo la otra, sin transición propia",
          (bars, scene_site_center_cells(60, 6, ra, rb, 3.0, "both", 16 / 9.0, 1080, {"video"}, {"video": 1.0}, 5, badge={"v": ("1080", 1.0), "a": ("AAC", 1.0)})
           == scene_site_center_cells(60, 6, ra, rb, 3.0, "both", 16 / 9.0, 1080, {"video"}, {"video": 2.9}, 5, badge={"v": ("1080", 1.0), "a": ("AAC", 1.0)})),
          ({10, 11, 12, 13, 14}, True))
    # la escena viva: la tarjeta (fila y0+9) la limpia el dibujo que la reemplaza y la transición usa un solo plan
    S = scene_defaults()
    S.update(geo=(46, 24, 6, 17), a=ra, b=rb, name="YouTube", mode="video", mode_orig="video", title_raw="Pan casero", label="Analizando enlace",
             pct=10, shown=0.2, aspect=16 / 9.0, res=1080, vinfo={"codec": "avc1", "fps": 30})
    st = scene_state()
    hold = SITE_HOLD_AT * SITE_SECS
    ta, fr = hold + 0.2, 0
    for _ in range(12):
        scene_cells(S, st, ta, ta, fr)
        ta, fr = ta + 0.05, fr + 1
    c_site = scene_cells(S, st, ta, ta, fr)
    S.update(label="Limpiando · 3")
    t_sw, plans = ta, set()
    for k in range(0, 30):
        ta = t_sw + k * 0.04
        c_mid = scene_cells(S, st, ta, ta, fr + k)
        if st.get("flow"):
            plans.add(id(st["flow"]["plan"]))
    check("escena 1.4.2: con la tarjeta en y0+9 y un dibujo nuevo, la fila se limpia entera y el cambio usa un solo plan",
          (any(y == 15 for (_x, y) in c_site), "1080p" in "".join(v[0] for (_x, y), v in sorted(c_mid.items()) if y == 15), len(plans), st["mcur"]), (True, False, 1, "clean"))   # 1.4.8: la fila y0+9 ahora lleva el estado de la escena nueva

    # ── 1.4.6: el carril de tarjetas (hasta 3 a la vez; entran por la derecha; salen por la izquierda, las desplace otra o hayan terminado: 1.5.5) ──
    _rt = lambda cs, y: "".join(cs[(x, y)][0] if (x, y) in cs else " " for x in range(1, 70)).strip()
    _Wr = {"geo": (60, 24, 6, 17), "label": "Descargando video 1/2", "mode_orig": "both", "stream_total": 2, "stream_seen": 1, "skind": {1: "video"},
           "spct": {1: 30.0}, "past_dl": True}
    _wa = rail_want(_Wr)
    check("carril 1.4.6: lo que pide el estado: la pista activa con su % real y la que falta en espera (se adivina por el modo)",
          [(w["id"], w["kind"], w["state"], w["pct"]) for w in _wa], [("video", "video", "activa", 30.0), ("audio", "audio", "espera", None)])
    check("carril 1.4.6: con otro texto de estado todas las pistas están hechas y piden unión o guardado",
          ([w["state"] for w in rail_want(dict(_Wr, label="Uniendo pistas"))], [w["id"] for w in rail_want(dict(_Wr, label="Uniendo pistas"))],
           [w["id"] for w in rail_want(dict(_Wr, label="Guardando"))], rail_want({"label": "Analizando"})),
          (["hecho", "hecho", "activa"], ["video", "audio", "merge"], ["video", "audio", "save"], []))
    check("carril 1.4.6: caben 3 tarjetas en cualquier ancho (de 31 a 80 columnas)",
          all(3 * rail_width(w_) + 2 * RAIL_GAP <= w_ - 2 and 8 <= rail_width(w_) <= 16 for w_ in range(31, 81)), True)
    _Tr = {}
    _R0 = rail_step(_Wr, _Tr, 60, 1.0, 0.0)
    check("carril 1.4.6: las tarjetas del primer cuadro ya están en su sitio (el morph las trae del dibujo anterior), no se deslizan",
          ([c["id"] for c in _R0["cards"]], all(c["x"] == c["tx"] and c["fade"] == 1.0 for c in _R0["cards"]), _R0["move"]), (["video", "audio"], True, False))
    _Wr.update(label="Descargando audio 2/2", stream_seen=2, skind={1: "video", 2: "audio"}, spct={1: 100.0, 2: 10.0})
    rail_step(_Wr, _Tr, 60, 1.1, 0.0)
    _hold = [c["state"] for c in _R0["cards"]]
    rail_step(_Wr, _Tr, 60, 1.1 + RAIL_DONE_HOLD + 0.05, 0.0)
    _ex = {c["id"]: c["exit"] for c in _R0["cards"]}
    check("carril 1.4.6: una pista terminada se queda con su ✓ un instante y sale por la IZQUIERDA (1.5.5); la que sigue se queda",
          (_hold, _ex), (["hecho", "activa"], {"video": "left", "audio": None}))
    for q in range(1, 40):
        rail_step(_Wr, _Tr, 60, 1.9 + q * 0.05, 0.0)
    check("carril 1.4.6: la tarjeta que salió ya no está y la otra queda centrada", ([c["id"] for c in _R0["cards"]], _R0["cards"][0]["x"] == _R0["cards"][0]["tx"]), (["audio"], True))
    _Wr.update(label="Uniendo pistas", spct={1: 100.0, 2: 100.0})
    rail_step(_Wr, _Tr, 60, 3.87, 0.0)                                     # 1.5.5: un cuadro corto (dt 0.02 s); con la entrada al doble de velocidad, uno de 0.15 s ya la acerca casi del todo
    _mc = [c for c in _R0["cards"] if c["id"] == "merge"][0]
    check("carril 1.4.6: una tarjeta nueva entra por la derecha (fuera de la pantalla) y se desliza a su sitio",
          (_mc["x"] > _mc["tx"] + 10, _mc["fade"] < 1.0, _mc["tx"] < 60), (True, True, True))
    for q in range(1, 90):
        rail_step(_Wr, _Tr, 60, 4.0 + q * 0.05, 0.0)
    check("carril 1.4.6: tras deslizarse queda en su sitio y a todo color", (_mc["x"] == _mc["tx"], _mc["fade"]), (True, 1.0))
    # más de 3: la nueva (activa) desplaza a la más antigua que no esté activa, y esa sale por la IZQUIERDA; la que espera no desplaza a nadie
    _Wm = {"label": "Descargando audio 3/5", "mode_orig": "audio", "stream_total": 5, "stream_seen": 3, "past_dl": True,
           "skind": {1: "audio", 2: "audio", 3: "audio"}, "spct": {1: None, 2: None, 3: 5.0}}
    _Tm = {}
    _Rm = rail_step(_Wm, _Tm, 60, 1.0, 0.0)
    check("carril 1.4.9: con 5 pistas de audio hay UNA sola tarjeta de audio (la pista en curso: 3.ª de 5, con su % real)",
          ([c["id"] for c in _Rm["cards"]], [c["state"] for c in _Rm["cards"]], [(c["pct"], c["idx"], c["of"]) for c in _Rm["cards"]]),
          (["audio"], ["activa"], [(5.0, 3, 5)]))
    _Wm.update(label="Uniendo pistas", spct={1: 100.0, 2: 100.0, 3: 100.0, 4: 100.0, 5: 100.0})
    rail_step(_Wm, _Tm, 60, 1.1, 0.0)
    check("carril 1.4.9: al acabar todas las pistas la tarjeta de audio se pone ✓ y entra la unión; nunca más de 3 vivas",
          ([c["state"] for c in _Rm["cards"] if c["id"] == "audio"], [c["id"] for c in _Rm["cards"] if c["id"] == "merge"], len([c for c in _Rm["cards"] if not c["exit"]]) <= RAIL_MAX),
          (["hecho"], ["merge"], True))
    _Wf = {"label": "Guardando", "past_dl": True, "stream_total": 3, "stream_seen": 3, "mode_orig": "audio", "skind": {1: "video", 2: "audio", 3: "audio"},
           "spct": {1: 100.0, 2: 100.0, 3: 50.0}}
    _Tf = {}
    _Rf = rail_step(dict(_Wf, label="Descargando audio 3/3", past_dl=False), _Tf, 60, 1.0, 0.0)
    _Rf["cards"].append({"id": "x1", "kind": "merge", "pct": None, "state": "activa", "x": 20.0, "tx": 20.0, "fade": 1.0, "exit": None, "exit_t": None, "done_t": None, "born": 1.0})
    _Rf["gone"].add("x1")
    _Rf["cards"].append({"id": "x2", "kind": "audio", "pct": None, "state": "activa", "x": 30.0, "tx": 30.0, "fade": 1.0, "exit": None, "exit_t": None, "done_t": None, "born": 1.0})
    _Rf["gone"].add("x2")
    rail_step(_Wf, _Tf, 60, 1.05, 0.0)
    _sides = {c["id"]: c["exit"] for c in _Rf["cards"]}
    check("carril 1.4.6: al llenarse, quien cede el sitio sale por la izquierda (y las que terminaron también, 1.5.5)",
          ([_sides[k] for k in ("audio",)], any(v == "left" for v in _sides.values())), ([_sides["audio"]], True))
    _Tl2 = {}
    _Rl = rail_step(_Wr, _Tl2, 60, 1.0, 0.0)
    cl = scene_rail_cells(60, 6, ra, rb, _Rl["cards"], 1.3)
    cl2 = scene_rail_cells(60, 6, ra, rb, _Rl["cards"], 1.6)
    check("carril 1.4.6: dibujo: etiqueta, marco, barra y texto en y0+4 … y0+9, repetible, se mueve y todo dentro de la pantalla",
          ({y for (_x, y) in cl} <= set(range(10, 16)), cl == scene_rail_cells(60, 6, ra, rb, _Rl["cards"], 1.3), cl != cl2,
           all(1 <= x < 60 for (x, _y) in cl), "ECHO" not in _rt(cl, 10)), (True, True, True, True, True))
    _Cc = {"id": "t1", "kind": "video", "pct": 10.0, "state": "activa", "x": 20.0, "tx": 20.0, "fade": 1.0, "exit": None, "exit_t": None, "done_t": None, "born": 0.0}
    _nbar = lambda cs: sum(1 for (_x, y), v in cs.items() if y == 14 and v[0] == "━")
    check("carril 1.4.6 (1.5.6): la tarjeta no lleva barra de progreso en ningún estado (con 10 % y 90 % es lo mismo); hecho: ✓; espera: nada",
          (_nbar(rail_card_cells(_Cc, 6, ra, rb, 1.0, 10)) == _nbar(rail_card_cells(dict(_Cc, pct=90.0), 6, ra, rb, 1.0, 10)) == 0,
           "✓" in _rt(rail_card_cells(dict(_Cc, state="hecho", pct=100.0), 6, ra, rb, 1.0, 10), 15),
           _nbar(rail_card_cells(dict(_Cc, state="espera", pct=None), 6, ra, rb, 1.0, 10)),
           "VIDEO" in _rt(rail_card_cells(_Cc, 6, ra, rb, 1.0, 10), 10), "AUDIO" in _rt(rail_card_cells(dict(_Cc, kind="audio"), 6, ra, rb, 1.0, 10), 10),
           "UNIÓN" in _rt(rail_card_cells(dict(_Cc, kind="merge"), 6, ra, rb, 1.0, 10), 10), "GUARDADO" in _rt(rail_card_cells(dict(_Cc, kind="save"), 6, ra, rb, 1.0, 10), 10)),
          (True, True, 0, True, True, True, True))
    check("carril 1.4.6: cada tarjeta cabe en su ancho (8 a 16 columnas) y en sus 6 filas, con y sin %, en todos los estados",
          all({y for (_x, y) in rail_card_cells(dict(_Cc, kind=k_, state=s_, pct=p_, x=10.0), 6, ra, rb, t_, cw_)} <= set(range(10, 16))
              and min(x for (x, _y) in rail_card_cells(dict(_Cc, kind=k_, state=s_, pct=p_, x=10.0), 6, ra, rb, t_, cw_)) >= 10
              and max(x for (x, _y) in rail_card_cells(dict(_Cc, kind=k_, state=s_, pct=p_, x=10.0), 6, ra, rb, t_, cw_)) < 10 + cw_
              for k_ in ("video", "audio", "merge", "save") for s_ in ("activa", "espera", "hecho") for p_ in (None, 55.0) for t_ in (0.2, 0.9) for cw_ in (8, 9, 12, 16)), True)
    _Ca = dict(_Cc, kind="audio")
    check("carril 1.4.9: todas las pistas de audio comparten UNA animación (el ecualizador): el dibujo no depende del idioma ni del orden; se mueve activo y queda quieto hecho",
          (rail_card_cells(dict(_Ca, idx=1, of=3), 6, ra, rb, 0.9, 12) == rail_card_cells(dict(_Ca, idx=3, of=3, lang="en-US"), 6, ra, rb, 0.9, 12) or
           {k: v for k, v in rail_card_cells(dict(_Ca, idx=1, of=3), 6, ra, rb, 0.9, 12).items() if k[1] >= 11 and k[1] <= 13} ==
           {k: v for k, v in rail_card_cells(dict(_Ca, idx=3, of=3, lang="en-US"), 6, ra, rb, 0.9, 12).items() if k[1] >= 11 and k[1] <= 13},
           rail_card_cells(dict(_Ca, state="hecho", pct=100.0), 6, ra, rb, 0.3, 12) == rail_card_cells(dict(_Ca, state="hecho", pct=100.0), 6, ra, rb, 0.7, 12),
           rail_card_cells(dict(_Ca, state="activa"), 6, ra, rb, 0.3, 12) != rail_card_cells(dict(_Ca, state="activa"), 6, ra, rb, 0.5, 12)),
          (True, True, True))
    check("carril 1.4.9: la tarjeta de audio cabe en su ancho (8 a 16) y en sus 6 filas, en todos los estados",
          all({y for (_x, y) in rail_card_cells(dict(_Ca, state=s_, pct=p_, x=10.0), 6, ra, rb, t_, cw_)} <= set(range(10, 16))
              and 10 <= min(x for (x, _y) in rail_card_cells(dict(_Ca, state=s_, pct=p_, x=10.0), 6, ra, rb, t_, cw_))
              and max(x for (x, _y) in rail_card_cells(dict(_Ca, state=s_, pct=p_, x=10.0), 6, ra, rb, t_, cw_)) < 10 + cw_
              for s_ in ("activa", "espera", "hecho") for p_ in (None, 55.0) for t_ in (0.2, 0.55, 0.9, 1.3) for cw_ in (8, 9, 12, 16)), True)
    _Wl = {"label": "Descargando audio es-US 2/3", "mode_orig": "both", "stream_total": 3, "stream_seen": 2, "past_dl": True,
           "skind": {1: "video", 2: "audio", 3: "audio"}, "spct": {1: 100.0, 2: 5.0}, "slang": {2: "es-US", 3: "en-US"}}
    check("carril 1.4.9: las pistas se reúnen por tipo: un video y un audio (pista en curso: 1.ª de 2, es-US, 5 %)",
          [(w["id"], w["state"], w["pct"], w["lang"], w["idx"], w["of"]) for w in rail_want(_Wl)],
          [("video", "hecho", 100.0, None, 1, 1), ("audio", "activa", 5.0, "es-US", 1, 2)])
    check("carril 1.4.9: el título de audio lleva el idioma («AUDIO ES-US»); si no cabe, solo «ES-US»; sin idioma, con varias pistas «AUDIO 2»; con una sola, «AUDIO»",
          (_rt(rail_card_cells(dict(_Ca, lang="es-US"), 6, ra, rb, 1.0, 16), 10), _rt(rail_card_cells(dict(_Ca, lang="es-US"), 6, ra, rb, 1.0, 10), 10),
           _rt(rail_card_cells(dict(_Ca, idx=2, of=3), 6, ra, rb, 1.0, 10), 10), _rt(rail_card_cells(_Ca, 6, ra, rb, 1.0, 10), 10)),
          ("AUDIO ES-US", "ES-US", "AUDIO 2", "AUDIO"))
    # el título cambia de pista en pista con el estilo de las tarjetas: el viejo sale por la izquierda y el nuevo entra por la derecha
    _Wt = {"label": "Descargando audio es-US 1/2", "mode_orig": "audio", "stream_total": 2, "stream_seen": 1, "past_dl": True,
           "skind": {1: "audio"}, "spct": {1: 40.0}, "slang": {1: "es-US"}}
    _Tt = {}
    _Rt = rail_step(_Wt, _Tt, 60, 1.0, 0.0)
    _ct = _Rt["cards"][0]
    _t0 = _rt(rail_card_cells(_ct, 6, ra, rb, 1.0, 16), 10)
    _Wt.update(label="Descargando audio en-US 2/2", stream_seen=2, skind={1: "audio", 2: "audio"}, spct={1: 100.0, 2: 0}, slang={1: "es-US", 2: "en-US"})
    rail_step(_Wt, _Tt, 60, 2.0, 0.0)
    _tw = [rail_card_cells(_ct, 6, ra, rb, 2.0 + k_ * RAIL_TITLE_T / 10.0, rail_width(60)) for k_ in range(0, 12)]
    _xl, _xr = _ct["x"], _ct["x"] + rail_width(60)
    check("carril 1.4.9: la misma tarjeta sigue viva al pasar de pista (no sale ni entra otra) y su título es el de la pista nueva, con su % y sin ✓",
          ([c["id"] for c in _Rt["cards"]], _ct["state"], _ct["pct"], _ct["title_old"], _ct["title"], _ct["exit"]),
          (["audio"], "activa", 0, "AUDIO ES-US", "AUDIO EN-US", None))
    check("carril 1.4.9: el título se desliza: empieza como el viejo, termina como el nuevo y en medio ninguna letra sale de su tarjeta (fila de la etiqueta)",
          (_rt(_tw[0], 10), _rt(_tw[10], 10), _rt(_tw[11], 10), _rt(_tw[3], 10) not in ("AUDIO ES-US", "AUDIO EN-US"),
           all(_xl <= x < _xr for cs in _tw for (x, y) in cs if y == 10), all(y in range(10, 16) for cs in _tw for (_x, y) in cs)),
          ("AUDIO ES-US", "AUDIO EN-US", "AUDIO EN-US", True, True, True))
    check("carril 1.4.9: el cambio de título es repetible y lo sigue el loop de la escena (hasta que termina de deslizarse)",
          (rail_card_cells(_ct, 6, ra, rb, 2.2, rail_width(60)) == rail_card_cells(_ct, 6, ra, rb, 2.2, rail_width(60)),
           rail_loop(_Wt, _Tt, 60, 0.0) >= RAIL_TITLE_T - 0.01, _Rt["move"]),
          (True, True, True))
    # ── 1.4.8: estilo visual único y los tres modos de UX ──
    check("UX 1.5.1: wait · real · cualquier número son los segundos; los nombres de antes siguen y lo inválido cae en wait",
          [ux_mode_parse(x_, y_) for x_, y_ in (("wait", None), ("real", None), ("3", None), ("2,5", None), ("0", None), ("99", None), ("-4", None), ("espera", None),
                                                 ("ya", None), ("segundos", "3"), ("segundos", None), ("segundos", "x"), ("loop", None), ("", None), ("zzz", None), (" REAL ", None))],
          [("loop", None), ("real", None), ("secs", 3.0), ("secs", 2.5), ("secs", 0.0), ("secs", 60.0), ("loop", None), ("loop", None),
           ("real", None), ("secs", 3.0), ("secs", UX_SECS_DEFAULT), ("secs", UX_SECS_DEFAULT), ("loop", None), ("loop", None), ("loop", None), ("real", None)])
    check("UX 1.5.1: --config tiene una sola opción de UX (DLPY_UX, wait por omisión); ya no hay DLPY_UX_SECS ni DLPY_SCENE_MODE en la lista",
          ([(n, v) for n, v, _t in CONFIG_OPTIONS if n in ("DLPY_UX", "DLPY_UX_SECS")], any(n == "DLPY_SCENE_MODE" for n, _v, _t in CONFIG_OPTIONS)),
          ([("DLPY_UX", "wait")], False))
    _smx = SCENE_MODE
    try:
        res_ = []
        for md_ in (("loop", None), ("real", None), ("secs", 3.0)):
            globals()["SCENE_MODE"] = md_
            res_.append((rail_hold(), motif_hold_secs({"geo": (60, 24, 6, 17)}, {"ms": 0.0, "mt": 0.0}, "send", 1.0)))
    finally:
        globals()["SCENE_MODE"] = _smx
    check("UX 1.4.8: el ✓ de una tarjeta y la espera entre escenas según el modo (espera: el loop · ya: nada · segundos: N s)",
          [(round(h_, 6), round(w_, 6)) for h_, w_ in res_],
          [(RAIL_DONE_HOLD, round((-1.0) % SEND_CYCLE, 6)), (0.0, 0.0), (3.0, 2.0)])
    _Dc = _MotifCtx(60, 6, ra, rb, 5.7, 3, {}, set())
    _Sc = {"conv": {"pct": 25.0, "src": "VP9", "dst": "HEVC"}, "pp_pct": 80.0, "check": {"items": [("VP9", 1)], "verdict": None}, "clean": 3, "send_to": "DLPY",
           "ask": {"secs": 20, "t0": time.time() - 5, "src": "VIEJO", "dst": "NUEVO"}, "welcome": {"kind": "updated", "old": "1.4.6", "new": "1.4.7"}}
    _Tc = {"ms": 4.0, "mt": None, "cinfo": ("VP9", "HEVC", 4.0)}
    _ch = {k_: scene_chrome(k_, MOTIFS[k_].draw(_Sc, _Tc, _Dc, 5.0), _Sc, _Tc, _Dc, 5.0) for k_ in CHROME_PARTS}
    check("estilo 1.4.8: cada escena de ancho completo lleva su etiqueta en y0+4 (su nombre en mayúsculas) y (1.5.6) ninguna lleva barra en y0+8 ni % en ninguna fila",
          (all(MOTIF_NAMES[k_].upper() in _rt(c_, 10) for k_, c_ in _ch.items()),
           all(not _rt(c_, 14) for c_ in _ch.values()),
           all("%" not in _rt(c_, y_) for c_ in _ch.values() for y_ in (10, 14, 15))), (True, True, True))
    check("estilo 1.4.8: el dibujo no se toca (todo lo que tenía sigue igual) y todo cabe en la pantalla y en y0+4 … y0+9",
          (all(all(c_.get(k2_) == v2_ for k2_, v2_ in MOTIFS[k_].draw(_Sc, _Tc, _Dc, 5.0).items()) for k_, c_ in _ch.items()),
           all(all(1 <= x < 60 and 10 <= y <= 15 for (x, y) in c_) for c_ in _ch.values())), (True, True))
    check("estilo 1.4.8 (1.5.6): la conversión no lleva % ni barra (el estado activo va vacío); la espera de Enter dice «espera»; guardar termina en ✓ y verde",
          (_rt(_ch["conv"], 15), _rt(_ch["ask"], 15), _rt(scene_chrome("save", MOTIFS["save"].draw(_Sc, _Tc, _Dc, 5.0), _Sc, _Tc, _Dc, 5.0 - SAVE_STREAM_SECS - 0.2), 15),
           _rt(scene_chrome("save", MOTIFS["save"].draw(_Sc, _Tc, _Dc, 5.0), _Sc, _Tc, _Dc, 5.0), 15) != "✓",
           not any(v[0] == "━" for (x, y), v in scene_chrome("conv", MOTIFS["conv"].draw(dict(_Sc, conv={"pct": 90.0}), _Tc, _Dc, 5.0),
                                                              dict(_Sc, conv={"pct": 90.0}), _Tc, _Dc, 5.0).items() if y == 14)),
          ("", "espera", "✓", True, True))
    _Cs = {"id": "t1", "kind": "video", "pct": 25.0, "state": "activa", "x": 20.0, "tx": 20.0, "fade": 1.0, "exit": None, "exit_t": None, "done_t": None, "born": 0.0}
    _cr = rail_card_cells(_Cs, 6, ra, rb, 5.7, 10)
    check("estilo 1.4.8: la tarjeta del carril y la escena de ancho completo usan las mismas filas, la misma etiqueta/estado y el mismo color de etiqueta",
          (_rt(_cr, 10), _rt(_cr, 15), {y for (_x, y) in _cr if y in (10, 14, 15)}, {y for (_x, y) in _ch["conv"] if y in (10, 14, 15)},
           {v[1] for (_x, y), v in _cr.items() if y == 10}, {v[1] for (_x, y), v in _ch["conv"].items() if y == 10}),
          ("VIDEO", "", {10}, {10}, {SCENE_WHITE}, {SCENE_WHITE}))   # 1.5.6: ni barra (fila 14) ni % (fila 15) en una escena activa: solo etiqueta y dibujo
    _cb = rail_card_cells(_Cs, 6, ra, rb, 5.7, 12, {"v": ("1080p", None)})
    check("carril 1.5.0: la tarjeta activa no lleva % (ni con barra real ni sin ella); con dato del archivo, solo ese dato; hecho y espera igual que antes",
          ("%" in _rt(_cb, 15), _rt(_cb, 15), "%" in _rt(rail_card_cells(dict(_Cs, pct=None), 6, ra, rb, 5.7, 10), 15),
           _rt(rail_card_cells(dict(_Cs, state="hecho"), 6, ra, rb, 5.7, 10), 15), _rt(rail_card_cells(dict(_Cs, state="espera"), 6, ra, rb, 5.7, 10), 15)),
          (False, "1080p", False, "✓", "espera"))
    check("carril 1.4.6: la que sale pasa por detrás de las que se quedan (no se mezclan los glifos)",
          all(not ({x for (x, _y) in scene_rail_cells(60, 6, ra, rb, [dict(_Cc, x=float(xe), exit="left", exit_t=0.0, id="e"), dict(_Cc, x=20.0, id="v")], 1.0)
                    if 20 <= x < 20 + rail_width(60)} - {x for (x, _y) in rail_card_cells(dict(_Cc, x=20.0), 6, ra, rb, 1.0, rail_width(60))}) for xe in (14, 18, 24)), True)
    check("carril 1.4.6: «Carril» es un motivo con nombre; descarga, unión y guardado lo piden (D L P Y, conversión y espera mandan) y DLPY_SCENE_RAIL=0 devuelve los tres de la 1.4.5",
          (motif_name("rail"), [scene_motif_kind(x) for x in ({"label": "Descargando audio 2/2"}, {"label": "Uniendo pistas"}, {"label": "Guardando"},
                                                              {"label": "Guardando", "brand": True}, {"label": "Guardando", "conv": {"end": None}})]),
          ("Carril", ["rail", "rail", "rail", "dlpy", "conv"]))
    _rs = SCENE_RAIL
    try:
        globals()["SCENE_RAIL"] = False
        _old3 = [scene_motif_kind(x) for x in ({"label": "Descargando audio 2/2"}, {"label": "Uniendo pistas"}, {"label": "Guardando"})]
    finally:
        globals()["SCENE_RAIL"] = _rs
    check("carril 1.4.6: con DLPY_SCENE_RAIL=0 vuelven Descarga, Unión y Guardado", _old3, ["download", "merge", "save"])
    check("carril 1.4.6: DLPY_SCENE_RAIL está en la configuración, encendida por omisión",
          [(n, v) for n, v, _t in CONFIG_OPTIONS if n == "DLPY_SCENE_RAIL"], [("DLPY_SCENE_RAIL", "1")])
    _Sq = {"geo": (60, 24, 6, 17)}
    check("carril 1.4.6: el loop del carril espera el ✓ y la salida (≤ el tope de espera); sin tarjetas no espera",
          (rail_loop(_Sq, {}, 60, 0.3), 0.0 < rail_loop(_Sq, {"rail": _Rl}, 60, 0.3) <= MOTIF_HOLD_MAX, motif_loop_left(_Sq, {"ms": 0.0, "mt": None, "rail": _Rl}, "rail", 0.3) > 0.0),
          (0.0, True, True))
    check("carril 1.4.6: mientras las tarjetas se deslizan la escena va a tope de cuadros; quieto, a CONV_FPS",
          (scene_fps({"label": "Descargando video"}, {"rail_fast": 9.0}, 8.9, SITE_HOLD_AT * SITE_SECS), scene_fps({"label": "Descargando video"}, {"rail_fast": 9.0}, 9.5, SITE_HOLD_AT * SITE_SECS)),
          (SITE_FPS, CONV_FPS))
    # el recorrido completo por scene_motif: sitio → carril (las celdas viajan) → conversión (el ✓ y la salida terminan antes) → carril otra vez
    _Sf = {"geo": (46, 24, 6, 17), "a": ra, "b": rb, "brand": False, "conv": None, "label": "Preparando", "done": set(), "mode_orig": "both", "mode": "both",
           "stream_total": 2, "stream_seen": 0, "aspect": 16 / 9.0, "res": 1080}
    _Tq = {"mcur": None, "mprev": None, "mt": None, "ms": 0.0, "msp": 0.0, "site_done": set(), "site_done_at": {}, "site_prev_cells": {}, "site_trans_t": None}
    _fr, _okc = 0, True
    def _run(t0_, t1_, st_=0.05):
        nonlocal_t = [t0_]
        out_ = []
        while nonlocal_t[0] <= t1_:
            c_ = scene_motif(_Sf, _Tq, {}, nonlocal_t[0], 1.16, int(nonlocal_t[0] * 24))
            out_.append(c_)
            nonlocal_t[0] += st_
        return out_
    _run(2.0, 2.3)
    _Sf.update(label="Descargando video 1/2", stream_seen=1, skind={1: "video"}, spct={1: 5.0}, past_dl=True)
    _f1 = _run(2.4, 3.6)
    _Sf.update(spct={1: 100.0}, label="Descargando audio 2/2", stream_seen=2, skind={1: "video", 2: "audio"})
    _f2 = _run(3.7, 5.5)
    _Sf.update(label="Uniendo pistas", spct={1: 100.0, 2: 100.0})
    _f3 = _run(5.6, 7.6)
    _Sf.update(label="Convirtiendo", conv={"end": None, "src": "VP9", "dst": "HEVC", "t0": 7.7})
    _f4 = _run(7.7, 11.5)
    check("carril 1.4.6: sitio → carril → conversión sin errores, siempre dentro de y0+4 … y0+9 y de la pantalla; la conversión espera el final del carril",
          (all(1 <= x < 46 and 10 <= y <= 15 for fr_ in _f1 + _f2 + _f3 + _f4 for (x, y) in fr_),
           _Tq["mcur"], any("✓" in "".join(v[0] for v in fr_.values()) for fr_ in _f2 + _f3)), (True, "conv", True))


SELFTEST_GROUPS = (_st_t1, _st_t2, _st_t3, _st_t4, _st_t5, _st_t6,
                   _st_t7_t9, _st_t10, _st_t11, _st_t12, _st_t13, _st_t14,
                   _st_t15, _st_t16, _st_t17, _st_t18, _st_t19, _st_t20_t22,
                   _st_t23, _st_t24, _st_t25, _st_t26, _st_t27, _st_t27_limpieza, _st_t28_morph)


def selftest():
    """`python dlpy.py --selftest`: pruebas rápidas de funciones puras (sin disco ni red)."""
    fails = []

    # [T0] Infraestructura de la prueba
    def check(nombre, obtenido, esperado):
        if obtenido != esperado:
            fails.append(nombre)
            print(f"✗ {nombre}: esperado {esperado!r}, obtenido {obtenido!r}")

    for grupo in SELFTEST_GROUPS:
        grupo(check)
    print(f"Autoprueba: {'OK' if not fails else str(len(fails)) + ' fallo(s)'}")
    return 1 if fails else 0


# ─────────────── [K2] Funciones disponibles según el sistema ───────────────
def capabilities():
    """[(función, estado, motivo)] de lo que funciona en ESTE sistema, según lo que hay instalado."""
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
    add("Carpeta interna (oculta)", "ok", f"{INTERNAL_DIR} (estado, caché y script).")
    if ENV_STATE["error"]:
        add("Variables DLPY_* recordadas", "no", f"No se guardan en {ENV_STATE['path']}: {ENV_STATE['error']}")
    elif ENV_STATE["path"]:
        add("Variables DLPY_* recordadas", "ok", f"Se guardan en {ENV_STATE['path']} (sobreviven a las actualizaciones).")
    add("Carpeta de descargas", "ok", f"{FILES_DIR} (sandbox de a-Shell, visible en Archivos).")
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
    add("Colores y barras animadas", "ok" if USE_COLOR else "part",
        "ANSI activo." if USE_COLOR else
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
    """Importa yt_dlp en segundo plano (~170 ms en a-Shell)"""
    def _go():
        with quiet("preload_ytdlp"):
            import yt_dlp  # noqa: F401
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
        _env_cols = _ORIG_GTS((0, 0)).columns
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


def config_rows(data):
    """1.3.2:"""
    rows = [(n, d, t, data.get(n)) for n, d, t in CONFIG_OPTIONS]
    known = {n for n, _d, _t in CONFIG_OPTIONS}
    rows += [(k, "", "variable guardada que no está en la lista de opciones conocidas", data[k]) for k in sorted(data) if k not in known]
    return rows


def config_choice(raw, rows):
    """1.3.2:"""
    s = str(raw or "").strip()
    low = s.lower()
    if low in ("", "q", "salir", "exit"):
        return ("quit",)
    if low in ("l", "lista", "list"):
        return ("list",)
    if low in ("o", "olvidar"):
        return ("forget",)
    if "=" in s:
        return ("set", s)
    if s.isdigit():
        n = int(s)
        return ("pick", rows[n - 1][0]) if 1 <= n <= len(rows) else ("bad", f"1-{len(rows)}")
    key = config_key(s)
    if key and key in {r[0] for r in rows}:
        return ("pick", key)
    return ("bad", "nº, nombre, NOMBRE=valor, l, o o q")


def config_show_list(rows):
    """1.3.2: una línea por opción: «nº ● NOMBRE valor» (● = guardada; sin guardar, entre corchetes la de por omisión)."""
    w = term_width()
    for i, (name, default, _text, val) in enumerate(rows, 1):
        head = f"{i:>2} " + (paint("●", "mint") if val is not None else " ") + f" {name} "
        room = max(4, w - 5 - len(name) - 1)
        print(head + (paint(fit_text(val, room), "white", True) if val is not None else paint(fit_text(f"[{default or '—'}]", room), "gray")))


def config_interactive():
    """1.3.2:"""
    rc = 0
    kv("Archivo", ENV_FILE)
    print()
    config_show_list(config_rows(_read_env_json(ENV_FILE)))
    print()
    note("Nº o nombre: elegir · NOMBRE=valor: guardar · l: lista · o: olvidar todas · Enter: salir")
    prompt = paint("▸", "orange", True) + " "
    cur = prompt
    while True:
        rows = config_rows(_read_env_json(ENV_FILE))
        try:
            raw = ask_line(cur, True, "▸ ")
        except (EOFError, KeyboardInterrupt):
            break
        act = config_choice(raw, rows)
        if act[0] == "quit":
            break
        if act[0] == "bad":
            cur = retry_prompt(cur, raw, bad_prompt(act[1]), "Escribe " + act[1] + ".")
            continue
        cur = prompt
        try:
            if act[0] == "list":
                config_show_list(rows)
                continue
            if act[0] == "forget":
                if ask("¿Borrar todas las variables guardadas?", default=False):
                    had = len(_read_env_json(ENV_FILE))
                    config_write({}, ENV_FILE)
                    m_ok(f"Configuración borrada ({had} guardada{'' if had == 1 else 's'})")
                continue
            item = act[1]
            if act[0] == "pick":
                _n, default, text, val = next(r for r in rows if r[0] == act[1])
                print(paint("▍", "orange") + paint(act[1], "white", True))
                note(text)
                kv("Guardado", val if val is not None else "(ninguno)")
                kv("Por omisión", default or "—")
                note("Escribe el valor nuevo · Enter = dejarlo · - = borrar")
                try:
                    new = ask_line(prompt, True, "▸ ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if not new:
                    note("Sin cambios.")
                    continue
                item = act[1] + "=" + ("" if new == "-" else new)
            changes, errors = config_edit([item], ENV_FILE)
            for key, _old, new_v in changes:
                m_ok(f"{key} = {new_v}" if new_v is not None else f"{key} borrada")
            if not changes and not errors:
                note("Sin cambios.")
            for msg in errors:
                m_err(msg)
                rc = 1
            if changes:
                note("Se aplica la próxima vez que abras DLpy.")
        except OSError as e:
            m_err(f"No se pudo guardar en {ENV_FILE}: {e}")
            rc = 1
    print()
    note("Listo. Con --config NOMBRE=valor también se guarda sin menú; --config --lista muestra solo lo guardado.")
    return rc


def clear_test():
    """`python dlpy.py --cleartest` (1.3.2):"""
    if not (tty_both()):
        print("--cleartest necesita un terminal interactivo.")
        return 1
    print(title_bar(f"DLpy v{VERSION}", paint("prueba de borrado", "gray")))
    print(rule())
    note("Se llena la pantalla, se borra con cada modo y eliges el que quede limpio sin deslizar.")
    prev, rc, saved = CLEAR_MODE, 0, None
    try:
        for name, text in CLEAR_MODES:
            if ask_line(paint(f"[{name}] ", "orange", True) + paint("Enter = probar ▸ ", "gray"), True, f"[{name}] Enter ▸ ").strip().lower() == "q":
                break
            rows = term_rows()
            for i in range(rows + 8):
                print(f"línea de prueba {i + 1}")
            time.sleep(0.8)
            globals()["CLEAR_MODE"] = name
            native_clear()
            print(paint(f"Modo {name}", "white", True))
            note(text)
            ans = ask_line(paint("¿Quedó limpia sin deslizar? s = guardar · n = siguiente · q = salir ▸ ", "gray"), True, "s/n/q ▸ ").strip().lower()
            if ans in ("s", "si", "sí", "y"):
                saved = name
                break
            if ans == "q":
                break
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        globals()["CLEAR_MODE"] = prev
    if saved:
        try:
            config_edit([f"DLPY_CLEARMODE={saved}"], ENV_FILE)
            m_ok(f"DLPY_CLEARMODE = {saved} (se aplica la próxima vez que abras DLpy)")
        except OSError as e:
            m_err(f"No se pudo guardar en {ENV_FILE}: {e}")
            rc = 1
    else:
        note("No se guardó ningún modo.")
    return rc


def print_config(args=None):
    """`python dlpy.py --config` (1.3.0):"""
    args = list(sys.argv[1:] if args is None else args)
    flags, pos = parse_cli(args)
    items = list(pos)
    if isinstance(flags.get("config"), str) and flags["config"]:
        items.insert(0, flags["config"])                      # «--config=NOMBRE=valor»
    print(title_bar(f"DLpy v{VERSION}", paint("config", "gray")))
    print(rule())
    rc = 0
    if (not items and not flags.get("olvidar") and not flags.get("opciones") and not flags.get("lista")
            and tty_both()):
        return config_interactive()                          # 1.3.2: «--config» a secas en un terminal = menú interactivo
    try:
        if flags.get("olvidar"):
            had = len(_read_env_json(ENV_FILE))
            config_write({}, ENV_FILE)
            m_ok(f"Configuración borrada ({had} guardada{'' if had == 1 else 's'})")
        changes, errors = config_edit(items, ENV_FILE)
    except OSError as e:
        m_err(f"No se pudo guardar en {ENV_FILE}: {e}")
        return 1
    for key, _old, new in changes:
        m_ok(f"{key} = {new}" if new is not None else f"{key} borrada")
    for msg in errors:
        m_err(msg)
        rc = 1
    data = _read_env_json(ENV_FILE)
    kv("Archivo", ENV_FILE)
    if ENV_STATE.get("migrated"):
        note(f"Se trajeron {ENV_STATE['migrated']} variable(s) del env.json antiguo.")
    print()
    print(paint("Guardadas", "white", True))
    if data:
        for k in sorted(data):
            print("  " + paint(k, "gray") + " = " + data[k])
    else:
        note("(ninguna)")
    if flags.get("opciones"):
        print()
        print(paint("Opciones conocidas", "white", True))
        for name, default, text in CONFIG_OPTIONS:
            print("  " + (paint("● ", "mint") if name in data else "  ") + name + paint(f"  [{default or '—'}]", "gray"))
            for ln in wrap_text(text, max(10, term_width() - 6)):
                print("    " + paint(ln, "gray"))
    print()
    note("Guardar: --config NOMBRE=valor · borrar una: --config NOMBRE= · borrar todas: --config --olvidar · opciones: --config --opciones")
    note("El nombre puede ir sin DLPY_ (rows = DLPY_ROWS). Un export manda en esa ejecución y también se guarda. DLPY_FORGET y DLPY_NOVERIFY son de una sola ejecución.")
    return rc


# ╔══════════════════════════════════════════════════════════════════════╗
# ║ ÁREA L · PRINCIPAL — main()                                          ║
# ╚══════════════════════════════════════════════════════════════════════╝
# ───────────────────────── [L1] Principal ─────────────────────────
class _Run:
    """Estado compartido entre los pasos de main(): cada paso lee y escribe aquí lo suyo (0.7.3)."""


def _end(rc):
    """Código de salida de un modo especial (los que devolvían None terminan con 0)."""
    return 0 if rc is None else rc


def _m_modes(run):
    """[M0a] Modos especiales (--selftest, --sistema, --perfil, --config, --2shortcuts, --scb, --scm:"""
    sys.argv[1:] = norm_args(sys.argv[1:])      # «—scb» (raya larga del teclado) → «--scb»
    if "--selftest" in sys.argv[1:]:
        return _end(selftest())
    if "--sistema" in sys.argv[1:]:
        return _end(print_capabilities())
    if "--perfil" in sys.argv[1:]:
        return _end(print_profile())
    if _wants(sys.argv[1:], "config"):
        return _end(print_config(sys.argv[1:]))              # 1.3.0: ver y cambiar las variables DLPY_* guardadas
    if _wants(sys.argv[1:], "cleartest"):
        return _end(clear_test())                            # 1.3.2: probar los modos de borrado de la consola
    if wants_2shortcuts(sys.argv[1:]):
        return _end(send_code_to_shortcut())
    cli_flags, cli_args = parse_cli(sys.argv[1:])
    NO_UPDATES["on"] = bool(cli_flags.get("noupdates") or cli_flags.get("no-updates") or UPDATE_DAYS == 0)
    LATE_UPDATES["on"] = cli_flags.get("shortcutpick") is not None and not NO_UPDATES["on"]
    if wants_scb(sys.argv[1:]):
        return _end(shortcut_back(cli_flags, cli_args))   # analiza y avisa al atajo «DLpy» con el JSON
    if wants_scm(sys.argv[1:]):
        return _end(shortcut_mode(cli_flags, cli_args))   # JSON en la salida y nada más
    run.cli_args = cli_args
    if cli_flags.get("view") is not None:        # 1.3.4: --view / --view=shortcut|view: el modo de vista solo para esta ejecución
        VIEW_RUN["mode"] = "view" if cli_flags["view"] is True else str(cli_flags["view"]).strip().lower() or "view"
    _sp = cli_flags.get("shortcutpick")
    if isinstance(_sp, str) and "://" in _sp and "=" not in _sp.split("://", 1)[0]:
        cli_args = [_sp] + list(cli_args)   # el atajo mandó la bandera vacía y Atajos se comió el vacío: eso era el enlace
        cli_flags["shortcutpick"] = ""
        run.cli_args = cli_args
    run.spick = parse_shortcut_pick(cli_flags.get("shortcutpick"))      # lo que eligió el atajo
    if run.spick is None and cli_flags.get("shortcutpick") is not None:
        run.spick = {}              # 0.8.4: bandera presente pero sin valores útiles: sigue siendo modo atajo
    if run.spick is not None:
        quiet_set(True)             # 0.8.1: sin animaciones hasta la intro del sitio
    input_lock()                    # iOS: entrada bloqueada hasta la primera pregunta
    return None


def _m_prepare(run):
    """[M0b] Preparación: carpetas y límite de almacenamiento."""
    early_site_intro(run)           # 0.8.2: con --shortcutpick la intro sale lo primero: consola limpia, sin preguntas antes
    os.makedirs(FILES_DIR, exist_ok=True)
    drop_internal_leftovers()       # resto de un reinicio de .dlpy_internal que se cortó
    os.makedirs(INTERNAL_DIR, exist_ok=True)
    ensure_dirs()
    clear_screen()                  # banner arriba, sin restos de la ejecución anterior

    if ENV_STATE["error"]:
        m_warn(f"No se pudieron guardar las variables DLPY_* en {ENV_STATE['path']}")
        note(ENV_STATE["error"])
    with quiet("clean_trash 0.9.9"):
        migrate_trash_dates()       # 1.1.8: lo que ya estaba en la papelera cuenta sus 30 días desde hoy (una vez)
        _gone = clean_trash()       # 0.9.9: trash con >30 días se borra definitivo
        SCENE["trash_gone"] = _gone
        if _gone and not SCENE["on"]:
            m_ok(f"Papelera: {_gone} archivo(s) borrado(s) definitivamente (más de {TRASH_EXPIRE_DAYS:g} días en ella).")
        if _gone and SCENE["on"]:   # 1.1.5: también se anota en la escena (no en el shell)
            SCENE["clean"] = _gone
            scene_status(clean_label("Vaciando", None, _gone))
            scene_hold(SCENE_CLEAN_SECS)
    if QUIET["on"]:
        CLEAN_LATE["on"] = True     # 0.8.2: --shortcutpick no pregunta: la limpieza se ofrece al terminar la descarga
    else:
        with quiet("clean_old"):
            clean_old()             # 0.9.9: >10 días -> trash
    check_storage()                 # antes de cualquier otro proceso
    return None


def _debug_environment():
    """Con DLPY_DEBUG: ancho del terminal y datos del entorno."""
    try:
        env_cols = _ORIG_GTS((0, 0)).columns
    except Exception as _ign:
        ignore("main", _ign)
        env_cols = 0
    m_info(f"Ancho del terminal: variable={env_cols or '?'} · ioctl={_ioctl_cols() or '?'} · medido={_PROBE['cols'] or '?'}"
           f" · texto={term_width()} · barras={safe_width()}")
    dbg("entorno", {"python": sys.version.split()[0], "plataforma": sys.platform, "modo": PLATFORM,
                    "maquina": getattr(os.uname(), "machine", "?") if hasattr(os, "uname") else "?",
                    "script": SCRIPT_PATH, "ffmpeg": shutil.which("ffmpeg"),
                    "files": FILES_DIR,
                    "internal": INTERNAL_DIR, "env": dict(ENV_STATE)})


def _m_update(run):
    """[M0c] Actualización del script, versión instalada y dependencias."""
    reexec = getattr(sys, "_dlpy_reexec", False)     # recién instalada por la anterior: ya se comprobó
    if "--actualizar" in sys.argv[1:]:
        if not reexec:
            check_update(force=True)
        if UPDATE_CHECKED["ok"] or reexec:
            check_mark("script", script_sig())
        return 0 if check_dependencies(force=True) else 1
    script_due = (not NO_UPDATES["on"] and not LATE_UPDATES["on"] and not reexec
                  and check_due("script", script_sig()))          # según DLPY_UPDATES (1.4.4: siempre · cada N días · nunca)
    deps_due = not NO_UPDATES["on"] and not LATE_UPDATES["on"] and check_due("deps")
    prefetch_phase(script_due, deps_due)                           # 1.4.4: DLpy, pip y yt-dlp se comprueban a la vez
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
    prefetch_summary()                                             # 1.4.4: todo al día → una sola línea en la escena
    cleanup_internal()
    if DEBUG:
        _debug_environment()
    return None


def resume_one(item):
    """Reanuda una descarga pendiente con su enlace y su elección guardados (los mismos pasos que una normal)."""
    reset_site_state()
    run = _Run()
    run.cli_args, run.spick = [item["link"]], dict(item["pick"])
    clear_screen()
    for step in RESUME_STEPS:
        rc = step(run)
        if rc is not None:
            return rc
    return 0


def _m_resume(run):
    """[M0d] Menú de descargas pendientes:"""
    if getattr(run, "spick", None) is not None or not (tty_both()):
        return None
    cli = getattr(run, "cli_args", None) or []
    try:
        items = resume_candidates(cli[0] if cli else None)
    except Exception as _ign:
        ignore("resume_candidates", _ign)
        return None
    picked = resume_menu(items) if items else []
    if not picked:
        return None
    results = []
    for k, it in enumerate(picked):
        rc = resume_one(it)
        results.append((it["title"], rc == 0))
        if rc != 0 and k < len(picked) - 1 and not ask_clean("¿Seguir con las demás descargas pendientes?", True):
            break
    print()
    for title, ok in results:
        (m_ok if ok else m_warn)(("Reanudada: " if ok else "No se completó: ") + title)
    if cli:
        return None
    return 0 if all(ok for _t, ok in results) else 1


def _m_link(run):
    """[M1] Enlace (1): yt_dlp se carga en segundo plano mientras se pide."""
    preload_ytdlp()                 # yt_dlp se carga en segundo plano mientras se pide el enlace

    # Antes de la primera pregunta: tirar Enter residual del lanzamiento por Atajos
    drain_pending_input(0.12)
    run.link = get_link(run.cli_args)
    if not run.link:
        m_err("Sin enlace.")
        return 1
    import yt_dlp                   # ya cargado por el hilo (o espera lo que falte)
    run.yt_dlp = yt_dlp
    roast_link(run.link)
    warn_youtube_js(run.link)
    return None


def _m_analyze(run):
    """[M1] Análisis (1 · 1b): extrae la información y deja listos formatos, audios, videos y pistas."""
    link = run.link
    scene_status("Analizando enlace", frac=0.02)
    # 1) Extraer información
    bar = Bar()
    if DEBUG:
        m_info("Analizando enlace...")
    else:
        bar.start("Analizando enlace")
    try:
        info, run.base_opts = analyze_link(run.yt_dlp, link)
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
    run.info = info

    with quiet("main"):
        save_json(LAST_FILE, {"link": link, "date": int(time.time()), "title": info.get("title") or ""})

    run.title = info.get("title") or "video"
    scene_title(run.title)
    scene_shape(info)
    run.key = video_key(info)
    run.index = load_json(INDEX_FILE)
    run.old_file, run.old_entry = lookup_downloaded(run.index, run.key)
    dbg("info", {"clave": run.key, "titulo": run.title, "id": info.get("id"),
                 "extractor": info.get("extractor_key"), "duracion": info.get("duration"),
                 "formatos": len(info.get("formats") or [])})
    dbg("ya descargado", {"archivo": run.old_file, "entrada": run.old_entry} if run.old_file else "no")
    roast_info(info, link, run.old_file)

    # 1b) Ya descargado: aquí NO se pregunta «¿Descargar de nuevo?»: se elige primero y reuse_downloaded
    # (paso 4c) pregunta solo si lo elegido es EXACTAMENTE lo que ya tienes.
    if run.old_file:
        dbg("ya descargado", {"archivo": run.old_file, "se pregunta": "después de elegir"})

    formats, audios, videos = split_formats(info)       # de peor a mejor calidad (misma lista que el atajo)
    run.formats, run.audios, run.videos = formats, audios, videos
    dbg("formatos sin códec (supuestos)", [f.get("format_id") for f in formats if f.get("_guess")])

    if not audios and not videos:
        m_err("No se encontraron formatos.")
        return 1

    run.orig_ids = mark_originals(audios)
    run.tracks, run.orig_lang = build_tracks(audios, run.orig_ids)
    tracks = run.tracks
    run.multi_lang = len({t["lang"] for t in tracks if t["lang"] != "und"}) > 1
    run.can_merge = ffmpeg_available()
    dbg("formatos", {"audio": len(audios), "video": len(videos), "ffmpeg": run.can_merge,
                     "ffmpeg_ruta": shutil.which("ffmpeg"), "idioma_original": run.orig_lang,
                     "originales": sorted(run.orig_ids)})
    dbg("pistas", [{"idioma": t["lang"], "format_id": t["fmt"].get("format_id"),
                    "original": t["original"], "apple": apple_audio(t["fmt"])}
                   for t in tracks])
    return None


def _ci_rows(run):
    """[M2] 2)"""
    from types import SimpleNamespace
    audios, videos, title = run.audios, run.videos, run.title
    orig_ids, can_merge, auto = run.orig_ids, run.can_merge, run.auto
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
    return SimpleNamespace(title=title, a_rows=a_rows, v_rows=v_rows, choices=choices, best_n=best_n,
                           auto_n=auto_n, auto_line=auto_line, a_flags=["apple", "orig"], v_flags=["apple"],
                           a_vis=a_vis, v_vis=v_vis,
                           can_more=len(a_vis) < len(a_rows) or len(v_vis) < len(v_rows))


def _ci_show_list(ls, full, scene_status_text=None):
    """Pantalla de la lista; devuelve True si quedan filas ocultas (se ven con «m»)."""
    if full:
        hide_keyboard(0.3)          # iOS: lista completa con el teclado abajo para poder deslizar
    if scene_status_text is not None:
        native_clear()
        scene_list_top(ls.title, scene_status_text, animate=not getattr(ls, "top_seen", False))
        ls.top_seen = True
    else:
        clear_screen()
        show_title(ls.title)
    legend(["apple", "orig"])
    a_show = ls.a_rows if full else [ls.a_rows[i] for i in ls.a_vis]
    v_show = ls.v_rows if full else [ls.v_rows[i] for i in ls.v_vis]
    asx, vsx = len(ls.a_rows) - len(a_show), len(ls.v_rows) - len(v_show)
    if ls.a_rows:
        header("AUDIO" + (f" · +{asx} más" if asx else ""))
        print_rows(a_show, ls.a_flags, AUDIO_HEAD)
    if ls.v_rows:
        header("VIDEO" + (f" · +{vsx} más" if vsx else ""), gap=False)
        rows, vhead = drop_empty_cols(v_show, VIDEO_HEAD)   # «Rango» solo si algún formato lo usa
        print_rows(rows, ls.v_flags, vhead)
    if ls.auto_n:
        print(paint(f"{ls.auto_n:>3}", "orange", True) + "  " + paint(ls.auto_line, "gray"))
    print()
    more = bool(asx or vsx)
    hint("n.º · b ★ mejor · " + ("m más · " if more else "") + "q salir")
    return more


def _ci_ask(run, ls):
    """3) Elegir. Devuelve (código de salida, None) si se sale (q, Ctrl-C) o (None, (kind, fmt, raw, use_auto))."""
    use_auto = run.use_auto
    full0 = bool(getattr(run, "show_full", False))                         # v=more (atajo): se abre ya la lista completa
    back = scene_list_enter("Ver todos" if full0 else "Elige un formato") if SCENE["on"] else None   # 0.9.5: la escena cede
    top = scene_list_status(ls, full0) if back is not None else None
    pal = _scene_palette() if back is not None else None                  # números, flechas y marcas con el color del sitio
    try:
        return _ci_ask_loop(run, ls, use_auto, full0, top, back)
    finally:
        if pal is not None:
            PALETTE["orange"] = pal


def _scene_palette():
    """Pone el color del sitio como «orange» (números, flechas ▸, marca de predeterminada) y devuelve el original."""
    old = PALETTE["orange"]
    with quiet("_scene_palette"):
        PALETTE["orange"] = (mix(SCENE["a"], SCENE["b"], 0.35), old[1])
    return old


def scene_list_status(ls, full):
    """El estado gris bajo el título de la lista en la escena."""
    n = len(ls.a_rows) + len(ls.v_rows)
    return f"Ver todos · {n} formatos" if full else "Elige un formato"


def _ci_ask_loop(run, ls, use_auto, full0, top, back):
    choices, auto_n = ls.choices, ls.auto_n
    hidden = _ci_show_list(ls, full0, top)
    cur = PROMPT
    while True:
        try:
            typed = ask_line(cur)
            raw = typed.strip().lower()
        except (EOFError, KeyboardInterrupt):
            return 1, None
        if raw == "q":
            return 0, None
        if raw == "":
            cur = retry_prompt(cur, typed)          # Enter vacío / Enter fantasma: sin línea nueva
            continue
        if raw == "m" and hidden and ls.can_more:
            if top is not None:
                top = scene_list_status(ls, True)
            hidden = _ci_show_list(ls, True, top)
            cur = PROMPT
            continue
        if raw == "b":
            kind, fmt = auto_best(run.audios, run.videos, run.orig_ids, run.can_merge)
            break
        if raw.isdecimal() and int(raw) in choices:
            kind, fmt = choices[int(raw)]
            use_auto = bool(auto_n and int(raw) == auto_n)
            break
        cur = retry_prompt(cur, typed, bad_prompt(f"1-{len(choices)}, b" + (", m" if hidden else "") + " o q"),
                           f"Opción inválida: escribe un número del 1 al {len(choices)}, b"
                           + (", m" if hidden else "") + " o q.")
    scene_list_leave(run, back)             # 0.9.5: la escena vuelve a abrirse desde el centro (sin escena no hace nada)
    return None, (kind, fmt, raw, use_auto)


def _choose_interactive(run):
    """[M2] 2)"""
    ls = _ci_rows(run)
    code, pick = _ci_ask(run, ls)
    if pick is None:
        return code
    run.kind, run.fmt, run.raw, run.use_auto = pick
    return None


def _m_choose(run):
    """[M2] 2-3) Con --shortcutpick el atajo ya eligió (resolución/fps o solo audio): se salta la lista."""
    scene_status("Eligiendo formato", frac=0.05)
    audios, videos, spick = run.audios, run.videos, run.spick
    auto = ytdlp_auto_pick(run.info, audios, videos)         # (video, audio|None) que elegiría yt-dlp
    run.auto = auto
    run.use_auto = False
    pre = (shortcut_resolve_video(spick, audios, videos, run.tracks, run.orig_ids, run.can_merge, auto)
           if spick else None)
    if pre is not None and spick and str(spick.get("v") or "").lower() == "ytdlp":
        run.use_auto = True
    run.show_full = bool(spick) and str(spick.get("v") or "").strip().lower() in SC_MORE_IDS   # «Ver todos» del atajo
    if spick and spick.get("v") and pre is None and not run.show_full:      # 1.5.3: no se cae a la lista: mismo formato con otra escritura o el mejor compatible
        item = None
        with quiet("shortcut_remembered"):
            item = shortcut_remembered(video_key(run.info), spick.get("v"))
        fb = shortcut_fallback_video(str(spick.get("v")), audios, videos, run.orig_ids, run.can_merge, item)
        dbg("atajo", {"v": spick.get("v"), "guardado": item, "respaldo": fb[2] if fb else None})
        if fb is not None:
            pre = (fb[0], fb[1])
            m_warn("El formato del atajo ya no está: se usa " + {"mismo id": "el mismo con otro id.", "mismo número": "el mismo con otro id.",
                   "misma calidad": "la misma calidad (otro id).", "calidad más parecida": "la calidad más parecida."}.get(fb[2], "el mejor compatible."))
    if pre is not None:
        run.kind, run.fmt = pre
        run.raw = "atajo"
    else:
        dbg("lista", {"atajo": bool(spick), "v": (spick or {}).get("v"), "ver_todos": run.show_full})      # 1.5.3: por qué se abre la lista
        rc = _choose_interactive(run)
        if rc is not None:
            return rc

    dbg("elegido", {"entrada": run.raw, "tipo": run.kind, "formato": pick(run.fmt, FMT_KEYS)})
    scene_shape(run.fmt, run.info)
    roast_choice(run.kind, run.fmt)
    return None


def _chosen_text(kind, fmt):
    """Texto de «Elegido»: resolución, contenedor, códec y rango (video) o idioma, códec y bitrate (audio)."""
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
        return " · ".join(bits)
    bits = [str(fmt.get("ext") or "?"),
            acodec_short(fmt),
            f"{abr_of(fmt):.0f}k"]
    lang = fmt.get("language")
    if lang:
        bits.insert(0, str(lang))
    return "audio · " + " · ".join(bits)


def _m_summary(run):
    """[M3] Resumen limpio tras la lista (evita teclado/prompt bajo decenas de filas)."""
    clear_screen()
    show_title(run.title)
    run.elegido = _chosen_text(run.kind, run.fmt)
    return None


def _m_tracks(run):
    """[M4] 4) Armar la selección de pistas (audio principal y extras) y el contenedor de salida."""
    kind, fmt, audios, tracks = run.kind, run.fmt, run.audios, run.tracks
    auto, use_auto, spick = run.auto, run.use_auto, run.spick
    fmt_id, merge_ext = fmt["format_id"], None
    selected, audio_line = [], ""
    if kind == "v" and not has(fmt.get("acodec")):
        if not audios:
            m_warn("No hay audio disponible; se descargará solo el video.")
        elif not run.can_merge:
            m_warn("Este video no trae audio y no hay ffmpeg para unirlos.")
            m_info("Se descargará solo el video.")
        else:
            primary = next((t for t in tracks if t["original"]), tracks[0])
            auto_t = (next((t for t in tracks if str(t["fmt"].get("format_id")) == str(auto[1].get("format_id"))), None)
                      if use_auto and auto and auto[1] else None)
            if auto_t is not None:                 # «yt-dlp auto» lleva el audio que eligió yt-dlp, sin menús
                primary = auto_t
                selected = [primary]
            elif run.multi_lang and spick:
                primary, selected = shortcut_tracks(spick, tracks, primary)      # elegidas en el atajo
            elif run.multi_lang:
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
    elif kind == "v" and run.multi_lang:
        audio_line = "Audio: incluido; no admite pistas adicionales"

    m_block("Elegido", [run.elegido] + ([audio_line] if audio_line else []))
    run.fmt_id, run.merge_ext, run.selected = fmt_id, merge_ext, selected
    return None


def _m_convert_reuse(run):
    """[M4] 4b) Si el resultado no es nativo en Apple, ofrecer convertirlo; 4c) ¿ya está descargado así?"""
    kind, fmt, fmt_id, selected = run.kind, run.fmt, run.fmt_id, run.selected
    index, key = run.index, run.key
    # 4b) Si el resultado no es nativo en Apple, ofrecer convertirlo
    plan = apple_plan(kind, fmt, selected, run.merge_ext)
    dbg("selección", {"fmt_id": fmt_id, "merge_ext": run.merge_ext,
                      "pistas": [t["fmt"].get("format_id") for t in selected]})
    dbg("plan Apple", plan if plan else "no hace falta (ya es compatible)")
    if plan and run.use_auto:
        m_info("yt-dlp auto: se descarga tal cual, sin convertir.")
        plan = None                       # la opción de yt-dlp no pregunta ni convierte
    elif plan:
        plan = ask_apple_convert(plan, run.can_merge, guess_duration(run.info, fmt), fmt)
        dbg("conversión", "aceptada" if plan else "rechazada / no disponible")
    run.plan = plan
    run.conv_state = {}

    # 4c) ¿Ya está descargado con estos mismos parámetros / streams? (se busca en TODO lo que bajaste de
    # este video, no solo en la última descarga; lo que sea otra elección se conserva y se descarga aparte)
    hist = history_for(key, index)
    old_file, old_entry = history_match(hist, fmt_id, conv_mode({}, plan or {}))
    run.old_file = old_file
    if hist and not old_file:
        m_info("Ya tienes este video con otra calidad o audio: se guarda con el nombre original.")
    if old_file and reuse_downloaded(old_file, old_entry, index, key, run.title, run.info, kind,
                                     fmt, fmt_id, selected, run.orig_ids, plan):
        roast_done(len(index) - 1, reused=True)
        return 0
    return None


def _stream_specs(fmt, fmt_id, formats):
    """Especificaciones de streams a (posible) reutilizar desde caché y a reanudar: ([(id, ext)], [(id, ext, tamaño)])."""
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
    return format_specs, resume_specs


def _ytdlp_options(run):
    """Opciones de yt-dlp para la descarga (con DLPY_DEBUG: yt-dlp tal cual, verbose y progreso nativo)."""
    ui = run.ui
    opts = {
        **run.base_opts,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "format": run.fmt_id,
        "outtmpl": os.path.join(run.work_dir.replace("%", "%%"), run.base.replace("%", "%%") + ".%(ext)s"),
        "continuedl": True,
        # False = no sobrescribir: si el intermedio ya está completo (caché), se salta
        "overwrites": False,
        "noprogress": True,
        "consoletitle": False,
        "progress_hooks": [ui.hook],
        "postprocessor_hooks": [ui.pp_hook],
    }
    if run.merge_ext:
        opts["merge_output_format"] = run.merge_ext
        opts["allow_multiple_audio_streams"] = True
    if DEBUG:
        # yt-dlp tal cual (verbose y progreso nativo), como fuera del script
        opts.update({"quiet": False, "no_warnings": False, "verbose": True,
                     "noprogress": False})
        dbg("opciones yt-dlp", {k: v for k, v in opts.items()
                                if k not in ("progress_hooks", "postprocessor_hooks")})
    return opts


def _m_workspace(run):
    """[M5] 5) Nombre de archivo, carpeta de trabajo (reanudable), caché de streams, panel y opciones de yt-dlp."""
    base = safe_name(run.title)           # siempre el nombre original del video (sin « (nuevo)», «[id]» ni «-2»)

    # Especificaciones de streams a (posible) reutilizar desde caché
    format_specs, resume_specs = _stream_specs(run.fmt, run.fmt_id, run.formats)

    # Trabajo temporal en internal (carpeta estable para poder reanudar);
    # el resultado final va a dlpy_files
    work_dir, base, resumed, discarded = prepare_resume_dir(resume_key(run.key, resume_specs), base)

    dbg("nombre / trabajo", {"base": base, "work_dir": work_dir, "specs": format_specs,
                             "reanudado": resumed})
    reused = seed_work_from_cache(work_dir, base, run.key, format_specs)
    remember_resume(work_dir, run)        # 0.7.8: enlace y elección para el menú de pendientes
    run.start_bytes = resume_data_bytes(work_dir)
    dbg("caché de streams", {"reutilizados": reused})
    if reused:
        m_info(f"Caché de streams: {reused} archivo(s) reutilizado(s) (< 24 h)")

    STREAM_KINDS.clear()                  # 1.3.6: el tipo de cada stream sale de los formatos ya analizados (no del hook)
    for _f in (run.formats or []):
        _k = format_kinds(_f)
        if _k:
            STREAM_KINDS[str(_f.get("format_id"))] = _k
    ui = DownloadUI(vkey=run.key, resumed=bool(resumed))
    ui.total = len(format_specs)
    run.ui, run.base, run.work_dir, run.resumed, run.discarded = ui, base, work_dir, resumed, discarded
    run.opts = _ytdlp_options(run)
    return None


def _m_download(run):
    """[M6] Descarga con yt-dlp (progreso, conversión y reanudación). Deja la ruta en run.final."""
    ui, work_dir, plan, conv_state = run.ui, run.work_dir, run.plan, run.conv_state
    selected, merge_ext = run.selected, run.merge_ext
    if QUIET["on"]:
        quiet_set(False)                  # 0.8.1: desde aquí vuelven las animaciones (la intro y la descarga)
    try:
        site_theme_apply(run)             # 0.7.8: la pantalla de descarga usa los colores del sitio
        if not getattr(run, "site_shown", False):     # con --shortcutpick la intro ya salió al abrir
            site_intro(run)               # intro de 1 s: la etiqueta queda lista para el banner de abajo
    except KeyboardInterrupt:
        raise
    except Exception as _ign:
        ignore("site_intro", _ign)
    clear_screen()
    hide_keyboard()
    settle_terminal()                     # espera a que el terminal tome su alto nuevo ANTES de pintar el panel
    file_title(run.base)
    if run.resumed:
        m_ok(f"Reanudando: {human_size(run.resumed)} ya descargados")
    elif run.discarded:
        m_warn("Parcial descartado tras fallos repetidos; se empieza de cero.")
    ui.begin()
    final = None
    try:
        with run.yt_dlp.YoutubeDL(run.opts) as ydl:
            if merge_ext and selected:
                ydl.add_post_processor(
                    make_track_pp([track_label(t) for t in selected], ui.bar),
                    when="post_process")
            if plan:
                ydl.add_post_processor(make_apple_pp(plan, conv_state, ui.bar),
                                       when="post_process")
            res = run_download(ydl, run.yt_dlp, run.info, run.link, run.fmt_id)
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
        saved = keep_for_resume(work_dir, run.start_bytes, failed=False)
        m_err("Descarga cancelada.")
        if saved:
            m_info(f"Avance guardado ({human_size(saved)}): repite el mismo enlace y formato para reanudar.")
        roast_cancel()
        return 1
    except Exception as e:
        ui.abort()
        saved = keep_for_resume(work_dir, run.start_bytes, failed=True)
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
    run.final = final
    return None


def _m_store(run):
    """[M7] Mover el resultado terminado a dlpy_files (solo procesos completados) y sustituir el anterior."""
    final, work_dir, old_file = run.final, run.work_dir, run.old_file
    dest_name = os.path.basename(final)
    dest_path = os.path.join(FILES_DIR, dest_name)
    replacing = bool(old_file) or (os.path.isfile(dest_path) and os.path.abspath(final) != os.path.abspath(dest_path))
    scene_status("Sustituyendo" if replacing else "Guardando", frac=0.95)      # 1.4.2: si hay uno que se sustituye, el viejo se deshace en el nuevo
    if os.path.abspath(final) != os.path.abspath(dest_path):
        try:
            if os.path.isfile(dest_path):                     # mismo nombre: el nuevo reemplaza al anterior
                os.remove(dest_path)
            drop_deliveries(dest_name)                        # y su entrega anterior (enlace al archivo viejo) también
            move_file(final, dest_path)
            final = dest_path
        except Exception as e:
            cleanup_work(work_dir)
            m_err(f"No se pudo guardar el archivo en {FILES_DIR}: {e}")
            return 1

    cleanup_work(work_dir)
    dbg("movido a", final)

    # Reemplazar el archivo anterior y quitar el sufijo temporal
    if old_file and os.path.abspath(old_file) != os.path.abspath(final):
        with quiet("main", OSError):
            os.remove(old_file)
        drop_deliveries(os.path.basename(old_file))
        _root, _ext = os.path.splitext(os.path.basename(final))      # solo el sufijo final del nombre, no el título
        clean = os.path.join(os.path.dirname(final), re.sub(r" \(nuevo\)(?=(?:-\d+)?$)", "", _root) + _ext)
        if clean != final and not os.path.exists(clean):
            os.replace(final, clean)
            final = clean
    run.final = final
    scene_hold(SCENE_SAVE_SECS)           # 1.1.3: el archivo entra en dlpy_files y se alcanza a ver (✓) antes de seguir
    return None


def _m_register(run):
    """[M8] 6) Registrar (con datos técnicos) y enviar el archivo."""
    final, key, title = run.final, run.key, run.title
    index = load_json(INDEX_FILE)         # se relee: durante la descarga el índice pudo cambiar (otra ejecución)
    index[key] = {"file": os.path.basename(final), "title": title,
                  "date": int(time.time()), "version": VERSION,
                  "meta": build_meta(run.kind, run.fmt, run.fmt_id, run.selected, run.orig_ids, final,
                                    run.conv_state or None, run.info)}
    dbg("índice", index[key])
    try:
        save_json(INDEX_FILE, index)
    except Exception as e:
        m_warn(f"No se pudo guardar el índice: {e}")
    history_add(key, index[key])          # downloads.json guarda cada descarga, no solo la última

    result_card(final, title, index[key]["meta"], run.info.get("duration"))
    roast_done(len(index) - 1)
    deliver(final, title)
    return 0


RESUME_STEPS = (_m_link, _m_analyze, _m_choose, _m_summary, _m_tracks, _m_convert_reuse, _m_workspace, _m_download,
                _m_store, _m_register)
MAIN_STEPS = (_m_modes, _m_prepare, _m_update, _m_resume, _m_link, _m_analyze, _m_choose, _m_summary, _m_tracks,
              _m_convert_reuse, _m_workspace, _m_download, _m_store, _m_register)


def main():
    """Ejecuta los pasos de MAIN_STEPS en orden; el primero que devuelve un código (no None) termina main()."""
    run = _Run()
    try:
        for step in MAIN_STEPS:
            rc = step(run)
            if rc is not None:
                return rc
        return 0
    finally:
        scene_error_end()                   # 1.0.8: un error se muestra en D L P Y antes de cerrar la escena
        scene_stop(clear=True)              # 0.9.3: si la escena sigue activa (error, Ctrl-C, sin entrega) se quita y la consola vuelve a lo normal


if __name__ == "__main__":
    sys.exit(run_guarded(main))
