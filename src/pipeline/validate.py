import csv
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from pathlib import Path


# ---------------------------------------------------------
# FOLDERS
# ---------------------------------------------------------

RAW_FOLDER = Path("data/raw")
PROCESSED_FOLDER = Path("data/processed")
REJECTED_FOLDER = Path("data/rejected")


# ---------------------------------------------------------
# REQUIRED COLUMNS
# ---------------------------------------------------------

REQUIRED_COLUMNS = {
    "patients": [
        "patient_id",
        "first_name",
        "last_name",
        "date_of_birth",
        "sex",
        "address",
        "registration_date",
    ],

    "services": [
        "service_id",
        "service_name",
        "category",
        "price",
    ],

    "branches": [
        "branch_id",
        "branch_name",
        "city",
        "address",
        "contact_number",
        "email",
    ],

    "patient_services": [
        "patient_service_id",
        "patient_id",
        "service_id",
        "branch_id",
        "requested_at",
        "status",
    ],

    "specimens": [
        "specimen_id",
        "patient_service_id",
        "specimen_type",
        "collected_at",
        "received_at",
        "status",
    ],

    "lab_results": [
        "result_id",
        "patient_service_id",
        "test_code",
        "result_value",
        "unit",
        "reference_range",
        "result_status",
        "created_at",
        "validated_at",
    ],

    "payments": [
        "payment_id",
        "patient_service_id",
        "amount",
        "payment_method",
        "payment_status",
        "payment_date",
    ],
}


# ---------------------------------------------------------
# ALLOWED STATUS VALUES
# ---------------------------------------------------------

ALLOWED_PATIENT_SERVICE_STATUSES = {
    "Pending",
    "Processing",
    "Completed",
    "Cancelled",
}

ALLOWED_SPECIMEN_STATUSES = {
    "Collected",
    "Received",
    "Processing",
    "Completed",
    "Rejected",
}

ALLOWED_RESULT_STATUSES = {
    "Pending",
    "Validated",
    "Rejected",
}

ALLOWED_PAYMENT_STATUSES = {
    "Pending",
    "Paid",
    "Failed",
    "Refunded",
}


# ---------------------------------------------------------
# READ CSV
# ---------------------------------------------------------

def read_csv(file_path):

    with open(
        file_path,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:

        return list(
            csv.DictReader(file)
        )


# ---------------------------------------------------------
# WRITE CSV
# ---------------------------------------------------------

def write_csv(
    file_path,
    rows,
    columns,
):

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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


# ---------------------------------------------------------
# VALIDATE DATE
# ---------------------------------------------------------

def validate_date(
    value,
    field_name,
):

    if not value:
        return f"{field_name} is required"

    try:

        parsed_date = date.fromisoformat(
            value
        )

    except ValueError:

        return (
            f"{field_name} has invalid "
            f"date format"
        )

    if parsed_date > date.today():

        return (
            f"{field_name} cannot be "
            f"in the future"
        )

    return None


# ---------------------------------------------------------
# VALIDATE TIMESTAMP
# ---------------------------------------------------------

def validate_timestamp(
    value,
    field_name,
):

    if not value:
        return f"{field_name} is required"

    try:

        datetime.fromisoformat(
            value
        )

    except ValueError:

        return (
            f"{field_name} has invalid "
            f"timestamp format"
        )

    return None


# ---------------------------------------------------------
# VALIDATE DECIMAL
# ---------------------------------------------------------

def validate_decimal(
    value,
    field_name,
):

    if not value:
        return f"{field_name} is required"

    try:

        Decimal(value)

    except InvalidOperation:

        return (
            f"{field_name} must be a valid "
            f"number"
        )

    return None


# ---------------------------------------------------------
# VALIDATE ONE ROW
# ---------------------------------------------------------

def validate_row(
    table_name,
    row,
):

    required_columns = REQUIRED_COLUMNS[
        table_name
    ]

    optional_columns = {
        "address",
        "contact_number",
        "email",
        "result_value",
        "unit",
        "reference_range",
        "received_at",
        "validated_at",
    }

    # -----------------------------------------------------
    # REQUIRED FIELDS
    # -----------------------------------------------------

    for column in required_columns:

        if column in optional_columns:
            continue

        if not row.get(column):

            return (
                f"{column} is required"
            )

    # -----------------------------------------------------
    # PATIENTS
    # -----------------------------------------------------

    if table_name == "patients":

        error = validate_date(
            row["date_of_birth"],
            "date_of_birth",
        )

        if error:
            return error

        error = validate_date(
            row["registration_date"],
            "registration_date",
        )

        if error:
            return error

    # -----------------------------------------------------
    # SERVICES
    # -----------------------------------------------------

    elif table_name == "services":

        error = validate_decimal(
            row["price"],
            "price",
        )

        if error:
            return error

    # -----------------------------------------------------
    # PATIENT SERVICES
    # -----------------------------------------------------

    elif table_name == "patient_services":

        error = validate_timestamp(
            row["requested_at"],
            "requested_at",
        )

        if error:
            return error

        if (
            row["status"]
            not in ALLOWED_PATIENT_SERVICE_STATUSES
        ):

            return (
                f"Invalid patient service "
                f"status: {row['status']}"
            )

    # -----------------------------------------------------
    # SPECIMENS
    # -----------------------------------------------------

    elif table_name == "specimens":

        error = validate_timestamp(
            row["collected_at"],
            "collected_at",
        )

        if error:
            return error

        if row["received_at"]:

            error = validate_timestamp(
                row["received_at"],
                "received_at",
            )

            if error:
                return error

            collected_at = datetime.fromisoformat(
                row["collected_at"]
            )

            received_at = datetime.fromisoformat(
                row["received_at"]
            )

            if received_at < collected_at:

                return (
                    "received_at cannot be "
                    "before collected_at"
                )

        if (
            row["status"]
            not in ALLOWED_SPECIMEN_STATUSES
        ):

            return (
                f"Invalid specimen status: "
                f"{row['status']}"
            )

    # -----------------------------------------------------
    # LAB RESULTS
    # -----------------------------------------------------

    elif table_name == "lab_results":

        error = validate_timestamp(
            row["created_at"],
            "created_at",
        )

        if error:
            return error

        if row["validated_at"]:

            error = validate_timestamp(
                row["validated_at"],
                "validated_at",
            )

            if error:
                return error

            created_at = datetime.fromisoformat(
                row["created_at"]
            )

            validated_at = datetime.fromisoformat(
                row["validated_at"]
            )

            if validated_at < created_at:

                return (
                    "validated_at cannot be "
                    "before created_at"
                )

        if (
            row["result_status"]
            not in ALLOWED_RESULT_STATUSES
        ):

            return (
                f"Invalid result status: "
                f"{row['result_status']}"
            )

        if row["result_value"]:

            error = validate_decimal(
                row["result_value"],
                "result_value",
            )

            if error:
                return error

    # -----------------------------------------------------
    # PAYMENTS
    # -----------------------------------------------------

    elif table_name == "payments":

        error = validate_decimal(
            row["amount"],
            "amount",
        )

        if error:
            return error

        error = validate_timestamp(
            row["payment_date"],
            "payment_date",
        )

        if error:
            return error

        if (
            row["payment_status"]
            not in ALLOWED_PAYMENT_STATUSES
        ):

            return (
                f"Invalid payment status: "
                f"{row['payment_status']}"
            )

    return None


# ---------------------------------------------------------
# VALIDATE ONE FILE
# ---------------------------------------------------------

def validate_file(
    table_name,
    file_path,
):

    print()
    print(
        f"Validating: {file_path}"
    )

    rows = read_csv(file_path)

    valid_rows = []
    rejected_rows = []

    for row in rows:

        error = validate_row(
            table_name,
            row,
        )

        if error:

            row["rejection_reason"] = error

            rejected_rows.append(row)

        else:

            valid_rows.append(row)

    processed_file = (
        PROCESSED_FOLDER
        / table_name
        / file_path.name
    )

    rejected_file = (
        REJECTED_FOLDER
        / table_name
        / file_path.name
    )

    # -----------------------------------------------------
    # WRITE VALID RECORDS
    # -----------------------------------------------------

    if valid_rows:

        columns = list(
            valid_rows[0].keys()
        )

        write_csv(
            processed_file,
            valid_rows,
            columns,
        )

        print(
            f"Valid records written: "
            f"{len(valid_rows)}"
        )

    # -----------------------------------------------------
    # WRITE REJECTED RECORDS
    # -----------------------------------------------------

    if rejected_rows:

        columns = list(
            rejected_rows[0].keys()
        )

        write_csv(
            rejected_file,
            rejected_rows,
            columns,
        )

        print(
            f"Rejected records written: "
            f"{len(rejected_rows)}"
        )

    return (
        len(valid_rows),
        len(rejected_rows),
    )


# ---------------------------------------------------------
# MAIN VALIDATION
# ---------------------------------------------------------

def main():

    print(
        "Starting validation..."
    )

    total_valid = 0
    total_rejected = 0

    successful_tables = []
    rejected_tables = []

    # -----------------------------------------------------
    # LOOP THROUGH TABLES
    # -----------------------------------------------------

    for table_name in REQUIRED_COLUMNS:

        table_folder = (
            RAW_FOLDER / table_name
        )

        if not table_folder.exists():
            continue

        raw_files = sorted(
            table_folder.glob("*.csv")
        )

        table_had_new_batch = False
        table_had_rejection = False

        for raw_file in raw_files:

            processed_file = (
                PROCESSED_FOLDER
                / table_name
                / raw_file.name
            )

            rejected_file = (
                REJECTED_FOLDER
                / table_name
                / raw_file.name
            )

            # -------------------------------------------------
            # IDEMPOTENCY
            # -------------------------------------------------

            if (
                processed_file.exists()
                or rejected_file.exists()
            ):

                print(
                    f"Skipping already processed "
                    f"batch: {raw_file.name}"
                )

                continue

            table_had_new_batch = True

            valid_count, rejected_count = (
                validate_file(
                    table_name,
                    raw_file,
                )
            )

            total_valid += valid_count
            total_rejected += rejected_count

            if rejected_count > 0:

                table_had_rejection = True

        # -------------------------------------------------
        # TABLE RESULT
        # -------------------------------------------------

        if table_had_new_batch:

            if table_had_rejection:

                rejected_tables.append(
                    table_name
                )

            else:

                successful_tables.append(
                    table_name
                )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    print()
    print(
        f"Total valid records: "
        f"{total_valid}"
    )

    print(
        f"Total rejected records: "
        f"{total_rejected}"
    )

    print()

    print(
        "Tables successfully validated:"
    )

    for table_name in successful_tables:

        print(
            f"  ✓ {table_name}"
        )

    print()

    print(
        "Tables with rejected records:"
    )

    for table_name in rejected_tables:

        print(
            f"  ✗ {table_name}"
        )

    return (
        total_valid,
        total_rejected,
        successful_tables,
        rejected_tables,
    )


# ---------------------------------------------------------
# RUN DIRECTLY
# ---------------------------------------------------------

if __name__ == "__main__":
    main()