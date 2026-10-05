import os, re, runpy, sys, time, urllib.request

URL = os.environ.get("DLPY_UPDATE_URL") or "https://raw.githubusercontent.com/ElDelDLpy/DLpy/main/dlpy.py"
DEST = os.path.join(os.path.expanduser("~"), "Documents", "dlpy.py")
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
if texto:
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST + ".tmp", "w", encoding="utf-8") as f:
        f.write(texto)
    os.replace(DEST + ".tmp", DEST)
    sys._dlpy_reexec = True
elif os.path.isfile(DEST):
    print("Sin conexión con GitHub: se abre la copia que ya hay en Documents.")
else:
    sys.exit("No se pudo descargar DLpy y no hay copia en Documents.")
sys.argv[0] = DEST
runpy.run_path(DEST, run_name="__main__")