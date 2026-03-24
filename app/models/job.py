"""Job model for tracking background CSV processing tasks"""

from sqlalchemy import Column, String, Integer, Text, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum
from datetime import datetime
from typing import Optional

from app.db.base import Base


class JobStatus(str, enum.Enum):
    """Enumeration of possible job statuses"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(Base):
    """
    Job model for tracking background CSV processing tasks.

    Stores metadata about file uploads and their processing status,
    allowing clients to poll for completion and track progress.
    """

    __tablename__ = "jobs"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique job identifier"
    )

    # Tenant
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True, comment="Company/tenant ID")

    # Job Status
    status = Column(
        SQLAlchemyEnum(JobStatus, name="job_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=JobStatus.PENDING,
        index=True,
        comment="Current job status"
    )

    # File Information
    filename = Column(String(255), nullable=False, comment="Original filename")
    file_path = Column(String(500), nullable=False, comment="Path to uploaded file")

    # Processing Progress
    total_rows = Column(Integer, nullable=True, comment="Total rows in CSV file")
    processed_rows = Column(Integer, default=0, comment="Number of rows processed")

    # Error Information
    error_message = Column(Text, nullable=True, comment="Error message if failed")

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Job creation timestamp"
    )
    started_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Processing start timestamp"
    )
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Processing completion timestamp"
    )

    # Additional Metadata (JSON) - using 'job_metadata' to avoid SQLAlchemy reserved name
    job_metadata = Column(
        'metadata',  # Database column name
        JSONB,
        default=dict,
        nullable=False,
        comment="Additional job metadata"
    )

    def __repr__(self) -> str:
        return (
            f"<Job(id={self.id}, status={self.status.value}, "
            f"filename={self.filename}, progress={self.progress_percentage}%)>"
        )

    @property
    def progress_percentage(self) -> Optional[float]:
        """
        Calculate processing progress percentage.

        Returns:
            Progress percentage (0-100) or None if total_rows not set
        """
        if self.total_rows and self.total_rows > 0:
            return round((self.processed_rows / self.total_rows) * 100, 2)
        return None

    @property
    def duration_seconds(self) -> Optional[float]:
        """
        Calculate job duration in seconds.

        Returns:
            Duration in seconds or None if not completed
        """
        if self.started_at:
            end_time = self.completed_at or datetime.now(self.started_at.tzinfo)
            return (end_time - self.started_at).total_seconds()
        return None

    def update_status(
        self,
        status: JobStatus,
        error_message: Optional[str] = None,
        processed_rows: Optional[int] = None,
        total_rows: Optional[int] = None
    ) -> None:
        """
        Update job status and related fields.

        Args:
            status: New job status
            error_message: Error message if status is FAILED
            processed_rows: Number of rows processed
            total_rows: Total number of rows
        """
        self.status = status

        if status == JobStatus.PROCESSING and not self.started_at:
            self.started_at = func.now()

        if status in (JobStatus.COMPLETED, JobStatus.FAILED):
            self.completed_at = func.now()

        if error_message:
            self.error_message = error_message

        if processed_rows is not None:
            self.processed_rows = processed_rows

        if total_rows is not None:
            self.total_rows = total_rows
