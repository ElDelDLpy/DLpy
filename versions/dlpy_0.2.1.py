#!dlpy.py
# -*- coding: utf-8 -*-
# 0.2.1: «SOFTWARE DE CODIFICACION». Todo archivo final mp4/m4v/m4a lleva «DLpy <VERSION>» en ese metadato (el ©too que iOS muestra en
#        Fotos/Archivos > Info; antes salia el «Lavf…» de ffmpeg). Se escribe con `-metadata encoding_tool=` (el `encoder` de ffmpeg lo pisa
#        el propio muxer con su Lavf, y -fflags +bitexact lo quita sin dejar el nuestro). Las pasadas que ya reescriben el archivo
#        (conversion a Apple, etiquetado de pistas de audio) lo escriben en la misma pasada; al final, si el archivo aun no lo lleva, se
#        hace UN remux sin recodificar (-c copy +faststart) solo para eso. Se lee directo del atom ©too (sin ffprobe), asi que no se
#        repite. mkv/mov/mp3... no cambian (sus muxers no dejan poner el nuestro). Un fallo solo avisa. Se apaga con --config TOOLTAG=0.
# 0.2.0: MODULOS AL DIA. La revision semanal (la misma de la autoactualizacion, UPDATE_DAYS) tambien actualiza los modulos ya
#        instalados en dlpy_files/_modules/ (hoy dlpy_anim.py): si el index.json de MODULES_URL trae otro sha256 con la API que
#        espera este host, baja la version nueva, verifica el hash y que compile, y la reemplaza (si algo falla se conserva la
#        anterior). Los modulos que no estan instalados no se bajan solos (siguen bajandose al usarlos). Si el host acaba de
#        actualizarse, el host nuevo hace esta revision. Nuevos: --update-modules (revisa ya e instala los que falten) y la
#        opcion "Actualizar modulos" del menu de config. Una copia en modules/ junto a este archivo sigue teniendo prioridad.
#        DEPENDENCIAS: la misma revision tambien pone al dia los paquetes de pip de la clave DEPS (por defecto "pip,yt-dlp"; se
#        agregan mas con --config DEPS=pip,yt-dlp,otro). Consulta PyPI y solo corre `pip install -U` si hay version mas nueva que
#        la instalada (los no instalados solo se instalan con --update-deps). Con salida JSON (--scb/--shortcutpick/--long) es
#        silenciosa y redirige la salida de pip. Un fallo nunca detiene el script. Nuevo: --update-deps y su opcion en el menu.
#        Los modulos nuevos que aparezcan en index.json y ya esten instalados tambien se actualizan, sin tocar el host.
# 0.1.9: AUTOACTUALIZACION. Al abrir (una vez por semana, UPDATE_DAYS) consulta el ultimo Release de GitHub (ElDelDLpy/DLpy); si su
#        version es MAYOR, baja el asset dlpy.py, verifica su SHA-256 (asset dlpy.py.sha256 o, si falta, el de las notas del Release),
#        que compile, que empiece con #!dlpy.py y que su VERSION coincida con la del tag; guarda la anterior en dlpy_files/_backups/,
#        reescribe este mismo archivo y SIGUE la ejecucion con la version nueva (runpy en el mismo proceso: sin os.exec, que a-Shell no
#        soporta) con los mismos argumentos. Sin red reintenta al dia siguiente. No corre en --scm/--idiomas/--config/--version/--help
#        (tiempo limitado o sin necesidad); en --scb/--shortcutpick/--long es silencioso (la salida es JSON). Se apaga con --config UPDATE=0;
#        --self-update fuerza la consulta ya. DLPY_NOUPDATE=1 en el entorno tambien la salta.
# 0.1.8: la escena (dlpy_anim.py 0.0.2) MUESTRA LA CONVERSION. El host solo pasa la AnimUI a ensure_apple/apple_convert/run_conv y llama
#        ui.conv_begin(path, streams, plan, final_ext, enc) / ui.conv_progress(%) / ui.conv_end(ok) (ui_conv: se salta si no hay escena o
#        el modulo es anterior). Que dicen los chips (VP9 -> H.264, MKV -> MP4...) lo decide el modulo. --long no usa escena.
# 0.1.7: (VERSION queda fija en 0.1.7: los cambios siguientes se anotan aqui, sin subir el numero.)
#        (1) ANIM="0" por defecto: las animaciones de la escena quedan apagadas (se activan con --config ANIM=1; una
#        dlpy_config.json ya guardada conserva su valor). (2) Despues de CADA descarga se revisa el archivo final con ffprobe
#        (o `ffmpeg -i` si no hay ffprobe) y, si no es compatible con Apple, se convierte; vale tambien lo que la lista
#        --scm/--scb marco como nativo (), porque el archivo real puede no serlo (p. ej. hev1, 10 bits 4:4:4, mkv).
#        Compatible = mp4/m4v/mov (m4a/mp3/... si es solo audio) con H.264 o HEVC (hvc1) en yuv420p y audio AAC/ALAC/MP3/AC-3/E-AC-3.
#        El ffmpeg de a-Shell no trae libx264/libx265: se recodifica con los encoders que ESE ffmpeg declare (como en 2.1.5):
#        hevc_videotoolbox (-allow_sw 1) -> libx265 -> libkvazaar -> libx264 -> h264_videotoolbox; conserva 10 bits y HDR (etiquetas BT.2020).
#        Se hace lo minimo: solo cambia el contenedor (copia, sin recodificar) o la etiqueta hvc1 cuando basta; recodifica
#        (H.264 + AAC) solo la pista que no sirve. Si falla, se conserva el original y se avisa.
# 0.1.6: nombres simples y "seguros". safe_title(): sin emojis, enlaces ni simbolos raros (% + $ ` ! \\ / : * ? " < > | # & ...), sin
#        el encabezado de estadisticas de redes ("14K reactions · 1.9K shares |"), una sola linea, corto y cortado en palabra.
#        --scb/--scm (prompt del JSON), listas y pantallas muestran ese nombre corto (50); el archivo guardado se llama igual (60,
#        sin [id]): se baja como <id>.<ext> y al terminar se renombra; si ya existe, DUP decide ("nombre (2)" o reemplazar).
# 0.1.5: --long: el avance (`progress`) ya es real y no salta a 99. Antes solo sumaba los bytes que yt-dlp informaba: al acabar la
#        primera pista (video) "hecho" igualaba al "total" conocido y quedaba en 99 mientras bajaba el audio, y las pistas sin
#        total (fragmentos HLS/DASH, p. ej. ok.ru) no movian nada hasta el final. Ahora cada pista aporta fraccion x peso:
#        peso = tamano real, o el esperado (filesize/filesize_approx/tbr x duracion de la lista de formatos), y las pistas aun
#        no iniciadas cuentan con su tamano esperado; sin total usa fragment_index/fragment_count; si no hay forma de
#        estimar, avance indeterminado con los MB bajados en el titulo. Nunca baja y llega a 100 solo al terminar (--done).
# 0.1.4: --long (con --scm y --shortcutpick): para la accion "Execute Long Command" de a-Shell (iOS 27). Corre con el tiempo
#        en segundo plano de iOS (banner, Dynamic Island, pantalla bloqueada), sin los 5 s de --scm, y avisa el avance con
#        `progress` (porcentaje de la descarga; al procesar, indeterminado). La salida es SOLO una linea JSON que lee el atajo.
#        --scm --long: instala yt-dlp si falta y devuelve el JSON shortcutmode COMPLETO (sin topes de videos/pistas) con lo
#        Apple nativo primero ( ); ya no hay timeout/install -> --scb, solo las listas de reproduccion piden --scb.
#        --shortcutpick --long: {"dlpy":"file","ok":true,"file_path":...,"file_title":...} o {"dlpy":"file","ok":false,"error":...};
#        sin escena animada ni vuelta por shortcuts:// (CALLBACK no se usa). Sin --long todo sigue igual que en 0.1.3.
# 0.1.3: --scm ya no usa un hilo ni os._exit(0): en a-Shell, al vencer el tiempo, os._exit cerraba el proceso con el hilo
#        todavia dentro de yt-dlp y terminaba en "segmentation fault". Ahora el limite lo vigila el logger de yt-dlp
#        (_Log.deadline), que corta entre una peticion y la siguiente; sin hilos al salir.
# 0.1.2: el index.json de idiomas del script usa el mismo formato que el del atajo, asi que el archivo se puede copiar
#        tal cual de uno a otro: {"names": ["🇺🇸 English", ...], "🇺🇸 English": "en", ...} (names da el orden; cada
#        etiqueta apunta a su codigo). Cada uno sigue leyendo el suyo (script: LANG_URL/index.json); el script tambien
#        acepta los formatos anteriores (lista de codigos, {code,label}, {codigo: etiqueta}).
# 0.1.1: las animaciones de la escena (descarga, barra, morph, union, envio) viven en un modulo aparte, dlpy_anim.py
#        (version propia, ver su cabecera: 0.0.1): carpeta modules/ junto a este archivo o dlpy_files/_modules/; si falta se baja de MODULES_URL (modules/index.json con version, api y sha256; se verifica el hash). Es opcional: sin el
#        archivo, con ANIM=0, fuera de un terminal con color, con un API distinta (ANIM_API) o ante cualquier
#        fallo se usa la barra simple de siempre.
#        Seguridad: (1) ffmpeg por os.system escapa $ y ` y los nombres de archivo ya no los llevan;
#        (2) los .po solo pueden usar {marcadores} simples que existan en el texto original;
#        (3) la configuracion se valida (valores permitidos) al leerla, con --config y en el menu.
# 0.1.0: los idiomas .po faltantes se bajan de GitHub (LANG_URL, por defecto script/lang del repo);
#        el menu de idioma ofrece los remotos (index.json); --update-langs re-baja los instalados.
# 0.0.9: todo texto pasa por tr()/trn() (gettext): el espanol va en el codigo y los demas idiomas son
#        paquetes .po en dlpy_files/_lang/ (sin STR ni T()); dlpy_i18n.py extrae el .pot y valida.
# 0.0.8: descargas en dlpy_files/_cache/<enlace> (pistas reutilizables 24 h, DLPY CACHE_H) y
#        colocacion final con DUP=new|replace (antes yt-dlp se saltaba el archivo ya existente).
# 0.0.7: pistas de audio con language=und (iOS elegia por idioma del sistema, no la principal);
#        ffmpeg con respaldo os.system y aviso si el etiquetado falla.
# 0.0.6: run_pick() unico (sin pasar por texto V=,A=,X=); start() comun para --scb y terminal;
#        download/pick_container/can_merge reciben la config como parametros (sin leer CFG).
"""DLpy - descargador de video y audio para a-Shell (basado en yt-dlp)."""
import os
import sys
import io
import re
import json
import time
import shutil
import hashlib
import warnings
import contextlib
import importlib
import importlib.util
import subprocess
import urllib.parse

VERSION = "0.2.1"

START = time.time()     # para el limite de tiempo de --scm
LONG = False            # --long: salida JSON unica + avance con `progress` (Execute Long Command)
_OUT = sys.stdout       # salida real: en --long el resto de prints se descarta y solo se emite el JSON final
_PG = {"trk": {}, "exp": {}, "n": 1, "dur": None, "last": 0.0, "pct": 0, "ind": False, "emitted": False}
SCM_LIMIT = 5.0         # segundos maximos de --scm; si no alcanza, el atajo usa --scb
APPLE = "\uf8ff"        #  (logo de Apple; se ve en iOS/macOS) = reproducible de forma nativa

ANIM_API = 1           # contrato que este host espera de dlpy_anim.py (su API)
DEP_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")      # nombre de paquete de pip valido (va a un comando)

SHORTCUT_NAME = "DLpy"
DOCS = os.path.expanduser("~/Documents")
CFG_PATH = os.path.join(DOCS, "dlpy_config.json")
DEFAULTS = {
    "LANG": "es",        # idioma del script
    "LANG_URL": "https://raw.githubusercontent.com/ElDelDLpy/DLpy/main/script/lang",  # de donde se bajan los .po
    "MODULES_URL": "https://raw.githubusercontent.com/ElDelDLpy/DLpy/main/script/modules",  # de donde se baja dlpy_anim.py
    "DIR": "dlpy_files",  # carpeta de descargas (relativa a ~/Documents)
    "MERGE": "auto",     # contenedor al unir: auto (mp4 si todo es compatible con Apple, si no mkv) | mp4 | mkv
    "AUDIO": "native",   # audio solo: native | mp3 | m4a
    "FFMPEG": "auto",    # auto | yes | no (forzar la deteccion de ffmpeg)
    "CALLBACK": "1",     # 1 = al terminar, abrir el atajo para previsualizar
    "DUP": "new",        # si el archivo final ya existe: new (nombre (2)) | replace
    "CACHE_H": "24",     # horas que se conservan las pistas en dlpy_files/_cache (0 = borrar al terminar)
    "PATH": "abs",       # ruta enviada al atajo: abs (absoluta) | home (desde ~) | rel (desde ~/Documents)
    "DEPS": "pip,yt-dlp",  # paquetes de pip que la revision semanal mantiene al dia (separados por coma)
    "TOOLTAG": "1",      # 1 = escribir «DLpy <version>» en el «Software de codificación» del mp4/m4v/m4a final | 0 = no
    "UPDATE": "1",       # 1 = al abrir, buscar cada semana un Release nuevo de dlpy.py (y poner al dia sus modulos y dependencias) | 0 = no
    "ANIM": "0",         # 0 = barra simple (por defecto) | 1 = animaciones de la escena si existe dlpy_anim.py (terminal con color)
}

# ------------------------------------------------------- idiomas (estilo gettext)
# El codigo trae los textos en espanol: tr("texto") los devuelve tal cual. Otro idioma es un
# paquete <codigo>.po en dlpy_files/_lang/ (msgid = el texto en espanol). Sin paquete, espanol.
BASE_LANG = "es"
BASE_LABEL = "🇪🇸 Español"
_CATS = {}
LANG_RE = re.compile(r"^[A-Za-z]{2,3}(?:[_-][A-Za-z0-9]{2,8})?$")
NET_LANGS = True       # False en --scm/--idiomas: sin red para no pasar el limite de tiempo
_TRIED = set()


def _unq(s):
    s = s.strip()
    if len(s) < 2 or s[0] != '"' or s[-1] != '"':
        return ""
    return re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t"}.get(m.group(1), m.group(1)), s[1:-1])


def parse_po(text):
    """Lector minimo de .po (sin msgfmt): ({msgid: msgstr | [formas]}, encabezado). Ignora fuzzy."""
    msgs, hdr = {}, {}
    for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n")):
        e, cur, fuzzy = {}, None, False
        for ln in block.split("\n"):
            ln = ln.strip()
            if ln.startswith("#"):
                fuzzy = fuzzy or (ln.startswith("#,") and "fuzzy" in ln)
                continue
            m = re.match(r'(msgctxt|msgid_plural|msgid|msgstr)(?:\[(\d+)\])?\s+(".*)$', ln)
            if m:
                cur = (m.group(1), int(m.group(2) or 0))
                e[cur] = _unq(m.group(3))
            elif ln.startswith('"') and cur:
                e[cur] += _unq(ln)
        mid = e.get(("msgid", 0))
        if mid is None or ("msgctxt", 0) in e:
            continue
        if ("msgid_plural", 0) in e:
            forms = [v for (k, i), v in sorted(e.items(), key=lambda kv: kv[0][1]) if k == "msgstr"]
            val = forms if any(forms) else None
        else:
            val = e.get(("msgstr", 0)) or None
        if mid == "":
            for ln in (val or "").split("\n"):
                k, _s, v = ln.partition(":")
                if v:
                    hdr[k.strip()] = v.strip()
        elif val and not fuzzy:
            msgs[mid] = val
    return msgs, hdr


_PH = re.compile(r"\{[^{}]*\}")


def _ph_names(text):
    """Nombres de {marcadores} de `text` (ignora {{ y }}); None si alguno no es un nombre simple."""
    names = set()
    for m in _PH.findall(text.replace("{{", "").replace("}}", "")):
        n = m[1:-1]
        if not re.fullmatch(r"\w*", n):       # {x.attr}, {x[0]}, {x!r}, {x:>99}: no permitidos
            return None
        names.add(n)
    return names


def safe_msgs(msgs):
    """Quita las traducciones con marcadores raros o que no existan en el texto original."""
    out = {}
    for mid, val in msgs.items():
        allowed = _ph_names(mid) or set()
        forms = val if isinstance(val, list) else [val]
        ok = True
        for f in forms:
            names = _ph_names(f) if isinstance(f, str) else set()
            if names is None or (not isinstance(val, list) and not names <= allowed) \
                    or (isinstance(val, list) and not all(re.fullmatch(r"\w+", n) for n in names)):
                ok = False
                break
        if ok:
            out[mid] = val
    return out


def lang_dir():
    return os.path.join(base_dir(), "_lang")


def load_cat(code):
    """(mensajes, encabezado, funcion de plural) del idioma; el base no necesita paquete."""
    if code not in _CATS:
        msgs, hdr, plural = {}, {}, None
        if code != BASE_LANG and LANG_RE.match(code or ""):
            if NET_LANGS and code not in _TRIED and not lang_installed(code):
                _TRIED.add(code)
                lang_download(code)
            try:
                with open(os.path.join(lang_dir(), code + ".po"), encoding="utf-8") as f:
                    msgs, hdr = parse_po(f.read())
                msgs = safe_msgs(msgs)
                from gettext import c2py
                plural = c2py(re.search(r"plural=([^;]+)", hdr.get("Plural-Forms", "")).group(1))
            except Exception:
                pass
        _CATS[code] = (msgs, hdr, plural)
    return _CATS[code]


def tr_in(code, msg, **kw):
    """Texto `msg` (en espanol) en el idioma `code`; {marcadores} se rellenan con kw."""
    s = load_cat(code)[0].get(msg)
    for t in (s, msg):
        if isinstance(t, str):
            try:
                return t.format(**kw) if kw else t
            except (KeyError, IndexError, ValueError):
                pass
    return msg


def trn_in(code, one, other, n, **kw):
    """Como tr_in con plural (ngettext): `one` si n == 1, si no `other`; {n} disponible."""
    msgs, _h, plural = load_cat(code)
    forms, s = msgs.get(one), None
    if isinstance(forms, list) and plural:
        try:
            s = forms[int(plural(n))]
        except Exception:
            s = None
    kw.setdefault("n", n)
    for t in (s, one if n == 1 else other):
        if isinstance(t, str):
            try:
                return t.format(**kw)
            except (KeyError, IndexError, ValueError):
                pass
    return one if n == 1 else other


def tr(msg, **kw):
    return tr_in(CFG["LANG"], msg, **kw)


def trn(one, other, n, **kw):
    return trn_in(CFG["LANG"], one, other, n, **kw)


def lang_name(code):
    h = load_cat(code)[1]
    return h.get("X-Name") or h.get("X-Label") or (BASE_LABEL.split(" ", 1)[-1] if code == BASE_LANG else code)


def list_langs():
    """[(codigo, etiqueta)]: el base y un paquete .po por idioma instalado."""
    out = [(BASE_LANG, BASE_LABEL)]
    try:
        names = sorted(os.listdir(lang_dir()))
    except OSError:
        names = []
    for fn in names:
        if fn.endswith(".po") and fn[:-3] != BASE_LANG:
            out.append((fn[:-3], load_cat(fn[:-3])[1].get("X-Label") or fn[:-3]))
    return out


def lang_installed(code):
    return os.path.exists(os.path.join(lang_dir(), code + ".po"))


def lang_url(name):
    return CFG["LANG_URL"].rstrip("/") + "/" + name


def http_get(url, timeout=4, limit=2000000):
    """Bytes de `url` o None. Usa urllib y, si falla, curl (a-Shell) por os.system."""
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "DLpy/" + VERSION})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read(limit)
    except Exception:
        pass
    tmp = os.path.join(DOCS, ".dlpy_get.tmp")
    try:
        import shlex
        rc = os.system("curl -fsSL --max-time %d -o %s %s >/dev/null 2>&1"
                       % (timeout, shlex.quote(tmp), shlex.quote(url)))
        if rc == 0:
            with open(tmp, "rb") as f:
                return f.read(limit) or None
    except Exception:
        pass
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    return None


def lang_download(code):
    """Baja <LANG_URL>/<code>.po a dlpy_files/_lang/ (valido y atomico). True si quedo instalado."""
    if code == BASE_LANG or not LANG_RE.match(code or ""):
        return False
    raw = http_get(lang_url(code + ".po"))
    try:
        text = raw.decode("utf-8")
        ok = bool(parse_po(text)[0])
    except Exception:
        ok = False
    if not ok:
        return False
    try:
        os.makedirs(lang_dir(), exist_ok=True)
        dst = os.path.join(lang_dir(), code + ".po")
        with open(dst + ".tmp", "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(dst + ".tmp", dst)
    except OSError:
        return False
    _CATS.pop(code, None)
    return True


def parse_lang_index(raw):
    """[(codigo, etiqueta)] de un index.json (bytes o texto); [] si no se entiende.
    Formato unico, el del atajo: {"names": ["🇺🇸 English", ...], "🇺🇸 English": "en", ...}
    (names da el orden y cada etiqueta apunta a su codigo; el atajo solo lee esas claves).
    Tambien acepta los formatos anteriores del script: lista de codigos, de {code,label} o {codigo: etiqueta}."""
    try:
        d = json.loads(raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw)
        if isinstance(d, dict) and isinstance(d.get("names"), list):       # formato del atajo
            items = [(d.get(n), n) for n in d["names"] if isinstance(n, str)]
        elif isinstance(d, dict):
            items = [(v, k) if isinstance(v, str) and not LANG_RE.match(k) and LANG_RE.match(v) else (k, v)
                     for k, v in d.items()]                               # {codigo: etiqueta} o {etiqueta: codigo}
        else:
            items = [(x, None) if isinstance(x, str) else (x.get("code"), x.get("label"))
                     for x in d if isinstance(x, (str, dict))]
    except Exception:
        return []
    out, seen = [], set()
    for c, l in items:
        if isinstance(l, dict):
            l = l.get("label") or l.get("name")
        if isinstance(c, str) and LANG_RE.match(c) and c != BASE_LANG and c not in seen:
            seen.add(c)
            out.append((c, l if isinstance(l, str) and l else c))
    return out


def remote_langs():
    """[(codigo, etiqueta)] de <LANG_URL>/index.json (formato en parse_lang_index)."""
    return parse_lang_index(http_get(lang_url("index.json"), 3))


CHOICES = {
    "MERGE": {"auto", "mp4", "mkv"}, "AUDIO": {"native", "mp3", "m4a"},
    "FFMPEG": {"auto", "yes", "no"}, "CALLBACK": {"0", "1"}, "DUP": {"new", "replace"},
    "PATH": {"abs", "home", "rel"}, "ANIM": {"0", "1"}, "UPDATE": {"0", "1"}, "TOOLTAG": {"0", "1"},
}


def valid_cfg(k, v):
    """(ok, valor normalizado) para la clave de configuracion k."""
    v = str(v).strip()
    if k in CHOICES:
        v = v.lower()
        return v in CHOICES[k], v
    if k == "LANG":
        return bool(LANG_RE.match(v)), v
    if k in ("LANG_URL", "MODULES_URL"):
        return v.lower().startswith("https://"), v
    if k == "CACHE_H":
        try:
            return float(v) >= 0, v
        except ValueError:
            return False, v
    if k == "DIR":
        return bool(v) and "\x00" not in v, v
    if k == "DEPS":
        names = [x for x in re.split(r"[,\s]+", v) if x]
        return all(DEP_RE.match(x) for x in names), ",".join(names)
    return True, v


def load_cfg():
    c = dict(DEFAULTS)
    try:
        with open(CFG_PATH, encoding="utf-8") as f:
            d = json.load(f)
        for k, v in d.items():
            k = str(k).upper()
            if k in c:
                ok, nv = valid_cfg(k, v)
                if ok:
                    c[k] = nv
    except Exception:
        pass
    if c["DIR"] == "DLpy":          # carpeta por defecto de versiones anteriores
        c["DIR"] = DEFAULTS["DIR"]
    return c


def save_cfg():
    try:
        os.makedirs(DOCS, exist_ok=True)
        with open(CFG_PATH, "w", encoding="utf-8") as f:
            json.dump(CFG, f, ensure_ascii=False, indent=1)
        return True
    except Exception:
        return False


CFG = load_cfg()


# ---------------------------------------------------------------- utilidades
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.I)


_STATS = re.compile(r"\b(reactions?|views?|shares?|likes?|comments?|followers?|reacciones|vistas|compartidos?|me gusta)\b", re.I)


def safe_title(t, n=50, fallback="video"):
    """Nombre corto y seguro (sirve para mostrar y para archivos): letras, numeros, espacio y - _ . , ( )."""
    t = URL_RE.sub(" ", t or "")
    parts = [p for p in re.split(r"\s*[|\uff5c]\s*", t) if p.strip()]
    keep = [p for p in parts if not _STATS.search(p)]
    t = " ".join((keep or parts)[:1]) if keep else " ".join(parts[:1])
    t = re.sub(r"[^\w\s.,()-]", " ", t)           # emojis y simbolos fuera (los acentos se conservan)
    t = re.sub(r"\s+([.,)])", r"\1", re.sub(r"\s+", " ", t)).strip(" ._-,")
    if len(t) > n:
        cut = t[:n]
        t = (cut.rsplit(" ", 1)[0] if " " in cut[n // 2:] else cut).strip(" ._-,")
    return t or fallback


def jprint(obj):
    """JSON compacto en una linea (el atajo busca "ok":true, "use_scb":true...)."""
    sys.stdout.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def prog(*args):
    """Avance para Execute Long Command (comando `progress` de a-Shell). Sin --long no hace nada y nunca falla."""
    if not LONG:
        return
    try:
        subprocess.run(["progress"] + [str(a) for a in args], capture_output=True)
    except Exception:
        pass


def est_size(f, dur=None):
    """Bytes esperados de una pista segun su dict de formato (0 si no se puede estimar)."""
    f = f or {}
    n = f.get("filesize") or f.get("filesize_approx") or 0
    if not n and f.get("tbr"):
        d = dur or f.get("duration") or _PG.get("dur")
        n = float(f["tbr"]) * 1000 / 8.0 * d if d else 0
    return int(n or 0)


def long_plan(by, fmt):
    """--long: tamanos esperados de las pistas a bajar (ids de fmt) para que el avance cuente las que aun no empiezan."""
    ids = [i for i in (fmt or "").split("+") if i]
    _PG["n"] = max(1, len(ids))
    _PG["exp"] = {i: est_size((by or {}).get(i)) for i in ids}


def long_pct():
    """Avance global 0-99 o None: suma fraccion x peso de cada pista; las que no empezaron valen su tamano esperado."""
    trk = _PG["trk"]
    items = [(t["f"], t["w"]) for t in trk.values()]
    spare = [w for i, w in _PG["exp"].items() if i not in trk]
    for w in spare[:max(0, _PG["n"] - len(trk))]:
        items.append((0.0, w))
    items += [(0.0, 0)] * max(0, _PG["n"] - len(items))
    known = [w for _, w in items if w]
    if not known and not any(f for f, _ in items) and not any(t.get("fr") for t in trk.values()):
        return None
    avg = sum(known) / len(known) if known else 1.0
    tw = sum((w or avg) for _, w in items)
    if tw <= 0:
        return None
    return min(99, int(sum(f * (w or avg) for f, w in items) * 100 / tw))


def long_hook(d):
    """--long: avance real. Por pista: fraccion = bytes/total (o fragmentos, o bytes/tamano esperado) y su peso en bytes."""
    st = d.get("status")
    inf = d.get("info_dict") or {}
    key = str(inf.get("format_id") or d.get("filename") or "?")
    t = _PG["trk"].setdefault(key, {"f": 0.0, "w": 0, "done": 0})
    done = d.get("downloaded_bytes") or 0
    t["done"] = max(t["done"], done)
    if st == "finished":
        t["f"] = 1.0
        t["w"] = int(d.get("total_bytes") or t["done"] or t["w"] or _PG["exp"].get(key) or 0)
    elif st == "downloading":
        tot = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        w = int(tot or _PG["exp"].get(key) or est_size(inf) or 0)
        if w:
            t["w"] = max(t["w"], w)
        fc = d.get("fragment_count") or 0
        if tot or w:
            f = t["done"] / float(max(t["w"], 1))
        elif fc:
            t["fr"] = True
            f = max(0, (d.get("fragment_index") or 1) - 1) / float(fc)
        else:
            f = 0.0
        t["f"] = max(t["f"], min(0.99, f))
        now = time.time()
        if now - _PG["last"] < 1.0:
            return
        _PG["last"] = now
    else:
        return
    pct = long_pct()
    if pct is None:           # sin forma de estimar: indeterminado, con los MB bajados en el titulo
        if not _PG["ind"]:
            _PG["ind"] = True
            prog("--indeterminate")
        prog("--title", "DLpy \u00b7 " + fmt_size(sum(x["done"] for x in _PG["trk"].values())))
    elif pct > _PG["pct"]:
        _PG["pct"] = pct
        if _PG["ind"]:
            _PG["ind"] = False
            prog("--title", "DLpy")
        prog("%d%%" % pct)


def long_pp_hook(d):
    """--long: el postproceso (union con ffmpeg...) no tiene porcentaje: avance indeterminado."""
    if d.get("status") == "started":
        prog("--title", tr("⚙️ Procesando…"))
        prog("--indeterminate")


def emit_long(**d):
    """--long: la UNICA linea que recibe el atajo (ASCII puro: los acentos van como \\uXXXX)."""
    o = {"dlpy": "file"}
    o.update(d)
    _PG["emitted"] = True
    _OUT.write(json.dumps(o, ensure_ascii=True, separators=(",", ":")) + "\n")
    _OUT.flush()


def shared_path(path):
    """Ruta que se envia al atajo segun CFG[PATH]: abs | home | rel."""
    mode = CFG["PATH"].lower()
    if mode == "rel":
        return os.path.relpath(path, DOCS)
    if mode == "home":
        return os.path.relpath(path, os.path.expanduser("~"))
    return os.path.abspath(path)


def clean_url(s):
    m = URL_RE.search(s or "")
    return m.group(0).rstrip(".,;)") if m else ""


def clean_err(e):
    s = ANSI.sub("", str(e)).strip()
    s = re.sub(r"^(ERROR:\s*)+", "", s)
    s = re.sub(r"\s*\(caused by .*", "", s, flags=re.S)
    return s.splitlines()[0][:300] if s else e.__class__.__name__


def fmt_size(n):
    if not n:
        return ""
    n = float(n)
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return "%d %s" % (n, u) if u == "B" else "%.1f %s" % (n, u)
        n /= 1024.0


def fmt_dur(s):
    try:
        s = int(s)
    except Exception:
        return ""
    h, r = divmod(s, 3600)
    m, sec = divmod(r, 60)
    return "%d:%02d:%02d" % (h, m, sec) if h else "%d:%02d" % (m, sec)


def base_dir():
    d = CFG["DIR"] or "dlpy_files"
    return d if os.path.isabs(d) else os.path.join(DOCS, d)


def out_dir():
    d = base_dir()
    os.makedirs(d, exist_ok=True)
    return d


class _Deadline(BaseException):
    """Se lanza desde _Log al vencer el limite. BaseException: yt-dlp atrapa Exception, no esto."""


class _Log:
    deadline = None          # time.time() maximo; None = sin limite

    def debug(self, m):
        # yt-dlp manda aqui cada paso ("Downloading webpage"...): sirve para cortar sin hilos ni os._exit
        if self.deadline is not None and time.time() > self.deadline:
            raise _Deadline()

    info = warning = error = debug


def import_ytdlp(install=False):
    try:
        import yt_dlp
        return yt_dlp
    except ImportError:
        pass
    if not install:
        return None
    print(tr("⬇️ Instalando yt-dlp (solo la primera vez)…"))
    os.system("pip install -q yt-dlp")
    importlib.invalidate_caches()
    try:
        import yt_dlp
        return yt_dlp
    except ImportError:
        print(tr("No se pudo instalar yt-dlp. Revisa tu conexión."))
        return None


def can_merge(mode="auto"):
    mode = (mode or "auto").lower()
    if mode in ("yes", "1", "true"):
        return True
    if mode in ("no", "0", "false"):
        return False
    try:
        from yt_dlp.postprocessor.ffmpeg import FFmpegPostProcessor
        return bool(FFmpegPostProcessor(None).available)
    except Exception:
        return False


# ------------------------------------------------- analisis de formatos
AUD_EXT = {"m4a", "mp3", "opus", "ogg", "aac", "flac", "wav", "weba"}
BAD_ID = re.compile(r"[,+\"'\s\\:]")
V_ORDER = {"avc1": 0, "hevc": 1, "vp9": 2, "av1": 3}


def fam_v(c):
    c = (c or "").lower()
    for k, n in (("avc", "avc1"), ("h264", "avc1"), ("hev", "hevc"), ("hvc", "hevc"),
                 ("h265", "hevc"), ("vp09", "vp9"), ("vp9", "vp9"), ("vp8", "vp8"),
                 ("av01", "av1"), ("av1", "av1")):
        if c.startswith(k):
            return n
    return c.split(".")[0] or "?"


def fam_a(c):
    c = (c or "").lower()
    for k, n in (("mp4a", "aac"), ("aac", "aac"), ("opus", "opus"), ("vorbis", "vorbis"),
                 ("ec-3", "eac3"), ("eac3", "eac3"), ("ac-3", "ac3"), ("mp3", "mp3"),
                 ("flac", "flac")):
        if c.startswith(k):
            return n
    return c.split(".")[0] or "?"


def is_media(f):
    fid = f.get("format_id")
    if not fid or BAD_ID.search(str(fid)):
        return False
    if f.get("ext") == "mhtml" or f.get("protocol") == "mhtml":
        return False
    if str(f.get("format_note", "")).lower() == "storyboard":
        return False
    return True


def classify(f):
    vc, ac = f.get("vcodec"), f.get("acodec")
    hv = vc not in (None, "none")
    ha = ac not in (None, "none")
    if vc == "none" and ac is None:
        ha = True
    if ac == "none" and vc is None:
        hv = True
    if vc is None and ac is None:
        if f.get("height") or f.get("width"):
            return "mux"
        if f.get("abr") or f.get("ext") in AUD_EXT:
            return "aud"
        return "mux"
    if hv and ha:
        return "mux"
    if hv:
        return "vid"
    if ha:
        return "aud"
    return None


def size_of(f, dur):
    n = f.get("filesize") or f.get("filesize_approx")
    if not n and f.get("tbr") and dur:
        n = f["tbr"] * 1000 / 8.0 * dur
    return n


def apple_v(f):
    """Video nativo de Apple: H.264/HEVC en mp4/m4v/mov."""
    return fam_v(f.get("vcodec")) in ("avc1", "hevc") and (f.get("ext") or "") in ("mp4", "m4v", "mov")


def apple_a(f):
    """Audio nativo de Apple: AAC/ALAC/MP3/AC-3/E-AC-3/FLAC/WAV."""
    return fam_a(f.get("acodec")) in ("aac", "alac", "mp3", "ac3", "eac3", "flac", "wav") \
        and (f.get("ext") or "") in ("m4a", "mp4", "mp3", "aac", "caf", "flac", "wav", "m4v", "mov")


def build_menu(info, merge_ok, vmax=60, tmax=20, apple_first=False):
    """Todo lo encontrado (sin deduplicar). El numero va primero: el atajo lo usa de indice.
    vmax/tmax=None: sin tope. apple_first: lo Apple nativo ( ) antes que lo demas (dentro de cada grupo, por resolucion)."""
    dur = info.get("duration")
    fmts = [f for f in (info.get("formats") or []) if is_media(f)]
    if not fmts and info.get("url"):
        return {
            "video_labels": ["1 · best · %s" % (info.get("ext") or "")],
            "video_ids": ["best"], "video_audio_step": ["none"],
            "track_labels": [], "track_ids": [], "extra_menu": {},
        }

    def a_rank(f):
        note = str(f.get("format_note", "")).lower()
        orig = 1 if ("original" in note or "default" in note) else 0
        return (-orig, -(f.get("language_preference") or 0), 0 if apple_a(f) else 1,
                -(f.get("abr") or f.get("tbr") or 0))

    # Una sola pista por idioma: la mejor Apple nativa; si no hay ninguna, la de mayor calidad.
    # Sin idioma informado: una por familia de codec.
    best = {}
    for f in fmts:
        if classify(f) != "aud":
            continue
        lang = (f.get("language") or "").lower()
        key = lang or ("?", fam_a(f.get("acodec")))
        sc = (1 if apple_a(f) else 0, f.get("abr") or f.get("tbr") or 0)
        if key not in best or sc > best[key][0]:
            best[key] = (sc, f)
    tracks = sorted([x[1] for x in best.values()], key=a_rank)[:tmax]
    t_labels, t_ids = [], []
    for i, f in enumerate(tracks, 1):
        note = str(f.get("format_note", "")).lower()
        parts = [str(i)]
        if apple_a(f):
            parts.append(APPLE)
        parts += [f.get("language") or "–", fam_a(f.get("acodec")), f.get("ext") or ""]
        if f.get("abr") or f.get("tbr"):
            parts.append("%dk" % round(f.get("abr") or f.get("tbr")))
        sz = fmt_size(size_of(f, dur))
        if sz:
            parts.append(sz)
        if "original" in note:
            parts.append("★")
        t_labels.append(" · ".join(p for p in parts if p))
        t_ids.append(str(f["format_id"]))

    cand = []
    for f in fmts:
        k = classify(f)
        if k == "mux" or (k == "vid" and merge_ok):
            ap = apple_v(f) and (k == "vid" or apple_a(f) or f.get("acodec") is None)
            cand.append((f, k, ap))
    cand.sort(key=lambda t: ((0 if t[2] else 1) if apple_first else 0,
                             -(t[0].get("height") or 0), -((t[0].get("fps") or 0) > 30),
                             0 if t[2] else 1, V_ORDER.get(fam_v(t[0].get("vcodec")), 9),
                             0 if t[1] == "mux" else 1, -(t[0].get("tbr") or 0)))
    v_labels, v_ids, v_steps = [], [], []
    n = 0
    for f, k, ap in cand[:vmax]:
        n += 1
        h = f.get("height")
        res = ("%dp" % h + ("%d" % f["fps"] if (f.get("fps") or 0) > 30 else "")) if h \
            else (f.get("resolution") or f.get("format_note") or "video")
        parts = [str(n)]
        if ap:
            parts.append(APPLE)
        parts += [res, f.get("ext") or "", fam_v(f.get("vcodec"))]
        if k == "mux":
            parts.append("🔊")
        if f.get("tbr"):
            parts.append("%dk" % round(f["tbr"]))
        sz = fmt_size(size_of(f, dur))
        if sz:
            parts.append(sz)
        v_labels.append(" · ".join(p for p in parts if p))
        vid = str(f["format_id"])
        if k == "mux" or not tracks:
            v_ids.append(vid)
            v_steps.append("none")
        elif len(tracks) == 1:
            v_ids.append("%s~%s" % (vid, t_ids[0]))     # "~" = "+" (el atajo decodifica el "+")
            v_steps.append("none")
        else:
            v_ids.append(vid)
            v_steps.append("full")

    if tracks:                                           # entrada "solo audio"
        n += 1
        if len(tracks) == 1:
            t = tracks[0]
            parts = [str(n)] + ([APPLE] if apple_a(t) else []) + ["🎵 audio", t.get("ext") or "",
                                                                  fmt_size(size_of(t, dur))]
            v_labels.append(" · ".join(p for p in parts if p))
            v_ids.append("audio:%s" % t_ids[0])
            v_steps.append("none")
        else:
            v_labels.append("%d · 🎵 audio" % n)
            v_ids.append("audio")
            v_steps.append("one")

    extra = {}
    if len(tracks) > 1:
        for i in range(1, len(tracks) + 1):
            extra[str(i)] = [l for j, l in enumerate(t_labels, 1) if j != i]
    return {
        "video_labels": v_labels, "video_ids": v_ids, "video_audio_step": v_steps,
        "track_labels": t_labels, "track_ids": t_ids, "extra_menu": extra,
    }


def silent(fn, *a, **k):
    warnings.filterwarnings("ignore")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        return fn(*a, **k)


def extract(yt, url, sock=25, deadline=None):
    log = _Log()
    log.deadline = deadline
    o = {"quiet": True, "no_warnings": True, "logger": log, "skip_download": True,
         "noplaylist": True, "extract_flat": "in_playlist", "socket_timeout": sock}
    with yt.YoutubeDL(o) as y:
        return y.extract_info(url, download=False)


def is_playlist(info):
    return info.get("_type") in ("playlist", "multi_video") or "entries" in info


# ------------------------------------------------------------- descarga
def cache_hours():
    try:
        return max(0.0, float(CFG["CACHE_H"]))
    except ValueError:
        return 24.0


def sweep_cache(hours):
    """Borra de dlpy_files/_cache las carpetas de enlaces sin uso en mas de `hours` horas."""
    root = os.path.join(out_dir(), "_cache")
    try:
        names = os.listdir(root)
    except OSError:
        return
    limit = time.time() - hours * 3600
    for n in names:
        p = os.path.join(root, n)
        try:
            if os.path.isdir(p) and os.path.getmtime(p) < limit:
                shutil.rmtree(p, ignore_errors=True)
        except OSError:
            pass


def work_dir(url):
    """Carpeta estable por enlace: yt-dlp reutiliza ahi las pistas ya bajadas."""
    d = os.path.join(out_dir(), "_cache", hashlib.md5(url.encode("utf-8")).hexdigest()[:10])
    os.makedirs(d, exist_ok=True)
    os.utime(d, None)
    return d


def place(path, mode):
    """Mueve el resultado a dlpy_files; si ya existe: new = 'nombre (2)', replace = reemplaza."""
    dest = os.path.join(out_dir(), os.path.basename(path))
    if os.path.exists(dest) and mode != "replace":
        stem, ext = os.path.splitext(dest)
        n = 2
        while os.path.exists("%s (%d)%s" % (stem, n, ext)):
            n += 1
        dest = "%s (%d)%s" % (stem, n, ext)
    os.replace(path, dest)
    return dest


# ---------------------------------------------------------------- animaciones (modulo opcional)
_ANIM = {"mod": None, "tried": False}


def module_dirs():
    """Donde buscar modulos: modules/ junto a este archivo y dlpy_files/_modules/ (donde se bajan)."""
    dirs = []
    try:
        dirs.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules"))
    except NameError:
        pass
    dirs.append(os.path.join(base_dir(), "_modules"))
    return dirs


def module_index():
    """index.json de MODULES_URL ({nombre: {version, api, sha256}}) o None (sin red o formato raro)."""
    try:
        idx = json.loads(http_get(CFG["MODULES_URL"].rstrip("/") + "/index.json", 6).decode("utf-8"))
        return idx if isinstance(idx, dict) else None
    except Exception:
        return None


def module_download(name, api, idx=None):
    """Baja <MODULES_URL>/<name>.py a dlpy_files/_modules/ si index.json (`idx`, o el de la red) lo trae con la api esperada y el
    sha256 coincide (y compila). True si quedo instalado; si algo falla, el archivo que hubiera se conserva."""
    base = CFG["MODULES_URL"].rstrip("/") + "/"
    try:
        info = (idx or module_index())[name]
        want = str(info["sha256"]).lower()
        if info.get("api") != api or not re.fullmatch(r"[0-9a-f]{64}", want):
            return False
        raw = http_get(base + name + ".py", 20, 4000000)
        if not raw or hashlib.sha256(raw).hexdigest() != want:
            return False
        compile(raw, name + ".py", "exec")
        d = os.path.join(base_dir(), "_modules")
        os.makedirs(d, exist_ok=True)
        dst = os.path.join(d, name + ".py")
        with open(dst + ".tmp", "wb") as f:
            f.write(raw)
        os.replace(dst + ".tmp", dst)
        return True
    except Exception:
        return False


MODULE_APIS = {"dlpy_anim": ANIM_API}      # modulos que conoce este host y la API que espera de cada uno


def update_modules(install=False):
    """Pone al dia los modulos de dlpy_files/_modules/: los instalados cuyo sha256 difiere del de index.json (con `install`, tambien
    baja los que faltan). (consultado, [nombres actualizados]); consultado=False si no se pudo leer index.json."""
    idx = module_index()
    if idx is None:
        return False, []
    d = os.path.join(base_dir(), "_modules")
    names = list(MODULE_APIS)
    try:
        names += sorted(f[:-3] for f in os.listdir(d) if f.endswith(".py") and re.fullmatch(r"\w+", f[:-3]) and f[:-3] not in MODULE_APIS)
    except OSError:
        pass
    done = []
    for name in names:
        api = MODULE_APIS.get(name) or (idx.get(name) or {}).get("api")
        p = os.path.join(d, name + ".py")
        try:
            if os.path.isfile(p):
                with open(p, "rb") as f:
                    if hashlib.sha256(f.read()).hexdigest() == str(idx[name]["sha256"]).lower():
                        continue
            elif not install:
                continue
            if module_download(name, api, idx):
                done.append(name)
        except Exception:
            continue
    return True, done


def check_modules(quiet=True, force=False, install=False):
    """update_modules + aviso: dice los actualizados; con `force` tambien que estan al dia o que no se pudo consultar."""
    checked, done = update_modules(install)
    if quiet:
        return
    if done:
        print(tr("🧩 Módulos actualizados: {m}", m=", ".join(done)))
    elif force:
        print(tr("✅ Módulos al día.") if checked else tr("⚠️ No se pudo consultar los módulos."))


def pip_version(name):
    """Version instalada del paquete de pip `name` o None."""
    try:
        import importlib.metadata as md
        importlib.invalidate_caches()
        return md.version(name)
    except Exception:
        return None


def _vnum(s):
    m = re.match(r"\d+(?:\.\d+)*", str(s or ""))
    return tuple(int(x) for x in m.group(0).split(".")) if m else None


def pypi_latest(name):
    """Ultima version estable de `name` en PyPI o None (sin red o no existe)."""
    try:
        return str(json.loads(http_get("https://pypi.org/pypi/%s/json" % name, 6).decode("utf-8"))["info"]["version"])
    except Exception:
        return None


def update_deps(install=False, quiet=True):
    """Pone al dia los paquetes de CFG[\"DEPS\"]: pip install -U solo si PyPI trae algo mas nuevo que lo instalado (con `install`,
    tambien instala los que faltan). (consultado, [(nombre, antes, despues)], [fallidos]); consultado=False si PyPI no respondio."""
    import shlex
    seen, done, bad = False, [], []
    for name in [x for x in CFG["DEPS"].split(",") if DEP_RE.match(x)]:
        have = pip_version(name)
        if have is None and not install:
            continue
        last = pypi_latest(name)
        if last is None:
            continue
        seen = True
        a, b = _vnum(have), _vnum(last)
        if have is not None and (have == last or (a and b and a >= b)):
            continue
        os.system("pip install -q -U %s%s" % (shlex.quote(name), " >/dev/null 2>&1" if quiet else ""))
        now = pip_version(name)
        if now is not None and now != have:
            done.append((name, have, now))
        else:
            bad.append(name)
    return seen, done, bad


def check_deps(quiet=True, force=False, install=False):
    seen, done, bad = update_deps(install, quiet)
    if quiet:
        return
    if done:
        print(tr("📦 Dependencias actualizadas: {d}", d=", ".join("%s %s → %s" % (n, a or "-", b) for n, a, b in done)))
    if bad and force:
        print(tr("⚠️ No se pudo actualizar: {d}", d=", ".join(bad)))
    if force and not done and not bad:
        print(tr("✅ Dependencias al día.") if seen else tr("⚠️ No se pudo consultar las dependencias."))


def check_extras(quiet=True, force=False, install=False):
    """Modulos y dependencias: nunca detiene el script."""
    for fn in (check_modules, check_deps):
        try:
            fn(quiet, force, install)
        except Exception:
            pass


def _load_module(path):
    """dlpy_anim.py de `path` ya configurado, o None (no carga o su API no es la que espera este host)."""
    try:
        spec = importlib.util.spec_from_file_location("dlpy_anim", path)
        m = importlib.util.module_from_spec(spec)
        sys.modules["dlpy_anim"] = m
        spec.loader.exec_module(m)
        if getattr(m, "API", None) != ANIM_API:   # otro contrato: mejor la barra simple que fallar a medias
            raise ImportError("API")
        m.configure(tr=tr, lang=CFG["LANG"], version=VERSION)
        return m
    except Exception:
        sys.modules.pop("dlpy_anim", None)
        return None


def load_anim():
    """Carga dlpy_anim.py (modules/ junto a este archivo o dlpy_files/_modules/; si no esta, lo baja). None si esta
    apagado, falta o falla."""
    if _ANIM["tried"]:
        return _ANIM["mod"]
    _ANIM["tried"] = True
    try:
        if CFG["ANIM"] != "1" or not sys.stdout.isatty():
            return None
    except Exception:
        return None
    for attempt in (0, 1):
        for d in module_dirs():
            p = os.path.join(d, "dlpy_anim.py")
            if os.path.isfile(p):
                m = _load_module(p)
                if m:
                    _ANIM["mod"] = m
                    return m
        if attempt == 0 and not module_download("dlpy_anim", ANIM_API):
            break
    return None


def anim_ui(url, fmt, audio_only):
    """AnimUI para una descarga, o None (sin modulo, sin color o escena imposible): entonces manda la barra simple."""
    if LONG:
        return None          # --long: nada de ANSI en la salida; el avance va por `progress`
    m = load_anim()
    try:
        if m is None or not m.available():
            return None
        total = 1 if audio_only else max(1, (fmt or "").split("/")[0].count("+") + 1)
        return m.AnimUI(url, total=total, audio_only=audio_only)
    except Exception:
        return None


def download(yt, url, fmt, merge="mp4", multi=False, audio_only=False, show=True,
             audio_fmt="native", cache_h=24.0, dup="new", ui=None):
    """ui: AnimUI opcional (lo cierra quien lo creo); si no arranca la escena, se usa la barra simple."""
    sweep_cache(cache_h)
    outdir = work_dir(url)
    last = [0.0]
    scene = bool(ui and show and ui.begin())

    def hook(d):
        if LONG:
            return long_hook(d)
        if not show:
            return
        if scene:
            return ui.hook(d)
        st = d.get("status")
        if st == "downloading":
            now = time.time()
            if now - last[0] < 0.7:
                return
            last[0] = now
            tot = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            done = d.get("downloaded_bytes") or 0
            pct = "%5.1f%%" % (done * 100.0 / tot) if tot else fmt_size(done)
            sp = d.get("speed")
            eta = d.get("eta")
            sys.stdout.write("\r⬇️ %s %s %s      " % (
                pct, (fmt_size(sp) + "/s") if sp else "", ("ETA " + fmt_dur(eta)) if eta else ""))
            sys.stdout.flush()
        elif st == "finished":
            sys.stdout.write("\r" + " " * 50 + "\r")
            print(tr("⚙️ Procesando…"))

    o = {
        "format": fmt,
        "outtmpl": os.path.join(outdir, "%(id)s.%(ext)s"),
        "noplaylist": True, "quiet": True, "no_warnings": True, "noprogress": True,
        "logger": _Log(), "progress_hooks": [hook], "retries": 5, "fragment_retries": 5,
        "socket_timeout": 25, "trim_file_name": 150, "keepvideo": cache_h > 0, "allow_multiple_audio_streams": bool(multi),
        "merge_output_format": merge if merge in ("mp4", "mkv") else "mp4",
    }
    if scene:
        o["postprocessor_hooks"] = [ui.pp_hook]
    elif LONG:
        o["postprocessor_hooks"] = [long_pp_hook]
    if audio_only and audio_fmt in ("mp3", "m4a"):
        o["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": audio_fmt,
                                "preferredquality": "192"}]
    with yt.YoutubeDL(o) as y:
        info = y.extract_info(url, download=True)
        rd = info.get("requested_downloads") or []
        path = (rd[0].get("filepath") if rd else None) or info.get("filepath") or y.prepare_filename(info)
    if path and not os.path.exists(path):          # extension cambiada por el postproceso
        stem = os.path.splitext(path)[0]
        for ext in ("mp4", "mkv", "mp3", "m4a", "webm", "opus"):
            if os.path.exists(stem + "." + ext):
                path = stem + "." + ext
                break
    # nombre final simple y seguro (el atajo decodifica % y +, el shell interpreta $ ` ! \\)
    if path and os.path.exists(path):
        ext = os.path.splitext(path)[1].lower()
        new = os.path.join(os.path.dirname(path), safe_title(info.get("title"), 60, safe_title(str(info.get("id") or ""), 60)) + ext)
        if new != path:
            os.replace(path, new)
            path = new
    if path and os.path.exists(path):
        path = place(path, dup)
    if cache_h <= 0:
        shutil.rmtree(outdir, ignore_errors=True)
    return path, safe_title(info.get("title"), 60, "") or os.path.basename(path or "")


def open_shortcut(path):
    """Devuelve el archivo al atajo (que lo previsualiza)."""
    if CFG["CALLBACK"] != "1" or not path or not os.path.exists(path):
        return
    fp = shared_path(path)
    print("📎 " + fp)
    payload = json.dumps({"file_path": fp, "file_title": os.path.basename(path)},
                         ensure_ascii=True, separators=(",", ":"))
    url = "shortcuts://run-shortcut?name=%s&input=text&text=%s" % (
        urllib.parse.quote(SHORTCUT_NAME, safe=""), urllib.parse.quote(payload, safe=""))
    try:
        os.system('open "%s"' % url)
    except Exception:
        pass


def finish(path):
    print(tr("✅ Listo"))
    print(tr("📁 Guardado en: {p}", p=path))
    open_shortcut(path)


# ------------------------------------------------------------- comandos
def cmd_idiomas():
    langs = list_langs()
    jprint({
        "lang_title": tr("Idioma del script"),
        "lang_labels": [l for _, l in langs],
        "lang_map": {l: c for c, l in langs},
        "lang_set_map": {c: tr_in(c, "✅ Idioma del script: {lang}", lang=lang_name(c))
                         for c, _l in langs},
    })


def cmd_config(args):
    if args:
        for a in args:
            if "=" not in a:
                continue
            k, v = a.split("=", 1)
            k = k.strip().upper()
            if k.startswith("DLPY_"):
                k = k[5:]
            if k in CFG:
                ok, nv = valid_cfg(k, v)
                if ok:
                    CFG[k] = nv
                else:
                    print(tr("⚠️ Valor no válido para {k}: {v}", k=k, v=v.strip()))
        save_cfg()
        if CFG["LANG"] != BASE_LANG and not lang_installed(CFG["LANG"]):
            lang_download(CFG["LANG"])
        return
    while True:
        print("\n" + tr("⚙️ Configuración de DLpy (script {v})", v=VERSION))
        items = [("LANG", tr("Idioma")),
                 ("LANG_URL", tr("URL de idiomas (GitHub)")),
                 ("MODULES_URL", tr("URL de módulos (GitHub)")),
                 ("DIR", tr("Carpeta de descargas")),
                 ("MERGE", tr("Contenedor de video (auto/mp4/mkv)")),
                 ("AUDIO", tr("Formato de audio (native/mp3/m4a)")),
                 ("FFMPEG", tr("ffmpeg (auto/yes/no)")),
                 ("DUP", tr("Si el archivo ya existe (new/replace)")),
                 ("CACHE_H", tr("Horas de caché de pistas (0 = sin caché)")),
                 ("PATH", tr("Ruta enviada al atajo (abs/home/rel)")),
                 ("ANIM", tr("Animaciones (1/0)")),
                 ("DEPS", tr("Dependencias de pip al día (separadas por coma)")),
                 ("TOOLTAG", tr("Escribir DLpy en el software de codificación (1/0)")),
                 ("UPDATE", tr("Buscar actualización de DLpy cada semana (1/0)"))]
        for i, (k, lab) in enumerate(items, 1):
            print(" %d. %s: %s" % (i, lab, CFG[k]))
        print(" %d. %s" % (len(items) + 1, tr("Actualizar yt-dlp")))
        print(" %d. %s" % (len(items) + 2, tr("Actualizar idiomas")))
        print(" %d. %s" % (len(items) + 3, tr("Actualizar módulos")))
        print(" %d. %s" % (len(items) + 4, tr("Actualizar dependencias")))
        print(" 0. %s" % tr("Salir"))
        try:
            n = int(input(tr("Número") + ": ").strip() or 0)
        except (ValueError, EOFError):
            return
        if n == 0:
            return
        if n == len(items) + 1:
            cmd_update()
        elif n == len(items) + 2:
            cmd_update_langs([])
        elif n == len(items) + 3:
            cmd_update_modules()
        elif n == len(items) + 4:
            cmd_update_deps()
        elif 1 <= n <= len(items):
            k = items[n - 1][0]
            if k == "LANG":
                langs = list_langs()
                have = {c for c, _l in langs}
                langs += [(c, "⬇️ " + l) for c, l in remote_langs() if c not in have]
                for i, (c, l) in enumerate(langs, 1):
                    print(" %d. %s" % (i, l))
                try:
                    code = langs[int(input(tr("Número") + ": ")) - 1][0]
                except (ValueError, IndexError, EOFError):
                    print(tr("Opción no válida."))
                    continue
                if code != BASE_LANG and not lang_installed(code):
                    print(tr("⬇️ Descargando idioma…"))
                    if not lang_download(code):
                        print(tr("⚠️ No se pudo descargar el idioma (sin internet o archivo no encontrado)."))
                        continue
                CFG["LANG"] = code
            else:
                nv = input(tr("Nuevo valor: ")).strip()
                ok, nv = valid_cfg(k, nv) if nv else (False, "")
                if not ok:
                    print(tr("Opción no válida."))
                    continue
                CFG[k] = nv
            save_cfg()
            print(tr("✅ Guardado."))


REPO = "ElDelDLpy/DLpy"
UPDATE_DAYS = 7


def vtuple(s):
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", str(s))
    return tuple(int(x) for x in m.groups()) if m else None


def update_due(set_next=None):
    """Sin argumento: instante (epoch) desde el que toca consultar. Con `set_next`: lo guarda (dlpy_files/_update.json)."""
    p = os.path.join(base_dir(), "_update.json")
    if set_next is None:
        try:
            with open(p, encoding="utf-8") as f:
                return float(json.load(f).get("next", 0))
        except Exception:
            return 0.0
    try:
        os.makedirs(base_dir(), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"next": set_next}, f)
    except OSError:
        pass


def fetch_update():
    """(consultado, version, codigo): consultado=False si no se pudo hablar con GitHub; version/codigo solo si hay un Release MAS NUEVO
    y verificado (sha256, compila, #!dlpy.py y VERSION igual a la del tag)."""
    try:
        rel = json.loads(http_get("https://api.github.com/repos/%s/releases/latest" % REPO, 5).decode("utf-8"))
        tag = str(rel["tag_name"])
        new = vtuple(tag)
    except Exception:
        return False, None, None
    if not new or new <= vtuple(VERSION):
        return True, None, None
    try:
        urls = {a.get("name"): str(a.get("browser_download_url") or "") for a in rel.get("assets") or []}
        pre = "https://github.com/%s/releases/download/%s/" % (REPO, tag)
        u = urls.get("dlpy.py") or pre + "dlpy.py"
        us = urls.get("dlpy.py.sha256") or ""
        if not u.startswith("https://github.com/") or (us and not us.startswith("https://github.com/")):
            return False, None, None
        raw = http_get(u, 30, 4000000)
        sha = (http_get(us, 6).decode("utf-8", "ignore") if us else "") or str(rel.get("body") or "")
        m = re.search(r"\b[0-9a-fA-F]{64}\b", sha)
        if not raw or not m or hashlib.sha256(raw).hexdigest() != m.group(0).lower():
            return False, None, None
        compile(raw, "dlpy.py", "exec")
        v = re.search(rb'(?m)^VERSION = "(\d+\.\d+\.\d+)"', raw)
        if not raw.startswith(b"#!dlpy.py") or not v or vtuple(v.group(1).decode()) != new:
            return False, None, None
        return True, ".".join(map(str, new)), raw
    except Exception:
        return False, None, None


def self_update(argv, quiet=True, force=False):
    """Busca (cada UPDATE_DAYS dias, o ya con `force`) un Release nuevo; si lo hay, reescribe este archivo y SIGUE con la version nueva
    (runpy, mismos argumentos). True si corrio la nueva (quien llama termina). quiet: sin prints (salidas JSON)."""
    if os.environ.pop("DLPY_EXTCHECK", None):      # el host anterior se acaba de actualizar: este revisa modulos y dependencias
        check_extras(quiet)
    if not force and (CFG["UPDATE"] != "1" or os.environ.get("DLPY_NOUPDATE") or time.time() < update_due()):
        return False
    checked, ver, raw = fetch_update()
    update_due(time.time() + (UPDATE_DAYS if checked else 1) * 86400)     # sin red: reintenta manana
    if not raw:
        if force:
            print(tr("✅ DLpy está al día ({v}).", v=VERSION) if checked else tr("⚠️ No se pudo consultar o verificar la actualización."))
        if checked:
            check_extras(quiet, force)
        return False
    try:
        path = os.path.abspath(__file__)
        bk = os.path.join(base_dir(), "_backups")
        os.makedirs(bk, exist_ok=True)
        if not quiet:
            print(tr("🔄 Nueva versión {v} (tienes {o}): actualizando…", v=ver, o=VERSION))
        shutil.copy2(path, os.path.join(bk, "dlpy_%s.py" % VERSION))
        with open(path + ".tmp", "wb") as f:
            f.write(raw)
        os.replace(path + ".tmp", path)
    except (OSError, NameError) as e:
        if not quiet:
            print(tr("⚠️ No se pudo actualizar DLpy: {e}", e=clean_err(e)))
        return False
    if not quiet:
        print(tr("✅ DLpy actualizado a {v}.", v=ver))
    os.environ["DLPY_NOUPDATE"] = "1"
    os.environ["DLPY_EXTCHECK"] = "1"
    sys.argv = [path] + list(argv[1:])
    import runpy
    runpy.run_path(path, run_name="__main__")
    return True


def cmd_update():
    print(tr("🔄 Actualizando yt-dlp…"))
    os.system("pip install -q -U yt-dlp")


def cmd_update_modules():
    print(tr("🧩 Actualizando módulos…"))
    check_modules(False, True, True)


def cmd_update_deps():
    print(tr("📦 Actualizando dependencias…"))
    check_deps(False, True, True)


def cmd_update_langs(codes):
    """Re-baja los .po instalados, o solo `codes` (que tambien instala los que falten)."""
    codes = [c for c in codes if LANG_RE.match(c) and c != BASE_LANG]
    if not codes:
        codes = [c for c, _l in list_langs() if c != BASE_LANG]
    if not codes:
        return print(tr("No hay idiomas instalados."))
    print(tr("🌐 Actualizando idiomas…"))
    bad = 0
    for c in codes:
        ok = lang_download(c)
        bad += not ok
        print(" %s %s" % ("✅" if ok else "⚠️", c))
    if bad:
        print(tr("⚠️ No se pudo descargar el idioma (sin internet o archivo no encontrado)."))


def make_payload(info, url, vmax=60, tmax=20, apple_first=False):
    menu = build_menu(info, can_merge(CFG["FFMPEG"]), vmax, tmax, apple_first)
    if not menu["video_ids"]:
        return {"ok": False, "error": tr("No se encontraron formatos descargables.")}
    head = "🎬 %s" % safe_title(info.get("title"), 50, "")  if info.get("title") else "🎬 %s" % url
    bits = [fmt_dur(info.get("duration")), info.get("uploader") or info.get("channel") or ""]
    out = {"ok": True, "link": url, "prompt": " · ".join([head] + [b for b in bits if b])}
    out.update(menu)
    return out


def analyze(yt, url, sock, vmax=60, tmax=20, deadline=None, apple_first=False):
    """(payload, info). payload = dict para el atajo; info = datos de yt-dlp (None si no hay).
    Con `deadline` lanza _Deadline si se pasa de ese instante."""
    info = extract(yt, url, sock, deadline)
    if not info:
        return {"ok": False, "error": tr("No se encontraron formatos descargables.")}, None
    if is_playlist(info):
        return {"ok": True, "use_scb": True, "reason": "playlist"}, info
    if info.get("is_live"):
        return {"ok": False, "error": tr("Las transmisiones en vivo no se pueden descargar.")}, info
    return make_payload(info, url, vmax, tmax, apple_first), info


def long_scm(url):
    """--scm --long: como --scm pero sin limite de tiempo (Execute Long Command). Instala yt-dlp si falta.
    Devuelve el JSON shortcutmode COMPLETO (sin topes de videos/pistas, lo Apple nativo primero); solo las listas de reproduccion piden --scb (menus en la terminal)."""
    warnings.filterwarnings("ignore")
    buf = io.StringIO()

    def out(d):
        d2 = {"dlpy": "shortcutmode"}
        d2.update(d)
        _PG["emitted"] = True
        _OUT.write(json.dumps(d2, ensure_ascii=False, separators=(",", ":")) + "\n")
        _OUT.flush()

    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            url = clean_url(url)
            if not url:
                return out({"ok": False, "error": tr("No se encontró un enlace válido.")})
            prog("--title", "DLpy")
            prog("--indeterminate")
            yt = import_ytdlp(True)
            if yt is None:
                return out({"ok": False, "error": tr("No se pudo instalar yt-dlp. Revisa tu conexión.")})
            return out(analyze(yt, url, 25, vmax=None, tmax=None, apple_first=True)[0])
    except Exception as e:
        out({"ok": False, "error": tr("No se pudo leer el enlace: {e}", e=clean_err(e))})
    finally:
        if not _PG["emitted"]:
            out({"ok": False, "error": "?"})


def cmd_scm(url):
    """Rapido: maximo SCM_LIMIT segundos. Si no alcanza, pide al atajo usar --scb."""
    if LONG:
        return long_scm(url)

    def out(d):
        d2 = {"dlpy": "shortcutmode"}
        d2.update(d)
        jprint(d2)

    url = clean_url(url)
    if not url:
        return out({"ok": False, "error": tr("No se encontró un enlace válido.")})
    yt = import_ytdlp(False)
    if yt is None:
        return out({"ok": True, "use_scb": True, "reason": "install"})
    # Sin hilos: en a-Shell, os._exit(0) con un hilo aun dentro de yt-dlp daba "segmentation fault".
    # El limite se comprueba en cada mensaje de yt-dlp (_Log); un socket colgado puede pasarse hasta socket_timeout (4 s).
    deadline = max(START + SCM_LIMIT - 0.4, time.time() + 0.3)
    try:
        res = silent(analyze, yt, url, 4, deadline=deadline)[0]
    except _Deadline:
        return out({"ok": True, "use_scb": True, "reason": "timeout"})
    except Exception as e:
        if time.time() > deadline:       # fallo tardio (p. ej. socket vencido pasado el limite): que lo intente --scb
            return out({"ok": True, "use_scb": True, "reason": "timeout"})
        return out({"ok": False, "error": tr("No se pudo leer el enlace: {e}", e=clean_err(e))})
    out(res)


def _safe(o):
    """El atajo decodifica el texto recibido: neutralizar % y + dentro de los textos."""
    if isinstance(o, str):
        return o.replace("%", "％").replace("+", "＋")
    if isinstance(o, list):
        return [_safe(x) for x in o]
    if isinstance(o, dict):
        return {k: _safe(v) for k, v in o.items()}
    return o


def open_shortcut_text(text):
    url = "shortcuts://run-shortcut?name=%s&input=text&text=%s" % (
        urllib.parse.quote(SHORTCUT_NAME, safe=""), urllib.parse.quote(text, safe=""))
    try:
        os.system('open "%s"' % url)
    except Exception:
        pass
    return len(url)


def start(url=""):
    """Arranque comun de --scb y modo terminal: (url, yt) o (None, None) si falta algo."""
    url = clean_url(url)
    if not url:
        try:
            url = clean_url(input(tr("🔗 Pega el enlace: ")))
        except EOFError:
            return None, None
    if not url:
        print(tr("No se encontró un enlace válido."))
        return None, None
    yt = import_ytdlp(True)
    return (url, yt) if yt else (None, None)


def cmd_scb(url=""):
    """Igual que --scm pero sin limite de tiempo; luego manda el JSON al atajo."""
    url, yt = start(url)
    if not url:
        return
    print("🔎 …")
    try:
        payload, info = analyze(yt, url, 25)
    except Exception as e:
        payload, info = {"ok": False, "error": tr("No se pudo leer el enlace: {e}", e=clean_err(e))}, None
    if payload.get("use_scb"):                 # lista de reproduccion: menus en la terminal
        return interactive_playlist(yt, info, url)
    vmax, tmax = 60, 20
    while True:
        d = {"dlpy": "shortcutmode"}
        d.update(_safe(payload))
        text = json.dumps(d, ensure_ascii=True, separators=(",", ":"))
        if len(urllib.parse.quote(text, safe="")) < 45000 or not info or vmax <= 10:
            break
        vmax, tmax = vmax // 2, max(4, tmax // 2)    # URL demasiado larga: reducir
        payload = make_payload(info, url, vmax, tmax)
    print(tr("📲 Enviando las opciones al atajo…"))
    open_shortcut_text(text)


def parse_pick(p):
    m = re.match(r"\s*V=([^,]*),A=([^,]*),X=(.*)$", p or "", re.S)
    if not m:
        return None
    return m.group(1).strip(), m.group(2).strip(), m.group(3).strip()


MP4_AUDIO = ("aac", "mp3", "ac3", "eac3", "alac")


def formats_by_id(yt, url):
    try:
        info = extract(yt, url, 25) or {}
        _PG["dur"] = info.get("duration")
        return {str(f.get("format_id")): f for f in (info.get("formats") or [])}
    except Exception:
        return {}


def pick_container(by, fmt, mode="auto"):
    """auto: mp4 si todo lo elegido cabe en mp4 y es compatible con Apple; si no, mkv."""
    mode = (mode or "auto").lower()
    if mode in ("mp4", "mkv"):
        return mode
    if not by:
        return "mkv"
    for i in [p for p in fmt.split("+") if p]:
        f = by.get(i)
        if f is None:
            continue
        k = classify(f)
        if k in ("vid", "mux") and fam_v(f.get("vcodec")) not in ("avc1", "hevc"):
            return "mkv"
        if k in ("aud", "mux") and fam_a(f.get("acodec")) not in MP4_AUDIO:
            return "mkv"
    return "mp4"


def run_ffmpeg(args, out):
    """ffmpeg por subprocess; si no se puede, por os.system (a-Shell). (ok, error)."""
    err = ""
    try:
        r = subprocess.run(args, capture_output=True)
        if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 0:
            return True, ""
        err = (r.stderr or b"").decode("utf-8", "ignore").strip()[-200:] or "rc=%s" % r.returncode
    except Exception as e:
        err = clean_err(e)
    try:
        if os.path.exists(out):
            os.remove(out)
        q = lambda a: '"%s"' % re.sub(r'([\\"$`])', r"\\\1", str(a))
        os.system(" ".join(q(a) for a in args))
        if os.path.exists(out) and os.path.getsize(out) > 0:
            return True, ""
    except Exception as e:
        err = clean_err(e)
    return False, err or "ffmpeg"


TOOL_EXT = {".mp4", ".m4v", ".m4a"}


def tool_tag():
    return "DLpy " + VERSION


def tool_args(path):
    """Argumentos de ffmpeg que escriben «Software de codificacion» (©too) en `path`; [] si TOOLTAG=0 o el contenedor no lo admite."""
    if CFG["TOOLTAG"] != "1" or os.path.splitext(path or "")[1].lower() not in TOOL_EXT:
        return []
    return ["-metadata", "encoding_tool=" + tool_tag()]


def read_tool_tag(path):
    """Texto del atom ©too (Software de codificacion) de un mp4/m4v/m4a, \"\" si no lo trae, None si no se pudo leer."""
    import struct
    try:
        with open(path, "rb") as f:
            end = os.fstat(f.fileno()).st_size
            pos = 0
            while pos + 8 <= end:
                f.seek(pos)
                h = f.read(16)
                sz, t = struct.unpack(">I4s", h[:8])
                hs = 8
                if sz == 1 and len(h) == 16:
                    sz, hs = struct.unpack(">Q", h[8:16])[0], 16
                elif sz == 0:
                    sz = end - pos
                if sz < hs:
                    return None
                if t == b"moov":
                    if sz > 64000000:
                        return None
                    f.seek(pos + hs)
                    moov = f.read(sz - hs)
                    j = moov.find(b"\xa9too")
                    if j < 0:
                        return ""
                    n = struct.unpack(">I", moov[j + 4:j + 8])[0]
                    return moov[j + 20:j + 4 + n].decode("utf-8", "ignore") if moov[j + 8:j + 12] == b"data" else ""
                pos += sz
    except Exception:
        pass
    return None


def ensure_tool_tag(path):
    """Si el mp4/m4v/m4a final aun no dice «DLpy <version>» en Software de codificacion, lo remuxa sin recodificar para escribirlo.
    (ok, error): un fallo no toca el archivo."""
    try:
        if not tool_args(path) or not os.path.exists(path) or CFG["FFMPEG"].lower() in ("no", "0", "false"):
            return True, ""
        if read_tool_tag(path) == tool_tag():
            return True, ""
        base, ext = os.path.splitext(path)
        tmp = base + "_tool" + ext
        ok, err = run_ffmpeg([ffmpeg_exe(), "-y", "-v", "error", "-i", "file:" + path, "-map", "0:v?", "-map", "0:a?", "-c", "copy"]
                             + tool_args(tmp) + ["-movflags", "+faststart", tmp], tmp)
        if ok:
            os.replace(tmp, path)
            return True, ""
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass
        return False, err
    except Exception as e:
        return False, clean_err(e)


def tag_audio_tracks(path, labels):
    """Varias pistas de audio: solo la primera queda como predeterminada, todas con
    language=und (si llevan idioma, el reproductor de iOS elige la del idioma del sistema y no
    la principal) y el idioma/nombre solo en title (mkv) o handler_name (mp4). (ok, error)"""
    if len(labels) < 2 or not path or not os.path.exists(path):
        return True, ""
    base, ext = os.path.splitext(path)
    tmp = base + "_tag" + ext
    args = ["ffmpeg", "-y", "-v", "error", "-i", path, "-map", "0:v?", "-map", "0:a?", "-c", "copy"]
    for i, lab in enumerate(labels):
        args += ["-disposition:a:%d" % i, "default" if i == 0 else "0",
                 "-metadata:s:a:%d" % i, "language=und",
                 "-metadata:s:a:%d" % i, "title=%s" % (lab or "Audio %d" % (i + 1))]
        if ext.lower() in (".mp4", ".m4v", ".mov"):
            args += ["-metadata:s:a:%d" % i, "alternate_group=1",
                     "-metadata:s:a:%d" % i, "handler_name=%s" % (lab or "Audio %d" % (i + 1))]
    args += tool_args(tmp)
    args.append(tmp)
    ok, err = run_ffmpeg(args, tmp)
    if ok:
        os.replace(tmp, path)
        return True, ""
    try:
        if os.path.exists(tmp):
            os.remove(tmp)
    except Exception:
        pass
    return False, err


# ------------------------------------------------ compatibilidad con Apple (se revisa SIEMPRE al terminar de bajar)
# Misma idea que el proyecto 2.1.5: el ffmpeg de a-Shell NO trae libx264/libx265, asi que se recodifica con los encoders que
# ESE ffmpeg declare (`ffmpeg -encoders`): hevc_videotoolbox (hardware) -> libx265 -> libkvazaar -> libx264 -> h264_videotoolbox.
A_VCODECS = {"h264", "hevc"}
A_VEXT = {".mp4", ".m4v", ".mov"}
A_AEXT = {".m4a", ".mp3", ".aac", ".flac", ".wav", ".caf", ".mp4", ".m4v", ".mov"}
A_ACODECS_VID = {"aac", "alac", "mp3", "ac3", "eac3"}                  # dentro de mp4/mov
A_ACODECS_AUD = {"aac", "alac", "mp3", "flac", "ac3", "eac3"}          # archivo solo de audio (mas pcm_*)
A_PIX = {"h264": {"yuv420p", "yuvj420p"}, "hevc": {"yuv420p", "yuvj420p", "yuv420p10le"}}
_COVER = {"mjpeg", "png", "bmp", "gif", "webp"}
_ENC_CACHE = {}


class Streams(list):
    """Pistas reales de un archivo (sin portadas); .dur = duracion en segundos o None."""
    dur = None


def ffmpeg_exe():
    return shutil.which("ffmpeg") or "ffmpeg"


def ffprobe_exe():
    d, n = os.path.split(ffmpeg_exe())
    near = os.path.join(d, n.lower().replace("ffmpeg", "ffprobe")) if d else None
    return near if near and os.path.exists(near) else (shutil.which("ffprobe") or "ffprobe")


def run_capture(args):
    """Salida (stdout+stderr) de un comando; subprocess y, si no se puede lanzar, os.system a un archivo (a-Shell). None si falla."""
    try:
        r = subprocess.run(args, capture_output=True, stdin=subprocess.DEVNULL, timeout=60)
        return ((r.stdout or b"") + b"\n" + (r.stderr or b"")).decode("utf-8", "ignore")
    except OSError:
        pass
    except Exception:
        return None
    tmp = os.path.join(DOCS, ".dlpy_probe.txt")
    try:
        q = lambda a: '"%s"' % re.sub(r'([\\"$`])', r"\\\1", str(a))
        os.system(" ".join(q(a) for a in args) + ' > "%s" 2>&1' % tmp)
        with open(tmp, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return None
    finally:
        try:
            os.remove(tmp)
        except Exception:
            pass


def ffmpeg_encoders():
    """Encoders que trae ESTE ffmpeg (una sola lectura). Vacio si no se pudo leer (entonces se prueban todos)."""
    exe = ffmpeg_exe()
    if exe not in _ENC_CACHE:
        have = set()
        for ln in (run_capture([exe, "-hide_banner", "-encoders"]) or "").splitlines():
            p = ln.split()
            if len(p) >= 2 and p[0][:1] in "VAS" and "." in p[0]:
                have.add(p[1])
        _ENC_CACHE[exe] = have
    return _ENC_CACHE[exe]


def pix_bits(pix):
    m = re.search(r"(\d+)(?:le|be)$", pix or "")
    return int(m.group(1)) if m else 8


def _kbps(v):
    try:
        return int(round(int(v) / 1000.0))
    except (TypeError, ValueError):
        return None


def probe_streams(path):
    """Streams (pistas de video/audio reales) o None si no se pudo leer. Cada pista: type, codec, tag, pix, idx, kbps, trc."""
    out = run_capture([ffprobe_exe(), "-v", "error", "-show_entries",
                       "stream=index,codec_type,codec_name,codec_tag_string,pix_fmt,bit_rate,color_transfer:stream_disposition=attached_pic:format=duration",
                       "-of", "json", "file:" + path])
    try:
        j = json.loads(out[out.index("{"):out.rindex("}") + 1])
        res = Streams()
        try:
            res.dur = float((j.get("format") or {}).get("duration")) or None
        except (TypeError, ValueError):
            pass
        for st in j.get("streams", []):
            t = st.get("codec_type")
            if t not in ("video", "audio"):
                continue
            if t == "video" and ((st.get("disposition") or {}).get("attached_pic") or st.get("codec_name") in _COVER):
                continue
            res.append({"type": t, "codec": (st.get("codec_name") or "").lower(), "tag": (st.get("codec_tag_string") or "").lower(),
                        "pix": (st.get("pix_fmt") or "").lower(), "idx": int(st.get("index", len(res))),
                        "kbps": _kbps(st.get("bit_rate")), "trc": (st.get("color_transfer") or "").lower()})
        if res:
            return res
    except Exception:
        pass
    out = run_capture([ffmpeg_exe(), "-hide_banner", "-i", "file:" + path])        # respaldo: leer el texto de `ffmpeg -i`
    if not out:
        return None
    res = Streams()
    dm = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", out)
    if dm:
        res.dur = int(dm.group(1)) * 3600 + int(dm.group(2)) * 60 + float(dm.group(3)) or None
    for ln in out.splitlines():
        m = re.search(r"Stream #0:(\d+)[^:]*(?:\([^)]*\))?: (Video|Audio): (\w+)", ln)
        if not m:
            continue
        t, c = m.group(2).lower(), m.group(3).lower()
        if t == "video" and ("attached pic" in ln or c in _COVER):
            continue
        tag = re.search(r"\((\w{4}) / 0x", ln)
        pix = re.search(r",\s*(yuv\w+|nv\d+|p010\w*|gray\w*|rgb\w*|gbr\w*)", ln)
        kb = re.search(r",\s*(\d+)\s*kb/s", ln)
        trc = re.search(r"smpte2084|arib-std-b67", ln)
        res.append({"type": t, "codec": c, "tag": tag.group(1).lower() if tag else "",
                    "pix": pix.group(1).lower() if pix else "", "idx": int(m.group(1)),
                    "kbps": int(kb.group(1)) if kb else None, "trc": trc.group(0) if trc else ""})
    return res or None


def apple_verdict(path, streams):
    """(ok, plan). plan: {"audio_only", "cont", "v": copy|enc|None, "tag", "a": [copy|enc, ...]} con lo MINIMO a cambiar."""
    ext = os.path.splitext(path)[1].lower()
    vs = [s for s in streams if s["type"] == "video"][:1]
    au = [s for s in streams if s["type"] == "audio"]
    plan = {"audio_only": not vs, "cont": True, "v": None, "tag": False, "a": []}
    if vs:
        v = vs[0]
        plan["cont"] = ext in A_VEXT
        okv = v["codec"] in A_VCODECS and v["pix"] in A_PIX.get(v["codec"], ())
        plan["v"] = "copy" if okv else "enc"
        plan["tag"] = okv and v["codec"] == "hevc" and v["tag"] != "hvc1"   # hev1 no lo reproduce Apple: basta cambiar la etiqueta
        plan["a"] = ["copy" if a["codec"] in A_ACODECS_VID else "enc" for a in au]
    else:
        plan["cont"] = ext in A_AEXT
        plan["a"] = ["copy" if (a["codec"] in A_ACODECS_AUD or a["codec"].startswith("pcm_")) else "enc" for a in au]
        if not au:
            return True, plan                      # sin pistas legibles: no hay nada que convertir
    ok = plan["cont"] and plan["v"] in (None, "copy") and not plan["tag"] and all(x == "copy" for x in plan["a"])
    return ok, plan


def _unique(path):
    if not os.path.exists(path):
        return path
    stem, ext = os.path.splitext(path)
    n = 2
    while os.path.exists("%s (%d)%s" % (stem, n, ext)):
        n += 1
    return "%s (%d)%s" % (stem, n, ext)


HDR_TAGS = {"smpte2084": ("bt2020", "smpte2084", "bt2020nc"), "arib-std-b67": ("bt2020", "arib-std-b67", "bt2020nc")}


def video_attempts(v, size, dur):
    """[(encoder, nombre, opciones)] en orden, solo con encoders de este ffmpeg (si no se pudo leer la lista, todos).
    Calidad 'fast' del proyecto 2.1.5: VideoToolbox al bitrate del origen; x265 veryfast crf 26; x264 veryfast crf 21."""
    ob = 10 if pix_bits(v["pix"]) > 8 else 8                      # Apple reproduce hasta 10 bits
    pix = "yuv420p10le" if ob == 10 else "yuv420p"
    kb = v.get("kbps") or (int(size * 8 / 1000.0 / dur) if size and dur else 4000)
    kb = int(min(30000, max(500, kb)))
    hdr = HDR_TAGS.get(v.get("trc") or "")
    tags, xp = [], []
    if hdr:
        tags = ["-color_primaries", hdr[0], "-color_trc", hdr[1], "-colorspace", hdr[2]]
        xp = ["colorprim=%s" % hdr[0], "transfer=%s" % hdr[1], "colormatrix=%s" % hdr[2]]
    vt = ["-c:v", "hevc_videotoolbox", "-b:v", "%dk" % kb, "-allow_sw", "1", "-tag:v", "hvc1", "-pix_fmt", pix] + tags \
        + (["-profile:v", "main10"] if ob == 10 else [])
    ps = (["profile=main10"] if ob == 10 else []) + xp
    x265 = ["-c:v", "libx265", "-preset", "veryfast", "-crf", "26", "-tag:v", "hvc1", "-pix_fmt", pix] + tags \
        + (["-x265-params", ":".join(ps)] if ps else [])
    kvz = ["-c:v", "libkvazaar", "-kvazaar-params", "qp=22,preset=fast", "-tag:v", "hvc1", "-pix_fmt", "yuv420p"] + tags
    x264 = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-tag:v", "avc1"] + tags
    h264vt = ["-c:v", "h264_videotoolbox", "-b:v", "%dk" % kb, "-allow_sw", "1", "-pix_fmt", "yuv420p", "-tag:v", "avc1"] + tags
    sets = [("hevc_videotoolbox", "VideoToolbox HEVC", vt), ("libx265", "x265", x265)]
    if ob == 8:
        sets.append(("libkvazaar", "Kvazaar", kvz))
    if not hdr:                                                     # HDR a 8 bits sin tone mapping se veria apagado
        sets += [("libx264", "x264", x264), ("h264_videotoolbox", "VideoToolbox H.264", h264vt)]
    have = ffmpeg_encoders()
    return [t for t in sets if not have or t[0] in have] or sets


SPIN = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


def _read_progress(pfile):
    """(segundos procesados, velocidad x, bytes escritos) del archivo -progress de ffmpeg (ultimo valor); None si no hay dato."""
    secs = speed = size = None
    try:
        with open(pfile, "r", encoding="utf-8", errors="ignore") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return secs, speed, size
    for ln in reversed(lines):
        k, _, v = ln.partition("=")
        try:
            if secs is None and k in ("out_time_us", "out_time_ms"):
                secs = max(0.0, int(v) / 1e6)
            elif speed is None and k == "speed":
                speed = float(v.strip().rstrip("x"))
            elif size is None and k == "total_size":
                size = int(v)
        except ValueError:
            pass
        if secs is not None and speed is not None and size is not None:
            break
    return secs, speed, size


def ui_conv(ui, name, *a):
    """Llama ui.conv_<name>(...) si la escena existe y su modulo lo trae (un dlpy_anim.py anterior a 0.0.2 no lo tiene: se salta)."""
    f = getattr(ui, "conv_" + name, None) if ui else None
    if f:
        f(*a)


def run_conv(args, out, dur=None, show=False, ui=None):
    """ffmpeg con avance REAL. Como en 2.1.5: el avance (-progress) y los errores van a ARCHIVOS y se consultan con poll();
    leer una tuberia (stdout=PIPE) se quedaba colgado en a-Shell. Terminal: spinner + % + velocidad + ETA; --long: `progress`.
    Solo si no se puede LANZAR el proceso se reintenta con os.system (sin avance). Un fallo normal del encoder no se repite."""
    pfile, efile = out + ".progress", out + ".err"
    for f in (pfile, efile):
        try:
            os.remove(f)
        except OSError:
            pass
    cmd = args[:1] + ["-hide_banner", "-nostats", "-progress", pfile] + args[1:]
    errfh = None
    try:
        errfh = open(efile, "w", encoding="utf-8")
        proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=errfh)
    except Exception as e:
        if errfh is not None:
            try:
                errfh.close()
            except Exception:
                pass
        ok, e2 = run_ffmpeg(args, out)
        return ok, e2 or clean_err(e)
    t0, tick, last_pct, width = time.time(), 0, -1, 0
    try:
        while proc.poll() is None:
            secs, speed, size = _read_progress(pfile)
            tick += 1
            if secs is not None and dur:
                pct = min(99.0, secs * 100.0 / dur)
                info = "%4.1f%%" % pct
                if speed:
                    info += "  %.1fx  ETA %s" % (speed, fmt_dur(max(0, (dur - secs) / speed)))
                if size:
                    info += "  " + fmt_size(size)
                if LONG and int(pct) != last_pct:
                    last_pct = int(pct)
                    prog("%d%%" % last_pct)
                ui_conv(ui, "progress", pct)
            elif secs is not None:
                info = "t=%s%s" % (fmt_dur(secs), ("  %.1fx" % speed) if speed else "")
            else:
                info = tr("iniciando…") + " %ds" % int(time.time() - t0)
            if show:
                line = "\r%s %s   " % (SPIN[tick % len(SPIN)], info)
                width = max(width, len(line))
                sys.stdout.write(line)
                sys.stdout.flush()
            try:
                proc.wait(timeout=0.4)
            except subprocess.TimeoutExpired:
                pass
    except BaseException:
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            pass
        raise
    finally:
        try:
            errfh.close()
        except Exception:
            pass
        if show and width:
            sys.stdout.write("\r" + " " * width + "\r")
            sys.stdout.flush()
    err = ""
    try:
        with open(efile, encoding="utf-8", errors="ignore") as fh:
            err = " ".join(fh.read().split())[-300:]
    except OSError:
        pass
    for f in (pfile, efile):
        try:
            os.remove(f)
        except OSError:
            pass
    if proc.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 0:
        return True, ""
    return False, err or "rc=%s" % proc.returncode


def apple_convert(path, streams, plan, show=False, ui=None):
    """Aplica `plan`. (nueva_ruta, error): si falla, error != "" y la ruta sigue siendo la original. ui: AnimUI (la escena muestra la conversion)."""
    audio_only = plan["audio_only"]
    ext = os.path.splitext(path)[1].lower()
    vs = [s for s in streams if s["type"] == "video"][:1]
    au = [s for s in streams if s["type"] == "audio"]
    if audio_only:
        final_ext = ext if plan["cont"] else ".m4a"
    else:
        final_ext = ext if ext in A_VEXT else ".mp4"
    base_name = os.path.splitext(path)[0]
    tmp = base_name + "_apple" + final_ext
    exe = ffmpeg_exe()
    base = [exe, "-y", "-v", "error", "-i", "file:" + path]
    maps = []
    if vs:
        maps += ["-map", "0:%d" % vs[0]["idx"]]
    for a in au:
        maps += ["-map", "0:%d" % a["idx"]]
    abr = 256 if any((a.get("kbps") or 0) >= 200 for a in au) else 192
    tail = []
    for i, m in enumerate(plan["a"]):
        tail += ["-c:a:%d" % i, "copy" if m == "copy" else "aac"]
        if m != "copy":
            tail += ["-b:a:%d" % i, "%dk" % abr]
    tail = (["-vn"] if audio_only else ["-sn", "-dn"]) + tail + ([] if audio_only else ["-movflags", "+faststart"])
    names = []
    if vs and plan["v"] == "enc":
        try:
            size = os.path.getsize(path)
        except OSError:
            size = 0
        tries = video_attempts(vs[0], size, streams.dur)
    elif vs:
        tries = [("copy", "remux", ["-c:v", "copy"] + (["-tag:v", "hvc1"] if vs[0]["codec"] == "hevc" else []))]
    else:
        tries = [("", "audio", [])]
    errs = []
    for enc, name, vopts in tries:
        ui_conv(ui, "begin", path, streams, plan, final_ext, enc)
        ok, err = run_conv(base + maps + vopts + tail + tool_args(tmp) + [tmp], tmp, streams.dur, show, ui)
        if ok:
            new = path if final_ext == ext else _unique(base_name + final_ext)
            os.replace(tmp, new)
            if new != path:
                try:
                    os.remove(path)
                except Exception:
                    pass
            ui_conv(ui, "end", True)
            return new, ""
        errs.append("%s: %s" % (name, err))
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass
    ui_conv(ui, "end", False)
    return path, " | ".join(errs)[-400:] or "ffmpeg"


def ensure_apple(path, quiet=False, ui=None):
    """Revisa el archivo YA descargado (siempre, aunque la lista lo marcara como nativo) y lo convierte si no sirve en
    Apple. Devuelve (ruta, aviso): aviso == "" si todo bien; si no se pudo revisar/convertir, el original queda intacto."""
    if not path or not os.path.exists(path):
        return path, ""
    if CFG["FFMPEG"].lower() in ("no", "0", "false"):
        return path, tr("⚠️ No se pudo comprobar la compatibilidad con Apple: ffmpeg está desactivado.")
    if not quiet:
        print(tr("🍎 Comprobando compatibilidad con Apple…"))
    prog("--title", tr("🍎 Comprobando compatibilidad con Apple…"))
    prog("--indeterminate")
    try:
        streams = probe_streams(path)
        if not streams:
            return path, tr("⚠️ No se pudo comprobar la compatibilidad con Apple: ffmpeg/ffprobe no disponible o archivo ilegible.")
        ok, plan = apple_verdict(path, streams)
        if ok:
            return path, ""
        if not quiet:
            print(tr("🔄 Convirtiendo a un formato compatible con Apple…"))
        prog("--title", tr("🔄 Convirtiendo a un formato compatible con Apple…"))
        new, err = apple_convert(path, streams, plan, show=not quiet and not LONG, ui=ui)
        if err:
            return path, tr("⚠️ No se pudo convertir a un formato compatible con Apple: {e}", e=err)
        return new, ""
    except Exception as e:
        ui_conv(ui, "end", False)                  # si la escena de conversion quedo abierta, se quita
        return path, tr("⚠️ No se pudo comprobar la compatibilidad con Apple: {e}", e=clean_err(e))


def run_pick(yt, url, v, a="", x=""):
    """Descarga la eleccion (v=video o audio:ID, a=audio principal, x=extras unidos con +)."""
    v = v.replace("~", "+")
    audio_only = v.startswith("audio")
    if audio_only:
        fmt = v.split(":", 1)[1] if ":" in v else a
    else:
        fmt = "+".join(p for p in (v, a, x) if p)
    multi = bool(x) and not audio_only
    print(tr("⏳ Descargando…"))
    ui = anim_ui(url, fmt, audio_only)
    tag_err = tool_err = None
    try:
        by = {}
        if (not audio_only and (multi or CFG["MERGE"].lower() == "auto")) or (LONG and "+" in fmt):
            by = formats_by_id(yt, url)
        if LONG:
            long_plan(by, fmt)
        merge = "mp4" if audio_only else pick_container(by, fmt, CFG["MERGE"])
        path, _ = download(yt, url, fmt, merge, multi, audio_only, audio_fmt=CFG["AUDIO"],
                           cache_h=cache_hours(), dup=CFG["DUP"], ui=ui)
        path, apple_warn = ensure_apple(path, quiet=bool(ui), ui=ui)   # siempre: ni la lista ni MERGE garantizan que el archivo sirva
        if multi:
            ids = [i for i in [a] + x.split("+") if i]
            ok, err = tag_audio_tracks(path, [(by.get(i) or {}).get("language") or "" for i in ids])
            if not ok:
                tag_err = err
        ok, err = ensure_tool_tag(path)            # Software de codificacion = «DLpy <version>» (si las pasadas anteriores no lo dejaron)
        if not ok:
            tool_err = err
    except KeyboardInterrupt:
        if ui:
            ui.abort()
        raise
    except Exception as e:
        if ui:
            ui.end(ok=False, error=clean_err(e))
        if LONG:
            return emit_long(ok=False, error=tr("❌ Falló la descarga: {e}", e=clean_err(e)))
        print(tr("❌ Falló la descarga: {e}", e=clean_err(e)))
        return
    if LONG:
        if not path or not os.path.exists(path):
            return emit_long(ok=False, error=tr("❌ Falló la descarga: {e}", e="archivo"))
        prog("--done")
        warns = ([tr("⚠️ No se pudieron etiquetar las pistas de audio: {e}", e=tag_err)] if tag_err else []) \
            + ([apple_warn] if apple_warn else []) \
            + ([tr("⚠️ No se pudo escribir DLpy en el software de codificación: {e}", e=tool_err)] if tool_err else [])
        extra = {"warn": " ".join(warns)} if warns else {}
        return emit_long(ok=True, file_path=shared_path(path), file_title=os.path.basename(path), **extra)
    if ui:
        ui.end(ok=True, send=CFG["CALLBACK"] == "1")
    if apple_warn:
        print(apple_warn)
    if tag_err:
        print(tr("⚠️ No se pudieron etiquetar las pistas de audio: {e}", e=tag_err))
    if tool_err:
        print(tr("⚠️ No se pudo escribir DLpy en el software de codificación: {e}", e=tool_err))
    finish(path)


def long_pick(pick, url):
    """--long: todo lo que se imprima se descarta; el atajo recibe una sola linea JSON (emit_long)."""
    warnings.filterwarnings("ignore")
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            url = clean_url(url)
            pr = parse_pick(pick)
            if not url or not pr:
                return emit_long(ok=False, error=tr("No se encontró un enlace válido."))
            prog("--title", "DLpy")
            prog("--indeterminate")
            yt = import_ytdlp(True)
            if yt is None:
                return emit_long(ok=False, error=tr("No se pudo instalar yt-dlp. Revisa tu conexión."))
            run_pick(yt, url, *pr)
    except Exception as e:
        emit_long(ok=False, error=clean_err(e))
    if not _PG["emitted"]:
        emit_long(ok=False, error=clean_err(buf.getvalue().strip().splitlines()[-1]) if buf.getvalue().strip() else "?")


def cmd_pick(pick, url):
    if LONG:
        return long_pick(pick, url)
    url = clean_url(url)
    pr = parse_pick(pick)
    if not url or not pr:
        print(tr("❌ Falló la descarga: {e}", e=tr("No se encontró un enlace válido.")))
        return
    yt = import_ytdlp(True)
    if yt is None:
        return
    run_pick(yt, url, *pr)


# ------------------------------------------------ modo interactivo (--scb)
def ask_index(prompt, n):
    while True:
        try:
            i = int(input("%s [1-%d]: " % (prompt, n)).strip())
            if 1 <= i <= n:
                return i
        except ValueError:
            pass
        except EOFError:
            raise SystemExit(0)
        print(tr("Opción no válida."))


def ask_multi(prompt, n):
    try:
        s = input(prompt + ": ").strip().lower()
    except EOFError:
        return []
    if not s:
        return []
    if s in ("a", "all", "*"):
        return list(range(1, n + 1))
    out = []
    for part in re.split(r"[,\s]+", s):
        m = re.match(r"^(\d+)-(\d+)$", part)
        if m:
            out += list(range(int(m.group(1)), int(m.group(2)) + 1))
        elif part.isdigit():
            out.append(int(part))
    seen, res = set(), []
    for i in out:
        if 1 <= i <= n and i not in seen:
            seen.add(i)
            res.append(i)
    return res


def interactive_single(yt, info, url):
    merge_ok = can_merge(CFG["FFMPEG"])
    if not merge_ok:
        print(tr("ℹ️ Sin ffmpeg: solo se ofrecen videos que ya traen audio."))
    m = build_menu(info, merge_ok)
    if not m["video_ids"]:
        print(tr("No se encontraron formatos descargables."))
        return
    print("\n" + tr("🎬 Elige la calidad"))
    for l in m["video_labels"]:
        print("  " + l)
    i = ask_index(tr("Número"), len(m["video_ids"])) - 1
    v, step = m["video_ids"][i], m["video_audio_step"][i]
    a, x = "", ""
    if step != "none":
        print("\n" + tr("🔊 Audio principal"))
        for l in m["track_labels"]:
            print("  " + l)
        na = ask_index(tr("Número"), len(m["track_ids"]))
        a = m["track_ids"][na - 1]
        if step == "full":
            others = m["extra_menu"].get(str(na), [])
            if others:
                print("\n" + tr("🔊 Audios adicionales (números separados por coma, a = todos, Enter = ninguno)"))
                for l in others:
                    print("  " + l)
                nums = [int(l.split(" · ")[0]) for l in others]
                sel = ask_multi(tr("Número"), len(others))
                x = "+".join(m["track_ids"][nums[j - 1] - 1] for j in sel)
    run_pick(yt, url, v, a, x)


def interactive_playlist(yt, info, url):
    entries = [e for e in (info.get("entries") or []) if e]
    print(trn("📃 Lista con {n} elemento: {t}", "📃 Lista con {n} elementos: {t}", len(entries), t=safe_title(info.get("title"), 50, "")))
    for i, e in enumerate(entries[:50], 1):
        print("  %d. %s" % (i, safe_title(e.get("title"), 50, str(e.get("id") or ""))))
    if len(entries) > 50:
        print("  …")
    sel = ask_multi(tr("Elementos (Enter = todos, ej. 1-3,7)"), len(entries)) or list(range(1, len(entries) + 1))
    merge_ok = can_merge(CFG["FFMPEG"])
    presets = [(tr("Mejor calidad"), "bv*+ba/b" if merge_ok else "b", False)]
    for h in (1080, 720, 480):
        presets.append(("%dp" % h, ("bv*[height<=%d]+ba/b[height<=%d]" % (h, h)) if merge_ok
                        else "b[height<=%d]/b" % h, False))
    presets.append((tr("Solo audio"), "ba/b", True))
    print("\n" + tr("Calidad para toda la lista"))
    for i, (l, _, _) in enumerate(presets, 1):
        print("  %d. %s" % (i, l))
    _, fmt, audio = presets[ask_index(tr("Número"), len(presets)) - 1]
    ok = bad = 0
    for k in sel:
        e = entries[k - 1]
        eu = e.get("webpage_url") or e.get("url") or ""
        if not eu.startswith("http"):
            bad += 1
            continue
        print("\n[%d/%d] %s" % (sel.index(k) + 1, len(sel), safe_title(e.get("title"), 50, "") or eu))
        try:
            path, _ = download(yt, eu, fmt, CFG["MERGE"], False, audio, audio_fmt=CFG["AUDIO"],
                               cache_h=cache_hours(), dup=CFG["DUP"])
            ensure_tool_tag(path)
            print(tr("📁 Guardado en: {p}", p=path))
            ok += 1
        except Exception as ex:
            print(tr("❌ Falló la descarga: {e}", e=clean_err(ex)))
            bad += 1
    print("\n" + tr("Terminado: {ok} bien, {bad} con error.", ok=ok, bad=bad))


def cmd_term(url=""):
    url, yt = start(url)
    if not url:
        return
    try:
        info = extract(yt, url)
    except Exception as e:
        print(tr("No se pudo leer el enlace: {e}", e=clean_err(e)))
        return
    if not info:
        print(tr("No se encontraron formatos descargables."))
    elif is_playlist(info):
        interactive_playlist(yt, info, url)
    elif info.get("is_live"):
        print(tr("Las transmisiones en vivo no se pueden descargar."))
    else:
        print("🎬 %s %s" % (safe_title(info.get("title"), 50, "") or url, fmt_dur(info.get("duration"))))
        interactive_single(yt, info, url)


def usage():
    print("DLpy %s\n%s" % (VERSION, tr("""Lo controla el atajo "DLpy". Comandos que usa el atajo:
  python dlpy.py                      menú interactivo (pide el enlace)
  python dlpy.py <url>                descarga interactiva de ese enlace
  python dlpy.py --idiomas            JSON con los idiomas del script
  python dlpy.py --config [K=V ...]   configuración (sin argumentos: menú)
  python dlpy.py --scm <url>          JSON rápido (máx. 5 s) con TODO lo encontrado; si no
                                      alcanza o es lista/falta yt-dlp: {"use_scb":true}
  python dlpy.py --scb <url>          igual pero sin límite de tiempo; manda el JSON al atajo
  python dlpy.py --shortcutpick "V=..,A=..,X=.." <url>   descarga la elección
Además: --update (actualiza yt-dlp), --update-langs [códigos] (re-baja idiomas), --update-modules (actualiza los módulos), --update-deps (actualiza pip, yt-dlp y demás dependencias), --self-update (busca ya un Release nuevo de DLpy), --version, --help.""")))
    print(tr("  --long (con --shortcutpick o --scm): para \"Execute Long Command\" (iOS 27); sin limite de tiempo,\n"
             "                                      avisa el avance con `progress`, devuelve una linea JSON; con --scm,\n"
             "                                      la lista completa de formatos con lo Apple nativo primero"))


def main(argv):
    global NET_LANGS, LONG
    a = argv[1:]
    if "--long" in a:                  # solo cambia como se descarga/avisa; el resto de comandos lo ignora
        LONG = True
        a = [x for x in a if x != "--long"]
    if not a:
        return self_update(argv, quiet=False) or cmd_term("")
    c = a[0]
    if c == "--self-update":
        self_update(argv, quiet=False, force=True)
        return
    if c not in ("--scm", "--idiomas", "--langs", "--config", "--update", "--update-langs", "--update-modules", "--update-deps", "--version", "-v", "--help", "-h") \
            and self_update(argv, quiet=LONG or c in ("--scb", "--shortcutpick")):
        return
    if c in ("--idiomas", "--langs", "--scm"):
        NET_LANGS = False
    if c in ("--idiomas", "--langs"):
        return cmd_idiomas()
    if c == "--config":
        return cmd_config(a[1:])
    if c == "--scm":
        return cmd_scm(a[1] if len(a) > 1 else "")
    if c == "--scb":
        return cmd_scb(a[1] if len(a) > 1 else "")
    if c == "--shortcutpick":
        return cmd_pick(a[1] if len(a) > 1 else "", a[2] if len(a) > 2 else "")
    if c == "--update":
        return cmd_update()
    if c == "--update-langs":
        return cmd_update_langs(a[1:])
    if c == "--update-modules":
        return cmd_update_modules()
    if c == "--update-deps":
        return cmd_update_deps()
    if c in ("--version", "-v"):
        return print(VERSION)
    if c in ("--help", "-h"):
        return usage()
    return cmd_term(" ".join(a))


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print()
    except SystemExit:
        raise
    except Exception as exc:
        print(tr("❌ Error inesperado ({tipo}): {e}", tipo=exc.__class__.__name__, e=clean_err(exc)))
        sys.exit(1)
