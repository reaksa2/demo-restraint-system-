/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#14181A',        // near-black, admin chrome
        slate: '#5B6764',      // secondary text
        paper: '#F7F3EC',      // warm off-white, menu display background
        sand: '#E8DFCE',       // borders/cards on paper
        marigold: {
          DEFAULT: '#C8811A',  // primary accent — turmeric, not clay/terracotta
          dark: '#9C6414',
          light: '#F0DDB8',
        },
        moss: {
          DEFAULT: '#435E4A',  // secondary accent — herb green
          light: '#DCE5DE',
        },
        clay: '#B3462C',        // danger / unavailable, used sparingly
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        khmer: ['"Noto Sans Khmer"', 'sans-serif'],
        display: ['Fraunces', 'serif'],
        'khmer-display': ['"Noto Serif Khmer"', 'serif'],
      },
    },
  },
  plugins: [],
}
