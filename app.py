import os
import sqlite3

import bcrypt
from flask import Flask, jsonify

app = Flask(__name__)


def verifier_authentification_utilisateur(nom_utilisateur: str, mot_passe_fourni: str, db_path: str = "secure_users.db") -> bool:
    """
    Version intentionnellement vulnérable (Injection SQL), utilisée comme cible
    pédagogique pour les scans SAST du pipeline (Semgrep) et les tests unitaires.

    Volontairement jamais exposée via une route HTTP de l'application.

    Vulnérabilités introduites :
    - A03:2021 (Injection SQL) : Concaténation directe des variables dans la requête
      au lieu d'utiliser des requêtes paramétrées.
    """
    if not nom_utilisateur or not mot_passe_fourni:
        return False

    try:
        with sqlite3.connect(db_path) as connexion:
            curseur = connexion.cursor()

            # VULNÉRABILITÉ : Concaténation directe permettant une injection SQL
            requete = f"SELECT password_hash FROM users WHERE username = '{nom_utilisateur}'"
            curseur.execute(requete)

            resultat = curseur.fetchone()

            if not resultat:
                return False

            stocke_hash_bytes = resultat[0].encode("utf-8")
            fourni_bytes = mot_passe_fourni.encode("utf-8")

            if bcrypt.checkpw(fourni_bytes, stocke_hash_bytes):
                return True

    except sqlite3.Error:
        pass
    except Exception:
        pass

    return False


@app.get("/health")
def health():
    """Liveness check utilisé par la plateforme de déploiement (Render)."""
    return jsonify(status="ok")


@app.get("/check-config")
def check_config():
    """Vérifie qu'une configuration requise est bien injectée via l'environnement,
    sans jamais exposer sa valeur — utile pour valider un déploiement sans fuiter de secret."""
    is_configured = bool(os.environ.get("EXTERNAL_API_KEY"))
    status_code = 200 if is_configured else 503
    return jsonify(external_api_key_configured=is_configured), status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
