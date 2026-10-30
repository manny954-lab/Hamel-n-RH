"""Configuración de la base de datos y sesiones SQLAlchemy."""

from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.core.config import settings


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos ORM."""

    pass


# SQLite requiere check_same_thread=False porque FastAPI atiende peticiones en
# hilos distintos. Para otros motores (postgresql) se ignora el argumento.
_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    pool_pre_ping=True,
    future=True,
)


@event.listens_for(engine, "connect")
def _configurar_sqlite(dbapi_connection, connection_record):  # noqa: ARG001
    """Aplica pragmas de SQLite: WAL (lectura/escritura concurrente) y busy_timeout.

    Así el servidor y el semillero pueden compartir el mismo archivo .db sin
    bloquearse mutuamente, y todo funciona sin servidor PostgreSQL externo.
    """
    if settings.database_url.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

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
    # Importar TODOS los modelos para que queden registrados en la metadata de
    # Base antes de crear las tablas.
    import app.models  # noqa: F401
    import app.models.security  # noqa: F401
    import app.models.catalogs  # noqa: F401
    import app.models.employees  # noqa: F401
    import app.models.attendance  # noqa: F401
    import app.models.incidents  # noqa: F401
    import app.models.payroll  # noqa: F401

    Base.metadata.create_all(bind=engine)
