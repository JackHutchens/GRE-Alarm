"""
Comprehensive Unit Tests for AlarmStateManager (app/alarm_state.py).

Tests:
1. Initial state defaults
2. State transitions (IDLE -> ALARM_RINGING -> QUIZ_ACTIVE -> VICTORY / CAT_PUNISHMENT)
3. Scoring mechanics and points application (including edge cases: negative score, zero delta)
4. Watchdog inactivity detection (5-minute timeout reverting to ALARM_RINGING)
5. 5-minute quiz countdown window expiration
6. Cat punishment volume ramp tracking and victory during punishment
7. Disarm reset behavior
8. Serialization integrity via get_status()
"""

import time
import pytest
from app.alarm_state import AlarmStateManager, TARGET_POINTS, QUIZ_WINDOW_SECONDS, INACTIVITY_TIMEOUT_SECONDS


class TestAlarmStateManager:
    def test_initial_state_defaults(self):
        mgr = AlarmStateManager()
        assert mgr.state == "IDLE"
        assert mgr.alarm_time_str == "07:00"
        assert mgr.alarm_period == "AM"
        assert mgr.is_armed is False
        assert mgr.selected_model == "model6"
        assert mgr.master_volume == 1.0
        assert mgr.current_points == 0
        assert mgr.quiz_start_time is None
        assert mgr.questions_answered_count == 0
        assert mgr.correct_count == 0
        assert mgr.incorrect_count == 0
        assert mgr.current_question_id is None
        assert mgr.seen_question_ids == []
        assert mgr.cat_punishment_start_time is None
        assert isinstance(mgr.last_interaction_time, float)

    def test_trigger_alarm(self):
        mgr = AlarmStateManager()
        t_before = time.time()
        mgr.trigger_alarm()
        assert mgr.state == "ALARM_RINGING"
        assert mgr.last_interaction_time >= t_before

    def test_start_quiz(self):
        mgr = AlarmStateManager()
        mgr.trigger_alarm()
        mgr.current_points = 50
        mgr.correct_count = 2
        mgr.incorrect_count = 1
        mgr.questions_answered_count = 3
        
        mgr.start_quiz()
        assert mgr.state == "QUIZ_ACTIVE"
        assert mgr.current_points == 0
        assert mgr.quiz_start_time is not None
        assert mgr.correct_count == 0
        assert mgr.incorrect_count == 0
        assert mgr.questions_answered_count == 0
        assert mgr.cat_punishment_start_time is None

    def test_apply_points_positive(self):
        mgr = AlarmStateManager()
        mgr.start_quiz()
        mgr.apply_points(25)
        assert mgr.current_points == 25
        assert mgr.questions_answered_count == 1
        assert mgr.correct_count == 1
        assert mgr.incorrect_count == 0
        assert mgr.state == "QUIZ_ACTIVE"

    def test_apply_points_victory(self):
        mgr = AlarmStateManager()
        mgr.start_quiz()
        mgr.apply_points(100)
        assert mgr.current_points == 100
        assert mgr.state == "VICTORY"

    def test_apply_points_over_target(self):
        mgr = AlarmStateManager()
        mgr.start_quiz()
        mgr.apply_points(110)
        assert mgr.current_points == 110
        assert mgr.state == "VICTORY"

    def test_apply_points_negative_underflow(self):
        """
        Point of failure: Does current_points underflow below 0 when delta is negative?
        """
        mgr = AlarmStateManager()
        mgr.start_quiz()
        mgr.apply_points(-15)
        # Verify actual behavior: current_points becomes negative (-15)
        assert mgr.current_points == -15
        assert mgr.questions_answered_count == 1
        assert mgr.correct_count == 0
        assert mgr.incorrect_count == 1

    def test_apply_points_zero_delta(self):
        """
        Point of failure: delta == 0 is counted as an incorrect answer.
        """
        mgr = AlarmStateManager()
        mgr.start_quiz()
        mgr.apply_points(0)
        assert mgr.current_points == 0
        assert mgr.questions_answered_count == 1
        # In current implementation: delta > 0 is correct, else incorrect
        assert mgr.incorrect_count == 1
        assert mgr.correct_count == 0

    def test_disarm(self):
        mgr = AlarmStateManager()
        mgr.is_armed = True
        mgr.trigger_alarm()
        mgr.start_quiz()
        mgr.current_points = 45
        
        mgr.disarm()
        assert mgr.state == "IDLE"
        assert mgr.is_armed is False
        assert mgr.quiz_start_time is None
        assert mgr.cat_punishment_start_time is None
        assert mgr.current_points == 0

    def test_watchdog_inactivity_reverts_alarm(self):
        """
        Inactivity watchdog: If user has 0 interactions for >= 300 seconds during QUIZ_ACTIVE,
        the system must revert to ALARM_RINGING and reset points.
        """
        mgr = AlarmStateManager()
        mgr.start_quiz()
        mgr.current_points = 50
        
        # Simulate 301 seconds of inactivity
        mgr.last_interaction_time = time.time() - (INACTIVITY_TIMEOUT_SECONDS + 1.0)
        
        res = mgr.check_watchdog()
        assert res == "INACTIVITY_REVERT_ALARM"
        assert mgr.state == "ALARM_RINGING"
        assert mgr.current_points == 0
        assert mgr.quiz_start_time is None
        assert mgr.cat_punishment_start_time is None

    def test_watchdog_inactivity_during_cat_punishment(self):
        """
        If user falls asleep during CAT_PUNISHMENT (inactivity >= 300s), reverts to ALARM_RINGING.
        """
        mgr = AlarmStateManager()
        mgr.state = "CAT_PUNISHMENT"
        mgr.current_points = 30
        mgr.last_interaction_time = time.time() - (INACTIVITY_TIMEOUT_SECONDS + 5.0)
        
        res = mgr.check_watchdog()
        assert res == "INACTIVITY_REVERT_ALARM"
        assert mgr.state == "ALARM_RINGING"
        assert mgr.current_points == 0

    def test_watchdog_inactivity_refreshed_by_interaction(self):
        mgr = AlarmStateManager()
        mgr.start_quiz()
        # Set old interaction
        mgr.last_interaction_time = time.time() - 250.0
        # User interacts
        mgr.record_interaction()
        assert (time.time() - mgr.last_interaction_time) < 1.0
        
        res = mgr.check_watchdog()
        assert res == "QUIZ_ACTIVE"
        assert mgr.state == "QUIZ_ACTIVE"

    def test_quiz_timer_expiration_triggers_cat_punishment(self):
        """
        When 5-minute quiz window expires and points < 100, transitions to CAT_PUNISHMENT.
        """
        mgr = AlarmStateManager()
        mgr.start_quiz()
        mgr.current_points = 80
        # Simulate 301s elapsed since quiz start, but user was active 5 seconds ago
        mgr.quiz_start_time = time.time() - (QUIZ_WINDOW_SECONDS + 1.0)
        mgr.last_interaction_time = time.time() - 5.0
        
        res = mgr.check_watchdog()
        assert res == "TRIGGER_CAT_PUNISHMENT"
        assert mgr.state == "CAT_PUNISHMENT"
        assert mgr.cat_punishment_start_time is not None

    def test_quiz_timer_expiration_with_target_points_is_victory(self):
        """
        If current_points >= TARGET_POINTS when timer expires, state is VICTORY.
        """
        mgr = AlarmStateManager()
        mgr.start_quiz()
        mgr.current_points = 100
        mgr.quiz_start_time = time.time() - (QUIZ_WINDOW_SECONDS + 1.0)
        mgr.last_interaction_time = time.time() - 5.0
        
        res = mgr.check_watchdog()
        assert res == "VICTORY"
        assert mgr.state == "VICTORY"

    def test_cat_punishment_victory(self):
        """
        During CAT_PUNISHMENT, achieving TARGET_POINTS transitions to VICTORY.
        """
        mgr = AlarmStateManager()
        mgr.state = "CAT_PUNISHMENT"
        mgr.current_points = 90
        mgr.last_interaction_time = time.time()
        
        # Apply 15 points
        mgr.apply_points(15)
        assert mgr.current_points == 105
        assert mgr.state == "VICTORY"
        
        res = mgr.check_watchdog()
        assert res == "VICTORY"

    def test_get_status_serialization(self):
        mgr = AlarmStateManager()
        mgr.is_armed = True
        mgr.alarm_time_str = "06:30"
        mgr.alarm_period = "AM"
        mgr.master_volume = 0.9
        mgr.start_quiz()
        mgr.apply_points(25)
        
        status = mgr.get_status()
        assert status["state"] == "QUIZ_ACTIVE"
        assert status["alarm_time_str"] == "06:30"
        assert status["alarm_period"] == "AM"
        assert status["is_armed"] is True
        assert status["selected_model"] == "model6"
        assert status["master_volume"] == 0.9
        assert status["current_points"] == 25
        assert status["target_points"] == 100
        assert 0.0 < status["quiz_remaining_seconds"] <= 300.0
        assert status["quiz_window_seconds"] == 300.0
        assert 0.0 < status["inactivity_remaining_seconds"] <= 300.0
        assert status["questions_answered_count"] == 1
        assert status["correct_count"] == 1
        assert status["incorrect_count"] == 0
        assert status["cat_ramp_fraction"] == 0.0

    def test_cat_ramp_fraction_calculation(self):
        mgr = AlarmStateManager()
        mgr.state = "CAT_PUNISHMENT"
        mgr.cat_punishment_start_time = time.time() - 15.0  # 15s elapsed out of 30s
        
        status = mgr.get_status()
        assert 0.45 <= status["cat_ramp_fraction"] <= 0.55
        
        # After 35s, ramp fraction caps at 1.0
        mgr.cat_punishment_start_time = time.time() - 35.0
        status = mgr.get_status()
        assert status["cat_ramp_fraction"] == 1.0
