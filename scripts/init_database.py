#!/usr/bin/env python3
"""
Terra35 Vanilla Operations Cost Analysis Database Initialization

This script initializes the SQLite database with the required schema and initial data.
It can be run multiple times safely - it will only create missing tables and data.

Usage:
    python scripts/init_database.py [--recreate] [--db-path path/to/database.db]
    
Options:
    --recreate    Drop and recreate all tables (WARNING: destroys existing data)
    --db-path     Specify database file path (default: data/costs/vanilla_costs.db)
"""

import sqlite3
import json
import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class DatabaseInitializer:
    def __init__(self, db_path='data/costs/vanilla_costs.db', recreate=False):
        self.db_path = Path(db_path)
        self.recreate = recreate
        self.schema_path = project_root / 'config' / 'database_schema.sql'
        self.json_schema_path = project_root / 'config' / 'database_schema.json'
        self.taxonomy_path = project_root / 'config' / 'cost_category_taxonomy.json'
        
        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    def load_sql_schema(self):
        """Load SQL schema from file"""
        try:
            with open(self.schema_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print(f"ERROR: Schema file not found: {self.schema_path}")
            sys.exit(1)
    
    def load_json_config(self, config_path):
        """Load JSON configuration file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERROR: Config file not found: {config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in {config_path}: {e}")
            sys.exit(1)
    
    def create_database(self):
        """Create database and initialize with schema"""
        
        # Remove existing database if recreating
        if self.recreate and self.db_path.exists():
            print(f"Removing existing database: {self.db_path}")
            self.db_path.unlink()
        
        # Load SQL schema
        print("Loading database schema...")
        sql_schema = self.load_sql_schema()
        
        # Connect to database (creates file if doesn't exist)
        print(f"Connecting to database: {self.db_path}")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA temp_store=memory")
            
            # Execute schema
            print("Creating database schema...")
            conn.executescript(sql_schema)
            conn.commit()
            
            print("Database schema created successfully!")
            
        return self.db_path
    
    def populate_cost_categories(self):
        """Populate cost categories from taxonomy JSON"""
        print("Loading cost category taxonomy...")
        taxonomy = self.load_json_config(self.taxonomy_path)
        
        with sqlite3.connect(self.db_path) as conn:
            # Get revenue stream IDs
            revenue_stream_map = {}
            cursor = conn.execute("SELECT id, code FROM revenue_streams")
            for row in cursor:
                revenue_stream_map[row[1]] = row[0]
            
            # Insert cost categories
            categories_inserted = 0
            
            # Process each revenue stream
            for stream_code, stream_data in taxonomy['cost_taxonomy']['revenue_streams'].items():
                if stream_code not in revenue_stream_map:
                    continue
                    
                stream_id = revenue_stream_map[stream_code]
                categories = stream_data.get('categories', {})
                
                for cat_code, cat_data in categories.items():
                    # Insert main category
                    try:
                        conn.execute("""
                            INSERT OR IGNORE INTO cost_categories 
                            (revenue_stream_id, name, code, description)
                            VALUES (?, ?, ?, ?)
                        """, (stream_id, cat_data['name'], cat_code, cat_data.get('description', '')))
                        categories_inserted += 1
                    except sqlite3.IntegrityError:
                        pass  # Category already exists
                    
                    # Get category ID for subcategories
                    cursor = conn.execute("""
                        SELECT id FROM cost_categories 
                        WHERE revenue_stream_id = ? AND code = ?
                    """, (stream_id, cat_code))
                    cat_row = cursor.fetchone()
                    if not cat_row:
                        continue
                    parent_cat_id = cat_row[0]
                    
                    # Insert subcategories
                    subcategories = cat_data.get('subcategories', {})
                    for subcat_code, subcat_data in subcategories.items():
                        try:
                            conn.execute("""
                                INSERT OR IGNORE INTO cost_categories 
                                (revenue_stream_id, name, code, description, parent_category_id)
                                VALUES (?, ?, ?, ?, ?)
                            """, (stream_id, subcat_data['name'], subcat_code, 
                                 subcat_data.get('description', ''), parent_cat_id))
                            categories_inserted += 1
                        except sqlite3.IntegrityError:
                            pass  # Subcategory already exists
            
            # Process supporting operations
            if 'supporting_operations' in taxonomy['cost_taxonomy']:
                supporting_ops = taxonomy['cost_taxonomy']['supporting_operations']
                stream_id = revenue_stream_map.get('supporting_ops')
                
                if stream_id:
                    categories = supporting_ops.get('categories', {})
                    for cat_code, cat_data in categories.items():
                        try:
                            conn.execute("""
                                INSERT OR IGNORE INTO cost_categories 
                                (revenue_stream_id, name, code, description)
                                VALUES (?, ?, ?, ?)
                            """, (stream_id, cat_data['name'], cat_code, cat_data.get('description', '')))
                            categories_inserted += 1
                        except sqlite3.IntegrityError:
                            pass
                        
                        # Get category ID for subcategories
                        cursor = conn.execute("""
                            SELECT id FROM cost_categories 
                            WHERE revenue_stream_id = ? AND code = ?
                        """, (stream_id, cat_code))
                        cat_row = cursor.fetchone()
                        if not cat_row:
                            continue
                        parent_cat_id = cat_row[0]
                        
                        # Insert subcategories
                        subcategories = cat_data.get('subcategories', {})
                        for subcat_code, subcat_data in subcategories.items():
                            try:
                                conn.execute("""
                                    INSERT OR IGNORE INTO cost_categories 
                                    (revenue_stream_id, name, code, description, parent_category_id)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (stream_id, subcat_data['name'], subcat_code, 
                                     subcat_data.get('description', ''), parent_cat_id))
                                categories_inserted += 1
                            except sqlite3.IntegrityError:
                                pass
            
            conn.commit()
            print(f"Inserted {categories_inserted} cost categories")
    
    def create_initial_collection_session(self):
        """Create initial collection session for tracking"""
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO collection_sessions 
                    (session_name, milestone, status, notes)
                    VALUES (?, ?, ?, ?)
                """, ('Database Initialization', 'milestone_1', 'completed', 
                     'Initial database setup and schema creation'))
                conn.commit()
                print("Created initial collection session")
            except sqlite3.IntegrityError:
                pass  # Session already exists
    
    def verify_database(self):
        """Verify database was created correctly"""
        print("Verifying database structure...")
        
        with sqlite3.connect(self.db_path) as conn:
            # Check table existence
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor]
            
            expected_tables = [
                'collection_log', 'collection_sessions', 'cost_categories', 
                'cost_items', 'cost_pricing', 'revenue_streams',
                'source_references', 'sources', 'validation_results', 
                'validation_rules', 'volume_discounts'
            ]
            
            missing_tables = set(expected_tables) - set(tables)
            if missing_tables:
                print(f"ERROR: Missing tables: {missing_tables}")
                return False
            
            print(f"✓ All {len(tables)} tables created successfully")
            
            # Check revenue streams
            cursor = conn.execute("SELECT COUNT(*) FROM revenue_streams")
            stream_count = cursor.fetchone()[0]
            print(f"✓ Revenue streams: {stream_count}")
            
            # Check cost categories
            cursor = conn.execute("SELECT COUNT(*) FROM cost_categories")
            category_count = cursor.fetchone()[0]
            print(f"✓ Cost categories: {category_count}")
            
            # Check validation rules
            cursor = conn.execute("SELECT COUNT(*) FROM validation_rules")
            rule_count = cursor.fetchone()[0]
            print(f"✓ Validation rules: {rule_count}")
            
            return True
    
    def initialize(self):
        """Main initialization method"""
        print(f"Terra35 Vanilla Operations Database Initialization")
        print(f"Database: {self.db_path}")
        print(f"Recreate: {self.recreate}")
        print("-" * 50)
        
        try:
            # Create database and schema
            self.create_database()
            
            # Populate with initial data
            self.populate_cost_categories()
            self.create_initial_collection_session()
            
            # Verify everything worked
            if self.verify_database():
                print("\n" + "="*50)
                print("✅ Database initialization completed successfully!")
                print(f"Database location: {self.db_path.absolute()}")
                print("="*50)
                return True
            else:
                print("\n❌ Database verification failed!")
                return False
                
        except Exception as e:
            print(f"\n❌ Database initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    parser = argparse.ArgumentParser(description='Initialize Terra35 Vanilla Operations Cost Database')
    parser.add_argument('--recreate', action='store_true', 
                       help='Drop and recreate all tables (destroys existing data)')
    parser.add_argument('--db-path', default='data/costs/vanilla_costs.db',
                       help='Database file path (default: data/costs/vanilla_costs.db)')
    
    args = parser.parse_args()
    
    # Warn about data destruction
    if args.recreate:
        response = input("WARNING: --recreate will destroy all existing data. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    # Initialize database
    initializer = DatabaseInitializer(db_path=args.db_path, recreate=args.recreate)
    success = initializer.initialize()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()