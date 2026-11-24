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
# Respetar siempre el motor de idiomas de la UX ([UX4b]: ux_text / ux_pick / ux_chip y los catálogos I18N / I18N_UX / I18N_WELCOME): toda animación nueva (o cambiada) que lleve texto debe pedírselo al motor, es decir, el texto que se ve es el valor del idioma activo (nunca un literal en español ni en inglés), traducido ANTES de medirlo y medido por su ancho real; al añadir un texto nuevo, añadir su clave en español y sus traducciones al catálogo (_UX_ROWS / I18N) y su prueba en el selftest.
# ==== FIN REGLAS ====

# ==== CHANGELOG ====
#
# ## 2.1.3
#
# - Atajo config más amigable: etiquetas en español agrupadas (Interfaz, Animación, Descargas…),
#   `label_map` (etiqueta → nombre técnico) y detalle con el nombre DLPY_*. El atajo usa el mapa
#   en lugar de partir la etiqueta por el primer espacio.
#
# ## 2.1.2
#
# - Fix atajo + DEBUG: con DLPY_DEBUG_LOGGING=1 el JSON de --atajo/--scm/--scb/--shortcutpick
#   ya no se contamina. `dbg()` no escribe en modos JSON ni sin TTY; el tee del log de debug
#   no se activa en esos modos; el mensaje «[debug] Log guardado: …» no va a stdout.
# - Fix: `--atajo` / `--shortcut` no toman el bloqueo de instancia (GUARD_SKIP + instance_guard).
#   Un instance.json residual ya no hace que el atajo reciba error en vez de JSON.
#
# ## 2.1.1
#
# - (interno) primeros intentos del fix de debug→stdout; supersedido por 2.1.2.
#
# ## 2.1.0
#
# - Atajo: el menú principal ya no es estático. `python dlpy.py --atajo` (alias `--shortcut`) entrega en un JSON todo lo que el atajo necesita: textos del menú, idiomas y las 40 opciones de --config con su etiqueta, detalle y elecciones. El atajo elige de listas (Choose from List) en vez de un menú fijo: si cambia un texto en el py, el atajo lo muestra sin tocar el archivo del atajo.
# - Atajo multi idioma: todos los textos del atajo pasan por el motor (t_display) con msgid español canónico en I18N_ATAJO; con paquete, el atajo entero sale en el idioma activo (menú, config, sistema, errores); sin paquete, cae al español. El menú de actualizar el script desde el portapapeles queda en español (es la vía de rescate cuando el py instalado es viejo).
# - Atajo: config sin terminal. Nueva sección «Configurar variables» en el menú principal: lista las opciones con marca (● guardada · ✗ inválida · ○ por omisión), muestra descripción, valor guardado, por omisión y nombre anterior, y deja cambiar (lista de valores o escribir), borrar una o borrar todas, guardando con --config. Si el valor es inválido, la lista lo marca ✗ y en ejecución se usa el predeterminado.
# - Atajo: el cambio de idioma ya no usa el alias viejo: guarda con --config DLPY_LANGUAGE=código (antes DLPY_LANG=, alias). La lista de idiomas sale del mismo --atajo (ya no llama a --idiomas).
# - Atajo: nueva sección «Sistema / Diagnóstico» con Sistema, Perfil y Versiones (esta última abre el terminal, porque es interactiva). «Adiccional» (typo del atajo) pasa a «Adicional».
# - Atajo: si el dlpy.py instalado no trae --atajo, el atajo lo dice y ofrece bajar la última versión desde GitHub en vez de mostrar menús vacíos.
# - Selftest: atajo_selftest() comprueba --atajo (textos no vacíos, etiquetas únicas, mapas = etiquetas, config cubre CONFIG_OPTIONS, choice_map = choice_labels, idioma con ask/auto).
# - I18N_ATAJO: nueva tabla con los msgid del atajo (como I18N_CONFIG); cuando los catálogos .mo se regeneren con esos msgid, el atajo se traducirá; hasta entonces, cae al español.
#
# ==== FIN CHANGELOG ==== 
VERSION = "2.1.3"

# Índice de secciones (cada una empieza con una cabecera «# ──── Título ────»; busca el título):
#   Variables DLPY_* recordadas · Plataforma · Rutas · Compatibilidad nativa Apple · Interfaz · Terminal:
#   ancho y texto · Mensajes y debug · Escena continua de --shortcutpick · Pantalla: banner,
#   títulos y listas · Barras y paneles de progreso · Terminal: teclado y cuenta regresiva · Utilidades ·
#   Formatos y pistas: etiquetas y selección · Post-proceso: pista predeterminada · Compatibilidad Apple:
#   conversión opcional · Bits, HDR y sondeo del video · Ya descargado: reutilizar o convertir · JSON /
#   índice · Enlace y portapapeles · Dependencias · Actualizaciones (Releases de GitHub) · YouTube: runtime de
#   JavaScript + yt-dlp-ejs · Rechazos recordados · Changelog · Limpieza de almacenamiento ·
#   Control de versión · Releases de GitHub
#   (listado) · Comparar versiones: huellas y diferencias · Pantalla de
#   versiones (--versions) · Caché de streams (24 h) · Reanudación de descargas (con menú de pendientes) ·
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
#   ÁREA G · MANTENIMIENTO Y VERSIONES: [G1] Changelog, [G2] Limpieza de almacenamiento, [G3] Control de versión, [G5] Releases de GitHub, [G6] Comparar versiones, [G8] Pantalla de versiones (--ver
#   ÁREA H · CACHÉ Y REANUDACIÓN: [H2] Caché de streams (24 h), [H3] Reanudación de descargas y menú de pendientes, [H4] Limpieza de la carpeta inter
#   ÁREA I · ENTREGA Y ANÁLISIS: [I1] Entrega del archivo (Atajos), [I2] Atajo de iOS (--2shortcuts), [I3] Análisis tolerante (equivale, [I4] Error «no eres un bot»
#   ÁREA J · MODO ATAJO: [J1] Modo atajo (--scm / --scb)
#   ÁREA K · AUTOPRUEBA Y SISTEMA: [K1] Autoprueba, [K2] Funciones disponibles según 
#   ÁREA L · PRINCIPAL: [L1] Principal
#   ÁREA UX · ESCENA DE SHORTCUTMODE (animaciones avanzadas; va entre [B2] y [B4]): [UX1] Sitios populares, [UX2] Escena continua, [UX3] Lista «Ver todos», [UX4] Puente UX (funciones ux_*)
#   ÁREA UIM · INTERFAZ SIN SHORTCUTMODE: [B4] Pantalla, [B5] Barras y paneles, [B6] Terminal (teclado y cuenta regresiva); solo habla con la escena por el puente [UX4]
#   main(): [M0a] modos especiales · [M0b] preparación · [M0c] actualización y dependencias · [M1] enlace y análisis ·
#           [M2] lista y elección · [M3] resumen · [M4] pistas, conversión y ya descargado · [M5] nombre y trabajo ·
#           [M6] descarga con yt-dlp · [M7] mover el resultado · [M8] registrar y entregar
#   selftest(): [T0]…[T27] (cada una antes de su grupo de pruebas; cada grupo es una función _st_t*; main(): una función _m_* por paso)

import atexit
import math
import os
import re
import glob
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
import gettext
import io
import string
import struct

BOOT_T0 = time.time()                  # 1.2.2: lo primero tras los imports: --scm cuenta su tope de tiempo desde aquí

# ╔════════════════════════════════════════════════════════════════════════════════╗
# ║ ÁREA A · NÚCLEO — entorno, plataforma, rutas, compatibilidad Apple, interfaz   ║
# ╚════════════════════════════════════════════════════════════════════════════════╝
# ─────────────────────── [A1] Variables DLPY_* recordadas ───────────────────────
# 1.3.0: la configuración vive en dlpy_files, fuera de .dlpy_internal (1.6.5: con DLPY_HIDE_SCRIPT_FILES=1 es «.dlpy_config.json»)
CONFIG_NAME = "dlpy_config.json"
# 1.6.5: nombre SIN punto de la carpeta interna; INTERNAL_NAME (más abajo) es este, con punto si DLPY_HIDE_SCRIPT_FILES=1
INTERNAL_BASE = "dlpy_internal"
# 1.6.5: 1 = los archivos del script van ocultos (con punto) · 0 (predeterminado desde 1.6.6) = visibles
HIDE_FILES_KEY = "DLPY_HIDE_SCRIPT_FILES"

# 2.0.9: renombre de config por uso real. CONFIG_ALIASES = nombre viejo -> nombre canónico nuevo. El viejo sigue valiendo
# (alias): se migra a canónico al leer disco/entorno y el canónico manda si hay los dos. Reglas de nombre (12-factor /
# convenciones de variables de entorno): SCREAMING_SNAKE_CASE, prefijo por subsistema (DLPY_SCENE_, DLPY_CLEAR_,
# DLPY_SHORTCUT_, DLPY_UPDATE_, DLPY_ANALYZE_), nombre positivo para booleanos (…_ENABLED) y unidad en el nombre
# para números (…_SECS, …_MB, …_COUNT, …_COLS). Un nombre debe decir qué hace y sobre qué, no solo el tema.
CONFIG_ALIASES = {
    "DLPY_DEBUG": "DLPY_DEBUG_LOGGING",
    "DLPY_LOG_KEEP": "DLPY_DEBUG_LOG_KEEP_COUNT",
    "DLPY_ROWS": "DLPY_LIST_VISIBLE_ROWS",
    "DLPY_LINES": "DLPY_UI_LINES",
    "DLPY_WIDTH": "DLPY_TERMINAL_WIDTH_COLS",
    "DLPY_COLOR": "DLPY_COLOR_TRUECOLOR",
    "DLPY_ANIM": "DLPY_ANIMATIONS_ENABLED",
    "DLPY_BAR_CLASSIC": "DLPY_PROGRESS_BAR_CLASSIC",
    "DLPY_SITE_ANIM": "DLPY_ANALYZE_ANIMATION_ENABLED",
    "DLPY_PIP_SCENE": "DLPY_PIP_USES_SCENE",
    "DLPY_GLITCH": "DLPY_GLITCH_EFFECT_ENABLED",
    "DLPY_CALM": "DLPY_TEXT_CALM_MODE",
    "DLPY_UX": "DLPY_SCENE_RHYTHM",
    "DLPY_ANALYZE_TTL": "DLPY_ANALYZE_RESULT_TTL_SECS",
    "DLPY_LOOP": "DLPY_ANIMATION_LOOP_SECS",
    "DLPY_CONVERT_ANIM": "DLPY_CONVERT_LIGHT_ANIMATION",
    "DLPY_CONVERT_QUALITY": "DLPY_CONVERT_PRESET",
    "DLPY_HIDE": "DLPY_HIDE_SCRIPT_FILES",
    "DLPY_CLEAR_HISTORY": "DLPY_CLEAR_PURGE_SCROLLBACK",
    "DLPY_CLEAR_BOOT": "DLPY_CLEAR_FIRST_MODE",
    "DLPY_CLEAR": "DLPY_CLEAR_MODE",
    "DLPY_OUTRO": "DLPY_SCENE_OUTRO_ENABLED",
    "DLPY_TOPBAR": "DLPY_TOP_BAR_FIELDS",
    "DLPY_BOTTOMBAR": "DLPY_BOTTOM_BAR_FIELDS",
    "DLPY_VIEW": "DLPY_FINISH_DELIVERY_MODE",
    "DLPY_WATCHDOG": "DLPY_SINGLE_INSTANCE_WATCHDOG",
    "DLPY_SAFE_LIST": "DLPY_SHORTCUT_DIRECT_LIST_MODE",
    "DLPY_CLIPBOARD": "DLPY_CLIPBOARD_READ_LINK_ENABLED",
    "DLPY_LANG": "DLPY_LANGUAGE",
    "DLPY_LANG_IDS": "DLPY_TRANSLATION_DEBUG_MODE",
    "DLPY_UPDATES": "DLPY_UPDATE_CHECK_INTERVAL",
    "DLPY_REPO": "DLPY_UPDATE_REPO",
    "DLPY_STORAGE_MB": "DLPY_STORAGE_LIMIT_MB",
    "DLPY_TIMEOUT_SC": "DLPY_SHORTCUT_ANALYZE_TIMEOUT_SECS",
    "DLPY_TIMEOUT_SCM": "DLPY_SHORTCUT_MODE_TIMEOUT_SECS",
    "DLPY_TIMEOUT_HARD": "DLPY_SHORTCUT_MODE_HARD_TIMEOUT_SECS",
    "DLPY_FRAGMENTS": "DLPY_CONCURRENT_FRAGMENTS",
    "DLPY_SUBS": "DLPY_SUBTITLE_LANGS",
    "DLPY_TAGS": "DLPY_MEDIA_TAGS_ENABLED",
    "DLPY_YTDLP_ARGS": "DLPY_YTDLP_EXTRA_ARGS",
    "DLPY_DEBUGLOG": "DLPY_DEBUG_LOG_FILE_ENABLED",
    "DLPY_EARLYCLEAR": "DLPY_CLEAR_ON_STARTUP_ENABLED",
    "DLPY_NATIVECLEAR": "DLPY_CLEAR_USE_NATIVE",
    "DLPY_LOCK": "DLPY_INPUT_LOCK_ENABLED",
    "DLPY_PROBE": "DLPY_PROBE_TERMINAL_WIDTH_ENABLED",
    "DLPY_CONSERVE": "DLPY_KEEP_DOWNLOADS_OVER_LIMIT",
    "DLPY_SCM_SAVE": "DLPY_SHORTCUT_SAVE_ANALYSIS_JSON",
    "DLPY_SELFTEST_DIR": "DLPY_SELFTEST_MODULES_DIR",
    "DLPY_SELFTEST_FILE": "DLPY_SELFTEST_MODULE_FILE",
    "DLPY_LANG_DIR": "DLPY_LANG_PACKS_DIR",
    "DLPY_FORGET": "DLPY_IGNORE_SAVED_CONFIG",
    "DLPY_NOVERIFY": "DLPY_SKIP_SHA_VERIFY",
}
# 2.0.9: alias heredados cuyo VALOR hay que convertir (no basta con cambiar la clave). DLPY_NO_UPDATE (presencia = nunca)
# -> DLPY_UPDATE_CHECK_INTERVAL=0 · DLPY_CHECK_HOURS (horas) -> DLPY_UPDATE_CHECK_INTERVAL=<n>h (el nuevo número solo es
# días) · DLPY_SCENE_MODE (loop -> wait, el resto igual) -> DLPY_SCENE_RHYTHM · DLPY_UX_SECS (segundos sueltos, solo
# valían con DLPY_UX=segundos) -> DLPY_SCENE_RHYTHM=<n>. DLPY_SCENE_RAIL no está aquí: era comentario sin lectura,
# sin efecto desde 1.4.5, retirado como opción (ver changelog).
CONFIG_LEGACY_VALUE = {
    "DLPY_NO_UPDATE": "DLPY_UPDATE_CHECK_INTERVAL",
    "DLPY_CHECK_HOURS": "DLPY_UPDATE_CHECK_INTERVAL",
    "DLPY_SCENE_MODE": "DLPY_SCENE_RHYTHM",
    "DLPY_UX_SECS": "DLPY_SCENE_RHYTHM",
}
CONFIG_ALIAS_REVERSE = {}
for _old, _new in CONFIG_ALIASES.items():
    CONFIG_ALIAS_REVERSE.setdefault(_new, _old)


def config_migrate_value(old, value):
    """2.0.9: (clave canónica, valor canónico) para una clave vieja o nueva. None si la vieja no tiene efecto (p. ej. DLPY_NO_UPDATE vacío)."""
    old = str(old or "").strip().upper()
    value = "" if value is None else str(value)
    if old in CONFIG_ALIASES:
        return CONFIG_ALIASES[old], value
    if old == "DLPY_NO_UPDATE":
        return ("DLPY_UPDATE_CHECK_INTERVAL", "0") if value.strip().lower() not in ("", "0", "no", "false") else None
    if old == "DLPY_CHECK_HOURS":
        try:
            hours = float(str(value).strip().replace(",", "."))
        except (TypeError, ValueError):
            return None
        if not math.isfinite(hours) or hours <= 0:
            return None
        return ("DLPY_UPDATE_CHECK_INTERVAL", ("%g" % hours) + "h")
    if old == "DLPY_SCENE_MODE":
        low = value.strip().lower()
        if low == "loop":
            return ("DLPY_SCENE_RHYTHM", "wait")
        if low in ("real", "wait") or re.fullmatch(r"\d+(?:[.,]\d+)?", low or ""):
            return ("DLPY_SCENE_RHYTHM", value.strip())
        return None
    if old == "DLPY_UX_SECS":
        if re.fullmatch(r"\s*\d+(?:[.,]\d+)?\s*", value or ""):
            return ("DLPY_SCENE_RHYTHM", value.strip())
        return None
    return old, value


def _env_lookup(mapping, name, default=None):
    """2.0.9: valor de `name` (canónico o viejo) en `mapping` (os.environ o un dict de entorno). El canónico manda; si solo está el viejo, devuelve su valor migrado."""
    if mapping is None:
        return default
    try:
        get = mapping.get
    except AttributeError:
        return default
    canon = CONFIG_ALIASES.get(str(name or "").strip().upper(), str(name or "").strip().upper())
    # El nombre ya puede ser canónico o viejo: normaliza a canónico para la búsqueda principal.
    if str(name or "").strip().upper() in CONFIG_ALIASES:
        canon = CONFIG_ALIASES[str(name or "").strip().upper()]
    elif str(name or "").strip().upper() in CONFIG_LEGACY_VALUE:
        canon = CONFIG_LEGACY_VALUE[str(name or "").strip().upper()]
    else:
        canon = str(name or "").strip().upper()
    if canon in mapping and str(mapping.get(canon) or "") != "":
        return mapping.get(canon)
    # Viejo 1:1: mismo valor, otra clave.
    for old, new in CONFIG_ALIASES.items():
        if new == canon and old in mapping and str(mapping.get(old) or "") != "":
            return mapping.get(old)
    # Viejo con conversión de valor: solo si el canónico no está.
    for old, new in CONFIG_LEGACY_VALUE.items():
        if new == canon and old in mapping and str(mapping.get(old) or "") != "":
            migrated = config_migrate_value(old, mapping.get(old))
            if migrated is not None:
                return migrated[1]
    # El canónico puede estar presente aunque vacío (p. ej. DLPY_LANGUAGE=""): eso sí cuenta como «puesto» para quien lo lee con default.
    if canon in mapping:
        return mapping.get(canon)
    return default


def env_get(name, default=None):
    """2.0.9: os.environ.get alias-aware (canónico o viejo). Sustituye a os.environ.get(\"DLPY_…\") en lecturas de config."""
    return _env_lookup(os.environ, name, default)


def config_canonical(name):
    """2.0.9: nombre canónico de una opción (viejo, nuevo o sin DLPY_): «lang» / «DLPY_LANG» -> «DLPY_LANGUAGE». None si no es un nombre DLPY_ válido."""
    k = str(name or "").strip().upper().replace("-", "_")
    if not k:
        return None
    if not k.startswith("DLPY_"):
        k = "DLPY_" + k
    if not re.match(r"^DLPY_[A-Z0-9_]+$", k):
        return None
    if k in CONFIG_ALIASES:
        return CONFIG_ALIASES[k]
    if k in CONFIG_LEGACY_VALUE:
        return CONFIG_LEGACY_VALUE[k]
    return k


def config_old_name(canonical):
    """2.0.9: nombre viejo de un canónico (para mostrar «Nombre anterior»), o None si no tenía viejo."""
    return CONFIG_ALIAS_REVERSE.get(str(canonical or "").strip().upper())




def hide_files_parse(raw=None):
    """1.6.5: DLPY_HIDE_SCRIPT_FILES → True (archivos del script ocultos, con punto delante) o False (visibles). 1.6.6: lo vacío o no reconocido = visibles (predeterminado);
    solo 1 · on · yes · true · y · si · hide · hidden · oculto los ocultan."""
    return str(raw if raw is not None else "").strip().lower() in ("1", "on", "yes", "true", "y", "s", "si", "sí", "hide", "hidden", "oculto", "ocultos")


def hidden_name(base, hide=True):
    """1.6.5: `base` con un punto delante si `hide` (lo que empieza por punto no se ve en la app Archivos de iOS); tal cual si no."""
    return "." + base if hide else base
ENV_SKIP = {"DLPY_IGNORE_SAVED_CONFIG", "DLPY_SKIP_SHA_VERIFY", "DLPY_LANG_PACKS_DIR", "DLPY_FORGET", "DLPY_NOVERIFY", "DLPY_LANG_DIR"}  # 2.0.9: canónicos + viejos (nunca se guardan)
# dónde se guardó y por qué falló
ENV_STATE = {"path": None, "error": None}


def _read_env_json(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            out = {}
            for k, v in data.items():
                if not (isinstance(k, str) and isinstance(v, str) and k.startswith("DLPY_")):
                    continue
                # 2.0.9: el disco puede traer nombres viejos: se migran a canónico al leer (el canónico manda si hay los dos).
                migrated = config_migrate_value(k, v)
                if migrated is None:
                    continue
                canon, val = migrated
                if canon in ENV_SKIP or k in ENV_SKIP:
                    continue
                # 2.0.9: el canónico manda si hay los dos (el viejo solo rellena si no hay canónico).
                if k == canon:
                    out[canon] = val
                elif canon not in out:
                    out[canon] = val
            return out
    except (OSError, ValueError):
        pass        # 1.9.4: aquí aún no existe dbg/ignore (se definen más abajo): se queda sin anotar a propósito
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


def persist_env(env=None, path=None):
    """Las DLPY_* definidas se guardan en `path`; las no definidas se recuperan de ahí (en a-Shell las «export»"""
    env = os.environ if env is None else env
    path = path or ENV_FILE
    ENV_STATE["path"], ENV_STATE["error"] = path, None
    try:
        disk = _read_env_json(path)
        forget = str(_env_lookup(env, "DLPY_IGNORE_SAVED_CONFIG", "") or "").strip().lower() not in ("", "0", "no", "false")
        merged = {} if forget else dict(disk)
        # 2.0.9: el entorno puede traer nombres viejos: se migran; el canónico manda si hay los dos.
        canon_env = {}
        for k, v in env.items():
            if not (isinstance(k, str) and k.startswith("DLPY_") and k not in ENV_SKIP):
                continue
            migrated = config_migrate_value(k, v)
            if migrated is None:
                continue
            canon, val = migrated
            if canon in ENV_SKIP:
                continue
            # El canónico directo manda sobre el alias: si ya vino del canónico, no lo pisa un alias.
            if canon in canon_env and k != canon:
                continue
            canon_env[canon] = val
        merged.update(canon_env)
        for k, v in list(canon_env.items()):
            if k not in env:
                env[k] = v
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


def device_label(machine=None):
    """1.6.7: el dispositivo que detecta el script («iPad13,8» → «iPad», «iPhone15,2» → «iPhone», «iPod…» → «iPod»); sin dato claro, «equipo»."""
    m = (machine if machine is not None else machine_name()) or ""
    for name in ("iPhone", "iPad", "iPod"):
        if m.lower().startswith(name.lower()):
            return name
    return "equipo"


def env_file_path(home=None, hide=None):
    """Dónde se guardan las DLPY_*: dlpy_files/dlpy_config.json (1.6.5: o «.dlpy_config.json», según DLPY_HIDE_SCRIPT_FILES). Con `hide` (True/False) devuelve ese nombre;
    sin él busca el que exista (si solo hay uno, ese; si no hay ninguno o hay los dos, el que pida DLPY_HIDE_SCRIPT_FILES del entorno, que por omisión es el visible)."""
    home = home or os.path.expanduser("~")
    folder = os.path.join(home, "Documents", "dlpy_files")
    shown, hidden = os.path.join(folder, CONFIG_NAME), os.path.join(folder, hidden_name(CONFIG_NAME))
    if hide is not None:
        return hidden if hide else shown
    a, b = os.path.isfile(shown), os.path.isfile(hidden)
    if a != b:
        return shown if a else hidden
    return hidden if hide_files_parse(env_get(HIDE_FILES_KEY)) else shown


ENV_FILE = env_file_path()
if not any(a.lstrip("-\u2013\u2014").lower() == "selftest" for a in sys.argv[1:]):
    persist_env(path=ENV_FILE)
# 1.6.5: ya con lo guardado en la configuración (persist_env lo trae al entorno)
HIDE_FILES = hide_files_parse(env_get(HIDE_FILES_KEY))
# carpeta interna dentro de dlpy_files: «.dlpy_internal» (oculta) o «dlpy_internal»
INTERNAL_NAME = hidden_name(INTERNAL_BASE, HIDE_FILES)


# 1.3.0: opciones conocidas (para «--config --opciones»): (nombre, valor por omisión, qué hace). Las de una sola ejecución (DLPY_IGNORE_SAVED_CONFIG,
# DLPY_SKIP_SHA_VERIFY) no se guardan y no salen aquí.
# idioma con que se muestra todo mientras no hay uno elegido (y si la pregunta de idioma se queda sin respuesta)
# 2.0.8: español, único idioma embebido; el resto (incluido el inglés) se baja de GitHub
DEFAULT_LANG = "es"
# 1.7.1: valor predeterminado de DLPY_LANGUAGE: la escena pregunta el idioma (se guarda lo que se elija)
LANG_ASK = "ask"

CONFIG_OPTIONS = (
    ("DLPY_DEBUG_LOGGING", "", "1 = depuración (logs extra y salida verbosa)"),
    ("DLPY_DEBUG_LOG_KEEP_COUNT", "20", "cuántos logs de depuración se conservan"),
    ("DLPY_LIST_VISIBLE_ROWS", "auto", "filas de lista que caben: auto o número"),
    ("DLPY_UI_LINES", "26", "líneas de la interfaz"),
    ("DLPY_TERMINAL_WIDTH_COLS", "auto", "ancho en columnas (mín. 20) o auto"),
    ("DLPY_COLOR_TRUECOLOR", "1", "1 = truecolor · 0 = colores básicos"),
    ("DLPY_ANIMATIONS_ENABLED", "1", "1 = animaciones · 0 = sin animaciones"),
    ("DLPY_PROGRESS_BAR_CLASSIC", "0", "1 = barra clásica █░ · 0 = estilo actual"),
    ("DLPY_ANALYZE_ANIMATION_ENABLED", "1", "1 = animación del análisis del enlace · 0 = no"),
    ("DLPY_PIP_USES_SCENE", "1", "1 = pip puede ceder la escena · 0 = pip escribe al terminal"),
    ("DLPY_GLITCH_EFFECT_ENABLED", "1", "1 = efecto glitch en transiciones · 0 = sin ruido"),
    ("DLPY_TEXT_CALM_MODE", "0", "1 = textos de D L P Y más legibles (menos ruido) · 0 = normal"),
    ("DLPY_SCENE_RHYTHM", "wait", "ritmo de escenas, incluido el análisis del enlace: wait = cada loop entero · real = al ritmo del proceso · número = segundos fijos (0–60). D L P Y no espera"),
    ("DLPY_ANALYZE_RESULT_TTL_SECS", "60", "segundos de validez del resultado del análisis antes de bajar (0 = no reanalizar); evita 403 si wait alarga la espera"),
    ("DLPY_ANIMATION_LOOP_SECS", "1", "segundos del loop de animaciones de proceso y del análisis del enlace (0.2–3); D L P Y no espera"),
    ("DLPY_CONVERT_LIGHT_ANIMATION", "1", "1 = conversión ligera (menos animación) · 0 = conversión animada (no es la calidad)"),
    ("DLPY_CONVERT_PRESET", "fast", "preset de conversión: fast · high · best · prores"),
    ("DLPY_HIDE_SCRIPT_FILES", "0", "0 = archivos del script visibles · 1 = ocultos (con punto). Descargas y papelera siempre visibles"),
    ("DLPY_CLEAR_PURGE_SCROLLBACK", "1", "1 = al limpiar purga el scrollback del terminal · 0 = no"),
    ("DLPY_CLEAR_FIRST_MODE", "reset", "primer borrado al arrancar: reset · auto · home · down · purge-first"),
    ("DLPY_CLEAR_MODE", "auto", "limpieza normal: auto · home · down · purge-first · reset"),
    ("DLPY_SCENE_OUTRO_ENABLED", "1", "1 = cierre de escena hacia el centro · 0 = solo limpia"),
    ("DLPY_TOP_BAR_FIELDS", "0", "franja superior: 0 = oculta · 1 = DTV (todo) · letras D/T/V en el orden que quieras (se ve al descargar; si no cabe, se quitan D y T en ese orden)"),
    ("DLPY_BOTTOM_BAR_FIELDS", "1", "franja inferior (activa por defecto): 0 = oculta · 1 = EAN (todo) · E = errores (✕) · A = advertencias (!) · N = red (⇅, siempre visible: se pone blanco cuando el script conecta a internet); orden configurable (EAN / NAE)"),
    ("DLPY_FINISH_DELIVERY_MODE", "view", "al terminar: view = el comando `view` de a-Shell (predeterminado) · shortcut = se entrega al atajo"),
    ("DLPY_SINGLE_INSTANCE_WATCHDOG", "1", "1 = una sola ejecución a la vez (bloqueo) y vigilante de congelamientos (con DLPY_DEBUG_LOGGING anota dónde se atasca) · 0 = apagado"),
    ("DLPY_SHORTCUT_DIRECT_LIST_MODE", "0", "0 = apagado (predeterminado) · 1 = --scm y --scb listan directo en el script (lista normal, «m» = más) y descargan ahí, sin JSON ni atajo · all = abre ya la lista completa"),
    ("DLPY_CLIPBOARD_READ_LINK_ENABLED", "", "1 = leer enlace del portapapeles"),
    ("DLPY_LANGUAGE", LANG_ASK, "idioma: ask · auto · es · en · pt · fr · de · it · ru · zh · hi · ar · ja · ko · pl (es = único embebido; el resto se baja de GitHub)"),
    ("DLPY_TRANSLATION_DEBUG_MODE", "0", "diagnóstico de traducción: 0 = apagado · mark = colorea el texto traducido · id = muestra solo el msgid original (sin traducción ni catálogos de idioma) · both = id + mark: solo el msgid original, coloreado"),
    ("DLPY_UPDATE_CHECK_INTERVAL", "1w", "comprobar actualizaciones del script y de sus dependencias: cada cuánto, con unidad (30m minutos · 6h horas · 2d días · 1w semanas · daily · weekly) o un número = días · on = cada arranque · 0/off = nunca (predeterminado: 1w = semanal)"),
    ("DLPY_UPDATE_REPO", "ElDelDLpy/DLpy", "repo de GitHub de los Releases"),
    ("DLPY_STORAGE_LIMIT_MB", "1024", "límite de almacenamiento en MB"),
    ("DLPY_SHORTCUT_ANALYZE_TIMEOUT_SECS", "90", "tope del análisis en el atajo (s; 0 = sin tope)"),
    ("DLPY_SHORTCUT_MODE_TIMEOUT_SECS", "5", "tope de --scm (s)"),
    ("DLPY_SHORTCUT_MODE_HARD_TIMEOUT_SECS", "8", "tope duro de --scm desde el arranque (s; 0 = sin tope)"),
    ("DLPY_CONCURRENT_FRAGMENTS", "4", "fragmentos que se bajan a la vez en DASH/HLS (1–16; 1 = uno a uno, lo más suave para a-Shell mini)"),
    ("DLPY_SUBTITLE_LANGS", "0", "subtítulos junto al video: 0 = no · idiomas separados por coma (es,en) · all = todos"),
    ("DLPY_MEDIA_TAGS_ENABLED", "1", "1 = título, artista y carátula en m4a/mp4/mp3 con mutagen (si está instalado) · 0 = no"),
    ("DLPY_YTDLP_EXTRA_ARGS", "", "argumentos extra para yt-dlp"),
)

# ─────────────────────── [A1b] Idioma de la interfaz (1.7.0) ───────────────────────
LANG_CODES = ("es", "en", "pt", "fr", "de", "it", "ru", "zh", "hi", "ar", "ja", "ko", "pl")
LANG_NAMES = {"es": "Español", "en": "English", "pt": "Português", "fr": "Français", "de": "Deutsch", "it": "Italiano", "ru": "русский", "zh": "中文", "hi": "हिन्दी", "ar": "العربية", "ja": "日本語", "ko": "한국어", "pl": "Polski"}
# 2.0.8: nombres en español (metadato, no traducción de UI): lo que ve Atajos cuando necesita el nombre en español
LANG_NAMES_ES = {"es": "Español", "en": "Inglés", "pt": "Portugués", "fr": "Francés", "de": "Alemán", "it": "Italiano", "ru": "Ruso", "zh": "Chino", "hi": "Hindi", "ar": "Árabe", "ja": "Japonés", "ko": "Coreano", "pl": "Polaco"}
# 2.0.8: idiomas con escritura de derecha a izquierda (el terminal muestra el orden lógico; no se espeja el dibujo)
LANG_RTL = frozenset({"ar"})
# 2.0.8: nplurals que debe declarar cada catálogo (polaco y ruso: 3; árabe: 6; resto según su regla). La validación genérica de lang_pack_check ya exige que cada forma exista; esto caza catálogos con cabecera Plural-Forms equivocada.
LANG_PLURALS = {"es": 2, "en": 2, "pt": 2, "fr": 2, "de": 2, "it": 2, "ru": 3, "zh": 1, "hi": 2, "ar": 6, "ja": 1, "ko": 1, "pl": 3}
LANG_ALIASES = {"español": "es", "spanish": "es", "castellano": "es", "english": "en", "inglés": "en", "ingles": "en",
                "português": "pt", "portugues": "pt", "portuguese": "pt", "français": "fr", "frances": "fr", "french": "fr",
                "deutsch": "de", "german": "de", "alemán": "de", "alemao": "de", "italiano": "it", "italian": "it",
                "polaco": "pl", "polish": "pl", "polski": "pl", "polska": "pl", "poland": "pl", "polonais": "pl",
                "es": "es", "en": "en", "pt": "pt", "fr": "fr", "de": "de", "it": "it", "ru": "ru", "zh": "zh", "hi": "hi", "ar": "ar", "ja": "ja", "ko": "ko", "pl": "pl", "ruso": "ru", "rusian": "ru", "russian": "ru", "русский": "ru", "chino": "zh", "chinese": "zh", "mandarín": "zh", "mandarin": "zh", "hindi": "hi", "árabe": "ar", "arabic": "ar", "العربية": "ar", "japonés": "ja", "japanese": "ja", "japan": "ja", "coreano": "ko", "korean": "ko", "한국어": "ko", "日本語": "ja", "हिन्दी": "hi"}
# ─────────────────────── [UX4c] Motor de idiomas: paquetes por idioma (1.9.1) ───────────────────────
# 2.0.8: solo el español (canónico, msgid) viaja dentro del script. Los otros 12 idiomas (incluido el inglés) son catálogos GNU gettext
# (dlpy_lang_<código>.mo) publicados en la carpeta `languages/` de la rama main del repo (2.0.1; antes, un Release aparte). Los paquetes se verifican con el SHA256SUMS
# de esa misma carpeta (una línea «hash  nombre» por catálogo; la revisión del catálogo no depende de VERSION, por lo que puede actualizarse sin publicar otra versión de DLpy.
import http.client as _http_client
# 1.9.3: familias de errores esperables; lo que no encaje aquí ya no se traga en silencio (llega a diagnostic_report / install_diagnostic_hooks).
# red: URLError/HTTPError/timeout/SSL son OSError; JSON o UTF-8 inválidos son ValueError
NET_ERRORS = (OSError, ValueError, EOFError, _http_client.HTTPException)
# respuesta bien formada pero con otra forma de la esperada
PARSE_ERRORS = (KeyError, IndexError, TypeError, AttributeError)
# disco: escritura, JSON no serializable, texto no codificable
DISK_ERRORS = (OSError, ValueError, TypeError)
PACK_FORMAT = 3      # 2.0.8: formato 3 = todos los msgid son español (antes, fragment:/format:/template usaban el inglés como msgid). Un catálogo formato 2 se rechaza y se vuelve a descargar.
PACK_LANGS = ("en", "pt", "fr", "de", "it", "ru", "zh", "hi", "ar", "ja", "ko", "pl")
LANG_BRANCH, LANG_REMOTE_DIR, LANG_SUMS = "main", "languages", "SHA256SUMS"      # 2.0.1: dónde viven los catálogos en el repo (raw.githubusercontent.com)
# 1.9.2: la revisión del catálogo usa check_due/check_mark y respeta DLPY_UPDATE_CHECK_INTERVAL.
PACK_STATE = {"loaded": set(), "tried": set(), "warned": set(), "err": {}, "missing": {}}
_TPL_PACK = {}                        # código → [(plantilla española, traducción del catálogo gettext)]
LANG_TRANSLATIONS = {}                # código → gettext.GNUTranslations (o respaldo español, identidad)


class LangTable(dict):
    """Vista dict compatible con el código existente; carga un catálogo .mo local bajo demanda."""

    def __init__(self, section, data=None):
        dict.__init__(self, data or {})
        self.section = section

    def __missing__(self, code):
        if code in PACK_LANGS and lang_pack_load(code) and dict.__contains__(self, code):
            return dict.__getitem__(self, code)
        raise KeyError(code)

    def get(self, code, default=None):
        try:
            return self[code]
        except KeyError:
            return default

    def __contains__(self, code):
        if not dict.__contains__(self, code) and code in PACK_LANGS:
            lang_pack_load(code)
        return dict.__contains__(self, code)


def lang_pack_dir():
    """Carpeta de catálogos GNU .mo: DLPY_LANG_PACKS_DIR (pruebas) o internal/languages."""
    override = env_get("DLPY_LANG_PACKS_DIR")
    if override:
        return override
    return os.path.join(INTERNAL_DIR, "languages")


def lang_pack_path(code):
    return os.path.join(lang_pack_dir(), "dlpy_lang_%s.mo" % code)


def lang_pack_url(code):
    """URL fija del catálogo en la carpeta languages/ de main (2.0.1); no depende de VERSION ni del listado de Releases."""
    if code not in PACK_LANGS:
        return None
    repo = str(globals().get("UPDATE_REPO") or "ElDelDLpy/DLpy").strip().strip("/")
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
        return None
    return ("https://raw.githubusercontent.com/%s/%s/%s/dlpy_lang_%s.mo" %
            (repo, urllib.parse.quote(LANG_BRANCH, safe=""), LANG_REMOTE_DIR, code))


def lang_pack_sha_url(code):
    """2.0.1: URL del SHA256SUMS de la carpeta (el mismo para todos los idiomas: una sola petición dice cuáles cambiaron)."""
    url = lang_pack_url(code)
    return url.rsplit("/", 1)[0] + "/" + LANG_SUMS if url else None


def _lang_pack_sha_value(raw, name=None):
    """Extrae un SHA-256 de un SHA256SUMS («hash  nombre» por línea) o de un sidecar de un solo hash, en bytes o en texto.
    2.0.1: con `name` se toma la línea de ese archivo y, si el texto trae nombres pero no el pedido, no hay hash (nunca el de otro idioma)."""
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", "replace")
    raw = str(raw or "")
    named = re.findall(r"(?im)^\s*([0-9a-f]{64})\s+\*?(\S+)\s*$", raw)
    if named and name:
        for digest, fname in named:
            if fname.rsplit("/", 1)[-1] == name:
                return digest.lower()
        return None
    match = re.search(r"(?i)\b([0-9a-f]{64})\b", raw)
    return match.group(1).lower() if match else None


def _format_fields(value):
    """Campos de str.format; None indica una plantilla mal formada."""
    fields = []
    try:
        for _literal, field_name, _spec, _conversion in string.Formatter().parse(value):
            if field_name is not None:
                fields.append(str(field_name))
    except (ValueError, TypeError):
        return None
    return sorted(fields)


def lang_pack_check(raw, code):
    """Abre un GNU MO y valida idioma, formato, revisión declarada, UTF-8 y marcadores."""
    try:
        if not isinstance(raw, (bytes, bytearray)) or len(raw) < 28:
            return None
        tr = gettext.GNUTranslations(io.BytesIO(raw))
        info = {str(k).lower(): str(v) for k, v in tr.info().items()}
        if info.get("language", "").lower().split(".")[0].split("_")[0] != code:
            return None
        if info.get("x-dlpy-catalog-format") != str(PACK_FORMAT):
            return None
        # La revisión identifica la edición del catálogo, no la versión de DLpy.
        # Esto permite que un mismo Release de idiomas sirva a varias versiones del script.
        revision = info.get("x-dlpy-catalog-revision", "").strip()
        if not revision or len(revision) > 80 or not re.fullmatch(r"[A-Za-z0-9._+-]+", revision):
            return None
        if "utf-8" not in info.get("content-type", "").lower():
            return None
        plural_header = info.get("plural-forms", "")
        if not re.search(r"\bnplurals\s*=\s*\d+", plural_header) or "plural" not in plural_header:
            return None
        _want_nplurals = LANG_PLURALS.get(code)
        if _want_nplurals is not None:
            _m_npl = re.search(r"\bnplurals\s*=\s*(\d+)", plural_header)
            if not _m_npl or int(_m_npl.group(1)) != _want_nplurals:
                return None
        catalog = getattr(tr, "_catalog", {})
        # Todas las categorías gramaticales que puede producir la regla deben existir.
        # Así gettext nunca cae accidentalmente al msgid español por una forma plural ausente.
        plural_sources = (("noun:files", "archivo"), ("noun:hour", "hora"), ("noun:day", "día"))  # 2.0.8: msgid español también en plurales
        plural_samples = (0, 1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 20, 21, 22, 23, 24, 25, 26, 99, 100, 101, 102, 111, 1000)  # 2.0.8: 12-14 y 22-24 cubren la frontera few/many del polaco y del ruso
        for context, singular in plural_sources:
            base = context + "\x04" + singular
            for number in plural_samples:
                try:
                    index = int(tr.plural(number))
                except Exception:
                    return None
                if (base, index) not in catalog:
                    return None
        # Una entrada con variables distintas se elimina del catálogo: gettext caerá al español.
        # 2.0.8: si la cabecera declara un nplurals distinto del esperado para ese idioma, el catálogo se rechaza entero (un .mo polaco con nplurals=2 traduciría mal 2-4 y 22-24).
        # También se inspeccionan las formas plurales, sin rechazar el idioma por una entrada normal defectuosa.
        bad = []
        for key, val in list(catalog.items()):
            if key == "" or not isinstance(val, str):
                continue
            if isinstance(key, tuple) and len(key) == 2:
                msgid = str(key[0]).split("\x04", 1)[-1]
            elif isinstance(key, str):
                msgid = key.split("\x04", 1)[-1]
            else:
                continue
            src_fields = _format_fields(msgid)
            dst_fields = _format_fields(val)
            if src_fields is None or dst_fields is None or src_fields != dst_fields:
                bad.append(key)
        for key in bad:
            catalog.pop(key, None)
        if bad:
            PACK_STATE["err"][code] = "placeholders:%d" % len(bad)
        return tr
    except (OSError, ValueError, EOFError, UnicodeError, struct.error):
        return None


def lang_pack_read(code):
    """Catálogo .mo local validado contra su .sha256."""
    import hashlib
    path = lang_pack_path(code)
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
        with open(path + ".sha256", "r", encoding="utf-8") as fh:
            expected = _lang_pack_sha_value(fh.read(), os.path.basename(path))
    except OSError:
        return None
    if not expected or hashlib.sha256(raw).hexdigest() != expected:
        PACK_STATE["err"][code] = "sha"
        return None
    tr = lang_pack_check(raw, code)
    if tr is None:
        PACK_STATE["err"][code] = "format"
    return tr


def lang_pack_coverage(tr):
    """1.9.4: claves que el script necesita y el catálogo no trae, en todas las categorías (ui, fragmentos, formatos, nombres, plantillas); antes solo se contaba «ui»."""
    table = lambda t: dict.__getitem__(t, "es")
    required = {"ui\x04" + key for key in set(table(I18N)) | set(table(I18N_WELCOME)) | set(table(I18N_UX))}
    required |= {"fragment:%s\x04%s" % (es, en) for es, en in table(I18N_PHRASES).items()}
    required |= {"format:%s\x04%s" % (key, source) for key, source in table(I18N_FMT).items()}
    required.add("noun\x04equipo")  # 2.0.8: el msgid de noun es el español «equipo», no «device»
    required |= {"template\x04" + es for es in _TPL_ROWS}
    return sorted(required - {key for key in getattr(tr, "_catalog", {}) if isinstance(key, str)})


def lang_pack_apply(code, tr):
    """Instala un catálogo gettext sin tocar builtins; cada clave que falte usa el fallback español (identidad). 2.0.8: todos los msgid son español."""
    tr.add_fallback(_SPANISH_TRANSLATION)
    LANG_TRANSLATIONS[code] = tr
    ui_es = dict.__getitem__(I18N, "es")
    msgs = {key: tr.pgettext("ui", key) for key in ui_es}
    dict.__setitem__(I18N, code, msgs)
    phrases = {}
    for es in dict.__getitem__(I18N_PHRASES, "es"):
        phrases[es] = tr.pgettext("fragment:" + es, es)  # 2.0.8: msgid = fragmento español
    dict.__setitem__(I18N_PHRASES, code, phrases)
    welcome = {key: tr.pgettext("ui", key) for key in dict.__getitem__(I18N_WELCOME, "es")}
    dict.__setitem__(I18N_WELCOME, code, welcome)
    ux = {key: tr.pgettext("ui", key) for key in dict.__getitem__(I18N_UX, "es")}
    dict.__setitem__(I18N_UX, code, ux)
    fmt = {key: tr.pgettext("format:" + key, source) for key, source in dict.__getitem__(I18N_FMT, "es").items()}  # 2.0.8: msgid = plantilla española
    dict.__setitem__(I18N_FMT, code, fmt)
    dict.__setitem__(I18N_DEVICE, code, tr.pgettext("noun", "equipo"))  # 2.0.8: msgid español
    # 2.0.8: los textos de idioma son traducciones, no metadatos: se rellenan desde el mismo catálogo (si el catálogo no los trae, queda el español).
    dict.__setitem__(LANG_SET_TEXT, code, tr.pgettext("ui", "Idioma establecido"))
    dict.__setitem__(LANG_CURRENT_TEXT, code, tr.pgettext("ui", "Idioma actual"))
    dict.__setitem__(LANG_SELECT_TEXT, code, tr.pgettext("ui", "Seleccione idioma"))
    dict.__setitem__(UX_ENTER, code, tr.pgettext("ui", "Enter"))
    _TPL_PACK[code] = [(es, tr.pgettext("template", es)) for es in _TPL_ROWS]
    _TPL_RX.pop(code, None)
    # La cobertura se registra para diagnóstico; las claves ausentes ya quedaron cubiertas por inglés.
    PACK_STATE["missing"][code] = len(lang_pack_coverage(tr))


def _lang_pack_activate(code, tr):
    """Activa un catálogo ya validado y deja coherente el estado de carga."""
    lang_pack_apply(code, tr)
    PACK_STATE["loaded"].add(code)
    PACK_STATE["tried"].add(code)
    return True


def lang_ids_literal():
    """1.9.2: DLPY_TRANSLATION_DEBUG_MODE=id/both muestran el msgid, que es el español del propio py: no hacen falta catálogos (.mo), así que ni se cargan ni se comprueban ni se descargan."""
    return globals().get("LANG_ID_MODE") in ("id", "both")


def lang_pack_load(code):
    """Carga una sola vez por ejecución desde disco; nunca realiza solicitudes de red."""
    if lang_ids_literal():
        return False
    if code in PACK_STATE["loaded"]:
        return True
    if code not in PACK_LANGS or code in PACK_STATE["tried"]:
        return False
    if "FILES_DIR" not in globals() and not env_get("DLPY_LANG_PACKS_DIR"):
        return False
    PACK_STATE["tried"].add(code)
    tr = lang_pack_read(code)
    if tr is None:
        return False
    return _lang_pack_activate(code, tr)


def lang_pack_download(code, timeout=8, sha_raw=None):
    """Descarga el SHA256SUMS de languages/ (o recibe su texto en `sha_raw`) y el .mo; valida hash y catálogo antes de instalarlos.
    1.9.2: solo la petición real del .mo activa la animación D L P Y (el sidecar pequeño no la activa)."""
    import hashlib
    if code not in PACK_LANGS or lang_ids_literal():
        return False
    url = lang_pack_url(code)
    sha_url = lang_pack_sha_url(code)
    if not url or not sha_url:
        PACK_STATE["err"][code] = "release"
        return False
    try:
        if sha_raw is None:
            sha_raw = fresh_bytes(sha_url, timeout, limit=4096)
        expected = _lang_pack_sha_value(sha_raw, "dlpy_lang_%s.mo" % code)
    except NET_ERRORS as _ign:
        ignore("lang_pack_download", _ign)
        PACK_STATE["err"][code] = "red"
        return False
    if not expected:
        PACK_STATE["err"][code] = "sha"
        return False

    scene_started = ux_language_download(code)
    installed = False
    try:
        try:
            raw = fresh_bytes(url, timeout)
        except NET_ERRORS as _ign:
            ignore("lang_pack_download", _ign)
            PACK_STATE["err"][code] = "red"
            return False
        if raw is None:
            PACK_STATE["err"][code] = "red"
            return False
        if hashlib.sha256(raw).hexdigest() != expected:
            PACK_STATE["err"][code] = "sha"
            return False
        if lang_pack_check(raw, code) is None:
            PACK_STATE["err"][code] = "format"
            return False
        path = lang_pack_path(code)
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path + ".tmp", "wb") as fh:
                fh.write(raw)
            with open(path + ".sha256.tmp", "w", encoding="utf-8") as fh:
                fh.write("%s  %s\n" % (expected, os.path.basename(path)))
            os.replace(path + ".tmp", path)
            os.replace(path + ".sha256.tmp", path + ".sha256")
        except OSError as _ign:
            ignore("lang_pack_download", _ign)
            with quiet("lang_pack_download_tmp", OSError):
                os.remove(path + ".tmp")
                os.remove(path + ".sha256.tmp")
            PACK_STATE["err"][code] = "disco"
            return False
        PACK_STATE["tried"].discard(code)
        PACK_STATE["err"].pop(code, None)
        installed = True
        return True
    finally:
        if scene_started:
            try:
                ux_language_done(code, installed)
            except Exception as _ign:
                ignore("ux_language_done", _ign)


def lang_pack_sync(code, timeout=6, force=False):
    """Actualiza el catálogo elegido con el mismo calendario del actualizador (DLPY_UPDATE_CHECK_INTERVAL).
    La firma local permite repetir la comprobación si el paquete falta o cambió; una consulta fallida no consume el intervalo."""
    import hashlib
    if code not in PACK_LANGS or lang_ids_literal():
        return False
    path = lang_pack_path(code)
    local_tr = lang_pack_read(code)
    try:
        with open(path, "rb") as fh:
            local_sha = hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        local_sha = "missing"
    key = "language:" + code

    # --noupdates / DLPY_UPDATE_CHECK_INTERVAL=0 también apaga las peticiones de idioma, pero no la carga local.
    if NO_UPDATES["on"] and not force:
        return _lang_pack_activate(code, local_tr) if local_tr is not None else False
    if not force and not check_due(key, local_sha):
        return _lang_pack_activate(code, local_tr) if local_tr is not None else False

    scene_check_started = ux_language_check(code)
    sha_raw = None
    try:
        sha_url = lang_pack_sha_url(code)
        sha_raw = fresh_bytes(sha_url, timeout, limit=4096) if sha_url else None
    except NET_ERRORS as _ign:
        ignore("lang_pack_sync_sha", _ign)
    remote_sha = _lang_pack_sha_value(sha_raw, "dlpy_lang_%s.mo" % code)
    if not remote_sha:
        PACK_STATE["err"][code] = "red"
        if scene_check_started:
            ux_language_check_done(code, "failed")
        if local_tr is not None:
            _lang_pack_activate(code, local_tr)
            _lang_pack_warning(code, "no se pudo comprobar la actualización; se conserva el paquete local")
            return True
        _lang_pack_warning(code, "no se pudo descargar; se usará español")
        return False

    # Un SHA idéntico confirma que el catálogo local sigue siendo el publicado.
    if local_tr is not None and local_sha == remote_sha:
        check_mark(key, remote_sha)
        PACK_STATE["err"].pop(code, None)
        if scene_check_started:
            ux_language_check_done(code, "current")
        return _lang_pack_activate(code, local_tr)

    # El paquete falta o el repo publicó otro SHA: el actualizador descarga el .mo.
    if scene_check_started:
        ux_language_check_done(code, "changed")
    if lang_pack_download(code, timeout, sha_raw=sha_raw):
        check_mark(key, remote_sha)
        PACK_STATE["loaded"].discard(code)
        PACK_STATE["tried"].discard(code)
        return lang_pack_load(code)

    # La actualización incompleta nunca invalida una copia local previamente validada.
    if local_tr is not None:
        _lang_pack_activate(code, local_tr)
        _lang_pack_warning(code, "falló la descarga de la actualización; se conserva el paquete local")
        return True
    _lang_pack_warning(code, "falló la descarga; se usará español")
    return False


def _lang_pack_warning(code, detail):
    """Registra una única advertencia por idioma y ejecución si el catálogo no se pudo sincronizar."""
    if code in PACK_STATE["warned"]:
        return
    PACK_STATE["warned"].add(code)
    name = LANG_NAMES.get(code, code)
    m_warn(f"Idioma {name}: {detail}.")


def lang_ensure(code=None):
    """Carga el catálogo local antes del resto del flujo; la búsqueda remota queda para update_phase y DLPY_UPDATE_CHECK_INTERVAL."""
    code = code or LANG
    if lang_ids_literal():
        return "es"
    if code not in PACK_LANGS or lang_pack_load(code):
        return code
    if NO_UPDATES["on"]:
        _lang_pack_warning(code, "no hay un paquete local válido y las actualizaciones están desactivadas; se usará español")
    return "es"


def lang_effective(code):
    """Idioma real: paquete local si está validado; si no, español. 1.9.2: con DLPY_TRANSLATION_DEBUG_MODE=id/both siempre «es» (el msgid; sin catálogos)."""
    if lang_ids_literal():
        return "es"
    if code in PACK_LANGS and code not in PACK_STATE["loaded"] and not lang_pack_load(code):
        return "es"
    return code

I18N = LangTable("msgs", {
    # 2.0.8: solo español embebido (identidad: clave = valor). El resto llega en su .mo; la clave que falte cae al español.
    'es': {
        'Preparando': 'Preparando',
        'Preparando descarga': 'Preparando descarga',
        'Guardado': 'Guardado',
        'Guardando': 'Guardando',
        'Sustituyendo': 'Sustituyendo',
        'Finalizando': 'Finalizando',
        'Descargando': 'Descargando',
        'Descargando audio': 'Descargando audio',
        'Descargando video': 'Descargando video',
        'Esperando respuesta': 'Esperando respuesta',
        'Sí': 'Sí',
        'No': 'No',
        'DEBUG activo': 'DEBUG activo',
        'DEBUG desactivado': 'DEBUG desactivado',
        'Sin respuesta': 'Sin respuesta',
        '--cleartest necesita un terminal interactivo.': '--cleartest necesita un terminal interactivo.',
        'Enter = probar ▸': 'Enter = probar ▸',
        'audio': 'audio',
        'Enviando': 'Enviando',
        'Enviando a DLpy': 'Enviando a DLpy',
        'Abriendo con view': 'Abriendo con view',
        'Analizando enlace': 'Analizando enlace',
        'Eligiendo formato': 'Eligiendo formato',
        'Uniendo pistas': 'Uniendo pistas',
        'Revisando archivo': 'Revisando archivo',
        'Revisando · ya es compatible': 'Revisando · ya es compatible',
        'Revisando · hay que convertir': 'Revisando · hay que convertir',
        'Convirtiendo': 'Convirtiendo',
        'Ajustando pistas': 'Ajustando pistas',
        'Comprobando actualizaciones': 'Comprobando actualizaciones',
        'No se pudo comprobar actualizaciones': 'No se pudo comprobar actualizaciones',
        'Comprobando DLpy': 'Comprobando DLpy',
        'No se pudo comprobar DLpy': 'No se pudo comprobar DLpy',
        'Instalando DLpy': 'Instalando DLpy',
        'No se pudo instalar DLpy': 'No se pudo instalar DLpy',
        'Actualizando pip': 'Actualizando pip',
        'Comprobando pip': 'Comprobando pip',
        'Primera ejecución': 'Primera ejecución',
        'Misma versión': 'Misma versión',
        'Versión anterior': 'Versión anterior',
        'Actualizado': 'Actualizado',
        'Cambió el hash · edición detectada': 'Cambió el hash · edición detectada',
        'Ver todos': 'Ver todos',
        'Error': 'Error',
        'Cancelado': 'Cancelado',
        'Descarga lista': 'Descarga lista',
        'Descarga cancelada': 'Descarga cancelada',
        'Sin enlace': 'Sin enlace',
        'No se encontraron formatos': 'No se encontraron formatos',
        'No hay enlace: usa --scb LINK o --scm LINK.': 'No hay enlace: usa --scb LINK o --scm LINK.',
        'El análisis tardó demasiado para --scm; usa --scb.': 'El análisis tardó demasiado para --scm; usa --scb.',
        'El análisis tardó más de': 'El análisis tardó más de',
        'Sin respuesta: se elige': 'Sin respuesta: se elige',
        'No hay video compatible': 'No hay video compatible',
        'Se usará el mejor disponible': 'Se usará el mejor disponible',
        'Sin ffmpeg no se puede unir audio; el video quedará sin audio.': 'Sin ffmpeg no se puede unir audio; el video quedará sin audio.',
        'Se detectaron varios idiomas.': 'Se detectaron varios idiomas.',
        'Sin respuesta: se usa la pista original.': 'Sin respuesta: se usa la pista original.',
        'Se descargará de nuevo.': 'Se descargará de nuevo.',
        'Se reutiliza el archivo ya descargado.': 'Se reutiliza el archivo ya descargado.',
        'Conversión cancelada.': 'Conversión cancelada.',
        'No se pudo convertir el archivo existente': 'No se pudo convertir el archivo existente',
        'No se pudo guardar el archivo convertido': 'No se pudo guardar el archivo convertido',
        'No se pudo guardar el índice': 'No se pudo guardar el índice',
        'Espera mientras convierte · puede tardar · no cierres la app': 'Espera mientras convierte · puede tardar · no cierres la app',
        'Espera mientras convierte · no cierres la app': 'Espera mientras convierte · no cierres la app',
        'Espera · puede tardar · no cierres la app': 'Espera · puede tardar · no cierres la app',
        'Espera · no cierres la app': 'Espera · no cierres la app',
        'No cierres la app': 'No cierres la app',
        'Espera…': 'Espera…',
        'Sitio': 'Sitio',
        'Estreno': 'Estreno',
        'Novedad': 'Novedad',
        'Retroceso': 'Retroceso',
        'Igual': 'Igual',
        'Revisión': 'Revisión',
        'Espera': 'Espera',
        'Relevo': 'Relevo',
        'Conversión': 'Conversión',
        'Sustitución': 'Sustitución',
        'Unión': 'Unión',
        'Limpieza': 'Limpieza',
        'Papelera': 'Papelera',
        'Envío': 'Envío',
        'Descarga': 'Descarga',
        'Pulso': 'Pulso',
        'Carril': 'Carril',
        'El análisis rápido se quedó sin tiempo': 'El análisis rápido se quedó sin tiempo',
        'Seguimos sin límite de tiempo': 'Seguimos sin límite de tiempo',
        'Analizando enlace · puede tardar más': 'Analizando enlace · puede tardar más',
        'Toca la pantalla · Enter convertir · r remux · n original': 'Toca la pantalla · Enter convertir · r remux · n original',
        'Enter convertir · r remux · n original': 'Enter convertir · r remux · n original',
        'Toca la pantalla · Enter sustituir · n conservar': 'Toca la pantalla · Enter sustituir · n conservar',
        'Enter sustituir · n conservar': 'Enter sustituir · n conservar',
        'sin respuesta se convierte': 'sin respuesta se convierte',
        'sin respuesta se sustituye': 'sin respuesta se sustituye',
        'Toca la pantalla para abrir el teclado': 'Toca la pantalla para abrir el teclado',
        'Toca para abrir el teclado': 'Toca para abrir el teclado',
        '¿Convertir este video?': '¿Convertir este video?',
        '¿Convertir ahora?': '¿Convertir ahora?',
        '¿Convertir?': '¿Convertir?',
        '¿Sustituir el archivo?': '¿Sustituir el archivo?',
        '¿Sustituir archivo?': '¿Sustituir archivo?',
        '¿Sustituir?': '¿Sustituir?',
        'Solo audio': 'Solo audio',
        'Solo audio (mejor)': 'Solo audio (mejor)',
        'Solo audio · mejor': 'Solo audio · mejor',
        'Solo audio · Apple': 'Solo audio · Apple',
        'con audio': 'con audio',
        'original': 'original',
        'yt-dlp auto': 'yt-dlp auto',
        'Guardadas': 'Guardadas',
        'Opciones conocidas': 'Opciones conocidas',
        'Archivo': 'Archivo',
        'Por omisión': 'Por omisión',
        'Sin cambios.': 'Sin cambios.',
        'Configuración borrada': 'Configuración borrada',
        'Listo. Con --config NOMBRE=valor también se guarda sin menú; --config --lista muestra solo lo guardado.': 'Listo. Con --config NOMBRE=valor también se guarda sin menú; --config --lista muestra solo lo guardado.',
        'Nº o nombre: elegir · NOMBRE=valor: guardar · l: lista · o: olvidar todas · Enter: salir': 'Nº o nombre: elegir · NOMBRE=valor: guardar · l: lista · o: olvidar todas · Enter: salir',
        'Escribe el valor nuevo · Enter = dejarlo · - = borrar': 'Escribe el valor nuevo · Enter = dejarlo · - = borrar',
        'No se pudo guardar en': 'No se pudo guardar en',
        'No se guardó ningún modo.': 'No se guardó ningún modo.',
        'Se llena la pantalla, se borra con cada modo y eliges el que quede limpio sin deslizar.': 'Se llena la pantalla, se borra con cada modo y eliges el que quede limpio sin deslizar.',
        '¿Quedó limpia sin deslizar? s = guardar · n = siguiente · q = salir': '¿Quedó limpia sin deslizar? s = guardar · n = siguiente · q = salir',
        '¿Quedó limpia sin deslizar?': '¿Quedó limpia sin deslizar?',
        'guardar': 'guardar',
        'siguiente': 'siguiente',
        'salir': 'salir',
        'Modo': 'Modo',
        'como siempre: `clear` nativo de a-Shell + vaciar historial': 'como siempre: `clear` nativo de a-Shell + vaciar historial',
        'cursor arriba, borrar pantalla, vaciar historial y cursor arriba (ESC[H ESC[2J ESC[3J ESC[H)': 'cursor arriba, borrar pantalla, vaciar historial y cursor arriba (ESC[H ESC[2J ESC[3J ESC[H)',
        'cursor arriba y borrar hacia abajo, sin empujar nada al historial (ESC[H ESC[J ESC[3J)': 'cursor arriba y borrar hacia abajo, sin empujar nada al historial (ESC[H ESC[J ESC[3J)',
        'vaciar el historial primero y borrar después (ESC[3J ESC[H ESC[2J)': 'vaciar el historial primero y borrar después (ESC[3J ESC[H ESC[2J)',
        'reinicio total del terminal (ESC c; en a-Shell puede dejar la consola en negro)': 'reinicio total del terminal (ESC c; en a-Shell puede dejar la consola en negro)',
        'prueba de borrado': 'prueba de borrado',
        'config': 'config',
        'sistema': 'sistema',
        'perfil': 'perfil',
        'Sin datos técnicos (versión anterior).': 'Sin datos técnicos (versión anterior).',
        'Cada medida es de esta ejecución (el disco y yt_dlp pueden estar ya en caché).': 'Cada medida es de esta ejecución (el disco y yt_dlp pueden estar ya en caché).',
        'Corre en': 'Corre en',
        'Ancho': 'Ancho',
        'Guardar: --config NOMBRE=valor · borrar una: --config NOMBRE= · borrar todas: --config --olvidar · opciones: --config --opciones': 'Guardar: --config NOMBRE=valor · borrar una: --config NOMBRE= · borrar todas: --config --olvidar · opciones: --config --opciones',
        'ya es compatible': 'ya es compatible',
        'hay que convertir': 'hay que convertir',
        'puede tardar': 'puede tardar',
        'no cierres la app': 'no cierres la app',
        'pista original': 'pista original',
        'predeterminada': 'predeterminada',
        'recomendada': 'recomendada',
        'compatible': 'compatible',
        'Descarga cancelada.': 'Descarga cancelada.',
        'El archivo ya existe.': 'El archivo ya existe.',
        'Se conserva el original: el archivo se guarda sin convertir.': 'Se conserva el original: el archivo se guarda sin convertir.',
        'Archivos del script ocultos': 'Archivos del script ocultos',
        'Archivos del script visibles': 'Archivos del script visibles',
        'Sin mover (ya existe con el otro nombre): ': 'Sin mover (ya existe con el otro nombre): ',
        'Sin respuesta: se elige Sí.': 'Sin respuesta: se elige Sí.',
        'Sin respuesta: se elige No.': 'Sin respuesta: se elige No.',
        'Ver todos (+': 'Ver todos (+',
        'VIDEO': 'VIDEO',
        'AUDIO': 'AUDIO',
        'UNIÓN': 'UNIÓN',
        'GUARDADO': 'GUARDADO',
        'PISTA': 'PISTA',
        'espera': 'espera',
        'min': 'min',
        'seg': 'seg',
        'analizando': 'analizando',
        'actualizaciones': 'actualizaciones',
        'listas': 'listas',
        'falló': 'falló',
        'reintenta al abrir': 'reintenta al abrir',
        'ARCHIVO': 'ARCHIVO',
        'ELEGIR PISTA PREDETERMINADA': 'ELEGIR PISTA PREDETERMINADA',
        'ELEGIR PISTAS DE AUDIO ADICIONAL': 'ELEGIR PISTAS DE AUDIO ADICIONAL',
        'COMPATIBILIDAD APPLE': 'COMPATIBILIDAD APPLE',
        'YA DESCARGADO': 'YA DESCARGADO',
        'VERSIONES': 'VERSIONES',
        'DESCARGAS PENDIENTES': 'DESCARGAS PENDIENTES',
        'CHANGELOG · GITHUB': 'CHANGELOG · GITHUB',
        'Fmt': 'Fmt',
        'Códec': 'Códec',
        'Idioma': 'Idioma',
        'Tamaño': 'Tamaño',
        'Res': 'Res',
        'Rango': 'Rango',
        'Audio': 'Audio',
        'Pista': 'Pista',
        'Formato': 'Formato',
        'más': 'más',
        '(ninguna)': '(ninguna)',
        'Título': 'Título',
        'Portapapeles': 'Portapapeles',
        'Sin enlace.': 'Sin enlace.',
        'Cancelado.': 'Cancelado.',
        'Otra ejecución de DLpy sigue activa: espera a que termine.': 'Otra ejecución de DLpy sigue activa: espera a que termine.',
        'Analizando enlace...': 'Analizando enlace...',
        'No se encontraron formatos.': 'No se encontraron formatos.',
        'No se encontró el archivo descargado.': 'No se encontró el archivo descargado.',
        'No hay audio disponible; se descargará solo el video.': 'No hay audio disponible; se descargará solo el video.',
        'Este video no trae audio y no hay ffmpeg para unirlos.': 'Este video no trae audio y no hay ffmpeg para unirlos.',
        'Se descargará solo el video.': 'Se descargará solo el video.',
        'yt-dlp auto: se descarga tal cual, sin convertir.': 'yt-dlp auto: se descarga tal cual, sin convertir.',
        'Ya tienes este video con otra calidad o audio: se guarda con el nombre original.': 'Ya tienes este video con otra calidad o audio: se guarda con el nombre original.',
        'Caché de streams:': 'Caché de streams:',
        'archivo(s) reutilizado(s)': 'archivo(s) reutilizado(s)',
        'Reanudando:': 'Reanudando:',
        'ya descargados': 'ya descargados',
        'Parcial descartado tras fallos repetidos; se empieza de cero.': 'Parcial descartado tras fallos repetidos; se empieza de cero.',
        'Error al descargar:': 'Error al descargar:',
        'Error al analizar:': 'Error al analizar:',
        'Avance guardado': 'Avance guardado',
        'No se pudo guardar el archivo en': 'No se pudo guardar el archivo en',
        'Papelera:': 'Papelera:',
        'archivo(s) borrado(s) definitivamente': 'archivo(s) borrado(s) definitivamente',
        'más de': 'más de',
        'días en ella': 'días en ella',
        'Elige un formato': 'Elige un formato',
        'Ver todos ·': 'Ver todos ·',
        'formatos': 'formatos',
        'n.º · b ★ mejor ·': 'n.º · b ★ mejor ·',
        'm más · ': 'm más · ',
        'q salir': 'q salir',
        'Opción inválida: escribe un número del 1 al': 'Opción inválida: escribe un número del 1 al',
        'Elegido': 'Elegido',
        'Audio:': 'Audio:',
        'pistas': 'pistas',
        'incluido; no admite pistas adicionales': 'incluido; no admite pistas adicionales',
        'sin audio': 'sin audio',
        'audio · ': 'audio · ',
        'Vaciando': 'Vaciando',
        'compatible Apple': 'compatible Apple',
        'Abriendo con view...': 'Abriendo con view...',
        'Reanalizando el enlace...': 'Reanalizando el enlace...',
        'Reintentando análisis (yt-dlp en bruto)...': 'Reintentando análisis (yt-dlp en bruto)...',
        'Sin respuesta: se convierte.': 'Sin respuesta: se convierte.',
        'Sin respuesta: se instala.': 'Sin respuesta: se instala.',
        'Sin respuesta: no se instala.': 'Sin respuesta: no se instala.',
        'El archivo descargado ya es compatible con Apple: se guarda sin convertir.': 'El archivo descargado ya es compatible con Apple: se guarda sin convertir.',
        'Este resultado no es compatible con Apple.': 'Este resultado no es compatible con Apple.',
        'No hay ffmpeg para convertir; se descargará tal cual.': 'No hay ffmpeg para convertir; se descargará tal cual.',
        'Conversión cancelada; se descargará sin convertir.': 'Conversión cancelada; se descargará sin convertir.',
        'Remux: se cambia el contenedor y el audio; el video no se recodifica.': 'Remux: se cambia el contenedor y el audio; el video no se recodifica.',
        'Último enlace': 'Último enlace',
        'última versión': 'última versión',
        'versión local': 'versión local',
        'actualizada': 'actualizada',
        'actualizado': 'actualizado',
        'instalado': 'instalado',
        'instalada': 'instalada',
        'idéntica al Release': 'idéntica al Release',
        'Nueva versión de DLpy': 'Nueva versión de DLpy',
        'no se pudo comprobar la última versión': 'no se pudo comprobar la última versión',
        'para YouTube': 'para YouTube',
        'timeout': 'timeout',
        'sin red': 'sin red',
        'misma versión': 'misma versión',
        'edición detectada': 'edición detectada',
        'Cambió el hash': 'Cambió el hash',
        'Comprobando': 'Comprobando',
        'Actualizando': 'Actualizando',
        'Instalando': 'Instalando',
        'Analizando': 'Analizando',
        'Uniendo': 'Uniendo',
        'Revisando': 'Revisando',
        'No se pudo comprobar': 'No se pudo comprobar',
        'No se pudo instalar': 'No se pudo instalar',
        'No se pudo actualizar': 'No se pudo actualizar',
        'Pega el enlace': 'Pega el enlace',
        'Todo al día': 'Todo al día',
        'Hay una versión nueva de DLpy': 'Hay una versión nueva de DLpy',
        'Actualización': 'Actualización',
        'Actualización de': 'Actualización de',
        'Versión': 'Versión',
        'Conectando a GitHub': 'Conectando a GitHub',
        'Caché de streams': 'Caché de streams',
        'Caché stream': 'Caché stream',
        'Reutilizado de caché: formato': 'Reutilizado de caché: formato',
        'Reanudando': 'Reanudando',
        'Movidos a papelera': 'Movidos a papelera',
        'Limpiando': 'Limpiando',
        'El formato del atajo ya no está: se usa': 'El formato del atajo ya no está: se usa',
        'El formato elegido ya no está disponible; se usa el mejor equivalente.': 'El formato elegido ya no está disponible; se usa el mejor equivalente.',
        'Mismo número con código distinto: revisa cuál es el bueno.': 'Mismo número con código distinto: revisa cuál es el bueno.',
        'Mismos streams ya descargados: se convierte ese archivo sin volver a bajarlo.': 'Mismos streams ya descargados: se convierte ese archivo sin volver a bajarlo.',
        'Estimación ~': 'Estimación ~',
        'Convertido a': 'Convertido a',
        'Usando': 'Usando',
        'Se usará la': 'Se usará la',
        'Actualiza yt-dlp (pip install -U yt-dlp) o inténtalo más tarde.': 'Actualiza yt-dlp (pip install -U yt-dlp) o inténtalo más tarde.',
        'Instálala con: pip install': 'Instálala con: pip install',
        'Instálalo con:': 'Instálalo con:',
        'Si pip indicó éxito, vuelve a ejecutar DLpy; si no: pip install': 'Si pip indicó éxito, vuelve a ejecutar DLpy; si no: pip install',
        'pip terminó con error (código': 'pip terminó con error (código',
        'YouTube necesita un runtime de JavaScript y no hay ninguno: pueden faltar formatos.': 'YouTube necesita un runtime de JavaScript y no hay ninguno: pueden faltar formatos.',
        'YouTube pide comprobar que no eres un bot; no se puede analizar este enlace.': 'YouTube pide comprobar que no eres un bot; no se puede analizar este enlace.',
        'No se pudo abrir con view: el archivo está en dlpy_files.': 'No se pudo abrir con view: el archivo está en dlpy_files.',
        'El archivo a entregar está vacío.': 'El archivo a entregar está vacío.',
        'Guardado. DLpy lo lee en cada ejecución: ya vale desde el siguiente comando, sin reiniciar nada.': 'Guardado. DLpy lo lee en cada ejecución: ya vale desde el siguiente comando, sin reiniciar nada.',
        'El nombre puede ir sin DLPY_ (list_visible_rows = DLPY_LIST_VISIBLE_ROWS). Un export manda en esa ejecución y también se guarda. DLPY_IGNORE_SAVED_CONFIG y DLPY_SKIP_SHA_VERIFY son de una sola ejecución.': 'El nombre puede ir sin DLPY_ (list_visible_rows = DLPY_LIST_VISIBLE_ROWS). Un export manda en esa ejecución y también se guarda. DLPY_IGNORE_SAVED_CONFIG y DLPY_SKIP_SHA_VERIFY son de una sola ejecución.',
        'Opción inválida: T, números del 1 al': 'Opción inválida: T, números del 1 al',
        '✓ actual · ⬆ la de actualizar': '✓ actual · ⬆ la de actualizar',
        'Cuando haya una versión más nueva que la': 'Cuando haya una versión más nueva que la',
        'Se volverá a preguntar en la próxima comprobación': 'Se volverá a preguntar en la próxima comprobación',
        'No se vuelve a preguntar por esta versión; --actualizar lo pregunta de nuevo.': 'No se vuelve a preguntar por esta versión; --actualizar lo pregunta de nuevo.',
        'No se vuelve a preguntar por esta versión; con --actualizar la instalas.': 'No se vuelve a preguntar por esta versión; con --actualizar la instalas.',
        'No hay versiones para instalar (Releases de GitHub).': 'No hay versiones para instalar (Releases de GitHub).',
        'No se pudieron leer los Releases de GitHub.': 'No se pudieron leer los Releases de GitHub.',
        'El repositorio no tiene Releases publicados.': 'El repositorio no tiene Releases publicados.',
        'SHA-256 no coincide: el archivo descargado no es el que publicó el Release; no se instala.': 'SHA-256 no coincide: el archivo descargado no es el que publicó el Release; no se instala.',
        'SHA-256 sin verificar (DLPY_SKIP_SHA_VERIFY=1)': 'SHA-256 sin verificar (DLPY_SKIP_SHA_VERIFY=1)',
        'Sin SHA-256: este Release no publica hash, no se pudo verificar la descarga.': 'Sin SHA-256: este Release no publica hash, no se pudo verificar la descarga.',
        'Sin SHA-256 publicado: no se instala. DLPY_SKIP_SHA_VERIFY=1 omite la verificación.': 'Sin SHA-256 publicado: no se instala. DLPY_SKIP_SHA_VERIFY=1 omite la verificación.',
        'No se pudieron guardar las variables DLPY_* en': 'No se pudieron guardar las variables DLPY_* en',
        'No se pudo usar el portapapeles y el código no cabe dentro del enlace.': 'No se pudo usar el portapapeles y el código no cabe dentro del enlace.',
        'No se pudo usar el portapapeles; el código va dentro del enlace.': 'No se pudo usar el portapapeles; el código va dentro del enlace.',
        'No se pudo leer el código': 'No se pudo leer el código',
        'No se volvió a abrir.': 'No se volvió a abrir.',
        'No se detectó': 'No se detectó',
        'DLPY_YTDLP_EXTRA_ARGS inválido': 'DLPY_YTDLP_EXTRA_ARGS inválido',
        'changelog.md generado en dlpy_files desde los Releases de GitHub': 'changelog.md generado en dlpy_files desde los Releases de GitHub',
        'Changelog actualizado desde los Releases de GitHub (': 'Changelog actualizado desde los Releases de GitHub (',
        'No hay changelog que añadir (changelog.md no existe todavía): va sin él.': 'No hay changelog que añadir (changelog.md no existe todavía): va sin él.',
        'Apple reproduce HEVC de hasta 10 bits; con 12 el archivo puede no abrirse en Apple.': 'Apple reproduce HEVC de hasta 10 bits; con 12 el archivo puede no abrirse en Apple.',
        'Con 10 bits se pierde algo de precisión de color; con 8 más.': 'Con 10 bits se pierde algo de precisión de color; con 8 más.',
        'El tone mapping no funcionó: se conserva el HDR en 10 bits.': 'El tone mapping no funcionó: se conserva el HDR en 10 bits.',
        'Este ffmpeg no trae zscale/tonemap: el HDR se conserva en 10 bits (a 8 bits sin tone mapping se vería apagado).': 'Este ffmpeg no trae zscale/tonemap: el HDR se conserva en 10 bits (a 8 bits sin tone mapping se vería apagado).',
        'HDR detectado: se conserva con sus etiquetas de color (BT.2020 ·': 'HDR detectado: se conserva con sus etiquetas de color (BT.2020 ·',
        'HDR detectado: se pasa a SDR (BT.709) con tone mapping; tarda más.': 'HDR detectado: se pasa a SDR (BT.709) con tone mapping; tarda más.',
        'No hay modo sin pérdida aquí (este ffmpeg no trae x265 ni Kvazaar, o el video es de más de 8 bits): se usa la mayor calidad posible.': 'No hay modo sin pérdida aquí (este ffmpeg no trae x265 ni Kvazaar, o el video es de más de 8 bits): se usa la mayor calidad posible.',
        'No hubo modo sin pérdida (este ffmpeg no trae x265 ni Kvazaar, o el video es de más de 8 bits): se usó': 'No hubo modo sin pérdida (este ffmpeg no trae x265 ni Kvazaar, o el video es de más de 8 bits): se usó',
        'Sin pérdida: el video se recodifica sin quitar nada de lo decodificado; el archivo pesa mucho más que el original.': 'Sin pérdida: el video se recodifica sin quitar nada de lo decodificado; el archivo pesa mucho más que el original.',
        'ProRes 422 HQ: casi igual al original (no es matemáticamente sin pérdida); el archivo sale en .mov y pesa muchísimo más.': 'ProRes 422 HQ: casi igual al original (no es matemáticamente sin pérdida); el archivo sale en .mov y pesa muchísimo más.',
        'ProRes 422 HQ: 10 bits.': 'ProRes 422 HQ: 10 bits.',
        'No se pudo convertir a compatible Apple': 'No se pudo convertir a compatible Apple',
        'No se pudo ajustar la pista predeterminada': 'No se pudo ajustar la pista predeterminada',
        'No se pudo leer el archivo: se sigue el plan de conversión de antes.': 'No se pudo leer el archivo: se sigue el plan de conversión de antes.',
        'No se pudieron detectar los bits del origen; si el archivo resulta tener más de 8 se': 'No se pudieron detectar los bits del origen; si el archivo resulta tener más de 8 se',
        'Leyendo los bits del video de origen…': 'Leyendo los bits del video de origen…',
        'El archivo descargado es de': 'El archivo descargado es de',
        'Revisado el archivo real:': 'Revisado el archivo real:',
        '¿Instalar alguna? n.º': '¿Instalar alguna? n.º',
        'Reintentando análisis (': 'Reintentando análisis (',
        'listo': 'listo',
        'Remux a': 'Remux a',
        'Recodificar el video a': 'Recodificar el video a',
        'El video de origen es de': 'El video de origen es de',
        'bits': 'bits',
        's a 8 bits; con más bits tarda algo más.': 's a 8 bits; con más bits tarda algo más.',
        's (umbral de pregunta:': 's (umbral de pregunta:',
        'Conservar': 'Conservar',
        'bits: degradados suaves': 'bits: degradados suaves',
        'A 8 bits:': 'A 8 bits:',
        'Origen de': 'Origen de',
        'bits: se guarda en 8': 'bits: se guarda en 8',
        'Esperado': 'Esperado',
        'Obtenido:': 'Obtenido:',
        'líneas más: «m»': 'líneas más: «m»',
        'más antiguas sin mostrar': 'más antiguas sin mostrar',
        'más: «m»': 'más: «m»',
        'SHA-256 verificado': 'SHA-256 verificado',
        'versión local más reciente que la del último Release': 'versión local más reciente que la del último Release',
        'bajaste a propósito desde la': 'bajaste a propósito desde la',
        'no se ofrece la': 'no se ofrece la',
        'del Release': 'del Release',
        'del Release no es más nueva que la': 'del Release no es más nueva que la',
        'de la que bajaste a propósito.': 'de la que bajaste a propósito.',
        'Hay una versión nueva de DLpy:': 'Hay una versión nueva de DLpy:',
        '(Release)': '(Release)',
        'No se pudo lanzar pip para': 'No se pudo lanzar pip para',
        'Falta la dependencia:': 'Falta la dependencia:',
        'es obligatoria: sin ella DLpy no puede continuar.': 'es obligatoria: sin ella DLpy no puede continuar.',
        'hay una': 'hay una',
        '(rechazada; --actualizar la instala)': '(rechazada; --actualizar la instala)',
        'No se pudo copiar changelog a dlpy_files:': 'No se pudo copiar changelog a dlpy_files:',
        'No se pudo escribir el changelog:': 'No se pudo escribir el changelog:',
        'Changelog actualizado desde los Releases de GitHub': 'Changelog actualizado desde los Releases de GitHub',
        'versión/es': 'versión/es',
        'Almacenamiento': 'Almacenamiento',
        'supera límite': 'supera límite',
        'pero se conserva (DLPY_KEEP_DOWNLOADS_OVER_LIMIT=1).': 'pero se conserva (DLPY_KEEP_DOWNLOADS_OVER_LIMIT=1).',
        'Movidos a papelera:': 'Movidos a papelera:',
        'archivo(s) de más de': 'archivo(s) de más de',
        'días. Se borrarán tras': 'días. Se borrarán tras',
        'días en trash.': 'días en trash.',
        'Trash:': 'Trash:',
        'borrado:': 'borrado:',
        'd en papelera (límite': 'd en papelera (límite',
        'No se pudo reiniciar': 'No se pudo reiniciar',
        'edición detectada (cambió el hash, misma versión)': 'edición detectada (cambió el hash, misma versión)',
        'No se pudo obtener la': 'No se pudo obtener la',
        '(descarga fallida, archivo no válido o SHA-256 que no coincide).': '(descarga fallida, archivo no válido o SHA-256 que no coincide).',
        'Bajaste de la': 'Bajaste de la',
        'a la': 'a la',
        'No se ofrecerá actualizar hasta que haya un Release con una': 'No se ofrecerá actualizar hasta que haya un Release con una',
        'En el próximo arranque se volverá a ofrecer': 'En el próximo arranque se volverá a ofrecer',
        'No se pudo cachear stream': 'No se pudo cachear stream',
        'No se pudo sembrar': 'No se pudo sembrar',
        'sin terminar (caducan a las 24 h).': 'sin terminar (caducan a las 24 h).',
        'T todas · n.º (1 3 · 1-3) · D n.º descartar ·': 'T todas · n.º (1 3 · 1-3) · D n.º descartar ·',
        'Enter = ninguna': 'Enter = ninguna',
        'Descartadas:': 'Descartadas:',
        'No se pudo abrir el atajo': 'No se pudo abrir el atajo',
        'el archivo está en dlpy_files.': 'el archivo está en dlpy_files.',
        'No se pudo leer el código:': 'No se pudo leer el código:',
        'DLPY_YTDLP_EXTRA_ARGS inválido:': 'DLPY_YTDLP_EXTRA_ARGS inválido:',
        'Reintentando análisis': 'Reintentando análisis',
        'no se pudo medir': 'no se pudo medir',
        'sin changelog': 'sin changelog',
        'el mismo con otro id.': 'el mismo con otro id.',
        'la misma calidad (otro id).': 'la misma calidad (otro id).',
        'la calidad más parecida.': 'la calidad más parecida.',
        'el mejor compatible.': 'el mejor compatible.',
        'Predeterminada:': 'Predeterminada:',
        'n.º separados por espacio (ej. 1 2 4) ·': 'n.º separados por espacio (ej. 1 2 4) ·',
        'No se pudo ajustar la pista predeterminada:': 'No se pudo ajustar la pista predeterminada:',
        'No se pudo convertir a compatible Apple:': 'No se pudo convertir a compatible Apple:',
        'No se pudo convertir el archivo existente:': 'No se pudo convertir el archivo existente:',
        'No se pudo guardar el archivo convertido:': 'No se pudo guardar el archivo convertido:',
        'No se pudo guardar el índice:': 'No se pudo guardar el índice:',
        'no disponible; probando': 'no disponible; probando',
        'Opción 1-': 'Opción 1-',
        'Enter = convertir': 'Enter = convertir',
        'r = solo remux': 'r = solo remux',
        '¿Incluir pistas adicionales? (s/N)': '¿Incluir pistas adicionales? (s/N)',
        '¿Instalar': '¿Instalar',
        '(S/n)': '(S/n)',
        '¿Con changelog? (s/N)': '¿Con changelog? (s/N)',
        'Release ≠ instalada (código distinto:': 'Release ≠ instalada (código distinto:',
        'líneas)': 'líneas)',
        'guardado; vale desde el siguiente comando': 'guardado; vale desde el siguiente comando',
        'No se pudo comprobar la última versión (Releases de GitHub)': 'No se pudo comprobar la última versión (Releases de GitHub)',
        'entregado': 'entregado',
        'días': 'días',
        'día': 'día',
        'archivo(s)': 'archivo(s)',
        'de más de': 'de más de',
        'Se borrarán tras': 'Se borrarán tras',
        'en trash': 'en trash',
        'en papelera': 'en papelera',
        'horas': 'horas',
        'hora': 'hora',
        'caducan a las 24 h': 'caducan a las 24 h',
        'sin terminar': 'sin terminar',
        # 1.9.4: frases completas que antes quedaban en español
        'más rápido': 'más rápido',
        'Puede verse con bandas en cielos y degradados': 'Puede verse con bandas en cielos y degradados',
        'no se pudo comprobar la actualización; se conserva el paquete local': 'no se pudo comprobar la actualización; se conserva el paquete local',
        'no se pudo descargar; se usará español': 'no se pudo descargar; se usará español',
        'falló la descarga de la actualización; se conserva el paquete local': 'falló la descarga de la actualización; se conserva el paquete local',
        'falló la descarga; se usará español': 'falló la descarga; se usará español',
        'no hay un paquete local válido y las actualizaciones están desactivadas; se usará español': 'no hay un paquete local válido y las actualizaciones están desactivadas; se usará español',
        '● guardada  ·  ✗ guardada inválida (se usa el predeterminado)  ·  [ ] predeterminado': '● guardada  ·  ✗ guardada inválida (se usa el predeterminado)  ·  [ ] predeterminado',
        'No se pudieron detectar los bits del origen; si el archivo resulta tener más de 8 se conservan (hasta 10)': 'No se pudieron detectar los bits del origen; si el archivo resulta tener más de 8 se conservan (hasta 10)',
        'n.º': 'n.º',
        'Enter = original': 'Enter = original',
        'Enter = todas': 'Enter = todas',
        'Enter = no': 'Enter = no',
        'descargando': 'descargando',
        'el archivo': 'el archivo',
        'leyendo los Releases de': 'leyendo los Releases de',
        '(versiones y changelog)': '(versiones y changelog)',
        # 2.0.6: claves que faltaban en el catálogo embebido (el resto ya estaba)
        'Conversión rápida (solo remux/audio): se convierte sin preguntar.': 'Conversión rápida (solo remux/audio): se convierte sin preguntar.',
        '¿Seguir con las demás descargas pendientes?': '¿Seguir con las demás descargas pendientes?',
        'Idioma establecido': 'Idioma establecido',
        'Idioma actual': 'Idioma actual',
        'Seleccione idioma': 'Seleccione idioma',
        'Enter': 'Enter',
        ' (con v=audio, a=<audio_ids[n]> elige ese audio exacto; v=more abre la lista completa)': ' (con v=audio, a=<audio_ids[n]> elige ese audio exacto; v=more abre la lista completa)',
    },
})

I18N_PHRASES = LangTable("phrases", {
    'es': {
        ' con audio': ' con audio',
        ' sin audio': ' sin audio',
        ' guardadas': ' guardadas',
        ' guardada': ' guardada',
        ' guardados': ' guardados',
        ' guardado': ' guardado',
        ' archivos': ' archivos',
        ' archivo': ' archivo',
        ' segundos': ' segundos',
        ' minutos': ' minutos',
    },
})

# 1.7.1: textos de la bienvenida / cambio de versión que faltaban en el catálogo (rótulos del dibujo de primera ejecución y tarjetas de versión). Se unen a I18N.
I18N_WELCOME = LangTable("welcome", {
    'es': {
        'carpetas': 'carpetas',
        'estado': 'estado',
        'Edición detectada': 'Edición detectada',
        'Actualizada': 'Actualizada',
        'Bajada de versión': 'Bajada de versión',
        'carpeta interna reiniciada': 'carpeta interna reiniciada',
        'no se pudo reiniciar': 'no se pudo reiniciar',
        'Instalada a propósito desde --versions.': 'Instalada a propósito desde --versions.',
        'El dlpy.py se reemplazó por uno más viejo fuera de DLpy (copia manual, atajo o copia antigua).': 'El dlpy.py se reemplazó por uno más viejo fuera de DLpy (copia manual, atajo o copia antigua).',
    },
})
for _c, _d in I18N_WELCOME.items():
    I18N.setdefault(_c, {}).update(_d)

# 1.7.1: textos que viven DENTRO de las animaciones (chips y líneas de la pregunta). Una fila por clave (español canónico); las traducciones llegan en el .mo y se unen a I18N.
# El dibujo no lleva texto propio: lo pide con ux_text / ux_pick / ux_chip (sección [UX4b]). Las claves «Enter …» y «n …» son segmentos de la línea de opciones (se unen con « · »).
_UX_LANGS = ()  # 2.0.8: ningún idioma embebido; todos llegan en su .mo
_UX_ROWS = (
    'VIEJO',
    'NUEVO',
    'Toca la pantalla',
    'Toca = teclado',
    'Enter sustituir',
    'Enter convertir',
    'Enter sí',
    'n no',
    'Adelanto',
    'papelera',
    'basura',
    '¿RES?',
    '¿COD?',
    '¿FPS?',
    '¿BIT?',
    '¿KHZ?',
)
I18N_UX = LangTable("ux", {"es": {k: k for k in _UX_ROWS}})  # 2.0.8: solo español embebido (identidad)
for _c, _d in I18N_UX.items():
    I18N.setdefault(_c, {}).update(_d)

# 2.0.9: descripciones y textos de --config como msgid español canónico (motor de idiomas, regla 11).
I18N_CONFIG = LangTable("config", {
    'es': {
        '1 = depuración (logs extra y salida verbosa)': '1 = depuración (logs extra y salida verbosa)',
        'cuántos logs de depuración se conservan': 'cuántos logs de depuración se conservan',
        'filas de lista que caben: auto o número': 'filas de lista que caben: auto o número',
        'líneas de la interfaz': 'líneas de la interfaz',
        'ancho en columnas (mín. 20) o auto': 'ancho en columnas (mín. 20) o auto',
        '1 = truecolor · 0 = colores básicos': '1 = truecolor · 0 = colores básicos',
        '1 = animaciones · 0 = sin animaciones': '1 = animaciones · 0 = sin animaciones',
        '1 = barra clásica █░ · 0 = estilo actual': '1 = barra clásica █░ · 0 = estilo actual',
        '1 = animación del análisis del enlace · 0 = no': '1 = animación del análisis del enlace · 0 = no',
        '1 = pip puede ceder la escena · 0 = pip escribe al terminal': '1 = pip puede ceder la escena · 0 = pip escribe al terminal',
        '1 = efecto glitch en transiciones · 0 = sin ruido': '1 = efecto glitch en transiciones · 0 = sin ruido',
        '1 = textos de D L P Y más legibles (menos ruido) · 0 = normal': '1 = textos de D L P Y más legibles (menos ruido) · 0 = normal',
        'ritmo de escenas, incluido el análisis del enlace: wait = cada loop entero · real = al ritmo del proceso · número = segundos fijos (0–60). D L P Y no espera': 'ritmo de escenas, incluido el análisis del enlace: wait = cada loop entero · real = al ritmo del proceso · número = segundos fijos (0–60). D L P Y no espera',
        'segundos de validez del resultado del análisis antes de bajar (0 = no reanalizar); evita 403 si wait alarga la espera': 'segundos de validez del resultado del análisis antes de bajar (0 = no reanalizar); evita 403 si wait alarga la espera',
        'segundos del loop de animaciones de proceso y del análisis del enlace (0.2–3); D L P Y no espera': 'segundos del loop de animaciones de proceso y del análisis del enlace (0.2–3); D L P Y no espera',
        '1 = conversión ligera (menos animación) · 0 = conversión animada (no es la calidad)': '1 = conversión ligera (menos animación) · 0 = conversión animada (no es la calidad)',
        'preset de conversión: fast · high · best · prores': 'preset de conversión: fast · high · best · prores',
        '0 = archivos del script visibles · 1 = ocultos (con punto). Descargas y papelera siempre visibles': '0 = archivos del script visibles · 1 = ocultos (con punto). Descargas y papelera siempre visibles',
        '1 = al limpiar purga el scrollback del terminal · 0 = no': '1 = al limpiar purga el scrollback del terminal · 0 = no',
        'primer borrado al arrancar: reset · auto · home · down · purge-first': 'primer borrado al arrancar: reset · auto · home · down · purge-first',
        'limpieza normal: auto · home · down · purge-first · reset': 'limpieza normal: auto · home · down · purge-first · reset',
        '1 = cierre de escena hacia el centro · 0 = solo limpia': '1 = cierre de escena hacia el centro · 0 = solo limpia',
        'franja superior: 0 = oculta · 1 = DTV (todo) · letras D/T/V en el orden que quieras (se ve al descargar; si no cabe, se quitan D y T en ese orden)': 'franja superior: 0 = oculta · 1 = DTV (todo) · letras D/T/V en el orden que quieras (se ve al descargar; si no cabe, se quitan D y T en ese orden)',
        'franja inferior (activa por defecto): 0 = oculta · 1 = EAN (todo) · E = errores (✕) · A = advertencias (!) · N = red (⇅, siempre visible: se pone blanco cuando el script conecta a internet); orden configurable (EAN / NAE)': 'franja inferior (activa por defecto): 0 = oculta · 1 = EAN (todo) · E = errores (✕) · A = advertencias (!) · N = red (⇅, siempre visible: se pone blanco cuando el script conecta a internet); orden configurable (EAN / NAE)',
        'al terminar: view = el comando `view` de a-Shell (predeterminado) · shortcut = se entrega al atajo': 'al terminar: view = el comando `view` de a-Shell (predeterminado) · shortcut = se entrega al atajo',
        '1 = una sola ejecución a la vez (bloqueo) y vigilante de congelamientos (con DLPY_DEBUG_LOGGING anota dónde se atasca) · 0 = apagado': '1 = una sola ejecución a la vez (bloqueo) y vigilante de congelamientos (con DLPY_DEBUG_LOGGING anota dónde se atasca) · 0 = apagado',
        '0 = apagado (predeterminado) · 1 = --scm y --scb listan directo en el script (lista normal, «m» = más) y descargan ahí, sin JSON ni atajo · all = abre ya la lista completa': '0 = apagado (predeterminado) · 1 = --scm y --scb listan directo en el script (lista normal, «m» = más) y descargan ahí, sin JSON ni atajo · all = abre ya la lista completa',
        '1 = leer enlace del portapapeles': '1 = leer enlace del portapapeles',
        'diagnóstico de traducción: 0 = apagado · mark = colorea el texto traducido · id = muestra solo el msgid original (sin traducción ni catálogos de idioma) · both = id + mark: solo el msgid original, coloreado': 'diagnóstico de traducción: 0 = apagado · mark = colorea el texto traducido · id = muestra solo el msgid original (sin traducción ni catálogos de idioma) · both = id + mark: solo el msgid original, coloreado',
        'comprobar actualizaciones del script y de sus dependencias: cada cuánto, con unidad (30m minutos · 6h horas · 2d días · 1w semanas · daily · weekly) o un número = días · on = cada arranque · 0/off = nunca (predeterminado: 1w = semanal)': 'comprobar actualizaciones del script y de sus dependencias: cada cuánto, con unidad (30m minutos · 6h horas · 2d días · 1w semanas · daily · weekly) o un número = días · on = cada arranque · 0/off = nunca (predeterminado: 1w = semanal)',
        'repo de GitHub de los Releases': 'repo de GitHub de los Releases',
        'límite de almacenamiento en MB': 'límite de almacenamiento en MB',
        'tope del análisis en el atajo (s; 0 = sin tope)': 'tope del análisis en el atajo (s; 0 = sin tope)',
        'tope de --scm (s)': 'tope de --scm (s)',
        'tope duro de --scm desde el arranque (s; 0 = sin tope)': 'tope duro de --scm desde el arranque (s; 0 = sin tope)',
        'fragmentos que se bajan a la vez en DASH/HLS (1–16; 1 = uno a uno, lo más suave para a-Shell mini)': 'fragmentos que se bajan a la vez en DASH/HLS (1–16; 1 = uno a uno, lo más suave para a-Shell mini)',
        'subtítulos junto al video: 0 = no · idiomas separados por coma (es,en) · all = todos': 'subtítulos junto al video: 0 = no · idiomas separados por coma (es,en) · all = todos',
        '1 = título, artista y carátula en m4a/mp4/mp3 con mutagen (si está instalado) · 0 = no': '1 = título, artista y carátula en m4a/mp4/mp3 con mutagen (si está instalado) · 0 = no',
        'argumentos extra para yt-dlp': 'argumentos extra para yt-dlp',
        'variable guardada que no está en la lista de opciones conocidas': 'variable guardada que no está en la lista de opciones conocidas',
        'Nombre anterior': 'Nombre anterior',
        'Antes:': 'Antes:',
        'Nº o nombre: elegir · NOMBRE=valor: guardar · l: lista · o: olvidar todas · Enter: salir': 'Nº o nombre: elegir · NOMBRE=valor: guardar · l: lista · o: olvidar todas · Enter: salir',
        'Escribe el valor nuevo · Enter = dejarlo · - = borrar': 'Escribe el valor nuevo · Enter = dejarlo · - = borrar',
        'Sin cambios.': 'Sin cambios.',
        'Por omisión': 'Por omisión',
        'Guardadas': 'Guardadas',
        'Guardado': 'Guardado',
        'Opciones conocidas': 'Opciones conocidas',
        '¿Borrar todas las variables guardadas?': '¿Borrar todas las variables guardadas?',
        'El nombre puede ir sin DLPY_ (list_visible_rows = DLPY_LIST_VISIBLE_ROWS). Un export manda en esa ejecución y también se guarda. DLPY_IGNORE_SAVED_CONFIG y DLPY_SKIP_SHA_VERIFY son de una sola ejecución (no se guardan).': 'El nombre puede ir sin DLPY_ (list_visible_rows = DLPY_LIST_VISIBLE_ROWS). Un export manda en esa ejecución y también se guarda. DLPY_IGNORE_SAVED_CONFIG y DLPY_SKIP_SHA_VERIFY son de una sola ejecución (no se guardan).',
        'Listo. Con --config NOMBRE=valor también se guarda sin menú; --config --lista muestra solo lo guardado.': 'Listo. Con --config NOMBRE=valor también se guarda sin menú; --config --lista muestra solo lo guardado.',
        'Guardar: --config NOMBRE=valor · borrar una: --config NOMBRE= · borrar todas: --config --olvidar · opciones: --config --opciones': 'Guardar: --config NOMBRE=valor · borrar una: --config NOMBRE= · borrar todas: --config --olvidar · opciones: --config --opciones',
        'idioma: ask · auto · es · en · pt · fr · de · it · ru · zh · hi · ar · ja · ko · pl (es = único embebido; el resto se baja de GitHub)': 'idioma: ask · auto · es · en · pt · fr · de · it · ru · zh · hi · ar · ja · ko · pl (es = único embebido; el resto se baja de GitHub)',
    },
})
for _c, _d in I18N_CONFIG.items():
    I18N.setdefault(_c, {}).update(_d)

# 2.1.0: textos del atajo (menú, config, sistema, errores): msgid español canónico; el motor los traduce como a I18N_CONFIG.
# Sin paquete caen al español; con paquete, al idioma activo. El menú de actualizar el script desde el portapapeles queda en
# español (es la vía de rescate cuando el py instalado es viejo) y no entra aquí.
I18N_ATAJO = LangTable("atajo", {
    'es': {
        'DLpy': 'DLpy',
        '➡️ Abrir': '➡️ Abrir',
        '➡️ Ingresar Link': '➡️ Ingresar Link',
        'ℹ️ Buscar Actualización': 'ℹ️ Buscar Actualización',
        '🌎 Idioma': '🌎 Idioma',
        '⚙️ Configurar variables': '⚙️ Configurar variables',
        '📋 Portapapeles': '📋 Portapapeles',
        '🛠️ Reinstalar/Instalar': '🛠️ Reinstalar/Instalar',
        '🩺 Sistema / Diagnóstico': '🩺 Sistema / Diagnóstico',
        'Link': 'Link',
        '⚠️ Error:': '⚠️ Error:',
        'ℹ️ Audio principal': 'ℹ️ Audio principal',
        '🌎 Adicional': '🌎 Adicional',
        '⚠️ Actualiza dlpy.py': '⚠️ Actualiza dlpy.py',
        'Este atajo necesita un dlpy.py más nuevo (con --atajo). Se baja la última versión desde GitHub.': 'Este atajo necesita un dlpy.py más nuevo (con --atajo). Se baja la última versión desde GitHub.',
        '✅ dlpy.py reinstalado': '✅ dlpy.py reinstalado',
        '✅ Se instaló dlpy.py': '✅ Se instaló dlpy.py',
        'No existía, se bajó la última versión desde GitHub.\n\n¿Continuar con ejecución?': 'No existía, se bajó la última versión desde GitHub.\n\n¿Continuar con ejecución?',
        '🖥 Sistema': '🖥 Sistema',
        '⏱ Perfil': '⏱ Perfil',
        '📦 Versiones': '📦 Versiones',
        '⬅ Volver': '⬅ Volver',
        '⬅ Cancelar': '⬅ Cancelar',
        '⚙️ Elige una opción · ● guardada · ✗ inválida · ○ por omisión': '⚙️ Elige una opción · ● guardada · ✗ inválida · ○ por omisión',
        '🗑 Borrar todas…': '🗑 Borrar todas…',
        '✅ Listo / Salir': '✅ Listo / Salir',
        '✏️ Cambiar valor': '✏️ Cambiar valor',
        '🗑 Borrar (volver a por omisión)': '🗑 Borrar (volver a por omisión)',
        '¿Cambiar otra opción?': '¿Cambiar otra opción?',
        '✏️ Escribir otro valor…': '✏️ Escribir otro valor…',
        'Escribe el valor nuevo': 'Escribe el valor nuevo',
        'Elige el valor nuevo': 'Elige el valor nuevo',
        '✅ Guardado': '✅ Guardado',
        '✅ Borrado': '✅ Borrado',
        '✅ Configuración borrada': '✅ Configuración borrada',
        'Se borraron todas las variables guardadas.': 'Se borraron todas las variables guardadas.',
        '¿Borrar esta opción?': '¿Borrar esta opción?',
        'volverá a su valor por omisión.': 'volverá a su valor por omisión.',
        'Se borrarán todas las variables guardadas y volverán a sus valores por omisión.': 'Se borrarán todas las variables guardadas y volverán a sus valores por omisión.',
        'Preguntar siempre': 'Preguntar siempre',
        'Automático': 'Automático',
    },
})
for _c, _d in I18N_ATAJO.items():
    I18N.setdefault(_c, {}).update(_d)
UX_ENTER = {"es": "Enter"}     # 2.0.8: solo español embebido; el resto se rellena desde el paquete en lang_pack_apply (Enter · Entrée · Invio)


def lang_parse(raw, fallback=None):
    """1.7.0: "en", "en-US", "en_US", "English", "português", "polski" → código (es/en/pt/fr/de/it/pl); None si no se reconoce."""
    if raw is None:
        return fallback
    s = str(raw).strip().lower().replace("_", "-")
    if not s or s in ("auto", "automatic", "automático", "automatico"):
        return fallback
    if s in LANG_ALIASES:
        return LANG_ALIASES[s]
    base = s.split("-")[0]
    if base in LANG_ALIASES:
        return LANG_ALIASES[base]
    return fallback


def lang_ask_pending(env=None):
    """1.7.1: True si DLPY_LANGUAGE vale «ask» o no está (el predeterminado): hay que preguntar el idioma en la escena. «auto» (el del sistema) o un código no preguntan."""
    v = str(_env_lookup(os.environ if env is None else env, "DLPY_LANGUAGE", "") or "").strip().lower()
    return v in ("", LANG_ASK, "preguntar", "?")


def _lang_detect():
    if lang_ask_pending():
        # 1.7.1: sin idioma elegido todo sale en español hasta que la escena pregunte (el LANG del sistema solo cuenta con DLPY_LANGUAGE=auto)
        return DEFAULT_LANG
    for key in ("DLPY_LANGUAGE", "LANG", "LANGUAGE"):
        v = env_get(key) if key.startswith("DLPY_") else os.environ.get(key)
        if v:
            c = lang_parse(v)
            if c:
                return c
    return DEFAULT_LANG


LANG = _lang_detect()


def lang_id_mode_parse(raw):
    """0/off · mark (color) · id (solo msgid) · both (id + mark: solo msgid, coloreado)."""
    value = str(raw if raw is not None else "0").strip().lower()
    if value in ("", "0", "off", "no", "false", "none", "disabled"):
        return "off"
    if value in ("mark", "color", "colour", "marcar", "colorido"):
        return "mark"
    if value in ("id", "show", "ver", "msgid"):
        return "id"
    if value in ("both", "all", "ambos", "todo"):
        return "both"
    return "off"


LANG_ID_MODE = lang_id_mode_parse(env_get("DLPY_TRANSLATION_DEBUG_MODE", "0"))


# cian eléctrico: nada más en la interfaz lo usa (naranja, magenta, verde, ámbar y rojo ya son de la paleta)
LANG_MARK_RGB = (0, 229, 255)


MARKED_TEXT = {}                 # textos traducidos (en minúsculas) que la escena debe pintar en el color de mark
_MARK_LINE_CACHE = {}


def lang_mark_register(plain):
    """Anota un texto traducido para colorearlo al pintar la escena (no se le añade ningún carácter)."""
    key = " ".join(_ANSI_RE.sub("", str(plain)).split()).lower()
    if len(key) >= 3 and key not in MARKED_TEXT:
        MARKED_TEXT[key] = True
        _MARK_LINE_CACHE.clear()
        while len(MARKED_TEXT) > 400:
            MARKED_TEXT.pop(next(iter(MARKED_TEXT)))


def lang_mark_cells(cells):
    """DLPY_TRANSLATION_DEBUG_MODE=mark/both en la escena: las celdas cuyo texto coincide (sin importar mayúsculas) con un texto anotado (el que se muestra: traducción con mark, msgid con both) pasan al color de mark.
    Es lo único que toca el color: el texto de las animaciones sigue siendo plano. Solo se llega aquí con mark/both."""
    if LANG_ID_MODE not in ("mark", "both") or not MARKED_TEXT or not cells:
        return cells
    rows = {}
    for (x, y), v in cells.items():
        if v and v[0]:
            rows.setdefault(y, []).append(x)
    out = dict(cells)
    for y, xs in rows.items():
        xs.sort()
        chars, pos, prev = [], [], None
        for x in xs:
            # hueco entre celdas: separa (una frase no cruza espacios vacíos)
            if prev is not None and x != prev + 1:
                chars.append(" ")
                pos.append(None)
            for ch in cells[(x, y)][0]:
                chars.append(ch)
                pos.append(x)
            prev = x
        line = "".join(chars).lower()
        hit = _MARK_LINE_CACHE.get(line)
        if hit is None:
            hit = set()
            for m in MARKED_TEXT:
                i = line.find(m)
                while i >= 0:
                    e = i + len(m)
                    if (i == 0 or not line[i - 1].isalnum()) and (e >= len(line) or not line[e].isalnum()):
                        hit.update(range(i, e))
                    i = line.find(m, e)
            if len(_MARK_LINE_CACHE) > 600:
                _MARK_LINE_CACHE.clear()
            _MARK_LINE_CACHE[line] = hit
        for i in hit:
            x = pos[i]
            if x is not None and cells[(x, y)][0] != " ":
                ch, _col, bg = cells[(x, y)][0], cells[(x, y)][1], cells[(x, y)][2]
                out[(x, y)] = (ch, LANG_MARK_RGB, bg)
    return out


def lang_mark_color(output):
    """DLPY_TRANSLATION_DEBUG_MODE=mark: pinta el propio texto traducido (cian eléctrico, color que el resto del script no usa), sin símbolos ni caracteres extra: el ancho no cambia y, si el texto ya trae
    colores, se reaplica el color tras cada reinicio para que se vea entero. Es solo ANSI de terminal: los JSON del atajo lo limpian (json_clean)."""
    rgb, basic = LANG_MARK_RGB, "96"
    seq = "\x1b[" + (f"38;2;{rgb[0]};{rgb[1]};{rgb[2]}" if TRUECOLOR else basic) + "m"
    return seq + output.replace(RESET, RESET + seq) + RESET


def lang_debug_output(output, source, enabled=True):
    """DLPY_TRANSLATION_DEBUG_MODE: off = nada · mark = colorea lo que se muestra (la traducción) · id = SOLO el msgid original, en plano (en lugar de la traducción) ·
    both = id + mark: solo el msgid original, coloreado. El color es siempre el mismo (mark) y se aplica a lo que se ve; la clave original y los datos dinámicos no se tocan."""
    output = str(output if output is not None else "")
    source = str(source if source is not None else "")
    mode = LANG_ID_MODE if enabled else "off"
    if not output or mode == "off":
        return output
    if mode in ("id", "both"):
        output = source or output                       # 1.9.2: con id/both nunca sale la traducción, solo el msgid
    if mode == "id":
        return output                                   # id solo muestra el msgid: sin color (el color es de mark/both)
    if USE_COLOR and _ANSI_RE.sub("", output).strip():
        _sc = globals().get("SCENE")
        if _sc and _sc.get("on"):
            # en la escena no hay ANSI en el texto (las animaciones lo rompen): se anota y se colorea al pintar (lang_mark_cells)
            lang_mark_register(output)
        else:
            output = lang_mark_color(output)
    return output


# 2.0.8: LANG_ENGLISH eliminado; ver LANG_NAMES_ES (nombres en español) junto a LANG_NAMES.


LANG_FLAGS = {"es": "🇪🇸", "en": "🇺🇸", "pt": "🇧🇷", "fr": "🇫🇷", "de": "🇩🇪", "it": "🇮🇹",
              "ru": "🇷🇺", "zh": "🇨🇳", "hi": "🇮🇳", "ar": "🇸🇦", "ja": "🇯🇵", "ko": "🇰🇷", "pl": "🇵🇱"}


# 1.7.0: «Idioma establecido» en cada idioma, para la alerta del atajo tras guardar la elección (se busca por el código elegido, no por el activo)
LANG_SET_TEXT = {"es": "Idioma establecido"}  # 2.0.8: solo español embebido; el resto se rellena desde el paquete en lang_pack_apply


# 1.7.0: «Idioma actual» en cada idioma: el título de la lista de elegir idioma es «<esto>: <nombre del idioma activo>» (lang_title)
LANG_CURRENT_TEXT = {"es": "Idioma actual"}  # 2.0.8: solo español embebido; el resto se rellena desde el paquete


# 1.7.1: «Seleccione idioma» en cada idioma: la escena que pregunta el idioma (DLPY_LANGUAGE=ask) lo va mostrando en todos, uno tras otro, bajo el dibujo
LANG_SELECT_TEXT = {"es": "Seleccione idioma"}  # 2.0.8: solo español embebido; el resto se rellena desde el paquete
# 2.0.8: "Seleccione idioma" ya está en I18N["es"]; no hace falta el bucle.


def languages_payload(current=None):
    """`--idiomas`: todos los idiomas disponibles para que Atajos arme la lista de elegir.
    «lang_labels» es lo que se ve (bandera + nombre, sin código y SIN el idioma actual); «lang_map» es el diccionario etiqueta → código
    (Atajos busca ahí lo que se eligió) y «lang_codes» va en paralelo a «lang_labels»; «lang_command» es el comando que guarda la elección
    (--config DLPY_LANGUAGE=código). «lang_current» / «lang_current_name» / «lang_title» dicen cuál está activo."""
    cur = current or LANG or DEFAULT_LANG
    langs = [{"code": c, "flag": LANG_FLAGS.get(c, ""), "name": LANG_NAMES.get(c, c), "name_es": LANG_NAMES_ES.get(c, c),
              "label": ("%s %s" % (LANG_FLAGS.get(c, ""), LANG_NAMES.get(c, c))).strip(),
              "label_full": ("%s %s (%s)" % (LANG_FLAGS.get(c, ""), LANG_NAMES.get(c, c), LANG_NAMES_ES.get(c, c))).strip(), "current": False,
              "set_text": LANG_SET_TEXT.get(c, LANG_SET_TEXT["es"])} for c in LANG_CODES if c != cur]
    return {"version": VERSION, "lang_current": cur, "lang_current_name": LANG_NAMES.get(cur, cur), "lang_default": DEFAULT_LANG,
            "lang_count": len(langs), "lang_ask": LANG_ASK, "lang_title": "%s: %s" % (LANG_CURRENT_TEXT.get(cur, LANG_CURRENT_TEXT["es"]), LANG_NAMES.get(cur, cur)),
            "lang_labels": [l["label"] for l in langs], "lang_codes": [l["code"] for l in langs],
            "lang_map": {l["label"]: l["code"] for l in langs}, "lang_list": langs,
            "lang_command": "--config DLPY_LANGUAGE=<code>",
            # «Idioma establecido» en el idioma activo
            "lang_set": LANG_SET_TEXT.get(cur, LANG_SET_TEXT["es"]),
            # código → «Idioma establecido» en ESE idioma: la alerta busca ahí el LangCode elegido
            "lang_set_map": dict(LANG_SET_TEXT),
            # paralelo a lang_codes
            "lang_set_texts": [LANG_SET_TEXT.get(c, LANG_SET_TEXT["es"]) for c in (l["code"] for l in langs)]}


def print_languages():
    """`python dlpy.py --idiomas` (alias `--langs`): una línea de JSON ASCII en la salida y nada más (sin banner ni animaciones)."""
    sys.stdout.write(json.dumps(json_clean(languages_payload()), ensure_ascii=True, separators=(",", ":")) + "\n")
    sys.stdout.flush()
    return 0


ATAJO_VERSION = 1  # 2.1.0: esquema del JSON de --atajo (el atajo comprueba que exista; si no, ofrece actualizar dlpy.py)


def atajo_ui():
    """2.1.0: textos del atajo en el idioma activo: cada clave es un msgid español de I18N_ATAJO. Los mapas
    etiqueta → clave son lo que usa el atajo para ramificar sin comparar textos traducidos."""
    def _u(msgid):
        return t_display(msgid, _debug=False)  # sin marcas de DLPY_TRANSLATION_DEBUG_MODE: Atajos compara etiquetas exactas

    menu = [("open", "➡️ Abrir"), ("link", "➡️ Ingresar Link"), ("update", "ℹ️ Buscar Actualización"),
            ("language", "🌎 Idioma"), ("config", "⚙️ Configurar variables"), ("clipboard", "📋 Portapapeles"),
            ("reinstall", "🛠️ Reinstalar/Instalar"), ("system", "🩺 Sistema / Diagnóstico")]
    system = [("system", "🖥 Sistema"), ("profile", "⏱ Perfil"), ("versions", "📦 Versiones"), ("back", "⬅ Volver")]
    detail = [("change", "✏️ Cambiar valor"), ("delete", "🗑 Borrar (volver a por omisión)"), ("back", "⬅ Cancelar")]
    return {
        "menu_prompt": _u("DLpy"),
        "menu_labels": [_u(m) for _k, m in menu],
        "menu_map": {_u(m): k for k, m in menu},
        "link_prompt": _u("Link"),
        "link_error_title": _u("⚠️ Error:"),
        "audio_prompt": _u("ℹ️ Audio principal"),
        "extra_prompt": _u("🌎 Adicional"),
        "update_needed_title": _u("⚠️ Actualiza dlpy.py"),
        "update_needed_msg": _u("Este atajo necesita un dlpy.py más nuevo (con --atajo). Se baja la última versión desde GitHub."),
        "reinstall_done": _u("✅ dlpy.py reinstalado"),
        "installed_title": _u("✅ Se instaló dlpy.py"),
        "installed_msg": _u("No existía, se bajó la última versión desde GitHub.\n\n¿Continuar con ejecución?"),
        "system_prompt": _u("🩺 Sistema / Diagnóstico"),
        "system_labels": [_u(m) for _k, m in system],
        "system_map": {_u(m): k for k, m in system},
        "config_prompt": _u("⚙️ Elige una opción · ● guardada · ✗ inválida · ○ por omisión"),
        "config_forget_label": _u("🗑 Borrar todas…"),
        "config_done_label": _u("✅ Listo / Salir"),
        "config_detail_labels": [_u(m) for _k, m in detail],
        "config_detail_map": {_u(m): k for k, m in detail},
        "config_custom_label": _u("✏️ Escribir otro valor…"),
        "config_ask_value": _u("Escribe el valor nuevo"),
        "config_ask_choice": _u("Elige el valor nuevo"),
        "config_saved_title": _u("✅ Guardado"),
        "config_deleted_title": _u("✅ Borrado"),
        "config_forget_title": _u("¿Borrar todas las variables guardadas?"),
        "config_forget_msg": _u("Se borrarán todas las variables guardadas y volverán a sus valores por omisión."),
        "config_forget_done": _u("✅ Configuración borrada"),
        "config_forget_done_msg": _u("Se borraron todas las variables guardadas."),
        "config_delete_title": _u("¿Borrar esta opción?"),
        "config_delete_msg": _u("volverá a su valor por omisión."),
    }


# 2.1.0: las 15 opciones sí/no de config_validate (flag01), en el mismo orden que allí.
_CONFIG_FLAG_NAMES = ("DLPY_DEBUG_LOGGING", "DLPY_COLOR_TRUECOLOR", "DLPY_ANIMATIONS_ENABLED", "DLPY_PROGRESS_BAR_CLASSIC",
                      "DLPY_ANALYZE_ANIMATION_ENABLED", "DLPY_PIP_USES_SCENE", "DLPY_GLITCH_EFFECT_ENABLED", "DLPY_TEXT_CALM_MODE",
                      "DLPY_CONVERT_LIGHT_ANIMATION", "DLPY_HIDE_SCRIPT_FILES", "DLPY_CLEAR_PURGE_SCROLLBACK", "DLPY_SCENE_OUTRO_ENABLED",
                      "DLPY_CLIPBOARD_READ_LINK_ENABLED", "DLPY_SINGLE_INSTANCE_WATCHDOG", "DLPY_MEDIA_TAGS_ENABLED")


def config_choices(name):
    """2.1.0: (kind, choices, choice_labels) de una opción para el atajo: flag = 1/0 · choice = lista cerrada ·
    choice_or_text = lista + «escribir otro» · number/text = escribir. Las etiquetas ya van traducidas."""
    n = config_canonical(name) or str(name or "")
    if n in _CONFIG_FLAG_NAMES:
        return "flag", ["1", "0"], ["1", "0"]
    if n == "DLPY_CONVERT_PRESET":
        return "choice", ["fast", "high", "best", "prores"], ["fast", "high", "best", "prores"]
    if n in ("DLPY_CLEAR_MODE", "DLPY_CLEAR_FIRST_MODE"):
        return "choice", ["auto", "home", "down", "purge-first", "reset"], ["auto", "home", "down", "purge-first", "reset"]
    if n == "DLPY_FINISH_DELIVERY_MODE":
        return "choice", ["view", "shortcut"], ["view", "shortcut"]
    if n == "DLPY_SHORTCUT_DIRECT_LIST_MODE":
        return "choice", ["0", "1", "all"], ["0", "1", "all"]
    if n == "DLPY_TRANSLATION_DEBUG_MODE":
        return "choice", ["0", "mark", "id", "both"], ["0", "mark", "id", "both"]
    if n == "DLPY_LANGUAGE":
        codes = ["ask", "auto"] + list(LANG_CODES)
        labels = [t_display("Preguntar siempre", _debug=False) + " (ask)",
                  t_display("Automático", _debug=False) + " (auto)"]
        labels += [("%s %s (%s)" % (LANG_FLAGS.get(c, ""), LANG_NAMES.get(c, c), c)).strip() for c in LANG_CODES]
        return "choice", codes, labels
    if n == "DLPY_UPDATE_CHECK_INTERVAL":
        return "choice_or_text", ["0", "on", "30m", "6h", "1d", "1w"], ["0", "on", "30m", "6h", "1d", "1w"]
    if n == "DLPY_SCENE_RHYTHM":
        return "choice_or_text", ["wait", "real"], ["wait", "real"]
    if n in ("DLPY_TOP_BAR_FIELDS", "DLPY_BOTTOM_BAR_FIELDS"):
        return "choice_or_text", ["0", "1"], ["0", "1"]
    if n == "DLPY_SUBTITLE_LANGS":
        return "choice_or_text", ["0", "all"], ["0", "all"]
    if n in ("DLPY_DEBUG_LOG_KEEP_COUNT", "DLPY_LIST_VISIBLE_ROWS", "DLPY_UI_LINES", "DLPY_TERMINAL_WIDTH_COLS",
             "DLPY_ANIMATION_LOOP_SECS", "DLPY_ANALYZE_RESULT_TTL_SECS", "DLPY_STORAGE_LIMIT_MB",
             "DLPY_SHORTCUT_ANALYZE_TIMEOUT_SECS", "DLPY_SHORTCUT_MODE_TIMEOUT_SECS", "DLPY_SHORTCUT_MODE_HARD_TIMEOUT_SECS",
             "DLPY_CONCURRENT_FRAGMENTS"):
        return "number", [], []
    return "text", [], []


def atajo_config_payload():
    """2.1.3: opciones de --config para el atajo con etiquetas amigables y label_map.
    labels: lista para Choose from List (solo opciones elegibles: «Elegir de la lista» no admite filas no seleccionables,
    así que no se mezclan separadores de grupo; el orden sí sigue los grupos).
    label_map: etiqueta visible → nombre técnico DLPY_*.
    by_name: datos por nombre técnico (kind, choices, detail, …)."""
    # Título corto en español (msgid) por opción; si falta, se deriva de la descripción.
    titles = {
        "DLPY_DEBUG_LOGGING": "Depuración (logs extra)",
        "DLPY_DEBUG_LOG_KEEP_COUNT": "Logs de depuración a conservar",
        "DLPY_LIST_VISIBLE_ROWS": "Filas visibles en listas",
        "DLPY_UI_LINES": "Líneas de la interfaz",
        "DLPY_TERMINAL_WIDTH_COLS": "Ancho del terminal",
        "DLPY_COLOR_TRUECOLOR": "Color truecolor",
        "DLPY_ANIMATIONS_ENABLED": "Animaciones",
        "DLPY_PROGRESS_BAR_CLASSIC": "Barra de progreso clásica",
        "DLPY_ANALYZE_ANIMATION_ENABLED": "Animación al analizar enlace",
        "DLPY_PIP_USES_SCENE": "Pip usa la escena",
        "DLPY_GLITCH_EFFECT_ENABLED": "Efecto glitch",
        "DLPY_TEXT_CALM_MODE": "Textos más legibles",
        "DLPY_SCENE_RHYTHM": "Ritmo de escenas",
        "DLPY_ANALYZE_RESULT_TTL_SECS": "Validez del análisis (s)",
        "DLPY_ANIMATION_LOOP_SECS": "Duración del loop de animación",
        "DLPY_CONVERT_LIGHT_ANIMATION": "Conversión ligera",
        "DLPY_CONVERT_PRESET": "Preset de conversión",
        "DLPY_HIDE_SCRIPT_FILES": "Ocultar archivos del script",
        "DLPY_CLEAR_PURGE_SCROLLBACK": "Purgar scrollback al limpiar",
        "DLPY_CLEAR_FIRST_MODE": "Primer borrado al arrancar",
        "DLPY_CLEAR_MODE": "Modo de limpieza",
        "DLPY_SCENE_OUTRO_ENABLED": "Cierre de escena",
        "DLPY_TOP_BAR_FIELDS": "Franja superior",
        "DLPY_BOTTOM_BAR_FIELDS": "Franja inferior",
        "DLPY_LANGUAGE": "Idioma de la interfaz",
        "DLPY_UPDATE_CHECK_INTERVAL": "Intervalo de comprobación de actualizaciones",
        "DLPY_CLIPBOARD_READ_LINK_ENABLED": "Leer link del portapapeles",
        "DLPY_SINGLE_INSTANCE_WATCHDOG": "Una sola ejecución a la vez",
        "DLPY_STORAGE_LIMIT_MB": "Límite de almacenamiento (MB)",
        "DLPY_SHORTCUT_ANALYZE_TIMEOUT_SECS": "Tope de análisis en el atajo (s)",
        "DLPY_SHORTCUT_MODE_TIMEOUT_SECS": "Tope de --scm (s)",
        "DLPY_SHORTCUT_MODE_HARD_TIMEOUT_SECS": "Tope duro de --scm (s)",
        "DLPY_CONCURRENT_FRAGMENTS": "Fragmentos concurrentes",
        "DLPY_SUBTITLE_LANGS": "Idiomas de subtítulos",
        "DLPY_MEDIA_TAGS_ENABLED": "Etiquetas de medios (título/carátula)",
        "DLPY_YTDLP_EXTRA_ARGS": "Argumentos extra de yt-dlp",
        "DLPY_DEBUG_LOG_FILE_ENABLED": "Guardar log de depuración en archivo",
        "DLPY_TRANSLATION_DEBUG_MODE": "Diagnóstico de traducción",
        "DLPY_SCENE_MODE": "Modo de escena",
    }
    # Orden de grupos en la lista del atajo (nombre técnico → grupo).
    groups = (
        ("Depuración", ("DLPY_DEBUG_LOGGING", "DLPY_DEBUG_LOG_FILE_ENABLED", "DLPY_DEBUG_LOG_KEEP_COUNT", "DLPY_TRANSLATION_DEBUG_MODE")),
        ("Interfaz", ("DLPY_LANGUAGE", "DLPY_LIST_VISIBLE_ROWS", "DLPY_UI_LINES", "DLPY_TERMINAL_WIDTH_COLS", "DLPY_COLOR_TRUECOLOR",
                      "DLPY_TOP_BAR_FIELDS", "DLPY_BOTTOM_BAR_FIELDS", "DLPY_TEXT_CALM_MODE")),
        ("Animación y escenas", ("DLPY_ANIMATIONS_ENABLED", "DLPY_PROGRESS_BAR_CLASSIC", "DLPY_ANALYZE_ANIMATION_ENABLED",
                                 "DLPY_GLITCH_EFFECT_ENABLED", "DLPY_SCENE_RHYTHM", "DLPY_SCENE_MODE", "DLPY_ANIMATION_LOOP_SECS",
                                 "DLPY_SCENE_OUTRO_ENABLED", "DLPY_PIP_USES_SCENE", "DLPY_CONVERT_LIGHT_ANIMATION")),
        ("Terminal", ("DLPY_CLEAR_MODE", "DLPY_CLEAR_FIRST_MODE", "DLPY_CLEAR_PURGE_SCROLLBACK", "DLPY_HIDE_SCRIPT_FILES")),
        ("Descargas y medios", ("DLPY_CONVERT_PRESET", "DLPY_CONCURRENT_FRAGMENTS", "DLPY_SUBTITLE_LANGS", "DLPY_MEDIA_TAGS_ENABLED",
                                "DLPY_STORAGE_LIMIT_MB", "DLPY_YTDLP_EXTRA_ARGS", "DLPY_ANALYZE_RESULT_TTL_SECS")),
        ("Atajo y sistema", ("DLPY_CLIPBOARD_READ_LINK_ENABLED", "DLPY_SINGLE_INSTANCE_WATCHDOG", "DLPY_UPDATE_CHECK_INTERVAL",
                             "DLPY_SHORTCUT_ANALYZE_TIMEOUT_SECS", "DLPY_SHORTCUT_MODE_TIMEOUT_SECS", "DLPY_SHORTCUT_MODE_HARD_TIMEOUT_SECS")),
    )
    data = _read_env_json(ENV_FILE) if isinstance(ENV_FILE, str) else {}
    if not isinstance(data, dict):
        data = {}
    by_name = {}
    rows = list(config_rows(data))
    row_by = {r[0]: r for r in rows}
    for name, default, desc, saved in rows:
        kind, choices, choice_labels = config_choices(name)
        valid = True
        if saved is not None:
            valid = bool(config_validate(name, saved)[0])
        if saved is not None:
            mark, display = ("●" if valid else "✗"), str(saved)
        else:
            mark, display = "○", "[%s]" % (default if default != "" else "—")
        title = titles.get(name) or (desc.split("·")[0].split(":")[0].strip()[:40] or name)
        title = t_display(title, _debug=False)
        label = "%s %s — %s" % (mark, title, display)
        detail = "%s\n%s: %s\n%s: %s\n%s: %s" % (
            t_display(desc, _debug=False),
            t_display("Guardado", _debug=False), saved if saved is not None else "—",
            t_display("Por omisión", _debug=False), default if default != "" else "—",
            t_display("Nombre técnico", _debug=False), name)
        old = config_old_name(name)
        if old:
            detail += "\n%s: %s" % (t_display("Nombre anterior", _debug=False), old)
        opt = {"name": name, "default": default, "desc": t_display(desc, _debug=False), "saved": saved, "valid": valid,
               "old": old, "kind": kind, "choices": choices, "choice_labels": choice_labels,
               "choice_map": {lab: val for lab, val in zip(choice_labels, choices)},
               "label": label, "title": title, "detail": detail}
        by_name[name] = opt
    # Lista ordenada por grupos (sin filas separadoras: en el atajo todo lo que sale en la lista se puede tocar);
    # opciones no agrupadas al final.
    seen = set()
    labels = []
    label_map = {}
    for _group_title, names in groups:
        chunk = [n for n in names if n in by_name]
        if not chunk:
            continue
        for n in chunk:
            lab = by_name[n]["label"]
            labels.append(lab)
            label_map[lab] = n
            seen.add(n)
    for name, _d, _desc, _s in rows:
        if name in seen:
            continue
        lab = by_name[name]["label"]
        labels.append(lab)
        label_map[lab] = name
    return {"labels": labels, "label_map": label_map, "by_name": by_name,
            "saved_count": len(data), "file": CONFIG_NAME}




def atajo_payload():
    """2.1.0: `--atajo`: todo lo que el atajo necesita en un JSON (textos, idiomas y opciones de config)."""
    payload = dict(languages_payload())
    payload["atajo_version"] = ATAJO_VERSION
    payload["ui"] = atajo_ui()
    payload["config"] = atajo_config_payload()
    return payload


def print_atajo():
    """`python dlpy.py --atajo` (alias `--shortcut`): una línea de JSON ASCII en la salida y nada más (sin banner ni animaciones)."""
    sys.stdout.write(json.dumps(json_clean(atajo_payload()), ensure_ascii=True, separators=(",", ":")) + "\n")
    sys.stdout.flush()
    return 0


def wants_atajo(args):
    """¿Se pidió --atajo / --shortcut? Acepta rayas largas («—atajo»)."""
    return _wants(args, "atajo") or _wants(args, "shortcut")


def atajo_selftest():
    """2.1.0: comprobaciones de --atajo para el módulo de selftest (modules/dlpy_selftest.py): (nombre, ok, detalle)."""
    checks = []
    try:
        ui = atajo_ui()
    except Exception as e:
        return [("atajo ui: se construye", False, str(e))]
    str_vals = [v for v in ui.values() if isinstance(v, str)]
    checks.append(("atajo ui: sin textos vacíos", all(v for v in str_vals), "%d textos" % len(str_vals)))
    checks.append(("atajo menú: etiquetas únicas", len(set(ui["menu_labels"])) == len(ui["menu_labels"]), "%d opciones" % len(ui["menu_labels"])))
    checks.append(("atajo menú: mapa = etiquetas", set(ui["menu_map"]) == set(ui["menu_labels"]), "claves: %s" % ",".join(sorted(ui["menu_map"].values()))))
    checks.append(("atajo sistema: mapa = etiquetas", set(ui["system_map"]) == set(ui["system_labels"]), "claves: %s" % ",".join(sorted(ui["system_map"].values()))))
    checks.append(("atajo detalle: mapa = etiquetas", set(ui["config_detail_map"]) == set(ui["config_detail_labels"]), "claves: %s" % ",".join(sorted(ui["config_detail_map"].values()))))
    try:
        cfg = atajo_config_payload()
    except Exception as e:
        return checks + [("atajo config: se construye", False, str(e))]
    checks.append(("atajo config: cubre CONFIG_OPTIONS", all(n in cfg["by_name"] for n, _d, _t in CONFIG_OPTIONS),
                   "%d opciones" % len(cfg["by_name"])))
    checks.append(("atajo config: label_map cubre etiquetas",
                   isinstance(cfg.get("label_map"), dict)
                   and set(cfg["label_map"]) == set(cfg["labels"])
                   and not any(l.startswith("──") for l in cfg["labels"]),
                   "%d etiquetas" % len(cfg.get("label_map") or {})))
    checks.append(("atajo config: label_map → by_name",
                   all(v in cfg["by_name"] for v in (cfg.get("label_map") or {}).values()), "nombres ok"))
    checks.append(("atajo config: choice_map = choice_labels",
                   all(set(o["choice_map"]) == set(o["choice_labels"]) and len(o["choice_map"]) == len(o["choice_labels"])
                       for o in cfg["by_name"].values()), "etiqueta → valor"))
    lang_opt = cfg["by_name"].get("DLPY_LANGUAGE", {})
    checks.append(("atajo config: idioma con ask/auto", list(lang_opt.get("choices", []))[:2] == ["ask", "auto"],
                   "choices: %s" % ",".join(list(lang_opt.get("choices", []))[:4])))
    try:
        pay = atajo_payload()
        checks.append(("atajo: payload con idiomas + ui + config",
                       all(k in pay for k in ("lang_labels", "lang_map", "lang_set_map", "ui", "config")) and pay.get("atajo_version") == ATAJO_VERSION,
                       "atajo_version=%s" % pay.get("atajo_version")))
    except Exception as e:
        checks.append(("atajo: payload con idiomas + ui + config", False, str(e)))
    es = dict.__getitem__(I18N_ATAJO, "es") or {}
    checks.append(("atajo: I18N_ATAJO con los msgid", len(es) >= 39, "%d msgid" % len(es)))
    return checks


def wants_languages(args):
    """¿Se pidió --idiomas / --langs? Acepta rayas largas («—idiomas»)."""
    return _wants(args, "idiomas") or _wants(args, "langs")


def set_lang(raw, quiet_msg=False):
    """1.7.0: cambia el idioma en esta ejecución y lo deja en DLPY_LANGUAGE (lo guarda la configuración).
    2.0.6: confirma en verde (mint) con «Idioma establecido» en el idioma aplicado, salvo quiet_msg."""
    global LANG
    code = lang_parse(raw) or DEFAULT_LANG
    LANG = code
    os.environ["DLPY_LANGUAGE"] = code
    os.environ.pop("DLPY_LANG", None)  # 2.0.9: no dejar el alias viejo con un valor distinto
    if not quiet_msg:
        try:
            msg = LANG_SET_TEXT.get(code) or LANG_SET_TEXT.get("es") or "Idioma establecido"
            if SCENE.get("on"):
                # con escena viva el aviso va en el estado (verde vía label_ok)
                scene_status(t_display("Idioma") + " · " + msg)
                SCENE["label_ok"] = True
            else:
                _say("mint", msg, "✓")
        except Exception as _ign:
            ignore("set_lang: aviso idioma", _ign)
    return code



# ── localización de números y fechas (punto de salida) ──
_LOCALE_COMMA = frozenset({"pt", "fr", "de", "it", "ru", "pl"})  # 2.0.8: decimal con coma; es mantiene punto, como siempre; pl con coma
_DATE_FMT = {
    "en": "%Y-%m-%d %H:%M", "pt": "%d/%m/%Y %H:%M", "fr": "%d/%m/%Y %H:%M",
    "de": "%d.%m.%Y %H:%M", "it": "%d/%m/%Y %H:%M", "es": "%d/%m/%Y %H:%M",
    "ru": "%d.%m.%Y %H:%M", "zh": "%Y/%m/%d %H:%M", "hi": "%d/%m/%Y %H:%M",
    "ar": "%Y-%m-%d %H:%M", "ja": "%Y/%m/%d %H:%M", "ko": "%Y/%m/%d %H:%M", "pl": "%d.%m.%Y %H:%M",
}
_DATE_FMT_SHORT = {
    "en": "%Y-%m-%d", "pt": "%d/%m/%Y", "fr": "%d/%m/%Y", "de": "%d.%m.%Y",
    "it": "%d/%m/%Y", "es": "%d/%m/%Y", "ru": "%d.%m.%Y", "zh": "%Y/%m/%d",
    "hi": "%d/%m/%Y", "ar": "%Y-%m-%d", "ja": "%Y/%m/%d", "ko": "%Y/%m/%d", "pl": "%d.%m.%Y",
}


def sec_unit():
    """Unidad de segundos para pantalla: «s» en español (como siempre); en el resto, la del catálogo."""
    return "s" if (LANG or DEFAULT_LANG) == "es" else t_display("seg")


def loc_num(n, decimals=None):
    """Número para pantalla: coma decimal en pt/fr/de/it/ru/pl; punto en es/en/zh/ja/ko/ar y resto. 2.0.8: es mantiene punto, pl con coma."""
    try:
        x = float(n)
    except (TypeError, ValueError):
        return str(n)
    if decimals is None:
        s = ("%d" % int(x)) if x == int(x) else ("%.10g" % x)
    else:
        s = ("%." + str(int(decimals)) + "f") % x
    if (LANG or DEFAULT_LANG) in _LOCALE_COMMA:
        s = s.replace(".", ",")
    return s


def loc_date(ts=None, short=False):
    """Fecha/hora localizada según DLPY_LANGUAGE; `ts` epoch o None = ahora."""
    import time as _t
    if ts is None:
        tt = _t.localtime()
    else:
        try:
            tt = _t.localtime(float(ts))
        except (TypeError, ValueError):
            return str(ts)
    fmt = (_DATE_FMT_SHORT if short else _DATE_FMT).get(LANG or DEFAULT_LANG) or "%Y-%m-%d %H:%M"
    return _t.strftime(fmt, tt)



# ── plantillas de frases completas con variables (orden de palabras propio de cada idioma) ──
_FMT_RX = (
    ("upd", re.compile(r"^Actualización de (.+?): (.+)$")),
    ("next", re.compile(r"^Se usará la (\S+) la próxima vez que abras DLpy\.$")),
    ("remux", re.compile(r"^Remux a (\S+): video sin recodificar \(puede no verse en Apple\)$")),
    ("conv", re.compile(r"^Convertido a (\S+) compatible con Apple(.*)$")),
    ("reenc", re.compile(r"^Recodificar el video a (\S+) puede tardar bastante en el (.+)\.$")),
)
I18N_FMT = LangTable("fmt", {
    "es": {"upd": "Actualización de {0}: {1}", "next": "Se usará la {0} la próxima vez que abras DLpy.",
           "remux": "Remux a {0}: video sin recodificar (puede no verse en Apple)", "conv": "Convertido a {0} compatible con Apple{1}",
           "reenc": "Recodificar el video a {0} puede tardar bastante en el {1}."},
})
I18N_DEVICE = LangTable("device", {"es": "equipo"})


class _SpanishTranslations(gettext.NullTranslations):
    """Catálogo español embebido (identidad): respaldo por mensaje para todos los paquetes descargables."""

    def pgettext(self, context, message):
        if context == "ui":
            return dict.__getitem__(I18N, "es").get(message, message)
        if context == "noun":
            return message
        if context == "template" or context.startswith("format:"):
            return message
        if context.startswith("fragment:"):
            return message
        return message

    def gettext(self, message):
        return dict.__getitem__(I18N, "es").get(message, message)

    def npgettext(self, context, singular, plural, n):
        try:
            count = int(n)
        except (TypeError, ValueError, OverflowError):
            count = 0
        if context == "noun:files":
            return singular if count == 1 else plural
        return singular if count == 1 else plural


_SPANISH_TRANSLATION = _SpanishTranslations()
LANG_TRANSLATIONS["es"] = _SPANISH_TRANSLATION


# ─────────────────────── Frases con huecos ({0}, {1}…) en los 11 idiomas (1.7.3) ───────────────────────
# El español canónico lleva los valores intercalados («…con {0}; se usará…»); el catálogo solo entiende frases enteras o trozos, así que esas frases salían mitad
# en español. Cada fila: español con {n} (las traducciones llegan en el .mo). Sin punto final: si el original lo traía, se añade al traducir (「。」 en zh / ja).
_TPL_LANGS = ()  # 2.0.8: ningún idioma embebido
_TPL_ROWS = (
    'No hay video compatible con {0}; se usará el mejor disponible',
    'Conversión rápida (~{0} s estimados): se convierte sin preguntar',
    'Conversión rápida (~{0} s estimados): se convierte sin preguntar y se conservan {1} bits',
    'Conversión rápida (~{0} s estimados): se convierte sin preguntar y se conservan {1} bits (origen de {2})',
    'Conversión rápida (solo remux/audio): se convierte sin preguntar',
    'Conversión larga (~{0} s): la escena preguntará justo antes de convertir (Enter convertir · r remux · n conservar original)',
    'El archivo descargado es de {0} bits: se conservan',
    'El archivo descargado es de {0} bits: se conservan como {1} bits (lo máximo que reproduce Apple)',
    'No se pudo instalar la actualización: {0}',
    'No se pudo instalar la {0}: {1}',
    'pip terminó con error (código {0}) al instalar {1}',
    'Descargando la {0} desde {1}',
    'Enviando a {0}',
    'Subtítulos: {0}',
    'Enviando el código v{0} ({1} · {2}) a {3}',
    'Avance guardado ({0}): repite el mismo enlace y formato para reanudar',
    'Avance guardado ({0}): al repetirlo se reanuda solo',
    'No se pudo instalar yt-dlp-ejs; YouTube puede mostrar menos formatos',
    'Opción inválida: T, números del 1 al {0}, D n.º o Enter',
    'La {0} ({1}) es idéntica a la instalada; no hay nada que cambiar',
    'No se detectó {0} tras instalarlo',
    'Actualización {0} -> {1}: {2} reiniciado, descargas conservadas',
    'La {0} del Release no es más nueva que la {1}, de la que bajaste a propósito',
    'Ancho del terminal: {0}',
    'Idioma {0} no disponible sin conexión; se usa español',
    'Descargando idioma {0}',
    'Comprobando idioma {0}',
    'Comprobando idioma {0} · actualización disponible',
    'Comprobando idioma {0} · al día',
    'Descargando idioma {0} · {1}',
    '¿Incluir pistas adicionales?',
    '¿Instalar {0}?',
    '¿Quedarte en la {0} hasta que salga una más nueva?',
    '¿Con changelog?',
    '¿Descargar de nuevo?',
    '¿Conservar {0} bits?',
    '¿Usarlo?',
    '¿Borrar todas las variables guardadas?',
    '¿Actualizar {0}?',
    'Todos los changelog',
    'Ver todo',
    'CHANGELOG {0} · se instalará',
    'Notas de versión {0}',
    'Línea de prueba {0}',
    'Modo {0}',
    '{0} movido',
    '{0} movidos',
    '{0} borrado',
    '{0} borrados',
    'Idioma {0}: {1}',
    'Esperado ({0}): {1}',
    'Obtenido: {0}',
    'Hay una versión nueva de DLpy: {0} → {1} (Release)',
    'Con 10 bits se pierde algo de precisión de color; con 8 más. {0}',
    'Descartadas: {0}',
    'No se pudieron guardar las variables DLPY_* en {0}',
    'Predeterminada: {0} · {1}',
    'No se pudo convertir el archivo existente: {0}',
    'No se pudo lanzar pip para {0}: {1}',
    'No se pudo escribir el changelog: {0}',
    'Versión {0} → {1}',
    'Caché stream {0}: {1}',
    'Reutilizado de caché: formato {0} ({1})',
    'No se pudo leer el código: {0}',
    'DLPY_YTDLP_EXTRA_ARGS inválido: {0}',
    'Reintentando análisis ({0})',
    'Error al descargar: {0}',
    'Usando {0}',
    'No se pudo cachear stream {0}: {1}',
    'Error al analizar: {0}',
    'No se pudo ajustar la pista predeterminada: {0}',
    'No se pudo convertir a compatible Apple: {0}',
    'No se pudo sembrar {0}: {1}',
    'Opción 1-{0}',
    'DLpy {0} · instalada ({1})',
    'Estimación ~{0} s a 8 bits; con más bits tarda algo más',
    'A 8 bits: {0}, pero pierde precisión de color. {1}',
    '(+{0} líneas más: «m»)',
    '(+{0} más: «m»)',
    '(+{0} más antiguas sin mostrar)',
    'DLpy {0} · no se pudo comprobar la última versión (Releases de GitHub)',
    'DLpy {0} · versión local más reciente que la del último Release ({1})',
    'Se volverá a preguntar en la próxima comprobación ({0}) o con --actualizar',
    'Changelog actualizado desde los Releases de GitHub ({0} versión/es)',
    'Movidos a papelera: {0} archivo(s) de más de {1} días. Se borrarán tras {2} días en trash',
    'Papelera: {0} archivo(s) borrado(s) definitivamente (más de {1} días en ella)',
    'Instalar la {0}',
    'Instalar la {0} para la próxima vez',
    'Instalar la {0} y ejecutarla ahora',
    'No se pudo obtener la {0} (descarga fallida, archivo no válido o SHA-256 que no coincide)',
    '{0} sin terminar (caducan a las 24 h)',
    'Caché de streams: {0} archivo(s) reutilizado(s) (< 24 h)',
    'Reanudando: {0} ya descargados',
    '{0} · Release ≠ instalada (código distinto: -{1} +{2} líneas)',
    'DLpy {0} · bajaste a propósito desde la {1}; no se ofrece la {2} del Release',
    'Cuando haya una versión más nueva que la {0} se avisará. Con --actualizar puedes instalarla de todos modos',
    'Bajaste de la {0} a la {1}. No se ofrecerá actualizar hasta que haya un Release con una versión más nueva que la {2}; con --actualizar puedes volver a instalarla',
    'Bajaste de la {0} a la {1}. En el próximo arranque se volverá a ofrecer actualizar',
    'DLPY_CLEAR_MODE = {0} (guardado; vale desde el siguiente comando)',
    'Configuración borrada ({0} guardada(s))',
    'Estimación ~{0} s (umbral de pregunta: {1} s)',
    '{0} {1} · hay una {2} (rechazada; --actualizar la instala)',
    'Almacenamiento {0} supera límite {1} pero se conserva (DLPY_KEEP_DOWNLOADS_OVER_LIMIT=1)',
    'Trash: {0} borrado: {1} d en papelera (límite {2})',
    '{0} no disponible; probando {1}',
    '{0} es obligatoria: sin ella DLpy no puede continuar',
    '{0} ✓ · {1} ~ · {2} ✗ · {3} – (no aplica)',
    'Puede verse con bandas; el {0} se pasa a SDR con tone mapping (tarda ~3 veces más) y pierde el brillo extra del HDR',
    'No se pudo abrir el atajo «{0}»: el archivo está en dlpy_files',
    'Enter = {0}',
)
# 1.9.4: huecos {n} que son, a su vez, frases conocidas y se traducen de forma recursiva (el resto de huecos pasa tal cual: nombres, rutas, versiones, errores externos).
_TPL_NESTED = {
    'Idioma {0}: {1}': (1,),
    'Con 10 bits se pierde algo de precisión de color; con 8 más. {0}': (0,),
    'A 8 bits: {0}, pero pierde precisión de color. {1}': (0, 1),
}
_TPL_RX = {}                          # 1.9.0: por idioma (cada paquete trae sus filas)


def _tpl_rows(code):
    """1.9.0: [(español con {n}, traducción)] del idioma: las del español viajan en el script (identidad); las demás, en su paquete."""
    if code == "es":
        return [(es, es) for es in _TPL_ROWS]
    lang_pack_load(code)
    return _TPL_PACK.get(code) or []


def _t_rows(text, code):
    """1.7.3: traduce una frase con huecos (_TPL_ROWS). None si no encaja o el idioma no tiene filas. Los valores ({0}…) pasan tal cual.
    1.9.4: la plantilla más específica va primero («Instalar la {0}» no se come a «Instalar la {0} y ejecutarla ahora») y los huecos de _TPL_NESTED se traducen recursivamente."""
    if not text:
        return None
    rxs = _TPL_RX.get(code)
    if rxs is None:
        rxs = []
        for es, tr in _tpl_rows(code):
            parts = re.split(r"\{(\d)\}", es)
            rx = "".join(re.escape(x) if i % 2 == 0 else "(.+?)" for i, x in enumerate(parts))
            rxs.append((len("".join(parts[0::2])), re.compile("^" + rx + "$", re.S), tr, [int(x) for x in parts[1::2]], _TPL_NESTED.get(es, ()), es))
        rxs.sort(key=lambda row: -row[0])
        if rxs:
            _TPL_RX[code] = rxs
    core = text.rstrip(".")
    suf = text[len(core):]
    for _spec, rx, tr, order, nested, es_template in rxs:
        m = rx.match(core)
        if not m:
            continue
        vals = {n: v for n, v in zip(order, m.groups())}
        # Las plantillas de contadores solo aceptan una cantidad numérica.
        # Sin esta comprobación, «{0} borrado» podía capturar por error toda
        # la frase anterior («Limpiando · 3 movidos · 1») y traducirla a medias.
        if es_template in ("{0} movido", "{0} movidos", "{0} borrado", "{0} borrados"):
            if not re.fullmatch(r"\d+", vals.get(0, "").strip()):
                continue
        for n in nested:
            if n in vals:
                vals[n] = t_display(vals[n], lang=code, _debug=False)
        out = tr.format(*[vals[i] for i in range(max(vals) + 1)] if vals else ())
        if suf == "." and code in ("zh", "ja"):
            return out + "。"
        return out + suf
    return None


def _t_dotted(text, code):
    """1.7.3: «Frase del catálogo.» (con punto final) cuando el catálogo la tiene sin punto."""
    if text.endswith(".") and not text.endswith(".."):
        hit = (I18N.get(code) or {}).get(text[:-1])
        if hit is not None:
            return hit + ("。" if code in ("zh", "ja") else ".")
    return None



def _t_template(text, code, _debug=False):
    """Frases completas con variables («Actualización de pip: 1 → 2», «Se usará la 1.7.0 la próxima vez…»): None si no encaja."""
    tpl = I18N_FMT.get(code)
    if not tpl:
        return None
    for name, rx in _FMT_RX:
        m = rx.match(text)
        if not m or name not in tpl:
            continue
        g = list(m.groups())
        if name == "conv" and g[1]:
            inner = re.match(r"^ \((.*)\)$", g[1])
            g[1] = (" (" + " · ".join(t_display(x, lang=code, _debug=_debug) for x in inner.group(1).split(" · ")) + ")") if inner else g[1]
        if name == "reenc" and g[1] == "equipo":
            g[1] = I18N_DEVICE.get(code, g[1])
        return tpl[name].format(*g)
    return None


def _translation_for(code):
    if code in PACK_LANGS and code not in PACK_STATE["loaded"]:
        lang_pack_load(code)
    return LANG_TRANSLATIONS.get(code) or _SPANISH_TRANSLATION


def tr(text, lang=None, _debug=True):
    """gettext contextual; el msgid canónico se conserva como referencia de diagnóstico."""
    if text is None:
        return text
    text = str(text)
    if not text:
        return text
    code = lang_effective(lang or LANG)
    out = text if code == "es" else _translation_for(code).pgettext("ui", text)
    return lang_debug_output(out, text, enabled=_debug)


def trc(context, message, lang=None, _debug=True):
    """Traducción explícita con contexto; el identificador visible es el msgid original."""
    if message is None:
        return message
    message = str(message)
    code = lang_effective(lang or LANG)
    out = message if code == "es" else _translation_for(code).pgettext(str(context), message)
    return lang_debug_output(out, message, enabled=_debug)


def trf(context, message, lang=None, **values):
    """Traduce y formatea antes de añadir la información de diagnóstico."""
    out = trc(context, message, lang=lang, _debug=False)
    try:
        out = out.format(**values)
    except (KeyError, IndexError, ValueError) as _ign:
        ignore('trf: formato de la traducción', _ign)
    return lang_debug_output(out, message)


def trn(singular, plural, n, lang=None, context="noun:files", _debug=True):
    """Plural gettext con el msgid singular/plural disponible para inspección."""
    code = lang_effective(lang or LANG)
    if code == "es":
        try:
            out = singular if float(n) == 1.0 else plural
        except (TypeError, ValueError, OverflowError):
            out = plural
    else:
        out = _translation_for(code).npgettext(context, singular, plural, n)
    source = singular if str(out) == str(singular) or str(n) == "1" else plural
    return lang_debug_output(out, source, enabled=_debug)


def tr_fragment(spanish_fragment, lang=None):
    """Traduce un fragmento registrado por contexto sin sustituir subcadenas."""
    es_msg = (I18N_PHRASES.get("es") or {}).get(spanish_fragment)
    if es_msg is None:
        return lang_debug_output(spanish_fragment, spanish_fragment)
    out = trc("fragment:" + spanish_fragment, es_msg, lang=lang, _debug=False)
    if spanish_fragment.strip() and spanish_fragment.strip()[:1].isupper():
        lead = out[:len(out) - len(out.lstrip())]
        trail = out[len(out.rstrip()):]
        core = out.strip()
        out = lead + (core[:1].upper() + core[1:] if core else core) + trail
    return lang_debug_output(out, spanish_fragment)

def _t_unit_expression(text, code, _debug=False):
    """Solo unidades temporales con número, una estructura conocida y no una búsqueda de subcadenas."""
    m = re.fullmatch(r"(\d+(?:[.,]\d+)?)\s+(hora|horas|día|días)", text, re.I)
    if not m:
        return None
    unit = m.group(2).lower()
    if code == "es":
        return text
    if unit in ("hora", "horas"):
        singular, plural, context = "hora", "horas", "noun:hour"  # 2.0.8: msgid español
    else:
        singular, plural, context = "día", "días", "noun:day"  # 2.0.8: msgid español
    try:
        count = float(m.group(1).replace(",", "."))
    except ValueError:
        return None
    translated = trn(singular, plural, count, lang=code, context=context, _debug=_debug)
    return m.group(1) + " " + translated


def _t_download_progress(text, code, _debug=False):
    """Estado de descarga: localiza la etiqueta y conserva nombre/contador como datos literales."""
    m = re.fullmatch(r"(Descargando (?:audio|video))\s+(.+)", text)
    if not m:
        return None
    prefix, rest = m.groups()
    rest = rest.strip()
    if not rest:
        return None
    detail, count = rest, None
    if re.fullmatch(r"\d+\s*/\s*\d+", rest):
        detail, count = "", rest
    else:
        tail = re.fullmatch(r"(.+?)\s+(\d+\s*/\s*\d+)", rest)
        if tail:
            detail, count = tail.groups()
    parts = [tr(prefix, lang=code, _debug=_debug)]
    if detail:
        parts.append(detail)
    if count:
        parts.append(count)
    return " ".join(parts)

def t_status(text, lang=None):
    """Localiza estados de la escena sin tocar el detalle dinámico que viene del proceso o del sitio."""
    if text is None:
        return text
    text = str(text)
    code = lang_effective(lang or LANG)
    if not text:
        return text
    if code == "es":
        return t_display(text, lang=code)
    exact = t_display(text, lang=code)
    if exact != text:
        return exact
    if text.startswith("Error: "):
        return lang_debug_output(tr("Error", lang=code, _debug=False) + text[len("Error"):], text)
    prefixes = ("Descargando audio", "Descargando video", "Preparando descarga", "Analizando enlace",
                "Eligiendo formato", "Revisando archivo", "Comprobando", "Convirtiendo", "Instalando",
                "Actualizando", "Ajustando pistas", "Uniendo pistas", "Sustituyendo", "Guardando",
                "Enviando", "Finalizando", "Descargando", "Bajada de versión", "Actualizada",
                "Edición detectada", "No se pudo reiniciar", "no se pudo reiniciar", "No se pudo guardar en",
                "No se pudo guardar el archivo en", "No se pudo guardar el archivo convertido:",
                "No se pudo guardar el índice:", "No se pudo actualizar", "No se pudo instalar",
                "Caché de streams:", "Caché stream", "Reutilizado de caché:", "Reanudando:",
                "Parcial descartado", "Papelera:", "Configuración borrada", "Idioma ",
                "Convertido a", "Remux a", "Estimación ~", "HDR detectado:", "Sin respuesta:",
                "El formato del atajo", "El formato elegido", "No hay audio disponible",
                "No hay ffmpeg", "No se encontraron formatos", "No se encontró el archivo",
                "No se pudo convertir", "No se pudo abrir con view", "No se pudo usar el portapapeles",
                "No se pudieron leer los Releases", "No se pudo comprobar", "No se pudo instalar",
                "pip terminó con error", "Instalando DLpy", "Instalando ", "Actualizando pip",
                "Comprobando DLpy", "Comprobando pip", "Comprobando actualizaciones",
                "Reintentando análisis", "Enviando el código", "Versión ", "CHANGELOG ",
                "Notas de versión", "Sin datos técnicos", "Listo. Con --config",
                "Mismo número con código distinto", "El repositorio no tiene Releases",
                "El archivo a entregar está vacío", "El archivo descargado ya es compatible",
                "El tone mapping no funcionó", "Este ffmpeg no trae", "No hubo modo sin pérdida",
                "Se usará la ", "Se detectaron varios idiomas", "Se descargará de nuevo",
                "Se reutiliza el archivo", "Conversión cancelada", "Conversión rápida",
                "Opción inválida", "Cancelado", "Descarga cancelada", "Descarga lista")
    for prefix in sorted(prefixes, key=len, reverse=True):
        if text.startswith(prefix) and text[len(prefix):len(prefix) + 1] in (" ", ":", "·"):
            # una sola marca/color para toda la frase
            return lang_debug_output(tr(prefix, lang=code, _debug=False) + text[len(prefix):], text)
    if " · " in text:
        return " · ".join(t_status(part, lang=code) for part in text.split(" · "))
    return text


def _t_core(text, code):
    """1.9.4: traducción de una frase completa sin decorar: gettext exacto, plantillas, fragmentos declarados, unidades y progreso de descarga. None si no hay."""
    if not text.strip():
        return None
    exact = tr(text, lang=code, _debug=False)
    if exact != text:
        return exact
    full = _t_template(text, code, _debug=False)
    if full is None:
        full = _t_rows(text, code)
    if full is None:
        full = _t_dotted(text, code)
    if full is not None:
        return full
    # Fragmentos declarados solo cuando el fragmento completo es el mensaje.
    for es_fragment in (I18N_PHRASES.get("es") or {}):
        if text.strip().casefold() == es_fragment.strip().casefold():
            value = trc("fragment:" + es_fragment, (I18N_PHRASES.get("es") or {}).get(es_fragment, es_fragment), lang=code, _debug=False).strip()
            if text.strip()[:1].isupper() and value:
                value = value[:1].upper() + value[1:]
            lead = text[:len(text) - len(text.lstrip())]
            trail = text[len(text.rstrip()):]
            return lead + value + trail
    # Unidad con número: caso estructurado, no sustitución léxica.
    unit = _t_unit_expression(text, code, _debug=False)
    if unit is not None:
        return unit
    # Contador de progreso de una descarga: el dato (idioma/posición) permanece literal.
    return _t_download_progress(text, code, _debug=False)


def _t_star(text, code):
    """1.9.4: _t_core con el prefijo «★ » de las recomendadas tratado aparte."""
    if text.startswith("★ "):
        inner = _t_star(text[2:], code)
        return None if inner is None else "★ " + inner
    return _t_core(text, code)


def _t_compound(text, code):
    """1.9.4: ayudas «pieza · pieza · {Enter = x}». Cada pieza, o el tramo más largo de piezas contiguas que sea una clave (p. ej. «T todas · n.º (1 3 · 1-3) · D n.º descartar ·»),
    se traduce por separado; una pieza entre llaves de énfasis ({…}) conserva las llaves. None si ninguna pieza cambia."""
    if " · " not in text and not (text.startswith("{") and text.endswith("}")):
        return None
    items = []
    for piece in text.split(" · "):
        inner = piece[1:-1]
        if len(piece) > 2 and piece.startswith("{") and piece.endswith("}") and "{" not in inner and "}" not in inner:
            items.append((True, inner))
        else:
            items.append((False, piece))
    out, changed, i, total = [], False, 0, len(items)
    while i < total:
        wrapped, core = items[i]
        if wrapped:
            hit = _t_star(core, code)
            if hit is not None and hit != core:
                changed = True
            out.append("{" + (hit if hit is not None else core) + "}")
            i += 1
            continue
        end = i
        while end < total and not items[end][0]:
            end += 1
        done = False
        for stop in range(end, i, -1):
            cand = " · ".join(items[k][1] for k in range(i, stop))
            for form in (cand, cand + " ·", cand + " · "):       # las claves antiguas pueden terminar en « ·»
                hit = _t_star(form, code)
                if hit is not None and hit != form:
                    if form != cand:
                        hit = hit.rstrip()
                        if hit.endswith("·"):
                            hit = hit[:-1].rstrip()
                    out.append(hit)
                    changed, done, i = True, True, stop
                    break
            if done:
                break
        if not done:
            out.append(items[i][1])
            i += 1
    return " · ".join(out) if changed else None


def t_display(text, lang=None, _debug=True):
    """Adaptador compatible: gettext exacto + plantillas declaradas + fragmentos/formatos completos + ayudas por piezas.

    No sustituye palabras dentro de títulos, nombres, errores externos ni frases desconocidas.
    """
    if text is None:
        return text
    if not isinstance(text, str):
        text = str(text)
    code = lang_effective(lang or LANG)
    if not text:
        return text
    if code == "es":
        return lang_debug_output(text, text, enabled=_debug)
    if text.startswith("★ "):
        return "★ " + t_display(text[2:], lang=code, _debug=_debug)
    hit = _t_core(text, code)
    if hit is None:
        hit = _t_compound(text, code)
    return lang_debug_output(text if hit is None else hit, text, enabled=_debug)


def t(text, lang=None):
    return t_display(text, lang)


# ─────────────────────── [UX4b] Texto de las animaciones: un solo motor (1.7.1) ───────────────────────
# El dibujo (puntos, vías, chips, barras) es neutro; cualquier texto que lleve dentro sale de aquí, del idioma activo: se traduce primero y se mide después por su ancho
# real. Quien dibuja nunca compara ni mide texto en español. Las claves son el español canónico de siempre (catálogos I18N, I18N_WELCOME, I18N_UX).
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


CONFIG_KEY_RE = re.compile(r"^DLPY_[A-Z0-9_]+$")


def config_key(raw):
    """1.3.0 + 2.0.9: viejo, nuevo o sin DLPY_ -> canónico."""
    k = str(raw or "").strip().upper().replace("-", "_")
    if not k.startswith("DLPY_"):
        k = "DLPY_" + k
    if not CONFIG_KEY_RE.match(k):
        return None
    return config_canonical(k)


def config_write(data, path=None):
    """1.3.0: guarda `data` (solo DLPY_* de texto) en el archivo de configuración, de forma atómica. Crea la carpeta si falta. 2.0.9: siempre en canónico (el viejo se migra al escribir)."""
    path = path or ENV_FILE
    canon = {}
    for k, v in data.items():
        if not (isinstance(k, str) and isinstance(v, str) and k.startswith("DLPY_") and k not in ENV_SKIP):
            continue
        migrated = config_migrate_value(k, v)
        if migrated is None:
            continue
        ck, cv = migrated
        if ck in ENV_SKIP:
            continue
        # 2.0.9: el canónico manda si hay los dos.
        if k == ck:
            canon[ck] = cv
        else:
            canon.setdefault(ck, cv)
    save_json(path, canon, mkdir=True, sort_keys=True)


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
# Descargas completadas únicamente
FILES_DIR = os.path.join(HOME, "Documents", "dlpy_files")
# Índice, estado, caché, trabajo temporal y changelog (carpeta oculta dentro de dlpy_files). 1.3.0: las variables DLPY_* ya no van aquí:
# están en dlpy_files/dlpy_config.json, que no se borra al cambiar de versión.
INTERNAL_DIR = os.path.join(FILES_DIR, INTERNAL_NAME)
# .dlpy_internal/: state/ (estado), cache/streams/, logs/, work/ (descargas en curso),
# delivery/<id>/ (copias de entrega al atajo) y trash/. script/ queda solo como ruta heredada de migración.
# Se borra entera en cada subida o bajada de versión (reset_internal): cada versión empieza de cero.
STATE_DIR = os.path.join(INTERNAL_DIR, "state")
CACHE_DIR = os.path.join(INTERNAL_DIR, "cache")
INDEX_FILE = os.path.join(STATE_DIR, "index.json")
# 1.5.4: de cada video, los formatos del JSON del atajo (id, resolución, fps…) para respaldar la elección
SHORTCUT_PICKS_FILE = os.path.join(STATE_DIR, "shortcut_picks.json")
# todo lo descargado de cada video: {clave: [entrada, ...]}
HISTORY_FILE = os.path.join(STATE_DIR, "downloads.json")
LAST_FILE = os.path.join(STATE_DIR, "last_link.json")
VERSION_FILE = os.path.join(STATE_DIR, "version.json")
DOWNGRADE_FILE = os.path.join(STATE_DIR, "downgrades.json")   # bajadas de versión (historial y pendiente)
CHECK_FILE = os.path.join(STATE_DIR, "checks.json")
DEPS_STATE_FILE = os.path.join(STATE_DIR, "deps.json")      # rechazos recordados
SHORTCUT_JSON = os.path.join(STATE_DIR, "shortcut_analysis.json")      # copia legible de la última salida
# El changelog público se guarda una sola vez junto a las descargas.
CHANGELOG_FILE = os.path.join(FILES_DIR, "changelog.md")
TRASH_DIR = os.path.join(FILES_DIR, "trash")
TRASH_INTERNAL = os.path.join(INTERNAL_DIR, "trash")
# Todos los registros internos viven dentro de internal, independiente de DLPY_HIDE_SCRIPT_FILES.
LOGS_DIR = os.path.join(INTERNAL_DIR, "logs")
ERROR_LOG_FILE = os.path.join(LOGS_DIR, "errors.log")
WARNING_LOG_FILE = os.path.join(LOGS_DIR, "warnings.log")
SHORTCUTMODE_LOG = ERROR_LOG_FILE  # compatibilidad interna: el antiguo log combinado ahora apunta solo a errores.
TRASH_DAYS = 10.0
TRASH_SECS = int(TRASH_DAYS * 86400)
TRASH_EXPIRE_DAYS = 30.0
TRASH_EXPIRE_SECS = int(TRASH_EXPIRE_DAYS * 86400)

CONSERVE_DOWNLOADS = True  # 2.0.9: legado; check_storage lee DLPY_KEEP_DOWNLOADS_OVER_LIMIT (antes DLPY_CONSERVE)

STREAM_CACHE_DIR = os.path.join(CACHE_DIR, "streams")
WORK_ROOT = os.path.join(INTERNAL_DIR, "work")
DELIVERY_DIR = os.path.join(INTERNAL_DIR, "delivery")
# En FILES_DIR no se considera "descarga" el changelog, logs, trash, la configuración ni la carpeta interna (1.6.6: ni una carpeta «backups» que dejaron versiones viejas; es del usuario y no se toca)
# 1.1.6: trash no es una descarga (1.6.5: ni la carpeta interna ni el log, aunque estén visibles)
RESERVED = {"backups", "changelog.md", "logs", "trash", CONFIG_NAME, INTERNAL_BASE, "shortcutmode.log"}

# 1.6.5: DLPY_HIDE_SCRIPT_FILES. Lo que el interruptor oculta (con punto delante) o muestra (sin él) dentro de dlpy_files: los archivos del script. Las descargas y trash
# no entran: son del usuario.
HIDE_ITEMS = (CONFIG_NAME, INTERNAL_BASE, "shortcutmode.log", "logs")


def ensure_internal_logs():
    """Crea internal/logs."""
    try:
        os.makedirs(LOGS_DIR, exist_ok=True)
        return True
    except OSError as _ign:
        ignore("ensure_internal_logs", _ign)
        return False


def hide_files_sync(hide=None, files_dir=None):
    """1.6.5: deja los archivos del script (HIDE_ITEMS) como pide `hide` (por omisión DLPY_HIDE_SCRIPT_FILES): con punto (ocultos) o sin él (visibles). Solo renombra lo que
    existe y cuyo nombre nuevo está libre: nunca pisa nada. Devuelve (movidos, saltados): [(nombre de antes, nombre nuevo)] y [nombres que no se pudieron mover]."""
    hide = HIDE_FILES if hide is None else bool(hide)
    files_dir = FILES_DIR if files_dir is None else files_dir
    moved, skipped = [], []
    for base in HIDE_ITEMS:
        src, dst = (base, hidden_name(base)) if hide else (hidden_name(base), base)
        p_src, p_dst = os.path.join(files_dir, src), os.path.join(files_dir, dst)
        if not os.path.lexists(p_src):
            continue
        if os.path.lexists(p_dst):
            skipped.append(src)            # ya hay otro con el nombre nuevo: se deja tal cual (nada se pierde)
            continue
        try:
            os.rename(p_src, p_dst)
            moved.append((src, dst))
        except OSError:
            skipped.append(src)
    return moved, skipped


def hide_files_apply(path=None, files_dir=None):
    """1.6.5: aplica lo que diga DLPY_HIDE_SCRIPT_FILES en el archivo de configuración `path` (por omisión ENV_FILE): renombra lo que haga falta (hide_files_sync) y devuelve
    (movidos, saltados, configuración): la ruta del archivo de configuración ya con su nombre nuevo (None si no existe)."""
    path = path or ENV_FILE
    files_dir = FILES_DIR if files_dir is None else files_dir
    hide = hide_files_parse(_read_env_json(path).get(HIDE_FILES_KEY))
    moved, skipped = hide_files_sync(hide, files_dir)
    cfg = os.path.join(files_dir, hidden_name(CONFIG_NAME, hide))
    return moved, skipped, (cfg if os.path.isfile(cfg) else None)


def hide_files_after_config():
    """1.6.5: tras guardar la configuración con --config: aplica DLPY_HIDE_SCRIPT_FILES al instante, deja ENV_FILE en el archivo de configuración con su nombre nuevo y dice
    qué se movió (o qué no se pudo)."""
    global ENV_FILE
    moved, skipped, cfg = hide_files_apply(ENV_FILE)
    if cfg:
        ENV_FILE = cfg
    if moved:
        m_ok(("Archivos del script ocultos" if moved[0][1].startswith(".") else "Archivos del script visibles") + f" ({len(moved)}): " + ", ".join(b for _a, b in moved))
    if skipped:
        m_warn("Sin mover (ya existe con el otro nombre): " + ", ".join(skipped))
    return moved


if not any(a.lstrip("-\u2013\u2014").lower() == "selftest" for a in sys.argv[1:]):
    hide_files_sync()                      # 1.6.5: renombra los archivos del script según DLPY_HIDE_SCRIPT_FILES al abrir DLpy
    _cfg_now = os.path.join(FILES_DIR, hidden_name(CONFIG_NAME, HIDE_FILES))
    if os.path.isfile(_cfg_now):
        ENV_FILE = _cfg_now                # la configuración sigue al interruptor
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

# Descargas «como tal» (para el límite de almacenamiento y la limpieza): video + audio + subtítulos e imágenes
AUDIO_EXTS = {"m4a", "mp3", "aac", "opus", "ogg", "oga", "wav", "flac", "aiff", "aif",
              "caf", "wma", "weba", "mka", "alac", "ac3", "eac3"}
EXTRA_EXTS = {"srt", "vtt", "ass", "lrc", "jpg", "jpeg", "png", "webp", "gif"}
DOWNLOAD_EXTS = VIDEO_EXTS | AUDIO_EXTS | EXTRA_EXTS

# (nombre en pip, módulo, obligatoria)
# 1.2.6: pip va primero para que yt-dlp se instale ya con el pip nuevo
DEPENDENCIES = [("pip", "pip", False), ("yt-dlp", "yt_dlp", True), ("mutagen", "mutagen", False)]   # 2.0.7: mutagen opcional (etiquetas y carátula)

# ─────────────── [A4] Compatibilidad nativa Apple ───────────────
# 1.2.4: «h265» (como lo declaran algunos sitios) es HEVC: ya no se recodifica
APPLE_VCODEC = ("avc1", "h264", "hvc1", "hev1", "hevc", "h265")
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


def apple_unsure(f):
    """1.6.9: True si el códec NO se pudo determinar (se adivinó con «_guess» o quedó «unknown») en un contenedor de Apple: normalmente es nativo,
    pero no está comprobado. Se muestra como «🍎?» para animar a elegir esas opciones primero."""
    if f.get("_guess"):
        return True
    ext = f.get("ext")
    v, a = (f.get("vcodec") or "").lower(), (f.get("acodec") or "").lower()
    if has(v):
        return ext in APPLE_VEXT and (v == "unknown" or (v.startswith(APPLE_VCODEC) and a == "unknown"))
    return a == "unknown" and ext in APPLE_AEXT


# ───────────────────────── [A5] Interfaz ─────────────────────────
WAIT_SECONDS = 10
PHANTOM_SECS = 0.4        # un Enter vacío antes de este tiempo se considera fantasma
PHANTOM_BOOT = 1.0        # ... y también en el primer segundo de la ejecución
START_T = time.time()
DEBUG = env_get("DLPY_DEBUG_LOGGING", "").strip().lower() not in ("", "0", "no", "false")
_env_color = env_get("DLPY_COLOR_TRUECOLOR")
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
KEYBOARD_POLL = 0.05     # esperar el alto nuevo al bajar el teclado
FFMPEG_TICK = 0.25       # refresco de la barra de ffmpeg
FILE_POLL = 0.4          # esperar a que el archivo deje de crecer
OPEN_RETRY = 1.5         # reintento de `open` al entregar al atajo
VIEW_RUN = {"mode": None}   # 1.3.4: --view fija el modo de vista solo para esta ejecución (None = el de DLPY_FINISH_DELIVERY_MODE)
VIEW_WORDS = {"view": "view", "vista": "view", "ashell": "view", "a-shell": "view", "v": "view",
              "shortcut": "shortcut", "shortcuts": "shortcut", "atajo": "shortcut", "atajos": "shortcut"}


def view_mode(raw=None):
    """1.3.4:"""
    if raw is True:
        return "view"
    if raw is None:
        raw = VIEW_RUN.get("mode")
        if raw is None:
            raw = env_get("DLPY_FINISH_DELIVERY_MODE")
    # 1.7.8: lo vacío o desconocido = view, el predeterminado (la 1.7.7 lo había pasado a shortcut; en iOS no abría el atajo)
    return VIEW_WORDS.get(str(raw or "").strip().lower(), "view")


def send_key(view=False):
    """1.9.8: la CLAVE (en español) del estado del envío. La escena guarda la clave y la traduce al pintar (t_status); si se guardara ya traducida
    («Sending to…»), scene_motif_kind no la reconocería con otro idioma y el centro caía en D L P Y en vez del dibujo de envío."""
    return "Abriendo con view" if view else "Enviando a " + SHORTCUT_NAME


def send_label(view=False):
    """1.3.4: el texto de estado del cierre de la escena: lo que de verdad va a pasar con el archivo (atajo o view)."""
    # 1.9.0: la frase completa usa la plantilla contextual «Enviando a {0}».
    return t_display("Abriendo con view") if view else t_display("Enviando a " + SHORTCUT_NAME)
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

# Secuencia de respaldo de clear_screen (DLPY_CLEAR_MODE=1..4; por defecto 3). Solo se usa si el `clear` nativo falla.
CLEAR_SEQS = {"1": "\x1b[3J\x1b[2J\x1b[H", "2": "\x1b[2J\x1b[3J\x1b[H",
              "3": "\x1bc", "4": HOME_CLEAR}
CLEAR_SEQ = CLEAR_SEQS.get(env_get("DLPY_CLEAR_MODE", "3").strip(), CLEAR_SEQS["3"])
# 1.2.3: «ESC[3J» borra también el historial de desplazamiento (scrollback). Sin él, el borrado solo limpia lo visible y, cuando la
# ventana de a-Shell cambia de alto (teclado, ventana de Atajos), el terminal vuelve a meter arriba las líneas viejas de sesiones
# anteriores. DLPY_CLEAR_PURGE_SCROLLBACK=0 lo desactiva.
# 1.3.2: es intencional (a-Shell conserva texto entre sesiones): sigue activo por omisión.


def purge_seq(raw):
    """1.3.2: «ESC[3J» (vaciar el historial al borrar), salvo que DLPY_CLEAR_PURGE_SCROLLBACK valga 0 / no / false / off o esté vacía. Sin definir = se manda."""
    raw = "1" if raw is None else raw
    return "" if str(raw).strip().lower() in ("0", "no", "false", "off", "") else "\x1b[3J"


PURGE_SEQ = purge_seq(env_get("DLPY_CLEAR_PURGE_SCROLLBACK"))

# 1.3.2: DLPY_CLEAR_MODE elige cómo se limpia TODA la consola (siempre incluye vaciar el historial salvo DLPY_CLEAR_PURGE_SCROLLBACK=0). «auto» = como siempre
# (`clear` nativo de a-Shell + vaciar historial). Los demás mandan una secuencia directa; si con «auto» tienes que deslizar tras borrar,
# prueba con «python dlpy.py --cleartest», que los enseña uno a uno y guarda el que elijas.
CLEAR_MODES = (
    ("auto", "como siempre: `clear` nativo de a-Shell + vaciar historial"),
    ("home", "cursor arriba, borrar pantalla, vaciar historial y cursor arriba (ESC[H ESC[2J ESC[3J ESC[H)"),
    ("down", "cursor arriba y borrar hacia abajo, sin empujar nada al historial (ESC[H ESC[J ESC[3J)"),
    ("purge-first", "vaciar el historial primero y borrar después (ESC[3J ESC[H ESC[2J)"),
    ("reset", "reinicio total del terminal (ESC c; en a-Shell puede dejar la consola en negro)"),
)
CLEAR_MODE = (env_get("DLPY_CLEAR_MODE") or "auto").strip().lower()


def clear_mode_seq(mode, purge=None):
    """1.3.2:"""
    purge = PURGE_SEQ if purge is None else purge
    return {"home": "\x1b[H\x1b[2J" + purge + "\x1b[H", "down": "\x1b[H\x1b[J" + purge,
            "purge-first": purge + "\x1b[H\x1b[2J", "reset": "\x1bc"}.get(str(mode or "").strip().lower())
# 0.8.9: borrado nativo de a-Shell (comando `clear`); DLPY_CLEAR_USE_NATIVE=0 lo desactiva y usa CLEAR_SEQ
NATIVE_CLEAR = env_get("DLPY_CLEAR_USE_NATIVE", "1").strip().lower() not in ("0", "no", "false", "")
_NATIVE_CLEAR_BAD = [False]               # True si `clear` falló una vez: no se vuelve a intentar en esta ejecución


def _scm_run():
    """True si esta ejecución es --scm / --scb:"""
    try:
        return any(a[:1] in "-\u2013\u2014" and a.lstrip("-\u2013\u2014").lower().split("=")[0] in ("scm", "scb")
                   for a in sys.argv[1:])
    except Exception:
        return False


SC_LIST_FLAG = "--shortcutpick"


def sc_list_mode(raw=None):
    """1.9.9: DLPY_SHORTCUT_DIRECT_LIST_MODE → "" (apagado, predeterminado) · "short" (lista normal) · "all" (lista completa). Lo vacío o no reconocido = apagado."""
    v = str(env_get("DLPY_SHORTCUT_DIRECT_LIST_MODE", "") if raw is None else raw).strip().lower()
    if v in ("1", "on", "yes", "true", "y", "s", "si", "sí", "short", "list", "lista"):
        return "short"
    if v in ("all", "full", "todos", "completa"):
        return "all"
    return ""


def sc_list_args(args, mode=None):
    """1.9.9: con DLPY_SHORTCUT_DIRECT_LIST_MODE activo, --scb (también con raya larga o «=valor») se quita y la ejecución sigue el flujo de --shortcutpick sin valores
    (lista normal) o con v=more (lista completa): el script lista directo, con el estilo de la escena, y descarga. --scm no se toca aquí (ver sc_list_scm_json).
    Sin --scb, o apagado, devuelve `args` tal cual."""
    mode = sc_list_mode() if mode is None else mode
    if not mode:
        return list(args)
    out, hit, has_pick = [], False, False
    for a in args:
        name = a.lstrip("-\u2013\u2014").lower().split("=")[0] if a[:1] and a[:1] in "-\u2013\u2014" else ""
        if name == "scb":
            hit = True
            continue
        has_pick = has_pick or name == "shortcutpick"
        out.append(a)
    if not hit:
        return list(args)
    if not has_pick:
        out.append(SC_LIST_FLAG + ("=v=more" if mode == "all" else "="))
    return out


def sc_list_scm_json(link=None):
    """1.9.9: con DLPY_SHORTCUT_DIRECT_LIST_MODE activo --scm no analiza (corre en «Ejecutar comando», sin pantalla donde listar): responde al instante que el atajo siga con --scb,
    que sí abre a-Shell y lista ahí. Mismo aviso que el del timeout (use_scb), así el atajo usa la rama que ya tiene."""
    return {"dlpy": "shortcutmode", "schema": 1, "ok": False, "status": "error", "version": VERSION, "link": link or "",
            "error_code": "sc_list", "error": "Lista directa: sigue con --scb.", "use_scb": True, "sc_list": sc_list_mode()}


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
        if env_get("DLPY_CLEAR_ON_STARTUP_ENABLED", "1").strip().lower() in ("0", "no", "false", ""):
            return False
        if DEBUG or not sys.stdout.isatty() or _scm_run():
            return False
        if any(a.lstrip("-\u2013\u2014").lower().split("=")[0] in ("selftest", "sistema", "perfil", "2shortcuts",
                                                                      "2shorcuts", "scm", "scb", "shortcutpick", "atajo", "shortcut")
               for a in sys.argv[1:]):
            return False
        # 1.3.5: como en 0.3.6, el primer borrado es el completo (ESC c: reinicia el terminal y limpia también lo que dejaron las versiones
        # anteriores). Después clear_screen() usa el softclear (sin parpadeo). DLPY_CLEAR_FIRST_MODE=auto|home|down|purge-first|reset;
        # si se define DLPY_CLEAR_MODE propio, manda ese.
        return native_clear(mode=early_clear_mode(env_get("DLPY_CLEAR_FIRST_MODE"), CLEAR_MODE))
    except Exception:
        return False


# 1.9.9: DLPY_SHORTCUT_DIRECT_LIST_MODE: antes de que nada mire --scm / --scb (borrado inicial, log, silencio de la salida) la ejecución ya es la de la lista directa
SC_LIST_RUN = {"on": False}
if sc_list_mode():
    _sc_args = sc_list_args(sys.argv[1:])
    if _sc_args != sys.argv[1:]:
        SC_LIST_RUN["on"] = True
        sys.argv[1:] = _sc_args

wait_terminal_ready()
early_clear()

# ── [A5b] Estilo «Aurora» (el mismo de dlpy_test_panel.py) ──
# DLPY_COLOR_TRUECOLOR=0: colores básicos · DLPY_ANIMATIONS_ENABLED=0: sin animación · DLPY_PROGRESS_BAR_CLASSIC=1: barra «█░»
def _flag_env(name, default=True):
    v = env_get(name)
    return default if v is None else str(v).strip().lower() not in ("0", "no", "false", "")


def _env_num(name, default, minimum=0.0):
    """Número de una variable de entorno."""
    raw = (env_get(name) or "").strip()
    if not raw:
        return default
    try:
        v = float(raw)
    except ValueError:
        return default
    return v if math.isfinite(v) and v >= minimum else default


# ── Log de debug: con DLPY_DEBUG_LOGGING todo lo que sale en pantalla se copia a internal/logs/dlpy_debug_<fecha>.log ──
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
        if not DEBUG or not _flag_env("DLPY_DEBUG_LOG_FILE_ENABLED", True):
            return None
        if any(a.lstrip("-\u2013\u2014").lower().split("=")[0] == "selftest" for a in sys.argv[1:]):
            return None
        # 2.1.2: modos JSON del atajo — sin tee ni mensaje final en stdout
        try:
            _args = sys.argv[1:]
            if wants_atajo(_args) or wants_scm(_args) or wants_scb(_args) or _wants(_args, "shortcutpick"):
                return None
        except Exception:
            pass
        ensure_internal_logs()
        d = LOGS_DIR
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, "dlpy_debug_" + time.strftime("%Y%m%d_%H%M%S") + ".log")
        DEBUG_LOG["fh"] = open(path, "w", encoding="utf-8", errors="replace")
        DEBUG_LOG["path"] = path
        with quiet("debug_log_start", OSError):
            keep = int(_env_num("DLPY_DEBUG_LOG_KEEP_COUNT", 20, 1))
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
        args = sys.argv[1:]
        if not (wants_scm(args) or wants_scb(args) or wants_languages(args)
                or wants_atajo(args) or _wants(args, "shortcutpick")):
            rel = os.path.relpath(path, os.path.dirname(FILES_DIR)) if FILES_DIR else path
            inner = getattr(sys.stdout, "_inner", sys.stdout)
            inner.write(f"\n[debug] Log guardado: {rel}\n")
            inner.flush()
    except Exception as _ign:
        DEBUG_LOG["fh"] = None


TRUECOLOR = USE_COLOR and _flag_env("DLPY_COLOR_TRUECOLOR", True)
ANIM = sys.stdout.isatty() and not DEBUG and _flag_env("DLPY_ANIMATIONS_ENABLED", True)
CLASSIC = _flag_env("DLPY_PROGRESS_BAR_CLASSIC", False)
FILL, EMPTY = ("█", "░") if CLASSIC else ("━", "╌")

# nombre: (rgb, color básico de respaldo)
PALETTE = {"orange": ((255, 138, 61), "93"), "magenta": ((255, 61, 139), "95"),
           "mint": ((61, 220, 151), "92"), "amber": ((255, 196, 61), "93"),
           "gray": ((130, 130, 144), "2"), "track": ((58, 58, 70), "90"),
           "white": ((235, 235, 240), "0"), "red": ((255, 85, 102), "91")}
# nombres antiguos → paleta Aurora (así todo el script queda uniforme)
_ALIAS = {"green": "mint", "yellow": "amber", "blue": "orange", "cyan": "orange", "dim": "gray"}
FLAG_COLORS = {"apple": "mint", "orig": "amber", "default": "orange", "best": "magenta",
               "cur": "mint", "upd": "orange", "saved": "mint", "bad": "red"}      # 2.0.0: cur/upd (versiones) · saved/bad (config)
FLAG_MARKS = {"apple": "✓", "orig": "◆", "default": "▸", "best": "★", "cur": "✓", "upd": "⬆", "saved": "●", "bad": "✗"}
FLAG_TEXT = {"apple": "compatible Apple", "orig": "pista original", "default": "predeterminada",
             "best": "recomendada"}
ANIM_LIVE = ANIM                    # animaciones que redibujan en su sitio
CLEAN_LATE = {"on": False}             # 0.8.2: limpieza de archivos antiguos pospuesta al final de la descarga
# ── [UX-estado] inicio: el único estado de la escena que vive fuera del área UX (lo definen aquí para que _say / native_clear lo vean sin importar el orden) ──
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
            "skind": {}, "spct": {}, "slang": {}, "past_dl": False, "motivo": "", "gate_paid": None, "loop_paid": None, "site_t": None, "fast": False, "speed": None, "speed_last": None, "speed_peak": 0.0, "speed_t": None, "speed_end": None}      # 1.4.5: qué es y cuánto lleva cada pista, si ya empezó la descarga y el nombre del motivo del centro


SCENE = scene_defaults()


def quiet_set(on):
    """Apaga (True) o devuelve (False) las animaciones. Solo --shortcutpick lo usa, hasta justo antes de la intro."""
    global ANIM_LIVE
    QUIET["on"] = bool(on)
    ANIM_LIVE = False if on else ANIM


def ux_on():
    """1.5.7: ¿está viva la escena? (la UIM y el núcleo preguntan aquí, no a SCENE)."""
    return bool(SCENE["on"])


def ux_get(key, default=None):
    """1.5.7: un dato del estado de la escena (la UIM y el resto no leen SCENE directamente)."""
    return SCENE.get(key, default)


def ux_set(**kw):
    """1.5.7: deja datos para la escena (la línea de pip, el comando que corre, el enlace…); sin escena nadie los lee."""
    SCENE.update(kw)


def ux_pop(key):
    """1.5.7: borra un dato que se dejó para la escena."""
    return SCENE.pop(key, None)
# ── [UX-estado] fin ──


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


# 1.9.7: pasos del degradado del sitio (antes 6: se veía un corte brusco entre dos tonos); 32 pasos no se distinguen a simple vista
GRAD_STEPS = 32


def mix6(a, b, k):
    """mix(a, b, k) con k acotado a 0–1 y en GRAD_STEPS pasos (1.9.7: 32; antes 6, con cortes visibles; el nombre se conserva)."""
    return mix(a, b, round(max(0.0, min(1.0, k)) * GRAD_STEPS) / float(GRAD_STEPS))


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
# ║ ÁREA B · TERMINAL Y PANTALLA — ancho, mensajes, banner, barras, teclado        ║
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


def json_clean(obj):
    """Copia de `obj` sin secuencias ANSI en ningún texto (claves incluidas): nada de color (p. ej. DLPY_TRANSLATION_DEBUG_MODE=mark) debe llegar a los JSON que lee Atajos,
    porque si las etiquetas de las listas llevan códigos de color, lo elegido ya no coincide con el diccionario («opción fuera del dominio»)."""
    if isinstance(obj, str):
        return _ANSI_RE.sub("", obj) if "\x1b" in obj else obj
    if isinstance(obj, dict):
        return {json_clean(k): json_clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_clean(v) for v in obj]
    return obj
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


def nowrap(text):
    """Apaga el salto automático de línea mientras se escribe `text`."""
    return WRAP_OFF + text + WRAP_ON if sys.stdout.isatty() else text


# ───────────────────── [B2] Mensajes y debug ─────────────────────
# 1.9.4: estado mutable de la ejecución (antes globals sueltas): bar = barra de progreso activa · nested_ios = a-Shell: esta ejecución la lanzó runpy dentro del proceso de otra versión
RUNTIME = {"bar": None, "nested_ios": False}

# Contadores de diagnóstico para DLPY_BOTTOM_BAR_FIELDS. Se protegen porque los avisos pueden llegar desde hilos.
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


def diagnostic_snapshot():
    with DIAGNOSTICS_LOCK:
        return dict(DIAGNOSTICS)

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


def _say(color, msg, mark=None):
    msg = t_status(msg)  # 1.9.0: localiza estados propios sin alterar detalles externos
    # 1.9.2: todo error/aviso enciende la bottombar y se guarda por separado en internal/logs/errors.log y warnings.log.
    if color in ("red", "amber"):
        diagnostic_report("E" if color == "red" else "A", msg)
    # 1.0.4: con escena activa los errores no rompen la animación; se registran y se integran en D L P Y.
    if ux_on():
        if color != "red":
            dbg("escena: aviso omitido", msg)
            return
        # error en escena: pasar a D L P Y en vez de cortar (el detalle ya quedó en el log).
        try:
            ux_set_error(msg)             # 1.0.8: D L P Y con el error (texto limpio)
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
                ux_stop(clear=True)
            except Exception as _ign:
                ignore('_say: parar UX', _ign)
    lines = wrap_text(msg, term_width() - 2)
    b = RUNTIME["bar"]
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
    _say("amber", msg, "!")          # _say cuenta el aviso (bottombar) y lo registra


def m_info(msg):
    _say("orange", msg)


def m_err(msg):
    _say("red", msg, "✕")            # _say cuenta el error (bottombar) y lo registra


def note(text):
    """Texto de apoyo en gris, sangrado 2 columnas (como los subtítulos de dpt)."""
    text = t_display(text)  # 1.7.0
    for ln in wrap_text(text, term_width() - 2):
        print("  " + paint(ln, "gray"))


def hint(text):
    """Ayuda de un prompt:"""
    text = t_display(text)  # 1.7.0
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


debug_log_start()                          # 0.8.6: con DLPY_DEBUG_LOGGING, el log también va a internal/logs/


def install_diagnostic_hooks():
    """Una excepción que nadie captura (hilo principal o secundario) también es un error: se cuenta, se registra y luego sigue el comportamiento de siempre."""
    prev_sys, prev_thr = sys.excepthook, getattr(threading, "excepthook", None)

    def _sys_hook(et, ev, tb):
        if not issubclass(et, (KeyboardInterrupt, SystemExit)):
            diagnostic_report("E", f"Excepción sin capturar: {et.__name__}: {ev}")
        return prev_sys(et, ev, tb)

    sys.excepthook = _sys_hook
    if prev_thr is not None:
        def _thr_hook(args):
            if args.exc_type is not None and not issubclass(args.exc_type, (KeyboardInterrupt, SystemExit)):
                diagnostic_report("E", f"Excepción sin capturar en un hilo: {args.exc_type.__name__}: {args.exc_value}")
            return prev_thr(args)
        threading.excepthook = _thr_hook


install_diagnostic_hooks()


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


# ───────────────────── Estado compartido UX ↔ UIM ─────────────────────
# Estado del sitio para conservar la etiqueta del encabezado entre cambios de escena.
SESSION = {"tag": None}
# 0.7.8: colores del sitio para la pantalla de descarga (los fija site_theme_apply; None = naranja→magenta de siempre)
THEME = {"a": None, "b": None, "full": None}


def theme_rgb():
    """(color 1, color 2) del degradado: los del sitio si hay tema; si no, naranja→magenta."""
    if THEME["a"] and THEME["b"]:
        return THEME["a"], THEME["b"]
    return PALETTE["orange"][0], PALETTE["magenta"][0]


def _host(link):
    try:
        s = str(link).strip()
        return (urllib.parse.urlparse(s if "//" in s else "//" + s).hostname or "").lower()
    except (ValueError, AttributeError) as _ign:
        ignore("_host", _ign)
        return ""


def _host_is(host, domains):
    return any(host == d or host.endswith("." + d) for d in domains)


# ───────────────────── Compartido UX ↔ UIM: ruido y glitch ─────────────────────
# Lo usan la escena (UX) y la pantalla normal (UIM): por eso viven fuera de las dos áreas.
SITE_GLITCH = "▒░#@%&$/\\|<>=+*"
# 1.7.2: DLPY_GLITCH_EFFECT_ENABLED=0 apaga el ruido (SITE_GLITCH) de todas las escenas: las animaciones salen directas
GLITCH = _flag_env("DLPY_GLITCH_EFFECT_ENABLED", True)


def _rn(s):
    """Ruido determinista 0–1 (la intro se ve igual en cada ejecución)."""
    s = math.sin(s * 127.1) * 43758.5453
    return s - math.floor(s)


# Colores y suavizado: solo los usa la escena (UX).
def _fg(c):
    return f"\x1b[38;2;{c[0]};{c[1]};{c[2]}m"


def _bg(c):
    return f"\x1b[48;2;{c[0]};{c[1]};{c[2]}m"


# ═══════════════════ ÁREA UX · la escena COMPLEJA de shortcutmode (animaciones avanzadas, estética) ═══════════════════
# UX = TODO lo que se ve con --shortcutpick / --scm: intro del sitio, escena continua, dibujos del centro, morph, carril de tarjetas, colores del sitio,
# degradados, disolución final y lista «Ver todos» de la escena. Secciones: [UX1] Sitios populares · [UX2] Escena continua · [UX3] Lista «Ver todos» · [UX4] Puente UX.
# REGLA 1.5.8: lo decorativo vive SOLO aquí; sin shortcutmode no se ejecuta. El resto del script no toca la escena por dentro: solo llama a las ux_* de [UX4]
# (y a SCENE/QUIET como estado compartido). Dentro del área UX no se imprimen mensajes normales (eso es de la UIM). El selftest [T29] comprueba la separación.

# ───────────────────── [UX1] Sitios populares: intro de 1 s y etiqueta del banner ─────────────────────
# Antes de la pantalla de descarga sale una intro mínima con los colores del sitio y una forma según lo que se
# baja (video, audio, video+audio, lista o en vivo). La etiqueta (« YT ►♪ ») vuela a la esquina del borde de la
# tarjeta y queda ahí: es el mismo sitio donde el banner la pinta tras el clear_screen de la descarga.
SITE_ANIM = _flag_env("DLPY_ANALYZE_ANIMATION_ENABLED", True)       # DLPY_ANALYZE_ANIMATION_ENABLED=0 la apaga
SITE_SECS = 2.0                                    # duración de la intro (s)
SITE_HOLD_AT = 0.58                                # punto de la intro (0–1) donde espera si el análisis sigue en curso
SITE_HOLD_MAX = 20.0                               # tope de la espera (s)
# 1.9.8: UN solo reloj de cuadros para todas las animaciones (sitio, video/audio, conversión ligera y DLPY); NOISE_FPS es solo el parpadeo del ruido/glitch
ANIM_FPS = 30
NOISE_FPS = 12
SITE_FPS = ANIM_FPS
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


def reset_site_state():
    """Entre dos descargas seguidas (menú de pendientes): la siguiente vuelve a elegir tema y etiqueta."""
    SESSION["tag"] = None
    THEME["a"] = THEME["b"] = THEME["full"] = None


def early_site_intro(run):
    """--shortcutpick:"""
    try:
        if getattr(run, "spick", None) is None:
            return
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
MOTIF_FPS = ANIM_FPS      # 1.9.8: el reloj único (antes 12)
# alto de las barras junto al marco (1.4.2: el del marco; las dos tarjetas van en la fila de debajo)
BOTH_BARS_ROWS = 5
# video + audio: hueco entre el marco y las barras y ancho de las 5 barras (18 + 2 + 9 = 29 = la regla)
BOTH_GAP, BOTH_EQW = 2, 9
MOTIF_ROWS = 5           # alto del motivo (filas)
# (1.5.5: 0.65 → 0.325, el doble de rápido) s que tarda un dibujo del centro en volverse otro (1.4.2: 0.55 → 0.65, el viaje de las celdas necesita un poco más)
SCENE_SWAP = 0.325
# Tiempos de la escena, en UNA tabla (1.5.9): todo lo demás se mide con estos cuatro, así las animaciones se sienten del mismo ritmo.
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


# 1.6.4: lo que dura el loop de CUALQUIER animación de proceso (1.6.4: 0,5 → 1 s y configurable con DLPY_ANIMATION_LOOP_SECS; wait lo espera entero; real no espera)
LOOP_SECS = loop_secs_parse(env_get("DLPY_ANIMATION_LOOP_SECS"))
# s de un paso completo de un proceso (guardar, sustituir, el ✓ de una tarjeta antes de salir); UX_BEAT + UX_SETTLE = LOOP_SECS (1.6.4: 70 % / 30 % del loop)
UX_BEAT = LOOP_SECS * 0.7
# s que tarda un dibujo en asentarse tras su paso (el final suave del guardado, de la sustitución y la salida de una tarjeta)
UX_SETTLE = LOOP_SECS * 0.3
UX_CYCLE = LOOP_SECS     # s de un ciclo de los dibujos que se repiten (envío, descarga, pulso)
# s fijos que se deja ver un paso cuando no hay animación que medir (fuera de «wait»: limpieza, guardado y envío) (1.8.1: max(1.4, LOOP_SECS + 0.4) → LOOP_SECS: todo dura el loop)
UX_HOLD = LOOP_SECS
# 1.4.2: fila (desde lo alto del dibujo) de la tarjeta que cambia: justo DEBAJO del marco del video
BADGE_ROW = MOTIF_ROWS
# Filas de la escena (desde la regla de arriba, y0): regla 0 · título 2 · dibujo del centro 4 … 8 · tarjeta 9 · AIRE (10–11) · texto de estado 12.
# 1.8.2: una fila más de aire bajo el dibujo para que el carril (y el medidor de velocidad) no queden pegados al texto de estado.
# Todo lo que se agregue debajo del dibujo (preguntas, avisos) cuelga de SCENE_STATUS_ROW, nunca de un número suelto, y SCENE_ROWS es el alto total
# (para centrar la escena en la pantalla).
SCENE_STATUS_ROW = 4 + BADGE_ROW + 3                   # 1.8.2: +3 (antes +2) → más aire bajo tarjetas / dibujo
SCENE_ROWS = SCENE_STATUS_ROW + 2
SCENE_TOP = 3                  # fila 1 = aire exterior · fila 2 = topbar seguro · fila 3 = inicio de la escena
# cuadros por segundo de los dibujos ligeros (1.6.4: 20 → 24 = 24 cuadros por loop de 1 s, movimiento fluido; 1.6.3: 12 → 20)
CONV_FPS = ANIM_FPS       # 1.9.8: el reloj único (antes 24)
# 1.2.1: celdas por segundo de los paquetes ● • · que cruzan la vía de la conversión (mínimo; 1.6.3: conv_flow)
CONV_FLOW = 5.0
# 1.6.3: s que tarda un paquete en cruzar la vía (más CONV_END_HOLD = el loop de la conversión)
CONV_TRAVEL = LOOP_SECS - UX_SETTLE


def conv_flow(gap):
    """1.6.3: celdas por segundo de los paquetes de la conversión para que crucen una vía de `gap` celdas en CONV_TRAVEL (nunca menos de CONV_FLOW)."""
    return max(CONV_FLOW, float(gap) / CONV_TRAVEL)


CONV_KEY_FADE = 0.35     # 1.2.1: s que tarda en apagarse la tecla Enter al pasar de la pregunta a la conversión
# (1.6.3: 8 → 12) 1.2.1: cuadros por segundo del dibujo de conversión mientras ffmpeg trabaja (ligero, para no quitarle CPU); con convert_fast_anim (1.6.4) ni eso: la escena se congela y solo repinta al cambiar el %
CONV_RUN_FPS = 12
# 1.6.4: 1 = mientras convierte se detiene toda animación y todo lo que gasta recursos (la escena queda quieta y solo repinta al subir el %; ffmpeg se mide cada FFMPEG_TICK_FAST) · 0 = la conversión sigue animada
CONVERT_FAST_ANIM = _flag_env("DLPY_CONVERT_LIGHT_ANIMATION", True)
# 1.6.4: s entre lecturas del avance de ffmpeg con convert_fast_anim (FFMPEG_TICK = 0,25 sin él)
FFMPEG_TICK_FAST = 1.0
# 1.6.4: s máximos que duerme el hilo de la escena en convert_fast_anim (lo despierta cualquier cambio: %, texto, fin, paro)
FAST_TICK = 1.0
# 1.6.4: suavizado (1/s) con que se llenan los puntos de la conversión hacia el % real (sin convert_fast_anim)
CONV_FILL_RATE = 6.0
CONV_NOTICE = ("Espera mientras convierte · puede tardar · no cierres la app", "Espera mientras convierte · no cierres la app",
               "Espera · puede tardar · no cierres la app", "Espera · no cierres la app", "No cierres la app", "Espera…")    # 1.6.4: el aviso bajo el texto de estado, de más largo a más corto (cabe el primero que quepa)
# 1.6.4: despierta al hilo de la escena dormido en convert_fast_anim
_FAST_WAKE = threading.Event()
SCENE_FPS = ANIM_FPS        # 1.9.8: el reloj único (antes 15)
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


# lo que no se pudo determinar (5 caracteres: impar, centrado) · claves en español canónico
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
    _scene_tail = 3 if BOTTOMBAR else 1
    if sw < 30 or Hh < max(16, SCENE_TOP + SCENE_STATUS_ROW + _scene_tail):
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
    y0 = SCENE_TOP        # 1.6.6: la escena va arriba de la consola, con una sola línea de aire
    ymax = min(Hh, y0 + SCENE_STATUS_ROW + (3 if BOTTOMBAR else 1))
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
        # filas completas desde la columna 1 (filas enteras, sin depender del cuadro anterior)
        for y in range(1, ymax + 1):
            parts, cur = [], None
            skip = False
            for x in range(1, W):
                if skip:                                   # 1.7.0: ver scene_paint
                    skip = False
                    continue
                c = allc.get((x, y))
                key, ch = (c[1:], c[0]) if c else (None, " ")
                wide = bool(ch) and ch[0] >= "\u1100" and x < W - 1 and unicodedata.east_asian_width(ch[0]) in ("W", "F")
                if not ch or (ch[0] >= "\u1100" and not wide and unicodedata.east_asian_width(ch[0]) in ("W", "F")):
                    ch = " "
                if key != cur:
                    parts.append(sgr(key) if key else RESET)
                    cur = key
                parts.append(ch)
                skip = wide
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
        # 1.6.6: reset completo ya con el alto estable (sin tener que hacer scroll para ver la escena)
        native_clear(HOME_CLEAR, mode=scene_clear_mode())
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
                time.sleep(frame_gap(ta + time.monotonic() - now, SITE_FPS))      # 1.9.8: hasta el siguiente cuadro, sin sondear
        SESSION["tag"] = (tag, a, fg)
    finally:
        sys.stdout.write(RESET + WRAP_ON + CURSOR_SHOW)
        sys.stdout.flush()
    return True


# ───────────────────── [UX2] Escena continua de --shortcutpick (0.9.3) ─────────────────────
# Con --shortcutpick la intro del sitio no se deshace: sigue como una escena viva que NO imprime líneas nuevas.
# El nombre del sitio se transforma (glitch) en el título del video; debajo va UN solo texto con el proceso en curso
# (analizando, descargando con %, uniendo, guardando, enviando); la regla de arriba hace de barra de progreso y el glifo
# (video / audio) sigue en movimiento. Al final: «Enviando a DLpy», la disolución de siempre (scene_dissolve) y el atajo.
# Un hilo pinta la escena; mientras tanto stdout está silenciado (_SceneMute) para que ningún mensaje, barra, banner o
# tarjeta del resto del script la pise. Un error (m_err), una pregunta pendiente o pip la cortan y todo sale como antes.
# 0.9.4: las actualizaciones se buscan dentro de la escena (título «D L P Y», regla que barre, texto de lo que hace, sin preguntas)
# y la salida es propia: «Enviando a DLpy» y la escena se cierra hacia el centro (scene_dissolve) antes de borrar la pantalla.
# 1.0.2: el centro de la escena cambia de dibujo según lo que pasa (el del sitio, la escena de conversión o la escena DLPY): ver
# scene_motif. Los cambios usan el mismo ruido que el título y el texto, y la escena solo sube a 24 cuadros mientras algo se transforma.
# 1.1.3: el centro tiene tres dibujos más según el paso (unión, guardado y envío): ver scene_merge_cells, scene_save_cells y scene_send_cells.
# 1.2.9: dos más para el arranque: «Primera ejecución» (scene_first_cells) y «Actualizado» (scene_updated_cells); ver scene_welcome.
# 1.6.5: dos más para los cambios de versión: «Versión anterior» (scene_downgrade_cells) y «Misma versión» (scene_same_cells); ver scene_welcome y WELCOME_KINDS.
# 1.4.2: el paso de un dibujo del centro a otro es un morph (las celdas viajan; ver «Motor de morph del centro») y la tarjeta del video va bajo el marco.
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


# 1.4.8: segundos por escena si piden «segundos» sin número (nombre antiguo)
UX_SECS_DEFAULT = 2.0
# 1.5.1: nombres de los tres modos de DLPY_SCENE_RHYTHM (el primero de cada fila es el de la configuración; los demás, los de antes)
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


# 1.6.7: ya no se leen DLPY_SCENE_MODE ni DLPY_UX_SECS (solo DLPY_SCENE_RHYTHM)   # DLPY_SCENE_RHYTHM=wait (predeterminado) | real | <segundos>; DLPY_SCENE_MODE=loop | real | <segundos> sigue valiendo
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


# 1.8.3: franja superior (dispositivo · tiempo · versión); 0 = apagada
TOPBAR = topbar_parse(env_get("DLPY_TOP_BAR_FIELDS"))
# 1.9.2: franja inferior de errores/advertencias; 0 = apagada
BOTTOMBAR = bottom_bar_parse(env_get("DLPY_BOTTOM_BAR_FIELDS", "1"))   # activa por defecto (con la variable vacía o en 0 se apaga)
# 1.9.2: reserva una fila extra para el aire y otra para no pisar avisos de conversión
SCENE_ROWS = SCENE_STATUS_ROW + (4 if BOTTOMBAR else 2)


# 1.8.8: icono de red de la franja (ancho 1; los emojis miden 2 celdas y a-Shell los mide mal)
NET_ICON = "⇅"
TOPBAR_SEP = "  ·  "
# 1.8.9: si la franja no cabe, se quitan D, T y luego V (siempre queda al menos un campo)
TOPBAR_DROP = ("D", "T", "V")
# 1.9.2: si no cabe, se conserva el icono de error antes que el de aviso; 1.9.4: la red se quita primero
BOTTOMBAR_DROP = ("N", "A", "E")
# eventos internos E/A y red N; símbolos compactos y de una columna (sin contador visible)
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
            parts.append((k, f"v{VERSION}"))
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


# DLPY_SCENE_OUTRO_ENABLED=0: la escena (UX) no se cierra hacia el centro antes del atajo; solo se limpia la consola
OUTRO = _flag_env("DLPY_SCENE_OUTRO_ENABLED", True)
SCENE_OUTRO_SECS = 0.9                              # s que tarda la escena en cerrarse hacia el centro
# (1.5.5: 0.10 → 0.05) 1.0.6: s que espera el dibujo del centro tras el título (cascada)
SCENE_LAG_MOTIF = 0.05
SCENE_LAG_LABEL = 0.18                              # 1.0.6: s que espera el texto de estado tras el título (cascada)
# 1.0.6: suavizado de la regla (1/s; equivale a 0.15 por cuadro a 24 fps)
SCENE_BAR_RATE = 3.9
SCENE_ASP_RATE = 3.1                                # 1.0.6: suavizado de la proporción del marco (1/s)
SCENE_BUSY_RATE = 9.0                               # 1.0.6: fundido barrido de espera ↔ barra de progreso (1/s)
# DLPY_PIP_USES_SCENE=0: pip siempre cede la escena (escribe directo al terminal)
SCENE_PIP = _flag_env("DLPY_PIP_USES_SCENE", True)
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
    """1.9.8: s hasta el siguiente límite de cuadro de un reloj que lleva `t` s a `fps` cuadros por segundo (entre 0,5 ms y un cuadro)."""
    fps = max(1.0, float(fps))
    return max(0.0005, min(1.0 / fps, (math.floor(t * fps + 1e-9) + 1) / fps - t))


def frame_wait(t0, fps, base=0.0):
    """1.9.8: duerme hasta el siguiente cuadro de un reloj que arrancó en `t0` (time.monotonic) y llevaba `base` s; sin sondear ni acumular retraso."""
    time.sleep(frame_gap(base + time.monotonic() - t0, fps))


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


# 1.3.6: format_id → ("video",) / ("audio",) / ("video", "audio"), de la lista de formatos ya analizada
STREAM_KINDS = {}


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
# u (avance propio de la celda) en que sale de su sitio y llega al nuevo
FLOW_LEAVE, FLOW_LAND = 0.12, 0.86
FLOW_ROLES = (("line", "─│╭╮╰╯├┤┬┴┼━┃═║╔╗╚╝┌┐└┘▬"), ("shade", "░▒▓"), ("bar", "▁▂▃▄▅▆▇█▀▌▐"),
              ("dot", "●•·○◦∙()›"), ("mark", "►✓✗♪"))
FLOW_ROLE_OF = {ch: role for role, chars in FLOW_ROLES for ch in chars}
# quién sale antes: el contenedor y luego el contenido
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
# 1.7.6: s de los fundidos de la escena: un gesto breve, el normal (el encendido de una tarjeta) y el que acompaña un cambio grande
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


def scene_swap_cells(old, new, p, f, a, b):
    """Un dibujo del centro se vuelve otro (p de 0 a 1), sin estado: mide y reproduce en la misma llamada. La escena viva usa
    scene_flow_step (mide una vez por transición)."""
    if p <= 0.0:
        return dict(old)
    if p >= 1.0:
        return dict(new)
    return flow_frame(flow_plan(old, new), old, new, p, f, a, b)


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


# ── Los tres dibujos del centro de la escena (1.0.3) ──
# El centro (5 filas bajo el título, 6 con la tarjeta del video) muestra uno de tres dibujos y pasa de uno a otro en SCENE_SWAP (1.4.2: sus celdas viajan; antes, ruido que se disuelve):
#   · el del sitio (marco de video, ecualizador, lista o directo) mientras descarga; si son dos pistas (both) y una termina,
#     su dibujo se deshace y el que queda se desliza al centro (0.55 s);
#   · la escena de conversión, solo mientras convierte;
#   · la escena DLPY, con el título «D L P Y»: boot aSH → PY → DLPY con comando contextual.
def scene_chip_text(x):
    """Texto de un chip de la escena de conversión: mayúsculas, en el idioma activo y como mucho CHIP_COLS columnas reales («webm» → «WEBM»). 1.7.1: lo resuelve ux_chip."""
    return ux_chip(x)


# 1.4.1: qué texto de estado pide qué dibujo (1.2.5 revisión · 1.1.3 unión y guardado · 1.1.5 limpieza · 1.1.7 papelera). El resto de
# dibujos lo decide el estado (D L P Y, envío, conversión, pregunta, arranque); todos viven en MOTIFS, más abajo.
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


# 1.4.2: s que cruza el paquete de VIEJO a NUEVO al sustituir; después queda sustituido (✓)
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


# 1.2.7: la escena D L P Y teclea rápido (0,6 s) y «ejecuta» (Enter + 0,45 s) cada comando
TYPE_DELAY_SECS, TYPE_DURATION_SECS, TYPE_RUN_SECS = 0.1, 0.6, 0.45
# y el texto de estado no pasa al siguiente hasta que termina (scene_status)
TYPE_STEP_SECS = TYPE_DELAY_SECS + TYPE_DURATION_SECS + TYPE_RUN_SECS


# 1.3.3: textos de un proceso que sigue en curso
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


# 1.3.3: tope de espera: la intro, el cambio del dibujo, un paso y un respiro
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
        # con loop: una medida NUEVA (no la del cuadro anterior al cambio de estado)
        if mv and mv[0] == kind and mv[1] and (not loop or (mv[2] or 0.0) <= 0.05 and mv[3] >= t_in):
            return True
        time.sleep(0.02)
    return False


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


def scene_wait_anim(kind, secs):
    """1.5.5: lo que espera el flujo por la animación `kind` según el modo UX. «wait»: a que el dibujo se vea y cierre su loop en curso, y nada
    más (sin pausas fijas; 1.5.9: con scene_gate, que además avisa a la escena para no retenerlo otra vez) · segundos: esos `secs` (scene_hold) ·
    «real»: nada, el proceso sigue haya terminado o no la animación."""
    if SCENE_MODE[0] == "loop":
        if scene_wait_motif(kind):
            scene_gate()
        return
    scene_hold(secs)


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


# ── Tres dibujos más del centro (1.1.3): unión, guardado y envío ──
# Mismas reglas que la conversión: tres filas (y0+5 … y0+7), colores del degradado del sitio, funciones puras que dependen solo de `lt`
# (segundos desde que empezó el dibujo) y entradas / salidas con el morph de scene_flow_step (1.4.2; antes el ruido de scene_swap_cells).
# 1.8.5: cierre de la escena de sustitución; el guardado normal ya no espera
SCENE_REPLACE_SECS = UX_HOLD
# 1.1.3: s que se deja ver «Enviando…» antes de cerrar la escena (antes 0.85)
SCENE_SEND_SECS = UX_HOLD
# 1.1.3: celdas por segundo que avanzan los bloques de la unión (1.6.4: un ciclo de 4 celdas = un loop)
MERGE_SPEED = 4.0 / LOOP_SECS
# 1.1.3: s que fluyen los bloques hacia la carpeta; después queda guardado
SAVE_STREAM_SECS = UX_BEAT
# 1.1.3: s de un ciclo del envío (vuelo del cometa + onda al llegar)
SEND_CYCLE = UX_CYCLE
# 1.6.3: s del ciclo con que se dibujó el envío; scene_send_cells lo comprime a SEND_CYCLE
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


# (1.6.3: el barrido de la revisión va y viene en LOOP_SECS, a la velocidad que pida el ancho; ya no hay CHECK_SPEED)
CHECK_TONE = (255, 190, 90)                         # 1.2.5: ámbar de «esto hay que convertirlo»
# 1.6.1: parpadeos de los tres cuadros al determinarse lo detectado (destello · apagón, ×3)
CHECK_BLINKS = 2
# 1.6.2: s por destello o apagón (0.12 → 0.15: se alcanza a ver aunque el terminal tarde en pintar)
CHECK_BLINK_STEP = LOOP_SECS / (CHECK_BLINKS * 2)
CHECK_BLINK_SECS = CHECK_BLINKS * 2 * CHECK_BLINK_STEP
# 1.6.2: un pulso completo de la revisión resuelta (arranca donde acaba el parpadeo); parpadeo + pulso = el loop de la resolución
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


SCENE_CLEAN_SECS = UX_HOLD                              # 1.1.5: s que se deja ver «Limpiando» antes de seguir
# 1.1.5: ciclos por segundo de los archivos que caen a la papelera (1.6.4: un ciclo = un loop)
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


# 1.7.1: s de un ciclo de los dibujos de bienvenida = lo que dura la escena (antes 1.0; 1.7.0: motif_loop_left usa esta cuenta). FIJO: ya no depende de DLPY_ANIMATION_LOOP_SECS
WELCOME_CYCLE = 2.0
# 1.7.0: s que se deja ver «Primera ejecución» / «Actualizado» (un ciclo menos el retraso del dibujo). FIJO: no depende de DLPY_SCENE_RHYTHM ni de DLPY_ANIMATION_LOOP_SECS
SCENE_WELCOME_SECS = WELCOME_CYCLE - 0.05
# 1.6.3: s del ciclo con que se dibujaron; las escenas lo comprimen a WELCOME_CYCLE
WELCOME_BASE = 2.4
# 1.2.9: s que tardan los chevrones en cruzar la vía antes de llegar a la versión nueva
WELCOME_FLY = 1.1
WELCOME_ITEMS = ("carpetas", "estado", "listo")     # 1.2.9: los tres pasos de la primera ejecución
# 1.8.1: los dibujos de la pantalla de actualización (D L P Y y sus escenas de versión): no los afectan las reglas del loop (ni retienen ni se retienen)
UPDATE_KINDS = ("dlpy", "first", "updated", "downgrade", "same", "ahead")
# 1.6.5: los dibujos de arranque / versión: primera ejecución · sube · baja · misma versión (1.7.1: + ahead = la local es mayor que el Release)
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


# ── Descarga y Pulso (1.4.5) ──
# «Descarga» entra cuando empieza a bajar la primera pista y se queda mientras dure; «Pulso» es el reposo entre motivos una vez que
# la descarga empezó (el sitio ya no vuelve). Mismas reglas que los demás: filas y0+5 … y0+7, funciones puras de `lt`.
# 1.4.5: s de un ciclo de la descarga (a cada pista le cruza un paquete ● • ·)
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
    return scene_dlpy_cells(d.W, d.y0, d.a, d.b, d.ta - start, VERSION, lab, tt)


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


# ── Carril de tarjetas (1.4.6) ──
# Una sola escena de la apertura al cierre: los procesos del flujo (VIDEO, AUDIO, UNIÓN, GUARDADO) son tarjetas en un carril de hasta
# RAIL_MAX a la vez. Una tarjeta nueva entra por la derecha y empuja a las demás; si no cabe, la más antigua sale por la IZQUIERDA.
# Una tarjeta cuyo proceso terminó se queda un instante con su ✓ y sale también por la IZQUIERDA (1.5.5; antes salía por la derecha). Las tarjetas ya presentes en el primer cuadro
# del carril no se deslizan: el motor de morph las lleva desde el dibujo anterior (el marco del video y el ecualizador del sitio).
# DLPY_SCENE_RAIL=0 devuelve la Descarga / Unión / Guardado de la 1.4.5.
RAIL_MAX, RAIL_GAP = 3, 2                           # tarjetas a la vez y columnas entre ellas
RAIL_KINDS = ("download", "merge", "save")           # los dibujos de 1.4.5 que ahora viven dentro del carril
# 1/s: suavizado de las tarjetas al entrar y al recolocarse (1.5.5: 7 → 14, el doble de rápido)
RAIL_MOVE = 14.0
# 1.8.2: salida decidida desde el primer frame (misma sensación que el video)
RAIL_EXIT_V0, RAIL_EXIT_ACC = 62.0, 170.0
# 1.8.2: solo un destello de ✓ y fuera (antes UX_BEAT ≈ 0,7 s → se sentía frenado)
RAIL_DONE_HOLD = 0.14
RAIL_FADE_IN = 0.15                                 # s que tarda en aparecer una tarjeta que entra (1.5.5: 0.3 → 0.15)
# 1.4.9: s que tarda el título de una tarjeta en deslizarse al de la pista siguiente
RAIL_TITLE_T = 0.5
# 1.8.2: tiempo de salida que cuenta el loop (antes UX_SETTLE); acorde al movimiento rápido
RAIL_EXIT_T = 0.28
# 1.8.2: fundido mientras sale; corto para no «apagar y luego mover»
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


# ── Estilo visual de la escena (1.4.8) ──
# Toda escena (tarjeta del carril o dibujo a todo el ancho) se lee igual, de arriba abajo, en las mismas filas del centro (y0+4 … y0+9):
#   · fila 0 — ETIQUETA: el nombre del proceso en mayúsculas (VIDEO, CONVERSIÓN, ENVÍO…), centrada.
#   · filas 1-3 — el DIBUJO del proceso (3 filas): su propio dibujo, pero siempre con los mismos tonos.
#   · fila 4 — (1.5.6) vacía: las escenas ya no llevan barra de progreso; el avance lo lleva la regla de arriba.
#   · fila 5 — ESTADO: «espera» o ✓ (1.5.6: nunca un % ni puntos de avance), o el dato del archivo que se pida.
# 1.8.2: debajo del bloque (y0+10 …) hay más aire antes del medidor de velocidad y del texto de estado global (SCENE_STATUS_ROW).
# Tres estados, tres tonos: «espera» = gris apagado · «activa» = los colores del sitio (degradado) con blanco · «hecho» = verde con ✓.
# Etiqueta y estado salen de style_label · style_status (las usan las tarjetas del carril y scene_chrome, que los pone a las
# escenas de ancho completo), así que un cambio de estilo se hace en un solo sitio. D L P Y (la ventana a-Shell) y el Pulso (reposo) quedan como están.
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


# 1.7.6: celdas de cola del cometa que recorre el marco del video (antes 6, con caída lineal)
COMET_TAIL = 9.0


def comet_glow(head, idx, n, tail=COMET_TAIL):
    """1.7.6: brillo (0 a 1) de la celda `idx` de un recorrido de `n` celdas con el cometa en `head` (posición con decimales): la cabeza llega a 1 y la cola se apaga con
    curva cuadrática en `tail` celdas; la celda que está a punto de recibirlo se enciende antes (a menos de una celda), así el cometa no salta de celda en celda. Pura."""
    d = (head - idx) % n
    if d > n - 1.0:
        return d - (n - 1.0)
    return 0.0 if d >= tail else (1.0 - d / tail) ** 2


# 1.7.5 (1.7.6: = MOTION_BASE): s que tarda una tarjeta en encenderse (espera → activa) y en asentar su verde (activa → hecho)
RAIL_TONE_T = MOTION_BASE
# 1.7.5: fuerza (0 a 1) del destello blanco-verde que se apaga al terminar una tarjeta
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


# Escenas a todo ancho con el estilo de la escena (1.4.8): qué partes lleva cada una (l = etiqueta · b = barra · s = estado). D L P Y y Pulso, ninguna.
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

# 1.4.5: el nombre de cada motivo (lo que entra al centro de la escena). «site» no está en MOTIFS: es el dibujo con que arranca (kind None).
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


# 1.5.9: s que vale la marca «el flujo ya esperó este dibujo» (scene_gate)
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
    """Cuadros por segundo: a tope en intro/cierre/transformaciones; si no, CONV_FPS o SCENE_FPS. 1.0.3: también a tope durante salida de tipo."""
    if ta < hold or S.get("t_out") is not None or S.get("k_out") is not None or S.get("t_in") is not None or S.get("ask"):
        # 1.1.1: también mientras espera el Enter (texto animado)
        return SITE_FPS
    if st.get("key_fade_t") is not None and 0 <= ta - st["key_fade_t"] < CONV_KEY_FADE + 0.1:
        # 1.2.1: la tecla Enter apagándose, a tope de cuadros
        return SITE_FPS
    for m in (st.get("bdg") or {}).values():                         # 1.0.7: la etiqueta cambiando va a tope de cuadros
        if m[1] is not None and 0 <= ta - m[1] < SCENE_BADGE_SECS + 0.1:
            return SITE_FPS
    for key, dur in (("mt", SCENE_SWAP), ("t", SCENE_MORPH), ("tt", SCENE_TITLE_MORPH), ("site_trans_t", SCENE_SWAP)):
        t0 = st.get(key)
        # 1.0.6: incluye la espera de la cascada
        if t0 is not None and -SCENE_LAG_LABEL <= ta - t0 < dur + 0.1 + SCENE_LAG_LABEL:
            return SITE_FPS
    if ta < st.get("rail_fast", 0.0):                                # 1.4.6: tarjetas del carril deslizándose
        return SITE_FPS
    _ck = S.get("check") or {}
    # 1.6.1: los cuadros parpadeando, a tope de cuadros (1.6.2: y mientras espera a pintarse el primero)
    if _ck.get("verdict") is not None and (_ck.get("t") is None or 0 <= ta - _ck["t"] < CHECK_BLINK_SECS + 0.1):
        return SITE_FPS
    # 1.1.3: unión y guardado (1.1.5: y limpieza; 1.2.5: y revisión; 1.2.9: y arranque), como la conversión (1.4.1: la marca light de MOTIFS)
    if getattr(MOTIFS.get(scene_motif_kind(S)), "light", False):
        return CONV_FPS
    if S.get("brand"):
        return SCENE_FPS
    cv = S.get("conv")
    # 1.2.1: la conversión, más ligera que el resto
    return CONV_RUN_FPS if (cv and cv.get("end") is None) else SITE_FPS


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


# 1.6.4: s entre repintados completos en convert_fast_anim (por si el terminal borró algo; el resto del tiempo no se pinta nada)
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




# 1.7.0: s de un ciclo del medidor de velocidad (un loop, como las demás animaciones de proceso)
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
    """Hilo de la escena: 24 cuadros por segundo hasta que SCENE["stop"]."""
    S = SCENE
    out, (W, _h, _y0, ymax) = S["out"], S["geo"]
    st = scene_state()
    hold = SITE_HOLD_AT * SITE_SECS
    # al volver de la lista no se repite la intro
    t0 = full_t = time.monotonic() - (hold + 0.4 if S.get("resume") else 0.0)
    rows_seen, last, fps = S["rows"], -1, SITE_FPS
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
                scene_paint(out, scene_cells(S, st, min(ta, hold), ta, f), st, W, ymax)
            time.sleep(frame_gap(time.monotonic() - t0, fps))      # 1.9.8: hasta el siguiente límite de cuadro
    except Exception as _ign:
        S["err"] = f"{type(_ign).__name__}: {_ign}"      # 1.0.1: --scb lo anota en state/scb_debug.json
        ignore("scene_loop", _ign)


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


def scene_saved():
    """1.8.5: compatibilidad interna; la animación ficticia de «Guardando» está desactivada.
    El estado «Guardado» lo publica _m_store después de completar el movimiento real."""
    return False


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


def scene_brand(on=True):
    """El título pasa a «D L P Y» (arranque y actualizaciones; 1.9.8: ya no el envío); con on=False vuelve al del video."""
    if SCENE["on"]:
        if on and not SCENE.get("brand"):
            # 1.5.9: el dibujo en curso termina de verse antes de que entre D L P Y
            scene_gate("dlpy")
        SCENE["brand"] = bool(on)
        SCENE["err_brand"] = False


def scene_brand_end():
    """1.8.0: D L P Y (el actualizador) ya terminó y el flujo sigue con el resto de las escenas: el título, el centro y la regla dejan D L P Y y vuelven a lo suyo
    (el sitio, el análisis, la descarga…). scene_note solo lo ENCIENDE (scene_brand) y nadie lo devolvía: con las actualizaciones primero la descarga seguía
    dentro de D L P Y («Descargando video · 0 %» bajo el título D L P Y, sin pasar a las demás escenas). Antes de soltarlo, el comando que se ve termina de
    mostrarse (tecleado y ejecutado), como en scene_welcome; el dibujo de D L P Y cierra su loop en curso por su cuenta (motif_loop_left en scene_motif).
    No hace nada sin escena, con D L P Y ya apagado ni con un error (scene_error_end lo necesita encendido). True si lo apagó."""
    S = SCENE
    if not S["on"] or not S.get("brand") or S.get("last_error"):
        return False
    if S.get("label_wall"):
        scene_wait_step(str(S.get("label") or ""))
    S["brand"], S["err_brand"], S["busy"] = False, False, False
    return True


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
    # 1.5.9: modo «wait»: lo que dura la animación (entrar + su loop), no `secs` fijos
    if SCENE_MODE[0] == "loop":
        th = SCENE.get("th")
        if th is not None and th.is_alive() and th is not threading.current_thread():
            scene_gate()
            return True
    time.sleep(max(0.0, float(scene_dwell(secs))))
    return True


def welcome_hold(secs):
    """1.7.0: deja ver la bienvenida `secs` segundos FIJOS (no depende de DLPY_SCENE_RHYTHM ni de DLPY_ANIMATION_LOOP_SECS, a diferencia de scene_hold). No espera sin escena o con error. True si esperó."""
    if not SCENE["on"] or SCENE.get("last_error"):
        return False
    time.sleep(max(0.0, float(secs)))
    return True


def welcome_kind(stored, version):
    """1.2.9: qué escena de arranque toca: «first» (no hay versión guardada), «updated» (la guardada es menor: subida), «downgrade» (la guardada es mayor: bajada,
    1.6.5) o None (misma versión)."""
    if not stored:
        return "first"
    if stored == version:
        return None
    move = version_move(stored, version)
    return None if move == "igual" else "downgrade" if move == "baja" else "updated"


def code_change(stored_hash, cur_hash):
    """1.3.2:"""
    if not cur_hash:
        return None
    if not stored_hash:
        return "first"
    return None if stored_hash == cur_hash else "edited"


def scene_welcome(kind, old=None, new=None, down=False, edited=False, text=None):
    """1.2.9: (1.6.5: kind «first» · «updated» (sube) · «downgrade» (baja; también «updated» con down=True) · «same» (misma versión; también «updated» con edited=True).
    `text` = el texto de estado propio (por omisión el de cada caso).)"""
    S = SCENE
    if kind == "updated" and down:
        kind = "downgrade"
    elif kind in ("updated", "same") and edited:
        kind = "same"
    if kind not in WELCOME_KINDS or not S["on"] or S.get("last_error"):
        return False
    if text:
        text = str(text)
    elif kind == "first":
        text = f"Primera ejecución · DLpy {new or VERSION}"
    elif kind == "ahead":                                             # 1.7.1: la local es mayor que el Release
        text = f"DLpy {new or VERSION} · versión local"
    # 1.3.2: misma versión, otro código (los chips llevan la versión; el hash va en el texto)
    elif kind == "same":
        text = "Cambió el hash · edición detectada" if edited else f"Misma versión · {new or old or VERSION}"
    else:
        text = f"{'Versión anterior' if kind == 'downgrade' else 'Actualizado'} · {old or '?'} → {new or VERSION}"
    # 1.3.1: cómo estaba la escena antes
    prev = {k: S.get(k) for k in ("brand", "busy", "err_brand", "label", "pct")}
    # 1.8.0: el comando de D L P Y que se ve termina de mostrarse (tecleado y ejecutado) ANTES de que la bienvenida lo tape;
    if S.get("brand") and S.get("label_wall"):
        # scene_status ya no lo espera (con S["welcome"] puesto el centro deja de ser D L P Y) y el comando se cortaba a medias
        scene_wait_step(str(S.get("label") or ""))
    S["welcome"] = {"kind": kind, "old": old, "new": new or VERSION, "edited": bool(edited)}
    try:
        scene_brand()
        scene_busy()
        scene_status(text)
        return welcome_hold(SCENE_WELCOME_SECS)
    finally:
        S["welcome"] = None
        # 1.3.1: se devuelve todo a como estaba (si no, D L P Y se quedaba para el resto del flujo)
        if not S.get("last_error"):
            S["brand"], S["busy"], S["err_brand"] = bool(prev["brand"]), bool(prev["busy"]), bool(prev["err_brand"])
            S["label"], S["pct"] = prev["label"] or "", prev["pct"]


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


def scene_convert(codec, label="Convirtiendo", src=None, dst=None):
    """1.0.2:"""
    if not SCENE["on"]:
        return
    cv = SCENE.get("conv")
    if not (cv and cv.get("end") is None):
        # 1.5.9: el dibujo en curso termina de verse antes de que entre la conversión
        scene_gate("conv")
    # otro intento (otro encoder): el destino cambia, el origen es el mismo
    if cv and cv.get("end") is None:
        cv["codec"], cv["dst"], cv["pct"] = str(codec or ""), scene_chip_text(dst or codec), None
        if src:
            cv["src"] = scene_chip_text(src)
    else:
        SCENE["conv"] = {"codec": str(codec or ""), "t0": SCENE.get("ta", 0.0), "end": None, "pct": None,
                         "src": scene_chip_text(src), "dst": scene_chip_text(dst or codec)}
    _FAST_WAKE.set()
    scene_status(label)


# 1.2.8: s que se deja ver la conversión terminada (1.6.4: la vía llena y el destino destellando = un loop) antes de pasar a la escena siguiente
CONV_END_HOLD = LOOP_SECS


def scene_convert_end():
    """Termina la conversión: el avance pasa a 100 % y el dibujo queda hasta terminar su loop (motif_loop_left, en scene_motif)."""
    cv = SCENE.get("conv")
    if SCENE["on"] and cv and cv.get("end") is None:
        scene_conv_progress(100)
        cv["end"] = SCENE.get("ta", 0.0)
        # 1.6.4: se acabó convert_fast_anim: la escena vuelve a animarse (vía llena + destello)
        _FAST_WAKE.set()


def scene_check(items=None, verdict=None, label=None):
    """1.2.5:"""
    if not SCENE["on"]:
        return
    prev = SCENE.get("check") or {}
    # 1.6.2: desde cuándo se ve el veredicto lo anota _draw_check al pintarlo (con el mismo veredicto no se reinicia)
    t_v = prev.get("t") if (verdict is not None and prev.get("verdict") == verdict) else None
    SCENE["check"] = {"items": items, "verdict": verdict, "t": t_v}
    # 1.6.1: la resolución (parpadeo + pulso) es otro tramo del dibujo: se espera aparte
    if verdict is not None and prev.get("verdict") != verdict:
        # (si no, la espera del escaneo «paga» también la de la resolución y el modo «wait» la salta)
        SCENE["gate_paid"] = SCENE["loop_paid"] = None
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
        _FAST_WAKE.set()
        return
    try:
        p = max(0.0, min(100.0, float(pct)))
    except (TypeError, ValueError):
        return
    p = max(p, cv.get("pct") or 0.0)
    # 1.6.4: en convert_fast_anim la escena solo despierta cuando cambia el % entero
    moved = int(p) != int(cv.get("pct") or -1.0)
    cv["pct"], SCENE["pct"] = p, p
    SCENE["frac"] = max(SCENE["frac"], min(0.94, 0.8 + 0.14 * p / 100.0))
    if moved:
        _FAST_WAKE.set()


SCENE_ASK_SECS = 20                                 # 1.1.1: s que espera el Enter de una conversión larga


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


# 1.2.0: s que dura el ciclo «Toca la pantalla…» ⇄ «¿Convertir este video?» (1.2.1)
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
            # 1.2.0: sin respuesta (se acabó la cuenta) = la predeterminada: convertir (1.4.2: o sustituir)
            result = True
        if not S["on"] and not result:
            return None
        return result
    finally:
        S["ask"] = None
        S["busy"] = busy_prev
        with quiet("scene_ask_enter close"):
            keys.close()
        # 1.6.8: respondida la petición (Enter, r, n o se acabó la cuenta), el teclado baja
        hide_keyboard()


# 1.7.1: s que espera la elección del idioma; sin respuesta sigue en inglés y no guarda (vuelve a preguntar la próxima vez)
LANG_PICK_SECS = 60
# 1.7.1: s que se ve «Seleccione idioma» en cada idioma y s que tarda en cambiar al del siguiente
LANG_TITLE_HOLD, LANG_TITLE_MORPH = 1.5, 0.4
# 1.7.1: teclas de siguiente / anterior (el teclado de iOS no tiene flechas); Enter acepta; 1-9 y 0 saltan al idioma 1-10
_LANG_NEXT, _LANG_PREV = "nNlLjJ .>\t", "pPhHkK,<"
_ARROW_RX = re.compile(r"\x1b[\[O]([ABCD])|\x1b")


def lang_pick_step(sel, n, text, enter_ok=True):
    """1.7.1: aplica lo tecleado `text` a la selección `sel` de `n` idiomas. (nueva selección, aceptada?, hubo cambio?). Flechas (→ ↓ siguiente · ← ↑ anterior),
    n / espacio / Tab siguiente, p anterior, 1-9 y 0 saltan, Enter acepta (si `enter_ok`; el Enter fantasma del arranque no cuenta)."""
    done, moved = False, False
    toks, i, s_ = [], 0, str(text or "")
    while i < len(s_):
        mt = _ARROW_RX.match(s_, i)
        if mt:
            toks.append({"C": ">", "B": ">", "D": "<", "A": "<"}.get(mt.group(1), ""))
            i = mt.end()
        else:
            toks.append(s_[i])
            i += 1
    for ch in toks:
        if not ch:
            continue
        if ch in "\r\n":
            if enter_ok:
                done = True
                break
            continue
        if ch in _LANG_NEXT:
            sel, moved = (sel + 1) % n, True
        elif ch in _LANG_PREV:
            sel, moved = (sel - 1) % n, True
        elif ch.isdigit() and ch.isascii():
            k = 9 if ch == "0" else int(ch) - 1
            if k < n:
                sel, moved = k, True
    return sel, done, moved


def lang_pick_start():
    """1.7.1: el idioma con que arranca la selección: el del sistema (LANG / LANGUAGE) si se reconoce; si no, el predeterminado."""
    for key in ("LANG", "LANGUAGE"):
        c = lang_parse(os.environ.get(key))
        if c in LANG_CODES:
            return c
    return DEFAULT_LANG


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
    ca = scene_cols(fit_text(LANG_SELECT_TEXT[codes[i % n]], room), cx)
    cb = scene_cols(fit_text(LANG_SELECT_TEXT[codes[(i + 1) % n]], room), cx)
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


def scene_lang_pick(secs=None):
    """1.7.1: DLPY_LANGUAGE=ask (el predeterminado): la escena pregunta el idioma. Devuelve el código elegido (ya aplicado con set_lang y guardado en la configuración) o None
    (sin escena, sin teclado, sin respuesta en `secs` s o ya hay un idioma elegido: todo sigue en el predeterminado y no se guarda, así que vuelve a preguntar)."""
    S = SCENE
    if not S["on"] or S.get("last_error") or not lang_ask_pending() or not countdown_supported():
        return None
    try:
        keys = _PosixKeys()
    except Exception as _ign:
        ignore("scene_lang_pick", _ign)
        return None
    secs = float(secs or LANG_PICK_SECS)
    codes = list(LANG_CODES)
    result, busy_prev = None, S.get("busy")
    try:
        input_unlock()
        drain_pending_input()
        t_w, hold = time.time(), SITE_HOLD_AT * SITE_SECS
        while S["on"] and S.get("ta", 0.0) < hold and time.time() - t_w < 6.0:       # primero termina la intro
            time.sleep(0.05)
        if not S["on"]:
            return None
        t0 = time.time()
        S["busy"] = True
        S["ask"] = {"kind": "lang", "codes": codes, "sel": codes.index(lang_pick_start()), "secs": secs, "t0": t0, "ta0": S.get("ta", 0.0), "tk": 0.0}
        done = False
        while not done and S["on"] and time.time() - t0 < secs:
            txt = keys.read(0.1)
            if not txt:
                continue
            if "\x03" in txt:
                raise KeyboardInterrupt
            if "\x04" in txt:
                raise EOFError
            # Enter fantasma
            ok_enter = not (time.time() - t0 < PHANTOM_SECS or time.time() - START_T < PHANTOM_BOOT)
            S["ask"]["sel"], done, moved = lang_pick_step(S["ask"]["sel"], len(codes), txt, ok_enter)
            if moved:
                S["ask"]["tk"] = time.time()
        if done and S["on"]:
            result = codes[S["ask"]["sel"]]
            S["ask"]["tk"] = time.time()
            time.sleep(0.3)                                           # se ve cómo queda la elección antes de seguir
        return result
    finally:
        S["ask"] = None
        S["busy"] = busy_prev
        with quiet("scene_lang_pick close"):
            keys.close()
        if result:
            set_lang(result)
            with quiet("scene_lang_pick save", OSError):
                # se guarda: no vuelve a preguntar (--config DLPY_LANGUAGE=ask lo pide otra vez)
                config_edit(["DLPY_LANGUAGE=" + result], ENV_FILE)
        hide_keyboard()


def scene_questions():
    """Antes:"""
    return False


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


def scene_handoff():
    """1.8.0: otra versión de DLpy va a correr en ESTE proceso (reexec_script, runpy) con la escena viva (--shortcutpick y --scb buscan las actualizaciones
    primero): la escena se cierra hacia el centro como al enviar, stdout y stderr vuelven a lo real y la versión nueva abre la suya desde cero.
    Sin escena no hace nada. True si cerró."""
    S = SCENE
    if not S["on"]:
        return False
    with quiet("scene_handoff"):
        scene_busy(False)
        if not S.get("last_error"):
            # el texto de estado («DLpy X · instalada») termina de transformarse y se lee
            time.sleep(SCENE_MORPH + 0.2)
        scene_outro()                             # el hilo de la escena pinta el cierre
    scene_stop(cursor=False)
    with quiet("scene_handoff"):
        while isinstance(sys.stdout, _SceneMute):
            sys.stdout = sys.stdout._inner
        while isinstance(sys.stderr, _SceneErrMute):
            sys.stderr = sys.stderr._inner
        sys.stdout.write(RESET + CURSOR_SHOW)
        sys.stdout.flush()
    return True


# ───────────────────── [UX3] Lista «Ver todos» con el estilo de la escena (0.9.5) ─────────────────────
# La lista completa (o la corta, si el formato del atajo ya no existe) hay que verla y deslizarla, así que la escena no puede
# pintarla: cede. Pero cede con su propio lenguaje: el texto cambia a «Ver todos», la escena se cierra hacia el centro, la lista abre con
# la regla de degradado del sitio, el título del video en blanco que se transforma y el estado en gris; números, flechas y marcas
# toman el color del sitio. Al elegir, la escena vuelve a abrirse desde el centro y sigue la descarga.
SCENE_LIST_SECS = 0.45                              # s que tarda en entrar la cabecera de la lista


def scene_list_top_cells(S, W, title, status, p, f):
    title, status = t_status(title), t_status(status)  # gettext: etiquetas de escena
    """Cabecera de la lista en el estilo de la escena (p de 0 a 1):"""
    a, b, cx = S['a'], S['b'], W // 2 + 1
    cells = {}
    opened = smooth(p / 0.6)
    for d in range(-14, 15):
        if abs(d) / 14.0 <= opened:
            cells[(cx + d, 1)] = ("─", mix6(a, b, (d + 14) / 28.0), None)
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
        go = bool(animate and ANIM and USE_COLOR and TRUECOLOR)
        t0 = time.monotonic()
        while True:
            # 1.9.8: avanza por tiempo real (no por número de cuadros) y duerme hasta el siguiente límite de cuadro
            el = time.monotonic() - t0
            p = min(1.0, el / SCENE_LIST_SECS) if go else 1.0
            scene_paint(out, scene_list_top_cells(S, W, title, status, p, int(el * SITE_FPS)), st, W, 3)
            if p >= 1.0:
                break
            time.sleep(frame_gap(el, SITE_FPS))
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


# ── Error en la escena (1.0.8; en 1.5.7 pasó del núcleo a la UX): el texto corto y limpio, y cómo se integra en D L P Y ──
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


# ───────────────────── [UX4] Puente UX → resto del script (1.5.7) ─────────────────────
# La ÚNICA puerta de la escena. Lo que está fuera del área UX (la UIM, el núcleo, actualizaciones, limpieza, entrega, modo atajo, main)
# no llama a scene_* / rail_* / site_* ni lee SCENE por dentro: usa estas funciones ux_*, que sin escena no hacen nada o devuelven lo neutro.
# Cada ux_* de abajo llama a la función de la escena por su nombre en el momento de usarla (así una prueba puede sustituir la de dentro).
# Para añadir algo que la UIM o el resto deban decirle a la escena: función ux_* aquí; el selftest [T29] avisa si alguien se salta el puente.
# ajustes y tabla que la UIM y el resto leen tal cual
UX_SHARED = ("SCENE_DWELL", "SCENE_PIP", "SCENE_CLEAN_SECS", "SCENE_REPLACE_SECS", "STREAM_KINDS")


# ── La UIM (DownloadUI y Bar) avisa de la descarga ──
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


def ux_pp_progress(pct):
    """El avance real de la unión (1.3.9); sin escena no se guarda."""
    if SCENE["on"]:
        SCENE["pp_pct"] = pct


# ── Funciones de la escena que el resto del script usa tal cual ──
def ux_lang_pick(*a, **k):
    return scene_lang_pick(*a, **k)


def ux_language_check(code):
    """1.9.2: publica en D L P Y la consulta SHA del actualizador de idiomas y espera a que se teclee el GET real."""
    code = str(code or "").lower()
    if not SCENE["on"] or code not in PACK_LANGS:
        return False
    scene_brand()
    ux_set(lang_code=code, lang_asset="sha256")
    scene_busy(True)
    label = "Comprobando idioma " + LANG_NAMES.get(code, code)
    scene_status(label)
    scene_wait_step(label)
    return True


def ux_language_check_done(code, result="current"):
    """Resultado ✓/✗ de la consulta SHA; en caso de actualización deja D L P Y listo para el GET del .mo."""
    code = str(code or "").lower()
    if not SCENE["on"] or SCENE.get("lang_code") != code:
        return False
    name = LANG_NAMES.get(code, code)
    if result == "failed":
        label = t_display("Error") + ": " + t_display("Idioma")
    elif result == "changed":
        label = "Comprobando idioma %s · actualización disponible" % name
    else:
        label = "Comprobando idioma %s · al día" % name
    scene_busy(False)
    scene_status(label)
    scene_wait_step(label)
    time.sleep(max(0.0, float(scene_dwell(SCENE_DWELL))))
    if result != "changed":
        scene_brand_end()
        ux_pop("lang_code")
        ux_pop("lang_asset")
    return True


def ux_language_download(code):
    """1.9.2: publica en D L P Y la descarga real del catálogo .mo seleccionado."""
    code = str(code or "").lower()
    if not SCENE["on"] or code not in PACK_LANGS:
        return False
    scene_brand()
    ux_set(lang_code=code, lang_asset="mo")
    scene_busy(True)
    label = "Descargando idioma " + LANG_NAMES.get(code, code)
    scene_status(label)
    scene_wait_step(label)
    return True


def ux_language_done(code, ok=True):
    """1.9.2: muestra el resultado del GET, deja verlo y devuelve la escena a su flujo anterior."""
    code = str(code or "").lower()
    if not SCENE["on"] or SCENE.get("lang_code") != code:
        return False
    name = LANG_NAMES.get(code, code)
    if ok:
        # 2.0.6: «Idioma · Lingua impostata» (etc.) en verde en la escena
        set_msg = LANG_SET_TEXT.get(code) or LANG_SET_TEXT.get("es") or "Idioma establecido"
        label = t_display("Idioma") + " · " + set_msg
    else:
        label = t_display("Error") + ": " + t_display("Idioma")
    scene_status(label)
    if ok:
        SCENE["label_ok"] = True
    scene_wait_step(label)
    time.sleep(max(0.0, float(scene_dwell(SCENE_DWELL))))
    scene_brand_end()
    ux_pop("lang_code")
    ux_pop("lang_asset")
    return True


def ux_ask_enter(*a, **k):
    return scene_ask_enter(*a, **k)


def ux_brand_end(*a, **k):
    return scene_brand_end(*a, **k)


def ux_check(*a, **k):
    return scene_check(*a, **k)


def ux_check_end(*a, **k):
    return scene_check_end(*a, **k)


def ux_code_change(*a, **k):
    return code_change(*a, **k)


def ux_conv_progress(*a, **k):
    return scene_conv_progress(*a, **k)


def ux_convert(*a, **k):
    return scene_convert(*a, **k)


def ux_convert_end(*a, **k):
    return scene_convert_end(*a, **k)


def ux_ffmpeg_tick():
    """1.6.4: s entre lecturas del avance de ffmpeg: con convert_fast_anim (DLPY_CONVERT_LIGHT_ANIMATION) cada FFMPEG_TICK_FAST, si no cada FFMPEG_TICK."""
    return FFMPEG_TICK_FAST if CONVERT_FAST_ANIM else FFMPEG_TICK


def ux_early_site_intro(*a, **k):
    return early_site_intro(*a, **k)


def ux_end(*a, **k):
    return scene_end(*a, **k)


def ux_error_end(*a, **k):
    return scene_error_end(*a, **k)


def ux_format_kinds(*a, **k):
    return format_kinds(*a, **k)


def ux_handoff(*a, **k):
    return scene_handoff(*a, **k)


def ux_hold(*a, **k):
    return scene_hold(*a, **k)


def ux_list_enter(*a, **k):
    return scene_list_enter(*a, **k)


def ux_list_leave(*a, **k):
    return scene_list_leave(*a, **k)


def ux_list_top(*a, **k):
    return scene_list_top(*a, **k)


def ux_note(*a, **k):
    return scene_note(*a, **k)


def ux_questions(*a, **k):
    return scene_questions(*a, **k)


def ux_reset_site_state(*a, **k):
    return reset_site_state(*a, **k)


def ux_set_error(*a, **k):
    return scene_set_error(*a, **k)


def ux_shape(*a, **k):
    return scene_shape(*a, **k)


def ux_site_intro(*a, **k):
    return site_intro(*a, **k)


def ux_site_theme_apply(*a, **k):
    return site_theme_apply(*a, **k)


def ux_start(*a, **k):
    return scene_start(*a, **k)


def ux_status(*a, **k):
    return scene_status(*a, **k)


def ux_stop(*a, **k):
    return scene_stop(*a, **k)


def ux_title(*a, **k):
    return scene_title(*a, **k)


def ux_wait_anim(*a, **k):
    return scene_wait_anim(*a, **k)


def ux_welcome(*a, **k):
    return scene_welcome(*a, **k)


def ux_welcome_kind(*a, **k):
    return welcome_kind(*a, **k)


# ═══════════════════ FIN ÁREA UX ═══════════════════


# ═══════════════════ ÁREA UIM · la interfaz SIMPLE sin shortcutmode (menú, banner, listas, progreso) ═══════════════════
# UIM = lo que se ve SIN escena: banner de texto [B4], progreso simple [B5] y teclado / cuenta regresiva [B6]. Es la interfaz mínima: texto plano,
# una línea de avance sin hilo, sin degradados, sin animaciones, sin intro ni disolución (todo eso es de la UX), y debe verse igual en un terminal sin color.
# REGLA 1.5.8: aquí NO entra nada decorativo (grad, mix, Thread, SITE_GLITCH, _rn, theme_rgb, ANIM_LIVE, OUTRO…): el selftest [T29] lo comprueba.
# La UIM avisa a la escena solo con las funciones ux_* de [UX4] (que no hacen nada sin escena) y pinta lo suyo.

# ───────────────────── [B4] UIM · Pantalla: banner, títulos y listas ─────────────────────
def rule(title=None, w=None):
    title = t_display(title) if title else title  # 1.7.0
    """UIM · línea simple a todo el ancho (sin degradado); con título: «━━ TÍTULO ━━━━…»."""
    w = w or safe_width()
    if not title:
        return paint(FILL * w, "gray")
    t = f" {fit_text(title, max(1, w - 6))} "
    return paint(FILL * 2, "gray") + paint(t, "white", True) + paint(FILL * max(0, w - 2 - dwidth(t)), "gray")


def title_bar(left, right):
    left, right = t_display(left), t_display(right)  # 1.7.0
    """Cabecera «▍izquierda … derecha» a todo el ancho seguro."""
    w = safe_width()
    gap = max(1, w - 1 - dwidth(left) - dwidth(right))
    return paint("▍", "orange") + paint(left, "white", True) + " " * gap + right


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
# líneas que ocupa el encabezado (para repartir la pantalla)
BANNER = {"h": 3}


def scale_state(frac, kind):
    """«ok» / «warn» / «crit» de una escala de la barra. kind: «phone» (equipo) o «mine» (DLpy)."""
    if frac is None:
        return "ok"
    crit = SCALE_CRIT_PHONE if kind == "phone" else SCALE_CRIT_MINE
    return "crit" if frac >= crit else ("warn" if frac >= SCALE_WARN else "ok")


def banner_width():
    """Ancho del encabezado y de los bloques de texto fijos: el ancho seguro, entre 20 y 60 columnas."""
    return max(20, min(safe_width(), 60))


def banner_rows(w):
    """UIM · encabezado de texto simple, cada línea de `w` columnas como mucho: versión + debug, sistema y espacio (en texto, sin barra)."""
    state = paint(t_display("DEBUG activo"), "amber", True) if DEBUG else paint(t_display("DEBUG desactivado"), "gray")
    try:
        r = storage_report()
        _head, detail, over = storage_lines()
        mine = r["total"] / CLEAN_LIMIT if CLEAN_LIMIT > 0 else 0.0
    except Exception:
        detail, over, mine = [], False, 0.0
    phone = disk_fraction()
    left = paint("▍", "orange") + paint(f"DLpy v{VERSION}", "white", True)
    rows = [left + " " * max(1, w - dwidth(left) - dwidth(state)) + state,
            paint(fit_text(f"  {platform_name()} · {machine_name()}", w), "gray")]
    space = ((paint(f"{device_label()} {phone * 100:.0f}%", SCALE_COLOR[scale_state(phone, "phone")]) + paint(" · ", "gray")) if phone is not None else "")
    rows.append("  " + space + paint(f"DLpy {mine * 100:.0f}%", SCALE_COLOR[scale_state(mine, "mine")]))
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
               "mp4a": "AAC", "aac": "AAC", "opus": "Opus", "prores": "ProRes", "ec-3": "E-AC-3", "eac3": "E-AC-3", "ac-3": "AC-3",
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
    """Borra la consola y deja solo el banner."""
    if DEBUG:
        print()
        print(paint(EMPTY * min(safe_width(), 40), "track"))
        banner()
        return
    if sys.stdout.isatty() and clear_mode_seq(CLEAR_MODE) is None:     # 1.3.2: con un DLPY_CLEAR_MODE propio se borra con él
        _soft_clear_screen()
        return
    native_clear()
    probe_cols(refresh=True)              # por si se giró el teléfono o cambió el tamaño
    banner()


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
        ok = True
    finally:
        sys.stdout = real                       # quita la envoltura
    body = "".join(soft.buf)
    with quiet("soft_clear"):
        # ESC[r suelta la región de desplazamiento anterior; el banner la vuelve a fijar si hace falta
        real.write("\x1b[?2026h\x1b[r\x1b[0m\x1b[H" + body + "\x1b[J" + PURGE_SEQ + "\x1b[?2026l")
        real.flush()
    return ok


def uim_final_clear():
    """UIM · lo último antes de enviar el archivo al atajo (sin escena): solo limpia la consola. 1.5.8: sin disolución, sin pausa, sin degradado."""
    if DEBUG or not sys.stdout.isatty():
        return False
    try:
        native_clear()
        sys.stdout.write(RESET + CURSOR_SHOW)
        sys.stdout.flush()
        return True
    except KeyboardInterrupt:
        raise
    except Exception as _ign:
        ignore("uim_final_clear", _ign)
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
    header(t_display("ARCHIVO"), gap=False)
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


def legend(keys):
    """«✓ compatible Apple   ◆ pista original» (marca de color + texto gris)."""
    print("\n".join("  " + ln for ln in _legend_lines(keys)))


def _legend_lines(keys):
    w = term_width() - 2
    lines, cur, curlen = [], [], 0
    for k in keys:
        _ft = t_display(FLAG_TEXT[k])  # 1.7.0
        plain = "x " + _ft
        colored = flag_mark(k) + " " + paint(_ft, "gray")
        add = len(plain) + (3 if cur else 0)
        if cur and curlen + add > w:
            lines.append("   ".join(cur))
            cur, curlen, add = [], 0, len(plain)
        cur.append(colored)
        curlen += add
    if cur:
        lines.append("   ".join(cur))
    return lines


LEGEND_MARKS = {"✓": "mint", "⬆": "orange", "●": "mint", "✗": "red", "◆": "amber", "▸": "orange", "★": "magenta"}


def legend_lines(text):
    """2.0.0: líneas de una leyenda de lista con su texto ya traducido (ej. «✓ actual · ⬆ la de actualizar»), cada una de `term_width() - 2` columnas como mucho."""
    return wrap_text(t_display(text), term_width() - 2)


def legend_note(text):
    """2.0.0: la leyenda de una lista con un texto ya existente en el catálogo: sangrada 2 columnas como legend(), las marcas con su color y el resto en gris."""
    rx = "([" + re.escape("".join(LEGEND_MARKS)) + "])"
    for ln in legend_lines(text):
        print("  " + "".join(paint(p, LEGEND_MARKS[p]) if p in LEGEND_MARKS else paint(p, "gray") for p in re.split(rx, ln) if p))


def print_rows(rows, flags, head=None, num_w=None, clip=None):
    """2.0.0: LA lista numerada de la UIM y de la UX (formatos, pistas, versiones, pendientes, configuración y opciones); todas se dibujan aquí.
    rows: [{"n": número, "flags": {…}, "cols": [texto, …]}] (todas con las mismas columnas).
    flags: marcas a la derecha; una marca puede ser un grupo (tupla de claves que comparten celda: sale la primera presente).
    num_w: ancho común de los números cuando se pintan varias tablas seguidas. clip: índice de la columna que se recorta para que cada fila ocupe una sola línea."""
    if not rows:
        return
    w = term_width()
    nw = max(max(len(str(r["n"])) for r in rows), num_w or 0)
    pw = 1 + nw + 2                                   # « n  »
    logo_w = apple_col_width(rows)                    # 1.9.9: la columna «logo» es la manzana (1 o 2 celdas)
    fw = max(1, sum(logo_w if k == "logo" else 1 for k in flags) + len(flags) - 1)   # ancho de la columna de marcas
    ncol = len(rows[0]["cols"])
    if clip is not None and 0 <= clip < ncol:         # 2.0.0: la columna larga (título, valor) se recorta; el resto se mide entera
        others = [max([dwidth(r["cols"][i]) for r in rows] + ([dwidth(head[i])] if head else [])) for i in range(ncol) if i != clip]
        room_c = max(4, w - pw - sum(others) - 2 * (ncol - 1) - 1 - fw - 1)
        rows = [dict(r, cols=[fit_text(c, room_c) if i == clip else c for i, c in enumerate(r["cols"])]) for r in rows]
    allr = [r["cols"] for r in rows] + ([head] if head else [])
    widths = [max(dwidth(c[i]) for c in allr) for i in range(ncol)]

    def prefix(r):               # ★ («b») o ▸ (predeterminada) ocupan el margen: no restan ancho
        return (flag_mark("best") if "best" in r["flags"]
                else flag_mark("default") if "default" in r["flags"] else " ") \
            + paint(f"{r['n']:>{nw}}", "orange", True) + "  "

    def line(r, body_vis, body):
        gap = max(1, w - pw - body_vis - fw - 1)
        def cell(k):
            if k == "logo":
                m = apple_row_mark(r)
                return m + " " * (logo_w - dwidth(m)) if m else " " * logo_w
            if isinstance(k, tuple):                  # 2.0.0: varias marcas en una misma celda
                hit = next((x for x in k if x in r["flags"]), None)
                return flag_mark(hit) if hit else " "
            return flag_mark(k) if k in r["flags"] else " "
        return prefix(r) + body + " " * gap + " ".join(cell(k) for k in flags)

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

    short = {t("con audio"): "c/audio", t("sin audio"): "s/audio", "con audio": "c/audio", "sin audio": "s/audio"}
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


def drain_pending_input(max_wait=0.08):
    """Descarta bytes ya pendientes en stdin (Enter residual al abrir desde Atajos)."""
    if RUNTIME["nested_ios"]:
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
    """input(). 1.6.8: con la escena viva, al responder baja el teclado."""
    try:
        return _ask_line(prompt, phantom, plain)
    finally:
        if ux_on():
            hide_keyboard()


def _ask_line(prompt, phantom=True, plain=None):
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
    # Enter vacío / «fantasma» no es un aviso; una opción escrita y no válida, sí
    typed_ok = bool(str(typed or "").strip())
    if erase_input_line(cur, typed):
        if typed_ok:
            # el prompt rojo se repite en su línea: la bottombar avisa
            diagnostic_report("A", warn or "Respuesta inválida: " + str(typed).strip()[:60])
        return bad or cur
    if warn:
        m_warn(warn)                                    # m_warn ya cuenta el aviso
    elif typed_ok:
        diagnostic_report("A", "Respuesta inválida: " + str(typed).strip()[:60])
    return cur


def bad_prompt(why):
    """«✗ 1-12, b o q ▸ »: el prompt tras una opción inválida (la ayuda corta va en la misma línea)."""
    return paint("✗", "red", True) + " " + paint(why, "gray") + " " + paint("▸", "orange", True) + " "


# ───────────────────── [B5] UIM · Progreso simple: Bar y DownloadUI ─────────────────────
def speed_text(v):
    """Velocidad de bajada con el mismo formato en todas las barras."""
    return f"↓ {human_size(v)}/s"


def spaced(text):
    """«3.0MB/s» → «3.0 MB/s» (número y unidad separados, como en dpt)."""
    return re.sub(r"(\d)(B|KB|MB|GB|TB)\b", r"\1 \2", str(text))


def size_pair(done, total):
    """«20/48 MB» (o GB si el total pasa de 1 GB)."""
    u, d = ("GB", 1024 ** 3) if total >= 1024 ** 3 else ("MB", 1024 ** 2)
    f = "{:.1f}" if d > 1024 ** 2 else "{:.0f}"
    return f"{f.format(done / d)}/{f.format(total / d)} {u}"


_CURSOR = {"hidden": False, "atexit": False}


def cursor_show():
    """Devuelve el cursor (no hace nada si no estaba oculto)."""
    if not _CURSOR["hidden"]:
        return
    _CURSOR["hidden"] = False
    with quiet("cursor_show"):
        sys.stdout.write(CURSOR_SHOW)
        sys.stdout.flush()


class Bar:
    """UIM · progreso SIMPLE (1.5.8): sin hilo, sin panel, sin degradado, sin animación ni vigilancia de archivos.
    Al empezar: «etiqueta...». Mientras hay avance conocido: UNA línea («  42%  etiqueta  velocidad ETA») que se reescribe en su sitio como mucho
    una vez por segundo, cuando quien la usa llama a set()/kick(). Al terminar: «etiqueta: listo (tamaño)». Con escena (UX) no pinta nada propio."""

    TICK = 1.0                              # s mínimos entre dos reescrituras de la línea de avance

    def __init__(self, panel=False):        # `panel` se acepta por compatibilidad: la UIM ya no tiene panel
        self.lock = threading.RLock()
        self.active = False
        self.label, self.pct, self.tail = "", None, ""
        self.indet, self.hold, self.t0 = True, 0.0, 0.0
        self.hook_t, self.last_draw, self.last_len = 0.0, 0.0, 0
        self.final_tail, self.final_size = "", ""
        self.step, self.sizes, self.engine = "", None, ""
        self.hist = []                       # velocidades recientes (DownloadUI las reinicia por pista)
        self.w = safe_width()

    @property
    def th(self):
        """Nombre de cuando había hilo: verdadero mientras la barra está activa (DownloadUI y _say lo consultan)."""
        return True if self.active else None

    def _live(self):
        return sys.stdout.isatty() and not DEBUG and not QUIET["on"] and not ux_on()

    # ── ciclo de vida ──
    def start(self, label, indeterminate=True, tail=""):
        self.stop()
        self.w = safe_width()
        with self.lock:
            self.label, self.pct, self.tail = label, None, tail
            self.indet, self.hold, self.t0 = indeterminate, 0.0, time.time()
            self.hook_t, self.last_draw = 0.0, 0.0
            self.final_tail = self.final_size = ""
            self.step, self.sizes, self.engine = "", None, ""
            self.hist = []
        RUNTIME["bar"] = self
        self.active = True
        m_info(label + "...")

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
        self._tick()

    def kick(self):
        """Quien usa la barra avisa de que hay algo nuevo: reescribe la línea de avance si toca."""
        self._tick()

    def _tick(self):
        with self.lock:
            if not self.active or (self.pct is None and not self.tail) or not self._live():
                return
            now = time.time()
            if now - self.last_draw < self.TICK or now < self.hold:
                return
            self.last_draw = now
            head = (f"[{self.step}] " if self.step else "") + (f"{self.pct:.0f}%  {self.label}" if self.pct is not None else self.label) + (f"  {self.tail}" if self.tail else "")
            sys.stdout.write(CLR + nowrap(paint(fit_text("  " + head, max(10, self.w - 1)), "gray")))
            sys.stdout.flush()
            self.last_len = 1

    def _erase(self):
        """Borra la línea de avance (con `self.lock` tomado)."""
        if self.last_len:
            sys.stdout.write(CLR)
            sys.stdout.flush()
        self.last_len = 0

    def stop(self, msg=None, level="ok", keep=False):
        if self.active:
            self.active = False
            if not keep:
                with self.lock:
                    self._erase()
        if RUNTIME["bar"] is self and not keep:
            RUNTIME["bar"] = None
        if msg:
            {"ok": m_ok, "warn": m_warn, "info": m_info, "err": m_err}[level](msg)

    def done(self, min_secs=0.0):
        """Borra la línea de avance y deja «etiqueta: listo (tamaño)». Si duró menos de min_secs solo se borra."""
        elapsed = time.time() - self.t0
        with self.lock:
            label = self.label
            size = self.final_size or spaced(self.final_tail)
        self.stop()
        if elapsed < min_secs:
            return
        m_ok(f"{label}: listo" + (f" ({size})" if size else ""))

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
            self._erase()

    def watch(self, paths, total=0):
        """Compatibilidad: la UIM ya no vigila archivos para calcular el avance (solo cuenta lo que informa yt-dlp)."""
        return None


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
    # 1.3.6: «sd» / «hd» sin datos en el hook: es video
    if "video" in STREAM_KINDS.get(str(info.get("format_id") or ""), ()):
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
    """UIM · una barra simple por proceso (la UX recibe los avisos por el puente ux_download_*):"""

    def __init__(self, vkey=None, resumed=False):
        self.bar = Bar(panel=True)
        self.key = None
        self._started = False    # 1.7.0: ya se abrió alguna pista (la primera puede llegar sin nombre)
        self._key_none = False
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

    def begin(self):
        ux_download_begin()
        self.bar.start("Preparando")

    def hook(self, d):
        """Hook de progreso de yt-dlp: un fallo de la interfaz nunca debe abortar la descarga."""
        if d.get("status") == "downloading":
            net_touch()                                       # 1.8.8: el avance de la descarga es actividad de red
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
            if self._started and self._key_none and key is not None:
                # 1.7.0: la primera vez llegó sin nombre y ahora sí lo trae: es la misma pista, solo se completa el nombre
                self.key, self._key_none = key, False
            if key != self.key or not self._started:
                if b.th and self.key is not None:
                    b.done()
                lbl = stream_label(d)
                if b.th:
                    b.set(label=lbl, tail="")
                else:
                    b.start(lbl)
                self.seen += 1
                # 1.5.7: la escena (UX) se entera por el puente: forma, pista y datos reales
                ux_download_stream(d, self.seen, self.total)
                b.set(step=f"{self.seen}/{self.total}" if self.total > 1 and self.seen <= self.total
                      else "")
                with b.lock:
                    b.hist, b.sizes, b.pct, b.indet = [], None, None, True
                self.key = key
                self._started, self._key_none = True, key is None
                self._reset_speed()
                if self.resumed:
                    self._base_b = d.get("downloaded_bytes") or 0
                fn = d.get("filename") or ""
                b.watch([d.get("tmpfilename"), fn + ".part" if fn else None, fn],
                        (d.get("info_dict") or {}).get("filesize")
                        or (d.get("info_dict") or {}).get("filesize_approx") or 0)
            b.hook_t = time.time()             # yt-dlp está avisando: _poll no interviene
            pct = progress_pct(d)
            ux_download_progress(pct)
            parts = []
            spd = self._speed(d)
            ux_download_speed(spd)   # 1.7.0: la velocidad real alimenta la animación de la escena
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
            ux_download_stream_done(d)
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
            ux_pp_start(name)
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


# ───────────────────── [B6] UIM · Terminal: teclado y cuenta regresiva ─────────────────────
def hide_keyboard(settle=0.0):
    """iOS (a-Shell): baja el teclado. `settle` espera (s) a que el terminal tome su alto nuevo."""
    with quiet("hide_keyboard"):
        sh_run("hideKeyboard >/dev/null 2>&1")
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
LOCK_INPUT = _flag_env("DLPY_INPUT_LOCK_ENABLED", False)      # apagado: congelaba a-Shell


def input_lock():
    """iOS (a-Shell):"""
    if not LOCK_INPUT or RUNTIME["nested_ios"] or INPUT_LOCK["fd"] is not None:
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


def reexec_script():
    """Ejecuta SCRIPT_PATH (recién instalado o restaurado)"""
    import runpy
    with quiet("reexec_script"):
        if RUNTIME["bar"] is not None:
            RUNTIME["bar"].stop()
    # 1.8.0: con la escena viva (--shortcutpick / --scb) se cierra antes de que corra la versión nueva (por el puente [UX4], como todo lo de fuera de la UX)
    ux_handoff()
    with quiet("reexec_script"):
        sys.stdout.flush()
        sys.stderr.flush()
    # a-Shell: ni tcsetattr ni select sobre stdin aquí
    sys._dlpy_reexec = True
    runpy.run_path(SCRIPT_PATH, run_name="__main__")


def _esc_next(esc, ch):
    """1.7.5: estado de una secuencia de escape tras recibir `ch` (False = terminó). ESC [ … A y ESC O A (flechas en modo aplicación): esta última lleva una letra más."""
    if ch == "O" and esc is True:
        return "O"
    return False if (ch.isalpha() or ch == "~") else esc


def timed_input(prompt, seconds=WAIT_SECONDS, phantom=True, plain=None):
    """Cuenta regresiva. 1.6.8: con la escena viva, al responder baja el teclado."""
    try:
        return _timed_input(prompt, seconds, phantom, plain)
    finally:
        if ux_on():
            hide_keyboard()


def _timed_input(prompt, seconds=WAIT_SECONDS, phantom=True, plain=None):
    if not countdown_supported():
        return ask_line(prompt, phantom, plain)
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
                    sys.stdout.write(CLR + prompt + paint(t_display("Sin respuesta"), "gray") + "\n")
                    sys.stdout.flush()
                    return None
                secs = int(left) + 1
                # 1.5.8 (UIM): solo el número de segundos, sin barra ni degradado
                key = secs
                if key != shown:
                    shown = key
                    sys.stdout.write(CLR + nowrap(prompt + paint(f" {secs} s", "amber" if secs <= 3 else "gray")))
                    sys.stdout.flush()
                timeout = 0.1
            text = keys.read(timeout)
            if not text:
                continue
            for ch in text:
                if esc:                       # saltar secuencias de flechas, etc.
                    esc = _esc_next(esc, ch)
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


# ═══════════════════ FIN ÁREA UIM ═══════════════════


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


YN_KEYS = {
    "es": ("S", "N"), "en": ("Y", "N"), "pt": ("S", "N"), "fr": ("O", "N"),
    "de": ("J", "N"), "it": ("S", "N"), "ru": ("Д", "Н"), "zh": ("Y", "N"),
    "hi": ("Y", "N"), "ar": ("Y", "N"), "ja": ("Y", "N"), "ko": ("Y", "N"), "pl": ("T", "N"),  # 2.0.8: polaco Tak/Nie
}


def _yn_keys():
    return YN_KEYS.get(lang_effective(LANG), ("S", "N"))  # 2.0.8: respaldo español


def parse_yn(ans, default=True):
    """True/False según la respuesta; acepta las teclas locales y alias comunes; Enter = default."""
    a = (ans or "").strip().casefold()
    if a == "":
        return default
    yes_key, no_key = _yn_keys()
    if a in {yes_key.casefold(), "s", "si", "sí", "y", "yes"}:
        return True
    if a in {no_key.casefold(), "n", "no"}:
        return False
    return None


YN_SUFFIX_RE = re.compile(r"\s*(?:\([^\s/()]/[^\s/()](?:/[a-zA-Z])?\))?\s*▸?\s*$")


def yn_prompt(msg, default=True, alt=None):
    """Pregunta localizada con tecla de respuesta según el idioma activo."""
    base = YN_SUFFIX_RE.sub("", str(msg)).strip()
    base = t_display(base)
    yes_key, no_key = _yn_keys()
    keys = (yes_key.upper() if default else yes_key.lower()) + "/" + (no_key.lower() if default else no_key.upper())
    return f"{base} ({keys}{'/' + alt[0] if alt else ''}) ▸ "


def yn_line(default=True, alt=None):
    """Opciones Sí/No traducidas; la tecla de la opción por omisión va en mayúscula."""
    def opt(key, label, on):               # la opción por omisión resalta; la otra queda en gris
        return (paint(f"[{key}]", "orange", True) + " " + paint(label, "white", True) if on
                else paint(f"[{key}] {label}", "gray"))
    yes_key, no_key = _yn_keys()
    extra = ("  " + paint(f"[{alt[0]}] {t_display(alt[1])}", "gray")) if alt else ""
    return (" " + opt(yes_key.upper() if default else yes_key.lower(), t_display("Sí"), default) + "  "
            + opt(no_key.lower() if default else no_key.upper(), t_display("No"), not default) + extra + " " + paint("▸", "orange", True) + " ")


def print_question(text):
    """Pregunta traducida en blanco y negrita, sin el sufijo de teclas."""
    base = YN_SUFFIX_RE.sub("", str(text)).strip()
    base = t_display(base)
    for i, ln in enumerate(wrap_text(base, term_width() - 1)):
        print((paint("▍", "orange") if i == 0 else " ") + paint(ln, "white", True))


def ask_yn(prompt, default=True, seconds=False, alt=None):
    """Pregunta s/n y la repite hasta recibir una respuesta válida."""
    # 0.8.2: --shortcutpick no pregunta antes de la descarga: respuesta predeterminada
    if QUIET["on"]:
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


def kbps_text(k):
    """«850 kbps», «2.1 Mbps»; None si no hay dato."""
    return fmt_kbps(k) if k else None


def fmt_kbps(k):
    k = float(k)
    # 1.7.5: 999.5 ya se redondea a «1000»
    return f"{loc_num(k / 1000, 1)} Mbps" if k >= 999.5 else f"{loc_num(k, 0)} kbps"


def precise_size(n):
    """Como human_size pero con GB a 2 decimales y 0B explícito; decimal según idioma."""
    n = int(n or 0)
    if n < 1024:
        return f"{loc_num(n, 0)}B"
    x = float(n)
    for u in ("KB", "MB", "GB"):
        x /= 1024
        if x < 1023.95 or u == "GB":                   # 1.7.5: con 1 decimal 1023.95 ya se lee «1024.0»
            return f"{loc_num(x, 2)}{u}" if u == "GB" else f"{loc_num(x, 1)}{u}"


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
    """Etiqueta de un formato SIN resolución conocida, tal cual la da yt-dlp (1.6.0: nada inventado, ya no «id1» ni «?»):
    su «resolution» (si no es «unknown»), si no su «format_note», si no su «format_id» sin tocar."""
    for key in ("resolution", "format_note"):
        val = str(f.get(key) or "").strip()
        if val and val.lower() not in ("unknown", "none", "?"):
            return val
    return str(f.get("format_id") or "").strip() or "?"


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
    if apple_unsure(f):
        flags.add("unsure")                           # 1.9.9: «?» en la lista, como el JSON
    return {"n": n, "flags": flags,
            "cols": [f.get("ext", "?"), f"{codec} {abr:.0f}k" if abr else codec,
                     f.get("language") or "",
                     human_size(f.get("filesize") or f.get("filesize_approx"))]}


AUDIO_ONLY_EXTS = ("m4a", "mp3", "aac", "wav", "aiff", "caf", "flac", "ogg", "opus", "weba")


def real_size(f):
    """1.6.0: (ancho, alto) REALES que yt-dlp informa aunque falte «height»: de «resolution» («1280x720») o, si no,
    de «format_note» / «format» («720p», «1080p60»). (None, None) si no hay ninguno: nunca se inventa una resolución."""
    for key in ("resolution", "format_note", "format"):
        s = str(f.get(key) or "")
        m = re.search(r"(?<!\d)(\d{3,5})\s*[x×]\s*(\d{3,5})(?!\d)", s)
        if m:
            return int(m.group(1)), int(m.group(2))
        m = re.search(r"(?<![\d.])(\d{3,4})[pi](?![A-Za-z])", s)
        if m and int(m.group(1)) >= 100:
            return None, int(m.group(1))
    return None, None


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
    # 1.6.0: sin «height» pero con «resolution»/«format_note» reales: se usan (antes salía «sd»/«hd»)
    if not f.get("height"):
        _w, _h = real_size(f)
        if _h:
            f["height"] = _h
            if _w and not f.get("width"):
                f["width"] = _w
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
    return {"n": n, "flags": ({"apple"} if apple_video(f) else set()) | ({"unsure"} if apple_unsure(f) else set()),
            "cols": [res_label(f), f.get("ext", "?"),
                     (f.get("vcodec") or "?").split(".")[0] + ("?" if f.get("_guess") else ""),
                     range_label(f),
                     t("con audio") if has(f.get("acodec")) else t("sin audio"),
                     human_size(f.get("filesize") or f.get("filesize_approx"))]}


UI_LINES = int(env_get("DLPY_UI_LINES", "26").strip() or 26) if env_get("DLPY_UI_LINES", "26").strip().isdecimal() else 26


def ui_lines():
    """Líneas de la interfaz, banner incluido: 26 siempre; DLPY_UI_LINES=0 usa el alto del terminal."""
    if UI_LINES:
        return UI_LINES
    try:
        return term_rows()
    except (OSError, ValueError):
        return 24


def banner_height():
    """Líneas ocupadas arriba: únicamente el encabezado."""
    return BANNER["h"]


def list_cap(overhead=16):
    """Filas máximas de la lista de formatos dentro de las 26 líneas de la interfaz."""
    env = env_get("DLPY_LIST_VISIBLE_ROWS", "").strip()
    if env.isdecimal():
        return int(env) or 10 ** 6
    return max(8, ui_lines() - overhead)


def visible_cap(overhead, lines=None):
    """Filas de una lista que caben en las 26 líneas de la interfaz. None solo con DLPY_LIST_VISIBLE_ROWS=0."""
    env = env_get("DLPY_LIST_VISIBLE_ROWS", "").strip()
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
        header(t_display("ELEGIR PISTA PREDETERMINADA") + (f" · +{len(trows) - len(vis)} " + t_display("más") if hid else ""), gap=False)
        m_info("Se detectaron varios idiomas.")
        legend(keys)
        print_rows([trows[i] for i in vis] if hid else trows, keys, [t_display(h) for h in TRACK_HEAD])
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
        header(t_display("ELEGIR PISTAS DE AUDIO ADICIONAL") + (f" · +{len(orows) - len(vis)} " + t_display("más") if hid else ""), gap=False)
        legend(keys)
        print_rows([orows[i] for i in vis] if hid else orows, keys, [t_display(h) for h in TRACK_HEAD])
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
                # 1.7.5: ffmpeg puede dar un tiempo negativo al arrancar
                secs = max(0.0, int(ln.split("=", 1)[1]) / 1e6)
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


def _read_progress_extra(pfile):
    """1.6.9: (fotogramas por segundo, bytes escritos) reales del archivo -progress de ffmpeg; None donde no hay dato."""
    try:
        with open(pfile, "r", encoding="utf-8", errors="ignore") as fh:
            lines = fh.read().splitlines()
    except OSError as _ign:
        ignore("_read_progress_extra", _ign)
        return None, None
    fps, size = None, None
    for ln in reversed(lines):
        if fps is None and ln.startswith("fps="):
            try:
                fps = float(ln.split("=", 1)[1]) or None
            except ValueError:
                pass
        elif size is None and ln.startswith("total_size="):
            try:
                size = int(ln.split("=", 1)[1]) or None
            except ValueError:
                pass
        if fps is not None and size is not None:
            break
    return fps, size


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
            # (1.6.4: con convert_fast_anim se lee el avance cada FFMPEG_TICK_FAST en vez de FFMPEG_TICK)
            drain_err()
            if DEBUG and time.time() - last_raw[0] >= 2.0:
                last_raw[0] = time.time()
                raw = _read_progress_raw(pfile)
                if raw:
                    dbg("ffmpeg progress", raw)
            secs, speed = _read_progress(pfile)
            if secs is not None:
                parts = []
                fps_now, out_bytes = _read_progress_extra(pfile)      # 1.6.9: datos reales de la salida
                if duration:
                    if speed:
                        parts.append(f"{speed:.1f}x")
                        eta = int(max(0.0, duration - secs) / speed)
                        parts.append(f"ETA {eta // 60:02d}:{eta % 60:02d}")
                    if fps_now:
                        parts.append(f"{fps_now:.0f} fps")
                    if out_bytes:
                        parts.append(human_size(out_bytes))
                    _pc = min(99.9, secs / duration * 100)
                    bar.set(pct=_pc, tail="  ".join(parts), val=speed)
                    ux_conv_progress(_pc)                       # 1.2.1: el mismo % en la escena de conversión
                else:
                    if speed:
                        parts.append(f"{speed:.1f}x")
                    parts.append(f"t={int(secs) // 60:02d}:{int(secs) % 60:02d}")
                    bar.set(tail="  ".join(parts), indeterminate=True, val=speed)
                    ux_conv_progress(None)
            bar.kick()
            try:
                # 1.6.4: duerme hasta el próximo avance o hasta que ffmpeg termine (lo que pase primero)
                proc.wait(timeout=ux_ffmpeg_tick())
            except subprocess.TimeoutExpired:
                pass
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
    ux_conv_progress(100.0)


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


def convert_quality_parse(raw):
    """1.6.9: «fast» (rápida, como 1.6.8; predeterminado), «high» (alta: x265 medium crf 20), «best» (sin pérdida) o «prores» (ProRes 422 HQ en .mov). Lo desconocido → fast."""
    v = str(raw or "").strip().lower()
    if v in ("best", "mejor", "lossless", "sin perdida", "sin pérdida"):
        return "best"
    if v in ("high", "alta", "alto", "media", "medium", "balanced"):
        return "high"
    if v in ("prores", "pro res", "pro-res"):
        return "prores"
    return "fast"


# 1.6.9: fast (predeterminado) · high · best (sin pérdida) · prores
CONVERT_QUALITY = convert_quality_parse(env_get("DLPY_CONVERT_PRESET"))
# 1.6.9: ×tiempo real a 1080p30 (x265/Kvazaar en software; ProRes por hardware); estimación inicial: luego manda la velocidad medida
CONVERT_BASE_SPEEDS = {"best": 0.3, "high": 0.5, "prores": 2.0}
VT_BEST_BOOST, VT_BEST_CAP = 1.5, 40000   # 1.6.9: best con VideoToolbox: bitrate ×1,5 del origen, tope en kb/s


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
        parts.append(f"video {plan['vsrc']} → " + (str(plan["target_enc"]) if str(plan.get("target_enc") or "").startswith(str(plan.get("target") or "\0")) else (plan.get("target") or "HEVC")) + (f" ({plan['target_enc']})" if plan.get("target_enc") and not str(plan["target_enc"]).startswith(str(plan.get("target") or "")) else ""))
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
# Velocidad de referencia: ~2.5× tiempo real a 1080p30 con hevc_videotoolbox (fast; con best, CONVERT_BASE_SPEED_BEST).
CONVERT_BASE_SPEED = 2.5


def conv_base_speed(quality=None):
    """1.6.9: velocidad de referencia según la calidad (best y high son software, mucho más lentas que VideoToolbox)."""
    return CONVERT_BASE_SPEEDS.get(quality or CONVERT_QUALITY, CONVERT_BASE_SPEED)


def conv_scale(plan):
    """Coste relativo a 1080p30 (mínimo 0.15): crece con el cuadrado de la altura y con los fps."""
    h = float(plan.get("height") or 0) or 720.0
    fps = float(plan.get("fps") or 0) or 30.0
    tm = (plan.get("hdr_mode") == "tonemap") if "hdr_mode" in plan else bool(plan.get("hdr")) and encode_bits(plan.get("out_bits")) <= 8
    # 1.2.1: el tone mapping (HDR → SDR) cuesta ~3×
    return max(0.15, (h / 1080.0) ** 2 * (fps / 30.0) * (3.0 if tm else 1.0))


def measured_conv_speed(index=None):
    """Velocidad de conversión REAL de este equipo:"""
    with quiet("measured_conv_speed"):
        idx = load_json(INDEX_FILE) if index is None else index
        rows = []
        for e in idx.values():
            cv = ((e or {}).get("meta") or {}).get("conv") or {}
            # 1.6.9: solo las hechas con esta calidad (las de antes de 1.6.9 eran fast)
            if cv.get("speed") and (cv.get("quality") or "fast") == CONVERT_QUALITY:
                rows.append((e.get("date") or 0, float(cv["speed"])))
        rows.sort()
        vals = sorted(v for _, v in rows[-5:])
        if vals:
            return min(40.0, max(0.1, vals[len(vals) // 2]))
    return conv_base_speed()


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
_ENCODERS = {}
ENGINE_PREFIX = (("ProRes 422 HQ VideoToolbox", "prores_videotoolbox"), ("ProRes 422 HQ software", "prores_ks"), ("x265", "libx265"), ("Kvazaar", "libkvazaar"),
                 # 1.6.9: nombre del intento (por el principio) → encoder de ffmpeg
                 ("VideoToolbox", "hevc_videotoolbox"), ("x264", "libx264"))


def encoder_for(name):
    """1.6.9: el encoder de ffmpeg de un intento («x265 sin pérdida» → libx265); None si no se conoce."""
    return next((enc for pre, enc in ENGINE_PREFIX if str(name).startswith(pre)), None)


def filter_attempts(sets, exe=None):
    """1.6.9: deja los intentos cuyo encoder trae este ffmpeg (si no se puede leer, o no queda ninguno, todos)."""
    if not exe:
        return sets
    have = ffmpeg_encoders(exe)
    return [a for a in sets if not have or encoder_for(a[1]) in have] or sets


def ffmpeg_encoders(exe):
    """1.6.9: los encoders que trae este ffmpeg (ffmpeg -encoders, una sola lectura por ffmpeg). Vacío si no se pudo leer."""
    import subprocess
    exe = exe or shutil.which("ffmpeg")
    if not exe:
        return set()
    if exe not in _ENCODERS:
        have = set()
        with quiet("ffmpeg_encoders"):
            r = subprocess.run([exe, "-hide_banner", "-encoders"], capture_output=True, text=True, timeout=15,
                               stdin=subprocess.DEVNULL)
            for ln in (r.stdout or "").splitlines():
                parts = ln.split()
                if len(parts) >= 2 and parts[0][:1] in "VAS" and "." in parts[0]:
                    have.add(parts[1])
        _ENCODERS[exe] = have
    return _ENCODERS[exe]


def hdr_kind(plan, probed=None):
    """1.2.1:"""
    trc = str((probed or {}).get("color_transfer") or "").lower()
    if trc == "smpte2084":
        return "pq"
    if trc == "arib-std-b67":
        return "hlg"
    if trc and trc not in ("unknown", "unspecified"):
        # el archivo dice SDR (bt709, …) aunque el análisis dijera otra cosa
        return None
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


def video_encoder_attempts(plan, quality=None, exe=None):
    """[(códec_corto, nombre_legible, opciones)] a probar en orden; la primera que funcione se queda.
    1.6.9: `quality` (fast, high, best o prores; por omisión DLPY_CONVERT_PRESET). best: x265 SIN PÉRDIDA primero (lossless; los de respaldo no lo son: VideoToolbox ×1,5 y x264 crf 18);
    high: x265 medium crf 20 primero; fast: como en 1.6.8. Con `exe` solo quedan los encoders que ese ffmpeg trae (si no se puede leer, todos)."""
    quality = quality or CONVERT_QUALITY
    if quality == "prores" and plan["venc"]:
        return prores_attempts(plan, exe)
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

    # best = sin pérdida; best y high = alta calidad (x265 primero)
    lossless, best = quality == "best", quality in ("best", "high")
    vb = f"{int(min(VT_BEST_CAP, plan['vbr'] * VT_BEST_BOOST))}k" if best else b
    ls = " sin pérdida" if lossless else ""

    def vt_opts(bits):
        o = vf + ["-c:v", "hevc_videotoolbox", "-b:v", vb, "-allow_sw", "1",
                  "-tag:v", "hvc1", "-pix_fmt", out_pix(bits)] + tags
        return o + (["-profile:v", "main10"] if bits == 10 else [])

    def x265_opts(bits):
        q = ["-preset", "veryfast"] if lossless else ["-preset", "medium" if best else "veryfast", "-crf", "20" if best else "26"]
        o = vf + ["-c:v", "libx265"] + q + ["-tag:v", "hvc1", "-pix_fmt", out_pix(bits)] + tags
        ps = (["lossless=1"] if lossless else []) + ([f"profile=main{bits}"] if bits > 8 else []) + xp
        return o + (["-x265-params", ":".join(ps)] if ps else [])

    # 1.6.9: Kvazaar (HEVC por software; el ffmpeg de a-Shell lo trae sin x265): solo 8 bits; lossless=1 es sin pérdida
    def kvz_opts():
        q = "lossless=1,preset=ultrafast" if lossless else "qp=18,preset=medium"
        return vf + ["-c:v", "libkvazaar", "-kvazaar-params", q, "-tag:v", "hvc1", "-pix_fmt", "yuv420p"] + tags

    x264 = vf + ["-c:v", "libx264", "-preset", "medium" if best else "veryfast", "-crf", "18" if best else "21",
                 "-pix_fmt", "yuv420p"] + tags          # H.264 High 10 casi no se usa en Apple
    if ob == 12:
        sets = [("hevc", "x265 12 bits" + ls, x265_opts(12)),
                ("hevc", "VideoToolbox HEVC 10 bits", vt_opts(10)),
                ("hevc", "x265 10 bits" + ls, x265_opts(10))]
        sets += ([("h264", "x264", x264)] if mode is None else [])
    else:
        sets = [("hevc", "VideoToolbox HEVC" + sfx, vt_opts(ob)),
                ("hevc", "x265" + ls + sfx, x265_opts(ob))]
        # 1.6.9: x265 y Kvazaar (los de software: los únicos sin pérdida) antes que el codificador por hardware
        if best:
            sets = [sets[1]] + ([("hevc", "Kvazaar" + ls + sfx, kvz_opts())] if ob == 8 else []) + [sets[0]]
        sets += ([("h264", "x264" + sfx, x264)] if mode != "keep" else [])
    # 1.6.9: solo los encoders que este ffmpeg trae (no se prueba lo que falta)
    return filter_attempts(sets, exe)


def prores_attempts(plan, exe=None):
    """1.6.9: ProRes 422 HQ (.mov): primero el de VideoToolbox, luego el de software; si este ffmpeg no trae ninguno, la cadena de «high». Mismo trato del HDR que los demás."""
    mode, kind = plan.get("hdr_mode"), plan.get("hdr_kind")
    vf, tags = [], []
    if mode == "keep" and kind in HDR_TAGS:
        pr, tr, mx = HDR_TAGS[kind]
        tags = ["-color_primaries", pr, "-color_trc", tr, "-colorspace", mx]
    elif mode == "tonemap" and kind:
        vf, tags = ["-vf", tonemap_filter(kind)], list(SDR_TAGS)
    else:
        mode = None
    sfx = " HDR" if mode == "keep" else " SDR" if mode == "tonemap" else ""
    sets = [("prores", "ProRes 422 HQ VideoToolbox" + sfx, vf + ["-c:v", "prores_videotoolbox", "-profile:v", "hq"] + tags),
            ("prores", "ProRes 422 HQ software" + sfx, vf + ["-c:v", "prores_ks", "-profile:v", "3", "-vendor", "apl0", "-pix_fmt", "yuv422p10le"] + tags)]
    return filter_attempts(sets + video_encoder_attempts(plan, "high"), exe)


def plan_ext(plan):
    """1.6.9: extensión de salida: con prores y video que se recodifica es .mov (ProRes no va en mp4); si no, la del plan."""
    if plan.get("venc") and plan.get("vsrc") is not None and CONVERT_QUALITY == "prores":
        return "mov"
    return plan.get("ext")


def plan_target(plan, exe=None, quality=None):
    """1.6.9: el códec y el codificador REALES con los que se va a recodificar (el primero que este ffmpeg trae): plan["target"] («HEVC» / «H.264»)
    y plan["target_enc"] («x265 sin pérdida», «VideoToolbox HEVC»…). Sin recodificar de video no hay destino y se borran. Devuelve el nombre o None."""
    plan.pop("target", None)
    plan.pop("target_enc", None)
    if not plan.get("venc") or plan.get("vsrc") is None:
        return None
    with quiet("plan_target"):
        vc, name, _o = video_encoder_attempts(plan, quality, exe=exe)[0]
        plan["target"], plan["target_enc"] = codec_name(vc) or "HEVC", name
        return name
    return None


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
    # 1.2.1: «yuv420p10le(tv, bt2020nc/bt2020/smpte2084, …)»
    tm = re.search(r"smpte2084|arib-std-b67", body)
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
                # 1.2.1: el color real (HDR)
                for _ck in ("color_space", "color_transfer", "color_primaries", "color_range"):
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


def probe_skip_note(donde, fmt):
    """1.7.8: la línea de debug cuando no se sondea un stream (sin URL http(s), sin datos útiles que yt-dlp ya informó o URL opaca sin códec real). Sin DLPY_DEBUG_LOGGING no hace nada."""
    fmt = fmt or {}
    dbg(f"{donde}: omitido (sin URL http(s), sin datos útiles o URL opaca sin códec real)",
        {"format_id": fmt.get("format_id"), "url_http": str(fmt.get("url") or "").lower().startswith(("http://", "https://")),
         "height": fmt.get("height"), "vcodec": fmt.get("vcodec"), "tbr": fmt.get("tbr")})


def probe_stream_bits(exe, fmt, timeout=12):
    """Bits del stream de video de `fmt` leyendo su cabecera con ffmpeg (sin descargarlo). 1.7.7: solo si stream_can_probe(fmt)."""
    import subprocess
    if not exe:
        return None
    if not stream_can_probe(fmt):
        probe_skip_note("sondeo de bits", fmt)                    # 1.7.8
        return None
    url = str((fmt or {}).get("url") or "")
    cmd = [exe, "-hide_banner", "-nostdin", "-probesize", "3000000", "-analyzeduration", "3000000"]
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
    """1.3.6 (1.7.7: solo si stream_can_probe(fmt))."""
    import subprocess
    if not exe:
        return None
    if not stream_can_probe(fmt):
        probe_skip_note("sondeo de datos reales", fmt)            # 1.7.8
        return None
    url = str((fmt or {}).get("url") or "")
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


# 2.0.4: extensiones de URL que ffmpeg sabe abrir como archivo o manifiesto
PROBE_URL_EXTS = (".mp4", ".m4v", ".m4a", ".mov", ".webm", ".mkv", ".mp3", ".aac", ".flac", ".ogg", ".opus", ".wav",
                  ".ts", ".flv", ".3gp", ".m3u8", ".mpd")


def stream_can_probe(fmt):
    """1.7.7: ¿se puede sondear este stream con ffmpeg? Solo con URL http(s) y algún dato útil que yt-dlp ya informó (alto, ancho, fps, códec real o bitrate).
    2.0.4: además, sin códec real la URL debe ser de un archivo o manifiesto conocido (PROBE_URL_EXTS): un formato como «full», «hd» o «sd» de ok.ru trae alto o
    bitrate pero su URL es opaca, y sondearla en un hilo mientras se descarga cerró a-Shell mini tras un rato. Lo que se lee se obtiene luego del archivo ya descargado. Pura."""
    fmt = fmt or {}
    url = str(fmt.get("url") or "")
    if not url.lower().startswith(("http://", "https://")):
        return False

    def num(k):
        try:
            return float(fmt.get(k) or 0) > 0
        except (TypeError, ValueError):
            return False
    real = lambda c: bool(c) and str(c).strip().lower() not in ("none", "unknown", "?")
    if real(fmt.get("vcodec")) or real(fmt.get("acodec")):
        return True
    if not any(num(k) for k in ("height", "width", "fps", "vbr", "abr", "tbr")):
        return False
    try:
        path = urllib.parse.urlparse(url).path.lower()
    except ValueError:
        return False
    return path.endswith(PROBE_URL_EXTS)


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
# nombres de ffprobe que Apple reproduce en mp4/m4v/mov
REAL_VCODECS = ("h264", "hevc")
# audio que cabe en mp4/m4v/mov y Apple reproduce
REAL_ACODECS = ("aac", "alac", "mp3", "ac3", "eac3")
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
    # el usuario pidió remux: el video no se recodifica pase lo que pase
    forced = bool(plan.get("remux_forced"))
    vc = ((real.get("v") or {}).get("codec") or "") if video else ""
    tag = (real.get("v") or {}).get("tag") if video else None
    venc = video and not forced and vc not in REAL_VCODECS
    # HEVC con etiqueta que Apple no abre: basta un remux con hvc1
    retag = video and vc == "hevc" and tag == "hev1"
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
        # sin recodificar video no hay conversión larga que preguntar
        new.pop("ask_enter", None)
    return new, changes, items


def plan_check_items(plan):
    """1.6.0: los tres cuadros de la revisión con lo que dice el plan (lo que informó el sitio), para cuando el archivo no se pudo leer:
    [(texto, ¿hay que convertirlo?)] = video (si hay) · audio · contenedor."""
    items = []
    if plan.get("vsrc") is not None:
        items.append((codec_name(plan.get("vsrc")) or str(plan.get("vsrc") or "?"), bool(plan.get("venc"))))
    asrc = list(plan.get("asrc") or [])
    items.append(((codec_name(asrc[0]) or str(asrc[0])) if asrc else "\u2014", any(plan.get("aenc") or [])))
    items.append((str(plan.get("cur") or "?"), bool(plan.get("remux"))))
    return items


def check_download(pp, path, plan):
    """1.2.5: lee el archivo real y decide si hace falta convertir. La escena hace el escaneo (haz sobre los tres «?») MIENTRAS se lee el archivo
    y, al terminar, los cuadros se resuelven a lo DETECTADO (video · audio · contenedor) ya con el veredicto (verde: ya es compatible · ámbar: hay
    que convertir). 1.6.1: sin lectura, los cuadros se resuelven con lo del plan en vez de quedarse en «?»."""
    ux_check()
    try:
        real = probe_file(getattr(pp, "executable", None), path)
    except Exception as _ign:
        ignore("check_download", _ign)
        real = None
    new, changes, items = refine_plan(plan, real)
    dbg("revisión del archivo", {"real": real, "cambios": changes})
    # 1.5.5: el haz termina su recorrido (el escaneo duró lo que tardó la lectura, mínimo un barrido)
    ux_wait_anim("check", 1.1)
    # 1.6.0: no se pudo leer: los cuadros muestran lo del plan y se sigue con él
    if items is None:
        items = plan_check_items(plan)
        m_info("No se pudo leer el archivo: se sigue el plan de conversión de antes.")
        ux_check(items, "conv")
        ux_wait_anim("check", 0.9)
        ux_check_end()
        return True
    if new is None:
        ux_check(items, "ok")
        m_ok("El archivo descargado ya es compatible con Apple: se guarda sin convertir.")
        # 1.5.5: el pulso verde termina su ciclo y sigue el proceso
        ux_wait_anim("check", 1.0)
        ux_check_end()
        return False
    ux_check(items, "conv")
    plan.clear()
    plan.update(new)
    if changes:
        m_info("Revisado el archivo real: " + plan_summary(plan))
    ux_wait_anim("check", 0.9)                                    # 1.5.5: idem con el pulso ámbar
    ux_check_end()
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
    parts = ([codec_name(used) or used.upper()] if used else []) + ([f"{bits} bits"] if bits else [])
    if plan.get("venc") and plan.get("lossless"):
        parts.append("sin pérdida")
    parts += ["HDR conservado"] if plan.get("hdr_mode") == "keep" else ["HDR → SDR"] if plan.get("hdr_mode") == "tonemap" else []
    if plan.get("remux_forced"):
        m_ok(f"Remux a {plan['ext'].upper()}: video sin recodificar (puede no verse en Apple)")
        return
    m_ok(f"Convertido a {str(plan_ext(plan)).upper()} compatible con Apple"
         + (f" ({' · '.join(parts)})" if parts else ""))
    if plan.get("venc"):
        w = bits_warning(plan.get("out_bits"), bits, used)
        if w:
            m_warn(w)
        if CONVERT_QUALITY == "best" and not plan.get("lossless") and plan.get("hdr_mode") != "tonemap":
            m_warn("No hubo modo sin pérdida (este ffmpeg no trae x265 ni Kvazaar, o el video es de más de 8 bits): se usó " + (plan.get("engine") or "otro codificador") + " con la mayor calidad posible.")


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
        if CONVERT_QUALITY == "prores":
            # 1.6.9: ProRes 422 es de 10 bits (el HDR se conserva con sus etiquetas)
            plan["out_bits"] = 10
        hdr_prepare(plan, real, exe)
    err, used, ok = None, None, False
    t_start = time.time()
    plan.pop("engine", None)
    plan.pop("lossless", None)
    # 1.6.4: sin escena el aviso va como una línea (con escena lo pone la propia escena)
    if not ux_on():
        m_info("Espera mientras convierte · puede tardar · no cierres la app.")

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
                ux_convert(scene_codec, ("Convirtiendo · " + name) if vcodec is not None else bar_label, scene_from, scene_to)      # 1.6.9: el nombre real (x265 sin pérdida, x264…), no solo el motor
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
                        plan["lossless"] = "sin pérdida" in name  # 1.6.9: lo que de verdad se usó
                    break
                err = "archivo vacío"
            except Exception as e:
                err = e
                dbg("intento fallido", {"video": vcodec, "name": name, "error": str(e)[-300:]})
            prev_name = name
            if os.path.exists(tmp):
                os.remove(tmp)

    if plan.get("vsrc") is not None:
        vsets = video_encoder_attempts(plan, exe=exe)
    else:
        vsets = [(None, "AAC (audio)", [])]
    run_sets(vsets)
    # 1.2.1: sin tone mapping que valga, el HDR se conserva
    if not ok and plan.get("hdr_mode") == "tonemap":
        m_warn("El tone mapping no funcionó: se conserva el HDR en 10 bits.")
        plan["hdr_mode"], plan["out_bits"] = "keep", 10
        run_sets(video_encoder_attempts(plan, exe=exe))
    ux_convert_end()
    if not ok:
        raise RuntimeError(str(err))
    plan["result"] = (probe_video(exe, tmp) if plan.get("vsrc") is not None else None)
    dbg("video convertido", plan["result"])
    plan["secs"] = int(round(time.time() - t_start))
    # velocidad real para estimar las próximas (solo con recodificación)
    with quiet("apple_convert_file", TypeError, ValueError):
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
    if plan.get("venc"):
        # 1.6.9: la velocidad medida solo sirve para estimar conversiones con la misma calidad
        d["quality"] = CONVERT_QUALITY
        if plan.get("lossless"):
            d["lossless"] = True                # 1.6.9: el video salió sin pérdida (x265 lossless)
    return d


def convert_confirmed(plan):
    """1.1.2:"""
    est = plan.pop("ask_enter", None)
    if est is None or not plan.get("venc"):
        return True
    try:
        # 1.6.9: el códec real del primer encoder disponible
        ok = ux_ask_enter(est, src=codec_name(plan.get("vsrc")) or plan.get("cur"), dst=plan.get("target") or "HEVC")
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
        return ux_ask_enter(src="VIEJO", dst="NUEVO", kind="replace")
    except EOFError:
        return False


def make_apple_pp(plan, state, bar=None):
    from yt_dlp.postprocessor import FFmpegPostProcessor

    class AppleConvertPP(FFmpegPostProcessor):
        def run(self, info):
            path = info.get("filepath")
            if not path or not os.path.exists(path):
                return [], info
            # 1.2.5: se lee el archivo real; si ya es compatible no se convierte
            if not check_download(self, path, plan):
                return [], info
            if not convert_confirmed(plan):                 # 1.1.2: la escena pide Enter justo antes de convertir
                return [], info
            # 1.6.9: con ProRes (y video que se recodifica) la salida es .mov
            ext = plan_ext(plan)
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
        # 1.4.2: con la escena viva se contesta en ella (Enter sustituye · n conserva)
        if ux_on():
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
                       + "." + plan_ext(plan))
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
    except DISK_ERRORS as e:
        m_warn(f"No se pudo guardar el índice: {e}")
    history_add(key, index[key])
    deliver(final, title)
    return True


def ask_keep_bits(plan, est, slow):
    """Pregunta si conservar los bits originales (origen de más de 8 bits)"""
    bits, hdr = plan["bits"], plan.get("hdr")
    if CONVERT_QUALITY == "prores":                 # 1.6.9: ProRes 422 siempre es de 10 bits: no hay nada que preguntar
        plan["out_bits"], plan["asked_bits"] = 10, False
        m_info("ProRes 422 HQ: 10 bits.")
        return plan
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
        print_rows([{"n": n, "flags": {"default"} if n == default_n else set(), "cols": [txt]}      # ▸ = la que vale con Enter o al acabar la cuenta
                    for n, (_, txt) in enumerate(choices, 1)], [])
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
    header(t_display("COMPATIBILIDAD APPLE"), gap=False)
    m_warn("Este resultado no es compatible con Apple.")
    if not can_merge:
        kv("Conversión", plan_summary(plan))
        m_info("No hay ffmpeg para convertir; se descargará tal cual.")
        return None
    if plan.get("venc") and not plan.get("bits") and fmt:
        # 1.7.7: URL http(s) y algún dato útil; una URL opaca (sin alto, códec real ni bitrate) no se sondea
        if stream_can_probe(fmt):
            note("Leyendo los bits del video de origen…")
            got = probe_stream_bits(_FfmpegShim().executable, fmt)
            if got:
                plan["bits"] = got
                plan["out_bits"] = min(encode_bits(got), 10)
        else:
            probe_skip_note("sondeo de bits", fmt)                # 1.7.8: la misma nota que en probe_stream_bits
    # 1.6.9: códec y codificador reales (según los encoders de este ffmpeg)
    plan_target(plan, _FfmpegShim().executable)
    kv("Conversión", plan_summary(plan))
    if "sin pérdida" in str(plan.get("target_enc") or ""):
        note("Sin pérdida: el video se recodifica sin quitar nada de lo decodificado; el archivo pesa mucho más que el original.")
    elif str(plan.get("target_enc") or "").startswith("ProRes"):
        note("ProRes 422 HQ: casi igual al original (no es matemáticamente sin pérdida); el archivo sale en .mov y pesa muchísimo más.")
    elif CONVERT_QUALITY == "best" and plan.get("venc") and plan.get("target_enc"):
        note("No hay modo sin pérdida aquí (este ffmpeg no trae x265 ni Kvazaar, o el video es de más de 8 bits): se usa la mayor calidad posible.")
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
            note(f"Recodificar el video a {plan.get('target') or 'HEVC'} puede tardar bastante en el {device_label()}.")
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
            # 1.1.1: conversión que se sabe que tarda
            ask_scene = bool(ux_on() and plan.get("venc") and est is not None and countdown_supported())
            # 1.1.2: el Enter se pide justo antes de convertir (convert_confirmed)
            if ask_scene:
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
    when_s = loc_date(when) if when else "?"
    header(t_display("YA DESCARGADO"), gap=False)
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
    if dl and loc_date(dl) != when_s:
        fecha += " · " + t_display("entregado") + " " + loc_date(dl)
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
        print("  " + paint("◆", "amber") + " " + paint(t_display("original"), "gray") + "   "
              + paint("▸", "orange") + " " + paint(t_display("predeterminada"), "gray"))
    if apple:
        print("  " + paint("✓", "mint") + " " + paint(t_display("compatible Apple"), "gray"))


# ───────────────────── [E2] Enlace y portapapeles ─────────────────────
def clipboard_cmd():
    """Orden que imprime el portapapeles, o None."""
    on = env_get("DLPY_CLIPBOARD_READ_LINK_ENABLED", "").strip().lower() not in ("", "0", "no", "false")
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
        return sh_run("pbcopy < " + shlex.quote(tmp)) == 0
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


# 1.4.4: lo último que hizo cada operación de las fases de actualización: clave → {ok, secs, code, val, err}. La escena D L P Y lo enseña.
NET = {}
# 1.4.4: respuesta de la última página de /releases (código HTTP o causa del fallo)
GH_LAST = {"code": None, "err": None}


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


# 1.8.8: s que sigue encendido tras la última actividad (evita el parpadeo con peticiones cortas)
NET_HOLD = 1.2
NET_FADE = 0.3                         # 1.8.9: s del fundido con que se apaga el icono (los últimos s de NET_HOLD)
# 1.8.8: peticiones en curso y última actividad (alimenta el icono ⇅ de la franja)
NETSTATE = {"busy": 0, "last": 0.0}
_NET_LOCK = threading.Lock()              # las comprobaciones de arranque corren en hilos paralelos


def net_touch(now=None):
    """1.8.8: hubo actividad de red ahora (p. ej. avance de una descarga)."""
    with _NET_LOCK:
        NETSTATE["last"] = time.time() if now is None else now


def net_begin():
    with _NET_LOCK:
        NETSTATE["busy"] += 1
        NETSTATE["last"] = time.time()


def net_end():
    with _NET_LOCK:
        NETSTATE["busy"] = max(0, NETSTATE["busy"] - 1)
        NETSTATE["last"] = time.time()


def net_active(now=None):
    """1.8.8: ¿el script está conectando a internet? Sí mientras haya una petición en curso o durante NET_HOLD s tras la última actividad."""
    now = time.time() if now is None else now
    with _NET_LOCK:
        return NETSTATE["busy"] > 0 or (NETSTATE["last"] > 0.0 and 0.0 <= now - NETSTATE["last"] < NET_HOLD)


def net_level(now=None):
    """1.8.9: intensidad (0 a 1) del icono ⇅: 1 con una petición en curso o poco después de la última actividad; baja linealmente a 0 en los últimos
    NET_FADE s de NET_HOLD (el fundido de apagado). Enciende de golpe, apaga suave. Es > 0 exactamente cuando net_active es verdadero."""
    now = time.time() if now is None else now
    with _NET_LOCK:
        if NETSTATE["busy"] > 0:
            return 1.0
        last = NETSTATE["last"]
    dt = now - last
    if last <= 0.0 or not (0.0 <= dt < NET_HOLD):
        return 0.0
    return max(0.0, min(1.0, (NET_HOLD - dt) / NET_FADE))


class net_busy:
    """1.8.8: `with net_busy():` marca una operación de red en curso (también si falla)."""

    def __enter__(self):
        net_begin()
        return self

    def __exit__(self, *exc):
        net_end()
        return False


def net_wrap_ytdlp(yt_dlp):
    """1.8.8: yt-dlp avisa de su red: cada urlopen y todo el análisis (extract_info sin descargar). Se aplica una sola vez por proceso;
    la descarga marca actividad con el avance del progreso (DownloadUI.hook), así el ffmpeg de después no cuenta como red."""
    with quiet("net_wrap_ytdlp"):
        cls = yt_dlp.YoutubeDL
        if getattr(cls, "_dlpy_net", False):
            return
        _uo, _ei = cls.urlopen, cls.extract_info

        def urlopen(self, *a, **k):
            with net_busy():
                return _uo(self, *a, **k)

        def extract_info(self, *a, **k):
            if k.get("download", a[1] if len(a) > 1 else True):
                return _ei(self, *a, **k)
            with net_busy():
                return _ei(self, *a, **k)
        cls.urlopen, cls.extract_info, cls._dlpy_net = urlopen, extract_info, True


def net_set(key, t0, ok, code=None, val=None, err=None):
    NET[key] = {"ok": bool(ok), "secs": max(0.0, time.time() - t0), "code": code, "val": val, "err": err}


def latest_version(pip_name, timeout=6):
    import urllib.request
    t0 = time.time()
    try:
        with net_busy(), urllib.request.urlopen(f"https://pypi.org/pypi/{pip_name}/json", timeout=timeout) as r:
            code = getattr(r, "status", None) or r.getcode()
            ver = json.load(r)["info"]["version"]
        net_set(pip_name, t0, True, code, ver)
        return ver
    except NET_ERRORS + PARSE_ERRORS as _ign:
        ignore("latest_version", _ign)
        net_set(pip_name, t0, False, err=net_err_text(_ign))
        return None


def vtuple(v):
    """Tupla numérica de una versión, rellenada a tres números («1.0» = «1.0.0»); () si no hay números."""
    t = tuple(int(x) for x in re.findall(r"\d+", v or ""))
    return t + (0,) * (3 - len(t)) if t else t


DOWNGRADE_CAUSES = ("manual", "externa")
DOWNGRADE_DELIBERATE = ("manual",)     # bajadas hechas a propósito desde DLpy (--versions)


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
UPDATE_REPO = (env_get("DLPY_UPDATE_REPO") or "ElDelDLpy/DLpy").strip().strip("/")
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
        # 2.0.6: cabecera y detalle por el motor (evita «Подключение · descargando…»)
        m_info(t("Conectando a GitHub") + " · " + t_display(str(what)))


def fresh_bytes(url, timeout=5, limit=None):
    """Bytes de `url` sin pasar por cachés."""
    import urllib.request
    import urllib.parse
    limit = limit or UPDATE_MAX_BYTES
    if is_github_url(url):
        gh_notice(t("descargando") + " " + (os.path.basename(urllib.parse.urlparse(url).path) or t("el archivo")))
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
        with quiet("fresh_bytes"), net_busy():
            with urllib.request.urlopen(urllib.request.Request(u, headers=headers),
                                        timeout=timeout) as r:
                raw = r.read(limit + 1)
            if len(raw) <= limit:
                return raw
    return None


# url del script → {"sha_url", "digest", "body"}: lo que publica su Release (lo llena parse_releases)
RELEASE_HASH = {}
# url del script → "ok" | "none" | "bad" | "off": resultado de la última verificación
VERIFY = {}
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
    if (env_get("DLPY_SKIP_SHA_VERIFY") or "").strip().lower() not in ("", "0", "no", "false"):
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
    """Texto del dlpy.py de `url` (el de un Release), o None si falla, no es un script válido o su SHA-256 no coincide o no está publicado."""
    if not url:
        return None
    try:
        raw = fresh_bytes(url, timeout)
        if raw is None:
            return None
        vr = verify_download(url, raw, timeout)
        if vr == "bad":
            return None
        # 1.8.7: sin hash publicado no se instala (cada Release publica el suyo); DLPY_SKIP_SHA_VERIFY=1 lo omite
        if vr == "none":
            m_err("Sin SHA-256 publicado: no se instala. DLPY_SKIP_SHA_VERIFY=1 omite la verificación.")
            return None
        text = raw.decode("utf-8").replace("\r\n", "\n")
        if not remote_script_version(text):
            return None
        compile(text, "dlpy.py", "exec")          # descarga truncada o dañada
        return text
    except NET_ERRORS + (SyntaxError,) as _ign:
        ignore("fetch_remote_script", _ign)
        return None


# --noupdates / --no-updates / DLPY_UPDATE_CHECK_INTERVAL=0: esta ejecución no busca nada (ni el script ni sus dependencias)
NO_UPDATES = {"on": False}
# --shortcutpick SIN escena viva: se busca al terminar la descarga (1.8.0: con escena viva se busca primero; _m_update lo apaga)
LATE_UPDATES = {"on": False, "done": False}
# Releases leídos en esta ejecución (los guarda remote_releases): de ahí sale changelog.md
RELEASES = {"list": None}
UPDATE_CHECKED = {"ok": False}        # ¿llegó a comprobarse la última versión (hubo red)?

# Búsqueda de actualizaciones (1.4.4: UNA sola variable, DLPY_UPDATE_CHECK_INTERVAL, para el script y para sus dependencias): fecha de la última
# comprobación por clave («script» = DLpy en GitHub, «deps» = pip / yt-dlp / yt-dlp-ejs) en state/checks.json.
UPDATES_ALWAYS = -1.0                 # valor interno de «on» (en cada arranque)
UPDATES_DEFAULT = 168.0               # 1.9.6: predeterminado: una vez por semana (168 h); el intervalo se guarda en HORAS
UPDATES_MIN_HOURS = 1.0 / 60.0        # 1.9.6: mínimo 1 minuto (evita peticiones continuas)
_UPDATES_UNITS = {
    "m": 1.0 / 60.0, "min": 1.0 / 60.0, "mins": 1.0 / 60.0, "minuto": 1.0 / 60.0, "minutos": 1.0 / 60.0, "minute": 1.0 / 60.0, "minutes": 1.0 / 60.0,
    "h": 1.0, "hr": 1.0, "hrs": 1.0, "hora": 1.0, "horas": 1.0, "hour": 1.0, "hours": 1.0,
    "d": 24.0, "dia": 24.0, "dias": 24.0, "día": 24.0, "días": 24.0, "day": 24.0, "days": 24.0,
    "w": 168.0, "sem": 168.0, "semana": 168.0, "semanas": 168.0, "week": 168.0, "weeks": 168.0,
}
_UPDATES_WORDS = {"hourly": 1.0, "cadahora": 1.0, "daily": 24.0, "diario": 24.0, "diaria": 24.0, "weekly": 168.0, "semanal": 168.0}


def updates_parse_hours(raw):
    """1.9.6: DLPY_UPDATE_CHECK_INTERVAL → horas, o None si no se entiende. «on»/«siempre»/«always» = -1 (en cada arranque) · «0»/«off»/«nunca» = 0 (nunca) ·
    número + unidad (30m, 6h, 2d, 1w; también min/hora/día/semana y sus formas en inglés) · número solo = DÍAS (compatible con antes) ·
    daily / weekly / hourly. Todo lo positivo se sube al mínimo de 1 minuto."""
    t = str(raw if raw is not None else "").strip().lower().replace(",", ".")
    if t in ("on", "siempre", "always", "s", "a"):
        return UPDATES_ALWAYS
    if t in ("off", "nunca", "never", "no"):
        return 0.0
    t = t.replace(" ", "")
    if t in _UPDATES_WORDS:
        return _UPDATES_WORDS[t]
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([a-záéíóú]*)", t)
    if not m:
        return None
    v, unit = float(m.group(1)), m.group(2)
    if unit and unit not in _UPDATES_UNITS:
        return None
    hours = v * (_UPDATES_UNITS[unit] if unit else 24.0)
    if not math.isfinite(hours):
        return None
    return 0.0 if hours == 0 else max(hours, UPDATES_MIN_HOURS)


def parse_updates(raw):
    """1.9.6: DLPY_UPDATE_CHECK_INTERVAL en HORAS (-1 = en cada arranque · 0 = nunca); vacío, negativo o texto raro = el predeterminado (1 semana)."""
    v = updates_parse_hours(raw)
    return UPDATES_DEFAULT if v is None else v


def _updates_from_env():
    """DLPY_UPDATE_CHECK_INTERVAL (horas); sin ella, las dos variables de la 1.4.3 (DLPY_NO_UPDATE → nunca · DLPY_CHECK_HOURS → horas) para no cambiar a nadie el comportamiento."""
    raw = env_get("DLPY_UPDATE_CHECK_INTERVAL")
    if raw is not None and raw.strip():
        return parse_updates(raw)
    if (env_get("DLPY_NO_UPDATE") or "").strip():
        return 0.0
    hours = _env_num("DLPY_CHECK_HOURS", -1.0, minimum=float("-inf"))
    return max(hours, UPDATES_MIN_HOURS) if hours > 0 else UPDATES_DEFAULT


UPDATE_HOURS = _updates_from_env()


def update_every_text(hours=None):
    """Cada cuánto se busca, en palabras («en cada arranque», «cada 30 min», «cada hora», «cada 6 h», «cada día», «cada 3 días», «cada semana», «nunca»)."""
    h = UPDATE_HOURS if hours is None else hours
    if h < 0:
        return "en cada arranque"
    if h == 0:
        return "nunca"
    if h < 1.0:
        mins = max(1, int(round(h * 60)))
        return "cada minuto" if mins == 1 else f"cada {mins} min"
    if h < 24.0:
        return "cada hora" if h == 1 else f"cada {h:g} h"
    days = h / 24.0
    if days >= 7 and abs(days / 7 - round(days / 7)) < 1e-9:
        w = int(round(days / 7))
        return "cada semana" if w == 1 else f"cada {w} semanas"
    return "cada día" if days == 1 else f"cada {days:g} días"


def due_from(rec, sig=None, now=None, hours=None):
    """¿Toca comprobar?"""
    now = time.time() if now is None else now
    # 1.9.6: de DLPY_UPDATE_CHECK_INTERVAL (horas): nunca → no toca · siempre → toca
    if hours is None:
        if UPDATE_HOURS == 0:
            return False
        hours = 0 if UPDATE_HOURS < 0 else UPDATE_HOURS
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
        header(f"CHANGELOG {ver} · se instalará", gap=False)  # plantilla localizada por rule()/t_display()
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
                header(t_display("CHANGELOG · GITHUB"), gap=False)
                show_all_release_notes(rels, ver)
            else:
                header(f"Notas de versión {ver}", gap=False)
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
        m_warn("SHA-256 sin verificar (DLPY_SKIP_SHA_VERIFY=1)")


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
    if not ux_note("Comprobando actualizaciones"):         # dentro de la escena el texto de estado hace de barra
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
    if len(bad) == len(keys) and ux_note("No se pudo comprobar actualizaciones", SCENE_DWELL):
        # ya se dijo una vez: los pasos de cada una no repiten el ✗
        PREFETCH["quiet_fail"] = True
    return True


def prefetch_summary():
    """1.4.4: si todo salió bien y no hubo nada que actualizar, un solo resumen en la escena."""
    P = PREFETCH
    chk = NET.get("check") or {}
    if P["on"] and ux_on() and chk.get("ok") and not P["changed"]:
        ux_note(f"Todo al día · {P['n']} comprobaciones · {chk['secs']:.1f} s", SCENE_DWELL)
    P["on"] = False


def version_scene(kind, old, new, text, edited=False):
    """1.6.5: la animación del veredicto de la comprobación de DLpy dentro de la escena: «updated» (hay una más nueva) · «same» (es la última; `edited` si el código
    difiere del Release) · «ahead» (la instalada es MÁS NUEVA que el Release; `old` = el Release, `new` = la instalada; 1.7.1: antes usaba «downgrade»). Pone `text` de estado y espera lo que dure el dibujo; sin escena no hace nada."""
    try:
        return ux_welcome(kind, old, new, edited=edited, text=text)
    except KeyboardInterrupt:
        raise
    except Exception as _ign:
        ignore("version_scene", _ign)
        return False


def check_update(force=False, late=False):
    """Si el último Release de GitHub es más nuevo, muestra sus release notes y, con Enter, lo instala y lo ejecuta."""
    # 1.4.4: ya la pidió prefetch_phase, en paralelo
    pre = PREFETCH["on"] and "DLpy" in PREFETCH["keys"] and not force and not late
    if pre:
        PREFETCH["keys"].remove("DLpy")
        rel = PREFETCH["res"].get("DLpy")
    else:
        cbar = Bar()
        if not ux_note("Comprobando DLpy"):      # 0.9.4: dentro de la escena el texto de estado hace de barra
            cbar.start("Comprobando DLpy")
        try:
            rel = fetch_latest_release(timeout=8 if force else 5)      # la actualización sale solo de los Releases
        finally:
            cbar.stop()
    sync_changelog(fetch=False)                 # changelog.md ← release notes de los Releases recién leídos
    if not rel:
        if not PREFETCH["quiet_fail"]:
            ux_note("No se pudo comprobar DLpy", SCENE_DWELL)
        m_warn(f"DLpy {VERSION} · no se pudo comprobar la última versión (Releases de GitHub)")
        return False
    remote, text = rel["ver"], rel["text"]
    UPDATE_CHECKED["ok"] = True                # hubo respuesta: cuenta como comprobada
    status = update_status(remote)
    if status == "nueva":
        PREFETCH["changed"] = True
    if status == "igual":
        try:
            mine = read_text(SCRIPT_PATH)
        except (OSError, ValueError) as _ign:
            ignore("check_update", _ign)
            mine = None
        same = compare_texts(text, mine) if mine is not None else None
        if not pre:                              # 1.4.4: en paralelo, el resumen final lo dice por todos
            # 1.6.5: misma versión (≈ si el código difiere)
            version_scene("same", VERSION, remote, f"DLpy {VERSION} · última versión", edited=(same == "distinto"))
        m_check(f"DLpy {VERSION} · última versión" + (" · idéntica al Release" if same == "igual" else ""))
        if same == "distinto":
            add, rem = diff_counts(diff_lines(text, mine, "Release", "instalada"))
            m_warn(f"{VERSION} · Release ≠ instalada (código distinto: -{rem} +{add} líneas)")
            note("Mismo número con código distinto: revisa cuál es el bueno.")
        return False
    if status == "local":
        if not pre:
            # 1.7.1: la del Release es anterior: animación propia (antes «downgrade»)
            version_scene("ahead", remote, VERSION, f"DLpy {VERSION} · versión local")
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
    m_info(f"Hay una versión nueva de DLpy: {VERSION} → {remote} (Release)")
    # 1.6.5: la subida detectada se anima
    version_scene("updated", VERSION, remote, f"Nueva versión de DLpy · {VERSION} → {remote}")
    if not ux_on():                        # dentro de la escena no se pintan avisos ni release notes
        show_verify(rel["url"])
    # a-Shell: esta pregunta va con input() normal (sin cbreak). Después la versión nueva corre en
    # este mismo proceso y cambiar el modo del terminal justo antes la congelaba.
    if ux_on():                            # 0.9.4: sin preguntas en la escena: la respuesta por omisión de siempre
        go = True
    elif late:
        go = confirm_install(f"Instalar la {remote} para la próxima vez", remote, rel["notes"], rel["date"],
                             seconds=WAIT_SECONDS)
    else:
        go = confirm_install(f"Instalar la {remote} y ejecutarla ahora", remote, rel["notes"], rel["date"])
    if not go:
        note(f"Se volverá a preguntar en la próxima comprobación ({update_every_text()}) o con --actualizar.")
        return False
    ux_note(f"Instalando DLpy {remote}", 0.5)
    _t_w = time.time()
    try:
        write_text(SCRIPT_PATH, text)
        net_set("write", _t_w, True)
    except DISK_ERRORS as e:
        net_set("write", _t_w, False, err=type(e).__name__)
        ux_note(f"No se pudo instalar DLpy {remote}", SCENE_DWELL)
        m_warn(f"No se pudo instalar la actualización: {e}")
        return False
    ux_note(f"DLpy {remote} · instalada", SCENE_DWELL)
    m_check(f"DLpy {remote} · instalada")
    if late:
        m_info(f"Se usará la {remote} la próxima vez que abras DLpy.")
        return False
    reexec_script()                                    # termina con SystemExit
    return True


def late_updates():
    """Con --shortcutpick SIN escena viva las actualizaciones no se buscan al abrir sino aquí, tras la descarga y justo antes de entregar el archivo (1.8.0: con escena viva van primero, ver updates_first)."""
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
        if LANG in PACK_LANGS:
            lang_pack_sync(LANG)      # 1.9.2: el modo tardío también comparte el calendario del actualizador
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
                ux_set(pip_line=lines[-1])
        stop.wait(0.2)


def pip_run(args):
    """Lanza pip con `args`."""
    cmd = pip_cmd(args)
    pkg = next((a for a in args if a != "install" and not a.startswith("-")), "pip").split("==", 1)[0]
    t0 = time.time()
    if ux_on():
        # 1.2.6: el comando que corre (1.3.3: la escena teclea el mismo, de pip_cmd(pip_args(…)))
        ux_set(cmd=cmd)
    if ux_on() and SCENE_PIP:           # 0.9.4: dentro de la escena pip escribe a un archivo para no pisarla
        log = os.path.join(STATE_DIR, "pip_scene.log")
        stop = threading.Event()
        with quiet("pip_run escena"):
            if os.path.exists(log):
                os.remove(log)
            # 1.4.4: la última línea de pip se ve en la escena
            threading.Thread(target=_pip_tail, args=(log, stop), daemon=True).start()
            try:
                with net_busy():                                              # 1.8.8: pip habla con PyPI mientras corre
                    rc = sh_run(cmd + " > " + shlex.quote(log) + " 2>&1")
            finally:
                stop.set()
                ux_set(pip_line=None)
            net_set("pip:" + pkg, t0, rc == 0, val=None, err=None if rc == 0 else f"pip falló ({rc})")
            if os.path.exists(log):
                with quiet("pip_run log", OSError, ValueError):
                    dbg("pip (escena)", read_text(log)[-400:])
                    os.remove(log)
                return rc
    ux_stop(clear=True)                  # 0.9.3: pip escribe directo en el terminal: la escena cede
    with net_busy():
        rc = sh_run(cmd)
    net_set("pip:" + pkg, t0, rc == 0, err=None if rc == 0 else f"pip falló ({rc})")
    return rc


def pip_install(pip_name):
    """Instala/actualiza `pip_name`."""
    m_info(f"Instalando {pip_name}...")
    PREFETCH["changed"] = True
    if ux_on() and pip_name.split("==", 1)[0].lower() not in str(ux_get("label") or "").lower():
        # 1.3.3: la escena habla de lo que corre de verdad (--scb instalaba yt-dlp con otro texto)
        ux_note(f"Instalando {pip_name}")
    try:
        rc = pip_run(pip_args(pip_name))
    except Exception as e:
        ignore("pip_install", e)
        m_warn(f"No se pudo lanzar pip para {pip_name}: {type(e).__name__}")
        return False
    finally:
        ux_pop("cmd")                          # 1.2.6: terminó: la escena vuelve a sus comandos de muestra
        refresh_paths()
    if rc != 0:
        code = rc                                      # 1.8.7: sh_run ya devuelve el código real
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
    """Si hay runtime de JavaScript, deja instalado yt-dlp-ejs en la versión que pide yt-dlp.
    1.7.1: con escena (D L P Y) no pregunta (Sí por omisión, como pip y yt-dlp) y la escena muestra lo que de verdad corre: «Instalando / Actualizando
    yt-dlp-ejs==X», su resultado (✓ / ✗) y la verificación «yt-dlp-ejs X · para YouTube». Sin escena (UIM) pregunta como siempre."""
    if not ytdlp_needs_js() or not js_runtime():
        return
    pin = ejs_pin()
    if not pin:
        return
    want = pin.split("==", 1)[1] if "==" in pin else None
    cur = pkg_version("yt-dlp-ejs") if is_installed("yt_dlp_ejs") else None
    if cur and (not want or cur == want):
        # 1.7.1: ✓ en la escena (verificación local, sin red ni pip)
        ux_note(f"yt-dlp-ejs {cur} · para YouTube", SCENE_DWELL)
        m_check(f"yt-dlp-ejs {cur} · para YouTube")
        declined_clear("yt-dlp-ejs")
        return
    what = "yt-dlp-ejs" + (f" {want}" if want else "")
    if not force and load_json(DEPS_STATE_FILE).get("yt-dlp-ejs") == pin:
        m_warn(f"{what} · " + (f"tienes {cur}" if cur else "falta")
               + " (rechazado; --actualizar lo pregunta)")
        return
    m_warn(f"{what} · " + (f"tienes {cur}" if cur else "falta") + " (YouTube lo necesita)")
    verb = "Actualizando" if cur else "Instalando"
    # 1.7.1: sin preguntas en la escena (Sí por omisión): se instala dentro de ella
    if ux_on():
        ux_note(f"{verb} {pin}", 0.5)
        wanted = True
    else:
        wanted = ask(f"¿Instalar {pin}? (S/n) ▸ ", seconds=WAIT_SECONDS)
    if wanted:
        pip_install(pin)
        if is_installed("yt_dlp_ejs"):
            ver = pkg_version("yt-dlp-ejs") or ""
            # 1.7.1: ✓ en la escena
            ux_note(f"yt-dlp-ejs {ver} · {'actualizada' if cur else 'instalado'}".replace("  ", " "), SCENE_DWELL)
            m_check(f"yt-dlp-ejs {ver} · instalado".replace("  ", " "))
            declined_clear("yt-dlp-ejs")
        else:
            # 1.7.1: ✗ en la escena
            ux_note(f"No se pudo {'actualizar' if cur else 'instalar'} yt-dlp-ejs", SCENE_DWELL)
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
            # 1.1.5: sin preguntas en la escena (Sí por omisión): se instala dentro de ella
            if ux_on():
                ux_note(f"Instalando {pip_name}")
                wanted = True
            else:
                ux_stop(clear=True)                   # 0.9.4: esto sí hay que preguntarlo: la escena cede
                m_warn(f"Falta la dependencia: {pip_name}" + (" (obligatoria)" if required else ""))
                wanted = ask(f"¿Instalar {pip_name}? (S/n) ▸ ", seconds=WAIT_SECONDS)
            if wanted:
                pip_install(pip_name)
            if not is_installed(module):
                if wanted:
                    # 1.3.3: ✗ en la escena (sin escena no hace nada)
                    ux_note(f"No se pudo instalar {pip_name}", SCENE_DWELL)
                if required:
                    if wanted:
                        m_err(f"No se detectó {pip_name} tras instalarlo.")
                        m_info("Si pip indicó éxito, vuelve a ejecutar DLpy; si no: pip install " + pip_name)
                    else:
                        m_err(f"{pip_name} es obligatoria: sin ella DLpy no puede continuar.")
                        m_info("Instálala con: pip install " + pip_name)
                    return False
                continue
            # 1.3.3: ✓ en la escena
            ux_note(f"{pip_name} {pkg_version(pip_name) or ''} · instalado".replace("  ", " "), SCENE_DWELL)
            m_check(f"{pip_name} {pkg_version(pip_name) or ''} · instalado".replace("  ", " "))
            continue

        if not due:
            continue
        cur = pkg_version(pip_name)
        # 1.4.4: ya la pidió prefetch_phase, en paralelo
        pre = PREFETCH["on"] and pip_name in PREFETCH["keys"] and not late
        if pre:
            PREFETCH["keys"].remove(pip_name)
            lat = PREFETCH["res"].get(pip_name)
        else:
            cbar = Bar()
            if not ux_note(f"Comprobando {pip_name}"):    # 0.9.4: dentro de la escena el texto de estado hace de barra
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
                if ux_note(f"Actualizando {pip_name} → {lat}", 0.5):     # sin preguntas en la escena: Sí por omisión
                    wanted = True
                else:
                    wanted = ask(f"¿Actualizar {pip_name}? (S/n) ▸ ", default=True, seconds=WAIT_SECONDS)
                if wanted:
                    done = pip_install(pip_name)
                    if ux_on():
                        ux_note(f"{pip_name} {pkg_version(pip_name) or '?'} · actualizada" if done
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
                ux_note(f"{pip_name} {cur} · última versión", SCENE_DWELL)
            m_check(f"{pip_name} {cur} · última versión")
        else:
            net_ok = False                       # sin respuesta de PyPI: se reintenta al siguiente arranque
            if not PREFETCH["quiet_fail"]:
                ux_note(f"No se pudo comprobar {pip_name}", SCENE_DWELL)
            m_warn(f"{pip_name} {cur or '?'} · no se pudo comprobar la última versión")
    if due:
        if not late:
            check_js_components(force)
        if net_ok:
            check_mark(key)
    return True


# ╔═════════════════════════════════════════════════════════════════════════════════════════════════════════╗
# ║ ÁREA G · MANTENIMIENTO Y VERSIONES — changelog, almacenamiento, versión, releases, --versions           ║
# ╚═════════════════════════════════════════════════════════════════════════════════════════════════════════╝
# ───────────────────── [G1] Changelog ─────────────────────
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
    """changelog.md ya se escribe directamente en dlpy_files."""
    return os.path.isfile(CHANGELOG_FILE)


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
    """Al abrir: mantiene una única copia en dlpy_files/changelog.md."""
    missing = not os.path.isfile(CHANGELOG_FILE)
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


def script_variants(live=None, md=None):
    """(sin_changelog, con_changelog)"""
    if live is None:
        live = read_text(SCRIPT_PATH)
    m = CL_RE.search(live)
    if m:                                    # el .py todavía trae su changelog
        return live[:m.start()] + live[m.end():], live
    if md is None and os.path.isfile(CHANGELOG_FILE):
        with quiet("script_variants", OSError):
            md = read_text(CHANGELOG_FILE)
    block = changelog_block_from_md(md)
    return live, (insert_changelog_block(live, block) if block else None)
# ───────────────────── [G2] Limpieza de almacenamiento ─────────────────────
CLEAN_LIMIT = int(_env_num("DLPY_STORAGE_LIMIT_MB", 1024.0) * 1024 * 1024)      # «inf» ya no impide arrancar


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
    """Quita subcarpetas vacías de root (no root en sí)."""
    for dp, dns, fns in os.walk(root, topdown=False):
        if dp == root:
            continue
        if dp == INTERNAL_DIR or dp.startswith(INTERNAL_DIR + os.sep):
            continue                # la carpeta oculta del script no se toca
        with quiet("prune_empty_dirs", OSError):
            os.rmdir(dp)            # solo funciona si está vacía


def storage_groups():
    """Rutas que se pueden limpiar, por categoría."""
    dl, cache = [], []
    if os.path.isdir(FILES_DIR):
        for n in sorted(os.listdir(FILES_DIR)):
            p = os.path.join(FILES_DIR, n)
            if is_data_entry(n) and os.path.isfile(p):
                if is_video_file(p):
                    dl.append(p)
            elif is_data_entry(n) and os.path.isdir(p) and not os.path.islink(p):
                dl += video_files(p)        # videos de las subcarpetas
    for p in (CACHE_DIR, WORK_ROOT):
        if os.path.isdir(p):
            cache.append(p)
    if os.path.isdir(DELIVERY_DIR):
        for n in sorted(os.listdir(DELIVERY_DIR)):
            p = os.path.join(DELIVERY_DIR, n)
            if os.path.isdir(p) and video_files(p):
                dl.append(p)       # copias de entrega al atajo (solo si contienen video)
    return {"dl": dl, "cache": cache}


def storage_report():
    """Bytes por categoría + otros + total, sin contar dos veces los enlaces duros."""
    groups = storage_groups()
    seen = set()
    r = {k: sum(tree_size(p, seen) for p in groups[k]) for k in ("dl", "cache")}
    # Lo que no cae en ninguna categoría (índice, changelog…)
    r["other"] = tree_size(INTERNAL_DIR, seen) + tree_size(FILES_DIR, seen)
    r["total"] = r["dl"] + r["cache"] + r["other"]
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
    # El changelog ya no necesita internal/script; los registros quedan centralizados en internal/logs.
    for d in (FILES_DIR, INTERNAL_DIR, STATE_DIR, CACHE_DIR, STREAM_CACHE_DIR, WORK_ROOT,
              DELIVERY_DIR, TRASH_DIR, LOGS_DIR):
        try:
            os.makedirs(d, exist_ok=True)
        except OSError as _ign:
            ignore('ensure_dirs', _ign)
    ensure_internal_logs()


def check_storage():
    """0.9.9: solo avisa, conserva descargas. 2.0.9: DLPY_KEEP_DOWNLOADS_OVER_LIMIT (antes DLPY_CONSERVE) sí se lee: 1 = conservar (por omisión, como siempre) · 0 = permitir limpieza."""
    if _flag_env("DLPY_KEEP_DOWNLOADS_OVER_LIMIT", True):
        with quiet("check_storage 0.9.9"):
            seen = set()
            total = tree_size(INTERNAL_DIR, seen) + tree_size(FILES_DIR, seen)
            if total > CLEAN_LIMIT:
                m_warn(f"Almacenamiento {human_size(total)} supera límite {human_size(CLEAN_LIMIT)} pero se conserva (DLPY_KEEP_DOWNLOADS_OVER_LIMIT=1).")
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
    """Descargas sueltas en dlpy_files y sus subcarpetas (sin carpetas ocultas, enlaces ni otros archivos)."""
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
            # 1.7.9: un apóstrofo en el nombre cambia el entrecomillado en el reintento
            for form in ash_quote_forms(path):
                rc = sh_run(f"trash {form} >/dev/null 2>&1")
                if rc == 0 and not os.path.exists(path):
                    return True
    return False

def log_shortcutmode_diagnostic(kind, msg):
    """Guarda errores y advertencias por separado dentro de internal/logs/."""
    try:
        level = "WARNING" if str(kind).upper() in ("WARNING", "WARN", "A") else "ERROR"
        path = WARNING_LOG_FILE if level == "WARNING" else SHORTCUTMODE_LOG
        os.makedirs(os.path.dirname(path), exist_ok=True)
        clean = str(msg).replace(chr(10), " ").replace(chr(13), " ").strip()[:800]
        line = time.strftime("%Y-%m-%d %H:%M:%S") + " [" + level + "] " + clean + chr(10)
        with open(path, "a", encoding="utf-8", errors="replace") as fh:
            fh.write(line)
    except Exception as _ign:
        try:
            dbg("registro de diagnóstico falló", repr(_ign))
        except Exception:
            pass


def log_shortcutmode_error(msg):
    """Registra y cuenta un error procedente de stderr o del modo atajo."""
    diagnostic_report("E", msg)


def log_shortcutmode_stderr(msg):
    """Clasifica stderr: warnings reconocibles van a warnings.log; el resto, a errors.log."""
    raw = str(msg or "")
    is_warning = bool(re.search(r"(?i)(?:\[WARNING\]|\bWARN(?:ING)?\b|\b[A-Za-z]+Warning:)", raw))
    if is_warning:
        diagnostic_report("A", raw)
    else:
        log_shortcutmode_error(raw)


def ensure_trash():
    for d in (TRASH_DIR, TRASH_INTERNAL):
        try:
            os.makedirs(d, exist_ok=True)
        except OSError as _ign:
            ignore('ensure_trash: crear carpeta', _ign)
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
    except OSError as e:
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
                if ux_on():
                    # 1.1.7: en la escena no se imprime
                    dbg("trash borrado", {"archivo": os.path.basename(p), "dias": int(age // 86400)})
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
    in_scene = bool(ux_on())
    gone = int(ux_get("trash_gone") or 0)                      # 1.1.8: lo ya borrado de la papelera en este arranque
    # 1.1.5: la limpieza se ve en la escena (dibujo «clean»), no en el shell
    if in_scene:
        ux_set(clean=len(rows))
        ux_status(clean_label("Limpiando", len(rows), gone))
    moved = 0
    for p, age, size in rows:
        if move_to_trash(p):
            moved += 1
    if moved:
        prune_empty_dirs(FILES_DIR)
        prune_index()
        m_ok(f"Movidos a papelera: {moved} archivo(s) de más de {TRASH_DAYS:g} días. Se borrarán tras {TRASH_EXPIRE_DAYS:g} días en trash.")
    if in_scene:
        ux_set(clean=moved)
        ux_status(clean_label("Limpiando", moved, gone))
        ux_hold(SCENE_CLEAN_SECS)                              # se alcanza a ver caer los archivos antes de seguir
    return moved


def is_data_entry(name):
    """Nombre que cuenta como descarga completada (no basura)."""
    return not (name.startswith(".") or name.endswith((".tmp", ".part", ".ytdl", ".temp"))
                or name in RESERVED)


def reset_previous(prev, announce=True):
    """1.6.6: al cambiar de versión borra .dlpy_internal entero y conserva dlpy_files (descargas, papelera y configuración). Nada se archiva."""
    dbg("reset_previous", f"borrando {INTERNAL_DIR}, conservando {FILES_DIR}")
    try:
        if os.path.isdir(INTERNAL_DIR):
            shutil.rmtree(INTERNAL_DIR, ignore_errors=True)
        ensure_dirs()
        ensure_trash()
        m_info(f"Actualización {prev} -> {VERSION}: {INTERNAL_NAME} reiniciado, descargas conservadas.")
    except OSError as e:
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
                 "externa": "El dlpy.py se reemplazó por uno más viejo fuera de DLpy "
                            "(copia manual, atajo o copia antigua)."}


def downgrade_notice(stored):
    """Registro de la bajada `stored` → VERSION (sin escribirlo a disco ni imprimir:"""
    return make_downgrade_record(stored, VERSION, load_json(DOWNGRADE_FILE).get("pending"))


def update_card_rows(stored, current, down, freed, inner):
    """Líneas (pintadas)"""
    if down:
        # 1.7.1: traducida
        rows = card_text_rows(t_status(f"Bajada de versión {stored} → {current}"), inner, "white", True, "!", "amber")
        rows += card_text_rows(t_display(DOWNGRADE_WHY.get(down.get("causa"), DOWNGRADE_WHY["externa"])), inner)
    else:
        rows = card_text_rows(t_status(f"Actualizada {stored} → {current}"), inner, "white", True, "✓", "mint")
    if freed is None:
        rows += card_text_rows(t_status(f"no se pudo reiniciar {INTERNAL_NAME}"), inner, "amber", False, "!", "amber")
    else:
        rows += card_text_rows(t_display("carpeta interna reiniciada"), inner)
    return rows


def show_update_card(stored, down, freed):
    """Una sola tarjeta con lo ocurrido al cambiar de versión (en vez de varios mensajes sueltos)."""
    try:
        lines = update_card_rows(stored, VERSION, down, freed, card_inner())
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
        if ux_welcome("same", VERSION, VERSION, edited=True):
            return
    except KeyboardInterrupt:
        raise
    except Exception as _ign:
        ignore("show_edit_card", _ign)
    try:
        rows = card_text_rows(t_display(f"Edición detectada · {VERSION}"), card_inner(), "white", True, "✓", "mint")
        rows += card_text_rows(t_display("Cambió el hash · misma versión"), card_inner())
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
        change = ux_code_change(state.get("code_hash"), cur_hash)      # 1.3.2: misma versión, ¿otro código?
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
        # bottombar: el script se reemplazó por uno más viejo
        diagnostic_report("A", f"Bajada de versión {stored} → {VERSION}")
    if not reset_previous(prev, announce=bool(stored)):
        return False

    freed = 0
    if stored:                # subida o bajada: .dlpy_internal empieza de cero
        freed = reset_internal()
        if freed is not None:
            ensure_dirs()
        else:
            diagnostic_report("A", f"no se pudo reiniciar {INTERNAL_NAME}")
        show_update_card(stored, down, freed)
    save_json(VERSION_FILE, {"version": VERSION, "code_hash": cur_hash})
    ensure_changelog()       # changelog.md ← release notes de GitHub (versión actual e inferiores)
    if down:
        downgrade_commit(down)
    # 1.2.9: dentro de la escena, «Primera ejecución» o «Actualizado» (fuera de ella ya salió la tarjeta)
    try:
        ux_welcome(ux_welcome_kind(stored, VERSION), stored, VERSION, down=bool(down))
    except KeyboardInterrupt:
        raise
    except Exception as _ign:
        ignore("scene_welcome", _ign)
    return True
# ───────────────────── [G5] Releases de GitHub (listado) ─────────────────────
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
        with net_busy(), urllib.request.urlopen(req, timeout=timeout) as r:
            GH_LAST["code"], GH_LAST["err"] = getattr(r, "status", None) or r.getcode(), None
            return json.load(r)
    except NET_ERRORS as _ign:
        ignore("remote_releases", _ign)
        GH_LAST["code"], GH_LAST["err"] = None, net_err_text(_ign)
        return None


def _releases_data(timeout=8, pages=REL_MAX_PAGES):
    """(respuesta JSON de la API de GitHub para /releases con todas las páginas, info)"""
    info = repo_info()
    if not info:
        return None, None
    gh_notice(t("leyendo los Releases de") + f" {info[0]}/{info[1]} " + t("(versiones y changelog)"))
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


def release_rows(releases):
    """Filas de la lista de --versions: una por Release."""
    return [{"ver": r["ver"], "src": "release", "ref": r["url"], "notes": r["notes"],
             "date": r.get("date") or "", "label": "Release"} for r in releases or []]
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


# ───────────────────── [G8] Pantalla de versiones (--versions) ─────────────────────
# 1.6.6: sin sistema de fallos ni backups. --versions solo lista los Releases de GitHub y deja instalar uno (nada se guarda aparte).
def version_rows(rows, cur, upd, start=1):
    """2.0.0: filas de la lista de versiones en el formato de print_rows (el mismo dibujo que las demás listas): número, versión y fecha; marcas ✓ actual y ⬆ la de actualizar."""
    dated = any(r.get("date") for r in rows)
    return [{"n": i, "flags": ({"cur"} if r["ver"] == cur else set()) | ({"upd"} if upd and r["ver"] == upd else set()),
             "cols": [r["ver"], r.get("date") or ""] if dated else [r["ver"]]} for i, r in enumerate(rows, start)]


def install_text(src, ver):
    """Texto válido (con versión y SHA-256 correcto) del Release, o None."""
    m_info(f"Descargando la {ver} desde {src['label']}...")
    return fetch_remote_script(timeout=20, url=src["ref"])


def parse_menu_choice(ans, n):
    """0 = no instalar (vacío / 0 / n / no); 1..n = esa opción; None = no se entiende."""
    a = (ans or "").strip().lower()
    if a in ("", "0", "n", "no"):
        return 0
    if a.isdecimal() and 1 <= int(a) <= n:
        return int(a)
    return None


def install_version(ver, text, hold=True):
    """Reemplaza dlpy.py por `text` (versión `ver`). Si es más vieja que la actual lo anota para check_version (bajada a propósito)."""
    try:
        write_text(SCRIPT_PATH, text)
    except DISK_ERRORS as e:
        m_err(f"No se pudo instalar la {ver}: {e}")
        return False
    if version_move(VERSION, ver) == "baja":          # downgrade a propósito: lo anota check_version al arrancar
        mark_downgrade_pending(VERSION, ver, "manual", hold)
    return True


def _version_rows():
    """Busca los Releases de GitHub y devuelve sus filas (vacío si no hay o no se pudieron leer)."""
    cbar = Bar()
    cbar.start("Buscando versiones")
    try:
        releases = remote_releases()
    finally:
        cbar.stop()
    if releases is None:
        m_warn("No se pudieron leer los Releases de GitHub.")
    elif not releases:
        m_warn("El repositorio no tiene Releases publicados.")
    rows = release_rows(releases)
    if not rows:
        m_warn("No hay versiones para instalar (Releases de GitHub).")
    return rows


def _pick_version(rows):
    """Muestra las versiones (marcando la actual y la de actualizar) y deja elegir una; None si no se elige ninguna."""
    upd = rows[0]["ver"]
    shown = rows[:20]
    vrows = version_rows(shown, VERSION, upd)
    legend_txt = "✓ actual · ⬆ la de actualizar"

    def draw(full):
        """Pantalla de versiones dentro de las 26 líneas; True si quedan ocultas (se ven con «m»)."""
        if full:
            hide_keyboard(0.3)
        clear_screen()
        header(t_display("VERSIONES"), gap=False)
        used = banner_height() + 1 + 1 + 1 + len(legend_lines(legend_txt))      # banner, cabecera, nota de «más», prompt, leyenda
        cap = None if full else visible_cap(used)
        k = len(vrows) if cap is None else min(len(vrows), max(1, cap))
        legend_note(legend_txt)
        print_rows(vrows[:k], ["cur", "upd"], num_w=len(str(len(vrows))))
        if k < len(vrows):
            note(f"(+{len(vrows) - k} más: «m»)")
        elif len(rows) > len(shown):
            note(f"(+{len(rows) - len(shown)} más antiguas sin mostrar)")
        return k < len(vrows)

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
                               + " (o Enter para no instalar).")
            continue
        break
    return shown[n - 1] if n else None


def _install_version(row):
    """Confirma e instala la versión `row` (release notes, bajar de versión)."""
    ver = row["ver"]
    if not confirm_install(f"Instalar la {ver}", ver, row["notes"], row["date"]):
        return None
    text = install_text(row, ver)
    if not text:
        m_err(f"No se pudo obtener la {ver} (descarga fallida, archivo no válido o SHA-256 que no coincide).")
        return None
    show_verify(row["ref"])
    with quiet("offer_versions", OSError, ValueError):
        if text_fingerprints(text)[1] == text_fingerprints(read_text(SCRIPT_PATH))[1]:
            m_info(f"La {ver} ({row['label']}) es idéntica a la instalada; no hay nada que cambiar.")
            return None
    down = version_move(VERSION, ver) == "baja"
    stay = True
    if down:                                  # versión más vieja: ¿bloquear actualizar hasta que salga otra?
        stay = ask(f"¿Quedarte en la {ver} hasta que salga una más nueva?", default=False)
    if not install_version(ver, text, stay):
        return None
    return ver, down, stay


def _version_notes(ver, down, stay):
    """Avisos tras instalar: qué pasará con las actualizaciones."""
    if down:
        if stay:
            note(f"Bajaste de la {VERSION} a la {ver}. No se ofrecerá actualizar hasta que haya un Release con una "
                 f"versión más nueva que la {VERSION}; con --actualizar puedes volver a instalarla.")
        else:
            note(f"Bajaste de la {VERSION} a la {ver}. En el próximo arranque se volverá a ofrecer "
                 f"actualizar.")


def offer_versions():
    """--versions: lista los Releases de GitHub y deja instalar uno."""
    rows = _version_rows()
    if not rows:
        return False
    row = _pick_version(rows)
    if row is None:
        return False
    done = _install_version(row)
    if done is None:
        return False
    ver, down, stay = done
    m_check(f"DLpy {ver} · instalada ({row['label']})")
    _version_notes(ver, down, stay)
    reexec_script()                                       # termina con SystemExit
    return True


# ───────────────── [L0] Instancia única y vigilante (2.0.3) ─────────────────
# a-Shell avisa «too many python scripts running» cuando hay demasiados intérpretes vivos, y desde Atajos (extensión, sin terminal) una ejecución
# que Atajos ya cortó puede seguir viva y dejar a a-Shell sin responder. Aquí: state/instance.json guarda id, hora de inicio y un «latido» que un hilo
# refresca cada GUARD_BEAT s. Otra ejecución que arranque con un latido reciente espera un poco y, si sigue viva, avisa y sale (--scm / --scb: JSON
# con error_code «busy»). Un latido viejo (proceso muerto o congelado por iOS) o una ejecución --scm que pasó de GUARD_EXT_LIMIT s no estorban.
# El mismo hilo, con DEBUG, anota en el log la pila de todos los hilos cuando el flujo principal lleva GUARD_STUCK s en la misma línea.
# DLPY_SINGLE_INSTANCE_WATCHDOG=0 lo apaga. No mata nada: en a-Shell matar un hilo dentro de ssl dio segmentation fault (ver --scm).
GUARD = {"id": None, "stop": threading.Event(), "thread": None, "mode": "run", "t0": 0.0, "limit": 0.0}
GUARD_BEAT, GUARD_STALE, GUARD_WAIT, GUARD_STUCK, GUARD_EXT_LIMIT = 2.0, 7.0, 4.0, 15.0, 20.0
GUARD_BUSY = "Otra ejecución de DLpy sigue activa: espera a que termine."
GUARD_SKIP = ("--selftest", "--sistema", "--perfil", "--atajo", "--shortcut")  # JSON puro: no toman el bloqueo


def guard_on():
    return _flag_env("DLPY_SINGLE_INSTANCE_WATCHDOG", True)


def guard_mode(args):
    """scm · scb · pick (shortcutpick) · run (el resto)."""
    if wants_scm(args):
        return "scm"
    if wants_scb(args):
        return "scb"
    return "pick" if _wants(args, "shortcutpick") else "run"


def guard_path():
    return os.path.join(STATE_DIR, "instance.json")


def guard_read():
    """El bloqueo escrito en disco (dict) o None."""
    with quiet("guard_read", OSError, ValueError):
        with open(guard_path(), "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else None
    return None


def guard_write():
    info = {"id": GUARD["id"], "mode": GUARD["mode"], "t0": GUARD["t0"], "limit": GUARD["limit"], "beat": time.time(), "version": VERSION}
    with quiet("guard_write", OSError, ValueError, TypeError):
        write_text(guard_path(), json.dumps(info), mkdir=True)


def guard_alive(info, now=None):
    """¿`info` es de OTRA ejecución viva? Latido reciente y, en --scm, dentro de su límite (pasado el límite es una ejecución que Atajos ya cortó)."""
    if not info or info.get("id") == GUARD["id"]:
        return False
    now = time.time() if now is None else now
    try:
        if now - float(info.get("beat") or 0) > GUARD_STALE:
            return False
        limit = float(info.get("limit") or 0)
    except (TypeError, ValueError):
        return False
    return not (limit and now > limit)


def guard_release():
    GUARD["stop"].set()
    info = guard_read()
    if info and info.get("id") == GUARD["id"]:
        with quiet("guard_release", OSError):
            os.remove(guard_path())


def _guard_dump(secs):
    import traceback
    names = {t.ident: t.name for t in threading.enumerate()}
    parts = ["hilo %s:\n%s" % (names.get(tid, tid), "".join(traceback.format_stack(fr)[-5:])) for tid, fr in sys._current_frames().items()]
    dbg("vigilante: el flujo principal lleva %d s en la misma línea (puede ser una espera normal)" % secs, "\n".join(parts)[:3000])


def _guard_loop():
    main_id = threading.main_thread().ident
    last, since, dumped = None, time.time(), set()
    while not GUARD["stop"].wait(GUARD_BEAT):
        guard_write()
        fr = sys._current_frames().get(main_id) if DEBUG else None
        if fr is None:
            continue
        key, now = (fr.f_code.co_filename, fr.f_lineno), time.time()
        if key != last:
            last, since = key, now
        elif now - since >= GUARD_STUCK and key not in dumped:
            dumped.add(key)
            _guard_dump(int(now - since))


def guard_start():
    sys._dlpy_guard_id = GUARD["id"]                  # una versión lanzada con runpy en este mismo proceso reutiliza el bloqueo
    guard_write()
    atexit.register(guard_release)
    GUARD["thread"] = threading.Thread(target=_guard_loop, daemon=True)
    GUARD["thread"].start()


def instance_guard(args):
    """None = seguir. Con otra ejecución viva avisa y devuelve el código de salida."""
    if not guard_on() or any(a in GUARD_SKIP for a in args) or _wants(args, "config") or _wants(args, "cleartest") or wants_atajo(args):
        return None
    if getattr(sys, "_dlpy_guard_id", None):          # reejecución dentro del mismo proceso (reexec_script)
        GUARD["id"] = sys._dlpy_guard_id
        return None
    GUARD["id"], GUARD["mode"], GUARD["t0"] = uuid.uuid4().hex, guard_mode(args), time.time()
    GUARD["limit"] = GUARD["t0"] + GUARD_EXT_LIMIT if GUARD["mode"] == "scm" else 0.0
    info = guard_read()
    end = time.time() + (GUARD_WAIT if GUARD["mode"] == "run" else 1.5)       # desde Atajos no se puede esperar mucho
    while guard_alive(info) and time.time() < end:
        time.sleep(0.3)
        info = guard_read()
    if not guard_alive(info):
        guard_start()
        return None
    dbg("instancia: ya hay otra ejecución", info)
    if GUARD["mode"] in ("scm", "scb"):
        out = shortcut_error("busy", GUARD_BUSY)
        sys.stdout.write(json.dumps(json_clean(out), ensure_ascii=True, separators=(",", ":")) + "\n")
        sys.stdout.flush()
        return 0
    m_err(GUARD_BUSY)
    return 1


def run_main(entry):
    """Ejecuta entry(). Con --versions muestra la lista de versiones; y recuerda si esta ejecución la lanzó otra versión (runpy en a-Shell)."""
    args = norm_args(sys.argv[1:])           # «—versions» (raya larga de iOS) = «--versions»
    busy = instance_guard(args)               # 2.0.3: una sola ejecución a la vez
    if busy is not None:
        return busy
    if "--selftest" in args or "--sistema" in args or "--perfil" in args or _wants(args, "config") or _wants(args, "cleartest") or wants_languages(args) or wants_2shortcuts(args) or wants_scm(args) or wants_scb(args) \
            or _wants(args, "shortcutpick") or wants_atajo(args):
        return entry()
    if "--versions" in args:                 # lista manual de versiones
        clear_screen()
        offer_versions()
        return 0
    nested = getattr(sys, "_dlpy_guarded", False)     # tras actualizar/instalar otra versión (runpy)
    RUNTIME["nested_ios"] = bool(nested)
    sys._dlpy_guarded = True
    try:
        return entry()
    finally:
        if not nested:
            with quiet("run_main", AttributeError):
                del sys._dlpy_guarded


# ╔════════════════════════════════════════════════════════════════════════════════════════════════╗
# ║ ÁREA H · CACHÉ Y REANUDACIÓN — caché de streams, reanudación, carpeta interna                  ║
# ╚════════════════════════════════════════════════════════════════════════════════════════════════╝

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
            if n.startswith(prefix) and "." not in n[len(prefix):] and not n.endswith((".part", ".ytdl", ".tmp", ".meta")):      # 1.7.5: «137.» no es «137.1.»
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
    except DISK_ERRORS as e:
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
        except OSError as e:
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


def resume_rows(items):
    """2.0.0: filas de la lista de pendientes en el formato de print_rows: título, avance («120 MB / 400 MB») y antigüedad."""
    return [{"n": n, "flags": set(),
             "cols": [it["title"], human_size(it["bytes"]) + (f" / {human_size(it['total'])}" if it["total"] > it["bytes"] else ""),
                      _resume_age(it["age"])]} for n, it in enumerate(items, 1)]


def resume_menu(items):
    """Pantalla de descargas pendientes. Devuelve las elegidas para reanudar ([] = ninguna). «D» las descarta."""
    items = list(items)
    while items:
        clear_screen()
        header(t_display("DESCARGAS PENDIENTES"), gap=False)
        m_info(f"{len(items)} sin terminar (caducan a las 24 h).")
        print_rows(resume_rows(items), [], clip=0)
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


# «․» (punto de enumeración): se ve como un punto pero no cuenta como extensión
DOT_SAFE = "\u2024"


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
    if ux_on() and ux_questions():
        # 0.9.3: hay algo que preguntar: la escena cede y sale como siempre (1.1.5: ux_questions ya es siempre False)
        ux_stop(clear=True)
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
    # 0.9.4: «Enviando a DLpy» (1.3.4: o «Abriendo con view»), la escena se cierra hacia el centro y borra la pantalla
    cleared = ux_end(view=(view_mode() == "view"))
    if not cleared:
        # 1.5.8 (UIM): sin escena solo se limpia la consola; la disolución es de la escena (UX)
        cleared = uim_final_clear()
    if _deliver_platform(final, title, quiet=cleared):
        mark_delivered(final)


def ash_quote(s, style="dq"):
    """1.7.9: entrecomilla `s` para el analizador de comandos de a-Shell (no entiende la forma POSIX de shlex.quote con un apóstrofo dentro).
    Sin apóstrofo: comillas simples (como shlex.quote). Con apóstrofo: comillas dobles, escapando con barra invertida la barra, la comilla doble, el $ y el acento grave
    (style="dq"), o, con style="bs", cada carácter raro con barra invertida."""
    s = str(s)
    if s and re.fullmatch(r"[A-Za-z0-9_@%+=:,./-]+", s):
        return s
    if "'" not in s:
        return "'" + s + "'"
    if style == "bs" and any(ord(c) < 32 or ord(c) == 127 for c in s):
        # 1.9.3: barra invertida + salto de línea es continuación de línea (el salto se perdería): con caracteres de control solo sirve las comillas dobles
        style = "dq"
    if style == "bs":
        return "".join(c if (c.isalnum() or c in "_@%+=:,./-") else "\\" + c for c in s)
    return '"' + re.sub(r'([\\"$`])', r"\\\1", s) + '"'


def ash_quote_forms(s):
    """1.7.9: las formas de entrecomillar `s` por orden de intento (una sola si da igual)."""
    forms = [ash_quote(s)]
    alt = ash_quote(s, "bs")
    if alt not in forms:
        forms.append(alt)
    return forms


def _deliver_view(final, quiet=False):
    """1.3.4: abre el archivo con el `view` de a-Shell. 1.7.9: con apóstrofo en el nombre, el reintento cambia de entrecomillado."""
    if not quiet:
        m_info("Abriendo con view...")
    cmds = ["view " + f for f in ash_quote_forms(final)]
    dbg("entrega", {"origen": final, "modo": "view", "comando": cmds[0]})
    for n in range(2):
        if n:
            time.sleep(OPEN_RETRY)
        if sh_run(cmds[min(n, len(cmds) - 1)]) == 0:
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
        if sh_run("open " + shlex.quote(url)) == 0:
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
    payload = json.dumps(json_clean(data), ensure_ascii=False)
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
        copied = sh_run("pbcopy < " + shlex.quote(tmp)) == 0
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
    sh_run("open " + shlex.quote(url))
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
    """Banderas extra de yt-dlp en bruto (DLPY_YTDLP_EXTRA_ARGS)."""
    raw = env_get("DLPY_YTDLP_EXTRA_ARGS", "").strip()
    try:
        mine = shlex.split(raw) if raw else []
    except ValueError as e:
        m_warn(f"DLPY_YTDLP_EXTRA_ARGS inválido: {e}")
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


ANALYSIS = {"stage": None, "t": None}          # etapa del análisis que funcionó


def analyze_link(yt_dlp, link, quick=False, argv=None):
    """Devuelve (info, base_opts)."""
    ux_set(link=link)                      # 1.4.3: la escena D L P Y teclea este enlace en extract_info(…)
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
                ANALYSIS["t"] = time.monotonic()      # 1.7.3: de cuándo son las URLs de los streams
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
    ux_set(ana_raw=True)                   # 1.4.4: este paso sí es `yt-dlp -J <enlace>`: la escena teclea ese comando
    _t_raw = time.time()
    info = probe_cli_json(link, extra, 60 if quick else 180)
    if info:
        net_set("analyze", _t_raw, True, None, str(info.get("extractor_key") or info.get("extractor") or "") or None)
    if info:
        dbg("análisis", "funcionó: yt-dlp en bruto (-J)")
        ANALYSIS["stage"] = "yt-dlp en bruto"
        ANALYSIS["t"] = time.monotonic()
        base = cli_like_opts(yt_dlp, ["--no-playlist"] + extra) or {}
        return info, base
    raise last or RuntimeError("no se pudo analizar el enlace")


# Errores que justifican reanalizar el enlace (se evalúa sobre el texto en minúsculas).
_RETRY_RE = re.compile(r"not available|expired|forbidden|\bhttp error (?:403|410)\b")


def _dl_ok(res):
    """1.7.1: ¿yt-dlp dejó al menos un archivo (requested_downloads con filepath)? Con ignoreerrors un fallo devolvía el análisis sin ruta y sin error."""
    try:
        return any((d or {}).get("filepath") for d in ((res or {}).get("requested_downloads") or []))
    except AttributeError:
        return False


# 1.7.3: s de vida del análisis antes de bajar; más viejo → se reanaliza (las URLs de los streams caducan)
INFO_TTL = _env_num("DLPY_ANALYZE_RESULT_TTL_SECS", 60.0)
# 1.7.3: pausa antes del último reintento si la URL recién obtenida también da 403 / 410
RETRY_PAUSE = 1.0


def analysis_age():
    """1.7.3: segundos desde que terminó el último análisis (None si no hay marca)."""
    t = ANALYSIS.get("t")
    return None if t is None else time.monotonic() - t


def run_download(ydl, yt_dlp, info, link, fmt_id):
    """Descarga con el MISMO análisis que vio el usuario (así los format_id coinciden). 1.7.3: si ese análisis ya es viejo (las URLs caducan; con DLPY_SCENE_RHYTHM=wait
    pasa tiempo entre analizar y bajar) se reanaliza antes de empezar."""
    import copy

    def clone():
        try:
            return copy.deepcopy(info)
        except Exception as _ign:
            ignore("clone", _ign)
            return dict(info)

    age = analysis_age()
    stale = INFO_TTL > 0 and age is not None and age > INFO_TTL
    if stale:
        dbg("análisis viejo", f"{age:.0f} s > {INFO_TTL:.0f} s: se reanaliza antes de descargar")
    else:
        try:
            res = ydl.process_ie_result(clone(), download=True)
            if _dl_ok(res):
                return res
            # 1.7.1: antes se daba por buena y salía «No se encontró el archivo»
            dbg("sin archivo con el análisis previo", "yt-dlp devolvió sin error y sin archivo")
        except yt_dlp.utils.DownloadError as e:
            dbg("fallo con el análisis previo", str(e))
            if not _RETRY_RE.search(str(e).lower()):
                raise
    b = RUNTIME["bar"]
    if b is not None and b.th:
        b.reset("Reanalizando el enlace")      # dentro del panel: imprimir encima de él lo dejaba pegado
    else:
        m_info("Reanalizando el enlace...")
    for attempt in (1, 2):
        try:
            res = ydl.extract_info(link, download=True)
            if _dl_ok(res):
                return res
            dbg("sin archivo tras reanalizar", "yt-dlp devolvió sin error y sin archivo")
            break
        except yt_dlp.utils.DownloadError as e:
            dbg("fallo tras reanalizar", str(e))
            low = str(e).lower()
            if "not available" in low:
                break
            # 1.7.3: la URL recién obtenida también dio 403 / 410: un último intento tras una pausa corta
            if attempt == 1 and _RETRY_RE.search(low):
                time.sleep(RETRY_PAUSE)
                continue
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
# más formatos que esto: la lista completa NO va en el JSON (se ve en el script con v=more)
SC_ALL_MAX = 40
SC_MORE_IDS = ("more", "all", "todos", "ver_todos")    # lo que devuelve el atajo (v=…) al elegir «Ver todos»
SC_URL_MAX = 30000                     # largo máximo de la URL shortcuts://; si pasa, el JSON va por el portapapeles
SC_TIMEOUT = _env_num("DLPY_SHORTCUT_ANALYZE_TIMEOUT_SECS", 90.0)     # tope del análisis para el atajo (s; 0 = sin tope)
# --scm corre en «Ejecutar comando» de a-Shell EN EXTENSIÓN y Atajos la corta a ~10 s (medido): el análisis
# tiene que responder antes. Se cuenta desde que arrancó el script (BOOT_T0, justo tras los imports); si no alcanza,
# devuelve «timeout». 1.2.1: tope de 7 s (antes 5) y la espera final se acorta para que el proceso termine antes de
# SCM_HARD (así Atajos recibe siempre el JSON y no el corte de ~10 s).
SCM_TIMEOUT = _env_num("DLPY_SHORTCUT_MODE_TIMEOUT_SECS", 5.0)          # 1.2.7: 5 s (antes 7)
# s (desde BOOT_T0) a los que el proceso debería haber terminado; 0 = sin tope.
SCM_HARD = _env_num("DLPY_SHORTCUT_MODE_HARD_TIMEOUT_SECS", 8.0)
# OJO: BOOT_T0 va tras compilar el script (~1 s en iPhone, no se cuenta): 8,0 aquí ≈ 9 s reales frente al corte de ~10 s de Atajos
SCM = {"on": False, "abort": threading.Event(), "thread": None}     # estado de --scm
# s que se espera (como máximo) a que el hilo de análisis termine solo tras un timeout
SCM_UNWIND = 2.0
# 1.2.1: segundos por fase (boot, prep, imp, opts, net, ff, build, total): va en el JSON («timing»)
SC_TIMING = {}
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
APPLE_MARK_UNSURE = APPLE_MARK + "?"   # 1.6.9: códec sin determinar (normalmente nativo de Apple, sin comprobar)


# 1.9.9: la lista de terminal (--scb/--scm incluidas) muestra la misma manzana que el JSON del atajo: «» compatible, «?» códec sin comprobar (una sola columna)
FLAG_MARKS["logo"], FLAG_COLORS["logo"], FLAG_TEXT["logo"] = APPLE_MARK, "mint", FLAG_TEXT["apple"]
FLAG_MARKS["logo?"], FLAG_COLORS["logo?"], FLAG_TEXT["logo?"] = APPLE_MARK_UNSURE, "amber", FLAG_TEXT["apple"]


def apple_row_mark(r):
    """1.9.9: la marca de manzana de una fila de la lista: compatible (), sin comprobar (?) o vacía."""
    return flag_mark("logo?") if "unsure" in r["flags"] else flag_mark("logo") if "apple" in r["flags"] else ""


def apple_col_width(rows):
    """1.9.9: ancho de la columna de manzana: 2 si alguna fila lleva «?», 1 si no."""
    return 2 if any("unsure" in r["flags"] for r in rows) else 1


def apple_tag(f, ok):
    """Manzana (compatible, `ok`), manzana con ? (códec sin determinar) o nada; con espacio delante si hay marca."""
    return " " + (APPLE_MARK_UNSURE if apple_unsure(f) else APPLE_MARK) if (ok or apple_unsure(f)) else ""


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
    # 1.7.0
    return lead + (t_display(" · original") if t["original"] else "") + f" · {tech}" + apple_tag(f, apple_audio(f))


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
        # 1.7.0: "audio" no está en catálogo, queda tal cual en en
        parts = [("★ " if is_best else "") + (lang or t_display("audio")), tech, size_t]
        orig = f.get("format_id") in orig_ids
        if orig:
            parts.insert(2, t_display("original"))
        label = f"{n} · " + " · ".join(p for p in parts if p) + apple_tag(f, apple_audio(f))
        out.append({"n": n, "id": str(f.get("format_id")), "label": label, "lang": lang or None,
                    "ext": f.get("ext"), "codec": acodec_short(f),
                    "abr": round(abr) if abr else None, "size_bytes": size, "size": human_size(size) if size else None,
                    "size_est": None if size else size_t, "original": orig, "compatible": bool(apple_audio(f)),
                    "unsure": apple_unsure(f), "best": is_best})
    return out


def shortcut_error(code, msg, link=None, elapsed=None):
    msg = t_display(msg)  # 1.7.0: el JSON del atajo sale traducido
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
    """«1920p vp09», «1 mp4 con audio» (sin resolución: el id de yt-dlp tal cual): resolución/etiqueta + códec (o contenedor si no hay códec)."""
    name = shortcut_video_name(f)
    vc = str(f.get("vcodec") or "unknown").split(".")[0]
    if vc.lower() in ("unknown", "?", "none", ""):
        return f"{name} {f.get('ext') or '?'}" + (tr_fragment(" con audio") if has(f.get("acodec")) else "")  # 1.7.0
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
                   else (f"{f.get('ext') or '?'} · {t('con audio')}" if has_a else (f.get("ext") or "?"))),
        "k": k_label(f), "range": range_label(f) or None, "hdr": detect_hdr(f), "size_bytes": size,
        "size": human_size(size) if size else None, "compatible": bool(apple_video(f)),
        "unsure": apple_unsure(f), "kbps": round(kbps) if kbps else None,
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
        "unsure": apple_unsure(av) or (aa is not None and apple_unsure(aa)),
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
        # 1.7.0 "height": None, "fps": None, "ext": None, "vcodec": None,
        "id": "audio", "name": t_display("Solo audio"),
        "range": None, "hdr": None, "size_bytes": None, "size": None,
        "compatible": _ap_ok, "unsure": _ap is not None and apple_unsure(_ap), "audio": "only",
        "audio_step": "track" if multi_lang else "none", "best": bk == "a",
        "have": got_audio, "detail": solo_audio or None})
    if not _same:                      # el mejor no es el compatible con Apple: opción aparte (se pregunta convertir)
        items.append({
            # 1.7.0 "height": None, "fps": None, "ext": None,
            "id": "audio_best", "name": t_display("Solo audio (mejor)"),
            "vcodec": None, "range": None, "hdr": None, "size_bytes": None, "size": None,
            "compatible": bool(apple_audio(_ba)), "unsure": apple_unsure(_ba), "audio": "only",
            "audio_step": "track" if multi_lang else "none", "best": False, "ask_convert": True,
            "have": False, "detail": audio_desc(_ba)})
    return items, extras_error


def _sc_menu_label(n, it, v_items, audio_is_best):
    """Texto del menú de Atajos para la opción `it` (número, nombre y marcas 🔊 🔇 Apple ✅)."""
    # emojis en color (el menú de Atajos es texto plano, pero los emojis sí se ven en color)
    marks = ((" 🔊" if it.get("audio") == "included" else " 🔇" if it.get("audio") == "none" else "")
             + (f" {APPLE_MARK_UNSURE}" if it.get("unsure") else f" {APPLE_MARK}" if it.get("compatible") else "")
             + (" ✅" if it.get("have") else ""))
    if it["id"] in ("audio", "audio_best"):
        two = any(o["id"] == "audio_best" for o in v_items)      # hay dos: Apple y mejor
        head = (t_display("Solo audio · Apple") if it["id"] == "audio" else t_display("★ Solo audio · mejor")) if two else (
            t_display("★ Solo audio · mejor") if audio_is_best else t_display("Solo audio"))  # 1.7.0
        return f"{n} · ♫ {head}" + (f" · {it['detail']}" if it.get("detail") else "") + marks
    if it["id"] == "ytdlp":
        same = next((o["n"] for o in v_items if o.get("n") and o["id"] == it["auto"]["video_id"]), None)
        return f"{n} · yt-dlp auto · {it['vcodec']}" + (f" (= {same})" if same else "") + marks
    vc = str(it["vcodec"] or "")
    # el emoji 🔊 ya marca audio; quitar el sufijo «· con audio» (idioma activo o español)
    vc = re.sub(r"\s*·\s*(?:" + re.escape(t("con audio")) + r"|con audio)$", "", vc)
    # 1.7.0: la etiqueta del menú se traduce al final de _sc_menu_label
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
                        "label": f"{n} · {t_display(shortcut_track_name(t))}" + (" ✅" if got else ""),  # 1.7.0
                        "format_id": str(f.get("format_id")), "ext": f.get("ext"),
                        "codec": acodec_short(f),
                        "abr": round(abr_of(f)) if abr_of(f) else None,
                        "original": bool(t["original"]), "compatible": bool(apple_audio(f)), "unsure": apple_unsure(f)})
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
        # 1.7.0: menú del atajo traducido (ids intactos)
        it["label"] = t_display(_sc_menu_label(n, it, items, audio_is_best))


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
    # 1.7.0 "height": None, "fps": None, "ext": None, "vcodec": None,
    v_items.append({"id": "more", "name": t_display("Ver todos"),
                    "range": None, "hdr": None, "size_bytes": None, "size": None, "compatible": False, "unsure": False,
                    "audio": "none", "audio_step": "none", "best": False, "have": False, "more": True,
                    "n": n_more, "label": f"{n_more} \u00b7 \u25b8 {t_display('Ver todos')} (+{more_n})"})  # 1.7.0
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
        # 1.7.0 (shortcut_error ya traduce)
        return shortcut_error("no_formats", t_display("No se encontraron formatos."), link)
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
        "more_label": f"\u25b8 {t_display('Ver todos')} (+{more_n})" if more_n > 0 else None,  # 1.7.0
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
                       + t_display(" (con v=audio, a=<audio_ids[n]> elige ese audio exacto; v=more abre la lista completa)"),  # 1.7.0
        "pick_example": _sc_pick_example(v_items, t_items, multi_lang)}


def _sc_prepare(box):
    """1.2.1:"""
    t0 = time.time()
    with quiet("_sc_prepare argv"):
        box["argv"] = user_argv()
    # 1.6.0: --scm ya no lee índice ni historial: solo genera el JSON con lo que dice yt-dlp
    _sc_add("prep", time.time() - t0)


# 1.6.0: no vienen de yt-dlp
SCM_DROP_KEYS = ("already_downloaded", "downloaded", "pick_format", "pick_example", "stage")


def slim_scm(data):
    """1.6.0: el JSON de --scm solo lleva lo que dice yt-dlp y lo que el atajo necesita para elegir (videos, pistas de idioma, extras, audios,
    «Ver todos»). Fuera: lo de descargas previas, las marcas «have» y los textos de ayuda del script."""
    for k in SCM_DROP_KEYS:
        data.pop(k, None)
    for lst in ("videos", "all_videos", "audios", "tracks"):
        for it in data.get(lst) or []:
            if isinstance(it, dict):
                it.pop("have", None)
    return data


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
        net_wrap_ytdlp(yt_dlp)                  # 1.8.8: el icono de red de la franja
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
    # 1.6.0: --scm no revisa si ya existe un archivo: nada de índice ni historial
    if SCM["on"]:
        old_file, old_entry, hist_ = None, None, []
    else:
        idx = load_json(INDEX_FILE)
        old_file, old_entry = lookup_downloaded(idx, key)
        hist_ = history_for(key, idx, None)
    # casi siempre ya terminó; si no, el respaldo es el mismo de ffmpeg_available
    fth.join(3.0)
    can_merge = ff["ok"] if "ok" in ff else bool(shutil.which("ffmpeg"))
    data = build_shortcut_payload(info, link, can_merge, old_file, old_entry, hist_)
    with quiet("shortcut_remember"):
        # 1.5.4: la lista del JSON se guarda: si el id cambia en la descarga, se conserva la calidad
        shortcut_remember(key, data)
    _sc_add("build", time.time() - _t_b)
    data["stage"] = ANALYSIS["stage"]
    if SCM["on"]:
        slim_scm(data)
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
            json.dump(json_clean(data), fh, ensure_ascii=False, indent=2)


def shortcut_mode(flags, pos):
    """`--scm LINK`:"""
    link = pos[0] if pos else None
    if sc_list_mode():                          # 1.9.9: DLPY_SHORTCUT_DIRECT_LIST_MODE: nada que analizar aquí; el atajo sigue con --scb
        sys.stdout.write(json.dumps(sc_list_scm_json(link), ensure_ascii=True, separators=(",", ":")) + "\n")
        sys.stdout.flush()
        return 0
    real_out, real_err = sys.stdout, sys.stderr
    sink = open(os.devnull, "w", encoding="utf-8")
    sys.stdout = sys.stderr = sink              # mensajes internos, yt-dlp, avisos: nada ensucia la salida
    SCM["on"] = True
    # desde los imports hasta aquí (definiciones, dlpy_config.json…)
    SC_TIMING["boot"] = round(time.time() - BOOT_T0, 2)
    data = None
    try:
        left = max(1.0, SCM_TIMEOUT - (time.time() - BOOT_T0)) if SCM_TIMEOUT > 0 else None
        data = collect_with_timeout(link, secs=left)
        if data and data.get("error_code") == "timeout":
            data["use_scb"] = True              # el atajo debe seguir con --scb (sin tope de tiempo)
            data["error"] = t_display("El análisis tardó demasiado para --scm; usa --scb.")  # 1.7.0
    except KeyboardInterrupt:
        data = shortcut_error("cancelled", "Cancelado.", link)
    except BaseException as e:
        data = shortcut_error("crash", f"{type(e).__name__}: {e}", link)
    finally:
        sys.stdout, sys.stderr = real_out, real_err
        if data_is_final(data):
            sink.close()                        # con «timeout» el hilo sigue vivo y podría escribir
    # 1.2.1: dónde se fue el tiempo (y, si hubo timeout, en qué fase se quedó)
    if isinstance(data, dict):
        SC_TIMING["total"] = round(time.time() - BOOT_T0, 2)
        data["timing"] = dict(SC_TIMING)
        if not data_is_final(data):
            data["phase"] = SC_PHASE[0]
    text = json.dumps(json_clean(data), ensure_ascii=True, separators=(",", ":"))
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
    # salvo con DLPY_DEBUG_LOGGING o DLPY_SHORTCUT_SAVE_ANALYSIS_JSON=1 (y entonces va DESPUÉS de imprimir, no antes)
    if DEBUG or _flag_env("DLPY_SHORTCUT_SAVE_ANALYSIS_JSON", False):
        write_shortcut_json(data)
    return 0


def data_is_final(data):
    return bool(data) and data.get("error_code") != "timeout"


def shortcut_send(data, name=None):
    """Abre shortcuts://run-shortcut?name=… con el JSON como entrada (sin «videos», «tracks»"""
    name = name or SHORTCUT_NAME
    slim = {k: v for k, v in data.items() if k not in ("videos", "tracks", "audios", "all_videos")}
    text = json.dumps(json_clean(slim), ensure_ascii=True, separators=(",", ":"))
    url = ("shortcuts://run-shortcut?name=" + urllib.parse.quote(name)
           + "&input=text&text=" + urllib.parse.quote(text, safe=""))
    how = "url"
    if len(url) > SC_URL_MAX and shortcut_copy(text):
        url, how = shortcut_clip_url(name), "portapapeles"
    dbg("scb", {"via": how, "bytes": len(text), "url": url[:80]})
    sh_run("open " + shlex.quote(url))
    return how


SCB_NOTES = ("El análisis rápido se quedó sin tiempo", "Seguimos sin límite de tiempo", "Analizando enlace · puede tardar más")


def scb_clear():
    """--scb nunca usa native_clear (la consola es del atajo): borra con la secuencia directa."""
    with quiet("scb_clear"):
        if sys.stdout.isatty():
            # 1.3.2: el historial solo con DLPY_CLEAR_PURGE_SCROLLBACK=1 · 1.0.1: sin «ESC c» (reinicio total): en a-Shell dejaba la consola en negro
            sys.stdout.write(RESET + "\x1b[2J" + PURGE_SEQ + "\x1b[H" + CURSOR_SHOW)
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
            json.dump(json_clean(data), fh, ensure_ascii=False, indent=1, default=str)


def scb_first_updates():
    """1.8.0: --scb, con la escena ya viva: lo primero es D L P Y buscando actualizaciones (DLpy, pip, yt-dlp) y, si hay un DLpy más nuevo, instalarlo y correr ya
    la versión nueva (que repite este arranque y sigue con normalidad). Sin escena, o con --noupdates, no hace nada (como antes de 1.8.0). Nunca rompe --scb:
    cualquier fallo se anota y el análisis sigue. True si corrió."""
    if not updates_first():
        return False
    try:
        # _m_prepare no corre en --scb: las carpetas que usan las comprobaciones se crean aquí
        ensure_dirs()
        update_phase()
        return True
    except KeyboardInterrupt:
        return False
    except Exception as _ign:
        ignore("scb_first_updates", _ign)
        return False


def scb_scene_start(link):
    """Arranca la escena de --scb con el aviso en palabras sencillas."""
    try:
        if not link:
            return False
        from types import SimpleNamespace
        run = SimpleNamespace(link=str(link), info={}, spick=None)
        started, tries = False, 0
        # desde Atajos la ventana mide 53x0 los primeros ~2 s: se espera y se reintenta
        for tries in (1, 2):
            wait_terminal_ready(timeout=3.0, force=True)
            if ux_start(run):
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
        ux_lang_pick()                          # 1.7.1: DLPY_LANGUAGE=ask: el idioma se pregunta antes de los avisos
        # 1.8.0: D L P Y busca actualizaciones primero (si hay un DLpy nuevo, lo instala y corre ya)
        scb_first_updates()
        ux_note(SCB_NOTES[0], hold=SCENE_DWELL + 0.5)
        ux_note(SCB_NOTES[1], hold=SCENE_DWELL + 0.3)
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
            # 1.3.3: la escena cuenta cómo salió (✓ / ✗) antes de seguir con el análisis
            if scene:
                ux_note(f"yt-dlp {pkg_version('yt-dlp') or ''} · instalado".replace("  ", " ") if is_installed("yt_dlp", fresh=True)
                           else "No se pudo instalar yt-dlp", SCENE_DWELL)
    try:
        if scene:
            ux_note(SCB_NOTES[2])
        data = collect_with_timeout(link)
    except KeyboardInterrupt:
        data = shortcut_error("cancelled", "Cancelado.", link)
    write_shortcut_json(data)
    CLEAN_LATE["on"] = True
    # hay algo que preguntar (archivos viejos): la escena cede (1.1.5: ya no; la limpieza corre en la escena)
    if ux_on() and ux_questions():
        ux_stop()
        scb_clear()
    with quiet("shortcut_back"):
        clean_old()                             # al final del trabajo, antes de pasar al atajo
    if scene:
        scb_diag(scene=True, scene_alive=bool(ux_get("th") is not None and ux_get("th").is_alive()), scene_error=ux_get("err"),
                 json_ok=bool(data and data.get("ok", True)))
    # 1.0.8: el análisis falló: se indica en D L P Y
    if scene and ux_on() and isinstance(data, dict) and data.get("ok") is False:
        log_shortcutmode_error(f"{data.get('error_code') or 'error'}: {data.get('error') or ''}")
        ux_set_error(data.get("error") or "Error")
    # «Enviando a DLpy» (o el error en D L P Y) y la escena se cierra hacia el centro
    if ux_end():
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
# 2.0.2: las pruebas (funciones _st_t*, SELFTEST_GROUPS y selftest_run) viven en modules/dlpy_selftest.py y se cargan solo con --selftest.
# El módulo se ejecuta con exec dentro del espacio de nombres de este archivo (mismas variables y funciones, sin cambiar las pruebas).
SELFTEST_MODULE, SELFTEST_REMOTE_DIR = "dlpy_selftest.py", "modules"


def selftest_dir():
    """Carpeta caché del módulo: DLPY_SELFTEST_MODULES_DIR (pruebas) o internal/modules."""
    return env_get("DLPY_SELFTEST_MODULES_DIR") or os.path.join(INTERNAL_DIR, "modules")


def selftest_url(name):
    """URL fija en la carpeta modules/ de main (como languages/); no depende de VERSION."""
    repo = str(globals().get("UPDATE_REPO") or "ElDelDLpy/DLpy").strip().strip("/")
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
        return None
    return "https://raw.githubusercontent.com/%s/%s/%s/%s" % (repo, urllib.parse.quote(LANG_BRANCH, safe=""), SELFTEST_REMOTE_DIR, name)


def selftest_module_text():
    """(texto, origen) del módulo de la autoprueba o (None, motivo). Orden: DLPY_SELFTEST_MODULE_FILE, junto a este archivo (modules/), caché verificada y, al final, descarga de main con SHA-256."""
    import hashlib
    local = [env_get("DLPY_SELFTEST_MODULE_FILE") or "",
             os.path.join(os.path.dirname(os.path.abspath(__file__)), SELFTEST_REMOTE_DIR, SELFTEST_MODULE),
             os.path.join(selftest_dir(), SELFTEST_MODULE)]
    for path in local:
        if path and os.path.isfile(path):
            try:
                with open(path, "rb") as fh:
                    raw = fh.read()
            except OSError as _ign:
                ignore("selftest_module_text", _ign)
                continue
            if path == local[2]:                           # la caché solo vale con su hash
                try:
                    want = _lang_pack_sha_value(read_text(path + ".sha256"), SELFTEST_MODULE)
                except OSError as _ign:
                    ignore("selftest_module_text", _ign)
                    want = None
                if want != hashlib.sha256(raw).hexdigest():
                    continue
            return raw.decode("utf-8"), path
    url, sums = selftest_url(SELFTEST_MODULE), selftest_url(LANG_SUMS)
    if not url or not sums:
        return None, "repo"
    try:
        expected = _lang_pack_sha_value(fresh_bytes(sums, 8, limit=4096), SELFTEST_MODULE)
        raw = fresh_bytes(url, 8)
    except NET_ERRORS as _ign:
        ignore("selftest_module_text", _ign)
        return None, "red"
    if raw is None:
        return None, "red"
    if not expected or hashlib.sha256(raw).hexdigest() != expected:
        return None, "sha"
    path = os.path.join(selftest_dir(), SELFTEST_MODULE)
    try:
        write_text(path, raw.decode("utf-8"), mkdir=True)
        write_text(path + ".sha256", "%s  %s\n" % (expected, SELFTEST_MODULE))
    except (OSError, ValueError) as _ign:
        ignore("selftest_module_text", _ign)
    return raw.decode("utf-8"), url


def selftest():
    """`python dlpy.py --selftest`: carga modules/dlpy_selftest.py (verificado) y corre las pruebas."""
    text, origin = selftest_module_text()
    if text is None:
        print("Autoprueba: no se pudo obtener %s/%s (%s). Pon el archivo junto a dlpy.py o revisa la red." % (SELFTEST_REMOTE_DIR, SELFTEST_MODULE, origin))
        return 1
    found = re.search(r'(?m)^SELFTEST_FOR = "([^"]*)"', text)
    if not found or found.group(1) != VERSION:
        print("Autoprueba: el módulo es de la versión %s y dlpy.py es la %s; no se ejecuta." % (found.group(1) if found else "?", VERSION))
        return 1
    exec(compile(text, origin, "exec"), globals())
    return globals()["selftest_run"]()



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
        "(sin pérdida con x265 o Kvazaar si ffmpeg lo trae (8 bits en Kvazaar); si no, VideoToolbox o libx264; DLPY_CONVERT_PRESET lo cambia).")
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
        add("Ofrecer el enlace del portapapeles", "ok", "Con «pbpaste» (DLPY_CLIPBOARD_READ_LINK_ENABLED=1).")
    else:
        add("Ofrecer el enlace del portapapeles", "na",
            "Desactivado a propósito: iOS pregunta «¿Permitir pegar?» en cada lectura. "
            "Actívalo con DLPY_CLIPBOARD_READ_LINK_ENABLED=1.")
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



def config_validate(name, value):
    """1.8.4: (ok, normalized|None). ok=False → valor inválido (en runtime se usa el predeterminado)."""
    v = str(value if value is not None else "").strip()
    n = config_canonical(name) or str(name or "")
    if v == "":
        return True, ""
    low = v.lower()

    def flag01():
        if low in ("0", "1"):
            return True, low
        if low in ("on", "yes", "true", "si", "sí"):
            return True, "1"
        if low in ("off", "no", "false"):
            return True, "0"
        return False, None

    def num(min_v=None, max_v=None, allow_float=True):
        try:
            x = float(v.replace(",", ".")) if allow_float else float(int(v))
        except Exception:
            return False, None
        if not math.isfinite(x):
            return False, None
        if min_v is not None and x < min_v:
            return False, None
        if max_v is not None and x > max_v:
            return False, None
        if allow_float and ("." in v or "," in v):
            s = ("%g" % x)
        else:
            s = str(int(x)) if x == int(x) else ("%g" % x)
        return True, s

    if n in ("DLPY_DEBUG_LOGGING", "DLPY_COLOR_TRUECOLOR", "DLPY_ANIMATIONS_ENABLED", "DLPY_PROGRESS_BAR_CLASSIC", "DLPY_ANALYZE_ANIMATION_ENABLED",
             "DLPY_PIP_USES_SCENE", "DLPY_GLITCH_EFFECT_ENABLED", "DLPY_TEXT_CALM_MODE", "DLPY_CONVERT_LIGHT_ANIMATION", "DLPY_HIDE_SCRIPT_FILES",
             "DLPY_CLEAR_PURGE_SCROLLBACK", "DLPY_SCENE_OUTRO_ENABLED", "DLPY_CLIPBOARD_READ_LINK_ENABLED", "DLPY_SINGLE_INSTANCE_WATCHDOG", "DLPY_MEDIA_TAGS_ENABLED"):
        return flag01()
    if n == "DLPY_CONCURRENT_FRAGMENTS":
        return num(1, 16, allow_float=False)
    if n == "DLPY_SUBTITLE_LANGS":
        return (True, "0") if low in ("0", "no", "off", "") else ((True, "all") if low == "all" else (bool(subs_langs(low)), ",".join(subs_langs(low))))
    if n == "DLPY_SCENE_RHYTHM":
        if low in ("wait", "real", "loop"):
            return True, "wait" if low == "loop" else low
        ok, s = num(0, 60)
        return ok, s
    if n == "DLPY_ANIMATION_LOOP_SECS":
        return num(0.2, 3)
    if n == "DLPY_ANALYZE_RESULT_TTL_SECS":
        return num(0, 86400)
    if n == "DLPY_DEBUG_LOG_KEEP_COUNT":
        return num(1, 1000, allow_float=False)
    if n == "DLPY_UI_LINES":
        return num(0, 200, allow_float=False)
    if n == "DLPY_TERMINAL_WIDTH_COLS":
        if low == "auto":
            return True, "auto"
        return num(20, 500, allow_float=False)
    if n == "DLPY_LIST_VISIBLE_ROWS":
        if low == "auto":
            return True, "auto"
        return num(1, 200, allow_float=False)
    if n == "DLPY_CONVERT_PRESET":
        if low in ("fast", "high", "best", "prores"):
            return True, low
        return False, None
    if n == "DLPY_SHORTCUT_DIRECT_LIST_MODE":
        mode_ = sc_list_mode(v)
        if low in ("0", "off", "no", "false", "none"):
            return True, "0"
        return (True, {"short": "1", "all": "all"}[mode_]) if mode_ else (False, None)
    if n == "DLPY_FINISH_DELIVERY_MODE":
        if low in ("view", "shortcut"):
            return True, low
        return False, None
    if n in ("DLPY_CLEAR_MODE", "DLPY_CLEAR_FIRST_MODE"):
        if low in ("auto", "home", "down", "purge-first", "reset"):
            return True, low
        return False, None
    if n == "DLPY_TOP_BAR_FIELDS":
        if low in ("0", "off", "no", "false", "none", "oculto", "hide", "hidden"):
            return True, "0"
        if low in ("1", "on", "yes", "true", "all", "si", "sí"):
            return True, "1"
        letters = [c for c in v.upper() if c in "DTV"]
        if letters and all(c in "DTV, ·|_-;" for c in v.upper()):
            # unique order
            seen = []
            for c in v.upper():
                if c in "DTV" and c not in seen:
                    seen.append(c)
            return True, "".join(seen)
        return False, None
    if n == "DLPY_BOTTOM_BAR_FIELDS":
        if low in ("0", "off", "no", "false", "none", "oculto", "hide", "hidden"):
            return True, "0"
        if low in ("1", "on", "yes", "true", "all", "si", "sí"):
            return True, "1"
        if any(c in "EAN" for c in v.upper()) and all(c in "EAN, ·|_-;" for c in v.upper()):
            seen = []
            for c in v.upper():
                if c in "EAN" and c not in seen:
                    seen.append(c)
            return True, "".join(seen)
        return False, None
    if n == "DLPY_TRANSLATION_DEBUG_MODE":
        mode = lang_id_mode_parse(v)
        if mode == "off":
            return (True, "0") if low in ("0", "off", "no", "false", "none", "disabled", "") else (False, None)
        return True, mode
    if n == "DLPY_LANGUAGE":
        if low in ("ask", "auto", "es", "en", "pt", "fr", "de", "it", "ru", "zh", "hi", "ar", "ja", "ko", "pl"):
            return True, low
        # aliases handled at runtime; accept non-empty short tokens
        if 1 <= len(v) <= 16:
            return True, v
        return False, None
    if n == "DLPY_UPDATE_CHECK_INTERVAL":
        hrs = updates_parse_hours(v)
        if hrs is None:
            return False, None
        if hrs < 0:
            return True, "on"
        if hrs == 0:
            return True, "0"
        return True, re.sub(r"\s+", "", low.replace(",", "."))
    if n in ("DLPY_STORAGE_LIMIT_MB", "DLPY_SHORTCUT_ANALYZE_TIMEOUT_SECS", "DLPY_SHORTCUT_MODE_TIMEOUT_SECS", "DLPY_SHORTCUT_MODE_HARD_TIMEOUT_SECS"):
        return num(0, 10_000_000)
    if n in ("DLPY_UPDATE_REPO", "DLPY_YTDLP_EXTRA_ARGS"):
        return True, v
    return True, v


def config_aliases_selftest():
    """2.0.9: comprobaciones de renombre para el módulo de selftest (modules/dlpy_selftest.py): (nombre, ok, detalle). El módulo externo debe llamar a esta función."""
    checks = []
    for old, new in sorted(CONFIG_ALIASES.items()):
        checks.append((f"alias {old} -> {new}", config_canonical(old) == new, f"{old} -> {config_canonical(old)}"))
        checks.append((f"alias {new} estable", config_canonical(new) == new, new))
    for bare, want in (("lang", "DLPY_LANGUAGE"), ("rows", "DLPY_LIST_VISIBLE_ROWS"), ("ux", "DLPY_SCENE_RHYTHM"),
                       ("language", "DLPY_LANGUAGE"), ("list_visible_rows", "DLPY_LIST_VISIBLE_ROWS")):
        checks.append((f"config_key sin prefijo {bare}", config_key(bare) == want, f"{bare} -> {config_key(bare)}"))
    for old, new in (("DLPY_NO_UPDATE", "DLPY_UPDATE_CHECK_INTERVAL"), ("DLPY_CHECK_HOURS", "DLPY_UPDATE_CHECK_INTERVAL"),
                     ("DLPY_SCENE_MODE", "DLPY_SCENE_RHYTHM")):
        checks.append((f"legado {old} -> {new}", config_canonical(old) == new, f"{old} -> {config_canonical(old)}"))
    checks.append(("migración NO_UPDATE", config_migrate_value("DLPY_NO_UPDATE", "1") == ("DLPY_UPDATE_CHECK_INTERVAL", "0"), str(config_migrate_value("DLPY_NO_UPDATE", "1"))))
    checks.append(("migración CHECK_HOURS", config_migrate_value("DLPY_CHECK_HOURS", "48") == ("DLPY_UPDATE_CHECK_INTERVAL", "48h"), str(config_migrate_value("DLPY_CHECK_HOURS", "48"))))
    checks.append(("migración SCENE_MODE loop", config_migrate_value("DLPY_SCENE_MODE", "loop") == ("DLPY_SCENE_RHYTHM", "wait"), str(config_migrate_value("DLPY_SCENE_MODE", "loop"))))
    checks.append(("I18N_CONFIG cubre descripciones", all(t in (I18N_CONFIG.get("es") or {}) for _n, _d, t in CONFIG_OPTIONS), "todas las descripciones en I18N_CONFIG"))
    checks.append(("sin DLPY_ interno en constantes", "DLPY_TYPE_AT" not in globals() and "DLPY_FPS" not in globals(), "TYPE_* / SCENE_FPS sin prefijo"))
    return checks


def config_mark(name, default, val):
    """1.8.4: símbolo de estado · ● guardada válida · ✗ guardada inválida · espacio = predeterminado."""
    if val is None:
        return " "
    ok, _ = config_validate(name, val)
    return "✗" if not ok else "●"


def config_rows(data):
    """1.3.2:"""
    rows = [(n, d, t, data.get(n)) for n, d, t in CONFIG_OPTIONS]
    known = {n for n, _d, _t in CONFIG_OPTIONS}
    rows += [(k, "", "variable guardada que no está en la lista de opciones conocidas", data[k]) for k in sorted(data) if k not in known]  # 2.0.9: msgid en I18N_CONFIG, se traduce con note()
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


def config_list_rows(rows):
    """2.0.0: filas de la lista de --config en el formato de print_rows: «nº NOMBRE valor» y a la derecha ● guardada · ✗ guardada pero inválida ([predeterminado] si no hay guardada)."""
    out = []
    for i, (name, default, _text, val) in enumerate(rows, 1):
        mark, dflt = config_mark(name, default, val), f"[{default or '—'}]"
        out.append({"n": i, "flags": {"saved"} if mark == "●" else {"bad"} if mark == "✗" else set(),
                    "cols": [name, dflt if val is None else f"{val} → {dflt}" if mark == "✗" else val]})
    return out


def config_show_list(rows):
    """1.3.2 / 1.8.4 / 2.0.0: la lista de --config con el dibujo único de las listas (print_rows)."""
    print_rows(config_list_rows(rows), [("saved", "bad")], clip=1)


def config_redraw(msg=None):
    """1.8.4: limpia la terminal y pinta de nuevo archivo + lista + ayuda (menú config legible al cambiar varias)."""
    try:
        # 1.9.3: ya usa la limpieza sin parpadeo (antes llamaba a una función inexistente)
        clear_screen()
    except Exception:
        print("\n" * 3)
    print(title_bar(f"DLpy v{VERSION}", paint("config", "gray")))
    print(rule())
    kv("Archivo", ENV_FILE)
    if msg:
        print()
        note(msg)
    print()
    legend_note("● guardada  ·  ✗ guardada inválida (se usa el predeterminado)  ·  [ ] predeterminado")
    config_show_list(config_rows(_read_env_json(ENV_FILE)))
    print()
    note("Nº o nombre: elegir · NOMBRE=valor: guardar · l: lista · o: olvidar todas · Enter: salir")


def config_interactive():
    """1.3.2 / 1.8.4: menú con redibujado al cambiar; la lista muestra ●/✗ al momento."""
    rc = 0
    config_redraw()
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
                config_redraw()
                continue
            if act[0] == "forget":
                if ask("¿Borrar todas las variables guardadas?", default=False):
                    had = len(_read_env_json(ENV_FILE))
                    config_write({}, ENV_FILE)
                    hide_files_after_config()
                    config_redraw(f"Configuración borrada ({had} guardada(s))")
                else:
                    config_redraw()
                continue
            item = act[1]
            if act[0] == "pick":
                _n, default, text, val = next(r for r in rows if r[0] == act[1])
                try:
                    clear_screen()        # 1.9.3: antes llamaba a una función inexistente
                except Exception as _ign:
                    ignore('config: limpiar pantalla', _ign)
                print(title_bar(f"DLpy v{VERSION}", paint("config", "gray")))
                print(rule())
                print(paint("·", "orange") + paint(act[1], "white", True))
                note(text)
                _old_pick = config_old_name(act[1])
                if _old_pick:
                    kv("Nombre anterior", _old_pick)
                mark = config_mark(act[1], default, val)
                if val is None:
                    kv("Guardado", "(ninguno)")
                elif mark == "✗":
                    kv("Guardado", paint(str(val), "red") + paint(" (inválido → predeterminado)", "gray"))
                else:
                    kv("Guardado", val)
                kv("Por omisión", default or "—")
                note("Escribe el valor nuevo · Enter = dejarlo · - = borrar")
                try:
                    new = ask_line(prompt, True, "▸ ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if not new:
                    config_redraw("Sin cambios.")
                    continue
                item = act[1] + "=" + ("" if new == "-" else new)
            changes, errors = config_edit([item], ENV_FILE)
            msg_parts = []
            for key, _old, new_v in changes:
                if new_v is None:
                    msg_parts.append(f"{key} borrada")
                else:
                    ok, _ = config_validate(key, new_v)
                    msg_parts.append(f"{key} = {new_v}" + ("" if ok else " (inválido → se usará el predeterminado)"))
            if not changes and not errors:
                msg_parts.append("Sin cambios.")
            for msg in errors:
                m_err(msg)
                rc = 1
            if changes and any(k == HIDE_FILES_KEY for k, _o, _n in changes):
                hide_files_after_config()
            config_redraw(" · ".join(msg_parts) if msg_parts else None)
        except OSError as e:
            m_err(f"No se pudo guardar en {ENV_FILE}: {e}")
            rc = 1
            config_redraw()
    print()
    note("Listo. Con --config NOMBRE=valor también se guarda sin menú; --config --lista muestra solo lo guardado.")
    return rc


def clear_test():
    """`python dlpy.py --cleartest` (1.3.2):"""
    if not (tty_both()):
        print(t_display("--cleartest necesita un terminal interactivo."))
        return 1
    print(title_bar(f"DLpy v{VERSION}", paint(t_display("prueba de borrado"), "gray")))
    print(rule())
    note("Se llena la pantalla, se borra con cada modo y eliges el que quede limpio sin deslizar.")
    prev, rc, saved = CLEAR_MODE, 0, None
    try:
        for name, text in CLEAR_MODES:
            if ask_line(paint(f"[{name}] ", "orange", True) + paint(t_display("Enter = probar ▸"), "gray"), True, f"[{name}] Enter ▸ ").strip().lower() == "q":
                break
            rows = term_rows()
            for i in range(rows + 8):
                print(t_display(f"Línea de prueba {i + 1}"))
            time.sleep(0.8)
            globals()["CLEAR_MODE"] = name
            native_clear()
            print(paint(t_display(f"Modo {name}"), "white", True))
            note(text)
            yes_key, no_key = _yn_keys()
            question = (t_display("¿Quedó limpia sin deslizar?") + f" {yes_key} = {t_display('guardar')} · "
                        + f"{no_key} = {t_display('siguiente')} · q = {t_display('salir')} ▸ ")
            ans = ask_line(paint(question, "gray"), True, "/".join((yes_key, no_key, "q")) + " ▸ ").strip().lower()
            yn = parse_yn(ans, default=None)
            if yn is True:
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
            config_edit([f"DLPY_CLEAR_MODE={saved}"], ENV_FILE)
            m_ok(f"DLPY_CLEAR_MODE = {saved} (guardado; vale desde el siguiente comando)")
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
        # 1.3.2: «--config» a secas en un terminal = menú interactivo
        return config_interactive()
    try:
        if flags.get("olvidar"):
            had = len(_read_env_json(ENV_FILE))
            config_write({}, ENV_FILE)
            m_ok(f"Configuración borrada ({had} guardada(s))")
        changes, errors = config_edit(items, ENV_FILE)
    except OSError as e:
        m_err(f"No se pudo guardar en {ENV_FILE}: {e}")
        return 1
    for key, _old, new in changes:
        m_ok(f"{key} = {new}" if new is not None else f"{key} borrada")
    for msg in errors:
        m_err(msg)
        rc = 1
    if flags.get("olvidar") or any(k == HIDE_FILES_KEY for k, _o, _n in changes):
        hide_files_after_config()                          # 1.6.5: DLPY_HIDE_SCRIPT_FILES se aplica al instante
    data = _read_env_json(ENV_FILE)
    kv("Archivo", ENV_FILE)
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
            for ln in wrap_text(t_display(text), max(10, term_width() - 6)):
                print("    " + paint(ln, "gray"))
            _old_cfg = config_old_name(name)
            if _old_cfg:
                print("    " + paint(t_display("Antes:") + " " + _old_cfg, "gray"))
    print()
    note("Guardar: --config NOMBRE=valor · borrar una: --config NOMBRE= · borrar todas: --config --olvidar · opciones: --config --opciones")
    note("El nombre puede ir sin DLPY_ (list_visible_rows = DLPY_LIST_VISIBLE_ROWS). Un export manda en esa ejecución y también se guarda. DLPY_IGNORE_SAVED_CONFIG y DLPY_SKIP_SHA_VERIFY son de una sola ejecución.")
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
    if wants_languages(sys.argv[1:]):
        return _end(print_languages())                       # 1.7.0: JSON de idiomas para el atajo (lista de elegir)
    if wants_atajo(sys.argv[1:]):
        return _end(print_atajo())                            # 2.1.0: JSON de textos + idiomas + config para el atajo
    if _wants(sys.argv[1:], "cleartest"):
        return _end(clear_test())                            # 1.3.2: probar los modos de borrado de la consola
    if wants_2shortcuts(sys.argv[1:]):
        return _end(send_code_to_shortcut())
    cli_flags, cli_args = parse_cli(sys.argv[1:])
    if SC_LIST_RUN["on"]:
        dbg("DLPY_SHORTCUT_DIRECT_LIST_MODE", {"modo": sc_list_mode(), "argumentos": sys.argv[1:]})     # 1.9.9: --scb reencaminado a la lista directa
    NO_UPDATES["on"] = bool(cli_flags.get("noupdates") or cli_flags.get("no-updates") or UPDATE_HOURS == 0)
    # 1.8.0: _m_update lo apaga si la escena está viva (las actualizaciones van primero)
    LATE_UPDATES["on"] = cli_flags.get("shortcutpick") is not None and not NO_UPDATES["on"]
    if wants_scb(sys.argv[1:]):
        return _end(shortcut_back(cli_flags, cli_args))   # analiza y avisa al atajo «DLpy» con el JSON
    if wants_scm(sys.argv[1:]):
        return _end(shortcut_mode(cli_flags, cli_args))   # JSON en la salida y nada más
    run.cli_args = cli_args
    # 1.3.4: --view / --view=shortcut|view: el modo de vista solo para esta ejecución
    if cli_flags.get("view") is not None:
        VIEW_RUN["mode"] = "view" if cli_flags["view"] is True else str(cli_flags["view"]).strip().lower() or "view"
    _sp = cli_flags.get("shortcutpick")
    if isinstance(_sp, str) and "://" in _sp and "=" not in _sp.split("://", 1)[0]:
        # el atajo mandó la bandera vacía y Atajos se comió el vacío: eso era el enlace
        cli_args = [_sp] + list(cli_args)
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
    # 0.8.2: con --shortcutpick la intro sale lo primero: consola limpia, sin preguntas antes
    ux_early_site_intro(run)
    # 1.7.1: DLPY_LANGUAGE=ask (predeterminado): la escena pregunta el idioma (solo con escena viva y teclado)
    ux_lang_pick()
    os.makedirs(FILES_DIR, exist_ok=True)
    drop_internal_leftovers()       # resto de un reinicio de .dlpy_internal que se cortó
    os.makedirs(INTERNAL_DIR, exist_ok=True)
    ensure_dirs()
    # 1.9.2: carga el paquete local; la búsqueda/descarga remota la gobierna update_phase con DLPY_UPDATE_CHECK_INTERVAL
    lang_ensure()
    clear_screen()                  # banner arriba, sin restos de la ejecución anterior

    if ENV_STATE["error"]:
        m_warn(f"No se pudieron guardar las variables DLPY_* en {ENV_STATE['path']}")
        note(ENV_STATE["error"])
    with quiet("clean_trash 0.9.9"):
        _gone = clean_trash()       # 0.9.9: trash con >30 días se borra definitivo
        ux_set(trash_gone=_gone)
        if _gone and not ux_on():
            m_ok(f"Papelera: {_gone} archivo(s) borrado(s) definitivamente (más de {TRASH_EXPIRE_DAYS:g} días en ella).")
        if _gone and ux_on():   # 1.1.5: también se anota en la escena (no en el shell)
            ux_set(clean=_gone)
            ux_status(clean_label("Vaciando", None, _gone))
            ux_hold(SCENE_CLEAN_SECS)
    if QUIET["on"]:
        CLEAN_LATE["on"] = True     # 0.8.2: --shortcutpick no pregunta: la limpieza se ofrece al terminar la descarga
    else:
        with quiet("clean_old"):
            clean_old()             # 0.9.9: >10 días -> trash
    check_storage()                 # antes de cualquier otro proceso
    return None


def _debug_environment():
    """Con DLPY_DEBUG_LOGGING: ancho del terminal y datos del entorno."""
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


def updates_first():
    """1.8.0: ¿las actualizaciones van PRIMERO en esta ejecución? Con la escena viva, sí: --shortcutpick y --scb abren D L P Y y buscan DLpy, pip y yt-dlp antes de seguir
    (si hay un DLpy más nuevo, lo instala y corre ya la versión nueva). Sin escena (la terminal no la admite) no hay dónde animar ni preguntar:
    --shortcutpick las deja para el final (LATE_UPDATES) y --scb no las busca. Tampoco con --noupdates / DLPY_UPDATE_CHECK_INTERVAL=0."""
    return ux_on() and not NO_UPDATES["on"]


def update_phase():
    """1.8.0: lo de _m_update tras --actualizar (lo comparten _m_update y --scb): busca DLpy, pip y yt-dlp, instala y corre un DLpy más nuevo
    (reexec_script no vuelve), revisa la versión instalada y las dependencias. Sin escena, las búsquedas salen a la vez (prefetch_phase). Con la escena viva
    van UNA A UNA, cada una con su comando real en D L P Y (GET api.github.com/…/releases, GET pypi.org/pypi/pip/json…), como en 1.7.9: la búsqueda en paralelo
    solo tenía un comando de resumen («GET pypi.org x2 · github.com») que no es lo que el script ejecuta. None si todo siguió bien; 1 si hay que parar."""
    reexec = getattr(sys, "_dlpy_reexec", False)     # recién instalada por la anterior: ya se comprobó
    script_due = (not NO_UPDATES["on"] and not LATE_UPDATES["on"] and not reexec
                  # según DLPY_UPDATE_CHECK_INTERVAL (1.4.4: siempre · cada N días · nunca)
                  and check_due("script", script_sig()))
    deps_due = not NO_UPDATES["on"] and not LATE_UPDATES["on"] and check_due("deps")
    # 1.8.0: con la escena viva NO hay búsqueda en paralelo: cada comprobación teclea su comando real
    if not ux_on():
        prefetch_phase(script_due, deps_due)                       # 1.4.4: DLpy, pip y yt-dlp se comprueban a la vez
    if reexec:
        UPDATE_CHECKED["ok"] = True              # la versión anterior acaba de comprobar y la instaló
    if script_due:
        if check_update():
            return 0
    if not check_version():
        return 1
    if (script_due or reexec) and UPDATE_CHECKED["ok"]:
        check_mark("script", script_sig())
    if not LATE_UPDATES["on"] and LANG in PACK_LANGS:
        lang_pack_sync(LANG)          # 1.9.2: paquetes de idioma usan el mismo calendario DLPY_UPDATE_CHECK_INTERVAL
    if not check_dependencies(updates=not (NO_UPDATES["on"] or LATE_UPDATES["on"])):
        return 1
    prefetch_summary()                                             # 1.4.4: todo al día → una sola línea en la escena
    cleanup_internal()
    if DEBUG:
        _debug_environment()
    return None


def _m_update(run):
    """[M0c] Actualización del script, versión instalada y dependencias."""
    reexec = getattr(sys, "_dlpy_reexec", False)     # recién instalada por la anterior: ya se comprobó
    if "--actualizar" in sys.argv[1:]:
        if not reexec:
            check_update(force=True)
        if UPDATE_CHECKED["ok"] or reexec:
            check_mark("script", script_sig())
        if LANG in PACK_LANGS:
            lang_pack_sync(LANG, force=True)
        return 0 if check_dependencies(force=True) else 1
    # 1.8.0: --shortcutpick con la escena viva: las actualizaciones van primero, no al final
    if LATE_UPDATES["on"] and updates_first():
        LATE_UPDATES["on"] = False
    rc = update_phase()
    # 1.8.0: D L P Y terminó: la escena suelta el título y el centro y el flujo pasa al resto de las escenas (sin esto se quedaba en D L P Y durante la descarga)
    ux_brand_end()
    return rc


def resume_one(item):
    """Reanuda una descarga pendiente con su enlace y su elección guardados (los mismos pasos que una normal)."""
    ux_reset_site_state()
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
    net_wrap_ytdlp(yt_dlp)          # 1.8.8: el icono de red de la franja
    run.yt_dlp = yt_dlp
    warn_youtube_js(run.link)
    return None


def _m_analyze(run):
    """[M1] Análisis (1 · 1b): extrae la información y deja listos formatos, audios, videos y pistas."""
    link = run.link
    ux_status("Analizando enlace", frac=0.02)
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
    ux_title(run.title)
    ux_shape(info)
    run.key = video_key(info)
    run.index = load_json(INDEX_FILE)
    run.old_file, run.old_entry = lookup_downloaded(run.index, run.key)
    dbg("info", {"clave": run.key, "titulo": run.title, "id": info.get("id"),
                 "extractor": info.get("extractor_key"), "duracion": info.get("duration"),
                 "formatos": len(info.get("formats") or [])})
    dbg("ya descargado", {"archivo": run.old_file, "entrada": run.old_entry} if run.old_file else "no")

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
                   + len(_legend_lines(["logo", "orig"])) + n_head + (1 if auto else 0) + 1   # +1: la línea en blanco
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
                           auto_n=auto_n, auto_line=auto_line, a_flags=["logo", "orig"], v_flags=["logo"],
                           a_vis=a_vis, v_vis=v_vis,
                           can_more=len(a_vis) < len(a_rows) or len(v_vis) < len(v_rows))


def _ci_show_list(ls, full, scene_status_text=None):
    """Pantalla de la lista; devuelve True si quedan filas ocultas (se ven con «m»)."""
    if full:
        hide_keyboard(0.3)          # iOS: lista completa con el teclado abajo para poder deslizar
    if scene_status_text is not None:
        native_clear()
        ux_list_top(ls.title, scene_status_text, animate=not getattr(ls, "top_seen", False))
        ls.top_seen = True
    else:
        clear_screen()
        show_title(ls.title)
    legend(["logo", "orig"])
    nwid = len(str(max(ls.choices))) if ls.choices else None          # 2.0.0: una sola anchura de número para audio, video y «yt-dlp auto»
    a_show = ls.a_rows if full else [ls.a_rows[i] for i in ls.a_vis]
    v_show = ls.v_rows if full else [ls.v_rows[i] for i in ls.v_vis]
    asx, vsx = len(ls.a_rows) - len(a_show), len(ls.v_rows) - len(v_show)
    if ls.a_rows:
        header(t_display("AUDIO") + (f" · +{asx} " + t_display("más") if asx else ""))
        print_rows(a_show, ls.a_flags, [t_display(h) for h in AUDIO_HEAD], num_w=nwid)
    if ls.v_rows:
        header(t_display("VIDEO") + (f" · +{vsx} " + t_display("más") if vsx else ""), gap=False)
        rows, vhead = drop_empty_cols(v_show, VIDEO_HEAD)   # «Rango» solo si algún formato lo usa
        print_rows(rows, ls.v_flags, [t_display(h) for h in vhead], num_w=nwid)
    if ls.auto_n:
        print_rows([{"n": ls.auto_n, "flags": set(), "cols": [ls.auto_line]}], [], num_w=nwid)
    print()
    more = bool(asx or vsx)
    hint(t_display("n.º · b ★ mejor ·") + (" " + t_display("m más · ") if more else " ") + t_display("q salir"))
    return more


def _ci_ask(run, ls):
    """3) Elegir. Devuelve (código de salida, None) si se sale (q, Ctrl-C) o (None, (kind, fmt, raw, use_auto))."""
    use_auto = run.use_auto
    # v=more (atajo): se abre ya la lista completa
    full0 = bool(getattr(run, "show_full", False))
    back = ux_list_enter("Ver todos" if full0 else "Elige un formato") if ux_on() else None   # 0.9.5: la escena cede
    top = scene_list_status(ls, full0) if back is not None else None
    # números, flechas y marcas con el color del sitio
    pal = _scene_palette() if back is not None else None
    try:
        return _ci_ask_loop(run, ls, use_auto, full0, top, back)
    finally:
        if pal is not None:
            PALETTE["orange"] = pal


def _scene_palette():
    """Pone el color del sitio como «orange» (números, flechas ▸, marca de predeterminada) y devuelve el original."""
    old = PALETTE["orange"]
    with quiet("_scene_palette"):
        PALETTE["orange"] = (mix(ux_get("a"), ux_get("b"), 0.35), old[1])
    return old


def scene_list_status(ls, full):
    """El estado gris bajo el título de la lista en la escena."""
    n = len(ls.a_rows) + len(ls.v_rows)
    return t_display("Ver todos ·") + f" {n} " + t_display("formatos") if full else t_display("Elige un formato")


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
    ux_list_leave(run, back)             # 0.9.5: la escena vuelve a abrirse desde el centro (sin escena no hace nada)
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
    ux_status("Eligiendo formato", frac=0.05)
    audios, videos, spick = run.audios, run.videos, run.spick
    auto = ytdlp_auto_pick(run.info, audios, videos)         # (video, audio|None) que elegiría yt-dlp
    run.auto = auto
    run.use_auto = False
    pre = (shortcut_resolve_video(spick, audios, videos, run.tracks, run.orig_ids, run.can_merge, auto)
           if spick else None)
    if pre is not None and spick and str(spick.get("v") or "").lower() == "ytdlp":
        run.use_auto = True
    run.show_full = bool(spick) and str(spick.get("v") or "").strip().lower() in SC_MORE_IDS   # «Ver todos» del atajo
    # 1.5.3: no se cae a la lista: mismo formato con otra escritura o el mejor compatible
    if spick and spick.get("v") and pre is None and not run.show_full:
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
        # 1.5.3: por qué se abre la lista
        dbg("lista", {"atajo": bool(spick), "v": (spick or {}).get("v"), "ver_todos": run.show_full})
        rc = _choose_interactive(run)
        if rc is not None:
            return rc

    dbg("elegido", {"entrada": run.raw, "tipo": run.kind, "formato": pick(run.fmt, FMT_KEYS)})
    ux_shape(run.fmt, run.info)
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
        bits.append(t("con audio") if has(fmt.get("acodec")) else t("sin audio"))
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


class _QuietLog:
    """Logger silencioso de yt-dlp: los avisos y errores se separan en internal/logs y el contexto técnico también va al debug."""
    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        diagnostic_report("A", msg)
        dbg("yt-dlp aviso", msg)

    def error(self, msg):
        log_shortcutmode_error(msg)
        dbg("yt-dlp error", msg)


# ─────────── [M6b] 2.0.7: fragmentos en paralelo, subtítulos y etiquetas (mutagen) ───────────
def fragments_n():
    """2.0.7: fragmentos a la vez (DLPY_CONCURRENT_FRAGMENTS, 1–16; 4 por omisión)."""
    return int(max(1, min(16, _env_num("DLPY_CONCURRENT_FRAGMENTS", 4.0, 1.0))))


def user_set_fragments():
    """2.0.7: ¿el usuario ya pidió -N / --concurrent-fragments en DLPY_YTDLP_EXTRA_ARGS? Entonces no se toca."""
    return any(a == "-N" or a.startswith("-N") and a[2:].isdigit() or a.startswith("--concurrent-fragments")
               for a in user_argv())


def subs_langs(raw=None):
    """2.0.7: DLPY_SUBTITLE_LANGS → lista de idiomas (['es', 'en']), ['all'] o [] si está apagado o no es válido."""
    v = str(env_get("DLPY_SUBTITLE_LANGS", "0") if raw is None else raw).strip().lower()
    if v in ("", "0", "no", "off", "false"):
        return []
    if v == "all":
        return ["all"]
    out = [x for x in re.split(r"[,\s;]+", v) if re.fullmatch(r"[a-z]{2,3}(?:-[a-z0-9]{2,8})*", x)]
    return out


def sub_files(res):
    """2.0.7: rutas de los subtítulos que yt-dlp dejó (requested_subtitles con filepath), que existan."""
    out = []
    try:
        for lang, d in sorted(((res or {}).get("requested_subtitles") or {}).items()):
            fp = (d or {}).get("filepath")
            if fp and os.path.isfile(fp):
                out.append((str(lang), fp))
    except AttributeError:
        pass
    return out


def store_subs(subs, final):
    """2.0.7: copia los subtítulos junto a `final` como «<nombre>.<idioma>.<ext>». Devuelve cuántos. Un fallo no detiene nada."""
    n = 0
    root = os.path.splitext(final)[0]
    for lang, fp in subs or []:
        try:
            ext = os.path.splitext(fp)[1] or ".vtt"
            dst = f"{root}.{lang}{ext}"
            if os.path.isfile(dst):
                os.remove(dst)
            move_file(fp, dst)
            n += 1
        except Exception as _ign:
            ignore("store_subs", _ign)
    return n


def _cover_bytes(thumb):
    """2.0.7: (bytes, 'jpeg'|'png') de la miniatura; webp se pasa a jpg con Pillow si está. None si no se puede."""
    ext = os.path.splitext(thumb)[1].lower()
    if ext in (".jpg", ".jpeg", ".png"):
        with open(thumb, "rb") as fh:
            return fh.read(), ("png" if ext == ".png" else "jpeg")
    if is_installed("PIL"):
        from PIL import Image
        buf = io.BytesIO()
        with Image.open(thumb) as im:
            im.convert("RGB").save(buf, "JPEG", quality=92)
        return buf.getvalue(), "jpeg"
    return None


def embed_tags(final, info, work_dir):
    """2.0.7: título, artista y carátula con mutagen en m4a/mp4/m4v/mov/mp3. Solo si DLPY_MEDIA_TAGS_ENABLED=1 y mutagen está instalado. True si escribió algo.
    Cualquier fallo se anota y se ignora: el archivo descargado nunca se pierde por unas etiquetas."""
    if not _flag_env("DLPY_MEDIA_TAGS_ENABLED", True) or not is_installed("mutagen") or not final or not os.path.isfile(final):
        return False
    ext = os.path.splitext(final)[1].lower()
    if ext not in (".m4a", ".mp4", ".m4v", ".mov", ".mp3"):
        return False
    info = info or {}
    title = str(info.get("track") or info.get("title") or "")
    artist = str(info.get("artist") or info.get("creator") or info.get("uploader") or info.get("channel") or "")
    cover = None
    with quiet("embed_tags", Exception):
        thumbs = sorted(glob.glob(os.path.join(work_dir, "*.jpg")) + glob.glob(os.path.join(work_dir, "*.jpeg")) +
                        glob.glob(os.path.join(work_dir, "*.png")) + glob.glob(os.path.join(work_dir, "*.webp")))
        if thumbs:
            cover = _cover_bytes(thumbs[0])
    try:
        if ext == ".mp3":
            from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TPE1, APIC
            try:
                tags = ID3(final)
            except ID3NoHeaderError:
                tags = ID3()
            if title:
                tags.setall("TIT2", [TIT2(encoding=3, text=title)])
            if artist:
                tags.setall("TPE1", [TPE1(encoding=3, text=artist)])
            if cover:
                tags.setall("APIC", [APIC(encoding=3, mime="image/" + cover[1], type=3, desc="Cover", data=cover[0])])
            tags.save(final)
        else:
            from mutagen.mp4 import MP4, MP4Cover
            mp = MP4(final)
            if title:
                mp["\xa9nam"] = [title]
            if artist:
                mp["\xa9ART"] = [artist]
            if cover:
                mp["covr"] = [MP4Cover(cover[0], MP4Cover.FORMAT_PNG if cover[1] == "png" else MP4Cover.FORMAT_JPEG)]
            mp.save()
        dbg("etiquetas mutagen", {"archivo": os.path.basename(final), "titulo": bool(title), "artista": bool(artist), "caratula": bool(cover)})
        return True
    except Exception as e:
        dbg("etiquetas mutagen fallaron", f"{type(e).__name__}: {e}")
        return False


def _ytdlp_options(run):
    """Opciones de yt-dlp para la descarga (con DLPY_DEBUG_LOGGING: yt-dlp tal cual, verbose y progreso nativo)."""
    ui = run.ui
    opts = {
        **run.base_opts,
        # 1.7.1: la CLI trae «only_download»: un fallo al bajar no lanzaba nada y el reintento de run_download nunca corría
        "ignoreerrors": False,
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
        "logger": _QuietLog(),              # 1.7.3: sin ERROR de yt-dlp en pantalla mientras run_download reintenta
    }
    if run.merge_ext:
        opts["merge_output_format"] = run.merge_ext
        opts["allow_multiple_audio_streams"] = True
    if not user_set_fragments():
        opts["concurrent_fragment_downloads"] = fragments_n()       # 2.0.7: DASH/HLS en paralelo (el -N del usuario manda)
    _sl = subs_langs()
    if _sl:                                                          # 2.0.7: subtítulos junto al video (si fallan, solo avisa)
        opts.update({"writesubtitles": True, "writeautomaticsub": False, "subtitleslangs": _sl,
                     "subtitlesformat": "srt/vtt/best"})
    if _flag_env("DLPY_MEDIA_TAGS_ENABLED", True) and is_installed("mutagen"):
        opts["writethumbnail"] = True                                # 2.0.7: la miniatura se usa de carátula (mutagen) y no se guarda aparte
    if DEBUG:
        # yt-dlp tal cual (verbose y progreso nativo), como fuera del script
        opts.update({"quiet": False, "no_warnings": False, "verbose": True,
                     "noprogress": False})
        opts.pop("logger", None)
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

    # 1.3.6: el tipo de cada stream sale de los formatos ya analizados (no del hook)
    STREAM_KINDS.clear()
    for _f in (run.formats or []):
        _k = ux_format_kinds(_f)
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
        # 1.5.8: la intro y los colores del sitio son de la UX; la UIM (sin shortcutmode) no los lleva
        if getattr(run, "spick", None) is not None:
            ux_site_theme_apply(run)         # 0.7.8: la pantalla de descarga usa los colores del sitio
            if not getattr(run, "site_shown", False):     # con la escena la intro ya salió al abrir
                ux_site_intro(run)           # intro de 1 s: la etiqueta queda lista para el banner de abajo
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
            run.subs = sub_files(res)                                  # 2.0.7: subtítulos listos en la carpeta de trabajo
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
    with quiet("embed_tags", Exception):
        embed_tags(final, run.info, work_dir)                          # 2.0.7: etiquetas y carátula antes de mover el archivo
    run.final = final
    return None


def _m_store(run):
    """[M7] Mover el resultado terminado a dlpy_files (solo procesos completados) y sustituir el anterior."""
    final, work_dir, old_file = run.final, run.work_dir, run.old_file
    dest_name = os.path.basename(final)
    dest_path = os.path.join(FILES_DIR, dest_name)
    replacing = bool(old_file) or (os.path.isfile(dest_path) and os.path.abspath(final) != os.path.abspath(dest_path))
    if replacing:
        ux_status("Sustituyendo", frac=0.95)      # 1.4.2: la sustitución conserva su escena independiente
    if os.path.abspath(final) != os.path.abspath(dest_path):
        tmp_dest = dest_path + ".tmp"
        try:
            drop_deliveries(dest_name)                        # su entrega anterior (enlace al archivo viejo) también
            # mismo nombre: el nuevo reemplaza al anterior, pero el viejo no se borra hasta tener el nuevo entero (1.7.5)
            if os.path.isfile(dest_path):
                move_file(final, tmp_dest)
                os.replace(tmp_dest, dest_path)
            else:
                move_file(final, dest_path)
            final = dest_path
        except Exception as e:
            with quiet("_m_store", OSError):
                os.remove(tmp_dest)
            cleanup_work(work_dir)
            m_err(f"No se pudo guardar el archivo en {FILES_DIR}: {e}")
            return 1

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
    _ns = store_subs(getattr(run, "subs", None), final)              # 2.0.7: subtítulos junto al archivo; luego sí se limpia el trabajo
    if _ns:
        m_ok(f"Subtítulos: {_ns}")
    cleanup_work(work_dir)
    if replacing:
        ux_hold(SCENE_REPLACE_SECS)  # solo se conserva el cierre de la escena real de sustitución
    # 1.8.5: confirmar después de move_file/os.replace, sin animar un progreso inexistente
    ux_status("Guardado", frac=1.0)
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
    except DISK_ERRORS as e:
        m_warn(f"No se pudo guardar el índice: {e}")
    history_add(key, index[key])          # downloads.json guarda cada descarga, no solo la última

    result_card(final, title, index[key]["meta"], run.info.get("duration"))
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
    except Exception as exc:
        # llega a la bottombar antes de que la escena se cierre
        diagnostic_report("E", f"Error inesperado: {type(exc).__name__}: {exc}")
        raise
    finally:
        ux_error_end()                   # 1.0.8: un error se muestra en D L P Y antes de cerrar la escena
        # 0.9.3: si la escena sigue activa (error, Ctrl-C, sin entrega) se quita y la consola vuelve a lo normal
        ux_stop(clear=True)


if __name__ == "__main__":
    sys.exit(run_main(main))