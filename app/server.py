"""
Lightweight REST & Static Web Server for the GRE Torture Alarm Application.

Zero third-party dependencies (uses Python built-in http.server & urllib).
Serves:
- Modern dark mode frontend (HTML/CSS/JS)
- Real-time alarm state management & watchdog
- GRE question serving & calibrated scoring evaluation
- 500 tasteful shut-up messages & 100 ways to love a cat data
"""

import os
import sys
import re
import math
import json
import time
import mimetypes
import urllib.parse
from urllib.parse import urlparse, parse_qs
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict, List, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.scoring_engine import GREScoringEngine
from app.alarm_state import AlarmStateManager

WEB_DIR = os.path.join(PROJECT_ROOT, "web")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
AUDIO_DIR = os.path.join(PROJECT_ROOT, "audio_samples")
AMBIENT_DIR = os.path.join(PROJECT_ROOT, "ambient_tracks")

class GREAlarmHandler(BaseHTTPRequestHandler):
    scoring_engine = GREScoringEngine()
    state_manager = AlarmStateManager()

    def _validate_origin(self) -> bool:
        """Validate that cross-origin requests originate strictly from local loopback or matching host."""
        fetch_site = self.headers.get("Sec-Fetch-Site", "")
        if fetch_site == "cross-site":
            return False

        origin = self.headers.get("Origin", "")
        if not origin:
            return True
        parsed = urlparse(origin)
        host_hdr = self.headers.get("Host", "")
        allowed_hosts = {"127.0.0.1", "localhost"}
        if parsed.hostname in allowed_hosts or parsed.netloc == host_hdr:
            return True
        return False

    def _send_security_headers(self):
        """Send standard Zero-Trust defensive response headers."""
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Permissions-Policy", "microphone=(), camera=(), geolocation=()")
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "img-src 'self' data:; "
            "media-src 'self' blob:; "
            "connect-src 'self'"
        )
        self.send_header("Content-Security-Policy", csp)

    def _send_cors_headers(self):
        origin = self.headers.get("Origin", "")
        if origin and self._validate_origin():
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Range")

    def do_OPTIONS(self):
        if not self._validate_origin():
            self.send_error(403, "Cross-Origin Access Prohibited")
            return
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if not self._validate_origin():
            self.send_error(403, "Cross-Origin Access Prohibited")
            return
        parsed = urlparse(self.path)
        path = parsed.path

        # API Endpoints
        if path == "/api/status":
            self._send_json(self.state_manager.get_status())
            return

        elif path == "/api/question/next":
            self.state_manager.record_interaction()
            q = self.scoring_engine.get_random_question(exclude_ids=self.state_manager.seen_question_ids[-20:])
            self.state_manager.current_question_id = q["id"]
            self.state_manager.seen_question_ids.append(q["id"])
            self._send_json(q)
            return

        elif path == "/api/shut_up_messages":
            messages_file = os.path.join(DATA_DIR, "shut_up_messages.json")
            if os.path.exists(messages_file):
                with open(messages_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._send_json(data)
            else:
                self._send_json(["SHUT UP :((((("] * 500)
            return

        elif path == "/api/cat_ways":
            cat_file = os.path.join(DATA_DIR, "cat_ways.json")
            if os.path.exists(cat_file):
                with open(cat_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._send_json(data)
            else:
                self._send_json(["Love your cat unconditionally"])
            return

        elif path == "/api/cat_karaoke":
            karaoke_file = os.path.join(DATA_DIR, "cat_karaoke_lyrics.json")
            if os.path.exists(karaoke_file):
                with open(karaoke_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._send_json(data)
            else:
                self._send_json([])
            return

        elif path == "/api/hidden_cats":
            hidden_cats_file = os.path.join(DATA_DIR, "hidden_cat_features.json")
            if os.path.exists(hidden_cats_file):
                with open(hidden_cats_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._send_json(data)
            else:
                self._send_json([])
            return

        elif path == "/api/ambient_tracks":
            manifest_file = os.path.join(AMBIENT_DIR, "manifest.json")
            if os.path.exists(manifest_file):
                with open(manifest_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._send_json(data)
            else:
                self._send_json([])
            return

        # Audio Serving for "100 Ways to Love a Cat", alarm sounds, and ambient tracks
        elif path.startswith("/audio/") or path.startswith("/ambient_tracks/"):
            self._serve_audio(path)
            return

        # Static File Serving
        self._serve_static(path)

    def do_POST(self):
        if not self._validate_origin():
            self.send_error(403, "Cross-Origin Access Prohibited")
            return

        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        if path == "/api/interaction":
            self.state_manager.record_interaction()
            self._send_json({"status": "ok", "last_active": self.state_manager.last_interaction_time})
            return

        elif path == "/api/arm":
            # Zero-Trust Input Validation & Sanitization
            time_val = body.get("time")
            if time_val is not None:
                if isinstance(time_val, str) and re.match(r"^(0?[1-9]|1[0-2]):[0-5][0-9]$", time_val.strip()):
                    self.state_manager.alarm_time_str = time_val.strip()

            period_val = body.get("period")
            if period_val in ("AM", "PM"):
                self.state_manager.alarm_period = period_val

            if "is_armed" in body:
                self.state_manager.is_armed = bool(body.get("is_armed"))

            model_val = body.get("model")
            if model_val in {f"model{i}" for i in range(1, 8)}:
                self.state_manager.selected_model = model_val

            vol_val = body.get("volume")
            if vol_val is not None:
                try:
                    vf = float(vol_val)
                    if math.isnan(vf) or math.isinf(vf):
                        self.state_manager.master_volume = 1.0
                    else:
                        self.state_manager.master_volume = max(0.0, min(1.0, vf))
                except (ValueError, TypeError):
                    self.state_manager.master_volume = 1.0

            self._send_json(self.state_manager.get_status())
            return

        elif path == "/api/trigger":
            self.state_manager.trigger_alarm()
            self._send_json(self.state_manager.get_status())
            return

        elif path == "/api/shut_up":
            # Silences alarm, activates 5-minute quiz timer
            self.state_manager.start_quiz()
            self._send_json(self.state_manager.get_status())
            return

        elif path == "/api/question/submit":
            self.state_manager.record_interaction()
            qid = body.get("question_id", self.state_manager.current_question_id)
            user_ans = body.get("user_answer")

            # 1. Zero-Trust Check: Question existence validation
            if not qid or qid not in self.scoring_engine.questions_by_id:
                self._send_json({
                    "evaluation": {"error": "Question ID not found", "is_correct": False, "points_delta": 0},
                    "current_points": self.state_manager.current_points,
                    "target_points": 100,
                    "state": self.state_manager.state
                })
                return

            # 2. Zero-Trust Replay Protection: Prevent duplicate question scoring in same session
            if self.state_manager.is_question_answered(qid):
                self._send_json({
                    "evaluation": {
                        "error": "Question already submitted in this session",
                        "is_correct": False,
                        "points_delta": 0
                    },
                    "current_points": self.state_manager.current_points,
                    "target_points": 100,
                    "state": self.state_manager.state
                })
                return

            # 3. Check watchdog and determine punishment status
            self.state_manager.check_watchdog()
            is_punishment = (self.state_manager.state == "CAT_PUNISHMENT" or (
                self.state_manager.quiz_start_time is not None and 
                (time.time() - self.state_manager.quiz_start_time) >= 300.0
            ))

            result = self.scoring_engine.evaluate_answer(
                qid, user_ans, self.state_manager.current_points, punishment_mode=is_punishment
            )
            delta = result.get("points_delta", 0)

            # Atomically apply points and register question as answered
            self.state_manager.apply_points(delta, question_id=qid)

            # Invalidate current_question_id until a new question is fetched
            if self.state_manager.current_question_id == qid:
                self.state_manager.current_question_id = None

            # Return updated game state alongside solution
            resp = {
                "evaluation": result,
                "current_points": self.state_manager.current_points,
                "target_points": 100,
                "state": self.state_manager.state
            }
            self._send_json(resp)
            return

        elif path == "/api/disarm":
            self.state_manager.disarm()
            self._send_json(self.state_manager.get_status())
            return

        self.send_error(404, "Endpoint not found")

    def _read_json_body(self) -> dict:
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len > 65536:  # SEC-1: Enforce 64 KB limit to prevent body size DoS
            self.send_error(413, "Payload Too Large")
            return {}
        if content_len > 0:
            raw = self.rfile.read(content_len).decode("utf-8")
            try:
                return json.loads(raw)
            except Exception:
                return {}
        return {}

    def _send_json(self, data: Any, status: int = 200):
        try:
            payload = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self._send_security_headers()
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(payload)
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
            pass

    def _serve_audio(self, path: str):
        # Resolve target audio file and strictly confine within allowed directory to prevent directory traversal
        if path.startswith("/ambient_tracks/"):
            clean_path = urllib.parse.unquote(path[16:]).lstrip("/\\")
            base_dir = AMBIENT_DIR
        elif path.startswith("/audio/ambient/"):
            clean_path = urllib.parse.unquote(path[15:]).lstrip("/\\")
            base_dir = AMBIENT_DIR
        else:
            clean_path = urllib.parse.unquote(path[7:]).lstrip("/\\")
            base_dir = AUDIO_DIR

        dir_root = os.path.abspath(base_dir)

        if base_dir == AUDIO_DIR and clean_path in ("cat_song.mp3", "100 Ways To Love A Cat Ways 1-100.mp3"):
            file_path = os.path.abspath(os.path.join(AUDIO_DIR, "100 Ways To Love A Cat Ways 1-100.mp3"))
        else:
            file_path = os.path.abspath(os.path.join(base_dir, clean_path))

        if not (file_path == dir_root or file_path.startswith(dir_root + os.sep)):
            self.send_error(403, "Access Denied: Path Traversal Prohibited")
            return

        if not os.path.exists(file_path) or os.path.isdir(file_path):
            self.send_error(404, f"Audio File Not Found: {clean_path}")
            return

        total_size = os.path.getsize(file_path)
        range_header = self.headers.get("Range")

        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "audio/mpeg" if file_path.endswith(".mp3") else "audio/wav"

        if range_header and range_header.startswith("bytes="):
            # Parse Range: bytes=start-end (supporting RFC 7233 standard and suffix byte ranges)
            try:
                range_val = range_header[6:].strip()
                parts = range_val.split("-")
                if not parts[0] and len(parts) > 1 and parts[1]:
                    # Suffix byte range: bytes=-500 -> last 500 bytes
                    suffix_len = int(parts[1])
                    start = max(0, total_size - suffix_len)
                    end = total_size - 1
                elif parts[0] and (len(parts) == 1 or not parts[1]):
                    # Prefix byte range: bytes=500- -> from 500 to end
                    start = int(parts[0])
                    end = total_size - 1
                elif parts[0] and parts[1]:
                    # Standard range: bytes=500-999
                    start = int(parts[0])
                    end = int(parts[1])
                else:
                    start = 0
                    end = total_size - 1

                start = max(0, min(start, total_size - 1))
                end = max(start, min(end, total_size - 1))
                length = end - start + 1

                self.send_response(206)
                self.send_header("Content-Type", mime_type)
                self.send_header("Content-Range", f"bytes {start}-{end}/{total_size}")
                self.send_header("Content-Length", str(length))
                self.send_header("Accept-Ranges", "bytes")
                self._send_security_headers()
                self._send_cors_headers()
                self.end_headers()

                with open(file_path, "rb") as f:
                    f.seek(start)
                    remaining = length
                    while remaining > 0:
                        chunk_size = min(remaining, 65536)
                        data = f.read(chunk_size)
                        if not data:
                            break
                        try:
                            self.wfile.write(data)
                        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
                            break
                        remaining -= len(data)
                return
            except Exception as e:
                sys.stderr.write(f"Audio range streaming error: {e}\n")
                self.send_error(500, "Internal Server Error")
                return

        # Full file response
        self.send_response(200)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(total_size))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "public, max-age=3600")
        self._send_security_headers()
        self._send_cors_headers()
        self.end_headers()

        with open(file_path, "rb") as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                try:
                    self.wfile.write(data)
                except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
                    break

    def _serve_static(self, path: str):
        if path in ("", "/"):
            path = "/index.html"
        
        # Sanitize and strictly confine within WEB_DIR to prevent directory traversal
        rel_path = path.lstrip("/\\")
        file_path = os.path.abspath(os.path.join(WEB_DIR, rel_path))
        web_root = os.path.abspath(WEB_DIR)
        
        if not (file_path == web_root or file_path.startswith(web_root + os.sep)):
            self.send_error(403, "Access Denied: Path Traversal Prohibited")
            return

        if not os.path.exists(file_path) or os.path.isdir(file_path):
            self.send_error(404, f"File Not Found: {path}")
            return

        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self._send_security_headers()
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            sys.stderr.write(f"Static file read error: {e}\n")
            self.send_error(500, "Internal Server Error")

    def log_message(self, format, *args):
        # Mute standard noisy HTTP polling logs
        return

def run_server(host: str = "127.0.0.1", port: int = 8765):
    server = ThreadingHTTPServer((host, port), GREAlarmHandler)
    server.daemon_threads = True
    print(f"GRE Torture Alarm Server running at http://{host}:{port}/")
    return server

if __name__ == "__main__":
    server = run_server()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()
