import json
from pathlib import Path

DELIMITER = "|"


def parse_index_line(line: str) -> tuple[str | None, str | None]:
    """Split a raw index line into (phrase, sentence).

    Returns (None, None) for blank lines and comments. A line may carry an
    optional draft sentence after a '|': 'phrase | draft sentence'.
    """
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None, None
    if DELIMITER in stripped:
        phrase, sentence = stripped.split(DELIMITER, 1)
        return phrase.strip(), (sentence.strip() or None)
    return stripped, None


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
    kept = []
    for line in lines:
        phrase, _ = parse_index_line(line)
        if phrase is not None and phrase in phrases:
            continue
        kept.append(line)
    text = "\n".join(kept)
    if text:
        text += "\n"
    index_path.write_text(text, encoding="utf-8")
