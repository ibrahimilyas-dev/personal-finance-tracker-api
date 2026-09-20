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

from statistics import mean, pstdev


def _classify_frequency(average_gap_days: float) -> str | None:
    """
    Map an average gap between transactions (in days) to a human-readable
    frequency label, allowing some tolerance for real-world irregularity
    (e.g. a "monthly" bill doesn't land on exactly the same day every time).

    Returns None if the gap doesn't fall into a recognisable pattern.
    """
    if 5 <= average_gap_days <= 9:
        return "weekly"
    if 25 <= average_gap_days <= 35:
        return "monthly"
    if 350 <= average_gap_days <= 380:
        return "yearly"
    return None


def detect_recurring_payments(transactions: list[Transaction]) -> list[dict]:
    """
    Identify likely recurring payments by grouping transactions by
    merchant and checking whether their amounts and timing are
    consistent enough to suggest a subscription or regular bill.

    Heuristic, not exact: a merchant needs at least 2 transactions,
    amounts within roughly 10% of their average, and a consistent
    gap between transactions matching a weekly, monthly, or yearly
    pattern (with tolerance for real-world irregularity).
    """
    by_merchant: dict[str, list[Transaction]] = defaultdict(list)
    for transaction in transactions:
        if transaction.transaction_type == "expense":
            by_merchant[transaction.merchant].append(transaction)

    recurring = []

    for merchant, merchant_transactions in by_merchant.items():
        if len(merchant_transactions) < 2:
            continue  # Need at least 2 occurrences to detect a pattern

        sorted_transactions = sorted(merchant_transactions, key=lambda t: t.date)
        amounts = [float(t.amount) for t in sorted_transactions]
        average_amount = mean(amounts)

        # Amounts must be reasonably consistent — allow up to 10% deviation
        amount_tolerance = average_amount * 0.10
        if pstdev(amounts) > amount_tolerance:
            continue

        # Calculate gaps in days between consecutive transactions
        gaps = [
            (sorted_transactions[i].date - sorted_transactions[i - 1].date).days
            for i in range(1, len(sorted_transactions))
        ]
        average_gap = mean(gaps)

        frequency = _classify_frequency(average_gap)
        if frequency is None:
            continue

        recurring.append(
            {
                "merchant": merchant,
                "category": sorted_transactions[-1].category,
                "average_amount": round(average_amount, 2),
                "frequency": frequency,
                "occurrences": len(sorted_transactions),
                "last_date": sorted_transactions[-1].date.isoformat(),
            }
        )

    recurring.sort(key=lambda item: item["average_amount"], reverse=True)
    return recurring