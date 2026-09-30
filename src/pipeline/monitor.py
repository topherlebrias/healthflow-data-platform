import csv
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_FILE = PROJECT_ROOT / "logs" / "pipeline_runs.csv"


def load_runs():
    if not LOG_FILE.exists():
        raise FileNotFoundError(
            f"Pipeline log does not exist: {LOG_FILE}"
        )

    with open(LOG_FILE, "r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def calculate_duration(start_time, end_time):
    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)

    duration = end - start

    return duration.total_seconds()


def determine_run_status(run):
    status = run["status"]
    rejected = int(run["records_rejected"])

    if status == "FAILED":
        return "FAILED"

    if rejected > 0:
        return "SUCCESS_WITH_DATA_QUALITY_ISSUES"

    return "SUCCESS"


def main():
    runs = load_runs()

    if not runs:
        print("No pipeline runs found.")
        return

    latest_run = runs[-1]

    successful_runs = 0
    quality_issue_runs = 0
    failed_runs = 0

    total_rejected = 0
    total_extracted = 0

    durations = []

    for run in runs:
        run_status = determine_run_status(run)

        if run_status == "SUCCESS":
            successful_runs += 1

        if run_status == "SUCCESS_WITH_DATA_QUALITY_ISSUES":
            quality_issue_runs += 1

        if run_status == "FAILED":
            failed_runs += 1

        total_rejected += int(run["records_rejected"])
        total_extracted += int(run["records_extracted"])

        if run["end_time"]:
            duration = calculate_duration(
                run["start_time"],
                run["end_time"],
            )

            durations.append(duration)

    total_runs = len(runs)

    if durations:
        average_duration = sum(durations) / len(durations)
    else:
        average_duration = 0

    latest_extracted = int(
        latest_run["records_extracted"]
    )

    latest_rejected = int(
        latest_run["records_rejected"]
    )

    if latest_extracted > 0:
        latest_rejection_rate = (
            latest_rejected / latest_extracted
        ) * 100
    else:
        latest_rejection_rate = 0

    latest_status = determine_run_status(latest_run)

    print("=" * 60)
    print("HEALTHFLOW PIPELINE MONITORING")
    print("=" * 60)

    print()
    print("LATEST PIPELINE RUN")
    print("-" * 60)

    print(f"Run ID: {latest_run['run_id']}")
    print(f"Start time: {latest_run['start_time']}")
    print(f"End time: {latest_run['end_time']}")
    print(f"Status: {latest_status}")

    print(
        f"Records extracted: "
        f"{latest_run['records_extracted']}"
    )

    print(
        f"Records valid: "
        f"{latest_run['records_valid']}"
    )

    print(
        f"Records rejected: "
        f"{latest_run['records_rejected']}"
    )

    print(
        f"Records transformed: "
        f"{latest_run['records_transformed']}"
    )

    print()
    print("LATEST DATA QUALITY")
    print("-" * 60)

    print(
        f"Latest rejection rate: "
        f"{latest_rejection_rate:.2f}%"
    )

    print()
    print("PIPELINE HISTORY")
    print("-" * 60)

    print(f"Total runs: {total_runs}")
    print(f"Clean successful runs: {successful_runs}")
    print(
        f"Successful runs with quality issues: "
        f"{quality_issue_runs}"
    )
    print(f"Failed runs: {failed_runs}")

    print(
        f"Total records extracted: "
        f"{total_extracted}"
    )

    print(
        f"Total records rejected: "
        f"{total_rejected}"
    )

    print()
    print("PERFORMANCE")
    print("-" * 60)

    print(
        f"Average pipeline duration: "
        f"{average_duration:.2f} seconds"
    )

    print()
    print("=" * 60)
    print("PIPELINE MONITORING COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()