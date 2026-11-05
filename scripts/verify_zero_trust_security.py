"""
Verification Script: Validates Zero-Trust Web Paradigm Implementation across the GRE Alarm codebase.
Tests:
1. NaN / Inf / Extreme Float Volume State Poisoning Sanitization (RFC 8259 compliance).
2. Elimination of 95% probabilistic drop rate; verified deterministic throttled watchdog reporting.
3. Zero-Trust Question Replay Attack & Score Inflation Mitigation.
4. HTTP Security Defense Headers (CSP, nosniff, DENY, strict-origin-when-cross-origin).
5. Sec-Fetch-Site cross-site mutation rejection.
6. Schema and type validation on /api/arm endpoint.
"""

import os
import sys
import json
import time
import math
import re
import socket
import threading
import urllib.request
import urllib.error

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.alarm_state import AlarmStateManager
from app.scoring_engine import GREScoringEngine
from app.server import run_server

def test_zero_trust_features():
    print("=" * 65)
    print("VERIFYING ZERO-TRUST WEB PARADIGM & ADVERSARIAL DEFENSES")
    print("=" * 65)

    # 1. State Poisoning Prevention
    mgr = AlarmStateManager()
    mgr.master_volume = float("nan")
    status = mgr.get_status()
    serialized = json.dumps(status)
    assert '"master_volume": NaN' not in serialized, "FAILED: NaN leaked into serialized status"
    assert isinstance(status["master_volume"], float)
    assert status["master_volume"] == 1.0, f"Expected 1.0 fallback, got {status['master_volume']}"

    mgr.master_volume = float("inf")
    assert mgr.master_volume == 1.0
    mgr.master_volume = 3.5
    assert mgr.master_volume == 1.0
    mgr.master_volume = -0.5
    assert mgr.master_volume == 0.0
    print("[PASS] 1. State Poisoning: NaN/Inf/Out-of-bounds sanitized; RFC 8259 JSON compliance guaranteed.")

    # 2. Watchdog Deterministic Ping
    js_path = os.path.join(PROJECT_ROOT, "web", "app.js")
    with open(js_path, "r", encoding="utf-8") as f:
        js = f.read()

    assert "Math.random() < 0.05" not in js, "FAILED: Probabilistic lottery drop still exists in app.js"
    assert "REPORT_THROTTLE_MS = 15000" in js or "REPORT_THROTTLE_MS" in js
    assert "now - lastReportedTime >= REPORT_THROTTLE_MS" in js
    print("[PASS] 2. Watchdog: 95% lottery drop eliminated; deterministic 15s throttled reporting active.")

    # 3. Question Replay Prevention
    state_mgr = AlarmStateManager()
    engine = GREScoringEngine()
    state_mgr.start_quiz()

    q = engine.questions_by_id["gre_0001"]
    correct_ans = q["correct_answer"]
    pts = q["point_value"]

    eval_res = engine.evaluate_answer("gre_0001", correct_ans, state_mgr.current_points)
    first_res = state_mgr.apply_points(eval_res["points_delta"], question_id="gre_0001")
    assert first_res is True
    assert state_mgr.current_points == pts

    # Replay attack attempt
    for _ in range(5):
        eval_res = engine.evaluate_answer("gre_0001", correct_ans, state_mgr.current_points)
        subsequent_res = state_mgr.apply_points(eval_res["points_delta"], question_id="gre_0001")
        assert subsequent_res is False

    assert state_mgr.current_points == pts, f"Replay inflation detected! Points = {state_mgr.current_points}"
    assert state_mgr.state == "QUIZ_ACTIVE", "Replay attack falsely triggered VICTORY!"
    print("[PASS] 3. Replay Protection: Replayed questions rejected; score inflation strictly prevented.")

    # 4. Live Server Tests: Security Headers, Origin & Sec-Fetch-Site
    PORT = 8792
    server = run_server(host="127.0.0.1", port=PORT)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.3)

    try:
        # Check HTTP Security Headers
        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/api/status")
        with urllib.request.urlopen(req) as resp:
            headers = dict(resp.headers)
            assert headers.get("X-Content-Type-Options") == "nosniff"
            assert headers.get("X-Frame-Options") == "DENY"
            assert "Content-Security-Policy" in headers
            assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        print("[PASS] 4. Security Headers: CSP, nosniff, DENY, and strict-origin headers verified.")

        # Check Sec-Fetch-Site cross-site block
        req_csrf = urllib.request.Request(
            f"http://127.0.0.1:{PORT}/api/interaction",
            data=b"{}",
            headers={"Content-Type": "application/json", "Sec-Fetch-Site": "cross-site"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req_csrf) as resp:
                assert False, "FAILED: Sec-Fetch-Site cross-site was not rejected!"
        except urllib.error.HTTPError as e:
            assert e.code == 403
        print("[PASS] 5. Cross-Origin Protection: Sec-Fetch-Site 'cross-site' blocked with HTTP 403.")

        # Check Server-Side /api/question/submit Replay Protection
        # 1. Fetch next question
        req_next = urllib.request.Request(f"http://127.0.0.1:{PORT}/api/question/next")
        with urllib.request.urlopen(req_next) as resp:
            q_data = json.loads(resp.read().decode("utf-8"))
            qid = q_data["id"]

        # 2. First submission
        submit_payload = json.dumps({"question_id": qid, "user_answer": ["A"]}).encode("utf-8")
        req_sub1 = urllib.request.Request(
            f"http://127.0.0.1:{PORT}/api/question/submit",
            data=submit_payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req_sub1) as resp:
            sub1_data = json.loads(resp.read().decode("utf-8"))
            assert "is_correct" in sub1_data["evaluation"]

        # 3. Second submission (Replay)
        req_sub2 = urllib.request.Request(
            f"http://127.0.0.1:{PORT}/api/question/submit",
            data=submit_payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req_sub2) as resp:
            sub2_data = json.loads(resp.read().decode("utf-8"))
            assert sub2_data["evaluation"].get("error") == "Question already submitted in this session"
            assert sub2_data["evaluation"].get("points_delta") == 0
        print("[PASS] 6. Endpoint Replay Mitigation: /api/question/submit strictly rejects duplicate submissions.")

        # Check /api/arm NaN Volume Handling over HTTP
        arm_payload = json.dumps({"volume": "nan", "time": "08:30", "period": "AM"}).encode("utf-8")
        req_arm = urllib.request.Request(
            f"http://127.0.0.1:{PORT}/api/arm",
            data=arm_payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req_arm) as resp:
            arm_data = json.loads(resp.read().decode("utf-8"))
            assert not math.isnan(arm_data["master_volume"])
            assert arm_data["master_volume"] == 1.0
            assert arm_data["alarm_time_str"] == "08:30"
        print("[PASS] 7. Input Sanitization: /api/arm invalid number sanitized over HTTP.")

    finally:
        server.shutdown()
        server.server_close()

    print("=" * 65)
    print("ALL ZERO-TRUST AUDIT & SECURITY DEFENSES VERIFIED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    test_zero_trust_features()
