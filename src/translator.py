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


def translate(
    phrase: str,
    num_examples: int = 2,
    prompt_name: str = "interview",
    model: str = DEFAULT_MODEL,
) -> dict:
    template = _load_template(prompt_name)
    prompt = _build_prompt(template, num_examples)
    msg = client.messages.create(
        model=model,
        max_tokens=800,
        messages=[{"role": "user", "content": prompt + " " + phrase}],
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
