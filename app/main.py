from fastapi import FastAPI

from app.routes import transactions

app = FastAPI(
    title="Personal Finance Tracker API",
    description="A REST API for tracking personal transactions, categorising spending, and generating financial analytics.",
    version="0.1.0",
)

app.include_router(transactions.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Simple endpoint to confirm the API is running."""
    return {"status": "ok"}