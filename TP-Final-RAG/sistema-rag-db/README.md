# 🔍 Sistema RAG con Base de Datos

Sistema de **Recuperación Aumentada por Generación (RAG)** que permite consultar bases de datos usando lenguaje natural. Implementa la arquitectura de tres módulos basada en las mejores prácticas de investigación en RAG.

## 🏗️ Arquitectura

El sistema implementa una arquitectura de **tres módulos** inspirada en el paper "Enhancing Retrieval-Augmented Generation: A Study of Best Practices":

### 1. 🔍 Módulo de Expansión de Consulta (Query Expansion)
- Optimiza la consulta del usuario para mejorar la recuperación
- Utiliza LLM para expandir términos y conceptos clave
- Mantiene la intención original de la consulta

### 2. 📚 Módulo de Recuperación (Retrieval)
- Búsqueda semántica usando embeddings de OpenAI
- Soporte para bases de datos SQLite y PostgreSQL intercambiables
- Indexación automática con FAISS para búsquedas eficientes

### 3. 🤖 Módulo de Generación (Generation)
- Generación de respuestas usando contexto recuperado
- Implementa técnicas de Contrastive ICL y Focus Mode
- Citas automáticas de fuentes y control de calidad

## 🚀 Características

- **Bases de datos intercambiables**: SQLite (local) o PostgreSQL (producción)
- **Interfaz web moderna**: Frontend HTML/CSS/JavaScript intuitivo
- **API RESTful completa**: Documentación automática con FastAPI
- **Procesamiento de documentos**: Soporte para TXT, JSON y más
- **Métricas en tiempo real**: Tiempos de recuperación y generación
- **Gestión de fuentes**: Agregar, listar y eliminar documentos
- **Logging completo**: Seguimiento de consultas y rendimiento

## 📋 Requisitos

- Python 3.8 o superior
- OpenAI API Key
- (Opcional) PostgreSQL para producción

## 🛠️ Instalación y Configuración

### Opción 1: Inicio Rápido (Recomendado)

```bash
# Clonar o descargar el proyecto
cd sistema-rag-db

# Ejecutar script de inicio automático
./start.sh
```

### Opción 2: Instalación Manual

```bash
# 1. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env y configurar OPENAI_API_KEY

# 4. Iniciar servidor
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Configuración de Variables de Entorno

Edita el archivo `.env`:

```bash
# OpenAI Configuration
OPENAI_API_KEY=tu_clave_de_openai_aqui

# Database Configuration  
DB_TYPE=sqlite  # sqlite o postgresql
SQLITE_DB_PATH=./data/sistema_rag.db

# Para PostgreSQL:
# DB_TYPE=postgresql
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DB=sistema_rag
# POSTGRES_USER=tu_usuario
# POSTGRES_PASSWORD=tu_password

# RAG Configuration
CHUNK_SIZE=512
CHUNK_OVERLAP=50
SIMILARITY_TOP_K=5
LLM_MODEL=gpt-3.5-turbo
TEMPERATURE=0.1
```

## 🎯 Uso del Sistema

### 1. Acceso Web
- Interfaz principal: http://localhost:8000
- Documentación API: http://localhost:8000/docs

### 2. Agregar Documentos

**Opción A: Interfaz Web**
- Ve a la pestaña "Documentos"
- Arrastra archivos o usa el botón "Seleccionar Archivo"
- O escribe texto directamente

**Opción B: API**
```bash
# Subir archivo
curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@tu_documento.txt"

# Agregar texto directo
curl -X POST "http://localhost:8000/documents/text" \
     -H "Content-Type: application/json" \
     -d '{"content": "Tu texto aquí", "source": "nombre_fuente"}'
```

### 3. Realizar Consultas

**Interfaz Web:**
- Escribe tu pregunta en lenguaje natural
- Ejemplo: "¿Cuáles son los beneficios de la inteligencia artificial?"

**API:**
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "¿Qué es la inteligencia artificial?"}'
```

## 📊 Ejemplos de Consultas

El sistema incluye documentos de ejemplo sobre IA y Sistemas Inteligentes. Prueba estas consultas:

- "¿Qué beneficios tiene la inteligencia artificial?"
- "¿Cuáles son los desafíos de los sistemas inteligentes?"
- "¿En qué sectores se aplica la IA?"
- "¿Qué tecnologías son clave en sistemas inteligentes?"

## 🏗️ Estructura del Proyecto

```
sistema-rag-db/
├── backend/
│   ├── __init__.py
│   ├── main.py           # API FastAPI
│   ├── config.py         # Configuración del sistema
│   ├── models.py         # Modelos de datos
│   ├── database.py       # Gestor de base de datos
│   └── rag_system.py     # Sistema RAG principal
├── frontend/
│   └── index.html        # Interfaz web
├── data/
│   ├── ejemplo_ia.txt    # Documento de ejemplo
│   └── sistemas_inteligentes.json
├── requirements.txt      # Dependencias Python
├── .env.example         # Ejemplo de configuración
├── start.sh            # Script de inicio
└── README.md           # Este archivo
```

## 🔧 API Endpoints

### Consultas
- `POST /query` - Procesar consulta en lenguaje natural
- `GET /health` - Estado del sistema

### Documentos
- `POST /documents/upload` - Subir archivo
- `POST /documents/text` - Agregar texto directo

### Gestión
- `GET /sources` - Listar fuentes disponibles
- `DELETE /sources/{source_name}` - Eliminar fuente
- `GET /config` - Ver configuración del sistema

## 🧪 Desarrollo y Personalización

### Cambiar el Modelo LLM
Edita `.env`:
```bash
LLM_MODEL=gpt-4  # o gpt-3.5-turbo-16k
```

### Usar PostgreSQL
```bash
DB_TYPE=postgresql
POSTGRES_HOST=tu_host
POSTGRES_PORT=5432
POSTGRES_DB=sistema_rag
POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_password
```

### Personalizar Chunking
```bash
CHUNK_SIZE=1024      # Tamaño de chunks más grande
CHUNK_OVERLAP=100    # Mayor solapamiento
SIMILARITY_TOP_K=8   # Más resultados por consulta
```

## 📈 Monitoreo y Logs

El sistema registra automáticamente:
- Consultas originales y expandidas
- Tiempos de recuperación y generación
- Puntuaciones de similitud
- Fuentes consultadas

Accede a las métricas en la interfaz web o consulta la base de datos directamente.

## 🛡️ Consideraciones de Seguridad

- Mantén tu `OPENAI_API_KEY` segura y nunca la compartas
- En producción, configura CORS específicamente
- Usa HTTPS para conexiones de base de datos remotas
- Considera implementar autenticación para la API

## 🤝 Contribuciones

Este sistema está diseñado para ser extensible. Algunas ideas para mejoras:

- Soporte para más tipos de documentos (PDF, Word, etc.)
- Integración con más modelos de embeddings
- Interfaz de administración avanzada
- Soporte para múltiples idiomas
- Integración con bases de datos vectoriales especializadas (Pinecone, Weaviate)

## 📚 Referencias

- [LlamaIndex Documentation](https://docs.llamaindex.ai)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- Paper: "Enhancing Retrieval-Augmented Generation: A Study of Best Practices"

## 📝 Licencia

Este proyecto se proporciona como material educativo para el Seminario "Agentes Inteligentes y LLM".

---

**¿Necesitas ayuda?**

1. Verifica que tu `OPENAI_API_KEY` esté configurada correctamente
2. Asegúrate de tener documentos agregados antes de hacer consultas
3. Revisa los logs en la terminal para mensajes de error detallados
4. Consulta la documentación de la API en http://localhost:8000/docs
