import duckdb
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

TRANSFORMED_FOLDER = PROJECT_ROOT / "data" / "transformed"
WAREHOUSE_FOLDER = PROJECT_ROOT / "warehouse"
DATABASE_FILE = WAREHOUSE_FOLDER / "healthflow.duckdb"


def get_connection():
    WAREHOUSE_FOLDER.mkdir(
        parents=True,
        exist_ok=True,
    )

    return duckdb.connect(
        str(DATABASE_FILE)
    )


def load_dimension(
    connection,
    csv_file,
    table_name,
):
    csv_path = TRANSFORMED_FOLDER / csv_file

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Transformed file not found: {csv_path}"
        )

    print()
    print(f"Loading dimension: {table_name}")
    print(f"Source: {csv_path}")

    connection.execute(
        f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT *
        FROM read_csv_auto(?);
        """,
        [str(csv_path)],
    )

    count = connection.execute(
        f"""
        SELECT COUNT(*)
        FROM {table_name};
        """
    ).fetchone()[0]

    print(
        f"Loaded {count} records into {table_name}."
    )

    return count


def load_fact(
    connection,
    csv_file,
    table_name,
):
    csv_path = TRANSFORMED_FOLDER / csv_file

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Transformed file not found: {csv_path}"
        )

    print()
    print(f"Loading fact table: {table_name}")
    print(f"Source: {csv_path}")

    connection.execute(
        f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT *
        FROM read_csv_auto(?);
        """,
        [str(csv_path)],
    )

    count = connection.execute(
        f"""
        SELECT COUNT(*)
        FROM {table_name};
        """
    ).fetchone()[0]

    print(
        f"Loaded {count} records into {table_name}."
    )

    return count


def verify_warehouse(connection):
    print()
    print("WAREHOUSE VALIDATION")
    print("-" * 60)

    tables = [
        "dim_patient",
        "dim_service",
        "dim_branch",
        "fact_lab_service",
    ]

    for table_name in tables:
        result = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM {table_name};
            """
        ).fetchone()[0]

        print(
            f"{table_name}: {result} records"
        )


def main():
    print("=" * 60)
    print("HEALTHFLOW DATA WAREHOUSE LOAD")
    print("=" * 60)

    connection = get_connection()

    try:
        load_dimension(
            connection,
            "dim_patient.csv",
            "dim_patient",
        )

        load_dimension(
            connection,
            "dim_service.csv",
            "dim_service",
        )

        load_dimension(
            connection,
            "dim_branch.csv",
            "dim_branch",
        )

        load_fact(
            connection,
            "fact_lab_service.csv",
            "fact_lab_service",
        )
        
        print()
        print("CREATING ANALYTICAL VIEW")
        print("-" * 60)

        connection.execute(
            """
            CREATE OR REPLACE VIEW vw_lab_service_analysis AS
            SELECT
                f.patient_service_id,
                f.patient_id,
                p.first_name,
                p.last_name,
                p.sex,
                f.service_id,
                s.service_name,
                s.category,
                f.branch_id,
                b.branch_name,
                b.city,
                f.requested_at,
                f.completed_at,
                f.status,
                f.turnaround_minutes,
                f.revenue
            FROM fact_lab_service f
            LEFT JOIN dim_patient p
                ON f.patient_id = p.patient_id
            LEFT JOIN dim_service s
                ON f.service_id = s.service_id
            LEFT JOIN dim_branch b
                ON f.branch_id = b.branch_id;
            """
        )

        print(
            "Analytical view created: "
            "vw_lab_service_analysis"
        )

        verify_warehouse(connection)

        print()
        print("=" * 60)
        print("WAREHOUSE LOAD COMPLETED SUCCESSFULLY")
        print("=" * 60)

    finally:
        connection.close()


if __name__ == "__main__":
    main()