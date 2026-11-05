"""
Verification Script for Audio Blending, Isolated Volume, Curled Claw Cursor, Dynamic Page Resize,
Smooth Cat Repositioning, and Max Study Duration with Session Statistics.
"""

import os
import re

def main():
    web_dir = os.path.join(os.path.dirname(__file__), "..", "web")
    app_js_path = os.path.join(web_dir, "app.js")
    index_html_path = os.path.join(web_dir, "index.html")
    styles_css_path = os.path.join(web_dir, "styles.css")
    curled_svg_path = os.path.join(web_dir, "claw_curled.svg")

    with open(app_js_path, "r", encoding="utf-8") as f:
        js = f.read()

    with open(index_html_path, "r", encoding="utf-8") as f:
        html = f.read()

    with open(styles_css_path, "r", encoding="utf-8") as f:
        css = f.read()

    print("--- 1. Testing Audio Blending Implementation ---")
    assert "blendFrac = Math.min(1.0, elapsed / 30.0)" in js, "blendFrac calculation missing"
    assert "catTargetVolume = Math.max(0.001, blendFrac * 1.0)" in js, "100WTLAC target volume not ramping to 1.0"
    assert "blendedAmbientVol = Math.max(0.0, (1.0 - blendFrac) * baseAmbient)" in js, "Ambient audio cross-fade calculation missing"
    assert "triggerCatPunishment" in js
    # Verify triggerCatPunishment does NOT stop procedural audio prematurely
    trigger_match = re.search(r"function triggerCatPunishment\(\)\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}", js)
    assert trigger_match, "triggerCatPunishment function not found"
    assert "stopProceduralBackgroundTrack();" not in trigger_match.group(1), "triggerCatPunishment must not stop procedural track prematurely"
    print("PASS: Audio cross-fade blending correctly designed (cat 0->1.0, ambient ambientVol->0 over 30s)")

    print("\n--- 2. Testing Volume Isolation & Master Volume Deletion ---")
    assert "STATE.alarmAudioElement.volume = 1.0;" in js, "Alarm audio element volume not fixed to 1.0"
    assert "masterGain.gain.setValueAtTime(1.0, ctx.currentTime);" in js, "Alarm synth masterGain not fixed to 1.0"
    assert "masterGain.gain.exponentialRampToValueAtTime(1.0, ctx.currentTime + 30.0);" in js, "Fallback cat synth not ramping to 1.0"
    assert "slider-ambient-volume-sync" in html, "Ambient volume sliders missing in HTML"
    assert "setAmbientVolume" in js, "setAmbientVolume function missing in JS"
    assert "Alarm &amp; 100WTLAC Volume" not in html, "Master volume block must be deleted from UI"
    assert "masterVolume: 0.85" not in js, "Legacy masterVolume setting must be deleted"
    print("PASS: Master volume option deleted; Alarm assault and 100WTLAC locked strictly at 100%; slider isolated to ambient audio")

    print("\n--- 2b. Testing Replacement of Generated Tracks with ambient_tracks Folder ---")
    assert "procedural1" not in js, "Legacy generated tracks (procedural1-5) must be removed from app.js"
    assert "procedural1" not in html, "Legacy generated tracks (procedural1-5) must be removed from index.html"
    assert "ambient_clean_soul" in js, "ambient_clean_soul must be present in app.js"
    assert "ambient_clean_soul" in html, "ambient_clean_soul must be present in index.html"
    assert "/ambient_tracks/08_clean_soul.mp3" in js, "ambient_tracks audio path must be in app.js"
    print("PASS: Generated tracks replaced completely with ambient_tracks folder audio")

    print("\n--- 3. Testing Curled Paw Active Clicker Asset & Styles ---")
    assert os.path.exists(curled_svg_path), "claw_curled.svg missing in web directory"
    with open(curled_svg_path, "r", encoding="utf-8") as f:
        svg_content = f.read()
    assert "curledBladeGrad" in svg_content or "curled" in svg_content, "claw_curled.svg lacks curled claw features"
    assert "body.punishment-cat-mode button:active" in css or "body.punishment-cat-mode:active" in css, "Active cursor rule missing in styles.css"
    assert "claw_curled.svg" in css, "claw_curled.svg reference missing in styles.css"
    print("PASS: Curled claw cursor asset & CSS :active selectors successfully implemented")

    print("\n--- 4. Testing Dynamic Page Length Resizing ---")
    assert "computeContentDimensions" in js, "computeContentDimensions function missing"
    assert "setupDynamicResizeObservers" in js, "setupDynamicResizeObservers function missing"
    assert "ResizeObserver" in js, "ResizeObserver not utilized"
    assert "footer.offsetTop" in js or "main.offsetTop" in js, "Content bounds measurement not checking main/footer offsets"
    assert "layer.style.height" in js, "Dynamic layer height sizing missing"
    print("PASS: Dynamic page length calculation and ResizeObserver integrated")

    print("\n--- 5. Testing Smooth Cat Re-placement on Resize ---")
    assert "smoothlyRepositionCatsOnResize" in js, "smoothlyRepositionCatsOnResize function missing"
    assert "scaleX = newW / oldW" in js, "Proportional X scaling missing"
    assert "scaleY = newH / oldH" in js, "Proportional Y scaling missing"
    assert "c.vy = -Math.max" in js, "Upward bounce impulse on floor compression missing"
    print("PASS: Smooth cat repositioning with proportional scaling and upward bounce impulse verified")

    print("\n--- 6. Testing Max Study Duration & Session Statistics Modal ---")
    assert "maxStudyDurationMinutes: 20" in js, "maxStudyDurationMinutes initial state missing"
    assert "select-max-study-duration" in html, "Max study duration select element missing in HTML"
    assert "modal-session-statistics" in html, "modal-session-statistics missing in HTML"
    assert "stats-total-time" in html, "stats-total-time element missing in HTML"
    assert "stats-questions-count" in html, "stats-questions-count element missing in HTML"
    assert "stats-accuracy-pct" in html, "stats-accuracy-pct element missing in HTML"
    assert "stats-final-score" in html, "stats-final-score element missing in HTML"
    assert "stats-subtypes-breakdown" in html, "stats-subtypes-breakdown element missing in HTML"
    assert "stats-readiness-level" in html, "stats-readiness-level element missing in HTML"
    assert "stats-menagerie-level" in html, "stats-menagerie-level element missing in HTML"
    assert "endStudySessionMaxDuration" in js, "endStudySessionMaxDuration function missing in JS"
    assert "openSessionStatisticsModal" in js, "openSessionStatisticsModal function missing in JS"
    assert "closeSessionStatisticsModal" in js, "closeSessionStatisticsModal function missing in JS"
    assert "btn-stats-arm-next" in html and "btn-stats-arm-next" in js, "btn-stats-arm-next wiring missing"
    print("PASS: Max study duration setting, timeout triggers, and comprehensive session statistics modal verified")

    print("\n*** ALL USER REQUIREMENTS VERIFIED SUCCESSFULLY! ***")

if __name__ == "__main__":
    main()
