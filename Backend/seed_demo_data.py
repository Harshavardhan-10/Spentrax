"""Seed the demo user with data covering every feature.

Run:  .\\venv\\Scripts\\python.exe seed_demo_data.py
Re-run anytime to reset the demo account to a fresh state.
"""
import json
import random
import sqlite3
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import bcrypt

sys.stdout.reconfigure(encoding="utf-8")

DB = Path(__file__).parent / "expense.db"
EMAIL = "demo@example.com"
PASSWORD = "DemoPass123!"

MERCHANTS = {
    "Food": ["Swiggy", "Zomato", "Big Bazaar", "Zepto", "Blinkit"],
    "Transportation": ["Indian Oil", "Uber", "Ola", "RedBus"],
    "Shopping": ["Amazon", "Flipkart", "Myntra", "Reliance Digital"],
    "Entertainment": ["PVR Cinemas", "BookMyShow", "Spotify"],
    "Bills": ["Airtel", "Jio", "BSES"],
    "Healthcare": ["Apollo Pharmacy", "MedPlus"],
    "Education": ["Coursera", "Amazon Books"],
    "Travel": ["MakeMyTrip", "IRCTC"],
    "Utilities": ["BSES", "MCD"],
}
PAYMENTS = ["UPI", "CASH", "DEBIT_CARD", "CREDIT_CARD", "BANK_TRANSFER"]


def main():
    db = sqlite3.connect(DB)
    cur = db.cursor()

    cur.execute("SELECT id, name, password_hash FROM users WHERE email = ?", (EMAIL,))
    row = cur.fetchone()
    if row:
        user_id = row[0]
    else:
        password_hash = bcrypt.hashpw(PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cur.execute(
            "INSERT INTO users (name, email, password_hash, is_active, created_at, updated_at) "
            "VALUES (?, ?, ?, 1, datetime('now'), datetime('now'))",
            ("Demo User", EMAIL, password_hash),
        )
        user_id = cur.lastrowid
        print(f"Created user id={user_id} ({EMAIL})")

    print(f"Resetting demo data for user {user_id}...")
    for table in ("recurring_expenses", "ai_insights", "budgets", "expenses"):
        cur.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))
    cur.execute(
        "DELETE FROM categories WHERE user_id = ? AND is_default = 0", (user_id,)
    )
    db.commit()

    cats = {}
    cur.execute("SELECT id, name FROM categories WHERE is_default = 1 OR user_id = ?", (user_id,))
    for cid, name in cur.fetchall():
        cats[name] = cid
    for name in ("Subscriptions", "Investments"):
        if name not in cats:
            cur.execute(
                "INSERT INTO categories (name, description, is_default, user_id, created_at) "
                "VALUES (?, ?, 0, ?, datetime('now'))",
                (name, f"Custom category: {name}", user_id),
            )
            cats[name] = cur.lastrowid
    db.commit()

    today = date.today()
    rng = random.Random(20260814)
    expense_ids = {}
    aug_totals = {name: 0.0 for name in cats}

    def add_expense(category, amount, description, merchant, day, payment, notes=None, recurring=False, months_back=0):
        month_start = date(today.year, today.month, 1)
        d = date(month_start.year, month_start.month - months_back, min(day, 28))
        cur.execute(
            "INSERT INTO expenses (user_id, category_id, amount, description, merchant, payment_method, "
            "expense_date, notes, is_recurring, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
            (user_id, cats[category], amount, description, merchant, payment, d.isoformat(), notes, recurring),
        )
        key = (category, months_back)
        expense_ids[key] = cur.lastrowid
        aug_totals[category] = aug_totals.get(category, 0.0) + amount
        return cur.lastrowid

    for months_back in range(7, -1, -1):
        add_expense("Rent", 15000.00, "Monthly Rent", "Rent", 1, "UPI", recurring=True, months_back=months_back)
    for months_back in range(5, -1, -1):
        add_expense("Subscriptions", 499.00, "Netflix Subscription", "Netflix", 1, "CREDIT_CARD",
                    "Standard plan", recurring=True, months_back=months_back)
        add_expense("Healthcare", 999.00, "Gym Membership", "Gold's Gym", 5, "DEBIT_CARD",
                    "Monthly membership", recurring=True, months_back=months_back)

    for months_back in range(7, -1, -1):
        if months_back == 0:
            food = [(480, "Vegetables", "Big Bazaar"), (620, "Groceries", "Blinkit"), (850, "Weekend groceries", "Zepto")]
            transport = [(220, "Petrol", "Indian Oil"), (350, "Cab ride", "Uber")]
            shopping = [(1450, "T-shirt", "Myntra"), (2200, "Running shoes", "Amazon")]
            entertainment = [(900, "Movie night", "PVR Cinemas"), (150, "Concert ticket", "BookMyShow")]
            bills = [(1200, "Electricity bill", "BSES"), (900, "Mobile recharge", "Airtel")]
            utilities = [(1100, "Water bill", "MCD")]
            healthcare = [(750, "Pharmacy", "Apollo Pharmacy")]
            education = [(2500, "Online course", "Coursera")]
            travel = [(1800, "Weekend trip", "MakeMyTrip")]
            other = []
        else:
            food = [(rng.randint(200, 900), desc, merchant) for desc, merchant in
                    [(f"Groceries {rng.randint(1, 99)}", rng.choice(MERCHANTS["Food"])) for _ in range(rng.randint(2, 4))]]
            transport = [(rng.randint(80, 500), "Fuel" if rng.random() < 0.5 else "Cab", rng.choice(MERCHANTS["Transportation"]))
                         for _ in range(rng.randint(1, 2))]
            shopping = [(rng.randint(800, 3000), "Online order", rng.choice(MERCHANTS["Shopping"]))
                        for _ in range(rng.randint(0, 2))]
            entertainment = [(rng.randint(200, 900), "Entertainment", rng.choice(MERCHANTS["Entertainment"]))
                             for _ in range(rng.randint(1, 2))]
            bills = [(rng.randint(800, 2200), "Bill payment", rng.choice(MERCHANTS["Bills"])) for _ in range(1)]
            utilities = [(rng.randint(900, 1800), "Utility bill", "BSES") for _ in range(rng.randint(0, 1))]
            healthcare = [(rng.randint(300, 1500), "Health", "Apollo Pharmacy") for _ in range(rng.randint(0, 1))]
            education = [(rng.randint(500, 2500), "Education", "Coursera") for _ in range(rng.randint(0, 1))]
            travel = [(rng.randint(1000, 4000), "Travel", "MakeMyTrip") for _ in range(rng.randint(0, 1))]
            other = []

        for amount, desc, merchant in food:
            add_expense("Food", amount, desc, merchant, rng.randint(1, 28), rng.choice(PAYMENTS), months_back=months_back)
        for amount, desc, merchant in transport:
            add_expense("Transportation", amount, desc, merchant, rng.randint(1, 28), rng.choice(PAYMENTS), months_back=months_back)
        for amount, desc, merchant in shopping:
            add_expense("Shopping", amount, desc, merchant, rng.randint(1, 28), rng.choice(PAYMENTS), months_back=months_back)
        for amount, desc, merchant in entertainment:
            add_expense("Entertainment", amount, desc, merchant, rng.randint(1, 28), rng.choice(PAYMENTS), months_back=months_back)
        for amount, desc, merchant in bills:
            add_expense("Bills", amount, desc, merchant, rng.randint(1, 28), rng.choice(PAYMENTS), months_back=months_back)
        for amount, desc, merchant in utilities:
            add_expense("Utilities", amount, desc, merchant, rng.randint(1, 28), rng.choice(PAYMENTS), months_back=months_back)
        for amount, desc, merchant in healthcare:
            add_expense("Healthcare", amount, desc, merchant, rng.randint(1, 28), rng.choice(PAYMENTS), months_back=months_back)
        for amount, desc, merchant in education:
            add_expense("Education", amount, desc, merchant, rng.randint(1, 28), rng.choice(PAYMENTS), months_back=months_back)
        for amount, desc, merchant in travel:
            add_expense("Travel", amount, desc, merchant, rng.randint(1, 28), rng.choice(PAYMENTS), months_back=months_back)
        for amount, desc, merchant in other:
            add_expense("Other", amount, desc, merchant, rng.randint(1, 28), rng.choice(PAYMENTS), months_back=months_back)

    add_expense("Investments", 5000.00, "Mutual Fund SIP", "HDFC MF", 3, "BANK_TRANSFER",
                "Monthly SIP investment")
    laptop_id = add_expense("Shopping", 45000.00, "MacBook Pro purchase", "Apple Store", 10, "BANK_TRANSFER",
                            "Big purchase - checked with family first")
    db.commit()

    cur.execute(
        "SELECT amount FROM expenses WHERE user_id = ? AND category_id = ? AND expense_date < ?",
        (user_id, cats["Shopping"], f"{today.year:04d}-{today.month:02d}-10"),
    )
    historical = [r[0] for r in cur.fetchall()]
    mean = sum(historical) / len(historical) if historical else 0.0
    std = (sum((a - mean) ** 2 for a in historical) / len(historical)) ** 0.5 if historical else 0.0
    z_score = (45000.0 - mean) / std if std else 0.0
    print(f"Shopping anomaly: mean={mean:.2f}, std={std:.2f}, z={z_score:.1f}, samples={len(historical)}")

    now = datetime.now()

    def insight(i_type, title, content, severity, meta=None, hours_ago=0):
        created = (now - timedelta(hours=hours_ago)).strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(
            "INSERT INTO ai_insights (user_id, insight_type, title, content, severity, insight_metadata, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, i_type, title, content, severity, json.dumps(meta) if meta else None, created),
        )

    cur.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ? AND expense_date >= ? AND expense_date < ?",
        (user_id, f"{today.year:04d}-{today.month:02d}-01", date(today.year, today.month + 1, 1).isoformat()),
    )
    aug_total = cur.fetchone()[0]
    first_prev = date(today.year, today.month - 1, 1)
    cur.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ? AND expense_date >= ? AND expense_date < ?",
        (user_id, first_prev.isoformat(), f"{today.year:04d}-{today.month:02d}-01"),
    )
    jul_total = cur.fetchone()[0]
    change = (aug_total - jul_total) / jul_total * 100 if jul_total > 0 else 0.0
    shopping_total = aug_totals.get("Shopping", 0.0)
    share = shopping_total / aug_total * 100 if aug_total else 0.0

    insight("ANOMALY", "Unusual spending in Shopping",
            f"An expense of \u20b945,000.00 in Shopping is {z_score:.1f} standard deviations above your typical "
            f"average of \u20b9{mean:,.2f} in this category. Verify this transaction is correct.",
            "WARNING", {"amount": 45000.0, "category": "Shopping", "z_score": round(z_score, 2),
                        "mean": round(mean, 2), "expense_id": laptop_id}, hours_ago=2)
    insight("SPENDING", "Spending increased",
            f"Your spending is {change:.1f}% higher than last month. Review your largest categories for "
            "savings opportunities.", "WARNING", hours_ago=5)
    insight("BUDGET", f"High concentration in Shopping",
            f"Shopping accounts for {share:.0f}% of this month's spending (\u20b9{shopping_total:,.2f}). "
            "Consider setting a budget for it.", "WARNING", hours_ago=8)
    insight("MONTHLY_SUMMARY", f"Monthly summary \u2014 {today.month:02d}/{today.year}",
            f"You spent \u20b9{aug_total:,.2f} this month, which is {change:.1f}% "
            f"{'higher' if change > 0 else 'lower'} than last month. Shopping was your largest category "
            f"at \u20b9{shopping_total:,.2f}.", "INFO", {"month": today.month, "year": today.year}, hours_ago=10)

    budgets = {
        "Rent": 15000.00, "Food": 1500.00, "Shopping": 30000.00, "Entertainment": 2000.00,
        "Transportation": 1000.00, "Bills": 3000.00, "Utilities": 1500.00, "Healthcare": 2500.00,
        "Education": 5000.00, "Travel": 4000.00, "Subscriptions": 600.00,
    }
    for name, amount in budgets.items():
        cur.execute(
            "INSERT INTO budgets (user_id, category_id, amount, month, year, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
            (user_id, cats[name], amount, today.month, today.year),
        )
    prev = date(today.year, today.month - 1, 1)
    for name, amount in (("Rent", 15000.00), ("Food", 1800.00), ("Transportation", 900.00), ("Entertainment", 1500.00)):
        cur.execute(
            "INSERT INTO budgets (user_id, category_id, amount, month, year, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
            (user_id, cats[name], amount, prev.month, prev.year),
        )

    recurring = [
        ("Rent", 15000.00, "MONTHLY", expense_ids[("Rent", 0)], "2026-09-01", 0.99),
        ("Netflix", 499.00, "MONTHLY", expense_ids[("Subscriptions", 0)], "2026-09-01", 0.97),
        ("Gold's Gym", 999.00, "MONTHLY", expense_ids[("Healthcare", 0)], "2026-09-05", 0.95),
    ]
    for name, amount, frequency, exp_id, next_due, confidence in recurring:
        cur.execute(
            "INSERT INTO recurring_expenses (user_id, expense_id, name, amount, frequency, next_due_date, "
            "confidence_score, is_active, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, 1, datetime('now'), datetime('now'))",
            (user_id, exp_id, name, amount, frequency, next_due, confidence),
        )

    db.commit()

    cur.execute("SELECT COUNT(*) FROM expenses WHERE user_id = ?", (user_id,))
    count = cur.fetchone()[0]
    cur.execute("SELECT category_id, ROUND(SUM(amount), 2) FROM expenses WHERE user_id = ? "
                "AND expense_date >= ? GROUP BY category_id",
                (user_id, f"{today.year:04d}-{today.month:02d}-01"))
    aug_breakdown = [(cats_name(cats, cid), total) for cid, total in cur.fetchall()]
    db.close()

    print(f"\nExpenses: {count} total | August total: \u20b9{aug_total:,.2f} (July: \u20b9{jul_total:,.2f}, {change:+.1f}%)")
    print("August by category:", ", ".join(f"{n}=\u20b9{t:,.0f}" for n, t in sorted(aug_breakdown, key=lambda x: -x[1])))
    print(f"\nLogin: {EMAIL} / {PASSWORD}")


def cats_name(cats, cid):
    for name, c in cats.items():
        if c == cid:
            return name
    return str(cid)


if __name__ == "__main__":
    main()
