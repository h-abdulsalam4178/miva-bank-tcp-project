import csv
import itertools
import json
import os
import config

HERE = os.path.dirname(os.path.abspath(__file__))
MATRIX = os.path.join(HERE, "..", "demo_bank", "fault_matrix.csv")

NAMES = ["business_criticality", "security_sensitivity", "transaction_impact",
         "change_relevance", "historical_defect_exposure"]

WEIGHT_SETS = {
    "default": [0.25, 0.20, 0.25, 0.20, 0.10],
    "A equal": [0.20, 0.20, 0.20, 0.20, 0.20],
    "B impact-heavy": [0.30, 0.20, 0.30, 0.10, 0.10],
    "C likelihood-heavy": [0.15, 0.15, 0.15, 0.35, 0.20],
}


def ranking(rows, weights):
    scored = []
    for row in rows:
        total = sum(w * row[name] for w, name in zip(weights, NAMES))
        scored.append((round(total, 6), row["test_case_id"]))
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


def kendall(a, b):
    pos_a = {t: i for i, t in enumerate(a)}
    pos_b = {t: i for i, t in enumerate(b)}
    agree = disagree = 0
    for x, y in itertools.combinations(a, 2):
        if (pos_a[x] - pos_a[y]) * (pos_b[x] - pos_b[y]) > 0:
            agree += 1
        else:
            disagree += 1
    return (agree - disagree) / (agree + disagree)


matrix = load_matrix()
runs = config.official_runs()
print("Official runs:", len(runs))

for name, weights in WEIGHT_SETS.items():
    assert abs(sum(weights) - 1.0) < 1e-9, name + " does not sum to 1"
    apfds = []
    taus = []
    for rows in runs:
        order = ranking(rows, weights)
        base = ranking(rows, WEIGHT_SETS["default"])
        apfds.append(apfd(order, matrix))
        taus.append(kendall(base, order))
    print(name, "| APFD mean", round(sum(apfds) / len(apfds), 3),
          "range", round(min(apfds), 3), "to", round(max(apfds), 3),
          "| tau vs default", round(sum(taus) / len(taus), 3))