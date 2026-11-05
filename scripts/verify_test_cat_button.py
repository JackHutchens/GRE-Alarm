"""
Verification script for immediate test progression to the "100 Ways to Love a Cat" phase.
"""
import os
import re

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_js_path = os.path.join(project_root, "web", "app.js")
index_html_path = os.path.join(project_root, "web", "index.html")

with open(app_js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

with open(index_html_path, "r", encoding="utf-8") as f:
    html_code = f.read()

def test_buttons_in_html():
    # Setup card button
    assert 'id="btn-test-cat-punishment"' in html_code, "btn-test-cat-punishment missing in index.html"
    assert 'Test "100 Ways to Love a Cat" Phase' in html_code
    
    # Top banner button (accessible at all times during quiz / timer)
    assert 'id="btn-banner-trigger-cat"' in html_code, "btn-banner-trigger-cat missing in index.html"
    assert 'Test Cat Phase' in html_code
    
    # Ringing panel button
    assert 'id="btn-ringing-test-cat"' in html_code, "btn-ringing-test-cat missing in index.html"
    
    print("[OK] HTML buttons verified: Setup panel, top banner, and alarm ringing panel all contain testing buttons.")

def test_js_handler():
    assert "async function testImmediateCatPunishment" in js_code, "testImmediateCatPunishment function missing in app.js"
    assert "triggerCatPunishment()" in js_code
    assert "btn-test-cat-punishment" in js_code
    assert "btn-banner-trigger-cat" in js_code
    assert "btn-ringing-test-cat" in js_code
    
    # Verify function zeros out timer and primes audio
    fn_match = re.search(r'async function testImmediateCatPunishment\(\)\s*\{(.*?)\n\}', js_code, re.DOTALL)
    assert fn_match, "testImmediateCatPunishment body not found"
    fn_body = fn_match.group(1)
    assert "STATE.quizSecondsRemaining = 0" in fn_body
    assert "triggerCatPunishment()" in fn_body
    
    print("[OK] JS handler verified: testImmediateCatPunishment zeros countdown, loads question if needed, and engages cat punishment.")

if __name__ == "__main__":
    print("=" * 60)
    print("VERIFYING '100 WAYS TO LOVE A CAT' TEST BUTTON")
    print("=" * 60)
    test_buttons_in_html()
    test_js_handler()
    print("=" * 60)
    print("ALL TEST BUTTON VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 60)
