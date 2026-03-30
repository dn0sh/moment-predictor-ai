# AI-generated: интеграционные тесты API (TestClient, SQLite :memory:)
import pytest
from fastapi.testclient import TestClient


def test_root(client: TestClient):
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data.get("service") == "Moment Predictor API"
    assert data.get("docs") == "/docs"
    assert data.get("health") == "/health"


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_register(client: TestClient):
    r = client.post("/api/auth/register", json={"username": "alice", "password": "secret123"})
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "alice"
    assert "id" in data
    assert data["total_points"] == 0


def test_login(client: TestClient):
    client.post("/api/auth/register", json={"username": "bob", "password": "pw1234"})
    r = client.post("/api/auth/login", json={"username": "bob", "password": "pw1234"})
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert r.json().get("token_type") == "bearer"


def test_register_duplicate(client: TestClient):
    body = {"username": "dup", "password": "x1234"}
    assert client.post("/api/auth/register", json=body).status_code == 200
    r2 = client.post("/api/auth/register", json=body)
    assert r2.status_code == 409
    assert r2.json().get("detail") == "Имя пользователя уже занято."


def test_login_invalid(client: TestClient):
    client.post("/api/auth/register", json={"username": "carl", "password": "ok1234"})
    r = client.post("/api/auth/login", json={"username": "carl", "password": "wrong"})
    assert r.status_code == 401


def _register_and_token(client: TestClient, username: str = "pred_user", password: str = "pw1234") -> str:
    client.post("/api/auth/register", json={"username": username, "password": password})
    r = client.post("/api/auth/login", json={"username": username, "password": password})
    return r.json()["access_token"]


def test_prediction_create(client: TestClient):
    token = _register_and_token(client)
    r = client.post(
        "/api/prediction",
        json={"video_id": "vid1", "video_timestamp": 42.5, "event_type": "goal"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["video_id"] == "vid1"
    assert data["video_timestamp"] == 42.5
    assert data["event_type"] == "goal"
    assert data["accuracy_score"] is None
    assert data.get("points_earned") == 100


def test_prediction_esports_ace_more_points(client: TestClient):
    token = _register_and_token(client, "ace_player")
    r = client.post(
        "/api/prediction",
        json={"video_id": "v_ace", "video_timestamp": 1.0, "event_type": "ace"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json().get("points_earned") == 150
    lb = client.get("/api/leaderboard").json()
    me = next(x for x in lb if x["username"] == "ace_player")
    assert me["total_points"] == 150


def test_prediction_requires_auth(client: TestClient):
    r = client.post(
        "/api/prediction",
        json={"video_id": "v", "video_timestamp": 1.0, "event_type": "goal"},
    )
    assert r.status_code == 401


def test_leaderboard(client: TestClient):
    token = _register_and_token(client, "leader1")
    client.post(
        "/api/prediction",
        json={"video_id": "v", "video_timestamp": 1.0, "event_type": "goal"},
        headers={"Authorization": f"Bearer {token}"},
    )
    r = client.get("/api/leaderboard")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) >= 1
    assert rows[0]["username"] == "leader1"
    assert rows[0]["total_points"] == 100


def test_predictions_own(client: TestClient):
    token = _register_and_token(client, "owner")
    pr = client.post(
        "/api/prediction",
        json={"video_id": "vx", "video_timestamp": 9.0, "event_type": "save"},
        headers={"Authorization": f"Bearer {token}"},
    )
    uid = pr.json()["user_id"]
    r = client.get(f"/api/predictions/{uid}", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["event_type"] == "save"


def test_predictions_other_forbidden(client: TestClient):
    t1 = _register_and_token(client, "user_a")
    t2 = _register_and_token(client, "user_b")
    pr = client.post(
        "/api/prediction",
        json={"video_id": "v", "video_timestamp": 1.0, "event_type": "goal"},
        headers={"Authorization": f"Bearer {t1}"},
    )
    uid_a = pr.json()["user_id"]
    r = client.get(f"/api/predictions/{uid_a}", headers={"Authorization": f"Bearer {t2}"})
    assert r.status_code == 403


def test_event_admin(client: TestClient):
    reg = client.post(
        "/api/auth/register", json={"username": "admin_flow", "password": "pw1234"}
    ).json()
    uid = reg["id"]
    token = client.post(
        "/api/auth/login", json={"username": "admin_flow", "password": "pw1234"}
    ).json()["access_token"]
    client.post(
        "/api/prediction",
        json={"video_id": "testvid", "video_timestamp": 10.0, "event_type": "goal"},
        headers={"Authorization": f"Bearer {token}"},
    )
    r = client.post(
        "/api/event",
        json={"video_id": "testvid", "timestamp": 25.0, "event_type": "goal", "confirmed_by_admin": True},
        headers={"X-Admin-Key": "pytest-admin-key"},
    )
    assert r.status_code == 200
    assert r.json()["video_id"] == "testvid"
    # accuracy = 1 - min(1, 15/30) = 0.5
    me = client.get(f"/api/predictions/{uid}", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    scored = me.json()[0]["accuracy_score"]
    assert scored is not None
    assert abs(scored - 0.5) < 1e-6


def test_event_no_admin_key(client: TestClient):
    r = client.post(
        "/api/event",
        json={"video_id": "x", "timestamp": 1.0, "event_type": "goal"},
    )
    assert r.status_code == 403


def test_event_wrong_admin_key(client: TestClient):
    r = client.post(
        "/api/event",
        json={"video_id": "x", "timestamp": 1.0, "event_type": "goal"},
        headers={"X-Admin-Key": "wrong-key"},
    )
    assert r.status_code == 403


def test_stats(client: TestClient):
    r = client.get("/api/stats")
    assert r.status_code == 200
    assert r.json()["total_users"] == 0
    _register_and_token(client, "stats_u")
    r2 = client.get("/api/stats")
    assert r2.json()["total_users"] == 1


@pytest.mark.skip(
    reason="Optional: run without TESTING=1 and exceed 10 req/min from one IP (manual / CI job)"
)
def test_rate_limit_optional_placeholder():
    assert False
