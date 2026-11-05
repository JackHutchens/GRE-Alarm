"""
Script to fix GRE Question Data Integrity:
1. Prune malformed 2-option question gre_0982.
2. Complete all 184 Problem Solving questions to standard 5 options (A-E) with plausible numeric distractors.
3. Complete all 282 Sentence Equivalence questions to standard 6 options (A-F) with GRE-level vocabulary distractors matching parts of speech.
"""
import json
import re
import random

def fix_data():
    with open("data/gre_questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Original total questions: {len(questions)}")

    # 1. Prune gre_0982
    questions = [q for q in questions if q["id"] != "gre_0982"]
    print(f"After pruning gre_0982: {len(questions)}")

    # GRE Vocabulary distractor pools by part of speech / tone
    adj_distractors = [
        "superfluous", "ephemeral", "esoteric", "equivocal", "laconic", "loquacious",
        "parsimonious", "pellucid", "recalcitrant", "tenuous", "vacuous", "zealous",
        "didactic", "disparate", "fastidious", "gregarious", "intractable", "inchoate",
        "salutary", "soporific", "specious", "strident", "taciturn", "venerable",
        "austere", "banal", "capricious", "cogent", "convoluted", "diffident",
        "dispassionate", "ebullient", "enigmatic", "erratic", "exigent", "fallacious",
        "flippant", "impecunious", "incipient", "indolent", "innocuous", "insipid",
        "intrepid", "inveterate", "judicious", "lethargic", "magnanimous", "mercurial",
        "nebulous", "obsequious", "obstinate", "ostentatious", "pedantic", "perfunctory",
        "precocious", "prosaic", "quixotic", "reticent", "sagacious", "scrupulous",
        "spurious", "stolid", "trenchant", "ubiquitous", "untenable", "vacillating",
        "vicarious", "visceral", "vituperative", "voracious", "adulterated", "beneficent"
    ]

    verb_distractors = [
        "ameliorate", "attenuate", "belie", "corroborate", "delineate", "denigrate",
        "deride", "dissemble", "disparage", "emulate", "equivocate", "exacerbate",
        "exculpate", "forestall", "foster", "gainsay", "implore", "obviate",
        "oscillate", "perpetuate", "placate", "prevaricate", "propitiate", "reproach",
        "repudiate", "rescind", "supplant", "undermine", "vacillate", "venerate",
        "vindicate", "abnegate", "bolster", "circumvent", "condone", "confound",
        "contravene", "curtail", "defame", "demur", "disseminate", "diverge",
        "elucidate", "engender", "enervate", "extenuate", "extrapolate", "impugn",
        "inculcate", "instigate", "mitigate", "mollify", "obfuscate", "palliate",
        "promulgate", "refute", "renege", "substantiate", "transgress", "usurp"
    ]

    noun_distractors = [
        "anomaly", "antipathy", "apathy", "audacity", "avarice", "banality",
        "catalyst", "chauvinism", "complaisance", "deference", "derision", "dilettante",
        "disparagement", "dogma", "duplicity", "efficacy", "enmity", "epiphany",
        "equanimity", "fidelity", "frivolity", "garrulity", "harangue", "heterodoxy",
        "hubris", "iconoclast", "impetus", "indolence", "ingenuity", "inimicality",
        "insularity", "intransigence", "magnanimity", "malfeasance", "maverick", "mendacity",
        "pariah", "pedantry", "penchant", "perfusion", "perfidy", "piety",
        "platitude", "polemic", "pragmatism", "probity", "propensity", "propriety",
        "puerility", "quandary", "rancor", "rectitude", "repudiation", "sanction",
        "scarcity", "serendipity", "stratagem", "subterfuge", "syllogism", "temerity"
    ]

    # Detect part of speech heuristically from existing options
    def get_pos(options_texts):
        joined = " ".join(options_texts).lower()
        # Verb indicators: ends in ate, ize, fy, ed, ing, or common verb prefixes
        verb_score = sum(1 for w in options_texts if w.endswith(("ate", "ize", "ify", "ed", "ing", "fy", "en")))
        adj_score = sum(1 for w in options_texts if w.endswith(("ous", "ic", "al", "able", "ible", "ive", "ful", "ant", "ent", "less")))
        noun_score = sum(1 for w in options_texts if w.endswith(("ity", "tion", "sion", "ness", "ment", "ism", "ance", "ence", "or", "er")))
        
        if verb_score >= adj_score and verb_score >= noun_score and verb_score > 0:
            return "verb"
        elif noun_score >= adj_score and noun_score >= verb_score and noun_score > 0:
            return "noun"
        else:
            return "adj"

    random.seed(42)  # Deterministic generation
    se_fixed = 0

    for q in questions:
        if q.get("subtype") == "Sentence Equivalence":
            opts = q.get("options", [])
            if len(opts) == 5:
                existing_texts = [o["text"].strip().lower() for o in opts]
                pos = get_pos([o["text"].strip().lower() for o in opts])
                pool = verb_distractors if pos == "verb" else (noun_distractors if pos == "noun" else adj_distractors)
                
                # Pick distractor not already in choices
                candidates = [w for w in pool if w.lower() not in existing_texts]
                chosen = random.choice(candidates)
                opts.append({
                    "label": "F",
                    "text": chosen
                })
                q["options"] = opts
                se_fixed += 1

    print(f"Fixed {se_fixed} Sentence Equivalence questions to 6 choices (A-F).")

    # 2. Fix 184 Problem Solving questions with 4 choices to 5 choices (A-E)
    ps_fixed = 0
    for q in questions:
        if q.get("subtype") == "Problem Solving":
            opts = q.get("options", [])
            if len(opts) == 4:
                existing_texts = [o["text"].strip() for o in opts]
                
                # Try parsing as numbers
                numeric_vals = []
                for t in existing_texts:
                    # Clean currency, percent, units
                    clean_t = re.sub(r"[^\d.-]", "", t)
                    try:
                        numeric_vals.append(float(clean_t))
                    except ValueError:
                        pass
                
                if len(numeric_vals) == 4:
                    numeric_vals.sort()
                    # Calculate step/diff
                    diffs = [numeric_vals[i+1] - numeric_vals[i] for i in range(3)]
                    avg_diff = sum(diffs) / len(diffs)
                    if avg_diff == 0:
                        avg_diff = max(1.0, numeric_vals[-1] * 0.1)

                    # Distractor candidates: step above max, step below min, or midpoint
                    is_integer = all(v.is_integer() for v in numeric_vals)
                    candidate = numeric_vals[-1] + avg_diff
                    if is_integer:
                        candidate = round(candidate)
                    else:
                        candidate = round(candidate, 2)
                    
                    # Ensure candidate doesn't match existing
                    if candidate in numeric_vals:
                        candidate = numeric_vals[-1] + 2 * avg_diff
                        if is_integer: candidate = round(candidate)

                    # Preserve formatting (e.g. if original had %, $, or integer format)
                    sample = existing_texts[0]
                    cand_str = str(int(candidate)) if is_integer and isinstance(candidate, (int, float)) and float(candidate).is_integer() else str(candidate)
                    if sample.startswith("$"):
                        cand_str = f"${cand_str}"
                    elif sample.endswith("%"):
                        cand_str = f"{cand_str}%"
                    elif "km" in sample.lower():
                        cand_str = f"{cand_str} km"
                    elif "hr" in sample.lower() or "hour" in sample.lower():
                        cand_str = f"{cand_str} hrs"
                    elif "sec" in sample.lower():
                        cand_str = f"{cand_str} sec"
                else:
                    # Non-numeric or algebraic string
                    cand_str = "None of the above"

                opts.append({
                    "label": "E",
                    "text": cand_str
                })
                q["options"] = opts
                ps_fixed += 1

    print(f"Fixed {ps_fixed} Problem Solving questions to 5 choices (A-E).")

    with open("data/gre_questions.json", "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    print("Successfully wrote updated data/gre_questions.json")

if __name__ == "__main__":
    fix_data()
