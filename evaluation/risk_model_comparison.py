import csv
import json
import os
import config

HERE = os.path.dirname(os.path.abspath(__file__))
MATRIX = os.path.join(HERE, "..", "demo_bank", "fault_matrix.csv")


def additive(row):
    return (0.25 * row["business_criticality"]
            + 0.20 * row["security_sensitivity"]
            + 0.25 * row["transaction_impact"]
            + 0.20 * row["change_relevance"]
            + 0.10 * row["historical_defect_exposure"])


def multiplicative(row):
    impact = (0.25 * row["business_criticality"]
              + 0.20 * row["security_sensitivity"]
              + 0.25 * row["transaction_impact"]) / 0.70
    likelihood = (0.20 * row["change_relevance"]
                  + 0.10 * row["historical_defect_exposure"]) / 0.30
    return impact * likelihood


def ranking(rows, score_function):
    scored = [(round(score_function(r), 6), r["test_case_id"]) for r in rows]
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [test_id for _, test_id in scored]


def load_matrix():
    with open(MATRIX, newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))
    return {row[0]: [int(x) for x in row[1:-1]] for row in rows[1:]}


def apfd(order, matrix):
    n = len(order)
    m = len(next(iter(matrix.values())))
    total = 0
    for bug in range(m):
        for position, test_id in enumerate(order, start=1):
            if matrix[test_id][bug] == 1:
                total += position
                break
    return 1 - total / (n * m) + 1 / (2 * n)


runs = config.official_runs()
matrix = load_matrix()
print("Official runs:", len(runs))

for name, function in [("additive (prototype)", additive),
                       ("multiplicative", multiplicative)]:
    values = [apfd(ranking(rows, function), matrix) for rows in runs]
    print(name, "| APFD mean", round(sum(values) / len(values), 3),
          "range", round(min(values), 3), "to", round(max(values), 3))