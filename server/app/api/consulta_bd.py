"""Endpoints de consulta de base de datos (solo administradores).

Permite ejecutar consultas SELECT seguras para consultar información
directamente de la base de datos. Está protegido contra inyección SQL
y operaciones destructivas (DELETE, UPDATE, DROP, etc.).
"""

import re
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_current_user, requerir_permiso
from app.models.security import Usuario

router = APIRouter(prefix="/api/v1/consulta", tags=["Consulta de base de datos"])

# Palabras prohibidas (no permitir en consultas)
PALABRAS_PROHIBIDAS = [
    r"\bDROP\b", r"\bDELETE\b", r"\bUPDATE\b", r"\bINSERT\b",
    r"\bALTER\b", r"\bTRUNCATE\b", r"\bCREATE\b", r"\bGRANT\b",
    r"\bREVOKE\b", r"\bEXEC\b", r"\bEXECUTE\b", r"\bMERGE\b",
    r"\bBACKUP\b", r"\bRESTORE\b", r"\bBULK\b", r"\bOPENROWSET\b",
]


def _validar_consulta_segura(sql: str) -> None:
    """Valida que la consulta sea solo SELECT y no contenga operaciones peligrosas."""
    sql_upper = sql.upper().strip()

    # Debe empezar con SELECT
    if not sql_upper.startswith("SELECT"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten consultas SELECT.",
        )

    # No permitir palabras prohibidas
    for patron in PALABRAS_PROHIBIDAS:
        if re.search(patron, sql_upper):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La consulta contiene una operación no permitida: {patron}",
            )

    # No permitir punto y coma múltiple (evitar inyección de múltiples sentencias)
    if sql.count(";") > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se permiten múltiples sentencias SQL.",
        )


@router.post("/ejecutar", response_model=dict)
def ejecutar_consulta(
    datos: dict,
    db: Session = Depends(get_db),
    _: Usuario = Depends(requerir_permiso("consulta_bd.ejecutar")),
):
    """Ejecuta una consulta SELECT segura y devuelve los resultados."""
    sql = datos.get("consulta", "").strip()

    if not sql:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La consulta no puede estar vacía.",
        )

    _validar_consulta_segura(sql)

    try:
        resultado = db.execute(text(sql))
        columnas = list(resultado.keys())
        filas = resultado.fetchall()

        # Convertir a lista de diccionarios para JSON
        datos_salida = []
        for fila in filas:
            fila_dict = {}
            for i, col in enumerate(columnas):
                valor = fila[i]
                # Convertir tipos no serializables a string
                if hasattr(valor, "isoformat"):
                    valor = valor.isoformat()
                elif isinstance(valor, bytes):
                    valor = str(valor)
                elif valor is None:
                    valor = ""
                fila_dict[col] = valor
            datos_salida.append(fila_dict)

        return {
            "columnas": columnas,
            "filas": datos_salida,
            "total": len(datos_salida),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en la consulta: {str(e)}",
        )
