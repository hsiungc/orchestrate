module.exports = {
    mode: "jit",
    content: [
      // Example content paths...
      './public/**/*.html',
      './src/**/*.{js,jsx,ts,tsx,vue}',
    ],
    darkMode: "media", // false, class, or media 
    theme: {
      extend: {
        colors: {
          primary: {
            lighter: 'hsl(207, 73%, 52%)',
            default: 'hsl(207, 73%, 57%)',
            darker: 'hsl(207, 73%, 44%)'
          }
        }
      },
    },
    variants: {
      extend: {},
    },
    plugins: [],
  }
  