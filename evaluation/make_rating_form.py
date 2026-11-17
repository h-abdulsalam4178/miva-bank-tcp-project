import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "..", "demo_bank", "test_cases.csv")
OUT = os.path.join(HERE, "rating_form.csv")

with open(SOURCE, newline="", encoding="utf-8") as file:
    tests = list(csv.DictReader(file))

with open(OUT, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow(["test_case_id", "description", "functionality",
                     "business_criticality", "security_sensitivity",
                     "transaction_impact", "change_relevance",
                     "historical_defect_exposure"])
    for test in tests:
        writer.writerow([test["test_case_id"], test["description"],
                         test["functionality"], "", "", "", "", ""])

print("Saved", len(tests), "rows to", OUT)