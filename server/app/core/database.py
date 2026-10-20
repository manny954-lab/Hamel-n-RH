"""Configuración de la base de datos y sesiones SQLAlchemy."""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.core.config import settings


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos ORM."""

    pass


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)


def get_db() -> Generator[Session, None, None]:
    """Generador de sesiones de base de datos para inyección en FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Crea todas las tablas definidas en los modelos.

    Útil para entornos de prueba o desarrollo inicial. En producción se deben
    aplicar las migraciones de Alembic.
    """
    # Importar modelos para que estén registrados en la metadata de Base.
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
