#!/bin/bash

# Script de déploiement pour BornSafe

echo "🚀 Déploiement de BornSafe Backend"

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Créer l'environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install --upgrade pip
pip install -r bornsafe_backend/requirements.txt

# Variables d'environnement
if [ ! -f .env ]; then
    echo "⚠️  Fichier .env non trouvé, création à partir du modèle..."
    cp .env.example .env
    echo "⚠️  Veuillez éditer le fichier .env avec vos configurations"
fi

# Migrations
echo "🗃️  Application des migrations..."
cd bornsafe_backend
python manage.py migrate

# Créer le superuser
echo "👤 Création du super utilisateur..."
python manage.py createsuperuser

# Collecte des fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "✅ Déploiement terminé!"
echo "🌐 Pour lancer le serveur: cd bornsafe_backend && python manage.py runserver"
