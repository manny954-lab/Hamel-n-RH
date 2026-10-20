"""Aplicación FastAPI principal del servidor Hamelín RH."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import auth, usuarios, roles, catalogos, empleados, asistencia, incidencias, nomina, auditoria, reportes, consulta_bd


def create_app() -> FastAPI:
    app = FastAPI(
        title="Hamelín RH - API",
        description="API privada del sistema de control de asistencia, incidencias y prenómina para Cool Circle.",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(usuarios.router)
    app.include_router(roles.router)
    app.include_router(catalogos.router)
    app.include_router(empleados.router)
    app.include_router(asistencia.router)
    app.include_router(incidencias.router)
    app.include_router(nomina.router)
    app.include_router(auditoria.router)
    app.include_router(reportes.router)
    app.include_router(consulta_bd.router)
    app.include_router(consulta_bd.router)

    @app.get("/health", tags=["Salud"])
    def health():
        return {"status": "ok", "service": "hamelin-rh-api"}

    @app.get("/", tags=["Salud"])
    def root():
        return {"mensaje": "Hamelín RH API - servidor operativo"}

    return app


app = create_app()
