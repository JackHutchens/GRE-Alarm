"""
Bundle web/ files into a standalone Generative UI artifact.
"""
import os
import json

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
art_dir = r"C:\Users\jacka\.gemini\antigravity\brain\ae759fcb-adde-4ada-a1a8-c7f9b73b75ae"

with open(os.path.join(project_root, "web", "index.html"), "r", encoding="utf-8") as f:
    html = f.read()

with open(os.path.join(project_root, "web", "styles.css"), "r", encoding="utf-8") as f:
    css = f.read()

with open(os.path.join(project_root, "web", "app.js"), "r", encoding="utf-8") as f:
    js = f.read()

# Load 500 messages & 100 cat ways to inline into artifact for 100% offline standalone usage
with open(os.path.join(project_root, "data", "shut_up_messages.json"), "r", encoding="utf-8") as f:
    messages_data = json.load(f)

with open(os.path.join(project_root, "data", "cat_ways.json"), "r", encoding="utf-8") as f:
    cat_ways_data = json.load(f)

with open(os.path.join(project_root, "data", "cat_karaoke_lyrics.json"), "r", encoding="utf-8") as f:
    cat_karaoke_data = json.load(f)

with open(os.path.join(project_root, "data", "hidden_cat_features.json"), "r", encoding="utf-8") as f:
    hidden_cats_data = json.load(f)

# Load a balanced sample of 250 questions across all subtypes to inline for offline standalone usage
with open(os.path.join(project_root, "data", "gre_questions.json"), "r", encoding="utf-8") as f:
    all_questions = json.load(f)

# Pick balanced samples
from collections import defaultdict
by_sub = defaultdict(list)
for q in all_questions:
    by_sub[q.get("subtype")].append(q)

sample_questions = []
for sub, qlist in by_sub.items():
    sample_questions.extend(qlist[:45])  # ~45 per subtype = ~270 balanced questions

inline_payload = f"""
<script>
window.BUNDLED_SHUT_UP_MESSAGES = {json.dumps(messages_data)};
window.BUNDLED_CAT_WAYS = {json.dumps(cat_ways_data)};
window.BUNDLED_CAT_KARAOKE = {json.dumps(cat_karaoke_data)};
window.BUNDLED_HIDDEN_CATS = {json.dumps(hidden_cats_data)};
window.BUNDLED_GRE_QUESTIONS = {json.dumps(sample_questions)};
</script>
"""

# Enhance app.js to use window.BUNDLED_GRE_QUESTIONS if fetch fails
js_enhanced = js.replace(
    'const fallbackQ = {',
    'if (window.BUNDLED_GRE_QUESTIONS && window.BUNDLED_GRE_QUESTIONS.length > 0) {\n'
    '      const pool = window.BUNDLED_GRE_QUESTIONS;\n'
    '      const picked = pool[Math.floor(Math.random() * pool.length)];\n'
    '      const t = picked.estimated_time_seconds || 90;\n'
    '      const d = picked.difficulty === "hard" ? 8 : (picked.difficulty === "easy" ? 0 : 4);\n'
    '      const pts = Math.round(12 + 0.12 * t + d + 4);\n'
    '      picked.point_value = pts;\n'
    '      picked.penalty_value = Math.round(pts / 2);\n'
    '      STATE.currentQuestion = picked;\n'
    '      renderQuestion(picked);\n'
    '      return;\n'
    '    }\n'
    '    const fallbackQ = {'
)

# Inline CSS & JS
import urllib.parse
with open(os.path.join(project_root, "web", "favicon.svg"), "r", encoding="utf-8") as f:
    fav_svg = f.read()
fav_data_uri = f"data:image/svg+xml,{urllib.parse.quote(fav_svg)}"

html_bundled = html.replace('<link rel="icon" type="image/svg+xml" href="./favicon.svg">', f'<link rel="icon" type="image/svg+xml" href="{fav_data_uri}">')
html_bundled = html_bundled.replace('<link rel="stylesheet" href="./styles.css">', f'<style>\n{css}\n</style>')
html_bundled = html_bundled.replace('<script src="./app.js"></script>', f'{inline_payload}\n<script>\n{js_enhanced}\n</script>')

# Also write favicon.svg to artifact directory
with open(os.path.join(art_dir, "favicon.svg"), "w", encoding="utf-8") as f:
    f.write(fav_svg)

out_path = os.path.join(art_dir, "gre_alarm_prototype.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html_bundled)

print(f"Artifact created at {out_path} ({len(html_bundled):,} bytes)")
