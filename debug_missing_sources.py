#!/usr/bin/env python3
"""
Debug script to identify missing source references
"""

import sqlite3
from pathlib import Path

def get_database_path():
    script_dir = Path(__file__).parent
    db_path = script_dir / "data" / "costs" / "vanilla_costs.db"
    return str(db_path)

def debug_missing_sources():
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== DEBUGGING MISSING SOURCE REFERENCES ===")
    
    # Test 1: Basic counts
    cursor.execute("SELECT COUNT(*) FROM cost_pricing")
    total_pricing = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM source_references")
    total_references = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT cost_pricing_id) FROM source_references")
    unique_pricing_with_refs = cursor.fetchone()[0]
    
    print(f"Total cost_pricing entries: {total_pricing}")
    print(f"Total source_references: {total_references}")
    print(f"Unique cost_pricing with refs: {unique_pricing_with_refs}")
    print(f"Missing: {total_pricing - unique_pricing_with_refs}")
    print()
    
    # Test 2: Find missing entries with LEFT JOIN
    cursor.execute("""
        SELECT cp.id, ci.item_name, cc.name as category
        FROM cost_pricing cp
        JOIN cost_items ci ON cp.cost_item_id = ci.id
        JOIN cost_categories cc ON ci.category_id = cc.id
        LEFT JOIN source_references sr ON cp.id = sr.cost_pricing_id
        WHERE sr.cost_pricing_id IS NULL
        LIMIT 10
    """)
    
    missing_entries = cursor.fetchall()
    print(f"Found {len(missing_entries)} missing entries (first 10):")
    for entry in missing_entries:
        print(f"  ID: {entry[0]}, Item: {entry[1]}, Category: {entry[2]}")
    
    conn.close()

if __name__ == "__main__":
    debug_missing_sources()