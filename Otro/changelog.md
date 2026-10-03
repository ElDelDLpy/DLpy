# Changelog DLpy

## 0.7.7

- Recuperación: ahora también lista los backups internos que DLpy guarda al actualizar
  (dlpy_files/backups/<versión>/dlpy_<versión>.py), sin necesitar DLPY_DEV ni internet.
  La lista une GitHub (versions/), el repo local y esos backups, una entrada por versión
  (gana GitHub, luego el repo local, luego los backups).
- --selftest: pruebas de merge_versions y backup_versions.
- Lista de versiones (--versiones y recuperación) rehecha: una fila por versión con TODOS
  sus orígenes (GitHub, GitHub main, local, backup, instalada) y marcas: ✓ actual,
  ⬆ la que se instala al actualizar (el dlpy.py de GitHub), ✖ crasheó (siempre, también
  ×N), ≠ difiere y = idénticas. Ya no oculta la versión que falló.
- Comparación de versiones iguales: huella SHA-256 del archivo y del código SIN el
  changelog (el instalado ya no lo trae). Estados: idénticas, solo changelog, código
  distinto. GitHub se compara con el hash git de la API (sin descargar); solo descarga
  lo que difiere. Al elegir una versión muestra el diff con colores (rojo/verde).
- Si GitHub y local/backup tienen archivos DISTINTOS de la versión elegida pregunta de
  cuál instalar; si son iguales no pregunta. Si ya es idéntica a la instalada lo dice.
- Historial de fallos state/crash_log.json (versión, huella del código, error, hora;
  también los cierres inesperados). Si lo que vas a instalar o restaurar es IDÉNTICO al
  código que falló, avisa antes y pregunta (por defecto no). Misma versión pero otro
  código: lo indica sin bloquear. Vale para actualizar y para volver a una versión.
- Actualización: sigue preguntando siempre (decir que no no se recuerda). Con la misma
  versión avisa si el código instalado difiere del de GitHub.
- Solo con DLPY_DEV=1 y solo en a-Shell (iOS) copia además el snapshot actual a
  ~/Documents/dlpy.py (no si ese archivo es el propio script en ejecución). Sin DEV, o en
  otra plataforma, no lo copia.
- Una sola comparación para todo lo que habla de versiones: al buscar actualizaciones
  compara la de actualización (`main`) con la copia de versions/ en GitHub, el repo
  local, los backups y la instalada, igual que la lista (hash git y huellas del código
  sin changelog, diff con colores si difieren). Con la misma versión dice «idéntica a
  GitHub» o qué difiere; con una nueva dice si es igual a su copia de versions/.
  Tras recuperar una versión, la de GitHub con el mismo número que falló pero OTRO
  código sí se ofrece (puede estar corregida). Al arrancar avisa si la versión
  instalada difiere de su copia guardada (editada sin subir versión). DEV dice si la
  versión ya existía en versions/ con código distinto o solo otro changelog.
- --selftest: pruebas de huellas, comparación, historial de fallos y copia a Documents.

## 0.7.6

- YA DESCARGADO: si el video ya se había entregado antes (el índice guarda
  «delivered» con la hora de la última entrega) y eliges no descargar de nuevo, ahora
  pregunta «¿Abrir otra vez con Atajos? (S/n)» (en Android/escritorio «¿Abrir otra vez
  el archivo?») en vez de abrirlo directo. Si nunca se había entregado (o la entrada
  es de una versión anterior), se manda directo como siempre. Lo mismo al reutilizar
  el archivo con los mismos parámetros. El resumen muestra la línea «Entregado».
- DLPY_DEV=1 (modo desarrollo): al correr una versión nueva por primera vez copia el
  script (con su changelog) a <repo>/versions/dlpy_x.y.z.py, donde <repo> es DLPY_REPO
  o la carpeta con .git junto al script (o ~/Documents/DLpy). Solo copia: el commit y
  el push los haces tú con lg2. Si la misma versión ya existe con otro contenido guarda
  dlpy_x.y.z_<hash>.py sin pisarla. Sin DLPY_DEV no copia nada. El banner muestra «DEV»
  solo cuando está activo.
- Recuperación tras un fallo: si DLpy revienta con una excepción, o la ejecución
  anterior quedó cortada y esa versión aún no había terminado bien ninguna vez,
  consulta versions/ del repositorio de GitHub (sin internet, el repo local), lista las
  versiones y deja elegir una. La elegida se instala (la rota se guarda en
  script/crash/) y se ejecuta. También `--versiones` para listar a mano.
- Tras recuperar se anota la versión que falló (state/recovered.json): mientras GitHub
  no tenga una versión MÁS NUEVA que la que falló no se ofrece actualizar (solo una
  nota; `--actualizar` la instala igualmente). Si ya hay una más nueva, avisa como
  siempre. Al restaurar una versión más vieja ya no dice «Actualización detectada».
- Limitación: un error de sintaxis impide que el script arranque, así que no puede
  rescatarse solo (haría falta un lanzador aparte).
- --selftest: pruebas de dev_repo_dir, dev_version_target, parse_versions_listing,
  github_repo_info, parse_menu_choice, should_offer_after_abrupt,
  skip_update_after_recovery, mark_delivered y deliver_existing.

## 0.7.5

- Conversión: antes de la barra imprime «Usando VideoToolbox HEVC» / «Usando x265»
  / etc. y la barra queda genérica («Conv.» / «Remux»). Si un intento falla avisa
  y pasa al siguiente encoder.

## 0.7.4

- Actualización: si hay una versión nueva en GitHub pregunta SIEMPRE (ya no se
  guarda «rechazada» en state/update.json). Decir que no solo vale en esa
  ejecución; al siguiente arranque vuelve a salir la pregunta.
- Bits de video: se detectan solo con datos claros (bit_depth/bits o texto
  10bit/main10/… en format/format_note). HDR no asume 10 bits. Si hay ≥10 bits
  detectados y la conversión se estima lenta (> 60 s) pregunta si mantener esos
  bits o pasar a 8 (más rápido; por defecto 8). Sin detección → 8 bits.
- Barra de conversión: muestra el encoder real («Conv. VideoToolbox HEVC»,
  «Conv. x265», «Conv. x264», «Remux», «Conv. audio»).
- stream_label: si hay altura/ancho/resolución NxM se etiqueta como Video
  aunque vcodec venga vacío o «none» (HLS y sitios que no rellenan códec).
- Tras elegir formato se limpia la pantalla y se muestra un resumen «Elegido: …».
- Títulos de pistas: «Elegir pista predeterminada» y «Elegir pistas de audio
  adicional».
- YA DESCARGADO unificado: bloque compacto (archivo, video, pistas/idiomas) al
  estilo del resumen de elección, antes de «¿Descargar de nuevo…?».
- --selftest: pruebas de detect_bit_depth, stream_label con sin códec, y de que
  check_update ya no depende de declined.

## 0.7.3

- Conversión Apple: ya no pregunta si el trabajo es rápido. Sin recodificar video
  (solo remux y/o audio → AAC) se convierte solo. Con recodificación de video se
  estima el tiempo (duración × resolución × fps, ~2.5× tiempo real a 1080p30 con
  VideoToolbox) y, si queda ≤ 60 s, también se convierte sin preguntar (un clip
  corto en 4K o a pocos fps puede ser rápido). Solo pregunta cuando la estimación
  supera el minuto o no hay duración conocida. Sigue avisando qué se va a hacer.
- --selftest: pruebas de convert_is_quick.

## 0.7.2

- Preguntas s/n unificadas en un solo sitio: ask_yn (por donde pasan todas, también
  ask) arma el final de CUALQUIER pregunta con yn_prompt: quita el «(S/n)» / «(s/N)»
  / «▸» que traiga el texto y pone «(S/n) ▸ » si el valor por defecto es sí o
  «(s/N) ▸ » si es no. Así toda pregunta lo muestra siempre, la mayúscula coincide
  con lo que hace Enter y una pregunta nueva no puede olvidarlo. Las preguntas de
  elegir número («▸ ») no son s/n y no cambian.
- Ojo con las actualizaciones: la pregunta «¿Instalar la x.y.z…?» la pinta la
  versión que YA tienes instalada. Hasta que una versión con este arreglo esté en
  GitHub e instalada, la actualización seguirá preguntando con el texto de la
  versión vieja.
- --selftest: pruebas nuevas de yn_prompt.

## 0.7.1

- Actualización: si la versión local es MÁS NUEVA que la del dlpy.py de GitHub (el
  autor puede tener una sin subir) ya no dice «última versión»: muestra el aviso
  «DLpy x.y.z · versión local más reciente que la de GitHub (a.b.c)» y sigue sin
  ofrecer nada. Con la misma versión sigue saliendo «✓ última versión». La
  comparación vive en update_status (--selftest la prueba).
- Estilo de las preguntas s/n unificado: la de actualizar («¿Instalar la x.y.z y
  ejecutarla ahora?») era la única sin «(S/n) ▸ »; ahora igual que las demás.
- `--2shortcuts` pinta el mismo encabezado que el resto del script (banner con
  versión, plataforma y espacio) antes de preguntar «¿Con changelog? (s/N) ▸ ».

## 0.7.0

- `--2shortcuts` pregunta qué mandar: «¿Con changelog? (s/N)». Sin changelog (por
  defecto, también si no hay terminal) manda el dlpy.py tal como está en disco,
  que ya no trae el bloque CHANGELOG; con changelog manda el script con todo el
  historial: el propio archivo si aún lo trae, si no la copia completa que
  guarda DLpy en script/script_snapshot.py (solo si es de esta misma versión) y,
  si tampoco hay, lo reconstruye desde changelog.md en el mismo sitio y formato
  de siempre. Sin ninguna fuente de changelog no pregunta y lo avisa. Antes de
  copiar muestra qué se manda y cuánto pesa.
- Revisión de errores: sin nombres indefinidos, funciones duplicadas ni imports
  sin uso, y --selftest pasa en ios, android, macos, linux y windows. Único fallo
  encontrado y corregido: al reconstruir el changelog desde changelog.md salía una
  línea «#» de más antes de «# ==== FIN CHANGELOG ====».
- --selftest: pruebas nuevas de script_variants y changelog_block_from_md.

## 0.6.9

- `--enviar-codigo` (0.6.8) se reemplaza por `--2shortcuts` (solo iOS / a-Shell):
  manda el dlpy.py actual tal cual a tu atajo «DLpy» y sale. Sin JSON, sin copia
  en delivery y sin claves extra: el atajo recibe el texto del script como
  entrada y lo reconoce porque empieza con #!dlpy.py. También acepta
  `--2shorcuts` (sin la t) y las rayas largas que pone el teclado de iOS.
- Cómo viaja: el script se copia al portapapeles (pbcopy) y se lanza
  shortcuts://run-shortcut?name=DLpy&input=clipboard, porque el código pesa
  cientos de KB y no cabe de forma fiable en la URL. Si pbcopy falla, lo manda
  dentro de la URL (input=text) avisando. Ojo: sobrescribe el portapapeles.
- Fuera de iOS avisa de que no aplica.
- --selftest: pruebas de shortcut_clip_url, shortcut_text_url y wants_2shortcuts.

## 0.6.8

- Nuevo `--enviar-codigo` (solo iOS / a-Shell): manda el dlpy.py actual a tu atajo
  «DLpy» de Atajos y sale, igual que se entregan los videos. Hace una copia del
  script en dlpy_internal/delivery/<id>/dlpy.py (el original no se toca) y lanza
  shortcuts://run-shortcut con {"file_path", "file_title": "dlpy.py", "kind":
  "script", "version"}. El atajo sabe que es el código porque trae kind=script;
  los videos no llevan esa clave. La copia se borra sola a las 24 h como el
  resto de entregas. En Android y escritorio avisa de que no aplica.
- deliver y --enviar-codigo comparten shortcut_run_url (sin cambiar lo que ya se
  mandaba al atajo).
- --selftest: prueba nueva de shortcut_run_url.

## 0.6.7

- Revisión unificada al arrancar: la actualización de DLpy y todas las
  dependencias se comprueban SIEMPRE y cada una deja una línea con el mismo
  formato «✓ nombre versión · estado» (✓ verde si está al día; ● amarillo si
  falta o no se pudo comprobar). Antes eran silenciosas cuando todo estaba bien.
  Orden: DLpy, yt-dlp, ffmpeg, runtime de JavaScript, termux-api (solo Android),
  yt-dlp-ejs.
- Dependencias por plataforma: lo que falta del sistema se instala con UNA sola
  pregunta («¿Instalar ffmpeg, Runtime de JavaScript, termux-api con …?») y el
  gestor de cada sistema: Android → pkg (ffmpeg, nodejs, termux-api); macOS →
  brew (ffmpeg, deno); Windows → winget (Gyan.FFmpeg, DenoLand.Deno); Linux →
  apt/dnf/pacman/zypper/apk (ffmpeg, nodejs). iOS no instala nada (a-Shell trae
  ffmpeg y no hay runtime de JavaScript). El runtime solo se pide si el yt-dlp
  instalado exige JavaScript para YouTube. Android avisa además de que la app
  Termux:API (F-Droid) no se puede instalar desde el script.
- Recuerda el «no»: si rechazas instalar algo (ffmpeg, runtime, termux-api,
  yt-dlp-ejs) o actualizar yt-dlp, no vuelve a preguntar (state/deps.json; para
  yt-dlp y yt-dlp-ejs, hasta que salga otra versión). La línea sigue apareciendo
  en amarillo. Si luego lo instalas por tu cuenta, el rechazo se olvida solo.
  `--actualizar` ahora revisa también las dependencias y vuelve a preguntar lo
  rechazado.
- Corrige: al rechazar la instalación de yt-dlp el mensaje «es obligatoria» salía
  dos veces.
- --selftest: pruebas nuevas de system_install_cmds por plataforma.

## 0.6.6

- Android: al instalar una actualización desde GitHub, el código nuevo se
  guarda también en la carpeta desde la que se abrió DLpy (p. ej. Descargas),
  la que tenía antes de moverse a ~/dlpy.py. relocate_to_root recuerda esa
  ruta (DLPY_ORIGIN) al mover el script y check_update, además de actualizar
  ~/dlpy.py como siempre, escribe ahí la versión nueva (sync_origin_copy).
  Si esa carpeta ya no existe o no se puede escribir, avisa y sigue.
- Todo lo demás funciona igual: en iOS y fuera de Android no cambia nada, y
  si DLpy ya estaba en ~ (no se movió) no hay copia extra.
- --selftest: pruebas nuevas de sync_origin_copy.

## 0.6.5

- Cuarta versión de prueba de la actualización desde GitHub: no cambia el
  funcionamiento, solo sube la versión.

## 0.6.4

- Tercera versión de prueba de la actualización desde GitHub: no cambia el
  funcionamiento, solo sube la versión.

## 0.6.3

- Segunda versión de prueba de la actualización desde GitHub: no cambia el
  funcionamiento, solo sube la versión.

## 0.6.2

- Versión de prueba para comprobar la actualización desde GitHub: no cambia
  el funcionamiento, solo sube la versión.

## 0.6.1

- Actualización desde GitHub: al arrancar compara su versión con la del dlpy.py
  del repositorio ElDelDLpy/DLpy (rama main). Si hay una más nueva pregunta
  «¿Instalar la x.y.z y ejecutarla ahora?». Si aceptas, reemplaza el script y
  ejecuta la versión nueva al instante con los mismos argumentos (en el mismo
  proceso, sin exec, para que funcione también en a-Shell). En esa ejecución
  check_version archiva la versión anterior y guarda el changelog como siempre.
- Antes de reemplazar valida la descarga: empieza con #!dlpy.py, trae VERSION y
  compila sin errores. Sin red o con una respuesta inválida no avisa y sigue.
- Si dices que no, no vuelve a preguntar por esa misma versión (se guarda en
  state/update.json); cuando suba otra más nueva vuelve a preguntar.
- Nuevo `--actualizar`: consulta ahora mismo (aunque hubieras dicho que no),
  avisa si ya tienes la última y sale. DLPY_NO_UPDATE=1 desactiva la
  comprobación automática; DLPY_UPDATE_URL cambia el enlace del dlpy.py.
- --selftest: pruebas nuevas de remote_script_version.

## 0.6.0

- Modos de ejecución: además de iOS (a-Shell) y Android (Termux), DLpy corre
  ahora en Linux, macOS y Windows (WSL cuenta como Linux). detect_platform
  devuelve «ios», «android», «macos», «linux» o «windows»; antes todo lo que
  no era Android caía en el modo iOS. En iOS (a-Shell) la detección se amplía
  (APPNAME, hideKeyboard, ruta de la sandbox de iOS) para que NO se confunda con
  macOS, y el comportamiento de iOS y Android no cambia.
  DLPY_PLATFORM=ios|android|macos|linux|windows fuerza el modo.
- El banner indica en qué corre (platform_name): «a-Shell · iOS», «Termux ·
  Android», «Linux», «Linux · WSL», «macOS 14», «Windows 11»…, con la
  arquitectura y la versión de Python. Se recorta al ancho de la pantalla.
- Nuevo `--sistema`: informe de qué funciones están disponibles en este sistema
  (✓ / ✗ / ~) y el motivo de cada una, calculado con lo que realmente hay
  instalado (ffmpeg, portapapeles, notificaciones, abrir archivos…).
- Equivalencias por modo:
  · Descargas: iOS → dlpy_files; Android, Linux, macOS y Windows → carpeta
    Descargas del sistema (Linux respeta XDG_DOWNLOAD_DIR); backups y changelog
    en Descargas/DLpy; lo interno en ~/.dlpy/dlpy_internal. DLPY_DOWNLOAD_DIR
    cambia el destino.
  · Al terminar: iOS → Atajo; Android → termux-open + notificación; escritorio →
    abre el archivo con la app por defecto (xdg-open / open / os.startfile) y
    manda notificación (notify-send / osascript / globo de Windows) si existe.
    DLPY_ACTION=open|share|none (en escritorio «share» abre la carpeta;
    DLPY_ANDROID_ACTION sigue valiendo). Sin pantalla (SSH/servidor) no abre.
  · Compatibilidad: iOS y macOS → códecs nativos de Apple y conversión
    opcional (VideoToolbox); Android, Linux y Windows → «reproducible» sin
    convertir (h264/vp9/hevc/aac/opus en mp4/webm/mkv).
  · Portapapeles: Android (termux-clipboard-get), macOS (pbpaste), Linux
    (wl-paste/xclip/xsel) y Windows (Get-Clipboard) ofrecen el enlace copiado.
    En iOS es opcional (DLPY_CLIPBOARD=1) porque iOS pide permiso de pegado.
  · ffmpeg: Android → pkg; macOS → brew; Linux → apt/dnf/pacman/zypper/apk;
    Windows → winget; en cada caso pregunta antes. En iOS no se toca.
  · pip: escritorio usa «python -m pip» sin shell, reintenta con --user y
    con --break-system-packages (PEP 668); iOS y Android igual que antes.
- Windows: activa los colores ANSI de la consola, fuerza UTF-8 en la salida,
  usa msvcrt para la cuenta regresiva y para vaciar el teclado, evita nombres
  reservados (CON, NUL…) y no usa termios.
- Corrige: countdown_supported fallaba en Windows (ImportError sin capturar);
  drain_pending_input se comía la entrada cuando stdin era una tubería
  (echo s | python dlpy.py); hide_keyboard ejecutaba un comando inexistente
  fuera de iOS; pip_install usaba shlex.quote en Windows (comillas inválidas).
- YouTube (yt-dlp ≥ 2025.11.12 exige un runtime de JavaScript y el paquete
  yt-dlp-ejs en la versión exacta que fija esa versión de yt-dlp): como iOS y
  Android instalan yt-dlp con --no-deps, yt-dlp-ejs nunca se instalaba. Ahora,
  si hay un runtime de JavaScript (deno, node, bun o quickjs), DLpy lee de los
  metadatos de yt-dlp qué versión de yt-dlp-ejs pide y ofrece instalarla.
  Si el único runtime es node/bun/quickjs añade solo «--js-runtimes <rt>»
  (deno ya viene activado); no pisa DLPY_YTDLP_ARGS. Al pegar un enlace de
  YouTube sin runtime avisa y dice cómo instalarlo (Termux: pkg install nodejs).
  Otros sitios no se ven afectados. --sistema lo muestra.
- --selftest: pruebas nuevas de detect_platform por sistema, platform_name,
  safe_name con nombres reservados, desktop_downloads_dir, capabilities,
  ejs_pin y js_runtime_args.

## 0.5.4

- Android: DLpy pide solo el acceso al almacenamiento. Si falta ~/storage/shared
  (o Descargas no se puede escribir) ejecuta termux-setup-storage al arrancar,
  muestra el aviso de permiso de Android y espera hasta 45 s a que lo aceptes;
  si lo aceptas sigue en Descargas en esa misma ejecución, sin reiniciar Termux.
  Solo lo intenta una vez (marca ~/.dlpy/storage_asked): si lo rechazas, las
  siguientes ejecuciones usan ~/dlpy_files y avisan; la marca se borra cuando el
  acceso funciona, así que si luego lo pierdes vuelve a pedirlo.
  DLPY_NO_STORAGE_SETUP=1 lo desactiva. Fuera de Android no hace nada.
- --selftest nunca lanza el permiso.

## 0.5.3

- Android: copiar y mover archivos ya no falla en el almacenamiento compartido
  (Descargas). shutil.copy2/move intentan chmod/utime sobre el destino y Android
  lo rechaza con «Operation not permitted»; eso podía dejar sin guardar el video,
  sin índice y sin reutilizar nada. Ahora todo pasa por copy_file/move_file, que
  copian el contenido y tratan permisos y fecha como opcionales. iOS no cambia.
- Android: la caché de streams (24 h) avisa siempre si no pudo guardar una pista
  (antes solo en debug) y, al terminar, indica cuántas pistas quedaron en caché.
  Si el enlace físico falla se copia el archivo en su lugar.
- Android: compartir un enlace a Termux queda automatizado: en la primera
  ejecución DLpy crea solo ~/bin/termux-url-opener (si ya había uno ajeno no lo
  toca y lo avisa; «--instalar-android» sigue sirviendo para forzarlo).
- --selftest: pruebas nuevas de copy_file/move_file.

## 0.5.2

- Android: al terminar la descarga Termux abre el archivo solo, con el
  reproductor de Android (termux-open --view con el tipo MIME del archivo;
  si falla, termux-open normal). Antes solo se abría con
  DLPY_ANDROID_ACTION=open. Ahora DLPY_ANDROID_ACTION vale «open» por defecto;
  «share» comparte el archivo y «none» no abre nada. Si no se pudo abrir, avisa
  el motivo probable (Termux en segundo plano necesita «Mostrar sobre otras
  apps») y la notificación sigue abriéndolo al tocarla.
- Android: al arrancar, DLpy se mueve solo a la raíz de Termux (~/dlpy.py) si
  estaba en otra carpeta (p. ej. Descargas) y se vuelve a ejecutar desde ahí con
  los mismos argumentos; borra el original y actualiza ~/bin/termux-url-opener
  si apuntaba a la ruta vieja. Si no puede moverse, sigue donde está. Además el
  directorio de trabajo pasa a ser ~. DLPY_NO_MOVE=1 desactiva el movimiento.
- Aclaración: en Android los videos terminados van a Descargas (no a
  Descargas/DLpy, que solo guarda backups y changelog), como desde 0.5.1.
- --selftest: prueba nueva de root_move_target.

## 0.5.1

- Android: los archivos terminados se guardan directo en la carpeta Descargas
  de Android (antes iban a Descargas/DLpy). Backups y changelog siguen en
  Descargas/DLpy. DLPY_DOWNLOAD_DIR cambia el destino de las descargas.
- Seguridad: Descargas es de todo el teléfono, así que DLpy solo toca lo que
  él mismo descargó (lo registrado en su índice). La limpieza por espacio y el
  orden de carpetas no ven ni borran tus otros archivos de Descargas.
- Los archivos que ya estaban en Descargas/DLpy (0.5.0) se siguen reconociendo;
  al volver a descargarlos pasan a Descargas.
- iOS no cambia: el destino sigue siendo dlpy_files.

## 0.5.0

- Detección de plataforma al arrancar (detect_platform): Android/Termux si hay
  TERMUX_VERSION, PREFIX/HOME de com.termux o sys.platform «android»; en cualquier
  otro caso se usa el modo iOS/a-Shell, que queda EXACTAMENTE como en 0.4.9.
  DLPY_PLATFORM=ios|android fuerza una u otra.
- Modo Android (Termux):
  · Guarda en Descargas/DLpy (almacenamiento compartido, requiere
    termux-setup-storage); sin permiso usa ~/dlpy_files y lo avisa. Lo interno
    (índice, caché, work/) va en ~/.dlpy/dlpy_internal.
  · No hay Atajos: al terminar avisa la ruta, escanea el archivo para la galería
    (termux-media-scan) y manda una notificación (termux-notification) si Termux:API
    está instalado. DLPY_ANDROID_ACTION=open|share abre o comparte el archivo.
  · Sin conversión Apple: «compatible» pasa a significar reproducible en Android
    (h264/vp9/hevc/aac/opus en mp4/webm/mkv) y el mejor formato prefiere h264.
  · Ofrece instalar ffmpeg con «pkg install» si falta; pip reintenta con
    --break-system-packages si Termux lo pide.
  · Si el portapapeles trae un enlace (termux-clipboard-get) lo ofrece primero.
  · «--instalar-android» crea ~/bin/termux-url-opener: al compartir un enlace a
    Termux desde cualquier app se abre DLpy con ese enlace.
  · Sin hideKeyboard, ancho de barras 60 y textos sin iPhone/a-Shell.
- Prueba nueva en --selftest para detect_platform.

## 0.4.9

- Reanudación automática: una descarga cortada (Ctrl+C, error de red, iOS
  cerrando a-Shell) continúa sola al repetir el mismo enlace con los mismos
  formatos. La carpeta de trabajo ya no es aleatoria: es work/resume-<huella>,
  con la huella calculada de enlace + format_id + extensión + tamaño exacto.
  Cambiar formato, calidad o pistas da otra huella y empieza de cero.
- El nombre base se guarda en resume.json para que el .part siga reconociéndose.
- Cancelar o fallar ya no borra el avance; solo se borra al terminar bien.
  Tras 3 fallos seguidos sin avanzar, el parcial se descarta (por si está dañado).
- Los parciales caducan 24 h después de su ÚLTIMA modificación (antes: de la
  creación de la carpeta).
- La velocidad final de una pista reanudada no cuenta los bytes ya descargados.

## 0.4.8

- En la lista de formatos, Enter sin escribir nada ya no sale del script: se
  vuelve a preguntar. Solo «q» sale. Así un Enter accidental no tira la sesión.

## 0.4.7

- Una opción inexistente o una respuesta que no es s/n ya no hace seguir (ni
  salir) al script: se avisa y se repite la pregunta. Afecta a la lista de
  formatos, la pista predeterminada, las pistas adicionales (ahora se valida
  cada número), «¿Usarlo?», «¿Descargar de nuevo?», «¿Convertir?» y las
  preguntas de dependencias. Enter y la cuenta regresiva siguen igual.
- «¿Convertir? (S/n)» de compatibilidad Apple tiene ahora cuenta regresiva
  (WAIT_SECONDS): si vence sin escribir nada se aplica la respuesta por
  defecto (convertir). Empezar a escribir cancela la cuenta.
- Nuevo helper ask_yn() y parse_yn(); el --selftest incluye pruebas de parse_yn.

## 0.4.6

- La línea final de cada pista muestra siempre la velocidad media. Antes solo
  aparecía si la descarga duraba más de 0.3 s, así que las pistas de audio
  (archivos pequeños que bajan casi al instante) quedaban sin «↓ …». Ahora el
  mínimo es 0.05 s; si yt-dlp tampoco da el tiempo se usa el de la propia pista.
- Al empezar la descarga se muestra el nombre del archivo («Archivo: …»)
  antes de las barras.

## 0.4.5

- Las barras de descarga muestran directamente la calidad («1080p», «1080p60»)
  en las pistas de video y el idioma («es-US») en las de audio, sin la palabra
  «Video»/«Audio». Antes «Video 1080p» se recortaba a «Video …» en pantallas
  angostas y se perdía justo el dato útil. La calidad usa el mismo formato que
  la columna «Res» de la lista. Sin altura o sin idioma queda «Video»/«Audio».
  La línea final de cada pista usa la misma etiqueta («1080p: listo (↓ …)»).
- El --selftest incluye ahora pruebas de stream_label.

## 0.4.4

- Corrige un falso positivo al reintentar una descarga: antes bastaba que el
  texto del error contuviera «403» o «410» (p. ej. dentro de una URL o un ID)
  para reanalizar el enlace sin necesidad. Ahora solo se reintenta ante
  «HTTP Error 403/410», «not available», «expired» o «forbidden».
- Los ~60 bloques «except … as _ign: dbg("x: ignorado", …)» pasan a un único
  helper ignore(donde, error) con la misma salida en modo debug; se quitan
  los «pass» sobrantes. Se acotan las excepciones de term_width, _host,
  load_json y countdown_supported a los errores esperables (antes Exception).
  Sin debug el comportamiento no cambia.
- Las órdenes al shell (pip install y la apertura del atajo) ahora escapan
  los argumentos con shlex.quote en vez de comillas armadas a mano.
- La cabecera «Principal» queda justo encima de main() (estaba antes del
  bloque de análisis tolerante).
- Nuevo `python dlpy.py --selftest`: pruebas rápidas de funciones puras
  (safe_name, vtuple, normalize_format, parse_sections, mark_originals,
  auto_best, yes y el filtro de reintento). No toca disco ni red.

## 0.4.3

- Elimina por completo el soporte de cookies: ya no se lee, valida, guarda
  ni usa ningún cookies.txt (desaparecen parse_cookies, read_cookies,
  cookies_file, save_cookies_text, read_pasted_cookies, DLPY_COOKIES y el
  uso de cookiefile/--cookies en el análisis y la descarga). Ante el error
  «Sign in to confirm you're not a bot» solo se avisa y se termina, sin
  pedir nada. Un ~/Documents/dlpy_cookies.txt que haya quedado de versiones
  anteriores ya no se toca: bórralo a mano si quieres.
- DLPY_YTDLP_ARGS sigue pasando a yt-dlp las banderas en bruto tal cual.
- Los errores que antes se tragaban en silencio (except … pass / return /
  valor por defecto) ahora se anotan en modo debug («[debug] función:
  ignorado …»). Sin debug el comportamiento no cambia. Se dejan igual el
  Ctrl+C / fin de entrada del usuario y el propio dbg().
- Aclara que DLPY_CLEAR vale 3 por defecto (reinicio completo del terminal,
  \x1bc); el changelog 0.3.7 indicaba 1 y el comentario del código remitía
  a él. Solo se corrige el comentario: el comportamiento es el mismo.
- Erratas del encabezado: «llengan» → «llegan», «realizas» → «realizadas».

## 0.4.2

- Error «Sign in to confirm you're not a bot»: ahora solo se pide PEGAR el
  contenido del cookies.txt (formato Netscape) y terminar con una línea
  vacía. Se valida, se guarda en ~/Documents/dlpy_cookies.txt (permisos
  privados) y se reintenta el análisis. Ya no se pide una ruta de archivo.
- Tras pegar se limpia la pantalla para no dejar las cookies a la vista.

## 0.4.1

- Al actualizar de versión, el backup de dlpy_files (descargas e índice) sigue
  igual y ahora, si en dlpy_internal hay descargas (delivery/, cache/, work/
  u otras sueltas), pregunta «¿Mover también las descargas de dlpy_internal
  a backups? (s/N)». Con «s» pasan a backups/<versión>/_internal/ junto al
  index.json; state/ y script/ no se tocan. Con «N» (Enter) no se mueve nada.
- Cookies de YouTube: si existe ~/Documents/dlpy_cookies.txt (o la ruta de
  DLPY_COOKIES) se usa en el análisis y en la descarga (formato Netscape),
  salvo que se pase --cookies/--cookies-from-browser en DLPY_YTDLP_ARGS.
  Avisa si el archivo está vacío, no tiene formato válido, no trae cookies de
  YouTube/Google o parecen caducadas. El archivo queda fuera de dlpy_files,
  así que ninguna limpieza ni backup lo toca.
- Error «Sign in to confirm you're not a bot»: ya no repite los intentos
  (no sirven); explica qué hacer y permite pegar la ruta de un cookies.txt,
  que se copia a ~/Documents/dlpy_cookies.txt y reintenta el análisis.
  Nota: yt-dlp no admite usuario y contraseña de Google; hacen falta cookies.

## 0.4.0

- Corrige un error de texto en el tercer comentario del encabezado
  («momentos» → «momento»).

## 0.3.9

- dlpy_internal reorganizada en subcarpetas: state/ (index.json,
  last_link.json, version.json), script/ (script_snapshot.py, changelog.md),
  cache/streams/ (antes stream_cache/), work/ (descargas en curso) y
  delivery/<id>/ (copias de entrega al atajo, antes sueltas en la raíz).
- Migración automática al arrancar: mueve lo de la estructura anterior a su
  sitio nuevo (se hace antes de revisar el almacenamiento y la versión).
- Limpieza por límite, opción «backups»: ahora borra solo las descargas
  (video, audio, subtítulos e imágenes descargadas) dentro de backups/ y de
  las carpetas de versión legadas. Scripts (.py), changelogs, índices y
  cualquier otro archivo se conservan; las carpetas que queden vacías se
  eliminan. El aviso y los tamaños del banner lo reflejan.
- Las caducidades de 24 h (entregas y work/) se aplican ahora por elemento.

## 0.3.8

- Las barras de descarga ahora muestran siempre la velocidad de bajada
  («↓ 2.4MB/s»): si yt-dlp no la informa (o aún no hay porcentaje) se calcula
  a partir de los bytes descargados, y es el último dato en recortarse cuando
  la pantalla es angosta (antes se perdía al no haber porcentaje conocido).
- Al terminar cada pista la línea final conserva la velocidad media de esa
  descarga (también en el modo sin TTY / debug: «Video 1080p: listo (↓ …)»).
- Limpieza por límite de almacenamiento: la opción «videos descargados» ahora
  borra solo los archivos de video dentro de dlpy_files y sus subcarpetas
  (excluye backups/). Audios, changelog y demás archivos no se tocan; las
  subcarpetas que queden vacías se eliminan. Las copias de entrega en
  dlpy_internal solo se borran si contienen un video.

## 0.3.7

- Corrige que tras un clear a mitad de ejecución (p. ej. al elegir «b» con
  una lista larga) la pantalla quedara en blanco y hubiera que subir con
  scroll: ahora se vacía primero el historial (\x1b[3J) y después la
  pantalla (\x1b[2J\x1b[H), para que la vista no se quede desfasada.
- DLPY_CLEAR=1..4 elige el método de limpieza si en tu terminal sigue
  fallando: 1 = historial → pantalla (por defecto), 2 = pantalla →
  historial (como 0.3.6), 3 = reinicio completo del terminal (\x1bc),
  4 = solo pantalla (como 0.3.3, sin vaciar el historial).

## 0.3.6

- clear_screen ahora también vacía el historial de desplazamiento del
  terminal (\x1b[3J) además de la pantalla visible, para no ver logs
  anteriores al hacer scroll en la misma sesión. No afecta a otras sesiones
  de a-Shell (cada una tiene su propio buffer).

## 0.3.5

- Banner mucho más notorio: barra de título a todo el ancho en video
  inverso (cian; amarilla con «DEBUG ACTIVO» cuando debug está encendido),
  con la versión a la izquierda, y una línea separadora debajo del espacio.
- Al arrancar se limpia la consola (clear_screen) para que el banner quede
  arriba y no mezclado con la salida de la ejecución anterior. En debug no
  se borra: solo se imprime el separador.

## 0.3.4

- Banner más preciso: el total de «Espacio» ahora es el mismo que usa la
  limpieza de almacenamiento (antes omitía índice, snapshot y changelog, que
  ahora salen como «otros»), muestra el % del límite (amarillo si se pasa),
  el número de descargas y los GB con 2 decimales.
- El desglose del banner se ajusta al ancho real (safe_width) en vez de
  desbordar y romper la línea en pantallas angostas.
- Se quita el banner duplicado que salía tras pegar el enlace (se imprimía
  sin limpiar nada, apilado sobre el de arranque y los comentarios).
- Código obsoleto eliminado: CL_START/CL_END (sin uso), parámetro «compact»
  de banner (se ignoraba), rama duplicada TTY/no-TTY en clear_screen,
  comentario engañoso de storage_summary y condición redundante en
  reuse_downloaded.

## 0.3.3

- Banner ampliado: muestra el espacio usado por DLpy (descargas, caché/
  temporales y backups) junto a la versión y el estado de debug.
- Cada clear_screen vuelve a pintar ese mismo banner (versión + debug +
  espacio) para que quede visible tras limpiar la consola.
- Limpieza de consola más oportuna antes de preguntas clave (pistas,
  conversión Apple) para que el teclado de iOS no tape las opciones.

## 0.3.2

- apple_plan: si video + audios + contenedor ya son compatibles con Apple
  (aunque haya merge_ext), no se ofrece conversión innecesaria.
- normalize_format: más conservador al asumir avc1/mp4a; solo lo hace en
  contenedores Apple con indicios claros de video; en el resto deja
  «unknown» y no marca como compatible Apple.
- reuse_downloaded: comentario y lógica aclarados (si el archivo ya está
  convertido y ahora no se pide conversión, o viceversa sin original, se
  fuerza re-descarga).
- ask_apple_convert: al cancelar con Ctrl+C avisa claramente que se
  descargará sin convertir.
- ffmpeg_progress: cierra el archivo de error de ffmpeg en todos los
  caminos (incluido fallo al lanzar Popen).
- tree_size / check_storage: el conjunto de inodos se reutiliza de forma
  coherente al sumar categorías para no sobrestimar con hard-links.

## 0.3.1

- Corrige que el changelog no se sacara del .py: solo se extraía cuando la
  versión cambiaba respecto a la guardada. Ahora, en cada arranque, si el
  script trae un bloque «CHANGELOG … FIN CHANGELOG» se mueve a changelog.md
  y se quita del .py (aunque la versión sea la misma, p. ej. al volver a
  pegar el archivo).
- Si la versión ya existe en changelog.md se actualiza su texto (antes se
  ignoraba el nuevo).
- Los marcadores se reconocen aunque cambien los espacios o las mayúsculas
  de «FIN»; si hay inicio sin fin, avisa y no toca el script.
- Al terminar muestra cuántas versiones nuevas se guardaron.

## 0.3.0

- Corrige «No se encontraron formatos» en sitios cuyos formatos llegan sin
  códec (yt-dlp deja vcodec/acodec en None; p. ej. PornHub con MP4 directos):
  antes se descartaban todos. Ahora un formato sin códec declarado se toma
  como un archivo único con video y audio (o solo audio si así se indica).
  En MP4/M4V/MOV se asume avc1/mp4a (se marca con «?» en la tabla); en otros
  contenedores se trata como no compatible con Apple y se ofrece convertir.
- El análisis original de yt-dlp no se toca: la normalización se hace sobre
  copias, solo para armar la lista.

## 0.2.9

- Corrige «Unable to download webpage: HTTP Error 404» al analizar algunos
  sitios que sí funcionan con yt-dlp en bruto. El análisis ahora prueba en
  orden: (1) opciones de biblioteca como hasta ahora, (2) opciones idénticas
  a las del CLI de yt-dlp (reintentos, cabeceras y demás valores por defecto),
  (3) lo mismo sin --no-playlist y (4) el ejecutable yt-dlp -J si existe.
  Las opciones que funcionaron se reutilizan también al descargar.
- DLPY_YTDLP_ARGS="…" añade banderas de yt-dlp en bruto (p. ej. --cookies
  archivo.txt, --user-agent "…", --add-header "Referer:…") al análisis y a la
  descarga.
- En debug se anota qué intento falló y cuál funcionó.

## 0.2.8

- Corrige «Requested format is not available» al descargar (visto en
  Facebook): antes yt-dlp volvía a analizar el enlace al descargar y a veces
  devolvía otra lista de formatos distinta a la que se mostró. Ahora se
  descarga con el mismo análisis que vio el usuario (process_ie_result).
- Si aun así falla porque el formato ya no existe o la URL caducó: reanaliza
  el enlace y, como último recurso, usa el mejor equivalente avisándolo.
- Los comentarios inteligentes no tocan el enlace ni la descarga (solo
  imprimen); el fallo no venía de ellos.

## 0.2.7

- Comentarios inteligentes según el uso (humor irreverente), en dos momentos:
  * Al recibir el enlace: según la hora/día (madrugada, comida, lunes,
    viernes/sábado noche, 31 dic, 14 feb…) y según el sitio (YouTube, TikTok,
    X, Instagram/Facebook, Twitch, Reddit…). Sitio adulto: alerta que
    parpadea y comentario aparte.
  * Tras analizar el video: contenido +18, directo, muy largo o muy corto, y
    «ya lo tenías». Tras elegir formato: más de 2 GB, 4K, resolución baja,
    solo audio.
  * Al terminar (o al entregar uno ya descargado), al cancelar con Ctrl+C y
    al aparecer la limpieza de almacenamiento.
- Los comentarios de las primeras etapas se repintan tras limpiar la pantalla
  (máx. 4) para que no se pierdan.
- DLPY_ROAST=0 los apaga. Ninguno puede interrumpir una descarga.

## 0.2.6

- Limpieza de almacenamiento al arrancar (antes de todo lo demás): si
  dlpy_internal + dlpy_files pesan más de 1 GB, muestra cuánto ocupa cada
  parte y pregunta por separado si borrar: videos descargados, caché y
  temporales (stream_cache, work y entregas) y backups. Por defecto responde
  No. Los archivos con enlaces duros se cuentan una sola vez.
- Al borrar descargas se limpian también sus entradas del índice.
- El límite se puede cambiar con DLPY_CLEAN_LIMIT_MB (por defecto 1024).

## 0.2.5

- Modo debug (DLPY_DEBUG=1) mejorado, sin cambiar nada cuando está apagado:
  * La descarga corre yt-dlp en modo verbose y con su progreso nativo
    (incluye las líneas de ffmpeg de unir/remux), igual que fuera del script.
  * ffmpeg propio (conversión y ajuste de pistas): imprime el comando
    completo, su salida en bruto en vivo (loglevel info), el bloque
    -progress cada 2 s y el código de salida.
  * Líneas «[debug] …» con los datos de cada paso: info del video, formatos,
    pistas, formato elegido, selección, plan Apple, decisión de reutilizar,
    caché de streams, opciones de yt-dlp, eventos de hooks, archivo final,
    entrada del índice y entrega al atajo.
  * Sin barras animadas (se usan líneas de texto) y sin borrar la pantalla
    (se imprime un separador) para no perder lo ya mostrado.

## 0.2.4

- Al convertir a Apple con varios idiomas, las pistas de audio conservan su
  nombre (antes salían como «Track 1, 2…»): se escribe de nuevo el título y
  el handler_name de cada pista (el MP4 solo guarda el segundo) y cuál es la
  predeterminada. Aplica también al convertir un archivo ya descargado.

## 0.2.3

- Estilo unificado: todas las barras (descarga, unión, conversión, ajuste de
  pistas) usan el mismo diseño y siempre dibujan la barra. Si no cabe todo,
  se recorta primero el ETA, luego la velocidad y por último el nombre,
  en vez de quedarse solo con el porcentaje.
- Nombres de fase más cortos («Conv. HEVC», «Uniendo», «Pistas»…).
- Reutiliza lo ya descargado: si eliges los mismos parámetros que el archivo
  YA DESCARGADO (mismas pistas/formato y misma decisión de conversión) no
  se vuelve a bajar nada: se entrega el que ya existe.
- Si el archivo ya descargado tiene esos mismos streams pero sin convertir y
  ahora eliges convertir, se convierte ese archivo directamente (con barra),
  sin volver a descargar.
- La caché de streams de 24 h sigue funcionando para el resto de casos.

## 0.2.2

- La conversión a Apple y el ajuste de pistas ya muestran barra de progreso
  real: porcentaje, velocidad (p. ej. 1.8x) y ETA, leídos del -progress de
  ffmpeg. Si el video no informa su duración, la barra pasa a modo
  indeterminado con el tiempo ya procesado.
- Cada intento de encoder (HEVC hardware → HEVC software → H.264) reinicia
  la barra con su propio nombre.
- Unir audio/video muestra avance real vigilando el tamaño del archivo
  temporal frente a la suma de las pistas.
- Ctrl+C durante una conversión detiene ffmpeg.
- Si no se puede lanzar ffmpeg directamente, vuelve al método anterior
  (sin porcentaje, con barra indeterminada).

## 0.2.1

- Corrige el congelamiento al preguntar «¿Convertir?» cuando había varios
  idiomas (venía justo después de las preguntas con cuenta regresiva):
  esa pregunta usa ahora el mismo lector de línea que las anteriores
  (timed_input sin cuenta) en vez de input().
- La conversión de video usa HEVC (H.265, etiqueta hvc1) en lugar de H.264:
  prueba hevc_videotoolbox → libx265 y, solo como último recurso,
  libx264. El índice guarda el códec realmente usado.

## 0.2.0

- Si el formato elegido (o las pistas de audio elegidas) no es compatible con
  Apple, pregunta si convertirlo: video → H.264, audio → AAC, contenedor →
  MP4 (video) o M4A (audio). Lo que ya es compatible se copia sin recodificar
  (solo remux); HEVC se etiqueta hvc1.
- Video: prueba h264_videotoolbox y, si falla, libx264.
- Sin ffmpeg avisa y descarga tal cual. Si la conversión falla, conserva el original.
- El índice guarda «converted» y YA DESCARGADO muestra la línea «Conversión».

## 0.1.9

- YA DESCARGADO muestra de forma explícita la pista usada y su idioma
  (además de la tabla de pistas si hay varias).
- Limpia la consola antes de listar formatos y al iniciar la descarga;
  tras cada limpieza se vuelve a pintar el banner de arranque.
- Copia el changelog actual a dlpy_files/changelog.md.

## 0.1.8

- Corrige el doble prompt al lanzar desde Atajos (p. ej. «¿Usarlo? ▸ ¿Usarlo? ▸»):
  se drenan los Enter residuales del buffer de stdin antes de cada pregunta,
  sin cambiar el modo del terminal.
- El banner ya no se reimprime justo después del arranque (quedaba duplicado);
  solo en pasos posteriores (análisis / descarga).

## 0.1.7

- dlpy_data → dlpy_files: solo descargas terminadas y backups/.
- Todo lo demás (índice, último enlace, versión, snapshot, changelog,
  caché de pistas y directorios de trabajo) vive en dlpy_internal.
- Caché de streams 24 h: si se vuelve a pedir el mismo format_id
  (mismo video a la misma resolución/pista), se reutiliza el archivo
  intermedio sin volver a bajarlo. Si el formato elegido es distinto
  (p. ej. 720 en vez de 1080), se descarga de nuevo.
- Migración automática desde dlpy_data al arrancar.
- El banner (DLpy vX · debug) se reimprime en los pasos principales
  para que la versión quede visible durante toda la ejecución.

## 0.1.6

- Corrige el congelamiento al pedir entrada (introducido en 0.1.5): se quitan los
  cambios al modo del terminal (apagar eco y vaciar la entrada).
- Enter fantasma: ahora se ignora una respuesta vacía que llega casi al instante
  de mostrar la pregunta (menos de 0.4 s), sin tocar el terminal.
