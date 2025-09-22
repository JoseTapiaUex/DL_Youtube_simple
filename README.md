# Descargador de Videos y Playlists de YouTube

Un programa sencillo en Python para descargar videos individuales y playlists completas de YouTube a una carpeta local.

## Características

- ✅ Solicita la URL de YouTube al usuario (video o playlist)
- ✅ **NUEVO:** Soporte para descarga de playlists completas
- ✅ **NUEVO:** Detección automática de tipo de contenido
- ✅ Descarga videos en la carpeta `download` del repositorio local
- ✅ La carpeta `download` está excluida del control de versiones (`.gitignore`)
- ✅ Interfaz de línea de comandos amigable
- ✅ Validación de URLs de YouTube
- ✅ Soporte para múltiples descargas en una sesión
- ✅ Organización automática de playlists en subcarpetas

## Instalación

1. Asegúrate de tener Python 3.7 o superior instalado
2. Instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

## Uso

Ejecuta el programa:

```bash
python youtube_downloader.py
```

El programa te pedirá:
1. La URL del video de YouTube que quieres descargar
2. Automáticamente creará la carpeta `download` si no existe
3. Descargará el video en esa carpeta
4. Te preguntará si quieres descargar otro video

## Ejemplos de uso

### Descarga de video individual
```
🎬 DESCARGADOR DE VIDEOS Y PLAYLISTS DE YOUTUBE
==================================================
📁 Carpeta de descarga: D:\Users\ISX100\Documents\GitHub\DL_Youtube_simple\download

------------------------------
🔗 Ingresa la URL de YouTube (video o playlist): https://www.youtube.com/watch?v=dQw4w9WgXcQ

📺 Se detectó un video individual.
Descargando video desde: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Obteniendo información del video...
📺 Título: Rick Astley - Never Gonna Give You Up (Official Video)
👤 Autor: Rick Astley
⏱️ Duración: 3:33
Iniciando descarga...
✅ Video descargado exitosamente!
📁 Video guardado en: D:\Users\ISX100\Documents\GitHub\DL_Youtube_simple\download
```

### Descarga de playlist completa
```
🎬 DESCARGADOR DE VIDEOS Y PLAYLISTS DE YOUTUBE
==================================================
📁 Carpeta de descarga: D:\Users\ISX100\Documents\GitHub\DL_Youtube_simple\download

------------------------------
🔗 Ingresa la URL de YouTube (video o playlist): https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMOV8u4MvX6j_7GfFg

🎵 Se detectó una playlist de YouTube.
¿Quieres descargar toda la playlist? (s/n): s

Descargando playlist desde: https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMOV8u4MvX6j_7GfFg
Obteniendo información de la playlist...
📁 Playlist: Música de los 80s
👤 Autor: Canal Musical
🎬 Cantidad de videos: 25

📋 Primeros videos en la playlist:
   1. Video Musical 1 (3:45)
   2. Video Musical 2 (4:12)
   3. Video Musical 3 (3:28)
   ... y 22 videos más

Iniciando descarga...
✅ Playlist descargada exitosamente!
📁 Playlist guardada en: D:\Users\ISX100\Documents\GitHub\DL_Youtube_simple\download
```

## Características técnicas

- **Calidad**: Descarga en la mejor calidad disponible hasta 720p
- **Formato**: MP4 (formato más compatible)
- **Validación**: Verifica que la URL sea de YouTube antes de intentar descargar
- **Detección inteligente**: Identifica automáticamente si la URL es un video individual o playlist
- **Organización**: Las playlists se guardan en subcarpetas con el nombre de la playlist
- **Numeración**: Los videos de playlist se numeran automáticamente (1 - Título, 2 - Título, etc.)
- **Manejo de errores**: Muestra mensajes claros en caso de problemas

## Estructura del proyecto

```
DL_Youtube_simple/
├── youtube_downloader.py    # Script principal
├── requirements.txt         # Dependencias de Python
├── .gitignore              # Excluye la carpeta download
├── README.md               # Este archivo
└── download/               # Carpeta donde se guardan los videos (ignorada por git)
    ├── video_individual.mp4
    └── Nombre_Playlist/    # Subcarpeta para playlists
        ├── 1 - Video 1.mp4
        ├── 2 - Video 2.mp4
        └── 3 - Video 3.mp4
```

## Dependencias

- `yt-dlp`: Biblioteca para descargar videos de YouTube y otros sitios de video

## Notas

- Los videos descargados se guardan en la carpeta `download/` que se crea automáticamente
- Esta carpeta está excluida del control de versiones para evitar subir archivos grandes al repositorio
- El programa valida que las URLs sean de YouTube antes de intentar la descarga
- Soporta cancelación con Ctrl+C