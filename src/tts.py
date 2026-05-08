import hashlib
import os
from pathlib import Path
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "nPczCjzI2devNBz1zQrb")
MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")

MEDIA_DIR = Path("media")
MEDIA_DIR.mkdir(exist_ok=True)


def _filename(text: str) -> str:
    h = hashlib.md5(f"{VOICE_ID}:{text}".encode("utf-8")).hexdigest()[:12]
    return f"el_{h}.mp3"


def synthesize(text: str) -> str:
    """Return mp3 filename in media/. Cached on disk so reruns are free."""
    fname = _filename(text)
    path = MEDIA_DIR / fname
    if path.exists():
        return fname

    audio = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        model_id=MODEL,
        text=text,
        output_format="mp3_44100_128",
        voice_settings={
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.15,
            "use_speaker_boost": True,
        },
    )
    with open(path, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    return fname
