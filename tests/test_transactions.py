def test_create_and_read_transaction(client):
    payload = {
        "type": "income",
        "amount": 50000.00,
        "category": "Salary",
        "date": "2026-10-01",
        "description": "Monthly Salary"
    }
    response = client.post("/api/transactions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert float(data["amount"]) == 50000.00
    assert data["type"] == "income"

    # Get single transaction
    tx_id = data["id"]
    get_res = client.get(f"/api/transactions/{tx_id}")
    assert get_res.status_code == 200
    assert get_res.json()["category"] == "Salary"

def test_transaction_validation_errors(client):
    # Invalid amount <= 0
    res1 = client.post("/api/transactions", json={
        "type": "expense", "amount": 0, "category": "Food", "date": "2026-10-01"
    })
    assert res1.status_code == 422

    # Negative amount
    res1_neg = client.post("/api/transactions", json={
        "type": "expense", "amount": -50.00, "category": "Food", "date": "2026-10-01"
    })
    assert res1_neg.status_code == 422

    # Invalid type
    res2 = client.post("/api/transactions", json={
        "type": "invalid_type", "amount": 100, "category": "Food", "date": "2026-10-01"
    })
    assert res2.status_code == 422

    # Empty category
    res3 = client.post("/api/transactions", json={
        "type": "expense", "amount": 100, "category": "   ", "date": "2026-10-01"
    })
    assert res3.status_code == 422

def test_invalid_month_filters(client):
    # Month 00
    res1 = client.get("/api/transactions?month=2025-00")
    assert res1.status_code == 422

    # Month 19
    res2 = client.get("/api/transactions?month=2025-19")
    assert res2.status_code == 422

def test_update_and_delete_transaction(client):
    create_res = client.post("/api/transactions", json={
        "type": "expense", "amount": 15000.00, "category": "Rent", "date": "2026-10-02", "description": "Initial note"
    })
    tx_id = create_res.json()["id"]

    # Update
    update_res = client.put(f"/api/transactions/{tx_id}", json={"amount": 16000.00})
    assert update_res.status_code == 200
    assert float(update_res.json()["amount"]) == 16000.00

    # Clear description explicitly setting to null (Item #6 & #15)
    clear_res = client.put(f"/api/transactions/{tx_id}", json={"description": None})
    assert clear_res.status_code == 200
    assert clear_res.json()["description"] is None

    # Empty update payload (Item #11 & #15)
    empty_up_res = client.put(f"/api/transactions/{tx_id}", json={})
    assert empty_up_res.status_code == 400
    assert "at least one field must be provided" in empty_up_res.json()["detail"].lower()

    # Delete
    del_res = client.delete(f"/api/transactions/{tx_id}")
    assert del_res.status_code == 204

    # 404 check (Item #15)
    get_res = client.get(f"/api/transactions/{tx_id}")
    assert get_res.status_code == 404
    assert "not found" in get_res.json()["detail"].lower()

def test_transaction_pagination(client):
    # Create 5 entries
    for i in range(5):
        client.post("/api/transactions", json={
            "type": "expense", "amount": 100 + i, "category": "Test", "date": "2026-10-01"
        })

    # Page 1 limit 2
    res = client.get("/api/transactions?page=1&limit=2")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["total_pages"] == 3
    assert data["page"] == 1
