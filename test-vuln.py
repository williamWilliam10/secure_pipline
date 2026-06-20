import subprocess
import re
from flask import Flask, request

app = Flask(__name__)


@app.route("/run")
def run_command():
    user_input = request.args.get("host")

    # Validation stricte de l'entrée : uniquement des caractères autorisés
    # pour un nom d'hôte ou une adresse IP (lettres, chiffres, points, tirets)
    if not user_input or not re.fullmatch(r"[a-zA-Z0-9.\-]+", user_input):
        return "Entrée invalide", 400

    # subprocess.run avec une liste d'arguments : pas de shell, pas de concaténation
    # Le système ne peut pas interpréter user_input comme une commande supplémentaire
    result = subprocess.run(
        ["ping", "-c", "4", user_input],
        capture_output=True,
        text=True,
        timeout=10
    )

    return result.stdout