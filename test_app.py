import unittest
import sqlite3
import bcrypt
import os
import secrets
from app import app, verifier_authentification_utilisateur


class TestAuthenticationSecurity(unittest.TestCase):
    
    DB_TEST_PATH = "test_secure_users.db"
    
    def setUp(self):
        """Initialise une base de données de test et insère un utilisateur valide avant chaque test."""
        if os.path.exists(self.DB_TEST_PATH):
            os.remove(self.DB_TEST_PATH)
            
        with sqlite3.connect(self.DB_TEST_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL
                )
            """)
            
            # Génération d'un vrai hash bcrypt pour le test
            self.test_user = "alice"
            self.test_password = os.environ.get("TEST_USER_PASSWORD") or secrets.token_urlsafe(16)

            hashed_pw = bcrypt.hashpw(self.test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                (self.test_user, hashed_pw)
            )
            conn.commit()

    def tearDown(self):
        """Nettoie la base de données de test après chaque test."""
        if os.path.exists(self.DB_TEST_PATH):
            os.remove(self.DB_TEST_PATH)

    def test_succes_authentification(self):
        """Vérifie qu'un utilisateur avec les bons identifiants est authentifié avec succès."""
        resultat = verifier_authentification_utilisateur(self.test_user, self.test_password, self.DB_TEST_PATH)
        self.assertTrue(resultat)

    def test_echec_mauvais_mot_de_passe(self):
        """Vérifie qu'un mauvais mot de passe refuse l'accès."""
        resultat = verifier_authentification_utilisateur(self.test_user, "WrongPassword!", self.DB_TEST_PATH)
        self.assertFalse(resultat)

    def test_echec_utilisateur_inconnu(self):
        """Vérifie qu'un utilisateur inexistant refuse l'accès."""
        resultat = verifier_authentification_utilisateur("utilisateur_inconnu", self.test_password, self.DB_TEST_PATH)
        self.assertFalse(resultat)

    def test_echec_entrees_vides(self):
        """Vérifie le comportement sécurisé face à des entrées vides ou nulles."""
        self.assertFalse(verifier_authentification_utilisateur("", self.test_password, self.DB_TEST_PATH))
        self.assertFalse(verifier_authentification_utilisateur(self.test_user, "", self.DB_TEST_PATH))
        self.assertFalse(verifier_authentification_utilisateur("", "", self.DB_TEST_PATH))


class TestEndpoints(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_check_config_sans_variable(self):
        os.environ.pop("EXTERNAL_API_KEY", None)
        response = self.client.get("/check-config")
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.get_json()["external_api_key_configured"])

    def test_check_config_avec_variable(self):
        os.environ["EXTERNAL_API_KEY"] = "valeur-de-test"
        try:
            response = self.client.get("/check-config")
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.get_json()["external_api_key_configured"])
            self.assertNotIn("valeur-de-test", response.get_data(as_text=True))
        finally:
            os.environ.pop("EXTERNAL_API_KEY", None)


if __name__ == "__main__":
    unittest.main()