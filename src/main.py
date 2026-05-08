import argparse
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from src.translator import translate
from src.tts import synthesize
from src.deck import build_deck


INPUT = Path("input/phrases.txt")
OUTPUT = Path("output/interview.apkg")
OUTPUT.parent.mkdir(exist_ok=True)


def read_phrases() -> list[str]:
    lines = INPUT.read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]


def build_cards_for(phrase: str, num_examples: int) -> list[dict]:
    print(f"→ {phrase}")
    try:
        data = translate(phrase, num_examples=num_examples)
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
    parser = argparse.ArgumentParser(description="Build an Anki deck from a phrase list.")
    default_n = int(os.environ.get("NUM_EXAMPLES", "2"))
    parser.add_argument(
        "-n", "--examples",
        type=int,
        default=default_n,
        help=f"Number of example sentences per phrase (default: {default_n}, from NUM_EXAMPLES env or 2).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.examples < 1:
        raise SystemExit("--examples must be >= 1")

    phrases = read_phrases()
    print(f"Building cards for {len(phrases)} phrases ({args.examples} example(s) each)…\n")
    all_cards = []
    for p in phrases:
        all_cards.extend(build_cards_for(p, num_examples=args.examples))
    if not all_cards:
        print("No cards built. Check API keys and input.")
        return
    build_deck(all_cards, str(OUTPUT))
    print(f"\n✓ Wrote {len(all_cards)} cards → {OUTPUT}")


if __name__ == "__main__":
    main()
