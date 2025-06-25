from flask import Flask, send_file, Response, request
import os
from .rag_system import RagSystem
from dotenv import load_dotenv

app = Flask(__name__)

# FLASK
@app.route('/', methods=['GET'])
def serve_index():
    return send_file('../frontend/index.html')

@app.route('/query', methods=['GET'])
def query():
    """
    Endpoint para procesar consultas RAG SQL.
    """
    global rag_system
    user_query = request.args.get('q', "")
    if not user_query:
        return Response(response="No query provided", status=404)
    response = rag_system.response(user_query)
    return Response(response=response, status=200)

if __name__ == '__main__':
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    print(f"GOOGLE_API_KEY: {api_key}")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")
    rag_system = RagSystem(api_key)
    app.run(debug=False, port=5000)
    