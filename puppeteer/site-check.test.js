const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const HomePage = require('./pages/HomePage');

describe('Cannabot.pro website', () => {
  let browser;
  let page;
  let homePage;

  beforeAll(async () => {
    browser = await puppeteer.launch({ 
      headless: false,
      defaultViewport: null
    });
    
    page = await browser.newPage();
    await page.setDefaultNavigationTimeout(30000);
    
    homePage = new HomePage(page);
  });

  beforeEach(async () => {
    await fs.mkdir('./report/screenshots', { recursive: true });
  });

  afterAll(async () => {
    if (browser) {
      await browser.close();
    }
  });

  it('should take a screenshot of the homepage', async () => {
    console.log('Running tests...');
    
    await homePage.setViewport();
    await homePage.navigate();
    await homePage.takeScreenshot('./report/screenshots/cannabot-homepage.png');

    console.log('Screenshot taken successfully! ✨');
  });
});
