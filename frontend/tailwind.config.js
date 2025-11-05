/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        terminal: {
          black: 'var(--bg)',
          white: 'var(--text)',
          gray: 'var(--border)',
          muted: 'var(--muted)',
        },
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', '"Fira Code"', '"SF Mono"', 'Consolas', '"Courier New"', 'monospace'],
      },
      animation: {
        'blink': 'blink 1s infinite',
        'typing': 'typing 2s steps(40, end)',
        'fade-in': 'fadeIn 0.2s ease-in',
        'slide-in': 'slideIn 0.3s ease-out',
      },
    },
  },
  plugins: [],
}

