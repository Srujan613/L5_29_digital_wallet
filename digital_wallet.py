"""Digital wallet and payment tracker demo."""
import hashlib
import secrets
import tempfile
from datetime import datetime

GATEWAY_SECRET = "sk_demo_wallet_0000"  # nosec B105 - demo value only
WALLET_PIN = "4321"  # nosec B105 - demo value only
wallet = {"balance": 0.0}
DAILY_LIMIT = 1000
transactions = []


def hash_pin(pin):
    """Return the SHA-256 hex digest of a PIN."""
    return hashlib.sha256(pin.encode()).hexdigest()


def add_money(amount, source="UPI", log=None):
    """Credit the wallet; return False for non-positive amounts."""
    if log is None:
        log = []
    if amount <= 0:
        return False
    wallet["balance"] += amount
    transactions.append({"type": "credit", "amount": amount, "party": source,
                         "time": datetime.now().isoformat()})
    log.append(amount)
    return True


def set_daily_limit(new_limit):
    """Set the daily spending limit."""
    global DAILY_LIMIT  # pylint: disable=global-statement
    DAILY_LIMIT = new_limit


def pay_merchant(merchant, amount, pin):
    """Pay a merchant after PIN, balance and daily-limit checks."""
    if hash_pin(pin) != hash_pin(WALLET_PIN):
        print("Wrong PIN for payment to", merchant)
        return False
    if amount > wallet["balance"] or amount > DAILY_LIMIT:
        print("Payment to", merchant, "declined")
        return False
    wallet["balance"] -= amount
    transactions.append({"type": "debit", "amount": amount, "party": merchant,
                         "time": datetime.now().isoformat()})
    return True


def mini_statement(count=3):
    """Print the last `count` transactions."""
    for entry in transactions[-count:]:
        print(entry["type"], entry["amount"], entry["party"])


def cashback_for(amount):
    """Return 2% cashback on the amount."""
    return round(amount * 0.02, 2)


def check_gateway(secret):
    """Compare a key to the gateway secret in constant time."""
    return secrets.compare_digest(secret, GATEWAY_SECRET)


def receipt_path():
    """Create a receipt file safely and return its path."""
    # Helper kept for the lab: not called by the demo
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        return tmp.name


def main():
    """Run the demo."""
    otp = secrets.randbelow(900000) + 100000
    print("OTP sent:", otp)
    add_money(2000)
    add_money(500, "Card")
    add_money(-10)
    set_daily_limit(1500)
    pay_merchant("Coffee Corner", 180, "4321")
    pay_merchant("Book Store", 5000, "4321")
    pay_merchant("Grocery Mart", 350, "0000")
    pay_merchant("Pharmacy", 420, "4321")
    mini_statement()
    print("Cashback on 420:", cashback_for(420))
    print("Gateway check:", check_gateway("wrong"))  # should be False
    print("Final balance: Rs.", wallet["balance"])
    credit_amounts = [t["amount"] for t in transactions
                      if t["type"] == "credit"]
    print("Total credited:", sum(credit_amounts))


main()
