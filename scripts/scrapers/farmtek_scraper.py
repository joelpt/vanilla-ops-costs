#!/usr/bin/env python3
"""
Terra35 Vanilla Operations Cost Analysis - FarmTek Scraper

FarmTek is a major supplier of greenhouse equipment and supplies.
This scraper focuses on greenhouse structures, benching systems, 
climate control, and growing supplies relevant to vanilla cultivation.

Website: https://www.farmtek.com/
Key Categories: Greenhouse Kits, Benching, HVAC, Irrigation
"""

import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Any
import time

from .base_scraper import BaseScraper, ScrapedProduct

class FarmTekScraper(BaseScraper):
    """
    Scraper for FarmTek greenhouse and horticultural equipment
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            supplier_name="FarmTek",
            base_url="https://www.farmtek.com",
            rate_limit_delay=2.0,  # Be respectful with 2 second delays
            **kwargs
        )
        
        # Category mappings from FarmTek to our taxonomy
        self.category_mapping = {
            'greenhouse-kits': 'infrastructure/structures',
            'greenhouse-benching': 'infrastructure/benching', 
            'greenhouse-ventilation': 'infrastructure/climate_control',
            'greenhouse-heating': 'infrastructure/climate_control',
            'irrigation-systems': 'infrastructure/irrigation',
            'growing-supplies': 'operational_costs/growing_supplies'
        }
        
        # Product URLs to scrape - focusing on vanilla-relevant equipment
        self.target_urls = [
            '/greenhouse-kits/',
            '/greenhouse-benching/',
            '/greenhouse-ventilation/', 
            '/greenhouse-heating/',
            '/irrigation-systems/',
            '/growing-supplies/'
        ]
    
    def scrape_products(self, max_products_per_category: int = 50) -> List[ScrapedProduct]:
        """
        Scrape FarmTek products relevant to vanilla cultivation
        """
        all_products = []
        
        for url_path in self.target_urls:
            self.logger.info(f"Scraping category: {url_path}")
            
            try:
                products = self.scrape_category(url_path, max_products_per_category)
                all_products.extend(products)
                
                self.logger.info(f"Found {len(products)} products in {url_path}")
                
            except Exception as e:
                self.logger.error(f"Failed to scrape category {url_path}: {e}")
                if self.current_session:
                    self.current_session.errors.append(f"Category {url_path}: {e}")
                continue
        
        self.logger.info(f"Total products scraped: {len(all_products)}")
        return all_products
    
    def scrape_category(self, url_path: str, max_products: int = 50) -> List[ScrapedProduct]:
        """
        Scrape a specific product category
        """
        category_url = urljoin(self.base_url, url_path)
        response = self.make_request(category_url)
        
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        products = []
        
        # Find product listings (this is a mock implementation - would need real HTML analysis)
        product_links = soup.find_all('a', href=re.compile(r'/product/'))
        
        for i, link in enumerate(product_links[:max_products]):
            if not link.get('href'):
                continue
                
            product_url = urljoin(self.base_url, link.get('href'))
            
            try:
                product = self.scrape_product_detail(product_url, url_path)
                if product:
                    products.append(product)
                    
            except Exception as e:
                self.logger.warning(f"Failed to scrape product {product_url}: {e}")
                continue
        
        return products
    
    def scrape_product_detail(self, product_url: str, category_path: str) -> Optional[ScrapedProduct]:
        """
        Scrape individual product details
        """
        response = self.make_request(product_url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract product information (mock implementation - would need real selectors)
        try:
            # Product name
            title_elem = soup.find('h1') or soup.find('title')
            product_name = title_elem.get_text(strip=True) if title_elem else "Unknown Product"
            
            # Product code/SKU
            sku_elem = soup.find(attrs={'data-sku': True}) or soup.find(text=re.compile(r'SKU|Model'))
            product_code = None
            if sku_elem:
                if hasattr(sku_elem, 'get'):
                    product_code = sku_elem.get('data-sku')
                else:
                    # Extract from text
                    sku_match = re.search(r'(?:SKU|Model)[:\s]+([A-Z0-9-]+)', str(sku_elem))
                    product_code = sku_match.group(1) if sku_match else None
            
            # Price extraction
            price_elem = soup.find(attrs={'class': re.compile(r'price|cost')})
            unit_cost = None
            unit = 'each'
            
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                unit_cost = self.parse_price(price_text)
                
                # Try to determine unit
                if 'per sq ft' in price_text.lower() or '/sq ft' in price_text.lower():
                    unit = 'per_sq_ft'
                elif 'per foot' in price_text.lower() or '/ft' in price_text.lower():
                    unit = 'per_foot'
                elif 'per pound' in price_text.lower() or '/lb' in price_text.lower():
                    unit = 'per_pound'
            
            # Specifications
            specs = {}
            
            # Look for specification tables or lists
            spec_section = soup.find(attrs={'class': re.compile(r'spec|detail|feature')})
            if spec_section:
                # Extract key-value pairs
                spec_items = spec_section.find_all(['li', 'tr', 'div'])
                for item in spec_items:
                    text = item.get_text(strip=True)
                    if ':' in text:
                        key, value = text.split(':', 1)
                        specs[key.strip()] = value.strip()
            
            # Dimensions
            dimensions = self.extract_dimensions(soup.get_text())
            if dimensions:
                specs.update(dimensions)
            
            # Generate item ID
            item_id = self.generate_item_id(product_name, product_code)
            
            # Map to our category taxonomy
            category = self.category_mapping.get(
                category_path.strip('/'), 
                'infrastructure/structures'
            )
            
            # Determine confidence level based on data completeness
            confidence = 'HIGH' if unit_cost and product_code else 'MEDIUM'
            
            return ScrapedProduct(
                item_id=item_id,
                item_name=product_name,
                category=category.split('/')[0],
                subcategory=category.split('/')[1] if '/' in category else None,
                specifications=specs if specs else None,
                unit_cost=unit_cost,
                unit=unit,
                source_url=product_url,
                product_code=product_code,
                confidence_level=confidence,
                notes=f"Scraped from FarmTek category: {category_path}"
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing product details from {product_url}: {e}")
            return None
    
    def extract_dimensions(self, text: str) -> Dict[str, str]:
        """Extract dimensional specifications from text"""
        dimensions = {}
        
        # Common dimension patterns
        patterns = {
            'length': re.compile(r'(\d+(?:\.\d+)?)\s*(?:feet|ft|\')\s*(?:long|length)', re.IGNORECASE),
            'width': re.compile(r'(\d+(?:\.\d+)?)\s*(?:feet|ft|\')\s*(?:wide|width)', re.IGNORECASE),
            'height': re.compile(r'(\d+(?:\.\d+)?)\s*(?:feet|ft|\')\s*(?:high|height|tall)', re.IGNORECASE),
            'area': re.compile(r'(\d+(?:,\d+)?)\s*(?:sq\.?\s*ft|square\s+feet)', re.IGNORECASE)
        }
        
        for dim_name, pattern in patterns.items():
            match = pattern.search(text)
            if match:
                dimensions[dim_name] = match.group(1).replace(',', '')
        
        return dimensions
    
    def generate_item_id(self, product_name: str, product_code: Optional[str] = None) -> str:
        """Generate unique item ID"""
        if product_code:
            return f"FARMTEK_{product_code}"
        else:
            # Generate from name
            clean_name = re.sub(r'[^a-zA-Z0-9]', '_', product_name.upper())
            clean_name = re.sub(r'_+', '_', clean_name)[:20]  # Limit length
            return f"FARMTEK_{clean_name}"

# Example usage and testing
if __name__ == '__main__':
    import logging
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create scraper
    scraper = FarmTekScraper()
    
    print(f"Testing {scraper.supplier_name} scraper...")
    
    # Run a small test session
    try:
        results = scraper.run_scraping_session(max_products_per_category=5)
        
        print(f"\nSession Results:")
        print(f"- Products scraped: {len(results.products_scraped)}")
        print(f"- Requests made: {results.requests_made}")
        print(f"- Cache hits: {results.cache_hits}")
        print(f"- Errors: {len(results.errors)}")
        print(f"- Warnings: {len(results.warnings)}")
        
        # Show sample products
        if results.products_scraped:
            print(f"\nSample products:")
            for product in results.products_scraped[:3]:
                print(f"- {product.item_name} (${product.unit_cost}/{product.unit})")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()