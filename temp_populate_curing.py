#!/usr/bin/env python3
"""
Database population script for Task 2.7 - Curing Chamber Systems
Based on verified research from vanilla_curing_chamber_systems_research_2025.md
"""

import sqlite3
from datetime import date

def populate_curing_systems():
    conn = sqlite3.connect('data/costs/vanilla_costs.db')
    cursor = conn.cursor()
    
    # Get the category ID for Curing Chamber Systems
    cursor.execute("SELECT id FROM cost_categories WHERE name = ?", ("Curing Chamber Systems",))
    category_result = cursor.fetchone()
    if not category_result:
        print("ERROR: Category 'Curing Chamber Systems' not found!")
        return
    
    category_id = category_result[0]
    print(f"Category ID found: {category_id}")
    
    # Define curing systems with verified pricing from research
    curing_systems = [
        {
            'item_id': 'NYLE_FD24_DEHYDRATOR',
            'name': 'Nyle FD24 Commercial Heat Pump Dehydrator',
            'specifications': '{"manufacturer": "Nyle Dehydrators", "model": "FD24", "water_removal": "24 lbs/hour", "product_load": "800-1600 lbs wet product per batch", "temperature_range": "80-160°F (26-71°C) heat pump, 160-180°F (71-82°C) auxiliary", "capacity": "8 racks, 160 trays", "drying_space": "8\'2\\" D x 5\'2\\" L x 6\'0\\" H", "features": ["PLC controls", "Touchscreen interface", "Remote monitoring", "Precise humidity control"], "certifications": ["NSF Certified"]}',
            'notes': 'Verified pricing from Nyle Dehydrators website August 9, 2025. Includes installation. Financing available from $2,095/month. NSF certified for food safety.',
            'unit_cost': 102995.00,
            'unit': 'per_system',
            'total_5000sqft': 102995,
            'confidence': 'HIGH'
        },
        {
            'item_id': 'NYLE_FD60_DEHYDRATOR',
            'name': 'Nyle FD60 Commercial Heat Pump Dehydrator',
            'specifications': '{"manufacturer": "Nyle Dehydrators", "model": "FD60", "water_removal": "60 lbs/hour", "product_load": "1800-3600 lbs wet product per batch", "temperature_range": "80-160°F (26-71°C) heat pump, 160-180°F (71-82°C) auxiliary", "capacity": "18 racks, 360 trays", "drying_space": "13\'0\\" D x 7\'7\\" L x 6\'0\\" H", "features": ["Three 24\\" circulating fans", "PLC controls", "Touchscreen interface", "Data logging"], "certifications": ["NSF Certified"]}',
            'notes': 'Verified pricing from Nyle Dehydrators website August 9, 2025. Includes installation. Financing available from $2,095/month. Higher capacity system for larger operations.',
            'unit_cost': 149995.00,
            'unit': 'per_system',
            'total_5000sqft': 149995,
            'confidence': 'HIGH'
        },
        {
            'item_id': 'KING_SON_VANILLA_CHAMBER',
            'name': 'King Son Vanilla Curing Chamber 2.0 (Specialized System)',
            'specifications': '{"manufacturer": "King Son Instrument Tech Co., Ltd.", "model": "Vanilla Curing Chamber 2.0", "processing_integration": "All 5 stages (Killing, Sweating, Curing, Drying, Conditioning)", "capacity": "2 columns with 10 layer mesh trays each", "monitoring": "KSON APP with Wi-Fi real-time monitoring", "programs": "5 built-in vanilla pod sweating/fermentation modes", "features": ["Frozen pod processing", "4x traditional processing volume", "Climate simulation", "Program control automation"]}',
            'notes': 'Industry-leading specialized vanilla processing equipment from Taiwan. Website inaccessible during validation (August 9, 2025). Custom quotes required. Premium pricing expected for specialized functionality.',
            'unit_cost': 122500.00,  # Mid-range of $80k-165k estimate
            'unit': 'per_system',
            'total_5000sqft': 122500,
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'NYLE_ADAPTED_VANILLA_SYSTEM',
            'name': 'Nyle Dehydrator with Vanilla-Specific Modifications',
            'specifications': '{"base_system": "Nyle FD24 or FD60", "modifications": ["Vanilla-specific humidity control", "Fermentation chamber additions", "Control system integration"], "temperature_control": "35-65°C precision", "humidity_management": "65-85% RH during fermentation", "multi_stage": "Separate chambers for sweating, fermentation, drying"}',
            'notes': 'Complete vanilla curing system based on verified Nyle equipment with specialized modifications for vanilla processing requirements. August 9, 2025 analysis.',
            'unit_cost': 172995.00,  # Mid-range of $135,995-209,995
            'unit': 'per_system',
            'total_5000sqft': 172995,
            'confidence': 'HIGH'
        },
        {
            'item_id': 'CUSTOM_MULTI_CHAMBER_SYSTEM',
            'name': 'Custom-Built Multi-Chamber Vanilla Curing System',
            'specifications': '{"chambers": "Multiple processing chambers (sweating, drying, conditioning)", "controls": "Advanced environmental controls", "automation": "Monitoring and control systems", "installation": "Engineering and professional installation", "customization": "Tailored for specific space and process requirements"}',
            'notes': 'Custom-built system designed specifically for vanilla curing operations. Modular design allows for expansion and customization. August 9, 2025 cost analysis.',
            'unit_cost': 87500.00,  # Mid-range of $65,000-110,000
            'unit': 'per_system',
            'total_5000sqft': 87500,
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'TRADITIONAL_MODERN_CONTROLS',
            'name': 'Traditional Methods with Modern Controls System',
            'specifications': '{"sweating_boxes": "Traditional sweating boxes with modern temperature/humidity controls (8 units)", "drying_chamber": "Commercial drying chamber", "monitoring": "Environmental monitoring systems", "storage": "Conditioning storage systems", "approach": "Proven traditional methods enhanced with modern technology"}',
            'notes': 'Cost-effective approach combining traditional vanilla curing methods with modern environmental controls and monitoring. Suitable for smaller operations. August 9, 2025 analysis.',
            'unit_cost': 54000.00,  # Mid-range of $38,000-70,000
            'unit': 'per_system',
            'total_5000sqft': 54000,
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'VANILLA_CURING_MODIFICATIONS',
            'name': 'Vanilla-Specific Equipment Modifications Package',
            'specifications': '{"temperature_control": "Precision control for 35-65°C range", "humidity_management": "65-85% RH during fermentation phases", "monitoring_systems": "Data logging and remote access capabilities", "installation": "Professional integration with existing equipment"}',
            'notes': 'Modification package to adapt existing commercial dehydrators for vanilla-specific requirements. Essential for proper fermentation and curing stages. August 9, 2025 pricing.',
            'unit_cost': 22500.00,  # Mid-range of $15,000-30,000
            'unit': 'per_modification',
            'total_5000sqft': 22500,
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'SWEATING_BOX_MODERN',
            'name': 'Traditional Sweating Box with Modern Controls (Single Unit)',
            'specifications': '{"construction": "Insulated wooden or metal construction", "heating": "Electric heating elements with thermostatic control", "capacity": "Sized for daily batch processing", "controls": "Modern temperature and humidity monitoring", "application": "Traditional vanilla sweating process"}',
            'notes': 'Individual sweating box unit with modern environmental controls. Multiple units required for complete system (typically 8 units for commercial operation). August 9, 2025 pricing.',
            'unit_cost': 2500.00,  # Mid-range estimate for single unit
            'unit': 'per_unit',
            'total_5000sqft': 20000,  # 8 units for complete system
            'confidence': 'MEDIUM'
        }
    ]
    
    # Clear existing entries to prevent duplicates
    cursor.execute("DELETE FROM cost_items WHERE category_id = ? AND (item_id LIKE 'NYLE_%' OR item_id LIKE 'KING_%' OR item_id LIKE 'CUSTOM_%' OR item_id LIKE 'TRADITIONAL_%' OR item_id LIKE 'VANILLA_%' OR item_id LIKE 'SWEATING_%')", (category_id,))
    
    # Insert cost items and pricing
    for system in curing_systems:
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
            
            print(f"✅ Added: {system['name']} - ${system['unit_cost']:,.2f} {system['unit']} (Confidence: {system['confidence']})")
            
        except Exception as e:
            print(f"❌ Error adding {system['item_id']}: {e}")
    
    # Commit all changes
    conn.commit()
    
    # Verify additions
    cursor.execute("SELECT COUNT(*) FROM cost_items WHERE category_id = ?", (category_id,))
    item_count = cursor.fetchone()[0]
    print(f"\n✅ Total items in Curing Chamber Systems category: {item_count}")
    
    conn.close()
    print("\n🎉 Task 2.7 Curing Chamber Systems database population completed successfully!")

if __name__ == "__main__":
    populate_curing_systems()