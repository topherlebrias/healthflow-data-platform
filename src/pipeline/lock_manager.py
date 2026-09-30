from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOCK_FILE = PROJECT_ROOT / "state" / "pipeline.lock"


def acquire_lock():
    LOCK_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if LOCK_FILE.exists():
        return False

    LOCK_FILE.write_text(
        "HealthFlow pipeline is currently running.",
        encoding="utf-8",
    )

    return True


def release_lock():
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()