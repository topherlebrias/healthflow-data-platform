import duckdb
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_FILE = PROJECT_ROOT / "warehouse" / "healthflow.duckdb"


def main():
    connection = duckdb.connect(str(DATABASE_FILE))

    try:
        print("=" * 60)
        print("HEALTHFLOW DATA WAREHOUSE")
        print("=" * 60)

        print()
        print("TABLES AND VIEWS")
        print("-" * 60)

        objects = connection.execute(
            """
            SELECT table_name, table_type
            FROM information_schema.tables
            WHERE table_schema = 'main'
            ORDER BY table_name;
            """
        ).fetchall()

        for name, object_type in objects:
            print(f"{name} ({object_type})")

        print()
        print("ANALYTICAL VIEW")
        print("-" * 60)

        rows = connection.execute(
            """
            SELECT *
            FROM vw_lab_service_analysis
            ORDER BY patient_service_id;
            """
        ).fetchall()

        columns = [
            column[0]
            for column in connection.description
        ]

        print(columns)

        for row in rows:
            print(row)

        print()
        print("=" * 60)
        print("WAREHOUSE VERIFICATION COMPLETED")
        print("=" * 60)

    finally:
        connection.close()


if __name__ == "__main__":
    main()