import hashlib
import secrets
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP


class BankError(Exception):
    """Raised when the bank refuses to do something."""


class Bank:
    MAX_FAILED_ATTEMPTS = 3
    DAILY_TRANSFER_LIMIT = Decimal("500000.00")
    PAYMENT_LIMIT = Decimal("200000.00")
    PAYMENT_CHARGE_RATE = Decimal("0.015")
    PAYMENT_CHARGE_CAP = Decimal("2000.00")
    MIN_PASSWORD_LENGTH = 8

    def __init__(self, name="Miva Bank", faults=()):
        self.name = name
        self.faults = frozenset(faults)
        self.users = {}
        self.accounts = {}
        self.sessions = {}
        self.transactions = []
        self.day = 0
        self.merchants = {}

    @staticmethod
    def _hash(password, salt):
        return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

    def create_user(self, username, first_name, last_name, city,
                    password, email, middle_name=""):
        salt = secrets.token_hex(4)
        self.users[username] = {
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "city": city,
            "email": email,
            "salt": salt,
            "pw_hash": self._hash(password, salt),
            "failed": 0,
            "locked": False,
        }

    def display_name(self, username):
        user = self.users[username]
        parts = [user["first_name"], user["middle_name"], user["last_name"]]
        return " ".join(part for part in parts if part)

    def open_account(self, owner, account_no, balance):
        self.accounts[account_no] = {"owner": owner, "balance": Decimal(balance)}

    def login(self, username, password):
        user = self.users.get(username)
        if user is None:
            raise BankError("Invalid credentials")
        if user["locked"]:
            raise BankError("Account locked")
        if self._hash(password, user["salt"]) != user["pw_hash"]:
            user["failed"] += 1
            if self._f("F01"):
                lock = user["failed"] > self.MAX_FAILED_ATTEMPTS
            else:
                lock = user["failed"] >= self.MAX_FAILED_ATTEMPTS
            if lock:
                user["locked"] = True
            raise BankError("Invalid credentials")
        if not self._f("F02"):
            user["failed"] = 0
        token = secrets.token_hex(8)
        self.sessions[token] = username
        return token    
    
    def _user(self, token):
        username = self.sessions.get(token)
        if username is None:
            raise BankError("Not authenticated")
        return username

    def logout(self, token):
        if not self._f("F03"):
            self.sessions.pop(token, None)

    def _require_owner(self, username, account_no):
        account = self.accounts.get(account_no)
        if account is None:
            raise BankError("Account not found")
        if account["owner"] != username and not self._f("F05"):
            raise BankError("Not authorised for this account")
        return account

    def get_balance(self, token, account_no):
        username = self._user(token)
        return self._require_owner(username, account_no)["balance"]
    
    @staticmethod
    def _money(value):
        try:
            return Decimal(str(value)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP)
        except Exception:
            raise BankError("Invalid amount")

    @staticmethod
    def _transfer_fee(amount):
        if amount <= Decimal("5000"):
            return Decimal("10.00")
        if amount <= Decimal("50000"):
            return Decimal("25.00")
        return Decimal("50.00")

    def transfer(self, token, from_acct, to_acct, amount):
        username = self._user(token)
        amt = self._money(amount)
        if self._f("F04"):
            invalid = amt < 0
        else:
            invalid = amt <= 0
        if invalid:
            raise BankError("Amount must be greater than zero")
        if from_acct == to_acct:
            raise BankError("Source and destination must differ")
        source = self._require_owner(username, from_acct)
        destination = self.accounts.get(to_acct)
        if destination is None:
            raise BankError("Destination account not found")
        fee = self._transfer_fee(amt)
        if self._f("F06"):
            needed = amt
        else:
            needed = amt + fee
        if source["balance"] < needed:
            raise BankError("Insufficient funds")
        if self._f("F07"):
            over = amt > self.DAILY_TRANSFER_LIMIT
        else:
            over = self._transferred_today(username) + amt > self.DAILY_TRANSFER_LIMIT
        if over:
            raise BankError("Daily transfer limit exceeded")
        source["balance"] -= amt + fee
        destination["balance"] += amt
        self._record(from_acct, "TRANSFER_OUT", amt, fee, to_acct, username)
        self._record(to_acct, "TRANSFER_IN", amt, Decimal("0.00"), from_acct, username)
        return fee
    
    def advance_day(self):
        self.day += 1

    def _record(self, account, kind, amount, fee, counterparty, actor,
                reference=""):
        self.transactions.append({
            "id": len(self.transactions) + 1,
            "account": account,
            "type": kind,
            "amount": amount,
            "fee": fee,
            "counterparty": counterparty,
            "actor": actor,
            "reference": reference,
            "day": self.day,
        })

    def _transferred_today(self, username):
        total = Decimal("0.00")
        for t in self.transactions:
            if (t["actor"] == username and t["type"] == "TRANSFER_OUT"
                    and t["day"] == self.day):
                total += t["amount"]
        return total
    
    def add_merchant(self, merchant_id):
        self.merchants[merchant_id] = {"balance": Decimal("0.00")}

    def pay(self, token, from_acct, merchant_id, amount, reference):
        username = self._user(token)
        amt = self._money(amount)
        if amt <= 0:
            raise BankError("Amount must be greater than zero")
        if not reference:
            raise BankError("Payment reference required")
        if self._f("F08"):
            over = amt >= self.PAYMENT_LIMIT
        else:
            over = amt > self.PAYMENT_LIMIT
        if over:
            raise BankError("Payment limit exceeded")
        if merchant_id not in self.merchants:
            raise BankError("Merchant not found")
        source = self._require_owner(username, from_acct)
        duplicate = False
        for t in self.transactions:
            if (t["account"] == from_acct and t["type"] == "PAYMENT"
                    and t["reference"] == reference):
                duplicate = True
        if duplicate and not self._f("F09"):
            raise BankError("Duplicate payment reference")
        if self._f("F10"):
            mode = ROUND_DOWN
        else:
            mode = ROUND_HALF_UP
        charge = (amt * self.PAYMENT_CHARGE_RATE).quantize(
            Decimal("0.01"), rounding=mode)
        charge = min(charge, self.PAYMENT_CHARGE_CAP)
        if source["balance"] < amt + charge:
            raise BankError("Insufficient funds")
        source["balance"] -= amt + charge
        self.merchants[merchant_id]["balance"] += amt
        self._record(from_acct, "PAYMENT", amt, charge, merchant_id,
                     username, reference)
        return charge
    
    def change_password(self, token, old_password, new_password):
        username = self._user(token)
        user = self.users[username]
        if not self._f("F11"):
            if self._hash(old_password, user["salt"]) != user["pw_hash"]:
                raise BankError("Current password incorrect")
        if self._f("F12"):
            min_length = 6
        else:
            min_length = self.MIN_PASSWORD_LENGTH
        if (len(new_password) < min_length
                or not any(c.isdigit() for c in new_password)):
            raise BankError("Password does not meet policy")
        user["pw_hash"] = self._hash(new_password, user["salt"])

    def update_email(self, token, email):
        username = self._user(token)
        local, _, domain = email.partition("@")
        if not local or "." not in domain or " " in email:
            raise BankError("Invalid email address")
        self.users[username]["email"] = email

    def get_profile(self, token):
        username = self._user(token)
        user = self.users[username]
        return {
            "name": self.display_name(username),
            "city": user["city"],
            "email": user["email"],
        }
    
    def get_history(self, token, account_no, page=1, page_size=10):
        username = self._user(token)
        self._require_owner(username, account_no)
        if page < 1 or page_size < 1:
            raise BankError("Invalid page parameters")
        entries = [t for t in self.transactions if t["account"] == account_no]
        if not self._f("F13"):
            entries = list(reversed(entries))
        start = (page - 1) * page_size
        if self._f("F14"):
            start += 1
        return [dict(e) for e in entries[start:start + page_size]]
    
    def _f(self, code):
        return code in self.faults