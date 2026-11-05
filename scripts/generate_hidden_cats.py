"""
Generate 100 hidden cat features (cutesy vs spooky) with exact CSS classes,
SVGs/emojis, tooltips, screen placement coordinates, and appearance order.
Rule: Ways 1-15 can ONLY receive cutesy features. Ways 16-100 receive a mix.
"""
import json
import random

random.seed(42) # Deterministic shuffle

cutesy_templates = [
    ("Sleepy Tabby", "cutesy", "🐾 A tiny striped kitten curling up comfortably on the header bar.", "🐱", "top-left-perim"),
    ("Pink Jellybean Paw", "cutesy", "🐾 Soft pink kitten toe-beans peeking from the screen edge.", "🐾", "left-perim"),
    ("Twitching Calico Tail", "cutesy", "🐾 A playful calico tail swishing back and forth beneath the timer.", "🐈", "timer-accent"),
    ("Pastel Cat Ears", "cutesy", "🐾 Fuzzy pastel feline ears popping up above the quiz card.", "🐱", "card-top"),
    ("Little Rolling Yarn Ball", "cutesy", "🐾 A cozy ball of soft blue yarn rolling slowly across the panel.", "🧶", "bottom-left"),
    ("Warm Milk Saucer", "cutesy", "🐾 A ceramic saucer with warm milk placed beside the score bar.", "🥛", "score-accent"),
    ("Gentle Purr Pulse", "cutesy", "🐾 Soft pulsating green aura representing a cat purring at 25 Hz.", "💚", "status-pulse"),
    ("Playful Scratching Post", "cutesy", "🐾 A tiny sisal scratching post standing beside the disarm button.", "🪵", "button-side"),
    ("Whisker Watermark", "cutesy", "🐾 Delicate white whiskers subtly etched into the question card.", "ᗢ", "card-bg"),
    ("Pouncing Ginger Kitten", "cutesy", "🐾 An energetic ginger kitten playfully crouching for a jump.", "🐈", "right-perim"),
    ("Fishbone Snack Token", "cutesy", "🐾 A miniature cartoon fishbone treat resting on the difficulty tag.", "🐟", "tag-accent"),
    ("Cat Loaf Formation", "cutesy", "🐾 A perfectly tucked loafed cat resting quietly on the margin.", "🍞", "right-shelf"),
    ("Napping Tuxedo", "cutesy", "🐾 A dapper black-and-white kitten snoozing atop the digital clock.", "😺", "clock-roof"),
    ("Friendly Nose Boop", "cutesy", "🐾 A sweet pink nose looking for a gentle finger boop.", "🐽", "corner-float"),
    ("Feather Wand Toy", "cutesy", "🐾 A colorful feather teaser dangling from the upper right corner.", "🪶", "top-right"),
    ("Curled Sleeping Kitten", "cutesy", "🐾 Sound asleep, dreaming of tuna and warm laundry.", "💤", "panel-corner"),
    ("Blinking Golden Eyes", "cutesy", "🐾 Friendly, curious round golden eyes watching your GRE progress.", "👀", "quiz-side"),
    ("Stretching Mitted Cat", "cutesy", "🐾 Big morning stretch showing off white mitten paws.", "🐈", "bottom-bar"),
    ("Happy Biscuit Maker", "cutesy", "🐾 Kneading an invisible blanket with rhythmic affection.", "🐾", "clock-side"),
    ("Chonky Fluffball", "cutesy", "🐾 An extremely fluffy round cat floating softly in ambient space.", "☁", "float-cloud"),
    ("Silver Bell Collar", "cutesy", "🐾 A shiny silver bell that tinkles softly when you submit answers.", "🔔", "submit-accent"),
    ("Catnip Leaf Charm", "cutesy", "🐾 A fragrant organic catnip leaf fluttering in the corner.", "🌿", "left-shelf"),
    ("Mischievous Peekaboo", "cutesy", "🐾 Two paws and big round eyes peeking over the answer feedback box.", "😸", "feedback-top"),
    ("Cardboard Box Haven", "cutesy", "🐾 If it fits, it sits: a small cozy brown cardboard box.", "📦", "right-bottom"),
    ("Sunbeam Basking Cat", "cutesy", "🐾 Soaking up artificial screen photons with pure bliss.", "☀️", "center-top"),
    ("Teeny Mitten Tracks", "cutesy", "🐾 A neat trail of miniature footprints walking across the header.", "🐾", "header-walk"),
    ("Headbutt of Love", "cutesy", "🐾 A firm, loving feline forehead rub wishing you ETS success.", "😻", "nav-side"),
    ("Gentle Kneading Paws", "cutesy", "🐾 Rhythmically pressing into the card background.", "🐾", "card-knead"),
    ("Silly Tongue Blep", "cutesy", "🐾 A tiny pink tongue sticking out in pure derpiness.", "👅", "badge-side"),
    ("Tiny Paper Bag Scout", "cutesy", "🐾 Rustling around happily in a miniature paper grocery bag.", "🛍️", "bottom-drift"),
    ("Yarn String Trail", "cutesy", "🐾 A delicate pink string connecting the timer to the score counter.", "🧵", "timer-line"),
    ("Purring Soundwave", "cutesy", "🐾 Visual harmonic ripples of a content 10 lb domestic companion.", "〰️", "ambient-wave"),
    ("Gentle Tail Wrap", "cutesy", "🐾 A furry tail gently wrapped around the question number badge.", "➰", "qnum-tail"),
    ("Kitten Chirp Glyph", "cutesy", "🐾 An affectionate musical trill rendered as floating notes.", "🎶", "sound-note"),
    ("Tucked Paws Monorail", "cutesy", "🐾 Laying flat like a monorail along the bottom edge of the banner.", "🚝", "banner-rail"),
    ("Soft Chin Scratch Spot", "cutesy", "🐾 An inviting little indicator for chin scritches.", "✨", "chin-spot"),
    ("Mouse Toy on String", "cutesy", "🐾 A plush grey mouse bobbing gently on an elastic cord.", "🐁", "mouse-toy"),
    ("Golden Fur Watermark", "cutesy", "🐾 Subtle warm feline silhouette glowing beneath the reading passage.", "✨", "passage-watermark"),
    ("Perched Window Watcher", "cutesy", "🐾 Looking intently at bird simulations outside the browser viewport.", "🪟", "window-perch"),
    ("Playful Paw Swat", "cutesy", "🐾 Swatting at your cursor when you move too close to the options.", "🐾", "swat-zone"),
    ("Cozy Heated Pad", "cutesy", "🐾 Glowing gently warm under the 100-point victory marker.", "♨️", "score-pad"),
    ("Cuddly Spooning Pair", "cutesy", "🐾 Two yin-yang kittens napping in synchronous bliss.", "☯️", "yin-yang"),
    ("Butterflies & Paws", "cutesy", "🐾 A pastel butterfly chased by a tiny tuxedo kitten.", "🦋", "butterfly-chase"),
    ("Milk Mustache Badge", "cutesy", "🐾 A proud white milk ring around a happy little muzzle.", "🥛", "muzzle-badge"),
    ("Feline High-Five", "cutesy", "🐾 Raised paw offering congratulations on correct GRE logic.", "✋", "high-five"),
    ("Snuggly Blanket Cocoon", "cutesy", "🐾 Completely burrowed into a fleece blanket fortress.", "🛋️", "cocoon-corner"),
    ("Playful Bunny Kicks", "cutesy", "🐾 Rapid-fire hind leg kicks clutching a toy carrot.", "🥕", "bunny-kicks"),
    ("Whisker Twitch Radar", "cutesy", "🐾 Sensitive radar whiskers sensing multiple choice traps.", "📡", "radar-whiskers"),
    ("Happy Elevator Butt", "cutesy", "🐾 Involuntary reflex when scritched right above the tail base.", "🐈", "elevator-butt"),
    ("Feline Guardian Angel", "cutesy", "🐾 A haloed kitten blessing your Verbal Reasoning percentiles.", "😇", "guardian-angel")
]

spooky_templates = [
    ("Crimson Slit Stare", "spooky", "⚠️ Unblinking crimson feline slit pupils burning out of the void.", "👁️", "dark-corner-1"),
    ("Glass Gouge Scratches", "spooky", "⚠️ Three jagged razor claw marks slicing through the UI panel.", "⚡", "panel-gouge-1"),
    ("The Elongated Shadow", "spooky", "⚠️ An unnaturally stretched feline silhouette lurking along the bottom.", "👤", "floor-shadow"),
    ("Hollow Socket Watcher", "spooky", "⚠️ Empty abyssal eye sockets tracking your mouse coordinates.", "💀", "abyss-watcher"),
    ("Glitch Static Feline", "spooky", "⚠️ Distorted CRT scanline cat glitching across the background.", "📺", "screen-glitch"),
    ("Cheshire Void Grin", "spooky", "⚠️ A floating disembodied crescent grin hovering in the upper darkness.", "🦷", "floating-grin"),
    ("Bloodied Paw Trail", "spooky", "⚠️ Dark red feline pawprints tracking directly toward your answers.", "🐾", "crimson-track"),
    ("Eldritch Whispering Fur", "spooky", "⚠️ 'THE FELINE NEVER SLEEPS... WHY SHOULD YOU?'", "🩸", "whisper-text-1"),
    ("Skeletal Lynx Totem", "spooky", "⚠️ Weathered feline bone skull etched into the backdrop grid.", "☠️", "skull-etch"),
    ("Eight-Legged Shadow Cat", "spooky", "⚠️ A multi-limbed arachnid-feline phantom clinging to the left wall.", "🕷️", "wall-stalker"),
    ("Unsettling Hyper-Realistic Eye", "spooky", "⚠️ A biological feline eye with microscopic veins staring intently.", "👁️", "bio-eye"),
    ("Claw Gouges on Timer", "spooky", "⚠️ Deep serrated gashes torn through the 5-minute countdown clock.", "🔪", "timer-gash"),
    ("Translucent Phantom Paws", "spooky", "⚠️ Ghostly pale claws slowly reaching around the viewport frame.", "👻", "edge-reach"),
    ("Cursed Hieroglyph of Bastet", "spooky", "⚠️ An ancient occult talisman pulsing with dark violet luminescence.", "🔮", "occult-talisman"),
    ("Demonic Low Purr Glyph", "spooky", "⚠️ Infrasonic 18 Hz vibration rippling the UI elements.", "〰️", "infra-ripple"),
    ("Inverted Shadow Feline", "spooky", "⚠️ A silhouette crawling upside-down along the top navigation bar.", "🕷️", "top-invert"),
    ("Predator Stalk Stance", "spooky", "⚠️ Crouched motionless on the reading passage, waiting for you to fail.", "🐆", "passage-stalk"),
    ("Dripping Pitch Silhouette", "spooky", "⚠️ Black tar-like darkness dripping slowly from feline claws.", "💧", "pitch-drip"),
    ("The Grinning Feral", "spooky", "⚠️ Sharp predatory fangs gleaming behind the submit button.", "🦷", "submit-fangs"),
    ("Curse of the Broken Clock", "spooky", "⚠️ Ghostly claw frozen on the digital seconds counter.", "⌛", "clock-curse"),
    ("Feline Specter of Insomnia", "spooky", "⚠️ A pale apparition that appears only when exhaustion peaks.", "🌫️", "insomnia-specter"),
    ("Sub-Auditory Hiss Sigil", "spooky", "⚠️ Silent venomous feline snarl frozen in the stylesheet.", "🐍", "snarl-sigil"),
    ("Looming Feral Shadow", "spooky", "⚠️ A massive panzer-sized cat shadow cast against the screen background.", "🌑", "looming-shadow"),
    ("The Screeching Wraith", "spooky", "⚠️ Distorted acoustic waveform of a nocturnal territory dispute.", "🔊", "screech-wave"),
    ("Eldritch Whiskers of Rot", "spooky", "⚠️ Tendrils of black smoke curling from the difficulty badge.", "💨", "smoke-whiskers"),
    ("Gouged Option Box", "spooky", "⚠️ Choice D has been scratched into near illegibility by frantic claws.", "❌", "choice-gouge"),
    ("Bleeding Screen Corner", "spooky", "⚠️ Subtle crimson tint spreading from the top-left viewport corner.", "🩸", "bleed-corner"),
    ("Nightmare Kitten Jaw", "spooky", "⚠️ Far too many rows of needle-sharp teeth.", "🦷", "needle-teeth"),
    ("Watcher in the Status Pill", "spooky", "⚠️ Two tiny yellow slit eyes blinking inside the status indicator.", "👁️", "status-eye"),
    ("The Nine Dead Lives", "spooky", "⚠️ Nine tally marks carved into the score display border.", "卌", "tally-marks"),
    ("The Phantom Meow Whisper", "spooky", "⚠️ 'You missed the Text Completion blank...'", "💬", "whisper-tc"),
    ("Shadow Paws Clamping Score", "spooky", "⚠️ Claws digging deep into your accumulated points total.", "🐾", "score-clamp"),
    ("The Void Jumper", "spooky", "⚠️ Fleeting blur darting across the periphery when you look away.", "⚡", "peripheral-blur"),
    ("Cursed Catnip Curse", "spooky", "⚠️ Black withered leaves emitting a sickly purple miasma.", "🍂", "purple-miasma"),
    ("Gazing from the Deep RAM", "spooky", "⚠️ Memory address 0xDEADBEEF stares back with feline malice.", "💾", "ram-stare"),
    ("The Slit-Pupil Eclipse", "spooky", "⚠️ The circular disarm button turns into a massive yellow pupil.", "🟡", "pupil-eclipse"),
    ("Scratch Code Injection", "spooky", "⚠️ Corrupted HTML tags clawed into the question explanation.", "👾", "glitch-code"),
    ("The Flayed Yarn Ball", "spooky", "⚠️ Made of unraveling biological nerve fibers.", "🧶", "nerve-yarn"),
    ("Crouching Chimera", "spooky", "⚠️ Feline body with predatory reptilian scales glistening in dark mode.", "🦎", "chimera-crouch"),
    ("Hissing Terminal Cursor", "spooky", "⚠️ The text caret barks an aggressive warning hiss.", "⚡", "cursor-hiss"),
    ("The Night Terror Prowler", "spooky", "⚠️ Wandering between your sleeping consciousness and wakefulness.", "🌌", "prowler-night"),
    ("Bloody Milk Bowl", "spooky", "⚠️ The milk saucer is overflowing with crimson rust.", "🥣", "bloody-bowl"),
    ("Predator Heat Signature", "spooky", "⚠️ Thermal infrared cat silhouette locking onto your skull.", "🌡️", "thermal-cat"),
    ("Warped Feline Spine", "spooky", "⚠️ Impossibly contorted silhouette twisting behind the timer bar.", "🦴", "warped-spine"),
    ("The Screaming Calico", "spooky", "⚠️ Soundless open-mouthed terror mask frozen in amber CSS.", "🙀", "scream-calico"),
    ("Curse of the 100th Way", "spooky", "⚠️ 'Love them... or they will claim your waking soul.'", "📜", "curse-scroll"),
    ("Razor Whiskers", "spooky", "⚠️ Chrome metallic barbs that shred careless taps.", "🪒", "razor-barbs"),
    ("Feline Necromancer", "spooky", "⚠️ Raising previous incorrect answers back from the dead.", "🧙", "necromancer-cat"),
    ("The Eternal Watcher", "spooky", "⚠️ Never blinks. Never sleeps. Always tallies your score.", "👁️", "eternal-watcher"),
    ("Abyssal Claws of ETS", "spooky", "⚠️ Giant spectral feline talons holding your GRE percentile hostage.", "🦅", "ets-talons")
]

# Guarantee:
# Ways 1 to 15: strictly cutesy features (first 15 items in manifest)
cutesy_shuffled = cutesy_templates.copy()
random.shuffle(cutesy_shuffled)

first_15 = cutesy_shuffled[:15]
remaining_cutesy = cutesy_shuffled[15:]

# Remaining 85 slots: 35 cutesy + 50 spooky
remaining_pool = remaining_cutesy + spooky_templates
random.shuffle(remaining_pool)

manifest_100 = first_15 + remaining_pool

features_json = []
for idx, (name, cat_type, desc, icon, loc) in enumerate(manifest_100):
    features_json.append({
        "way_unlock": idx + 1,
        "name": name,
        "type": cat_type,
        "description": desc,
        "icon": icon,
        "location": loc
    })

out_file = r"data/hidden_cat_features.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(features_json, f, indent=2)

print(f"Generated {len(features_json)} hidden cat features in {out_file}")
cutesy_first_15 = [f["type"] for f in features_json[:15]]
print("First 15 types:", cutesy_first_15)
assert all(t == "cutesy" for t in cutesy_first_15), "ERROR: First 15 must be 100% cutesy!"
spooky_after_15 = [f["type"] for f in features_json[15:] if f["type"] == "spooky"]
print(f"Spooky features after Way 15: {len(spooky_after_15)}")
