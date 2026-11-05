import json

with open("data/gre_questions.json", encoding="utf-8") as f:
    questions = json.load(f)

for q in questions:
    labels = {o.get("label") for o in q.get("options", [])}
    ans = q.get("correct_answer", [])
    missing = [a for a in ans if a not in labels]
    if missing and q.get("subtype") in ["Reading Comprehension", "Text Completion (2 Blanks)"]:
        print(f"=== ID: {q['id']} ({q.get('subtype')}) ===")
        print("Question:", q["question"][:120])
        print("Options:", [(o.get("label"), o.get("text", "")[:30]) for o in q["options"]])
        print("Answer:", q["correct_answer"])
        print("Missing from options:", missing)
        print()
