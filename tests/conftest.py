import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    from pomelo_api import config

    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "pomelo.db")
    monkeypatch.setattr(config, "UPLOAD_DIR", tmp_path / "uploads")
    from pomelo_api.main import app

    with TestClient(app) as c:
        yield c


def login(client, email, password):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def maya(client):
    return login(client, "maya.patel@example.com", "pomelo123")


@pytest.fixture()
def clinician(client):
    return login(client, "dr.rivera@pomelocare.example", "clinician123")
