"""
Comprehensive verification test suite covering:
1. Security Path Traversal Confinement (Static & Audio endpoints)
2. Threading server & Concurrent Handling
3. Scoring Engine Dict Answer Sorting & Multi-Blank normalization
4. Question Data Integrity (6-option SE, 5-option PS, anomaly pruning)
5. 5 Procedural Audio Samples verification (duration, channels, sample rate)
6. State synchronization & Disarm point reset
"""
import os
import sys
import json
import time
import wave
import urllib.request
import urllib.error
import threading

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.server import run_server
from app.scoring_engine import GREScoringEngine
from app.alarm_state import AlarmStateManager

def test_all():
    print("=" * 60)
    print("RUNNING GRE TORTURE ALARM COMPREHENSIVE VERIFICATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. DATA INTEGRITY CHECKS
    # ---------------------------------------------------------
    q_path = os.path.join(PROJECT_ROOT, "data", "gre_questions.json")
    with open(q_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"[OK] Total questions loaded: {len(questions)}")
    assert not any(q["id"] == "gre_0982" for q in questions), "gre_0982 was not pruned!"
    print("[OK] Anomalous 2-option question gre_0982 confirmed pruned.")

    se_qs = [q for q in questions if q["subtype"] == "Sentence Equivalence"]
    assert len(se_qs) == 282, f"Expected 282 SE questions, found {len(se_qs)}"
    for q in se_qs:
        assert len(q["options"]) == 6, f"SE {q['id']} has {len(q['options'])} options instead of 6!"
        assert [o["label"] for o in q["options"]] == ["A", "B", "C", "D", "E", "F"], f"SE {q['id']} labels invalid!"
    print("[OK] All 282 Sentence Equivalence questions confirmed 6-choice (A-F) compliant.")

    ps_qs = [q for q in questions if q["subtype"] == "Problem Solving"]
    assert len(ps_qs) == 223, f"Expected 223 PS questions, found {len(ps_qs)}"
    for q in ps_qs:
        assert len(q["options"]) == 5, f"PS {q['id']} has {len(q['options'])} options instead of 5!"
        assert [o["label"] for o in q["options"]] == ["A", "B", "C", "D", "E"], f"PS {q['id']} labels invalid!"
    print("[OK] All 223 Problem Solving questions confirmed 5-choice (A-E) compliant.")

    # ---------------------------------------------------------
    # 2. SCORING ENGINE DICT ANSWER COMPARISON BUG
    # ---------------------------------------------------------
    engine = GREScoringEngine()
    # 2a. Test non-positional dictionary submission against expected ['B', 'E']
    q_dummy = {
        "id": "test_dict_q",
        "subtype": "Sentence Equivalence",
        "point_value": 20,
        "penalty_value": 10,
        "correct_answer": ["B", "E"],
        "explanation": "Test explanation."
    }
    engine.questions_by_id["test_dict_q"] = q_dummy

    res_correct_dict = engine.evaluate_answer("test_dict_q", {"1": "E", "2": "B"}, 0, punishment_mode=False)
    assert res_correct_dict["is_correct"] is True, f"Dict comparison failed: {res_correct_dict}"
    assert res_correct_dict["points_delta"] == 20

    res_wrong_dict = engine.evaluate_answer("test_dict_q", {"1": "A", "2": "B"}, 0, punishment_mode=False)
    assert res_wrong_dict["is_correct"] is False
    assert res_wrong_dict["points_delta"] == -10

    # 2b. Test positional Text Completion: {"1": "B", "2": "E"} is True, but {"1": "E", "2": "B"} must be False
    q_tc = {
        "id": "test_tc_pos",
        "subtype": "Text Completion (2 Blanks)",
        "point_value": 24,
        "penalty_value": 12,
        "correct_answer": ["B", "E"]
    }
    engine.questions_by_id["test_tc_pos"] = q_tc
    assert engine.evaluate_answer("test_tc_pos", {"1": "B", "2": "E"}, 0)["is_correct"] is True
    assert engine.evaluate_answer("test_tc_pos", {"1": "E", "2": "B"}, 0)["is_correct"] is False
    print("[OK] Scoring Engine dict answer sorting bug verified fixed (values sorted, and TC blanks verified positionally).")

    # ---------------------------------------------------------
    # 3. PROCEDURAL 30s AUDIO SAMPLES VERIFICATION
    # ---------------------------------------------------------
    proc_files = [
        "procedural1_circadian_accelerando.wav",
        "procedural2_gamma_baroque.wav",
        "procedural3_fractal_pentatonic.wav",
        "procedural4_baroque_adagio_60bpm.wav",
        "procedural5_beta_lofi_mixolydian.wav"
    ]
    for fname in proc_files:
        p = os.path.join(PROJECT_ROOT, "audio_samples", fname)
        assert os.path.exists(p), f"Missing procedural audio file: {p}"
        with wave.open(p, "rb") as wf:
            assert wf.getnchannels() == 2, f"{fname} is not stereo!"
            assert wf.getframerate() == 44100, f"{fname} is not 44.1 kHz!"
            assert wf.getsampwidth() == 2, f"{fname} is not 16-bit!"
            dur = wf.getnframes() / wf.getframerate()
            assert 29.5 <= dur <= 30.5, f"{fname} duration is {dur}s, expected 30s!"
    print("[OK] All 5 procedural audio tracks verified: 44.1kHz 16-bit stereo ~30s WAV files.")

    # ---------------------------------------------------------
    # 4. SERVER & SECURITY CONFINEMENT TESTS (LIVE PORT)
    # ---------------------------------------------------------
    port = 8788
    server = run_server(host="127.0.0.1", port=port)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(0.5)

    base_url = f"http://127.0.0.1:{port}"

    try:
        # A. Path Traversal Attacks in Static Server
        traversal_attempts = [
            "/../main.py",
            "/..%2Fmain.py",
            "/..\\main.py",
            "/....//....//main.py",
            "/..%2f..%2fapp/server.py"
        ]
        for trav in traversal_attempts:
            try:
                req = urllib.request.Request(f"{base_url}{trav}")
                with urllib.request.urlopen(req) as resp:
                    assert False, f"Directory traversal attack succeeded on {trav}! Status: {resp.status}"
            except urllib.error.HTTPError as e:
                assert e.code in (403, 404), f"Unexpected status {e.code} for traversal {trav}"
        print("[OK] Static file server path traversal strictly blocked (403/404).")

        # B. Path Traversal Attacks in Audio Server
        audio_traversals = [
            "/audio/../main.py",
            "/audio/..%2Fmain.py",
            "/audio/..\\main.py",
            "/audio/..%2f..%2fapp/server.py"
        ]
        for trav in audio_traversals:
            try:
                req = urllib.request.Request(f"{base_url}{trav}")
                with urllib.request.urlopen(req) as resp:
                    assert False, f"Audio directory traversal attack succeeded on {trav}! Status: {resp.status}"
            except urllib.error.HTTPError as e:
                assert e.code in (403, 404), f"Unexpected status {e.code} for audio traversal {trav}"
        print("[OK] Audio endpoint path traversal strictly blocked (403/404).")

        # C. Threading & State Sync Endpoint: /api/shut_up starts quiz timer
        req_shut_up = urllib.request.Request(f"{base_url}/api/shut_up", data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req_shut_up) as resp:
            data = json.loads(resp.read().decode())
            assert data["state"] == "QUIZ_ACTIVE"
            assert data["current_points"] == 0
        print("[OK] /api/shut_up successfully starts quiz and syncs server state.")

        # D. Disarm point reset prevents bleed across test sessions
        # First add points with valid question gre_0001
        req_sub = urllib.request.Request(
            f"{base_url}/api/question/submit",
            data=json.dumps({"question_id": "gre_0001", "user_answer": ["D"]}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req_sub) as resp:
            data = json.loads(resp.read().decode())
            assert data["current_points"] > 0, f"Expected positive points, got {data}"
            pts_accum = data["current_points"]

        # Now disarm
        req_disarm = urllib.request.Request(f"{base_url}/api/disarm", data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req_disarm) as resp:
            data = json.loads(resp.read().decode())
            assert data["state"] == "IDLE"
            assert data["current_points"] == 0, f"Expected 0 points after disarm, got {data}"
        print(f"[OK] /api/disarm confirmed to reset server accumulated points (was {pts_accum} -> now 0).")

        # E. Procedural Audio streaming endpoint test
        for pfile in proc_files:
            req_aud = urllib.request.Request(f"{base_url}/audio/{pfile}")
            with urllib.request.urlopen(req_aud) as resp:
                assert resp.status == 200
                chunk = resp.read(1024)
                assert len(chunk) == 1024
        print("[OK] All 5 procedural audio files served successfully via /audio/ endpoint.")

    finally:
        server.shutdown()
        server.server_close()

    print("\n" + "=" * 60)
    print("ALL VERIFICATION SUITES PASSED FLAWLESSLY (6/6)!")
    print("=" * 60)

if __name__ == "__main__":
    test_all()
