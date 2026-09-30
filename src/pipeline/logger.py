import csv
from datetime import datetime
from pathlib import Path


LOG_FILE = Path("logs/pipeline_runs.csv")


def start_run():
    """Create a new pipeline run record."""

    LOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    run_id = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )

    start_time = datetime.now()

    return {
        "run_id": run_id,
        "start_time": start_time,
        "end_time": "",
        "status": "RUNNING",
        "records_extracted": 0,
        "records_valid": 0,
        "records_rejected": 0,
        "records_transformed": 0,
        "error_message": "",
    }


def finish_run(
    run_info,
    status,
    records_extracted=0,
    records_valid=0,
    records_rejected=0,
    records_transformed=0,
    error_message="",
):
    """Complete a pipeline run and save it."""

    run_info["end_time"] = datetime.now().isoformat(
        sep=" ",
        timespec="seconds",
    )

    run_info["status"] = status

    run_info["records_extracted"] = (
        records_extracted
    )

    run_info["records_valid"] = (
        records_valid
    )

    run_info["records_rejected"] = (
        records_rejected
    )

    run_info["records_transformed"] = (
        records_transformed
    )

    run_info["error_message"] = error_message

    file_exists = LOG_FILE.exists()

    with open(
        LOG_FILE,
        "a",
        newline="",
        encoding="utf-8",
    ) as file:

        fieldnames = [
            "run_id",
            "start_time",
            "end_time",
            "status",
            "records_extracted",
            "records_valid",
            "records_rejected",
            "records_transformed",
            "error_message",
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(run_info)