import json

with open("data/gre_questions.json", encoding="utf-8") as f:
    questions = json.load(f)

se_missing_f = []
se_valid = []

for q in questions:
    if q.get("subtype") == "Sentence Equivalence":
        labels = [o.get("label") for o in q.get("options", [])]
        ans = q.get("correct_answer", [])
        if len(labels) == 6 and set(labels) == {"A", "B", "C", "D", "E", "F"}:
            se_valid.append(q)
        else:
            se_missing_f.append((q["id"], labels, ans))

print(f"Total SE questions: {len(se_valid) + len(se_missing_f)}")
print(f"SE with all 6 options (A-F): {len(se_valid)}")
print(f"SE with missing option (e.g. 5 options): {len(se_missing_f)}")
print("\nSamples of missing option SE:")
for item in se_missing_f[:5]:
    print(" ", item)
