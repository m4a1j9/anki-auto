# anki-auto

Generate Anki cards for tech-interview English from a curated phrase list.

Each phrase becomes one card per example sentence:

- **Front:** an example sentence using the phrase, in real frontend / web-dev interview register.
- **Back:** the same sentence + the target phrase + Russian translation (with web-dev anglicisms where natural) + an ElevenLabs audio clip.

Pipeline: `input/phrases.txt` → Claude Sonnet (translation + N examples as JSON) → ElevenLabs Multilingual v2 TTS → `genanki` → `output/interview.apkg`.

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

Curate `input/phrases.txt` (one phrase per line; lines starting with `#` are skipped). Then:

```powershell
poe build       # default: 2 examples per phrase
poe build1      # 1 example per phrase
poe build3      # 3 examples per phrase
poe build -- -n 5    # arbitrary count
poe clean       # wipe output/ and media/
poe             # list all tasks
```

Output lands at `output/interview.apkg`. Import into Anki with **File → Import** (or `Ctrl+Shift+I`). The deck is created at `English::phrases::interview`.

## Configuration

All knobs live in `.env`:

| Variable               | Default                   | Notes                                         |
|------------------------|---------------------------|-----------------------------------------------|
| `ANTHROPIC_API_KEY`    | —                         | Required.                                     |
| `ELEVENLABS_API_KEY`   | —                         | Required.                                     |
| `ELEVENLABS_VOICE_ID`  | `nPczCjzI2devNBz1zQrb`    | Brian. Pick one and stick with it.            |
| `ELEVENLABS_MODEL`     | `eleven_multilingual_v2`  | Use `eleven_turbo_v2_5` for cheap iteration.  |
| `NUM_EXAMPLES`         | `2`                       | Overridden by `-n` / `--examples` CLI flag.   |

## Re-runs are safe

- Note GUIDs are stable per `(target_expression, example_sentence)` — re-importing the deck **updates** existing cards instead of duplicating, and your review history is preserved.
- Audio is cached in `media/` keyed by voice ID + text — rerunning doesn't re-pay ElevenLabs for sentences you've already synthesized.
- Adding new lines to `phrases.txt` and rerunning only generates the deltas.

## Cost

Per 100 phrases at 2 examples each (200 cards):

- Claude Sonnet 4.6 translations: ~$2
- ElevenLabs Multilingual v2 TTS: ~$3–4

Drop to Haiku (`claude-haiku-4-5-20251001` in `src/translator.py`) and Turbo (`eleven_turbo_v2_5` in `.env`) for ~10× cheaper iteration while you're tuning the prompt.

## Project layout

```
anki-auto/
├── input/phrases.txt        # curated phrase list (you edit this)
├── output/interview.apkg    # generated deck (gitignored)
├── media/                   # audio cache (gitignored)
├── src/
│   ├── main.py              # CLI orchestrator
│   ├── translator.py        # Claude prompt — the highest-leverage file
│   ├── tts.py               # ElevenLabs synthesis with on-disk cache
│   └── deck.py              # genanki model + deck builder
├── pyproject.toml           # poethepoet task definitions
└── requirements.txt
```

## Tweaking quality

The translation prompt in `src/translator.py` is the single highest-leverage file in the repo. After every batch, look at a handful of generated cards and adjust the prompt — it's where 90% of the quality lives, not in the code.
