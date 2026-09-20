import uuid

from sqlalchemy.orm import Session

from app.models import Transaction
from app.schemas import TransactionCreate


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