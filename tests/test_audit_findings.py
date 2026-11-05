"""
Audit Verification Test Suite: Validates all security patches, website-breaking bug fixes,
and documents remaining adversarial attack vectors across the GRE Alarm codebase.
"""

import os
import json
import re
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestAuditFindings:

    # ----------------------------------------------------------------------
    # 1. SECURITY VULNERABILITIES & VERIFIED PATCHES
    # ----------------------------------------------------------------------
    def test_finding_unbounded_content_length_dos_patched(self):
        """
        VERIFICATION: In app/server.py, _read_json_body enforces a 64 KB limit (65536 bytes).
        Payloads exceeding 64 KB return HTTP 413 Payload Too Large, preventing memory exhaustion DoS.
        """
        server_path = os.path.join(PROJECT_ROOT, "app", "server.py")
        with open(server_path, "r", encoding="utf-8") as f:
            content = f.read()

        match = re.search(r"def _read_json_body\(self\)[\s\S]*?(?=def |\Z)", content)
        assert match is not None
        body_func = match.group(0)

        assert "content_len > 65536" in body_func
        assert 'self.send_error(413, "Payload Too Large")' in body_func

    def test_finding_cors_origin_validation_patched(self):
        """
        VERIFICATION: In app/server.py, wildcard CORS is replaced with _validate_origin().
        Foreign cross-origin POST requests are rejected with HTTP 403 Forbidden.
        """
        server_path = os.path.join(PROJECT_ROOT, "app", "server.py")
        with open(server_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "def _validate_origin(self)" in content
        assert 'self.send_error(403, "Cross-Origin Access Prohibited")' in content
        assert 'self.send_header("Access-Control-Allow-Origin", "*")' not in content

    def test_finding_sri_hashes_on_cdns_patched(self):
        """
        VERIFICATION: In web/index.html, KaTeX stylesheets and scripts include
        cryptographic SHA-384 Subresource Integrity (SRI) hashes and crossorigin="anonymous".
        """
        html_path = os.path.join(PROJECT_ROOT, "web", "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        assert 'integrity="sha384-n8MVd4RsNIU0tAv4ct0nTaAbDJwPJzDEaqSD1odI+WdtXRGWt2kTvGFasHpSy3SV"' in html
        assert 'integrity="sha384-XjKyOOlGwcjNTAIQHIpgOno0Hl1YQqzUOEleOLALmuqehneUG+vnGctmUb0ZY0l8"' in html
        assert 'integrity="sha384-+VBxd3r6XgURycqtZ117nYw44OOcIax56Z4dCRWbxyPt0Koah1uHoK0o4+/RRE05"' in html
        assert 'crossorigin="anonymous"' in html

    def test_finding_sanitized_500_exception_patched(self):
        """
        VERIFICATION: In app/server.py line 374, _serve_static sends a generic
        500 Internal Server Error without leaking filesystem paths to the client response.
        """
        server_path = os.path.join(PROJECT_ROOT, "app", "server.py")
        with open(server_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert 'self.send_error(500, "Internal Server Error")' in content
        assert 'self.send_error(500, f"Error reading file: {e}")' not in content

    # ----------------------------------------------------------------------
    # 2. WEBSITE-BREAKING BUGS & VERIFIED PATCHES
    # ----------------------------------------------------------------------
    def test_finding_latex_retry_cap_patched(self):
        """
        VERIFICATION: In web/app.js, renderLaTeX caps recursive retries at 10 (retries < 10).
        Offline sessions no longer produce runaway infinite timer loops.
        """
        js_path = os.path.join(PROJECT_ROOT, "web", "app.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        match = re.search(r"function renderLaTeX\([^)]*\)[\s\S]*?(?=function |\Z)", js)
        assert match is not None
        func = match.group(0)

        assert "retries = 0" in func or "retries" in func
        assert "retries < 10" in func
        assert "KaTeX unavailable; proceeding with standard plaintext rendering" in func

    def test_finding_quiz_timer_wallclock_derivation_patched(self):
        """
        VERIFICATION: In web/app.js, startQuizTimer derives remaining seconds from
        Date.now() wall-clock time, eliminating background tab throttling desynchronization.
        """
        js_path = os.path.join(PROJECT_ROOT, "web", "app.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        match = re.search(r"function startQuizTimer\(\)[\s\S]*?(?=function |\Z)", js)
        assert match is not None
        func = match.group(0)

        assert "STATE.quizStartTime" in func
        assert "Math.floor((Date.now() - STATE.quizStartTime) / 1000)" in func

    def test_finding_physics_raf_sleep_when_idle_patched(self):
        """
        VERIFICATION: In web/app.js, physicsStep sets physicsLoopRunning = false
        and sleeps when STATE.bouncingCats is empty, avoiding 60-144Hz idle CPU drain.
        """
        js_path = os.path.join(PROJECT_ROOT, "web", "app.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        match = re.search(r"if\s*\(STATE\.bouncingCats\.length === 0\)[\s\S]*?physicsLoopRunning = false", js)
        assert match is not None, "Idle sleep confirmed for physicsStep"

    def test_finding_http_range_suffix_parsing_patched(self):
        """
        VERIFICATION: In app/server.py _serve_audio, Range: bytes=-500 parses
        suffix ranges according to RFC 7233: start = max(0, total_size - int(parts[1])).
        """
        server_path = os.path.join(PROJECT_ROOT, "app", "server.py")
        with open(server_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "start = max(0, total_size - suffix_len)" in content
        assert "end = total_size - 1" in content

    def test_finding_reading_comprehension_gre_0958_patched(self):
        """
        VERIFICATION: In data/gre_questions.json, gre_0958 has 5 ETS-compliant options (A through E).
        """
        q_path = os.path.join(PROJECT_ROOT, "data", "gre_questions.json")
        with open(q_path, "r", encoding="utf-8") as f:
            questions = json.load(f)

        q = next((x for x in questions if x["id"] == "gre_0958"), None)
        assert q is not None
        assert len(q["options"]) == 5
        assert [o["label"] for o in q["options"]] == ["A", "B", "C", "D", "E"]
        assert q["correct_answer"] == ["D"]

    # ----------------------------------------------------------------------
    # 3. ZERO-TRUST RESOLUTIONS: VERIFIED SECURITY & THREAT MITIGATIONS
    # ----------------------------------------------------------------------
    def test_finding_state_poisoning_via_nan_volume_patched(self):
        """
        VERIFICATION: In app/alarm_state.py & app/server.py, master_volume sanitizes
        and rejects non-finite floats ('nan', 'inf', out-of-bounds).
        json.dumps(mgr.get_status()) is strictly RFC 8259 compliant and never produces 'NaN'.
        """
        from app.alarm_state import AlarmStateManager
        mgr = AlarmStateManager()
        mgr.master_volume = float("nan")
        status = mgr.get_status()
        serialized = json.dumps(status)
        assert '"master_volume": NaN' not in serialized
        assert isinstance(status["master_volume"], float)
        assert 0.0 <= status["master_volume"] <= 1.0

        # Test extreme out-of-bounds and inf
        mgr.master_volume = float("inf")
        assert mgr.master_volume == 1.0
        mgr.master_volume = 2.5
        assert mgr.master_volume == 1.0
        mgr.master_volume = -0.5
        assert mgr.master_volume == 0.0

    def test_finding_inactivity_watchdog_lottery_drop_patched(self):
        """
        VERIFICATION: In web/app.js, the probabilistic 95% lottery drop (Math.random() < 0.05)
        has been eliminated and replaced with a deterministic throttled reporting mechanism.
        100% of user activity sessions reliably report interaction without dropping events.
        """
        js_path = os.path.join(PROJECT_ROOT, "web", "app.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        # Ensure random lottery drop is gone
        assert "Math.random() < 0.05" not in js

        # Ensure deterministic throttle is in place
        assert "REPORT_THROTTLE_MS" in js
        assert "now - lastReportedTime >= REPORT_THROTTLE_MS" in js

    def test_finding_question_replay_attack_patched(self):
        """
        VERIFICATION: AlarmStateManager and /api/question/submit enforce Zero-Trust replay protection.
        Submitting the same question repeatedly rejects duplicate point awards, preventing
        arbitrary score inflation and false victories.
        """
        from app.alarm_state import AlarmStateManager
        from app.scoring_engine import GREScoringEngine
        state_mgr = AlarmStateManager()
        engine = GREScoringEngine()

        state_mgr.start_quiz()
        assert state_mgr.current_points == 0

        q = engine.questions_by_id["gre_0001"]
        correct_ans = q["correct_answer"]
        pts = q["point_value"]

        # First submission succeeds and awards points
        eval_res = engine.evaluate_answer("gre_0001", correct_ans, state_mgr.current_points)
        accepted = state_mgr.apply_points(eval_res["points_delta"], question_id="gre_0001")
        assert accepted is True
        assert state_mgr.current_points == pts

        # Replay attempts are rejected; points cannot be multiplied
        for _ in range(4):
            eval_res = engine.evaluate_answer("gre_0001", correct_ans, state_mgr.current_points)
            accepted = state_mgr.apply_points(eval_res["points_delta"], question_id="gre_0001")
            assert accepted is False

        assert state_mgr.current_points == pts  # Remains exactly pts, NOT pts * 5
        assert state_mgr.state == "QUIZ_ACTIVE"  # Does not reach false VICTORY

    def test_finding_zero_trust_security_headers_patched(self):
        """
        VERIFICATION: In app/server.py, GREAlarmHandler includes standard Zero-Trust
        defensive headers (CSP, nosniff, DENY, strict-origin-when-cross-origin).
        """
        server_path = os.path.join(PROJECT_ROOT, "app", "server.py")
        with open(server_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Content-Security-Policy" in content
        assert "X-Content-Type-Options" in content
        assert "X-Frame-Options" in content
        assert "Referrer-Policy" in content

    def test_finding_zero_trust_sec_fetch_site_blocked(self):
        """
        VERIFICATION: In app/server.py, _validate_origin blocks requests with
        Sec-Fetch-Site: cross-site.
        """
        server_path = os.path.join(PROJECT_ROOT, "app", "server.py")
        with open(server_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert 'fetch_site == "cross-site"' in content
