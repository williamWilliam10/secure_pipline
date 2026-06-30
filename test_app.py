import pytest
from app import app


@pytest.fixture
def client():
    """
    Crée un client de test Flask, qui simule des requêtes HTTP
    sans avoir besoin de lancer un vrai serveur.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check_status_code(client):
    """La route / doit répondre avec un code 200 (OK)."""
    response = client.get("/")
    assert response.status_code == 200


def test_health_check_content(client):
    """La route / doit renvoyer un JSON contenant le statut 'ok'."""
    response = client.get("/")
    data = response.get_json()
    assert data["status"] == "ok"


def test_check_config_with_api_key(client, monkeypatch):
    """
    Si la variable d'environnement EXTERNAL_API_KEY est définie,
    /check-config doit répondre 200 avec api_key_configured=True.
    """
    monkeypatch.setenv("EXTERNAL_API_KEY", "fausse-cle-de-test")
    # On doit recharger le module pour que os.environ.get soit relu
    import importlib
    import app as app_module
    importlib.reload(app_module)

    with app_module.app.test_client() as test_client:
        response = test_client.get("/check-config")
        assert response.status_code == 200
        assert response.get_json()["api_key_configured"] is True


def test_check_config_without_api_key(client, monkeypatch):
    """
    Si EXTERNAL_API_KEY n'est pas définie, /check-config doit
    répondre 500 avec api_key_configured=False.
    """
    monkeypatch.delenv("EXTERNAL_API_KEY", raising=False)
    import importlib
    import app as app_module
    importlib.reload(app_module)

    with app_module.app.test_client() as test_client:
        response = test_client.get("/check-config")
        assert response.status_code == 500
        assert response.get_json()["api_key_configured"] is False


def test_check_config_never_exposes_the_real_key(client, monkeypatch):
    """
    Test de sécurité : même si la clé est configurée, la réponse
    ne doit JAMAIS contenir sa valeur réelle, juste un booléen.
    """
    secret_value = "valeur-secrete-ne-doit-jamais-apparaitre"
    monkeypatch.setenv("EXTERNAL_API_KEY", secret_value)
    import importlib
    import app as app_module
    importlib.reload(app_module)

    with app_module.app.test_client() as test_client:
        response = test_client.get("/check-config")
        assert secret_value not in response.get_data(as_text=True)