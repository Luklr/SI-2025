# from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase


class Database:
    DATABASE_URL = "sqlite:///./empresa_datos.db"

    @classmethod
    def get_engine(cls) -> SQLDatabase:
        return SQLDatabase.from_uri(cls.DATABASE_URL)
        # return create_engine(cls.DATABASE_URL)
