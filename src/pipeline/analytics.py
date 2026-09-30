import duckdb
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_FILE = PROJECT_ROOT / "warehouse" / "healthflow.duckdb"


def main():
    connection = duckdb.connect(
        str(DATABASE_FILE)
    )

    try:
        print("=" * 60)
        print("HEALTHFLOW ANALYTICS")
        print("=" * 60)

        print()
        print("1. TOTAL LABORATORY SERVICES")
        print("-" * 60)

        result = connection.execute(
            """
            SELECT COUNT(*)
            FROM fact_lab_service;
            """
        ).fetchone()

        print(
            f"Total services: {result[0]}"
        )

        print()
        print("2. TOTAL REVENUE")
        print("-" * 60)

        result = connection.execute(
            """
            SELECT
                COALESCE(SUM(revenue), 0)
            FROM fact_lab_service;
            """
        ).fetchone()

        print(
            f"Total revenue: PHP {result[0]:,.2f}"
        )

        print()
        print("3. AVERAGE TURNAROUND TIME")
        print("-" * 60)

        result = connection.execute(
            """
            SELECT
                AVG(turnaround_minutes)
            FROM fact_lab_service
            WHERE turnaround_minutes IS NOT NULL;
            """
        ).fetchone()

        if result[0] is None:
            print("Average TAT: No data")
        else:
            print(
                f"Average TAT: {result[0]:.2f} minutes"
            )

        print()
        print("4. SERVICES BY BRANCH")
        print("-" * 60)

        rows = connection.execute(
            """
            SELECT
                b.branch_name,
                COUNT(*) AS total_services
            FROM fact_lab_service f
            JOIN dim_branch b
                ON f.branch_id = b.branch_id
            GROUP BY
                b.branch_name
            ORDER BY
                total_services DESC;
            """
        ).fetchall()

        for branch_name, total_services in rows:
            print(
                f"{branch_name}: "
                f"{total_services} services"
            )

        print()
        print("5. REVENUE BY SERVICE")
        print("-" * 60)

        rows = connection.execute(
            """
            SELECT
                s.service_name,
                COUNT(*) AS total_services,
                SUM(f.revenue) AS total_revenue
            FROM fact_lab_service f
            JOIN dim_service s
                ON f.service_id = s.service_id
            GROUP BY
                s.service_name
            ORDER BY
                total_revenue DESC;
            """
        ).fetchall()

        for service_name, total_services, total_revenue in rows:
            print(
                f"{service_name}: "
                f"{total_services} services, "
                f"PHP {total_revenue:,.2f}"
            )

    finally:
        connection.close()


if __name__ == "__main__":
    main()