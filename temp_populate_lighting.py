#!/usr/bin/env python3
"""
Database population script for Task 2.6 - Supplemental Lighting Systems
Based on verified research from vanilla_supplemental_lighting_research_2025.md
"""

import sqlite3
from datetime import date

def populate_lighting_systems():
    conn = sqlite3.connect('data/costs/vanilla_costs.db')
    cursor = conn.cursor()
    
    # Get the category ID for Supplemental Lighting
    cursor.execute("SELECT id FROM cost_categories WHERE name = ?", ("Supplemental Lighting",))
    category_result = cursor.fetchone()
    if not category_result:
        print("ERROR: Category 'Supplemental Lighting' not found!")
        return
    
    category_id = category_result[0]
    print(f"Category ID found: {category_id}")
    
    # Define lighting systems with verified pricing from research
    lighting_systems = [
        {
            'item_id': 'GAVITA_RS1900E_LOW',
            'name': 'Gavita RS 1900e LED System (Low Cost Range)',
            'specifications': '{"manufacturer": "Gavita", "model": "RS 1900e LED", "output": "1900 μmol/s", "efficiency": "3.0 μmol/J", "coverage": "16-25 sq ft", "features": ["Lightweight", "Foldable 6-bar design", "DLC listed"], "fixtures_needed_5000sf": 200}',
            'notes': 'Verified pricing from LED Grow Lights Depot and Growers House January 9, 2025. Lower end of confirmed retail pricing range.',
            'unit_cost': 800.00,
            'unit': 'per_fixture',
            'total_5000sqft': 160000,  # 200 fixtures at $800 each
            'confidence': 'HIGH'
        },
        {
            'item_id': 'GAVITA_RS1900E_HIGH',
            'name': 'Gavita RS 1900e LED System (High Cost Range)',
            'specifications': '{"manufacturer": "Gavita", "model": "RS 1900e LED", "output": "1900 μmol/s", "efficiency": "3.0 μmol/J", "coverage": "16-25 sq ft", "features": ["Lightweight", "Foldable 6-bar design", "DLC listed"], "fixtures_needed_5000sf": 313}',
            'notes': 'Verified pricing from LED Grow Lights Depot and Growers House January 9, 2025. Higher end of confirmed retail pricing with maximum fixture count.',
            'unit_cost': 2024.00,
            'unit': 'per_fixture',
            'total_5000sqft': 633512,  # 313 fixtures at $2024 each
            'confidence': 'HIGH'
        },
        {
            'item_id': 'GAVITA_PRO_1700E_ML',
            'name': 'Gavita Pro 1700e LED ML System',
            'specifications': '{"manufacturer": "Gavita", "model": "Pro 1700e LED ML", "power": "645W", "output": "1700 μmol/s", "efficiency": "2.6 μmol/J", "application": "Direct HPS replacement", "suitable_for": "Commercial greenhouse"}',
            'notes': 'Alternative Gavita model from website research January 9, 2025. Lower efficiency but proven commercial system.',
            'unit_cost': 1200.00,  # Estimated based on model positioning
            'unit': 'per_fixture',
            'total_5000sqft': 300000,  # 250 fixtures estimated
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'CLW_MEGADRIVE_SYSTEM',
            'name': 'California LightWorks MegaDrive LED System',
            'specifications': '{"manufacturer": "California LightWorks", "system": "MegaDrive", "features": ["30% lower fixture costs", "80% lower installation costs", "50% lower operating costs vs HPS"], "power_options": ["3kW units", "10kW centralized units"], "support": "Up to 80 fixtures per unit"}',
            'notes': 'Research from AgriTechTomorrow case study January 9, 2025. Proven in 70,000 sq ft Nipomo AG installation. Custom quotes required.',
            'unit_cost': 350000.00,  # Complete system estimate
            'unit': 'per_system',
            'total_5000sqft': 350000,
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'FLUENCE_COMMERCIAL_SYSTEM',
            'name': 'Fluence Bioengineering Commercial LED System',
            'specifications': '{"manufacturer": "Fluence Bioengineering", "series": ["VYPR 4", "RAPTR 2", "SPYDR"], "features": ["Tunable spectra", "Maximum versatility", "OSRAM LED chips"], "proven_scale": "120,000+ sq ft installations", "manufacturing": "USA"}',
            'notes': 'Research from BusinessWire case study January 9, 2025. Proven at Holistic Industries scale. Custom quotes required for commercial installations.',
            'unit_cost': 400000.00,  # Complete system estimate
            'unit': 'per_system',
            'total_5000sqft': 400000,
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'VANILLA_60KW_POWER_SYSTEM',
            'name': 'Vanilla-Optimized 60kW LED Power System',
            'specifications': '{"power_density": "12 watts per sq ft", "total_power": "60,000 watts (60 kW)", "target_ppfd": "40-80 μmol/m²/s", "efficiency_target": ">2.1 μmol/J", "coverage": "5000 sq ft", "power_savings": "60% vs high-light crops"}',
            'notes': 'System sizing based on vanilla orchid low-light requirements. January 9, 2025 research from LED Grow Lights Depot specifications.',
            'unit_cost': 250000.00,  # Mid-range complete system
            'unit': 'per_system',
            'total_5000sqft': 250000,
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'LED_INSTALLATION_TRADITIONAL',
            'name': 'Traditional LED Installation (60kW System)',
            'specifications': '{"installation_type": "Traditional", "power_capacity": "60 kW additional load", "includes": ["Mounting systems", "Wiring and controls", "Distribution panels", "Integration with greenhouse systems"]}',
            'notes': 'Installation cost estimate for 60kW LED system January 9, 2025. Includes electrical infrastructure upgrades.',
            'unit_cost': 60000.00,  # Mid-range of $40k-80k estimate
            'unit': 'per_installation',
            'total_5000sqft': 60000,
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'LED_INSTALLATION_MEGADRIVE',
            'name': 'MegaDrive LED Installation (80% Cost Reduction)',
            'specifications': '{"installation_type": "MegaDrive System", "power_capacity": "60 kW", "cost_savings": "80% reduction vs traditional", "features": ["Centralized power units", "Reduced wiring complexity", "Simplified installation"]}',
            'notes': 'California LightWorks MegaDrive installation cost advantage from case study January 9, 2025. 80% installation cost reduction.',
            'unit_cost': 12000.00,  # 80% reduction of $60k
            'unit': 'per_installation',
            'total_5000sqft': 12000,
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'LIGHTING_CONTROL_BASIC',
            'name': 'Basic PAR Monitoring and Control System',
            'specifications': '{"components": ["PAR sensors", "Basic DLI monitoring", "Manual scheduling"], "features": ["Real-time PPFD measurement", "Daily light integral calculation"], "automation": "Basic"}',
            'notes': 'Essential control system for vanilla supplemental lighting January 9, 2025. Industry standard pricing estimate.',
            'unit_cost': 3500.00,  # Mid-range of $2k-5k
            'unit': 'per_system',
            'total_5000sqft': 3500,
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'LIGHTING_CONTROL_ADVANCED',
            'name': 'Advanced Environmental Integration Control System',
            'specifications': '{"components": ["PAR sensors", "Environmental integration", "Automated scheduling", "Spectrum control"], "features": ["Time-of-use optimization", "Greenhouse climate integration", "Automated DLI management"], "automation": "Full"}',
            'notes': 'Advanced control system with full greenhouse integration January 9, 2025. Commercial greenhouse control system pricing.',
            'unit_cost': 37500.00,  # Mid-range of $25k-50k
            'unit': 'per_system',
            'total_5000sqft': 37500,
            'confidence': 'MEDIUM'
        }
    ]
    
    # Clear existing entries to prevent duplicates
    cursor.execute("DELETE FROM cost_items WHERE category_id = ? AND (item_id LIKE 'GAVITA_%' OR item_id LIKE 'CLW_%' OR item_id LIKE 'FLUENCE_%' OR item_id LIKE 'VANILLA_%' OR item_id LIKE 'LED_%' OR item_id LIKE 'LIGHTING_%')", (category_id,))
    
    # Insert cost items and pricing
    for system in lighting_systems:
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
    print(f"\n✅ Total items in Supplemental Lighting category: {item_count}")
    
    conn.close()
    print("\n🎉 Task 2.6 Supplemental Lighting Systems database population completed successfully!")

if __name__ == "__main__":
    populate_lighting_systems()