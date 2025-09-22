#!/usr/bin/env python3
"""
Descargador de videos de YouTube
Programa sencillo para descargar videos de YouTube en la carpeta 'download'
"""

import os
import sys
from pathlib import Path
from yt_dlp import YoutubeDL

def crear_carpeta_download():
    """Crea la carpeta 'download' si no existe"""
    download_path = Path("download")
    download_path.mkdir(exist_ok=True)
    return download_path

def validar_url_youtube(url):
    """Valida si la URL es de YouTube"""
    youtube_dominios = ['youtube.com', 'youtu.be', 'm.youtube.com']
    return any(dominio in url.lower() for dominio in youtube_dominios)

def detectar_tipo_url(url):
    """Detecta si la URL es un video individual o una playlist"""
    url_lower = url.lower()
    
    if 'playlist?list=' in url_lower:
        return 'playlist'
    elif 'watch?v=' in url_lower and 'list=' in url_lower:
        return 'video_en_playlist'
    else:
        return 'video_individual'

def descargar_video(url, carpeta_destino, descargar_playlist=False):
    """Descarga el video o playlist de YouTube a la carpeta especificada"""
    try:
        # Configuración para yt-dlp
        if descargar_playlist:
            ydl_opts = {
                'outtmpl': str(carpeta_destino / '%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s'),
                'format': 'best[height<=720]',  # Descarga en calidad máxima hasta 720p
                'noplaylist': False,  # Permite descargar playlists
            }
        else:
            ydl_opts = {
                'outtmpl': str(carpeta_destino / '%(title)s.%(ext)s'),
                'format': 'best[height<=720]',  # Descarga en calidad máxima hasta 720p
                'noplaylist': True,  # Solo descarga el video, no la playlist completa
            }
        
        with YoutubeDL(ydl_opts) as ydl:
            tipo_url = detectar_tipo_url(url)
            
            if descargar_playlist or tipo_url == 'playlist':
                print(f"Descargando playlist desde: {url}")
                print("Obteniendo información de la playlist...")
            else:
                print(f"Descargando video desde: {url}")
                print("Obteniendo información del video...")
            
            # Obtener información del video/playlist
            info = ydl.extract_info(url, download=False)
            
            if descargar_playlist or tipo_url == 'playlist':
                # Información de playlist
                titulo_playlist = info.get('title', 'Playlist sin título')
                cantidad_videos = info.get('playlist_count', 0)
                autor = info.get('uploader', 'Autor desconocido')
                
                print(f"📁 Playlist: {titulo_playlist}")
                print(f"👤 Autor: {autor}")
                print(f"🎬 Cantidad de videos: {cantidad_videos}")
                
                # Mostrar primeros videos de la playlist
                entries = info.get('entries', [])
                if entries:
                    print("\n📋 Primeros videos en la playlist:")
                    for i, entry in enumerate(entries[:5]):  # Mostrar solo los primeros 5
                        titulo_video = entry.get('title', 'Sin título')
                        duracion = entry.get('duration', 0)
                        if duracion:
                            minutos = duracion // 60
                            segundos = duracion % 60
                            print(f"   {i+1}. {titulo_video} ({minutos}:{segundos:02d})")
                    if len(entries) > 5:
                        print(f"   ... y {len(entries) - 5} videos más")
            else:
                # Información de video individual
                titulo = info.get('title', 'Video sin título')
                duracion = info.get('duration', 0)
                autor = info.get('uploader', 'Autor desconocido')
                
                print(f"📺 Título: {titulo}")
                print(f"👤 Autor: {autor}")
                if duracion:
                    minutos = duracion // 60
                    segundos = duracion % 60
                    print(f"⏱️ Duración: {minutos}:{segundos:02d}")
            
            print("\nIniciando descarga...")
            ydl.download([url])
            
            if descargar_playlist or tipo_url == 'playlist':
                print("✅ Playlist descargada exitosamente!")
            else:
                print("✅ Video descargado exitosamente!")
            
    except Exception as e:
        print(f"❌ Error durante la descarga: {str(e)}")
        return False
    
    return True

def main():
    """Función principal del programa"""
    print("=" * 50)
    print("🎬 DESCARGADOR DE VIDEOS Y PLAYLISTS DE YOUTUBE")
    print("=" * 50)
    
    # Crear carpeta de descarga
    carpeta_download = crear_carpeta_download()
    print(f"📁 Carpeta de descarga: {carpeta_download.absolute()}")
    
    while True:
        print("\n" + "-" * 30)
        url = input("🔗 Ingresa la URL de YouTube (video o playlist): ").strip()
        
        if not url:
            print("❌ Por favor, ingresa una URL válida.")
            continue
            
        if not validar_url_youtube(url):
            print("❌ La URL no parece ser de YouTube. Por favor, verifica la URL.")
            continue
        
        # Detectar tipo de URL y preguntar al usuario
        tipo_url = detectar_tipo_url(url)
        descargar_playlist = False
        
        if tipo_url == 'playlist':
            print("\n🎵 Se detectó una playlist de YouTube.")
            opcion = input("¿Quieres descargar toda la playlist? (s/n): ").strip().lower()
            descargar_playlist = opcion in ['s', 'si', 'sí', 'y', 'yes']
            
        elif tipo_url == 'video_en_playlist':
            print("\n🎬 Se detectó un video que pertenece a una playlist.")
            opcion = input("¿Quieres descargar solo este video (v) o toda la playlist (p)? (v/p): ").strip().lower()
            descargar_playlist = opcion in ['p', 'playlist', 'playlist']
            
            if not descargar_playlist:
                print("📺 Descargando solo el video individual...")
        else:
            print("\n📺 Se detectó un video individual.")
        
        # Intentar descargar el video o playlist
        if descargar_video(url, carpeta_download, descargar_playlist):
            if descargar_playlist:
                print(f"📁 Playlist guardada en: {carpeta_download.absolute()}")
            else:
                print(f"📁 Video guardado en: {carpeta_download.absolute()}")
        
        # Preguntar si quiere descargar otro contenido
        continuar = input("\n¿Quieres descargar otro video/playlist? (s/n): ").strip().lower()
        if continuar not in ['s', 'si', 'sí', 'y', 'yes']:
            break
    
    print("\n👋 ¡Gracias por usar el descargador!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Descarga cancelada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1)
