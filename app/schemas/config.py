"""Pydantic schemas for configuration endpoints (Departamentos & Secciones)"""

from pydantic import BaseModel, Field
from typing import List


class DepartamentoResponse(BaseModel):
    id_departamento: int
    nombre: str
    icono_name: str

    class Config:
        from_attributes = True


class SeccionResponse(BaseModel):
    id_seccion: int
    nombre: str
    icono_name: str

    class Config:
        from_attributes = True


class BulkDepartamentoResponse(BaseModel):
    count: int = Field(..., description="Number of records upserted")
    items: List[DepartamentoResponse]


class BulkSeccionResponse(BaseModel):
    count: int = Field(..., description="Number of records upserted")
    items: List[SeccionResponse]
