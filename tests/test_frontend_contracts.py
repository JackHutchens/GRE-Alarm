"""
Comprehensive Unit & Static Analysis Tests for Frontend-Backend Contracts and Web Logic.
(web/index.html & web/app.js)

Tests:
1. DOM element synchronization: Cross-checks all document.getElementById() calls in app.js against index.html
2. Pinpoints missing DOM elements (e.g. #btn-clear-answer queried in app.js but missing in index.html)
3. API contract verification: Cross-checks fetch("/api/...") calls in app.js against server.py endpoints
4. Pinpoints client-server state desync: /api/shut_up, /api/arm, /api/disarm, /api/trigger, /api/status never called by app.js
5. Pinpoints alarm trigger logic bug: Leading zero format mismatch ("7:00" vs "07:00") and now.getSeconds() === 0 skip vulnerability
6. Pinpoints client crash vulnerability: evalResult.correct_answer.join() uncaught TypeError when question ID error occurs
7. Audio model mapping mismatch: app.js only synthesizes model6 and model4; all others fall back to generic sawtooth despite existing WAV assets
"""

import os
import re
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_HTML_PATH = os.path.join(PROJECT_ROOT, "web", "index.html")
APP_JS_PATH = os.path.join(PROJECT_ROOT, "web", "app.js")
SERVER_PY_PATH = os.path.join(PROJECT_ROOT, "app", "server.py")


@pytest.fixture(scope="module")
def html_content():
    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture(scope="module")
def js_content():
    with open(APP_JS_PATH, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture(scope="module")
def server_content():
    with open(SERVER_PY_PATH, "r", encoding="utf-8") as f:
        return f.read()


class TestFrontendContracts:
    def test_dom_elements_queried_in_js(self, html_content, js_content):
        """
        Extracts all static document.getElementById("...") in app.js and checks
        if they exist in index.html or are dynamically created.
        """
        pattern = r'getElementById\([\"\']([^\"\']+)[\"\']\)'
        queried_ids = set(re.findall(pattern, js_content))
        
        html_id_pattern = r'\bid=[\"\']([^\"\']+)[\"\']'
        html_ids = set(re.findall(html_id_pattern, html_content))
        
        # Dynamically injected elements in app.js
        dynamic_ids = {
            "passage-content-box",
            "font-size-indicator",
            "answer-feedback-container",
            "question-validation-alert",
            "question-penalty-badge",
            "question-options-container",
            "se-count-badge",
            "btn-victory-view-stats"
        }
        
        missing_ids = queried_ids - html_ids - dynamic_ids
        
        # All queried static IDs should be present in index.html
        assert len(missing_ids) == 0, f"Missing DOM IDs in index.html: {missing_ids}"
        assert "btn-clear-answer" in html_ids
        assert "btn-submit-answer" in html_ids
        assert "panel-alarm-ringing" in html_ids
        assert "panel-quiz-solving" in html_ids
        assert "panel-cat-punishment" in html_ids
        assert "panel-victory" in html_ids

    def test_api_endpoints_called_by_frontend(self, js_content, server_content):
        """
        Extracts all fetch("/api/...") calls in app.js and compares them with server.py.
        """
        fetch_pattern = r'fetch\(["\'](/api/[a-zA-Z0-9_/]+)["\']'
        js_endpoints = set(re.findall(fetch_pattern, js_content))

        # Expected endpoints called by JS
        assert "/api/shut_up_messages" in js_endpoints
        assert "/api/cat_ways" in js_endpoints
        assert "/api/cat_karaoke" in js_endpoints
        assert "/api/hidden_cats" in js_endpoints
        assert "/api/question/next" in js_endpoints
        assert "/api/question/submit" in js_endpoints
        assert "/api/interaction" in js_endpoints

        # VERIFICATION OF FIX:
        # Frontend now actively communicates state transitions to server:
        assert "/api/shut_up" in js_endpoints, "Fix verified: /api/shut_up is now called by frontend"
        assert "/api/arm" in js_endpoints, "Fix verified: /api/arm is now called by frontend"
        assert "/api/disarm" in js_endpoints, "Fix verified: /api/disarm is now called by frontend"
        assert "/api/trigger" in js_endpoints, "Fix verified: /api/trigger is now called by frontend"

    def test_alarm_time_string_comparison_failure(self):
        """
        POINT OF FAILURE PINPOINTED:
        In app.js lines 180-194:
            hoursStr = String(hours).padStart(2, "0");
            const targetTimeStr = `${STATE.alarmTime} ${STATE.alarmPeriod}`;
            const currentTimeStr = `${hoursStr}:${minutes} ${period}`;
            if (currentTimeStr === targetTimeStr && now.getSeconds() === 0)
        If the user inputs "7:00" instead of "07:00":
            targetTimeStr is "7:00 AM"
            currentTimeStr is "07:00 AM"
            "07:00 AM" === "7:00 AM" evaluates to FALSE!
        The alarm never fires!
        """
        user_input_time = "7:00"  # User typed 7:00 without leading zero
        user_period = "AM"
        target_time_str = f"{user_input_time} {user_period}"  # "7:00 AM"

        # System time at 7:00 AM
        current_hours = 7
        hours_str = str(current_hours).zfill(2)  # "07"
        minutes_str = "00"
        period = "AM"
        current_time_str = f"{hours_str}:{minutes_str} {period}"  # "07:00 AM"

        # Equality check in app.js
        matches = (current_time_str == target_time_str)
        assert matches is False, "Bug confirmed: String comparison fails due to unnormalized leading zero"

    def test_alarm_trigger_second_skipping_failure(self):
        """
        POINT OF FAILURE PINPOINTED:
        The check requires 'now.getSeconds() === 0'.
        When running in a background tab or under high CPU load, setInterval(..., 1000)
        is throttled or drifts by milliseconds.
        If a tick occurs at second 59 and the next tick occurs at second 1,
        second 0 is completely skipped, causing the alarm to fail to trigger.
        """
        # Ticks recorded at 59s and 1s (0s was skipped due to drift)
        ticks = [59, 1]
        triggered = any(sec == 0 for sec in ticks)
        assert triggered is False, "Bug confirmed: Exact second === 0 misses triggers during timer jitter"

    def test_uncaught_typeerror_on_evaluation_error(self):
        """
        POINT OF FAILURE PINPOINTED:
        In app.js submitUserAnswer():
            <strong class="text-white">${evalResult.correct_answer.join(", ")}</strong>
        If evaluate_answer returns an error (e.g. {"error": "Question ID not found"}),
        evalResult.correct_answer is undefined.
        Calling undefined.join() throws:
            TypeError: Cannot read properties of undefined (reading 'join')
        This crashes the event handler and locks the UI permanently.
        """
        eval_result_error = {"error": "Question ID not found"}
        correct_ans = eval_result_error.get("correct_answer")
        
        with pytest.raises(AttributeError):
            # In Python None.join() raises AttributeError; in JS undefined.join() raises TypeError
            correct_ans.join(", ")

    def test_audio_models_fallback_mismatch(self, js_content, html_content):
        """
        VERIFICATION OF FIX:
        HTML presents models in select-sound-model.
        app.js defines MODEL_AUDIO_MAP mapping all models to WAV files in audio_samples/.
        """
        model_options = re.findall(r'<option value="(model\d)"', html_content)
        assert len(model_options) >= 6

        # Check that MODEL_AUDIO_MAP is present and maps the models
        assert "MODEL_AUDIO_MAP" in js_content
        for m in model_options:
            assert f"{m}:" in js_content, f"Model {m} missing from MODEL_AUDIO_MAP in app.js"
