import csv
import os
from tests_suite import TESTS, build_bank

BUGS = ["F01", "F02", "F03", "F04", "F05", "F06", "F07",
        "F08", "F09", "F10", "F11", "F12", "F13", "F14"]


def passes(test_function, faults=()):
    try:
        test_function(build_bank(faults))
        return True
    except Exception:
        return False


# Safety check: every test must pass on the clean bank first.
for test_id, description, area, function in TESTS:
    if not passes(function):
        print("STOP: the clean bank fails", test_id)
        raise SystemExit

# Build the matrix: 1 means the test caught the bug, 0 means it did not.
rows = []
for test_id, description, area, function in TESTS:
    row = [test_id]
    for bug in BUGS:
        caught = 0 if passes(function, (bug,)) else 1
        row.append(caught)
    row.append(sum(row[1:]))
    rows.append(row)

# Show which tests catch each bug.
print("WHICH TESTS CATCH EACH BUG")
for position, bug in enumerate(BUGS, start=1):
    catchers = [row[0] for row in rows if row[position] == 1]
    print(bug, "->", len(catchers), "test(s):", ", ".join(catchers))

# Show tests that catch nothing.
silent = [row[0] for row in rows if row[-1] == 0]
print()
print("Tests that catch no bug:", len(silent))

# Save the matrix as a file for your report.
path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "fault_matrix.csv")
with open(path, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["test_case_id", *BUGS, "bugs_caught"])
    writer.writerows(rows)
print("Saved:", path)