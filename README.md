# Descargador de Videos de YouTube

Un programa sencillo en Python para descargar videos de YouTube a una carpeta local.

## Características

- ✅ Solicita la URL de YouTube al usuario
- ✅ Descarga videos en la carpeta `download` del repositorio local
- ✅ La carpeta `download` está excluida del control de versiones (`.gitignore`)
- ✅ Interfaz de línea de comandos amigable
- ✅ Validación de URLs de YouTube
- ✅ Soporte para múltiples descargas en una sesión

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

## Ejemplo de uso

```
🎬 DESCARGADOR DE VIDEOS DE YOUTUBE
==================================================
📁 Carpeta de descarga: D:\Users\ISX100\Documents\GitHub\DL_Youtube_simple\download

------------------------------
🔗 Ingresa la URL del video de YouTube: https://www.youtube.com/watch?v=dQw4w9WgXcQ

Descargando video desde: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Obteniendo información del video...
Título: Rick Astley - Never Gonna Give You Up (Official Video)
Duración: 3:32
Iniciando descarga...
✅ Descarga completada exitosamente!
📁 Video guardado en: D:\Users\ISX100\Documents\GitHub\DL_Youtube_simple\download

¿Quieres descargar otro video? (s/n): n

👋 ¡Gracias por usar el descargador!
```

## Características técnicas

- **Calidad**: Descarga en la mejor calidad disponible hasta 720p
- **Formato**: MP4 (formato más compatible)
- **Validación**: Verifica que la URL sea de YouTube antes de intentar descargar
- **Manejo de errores**: Muestra mensajes claros en caso de problemas

## Estructura del proyecto

```
DL_Youtube_simple/
├── youtube_downloader.py    # Script principal
├── requirements.txt         # Dependencias de Python
├── .gitignore              # Excluye la carpeta download
├── README.md               # Este archivo
└── download/               # Carpeta donde se guardan los videos (ignorada por git)
```

## Dependencias

- `yt-dlp`: Biblioteca para descargar videos de YouTube y otros sitios de video

## Notas

- Los videos descargados se guardan en la carpeta `download/` que se crea automáticamente
- Esta carpeta está excluida del control de versiones para evitar subir archivos grandes al repositorio
- El programa valida que las URLs sean de YouTube antes de intentar la descarga
- Soporta cancelación con Ctrl+C