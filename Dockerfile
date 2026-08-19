FROM python:3.14-slim

# 1. Variables d'environnement pour optimiser Python en conteneur
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

# 2. Mise à jour des paquets système (corrige les CVE connues) PUIS installation des dépendances Python
# pip embarque en interne (pip/_vendor) une copie figée de setuptools et msgpack contenant
# des CVE connues (CVE-2025-47273, CVE-2026-59890, GHSA-6v7p-g79w-8964), non corrigeables via
# `pip install --upgrade` puisqu'elles sont vendorisées dans pip lui-même, pas installées à part.
# Comme pip n'est utile qu'au build (jamais à l'exécution par gunicorn), on le désinstalle une
# fois les dépendances posées : ça élimine ces CVE et réduit la surface de l'image finale.
RUN apt-get update && apt-get upgrade -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt && \
    pip uninstall --yes pip setuptools wheel

COPY app.py .

# 3. SÉCURITÉ CRITIQUE : Création d'un utilisateur non-root
# Checkov lèvera une alerte rouge si cette étape est manquante.
RUN useradd -u 8888 -m -d /home/appuser appuser && chown -R appuser:appuser /app /home/appuser
USER appuser

EXPOSE 5000

# 4. Healthcheck sur l'endpoint applicatif dédié
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=2)" || exit 1

# 5. On utilise Gunicorn au lieu de "python app.py"
# C'est ici qu'on lie l'application à 0.0.0.0 pour que Docker expose le port.
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "app:app"]