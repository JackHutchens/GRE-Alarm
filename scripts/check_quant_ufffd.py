import json

with open("data/gre_questions.json", encoding="utf-8") as f:
    questions = json.load(f)

quant = [q for q in questions if q.get("section") == "Quantitative Reasoning"]
print(f"Total Quant: {len(quant)}")

has_ufffd = 0
for q in quant:
    qtext = q.get("question", "")
    exp = q.get("explanation", "") or ""
    opt_texts = [o.get("text", "") for o in q.get("options", [])]
    all_str = qtext + " " + exp + " " + " ".join(opt_texts)
    if "\ufffd" in all_str:
        has_ufffd += 1

print(f"Quant questions with \\ufffd: {has_ufffd}")

# Check what topics or categories these quant questions have
topics = {}
for q in quant:
    top = q.get("topic", "Unknown")
    topics[top] = topics.get(top, 0) + 1
print("Quant topics:", topics)
