"""Repository for Job model"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.job import Job, JobStatus
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    """Repository for Job model with job-specific query methods"""

    def __init__(self, db: Session):
        super().__init__(Job, db)

    def get_by_status(self, status: JobStatus, limit: int = 100) -> List[Job]:
        """
        Get jobs by status.

        Args:
            status: Job status to filter by
            limit: Maximum number of jobs to return

        Returns:
            List of Job instances
        """
        return (
            self.db.query(Job)
            .filter(Job.status == status)
            .order_by(desc(Job.created_at))
            .limit(limit)
            .all()
        )

    def get_recent_jobs(self, limit: int = 50) -> List[Job]:
        """
        Get recently created jobs.

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of Job instances
        """
        return (
            self.db.query(Job)
            .order_by(desc(Job.created_at))
            .limit(limit)
            .all()
        )

    def get_pending_jobs(self) -> List[Job]:
        """
        Get all pending jobs.

        Returns:
            List of pending Job instances
        """
        return self.get_by_status(JobStatus.PENDING)

    def get_processing_jobs(self) -> List[Job]:
        """
        Get all currently processing jobs.

        Returns:
            List of processing Job instances
        """
        return self.get_by_status(JobStatus.PROCESSING)

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        error_message: Optional[str] = None,
        processed_rows: Optional[int] = None,
        total_rows: Optional[int] = None
    ) -> Optional[Job]:
        """
        Update job status and related fields.

        Args:
            job_id: Job ID
            status: New status
            error_message: Error message if failed
            processed_rows: Number of rows processed
            total_rows: Total number of rows

        Returns:
            Updated Job instance or None if not found
        """
        job = self.get(job_id)
        if not job:
            return None

        # Update status
        job.status = status

        # Update timestamps based on status
        if status == JobStatus.PROCESSING and not job.started_at:
            job.started_at = datetime.utcnow()

        if status in (JobStatus.COMPLETED, JobStatus.FAILED):
            job.completed_at = datetime.utcnow()

        # Update error message
        if error_message:
            job.error_message = error_message

        # Update progress
        if processed_rows is not None:
            job.processed_rows = processed_rows

        if total_rows is not None:
            job.total_rows = total_rows

        self.db.commit()
        self.db.refresh(job)

        return job

    def update_progress(self, job_id: str, processed_rows: int) -> Optional[Job]:
        """
        Update job progress.

        Args:
            job_id: Job ID
            processed_rows: Number of rows processed

        Returns:
            Updated Job instance or None if not found
        """
        job = self.get(job_id)
        if not job:
            return None

        job.processed_rows = processed_rows
        self.db.commit()
        self.db.refresh(job)

        return job

    def cleanup_old_jobs(self, days: int = 7) -> int:
        """
        Delete completed/failed jobs older than specified days.

        Args:
            days: Number of days to keep jobs

        Returns:
            Number of jobs deleted
        """
        cutoff_date = datetime.utcnow() - datetime.timedelta(days=days)

        deleted = (
            self.db.query(Job)
            .filter(
                Job.status.in_([JobStatus.COMPLETED, JobStatus.FAILED]),
                Job.completed_at < cutoff_date
            )
            .delete()
        )

        self.db.commit()
        return deleted
