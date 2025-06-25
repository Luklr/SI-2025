import os
from langchain_community.utilities import SQLDatabase


class Database:
    DATABASE_URL = f"sqlite:///{os.getenv('DB_PATH', './universidad.db')}"

    @classmethod
    def get_engine(cls) -> SQLDatabase:
        # Si no existe la BD, la crea ejecutando create_db.py
        try:
            from . import create_db  # Importa el script que crea la base de datos
        except ImportError:
            print("Error al importar el módulo de creación de base de datos. Asegúrate de que 'create_db.py' existe en el directorio correcto.")
            raise
        db_path = os.getenv('DB_PATH', './universidad.db')
        create_db.crear_base_datos_universidad(db_path)
        return SQLDatabase.from_uri(cls.DATABASE_URL)
