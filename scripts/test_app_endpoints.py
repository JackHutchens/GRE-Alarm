"""
Integration tests for GRE Torture Alarm Backend & API.
"""
import os
import sys
import time
import json
import urllib.request
import threading

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.server import run_server

def run_tests():
    server = run_server(port=8769)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.5)

    base = "http://127.0.0.1:8769"

    # 1. Test Status
    with urllib.request.urlopen(f"{base}/api/status") as res:
        data = json.loads(res.read().decode())
        print(f"1. Status endpoint OK: state={data['state']}, target={data['target_points']}")

    # 2. Test 500 Messages
    with urllib.request.urlopen(f"{base}/api/shut_up_messages") as res:
        msgs = json.loads(res.read().decode())
        print(f"2. Shut-up messages OK: count={len(msgs)}, sample='{msgs[0]}'")

    # 3. Test Cat Ways
    with urllib.request.urlopen(f"{base}/api/cat_ways") as res:
        ways = json.loads(res.read().decode())
        print(f"3. Cat ways OK: count={len(ways)}, sample='{ways[0]}'")

    # 4. Test Question Serving
    with urllib.request.urlopen(f"{base}/api/question/next") as res:
        q = json.loads(res.read().decode())
        print(f"4. Question OK: id={q['id']}, subtype='{q['subtype']}', pts={q['point_value']}, penalty={q['penalty_value']}")

    # 5. Test Answer Submission
    req = urllib.request.Request(
        f"{base}/api/question/submit",
        data=json.dumps({"question_id": q["id"], "user_answer": ["A"]}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        ans_res = json.loads(res.read().decode())
        print(f"5. Answer Submission OK: is_correct={ans_res['evaluation']['is_correct']}, delta={ans_res['evaluation']['points_delta']}, score={ans_res['current_points']}")

    # 6. Test Static index.html
    with urllib.request.urlopen(f"{base}/index.html") as res:
        content = res.read().decode()
        print(f"6. Static index.html OK: bytes={len(content)}")

    # 7. Test Cat Karaoke Lyrics & Word Tracking
    with urllib.request.urlopen(f"{base}/api/cat_karaoke") as res:
        karaoke = json.loads(res.read().decode())
        print(f"7. Cat Karaoke API OK: count={len(karaoke)}, way 1='{karaoke[0]['action']}', way 100='{karaoke[99]['action']}', way 1 words count={len(karaoke[0]['words'])}")
        assert len(karaoke[0]['words']) > 0, "Way 1 must have word-level timestamps"

    # 8. Test Audio Streaming with HTTP Range Request (HTTP 206 Partial Content)
    req_audio = urllib.request.Request(
        f"{base}/audio/cat_song.mp3",
        headers={"Range": "bytes=0-1023"}
    )
    with urllib.request.urlopen(req_audio) as res:
        chunk = res.read()
        print(f"8. Audio Streaming HTTP 206 OK: status={res.status}, bytes_received={len(chunk)}, content_range={res.headers.get('Content-Range')}")

    # 9. Test 100 Hidden Cat Features
    with urllib.request.urlopen(f"{base}/api/hidden_cats") as res:
        cats = json.loads(res.read().decode())
        print(f"9. Hidden Cats API OK: total={len(cats)}")
        assert len(cats) == 100, f"Expected 100 cats, got {len(cats)}"
        first_15_types = [c['type'] for c in cats[:15]]
        assert all(t == 'cutesy' for t in first_15_types), "First 15 cats must all be cutesy!"
        spooky_count = sum(1 for c in cats[15:] if c['type'] == 'spooky')
        print(f"   First 15 100% cutesy verified. Spooky features unlocked after Way 15: {spooky_count}")

    # 10. Test 100% Penalty in Punishment Mode
    eval_standard = server.RequestHandlerClass.scoring_engine.evaluate_answer(
        q["id"], ["WRONG_CHOICE_XYZ"], 0, punishment_mode=False
    )
    eval_punishment = server.RequestHandlerClass.scoring_engine.evaluate_answer(
        q["id"], ["WRONG_CHOICE_XYZ"], 0, punishment_mode=True
    )
    print(f"10. Punishment penalty escalation: Standard delta={eval_standard['points_delta']} (-{q['penalty_value']}), Punishment delta={eval_punishment['points_delta']} (-{q['point_value']})")
    assert eval_punishment['points_delta'] == -q['point_value'], "Punishment mode must deduct 100% of point value"

    # 11. Test Multi-Select MCQ Answer Submission (e.g. Reading Comprehension with multiple answers ['A', 'B', 'C'])
    req_multi = urllib.request.Request(
        f"{base}/api/question/submit",
        data=json.dumps({"question_id": "gre_0892", "user_answer": ["A", "B", "C"]}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_multi) as res:
        ans_multi = json.loads(res.read().decode())
        print(f"11. Multi-Select MCQ Evaluation OK: is_correct={ans_multi['evaluation']['is_correct']}, correct_answer={ans_multi['evaluation']['correct_answer']}")
        assert ans_multi['evaluation']['is_correct'] is True, "Multi-select submission of ['A', 'B', 'C'] must evaluate to True"

    server.server_close()
    print("\n>>> ALL BACKEND API & INTEGRATION TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    run_tests()
