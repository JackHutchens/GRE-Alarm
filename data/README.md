# GRE Alarm - Question Dataset

This directory contains the cleaned, deduplicated, and enriched GRE question database used by the GRE Alarm application.

## Schema Specification

Each question entry adheres to the following JSON schema:

```json
{
  "id": "gre_0001",
  "source": "gre_recall | estbook_huggingface | indiabix",
  "source_id": "original_source_identifier",
  "section": "Verbal Reasoning | Quantitative Reasoning",
  "subtype": "Text Completion | Sentence Equivalence | Reading Comprehension | Problem Solving",
  "topic": "Specific domain topic (e.g., Geometry, Probability, Integers, Vocabulary)",
  "difficulty": "easy | medium | hard",
  "estimated_time_seconds": 65,
  "fingerprint": "sha256_cryptographic_content_hash",
  "passage": "Optional academic passage string for Reading Comprehension, or null",
  "question": "Full question stem text",
  "options": [
    {
      "label": "A",
      "text": "Option text"
    }
  ],
  "correct_answer": [
    "A"
  ],
  "explanation": "Detailed pedagogical explanation or step-by-step mathematical derivation"
}
```

## Features
- **Pacing Estimation**: Cognitive and time-to-solve estimation strictly modeled on ETS examination timings, reading speed (180-220 wpm), and mathematical calculation steps.
- **De-duplication**: Exact SHA-256 fingerprint filtering and n-gram shingle Jaccard near-duplicate elimination (threshold 0.85).
