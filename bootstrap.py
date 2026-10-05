#!dlpy.py - bootstrap: al ejecutarse se reemplaza por el dlpy.py real de GitHub y lo abre.
import os, re, runpy, sys, time, urllib.request

URL = os.environ.get("DLPY_UPDATE_URL") or "https://raw.githubusercontent.com/ElDelDLpy/DLpy/main/dlpy.py"
DEST = os.path.abspath(__file__)
MAX = 3 * 1024 * 1024


def descargar():
    try:
        req = urllib.request.Request(f"{URL}?_={int(time.time())}", headers={
            "User-Agent": "DLpy-bootstrap", "Cache-Control": "no-cache", "Pragma": "no-cache"})
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read(MAX + 1)
        if len(raw) > MAX:
            return None
        text = raw.decode("utf-8").replace("\r\n", "\n")
        if not text.startswith("#!dlpy.py") or not re.search(r'(?m)^VERSION = "\d+\.\d+\.\d+"[ \t]*$', text):
            return None
        compile(text, "dlpy.py", "exec")
        return text
    except Exception:
        return None


texto = descargar()
if not texto:
    sys.exit("No se pudo descargar DLpy (¿sin conexión?). Vuelve a abrirlo para reintentar.")
with open(DEST + ".tmp", "w", encoding="utf-8") as f:
    f.write(texto)
os.replace(DEST + ".tmp", DEST)
sys._dlpy_reexec = True
sys.argv[0] = DEST
runpy.run_path(DEST, run_name="__main__")
