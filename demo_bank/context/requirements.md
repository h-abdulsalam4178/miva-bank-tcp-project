# Miva Bank (fictional demo): Business Rules and Requirements

R1 Authentication: A customer logs in with a username and password. A failed
login gives the same generic message whether the username or the password
was wrong.
R2 Lockout: After 3 consecutive failed login attempts the account is locked,
even if the correct password is then entered. A successful login resets
the failed-attempt counter to zero.
R3 Logout: Logging out ends the session. The session ticket must stop working
immediately.
R4 Transfers: The amount must be greater than zero. The source and destination
accounts must differ. The sender must own the source account.
R5 Transfer fee: N10 for amounts up to N5,000; N25 up to N50,000; N50 above
that. The sender needs enough balance to cover the amount plus the fee.
R6 Daily transfer limit: A customer may send at most N500,000 in total per
day, counting all transfers made that day. The total resets the next day.
R7 Payments: A payment reference is required and may be used only once per
account. The maximum payment is N200,000; a payment of exactly N200,000 is
allowed. The service charge is 1.5% of the amount, rounded to the nearest
kobo, and never more than N2,000. The payer must own the account.
R8 Password change: The customer must supply the current password. The new
password must have at least 8 characters and at least one digit.
R9 Email update: An email address must contain text before the @ sign and a
dot after it, and must not contain spaces.
R10 Account privacy: A customer may view the balance and transaction history
of their own accounts only.
R11 History: Transactions are listed newest first, in pages. Each entry shows
the type, amount, fee and counterparty.
