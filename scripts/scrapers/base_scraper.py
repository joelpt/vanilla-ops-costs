#!/usr/bin/env python3
"""
Terra35 Vanilla Operations Cost Analysis - Base Scraper Framework

This module provides the foundational scraping infrastructure for collecting
cost data from various suppliers and sources. It includes rate limiting,
error handling, caching, and data validation capabilities.

Usage:
    from base_scraper import BaseScraper
    
    class MySupplierScraper(BaseScraper):
        def scrape_products(self):
            # Implementation here
            pass
"""

import requests
import time
import json
import hashlib
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Any, Union
import logging
from dataclasses import dataclass, asdict
import random
import sys
from abc import ABC, abstractmethod

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.constants import (
    STATUS_ACTIVE, COMPANY_TYPE_SUPPLIER, SOURCE_TIER_PRIMARY,
    MILESTONE_DATA_COLLECTION, SESSION_STATUS_IN_PROGRESS,
    REFERENCE_TYPE_PRIMARY, ACTIVITY_TYPE_CREATED, DEFAULT_UNIT
)

@dataclass
class ScrapedProduct:
    """Standard data structure for scraped product information"""
    item_id: str
    item_name: str
    category: str
    subcategory: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    unit_cost: Optional[float] = None
    unit: Optional[str] = None
    volume_discounts: Optional[List[Dict[str, Any]]] = None
    source_url: str = ""
    product_code: Optional[str] = None
    confidence_level: str = "MEDIUM"
    scraped_at: str = ""
    notes: Optional[str] = None
    
    def __post_init__(self):
        if not self.scraped_at:
            self.scraped_at = datetime.now().isoformat()

@dataclass
class ScrapingResult:
    """Container for scraping session results"""
    supplier: str
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    products_scraped: List[ScrapedProduct] = None
    errors: List[str] = None
    warnings: List[str] = None
    cache_hits: int = 0
    requests_made: int = 0
    
    def __post_init__(self):
        if self.products_scraped is None:
            self.products_scraped = []
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

class BaseScraper(ABC):
    """
    Base class for all supplier scrapers with common functionality:
    - Rate limiting and respectful scraping
    - Response caching for audit trails
    - Error handling and retry logic
    - Database integration for storing results
    - Logging and monitoring
    """
    
    def __init__(self, 
                 supplier_name: str,
                 base_url: str,
                 cache_dir: Optional[str] = None,
                 db_path: Optional[str] = None,
                 rate_limit_delay: float = 1.0,
                 max_retries: int = 3,
                 timeout: int = 30):
        
        self.supplier_name = supplier_name
        self.base_url = base_url
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Setup directories
        self.project_root = project_root
        self.cache_dir = Path(cache_dir or project_root / 'data' / 'cache' / supplier_name.lower())
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Database connection
        self.db_path = db_path or str(project_root / 'data' / 'costs' / 'vanilla_costs.db')
        
        # Session management
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Tracking
        self.last_request_time = 0
        self.request_count = 0
        self.cache_hit_count = 0
        
        # Current session tracking
        self.current_session: Optional[ScrapingResult] = None
        
        # Logging setup
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the scraper"""
        log_dir = self.project_root / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # Create supplier-specific logger
        self.logger = logging.getLogger(f'scraper.{self.supplier_name.lower()}')
        self.logger.setLevel(logging.INFO)
        
        # File handler
        log_file = log_dir / f'{self.supplier_name.lower()}_scraper.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def start_session(self) -> str:
        """Start a new scraping session"""
        session_id = f"{self.supplier_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = ScrapingResult(
            supplier=self.supplier_name,
            session_id=session_id,
            start_time=datetime.now()
        )
        
        self.logger.info(f"Started scraping session: {session_id}")
        return session_id
    
    def end_session(self) -> ScrapingResult:
        """End the current scraping session and return results"""
        if not self.current_session:
            raise ValueError("No active session to end")
        
        self.current_session.end_time = datetime.now()
        self.current_session.cache_hits = self.cache_hit_count
        self.current_session.requests_made = self.request_count
        
        duration = (self.current_session.end_time - self.current_session.start_time).total_seconds()
        
        self.logger.info(
            f"Completed session {self.current_session.session_id}: "
            f"{len(self.current_session.products_scraped)} products, "
            f"{self.request_count} requests, "
            f"{self.cache_hit_count} cache hits, "
            f"{duration:.1f}s duration"
        )
        
        session_result = self.current_session
        self.current_session = None
        
        return session_result
    
    def rate_limit(self):
        """Implement rate limiting between requests"""
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            # Add small random jitter to avoid request batching
            sleep_time += random.uniform(0, 0.1)
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_cache_key(self, url: str, params: Optional[Dict] = None) -> str:
        """Generate cache key for URL and parameters"""
        cache_data = {'url': url}
        if params:
            cache_data['params'] = sorted(params.items())
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for given key"""
        return self.cache_dir / f"{cache_key}.json"
    
    def load_from_cache(self, cache_key: str, max_age_hours: int = 24) -> Optional[Dict]:
        """Load response from cache if available and not expired"""
        cache_path = self.get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
            
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            age_hours = (datetime.now() - cached_time).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                self.logger.info(f"Cache expired for key {cache_key} (age: {age_hours:.1f}h)")
                return None
            
            self.cache_hit_count += 1
            self.logger.debug(f"Cache hit for key {cache_key}")
            return cached_data
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.logger.warning(f"Invalid cache file {cache_path}: {e}")
            return None
    
    def save_to_cache(self, cache_key: str, response_data: Dict):
        """Save response data to cache"""
        cache_path = self.get_cache_path(cache_key)
        
        cached_data = {
            'timestamp': datetime.now().isoformat(),
            'url': response_data.get('url', ''),
            'status_code': response_data.get('status_code', 0),
            'headers': dict(response_data.get('headers', {})),
            'content': response_data.get('content', ''),
            'encoding': response_data.get('encoding', 'utf-8')
        }
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(cached_data, f, indent=2)
            self.logger.debug(f"Cached response for key {cache_key}")
        except Exception as e:
            self.logger.error(f"Failed to cache response {cache_key}: {e}")
    
    def make_request(self, url: str, params: Optional[Dict] = None, 
                    cache_hours: int = 24, **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with caching and error handling"""
        
        # Check cache first
        cache_key = self.get_cache_key(url, params)
        cached_data = self.load_from_cache(cache_key, cache_hours)
        
        if cached_data:
            # Create mock response from cached data
            response = requests.Response()
            response._content = cached_data['content'].encode(cached_data.get('encoding', 'utf-8'))
            response.status_code = cached_data['status_code']
            response.headers.update(cached_data.get('headers', {}))
            response.url = cached_data['url']
            response.encoding = cached_data.get('encoding', 'utf-8')
            return response
        
        # Apply rate limiting
        self.rate_limit()
        
        # Make request with retries
        for attempt in range(self.max_retries + 1):
            try:
                self.logger.debug(f"Making request to {url} (attempt {attempt + 1})")
                
                response = self.session.get(
                    url, 
                    params=params,
                    timeout=self.timeout,
                    **kwargs
                )
                
                self.request_count += 1
                
                if response.status_code == 200:
                    # Cache successful response
                    self.save_to_cache(cache_key, {
                        'url': response.url,
                        'status_code': response.status_code,
                        'headers': response.headers,
                        'content': response.text,
                        'encoding': response.encoding
                    })
                    
                    return response
                elif response.status_code in [403, 404, 410]:
                    # Don't retry for these errors
                    self.logger.warning(f"HTTP {response.status_code} for {url}")
                    break
                else:
                    self.logger.warning(f"HTTP {response.status_code} for {url}, retrying...")
                    
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request error for {url} (attempt {attempt + 1}): {e}")
                
                if attempt < self.max_retries:
                    # Exponential backoff
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait_time)
        
        self.logger.error(f"Failed to fetch {url} after {self.max_retries + 1} attempts")
        return None
    
    def parse_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text"""
        if not price_text:
            return None
        
        # Remove common currency symbols and formatting
        import re
        
        # Clean the text
        cleaned = re.sub(r'[^\d.,]', '', str(price_text))
        
        # Handle different decimal separators
        if ',' in cleaned and '.' in cleaned:
            # Assume European format (1.234,56) if comma comes after dot
            if cleaned.rindex(',') > cleaned.rindex('.'):
                cleaned = cleaned.replace('.', '').replace(',', '.')
            else:
                # American format (1,234.56)
                cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Could be either decimal separator or thousands separator
            # If there are exactly 2 digits after comma, treat as decimal
            parts = cleaned.split(',')
            if len(parts) == 2 and len(parts[1]) == 2:
                cleaned = cleaned.replace(',', '.')
            else:
                cleaned = cleaned.replace(',', '')
        
        try:
            return float(cleaned)
        except ValueError:
            self.logger.warning(f"Could not parse price from: {price_text}")
            return None
    
    def validate_product(self, product: ScrapedProduct) -> List[str]:
        """Validate scraped product data and return list of issues"""
        issues = []
        
        if not product.item_name:
            issues.append("Missing item name")
        
        if not product.category:
            issues.append("Missing category")
        
        if not product.source_url:
            issues.append("Missing source URL")
        
        if product.unit_cost is not None:
            if product.unit_cost <= 0:
                issues.append("Invalid unit cost (must be positive)")
            if product.unit_cost > 1000000:
                issues.append("Unit cost seems unreasonably high")
        
        if product.unit_cost is not None and not product.unit:
            issues.append("Unit cost provided but unit is missing")
        
        return issues
    
    def _get_or_create_session(self, conn: sqlite3.Connection, session_id: Optional[str]) -> Optional[int]:
        """Get or create collection session and return database session ID"""
        if not session_id:
            return None
            
        conn.execute("""
            INSERT OR IGNORE INTO collection_sessions 
            (session_name, milestone, status)
            VALUES (?, ?, ?)
        """, (session_id, MILESTONE_DATA_COLLECTION, SESSION_STATUS_IN_PROGRESS))
        
        cursor = conn.execute(
            "SELECT id FROM collection_sessions WHERE session_name = ?",
            (session_id,)
        )
        session_row = cursor.fetchone()
        return session_row[0] if session_row else None
    
    def _insert_cost_item(self, conn: sqlite3.Connection, product: ScrapedProduct) -> Optional[int]:
        """Insert cost item and return the cost item ID"""
        conn.execute("""
            INSERT OR REPLACE INTO cost_items 
            (item_id, item_name, category_id, specifications, notes, status)
            VALUES (?, ?, 
                   (SELECT id FROM cost_categories WHERE code = ? LIMIT 1), 
                   ?, ?, ?)
        """, (
            product.item_id,
            product.item_name,
            product.category,
            json.dumps(product.specifications) if product.specifications else None,
            product.notes,
            STATUS_ACTIVE
        ))
        
        cursor = conn.execute(
            "SELECT id FROM cost_items WHERE item_id = ?",
            (product.item_id,)
        )
        cost_item_row = cursor.fetchone()
        return cost_item_row[0] if cost_item_row else None
    
    def _insert_pricing(self, conn: sqlite3.Connection, cost_item_id: int, product: ScrapedProduct) -> Optional[int]:
        """Insert pricing information and return pricing ID"""
        if product.unit_cost is None:
            return None
            
        conn.execute("""
            INSERT INTO cost_pricing 
            (cost_item_id, unit_cost, unit, effective_date, confidence_level)
            VALUES (?, ?, ?, DATE('now'), ?)
        """, (
            cost_item_id,
            product.unit_cost,
            product.unit or DEFAULT_UNIT,
            product.confidence_level
        ))
        
        cursor = conn.execute(
            "SELECT id FROM cost_pricing WHERE cost_item_id = ? ORDER BY id DESC LIMIT 1",
            (cost_item_id,)
        )
        pricing_row = cursor.fetchone()
        return pricing_row[0] if pricing_row else None
    
    def _insert_source_reference(self, conn: sqlite3.Connection, pricing_id: int, product: ScrapedProduct) -> bool:
        """Insert source reference and return success status"""
        if not product.source_url:
            return False
            
        # Get or create source
        conn.execute("""
            INSERT OR IGNORE INTO sources (company_name, company_type, tier)
            VALUES (?, ?, ?)
        """, (self.supplier_name, COMPANY_TYPE_SUPPLIER, SOURCE_TIER_PRIMARY))
        
        cursor = conn.execute(
            "SELECT id FROM sources WHERE company_name = ?",
            (self.supplier_name,)
        )
        source_row = cursor.fetchone()
        source_id = source_row[0] if source_row else None
        
        if not source_id:
            return False
            
        conn.execute("""
            INSERT INTO source_references 
            (cost_pricing_id, source_id, reference_type, source_url, 
             product_code, date_accessed)
            VALUES (?, ?, ?, ?, ?, DATE('now'))
        """, (
            pricing_id, source_id, REFERENCE_TYPE_PRIMARY, product.source_url,
            product.product_code
        ))
        
        return True
    
    def _log_collection_activity(self, conn: sqlite3.Connection, db_session_id: int, 
                               cost_item_id: int, product: ScrapedProduct) -> None:
        """Log collection activity for audit trail"""
        conn.execute("""
            INSERT INTO collection_log 
            (session_id, cost_item_id, action_type, new_values)
            VALUES (?, ?, ?, ?)
        """, (
            db_session_id, cost_item_id, ACTIVITY_TYPE_CREATED,
            json.dumps(asdict(product))
        ))
    
    def save_products(self, products: List[ScrapedProduct], 
                     session_id: Optional[str] = None) -> int:
        """Save scraped products to database"""
        if not products:
            return 0
        
        session_id = session_id or (self.current_session.session_id if self.current_session else None)
        saved_count = 0
        
        with sqlite3.connect(self.db_path) as conn:
            db_session_id = self._get_or_create_session(conn, session_id)
            
            for product in products:
                try:
                    # Insert cost item
                    cost_item_id = self._insert_cost_item(conn, product)
                    if not cost_item_id:
                        continue
                    
                    # Insert pricing and source reference if available
                    pricing_id = self._insert_pricing(conn, cost_item_id, product)
                    if pricing_id:
                        self._insert_source_reference(conn, pricing_id, product)
                    
                    # Log collection activity
                    if db_session_id:
                        self._log_collection_activity(conn, db_session_id, cost_item_id, product)
                    
                    saved_count += 1
                    
                except sqlite3.Error as e:
                    self.logger.error(f"Database error saving product {product.item_id}: {e}")
                    continue
            
            conn.commit()
        
        self.logger.info(f"Saved {saved_count} products to database")
        return saved_count
    
    @abstractmethod
    def scrape_products(self, **kwargs) -> List[ScrapedProduct]:
        """
        Abstract method to be implemented by concrete scrapers.
        Should return a list of ScrapedProduct objects.
        """
        pass
    
    def run_scraping_session(self, **kwargs) -> ScrapingResult:
        """
        Run complete scraping session with proper session management
        """
        self.start_session()
        exception_occurred = None
        
        try:
            # Run the actual scraping
            products = self.scrape_products(**kwargs)
            
            # Validate products
            for product in products:
                issues = self.validate_product(product)
                if issues:
                    self.current_session.warnings.extend([
                        f"{product.item_id}: {issue}" for issue in issues
                    ])
            
            # Save to database
            if products:
                saved_count = self.save_products(products)
                self.logger.info(f"Saved {saved_count}/{len(products)} products")
            
            self.current_session.products_scraped = products
            
        except Exception as e:
            self.logger.error(f"Scraping session failed: {e}")
            self.current_session.errors.append(str(e))
            exception_occurred = e
        finally:
            result = self.end_session()
        
        if exception_occurred:
            raise exception_occurred
        return result