"""Configuración de pruebas del servidor Hamelín RH.

Usa una base de datos de prueba separada (hamelin_rh_test) en PostgreSQL.
Cada prueba obtiene una sesión con transacción que se revierte al final,
manteniendo el esquema limpio entre pruebas.
"""

import os
from typing import Generator

# Forzar URL de base de datos de prueba ANTES de importar la app.
os.environ["DATABASE_URL"] = "postgresql+psycopg2://postgres@localhost:5433/hamelin_rh_test"
os.environ["ENVIRONMENT"] = "testing"

import pytest  # noqa: E402

from app.core.database import Base, engine, SessionLocal  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def crear_esquema_prueba():
    """Crea todas las tablas una vez al inicio de la sesión de pruebas."""
    import app.models  # noqa: F401  (registra modelos en Base.metadata)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db() -> Generator:
    """Sesión de base de datos con transacción revertible por prueba."""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
