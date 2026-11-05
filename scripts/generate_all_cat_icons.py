"""
Generate 100 hidden feline features where EVERY icon is an unmistakable cat.
Strict Rule: Ways 1-15 can ONLY receive cutesy/tasteful cats.
Ways 16-100 receive a randomized mix of spooky and cutesy cats.
"""
import json
import random

random.seed(100) # Deterministic shuffle

cutesy_cats = [
    ("Sleepy Orange Tabby", "cutesy", "🐾 A cozy ginger tabby kitten curled up taking a 16-hour catnap.", "🐱"),
    ("Calico Loaf Kitten", "cutesy", "🐾 A perfectly tucked calico loaf with paws hidden under warm fur.", "🐈"),
    ("Tuxedo Gentleman Cat", "cutesy", "🐾 A polite black-and-white feline dressed in full formal attire.", "🐱"),
    ("Fluffy White Persian", "cutesy", "🐾 A cloud of soft white fur gazing with regal contentment.", "😺"),
    ("Scottish Fold Mitten", "cutesy", "🐾 Cute folded ears and round curious saucer eyes.", "😸"),
    ("Siamese Blue-Point", "cutesy", "🐾 Elegant cream coat with deep sapphire eyes and dark paws.", "😽"),
    ("Playful Ginger Pouncer", "cutesy", "🐾 Wiggling its hindquarters getting ready for a playful leap.", "🐈"),
    ("Chonky Fluffball Cat", "cutesy", "🐾 An adorable round feline rolling happily on its back.", "😻"),
    ("Biscuit-Maker Tabby", "cutesy", "🐾 Rhythmically kneading an invisible bakery of warm blankets.", "🐱"),
    ("Sunbeam Basking Feline", "cutesy", "🐾 Following the warm patch of sunlight across your screen.", "😺"),
    ("Paper Bag Scout Cat", "cutesy", "🐾 Peeking out of a rustling paper bag with wide playful eyes.", "😸"),
    ("Cardboard Box Lurker", "cutesy", "🐾 If it fits, it sits: reigning supreme in a small delivery box.", "📦🐱"),
    ("Feather-Wand Chaser Cat", "cutesy", "🐾 Eyes dilated tracking an imaginary feather teaser.", "🐱"),
    ("Rolling Yarn Kitten", "cutesy", "🐾 Completely tangled in pink yarn and having the time of its life.", "🧶🐱"),
    ("Warm Milk Sipper Cat", "cutesy", "🐾 Lapping happily at a ceramic saucer with a white milk mustache.", "🥛🐱"),
    ("Purring Lap Warmth Cat", "cutesy", "🐾 Emitting soothing 25 Hz low-frequency healing purrs.", "😻"),
    ("Mitten-Paw Climber", "cutesy", "🐾 Climbing up the panel margin with snowy white paws.", "🐾🐱"),
    ("Chin-Scritch Enthusiast", "cutesy", "🐾 Tilting its chin upward in absolute ecstasy as you hover.", "😽"),
    ("Chirping Bird-Watcher Cat", "cutesy", "🐾 Chattering its teeth at imaginary pigeons outside the window.", "🐱"),
    ("Monorail Balcony Cat", "cutesy", "🐾 Laying completely flat along the top banner like a furry monorail.", "🐈"),
    ("Silly Tongue Blep Kitten", "cutesy", "🐾 Forgot to pull its tiny pink tongue back into its mouth.", "👅🐱"),
    ("High-Five Mitten Cat", "cutesy", "🐾 Reaching out a furry paw offering congratulations on correct logic.", "✋🐱"),
    ("Blanket Fort Burrower", "cutesy", "🐾 Tunneling under the UI styles into a fleece blanket cave.", "🛋️🐱"),
    ("Bunny-Kicking Tigerling", "cutesy", "🐾 Grabbing a plush toy with its front paws and rapid-kicking with hind paws.", "🐱"),
    ("Velvet-Eared Munchkin", "cutesy", "🐾 Short little legs scampering across the header bar with joy.", "🐱"),
    ("Headbutt Affectionate Cat", "cutesy", "🐾 Bumping its forehead gently against your cursor to say 'I love you'.", "😻"),
    ("Silver-Bell Jingle Cat", "cutesy", "🐾 Tinkling a tiny silver collar bell every time you read a line.", "🔔🐱"),
    ("Catnip Dreamer Feline", "cutesy", "🐾 In deep philosophical contemplation after rolling in organic catnip.", "🌿🐱"),
    ("Friendly Nose-Boop Cat", "cutesy", "🐾 Reaching forward with a soft damp pink nose for a boop.", "🐽🐱"),
    ("Soft Muzzle Groomer Cat", "cutesy", "🐾 Thoroughly licking its paws and smoothing down its facial whiskers.", "😸"),
    ("Prowling Alley Tabby", "cutesy", "🐾 Confident domestic ruler surveying its indoor kingdom.", "🐈"),
    ("Coiffed Show-Ring Cat", "cutesy", "🐾 Brushed to perfection with a silk ribbon collar.", "🎀🐱"),
    ("Sleepy Window Hammock Cat", "cutesy", "🐾 Suspended in mid-air in a suction-cup window perch.", "🪟🐱"),
    ("Stretchy Noodle Cat", "cutesy", "🐾 Performing an impossible 36-inch elongated feline morning stretch.", "〰️🐱"),
    ("Happy Elevator-Butt Cat", "cutesy", "🐾 Involuntary rear-elevation reflex triggered by affectionate scritches.", "🐈"),
    ("Curled Cinnamon-Roll Cat", "cutesy", "🐾 Tail tucked over its nose, forming a flawless golden swirl.", "🥐🐱"),
    ("Yin-Yang Spooning Kitten", "cutesy", "🐾 Intertwined with a sibling in harmonious symmetrical sleep.", "☯️🐱"),
    ("Butterfly Stalker Cat", "cutesy", "🐾 Fascinated by a fluttering pastel cursor on the margin.", "🦋🐱"),
    ("Wool-Sock Snuggler Cat", "cutesy", "🐾 Happily cuddling an old wool sock stolen from the laundry hamper.", "🧦🐱"),
    ("Whisker-Twitch Radar Cat", "cutesy", "🐾 Twitched whiskers detecting tricky ETS distractor options.", "📡🐱"),
    ("Gentle Guardian Angel Cat", "cutesy", "🐾 Hovering above your GRE score with tiny white feathered wings.", "😇🐱"),
    ("Squeaky-Meow Sweetheart", "cutesy", "🐾 Opens its mouth wide but only a tiny squeak comes out.", "🎶🐱"),
    ("Soft Belly-Roll Kitten", "cutesy", "🐾 Exposing its soft tummy fur: it's not a trap, it trusts you!", "✨🐱"),
    ("Midnight Mitted Prowler", "cutesy", "🐾 Silent footsteps sneaking past the 5-minute timer.", "🐾🐱"),
    ("Cozy Heated-Pad Cat", "cutesy", "🐾 Melting into a puddle of blissful warmth.", "♨️🐱"),
    ("Sneaky Ankle-Weaver Cat", "cutesy", "🐾 Weaving figure-eights around your ankles as you work.", "🧶🐱"),
    ("Morning Yawn Lioness", "cutesy", "🐾 Displaying all 30 teeth in a magnificent, refreshing yawn.", "🦁"),
    ("Mouse-Toy Victor Cat", "cutesy", "🐾 Proudly parading a catnip mouse trophy around the room.", "🐁🐱"),
    ("Pure Serenity Zen Cat", "cutesy", "🐾 Sitting in meditation, undisturbed by GRE timer stress.", "🧘🐱"),
    ("Curious Mirror Explorer", "cutesy", "🐾 Poking at its own reflection with puzzled fascination.", "🪞🐱")
]

spooky_cats = [
    ("Crimson Slit-Eyed Stalker", "spooky", "⚠️ Unblinking crimson slit pupils staring intently from deep screen shadows.", "👁️🐱"),
    ("The Void Stalker", "spooky", "⚠️ Pure pitch-black feline silhouette absorbing all ambient light.", "🐈‍⬛"),
    ("Cheshire Disembodied Grinner", "spooky", "⚠️ Floating razor-sharp fangs gleaming in the upper darkness.", "🦷🐱"),
    ("Skeletal Lynx Spectre", "spooky", "⚠️ Weathered feline bone skull silently tracking your answer selections.", "💀🐱"),
    ("Eight-Legged Arachnid Cat", "spooky", "⚠️ An unnatural multi-limbed feline phantom scuttling along the wall.", "🕷️🐱"),
    ("Glitch-Static Cyber Cat", "spooky", "⚠️ CRT scanline feline flickering and corrupting stylesheet elements.", "📺🐱"),
    ("Abyssal Shadow Predator", "spooky", "⚠️ An impossibly elongated feline shadow stretching across the bottom.", "👤🐱"),
    ("Hollow-Socketed Watcher Cat", "spooky", "⚠️ Empty black voids where eyes should be, staring directly into your soul.", "🕳️🐱"),
    ("Blood-Clawed Screecher", "spooky", "⚠️ Sharp razor talons glistening with crimson ichor.", "🩸🐱"),
    ("Two-Headed Chimera Cat", "spooky", "⚠️ Twin heads arguing in silent malevolent telepathy.", "👥🐱"),
    ("Feral Spiteful Tom", "spooky", "⚠️ Ears pinned flat, hissing with visceral territory aggression.", "😾"),
    ("Eldritch Tentacle-Furred Cat", "spooky", "⚠️ Tendrils of dark matter writhing beneath its coarse fur.", "🐙🐱"),
    ("Inverted Ceiling Crawler Cat", "spooky", "⚠️ Prowling upside-down across the ceiling directly above you.", "🙃🐱"),
    ("Spectral Ghost Kitten", "spooky", "⚠️ Translucent phantom feline drifting silently through the glass panel.", "👻🐱"),
    ("Unblinking Yellow Basilisk Cat", "spooky", "⚠️ A biological predator stare that paralyzes your concentration.", "🟡🐱"),
    ("Demonic Horned Felid", "spooky", "⚠️ Curved ram horns protruding from obsidian feline fur.", "😈🐱"),
    ("Razor-Fanged Nightmare Cat", "spooky", "⚠️ Too many rows of needle-sharp teeth gleaming behind a cruel grin.", "🦷🐱"),
    ("Weathered Tomb Bastet", "spooky", "⚠️ Ancient cursed stone idol radiating five thousand years of sleep deprivation.", "🏺🐱"),
    ("Dripping Pitch Phantom", "spooky", "⚠️ Black tar-like darkness steadily dripping from extended claws.", "💧🐱"),
    ("Infrasonic Roar Predator", "spooky", "⚠️ Emitting a low 28 Hz guttural growl that vibrates your sternum.", "🐆"),
    ("Night-Terror Prowler Cat", "spooky", "⚠️ Stalking the threshold between your conscious mind and sleep paralysis.", "🌌🐱"),
    ("Needle-Teeth Vampire Feral", "spooky", "⚠️ Elongated canine fangs dripping with dark anticoagulant.", "🧛🐱"),
    ("Cursed Black Cat of Ill Omen", "spooky", "⚠️ Crossed your digital path; subtracts points with a chilling stare.", "🐈‍⬛"),
    ("The Screaming Calico Banshee", "spooky", "⚠️ Soundless open-mouthed terror howl frozen in amber pixels.", "🙀"),
    ("Necromancer Cat of Lost Answers", "spooky", "⚠️ Resurrecting every question you got wrong to haunt your score.", "🧙🐱"),
    ("Flayed-Fur Shadow Cat", "spooky", "⚠️ Crackling with dark static electricity that distorts font rendering.", "⚡🐱"),
    ("Slit-Pupil Eclipse Cat", "spooky", "⚠️ A giant feline eye consuming the circular interface controls.", "🌑🐱"),
    ("Deep RAM Lurker Cat", "spooky", "⚠️ Prowling inside memory address 0xDEADBEEF, corrupting your sleep drive.", "💾🐱"),
    ("Cursed Catnip Revenant", "spooky", "⚠️ Black withered leaves emitting a sickly psychic miasma.", "🍂🐱"),
    ("Bleeding-Whiskers Fiend", "spooky", "⚠️ Razor barbs that slice through hesitant cursor clicks.", "🩸🐱"),
    ("The Peripheral Blur Prowler", "spooky", "⚠️ Only visible when looking away; darts into cover when you gaze directly.", "💨🐱"),
    ("Screeching Alley Phantom", "spooky", "⚠️ Acoustic ghost of a 3 AM alleyway territory scream.", "🔊🐱"),
    ("Ancient Mummy Feline", "spooky", "⚠️ Linen bandages trailing as it claws through centuries of tomb dust.", "📜🐱"),
    ("Venomous Spitting Manul", "spooky", "⚠️ Flat-faced mountain predator spitting auditory venom.", "🐍🐱"),
    ("Warped Spine Contortionist Cat", "spooky", "⚠️ Impossibly bent feline spine slithering through the DOM hierarchy.", "🦴🐱"),
    ("Phantom Meow Whispering Cat", "spooky", "⚠️ Whispering: 'The five minute timer has expired... you belong to us now.'", "💬🐱"),
    ("Bloody-Paw Track Stalker", "spooky", "⚠️ Leaving glowing crimson pawprints directly across your problem.", "🐾🐱"),
    ("The 100th Way Cursed Sovereign", "spooky", "⚠️ 'Love them... or they will revoke your waking consciousness.'", "👑🐱"),
    ("Gargoyle Stone Cat", "spooky", "⚠️ Perched motionless on the container corner, unblinking in the dark.", "🗿🐱"),
    ("Void Jumper Felid", "spooky", "⚠️ Teleporting instantly across screen coordinates in quantum blurs.", "⚡🐈‍⬛"),
    ("Sub-Auditory Hissing Panther", "spooky", "⚠️ Silent subsonic warning hiss that triggers cold sweat.", "🐆"),
    ("Thermal Heat-Lock Predator", "spooky", "⚠️ Infrared feline silhouette locking onto your cerebral heat signature.", "🌡️🐱"),
    ("Hypnotic Spiral-Eyed Cat", "spooky", "⚠️ Concentric revolving rings trying to lure you back into slow-wave slumber.", "🌀🐱"),
    ("Ashen Ember Feline", "spooky", "⚠️ Burning charcoal coat shedding glowing sparks across the glass panel.", "🔥🐱"),
    ("Creeping Mist Panther", "spooky", "⚠️ Claws emerging from a bank of cold graveyard fog.", "🌫️🐱"),
    ("Cursed Hieroglyph Bastet", "spooky", "⚠️ An ancient occult talisman pulsing with dark violet luminescence.", "🔮🐱"),
    ("Cold Frostbitten Snow Leopard", "spooky", "⚠️ Freezing the timer progress bar in ice crystals.", "❄️🐆"),
    ("Uncanny Valley Human-Faced Cat", "spooky", "⚠️ Feline body with an eerily recognizable, judging human expression.", "🎭🐱"),
    ("The Insomnia Entity Cat", "spooky", "⚠️ Manifests exclusively when sleep deprivation reaches dangerous thresholds.", "👁️‍🗨️🐱"),
    ("Abyssal ETS Percentile Reaper", "spooky", "⚠️ Spectral feline grim reaper holding your GRE quantitative percentile hostage.", "🦅🐱")
]

# Guarantee:
# Ways 1 to 15: strictly cutesy features (first 15 items in manifest)
cutesy_shuffled = cutesy_cats.copy()
random.shuffle(cutesy_shuffled)

first_15 = cutesy_shuffled[:15]
remaining_cutesy = cutesy_shuffled[15:]

# Remaining 85 slots: 35 cutesy + 50 spooky
remaining_pool = remaining_cutesy + spooky_cats
random.shuffle(remaining_pool)

manifest_100 = first_15 + remaining_pool

features_json = []
for idx, (name, cat_type, desc, icon) in enumerate(manifest_100):
    features_json.append({
        "way_unlock": idx + 1,
        "name": name,
        "type": cat_type,
        "description": desc,
        "icon": icon
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

# Verify EVERY SINGLE ICON contains a cat
cat_emojis = ["🐱", "🐈", "🐆", "🐅", "🦁", "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾"]
for idx, f in enumerate(features_json):
    assert any(c in f["icon"] for c in cat_emojis), f"Item {idx+1} ({f['name']}) icon '{f['icon']}' does not contain a cat!"

print("ALL 100 ICONS VERIFIED AS 100% CATS!")
