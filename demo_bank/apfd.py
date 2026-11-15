import csv
import os
import random

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "fault_matrix.csv")


def load_matrix():
    with open(PATH, newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))
    bugs = rows[0][1:-1]
    matrix = {}
    for row in rows[1:]:
        matrix[row[0]] = [int(x) for x in row[1:-1]]
    return bugs, matrix


def apfd(order, matrix, bug_count):
    n = len(order)
    total_positions = 0
    for b in range(bug_count):
        for position, test_id in enumerate(order, start=1):
            if matrix[test_id][b] == 1:
                total_positions += position
                break
    return 1 - total_positions / (n * bug_count) + 1 / (2 * n)


# Sanity check: your Step 1 example. Expect 0.625 and 0.75.
tiny = {"T1": [0, 1], "T2": [0, 0], "T3": [1, 0], "T4": [0, 1]}
print("Step 1, order A:", apfd(["T1", "T2", "T3", "T4"], tiny, 2))
print("Step 1, order B:", apfd(["T3", "T4", "T1", "T2"], tiny, 2))
print()

bugs, matrix = load_matrix()
original = list(matrix)
print("Original order APFD:", round(apfd(original, matrix, len(bugs)), 3))

random.seed(42)
scores = []
for _ in range(100):
    shuffled = original[:]
    random.shuffle(shuffled)
    scores.append(apfd(shuffled, matrix, len(bugs)))
print("Random order APFD (mean of 100):", round(sum(scores) / len(scores), 3))
print("Random order range:", round(min(scores), 3), "to", round(max(scores), 3))