# Personal Finance Tracker API

A backend REST API for managing, categorising and analysing personal financial transactions, built with Python, FastAPI and PostgreSQL.

I built this project to develop my backend software engineering skills and gain practical experience working with REST APIs, relational databases, data validation and automated testing.

The application allows financial transactions to be stored in PostgreSQL, automatically categorised and analysed to provide insights into spending patterns and potential recurring payments.

## Features

- Create and store financial transactions
- Retrieve all transactions
- Retrieve individual transactions by ID
- Delete transactions
- Automatically categorise transactions based on merchant information
- Bulk import transactions from CSV files
- Calculate monthly financial summaries
- Analyse spending by category
- Detect potential recurring payments
- Validate incoming data using Pydantic
- Handle invalid requests and file uploads
- Automated testing with pytest

## Tech Stack

`Python` `FastAPI` `PostgreSQL` `SQLAlchemy` `Pydantic` `pytest` `Git`

## Project Structure

```text
personal-finance-tracker-api/
│
├── app/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── analytics.py
│   │   └── transactions.py
│   │
│   ├── __init__.py
│   ├── analytics.py
│   ├── categorizer.py
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── sample_data/
│   └── transactions.csv
│
├── tests/
│   ├── test_analytics.py
│   ├── test_categorizer.py
│   └── test_transactions.py
│
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Architecture

The application uses a modular architecture to keep different responsibilities separated.

The API routes handle HTTP requests and responses, while database operations are separated into their own layer. SQLAlchemy models define how transaction data is stored in PostgreSQL, while Pydantic schemas validate data entering and leaving the API.

Transaction categorisation and financial analytics are implemented as separate modules rather than being placed directly inside the API routes.

This separation makes the application easier to understand, maintain and test.

## API Endpoints

### Transactions

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/transactions/` | Create a new transaction |
| `GET` | `/transactions/` | Retrieve all transactions |
| `GET` | `/transactions/{transaction_id}` | Retrieve a transaction by ID |
| `DELETE` | `/transactions/{transaction_id}` | Delete a transaction |
| `POST` | `/transactions/import` | Import transactions from a CSV file |

### Analytics

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/analytics/monthly` | Generate a monthly financial summary |
| `GET` | `/analytics/categories` | Analyse spending by category |
| `GET` | `/analytics/recurring` | Identify potential recurring payments |

## Transaction Categorisation

Transactions are automatically categorised using merchant information.

Example categorisation:

```text
TESCO       -> Groceries
ALDI        -> Groceries
UBER        -> Transport
SHELL       -> Fuel
NETFLIX     -> Entertainment
SPOTIFY     -> Entertainment
```

The categorisation logic is kept separate from the API routes, making it easier to add new merchants and categories without modifying the endpoint logic.

Matching is case-insensitive and can identify known merchants even when additional information appears within the merchant name.

Unknown merchants are assigned a default category.

## Financial Analytics

The analytics layer processes stored transaction data to generate useful information about financial activity.

The application can calculate and analyse:

- Total income
- Total expenses
- Net savings
- Savings rate
- Spending by category
- Monthly financial activity
- Potential recurring payments

Income and expenses are treated separately so that spending analysis is not distorted by incoming payments.

## Recurring Payment Detection

The application analyses transaction history to identify transactions that may represent recurring payments.

Recurring detection considers repeated merchant activity and the consistency of transaction amounts across different periods.

This can help identify payments such as subscriptions and memberships.

The implementation is intentionally heuristic, meaning unusual payment schedules or changing subscription prices may not always be detected correctly.

## CSV Import

Transactions can be imported in bulk using a CSV file.

Expected fields include:

```text
date
merchant
description
amount
transaction_type
```

Uploaded files are validated before being processed.

The API rejects unsupported file types and handles files that cannot be decoded as valid UTF-8 text with an appropriate HTTP error response.

## Getting Started

### Requirements

Before running the application, ensure you have:

- Python
- PostgreSQL
- pip
- Git

installed on your system.

### Clone the Repository

```bash
git clone https://github.com/ibrahimilyas-dev/personal-finance-tracker-api.git
cd personal-finance-tracker-api
```

### Create a Virtual Environment

On Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

### Install Dependencies

```powershell
pip install -r requirements.txt
```

## Database Configuration

The application uses PostgreSQL for persistent transaction storage.

Create a PostgreSQL database for the application and configure the connection using an environment variable.

Create a `.env` file in the project directory.

Example:

```text
DATABASE_URL=postgresql://username:password@localhost:5432/finance_tracker
```

Replace the example username, password and database name with your own PostgreSQL configuration.

The real `.env` file should never be committed to GitHub.

## Running the Application

Start the FastAPI development server using:

```powershell
uvicorn app.main:app --reload
```

Once the application is running, FastAPI provides interactive API documentation through Swagger UI.

This interface can be used to inspect and test the available API endpoints directly from a browser.

## Running Tests

The project includes an automated test suite built using pytest.

Run all tests with:

```powershell
pytest -v
```

The current test suite contains 16 automated tests covering areas including:

- Transaction creation
- Transaction retrieval
- Transaction deletion
- Invalid transaction data
- Missing transactions
- Merchant categorisation
- Case-insensitive categorisation
- Unknown merchants
- Monthly financial calculations
- Category breakdowns
- Recurring payment detection
- API endpoint behaviour

All 16 tests currently pass.

## Engineering Decisions

### Decimal Values for Financial Data

Financial applications require accurate representation of monetary values.

Using standard floating-point numbers for money can introduce small precision errors. Decimal values are therefore used where appropriate to make financial calculations more predictable.

### Separate Database and API Models

SQLAlchemy models represent how information is stored in PostgreSQL, while Pydantic schemas define and validate the information accepted and returned by the API.

Keeping these responsibilities separate prevents database implementation details from becoming tightly coupled to the public API.

### Separation of Business Logic

Transaction categorisation and financial analytics are kept separate from the HTTP routing layer.

Routes are responsible for receiving requests and returning responses, while dedicated modules perform the underlying application logic.

This makes individual components easier to test and reduces unnecessary dependencies between different parts of the application.

### Rule-Based Categorisation

Transaction categories are assigned using explicit merchant matching rules.

For the current scope of the project, a rule-based approach provides predictable and explainable behaviour without requiring an external service or machine learning model.

The categorisation system can also be extended by adding additional merchants and categories.

### Heuristic Recurring Payment Detection

Recurring transactions are identified by analysing patterns within transaction history.

The current implementation considers factors such as merchant information and transaction amounts to determine whether payments appear consistently.

This keeps the detection logic understandable and testable while acknowledging that real financial activity does not always follow perfectly regular patterns.

## Error Handling

The API handles a number of invalid inputs and expected failure scenarios.

These include:

- Requesting a transaction that does not exist
- Attempting to delete a transaction that does not exist
- Providing invalid transaction information
- Uploading an unsupported file type
- Uploading CSV content that is not valid UTF-8 text

Appropriate HTTP status codes and error messages are returned to the client.

## Automated Testing

Testing was included throughout development rather than being treated only as a final step.

The test suite covers the API, categorisation system and analytics functionality.

Tests include both expected behaviour and edge cases, such as:

- Unknown merchants
- Different merchant capitalisation
- Months with no income
- Inconsistent recurring transaction amounts
- Non-existent transaction IDs
- Invalid transaction values

This allows changes to be made to the application while checking that existing functionality continues to behave correctly.

## Current Limitations

The current version focuses primarily on backend functionality.

Current limitations include:

- No user authentication
- No frontend interface
- No database migration system
- CSV imports are not automatically deduplicated
- Categorisation relies on predefined merchant rules
- Recurring payment detection may miss irregular payments
- Recurring detection may produce false positives in certain cases
- Database isolation within automated tests could be improved

## Future Improvements

Possible future improvements include:

- Add user authentication and individual user accounts
- Introduce Alembic database migrations
- Add duplicate transaction detection during CSV imports
- Add transaction updating
- Add transaction filtering and searching
- Add pagination for larger transaction datasets
- Store categorisation rules within PostgreSQL
- Improve recurring payment detection
- Add configurable spending categories
- Add budgeting functionality
- Develop a React frontend dashboard
- Add financial charts and visualisations
- Introduce isolated test databases and reusable fixtures
- Deploy the application to a cloud platform

## What I Learned

Building this project gave me practical experience designing a backend application beyond individual programming exercises.

I developed a stronger understanding of how REST APIs interact with relational databases and how FastAPI, SQLAlchemy and Pydantic can be used together while maintaining separate responsibilities.

Building the analytics and categorisation components gave me experience translating application requirements into independent pieces of business logic that could be tested separately from the API.

I also gained practical experience with automated testing using pytest. Writing tests for both expected behaviour and edge cases helped me understand how a test suite can make it safer to modify and extend an application.

The project also improved my understanding of Git, API design, validation, error handling and structuring a Python application so that it can be understood and extended by other developers.

## Author

**Ibrahim Imran Ilyas**

MSci Software Engineering  
University of Glasgow

[LinkedIn](https://www.linkedin.com/in/ibrahim-ilyas/)