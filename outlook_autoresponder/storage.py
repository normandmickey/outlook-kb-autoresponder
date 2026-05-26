import json
from pathlib import Path


def state_path_for(data_path: Path):
    return data_path / 'state.json'


def _ensure(data_path: Path):
    data_path.mkdir(parents=True, exist_ok=True)
    state_path = state_path_for(data_path)
    if not state_path.exists():
        state_path.write_text(json.dumps({'processed_message_ids': []}, indent=2))
    return state_path


def load_state(data_path: Path):
    state_path = _ensure(data_path)
    return json.loads(state_path.read_text())


def save_state(data_path: Path, state):
    state_path = _ensure(data_path)
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True))


def is_processed(data_path: Path, message_id: str) -> bool:
    state = load_state(data_path)
    return message_id in state.get('processed_message_ids', [])


def mark_processed(data_path: Path, message_id: str):
    state = load_state(data_path)
    ids = state.setdefault('processed_message_ids', [])
    if message_id not in ids:
        ids.append(message_id)
    save_state(data_path, state)
