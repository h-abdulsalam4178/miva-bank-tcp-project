from decimal import Decimal
from bank import Bank


def make(faults=()):
    bank = Bank(faults=faults)
    bank.create_user("hauwa", "Hauwa", "Musa", "Abuja", "Passw0rd1",
                     "hauwa@example.com", middle_name="Zainab")
    bank.open_account("hauwa", "A1001", "900000.00")
    bank.open_account("hauwa", "A1002", "50000.00")
    return bank


def newest_first(bank):
    token = bank.login("hauwa", "Passw0rd1")
    for amount in ["1000", "2000", "3000"]:
        bank.transfer(token, "A1001", "A1002", amount)
    amounts = [e["amount"] for e in bank.get_history(token, "A1001")]
    return amounts == [Decimal("3000.00"), Decimal("2000.00"), Decimal("1000.00")]


def latest_entry_correct(bank):
    token = bank.login("hauwa", "Passw0rd1")
    bank.transfer(token, "A1001", "A1002", "10000")
    bank.transfer(token, "A1001", "A1002", "5000")
    latest = bank.get_history(token, "A1001")[0]
    return latest["amount"] == Decimal("5000.00") and latest["fee"] == Decimal("10.00")


def pagination_correct(bank):
    token = bank.login("hauwa", "Passw0rd1")
    for amount in ["100", "200", "300", "400", "500"]:
        bank.transfer(token, "A1001", "A1002", amount)
    page2 = [e["amount"] for e in bank.get_history(token, "A1001", page=2, page_size=2)]
    return page2 == [Decimal("300.00"), Decimal("200.00")]


checks = [
    ("History is newest first", newest_first),
    ("Latest entry is correct", latest_entry_correct),
    ("Page 2 holds the right entries", pagination_correct),
]

for faults in [(), ("F13",), ("F14",)]:
    print("VERSION:", faults[0] if faults else "clean")
    for name, check in checks:
        passed = check(make(faults))
        print("    ", name, "->", "pass" if passed else "FAIL  <-- bug caught")