import random

AREAS = ["Authentication", "Fund Transfer", "Payment Processing",
         "Account Management", "Transaction History"]

random.seed(2026)
recently_changed = random.sample(AREAS, 2)
past_defects = random.sample(AREAS, 2)

print("Recently changed areas:", recently_changed)
print("Areas with past defects:", past_defects)