import json

with open("run_logs/runs.jsonl", encoding="utf-8") as file:
    runs = [json.loads(line) for line in file if line.strip()]

print("Runs recorded:", len(runs))

for number, run in enumerate(runs, start=1):
    if not run["raw_response"]:
        continue
    scores = json.loads(run["raw_response"])
    for row in scores:
        if row["test_case_id"] == "TC003":
            print("Run", number, run["time"], "->",
                  row["business_criticality"],
                  row["security_sensitivity"],
                  row["transaction_impact"],
                  row["change_relevance"],
                  row["historical_defect_exposure"])