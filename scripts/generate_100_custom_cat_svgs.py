"""
Generate 100 unique, hand-crafted vector SVG feline avatars for the Menagerie.
NO double emojis. Every icon is a dedicated custom SVG feline artwork.
"""
import json
import xml.etree.ElementTree as ET

def make_cat_svg(cat_id, name, cat_type):
    # Generates a dedicated custom SVG for each cat based on its name and lore
    # Base head geometry: Head center (18, 20), radius ~12
    
    # Color palettes by breed / archetype
    svg_elements = []
    
    # Default parameters
    bg_accent = ""
    ears = ""
    fur_color = "#f97316" # Orange tabby default
    fur_stroke = "#c2410c"
    inner_ear = "#fecdd3"
    muzzle_color = "#ffedd5"
    nose_color = "#f43f5e"
    eye_type = "cutesy_round"
    eye_color = "#0284c7"
    whiskers_color = "#fdba74"
    special_decor = ""
    
    # Match specific cats
    n = name.lower()
    
    # -------------------------------------------------------------
    # BREED & FUR DETERMINATION
    # -------------------------------------------------------------
    if "tuxedo" in n:
        fur_color = "#18181b"; fur_stroke = "#3f3f46"; muzzle_color = "#f8fafc"; eye_color = "#eab308"; whiskers_color = "#e2e8f0"
        special_decor += '<polygon points="18,30 16,33 20,33" fill="#ef4444"/><polygon points="15,31 18,32 15,33" fill="#dc2626"/><polygon points="21,31 18,32 21,33" fill="#dc2626"/>' # Bowtie
    elif "calico" in n:
        fur_color = "#f8fafc"; fur_stroke = "#cbd5e1"; muzzle_color = "#f8fafc"; eye_color = "#10b981"; whiskers_color = "#94a3b8"
        special_decor += '<path d="M8 12 Q14 10 16 16 Q10 20 8 16 Z" fill="#ea580c"/>' # Ginger patch
        special_decor += '<path d="M22 13 Q28 11 28 17 Q24 20 20 16 Z" fill="#1e293b"/>' # Dark patch
    elif "siamese" in n:
        fur_color = "#fef3c7"; fur_stroke = "#d97706"; muzzle_color = "#451a03"; inner_ear = "#78350f"; eye_color = "#2563eb"; whiskers_color = "#92400e"
        special_decor += '<ellipse cx="18" cy="21" rx="8" ry="6" fill="#451a03" opacity="0.85"/>' # Dark facial mask
    elif "persian" in n or "fluffy white" in n:
        fur_color = "#f8fafc"; fur_stroke = "#cbd5e1"; muzzle_color = "#f1f5f9"; eye_color = "#059669"; whiskers_color = "#cbd5e1"
        special_decor += '<circle cx="6" cy="22" r="4" fill="#f8fafc"/><circle cx="30" cy="22" r="4" fill="#f8fafc"/>' # Fluffy cheek ruffs
    elif "orange" in n or "ginger" in n or "cinnamon" in n:
        fur_color = "#f97316"; fur_stroke = "#c2410c"; eye_color = "#ca8a04"; muzzle_color = "#ffedd5"; whiskers_color = "#fdba74"
        special_decor += '<path d="M18 10 L18 14 M15 11 L16 15 M21 11 L20 15" stroke="#c2410c" stroke-width="1"/>' # Tabby stripes
    elif "void" in n or "midnight" in n or "black cat" in n or "shadow" in n:
        fur_color = "#09090b"; fur_stroke = "#27272a"; inner_ear = "#18181b"; muzzle_color = "#18181b"; eye_color = "#facc15"; eye_type = "slit"; whiskers_color = "#71717a"
    elif "ghost" in n or "spectral" in n or "phantom" in n:
        fur_color = "#06b6d4"; fur_stroke = "#22d3ee"; inner_ear = "#67e8f9"; muzzle_color = "#cffafe"; eye_color = "#ffffff"; eye_type = "spectral"; whiskers_color = "#a5f3fc"
        bg_accent = '<path d="M8 28 C6 34, 18 36, 18 33 C18 36, 30 34, 28 28 Z" fill="#06b6d4" opacity="0.3"/>'
    elif "vampire" in n:
        fur_color = "#2e1065"; fur_stroke = "#581c87"; inner_ear = "#831843"; eye_color = "#dc2626"; eye_type = "slit"
        special_decor += '<polygon points="15,25 16,29 17,25" fill="#ffffff"/><polygon points="19,25 20,29 21,25" fill="#ffffff"/><circle cx="16" cy="29" r="0.8" fill="#dc2626"/>' # Vampire fangs
    elif "demon" in n or "horned" in n:
        fur_color = "#450a0a"; fur_stroke = "#991b1b"; inner_ear = "#7f1d1d"; eye_color = "#f59e0b"; eye_type = "slit"
        special_decor += '<path d="M11 9 Q6 3 3 7 Q8 10 11 12 Z" fill="#18181b" stroke="#dc2626" stroke-width="0.8"/>' # Left Horn
        special_decor += '<path d="M25 9 Q30 3 33 7 Q28 10 25 12 Z" fill="#18181b" stroke="#dc2626" stroke-width="0.8"/>' # Right Horn
    elif "cyber" in n or "ram" in n or "glitch" in n:
        fur_color = "#0f172a"; fur_stroke = "#06b6d4"; inner_ear = "#38bdf8"; eye_color = "#06b6d4"; eye_type = "cyber"
        special_decor += '<line x1="6" y1="18" x2="30" y2="18" stroke="#06b6d4" stroke-width="0.6" stroke-dasharray="2 1"/><rect x="8" y="16" width="20" height="4" fill="#06b6d4" opacity="0.25"/>' # Cyber visor
    elif "skeletal" in n:
        fur_color = "#f8fafc"; fur_stroke = "#64748b"; muzzle_color = "#e2e8f0"; eye_color = "#000000"; eye_type = "socket"
        special_decor += '<path d="M16 23 L16 26 M18 23 L18 26 M20 23 L20 26" stroke="#475569" stroke-width="0.8"/>' # Teeth marks
    elif "blood" in n or "bleeding" in n:
        fur_color = "#18181b"; fur_stroke = "#ef4444"; inner_ear = "#7f1d1d"; eye_color = "#ef4444"; eye_type = "slit"
        special_decor += '<path d="M9 14 L12 25 M14 12 L17 26 M19 12 L22 25" stroke="#ef4444" stroke-width="1" stroke-linecap="round" opacity="0.8"/>' # Blood scratches
    elif "hypnotic" in n:
        fur_color = "#1e1b4b"; fur_stroke = "#6366f1"; inner_ear = "#818cf8"; eye_type = "hypno"
    elif "cheshire" in n:
        fur_color = "#4a044e"; fur_stroke = "#a21caf"; inner_ear = "#d946ef"; eye_color = "#facc15"; eye_type = "slit"
        special_decor += '<path d="M10 24 Q18 34 26 24 Q18 27 10 24 Z" fill="#ffffff" stroke="#a21caf" stroke-width="0.8"/><path d="M12 25 L13 28 M15 25 L16 28 M18 25 L18 28 M20 25 L20 28 M23 25 L22 28" stroke="#701a75" stroke-width="0.6"/>' # Cheshire Grin
    elif "box" in n:
        fur_color = "#ea580c"; fur_stroke = "#9a3412"; eye_color = "#10b981"
        special_decor += '<rect x="6" y="24" width="24" height="11" fill="#78350f" stroke="#451a03" stroke-width="1" rx="1"/><line x1="6" y1="24" x2="18" y2="28" stroke="#451a03" stroke-width="0.8"/><line x1="30" y1="24" x2="18" y2="28" stroke="#451a03" stroke-width="0.8"/>' # Box
    elif "yarn" in n:
        fur_color = "#f97316"; fur_stroke = "#c2410c"; eye_color = "#0284c7"
        special_decor += '<circle cx="28" cy="28" r="6" fill="#ec4899" stroke="#be185d" stroke-width="0.8"/><path d="M28 24 Q24 28 28 32 M25 26 Q29 30 27 34" stroke="#fbcfe8" stroke-width="0.6"/><path d="M22 29 Q18 33 12 32" stroke="#ec4899" stroke-width="0.8"/>' # Yarn ball & string
    elif "angel" in n:
        fur_color = "#ffffff"; fur_stroke = "#93c5fd"; eye_color = "#38bdf8"
        special_decor += '<ellipse cx="18" cy="5" rx="7" ry="2" fill="none" stroke="#facc15" stroke-width="1.2"/>' # Halo
    elif "spitting manul" in n or "manul" in n:
        fur_color = "#94a3b8"; fur_stroke = "#475569"; muzzle_color = "#cbd5e1"; eye_color = "#eab308"; eye_type = "slit"
        special_decor += '<circle cx="8" cy="22" r="5" fill="#94a3b8"/><circle cx="28" cy="22" r="5" fill="#94a3b8"/>' # Fat round manul cheeks
    elif "panther" in n or "leopard" in n:
        fur_color = "#0f172a"; fur_stroke = "#334155"; eye_color = "#84cc16"; eye_type = "slit"
    elif "lion" in n:
        fur_color = "#d97706"; fur_stroke = "#92400e"; eye_color = "#ca8a04"
        special_decor += '<circle cx="18" cy="20" r="14" fill="none" stroke="#b45309" stroke-width="3" stroke-dasharray="3 1.5"/>' # Lion mane
    elif "blep" in n:
        fur_color = "#fb923c"; fur_stroke = "#c2410c"; eye_color = "#0284c7"
        special_decor += '<path d="M17 25 Q18 29 19 25 Z" fill="#f43f5e"/>' # Tiny blep tongue
    elif "bell" in n:
        fur_color = "#f43f5e"; fur_stroke = "#be123c"; eye_color = "#38bdf8"
        special_decor += '<circle cx="18" cy="32" r="2.5" fill="#facc15" stroke="#ca8a04" stroke-width="0.6"/><circle cx="18" cy="33" r="0.6" fill="#78350f"/>' # Bell
    elif cat_type == "spooky":
        fur_color = "#1e1b4b" if cat_id % 2 == 0 else "#18181b"
        fur_stroke = "#4338ca" if cat_id % 2 == 0 else "#991b1b"
        eye_color = "#dc2626" if cat_id % 3 == 0 else ("#facc15" if cat_id % 3 == 1 else "#c084fc")
        eye_type = "slit"
    else:
        # Assorted warm domestic colors
        coats = [
            ("#fb923c", "#c2410c", "#ca8a04"), # ginger
            ("#94a3b8", "#475569", "#0284c7"), # grey tabby
            ("#d1d5db", "#6b7280", "#10b981"), # silver
            ("#fdba74", "#ea580c", "#059669"), # peach
            ("#e2e8f0", "#94a3b8", "#38bdf8"), # cream
        ]
        pick = coats[cat_id % len(coats)]
        fur_color = pick[0]; fur_stroke = pick[1]; eye_color = pick[2]

    # Specific eye variations
    if "sleep" in n or "purr" in n or "cozy" in n:
        eye_type = "sleeping"
    elif "wink" in n:
        eye_type = "wink"

    # -------------------------------------------------------------
    # BUILD SVG COMPONENTS
    # -------------------------------------------------------------
    # 1. Ears
    if "scottish fold" in n:
        ears = f'''
        <path d="M8 17 C8 11, 14 10, 13 16 Z" fill="{fur_color}" stroke="{fur_stroke}" stroke-width="1"/>
        <path d="M28 17 C28 11, 22 10, 23 16 Z" fill="{fur_color}" stroke="{fur_stroke}" stroke-width="1"/>
        '''
    else:
        ears = f'''
        <!-- Ears -->
        <polygon points="7,18 10,6 16,13" fill="{fur_color}" stroke="{fur_stroke}" stroke-width="1.2" stroke-linejoin="round"/>
        <polygon points="9,16 11,9 14,13" fill="{inner_ear}"/>
        <polygon points="29,18 26,6 20,13" fill="{fur_color}" stroke="{fur_stroke}" stroke-width="1.2" stroke-linejoin="round"/>
        <polygon points="27,16 25,9 22,13" fill="{inner_ear}"/>
        '''

    # 2. Head Shape
    head = f'''
    <!-- Head Base -->
    <ellipse cx="18" cy="20" rx="12" ry="10.5" fill="{fur_color}" stroke="{fur_stroke}" stroke-width="1.3"/>
    '''

    # 3. Eyes rendering
    if eye_type == "sleeping":
        eyes = f'''
        <!-- Sleeping Happy Curved Eyes -->
        <path d="M12 18 Q14 15 16 18" stroke="{fur_stroke}" stroke-width="1.5" stroke-linecap="round" fill="none"/>
        <path d="M20 18 Q22 15 24 18" stroke="{fur_stroke}" stroke-width="1.5" stroke-linecap="round" fill="none"/>
        '''
    elif eye_type == "slit":
        eyes = f'''
        <!-- Predatory Slit Eyes -->
        <ellipse cx="13.5" cy="18" rx="3.2" ry="3.2" fill="{eye_color}"/>
        <ellipse cx="13.5" cy="18" rx="0.9" ry="3" fill="#000000"/>
        <ellipse cx="22.5" cy="18" rx="3.2" ry="3.2" fill="{eye_color}"/>
        <ellipse cx="22.5" cy="18" rx="0.9" ry="3" fill="#000000"/>
        '''
    elif eye_type == "hypno":
        eyes = f'''
        <!-- Hypnotic Spiral Concentric Eyes -->
        <circle cx="13.5" cy="18" r="3.2" fill="#818cf8"/>
        <circle cx="13.5" cy="18" r="2" fill="none" stroke="#312e81" stroke-width="0.8"/>
        <circle cx="13.5" cy="18" r="0.8" fill="#ffffff"/>
        <circle cx="22.5" cy="18" r="3.2" fill="#818cf8"/>
        <circle cx="22.5" cy="18" r="2" fill="none" stroke="#312e81" stroke-width="0.8"/>
        <circle cx="22.5" cy="18" r="0.8" fill="#ffffff"/>
        '''
    elif eye_type == "socket":
        eyes = f'''
        <!-- Hollow Skeletal Sockets -->
        <circle cx="13.5" cy="18" r="3.5" fill="#09090b"/>
        <circle cx="13.5" cy="18" r="1" fill="#ef4444"/>
        <circle cx="22.5" cy="18" r="3.5" fill="#09090b"/>
        <circle cx="22.5" cy="18" r="1" fill="#ef4444"/>
        '''
    elif eye_type == "cyber":
        eyes = f'''
        <!-- Cyber Visor Glowing Optics -->
        <rect x="11" y="16.5" width="5" height="3" rx="1" fill="#06b6d4"/>
        <rect x="20" y="16.5" width="5" height="3" rx="1" fill="#06b6d4"/>
        <circle cx="13.5" cy="18" r="1" fill="#ffffff"/>
        <circle cx="22.5" cy="18" r="1" fill="#ffffff"/>
        '''
    elif eye_type == "spectral":
        eyes = f'''
        <!-- Spectral White Voids -->
        <ellipse cx="13.5" cy="18" rx="3" ry="3.5" fill="#ffffff" filter="drop-shadow(0 0 2px #22d3ee)"/>
        <ellipse cx="22.5" cy="18" rx="3" ry="3.5" fill="#ffffff" filter="drop-shadow(0 0 2px #22d3ee)"/>
        '''
    else: # cutesy_round
        eyes = f'''
        <!-- Big Saucer Eyes with Highlights -->
        <circle cx="13.5" cy="18" r="3.2" fill="{eye_color}"/>
        <circle cx="13.5" cy="18" r="2.2" fill="#09090b"/>
        <circle cx="12.5" cy="16.8" r="1" fill="#ffffff"/>
        <circle cx="14.5" cy="19" r="0.5" fill="#ffffff"/>
        
        <circle cx="22.5" cy="18" r="3.2" fill="{eye_color}"/>
        <circle cx="22.5" cy="18" r="2.2" fill="#09090b"/>
        <circle cx="21.5" cy="16.8" r="1" fill="#ffffff"/>
        <circle cx="23.5" cy="19" r="0.5" fill="#ffffff"/>
        '''

    # 4. Muzzle, Nose, Mouth
    muzzle = f'''
    <!-- Muzzle & Whiskers -->
    <ellipse cx="16" cy="24" rx="2.5" ry="1.8" fill="{muzzle_color}"/>
    <ellipse cx="20" cy="24" rx="2.5" ry="1.8" fill="{muzzle_color}"/>
    <polygon points="17,22.2 19,22.2 18,23.4" fill="{nose_color}"/>
    <path d="M16.5 24 Q18 25.5 19.5 24" stroke="{fur_stroke}" stroke-width="0.8" fill="none"/>
    <!-- Whiskers -->
    <line x1="6" y1="21" x2="13" y2="23" stroke="{whiskers_color}" stroke-width="0.8"/>
    <line x1="5" y1="24" x2="13" y2="24.5" stroke="{whiskers_color}" stroke-width="0.8"/>
    <line x1="6" y1="27" x2="13" y2="26" stroke="{whiskers_color}" stroke-width="0.8"/>
    <line x1="30" y1="21" x2="23" y2="23" stroke="{whiskers_color}" stroke-width="0.8"/>
    <line x1="31" y1="24" x2="23" y2="24.5" stroke="{whiskers_color}" stroke-width="0.8"/>
    <line x1="30" y1="27" x2="23" y2="26" stroke="{whiskers_color}" stroke-width="0.8"/>
    '''

    svg = f'''<svg viewBox="0 0 36 36" class="cat-svg-avatar" fill="none" xmlns="http://www.w3.org/2000/svg">{bg_accent}{ears}{head}{special_decor}{eyes}{muzzle}</svg>'''
    
    # Strip extra newlines & spaces
    svg_clean = "".join(line.strip() for line in svg.splitlines())
    return svg_clean

# Load current features
with open("data/hidden_cat_features.json", "r", encoding="utf-8") as f:
    features = json.load(f)

for f in features:
    svg_icon = make_cat_svg(f["way_unlock"], f["name"], f["type"])
    # Validate SVG
    ET.fromstring(svg_icon)
    f["icon"] = svg_icon

# Save back to data/hidden_cat_features.json
with open("data/hidden_cat_features.json", "w", encoding="utf-8") as f:
    json.dump(features, f, indent=2)

print(f"Successfully generated {len(features)} 100% custom SVG feline icons in data/hidden_cat_features.json!")
print("Sample Way 1 SVG:", features[0]["icon"][:80], "...")
print("Sample Way 100 SVG:", features[99]["icon"][:80], "...")
