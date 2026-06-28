FROM python:3.12-alpine

# 1. Variables d'environnement pour optimiser Python en conteneur
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

# 2. Mise à jour des paquets système (corrige les CVE connues) PUIS installation des dépendances Python
RUN apt-get update && apt-get upgrade -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

COPY app.py .

# 3. SÉCURITÉ CRITIQUE : Création d'un utilisateur non-root
# Checkov lèvera une alerte rouge si cette étape est manquante.
RUN useradd -u 8888 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# 4. On utilise Gunicorn au lieu de "python app.py"
# C'est ici qu'on lie l'application à 0.0.0.0 pour que Docker expose le port.
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "app:app"]