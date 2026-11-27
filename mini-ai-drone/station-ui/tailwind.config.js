/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dji: {
          dark: '#07090e',
          card: '#0c1017',
          border: 'rgba(255, 255, 255, 0.08)',
          cyan: '#00f2fe',
          emerald: '#00f5a0',
          amber: '#ffb300',
          red: '#ff3366',
          purple: '#9d4edd',
        }
      },
      fontFamily: {
        mono: ['SF Mono', 'Menlo', 'Monaco', 'Cascadia Code', 'Consolas', 'Courier New', 'monospace'],
        sans: ['Geist', 'Plus Jakarta Sans', 'system-ui', 'sans-serif'],
      },
      animation: {
        'radar-pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shutter-flash': 'flash 0.3s ease-out forwards',
        'spin-slow': 'spin 8s linear infinite',
      },
      keyframes: {
        flash: {
          '0%': { opacity: '0.8' },
          '100%': { opacity: '0' },
        }
      }
    },
  },
  plugins: [],
}
