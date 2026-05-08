import json
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

PROMPT_TEMPLATE = """You are helping a Russian-speaking middle/senior frontend developer prepare for tech interviews in English.

For the phrase below, return STRICT JSON with this exact shape:

{{
  "phrase": "<the phrase, normalized lowercase unless proper noun>",
  "definition": "<Russian translation followed by ' — ' and a short Russian usage note (when to use it, formality, tone). One line, under 120 chars.>",
  "examples": [
{example_slots}
  ]
}}

Rules:
- Return EXACTLY {n} example sentence(s).
- Examples must sound like real tech-interview speech: coding problems, system design discussion, behavioral answers, clarifying questions.
- Vary contexts across the examples (e.g. whiteboard, system-design, behavioral).
- Each example 8-20 words. Natural spoken English, not textbook.
- The target phrase must appear verbatim (or near-verbatim, allowing natural conjugation) in each example.
- Return ONLY the JSON. No prose, no markdown fences.

Phrase: """


def _build_prompt(n: int) -> str:
    slots = ",\n".join(
        ['    "<example sentence using the phrase, in tech-interview register>"']
        + ['    "<another example, different context>"'] * (n - 1)
    )
    return PROMPT_TEMPLATE.format(n=n, example_slots=slots)


def translate(phrase: str, num_examples: int = 2) -> dict:
    prompt = _build_prompt(num_examples)
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt + phrase}],
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
