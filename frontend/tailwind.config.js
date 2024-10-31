/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./src/**/*.{html,js,jsx,ts,tsx}"],
  theme: {
    extend: {
      backgroundColor: {
        primary: '#f7f7f7',
        dark: '#000000',
      },
    },
  },
  plugins: [],
}
