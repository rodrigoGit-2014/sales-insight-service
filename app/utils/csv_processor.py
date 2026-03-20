"""CSV processing utilities for streaming large files"""

import csv
from typing import Iterator, List, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CSVStreamProcessor:
    """
    Streaming CSV processor for handling large files without loading all into memory.

    This class reads CSV files in chunks, allowing for efficient processing
    of files that are too large to fit in memory.
    """

    REQUIRED_COLUMNS = {
        'id_pedido', 'id_cliente', 'fecha', 'hora',
        'id_departamento', 'id_seccion', 'id_producto',
        'nombre_producto', 'precio_unitario', 'cantidad', 'precio_total'
    }

    def __init__(self, file_path: str):
        """
        Initialize CSV processor.

        Args:
            file_path: Path to the CSV file to process
        """
        self.file_path = Path(file_path)
        self._total_rows: Optional[int] = None

        if not self.file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")

    @property
    def total_rows(self) -> Optional[int]:
        """
        Get total number of rows in the CSV file (excluding header).

        Returns:
            Number of rows or None if not yet calculated

        Note: This requires reading the entire file once, so use sparingly.
        """
        if self._total_rows is None:
            self._total_rows = self._count_rows()
        return self._total_rows

    def _count_rows(self) -> int:
        """Count total rows in CSV file"""
        count = 0
        with open(self.file_path, 'r', encoding='utf-8') as f:
            # Skip header
            next(f, None)
            for _ in f:
                count += 1
        return count

    def validate_structure(self) -> bool:
        """
        Validate CSV file has required columns.

        Returns:
            True if valid, False otherwise

        Raises:
            ValueError: If required columns are missing
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = set(reader.fieldnames or [])

            missing_columns = self.REQUIRED_COLUMNS - fieldnames
            if missing_columns:
                raise ValueError(
                    f"CSV file is missing required columns: {', '.join(missing_columns)}"
                )

            return True

    def process_in_batches(
        self,
        batch_size: int = 5000,
        skip_errors: bool = False
    ) -> Iterator[List[Dict]]:
        """
        Process CSV file in batches.

        Args:
            batch_size: Number of rows per batch (default: 5000)
            skip_errors: If True, skip invalid rows instead of failing

        Yields:
            List of dictionaries representing CSV rows

        Raises:
            ValueError: If CSV structure is invalid
        """
        # Validate structure first
        self.validate_structure()

        with open(self.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            batch = []
            row_num = 0

            for row in reader:
                row_num += 1

                try:
                    # Basic validation - check for empty required fields
                    if not all(row.get(col) for col in self.REQUIRED_COLUMNS):
                        raise ValueError(f"Row {row_num}: Missing required field(s)")

                    batch.append(row)

                    if len(batch) >= batch_size:
                        logger.info(f"Processing batch ending at row {row_num}")
                        yield batch
                        batch = []

                except ValueError as e:
                    if skip_errors:
                        logger.warning(f"Skipping invalid row {row_num}: {e}")
                        continue
                    else:
                        raise

            # Yield final batch if any rows remain
            if batch:
                logger.info(f"Processing final batch with {len(batch)} rows")
                yield batch

    def get_sample_rows(self, n: int = 5) -> List[Dict]:
        """
        Get first N rows as sample.

        Args:
            n: Number of rows to return

        Returns:
            List of dictionaries representing the first N rows
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return [row for _, row in zip(range(n), reader)]
