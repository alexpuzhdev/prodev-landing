import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path):
    os.environ["DB_PATH"] = str(tmp_path / "test.db")
    os.environ["ADMIN_PASSWORD"] = "test-password"
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ.pop("STATIC_DIR", None)
    from app.main import create_app

    with TestClient(create_app()) as c:
        yield c
