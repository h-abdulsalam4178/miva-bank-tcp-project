from decimal import Decimal
from bank import Bank, BankError


def build_bank(faults=()):
    bank = Bank(faults=faults)
    bank.create_user("hauwa", "Hauwa", "Musa", "Abuja", "Passw0rd1",
                     "hauwa@example.com", middle_name="Zainab")
    bank.create_user("khadijah", "Khadijah", "Bello", "Kwara", "Secure#99",
                     "khadijah@example.com")
    bank.open_account("hauwa", "A1001", "900000.00")
    bank.open_account("hauwa", "A1002", "50000.00")
    bank.open_account("khadijah", "B2001", "10000.00")
    bank.add_merchant("MERCH01")
    return bank


def expect_error(action):
    try:
        action()
    except BankError:
        return
    raise AssertionError("The bank should have refused this, but it did not")


def hauwa_login(bank):
    return bank.login("hauwa", "Passw0rd1")


def tc001(bank):
    token = hauwa_login(bank)
    assert token
    assert bank.get_balance(token, "A1001") == Decimal("900000.00")


def tc002(bank):
    expect_error(lambda: bank.login("hauwa", "WrongPass1"))


def tc003(bank):
    for _ in range(3):
        expect_error(lambda: bank.login("hauwa", "WrongPass1"))
    expect_error(lambda: bank.login("hauwa", "Passw0rd1"))


def tc004(bank):
    expect_error(lambda: bank.login("hauwa", "bad1"))
    expect_error(lambda: bank.login("hauwa", "bad2"))
    hauwa_login(bank)
    for _ in range(2):
        try:
            bank.login("hauwa", "bad3")
        except BankError:
            pass
    hauwa_login(bank)


def tc005(bank):
    token = hauwa_login(bank)
    bank.logout(token)
    expect_error(lambda: bank.get_balance(token, "A1001"))


def tc006(bank):
    expect_error(lambda: bank.login("nobody", "Passw0rd1"))


def khadijah_login(bank):
    return bank.login("khadijah", "Secure#99")


def tc007(bank):
    token = hauwa_login(bank)
    bank.transfer(token, "A1001", "A1002", "10000")
    assert bank.get_balance(token, "A1001") == Decimal("889975.00")
    assert bank.get_balance(token, "A1002") == Decimal("60000.00")


def tc008(bank):
    token = hauwa_login(bank)
    bank.transfer(token, "A1001", "B2001", "5000")
    assert bank.get_balance(token, "A1001") == Decimal("894990.00")
    assert bank.get_balance(khadijah_login(bank), "B2001") == Decimal("15000.00")


def tc009(bank):
    token = hauwa_login(bank)
    expect_error(lambda: bank.transfer(token, "A1001", "A1002", "0"))


def tc010(bank):
    token = hauwa_login(bank)
    expect_error(lambda: bank.transfer(token, "A1001", "A1002", "-500"))


def tc011(bank):
    token = khadijah_login(bank)
    expect_error(lambda: bank.transfer(token, "A1001", "B2001", "1000"))


def tc012(bank):
    token = khadijah_login(bank)
    expect_error(lambda: bank.transfer(token, "B2001", "A1001", "10000"))


def tc013(bank):
    token = hauwa_login(bank)
    bank.transfer(token, "A1001", "B2001", "300000")
    expect_error(lambda: bank.transfer(token, "A1001", "B2001", "300000"))
    bank.advance_day()
    bank.transfer(token, "A1001", "B2001", "300000")

def tc014(bank):
    token = hauwa_login(bank)
    bank.pay(token, "A1001", "MERCH01", "20000", "INV-001")
    assert bank.get_balance(token, "A1001") == Decimal("879700.00")
    assert bank.merchants["MERCH01"]["balance"] == Decimal("20000.00")


def tc015(bank):
    token = hauwa_login(bank)
    bank.pay(token, "A1001", "MERCH01", "12345.67", "INV-002")
    assert bank.get_balance(token, "A1001") == Decimal("887469.14")


def tc016(bank):
    token = hauwa_login(bank)
    bank.pay(token, "A1001", "MERCH01", "1000", "DUP-1")
    expect_error(lambda: bank.pay(token, "A1001", "MERCH01", "1000", "DUP-1"))


def tc017(bank):
    token = hauwa_login(bank)
    bank.pay(token, "A1001", "MERCH01", "200000", "LIM-1")
    assert bank.get_balance(token, "A1001") == Decimal("698000.00")


def tc018(bank):
    token = hauwa_login(bank)
    expect_error(lambda: bank.pay(token, "A1001", "MERCH01", "200000.01", "LIM-2"))


def tc019(bank):
    token = khadijah_login(bank)
    expect_error(lambda: bank.pay(token, "A1001", "MERCH01", "1000", "OWN-1"))

def tc020(bank):
    token = hauwa_login(bank)
    bank.change_password(token, "Passw0rd1", "NewPassw0rd2")
    bank.logout(token)
    bank.login("hauwa", "NewPassw0rd2")
    expect_error(lambda: bank.login("hauwa", "Passw0rd1"))


def tc021(bank):
    token = hauwa_login(bank)
    expect_error(lambda: bank.change_password(token, "NotMyOld1", "NewPassw0rd2"))


def tc022(bank):
    token = hauwa_login(bank)
    expect_error(lambda: bank.change_password(token, "Passw0rd1", "Abc1234"))


def tc023(bank):
    token = hauwa_login(bank)
    bank.update_email(token, "hauwa.musa@example.com")
    assert bank.get_profile(token)["email"] == "hauwa.musa@example.com"


def tc024(bank):
    token = hauwa_login(bank)
    expect_error(lambda: bank.update_email(token, "not-an-email"))
    assert bank.get_profile(token)["email"] == "hauwa@example.com"


def tc025(bank):
    token = khadijah_login(bank)
    expect_error(lambda: bank.get_balance(token, "A1001"))

def tc026(bank):
    token = hauwa_login(bank)
    for amount in ["1000", "2000", "3000"]:
        bank.transfer(token, "A1001", "A1002", amount)
    amounts = [e["amount"] for e in bank.get_history(token, "A1001")]
    assert amounts == [Decimal("3000.00"), Decimal("2000.00"), Decimal("1000.00")]


def tc027(bank):
    token = hauwa_login(bank)
    bank.transfer(token, "A1001", "A1002", "10000")
    bank.transfer(token, "A1001", "A1002", "5000")
    latest = bank.get_history(token, "A1001")[0]
    assert latest["type"] == "TRANSFER_OUT"
    assert latest["amount"] == Decimal("5000.00")
    assert latest["fee"] == Decimal("10.00")
    assert latest["counterparty"] == "A1002"
    incoming = bank.get_history(token, "A1002")[0]
    assert incoming["type"] == "TRANSFER_IN"
    assert incoming["fee"] == Decimal("0.00")


def tc028(bank):
    token = hauwa_login(bank)
    for amount in ["100", "200", "300", "400", "500"]:
        bank.transfer(token, "A1001", "A1002", amount)
    page2 = [e["amount"] for e in bank.get_history(token, "A1001", page=2, page_size=2)]
    assert page2 == [Decimal("300.00"), Decimal("200.00")]


def tc029(bank):
    token = khadijah_login(bank)
    expect_error(lambda: bank.get_history(token, "A1001"))


def tc030(bank):
    token = khadijah_login(bank)
    assert bank.get_history(token, "B2001") == []

TESTS = [
    ("TC001", "Verify successful customer login", "Authentication", tc001),
    ("TC002", "Verify invalid password rejection", "Authentication", tc002),
    ("TC003", "Verify account lockout after three failed logins", "Authentication", tc003),
    ("TC004", "Verify failed-attempt counter resets after success", "Authentication", tc004),
    ("TC005", "Verify logout invalidates the session", "Authentication", tc005),
    ("TC006", "Verify login with unknown username is rejected", "Authentication", tc006),
    ("TC007", "Verify transfer between own accounts with fee", "Fund Transfer", tc007),
    ("TC008", "Verify transfer to another customer's account", "Fund Transfer", tc008),
    ("TC009", "Verify zero-amount transfer is rejected", "Fund Transfer", tc009),
    ("TC010", "Verify negative-amount transfer is rejected", "Fund Transfer", tc010),
    ("TC011", "Verify transfer from an account the user does not own is rejected", "Fund Transfer", tc011),
    ("TC012", "Verify transfer is rejected when balance cannot cover amount plus fee", "Fund Transfer", tc012),
    ("TC013", "Verify daily transfer limit is applied cumulatively", "Fund Transfer", tc013),
    ("TC014", "Verify successful payment to a merchant with service charge", "Payment Processing", tc014),
    ("TC015", "Verify payment service charge is rounded correctly", "Payment Processing", tc015),
    ("TC016", "Verify duplicate payment reference is rejected", "Payment Processing", tc016),
    ("TC017", "Verify payment exactly at the per-payment limit is accepted", "Payment Processing", tc017),
    ("TC018", "Verify payment above the per-payment limit is rejected", "Payment Processing", tc018),
    ("TC019", "Verify payment from an account the user does not own is rejected", "Payment Processing", tc019),
    ("TC020", "Verify successful password change", "Account Management", tc020),
    ("TC021", "Verify password change is rejected when the old password is wrong", "Account Management", tc021),
    ("TC022", "Verify password policy rejects a password shorter than 8 characters", "Account Management", tc022),
    ("TC023", "Verify successful email update", "Account Management", tc023),
    ("TC024", "Verify invalid email address is rejected", "Account Management", tc024),
    ("TC025", "Verify balance enquiry on another customer's account is rejected", "Account Management", tc025),
    ("TC026", "Verify history lists transactions newest first", "Transaction History", tc026),
    ("TC027", "Verify history entries show type, amount, fee and counterparty", "Transaction History", tc027),
    ("TC028", "Verify history pagination returns the correct page", "Transaction History", tc028),
    ("TC029", "Verify history of another customer's account is rejected", "Transaction History", tc029),
    ("TC030", "Verify history is empty for an account with no transactions", "Transaction History", tc030),
]