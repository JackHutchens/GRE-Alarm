import json

with open("data/hidden_cat_features.json", "r", encoding="utf-8") as f:
    features = json.load(f)

for i in range(0, 100, 10):
    print(f"=== Items {i+1} to {min(100, i+10)} ===")
    for f in features[i:i+10]:
        print(f"#{f['way_unlock']} [{f['type']}]: {f['name']} - {f['description']}")
