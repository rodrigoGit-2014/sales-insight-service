"""Configuration endpoints for Departamentos and Secciones CSV upload"""

import csv
import io
import unicodedata

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.api.deps import get_db
from app.models.departamento import Departamento
from app.models.seccion import Seccion
from app.schemas.config import (
    DepartamentoResponse,
    SeccionResponse,
    BulkDepartamentoResponse,
    BulkSeccionResponse,
)

router = APIRouter(prefix="/config", tags=["Configuration"])

# ---------------------------------------------------------------------------
# Icon mapping: keyword (lowercase, no accents) → lucide icon name
# ---------------------------------------------------------------------------
ICON_MAP = {
    "fruta": "apple",
    "verdura": "carrot",
    "bebida": "glass-water",
    "lacteo": "milk",
    "untable": "sandwich",
    "hierba": "leaf",
    "organico": "sprout",
    "crema": "droplet",
    "panaderia": "croissant",
    "carne": "beef",
    "pescado": "fish",
    "limpieza": "sparkles",
    "snack": "cookie",
    "cereal": "wheat",
    "congelado": "snowflake",
    "condimento": "flame",
    "huevo": "egg",
    "aceite": "droplets",
    "agua": "glass-water",
    "jugo": "cup-soda",
    "cafe": "coffee",
    "te": "coffee",
    "pan": "croissant",
    "queso": "milk",
    "yogur": "milk",
    "mantequilla": "sandwich",
    "mermelada": "cherry",
    "miel": "cherry",
    "arroz": "wheat",
    "pasta": "wheat",
    "harina": "wheat",
    "azucar": "candy",
    "sal": "flame",
    "salsa": "flame",
    "conserva": "package",
    "enlatado": "package",
    "galleta": "cookie",
    "chocolate": "candy",
    "dulce": "candy",
    "vino": "wine",
    "cerveza": "beer",
    "licor": "wine",
}

DEFAULT_ICON = "package"


def _strip_accents(text: str) -> str:
    """Remove accent marks from text for matching."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.category(c).startswith("M"))


def assign_icon(nombre: str) -> str:
    """Select the best icon for a given category name."""
    normalized = _strip_accents(nombre.lower().strip())
    # Try exact match first
    if normalized in ICON_MAP:
        return ICON_MAP[normalized]
    # Try substring match
    for keyword, icon in ICON_MAP.items():
        if keyword in normalized or normalized in keyword:
            return icon
    return DEFAULT_ICON


def _parse_csv(content: bytes, required_columns: list[str]) -> list[dict]:
    """Parse CSV bytes and validate required columns."""
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file is empty or has no headers",
        )

    # Normalize fieldnames (strip whitespace)
    reader.fieldnames = [f.strip() for f in reader.fieldnames]

    missing = set(required_columns) - set(reader.fieldnames)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required columns: {', '.join(sorted(missing))}",
        )

    rows = []
    for i, row in enumerate(reader, start=2):
        stripped = {k.strip(): v.strip() for k, v in row.items() if k}
        rows.append(stripped)

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file contains no data rows",
        )

    return rows


# ---------------------------------------------------------------------------
# Departamentos
# ---------------------------------------------------------------------------

@router.get(
    "/departamentos",
    response_model=list[DepartamentoResponse],
    summary="List all departamentos",
)
def list_departamentos(db: Session = Depends(get_db)):
    return db.query(Departamento).order_by(Departamento.nombre).all()


@router.post(
    "/departamentos/upload",
    response_model=BulkDepartamentoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload departamentos CSV",
)
async def upload_departamentos(
    file: UploadFile = File(..., description="CSV with id_departamento,nombre"),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are accepted",
        )

    content = await file.read()
    rows = _parse_csv(content, ["id_departamento", "nombre"])

    items = []
    for row in rows:
        try:
            id_dep = int(row["id_departamento"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid id_departamento: {row['id_departamento']}",
            )
        nombre = row["nombre"]
        icono = assign_icon(nombre)
        items.append(
            {"id_departamento": id_dep, "nombre": nombre, "icono_name": icono}
        )

    # Upsert using PostgreSQL ON CONFLICT
    stmt = pg_insert(Departamento).values(items)
    stmt = stmt.on_conflict_do_update(
        index_elements=["id_departamento"],
        set_={"nombre": stmt.excluded.nombre, "icono_name": stmt.excluded.icono_name},
    )
    db.execute(stmt)
    db.commit()

    # Return the upserted records
    ids = [item["id_departamento"] for item in items]
    saved = (
        db.query(Departamento)
        .filter(Departamento.id_departamento.in_(ids))
        .order_by(Departamento.nombre)
        .all()
    )

    return BulkDepartamentoResponse(
        count=len(saved),
        items=[DepartamentoResponse.model_validate(s) for s in saved],
    )


# ---------------------------------------------------------------------------
# Secciones
# ---------------------------------------------------------------------------

@router.get(
    "/secciones",
    response_model=list[SeccionResponse],
    summary="List all secciones",
)
def list_secciones(db: Session = Depends(get_db)):
    return db.query(Seccion).order_by(Seccion.nombre).all()


@router.post(
    "/secciones/upload",
    response_model=BulkSeccionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload secciones CSV",
)
async def upload_secciones(
    file: UploadFile = File(..., description="CSV with id_seccion,nombre"),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are accepted",
        )

    content = await file.read()
    rows = _parse_csv(content, ["id_seccion", "nombre"])

    items = []
    for row in rows:
        try:
            id_sec = int(row["id_seccion"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid id_seccion: {row['id_seccion']}",
            )
        nombre = row["nombre"]
        icono = assign_icon(nombre)
        items.append(
            {"id_seccion": id_sec, "nombre": nombre, "icono_name": icono}
        )

    stmt = pg_insert(Seccion).values(items)
    stmt = stmt.on_conflict_do_update(
        index_elements=["id_seccion"],
        set_={"nombre": stmt.excluded.nombre, "icono_name": stmt.excluded.icono_name},
    )
    db.execute(stmt)
    db.commit()

    ids = [item["id_seccion"] for item in items]
    saved = (
        db.query(Seccion)
        .filter(Seccion.id_seccion.in_(ids))
        .order_by(Seccion.nombre)
        .all()
    )

    return BulkSeccionResponse(
        count=len(saved),
        items=[SeccionResponse.model_validate(s) for s in saved],
    )
