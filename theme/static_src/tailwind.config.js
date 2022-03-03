module.exports = {
  variants: {
    extend: {
      backgroundColor: ['active'],
      margin: ['first']
    }
  },
  purge: [
    '../templates/**/*.html',
    '../../**/templates/**/*.html'
  ]
}