import json

FIELDS = ["business_criticality", "security_sensitivity",
          "transaction_impact", "change_relevance",
          "historical_defect_exposure"]

with open("run_logs/runs.jsonl", encoding="utf-8") as file:
    runs = [json.loads(line) for line in file if line.strip()]


def scores_of(run):
    rows = json.loads(run["raw_response"])
    return {row["test_case_id"]: [row[f] for f in FIELDS] for row in rows}


first = scores_of(runs[-2])
second = scores_of(runs[-1])

same = 0
total = 0
for test_id in first:
    for position, (a, b) in enumerate(zip(first[test_id], second[test_id])):
        total += 1
        if a == b:
            same += 1
        else:
            print(test_id, FIELDS[position], ":", a, "->", b)

print()
print("Identical numbers:", same, "of", total)