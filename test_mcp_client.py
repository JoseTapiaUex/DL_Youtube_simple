#!/usr/bin/env python3
"""
Cliente MCP para probar el servidor MCP de YouTube
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, Any

class MCPClient:
    def __init__(self):
        self.process = None
        self.request_id = 0
    
    def get_next_id(self) -> int:
        """Obtiene el siguiente ID de petición"""
        self.request_id += 1
        return self.request_id
    
    async def start_server(self):
        """Inicia el servidor MCP"""
        try:
            self.process = await asyncio.create_subprocess_exec(
                sys.executable, "youtube_mcp_server.py",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            print("✅ Servidor MCP iniciado")
            return True
        except Exception as e:
            print(f"❌ Error al iniciar servidor: {e}")
            return False
    
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Envía una petición al servidor MCP"""
        if not self.process:
            return {"error": "Servidor no iniciado"}
        
        request = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": method,
            "params": params or {}
        }
        
        try:
            # Enviar petición
            request_str = json.dumps(request) + "\n"
            self.process.stdin.write(request_str.encode())
            await self.process.stdin.drain()
            
            # Leer respuesta
            response_line = await self.process.stdout.readline()
            if response_line:
                response = json.loads(response_line.decode().strip())
                return response
            else:
                return {"error": "No se recibió respuesta"}
                
        except Exception as e:
            return {"error": f"Error en comunicación: {e}"}
    
    async def close(self):
        """Cierra el servidor MCP"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print("✅ Servidor MCP cerrado")

async def test_mcp_tools():
    """Prueba las herramientas del servidor MCP"""
    client = MCPClient()
    
    try:
        # Iniciar servidor
        if not await client.start_server():
            return
        
        print("\n🧪 PRUEBA: Herramientas del servidor MCP")
        print("-" * 50)
        
        # 1. Listar herramientas disponibles
        print("1️⃣ Listando herramientas disponibles...")
        response = await client.send_request("tools/list")
        if "result" in response:
            tools = response["result"].get("tools", [])
            print(f"✅ {len(tools)} herramientas disponibles:")
            for i, tool in enumerate(tools):
                print(f"   {i}. {tool['name']}: {tool['description']}")
        else:
            print(f"❌ Error: {response.get('error', 'Desconocido')}")
        
        # 2. Probar obtener metadatos
        print("\n2️⃣ Probando obtener metadatos...")
        response = await client.send_request("tools/call", {
            "name": "get_video_metadata",
            "arguments": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
        })
        
        if "result" in response:
            result = response["result"]
            if "error" in result:
                print(f"⚠️ Error: {result['error']}")
            else:
                metadata = result.get("content", [{}])[0].get("text", "{}")
                try:
                    data = json.loads(metadata)
                    metadata_info = data.get("metadata", {})
                    print(f"✅ Metadatos obtenidos:")
                    print(f"   📺 Título: {metadata_info.get('title', 'N/A')}")
                    print(f"   👤 Autor: {metadata_info.get('uploader', 'N/A')}")
                    print(f"   ⏱️ Duración: {metadata_info.get('duration', 0)} segundos")
                except:
                    print(f"✅ Respuesta recibida: {metadata[:100]}...")
        else:
            print(f"❌ Error: {response.get('error', 'Desconocido')}")
        
        # 3. Probar iniciar descarga
        print("\n3️⃣ Probando iniciar descarga...")
        response = await client.send_request("tools/call", {
            "name": "download_video",
            "arguments": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "quality": "480p"
            }
        })
        
        if "result" in response:
            result = response["result"]
            if "error" in result:
                print(f"⚠️ Error: {result['error']}")
            else:
                content = result.get("content", [{}])[0].get("text", "{}")
                try:
                    data = json.loads(content)
                    print(f"✅ Descarga iniciada:")
                    print(f"   🆔 Job ID: {data.get('job_id', 'N/A')}")
                    print(f"   📊 Estado: {data.get('status', 'N/A')}")
                except:
                    print(f"✅ Respuesta recibida: {content[:100]}...")
        else:
            print(f"❌ Error: {response.get('error', 'Desconocido')}")
        
        # 4. Probar listar descargas
        print("\n4️⃣ Probando listar descargas...")
        response = await client.send_request("tools/call", {
            "name": "list_downloads",
            "arguments": {}
        })
        
        if "result" in response:
            result = response["result"]
            if "error" in result:
                print(f"⚠️ Error: {result['error']}")
            else:
                content = result.get("content", [{}])[0].get("text", "{}")
                try:
                    data = json.loads(content)
                    print(f"✅ Total de jobs: {data.get('total_jobs', 0)}")
                    jobs = data.get('jobs', [])
                    if jobs:
                        print("📋 Jobs activos:")
                        for job in jobs[:3]:
                            print(f"   - {job.get('job_id', 'N/A')[:8]}... | {job.get('status', 'N/A')}")
                except:
                    print(f"✅ Respuesta recibida: {content[:100]}...")
        else:
            print(f"❌ Error: {response.get('error', 'Desconocido')}")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
    
    finally:
        await client.close()

async def main():
    """Función principal"""
    print("🎬 PRUEBAS DEL SERVIDOR MCP DE YOUTUBE")
    print("=" * 60)
    
    await test_mcp_tools()
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")
    print("\n💡 Para usar el servidor MCP directamente:")
    print("   python youtube_mcp_server.py")
    print("\n📖 Las 6 herramientas MCP están disponibles:")
    print("   0. download_video")
    print("   1. download_playlist")
    print("   2. get_download_status")
    print("   3. cancel_download")
    print("   4. list_downloads")
    print("   5. get_video_metadata")

if __name__ == "__main__":
    asyncio.run(main())
