"""
Scoring and Evaluation Engine for GRE Alarm Application.

Analyzes the question pool and computes calibrated point values:
- Range: 16 to 44 points per question based on estimated solve time (35s-170s),
  cognitive subtype load (1-3 blanks, SE, RC passage, Quant problem solving),
  and difficulty level (easy, medium, hard).
- Incorrect answers deduct exactly half their point value (rounded).
- Provides balanced question sampling and robust answer validation.
"""

import os
import json
import random
from typing import Dict, Any, List, Optional, Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "gre_questions.json")

DIFF_OFFSET = {
    "easy": 0,
    "medium": 4,
    "hard": 8
}

SUBTYPE_OFFSET = {
    "Text Completion (1 Blank)": 0,
    "Sentence Equivalence": 2,
    "Text Completion (2 Blanks)": 4,
    "Problem Solving": 5,
    "Reading Comprehension": 6,
    "Text Completion (3 Blanks)": 8
}

class GREScoringEngine:
    def __init__(self, data_path: str = DATA_PATH):
        self.data_path = data_path
        self.questions = []
        self.questions_by_id = {}
        self._load_and_calibrate()

    def _load_and_calibrate(self):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Questions file not found: {self.data_path}")
            
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw_questions = json.load(f)

        for q in raw_questions:
            t = q.get("estimated_time_seconds", 90)
            diff = q.get("difficulty", "medium")
            subtype = q.get("subtype", "Text Completion (1 Blank)")

            diff_val = DIFF_OFFSET.get(diff, 4)
            subtype_val = SUBTYPE_OFFSET.get(subtype, 3)

            # Calibrated formula: Base 12 + time factor + difficulty + subtype complexity
            pts = int(round(12 + 0.12 * t + diff_val + subtype_val))
            penalty = int(round(pts / 2.0))

            q["point_value"] = pts
            q["penalty_value"] = penalty
            
            self.questions.append(q)
            self.questions_by_id[q["id"]] = q

    def get_question_count(self) -> int:
        return len(self.questions)

    def get_random_question(self, exclude_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Returns a randomized question, avoiding recently seen IDs if possible."""
        pool = self.questions
        if exclude_ids:
            pool = [q for q in self.questions if q["id"] not in exclude_ids]
            if not pool:  # Fallback if pool exhausted
                pool = self.questions

        selected = random.choice(pool)
        # Return a copy safe for client presentation (strip answer until evaluated)
        client_q = {
            "id": selected["id"],
            "section": selected.get("section", "Verbal Reasoning"),
            "subtype": selected.get("subtype", ""),
            "difficulty": selected.get("difficulty", "medium"),
            "estimated_time_seconds": selected.get("estimated_time_seconds", 90),
            "point_value": selected["point_value"],
            "penalty_value": selected["penalty_value"],
            "is_multi_select": selected.get("is_multi_select", False),
            "passage": selected.get("passage"),
            "question": selected.get("question", ""),
            "options": selected.get("options", [])
        }
        return client_q

    def evaluate_answer(self, question_id: str, user_answer: Any, current_points: int, punishment_mode: bool = False) -> Dict[str, Any]:
        """
        Validates user response.
        - user_answer can be string "A" or list ["A", "C"] or dict {"1": "A", "2": "D"}.
        - If punishment_mode is True (5-min timer broken), incorrect deduction is 100% of problem value.
        - Returns validation result, point adjustment, and solution details.
        """
        q = self.questions_by_id.get(question_id)
        if not q:
            return {"error": "Question ID not found"}

        expected = q.get("correct_answer")
        is_positional = bool(q and "Text Completion" in q.get("subtype", "") and isinstance(expected, (list, tuple)) and len(expected) > 1)
        is_correct = self._compare_answers(user_answer, expected, is_positional=is_positional)

        if is_correct:
            points_delta = q["point_value"]
            new_total = current_points + points_delta
        else:
            # 100% penalty in punishment mode, otherwise standard 50% penalty
            penalty = q["point_value"] if punishment_mode else q["penalty_value"]
            points_delta = -penalty
            new_total = current_points + points_delta

        return {
            "question_id": question_id,
            "is_correct": is_correct,
            "points_delta": points_delta,
            "penalty_percentage": 100 if punishment_mode else 50,
            "new_total": new_total,
            "correct_answer": expected,
            "explanation": q.get("explanation", "Standard ETS derivation."),
            "target_points": 100
        }

    def _compare_answers(self, user_ans: Any, expected_ans: Any, is_positional: bool = False) -> bool:
        """Robust comparison of user submitted answer and ground truth answer."""
        if user_ans is None or expected_ans is None:
            return False

        import re

        def extract_dict_key_num(k: Any) -> int:
            digits = re.findall(r"\d+", str(k))
            return int(digits[0]) if digits else 0

        if is_positional:
            # Positional comparison for Multi-Blank Text Completion:
            # Blank 1 must match expected[0], Blank 2 must match expected[1], etc.
            if isinstance(user_ans, dict):
                sorted_keys = sorted(user_ans.keys(), key=extract_dict_key_num)
                user_list = [str(user_ans[k]).strip().upper() for k in sorted_keys if str(user_ans[k]).strip()]
            elif isinstance(user_ans, (list, tuple)):
                user_list = [str(x).strip().upper() for x in user_ans if str(x).strip()]
            else:
                user_list = [str(user_ans).strip().upper()]

            if isinstance(expected_ans, (list, tuple)):
                exp_list = [str(x).strip().upper() for x in expected_ans if str(x).strip()]
            else:
                exp_list = [str(expected_ans).strip().upper()]

            return user_list == exp_list

        # Non-positional comparison (Sentence Equivalence, Multi-Select Problem Solving):
        # Order of selection does not matter; compare as sorted sets
        def normalize_set(ans: Any) -> List[str]:
            if isinstance(ans, str):
                cleaned = ans.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
                parts = [p.strip().upper() for p in cleaned.split(",") if p.strip()]
                return sorted(parts)
            elif isinstance(ans, (list, tuple)):
                return sorted([str(x).strip().upper() for x in ans if str(x).strip()])
            elif isinstance(ans, dict):
                return sorted([str(v).strip().upper() for k, v in ans.items() if str(v).strip()])
            return [str(ans).strip().upper()]

        return normalize_set(user_ans) == normalize_set(expected_ans)
