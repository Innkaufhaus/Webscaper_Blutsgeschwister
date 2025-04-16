# Blutsgeschwister Product Scraper

A web application that scrapes product data from Blutsgeschwister's online store and exports it in XML or CSV format.

## Features

- Scrape product data from Blutsgeschwister product pages
- Export data in XML format with Google Shopping attributes
- Export data in CSV format
- Modern, responsive web interface using Tailwind CSS
- Error handling and validation
- Detailed logging

## Setup for Local Development

1. Clone the repository:
```bash
git clone https://github.com/Innkaufhaus/Webscaper_Blutsgeschwister.git
cd Webscaper_Blutsgeschwister
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browser:
```bash
playwright install chromium
```

## Running the Application

1. Start the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. Open your browser and navigate to `http://localhost:8000`

3. Enter a Blutsgeschwister product URL and click "Produkt analysieren"

4. Once the data is scraped, you can download it in XML or CSV format

## Project Structure

- `app/main.py` - FastAPI application and route handlers
- `app/scraper.py` - Product scraping logic using Playwright
- `app/exporters/` - XML and CSV export functionality
- `app/templates/` - HTML templates
- `app/static/` - Static files (CSS, images)

## Requirements

- Python 3.11+
- FastAPI
- Playwright
- See requirements.txt for full list

## Deployment

The application is configured for deployment on Render.com using:
- `render.yaml` - Render configuration
- `start.sh` - Start script for the web service

## Development

To make changes:

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit:
```bash
git add .
git commit -m "Description of your changes"
```

3. Push to GitHub:
```bash
git push origin feature/your-feature-name
```

## License

MIT License
