#!/usr/bin/env python3
"""
Script to create materialized views in the database.
Run this after deploying to Railway or when setting up a new database.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

def create_materialized_views():
    """Create all materialized views in the database."""

    print("Creating materialized views...")
    print(f"Database URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'configured'}")

    # Read the SQL file
    sql_file = Path(__file__).parent.parent / "docker" / "postgres" / "create_materialized_views.sql"

    if not sql_file.exists():
        print(f"ERROR: SQL file not found at {sql_file}")
        sys.exit(1)

    with open(sql_file, 'r') as f:
        sql_content = f.read()

    # Create database engine
    try:
        engine = create_engine(settings.DATABASE_URL)
        print("✓ Connected to database")
    except Exception as e:
        print(f"ERROR: Failed to connect to database: {e}")
        sys.exit(1)

    # Execute the SQL
    try:
        with engine.connect() as conn:
            # Execute the entire SQL file
            conn.execute(text(sql_content))
            conn.commit()
            print("✓ Materialized views created successfully!")

            # Verify views were created
            result = conn.execute(text("""
                SELECT schemaname, matviewname
                FROM pg_matviews
                WHERE schemaname = 'public'
                ORDER BY matviewname;
            """))

            views = result.fetchall()
            if views:
                print(f"\n✓ Created {len(views)} materialized views:")
                for schema, view_name in views:
                    print(f"  - {view_name}")
            else:
                print("⚠ Warning: No materialized views found after creation")

    except Exception as e:
        print(f"ERROR: Failed to create materialized views: {e}")
        sys.exit(1)

    print("\n✓ Done! Materialized views are ready.")
    print("\nNote: After uploading data via /upload-transactions,")
    print("the views will be automatically refreshed.")

if __name__ == "__main__":
    create_materialized_views()
