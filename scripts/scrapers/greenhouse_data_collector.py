#!/usr/bin/env python3
"""
Terra35 Vanilla Operations Cost Analysis - Greenhouse Data Collector

This script processes the manual research data collected from FarmTek, GrowSpan, and Stuppy
and formats it into our database structure for greenhouse infrastructure costs.

Usage:
    python scripts/scrapers/greenhouse_data_collector.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.scrapers.base_scraper import BaseScraper, ScrapedProduct

class GreenhouseDataCollector(BaseScraper):
    """Collector for manually researched greenhouse structure data"""
    
    def __init__(self):
        super().__init__(
            supplier_name="Manual_Research", 
            base_url="https://manual-research",
            cache_dir=str(project_root / 'data' / 'cache' / 'greenhouse_research')
        )
    
    def scrape_products(self) -> List[ScrapedProduct]:
        """Process manually collected greenhouse data into structured format"""
        products = []
        
        # FarmTek GrowSpan Series 750
        products.append(ScrapedProduct(
            item_id="FARMTEK_GS750_32X120",
            item_name="GrowSpan Series 750 Commercial Greenhouse (32'W x 120'L)",
            category="infrastructure",
            subcategory="greenhouse_structure",
            specifications={
                "dimensions": "32'W x 120'L x 16'-3/8\"H",
                "area_sqft": 3840,
                "frame_material": "Galvanized steel",
                "covering": "Inflatable double poly film",
                "endwalls": "8mm twin-wall polycarbonate", 
                "sidewall_height": "7'",
                "snow_load_psf": 25,
                "wind_speed_mph": 105,
                "weight_lbs": 15500,
                "door": "4'W x 7'H double greenhouse door",
                "suitable_for_vanilla": True,
                "climate_control_ready": True
            },
            unit_cost=29948.00,
            unit="complete_structure",
            source_url="https://www.farmtek.com/prod/growspan-series-750-commercial-greenhouse-non-blackout-32-w-x-120-l.html",
            product_code="S750G32120S",
            confidence_level="HIGH",
            notes="Excellent for vanilla - inflatable double poly and polycarbonate provide good insulation for 85°F/85% humidity requirements"
        ))
        
        # FarmTek GrowSpan Series 2000 
        products.append(ScrapedProduct(
            item_id="FARMTEK_GS2000_30X96",
            item_name="GrowSpan Series 2000 Commercial Greenhouse (30'W x 96'L)",
            category="infrastructure", 
            subcategory="greenhouse_structure",
            specifications={
                "dimensions": "30'W x 96'L x 18'2\"H",
                "area_sqft": 2880,
                "frame_material": "Galvanized steel",
                "covering": "8mm polycarbonate roof, sides, and end walls",
                "sidewall_height": "10'",
                "roof_design": "6/12 peak design",
                "weight_lbs": 10761,
                "anchoring": "Ground post system",
                "suitable_for_vanilla": True,
                "climate_control_ready": True,
                "expandable": True
            },
            unit_cost=36419.00,
            unit="complete_structure", 
            source_url="https://www.farmtek.com/prod/gs230096gp.html",
            product_code="GS230096GP",
            confidence_level="HIGH",
            notes="Excellent for vanilla - 8mm polycarbonate provides superior insulation, 10' sidewalls allow better air circulation"
        ))
        
        # FarmTek Premium Greenhouse Benching
        products.append(ScrapedProduct(
            item_id="FARMTEK_BENCH_6X8",
            item_name="Premium Stationary Greenhouse Bench (6'W x 8'L)",
            category="infrastructure",
            subcategory="benching_system", 
            specifications={
                "dimensions": "6'W x 8'L x 32\"H",
                "area_sqft": 48,
                "frame_material": "1.25\" 14-gauge galvanized structural steel",
                "surface": "Durable expanded metal top",
                "rails": "Extruded aluminum 4\" side rails", 
                "fasteners": "Stainless steel assembly",
                "weight_lbs": 300,
                "bench_height_inches": 32,
                "suitable_for_vanilla": True,
                "expandable": True,
                "made_in_usa": True
            },
            unit_cost=695.00,
            unit="per_bench",
            source_url="https://www.farmtek.com/prod/112416s6x08.html",
            product_code="112416S6X08", 
            confidence_level="HIGH",
            notes="Ideal for vanilla - 32\" height perfect for containers, connects for full greenhouse length"
        ))
        
        # GrowSpan Direct Series 2000 (manufacturer direct)
        products.append(ScrapedProduct(
            item_id="GROWSPAN_SERIES2000_CUSTOM",
            item_name="GrowSpan Series 2000 Commercial Greenhouse (Custom Configuration)",
            category="infrastructure",
            subcategory="greenhouse_structure",
            specifications={
                "design": "Gothic peak-roof polycarbonate",
                "frame_material": "Triple-galvanized steel",
                "covering": "8mm polycarbonate panels (impact resistant)",
                "sidewall_height": "10'",
                "roof_design": "6/12 peak design", 
                "connection": "Gutter-connected system",
                "expandable": True,
                "suitable_for_vanilla": True,
                "climate_control_ready": True,
                "manufacturer_direct": True,
                "custom_quote_required": True
            },
            unit_cost=None,  # Requires custom quote
            unit="custom_quote",
            source_url="https://www.growspan.com/structures/commercial-series/s-2000/",
            product_code="SERIES_2000",
            confidence_level="HIGH",
            notes="Direct manufacturer pricing available, excellent for vanilla with impact-resistant polycarbonate and precise climate control capability"
        ))
        
        # Stuppy CS3 A-Frame (premium US manufacturer)
        products.append(ScrapedProduct(
            item_id="STUPPY_CS3_CUSTOM",
            item_name="Stuppy CS3 A-Frame Greenhouse (Custom Configuration)",
            category="infrastructure", 
            subcategory="greenhouse_structure",
            specifications={
                "design": "Traditional A-frame",
                "frame_material": "4\" x 2\" - 11-gauge galvanized steel columns",
                "connection": "Gutter-connectable multi-bay",
                "max_width": "50 feet",
                "gutter_height": "16 feet available", 
                "sidewall_height": "10' standard (12' available)",
                "truss_spacing": "12' standard",
                "vents": "Single or double-roof motorized",
                "bench_compatible": True,
                "trolley_system_ready": True,
                "suitable_for_vanilla": True,
                "made_in_usa": True,
                "custom_quote_required": True
            },
            unit_cost=None,  # Requires custom quote
            unit="custom_quote",
            source_url="https://www.stuppy.com/cs3/",
            product_code="CS3_AFRAME", 
            confidence_level="HIGH",
            notes="Premium USA-manufactured option, excellent for vanilla with tall sidewalls and motorized vents for precise climate control"
        ))
        
        # Add cost per square foot calculations
        for product in products:
            if product.unit_cost and "area_sqft" in product.specifications:
                area = product.specifications["area_sqft"]
                cost_per_sqft = product.unit_cost / area
                product.specifications["cost_per_sqft"] = round(cost_per_sqft, 2)
        
        return products

def main():
    """Run the greenhouse data collection"""
    print("Terra35 Vanilla Operations - Greenhouse Data Collector")
    print("=" * 60)
    
    collector = GreenhouseDataCollector()
    
    # Run data collection session
    result = collector.run_scraping_session()
    
    print(f"\nCollection Summary:")
    print(f"Products collected: {len(result.products_scraped)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")
    
    if result.errors:
        print(f"\nErrors encountered:")
        for error in result.errors:
            print(f"  - {error}")
    
    if result.warnings:
        print(f"\nWarnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
    
    print(f"\nData collection completed successfully!")
    print(f"Session ID: {result.session_id}")
    print(f"Duration: {(result.end_time - result.start_time).total_seconds():.1f} seconds")

if __name__ == "__main__":
    main()