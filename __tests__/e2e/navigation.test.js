const puppeteer = require('puppeteer');

describe('Navigation', () => {
  let browser;
  let page;

  beforeAll(async () => {
    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox']
    });
    page = await browser.newPage();
  });

  afterAll(async () => {
    await browser.close();
  });

  test('should navigate through main sections', async () => {
    await page.goto('http://localhost:3000');
    
    // Click on About link
    await page.click('a[href="/about"]');
    await page.waitForSelector('h1');
    let heading = await page.$eval('h1', el => el.textContent);
    expect(heading).toContain('About');

    // Click on Contact link
    await page.click('a[href="/contact"]');
    await page.waitForSelector('h1');
    heading = await page.$eval('h1', el => el.textContent);
    expect(heading).toContain('Contact');
  });

  test('should show 404 page for invalid routes', async () => {
    await page.goto('http://localhost:3000/invalid-route');
    const errorHeading = await page.$eval('h1', el => el.textContent);
    expect(errorHeading).toContain('404');
  });
});
