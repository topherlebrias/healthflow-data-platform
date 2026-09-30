import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path


PROCESSED_FOLDER = Path("data/processed")
TRANSFORMED_FOLDER = Path("data/transformed")


def read_csv(file_path):
    with open(file_path, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def read_all_csvs(file_paths):
    rows = []

    for file_path in file_paths:
        rows.extend(read_csv(file_path))

    return rows


def write_csv(file_path, rows, columns):
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=columns,
        )

        writer.writeheader()
        writer.writerows(rows)


def get_all_files(table_name):
    table_folder = PROCESSED_FOLDER / table_name

    files = sorted(table_folder.glob("*.csv"))

    if not files:
        raise FileNotFoundError(
            f"No processed CSV found for {table_name}"
        )

    return files


def get_latest_file(table_name):
    files = get_all_files(table_name)

    return files[-1]


def create_dimensions():
    # ---------------------------------------------------------
    # PATIENTS
    # ---------------------------------------------------------
    #
    # Patients are currently being processed incrementally.
    # Therefore, we read all processed patient batches.
    #
    patients = read_all_csvs(
        get_all_files("patients")
    )

    patient_rows = []

    for patient in patients:
        patient_rows.append({
            "patient_id": patient["patient_id"],
            "first_name": patient["first_name"],
            "last_name": patient["last_name"],
            "sex": patient["sex"],
            "date_of_birth": patient["date_of_birth"],
        })

    write_csv(
        TRANSFORMED_FOLDER / "dim_patient.csv",
        patient_rows,
        [
            "patient_id",
            "first_name",
            "last_name",
            "sex",
            "date_of_birth",
        ],
    )

    # ---------------------------------------------------------
    # SERVICES
    # ---------------------------------------------------------
    #
    # Services are a snapshot table.
    #
    # We only want the latest complete snapshot.
    #
    latest_services_file = get_latest_file("services")

    services = read_csv(latest_services_file)

    service_rows = []

    for service in services:
        service_rows.append({
            "service_id": service["service_id"],
            "service_name": service["service_name"],
            "category": service["category"],
            "price": service["price"],
        })

    write_csv(
        TRANSFORMED_FOLDER / "dim_service.csv",
        service_rows,
        [
            "service_id",
            "service_name",
            "category",
            "price",
        ],
    )

    # ---------------------------------------------------------
    # BRANCHES
    # ---------------------------------------------------------
    #
    # Branches are also a snapshot table.
    #
    # We only want the latest complete snapshot.
    #
    latest_branches_file = get_latest_file("branches")

    branches = read_csv(latest_branches_file)

    branch_rows = []

    for branch in branches:
        branch_rows.append({
            "branch_id": branch["branch_id"],
            "branch_name": branch["branch_name"],
            "city": branch["city"],
        })

    write_csv(
        TRANSFORMED_FOLDER / "dim_branch.csv",
        branch_rows,
        [
            "branch_id",
            "branch_name",
            "city",
        ],
    )

    print(
        f"Dimensions created: "
        f"{len(patient_rows)} patients, "
        f"{len(service_rows)} services, "
        f"{len(branch_rows)} branches"
    )


def create_fact_lab_service():
    # ---------------------------------------------------------
    # PATIENT SERVICES
    # ---------------------------------------------------------
    #
    # Patient services are incremental.
    # Therefore, read all processed batches.
    #
    patient_services = read_all_csvs(
        get_all_files("patient_services")
    )

    # ---------------------------------------------------------
    # LAB RESULTS
    # ---------------------------------------------------------

    lab_results = read_all_csvs(
        get_all_files("lab_results")
    )

    # ---------------------------------------------------------
    # PAYMENTS
    # ---------------------------------------------------------

    payments = read_all_csvs(
        get_all_files("payments")
    )

    # ---------------------------------------------------------
    # FIND LATEST VALIDATED RESULT
    # ---------------------------------------------------------

    latest_results = {}

    for result in lab_results:

        patient_service_id = result[
            "patient_service_id"
        ]

        if not result["validated_at"]:
            continue

        validated_at = datetime.fromisoformat(
            result["validated_at"]
        )

        if (
            patient_service_id not in latest_results
            or validated_at
            > latest_results[
                patient_service_id
            ]["validated_at"]
        ):
            latest_results[patient_service_id] = {
                "validated_at": validated_at,
                "result": result,
            }

    # ---------------------------------------------------------
    # CALCULATE REVENUE
    # ---------------------------------------------------------

    revenue_by_service = {}

    for payment in payments:

        patient_service_id = payment[
            "patient_service_id"
        ]

        amount = Decimal(
            payment["amount"]
        )

        revenue_by_service[
            patient_service_id
        ] = (
            revenue_by_service.get(
                patient_service_id,
                Decimal("0.00"),
            )
            + amount
        )

    # ---------------------------------------------------------
    # CREATE FACT TABLE
    # ---------------------------------------------------------

    fact_rows = []

    for service in patient_services:

        patient_service_id = service[
            "patient_service_id"
        ]

        requested_at = datetime.fromisoformat(
            service["requested_at"]
        )

        completed_at = None

        turnaround_minutes = ""

        if patient_service_id in latest_results:

            completed_at = latest_results[
                patient_service_id
            ]["validated_at"]

            turnaround = (
                completed_at - requested_at
            )

            turnaround_minutes = int(
                turnaround.total_seconds()
                / 60
            )

        revenue = revenue_by_service.get(
            patient_service_id,
            Decimal("0.00"),
        )

        fact_rows.append({
            "patient_service_id":
                patient_service_id,

            "patient_id":
                service["patient_id"],

            "service_id":
                service["service_id"],

            "branch_id":
                service["branch_id"],

            "requested_at":
                service["requested_at"],

            "completed_at":
                (
                    completed_at.isoformat(
                        sep=" "
                    )
                    if completed_at
                    else ""
                ),

            "status":
                service["status"],

            "turnaround_minutes":
                turnaround_minutes,

            "revenue":
                f"{revenue:.2f}",
        })

    write_csv(
        TRANSFORMED_FOLDER
        / "fact_lab_service.csv",

        fact_rows,

        [
            "patient_service_id",
            "patient_id",
            "service_id",
            "branch_id",
            "requested_at",
            "completed_at",
            "status",
            "turnaround_minutes",
            "revenue",
        ],
    )

    print(
        f"Fact table created: "
        f"{len(fact_rows)} laboratory services"
    )

    return len(fact_rows)


def main():

    TRANSFORMED_FOLDER.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "Starting transformation..."
    )

    create_dimensions()

    records_transformed = (
        create_fact_lab_service()
    )

    print(
        "Transformation completed successfully."
    )

    return records_transformed


if __name__ == "__main__":
    main()