def test_prompt_example_summary(client):
    """
    Prompt Example Scenario:
    - Salary: ₹50,000 (Income)
    - Rent: ₹15,000 (Expense)
    - Food: ₹4,500 (Expense)
    - Transport: ₹2,000 (Expense)

    Expected:
    Income: ₹50,000
    Expenses: ₹21,500
    Balance: ₹28,500
    """
    entries = [
        {"type": "income", "amount": 50000.00, "category": "Salary", "date": "2026-10-01", "description": "Salary"},
        {"type": "expense", "amount": 15000.00, "category": "Rent", "date": "2026-10-02", "description": "Rent"},
        {"type": "expense", "amount": 4500.00, "category": "Food", "date": "2026-10-03", "description": "Food"},
        {"type": "expense", "amount": 2000.00, "category": "Transport", "date": "2026-10-04", "description": "Transport"}
    ]

    for entry in entries:
        res = client.post("/api/transactions", json=entry)
        assert res.status_code == 201

    summary_res = client.get("/api/summary")
    assert summary_res.status_code == 200
    data = summary_res.json()

    assert float(data["total_income"]) == 50000.00
    assert float(data["total_expenses"]) == 21500.00
    assert float(data["remaining_balance"]) == 28500.00
    assert data["transaction_count"] == 4

    # Verify breakdown
    breakdown = {cat["category"]: float(cat["amount"]) for cat in data["expense_category_breakdown"]}
    assert breakdown["Rent"] == 15000.00
    assert breakdown["Food"] == 4500.00
    assert breakdown["Transport"] == 2000.00

def test_currency_conversion_behavior(client):
    """Test display currency conversion for USD/EUR/GBP (Item #4 & #15)."""
    client.post("/api/transactions", json={
        "type": "income", "amount": 100000.00, "category": "Salary", "date": "2026-10-01"
    })

    # USD Conversion (rate 0.012 -> 100,000 * 0.012 = 1200)
    usd_res = client.get("/api/summary?currency=USD")
    assert usd_res.status_code == 200
    usd_data = usd_res.json()
    assert usd_data["currency"] == "USD"
    assert float(usd_data["total_income"]) == 1200.00

def test_unsupported_currency_error(client):
    res = client.get("/api/summary?currency=INVALID")
    assert res.status_code == 400
    assert "unsupported currency" in res.json()["detail"].lower()

def test_invalid_month_summary_error(client):
    res1 = client.get("/api/summary?month=2025-00")
    assert res1.status_code == 422

    res2 = client.get("/api/summary?month=2025-19")
    assert res2.status_code == 422
