from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_transaction_returns_201_with_assigned_category():
    payload = {
        "date": "2026-09-01",
        "merchant": "TESCO",
        "description": "Test transaction",
        "amount": "25.00",
        "transaction_type": "expense",
    }

    response = client.post("/transactions/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["merchant"] == "TESCO"
    assert data["category"] == "Groceries"
    assert "id" in data


def test_create_transaction_rejects_negative_amount():
    payload = {
        "date": "2026-09-01",
        "merchant": "TESCO",
        "amount": "-10.00",
        "transaction_type": "expense",
    }

    response = client.post("/transactions/", json=payload)

    assert response.status_code == 422  # FastAPI's validation error status code


def test_get_nonexistent_transaction_returns_404():
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/transactions/{fake_id}")
    assert response.status_code == 404


def test_create_then_delete_transaction():
    payload = {
        "date": "2026-09-01",
        "merchant": "UBER",
        "amount": "12.00",
        "transaction_type": "expense",
    }

    create_response = client.post("/transactions/", json=payload)
    transaction_id = create_response.json()["id"]

    delete_response = client.delete(f"/transactions/{transaction_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/transactions/{transaction_id}")
    assert get_response.status_code == 404