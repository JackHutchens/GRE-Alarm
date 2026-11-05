import xml.etree.ElementTree as ET
import urllib.parse

# 1. Sleek, Deadly, Beautiful Feline Claw Cursor
# Active tip at (4, 3) for pinpoint clicking accuracy
claw_default_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 36 36" fill="none">
  <defs>
    <linearGradient id="furGrad" x1="12" y1="20" x2="30" y2="34" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#27272a"/>
      <stop offset="50%" stop-color="#18181b"/>
      <stop offset="100%" stop-color="#09090b"/>
    </linearGradient>
    <linearGradient id="clawBlade" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="35%" stop-color="#fef08a"/>
      <stop offset="70%" stop-color="#f59e0b"/>
      <stop offset="100%" stop-color="#dc2626"/>
    </linearGradient>
    <radialGradient id="padGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#fda4af"/>
      <stop offset="60%" stop-color="#f43f5e"/>
      <stop offset="100%" stop-color="#9f1239"/>
    </radialGradient>
    <filter id="clawGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="1" stdDeviation="1.2" flood-color="#ef4444" flood-opacity="0.6"/>
    </filter>
  </defs>

  <!-- Drop Shadow under paw -->
  <ellipse cx="20" cy="24" rx="10" ry="8" fill="#000000" opacity="0.4"/>

  <!-- Furry Paw Wrist / Forelimb -->
  <path d="M14 36 C14 26, 17 22, 22 22 C27 22, 30 26, 30 36 Z" fill="url(#furGrad)" stroke="#3f3f46" stroke-width="1"/>

  <!-- Razor Hooked Talons -->
  <!-- Talon 1 (Main click point at 4, 3) -->
  <path d="M4 3 C6 7, 9 12, 11 14 C10 11, 8 7, 4 3 Z" fill="url(#clawBlade)" stroke="#ef4444" stroke-width="0.8" filter="url(#clawGlow)"/>
  <path d="M4 3 L6 8" stroke="#ffffff" stroke-width="0.9" stroke-linecap="round"/>

  <!-- Talon 2 -->
  <path d="M12 2 C13 7, 15 11, 16 13 C15 10, 14 6, 12 2 Z" fill="url(#clawBlade)" stroke="#ef4444" stroke-width="0.8" filter="url(#clawGlow)"/>
  <path d="M12 2 L14 7" stroke="#ffffff" stroke-width="0.9" stroke-linecap="round"/>

  <!-- Talon 3 -->
  <path d="M21 4 C21 8, 22 12, 23 14 C22 11, 21 8, 21 4 Z" fill="url(#clawBlade)" stroke="#ef4444" stroke-width="0.8" filter="url(#clawGlow)"/>
  <path d="M21 4 L22 8" stroke="#ffffff" stroke-width="0.8" stroke-linecap="round"/>

  <!-- Talon 4 -->
  <path d="M29 8 C28 12, 28 15, 27 17 C28 14, 29 11, 29 8 Z" fill="url(#clawBlade)" stroke="#ef4444" stroke-width="0.8" filter="url(#clawGlow)"/>

  <!-- Toe Digits & Pink Pads -->
  <!-- Toe 1 -->
  <circle cx="10" cy="15" r="3.2" fill="#27272a" stroke="#52525b" stroke-width="0.8"/>
  <circle cx="9.8" cy="15" r="2" fill="url(#padGlow)"/>

  <!-- Toe 2 -->
  <circle cx="16" cy="14" r="3.2" fill="#27272a" stroke="#52525b" stroke-width="0.8"/>
  <circle cx="16" cy="14" r="2" fill="url(#padGlow)"/>

  <!-- Toe 3 -->
  <circle cx="22" cy="15" r="3.2" fill="#27272a" stroke="#52525b" stroke-width="0.8"/>
  <circle cx="22.2" cy="15" r="2" fill="url(#padGlow)"/>

  <!-- Toe 4 -->
  <circle cx="27" cy="18" r="2.8" fill="#27272a" stroke="#52525b" stroke-width="0.8"/>
  <circle cx="27" cy="18" r="1.7" fill="url(#padGlow)"/>

  <!-- Central Palm Pad -->
  <path d="M15 24 C15 20, 18 19, 22 19 C26 19, 29 20, 29 24 C29 28, 26 31, 22 31 C18 31, 15 28, 15 24 Z" fill="#27272a" stroke="#52525b" stroke-width="1"/>
  <path d="M16.5 24 C16.5 21, 19 20, 22 20 C25 20, 27.5 21, 27.5 24 C27.5 27.5, 25 29.5, 22 29.5 C19 29.5, 16.5 27.5, 16.5 24 Z" fill="url(#padGlow)"/>
  <ellipse cx="22" cy="23" rx="2.5" ry="1.5" fill="#ffffff" opacity="0.45"/>
</svg>"""

# 2. Lethal Swiping Claw Pointer (with glowing energetic slash trails)
# Tip at (5, 4)
claw_pointer_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="38" height="38" viewBox="0 0 38 38" fill="none">
  <defs>
    <linearGradient id="slashGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#f43f5e" stop-opacity="0.9"/>
      <stop offset="50%" stop-color="#f59e0b" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#ef4444" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="bladeGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="30%" stop-color="#fef08a"/>
      <stop offset="65%" stop-color="#f59e0b"/>
      <stop offset="100%" stop-color="#dc2626"/>
    </linearGradient>
    <radialGradient id="padGlow2" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#fda4af"/>
      <stop offset="60%" stop-color="#f43f5e"/>
      <stop offset="100%" stop-color="#881337"/>
    </radialGradient>
  </defs>

  <!-- Curved Energy Slash Trails -->
  <path d="M2 12 Q12 1 24 2" stroke="url(#slashGrad)" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M5 16 Q16 4 28 6" stroke="url(#slashGrad)" stroke-width="2" stroke-linecap="round"/>
  <path d="M10 20 Q20 8 32 11" stroke="url(#slashGrad)" stroke-width="1.8" stroke-linecap="round"/>

  <!-- Furry Base -->
  <path d="M16 38 C16 28, 19 24, 24 24 C29 24, 32 28, 32 38 Z" fill="#18181b" stroke="#52525b" stroke-width="1"/>

  <!-- Razor Hooked Talons Extended for Strike -->
  <!-- Talon 1 (Click point at 5, 4) -->
  <path d="M5 4 C8 8, 11 13, 13 16 C12 13, 10 8, 5 4 Z" fill="url(#bladeGrad)" stroke="#ef4444" stroke-width="0.8"/>
  <path d="M5 4 L8 9" stroke="#ffffff" stroke-width="1" stroke-linecap="round"/>

  <!-- Talon 2 -->
  <path d="M14 3 C16 7, 18 12, 19 15 C18 11, 16 7, 14 3 Z" fill="url(#bladeGrad)" stroke="#ef4444" stroke-width="0.8"/>
  <path d="M14 3 L16 8" stroke="#ffffff" stroke-width="1" stroke-linecap="round"/>

  <!-- Talon 3 -->
  <path d="M23 5 C24 9, 25 14, 26 16 C25 12, 24 9, 23 5 Z" fill="url(#bladeGrad)" stroke="#ef4444" stroke-width="0.8"/>

  <!-- Talon 4 -->
  <path d="M31 9 C30 13, 30 17, 29 19 C30 16, 31 13, 31 9 Z" fill="url(#bladeGrad)" stroke="#ef4444" stroke-width="0.8"/>

  <!-- Toe Pads -->
  <circle cx="12" cy="17" r="3.4" fill="#27272a" stroke="#ef4444" stroke-width="1"/>
  <circle cx="11.8" cy="17" r="2.2" fill="url(#padGlow2)"/>

  <circle cx="18" cy="16" r="3.4" fill="#27272a" stroke="#ef4444" stroke-width="1"/>
  <circle cx="18" cy="16" r="2.2" fill="url(#padGlow2)"/>

  <circle cx="24" cy="17" r="3.4" fill="#27272a" stroke="#ef4444" stroke-width="1"/>
  <circle cx="24.2" cy="17" r="2.2" fill="url(#padGlow2)"/>

  <circle cx="29" cy="20" r="3" fill="#27272a" stroke="#ef4444" stroke-width="1"/>
  <circle cx="29" cy="20" r="1.9" fill="url(#padGlow2)"/>

  <!-- Palm Pad -->
  <path d="M17 26 C17 22, 20 21, 24 21 C28 21, 31 22, 31 26 C31 30, 28 33, 24 33 C20 33, 17 30, 17 26 Z" fill="#27272a" stroke="#ef4444" stroke-width="1.2"/>
  <path d="M18.5 26 C18.5 23, 21 22, 24 22 C27 22, 29.5 23, 29.5 26 C29.5 29.5, 27 31.5, 24 31.5 C21 31.5, 18.5 29.5, 18.5 26 Z" fill="url(#padGlow2)"/>
  <ellipse cx="24" cy="25" rx="3" ry="1.8" fill="#ffffff" opacity="0.5"/>
</svg>"""

ET.fromstring(claw_default_svg)
ET.fromstring(claw_pointer_svg)
print("Both claw cursors parsed cleanly!")

def encode_svg(s):
    # Minimal URL safe encoding for CSS cursor data URI
    return urllib.parse.quote("".join(line.strip() for line in s.splitlines()))

def_encoded = encode_svg(claw_default_svg)
ptr_encoded = encode_svg(claw_pointer_svg)

with open("web/claw_default.svg", "w", encoding="utf-8") as f:
    f.write(claw_default_svg)

with open("web/claw_pointer.svg", "w", encoding="utf-8") as f:
    f.write(claw_pointer_svg)

print("Saved claw_default.svg and claw_pointer.svg!")

# Output CSS cursor strings:
print(f"claw_default: data:image/svg+xml,{def_encoded[:40]}... (len={len(def_encoded)})")
print(f"claw_pointer: data:image/svg+xml,{ptr_encoded[:40]}... (len={len(ptr_encoded)})")
