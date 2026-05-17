# anki-auto

Generate Anki cards for tech-interview English from a curated phrase list.

Each phrase becomes one card per example sentence:

- **Front:** an example sentence using the phrase, in real frontend / web-dev interview register.
- **Back:** the same sentence + the target phrase + Russian translation (with web-dev anglicisms where natural) + an ElevenLabs audio clip.

Pipeline: `input/<deck/path>/index.txt` → Claude Sonnet (translation + N examples as JSON, using the template named in `setup.toml`) → ElevenLabs Multilingual v2 TTS → `genanki` → `output/<deck/path>.apkg`.

Each deck lives in its own directory under `input/`. The directory path becomes the Anki deck name (`/` → `::`). Two decks ship out of the box:

- `input/English/phrases/interview/` — frontend tech-interview register (deck `English::phrases::interview`)
- `input/English/common/` — everyday vocabulary (deck `English::common`)

Add your own by creating `input/<your/path>/` with two files: `index.txt` (one phrase per line) and `setup.toml` (which prompt template to use).

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# edit .env and paste your ANTHROPIC_API_KEY and ELEVENLABS_API_KEY
```

If `Activate.ps1` is blocked: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` (one-time).

## Usage

Curate `input/<deck/path>/index.txt` (one phrase per line; lines starting with `#` are skipped). Then:

```powershell
poe build-interview                              # English::phrases::interview
poe build-common                                 # English::common
poe build -- -p English/common                   # any deck by path
poe clean                                        # wipe output/ and media/
poe                                              # list all tasks
```

Output lands at `output/<deck/path>.apkg`. Import into Anki with **File → Import** (or `Ctrl+Shift+I`). The Anki deck name mirrors the directory path with `/` replaced by `::`.

## Adding a new deck

1. Create a directory `input/<your/path>/` — the path becomes the Anki deck name.
2. Add `index.txt` with one phrase per line (`#` lines are skipped).
3. Add `setup.toml` pointing at a prompt template:

   ```toml
   prompt = "common"            # required: name of prompts/<name>.txt
   num_examples = 1             # optional: default 1
   model = "claude-sonnet-4-6"  # optional: any Claude model id
   ```

4. Run `poe build -- -p <your/path>`.

If you need a new prompt style, drop a template into `prompts/<name>.txt` — it must contain `{n}` and `{example_slots}` placeholders and escape literal JSON braces as `{{` / `}}` (see `prompts/interview.txt`).

## Configuration

All knobs live in `.env`:

| Variable               | Default                   | Notes                                         |
|------------------------|---------------------------|-----------------------------------------------|
| `ANTHROPIC_API_KEY`    | —                         | Required.                                     |
| `ELEVENLABS_API_KEY`   | —                         | Required.                                     |
| `ELEVENLABS_VOICE_ID`  | `nPczCjzI2devNBz1zQrb`    | Brian. Pick one and stick with it.            |
| `ELEVENLABS_MODEL`     | `eleven_multilingual_v2`  | Use `eleven_turbo_v2_5` for cheap iteration.  |

## Re-runs are safe

- Note GUIDs are stable per `(target_expression, example_sentence)` — re-importing the deck **updates** existing cards instead of duplicating, and your review history is preserved.
- Audio is cached in `media/` keyed by voice ID + text — rerunning doesn't re-pay ElevenLabs for sentences you've already synthesized.
- Adding new lines to `phrases.txt` and rerunning only generates the deltas.

## Cost

Per 100 phrases at 2 examples each (200 cards):

- Claude Sonnet 4.6 translations: ~$2
- ElevenLabs Multilingual v2 TTS: ~$3–4

Drop to Haiku — set `model = "claude-haiku-4-5-20251001"` in the deck's `setup.toml`, and switch to Turbo (`eleven_turbo_v2_5` in `.env`) — for ~10× cheaper iteration while you're tuning a prompt.

## Project layout

```
anki-auto/
├── prompts/                            # Claude prompt templates (flat)
│   ├── interview.txt
│   └── common.txt
├── input/                              # one directory per deck (you edit these)
│   └── English/
│       ├── common/
│       │   ├── index.txt               # phrases, one per line
│       │   └── setup.toml              # prompt = "common"
│       └── phrases/
│           └── interview/
│               ├── index.txt
│               └── setup.toml          # prompt = "interview"
├── output/<deck/path>.apkg             # generated decks (gitignored)
├── media/                              # audio cache (gitignored)
├── src/
│   ├── main.py                         # CLI orchestrator + deck discovery
│   ├── translator.py                   # loads prompts/<name>.txt and calls Claude
│   ├── tts.py                          # ElevenLabs synthesis with on-disk cache
│   └── deck.py                         # genanki model + deck builder
├── pyproject.toml                      # poethepoet task definitions
└── requirements.txt
```

## Tweaking quality

The files in `prompts/` are the single highest-leverage spot in the repo. After every batch, look at a handful of generated cards and adjust the relevant prompt — it's where 90% of the quality lives, not in the code.
