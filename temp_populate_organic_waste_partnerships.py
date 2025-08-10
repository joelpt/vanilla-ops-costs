#!/usr/bin/env python3
"""
Database Population Script: Organic Waste Recycling Partnerships
Task 2.23 - Terra35 Vanilla Operations Cost Analysis

Populates database with organic waste recycling partnership costs
based on verified research document analysis.
"""

import sqlite3
import json
from datetime import datetime

def populate_organic_waste_partnerships(db_path="data/costs/vanilla_costs.db"):
    """
    Populate database with organic waste recycling partnership cost data.
    
    Based on research from data/organic_waste_recycling_partnerships_2025.md
    Including verified suppliers: Cedar Grove Composting, Recology Organics
    """
    
    # Organic waste recycling partnership categories
    partnerships_data = [
        {
            "name": "Cedar Grove Composting Partnership",
            "description": "Commercial organic waste composting services with Cedar Grove Composting (Maple Valley, WA). Accepts food scraps, yard trimmings, agricultural waste.",
            "unit": "per_cubic_yard",
            "confidence": "HIGH",
            "pricing": {
                "min": 35, "max": 50, "typical": 42
            },
            "notes": "VERIFIED supplier at https://cedar-grove.com with facilities in Seattle and Maple Valley, WA. Pricing includes collection service."
        },
        {
            "name": "Recology Organics Partnership", 
            "description": "Full-service organic waste collection and processing through Recology Organics (formerly CleanScapes). Comprehensive organic waste management with reporting.",
            "unit": "per_cubic_yard",
            "confidence": "HIGH", 
            "pricing": {
                "min": 45, "max": 65, "typical": 55
            },
            "notes": "VERIFIED supplier at https://www.recology.com with operations throughout Pacific Northwest. Includes detailed waste diversion reporting for compliance."
        },
        {
            "name": "Local Agricultural Exchange Program",
            "description": "Partnership with regional farms through Oregon Tilth Certified Organic Exchange and Clackamas County Farm Bureau for organic waste material sharing.",
            "unit": "per_year", 
            "confidence": "MEDIUM",
            "pricing": {
                "min": 0, "max": 500, "typical": 200
            },
            "notes": "Cost-neutral or small revenue programs through local agricultural networks. Requires organic certification for premium programs."
        },
        {
            "name": "Regional Composting Facility Partnership",
            "description": "Partnership with regional composting facilities for agricultural and food processing waste. Custom composting programs with soil amendment production.",
            "unit": "per_cubic_yard",
            "confidence": "MEDIUM",
            "pricing": {
                "min": 20, "max": 40, "typical": 30
            },
            "notes": "Pricing for clean agricultural waste. Multiple facilities in Oregon region. Potential closed-loop partnerships for soil amendments."
        },
        {
            "name": "Waste-to-Energy Partnership",
            "description": "Partnership with regional waste-to-energy facilities (Columbia Ridge, Republic Services) for organic waste processing into renewable energy.",
            "unit": "per_cubic_yard", 
            "confidence": "MEDIUM",
            "pricing": {
                "min": 15, "max": 50, "typical": 32
            },
            "notes": "Revenue sharing potential for premium feedstock. Transportation coordination required for cost-effective delivery to regional facilities."
        },
        {
            "name": "Organic Waste Disposal Cost Avoidance",
            "description": "Annual cost savings from avoiding traditional landfill disposal through organic waste partnership programs.",
            "unit": "per_year",
            "confidence": "HIGH", 
            "pricing": {
                "min": 3000, "max": 8000, "typical": 5500
            },
            "notes": "Estimated savings vs traditional waste disposal. Includes avoided tipping fees, reduced waste collection frequency, and compliance benefits."
        },
        {
            "name": "Premium Organic Waste Revenue Streams",
            "description": "Revenue from high-value organic waste streams (vanilla cuttings, bean processing waste) through specialized partnerships.",
            "unit": "per_year",
            "confidence": "MEDIUM",
            "pricing": {
                "min": 500, "max": 2500, "typical": 1500
            },
            "notes": "Vanilla cuttings at $0.10-0.25/lb for specialty applications. Requires development of premium markets and quality documentation."
        },
        {
            "name": "Regulatory Compliance Support Services",
            "description": "Partnership services for Oregon commercial waste diversion compliance including reporting, documentation, and audit support.",
            "unit": "per_year",
            "confidence": "HIGH",
            "pricing": {
                "min": 1000, "max": 3000, "typical": 2000
            },
            "notes": "Required for Oregon Recycling Modernization Act compliance. Includes quarterly reporting, certification programs, and audit support."
        },
        {
            "name": "Organic Waste Collection Service Partnership",
            "description": "Weekly organic waste collection service through established waste management partners with dedicated organics trucks.",
            "unit": "per_month",
            "confidence": "HIGH",
            "pricing": {
                "min": 150, "max": 350, "typical": 250
            },
            "notes": "Based on verified regional suppliers. Includes collection containers, scheduled pickup, and transportation to processing facilities."
        },
        {
            "name": "Sustainability Certification Support",
            "description": "Partnership support for environmental certifications (LEED, B-Corp, organic certification) through documented waste diversion programs.",
            "unit": "per_year", 
            "confidence": "MEDIUM",
            "pricing": {
                "min": 500, "max": 2000, "typical": 1250
            },
            "notes": "Support for corporate sustainability goals. Provides documentation for carbon credits, environmental stewardship positioning, and certification maintenance."
        }
    ]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get operational costs category ID  
    cursor.execute("SELECT id FROM cost_categories WHERE name = ?", ("Operational Costs",))
    operational_costs_result = cursor.fetchone()
    if not operational_costs_result:
        raise ValueError("Operational Costs category not found")
    
    operational_costs_category_id = operational_costs_result[0]
    
    # Clear existing organic waste partnership entries to avoid duplicates
    cursor.execute("DELETE FROM cost_items WHERE item_name LIKE '%Partnership%' OR item_name LIKE '%Exchange%' OR item_name LIKE '%Disposal Cost Avoidance%' OR item_name LIKE '%Revenue Stream%' OR item_name LIKE '%Compliance Support%' OR item_name LIKE '%Collection Service%' OR item_name LIKE '%Certification Support%'")
    
    items_added = 0
    
    # Insert partnership categories  
    for item in partnerships_data:
        item_id_code = f"OW_{items_added + 1:03d}"
        
        # Insert cost item
        cursor.execute('''
            INSERT INTO cost_items (
                item_id, item_name, category_id, specifications, notes
            ) VALUES (?, ?, ?, ?, ?)
        ''', (item_id_code, item['name'], operational_costs_category_id, 
              f'{{"unit": "{item["unit"]}", "confidence_level": "{item["confidence"]}"}}', 
              item['description']))
        
        cost_item_id = cursor.lastrowid
        
        # Insert pricing information (min, typical, max as separate entries)
        pricing_entries = [
            (item['pricing']['min'], 'minimum'),
            (item['pricing']['typical'], 'typical'),  
            (item['pricing']['max'], 'maximum')
        ]
        
        for cost, cost_type in pricing_entries:
            cursor.execute('''
                INSERT INTO cost_pricing (
                    cost_item_id, unit_cost, unit, currency, 
                    effective_date, volume_tier, confidence_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?)  
            ''', (cost_item_id, cost, item['unit'], 'USD', 
                  datetime.now().strftime('%Y-%m-%d'), cost_type, item['confidence']))
        
        items_added += 1
        print(f"Added {item['name']}: ${item['pricing']['min']:,}-{item['pricing']['max']:,} {item['unit']}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Successfully populated {items_added} organic waste recycling partnership categories")
    print("🔍 VERIFICATION NOTES:")
    print("  - Cedar Grove Composting: VERIFIED at https://cedar-grove.com")
    print("  - Recology Organics: VERIFIED at https://www.recology.com") 
    print("  - Research document source: data/organic_waste_recycling_partnerships_2025.md")
    return items_added

if __name__ == "__main__":
    populate_organic_waste_partnerships()