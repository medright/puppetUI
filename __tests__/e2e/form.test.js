const puppeteer = require('puppeteer');

describe('Contact Form', () => {
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
    await page.goto('http://localhost:3000/contact');
  });

  test('should submit contact form successfully', async () => {
    await page.type('input[name="name"]', 'John Doe');
    await page.type('input[name="email"]', 'john@example.com');
    await page.type('textarea[name="message"]', 'Hello, this is a test message');
    
    await Promise.all([
      page.click('button[type="submit"]'),
      page.waitForNavigation()
    ]);

    const successMessage = await page.$eval('.success-message', el => el.textContent);
    expect(successMessage).toContain('Message sent successfully');
  });

  test('should validate required fields', async () => {
    await page.click('button[type="submit"]');
    
    const errorMessages = await page.$$eval('.error-message', 
      elements => elements.map(el => el.textContent)
    );
    
    expect(errorMessages).toContain('Name is required');
    expect(errorMessages).toContain('Email is required');
    expect(errorMessages).toContain('Message is required');
  });
});
