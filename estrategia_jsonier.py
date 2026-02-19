import pdfplumber
import re
import json

# ==============================
# CONFIG
# ==============================

PDF_PATH = "aula15_short.pdf"
OUTPUT_FILE = "aula15.json"

DEBUG = False        # <-- change to False to export everything
DEBUG_LIMIT = 100    # number of exercises when DEBUG=True

# ==============================
# STEP 1 - Extract full text
# ==============================

def extract_text_from_pdf(path):
    full_text = ""

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lines = text.split("\n")

            # Remove top 3 lines (header)
            lines = lines[3:] if len(lines) > 3 else lines

            # Remove bottom 3 lines (footer)
            lines = lines[:-3] if len(lines) > 3 else lines

            page_text = "\n".join(lines)

            full_text += page_text + "\n"

    return full_text


# ==============================
# STEP 2 - Parse Exercises
# ==============================

from collections import Counter
import re

def clean_text(text):
    lines = text.split("\n")

    # Count repeated lines (headers/footers usually repeat a lot)
    line_counts = Counter(lines)

    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            continue

        # Remove repeated lines (likely header/footer)
        if line_counts[line] > 3:
            continue

        # Remove website lines
        if "www." in stripped:
            continue

        # Remove pure page numbers
        if re.fullmatch(r"\d+", stripped):
            continue

        # Remove lines with only numbers and spaces
        if re.fullmatch(r"[\d\s]+", stripped):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def parse_exercises(text):
    exercises = []

    parts = re.split(r"\n\s*(\d+)\.\s*", text)

    counter = 1

    for i in range(1, len(parts), 2):
        number = int(parts[i])
        content = parts[i+1]

        if DEBUG and counter > DEBUG_LIMIT:
            break

        # Extract meta
        meta_match = re.search(r"\((.*?)\)", content)
        meta = meta_match.group(1).strip() if meta_match else ""

        content_clean = content.replace(f"({meta})", "").strip()

        # --------------------------
        # EXTRACT ANSWER FIRST
        # --------------------------

        answer = ""

        match1 = re.search(r"Gabarito:\s*(Correto|Errado)", content_clean, re.IGNORECASE)
        match2 = re.search(r"Gabarito\s*(?:letra|Letra)\s*([A-E])", content_clean)

        if match1:
            answer = match1.group(1).capitalize()
        elif match2:
            answer = match2.group(1).upper()

        # --------------------------
        # SPLIT QUESTION / COMMENTARY
        # --------------------------

        # Try explicit split first
        split_comment = re.split(r"Coment[aá]rios?:", content_clean, maxsplit=1)

        if len(split_comment) > 1:
            question_part = split_comment[0].strip()
            commentary_part = split_comment[1].strip()
        else:
            # Fallback: split at first Gabarito occurrence
            gabarito_pos = content_clean.find("Gabarito")
            if gabarito_pos != -1:
                before_gabarito = content_clean[:gabarito_pos].strip()
            else:
                before_gabarito = content_clean

            # Heuristic: find last alternative (A) ... E)
            alt_matches = list(re.finditer(r"\n[A-E]\)", before_gabarito))

            if alt_matches:
                last_alt = alt_matches[-1]
                split_pos = last_alt.end()
                question_part = before_gabarito[:split_pos].strip()
                commentary_part = before_gabarito[split_pos:].strip()
            else:
                question_part = before_gabarito
                commentary_part = ""

        # ==========================
        # EDGE CASE FIXES
        # ==========================

        # 1️⃣ Detect "Questão correta/errada"
        if not answer:
            qc_match = re.search(r"Quest[aã]o\s+(correta|errada)", content_clean, re.IGNORECASE)
            if qc_match:
                word = qc_match.group(1).lower()
                answer = "Correto" if "corret" in word else "Errado"

                # Treat entire block as commentary except first line
                lines = content_clean.split("\n")
                if len(lines) > 1:
                    question_part = lines[0].strip()
                    commentary_part = "\n".join(lines[1:]).strip()

        # 2️⃣ If commentary empty but answer exists → copy answer
        if answer and not commentary_part.strip():
            commentary_part = answer

        # 3️⃣ Certo/Errado heuristic split
        # If no alternatives and commentary empty but multiple sentences
        if not commentary_part:
            alt_exists = re.search(r"\n[A-E]\)", question_part)

            if not alt_exists:
                sentences = re.split(r"(?<=\.)\s+", question_part)
                if len(sentences) > 1:
                    question_part = sentences[0].strip()
                    commentary_part = " ".join(sentences[1:]).strip()


        exercise = {
            "id": f"15-ort-{counter:03}",
            "number": number,
            "meta": meta,
            "question": question_part,
            "commentary": commentary_part,
            "answer": answer
        }

        exercises.append(exercise)
        counter += 1

    return exercises
    exercises = []

    text = clean_text(text)

    parts = re.split(r"\n\s*(\d+)\.\s*", text)

    counter = 1

    for i in range(1, len(parts), 2):
        number = int(parts[i])
        content = parts[i+1]

        if DEBUG and counter > DEBUG_LIMIT:
            break

        # Extract meta
        meta_match = re.search(r"\((.*?)\)", content)
        meta = meta_match.group(1).strip() if meta_match else ""

        # Split question from commentary
        split_comment = re.split(r"Coment[aá]rio[s]?:", content, maxsplit=1)

        question_part = split_comment[0]
        commentary_part = split_comment[1] if len(split_comment) > 1 else ""

        question = question_part.replace(f"({meta})", "").strip()

        # ==========================
        # ANSWER EXTRACTION
        # ==========================

        answer = ""
        
        # Pattern 1: Gabarito: Correto / Errado
        match1 = re.search(r"Gabarito:\s*(Correto|Errado)", commentary_part, re.IGNORECASE)
        
        # Pattern 2: Gabarito letra C / Gabarito Letra C
        match2 = re.search(r"Gabarito\s*(?:letra|Letra)\s*([A-E])", commentary_part)
        
        if match1:
            answer = match1.group(1).capitalize()
        elif match2:
            answer = match2.group(1).upper()

        exercise = {
            "id": f"15-ort-{counter:03}",
            "number": number,
            "meta": meta,
            "question": question,
            "commentary": commentary_part.strip(),
            "answer": answer
        }

        exercises.append(exercise)
        counter += 1

    return exercises

    exercises = []

    # Split by numbered exercises (1. 2. 3. etc)
    parts = re.split(r"\n\s*(\d+)\.\s*", text)

    # parts structure:
    # ["", "1", "exercise text", "2", "exercise text", ...]

    counter = 1

    for i in range(1, len(parts), 2):
        number = int(parts[i])
        content = parts[i+1]

        # Stop early if DEBUG
        if DEBUG and counter > DEBUG_LIMIT:
            break

        # Extract meta (text inside first parentheses)
        meta_match = re.search(r"\((.*?)\)", content)
        meta = meta_match.group(1).strip() if meta_match else ""

        # Split question and commentary
        split_comment = content.split("Comentários:")
        question_part = split_comment[0]
        commentary_part = split_comment[1] if len(split_comment) > 1 else ""

        # Clean question (remove meta)
        question = question_part.replace(f"({meta})", "").strip()

        # Extract answer
        answer_match = re.search(r"Gabarito:\s*([A-Za-zçÇ]+)", commentary_part)
        answer = answer_match.group(1).strip() if answer_match else ""

        exercise = {
            "id": f"15-ort-{counter:03}",
            "number": number,
            "meta": meta,
            "question": question,
            "commentary": commentary_part.strip(),
            "answer": answer
        }

        exercises.append(exercise)
        counter += 1

    return exercises


# ==============================
# MAIN
# ==============================

def main():
    print("Extracting text from PDF...")
    text = extract_text_from_pdf(PDF_PATH)

    print("Parsing exercises...")
    exercises = parse_exercises(text)

    print(f"Saving {len(exercises)} exercises to JSON...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(exercises, f, ensure_ascii=False, indent=2)

    print("Done.")


if __name__ == "__main__":
    main()
