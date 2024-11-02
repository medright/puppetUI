const puppeteer = require('puppeteer');

describe('API Integration', () => {
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

  test('should load and display user data', async () => {
    await page.goto('http://localhost:3000/users');
    
    // Wait for API data to load
    await page.waitForSelector('.user-list');
    
    const userElements = await page.$$('.user-card');
    expect(userElements.length).toBeGreaterThan(0);
    
    const firstUserName = await userElements[0].$eval('.user-name', el => el.textContent);
    expect(firstUserName).toBeTruthy();
  });

  test('should handle API errors gracefully', async () => {
    // Mock failed API response
    await page.setRequestInterception(true);
    page.on('request', request => {
      if (request.url().includes('/api/users')) {
        request.abort();
      } else {
        request.continue();
      }
    });

    await page.goto('http://localhost:3000/users');
    
    const errorMessage = await page.waitForSelector('.error-message');
    const errorText = await errorMessage.evaluate(el => el.textContent);
    expect(errorText).toContain('Failed to load users');
  });
});
