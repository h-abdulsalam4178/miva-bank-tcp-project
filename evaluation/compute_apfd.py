import csv
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
MATRIX = os.path.join(HERE, "..", "demo_bank", "fault_matrix.csv")
RANKINGS = os.path.join(HERE, "rankings.json")


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


matrix = load_matrix()
original = list(matrix)

with open(RANKINGS, encoding="utf-8") as file:
    rankings = json.load(file)

print("Original order:", round(apfd(original, matrix), 3))

random.seed(42)
random_scores = []
for _ in range(100):
    shuffled = original[:]
    random.shuffle(shuffled)
    random_scores.append(apfd(shuffled, matrix))
print("Random order (mean of 100):",
      round(sum(random_scores) / len(random_scores), 3))

llm_scores = []
for number, order in enumerate(rankings, start=1):
    value = apfd(order, matrix)
    llm_scores.append(value)
    print("LLM-assisted run", number, ":", round(value, 3))

print("LLM-assisted mean:", round(sum(llm_scores) / len(llm_scores), 3),
      "| range:", round(min(llm_scores), 3), "to", round(max(llm_scores), 3))

def detection_rate(order, matrix, k):
    m = len(next(iter(matrix.values())))
    found = 0
    for bug in range(m):
        if any(matrix[t][bug] == 1 for t in order[:k]):
            found += 1
    return found / m


random.seed(42)
random_orders = []
for _ in range(100):
    shuffled = original[:]
    random.shuffle(shuffled)
    random_orders.append(shuffled)

print()
print("Share of the 14 bugs found after the first k tests")
for k, label in [(3, "10%"), (6, "20%"), (15, "50%")]:
    orig = detection_rate(original, matrix, k)
    rnd = sum(detection_rate(o, matrix, k) for o in random_orders) / 100
    llm = sum(detection_rate(o, matrix, k) for o in rankings) / len(rankings)
    print(label, "(", k, "tests ): original", round(orig, 2),
          "| random", round(rnd, 2), "| LLM mean", round(llm, 2))