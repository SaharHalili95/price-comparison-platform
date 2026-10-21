from app.core.config import settings


def test_root_reports_api(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_checks_the_database(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["database"] == "ok"


def test_database_is_postgres():
    assert settings.DATABASE_URL.startswith("postgresql")
