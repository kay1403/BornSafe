FROM python:3.11-slim

WORKDIR /app

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=bornsafe_backend.settings

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY bornsafe_backend/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copie du projet
COPY . .

# Exposition du port
EXPOSE 8000

# Commande de démarrage
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "bornsafe_backend.wsgi:application"]
