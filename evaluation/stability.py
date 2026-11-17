import itertools
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "rankings.json"), encoding="utf-8") as file:
    rankings = json.load(file)


def kendall(a, b):
    pos_a = {test: i for i, test in enumerate(a)}
    pos_b = {test: i for i, test in enumerate(b)}
    agree = 0
    disagree = 0
    for x, y in itertools.combinations(a, 2):
        direction = (pos_a[x] - pos_a[y]) * (pos_b[x] - pos_b[y])
        if direction > 0:
            agree += 1
        else:
            disagree += 1
    return (agree - disagree) / (agree + disagree)


values = []
for i, j in itertools.combinations(range(len(rankings)), 2):
    tau = kendall(rankings[i], rankings[j])
    values.append(tau)
    print("Run", i + 1, "vs run", j + 1, ":", round(tau, 3))

print()
print("Mean tau:", round(sum(values) / len(values), 3),
      "| range:", round(min(values), 3), "to", round(max(values), 3))