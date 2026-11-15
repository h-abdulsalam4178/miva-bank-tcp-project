import csv
import os
from tests_suite import TESTS

path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "test_cases.csv")

with open(path, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["test_case_id", "description", "functionality"])
    for test_id, description, area, function in TESTS:
        writer.writerow([test_id, description, area])

print("Saved", len(TESTS), "test cases to", path)