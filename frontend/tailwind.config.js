/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./src/**/*.{html,js,jsx,ts,tsx}"],
  theme: {
    extend: {
      backgroundColor: {
        primary: '#f7f7f7',
        dark: '#1f2937', // Changed dark background color to a dark gray
      },
      textColor: {
        primary: '#333', // Added primary text color
        secondary: '#666', // Added secondary text color
      },
    },
  },
  plugins: [],
}
