# Sistema RAG-SQL 🤖💾

Sistema de consultas en lenguaje natural sobre bases de datos usando LLM (Google Gemini).

## 🚀 Configuración Inicial

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```
O bien, instalar manualmente:
```bash
pip install flask langgraph langchain_google_genai langchain_core langchain_community sqlalchemy pandas python-dotenv typing_extensions
```

### 2. Configurar API Key
Crea un archivo `.env` en la raíz del proyecto:
```
GOOGLE_API_KEY=tu_api_key_aquí
```

### 3. Ejecutar el sistema
```bash
# Desde la raíz del proyecto, ejecuta:
python3 -m backend.main
```

## 📊 Datos de Ejemplo

La base de datos contiene tres tablas principales:

### 👨‍🎓 Estudiantes
- id, nombre, apellido, edad, carrera, promedio, fecha_ingreso

### 📚 Cursos
- id, nombre, creditos, profesor, departamento

### 📝 Inscripciones
- id, estudiante_id, curso_id, calificacion, semestre

Incluye datos de ejemplo para cada tabla, como estudiantes de distintas carreras, cursos de diferentes departamentos y varias inscripciones con calificaciones y semestres.

## 🤔 Ejemplos de Consultas

Puedes hacer preguntas como:
- "¿Cuántos estudiantes hay en Ingeniería Informática?"
- "¿Cuál es el promedio general de los estudiantes de Matemáticas?"
- "¿Qué cursos dicta el Dr. Smith?"
- "¿Quién obtuvo la calificación más alta en Algoritmos y Estructuras de Datos?"
- "¿Cuántos estudiantes se inscribieron en el semestre 2023-1?"
- "¿Qué estudiantes tienen promedio mayor a 9?"

## 🌐 Interfaz Web

El sistema incluye una interfaz web simple:
- Accede a `http://localhost:5000`
- Escribe tu pregunta en lenguaje natural
- Obtén respuestas basadas en los datos

## 🏗️ Arquitectura

1. **Expansión de consulta**: Mejora la pregunta del usuario
2. **Generación SQL**: Convierte la pregunta a SQL usando Gemini
3. **Ejecución**: Ejecuta la consulta en la base de datos
4. **Respuesta**: Genera respuesta en lenguaje natural

## 🔧 Tecnologías

- **LLM**: Google Gemini 2.0 Flash
- **Framework**: LangChain + LangGraph
- **Base de datos**: SQLite
- **Backend**: Flask
- **Frontend**: HTML/CSS/JavaScript
- **Framework**: LangChain + LangGraph
- **Base de datos**: SQLite
- **Backend**: Flask
- **Frontend**: HTML/CSS/JavaScript
