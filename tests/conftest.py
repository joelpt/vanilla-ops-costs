#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Terra35 unit tests
"""

import pytest
import sqlite3
import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import sys
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def temp_db():
    """Create temporary SQLite database for testing using full schema"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    # Use the actual database initializer to create a properly structured test database
    from scripts.init_database import DatabaseInitializer
    
    try:
        initializer = DatabaseInitializer(db_path, recreate=True)
        initializer.create_database()
        # Also need to populate categories from taxonomy
        initializer.populate_cost_categories()
    except Exception as e:
        # If initialization fails, fall back to a minimal schema
        print(f"Warning: Database initialization failed ({e}), using minimal schema")
        with sqlite3.connect(db_path) as conn:
            conn.executescript("""
                CREATE TABLE revenue_streams (
                    id INTEGER PRIMARY KEY,
                    code TEXT UNIQUE,
                    name TEXT
                );
                
                CREATE TABLE cost_categories (
                    id INTEGER PRIMARY KEY,
                    revenue_stream_id INTEGER,
                    name TEXT,
                    code TEXT,
                    description TEXT
                );
                
                CREATE TABLE cost_items (
                    id INTEGER PRIMARY KEY,
                    item_id TEXT UNIQUE,
                    item_name TEXT,
                    category_id INTEGER,
                    specifications TEXT,
                    notes TEXT,
                    status TEXT DEFAULT 'active'
                );
                
                CREATE TABLE collection_sessions (
                    id INTEGER PRIMARY KEY,
                    session_name TEXT,
                    milestone TEXT,
                    status TEXT,
                    notes TEXT
                );
                
                INSERT INTO revenue_streams (code, name) VALUES
                    ('grow_produce', 'Grow & Produce'),
                    ('partner_produce', 'Partner & Produce'),
                    ('make_produce', 'Make & Produce');
            """)
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)

@pytest.fixture
def temp_cache_dir():
    """Create temporary cache directory for testing"""
    temp_dir = tempfile.mkdtemp(prefix='test_cache_')
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def sample_config_data():
    """Sample configuration data for testing"""
    return {
        "version": "1.0",
        "data_quality_thresholds": {
            "excellent": 0.95,
            "good": 0.85,
            "acceptable": 0.70,
            "poor": 0.50
        },
        "price_ranges": {
            "min_reasonable_cost": 0.01,
            "max_reasonable_cost": 100000.0,
            "suspicious_high_threshold": 50000.0,
            "suspicious_low_threshold": 0.10
        },
        "data_freshness": {
            "max_age_days": 365,
            "preferred_age_days": 90,
            "critical_age_days": 730
        },
        "required_fields": {
            "cost_items": ["item_id", "item_name", "category"],
            "cost_pricing": ["unit_cost", "unit", "effective_date"],
            "source_references": ["source_url", "date_accessed"]
        },
        "confidence_weights": {
            "has_source": 0.25,
            "recent_data": 0.20,
            "complete_fields": 0.20,
            "reasonable_price": 0.15,
            "has_product_code": 0.10,
            "has_specifications": 0.10
        }
    }

@pytest.fixture
def sample_citation_config():
    """Sample citation configuration for testing"""
    return {
        "source_citation_format": {
            "version": "1.0",
            "citation_templates": {
                "supplier_website": {
                    "format": "{company_name}. \"{product_name}.\" {website_name}, accessed {date_accessed}. {source_url}",
                    "required_fields": ["company_name", "product_name", "website_name", "source_url", "date_accessed"]
                },
                "direct_quote": {
                    "format": "{contact_person}, {company_name}. Price quote #{quote_number}. {date_accessed}. Personal communication.",
                    "required_fields": ["company_name", "contact_person", "quote_number", "date_accessed"]
                }
            },
            "data_source_types": {
                "tier_1_preferred": {
                    "types": ["supplier_website", "direct_quote"],
                    "description": "Primary sources with highest reliability"
                },
                "tier_2_acceptable": {
                    "types": ["industry_report", "government_database"],
                    "description": "Secondary sources with good reliability"
                },
                "tier_3_caution": {
                    "types": ["comparable_product", "historical_data"],
                    "description": "Tertiary sources requiring additional validation"
                }
            },
            "citation_requirements": {
                "mandatory_fields": ["citation_type", "source_url", "company_name", "date_accessed"]
            }
        }
    }

@pytest.fixture
def sample_scraped_product():
    """Sample scraped product data for testing"""
    from scripts.scrapers.base_scraper import ScrapedProduct
    
    return ScrapedProduct(
        item_id="FARMTEK_GH123",
        item_name="Gothic Arch Greenhouse Kit 12x20",
        category="infrastructure",
        subcategory="structures",
        specifications={
            "size": "12' x 20'",
            "covering": "6mm twin-wall polycarbonate",
            "material": "galvanized steel"
        },
        unit_cost=2499.00,
        unit="each",
        volume_discounts=[
            {"quantity": "2-4 units", "price": 2299.00},
            {"quantity": "5+ units", "price": 2099.00}
        ],
        source_url="https://www.farmtek.com/product/gothic-arch-greenhouse-gt-1220",
        product_code="GT-1220",
        confidence_level="HIGH",
        notes="Price includes basic hardware kit"
    )

@pytest.fixture
def sample_item_data():
    """Sample item data for validation testing"""
    return {
        "item_id": "FARMTEK_GH123",
        "item_name": "Gothic Arch Greenhouse Kit 12x20",
        "category": "infrastructure",
        "specifications": {
            "size": "12' x 20'",
            "material": "galvanized steel"
        },
        "pricing": {
            "unit_cost": 2499.00,
            "unit": "each"
        },
        "sources": [
            {
                "source_url": "https://www.farmtek.com/product/gothic-arch-greenhouse-gt-1220",
                "date_accessed": "2024-12-30",
                "product_code": "GT-1220"
            }
        ]
    }

@pytest.fixture
def mock_requests():
    """Mock requests for testing scrapers"""
    with patch('requests.Session.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>Test Content</body></html>'
        mock_response.url = 'https://example.com'
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def temp_config_files(tmp_path):
    """Create temporary configuration files for testing"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Create validation config
    validation_config = {
        "version": "1.0",
        "data_quality_thresholds": {"excellent": 0.95, "good": 0.85, "acceptable": 0.70},
        "price_ranges": {"min_reasonable_cost": 0.01, "max_reasonable_cost": 100000.0},
        "confidence_weights": {"has_source": 0.25, "recent_data": 0.20}
    }
    
    with open(config_dir / "validation_config.json", 'w') as f:
        json.dump(validation_config, f)
    
    # Create citation config
    citation_config = {
        "source_citation_format": {
            "citation_templates": {
                "supplier_website": {
                    "format": "{company_name}. \"{product_name}.\" {website_name}, accessed {date_accessed}. {source_url}",
                    "required_fields": ["company_name", "product_name", "website_name", "source_url", "date_accessed"]
                }
            },
            "data_source_types": {
                "tier_1_preferred": {"types": ["supplier_website"]}
            },
            "citation_requirements": {
                "mandatory_fields": ["citation_type", "source_url", "company_name", "date_accessed"]
            }
        }
    }
    
    with open(config_dir / "source_citation_format.json", 'w') as f:
        json.dump(citation_config, f)
    
    # Copy the actual database schema file for integration tests
    actual_schema_path = project_root / 'config' / 'database_schema.sql'
    if actual_schema_path.exists():
        shutil.copy2(actual_schema_path, config_dir / "database_schema.sql")
    else:
        # Fallback minimal schema if full schema not available
        schema_sql = """
        CREATE TABLE revenue_streams (
            id INTEGER PRIMARY KEY,
            code TEXT UNIQUE,
            name TEXT
        );
        
        CREATE TABLE cost_categories (
            id INTEGER PRIMARY KEY,
            revenue_stream_id INTEGER,
            name TEXT,
            code TEXT,
            description TEXT
        );
        
        CREATE TABLE cost_items (
            id INTEGER PRIMARY KEY,
            item_id TEXT UNIQUE,
            item_name TEXT,
            category_id INTEGER,
            specifications TEXT,
            status TEXT DEFAULT 'active'
        );
        
        CREATE TABLE collection_sessions (
            id INTEGER PRIMARY KEY,
            session_name TEXT,
            status TEXT
        );
        
        INSERT INTO revenue_streams (code, name) VALUES
            ('grow_produce', 'Grow & Produce'),
            ('partner_produce', 'Partner & Produce'),
            ('make_produce', 'Make & Produce');
        """
        with open(config_dir / "database_schema.sql", 'w') as f:
            f.write(schema_sql)
    
    # Copy the actual taxonomy file for integration tests 
    actual_taxonomy_path = project_root / 'config' / 'cost_category_taxonomy.json'
    if actual_taxonomy_path.exists():
        shutil.copy2(actual_taxonomy_path, config_dir / "cost_category_taxonomy.json")
    else:
        # Fallback minimal taxonomy if full taxonomy not available
        taxonomy = {
            "cost_taxonomy": {
                "revenue_streams": {
                    "grow_produce": {
                        "categories": {
                            "infrastructure": {
                                "name": "Infrastructure",
                                "description": "Physical infrastructure costs"
                            }
                        }
                    }
                }
            }
        }
        with open(config_dir / "cost_category_taxonomy.json", 'w') as f:
            json.dump(taxonomy, f)
    
    return config_dir