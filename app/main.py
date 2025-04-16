from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, Response
from pathlib import Path
import logging
from typing import Dict
import json
import asyncio

from .scraper import ProductScraper
from .exporters import XMLExporter, CSVExporter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Blutsgeschwister Product Scraper")

# Mount templates and static directories
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Store scraped data temporarily (in a production environment, use a proper database)
SCRAPED_DATA: Dict = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page with the input form."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/scrape")
async def scrape_product(request: Request):
    """Handle product URL submission and trigger scraping."""
    try:
        form = await request.form()
        product_url = form.get("product_url")
        
        if not product_url or not product_url.startswith("https://www.blutsgeschwister.de/de"):
            raise HTTPException(
                status_code=400, 
                detail="Invalid Blutsgeschwister product URL. URL must start with 'https://www.blutsgeschwister.de/de'"
            )
        
        # Set a longer timeout for scraping
        try:
            async with asyncio.timeout(120):  # 120 seconds timeout
                async with ProductScraper() as scraper:
                    product_data = await scraper.scrape_product(product_url)
        except asyncio.TimeoutError:
            logger.error("Scraping timeout")
            raise HTTPException(
                status_code=504,
                detail="Scraping timeout. The server took too long to respond. Please try again."
            )
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error during scraping: {str(e)}"
            )
            
        # Store the scraped data
        SCRAPED_DATA.clear()  # Clear previous data
        SCRAPED_DATA.update(product_data)
        
        # Return a summary of the scraped data
        return {
            "status": "success",
            "message": "Daten erfolgreich extrahiert",
            "data": {
                "name": product_data.get("name", ""),
                "artikelnummer": product_data.get("artikelnummer", ""),
                "groessen": product_data.get("groessen", []),
                "bilder_count": len(product_data.get("bilder", [])),
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ein unerwarteter Fehler ist aufgetreten: {str(e)}"
        )

@app.get("/download/{format}")
async def download_file(format: str):
    """Handle file downloads for XML and CSV formats."""
    if not SCRAPED_DATA:
        raise HTTPException(
            status_code=404, 
            detail="No scraped data available. Please scrape a product first."
        )
    
    try:
        filename = f"product_{SCRAPED_DATA.get('artikelnummer', 'export')}"
        
        if format == "xml":
            content = XMLExporter.generate_xml(SCRAPED_DATA)
            media_type = "application/xml"
            filename = f"{filename}.xml"
        elif format == "csv":
            content = CSVExporter.generate_csv(SCRAPED_DATA)
            media_type = "text/csv"
            filename = f"{filename}.csv"
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid format specified. Use 'xml' or 'csv'."
            )
        
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': f'{media_type}; charset=utf-8'
        }
        
        return Response(
            content=content,
            media_type=media_type,
            headers=headers
        )
            
    except Exception as e:
        logger.error(f"Error generating {format} file: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating {format} file: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
