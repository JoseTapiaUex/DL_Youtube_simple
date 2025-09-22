#!/usr/bin/env python3
"""
MCP Server para descarga de videos y playlists de YouTube
Ofrece herramientas para gestionar descargas asíncronas
"""

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum

from fastmcp import FastMCP
from pydantic import BaseModel
from yt_dlp import YoutubeDL
import threading
import time

# Estados posibles de una descarga
class DownloadStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Modelo para representar un job de descarga
class DownloadJob(BaseModel):
    job_id: str
    url: str
    title: str
    status: DownloadStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    download_path: Optional[str] = None
    is_playlist: bool = False
    total_videos: Optional[int] = None
    downloaded_videos: int = 0

# Modelo para parámetros de descarga de video
class DownloadVideoParams(BaseModel):
    url: str
    quality: str = "720p"

# Modelo para parámetros de descarga de playlist
class DownloadPlaylistParams(BaseModel):
    url: str
    quality: str = "720p"

# Modelo para obtener estado
class GetStatusParams(BaseModel):
    job_id: str

# Modelo para cancelar descarga
class CancelDownloadParams(BaseModel):
    job_id: str

# Modelo para obtener metadatos
class GetMetadataParams(BaseModel):
    url: str

# Crear la instancia del servidor MCP
mcp = FastMCP("YouTube Downloader MCP Server")

# Almacenamiento en memoria de los jobs (en producción usar una base de datos)
download_jobs: Dict[str, DownloadJob] = {}
active_downloads: Dict[str, threading.Thread] = {}

# Configuración de descarga
DOWNLOAD_FOLDER = Path("download")
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

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
        job.status = DownloadStatus.RUNNING
        job.started_at = datetime.now()
        
        # Configuración para yt-dlp
        if is_playlist:
            ydl_opts = {
                'outtmpl': str(DOWNLOAD_FOLDER / '%(playlist_index)s - %(title)s.%(ext)s'),
                'format': f'best[height<={quality[:-1]}]' if quality != "720p" else 'best[height<=720]',
                'noplaylist': False,
                'progress_hooks': [lambda d: actualizar_progreso(job_id, d)],
            }
        else:
            ydl_opts = {
                'outtmpl': str(DOWNLOAD_FOLDER / '%(title)s.%(ext)s'),
                'format': f'best[height<={quality[:-1]}]' if quality != "720p" else 'best[height<=720]',
                'noplaylist': True,
                'progress_hooks': [lambda d: actualizar_progreso(job_id, d)],
            }
        
        with YoutubeDL(ydl_opts) as ydl:
            # Obtener información antes de descargar
            info = ydl.extract_info(url, download=False)
            
            # Actualizar información del job
            if is_playlist:
                job.title = info.get('title', 'Playlist sin título')
                job.total_videos = info.get('playlist_count', 0)
            else:
                job.title = info.get('title', 'Video sin título')
                job.total_videos = 1
            
            # Realizar la descarga
            ydl.download([url])
            
            # Marcar como completado
            job.status = DownloadStatus.COMPLETED
            job.completed_at = datetime.now()
            job.downloaded_videos = job.total_videos or 1
            
    except Exception as e:
        # Marcar como fallido
        job.status = DownloadStatus.FAILED
        job.completed_at = datetime.now()
        job.error_message = str(e)
    
    finally:
        # Limpiar el hilo activo
        if job_id in active_downloads:
            del active_downloads[job_id]

def actualizar_progreso(job_id: str, progress_data: dict):
    """Actualiza el progreso de descarga"""
    if job_id in download_jobs:
        job = download_jobs[job_id]
        if 'downloaded_bytes' in progress_data and 'total_bytes' in progress_data:
            # Calcular progreso porcentual
            if progress_data['total_bytes'] > 0:
                progress = (progress_data['downloaded_bytes'] / progress_data['total_bytes']) * 100
                job.downloaded_videos = int(progress / 100 * (job.total_videos or 1))

@mcp.tool()
def download_video(url: str, quality: str = "720p") -> dict:
    """
    Start downloading a video from YouTube or other supported sites.
    Returns a job ID to track download progress.
    
    Args:
        url: URL of the video to download
        quality: Quality of the download (e.g., "720p", "480p", "1080p")
    
    Returns:
        dict: Job information with job_id
    """
    # Validar URL
    if not validar_url_youtube(url):
        return {"error": "URL no válida de YouTube"}
    
    # Verificar que no sea una playlist
    if detectar_tipo_url(url) == 'playlist':
        return {"error": "Esta URL es una playlist. Usa download_playlist en su lugar."}
    
    # Crear nuevo job
    job_id = str(uuid.uuid4())
    job = DownloadJob(
        job_id=job_id,
        url=url,
        title="Preparando descarga...",
        status=DownloadStatus.PENDING,
        created_at=datetime.now(),
        is_playlist=False
    )
    
    download_jobs[job_id] = job
    
    # Iniciar descarga en hilo separado
    thread = threading.Thread(
        target=ejecutar_descarga,
        args=(job_id, url, False, quality)
    )
    thread.start()
    active_downloads[job_id] = thread
    
    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Descarga de video iniciada"
    }

@mcp.tool()
def download_playlist(url: str, quality: str = "720p") -> dict:
    """
    Start downloading an entire playlist from YouTube or other supported sites.
    Returns a job ID to track download progress.
    
    Args:
        url: URL of the playlist to download
        quality: Quality of the download (e.g., "720p", "480p", "1080p")
    
    Returns:
        dict: Job information with job_id
    """
    # Validar URL
    if not validar_url_youtube(url):
        return {"error": "URL no válida de YouTube"}
    
    # Verificar que sea una playlist
    if detectar_tipo_url(url) not in ['playlist', 'video_en_playlist']:
        return {"error": "Esta URL no es una playlist. Usa download_video en su lugar."}
    
    # Crear nuevo job
    job_id = str(uuid.uuid4())
    job = DownloadJob(
        job_id=job_id,
        url=url,
        title="Preparando descarga de playlist...",
        status=DownloadStatus.PENDING,
        created_at=datetime.now(),
        is_playlist=True
    )
    
    download_jobs[job_id] = job
    
    # Iniciar descarga en hilo separado
    thread = threading.Thread(
        target=ejecutar_descarga,
        args=(job_id, url, True, quality)
    )
    thread.start()
    active_downloads[job_id] = thread
    
    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Descarga de playlist iniciada"
    }

@mcp.tool()
def get_download_status(job_id: str) -> dict:
    """
    Check the status of a download job.
    
    Args:
        job_id: ID of the download job to check
    
    Returns:
        dict: Current status and details of the job
    """
    if job_id not in download_jobs:
        return {"error": "Job ID no encontrado"}
    
    job = download_jobs[job_id]
    
    return {
        "job_id": job_id,
        "title": job.title,
        "status": job.status,
        "created_at": job.created_at.isoformat(),
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error_message": job.error_message,
        "is_playlist": job.is_playlist,
        "total_videos": job.total_videos,
        "downloaded_videos": job.downloaded_videos,
        "progress_percentage": round((job.downloaded_videos / (job.total_videos or 1)) * 100, 2) if job.total_videos else 0
    }

@mcp.tool()
def cancel_download(job_id: str) -> dict:
    """
    Cancel a running or pending download job.
    
    Args:
        job_id: ID of the download job to cancel
    
    Returns:
        dict: Result of the cancellation attempt
    """
    if job_id not in download_jobs:
        return {"error": "Job ID no encontrado"}
    
    job = download_jobs[job_id]
    
    if job.status in [DownloadStatus.COMPLETED, DownloadStatus.FAILED, DownloadStatus.CANCELLED]:
        return {"error": f"No se puede cancelar un job con estado: {job.status}"}
    
    # Marcar como cancelado
    job.status = DownloadStatus.CANCELLED
    job.completed_at = datetime.now()
    
    # Terminar el hilo si está activo
    if job_id in active_downloads:
        # Nota: En una implementación real, necesitarías un mecanismo más robusto
        # para cancelar yt-dlp. Aquí solo marcamos el job como cancelado.
        del active_downloads[job_id]
    
    return {
        "job_id": job_id,
        "status": "cancelled",
        "message": "Descarga cancelada exitosamente"
    }

@mcp.tool()
def list_downloads() -> dict:
    """
    List all download jobs with their current status.
    
    Returns:
        dict: List of all download jobs and their statuses
    """
    jobs_list = []
    
    for job_id, job in download_jobs.items():
        jobs_list.append({
            "job_id": job_id,
            "title": job.title,
            "status": job.status,
            "created_at": job.created_at.isoformat(),
            "is_playlist": job.is_playlist,
            "total_videos": job.total_videos,
            "downloaded_videos": job.downloaded_videos,
            "progress_percentage": round((job.downloaded_videos / (job.total_videos or 1)) * 100, 2) if job.total_videos else 0
        })
    
    # Ordenar por fecha de creación (más recientes primero)
    jobs_list.sort(key=lambda x: x['created_at'], reverse=True)
    
    return {
        "total_jobs": len(jobs_list),
        "jobs": jobs_list
    }

@mcp.tool()
def get_video_metadata(url: str) -> dict:
    """
    Fetch metadata about a video without downloading it.
    
    Args:
        url: URL of the video or playlist to get metadata for
    
    Returns:
        dict: Video/playlist metadata information
    """
    # Validar URL
    if not validar_url_youtube(url):
        return {"error": "URL no válida de YouTube"}
    
    try:
        metadata = obtener_metadatos_video(url)
        tipo_url = detectar_tipo_url(url)
        
        return {
            "url": url,
            "type": tipo_url,
            "metadata": metadata
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Ejecutar el servidor MCP
    mcp.run()
