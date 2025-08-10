#!/usr/bin/env python3
"""
Database population script for Task 2.15: Extraction Facility Infrastructure Requirements
Based on comprehensive research in vanilla_extraction_facility_infrastructure_2025.md

This script populates the database with verified infrastructure cost categories from the research document,
including construction costs, regulatory requirements, and utility infrastructure.
"""

import sqlite3
import json
from datetime import datetime
import os

def get_database_path():
    """Get the database path, trying both possible locations."""
    possible_paths = [
        '/Users/joelthor/code/vanilla-ops-costs/data/costs/vanilla_costs.db',
        '/Users/joelthor/code/vanilla-ops-costs/data/vanilla_costs.db'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Default to the costs directory
    return possible_paths[0]

def populate_extraction_infrastructure():
    """Populate database with comprehensive extraction facility infrastructure cost data."""
    
    # Infrastructure systems based on research document
    infrastructure_systems = [
        {
            'item_id': 'EXTRACTION_FACILITY_SMALL_2500SQFT',
            'name': 'Small-Scale Extraction Facility Infrastructure (2,500 sq ft)',
            'specifications': json.dumps({
                "facility_size": "2,500 sq ft",
                "operation_type": "Small-scale vanilla extraction facility",
                "construction_cost_base": "$180/sq ft × 2,500 sq ft = $450,000",
                "food_grade_modifications": "$25,000-50,000 additional",
                "electrical_upgrades": "$30,000-60,000 (explosion-proof systems)",
                "mechanical_systems": "$40,000-80,000 (specialized HVAC)",
                "fire_protection": "$15,000-30,000 (sprinklers and suppression)",
                "total_construction": "$560,000-670,000",
                "permits_soft_costs": "$70,000-120,000",
                "total_development": "$630,000-790,000"
            }),
            'unit_cost': 710000.00,  # Mid-range estimate
            'unit': 'per_facility',
            'notes': 'Small-scale vanilla extraction facility with FDA food-grade construction, explosion-proof electrical, and specialized ventilation.',
            'confidence': 'MEDIUM'  # Based on regional construction cost verification
        },
        {
            'item_id': 'EXTRACTION_FACILITY_MEDIUM_5000SQFT',
            'name': 'Medium-Scale Extraction Facility Infrastructure (5,000 sq ft)',
            'specifications': json.dumps({
                "facility_size": "5,000 sq ft",
                "operation_type": "Medium-scale vanilla extraction facility",
                "construction_cost_base": "$200/sq ft × 5,000 sq ft = $1,000,000",
                "food_grade_systems": "$75,000-125,000",
                "electrical_infrastructure": "$80,000-150,000",
                "mechanical_systems": "$100,000-200,000",
                "fire_protection": "$40,000-75,000",
                "process_integration": "$50,000-100,000",
                "quality_control_lab": "$25,000-50,000",
                "automation_systems": "$30,000-75,000",
                "total_development": "$1,400,000-1,775,000"
            }),
            'unit_cost': 1587500.00,  # Mid-range estimate
            'unit': 'per_facility',
            'notes': 'Medium-scale facility with enhanced systems, quality control lab, and automation capabilities.',
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'EXTRACTION_FACILITY_LARGE_9000SQFT',
            'name': 'Large-Scale Extraction Facility Infrastructure (9,000 sq ft)',
            'specifications': json.dumps({
                "facility_size": "9,000 sq ft",
                "operation_type": "Large-scale integrated vanilla extraction facility",
                "construction_cost_base": "$220/sq ft × 9,000 sq ft = $1,980,000",
                "specialized_systems": "$200,000-350,000",
                "electrical_infrastructure": "$150,000-250,000",
                "mechanical_systems": "$200,000-350,000",
                "fire_protection": "$75,000-125,000",
                "automated_systems": "$100,000-200,000",
                "environmental_controls": "$75,000-150,000",
                "laboratory_facilities": "$50,000-100,000",
                "total_development": "$2,830,000-3,505,000"
            }),
            'unit_cost': 3167500.00,  # Mid-range estimate
            'unit': 'per_facility',
            'notes': 'Large-scale facility with advanced automation, environmental controls, and comprehensive laboratory facilities.',
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'FDA_FOOD_FACILITY_REGISTRATION',
            'name': 'FDA Food Facility Registration and Compliance Setup',
            'specifications': json.dumps({
                "requirement": "FDA food facility registration required",
                "registration_type": "Food processing facility under Bioterrorism Act",
                "biennial_renewal": "Required every 2 years",
                "inspection_readiness": "Facility must be ready for FDA inspection",
                "documentation": "Complete documentation of all processes required",
                "haccp_program": "Hazard Analysis Critical Control Points program required",
                "cgmp_compliance": "Current Good Manufacturing Practices compliance",
                "estimated_setup_cost": "Initial compliance setup and documentation"
            }),
            'unit_cost': 15000.00,
            'unit': 'per_facility',
            'notes': 'FDA registration is required for food processing facilities. Includes initial compliance setup, documentation, and HACCP program development.',
            'confidence': 'HIGH'  # FDA requirements verified
        },
        {
            'item_id': 'EXPLOSION_PROOF_ELECTRICAL_SYSTEMS',
            'name': 'Explosion-Proof Electrical Systems for Ethanol Processing',
            'specifications': json.dumps({
                "classification": "Class I, Division 1 or 2 hazardous location classification",
                "equipment": "Explosion-proof motors, switches, and control panels",
                "wiring_methods": "Rigid metal conduit with explosion-proof fittings",
                "grounding": "Enhanced grounding system for static electricity dissipation",
                "safety_systems": "Emergency stops, fire detection, gas detection, emergency lighting",
                "electrical_load": "100-335 kW typical connected load",
                "service_requirements": "480V, 3-phase service with 400-800 amp capacity",
                "cost_range": "$30,000-250,000 depending on facility size"
            }),
            'unit_cost': 140000.00,  # Mid-range estimate
            'unit': 'per_system',
            'notes': 'Specialized electrical systems required for safe ethanol processing operations with explosion-proof equipment.',
            'confidence': 'HIGH'
        },
        {
            'item_id': 'SPECIALIZED_HVAC_ETHANOL_PROCESSING',
            'name': 'Specialized HVAC Systems for Ethanol Vapor Management',
            'specifications': json.dumps({
                "temperature_control": "68-75°F for optimal extraction conditions",
                "humidity_control": "45-60% RH to prevent moisture issues",
                "air_changes": "6-12 air changes per hour minimum",
                "filtration": "HEPA filtration for contamination control",
                "ethanol_vapor_management": "Dedicated exhaust for ethanol processing areas",
                "explosion_proof_fans": "Spark-proof ventilation equipment",
                "air_monitoring": "Continuous ethanol vapor concentration monitoring",
                "emergency_ventilation": "High-volume exhaust for emergency situations",
                "cost_range": "$40,000-350,000 depending on facility size"
            }),
            'unit_cost': 195000.00,  # Mid-range estimate
            'unit': 'per_system',
            'notes': 'Comprehensive HVAC system designed for safe ethanol processing with specialized vapor management capabilities.',
            'confidence': 'HIGH'
        },
        {
            'item_id': 'FIRE_SUPPRESSION_ETHANOL_FACILITY',
            'name': 'Fire Suppression System for Ethanol Processing Facility',
            'specifications': json.dumps({
                "automatic_sprinklers": "NFPA 13 commercial sprinkler system throughout facility",
                "special_hazards": "Special suppression for ethanol storage areas",
                "foam_systems": "Alcohol-resistant foam systems for ethanol fires",
                "portable_extinguishers": "Class B fire extinguishers strategically located",
                "monitoring": "Fire alarm monitoring and central station reporting",
                "fire_rated_separation": "Fire-rated separation between ethanol and other areas",
                "water_supply": "Adequate municipal water pressure and flow",
                "cost_range": "$15,000-125,000 depending on facility size"
            }),
            'unit_cost': 70000.00,  # Mid-range estimate
            'unit': 'per_system',
            'notes': 'Comprehensive fire suppression system designed specifically for ethanol processing hazards.',
            'confidence': 'HIGH'
        },
        {
            'item_id': 'UTILITY_CONNECTIONS_EXTRACTION_FACILITY',
            'name': 'Utility Connections and Infrastructure for Extraction Facility',
            'specifications': json.dumps({
                "electrical_service": "$15,000-100,000 depending on service requirements",
                "transformer_installation": "Utility-owned transformer requirements",
                "water_service": "$5,000-15,000 connection fees plus $8,000-25,000 development charges",
                "fire_service": "$10,000-25,000 for fire sprinkler service",
                "sewer_connection": "$3,000-10,000 connection fees plus $5,000-20,000 capacity charges",
                "natural_gas_service": "$2,000-8,000 for standard service (optional)",
                "backflow_prevention": "$2,000-5,000 for required devices",
                "total_utility_costs": "$45,000-208,000 depending on facility requirements"
            }),
            'unit_cost': 126500.00,  # Mid-range estimate
            'unit': 'per_facility',
            'notes': 'Complete utility infrastructure including electrical service, water, sewer, and fire protection connections.',
            'confidence': 'MEDIUM'
        },
        {
            'item_id': 'FOOD_GRADE_CONSTRUCTION_SPECIFICATIONS',
            'name': 'FDA Food-Grade Construction Materials and Finishes',
            'specifications': json.dumps({
                "wall_surfaces": "Smooth, non-porous surfaces (stainless steel panels or FDA-approved coatings)",
                "flooring": "Seamless epoxy or urethane floors with integral cove base",
                "ceiling": "Washable surface, minimum 8-foot clearance over production areas",
                "drainage": "Floor drains with adequate slope (1/4 inch per foot minimum)",
                "lighting": "Shatterproof fixtures with minimum 50 foot-candles in production areas",
                "structural_requirements": "150-200 lbs/sq ft minimum floor loading, 14-18 feet ceiling height",
                "cost_premium": "$25,000-350,000 above standard construction depending on facility size"
            }),
            'unit_cost': 187500.00,  # Mid-range estimate
            'unit': 'per_facility',
            'notes': 'FDA-compliant food-grade construction materials and finishes required for vanilla processing facility.',
            'confidence': 'HIGH'
        },
        {
            'item_id': 'REGULATORY_COMPLIANCE_PERMITS_SETUP',
            'name': 'Regulatory Compliance and Permitting Package',
            'specifications': json.dumps({
                "building_permits": "$15,000-25,000",
                "design_professional": "$40,000-70,000 (architect/engineer)",
                "regulatory_consulting": "$15,000-25,000",
                "fda_registration": "$500/year facility registration",
                "osha_compliance": "Process Safety Management if ethanol >10,000 lbs",
                "environmental_permits": "Air discharge permits for ethanol vapors",
                "hazardous_waste": "EPA hazardous waste generator registration",
                "fire_department": "Fire department pre-planning and access",
                "health_department": "Food processing facility approval"
            }),
            'unit_cost': 85000.00,  # Mid-range for permits and consulting
            'unit': 'per_facility',
            'notes': 'Comprehensive regulatory compliance package including permits, professional services, and ongoing compliance requirements.',
            'confidence': 'MEDIUM'
        }
    ]
    
    db_path = get_database_path()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get category ID for Infrastructure Costs (under Grow & Produce revenue stream)
        cursor.execute('SELECT id FROM cost_categories WHERE name = ? AND revenue_stream_id = 1', ('Infrastructure Costs',))
        category_result = cursor.fetchone()
        
        if not category_result:
            print("Infrastructure Costs category not found. Creating it...")
            cursor.execute('''
                INSERT INTO cost_categories (revenue_stream_id, name, code, description, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            ''', (1, 'Infrastructure Costs', 'INFRASTRUCTURE_COSTS', 'Facility construction, regulatory compliance, and infrastructure requirements for vanilla extraction operations'))
            category_id = cursor.lastrowid
        else:
            category_id = category_result[0]
        
        items_added = 0
        items_updated = 0
        
        for system in infrastructure_systems:
            # Check if item already exists
            cursor.execute('SELECT id FROM cost_items WHERE item_id = ?', (system['item_id'],))
            existing_item = cursor.fetchone()
            
            if existing_item:
                # Update existing item
                cursor.execute('''
                    UPDATE cost_items 
                    SET item_name = ?, specifications = ?, notes = ?
                    WHERE item_id = ?
                ''', (system['name'], system['specifications'], system['notes'], system['item_id']))
                
                cost_item_db_id = existing_item[0]
                items_updated += 1
                print(f"Updated existing item: {system['name']}")
            else:
                # Insert new item
                cursor.execute('''
                    INSERT INTO cost_items (item_id, item_name, category_id, specifications, notes, status, created_at)
                    VALUES (?, ?, ?, ?, ?, 'active', datetime('now'))
                ''', (system['item_id'], system['name'], category_id, system['specifications'], system['notes']))
                
                cost_item_db_id = cursor.lastrowid
                items_added += 1
                print(f"Added new item: {system['name']}")
            
            # Handle pricing - check if pricing already exists
            cursor.execute('SELECT id FROM cost_pricing WHERE cost_item_id = ?', (cost_item_db_id,))
            existing_pricing = cursor.fetchone()
            
            if existing_pricing:
                # Update existing pricing
                cursor.execute('''
                    UPDATE cost_pricing 
                    SET unit_cost = ?, unit = ?, confidence_level = ?, effective_date = ?
                    WHERE cost_item_id = ?
                ''', (system['unit_cost'], system['unit'], system['confidence'], '2025-01-09', cost_item_db_id))
                print(f"  Updated pricing: ${system['unit_cost']:,.2f} {system['unit']}")
            else:
                # Insert new pricing
                cursor.execute('''
                    INSERT INTO cost_pricing (cost_item_id, unit_cost, unit, effective_date, confidence_level, created_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'))
                ''', (cost_item_db_id, system['unit_cost'], system['unit'], '2025-01-09', system['confidence']))
                print(f"  Added pricing: ${system['unit_cost']:,.2f} {system['unit']}")
        
        # Add source reference
        cursor.execute('''
            INSERT OR REPLACE INTO sources (
                company_name, company_type, website_url, tier, created_at
            ) VALUES (?, ?, ?, ?, datetime('now'))
        ''', (
            'Vanilla Extraction Facility Infrastructure Research Document 2025',
            'research_document',
            'vanilla_extraction_facility_infrastructure_2025.md',
            1
        ))
        
        conn.commit()
        print(f"\n✅ Successfully populated extraction facility infrastructure database!")
        print(f"   Items added: {items_added}")
        print(f"   Items updated: {items_updated}")
        print(f"   Total infrastructure categories: {len(infrastructure_systems)}")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    populate_extraction_infrastructure()