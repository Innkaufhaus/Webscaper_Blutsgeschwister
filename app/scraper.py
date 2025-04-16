from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from typing import Dict, List, Optional
import re
import logging
import json
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductScraper:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None

    async def __aenter__(self):
        try:
            logger.info("Starting Playwright and launching browser...")
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=True,  # Run in headless mode
                args=[
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                    '--disable-setuid-sandbox',
                    '--no-sandbox',
                    '--no-zygote',
                ],
                timeout=120000,  # 120 second timeout for browser launch
            )
            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            self.page = await self.context.new_page()
            await self.page.set_default_timeout(60000)  # 60 second timeout for all page operations
            logger.info("Browser and page setup complete")
            return self
        except Exception as e:
            logger.error(f"Error during browser setup: {str(e)}")
            if self.browser:
                await self.browser.close()
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.browser:
                await self.browser.close()
                logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")

    async def scrape_product(self, url: str) -> Dict:
        """
        Scrape product data from a Blutsgeschwister product page
        """
        try:
            logger.info(f"Starting to scrape URL: {url}")
            
            # Navigate to the page with a timeout
            try:
                logger.info("Navigating to product page...")
                await self.page.goto(url, wait_until="networkidle", timeout=60000)  # 60 second timeout
                logger.info("Page loaded successfully")
            except PlaywrightTimeout:
                logger.error("Timeout while loading the page")
                raise Exception("Die Seite konnte nicht geladen werden. Bitte versuchen Sie es später erneut.")
            except Exception as e:
                logger.error(f"Error during page navigation: {str(e)}")
                raise

            # Wait for critical elements
            try:
                logger.info("Waiting for product data to load...")
                await self.page.wait_for_selector('[data-product-id]', timeout=30000)  # 30 second timeout
                logger.info("Product data found on page")
            except PlaywrightTimeout:
                logger.error("Product data not found on page")
                raise Exception("Keine Produktdaten auf der Seite gefunden.")
            except Exception as e:
                logger.error(f"Error waiting for product data: {str(e)}")
                raise

            # Extract all required product data
            product_data = {
                "artikelnummer": await self._get_article_number(),
                "name": await self._get_product_name(),
                "groessen": await self._get_sizes(),
                "bilder": await self._get_images(),
                "passform": await self._get_fit_description(),
                "details": await self._get_details(),
                "kategorie": await self._get_category(),
                "metafields": await self._get_metafields()
            }

            # Log extracted data summary
            logger.info(f"Extracted data summary: Article #{product_data['artikelnummer']}, "
                       f"Name: {product_data['name']}, "
                       f"Sizes count: {len(product_data['groessen'])}, "
                       f"Images count: {len(product_data['bilder'])}")

            # Validate the extracted data
            if not product_data["artikelnummer"]:
                raise Exception("Artikelnummer konnte nicht gefunden werden.")
            
            if not product_data["name"]:
                raise Exception("Produktname konnte nicht gefunden werden.")

            logger.info("Successfully scraped product data")
            return product_data

        except Exception as e:
            logger.error(f"Error scraping product: {str(e)}")
            raise

    async def _get_article_number(self) -> str:
        """Extract article number"""
        try:
            article_number = await self.page.evaluate("""
                () => {
                    const element = document.querySelector('[data-product-id]');
                    return element ? element.getAttribute('data-product-id') : '';
                }
            """)
            logger.info(f"Found article number: {article_number}")
            return article_number or ""
        except Exception as e:
            logger.error(f"Error extracting article number: {str(e)}")
            return ""

    async def _get_product_name(self) -> str:
        """Extract product name"""
        try:
            name = await self.page.evaluate("""
                () => {
                    const element = document.querySelector('h1.product-title');
                    return element ? element.textContent.trim() : '';
                }
            """)
            logger.info(f"Found product name: {name}")
            return name or ""
        except Exception as e:
            logger.error(f"Error extracting product name: {str(e)}")
            return ""

    async def _get_sizes(self) -> List[str]:
        """Extract available sizes"""
        try:
            sizes = await self.page.evaluate("""
                () => {
                    const sizeElements = document.querySelectorAll('.size-selector option:not([disabled])');
                    return Array.from(sizeElements)
                        .map(el => el.textContent.trim())
                        .filter(size => size && size !== 'Größe wählen');
                }
            """)
            logger.info(f"Found sizes: {sizes}")
            return sizes or []
        except Exception as e:
            logger.error(f"Error extracting sizes: {str(e)}")
            return []

    async def _get_images(self) -> List[str]:
        """Extract product images"""
        try:
            images = await self.page.evaluate("""
                () => {
                    const images = document.querySelectorAll('.product-gallery img[src]');
                    return Array.from(images)
                        .map(img => img.src)
                        .filter(src => src && src.startsWith('http'));
                }
            """)
            logger.info(f"Found {len(images)} images")
            return images or []
        except Exception as e:
            logger.error(f"Error extracting images: {str(e)}")
            return []

    async def _get_fit_description(self) -> str:
        """Extract fit description"""
        try:
            fit = await self.page.evaluate("""
                () => {
                    const element = document.querySelector('.product-fit-description, .product-description');
                    return element ? element.textContent.trim() : '';
                }
            """)
            logger.info(f"Found fit description: {bool(fit)}")
            return fit or ""
        except Exception as e:
            logger.error(f"Error extracting fit description: {str(e)}")
            return ""

    async def _get_details(self) -> str:
        """Extract product details including care instructions and materials"""
        try:
            details = await self.page.evaluate("""
                () => {
                    const detailsSection = document.querySelector('.product-details, .product-information');
                    return detailsSection ? detailsSection.innerHTML.trim() : '';
                }
            """)
            logger.info(f"Found details: {bool(details)}")
            return self._clean_html(details) if details else ""
        except Exception as e:
            logger.error(f"Error extracting details: {str(e)}")
            return ""

    async def _get_category(self) -> str:
        """Extract product category"""
        try:
            category = await self.page.evaluate("""
                () => {
                    const breadcrumbs = document.querySelector('.breadcrumb');
                    if (!breadcrumbs) return '';
                    const links = Array.from(breadcrumbs.querySelectorAll('a'));
                    return links
                        .map(a => a.textContent.trim())
                        .filter(text => text && text !== 'Home')
                        .join(' > ');
                }
            """)
            logger.info(f"Found category: {category}")
            return category or ""
        except Exception as e:
            logger.error(f"Error extracting category: {str(e)}")
            return ""

    async def _get_metafields(self) -> Dict:
        """Get metafields with dynamic category mapping"""
        try:
            category = await self._get_category()
            sizes = await self._get_sizes()
            
            metafields = {
                "meta_google:age_group": "Erwachsener",
                "meta_google:brand": "Blutsgeschwister",
                "meta_google:condition": "New",
                "meta_google:gender": "Female",
                "meta_google:google_product_category": self._map_category_to_google(category),
                "meta_google:size": ", ".join(sizes) if sizes else "",
                "meta_google:google_product_type": category.split(" > ")[-1] if category else "",
                "meta_google:tags": ""
            }
            logger.info("Generated metafields")
            return metafields
        except Exception as e:
            logger.error(f"Error generating metafields: {str(e)}")
            return {}

    def _map_category_to_google(self, category: str) -> str:
        """Map Blutsgeschwister category to Google category"""
        category_lower = category.lower()
        
        if "kleider" in category_lower:
            return "Apparel & Accessories > Clothing > Dresses"
        elif "hosen" in category_lower:
            return "Apparel & Accessories > Clothing > Pants"
        elif "jacken" in category_lower:
            return "Apparel & Accessories > Clothing > Jackets"
        else:
            return "Apparel & Accessories > Clothing"

    def _clean_html(self, html: str) -> str:
        """Clean HTML content"""
        if not html:
            return ""
        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        # Remove HTML comments
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        # Remove extra whitespace
        html = re.sub(r'\s+', ' ', html).strip()
        return html
