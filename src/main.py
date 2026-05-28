import argparse
import tomllib
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from src.translator import translate, DEFAULT_MODEL
from src.tts import synthesize
from src.deck import build_deck
from src.learned import record_learned, drop_lines_from_index, parse_index_line

INPUT_ROOT = Path("input")
OUTPUT_ROOT = Path("output")
LEARNED_FILE = OUTPUT_ROOT / "learned.json"
SETUP_FILE = "setup.toml"
INDEX_FILE = "index.txt"
DEFAULT_NUM_EXAMPLES = 1


def discover_decks() -> list[str]:
    if not INPUT_ROOT.is_dir():
        return []
    decks = []
    for setup in INPUT_ROOT.rglob(SETUP_FILE):
        if (setup.parent / INDEX_FILE).is_file():
            decks.append(setup.parent.relative_to(INPUT_ROOT).as_posix())
    return sorted(decks)


def load_setup(deck_dir: Path) -> dict:
    setup_path = deck_dir / SETUP_FILE
    if not setup_path.is_file():
        raise SystemExit(f"Missing {SETUP_FILE} in {deck_dir}")
    with setup_path.open("rb") as f:
        setup = tomllib.load(f)
    if "prompt" not in setup:
        raise SystemExit(f"{setup_path} must define a 'prompt' field")
    return setup


def read_phrases(path: Path) -> list[tuple[str, str | None]]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        phrase, sentence = parse_index_line(line)
        if phrase:
            out.append((phrase, sentence))
    return out


def build_cards_for(phrase: str, sentence: str | None, num_examples: int, prompt_name: str, model: str) -> list[dict]:
    print(f"→ {phrase}" + ("  (draft sentence)" if sentence else ""))
    try:
        data = translate(phrase, num_examples=num_examples, prompt_name=prompt_name, model=model, sentence=sentence)
    except Exception as e:
        print(f"  ✗ translate failed: {e}")
        return []

    cards = []
    for sentence in data["examples"]:
        try:
            audio = synthesize(sentence)
        except Exception as e:
            print(f"  ⚠ tts failed for '{sentence}': {e}")
            audio = None
        cards.append({
            "target_expression": data["phrase"],
            "definition": data["definition"],
            "example_sentence": sentence,
            "audio_file": audio,
        })
    return cards


def parse_args():
    parser = argparse.ArgumentParser(description="Build an Anki deck from a curated phrase list.")
    available = discover_decks()
    parser.add_argument(
        "-p", "--prompt",
        required=True,
        help=(
            "Deck path under input/ (e.g. 'English/common'). The directory must contain "
            f"{INDEX_FILE} (phrase list) and {SETUP_FILE} (prompt + options). "
            f"Available: {', '.join(available) or '(none)'}."
        ),
    )
    return parser.parse_args()


def main():
    args = parse_args()

    deck_path = Path(args.prompt)
    deck_dir = INPUT_ROOT / deck_path
    if not deck_dir.is_dir():
        raise SystemExit(f"Deck directory not found: {deck_dir}")

    setup = load_setup(deck_dir)
    num_examples = int(setup.get("num_examples", DEFAULT_NUM_EXAMPLES))
    if num_examples < 1:
        raise SystemExit("num_examples must be >= 1")

    prompt_name = setup["prompt"]
    model = setup.get("model", DEFAULT_MODEL)

    index_path = deck_dir / INDEX_FILE
    output_path = OUTPUT_ROOT / deck_path.with_suffix(".apkg")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    deck_name = "::".join(deck_path.parts)

    phrases = read_phrases(index_path)
    print(
        f"[{deck_name}] prompt={prompt_name} model={model} "
        f"{len(phrases)} phrases × {num_examples} example(s) → {output_path}\n"
    )
    all_cards = []
    learned_now = []
    for phrase, sentence in phrases:
        cards = build_cards_for(phrase, sentence, num_examples=num_examples, prompt_name=prompt_name, model=model)
        if cards:
            all_cards.extend(cards)
            learned_now.append(phrase)
    if not all_cards:
        print("No cards built. Check API keys and input.")
        return
    build_deck(all_cards, str(output_path), deck_name=deck_name)
    print(f"\n✓ Wrote {len(all_cards)} cards → {output_path}")

    record_learned(learned_now, LEARNED_FILE)
    drop_lines_from_index(index_path, set(learned_now))
    print(f"✓ Moved {len(learned_now)} phrase(s) to {LEARNED_FILE}")


if __name__ == "__main__":
    main()
