"""
Parse the exact lyrics of '100 Ways To Love A Cat Ways 1-100' and generate
synchronized timestamped karaoke data matching the 35:21 (2120.8s) 125 BPM audio file.
"""
import os
import re
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Raw lyrics provided by user
RAW_LYRICS = """
[Verse 1]
There are one hundred ways to love a cat
One hundred loving ways
Way one: keep a tidy house for them
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way two: Be sure to clip their claws
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way three: scoop their box daily
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way four: brush them with a hairbrush
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 2]
There are one hundred ways to love a cat
One hundred loving ways
Way five: don't squeeze their paws hard
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way six: give them some fresh water
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way seven: let them have a fish
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way eight: buy them a scratching post
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 3]
There are one hundred ways to love a cat
One hundred loving ways
Way nine: put them in your lap
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way ten: be quiet when they're sleeping
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way eleven: whisper "I love you"
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way twelve: rub their soft belly
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 4]
There are one hundred ways to love a cat
One hundred loving ways
Way thirteen: make sure their tail is clean
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way fourteen: give them a yarn ball
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way fifteen: make them a nice bed
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way sixteen: buy him some catnip
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 5]
There are one hundred ways to love a cat
One hundred loving ways
Way seventeen: play them some music
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way eighteen: get them a cute collar
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way nineteen: make sure they're vaccinated
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way twenty: take their picture
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 6]
There are one hundred ways to love a cat
One hundred loving ways
Way twenty-one: brush their teeth
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way twenty-two: let them watch T.V
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way twenty-three: don't let them be outside by themselves
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way twenty-four: feed them some cat food
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 7]
There are one hundred ways to love a cat
One hundred loving ways
Way twenty-five: make sure their eyes are clean
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way twenty-six: put a liner in their box
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way twenty-seven: give them a mat to wipe their feet on
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way twenty-eight: don't forget them on Christmas
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 8]
There are one hundred ways to love a cat
One hundred loving ways
Way twenty-nine: make sure they're spayed or neutered
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way thirty: hold them like a baby
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way thirty-one: let them have a towel or blanket
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way thirty-two: keep your toilet lid down
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 9]
There are one hundred ways to love a cat
One hundred loving ways
Way thirty-three: don't let them chew on power cords
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way thirty-four: set them by the window
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way thirty-five: cat-proof your home
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way thirty-six: change their litter weekly
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 10]
There are one hundred ways to love a cat
One hundred loving ways
Way thirty-seven: praise them lavishly
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way thirty-eight: never feed him chicken bones
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way thirty-nine: teach them a funny trick
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way forty: give them a toy mouse
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 11]
There are one hundred ways to love a cat
One hundred loving ways
Way forty-one: clean up their hairballs
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way forty-two: keep them away from candles
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way forty-three: give him a separate zone
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way forty-four: never play with them aggressively
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 12]
There are one hundred ways to love a cat
One hundred loving ways
Way forty-five: increase his cuddle time
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way forty-six: be sure to watch his weight
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way forty-seven: if you leave, turn on the radio
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way forty-eight: scold him firmly but with kindness
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 13]
There are one hundred ways to love a cat
One hundred loving ways
Way forty-nine: respond when he meows *meow*
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way fifty: give them a thing of cat grass
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way fifty-one: scratch under his chin
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way fifty-two: remind him that you love him
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 14]
There are one hundred ways to love a cat
One hundred loving ways
Way fifty-three: give them a box to play in
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way fifty-four: if they're old, help them get down
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way fifty-five: let them lick you with their rough tongue
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way fifty-six: record precious memories
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 15]
There are one hundred ways to love a cat
One hundred loving ways
Way fifty-seven: dress them up in ribbons
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way fifty-eight: give them a flea treatment
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way fifty-nine: make a vet appointment
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way sixty: give them a little wet food
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 16]
There are one hundred ways to love a cat
One hundred loving ways
Way sixty-one: when they scratch you, don't get angry
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way sixty-two: give them some private time
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way sixty-three: treat them with respect
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way sixty-four: when he grooms himself, say "good job"
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 17]
There are one hundred ways to love a cat
One hundred loving ways
Way sixty-five: let them chase a laser pointer
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way sixty-six: clean out their ears
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way sixty-seven: never smoke around them
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way sixty-eight: buy a sturdy cat carrier
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 18]
There are one hundred ways to love a cat
One hundred loving ways
Way sixty-nine: listen to them purr
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way seventy: Dentabite Temptations
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way seventy-one: give them your full attention
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way seven-two: don't trap them in the laundry basket
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 19]
There are one hundred ways to love a cat
One hundred loving ways
Way seventy-three: let them sleep in bed with you
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way seventy-four: make sure they're not locked in the closet
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way seventy-five: don't let them play in plastic bags
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way seventy-six: give them a massage
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 20]
There are one hundred ways to love a cat
One hundred loving ways
Way seventy-seven: touch him as you pass by
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way seventy-eight: if he's on the couch, don't be mad
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way seventy-nine: if they hate fans, turn the fan off
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way eighty: when there's a bird outside, say "hey, look!"
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 21]
There are one hundred ways to love a cat
One hundred loving ways
Way eighty-one: intrigue them with a funny sound *honk*
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way eighty-two: don't forget sardine time
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way eighty-three: let him play with your old socks
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way eighty-four: stroke in the direction that his fur goes
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 22]
There are one hundred ways to love a cat
One hundred loving ways
Way eighty-five: admire his long whiskers
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way eighty-six: keep his box away from his food
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way eighty-seven: pretend that he's a piano
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way eighty-eight: don't interrupt them while they're eating
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 23]
There are one hundred ways to love a cat
One hundred loving ways
Way eighty-nine: when they're scared, go and comfort them
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way ninety: let him have a lick
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way ninety-one: if their breath stinks, give them Greenies
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way ninety-two: give him a ball with a bell in it
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 24]
There are one hundred ways to love a cat
One hundred loving ways
Way ninety-three: if it's hot, put ice in their bowl
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way ninety-four: let him drink out of the sink
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way ninety-five: don't vacuum if it scares him
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way ninety-six: draw a picture of him
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways

[Verse 25]
There are one hundred ways to love a cat
One hundred loving ways
Way ninety-seven: if you drop some food, it's theirs now
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way ninety-eight: read him a book
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way ninety-nine: feed him again
One hundred loving ways
There are one hundred ways to love a cat
One hundred loving ways
Way one hundred: just love them, every day
One hundred loving ways
[Chorus]
One hundred loving ways
One hundred loving ways
One hundred loving ways
One hundred loving ways
"""

def parse_and_timestamp_lyrics():
    # 125 BPM -> 0.48s per beat, 1.92s per 4-beat bar
    # Audio starts with ~3.84s guitar intro (2 bars).
    # Then Verse 1 begins at t = 3.84s.
    # Total duration = 2120.78s across 25 verses + chorus blocks.
    # Average block duration = (2120.78 - 3.84 - 15.0) / 25 = ~84.08 seconds per verse block.
    # Within each block:
    # 4 ways: each way takes 15.36s (8 bars)
    # 4 * 15.36s = 61.44s
    # Chorus: 4 lines of "One hundred loving ways" = 8 bars = 15.36s
    # Turnaround/fill = 4 bars = 7.68s
    # Total = 61.44 + 15.36 + 7.68 = 84.48s per verse block!

    INT_OFFSET = 3.84  # Guitar intro
    WAY_DURATION = 15.36 # 8 bars per way
    CHORUS_DURATION = 15.36 # 8 bars chorus
    FILL_DURATION = 7.68 # 4 bars turnaround
    BLOCK_DURATION = (4 * WAY_DURATION) + CHORUS_DURATION + FILL_DURATION  # 84.48s

    ways_data = []
    lines = RAW_LYRICS.strip().split("\n")
    
    current_verse = 1
    way_pattern = re.compile(r"^Way\s+([a-zA-Z\-\s0-9]+?):\s*(.*)$", re.IGNORECASE)

    current_ways_in_verse = []
    for line in lines:
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("["):
            if "Verse" in line_clean:
                m_v = re.search(r"Verse\s+(\d+)", line_clean)
                if m_v:
                    current_verse = int(m_v.group(1))
            continue
        
        m_way = way_pattern.match(line_clean)
        if m_way:
            num_word, action = m_way.groups()
            way_num = len(ways_data) + 1
            
            # Calculate timestamps
            verse_idx = (way_num - 1) // 4
            way_in_verse = (way_num - 1) % 4

            start_t = INT_OFFSET + (verse_idx * BLOCK_DURATION) + (way_in_verse * WAY_DURATION)
            end_t = start_t + WAY_DURATION

            item = {
                "way_number": way_num,
                "verse_index": verse_idx + 1,
                "way_word": num_word,
                "action": action,
                "display_lyric": f"Way {way_num}: {action}",
                "full_line": line_clean,
                "start_seconds": round(start_t, 2),
                "end_seconds": round(end_t, 2),
                "action_start_seconds": round(start_t + 7.68, 2), # "Way X..." begins at bar 5
            }
            ways_data.append(item)

    print(f"Parsed {len(ways_data)} ways to love a cat.")
    print("Sample Way 1:", ways_data[0])
    print("Sample Way 50:", ways_data[49])
    print("Sample Way 100:", ways_data[99])

    out_path = os.path.join(PROJECT_ROOT, "data", "cat_karaoke_lyrics.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(ways_data, f, indent=2)

    print(f"Saved synchronized karaoke lyrics to {out_path}")
    return ways_data

if __name__ == "__main__":
    parse_and_timestamp_lyrics()
