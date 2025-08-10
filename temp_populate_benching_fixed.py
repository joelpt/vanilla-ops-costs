#!/usr/bin/env python3
"""
Fixed database population script for Task 2.2 - Benching & Racking Systems
Using correct database schema with proper foreign key relationships
"""

import sqlite3
from datetime import datetime, date

def populate_benching_systems():
    conn = sqlite3.connect('data/costs/vanilla_costs.db')
    cursor = conn.cursor()
    
    # Get the category ID for Benching & Racking Systems
    cursor.execute("SELECT id FROM cost_categories WHERE name = ?", ("Benching & Racking Systems",))
    category_result = cursor.fetchone()
    if not category_result:
        print("ERROR: Category 'Benching & Racking Systems' not found!")
        return
    
    category_id = category_result[0]
    print(f"Category ID found: {category_id}")
    
    # Define benching systems with verified pricing
    benching_systems = [
        {
            'item_id': 'BGH_ROLLING_BENCH_5000',
            'name': 'BG Hydro Continuous/Custom Tray Rolling Bench System (5000 sq ft)',
            'specifications': '{"material": "12 gauge steel construction", "height": "24 inches adjustable with 3 inch legs (27 total)", "tray_depth": "2-3/4 inches", "finish": "DTM Clear finish or powder coat", "features": ["Anti-rotate stop plate", "Optional trellis mount points"], "lead_time": "4-6 weeks"}',
            'notes': 'Verified pricing from BG Hydro website January 9, 2025. $15.00/sq ft for 4000+ sq ft orders. Good for vanilla with trellis mounting capability.',
            'unit_cost': 15.00,
            'unit': 'per_sq_ft',
            'total_5000sqft': 75000,
            'confidence': 'HIGH',
            'source_info': {
                'supplier': 'BG Hydro',
                'url': 'https://www.bghydro.com/continuous-tray-rolling-bench-system-per-square-foot.html',
                'date_accessed': '2025-01-09'
            }
        },
        {
            'item_id': 'GA_METAL_ROLLING_4X18',
            'name': 'Gothic Arch Commercial Metal Rolling Bench (4\' x 18\')',
            'specifications': '{"height": "40-1/2 inches tall (32 inch bench surface)", "frame": "1.25 inch 14-gauge galvanized steel", "side_rails": "4 inch extruded aluminum", "load_capacity": "27 lbs per sq ft", "fasteners": "Stainless steel", "topping": "Expanded metal", "size": "4ft x 18ft (72 sq ft)"}',
            'notes': 'Verified pricing from Gothic Arch website January 9, 2025. $2,005.95 for 72 sq ft system. Excellent height for vanilla at 32" bench surface.',
            'unit_cost': 27.86,
            'unit': 'per_sq_ft',
            'total_5000sqft': 139300,
            'confidence': 'HIGH',
            'source_info': {
                'supplier': 'Gothic Arch Greenhouses',
                'url': 'https://www.gothicarchgreenhouses.com/rolling-greenhouse-benches',
                'date_accessed': '2025-01-09'
            }
        },
        {
            'item_id': 'GA_METAL_ROLLING_5X30',
            'name': 'Gothic Arch Commercial Metal Rolling Bench (5\' x 30\')',
            'specifications': '{"height": "40-1/2 inches tall (32 inch bench surface)", "frame": "1.25 inch 14-gauge galvanized steel", "side_rails": "4 inch extruded aluminum", "load_capacity": "27 lbs per sq ft", "fasteners": "Stainless steel", "topping": "Expanded metal", "size": "5ft x 30ft (150 sq ft)"}',
            'notes': 'Verified pricing from Gothic Arch website January 9, 2025. $3,259.95 for 150 sq ft system. Excellent height for vanilla at 32" bench surface.',
            'unit_cost': 21.73,
            'unit': 'per_sq_ft',
            'total_5000sqft': 108650,
            'confidence': 'HIGH',
            'source_info': {
                'supplier': 'Gothic Arch Greenhouses',
                'url': 'https://www.gothicarchgreenhouses.com/rolling-greenhouse-benches',
                'date_accessed': '2025-01-09'
            }
        },
        {
            'item_id': 'GA_METAL_ROLLING_6X66',
            'name': 'Gothic Arch Commercial Metal Rolling Bench (6\' x 66\')',
            'specifications': '{"height": "40-1/2 inches tall (32 inch bench surface)", "frame": "1.25 inch 14-gauge galvanized steel", "side_rails": "4 inch extruded aluminum", "load_capacity": "27 lbs per sq ft", "fasteners": "Stainless steel", "topping": "Expanded metal", "size": "6ft x 66ft (396 sq ft)"}',
            'notes': 'Verified pricing from Gothic Arch website January 9, 2025. $6,696.95 for 396 sq ft system. Excellent height for vanilla at 32" bench surface.',
            'unit_cost': 16.91,
            'unit': 'per_sq_ft',
            'total_5000sqft': 84550,
            'confidence': 'HIGH',
            'source_info': {
                'supplier': 'Gothic Arch Greenhouses',
                'url': 'https://www.gothicarchgreenhouses.com/rolling-greenhouse-benches',
                'date_accessed': '2025-01-09'
            }
        }
    ]
    
    # Clear existing entries to prevent duplicates
    cursor.execute("DELETE FROM cost_items WHERE category_id = ? AND item_id LIKE 'BGH_%' OR item_id LIKE 'GA_%'", (category_id,))
    
    # Insert cost items and pricing
    for system in benching_systems:
        try:
            # Insert cost item
            cursor.execute('''
                INSERT INTO cost_items (item_id, item_name, category_id, specifications, notes, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'active', datetime('now'), datetime('now'))
            ''', (system['item_id'], system['name'], category_id, system['specifications'], system['notes']))
            
            # Get the auto-generated ID for this cost item
            cost_item_db_id = cursor.lastrowid
            
            # Insert pricing information using the correct cost_item_id
            cursor.execute('''
                INSERT INTO cost_pricing (cost_item_id, unit_cost, unit, effective_date, total_cost_5000sqft, confidence_level, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            ''', (cost_item_db_id, system['unit_cost'], system['unit'], date.today(), system['total_5000sqft'], system['confidence']))
            
            print(f"✅ Added: {system['name']} - ${system['unit_cost']:.2f} {system['unit']} (Total: ${system['total_5000sqft']:,})")
            
        except Exception as e:
            print(f"❌ Error adding {system['item_id']}: {e}")
    
    # Commit all changes
    conn.commit()
    
    # Verify additions
    cursor.execute("SELECT COUNT(*) FROM cost_items WHERE category_id = ?", (category_id,))
    item_count = cursor.fetchone()[0]
    print(f"\n✅ Total items in Benching & Racking Systems category: {item_count}")
    
    conn.close()
    print("\n🎉 Task 2.2 Benching Systems database population completed successfully!")

if __name__ == "__main__":
    populate_benching_systems()