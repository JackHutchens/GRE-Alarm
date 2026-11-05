"""
Deep forensic auditor to find every poorly-designed, garbled, or incomplete question.
"""
import os
import re
import json

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(project_root, "data", "gre_questions.json")

with open(data_path, "r", encoding="utf-8") as f:
    questions = json.load(f)

print(f"Loaded {len(questions)} questions")

flagged = []

for q in questions:
    qid = q["id"]
    qtext = q.get("question", "")
    exp = q.get("explanation", "") or ""
    opts = q.get("options", [])
    opt_texts = [o.get("text", "") for o in opts]
    
    # 1. Missing words like "gets of what" or "sum of is"
    if re.search(r"\bgets\s+of\b", qtext) or re.search(r"\bequal to\s+of\b", qtext):
        flagged.append((qid, "Missing fraction words (e.g. 'gets of what')", qtext))
        continue

    # 2. Options with space-separated numbers that should be fractions (e.g. "1 7", "5 1 4", "7 2")
    if any(re.match(r"^\d+\s+\d+$", t.strip()) or re.match(r"^\d+\s+\d+\s+\d+$", t.strip()) for t in opt_texts):
        flagged.append((qid, f"Scrambled fraction options: {opt_texts}", qtext))
        continue

    # 3. Unbalanced parens in formulas (e.g. "(469 + 174^2 - (469 - 174^2")
    # Count parens in math-like expressions
    if qtext.count("(") != qtext.count(")"):
        # Check if it's verbal like (i) or quant formula
        # In verbal: (i), (ii), (iii)
        verbal_parens = len(re.findall(r"\([iIvVxX]+\)", qtext))
        remaining_left = qtext.count("(") - verbal_parens
        remaining_right = qtext.count(")") - verbal_parens
        if remaining_left != remaining_right and q.get("section") == "Quantitative Reasoning":
            flagged.append((qid, f"Unbalanced parentheses in math ({remaining_left} vs {remaining_right})", qtext))
            continue

    # 4. Scrambled exponents/fractions like "a x - 1 = b x - 3", "x ^ b ( b + c - a )", "x = 3 + 2 2"
    if any(p in qtext for p in ["a x - 1 = b x - 3", "x ^ b ( b + c - a )", "3 + 2 2", "243)^ n /5"]):
        flagged.append((qid, "Scrambled scraped formula", qtext))
        continue

    # 5. Replacement char or division symbol lost
    if "\ufffd" in qtext or any("\ufffd" in t for t in opt_texts):
        flagged.append((qid, "Corrupted replacement char in question/options", qtext))
        continue

    # 6. Options text containing raw '?' or empty
    if any(t.strip() in ["?", ""] for t in opt_texts):
        flagged.append((qid, f"Empty or question-mark option: {opt_texts}", qtext))
        continue

print(f"Total flagged questions: {len(flagged)}")
for qid, reason, qtxt in flagged:
    print(f"\n[{qid}] {reason}")
    print(f"  {qtxt[:100]}")
