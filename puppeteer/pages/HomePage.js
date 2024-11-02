class HomePage {
  constructor(page) {
    this.page = page;
    this.url = 'https://cannabot.pro';
  }

  async navigate() {
    await this.page.goto(this.url, {
      waitUntil: 'networkidle0'
    });
  }

  async takeScreenshot(path) {
    await this.page.screenshot({
      path: path,
      fullPage: true
    });
  }

  async setViewport(width = 1920, height = 1080) {
    await this.page.setViewport({ width, height });
  }
}

module.exports = HomePage; 