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
