import os
from dotenv import load_dotenv
from typing_extensions import TypedDict, Annotated
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import START, StateGraph
from database.database import Database
import google.generativeai as genai


class EstadoRAGSQL(TypedDict):
    pregunta: str               # Pregunta original del usuario
    pregunta_expandida: str     # Pregunta expandida/mejorada
    consulta_sql: str          # Consulta SQL generada
    resultado_sql: str         # Resultado de la consulta
    respuesta: str             # Respuesta final en lenguaje natural
    contexto_esquema: str      # Información del esquema de la DB

class SalidaSQL(TypedDict):
    """Consulta SQL generada."""
    consulta: Annotated[str, "", "Consulta SQL sintácticamente válida."]

class RagSystem:
    def __init__(self, db):
        load_dotenv()
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            convert_system_message_to_human=True,
            google_api_key=self.api_key,
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004"
        )
        self.db = Database.get_engine()


        # Orquestación de LangGraph
        self.constructor_graph = StateGraph(EstadoRAGSQL)

        self.constructor_graph.add_node("expandir_consulta", self.expandir_consulta)
        self.constructor_graph.add_node("generar_sql", self.generar_sql)
        self.constructor_graph.add_node("ejecutar_sql", self.ejecutar_sql)
        self.constructor_graph.add_node("generar_respuesta", self.generar_respuesta)

        self.constructor_graph.add_edge(START, "expandir_consulta")
        self.constructor_graph.add_edge("expandir_consulta", "generar_sql")
        self.constructor_graph.add_edge("generar_sql", "ejecutar_sql")
        self.constructor_graph.add_edge("ejecutar_sql", "generar_respuesta")

        self.grafo_rag_sql = self.constructor_graph.compile()

        
    
    def expandir_consulta(self, estado: EstadoRAGSQL) -> dict:
        """
        Expande y mejora la consulta del usuario para obtener mejores resultados SQL
        """
        prompt_expansion = ChatPromptTemplate.from_messages([
            ("system", """
            Eres un experto en análisis de consultas de bases de datos. Tu tarea es expandir y mejorar 
            la pregunta del usuario para que sea más específica y completa, considerando el contexto 
            de una base de datos universitaria.
            
            Contexto de la base de datos:
            - Tabla 'estudiantes': información personal y académica de estudiantes
            - Tabla 'cursos': información sobre materias y profesores
            - Tabla 'inscripciones': relación entre estudiantes y cursos con calificaciones
            
            Expande la pregunta agregando contexto relevante pero manteniendo la intención original.
            Si la pregunta ya es específica, mantenla igual.
            """),
            ("human", "Pregunta original: {pregunta}\n\nPregunta expandida:")
        ])
        
        chain = prompt_expansion | self.llm
        resultado = chain.invoke({"pregunta": estado["pregunta"]})
        
        return {"pregunta_expandida": resultado.content}

    def generar_sql(self, estado: EstadoRAGSQL) -> dict:
        """
        Genera consulta SQL automáticamente a partir de la pregunta en lenguaje natural
        """
        # Obtener información del esquema
        schema_info: str = self.db.get_table_info()
        
        # Prompt para generación de SQL siguiendo mejores prácticas de LangChain
        prompt_sql = ChatPromptTemplate.from_messages([
            ("system", """
            Dado una pregunta de entrada, crea una consulta {dialect} sintácticamente correcta para ejecutar.
            A menos que el usuario especifique en su pregunta un número específico de ejemplos que desea obtener,
            siempre limita tu consulta a un máximo de {top_k} resultados.
            
            Puedes ordenar los resultados por una columna relevante para devolver los ejemplos más interesantes.
            
            Nunca consultes todas las columnas de una tabla específica, solo solicita las pocas columnas 
            relevantes dada la pregunta.
            
            Presta atención a usar solo los nombres de columnas que puedes ver en la descripción del esquema.
            Ten cuidado de no consultar columnas que no existen. También, presta atención a qué columna 
            está en qué tabla.
            
            Solo usa las siguientes tablas:
            {table_info}
            
            IMPORTANTE: Responde SOLO con la consulta SQL, sin explicaciones adicionales.
            """),
            ("human", "Pregunta: {pregunta}")
        ])
        
        # Usar structured output para obtener SQL limpio
        llm_estructurado = self.llm.with_structured_output(SalidaSQL)
        
        # Preparar el prompt con información del esquema
        prompt_formateado = prompt_sql.invoke({
            "dialect": self.db.dialect,
            "top_k": 10,
            "table_info": schema_info,
            "pregunta": estado.get("pregunta_expandida", estado["pregunta"])
        })
        
        resultado = llm_estructurado.invoke(prompt_formateado)
        
        return {
            "consulta_sql": resultado["consulta"],
            "contexto_esquema": schema_info
        }

    def ejecutar_sql(self, estado: EstadoRAGSQL) -> dict:
        """
        Ejecuta la consulta SQL generada en la base de datos
        """
        # Crear herramienta de ejecución
        ejecutor_sql = self.db.get
        
        try:
            resultado = ejecutor_sql.invoke(estado["consulta_sql"])
            return {"resultado_sql": resultado}
        except Exception as e:
            return {"resultado_sql": f"Error al ejecutar SQL: {str(e)}"}

    def format_results_as_text(self, rows, columns):
        texts = []
        for row in rows:
            line = ", ".join(f"{col}: {val}" for col, val in zip(columns, row))
            texts.append(line)
        return texts  # devuelve lista de textos

    def generar_respuesta(self, estado: EstadoRAGSQL) -> dict:
        """
        Genera respuesta en lenguaje natural basada en los resultados de la consulta SQL
        """

        prompt_respuesta = ChatPromptTemplate.from_messages([
            ("system", """
            Eres un asistente experto que ayuda a interpretar resultados de bases de datos.
            Dada una pregunta del usuario, la consulta SQL ejecutada y su resultado,
            proporciona una respuesta clara y útil en lenguaje natural.
            
            INSTRUCCIONES:
            1. Responde de manera conversacional y amigable
            2. Incluye los datos más relevantes del resultado
            3. Si hay múltiples resultados, presenta un resumen claro
            4. Si no hay resultados, explica por qué podría ser
            5. Mantén la respuesta concisa pero informativa
            """),
            ("human", """
            Pregunta del usuario: {pregunta}
            Consulta SQL ejecutada: {consulta_sql}
            Resultado SQL: {resultado_sql}
            
            Respuesta en lenguaje natural:
            """)
        ])
        
        chain = prompt_respuesta | self.llm
        resultado = chain.invoke({
            "pregunta": estado["pregunta"],
            "consulta_sql": estado["consulta_sql"],
            "resultado_sql": estado["resultado_sql"]
        })
        
        return {"respuesta": resultado.content}

    def response(self, consulta:str):
        resultado = self.grafo_rag_sql.stream({"pregunta": consulta}, stream_mode="updates")
        return resultado