# Cannabot.pro Testing Suite

A Streamlit-based project with automated UI testing using Puppeteer. This project combines a Streamlit web application with automated browser testing capabilities.

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm (Node Package Manager)
- Chrome/Chromium browser

## Installation

### Python Setup
1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Node.js Setup (for UI Testing)
1. Navigate to the puppeteer directory:
```bash
cd puppeteer
```

2. Install Node.js dependencies:
```bash
npm install
```

## Running the Application

1. Start the Streamlit app:
```bash
streamlit run app.py
```

## Running Tests

### UI Tests (Puppeteer)
Navigate to the puppeteer directory and run:
```bash
npm test
```

For specific test files:
```bash
npm test -- puppeteer/site-check.test.js
```

## Project Structure

```
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
├── presets.py                # Presets configuration
├── test_presets.json         # Test configuration presets
├── puppeteer/                # UI Testing directory
│   ├── pages/               
│   │   └── HomePage.js       # Page Object Model
│   ├── site-check.test.js    # Site testing suite
│   ├── appointment.test.js   # Appointment testing
│   └── package.json         # Node.js dependencies
└── README.md
```

## Features

- Streamlit web application
- Automated UI testing with Puppeteer
- Screenshot capture capabilities
- Custom test presets
- Configurable test environments

## Configuration

- `.env` - Environment variables
- `test_presets.json` - Test configuration presets
- `jest.config.js` - Jest testing configuration

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.