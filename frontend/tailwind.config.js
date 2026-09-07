/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // SkillBridge brand palette — a "ledger meets classroom" identity:
        // deep indigo ink (credits/trust) + warm amber (the exchange spark)
        ink: {
          50: '#f4f5fb',
          100: '#e6e8f5',
          200: '#c3c8e8',
          300: '#9aa3d8',
          400: '#6b76c2',
          500: '#4a54a8',
          600: '#383f8a',
          700: '#2d3270',
          800: '#22254f',
          900: '#171933',
          950: '#0e0f20',
        },
        ember: {
          50: '#fff8ed',
          100: '#ffedd0',
          200: '#ffd799',
          300: '#ffba5c',
          400: '#ff9a2e',
          500: '#f77f0f',
          600: '#db600a',
          700: '#b6460c',
          800: '#933811',
          900: '#792f12',
        },
        surface: {
          light: '#faf9f6',
          dark: '#12132a',
        },
      },
      fontFamily: {
        display: ['"Fraunces"', 'ui-serif', 'Georgia', 'serif'],
        sans: ['"Inter"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      borderRadius: {
        sm: '6px',
        md: '10px',
        lg: '16px',
        xl: '22px',
      },
      boxShadow: {
        card: '0 1px 2px rgba(23, 25, 51, 0.06), 0 4px 16px rgba(23, 25, 51, 0.06)',
        raised: '0 8px 30px rgba(23, 25, 51, 0.12)',
      },
    },
  },
  plugins: [],
};
