import os
import sqlite3

import bcrypt
from flask import Flask, jsonify

app = Flask(__name__)


def verifier_authentification_utilisateur(nom_utilisateur: str, mot_passe_fourni: str, db_path: str = "secure_users.db") -> bool:
    """
    Vérifie les identifiants d'un utilisateur contre la base SQLite (mots de passe
    hashés avec bcrypt), en se protégeant de l'injection SQL (A03:2021) via une
    requête paramétrée.
    """
    if not nom_utilisateur or not mot_passe_fourni:
        return False

    try:
        with sqlite3.connect(db_path) as connexion:
            curseur = connexion.cursor()

            curseur.execute(
                "SELECT password_hash FROM users WHERE username = ?",
                (nom_utilisateur,),
            )

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
    # Serveur de dev Werkzeug : lié à localhost par défaut pour ne jamais exposer
    # publiquement par accident. Utiliser gunicorn (voir Dockerfile) pour tout
    # déploiement réel — c'est aussi ce que fait le conteneur de production.
    app.run(host=os.environ.get("FLASK_RUN_HOST", "127.0.0.1"), port=5000)
