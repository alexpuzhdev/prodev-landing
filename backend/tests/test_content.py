def test_get_content_returns_seeded_texts(client):
    resp = client.get("/api/content")
    assert resp.status_code == 200
    data = resp.json()
    assert data["heroTitle"]["ru"] == "Цифровые продукты, которые запускаются в срок."
    assert data["heroTitle"]["en"] == "Digital products that ship on time."
    assert data["heroTitle"]["section"] == "Hero"
    assert len(data) >= 40
