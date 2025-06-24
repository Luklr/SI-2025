

class QueryExpansionModule:
    """Módulo 1: Expansión de Consulta - Optimiza la consulta del usuario"""

    def __init__(self):
        self.llm = OpenAI(model=settings.llm_model, temperature=0.1)

    def expand_query(self, original_query: str) -> str:
        """
        Expande la consulta original para mejorar la recuperación
        Basado en las técnicas del paper de Tolosa
        """
        expansion_prompt = f"""
        Eres un experto en optimización de consultas para sistemas de recuperación de información.
        
        Consulta original: "{original_query}"
        
        Tu tarea es expandir esta consulta para mejorar la recuperación de información relevante de una base de datos.
        
        Debes:
        1. Identificar conceptos clave y términos relacionados
        2. Agregar sinónimos y variaciones del tema
        3. Incluir contexto adicional que pueda ser relevante
        4. Mantener la intención original de la consulta
        
        Devuelve SOLO la consulta expandida, sin explicaciones adicionales.
        
        Consulta expandida:
        """

        try:
            response = self.llm.complete(expansion_prompt)
            expanded_query = response.text.strip()
            return expanded_query if expanded_query else original_query
        except Exception as e:
            print(f"Error en expansión de consulta: {e}")
            return original_query
