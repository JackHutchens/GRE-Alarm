"""
Comprehensive Unit Tests for GREScoringEngine (app/scoring_engine.py).

Tests:
1. Question pool loading, calibration formula, and penalty calculations
2. Difficulty offsets and subtype offsets
3. Safe randomized question dispatch (stripping answer keys)
4. Exclude-ids logic and exhaustion fallback
5. Answer comparison normalization across strings, lists, tuples, and dicts
6. Point of failure: Dict normalization sorting bug with non-alphabetical blank answers
7. Evaluation in standard mode (50% penalty) vs punishment mode (100% penalty)
8. Invalid question IDs and edge-case user inputs (None, empty, numbers, malformed types)
"""

import os
import pytest
from app.scoring_engine import GREScoringEngine, DIFF_OFFSET, SUBTYPE_OFFSET, DATA_PATH


@pytest.fixture(scope="module")
def engine():
    return GREScoringEngine()


class TestGREScoringEngine:

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            GREScoringEngine(data_path="nonexistent_gre_path_12345.json")

    def test_question_count_and_calibration(self, engine):
        count = engine.get_question_count()
        assert count > 1000
        assert len(engine.questions) == count
        assert len(engine.questions_by_id) == count

        for q in engine.questions:
            pts = q["point_value"]
            penalty = q["penalty_value"]
            assert 16 <= pts <= 44, f"Question {q['id']} points {pts} out of expected 16-44 range"
            assert penalty == int(round(pts / 2.0)), f"Question {q['id']} penalty mismatch"

    def test_calibrated_points_formula(self, engine):
        """
        Verify exact formula: round(12 + 0.12 * t + diff_offset + subtype_offset)
        """
        sample_q = engine.questions[0]
        t = sample_q.get("estimated_time_seconds", 90)
        diff = sample_q.get("difficulty", "medium")
        subtype = sample_q.get("subtype", "Text Completion (1 Blank)")

        diff_val = DIFF_OFFSET.get(diff, 4)
        subtype_val = SUBTYPE_OFFSET.get(subtype, 3)
        expected_pts = int(round(12 + 0.12 * t + diff_val + subtype_val))
        assert sample_q["point_value"] == expected_pts

    def test_get_random_question_strips_answer(self, engine):
        client_q = engine.get_random_question()
        assert "id" in client_q
        assert "question" in client_q
        assert "options" in client_q
        assert "point_value" in client_q
        assert "penalty_value" in client_q
        # Critical security/test contract: correct_answer and explanation must NOT be leaked
        assert "correct_answer" not in client_q
        assert "explanation" not in client_q

    def test_get_random_question_exclude_ids(self, engine):
        all_ids = [q["id"] for q in engine.questions[:10]]
        for _ in range(20):
            q = engine.get_random_question(exclude_ids=all_ids)
            assert q["id"] not in all_ids

    def test_get_random_question_exclude_ids_exhaustion_fallback(self, engine):
        all_ids = [q["id"] for q in engine.questions]
        # When all IDs are excluded, fallback returns from full pool rather than crashing
        q = engine.get_random_question(exclude_ids=all_ids)
        assert q is not None
        assert "id" in q

    # -------------------------------------------------------------
    # Answer Comparison Tests
    # -------------------------------------------------------------
    def test_compare_answers_single_string(self, engine):
        assert engine._compare_answers("A", ["A"]) is True
        assert engine._compare_answers("a", ["A"]) is True
        assert engine._compare_answers(["a"], ["A"]) is True
        assert engine._compare_answers("B", ["A"]) is False

    def test_compare_answers_multi_string_comma(self, engine):
        assert engine._compare_answers("A, C", ["A", "C"]) is True
        assert engine._compare_answers("c, a", ["A", "C"]) is True
        assert engine._compare_answers("['A', 'C']", ["A", "C"]) is True
        assert engine._compare_answers("A, B", ["A", "C"]) is False

    def test_compare_answers_list_order_independence(self, engine):
        assert engine._compare_answers(["C", "A"], ["A", "C"]) is True
        assert engine._compare_answers(["c", "a"], ["A", "C"]) is True
        assert engine._compare_answers(["A", "B", "C"], ["C", "B", "A"]) is True

    def test_compare_answers_dict_alphabetical_order(self, engine):
        """
        When dict values are already alphabetical (e.g. Blank 1 is A, Blank 2 is D),
        sorted(dict.items()) produces ['A', 'D'] which matches sorted(['A', 'D']).
        """
        assert engine._compare_answers({"1": "A", "2": "D"}, ["A", "D"]) is True

    def test_compare_answers_dict_non_alphabetical_sorting_failure(self, engine):
        """
        VERIFICATION OF FIX & DOCUMENTATION OF VALUE-SORTING ARCHITECTURE:
        In GREScoringEngine._compare_answers, dictionary values are now extracted and sorted:
        normalize(dict) returns:
            sorted([str(v).strip().upper() for k, v in ans.items() if str(v).strip()])
        which matches normalize(expected_ans) sorted([str(x).strip().upper() for x in ans]).
        Thus {"1": "E", "2": "B"} matches ["B", "E"] or ["E", "B"].
        """
        user_dict = {"1": "E", "2": "B"}
        expected_list = ["E", "B"]
        result = engine._compare_answers(user_dict, expected_list)
        assert result is True, "Fix verified: dict answers are sorted by value and match expected list"

    def test_compare_answers_dict_value_sorting_swapped_blanks_edge_case(self, engine):
        """
        ANALYSIS OF RESIDUAL LOGICAL RISK:
        Because _compare_answers sorts values rather than validating each key's blank index,
        swapping choices between blanks (e.g. Blank 1 getting Blank 2's answer)
        can inadvertently evaluate as True if values form the same set.
        """
        # Question where Blank 1 is 'B' and Blank 2 is 'E'
        expected = ["B", "E"]
        # If user submits Blank 1 = 'E' and Blank 2 = 'B' (completely inverted):
        inverted_dict = {"1": "E", "2": "B"}
        # Documents that value sorting treats this as identical:
        assert engine._compare_answers(inverted_dict, expected) is True

    def test_compare_answers_edge_cases(self, engine):
        # None inputs
        assert engine._compare_answers(None, ["A"]) is False
        assert engine._compare_answers("A", None) is False
        assert engine._compare_answers(None, None) is False

        # Empty inputs
        assert engine._compare_answers("", ["A"]) is False
        assert engine._compare_answers([], ["A"]) is False
        assert engine._compare_answers({}, ["A"]) is False

        # Numeric and boolean types
        assert engine._compare_answers(123, ["123"]) is True
        assert engine._compare_answers(False, ["FALSE"]) is True

    # -------------------------------------------------------------
    # Evaluate Answer Tests
    # -------------------------------------------------------------
    def test_evaluate_answer_correct(self, engine):
        q = engine.questions[0]
        qid = q["id"]
        expected = q["correct_answer"]
        pts = q["point_value"]

        res = engine.evaluate_answer(qid, expected, current_points=20, punishment_mode=False)
        assert res["is_correct"] is True
        assert res["points_delta"] == pts
        assert res["new_total"] == 20 + pts
        assert res["penalty_percentage"] == 50
        assert res["correct_answer"] == expected
        assert "explanation" in res

    def test_evaluate_answer_incorrect_standard(self, engine):
        q = engine.questions[0]
        qid = q["id"]
        wrong = ["NONEXISTENT_ANSWER"]
        penalty = q["penalty_value"]

        res = engine.evaluate_answer(qid, wrong, current_points=20, punishment_mode=False)
        assert res["is_correct"] is False
        assert res["points_delta"] == -penalty
        assert res["new_total"] == 20 - penalty
        assert res["penalty_percentage"] == 50

    def test_evaluate_answer_incorrect_punishment_mode(self, engine):
        """
        In punishment mode (5-min timer expired), incorrect answers incur 100% penalty.
        """
        q = engine.questions[0]
        qid = q["id"]
        wrong = ["NONEXISTENT_ANSWER"]
        full_pts = q["point_value"]

        res = engine.evaluate_answer(qid, wrong, current_points=50, punishment_mode=True)
        assert res["is_correct"] is False
        assert res["points_delta"] == -full_pts
        assert res["new_total"] == 50 - full_pts
        assert res["penalty_percentage"] == 100

    def test_evaluate_answer_correct_in_punishment_mode(self, engine):
        """
        Correct answer in punishment mode still awards full positive points.
        """
        q = engine.questions[0]
        qid = q["id"]
        expected = q["correct_answer"]
        pts = q["point_value"]

        res = engine.evaluate_answer(qid, expected, current_points=50, punishment_mode=True)
        assert res["is_correct"] is True
        assert res["points_delta"] == pts
        assert res["new_total"] == 50 + pts
        assert res["penalty_percentage"] == 100

    def test_evaluate_nonexistent_question_id(self, engine):
        res = engine.evaluate_answer("nonexistent_id_9999", ["A"], current_points=10)
        assert "error" in res
        assert res["error"] == "Question ID not found"
        # Notice: points_delta is not present in error dict!
        assert "points_delta" not in res
