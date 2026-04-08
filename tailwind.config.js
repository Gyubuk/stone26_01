/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './apps/**/templates/**/*.html',
    './templates/**/*.html',
    './apps/**/static/**/*.js',
    './static/**/*.js',
  ],
  safelist: [
    'xl:flex',
    'xl:block',
    'xl:hidden',
    'lg:flex',
    'lg:block',
    'lg:hidden',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
