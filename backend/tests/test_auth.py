def test_login_wrong_password_401(client):
    resp = client.post("/api/auth/login", json={"password": "wrong"})
    assert resp.status_code == 401


def test_login_ok_sets_cookie_and_me_works(client):
    assert client.get("/api/auth/me").status_code == 401
    resp = client.post("/api/auth/login", json={"password": "test-password"})
    assert resp.status_code == 200
    assert "prodev_session" in resp.cookies
    assert client.get("/api/auth/me").status_code == 200


def test_logout_clears_session(client):
    client.post("/api/auth/login", json={"password": "test-password"})
    client.post("/api/auth/logout")
    assert client.get("/api/auth/me").status_code == 401
