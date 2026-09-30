import csv
from datetime import datetime
from pathlib import Path

import os
import psycopg
from dotenv import load_dotenv

from state_manager import get_watermark


load_dotenv()


# ---------------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------------

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


# ---------------------------------------------------------
# FOLDERS
# ---------------------------------------------------------

RAW_FOLDER = Path("data/raw")


# ---------------------------------------------------------
# TABLES
# ---------------------------------------------------------

TABLES = [
    "patients",
    "services",
    "branches",
    "patient_services",
    "specimens",
    "lab_results",
    "payments",
]


# ---------------------------------------------------------
# INCREMENTAL COLUMNS
# ---------------------------------------------------------

INCREMENTAL_COLUMNS = {
    "patients": "registration_date",
    "patient_services": "requested_at",
    "specimens": "collected_at",
    "lab_results": "created_at",
    "payments": "payment_date",
}


# ---------------------------------------------------------
# WRITE CSV
# ---------------------------------------------------------

def write_csv(table_name, rows, columns):

    table_folder = (
        RAW_FOLDER / table_name
    )

    table_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    file_path = (
        table_folder
        / f"{table_name}_{timestamp}.csv"
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

    print(
        f"Created raw file: {file_path}"
    )

    return file_path


# ---------------------------------------------------------
# EXTRACT ONE TABLE
# ---------------------------------------------------------

def extract_table(
    connection,
    table_name,
):

    print()
    print(
        f"Extracting table: {table_name}"
    )

    incremental_column = (
        INCREMENTAL_COLUMNS.get(table_name)
    )

    pending_watermark = None

    # -----------------------------------------------------
    # INCREMENTAL EXTRACTION
    # -----------------------------------------------------

    if incremental_column:

        watermark = get_watermark(
            table_name
        )

        if watermark:

            query = f"""
                SELECT *
                FROM {table_name}
                WHERE {incremental_column} > %s
                ORDER BY {incremental_column};
            """

            print(
                f"Incremental extraction using "
                f"{incremental_column} > {watermark}"
            )

            with connection.cursor() as cursor:

                cursor.execute(
                    query,
                    (watermark,),
                )

                rows = cursor.fetchall()

                columns = [
                    description.name
                    for description in cursor.description
                ]

        else:

            query = f"""
                SELECT *
                FROM {table_name}
                ORDER BY {incremental_column};
            """

            print(
                "No watermark found. "
                "Performing initial full extraction."
            )

            with connection.cursor() as cursor:

                cursor.execute(query)

                rows = cursor.fetchall()

                columns = [
                    description.name
                    for description in cursor.description
                ]

    # -----------------------------------------------------
    # FULL SNAPSHOT
    # -----------------------------------------------------

    else:

        query = f"""
            SELECT *
            FROM {table_name};
        """

        print(
            "This table does not have an "
            "incremental column."
        )

        print(
            "Performing full snapshot extraction."
        )

        with connection.cursor() as cursor:

            cursor.execute(query)

            rows = cursor.fetchall()

            columns = [
                description.name
                for description in cursor.description
            ]

    # -----------------------------------------------------
    # CONVERT ROWS TO DICTIONARIES
    # -----------------------------------------------------

    dictionary_rows = []

    for row in rows:

        row_dict = {}

        for column, value in zip(
            columns,
            row,
        ):

            if value is None:

                row_dict[column] = ""

            elif isinstance(
                value,
                datetime,
            ):

                row_dict[column] = (
                    value.isoformat(
                        sep=" "
                    )
                )

            elif hasattr(
                value,
                "isoformat",
            ):

                row_dict[column] = (
                    value.isoformat()
                )

            else:

                row_dict[column] = str(
                    value
                )

        dictionary_rows.append(
            row_dict
        )

    # -----------------------------------------------------
    # NO NEW RECORDS
    # -----------------------------------------------------

    if not dictionary_rows:

        print(
            f"No new records found for "
            f"{table_name}."
        )

        return {
            "records": 0,
            "watermark": None,
            "file_path": None,
        }

    # -----------------------------------------------------
    # WRITE RAW DATA
    # -----------------------------------------------------

    file_path = write_csv(
        table_name,
        dictionary_rows,
        columns,
    )

    # -----------------------------------------------------
    # CALCULATE NEW WATERMARK
    # -----------------------------------------------------
    #
    # IMPORTANT:
    #
    # We DO NOT save this watermark here.
    #
    # We only return it to the pipeline.
    #
    # The pipeline will save it only after
    # successful processing.
    # -----------------------------------------------------

    if incremental_column:

        pending_watermark = max(
            row[incremental_column]
            for row in dictionary_rows
        )

        print(
            f"Pending watermark for "
            f"{table_name}: "
            f"{pending_watermark}"
        )

    print(
        f"Extracted "
        f"{len(dictionary_rows)} "
        f"records from {table_name}."
    )

    return {
        "records": len(dictionary_rows),
        "watermark": pending_watermark,
        "file_path": file_path,
    }


# ---------------------------------------------------------
# MAIN EXTRACTION FUNCTION
# ---------------------------------------------------------

def main():

    print(
        "Starting extraction..."
    )

    total_extracted = 0

    pending_watermarks = {}
    extracted_files = []

    with psycopg.connect(
        **DB_CONFIG
    ) as connection:

        for table_name in TABLES:

            result = extract_table(
                connection,
                table_name,
            )

            total_extracted += (
                result["records"]
            )

            if result["watermark"]:

                pending_watermarks[
                    table_name
                ] = result["watermark"]
            if result["file_path"]:
                
                extracted_files.append(result["file_path"])

    print()
    print(
        f"Total records extracted: "
        f"{total_extracted}"
    )

    return (
        total_extracted,
        pending_watermarks,
        extracted_files,
    )


# ---------------------------------------------------------
# RUN DIRECTLY
# ---------------------------------------------------------

if __name__ == "__main__":
    main()