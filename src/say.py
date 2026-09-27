import argparse
from dotenv import load_dotenv

load_dotenv()

from src.tts import synthesize, MEDIA_DIR


def main():
    parser = argparse.ArgumentParser(description="Synthesize a single sentence to mp3 via ElevenLabs.")
    parser.add_argument("text", help="The sentence to synthesize.")
    args = parser.parse_args()

    fname = synthesize(args.text)
    print(MEDIA_DIR / fname)


if __name__ == "__main__":
    main()
