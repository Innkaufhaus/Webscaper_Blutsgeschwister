# Blutsgeschwister Product Scraper

A web application that scrapes product data from Blutsgeschwister's online store and exports it in XML or CSV format.

## Features

- Scrape product data from Blutsgeschwister product pages
- Export data in XML format with Google Shopping attributes
- Export data in CSV format
- Modern, responsive web interface using Tailwind CSS
- Error handling and validation
- Detailed logging

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/blutsgeschwister-scraper.git
cd blutsgeschwister-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browser:
```bash
playwright install chromium
```

## Usage

1. Start the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. Open your browser and navigate to `http://localhost:8000`

3. Enter a Blutsgeschwister product URL and click "Produkt analysieren"

4. Once the data is scraped, you can download it in XML or CSV format

## Requirements

- Python 3.7+
- FastAPI
- Playwright
- See requirements.txt for full list

## License

MIT License
