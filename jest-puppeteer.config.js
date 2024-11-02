module.exports = {
  launch: {
    headless: 'new',
    args: ['--no-sandbox']
  },
  server: {
    command: 'npm start',
    port: 3000,
    launchTimeout: 10000,
    debug: true,
  },
}
