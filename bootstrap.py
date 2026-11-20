#!dlpy.py - bootstrap: se reemplaza con el último Release y reejecuta la misma entrada.
VERSION = "0.0.0"

import json, os, re, sys, tempfile, urllib.request

REPO = (os.environ.get("DLPY_REPO") or "ElDelDLpy/DLpy").strip().strip("/")
UA = {"User-Agent": "DLpy-bootstrap"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        return r.read()


def latest():
    data = json.loads(get(f"https://api.github.com/repos/{REPO}/releases?per_page=5"))
    for rel in data:
        if rel.get("draft") or rel.get("prerelease"):
            continue
        for a in rel.get("assets") or []:
            name = str(a.get("name") or "")
            url = a.get("browser_download_url")
            if url and (name == "dlpy.py" or re.match(r"^dlpy[_\-]?\d+\.\d+\.\d+\.py$", name, re.I)):
                text = get(url).decode("utf-8").replace("\r\n", "\n")
                if text.startswith("#!dlpy.py") and re.search(r'(?m)^VERSION = "\d+\.\d+\.\d+"', text):
                    return text
    raise SystemExit("DLpy bootstrap: no hay Release con dlpy.py")


path = os.path.abspath(__file__)
text = latest()
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".", prefix=".dlpy_")
try:
    os.write(fd, text.encode("utf-8"))
    os.close(fd)
    os.replace(tmp, path)
except Exception:
    try:
        os.close(fd)
        os.remove(tmp)
    except Exception:
        pass
    raise

import runpy
sys.argv[0] = path
runpy.run_path(path, run_name="__main__")
