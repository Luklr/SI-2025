Librerías recomendadas:
- PandasAI
- VannaAI

1. Arquitectura
La arquitectura de tres módulos (Expansión de Consulta, Recuperación, Generación) es un marco sólido para diseñar tu sistema, incluso si la "base de conocimiento" es una base de datos estructurada

2. Manejo de Consultas en Lenguaje Natural (Query Expansion):
◦ Para que un LLM consulte eficazmente una base de datos, la consulta en lenguaje natural del usuario a menudo necesita ser optimizada para la recuperación. El Módulo de Expansión de Consulta del paper es crucial aquí.
◦ Podrías adaptar el uso de Flan-T5 (o un modelo similar) para que, en lugar de generar "keywords" para documentos, genere condiciones de búsqueda, nombres de tablas/columnas relevantes o incluso partes de consultas SQL/NoSQL a partir de la pregunta del usuario. Esto "traduciría" el lenguaje natural en un formato más apto para la base de datos o el motor de búsqueda vectorial que uses.

3. Recuperación Eficiente de Información (Retrieval Module):
◦ El paper menciona FAISS para búsquedas de similitud en espacios de alta dimensión, y la consigna del TP de SI también sugiere "FAISS". Esto es directamente aplicable.
◦ En lugar de "chunks de documentos", podrías tratar los registros, filas o subconjuntos relevantes de tu base de datos como las "unidades" a indexar y recuperar. Para esto, necesitarías:
    ▪ Embeddings: Usar un Sentence Transformer (como el all-MiniLM-L6-v2 que usan) para crear embeddings de tus datos de la base de datos (ej. descripciones de productos, campos específicos, resúmenes de entradas). Estos embeddings representarían el "conocimiento" de tu base de datos en un formato vectorial.
    ▪ Base Vectorial: FAISS (o Chroma, como también sugiere la consigna de SI) se usaría como tu "motor de búsqueda" para encontrar los registros de la base de datos más semánticamente similares a la consulta del usuario, basada en los embeddings.

Prompt Design: Como el paper destaca, el diseño del prompt es crucial. Debes experimentar con prompts que le digan al LLM exactamente cómo debe usar la información recuperada de la base de datos para construir su respuesta. Por ejemplo: "Dada la siguiente información de la base de datos: [datos recuperados]. Responde a la pregunta: [consulta del usuario]." También puedes guiarlo sobre el formato de la respuesta (ej. "Solo proporciona datos de la base de datos").
