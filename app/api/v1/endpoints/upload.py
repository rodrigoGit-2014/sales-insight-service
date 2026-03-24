"""Upload endpoint for CSV file uploads"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.auth_deps import get_current_user, TokenData
from app.services.upload_service import UploadService
from app.schemas.job import JobCreateResponse
from app.models.job import JobStatus

router = APIRouter()


@router.post(
    "/upload-transactions",
    response_model=JobCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload transactions CSV file",
    description=(
        "Upload a CSV file containing sales transactions for processing. "
        "The file will be processed asynchronously in the background. "
        "Returns a job_id that can be used to track processing status."
    )
)
async def upload_transactions(
    file: UploadFile = File(..., description="CSV file with transactions"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Upload transactions CSV file for processing.

    The CSV file must have the following columns:
    - id_pedido: Order ID
    - id_cliente: Customer ID
    - fecha: Transaction date (YYYY-MM-DD)
    - hora: Transaction hour (0-23 or HH:MM:SS)
    - id_departamento: Department ID
    - id_seccion: Section ID
    - id_producto: Product ID
    - nombre_producto: Product name
    - precio_unitario: Unit price
    - cantidad: Quantity
    - precio_total: Total price

    The file will be processed asynchronously. Use the returned job_id
    to check processing status via GET /jobs/{job_id}.
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are accepted"
        )

    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read file: {str(e)}"
        )

    # Create upload job
    upload_service = UploadService(db)

    try:
        job = upload_service.create_upload_job(file.filename, file_content, current_user.company_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create upload job: {str(e)}"
        )

    return JobCreateResponse(
        job_id=job.id,
        status=job.status,
        message="File uploaded successfully. Processing has started.",
        created_at=job.created_at
    )
