"""
Configuração do banco de dados SQLite via SQLAlchemy
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Caminho do banco: /data/honorarios.db em produção (Railway volume) ou ./honorarios.db localmente
DB_PATH = os.environ.get("DATABASE_PATH", "./honorarios.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Ativar WAL mode e foreign keys no SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency para injetar sessão do banco nas rotas"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Criar todas as tabelas se não existirem"""
    from .models import user as user_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
