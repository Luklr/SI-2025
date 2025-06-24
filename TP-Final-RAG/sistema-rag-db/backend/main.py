"""
API Backend usando FastAPI para el sistema RAG
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
from pathlib import Path

# Importar nuestros módulos locales
from .models import QueryRequest, QueryResponse, DocumentUpload
from .rag_system import rag_system
from .config import settings

app = FastAPI(
    title="Sistema RAG con Base de Datos",
    description="Sistema de Recuperación Aumentada (RAG) que consulta bases de datos usando lenguaje natural",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos (frontend)
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Modelos adicionales para la API
class HealthResponse(BaseModel):
    status: str
    db_type: str
    sources_count: int

class SourceInfo(BaseModel):
    name: str
    chunks_count: int

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página principal del sistema"""
    frontend_file = frontend_path / "index.html"
    if frontend_file.exists():
        return HTMLResponse(content=frontend_file.read_text(), status_code=200)
    else:
        return HTMLResponse(
            content="""
            <html>
                <body>
                    <h1>Sistema RAG con Base de Datos</h1>
                    <p>API funcionando correctamente</p>
                    <p><a href="/docs">Ver documentación de la API</a></p>
                </body>
            </html>
            """,
            status_code=200
        )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Verificar el estado del sistema"""
    try:
        sources = rag_system.get_sources()
        return HealthResponse(
            status="healthy",
            db_type=settings.db_type,
            sources_count=len(sources)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el sistema: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Procesar una consulta en lenguaje natural"""
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="La consulta no puede estar vacía")
        
        # Verificar que tenemos documentos en la base
        sources = rag_system.get_sources()
        if not sources:
            raise HTTPException(
                status_code=404, 
                detail="No hay documentos en la base de datos. Por favor, agrega documentos primero."
            )
        
        # Procesar la consulta
        result = rag_system.process_query(
            query=request.query,
            max_results=request.max_results
        )
        
        return QueryResponse(
            query=result['query'],
            expanded_query=result['expanded_query'],
            response=result['response'],
            sources=result['sources'],
            similarity_scores=result['similarity_scores'],
            retrieval_time=result['retrieval_time'],
            generation_time=result['generation_time']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando consulta: {str(e)}")

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None)
):
    """Subir y procesar un documento"""
    try:
        # Leer contenido del archivo
        content = await file.read()
        
        # Procesar según el tipo de archivo
        if file.filename.endswith('.txt'):
            text_content = content.decode('utf-8')
        elif file.filename.endswith('.json'):
            json_data = json.loads(content.decode('utf-8'))
            text_content = json.dumps(json_data, indent=2, ensure_ascii=False)
        else:
            # Para otros tipos, intentar decodificar como texto
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400, 
                    detail="Tipo de archivo no soportado. Use archivos de texto (.txt) o JSON (.json)"
                )
        
        # Procesar metadata si se proporciona
        doc_metadata = {}
        if metadata:
            try:
                doc_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                doc_metadata = {"description": metadata}
        
        # Agregar metadata del archivo
        doc_metadata.update({
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content)
        })
        
        # Agregar documento al sistema RAG
        chunks_added = rag_system.add_document(
            content=text_content,
            source=file.filename,
            metadata=doc_metadata
        )
        
        return {
            "message": f"Documento '{file.filename}' procesado exitosamente",
            "chunks_added": chunks_added,
            "filename": file.filename,
            "size": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando documento: {str(e)}")

@app.post("/documents/text")
async def add_text_document(document: DocumentUpload):
    """Agregar un documento de texto directamente"""
    try:
        if not document.content.strip():
            raise HTTPException(status_code=400, detail="El contenido no puede estar vacío")
        
        chunks_added = rag_system.add_document(
            content=document.content,
            source=document.source,
            metadata=document.metadata
        )
        
        return {
            "message": f"Documento '{document.source}' agregado exitosamente",
            "chunks_added": chunks_added,
            "source": document.source
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error agregando documento: {str(e)}")

@app.get("/sources", response_model=List[str])
async def get_sources():
    """Obtener lista de todas las fuentes disponibles"""
    try:
        return rag_system.get_sources()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo fuentes: {str(e)}")

@app.delete("/sources/{source_name}")
async def delete_source(source_name: str):
    """Eliminar una fuente específica"""
    try:
        sources = rag_system.get_sources()
        if source_name not in sources:
            raise HTTPException(status_code=404, detail=f"Fuente '{source_name}' no encontrada")
        
        rag_system.delete_source(source_name)
        
        return {
            "message": f"Fuente '{source_name}' eliminada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando fuente: {str(e)}")

@app.get("/config")
async def get_configuration():
    """Obtener configuración actual del sistema"""
    return {
        "db_type": settings.db_type,
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "similarity_top_k": settings.similarity_top_k,
        "temperature": settings.temperature
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
