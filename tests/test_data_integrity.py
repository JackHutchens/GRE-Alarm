"""
Comprehensive Unit Tests for Data Integrity and Question Datasets (data/*).

Validates:
1. data/gre_questions.json (1,173 ETS-calibrated questions across 6 subtypes)
2. Question schemas, unique identifiers, option label consistency, answer mappings
3. Subtype-specific contracts (TC 1/2/3 blanks, SE exact 2 choices, RC passages, Quant)
4. Absence of corrupted glyphs (e.g. Unicode replacement character \\ufffd)
5. data/shut_up_messages.json (500 desperate messages)
6. data/cat_ways.json (100 cat care instructions)
7. data/cat_karaoke_lyrics.json (100 aligned lyrics with word-level timestamps)
8. data/hidden_cat_features.json (100 feline collectibles, first 15 strictly cutesy)
"""

import os
import json
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")


@pytest.fixture(scope="module")
def questions_data():
    path = os.path.join(DATA_DIR, "gre_questions.json")
    assert os.path.exists(path), f"File not found: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="module")
def messages_data():
    path = os.path.join(DATA_DIR, "shut_up_messages.json")
    assert os.path.exists(path), f"File not found: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="module")
def cat_ways_data():
    path = os.path.join(DATA_DIR, "cat_ways.json")
    assert os.path.exists(path), f"File not found: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="module")
def karaoke_data():
    path = os.path.join(DATA_DIR, "cat_karaoke_lyrics.json")
    assert os.path.exists(path), f"File not found: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="module")
def hidden_cats_data():
    path = os.path.join(DATA_DIR, "hidden_cat_features.json")
    assert os.path.exists(path), f"File not found: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestDataIntegrity:

    # -------------------------------------------------------------
    # GRE Questions Validation
    # -------------------------------------------------------------
    def test_gre_questions_count_and_uniqueness(self, questions_data):
        # 1,172 questions after pruning the anomalous 2-option question gre_0982
        assert len(questions_data) == 1172
        ids = [q["id"] for q in questions_data]
        assert len(ids) == len(set(ids)), "Duplicate question IDs detected!"
        assert not any(q["id"] == "gre_0982" for q in questions_data), "gre_0982 should have been pruned"

    def test_gre_questions_required_fields(self, questions_data):
        required = ["id", "section", "subtype", "difficulty", "question", "options", "correct_answer"]
        for idx, q in enumerate(questions_data):
            for field in required:
                assert field in q, f"Question at index {idx} (ID: {q.get('id')}) missing '{field}'"
            assert isinstance(q["options"], list) and len(q["options"]) > 0
            assert isinstance(q["correct_answer"], list) and len(q["correct_answer"]) > 0

    def test_gre_questions_valid_sections_and_difficulties(self, questions_data):
        valid_sections = {"Verbal Reasoning", "Quantitative Reasoning"}
        valid_diffs = {"easy", "medium", "hard"}
        valid_subtypes = {
            "Text Completion (1 Blank)",
            "Text Completion (2 Blanks)",
            "Text Completion (3 Blanks)",
            "Sentence Equivalence",
            "Reading Comprehension",
            "Problem Solving"
        }

        for q in questions_data:
            assert q["section"] in valid_sections, f"Invalid section {q['section']} in {q['id']}"
            assert q["difficulty"] in valid_diffs, f"Invalid difficulty {q['difficulty']} in {q['id']}"
            assert q["subtype"] in valid_subtypes, f"Invalid subtype {q['subtype']} in {q['id']}"

    def test_gre_questions_options_and_answer_mappings(self, questions_data):
        """
        Ensures all answers exist in options, and no option has empty text or label.
        """
        for q in questions_data:
            qid = q["id"]
            opts = q["options"]
            labels = set()
            for opt in opts:
                assert "label" in opt and len(opt["label"]) > 0, f"Malformed option label in {qid}"
                assert "text" in opt and len(opt["text"].strip()) > 0, f"Empty option text in {qid}: {opt}"
                labels.add(opt["label"])

            for ans in q["correct_answer"]:
                assert ans in labels, f"Answer '{ans}' not found among options {labels} in question {qid}"

    def test_gre_questions_subtype_specific_constraints(self, questions_data):
        for q in questions_data:
            qid = q["id"]
            subtype = q["subtype"]
            ca = q["correct_answer"]

            if subtype == "Sentence Equivalence":
                assert len(ca) == 2, f"Sentence Equivalence {qid} must have exactly 2 answers, got {ca}"
                assert q.get("is_multi_select") is True, f"SE {qid} must have is_multi_select=True"

            elif subtype == "Text Completion (1 Blank)":
                assert len(ca) == 1, f"TC 1 Blank {qid} must have exactly 1 answer, got {ca}"
                assert len(q["options"]) == 5, f"TC 1 Blank {qid} standard has 5 options, got {len(q['options'])}"

            elif subtype == "Text Completion (2 Blanks)":
                assert len(ca) == 2, f"TC 2 Blanks {qid} must have exactly 2 answers, got {ca}"
                assert len(q["options"]) == 6, f"TC 2 Blanks {qid} has 6 options (3 per blank), got {len(q['options'])}"
                blanks = [o.get("blank") for o in q["options"]]
                assert blanks.count(1) == 3 and blanks.count(2) == 3

            elif subtype == "Text Completion (3 Blanks)":
                assert len(ca) == 3, f"TC 3 Blanks {qid} must have exactly 3 answers, got {ca}"
                assert len(q["options"]) == 9, f"TC 3 Blanks {qid} has 9 options (3 per blank), got {len(q['options'])}"
                blanks = [o.get("blank") for o in q["options"]]
                assert blanks.count(1) == 3 and blanks.count(2) == 3 and blanks.count(3) == 3

            elif subtype == "Reading Comprehension":
                assert "passage" in q and q["passage"] is not None
                assert len(q["passage"].strip()) > 20, f"RC question {qid} has missing/empty passage"

    def test_sentence_equivalence_six_options_verification(self, questions_data):
        """
        VERIFICATION OF FIX:
        Official ETS GRE Sentence Equivalence questions ALWAYS contain exactly 6 options (A through F).
        All 282 Sentence Equivalence questions must now have exactly 6 valid options labeled A-F.
        """
        se_questions = [q for q in questions_data if q["subtype"] == "Sentence Equivalence"]
        assert len(se_questions) == 282
        for q in se_questions:
            assert len(q["options"]) == 6, f"Expected 6 SE options for {q['id']}, got {len(q['options'])}"
            labels = [o["label"] for o in q["options"]]
            assert labels == ["A", "B", "C", "D", "E", "F"], f"Invalid labels {labels} for {q['id']}"

    def test_quant_problem_solving_five_options_verification(self, questions_data):
        """
        VERIFICATION OF FIX:
        Official ETS GRE Quant Problem Solving questions have 5 options (A through E).
        All 223 Problem Solving questions must now have exactly 5 options labeled A-E.
        """
        ps_questions = [q for q in questions_data if q["subtype"] == "Problem Solving"]
        assert len(ps_questions) == 223
        for q in ps_questions:
            assert len(q["options"]) == 5, f"Expected 5 PS options for {q['id']}, got {len(q['options'])}"
            labels = [o["label"] for o in q["options"]]
            assert labels == ["A", "B", "C", "D", "E"], f"Invalid labels {labels} for {q['id']}"

    def test_gre_questions_no_corrupted_characters(self, questions_data):
        """
        Verify no unicode replacement characters (\ufffd) exist in questions, passages, or options.
        """
        for q in questions_data:
            qid = q["id"]
            assert "\ufffd" not in q.get("question", ""), f"Corrupted character in question {qid}"
            assert "\ufffd" not in (q.get("passage") or ""), f"Corrupted character in passage {qid}"
            for opt in q.get("options", []):
                assert "\ufffd" not in opt.get("text", ""), f"Corrupted character in option of {qid}"

    # -------------------------------------------------------------
    # Auxiliary Data Files Validation
    # -------------------------------------------------------------
    def test_shut_up_messages(self, messages_data):
        assert len(messages_data) == 500
        assert all(isinstance(m, str) and len(m.strip()) > 0 for m in messages_data)
        # Ensure high diversity (at least 350 distinct messages)
        assert len(set(messages_data)) >= 350

    def test_cat_ways(self, cat_ways_data):
        assert len(cat_ways_data) == 100
        assert all(isinstance(w, str) and len(w.strip()) > 0 for w in cat_ways_data)
        assert len(set(cat_ways_data)) == 100, "Cat ways should all be unique"

    def test_cat_karaoke_lyrics(self, karaoke_data):
        assert len(karaoke_data) == 100
        prev_end = 0.0
        for item in karaoke_data:
            assert "way_number" in item
            assert "start_seconds" in item
            assert "end_seconds" in item
            assert "action_start_seconds" in item
            assert "action_end_seconds" in item
            assert "words" in item
            assert item["start_seconds"] <= item["action_start_seconds"]
            assert item["action_start_seconds"] <= item["action_end_seconds"]
            assert item["action_end_seconds"] <= item["end_seconds"]
            assert item["start_seconds"] >= prev_end - 1.0  # Sequential progression
            prev_end = item["start_seconds"]

    def test_hidden_cat_features(self, hidden_cats_data):
        assert len(hidden_cats_data) == 100
        for idx, cat in enumerate(hidden_cats_data):
            assert cat["way_unlock"] == idx + 1
            assert "name" in cat and len(cat["name"]) > 0
            assert "type" in cat and cat["type"] in ("cutesy", "spooky")
            assert "icon" in cat and len(cat["icon"]) > 0
            assert "description" in cat and len(cat["description"]) > 0

        # First 15 must be cutesy (core product contract)
        first_15 = [c["type"] for c in hidden_cats_data[:15]]
        assert all(t == "cutesy" for t in first_15)

        # Spooky unlocked after Way 15
        spooky_count = sum(1 for c in hidden_cats_data[15:] if c["type"] == "spooky")
        assert spooky_count > 0, "Spooky felines must be present after Way 15"
