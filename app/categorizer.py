"""
Rule-based transaction categorisation.

Categorisation works by matching keywords found in the merchant name
(or description) against a lookup table. This keeps the categorisation
logic data-driven: adding support for a new merchant means adding one
entry to CATEGORY_RULES, not writing new code.
"""

DEFAULT_CATEGORY = "Uncategorised"

# Maps a keyword (checked case-insensitively against the merchant name)
# to the category it should be assigned. Add new rules here as needed.
CATEGORY_RULES: dict[str, str] = {
    "TESCO": "Groceries",
    "ALDI": "Groceries",
    "LIDL": "Groceries",
    "SAINSBURY": "Groceries",
    "ASDA": "Groceries",
    "UBER": "Transport",
    "BOLT": "Transport",
    "TRAINLINE": "Transport",
    "SHELL": "Fuel",
    "BP": "Fuel",
    "ESSO": "Fuel",
    "NETFLIX": "Entertainment",
    "SPOTIFY": "Entertainment",
    "DISNEY": "Entertainment",
    "AMAZON PRIME": "Entertainment",
}


def categorize_transaction(merchant: str) -> str:
    """
    Determine the category for a transaction based on its merchant name.

    Matching is case-insensitive and checks whether any known keyword
    appears anywhere in the merchant string. Returns DEFAULT_CATEGORY
    if no rule matches.
    """
    merchant_upper = merchant.upper()

    for keyword, category in CATEGORY_RULES.items():
        if keyword in merchant_upper:
            return category

    return DEFAULT_CATEGORY