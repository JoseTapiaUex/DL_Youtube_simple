#!/usr/bin/env python3
"""
Script manual para probar el servidor HTTP de YouTube
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def mostrar_menu():
    """Muestra el menú de opciones"""
    print("\n" + "="*50)
    print("🎬 YOUTUBE DOWNLOADER - PRUEBA MANUAL")
    print("="*50)
    print("1. Obtener metadatos de video")
    print("2. Iniciar descarga de video")
    print("3. Iniciar descarga de playlist")
    print("4. Ver estado de descarga")
    print("5. Listar todas las descargas")
    print("6. Cancelar descarga")
    print("0. Salir")
    print("-"*50)

def obtener_metadatos():
    """Obtener metadatos de un video"""
    url = input("🔗 Ingresa la URL del video: ").strip()
    
    if not url:
        print("❌ URL vacía")
        return
    
    try:
        response = requests.post(f"{BASE_URL}/metadata", json={"url": url})
        
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                print(f"❌ Error: {data['error']}")
            else:
                metadata = data["metadata"]
                print(f"\n✅ Metadatos obtenidos:")
                print(f"📺 Título: {metadata['title']}")
                print(f"👤 Autor: {metadata['uploader']}")
                print(f"⏱️ Duración: {metadata['duration']} segundos")
                print(f"👀 Vistas: {metadata['view_count']:,}")
                print(f"📁 Es playlist: {metadata['is_playlist']}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def iniciar_descarga_video():
    """Iniciar descarga de video individual"""
    url = input("🔗 Ingresa la URL del video: ").strip()
    quality = input("📺 Calidad (720p, 480p, 1080p) [720p]: ").strip() or "720p"
    
    if not url:
        print("❌ URL vacía")
        return
    
    try:
        response = requests.post(f"{BASE_URL}/download_video", 
                               json={"url": url, "quality": quality})
        
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                print(f"❌ Error: {data['error']}")
            else:
                print(f"\n✅ Descarga iniciada:")
                print(f"🆔 Job ID: {data['job_id']}")
                print(f"📊 Estado: {data['status']}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def iniciar_descarga_playlist():
    """Iniciar descarga de playlist"""
    url = input("🔗 Ingresa la URL de la playlist: ").strip()
    quality = input("📺 Calidad (720p, 480p, 1080p) [720p]: ").strip() or "720p"
    
    if not url:
        print("❌ URL vacía")
        return
    
    try:
        response = requests.post(f"{BASE_URL}/download_playlist", 
                               json={"url": url, "quality": quality})
        
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                print(f"❌ Error: {data['error']}")
            else:
                print(f"\n✅ Descarga de playlist iniciada:")
                print(f"🆔 Job ID: {data['job_id']}")
                print(f"📊 Estado: {data['status']}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def ver_estado():
    """Ver estado de una descarga"""
    job_id = input("🆔 Ingresa el Job ID: ").strip()
    
    if not job_id:
        print("❌ Job ID vacío")
        return
    
    try:
        response = requests.get(f"{BASE_URL}/status/{job_id}")
        
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                print(f"❌ Error: {data['error']}")
            else:
                print(f"\n✅ Estado del job:")
                print(f"🆔 Job ID: {data['job_id']}")
                print(f"📺 Título: {data['title']}")
                print(f"📊 Estado: {data['status']}")
                print(f"📈 Progreso: {data['progress_percentage']}%")
                print(f"🎬 Videos: {data['downloaded_videos']}/{data['total_videos']}")
                print(f"📁 Es playlist: {data['is_playlist']}")
                if data.get('error_message'):
                    print(f"❌ Error: {data['error_message']}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def listar_descargas():
    """Listar todas las descargas"""
    try:
        response = requests.get(f"{BASE_URL}/downloads")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Total de jobs: {data['total_jobs']}")
            
            if data['jobs']:
                print("\n📋 Jobs activos:")
                for i, job in enumerate(data['jobs'], 1):
                    print(f"{i}. 🆔 {job['job_id'][:8]}...")
                    print(f"   📺 {job['title'][:50]}...")
                    print(f"   📊 {job['status']} - {job['progress_percentage']}%")
                    print(f"   📁 Playlist: {'Sí' if job['is_playlist'] else 'No'}")
                    print()
            else:
                print("📋 No hay jobs activos")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def cancelar_descarga():
    """Cancelar una descarga"""
    job_id = input("🆔 Ingresa el Job ID a cancelar: ").strip()
    
    if not job_id:
        print("❌ Job ID vacío")
        return
    
    try:
        response = requests.post(f"{BASE_URL}/cancel/{job_id}")
        
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                print(f"❌ Error: {data['error']}")
            else:
                print(f"\n✅ {data['message']}")
                print(f"🆔 Job ID: {data['job_id']}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Función principal"""
    print("🎬 YOUTUBE DOWNLOADER - PRUEBA MANUAL")
    print("Asegúrate de que el servidor esté ejecutándose:")
    print("python youtube_http_server.py")
    
    while True:
        try:
            mostrar_menu()
            opcion = input("👉 Selecciona una opción: ").strip()
            
            if opcion == "0":
                print("👋 ¡Hasta luego!")
                break
            elif opcion == "1":
                obtener_metadatos()
            elif opcion == "2":
                iniciar_descarga_video()
            elif opcion == "3":
                iniciar_descarga_playlist()
            elif opcion == "4":
                ver_estado()
            elif opcion == "5":
                listar_descargas()
            elif opcion == "6":
                cancelar_descarga()
            else:
                print("❌ Opción no válida")
                
            input("\n⏸️ Presiona Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    main()
