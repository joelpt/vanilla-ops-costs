#!/usr/bin/env python3
"""
Unit tests for base scraper framework (base_scraper.py)
"""

import pytest
import json
import time
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta
import requests
import tempfile
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.scrapers.base_scraper import BaseScraper, ScrapedProduct, ScrapingResult


# Test implementation of abstract BaseScraper for testing
class MockScraper(BaseScraper):
    def scrape_products(self, **kwargs):
        """Test implementation of abstract method"""
        products = kwargs.get('products', [])
        return products


class TestScrapedProduct:
    """Test suite for ScrapedProduct dataclass"""
    
    def test_scraped_product_creation(self):
        """Test creating ScrapedProduct with required fields"""
        product = ScrapedProduct(
            item_id="TEST_001",
            item_name="Test Product",
            category="test_category",
            source_url="https://example.com"
        )
        
        assert product.item_id == "TEST_001"
        assert product.item_name == "Test Product"
        assert product.category == "test_category"
        assert product.source_url == "https://example.com"
        assert product.confidence_level == "MEDIUM"
        assert product.scraped_at != ""
        
    def test_scraped_product_with_optional_fields(self):
        """Test ScrapedProduct with all optional fields"""
        specifications = {"material": "steel", "size": "10x20"}
        volume_discounts = [{"quantity": "10+", "price": 100.0}]
        
        product = ScrapedProduct(
            item_id="TEST_002",
            item_name="Advanced Product",
            category="advanced",
            subcategory="premium",
            specifications=specifications,
            unit_cost=150.0,
            unit="each",
            volume_discounts=volume_discounts,
            source_url="https://example.com/product",
            product_code="ADV-002",
            confidence_level="HIGH",
            notes="Test notes"
        )
        
        assert product.subcategory == "premium"
        assert product.specifications == specifications
        assert product.unit_cost == 150.0
        assert product.unit == "each"
        assert product.volume_discounts == volume_discounts
        assert product.product_code == "ADV-002"
        assert product.confidence_level == "HIGH"
        assert product.notes == "Test notes"
        
    def test_scraped_product_auto_timestamp(self):
        """Test that scraped_at timestamp is automatically set"""
        before_creation = datetime.now()
        
        product = ScrapedProduct(
            item_id="TEST_TIME",
            item_name="Timestamp Test",
            category="time",
            source_url="https://example.com"
        )
        
        after_creation = datetime.now()
        scraped_time = datetime.fromisoformat(product.scraped_at)
        
        assert before_creation <= scraped_time <= after_creation


class TestScrapingResult:
    """Test suite for ScrapingResult dataclass"""
    
    def test_scraping_result_creation(self):
        """Test creating ScrapingResult with required fields"""
        start_time = datetime.now()
        result = ScrapingResult(
            supplier="TestSupplier",
            session_id="test_session_123",
            start_time=start_time
        )
        
        assert result.supplier == "TestSupplier"
        assert result.session_id == "test_session_123"
        assert result.start_time == start_time
        assert result.end_time is None
        assert result.products_scraped == []
        assert result.errors == []
        assert result.warnings == []
        assert result.cache_hits == 0
        assert result.requests_made == 0


class TestBaseScraper:
    """Test suite for BaseScraper class"""
    
    def test_base_scraper_initialization(self, temp_cache_dir):
        """Test BaseScraper initialization with default parameters"""
        scraper = MockScraper(
            supplier_name="TestSupplier",
            base_url="https://example.com",
            cache_dir=str(temp_cache_dir)
        )
        
        assert scraper.supplier_name == "TestSupplier"
        assert scraper.base_url == "https://example.com"
        assert scraper.rate_limit_delay == 1.0
        assert scraper.max_retries == 3
        assert scraper.timeout == 30
        assert scraper.cache_dir == temp_cache_dir
        
    def test_base_scraper_custom_parameters(self, temp_cache_dir, temp_db):
        """Test BaseScraper initialization with custom parameters"""
        scraper = MockScraper(
            supplier_name="CustomSupplier",
            base_url="https://custom.com",
            cache_dir=str(temp_cache_dir),
            db_path=temp_db,
            rate_limit_delay=2.0,
            max_retries=5,
            timeout=60
        )
        
        assert scraper.supplier_name == "CustomSupplier"
        assert scraper.base_url == "https://custom.com"
        assert scraper.rate_limit_delay == 2.0
        assert scraper.max_retries == 5
        assert scraper.timeout == 60
        assert scraper.db_path == temp_db
        
    def test_session_management(self, temp_cache_dir):
        """Test scraping session management"""
        scraper = MockScraper("TestSupplier", "https://example.com", cache_dir=str(temp_cache_dir))
        
        # Start session
        session_id = scraper.start_session()
        assert session_id.startswith("TestSupplier_")
        assert scraper.current_session is not None
        assert scraper.current_session.session_id == session_id
        assert scraper.current_session.supplier == "TestSupplier"
        
        # End session
        result = scraper.end_session()
        assert result.session_id == session_id
        assert result.end_time is not None
        assert scraper.current_session is None
        
    def test_end_session_without_start(self, temp_cache_dir):
        """Test ending session without starting one"""
        scraper = MockScraper("TestSupplier", "https://example.com", cache_dir=str(temp_cache_dir))
        
        with pytest.raises(ValueError, match="No active session to end"):
            scraper.end_session()
            
    def test_rate_limiting(self, temp_cache_dir):
        """Test rate limiting functionality"""
        scraper = MockScraper("TestSupplier", "https://example.com", 
                             cache_dir=str(temp_cache_dir), rate_limit_delay=0.1)
        
        # First call should not wait
        start_time = time.time()
        scraper.rate_limit()
        first_call_time = time.time() - start_time
        
        # Second call should wait
        start_time = time.time()
        scraper.rate_limit()
        second_call_time = time.time() - start_time
        
        assert first_call_time < 0.05  # Should be very fast
        assert second_call_time >= 0.1  # Should wait at least the delay
        
    def test_cache_key_generation(self, temp_cache_dir):
        """Test cache key generation"""
        scraper = MockScraper("TestSupplier", "https://example.com", cache_dir=str(temp_cache_dir))
        
        # Test with URL only
        key1 = scraper.get_cache_key("https://example.com/page")
        assert len(key1) == 32  # MD5 hash length
        
        # Test with URL and params
        key2 = scraper.get_cache_key("https://example.com/page", {"param1": "value1", "param2": "value2"})
        assert len(key2) == 32
        assert key1 != key2  # Should be different with params
        
        # Test consistency
        key3 = scraper.get_cache_key("https://example.com/page", {"param1": "value1", "param2": "value2"})
        assert key2 == key3  # Same input should produce same key
        
    def test_cache_save_and_load(self, temp_cache_dir):
        """Test cache saving and loading"""
        scraper = MockScraper("TestSupplier", "https://example.com", cache_dir=str(temp_cache_dir))
        
        # Save to cache
        cache_key = "test_key_123"
        response_data = {
            'url': 'https://example.com/test',
            'status_code': 200,
            'headers': {'Content-Type': 'text/html'},
            'content': '<html>test content</html>',
            'encoding': 'utf-8'
        }
        
        scraper.save_to_cache(cache_key, response_data)
        
        # Verify file was created
        cache_path = scraper.get_cache_path(cache_key)
        assert cache_path.exists()
        
        # Load from cache
        cached_data = scraper.load_from_cache(cache_key)
        assert cached_data is not None
        assert cached_data['url'] == response_data['url']
        assert cached_data['status_code'] == response_data['status_code']
        assert cached_data['content'] == response_data['content']
        
    def test_cache_expiration(self, temp_cache_dir):
        """Test cache expiration functionality"""
        scraper = MockScraper("TestSupplier", "https://example.com", cache_dir=str(temp_cache_dir))
        
        # Save to cache
        cache_key = "expired_key"
        response_data = {'url': 'https://example.com', 'status_code': 200, 'content': 'test'}
        scraper.save_to_cache(cache_key, response_data)
        
        # Modify timestamp to be old
        cache_path = scraper.get_cache_path(cache_key)
        with open(cache_path, 'r') as f:
            cached_data = json.load(f)
        
        # Set timestamp to 25 hours ago
        old_timestamp = (datetime.now() - timedelta(hours=25)).isoformat()
        cached_data['timestamp'] = old_timestamp
        
        with open(cache_path, 'w') as f:
            json.dump(cached_data, f)
        
        # Should return None for expired cache (max_age_hours=24 by default)
        result = scraper.load_from_cache(cache_key)
        assert result is None
        
    def test_cache_invalid_file(self, temp_cache_dir):
        """Test cache loading with invalid cache file"""
        scraper = MockScraper("TestSupplier", "https://example.com", cache_dir=str(temp_cache_dir))
        
        # Create invalid cache file
        cache_key = "invalid_key"
        cache_path = scraper.get_cache_path(cache_key)
        cache_path.write_text("invalid json content")
        
        # Should return None and not crash
        result = scraper.load_from_cache(cache_key)
        assert result is None
        
    @patch('requests.Session.get')
    def test_make_request_success(self, mock_get, temp_cache_dir):
        """Test successful HTTP request"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html>test content</html>'
        mock_response.url = 'https://example.com/test'
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response
        
        scraper = MockScraper("TestSupplier", "https://example.com", 
                             cache_dir=str(temp_cache_dir), rate_limit_delay=0.01)
        
        response = scraper.make_request("https://example.com/test")
        
        assert response is not None
        assert response.status_code == 200
        assert response.text == '<html>test content</html>'
        mock_get.assert_called_once()
        
    @patch('requests.Session.get')
    def test_make_request_with_cache(self, mock_get, temp_cache_dir):
        """Test HTTP request with cache hit"""
        scraper = MockScraper("TestSupplier", "https://example.com", 
                             cache_dir=str(temp_cache_dir), rate_limit_delay=0.01)
        
        # First request - should hit network
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html>cached content</html>'
        mock_response.url = 'https://example.com/cached'
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response
        
        response1 = scraper.make_request("https://example.com/cached")
        assert response1.status_code == 200
        assert mock_get.call_count == 1
        
        # Second request - should hit cache
        response2 = scraper.make_request("https://example.com/cached")
        assert response2.status_code == 200
        assert response2.text == '<html>cached content</html>'
        assert mock_get.call_count == 1  # No additional network call
        assert scraper.cache_hit_count == 1
        
    @patch('requests.Session.get')
    def test_make_request_retry_logic(self, mock_get, temp_cache_dir):
        """Test HTTP request retry logic"""
        scraper = MockScraper("TestSupplier", "https://example.com", 
                             cache_dir=str(temp_cache_dir), rate_limit_delay=0.01, max_retries=2)
        
        # Mock first two calls to fail, third to succeed
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 500
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.text = 'success'
        mock_response_success.url = 'https://example.com/retry'
        mock_response_success.headers = {}
        mock_response_success.encoding = 'utf-8'
        
        mock_get.side_effect = [mock_response_fail, mock_response_fail, mock_response_success]
        
        response = scraper.make_request("https://example.com/retry")
        
        assert response is not None
        assert response.status_code == 200
        assert mock_get.call_count == 3
        
    @patch('requests.Session.get')
    def test_make_request_max_retries_exceeded(self, mock_get, temp_cache_dir):
        """Test HTTP request when max retries exceeded"""
        scraper = MockScraper("TestSupplier", "https://example.com", 
                             cache_dir=str(temp_cache_dir), rate_limit_delay=0.01, max_retries=1)
        
        # All calls fail
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        response = scraper.make_request("https://example.com/fail")
        
        assert response is None
        assert mock_get.call_count == 2  # Initial call + 1 retry
        
    @patch('requests.Session.get')
    def test_make_request_non_retryable_error(self, mock_get, temp_cache_dir):
        """Test HTTP request with non-retryable error codes"""
        scraper = MockScraper("TestSupplier", "https://example.com", 
                             cache_dir=str(temp_cache_dir), rate_limit_delay=0.01)
        
        # 404 should not be retried
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        response = scraper.make_request("https://example.com/notfound")
        
        assert response is None
        assert mock_get.call_count == 1  # No retries for 404
        
    def test_parse_price_basic(self, temp_cache_dir):
        """Test basic price parsing"""
        scraper = MockScraper("TestSupplier", "https://example.com", cache_dir=str(temp_cache_dir))
        
        # Test various price formats
        assert scraper.parse_price("$123.45") == 123.45
        assert scraper.parse_price("123.45") == 123.45
        assert scraper.parse_price("$1,234.56") == 1234.56
        assert scraper.parse_price("1.234,56") == 1234.56  # European format
        assert scraper.parse_price("USD 99.99") == 99.99
        
    def test_parse_price_edge_cases(self, temp_cache_dir):
        """Test price parsing edge cases"""
        scraper = MockScraper("TestSupplier", "https://example.com", cache_dir=str(temp_cache_dir))
        
        assert scraper.parse_price("") is None
        assert scraper.parse_price(None) is None
        assert scraper.parse_price("No price available") is None
        assert scraper.parse_price("Price: $1,000") == 1000.0
        assert scraper.parse_price("€1.500,99") == 1500.99
        
    def test_validate_product_success(self, temp_cache_dir, sample_scraped_product):
        """Test successful product validation"""
        scraper = MockScraper("TestSupplier", "https://example.com", cache_dir=str(temp_cache_dir))
        
        issues = scraper.validate_product(sample_scraped_product)
        assert len(issues) == 0
        
    def test_validate_product_missing_required_fields(self, temp_cache_dir):
        """Test product validation with missing required fields"""
        scraper = MockScraper("TestSupplier", "https://example.com", cache_dir=str(temp_cache_dir))
        
        incomplete_product = ScrapedProduct(
            item_id="",  # Missing
            item_name="",  # Missing
            category="",  # Missing
            source_url=""  # Missing
        )
        
        issues = scraper.validate_product(incomplete_product)
        assert len(issues) == 3  # Required fields missing: item_name, category, source_url
        assert any("item name" in issue.lower() for issue in issues)
        assert any("category" in issue.lower() for issue in issues)
        assert any("source url" in issue.lower() for issue in issues)
        
    def test_validate_product_price_issues(self, temp_cache_dir):
        """Test product validation with price issues"""
        scraper = MockScraper("TestSupplier", "https://example.com", cache_dir=str(temp_cache_dir))
        
        # Test negative price
        product_negative = ScrapedProduct(
            item_id="TEST_NEG",
            item_name="Negative Price Product",
            category="test",
            source_url="https://example.com",
            unit_cost=-10.0
        )
        issues = scraper.validate_product(product_negative)
        assert any("positive" in issue.lower() for issue in issues)
        
        # Test extremely high price
        product_high = ScrapedProduct(
            item_id="TEST_HIGH",
            item_name="High Price Product", 
            category="test",
            source_url="https://example.com",
            unit_cost=2000000.0
        )
        issues = scraper.validate_product(product_high)
        assert any("unreasonably high" in issue.lower() for issue in issues)
        
        # Test price without unit
        product_no_unit = ScrapedProduct(
            item_id="TEST_NO_UNIT",
            item_name="No Unit Product",
            category="test", 
            source_url="https://example.com",
            unit_cost=100.0,
            unit=None
        )
        issues = scraper.validate_product(product_no_unit)
        assert any("unit is missing" in issue.lower() for issue in issues)
        
    def test_save_products_success(self, temp_cache_dir, temp_db, sample_scraped_product):
        """Test successful product saving to database"""
        scraper = MockScraper("TestSupplier", "https://example.com", 
                             cache_dir=str(temp_cache_dir), db_path=temp_db)
        
        products = [sample_scraped_product]
        saved_count = scraper.save_products(products, session_id="test_session")
        
        assert saved_count == 1
        
        # Verify data was saved
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.execute("SELECT item_id, item_name FROM cost_items WHERE item_id = ?", 
                                (sample_scraped_product.item_id,))
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == sample_scraped_product.item_id
            assert result[1] == sample_scraped_product.item_name
            
    def test_save_products_empty_list(self, temp_cache_dir, temp_db):
        """Test saving empty product list"""
        scraper = MockScraper("TestSupplier", "https://example.com", 
                             cache_dir=str(temp_cache_dir), db_path=temp_db)
        
        saved_count = scraper.save_products([])
        assert saved_count == 0
        
    def test_run_scraping_session_success(self, temp_cache_dir, temp_db):
        """Test complete scraping session"""
        scraper = MockScraper("TestSupplier", "https://example.com", 
                             cache_dir=str(temp_cache_dir), db_path=temp_db)
        
        # Create test products to return
        test_products = [
            ScrapedProduct(
                item_id="SESSION_TEST_001",
                item_name="Session Test Product 1",
                category="test",
                source_url="https://example.com/product1"
            ),
            ScrapedProduct(
                item_id="SESSION_TEST_002", 
                item_name="Session Test Product 2",
                category="test",
                source_url="https://example.com/product2"
            )
        ]
        
        result = scraper.run_scraping_session(products=test_products)
        
        assert isinstance(result, ScrapingResult)
        assert result.supplier == "TestSupplier"
        assert len(result.products_scraped) == 2
        assert result.end_time is not None
        assert len(result.errors) == 0
        
    def test_run_scraping_session_with_errors(self, temp_cache_dir, temp_db):
        """Test scraping session with errors"""
        scraper = MockScraper("TestSupplier", "https://example.com", 
                             cache_dir=str(temp_cache_dir), db_path=temp_db)
        
        # Mock scrape_products to raise an exception
        with patch.object(scraper, 'scrape_products', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                result = scraper.run_scraping_session()
        
        # Session should still be ended
        assert scraper.current_session is None