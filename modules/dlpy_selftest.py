#!dlpy_selftest.py - módulo de la autoprueba de dlpy.py (2.0.2). No se ejecuta solo: dlpy.py lo carga con exec dentro de su propio espacio de nombres (`python dlpy.py --selftest`).
# Va en la carpeta modules/ del repo (junto a su SHA256SUMS) y dlpy.py lo baja y verifica su SHA-256 antes de usarlo.
# Cada edición de dlpy.py que cambie algo probado actualiza también este archivo (regla de la cabecera de dlpy.py) y sube SELFTEST_FOR a la misma versión.
SELFTEST_FOR = "2.0.2"      # versión de dlpy.py para la que está escrito; dlpy.py no lo carga si no coincide con su VERSION

# ───────────────────────── [K1] Autoprueba ─────────────────────────
# Las pruebas son funciones normales (0.7.3): una por grupo [T1]…[T29] (T7–T9 y T20–T22 van juntas porque comparten
# variables) en vez de un texto compilado con exec: así editores, linters y tracebacks las ven. Cada grupo recibe
# check(nombre, obtenido, esperado). Para editarlas, busca las etiquetas [T0]…[T29] o los nombres _st_t*.
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
    """[T2] Progreso simple de la UIM (1.5.8: sin hilo, sin panel, sin degradado)"""
    import contextlib
    import io
    _bar = Bar(panel=True)
    check("barra UIM: sin hilo ni panel (no existen el bucle, el dibujo ni el panel)",
          (_bar.th, [hasattr(_bar, n) for n in ("_loop", "_draw", "_panel_lines", "_poll", "_slow")]), (None, [False] * 5))
    _buf = io.StringIO()
    with contextlib.redirect_stdout(_buf):
        _bar.start("Video 1080p")
        _on = _bar.th
        _bar.set(pct=40.0, tail="↓ 1.4MB/s", step="1/3")
        _bar.final_size = "480 MB"
        _bar.done()
    _out = _ANSI_RE.sub("", _buf.getvalue())
    check("barra UIM: «etiqueta...» al empezar, activa mientras corre y «etiqueta: listo (tamaño)» al acabar",
          (_on, "Video 1080p..." in _out, "Video 1080p: listo (480 MB)" in _out, _bar.th), (True, True, True, None))
    check("barra UIM: sin terminal no reescribe líneas de avance (nada de \\r)", "\r" in _buf.getvalue(), False)
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
    _ths_all = [(n, g, c1, c2, d) for d, n, g, c1, c2 in SITE_THEMES]
    check("1.6.9 temas: hex válidos, siglas únicas, dominios sin repetir y color 1 distinto de 2",
          (all(re.fullmatch(r"#[0-9a-f]{6}", c) for _n, _g, c1, c2, _d in _ths_all for c in (c1, c2)),
           len({g for _n, g, *_r in _ths_all}) == len(_ths_all),
           len({x for *_r, d in _ths_all for x in d}) == sum(len(d) for *_r, d in _ths_all),
           all(c1 != c2 for _n, _g, c1, c2, _d in _ths_all)), (True, True, True, True))
    check("1.6.9 temas: dominios alternos usan el tema de su sitio",
          [site_theme(h)[0] for h in ("xvideos.es", "es.xnxx.tv", "pornhubpremium.com", "bilibili.tv", "m.youtube.com", "t.me")],
          ["XVideos", "XNXX", "Pornhub", "Bilibili", "YouTube", "Telegram"])
    check("1.6.9 temas: sitio sin tema propio recibe uno propio (estable y distinto entre sitios)",
          (site_theme("hanime.tv", "Hanime")[2:] == site_theme("hanime.tv", "Hanime")[2:],
           site_theme("hanime.tv", "Hanime")[2:] != site_theme("nuvid.com", "Nuvid")[2:]), (True, True))
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
    """[T5] ffmpeg, bits, bitrate y metadatos de conversión"""
    import tempfile
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
    # 1.6.1: la revisión escanea los «?» mientras lee y se resuelve a lo detectado con su veredicto; sin lectura, los cuadros llevan lo del plan
    import types as _ty
    _calls, _g = [], globals()
    _sv = {k: _g[k] for k in ("ux_check", "ux_check_end", "ux_wait_anim", "probe_file", "m_info", "m_ok")}
    try:
        _g["ux_check"] = lambda items=None, verdict=None, label=None: _calls.append((items, verdict))
        _g["ux_check_end"] = lambda *a, **k: _calls.append("end")
        _g["ux_wait_anim"] = lambda *a, **k: None
        _g["m_info"] = _g["m_ok"] = lambda *a, **k: None
        _pp = _ty.SimpleNamespace(executable=None)
        _g["probe_file"] = lambda exe, path, timeout=20: _ok
        _calls.clear()
        _r1 = check_download(_pp, "x.mp4", dict(_pl))
        check("check_download 1.6.1: escaneo sobre «?» → resuelve a lo detectado con «ok»; ya compatible: no convierte",
              (_r1, [c if c == "end" else (c[0] is not None, c[1]) for c in _calls]),
              (False, [(False, None), (True, "ok"), "end"]))
        _g["probe_file"] = lambda exe, path, timeout=20: dict(_ok, a=["opus"], ext="mkv", fmt="matroska,webm")
        _calls.clear()
        _r2 = check_download(_pp, "x.mkv", dict(_pl))
        check("check_download 1.6.1: escaneo sobre «?» → resuelve a lo detectado con «conv»; hay que convertir",
              (_r2, [c if c == "end" else (c[0] is not None, c[1]) for c in _calls]),
              (True, [(False, None), (True, "conv"), "end"]))
        _g["probe_file"] = lambda exe, path, timeout=20: None
        _calls.clear()
        _r3 = check_download(_pp, "x.webm", dict(_pl))
        check("check_download 1.6.1: sin lectura, los cuadros muestran lo del plan (no se quedan en «?») y se sigue con el plan",
              (_r3, [c if c == "end" else (c[0] is not None, c[1]) for c in _calls]),
              (True, [(False, None), (True, "conv"), "end"]))
    finally:
        _g.update(_sv)
    _bi = [("H.264", False), ("AAC", True), ("MKV", True)]
    _ra, _rb = (255, 120, 80), (80, 120, 255)
    _b0, _b1, _b2 = (scene_check_cells(60, 6, _ra, _rb, 1.0, _bi, "conv", r) for r in (0.0, CHECK_BLINK_STEP * 1.5, CHECK_BLINK_SECS + 0.2))
    check("revisión 1.6.2: al resolverse parpadea (destello → apagón → destello) y después sigue con el pulso (que ya no depende del reloj del dibujo)",
          (check_blink_phase(0.0), check_blink_phase(CHECK_BLINK_STEP * 1.5), check_blink_phase(CHECK_BLINK_STEP * 2.5), check_blink_phase(CHECK_BLINK_SECS),
           check_blink_phase(None), _b0 != _b1, _b2 == scene_check_cells(60, 6, _ra, _rb, 3.7, _bi, "conv", CHECK_BLINK_SECS + 0.2), {k for k in _b0} == {k for k in _b1}),
          (1, 0, 1, None, None, True, True, True))
    _pc = lambda rt: scene_check_cells(60, 6, _ra, _rb, 1.0, _bi, "conv", rt)
    check("revisión 1.6.2: el pulso arranca donde acaba el parpadeo y cierra su ciclo completo (CHECK_PULSE_SECS); a mitad de ciclo es otro cuadro",
          (abs(CHECK_PULSE_SECS - LOOP_SECS) < 1e-9, _pc(CHECK_BLINK_SECS) == _pc(CHECK_BLINK_SECS + CHECK_PULSE_SECS),
           _pc(CHECK_BLINK_SECS) != _pc(CHECK_BLINK_SECS + CHECK_PULSE_SECS / 4.0)), (True, True, True))
    _sv_s = (SCENE["on"], SCENE.get("check"), SCENE.get("ta"), "ta" in SCENE, SCENE.get("gate_paid"), SCENE.get("loop_paid"))
    try:
        SCENE["on"], SCENE["ta"], SCENE["check"] = True, 5.0, None
        scene_check(_bi, "conv")
        _t1 = SCENE["check"]["t"]
        SCENE["check"]["t"] = 5.0                                       # (lo anota _draw_check al pintar el veredicto)
        SCENE["ta"] = 6.0
        scene_check(_bi, "conv")
        _t2 = SCENE["check"]["t"]
        scene_check()
        check("scene_check 1.6.2: no pone la marca del parpadeo (la anota el dibujo al pintarlo); con el mismo veredicto no la reinicia; sin veredicto no hay marca",
              (_t1, _t2, SCENE["check"]["t"]), (None, 5.0, None))
        SCENE["check"] = {"items": _bi, "verdict": "conv", "t": 5.0}
        check("scene_fps 1.6.2: parpadeando (o a la espera de pintar el primer cuadro del veredicto) va a tope de cuadros; después vuelve a CONV_FPS",
              (scene_fps({"label": "Revisando", "check": SCENE["check"]}, {}, 5.2, 0.0), scene_fps({"label": "Revisando", "check": SCENE["check"]}, {}, 9.0, 0.0),
               scene_fps({"label": "Revisando", "check": dict(SCENE["check"], t=None)}, {}, 9.0, 0.0)),
              (SITE_FPS, SITE_FPS, SITE_FPS))
        _lc = lambda ta, lt, ck=None: _loop_check({"check": ck or SCENE["check"], "ta": ta, "geo": (60, 24, 6, 17)}, {}, 60, lt)
        _l0, _l1, _l2 = _lc(5.2, 0.5), _lc(9.0, 0.5), _lc(5.0, 0.5, {"items": _bi, "verdict": "conv", "t": None})
        check("modo wait 1.6.3: el loop de la resolución = el parpadeo que falta (0,5 s en total; sin pintar aún: todo); pasado el parpadeo, lo que resta del pulso",
              (abs(_l0 - (CHECK_BLINK_SECS - 0.2)) < 1e-6, 0 <= _l1 < CHECK_PULSE_SECS + 1e-6,
               abs(_l2 - CHECK_BLINK_SECS) < 1e-6, abs(_lc(5.0 + CHECK_BLINK_SECS + 0.1, 0.5) - (CHECK_PULSE_SECS - 0.1)) < 1e-6),
              (True, True, True, True))
        _dd = _ty.SimpleNamespace(W=60, y0=6, a=_ra, b=_rb, ta=7.0)
        _s1 = {"check": {"items": _bi, "verdict": "conv", "t": None}, "mvis": ("check", True, 0.0, 0.0)}
        _s2 = {"check": {"items": _bi, "verdict": "conv", "t": None}, "mvis": ("check", False, None, 0.0)}
        _s3 = {"check": {"items": None, "verdict": None, "t": None}, "mvis": ("check", True, 0.0, 0.0)}
        _s4 = {"check": {"items": _bi, "verdict": "conv", "t": None}, "mvis": ("conv", True, 0.0, 0.0)}
        for _sx in (_s1, _s2, _s3, _s4):
            _draw_check(_sx, {}, _dd, 0.0)
        check("dibujo 1.6.2: el reloj del parpadeo arranca al pintar el veredicto con el dibujo ya dentro (no mientras entra, ni sin veredicto, ni si el centro es otro dibujo)",
              (_s1["check"]["t"], _s2["check"]["t"], _s3["check"]["t"], _s4["check"]["t"]), (7.0, None, None, None))
        SCENE["gate_paid"] = SCENE["loop_paid"] = ("check", 1.0)
        SCENE["check"] = {"items": None, "verdict": None, "t": None}
        scene_check(_bi, "conv")
        _p1 = (SCENE["gate_paid"], SCENE["loop_paid"])
        SCENE["gate_paid"] = SCENE["loop_paid"] = ("check", 2.0)
        scene_check(_bi, "conv")
        check("modo wait 1.6.1: al resolverse la revisión se borran las marcas «ya esperado» (la espera del escaneo no paga la de la resolución); con el mismo veredicto no",
              (_p1, SCENE["gate_paid"], SCENE["loop_paid"]), ((None, None), ("check", 2.0), ("check", 2.0)))
    finally:
        SCENE["on"], SCENE["check"], SCENE["gate_paid"], SCENE["loop_paid"] = _sv_s[0], _sv_s[1], _sv_s[4], _sv_s[5]
        if _sv_s[3]:
            SCENE["ta"] = _sv_s[2]
        else:
            SCENE.pop("ta", None)
    check("plan_check_items 1.6.0: video · audio · contenedor con lo que hay que convertir",
          plan_check_items({"vsrc": "vp09", "venc": True, "asrc": ["opus"], "aenc": [True], "cur": "webm", "remux": True}),
          [("VP9", True), ("Opus", True), ("webm", True)])
    check("plan_check_items 1.6.0: audio solo (sin video) → dos cuadros",
          [t for t, _n in plan_check_items({"vsrc": None, "asrc": [], "aenc": [], "cur": "m4a", "remux": False})], ["\u2014", "m4a"])
    check("format_tag 1.6.0: lo que dice yt-dlp, sin «id» ni «?» inventados",
          (format_tag({"format_id": "2"}), format_tag({"format_id": "hls-1080p-0"}), format_tag({"format_id": "2", "format_note": "HD"}),
           format_tag({"format_id": "2", "resolution": "640x360"}), format_tag({"format_id": "x", "resolution": "unknown"})),
          ("2", "hls-1080p-0", "HD", "640x360", "x"))
    check("real_size 1.6.0: resolución real de «resolution» o «format_note»; nada si no hay",
          (real_size({"resolution": "1280x720"}), real_size({"format_note": "1080p60"}), real_size({"format": "22 - 720p"}), real_size({"format_id": "sd"})),
          ((1280, 720), (None, 1080), (None, 720), (None, None)))
    check("normalize_format 1.6.0: sin height pero con resolución real → height real (ya no «sd»/«hd»)",
          (normalize_format({"format_id": "hd", "ext": "mp4", "vcodec": "avc1", "resolution": "1280x720"}).get("height"),
           normalize_format({"format_id": "x", "ext": "mp4", "vcodec": "avc1"}).get("height")), (720, None))
    _sd = {"already_downloaded": {"f": 1}, "downloaded": [1], "pick_format": "x", "pick_example": "y", "stage": "s", "track_ids": ["es"],
           "videos": [{"id": "1", "have": True}], "tracks": [{"id": "es", "have": False}], "audios": [], "all_videos": []}
    slim_scm(_sd)
    check("slim_scm 1.6.0: fuera lo de descargas previas y las marcas «have»; quedan idiomas y listas",
          (sorted(set(("already_downloaded", "downloaded", "pick_format", "pick_example", "stage")) & set(_sd)), _sd["track_ids"],
           _sd["videos"], _sd["tracks"]), ([], ["es"], [{"id": "1"}], [{"id": "es"}]))
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
              (_c0, _c1, _c2), (("Revisando archivo", {"items": None, "verdict": None, "t": None}, "check"), ("Revisando · hay que convertir", "conv"), (None, None)))
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
        # 1.5.9: scene_gate (modo wait: el flujo espera a que el dibujo se vea entero)
        _thg = threading.Thread(target=time.sleep, args=(30.0,), daemon=True)
        _thg.start()
        SCENE.update(th=_thg, gate_paid=None, loop_paid=None)
        _fut = time.time() + 1e6
        _gt = []

        def _gate(md, mv, nk=None, **kw):
            globals()["SCENE_MODE"], SCENE["mvis"] = md, mv
            t_ = time.time()
            r_ = scene_gate(nk, **kw)
            return r_, round(time.time() - t_, 1)
        # espera lo que le falta al loop (0.3 s)
        _gt.append(_gate(("loop", None), ("rail", True, 0.3, _fut, 7.0)))
        # el mismo dibujo ya se esperó: no vuelve a esperar
        _gt.append(_gate(("loop", None), ("rail", True, 0.3, _fut, 7.0)))
        SCENE["gate_paid"] = None
        # ya es el dibujo que entra: nada que esperar
        _gt.append(_gate(("loop", None), ("rail", True, 0.3, _fut, 7.0), "rail"))
        # el tope recorta la espera
        _gt.append(_gate(("loop", None), ("rail", True, 9.0, _fut, 8.0), limit=0.2))
        SCENE["gate_paid"] = None
        _gt.append(_gate(("real", None), ("rail", True, 0.5, _fut, 7.0)))                      # real: nada
        # segundos: mandan los segundos
        _gt.append(_gate(("secs", 2.0), ("rail", True, 0.5, _fut, 7.0)))
        # el sitio con new_kind None es el mismo dibujo: nada que esperar (1.8.1: hacia otro dibujo sí espera; ver _st_t37_sitio)
        _gt.append(_gate(("loop", None), (None, True, 0.5, _fut, 1.0)))
        _gt.append(_gate(("loop", None), ("idle", True, 0.5, _fut, 1.0)))                      # el Pulso tampoco
        # medida de 4 datos (sin instancia): vale y no espera
        _gt.append(_gate(("loop", None), ("check", True, 0.0, _fut)))
        check("escena 1.5.9: scene_gate espera el loop que falta (una sola vez por dibujo), respeta el tope y no espera en real, segundos, el mismo dibujo ni Pulso",
              _gt, [(True, 0.3), (False, 0.0), (False, 0.0), (True, 0.2), (False, 0.0), (False, 0.0), (False, 0.0), (False, 0.0), (False, 0.0)])
        SCENE["gate_paid"] = None
        SCENE.update(last_error="x")
        _gl = _gate(("loop", None), ("rail", True, 0.5, _fut, 7.0))
        SCENE.update(last_error=None, th=None)
        _gl2 = _gate(("loop", None), ("rail", True, 0.5, _fut, 7.0))
        check("escena 1.5.9: scene_gate no espera con un error ni sin hilo vivo", (_gl, _gl2), ((False, 0.0), (False, 0.0)))
        SCENE.update(th=_thg, gate_paid=None, loop_paid=None)
        globals()["SCENE_MODE"], SCENE["mvis"] = ("loop", None), ("save", True, 0.3, _fut, 3.0)
        _t0h = time.time()
        _rh = scene_hold(5.0)
        _dh = time.time() - _t0h
        _lp = (SCENE.get("loop_paid") or (None,))[0]
        check("escena 1.5.9: scene_hold en wait dura lo que le falta a la animación (no los 5 s fijos) y deja la marca para scene_motif",
              (_rh, 0.2 < _dh < 1.0, _lp), (True, True, "save"))
        # 1.8.5: el guardado no simula progreso. «Guardado» solo es el estado final
        # (publicado por _m_store una vez terminado el movimiento real del archivo).
        SCENE.update(th=_thg, label="Descargando", frac=0.0, pct=None, brand=False, welcome=None, conv=None, ask=None)
        globals()["SCENE_MODE"], SCENE["mvis"] = ("loop", None), ("rail", True, 0.0, _fut, 9.0)
        _sv = [scene_saved(), scene_motif_kind({"label": "Guardando"}), scene_motif_kind({"label": "Guardado"}),
              [w["id"] for w in rail_want({"label": "Guardado", "past_dl": True, "stream_total": 1, "stream_seen": 1,
                                            "skind": {1: "video"}, "spct": {1: 100}})]]
        check("escena 1.8.5: Guardando no tiene animación ni tarjeta; Guardado solo representa el resultado confirmado",
              _sv, [False, None, "rail", ["video"]])
        SCENE["loop_paid"] = ("save", time.time())
        _pd = [motif_loop_paid(SCENE, "conv"), motif_loop_paid(SCENE, "save"), motif_loop_paid(SCENE, "save")]
        SCENE["loop_paid"] = ("save", time.time() - 99.0)
        _pd.append(motif_loop_paid(SCENE, "save"))
        check("escena 1.5.9: motif_loop_paid gasta la marca una vez, solo para ese dibujo y mientras no caduque", _pd, [False, True, False, False])
    finally:
        globals()["SCENE_MODE"] = _smw
        SCENE.clear()
        SCENE.update(_sh3)
    check("escena 1.2.5: la revisión manda sobre unión/guardado, pero no sobre la conversión ni D L P Y",
          [scene_motif_kind(x) for x in ({"label": "Revisando archivo"}, {"label": "Revisando", "conv": {"end": None}}, {"label": "Revisando", "brand": True})],
          ["check", "conv", "dlpy"])
    check("escena 1.2.5 (1.6.3): la revisión va siempre a SITE_FPS (su barrido dura 0,5 s)", scene_fps({"label": "Revisando archivo"}, {}, 20.0, SITE_HOLD_AT * SITE_SECS), SITE_FPS)
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
    check("1.6.9 🍎? códec sin determinar (adivinado, unknown en mp4/m4a) vs conocido vs webm",
          (apple_unsure({"ext": "mp4", "vcodec": "avc1", "acodec": "mp4a", "_guess": True}),
           apple_unsure({"ext": "mp4", "vcodec": "unknown", "acodec": "unknown"}),
           apple_unsure({"ext": "m4a", "vcodec": "none", "acodec": "unknown"}),
           apple_unsure({"ext": "mp4", "vcodec": "avc1.640028", "acodec": "mp4a.40.2"}),
           apple_unsure({"ext": "webm", "vcodec": "unknown", "acodec": "unknown"}),
           apple_unsure({"ext": "mp4", "vcodec": "vp09.00.40.08", "acodec": "none"})),
          (True, True, True, False, False, False))
    check("1.6.9 🍎? etiqueta del menú: ? si no se determinó, 🍎 si sí, nada si no",
          (_sc_menu_label(1, {"id": "x", "name": "720p", "vcodec": "mp4", "best": False, "size": None, "compatible": True, "unsure": True},
                          [], False).endswith(APPLE_MARK_UNSURE),
           _sc_menu_label(1, {"id": "x", "name": "720p", "vcodec": "avc1", "best": False, "size": None, "compatible": True, "unsure": False},
                          [], False).endswith(APPLE_MARK),
           APPLE_MARK in _sc_menu_label(1, {"id": "x", "name": "720p", "vcodec": "vp09", "best": False, "size": None, "compatible": False},
                                        [], False)), (True, True, False))
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
    _a12 = video_encoder_attempts({"venc": True, "vbr": 4000, "out_bits": 12}, "fast")
    check("encoders 12: primero x265 12", (_a12[0][1], "profile=main12" in _a12[0][2]), ("x265 12 bits", True))
    check("encoders 12: cae a 10 y 8", [a[1] for a in _a12[1:]], ["VideoToolbox HEVC 10 bits", "x265 10 bits", "x264"])
    _a10 = video_encoder_attempts({"venc": True, "vbr": 4000, "out_bits": 10}, "fast")
    check("encoders 10: main10", ("main10" in " ".join(_a10[0][2]) or "profile=main10" in " ".join(_a10[1][2])), True)
    _a8 = video_encoder_attempts({"venc": True, "vbr": 4000, "out_bits": 8}, "fast")
    check("encoders 8: yuv420p", "yuv420p" in _a8[0][2], True)
    # 1.2.1: HDR al convertir
    check("hdr: tipo por el color del archivo o, si no dice, por la etiqueta",
          (hdr_kind({}, {"color_transfer": "smpte2084"}), hdr_kind({}, {"color_transfer": "arib-std-b67"}), hdr_kind({"hdr": "HDR10"}, None),
           hdr_kind({"hdr": "HLG"}, {"color_transfer": "unknown"}), hdr_kind({"hdr": "HDR10"}, {"color_transfer": "bt709"}), hdr_kind({}, None)),
          ("pq", "hlg", "pq", "hlg", None, None))
    check("hdr: conservar con 10 bits o más, tone mapping a 8, nada si no es HDR",
          (hdr_mode({"hdr_kind": "pq", "out_bits": 10}), hdr_mode({"hdr_kind": "pq", "out_bits": 12}), hdr_mode({"hdr_kind": "hlg", "out_bits": 8}),
           hdr_mode({"out_bits": 10})), ("keep", "keep", "tonemap", None))
    _ak = video_encoder_attempts({"venc": True, "vbr": 4000, "out_bits": 10, "hdr_kind": "pq", "hdr_mode": "keep"}, "fast")
    check("encoders HDR conservado: etiquetas BT.2020 + PQ en todos, main10 y sin x264",
          ([a[1] for a in _ak], all("smpte2084" in " ".join(a[2]) and "bt2020nc" in a[2] for a in _ak), "main10" in " ".join(_ak[1][2])),
          (["VideoToolbox HEVC HDR", "x265 HDR"], True, True))
    _at = video_encoder_attempts({"venc": True, "vbr": 4000, "out_bits": 10, "hdr_kind": "hlg", "hdr_mode": "tonemap"}, "fast")
    check("encoders HDR→SDR: filtro con arib-std-b67, 8 bits, etiquetas BT.709 y x264 al final",
          ([a[1] for a in _at], all("tonemap=tonemap=hable" in " ".join(a[2]) and "arib-std-b67" in " ".join(a[2]) and "yuv420p" in a[2]
                                    and "bt709" in a[2] for a in _at), "yuv420p10le" in " ".join(" ".join(a[2]) for a in _at)),
          (["VideoToolbox HEVC SDR", "x265 SDR", "x264 SDR"], True, False))
    _a12h = video_encoder_attempts({"venc": True, "vbr": 4000, "out_bits": 12, "hdr_kind": "pq", "hdr_mode": "keep"}, "fast")
    check("encoders HDR 12 bits: x265 12, VideoToolbox 10 y x265 10, sin x264 y con etiquetas",
          ([a[1] for a in _a12h], all("smpte2084" in " ".join(a[2]) for a in _a12h)),
          (["x265 12 bits", "VideoToolbox HEVC 10 bits", "x265 10 bits"], True))
    # 1.6.9: DLPY_CONVERT_QUALITY (best = sin pérdida · high · fast) y códec/encoder reales
    check("config 1.6.9: DLPY_CONVERT_QUALITY (predeterminado fast) está en las opciones conocidas",
          [(n, v) for n, v, _t in CONFIG_OPTIONS if n == "DLPY_CONVERT_QUALITY"], [("DLPY_CONVERT_QUALITY", "fast")])
    check("calidad 1.6.9: fast por omisión; best, high, prores y sus alias; lo desconocido es fast",
          [convert_quality_parse(x) for x in (None, "", "best", "mejor", "Lossless", "high", "ALTA", "prores", "fast", "RÁPIDA", "0", "xyz")],
          ["fast", "fast", "best", "best", "best", "high", "high", "prores", "fast", "fast", "fast", "fast"])
    _P8 = {"venc": True, "vbr": 4000, "out_bits": 8}
    _qb, _qh, _qf = (video_encoder_attempts(_P8, q) for q in ("best", "high", "fast"))
    check("encoders best 8 bits: x265 SIN PÉRDIDA (lossless=1, sin crf) primero; VideoToolbox ×1,5 (6000k) y x264 crf 18 de respaldo",
          ([a[1] for a in _qb], "-x265-params" in _qb[0][2] and "lossless=1" in _qb[0][2][_qb[0][2].index("-x265-params") + 1], "-crf" in _qb[0][2],
           "6000k" in _qb[2][2], "18" in _qb[3][2]),
          (["x265 sin pérdida", "Kvazaar sin pérdida", "VideoToolbox HEVC", "x264"], True, False, True, True))
    check("encoders best 8 bits: Kvazaar con lossless=1 (8 bits, hvc1); en 10 bits o HDR conservado no hay Kvazaar",
          (_qb[1][2][_qb[1][2].index("-kvazaar-params") + 1], "yuv420p" in _qb[1][2], "hvc1" in _qb[1][2],
           [a[1] for a in video_encoder_attempts({"venc": True, "vbr": 4000, "out_bits": 10}, "best")]),
          ("lossless=1,preset=ultrafast", True, True, ["x265 sin pérdida", "VideoToolbox HEVC", "x264"]))
    check("encoders high 8 bits: x265 medium crf 20 (sin lossless), VideoToolbox ×1,5 y x264 medium crf 18",
          ([a[1] for a in _qh], "medium" in _qh[0][2] and "20" in _qh[0][2], "-x265-params" in _qh[0][2], "6000k" in _qh[2][2], "medium" in _qh[3][2]),
          (["x265", "Kvazaar", "VideoToolbox HEVC", "x264"], True, False, True, True))
    check("encoders fast 8 bits: VideoToolbox al bitrate del origen, x265 veryfast crf 26 y x264 veryfast crf 21 (como 1.6.8)",
          ([a[1] for a in _qf], "4000k" in _qf[0][2], "veryfast" in _qf[1][2] and "26" in _qf[1][2], "veryfast" in _qf[2][2] and "21" in _qf[2][2]),
          (["VideoToolbox HEVC", "x265", "x264"], True, True, True))
    check("encoders best: el bitrate de VideoToolbox de respaldo tiene tope",
          "40000k" in video_encoder_attempts({"venc": True, "vbr": 30000, "out_bits": 8}, "best")[2][2], True)
    _qk = video_encoder_attempts({"venc": True, "vbr": 4000, "out_bits": 10, "hdr_kind": "pq", "hdr_mode": "keep"}, "best")
    check("encoders best HDR conservado: x265 sin pérdida HDR con main10 y etiquetas BT.2020 + PQ, sin x264",
          ([a[1] for a in _qk], all("smpte2084" in " ".join(a[2]) for a in _qk), "profile=main10" in " ".join(_qk[0][2]), "lossless=1" in " ".join(_qk[0][2])),
          (["x265 sin pérdida HDR", "VideoToolbox HEVC HDR"], True, True, True))
    _q12 = video_encoder_attempts({"venc": True, "vbr": 4000, "out_bits": 12}, "best")
    check("encoders best 12 bits: x265 12 y x265 10 sin pérdida, VideoToolbox 10 en medio y x264 al final",
          ([a[1] for a in _q12], "profile=main12" in " ".join(_q12[0][2])),
          (["x265 12 bits sin pérdida", "VideoToolbox HEVC 10 bits", "x265 10 bits sin pérdida", "x264"], True))
    check("velocidad base 1.6.9 por calidad: best < high < fast",
          (conv_base_speed("best"), conv_base_speed("high"), conv_base_speed("prores"), conv_base_speed("fast")), (0.3, 0.5, 2.0, CONVERT_BASE_SPEED))
    check("conv_info 1.6.9: guarda la calidad y si fue sin pérdida solo si recodificó",
          (conv_info({"venc": True, "vcodec": "hevc", "aenc": [], "out_bits": 8, "abr": 192, "lossless": True}, "hevc").get("lossless"),
           "quality" in conv_info({"venc": True, "aenc": [], "out_bits": 8}, "hevc"),
           "quality" in conv_info({"venc": False, "aenc": [], "out_bits": 8}, None)), (True, True, False))
    def _merge_detail_ok():
        _old = SCENE.get("vinfo"), SCENE.get("ainfo")
        try:
            SCENE["vinfo"], SCENE["ainfo"] = {"codec": "vp09.00.40.08"}, {"codec": "opus"}
            return scene_pp_text("FFmpegMerger") == "Uniendo pistas · VP9 + Opus"
        finally:
            SCENE["vinfo"], SCENE["ainfo"] = _old
    # el filtro por encoders disponibles usa lo que ffmpeg dice traer (se simula la lectura)
    _ENCODERS["ffmpeg-falso"] = {"libx264", "hevc_videotoolbox"}
    _ENCODERS["ffmpeg-vacio"] = set()
    # el de a-Shell: sin x265 ni x264, con Kvazaar
    _ENCODERS["ffmpeg-asehll"] = {"libkvazaar", "hevc_videotoolbox", "h264_videotoolbox", "libaom-av1"}
    check("encoders reales 1.6.9: sin libx265 no se prueba x265 y el códec real queda en el primero que hay; si no se puede leer, todos",
          ([a[1] for a in video_encoder_attempts(_P8, "best", exe="ffmpeg-falso")], [a[1] for a in video_encoder_attempts(_P8, "best", exe="ffmpeg-vacio")]),
          (["VideoToolbox HEVC", "x264"], ["x265 sin pérdida", "Kvazaar sin pérdida", "VideoToolbox HEVC", "x264"]))
    _pk = dict(_P8, vsrc="vp9")
    _ENCODERS["ffmpeg-prores"] = {"hevc_videotoolbox", "prores_videotoolbox", "prores_ks", "libkvazaar"}
    _ENCODERS["ffmpeg-solovt"] = {"hevc_videotoolbox", "h264_videotoolbox"}
    _ppr = dict(_P8, vsrc="vp9")
    check("prores 1.6.9: ProRes VideoToolbox, ProRes software y la cadena de high de respaldo; perfil hq / 3 y sin etiqueta hvc1",
          ([a[1] for a in video_encoder_attempts(_P8, "prores")],
           video_encoder_attempts(_P8, "prores")[0][2][:4], "-vendor" in video_encoder_attempts(_P8, "prores")[1][2],
           "hvc1" in video_encoder_attempts(_P8, "prores")[0][2]),
          (["ProRes 422 HQ VideoToolbox", "ProRes 422 HQ software", "x265", "Kvazaar", "VideoToolbox HEVC", "x264"],
           ["-c:v", "prores_videotoolbox", "-profile:v", "hq"], True, False))
    check("prores 1.6.9: solo los encoders que el ffmpeg trae; sin ProRes cae a high; HDR conservado con etiquetas y sin pasar por 8 bits",
          ([a[1] for a in video_encoder_attempts(_P8, "prores", exe="ffmpeg-prores")], [a[1] for a in video_encoder_attempts(_P8, "prores", exe="ffmpeg-solovt")],
           all("smpte2084" in " ".join(a[2]) for a in video_encoder_attempts({"venc": True, "vbr": 4000, "out_bits": 10, "hdr_kind": "pq", "hdr_mode": "keep"}, "prores")[:2])),
          (["ProRes 422 HQ VideoToolbox", "ProRes 422 HQ software", "Kvazaar", "VideoToolbox HEVC"], ["VideoToolbox HEVC"], True))
    check("prores 1.6.9: el códec real es ProRes, el resumen no repite el nombre y solo se recodifica de video a .mov (audio y remux siguen en su extensión)",
          (plan_target(_ppr, "ffmpeg-prores", "prores"), _ppr.get("target"),
           "→ ProRes 422 HQ VideoToolbox" in plan_summary(dict(_ppr, asrc=[], aenc=[], remux=False, cur="webm", ext="mp4")),
           codec_name("prores"), plan_ext({"venc": True, "vsrc": "vp9", "ext": "mp4"}), plan_ext({"venc": False, "vsrc": "hevc", "ext": "mp4"}),
           plan_ext({"venc": False, "vsrc": None, "ext": "m4a"})),
          ("ProRes 422 HQ VideoToolbox", "ProRes", True, "ProRes", ("mov" if CONVERT_QUALITY == "prores" else "mp4"), "mp4", "m4a"))
    check("encoders reales 1.6.9: con el ffmpeg de a-Shell (sin x265/x264, con Kvazaar) best empieza por Kvazaar sin pérdida y el códec real es HEVC",
          ([a[1] for a in video_encoder_attempts(_P8, "best", exe="ffmpeg-asehll")], plan_target(_pk, "ffmpeg-asehll", "best"), _pk.get("target"),
           [a[1] for a in video_encoder_attempts(dict(_P8, out_bits=10), "best", exe="ffmpeg-asehll")]),
          (["Kvazaar sin pérdida", "VideoToolbox HEVC"], "Kvazaar sin pérdida", "HEVC", ["VideoToolbox HEVC"]))
    _pt = dict(_P8, vsrc="vp9")
    _pu = dict(_P8, vsrc="vp9")
    _ENCODERS["ffmpeg-264"] = {"libx264"}
    check("plan_target 1.6.9: el destino es el códec del encoder real (HEVC con x265, H.264 si solo hay x264) y sin recodificar no hay destino",
          (plan_target(_pt, "ffmpeg-vacio", "best"), _pt.get("target"), plan_target(_pu, "ffmpeg-264", "best"), _pu.get("target"),
           plan_target({"venc": False, "vsrc": "hevc", "target": "HEVC"}), "→ H.264 (x264)" in plan_summary(dict(_pu, asrc=[], aenc=[], remux=False, cur="mp4", ext="mp4"))),
          ("x265 sin pérdida", "HEVC", "x264", "H.264", None, True))
    check("estado 1.6.9: la escena dice el encoder real (con «sin pérdida») y «Uniendo pistas» suma los códecs reales leídos",
          (scene_pp_text("FFmpegMerger") if not any((SCENE.get(k) or {}).get("codec") for k in ("vinfo", "ainfo")) else "Uniendo pistas",
           ("Convirtiendo · " + _qb[0][1]), _merge_detail_ok()),
          ("Uniendo pistas", "Convirtiendo · x265 sin pérdida", True))
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
    check("config 1.9.9: los nombres viejos ya no se traducen (config_key los deja tal cual)",
          (config_key("fastconvert"), config_key("scene_pip"), [n for n, _v, _t in CONFIG_OPTIONS if "FASTCONVERT" in n]),
          ("DLPY_FASTCONVERT", "DLPY_SCENE_PIP", []))
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
    check("env 1.3.0: ruta iOS en dlpy_files (fuera de la carpeta oculta)",
          (env_file_path("/h", hide=False), os.path.dirname(env_file_path("/h")) == os.path.dirname(INTERNAL_DIR.replace(HOME, "/h"))),
          (os.path.join("/h", "Documents", "dlpy_files", "dlpy_config.json"), True))
    # 1.3.0: edición con --config y supervivencia al reinicio de .dlpy_internal
    _cf = os.path.join(_ed, "files", CONFIG_NAME)
    config_write({}, _cf)
    _e = {}
    persist_env(_e, _cf)
    check("config 1.3.0: un archivo vacío (borrado a propósito) no trae nada", _e, {})
    check("config 1.3.0: nombres (con o sin DLPY_, minúsculas, guiones) y los no válidos",
          [config_key(x) for x in ("rows", "dlpy_rows", "DLPY_ROWS", "pip-scene", "", "  ", "a b", "ñ")],
          ["DLPY_ROWS", "DLPY_ROWS", "DLPY_ROWS", "DLPY_PIP_SCENE", None, None, None, None])
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
    _sv_env, _out, _sv_hide = globals()["ENV_FILE"], _io.StringIO(), globals()["hide_files_after_config"]
    try:
        # 1.9.3: --olvidar llama a hide_files_after_config(), que reasigna ENV_FILE al config REAL del dispositivo (dlpy_files) y el test leía la configuración del usuario
        globals()["hide_files_after_config"] = lambda: []
        globals()["ENV_FILE"] = os.path.join(_ed, "cmd", CONFIG_NAME)
        with _cl.redirect_stdout(_out):
            _r1 = print_config(["--config", "rows=3", "DLPY_PIP_SCENE=0"])
            _t1 = _out.getvalue()
            _r2 = print_config(["--config", "--opciones"])
            _t2 = _out.getvalue()[len(_t1):]
            _r3 = print_config(["--config", "x"])
            _r4 = print_config(["--config", "--olvidar"])
        _after = _read_env_json(globals()["ENV_FILE"])
    finally:
        globals()["ENV_FILE"] = _sv_env
        globals()["hide_files_after_config"] = _sv_hide
    check("config 1.3.0: --config guarda y lo muestra; --opciones lista las conocidas marcando las guardadas; un error da 1; --olvidar vacía",
          (_r1, "DLPY_ROWS = 3" in _t1, "DLPY_PIP_SCENE" in _t1, _r2, "DLPY_YTDLP_ARGS" in _t2, "●" in _t2, _r3, _r4, _after),
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
          (_ri, _ci, "DLPY_LOG_KEEP = 7" in _out.getvalue(), "DLPY_ROWS = 3" in _out.getvalue(), "DLPY_ROWS borrada" in _out.getvalue(), "Sin cambios" in _out.getvalue()),
          (0, {"DLPY_LOG_KEEP": "7"}, True, True, True, True))
    check("config 1.3.0: las opciones conocidas son DLPY_* válidas, sin repetir y sin las de una sola ejecución",
          (all(config_key(n) == n for n, _d, _t in CONFIG_OPTIONS), len({n for n, _d, _t in CONFIG_OPTIONS}) == len(CONFIG_OPTIONS),
           any(n in ENV_SKIP for n, _d, _t in CONFIG_OPTIONS)), (True, True, False))
    check("internal dentro de files (1.6.5: oculta con punto o visible según DLPY_HIDE)", (os.path.dirname(INTERNAL_DIR) == FILES_DIR,
                                              os.path.basename(INTERNAL_DIR).startswith("."), INTERNAL_NAME == hidden_name(INTERNAL_BASE, HIDE_FILES)),
          (True, HIDE_FILES, True))
    check("archivos: qué cuenta como descarga en dlpy_files",
          [is_data_entry(n) for n in (INTERNAL_NAME, "backups", "changelog.md", "x.part",
                                      "x.ytdl", "x.tmp", "video.mp4", "audio.m4a", "Mi carpeta")],
          [False, False, False, False, False, False, True, True, True])
    # 1.6.5: DLPY_HIDE — ocultar o mostrar los archivos del script
    check("1.6.7: device_label dice el dispositivo detectado (iPad, iPhone, iPod) o «equipo»",
          [device_label(m_) for m_ in ("iPad13,8", "iPhone15,2", "iPod9,1", "arm64", "", None)][:5] + [device_label("x86_64")],
          ["iPad", "iPhone", "iPod", "equipo", "equipo", "equipo"])
    check("hide 1.6.5: DLPY_HIDE se interpreta (1.6.6: vacío o lo no reconocido = visibles; 1 · on · yes · true · y · si · hide · hidden · oculto = ocultos)",
          [hide_files_parse(x) for x in (None, "", "1", "on", "yes", "x", "0", " No ", "FALSE", "off", "n", "visible", "show")],
          [False, False, True, True, True, False, False, False, False, False, False, False, False])
    check("hide 1.6.5: hidden_name pone o no el punto y los nombres de esta ejecución salen del interruptor",
          (hidden_name("x"), hidden_name("x", False), INTERNAL_NAME == hidden_name(INTERNAL_BASE, HIDE_FILES),
           os.path.basename(SHORTCUTMODE_LOG) == "errors.log", os.path.basename(WARNING_LOG_FILE) == "warnings.log",
           os.path.dirname(SHORTCUTMODE_LOG) == os.path.dirname(WARNING_LOG_FILE) == LOGS_DIR,
           os.path.dirname(LOGS_DIR) == INTERNAL_DIR),
          (".x", "x", True, True, True, True, True))
    _hh = os.path.join(_ed, "hh")
    _hf = os.path.join(_hh, "Documents", "dlpy_files")
    os.makedirs(_hf)
    _sv_hf = os.environ.pop(HIDE_FILES_KEY, None)
    try:
        # ninguno: el del interruptor (predeterminado, oculto)
        _p0 = env_file_path(_hh)
        os.environ[HIDE_FILES_KEY] = "0"
        _p1 = env_file_path(_hh)                                       # ninguno: el visible
        with open(os.path.join(_hf, CONFIG_NAME), "w", encoding="utf-8") as _f:
            _f.write("{}")
        os.environ[HIDE_FILES_KEY] = "1"
        # solo existe el visible: ese, aunque el interruptor diga oculto
        _p2 = env_file_path(_hh)
        os.remove(os.path.join(_hf, CONFIG_NAME))
        with open(os.path.join(_hf, "." + CONFIG_NAME), "w", encoding="utf-8") as _f:
            _f.write("{}")
        os.environ[HIDE_FILES_KEY] = "0"
        # solo existe el oculto: ese, aunque el interruptor diga visible
        _p3 = env_file_path(_hh)
        _p4 = (env_file_path(_hh, hide=True), env_file_path(_hh, hide=False))
    finally:
        if _sv_hf is None:
            os.environ.pop(HIDE_FILES_KEY, None)
        else:
            os.environ[HIDE_FILES_KEY] = _sv_hf
    check("hide 1.6.5: la configuración se busca con cualquiera de los dos nombres (si solo hay uno, ese; si no hay ninguno, el que pida el interruptor)",
          ([os.path.basename(x) for x in (_p0, _p1, _p2, _p3)], [os.path.basename(x) for x in _p4]),
          (["dlpy_config.json", "dlpy_config.json", "dlpy_config.json", ".dlpy_config.json"], [".dlpy_config.json", "dlpy_config.json"]))      # 1.6.6: sin nada, el interruptor por omisión es visible
    _sy = os.path.join(_ed, "sync")
    for _d in ("dlpy_internal", "logs", "trash"):
        os.makedirs(os.path.join(_sy, _d))
    for _n in (CONFIG_NAME, "shortcutmode.log", "video.mp4", os.path.join("trash", "viejo.mp4"), os.path.join("dlpy_internal", "x.json")):
        with open(os.path.join(_sy, _n), "w", encoding="utf-8") as _f:
            _f.write("x")
    _m1 = hide_files_sync(True, _sy)
    _l1 = sorted(os.listdir(_sy))
    _m2 = hide_files_sync(False, _sy)
    _l2 = sorted(os.listdir(_sy))
    _m2b = hide_files_sync(False, _sy)                                 # repetir: ya está todo con su nombre
    # ya hay otro con el nombre de destino: no se pisa
    os.makedirs(os.path.join(_sy, ".logs"))
    _m3 = hide_files_sync(True, _sy)
    _l3 = sorted(os.listdir(_sy))
    check("hide 1.6.5: ocultar renombra solo lo del script (config, carpeta interna, log y logs); las descargas y trash no se tocan y el contenido va con su carpeta",
          (len(_m1[0]), _m1[1], _l1, os.path.isfile(os.path.join(_sy, ".dlpy_internal", "x.json"))),
          (4, [], [".dlpy_config.json", ".dlpy_internal", ".logs", ".shortcutmode.log", "trash", "video.mp4"], True))
    check("hide 1.6.5: mostrar los devuelve a su nombre y repetir la orden no hace nada",
          (len(_m2[0]), _l2, _m2b),
          (4, ["dlpy_config.json", "dlpy_internal", "logs", "shortcutmode.log", "trash", "video.mp4"], ([], [])))
    check("hide 1.6.5: nunca pisa: si ya existe el nombre de destino se deja el de origen y se avisa",
          (_m3[1], len(_m3[0]), _l3), (["logs"], 3, [".dlpy_config.json", ".dlpy_internal", ".logs", ".shortcutmode.log", "logs", "trash", "video.mp4"]))
    check("hide 1.6.5: una carpeta que no existe no da error",
          hide_files_sync(True, os.path.join(_ed, "no_existe")), ([], []))
    _ap = os.path.join(_ed, "apply")
    os.makedirs(_ap)
    _c1 = os.path.join(_ap, CONFIG_NAME)
    with open(_c1, "w", encoding="utf-8") as _f:
        json.dump({HIDE_FILES_KEY: "1", "DLPY_ROWS": "9"}, _f)
    _a1 = hide_files_apply(_c1, _ap)
    _a2 = hide_files_apply(_a1[2], _ap) if _a1[2] else None
    with open(_a1[2], "w", encoding="utf-8") as _f:
        json.dump({HIDE_FILES_KEY: "0", "DLPY_ROWS": "9"}, _f)
    _a3 = hide_files_apply(_a1[2], _ap)
    check("hide 1.6.5: hide_files_apply lee el interruptor de la configuración, la renombra con el resto y devuelve su nombre nuevo (ida, repetir y vuelta)",
          (_a1[0], os.path.basename(_a1[2]), _a2[0], os.path.basename(_a3[2]), _read_env_json(_a3[2]).get("DLPY_ROWS")),
          ([(CONFIG_NAME, "." + CONFIG_NAME)], ".dlpy_config.json", [], "dlpy_config.json", "9"))
    check("hide 1.6.5: DLPY_HIDE está en las opciones conocidas (1) y la carpeta interna, el log y la config no cuentan como descarga aunque estén visibles",
          ([(n, v) for n, v, _t in CONFIG_OPTIONS if n == HIDE_FILES_KEY], [is_data_entry(n) for n in (INTERNAL_BASE, "." + INTERNAL_BASE, "shortcutmode.log", ".shortcutmode.log",
                                                                                                    CONFIG_NAME, ".dlpy_config.json", "logs", ".logs", "video.mp4")]),
          ([("DLPY_HIDE", "0")], [False, False, False, False, False, False, False, False, True]))
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
    # 1.7.1: descarga que yt-dlp devuelve sin archivo y sin error (ignoreerrors): se reintenta y las opciones ya no lo ocultan
    class _FakeDE(Exception):
        pass

    class _FakeUtils:
        DownloadError = _FakeDE

    class _FakeYtDlp:
        utils = _FakeUtils

    class _FakeYDL:
        def __init__(self, first, second, third=None):
            self.calls, self.r, self.params = [], [first, second, third], {}

        def process_ie_result(self, info, download=True):
            self.calls.append("proc")
            return self.r[0]

        def extract_info(self, link, download=True):
            self.calls.append("extract")
            r = self.r[1] if len(self.calls) == 2 else self.r[2]
            if isinstance(r, Exception):
                raise r
            return r
    _nofile, _file = {"requested_downloads": [{"format_id": "1"}]}, {"requested_downloads": [{"format_id": "1", "filepath": "/x/v.mp4"}]}
    _y1, _y2, _y3 = _FakeYDL(_file, None), _FakeYDL(_nofile, _file), _FakeYDL(_nofile, _FakeDE("Requested format is not available"), _file)
    _r1, _r2, _r3 = (run_download(_y, _FakeYtDlp, {"id": "x"}, "https://x", "1") for _y in (_y1, _y2, _y3))
    check("1.7.1: run_download: con archivo no reintenta; sin archivo y sin error reanaliza; si el formato ya no existe usa el mejor equivalente",
          (_r1 is _file, _y1.calls, _r2 is _file, _y2.calls, _r3 is _file, _y3.calls, _y3.params.get("format"), _dl_ok(None), _dl_ok(_nofile), _dl_ok(_file)),
          (True, ["proc"], True, ["proc", "extract"], True, ["proc", "extract", "extract"], "1/bv*+ba/b", False, False, True))

    # 1.7.3: análisis viejo → reanaliza sin usar el viejo; 403 tras reanalizar → un reintento más; opción en --config
    _t0, _p0 = ANALYSIS.get("t"), RETRY_PAUSE
    globals()["RETRY_PAUSE"] = 0.0
    try:
        ANALYSIS["t"] = time.monotonic() - 9999
        _y4 = _FakeYDL(_nofile, None, _file)
        _r4 = run_download(_y4, _FakeYtDlp, {"id": "x"}, "https://x", "1")
        ANALYSIS["t"] = time.monotonic()
        _y5 = _FakeYDL(_nofile, _FakeDE("HTTP Error 403: Forbidden"), _file)
        _r5 = run_download(_y5, _FakeYtDlp, {"id": "x"}, "https://x", "1")
        _y6 = _FakeYDL(_nofile, _FakeDE("HTTP Error 403: Forbidden"), _FakeDE("HTTP Error 403: Forbidden"))
        try:
            run_download(_y6, _FakeYtDlp, {"id": "x"}, "https://x", "1")
            _e6 = None
        except _FakeDE:
            _e6 = "403"
        ANALYSIS["t"] = None
        _y7 = _FakeYDL(_file, None)
        _r7 = run_download(_y7, _FakeYtDlp, {"id": "x"}, "https://x", "1")
    finally:
        ANALYSIS["t"] = _t0
        globals()["RETRY_PAUSE"] = _p0
    check("1.7.3: run_download: análisis viejo reanaliza sin usarlo; 403 tras reanalizar reintenta una vez más (y a la segunda falla); sin marca de edad usa el análisis",
          (_r4 is _file, _y4.calls, _r5 is _file, _y5.calls, _e6, _y6.calls, _r7 is _file, _y7.calls),
          (True, ["extract"], True, ["proc", "extract", "extract"], "403", ["proc", "extract", "extract"], True, ["proc"]))
    # 1.7.3: frases con huecos en los 11 idiomas (antes salían mitad en español) y retoques del inglés
    check("1.7.3: _TPL_ROWS: cada fila trae los 11 idiomas y los mismos huecos {n} que el español",
          [es for es, tr in _TPL_ROWS if len(tr) != len(_TPL_LANGS) or any(sorted(re.findall(r"\{\d\}", x)) != sorted(re.findall(r"\{\d\}", es)) for x in tr)], [])
    _tl = LANG
    try:
        _en = [t_display(x, "en") for x in ("No hay video compatible con 1080p; se usará el mejor disponible.", "pip terminó con error (código 1) al instalar yt-dlp.",
                                            "Espera mientras convierte · puede tardar · no cierres la app.", "Descargando la 1.7.3 desde GitHub...",
                                            "El archivo descargado es de 10 bits: se conservan.", "Conversión rápida (~12 s estimados): se convierte sin preguntar.",
                                            "¿Instalar alguna? n.º", "Cancelado.")]
        _ja = t_display("Enviando a Atajos...", "ja")
        _es = t_display("Enviando a Atajos...", "es")
    finally:
        globals()["LANG"] = _tl
    check("1.7.3: inglés: frases con valores intercalados traducidas enteras; «n.º» es «#» y «Canceled» (americano); el español no cambia",
          (_en, _ja, _es),
          (["No video compatible with 1080p; using the best available.", "pip finished with an error (code 1) while installing yt-dlp.",
            "Wait while it converts · it may take a while · do not close the app.", "Downloading 1.7.3 from GitHub...",
            "The downloaded file is 10-bit: keeping it.", "Quick conversion (~12 s estimated): converting without asking.", "Install any? #", "Canceled."],
           "Atajos に送信中...", "Enviando a Atajos..."))
    check("1.7.3: --config trae DLPY_ANALYZE_TTL (60 por omisión)", [(n, v) for n, v, _t in CONFIG_OPTIONS if n == "DLPY_ANALYZE_TTL"], [("DLPY_ANALYZE_TTL", "60")])

    class _FakeRun0:
        base_opts = {"format": "x"}
        fmt_id, merge_ext, work_dir, base = "1", None, "/tmp/w", "v"
        ui = type("U", (), {"hook": staticmethod(lambda d: None), "pp_hook": staticmethod(lambda d: None)})()

    class _FakeRun:
        base_opts = {"ignoreerrors": "only_download", "format": "x"}
        fmt_id, merge_ext, work_dir, base = "1", None, "/tmp/w", "v"
        ui = type("U", (), {"hook": staticmethod(lambda d: None), "pp_hook": staticmethod(lambda d: None)})()
    check("1.7.3: _ytdlp_options lleva el logger silencioso", isinstance(_ytdlp_options(_FakeRun0).get("logger"), _QuietLog), True)
    check("1.7.1: las opciones de la descarga no heredan ignoreerrors = only_download de la CLI de yt-dlp", _ytdlp_options(_FakeRun)["ignoreerrors"], False)
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
        os.environ["DLPY_VIEW"] = "shortcut"                            # 1.7.8: lo guardado en --config se respeta
        _m2b = view_mode()
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
    check("modo de vista 1.3.4 (1.7.8: view por omisión y lo vacío o desconocido es view; shortcut solo con «shortcut», «atajo»… o --view=shortcut); lo guardado en DLPY_VIEW se respeta; --view manda sobre DLPY_VIEW",
          (_m1, _m2, _m3, _m4, _m2b),
          (["view", "view", "view", "view", "view", "shortcut", "view", "view"], ("view", "shortcut"), "shortcut",
           ((True, ["https://x.y/z"]), ("shortcut", [])), "shortcut"))
    check("modo de vista 1.7.8: --config trae view como valor por omisión de DLPY_VIEW (y su texto lo marca como predeterminado)",
          [(d, "view = el comando `view` de a-Shell (predeterminado)" in x and "· shortcut = se entrega al atajo" in x) for k, d, x in CONFIG_OPTIONS if k == "DLPY_VIEW"],
          [("view", True)])
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
    # 1.7.9: el apóstrofo del título rompía `view`
    _ap = "/x/How something can go faster than what's possible.mp4"
    _cmds.clear()
    _os_sys2, _settle2, _retry2, _vm3 = os.system, globals()["settle_file"], globals()["OPEN_RETRY"], VIEW_RUN["mode"]
    try:
        _rc2 = [256]
        os.system = lambda c: (_cmds.append(c) or _rc2[0])
        globals()["settle_file"] = lambda p: None
        globals()["OPEN_RETRY"] = 0.0
        VIEW_RUN["mode"] = "view"
        _d3 = (_deliver_platform(_ap, "T", quiet=True), list(_cmds))
    finally:
        os.system, globals()["settle_file"], globals()["OPEN_RETRY"], VIEW_RUN["mode"] = _os_sys2, _settle2, _retry2, _vm3
    check("entrega 1.7.9: con apóstrofo en el nombre, view usa comillas dobles y el reintento la forma con barras invertidas (nunca la forma POSIX con '\"'\"')",
          (_d3, any("'\"'\"'" in c for c in _d3[1])),
          ((False, ["view \"/x/How something can go faster than what's possible.mp4\"",
                    "view /x/How\\ something\\ can\\ go\\ faster\\ than\\ what\\'s\\ possible.mp4"]), False))
    check("ash_quote 1.7.9: simple sin raros, comillas simples con espacios, dobles con apóstrofo (escapando \\ \" $ `), barras con style=bs",
          (ash_quote("/x/a.mp4"), ash_quote("/x/a b.mp4"), ash_quote("it's a $x"), ash_quote("it's \"q\" `c` \\"), ash_quote("it's a", "bs"), ash_quote("")),
          ("/x/a.mp4", "'/x/a b.mp4'", "\"it's a \\$x\"", "\"it's \\\"q\\\" \\`c\\` \\\\\"", "it\\'s\\ a", "''"))
    check("modo de vista 1.3.4: la escena de cierre dice lo real: «Abriendo con view» con chip VIEW; con el atajo, «Enviando a DLpy»",
          (send_label(True), send_label(False), [scene_motif_kind(x) for x in ({"label": "Abriendo con view", "brand": True},
                                                                              {"label": "Abriendo con view", "brand": True, "last_error": "x"},
                                                                              {"label": "Abriendo con view"})],
           scene_chip_text("view"), any(o[0] == "DLPY_VIEW" for o in CONFIG_OPTIONS)),
          ("Abriendo con view", "Enviando a " + SHORTCUT_NAME, ["send", "dlpy", "send"], "VIEW", True))   # 1.9.8: el envío es su dibujo con o sin D L P Y
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
    check("variantes con bloque", script_variants(_full, ""), (_head + _body, _full))
    check("variantes desde md", script_variants(_head + _body, _md)[1], _full)
    check("variantes sin fuente", script_variants(_head + _body, "")[1], None)
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
    check("yn multilínea", yn_prompt("¿Mover (1 MB) a trash? (s/N) ▸ ", False), "¿Mover (1 MB) a trash? (s/N) ▸ ")


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
        # 1.8.7: pip_run ya devuelve el código real (sh_run normaliza el estado de espera)
        globals()["pip_run"] = lambda args: 1
        check("pip_install: error (código de salida 1)", [pip_install("x"), len(_wr), "código 1" in _wr[-1]],
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
        check("1.8.7: fetch_remote_script rechaza un Release sin hash publicado", fetch_remote_script(url="u0"), None)
        os.environ["DLPY_NOVERIFY"] = "1"
        check("1.8.7: DLPY_NOVERIFY permite instalar sin hash", fetch_remote_script(url="u0"), _raw.decode())
        os.environ.pop("DLPY_NOVERIFY", None)
        check("1.8.7: el mensaje de «sin hash publicado» está traducido a los 11 idiomas",
              all(I18N[_lg].get("Sin SHA-256 publicado: no se instala. DLPY_NOVERIFY=1 omite la verificación.") for _lg in ("en", "pt", "fr", "de", "it", "ru", "zh", "hi", "ar", "ja", "ko")), True)
    finally:
        RELEASE_HASH.clear()
        RELEASE_HASH.update(_ov)
        globals()["fresh_bytes"], globals()["m_err"], globals()["note"] = _ofb, _oe, _on
        if _env is not None:
            os.environ["DLPY_NOVERIFY"] = _env
    _rr = release_rows(parse_releases(_rel, _info))
    check("filas: solo Releases", [(r["ver"], r["src"], r["label"]) for r in _rr],
          [("0.7.9", "release", "Release"), ("0.7.6", "release", "Release"), ("0.7.5", "release", "Release")])

    check("filas: nada", release_rows(None), [])
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
            globals()["FILES_DIR"] = os.path.join(_td, "files")
            globals()["CHANGELOG_FILE"] = os.path.join(globals()["FILES_DIR"], "changelog.md")
            RELEASES["list"] = None
            check("sync sin Releases: no toca nada", (sync_changelog(fetch=False), os.path.exists(globals()["CHANGELOG_FILE"])),
                  (None, False))
            check("sync escribe directamente en dlpy_files", sync_changelog(_rl), True)
            check("sync: changelog canónico", read_text(globals()["CHANGELOG_FILE"]), _clm)
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
            globals()["FILES_DIR"] = os.path.join(_td, "e_files")
            globals()["CHANGELOG_FILE"] = os.path.join(globals()["FILES_DIR"], "changelog.md")
            globals()["CHECK_FILE"] = os.path.join(_td, "e_checks.json")
            RELEASES["list"] = _rl
            NO_UPDATES["on"] = False
            _dest = globals()["CHANGELOG_FILE"]
            ensure_changelog()
            check("ensure_changelog: lo genera directamente en dlpy_files", read_text(_dest), _clm)
            os.remove(_dest)
            ensure_changelog()
            check("ensure_changelog: lo repone aunque ya se haya comprobado hoy", os.path.isfile(_dest), True)
            os.remove(_dest)
            os.remove(_dest)
            RELEASES["list"] = None
            NO_UPDATES["on"] = True
            ensure_changelog()
            check("ensure_changelog: con --noupdates y sin copia no inventa nada", os.path.isfile(_dest), False)
        finally:
            (globals()["CHANGELOG_FILE"], globals()["FILES_DIR"], globals()["CHECK_FILE"], RELEASES["list"],
             NO_UPDATES["on"]) = _oe
    globals()["VERSION"] = _ov_ver


def _st_t15(check):
    """[T15] Menú de versiones (--versions): solo Releases, sin fallos ni backups (1.6.6)"""
    check("menu vacío", parse_menu_choice("", 3), 0)
    check("menu n", parse_menu_choice(" N ", 3), 0)
    check("menu 2", parse_menu_choice("2", 3), 2)
    check("menu fuera de rango", parse_menu_choice("4", 3), None)
    check("menu texto", parse_menu_choice("hola", 3), None)
    _rr = release_rows([{"ver": "0.1.0", "url": "https://x/a", "notes": "n", "date": "2026-01-01"}, {"ver": "0.0.9", "url": "https://x/b", "notes": "", "date": ""}])
    check("filas: una por Release, con su enlace", [(x["ver"], x["src"], x["ref"], x["label"]) for x in _rr],
          [("0.1.0", "release", "https://x/a", "Release"), ("0.0.9", "release", "https://x/b", "Release")])
    check("filas: sin Releases no hay filas", (release_rows([]), release_rows(None)), ([], []))
def _st_t16(check):
    """[T16] ── notas de la versión dentro del propio .py (solo lectura) ──"""
    _sc_src = "#!dlpy.py\n# ==== CHANGELOG ====\n# ## 1.0.1\n#\n# - Dos.\n#   sigue\n#\n# ==== FIN CHANGELOG ====\nx = 1\n"
    check("notas del script: la versión pedida", script_changelog_notes("1.0.1", _sc_src), "- Dos.\n  sigue")
    check("notas del script: otra versión", script_changelog_notes("9.9.9", _sc_src), None)
    check("notas del script: sin bloque", script_changelog_notes("1.0.1", "#!dlpy.py\nprint(1)\n"), None)
    check("markdown del bloque", changelog_block_md("# ## 1.0.1\n#\n# - Dos.\n#   sigue\n"), "## 1.0.1\n\n- Dos.\n  sigue")


def _st_t17(check):
    """[T17] ── huellas, comparación de orígenes y bajadas ──"""
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
    _vr = version_rows([{"ver": "1.0.0", "src": "release", "date": "2026-10-01", "label": "Release"}], "1.0.0", "1.0.0")
    check("lista de versiones: la fila marca ✓ actual y ⬆ la de actualizar y muestra la fecha",
          (_vr[0]["n"], sorted(_vr[0]["flags"]), _vr[0]["cols"]), (1, ["cur", "upd"], ["1.0.0", "2026-10-01"]))
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
    check("hold: historial a propósito", downgrade_hold("0.1.1", {"history": [dict(_pend, causa="manual")]}), "0.1.3")
    check("hold: la causa «recuperacion» de versiones viejas ya no bloquea", downgrade_hold("0.1.1", {"history": [dict(_pend, causa="recuperacion")]}), None)
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
    check("roast: opción retirada",
          (any(k == "DLPY_ROAST" for k, _v, _d in CONFIG_OPTIONS),
           any(n in globals() for n in ("ROAST", "roast_say", "roast_link", "roast_info", "roast_choice", "roast_done", "roast_cancel", "is_adult", "PINNED"))),
          (False, False))
    _ths = [site_theme(h) for h in ("youtube.com", "tiktok.com", "example.com")]
    check("temas de sitio: conservan nombre, sigla y colores sin el sistema roast",
          all(len(t) == 4 and t[2] != t[3] and all(0 <= v <= 255 for v in t[2] + t[3]) for t in _ths), True)
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
    check("UIM 1.5.8: ya no existen la barra animada, la barra de espacio, la disolución ni la pestaña del sitio",
          [n in globals() for n in ("bar_str", "storage_bar", "outro_clear", "card_tab", "_eta_short", "track_str")], [False] * 6)


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
          # 1.6.9: mp4 sin códec determinado → 🍎?
          _ml[0], "1 · ★ 2 · mp4 · 2.1 Mbps · ~7.5 MB 🔊 " + APPLE_MARK_UNSURE)
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
    check("encabezado (UIM): el espacio va en texto, sin barra de bloques ni pestaña", ("▀" in _br[2], "DLpy" in _br[2], len(_br) >= 3), (False, True, True))
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
          _plain(update_card_rows("0.6.9", "0.7.1", None, 441000, 36)),
          ["✓ Actualizada 0.6.9 → 0.7.1", "  carpeta interna reiniciada"])
    check("tarjeta de bajada con fallo al reiniciar",
          _plain(update_card_rows("0.8.5", "0.7.1", {"causa": "manual", "salto": "menor"}, None, 40)),
          ["! Bajada de versión 0.8.5 → 0.7.1", "  Instalada a propósito desde", "  --versions.",
           f"! no se pudo reiniciar {INTERNAL_NAME}"])
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
        # 1.1.5: con escena, la limpieza no la cede y la deja en «Limpiando»
        mk("escena.mp4", 20)
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
    """[T26] 0.9.9: con trash (10d -> trash, 30d en trash -> borrado); 1.6.6: sin backups"""
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
    saved_t = dict(THEME)
    try:
        THEME.update({"a": None, "b": None, "full": None})
        check("tema: sin sitio, naranja→magenta", theme_rgb(), (PALETTE["orange"][0], PALETTE["magenta"][0]))
        THEME.update({"a": (1, 2, 3), "b": (4, 5, 6)})
        check("tema: colores del sitio", theme_rgb(), ((1, 2, 3), (4, 5, 6)))
        reset_site_state()
        check("reset del tema", (THEME["a"], THEME["full"], SESSION["tag"]), (None, None, None))
    finally:
        THEME.update(saved_t)
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
            check("1.6.6 reset_previous conserva files", reset_previous("0.9.8"), True)
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
    _carry = {}                              # 1.8.7: lo que una parte deja para las siguientes
    _st_t27_textos(check, _carry)
    _st_t27_marcos_y_versiones(check, _carry)
    _st_t27_loop_y_conversion(check, _carry)
    _st_t27_updates_en_escena(check, _carry)
    _st_t27_prefetch_y_pip(check, _carry)
    _st_t27_union_guardado_limpieza(check, _carry)
    _st_t27_motivos_y_cierre(check, _carry)
    _st_t27_flujo_visual(check, _carry)
    _st_t27_etiquetas_y_lista(check, _carry)


def _st_t27_textos(check, _carry):
    """[T27.1] ── parte 1 de 9 de _st_t27 (1.8.7): textos. `_carry` lleva entre partes los valores que las siguientes reutilizan. ──"""
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
    # 1.7.2: esta prueba mide el ruido: no depende de DLPY_GLITCH del entorno
    _gl1, globals()["GLITCH"] = GLITCH, True
    try:
        mid = scene_morph(c0, c1, 0.5, 3)
        _mid2 = scene_morph(c0, c1, 0.5, 3)
    finally:
        globals()["GLITCH"] = _gl1
    check("escena: a mitad de camino hay ruido y es repetible", (any(v[1] == 1 for v in mid.values()), mid),
          (True, _mid2))
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
    S = {"geo": (60, 24, 6, 19), "a": (255, 140, 0), "b": (220, 40, 180), "name": "YouTube", "mode": "video", "title_raw": "Pan casero",
         "brand": False, "busy": False, "label": "Descargando audio es-US 2/3", "pct": 45, "shown": 0.5, "k_out": None}
    st = scene_state()

    def row(cells, y):
        return "".join(cells[(x, y)][0] if (x, y) in cells else " " for x in range(1, 61)).strip()

    t = SITE_HOLD_AT * SITE_SECS
    scene_cells(S, st, t, t + 0.01, 1)                                  # primer cuadro tras la intro: el sitio
    c = scene_cells(S, st, t, t + 2.0, 50)
    check("escena: el título del video", row(c, 8), "Pan casero")
    status_row = 6 + SCENE_STATUS_ROW
    check("escena: texto de pista y %", row(c, status_row), "Descargando audio es-US 2/3 ·  45%")
    S["brand"] = True
    scene_cells(S, st, t, t + 2.1, 51)
    # 1.4.6: el carril termina su ✓ y su salida (≈ 1.6 s) antes de soltar el centro
    scene_cells(S, st, t, t + 3.0, 79)
    scene_cells(S, st, t, t + 4.0, 79)
    c = scene_cells(S, st, t, t + 5.0, 80)
    check("escena: el título pasa a D L P Y", row(c, 8), "D L P Y")
    check("escena DLPY: el centro pasa a ser la ventana a-Shell con el comando, la cadena y la versión",
          ("a-Shell" in row(c, 10), "$" in row(c, 11), all(w in row(c, 12) for w in ("aSH", "PY", "DLPY")),
           ("DLpy " + VERSION) in row(c, 13)), (True, True, True, True))
    # 1.4.5: sin «Descargando», el centro vuelve al sitio
    S["brand"], S["label"] = False, "Analizando enlace"
    scene_cells(S, st, t, t + 5.1, 81)
    c = scene_cells(S, st, t, t + 6.0, 100)
    check("escena: y puede volver al título del video", row(c, 8), "Pan casero")
    check("escena DLPY: al volver, el centro es otra vez el marco del video", ("a-Shell" in row(c, 10), "╭" in row(c, 10)), (False, True))
    S["label"], S["pct"], S["geo"] = "Descargando audio es-US 2/3", 45, (38, 24, 6, 17)
    st2 = {"rows": {}, "lab": None, "prev": "", "full": "", "t": 0.0, "tcur": None, "tprev": None, "tt": None}
    scene_cells(S, st2, t, t + 5.0, 140)
    cn = scene_cells(S, st2, t, t + 6.0, 170)
    check("escena: terminal angosto conserva idioma, 2/3 y %", "".join(cn[(x, status_row)][0] if (x, status_row) in cn else " " for x in range(1, 38)).strip(),
          "Audio es-US 2/3 ·  45%")
    S["label"], S["pct"], S["geo"] = "Comprobando " + "x" * 80, None, (60, 24, 6, 17)
    c = scene_cells(S, st, t, t + 6.0, 150)
    check("escena: un texto largo se recorta y cabe", 0 < len(row(c, status_row)) <= 54, True)
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
    # 1.8.1: el sitio se ve su loop entero y solo entonces entra la conversión
    scene_cells(cvS, stc, t, t + 0.01 + LOOP_SECS + 0.1, 1)
    cc = scene_cells(cvS, stc, t, t + 3.0 + LOOP_SECS, 80)
    check("escena: convirtiendo, el cuadro tiene el marco y el texto del motor",
          ("╭" in {v[0] for v in cc.values()}, row(cc, status_row)), (True, "Convirtiendo · VideoToolbox"))
    cvE = dict(S, conv={"codec": "HEVC", "t0": 0.0, "end": 1.0})
    # 1.2.8: el dibujo espera su loop antes de irse (y luego se retira)
    for _dt in (5.0, 9.5, 10.0, 10.5):
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
                                              scene_chip_text("H.264"), scene_chip_text("日本語"), scene_chip_text("Matroska Video File")], ["WEBM", "DV", "", "H.264", "日本語", "MATROSKA"])     # 1.7.1: ancho real, hasta 8 columnas
    # 1.2.1: la nueva escena de conversión (con %) y su avance
    pa0, pa4, pa10 = (scene_conv_cells(31, 6, ra, rb, 1.0, "VP9", "HEVC", v) for v in (0, 42, 100))
    # 1.6.4: el avance PINTA los puntos de la vía (•, y ● en la cabeza)
    _nb = lambda cs: sum(1 for (_x, _y), v in cs.items() if _y == 12 and v[0] in "•●")
    check("conversión 1.6.4: sin % escrito; 0 % no pinta ningún punto, 42 % algunos y 100 % toda la vía; cabe en 31 columnas",
          (not any("%" in rowtxt(c, y) for c in (pa0, pa4, pa10) for y in (11, 12, 13)), _nb(pa0) == 0 < _nb(pa4) < _nb(pa10),
           max(x for (x, _y) in pa10) < 31, min(x for (x, _y) in pa10) >= 1), (True, True, True, True))
    _gp = _conv_geo(60, "VP9", "HEVC")[4]
    _pz = {v: scene_conv_cells(60, 6, ra, rb, 1.0, "VP9", "HEVC", v, fast=True) for v in (0, 25, 75, 100)}
    _lane = lambda cs: sorted(x for (x, y), v in cs.items() if y == 12 and v[0] in "•●")
    check("conversión 1.6.4: los puntos se pintan de origen a destino con el % real (0 % ninguno; 25 % → 5 puntos, 75 % → 13, 100 % → toda la vía; los de menos % son los primeros)",
          ([len(_lane(c)) for c in _pz.values()], set(_lane(_pz[25])) <= set(_lane(_pz[75])) <= set(_lane(_pz[100])), _gp), ([0, 5, 13, 17], True, 17))
    check("conversión 1.6.4: sin loop de paquetes: con el mismo % el dibujo es el mismo en cualquier instante (convert_fast_anim), la cabeza ● es el último punto pintado y solo el 100 % destella",
          (scene_conv_cells(60, 6, ra, rb, 0.1, "VP9", "HEVC", 42, fast=True) == scene_conv_cells(60, 6, ra, rb, 7.3, "VP9", "HEVC", 42, fast=True),
           scene_conv_cells(60, 6, ra, rb, 0.1, "VP9", "HEVC", 42) == scene_conv_cells(60, 6, ra, rb, 7.3, "VP9", "HEVC", 42),
           scene_conv_cells(60, 6, ra, rb, 0.0, "VP9", "HEVC", 100) != scene_conv_cells(60, 6, ra, rb, LOOP_SECS / 4.0, "VP9", "HEVC", 100),
           scene_conv_cells(60, 6, ra, rb, 0.0, "VP9", "HEVC", 100, fast=True) == scene_conv_cells(60, 6, ra, rb, LOOP_SECS / 4.0, "VP9", "HEVC", 100, fast=True),
           "●" in "".join(v[0] for (x, y), v in _pz[75].items() if y == 12), "●" not in "".join(v[0] for (x, y), v in _pz[100].items() if y == 12)),
          (True, True, True, True, True, True))
    _smx = max(x for (x, y), v in _pz[75].items() if y == 12 and v[0] == "●")
    check("conversión 1.6.4: la cabeza ● va en la celda que se está llenando (la del extremo derecho de lo pintado)",
          _smx, max(_lane(_pz[75])))
    _Sc, _Tc = {"geo": (60, 24, 6, 19), "conv": {"end": None}}, {"ms": 5.0, "mt": None}
    check("conversión 1.6.4: sin loop mientras convierte; al terminar queda CONV_END_HOLD (un loop) para ver la vía llena y el destino destellando",
          (motif_loop_left(_Sc, _Tc, "conv", 7.0), round(motif_loop_left(dict(_Sc, conv={"end": 10.0}), _Tc, "conv", 10.3), 6),
           motif_loop_left(dict(_Sc, conv={"end": 10.0}), _Tc, "conv", 11.0 + CONV_END_HOLD)), (0.0, round(max(0.0, CONV_END_HOLD - 0.3), 6), 0.0))
    _Sx = {"geo": (60, 24, 6, 19), "check": {"items": None, "verdict": None}}
    _Tx = {"mt": None, "ms": 0.0, "cinfo": ("VP9", "HEVC", 0.0)}
    _ll = {k: motif_loop_left(_Sx, _Tx, k, 0.3) for k in ("conv", "merge", "save", "clean", "empty", "check", "send", "ask", None, "dlpy")}
    check("escena 1.2.8: cada dibujo con loop sabe cuánto falta para terminarlo; DLPY y la pregunta no esperan (1.8.1: el sitio sí, su loop de LOOP_SECS)",
          (all(_ll[k] > 0 for k in ("merge", "save", "clean", "empty", "check", "send")) and _ll["conv"] == 0.0, _ll["ask"], _ll[None], _ll["dlpy"],
           round(_ll["merge"], 6), round(_ll["send"], 6), round(_ll["save"], 6)),
          (True, 0.0, (-0.3) % LOOP_SECS, 0.0, round((-0.3) % (4.0 / MERGE_SPEED), 6), round((-0.3) % SEND_CYCLE, 6), round(SAVE_STREAM_SECS + UX_SETTLE - 0.3, 6)))
    _carry.update(_Sx=_Sx, _Tx=_Tx, _nb=_nb, c1=c1, c2=c2, cc=cc, cvS=cvS, pa0=pa0, pa10=pa10, pa4=pa4, ra=ra, rb=rb, row=row, rowtxt=rowtxt, status_row=status_row, stc=stc, t=t)


def _st_t27_marcos_y_versiones(check, _carry):
    """[T27.2] ── parte 2 de 9 de _st_t27 (1.8.7): marcos y versiones. `_carry` lleva entre partes los valores que las siguientes reutilizan. ──"""
    import io
    _Sx, _Tx, _nb, c1, c2, pa0, pa10, pa4, ra, rb, rowtxt = _carry["_Sx"], _carry["_Tx"], _carry["_nb"], _carry["c1"], _carry["c2"], _carry["pa0"], _carry["pa10"], _carry["pa4"], _carry["ra"], _carry["rb"], _carry["rowtxt"]
    # 1.2.9: escenas «Primera ejecución» y «Actualizado»
    # 1.6.3: los tiempos de estas pruebas son de la escala de 2,4 s del dibujo
    _wk = WELCOME_CYCLE / WELCOME_BASE
    wf0, wf1, wf2 = (scene_first_cells(60, 6, ra, rb, lt * _wk) for lt in (0.05, 1.0, 2.0))
    wu0, wu1 = (scene_updated_cells(60, 6, ra, rb, lt * _wk, "1.2.8", "1.2.9") for lt in (0.5, 1.8))
    _ck = lambda cs: sum(1 for v in cs.values() if v[0] == "✓")
    check("escena 1.2.9: el centro es «first» / «updated» con S['welcome'] (D L P Y no manda; un error sí; sin welcome nada cambia)",
          [scene_motif_kind(x) for x in ({"label": "x", "brand": True, "welcome": {"kind": "first"}},
                                         {"label": "x", "brand": True, "welcome": {"kind": "updated"}},
                                         {"label": "x", "brand": True, "welcome": {"kind": "first"}, "last_error": "e"},
                                         {"label": "x", "brand": True, "welcome": {"kind": "zzz"}},
                                         {"label": "Guardado", "welcome": None})],
          ["first", "updated", "dlpy", "dlpy", "rail"])
    check("primera ejecución 1.2.9: tres pasos (carpetas · estado · listo) en tres filas y se marcan con ✓ uno a uno",
          (rowtxt(wf2, 11).startswith("carpetas"), rowtxt(wf2, 12).startswith("estado"), rowtxt(wf2, 13).startswith("listo"),
           {y for (_x, y) in wf2} == {11, 12, 13}, _ck(wf0), _ck(wf1), _ck(wf2)), (True, True, True, True, 0, 1, 3))
    check("primera ejecución 1.2.9: repetible, se mueve, se repite cada ciclo y cabe en 31 columnas",
          (wf1 == scene_first_cells(60, 6, ra, rb, 1.0 * _wk), wf0 != wf1,
           scene_first_cells(60, 6, ra, rb, 0.5) == scene_first_cells(60, 6, ra, rb, 0.5 + WELCOME_CYCLE),
           max(x for (x, _y) in scene_first_cells(31, 6, ra, rb, 2.0 * _wk)) < 31, min(x for (x, _y) in scene_first_cells(31, 6, ra, rb, 2.0 * _wk)) >= 1),
          (True, True, True, True, True))
    check("actualizado 1.2.9: versión anterior a la izquierda, nueva a la derecha; en camino van chevrones › y al llegar un ✓",
          (rowtxt(wu0, 12).find("1.2.8") < rowtxt(wu0, 12).find("1.2.9"), "›" in rowtxt(wu0, 12), "✓" in rowtxt(wu0, 12),
           "✓" in rowtxt(wu1, 12), "›" in rowtxt(wu1, 12), {y for (_x, y) in wu0} == {11, 12, 13}),
          (True, True, False, True, False, True))
    check("actualizado 1.2.9: repetible, se mueve, se repite cada ciclo, sin versión pone «?» y cabe en 31 columnas con versiones largas",
          (wu0 == scene_updated_cells(60, 6, ra, rb, 0.5 * _wk, "1.2.8", "1.2.9"), wu0 != wu1,
           scene_updated_cells(60, 6, ra, rb, 0.125, "1.2.8", "1.2.9") == scene_updated_cells(60, 6, ra, rb, 0.125 + WELCOME_CYCLE, "1.2.8", "1.2.9"),
           "?" in rowtxt(scene_updated_cells(60, 6, ra, rb, 0.5 * _wk), 12),
           max(x for (x, _y) in scene_updated_cells(31, 6, ra, rb, 0.5, "12.34.56.78", "98.76.54.32")) < 31,
           min(x for (x, _y) in scene_updated_cells(31, 6, ra, rb, 0.5, "12.34.56.78", "98.76.54.32")) >= 1),
          (True, True, True, True, True, True))
    check("escena 1.2.9: primera ejecución y actualizado tienen loop (un ciclo) y no se deshacen hasta terminarlo",
          (round(motif_loop_left(_Sx, _Tx, "first", 0.3), 6), round(motif_loop_left(_Sx, _Tx, "updated", 0.3), 6),
           round(motif_loop_left(_Sx, _Tx, "first", 0.3 + WELCOME_CYCLE), 6), SCENE_WELCOME_SECS < WELCOME_CYCLE),
          (round(WELCOME_CYCLE - 0.3, 6), round(WELCOME_CYCLE - 0.3, 6), round(WELCOME_CYCLE - 0.3, 6), True))
    check("escena 1.2.9: qué escena de arranque toca (sin versión guardada = primera; otra = actualizado; igual = ninguna)",
          [welcome_kind(None, "1.2.9"), welcome_kind("", "1.2.9"), welcome_kind("1.2.8", "1.2.9"), welcome_kind("1.3.0", "1.2.9"),
           welcome_kind("1.2.9", "1.2.9")], ["first", "first", "updated", "downgrade", None])
    check("escena 1.6.5: welcome_kind distingue subida y bajada por número (no por texto) y la misma versión no pide escena",
          [welcome_kind(a_, b_) for a_, b_ in (("1.6.4", "1.6.5"), ("1.6.5", "1.6.4"), ("1.9.9", "1.10.0"), ("1.10.0", "1.9.9"), ("1.6.5", "1.6.5"), ("1.6", "1.6.0"),
                                                ("2.0.0", "1.9.9"), ("0.9.9", "1.0.0"))],
          ["updated", "downgrade", "updated", "downgrade", None, None, "downgrade", "updated"])
    # 1.6.5: «Versión anterior» (bajada) y «Misma versión»
    wd0, wd1 = (scene_downgrade_cells(60, 6, ra, rb, lt * _wk, "1.6.5", "1.6.4") for lt in (0.5, 1.8))
    ws0, ws1 = (scene_same_cells(60, 6, ra, rb, lt * _wk, "1.6.5", "1.6.5") for lt in (0.3, 1.2))
    we0 = scene_same_cells(60, 6, ra, rb, 0.3 * _wk, "1.6.5", "1.6.5", True)
    _all = lambda cs: "".join(rowtxt(cs, y) for y in (11, 12, 13))
    _ch = sorted((x_, y_) for (x_, y_), v_ in wd0.items() if v_[0] == "‹")
    check("bajada 1.6.5: la versión nueva (menor) queda a la izquierda y la que había a la derecha; en camino van chevrones ‹ (no ›) y al llegar un ✓",
          (rowtxt(wd0, 12).find("1.6.4") < rowtxt(wd0, 12).find("1.6.5"), "‹" in _all(wd0), "›" in _all(wd0), "✓" in rowtxt(wd0, 12),
           "✓" in rowtxt(wd1, 12), "‹" in _all(wd1), {y for (_x, y) in wd0} == {11, 12, 13}),
          (True, True, False, False, True, False, True))
    check("bajada 1.6.5: los chevrones se hunden: a la derecha van arriba y a la izquierda abajo (bajan hacia la versión nueva)",
          (len(_ch) >= 2, all(y1 >= y2 for (_x1, y1), (_x2, y2) in zip(_ch, _ch[1:])), _ch[0][1] > _ch[-1][1]), (True, True, True))
    check("bajada 1.6.5: repetible, se mueve, se repite cada ciclo, sin versión pone «?» y cabe en 31 columnas con versiones largas",
          (wd0 == scene_downgrade_cells(60, 6, ra, rb, 0.5 * _wk, "1.6.5", "1.6.4"), wd0 != scene_downgrade_cells(60, 6, ra, rb, 0.7 * _wk, "1.6.5", "1.6.4"),
           scene_downgrade_cells(60, 6, ra, rb, 0.125, "1.6.5", "1.6.4") == scene_downgrade_cells(60, 6, ra, rb, 0.125 + WELCOME_CYCLE, "1.6.5", "1.6.4"),
           "?" in rowtxt(scene_downgrade_cells(60, 6, ra, rb, 0.5 * _wk), 12),
           max(x for (x, _y) in scene_downgrade_cells(31, 6, ra, rb, 0.5, "12.34.56.78", "98.76.54.32")) < 31,
           min(x for (x, _y) in scene_downgrade_cells(31, 6, ra, rb, 0.5, "12.34.56.78", "98.76.54.32")) >= 1),
          (True, True, True, True, True, True))
    check("misma versión 1.6.5: la misma versión a los dos lados con «=» en medio (o «≈» si cambió el hash) y un puente ═ en una sola fila",
          (rowtxt(ws0, 12).count("1.6.5"), "=" in rowtxt(ws0, 12).replace("═", ""), "≈" in rowtxt(ws0, 12), "≈" in rowtxt(we0, 12), "═" in rowtxt(ws0, 12),
           {y for (_x, y) in ws0} == {11, 12, 13}, {y for (_x, y) in we0} == {11, 12, 13}, "●" in rowtxt(ws0, 12), "●" in rowtxt(ws1, 12),
           rowtxt(ws0, 12).find("●") != rowtxt(ws1, 12).find("●")),
          (2, True, False, True, True, True, True, True, True, True))
    check("misma versión 1.6.5: el destello recorre el puente (cambia con el tiempo), se repite cada ciclo y cabe en 31 columnas con versiones largas",
          (ws0 != ws1, ws0 == scene_same_cells(60, 6, ra, rb, 0.3 * _wk, "1.6.5", "1.6.5"),
           scene_same_cells(60, 6, ra, rb, 0.125, "1.6.5", "1.6.5") == scene_same_cells(60, 6, ra, rb, 0.125 + WELCOME_CYCLE, "1.6.5", "1.6.5"),
           "?" in rowtxt(scene_same_cells(60, 6, ra, rb, 0.5 * _wk), 12),
           max(x for (x, _y) in scene_same_cells(31, 6, ra, rb, 0.5, "12.34.56.78", "98.76.54.32", True)) < 31,
           min(x for (x, _y) in scene_same_cells(31, 6, ra, rb, 0.5, "12.34.56.78", "98.76.54.32", True)) >= 1),
          (True, True, True, True, True, True))
    check("escena 1.6.5: el centro es «downgrade» / «same» con S['welcome'] (D L P Y no manda; un error sí) y ambos tienen loop de un ciclo",
          ([scene_motif_kind(x) for x in ({"label": "x", "brand": True, "welcome": {"kind": "downgrade"}}, {"label": "x", "brand": True, "welcome": {"kind": "same"}},
                                          {"label": "x", "brand": True, "welcome": {"kind": "same"}, "last_error": "e"})],
           round(motif_loop_left(_Sx, _Tx, "downgrade", 0.3), 6), round(motif_loop_left(_Sx, _Tx, "same", 0.3), 6)),
          (["downgrade", "same", "dlpy"], round(WELCOME_CYCLE - 0.3, 6), round(WELCOME_CYCLE - 0.3, 6)))
    # 1.6.5: la comprobación de DLpy anima su veredicto (subida · misma versión · bajada) con los mismos textos de estado de siempre
    import contextlib
    import io
    _g_ = globals()
    _nm = ("fetch_latest_release", "sync_changelog", "ux_welcome", "ux_note", "confirm_install", "show_verify", "m_info", "m_check", "m_warn", "note")
    _sv_g = {n_: _g_[n_] for n_ in _nm}
    _sv_pf, _sv_uc = PREFETCH["on"], dict(UPDATE_CHECKED)
    _rec, _asks = [], []
    try:
        for n_ in ("sync_changelog", "show_verify", "m_info", "m_check", "m_warn", "note"):
            _g_[n_] = lambda *a, **k: None
        _g_["ux_welcome"] = lambda *a, **k: (_rec.append(a + (k.get("edited"), k.get("text"))) or True)
        _g_["ux_note"] = lambda *a, **k: True
        _g_["confirm_install"] = lambda *a, **k: (_asks.append(a[:2]) or False)
        PREFETCH["on"] = False
        _mine = read_text(SCRIPT_PATH)
        for _rm, _tx in ((VERSION, _mine), (VERSION, "otro código\n"), ("0.0.1", "x\n"), ("999.0.0", "x\n")):
            _g_["fetch_latest_release"] = lambda timeout=5, _r={"ver": _rm, "text": _tx, "url": "u", "notes": "", "date": None}: _r
            _out = io.StringIO()
            with contextlib.redirect_stdout(_out):
                check_update()
        _g_["ux_welcome"] = lambda *a, **k: 1 / 0
        _bad = version_scene("same", "1.0.0", "1.0.0", "t")
    finally:
        _g_.update(_sv_g)
        PREFETCH["on"] = _sv_pf
        UPDATE_CHECKED.update(_sv_uc)
    check("actualizaciones 1.6.5: el veredicto de la comprobación se anima con su texto de siempre (última = misma versión, «≈» si el Release difiere; Release menor = bajada; Release mayor = subida) y un fallo de la animación no la rompe",
          (_rec, _asks, _bad),
          ([("same", VERSION, VERSION, False, f"DLpy {VERSION} · última versión"), ("same", VERSION, VERSION, True, f"DLpy {VERSION} · última versión"),
            ("ahead", "0.0.1", VERSION, False, f"DLpy {VERSION} · versión local"),
            ("updated", VERSION, "999.0.0", False, f"Nueva versión de DLpy · {VERSION} → 999.0.0")], [(f"Instalar la 999.0.0 y ejecutarla ahora", "999.0.0")], False))
    _wk = ("on", "welcome", "label", "label_wall", "brand", "busy", "err_brand", "pct", "last_error")
    _sv, _secs, _hold0 = {k: SCENE.get(k) for k in _wk}, SCENE_WELCOME_SECS, globals()["welcome_hold"]
    _seen = []
    try:
        globals()["SCENE_WELCOME_SECS"] = 0.0
        globals()["welcome_hold"] = lambda secs: (_seen.append((SCENE["label"], SCENE["brand"], SCENE["busy"], (SCENE["welcome"] or {}).get("kind"))) or True)
        SCENE.update(on=True, welcome=None, label="Preparando", label_wall=None, brand=False, busy=False, err_brand=False, pct=None, last_error=None)
        _w = []
        for _a in (("updated", "1.2.8", "1.2.9", False), ("updated", "1.3.0", "1.2.9", True), ("first", None, None, False), ("zzz", None, None, False),
                   ("downgrade", "1.6.5", "1.6.4"), ("same", "1.6.5", "1.6.5"), ("same", "1.6.5", "1.6.5", False, True), ("updated", "1.6.5", "1.6.5", False, True),
                   ("updated", "1.6.4", "1.6.5", False, False, "Nueva versión de DLpy · 1.6.4 → 1.6.5")):
            _w.append((scene_welcome(*_a), SCENE["label"], SCENE["brand"], SCENE["busy"], SCENE["welcome"]))
        # ya en el título D L P Y: se respeta
        SCENE.update(brand=True, busy=True, label="Comprobando DLpy")
        _w.append((scene_welcome("first"), SCENE["label"], SCENE["brand"], SCENE["busy"]))
        SCENE.update(brand=False, busy=False, label="Preparando", last_error="x")      # con un error no se toca
        _w.append((scene_welcome("first"), SCENE["label"]))
        SCENE.update(on=False, last_error=None)
        _w.append(scene_welcome("first"))
    finally:
        globals()["SCENE_WELCOME_SECS"], globals()["welcome_hold"] = _secs, _hold0
        SCENE.update(_sv)
    check("escena 1.2.9/1.3.1: scene_welcome pone el texto de estado y D L P Y mientras dura, y al terminar lo deja todo como estaba (no se queda en D L P Y)",
          (_seen, _w),
          ([("Actualizado · 1.2.8 → 1.2.9", True, True, "updated"), ("Versión anterior · 1.3.0 → 1.2.9", True, True, "downgrade"),
            (f"Primera ejecución · DLpy {VERSION}", True, True, "first"),
            ("Versión anterior · 1.6.5 → 1.6.4", True, True, "downgrade"), ("Misma versión · 1.6.5", True, True, "same"),
            ("Cambió el hash · edición detectada", True, True, "same"), ("Cambió el hash · edición detectada", True, True, "same"),
            ("Nueva versión de DLpy · 1.6.4 → 1.6.5", True, True, "updated"),
            (f"Primera ejecución · DLpy {VERSION}", True, True, "first")],
           [(True, "Preparando", False, False, None), (True, "Preparando", False, False, None), (True, "Preparando", False, False, None),
            (False, "Preparando", False, False, None)] + [(True, "Preparando", False, False, None)] * 5
           + [(True, "Comprobando DLpy", True, True), (False, "Preparando"), False]))
    _cl = "# ==== CHANGELOG ====\n# ## 9.9.9\n# ==== FIN CHANGELOG ====\n"
    check("1.3.2: el hash del código ignora el changelog y detecta un cambio de código con la misma versión",
          (text_fingerprints("a = 1\n" + _cl)[1] == text_fingerprints("a = 1\n" + _cl.replace("9.9.9", "1.0.0"))[1],
           text_fingerprints("a = 1\n" + _cl)[1] == text_fingerprints("a = 2\n" + _cl)[1],
           [code_change(None, "h1"), code_change("", "h1"), code_change("h1", "h1"), code_change("h1", "h2"),
            code_change("h1", None), code_change(None, None)]),
          (True, False, ["first", "first", None, "edited", None, None]))
    _Tm = {"mt": 10.0, "ms": 9.0}                                       # 1.3.2: DLPY_SCENE_MODE
    _smr, _sx = SCENE_MODE, {"geo": (60, 24, 6, 19), "conv": {"pct": 50.0}, "pp_pct": 100.0}
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
    check("escena 1.3.9: modo real: el dibujo avanza con el % real (unión: 3 ciclos; 1.6.4: la conversión ya pinta el % directo y sigue el reloj; sin % o sin real, el reloj)",
          _rl, (9.9, 9.9, 0.0, round(3 * 4.0 / MERGE_SPEED, 6), 9.9, 0.7, 9.9))
    check("escena 1.3.2: DLPY_SCENE_MODE (loop · real · segundos) se interpreta y lo inválido cae en loop",
          [scene_mode_parse(v) for v in (None, "", "loop", "real", "Real", "2", "1,5", "0", "-1", "abc", "nan", "inf", "999")],
          [("loop", None), ("loop", None), ("loop", None), ("real", None), ("real", None), ("secs", 2.0), ("secs", 1.5), ("secs", 0.0),
           ("loop", None), ("loop", None), ("loop", None), ("loop", None), ("secs", 60.0)])
    check("escena 1.3.2: cuánto espera un dibujo (loop = lo que falte de su loop, real = nada, número = lo que falte para N s a la vista; «ask» nunca)",
          (round(motif_hold_secs(_Sx, _Tm, "send", 10.2, ("loop", None)), 6), motif_hold_secs(_Sx, _Tm, "send", 10.2, ("real", None)),
           round(motif_hold_secs(_Sx, _Tm, "send", 11.0, ("secs", 3.0)), 6), motif_hold_secs(_Sx, _Tm, "send", 14.0, ("secs", 3.0)),
           motif_hold_secs(_Sx, _Tm, "ask", 10.2, ("secs", 3.0)), round(motif_hold_secs(_Sx, {"mt": None, "ms": 5.0}, None, 6.0, ("secs", 2.0)), 6)),
          (round((-0.2) % SEND_CYCLE, 6), 0.0, 2.0, 0.0, 0.0, 1.0))
    check("borrado 1.3.2: DLPY_CLEAR_HISTORY manda «ESC[3J» por omisión y no con 0 / no / false / off / vacía",
          [purge_seq(v) for v in (None, "", "0", "no", "false", "OFF", "1", "sí", "abc")],
          ["\x1b[3J", "", "", "", "", "", "\x1b[3J", "\x1b[3J", "\x1b[3J"])
    check("borrado 1.3.2: DLPY_CLEAR (auto = nativo; home / down / purge-first / reset = secuencia con el historial; sin historial si DLPY_CLEAR_HISTORY=0)",
          ([clear_mode_seq(m, "P") for m in ("auto", "", "zzz", "home", "Down", "purge-first", "reset")], clear_mode_seq("home", ""),
           [n for n, _t in CLEAR_MODES]),
          ([None, None, None, "\x1b[H\x1b[2JP\x1b[H", "\x1b[H\x1b[JP", "P\x1b[H\x1b[2J", "\x1bc"], "\x1b[H\x1b[2J\x1b[H",
            ["auto", "home", "down", "purge-first", "reset"]))
    check("borrado 1.3.5: el primer borrado al arrancar es el clear 3 (reset) salvo DLPY_CLEAR_BOOT o un DLPY_CLEAR propio",
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
    check("conversión 1.6.4: sin % y en convert_fast_anim la vía queda quieta y tenue (ningún punto encendido); sin convert_fast_anim un solo punto ● la recorre despacio",
          (_nb(scene_conv_cells(60, 6, ra, rb, 0.05, "VP9", "HEVC", None, fast=True)), _nb(scene_conv_cells(60, 6, ra, rb, 0.05, "VP9", "HEVC", None)) > 0,
           scene_conv_cells(60, 6, ra, rb, 0.05, "VP9", "HEVC", None, fast=True) == scene_conv_cells(60, 6, ra, rb, 3.3, "VP9", "HEVC", None, fast=True),
           scene_conv_cells(60, 6, ra, rb, 0.05, "VP9", "HEVC", None) != scene_conv_cells(60, 6, ra, rb, 2.0 * LOOP_SECS * 0.5, "VP9", "HEVC", None)),
          (0, True, True, True))
    check("conversión 1.2.1: sin recuadro ni compuerta en medio de la vía (ni giratoria ni bloque)",
          [any(ch in rowtxt(c, 12) for ch in "▘▝▗▖▮█▓▒░") for c in (pa0, pa4, pa10, c1, c2)], [False] * 5)
    q1, q2 = (scene_conv_cells(60, 6, ra, rb, lt, "VP9", "HEVC", 42) for lt in (1.0, 2.0))
    check("conversión 1.2.1 (1.6.4): la vía son puntos •; sin avance no hay %; con el mismo avance el reloj no mueve nada (los puntos se pintan con el %)",
          ("•" in rowtxt(q2, 12), "%" not in rowtxt(c1, 13), sorted({y for (x, y) in set(q1) | set(q2) if q1.get((x, y)) != q2.get((x, y))}),
           q1 == scene_conv_cells(60, 6, ra, rb, 1.0, "VP9", "HEVC", 42), len(q1) < 80), (True, True, [], True, True))
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


def _st_t27_loop_y_conversion(check, _carry):
    """[T27.3] ── parte 3 de 9 de _st_t27 (1.8.7): loop y conversion. `_carry` lleva entre partes los valores que las siguientes reutilizan. ──"""
    import io
    cc, cvS, ra, rb, row, rowtxt, stc, t = _carry["cc"], _carry["cvS"], _carry["ra"], _carry["rb"], _carry["row"], _carry["rowtxt"], _carry["stc"], _carry["t"]
    # 1.6.4: DLPY_LOOP, convert_fast_anim y el aviso de la conversión
    check("loop 1.6.4: DLPY_LOOP se interpreta (coma o punto), se acota a 0,2–3 s y lo vacío o inválido da 1 s",
          [loop_secs_parse(v) for v in (None, "", "abc", "1", "0.5", "2,5", "0", "99", "nan", "inf", "-3", " 1.5 ")],
          [1.0, 1.0, 1.0, 1.0, 0.5, 2.5, 0.2, 3.0, 1.0, 1.0, 0.2, 1.5])
    check("loop 1.6.4: el loop predeterminado es de 1 s (sin DLPY_LOOP) y lo demás (paso + asentado, ciclos, unión, limpieza) sale de él",
          (LOOP_SECS_DEFAULT, LOOP_SECS == loop_secs_parse(os.environ.get("DLPY_LOOP")), LOOP_SECS_MIN <= LOOP_SECS <= LOOP_SECS_MAX,
           abs(UX_BEAT - 0.7 * LOOP_SECS) < 1e-9, abs(UX_SETTLE - 0.3 * LOOP_SECS) < 1e-9, UX_HOLD >= LOOP_SECS, GATE_PAID_SECS > LOOP_SECS,
           abs(SCENE_WELCOME_SECS + 0.05 - WELCOME_CYCLE) < 1e-9), (1.0, True, True, True, True, True, True, True))
    check("loop 1.6.4: 24 cuadros por loop (CONV_FPS ≥ 24) para que el movimiento sea fluido",
          CONV_FPS * LOOP_SECS >= 24 * min(1.0, LOOP_SECS) - 1e-9, True)
    check("config 1.6.4: DLPY_LOOP (1) y DLPY_CONVERT_ANIM (1) están en las opciones conocidas",
          ([(n, v) for n, v, _t in CONFIG_OPTIONS if n in ("DLPY_LOOP", "DLPY_CONVERT_ANIM")]), [("DLPY_LOOP", "1"), ("DLPY_CONVERT_ANIM", "1")])
    _fcv = CONVERT_FAST_ANIM
    # un estado nuevo: la conversión entra (cuadro 1) y, 3 s después, ya está quieta en el centro
    _stf = scene_state()
    scene_cells(cvS, _stf, t, t + 0.01, 1)
    # 1.8.1: el sitio se ve su loop entero y solo entonces entra la conversión
    scene_cells(cvS, _stf, t, t + 0.01 + LOOP_SECS + 0.1, 1)
    scene_cells(cvS, _stf, t, t + 3.0, 80)
    _fk = (scene_fast(cvS, _stf, t + 3.0, t), scene_fast(dict(cvS, conv=None), _stf, t + 3.0, t),
           scene_fast(dict(cvS, conv={"codec": "HEVC", "t0": 0.0, "end": 1.0}), _stf, t + 3.0, t),
           scene_fast(dict(cvS, last_error="x"), _stf, t + 3.0, t), scene_fast(dict(cvS, ask={"secs": 5}), _stf, t + 3.0, t),
           scene_fast(cvS, dict(_stf, mcur="rail"), t + 3.0, t), scene_fast(cvS, dict(_stf, mt=t + 2.95), t + 3.0, t),
           scene_fast(cvS, _stf, t - 0.5, t))
    try:
        globals()["CONVERT_FAST_ANIM"] = False
        _fk += (scene_fast(cvS, _stf, t + 3.0, t),)
    finally:
        globals()["CONVERT_FAST_ANIM"] = _fcv
    check("convert_fast_anim 1.6.4: solo se congela la escena cuando corre la conversión y su dibujo ya ocupa el centro sin transformaciones en curso (no con otro dibujo, error, pregunta, cambio de dibujo, intro, conversión ya terminada ni con DLPY_CONVERT_ANIM=0)",
          _fk, (True, False, False, False, False, False, False, False, False))
    _k0 = scene_fast_key(dict(cvS, conv={"pct": 40.2}), 24, 100.0)
    check("convert_fast_anim 1.6.4: la escena solo se repinta si cambia el % entero, el texto, el alto del terminal o cada FAST_REFRESH s",
          (_k0 == scene_fast_key(dict(cvS, conv={"pct": 40.7}), 24, 100.5), _k0 != scene_fast_key(dict(cvS, conv={"pct": 41.0}), 24, 100.0),
           _k0 != scene_fast_key(dict(cvS, conv={"pct": 40.2}, label="Otra cosa"), 24, 100.0), _k0 != scene_fast_key(dict(cvS, conv={"pct": 40.2}), 30, 100.0),
           _k0 != scene_fast_key(dict(cvS, conv={"pct": 40.2}), 24, 100.0 + FAST_REFRESH), scene_fast_key(dict(cvS, conv={"pct": None}), 24, 1.0)[0]),
          (True, True, True, True, True, None))
    check("convert_fast_anim 1.6.4: hay un aviso de espera y la lista va de más largo a más corto (con «no cierres la app» casi siempre)",
          (all(len(a_) > len(b_) for a_, b_ in zip(CONV_NOTICE, CONV_NOTICE[1:])), sum("no cierres la app" in x_.lower() for x_ in CONV_NOTICE), CONV_NOTICE[0].startswith("Espera mientras convierte")),
          (True, 5, True))
    _nt = {W_: scene_conv_notice({}, 6, W_ // 2 + 1, W_) for W_ in (80, 60, 40, 31, 12)}
    _ntx = {W_: "".join(v[0] for (_x, _y), v in sorted(c_.items()) if _y == 6 + SCENE_STATUS_ROW + 1) for W_, c_ in _nt.items()}
    check("convert_fast_anim 1.6.4: el aviso va en la fila bajo el texto de estado, se acorta según el ancho y siempre cabe en pantalla",
          (_ntx[80].startswith("Esperamientrasconvierte·puedetardar"), _ntx[60] == CONV_NOTICE[1].replace(" ", ""), "nocierreslaapp" in _ntx[40], "nocierreslaapp" in _ntx[31].lower(), _ntx[12],
           all(max(x_ for (x_, _y) in c_) < W_ for W_, c_ in _nt.items()), {y_ for c_ in _nt.values() for (_x, y_) in c_}),
          (True, True, True, True, "Espera…", True, {6 + SCENE_STATUS_ROW + 1}))
    check("convert_fast_anim 1.6.4: la escena de conversión lleva el aviso en la fila de abajo del estado; con la conversión terminada ya no",
          ("no cierres la app" in row(cc, 6 + SCENE_STATUS_ROW + 1), "no cierres" in row(scene_cells(dict(cvS, conv={"codec": "HEVC", "t0": 0.0, "end": 1.0}), dict(stc), t, t + 3.2, 90), 6 + SCENE_STATUS_ROW + 1)),
          (True, False))
    _cf = dict(cvS, fast=True, conv={"codec": "HEVC", "t0": 0.0, "end": None, "pct": 42.0}, pct=42.0, busy=True)
    _sf = scene_state()
    scene_cells(dict(_cf, fast=False), _sf, t, t + 0.01, 1)
    scene_cells(dict(_cf, fast=False), _sf, t, t + 3.0, 80)
    f1, f2 = scene_cells(_cf, _sf, t, t + 3.5, 84), scene_cells(_cf, _sf, t, t + 9.77, 234)
    check("convert_fast_anim 1.6.4: en convert_fast_anim el cuadro es estático: el mismo con otro reloj, aunque la regla esté «ocupada» (sin brillo que barre) y la vía quieta",
          (f1 == f2, len(f1) > 100), (True, True))
    _sv = dict(SCENE)
    try:
        SCENE.update(on=True, conv={"codec": "HEVC", "t0": 0.0, "end": None, "pct": None}, pct=None, frac=0.0)
        _FAST_WAKE.clear()
        scene_conv_progress(40.0)
        _wk1 = _FAST_WAKE.is_set()
        _FAST_WAKE.clear()
        scene_conv_progress(40.6)
        _wk2 = _FAST_WAKE.is_set()
        scene_conv_progress(41.2)
        _wk3 = _FAST_WAKE.is_set()
        _FAST_WAKE.clear()
        scene_convert_end()
        _wk4 = (_FAST_WAKE.is_set(), SCENE["conv"]["end"] is not None)
        _FAST_WAKE.clear()
        scene_status("Guardado")
        _wk5 = _FAST_WAKE.is_set()
    finally:
        SCENE.clear()
        SCENE.update(_sv)
        _FAST_WAKE.clear()
    check("convert_fast_anim 1.6.4: el hilo de la escena dormido despierta con un % entero nuevo, al terminar la conversión y con un texto nuevo, pero no con el mismo %",
          (_wk1, _wk2, _wk3, _wk4, _wk5), (True, False, True, (True, True), True))
    check("convert_fast_anim 1.6.4: ffmpeg se lee cada FFMPEG_TICK_FAST con convert_fast_anim y cada FFMPEG_TICK sin él",
          (ux_ffmpeg_tick() == (FFMPEG_TICK_FAST if CONVERT_FAST_ANIM else FFMPEG_TICK), FFMPEG_TICK_FAST > FFMPEG_TICK), (True, True))
    d0, d3, d5 = (scene_dlpy_cells(60, 6, ra, rb, lt, "1.2.3", "boot") for lt in (0.0, 3.0, 5.5))
    check("DLPY: ventana a-Shell con la cadena aSH ► PY ► DLPY boot, la versión y cinco filas",
          ("a-Shell" in rowtxt(d3, 10), all(w in rowtxt(d3, 12) for w in ("aSH", "PY", "DLPY")), "DLpy 1.2.3" in rowtxt(d3, 13),
           {y for (_x, y) in d3} == set(range(10, 15))), (True, True, True, True))
    check("DLPY 1.7.1: en boot el título lleva la versión y no se escribe «boot» (ni en el título ni en el pie); fuera de boot el título sigue siendo el del tema",
          ("1.2.3" in rowtxt(d3, 10), "boot" in rowtxt(d3, 10), "boot" in rowtxt(d3, 13), "DLpy 1.2.3" in rowtxt(d3, 13),
           "yt-dlp" in "".join(v[0] for (x_, y_), v in scene_dlpy_cells(60, 6, ra, rb, 3.0, "1.2.3", "Instalando yt-dlp").items() if y_ == 10)),
          (True, False, False, True, True))
    check("DLPY 1.2.7: el comando empieza vacío, se teclea rápido (0,7 s), se ejecuta y se queda (sin borrarse)",
          tuple("python dlpy.py" in rowtxt(scene_dlpy_cells(60, 6, ra, rb, 3.0, "1.2.3", "boot", tt), 11) for tt in (0.0, 0.4, 0.8, 1.2, 5.0)),
          (False, False, True, True, True))
    check("DLPY 1.2.7: tras el Enter gira el indicador y el paso dura DLPY_STEP_SECS",
          ("|" in rowtxt(scene_dlpy_cells(60, 6, ra, rb, 0.0, "1.2.3", "boot", 0.9), 11), DLPY_STEP_SECS), (True, 1.15))
    _th = threading.Thread(target=time.sleep, args=(3.0,), daemon=True)      # 1.3.3: un hilo de escena «vivo»
    _th.start()
    _sm = SCENE_MODE
    try:
        # 1.7.1: wait es el predeterminado; se fija aquí para que la prueba no dependa del entorno
        globals()["SCENE_MODE"] = ("loop", None)
        SCENE.update(on=True, brand=True, label="Comprobando pip", label_wall=time.time(), last_error=None, frac=0.0, pct=None, dl_done=None, th=_th, welcome=None, stop=False)
        _tm = threading.Timer(0.3, lambda: SCENE.__setitem__("dl_done", "Comprobando pip"))
        _tm.start()
        _t0 = time.time()
        scene_status("Actualizando pip")
        _dt = time.time() - _t0
        _w1 = (0.25 <= _dt < 1.5, SCENE.get("label"), SCENE.get("dl_done"))
        SCENE.update(dl_done=None, label="Comprobando pip")
        _t0 = time.time()
        # la escena no lo mostró: tope
        _w2 = (scene_wait_step("Comprobando pip", limit=0.2), 0.15 <= time.time() - _t0 < 1.0)
        SCENE["dl_done"] = "Comprobando pip"
        # ya mostrado: no espera
        _w3 = scene_wait_step("Comprobando pip", limit=0.2)
        globals()["SCENE_MODE"] = ("real", None)
        SCENE["dl_done"] = None
        _t0 = time.time()
        # real: cambia al instante
        _w4 = (scene_wait_step("Comprobando pip", limit=0.5), time.time() - _t0 < 0.1)
        globals()["SCENE_MODE"] = _sm
        SCENE.update(brand=False)
        _t0 = time.time()
        # si D L P Y no es lo que se ve, no espera
        _w5 = (scene_wait_step("Comprobando pip", limit=0.5), time.time() - _t0 < 0.1)
        SCENE.update(brand=True, th=None)
        _t0 = time.time()
        # sin hilo de escena vivo, no espera
        _w6 = (scene_wait_step("Comprobando pip", limit=0.5), time.time() - _t0 < 0.1)
        SCENE.update(th=_th, last_error="x")
        # tras un error, tampoco
        _w7 = scene_wait_step("Comprobando pip", limit=0.5)
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
    _carry.update(da=da, dg=dg, dy=dy)


def _st_t27_updates_en_escena(check, _carry):
    """[T27.4] ── parte 4 de 9 de _st_t27 (1.8.7): updates en escena. `_carry` lleva entre partes los valores que las siguientes reutilizan. ──"""
    import io
    # ── 1.4.4: DLPY_UPDATES (una sola variable), resultados reales en la escena, comprobaciones en paralelo, modo calmado ──
    import socket as _sk
    import urllib.error as _ue
    import urllib.request as _ur
    check("1.9.6: parse_updates (horas): on = -1 · 0/off = 0 · número solo = días · unidades m/h/d/w · daily/weekly/hourly · mínimo 1 min · vacío o texto raro = 1 semana",
          [parse_updates(x) for x in ("on", "ON", "siempre", "always", "off", "nunca", "0", "0.5", "1", "3", "7", "1,5", "", None, "abc", "-1", "-5")],
          [-1.0, -1.0, -1.0, -1.0, 0.0, 0.0, 0.0, 12.0, 24.0, 72.0, 168.0, 36.0, 168.0, 168.0, 168.0, 168.0, 168.0])
    check("1.9.6: parse_updates con unidades (30m, 30 min, 6h, 2d, 1w, 2 semanas, weekly, daily, hourly, 0.001m, 5x)",
          [parse_updates(x) for x in ("30m", "30 min", "6h", "2d", "1w", "2 semanas", "weekly", "daily", "hourly", "0.001m", "5x", "1.5h", "90 minutos")],
          [0.5, 0.5, 6.0, 48.0, 168.0, 336.0, 168.0, 24.0, 1.0, UPDATES_MIN_HOURS, 168.0, 1.5, 1.5])
    check("1.9.6: el predeterminado es semanal (168 h)", UPDATES_DEFAULT, 168.0)
    check("1.9.6: --config acepta DLPY_UPDATES con unidades y rechaza lo raro",
          [config_validate("DLPY_UPDATES", x) for x in ("30m", "6H", "2d", "1w", "1,5", "on", "0", "off", "weekly", "5x", "abc")],
          [(True, "30m"), (True, "6h"), (True, "2d"), (True, "1w"), (True, "1.5"), (True, "on"), (True, "0"), (True, "0"), (True, "weekly"), (False, None), (False, None)])
    _ud = UPDATE_HOURS
    try:
        _dd = {}
        for _lab, _days in (("nunca", 0.0), ("siempre", -1.0), ("1 día", 24.0), ("medio día", 12.0)):
            globals()["UPDATE_HOURS"] = _days
            _dd[_lab] = (due_from(None), due_from({"t": 1000, "sig": "a"}, "a", 1000 + 3600), due_from({"t": 1000, "sig": "a"}, "a", 1000 + 13 * 3600),
                         due_from({"t": 1000, "sig": "a"}, "a", 1000 + 25 * 3600), due_from({"t": 1000, "sig": "a"}, "b", 1000 + 60))
    finally:
        globals()["UPDATE_HOURS"] = _ud
    check("1.4.4: due_from con DLPY_UPDATES: 0 nunca toca (ni con firma nueva) · siempre toca siempre · N días toca al pasar N días",
          _dd,
          {"nunca": (False,) * 5, "siempre": (True,) * 5, "1 día": (True, False, False, True, True), "medio día": (True, False, True, True, True)})
    check("1.9.6: update_every_text (min · h · días · semanas)", [update_every_text(x) for x in (-1.0, 0.0, 0.5, 1 / 60.0, 1.0, 6.0, 24.0, 72.0, 36.0, 168.0, 336.0)],
          ["en cada arranque", "nunca", "cada 30 min", "cada minuto", "cada hora", "cada 6 h", "cada día", "cada 3 días", "cada 1.5 días", "cada semana", "cada 2 semanas"])
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
    check("1.5.2: DLPY_UPDATES manda; sin ella, las variables de la 1.4.3 siguen valiendo (NO_UPDATE = nunca · CHECK_HOURS / 24); por omisión, 1 semana",
          _res, [168.0, 168.0, 0.0, -1.0, 0.0, 48.0, 168.0, 48.0])
    _names = [o[0] for o in CONFIG_OPTIONS]
    check("1.9.6: --config tiene UNA variable de actualizaciones (1w = semanal por omisión) y la de modo calmado",
          ("DLPY_UPDATES" in _names, "DLPY_CHECK_HOURS" in _names, "DLPY_NO_UPDATE" in _names, "DLPY_CALM" in _names,
           [o[1] for o in CONFIG_OPTIONS if o[0] == "DLPY_UPDATES"], "script y de sus dependencias" in [o[2] for o in CONFIG_OPTIONS if o[0] == "DLPY_UPDATES"][0]),
          (True, False, False, True, ["1w"], True))
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
               "Downloading yt_dlp-2026.whl", "1/3 listas", "DLpy 1.4.4 · yt-dlp", "DLpy 1.4.4"])
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
    def _ej_run(cur, scene, ok=True):
        """1.7.1: corre check_js_components con todo lo de fuera simulado; devuelve (textos de la escena, instalaciones pedidas, preguntas hechas)."""
        notes, pips, asks, inst = [], [], [], [cur]
        def _pip(spec):
            pips.append(spec)
            if ok:
                inst[0] = "0.8.0"
            return ok
        def _ask(*a, **k):
            asks.append(a[0])
            return True
        def _note(text, hold=0.0):
            notes.append(text)
            return scene
        _nop = lambda *a, **k: None
        patch = {"ytdlp_needs_js": lambda *a, **k: True, "js_runtime": lambda: ("node", "/x/node"), "ejs_pin": lambda *a, **k: "yt-dlp-ejs==0.8.0",
                 "pkg_version": lambda *a, **k: inst[0], "is_installed": lambda *a, **k: inst[0] is not None, "pip_install": _pip, "ux_on": lambda: scene,
                 "ux_note": _note, "ask": _ask, "m_warn": _nop, "m_check": _nop, "note": _nop, "declined_clear": _nop, "declined_set": _nop,
                 "load_json": lambda *a, **k: {}}
        saved = {k: globals()[k] for k in patch}
        try:
            globals().update(patch)
            check_js_components(True)
        finally:
            globals().update(saved)
        return notes, pips, len(asks)
    _e1, _e2, _e3, _e4, _e5 = _ej_run(None, True), _ej_run("0.7.0", True), _ej_run("0.8.0", True), _ej_run(None, True, ok=False), _ej_run(None, False)
    check("1.7.1: la escena D L P Y instala yt-dlp-ejs sin preguntar y muestra «Instalando» y su ✓",
          _e1, (["Instalando yt-dlp-ejs==0.8.0", "yt-dlp-ejs 0.8.0 · instalado"], ["yt-dlp-ejs==0.8.0"], 0))
    check("1.7.1: la escena D L P Y también ACTUALIZA yt-dlp-ejs (versión distinta de la que pide yt-dlp) sin preguntar",
          _e2, (["Actualizando yt-dlp-ejs==0.8.0", "yt-dlp-ejs 0.8.0 · actualizada"], ["yt-dlp-ejs==0.8.0"], 0))
    check("1.7.1: con yt-dlp-ejs al día la escena solo lo verifica («para YouTube»): no instala ni pregunta",
          _e3, (["yt-dlp-ejs 0.8.0 · para YouTube"], [], 0))
    check("1.7.1: si yt-dlp-ejs no se pudo instalar la escena lo dice (✗) y no se queda con el texto de «Instalando»",
          _e4, (["Instalando yt-dlp-ejs==0.8.0", "No se pudo instalar yt-dlp-ejs"], ["yt-dlp-ejs==0.8.0"], 0))
    check("1.7.1: sin escena (UIM) yt-dlp-ejs se sigue preguntando antes de instalar", (_e5[1], _e5[2]), (["yt-dlp-ejs==0.8.0"], 1))
    _ej_lab = ("Actualizando yt-dlp-ejs==0.8.0", "yt-dlp-ejs 0.8.0 · actualizada", "No se pudo actualizar yt-dlp-ejs", "No se pudo instalar yt-dlp-ejs")
    check("1.7.1: la escena D L P Y entiende los textos de yt-dlp-ejs (comando, estado y traducción al idioma activo)",
          (_dlpy_topic(_ej_lab[0]), [_dlpy_state(x) for x in _ej_lab], t_status(_ej_lab[0], lang="en"), t_status(_ej_lab[2], lang="en")),
          (("yt-dlp-ejs", "pip install -U yt-dlp-ejs==0.8.0 --no-deps"), ["run", "ok", "fail", "fail"], "Updating yt-dlp-ejs==0.8.0", "Could not update yt-dlp-ejs"))
    _hs = PREFETCH.get("hosts")
    try:
        PREFETCH["hosts"] = prefetch_hosts(["DLpy", "pip", "yt-dlp"])
        _tp = _dlpy_topic("Comprobando actualizaciones")
    finally:
        PREFETCH["hosts"] = _hs
    check("1.4.4: prefetch_hosts y el comando de la escena en paralelo",
          (prefetch_hosts(["DLpy", "pip", "yt-dlp"]), prefetch_hosts(["pip"]), prefetch_hosts(["DLpy"]), _tp),
          ("pypi.org x2 · github.com", "pypi.org", "github.com", ("actualizaciones", "GET pypi.org x2 · github.com")))
    _carry.update(_ue=_ue, v=v)


def _st_t27_prefetch_y_pip(check, _carry):
    """[T27.5] ── parte 5 de 9 de _st_t27 (1.8.7): prefetch y pip. `_carry` lleva entre partes los valores que las siguientes reutilizan. ──"""
    import io
    _ue, da, dg, dy, ra, rb, rowtxt, v = _carry["_ue"], _carry["da"], _carry["dg"], _carry["dy"], _carry["ra"], _carry["rb"], _carry["rowtxt"], _carry["v"]
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

    # 1.8.7: sh_run es el único punto de lanzamiento de comandos y normaliza el código de salida
    _os_sys = os.system
    try:
        _shr = []
        for _v in (0, 1, 255, 256, 512):
            os.system = lambda c, _v=_v: _v
            _shr.append(sh_run("x"))
    finally:
        os.system = _os_sys
    check("1.8.7: sh_run devuelve el código real (el estado de espera × 256 se normaliza)", _shr, [0, 1, 255, 1, 2])

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
    # 1.7.2: esta prueba mide el ruido: no depende de DLPY_GLITCH del entorno
    _gl0, globals()["GLITCH"] = GLITCH, True
    mids = [scene_swap_cells(o_, n_, q / 10.0, 3, ra, rb) for q in range(1, 10)]
    check("transición del centro: en 0 el viejo, en 1 el nuevo, a mitad hay ruido y es repetible",
          (scene_swap_cells(o_, n_, 0.0, 3, ra, rb) == o_, scene_swap_cells(o_, n_, 1.0, 3, ra, rb) == n_,
           any(v[0] in SITE_GLITCH for m in mids for v in m.values()),
           mids == [scene_swap_cells(o_, n_, q / 10.0, 3, ra, rb) for q in range(1, 10)]), (True, True, True, True))
    globals()["GLITCH"] = _gl0
    # 1.7.2: DLPY_GLITCH=0 → ninguna escena pasa por ruido
    _gl = GLITCH
    try:
        globals()["GLITCH"] = False
        _gm = [scene_swap_cells(o_, n_, q / 10.0, 3, ra, rb) for q in range(0, 11)]
        _gt = [scene_morph({0: "a", 1: "b"}, {0: "c"}, q / 10.0, 3) for q in range(0, 11)]
        _gs = "".join(_subst_text("VIEJO", q / 10.0, 3) for q in range(0, 11))
    finally:
        globals()["GLITCH"] = _gl
    check("1.7.2: DLPY_GLITCH=0: el cambio de dibujo, el de texto y el chip viejo no sacan ruido y los extremos (0 y 1) no cambian",
          (any(v[0] in SITE_GLITCH for m in _gm for v in m.values()), any(k_ == 1 for m in _gt for _c, k_ in m.values()),
           any(ch_ in SITE_GLITCH for ch_ in _gs), _gm[0] == o_, _gm[-1] == n_), (False, False, False, True, True))
    check("1.7.2: --config trae DLPY_GLITCH (1 por omisión) y DLPY_CALM sigue aparte",
          ([(n, v) for n, v, _t in CONFIG_OPTIONS if n in ("DLPY_GLITCH", "DLPY_CALM")], ), ([("DLPY_GLITCH", "1"), ("DLPY_CALM", "0")], ))
    check("escena: qué dibujo ocupa el centro (D L P Y manda; al terminar la conversión, el del sitio)",
          [scene_motif_kind({"brand": True, "conv": {"end": None}}), scene_motif_kind({"conv": {"end": None}}),
           scene_motif_kind({"conv": {"end": 1.0}}), scene_motif_kind({})], ["dlpy", "conv", None, None])
    _carry.update(_rt=_rt)


def _st_t27_union_guardado_limpieza(check, _carry):
    """[T27.6] ── parte 6 de 9 de _st_t27 (1.8.7): union guardado limpieza. `_carry` lleva entre partes los valores que las siguientes reutilizan. ──"""
    import io
    ra, rb, v = _carry["ra"], _carry["rb"], _carry["v"]
    # 1.1.3: escenas de unión, guardado y envío
    def _rt(cs, y):
        return "".join(cs[(x, y)][0] if (x, y) in cs else " " for x in range(1, 70)).strip()
    check("escena 1.1.3: el dibujo del centro según el texto de estado (D L P Y > conversión > unión > guardado)",
          [scene_motif_kind(x) for x in ({"label": "Uniendo pistas"}, {"label": "Ajustando pistas"}, {"label": "Guardado"},
                                         {"label": "Descargando video"}, {"label": "Uniendo pistas", "conv": {"end": None}},
                                         {"label": "Guardado", "brand": True}, {"label": "Enviando a DLpy", "brand": True},
                                         {"label": "Enviando a DLpy"}, {"label": "Enviando a DLpy", "brand": True, "last_error": "x"})],
          ["rail", "rail", "rail", "rail", "conv", "dlpy", "send", "send", "dlpy"])   # 1.9.8: «Enviando» sin D L P Y también es envío
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
    check("guardado: el archivo, la carpeta y, al llegar, el punto de llegada ● (1.5.9: el ✓ ya no va en el dibujo, solo en el estado de la escena)",
          ("▓▓▓" in _rt(sv0, 12), os.path.basename(FILES_DIR) in _rt(sv0, 12), "●" in _rt(sv0, 12), "●" in _rt(sv1, 12), "✓" in _rt(sv1, 12),
           {y for (_x, y) in sv1} == {11, 12, 13}), (True, True, False, True, False, True))
    _rd = []
    for _k_, _cs_ in (("save", MOTIFS["save"].draw({}, {}, _MotifCtx(60, 6, ra, rb, SAVE_STREAM_SECS + 0.5, 3, {}, set()), 0.0)),
                      ("subst", MOTIFS["subst"].draw({}, {}, _MotifCtx(60, 6, ra, rb, SWAP_STREAM_SECS + 0.5, 3, {}, set()), 0.0))):
        _cc_ = scene_chrome(_k_, _cs_, {}, {}, _MotifCtx(60, 6, ra, rb, 0.0, 3, {}, set()), -(SAVE_STREAM_SECS + SWAP_STREAM_SECS + 0.5))
        _rd.append(sum(1 for v in _cc_.values() if v[0] == "✓"))
    for _kd in ("video", "save"):
        _cr = rail_card_cells({"kind": _kd, "state": "hecho", "pct": 100.0, "fade": 1.0, "exit": None, "x": 5.0, "born": 0.0}, 6, ra, rb, 1.0, 15)
        _rd.append(sum(1 for v in _cr.values() if v[0] == "✓"))
    check("1.5.9: el ✓ sale UNA sola vez por animación terminada (guardado, sustitución y tarjetas de video y guardado), nunca dentro del dibujo y otra vez en el estado",
          _rd, [1, 1, 1, 1])
    check("guardado: repetible, se mueve mientras guarda, cabe en 31 columnas y con «files» si falta sitio",
          (sv0 == scene_save_cells(60, 6, ra, rb, 0.3), sv0 != scene_save_cells(60, 6, ra, rb, 0.5),
           max(x for (x, _y) in scene_save_cells(31, 6, ra, rb, 0.3)) < 31, max(x for (x, _y) in scene_save_cells(31, 6, ra, rb, 1.8)) < 31,
           "files" in _rt(scene_save_cells(31, 6, ra, rb, 0.3), 12)), (True, True, True, True, True))
    se0, se1 = scene_send_cells(60, 6, ra, rb, 0.5 * SEND_CYCLE / SEND_BASE, "DLPY"), scene_send_cells(60, 6, ra, rb, 1.2 * SEND_CYCLE / SEND_BASE, "DLPY")
    check("envío: el chip del atajo, el cometa en vuelo (●) y la onda al llegar",
          ("DLPY" in _rt(se0, 12), "●" in _rt(se0, 12), "●" in _rt(se1, 12), "(" in _rt(se1, 12) and ")" in _rt(se1, 12),
           "(" in _rt(se0, 12), {y for (_x, y) in se0} == {11, 12, 13}), (True, True, False, True, False, True))
    check("envío: ciclo que se repite, repetible, se mueve y cabe en 31 columnas",
          (scene_send_cells(60, 6, ra, rb, 0.25) == scene_send_cells(60, 6, ra, rb, 0.25 + SEND_CYCLE), se0 == scene_send_cells(60, 6, ra, rb, 0.5 * SEND_CYCLE / SEND_BASE, "DLPY"),
           se0 != scene_send_cells(60, 6, ra, rb, 0.7 * SEND_CYCLE / SEND_BASE), max(x for (x, _y) in scene_send_cells(31, 6, ra, rb, 1.1, "ABCDEFGH")) < 31,
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
    sg = {"geo": (60, 24, 6, 19), "a": ra, "b": rb, "brand": False, "conv": None, "label": "Uniendo pistas", "done": set()}
    stg = {"mcur": None, "mprev": None, "mt": None, "ms": 0.0, "msp": 0.0, "site_done": set(), "site_done_at": {}, "site_prev_cells": {}, "site_trans_t": None}
    for q, tt_ in enumerate((2.0, 2.3, 2.9)):
        scene_motif(sg, stg, {(30, 11): ("x", ra, None)}, tt_, 1.16, q)
    check("escena 1.1.3: «Uniendo pistas» toma el centro (1.4.6: como tarjeta del carril)", stg["mcur"], "rail")
    sg["label"] = "Guardado"
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
          (t_display("papelera") in _rt(ce1, 12), {y for (_x, y) in ce1} == {11, 12, 13}, ce1 == scene_empty_cells(60, 6, ra, rb, 0.3, 3), ce1 != ce2,
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
    # a los 5.3 s del ciclo ya no hay paquete ni estela
    _wq = scene_wait_conv_cells(60, 6, ra, rb, 5.3, "VP9", "HEVC", 15.0)
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
    _w0, _w1 = scene_subst_cells(60, 6, ra, rb, 0.03), scene_subst_cells(60, 6, ra, rb, SWAP_STREAM_SECS + 0.5)
    check("1.4.2: al guardar sustituyendo: el paquete cruza, el viejo se deshace y queda el punto de llegada ● con NUEVO (1.5.9: sin ✓ en el dibujo)",
          ("VIEJO" in _rt(_w0, 12), "●" not in _rt(_w0, 12), "VIEJO" not in _rt(_w1, 12), "NUEVO" in _rt(_w1, 12), "●" in _rt(_w1, 12) and "✓" not in _rt(_w1, 12),
           MOTIFS["subst"].draw({}, {}, _MotifCtx(60, 6, ra, rb, 4.0, 3, {}, set()), 4.0) == scene_subst_cells(60, 6, ra, rb, 0.0),
           motif_loop_left({"geo": (60, 24, 6, 19)}, {"ms": 0.0, "mt": None}, "subst", 0.3) == max(0.0, SWAP_STREAM_SECS + UX_SETTLE - 0.3)), (True,) * 7)
    _dd2 = _MotifCtx(60, 6, ra, rb, 5.0, 3, {"v": ("1080p", 1.0), "a": ("AAC", 1.0)}, set())
    _S2 = {"geo": (60, 24, 6, 19), "a": ra, "b": rb, "mode": "both", "mode_orig": "both", "aspect": 16 / 9.0, "res": 1080, "ask": {"secs": 20, "t0": time.time(), "src": "VIEJO", "dst": "NUEVO"},
           "conv": None, "label": "x", "clean": 3, "check": {"items": None, "verdict": None}}
    _rows = {k: {y for (_x, y) in m.draw(_S2, {"ms": 4.0, "mt": None, "cinfo": ("VP9", "HEVC", 4.0)}, _dd2, 4.0)} for k, m in MOTIFS.items() if k not in ("dlpy", "send", "first", "updated", "rail")}
    check("1.4.2: ningún dibujo del centro invade la fila en blanco ni el texto de estado (todos dentro de y0+4 … y0+9); el estado va en y0+11",
          (all(r and max(r) <= 6 + 4 + BADGE_ROW and min(r) >= 6 + 4 for r in _rows.values()), SCENE_STATUS_ROW - (4 + BADGE_ROW), SCENE_ROWS), (True, 3, SCENE_STATUS_ROW + (4 if BOTTOMBAR else 2)))
    check("escena 1.1.7: el vaciado va a CONV_FPS",
          scene_fps({"label": "Vaciando · 2 de la papelera"}, {}, 20.0, SITE_HOLD_AT * SITE_SECS), CONV_FPS)
    check("escena 1.1.5: la limpieza va a CONV_FPS",
          scene_fps({"label": "Limpiando · 2 a la papelera"}, {}, 20.0, SITE_HOLD_AT * SITE_SECS), CONV_FPS)
    hq, stq = SITE_HOLD_AT * SITE_SECS, {"mt": 10.0, "t": 0.0, "tt": None}
    check("escena: cuadros por segundo (intro, transiciones y cierre a tope; convirtiendo y DLPY, menos)",
          [scene_fps({}, {}, 0.5, hq), scene_fps({"brand": True}, stq, 10.3, hq), scene_fps({"brand": True}, stq, 20.0, hq),
           scene_fps({"conv": {"end": None}}, stq, 20.0, hq), scene_fps({"conv": {"end": None}, "k_out": 0.2}, stq, 20.0, hq),
           scene_fps({"conv": {"end": 3.0}}, stq, 20.0, hq)], [SITE_FPS, SITE_FPS, DLPY_FPS, CONV_RUN_FPS, SITE_FPS, SITE_FPS])
    _carry.update(_rt=_rt)


def _st_t27_motivos_y_cierre(check, _carry):
    """[T27.7] ── parte 7 de 9 de _st_t27 (1.8.7): motivos y cierre. `_carry` lleva entre partes los valores que las siguientes reutilizan. ──"""
    import io
    _rt, ra, rb, v = _carry["_rt"], _carry["ra"], _carry["rb"], _carry["v"]
    # ── 1.4.1: registro de dibujos (MOTIFS), estado unificado, bolsas de streams y cierre ──
    _kn = {"dlpy", "conv", "ask", "replace", "subst", "check", "merge", "save", "clean", "empty", "send", "first", "updated", "downgrade", "same", "ahead", "download", "idle", "rail"}
    _sn = {scene_motif_kind(x) for x in ({"label": "Revisando archivo"}, {"label": "Uniendo pistas"}, {"label": "Ajustando pistas"},
                                         {"label": "Guardado"}, {"label": "Sustituyendo"}, {"label": "x", "ask": {"kind": "replace"}},
                                         {"label": "Limpiando · 3"}, {"label": "Vaciando · 3"}, {"label": "x", "brand": True},
                                         {"label": "Enviando a DLpy", "brand": True}, {"conv": {"end": None}},
                                         {"label": "Convirtiendo", "ask": {"secs": 20}}, {"label": "x", "brand": True, "welcome": {"kind": "first"}},
                                         {"label": "x", "brand": True, "welcome": {"kind": "updated"}},
                                         {"label": "x", "brand": True, "welcome": {"kind": "downgrade"}}, {"label": "x", "brand": True, "welcome": {"kind": "same"}},
                                         {"label": "x", "brand": True, "welcome": {"kind": "ahead"}},
                                         {"label": "Descargando video"}, {"label": "Guardado"}, {"label": "Preparando", "past_dl": True})}
    check("escena 1.4.1: MOTIFS tiene una fila por dibujo, cada estado cae en una y lo demás no pide dibujo",
          (set(MOTIFS) == _kn, _sn == (_kn - set(RAIL_KINDS)) | {"rail"}, all(callable(m.draw) for m in MOTIFS.values()), scene_motif_kind({"label": "Preparando"})),
          (True, True, True, None))
    check("escena 1.4.1: solo unión, guardado, limpieza, papelera, revisión, arranque, descarga y pulso van a CONV_FPS (marca light)",
          {k for k, m in MOTIFS.items() if m.light}, {"merge", "save", "subst", "clean", "empty", "first", "updated", "downgrade", "same", "ahead", "download", "idle", "rail"})
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
           scene_idle_cells(60, 6, ra, rb, 0.25) == scene_idle_cells(60, 6, ra, rb, 0.25 + PULSE_CYCLE),
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
        # 1.7.0: el primer avance ya mueve «Preparando descarga» a «Descargando» y se anota
        scene_progress(10.0)
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
          (_p0, _p1, _p2), (({1: 10.0}, False), ({1: "video", 2: "audio"}, {1: 40.0, 2: None}, True, "Descargando audio es-US 2/2"), {1: 40.0, 2: 100.0}))
    sj = {"geo": (60, 24, 6, 19), "a": ra, "b": rb, "brand": False, "conv": None, "label": "Preparando descarga", "done": set(), "mode_orig": "both",
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
    _Sl, _Tl = {"geo": (60, 24, 6, 19)}, {"ms": 0.0, "mt": None}
    check("escena 1.4.1: el loop de cada dibujo sale del registro (sin loop = 0)",
          {k: round(motif_loop_left(_Sl, _Tl, k, 0.3), 6) for k in ("ask", "dlpy", "send", "merge", "first", "updated", "downgrade", "same", "ahead", "clean", "empty", "save", "download", "idle", None)},
          {"ask": 0.0, "dlpy": 0.0, "send": round((-0.3) % SEND_CYCLE, 6), "merge": round((-0.3) % (4.0 / MERGE_SPEED), 6),
           "first": round((-0.3) % WELCOME_CYCLE, 6), "updated": round((-0.3) % WELCOME_CYCLE, 6),
           "downgrade": round((-0.3) % WELCOME_CYCLE, 6), "same": round((-0.3) % WELCOME_CYCLE, 6), "ahead": round((-0.3) % WELCOME_CYCLE, 6),
           "clean": round((-0.3) % (1.0 / CLEAN_SPEED), 6), "empty": round((-0.3) % (1.0 / CLEAN_SPEED), 6),
           "save": round(max(0.0, SAVE_STREAM_SECS + UX_SETTLE - 0.3), 6), "download": round((-0.3) % DOWN_CYCLE, 6),
           # 1.8.1: None = el sitio, con su loop
           "idle": round((-0.3) % PULSE_CYCLE, 6), None: round((-0.3) % LOOP_SECS, 6)})
    # 1.6.3: TODAS las animaciones con loop duran ~LOOP_SECS (0,5 s): wait espera ese loop entero y real no espera nada
    _KL = ("merge", "clean", "empty", "send", "first", "updated", "download", "idle", "save", "subst", "conv", "check")
    _Sq = lambda W, ck: {"geo": (W, 24, 6, 17), "check": ck, "ta": 100.0}
    _Tq = {"ms": 0.0, "mt": None, "cinfo": ("VP9", "HEVC", 0.0)}
    _cks = (({"items": None, "verdict": None, "t": None}, 0.0), ({"items": None, "verdict": "ok", "t": 100.0 - 0.1}, 0.0), ({"items": None, "verdict": "ok", "t": 100.0 - 2.3}, 0.0))
    _mxl = {k: max(motif_loop_left(_Sq(W, ck), _Tq, k, 0.013 * i) for i in range(0, 400) for W in (31, 60, 80) for ck, _z in _cks) for k in _KL}
    check("loops 1.6.3: ninguna animación tarda más de LOOP_SECS en cerrar su loop (conversión, revisión, guardar, sustituir, unión, limpieza, envío, descarga, Pulso, estreno y novedad)",
          {k: v <= (WELCOME_CYCLE if k in ("first", "updated") else LOOP_SECS) + 1e-6 for k, v in _mxl.items()}, {k: True for k in _KL})      # 1.7.1: la bienvenida dura WELCOME_CYCLE (2 s)
    check("loops 1.6.3: ninguna se queda en 0 de más (cada loop dura de verdad ~LOOP_SECS, no una fracción): el máximo de cada una ≥ LOOP_SECS − 6/conv_flow",
          {k: v >= (WELCOME_CYCLE if k in ("first", "updated") else LOOP_SECS) - 0.3 for k, v in _mxl.items() if k != "conv"}, {k: True for k in _KL if k != "conv"})
    _sq0 = _Sq(60, _cks[0][0])
    check("modo 1.6.3: real nunca retiene un dibujo (hold 0 en todos); wait lo retiene lo que le falta a su loop (≤ LOOP_SECS)",
          ({k: motif_hold_secs(_sq0, _Tq, k, 0.3, ("real", None)) for k in _KL if k != "check"} == {k: 0.0 for k in _KL if k != "check"},
           all(0.0 <= motif_hold_secs(_sq0, _Tq, k, 0.3, ("loop", None)) <= (WELCOME_CYCLE if k in ("first", "updated") else LOOP_SECS) + 1e-6 for k in _KL)), (True, True))
    check("loops 1.6.3 (1.6.4 / 1.8.2): las constantes cuadran con LOOP_SECS (paso + asentado · fin de la conversión · ciclos · limpieza · unión · parpadeo); carril: hold corto + salida rápida",
          (abs(UX_BEAT + UX_SETTLE - LOOP_SECS) < 1e-9, abs(CONV_END_HOLD - LOOP_SECS) < 1e-9,
           SEND_CYCLE == DOWN_CYCLE == PULSE_CYCLE == LOOP_SECS and WELCOME_CYCLE == 2.0, abs(1.0 / CLEAN_SPEED - LOOP_SECS) < 1e-9,
           abs(4.0 / MERGE_SPEED - LOOP_SECS) < 1e-9, 0.05 <= rail_hold(("loop", None)) <= 0.25, 0.15 <= RAIL_EXIT_T <= 0.45, rail_hold(("real", None)),
           abs(CHECK_BLINK_SECS - LOOP_SECS) < 1e-9),
          (True, True, True, True, True, True, True, 0.0, True))
    check("conversión 1.6.3: conv_flow cruza la vía en CONV_TRAVEL (nunca menos de CONV_FLOW) y las vías de 31 y 60 columnas caben en LOOP_SECS",
          (abs(conv_flow(14) * CONV_TRAVEL - 14) < 1e-9, conv_flow(1) == CONV_FLOW,
           all(_conv_geo(W_, "VP9", "HEVC")[4] / conv_flow(_conv_geo(W_, "VP9", "HEVC")[4]) <= CONV_TRAVEL + 1e-9 for W_ in (31, 60, 80))), (True, True, True))
    _dd = _MotifCtx(60, 6, ra, rb, 5.0, 3, {}, set())
    _sd = {"clean": 3, "send_to": None, "welcome": {"kind": "updated", "old": "1.2.8", "new": "1.2.9"}}
    check("escena 1.4.1: el registro pinta igual que las funciones *_cells (guardado, limpieza, papelera, envío, primera ejecución, actualizado)",
          (MOTIFS["save"].draw(_sd, {}, _dd, 4.0) == scene_save_cells(60, 6, ra, rb, 1.0),
           MOTIFS["clean"].draw(_sd, {}, _dd, 4.0) == scene_clean_cells(60, 6, ra, rb, 1.0, 3),
           MOTIFS["empty"].draw(_sd, {}, _dd, 4.0) == scene_empty_cells(60, 6, ra, rb, 1.0, 3),
           MOTIFS["send"].draw(_sd, {}, _dd, 4.0) == scene_send_cells(60, 6, ra, rb, 1.0, scene_chip_text(SHORTCUT_NAME)),
           MOTIFS["first"].draw(_sd, {}, _dd, 4.0) == scene_first_cells(60, 6, ra, rb, 1.0),
           MOTIFS["updated"].draw(_sd, {}, _dd, 4.0) == scene_updated_cells(60, 6, ra, rb, 1.0, "1.2.8", "1.2.9"),
           MOTIFS["downgrade"].draw(_sd, {}, _dd, 4.0) == scene_downgrade_cells(60, 6, ra, rb, 1.0, "1.2.8", "1.2.9"),
           MOTIFS["same"].draw(_sd, {}, _dd, 4.0) == scene_same_cells(60, 6, ra, rb, 1.0, "1.2.8", "1.2.9", False),
           MOTIFS["ahead"].draw(_sd, {}, _dd, 4.0) == scene_ahead_cells(60, 6, ra, rb, 1.0, "1.2.8", "1.2.9"),
           MOTIFS["same"].draw(dict(_sd, welcome={"kind": "same", "old": "1.2.9", "new": "1.2.9", "edited": True}), {}, _dd, 4.0)
           == scene_same_cells(60, 6, ra, rb, 1.0, "1.2.9", "1.2.9", True)),
          (True,) * 10)
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
    sm = {"geo": (60, 24, 6, 19), "a": ra, "b": rb, "brand": True, "conv": None}
    stm = {}
    # entra DLPY y a mitad vuelve el sitio: marcha atrás sin saltos (1.5.5: tiempos al doble de velocidad)
    for q, tt_ in enumerate((2.0, 2.1, 2.2)):
        scene_motif(sm, stm, {(30, 11): ("x", ra, None)}, tt_, 1.16, q)
    sm["brand"] = False
    scene_motif(sm, stm, {(30, 11): ("x", ra, None)}, 2.25, 1.16, 9)
    check("escena: si D L P Y se apaga a mitad de la transición, vuelve atrás desde donde iba",
          (stm["mcur"], stm["mprev"], round(1.0 - (2.25 - 2.0 - SCENE_LAG_MOTIF) / SCENE_SWAP, 3) == round((2.25 - stm["mt"]) / SCENE_SWAP, 3)), (None, "dlpy", True))


def _st_t27_flujo_visual(check, _carry):
    """[T27.8] ── parte 8 de 9 de _st_t27 (1.8.7): flujo visual. `_carry` lleva entre partes los valores que las siguientes reutilizan. ──"""
    import io
    ra, rb, status_row, v = _carry["ra"], _carry["rb"], _carry["status_row"], _carry["v"]
    # 1.0.6: flujo visual: suavizado por tiempo, iris desde el centro, cascada título → centro → texto y cambios sin saltos
    check("escena 1.0.6: el suavizado depende del tiempo, no de los cuadros (1 cuadro de 1/12 s = 2 de 1/24 s)",
          (round(scene_ease(0.0, 1.0, SCENE_BAR_RATE, 1 / 12.0), 6) == round(scene_ease(scene_ease(0.0, 1.0, SCENE_BAR_RATE, 1 / 24.0), 1.0, SCENE_BAR_RATE, 1 / 24.0), 6),
           scene_ease(0.3, 0.3, 5.0, 0.1), scene_ease(0.0, 1.0, 5.0, 0.0), scene_ease(0.0, 1.0, 5.0, 99.0) < 1.0), (True, 0.3, 0.0, True))
    wo = {(x, 5): ("a", ra, None) for x in range(10, 31)}
    wn = {(x, 5): ("b", rb, None) for x in range(10, 31)}
    # 1.7.2: esta prueba mide el ruido a mitad de la transición: no depende de DLPY_GLITCH del entorno
    _gl2, globals()["GLITCH"] = GLITCH, True
    wm = scene_swap_cells(wo, wn, 0.4, 3, ra, rb)
    changed = lambda m: sorted(x for (x, _y), v in m.items() if v[0] != "a")
    ch_x = changed(wm)
    check("transición del centro 1.0.6: abre desde el medio (lo que ya cambió está más cerca del centro que lo que no)",
          (len(ch_x) > 0, sum(abs(x - 20) for x in ch_x) / len(ch_x) < sum(abs(x - 20) for x in range(10, 31)) / 21.0,
           scene_swap_cells(wo, wn, 0.0, 3, ra, rb) == wo, scene_swap_cells(wo, wn, 1.0, 3, ra, rb) == wn, scene_swap_cells({}, {}, 0.5, 3, ra, rb)),
          (True, True, True, True, {}))
    globals()["GLITCH"] = _gl2
    sc = {"geo": (60, 24, 6, 19), "a": ra, "b": rb, "name": "YouTube", "mode": "video", "title_raw": "Pan casero", "brand": False,
          "busy": False, "label": "Analizando enlace", "pct": 10, "shown": 0.2, "k_out": None, "conv": None}
    sk = {"rows": {}, "lab": None, "prev": "", "full": "", "t": 0.0, "tcur": None, "tprev": None, "tt": None}
    t0_ = SITE_HOLD_AT * SITE_SECS
    scene_cells(sc, sk, t0_, t0_ + 0.01, 1)
    scene_cells(sc, sk, t0_, t0_ + 3.0, 60)                                # todo en reposo
    sc["brand"], sc["label"], sc["pct"] = True, "Comprobando DLpy", None  # cambian a la vez título, centro y texto
    scene_cells(sc, sk, t0_, t0_ + 3.1, 62)
    check("escena 1.0.6: en cascada, el centro y el texto esperan al título",
          (sk["tt"], round(sk["mt"] - 3.1 - t0_, 3), round(sk["t"] - 3.1 - t0_, 3)), (t0_ + 3.1, SCENE_LAG_MOTIF, SCENE_LAG_LABEL))
    sd = {"geo": (60, 24, 6, 19), "a": ra, "b": rb, "name": "YouTube", "mode": "video", "title_raw": "", "brand": False,
          "busy": False, "label": "Preparando", "pct": None, "shown": 0.2, "k_out": None, "conv": None}
    skd = {"rows": {}, "lab": None, "prev": "", "full": "", "t": 0.0, "tcur": None, "tprev": None, "tt": None}
    scene_cells(sd, skd, t0_, t0_ + 0.01, 1)
    scene_cells(sd, skd, t0_, t0_ + 3.0, 60)
    # como con yt-dlp desinstalado (scene_note)
    sd["brand"], sd["busy"], sd["label"], sd["dl_done"] = True, True, "Instalando yt-dlp", None
    scene_cells(sd, skd, t0_, t0_ + 3.1, 61)
    _en = skd["mt"]
    _row = lambda c: "".join(c[(x, 11)][0] for x in range(1, 61) if (x, 11) in c)
    _full = "pip install -U yt-dlp --no-deps"
    # el dibujo apenas empieza a aparecer
    _ca = scene_cells(sd, skd, t0_, _en + 0.1, 62)
    # ya se ve y se está tecleando
    _cb = scene_cells(sd, skd, t0_, _en + SCENE_SWAP + DLPY_TYPE_AT + 0.25, 63)
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
    # el dibujo D L P Y se deshace
    _cf = scene_cells(sd, skd, t0_, _en + 9.0 + SCENE_LAG_MOTIF + SCENE_SWAP / 2, 68)
    check("escena 1.3.3: al deshacerse D L P Y conserva su comando (no pasa a «python dlpy.py»)",
          ("python dlpy.py" in _row(_cf).replace("  ", " "), "dlpy.py" in "".join(v[0] for v in _cf.values())), (False, False))
    c0 = scene_cells(sc, sk, t0_, t0_ + 3.1 + SCENE_LAG_LABEL / 2, 63)
    check("escena 1.0.6: durante la espera el texto sigue siendo el viejo (nada parpadea)",
          "".join(c0[(x, status_row)][0] for x in range(1, 61) if (x, status_row) in c0).replace(" ", "").startswith("Analizandoenlace"), True)
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
    # el fundido de vuelta termina en cuadros de 0.05 s
    for q in range(40):
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
    # 1.0.8: los errores (stderr de yt-dlp, etc.) van a internal/logs/errors.log y se indican en D L P Y
    check("error en escena: texto corto y limpio", [scene_error_text("Error al descargar: ERROR: unable to download video data: HTTP Error 403: Forbidden"),
                                                     scene_error_text("\x1b[0;31mERROR:\x1b[0m   video no disponible"), scene_error_text("x" * 100, 20)],
          ["unable to download video data: HTTP Error 403: Forbidden", "video no disponible", "x" * 19 + "\u2026"])
    import io
    import tempfile
    _tmp_dir = tempfile.mkdtemp(prefix="dlpy_t27_")
    _tmp_log = os.path.join(_tmp_dir, "errors.log")
    _tmp_warn = os.path.join(_tmp_dir, "warnings.log")
    _old_log, _old_warn = globals()["SHORTCUTMODE_LOG"], globals()["WARNING_LOG_FILE"]
    globals()["SHORTCUTMODE_LOG"], globals()["WARNING_LOG_FILE"] = _tmp_log, _tmp_warn
    _real_err = io.StringIO()
    _em = _SceneErrMute(_real_err)
    try:
        _em.write("\x1b[0;31mERROR:\x1b[0m unable to download video data: HTTP Error 403: Forbidden\nsegunda")
        _em.write(" linea\n\n")
        _em.write("sin salto")
        _em.drain()
        _em.write("WARNING: formato alternativo detectado\n")
        _logged = open(_tmp_log, encoding="utf-8").read().splitlines()
        _warned = open(_tmp_warn, encoding="utf-8").read().splitlines()
        check("stderr en escena: errores y warnings se separan sin llegar a pantalla",
              (_real_err.getvalue(), [ln.split(" [ERROR] ", 1)[1] for ln in _logged],
               [ln.split(" [WARNING] ", 1)[1] for ln in _warned]),
              ("", ["stderr: ERROR: unable to download video data: HTTP Error 403: Forbidden", "stderr: segunda linea", "stderr: sin salto"],
               ["stderr: WARNING: formato alternativo detectado"]))
        _em.open = True
        _em.write("ya abierta\n")
        check("stderr: con la escena cerrada pasa tal cual", _real_err.getvalue(), "ya abierta\n")
    finally:
        globals()["SHORTCUTMODE_LOG"], globals()["WARNING_LOG_FILE"] = _old_log, _old_warn
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


def _st_t27_etiquetas_y_lista(check, _carry):
    """[T27.9] ── parte 9 de 9 de _st_t27 (1.8.7): etiquetas y lista. `_carry` lleva entre partes los valores que las siguientes reutilizan. ──"""
    import io
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
    hint_row = 6 + SCENE_STATUS_ROW - 1
    ask_row = hint_row + 1
    estimate_row = hint_row + 2
    _r1 = "".join(_ac[(x, ask_row)][0] for x in range(0, 60) if (x, ask_row) in _ac)
    _r2 = "".join(_ac[(x, estimate_row)][0] for x in range(0, 60) if (x, estimate_row) in _ac)
    check("pedir Enter: ocupa las dos filas del estado, centrado, y respeta lo demás",
          (_r1, _r2.startswith("~3min·sinrespuestaseconvierte"), (5, 12) in _ac, (6, 6) in _ac, abs((min(x for x, y in _ac if y == ask_row) + max(x for x, y in _ac if y == ask_row)) / 2 - 25) <= 1),
          ("Enterconvertir·rremux·noriginal", True, True, True, True))
    check("pedir Enter 1.2.0: la ayuda fluye de «Toca la pantalla…» a «¿Convertir este video?» según el ancho",
          (ask_hint_texts(60), ask_hint_texts(30), ask_hint_texts(20), ask_hint_texts(9)),
          (("Toca la pantalla para abrir el teclado", "¿Convertir este video?", 0), ("Toca para abrir el teclado", "¿Convertir este video?", 0),
           ("Toca = teclado", "¿Convertir ahora?", 0), ("", "¿Convertir?", 0)))
    def _hx(tt):
        _c = scene_ask_cells({}, {"est": 200, "secs": 20, "t0": time.time(), "ta0": 0.0}, tt, 6, 25, 48, lambda k: (200, 100, 50))
        return "".join(v[0] for (x, y), v in sorted(_c.items()) if y == hint_row)
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
        # 1.1.4: «r» en la escena = solo remux, sin recodificar el video
        _ans[0] = "r"
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
    # 1.7.2: esta prueba mide el ruido: no depende de DLPY_GLITCH del entorno
    _gl3, globals()["GLITCH"] = GLITCH, True
    try:
        _bc = badge_cells(30, 12, "LIVE", 0.0, 1.0, (255, 0, 0), (0, 0, 255))
        _bc1 = badge_cells(30, 12, "LIVE", 1.0, 1.0, (255, 0, 0), (0, 0, 255))
    finally:
        globals()["GLITCH"] = _gl3
    check("etiqueta: al cambiar sale del ruido y luego queda el texto", ("LIVE" in "".join(v[0] for v in _bc.values()),
          "".join(v[0] for _, v in sorted(_bc1.items())).strip()), (False, "LIVE"))
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
    check("mix6: GRAD_STEPS pasos (0.4 cae en 13/32)", (GRAD_STEPS, mix6(BLACK, WHITE, 0.4), mix6(BLACK, WHITE, 0.5)), (32, mix(BLACK, WHITE, 13 / 32.0), mix(BLACK, WHITE, 0.5)))
    _ra, _rb = (255, 0, 0), (255, 154, 164)
    _dif = [max(abs(x - y) for x, y in zip(mix6(_ra, _rb, i / 100.0), mix6(_ra, _rb, (i + 1) / 100.0))) for i in range(100)]
    check("mix6 1.9.7: sin saltos bruscos (rojo → rosa: ≤ 8 niveles entre vecinos al 1 %)", max(_dif) <= 8, True)
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
    # revertida: el «nuevo» es el viejo y en 0.6 se vuelve a ver el cuadro de 0.4
    f3 = scene_flow_step(stf, "flow", cnv, vid, 0.6, 5, ra, rb)
    check("morph: el plan se mide una vez, no cambia entre cuadros y la reversa pasa por el mismo cuadro",
          (stf["flow"]["plan"] is pl, f1 != f2, f3 == f1, scene_flow_step({}, "flow", vid, cnv, 0.0, 1, ra, rb) == vid, scene_flow_step({}, "flow", vid, cnv, 1.0, 1, ra, rb) == cnv),
          (True, True, True, True, True))
    # texto: lo que se comparte se desliza, lo demás sale del ruido
    c0, c1 = scene_cols("Descargando video", 30), scene_cols("Descargando audio 2", 30)
    sl = morph_slides(c0, c1)
    check("texto: los tramos compartidos se emparejan (en orden, sin cruzarse) y una letra suelta lejana no",
          (len(sl) >= 11, all(a_[0] < b_[0] and a_[1] < b_[1] for a_, b_ in zip(sl, sl[1:])), sl == morph_slides(c0, c1),
           morph_slides(scene_cols("abc", 10), scene_cols("xyzc", 30)) == []), (True, True, True, True))
    t0_, t1_ = scene_morph(c0, c1, 0.0, 3), scene_morph(c0, c1, 1.0, 3)
    # 1.7.2: esta prueba mide el ruido: no depende de DLPY_GLITCH del entorno
    _gl4, globals()["GLITCH"] = GLITCH, True
    try:
        tm, _tm2 = scene_morph(c0, c1, 0.5, 3), scene_morph(c0, c1, 0.5, 3)
    finally:
        globals()["GLITCH"] = _gl4
    check("texto: en 0 el viejo, en 1 el nuevo, a mitad las letras compartidas no hacen ruido y el resto sí",
          ("".join(v[0] for _x, v in sorted(t0_.items())), "".join(v[0] for _x, v in sorted(t1_.items())), tm == _tm2,
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
    check("carril 1.4.6 / 1.8.5: unión conserva su tarjeta; el guardado ya no inventa una tarjeta activa",
          ([w["state"] for w in rail_want(dict(_Wr, label="Uniendo pistas"))], [w["id"] for w in rail_want(dict(_Wr, label="Uniendo pistas"))],
           [w["id"] for w in rail_want(dict(_Wr, label="Guardando"))], [w["id"] for w in rail_want(dict(_Wr, label="Guardado"))],
           rail_want({"label": "Analizando"})),
          (["hecho", "hecho", "activa"], ["video", "audio", "merge"], ["video", "audio"], ["video", "audio"], []))
    check("carril 1.4.6: caben 3 tarjetas en cualquier ancho (de 31 a 80 columnas)",
          all(3 * rail_width(w_) + 2 * RAIL_GAP <= w_ - 2 and 8 <= rail_width(w_) <= 16 for w_ in range(31, 81)), True)
    _Tr = {}
    _sm_rail = SCENE_MODE
    # 1.7.1: wait es el predeterminado; se fija aquí para que la prueba no dependa del entorno
    globals()["SCENE_MODE"] = ("loop", None)
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
    globals()["SCENE_MODE"] = _sm_rail
    for q in range(1, 40):
        rail_step(_Wr, _Tr, 60, 1.9 + q * 0.05, 0.0)
    check("carril 1.4.6: la tarjeta que salió ya no está y la otra queda centrada", ([c["id"] for c in _R0["cards"]], _R0["cards"][0]["x"] == _R0["cards"][0]["tx"]), (["audio"], True))
    _Wr.update(label="Uniendo pistas", spct={1: 100.0, 2: 100.0})
    # 1.5.5: un cuadro corto (dt 0.02 s); con la entrada al doble de velocidad, uno de 0.15 s ya la acerca casi del todo
    rail_step(_Wr, _Tr, 60, 3.87, 0.0)
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
    _Wf = {"label": "Guardado", "past_dl": True, "stream_total": 3, "stream_seen": 3, "mode_orig": "audio", "skind": {1: "video", 2: "audio", 3: "audio"},
           "spct": {1: 100.0, 2: 100.0, 3: 50.0}}
    _Tf = {}
    _Rf = rail_step(_Wf, _Tf, 60, 1.0, 0.0)
    check("carril 1.8.5: después del guardado solo quedan las tarjetas reales de pista; no se inventa una de GUARDADO",
          ([c["id"] for c in _Rf["cards"]], any(c["id"] == "save" for c in _Rf["cards"])),
          ([], False))
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
    check("UX 1.5.1: wait · real · cualquier número son los segundos; los nombres de antes siguen y lo vacío o inválido cae en wait (1.7.1)",
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
           _rt(scene_chrome("save", MOTIFS["save"].draw(_Sc, _Tc, _Dc, 5.0), _Sc, _Tc, _Dc, 5.6), 15) != "✓",
           not any(v[0] == "━" for (x, y), v in scene_chrome("conv", MOTIFS["conv"].draw(dict(_Sc, conv={"pct": 90.0}), _Tc, _Dc, 5.0),
                                                              dict(_Sc, conv={"pct": 90.0}), _Tc, _Dc, 5.0).items() if y == 14)),
          ("", "espera", "✓", True, True))
    _Cs = {"id": "t1", "kind": "video", "pct": 25.0, "state": "activa", "x": 20.0, "tx": 20.0, "fade": 1.0, "exit": None, "exit_t": None, "done_t": None, "born": 0.0}
    _cr = rail_card_cells(_Cs, 6, ra, rb, 5.7, 10)
    check("estilo 1.4.8: la tarjeta del carril y la escena de ancho completo usan las mismas filas, la misma etiqueta/estado y el mismo color de etiqueta",
          (_rt(_cr, 10), _rt(_cr, 15), {y for (_x, y) in _cr if y in (10, 14, 15)}, {y for (_x, y) in _ch["conv"] if y in (10, 14, 15)},
           {v[1] for (_x, y), v in _cr.items() if y == 10}, {v[1] for (_x, y), v in _ch["conv"].items() if y == 10}),
          # 1.5.6: ni barra (fila 14) ni % (fila 15) en una escena activa: solo etiqueta y dibujo
          ("VIDEO", "", {10}, {10}, {SCENE_WHITE}, {SCENE_WHITE}))
    _cb = rail_card_cells(_Cs, 6, ra, rb, 5.7, 12, {"v": ("1080p", None)})
    check("carril 1.5.0: la tarjeta activa no lleva % (ni con barra real ni sin ella); con dato del archivo, solo ese dato; hecho y espera igual que antes",
          ("%" in _rt(_cb, 15), _rt(_cb, 15), "%" in _rt(rail_card_cells(dict(_Cs, pct=None), 6, ra, rb, 5.7, 10), 15),
           _rt(rail_card_cells(dict(_Cs, state="hecho"), 6, ra, rb, 5.7, 10), 15), _rt(rail_card_cells(dict(_Cs, state="espera"), 6, ra, rb, 5.7, 10), 15)),
          (False, "1080p", False, "✓", "espera"))
    check("carril 1.4.6: la que sale pasa por detrás de las que se quedan (no se mezclan los glifos)",
          all(not ({x for (x, _y) in scene_rail_cells(60, 6, ra, rb, [dict(_Cc, x=float(xe), exit="left", exit_t=0.0, id="e"), dict(_Cc, x=20.0, id="v")], 1.0)
                    if 20 <= x < 20 + rail_width(60)} - {x for (x, _y) in rail_card_cells(dict(_Cc, x=20.0), 6, ra, rb, 1.0, rail_width(60))}) for xe in (14, 18, 24)), True)
    check("carril 1.4.6: «Carril» es un motivo con nombre; descarga, unión y guardado lo piden (D L P Y, conversión y espera mandan)",
          (motif_name("rail"), [scene_motif_kind(x) for x in ({"label": "Descargando audio 2/2"}, {"label": "Uniendo pistas"}, {"label": "Guardado"},
                                                              {"label": "Guardado", "brand": True}, {"label": "Guardado", "conv": {"end": None}})]),
          ("Carril", ["rail", "rail", "rail", "dlpy", "conv"]))
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


_UX_MARK = {"ux": "# ═══════════════════ ÁREA UX", "ux_end": "# ═══════════════════ FIN ÁREA UX",
            "st": "# ───────────────────────── [K1] Autoprueba", "st_end": "# ─────────────── [K2] Funciones",
            "est": "# ── [UX-estado] inicio", "est_end": "# ── [UX-estado] fin"}


def _ux_scan(code):
    """1.5.7: (nombres de la UX, fugas). Fuga = un nombre de nivel superior del área UX (o SCENE) usado fuera de ella sin ser ux_* ni UX_SHARED.
    No cuentan: la autoprueba, la cabeza, el bloque [UX-estado] y los nombres que esa misma función asigna como locales."""
    import ast
    ls = code.split("\n")
    pos = {k: next(i for i, l in enumerate(ls, 1) if l.startswith(v)) for k, v in _UX_MARK.items()}
    tree = ast.parse(code)
    ux = set()
    for n in tree.body:
        if pos["ux"] <= n.lineno <= pos["ux_end"]:
            if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
                ux.add(n.name)
            elif isinstance(n, ast.Assign):
                ux.update(t.id for t in n.targets if isinstance(t, ast.Name))
    watch = ux | {"SCENE", "scene_defaults"}
    leaks = {}
    for n in tree.body:
        top = min([n.lineno] + [d.lineno for d in getattr(n, "decorator_list", [])])
        if pos["ux"] <= top <= pos["ux_end"] or pos["st"] <= top < pos["st_end"] or pos["est"] <= top <= pos["est_end"]:
            continue
        nodes = list(ast.walk(n))
        stores = {x.id for x in nodes if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Store)}
        for x in nodes:
            if isinstance(x, ast.Name) and x.id in watch and x.id not in stores and not x.id.startswith("ux_") and x.id not in UX_SHARED:
                leaks.setdefault(x.id, x.lineno)
    return ux, leaks


_UIM_PROHIBIDO = {"names": {"grad", "mix", "mix6", "SITE_GLITCH", "_rn", "theme_rgb", "ANIM_LIVE", "_fg", "_bg", "OUTRO", "smooth", "TRUECOLOR",
                            "outro_clear", "site_intro", "ux_site_intro", "ux_early_site_intro", "ux_site_theme_apply"}, "attrs": {"Thread"}}


def _uim_scan(code):
    """1.5.8: lo decorativo (degradados, ruido, hilos, intro, disolución, colores del sitio) que aparece dentro del área UIM. Debe ser {}."""
    import ast
    ls = code.split("\n")
    a = next(i for i, l in enumerate(ls, 1) if l.startswith("# ═══════════════════ ÁREA UIM"))
    b = next(i for i, l in enumerate(ls, 1) if l.startswith("# ═══════════════════ FIN ÁREA UIM"))
    found = {}
    for n in ast.parse(code).body:
        if a <= n.lineno <= b:
            for x in ast.walk(n):
                if isinstance(x, ast.Name) and x.id in _UIM_PROHIBIDO["names"]:
                    found.setdefault(x.id, x.lineno)
                elif isinstance(x, ast.Attribute) and x.attr in _UIM_PROHIBIDO["attrs"]:
                    found.setdefault(x.attr, x.lineno)
    return found


def _st_t29_separacion(check):
    """[T29] ── 1.5.7: UX (escena de shortcutmode) y UIM (interfaz sin shortcutmode) separadas: lo de fuera solo habla con la escena por el puente ux_* ──"""
    try:
        with open(os.path.abspath(__file__), encoding="utf-8") as fh:
            code = fh.read()
    except OSError:
        check("separación UX/UIM: sin acceso al propio código (se omite)", True, True)
        return
    ux, leaks = _ux_scan(code)
    check("separación UX/UIM: el área UX tiene su escena (motores, dibujos, carril) y el puente", [len(ux) > 150, "scene_note" in ux, "ux_download_stream" in ux], [True, True, True])
    check("separación UX/UIM: nada fuera de la UX usa nombres internos de la escena sin pasar por ux_* (UIM, núcleo, F/G/H/I/J/L)", sorted(leaks), [])
    fake = "\n".join([_UX_MARK["ux"], "def scene_note(x):", "    pass", _UX_MARK["ux_end"], _UX_MARK["st"], _UX_MARK["st_end"],
                      _UX_MARK["est"], "SCENE = {}", _UX_MARK["est_end"], "def ux_note(*a):", "    return scene_note(*a)",
                      "def uim():", "    scene_note(1)", "    return SCENE['on']"])
    check("separación UX/UIM: la comprobación sí detecta una fuga (el puente ux_* sí puede llamar a la escena; una función de la UIM no)",
          sorted(_ux_scan(fake)[1]), ["SCENE", "scene_note"])
    check("UIM simple: dentro del área UIM no hay degradados, ruido, hilos, intro, disolución ni colores del sitio", _uim_scan(code), {})
    check("UIM simple: la comprobación sí detecta lo decorativo (grad, mix y Thread dentro de la UIM)",
          sorted(_uim_scan("\n".join(["# ═══════════════════ ÁREA UIM", "import threading", "def f():", "    grad('x')", "    mix(1, 2, 3)",
                                        "    threading.Thread(target=f)", "# ═══════════════════ FIN ÁREA UIM"]))), ["Thread", "grad", "mix"])
    check("UIM simple: sin hilos de barra ni disolución propia (no existen Bar._loop, outro_clear ni OUTRO_HOLD)",
          [hasattr(Bar, "_loop"), "outro_clear" in globals(), "OUTRO_HOLD" in globals()], [False] * 3)
    api = [n for n in ("ux_on", "ux_get", "ux_set", "ux_pop", "ux_status", "ux_note", "ux_stop", "ux_download_begin", "ux_download_stream",
                       "ux_download_progress", "ux_download_stream_done", "ux_pp_start", "ux_pp_progress") if not callable(globals().get(n))]
    check("separación UX/UIM: el puente ux_* está completo", api, [])
    ok = ux_on() is False and ux_get("no_existe") is None and ux_pop("no_existe") is None
    ux_set(_t29=1)
    ok = ok and ux_get("_t29") == 1 and ux_pop("_t29") == 1 and ux_get("_t29") is None
    check("separación UX/UIM: ux_on / ux_get / ux_set / ux_pop sin escena (neutros) y sin dejar rastro en SCENE", ok, True)
    ux_pp_progress(50.0)
    check("separación UX/UIM: sin escena ux_pp_progress no guarda nada", SCENE.get("pp_pct"), None)



def _st_t30_idioma(check):
    """[T30] ── 1.7.0: idioma completo (DLPY_LANG) en UX y UIM ──"""
    _saved_lang = LANG
    try:
        # parseo
        check("idioma: parseo de códigos y nombres", [lang_parse("en"), lang_parse("en-US"), lang_parse("English"), lang_parse("pt-BR"), lang_parse("français"), lang_parse("de"), lang_parse("it"), lang_parse(""), lang_parse("xx"), lang_parse("español")], ["en", "en", "en", "pt", "fr", "de", "it", None, None, "es"])
        # cada clave del catálogo se traduce en los 5 idiomas
        _all = True
        for _code in ("en", "pt", "fr", "de", "it", "ru", "zh", "hi", "ar", "ja", "ko"):
            for _k, _v in I18N[_code].items():
                if t_display(_k, lang=_code) != _v:
                    _all = False
        check("idioma: todas las claves del catálogo traducen en los 11 idiomas", _all, True)
        check("idioma: es no traduce (canónico)", t_display("Descargando audio", lang="es"), "Descargando audio")
        check("idioma: prefijo con variable", t_display("Descargando audio 2/3", lang="en"), "Downloading audio 2/3")
        check("idioma: segmentos ·", t_display("Revisando · ya es compatible", lang="en"), "Checking · already compatible")
        check("idioma: set_lang", set_lang("en"), "en")
        check("idioma: LANG global tras set_lang", LANG, "en")
        check("idioma: CONV_NOTICE traducido", [t_display(t) for t in CONV_NOTICE[:2]], ["Wait while it converts · it may take a while · do not close the app", "Wait while it converts · do not close the app"])
        check("idioma: SCB_NOTES traducido", [t_display(t) for t in SCB_NOTES], ["Quick analysis ran out of time", "Continuing without a time limit", "Analyzing link · may take longer"])
        check("idioma: MOTIF_NAMES traducido", [t_display(MOTIF_NAMES[k]) for k in ("check", "merge", "save", "download", "conv")], ["Checking file", "Merge", "Saved", "Download", "Conversion"])
        _motif_expected = {
            "en": ("First run", "Checking file", "Replacing"),
            "pt": ("Primeira execução", "Verificando arquivo", "Substituindo"),
            "fr": ("Premier lancement", "Vérification du fichier", "Remplacement"),
            "de": ("Erster Start", "Datei wird geprüft", "Ersetzen"),
            "it": ("Primo avvio", "Verifica file", "Sostituzione"),
            "ru": ("Первый запуск", "Проверка файла", "Замена"),
            "zh": ("首次运行", "正在检查文件", "替换中"),
            "hi": ("पहली बार चलाया गया", "फ़ाइल की जाँच हो रही है", "बदला जा रहा है"),
            "ar": ("التشغيل الأول", "جارٍ فحص الملف", "جارٍ الاستبدال"),
            "ja": ("初回実行", "ファイルを確認中", "置換中"),
            "ko": ("첫 실행", "파일 확인 중", "교체 중"),
        }
        check("idioma: motivos de primera ejecución, comprobación y sustitución en los 11 idiomas",
              {c: tuple(t_display(MOTIF_NAMES[k], lang=c) for k in ("first", "check", "replace")) for c in _motif_expected}, _motif_expected)
        check("idioma: etiquetas antiguas ya no significan estreno, review ni handoff",
              (t_display("Estreno", lang="en"), t_display("Revisión", lang="en"), t_display("Relevo", lang="en")),
              ("First run", "Checking file", "File replacement"))
        check("idioma: DLPY título/pie traducido (en y ja, no queda «analizando»)", [_dlpy_title_for_ctx("analizando"), _dlpy_footer("Analizando enlace", "run", "1.7.0", "analizando", 36)[0], _net_line({"ok": False, "err": "timeout"}, "get"), t_display("analizando", lang="ja")], [" a-Shell · analyzing ", "DLpy 1.7.0 · analyzing", "timeout · retry on open", "解析中"])
        # ── [T31] idiomas nuevos, animaciones traducidas, reparación «Preparando descarga» y medidor de velocidad ──
        _lang_save = LANG
        for _c, _exp in (("ru", "Подготовка загрузки"), ("zh", "准备下载"), ("hi", "डाउनलोड की तैयारी"), ("ar", "جارٍ تحضير التنزيل"), ("ja", "ダウンロード準備中"), ("ko", "다운로드 준비 중")):
            globals()["LANG"] = _c
            check("idioma nuevo: " + _c + " traduce «Preparando descarga» y las etiquetas de animación",
                  [t_display("Preparando descarga"), t_display("VIDEO"), t_display("AUDIO"), t_display("UNIÓN"), t_display("GUARDADO"), t_display("PISTA"), t_display("espera"), ask_est_text(45), ask_est_text(200)],
                  [_exp, I18N[_c]["VIDEO"], I18N[_c]["AUDIO"], I18N[_c]["UNIÓN"], I18N[_c]["GUARDADO"], I18N[_c]["PISTA"], I18N[_c]["espera"], "~45 " + I18N[_c]["seg"], "~3 " + I18N[_c]["min"]])
        globals()["LANG"] = _lang_save
        check("idioma nuevo: los 6 catálogos cubren todas las claves", [len(I18N[c]) for c in ("ru", "zh", "hi", "ar", "ja", "ko")], [len(I18N["en"])] * 6)
        check("idioma nuevo: frases de los 6 idiomas", [len(I18N_PHRASES[c]) for c in ("ru", "zh", "hi", "ar", "ja", "ko")], [10] * 6)
        check("idioma nuevo: alias de los 6 idiomas", [lang_parse(x) for x in ("русский", "chino", "hindi", "árabe", "japonés", "coreano", "ru", "zh", "hi", "ar", "ja", "ko")], ["ru", "zh", "hi", "ar", "ja", "ko"] * 2)
        _sd = dict(SCENE)
        SCENE.update({"on": True, "label": "Preparando descarga", "pct": None, "frac": 0.08, "lo": 0.0, "hi": 0.0, "stream_seen": 1, "busy": True})
        _sc = dict(_scene_bag("spct"))
        scene_progress(40.0)
        check("reparación: el primer avance mueve «Preparando descarga» a «Descargando»", (SCENE["label"], SCENE["pct"], SCENE["busy"]), ("Descargando", 40.0, False))
        _scene_bag("spct").clear(); _scene_bag("spct").update(_sc); SCENE.update(_sd)
        _du = DownloadUI()
        _du._hook({"status": "downloading", "downloaded_bytes": 100, "total_bytes": 1000, "info_dict": {}})
        _du._hook({"status": "downloading", "downloaded_bytes": 200, "total_bytes": 1000, "filename": "video.mp4", "info_dict": {"format_id": "137"}})
        check("reparación: la primera pista se abre aunque el primer hook llegue sin nombre", (_du.seen, _du.key), (1, "video.mp4"))
        _c1 = scene_speed_cells(60, 6, (0, 0, 0), (255, 255, 255), 0.0, 1000000.0, 2000000.0)
        _c2 = scene_speed_cells(60, 6, (0, 0, 0), (255, 255, 255), LOOP_SECS, 1000000.0, 2000000.0)
        _c3 = scene_speed_cells(60, 6, (0, 0, 0), (255, 255, 255), LOOP_SECS / 4.0, 1000000.0, 2000000.0)
        check("velocidad: loop de 1 s que cierra limpio y se mueve en el medio", (_c1 == _c2, _c1 != _c3, bool(_c1), all(y == 6 + SCENE_STATUS_ROW - 1 for (_x, y) in _c1)), (True, True, True, True))
        check("idioma: ask_lines traducido", scene_ask_lines(60, None, 10), ("Tap the screen · Enter convert · r remux · n keep original", "no answer: it converts · 10 s"))
        # 1.7.1: UX unificada: el texto de las animaciones sale del idioma activo, se traduce antes de medirlo y se mide por su ancho real
        _ux_ok = {"chips": True, "wide": True, "es_idle": True, "l1": True, "l2": True, "touch": True, "hint": True, "keys": True, "left": True, "enter": True, "subst": True}
        _es_words = ("sustituir", "respuesta", "pantalla", "VIEJO", "NUEVO")
        for _code in LANG_CODES:
            globals()["LANG"] = _code
            _o, _n = ux_chip("VIEJO"), ux_chip("NUEVO")
            if not (_o and _n and dwidth(_o) <= CHIP_COLS and dwidth(_n) <= CHIP_COLS and ((_code == "es") == (_o == "VIEJO" and _n == "NUEVO"))):
                _ux_ok["chips"] = False
            if _code == "es" and (ux_text("Toca = teclado") != "Toca = teclado" or ux_enter_key() != "Enter"):
                _ux_ok["es_idle"] = False
            for _kind in (None, "replace"):
                for _room in (70, 60, 42, 30, 20, 12, 8):
                    _l1, _l2 = scene_ask_lines(_room, 200, 7.0, _kind)
                    _la, _lb, _lk = ask_hint_texts(_room, _kind)
                    if _room >= 12 and (dwidth(_l1) > _room or dwidth(_l2) > _room):
                        _ux_ok["l1"] = False
                    if _room >= 20 and (dwidth(_la) > _room or dwidth(_lb) > _room):
                        _ux_ok["hint"] = False
                    if _code != "es" and any(w in _l1 + _l2 + _la + _lb for w in _es_words):
                        _ux_ok["l2"] = False
                if not (_ask_l1(70, _kind)[1] and not _ask_l1(12, _kind)[1]):
                    _ux_ok["touch"] = False
                _kl = ask_key_mask(scene_ask_lines(60, None, 5, _kind)[0])
                _first = scene_ask_lines(60, None, 5, _kind)[0].split(" · ")[1 if _ask_l1(60, _kind)[1] else 0]
                if not (set(range(0, 0)) <= _kl and any(_first.startswith(nm) for nm in ux_enter_names()) and len(_kl) >= 3):
                    _ux_ok["keys"] = False
            _kw = scene_enter_chip(17)
            if _kw[0] != ux_enter_key() or _kw[1] != dwidth(ux_enter_key()) + 4 or scene_enter_chip(9)[0] != "↵":
                _ux_ok["enter"] = False
            _sc = {x for (_x, _y), (ch, _c, _b) in scene_subst_cells(60, 6, (255, 0, 0), (0, 0, 255), 0.03).items() for x in (ch,)}
            _txt = "".join(ch for (_xy, (ch, _c, _b)) in sorted(scene_subst_cells(60, 6, (255, 0, 0), (0, 0, 255), SWAP_STREAM_SECS + 0.5).items(), key=lambda kv: (kv[0][1], kv[0][0])))
            if _n not in _txt.replace(" ", "") and _code != "es":
                _ux_ok["subst"] = False
            if _code == "es" and "NUEVO" not in _txt:
                _ux_ok["subst"] = False
        globals()["LANG"] = "en"
        check("1.7.1: motor de texto de las animaciones: chips VIEJO / NUEVO traducidos (≤ 8 columnas), es canónico, líneas y pistas sin español ni desbordes en los 12 idiomas, «Toca la pantalla» por bandera (no por texto), tecla Enter por idioma y Sustituyendo con los rótulos del idioma",
              _ux_ok, {k: True for k in _ux_ok})
        # 1.7.2: el motor de texto llega a TODAS las animaciones: unión (VIDEO / AUDIO), papelera (limpieza / vaciado), marcadores «¿RES?»… del video y el error de D L P Y
        _flat_ = lambda cs: "".join(ch for (_xy, (ch, _c, _b)) in sorted(cs.items(), key=lambda kv: (kv[0][1], kv[0][0])))
        _un_ok = {"merge": True, "trash": True, "ph": True, "bounds": True, "err": True}
        _ph_keys = tuple(PH_VIDEO.values()) + (PH_AUDIO["hz"],)
        for _code in LANG_CODES:
            globals()["LANG"] = _code
            _mg = scene_merge_cells(60, 6, (255, 0, 0), (0, 0, 255), 1.0)
            if not (t_display("VIDEO") in _flat_(_mg) and t_display("AUDIO") in _flat_(_mg)):
                _un_ok["merge"] = False
            _ce_ = _flat_(scene_empty_cells(60, 6, (255, 0, 0), (0, 0, 255), 0.3, 3)) + _flat_(scene_clean_cells(60, 6, (255, 0, 0), (0, 0, 255), 0.3, 3))
            if _ce_.replace(" ", "").count(t_display("papelera").replace(" ", "")) != 2 or (_code != "es" and "papelera" in _ce_):      # put_text no pinta los espacios (ar: «سلة المهملات»)
                _un_ok["trash"] = False
            for _k in _ph_keys:
                _v = t_display(_k)
                if dwidth(_v) != 5 or (_code != "es" and "¿" in _v):
                    _un_ok["ph"] = False
            for _W in (31, 46, 60):
                for _f in (scene_merge_cells, scene_clean_cells, scene_empty_cells):
                    _cc_ = _f(_W, 6, (255, 0, 0), (0, 0, 255), 0.4) if _f is scene_merge_cells else _f(_W, 6, (255, 0, 0), (0, 0, 255), 0.4, 5)
                    if not (_cc_ and max(x for (x, _y) in _cc_) < _W and min(x for (x, _y) in _cc_) >= 1):
                        _un_ok["bounds"] = False
            _sv = dict(SCENE)
            try:
                SCENE.update(on=True, last_error="Preparando")
                if _dlpy_error_line() != t_display("Preparando"):
                    _un_ok["err"] = False
            finally:
                SCENE.clear()
                SCENE.update(_sv)
            # los marcadores traducidos quedan centrados en el marco, como los de siempre
            for _lab in [t_display(_k) for _k in _ph_keys]:
                _fw = site_frame_width(16 / 9.0, 29)
                _cc = site_video_cells(10, 4, _fw, (255, 0, 0), (0, 0, 255), 3.0, 1.0, 1080, badge=(_lab, 1.0))
                _tx = sorted(x for (x, y), v in _cc.items() if y == 4 + BADGE_ROW and v[0] != " ")
                if not (_tx and _tx[0] + _tx[-1] == 2 * (10 + _fw // 2)):
                    _un_ok["ph"] = False
        globals()["LANG"] = "en"
        check("1.7.2: unión (VIDEO / AUDIO), papelera de limpieza y vaciado, marcadores «¿RES?»… y error de D L P Y salen del idioma activo en los 12 idiomas, caben y quedan centrados",
              _un_ok, {k: True for k in _un_ok})
        check("1.7.2: los marcadores del video salen del motor (en inglés RES ?, no ¿RES?) y el español sigue igual",
              ([ph_text(k) for k in _ph_keys[:3]], t_display("¿KHZ?", lang="ru"), t_display("¿RES?", lang="es")), (["RES ?", "CDC ?", "FPS ?"], "КГЦ ?", "¿RES?"))
        # 1.7.1: animación «ahead» (la local es mayor que el Release)
        globals()["LANG"] = "es"
        _txt_ = lambda cs: "".join(ch for (_xy, (ch, _c, _b)) in sorted(cs.items(), key=lambda kv: (kv[0][1], kv[0][0])))
        _ah0, _ah1, _ah2 = (scene_ahead_cells(60, 6, (255, 0, 0), (0, 0, 255), t_, "1.7.0", "1.7.9") for t_ in (0.1, 0.9, 1.6))
        check("1.7.1: «ahead»: el Release a la izquierda y la local a la derecha, chevrones › subiendo (3 filas) antes de llegar y ▲ en el centro al llegar; repetible y dentro de las filas y0+5 … y0+7",
              ("1.7.0" in _txt_(_ah1), "1.7.9" in _txt_(_ah1), "›" in _txt_(_ah0) and "▲" not in _txt_(_ah0), "▲" in _txt_(_ah2) and "›" not in _txt_(_ah2),
               {y for (_x, y) in _ah0} <= {11, 12, 13}, len({y for (_x, y) in _ah1 if _txt_({(_x, y): _ah1[(_x, y)]}) == "›"}) >= 2,
               scene_ahead_cells(60, 6, (255, 0, 0), (0, 0, 255), 0.4, "1.7.0", "1.7.9") == scene_ahead_cells(60, 6, (255, 0, 0), (0, 0, 255), 0.4 + WELCOME_CYCLE, "1.7.0", "1.7.9"),
               max(x for (x, _y) in scene_ahead_cells(31, 6, (255, 0, 0), (0, 0, 255), 1.6, "1.7.0", "1.7.9")) < 31, "ahead" in WELCOME_KINDS, "ahead" in MOTIF_NAMES),
              (True,) * 10)
        globals()["LANG"] = "en"
        check("1.7.1: «ahead»: el nombre del motivo sale del catálogo en los 12 idiomas y la escena le pone el texto de estado de la versión local",
              ([t_display(MOTIF_NAMES["ahead"], lang=c) != "Adelanto" for c in LANG_CODES if c != "es"] == [True] * 11, t_display("Adelanto", lang="en")), (True, "Ahead"))
        globals()["LANG"] = "fr"
        check("1.7.1: el resaltado de la tecla funciona con «Entrée» (fr) e «Invio» (it)",
              (sorted(ask_key_mask("Entrée convertir · r remux · n garder"))[:3], sorted(ask_key_mask("Invio converti · r remux · n mantieni"))[:3], ux_enter_key(), ux_enter_key("it"), ux_enter_key("zh")),
              ([0, 1, 2], [0, 1, 2], "Entrée", "Invio", "Enter"))
        globals()["LANG"] = "ja"
        check("1.7.1: los chips aceptan texto ancho (ja = 2 columnas) y _conv_geo los mide por columnas",
              (ux_chip("VIEJO"), ux_chip("NUEVO"), _conv_geo(60, ux_chip("VIEJO"), ux_chip("NUEVO"))[2:4], scene_chip_text("日本語日本語日本語")), ("既存", "新規", (8, 8), "日本語日"))
        globals()["LANG"] = "en"
        _cw = scene_wait_conv_cells(60, 6, (255, 0, 0), (0, 0, 255), 1.0, scene_chip_text("VIEJO"), scene_chip_text("NUEVO"), 15.0, swap=True)
        check("1.7.1: la pregunta de sustituir en inglés dibuja OLD → NEW y no deja VIEJO / NUEVO",
              ("OLD" in "".join(ch for (_xy, (ch, _c, _b)) in sorted(_cw.items(), key=lambda kv: (kv[0][1], kv[0][0]))), "VIEJO" in "".join(ch for (_xy, (ch, _c, _b)) in _cw.items())), (True, False))
        # scene_cells con LANG=en: el lab se muestra traducido, S["label"] sigue en español
        try:
            _S = scene_defaults()
            _S.update(geo=(46, 24, 6, 17), a=(255, 138, 61), b=(255, 61, 139), name="YouTube", mode="video", mode_orig="video", title_raw="Pan casero", label="Descargando audio 1/1", pct=10, shown=0.2, aspect=16 / 9.0, res=1080, vinfo={"codec": "avc1", "fps": 30})
            _st = scene_state()
            _hold = SITE_HOLD_AT * SITE_SECS
            _ta, _fr = _hold + 0.2, 0
            for _ in range(12):
                scene_cells(_S, _st, _ta, _ta, _fr)
                _ta, _fr = _ta + 0.05, _fr + 1
            _cells = scene_cells(_S, _st, _ta, _ta, _fr)
            _txt = "".join(c[0] for (x, y), c in sorted(_cells.items()) if y == 6 + SCENE_STATUS_ROW)
            check("idioma: scene_cells muestra el estado traducido (en)", "Downloading" in _txt, True)
            check("idioma: scene_cells no deja el estado en español (en)", "Descargando" in _txt, False)
            check("idioma: S[label] sigue canónico en español", _S["label"], "Descargando audio 1/1")
        except Exception as _e:
            check("idioma: scene_cells traducido (excepción)", f"{type(_e).__name__}: {_e}", "")
        # JSON del atajo en en
        try:
            _info = {"formats": [{"format_id": "1", "ext": "mp4", "vcodec": "avc1", "acodec": "mp4a", "height": 1080, "width": 1920, "fps": 30, "tbr": 5000, "filesize": 1000000, "language": "en", "format_note": "English (Original)"}, {"format_id": "2", "ext": "m4a", "vcodec": "none", "acodec": "mp4a", "height": None, "width": None, "fps": None, "tbr": 128, "filesize": 100000, "language": "en", "format_note": "English (Original)"}], "title": "Test", "id": "abc", "duration": 60}
            _pay = build_shortcut_payload(_info, "https://youtube.com/watch?v=abc", True, None, None, [])
            _labels = " ".join(str(x) for x in (_pay.get("video_labels") or []) + (_pay.get("track_labels") or []) + (_pay.get("audio_labels") or []))
            check("idioma: JSON atajo en en no tiene 'Solo audio'", "Solo audio" not in _labels, True)
            check("idioma: JSON atajo en en no tiene 'Ver todos'", "Ver todos" not in _labels and "Ver todos" not in str(_pay.get("more_label") or ""), True)
            check("idioma: JSON atajo en en no tiene 'con audio'", "con audio" not in _labels, True)
            check("idioma: JSON atajo en en sí tiene 'Audio only' o 'See all'", ("Audio only" in _labels) or ("See all" in str(_pay.get("more_label") or "")), True)
        except Exception as _e:
            check("idioma: JSON atajo traducido (excepción)", f"{type(_e).__name__}: {_e}", "")
        # 1.7.0 (corrección): límites de palabra, plantillas completas, unidades y números
        set_lang("en")
        check("idioma: estado completo «Esperando respuesta»", t_display("Esperando respuesta"), "Waiting for a response")
        check("idioma: «Con audio» con mayúscula se traduce", t_display("Con audio"), "With audio")
        check("idioma: el nombre del atajo forma parte de una plantilla completa", t_display("Enviando a DLpy"), "Sending to DLpy")
        check("idioma: etiqueta interna de audio en minúsculas", t_display("audio"), "audio")
        check("idioma: horas y días tras un número", [t_display("1 hora"), t_display("2 horas"), t_display("3 días")], ["1 hour", "2 hours", "3 days"])
        check("idioma: plantilla «Se usará la» completa", t_display("Se usará la 1.7.0 la próxima vez que abras DLpy."), "Version 1.7.0 will be used the next time you open DLpy.")
        check("idioma: plantilla «Actualización de» completa", t_display("Actualización de yt-dlp: 1 → 2"), "Update of yt-dlp: 1 → 2")
        check("idioma: plantilla «Recodificar» con equipo", t_display("Recodificar el video a HEVC puede tardar bastante en el equipo."), "Re-encoding the video to HEVC can take a long time on this device.")
        set_lang("ja")
        check("idioma: estados completos en ja", "la próxima" not in t_display("Se usará la 1.7.0 la próxima vez que abras DLpy.") and t_display("Esperando respuesta") == "応答を待っています", True)
        for _c in ("en", "pt", "fr", "de", "it", "ru", "zh", "hi", "ar", "ja", "ko"):
            set_lang(_c)
            _bad = [n for n, _rx in _FMT_RX if n not in I18N_FMT[_c]]
            check("idioma: plantillas completas en " + _c, _bad, [])
        set_lang("es")
        check("idioma: en español 2,1 → punto y «s»", [loc_num(2.1, 1), loc_num(1, 1), sec_unit()], ["2.1", "1.0", "s"])
        set_lang("en")                   # las comprobaciones siguientes esperan inglés
        # --idiomas: JSON para Atajos
        _lp = json.loads(json.dumps(languages_payload("en"), ensure_ascii=True, separators=(",", ":")))
        _rest = [c for c in LANG_CODES if c != "en"]
        check("idiomas: JSON con los otros 11 códigos en orden y sin el actual", [_lp["lang_codes"], _lp["lang_count"], _lp["lang_current"], [l["code"] for l in _lp["lang_list"]], "en" in _lp["lang_map"].values()], [_rest, 11, "en", _rest, False])
        _lj = languages_payload("ja")
        check("idiomas: con ja activo sale en y no ja; el prompt nombra el activo", ["en" in _lj["lang_codes"], "ja" in _lj["lang_codes"], len(_lj["lang_labels"]), _lj["lang_title"]], [True, False, 11, "現在の言語: 日本語"])
        check("idiomas: etiquetas = bandera + nombre (sin código ni punto), paralelas a codes, y by_label da el código",
              [all(lb == "%s %s" % (LANG_FLAGS[cd], LANG_NAMES[cd]) for lb, cd in zip(_lp["lang_labels"], _lp["lang_codes"])), len(_lp["lang_labels"]) == len(_lp["lang_codes"]),
               any(" · " in lb or lb.endswith(" " + cd) for lb, cd in zip(_lp["lang_labels"], _lp["lang_codes"])), [_lp["lang_map"][lb] for lb in _lp["lang_labels"]] == _lp["lang_codes"],
               len(set(_lp["lang_labels"])) == 11, all(LANG_FLAGS.get(c) for c in LANG_CODES)], [True, True, False, True, True, True])
        # 1.7.0 (corrección): la escena respeta el ancho real de cada carácter (ja / zh / ko = 2 columnas, combinantes = 0): la caja D L P Y,
        # el aviso y el pintado dejan cada fila en exactamente W-1 columnas y los cinco renglones del marco con el mismo ancho
        _Wt, _res = 61, {}
        for _c in ("en", "ja", "zh", "ko"):
            set_lang(_c)
            import io as _io
            _sb, _sst = _io.StringIO(), {"rows": {}}
            _cl = scene_dlpy_cells(_Wt, 1, (255, 200, 60), (255, 60, 120), 0.3, "1.7.0", "Analizando enlace", tt=2.0)
            _cl.update(scene_conv_notice({}, 1, _Wt // 2 + 1, _Wt, 1.0))
            scene_paint(_sb, _cl, _sst, _Wt, 24)
            _rw = {y: dwidth(_ANSI_RE.sub("", r)) for y, r in _sst["rows"].items()}
            _box = {dwidth(_ANSI_RE.sub("", r).rstrip()) for y, r in _sst["rows"].items() if _ANSI_RE.sub("", r).strip()[:1] in ("╭", "│", "╰")}
            _res[_c] = [set(_rw.values()) == {_Wt - 1}, len(_box) == 1]
        check("idioma: la escena D L P Y y el aviso no se desalinean en en / ja / zh / ko", _res, {c: [True, True] for c in ("en", "ja", "zh", "ko")})
        _tc = text_cells("解析中 a\u0301")
        check("idioma: text_cells (ancho 2, combinante pegado)", [(s_, dx, w) for _i, s_, dx, w in _tc], [("解", 0, 2), ("析", 2, 2), ("中", 4, 2), (" ", 6, 1), ("a\u0301", 7, 1)])
        _pc = {}
        check("idioma: put_text deja la continuación vacía y devuelve el ancho", [put_text(_pc, 5, 1, "あb", WHITE), _pc[(5, 1)][0], _pc[(6, 1)][0], _pc[(7, 1)][0]], [3, "あ", "", "b"])
        check("idioma: clip_text corta por columnas", [clip_text("解析中", 5), clip_text("abc", 2)], ["解析", "ab"])
        check("idiomas: «Idioma establecido» en los 12 idiomas (lang_set_map, lang_set, lang_set_texts, set_text)",
              [sorted(_lp["lang_set_map"]) == sorted(LANG_CODES), all(_lp["lang_set_map"].values()), _lp["lang_set"], _lp["lang_set_map"]["ja"],
               _lp["lang_set_texts"] == [_lp["lang_set_map"][c] for c in _lp["lang_codes"]], [l["set_text"] for l in _lp["lang_list"]] == _lp["lang_set_texts"]],
              [True, True, "Language set", "言語を設定しました", True, True])
        set_lang("en")                   # las comprobaciones siguientes esperan inglés
        check("idiomas: prompt en el idioma actual y comando de guardado", [_lp["lang_title"], _lp["lang_command"]], ["Current language: English", "--config DLPY_LANG=<code>"])
        check("idiomas: cada idioma tiene nombre nativo e inglés", all(l["name"] and l["english"] for l in _lp["lang_list"]), True)
        check("idiomas: wants_languages acepta --idiomas, --langs y rayas largas", [wants_languages(["--idiomas"]), wants_languages(["--langs"]), wants_languages(["\u2014idiomas"]), wants_languages(["idiomas"]), wants_languages(["--sistema"])], [True, True, True, False, False])
        _sv_env = {k: os.environ.pop(k, None) for k in ("DLPY_LANG", "LANG", "LANGUAGE")}
        try:
            _d0 = _lang_detect()
            # 1.7.1: «auto» = el idioma del sistema; sin DLPY_LANG (o «ask») se pregunta y el LANG no cuenta
            os.environ["DLPY_LANG"] = "auto"
            os.environ["LANG"] = "C.UTF-8"
            _d1 = _lang_detect()
            os.environ["LANG"] = "es_ES.UTF-8"
            _d2 = _lang_detect()
            os.environ["DLPY_LANG"] = "ja"
            _d3 = _lang_detect()
            os.environ["DLPY_LANG"] = "ask"
            _d4 = _lang_detect()
        finally:
            for _k in ("DLPY_LANG", "LANG", "LANGUAGE"):
                os.environ.pop(_k, None)
            os.environ.update({k: v for k, v in _sv_env.items() if v is not None})
        check("idiomas: predeterminado en (sin config ni LANG válido), LANG del sistema y DLPY_LANG mandan", [DEFAULT_LANG, _d0, _d1, _d2, _d3, _d4, set_lang("xx")], ["en", "en", "en", "es", "ja", "en", "en"])
        check("idiomas 1.7.1: CONFIG_OPTIONS trae ask como valor por omisión de DLPY_LANG", [d for k, d, _x in CONFIG_OPTIONS if k == "DLPY_LANG"], ["ask"])
        check("idiomas: el JSON es ASCII", _lp is not None and json.dumps(languages_payload("es"), ensure_ascii=True).isascii(), True)
        check("idioma: CONFIG_OPTIONS incluye DLPY_LANG", any(k == "DLPY_LANG" for k, _d, _x in CONFIG_OPTIONS), True)
        check("idioma: shortcut_error traducido", shortcut_error("no_link", "No hay enlace: usa --scb LINK o --scm LINK.")["error"], "No link: use --scb LINK or --scm LINK.")
        # 1.7.1: la escena que pregunta el idioma (DLPY_LANG=ask, el predeterminado)
        check("idioma ask 1.7.1: pendiente con DLPY_LANG vacío / ask / preguntar; no con auto ni con un código",
              [lang_ask_pending({}), lang_ask_pending({"DLPY_LANG": "ask"}), lang_ask_pending({"DLPY_LANG": " ASK "}), lang_ask_pending({"DLPY_LANG": "preguntar"}),
               lang_ask_pending({"DLPY_LANG": "auto"}), lang_ask_pending({"DLPY_LANG": "en"}), lang_ask_pending({"DLPY_LANG": "xx"})],
              [True, True, True, True, False, False, False])
        check("idioma ask 1.7.1: «Seleccione idioma» en los 12 idiomas, distinto en cada uno, y la clave se traduce",
              (sorted(LANG_SELECT_TEXT) == sorted(LANG_CODES), len(set(LANG_SELECT_TEXT.values())), LANG_SELECT_TEXT["es"], t_display("Seleccione idioma", lang="en"), t_display("Seleccione idioma", lang="ja")),
              (True, 12, "Seleccione idioma", "Select language", "言語を選択"))
        _st = lambda txt, sel=1, ok=True: lang_pick_step(sel, 12, txt, ok)
        check("idioma ask 1.7.1: teclas (n / espacio / flecha → siguiente · p / flecha ← anterior · 1-9 y 0 saltan · Enter acepta, no el fantasma)",
              [_st("n"), _st(" "), _st("\x1b[C"), _st("p"), _st("\x1b[D"), _st("p", 0), _st("n", 11), _st("5"), _st("0"), _st("9", 1), _st("\r"), _st("\r", 1, False), _st("nn\r"), _st("x")],
              [(2, False, True), (2, False, True), (2, False, True), (0, False, True), (0, False, True), (11, False, True), (0, False, True), (4, False, True), (9, False, True),
               (8, False, True), (1, True, False), (1, False, False), (3, True, True), (1, False, False)])
        _ar = {"kind": "lang", "codes": list(LANG_CODES), "sel": 0, "secs": 60, "t0": time.time(), "ta0": 0.0, "tk": 0.0}
        _lw, _lok, _lt = 0, True, set()
        for _i, _c in enumerate(LANG_CODES):
            _ar["sel"] = _i
            _cl = scene_ask_cells({}, _ar, (LANG_TITLE_HOLD + LANG_TITLE_MORPH) * _i + 0.8, 6, 31, 60, lambda k: (120, 160, 255))
            _rows = {y: "".join(_cl[(x, y)][0] if (x, y) in _cl else " " for x in range(1, 61)).strip() for y in {k[1] for k in _cl}}
            _r0 = 6 + SCENE_STATUS_ROW - 1
            _lw = max([_lw] + [dwidth(v) for v in _rows.values()])
            _lt.add(_rows.get(_r0 + 1))
            if sorted(_rows) != [_r0, _r0 + 1, _r0 + 2] or LANG_NAMES[_c] not in _rows[_r0 + 2].replace(" ", "") or _rows[_r0].count("●") != 1 or _rows[_r0 + 1].replace(" ", "") != LANG_SELECT_TEXT[_c].replace(" ", ""):      # (la columna de continuación del carácter ancho es un hueco que scene_paint cubre)
                _lok = False
        check("idioma ask 1.7.1: la escena pinta tres filas (puntos · «Seleccione idioma» en cada idioma · nombre del elegido con n/p), caben en la pantalla y cada idioma sale a su tiempo",
              (_lok, _lw <= 59, len(_lt)), (True, True, 12))
        check("idioma ask 1.7.1: scene_lang_pick sin escena no pregunta ni cambia nada", (scene_lang_pick(), lang_pick_start() in LANG_CODES), (None, True))
        # 1.7.1: welcome en todos los idiomas y 2 s en escena
        _wr, _wb = (60, 160, 255), (255, 200, 60)
        _ok_lbl, _ok_txt, _ok_card, _ok_w = True, True, True, True
        for _code in ("en", "pt", "fr", "de", "it", "ru", "zh", "hi", "ar", "ja", "ko"):
            set_lang(_code)
            _cs = scene_first_cells(60, 6, _wr, _wb, WELCOME_CYCLE * 0.9)
            _row = lambda y: "".join(_cs[(x, y)][0] if (x, y) in _cs else " " for x in range(1, 70)).strip()
            _want = [t_display(n, lang=_code) for n in WELCOME_ITEMS]
            if not all(_row(11 + i).replace("", "").startswith(_want[i]) for i in range(3)) or (_code != "pt" and any(w in WELCOME_ITEMS for w in _want[:2])):      # pt: «estado» se escribe igual
                _ok_lbl = False
            _lim = max(dwidth(_row(y)) for y in (11, 12, 13))
            if _lim > 58:
                _ok_w = False
            for _t in ("Primera ejecución · DLpy 1.7.1", "Actualizado · 1.7.0 → 1.7.1", "Versión anterior · 1.7.1 → 1.7.0", "Misma versión · 1.7.1", "Cambió el hash · edición detectada"):
                if t_display(_t, lang=_code) == _t:
                    _ok_txt = False
            for _t in ("Actualizada 1.7.0 → 1.7.1", "Bajada de versión 1.7.1 → 1.7.0", "carpeta interna reiniciada", "Edición detectada · 1.7.1") + tuple(DOWNGRADE_WHY.values()):
                _localized = t_status(_t, lang=_code) if _t.startswith(("Actualizada", "Bajada de versión", "Edición detectada")) else t_display(_t, lang=_code)
                if _localized == _t:
                    _ok_card = False
        check("welcome 1.7.1: rótulos de la primera ejecución traducidos en los 11 idiomas (sin «carpetas» / «estado») y dentro del ancho", (_ok_lbl, _ok_w), (True, True))
        check("welcome 1.7.1: texto de estado y tarjetas de versión traducidos en los 11 idiomas", (_ok_txt, _ok_card), (True, True))
        set_lang("en")
        check("welcome 1.7.1: update_card_rows sin español con DLPY_LANG=en",
              [any(w in "".join(update_card_rows("1.7.0", "1.7.1", d_, f_, 60)) for w in ("Actualizada", "Bajada", "carpeta", "reiniciada")) for d_, f_ in ((None, 0), ({"causa": "manual"}, 0), ({"causa": "externa"}, None))],
              [False, False, False])
        check("welcome 1.7.1: la escena de bienvenida dura 2 s (un ciclo) y el hold deja el retraso del dibujo",
              (WELCOME_CYCLE, round(WELCOME_CYCLE - SCENE_WELCOME_SECS, 6)), (2.0, 0.05))
    finally:
        set_lang(_saved_lang)


def _st_t32_arreglos(check):
    """[T32] ── 1.7.5: revisión de errores (tamaños y bitrates, caché con prefijos, progreso negativo, reemplazo de archivo, ESC) ──"""
    import tempfile
    import io
    import contextlib
    import types
    _saved_lang = LANG
    set_lang("en")                                 # punto decimal
    try:
        check("1.7.5 human_size: junto al escalón pasa al siguiente (no «1024 KB»)",
              [human_size(n) for n in (1023, 1048166, 1073322394, 1099500890358, 10 * 1024)],
              ["1023 B", "1.0 MB", "1.0 GB", "1.0 TB", "10 KB"])
        check("1.7.5 precise_size: junto al escalón pasa al siguiente (no «1024.0KB»)",
              [precise_size(n) for n in (1023, 1024, 1048000, 1048575, 1073741823)],
              ["1023B", "1.0KB", "1023.4KB", "1.0MB", "1.00GB"])
        check("1.7.5 fmt_kbps: 999.6 kbps ya es «1.0 Mbps»",
              [fmt_kbps(k) for k in (999.4, 999.6, 1000, 12345)], ["999 kbps", "1.0 Mbps", "1.0 Mbps", "12.3 Mbps"])
        check("1.7.5 abr_label: ya no topa en 9.9Mb",
              [abr_label(k) for k in (320, 1411, 9949, 9950, 12000)], ["320kb", "1.4Mb", "9.9Mb", "010Mb", "012Mb"])
    finally:
        set_lang(_saved_lang)

    def _leak(texto):                              # lo que queda tecleado tras saltar las secuencias de escape
        esc, out = False, []
        for ch in texto:
            if esc:
                esc = _esc_next(esc, ch)
            elif ch == "\x1b":
                esc = True
            else:
                out.append(ch)
        return "".join(out)
    check("1.7.5 _esc_next: ESC [ A, ESC O A y ESC [ 1;5 C no dejan letras sueltas",
          (_leak("a\x1b[Ab"), _leak("a\x1bOAb"), _leak("\x1b[1;5Cx")), ("ab", "ab", "x"))

    with tempfile.TemporaryDirectory() as _td:
        _g = globals()
        _sv_cache = _g["STREAM_CACHE_DIR"]
        _g["STREAM_CACHE_DIR"] = os.path.join(_td, "cache")
        try:
            _d1, _b1 = stream_cache_paths("vid", "137.1")
            os.makedirs(_d1, exist_ok=True)
            write_text(_b1 + ".mp4", "x")
            _solo = (get_cached_stream("vid", "137", "mp4"), get_cached_stream("vid", "137"))
            _d0, _b0 = stream_cache_paths("vid", "137")
            write_text(_b0 + ".mp4", "y")
            _propio = (get_cached_stream("vid", "137", "mp4") == _b0 + ".mp4", get_cached_stream("vid", "137.1", "mp4") == _b1 + ".mp4")
        finally:
            _g["STREAM_CACHE_DIR"] = _sv_cache
        check("1.7.5 get_cached_stream: «137» no recibe el stream de «137.1»", _solo, (None, None))
        check("1.7.5 get_cached_stream: cada formato recibe el suyo", _propio, (True, True))

        _pf = os.path.join(_td, "p.txt")
        write_text(_pf, "out_time_us=-21333\nout_time_ms=-21333\nspeed=1.5x\nprogress=continue\n")
        _neg = _read_progress(_pf)
        write_text(_pf, "out_time_us=2500000\nspeed=N/A\nprogress=end\n")
        check("1.7.5 _read_progress: el tiempo negativo se limita a 0; speed=N/A → None", (_neg, _read_progress(_pf)), ((0.0, 1.5), (2.5, None)))

        _fd, _wd = os.path.join(_td, "files"), os.path.join(_td, "work")
        _sv_fd, _sv_dd, _sv_mv = _g["FILES_DIR"], _g["DELIVERY_DIR"], _g["move_file"]
        _g["FILES_DIR"], _g["DELIVERY_DIR"] = _fd, os.path.join(_td, "delivery")

        def _store(nuevo, boom=False):
            os.makedirs(_wd, exist_ok=True)
            write_text(os.path.join(_wd, "v.mp4"), nuevo)
            _run = types.SimpleNamespace(final=os.path.join(_wd, "v.mp4"), work_dir=_wd, old_file=None)
            if boom:
                def _fallo(src, dst):
                    write_text(dst, "parcial")
                    raise OSError("disco lleno")
                _g["move_file"] = _fallo
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    rc = _m_store(_run)
            finally:
                _g["move_file"] = _sv_mv
            return rc, _run
        try:
            os.makedirs(_fd, exist_ok=True)
            _dest = os.path.join(_fd, "v.mp4")
            write_text(_dest, "viejo")
            _rc_mal, _ = _store("nuevo", boom=True)
            _tras_fallo = (_rc_mal, read_text(_dest), os.path.exists(_dest + ".tmp"))
            _rc_ok, _run_ok = _store("nuevo")
            _tras_ok = (_rc_ok, read_text(_dest), os.path.exists(_dest + ".tmp"), _run_ok.final == _dest)
        finally:
            _g["FILES_DIR"], _g["DELIVERY_DIR"], _g["move_file"] = _sv_fd, _sv_dd, _sv_mv
        check("1.7.5 _m_store: si falla el movimiento el archivo anterior queda intacto y sin .tmp", _tras_fallo, (1, "viejo", False))
        check("1.7.5 _m_store: si funciona el nuevo reemplaza al anterior sin dejar .tmp", _tras_ok, (None, "nuevo", False, True))


def _st_t33_pulido(check):
    """[T33] ── 1.7.5: pulido de UX y animaciones del carril (transiciones de color de las tarjetas, fundidos con curva) ──"""
    lum = lambda col: col[0] + col[1] + col[2]
    ty = 5
    base = {(3, ty): ("V", SCENE_WHITE, None), (3, ty + 1): ("─", mix(BLACK, SAVED_TONE, 0.8), None), (3, ty + 5): ("✓", SAVED_TONE, None), (4, ty + 1): (" ", SCENE_GRAY, None)}
    idle = {"state": "espera", "act_t": None, "done_t": None}
    check("tarjeta: en espera no hay transición (misma tabla)", rail_tone_shift(base, idle, 10.0, ty) is base, True)
    done = {"state": "hecho", "done_t": 10.0}
    d0, d1 = rail_tone_shift(base, done, 10.0, ty), rail_tone_shift(base, done, 10.0 + RAIL_TONE_T + 0.01, ty)
    check("tarjeta: al terminar destella (más clara que el verde de «hecho»)", lum(d0[(3, ty + 5)][1]) > lum(SAVED_TONE), True)
    check("tarjeta: al terminar el título parte del blanco de «activa»", d0[(3, ty)][1], SCENE_WHITE)
    check("tarjeta: terminada la transición queda el color de «hecho» (misma tabla)", d1 is base, True)
    mid = rail_tone_shift(base, done, 10.0 + RAIL_TONE_T * 0.5, ty)
    check("tarjeta: el destello baja de forma continua", lum(d0[(3, ty + 5)][1]) >= lum(mid[(3, ty + 5)][1]) >= lum(SAVED_TONE), True)
    on = {"state": "activa", "act_t": 10.0, "done_t": None}
    a0, a1 = rail_tone_shift(base, on, 10.0, ty), rail_tone_shift(base, on, 10.0 + RAIL_TONE_T + 0.01, ty)
    check("tarjeta: al encenderse parte apagada y llega a su color", (lum(a0[(3, ty + 1)][1]) < lum(base[(3, ty + 1)][1]), a1 is base), (True, True))
    check("tarjeta: la transición no toca los espacios ni cambia las posiciones", (a0[(4, ty + 1)], sorted(a0) == sorted(base)), ((" ", SCENE_GRAY, None), True))
    check("tarjeta activa sin act_t (nació activa): sin transición", rail_tone_shift(base, {"state": "activa", "act_t": None}, 10.0, ty) is base, True)
    S = {"label": "Descargando video 1/2", "stream_total": 2, "stream_seen": 1, "past_dl": True, "skind": {1: "video", 2: "audio"}, "spct": {}, "slang": {}}
    st = {}
    R = rail_step(S, st, 60, 1.0, 0.0)
    ids = {c_["id"]: c_ for c_ in R["cards"]}
    check("carril: la pista que aún espera no lleva act_t", (ids["audio"]["state"], ids["audio"].get("act_t")), ("espera", None))
    S2 = dict(S, label="Descargando audio 2/2", stream_seen=2, spct={1: 100.0})
    R = rail_step(S2, st, 60, 2.0, 0.0)
    ids = {c_["id"]: c_ for c_ in R["cards"]}
    check("carril: al empezar la pista guarda el instante en que se enciende", (ids["audio"]["state"], ids["audio"].get("act_t")), ("activa", 2.0))
    cw_ = rail_width(60)
    c_ = {"id": "v", "kind": "video", "pct": 10.0, "state": "activa", "lang": None, "idx": 1, "of": 1, "title": None, "x": 6.0, "tx": 6.0, "fade": 0.5,
          "exit": None, "exit_t": None, "done_t": None, "born": 0.0}
    _rail_title_sync(c_, {"lang": None, "idx": 1, "of": 1}, cw_, 0.0)
    half = rail_card_cells(c_, 1, (255, 70, 70), (255, 154, 164), 5.0, cw_)
    full = rail_card_cells(dict(c_, fade=1.0), 1, (255, 70, 70), (255, 154, 164), 5.0, cw_)
    k_ = next(iter(half))
    check("carril: una tarjeta que entra a medio fundido se ve más apagada que la completa", lum(half[k_][1]) <= lum(full[k_][1]), True)


def _st_t34_movimiento(check):
    """[T34] ── 1.7.6: un solo lenguaje de movimiento (curva única, regla con borde suave y destello, cometa del video, ecualizadores continuos, duraciones) ──"""
    lum = lambda col: col[0] + col[1] + col[2]
    xs = [i / 20.0 for i in range(21)]
    check("movimiento 1.7.6: smooth() es FLOW_EASE (una sola curva), con extremos fijos y fuera de rango acotado",
          (smooth(0.0), smooth(1.0), smooth(-3.0), smooth(4.0), smooth(0.37) == FLOW_EASE(0.37)), (0.0, 1.0, 0.0, 1.0, True))
    check("movimiento 1.7.6: la curva única no baja nunca", all(smooth(b_) >= smooth(a_) for a_, b_ in zip(xs, xs[1:])), True)
    check("movimiento 1.7.6: las duraciones van de lo breve a lo grande y el encendido de una tarjeta es la normal",
          (MOTION_QUICK < MOTION_BASE < MOTION_SLOW, RAIL_TONE_T == MOTION_BASE, MOTIF_FPS), (True, True, ANIM_FPS))
    sums = [sum(bar_cover(i_, s_) for i_ in range(RULE_CELLS)) for s_ in (0.0, 0.25, 0.5, 1.0)]
    check("regla 1.7.6: lo cubierto es exactamente el avance (vacía, un cuarto, mitad, llena)",
          [round(v_, 6) for v_ in sums], [0.0, round(0.25 * RULE_CELLS, 6), round(0.5 * RULE_CELLS, 6), float(RULE_CELLS)])
    check("regla 1.7.6: la celda del frente queda a medias, las de atrás enteras y las de delante apagadas",
          (bar_cover(13, 0.5), round(bar_cover(14, 0.5), 6), bar_cover(15, 0.5)), (1.0, 0.5, 0.0))
    cov = [bar_cover(i_, 0.37) for i_ in range(RULE_CELLS)]
    check("regla 1.7.6: la cobertura no sube a lo largo de la regla", all(b_ <= a_ for a_, b_ in zip(cov, cov[1:])), True)
    fr = [bar_front(i_, 0.5) for i_ in range(RULE_CELLS)]
    check("regla 1.7.6: el destello está en el frente, se apaga lejos y no existe sin avance ni con la barra llena",
          (fr.index(max(fr)), fr[0], fr[-1], bar_front(3, 0.0), bar_front(3, 1.0), all(0.0 <= v_ <= 1.0 for v_ in fr)), (14, 0.0, 0.0, 0.0, 0.0, True))
    n_ = 24
    glow = [comet_glow(5.0, (5 - j_) % n_, n_) for j_ in range(int(COMET_TAIL) + 2)]
    check("cometa 1.7.6: la cabeza vale 1, la cola baja sin subir y se apaga a las COMET_TAIL celdas",
          (glow[0], all(b_ <= a_ for a_, b_ in zip(glow, glow[1:])), glow[int(COMET_TAIL)], glow[-1]), (1.0, True, 0.0, 0.0))
    check("cometa 1.7.6: la celda a punto de recibirlo se enciende antes (sin salto) y la que está más lejos sigue apagada",
          (comet_glow(5.0, 6, n_), comet_glow(5.5, 6, n_), comet_glow(5.999, 6, n_) > 0.99, comet_glow(6.0, 6, n_), comet_glow(4.0, 6, n_)), (0.0, 0.5, True, 1.0, 0.0))
    ra, rb = (255, 140, 0), (220, 40, 180)
    card = {"id": "t1", "kind": "video", "pct": 25.0, "state": "activa", "x": 20.0, "tx": 20.0, "fade": 1.0, "exit": None, "exit_t": None, "done_t": None, "born": 0.0}
    perim = lambda cells_: [v_[1] for (x_, y_), v_ in cells_.items() if v_[0] in "╭╮╰╯─│"]
    on, off = perim(rail_card_cells(card, 6, ra, rb, 5.7, 10)), perim(rail_card_cells(dict(card, state="espera"), 6, ra, rb, 5.7, 10))
    check("cometa 1.7.6: el marco activo es más claro que el de espera incluso en su celda más apagada, y hay una cabeza brillante",
          (min(lum(c_) for c_ in on) > max(lum(c_) for c_ in off), max(lum(c_) for c_ in on) > min(lum(c_) for c_ in on) + 150), (True, True))
    frames = {tuple(sorted(rail_card_cells(dict(card, kind="audio"), 6, ra, rb, 5.0 + j_ / 24.0, 10).items())) for j_ in range(8)}
    check("ecualizador 1.7.6: a 24 cuadros por segundo cada cuadro es distinto (antes se repetía uno de cada dos)", len(frames) >= 7, True)
    S = {"geo": (60, 24, 6, 17), "a": ra, "b": rb, "name": "YouTube", "mode": "video", "title_raw": "Pan casero",
         "brand": False, "busy": False, "label": "Descargando video", "pct": 45, "shown": 0.5, "k_out": None}
    t = SITE_HOLD_AT * SITE_SECS
    st = scene_state()
    scene_cells(S, st, t, t + 0.01, 1)
    c = scene_cells(S, st, t, t + 2.0, 50)
    cx = 60 // 2 + 1
    back, ahead = c[(cx - 14 + 3, 6)][1], c[(cx - 14 + 25, 6)][1]
    check("regla 1.7.6: lo cubierto lleva el color pleno del degradado y lo que falta, el apagado de siempre",
          (back == mix6(ra, rb, 3 / 28.0), ahead == mix(mix6(ra, rb, 25 / 28.0), BLACK, 0.62)), (True, True))
    fronts = []
    for s_ in (15.2 / RULE_CELLS, 15.6 / RULE_CELLS, 16.0 / RULE_CELLS):
        c_ = scene_cells(dict(S, shown=s_), scene_state(), t, t + 2.0, 50)
        fronts.append(lum(c_[(cx - 14 + 15, 6)][1]))
    check("regla 1.7.6: el avance entre dos celdas cambia el tono de la del frente poco a poco (no salta de golpe)",
          (len(set(fronts)) == 3, abs(fronts[1] - fronts[0]) < 200, abs(fronts[2] - fronts[1]) < 200), (True, True, True))


def _st_t35_sondeo(check):
    """[T35] ── 1.7.7: ffmpeg solo sondea un stream con URL http(s) y algún dato útil (a-Shell mini se cerraba al sondear una URL opaca, p. ej. «full» de ok.ru) ──"""
    import subprocess
    import types
    u_ = "https://vd1.okcdn.ru/?expires=1&id=2"
    cases = (
        ({"url": u_, "format_id": "full", "ext": "mp4", "protocol": "https", "vcodec": "unknown", "acodec": "unknown"}, False),   # el «full» del log: sin dato alguno
        ({"url": u_, "vcodec": "none", "acodec": None, "height": None, "tbr": 0}, False),
        # no numérico o cero no cuenta
        ({"url": u_, "vcodec": "?", "height": "no", "fps": 0}, False),
        # el hls-2213 del log
        ({"url": "https://x/a.m3u8", "vcodec": "avc1", "height": 800, "fps": 24, "tbr": 2214}, True),
        ({"url": u_, "height": 720}, True), ({"url": u_, "width": 1280}, True), ({"url": u_, "tbr": 900}, True), ({"url": u_, "vbr": 500.5}, True),
        ({"url": u_, "vcodec": "avc1.64001f"}, True), ({"url": u_, "acodec": "mp4a.40.2"}, True),
        # sin URL
        ({"height": 720, "vcodec": "avc1", "tbr": 900}, False),
        ({"url": "file:///a.mp4", "height": 720}, False), ({"url": "rtmp://h/v", "height": 720}, False), ({"url": "", "height": 720}, False),
        ({"url": "HTTP://x/v.mp4", "height": 720}, True), (None, False), ({}, False),
        ({"url": u_, "asr": 44100}, False), ({"url": u_, "asr": 44100, "abr": 128}, True), ({"url": u_, "abr": 0, "asr": 48000}, False))   # 1.7.8: la frecuencia de audio sola no cuenta
    check("sondeo 1.7.7: solo con URL http(s) y algún dato útil (alto, ancho, fps, códec real o bitrate; 1.7.8: `asr` solo no cuenta)",
          [stream_can_probe(f) for f, _w in cases], [w for _f, w in cases])
    calls, old_run = [], subprocess.run
    fake = types.SimpleNamespace(stdout="", returncode=1, stderr="  Stream #0:0: Video: hevc (Main 10), yuv420p10le(tv, bt709), 1280x720, 25 fps, 25 tbr")
    try:
        subprocess.run = lambda cmd, *a, **k: (calls.append(list(cmd)) or fake)
        opaque = {"url": u_, "format_id": "full", "vcodec": "unknown", "acodec": "unknown"}
        none_bits = (probe_stream_bits("/x/ffmpeg", opaque), probe_stream_facts("/x/ffmpeg", opaque), probe_stream_bits("/x/ffmpeg", None))
        n_opaque = len(calls)
        useful = {"url": u_, "height": 800, "vcodec": "avc1", "tbr": 2214, "http_headers": {"User-Agent": "u"}}
        got_bits, got_facts = probe_stream_bits("/x/ffmpeg", useful), probe_stream_facts("/x/ffmpeg", useful)
        no_exe = probe_stream_bits("", useful)
    finally:
        subprocess.run = old_run
    check("sondeo 1.7.7: una URL opaca no lanza ffmpeg (ni para los bits ni para los datos reales de la escena)", (none_bits, n_opaque), ((None, None, None), 0))
    check("sondeo 1.7.7: con datos sí se sondea (los dos, con -probesize y -analyzeduration de 3 MB / 3 s) y se leen los bits y los datos",
          (got_bits, (got_facts or {}).get("v", {}).get("codec"), len(calls) - n_opaque, no_exe,
           all("-probesize" in c and "3000000" in c and "-analyzeduration" in c and c[-1] == u_ for c in calls[n_opaque:])),
          (10, "hevc", 2, None, True))
    # 1.7.8: el debug dice cuándo se omite el sondeo (y calla cuando sí se sondea)
    notes, old_dbg, old_run = [], globals()["dbg"], subprocess.run
    try:
        globals()["dbg"] = lambda label, data=None: notes.append((str(label), data))
        subprocess.run = lambda cmd, *a, **k: fake
        probe_stream_bits("/x/ffmpeg", opaque)
        probe_stream_facts("/x/ffmpeg", opaque)
        skipped = list(notes)
        del notes[:]
        probe_stream_bits("/x/ffmpeg", useful)
        probe_stream_facts("/x/ffmpeg", useful)
        probe_stream_bits("", opaque)
        silent = list(notes)
    finally:
        globals()["dbg"], subprocess.run = old_dbg, old_run
    check("sondeo 1.7.8: el debug anota «omitido» al no sondear (bits y datos reales, con format_id) y no anota nada al sondear o sin ffmpeg",
          ([l.split(":")[0] for l, _d in skipped], all("omitido" in l for l, _d in skipped), [(d or {}).get("format_id") for _l, d in skipped], silent),
          (["sondeo de bits", "sondeo de datos reales"], True, ["full", "full"], []))


def _st_t36_primero(check):
    """[T36] ── 1.8.0: --shortcutpick y --scb buscan las actualizaciones PRIMERO con la escena D L P Y viva; si hay un DLpy nuevo, la escena cede y corre ya la versión nueva ──"""
    import io
    import runpy
    g = globals()
    keep = (SCENE["on"], NO_UPDATES["on"])
    try:
        SCENE["on"], NO_UPDATES["on"] = False, False
        no_scene = updates_first()
        SCENE["on"] = True
        with_scene = updates_first()
        NO_UPDATES["on"] = True
        no_updates = updates_first()
    finally:
        SCENE["on"], NO_UPDATES["on"] = keep
    check("1.8.0: updates_first: solo con la escena viva y sin --noupdates", (no_scene, with_scene, no_updates), (False, True, False))

    seen, keep = [], (SCENE["on"], NO_UPDATES["on"], dict(LATE_UPDATES), g["update_phase"])
    try:
        g["update_phase"] = lambda: (seen.append(LATE_UPDATES["on"]) or None)
        NO_UPDATES["on"] = False
        SCENE["on"] = True
        LATE_UPDATES.update(on=True, done=False)
        rc_scene = _m_update(None)
        SCENE["on"] = False
        LATE_UPDATES.update(on=True, done=False)
        rc_plain = _m_update(None)
    finally:
        SCENE["on"], NO_UPDATES["on"] = keep[0], keep[1]
        LATE_UPDATES.clear()
        LATE_UPDATES.update(keep[2])
        g["update_phase"] = keep[3]
    check("1.8.0: --shortcutpick con escena viva apaga LATE_UPDATES (busca primero); sin escena sigue al final como antes",
          (seen, rc_scene, rc_plain), ([False, True], None, None))

    out, err = io.StringIO(), io.StringIO()
    calls = []
    saved = (sys.stdout, sys.stderr, SCENE["on"], g["scene_outro"], g["scene_stop"], g["scene_busy"], time.sleep)
    try:
        sys.stdout, sys.stderr = _SceneMute(out), _SceneErrMute(err)
        SCENE["on"] = True
        g["scene_outro"] = lambda: calls.append("outro") or True
        g["scene_stop"] = lambda **k: calls.append(("stop", k)) or True
        g["scene_busy"] = lambda on=True: calls.append(("busy", on))
        time.sleep = lambda s: None
        closed = scene_handoff()
        back = (sys.stdout is out, sys.stderr is err)
        SCENE["on"] = False
        calls_off = len(calls)
        closed_off = scene_handoff()
        calls_after_off = len(calls)
    finally:
        sys.stdout, sys.stderr, SCENE["on"], g["scene_outro"], g["scene_stop"], g["scene_busy"], time.sleep = saved
    check("1.8.0: scene_handoff: la escena se cierra (ocupado fuera, cierre hacia el centro, stop sin tocar el cursor) y stdout/stderr vuelven a lo real; sin escena no hace nada",
          (closed, back, calls, CURSOR_SHOW in out.getvalue(), closed_off, calls_after_off == calls_off),
          (True, (True, True), [("busy", False), "outro", ("stop", {"cursor": False})], True, False, True))

    order = []
    had = hasattr(sys, "_dlpy_reexec")
    saved = (runpy.run_path, g["scene_handoff"])
    try:
        runpy.run_path = lambda p, run_name=None: order.append(("run", p, run_name))
        g["scene_handoff"] = lambda: order.append("handoff")
        reexec_script()
    finally:
        runpy.run_path, g["scene_handoff"] = saved
        if not had and hasattr(sys, "_dlpy_reexec"):
            del sys._dlpy_reexec
    check("1.8.0: reexec_script cierra la escena (scene_handoff) ANTES de correr la versión nueva", order, ["handoff", ("run", SCRIPT_PATH, "__main__")])

    order = []
    saved = {k: g[k] for k in ("ux_start", "wait_terminal_ready", "ux_lang_pick", "scb_first_updates", "ux_note", "scb_diag")}
    try:
        g["ux_start"] = lambda run: order.append("start") or True
        g["wait_terminal_ready"] = lambda **k: None
        g["ux_lang_pick"] = lambda: order.append("lang")
        g["scb_first_updates"] = lambda: order.append("updates")
        g["ux_note"] = lambda text, hold=0.0: order.append(text) or True
        g["scb_diag"] = lambda **k: None
        started = scb_scene_start("https://x.y/z")
    finally:
        g.update(saved)
    check("1.8.0: --scb: la escena abre, se elige el idioma, D L P Y busca actualizaciones y SOLO DESPUÉS salen los avisos del análisis",
          (started, order), (True, ["start", "lang", "updates", SCB_NOTES[0], SCB_NOTES[1]]))

    calls = []
    keep = (SCENE["on"], NO_UPDATES["on"], g["ensure_dirs"], g["update_phase"])
    try:
        g["ensure_dirs"] = lambda: calls.append("dirs")
        g["update_phase"] = lambda: calls.append("phase") or None
        SCENE["on"], NO_UPDATES["on"] = False, False
        r_off = (scb_first_updates(), list(calls))
        SCENE["on"] = True
        r_on = (scb_first_updates(), list(calls))
        del calls[:]
        NO_UPDATES["on"] = True
        r_no = (scb_first_updates(), list(calls))
        NO_UPDATES["on"] = False

        def boom():
            raise OSError("sin red")

        def stop():
            raise KeyboardInterrupt

        g["update_phase"] = boom
        r_err = scb_first_updates()
        g["update_phase"] = stop
        r_int = scb_first_updates()
    finally:
        SCENE["on"], NO_UPDATES["on"], g["ensure_dirs"], g["update_phase"] = keep
    check("1.8.0: scb_first_updates: sin escena o con --noupdates no hace nada; con escena crea carpetas y corre update_phase; un fallo o Ctrl-C no rompe --scb",
          (r_off, r_on, r_no, r_err, r_int), ((False, []), (True, ["dirs", "phase"]), (False, []), False, False))

    # update_phase: con la escena viva NO hay búsqueda en paralelo (su único comando era el de resumen «GET pypi.org x2 · github.com»): cada comprobación teclea el suyo, real
    calls = []
    keep = (SCENE["on"], NO_UPDATES["on"], dict(LATE_UPDATES), dict(PREFETCH), {k: g[k] for k in ("check_due", "script_sig", "prefetch_phase", "check_update", "check_version", "check_dependencies", "prefetch_summary", "cleanup_internal")})
    try:
        NO_UPDATES["on"] = False
        LATE_UPDATES.update(on=False, done=False)
        g["check_due"] = lambda *a, **k: True
        g["script_sig"] = lambda: "sig"
        g["prefetch_phase"] = lambda sd, dd: calls.append(("prefetch", sd, dd)) or False
        g["check_update"] = lambda *a, **k: calls.append("update") or False
        g["check_version"] = lambda: calls.append("version") or True
        g["check_dependencies"] = lambda **k: calls.append("deps") or True
        g["prefetch_summary"] = lambda: None
        g["cleanup_internal"] = lambda: None
        SCENE["on"] = True
        rc_on = (update_phase(), list(calls))
        del calls[:]
        SCENE["on"] = False
        rc_off = (update_phase(), list(calls))
    finally:
        SCENE["on"], NO_UPDATES["on"] = keep[0], keep[1]
        LATE_UPDATES.clear()
        LATE_UPDATES.update(keep[2])
        PREFETCH.clear()
        PREFETCH.update(keep[3])
        g.update(keep[4])
    check("1.8.0: update_phase con la escena viva busca DLpy, pip y yt-dlp UNA A UNA (cada una con su comando real en D L P Y, sin el comando de resumen); sin escena siguen en paralelo",
          (rc_on, rc_off), ((None, ["update", "version", "deps"]), (None, [("prefetch", True, True), "update", "version", "deps"])))
    check("1.8.0: el comando de cada comprobación de la escena es el real (GET a GitHub / a PyPI), nunca el de resumen «x2 · github.com»",
          [_dlpy_topic(x)[1] for x in ("Comprobando DLpy", "Comprobando pip", "Comprobando yt-dlp")],
          [f"GET api.github.com/repos/{UPDATE_REPO}/releases", "GET pypi.org/pypi/pip/json", "GET pypi.org/pypi/yt-dlp/json"])

    # scene_welcome: antes de tapar el comando de D L P Y espera a que se haya mostrado entero (con la bienvenida ya puesta scene_status no lo espera)
    seen = []
    keep = (dict(SCENE), {k: g[k] for k in ("scene_wait_step", "scene_brand", "scene_busy", "scene_status", "welcome_hold")})
    try:
        SCENE.update(on=True, last_error=None, brand=True, busy=True, label="Comprobando DLpy", label_wall=time.time(), welcome=None)
        g["scene_wait_step"] = lambda old, limit=None, alive=None: seen.append(("wait", old, SCENE["welcome"])) or True
        g["scene_brand"] = lambda on=True: seen.append("brand")
        g["scene_busy"] = lambda on=True: seen.append("busy")
        g["scene_status"] = lambda text, pct=None, frac=None: seen.append(("status", text, (SCENE["welcome"] or {}).get("kind")))
        g["welcome_hold"] = lambda secs: seen.append("hold") or True
        scene_welcome("same", "1.8.0", "1.8.0")
        back = (SCENE["brand"], SCENE["busy"], SCENE["label"], SCENE["welcome"])
    finally:
        SCENE.clear()
        SCENE.update(keep[0])
        g.update(keep[1])
    check("1.8.0: scene_welcome espera a que el comando de D L P Y a la vista se muestre entero ANTES de poner la bienvenida, y luego deja la escena como estaba",
          (seen, back),
          ([("wait", "Comprobando DLpy", None), "brand", "busy", ("status", "Misma versión · 1.8.0", "same"), "hold"], (True, True, "Comprobando DLpy", None)))

    # scene_brand_end: al terminar el actualizador D L P Y se suelta; sin esto la descarga seguía bajo el título D L P Y y no pasaba al resto de las escenas
    seen, res = [], []
    keep = (dict(SCENE), g["scene_wait_step"])
    try:
        g["scene_wait_step"] = lambda old, limit=None, alive=None: seen.append(("wait", old)) or True
        SCENE.update(on=True, last_error=None, brand=True, busy=True, err_brand=False, label="Descargando video", label_wall=time.time())
        # con D L P Y encendido manda sobre «Descargando»
        res.append(scene_motif_kind(SCENE))
        res.append(scene_brand_end())
        res.append((SCENE["brand"], SCENE["busy"], SCENE["err_brand"], SCENE["label"]))
        # ya apagado: el centro es el de la descarga
        res.append(scene_motif_kind(SCENE))
        res.append(scene_brand_end())                                             # ya apagado: nada que hacer
        SCENE.update(brand=True, busy=True, last_error="x")
        # con un error D L P Y se queda (scene_error_end lo necesita)
        res.append((scene_brand_end(), SCENE["brand"]))
        SCENE.update(last_error=None, on=False)
        res.append((scene_brand_end(), SCENE["brand"]))                           # sin escena no toca nada
        SCENE.update(on=True, label_wall=None)
        # sin comando a la vista no espera (solo el primer caso esperó)
        res.append((scene_brand_end(), len(seen)))
    finally:
        SCENE.clear()
        SCENE.update(keep[0])
        g["scene_wait_step"] = keep[1]
    check("1.8.0: scene_brand_end: D L P Y se suelta y el centro pasa a la descarga, tras esperar el comando a la vista; sin escena, ya apagado o con error no toca nada",
          (res, seen),
          (["dlpy", True, (False, False, False, "Descargando video"), "rail", False, (False, True), (False, True), (True, 1)], [("wait", "Descargando video")]))

    order = []
    keep = (g["update_phase"], g["ux_brand_end"])
    try:
        g["update_phase"] = lambda: order.append("phase") or 1
        g["ux_brand_end"] = lambda: order.append("brand_end")
        rc_end = _m_update(None)
    finally:
        g["update_phase"], g["ux_brand_end"] = keep
    check("1.8.0: _m_update suelta D L P Y al terminar update_phase (el flujo pasa al resto de las escenas) y devuelve lo mismo que update_phase",
          (rc_end, order), (1, ["phase", "brand_end"]))


def _st_t37_sitio(check):
    """[T37] ── 1.8.1: el sitio (el análisis del enlace: audio y video que se transforman en lo detectado) tiene su propio loop de LOOP_SECS y el modo wait lo espera; D L P Y no tiene reglas de loop ──"""
    g = globals()
    k_ = LOOP_SECS
    r6 = lambda x: round(x, 6)

    # · el loop del sitio (_loop_site / motif_loop_left con kind None)
    S0, T0 = {"geo": (60, 24, 6, 17)}, {"ms": 2.0, "mt": None}
    check("sitio 1.8.1: _loop_site: recién entrado hay un loop entero; luego lo que falta para cerrar el que va en curso (aunque ya haya pasado 1 s) y 0 al cerrarlo",
          [r6(_loop_site(S0, T0, 60, lt)) for lt in (-0.1, 0.0, 0.3 * k_, k_, 2.3 * k_)],
          [r6(k_), r6(k_), r6(0.7 * k_), 0.0, r6((-2.3 * k_) % k_)])
    S1 = {"geo": (60, 24, 6, 17), "site_t": 5.0}
    check("sitio 1.8.1: lo detectado reinicia la cuenta (cuenta desde que llegó, no desde que entró el sitio); si llegó antes de que entrara, cuenta desde que entró",
          ([r6(motif_loop_left(S1, T0, None, ta)) for ta in (5.0, 5.0 + 0.4 * k_, 5.0 + k_, 5.0 + 1.25 * k_)],
           r6(motif_loop_left(dict(S1, site_t=1.0), T0, None, 2.0 + 0.4 * k_)), r6(motif_loop_left(dict(S1, site_t=None), T0, None, 2.0 + 0.4 * k_))),
          ([r6(k_), r6(0.6 * k_), 0.0, r6(0.75 * k_)], r6(0.6 * k_), r6(0.6 * k_)))
    _mx = max(motif_loop_left({"geo": (60, 24, 6, 17)}, {"ms": 0.0, "mt": None}, None, 0.013 * i) for i in range(0, 400))
    check("loops 1.8.1: el sitio cierra su loop en LOOP_SECS (ni más ni menos) y UX_HOLD (el paso fijo sin animación que medir) también dura LOOP_SECS",
          (_mx <= k_ + 1e-6, _mx >= k_ - 0.02, UX_HOLD == LOOP_SECS), (True, True, True))
    check("loops 1.8.1: D L P Y y la pregunta no tienen loop; las escenas de versión conservan sus 2 s; UPDATE_KINDS = D L P Y + las de versión",
          ([r6(motif_loop_left(S0, {"ms": 0.0, "mt": None}, kk, 0.3)) for kk in ("dlpy", "ask", "replace")],
           r6(motif_loop_left(S0, {"ms": 0.0, "mt": None}, "updated", 0.3)), WELCOME_CYCLE, set(UPDATE_KINDS) == {"dlpy"} | set(WELCOME_KINDS)),
          ([0.0, 0.0, 0.0], r6((-0.3) % WELCOME_CYCLE), 2.0, True))

    # · scene_site_mark, scene_title y scene_shape avisan de lo detectado
    keep, keep_tag = dict(SCENE), SESSION.get("tag")
    try:
        SCENE.clear()
        SCENE.update(scene_defaults())
        SCENE.update(on=True, ta=3.5)
        m1 = (scene_site_mark(), SCENE["site_t"])
        SCENE.update(past_dl=True, ta=9.0)
        m2 = (scene_site_mark(), SCENE["site_t"])
        SCENE.update(on=False, past_dl=False, ta=11.0)
        m3 = (scene_site_mark(), SCENE["site_t"])
        SCENE.update(on=True, past_dl=False, site_t=None, ta=4.0, title_raw="")
        scene_title("Pan  casero")
        t1 = (SCENE["title_raw"], SCENE["site_t"])
        SCENE.update(ta=6.0)
        scene_title("Pan casero")
        t2 = SCENE["site_t"]
        scene_title("Otro")
        t3 = SCENE["site_t"]
        SCENE.update(site_t=None, ta=7.0, aspect=None, res=None, alabel=None, mode="both", mode_orig="both", vinfo={}, ainfo={}, count=0)
        scene_shape({"width": 1920, "height": 1080})
        s1 = SCENE["site_t"]
        SCENE.update(ta=8.0)
        scene_shape({"width": 1920, "height": 1080})
        s2 = SCENE["site_t"]
        SCENE.update(ta=9.5)
        scene_shape({"is_live": True, "width": 1280, "height": 720})
        s3 = SCENE["site_t"]
        SCENE.update(past_dl=True, ta=12.0)
        scene_shape({"width": 640, "height": 360})
        s4 = SCENE["site_t"]
    finally:
        SCENE.clear()
        SCENE.update(keep)
        SESSION["tag"] = keep_tag
    check("sitio 1.8.1: scene_site_mark anota cuándo llegó lo detectado (solo con escena y antes de la primera pista)", (m1, m2, m3), ((True, 3.5), (False, 3.5), (False, 3.5)))
    check("sitio 1.8.1: scene_title anota solo si el título cambia (el mismo título normalizado no reinicia el loop)", (t1, t2, t3), (("Pan casero", 4.0), 4.0, 6.0))
    check("sitio 1.8.1: scene_shape anota cuando lo detectado cambia (resolución, directo…), no con lo mismo, ni ya con la descarga en marcha", (s1, s2, s3, s4), (7.0, 7.0, 9.5, 9.5))

    # · scene_gate (wait): el sitio es una escena; la intro corriendo cuenta como sitio; D L P Y no espera
    thg = threading.Thread(target=time.sleep, args=(30.0,), daemon=True)
    thg.start()
    fut = time.time() + 1e6
    keep, keep_mode = dict(SCENE), g["SCENE_MODE"]
    try:
        SCENE.clear()
        SCENE.update(scene_defaults())
        SCENE.update(on=True, th=thg)

        def gate(md, mv, nk=None):
            g["SCENE_MODE"], SCENE["mvis"] = md, mv
            SCENE["gate_paid"] = SCENE["loop_paid"] = None
            t_ = time.time()
            r_ = scene_gate(nk)
            return r_, round(time.time() - t_, 1)
        gt = [gate(("loop", None), (None, True, 0.4, fut, 1.0), "rail"),
              gate(("loop", None), (None, True, 0.4, fut, 1.0), "dlpy"),
              gate(("loop", None), (None, True, 0.4, fut, 1.0), "updated"),
              gate(("loop", None), (None, True, 0.4, fut, 1.0)),
              gate(("real", None), (None, True, 0.4, fut, 1.0), "rail"),
              gate(("secs", 2.0), (None, True, 0.4, fut, 1.0), "rail"),
              gate(("loop", None), ("dlpy", True, 0.0, fut, 1.0), "rail"),
              gate(("loop", None), ("idle", True, 0.4, fut, 1.0), "rail")]
        check("sitio 1.8.1: scene_gate espera el loop que le falta al sitio al pasar a otro dibujo; no hacia D L P Y ni sus escenas de versión, ni sitio→sitio, ni en real o segundos, ni desde D L P Y (sin loop) o el Pulso",
              gt, [(True, 0.4), (False, 0.0), (False, 0.0), (False, 0.0), (False, 0.0), (False, 0.0), (False, 0.0), (False, 0.0)])
        g["SCENE_MODE"], SCENE["mvis"], SCENE["gate_paid"], SCENE["loop_paid"] = ("loop", None), None, None, None

        def publish():
            time.sleep(0.15)
            SCENE["mvis"] = (None, True, 0.2, fut, 1.0)
        th_ = threading.Thread(target=publish)
        th_.start()
        t_ = time.time()
        r_i = scene_gate("rail")
        d_i = time.time() - t_
        th_.join()
        SCENE.update(mvis=None, gate_paid=None, loop_paid=None)
        t_ = time.time()
        r_j = scene_gate()
        d_j = time.time() - t_
        check("sitio 1.8.1: con la intro aún corriendo (sin dibujo publicado) scene_gate espera a que el sitio entre y cierre su loop; sitio→sitio no espera",
              (r_i, 0.3 < d_i < 0.8, r_j, d_j < 0.2), (True, True, False, True))
    finally:
        SCENE.clear()
        SCENE.update(keep)
        g["SCENE_MODE"] = keep_mode

    # · scene_motif: el sitio no se deshace hasta cerrar su loop (wait), pero no retiene a D L P Y; en real no retiene nada
    ra, rb = (255, 0, 0), (0, 0, 255)

    def fresh():
        return {"mcur": None, "mprev": None, "mt": None, "ms": 0.0, "msp": 0.0, "site_done": set(), "site_done_at": {}, "site_prev_cells": {}, "site_trans_t": None}

    def base(**kw):
        return dict({"geo": (60, 24, 6, 17), "a": ra, "b": rb, "brand": False, "conv": None, "label": "Analizando enlace", "done": set(), "mode_orig": "both",
                     "stream_total": 2, "stream_seen": 0, "site_t": 3.0}, **kw)
    keep_mode = g["SCENE_MODE"]
    try:
        g["SCENE_MODE"] = ("loop", None)
        sj, stj = base(), fresh()
        scene_motif(sj, stj, {}, 3.0, 1.16, 1)
        sj.update(label="Descargando video 1/2", stream_seen=1, skind={1: "video"}, spct={1: 5.0}, past_dl=True)
        seen = []
        for q, tt_ in enumerate((3.3, 3.9, 4.05)):
            scene_motif(sj, stj, {}, tt_, 1.16, 2 + q)
            seen.append(stj["mcur"])
        sd, std = base(brand=True, label="Comprobando pip"), fresh()
        scene_motif(sd, std, {}, 3.3, 1.16, 1)
        g["SCENE_MODE"] = ("real", None)
        sr, str_ = base(label="Descargando video 1/2", stream_seen=1, skind={1: "video"}, spct={1: 5.0}, past_dl=True), fresh()
        scene_motif(sr, str_, {}, 3.3, 1.16, 1)
    finally:
        g["SCENE_MODE"] = keep_mode
    check("sitio 1.8.1: wait: el sitio no se deshace hasta cerrar su loop (cuenta desde lo detectado); D L P Y entra sin esperarlo; real no retiene nada",
          (seen, std["mcur"], str_["mcur"]), ([None, None, "rail"], "dlpy", "rail"))

    # · el primer cuadro: scene_stream marca past_dl antes de esperar en la compuerta, así que el primer cuadro ya pide otro dibujo y el sitio igual se ve su loop
    try:
        g["SCENE_MODE"] = ("loop", None)
        sf, stf = base(label="Descargando video 1/2", stream_seen=1, skind={1: "video"}, spct={1: 5.0}, past_dl=True, site_t=None), {}
        first = []
        for q, tt_ in enumerate((3.0, 3.5, 3.0 + 0.9 * k_, 3.0 + k_ + 0.05)):
            scene_motif(sf, stf, {}, tt_, 1.16, 20 + q)
            first.append(stf["mcur"])
        sf2, stf2 = base(label="Descargando video 1/2", stream_seen=1, skind={1: "video"}, spct={1: 5.0}, past_dl=True, resume=True), {}
        scene_motif(sf2, stf2, {}, 3.0, 1.16, 30)
    finally:
        g["SCENE_MODE"] = keep_mode
    check("sitio 1.8.1: aunque el primer cuadro ya pida otro dibujo (análisis rápido) el sitio se ve su loop entero; al volver de la lista (resume) no se retiene",
          (first, stf2["mcur"]), ([None, None, None, "rail"], "rail"))

    # · configuración
    cfg = {n: t for n, _v, t in CONFIG_OPTIONS}
    check("config 1.8.1: DLPY_UX y DLPY_LOOP dicen que el análisis del enlace es una escena y que D L P Y no espera",
          ("análisis del enlace" in cfg["DLPY_UX"] and "D L P Y" in cfg["DLPY_UX"], "análisis del enlace" in cfg["DLPY_LOOP"] and "D L P Y" in cfg["DLPY_LOOP"]), (True, True))



def _st_t38_topbar(check):
    """[T38] ── 1.8.3: franja superior DLPY_TOPBAR (D/T/V, orden, default 0) ──"""
    check("topbar 1.8.3: apagada con 0 / off / vacío",
          [topbar_parse(x) for x in ("0", "off", "", "no", None)],
          [(), (), (), (), ()])
    check("topbar 1.9.4: 1 / on / all = DTV (la N pasó a la franja inferior)",
          [topbar_parse(x) for x in ("1", "on", "all")],
          [("D", "T", "V"), ("D", "T", "V"), ("D", "T", "V")])
    check("topbar 1.8.3: el orden de letras manda (VTD, DV, V) y no se repiten",
          [topbar_parse(x) for x in ("VTD", "dv", "V", "D,T,V", "vtdv")],
          [("V", "T", "D"), ("D", "V"), ("V",), ("D", "T", "V"), ("V", "T", "D")])
    keep = TOPBAR
    try:
        globals()["TOPBAR"] = ("V",)
        t1 = topbar_line(BOOT_T0 + 42)
        globals()["TOPBAR"] = ("D", "T", "V")
        t2 = topbar_line(BOOT_T0 + 62)
        globals()["TOPBAR"] = ()
        t0 = topbar_line(BOOT_T0)
    finally:
        globals()["TOPBAR"] = keep
    check("topbar 1.8.3: texto según campos (vVERSION · tiempo mm:ss · device)",
          (t1 == f"v{VERSION}", "  ·  " in t2, t2.endswith(f"v{VERSION}"), t2.split("  ·  ")[1] == "1:02", t0 == ""),
          (True, True, True, True, True))
    cells = scene_topbar_cells(40, "iPhone  ·  0:42  ·  v1.8.3")
    ys = {y for (_x, y) in cells}
    check("topbar 1.9.2: se pinta centrada en la fila 2, con márgenes laterales, y no se pinta si no cabe",
          (ys == {2}, min((x for x, _y in cells), default=0) >= 2, max((x for x, _y in cells), default=0) <= 39, scene_topbar_cells(10, "iPhone  ·  0:42  ·  v1.8.3") == {}),
          (True, True, True, True))
    cfg = {n: t for n, _v, t in CONFIG_OPTIONS}
    check("topbar 1.8.3: DLPY_TOPBAR está en CONFIG_OPTIONS (default 0)",
          ("DLPY_TOPBAR" in cfg and cfg["DLPY_TOPBAR"].startswith("franja") and any(n == "DLPY_TOPBAR" and v == "0" for n, v, _t in CONFIG_OPTIONS)),
          True)


def _st_t40_red(check):
    """[T40] ── 1.8.8: icono de red ⇅ (1.9.4: letra N de DLPY_BOTTOMBAR, antes de DLPY_TOPBAR): estado con candado, ancho fijo, ganchos y configuración ──"""
    import threading as _th
    import urllib.request as _ur
    g = globals()
    check("red 1.9.4: la letra N ya no es de topbar_parse (se ignora) y sí de bottom_bar_parse (sola, ordenada y con otras)",
          ([topbar_parse(x) for x in ("N", "DTVN", "ND", "nvx", "1", "all")],
           [bottom_bar_parse(x) for x in ("N", "EAN", "NE", "nvx", "1", "all")]),
          ([(), ("D", "T", "V"), ("D",), ("V",), ("D", "T", "V"), ("D", "T", "V")],
           [("N",), ("E", "A", "N"), ("N", "E"), ("N",), ("E", "A", "N"), ("E", "A", "N")]))
    check("red 1.9.4: config_validate: DLPY_BOTTOMBAR acepta N; DLPY_TOPBAR ya no y sigue rechazando letras ajenas",
          ([config_validate("DLPY_BOTTOMBAR", x) for x in ("N", "eAn", "1", "0", "xyz")],
           [config_validate("DLPY_TOPBAR", x) for x in ("N", "dtv", "1", "0", "xyz")]),
          ([(True, "N"), (True, "EAN"), (True, "1"), (True, "0"), (False, None)],
           [(False, None), (True, "DTV"), (True, "1"), (True, "0"), (False, None)]))
    cfg = {n: t for n, _v, t in CONFIG_OPTIONS}
    check("red 1.9.4: la descripción de DLPY_BOTTOMBAR habla de N y de ⇅, la de DLPY_TOPBAR ya no; DLPY_TOPBAR conserva el default 0 y DLPY_BOTTOMBAR pasa a 1",
          (("N" in cfg["DLPY_BOTTOMBAR"] and "⇅" in cfg["DLPY_BOTTOMBAR"]), "⇅" in cfg["DLPY_TOPBAR"],
           all(any(n == k and v == d for n, v, _t in CONFIG_OPTIONS) for k, d in (("DLPY_TOPBAR", "0"), ("DLPY_BOTTOMBAR", "1")))), (True, False, True))

    keep_state, keep_bar = dict(NETSTATE), TOPBAR
    try:
        NETSTATE.update(busy=0, last=0.0)
        check("red 1.8.8: sin actividad no hay conexión", net_active(100.0), False)
        net_begin()
        check("red 1.8.8: con una petición en curso hay conexión (aunque pase el tiempo)", (net_active(), net_active(time.time() + 60)), (True, True))
        net_end()
        t_end = NETSTATE["last"]
        check("red 1.8.8: tras acabar sigue encendida NET_HOLD s y luego se apaga",
              (net_active(t_end + NET_HOLD * 0.5), net_active(t_end + NET_HOLD + 0.01)), (True, False))
        NETSTATE.update(busy=0, last=0.0)
        net_touch(50.0)
        check("red 1.8.8: net_touch (avance de descarga) enciende por NET_HOLD s", (net_active(50.5), net_active(50.0 + NET_HOLD + 0.1), net_active(49.0)), (True, False, False))
        NETSTATE.update(busy=0, last=0.0)
        try:
            with net_busy():
                inside = NETSTATE["busy"]
                raise ValueError("x")
        except ValueError:
            pass
        check("red 1.8.8: net_busy libera también si la operación falla", (inside, NETSTATE["busy"]), (1, 0))

        def _work():
            for _i in range(300):
                with net_busy():
                    pass
        ths = [_th.Thread(target=_work) for _ in range(8)]
        for t_ in ths:
            t_.start()
        for t_ in ths:
            t_.join()
        check("red 1.8.8: hilos en paralelo dejan el contador en 0", NETSTATE["busy"], 0)
        net_end()
        check("red 1.8.8: net_end de más no baja de 0", NETSTATE["busy"], 0)
        NETSTATE.update(busy=0, last=100.0)
        check("red 1.8.9: net_level vale 1 hasta los últimos NET_FADE s de NET_HOLD, baja a 0 (fundido) y es 0 después y antes",
              [round(net_level(100.0 + dt), 3) for dt in (0.0, NET_HOLD - NET_FADE, NET_HOLD - NET_FADE / 2, NET_HOLD, NET_HOLD + 1, -1.0)],
              [1.0, 1.0, 0.5, 0.0, 0.0, 0.0])
        check("red 1.8.9: net_level > 0 equivale a net_active (el mismo intervalo)",
              all((net_level(100.0 + i_ / 50) > 0.0) == net_active(100.0 + i_ / 50) for i_ in range(-10, 100)), True)
        net_begin()
        busy_lv = (net_level(), net_level(time.time() + 60))
        net_end()
        check("red 1.8.9: con una petición en curso net_level es 1 (aunque pase el tiempo)", busy_lv, (1.0, 1.0))
        NETSTATE.update(busy=0, last=0.0)
        check("red 1.8.9: sin actividad net_level es 0", net_level(100.0), 0.0)

        # --- 1.9.4: la N vive en la franja inferior (DLPY_BOTTOMBAR): el icono siempre está (mismo texto y ancho con o sin red); solo cambia el color
        keep_bottom = BOTTOMBAR
        t0 = BOOT_T0 + 42.0
        res = {}
        for combo in (("N",), ("E", "A", "N"), ("N", "E"), ("N", "A"), ("E", "N", "A")):
            g["BOTTOMBAR"] = combo
            NETSTATE.update(busy=0, last=0.0)
            off = bottom_bar_line()
            NETSTATE.update(busy=0, last=time.time())
            on = bottom_bar_line()
            res[combo] = (on == off, off.count(NET_ICON) == 1, off == off.strip() and not off.startswith("·") and not off.endswith("·"))
        check("red 1.9.4: con N el ⇅ siempre está en la franja inferior y el texto no cambia con la red (sin huecos ni puntos colgados)",
              all(v == (True, True, True) for v in res.values()), True)
        g["BOTTOMBAR"] = ("N", "E")
        check("red 1.9.4: N delante de E: «⇅  ·  ✕» con o sin red", bottom_bar_line(), f"{NET_ICON}  ·  ✕")
        g["BOTTOMBAR"] = ("E", "A")
        check("red 1.9.4: sin N la franja inferior no lleva el icono", NET_ICON not in bottom_bar_line(), True)
        g["BOTTOMBAR"] = ("N",)
        txt_n = bottom_bar_line()
        NETSTATE.update(busy=0, last=0.0)
        cn_off = scene_bottom_bar_cells(60, 20)
        net_begin()
        cn_on = scene_bottom_bar_cells(60, 20)
        net_end()
        NETSTATE.update(busy=0, last=time.time() - (NET_HOLD - NET_FADE / 2))
        cn_mid = scene_bottom_bar_cells(60, 20)
        NETSTATE.update(busy=0, last=0.0)
        icon_cols = lambda cs_: [v[1] for v in cs_.values() if v[0] == NET_ICON]
        check("red 1.9.4: solo N pinta únicamente el icono en la fila indicada: gris tenue sin red, blanco con petición en curso y entre ambos al apagarse",
              (txt_n, icon_cols(cn_off), icon_cols(cn_on), {y for _x, y in cn_on},
               len(icon_cols(cn_mid)) == 1 and all(d < m < w for d, m, w in zip(SCENE_DIM, icon_cols(cn_mid)[0], SCENE_WHITE)),
               set(cn_off) == set(cn_on) == set(cn_mid)),
              (NET_ICON, [SCENE_DIM], [SCENE_WHITE], {20}, True, True))
        g["BOTTOMBAR"] = ("E", "A", "N")
        with DIAGNOSTICS_LOCK:
            keep_act = dict(DIAGNOSTICS_ACTIVITY)
            DIAGNOSTICS_ACTIVITY.update(E=0.0, A=0.0)
        net_begin()
        mixed = scene_bottom_bar_cells(60, 20)
        net_end()
        with DIAGNOSTICS_LOCK:
            DIAGNOSTICS_ACTIVITY.update(keep_act)
        check("red 1.9.4: en la franja inferior solo la N se ilumina con la red; E y A siguen grises",
              ({v[1] for v in mixed.values() if v[0] == NET_ICON}, {v[1] for v in mixed.values() if v[0] in ("✕", "!")}),
              ({SCENE_WHITE}, {SCENE_DIM}))
        g["BOTTOMBAR"] = ("E", "A", "N")
        w_full = dwidth(bottom_bar_line())
        check("red 1.9.4: si no cabe se quita primero la N, luego A (E se conserva)",
              [bottom_bar_line(width=x) for x in (None, w_full, w_full - 1, dwidth("✕") + 3, 0)],
              [f"✕  ·  !  ·  {NET_ICON}", f"✕  ·  !  ·  {NET_ICON}", "✕  ·  !", "✕  ·  !" if dwidth("✕  ·  !") <= dwidth("✕") + 3 else "✕", "✕"])
        g["BOTTOMBAR"] = keep_bottom

        # --- franja superior sin N: D, T y V; si no cabe se quitan D y T y se conserva el orden
        g["TOPBAR"] = ("D", "T", "V")
        sep, d_, tm, vv = "  ·  ", device_label(), "0:42", f"v{VERSION}"
        full, no_d = sep.join([d_, tm, vv]), sep.join([tm, vv])
        check("franja 1.9.4: si no cabe se quitan D y T en ese orden (siempre queda la versión)",
              [topbar_line(t0, width=x) for x in (None, dwidth(full), dwidth(full) - 1, dwidth(no_d) - 1, 0)],
              [full, full, no_d, vv, vv])
        g["TOPBAR"] = ("V", "T", "D")
        check("franja 1.9.4: al quitar campos se respeta el orden de letras de los que quedan",
              topbar_line(t0, width=dwidth(sep.join([vv, tm, d_])) - 1), sep.join([vv, tm]))
        g["TOPBAR"] = ("D", "T", "V")
        NETSTATE.update(busy=0, last=0.0)
        net_begin()
        c_net = topbar_cells(dwidth(full) + 8)
        net_end()
        check("franja 1.9.4: la franja superior no lleva ⇅ ni cambia con la red", (NET_ICON in {v[0] for v in c_net.values()}, {v[1] for v in c_net.values()}), (False, {SCENE_DIM}))

        # --- modo calmado (DLPY_CALM=1): gris más claro, como el resto del texto tenue; el icono de la franja inferior sigue pasando a blanco con red
        g["BOTTOMBAR"] = ("N", "E")
        keep_calm = SCENE_CALM
        with DIAGNOSTICS_LOCK:
            keep_act = dict(DIAGNOSTICS_ACTIVITY)
            DIAGNOSTICS_ACTIVITY.update(E=0.0, A=0.0)
        try:
            g["SCENE_CALM"] = True
            NETSTATE.update(busy=0, last=0.0)
            k_off = scene_bottom_bar_cells(60, 20)
            net_begin()
            k_on = scene_bottom_bar_cells(60, 20)
            net_end()
        finally:
            g["SCENE_CALM"] = keep_calm
            g["BOTTOMBAR"] = keep_bottom
            with DIAGNOSTICS_LOCK:
                DIAGNOSTICS_ACTIVITY.update(keep_act)
        check("franja 1.9.4: con DLPY_CALM=1 el texto tenue usa SCENE_GRAY y el ⇅ de la franja inferior sigue pasando a blanco con red",
              ({v[1] for v in k_off.values()}, {v[1] for v in k_on.values() if v[0] != NET_ICON}, [v[1] for v in k_on.values() if v[0] == NET_ICON]),
              ({SCENE_GRAY}, {SCENE_GRAY}, [SCENE_WHITE]))
        check("topbar: aparece al empezar a analizar o fuera de la escena D L P Y; oculta durante D L P Y y si está apagada",
              [(g.__setitem__("TOPBAR", tb), topbar_visible(st))[1] for tb, st in
               ((("V",), {"label": "Analizando"}), (("V",), {"label": "Descargando video"}), (("V",), {"past_dl": True}),
                (("V", "D"), {"label": "Analizando", "brand": True}), ((), {"label": "Descargando"}),
                (("V",), {"label": "Comprobando", "brand": True}), (("V",), {"label": "Preparando"}))],
              [True, True, True, True, False, False, True])
        check("red 1.8.8: ⇅ mide 1 celda (a-Shell)", dwidth(NET_ICON), 1)

        # --- ganchos
        class _Resp:
            def __init__(self, seen):
                self.seen = seen

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self, n=-1):
                self.seen.append(NETSTATE["busy"])
                return b"ok"

            def getcode(self):
                return 200
        seen = []
        _uo = _ur.urlopen
        try:
            _ur.urlopen = lambda *a, **k: _Resp(seen)
            NETSTATE.update(busy=0, last=0.0)
            got = fresh_bytes("https://example.invalid/x")
        finally:
            _ur.urlopen = _uo
        check("red 1.8.8: fresh_bytes marca la red mientras lee y la suelta al terminar", (got, seen, NETSTATE["busy"]), (b"ok", [1], 0))

        seen_y = []

        class _YDL:
            def urlopen(self, *a, **k):
                seen_y.append(("u", NETSTATE["busy"]))
                return "r"

            def extract_info(self, url, download=True, **k):
                seen_y.append(("e" if download else "a", NETSTATE["busy"]))
                return {"u": url}

        class _Mod:
            YoutubeDL = _YDL
        NETSTATE.update(busy=0, last=0.0)
        net_wrap_ytdlp(_Mod)
        net_wrap_ytdlp(_Mod)                                   # idempotente: no se envuelve dos veces
        y = _YDL()
        y.urlopen("x")
        y.extract_info("l", download=False)
        y.extract_info("l", False)
        y.extract_info("l", download=True)
        y.extract_info("l")
        check("red 1.8.8: yt-dlp marca urlopen y el análisis (download=False, por nombre o posición), no la descarga ni el posproceso",
              (seen_y, NETSTATE["busy"]), ([("u", 1), ("a", 1), ("a", 1), ("e", 0), ("e", 0)], 0))
    finally:
        g["TOPBAR"] = keep_bar
        NETSTATE.clear()
        NETSTATE.update(keep_state)


def _version_problems(text, filename=None):
    """1.8.7: incoherencias de versión de un dlpy.py: VERSION (x.y.z, con Y y Z hasta 9), un solo changelog con esa versión y, si el archivo se llama dlpy_x.y.z.py, que coincida."""
    probs = []
    m = re.search(r'(?m)^VERSION = "([^"]*)"[ \t]*$', text)
    ver = m.group(1) if m else None
    if not ver or not re.fullmatch(r"\d+\.[0-9]\.[0-9]", ver):
        probs.append(f"VERSION inválida: {ver!r}")
    if not text.startswith("#!dlpy.py"):
        probs.append("la primera línea no empieza con #!dlpy.py")
    a, b = text.find("# ==== CHANGELOG ===="), text.find("# ==== FIN CHANGELOG ====")
    if a < 0 or b < a:
        probs.append("falta el bloque CHANGELOG")
    else:
        heads = re.findall(r"(?m)^# ## (\S+)\s*$", text[a:b])
        if heads != [ver]:
            probs.append(f"el changelog debe tener solo la versión {ver}: {heads}")
        if not re.search(r"(?m)^# - \S", text[a:b]):
            probs.append("el changelog no tiene viñetas")
    fm = re.fullmatch(r"dlpy_(\d+\.\d+\.\d+)\.py", os.path.basename(filename or ""))
    if fm and fm.group(1) != ver:
        probs.append(f"el nombre del archivo ({fm.group(1)}) no coincide con VERSION ({ver})")
    return probs


def _st_t39_version(check):
    """[T39] ── 1.8.7: VERSION, changelog y nombre de archivo coherentes (las reglas de la cabecera) ──"""
    good = '#!dlpy.py - x\n# ==== CHANGELOG ====\n#\n# ## 1.8.7\n#\n# - algo\n# ==== FIN CHANGELOG ====\n\nVERSION = "1.8.7"\n'
    check("versión: un texto coherente no da problemas", _version_problems(good, "dlpy_1.8.7.py"), [])
    check("versión: el nombre dlpy.py (instalado) no se compara", _version_problems(good, "dlpy.py"), [])
    check("versión: nombre de archivo distinto a VERSION", len(_version_problems(good, "dlpy_1.8.6.py")), 1)
    check("versión: Z de dos cifras no vale (solo hasta 9)", len(_version_problems(good.replace("1.8.7", "1.8.10"), None)), 1)
    check("versión: changelog con otra versión o con dos", [len(_version_problems(good.replace("# ## 1.8.7", "# ## 1.8.6"), None)),
          len(_version_problems(good.replace("# - algo", "# ## 1.8.6\n# - algo"), None))], [1, 1])
    check("versión: sin bloque de changelog", len(_version_problems('#!dlpy.py\nVERSION = "1.8.7"\n', None)) >= 1, True)
    try:
        with open(os.path.abspath(__file__), encoding="utf-8") as fh:
            own = fh.read()
    except OSError:
        check("versión: sin acceso al propio código (se omite)", True, True)
        return
    check("versión: este archivo es coherente (VERSION, changelog y nombre)", _version_problems(own, os.path.abspath(__file__)), [])
    check("versión: VERSION del texto = VERSION en ejecución", re.search(r'(?m)^VERSION = "([^"]*)"', own).group(1), VERSION)


# ─────────── [T41] Motor de idiomas: paquetes por idioma (1.9.2) ───────────
def _st_t41_motor_idiomas(check):
    """[T41] 1.9.2: gettext .mo, Release independiente, SHA-256 y calendario compartido DLPY_UPDATES."""
    import hashlib
    import tempfile
    g = globals()

    def _make_mo(language="ko", revision="1.9.0", catalog_format=PACK_FORMAT,
                 bad_placeholder=False, missing_plural=False, cancel="취소됨."):
        """Catálogo GNU MO mínimo para probar el cargador sin msgfmt, red ni paquetes instalados."""
        meta = (
            "Project-Id-Version: DLpy selftest\n"
            f"Language: {language}\n"
            "MIME-Version: 1.0\n"
            "Content-Type: text/plain; charset=UTF-8\n"
            "Content-Transfer-Encoding: 8bit\n"
            "Plural-Forms: nplurals=1; plural=0;\n"
            f"X-DLpy-Catalog-Format: {catalog_format}\n"
            f"X-DLpy-Catalog-Revision: {revision}\n"
        )
        entries = {
            "": meta,
            "ui\x04Cancelado.": cancel,
            "ui\x04Seleccione idioma": LANG_SELECT_TEXT["ko"],
            "ui\x04Enter sustituir": "Enter 대체",
            "noun\x04device": "기기",
            "template\x04Language {0} is not available offline; using English":
                "언어 테스트" if bad_placeholder else "{0} 테스트",
            "meaning\x04Review": "확인",
            "review\x04Review": "검토",
        }
        rows = [(k.encode("utf-8"), v.encode("utf-8")) for k, v in entries.items()]
        rows.append(("noun:files\x04archivo\x00archivos".encode("utf-8"), "파일".encode("utf-8")))
        rows.append(("noun:hour\x04hour\x00hours".encode("utf-8"), "시간".encode("utf-8")))
        if not missing_plural:
            rows.append(("noun:day\x04day\x00days".encode("utf-8"), "일".encode("utf-8")))
        rows.sort(key=lambda x: x[0])
        count = len(rows)
        orig_off = 28
        trans_off = orig_off + 8 * count
        orig_blob = bytearray()
        trans_blob = bytearray()
        orig_table, trans_table = [], []
        blob_start = 28 + 16 * count
        for original, _translated in rows:
            orig_table.append((len(original), blob_start + len(orig_blob)))
            orig_blob.extend(original + b"\0")
        trans_start = blob_start + len(orig_blob)
        for _original, translated in rows:
            trans_table.append((len(translated), trans_start + len(trans_blob)))
            trans_blob.extend(translated + b"\0")
        out = bytearray(struct.pack("<7I", 0x950412de, 0, count, orig_off, trans_off, 0, 0))
        for pair in orig_table:
            out.extend(struct.pack("<2I", *pair))
        for pair in trans_table:
            out.extend(struct.pack("<2I", *pair))
        out.extend(orig_blob)
        out.extend(trans_blob)
        return bytes(out)

    tabs = (I18N, I18N_PHRASES, I18N_WELCOME, I18N_UX, I18N_FMT, I18N_DEVICE)
    saved_tabs = [dict.get(table, "ko") for table in tabs]
    saved_loaded = "ko" in PACK_STATE["loaded"]
    saved_tried = "ko" in PACK_STATE["tried"]
    saved_warned = "ko" in PACK_STATE["warned"]
    saved_err = PACK_STATE["err"].get("ko")
    saved_missing = PACK_STATE["missing"].get("ko")
    saved_translation = LANG_TRANSLATIONS.get("ko")
    saved_tpl = _TPL_PACK.get("ko")
    saved_rx = _TPL_RX.get("ko")
    saved_env = os.environ.get("DLPY_LANG_DIR")
    saved_no_updates = NO_UPDATES["on"]
    saved_check_file = CHECK_FILE
    saved_update_hours = UPDATE_HOURS
    saved_files_dir, saved_internal_dir = FILES_DIR, INTERNAL_DIR
    saved_fns = {name: g[name] for name in ("fresh_bytes",)}

    def reset_ko():
        for table in tabs:
            dict.pop(table, "ko", None)
        LANG_TRANSLATIONS.pop("ko", None)
        PACK_STATE["loaded"].discard("ko")
        PACK_STATE["tried"].discard("ko")
        PACK_STATE["warned"].discard("ko")
        PACK_STATE["err"].pop("ko", None)
        PACK_STATE["missing"].pop("ko", None)
        _TPL_PACK.pop("ko", None)
        _TPL_RX.pop("ko", None)

    def put(directory, raw, sha=None):
        path = os.path.join(directory, "dlpy_lang_ko.mo")
        digest = sha or hashlib.sha256(raw).hexdigest()
        with open(path, "wb") as handle:
            handle.write(raw)
        with open(path + ".sha256", "w", encoding="utf-8") as handle:
            handle.write("%s  dlpy_lang_ko.mo\n" % digest)

    tmp = tempfile.mkdtemp(prefix="dlpy_lang_i18n_192_")
    try:
        # Verifica que la ruta predeterminada esté bajo internal/ y que el estado de intervalos sea aislado.
        os.environ.pop("DLPY_LANG_DIR", None)
        g["FILES_DIR"] = tmp
        g["INTERNAL_DIR"] = os.path.join(tmp, "internal")
        check("1.9.2: los catálogos viven en internal/languages", lang_pack_dir(), os.path.join(tmp, "internal", "languages"))
        g["FILES_DIR"], g["INTERNAL_DIR"] = saved_files_dir, saved_internal_dir
        os.environ["DLPY_LANG_DIR"] = tmp
        g["CHECK_FILE"] = os.path.join(tmp, "checks.json")
        g["UPDATE_HOURS"] = 24.0
        NO_UPDATES["on"] = True
        reset_ko()

        # Sin paquete local ni red, el idioma se resuelve al respaldo inglés.
        fallback = t_display("Cancelado.", lang="en")
        check("1.9.2: sin catálogo local se usa inglés sin red",
              [lang_pack_load("ko"), lang_effective("ko"), t_display("Cancelado.", lang="ko")],
              [False, "en", fallback])

        # El paquete 1.9.0 debe ser válido en el script 1.9.2: revision ya no es VERSION.
        valid = _make_mo(revision="1.9.0")
        parsed = lang_pack_check(valid, "ko")
        check("1.9.2: catálogo 1.9.0 válido en motor 1.9.2", parsed is not None, True)
        check("1.9.2: revisión independiente aceptada; formato, idioma y plurales se siguen validando",
              [lang_pack_check(_make_mo(revision="2026.11.14"), "ko") is not None,
               lang_pack_check(_make_mo(revision=""), "ko"),
               lang_pack_check(_make_mo(catalog_format=PACK_FORMAT + 1), "ko"),
               lang_pack_check(_make_mo(language="pt"), "ko"),
               lang_pack_check(b"not a GNU catalog", "ko"),
               lang_pack_check(_make_mo(missing_plural=True), "ko")],
              [True, None, None, None, None, None])

        # Una variable mal conservada se elimina solo de esa entrada.
        reset_ko()
        bad_tr = lang_pack_check(_make_mo(bad_placeholder=True), "ko")
        template_msgid = "template\x04Language {0} is not available offline; using English"
        check("1.9.2: variable defectuosa se elimina con respaldo inglés por mensaje",
              [bad_tr is not None, template_msgid in getattr(bad_tr, "_catalog", {}), PACK_STATE["err"].get("ko")],
              [True, False, "placeholders:1"])

        # El hash local es obligatorio.
        reset_ko()
        path = os.path.join(tmp, "dlpy_lang_ko.mo")
        with open(path, "wb") as handle:
            handle.write(valid)
        check("1.9.2: catálogo local sin .sha256 se rechaza", lang_pack_load("ko"), False)
        reset_ko()
        put(tmp, valid, sha="0" * 64)
        check("1.9.2: SHA-256 local incorrecto se rechaza", [lang_pack_load("ko"), PACK_STATE["err"].get("ko")], [False, "sha"])

        # Catálogo correcto: los adaptadores, contexto y plural siguen funcionando.
        reset_ko()
        put(tmp, valid)
        ok = lang_pack_load("ko")
        check("1.9.2: catálogo local validado alimenta los adaptadores",
              [ok, I18N["ko"]["Cancelado."], t_display("Cancelado.", lang="ko"),
               I18N_DEVICE["ko"], t_display("Comprobando pip", lang="ko"), lang_effective("ko")],
              [True, "취소됨.", "취소됨.", "기기", "Checking pip", "ko"])
        template_result = t_display("Idioma 日本語 no disponible sin conexión; se usa inglés", lang="ko")
        check("1.9.2: los contextos separan significados y mantienen variables/plurales",
              [trc("meaning", "Review", lang="ko"), trc("review", "Review", lang="ko"),
               template_result.startswith("日本語 "),
               trn("archivo", "archivos", 1, lang="ko"), trn("archivo", "archivos", 9, lang="ko"),
               t_display("Review my downloaded video.mp4", lang="ko")],
              ["확인", "검토", True, "파일", "파일", "Review my downloaded video.mp4"])

        # El enlace es fijo e independiente de la versión de DLpy.
        check("2.0.1: URL del catálogo y del SHA256SUMS apuntan a languages/ en main",
              [lang_pack_url("ko"), lang_pack_sha_url("ko")],
              ["https://raw.githubusercontent.com/ElDelDLpy/DLpy/main/languages/dlpy_lang_ko.mo",
               "https://raw.githubusercontent.com/ElDelDLpy/DLpy/main/languages/SHA256SUMS"])
        _sums = ("%s  dlpy_lang_ja.mo\n%s *dlpy_lang_ko.mo\n" % ("a" * 64, "b" * 64))
        check("2.0.1: SHA256SUMS: la línea de cada idioma; sin el idioma pedido no hay hash (nunca el de otro); un solo hash sin nombre sigue valiendo",
              [_lang_pack_sha_value(_sums, "dlpy_lang_ko.mo"), _lang_pack_sha_value(_sums, "dlpy_lang_ja.mo"), _lang_pack_sha_value(_sums, "dlpy_lang_fr.mo"),
               _lang_pack_sha_value(("c" * 64) + "\n", "dlpy_lang_ko.mo"), _lang_pack_sha_value(b"", "dlpy_lang_ko.mo")],
              ["b" * 64, "a" * 64, None, "c" * 64, None])

        # Descarga desde languages/ de main: primero el SHA256SUMS, después el .mo.
        reset_ko()
        for filename in os.listdir(tmp):
            os.remove(os.path.join(tmp, filename))
        sha_text = (hashlib.sha256(valid).hexdigest() + "  dlpy_lang_ko.mo\n").encode("utf-8")
        requested = []
        def fake_bytes(url, timeout=5, limit=None):
            requested.append(url)
            return sha_text if url.endswith(LANG_SUMS) else valid
        g["fresh_bytes"] = fake_bytes
        downloaded = lang_pack_download("ko")
        loaded = lang_pack_load("ko")
        check("1.9.2: descarga valida SHA remoto e instala el catálogo",
              [downloaded, loaded, sorted(os.listdir(tmp)), requested,
               t_display("Cancelado.", lang="ko")],
              [True, True, ["dlpy_lang_ko.mo", "dlpy_lang_ko.mo.sha256"],
               [lang_pack_sha_url("ko"), lang_pack_url("ko")], "취소됨."])

        # Hash sin coincidencia o catálogo roto: nunca se instala.
        reset_ko()
        for filename in os.listdir(tmp):
            os.remove(os.path.join(tmp, filename))
        g["fresh_bytes"] = lambda url, timeout=5, limit=None: (b"0" * 64 if url.endswith(LANG_SUMS) else valid)
        bad_sha = (lang_pack_download("ko"), PACK_STATE["err"].get("ko"), os.listdir(tmp))
        g["fresh_bytes"] = lambda url, timeout=5, limit=None: None
        no_sha = (lang_pack_download("ko"), PACK_STATE["err"].get("ko"))
        check("1.9.2: hash remoto inválido o ausente no instala",
              [bad_sha, no_sha], [(False, "sha", []), (False, "sha")])

        # Comparte la frecuencia DLPY_UPDATES: compara SHA al vencer el intervalo y reutiliza el paquete entre comprobaciones.
        NO_UPDATES["on"] = False
        reset_ko()
        for filename in os.listdir(tmp):
            os.remove(os.path.join(tmp, filename))
        put(tmp, valid)
        same_requests = []
        def same_pack(url, timeout=5, limit=None):
            same_requests.append(url)
            return sha_text
        g["fresh_bytes"] = same_pack
        same_ok = lang_pack_sync("ko")
        first_request_count = len(same_requests)
        same_again = lang_pack_sync("ko")
        check("1.9.2: el paquete comparte DLPY_UPDATES y no consulta dos veces dentro del intervalo",
              [same_ok, same_again, first_request_count, len(same_requests), t_display("Cancelado.", lang="ko")],
              [True, True, 1, 1, "취소됨."])

        changed = _make_mo(revision="1.9.0", cancel="취소 완료.")
        changed_sha = (hashlib.sha256(changed).hexdigest() + "  dlpy_lang_ko.mo\n").encode("utf-8")
        g["UPDATE_HOURS"] = UPDATES_ALWAYS   # simulación de un nuevo ciclo del actualizador
        update_requests = []
        def changed_pack(url, timeout=5, limit=None):
            update_requests.append(url)
            return changed_sha if url.endswith(LANG_SUMS) else changed
        g["fresh_bytes"] = changed_pack
        changed_ok = lang_pack_sync("ko")
        check("1.9.2: si cambia el SHA, actualiza el catálogo sin cambiar VERSION",
              [changed_ok, update_requests, t_display("Cancelado.", lang="ko"), VERSION],
              [True, [lang_pack_sha_url("ko"), lang_pack_url("ko")], "취소 완료.", VERSION])

        # Sin red, un paquete local previamente validado sigue activo.
        g["UPDATE_HOURS"] = UPDATES_ALWAYS
        g["fresh_bytes"] = lambda url, timeout=5, limit=None: None
        offline_ok = lang_pack_sync("ko")
        check("1.9.2: sin red conserva el idioma local válido",
              [offline_ok, t_display("Cancelado.", lang="ko")], [True, "취소 완료."])

        # --noupdates no consulta el Release, pero permite leer el paquete local.
        reset_ko()
        NO_UPDATES["on"] = True
        loaded_offline = lang_ensure("ko")
        check("1.9.2: --noupdates usa el paquete local sin red",
              [loaded_offline, lang_effective("ko")], ["ko", "ko"])
    finally:
        os.environ.pop("DLPY_LANG_DIR", None)
        if saved_env is not None:
            os.environ["DLPY_LANG_DIR"] = saved_env
        NO_UPDATES["on"] = saved_no_updates
        g["CHECK_FILE"] = saved_check_file
        g["UPDATE_HOURS"] = saved_update_hours
        g["FILES_DIR"], g["INTERNAL_DIR"] = saved_files_dir, saved_internal_dir
        for name, function in saved_fns.items():
            g[name] = function
        reset_ko()
        for table, value in zip(tabs, saved_tabs):
            if value is not None:
                dict.__setitem__(table, "ko", value)
        if saved_translation is not None:
            LANG_TRANSLATIONS["ko"] = saved_translation
        if saved_loaded:
            PACK_STATE["loaded"].add("ko")
        if saved_tried:
            PACK_STATE["tried"].add("ko")
        if saved_warned:
            PACK_STATE["warned"].add("ko")
        if saved_err is not None:
            PACK_STATE["err"]["ko"] = saved_err
        if saved_missing is not None:
            PACK_STATE["missing"]["ko"] = saved_missing
        if saved_tpl is not None:
            _TPL_PACK["ko"] = saved_tpl
        if saved_rx is not None:
            _TPL_RX["ko"] = saved_rx
        shutil.rmtree(tmp, ignore_errors=True)

# ─────────── [T42] Franjas, diagnósticos y posición de la UX (1.9.2) ───────────
def _st_t42_franjas_contadores(check):
    """[T42] 1.9.2: franjas discretas, destello E/A, logs separados, migraciones y posición."""
    import contextlib
    import io
    import tempfile
    g = globals()
    saved = {
        "bar": BOTTOMBAR,
        "lang_id_mode": LANG_ID_MODE,
        "lang": LANG,
        "use_color": USE_COLOR,
        "truecolor": TRUECOLOR,
        "diag": diagnostic_snapshot(),
        "activity": dict(DIAGNOSTICS_ACTIVITY),
        "scene_on": SCENE.get("on"),
        "lang_code": SCENE.get("lang_code"),
        "lang_asset": SCENE.get("lang_asset"),
        "error_log": SHORTCUTMODE_LOG,
        "warning_log": WARNING_LOG_FILE,
        "logs_dir": LOGS_DIR,
        "files_dir": FILES_DIR,
        "internal_dir": INTERNAL_DIR,
        "changelog": CHANGELOG_FILE,
        "time": time.time,
    }
    tmp = tempfile.mkdtemp(prefix="dlpy_diag_192_")
    try:
        check("bottom bar: default apagado, 1/on = EAN (1.9.4) y secuencia EA/AE",
              [bottom_bar_parse(x) for x in ("0", "off", "", "1", "on", "EA", "AE", "e-a", "a,e", "EAE")],
              [(), (), (), ("E", "A", "N"), ("E", "A", "N"), ("E", "A"), ("A", "E"), ("E", "A"), ("A", "E"), ("E", "A")])
        check("bottom bar: --config acepta EA/AE y rechaza otras letras",
              [config_validate("DLPY_BOTTOMBAR", x) for x in ("0", "1", "EA", "ae", "E A", "xyz")],
              [(True, "0"), (True, "1"), (True, "EA"), (True, "AE"), (True, "EA"), (False, None)])
        cfg = {n: (v, d) for n, v, d in CONFIG_OPTIONS}
        check("idiomas: DLPY_LANG_IDS ofrece off/mark/id/both y queda apagado por defecto",
              (cfg.get("DLPY_LANG_IDS", (None, ""))[0],
               [config_validate("DLPY_LANG_IDS", x) for x in ("0", "mark", "id", "both", "xyz")],
               [lang_id_mode_parse(x) for x in ("0", "mark", "id", "both")]),
              ("0", [(True, "0"), (True, "mark"), (True, "id"), (True, "both"), (False, None)],
               ["off", "mark", "id", "both"]))
        _mode_before = LANG_ID_MODE
        _color_before, _truecolor_before = USE_COLOR, TRUECOLOR
        g["USE_COLOR"], g["TRUECOLOR"] = True, True
        g["LANG_ID_MODE"] = "off"
        _plain_debug = lang_debug_output("Preparing", "Preparando")
        g["LANG_ID_MODE"] = "mark"
        _mark_debug = lang_debug_output("Preparing", "Preparando")
        g["LANG_ID_MODE"] = "id"
        _id_debug = lang_debug_output("Preparing", "Preparando")
        g["LANG_ID_MODE"] = "both"
        _both_debug = lang_debug_output("Preparing", "Preparando")
        _mark_cells = {}
        _mark_width = put_text(_mark_cells, 0, 0, _mark_debug, SCENE_DIM)
        g["LANG_ID_MODE"] = "mark"
        # texto que ya trae color: el color se reaplica tras cada reinicio
        _mark_nested = lang_debug_output(paint("A", "mint") + "b", "x")
        _old_lang = LANG
        g["LANG"] = "es"
        g["LANG_ID_MODE"] = "id"
        _actual_id = t_display("Preparando")
        g["LANG"] = _old_lang
        check("idiomas: mark colorea el propio texto (sin símbolos ni ancho extra); id muestra solo el msgid en plano; both solo el msgid, coloreado",
              (_ANSI_RE.sub("", _plain_debug), _ANSI_RE.sub("", _mark_debug), _id_debug,
               _ANSI_RE.sub("", _both_debug), dwidth(_mark_debug),
               text_cells(_mark_debug)[0][1], _mark_width, _mark_cells.get((0, 0), (None, None))[1], _actual_id,
               _mark_debug != "Preparing", "◆" in _mark_debug, _ANSI_RE.sub("", _mark_nested)),
              ("Preparing", "Preparing", "Preparando", "Preparando",
               dwidth("Preparing"), "P", dwidth("Preparing"), LANG_MARK_RGB, "Preparando",
               True, False, "Ab"))
        check("idiomas: both = solo el msgid coloreado (ANSI en la terminal); id = solo el msgid sin color",
              (_both_debug.startswith("\x1b["), _both_debug.endswith(RESET), _ANSI_RE.sub("", _both_debug), "\x1b" in _id_debug),
              (True, True, "Preparando", False))
        check("idiomas: con id/both la tecla Enter sale como msgid (Enter), con mark sigue en el idioma (Entrée)",
              ((g.__setitem__("LANG_ID_MODE", "id"), ux_enter_key("fr"))[1], (g.__setitem__("LANG_ID_MODE", "both"), ux_enter_key("it"))[1],
               (g.__setitem__("LANG_ID_MODE", "mark"), ux_enter_key("fr"))[1]),
              ("Enter", "Enter", "Entrée"))
        check("idiomas: los JSON del atajo salen sin códigos de color con mark (menús de --scm/--scb sin «opción fuera del dominio»)",
              (json_clean({_mark_debug: [_mark_debug, {"k": _mark_debug}], "n": 3}), "\x1b" in json.dumps(json_clean(languages_payload()))),
              ({"Preparing": ["Preparing", {"k": "Preparing"}], "n": 3}, False))
        g["LANG_ID_MODE"] = "mark"
        _wrapped = wrap_text(lang_debug_output("uno dos tres cuatro", "x"), 10)
        _clip = clip_text(lang_debug_output("uno dos tres", "x"), 5)
        _chip_old = dict(_UX_CHIP_CACHE)
        _UX_CHIP_CACHE.clear()
        _chip = ux_chip("webm")
        _UX_CHIP_CACHE.clear()
        check("idiomas: con mark el color sobrevive a wrap_text, clip_text, fit_text, ux_chip y MAYÚSCULAS (sin basura «38;2…» en la escena)",
              ([_ANSI_RE.sub("", x) for x in _wrapped], all(x.startswith("\x1b[") and x.endswith(RESET) for x in _wrapped),
               _ANSI_RE.sub("", _clip), _clip.endswith(RESET), _ANSI_RE.sub("", fit_text(lang_debug_output("uno dos tres", "x"), 6)),
               _ANSI_RE.sub("", _chip), _chip.startswith("\x1b["), ansi_upper(paint("ab", "mint")) == paint("AB", "mint")),
              (["uno dos", "tres", "cuatro"], True, "uno d", True, "uno d…", "WEBM", True, True))
        _UX_CHIP_CACHE.update(_chip_old)
        _was_on, _marked_before = SCENE.get("on"), dict(MARKED_TEXT)
        SCENE["on"] = True
        MARKED_TEXT.clear()
        _scene_txt = lang_debug_output("Download vorbereiten", "Preparando descarga")
        _row = {(x, 3): (ch, (1, 2, 3), None) for x, ch in enumerate("Download vorbereiten · 42%", start=5)}
        # en otra fila no cuenta como frase propia salvo que coincida
        _row.update({(x, 4): (ch, (1, 2, 3), None) for x, ch in enumerate("Download", start=5)})
        # «Downloads» no es la palabra «Download»
        _row.update({(x, 6): (ch, (1, 2, 3), None) for x, ch in enumerate("Downloads", start=5)})
        _painted = lang_mark_cells(_row)
        _cols = lambda y: {c[0] for (xx, yy), c in _painted.items() if yy == y and c[0] != " " for c in [c]} and sorted({_painted[k][1] for k in _painted if k[1] == y})
        check("idiomas: en la escena el texto queda plano (sin ANSI) y mark lo colorea al pintar, por palabras completas y sin cambiar el texto",
              (_scene_txt, _cols(3), _cols(6), "".join(_painted[(x, 3)][0] for x in range(5, 31))),
              ("Download vorbereiten", [LANG_MARK_RGB, (1, 2, 3)], [(1, 2, 3)], "Download vorbereiten · 42%"))
        g["LANG_ID_MODE"] = "both"
        MARKED_TEXT.clear()
        _both_txt = lang_debug_output("Warten", "Espera")
        _brow = {(x, 3): (ch, (1, 2, 3), None) for x, ch in enumerate(_both_txt, start=5)}
        _bp = lang_mark_cells(_brow)
        check("idiomas: both en la escena muestra solo el msgid y lo colorea; id muestra solo el msgid sin color",
              (_both_txt, {_bp[k][1] for k in _bp if _bp[k][0] != " "}, (g.__setitem__("LANG_ID_MODE", "id"), MARKED_TEXT.clear(), lang_debug_output("Warten", "Espera"))[2],
               (lambda _ip: {_ip[k][1] for k in _ip if _ip[k][0] != " "})(lang_mark_cells({(x, 3): (ch, (1, 2, 3), None) for x, ch in enumerate("Espera", start=5)}))),
              ("Espera", {LANG_MARK_RGB}, "Espera", {(1, 2, 3)}))
        g["LANG_ID_MODE"] = "mark"
        SCENE["on"] = _was_on
        MARKED_TEXT.clear()
        MARKED_TEXT.update(_marked_before)
        _pk_before = (set(PACK_STATE["tried"]), set(PACK_STATE["loaded"]))
        _lit = []
        for _m in ("id", "both"):
            g["LANG_ID_MODE"] = _m
            _lit.append((lang_effective("fr"), lang_pack_load("fr"), lang_pack_sync("fr", force=True), lang_pack_download("fr"), lang_ensure("fr"),
                         t_display("Comprobando pip", lang="fr", _debug=False), tr("Descargando", lang="de", _debug=False),
                         trn("archivo", "archivos", 2, lang="ja", _debug=False)))
        PACK_STATE["tried"], PACK_STATE["loaded"] = _pk_before[0], _pk_before[1]
        check("idiomas: id/both no usan catálogos: sin carga, sin descarga y todo sale como msgid (español del py)",
              _lit, [("es", False, False, False, "es", "Comprobando pip", "Descargando", "archivos")] * 2)
        g["LANG_ID_MODE"] = _mode_before
        g["USE_COLOR"], g["TRUECOLOR"] = _color_before, _truecolor_before
        check("bottom bar: opción activada por defecto (1)",
              (cfg.get("DLPY_BOTTOMBAR", (None, ""))[0], "E" in cfg.get("DLPY_BOTTOMBAR", (None, ""))[1], "A" in cfg.get("DLPY_BOTTOMBAR", (None, ""))[1]),
              ("1", True, True))

        with DIAGNOSTICS_LOCK:
            DIAGNOSTICS.update(E=2, A=5)
            DIAGNOSTICS_ACTIVITY.update(E=0.0, A=0.0)
        g["BOTTOMBAR"] = ("E", "A")
        ea = bottom_bar_line()
        g["BOTTOMBAR"] = ("A", "E")
        ae = bottom_bar_line()
        cells = scene_bottom_bar_cells(40, 18)
        same_style = cells == scene_topbar_cells(40, bottom_bar_line(width=36), row=18, highlights={g_: (net_level() if k_ == "N" else diagnostic_level(k_)) for k_, g_ in BOTTOMBAR_GLYPHS.items() if k_ in ("E", "A")})
        check("bottom bar: gris discreto como topbar, orden correcto y márgenes seguros",
              (ea, ae, {y for _x, y in cells}, min((x for x, _y in cells), default=0) >= 2,
               max((x for x, _y in cells), default=0) <= 39, same_style),
              ("✕  ·  !", "!  ·  ✕", {18}, True, True, True))
        check("UX: topbar centrado en la fila 2 y protegido por una fila libre arriba",
              (set(y for _x, y in scene_topbar_cells(40, "iPhone  ·  v1.9.2", row=2)),
               min(x for x, _y in scene_topbar_cells(40, "iPhone  ·  v1.9.2", row=2)) >= 2,
               max(x for x, _y in scene_topbar_cells(40, "iPhone  ·  v1.9.2", row=2)) <= 39),
              ({2}, True, True))
        check("UX: bottom bar deja aire bajo estado normal, aviso y pregunta",
              (scene_bottom_bar_row(3, False), scene_bottom_bar_row(3, True),
               scene_bottom_bar_row(3, True) - (3 + SCENE_STATUS_ROW + 1),
               3 + SCENE_STATUS_ROW + 3),
              (3 + SCENE_STATUS_ROW + 2, 3 + SCENE_STATUS_ROW + 3, 2, 3 + SCENE_STATUS_ROW + 3))
        check("bottom bar: ajuste de anchura conserva E antes que A; sin cifras aunque haya eventos",
              (bottom_bar_line(width=3), any(ch.isdigit() for ch in ea + ae)), ("✕", False))

        # Reloj fijo: el icono que recibe el evento se enciende y vuelve a su gris; el otro no cambia.
        fake_now = {"t": 100.0}
        g["time"].time = lambda: fake_now["t"]
        with DIAGNOSTICS_LOCK:
            DIAGNOSTICS.update(E=0, A=0)
            DIAGNOSTICS_ACTIVITY.update(E=0.0, A=0.0)
        g["BOTTOMBAR"] = ("E", "A")
        idle = scene_bottom_bar_cells(40, 18)
        diagnostic_increment("E", now=100.0)
        lit = scene_bottom_bar_cells(40, 18)
        fake_now["t"] = 100.0 + DIAG_HOLD - DIAG_FADE / 2.0
        fading = scene_bottom_bar_cells(40, 18)
        fake_now["t"] = 100.0 + DIAG_HOLD + 0.01
        returned = scene_bottom_bar_cells(40, 18)
        _icons = lambda cs: {v[0]: v[1] for v in cs.values() if v[0] in ("✕", "!")}
        check("bottom bar: E se ilumina blanco, A permanece gris y E vuelve suavemente a gris",
              (_icons(idle), _icons(lit), _icons(fading), _icons(returned), set(idle) == set(lit) == set(fading) == set(returned)),
              ({"✕": SCENE_DIM, "!": SCENE_DIM}, {"✕": SCENE_WHITE, "!": SCENE_DIM},
               {"✕": mix6(SCENE_DIM, SCENE_WHITE, 0.5), "!": SCENE_DIM},
               {"✕": SCENE_DIM, "!": SCENE_DIM}, True))
        diagnostic_increment("A", now=100.0)
        check("bottom bar: A también recibe su propio destello independiente", diagnostic_level("A", 100.0), 1.0)
        check("diagnóstico: incrementos independientes y protegidos",
              (diagnostic_increment("E", now=101.0), diagnostic_increment("A", now=101.0), diagnostic_snapshot()),
              (2, 2, {"E": 2, "A": 2}))

        # Los mensajes normales generan dos archivos distintos con el texto completo.
        g["SHORTCUTMODE_LOG"] = os.path.join(tmp, "internal", "logs", "errors.log")
        g["WARNING_LOG_FILE"] = os.path.join(tmp, "internal", "logs", "warnings.log")
        g["SCENE"]["on"] = False
        with DIAGNOSTICS_LOCK:
            DIAGNOSTICS.update(E=0, A=0)
            DIAGNOSTICS_ACTIVITY.update(E=0.0, A=0.0)
        with contextlib.redirect_stdout(io.StringIO()):
            m_warn("Advertencia de prueba para el log")
            m_err("Error de prueba para el log")
        with open(SHORTCUTMODE_LOG, "r", encoding="utf-8") as fh:
            error_text = fh.read()
        with open(WARNING_LOG_FILE, "r", encoding="utf-8") as fh:
            warning_text = fh.read()
        check("diagnóstico: errores y advertencias quedan separados y legibles en internal/logs",
              (diagnostic_snapshot(), "[ERROR] Error de prueba para el log" in error_text,
               "[WARNING] Advertencia de prueba para el log" in warning_text,
               "Advertencia de prueba" not in error_text, "Error de prueba" not in warning_text,
               os.path.basename(os.path.dirname(SHORTCUTMODE_LOG))),
              ({"E": 1, "A": 1}, True, True, True, True, "logs"))

        g["FILES_DIR"] = os.path.join(tmp, "logs_dir", "dlpy_files")
        g["INTERNAL_DIR"] = os.path.join(g["FILES_DIR"], "dlpy_internal")
        g["LOGS_DIR"] = os.path.join(g["INTERNAL_DIR"], "logs")
        check("ensure_internal_logs crea internal/logs", (ensure_internal_logs(), os.path.isdir(g["LOGS_DIR"])), (True, True))


        # 1.9.2: un solo punto (diagnostic_report) cuenta y registra; m_err/m_warn no cuentan doble; Enter vacío no es aviso, una opción inválida sí.
        with DIAGNOSTICS_LOCK:
            DIAGNOSTICS.update(E=0, A=0)
            DIAGNOSTICS_ACTIVITY.update(E=0.0, A=0.0)
        with contextlib.redirect_stdout(io.StringIO()):
            m_err("fallo de prueba")
            m_warn("aviso de prueba")
        _after_say = diagnostic_snapshot()
        retry_prompt("▸ ", "")
        _after_empty = diagnostic_snapshot()
        retry_prompt("▸ ", "zz")
        _after_bad = diagnostic_snapshot()
        diagnostic_report("E", "otro")
        check("diagnóstico: m_err/m_warn cuentan una vez, Enter vacío no avisa, opción inválida sí, diagnostic_report cuenta",
              (_after_say, _after_empty, _after_bad, diagnostic_snapshot(), diagnostic_report("X", "no")),
              ({"E": 1, "A": 1}, {"E": 1, "A": 1}, {"E": 1, "A": 2}, {"E": 2, "A": 2}, 0))
        check("diagnóstico: estados de fallo de la escena y excepciones sin capturar quedan cubiertos",
              (_dlpy_state("No se pudo instalar yt-dlp"), _dlpy_state("Error: x"), callable(sys.excepthook),
               sys.excepthook.__name__ == "_sys_hook"),
              ("fail", "fail", True, True))
        check("bottom bar: apagada no pinta celdas",
              (g.__setitem__("BOTTOMBAR", ()), bottom_bar_cells(40, 18)), (None, {}))

        SCENE["lang_code"] = "ja"
        SCENE["lang_asset"] = "sha256"
        name_check, command_check = _dlpy_topic("Comprobando idioma 日本語")
        SCENE["lang_asset"] = "mo"
        name, command = _dlpy_topic("Descargando idioma 日本語")
        check("D L P Y: revisar y descargar idioma muestran los GET reales con el mismo contexto",
              (_dlpy_ctx("Comprobando idioma 日本語"), name_check, command_check, _dlpy_state("Comprobando idioma 日本語"),
               name, command, _dlpy_state("Descargando idioma 日本語"),
               _dlpy_state("Descargando idioma 日本語 · 言語設定済み"), _dlpy_state("Error: Language")),
              ("language", "Idioma", "GET raw.githubusercontent.com/ElDelDLpy/DLpy/main/languages/SHA256SUMS", "run",
               "Idioma", "GET raw.githubusercontent.com/ElDelDLpy/DLpy/main/languages/dlpy_lang_ja.mo", "run", "ok", "fail"))
    finally:
        g["BOTTOMBAR"] = saved["bar"]
        g["LANG_ID_MODE"] = saved["lang_id_mode"]
        g["LANG"] = saved["lang"]
        g["USE_COLOR"] = saved["use_color"]
        g["TRUECOLOR"] = saved["truecolor"]
        g["SHORTCUTMODE_LOG"] = saved["error_log"]
        g["WARNING_LOG_FILE"] = saved["warning_log"]
        g["LOGS_DIR"] = saved["logs_dir"]
        g["FILES_DIR"] = saved["files_dir"]
        g["INTERNAL_DIR"] = saved["internal_dir"]
        g["CHANGELOG_FILE"] = saved["changelog"]
        g["time"].time = saved["time"]
        SCENE["on"] = saved["scene_on"]
        with DIAGNOSTICS_LOCK:
            DIAGNOSTICS.clear()
            DIAGNOSTICS.update(saved["diag"])
            DIAGNOSTICS_ACTIVITY.clear()
            DIAGNOSTICS_ACTIVITY.update(saved["activity"])
        if saved["lang_code"] is None:
            SCENE.pop("lang_code", None)
        else:
            SCENE["lang_code"] = saved["lang_code"]
        if saved["lang_asset"] is None:
            SCENE.pop("lang_asset", None)
        else:
            SCENE["lang_asset"] = saved["lang_asset"]
        shutil.rmtree(tmp, ignore_errors=True)


def _st_t43_limpieza_codigo(check):
    """[T43] 1.9.3: sin llamadas a softclear() (no existe), sin código muerto y VERSION fija en 1.9.3."""
    import inspect
    check("T43 VERSION con formato X.Y.Z", bool(re.fullmatch(r"\d+\.\d+\.\d+", VERSION)), True)
    for fn in (config_redraw, config_interactive):
        src = inspect.getsource(fn)
        check("T43 %s no llama a softclear()" % fn.__name__, "softclear(" in src, False)
        check("T43 %s limpia con clear_screen()" % fn.__name__, "clear_screen()" in src, True)
    check("T43 softclear sigue sin existir (nadie debe volver a llamarlo)", "softclear" in globals(), False)
    check("T43 _t_segment eliminada", "_t_segment" in globals(), False)
    check("T43 ux_saved eliminada", "ux_saved" in globals(), False)


def _st_t44_pines_y_errores(check):
    """[T44] 1.9.3: excepciones de red acotadas en la descarga y la sincronización de catálogos."""
    import tempfile
    g = globals()
    saved = {"fresh": fresh_bytes, "check_file": CHECK_FILE, "dir": os.environ.get("DLPY_LANG_DIR"),
             "err": dict(PACK_STATE["err"]), "tried": set(PACK_STATE["tried"]), "warned": set(PACK_STATE["warned"])}
    tmp = tempfile.mkdtemp()
    try:
        os.environ["DLPY_LANG_DIR"] = tmp
        g["CHECK_FILE"] = os.path.join(tmp, "check.json")
        PACK_STATE["warned"].add("ko")                      # sin avisos reales en la prueba

        def boom_os(url, timeout=5, limit=None):
            raise OSError("sin red")
        g["fresh_bytes"] = boom_os
        check("T44 descarga: un error de red (OSError) sigue siendo «red»",
              [lang_pack_download("ko"), PACK_STATE["err"].get("ko")], [False, "red"])
        check("T44 sync: un error de red no rompe y no deja nada escrito",
              [lang_pack_sync("ko", force=True), os.listdir(tmp)], [False, []])

        def boom_bug(url, timeout=5, limit=None):
            raise RuntimeError("bug")
        g["fresh_bytes"] = boom_bug
        try:
            lang_pack_download("ko")
            propagated = False
        except RuntimeError:
            propagated = True
        check("T44 descarga: un error inesperado ya no se traga en silencio", propagated, True)
        nl = ash_quote_forms("/a/it's\nnl.mp4")
        check("T44 ash_quote: apóstrofo + salto de línea no usa «\\\\\\n» (continuación de línea); una sola forma",
              [len(nl), "\\\n" in nl[0]], [1, False])
        check("T44 ash_quote: apóstrofo sin caracteres de control conserva sus dos formas",
              len(ash_quote_forms("/a/it's.mp4")), 2)
    finally:
        g["fresh_bytes"], g["CHECK_FILE"] = saved["fresh"], saved["check_file"]
        if saved["dir"] is None:
            os.environ.pop("DLPY_LANG_DIR", None)
        else:
            os.environ["DLPY_LANG_DIR"] = saved["dir"]
        for key in ("err", "tried", "warned"):
            PACK_STATE[key].clear()
            PACK_STATE[key].update(saved[key])
        shutil.rmtree(tmp, ignore_errors=True)


def _st_t45_nombres_indefinidos(check):
    """[T45] 1.9.3: análisis estático del propio script: ningún nombre usado sin definir (habría detectado una llamada a una función inexistente) ni función sin uso."""
    import ast
    import builtins
    try:
        with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
            src = fh.read()
        # 2.0.2: la autoprueba vive en modules/: se analiza junto con dlpy.py (un nombre que solo usan las pruebas sigue contando como usado)
        src += "\n" + (selftest_module_text()[0] or "")
        tree = ast.parse(src)
    except (OSError, SyntaxError, ValueError) as e:
        ignore("selftest_t45", e)
        return
    defined = set(dir(builtins)) | {"__file__"}
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(n.name)
        elif isinstance(n, ast.Import):
            defined.update((a.asname or a.name).split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom):
            defined.update(a.asname or a.name for a in n.names)
        elif isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            defined.add(n.id)
        elif isinstance(n, ast.arg):
            defined.add(n.arg)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            defined.add(n.name)
        elif isinstance(n, ast.Global):
            defined.update(n.names)
    undefined = sorted({n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)} - defined)
    check("T45 ningún nombre usado sin definir en el script", undefined, [])
    # API del motor de idiomas (tr / trc / trf / trn): se conserva aunque hoy nadie la llame
    api_sin_uso = {"trf"}
    unused = sorted(n.name for n in tree.body if isinstance(n, ast.FunctionDef) and n.name not in api_sin_uso
                    and len(re.findall(r"\b%s\b" % re.escape(n.name), src)) == 1)
    check("T45 ninguna función de nivel superior sin una sola referencia", unused, [])


def _st_t46_mensajes_traducibles(check):
    """[T46] 1.9.4: cada mensaje literal de m_* / note / hint / confirm_install tiene traducción (antes ~70 salían en español en todos los idiomas sin que nadie lo notara)."""
    import ast
    try:
        with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
    except (OSError, SyntaxError, ValueError) as e:
        ignore("selftest_t46", e)
        return
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node

    def inside_test(node):
        while node in parents:
            node = parents[node]
            if isinstance(node, ast.FunctionDef):
                return node.name.startswith("_st_")
        return False

    def sample(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.JoinedStr):
            return "".join(v.value if isinstance(v, ast.Constant) else "X" for v in node.values)
        return None
    sinks = {"m_ok": t_status, "m_warn": t_status, "m_info": t_status, "m_err": t_status, "m_check": t_status,
             "note": t_display, "hint": t_display, "legend_note": t_display, "confirm_install": t_display}
    finite = {"Sin respuesta: se elige X."}                # el hueco solo vale Sí / No y ambas frases existen exactas
    missing = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in sinks and node.args and not inside_test(node):
            text = sample(node.args[0])
            if text is None or text in finite or not any(c.isalpha() for c in text):
                continue
            if sinks[node.func.id](text, lang="en") == text and text not in missing:
                missing.append(text)
    check("T46 mensajes literales sin traducción (añade plantilla en _TPL_ROWS o clave en I18N)", sorted(missing), [])


def _st_t47_plantillas_y_cobertura(check):
    """[T47] 1.9.4: plantillas más específicas primero, huecos recursivos, ayudas por piezas con llaves y cobertura de los catálogos instalados."""
    en = lambda text: t_display(text, lang="en", _debug=False)
    check("T47 plantilla con huecos recursivos (frase fija dentro del hueco)",
          en("A 8 bits: SDR, pero pierde precisión de color. Puede verse con bandas en cielos y degradados."),
          "At 8 bits: SDR, but color precision is lost. Banding may be visible in skies and gradients.")
    check("T47 hueco recursivo con otra plantilla dentro",
          en("A 8 bits: más rápido, pero pierde precisión de color. Puede verse con bandas; el HDR10 se pasa a SDR con tone mapping (tarda ~3 veces más) y pierde el brillo extra del HDR."),
          "At 8 bits: faster, but color precision is lost. Banding may be visible; HDR10 is converted to SDR with tone mapping (takes ~3 times longer) and loses the extra HDR brightness.")
    check("T47 detalle de idioma traducido dentro de «Idioma {0}: {1}»",
          en("Idioma Italiano: no se pudo descargar; se usará inglés."), "Language Italiano: could not download; English will be used.")
    check("T47 el nombre del idioma (dato) no se toca",
          en("Idioma Español: falló la descarga; se usará inglés."), "Language Español: download failed; English will be used.")
    check("T47 la plantilla más específica gana: «Instalar la {0}» no se come a las largas",
          [en("Instalar la 1.9.4"), en("Instalar la 1.9.4 para la próxima vez"), en("Instalar la 1.9.4 y ejecutarla ahora")],
          ["Install 1.9.4", "Install 1.9.4 for next time", "Install 1.9.4 and run it now"])
    check("T47 el punto final se conserva", [en("Descartadas: 3."), en("Descartadas: 3")], ["Discarded: 3.", "Discarded: 3"])
    check("T47 ayudas con llaves de énfasis: cada pieza se traduce y las llaves se conservan",
          [en("T todas · n.º (1 3 · 1-3) · D n.º descartar · {Enter = ninguna}"), en("Opción 1-3 · {Enter = 2}"),
           en("{Enter = convertir} · r = solo remux · 8 s"), en("n.º · m más · {Enter = original}"),
           en("¿Instalar alguna? n.º · m más · {Enter = no}"), en("n.º separados por espacio (ej. 1 2 4) · m más · {Enter = todas}")],
          ["T all · # (1 3 · 1-3) · D # discard · {Enter = none}", "Option 1-3 · {Enter = 2}",
           "{Enter = convert} · r = remux only · 8 s", "# · m more · {Enter = original}",
           "Install any? # · m more · {Enter = no}", "numbers separated by spaces (e.g. 1 2 4) · m more · {Enter = all}"])
    check("T47 lo desconocido no se toca (títulos con « · » y llaves ajenas)",
          [en("Mi video · parte 2"), en("{abc}"), en("{Enter = quizá} · otra cosa")], ["Mi video · parte 2", "{abc}", "{Enter = quizá} · otra cosa"])
    nested_ok = all(n < len(re.findall(r"\{\d\}", es)) for es, idx in _TPL_NESTED.items() for n in idx)
    check("T47 _TPL_NESTED apunta a huecos que existen y a plantillas declaradas",
          [nested_ok, [es for es in _TPL_NESTED if es not in {row[0] for row in _TPL_ROWS}]], [True, []])
    stale = []
    for code in PACK_LANGS:
        try:
            loaded = lang_pack_load(code)
        except Exception as e:                          # un catálogo roto no debe tumbar la prueba: se informa abajo
            ignore("selftest_t47", e)
            loaded = False
        if loaded and code in LANG_TRANSLATIONS:
            gaps = lang_pack_coverage(LANG_TRANSLATIONS[code])
            if gaps:
                stale.append((code, len(gaps)))
    check("T47 los catálogos instalados traen todas las claves del script (si falla: publicar/actualizar los .mo de la revisión 1.9.4)", stale, [])


def _st_t48_fluidez(check):
    """[T48] ── 1.9.8: reloj único de cuadros, ritmo por límite de cuadro, repintado rotativo y marco de video continuo ──"""
    check("fluidez 1.9.8: un solo reloj (sitio, video/audio, conversión ligera y DLPY) y la conversión en marcha, más ligera",
          (SITE_FPS == CONV_FPS == DLPY_FPS == MOTIF_FPS == ANIM_FPS, CONV_RUN_FPS < ANIM_FPS, NOISE_FPS < ANIM_FPS), (True, True, True))
    gaps = [frame_gap(t_, 30) for t_ in (0.0, 0.01, 1.0 / 30, 0.5, 1.2345, 7.0 / 30 - 1e-12)]
    check("fluidez 1.9.8: frame_gap queda entre 0,5 ms y un cuadro", all(0.0005 <= g_ <= 1.0 / 30 + 1e-9 for g_ in gaps), True)
    check("fluidez 1.9.8: frame_gap lleva justo al siguiente límite de cuadro (no a medio cuadro)",
          (round(frame_gap(0.0, 30), 6), round(frame_gap(0.01, 30), 6), round(frame_gap(1.0 / 30 + 0.02, 30), 6)),
          (round(1.0 / 30, 6), round(1.0 / 30 - 0.01, 6), round(1.0 / 30 - 0.02, 6)))
    st_ = {"rows": {y_: "x" for y_ in range(1, 25)}}
    sizes, done_ = [], 0
    while st_["rows"] and done_ < 40:
        sizes.append(len(st_["rows"]))
        scene_refresh_slice(st_, 24, 30)
        done_ += 1
    check("fluidez 1.9.8: el repintado rotativo no borra todo de golpe y cubre todas las filas en ~0,35 s",
          (sizes[0] - sizes[1] < 24, done_ <= int(math.ceil(0.35 * 30)) + 1, not st_["rows"]), (True, True, True))
    st2_ = {"rows": {}}
    seen_ = set()
    for _i in range(12):
        before_ = {y_: "x" for y_ in range(1, 25)}
        st2_["rows"] = dict(before_)
        scene_refresh_slice(st2_, 24, 30)
        seen_ |= set(before_) - set(st2_["rows"])
    check("fluidez 1.9.8: la rotación recorre todas las filas sin salirse del rango", (len(seen_), min(seen_), max(seen_)), (24, 1, 24))
    # 1.9.8: el envío final no es D L P Y (solo arranque y actualizaciones): título del video y dibujo de envío
    old_s = dict(SCENE)
    try:
        SCENE.update(on=True, brand=False, err_brand=False, last_error=None, title_raw="Mi video", label="Guardado", pct=None, label_wall=None, welcome=None, ask=None, conv=None, th=None)
        lbl_ = send_label(False)
        kinds_ = (scene_motif_kind(dict(SCENE, label="Guardado", brand=True)), scene_motif_kind(dict(SCENE, label=lbl_, brand=True)),
                  scene_motif_kind(dict(SCENE, label=lbl_, brand=False)), scene_motif_kind(dict(SCENE, label=send_label(True), brand=False)))
        scene_status(lbl_, frac=1.0)
        after_ = (SCENE["brand"], SCENE["label"], scene_motif_kind(SCENE), scene_title_spec(SCENE)[0] != "grad")
    finally:
        SCENE.clear()
        SCENE.update(old_s)
    check("fluidez 1.9.8: D L P Y sigue siendo el dibujo del arranque y las actualizaciones; el envío y «Abriendo con view» son el dibujo de envío",
          kinds_, ("dlpy", "send", "send", "send"))
    check("fluidez 1.9.8: al enviar no se enciende D L P Y (el título no es el degradado de la marca) y el centro es el envío", after_, (False, lbl_, "send", True))
    # 1.9.8: con otro idioma el texto de envío ya traducido no coincidía con «Enviando…» y el centro caía en D L P Y: la escena guarda la clave y traduce al pintar
    lang0_ = globals().get("LANG")
    try:
        globals()["LANG"] = "en"
        en_ = (send_key(False), send_key(True), [scene_motif_kind({"label": x_}) for x_ in (send_key(False), send_key(True), scene_pp_text("FFmpegMerger"),
               scene_pp_text("AppleConvert"))], t_status(send_key(False)), t_status(send_key(True)))
    finally:
        globals()["LANG"] = lang0_
    check("fluidez 1.9.8: con la interfaz en inglés el envío, la unión y la conversión siguen siendo su dibujo (la escena guarda claves)",
          (en_[0], en_[1], en_[2], en_[3], en_[4]),
          ("Enviando a " + SHORTCUT_NAME, "Abriendo con view", ["send", "send", "rail", None], "Sending to " + SHORTCUT_NAME, "Opening with view"))
    ks_ = [i / 20.0 for i in range(21)]
    check("fluidez 1.9.8: outro_ease tiene extremos fijos, no baja nunca y acota lo que se sale",
          (outro_ease(0.0), outro_ease(1.0), outro_ease(-2.0), outro_ease(3.0), all(outro_ease(b_) >= outro_ease(a_) for a_, b_ in zip(ks_, ks_[1:]))),
          (0.0, 1.0, 0.0, 1.0, True))
    A_, B_ = (255, 0, 0), (0, 0, 255)
    check("fluidez 1.9.8: el marco de video se mueve entre cuadros contiguos (ya no a escalones de 12 cuadros)",
          site_video_cells(10, 4, 18, A_, B_, 3.0, 1.0) != site_video_cells(10, 4, 18, A_, B_, 3.0 + 1.0 / ANIM_FPS, 1.0), True)
    check("fluidez 1.9.8: el ruido de la etiqueta conserva su parpadeo propio (mismo paso de ruido, mismo texto)",
          badge_cells(20, 3, "1080p", 0.0, 3.0, A_, B_) == badge_cells(20, 3, "1080p", 0.0, 3.0 + 0.4 / NOISE_FPS, A_, B_), True)


def _st_t49_sc_lista(check):
    """[T49] ── 1.9.9: DLPY_SAFE_LIST: --scm / --scb listan directo (lista normal o completa); apagado no cambia nada ──"""
    url = "https://a.b/c"
    check("sc_list 1.9.9: valores de DLPY_SAFE_LIST (vacío y raros = apagado)",
          [sc_list_mode(v_) for v_ in ("", "0", "off", "zzz", "1", "on", "Sí", "all", "FULL")], ["", "", "", "", "short", "short", "short", "all", "all"])
    check("sc_list 1.9.9: apagado deja --scm y --scb tal cual",
          (sc_list_args(["--scm", url], mode=""), sc_list_args(["--scb", url], mode="")), (["--scm", url], ["--scb", url]))
    check("sc_list 1.9.9: --scb pasa al flujo de --shortcutpick sin valores (lista normal); --scm no se toca",
          (sc_list_args(["--scb", url], mode="short"), sc_list_args([url, "--scb"], mode="short"), sc_list_args(["--scm", url], mode="short")),
          ([url, "--shortcutpick="], [url, "--shortcutpick="], ["--scm", url]))
    _j = sc_list_scm_json(url)
    check("sc_list 1.9.9: --scm responde al instante use_scb (ok false, sin analizar) y serializa a ASCII",
          (_j["use_scb"], _j["ok"], _j["error_code"], _j["link"], json.loads(json.dumps(_j, ensure_ascii=True))["use_scb"]), (True, False, "sc_list", url, True))
    check("sc_list 1.9.9: con «all» abre la lista completa (v=more)", sc_list_args(["--scb", url], mode="all"), [url, "--shortcutpick=v=more"])
    check("sc_list 1.9.9: raya larga del teclado de iOS y --scb=NOMBRE", (sc_list_args(["\u2014scb", url], mode="short"), sc_list_args(["--scb=DLpy", url], mode="short")),
          ([url, "--shortcutpick="], [url, "--shortcutpick="]))
    check("sc_list 1.9.9: sin --scm/--scb (o con --shortcutpick ya puesto) no toca nada",
          (sc_list_args([url], mode="short"), sc_list_args(["--scb", "--shortcutpick", "v=1", url], mode="short"), sc_list_args(["--shortcutclip"], mode="all")),
          ([url], ["--shortcutpick", "v=1", url], ["--shortcutclip"]))
    cf_, pos_ = parse_cli(sc_list_args(["--scb", url], mode="short"))
    cf2_, pos2_ = parse_cli(sc_list_args(["--scb", url], mode="all"))
    check("sc_list 1.9.9: lo reencaminado lo entiende parse_cli como --shortcutpick (vacío / v=more) y el enlace queda como posicional",
          (cf_, pos_, cf2_, pos2_, parse_shortcut_pick(cf_.get("shortcutpick")), parse_shortcut_pick(cf2_.get("shortcutpick"))["v"] in SC_MORE_IDS, wants_scm(["--shortcutpick="])),
          ({"shortcutpick": ""}, [url], {"shortcutpick": "v=more"}, [url], None, True, False))
    t_ = time.monotonic()
    frame_wait(t_, 30)
    check("fluidez: frame_wait duerme como mucho un cuadro (antes solo lo nombraba el changelog de la 1.9.8)", 0.0 <= time.monotonic() - t_ < 0.2, True)
    _ra = video_row(1, {"format_id": "1", "ext": "mp4", "vcodec": "avc1", "acodec": "none", "height": 1080})
    _ru = video_row(2, {"format_id": "2", "ext": "mp4", "vcodec": "unknown", "acodec": "unknown", "height": 720})
    _rn = video_row(3, {"format_id": "3", "ext": "webm", "vcodec": "vp9", "acodec": "none", "height": 720})
    check("manzana 1.9.9: la fila de la lista lleva  (compatible),  + ? (sin comprobar) o nada, como el JSON",
          [_ANSI_RE.sub("", apple_row_mark(r_)) for r_ in (_ra, _ru, _rn)], [APPLE_MARK, APPLE_MARK_UNSURE, ""])
    check("manzana 1.9.9: la columna mide 2 si hay «?» y 1 si no; la lista usa «logo» en vez del ✓",
          (apple_col_width([_ra, _rn]), apple_col_width([_ra, _ru])), (1, 2))
    check("sc_list 1.9.9: --config acepta 0 · 1 · all · on/off y rechaza lo demás; apagado por omisión",
          ([config_validate("DLPY_SAFE_LIST", v_) for v_ in ("0", "1", "all", "on", "off", "zzz")],
           [(n_, d_) for n_, d_, _t in CONFIG_OPTIONS if n_ == "DLPY_SAFE_LIST"]),
          ([(True, "0"), (True, "1"), (True, "all"), (True, "1"), (True, "0"), (False, None)], [("DLPY_SAFE_LIST", "0")]))


def _st_t50_listas(check):
    """[T50] ── 2.0.0: una sola lista de terminal (print_rows) para formatos, pistas, versiones, pendientes, configuración y opciones de bits ──"""
    import contextlib
    _old_w = os.environ.get("DLPY_WIDTH")

    def draw(fn, *a, width=60, **k):
        os.environ["DLPY_WIDTH"] = str(width)
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                fn(*a, **k)
        finally:
            if _old_w is None:
                os.environ.pop("DLPY_WIDTH", None)
            else:
                os.environ["DLPY_WIDTH"] = _old_w
        return [_ANSI_RE.sub("", ln) for ln in buf.getvalue().split("\n") if ln != ""]

    vrows = version_rows([{"ver": "2.0.0", "date": "2026-11-18"}, {"ver": "1.9.9", "date": "2026-11-10"}, {"ver": "1.9.8", "date": ""}], "1.9.9", "2.0.0")
    check("T50 versiones: filas de print_rows (n, flags y columnas) con ✓ solo en la actual y ⬆ solo en la de actualizar",
          [(r["n"], sorted(r["flags"]), r["cols"]) for r in vrows],
          [(1, ["upd"], ["2.0.0", "2026-11-18"]), (2, ["cur"], ["1.9.9", "2026-11-10"]), (3, [], ["1.9.8", ""])])
    check("T50 versiones: sin ninguna fecha la lista lleva una sola columna",
          [r["cols"] for r in version_rows([{"ver": "1.0.0"}, {"ver": "0.9.9", "date": ""}], "1.0.0", None)], [["1.0.0"], ["0.9.9"]])
    out = draw(print_rows, vrows, ["cur", "upd"])
    check("T50 versiones: una línea por fila, número a la izquierda y marca a la derecha en la misma columna que las demás listas",
          (len(out), [ln.lstrip()[:1] for ln in out], [ln.rstrip()[-1:] for ln in out]), (3, ["1", "2", "3"], ["⬆", "✓", "8"]))
    pend = resume_rows([{"title": "Un título larguísimo " * 6, "bytes": 120 * 2 ** 20, "total": 400 * 2 ** 20, "age": 3 * 3600.0},
                        {"title": "Corto", "bytes": 5 * 2 ** 20, "total": 0, "age": 600.0}])
    out = draw(print_rows, pend, [], clip=0)
    check("T50 pendientes: cada descarga ocupa una sola línea (el título se recorta) y no pasa del ancho", (len(out), max(dwidth(ln) for ln in out) <= 60, "…" in out[0], "Corto" in out[1]), (2, True, True, True))
    check("T50 pendientes: avance «120 MB / 400 MB» y antigüedad como columnas", (pend[0]["cols"][1], pend[0]["cols"][2], pend[1]["cols"][1]), (human_size(120 * 2 ** 20) + " / " + human_size(400 * 2 ** 20), "3 h", human_size(5 * 2 ** 20)))
    crow = config_list_rows([("DLPY_ROWS", "26", "t", None), ("DLPY_LINES", "26", "t", "30"), ("DLPY_SAFE_LIST", "0", "t", "zzz")])
    check("T50 config: predeterminada = [valor] sin marca · guardada ● · inválida ✗ con su predeterminado",
          [(sorted(r["flags"]), r["cols"][1]) for r in crow], [([], "[26]"), (["saved"], "30"), (["bad"], "zzz → [0]")])
    out = draw(config_show_list, [("DLPY_ROWS", "26", "t", None), ("DLPY_LINES", "26", "t", "30"), ("DLPY_SAFE_LIST", "0", "t", "zzz")])
    check("T50 config: una sola celda de marca (● o ✗) a la derecha; la predeterminada no lleva ninguna", [ln.rstrip()[-1:] for ln in out], ["]", "●", "✗"])
    out = draw(print_rows, [{"n": 2, "flags": {"default"}, "cols": ["Recomendada: 10 bits"]}, {"n": 1, "flags": set(), "cols": ["Compatible: 8 bits"]}], [])
    check("T50 opciones de bits: ▸ en el margen de la predeterminada y los números alineados", (out[0][0], out[1][0], out[0].lstrip(" ▸")[:1], out[1].lstrip()[:1]), ("▸", " ", "2", "1"))
    long_n = [{"n": 9, "flags": set(), "cols": ["a"]}, {"n": 10, "flags": set(), "cols": ["b"]}]
    out_a = draw(print_rows, long_n[:1], [], num_w=2)
    out_b = draw(print_rows, long_n[1:], [], num_w=2)
    check("T50 num_w: varias tablas seguidas (audio, video, yt-dlp auto) alinean la última cifra de sus números", (out_a[0].index("9"), out_b[0].index("0")), (2, 2))
    check("T50 marcas nuevas con color y símbolo propio (cur · upd · saved · bad)",
          [(FLAG_MARKS[k], FLAG_COLORS[k]) for k in ("cur", "upd", "saved", "bad")], [("✓", "mint"), ("⬆", "orange"), ("●", "mint"), ("✗", "red")])
    out = draw(legend_note, "✓ actual · ⬆ la de actualizar")
    check("T50 leyenda de lista: sangrada 2 columnas con el texto del catálogo", out, ["  ✓ actual · ⬆ la de actualizar"])
    check("T50 ya no quedan los dibujos propios de lista (versiones, pendientes, leyenda de versiones, tokens)",
          [n_ for n_ in ("format_version_rows", "print_version_legend", "_resume_row", "_wrap_tokens") if n_ in globals()], [])
    try:
        with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
            code = fh.read()
    except OSError:
        check("T50 lista única: sin acceso al propio código (se omite)", True, True)
        return
    import ast
    tree = ast.parse(code)
    lists_ = {"_pick_version": "print_rows", "resume_menu": "print_rows", "config_show_list": "print_rows", "ask_keep_bits": "print_rows", "_ci_show_list": "print_rows", "ask_default_track": "print_rows", "ask_extra_tracks": "print_rows"}
    users = {}
    for fn in [n_ for n_ in ast.walk(tree) if isinstance(n_, ast.FunctionDef) and n_.name in lists_]:
        users[fn.name] = any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == lists_[fn.name] for c in ast.walk(fn))
    check("T50 lista única: cada pantalla con una lista numerada la dibuja con print_rows (UIM y UX)", sorted(k for k, v in users.items() if not v), [])


def _st_t51_modulo_selftest(check):
    """[T51] 2.0.2: el cargador del módulo de la autoprueba (caché con hash, descarga verificada, versión coherente)."""
    import hashlib
    import tempfile
    g = globals()
    raw = b'SELFTEST_FOR = "9.9.9"\n'
    good = hashlib.sha256(raw).hexdigest()
    check("2.0.2: URL del módulo y su SHA256SUMS apuntan a modules/ en main",
          [selftest_url(SELFTEST_MODULE), selftest_url(LANG_SUMS)],
          ["https://raw.githubusercontent.com/ElDelDLpy/DLpy/main/modules/dlpy_selftest.py",
           "https://raw.githubusercontent.com/ElDelDLpy/DLpy/main/modules/SHA256SUMS"])
    saved = {k: g[k] for k in ("fresh_bytes", "selftest_dir")}
    envs = {k: os.environ.get(k) for k in ("DLPY_SELFTEST_FILE", "DLPY_SELFTEST_DIR")}
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), SELFTEST_REMOTE_DIR, SELFTEST_MODULE)
    try:
        with tempfile.TemporaryDirectory() as d:
            g["selftest_dir"] = lambda: d
            os.environ.pop("DLPY_SELFTEST_FILE", None)
            sums = lambda digest: ("%s  %s\n" % (digest, SELFTEST_MODULE)).encode()
            net = {"calls": [], "sums": sums(good), "mod": raw}

            def fake(url, timeout=5, limit=None):
                net["calls"].append(url.rsplit("/", 1)[-1])
                return net["sums"] if url.endswith(LANG_SUMS) else net["mod"]
            g["fresh_bytes"] = fake
            if os.path.isfile(here):                       # junto a dlpy.py hay un módulo real: con él no se pide nada a la red (se comprueba más abajo)
                pass
            else:
                text, origin = selftest_module_text()
                check("2.0.2: sin archivo local se baja de main y se guarda con su hash", [text, net["calls"], os.path.isfile(os.path.join(d, SELFTEST_MODULE + ".sha256"))],
                      [raw.decode(), [LANG_SUMS, SELFTEST_MODULE], True])
                net["calls"].clear()
                check("2.0.2: la caché con hash válido no vuelve a descargar", [selftest_module_text()[0], net["calls"]], [raw.decode(), []])
                write_text(os.path.join(d, SELFTEST_MODULE), "SELFTEST_FOR = \"0\"\n")
                check("2.0.2: caché alterada (hash distinto) se descarta y se vuelve a bajar", selftest_module_text()[0], raw.decode())
            for f in os.listdir(d):
                os.remove(os.path.join(d, f))
            net["calls"].clear()
            net["sums"] = sums("0" * 64)
            check("2.0.2: SHA-256 que no coincide: no se usa el módulo", selftest_module_text() if not os.path.isfile(here) else (None, "sha"), (None, "sha"))
            net["sums"] = b""
            check("2.0.2: sin hash publicado tampoco se usa", selftest_module_text() if not os.path.isfile(here) else (None, "sha"), (None, "sha"))
        check("2.0.2: el módulo declara la versión de dlpy.py", SELFTEST_FOR, VERSION)
    finally:
        g.update(saved)
        for k, v in envs.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


SELFTEST_GROUPS = (_st_t1, _st_t2, _st_t3, _st_t4, _st_t5, _st_t6,
                   _st_t7_t9, _st_t10, _st_t11, _st_t12, _st_t13, _st_t14,
                   _st_t15, _st_t16, _st_t17, _st_t18, _st_t19, _st_t20_t22,
                   _st_t23, _st_t24, _st_t25, _st_t26, _st_t27, _st_t27_limpieza, _st_t28_morph, _st_t29_separacion, _st_t30_idioma, _st_t32_arreglos, _st_t33_pulido, _st_t34_movimiento,
                   _st_t35_sondeo, _st_t36_primero, _st_t37_sitio, _st_t38_topbar, _st_t39_version, _st_t40_red, _st_t41_motor_idiomas, _st_t42_franjas_contadores, _st_t43_limpieza_codigo, _st_t44_pines_y_errores, _st_t45_nombres_indefinidos, _st_t46_mensajes_traducibles, _st_t47_plantillas_y_cobertura, _st_t48_fluidez, _st_t49_sc_lista, _st_t50_listas, _st_t51_modulo_selftest)


def selftest_run():
    """`python dlpy.py --selftest`: pruebas rápidas de funciones puras (sin disco ni red)."""
    global LANG
    # las pruebas esperan el español canónico, sea cual sea DLPY_LANG / LANG del sistema
    LANG = "es"
    fails = []

    # [T0] Infraestructura de la prueba
    def check(nombre, obtenido, esperado):
        if obtenido != esperado:
            fails.append(nombre)
            print(f"✗ {nombre}: esperado {esperado!r}, obtenido {obtenido!r}")

    # [T0b] 1.9.1: autoprueba offline. Nunca descarga catálogos; si faltan, comprueba el respaldo y omite suites visuales que exigen traducciones instaladas.
    faltan = [c for c in PACK_LANGS if not lang_pack_load(c)]
    if faltan:
        check("1.9.1: el catálogo ausente recurre al inglés sin red", [lang_effective(faltan[0]), t_display("Cancelado.", lang=faltan[0])],
              ["en", t_display("Cancelado.", lang="en")])
        print("Catálogos no instalados: se usa inglés; se omiten pruebas que requieren paquetes descargados.")
    for grupo in SELFTEST_GROUPS:
        if faltan and grupo.__name__ in ("_st_t10", "_st_t14", "_st_t30_idioma"):
            continue
        grupo(check)
    print(f"Autoprueba: {'OK' if not fails else str(len(fails)) + ' fallo(s)'}")
    return 1 if fails else 0
