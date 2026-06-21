import os
from flask import Flask, jsonify

app = Flask(__name__)

API_KEY = os.environ.get("EXTERNAL_API_KEY")

@app.route("/")
def health():
    return jsonify({"status": "ok"})

@app.route("/check-config")
def check_config():
    if API_KEY:
        return jsonify({"api_key_configured": True})
    return jsonify({"api_key_configured": False}), 500

# Sécurisé pour le dev local, Gunicorn prendra le relais pour Docker
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)