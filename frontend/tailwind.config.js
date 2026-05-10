/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#0b3954',
          600: '#0a3349',
          700: '#072636',
        },
        severity: {
          clean: '#22c55e',
          watch: '#facc15',
          suspicious: '#f97316',
          confirmed: '#ef4444',
          critical: '#b91c1c',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
