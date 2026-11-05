"""
Finalize, Prune, and Format Question Database with LaTeX Math.

Performs:
1. Pruning of all flawed/unsolvable/poorly-designed questions.
2. Conversion of mathematical equations in questions, options, and explanations to LaTeX.
3. Parsing and normalizing multi-select Reading Comprehension answers.
4. Unicode character sanitation.
5. Re-calculation of calibrated points and penalties.
"""

import os
import re
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_BACKUP_PATH = os.path.join(PROJECT_ROOT, "data", "gre_questions_raw_backup.json")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "gre_questions.json")

# Offsets for calibrated scoring formula
DIFF_OFFSET = {"easy": 0, "medium": 4, "hard": 8}
SUBTYPE_OFFSET = {
    "Text Completion (1 Blank)": 0,
    "Sentence Equivalence": 2,
    "Text Completion (2 Blanks)": 4,
    "Problem Solving": 5,
    "Reading Comprehension": 6,
    "Text Completion (3 Blanks)": 8
}

def clean_unicode(text: str) -> str:
    if not text:
        return ""
    s = text
    s = s.replace("\ufffd", "'")
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2014", " — ").replace("\u2013", "–")
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()

def format_quant_math_to_latex(text: str) -> str:
    if not text:
        return ""
    
    t = text.strip()

    # 1. Fractions in options (e.g. '1 2' -> '$\\frac{1}{2}$', '5 1 2' -> '$5\\frac{1}{2}$', '66 2 3' -> '$66\\frac{2}{3}$')
    m_mixed = re.match(r"^(\d+)\s+(\d+)\s+(\d+)(.*)$", t)
    if m_mixed:
        w, n, d, rest = m_mixed.groups()
        return f"${w}\\frac{{{n}}}{{{d}}}${rest}"
    
    m_simple = re.match(r"^(\d+)\s+(\d+)(.*)$", t)
    if m_simple:
        n, d, rest = m_simple.groups()
        return f"$\\frac{{{n}}}{{{d}}}${rest}"

    # 2. Specific known question cleanups
    if "(6374)" in t and "(625)" in t:
        return "What is the units digit in $(6374^{1793} \\times 625^{317} \\times 341^{491})$?"
    
    if "(2^32 + 1)" in t:
        return "It is given that $(2^{32} + 1)$ is completely divisible by a whole number. Which of the following numbers is completely divisible by this number?"

    if "(112 x 5^4)" in t or "(112 x (5)^4)" in t:
        return "What is the value of $(112 \\times 5^4)$?"

    if "(0.04)^-1.5" in t:
        return "Evaluate $(0.04)^{-1.5}$."

    if "12^3 x 6^4" in t:
        return "Evaluate $\\frac{12^3 \\times 6^4}{432}$."

    # 3. Exponents: e.g. 2^32 -> $2^{32}$, 5^a -> $5^a$, 3^(x-y) -> $3^{x-y}$
    t = re.sub(r'\(?([0-9\.]+)\)?\^(-?[0-9\.]+)', r'$(\1)^{\2}$', t)
    t = re.sub(r'([a-zA-Z0-9]+)\^\(([^\)]+)\)', r'$\1^{\2}$', t)
    t = re.sub(r'([a-zA-Z0-9]+)\^([a-zA-Z0-9]+)', r'$\1^{\2}$', t)

    # 4. Roots: sqrt(...) -> $\sqrt{...}$
    t = re.sub(r'sqrt\(([^\)]+)\)', r'$\\sqrt{\1}$', t)

    # 5. Products between numbers: e.g. 5358 x 51 -> $5358 \times 51$
    t = re.sub(r'(\d+)\s*[xX]\s*(\d+)', r'$\1 \\times \2$', t)

    # 6. Area units: m^2 -> $\text{m}^2$
    t = re.sub(r'\b([0-9]+)\s*m\^2\b', r'$\1\\text{ m}^2$', t)
    t = re.sub(r'\$m\^\{2\}\$', r'$\\text{m}^2$', t)

    # 7. Inequalities
    t = re.sub(r'<=', r'$\\le$', t)
    t = re.sub(r'>=', r'$\\ge$', t)
    t = re.sub(r'!=', r'$\\neq$', t)

    # 8. Clean redundant nested/adjacent math delimiters
    t = re.sub(r'\$\$+', r'$', t)
    t = re.sub(r'\$\s*([\+\-\*/=])\s*\$', r' \1 ', t)

    return t

def finalize_database():
    source_file = RAW_BACKUP_PATH if os.path.exists(RAW_BACKUP_PATH) else OUTPUT_PATH
    with open(source_file, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Total raw questions in input: {len(questions)}")

    # Unsolvable or corrupted IDs to prune
    prune_ids = {
        "gre_0623",  # Mismatched 2-blank key ['A', 'F', 'H']
        "gre_1113",  # 1397 x 1397 = ? (arithmetic drill)
        "gre_1115",  # 935421 x 625 = ? (arithmetic drill)
        "gre_1119",  # 5358 x 51 = ? (arithmetic drill)
        "gre_1123",  # 72519 x 9999 = ? (arithmetic drill)
        "gre_1322",  # Garbled scraped formula
        "gre_1326",  # Garbled scraped formula
        "gre_1159",  # Missing fraction words ('If of A amount...')
        "gre_1335",  # Missing fraction words ('A gets of what...')
        "gre_1316",  # Scrambled fraction line
        "gre_1325",  # Scrambled formula
        "gre_1328",  # Scrambled formula
        "gre_1329",  # Scrambled formula
        "gre_1343",  # Unbalanced brackets formula
    }

    pruned = []
    final_questions = []

    for q in questions:
        qid = q["id"]

        if qid in prune_ids:
            pruned.append((qid, "Flawed/unsolvable/drill question"))
            continue

        subtype = q.get("subtype", "")
        options = q.get("options", [])
        raw_ans = q.get("correct_answer", [])

        # Fix Reading Comprehension condensed answer strings
        if subtype == "Reading Comprehension":
            new_ans = []
            for a in raw_ans:
                a_str = str(a).strip().upper()
                if a_str in ["ABC", "A B C", "A,B,C", "A, B, C"]:
                    new_ans.extend(["A", "B", "C"])
                elif a_str in ["AB", "A B", "A,B", "A, B"]:
                    new_ans.extend(["A", "B"])
                elif a_str in ["AC", "A C", "A,C", "A, C"]:
                    new_ans.extend(["A", "C"])
                elif a_str in ["BC", "B C", "B,C", "B, C"]:
                    new_ans.extend(["B", "C"])
                else:
                    new_ans.append(a_str)
            raw_ans = sorted(list(set(new_ans)))
            q["correct_answer"] = raw_ans

        # Check options labels vs answer labels
        opt_labels = {o.get("label") for o in options if o.get("label")}
        missing_labels = [a for a in raw_ans if a not in opt_labels]
        if missing_labels:
            pruned.append((qid, f"Missing answer labels {missing_labels} from options"))
            continue

        # Check options count
        if len(options) < 2:
            pruned.append((qid, "Fewer than 2 options"))
            continue

        # Clean unicode
        q["question"] = clean_unicode(q.get("question", ""))
        if q.get("passage"):
            q["passage"] = clean_unicode(q["passage"])
        if q.get("explanation"):
            q["explanation"] = clean_unicode(q["explanation"])

        # Format Quant math to LaTeX
        if q.get("section") == "Quantitative Reasoning":
            q["question"] = format_quant_math_to_latex(q["question"])
            if q.get("explanation"):
                q["explanation"] = format_quant_math_to_latex(q["explanation"])

        for opt in q.get("options", []):
            opt["text"] = clean_unicode(opt.get("text", ""))
            if q.get("section") == "Quantitative Reasoning":
                opt["text"] = format_quant_math_to_latex(opt["text"])

        # Recalculate calibrated points & penalties
        t_est = q.get("estimated_time_seconds", 90)
        diff_val = DIFF_OFFSET.get(q.get("difficulty", "medium"), 4)
        subtype_val = SUBTYPE_OFFSET.get(subtype, 3)
        pts = int(round(12 + 0.12 * t_est + diff_val + subtype_val))
        penalty = int(round(pts / 2.0))

        q["point_value"] = pts
        q["penalty_value"] = penalty

        final_questions.append(q)

    print(f"\nFinal count of verified questions: {len(final_questions)}")
    print(f"Total pruned questions: {len(pruned)}")

    # Breakdown by subtype
    subtypes = {}
    sections = {}
    for q in final_questions:
        st = q.get("subtype")
        subtypes[st] = subtypes.get(st, 0) + 1
        sec = q.get("section")
        sections[sec] = sections.get(sec, 0) + 1

    print("\nVerified Questions by Subtype:")
    for st, count in sorted(subtypes.items()):
        print(f"  {st:32}: {count}")

    print("\nVerified Questions by Section:")
    for sec, count in sorted(sections.items()):
        print(f"  {sec:32}: {count}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(final_questions, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Saved clean, LaTeX-formatted dataset to {OUTPUT_PATH}")
    return final_questions

if __name__ == "__main__":
    finalize_database()
