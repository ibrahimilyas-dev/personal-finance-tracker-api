import csv
import io
import uuid
from datetime import date as date_type
from decimal import Decimal, InvalidOperation

from sqlalchemy.orm import Session

from app.categorizer import categorize_transaction
from app.models import Transaction
from app.schemas import TransactionCreate, TransactionType


def create_transaction(db: Session, transaction: TransactionCreate, category: str) -> Transaction:
    """Insert a new transaction into the database and return it."""
    db_transaction = Transaction(
        date=transaction.date,
        merchant=transaction.merchant,
        description=transaction.description,
        amount=transaction.amount,
        transaction_type=transaction.transaction_type.value,
        category=category,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def get_transactions(db: Session) -> list[Transaction]:
    """Return all transactions, ordered by most recent date first."""
    return db.query(Transaction).order_by(Transaction.date.desc()).all()


def get_transaction_by_id(db: Session, transaction_id: uuid.UUID) -> Transaction | None:
    """Return a single transaction by its ID, or None if it doesn't exist."""
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


def delete_transaction(db: Session, transaction_id: uuid.UUID) -> bool:
    """
    Delete a transaction by ID.

    Returns True if a transaction was found and deleted, False if no
    matching transaction existed.
    """
    db_transaction = get_transaction_by_id(db, transaction_id)
    if db_transaction is None:
        return False
    db.delete(db_transaction)
    db.commit()
    return True


def import_transactions_from_csv(db: Session, csv_content: str) -> dict:
    """
    Parse CSV content and bulk-insert valid transactions.

    Expected columns: date, merchant, description, amount, transaction_type

    Returns a summary dict with counts of successful imports and any
    row-level errors encountered, rather than failing the whole import
    on one bad row.
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    imported_count = 0
    errors: list[str] = []

    for row_number, row in enumerate(reader, start=2):  # start=2: row 1 is the header
        try:
            transaction_date = date_type.fromisoformat(row["date"].strip())
            merchant = row["merchant"].strip()
            description = row.get("description", "").strip() or None
            amount = Decimal(row["amount"].strip())
            transaction_type = TransactionType(row["transaction_type"].strip().lower())

            if amount <= 0:
                raise ValueError("amount must be greater than 0")

            category = categorize_transaction(merchant)

            db_transaction = Transaction(
                date=transaction_date,
                merchant=merchant,
                description=description,
                amount=amount,
                transaction_type=transaction_type.value,
                category=category,
            )
            db.add(db_transaction)
            imported_count += 1

        except (KeyError, ValueError, InvalidOperation) as e:
            errors.append(f"Row {row_number}: {e}")

    db.commit()

    return {"imported": imported_count, "errors": errors}