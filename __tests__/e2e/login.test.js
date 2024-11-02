const puppeteer = require('puppeteer');

describe('Login Page', () => {
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

  beforeEach(async () => {
    await page.goto('http://localhost:3000/login');
  });

  test('should display login form', async () => {
    const emailInput = await page.$('input[type="email"]');
    const passwordInput = await page.$('input[type="password"]');
    const loginButton = await page.$('button[type="submit"]');

    expect(emailInput).toBeTruthy();
    expect(passwordInput).toBeTruthy();
    expect(loginButton).toBeTruthy();
  });

  test('should show error for invalid credentials', async () => {
    await page.type('input[type="email"]', 'invalid@example.com');
    await page.type('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    const errorMessage = await page.waitForSelector('.error-message');
    const errorText = await errorMessage.evaluate(el => el.textContent);
    expect(errorText).toContain('Invalid credentials');
  });
});
