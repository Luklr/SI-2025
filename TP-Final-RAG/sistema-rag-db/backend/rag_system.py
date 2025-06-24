"""
Sistema RAG con arquitectura de tres módulos:
1. Expansión de Consulta (Query Expansion)
2. Recuperación (Retrieval) 
3. Generación (Generation)
"""
import time
import os
from typing import List, Dict, Any, Optional
# from llama_index.core import Document
# from llama_index.core.node_parser import SentenceSplitter
# from llama_index.llms.openai import OpenAI
# from llama_index.embeddings.openai import OpenAIEmbedding
from .config import settings
from .database import db_manager


class RetrievalModule:
    """Módulo 2: Recuperación - Busca información relevante en la base de datos"""
    
    def __init__(self):
        self.embedding_model = OpenAIEmbedding(model=settings.embedding_model)
    
    def retrieve_relevant_chunks(
        self, 
        query: str, 
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Recupera chunks relevantes usando búsqueda por similitud semántica
        """
        if top_k is None:
            top_k = settings.similarity_top_k
        
        try:
            # Generar embedding de la consulta
            query_embedding = self.embedding_model.get_text_embedding(query)
            
            # Buscar chunks similares en la base de datos
            similar_chunks = db_manager.search_similar_chunks(
                query_embedding=query_embedding,
                top_k=top_k
            )
            
            return similar_chunks
            
        except Exception as e:
            print(f"Error en recuperación: {e}")
            return []

class GenerationModule:
    """Módulo 3: Generación - Genera respuesta usando LLM con contexto recuperado"""
    
    def __init__(self):
        self.llm = OpenAI(model=settings.llm_model, temperature=settings.temperature)
    
    def generate_response(
        self, 
        original_query: str,
        expanded_query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> str:
        """
        Genera respuesta final usando la consulta y el contexto recuperado
        Implementa las mejores prácticas del paper (Contrastive ICL y Focus Mode)
        """
        if not retrieved_chunks:
            return "No se encontró información relevante para responder a tu consulta."
        
        # Construir contexto a partir de los chunks recuperados
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            context_parts.append(
                f"[Fuente {i}: {chunk['source']}]\n"
                f"{chunk['content']}\n"
                f"(Relevancia: {chunk['similarity']:.3f})\n"
            )
        
        context = "\n".join(context_parts)
        
        # Prompt optimizado con técnicas del paper
        generation_prompt = f"""
        Eres un asistente inteligente especializado en proporcionar respuestas precisas y útiles basadas en información específica.
        
        CONSULTA ORIGINAL: {original_query}
        CONSULTA EXPANDIDA: {expanded_query}
        
        CONTEXTO RELEVANTE:
        {context}
        
        INSTRUCCIONES:
        1. Responde directamente a la consulta original del usuario
        2. Basa tu respuesta ÚNICAMENTE en el contexto proporcionado
        3. Si el contexto no contiene información suficiente, indícalo claramente
        4. Cita las fuentes cuando sea apropiado
        5. Sé preciso y conciso pero completo
        6. Si hay información contradictoria, señálala
        
        RESPUESTA:
        """
        
        try:
            response = self.llm.complete(generation_prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error en generación: {e}")
            return "Error al generar la respuesta. Por favor, intenta nuevamente."

class RAGSystem:
    """Sistema RAG completo que integra los tres módulos"""
    
    def __init__(self):
        self.query_expansion = QueryExpansionModule()
        self.retrieval = RetrievalModule()
        self.generation = GenerationModule()
        self.splitter = SentenceSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
    
    def process_query(self, query: str, max_results: int = None) -> Dict[str, Any]:
        """
        Procesa una consulta completa a través de los tres módulos
        """
        start_time = time.time()
        
        # Módulo 1: Expansión de Consulta
        expansion_start = time.time()
        expanded_query = self.query_expansion.expand_query(query)
        expansion_time = time.time() - expansion_start
        
        # Módulo 2: Recuperación
        retrieval_start = time.time()
        retrieved_chunks = self.retrieval.retrieve_relevant_chunks(
            expanded_query, 
            top_k=max_results or settings.similarity_top_k
        )
        retrieval_time = time.time() - retrieval_start
        
        # Módulo 3: Generación
        generation_start = time.time()
        response = self.generation.generate_response(
            query, 
            expanded_query, 
            retrieved_chunks
        )
        generation_time = time.time() - generation_start
        
        total_time = time.time() - start_time
        
        # Registrar en el log
        avg_similarity = sum(chunk['similarity'] for chunk in retrieved_chunks) / len(retrieved_chunks) if retrieved_chunks else 0.0
        
        db_manager.log_query(
            original_query=query,
            expanded_query=expanded_query,
            response=response,
            similarity_score=avg_similarity,
            retrieval_time=retrieval_time,
            generation_time=generation_time
        )
        
        return {
            'query': query,
            'expanded_query': expanded_query,
            'response': response,
            'sources': [chunk['source'] for chunk in retrieved_chunks],
            'similarity_scores': [chunk['similarity'] for chunk in retrieved_chunks],
            'retrieval_time': retrieval_time,
            'generation_time': generation_time,
            'total_time': total_time,
            'chunks_found': len(retrieved_chunks)
        }
    
    def add_document(self, content: str, source: str, metadata: Dict[str, Any] = None) -> int:
        """
        Añade un documento al sistema RAG
        """
        # Crear documento de LlamaIndex
        document = Document(text=content, metadata=metadata or {})
        
        # Dividir en chunks
        nodes = self.splitter.get_nodes_from_documents([document])
        
        chunks_added = 0
        for i, node in enumerate(nodes):
            # Generar embedding
            embedding = self.retrieval.embedding_model.get_text_embedding(node.text)
            
            # Almacenar en base de datos
            chunk_id = db_manager.store_document_chunk(
                content=node.text,
                source=source,
                chunk_index=i,
                embedding=embedding,
                metadata=metadata
            )
            chunks_added += 1
        
        return chunks_added
    
    def get_sources(self) -> List[str]:
        """Obtiene todas las fuentes disponibles"""
        return db_manager.get_all_sources()
    
    def delete_source(self, source: str):
        """Elimina una fuente del sistema"""
        db_manager.delete_source(source)

# Instancia global del sistema RAG
rag_system = RAGSystem()
