#!/usr/bin/env python3
"""
Database Population Script for Terra35 Vanilla Operations Cost Analysis

This script systematically extracts cost data from all research .md files
and populates the SQLite database with comprehensive cost items, sources,
and pricing information.

CRITICAL: This addresses the major project failure where 25 research files
were created but only 5 items populated in database.
"""

import sqlite3
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabasePopulator:
    def __init__(self, db_path: str = "data/costs/vanilla_costs.db"):
        self.db_path = db_path
        self.conn = None
        self.data_dir = Path("data")
        
        # Cost extraction patterns
        self.price_patterns = [
            r'\$([0-9,]+(?:\.[0-9]{2})?)',  # $123.45 or $1,234.56
            r'(\$[0-9,]+(?:\.[0-9]{2})?)\s*(?:per|/|each)',  # $123 per or $123/
            r'Price:\s*\$([0-9,]+(?:\.[0-9]{2})?)',  # Price: $123.45
            r'Cost:\s*\$([0-9,]+(?:\.[0-9]{2})?)',   # Cost: $123.45
            r'Total:\s*\$([0-9,]+(?:\.[0-9]{2})?)',  # Total: $123.45
        ]
        
        # URL patterns for source extraction
        self.url_pattern = r'https?://[^\s\)]+(?:\.[a-zA-Z]{2,})'
        
    def connect_database(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA foreign_keys = ON;")
            logger.info(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
            
    def close_database(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def get_category_id(self, category_name: str, revenue_stream: str = "Grow & Produce") -> Optional[int]:
        """Get category ID from database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT cc.id FROM cost_categories cc
                JOIN revenue_streams rs ON cc.revenue_stream_id = rs.id
                WHERE cc.name = ? AND rs.name = ?
            """, (category_name, revenue_stream))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting category ID: {e}")
            return None
    
    def insert_source(self, company_name: str, website_url: str, company_type: str = "supplier") -> int:
        """Insert source and return source ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO sources 
                (company_name, company_type, website_url, tier)
                VALUES (?, ?, ?, 1)
            """, (company_name, company_type, website_url))
            
            # Get the source ID
            cursor.execute("SELECT id FROM sources WHERE company_name = ?", (company_name,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error inserting source: {e}")
            return None
    
    def insert_cost_item(self, item_data: Dict) -> Optional[int]:
        """Insert cost item and return item ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO cost_items 
                (item_id, item_name, category_id, specifications, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (
                item_data['item_id'],
                item_data['item_name'], 
                item_data['category_id'],
                json.dumps(item_data.get('specifications', {})),
                item_data.get('notes', '')
            ))
            
            # Get the item ID
            cursor.execute("SELECT id FROM cost_items WHERE item_id = ?", (item_data['item_id'],))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error inserting cost item: {e}")
            return None
    
    def insert_pricing(self, pricing_data: Dict) -> bool:
        """Insert pricing data"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO cost_pricing 
                (cost_item_id, unit_cost, unit, effective_date, confidence_level, total_cost_5000sqft)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                pricing_data['cost_item_id'],
                pricing_data['unit_cost'],
                pricing_data['unit'],
                pricing_data['effective_date'],
                pricing_data['confidence_level'],
                pricing_data.get('total_cost_5000sqft')
            ))
            return True
        except Exception as e:
            logger.error(f"Error inserting pricing: {e}")
            return False
    
    def extract_costs_from_text(self, text: str) -> List[Dict]:
        """Extract cost information from markdown text"""
        costs = []
        lines = text.split('\n')
        
        current_item = None
        current_specs = {}
        current_price = None
        
        for line in lines:
            line = line.strip()
            
            # Look for item headers (typically ### or **Product Name**)
            if line.startswith('###') or ('**' in line and any(keyword in line.lower() for keyword in ['system', 'equipment', 'product', 'model'])):
                if current_item and current_price:
                    costs.append({
                        'name': current_item,
                        'price': current_price,
                        'specifications': current_specs.copy(),
                        'source_line': line
                    })
                
                # Reset for new item
                current_item = line.replace('###', '').replace('**', '').strip()
                current_specs = {}
                current_price = None
            
            # Extract prices using regex patterns
            for pattern in self.price_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    price_str = match.replace(',', '')
                    try:
                        current_price = float(price_str)
                        break
                    except ValueError:
                        continue
            
            # Extract specifications
            if ':' in line and not line.startswith('http'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip('- *')
                    value = parts[1].strip()
                    current_specs[key] = value
        
        # Don't forget the last item
        if current_item and current_price:
            costs.append({
                'name': current_item,
                'price': current_price,
                'specifications': current_specs,
                'source_line': current_item
            })
        
        return costs
    
    def extract_sources_from_text(self, text: str) -> List[Dict]:
        """Extract source URLs and companies from text"""
        sources = []
        lines = text.split('\n')
        
        for line in lines:
            # Find URLs
            urls = re.findall(self.url_pattern, line)
            for url in urls:
                # Extract company name from URL or context
                company_name = self.extract_company_from_url(url)
                if company_name:
                    sources.append({
                        'company_name': company_name,
                        'website_url': url,
                        'context_line': line
                    })
        
        return sources
    
    def extract_company_from_url(self, url: str) -> str:
        """Extract company name from URL"""
        # Common greenhouse/agricultural suppliers
        company_mapping = {
            'farmtek.com': 'FarmTek',
            'growspan.com': 'GrowSpan',
            'stuppy.com': 'Stuppy Greenhouse',
            'bghydro.com': 'BG Hydro',
            'gothicarchgreenhouses.com': 'Gothic Arch Greenhouses',
            'gavita.com': 'Gavita',
            'californialightworks.com': 'California LightWorks',
            'netafim.com': 'Netafim',
            'dramm.com': 'Dramm Corporation'
        }
        
        url_lower = url.lower()
        for domain, company in company_mapping.items():
            if domain in url_lower:
                return company
        
        # Extract domain as fallback
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return domain.replace('www.', '').replace('.com', '').title()
        except:
            return "Unknown Supplier"
    
    def determine_category(self, filename: str, content: str) -> str:
        """Determine cost category based on filename and content"""
        filename_lower = filename.lower()
        
        category_mapping = {
            'greenhouse': 'Greenhouse Infrastructure',
            'benching': 'Greenhouse Infrastructure', 
            'trellis': 'Greenhouse Infrastructure',
            'irrigation': 'Greenhouse Infrastructure',
            'climate': 'Greenhouse Infrastructure',
            'lighting': 'Greenhouse Infrastructure',
            'curing': 'Post-Harvest Processing',
            'dehydration': 'Post-Harvest Processing',
            'temperature': 'Post-Harvest Processing',
            'packaging': 'Post-Harvest Processing',
            'extraction': 'Processing Equipment',
            'distillation': 'Processing Equipment',
            'labor': 'Operational Costs',
            'energy': 'Utilities',
            'water': 'Utilities',
            'fertilizer': 'Growing Supplies',
            'growing_media': 'Growing Supplies',
            'substrate': 'Growing Supplies',
            'pollination': 'Growing Supplies',
            'quality': 'Quality Control',
            'waste': 'Waste Management',
            'renewable': 'Utilities'
        }
        
        for keyword, category in category_mapping.items():
            if keyword in filename_lower:
                return category
        
        return 'General Equipment'
    
    def process_research_file(self, filepath: Path) -> int:
        """Process a single research file and extract all cost data"""
        logger.info(f"Processing file: {filepath.name}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {e}")
            return 0
        
        # Determine category
        category_name = self.determine_category(filepath.name, content)
        category_id = self.get_category_id(category_name)
        
        if not category_id:
            logger.warning(f"Category '{category_name}' not found for file {filepath.name}")
            return 0
        
        # Extract sources and costs
        sources = self.extract_sources_from_text(content)
        costs = self.extract_costs_from_text(content)
        
        items_added = 0
        
        # Process sources
        source_ids = {}
        for source in sources:
            source_id = self.insert_source(
                source['company_name'],
                source['website_url']
            )
            if source_id:
                source_ids[source['company_name']] = source_id
        
        # Process costs
        for i, cost in enumerate(costs):
            if not cost['price'] or cost['price'] <= 0:
                continue
                
            # Generate item ID
            item_id = f"{filepath.stem.upper()}_{i+1:03d}"
            
            # Create item data
            item_data = {
                'item_id': item_id,
                'item_name': cost['name'],
                'category_id': category_id,
                'specifications': cost['specifications'],
                'notes': f"Extracted from {filepath.name} on {datetime.now().strftime('%Y-%m-%d')}"
            }
            
            # Insert item
            cost_item_id = self.insert_cost_item(item_data)
            
            if cost_item_id:
                # Insert pricing
                pricing_data = {
                    'cost_item_id': cost_item_id,
                    'unit_cost': cost['price'],
                    'unit': 'per_item',  # Default unit
                    'effective_date': datetime.now().strftime('%Y-%m-%d'),
                    'confidence_level': 'MEDIUM',  # Default confidence
                    'total_cost_5000sqft': None
                }
                
                if self.insert_pricing(pricing_data):
                    items_added += 1
                    logger.info(f"Added item: {cost['name']} - ${cost['price']}")
        
        self.conn.commit()
        return items_added
    
    def populate_all_research_files(self) -> Dict[str, int]:
        """Process all research files and populate database"""
        logger.info("Starting comprehensive database population from research files")
        
        results = {}
        total_items = 0
        
        # Find all research .md files
        research_files = list(self.data_dir.glob("*_2025.md"))
        logger.info(f"Found {len(research_files)} research files to process")
        
        for filepath in research_files:
            try:
                items_added = self.process_research_file(filepath)
                results[filepath.name] = items_added
                total_items += items_added
                logger.info(f"File {filepath.name}: {items_added} items added")
            except Exception as e:
                logger.error(f"Error processing file {filepath}: {e}")
                results[filepath.name] = 0
        
        logger.info(f"DATABASE POPULATION COMPLETE: {total_items} total items added across {len(research_files)} files")
        return results

def main():
    """Main execution function"""
    print("🚨 CRITICAL DATABASE POPULATION SCRIPT 🚨")
    print("Addressing major project failure: Research done but database empty")
    print("=" * 60)
    
    populator = DatabasePopulator()
    
    if not populator.connect_database():
        print("❌ Failed to connect to database")
        return 1
    
    try:
        # Populate database from all research files
        results = populator.populate_all_research_files()
        
        # Print summary
        print("\n📊 POPULATION SUMMARY:")
        print("-" * 40)
        total_items = sum(results.values())
        
        for filename, count in results.items():
            status = "✅" if count > 0 else "⚠️"
            print(f"{status} {filename}: {count} items")
        
        print("-" * 40)
        print(f"🎯 TOTAL ITEMS ADDED: {total_items}")
        
        # Verify database population
        cursor = populator.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cost_items")
        db_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sources")
        source_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cost_pricing")
        pricing_count = cursor.fetchone()[0]
        
        print(f"\n📈 DATABASE STATUS:")
        print(f"   Cost Items: {db_count}")
        print(f"   Sources: {source_count}")
        print(f"   Pricing Records: {pricing_count}")
        
        if total_items > 0:
            print("\n✅ SUCCESS: Database population completed!")
            print("   Milestone 2 tasks can now be properly marked as complete")
        else:
            print("\n⚠️  WARNING: No items were added - review extraction logic")
            
    finally:
        populator.close_database()
    
    return 0

if __name__ == "__main__":
    exit(main())