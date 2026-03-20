"""Celery task for processing CSV transaction files"""

import os
import logging
from datetime import datetime, date, time
from decimal import Decimal
from typing import Dict, List
from celery import Task
from sqlalchemy.exc import SQLAlchemyError

from celery_app.celery import celery_app
from app.db.session import SessionLocal
from app.models.ticket import Ticket
from app.models.job import Job, JobStatus
from app.utils.csv_processor import CSVStreamProcessor

# Configure logging
logger = logging.getLogger(__name__)


class TransactionProcessingTask(Task):
    """
    Base task class with custom error handling and retry logic.

    This task will automatically retry on failures with exponential backoff.
    """
    autoretry_for = (SQLAlchemyError,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True
    retry_backoff_max = 600  # Max 10 minutes between retries
    retry_jitter = True


@celery_app.task(bind=True, base=TransactionProcessingTask, name='process_transactions')
def process_transactions_task(self, job_id: str, file_path: str) -> Dict:
    """
    Process CSV transactions file in streaming mode with batch inserts.

    This task:
    1. Updates job status to 'processing'
    2. Reads CSV file in streaming mode (doesn't load all into memory)
    3. Processes data in batches of 5000 records
    4. Performs bulk inserts to PostgreSQL
    5. Updates progress after each batch
    6. Handles errors gracefully (can continue with next batch)
    7. Cleans up temporary file after completion

    Args:
        job_id: UUID of the job to track progress
        file_path: Path to the uploaded CSV file

    Returns:
        Dictionary with processing results

    Raises:
        Exception: If critical error occurs during processing
    """
    BATCH_SIZE = 5000
    db = SessionLocal()

    try:
        logger.info(f"Starting processing for job {job_id}, file: {file_path}")

        # Get job from database
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Update job status to processing
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow()
        db.commit()
        logger.info(f"Job {job_id} marked as PROCESSING")

        # Initialize CSV processor
        processor = CSVStreamProcessor(file_path)

        # Validate CSV structure
        try:
            processor.validate_structure()
        except ValueError as e:
            logger.error(f"CSV validation failed: {e}")
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
            return {'status': 'failed', 'error': str(e)}

        # Count total rows (for progress tracking)
        total_rows = processor.total_rows
        job.total_rows = total_rows
        db.commit()
        logger.info(f"Total rows to process: {total_rows}")

        total_processed = 0
        total_errors = 0
        error_messages = []

        # Process file in batches
        for batch_idx, batch in enumerate(processor.process_in_batches(BATCH_SIZE, skip_errors=True)):
            try:
                # Convert CSV rows to Ticket objects
                tickets = []
                for row in batch:
                    try:
                        ticket = Ticket(
                            id_pedido=str(row['id_pedido']),
                            id_cliente=str(row['id_cliente']),
                            fecha=_parse_date(row['fecha']),
                            hora=_parse_time(row['hora']),
                            id_departamento=str(row['id_departamento']),
                            id_seccion=str(row['id_seccion']),
                            id_producto=str(row['id_producto']),
                            nombre_producto=str(row['nombre_producto']),
                            precio_unitario=Decimal(str(row['precio_unitario'])),
                            cantidad=int(row['cantidad']),
                            precio_total=Decimal(str(row['precio_total']))
                        )
                        tickets.append(ticket)
                    except (ValueError, TypeError, KeyError) as e:
                        total_errors += 1
                        error_msg = f"Row validation error: {e}"
                        logger.warning(error_msg)
                        if len(error_messages) < 10:  # Store only first 10 errors
                            error_messages.append(error_msg)

                # Bulk insert tickets
                if tickets:
                    db.bulk_save_objects(tickets)
                    db.commit()
                    total_processed += len(tickets)
                    logger.info(f"Batch {batch_idx + 1} inserted: {len(tickets)} records")

                # Update job progress
                job.processed_rows = total_processed
                db.commit()

                # Update Celery task state for progress tracking
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'processed': total_processed,
                        'total': total_rows,
                        'percentage': round((total_processed / total_rows) * 100, 2) if total_rows else 0
                    }
                )

            except SQLAlchemyError as e:
                db.rollback()
                total_errors += len(batch)
                error_msg = f"Database error in batch {batch_idx + 1}: {e}"
                logger.error(error_msg)
                error_messages.append(error_msg)
                # Continue with next batch instead of failing completely

        # Mark job as completed
        job.status = JobStatus.COMPLETED
        job.processed_rows = total_processed
        job.completed_at = datetime.utcnow()

        # Add error summary to metadata if there were errors
        if error_messages:
            job.error_message = f"Completed with {total_errors} errors. First errors: {'; '.join(error_messages[:5])}"

        db.commit()

        logger.info(
            f"Job {job_id} completed successfully. "
            f"Processed: {total_processed}, Errors: {total_errors}"
        )

        return {
            'status': 'completed',
            'processed': total_processed,
            'errors': total_errors,
            'job_id': str(job_id)
        }

    except Exception as e:
        logger.error(f"Critical error processing job {job_id}: {e}", exc_info=True)

        # Update job as failed
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                db.commit()
        except Exception as update_error:
            logger.error(f"Failed to update job status: {update_error}")

        raise

    finally:
        db.close()

        # Clean up temporary file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Temporary file deleted: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to delete temporary file {file_path}: {e}")


def _parse_date(date_str: str) -> date:
    """Parse date string to date object"""
    if isinstance(date_str, date):
        return date_str
    # Try common date formats
    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_str}")


def _parse_time(time_str: str) -> time:
    """Parse time string to time object"""
    if isinstance(time_str, time):
        return time_str
    # Handle integer hour (0-23)
    try:
        hour = int(time_str)
        if 0 <= hour <= 23:
            return time(hour=hour)
    except (ValueError, TypeError):
        pass

    # Try common time formats
    for fmt in ['%H:%M:%S', '%H:%M', '%H']:
        try:
            return datetime.strptime(str(time_str), fmt).time()
        except ValueError:
            continue

    raise ValueError(f"Invalid time format: {time_str}")
