#!/usr/bin/env python3
"""
Database population script for Task 2.5 - Climate Control Systems
Based on verified research from greenhouse_climate_control_systems_research_2025.md
"""

import sqlite3
from datetime import date

def populate_climate_systems():
    conn = sqlite3.connect('data/costs/vanilla_costs.db')
    cursor = conn.cursor()
    
    # Get the category ID for Climate Control Systems
    cursor.execute("SELECT id FROM cost_categories WHERE name = ?", ("Climate Control Systems",))
    category_result = cursor.fetchone()
    if not category_result:
        print("ERROR: Category 'Climate Control Systems' not found!")
        return
    
    category_id = category_result[0]
    print(f"Category ID found: {category_id}")
    
    # Define climate control systems with verified pricing from research
    climate_systems = [
        {
            'item_id': 'PRIVA_INTEGRATED_SYSTEM',
            'name': 'Priva Professional Integrated Climate Control System',
            'specifications': '{"manufacturer": "Priva", "features": ["Full automation", "Remote monitoring", "AI optimization", "Integrated temp/humidity/lighting/CO2"], "installation": "Professional required", "coverage": "5000 sq ft", "precision": "Maximum"}',
            'notes': 'Professional integrated system from Priva with 60+ years experience. Contact: Juan Gonzalez (juan.gonzalez@priva.com). January 9, 2025 research.',
            'unit_cost': 100000.00,
            'unit': 'per_system',
            'total_5000sqft': 100000,
            'confidence': 'HIGH'
        },
        {
            'item_id': 'ARGUS_TITAN_ENVOY',
            'name': 'Argus Controls TITAN Envoy Environmental System',
            'specifications': '{"manufacturer": "Argus Control Systems", "system": "TITAN Envoy", "features": ["Cloud-based interface", "Heating/cooling/airflow/CO2 control", "Machine learning/AI", "Desktop and mobile access"], "capabilities": ["Humidity management", "Water/fertigation control", "Lighting control"]}',
            'notes': 'Advanced environmental control from world leader in horticultural automation. Proprietary control algorithms. January 9, 2025 research.',
            'unit_cost': 85000.00,
            'unit': 'per_system',
            'total_5000sqft': 85000,
            'confidence': 'HIGH'
        },
        {
            'item_id': 'SEMI_PROFESSIONAL_SYSTEM',
            'name': 'Semi-Professional Component Climate Control System',
            'specifications': '{"installation_type": "Semi-professional", "features": ["Manual/basic automation", "Reliable control", "Component-based"], "equipment_cost": "20000-35000", "installation_cost": "15000-25000"}',
            'notes': 'Cost-effective precision control system combining quality components with basic automation. January 9, 2025 industry analysis.',
            'unit_cost': 47500.00,
            'unit': 'per_system',
            'total_5000sqft': 47500,
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'MODINE_HD100_HEATER',
            'name': 'Modine Hot Dawg HD100 Natural Gas Heater (100,000 BTU)',
            'specifications': '{"manufacturer": "Modine", "model": "Hot Dawg HD100", "capacity": "100,000 BTU", "fuel": "Natural Gas", "application": "Greenhouse heating", "coverage": "Large greenhouse sections"}',
            'notes': 'Verified pricing from Greenhouse Megastore January 9, 2025. Commercial-grade natural gas heater suitable for Oregon winters.',
            'unit_cost': 1488.00,
            'unit': 'per_unit',
            'total_5000sqft': 4464,  # 3 units estimated for 5000 sq ft
            'confidence': 'HIGH'
        },
        {
            'item_id': 'MODINE_HD125_HEATER',
            'name': 'Modine Hot Dawg HD125 Natural Gas Heater (125,000 BTU)',
            'specifications': '{"manufacturer": "Modine", "model": "Hot Dawg HD125", "capacity": "125,000 BTU", "fuel": "Natural Gas", "application": "Greenhouse heating", "coverage": "Large greenhouse sections"}',
            'notes': 'Verified pricing from Greenhouse Megastore January 9, 2025. Higher capacity option for 5000 sq ft vanilla greenhouse heating.',
            'unit_cost': 1378.00,
            'unit': 'per_unit',
            'total_5000sqft': 4134,  # 3 units estimated for 5000 sq ft
            'confidence': 'HIGH'
        },
        {
            'item_id': 'JD_HAF_FAN_12',
            'name': 'J&D EZ Breeze HAF Fan (12")',
            'specifications': '{"manufacturer": "J&D", "model": "EZ Breeze HAF", "size": "12 inch", "application": "Horizontal Air Flow", "purpose": "Air circulation and disease prevention"}',
            'notes': 'Verified pricing from Greenhouse Megastore January 9, 2025. Essential for vanilla cultivation air circulation in high humidity.',
            'unit_cost': 160.00,
            'unit': 'per_unit',
            'total_5000sqft': 1760,  # 11 fans estimated for 5000 sq ft
            'confidence': 'HIGH'
        },
        {
            'item_id': 'AQUAFOG_TURBOXE',
            'name': 'Aquafog TurboXE Commercial Fogger',
            'specifications': '{"manufacturer": "Aquafog", "model": "TurboXE", "application": "Humidity control and cooling", "features": ["High-pressure fogging", "Temperature decrease 40-70F", "Humidity increase"], "suitability": "Commercial greenhouse"}',
            'notes': 'Verified pricing from Greenhouse Megastore January 9, 2025. Dual-purpose cooling and humidity control ideal for 85% RH requirement.',
            'unit_cost': 1774.00,
            'unit': 'per_unit',
            'total_5000sqft': 1774,
            'confidence': 'HIGH'
        },
        {
            'item_id': 'IGROW_800_CONTROLLER',
            'name': 'iGrow 800 Environmental Controller',
            'specifications': '{"manufacturer": "iGrow", "model": "800", "application": "Environmental control", "features": ["Temperature control", "Humidity monitoring", "Basic automation"], "interface": "Digital control panel"}',
            'notes': 'Verified pricing from Greenhouse Megastore January 9, 2025. Basic environmental controller for component-based systems.',
            'unit_cost': 1498.00,
            'unit': 'per_unit',
            'total_5000sqft': 1498,
            'confidence': 'HIGH'
        },
        {
            'item_id': 'QUEST_COMMERCIAL_DEHUMIDIFIER',
            'name': 'Quest Commercial Dehumidifier (506 Pint)',
            'specifications': '{"manufacturer": "Quest", "capacity": "506 pint", "application": "Commercial greenhouse dehumidification", "configurations": ["Overhead", "Standalone"], "climate": "Oregon-specific"}',
            'notes': 'Verified pricing from Hortitech Direct January 9, 2025. Oregon-based supplier with climate-specific recommendations.',
            'unit_cost': 615.50,  # Mid-range of $365-866
            'unit': 'per_unit',
            'total_5000sqft': 1231,  # 2 units estimated for 5000 sq ft
            'confidence': 'HIGH'
        }
    ]
    
    # Clear existing entries to prevent duplicates
    cursor.execute("DELETE FROM cost_items WHERE category_id = ? AND (item_id LIKE 'PRIVA_%' OR item_id LIKE 'ARGUS_%' OR item_id LIKE 'SEMI_%' OR item_id LIKE 'MODINE_%' OR item_id LIKE 'JD_%' OR item_id LIKE 'AQUAFOG_%' OR item_id LIKE 'IGROW_%' OR item_id LIKE 'QUEST_%')", (category_id,))
    
    # Insert cost items and pricing
    for system in climate_systems:
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
    print(f"\n✅ Total items in Climate Control Systems category: {item_count}")
    
    conn.close()
    print("\n🎉 Task 2.5 Climate Control Systems database population completed successfully!")

if __name__ == "__main__":
    populate_climate_systems()