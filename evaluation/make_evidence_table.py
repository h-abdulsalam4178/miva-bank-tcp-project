import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "..", "prototype", "run_logs", "runs.jsonl")
OUT = os.path.join(HERE, "evidence_table.csv")

with open(LOG, encoding="utf-8") as file:
    runs = [json.loads(line) for line in file if line.strip()]
official = [r for r in runs
            if r.get("prompt_version") == "v1.0" and r["time"] >= "2026-11-17"]
rows = json.loads(official[0]["raw_response"])

wanted = ["TC003", "TC012", "TC023"]
names = ["business_criticality", "security_sensitivity", "transaction_impact",
         "change_relevance", "historical_defect_exposure"]

with open(OUT, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow(["test", "attribute", "score", "evidence"])
    for row in rows:
        if row["test_case_id"] in wanted:
            for name in names:
                writer.writerow([row["test_case_id"], name, row[name],
                                 row.get(name + "_evidence", "")])
print("Saved", OUT)