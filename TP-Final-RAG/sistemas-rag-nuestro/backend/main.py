from flask import Flask, send_file, Response
import os
from database.database import Database

# Configuración de APIs (reemplaza con tus claves)
os.environ["OPENAI_API_KEY"] = "sk-..."  # Tu clave de OpenAI
os.environ["GOOGLE_API_KEY"] = "..."  # Tu clave de Google

app = Flask(__name__)

# FLASK
@app.route('/', methods=['GET'])
def serve_index():
    return send_file('../frontend/index.html')

@app.route('/query', methods=['GET'])
def query():
    
    return Response(response="",status=200)

if __name__ == '__main__':
    engine = Database.get_engine()
    app.run(debug=False)
    