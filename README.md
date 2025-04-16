# Blutsgeschwister Product Scraper

A web application that scrapes product data from Blutsgeschwister.de and exports it in XML and CSV formats.

## Features

- Scrapes product data from Blutsgeschwister.de product pages
- Extracts detailed product information including:
  - Article number
  - Product name
  - Available sizes
  - Image URLs
  - Fit description
  - Care instructions/materials/details
  - Category
- Exports data in two formats:
  - XML with structured product data and Google Shopping metafields
  - CSV formatted for Shopify import
- Modern, responsive web interface
- Built with FastAPI and Playwright

## Prerequisites

- Python 3.8+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd blutsgeschwister-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

## Running Locally

1. Start the application:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

## Deployment on Render.com

1. Create a new Web Service on Render.com

2. Configure the following:
   - Build Command: `pip install -r requirements.txt && playwright install chromium`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. Set Environment Variables:
   - `PYTHON_VERSION`: `3.9` (or your preferred version)

## Usage

1. Enter a valid Blutsgeschwister.de product URL in the input field
2. Click "Produkt analysieren" to start scraping
3. Once scraping is complete, use the download buttons to get the data in XML or CSV format

## File Formats

### XML Export
```xml
<produkt>
  <artikelnummer>...</artikelnummer>
  <groessen>M, L, XL</groessen>
  <bilder>
    <bild>https://.../1.jpg</bild>
    <bild>https://.../2.jpg</bild>
  </bilder>
  <details><![CDATA[HTML hier]]></details>
  <passform>...</passform>
  <metafields>
    <meta_google:age_group>Erwachsener</meta_google:age_group>
    <meta_google:brand>Blutsgeschwister</meta_google:brand>
    <!-- Additional metafields -->
  </metafields>
</produkt>
```

### CSV Export
Follows Shopify import format with the following columns:
```
VaterartikelNr,cHAN,fLagerbestandeigen,cbarcode,cArtNr,cName,cBeschreibung,cFirma,cHerstellerName,Attributgruppe,Attributname,Attributwert,Shopaktiv,Shop,IstVaterArtikel,kVaterartikel
```

## Error Handling

- Invalid URLs will return an error message
- Network issues during scraping are handled gracefully
- Missing data fields will be exported as empty values

## License

This project is licensed under the MIT License - see the LICENSE file for details
