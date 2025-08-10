#!/usr/bin/env python3
"""
Database Cleanup Script for Terra35 Vanilla Operations Cost Analysis

CRITICAL ISSUE IDENTIFIED: Database contains malformed item names with:
- Cost descriptions instead of equipment names
- Markdown formatting artifacts (⭐, -, $, etc.)
- Calculation text instead of proper product names
- Pricing ranges in name fields

This script cleans and normalizes all database entries.
"""

import sqlite3
import re
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseCleaner:
    def __init__(self, db_path: str = "data/costs/vanilla_costs.db"):
        self.db_path = db_path
        self.conn = None
        
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
    
    def backup_database(self):
        """Create backup before cleaning"""
        import shutil
        backup_path = self.db_path.replace('.db', '_pre_cleanup_backup.db')
        shutil.copy2(self.db_path, backup_path)
        logger.info(f"Backup created: {backup_path}")
    
    def clean_item_name(self, name: str) -> str:
        """Clean and normalize item name"""
        if not name:
            return "Unknown Item"
        
        # Remove markdown formatting
        name = re.sub(r'[⭐★✨]', '', name)  # Remove stars
        name = re.sub(r'\*\*([^*]+)\*\*', r'\\1', name)  # Remove **bold**
        name = re.sub(r'###?\s*', '', name)  # Remove ###
        name = re.sub(r'PRICING CONFIRMED|CONFIRMED|⭐|✅', '', name, flags=re.IGNORECASE)
        
        # Remove cost information from names
        name = re.sub(r'\$[0-9,]+(?:\.[0-9]{2})?(?:\s*-\s*\$[0-9,]+(?:\.[0-9]{2})?)?', '', name)
        name = re.sub(r'Cost:\s*.*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'Price:\s*.*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'Total:\s*.*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'Range:\s*.*$', '', name, flags=re.IGNORECASE)
        
        # Remove calculations and formulas
        name = re.sub(r'@\s*\$[0-9,]+.*?=.*$', '', name)  # Remove @ $X/hour = $Y
        name = re.sub(r'×\s*[0-9]+.*?=.*$', '', name)  # Remove × N = $Y
        name = re.sub(r'[0-9]+\s*hours?.*?=.*$', '', name, flags=re.IGNORECASE)
        
        # Remove leading dashes and bullets
        name = re.sub(r'^[\s\-•·]+', '', name)
        
        # Clean up parenthetical information that's not useful
        name = re.sub(r'\(complete installation\)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\(estimate.*?\)', '', name, flags=re.IGNORECASE)
        
        # Clean whitespace
        name = ' '.join(name.split())  # Normalize whitespace
        name = name.strip(' -:')  # Remove trailing punctuation
        
        # If name is too generic or empty, try to extract useful info
        if not name or name.lower() in ['total', 'cost', 'system', 'equipment', 'basic system', 'advanced system']:
            return "Equipment Cost Item"  # Generic fallback
        
        # Capitalize properly
        name = name.strip()
        if name and not name[0].isupper():
            name = name.capitalize()
        
        return name[:100]  # Limit length
    
    def normalize_unit_cost(self, cost_str: str) -> float:
        """Normalize cost values"""
        if not cost_str:
            return 0.0
        
        try:
            # Remove commas and convert
            cost_val = float(str(cost_str).replace(',', ''))
            
            # Sanity checks
            if cost_val < 0:
                return 0.0
            if cost_val > 10000000:  # 10M seems excessive
                logger.warning(f"Extremely high cost detected: ${cost_val}")
                return cost_val / 100 if cost_val > 100000000 else cost_val  # Maybe cents instead of dollars
            
            return cost_val
        except (ValueError, TypeError):
            logger.warning(f"Could not parse cost: {cost_str}")
            return 0.0
    
    def clean_all_items(self):
        """Clean all cost items in database"""
        logger.info("🧹 CLEANING ALL COST ITEMS")
        
        cursor = self.conn.cursor()
        
        # Get all items
        cursor.execute("SELECT id, item_name, item_id FROM cost_items")
        items = cursor.fetchall()
        
        cleaned_count = 0
        for item_id, item_name, item_code in items:
            original_name = item_name
            cleaned_name = self.clean_item_name(item_name)
            
            if cleaned_name != original_name:
                cursor.execute("""
                    UPDATE cost_items 
                    SET item_name = ? 
                    WHERE id = ?
                """, (cleaned_name, item_id))
                cleaned_count += 1
                logger.info(f"Cleaned: '{original_name[:50]}...' -> '{cleaned_name}'")
        
        logger.info(f"Cleaned {cleaned_count} item names")
        return cleaned_count
    
    def clean_pricing_data(self):
        """Clean pricing data"""
        logger.info("💰 CLEANING PRICING DATA")
        
        cursor = self.conn.cursor()
        
        # Get all pricing
        cursor.execute("SELECT id, unit_cost, unit FROM cost_pricing")
        pricing = cursor.fetchall()
        
        cleaned_count = 0
        for pricing_id, unit_cost, unit in pricing:
            original_cost = unit_cost
            normalized_cost = self.normalize_unit_cost(unit_cost)
            
            # Clean unit description
            cleaned_unit = unit if unit else 'per_item'
            if '$' in cleaned_unit:
                cleaned_unit = 'per_item'
            
            if normalized_cost != original_cost or cleaned_unit != unit:
                cursor.execute("""
                    UPDATE cost_pricing 
                    SET unit_cost = ?, unit = ?
                    WHERE id = ?
                """, (normalized_cost, cleaned_unit, pricing_id))
                cleaned_count += 1
                
                if normalized_cost != original_cost:
                    logger.info(f"Fixed cost: ${original_cost} -> ${normalized_cost}")
        
        logger.info(f"Cleaned {cleaned_count} pricing records")
        return cleaned_count
    
    def remove_invalid_items(self):
        """Remove items that are not actual products/equipment"""
        logger.info("🗑️  REMOVING INVALID ITEMS")
        
        cursor = self.conn.cursor()
        
        # Items that are clearly not products
        invalid_patterns = [
            'Application:',
            'Summary',
            'Analysis',
            'Requirements',
            'Risks',
            'Investment Analysis',
            'Cost Comparison',
            'Phase [0-9]:',
            'Program Economics',
            'ROI',
            'Mitigation',
            'Value Proposition',
            'Market Risks'
        ]
        
        removed_count = 0
        for pattern in invalid_patterns:
            cursor.execute("SELECT id, item_name FROM cost_items WHERE item_name LIKE ?", (f'%{pattern}%',))
            invalid_items = cursor.fetchall()
            
            for item_id, item_name in invalid_items:
                # Remove associated source references first
                cursor.execute("DELETE FROM source_references WHERE cost_item_id = ?", (item_id,))
                # Remove associated pricing
                cursor.execute("DELETE FROM cost_pricing WHERE cost_item_id = ?", (item_id,))
                # Finally remove the item
                cursor.execute("DELETE FROM cost_items WHERE id = ?", (item_id,))
                removed_count += 1
                logger.info(f"Removed invalid item: {item_name[:50]}...")
        
        logger.info(f"Removed {removed_count} invalid items")
        return removed_count
    
    def deduplicate_items(self):
        """Remove duplicate items"""
        logger.info("🔍 REMOVING DUPLICATES")
        
        cursor = self.conn.cursor()
        
        # Find duplicates by name and similar costs
        cursor.execute("""
            SELECT item_name, COUNT(*) as count 
            FROM cost_items 
            GROUP BY item_name 
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        
        removed_count = 0
        for item_name, count in duplicates:
            cursor.execute("SELECT id FROM cost_items WHERE item_name = ?", (item_name,))
            item_ids = cursor.fetchall()
            
            # Keep the first one, remove the rest
            for item_id_tuple in item_ids[1:]:
                item_id = item_id_tuple[0]
                cursor.execute("DELETE FROM cost_pricing WHERE cost_item_id = ?", (item_id,))
                cursor.execute("DELETE FROM cost_items WHERE id = ?", (item_id,))
                removed_count += 1
                logger.info(f"Removed duplicate: {item_name}")
        
        logger.info(f"Removed {removed_count} duplicate items")
        return removed_count
    
    def validate_data_quality(self):
        """Validate cleaned data quality"""
        logger.info("✅ VALIDATING DATA QUALITY")
        
        cursor = self.conn.cursor()
        
        # Count items by type
        cursor.execute("SELECT COUNT(*) FROM cost_items")
        total_items = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cost_items WHERE item_name LIKE '%$%'")
        items_with_cost_in_name = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cost_pricing WHERE unit_cost <= 0")
        zero_costs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cost_pricing WHERE unit_cost > 1000000")
        extreme_costs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sources")
        total_sources = cursor.fetchone()[0]
        
        return {
            'total_items': total_items,
            'items_with_cost_in_name': items_with_cost_in_name,
            'zero_costs': zero_costs,
            'extreme_costs': extreme_costs,
            'total_sources': total_sources,
            'data_quality_score': max(0, 100 - (items_with_cost_in_name + zero_costs + extreme_costs) * 5)
        }
    
    def comprehensive_cleanup(self):
        """Perform comprehensive database cleanup"""
        logger.info("🚨 STARTING COMPREHENSIVE DATABASE CLEANUP")
        
        # Backup first
        self.backup_database()
        
        # Clean items
        items_cleaned = self.clean_all_items()
        
        # Clean pricing
        pricing_cleaned = self.clean_pricing_data()
        
        # Remove invalid items
        invalid_removed = self.remove_invalid_items()
        
        # Remove duplicates
        duplicates_removed = self.deduplicate_items()
        
        # Commit changes
        self.conn.commit()
        
        # Validate quality
        quality_report = self.validate_data_quality()
        
        return {
            'items_cleaned': items_cleaned,
            'pricing_cleaned': pricing_cleaned,
            'invalid_removed': invalid_removed,
            'duplicates_removed': duplicates_removed,
            'quality_report': quality_report
        }

def main():
    """Main execution function"""
    print("🧹 DATABASE CLEANUP - Terra35 Vanilla Operations")
    print("=" * 60)
    print("CRITICAL: Cleaning malformed data from extraction process")
    
    cleaner = DatabaseCleaner()
    
    if not cleaner.connect_database():
        print("❌ Failed to connect to database")
        return 1
    
    try:
        # Perform comprehensive cleanup
        results = cleaner.comprehensive_cleanup()
        
        print(f"\n✅ CLEANUP COMPLETED:")
        print("-" * 40)
        print(f"📝 Items Cleaned: {results['items_cleaned']}")
        print(f"💰 Pricing Cleaned: {results['pricing_cleaned']}")
        print(f"🗑️  Invalid Items Removed: {results['invalid_removed']}")
        print(f"🔄 Duplicates Removed: {results['duplicates_removed']}")
        
        quality = results['quality_report']
        print(f"\n📊 FINAL DATA QUALITY:")
        print("-" * 40)
        print(f"📈 Quality Score: {quality['data_quality_score']}/100")
        print(f"📦 Total Items: {quality['total_items']}")
        print(f"🏢 Total Sources: {quality['total_sources']}")
        print(f"❌ Items with Cost in Name: {quality['items_with_cost_in_name']}")
        print(f"🚫 Zero Cost Items: {quality['zero_costs']}")
        print(f"⚠️  Extreme Cost Items: {quality['extreme_costs']}")
        
        if quality['data_quality_score'] >= 90:
            print("\n🎯 EXCELLENT: Database is now clean and ready for use!")
        elif quality['data_quality_score'] >= 75:
            print("\n✅ GOOD: Database quality significantly improved")
        else:
            print("\n⚠️  WARNING: Additional cleanup may be needed")
            
    finally:
        cleaner.conn.close()
    
    return 0

if __name__ == "__main__":
    exit(main())