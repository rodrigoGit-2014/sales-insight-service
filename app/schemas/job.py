"""Pydantic schemas for Job model"""

from pydantic import BaseModel, Field, ConfigDict, UUID4
from datetime import datetime
from typing import Optional
from app.models.job import JobStatus


class JobCreate(BaseModel):
    """Schema for creating a new Job"""

    filename: str = Field(..., max_length=255, description="Original filename")
    file_path: str = Field(..., max_length=500, description="Path to uploaded file")


class JobResponse(BaseModel):
    """Schema for Job responses"""

    job_id: UUID4 = Field(..., description="Unique job identifier", alias="id")
    status: JobStatus = Field(..., description="Current job status")
    filename: str = Field(..., description="Original filename")
    total_rows: Optional[int] = Field(None, description="Total rows in CSV")
    processed_rows: int = Field(0, description="Rows processed so far")
    progress_percentage: Optional[float] = Field(None, description="Progress percentage (0-100)")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Job creation time")
    started_at: Optional[datetime] = Field(None, description="Processing start time")
    completed_at: Optional[datetime] = Field(None, description="Processing completion time")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )


class JobCreateResponse(BaseModel):
    """Schema for initial job creation response"""

    job_id: UUID4 = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Initial job status (pending)")
    message: str = Field(..., description="Success message")
    created_at: datetime = Field(..., description="Job creation time")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )
