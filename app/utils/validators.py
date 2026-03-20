"""Custom validators for data validation"""

from datetime import date, datetime
from typing import Optional
from decimal import Decimal, InvalidOperation


def validate_date_range(
    fecha_inicio: Optional[date],
    fecha_fin: Optional[date]
) -> bool:
    """
    Validate that start date is before or equal to end date.

    Args:
        fecha_inicio: Start date
        fecha_fin: End date

    Returns:
        True if valid, False otherwise
    """
    if fecha_inicio and fecha_fin:
        return fecha_inicio <= fecha_fin
    return True


def validate_positive_decimal(value: str) -> Decimal:
    """
    Validate and convert string to positive Decimal.

    Args:
        value: String value to convert

    Returns:
        Decimal value

    Raises:
        ValueError: If value is not a valid positive decimal
    """
    try:
        dec_value = Decimal(value)
        if dec_value < 0:
            raise ValueError("Value must be positive")
        return dec_value
    except InvalidOperation:
        raise ValueError(f"Invalid decimal value: {value}")


def validate_positive_integer(value: str) -> int:
    """
    Validate and convert string to positive integer.

    Args:
        value: String value to convert

    Returns:
        Integer value

    Raises:
        ValueError: If value is not a valid positive integer
    """
    try:
        int_value = int(value)
        if int_value <= 0:
            raise ValueError("Value must be positive")
        return int_value
    except ValueError:
        raise ValueError(f"Invalid integer value: {value}")


def validate_csv_headers(headers: list, required_headers: set) -> bool:
    """
    Validate that CSV has all required headers.

    Args:
        headers: List of CSV headers
        required_headers: Set of required header names

    Returns:
        True if valid

    Raises:
        ValueError: If required headers are missing
    """
    header_set = set(headers)
    missing = required_headers - header_set

    if missing:
        raise ValueError(f"Missing required CSV columns: {', '.join(missing)}")

    return True
