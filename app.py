# app.py
import os
from flask import Flask, jsonify

app = Flask(__name__)

# Le secret est lu depuis une variable d'environnement au RUNTIME
# Jamais écrit en dur dans le code, jamais dans l'image Docker
API_KEY = os.environ.get("EXTERNAL_API_KEY")

@app.route("/")
def health():
    return jsonify({"status": "ok"})

@app.route("/check-config")
def check_config():
    # On ne révèle JAMAIS le secret lui-même, juste sa présence
    # C'est une bonne pratique : ne jamais exposer un secret dans une réponse, même en debug
    if API_KEY:
        return jsonify({"api_key_configured": True})
    return jsonify({"api_key_configured": False}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)