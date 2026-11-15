from tests_suite import TESTS, build_bank


def run_one(test_function, faults=()):
    try:
        test_function(build_bank(faults))
        return True
    except Exception:
        return False


for test_id, description, area, function in TESTS:
    result = "PASS" if run_one(function) else "FAIL"
    print(test_id, result, "-", description)