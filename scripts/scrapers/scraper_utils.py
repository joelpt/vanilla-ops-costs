#!/usr/bin/env python3
"""
Terra35 Vanilla Operations Cost Analysis - Scraper Utilities

Common utilities and helper functions for web scraping operations.
"""

import re
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common HTML entities
    entities = {
        '&amp;': '&',
        '&lt;': '<', 
        '&gt;': '>',
        '&quot;': '"',
        '&apos;': "'",
        '&nbsp;': ' ',
        '&#39;': "'",
        '&#x27;': "'",
        '&#x2F;': '/',
        '&#x60;': '`',
        '&#x3D;': '=',
    }
    
    for entity, replacement in entities.items():
        cleaned = cleaned.replace(entity, replacement)
    
    return cleaned

def extract_numeric_value(text: str) -> Optional[float]:
    """Extract first numeric value from text"""
    if not text:
        return None
    
    # Find first number (including decimals)
    match = re.search(r'(\d+(?:\.\d+)?)', str(text).replace(',', ''))
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    
    return None

def parse_dimensions(text: str) -> Dict[str, Any]:
    """Parse dimensional information from text"""
    dimensions = {}
    
    # Patterns for common dimensions
    patterns = {
        # Length x Width x Height patterns
        'lwh': re.compile(r'(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)', re.IGNORECASE),
        # Length x Width patterns  
        'lw': re.compile(r'(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)', re.IGNORECASE),
        # Individual dimensions with units
        'length': re.compile(r'(?:length|long|l)[:=]?\s*(\d+(?:\.\d+)?)\s*(?:ft|feet|in|inches|\'|")?', re.IGNORECASE),
        'width': re.compile(r'(?:width|wide|w)[:=]?\s*(\d+(?:\.\d+)?)\s*(?:ft|feet|in|inches|\'|")?', re.IGNORECASE),
        'height': re.compile(r'(?:height|high|tall|h)[:=]?\s*(\d+(?:\.\d+)?)\s*(?:ft|feet|in|inches|\'|")?', re.IGNORECASE),
        'depth': re.compile(r'(?:depth|deep|d)[:=]?\s*(\d+(?:\.\d+)?)\s*(?:ft|feet|in|inches|\'|")?', re.IGNORECASE),
    }
    
    # Try L x W x H pattern first
    lwh_match = patterns['lwh'].search(text)
    if lwh_match:
        dimensions.update({
            'length': float(lwh_match.group(1)),
            'width': float(lwh_match.group(2)), 
            'height': float(lwh_match.group(3))
        })
    elif patterns['lw'].search(text):
        lw_match = patterns['lw'].search(text)
        dimensions.update({
            'length': float(lw_match.group(1)),
            'width': float(lw_match.group(2))
        })
    
    # Try individual dimension patterns
    for dim_name, pattern in patterns.items():
        if dim_name in ['lwh', 'lw']:
            continue
            
        match = pattern.search(text)
        if match and dim_name not in dimensions:
            try:
                dimensions[dim_name] = float(match.group(1))
            except (ValueError, IndexError):
                continue
    
    return dimensions

def parse_specifications(text_content: str) -> Dict[str, Any]:
    """Parse product specifications from text content"""
    specs = {}
    
    # Split into lines and look for key-value pairs
    lines = text_content.split('\n')
    
    for line in lines:
        line = clean_text(line)
        if not line or len(line) < 3:
            continue
        
        # Look for various key-value separators
        separators = [':', '=', '-', '–', '—']
        for sep in separators:
            if sep in line:
                parts = line.split(sep, 1)
                if len(parts) == 2:
                    key = clean_text(parts[0])
                    value = clean_text(parts[1])
                    
                    # Filter out overly long keys/values
                    if len(key) < 50 and len(value) < 200:
                        specs[key] = value
                        break
    
    return specs

def categorize_product(product_name: str, description: str = "") -> Dict[str, str]:
    """Attempt to categorize product based on name and description"""
    text = f"{product_name} {description}".lower()
    
    # Category keywords
    categories = {
        'infrastructure/structures': ['greenhouse', 'frame', 'structure', 'kit', 'building'],
        'infrastructure/benching': ['bench', 'table', 'rack', 'stand', 'platform'],
        'infrastructure/climate_control': ['heater', 'cooler', 'ventilation', 'fan', 'hvac', 'temperature'],
        'infrastructure/irrigation': ['irrigation', 'watering', 'mist', 'drip', 'spray'],
        'infrastructure/lighting': ['light', 'lamp', 'led', 'fluorescent', 'grow light'],
        'operational_costs/growing_supplies': ['fertilizer', 'nutrient', 'soil', 'substrate', 'media'],
        'operational_costs/raw_materials': ['chemical', 'solution', 'additive'],
    }
    
    # Score each category
    scores = {}
    for category, keywords in categories.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > 0:
            scores[category] = score
    
    if scores:
        # Return highest scoring category
        best_category = max(scores, key=scores.get)
        parts = best_category.split('/')
        return {
            'category': parts[0],
            'subcategory': parts[1] if len(parts) > 1 else None
        }
    
    # Default fallback
    return {'category': 'infrastructure', 'subcategory': 'structures'}

def generate_item_id(supplier: str, product_name: str, product_code: Optional[str] = None) -> str:
    """Generate consistent item ID"""
    if product_code:
        # Use supplier + product code
        clean_code = re.sub(r'[^A-Z0-9]', '', product_code.upper())
        return f"{supplier.upper()}_{clean_code}"
    else:
        # Generate from product name
        clean_name = re.sub(r'[^a-zA-Z0-9]', '_', product_name.upper())
        clean_name = re.sub(r'_+', '_', clean_name)
        # Take first 20 characters
        clean_name = clean_name[:20].rstrip('_')
        # Add hash for uniqueness
        name_hash = hashlib.md5(product_name.encode()).hexdigest()[:6].upper()
        return f"{supplier.upper()}_{clean_name}_{name_hash}"

def validate_url(url: str) -> bool:
    """Validate URL format"""
    if not url:
        return False
    
    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))

def normalize_currency(price_text: str) -> Optional[float]:
    """Extract and normalize currency values"""
    if not price_text:
        return None
    
    # Remove currency symbols and common formatting
    cleaned = re.sub(r'[\$£€¥₹]', '', str(price_text))
    
    # Handle different number formats
    # European format: 1.234,56
    # American format: 1,234.56
    
    if ',' in cleaned and '.' in cleaned:
        # Both separators present
        comma_pos = cleaned.rfind(',')
        dot_pos = cleaned.rfind('.')
        
        if comma_pos > dot_pos:
            # European format (1.234,56)
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            # American format (1,234.56)
            cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
        # Only comma - could be thousands separator or decimal
        parts = cleaned.split(',')
        if len(parts) == 2 and len(parts[1]) <= 2:
            # Likely decimal separator
            cleaned = cleaned.replace(',', '.')
        else:
            # Likely thousands separator
            cleaned = cleaned.replace(',', '')
    
    # Extract numeric value
    match = re.search(r'(\d+(?:\.\d{1,2})?)', cleaned)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    
    return None

def detect_unit_from_text(text: str) -> str:
    """Detect measurement unit from text"""
    if not text:
        return 'each'
    
    text_lower = text.lower()
    
    # Unit patterns
    unit_patterns = {
        'per_sq_ft': [r'per\s+sq\.?\s*ft', r'/\s*sq\.?\s*ft', r'square\s+foot'],
        'per_foot': [r'per\s+f(?:oo)?t', r'/\s*f(?:oo)?t', r'linear\s+foot'],
        'per_gallon': [r'per\s+gal(?:lon)?', r'/\s*gal(?:lon)?'],
        'per_pound': [r'per\s+lb', r'per\s+pound', r'/\s*lb', r'/\s*pound'],
        'per_kg': [r'per\s+kg', r'per\s+kilogram', r'/\s*kg'],
        'per_liter': [r'per\s+l(?:iter)?', r'/\s*l(?:iter)?'],
        'per_piece': [r'per\s+piece', r'/\s*piece', r'each'],
        'per_pack': [r'per\s+pack', r'/\s*pack', r'per\s+package'],
    }
    
    for unit, patterns in unit_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return unit
    
    return 'each'

def save_scraper_config(config: Dict[str, Any], filepath: str):
    """Save scraper configuration to JSON file"""
    config_path = Path(filepath)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Add timestamp
    config['last_updated'] = datetime.now().isoformat()
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2, sort_keys=True)

def load_scraper_config(filepath: str) -> Dict[str, Any]:
    """Load scraper configuration from JSON file"""
    config_path = Path(filepath)
    
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

# Default scraper configurations
DEFAULT_SCRAPER_CONFIGS = {
    'farmtek': {
        'base_url': 'https://www.farmtek.com',
        'rate_limit_delay': 2.0,
        'categories': [
            '/greenhouse-kits/',
            '/greenhouse-benching/', 
            '/greenhouse-ventilation/',
            '/greenhouse-heating/',
            '/irrigation-systems/',
            '/growing-supplies/'
        ]
    },
    'growspan': {
        'base_url': 'https://www.growspan.com',
        'rate_limit_delay': 1.5,
        'categories': [
            '/greenhouse-structures/',
            '/climate-control/',
            '/growing-systems/'
        ]
    },
    'fisher_scientific': {
        'base_url': 'https://www.fishersci.com',
        'rate_limit_delay': 1.0,
        'categories': [
            '/laboratory-equipment/',
            '/chemicals/',
            '/lab-supplies/'
        ]
    }
}