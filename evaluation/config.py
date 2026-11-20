import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(HERE, "..", "prototype", "run_logs", "runs.jsonl")

PROMPT_VERSION = "v1.0"
START_TIME = "2026-11-17T09:33:00"
END_TIME = "2026-11-17T09:35:00"
EXPECTED_RUNS_COUNT = 5


def official_runs():
    """Load and return the parsed raw_response for the 5 official benchmark runs.

    Raises a ValueError if the count of matching runs is not exactly 5.
    """
    with open(LOG_PATH, encoding="utf-8") as file:
        runs = [json.loads(line) for line in file if line.strip()]

    matching = [
        json.loads(r["raw_response"])
        for r in runs
        if r.get("prompt_version") == PROMPT_VERSION
        and START_TIME <= r.get("time", "") <= END_TIME
    ]

    if len(matching) != EXPECTED_RUNS_COUNT:
        raise ValueError(
            f"Expected exactly {EXPECTED_RUNS_COUNT} official runs, but found {len(matching)}."
        )

    return matching
