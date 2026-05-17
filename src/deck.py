import hashlib
import genanki

MODEL_ID = 1872934401

MODEL = genanki.Model(
    MODEL_ID,
    "Interview Phrase",
    fields=[
        {"name": "Example Sentence"},
        {"name": "Target Expression"},
        {"name": "Definition"},
        {"name": "Audio"},
        {"name": "Picture"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": '<div class=sentence>{{Example Sentence}}</div>',
            "afmt": (
                '<div class=sentence>{{Example Sentence}}</div>'
                '<hr>'
                '<div class=definition> <b>{{Target Expression}}:</b> {{Definition}}</div>'
                '{{Audio}}'
                '{{#Picture}}'
                '<br>'
                '<div class="main_image">{{Picture}}</div>'
                '{{/Picture}}'
            ),
        }
    ],
    css=(
        ".card {\n"
        "font-size: 23px;\n"
        "text-align: left;\n"
        "color: black;\n"
        "background-color: #FFFAF0;\n"
        "font-family: Times New Roman;\n"
        "}\n\n"
        ".sentence {\n"
        "font-size: 30px;\n"
        "}\n\n"
        ".definition {\n"
        "font-size: 23px;\n"
        "}\n\n"
        "img {\n"
        "width: auto;\n"
        "height: auto;\n"
        "max-width: 900px;\n"
        "max-height: 450px;\n"
        "}\n"
    ),
)


def _deck_id_for(name: str) -> int:
    # genanki wants a stable int. Hash the deck name into a 31-bit positive int.
    h = hashlib.md5(name.encode("utf-8")).digest()
    return int.from_bytes(h[:4], "big") & 0x7FFFFFFF


def build_deck(cards: list[dict], out_path: str, deck_name: str = "English::phrases::interview"):
    deck = genanki.Deck(_deck_id_for(deck_name), deck_name)
    media_files = []

    for c in cards:
        audio_tag = f"[sound:{c['audio_file']}]" if c.get("audio_file") else ""
        note = genanki.Note(
            model=MODEL,
            fields=[
                c["example_sentence"],
                c["target_expression"],
                c["definition"],
                audio_tag,
                "",
            ],
            guid=genanki.guid_for(c["target_expression"], c["example_sentence"]),
        )
        deck.add_note(note)
        if c.get("audio_file"):
            media_files.append(f"media/{c['audio_file']}")

    pkg = genanki.Package(deck)
    pkg.media_files = list(set(media_files))
    pkg.write_to_file(out_path)
