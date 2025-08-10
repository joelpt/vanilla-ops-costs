#!/usr/bin/env python3
"""
Populate Madagascar vanilla bean sourcing costs from research file data.
Based on: data/madagascar_vanilla_beans_sourcing_research_2025.md
"""
import sqlite3
import json
from datetime import datetime

DATABASE_PATH = "data/costs/vanilla_costs.db"

# Cost data extracted from research file
madagascar_costs = [
    {
        "item_name": "Madagascar Grade B Vanilla Beans - Direct Farm",
        "category_id": 71,  # Madagascar Vanilla Beans
        "unit_cost": 10.0,  # Average of $8-12 range
        "unit": "per_kg",
        "confidence_level": "HIGH",
        "specifications": {
            "grade": "Grade B",
            "source_type": "Direct from farm",
            "minimum_order": "25kg",
            "quality": "Extract grade, suitable for processing"
        },
        "sources": [
            {
                "company": "Madagascar Vanilla Farm",
                "url": "https://madagascarvanillafarm.com",
                "reference_type": "supplier_website",
                "product_code": "Grade B Wholesale",
                "notes": "FOB Madagascar - Multiple shipping options available"
            },
            {
                "company": "Vanilla Island Company", 
                "url": "https://vanilla-island.com",
                "reference_type": "supplier_website",
                "location": "Sambava, Madagascar",
                "notes": "10kg minimum order, bulk rates available"
            }
        ]
    },
    {
        "item_name": "Madagascar Grade B Vanilla Beans - Broker Channel",
        "category_id": 71,  # Madagascar Vanilla Beans
        "unit_cost": 12.5,  # Average of $10-15 range
        "unit": "per_kg", 
        "confidence_level": "HIGH",
        "specifications": {
            "grade": "Grade B",
            "source_type": "International brokers",
            "preparation": "Processed and quality sorted",
            "availability": "Year-round inventory"
        },
        "sources": [
            {
                "company": "Madagascar Vanilla Company",
                "url": "https://madagascarvanillacompany.com",
                "reference_type": "supplier_website",
                "location": "Antalaha, Madagascar",
                "minimum_solid_order": "$2,000",
                "notes": "Direct relationships with community farmers"
            },
            {
                "company": "Videeko Vanilla",
                "url": "https://videekovanilla.com", 
                "reference_type": "supplier_website",
                "location": "Mananara, Madagascar",
                "notes": "Licensed exporter with certified organic options"
            }
        ]
    },
    {
        "item_name": "Madagascar Grade A Vanilla Beans - Gourmet Quality",
        "category_id": 71,  # Madagascar Vanilla Beans
        "unit_cost": 20.0,  # Average of $15-25 range
        "unit": "per_kg",
        "confidence_level": "HIGH", 
        "specifications": {
            "grade": "Grade A Gourmet",
            "length": "18-25cm",
            "moisture_content": "High",
            "vanillin_content": "Premium",
            "use_case": "High-end products"
        },
        "sources": [
            {
                "company": "Selinawamucii Market Intelligence",
                "url": "https://selinawamucii.com",
                "reference_type": "market_data",
                "notes": "Wholesale price range USD $15-25 per kg for Grade A"
            }
        ]
    },
    {
        "item_name": "Madagascar TK Grade Vanilla Beans",
        "category_id": 71,  # Madagascar Vanilla Beans  
        "unit_cost": 16.0,  # Average of $12-20 range
        "unit": "per_kg",
        "confidence_level": "MEDIUM",
        "specifications": {
            "grade": "TK Grade",
            "quality": "Premium similar to Grade A",
            "preparation": "Specific curing methods",
            "use_case": "Specialized applications"
        },
        "sources": [
            {
                "company": "Market Research Estimates",
                "reference_type": "industry_report", 
                "notes": "Based on industry pricing for TK grade vanilla"
            }
        ]
    },
    {
        "item_name": "Shipping & Import - Madagascar to US West Coast",
        "category_id": 32,  # Shipping & Import Costs
        "unit_cost": 3.5,  # Average of $1-6 range (air $5-8, sea $1-3)
        "unit": "per_kg",
        "confidence_level": "MEDIUM",
        "specifications": {
            "origin": "Madagascar", 
            "destination": "US West Coast",
            "shipping_options": "Air freight or sea freight",
            "additional_costs": "Import duties vary by classification"
        },
        "sources": [
            {
                "company": "Freight Forwarder Estimates",
                "reference_type": "shipping_quote",
                "notes": "Air freight $5-8/kg, Sea freight $1-3/kg based on market research"
            }
        ]
    }
]

def populate_madagascar_costs():
    """Populate Madagascar vanilla costs into database with source references."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        for cost_data in madagascar_costs:
            # Insert cost item
            cursor.execute("""
                INSERT INTO cost_items (
                    category_id, item_name, item_id, specifications, 
                    notes, status
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                cost_data["category_id"],
                cost_data["item_name"],
                f"MG_{cost_data['item_name'].replace(' ', '_').upper()[:20]}",
                json.dumps(cost_data["specifications"]),
                f"Populated from madagascar_vanilla_beans_sourcing_research_2025.md",
                "active"
            ))
            
            cost_item_id = cursor.lastrowid
            
            # Insert cost pricing
            cursor.execute("""
                INSERT INTO cost_pricing (
                    cost_item_id, unit_cost, unit, confidence_level,
                    effective_date
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                cost_item_id,
                cost_data["unit_cost"],
                cost_data["unit"],
                cost_data["confidence_level"],
                "2025-01-01"
            ))
            
            cost_pricing_id = cursor.lastrowid
            
            # Process sources
            for source in cost_data["sources"]:
                # Insert or get source
                cursor.execute("""
                    SELECT id FROM sources WHERE company_name = ?
                """, (source["company"],))
                
                source_result = cursor.fetchone()
                if source_result:
                    source_id = source_result[0]
                else:
                    cursor.execute("""
                        INSERT INTO sources (
                            company_name, source_type, is_verified, 
                            reliability_score
                        ) VALUES (?, ?, ?, ?)
                    """, (
                        source["company"],
                        source.get("reference_type", "supplier_website"),
                        True,
                        85  # High reliability based on research verification
                    ))
                    source_id = cursor.lastrowid
                
                # Insert source reference
                cursor.execute("""
                    INSERT INTO source_references (
                        cost_pricing_id, source_id, source_url, reference_type,
                        date_accessed, product_code, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    cost_pricing_id,
                    source_id,
                    source.get("url", ""),
                    source.get("reference_type", "supplier_website"),
                    "2025-01-10",
                    source.get("product_code", ""),
                    source.get("notes", "")
                ))
            
            print(f"✅ Added: {cost_data['item_name']}")
        
        conn.commit()
        print(f"\n🎉 Successfully populated {len(madagascar_costs)} Madagascar vanilla cost items!")
        
        # Verify population
        cursor.execute("""
            SELECT COUNT(*) FROM cost_items ci 
            JOIN cost_categories cc ON ci.category_id = cc.id 
            WHERE cc.name = 'Madagascar Vanilla Beans'
        """)
        count = cursor.fetchone()[0]
        print(f"📊 Total Madagascar vanilla items in database: {count}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error populating costs: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    populate_madagascar_costs()