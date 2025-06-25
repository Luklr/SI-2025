import os
from typing_extensions import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import START, StateGraph
from database.database import Database
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool


class EstadoRAGSQL(TypedDict):
    pregunta: str               # Pregunta original del usuario
    pregunta_expandida: str     # Pregunta expandida/mejorada
    consulta_sql: str          # Consulta SQL generada
    resultado_sql: str         # Resultado de la consulta
    respuesta: str             # Respuesta final en lenguaje natural
    schema_info: str  # Información del esquema de la DB

class SalidaSQL(TypedDict):
    """Consulta SQL generada."""
    consulta: str

class RagSystem:    
    def __init__(self, api_key: str|None):
        self.api_key = api_key
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("LLM_MODEL", "gemini-2.0-flash"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
            google_api_key=self.api_key,
        )
        # self.embeddings = GoogleGenerativeAIEmbeddings(
        #     model="models/text-embedding-004"
        # )
        self.db: SQLDatabase = Database.get_engine()
        self.schema_info: str = self.db.get_table_info()

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
        prompt_expansion = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
            Eres un experto en análisis de consultas de bases de datos de universidades. Tu tarea es expandir y mejorar la pregunta del usuario para que sea más específica y completa, considerando el contexto de una base de datos universitaria.
            
            Contexto de la base de datos:
            - Tabla 'estudiantes': información personal y académica de estudiantes
            - Tabla 'cursos': información sobre materias y profesores
            - Tabla 'inscripciones': relación entre estudiantes y cursos con calificaciones
            
            Expande la pregunta agregando contexto relevante pero manteniendo la intención original.
            Si la pregunta ya es específica, mantenla igual.

            REGLAS:
            1. Si la pregunta es clara, NO la cambies
            2. Solo agrega contexto si es necesario para claridad
            3. Mantén la intención original
            """,
                ),
                # ("human", "Pregunta original: {pregunta}\n\nPregunta expandida:"),
                ("human", "{pregunta}"),
            ]
        )
        
        chain = prompt_expansion | self.llm
        resultado = chain.invoke({"pregunta": estado["pregunta"]})
        return {"pregunta_expandida": resultado.content}

    def generar_sql(self, estado: EstadoRAGSQL) -> dict:
        """
        Genera consulta SQL automáticamente a partir de la pregunta en lenguaje natural
        """        
        # Prompt para generación de SQL 
        prompt_sql = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
            Dado una pregunta de entrada, crea una consulta {dialect} sintácticamente correcta para ejecutar.
             
            INSTRUCCIONES:
            A menos que el usuario especifique en su pregunta un número específico de ejemplos que desea obtener, siempre limita tu consulta a un máximo de {top_k} resultados. Si piden "todos", NO uses LIMIT.

            Puedes ordenar los resultados por una columna relevante para devolver los ejemplos más interesantes.
            
            Nunca consultes todas las columnas de una tabla específica, solo solicita las pocas columnas  relevantes dada la pregunta.
            
            Presta atención a usar solo los nombres de columnas que puedes ver en la descripción del esquema.
             
            Ten cuidado de no consultar columnas que no existen. También, presta atención a qué columna está en qué tabla.
            
            Solo usa las siguientes tablas:
            {table_info}
            
            IMPORTANTE: Responde SOLO con la consulta SQL, sin explicaciones adicionales.
            """,
                ),
                # ("human", "Pregunta: {pregunta}"),
                ("human", "{pregunta}"),
            ]
        )
        
        # Usar structured output para obtener SQL limpio
        llm_estructurado = self.llm.with_structured_output(SalidaSQL)
        
        # Preparar el prompt con información del esquema
        prompt_formateado = prompt_sql.invoke({
            "dialect": self.db.dialect,
            "top_k": 10,
            "table_info": self.schema_info,
            "pregunta": estado.get("pregunta_expandida", estado["pregunta"])
        })
        
        resultado = llm_estructurado.invoke(prompt_formateado)
        return {
            "consulta_sql": resultado["consulta"],
            "contexto_esquema": self.schema_info
        }

    def ejecutar_sql(self, estado: EstadoRAGSQL) -> dict:
        """
        Ejecuta la consulta SQL generada en la base de datos
        """
        ejecutor_sql = QuerySQLDatabaseTool(db=self.db)

        try:
            resultado = ejecutor_sql.invoke(estado["consulta_sql"])
            return {"resultado_sql": resultado}
        except Exception as e:
            return {"resultado_sql": f"Error al ejecutar SQL: {str(e)}"}

    def generar_respuesta(self, estado: EstadoRAGSQL) -> dict:
        """
        Genera respuesta en lenguaje natural basada en los resultados de la consulta SQL
        """

        prompt_respuesta = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
            Eres un asistente experto que ayuda a interpretar resultados de una base de datos universitaria.
            Dada una pregunta del usuario, la consulta SQL ejecutada y su resultado,
            proporciona una respuesta clara y útil en lenguaje natural.
            
            INSTRUCCIONES:
            1. Responde de manera conversacional y amigable
            2. Incluye los datos más relevantes del resultado
            3. Si hay múltiples resultados, presenta un resumen claro
            4. Si no hay resultados, explica por qué podría ser
            5. Mantén la respuesta concisa pero informativa
            6. NO menciones limitaciones de LIMIT ni nada relacionado con SQL o conceptos técnicos. El usuario objetivo no es técnico ni conoce ni debe conocer sobre la implementación de la base de datos.
            """,
                ),
                (
                    "human",
                    """
            Pregunta del usuario: {pregunta}
            Consulta SQL ejecutada: {consulta_sql}
            Resultado SQL: {resultado_sql}
            
            Respuesta en lenguaje natural:
            """,
                ),
            ]
        )
        
        chain = prompt_respuesta | self.llm
        resultado = chain.invoke({
            "pregunta": estado["pregunta"],
            "consulta_sql": estado["consulta_sql"],
            "resultado_sql": estado["resultado_sql"]
        })
        return {"respuesta": resultado.content}

    def response(self, consulta: str):
        # Ejecutar el pipeline completo
        resultado_completo = None
        
        for paso in self.grafo_rag_sql.stream(
            {"pregunta": consulta}, stream_mode="updates"
        ):
            for nombre_nodo, datos in paso.items():
                if nombre_nodo == "expandir_consulta":
                    print("🔍 **Expansión de consulta:**")
                    print(f"   Pregunta expandida: {datos['pregunta_expandida']}\n")
                
                elif nombre_nodo == "generar_sql":
                    print("💾 **Generación SQL:**")
                    print(f"   ```sql\n   {datos['consulta_sql']}\n   ```\n")
                
                elif nombre_nodo == "ejecutar_sql":
                    print("⚡ **Ejecución SQL:**")
                    print(f"   Resultado: {datos['resultado_sql']}\n")
                
                elif nombre_nodo == "generar_respuesta":
                    print("💬 **Respuesta final:**")
                    print(f"   {datos['respuesta']}\n")
                    resultado_completo = datos['respuesta']
        
        print("✅ **Proceso RAG SQL completado.**")
        return resultado_completo