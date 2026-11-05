"""
Comprehensive Integration & Unit Tests for the HTTP Server and Endpoints (app/server.py).

Tests:
1. All GET API endpoints (/api/status, /api/question/next, /api/shut_up_messages, /api/cat_ways,
   /api/cat_karaoke, /api/hidden_cats)
2. All POST API endpoints (/api/interaction, /api/arm, /api/trigger, /api/shut_up,
   /api/question/submit, /api/disarm)
3. Static asset serving (/, /index.html, /styles.css, /app.js, /favicon.svg, 404 handling)
4. Audio serving (/audio/cat_song.mp3, HTTP 206 Partial Content Range streaming, audio 404)
5. Security points of failure: Directory traversal vulnerability in static and audio endpoints
6. Malformed payload handling (bad JSON, missing fields, malformed Content-Length)
7. Unhandled type annotation bug: NameError on evaluating annotations of GREAlarmHandler._send_json
"""

import os
import sys
import json
import time
import socket
import inspect
import threading
from typing import Any
import urllib.request
import urllib.error
import pytest

from app.server import run_server, GREAlarmHandler, PROJECT_ROOT


TEST_HOST = "127.0.0.1"
TEST_PORT = 8798
BASE_URL = f"http://{TEST_HOST}:{TEST_PORT}"


@pytest.fixture(scope="module")
def live_server():
    server = run_server(host=TEST_HOST, port=TEST_PORT)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.3)
    yield server
    server.server_close()


def http_get(path: str, headers: dict = None) -> tuple[int, dict, bytes]:
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, dict(res.headers), res.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def http_post(path: str, body: dict = None, raw_body: bytes = None, headers: dict = None) -> tuple[int, dict, bytes]:
    url = f"{BASE_URL}{path}"
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    if raw_body is not None:
        data = raw_body
    elif body is not None:
        data = json.dumps(body).encode("utf-8")
    else:
        data = b"{}"
    req = urllib.request.Request(url, data=data, headers=h, method="POST")
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, dict(res.headers), res.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


class TestServerEndpoints:
    def test_status_endpoint(self, live_server):
        status, headers, body = http_get("/api/status")
        assert status == 200
        assert "application/json" in headers.get("Content-Type", "")
        assert headers.get("Access-Control-Allow-Origin") != "*"
        # Test with loopback origin
        status_c, headers_c, _ = http_get("/api/status", headers={"Origin": "http://127.0.0.1:8798"})
        assert headers_c.get("Access-Control-Allow-Origin") == "http://127.0.0.1:8798"
        data = json.loads(body.decode("utf-8"))
        assert "state" in data
        assert "target_points" in data
        assert data["target_points"] == 100
        assert "alarm_time_str" in data
        assert "is_armed" in data

    def test_question_next_endpoint(self, live_server):
        status, headers, body = http_get("/api/question/next")
        assert status == 200
        q = json.loads(body.decode("utf-8"))
        assert "id" in q
        assert "question" in q
        assert "options" in q
        assert "point_value" in q
        assert "penalty_value" in q
        # Ensure answer is stripped from client
        assert "correct_answer" not in q
        assert "explanation" not in q

    def test_shut_up_messages_endpoint(self, live_server):
        status, headers, body = http_get("/api/shut_up_messages")
        assert status == 200
        msgs = json.loads(body.decode("utf-8"))
        assert isinstance(msgs, list)
        assert len(msgs) == 500
        assert all(isinstance(m, str) and len(m) > 0 for m in msgs)

    def test_cat_ways_endpoint(self, live_server):
        status, headers, body = http_get("/api/cat_ways")
        assert status == 200
        ways = json.loads(body.decode("utf-8"))
        assert isinstance(ways, list)
        assert len(ways) == 100

    def test_cat_karaoke_endpoint(self, live_server):
        status, headers, body = http_get("/api/cat_karaoke")
        assert status == 200
        karaoke = json.loads(body.decode("utf-8"))
        assert isinstance(karaoke, list)
        assert len(karaoke) == 100
        sample = karaoke[0]
        assert "way_number" in sample
        assert "start_seconds" in sample
        assert "end_seconds" in sample
        assert "words" in sample
        assert len(sample["words"]) > 0

    def test_hidden_cats_endpoint(self, live_server):
        status, headers, body = http_get("/api/hidden_cats")
        assert status == 200
        cats = json.loads(body.decode("utf-8"))
        assert isinstance(cats, list)
        assert len(cats) == 100
        # First 15 must be cutesy
        assert all(c["type"] == "cutesy" for c in cats[:15])

    def test_interaction_endpoint(self, live_server):
        status, headers, body = http_post("/api/interaction")
        assert status == 200
        data = json.loads(body.decode("utf-8"))
        assert data.get("status") == "ok"
        assert "last_active" in data

    def test_arm_endpoint(self, live_server):
        payload = {
            "time": "06:15",
            "period": "AM",
            "is_armed": True,
            "model": "model7",
            "volume": 0.75
        }
        status, headers, body = http_post("/api/arm", body=payload)
        assert status == 200
        st = json.loads(body.decode("utf-8"))
        assert st["alarm_time_str"] == "06:15"
        assert st["alarm_period"] == "AM"
        assert st["is_armed"] is True
        assert st["selected_model"] == "model7"
        assert st["master_volume"] == 0.75

    def test_trigger_and_shut_up_flow(self, live_server):
        # 1. Trigger Alarm
        status, _, body = http_post("/api/trigger")
        assert status == 200
        st = json.loads(body.decode("utf-8"))
        assert st["state"] == "ALARM_RINGING"

        # 2. Click Shut Up (initiates 5-minute quiz)
        status, _, body = http_post("/api/shut_up")
        assert status == 200
        st = json.loads(body.decode("utf-8"))
        assert st["state"] == "QUIZ_ACTIVE"
        assert st["current_points"] == 0
        assert 0 < st["quiz_remaining_seconds"] <= 300.0

    def test_submit_answer_endpoint(self, live_server):
        # Fetch question
        _, _, qbody = http_get("/api/question/next")
        q = json.loads(qbody.decode("utf-8"))
        qid = q["id"]

        # Submit answer
        payload = {"question_id": qid, "user_answer": ["A"]}
        status, _, body = http_post("/api/question/submit", body=payload)
        assert status == 200
        res = json.loads(body.decode("utf-8"))
        assert "evaluation" in res
        assert "current_points" in res
        assert "is_correct" in res["evaluation"]
        assert "correct_answer" in res["evaluation"]

    def test_disarm_endpoint(self, live_server):
        status, _, body = http_post("/api/disarm")
        assert status == 200
        st = json.loads(body.decode("utf-8"))
        assert st["state"] == "IDLE"
        assert st["is_armed"] is False

    # -------------------------------------------------------------
    # Static Assets & Audio Tests
    # -------------------------------------------------------------
    def test_static_index_html(self, live_server):
        status, headers, body = http_get("/")
        assert status == 200
        assert b"GRE TORTURE ALARM" in body

        status2, _, body2 = http_get("/index.html")
        assert status2 == 200
        assert body == body2

    def test_static_styles_css(self, live_server):
        status, headers, body = http_get("/styles.css")
        assert status == 200
        assert "text/css" in headers.get("Content-Type", "")

    def test_static_app_js(self, live_server):
        status, headers, body = http_get("/app.js")
        assert status == 200
        assert b"GRE Torture Alarm" in body

    def test_static_favicon_svg(self, live_server):
        status, headers, body = http_get("/favicon.svg")
        assert status == 200
        assert "svg" in headers.get("Content-Type", "")

    def test_static_not_found(self, live_server):
        status, _, _ = http_get("/nonexistent_page.html")
        assert status == 404

    def test_audio_full_serving(self, live_server):
        # Audio endpoint should support cat song
        status, headers, body = http_get("/audio/cat_song.mp3")
        assert status == 200
        assert "audio/mpeg" in headers.get("Content-Type", "")
        assert headers.get("Accept-Ranges") == "bytes"
        # File is ~34MB, verify first chunk length
        assert len(body) > 1000000

    def test_audio_range_partial_content(self, live_server):
        """
        Tests HTTP 206 Partial Content Range streaming.
        """
        status, headers, body = http_get("/audio/cat_song.mp3", headers={"Range": "bytes=0-1023"})
        assert status == 206
        assert len(body) == 1024
        assert "bytes 0-1023/" in headers.get("Content-Range", "")
        assert headers.get("Content-Length") == "1024"

    def test_audio_not_found(self, live_server):
        status, _, _ = http_get("/audio/nonexistent_audio_file.wav")
        assert status == 404

    def test_ambient_tracks_manifest_api(self, live_server):
        status, headers, body = http_get("/api/ambient_tracks")
        assert status == 200
        assert "application/json" in headers.get("Content-Type", "")
        data = json.loads(body.decode("utf-8"))
        assert isinstance(data, list)
        assert len(data) >= 10
        first = data[0]
        assert "title" in first
        assert "artist" in first
        assert "duration" in first
        assert "license" in first
        assert "filename" in first
        assert "focus_benefit" in first

    def test_ambient_tracks_serving_and_range(self, live_server):
        status, headers, body = http_get("/ambient_tracks/01_space_1990.mp3")
        assert status == 200
        assert "audio/mpeg" in headers.get("Content-Type", "")
        assert len(body) > 1000000

        # Partial range request
        status_range, headers_range, body_range = http_get(
            "/ambient_tracks/01_space_1990.mp3", headers={"Range": "bytes=0-2047"}
        )
        assert status_range == 206
        assert len(body_range) == 2048
        assert "bytes 0-2047/" in headers_range.get("Content-Range", "")

        # Also via /audio/ambient/
        status_alias, _, body_alias = http_get("/audio/ambient/01_space_1990.mp3")
        assert status_alias == 200
        assert len(body_alias) == len(body)

    # -------------------------------------------------------------
    # Points of Failure & Vulnerability Tests
    # -------------------------------------------------------------
    def test_point_of_failure_missing_any_type_import(self):
        """
        VERIFICATION OF FIX:
        In app/server.py: 'Any' is now properly imported from typing.
        Evaluating annotations on GREAlarmHandler._send_json succeeds without NameError.
        """
        ann = inspect.get_annotations(GREAlarmHandler._send_json)
        assert "data" in ann
        assert ann["data"] is Any

    def _read_full_socket_response(self, path: str) -> bytes:
        s = socket.socket()
        s.connect((TEST_HOST, TEST_PORT))
        req = f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n"
        s.sendall(req.encode("utf-8"))
        chunks = []
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
        s.close()
        return b"".join(chunks)

    def test_vulnerability_static_directory_traversal(self, live_server):
        """
        VERIFICATION OF FIX:
        GREAlarmHandler._serve_static canonicalizes paths via os.path.abspath
        and confirms file_path.startswith(WEB_DIR + os.sep).
        Sending a raw GET request with '/../main.py' MUST be blocked with 403 Forbidden!
        """
        raw = self._read_full_socket_response("/../main.py")
        
        # Verify fix: Server blocks traversal with 403 Forbidden and no main.py leakage
        assert b"403" in raw
        assert b"Path Traversal Prohibited" in raw
        assert b"Launcher for GRE Torture Alarm" not in raw

    def test_vulnerability_audio_directory_traversal(self, live_server):
        """
        VERIFICATION OF FIX:
        GREAlarmHandler._serve_audio sanitizes clean_path and confines to AUDIO_DIR.
        Sending '/audio/../main.py' MUST be blocked with 403 Forbidden!
        """
        raw = self._read_full_socket_response("/audio/../main.py")

        assert b"403" in raw
        assert b"Path Traversal Prohibited" in raw
        assert b"Launcher for GRE Torture Alarm" not in raw

    def test_vulnerability_ambient_directory_traversal(self, live_server):
        raw = self._read_full_socket_response("/ambient_tracks/../main.py")
        assert b"403" in raw
        assert b"Path Traversal Prohibited" in raw
        assert b"Launcher for GRE Torture Alarm" not in raw

    def test_malformed_json_body_handled_gracefully(self, live_server):
        """
        Malformed JSON body should not crash the server (returns empty body dict or 200 with fallback).
        """
        status, headers, body = http_post("/api/arm", raw_body=b"{not valid json")
        assert status == 200  # _read_json_body catches exception and returns {}

    def test_submit_nonexistent_question_id_behavior(self, live_server):
        """
        POINT OF FAILURE: Submitting nonexistent question ID returns 200 OK with error in evaluation,
        and increments incorrect_count while points_delta is 0.
        """
        payload = {"question_id": "nonexistent_id_abc", "user_answer": ["A"]}
        status, _, body = http_post("/api/question/submit", body=payload)
        assert status == 200
        res = json.loads(body.decode("utf-8"))
        assert "evaluation" in res
        assert res["evaluation"].get("error") == "Question ID not found"
