def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_login_rejects_bad_password(client):
    r = client.post("/auth/login", json={"email": "maya.patel@example.com", "password": "nope"})
    assert r.status_code == 401


def test_signup_then_profile(client):
    r = client.post("/auth/signup", json={
        "email": "new@example.com", "password": "pw123456", "first_name": "Ava",
        "last_name": "Kim", "date_of_birth": "1995-01-01",
    })
    assert r.status_code == 201
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    assert client.get("/patients/me", headers=headers).json()["first_name"] == "Ava"


def test_my_profile(client, maya):
    r = client.get("/patients/me", headers=maya)
    assert r.status_code == 200
    assert r.json()["last_name"] == "Patel"


def test_update_profile(client, maya):
    r = client.patch("/patients/me", json={"phone": "+1-512-555-0000"}, headers=maya)
    assert r.json()["phone"] == "+1-512-555-0000"


def test_care_team_messages(client, maya):
    r = client.post("/care-teams/1/messages", json={"body": "Hi team"}, headers=maya)
    assert r.status_code == 201
    bodies = [m["body"] for m in client.get("/care-teams/1/messages", headers=maya).json()]
    assert "Hi team" in bodies


def test_provider_search(client, maya):
    r = client.get("/providers/search", params={"state": "TX"}, headers=maya)
    names = [p["name"] for p in r.json()]
    assert "Dr. Ana Rivera" in names and "Dr. Sam Okafor" not in names


def test_insurance_card_roundtrip(client, maya):
    r = client.post(
        "/documents/insurance-card",
        files={"file": ("card.png", b"\x89PNG fake", "image/png")},
        data={"side": "front"},
        headers=maya,
    )
    assert r.status_code == 201
    r = client.get("/documents/1/card.png", headers=maya)
    assert r.content == b"\x89PNG fake"


def test_care_plan_template_requires_clinician(client, maya, clinician):
    yaml_body = "name: GDM monitoring\nsteps:\n  - fasting glucose daily\n  - nutrition consult\n"
    hdr = {"Content-Type": "text/plain"}
    assert client.post("/care-plans/templates", content=yaml_body, headers={**maya, **hdr}).status_code == 403
    r = client.post("/care-plans/templates", content=yaml_body, headers={**clinician, **hdr})
    assert r.status_code == 201 and r.json()["steps"] == 2
