#!/usr/bin/env python3
"""
Servidor HTTP para descarga de videos y playlists de YouTube
Versión simplificada para pruebas y uso directo
"""

import json
import uuid
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from enum import Enum

from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL

# Estados posibles de una descarga
class DownloadStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Almacenamiento en memoria de los jobs
download_jobs: Dict[str, dict] = {}
active_downloads: Dict[str, threading.Thread] = {}

# Configuración de descarga
DOWNLOAD_FOLDER = Path("download")
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

# Crear la aplicación Flask
app = Flask(__name__)

def validar_url_youtube(url: str) -> bool:
    """Valida si la URL es de YouTube"""
    youtube_dominios = ['youtube.com', 'youtu.be', 'm.youtube.com']
    return any(dominio in url.lower() for dominio in youtube_dominios)

def detectar_tipo_url(url: str) -> str:
    """Detecta si la URL es un video individual o una playlist"""
    url_lower = url.lower()
    
    if 'playlist?list=' in url_lower:
        return 'playlist'
    elif 'watch?v=' in url_lower and 'list=' in url_lower:
        return 'video_en_playlist'
    else:
        return 'video_individual'

def obtener_metadatos_video(url: str) -> dict:
    """Obtiene metadatos de un video sin descargarlo"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Sin título'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Autor desconocido'),
                'view_count': info.get('view_count', 0),
                'upload_date': info.get('upload_date', ''),
                'description': info.get('description', '')[:500] + '...' if info.get('description') else '',
                'thumbnail': info.get('thumbnail', ''),
                'is_playlist': 'entries' in info,
                'playlist_count': info.get('playlist_count', 0) if 'entries' in info else 0
            }
    except Exception as e:
        raise Exception(f"Error al obtener metadatos: {str(e)}")

def ejecutar_descarga(job_id: str, url: str, is_playlist: bool = False, quality: str = "720p"):
    """Ejecuta la descarga en un hilo separado"""
    job = download_jobs[job_id]
    
    try:
        # Actualizar estado a running
        job['status'] = DownloadStatus.RUNNING
        job['started_at'] = datetime.now().isoformat()
        
        # Configuración para yt-dlp
        if is_playlist:
            ydl_opts = {
                'outtmpl': str(DOWNLOAD_FOLDER / '%(playlist_index)s - %(title)s.%(ext)s'),
                'format': f'best[height<={quality[:-1]}]' if quality != "720p" else 'best[height<=720]',
                'noplaylist': False,
            }
        else:
            ydl_opts = {
                'outtmpl': str(DOWNLOAD_FOLDER / '%(title)s.%(ext)s'),
                'format': f'best[height<={quality[:-1]}]' if quality != "720p" else 'best[height<=720]',
                'noplaylist': True,
            }
        
        with YoutubeDL(ydl_opts) as ydl:
            # Obtener información antes de descargar
            info = ydl.extract_info(url, download=False)
            
            # Actualizar información del job
            if is_playlist:
                job['title'] = info.get('title', 'Playlist sin título')
                job['total_videos'] = info.get('playlist_count', 0)
            else:
                job['title'] = info.get('title', 'Video sin título')
                job['total_videos'] = 1
            
            # Realizar la descarga
            ydl.download([url])
            
            # Marcar como completado
            job['status'] = DownloadStatus.COMPLETED
            job['completed_at'] = datetime.now().isoformat()
            job['downloaded_videos'] = job['total_videos']
            
    except Exception as e:
        # Marcar como fallido
        job['status'] = DownloadStatus.FAILED
        job['completed_at'] = datetime.now().isoformat()
        job['error_message'] = str(e)
    
    finally:
        # Limpiar el hilo activo
        if job_id in active_downloads:
            del active_downloads[job_id]

# Rutas de la API

@app.route('/', methods=['GET'])
def home():
    """Página de inicio con información del servidor"""
    return jsonify({
        "message": "YouTube Downloader HTTP Server",
        "version": "1.0.0",
        "tools": [
            {"name": "download_video", "method": "POST", "endpoint": "/download_video"},
            {"name": "download_playlist", "method": "POST", "endpoint": "/download_playlist"},
            {"name": "get_status", "method": "GET", "endpoint": "/status/<job_id>"},
            {"name": "cancel_download", "method": "POST", "endpoint": "/cancel/<job_id>"},
            {"name": "list_downloads", "method": "GET", "endpoint": "/downloads"},
            {"name": "get_metadata", "method": "POST", "endpoint": "/metadata"}
        ]
    })

@app.route('/download_video', methods=['POST'])
def download_video():
    """Iniciar descarga de video individual"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({"error": "URL requerida"}), 400
    
    url = data['url']
    quality = data.get('quality', '720p')
    
    # Validar URL
    if not validar_url_youtube(url):
        return jsonify({"error": "URL no válida de YouTube"}), 400
    
    # Verificar que no sea una playlist
    if detectar_tipo_url(url) == 'playlist':
        return jsonify({"error": "Esta URL es una playlist. Usa /download_playlist en su lugar."}), 400
    
    # Crear nuevo job
    job_id = str(uuid.uuid4())
    job = {
        'job_id': job_id,
        'url': url,
        'title': "Preparando descarga...",
        'status': DownloadStatus.PENDING,
        'created_at': datetime.now().isoformat(),
        'is_playlist': False,
        'total_videos': 1,
        'downloaded_videos': 0
    }
    
    download_jobs[job_id] = job
    
    # Iniciar descarga en hilo separado
    thread = threading.Thread(
        target=ejecutar_descarga,
        args=(job_id, url, False, quality)
    )
    thread.start()
    active_downloads[job_id] = thread
    
    return jsonify({
        "job_id": job_id,
        "status": "pending",
        "message": "Descarga de video iniciada"
    })

@app.route('/download_playlist', methods=['POST'])
def download_playlist():
    """Iniciar descarga de playlist completa"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({"error": "URL requerida"}), 400
    
    url = data['url']
    quality = data.get('quality', '720p')
    
    # Validar URL
    if not validar_url_youtube(url):
        return jsonify({"error": "URL no válida de YouTube"}), 400
    
    # Verificar que sea una playlist
    if detectar_tipo_url(url) not in ['playlist', 'video_en_playlist']:
        return jsonify({"error": "Esta URL no es una playlist. Usa /download_video en su lugar."}), 400
    
    # Crear nuevo job
    job_id = str(uuid.uuid4())
    job = {
        'job_id': job_id,
        'url': url,
        'title': "Preparando descarga de playlist...",
        'status': DownloadStatus.PENDING,
        'created_at': datetime.now().isoformat(),
        'is_playlist': True,
        'total_videos': 0,
        'downloaded_videos': 0
    }
    
    download_jobs[job_id] = job
    
    # Iniciar descarga en hilo separado
    thread = threading.Thread(
        target=ejecutar_descarga,
        args=(job_id, url, True, quality)
    )
    thread.start()
    active_downloads[job_id] = thread
    
    return jsonify({
        "job_id": job_id,
        "status": "pending",
        "message": "Descarga de playlist iniciada"
    })

@app.route('/status/<job_id>', methods=['GET'])
def get_download_status(job_id):
    """Verificar estado de descarga"""
    if job_id not in download_jobs:
        return jsonify({"error": "Job ID no encontrado"}), 404
    
    job = download_jobs[job_id]
    
    return jsonify({
        "job_id": job_id,
        "title": job['title'],
        "status": job['status'],
        "created_at": job['created_at'],
        "started_at": job.get('started_at'),
        "completed_at": job.get('completed_at'),
        "error_message": job.get('error_message'),
        "is_playlist": job['is_playlist'],
        "total_videos": job['total_videos'],
        "downloaded_videos": job['downloaded_videos'],
        "progress_percentage": round((job['downloaded_videos'] / (job['total_videos'] or 1)) * 100, 2) if job['total_videos'] else 0
    })

@app.route('/cancel/<job_id>', methods=['POST'])
def cancel_download(job_id):
    """Cancelar descarga en progreso"""
    if job_id not in download_jobs:
        return jsonify({"error": "Job ID no encontrado"}), 404
    
    job = download_jobs[job_id]
    
    if job['status'] in [DownloadStatus.COMPLETED, DownloadStatus.FAILED, DownloadStatus.CANCELLED]:
        return jsonify({"error": f"No se puede cancelar un job con estado: {job['status']}"}), 400
    
    # Marcar como cancelado
    job['status'] = DownloadStatus.CANCELLED
    job['completed_at'] = datetime.now().isoformat()
    
    # Terminar el hilo si está activo
    if job_id in active_downloads:
        del active_downloads[job_id]
    
    return jsonify({
        "job_id": job_id,
        "status": "cancelled",
        "message": "Descarga cancelada exitosamente"
    })

@app.route('/downloads', methods=['GET'])
def list_downloads():
    """Listar todas las descargas"""
    jobs_list = []
    
    for job_id, job in download_jobs.items():
        jobs_list.append({
            "job_id": job_id,
            "title": job['title'],
            "status": job['status'],
            "created_at": job['created_at'],
            "is_playlist": job['is_playlist'],
            "total_videos": job['total_videos'],
            "downloaded_videos": job['downloaded_videos'],
            "progress_percentage": round((job['downloaded_videos'] / (job['total_videos'] or 1)) * 100, 2) if job['total_videos'] else 0
        })
    
    # Ordenar por fecha de creación (más recientes primero)
    jobs_list.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({
        "total_jobs": len(jobs_list),
        "jobs": jobs_list
    })

@app.route('/metadata', methods=['POST'])
def get_video_metadata():
    """Obtener metadatos de video sin descargar"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({"error": "URL requerida"}), 400
    
    url = data['url']
    
    # Validar URL
    if not validar_url_youtube(url):
        return jsonify({"error": "URL no válida de YouTube"}), 400
    
    try:
        metadata = obtener_metadatos_video(url)
        tipo_url = detectar_tipo_url(url)
        
        return jsonify({
            "url": url,
            "type": tipo_url,
            "metadata": metadata
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🎬 Iniciando YouTube Downloader HTTP Server...")
    print("📡 Servidor disponible en: http://localhost:5000")
    print("📖 Documentación en: http://localhost:5000/")
    print("\n🛠️ Endpoints disponibles:")
    print("   POST /download_video")
    print("   POST /download_playlist") 
    print("   GET  /status/<job_id>")
    print("   POST /cancel/<job_id>")
    print("   GET  /downloads")
    print("   POST /metadata")
    print("\n⏹️ Para detener: Ctrl+C")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
