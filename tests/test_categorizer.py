from app.categorizer import categorize_transaction


def test_known_grocery_merchant_returns_groceries_category():
    assert categorize_transaction("TESCO") == "Groceries"


def test_known_transport_merchant_returns_transport_category():
    assert categorize_transaction("UBER") == "Transport"


def test_case_insensitive_matching():
    assert categorize_transaction("tesco") == "Groceries"
    assert categorize_transaction("Tesco Express") == "Groceries"


def test_merchant_with_extra_text_still_matches():
    """Real bank exports often include store numbers/locations."""
    assert categorize_transaction("TESCO STORES 2345 LONDON") == "Groceries"


def test_unknown_merchant_returns_default_category():
    assert categorize_transaction("SOME RANDOM SHOP") == "Uncategorised"