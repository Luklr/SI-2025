"""
Configuración principal del sistema RAG con bases de datos
"""
from pathlib import Path
from pydantic import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str = ""
    
    # Database Configuration
    db_type: Literal["sqlite", "postgresql"] = "sqlite"
    sqlite_db_path: str = "./data/sistema_rag.db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "sistema_rag"
    postgres_user: str = ""
    postgres_password: str = ""
    
    # RAG Configuration
    chunk_size: int = 512
    chunk_overlap: int = 50
    similarity_top_k: int = 5
    embedding_model: str = "text-embedding-ada-002"
    llm_model: str = "gpt-3.5-turbo"
    temperature: float = 0.1
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def database_url(self) -> str:
        """Construye la URL de la base de datos según el tipo configurado"""
        if self.db_type == "sqlite":
            # Crear directorio si no existe
            db_path = Path(self.sqlite_db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{db_path.absolute()}"
        else:
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

# Instancia global de configuración
settings = Settings()
