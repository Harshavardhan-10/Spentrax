"""Seed the demo user with data covering every feature.

Uses the app's SQLAlchemy engine / models, so it works identically on the
local SQLite database and on a remote Postgres database (e.g. Neon on Render).
The connection is read from DATABASE_URL exactly like the running server.

Run:
    python seed_demo_data.py               # reset the demo account to a fresh state
    python seed_demo_data.py --if-missing  # only seed when the demo user is absent
                                           # (used at deploy time so existing data
                                           # is never wiped on a cold start)
"""
import argparse
import json
import random
import sys
from datetime import date, datetime, timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8")

from sqlalchemy import delete, func, select

from app.core.database import SessionLocal, engine
from app.core.security import hash_password
from app.models.ai_insight import AIInsight
from app.models.budget import Budget
from app.models.category import Category
from app.models.expense import Expense
from app.models.recurring import RecurringExpense
from app.models.user import User
from app.services.category_service import seed_default_categories

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
    parser = argparse.ArgumentParser(description="Seed / reset the demo account.")
    parser.add_argument(
        "--if-missing",
        action="store_true",
        help="Only seed when the demo user does not exist or has no expenses.",
    )
    args = parser.parse_args()

    print(
        f"Seeding demo data into: "
        f"{engine.url.render_as_string(hide_password=True)}"
    )

    db = SessionLocal()
    try:
        seed_default_categories(db)

        user = db.scalar(select(User).where(User.email == EMAIL))
        if args.if_missing and user is not None:
            expense_count = db.scalar(
                select(func.count(Expense.id)).where(Expense.user_id == user.id)
            )
            if expense_count:
                print(
                    f"Demo user already exists with {expense_count} expenses; "
                    f"skipping (--if-missing)."
                )
                return
            print(
                "Demo user exists but has no expenses; seeding demo data... "
                "(use without --if-missing to force a full reset)"
            )

        if user is None:
            user = User(
                name="Demo User",
                email=EMAIL,
                password_hash=hash_password(PASSWORD),
                is_active=True,
            )
            db.add(user)
            db.flush()
            print(f"Created user id={user.id} ({EMAIL})")

        user_id = user.id
        print(f"Resetting demo data for user {user_id}...")
        db.execute(delete(RecurringExpense).where(RecurringExpense.user_id == user_id))
        db.execute(delete(AIInsight).where(AIInsight.user_id == user_id))
        db.execute(delete(Budget).where(Budget.user_id == user_id))
        db.execute(delete(Expense).where(Expense.user_id == user_id))
        db.execute(
            delete(Category).where(
                Category.user_id == user_id, Category.is_default.is_(False)
            )
        )
        db.commit()

        cats = {}
        for cat in db.scalars(
            select(Category).where(
                (Category.is_default.is_(True)) | (Category.user_id == user_id)
            )
        ):
            cats[cat.name] = cat.id
        for name in ("Subscriptions", "Investments"):
            if name not in cats:
                cat = Category(
                    name=name,
                    description=f"Custom category: {name}",
                    is_default=False,
                    user_id=user_id,
                )
                db.add(cat)
                db.flush()
                cats[name] = cat.id
        db.commit()

        today = date.today()
        rng = random.Random(20260814)
        expense_ids = {}
        aug_totals = {name: 0.0 for name in cats}

        def add_expense(
            category, amount, description, merchant, day, payment,
            notes=None, recurring=False, months_back=0,
        ):
            month_start = date(today.year, today.month, 1)
            d = date(month_start.year, month_start.month - months_back, min(day, 28))
            exp = Expense(
                user_id=user_id,
                category_id=cats[category],
                amount=amount,
                description=description,
                merchant=merchant,
                payment_method=payment,
                expense_date=d,
                notes=notes,
                is_recurring=recurring,
            )
            db.add(exp)
            db.flush()
            key = (category, months_back)
            expense_ids[key] = exp.id
            aug_totals[category] = aug_totals.get(category, 0.0) + amount
            return exp.id

        for months_back in range(7, -1, -1):
            add_expense(
                "Rent", 15000.00, "Monthly Rent", "Rent", 1, "UPI",
                recurring=True, months_back=months_back,
            )
        for months_back in range(5, -1, -1):
            add_expense(
                "Subscriptions", 499.00, "Netflix Subscription", "Netflix", 1,
                "CREDIT_CARD", "Standard plan", recurring=True, months_back=months_back,
            )
            add_expense(
                "Healthcare", 999.00, "Gym Membership", "Gold's Gym", 5,
                "DEBIT_CARD", "Monthly membership", recurring=True, months_back=months_back,
            )

        for months_back in range(7, -1, -1):
            if months_back == 0:
                food = [(480, "Vegetables", "Big Bazaar"), (620, "Groceries", "Blinkit"),
                        (850, "Weekend groceries", "Zepto")]
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
                food = [
                    (rng.randint(200, 900), desc, merchant)
                    for desc, merchant in
                    [(f"Groceries {rng.randint(1, 99)}", rng.choice(MERCHANTS["Food"]))
                     for _ in range(rng.randint(2, 4))]
                ]
                transport = [
                    (rng.randint(80, 500), "Fuel" if rng.random() < 0.5 else "Cab",
                     rng.choice(MERCHANTS["Transportation"]))
                    for _ in range(rng.randint(1, 2))
                ]
                shopping = [
                    (rng.randint(800, 3000), "Online order", rng.choice(MERCHANTS["Shopping"]))
                    for _ in range(rng.randint(0, 2))
                ]
                entertainment = [
                    (rng.randint(200, 900), "Entertainment", rng.choice(MERCHANTS["Entertainment"]))
                    for _ in range(rng.randint(1, 2))
                ]
                bills = [
                    (rng.randint(800, 2200), "Bill payment", rng.choice(MERCHANTS["Bills"]))
                    for _ in range(1)
                ]
                utilities = [
                    (rng.randint(900, 1800), "Utility bill", "BSES") for _ in range(rng.randint(0, 1))
                ]
                healthcare = [
                    (rng.randint(300, 1500), "Health", "Apollo Pharmacy") for _ in range(rng.randint(0, 1))
                ]
                education = [
                    (rng.randint(500, 2500), "Education", "Coursera") for _ in range(rng.randint(0, 1))
                ]
                travel = [
                    (rng.randint(1000, 4000), "Travel", "MakeMyTrip") for _ in range(rng.randint(0, 1))
                ]
                other = []

            for amount, desc, merchant in food:
                add_expense("Food", amount, desc, merchant, rng.randint(1, 28),
                            rng.choice(PAYMENTS), months_back=months_back)
            for amount, desc, merchant in transport:
                add_expense("Transportation", amount, desc, merchant, rng.randint(1, 28),
                            rng.choice(PAYMENTS), months_back=months_back)
            for amount, desc, merchant in shopping:
                add_expense("Shopping", amount, desc, merchant, rng.randint(1, 28),
                            rng.choice(PAYMENTS), months_back=months_back)
            for amount, desc, merchant in entertainment:
                add_expense("Entertainment", amount, desc, merchant, rng.randint(1, 28),
                            rng.choice(PAYMENTS), months_back=months_back)
            for amount, desc, merchant in bills:
                add_expense("Bills", amount, desc, merchant, rng.randint(1, 28),
                            rng.choice(PAYMENTS), months_back=months_back)
            for amount, desc, merchant in utilities:
                add_expense("Utilities", amount, desc, merchant, rng.randint(1, 28),
                            rng.choice(PAYMENTS), months_back=months_back)
            for amount, desc, merchant in healthcare:
                add_expense("Healthcare", amount, desc, merchant, rng.randint(1, 28),
                            rng.choice(PAYMENTS), months_back=months_back)
            for amount, desc, merchant in education:
                add_expense("Education", amount, desc, merchant, rng.randint(1, 28),
                            rng.choice(PAYMENTS), months_back=months_back)
            for amount, desc, merchant in travel:
                add_expense("Travel", amount, desc, merchant, rng.randint(1, 28),
                            rng.choice(PAYMENTS), months_back=months_back)
            for amount, desc, merchant in other:
                add_expense("Other", amount, desc, merchant, rng.randint(1, 28),
                            rng.choice(PAYMENTS), months_back=months_back)

        add_expense("Investments", 5000.00, "Mutual Fund SIP", "HDFC MF", 3,
                    "BANK_TRANSFER", "Monthly SIP investment")
        laptop_id = add_expense("Shopping", 45000.00, "MacBook Pro purchase", "Apple Store", 10,
                                "BANK_TRANSFER", "Big purchase - checked with family first")
        db.commit()

        month_start = date(today.year, today.month, 1)
        prev_start = date(today.year, today.month - 1, 1)

        historical = [
            float(a)
            for a in db.scalars(
                select(Expense.amount).where(
                    Expense.user_id == user_id,
                    Expense.category_id == cats["Shopping"],
                    Expense.expense_date < month_start,
                )
            )
        ]
        mean = sum(historical) / len(historical) if historical else 0.0
        std = (
            (sum((a - mean) ** 2 for a in historical) / len(historical)) ** 0.5
            if historical else 0.0
        )
        z_score = (45000.0 - mean) / std if std else 0.0
        print(
            f"Shopping anomaly: mean={mean:.2f}, std={std:.2f}, z={z_score:.1f}, "
            f"samples={len(historical)}"
        )

        now = datetime.now(timezone.utc)

        def insight(i_type, title, content, severity, meta=None, hours_ago=0):
            db.add(AIInsight(
                user_id=user_id,
                insight_type=i_type,
                title=title,
                content=content,
                severity=severity,
                insight_metadata=meta,
                created_at=now - timedelta(hours=hours_ago),
            ))

        aug_total = float(db.scalar(
            select(func.coalesce(func.sum(Expense.amount), 0)).where(
                Expense.user_id == user_id,
                Expense.expense_date >= month_start,
                Expense.expense_date < date(today.year, today.month + 1, 1),
            )
        ))
        jul_total = float(db.scalar(
            select(func.coalesce(func.sum(Expense.amount), 0)).where(
                Expense.user_id == user_id,
                Expense.expense_date >= prev_start,
                Expense.expense_date < month_start,
            )
        ))
        change = (aug_total - jul_total) / jul_total * 100 if jul_total > 0 else 0.0
        shopping_total = aug_totals.get("Shopping", 0.0)
        share = shopping_total / aug_total * 100 if aug_total else 0.0

        insight("ANOMALY", "Unusual spending in Shopping",
                f"An expense of \u20b945,000.00 in Shopping is {z_score:.1f} standard deviations "
                f"above your typical average of \u20b9{mean:,.2f} in this category. Verify this "
                "transaction is correct.",
                "WARNING", {"amount": 45000.0, "category": "Shopping", "z_score": round(z_score, 2),
                            "mean": round(mean, 2), "expense_id": laptop_id}, hours_ago=2)
        insight("SPENDING", "Spending increased",
                f"Your spending is {change:.1f}% higher than last month. Review your largest "
                "categories for savings opportunities.",
                "WARNING", hours_ago=5)
        insight("BUDGET", "High concentration in Shopping",
                f"Shopping accounts for {share:.0f}% of this month's spending "
                f"(\u20b9{shopping_total:,.2f}). Consider setting a budget for it.",
                "WARNING", hours_ago=8)
        insight("MONTHLY_SUMMARY", f"Monthly summary \u2014 {today.month:02d}/{today.year}",
                f"You spent \u20b9{aug_total:,.2f} this month, which is {change:.1f}% "
                f"{'higher' if change > 0 else 'lower'} than last month. Shopping was your largest "
                f"category at \u20b9{shopping_total:,.2f}.",
                "INFO", {"month": today.month, "year": today.year}, hours_ago=10)

        budgets = {
            "Rent": 15000.00, "Food": 1500.00, "Shopping": 30000.00, "Entertainment": 2000.00,
            "Transportation": 1000.00, "Bills": 3000.00, "Utilities": 1500.00, "Healthcare": 2500.00,
            "Education": 5000.00, "Travel": 4000.00, "Subscriptions": 600.00,
        }
        for name, amount in budgets.items():
            db.add(Budget(
                user_id=user_id, category_id=cats[name], amount=amount,
                month=today.month, year=today.year,
            ))
        prev = date(today.year, today.month - 1, 1)
        for name, amount in (("Rent", 15000.00), ("Food", 1800.00),
                             ("Transportation", 900.00), ("Entertainment", 1500.00)):
            db.add(Budget(
                user_id=user_id, category_id=cats[name], amount=amount,
                month=prev.month, year=prev.year,
            ))

        def next_due(day):
            nxt = date(today.year, today.month + 1, 1)
            return date(nxt.year, nxt.month, min(day, 28))

        recurring = [
            ("Rent", 15000.00, "MONTHLY", expense_ids[("Rent", 0)], next_due(1), 0.99),
            ("Netflix", 499.00, "MONTHLY", expense_ids[("Subscriptions", 0)], next_due(1), 0.97),
            ("Gold's Gym", 999.00, "MONTHLY", expense_ids[("Healthcare", 0)], next_due(5), 0.95),
        ]
        for name, amount, frequency, exp_id, due, confidence in recurring:
            db.add(RecurringExpense(
                user_id=user_id, expense_id=exp_id, name=name, amount=amount,
                frequency=frequency, next_due_date=due, confidence_score=confidence,
                is_active=True,
            ))

        db.commit()

        count = db.scalar(
            select(func.count(Expense.id)).where(Expense.user_id == user_id)
        )
        aug_rows = db.execute(
            select(Expense.category_id, func.round(func.sum(Expense.amount), 2))
            .where(
                Expense.user_id == user_id,
                Expense.expense_date >= month_start,
            )
            .group_by(Expense.category_id)
        ).all()
        aug_breakdown = [(cats_name(cats, cid), total) for cid, total in aug_rows]

        print(
            f"\nExpenses: {count} total | August total: \u20b9{aug_total:,.2f} "
            f"(July: \u20b9{jul_total:,.2f}, {change:+.1f}%)"
        )
        print(
            "August by category: ",
            ", ".join(f"{n}=\u20b9{t:,.0f}" for n, t in
                      sorted(aug_breakdown, key=lambda x: -x[1])),
        )
        print(f"\nLogin: {EMAIL} / {PASSWORD}")
    finally:
        db.close()


def cats_name(cats, cid):
    for name, c in cats.items():
        if c == cid:
            return name
    return str(cid)


if __name__ == "__main__":
    main()