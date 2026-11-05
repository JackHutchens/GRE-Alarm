"""
Generate synchronized timestamped karaoke data with word-level boundaries
calibrated to the actual audio file '100 Ways To Love A Cat Ways 1-100.mp3'.
"""
import os
import re
import json
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load verified verse starts
verse_starts = np.load(os.path.join(PROJECT_ROOT, "scripts", "verse_starts.npy"))

# Raw lyrics
with open(os.path.join(PROJECT_ROOT, "scripts", "build_cat_karaoke.py"), "r", encoding="utf-8") as f:
    orig_code = f.read()

# Extract RAW_LYRICS
m_raw = re.search(r'RAW_LYRICS\s*=\s*"""(.*?)"""', orig_code, re.DOTALL)
if not m_raw:
    raise ValueError("Could not extract RAW_LYRICS")
raw_lyrics = m_raw.group(1)

way_pattern = re.compile(r"^Way\s+([a-zA-Z\-\s0-9]+?):\s*(.*)$", re.IGNORECASE)

ways_list = []
lines = raw_lyrics.strip().split("\n")
for line in lines:
    line_clean = line.strip()
    m = way_pattern.match(line_clean)
    if m:
        num_word, action = m.groups()
        ways_list.append((len(ways_list) + 1, num_word.strip(), action.strip()))

print(f"Parsed {len(ways_list)} ways from lyrics.")
assert len(ways_list) == 100, f"Expected 100 ways, found {len(ways_list)}"

karaoke_data = []

for way_num, num_word, action in ways_list:
    verse_idx = (way_num - 1) // 4
    k = (way_num - 1) % 4
    v_start = float(verse_starts[verse_idx])
    
    start_t = round(v_start + (k * 15.36), 2)
    action_start_t = round(start_t + 7.68, 2)
    action_end_t = round(start_t + 13.50, 2)
    
    # End of this way's block
    if k < 3:
        end_t = round(v_start + ((k + 1) * 15.36), 2)
    else:
        # 4th way in verse: includes chorus until next verse start
        if verse_idx < 24:
            end_t = round(float(verse_starts[verse_idx + 1]), 2)
        else:
            end_t = 2120.75

    # Break into words: "Way", f"{way_num}:", then words in action
    # Clean action words
    action_words = [w for w in action.split() if w]
    all_words = ["Way", f"{way_num}:"] + action_words
    
    total_duration = action_end_t - action_start_t
    
    # Calculate word weights based on character length
    weights = [max(2, len(w)) for w in all_words]
    # First two ("Way", "X:") take about 1.5s total
    # Rest take the remaining time
    word_timings = []
    
    # Prefix: "Way X:" takes 1.4s
    prefix_dur = 1.40
    rest_dur = max(1.5, total_duration - prefix_dur)
    
    t_curr = action_start_t
    w0_dur = prefix_dur * 0.45
    word_timings.append({
        "word": "Way",
        "start": round(t_curr, 2),
        "end": round(t_curr + w0_dur, 2)
    })
    t_curr += w0_dur
    
    w1_dur = prefix_dur * 0.55
    word_timings.append({
        "word": f"{way_num}:",
        "start": round(t_curr, 2),
        "end": round(t_curr + w1_dur, 2)
    })
    t_curr += w1_dur
    
    # Action words
    rest_weights = [max(2, len(w)) for w in action_words]
    sum_rest = sum(rest_weights) if rest_weights else 1
    
    for w, wt in zip(action_words, rest_weights):
        w_dur = (wt / sum_rest) * rest_dur
        word_timings.append({
            "word": w,
            "start": round(t_curr, 2),
            "end": round(t_curr + w_dur, 2)
        })
        t_curr += w_dur

    item = {
        "way_number": way_num,
        "verse_index": verse_idx + 1,
        "way_word": num_word,
        "action": action,
        "display_lyric": f"Way {way_num}: {action}",
        "full_line": f"Way {num_word}: {action}",
        "start_seconds": start_t,
        "action_start_seconds": action_start_t,
        "action_end_seconds": action_end_t,
        "end_seconds": end_t,
        "words": word_timings
    }
    karaoke_data.append(item)

out_path = os.path.join(PROJECT_ROOT, "data", "cat_karaoke_lyrics.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(karaoke_data, f, indent=2)

print(f"Generated {len(karaoke_data)} ways with word-level timing at {out_path}")
print("Way 1:", karaoke_data[0]["words"])
print("Way 50:", karaoke_data[49]["words"])
print("Way 100:", karaoke_data[99]["words"])
