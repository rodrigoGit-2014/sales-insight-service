#!/usr/bin/env python3
"""Generate sample CSV data for testing"""

import csv
import random
from datetime import datetime, timedelta, date, time
from decimal import Decimal
import argparse
from pathlib import Path


# Sample data
DEPARTMENTS = ['DEPT001', 'DEPT002', 'DEPT003', 'DEPT004', 'DEPT005']
SECTIONS = ['SEC001', 'SEC002', 'SEC003', 'SEC004', 'SEC005', 'SEC006']
PRODUCTS = [
    ('PROD001', 'Laptop Dell XPS 15'),
    ('PROD002', 'iPhone 14 Pro'),
    ('PROD003', 'Samsung TV 55"'),
    ('PROD004', 'Sony Headphones WH-1000XM5'),
    ('PROD005', 'MacBook Pro 16"'),
    ('PROD006', 'iPad Air'),
    ('PROD007', 'Gaming Mouse Logitech'),
    ('PROD008', 'Mechanical Keyboard'),
    ('PROD009', 'Monitor LG 27"'),
    ('PROD010', 'Webcam Logitech C920'),
]


def generate_transaction(order_id: int, customer_id: int, start_date: date) -> dict:
    """Generate a single transaction record"""

    # Random date within last year
    days_back = random.randint(0, 365)
    transaction_date = start_date - timedelta(days=days_back)

    # Random hour (0-23)
    hour = random.randint(0, 23)

    # Random product
    product_id, product_name = random.choice(PRODUCTS)

    # Random pricing
    unit_price = Decimal(str(round(random.uniform(10.0, 2000.0), 2)))
    quantity = random.randint(1, 10)
    total_price = unit_price * quantity

    return {
        'id_pedido': f'ORD{order_id:08d}',
        'id_cliente': f'CUST{customer_id:06d}',
        'fecha': transaction_date.isoformat(),
        'hora': hour,
        'id_departamento': random.choice(DEPARTMENTS),
        'id_seccion': random.choice(SECTIONS),
        'id_producto': product_id,
        'nombre_producto': product_name,
        'precio_unitario': float(unit_price),
        'cantidad': quantity,
        'precio_total': float(total_price)
    }


def generate_csv(
    output_file: str,
    num_rows: int = 10000,
    num_customers: int = 1000
):
    """
    Generate CSV file with sample transaction data.

    Args:
        output_file: Output CSV file path
        num_rows: Number of rows to generate
        num_customers: Number of unique customers
    """
    print(f"Generating {num_rows:,} rows of sample data...")
    print(f"Number of customers: {num_customers:,}")

    start_date = date.today()

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'id_pedido', 'id_cliente', 'fecha', 'hora',
            'id_departamento', 'id_seccion', 'id_producto',
            'nombre_producto', 'precio_unitario', 'cantidad', 'precio_total'
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, num_rows + 1):
            # Random customer (with some repeat customers)
            customer_id = random.randint(1, num_customers)

            row = generate_transaction(i, customer_id, start_date)
            writer.writerow(row)

            if i % 10000 == 0:
                print(f"Generated {i:,} rows...")

    file_size = Path(output_file).stat().st_size
    file_size_mb = file_size / (1024 * 1024)

    print(f"\nCompleted!")
    print(f"File: {output_file}")
    print(f"Rows: {num_rows:,}")
    print(f"Size: {file_size_mb:.2f} MB")


def main():
    parser = argparse.ArgumentParser(
        description='Generate sample CSV data for sales analytics'
    )
    parser.add_argument(
        '--rows',
        type=int,
        default=10000,
        help='Number of rows to generate (default: 10,000)'
    )
    parser.add_argument(
        '--customers',
        type=int,
        default=1000,
        help='Number of unique customers (default: 1,000)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='sample_transactions.csv',
        help='Output CSV file name (default: sample_transactions.csv)'
    )

    args = parser.parse_args()

    generate_csv(
        output_file=args.output,
        num_rows=args.rows,
        num_customers=args.customers
    )


if __name__ == '__main__':
    main()
