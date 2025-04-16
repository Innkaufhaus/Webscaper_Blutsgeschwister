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
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch()
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        self.page = await self.context.new_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.browser.close()

    async def scrape_product(self, url: str) -> Dict:
        """
        Scrape product data from a Blutsgeschwister product page
        """
        try:
            logger.info(f"Starting to scrape URL: {url}")
            
            # Navigate to the page and wait for network idle
            await self.page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait for page to be fully loaded
            await asyncio.sleep(2)  # Give JavaScript some time to execute
            
            # Check if we're on a product page by looking for common product page elements
            is_product_page = await self.page.evaluate("""
                () => {
                    const selectors = [
                        '.product-detail',
                        '.product-information',
                        '.product-gallery',
                        'h1.product-title',
                        '[data-product-id]'
                    ];
                    return selectors.some(selector => document.querySelector(selector));
                }
            """)
            
            if not is_product_page:
                logger.error("Not a valid product page")
                raise Exception("Die URL scheint keine gültige Produktseite zu sein.")

            # Extract all required product data
            product_data = {
                "artikelnummer": await self._get_article_number(),
                "name": await self._get_product_name(),
                "groessen": await self._get_sizes(),
                "bilder": await self._get_images(),
                "passform": await self._get_fit_description(),
                "details": await self._get_details(),
                "kategorie": await self._get_category(),
                "metafields": {}  # Will be populated after basic data is collected
            }

            # Log the extracted data for debugging
            logger.info("Extracted product data:")
            for key, value in product_data.items():
                if key != "details":  # Skip logging HTML details
                    logger.info(f"{key}: {value}")

            # Generate metafields after we have the basic data
            product_data["metafields"] = await self._get_metafields(product_data)

            # Validate the extracted data
            if not product_data["artikelnummer"] and not product_data["name"]:
                raise Exception("Keine Produktdaten gefunden.")

            logger.info("Successfully scraped product data")
            return product_data

        except PlaywrightTimeout:
            logger.error("Timeout while loading the page")
            raise Exception("Die Seite konnte nicht geladen werden. Bitte versuchen Sie es später erneut.")
        except Exception as e:
            logger.error(f"Error scraping product: {str(e)}")
            raise

    async def _get_article_number(self) -> str:
        """Extract article number"""
        try:
            article_number = await self.page.evaluate("""
                () => {
                    // Try multiple selectors
                    const selectors = [
                        '[data-product-id]',
                        '[data-article-number]',
                        '.product-number',
                        '.sku',
                        '[itemprop="sku"]'
                    ];
                    
                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element) {
                            const value = element.getAttribute('data-product-id') || 
                                        element.getAttribute('data-article-number') || 
                                        element.textContent.trim();
                            if (value) return value;
                        }
                    }
                    return '';
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
                    const selectors = [
                        'h1.product-title',
                        'h1.product-name',
                        '.product-detail h1',
                        '[itemprop="name"]',
                        '.product-name'
                    ];
                    
                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element) {
                            return element.textContent.trim();
                        }
                    }
                    return '';
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
                    const selectors = [
                        '.size-selector option:not([disabled])',
                        '.size-options .available',
                        '[data-size]',
                        '.variant-size',
                        '.size-variant'
                    ];
                    
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length) {
                            return Array.from(elements)
                                .map(el => el.textContent.trim())
                                .filter(size => size && !['Größe wählen', 'Select size'].includes(size));
                        }
                    }
                    return [];
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
                    const selectors = [
                        '.product-gallery img[src]',
                        '.product-images img[src]',
                        '.gallery-image[src]',
                        '[data-image-role="product"] img[src]',
                        '.product-detail img[src]'
                    ];
                    
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length) {
                            return Array.from(elements)
                                .map(img => img.src)
                                .filter(src => src && src.startsWith('http'));
                        }
                    }
                    return [];
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
                    const selectors = [
                        '.product-fit-description',
                        '.product-description',
                        '.description',
                        '[data-description]',
                        '.fit-info'
                    ];
                    
                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element) {
                            return element.textContent.trim();
                        }
                    }
                    return '';
                }
            """)
            logger.info(f"Found fit description: {bool(fit)}")
            return fit or ""
        except Exception as e:
            logger.error(f"Error extracting fit description: {str(e)}")
            return ""

    async def _get_details(self) -> str:
        """Extract product details"""
        try:
            details = await self.page.evaluate("""
                () => {
                    const selectors = [
                        '.product-details',
                        '.product-information',
                        '.details',
                        '[data-details]',
                        '.product-attributes'
                    ];
                    
                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element) {
                            return element.innerHTML.trim();
                        }
                    }
                    return '';
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
                    const selectors = [
                        '.breadcrumb',
                        '.breadcrumbs',
                        '[data-breadcrumbs]',
                        '.product-category'
                    ];
                    
                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element) {
                            const links = Array.from(element.querySelectorAll('a'));
                            return links
                                .map(a => a.textContent.trim())
                                .filter(text => text && !['Home', 'Start'].includes(text))
                                .join(' > ');
                        }
                    }
                    return '';
                }
            """)
            logger.info(f"Found category: {category}")
            return category or ""
        except Exception as e:
            logger.error(f"Error extracting category: {str(e)}")
            return ""

    async def _get_metafields(self, product_data: Dict) -> Dict:
        """Get metafields with dynamic category mapping"""
        try:
            category = product_data.get("kategorie", "")
            sizes = product_data.get("groessen", [])
            
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
