import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client


# ---------------------------------------------------------
# LOAD .ENV FROM PROJECT ROOT
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

BUCKET_NAME = "healthflow-data-lake"


# ---------------------------------------------------------
# SUPABASE CLIENT
# ---------------------------------------------------------

def get_supabase_client():
    if not SUPABASE_URL:
        raise ValueError(
            f"SUPABASE_URL is missing from {ENV_FILE}"
        )

    if not SUPABASE_KEY:
        raise ValueError(
            f"SUPABASE_KEY is missing from {ENV_FILE}"
        )

    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
    )


# ---------------------------------------------------------
# UPLOAD FILE
# ---------------------------------------------------------

def upload_file(local_file_path):
    local_file_path = Path(local_file_path)

    if not local_file_path.exists():
        raise FileNotFoundError(
            f"File does not exist: {local_file_path}"
        )

    supabase = get_supabase_client()

    storage_path = (
        f"raw/{local_file_path.parent.name}/"
        f"{local_file_path.name}"
    )

    with open(local_file_path, "rb") as file:
        supabase.storage.from_(BUCKET_NAME).upload(
            storage_path,
            file,
            file_options={
                "content-type": "text/csv",
            },
        )

    print()
    print("File uploaded successfully.")
    print(f"Local file: {local_file_path}")
    print(f"Storage path: {storage_path}")

    return storage_path


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

def main():
    raw_folder = PROJECT_ROOT / "data" / "raw"

    csv_files = sorted(
        raw_folder.rglob("*.csv"),
        key=lambda file: file.stat().st_mtime,
        reverse=True,
    )

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files were found inside data/raw."
        )

    latest_file = csv_files[0]

    print("Testing Supabase Storage upload...")
    print(f"Selected file: {latest_file}")

    upload_file(latest_file)


if __name__ == "__main__":
    main()