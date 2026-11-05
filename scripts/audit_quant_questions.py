import json
import re

with open("data/gre_questions.json", encoding="utf-8") as f:
    questions = json.load(f)

quant = [q for q in questions if q.get("section") == "Quantitative Reasoning"]
print(f"Total Quant questions: {len(quant)}")

# Categorize Quant questions
arithmetic_drills = []
corrupted_char_questions = []
good_quant = []

drill_patterns = [
    r"^\(?\d+\s*[xX*]\s*\d+\)?\s*=\s*\?",
    r"^\(?\d+\s*[\+\-]\s*\d+\)?\s*=\s*\?",
    r"^\(?\d+\^?\d*\s*[xX*]\s*\d+\^?\d*\s*=\s*\?",
    r"\d+\s*x\s*\d+\s*=\s*\?"
]

for q in quant:
    qtext = q.get("question", "").strip()
    is_drill = any(re.search(pat, qtext) for pat in drill_patterns)
    has_corrupt = "" in qtext or any("" in o.get("text", "") for o in q.get("options", []))
    
    if is_drill:
        arithmetic_drills.append(q)
    elif has_corrupt:
        corrupted_char_questions.append(q)
    else:
        good_quant.append(q)

print(f"Trivial arithmetic drills (e.g. '1397 x 1397 = ?'): {len(arithmetic_drills)}")
for q in arithmetic_drills[:5]:
    print("  Drill:", q["id"], q["question"])

print(f"\nCorrupted character quant questions: {len(corrupted_char_questions)}")
for q in corrupted_char_questions[:5]:
    print("  Corrupt:", q["id"], repr(q["question"]))

print(f"\nLegitimate reasoning quant questions: {len(good_quant)}")
for q in good_quant[:5]:
    print("  Good:", q["id"], q["question"][:80])
