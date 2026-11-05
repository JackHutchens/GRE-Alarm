import json
import re

with open("data/gre_questions.json", encoding="utf-8") as f:
    questions = json.load(f)

quant = [q for q in questions if q.get("section") == "Quantitative Reasoning"]

prune_candidates = []
for q in quant:
    qtext = q.get("question", "").strip()
    exp = (q.get("explanation") or "").strip()
    
    # 1. Pure multiplication drills of large integers
    if re.search(r"^\(?\d+\s*[xX*]\s*\d+\)?\s*=\s*\?", qtext):
        prune_candidates.append((q["id"], "Trivial large multiplication drill", qtext))
    # 2. Garbled expressions
    elif "?" in qtext and ("1 + a ^(" in qtext or "1 + 1 = ?" in qtext):
        prune_candidates.append((q["id"], "Garbled formula typesetting", qtext))
    # 3. Missing or meaningless options
    elif any(o.get("text", "").strip() in ["?", "None of these", ""] for o in q.get("options", [])) and len(q.get("options", [])) < 4:
        prune_candidates.append((q["id"], "Inadequate options", qtext))

print(f"Total quant prune candidates: {len(prune_candidates)}")
for item in prune_candidates:
    print(" ", item[0], "|", item[1], "|", item[2][:70])
