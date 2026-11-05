"""
State Manager for the GRE Torture Alarm Application.

Tracks:
- Alarm schedule & arm status
- Real-time procedural audio state
- 5-Minute countdown timer (300s window to accumulate 100 points)
- Running points total (correct = +P, wrong = -P/2)
- 5-Minute inactivity watchdog (resets to full alarm if user falls back asleep)
- Cat punishment state ("100 Ways to Love a Cat" volume ramping over 30s)
"""

import time
import math
import threading
from typing import Dict, Any, Optional

QUIZ_WINDOW_SECONDS = 300.0  # 5 minutes
INACTIVITY_TIMEOUT_SECONDS = 300.0  # 5 minutes
TARGET_POINTS = 100

class AlarmStateManager:
    def __init__(self):
        self._lock = threading.RLock()
        self.state = "IDLE"  # IDLE, ALARM_RINGING, QUIZ_ACTIVE, CAT_PUNISHMENT, VICTORY
        self.alarm_time_str = "07:00"
        self.alarm_period = "AM"
        self.is_armed = False
        self.selected_model = "model6"  # Champion Model 6: Apex Felid Assault V2
        self._master_volume = 1.0

        # Quiz & Scoring
        self.current_points = 0
        self.quiz_start_time: Optional[float] = None
        self.last_interaction_time: float = time.time()
        self.questions_answered_count = 0
        self.correct_count = 0
        self.incorrect_count = 0
        self.current_question_id: Optional[str] = None
        self.seen_question_ids = []
        self.answered_question_ids = set()

        # Cat punishment tracking
        self.cat_punishment_start_time: Optional[float] = None

    @property
    def master_volume(self) -> float:
        with self._lock:
            if not isinstance(self._master_volume, (int, float)) or math.isnan(self._master_volume) or math.isinf(self._master_volume):
                self._master_volume = 1.0
            return float(self._master_volume)

    @master_volume.setter
    def master_volume(self, value: Any):
        with self._lock:
            try:
                val = float(value)
                if math.isnan(val) or math.isinf(val):
                    self._master_volume = 1.0
                else:
                    self._master_volume = max(0.0, min(1.0, val))
            except (ValueError, TypeError):
                self._master_volume = 1.0

    def record_interaction(self):
        """Called whenever the user moves mouse, types, clicks, or submits."""
        with self._lock:
            self.last_interaction_time = time.time()

    def check_watchdog(self) -> str:
        """
        Evaluates timers and watchdog.
        Returns state transition if any occurred.
        """
        with self._lock:
            now = time.time()

            # Check 5-minute inactivity watchdog during quiz or cat punishment
            if self.state in ("QUIZ_ACTIVE", "CAT_PUNISHMENT") and self.current_points < TARGET_POINTS:
                inactivity_duration = now - self.last_interaction_time
                if inactivity_duration >= INACTIVITY_TIMEOUT_SECONDS:
                    # User assumed to have fallen back asleep!
                    self.state = "ALARM_RINGING"
                    self.current_points = 0
                    self.quiz_start_time = None
                    self.cat_punishment_start_time = None
                    return "INACTIVITY_REVERT_ALARM"

            # Check 5-minute timer expiration during QUIZ_ACTIVE
            if self.state == "QUIZ_ACTIVE" and self.quiz_start_time is not None:
                elapsed = now - self.quiz_start_time
                if elapsed >= QUIZ_WINDOW_SECONDS:
                    if self.current_points >= TARGET_POINTS:
                        self.state = "VICTORY"
                        return "VICTORY"
                    else:
                        self.state = "CAT_PUNISHMENT"
                        self.cat_punishment_start_time = now
                        return "TRIGGER_CAT_PUNISHMENT"

            # Check if victory achieved during CAT_PUNISHMENT
            if self.state == "CAT_PUNISHMENT" and self.current_points >= TARGET_POINTS:
                self.state = "VICTORY"
                return "VICTORY"

            return self.state

    def trigger_alarm(self):
        """Transitions into ALARM_RINGING state."""
        with self._lock:
            self.state = "ALARM_RINGING"
            self.record_interaction()

    def start_quiz(self):
        """User clicked SHUT UP button. Silences RTG alarm, starts 5-minute timer."""
        with self._lock:
            self.state = "QUIZ_ACTIVE"
            self.current_points = 0
            self.quiz_start_time = time.time()
            self.last_interaction_time = time.time()
            self.cat_punishment_start_time = None
            self.questions_answered_count = 0
            self.correct_count = 0
            self.incorrect_count = 0
            self.current_question_id = None
            self.answered_question_ids.clear()

    def is_question_answered(self, question_id: str) -> bool:
        """Zero-Trust Replay Check: Returns True if question has already been answered in this session."""
        with self._lock:
            return question_id in self.answered_question_ids

    def record_question_answered(self, question_id: str):
        """Records question as answered to prevent replay attacks."""
        with self._lock:
            self.answered_question_ids.add(question_id)

    def apply_points(self, delta: int, question_id: Optional[str] = None) -> bool:
        """
        Applies point increment or decrement.
        If question_id is provided, enforces Zero-Trust replay protection.
        """
        with self._lock:
            if question_id is not None:
                if question_id in self.answered_question_ids:
                    return False  # Replay rejected!
                self.answered_question_ids.add(question_id)

            self.record_interaction()
            self.current_points += delta
            self.questions_answered_count += 1
            if delta > 0:
                self.correct_count += 1
            else:
                self.incorrect_count += 1

            if self.current_points >= TARGET_POINTS:
                self.state = "VICTORY"
            return True

    def disarm(self):
        """Resets the system back to IDLE."""
        with self._lock:
            self.state = "IDLE"
            self.is_armed = False
            self.quiz_start_time = None
            self.cat_punishment_start_time = None
            self.current_points = 0
            self.current_question_id = None
            self.answered_question_ids.clear()

    def get_status(self) -> Dict[str, Any]:
        """Serializes current state for frontend polling or synchronization."""
        with self._lock:
            self.check_watchdog()
            now = time.time()

            quiz_remaining = 0.0
            if self.quiz_start_time is not None:
                quiz_remaining = max(0.0, QUIZ_WINDOW_SECONDS - (now - self.quiz_start_time))

            inactivity_remaining = max(0.0, INACTIVITY_TIMEOUT_SECONDS - (now - self.last_interaction_time))

            cat_ramp_fraction = 0.0
            if self.cat_punishment_start_time is not None:
                elapsed_cat = now - self.cat_punishment_start_time
                cat_ramp_fraction = min(1.0, elapsed_cat / 30.0)

            return {
                "state": self.state,
                "alarm_time_str": self.alarm_time_str,
                "alarm_period": self.alarm_period,
                "is_armed": self.is_armed,
                "selected_model": self.selected_model,
                "master_volume": self.master_volume,
                "current_points": self.current_points,
                "target_points": TARGET_POINTS,
                "quiz_remaining_seconds": round(quiz_remaining, 1),
                "quiz_window_seconds": QUIZ_WINDOW_SECONDS,
                "inactivity_remaining_seconds": round(inactivity_remaining, 1),
                "questions_answered_count": self.questions_answered_count,
                "correct_count": self.correct_count,
                "incorrect_count": self.incorrect_count,
                "cat_ramp_fraction": round(cat_ramp_fraction, 3)
            }
