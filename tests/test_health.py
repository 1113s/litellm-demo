from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthz() -> None:
    response = client.get('/api/healthz')
    assert response.status_code == 503
    assert response.json() == {
        'error': {
            'code': 'HTTP_ERROR',
            'message': 'dependency check failed',
        }
    }


def test_swagger_docs_open() -> None:
    response = client.get('/docs')
    assert response.status_code == 200
