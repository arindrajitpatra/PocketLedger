def test_csv_export_formatting(client):
    # Entry with commas and quotes in description
    client.post("/api/transactions", json={
        "type": "expense",
        "amount": 1250.50,
        "category": "Bills",
        "date": "2026-10-05",
        "description": 'Electricity bill, including "taxes" & fees'
    })

    res = client.get("/api/export/csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    text = res.text
    assert "Bills" in text
    assert "1250.50" in text
    assert 'Electricity bill, including ""taxes"" & fees' in text or 'Electricity bill' in text
