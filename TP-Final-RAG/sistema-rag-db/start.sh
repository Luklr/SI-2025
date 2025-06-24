#!/bin/bash
# Script para iniciar el Sistema RAG

echo "🚀 Iniciando Sistema RAG con Base de Datos"
echo "========================================="

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado. Por favor, instala Python 3.8 o superior."
    exit 1
fi

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

# Verificar archivo .env
if [ ! -f ".env" ]; then
    echo "⚙️  Creando archivo de configuración .env..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Edita el archivo .env y configura tu OPENAI_API_KEY"
    echo "   Archivo: $(pwd)/.env"
    echo ""
    read -p "Presiona Enter cuando hayas configurado tu API key..."
fi

# Crear directorio de base de datos si no existe
mkdir -p data

echo ""
echo "✅ Configuración completada!"
echo ""
echo "🌐 Iniciando servidor web en http://localhost:8000"
echo "   - Interfaz web: http://localhost:8000"
echo "   - API docs: http://localhost:8000/docs"
echo ""
echo "Para detener el servidor, presiona Ctrl+C"
echo ""

# Iniciar el servidor
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
