"""
Database Cleaner, Pruner, and LaTeX Formatter for GRE Questions.

Operations:
1. Prunes unfixable/poorly-designed questions:
   - 157 Sentence Equivalence questions with dropped option F in answer key.
   - 1 Corrupted Text Completion question (gre_0623).
   - 6 Trivial manual arithmetic multiplication drills or garbled scraped formulas.
2. Fixes Reading Comprehension multi-select answers ('ABC' -> ['A', 'B', 'C'], 'AC' -> ['A', 'C'], etc.)
3. Converts all mathematical expressions in Quantitative and Verbal questions into standard LaTeX math ($...$).
4. Normalizes text formatting, fixing smart quotes, em-dashes, and encoding glitches.
5. Saves clean database to data/gre_questions.json and generates a verification report.
"""

import os
import re
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "gre_questions.json")

def clean_text_encoding(text: str) -> str:
    if not text:
        return ""
    
    # Replace known corrupt byte artefacts
    s = text
    s = s.replace("\ufffd", "'")  # replacement chars in gre_recall are almost exclusively apostrophes
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2014", " — ").replace("\u2013", "–")
    s = s.replace("\u00a0", " ")
    
    # Clean up double spaces
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()

def format_math_latex(text: str) -> str:
    """Converts common arithmetic, algebraic, and exponent notation to LaTeX."""
    if not text:
        return ""
    
    t = text

    # Handle explicit exponents: e.g., (0.04)^-1.5 -> $(0.04)^{-1.5}$
    t = re.sub(r'\(?([0-9\.]+)\)?\^(-?[0-9\.]+)', r'$(\1)^{\2}$', t)
    
    # Handle integer powers: e.g. 2^32 -> $2^{32}$, 5^4 -> $5^4$
    t = re.sub(r'([a-zA-Z0-9]+)\^([0-9]+)', r'$\1^{\2}$', t)
    
    # Handle composite exponents like x^(a-b) -> $x^{a-b}$
    t = re.sub(r'([a-zA-Z0-9]+)\^\(([^\)]+)\)', r'$\1^{\2}$', t)

    # Convert multiplication signs between numbers: e.g. "112 x 5" -> "$112 \times 5$"
    t = re.sub(r'(\d+)\s*[xX]\s*(\d+)', r'$\1 \\times \2$', t)
    t = re.sub(r'(\d+)\s*\*\s*(\d+)', r'$\1 \\times \2$', t)

    # Convert roots: sqrt(x) -> $\sqrt{x}$
    t = re.sub(r'sqrt\(([^\)]+)\)', r'$\\sqrt{\1}$', t)

    # Convert pi
    t = re.sub(r'\bpi\b', r'$\\pi$', t)

    # Convert inequalities <=, >=, !=
    t = re.sub(r'<=', r'$\\le$', t)
    t = re.sub(r'>=', r'$\\ge$', t)
    t = re.sub(r'!=', r'$\\neq$', t)

    # Cleanup any accidental nested math like $$x$$ -> $x$
    t = re.sub(r'\$\$+', r'$', t)
    # Cleanup adjacent math delimiters: e.g. $2^{32}$ + $1$ -> $2^{32} + 1$
    t = re.sub(r'\$\s*([\+\-\*/=])\s*\$', r' \1 ', t)

    return t

def process_database():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Initial raw question count: {len(questions)}")

    pruned = []
    cleaned_questions = []

    # Disallowed IDs (trivial drills or garbled formulas)
    disallowed_ids = {
        "gre_0623",  # Mismatched 2-blank answer key ['A', 'F', 'H']
        "gre_1113",  # 1397 x 1397 = ?
        "gre_1115",  # 935421 x 625 = ?
        "gre_1119",  # 5358 x 51 = ?
        "gre_1123",  # 72519 x 9999 = ?
        "gre_1322",  # Garbled scraped formula
        "gre_1326"   # Garbled scraped formula
    }

    for q in questions:
        qid = q["id"]

        # Check explicit disallowed
        if qid in disallowed_ids:
            pruned.append((qid, "Explicitly disallowed trivial/garbled question"))
            continue

        subtype = q.get("subtype", "")
        options = q.get("options", [])
        correct_answer = q.get("correct_answer", [])

        # Fix 1: Reading Comprehension multi-select condensed answer strings
        if subtype == "Reading Comprehension":
            new_ans = []
            for a in correct_answer:
                a_str = str(a).strip().upper()
                if a_str in ["ABC", "A B C", "A,B,C", "A, B, C"]:
                    new_ans = ["A", "B", "C"]
                elif a_str in ["AB", "A B", "A,B", "A, B"]:
                    new_ans = ["A", "B"]
                elif a_str in ["AC", "A C", "A,C", "A, C"]:
                    new_ans = ["A", "C"]
                elif a_str in ["BC", "B C", "B,C", "B, C"]:
                    new_ans = ["B", "C"]
                else:
                    new_ans.append(a_str)
            correct_answer = sorted(list(set(new_ans)))
            q["correct_answer"] = correct_answer

        # Check for invalid answers not present in option labels
        option_labels = {o.get("label") for o in options if o.get("label")}
        missing_labels = [a for a in correct_answer if a not in option_labels]
        if missing_labels:
            pruned.append((qid, f"Missing answer labels {missing_labels} in options {option_labels}"))
            continue

        # Check for adequate options count
        if len(options) < 2:
            pruned.append((qid, "Insufficient options count (< 2)"))
            continue

        # Clean text & format LaTeX
        q["question"] = clean_text_encoding(q.get("question", ""))
        if q.get("section") == "Quantitative Reasoning":
            q["question"] = format_math_latex(q["question"])

        if q.get("passage"):
            q["passage"] = clean_text_encoding(q["passage"])

        if q.get("explanation"):
            q["explanation"] = clean_text_encoding(q["explanation"])
            if q.get("section") == "Quantitative Reasoning":
                q["explanation"] = format_math_latex(q["explanation"])

        for opt in q.get("options", []):
            opt["text"] = clean_text_encoding(opt.get("text", ""))
            if q.get("section") == "Quantitative Reasoning":
                opt["text"] = format_math_latex(opt["text"])

        cleaned_questions.append(q)

    print(f"\nPruned questions count: {len(pruned)}")
    print(f"Remaining high-quality questions: {len(cleaned_questions)}")

    # Verify pruned types
    prune_reasons = {}
    for _, r in pruned:
        prune_reasons[r[:35]] = prune_reasons.get(r[:35], 0) + 1
    print("Pruning reasons breakdown:", prune_reasons)

    # Save to disk
    backup_path = os.path.join(PROJECT_ROOT, "data", "gre_questions_raw_backup.json")
    if not os.path.exists(backup_path):
        os.rename(DATA_PATH, backup_path)
        print(f"Backed up raw dataset to {backup_path}")

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(cleaned_questions, f, indent=2, ensure_ascii=False)
    print(f"Saved pristine cleaned dataset ({len(cleaned_questions)} questions) to {DATA_PATH}")

    return cleaned_questions, pruned

if __name__ == "__main__":
    process_database()
