# Prompt freeze record: version v1.0

Frozen on: 16 November 2026
Model: gemini-3.5-flash-lite (temperature left at the provider default)
Context documents (requirements, change log, defect history): frozen earlier
and committed before any LLM run.

## How the prompt developed

1. Original prompt: neutral score of 3 whenever evidence was missing.
   Problem seen: a 3 could not be told apart from real evidence; the model
   also used outside knowledge; two identical runs gave different numbers.
2. Added evidence labels (supported / inferred / missing) with the document
   reference, and an instruction not to use outside knowledge.
3. Added a scoring rubric for business criticality, security sensitivity and
   transaction impact. Two identical runs before the rubric: 124 of 150
   numbers identical. Two identical runs after the rubric: 146 of 150.

## Rules followed

- The prompt was changed only to improve consistency and agreement with the
  documents. It was never judged by APFD or by the fault-detection matrix,
  which the model never saw.
- No further prompt changes will be made. Official runs are recorded in
  run_logs/runs.jsonl with this version label.

## Known limitations

- The remaining differences cluster in tests where the bank must refuse an
  action (TC009, TC010, TC011).
- The author of the documents also built the seeded faults; the areas named
  in the change log and defect history were chosen by a fixed random seed
  (2026), not by fault location.
