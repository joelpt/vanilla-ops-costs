#!/usr/bin/env python3
"""
Database population script for Task 2.2 - Benching & Racking Systems
Based on verified research from greenhouse_benching_research_2025.md
"""

import sqlite3
from datetime import datetime

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
            'specifications': 'Material: 12 gauge steel construction, Height: 24" adjustable with 3" legs (27" total), Tray depth: 2-3/4", DTM Clear finish or powder coat, Anti-rotate stop plate, Optional trellis mount points, Lead time: 4-6 weeks',
            'notes': 'Verified pricing from BG Hydro website January 9, 2025. $15.00/sq ft for 4000+ sq ft orders. Good for vanilla with trellis mounting capability.',
            'unit_cost': 15.00,
            'unit': 'per_sq_ft',
            'total_5000sqft': 75000,
            'confidence': 'HIGH'
        },
        {
            'item_id': 'GA_METAL_ROLLING_4X18',
            'name': 'Gothic Arch Commercial Metal Rolling Bench (4\' x 18\')',
            'specifications': 'Height: 40-1/2" tall (32" bench surface), Frame: 1.25" 14-gauge galvanized steel, Side rails: 4" extruded aluminum, Load capacity: 27 lbs/sq ft, Stainless steel fasteners, Expanded metal topping',
            'notes': 'Verified pricing from Gothic Arch website January 9, 2025. $2,005.95 for 72 sq ft system. Excellent height for vanilla at 32" bench surface.',
            'unit_cost': 27.86,
            'unit': 'per_sq_ft',
            'total_5000sqft': 139300,
            'confidence': 'HIGH'
        },
        {
            'item_id': 'GA_METAL_ROLLING_5X30',
            'name': 'Gothic Arch Commercial Metal Rolling Bench (5\' x 30\')',
            'specifications': 'Height: 40-1/2" tall (32" bench surface), Frame: 1.25" 14-gauge galvanized steel, Side rails: 4" extruded aluminum, Load capacity: 27 lbs/sq ft, Stainless steel fasteners, Expanded metal topping',
            'notes': 'Verified pricing from Gothic Arch website January 9, 2025. $3,259.95 for 150 sq ft system. Excellent height for vanilla at 32" bench surface.',
            'unit_cost': 21.73,
            'unit': 'per_sq_ft',
            'total_5000sqft': 108650,
            'confidence': 'HIGH'
        },
        {
            'item_id': 'GA_METAL_ROLLING_6X66',
            'name': 'Gothic Arch Commercial Metal Rolling Bench (6\' x 66\')',
            'specifications': 'Height: 40-1/2" tall (32" bench surface), Frame: 1.25" 14-gauge galvanized steel, Side rails: 4" extruded aluminum, Load capacity: 27 lbs/sq ft, Stainless steel fasteners, Expanded metal topping',
            'notes': 'Verified pricing from Gothic Arch website January 9, 2025. $6,696.95 for 396 sq ft system. Excellent height for vanilla at 32" bench surface.',
            'unit_cost': 16.91,
            'unit': 'per_sq_ft',
            'total_5000sqft': 84550,
            'confidence': 'HIGH'
        },
        {
            'item_id': 'MARKET_BASIC_STATIONARY',
            'name': 'Market Average Basic Stationary Bench System',
            'specifications': 'Basic stationary systems with limited customization and standard materials',
            'notes': 'Industry average pricing from multiple sources January 9, 2025. Budget tier benching systems.',
            'unit_cost': 4.00,
            'unit': 'per_sq_ft',
            'total_5000sqft': 20000,
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'MARKET_PREMIUM_ROLLING',
            'name': 'Market Average Premium Rolling Bench System',
            'specifications': 'Advanced rolling systems with high-quality materials and custom configurations',
            'notes': 'Industry average pricing from multiple sources January 9, 2025. Premium tier with 25-30% space efficiency improvement.',
            'unit_cost': 16.00,
            'unit': 'per_sq_ft',
            'total_5000sqft': 80000,
            'confidence': 'MEDIUM'
        }
    ]
    
    # Insert cost items
    for system in benching_systems:
        try:
            cursor.execute('''
                INSERT INTO cost_items (item_id, item_name, category_id, specifications, notes, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'active', datetime('now'), datetime('now'))
            ''', (system['item_id'], system['name'], category_id, system['specifications'], system['notes']))
            
            # Insert pricing information
            cursor.execute('''
                INSERT INTO cost_pricing (item_id, unit_cost, unit, total_cost_5000sqft, confidence_level, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            ''', (system['item_id'], system['unit_cost'], system['unit'], system['total_5000sqft'], system['confidence']))
            
            print(f"✅ Added: {system['name']} - ${system['unit_cost']:.2f} {system['unit']} (Total: ${system['total_5000sqft']:,})")
            
        except Exception as e:
            print(f"❌ Error adding {system['item_id']}: {e}")
    
    # Add source references
    sources = [
        {
            'item_id': 'BGH_ROLLING_BENCH_5000',
            'supplier': 'BG Hydro',
            'url': 'https://www.bghydro.com/continuous-tray-rolling-bench-system-per-square-foot.html',
            'date_accessed': '2025-01-09',
            'verification_status': 'verified'
        },
        {
            'item_id': 'GA_METAL_ROLLING_4X18',
            'supplier': 'Gothic Arch Greenhouses',
            'url': 'https://www.gothicarchgreenhouses.com/rolling-greenhouse-benches',
            'date_accessed': '2025-01-09',
            'verification_status': 'verified'
        },
        {
            'item_id': 'GA_METAL_ROLLING_5X30',
            'supplier': 'Gothic Arch Greenhouses',
            'url': 'https://www.gothicarchgreenhouses.com/rolling-greenhouse-benches',
            'date_accessed': '2025-01-09',
            'verification_status': 'verified'
        },
        {
            'item_id': 'GA_METAL_ROLLING_6X66',
            'supplier': 'Gothic Arch Greenhouses',
            'url': 'https://www.gothicarchgreenhouses.com/rolling-greenhouse-benches',
            'date_accessed': '2025-01-09',
            'verification_status': 'verified'
        }
    ]
    
    for source in sources:
        try:
            cursor.execute('''
                INSERT INTO sources (item_id, supplier_name, source_url, date_accessed, verification_status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            ''', (source['item_id'], source['supplier'], source['url'], source['date_accessed'], source['verification_status']))
            
            print(f"✅ Added source: {source['supplier']} for {source['item_id']}")
            
        except Exception as e:
            print(f"❌ Error adding source for {source['item_id']}: {e}")
    
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