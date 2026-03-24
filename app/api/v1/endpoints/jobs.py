"""Job status endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from pydantic import UUID4

from app.api.deps import get_db
from app.api.auth_deps import get_current_user, TokenData
from app.services.upload_service import UploadService
from app.schemas.job import JobResponse

router = APIRouter()


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    summary="Get job status",
    description="Retrieve the status and progress of a background processing job"
)
def get_job_status(
    job_id: UUID4 = Path(..., description="Job UUID"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get job processing status.

    Returns detailed information about the job including:
    - Current status (pending, processing, completed, failed)
    - Processing progress (rows processed / total rows)
    - Progress percentage
    - Error message (if failed)
    - Timestamps (created, started, completed)

    Use this endpoint to poll for job completion after uploading a file.
    Recommended polling interval: 2-5 seconds.
    """
    upload_service = UploadService(db)

    job = upload_service.get_job_status(str(job_id))

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    return JobResponse(
        id=job.id,
        status=job.status,
        filename=job.filename,
        total_rows=job.total_rows,
        processed_rows=job.processed_rows,
        progress_percentage=job.progress_percentage,
        error_message=job.error_message,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at
    )
