// postcss.config.js
export default {
  plugins: [
    await import('postcss-import').then((mod) => mod.default),
    await import('tailwindcss').then((mod) => mod.default),
    await import('autoprefixer').then((mod) => mod.default),
  ],
};
