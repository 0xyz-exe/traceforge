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
        background: '#0a0a0a',
        foreground: '#fafafa',
        card: '#1a1a1a',
        border: '#2a2a2a',
        accent: '#3b82f6',
        success: '#22c55e',
        warning: '#eab308',
        error: '#ef4444',
        muted: '#737373',
      },
    },
  },
  plugins: [],
}
