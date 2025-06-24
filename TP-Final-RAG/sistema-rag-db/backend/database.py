"""
Gestor de base de datos con soporte para SQLite y PostgreSQL
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator, List, Dict, Any
import json
import numpy as np
from .config import settings
from .models import Base, DocumentChunk, QueryLog

class DatabaseManager:
    """Gestor de conexiones y operaciones de base de datos"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Inicializa la conexión a la base de datos"""
        if settings.db_type == "sqlite":
            self.engine = create_engine(
                settings.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            self.engine = create_engine(
                settings.database_url,
                echo=False
            )
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Crear tablas si no existen
        Base.metadata.create_all(bind=self.engine)
    
    @contextmanager
    def get_db(self) -> Generator[Session, None, None]:
        """Context manager para obtener una sesión de base de datos"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def store_document_chunk(
        self, 
        content: str, 
        source: str, 
        chunk_index: int,
        embedding: List[float],
        metadata: Dict[str, Any] = None
    ) -> int:
        """Almacena un chunk de documento con su embedding"""
        with self.get_db() as db:
            chunk = DocumentChunk(
                content=content,
                source=source,
                chunk_index=chunk_index,
                embedding_vector=json.dumps(embedding),
                metadata=json.dumps(metadata or {})
            )
            db.add(chunk)
            db.commit()
            db.refresh(chunk)
            return chunk.id
    
    def search_similar_chunks(
        self, 
        query_embedding: List[float], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Busca chunks similares usando embeddings (implementación básica)"""
        with self.get_db() as db:
            chunks = db.query(DocumentChunk).all()
            
            similarities = []
            for chunk in chunks:
                if chunk.embedding_vector:
                    chunk_embedding = json.loads(chunk.embedding_vector)
                    # Calcular similitud coseno
                    similarity = self._cosine_similarity(query_embedding, chunk_embedding)
                    similarities.append({
                        'chunk': chunk,
                        'similarity': similarity
                    })
            
            # Ordenar por similitud y tomar los top_k
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            results = []
            for item in similarities[:top_k]:
                chunk = item['chunk']
                results.append({
                    'id': chunk.id,
                    'content': chunk.content,
                    'source': chunk.source,
                    'similarity': item['similarity'],
                    'metadata': json.loads(chunk.metadata) if chunk.metadata else {}
                })
            
            return results
    
    def log_query(
        self,
        original_query: str,
        expanded_query: str = None,
        response: str = None,
        similarity_score: float = None,
        retrieval_time: float = None,
        generation_time: float = None
    ) -> int:
        """Registra una consulta en el log"""
        with self.get_db() as db:
            log_entry = QueryLog(
                original_query=original_query,
                expanded_query=expanded_query,
                response=response,
                similarity_score=similarity_score,
                retrieval_time=retrieval_time,
                generation_time=generation_time
            )
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            return log_entry.id
    
    def get_all_sources(self) -> List[str]:
        """Obtiene todas las fuentes disponibles"""
        with self.get_db() as db:
            sources = db.query(DocumentChunk.source).distinct().all()
            return [source[0] for source in sources]
    
    def delete_source(self, source: str):
        """Elimina todos los chunks de una fuente específica"""
        with self.get_db() as db:
            db.query(DocumentChunk).filter(DocumentChunk.source == source).delete()
            db.commit()
    
    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calcula la similitud coseno entre dos vectores"""
        try:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except Exception:
            return 0.0

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()
