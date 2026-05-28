import json
import os
from pathlib import Path
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _load_template(prompt_name: str) -> str:
    path = PROMPTS_DIR / f"{prompt_name}.txt"
    if not path.is_file():
        available = sorted(p.stem for p in PROMPTS_DIR.glob("*.txt"))
        raise FileNotFoundError(
            f"Prompt '{prompt_name}' not found at {path}. Available: {available}"
        )
    return path.read_text(encoding="utf-8")


def _build_prompt(template: str, n: int) -> str:
    slots = ",\n".join(
        ['    "<example sentence using the phrase>"']
        + ['    "<another example, different context>"'] * (n - 1)
    )
    return template.format(n=n, example_slots=slots)


DEFAULT_MODEL = "claude-sonnet-4-6"


def _draft_instructions(sentence: str) -> str:
    return (
        "A draft example sentence is provided below. Use it as the single example "
        "sentence instead of inventing a new one, keeping its original meaning and context.\n"
        "- Fix any grammar or wording mistakes.\n"
        "- If it is shorter than 8 words, naturally expand it to between 8 and 20 words.\n"
        "- If it is longer than 20 words, condense it to between 8 and 20 words.\n"
        "- The target phrase must still appear in the sentence.\n"
        f"\nDraft sentence: {sentence}"
    )


def translate(
    phrase: str,
    num_examples: int = 2,
    prompt_name: str = "interview",
    model: str = DEFAULT_MODEL,
    sentence: str | None = None,
) -> dict:
    if sentence:
        num_examples = 1
    template = _load_template(prompt_name)
    prompt = _build_prompt(template, num_examples)
    content = prompt + " " + phrase
    if sentence:
        content += "\n\n" + _draft_instructions(sentence)
    msg = client.messages.create(
        model=model,
        max_tokens=800,
        messages=[{"role": "user", "content": content}],
    )
    text = msg.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    data = json.loads(text)
    data["examples"] = data["examples"][:num_examples]
    return data
