#!/usr/bin/env python3
"""
Script de demostración del Sistema RAG
Carga datos de ejemplo y realiza consultas de prueba
"""
import requests
import json
import time
import os
from pathlib import Path

API_BASE = "http://localhost:8000"

def wait_for_server():
    """Espera a que el servidor esté disponible"""
    print("🔄 Esperando a que el servidor esté disponible...")
    for i in range(30):  # Esperar hasta 30 segundos
        try:
            response = requests.get(f"{API_BASE}/health")
            if response.status_code == 200:
                print("✅ Servidor disponible!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    print("❌ No se pudo conectar al servidor")
    return False

def load_example_documents():
    """Carga documentos de ejemplo"""
    print("\n📚 Cargando documentos de ejemplo...")
    
    # Documento 1: Texto sobre IA
    with open("data/ejemplo_ia.txt", "r", encoding="utf-8") as f:
        content = f.read()
    
    response = requests.post(
        f"{API_BASE}/documents/text",
        json={
            "content": content,
            "source": "introduccion_ia.txt",
            "metadata": {"tipo": "educativo", "tema": "inteligencia artificial"}
        }
    )
    
    if response.status_code == 200:
        print("✅ Documento de IA cargado exitosamente")
    else:
        print(f"❌ Error cargando documento de IA: {response.text}")
    
    # Documento 2: JSON sobre sistemas inteligentes
    with open("data/sistemas_inteligentes.json", "r", encoding="utf-8") as f:
        content = f.read()
    
    response = requests.post(
        f"{API_BASE}/documents/text",
        json={
            "content": content,
            "source": "sistemas_inteligentes.json",
            "metadata": {"tipo": "referencia", "formato": "json"}
        }
    )
    
    if response.status_code == 200:
        print("✅ Documento de Sistemas Inteligentes cargado exitosamente")
    else:
        print(f"❌ Error cargando documento de Sistemas Inteligentes: {response.text}")

def run_demo_queries():
    """Ejecuta consultas de demostración"""
    print("\n🎯 Ejecutando consultas de demostración...")
    
    demo_queries = [
        "¿Cuáles son los principales beneficios de la inteligencia artificial?",
        "¿Qué desafíos enfrentan los sistemas inteligentes?",
        "¿En qué sectores se aplican los sistemas inteligentes?",
        "¿Cuáles son las tecnologías clave en IA?",
        "¿Cómo funciona el machine learning?",
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{'='*60}")
        print(f"🔍 Consulta {i}: {query}")
        print('='*60)
        
        response = requests.post(
            f"{API_BASE}/query",
            json={"query": query}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"📝 Respuesta:")
            print(f"   {data['response']}")
            print(f"\n📊 Métricas:")
            print(f"   • Tiempo de recuperación: {data['retrieval_time']:.3f}s")
            print(f"   • Tiempo de generación: {data['generation_time']:.3f}s")
            print(f"   • Fuentes consultadas: {len(data['sources'])}")
            
            if data.get('expanded_query') and data['expanded_query'] != query:
                print(f"\n🔍 Consulta expandida:")
                print(f"   {data['expanded_query']}")
            
            if data['sources']:
                print(f"\n📚 Fuentes:")
                for j, source in enumerate(data['sources'], 1):
                    similarity = data['similarity_scores'][j-1] if j-1 < len(data['similarity_scores']) else 0
                    print(f"   {j}. {source} (similitud: {similarity:.1%})")
        else:
            print(f"❌ Error en consulta: {response.text}")
        
        time.sleep(2)  # Pausa entre consultas

def show_system_status():
    """Muestra el estado del sistema"""
    print("\n📊 Estado del Sistema:")
    print("="*40)
    
    # Health check
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Estado: {data['status']}")
            print(f"🗄️  Base de datos: {data['db_type']}")
            print(f"📚 Fuentes disponibles: {data['sources_count']}")
        else:
            print("❌ Sistema no disponible")
    except Exception as e:
        print(f"❌ Error conectando al sistema: {e}")
    
    # Configuración
    try:
        response = requests.get(f"{API_BASE}/config")
        if response.status_code == 200:
            config = response.json()
            print(f"\n⚙️  Configuración:")
            print(f"   • Modelo LLM: {config['llm_model']}")
            print(f"   • Modelo embeddings: {config['embedding_model']}")
            print(f"   • Tamaño de chunks: {config['chunk_size']}")
            print(f"   • Top K resultados: {config['similarity_top_k']}")
    except Exception as e:
        print(f"❌ Error obteniendo configuración: {e}")

def main():
    """Función principal de demostración"""
    print("🚀 Sistema RAG - Demostración")
    print("="*50)
    
    # Verificar si el servidor está ejecutándose
    if not wait_for_server():
        print("\n❌ El servidor no está disponible.")
        print("   Asegúrate de haber ejecutado './start.sh' primero")
        return
    
    # Mostrar estado inicial
    show_system_status()
    
    # Preguntar si cargar documentos de ejemplo
    response = input("\n¿Deseas cargar los documentos de ejemplo? (y/n): ").lower()
    if response in ['y', 'yes', 's', 'si', '']:
        load_example_documents()
        time.sleep(1)
        show_system_status()
    
    # Preguntar si ejecutar consultas de demostración
    response = input("\n¿Deseas ejecutar las consultas de demostración? (y/n): ").lower()
    if response in ['y', 'yes', 's', 'si', '']:
        run_demo_queries()
    
    # Información final
    print(f"\n{'='*60}")
    print("🎉 Demostración completada!")
    print(f"{'='*60}")
    print("🌐 Interfaz web: http://localhost:8000")
    print("📖 Documentación API: http://localhost:8000/docs")
    print("🛠️  Para personalizar, edita el archivo .env")
    print("\n¡Gracias por probar el Sistema RAG!")

if __name__ == "__main__":
    main()
