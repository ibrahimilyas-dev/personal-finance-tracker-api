from datetime import date
from decimal import Decimal

from app.analytics import calculate_category_breakdown, calculate_monthly_summary, detect_recurring_payments
from app.models import Transaction


def make_transaction(
    txn_date: date,
    merchant: str,
    amount: str,
    transaction_type: str,
    category: str = "Uncategorised",
) -> Transaction:
    """Helper to build a Transaction object in memory, without a database."""
    return Transaction(
        date=txn_date,
        merchant=merchant,
        description=None,
        amount=Decimal(amount),
        transaction_type=transaction_type,
        category=category,
    )


def test_monthly_summary_calculates_income_expenses_and_savings():
    transactions = [
        make_transaction(date(2026, 8, 1), "EMPLOYER", "2000.00", "income"),
        make_transaction(date(2026, 8, 5), "TESCO", "100.00", "expense", "Groceries"),
        make_transaction(date(2026, 8, 10), "SHELL", "50.00", "expense", "Fuel"),
    ]

    summary = calculate_monthly_summary(transactions)

    assert len(summary) == 1
    assert summary[0]["month"] == "2026-08"
    assert summary[0]["income"] == 2000.0
    assert summary[0]["expenses"] == 150.0
    assert summary[0]["net_savings"] == 1850.0
    assert summary[0]["savings_rate_percent"] == 92.5


def test_monthly_summary_handles_month_with_no_income():
    """Savings rate should be 0, not raise a division-by-zero error."""
    transactions = [
        make_transaction(date(2026, 8, 1), "TESCO", "50.00", "expense", "Groceries"),
    ]

    summary = calculate_monthly_summary(transactions)

    assert summary[0]["savings_rate_percent"] == 0.0


def test_category_breakdown_excludes_income_and_sorts_descending():
    transactions = [
        make_transaction(date(2026, 8, 1), "EMPLOYER", "2000.00", "income"),
        make_transaction(date(2026, 8, 2), "TESCO", "50.00", "expense", "Groceries"),
        make_transaction(date(2026, 8, 3), "SHELL", "80.00", "expense", "Fuel"),
    ]

    breakdown = calculate_category_breakdown(transactions)

    assert breakdown == [
        {"category": "Fuel", "total_spent": 80.0},
        {"category": "Groceries", "total_spent": 50.0},
    ]


def test_recurring_detection_flags_consistent_monthly_merchant():
    transactions = [
        make_transaction(date(2026, 6, 5), "NETFLIX", "15.99", "expense", "Entertainment"),
        make_transaction(date(2026, 7, 5), "NETFLIX", "15.99", "expense", "Entertainment"),
        make_transaction(date(2026, 8, 5), "NETFLIX", "15.99", "expense", "Entertainment"),
    ]

    recurring = detect_recurring_payments(transactions)

    assert len(recurring) == 1
    assert recurring[0]["merchant"] == "NETFLIX"
    assert recurring[0]["frequency"] == "monthly"
    assert recurring[0]["occurrences"] == 3


def test_recurring_detection_ignores_single_occurrence():
    """A merchant seen only once can't be recurring by definition."""
    transactions = [
        make_transaction(date(2026, 8, 1), "ONE OFF SHOP", "20.00", "expense"),
    ]

    assert detect_recurring_payments(transactions) == []


def test_recurring_detection_ignores_inconsistent_amounts():
    """Wildly varying amounts shouldn't be flagged, even with regular timing."""
    transactions = [
        make_transaction(date(2026, 6, 1), "TESCO", "20.00", "expense", "Groceries"),
        make_transaction(date(2026, 7, 1), "TESCO", "95.00", "expense", "Groceries"),
        make_transaction(date(2026, 8, 1), "TESCO", "15.00", "expense", "Groceries"),
    ]

    assert detect_recurring_payments(transactions) == []