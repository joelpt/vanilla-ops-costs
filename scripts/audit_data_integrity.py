#!/usr/bin/env python3
"""
Data Integrity Audit Script for Terra35 Vanilla Operations Cost Analysis

This script comprehensively audits:
1. Duplication between .md files and database
2. Missing data in either source
3. Completeness and thoroughness for each Milestone 2 task
4. Data quality and requirements compliance

CRITICAL: Ensures database is single source of truth with no redundancy
"""

import sqlite3
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataIntegrityAuditor:
    def __init__(self, db_path: str = "data/costs/vanilla_costs.db"):
        self.db_path = db_path
        self.conn = None
        self.data_dir = Path("data")
        
        # Price patterns for detecting duplicated cost data in .md files
        self.price_patterns = [
            r'\$([0-9,]+(?:\.[0-9]{2})?)',  # $123.45 or $1,234.56
            r'([0-9,]+(?:\.[0-9]{2})?)\s*dollars?',  # 123 dollars
            r'Cost:\s*\$([0-9,]+(?:\.[0-9]{2})?)',   # Cost: $123.45
            r'Price:\s*\$([0-9,]+(?:\.[0-9]{2})?)',  # Price: $123.45
            r'Total:\s*\$([0-9,]+(?:\.[0-9]{2})?)',  # Total: $123.45
            r'Range:\s*\$([0-9,]+(?:\.[0-9]{2})?)\s*-\s*\$([0-9,]+(?:\.[0-9]{2})?)',  # Range: $100 - $200
        ]
        
        # URL patterns for source detection
        self.url_pattern = r'https?://[^\s\)]+(?:\.[a-zA-Z]{2,})'
        
        # Milestone 2 task mapping
        self.milestone_2_tasks = {
            "2.1": "greenhouse_structures_commercial_research_2025.md",
            "2.2": "greenhouse_benching_research_2025.md", 
            "2.3": "vanilla_trellis_systems_research_2025.md",
            "2.4": "irrigation_fertigation_systems_research_2025.md",
            "2.5": "greenhouse_climate_control_systems_research_2025.md",
            "2.6": "vanilla_supplemental_lighting_research_2025.md",
            "2.7": "vanilla_curing_chamber_systems_research_2025.md",
            "2.8": "vanilla_dehydration_equipment_flavor_development_2025.md",
            "2.9": "temperature_humidity_control_curing_systems_2025.md",
            "2.10": "vanilla_packaging_equipment_research_2025.md",
            "2.11": "vanilla_extraction_equipment_ethanol_water_2025.md",
            "2.12": "vanilla_distillation_concentration_equipment_2025.md",
            "2.13": "vanilla_processing_labor_operational_costs_2025.md",
            "2.14": "vanilla_energy_costs_greenhouse_processing_2025.md",
            "2.15": "vanilla_extraction_facility_infrastructure_2025.md",
            "2.16": "vanilla_water_consumption_costs_oregon_city_2025.md",
            "2.17": "vanilla_fertilizer_nutrient_programs_2025.md",
            "2.18": "vanilla_growing_media_substrate_costs_2025.md",
            "2.19": "vanilla_contractor_labor_costs_analysis_2025.md",
            "2.21": "water_recycling_systems_vanilla_operations_2025.md",
            "2.22": "waste_to_revenue_processing_equipment_2025.md",
            "2.23": "organic_waste_recycling_partnerships_2025.md",
            "2.24": "oregon_city_renewable_energy_premium_costs_2025.md",
            "2.25": "owned_vs_purchased_renewable_energy_roi_2025.md",
            "2.28": "vanilla_pollination_tools_supplies_2025.md",
            "2.29": "vanilla_quality_testing_equipment_2025.md"
        }
        
    def connect_database(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            logger.info(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def get_database_costs(self) -> Dict[str, List[Dict]]:
        """Get all cost data from database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                ci.item_name,
                ci.item_id,
                cp.unit_cost,
                cp.unit,
                cp.confidence_level,
                s.company_name,
                s.website_url,
                ci.notes
            FROM cost_items ci 
            LEFT JOIN cost_pricing cp ON ci.id = cp.cost_item_id 
            LEFT JOIN source_references sr ON cp.id = sr.cost_pricing_id
            LEFT JOIN sources s ON sr.source_id = s.id
        """)
        
        results = cursor.fetchall()
        database_costs = {}
        
        for row in results:
            item_name, item_id, unit_cost, unit, confidence, company, url, notes = row
            
            # Extract source filename from notes
            source_file = "unknown"
            if notes and ".md" in notes:
                match = re.search(r'([a-zA-Z0-9_]+_2025\.md)', notes)
                if match:
                    source_file = match.group(1)
            
            if source_file not in database_costs:
                database_costs[source_file] = []
            
            database_costs[source_file].append({
                'item_name': item_name,
                'item_id': item_id,
                'unit_cost': unit_cost,
                'unit': unit,
                'confidence_level': confidence,
                'company_name': company,
                'website_url': url
            })
        
        return database_costs
    
    def extract_costs_from_md(self, filepath: Path) -> List[Dict]:
        """Extract cost figures from markdown file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")
            return []
        
        costs_found = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern in self.price_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    cost_value = match.group(1) if match.groups() else match.group(0)
                    costs_found.append({
                        'line_number': line_num,
                        'line_content': line.strip(),
                        'cost_value': cost_value,
                        'context': line.strip()[:100]
                    })
        
        return costs_found
    
    def extract_sources_from_md(self, filepath: Path) -> List[Dict]:
        """Extract source URLs from markdown file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return []
        
        sources_found = []
        urls = re.finditer(self.url_pattern, content)
        
        for match in urls:
            url = match.group(0)
            sources_found.append({
                'url': url,
                'context': content[max(0, match.start()-50):match.end()+50].strip()
            })
        
        return sources_found
    
    def audit_duplication(self) -> Dict[str, Dict]:
        """Audit for duplication between database and .md files"""
        logger.info("🔍 AUDITING FOR DUPLICATION")
        
        database_costs = self.get_database_costs()
        duplication_report = {}
        
        # Check each Milestone 2 task file
        for task_id, filename in self.milestone_2_tasks.items():
            filepath = self.data_dir / filename
            if not filepath.exists():
                logger.warning(f"File not found: {filename}")
                continue
            
            # Extract costs from .md file
            md_costs = self.extract_costs_from_md(filepath)
            
            # Get corresponding database costs
            db_costs = database_costs.get(filename, [])
            
            # Check for duplicated cost figures
            duplications = []
            for md_cost in md_costs:
                cost_val = float(md_cost['cost_value'].replace(',', '')) if md_cost['cost_value'].replace(',', '').replace('.', '').isdigit() else 0
                
                for db_cost in db_costs:
                    if db_cost['unit_cost'] and abs(float(db_cost['unit_cost']) - cost_val) < 0.01:
                        duplications.append({
                            'md_line': md_cost['line_number'],
                            'md_content': md_cost['context'],
                            'db_item': db_cost['item_name'],
                            'cost_value': cost_val
                        })
            
            duplication_report[task_id] = {
                'filename': filename,
                'md_costs_found': len(md_costs),
                'db_costs_found': len(db_costs),
                'duplications': duplications,
                'has_duplication': len(duplications) > 0
            }
        
        return duplication_report
    
    def audit_completeness(self) -> Dict[str, Dict]:
        """Audit completeness of each Milestone 2 task"""
        logger.info("📊 AUDITING COMPLETENESS")
        
        database_costs = self.get_database_costs()
        completeness_report = {}
        
        for task_id, filename in self.milestone_2_tasks.items():
            filepath = self.data_dir / filename
            if not filepath.exists():
                completeness_report[task_id] = {
                    'filename': filename,
                    'status': 'FILE_MISSING',
                    'db_items': 0,
                    'has_sources': False,
                    'completeness_score': 0
                }
                continue
            
            # Check database items
            db_costs = database_costs.get(filename, [])
            
            # Check for sources in .md file  
            md_sources = self.extract_sources_from_md(filepath)
            
            # Read file for research context
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                
                has_executive_summary = "executive summary" in content.lower()
                has_research_findings = len(content) > 1000  # Substantial research
                has_specifications = "specifications" in content.lower() or "features" in content.lower()
                
                completeness_score = 0
                if len(db_costs) > 0: completeness_score += 40  # Has database items
                if len(md_sources) > 0: completeness_score += 20  # Has sources
                if has_executive_summary: completeness_score += 15  # Has summary
                if has_research_findings: completeness_score += 15  # Substantial research
                if has_specifications: completeness_score += 10   # Technical details
                
                completeness_report[task_id] = {
                    'filename': filename,
                    'status': 'COMPLETE' if completeness_score >= 80 else 'INCOMPLETE',
                    'db_items': len(db_costs),
                    'md_sources': len(md_sources),
                    'has_executive_summary': has_executive_summary,
                    'has_research_findings': has_research_findings,
                    'has_specifications': has_specifications,
                    'completeness_score': completeness_score
                }
                
            except Exception as e:
                logger.error(f"Error analyzing {filename}: {e}")
                
        return completeness_report
    
    def audit_data_quality(self) -> Dict:
        """Audit data quality in database"""
        logger.info("🎯 AUDITING DATA QUALITY")
        
        cursor = self.conn.cursor()
        
        # Check for missing confidence levels
        cursor.execute("SELECT COUNT(*) FROM cost_pricing WHERE confidence_level IS NULL OR confidence_level = ''")
        missing_confidence = cursor.fetchone()[0]
        
        # Check for missing sources
        cursor.execute("""
            SELECT COUNT(*) FROM cost_items ci 
            LEFT JOIN source_references sr ON ci.id = sr.cost_item_id 
            WHERE sr.cost_item_id IS NULL
        """)
        missing_sources = cursor.fetchone()[0]
        
        # Check for unrealistic cost values
        cursor.execute("SELECT COUNT(*) FROM cost_pricing WHERE unit_cost <= 0")
        zero_costs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cost_pricing WHERE unit_cost > 1000000")
        extreme_costs = cursor.fetchone()[0]
        
        # Get total counts
        cursor.execute("SELECT COUNT(*) FROM cost_items")
        total_items = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sources")
        total_sources = cursor.fetchone()[0]
        
        return {
            'total_items': total_items,
            'total_sources': total_sources,
            'missing_confidence': missing_confidence,
            'missing_sources': missing_sources,
            'zero_costs': zero_costs,
            'extreme_costs': extreme_costs,
            'quality_score': max(0, 100 - (missing_confidence + missing_sources + zero_costs + extreme_costs) * 2)
        }
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive audit report"""
        logger.info("📋 GENERATING COMPREHENSIVE AUDIT REPORT")
        
        duplication_report = self.audit_duplication()
        completeness_report = self.audit_completeness()
        quality_report = self.audit_data_quality()
        
        # Summary statistics
        total_tasks = len(self.milestone_2_tasks)
        tasks_with_duplication = sum(1 for task in duplication_report.values() if task['has_duplication'])
        complete_tasks = sum(1 for task in completeness_report.values() if task.get('status') == 'COMPLETE')
        
        return {
            'summary': {
                'total_milestone_2_tasks': total_tasks,
                'tasks_with_duplication': tasks_with_duplication,
                'complete_tasks': complete_tasks,
                'completion_rate': f"{(complete_tasks/total_tasks)*100:.1f}%",
                'duplication_rate': f"{(tasks_with_duplication/total_tasks)*100:.1f}%",
                'overall_quality_score': quality_report['quality_score']
            },
            'duplication_audit': duplication_report,
            'completeness_audit': completeness_report,
            'data_quality_audit': quality_report
        }

def main():
    """Main execution function"""
    print("🔍 DATA INTEGRITY AUDIT - Terra35 Vanilla Operations")
    print("=" * 60)
    
    auditor = DataIntegrityAuditor()
    
    if not auditor.connect_database():
        print("❌ Failed to connect to database")
        return 1
    
    try:
        # Generate comprehensive report
        report = auditor.generate_comprehensive_report()
        
        print("\n📊 AUDIT SUMMARY:")
        print("-" * 40)
        summary = report['summary']
        print(f"📈 Overall Quality Score: {summary['overall_quality_score']}/100")
        print(f"✅ Complete Tasks: {summary['complete_tasks']}/{summary['total_milestone_2_tasks']} ({summary['completion_rate']})")
        print(f"🔄 Tasks with Duplication: {summary['tasks_with_duplication']}/{summary['total_milestone_2_tasks']} ({summary['duplication_rate']})")
        
        print(f"\n🎯 DATABASE STATUS:")
        quality = report['data_quality_audit']
        print(f"   Total Items: {quality['total_items']}")
        print(f"   Total Sources: {quality['total_sources']}")
        print(f"   Missing Confidence: {quality['missing_confidence']}")
        print(f"   Missing Sources: {quality['missing_sources']}")
        
        # Show critical duplication issues
        print(f"\n🚨 CRITICAL DUPLICATION ISSUES:")
        print("-" * 40)
        duplication_found = False
        for task_id, task_data in report['duplication_audit'].items():
            if task_data['has_duplication']:
                duplication_found = True
                print(f"❌ Task {task_id} ({task_data['filename']}): {len(task_data['duplications'])} duplicated cost figures")
                for dup in task_data['duplications'][:3]:  # Show first 3
                    print(f"   Line {dup['md_line']}: ${dup['cost_value']:.0f} (also in DB: {dup['db_item'][:50]}...)")
        
        if not duplication_found:
            print("✅ No critical duplication issues found")
        
        # Show incomplete tasks
        print(f"\n⚠️  INCOMPLETE TASKS:")
        print("-" * 40)
        incomplete_found = False
        for task_id, task_data in report['completeness_audit'].items():
            if task_data.get('status') != 'COMPLETE':
                incomplete_found = True
                score = task_data.get('completeness_score', 0)
                print(f"❌ Task {task_id} ({task_data['filename']}): {score}/100 completeness score")
                print(f"   DB Items: {task_data.get('db_items', 0)}, Sources: {task_data.get('md_sources', 0)}")
        
        if not incomplete_found:
            print("✅ All tasks appear complete")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        print("-" * 40)
        if summary['overall_quality_score'] >= 90:
            print("✅ EXCELLENT: Data integrity is very high")
        elif summary['overall_quality_score'] >= 75:
            print("⚠️  GOOD: Minor issues need attention")  
        elif summary['overall_quality_score'] >= 50:
            print("❌ POOR: Significant issues require immediate fix")
        else:
            print("🚨 CRITICAL: Major data integrity problems")
        
        # Save detailed report
        with open('data/audit_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print("\n📋 Detailed report saved to: data/audit_report.json")
        
    finally:
        auditor.conn.close()
    
    return 0

if __name__ == "__main__":
    exit(main())