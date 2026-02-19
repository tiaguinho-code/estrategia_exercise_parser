import json
import genanki
import hashlib
from pathlib import Path

INPUT_JSON = "aula15.json"
OUTPUT_APKG = "portuguese_orthography.apkg"

def format_html(text: str) -> str:
    """Convert plain text with newlines into Anki-safe HTML."""
    if not text:
        return ""
    # Normalize newlines and strip trailing spaces
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    # Split paragraphs and join with <br>
    parts = [p.strip() for p in text.split("\n") if p.strip()]
    return "<br>".join(parts)


def stable_id(text: str) -> int:
    """Generate stable numeric ID from text (for Anki)."""
    return int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16)

# Load JSON
data = json.loads(Path(INPUT_JSON).read_text(encoding="utf-8"))

# Define Anki model (note type)
model = genanki.Model(
    1607392319,
    "Orthography QA",
    fields=[
        {"name": "Question"},
        {"name": "Commentary"},
        {"name": "Answer"},
        {"name": "Meta"},
        {"name": "ID"},
        {"name": "Number"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": """
<div style="font-size:20px; white-space: pre-wrap;">{{Question}}</div>
""",
"afmt": """
{{FrontSide}}
<hr>
<div style="font-size:18px; white-space: pre-wrap;">{{Commentary}}</div>
<br>
<div style="color:gray;font-size:14px">
<b>Answer:</b> {{Answer}}<br>
<b>Meta:</b> {{Meta}}<br>
<b>ID:</b> {{ID}} | <b>#:</b> {{Number}}
</div>
""",
        }
    ],
)

deck = genanki.Deck(
    2059400110,
    "Portuguese Orthography",
)

notes_added = 0

for item in data:
    question_raw = (item.get("question") or "").strip()
    commentary_raw = (item.get("commentary") or "").strip()

    # Skip empty cards
    if not question_raw or not commentary_raw:
        continue

    question = format_html(question_raw)
    commentary = format_html(commentary_raw)
    meta = format_html((item.get("meta") or "").strip())
    answer = format_html((item.get("answer") or "").strip())

    note = genanki.Note(
        model=model,
        fields=[
            question,
            commentary,
            answer,
            meta,
            (item.get("id") or "").strip(),
            str(item.get("number") or ""),
        ],
        guid=str(stable_id(question_raw + commentary_raw)),
    )

    deck.add_note(note)
    notes_added += 1

print(f"Added {notes_added} cards")

genanki.Package(deck).write_to_file(OUTPUT_APKG)
print(f"Deck exported to {OUTPUT_APKG}")
