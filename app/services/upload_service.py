"""Service for handling file uploads and job creation"""

import os
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.job import Job, JobStatus
from app.repositories.job_repository import JobRepository
from app.core.config import settings
from celery_app.tasks.process_transactions import process_transactions_task


class UploadService:
    """Service for handling CSV file uploads and background processing"""

    def __init__(self, db: Session):
        self.db = db
        self.job_repository = JobRepository(db)
        self.upload_dir = Path(settings.UPLOAD_DIR)

        # Ensure upload directory exists
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def create_upload_job(self, filename: str, file_content: bytes, company_id: UUID) -> Job:
        """
        Create a new upload job and save the file.

        Args:
            filename: Original filename
            file_content: File content as bytes

        Returns:
            Created Job instance

        Raises:
            ValueError: If file is too large or invalid
        """
        # Validate file size
        if len(file_content) > settings.MAX_UPLOAD_SIZE:
            raise ValueError(
                f"File size ({len(file_content)} bytes) exceeds maximum allowed "
                f"({settings.MAX_UPLOAD_SIZE} bytes)"
            )

        # Validate file extension
        if not filename.lower().endswith('.csv'):
            raise ValueError("Only CSV files are accepted")

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = self.upload_dir / unique_filename

        # Save file to disk
        try:
            with open(file_path, 'wb') as f:
                f.write(file_content)
        except Exception as e:
            raise ValueError(f"Failed to save file: {e}")

        # Create job record
        job = Job(
            filename=filename,
            file_path=str(file_path),
            status=JobStatus.PENDING,
            company_id=company_id,
            created_at=datetime.utcnow()
        )

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        # Trigger background processing task
        try:
            process_transactions_task.delay(str(job.id), str(file_path), str(company_id))
        except Exception as e:
            # If task creation fails, mark job as failed
            job.status = JobStatus.FAILED
            job.error_message = f"Failed to queue processing task: {e}"
            self.db.commit()
            raise

        return job

    def get_job_status(self, job_id: str) -> Optional[Job]:
        """
        Get job status by ID.

        Args:
            job_id: Job UUID

        Returns:
            Job instance or None if not found
        """
        return self.job_repository.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a pending job.

        Args:
            job_id: Job UUID

        Returns:
            True if cancelled, False if job not found or already processing

        Note: Jobs that are already processing cannot be cancelled
        """
        job = self.job_repository.get(job_id)

        if not job:
            return False

        if job.status != JobStatus.PENDING:
            return False

        # Mark as failed with cancellation message
        job.status = JobStatus.FAILED
        job.error_message = "Job cancelled by user"
        job.completed_at = datetime.utcnow()

        # Clean up file if it exists
        if os.path.exists(job.file_path):
            try:
                os.remove(job.file_path)
            except Exception:
                pass

        self.db.commit()
        return True
