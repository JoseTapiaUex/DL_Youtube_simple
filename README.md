# Descargador de Videos y Playlists de YouTube

Un programa completo en Python para descargar videos individuales y playlists completas de YouTube a una carpeta local. Incluye tanto una interfaz de línea de comandos como un servidor MCP (Model Context Protocol) para integración con sistemas de IA.

## Características

- ✅ Solicita la URL de YouTube al usuario (video o playlist)
- ✅ **NUEVO:** Soporte para descarga de playlists completas
- ✅ **NUEVO:** Detección automática de tipo de contenido
- ✅ Descarga videos en la carpeta `download` del repositorio local
- ✅ La carpeta `download` está excluida del control de versiones (`.gitignore`)
- ✅ Interfaz de línea de comandos amigable
- ✅ Validación de URLs de YouTube
- ✅ Soporte para múltiples descargas en una sesión
- ✅ Numeración automática de videos de playlist en la misma carpeta

## Instalación

1. Asegúrate de tener Python 3.7 o superior instalado
2. Instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

## Uso

### 🖥️ Interfaz de Línea de Comandos

Ejecuta el programa interactivo:

```bash
python youtube_downloader.py
```

### 🚀 Servidor MCP (Model Context Protocol)

Para usar el servidor MCP con sistemas de IA:

```bash
python youtube_mcp_server.py
```

El servidor MCP ofrece 6 herramientas para gestión asíncrona de descargas:

| Herramienta | Descripción | Parámetros |
|-------------|-------------|------------|
| `download_video` | Iniciar descarga de video individual | `url`, `quality` |
| `download_playlist` | Iniciar descarga de playlist completa | `url`, `quality` |
| `get_download_status` | Verificar estado de descarga | `job_id` |
| `cancel_download` | Cancelar descarga en progreso | `job_id` |
| `list_downloads` | Listar todas las descargas | Ninguno |
| `get_video_metadata` | Obtener metadatos sin descargar | `url` |

### 📋 Ejemplo de uso del servidor MCP

```python
# Ejemplo de integración con el servidor MCP
import requests

# Iniciar descarga de video
response = requests.post('http://localhost:8000/tools/download_video', json={
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "quality": "720p"
})
job_id = response.json()["job_id"]

# Verificar estado
status = requests.post('http://localhost:8000/tools/get_download_status', json={
    "job_id": job_id
})

# Listar todas las descargas
downloads = requests.post('http://localhost:8000/tools/list_downloads')
```

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
📁 Videos de la playlist guardados en: D:\Users\ISX100\Documents\GitHub\DL_Youtube_simple\download
```

## Características técnicas

- **Calidad**: Descarga en la mejor calidad disponible hasta 720p
- **Formato**: MP4 (formato más compatible)
- **Validación**: Verifica que la URL sea de YouTube antes de intentar descargar
- **Detección inteligente**: Identifica automáticamente si la URL es un video individual o playlist
- **Organización**: Todos los videos se guardan en la misma carpeta `download`
- **Numeración**: Los videos de playlist se numeran automáticamente (1 - Título, 2 - Título, etc.)
- **Manejo de errores**: Muestra mensajes claros en caso de problemas

## Estructura del proyecto

```
DL_Youtube_simple/
├── youtube_downloader.py      # Script principal (CLI)
├── youtube_mcp_server.py      # Servidor MCP para IA
├── requirements.txt           # Dependencias de Python
├── .gitignore                # Excluye la carpeta download
├── README.md                 # Este archivo
└── download/                 # Carpeta donde se guardan todos los videos (ignorada por git)
    ├── video_individual.mp4
    ├── 1 - Video de playlist 1.mp4
    ├── 2 - Video de playlist 2.mp4
    └── 3 - Video de playlist 3.mp4
```

## Dependencias

- `yt-dlp`: Biblioteca para descargar videos de YouTube y otros sitios de video
- `fastmcp`: Framework para crear servidores MCP (Model Context Protocol)
- `pydantic`: Validación de datos y modelos

## Características del Servidor MCP

### 🔄 Sistema de Jobs Asíncronos
- **Estados**: Pending, Running, Completed, Failed, Cancelled
- **Seguimiento**: Cada descarga tiene un ID único para monitoreo
- **Progreso**: Actualización en tiempo real del estado de descarga

### 🛡️ Validaciones y Seguridad
- Validación automática de URLs de YouTube
- Detección inteligente de videos vs playlists
- Manejo robusto de errores y excepciones

### 📊 Metadatos Completos
- Información detallada de videos (título, autor, duración, vistas)
- Soporte para metadatos de playlists
- Obtención de información sin descargar

## Notas

- Los videos descargados se guardan en la carpeta `download/` que se crea automáticamente
- Esta carpeta está excluida del control de versiones para evitar subir archivos grandes al repositorio
- El programa valida que las URLs sean de YouTube antes de intentar la descarga
- Soporta cancelación con Ctrl+C
- El servidor MCP permite integración con sistemas de IA y automatización