import json
import os
import config

HERE = os.path.dirname(os.path.abspath(__file__))

WEIGHTS = {
    "business_criticality": 0.25,
    "security_sensitivity": 0.20,
    "transaction_impact": 0.25,
    "change_relevance": 0.20,
    "historical_defect_exposure": 0.10,
}

official = config.official_runs()
print("Official runs found:", len(official))


def ranking(rows):
    scored = []
    for row in rows:
        total = sum(WEIGHTS[name] * row[name] for name in WEIGHTS)
        scored.append((round(total, 6), row["test_case_id"]))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return scored


all_rankings = []
for number, run in enumerate(official, start=1):
    result = ranking(run)
    all_rankings.append([test_id for _, test_id in result])
    top = ", ".join(f"{t} ({s})" for s, t in result[:5])
    print("Run", number, "top 5:", top)

out = os.path.join(HERE, "rankings.json")
with open(out, "w", encoding="utf-8") as file:
    json.dump(all_rankings, file)
print("Saved:", out)