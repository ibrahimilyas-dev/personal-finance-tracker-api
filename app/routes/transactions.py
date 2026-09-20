import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app import crud
from app.categorizer import categorize_transaction
from app.database import get_db
from app.schemas import TransactionCreate, TransactionRead

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """Create a new transaction, automatically assigning its category
    based on the merchant name."""
    category = categorize_transaction(transaction.merchant)
    db_transaction = crud.create_transaction(db, transaction, category=category)
    return db_transaction


@router.get("/", response_model=list[TransactionRead])
def list_transactions(db: Session = Depends(get_db)):
    """Return all transactions."""
    return crud.get_transactions(db)


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: uuid.UUID, db: Session = Depends(get_db)):
    """Return a single transaction by ID, or 404 if it doesn't exist."""
    db_transaction = crud.get_transaction_by_id(db, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return db_transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete a transaction by ID, or 404 if it doesn't exist."""
    deleted = crud.delete_transaction(db, transaction_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")


@router.post("/import")
async def import_transactions(file: UploadFile, db: Session = Depends(get_db)):
    """
    Bulk-import transactions from an uploaded CSV file.

    Expected CSV columns: date, merchant, description, amount, transaction_type
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a CSV")

    content = await file.read()

    try:
        csv_content = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is not valid UTF-8 text")

    result = crud.import_transactions_from_csv(db, csv_content)
    return result