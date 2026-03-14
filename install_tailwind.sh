#!/bin/bash

echo "🚀 Installation de Tailwind CSS pour BornSafe"

cd bornsafe_backend

# Vérifier si Node.js est installé
if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé"
    echo "📦 Installation via Homebrew..."
    brew install node
fi

# Vérifier si npm est installé
if ! command -v npm &> /dev/null; then
    echo "❌ npm n'est pas installé"
    exit 1
fi

# Initialiser package.json si nécessaire
if [ ! -f package.json ]; then
    echo "📦 Initialisation de package.json..."
    npm init -y
fi

# Installer Tailwind CSS
echo "📦 Installation de Tailwind CSS v3.4.1..."
npm install -D tailwindcss@3.4.1 @tailwindcss/forms @tailwindcss/typography @tailwindcss/aspect-ratio

# Créer le fichier de configuration Tailwind
echo "⚙️  Création de tailwind.config.js..."
cat > tailwind.config.js << 'TAILWIND'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './templates/**/*.js',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        'gabon-green': '#3A7734',
        'gabon-yellow': '#FCD116',
        'gabon-blue': '#3A75C4',
        'gabon-flag-green': '#009E60',
        'gabon-flag-yellow': '#FCD116',
        'gabon-flag-blue': '#3A75C4',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
TAILWIND

# Créer le dossier static/css s'il n'existe pas
mkdir -p static/css

# Créer le fichier CSS d'entrée
echo "🎨 Création du fichier CSS d'entrée..."
cat > static/css/input.css << 'CSS'
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  
  html {
    @apply scroll-smooth;
  }
  
  body {
    @apply bg-gray-50 text-gray-900 antialiased font-sans;
  }
}

@layer components {
  .btn-primary {
    @apply inline-flex items-center px-4 py-2 bg-gabon-flag-green hover:bg-gabon-flag-green/90 text-white font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gabon-flag-green;
  }
  
  .btn-secondary {
    @apply inline-flex items-center px-4 py-2 border border-gray-300 bg-white hover:bg-gray-50 text-gray-700 font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gabon-flag-green;
  }
  
  .card {
    @apply bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden;
  }
  
  .form-input {
    @apply block w-full rounded-lg border-gray-300 shadow-sm focus:border-gabon-flag-green focus:ring focus:ring-gabon-flag-green focus:ring-opacity-50;
  }
  
  .form-select {
    @apply block w-full rounded-lg border-gray-300 shadow-sm focus:border-gabon-flag-green focus:ring focus:ring-gabon-flag-green focus:ring-opacity-50;
  }
  
  .badge {
    @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
  }
  
  .badge-success {
    @apply bg-green-100 text-green-800;
  }
  
  .badge-warning {
    @apply bg-yellow-100 text-yellow-800;
  }
  
  .badge-danger {
    @apply bg-red-100 text-red-800;
  }
  
  .badge-info {
    @apply bg-blue-100 text-blue-800;
  }
}
CSS

# Ajouter des scripts dans package.json
npm pkg set scripts.build="tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify"
npm pkg set scripts.watch="tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch"

# Compiler Tailwind
echo "🔨 Compilation de Tailwind CSS..."
npm run build

echo "✅ Installation terminée!"
echo ""
echo "📝 Commandes disponibles :"
echo "   npm run build  - Compile Tailwind pour la production"
echo "   npm run watch  - Compile Tailwind en mode développement (avec watch)"
echo ""
echo "🌐 N'oubliez pas d'ajouter dans votre settings.py :"
echo "   STATICFILES_DIRS = [BASE_DIR / 'static']"
echo "   et de charger le CSS dans vos templates avec :"
echo "   <link href=\"{% static 'css/output.css' %}\" rel=\"stylesheet\">"
