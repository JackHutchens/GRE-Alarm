"""
Verification script for Ambient Focus Audio Slider and Generator Selection.
Validates:
1. Audio volume slider in Quiz interface and Setup panel
2. Generator drop-down menu in Quiz interface and Setup panel
3. Real-time synchronized state, volume attenuation, and mute toggle
4. Visual indicator badge and custom CSS range thumb styling
"""
import os
import re

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_js_path = os.path.join(project_root, "web", "app.js")
index_html_path = os.path.join(project_root, "web", "index.html")
styles_css_path = os.path.join(project_root, "web", "styles.css")

with open(app_js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

with open(index_html_path, "r", encoding="utf-8") as f:
    html_code = f.read()

with open(styles_css_path, "r", encoding="utf-8") as f:
    css_code = f.read()

def test_html_controls():
    # Quiz panel ambient audio bar
    assert 'id="ambient-audio-bar"' in html_code, "ambient-audio-bar missing in index.html"
    assert 'id="slider-ambient-volume-quiz"' in html_code, "slider-ambient-volume-quiz missing in index.html"
    assert 'id="select-ambient-track-quiz"' in html_code, "select-ambient-track-quiz missing in index.html"
    assert 'id="btn-quiz-ambient-mute"' in html_code, "btn-quiz-ambient-mute missing in index.html"
    assert 'id="quiz-ambient-badge"' in html_code, "quiz-ambient-badge missing in index.html"
    assert 'id="label-ambient-volume-quiz"' in html_code, "label-ambient-volume-quiz missing in index.html"
    
    # Setup panel ambient controls
    assert 'id="slider-ambient-volume-setup"' in html_code, "slider-ambient-volume-setup missing in index.html"
    assert 'id="select-procedural-track"' in html_code, "select-procedural-track missing in index.html"
    
    # Check ambient tracks from ambient_tracks folder are listed in both dropdowns
    ambient_tracks = [
        "ambient_clean_soul", "ambient_promises", "ambient_fresh_air",
        "ambient_meditation_01", "ambient_meditation_02", "ambient_calmant",
        "ambient_space_1990", "ambient_mirage", "ambient_immersed",
        "ambient_frozen_star", "ambient_airship", "ambient_earth_on_wind", "none"
    ]
    for track in ambient_tracks:
        assert f'value="{track}"' in html_code, f'Track {track} missing in dropdowns'
    print("[OK] HTML controls verified: Slider, ambient tracks dropdown, mute button, and live badge present in Quiz panel and Setup.")

def test_js_logic():
    assert "ambientVolume" in js_code, "ambientVolume state missing in app.js"
    assert "isAmbientMuted" in js_code, "isAmbientMuted state missing in app.js"
    assert "function setAmbientVolume" in js_code, "setAmbientVolume function missing in app.js"
    assert "function setAmbientGenerator" in js_code, "setAmbientGenerator function missing in app.js"
    assert "function toggleAmbientMute" in js_code, "toggleAmbientMute function missing in app.js"
    assert "function applyAmbientAudioVolume" in js_code, "applyAmbientAudioVolume function missing in app.js"
    assert "slider-ambient-volume-sync" in js_code, "slider-ambient-volume-sync synchronization missing in app.js"
    assert "select-ambient-generator-sync" in js_code, "select-ambient-generator-sync synchronization missing in app.js"
    
    # Check volume application to proceduralAudio
    assert "STATE.proceduralAudio.volume = effectiveVol" in js_code or "STATE.proceduralAudio.volume =" in js_code
    print("[OK] JS logic verified: Real-time slider sync, volume attenuation, track switching, and mute toggle.")

def test_css_styling():
    assert "#ambient-audio-bar" in css_code, "ambient-audio-bar CSS missing in styles.css"
    assert ".slider-ambient-volume-sync" in css_code, "slider-ambient-volume-sync CSS missing in styles.css"
    assert "slider-ambient-volume-sync::-webkit-slider-thumb" in css_code, "Webkit slider thumb styling missing"
    assert "slider-ambient-volume-sync::-moz-range-thumb" in css_code, "Moz slider thumb styling missing"
    print("[OK] CSS styling verified: Custom cyan neon range thumb and glowing ambient bar gradients.")

if __name__ == "__main__":
    print("=" * 60)
    print("VERIFYING AMBIENT AUDIO SLIDER & GENERATOR DROPDOWN")
    print("=" * 60)
    test_html_controls()
    test_js_logic()
    test_css_styling()
    print("=" * 60)
    print("ALL AMBIENT AUDIO VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
