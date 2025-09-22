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

def descargar_video(url, carpeta_destino):
    """Descarga el video de YouTube a la carpeta especificada"""
    try:
        # Configuración para yt-dlp
        ydl_opts = {
            'outtmpl': str(carpeta_destino / '%(title)s.%(ext)s'),
            'format': 'best[height<=720]',  # Descarga en calidad máxima hasta 720p
            'noplaylist': True,  # Solo descarga el video, no la playlist completa
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            print(f"Descargando video desde: {url}")
            print("Obteniendo información del video...")
            
            # Obtener información del video
            info = ydl.extract_info(url, download=False)
            titulo = info.get('title', 'Video sin título')
            duracion = info.get('duration', 0)
            
            print(f"Título: {titulo}")
            if duracion:
                minutos = duracion // 60
                segundos = duracion % 60
                print(f"Duración: {minutos}:{segundos:02d}")
            
            print("Iniciando descarga...")
            ydl.download([url])
            print("✅ Descarga completada exitosamente!")
            
    except Exception as e:
        print(f"❌ Error durante la descarga: {str(e)}")
        return False
    
    return True

def main():
    """Función principal del programa"""
    print("=" * 50)
    print("🎬 DESCARGADOR DE VIDEOS DE YOUTUBE")
    print("=" * 50)
    
    # Crear carpeta de descarga
    carpeta_download = crear_carpeta_download()
    print(f"📁 Carpeta de descarga: {carpeta_download.absolute()}")
    
    while True:
        print("\n" + "-" * 30)
        url = input("🔗 Ingresa la URL del video de YouTube: ").strip()
        
        if not url:
            print("❌ Por favor, ingresa una URL válida.")
            continue
            
        if not validar_url_youtube(url):
            print("❌ La URL no parece ser de YouTube. Por favor, verifica la URL.")
            continue
        
        # Intentar descargar el video
        if descargar_video(url, carpeta_download):
            print(f"📁 Video guardado en: {carpeta_download.absolute()}")
        
        # Preguntar si quiere descargar otro video
        continuar = input("\n¿Quieres descargar otro video? (s/n): ").strip().lower()
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
