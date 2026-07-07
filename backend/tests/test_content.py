def test_get_content_returns_seeded_texts(client):
    resp = client.get("/api/content")
    assert resp.status_code == 200
    data = resp.json()
    assert data["heroTitle"]["ru"] == "Цифровые продукты, которые запускаются в срок."
    assert data["heroTitle"]["en"] == "Digital products that ship on time."
    assert data["heroTitle"]["section"] == "Hero"
    assert len(data) >= 40


def test_put_content_requires_auth(client):
    resp = client.put("/api/content/heroTitle", json={"ru": "x", "en": "y"})
    assert resp.status_code == 401


def test_put_content_updates_value(client):
    client.post("/api/auth/login", json={"password": "test-password"})
    resp = client.put(
        "/api/content/heroTitle", json={"ru": "Новый заголовок", "en": "New title"}
    )
    assert resp.status_code == 200
    assert resp.json() == {"key": "heroTitle", "ru": "Новый заголовок", "en": "New title"}
    data = client.get("/api/content").json()
    assert data["heroTitle"]["ru"] == "Новый заголовок"


def test_put_unknown_key_404(client):
    client.post("/api/auth/login", json={"password": "test-password"})
    resp = client.put("/api/content/noSuchKey", json={"ru": "x", "en": "y"})
    assert resp.status_code == 404
