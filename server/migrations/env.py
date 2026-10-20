"""Configuración de entorno de Alembic para Hamelín RH."""

import sys
from pathlib import Path

# Asegurar que la raíz del proyecto esté en sys.path para importar app.*
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

# Importar configuración y metadata de modelos
from app.core.config import settings
from app.core.database import Base
from app.models import security, catalogs, employees, attendance, incidents, payroll  # noqa: F401

# Interpretar el archivo de configuración de Alembic para logging
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Sobrescribir la URL de conexión con la variable de entorno
config.set_main_option("sqlalchemy.url", settings.database_url)

# Metadata de todos los modelos para autogenerar migraciones
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecutar migraciones en modo offline (sin conexión a BD)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecutar migraciones en modo online (con conexión a BD)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
