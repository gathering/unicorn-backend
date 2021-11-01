const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
    purge: [
        "../../templates/*.html",
        "../../templates/**/*.html"
    ],
    theme: {
      screens: {
        mobile: { max: '768px' },
        laptop: '1200px',
        desktop: '1600px',
        ...defaultTheme.screens
      },
      extend: {
        colors: {
          'logo-primary': '#f4772b',
          'logo-secondary': '#2ac4f4',
        },
        fontFamily: {
          sans: ['Inter', ...defaultTheme.fontFamily.sans],
        },
      },
    },
    variants: {
      textColor: ['responsive', 'hover', 'focus', 'group-hover'],
      backgroundColor: ['responsive', 'hover', 'focus'],
    },
    plugins: [require('@tailwindcss/ui')],
};
