# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Le secret EXTERNAL_API_KEY n'est PAS défini ici avec ENV
# Il sera injecté au moment du "docker run", pas au moment du "docker build"
EXPOSE 5000

CMD ["python", "app.py"]