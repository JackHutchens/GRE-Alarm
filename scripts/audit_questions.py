"""
Comprehensive question audit script.
Scans all 1,344 questions for:
1. Missing or invalid fields
2. Unsolvable questions (e.g. references to missing figures/diagrams)
3. Quality/coherence of text, options, answers, and explanations
4. Identification of math equations and formatting in questions, options, and explanations
"""
import os
import re
import json

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(project_root, "data", "gre_questions.json")

with open(data_path, "r", encoding="utf-8") as f:
    questions = json.load(f)

print(f"Total questions loaded: {len(questions)}")

# Categorize questions
by_section = {}
for q in questions:
    sec = q.get("section", "Unknown")
    by_section[sec] = by_section.get(sec, 0) + 1
print("By section:", by_section)

# 1. Check for missing diagram/figure references
figure_patterns = [
    r"\bfigure\b", r"\bdiagram\b", r"\bgraph above\b", r"\bchart above\b",
    r"\bshown above\b", r"\bshown below\b", r"\brefer to the figure\b",
    r"\bin the triangle above\b", r"\bin the circle above\b", r"\bshaded region\b"
]

questions_with_figure_ref = []
for q in questions:
    text = (q.get("question") or "") + " " + (q.get("passage") or "")
    text_lower = text.lower()
    for pat in figure_patterns:
        if re.search(pat, text_lower):
            questions_with_figure_ref.append((q["id"], q.get("section"), q.get("subtype"), text[:120], pat))
            break

print(f"\nQuestions mentioning figures/diagrams: {len(questions_with_figure_ref)}")
for qid, sec, sub, txt, pat in questions_with_figure_ref[:10]:
    print(f"  [{qid}] ({sec} / {sub}) Pattern '{pat}': {txt}...")

# 2. Check options validity
invalid_options = []
for q in questions:
    opts = q.get("options")
    if not opts or not isinstance(opts, list) or len(opts) < 2:
        invalid_options.append((q["id"], "Too few options"))
        continue
    # Check if options have text
    for opt in opts:
        if not opt.get("text") or not opt.get("label"):
            invalid_options.append((q["id"], f"Blank option: {opt}"))
            break
print(f"\nQuestions with invalid options: {len(invalid_options)}")

# 3. Check correct_answer validity
invalid_answers = []
for q in questions:
    ans = q.get("correct_answer")
    opts = q.get("options", [])
    labels = {o.get("label") for o in opts}
    if not ans or not isinstance(ans, list):
        invalid_answers.append((q["id"], "No answer list"))
        continue
    # Check if answer labels exist in options
    for a in ans:
        if a not in labels:
            invalid_answers.append((q["id"], f"Answer label '{a}' not in options {labels}"))
            break
print(f"Questions with invalid answer labels: {len(invalid_answers)}")
for item in invalid_answers[:5]:
    print("  ", item)

# 4. Check for truncated or nonsensical questions
truncated_questions = []
for q in questions:
    txt = (q.get("question") or "").strip()
    if len(txt) < 20:
        truncated_questions.append((q["id"], "Too short (<20 chars)", txt))
    elif txt.endswith("...") and len(txt) < 50:
        truncated_questions.append((q["id"], "Ellipsis cutoff", txt))
print(f"\nTruncated questions: {len(truncated_questions)}")
for item in truncated_questions:
    print("  ", item)

# 5. Check Quantitative Reasoning math expressions
quant_questions = [q for q in questions if q.get("section") == "Quantitative Reasoning"]
print(f"\nTotal Quant questions: {len(quant_questions)}")
sample_math = []
for q in quant_questions[:15]:
    sample_math.append((q["id"], q["question"], [o["text"] for o in q["options"]]))

print("\n--- SAMPLE QUANT QUESTIONS ---")
for qid, qtext, qopts in sample_math:
    print(f"\n[{qid}] {qtext}")
    print(f"  Options: {qopts}")
