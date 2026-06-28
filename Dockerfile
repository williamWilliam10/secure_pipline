FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

# apk au lieu de apt-get : mise à jour des paquets système Alpine
RUN apk update && apk upgrade && \
    apk add --no-cache gcc musl-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

COPY app.py .

RUN adduser -u 8888 -D appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "app:app"]