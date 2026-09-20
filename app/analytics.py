"""
Financial analytics computed over a set of transactions.

Calculations are done in Python rather than SQL aggregate queries.
This keeps the logic transparent and easy to unit test with plain
Python objects, at the cost of efficiency at very large data volumes
— an acceptable trade-off at this project's scale, and one a
production system would likely revisit by pushing aggregation into
the database instead.
"""

from collections import defaultdict
from decimal import Decimal

from app.models import Transaction


def calculate_monthly_summary(transactions: list[Transaction]) -> list[dict]:
    """
    Group transactions by year-month and compute income, expenses,
    net savings, and savings rate for each month.

    Savings rate is expressed as a percentage of income saved
    (0 if there was no income that month, to avoid division by zero).
    """
    months: dict[str, dict[str, Decimal]] = defaultdict(
        lambda: {"income": Decimal("0"), "expenses": Decimal("0")}
    )

    for transaction in transactions:
        month_key = transaction.date.strftime("%Y-%m")
        if transaction.transaction_type == "income":
            months[month_key]["income"] += transaction.amount
        else:
            months[month_key]["expenses"] += transaction.amount

    summary = []
    for month_key in sorted(months.keys()):
        income = months[month_key]["income"]
        expenses = months[month_key]["expenses"]
        net_savings = income - expenses
        savings_rate = float(net_savings / income * 100) if income > 0 else 0.0

        summary.append(
            {
                "month": month_key,
                "income": float(income),
                "expenses": float(expenses),
                "net_savings": float(net_savings),
                "savings_rate_percent": round(savings_rate, 2),
            }
        )

    return summary


def calculate_category_breakdown(transactions: list[Transaction]) -> list[dict]:
    """
    Group expense transactions by category and compute total spent per
    category, sorted from highest to lowest spend.

    Income transactions are excluded — this endpoint answers "where did
    my money go", not "where did my money come from".
    """
    totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

    for transaction in transactions:
        if transaction.transaction_type == "expense":
            totals[transaction.category] += transaction.amount

    breakdown = [
        {"category": category, "total_spent": float(total)}
        for category, total in totals.items()
    ]

    breakdown.sort(key=lambda item: item["total_spent"], reverse=True)

    return breakdown