import json
from pathlib import Path


STATE_FILE = Path("state/pipeline_state.json")


def load_state():
    if not STATE_FILE.exists():
        return {}

    with open(STATE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=4)


def get_watermark(table_name):
    state = load_state()
    return state.get(table_name)


def update_watermark(table_name, watermark):
    state = load_state()
    state[table_name] = watermark
    save_state(state)