#!dlpy.py - siempre empezar el script con este mismo comentario.
# Cada edicion de este archivo sube la version: x.y.z donde Y y Z solo llegan hasta el 9 y X no tiene limites.
# Cada edicion mete el changelog en el py.
# Conservar en todo momento los comentarios anteriores en el mismo orden sin importar las ediciones realizadas.
# ==== CHANGELOG ====
# ## 0.6.1
#
# - Actualización desde GitHub: al arrancar compara su versión con la del dlpy.py
#   del repositorio ElDelDLpy/DLpy (rama main). Si hay una más nueva pregunta
#   «¿Instalar la x.y.z y ejecutarla ahora?». Si aceptas, reemplaza el script y
#   ejecuta la versión nueva al instante con los mismos argumentos (en el mismo
#   proceso, sin exec, para que funcione también en a-Shell). En esa ejecución
#   check_version archiva la versión anterior y guarda el changelog como siempre.
# - Antes de reemplazar valida la descarga: empieza con #!dlpy.py, trae VERSION y
#   compila sin errores. Sin red o con una respuesta inválida no avisa y sigue.
# - Si dices que no, no vuelve a preguntar por esa misma versión (se guarda en
#   state/update.json); cuando suba otra más nueva vuelve a preguntar.
# - Nuevo `--actualizar`: consulta ahora mismo (aunque hubieras dicho que no),
#   avisa si ya tienes la última y sale. DLPY_NO_UPDATE=1 desactiva la
#   comprobación automática; DLPY_UPDATE_URL cambia el enlace del dlpy.py.
# - --selftest: pruebas nuevas de remote_script_version.
#
# ## 0.6.0
#
# - Modos de ejecución: además de iOS (a-Shell) y Android (Termux), DLpy corre
#   ahora en Linux, macOS y Windows (WSL cuenta como Linux). detect_platform
#   devuelve «ios», «android», «macos», «linux» o «windows»; antes todo lo que
#   no era Android caía en el modo iOS. En iOS (a-Shell) la detección se amplía
#   (APPNAME, hideKeyboard, ruta de la sandbox de iOS) para que NO se confunda con
#   macOS, y el comportamiento de iOS y Android no cambia.
#   DLPY_PLATFORM=ios|android|macos|linux|windows fuerza el modo.
# - El banner indica en qué corre (platform_name): «a-Shell · iOS», «Termux ·
#   Android», «Linux», «Linux · WSL», «macOS 14», «Windows 11»…, con la
#   arquitectura y la versión de Python. Se recorta al ancho de la pantalla.
# - Nuevo `--sistema`: informe de qué funciones están disponibles en este sistema
#   (✓ / ✗ / ~) y el motivo de cada una, calculado con lo que realmente hay
#   instalado (ffmpeg, portapapeles, notificaciones, abrir archivos…).
# - Equivalencias por modo:
#   · Descargas: iOS → dlpy_files; Android, Linux, macOS y Windows → carpeta
#     Descargas del sistema (Linux respeta XDG_DOWNLOAD_DIR); backups y changelog
#     en Descargas/DLpy; lo interno en ~/.dlpy/dlpy_internal. DLPY_DOWNLOAD_DIR
#     cambia el destino.
#   · Al terminar: iOS → Atajo; Android → termux-open + notificación; escritorio →
#     abre el archivo con la app por defecto (xdg-open / open / os.startfile) y
#     manda notificación (notify-send / osascript / globo de Windows) si existe.
#     DLPY_ACTION=open|share|none (en escritorio «share» abre la carpeta;
#     DLPY_ANDROID_ACTION sigue valiendo). Sin pantalla (SSH/servidor) no abre.
#   · Compatibilidad: iOS y macOS → códecs nativos de Apple y conversión
#     opcional (VideoToolbox); Android, Linux y Windows → «reproducible» sin
#     convertir (h264/vp9/hevc/aac/opus en mp4/webm/mkv).
#   · Portapapeles: Android (termux-clipboard-get), macOS (pbpaste), Linux
#     (wl-paste/xclip/xsel) y Windows (Get-Clipboard) ofrecen el enlace copiado.
#     En iOS es opcional (DLPY_CLIPBOARD=1) porque iOS pide permiso de pegado.
#   · ffmpeg: Android → pkg; macOS → brew; Linux → apt/dnf/pacman/zypper/apk;
#     Windows → winget; en cada caso pregunta antes. En iOS no se toca.
#   · pip: escritorio usa «python -m pip» sin shell, reintenta con --user y
#     con --break-system-packages (PEP 668); iOS y Android igual que antes.
# - Windows: activa los colores ANSI de la consola, fuerza UTF-8 en la salida,
#   usa msvcrt para la cuenta regresiva y para vaciar el teclado, evita nombres
#   reservados (CON, NUL…) y no usa termios.
# - Corrige: countdown_supported fallaba en Windows (ImportError sin capturar);
#   drain_pending_input se comía la entrada cuando stdin era una tubería
#   (echo s | python dlpy.py); hide_keyboard ejecutaba un comando inexistente
#   fuera de iOS; pip_install usaba shlex.quote en Windows (comillas inválidas).
# - YouTube (yt-dlp ≥ 2025.11.12 exige un runtime de JavaScript y el paquete
#   yt-dlp-ejs en la versión exacta que fija esa versión de yt-dlp): como iOS y
#   Android instalan yt-dlp con --no-deps, yt-dlp-ejs nunca se instalaba. Ahora,
#   si hay un runtime de JavaScript (deno, node, bun o quickjs), DLpy lee de los
#   metadatos de yt-dlp qué versión de yt-dlp-ejs pide y ofrece instalarla.
#   Si el único runtime es node/bun/quickjs añade solo «--js-runtimes <rt>»
#   (deno ya viene activado); no pisa DLPY_YTDLP_ARGS. Al pegar un enlace de
#   YouTube sin runtime avisa y dice cómo instalarlo (Termux: pkg install nodejs).
#   Otros sitios no se ven afectados. --sistema lo muestra.
# - --selftest: pruebas nuevas de detect_platform por sistema, platform_name,
#   safe_name con nombres reservados, desktop_downloads_dir, capabilities,
#   ejs_pin y js_runtime_args.
#
# ## 0.5.4
#
# - Android: DLpy pide solo el acceso al almacenamiento. Si falta ~/storage/shared
#   (o Descargas no se puede escribir) ejecuta termux-setup-storage al arrancar,
#   muestra el aviso de permiso de Android y espera hasta 45 s a que lo aceptes;
#   si lo aceptas sigue en Descargas en esa misma ejecución, sin reiniciar Termux.
#   Solo lo intenta una vez (marca ~/.dlpy/storage_asked): si lo rechazas, las
#   siguientes ejecuciones usan ~/dlpy_files y avisan; la marca se borra cuando el
#   acceso funciona, así que si luego lo pierdes vuelve a pedirlo.
#   DLPY_NO_STORAGE_SETUP=1 lo desactiva. Fuera de Android no hace nada.
# - --selftest nunca lanza el permiso.
#
# ## 0.5.3
#
# - Android: copiar y mover archivos ya no falla en el almacenamiento compartido
#   (Descargas). shutil.copy2/move intentan chmod/utime sobre el destino y Android
#   lo rechaza con «Operation not permitted»; eso podía dejar sin guardar el video,
#   sin índice y sin reutilizar nada. Ahora todo pasa por copy_file/move_file, que
#   copian el contenido y tratan permisos y fecha como opcionales. iOS no cambia.
# - Android: la caché de streams (24 h) avisa siempre si no pudo guardar una pista
#   (antes solo en debug) y, al terminar, indica cuántas pistas quedaron en caché.
#   Si el enlace físico falla se copia el archivo en su lugar.
# - Android: compartir un enlace a Termux queda automatizado: en la primera
#   ejecución DLpy crea solo ~/bin/termux-url-opener (si ya había uno ajeno no lo
#   toca y lo avisa; «--instalar-android» sigue sirviendo para forzarlo).
# - --selftest: pruebas nuevas de copy_file/move_file.
#
# ## 0.5.2
#
# - Android: al terminar la descarga Termux abre el archivo solo, con el
#   reproductor de Android (termux-open --view con el tipo MIME del archivo;
#   si falla, termux-open normal). Antes solo se abría con
#   DLPY_ANDROID_ACTION=open. Ahora DLPY_ANDROID_ACTION vale «open» por defecto;
#   «share» comparte el archivo y «none» no abre nada. Si no se pudo abrir, avisa
#   el motivo probable (Termux en segundo plano necesita «Mostrar sobre otras
#   apps») y la notificación sigue abriéndolo al tocarla.
# - Android: al arrancar, DLpy se mueve solo a la raíz de Termux (~/dlpy.py) si
#   estaba en otra carpeta (p. ej. Descargas) y se vuelve a ejecutar desde ahí con
#   los mismos argumentos; borra el original y actualiza ~/bin/termux-url-opener
#   si apuntaba a la ruta vieja. Si no puede moverse, sigue donde está. Además el
#   directorio de trabajo pasa a ser ~. DLPY_NO_MOVE=1 desactiva el movimiento.
# - Aclaración: en Android los videos terminados van a Descargas (no a
#   Descargas/DLpy, que solo guarda backups y changelog), como desde 0.5.1.
# - --selftest: prueba nueva de root_move_target.
#
# ## 0.5.1
#
# - Android: los archivos terminados se guardan directo en la carpeta Descargas
#   de Android (antes iban a Descargas/DLpy). Backups y changelog siguen en
#   Descargas/DLpy. DLPY_DOWNLOAD_DIR cambia el destino de las descargas.
# - Seguridad: Descargas es de todo el teléfono, así que DLpy solo toca lo que
#   él mismo descargó (lo registrado en su índice). La limpieza por espacio y el
#   orden de carpetas no ven ni borran tus otros archivos de Descargas.
# - Los archivos que ya estaban en Descargas/DLpy (0.5.0) se siguen reconociendo;
#   al volver a descargarlos pasan a Descargas.
# - iOS no cambia: el destino sigue siendo dlpy_files.
#
# ## 0.5.0
#
# - Detección de plataforma al arrancar (detect_platform): Android/Termux si hay
#   TERMUX_VERSION, PREFIX/HOME de com.termux o sys.platform «android»; en cualquier
#   otro caso se usa el modo iOS/a-Shell, que queda EXACTAMENTE como en 0.4.9.
#   DLPY_PLATFORM=ios|android fuerza una u otra.
# - Modo Android (Termux):
#   · Guarda en Descargas/DLpy (almacenamiento compartido, requiere
#     termux-setup-storage); sin permiso usa ~/dlpy_files y lo avisa. Lo interno
#     (índice, caché, work/) va en ~/.dlpy/dlpy_internal.
#   · No hay Atajos: al terminar avisa la ruta, escanea el archivo para la galería
#     (termux-media-scan) y manda una notificación (termux-notification) si Termux:API
#     está instalado. DLPY_ANDROID_ACTION=open|share abre o comparte el archivo.
#   · Sin conversión Apple: «compatible» pasa a significar reproducible en Android
#     (h264/vp9/hevc/aac/opus en mp4/webm/mkv) y el mejor formato prefiere h264.
#   · Ofrece instalar ffmpeg con «pkg install» si falta; pip reintenta con
#     --break-system-packages si Termux lo pide.
#   · Si el portapapeles trae un enlace (termux-clipboard-get) lo ofrece primero.
#   · «--instalar-android» crea ~/bin/termux-url-opener: al compartir un enlace a
#     Termux desde cualquier app se abre DLpy con ese enlace.
#   · Sin hideKeyboard, ancho de barras 60 y textos sin iPhone/a-Shell.
# - Prueba nueva en --selftest para detect_platform.
#
# ## 0.4.9
#
# - Reanudación automática: una descarga cortada (Ctrl+C, error de red, iOS
#   cerrando a-Shell) continúa sola al repetir el mismo enlace con los mismos
#   formatos. La carpeta de trabajo ya no es aleatoria: es work/resume-<huella>,
#   con la huella calculada de enlace + format_id + extensión + tamaño exacto.
#   Cambiar formato, calidad o pistas da otra huella y empieza de cero.
# - El nombre base se guarda en resume.json para que el .part siga reconociéndose.
# - Cancelar o fallar ya no borra el avance; solo se borra al terminar bien.
#   Tras 3 fallos seguidos sin avanzar, el parcial se descarta (por si está dañado).
# - Los parciales caducan 24 h después de su ÚLTIMA modificación (antes: de la
#   creación de la carpeta).
# - La velocidad final de una pista reanudada no cuenta los bytes ya descargados.
#
# ## 0.4.8
#
# - En la lista de formatos, Enter sin escribir nada ya no sale del script: se
#   vuelve a preguntar. Solo «q» sale. Así un Enter accidental no tira la sesión.
#
# ## 0.4.7
#
# - Una opción inexistente o una respuesta que no es s/n ya no hace seguir (ni
#   salir) al script: se avisa y se repite la pregunta. Afecta a la lista de
#   formatos, la pista predeterminada, las pistas adicionales (ahora se valida
#   cada número), «¿Usarlo?», «¿Descargar de nuevo?», «¿Convertir?» y las
#   preguntas de dependencias. Enter y la cuenta regresiva siguen igual.
# - «¿Convertir? (S/n)» de compatibilidad Apple tiene ahora cuenta regresiva
#   (WAIT_SECONDS): si vence sin escribir nada se aplica la respuesta por
#   defecto (convertir). Empezar a escribir cancela la cuenta.
# - Nuevo helper ask_yn() y parse_yn(); el --selftest incluye pruebas de parse_yn.
#
# ## 0.4.6
#
# - La línea final de cada pista muestra siempre la velocidad media. Antes solo
#   aparecía si la descarga duraba más de 0.3 s, así que las pistas de audio
#   (archivos pequeños que bajan casi al instante) quedaban sin «↓ …». Ahora el
#   mínimo es 0.05 s; si yt-dlp tampoco da el tiempo se usa el de la propia pista.
# - Al empezar la descarga se muestra el nombre del archivo («Archivo: …»)
#   antes de las barras.
#
# ## 0.4.5
#
# - Las barras de descarga muestran directamente la calidad («1080p», «1080p60»)
#   en las pistas de video y el idioma («es-US») en las de audio, sin la palabra
#   «Video»/«Audio». Antes «Video 1080p» se recortaba a «Video …» en pantallas
#   angostas y se perdía justo el dato útil. La calidad usa el mismo formato que
#   la columna «Res» de la lista. Sin altura o sin idioma queda «Video»/«Audio».
#   La línea final de cada pista usa la misma etiqueta («1080p: listo (↓ …)»).
# - El --selftest incluye ahora pruebas de stream_label.
#
# ## 0.4.4
#
# - Corrige un falso positivo al reintentar una descarga: antes bastaba que el
#   texto del error contuviera «403» o «410» (p. ej. dentro de una URL o un ID)
#   para reanalizar el enlace sin necesidad. Ahora solo se reintenta ante
#   «HTTP Error 403/410», «not available», «expired» o «forbidden».
# - Los ~60 bloques «except … as _ign: dbg("x: ignorado", …)» pasan a un único
#   helper ignore(donde, error) con la misma salida en modo debug; se quitan
#   los «pass» sobrantes. Se acotan las excepciones de term_width, _host,
#   load_json y countdown_supported a los errores esperables (antes Exception).
#   Sin debug el comportamiento no cambia.
# - Las órdenes al shell (pip install y la apertura del atajo) ahora escapan
#   los argumentos con shlex.quote en vez de comillas armadas a mano.
# - La cabecera «Principal» queda justo encima de main() (estaba antes del
#   bloque de análisis tolerante).
# - Nuevo `python dlpy.py --selftest`: pruebas rápidas de funciones puras
#   (safe_name, vtuple, normalize_format, parse_sections, mark_originals,
#   auto_best, yes y el filtro de reintento). No toca disco ni red.
#
# ## 0.4.3
#
# - Elimina por completo el soporte de cookies: ya no se lee, valida, guarda
#   ni usa ningún cookies.txt (desaparecen parse_cookies, read_cookies,
#   cookies_file, save_cookies_text, read_pasted_cookies, DLPY_COOKIES y el
#   uso de cookiefile/--cookies en el análisis y la descarga). Ante el error
#   «Sign in to confirm you're not a bot» solo se avisa y se termina, sin
#   pedir nada. Un ~/Documents/dlpy_cookies.txt que haya quedado de versiones
#   anteriores ya no se toca: bórralo a mano si quieres.
# - DLPY_YTDLP_ARGS sigue pasando a yt-dlp las banderas en bruto tal cual.
# - Los errores que antes se tragaban en silencio (except … pass / return /
#   valor por defecto) ahora se anotan en modo debug («[debug] función:
#   ignorado …»). Sin debug el comportamiento no cambia. Se dejan igual el
#   Ctrl+C / fin de entrada del usuario y el propio dbg().
# - Aclara que DLPY_CLEAR vale 3 por defecto (reinicio completo del terminal,
#   \x1bc); el changelog 0.3.7 indicaba 1 y el comentario del código remitía
#   a él. Solo se corrige el comentario: el comportamiento es el mismo.
# - Erratas del encabezado: «llengan» → «llegan», «realizas» → «realizadas».
#
# ## 0.4.2
#
# - Error «Sign in to confirm you're not a bot»: ahora solo se pide PEGAR el
#   contenido del cookies.txt (formato Netscape) y terminar con una línea
#   vacía. Se valida, se guarda en ~/Documents/dlpy_cookies.txt (permisos
#   privados) y se reintenta el análisis. Ya no se pide una ruta de archivo.
# - Tras pegar se limpia la pantalla para no dejar las cookies a la vista.
#
# ## 0.4.1
#
# - Al actualizar de versión, el backup de dlpy_files (descargas e índice) sigue
#   igual y ahora, si en dlpy_internal hay descargas (delivery/, cache/, work/
#   u otras sueltas), pregunta «¿Mover también las descargas de dlpy_internal
#   a backups? (s/N)». Con «s» pasan a backups/<versión>/_internal/ junto al
#   index.json; state/ y script/ no se tocan. Con «N» (Enter) no se mueve nada.
# - Cookies de YouTube: si existe ~/Documents/dlpy_cookies.txt (o la ruta de
#   DLPY_COOKIES) se usa en el análisis y en la descarga (formato Netscape),
#   salvo que se pase --cookies/--cookies-from-browser en DLPY_YTDLP_ARGS.
#   Avisa si el archivo está vacío, no tiene formato válido, no trae cookies de
#   YouTube/Google o parecen caducadas. El archivo queda fuera de dlpy_files,
#   así que ninguna limpieza ni backup lo toca.
# - Error «Sign in to confirm you're not a bot»: ya no repite los intentos
#   (no sirven); explica qué hacer y permite pegar la ruta de un cookies.txt,
#   que se copia a ~/Documents/dlpy_cookies.txt y reintenta el análisis.
#   Nota: yt-dlp no admite usuario y contraseña de Google; hacen falta cookies.
#
# ## 0.4.0
#
# - Corrige un error de texto en el tercer comentario del encabezado
#   («momentos» → «momento»).
#
# ## 0.3.9
#
# - dlpy_internal reorganizada en subcarpetas: state/ (index.json,
#   last_link.json, version.json), script/ (script_snapshot.py, changelog.md),
#   cache/streams/ (antes stream_cache/), work/ (descargas en curso) y
#   delivery/<id>/ (copias de entrega al atajo, antes sueltas en la raíz).
# - Migración automática al arrancar: mueve lo de la estructura anterior a su
#   sitio nuevo (se hace antes de revisar el almacenamiento y la versión).
# - Limpieza por límite, opción «backups»: ahora borra solo las descargas
#   (video, audio, subtítulos e imágenes descargadas) dentro de backups/ y de
#   las carpetas de versión legadas. Scripts (.py), changelogs, índices y
#   cualquier otro archivo se conservan; las carpetas que queden vacías se
#   eliminan. El aviso y los tamaños del banner lo reflejan.
# - Las caducidades de 24 h (entregas y work/) se aplican ahora por elemento.
#
# ## 0.3.8
#
# - Las barras de descarga ahora muestran siempre la velocidad de bajada
#   («↓ 2.4MB/s»): si yt-dlp no la informa (o aún no hay porcentaje) se calcula
#   a partir de los bytes descargados, y es el último dato en recortarse cuando
#   la pantalla es angosta (antes se perdía al no haber porcentaje conocido).
# - Al terminar cada pista la línea final conserva la velocidad media de esa
#   descarga (también en el modo sin TTY / debug: «Video 1080p: listo (↓ …)»).
# - Limpieza por límite de almacenamiento: la opción «videos descargados» ahora
#   borra solo los archivos de video dentro de dlpy_files y sus subcarpetas
#   (excluye backups/). Audios, changelog y demás archivos no se tocan; las
#   subcarpetas que queden vacías se eliminan. Las copias de entrega en
#   dlpy_internal solo se borran si contienen un video.
#
# ## 0.3.7
#
# - Corrige que tras un clear a mitad de ejecución (p. ej. al elegir «b» con
#   una lista larga) la pantalla quedara en blanco y hubiera que subir con
#   scroll: ahora se vacía primero el historial (\x1b[3J) y después la
#   pantalla (\x1b[2J\x1b[H), para que la vista no se quede desfasada.
# - DLPY_CLEAR=1..4 elige el método de limpieza si en tu terminal sigue
#   fallando: 1 = historial → pantalla (por defecto), 2 = pantalla →
#   historial (como 0.3.6), 3 = reinicio completo del terminal (\x1bc),
#   4 = solo pantalla (como 0.3.3, sin vaciar el historial).
#
# ## 0.3.6
#
# - clear_screen ahora también vacía el historial de desplazamiento del
#   terminal (\x1b[3J) además de la pantalla visible, para no ver logs
#   anteriores al hacer scroll en la misma sesión. No afecta a otras sesiones
#   de a-Shell (cada una tiene su propio buffer).
#
# ## 0.3.5
#
# - Banner mucho más notorio: barra de título a todo el ancho en video
#   inverso (cian; amarilla con «DEBUG ACTIVO» cuando debug está encendido),
#   con la versión a la izquierda, y una línea separadora debajo del espacio.
# - Al arrancar se limpia la consola (clear_screen) para que el banner quede
#   arriba y no mezclado con la salida de la ejecución anterior. En debug no
#   se borra: solo se imprime el separador.
#
# ## 0.3.4
#
# - Banner más preciso: el total de «Espacio» ahora es el mismo que usa la
#   limpieza de almacenamiento (antes omitía índice, snapshot y changelog, que
#   ahora salen como «otros»), muestra el % del límite (amarillo si se pasa),
#   el número de descargas y los GB con 2 decimales.
# - El desglose del banner se ajusta al ancho real (safe_width) en vez de
#   desbordar y romper la línea en pantallas angostas.
# - Se quita el banner duplicado que salía tras pegar el enlace (se imprimía
#   sin limpiar nada, apilado sobre el de arranque y los comentarios).
# - Código obsoleto eliminado: CL_START/CL_END (sin uso), parámetro «compact»
#   de banner (se ignoraba), rama duplicada TTY/no-TTY en clear_screen,
#   comentario engañoso de storage_summary y condición redundante en
#   reuse_downloaded.
#
# ## 0.3.3
#
# - Banner ampliado: muestra el espacio usado por DLpy (descargas, caché/
#   temporales y backups) junto a la versión y el estado de debug.
# - Cada clear_screen vuelve a pintar ese mismo banner (versión + debug +
#   espacio) para que quede visible tras limpiar la consola.
# - Limpieza de consola más oportuna antes de preguntas clave (pistas,
#   conversión Apple) para que el teclado de iOS no tape las opciones.
#
# ## 0.3.2
#
# - apple_plan: si video + audios + contenedor ya son compatibles con Apple
#   (aunque haya merge_ext), no se ofrece conversión innecesaria.
# - normalize_format: más conservador al asumir avc1/mp4a; solo lo hace en
#   contenedores Apple con indicios claros de video; en el resto deja
#   «unknown» y no marca como compatible Apple.
# - reuse_downloaded: comentario y lógica aclarados (si el archivo ya está
#   convertido y ahora no se pide conversión, o viceversa sin original, se
#   fuerza re-descarga).
# - ask_apple_convert: al cancelar con Ctrl+C avisa claramente que se
#   descargará sin convertir.
# - ffmpeg_progress: cierra el archivo de error de ffmpeg en todos los
#   caminos (incluido fallo al lanzar Popen).
# - tree_size / check_storage: el conjunto de inodos se reutiliza de forma
#   coherente al sumar categorías para no sobrestimar con hard-links.
#
# ## 0.3.1
#
# - Corrige que el changelog no se sacara del .py: solo se extraía cuando la
#   versión cambiaba respecto a la guardada. Ahora, en cada arranque, si el
#   script trae un bloque «CHANGELOG … FIN CHANGELOG» se mueve a changelog.md
#   y se quita del .py (aunque la versión sea la misma, p. ej. al volver a
#   pegar el archivo).
# - Si la versión ya existe en changelog.md se actualiza su texto (antes se
#   ignoraba el nuevo).
# - Los marcadores se reconocen aunque cambien los espacios o las mayúsculas
#   de «FIN»; si hay inicio sin fin, avisa y no toca el script.
# - Al terminar muestra cuántas versiones nuevas se guardaron.
#
# ## 0.3.0
#
# - Corrige «No se encontraron formatos» en sitios cuyos formatos llegan sin
#   códec (yt-dlp deja vcodec/acodec en None; p. ej. PornHub con MP4 directos):
#   antes se descartaban todos. Ahora un formato sin códec declarado se toma
#   como un archivo único con video y audio (o solo audio si así se indica).
#   En MP4/M4V/MOV se asume avc1/mp4a (se marca con «?» en la tabla); en otros
#   contenedores se trata como no compatible con Apple y se ofrece convertir.
# - El análisis original de yt-dlp no se toca: la normalización se hace sobre
#   copias, solo para armar la lista.
#
# ## 0.2.9
#
# - Corrige «Unable to download webpage: HTTP Error 404» al analizar algunos
#   sitios que sí funcionan con yt-dlp en bruto. El análisis ahora prueba en
#   orden: (1) opciones de biblioteca como hasta ahora, (2) opciones idénticas
#   a las del CLI de yt-dlp (reintentos, cabeceras y demás valores por defecto),
#   (3) lo mismo sin --no-playlist y (4) el ejecutable yt-dlp -J si existe.
#   Las opciones que funcionaron se reutilizan también al descargar.
# - DLPY_YTDLP_ARGS="…" añade banderas de yt-dlp en bruto (p. ej. --cookies
#   archivo.txt, --user-agent "…", --add-header "Referer:…") al análisis y a la
#   descarga.
# - En debug se anota qué intento falló y cuál funcionó.
#
# ## 0.2.8
#
# - Corrige «Requested format is not available» al descargar (visto en
#   Facebook): antes yt-dlp volvía a analizar el enlace al descargar y a veces
#   devolvía otra lista de formatos distinta a la que se mostró. Ahora se
#   descarga con el mismo análisis que vio el usuario (process_ie_result).
# - Si aun así falla porque el formato ya no existe o la URL caducó: reanaliza
#   el enlace y, como último recurso, usa el mejor equivalente avisándolo.
# - Los comentarios inteligentes no tocan el enlace ni la descarga (solo
#   imprimen); el fallo no venía de ellos.
#
# ## 0.2.7
#
# - Comentarios inteligentes según el uso (humor irreverente), en dos momentos:
#   * Al recibir el enlace: según la hora/día (madrugada, comida, lunes,
#     viernes/sábado noche, 31 dic, 14 feb…) y según el sitio (YouTube, TikTok,
#     X, Instagram/Facebook, Twitch, Reddit…). Sitio adulto: alerta que
#     parpadea y comentario aparte.
#   * Tras analizar el video: contenido +18, directo, muy largo o muy corto, y
#     «ya lo tenías». Tras elegir formato: más de 2 GB, 4K, resolución baja,
#     solo audio.
#   * Al terminar (o al entregar uno ya descargado), al cancelar con Ctrl+C y
#     al aparecer la limpieza de almacenamiento.
# - Los comentarios de las primeras etapas se repintan tras limpiar la pantalla
#   (máx. 4) para que no se pierdan.
# - DLPY_ROAST=0 los apaga. Ninguno puede interrumpir una descarga.
#
# ## 0.2.6
#
# - Limpieza de almacenamiento al arrancar (antes de todo lo demás): si
#   dlpy_internal + dlpy_files pesan más de 1 GB, muestra cuánto ocupa cada
#   parte y pregunta por separado si borrar: videos descargados, caché y
#   temporales (stream_cache, work y entregas) y backups. Por defecto responde
#   No. Los archivos con enlaces duros se cuentan una sola vez.
# - Al borrar descargas se limpian también sus entradas del índice.
# - El límite se puede cambiar con DLPY_CLEAN_LIMIT_MB (por defecto 1024).
#
# ## 0.2.5
#
# - Modo debug (DLPY_DEBUG=1) mejorado, sin cambiar nada cuando está apagado:
#   * La descarga corre yt-dlp en modo verbose y con su progreso nativo
#     (incluye las líneas de ffmpeg de unir/remux), igual que fuera del script.
#   * ffmpeg propio (conversión y ajuste de pistas): imprime el comando
#     completo, su salida en bruto en vivo (loglevel info), el bloque
#     -progress cada 2 s y el código de salida.
#   * Líneas «[debug] …» con los datos de cada paso: info del video, formatos,
#     pistas, formato elegido, selección, plan Apple, decisión de reutilizar,
#     caché de streams, opciones de yt-dlp, eventos de hooks, archivo final,
#     entrada del índice y entrega al atajo.
#   * Sin barras animadas (se usan líneas de texto) y sin borrar la pantalla
#     (se imprime un separador) para no perder lo ya mostrado.
#
# ## 0.2.4
#
# - Al convertir a Apple con varios idiomas, las pistas de audio conservan su
#   nombre (antes salían como «Track 1, 2…»): se escribe de nuevo el título y
#   el handler_name de cada pista (el MP4 solo guarda el segundo) y cuál es la
#   predeterminada. Aplica también al convertir un archivo ya descargado.
#
# ## 0.2.3
#
# - Estilo unificado: todas las barras (descarga, unión, conversión, ajuste de
#   pistas) usan el mismo diseño y siempre dibujan la barra. Si no cabe todo,
#   se recorta primero el ETA, luego la velocidad y por último el nombre,
#   en vez de quedarse solo con el porcentaje.
# - Nombres de fase más cortos («Conv. HEVC», «Uniendo», «Pistas»…).
# - Reutiliza lo ya descargado: si eliges los mismos parámetros que el archivo
#   YA DESCARGADO (mismas pistas/formato y misma decisión de conversión) no
#   se vuelve a bajar nada: se entrega el que ya existe.
# - Si el archivo ya descargado tiene esos mismos streams pero sin convertir y
#   ahora eliges convertir, se convierte ese archivo directamente (con barra),
#   sin volver a descargar.
# - La caché de streams de 24 h sigue funcionando para el resto de casos.
#
# ## 0.2.2
#
# - La conversión a Apple y el ajuste de pistas ya muestran barra de progreso
#   real: porcentaje, velocidad (p. ej. 1.8x) y ETA, leídos del -progress de
#   ffmpeg. Si el video no informa su duración, la barra pasa a modo
#   indeterminado con el tiempo ya procesado.
# - Cada intento de encoder (HEVC hardware → HEVC software → H.264) reinicia
#   la barra con su propio nombre.
# - Unir audio/video muestra avance real vigilando el tamaño del archivo
#   temporal frente a la suma de las pistas.
# - Ctrl+C durante una conversión detiene ffmpeg.
# - Si no se puede lanzar ffmpeg directamente, vuelve al método anterior
#   (sin porcentaje, con barra indeterminada).
#
# ## 0.2.1
#
# - Corrige el congelamiento al preguntar «¿Convertir?» cuando había varios
#   idiomas (venía justo después de las preguntas con cuenta regresiva):
#   esa pregunta usa ahora el mismo lector de línea que las anteriores
#   (timed_input sin cuenta) en vez de input().
# - La conversión de video usa HEVC (H.265, etiqueta hvc1) en lugar de H.264:
#   prueba hevc_videotoolbox → libx265 y, solo como último recurso,
#   libx264. El índice guarda el códec realmente usado.
#
# ## 0.2.0
#
# - Si el formato elegido (o las pistas de audio elegidas) no es compatible con
#   Apple, pregunta si convertirlo: video → H.264, audio → AAC, contenedor →
#   MP4 (video) o M4A (audio). Lo que ya es compatible se copia sin recodificar
#   (solo remux); HEVC se etiqueta hvc1.
# - Video: prueba h264_videotoolbox y, si falla, libx264.
# - Sin ffmpeg avisa y descarga tal cual. Si la conversión falla, conserva el original.
# - El índice guarda «converted» y YA DESCARGADO muestra la línea «Conversión».
#
# ## 0.1.9
#
# - YA DESCARGADO muestra de forma explícita la pista usada y su idioma
#   (además de la tabla de pistas si hay varias).
# - Limpia la consola antes de listar formatos y al iniciar la descarga;
#   tras cada limpieza se vuelve a pintar el banner de arranque.
# - Copia el changelog actual a dlpy_files/changelog.md.
#
# ## 0.1.8
#
# - Corrige el doble prompt al lanzar desde Atajos (p. ej. «¿Usarlo? ▸ ¿Usarlo? ▸»):
#   se drenan los Enter residuales del buffer de stdin antes de cada pregunta,
#   sin cambiar el modo del terminal.
# - El banner ya no se reimprime justo después del arranque (quedaba duplicado);
#   solo en pasos posteriores (análisis / descarga).
#
# ## 0.1.7
#
# - dlpy_data → dlpy_files: solo descargas terminadas y backups/.
# - Todo lo demás (índice, último enlace, versión, snapshot, changelog,
#   caché de pistas y directorios de trabajo) vive en dlpy_internal.
# - Caché de streams 24 h: si se vuelve a pedir el mismo format_id
#   (mismo video a la misma resolución/pista), se reutiliza el archivo
#   intermedio sin volver a bajarlo. Si el formato elegido es distinto
#   (p. ej. 720 en vez de 1080), se descarga de nuevo.
# - Migración automática desde dlpy_data al arrancar.
# - El banner (DLpy vX · debug) se reimprime en los pasos principales
#   para que la versión quede visible durante toda la ejecución.
#
# ## 0.1.6
#
# - Corrige el congelamiento al pedir entrada (introducido en 0.1.5): se quitan los
#   cambios al modo del terminal (apagar eco y vaciar la entrada).
# - Enter fantasma: ahora se ignora una respuesta vacía que llega casi al instante
#   de mostrar la pregunta (menos de 0.4 s), sin tocar el terminal.
# ==== FIN CHANGELOG ====
# DLpy - descargador para a-Shell mini basado en yt-dlp
# Uso: python dlpy.py [LINK]
#   Sin LINK: ofrece usar el último enlace.
#   --selftest: ejecuta pruebas rápidas de funciones puras y sale.
#   --sistema: muestra en qué corre y qué funciones están disponibles (y por qué).
#   --actualizar: busca ahora una versión nueva en GitHub (ver 0.6.1) y sale.
# Corre en iOS (a-Shell), Android (Termux), Linux, macOS y Windows (ver 0.6.0).

VERSION = "0.6.1"

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
    print("DLpy necesita acceso al almacenamiento: acepta el permiso de Android...")
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
            print("Acceso concedido.")
            return True
        time.sleep(0.5)
    print("No se concedió el acceso al almacenamiento; se usará ~/dlpy_files.")
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
DEBUG = os.environ.get("DLPY_DEBUG", "").strip().lower() not in ("", "0", "no", "false")
_env_color = os.environ.get("DLPY_COLOR")
if _env_color is not None:
    USE_COLOR = _env_color.strip().lower() not in ("0", "no", "false", "")
else:
    USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR") and ANSI_OK
CLR = "\r\x1b[2K" if sys.stdout.isatty() and ANSI_OK else "\r"
# Secuencia de clear_screen (DLPY_CLEAR=1..4; por defecto 3, ver changelog 0.3.7 y 0.4.3)
CLEAR_SEQS = {"1": "\x1b[3J\x1b[2J\x1b[H", "2": "\x1b[2J\x1b[3J\x1b[H",
              "3": "\x1bc", "4": "\x1b[2J\x1b[H"}
CLEAR_SEQ = CLEAR_SEQS.get(os.environ.get("DLPY_CLEAR", "3").strip(), CLEAR_SEQS["3"])

_ANSI = {"green": "92", "yellow": "93", "blue": "94", "red": "91",
         "cyan": "96", "dim": "2", "bold": "1"}
FLAG_COLORS = {"apple": "green", "orig": "yellow", "default": "blue"}
FLAG_TEXT = {"apple": f"compatible {PLAT_LABEL}", "orig": "pista original", "default": "predeterminada"}


def paint(text, color):
    return f"\x1b[{_ANSI[color]}m{text}\x1b[0m" if USE_COLOR else text


def dot(color):
    return paint("●", color)


def term_width():
    try:
        w = shutil.get_terminal_size((80, 24)).columns
    except (OSError, ValueError) as _ign:
        ignore("term_width", _ign)
        w = 80
    return max(24, min(w - 1, 110))


def safe_width():
    """Ancho para dibujar en una sola línea. a-Shell mini desde Atajos puede
    reportar más columnas de las reales, así que se limita (DLPY_WIDTH=N)."""
    try:
        cap = int(os.environ.get("DLPY_WIDTH", "60" if IS_ANDROID else "80" if IS_DESKTOP else "40"))
    except ValueError:
        cap = 40
    return max(20, min(term_width(), cap))


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


def _say(color, msg):
    lines = textwrap.wrap(plat_text(msg), term_width() - 2) or [""]
    b = ACTIVE_BAR
    if b is not None and b.th:
        with b.lock:                      # borra la barra, imprime y deja que se redibuje
            sys.stdout.write("\r" + " " * b.last_len + "\r")
            b.last_len = 0
            _say_lines(color, lines)
    else:
        _say_lines(color, lines)


def _say_lines(color, lines):
    print(dot(color) + " " + lines[0])
    for ln in lines[1:]:
        print("  " + ln)


def m_ok(msg):
    _say("green", msg)


def m_warn(msg):
    _say("yellow", msg)


def m_info(msg):
    _say("blue", msg)


def m_err(msg):
    _say("red", msg)


def note(text):
    print(paint(textwrap.fill(plat_text(text), term_width()), "dim"))


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
    print(paint(f"[debug] {label}: {text}", "dim"))
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
        _say("cyan", text)
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
            _say("cyan", t)
        except Exception as _ign:
            ignore("show_pinned", _ign)


def blink_alert(text, times=8, delay=0.3):
    """Texto parpadeante (alterna entre invertido y normal; no depende de ANSI blink)."""
    if not ROAST:
        return
    try:
        if sys.stdout.isatty() and USE_COLOR:
            for i in range(times):
                style = "\x1b[1;97;41m" if i % 2 == 0 else "\x1b[1;91m"
                sys.stdout.write(CLR + nowrap(style + " " + text + " \x1b[0m"))
                sys.stdout.flush()
                time.sleep(delay)
            sys.stdout.write(CLR)
        print(dot("red") + " " + paint(text, "red"))
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


def title_bar(left, right, style):
    """Barra de una línea a todo el ancho seguro, en video inverso si hay color."""
    w = safe_width()
    gap = max(1, w - len(left) - len(right))
    text = (left + " " * gap + right)[:w].ljust(w)
    return f"\x1b[{style}m{text}\x1b[0m" if USE_COLOR else text


def banner():
    """Encabezado notorio: barra de versión + debug, espacio usado y separador.
    Se pinta tras cada clear_screen (y al arrancar) para que quede visible."""
    if DEBUG:
        print(title_bar(f" DLpy v{VERSION}", "DEBUG ACTIVO ", "1;30;103"))
    else:
        print(title_bar(f" DLpy v{VERSION}", "debug off ", "1;30;106"))
    where = f"Corre en: {platform_name()} · {machine_name()}"
    if len(where) > safe_width():
        where = where[:safe_width() - 1] + "…"
    print(paint(where, "dim"))
    try:
        head, detail, over = storage_lines()
        print(paint(head, "yellow" if over else "dim"))
        for ln in detail:
            print(paint(ln, "dim"))
    except Exception:
        print(paint("Espacio: ?", "dim"))
    print(paint("─" * safe_width(), "yellow" if DEBUG else "cyan"))


def clear_screen():
    """Borra la consola y deja solo el banner (+ comentarios fijados).
    En debug no borra: imprime un separador para conservar lo ya mostrado."""
    if DEBUG:
        print()
        print(paint("─" * min(term_width(), 40), "dim"))
        banner()
        show_pinned()
        return
    if ANSI_OK:
        sys.stdout.write(CLEAR_SEQ)
        sys.stdout.flush()
    else:
        os.system("cls" if os.name == "nt" else "clear")
    banner()
    show_pinned()


def show_title(title):
    print()
    print(paint(textwrap.fill(title, term_width()), "bold"))


def header(title):
    w = term_width()
    text = " " + title[:max(1, w - 6)] + " "
    print()
    print(paint("──" + text + "─" * max(0, w - 2 - len(text)), "cyan"))


def kv(label, value, flag=None):
    w = term_width()
    lead = f"{label}: "
    extra = 2 if flag else 0
    lines = textwrap.wrap(str(value), max(8, w - len(lead) - extra)) or [""]
    if flag:
        lines[-1] += " " + dot(FLAG_COLORS[flag])
    print(paint(lead, "dim") + lines[0])
    for ln in lines[1:]:
        print(" " * len(lead) + ln)


def legend(keys):
    w = term_width()
    lines, cur, curlen = [], [], 0
    for k in keys:
        plain = "● " + FLAG_TEXT[k]
        colored = dot(FLAG_COLORS[k]) + " " + paint(FLAG_TEXT[k], "dim")
        add = len(plain) + (3 if cur else 0)
        if cur and curlen + add > w:
            lines.append("   ".join(cur))
            cur, curlen, add = [], 0, len(plain)
        cur.append(colored)
        curlen += add
    if cur:
        lines.append("   ".join(cur))
    print("\n".join(lines))


def print_rows(rows, flags, head=None):
    """rows: [{"n": int, "flags": set, "cols": [str, ...]}]. Tabla si cabe; si no, compacto."""
    if not rows:
        return
    w = term_width()
    nw = max(len(str(r["n"])) for r in rows)
    pw = nw + 1 + len(flags) + 1
    ncol = len(rows[0]["cols"])
    allr = [r["cols"] for r in rows] + ([head] if head else [])
    widths = [max(len(c[i]) for c in allr) for i in range(ncol)]
    table = pw + sum(widths) + 2 * (ncol - 1) <= w

    def prefix(r):
        fl = "".join(dot(FLAG_COLORS[k]) if k in r["flags"] else " " for k in flags)
        return f"{r['n']:>{nw}} " + fl + " "

    if table:
        if head:
            print(" " * pw + paint("  ".join(h.ljust(widths[i])
                                             for i, h in enumerate(head)).rstrip(), "dim"))
        for r in rows:
            print(prefix(r) + "  ".join(c.ljust(widths[i])
                                        for i, c in enumerate(r["cols"])).rstrip())
    else:
        for r in rows:
            text = " · ".join(c for c in r["cols"] if c)
            lines = textwrap.wrap(text, max(8, w - pw)) or [""]
            print(prefix(r) + lines[0])
            for ln in lines[1:]:
                print(" " * pw + ln)


def drain_pending_input(max_wait=0.08):
    """Descarta bytes ya pendientes en stdin (Enter residual al abrir desde Atajos).
    No cambia el modo del terminal: solo lee lo que ya está en el buffer."""
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


def ask_line(prompt):
    """input() robusto ante Enter fantasma (Atajos / a-Shell).
    1) Drena el buffer de stdin para no consumir un Enter residual como respuesta.
    2) Si aun así llega vacío en < PHANTOM_SECS, vuelve a pedir una sola vez.
    No toca el modo del terminal (cambiarlo congelaba a-Shell)."""
    drain_pending_input()
    t0 = time.time()
    r = input(prompt)
    if not r.strip() and time.time() - t0 < PHANTOM_SECS:
        # Segunda oportunidad: el prompt ya se imprimió; input() lo vuelve a mostrar
        # en una línea nueva tras el Enter fantasma.
        r = input(prompt)
    return r


BAR_FILL, BAR_EMPTY = "█", "░"


def speed_text(v):
    """Velocidad de bajada con el mismo formato en todas las barras."""
    return f"↓ {human_size(v)}/s"


class Bar:
    """Barra de una sola línea, redibujada en su sitio por un hilo (≈7 fps).
    Sin porcentaje conocido muestra una barra que rebota con el tiempo."""

    def __init__(self):
        self.lock = threading.Lock()
        self.th = None
        self.run = False
        self.live = sys.stdout.isatty() and not DEBUG
        self.label, self.pct, self.tail = "", None, ""
        self.indet, self.hold, self.t0, self.last_len = True, 0.0, 0.0, 0
        self.wpaths, self.wtotal, self.wsamp, self.wspeed = [], 0, None, None
        self.hook_t, self.last_draw = 0.0, 0.0
        self.final_tail = ""

    def start(self, label, indeterminate=True, tail=""):
        self.stop()
        with self.lock:
            self.label, self.pct, self.tail = label, None, tail
            self.indet, self.hold, self.t0 = indeterminate, 0.0, time.time()
            self.wpaths, self.wtotal, self.wsamp, self.wspeed = [], 0, None, None
            self.hook_t = 0.0
            self.final_tail = ""
        if not self.live:
            m_info(label + "...")
            return
        global ACTIVE_BAR
        ACTIVE_BAR = self
        self.run = True
        self.th = threading.Thread(target=self._loop, daemon=True)
        self.th.start()

    def set(self, label=None, pct=None, tail=None, indeterminate=None):
        with self.lock:
            if label is not None:
                self.label = label
            if tail is not None:
                self.tail = tail
            if pct is not None:
                self.indet = False
                if self.pct is not None and pct < self.pct - 0.05:
                    self.hold = time.time() + 1.5      # yt-dlp retrocedió: se ignora
                else:
                    self.pct = pct
            if indeterminate is not None:
                self.indet = indeterminate

    def stop(self, msg=None, level="ok"):
        global ACTIVE_BAR
        if self.th:
            self.run = False
            self.th.join(timeout=1)
            self.th = None
            with self.lock:
                sys.stdout.write("\r" + " " * self.last_len + "\r")
                sys.stdout.flush()
                self.last_len = 0
        if ACTIVE_BAR is self:
            ACTIVE_BAR = None
        if msg:
            {"ok": m_ok, "warn": m_warn, "info": m_info, "err": m_err}[level](msg)

    def done(self, min_secs=0.0):
        """Congela la barra como línea final y pasa a la siguiente línea.
        Si duró menos de min_secs solo se borra."""
        was_live = self.th is not None
        elapsed = time.time() - self.t0
        with self.lock:
            label, ftail = self.label, self.final_tail
        self.stop()
        if elapsed < min_secs:
            return
        if not was_live:
            m_ok(f"{label}: listo" + (f" ({ftail})" if ftail else ""))
            return
        line, _ = self._frame(final=True)
        sys.stdout.write("\r" + nowrap(line) + "\n")
        sys.stdout.flush()

    def _frame(self, final=False):
        w = max(20, safe_width() - 2)
        now = time.time()
        with self.lock:
            label, pct, tail = self.label, self.pct, self.tail
            indet, holding = self.indet or self.pct is None, now < self.hold
        if final:
            d, tail = dot("green"), self.final_tail
            if not indet:
                pct = 100.0
        else:
            d = dot("yellow" if holding else "green") if int(now * 2) % 2 == 0 else " "
        label = label[:max(8, w // 2)]
        if indet:
            el = int((self.t0 and now - self.t0) or 0)
            base = f"{el // 60:02d}:{el % 60:02d}"
        else:
            base = f"{pct:5.1f}%"
        # Siempre se intenta dibujar la barra (mín. MINBAR): primero se recorta
        # el ETA y por último la velocidad; antes de quitar la velocidad se acorta
        # el nombre (hasta 6 letras) para que se vea también en pantallas angostas.
        MINBAR = 8
        segs = [x for x in re.split(r"\s{2,}", tail.strip()) if x] if tail else []
        cands = ([base + "  " + "  ".join(segs[:k]) for k in range(len(segs), 0, -1)]
                 + [base])
        t = cands[-1]
        for c in cands:
            if w - (min(len(label), 6) + 3) - len(c) - 3 >= MINBAR:
                t = c
                break
        pre = len(label) + 3
        bar_w = w - pre - len(t) - 3
        if bar_w < MINBAR and len(label) > 6:
            keep = max(6, len(label) - (MINBAR - bar_w))
            label = label[:keep - 1] + "…"
            pre = len(label) + 3
            bar_w = w - pre - len(t) - 3
        if bar_w >= 8:
            if indet and final:
                bar = paint(BAR_FILL * bar_w, "green")
            elif indet:
                seg = max(3, bar_w // 5)
                span = bar_w - seg
                period = max(1, 2 * span)
                k = int(now * 8) % period
                pos = k if k <= span else period - k
                bar = (paint(BAR_EMPTY * pos, "dim") + paint(BAR_FILL * seg, "cyan")
                       + paint(BAR_EMPTY * (bar_w - seg - pos), "dim"))
            else:
                f = int(bar_w * min(100.0, pct) / 100)
                bar = paint(BAR_FILL * f, "green") + paint(BAR_EMPTY * (bar_w - f), "dim")
            return f"{d} {label} [{bar}] {t}", pre + bar_w + 3 + len(t)
        t = t[:max(0, w - pre)]
        return f"{d} {label} {t}", pre + len(t)

    def reset(self, label=None):
        """Reinicia la barra en modo indeterminado (otro intento / otra fase)."""
        with self.lock:
            if label is not None:
                self.label = label
            self.pct, self.tail, self.indet = None, "", True
            self.final_tail = ""
            self.hold, self.t0 = 0.0, time.time()

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
            self.set(pct=pct, tail=tail)
        else:
            self.set(tail=tail, indeterminate=True)

    def _draw(self):
        line, vis = self._frame()
        with self.lock:
            pad = max(0, self.last_len - vis)
            sys.stdout.write("\r" + nowrap(line + " " * pad) + "\r")
            sys.stdout.flush()
            self.last_len = vis
            self.last_draw = time.time()

    def kick(self):
        """Redibuja desde el hilo principal (al llegar un aviso de yt-dlp)."""
        if self.th and time.time() - self.last_draw > 0.12:
            self._draw()

    def _loop(self):
        while self.run:
            self._poll()
            self._draw()
            time.sleep(0.14)


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
    info = d.get("info_dict") or {}
    if has(info.get("vcodec")):
        return res_label(info) if (info.get("height") or info.get("resolution")) else "Video"
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
        self.bar = Bar()
        self.key = None
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
                    b.set(label=lbl)
                else:
                    b.start(lbl)
                self.key = key
                self._reset_speed()
                if self.resumed:
                    self._base_b = d.get("downloaded_bytes") or 0
                fn = d.get("filename") or ""
                b.watch([d.get("tmpfilename"), fn + ".part" if fn else None, fn],
                        (d.get("info_dict") or {}).get("filesize")
                        or (d.get("info_dict") or {}).get("filesize_approx") or 0)
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
            tail = "  ".join(parts)
            if pct is not None:
                b.hook_t = time.time()
                b.set(pct=pct, tail=tail)
            else:
                b.set(tail=tail)
            b.kick()
        elif st == "finished" and self.key is not None and key == self.key:
            b.watch([], 0)
            size = d.get("total_bytes") or d.get("downloaded_bytes") or self._maxb
            if self._base_b and size - self._base_b > 0:
                size -= self._base_b
            secs = d.get("elapsed") or (time.time() - self._t0)
            if size and secs and secs >= 0.05:
                with b.lock:
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

    def abort(self):
        self.bar.stop()


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


def timed_input(prompt, seconds=WAIT_SECONDS):
    """Cuenta regresiva. Devuelve None si vence sin escribir nada; si el usuario
    empieza a escribir, cancela la cuenta y devuelve la línea completa.
    La línea se edita a mano y el terminal NO vuelve al modo normal a mitad
    (cambiar de modo es lo que congelaba a-Shell)."""
    if not countdown_supported():
        return ask_line(prompt)
    drain_pending_input()
    try:
        keys = _WinKeys() if os.name == "nt" else _PosixKeys()
    except Exception as _ign:
        ignore("timed_input", _ign)
        return ask_line(prompt)

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
                    sys.stdout.write(CLR + prompt + paint("sin respuesta", "dim") + "\n")
                    sys.stdout.flush()
                    return None
                secs = int(left) + 1
                nb = max(0, min(20, safe_width() - len(prompt) - len(str(secs)) - 6))
                f = int(nb * left / seconds) if nb else 0
                if (f, secs) != shown:
                    shown = (f, secs)
                    cd = (f"[{paint(BAR_FILL * f, 'cyan')}{paint(BAR_EMPTY * (nb - f), 'dim')}] "
                          if nb >= 4 else "")
                    sys.stdout.write(CLR + nowrap(prompt + cd + paint(f"{secs}s", "dim")))
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
                    if not buf and time.time() - t_start < PHANTOM_SECS:
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


def ask_yn(prompt, default=True, seconds=False):
    """Pregunta s/n y la repite hasta recibir una respuesta válida.
    seconds=False: ask_line; seconds=None: timed_input sin cuenta; número: con cuenta.
    Devuelve True/False, o None si venció la cuenta regresiva.
    EOFError/KeyboardInterrupt se propagan a quien llama."""
    while True:
        r = ask_line(prompt) if seconds is False else timed_input(prompt, seconds)
        if r is None:
            return None
        v = parse_yn(r, default)
        if v is not None:
            return v
        m_warn("Respuesta inválida: escribe s o n.")


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
    if not n:
        return "?"
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f}{u}" if u == "B" else f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}TB"


def ffmpeg_available():
    try:
        from yt_dlp.postprocessor import FFmpegPostProcessor
        if FFmpegPostProcessor().available:
            return True
    except Exception as _ign:
        ignore("ffmpeg_available", _ign)
    return bool(shutil.which("ffmpeg"))


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
VIDEO_HEAD = ["Res", "Fmt", "Códec", "Audio", "Tamaño"]
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
                     "con audio" if has(f.get("acodec")) else "sin audio",
                     human_size(f.get("filesize") or f.get("filesize_approx"))]}


def auto_best(audios, videos, orig_ids, can_merge):
    if videos:
        apple = [f for f in videos if apple_video(f)]
        if not apple:
            m_warn(f"No hay video compatible con {PLAT_LABEL}; se usará el mejor disponible.")
            apple = videos
        if not can_merge:
            with_audio = [f for f in apple if has(f.get("acodec"))]
            if with_audio:
                apple = with_audio
            else:
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
    header("PISTA PREDETERMINADA")
    m_info("Se detectaron varios idiomas.")
    legend(["apple", "orig"])
    print_rows([track_row(i, t) for i, t in enumerate(tracks, 1)], ["apple", "orig"], TRACK_HEAD)
    hint = "Número de la pista · Enter = original"
    if countdown_supported():
        hint += f" · sin respuesta en {WAIT_SECONDS} s se usa la original"
    note(hint)
    while True:
        try:
            raw = timed_input("▸ ")
        except (EOFError, KeyboardInterrupt):
            return original, True
        if raw is None:
            m_info("Sin respuesta: se usa la pista original.")
            return original, True
        raw = raw.strip()
        if not raw:
            return original, False
        if raw.isdigit() and 1 <= int(raw) <= len(tracks):
            chosen = tracks[int(raw) - 1]
            m_ok(f"Predeterminada: {chosen['lang']} · {track_label(chosen)}")
            return chosen, False
        m_warn(f"Opción inválida: escribe un número del 1 al {len(tracks)} o Enter.")


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
    header("PISTAS ADICIONALES")
    legend(["apple", "orig"])
    print_rows([track_row(i, t) for i, t in enumerate(others, 1)], ["apple", "orig"], TRACK_HEAD)
    note("Números separados por espacio (ej. 1 2 4) · Enter = todas")
    while True:
        try:
            raw = timed_input("▸ ", None).strip()
        except (EOFError, KeyboardInterrupt):
            return [primary]
        if not raw:
            chosen = others
            break
        toks = [x for x in re.split(r"[\s,]+", raw) if x]
        bad = [x for x in toks if not (x.isdigit() and 1 <= int(x) <= len(others))]
        if bad:
            m_warn(f"Opción inválida: {' '.join(bad)} (usa números del 1 al {len(others)}).")
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
            sys.stdout.write(paint(chunk, "dim"))
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
                    bar.set(pct=min(99.9, secs / duration * 100), tail="  ".join(parts))
                else:
                    if speed:
                        parts.append(f"{speed:.1f}x")
                    parts.append(f"t={int(secs) // 60:02d}:{int(secs) % 60:02d}")
                    bar.set(tail="  ".join(parts), indeterminate=True)
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
    return {"ext": ext, "cur": cur or "?",
            "vsrc": _short(vcodec) if v is not None else None,
            "venc": venc,
            "hvc": v is not None and not venc and vcodec.startswith(HEVC_CODEC),
            "vbr": int(min(30000, max(500, vbr))),
            "asrc": [_short(f.get("acodec")) for f in auds], "aenc": aenc,
            "abr": 256 if any(abr_of(f) >= 200 for f in auds) else 192,
            "labels": [track_label(t) for t in selected] if (selected and v is not None) else [],
            "remux": remux}


def plan_summary(plan):
    parts = []
    if plan["venc"]:
        parts.append(f"video {plan['vsrc']} → HEVC")
    enc = sorted({s for s, e in zip(plan["asrc"], plan["aenc"]) if e})
    if enc:
        parts.append(f"audio {'/'.join(enc)} → AAC")
    if plan["remux"]:
        parts.append(f"contenedor {plan['cur']} → {plan['ext']}")
    return " · ".join(parts) or f"contenedor → {plan['ext']}"


def video_encoder_attempts(plan):
    """[(códec resultante, opciones)] a probar en orden; la primera que funcione se queda."""
    if not plan["venc"]:
        return [(None, ["-c:v", "copy"] + (["-tag:v", "hvc1"] if plan["hvc"] else []))]
    b = f"{plan['vbr']}k"
    return [("hevc", ["-c:v", "hevc_videotoolbox", "-b:v", b, "-allow_sw", "1",
                      "-tag:v", "hvc1", "-pix_fmt", "yuv420p"]),
            ("hevc", ["-c:v", "libx265", "-preset", "veryfast", "-crf", "26",
                      "-tag:v", "hvc1", "-pix_fmt", "yuv420p"]),
            ("h264", ["-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                      "-pix_fmt", "yuv420p"])]


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


def apple_convert_file(pp, path, plan, dur, bar, out_path):
    """Convierte path → out_path probando los encoders en orden. Devuelve el
    códec de video usado (None si no hubo recodificación) o lanza RuntimeError."""
    root, ext = os.path.splitext(out_path)
    tmp = root + ".apple" + ext
    vsets = video_encoder_attempts(plan) if plan["vsrc"] is not None else [(None, [])]
    err, used, ok = None, None, False
    for vcodec, vopts in vsets:
        try:
            aopts = apple_ffmpeg_opts(plan, vopts)
            dbg("intento de conversión", {"video": vcodec, "opciones": aopts})
            if bar is not None:
                bar.reset(f"Conv. {vcodec.upper()}" if vcodec else "Conv. audio")
                ffmpeg_progress(pp, path, tmp, aopts, dur, bar)
            else:
                pp.run_ffmpeg(path, tmp, aopts)
            if os.path.isfile(tmp) and os.path.getsize(tmp) > 0:
                used, ok = vcodec, True
                break
            err = "archivo vacío"
        except Exception as e:
            err = e
            dbg("intento fallido", {"video": vcodec, "error": str(e)[-300:]})
        if os.path.exists(tmp):
            os.remove(tmp)
    if not ok:
        raise RuntimeError(str(err))
    os.replace(tmp, out_path)
    return used


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
            state.update(path=dest, venc=plan["venc"], vcodec=used,
                         aenc=list(plan["aenc"]))
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
        deliver(old_file, title)
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
    bar = Bar()
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
    m_ok(f"Convertido a {plan['ext'].upper()} compatible con Apple"
         + (f" ({used.upper()})" if used else ""))
    conv = {"venc": plan["venc"], "vcodec": used, "aenc": list(plan["aenc"])}
    index[key] = {"file": os.path.basename(final), "title": title,
                  "date": int(time.time()), "version": VERSION,
                  "meta": build_meta(kind, fmt, fmt_id, selected, orig_ids, final, conv)}
    try:
        save_json(INDEX_FILE, index)
    except Exception as e:
        m_warn(f"No se pudo guardar el índice: {e}")
    deliver(final, title)
    return True


def ask_apple_convert(plan, can_merge):
    """Avisa de que no es nativo en Apple y pregunta. Devuelve el plan o None."""
    clear_screen()
    header("COMPATIBILIDAD APPLE")
    m_warn("Este resultado no es compatible con Apple.")
    kv("Conversión", plan_summary(plan))
    if not can_merge:
        m_info("No hay ffmpeg para convertir; se descargará tal cual.")
        return None
    if plan["venc"]:
        note("Recodificar el video a HEVC puede tardar bastante en el iPhone.")
    if countdown_supported():
        note(f"Enter = convertir · sin respuesta en {WAIT_SECONDS} s se convierte")
    try:
        # Mismo lector que las preguntas previas (cbreak): input() tras ellas
        # dejaba congelado a-Shell cuando había varios idiomas.
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
        out.append(FILES_DIR)       # 0.5.0 en Android guardaba aquí
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


def build_meta(kind, fmt, fmt_id, selected, orig_ids, final, conv=None):
    meta = {"kind": "video" if kind == "v" else "audio",
            "container": os.path.splitext(final)[1].lstrip("."),
            "format_id": fmt_id,
            "video": None,
            "tracks": []}
    if kind == "v":
        meta["video"] = {"res": res_label(fmt),
                         "codec": (fmt.get("vcodec") or "?").split(".")[0],
                         "apple": apple_video(fmt)}
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
    if conv:
        meta["converted"] = True
        if meta["video"]:
            if conv.get("venc"):
                meta["video"]["codec"] = conv.get("vcodec") or "hevc"
            meta["video"]["apple"] = True
        aenc = conv.get("aenc") or []
        for i, t in enumerate(meta["tracks"]):
            if i < len(aenc) and aenc[i]:
                t["codec"] = "aac"
            t["apple"] = True
    return meta


def show_existing(path, entry):
    try:
        size = os.path.getsize(path)
    except OSError as _ign:
        ignore("show_existing", _ign)
        size = 0
    when = entry.get("date")
    when_s = time.strftime("%Y-%m-%d %H:%M", time.localtime(when)) if when else "?"
    header("YA DESCARGADO")
    kv("Archivo", os.path.basename(path))
    kv("Tamaño", human_size(size))
    kv("Fecha", when_s)
    kv("Versión", f"v{entry.get('version', '?')}")
    meta = entry.get("meta")
    if not meta:
        kv("Contenedor", os.path.splitext(path)[1].lstrip("."))
        m_info("Sin datos técnicos: descargado con una versión anterior.")
        return
    kv("Tipo", meta.get("kind"))
    kv("Contenedor", meta.get("container"))
    if meta.get("converted"):
        kv("Conversión", "a compatible Apple", flag="apple")
    v = meta.get("video")
    if v:
        kv("Video", f"{v.get('res')} · {v.get('codec')}", flag="apple" if v.get("apple") else None)
    tracks = meta.get("tracks") or []
    if not tracks:
        kv("Audio", "sin pistas de audio")
        return
    # Pista predeterminada (la usada) e idioma, siempre visibles
    primary = next((t for t in tracks if t.get("default")), tracks[0])
    lang = primary.get("lang") or "und"
    label = primary.get("label") or lang
    codec = str(primary.get("codec") or "?")
    if primary.get("abr"):
        codec += f" {primary['abr']}k"
    flags_note = []
    if primary.get("original"):
        flags_note.append("original")
    if primary.get("apple"):
        flags_note.append(PLAT_LABEL)
    extra = f" · {' · '.join(flags_note)}" if flags_note else ""
    kv("Pista usada", f"{label}{extra}", flag="default")
    kv("Idioma", lang)
    if len(tracks) == 1:
        kv("Códec audio", codec, flag="apple" if primary.get("apple") else None)
    else:
        kv("Audio", f"{len(tracks)} pista(s) · predeterminada: {lang}")
        rows = []
        for i, t in enumerate(tracks, 1):
            fl = set()
            if t.get("apple"):
                fl.add("apple")
            if t.get("original"):
                fl.add("orig")
            if t.get("default"):
                fl.add("default")
            c = str(t.get("codec") or "?") + (f" {t['abr']}k" if t.get("abr") else "")
            rows.append({"n": i, "flags": fl,
                         "cols": [str(t.get("lang") or "und"), str(t.get("label") or ""), c]})
        print()
        legend(["apple", "orig", "default"])
        print_rows(rows, ["apple", "orig", "default"], ["Idioma", "Pista", "Códec"])


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
            if ask_yn("¿Usarlo? (S/n) ▸ ", default=True):
                return clip
        except (EOFError, KeyboardInterrupt):
            return None
    last = load_json(LAST_FILE).get("link")
    if last:
        kv("Último enlace", last)
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


def fetch_remote_script(timeout=5):
    """Texto del dlpy.py del repositorio, o None si falla o no es un script válido."""
    import urllib.request
    req = urllib.request.Request(UPDATE_URL, headers={
        "User-Agent": "DLpy-updater", "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(UPDATE_MAX_BYTES + 1)
        if len(raw) > UPDATE_MAX_BYTES:
            return None
        text = raw.decode("utf-8").replace("\r\n", "\n")
        if not remote_script_version(text):
            return None
        compile(text, "dlpy.py", "exec")          # descarga truncada o dañada
        return text
    except Exception as _ign:
        ignore("fetch_remote_script", _ign)
        return None


def check_update(force=False):
    """Si el repositorio tiene una versión más nueva, pregunta, la instala y la ejecuta.

    Devuelve True si se ejecutó la versión nueva (quien llama debe terminar)."""
    text = fetch_remote_script(timeout=8 if force else 5)
    remote = remote_script_version(text)
    if not remote:
        if force:
            m_warn("No se pudo consultar la última versión (sin red o enlace inválido).")
        return False
    if vtuple(remote) <= vtuple(VERSION):
        if force:
            m_ok(f"Ya tienes la última versión (v{VERSION}).")
        return False
    if not force and load_json(UPDATE_STATE_FILE).get("declined") == remote:
        return False
    m_info(f"Hay una versión nueva de DLpy: {VERSION} → {remote}")
    if not ask(f"¿Instalar la {remote} y ejecutarla ahora?"):
        try:
            save_json(UPDATE_STATE_FILE, {"declined": remote})
        except Exception as _ign:
            ignore("check_update", _ign)
        note("No se vuelve a preguntar por esta versión; con --actualizar la instalas.")
        return False
    try:
        write_text(SCRIPT_PATH, text)
    except Exception as e:
        m_warn(f"No se pudo instalar la actualización: {e}")
        return False
    m_ok(f"DLpy {remote} instalada.")
    import runpy
    runpy.run_path(SCRIPT_PATH, run_name="__main__")   # termina con SystemExit
    return True


def pip_install(pip_name):
    m_info(f"Instalando {pip_name}...")
    if IS_ANDROID:
        cmd = f"{shlex.quote(sys.executable)} -m pip install -U {shlex.quote(pip_name)} --no-deps"
        if os.system(cmd) != 0:            # Termux reciente puede exigir esta bandera
            os.system(cmd + " --break-system-packages")
    elif IS_IOS:
        os.system(f"pip install -U {shlex.quote(pip_name)} --no-deps")
    else:
        # Escritorio: sin shell (vale en Windows) y con reintento para PEP 668
        # (Linux/Homebrew marcan el Python del sistema como «externally managed»).
        import subprocess
        base = [sys.executable or "python3", "-m", "pip", "install", "-U", pip_name]
        for extra in ([], ["--break-system-packages"]):
            try:
                if subprocess.call(base + extra) == 0:
                    break
            except OSError as _ign:
                ignore("pip_install", _ign)
                break
    refresh_paths()


def ffmpeg_install_cmd():
    """Orden que instala ffmpeg con el gestor de este sistema, o None si no hay."""
    which = shutil.which
    if IS_ANDROID:
        return ["pkg", "install", "-y", "ffmpeg"] if which("pkg") else None
    if IS_MAC:
        return ["brew", "install", "ffmpeg"] if which("brew") else None
    if IS_WINDOWS:
        return (["winget", "install", "--id", "Gyan.FFmpeg", "-e",
                 "--accept-package-agreements", "--accept-source-agreements"]
                if which("winget") else None)
    if IS_LINUX:
        root = hasattr(os, "geteuid") and os.geteuid() == 0
        sudo = [] if root else (["sudo"] if which("sudo") else None)
        if sudo is None:
            return None
        for exe, args in (("apt-get", ["apt-get", "install", "-y", "ffmpeg"]),
                          ("dnf", ["dnf", "install", "-y", "ffmpeg-free"]),
                          ("pacman", ["pacman", "-S", "--noconfirm", "ffmpeg"]),
                          ("zypper", ["zypper", "--non-interactive", "install", "ffmpeg"]),
                          ("apk", ["apk", "add", "ffmpeg"])):
            if which(exe):
                return sudo + args
    return None


def ffmpeg_hint():
    return {"android": "pkg install ffmpeg", "macos": "brew install ffmpeg",
            "windows": "winget install Gyan.FFmpeg  (o https://ffmpeg.org/download.html)",
            "linux": "sudo apt install ffmpeg  (o el gestor de tu distribución)",
            "ios": "a-Shell lo incluye"}[PLATFORM]


def ensure_ffmpeg():
    """Si falta ffmpeg ofrece instalarlo con el gestor del sistema (no en iOS:
    a-Shell lo trae integrado)."""
    if IS_IOS or shutil.which("ffmpeg"):
        return
    m_warn("Falta ffmpeg (hace falta para unir audio y video).")
    cmd = ffmpeg_install_cmd()
    if cmd and ask(f"¿Instalar ffmpeg con «{' '.join(cmd)}»? (S/n) ▸ "):
        import subprocess
        try:
            subprocess.call(cmd)
        except OSError as e:
            m_warn(f"No se pudo lanzar el instalador: {e}")
        if shutil.which("ffmpeg"):
            m_ok("ffmpeg instalado")
            return
        if IS_WINDOWS:
            note("Si winget terminó bien, cierra y abre la terminal para que Windows encuentre ffmpeg.")
        m_warn("No se pudo instalar ffmpeg.")
    note("Instálalo con: " + ffmpeg_hint())


def ask(msg, default=True):
    try:
        return bool(ask_yn(msg, default))
    except (EOFError, KeyboardInterrupt):
        return False


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


def check_js_components():
    """Si hay runtime de JavaScript, deja instalado yt-dlp-ejs en la versión que pide
    yt-dlp. Sin runtime no hace nada (instalarlo sería inútil)."""
    if not ytdlp_needs_js() or not js_runtime():
        return
    pin = ejs_pin()
    if not pin:
        return
    want = pin.split("==", 1)[1] if "==" in pin else None
    cur = pkg_version("yt-dlp-ejs") if is_installed("yt_dlp_ejs") else None
    if cur and (not want or cur == want):
        return
    m_info("YouTube necesita yt-dlp-ejs" + (f" {want}" if want else "")
           + (f" (tienes {cur})" if cur else "") + ".")
    if ask(f"¿Instalar {pin}? (S/n) ▸ "):
        pip_install(pin)
        if is_installed("yt_dlp_ejs"):
            m_ok(f"yt-dlp-ejs {pkg_version('yt-dlp-ejs') or ''} instalado")
        else:
            m_warn("No se pudo instalar yt-dlp-ejs; YouTube puede mostrar menos formatos.")


def warn_youtube_js(link):
    """Aviso único al pegar un enlace de YouTube si falta el runtime de JavaScript."""
    if not _host_is(_host(link), ("youtube.com", "youtu.be", "youtube-nocookie.com")):
        return
    if not ytdlp_needs_js() or js_runtime():
        return
    m_warn("YouTube necesita un runtime de JavaScript y no hay ninguno: pueden faltar formatos.")
    note("Instálalo con: " + JS_INSTALL_HINT[PLATFORM])


def check_dependencies():
    """Revisa instalación y actualizaciones. Devuelve False si falta una obligatoria."""
    for pip_name, module, required in DEPENDENCIES:
        if not is_installed(module):
            m_warn(f"Falta la dependencia: {pip_name}" + (" (obligatoria)" if required else ""))
            wanted = ask(f"¿Instalar {pip_name}? (S/n) ▸ ")
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
            m_ok(f"{pip_name} {pkg_version(pip_name) or ''} instalado")
            continue

        cur = pkg_version(pip_name)
        cbar = Bar()
        cbar.start(f"Comprobando {pip_name}")
        try:
            lat = latest_version(pip_name)
        finally:
            cbar.stop()
        if cur and lat and vtuple(lat) > vtuple(cur):
            m_info(f"Actualización de {pip_name}: {cur} → {lat}")
            if ask(f"¿Actualizar {pip_name}? (S/n) ▸ "):
                pip_install(pip_name)
                m_ok(f"{pip_name} {pkg_version(pip_name) or '?'}")
        else:
            m_ok(f"{pip_name} {cur or ''}")
    ensure_ffmpeg()
    check_js_components()
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


def extract_changelog():
    """Saca el changelog del .py, lo agrega a changelog.md y lo quita del script."""
    try:
        src = read_text(SCRIPT_PATH)
    except Exception as _ign:
        ignore("extract_changelog", _ign)
        return
    m = CL_RE.search(src)
    if not m:
        if CL_OPEN_RE.search(src):
            m_warn("El changelog del script no tiene marcador de fin "
                   "(# ==== FIN CHANGELOG ====); no se tocó.")
        return
    lines = []
    for ln in m.group(1).splitlines():
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
        stripped = src[:m.start()] + src[m.end():]
        write_text(SCRIPT_PATH, stripped)
        m_ok(f"Changelog guardado en {CHANGELOG_FILE}"
             + (f" (+{len(added)} versión/es nueva/s)" if added else ""))
    except Exception as e:
        m_warn(f"Changelog guardado, pero no se pudo limpiar el script: {e}")


def changelog_pending():
    """True si el .py todavía trae su bloque de changelog por extraer."""
    try:
        return bool(CL_RE.search(read_text(SCRIPT_PATH)))
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


def check_version():
    migrate_legacy_dlpy_data()
    tidy_data()
    state = load_json(VERSION_FILE)
    stored = state.get("version")

    if stored == VERSION:
        if not os.path.isfile(SNAPSHOT_FILE):
            save_snapshot()
            save_json(VERSION_FILE, {"version": VERSION, "snapshot_version": VERSION})
        if changelog_pending():          # misma versión pero el .py trae changelog
            extract_changelog()
        publish_changelog_to_files()
        return True

    # ── Actualización (o primera instalación) ──
    prev = stored or "0.0.0"
    if stored:
        m_info(f"Actualización detectada: {stored} → {VERSION}")
    if not archive_previous(prev, state.get("snapshot_version"), announce=bool(stored)):
        return False

    save_snapshot()          # copia completa (con changelog) para futuros backups
    extract_changelog()      # changelog.md y limpieza del .py
    save_json(VERSION_FILE, {"version": VERSION, "snapshot_version": VERSION})
    return True


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


# ───────────────────── Entrega al atajo ─────────────────────
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
            m_ok("Abriendo en Android...")
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
        m_ok("Abriendo la carpeta..." if action == "share" else "Abriendo con la app por defecto...")
    else:
        m_info("No se abrió solo" + (f": {why}" if why else "") + ".")


def deliver(final, title):
    if IS_ANDROID:
        return deliver_android(final, title)
    if IS_DESKTOP:
        return deliver_desktop(final, title)
    path = unique_path(final)
    m_info(f"Enviando a {SHORTCUT_NAME}...")
    dbg("entrega", {"origen": final, "copia": path, "titulo": title})
    payload = json.dumps({"file_path": path, "file_title": title}, ensure_ascii=False)
    url = ("shortcuts://run-shortcut?name=" + urllib.parse.quote(SHORTCUT_NAME)
           + "&input=text&text=" + urllib.parse.quote(payload, safe=""))
    os.system("open " + shlex.quote(url))


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
    m_warn("Reanalizando el enlace...")
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
    check("etiqueta audio idioma", stream_label({"info_dict": {"vcodec": "none", "language": "es-US"}}), "es-US")
    check("etiqueta audio sin idioma", stream_label({"info_dict": {"vcodec": "none"}}), "Audio")
    check("yes vacío/def", yes("", False), False)
    check("yes s", yes(" S "), True)
    check("yes n", yes("n"), False)
    check("parse_yn vacío/def", parse_yn("", False), False)
    check("parse_yn sí", parse_yn(" Sí "), True)
    check("parse_yn no", parse_yn("NO"), False)
    check("parse_yn inválido", parse_yn("x"), None)
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
    print(title_bar(f" DLpy v{VERSION}", "sistema ", "1;30;106"))
    print(f"Corre en: {platform_name()} · {machine_name()} · Python {sys.version.split()[0]}")
    print(f"Modo: {PLATFORM}" + (" (forzado con DLPY_PLATFORM)" if os.environ.get("DLPY_PLATFORM") else ""))
    mark = {"ok": paint("✓", "green"), "no": paint("✗", "red"),
            "part": paint("~", "yellow"), "na": paint("–", "dim")}
    counts = {"ok": 0, "no": 0, "part": 0, "na": 0}
    for name, st, why in capabilities():
        counts[st] += 1
        print()
        print(f"{mark[st]} {paint(name, 'bold')}")
        for ln in textwrap.wrap(why, max(20, term_width() - 3)):
            print("  " + paint(ln, "dim"))
    print()
    print(f"{counts['ok']} ✓ · {counts['part']} ~ · {counts['no']} ✗ · {counts['na']} – (no aplica)")
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
        print("--instalar-android solo aplica en Termux (Android).")
        return 1
    st, path = write_url_opener(force=True)
    if st.startswith("error"):
        print(f"No se pudo crear {path}: {st[7:]}")
        return 1
    print(f"Listo: {path}")
    print("Comparte un enlace desde cualquier app a Termux y se abrirá DLpy con él.")
    if not SHARED_OK:
        print("Falta el almacenamiento compartido: ejecuta termux-setup-storage.")
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
    if "--actualizar" in sys.argv[1:]:
        check_update(force=True)
        return 0
    if not os.environ.get("DLPY_NO_UPDATE") and check_update():
        return 0
    if not check_version():
        return 1
    if not check_dependencies():
        return 1
    cleanup_internal()
    if DEBUG:
        try:
            env_cols = shutil.get_terminal_size((0, 0)).columns
        except Exception as _ign:
            ignore("main", _ign)
            env_cols = 0
        m_info(f"Ancho del terminal: variable={env_cols or '?'} · barras={safe_width()}")
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
        save_json(LAST_FILE, {"link": link, "date": int(time.time())})
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
        show_title(title)
        show_existing(old_file, old_entry)
        print()
        try:
            de_nuevo = ask_yn("¿Descargar de nuevo con otros parámetros? (s/N) ▸ ", default=False)
        except (EOFError, KeyboardInterrupt):
            return 1
        if not de_nuevo:
            roast_done(len(index) - 1, reused=True)
            deliver(old_file, title)
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

    # 2) Listar: audio y luego video (de peor a mejor calidad)
    clear_screen()
    show_title(title)
    legend(["apple", "orig"])
    choices, n = {}, 1
    if audios:
        header("AUDIO")
        rows = []
        for f in audios:
            rows.append(audio_row(n, f, orig_ids))
            choices[n] = ("a", f)
            n += 1
        print_rows(rows, ["apple", "orig"], AUDIO_HEAD)
    if videos:
        header("VIDEO")
        rows = []
        for f in videos:
            rows.append(video_row(n, f))
            choices[n] = ("v", f)
            n += 1
        print_rows(rows, ["apple"], VIDEO_HEAD)

    # 3) Elegir
    print()
    note(f"Número de formato · b = mejor compatible {PLAT_LABEL} · q = salir (Enter no sale)")
    while True:
        try:
            raw = ask_line("▸ ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return 1
        if raw == "q":
            return 0
        if raw == "":
            continue
        if raw == "b":
            kind, fmt = auto_best(audios, videos, orig_ids, can_merge)
            break
        if raw.isdigit() and int(raw) in choices:
            kind, fmt = choices[int(raw)]
            break
        m_warn(f"Opción inválida: escribe un número del 1 al {len(choices)}, b o q.")

    dbg("elegido", {"entrada": raw, "tipo": kind, "formato": pick(fmt, FMT_KEYS)})
    roast_choice(kind, fmt)

    # 4) Armar selección de pistas
    fmt_id, merge_ext = fmt["format_id"], None
    selected = []
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
            m_ok(f"Pistas de audio a incluir: {len(selected)}")
    elif kind == "v" and multi_lang:
        m_info("Este formato ya incluye su audio; no admite pistas adicionales.")

    # 4b) Si el resultado no es nativo en Apple, ofrecer convertirlo
    plan = apple_plan(kind, fmt, selected, merge_ext)
    dbg("selección", {"fmt_id": fmt_id, "merge_ext": merge_ext,
                      "pistas": [t["fmt"].get("format_id") for t in selected]})
    dbg("plan Apple", plan if plan else "no hace falta (ya es compatible)")
    if plan:
        plan = ask_apple_convert(plan, can_merge)
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
        m_ok(f"Convertido a {plan['ext'].upper()} compatible con Apple"
             + (f" ({conv_state['vcodec'].upper()})" if conv_state.get("vcodec") else ""))

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
                                    conv_state or None)}
    dbg("índice", index[key])
    try:
        save_json(INDEX_FILE, index)
    except Exception as e:
        m_warn(f"No se pudo guardar el índice: {e}")

    roast_done(len(index) - 1)
    deliver(final, title)
    return 0


if __name__ == "__main__":
    sys.exit(main())
