import json
import genanki
import hashlib
from pathlib import Path

INPUT_JSON = "aula15.json"
OUTPUT_APKG = "portuguese_orthography.apkg"

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
<div style="font-size:20px">{{Question}}</div>
""",
            "afmt": """
{{FrontSide}}
<hr>
<div style="font-size:18px">{{Commentary}}</div>
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
    question = (item.get("question") or "").strip()
    commentary = (item.get("commentary") or "").strip()

    # Skip empty cards
    if not question or not commentary:
        continue

    note = genanki.Note(
        model=model,
        fields=[
            question,
            commentary,
            (item.get("answer") or "").strip(),
            (item.get("meta") or "").strip(),
            (item.get("id") or "").strip(),
            str(item.get("number") or ""),
        ],
        guid=str(stable_id(question + commentary)),
    )

    deck.add_note(note)
    notes_added += 1

print(f"Added {notes_added} cards")

genanki.Package(deck).write_to_file(OUTPUT_APKG)
print(f"Deck exported to {OUTPUT_APKG}")
