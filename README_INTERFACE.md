# BornSafe Interface d'Administration - Mairie du Gabon

## 🎨 Interface utilisateur avec Tailwind CSS

### Installation

1. **Installer Tailwind CSS**
```bash
cd bornsafe_backend
./install_tailwind.sh
Configurer Django
Ajoutez dans settings.py :
python
import os

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'bornsafe_backend.context_processors.site_info',
            ],
        },
    },
]

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
Compiler Tailwind
bash
# Mode développement (avec auto-reload)
npm run watch

# Mode production (minifié)
npm run build
🎯 Fonctionnalités

Pour les agents de mairie

✅ Tableau de bord avec statistiques
✅ Gestion complète des actes de naissance
✅ Création et modification d'actes
✅ Validation des actes
✅ Génération PDF et QR code
✅ Recherche avancée
Pour les administrateurs

✅ Gestion des provinces du Gabon
✅ Gestion des utilisateurs
✅ Statistiques détaillées
✅ Configuration système
Pour les super admins

✅ Toutes les fonctionnalités
✅ Gestion des rôles
✅ Audit et logs
✅ Sauvegardes
🗺️ Adaptation pour le Gabon

L'interface est spécialement conçue pour les mairies du Gabon avec :

🇬🇦 Couleurs du drapeau gabonais (vert, jaune, bleu)
🗺️ Toutes les provinces pré-configurées
📅 Format de date localisé
📞 Format de téléphone adapté (+241)
🌍 Support des spécificités locales
📁 Structure des templates

text
templates/
├── base/
│   └── base.html           # Template de base
├── accounts/
│   ├── login.html           # Page de connexion
│   └── profil.html          # Profil utilisateur
├── actes/
│   ├── liste.html           # Liste des actes
│   ├── detail.html          # Détail d'un acte
│   └── formulaire.html      # Création/modification
├── provinces/
│   └── liste.html           # Gestion des provinces
├── dashboard.html           # Tableau de bord
└── statistiques.html        # Statistiques avancées
🚀 Déploiement

Collecte des fichiers statiques
bash
python manage.py collectstatic
Configuration Nginx
nginx
location /static/ {
    alias /chemin/vers/staticfiles/;
}

location /media/ {
    alias /chemin/vers/media/;
}
🎨 Personnalisation

Thème

Les couleurs peuvent être modifiées dans tailwind.config.js :

javascript
colors: {
  'gabon-flag-green': '#VOTRE_COULEUR',
  'gabon-flag-yellow': '#VOTRE_COULEUR',
  'gabon-flag-blue': '#VOTRE_COULEUR',
}
Composants

Tous les composants sont définis dans static/css/input.css et peuvent être personnalisés.

📱 Responsive Design

L'interface est entièrement responsive :

📱 Mobile : menu hamburger, colonnes empilées
💻 Desktop : navigation complète, grilles
🖥️ Grand écran : mise en page optimisée
🔒 Sécurité

Authentification requise pour toutes les pages
Gestion fine des permissions par rôle
Protection CSRF sur tous les formulaires
Sessions sécurisées
Rate limiting sur les tentatives de connexion
🌐 URLs disponibles

text
/                           # Redirection vers dashboard
/dashboard/                 # Tableau de bord
/accounts/login/            # Connexion
/accounts/logout/           # Déconnexion
/accounts/profil/           # Profil utilisateur
/actes/                     # Liste des actes
/actes/nouveau/             # Création d'acte
/actes/<id>/                # Détail d'acte
/provinces/                 # Gestion provinces
/statistiques/              # Statistiques
🧪 Tests

bash
# Tester les templates
python manage.py test templates.tests

# Vérifier les URLs
python manage.py show_urls | grep -E "dashboard|actes|provinces"
📦 Dépendances

Django 5.2+
Tailwind CSS 3.4.1
Alpine.js (pour les interactions)
Chart.js (pour les graphiques)
Font Awesome (icônes)
🆘 Support

Pour toute question ou assistance :

📧 Email : support@bornsafe.ga
📞 Téléphone : +241 01 23 45 67
🌐 Site : https://bornsafe.ga
Développé avec ❤️ pour les mairies de la République Gabonaise
