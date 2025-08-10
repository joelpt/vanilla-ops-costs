#!/usr/bin/env python3
"""
Database population script for Task 2.4 - Irrigation & Fertigation Systems
Based on verified research from irrigation_fertigation_systems_research_2025.md
"""

import sqlite3
from datetime import date

def populate_irrigation_systems():
    conn = sqlite3.connect('data/costs/vanilla_costs.db')
    cursor = conn.cursor()
    
    # Get the category ID for Irrigation & Fertigation
    cursor.execute("SELECT id FROM cost_categories WHERE name = ?", ("Irrigation & Fertigation",))
    category_result = cursor.fetchone()
    if not category_result:
        print("ERROR: Category 'Irrigation & Fertigation' not found!")
        return
    
    category_id = category_result[0]
    print(f"Category ID found: {category_id}")
    
    # Define irrigation systems with verified pricing from research
    irrigation_systems = [
        {
            'item_id': 'DRIP_PROFESSIONAL_LOW',
            'name': 'Commercial Drip Irrigation System - Professional Installation (Low Range)',
            'specifications': '{"installation_type": "Professional", "coverage": "5000 sq ft greenhouse", "cost_per_sq_ft": 1.50, "includes": ["Materials", "Labor", "Basic automation"], "suitable_for": "Vanilla orchid epiphytes"}',
            'notes': 'Professional installation cost from multiple irrigation databases January 9, 2025. Lower end of commercial range suitable for basic vanilla irrigation needs.',
            'unit_cost': 1.50,
            'unit': 'per_sq_ft',
            'total_5000sqft': 7500,
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'DRIP_PROFESSIONAL_HIGH',
            'name': 'Commercial Drip Irrigation System - Professional Installation (High Range)',
            'specifications': '{"installation_type": "Professional", "coverage": "5000 sq ft greenhouse", "cost_per_sq_ft": 4.50, "includes": ["Premium materials", "Expert labor", "Advanced automation", "Precision control"], "suitable_for": "Vanilla orchid specialized requirements"}',
            'notes': 'Professional installation cost from multiple irrigation databases January 9, 2025. Higher end includes specialized orchid irrigation features and precision control.',
            'unit_cost': 4.50,
            'unit': 'per_sq_ft',
            'total_5000sqft': 22500,
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'DOSATRON_D9GL_11GPM',
            'name': 'Dosatron D9GL Nutrient Injection System (11 GPM)',
            'specifications': '{"flow_range": "132-2377 GPH", "injection_range": "0.2-2% (1:500 to 1:50)", "pressure": "4.4-116 PSI", "concentrated_injection": "1-180 l/h", "power": "Water-powered, no electricity", "application": "Medium ornamental production"}',
            'notes': 'Verified pricing from Greenhouse Megastore January 9, 2025. Gold standard for fertilizer injection systems. Suitable for 5000 sq ft vanilla cultivation.',
            'unit_cost': 528.00,
            'unit': 'per_unit',
            'total_5000sqft': 528,
            'confidence': 'HIGH'
        },
        {
            'item_id': 'DOSATRON_D14MZ2',
            'name': 'Dosatron D14MZ2 Nutrient Injection System (14 GPM)',
            'specifications': '{"flow_capacity": "14 GPM", "dosage_range": "Multiple ranges available", "features": ["Water-powered operation", "Easy maintenance", "Fits all irrigation systems", "Series/parallel configuration"], "application": "Commercial greenhouse fertigation"}',
            'notes': 'Verified pricing from agricultural supply distributors January 9, 2025. Higher capacity system suitable for larger greenhouse sections.',
            'unit_cost': 965.95,
            'unit': 'per_unit',
            'total_5000sqft': 966,
            'confidence': 'HIGH'
        },
        {
            'item_id': 'DOSATRON_ACCESSORIES',
            'name': 'Dosatron System Accessories Kit',
            'specifications': '{"y_filter_kit": 53.39, "mixing_chamber_kit": 88.99, "flow_restrictor": 66.11, "total_accessories": 208.49}',
            'notes': 'Essential accessories for Dosatron fertigation systems from Greenhouse Megastore January 9, 2025. Includes Y filter, mixing chamber, and flow restrictor components.',
            'unit_cost': 208.49,
            'unit': 'per_kit',
            'total_5000sqft': 208,
            'confidence': 'HIGH'
        },
        {
            'item_id': 'WATER_RECYCLING_BASIC',
            'name': 'Commercial Water Recycling System (Basic Level)',
            'specifications': '{"technology": "Sand filtration systems", "capacity": "5000 sq ft greenhouse", "efficiency": "Basic water recapture", "components": ["Sand filtration", "Basic collection"], "recycling_target": "40% water usage reduction"}',
            'notes': 'Commercial water recycling cost from industry sources January 9, 2025. Lower end of $20,000-$500,000 range for basic sand filtration systems.',
            'unit_cost': 20000.00,
            'unit': 'per_system',
            'total_5000sqft': 20000,
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'WATER_RECYCLING_ADVANCED',
            'name': 'Commercial Water Recycling System (Advanced Purification)',
            'specifications': '{"technology": ["Ozone treatment (99.999999% bacteria kill)", "UV light pathogen sterilization"], "flow_rate": "10-1000 GPM capacity", "efficiency": "Near 100% water recycling", "rainwater_collection": "0.62 gallons per sq ft per inch rainfall"}',
            'notes': 'Advanced commercial water recycling from industry sources January 9, 2025. Mid-range of commercial systems suitable for environmental sustainability goals.',
            'unit_cost': 100000.00,
            'unit': 'per_system',
            'total_5000sqft': 100000,
            'confidence': 'MEDIUM'
        }
    ]
    
    # Clear existing entries to prevent duplicates
    cursor.execute("DELETE FROM cost_items WHERE category_id = ? AND (item_id LIKE 'DRIP_%' OR item_id LIKE 'DOSATRON_%' OR item_id LIKE 'WATER_%')", (category_id,))
    
    # Insert cost items and pricing
    for system in irrigation_systems:
        try:
            # Insert cost item
            cursor.execute('''
                INSERT INTO cost_items (item_id, item_name, category_id, specifications, notes, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'active', datetime('now'), datetime('now'))
            ''', (system['item_id'], system['name'], category_id, system['specifications'], system['notes']))
            
            # Get the auto-generated ID for this cost item
            cost_item_db_id = cursor.lastrowid
            
            # Insert pricing information
            cursor.execute('''
                INSERT INTO cost_pricing (cost_item_id, unit_cost, unit, effective_date, total_cost_5000sqft, confidence_level, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            ''', (cost_item_db_id, system['unit_cost'], system['unit'], date.today(), system['total_5000sqft'], system['confidence']))
            
            print(f"✅ Added: {system['name']} - ${system['unit_cost']:.2f} {system['unit']} (Confidence: {system['confidence']})")
            
        except Exception as e:
            print(f"❌ Error adding {system['item_id']}: {e}")
    
    # Commit all changes
    conn.commit()
    
    # Verify additions
    cursor.execute("SELECT COUNT(*) FROM cost_items WHERE category_id = ?", (category_id,))
    item_count = cursor.fetchone()[0]
    print(f"\n✅ Total items in Irrigation & Fertigation category: {item_count}")
    
    conn.close()
    print("\n🎉 Task 2.4 Irrigation/Fertigation Systems database population completed successfully!")

if __name__ == "__main__":
    populate_irrigation_systems()