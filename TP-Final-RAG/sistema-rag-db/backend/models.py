"""
Modelos de datos para el sistema RAG
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

Base = declarative_base()

class DocumentChunk(Base):
    """Modelo para almacenar chunks de documentos con sus embeddings"""
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    source = Column(String(255), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding_vector = Column(Text)  # JSON serializado del vector
    metadata = Column(Text)  # JSON serializado de metadata adicional
    created_at = Column(DateTime, default=datetime.utcnow)

class QueryLog(Base):
    """Modelo para almacenar logs de consultas"""
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    original_query = Column(Text, nullable=False)
    expanded_query = Column(Text)
    response = Column(Text)
    similarity_score = Column(Float)
    retrieval_time = Column(Float)
    generation_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

# Modelos Pydantic para API
class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5
    
class QueryResponse(BaseModel):
    query: str
    expanded_query: Optional[str]
    response: str
    sources: List[str]
    similarity_scores: List[float]
    retrieval_time: float
    generation_time: float

class DocumentUpload(BaseModel):
    content: str
    source: str
    metadata: Optional[dict] = None
