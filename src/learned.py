import json
from pathlib import Path


def load_learned(path: Path) -> dict[str, int]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def record_learned(phrases: list[str], path: Path) -> dict[str, int]:
    bank = load_learned(path)
    for phrase in phrases:
        bank[phrase] = bank.get(phrase, 0) + 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return bank


def drop_lines_from_index(index_path: Path, phrases: set[str]) -> None:
    lines = index_path.read_text(encoding="utf-8").splitlines()
    kept = [
        line for line in lines
        if not (line.strip() and not line.strip().startswith("#") and line.strip() in phrases)
    ]
    text = "\n".join(kept)
    if text:
        text += "\n"
    index_path.write_text(text, encoding="utf-8")
