from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.analytics import calculate_category_breakdown, calculate_monthly_summary
from app.database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/monthly")
def get_monthly_analytics(db: Session = Depends(get_db)):
    """Return income, expenses, net savings, and savings rate per month."""
    transactions = crud.get_transactions(db)
    return calculate_monthly_summary(transactions)


@router.get("/categories")
def get_category_analytics(db: Session = Depends(get_db)):
    """Return total spending per category, sorted highest to lowest."""
    transactions = crud.get_transactions(db)
    return calculate_category_breakdown(transactions)