#!/usr/bin/env python3
"""
Terra35 Vanilla Operations Cost Analysis - Validation Runner

Command-line tool for running data validation on collected cost data.
Can validate individual items, batches, or entire database contents.

Usage:
    python scripts/validation/validation_runner.py --all
    python scripts/validation/validation_runner.py --item FARMTEK_GH123
    python scripts/validation/validation_runner.py --session session_20241230
    python scripts/validation/validation_runner.py --report validation_report.json
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.constants import STATUS_ACTIVE
from scripts.validation.data_validator import DataValidator, ValidationLevel

class ValidationRunner:
    """Command-line validation runner"""
    
    def __init__(self, db_path: Optional[str] = None, output_file: Optional[str] = None):
        self.project_root = project_root
        self.db_path = db_path or str(project_root / 'data' / 'costs' / 'vanilla_costs.db')
        self.output_file = output_file
        self.validator = DataValidator(self.db_path)
        
    def get_item_from_database(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve item data from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get cost item
                cursor = conn.execute("""
                    SELECT ci.*, cc.code as category_code, rs.code as revenue_stream
                    FROM cost_items ci
                    JOIN cost_categories cc ON ci.category_id = cc.id
                    JOIN revenue_streams rs ON cc.revenue_stream_id = rs.id
                    WHERE ci.item_id = ?
                """, (item_id,))
                
                item_row = cursor.fetchone()
                if not item_row:
                    return None
                
                # Build item data structure
                item_data = {
                    'item_id': item_row[1],  # item_id column
                    'item_name': item_row[2],  # item_name column
                    'category': item_row[9],  # category_code from join
                    'specifications': json.loads(item_row[3]) if item_row[3] else {},
                    'notes': item_row[4]
                }
                
                # Get pricing data
                cursor = conn.execute("""
                    SELECT unit_cost, unit, currency, effective_date, confidence_level,
                           total_cost_5000sqft
                    FROM cost_pricing 
                    WHERE cost_item_id = (SELECT id FROM cost_items WHERE item_id = ?)
                    ORDER BY effective_date DESC
                    LIMIT 1
                """, (item_id,))
                
                pricing_row = cursor.fetchone()
                if pricing_row:
                    item_data['pricing'] = {
                        'unit_cost': pricing_row[0],
                        'unit': pricing_row[1],
                        'currency': pricing_row[2],
                        'effective_date': pricing_row[3],
                        'confidence_level': pricing_row[4],
                        'total_cost_5000sqft': pricing_row[5]
                    }
                
                # Get source references
                cursor = conn.execute("""
                    SELECT sr.source_url, sr.product_code, sr.date_accessed, 
                           sr.reference_type, s.company_name, s.tier
                    FROM source_references sr
                    JOIN sources s ON sr.source_id = s.id
                    JOIN cost_pricing cp ON sr.cost_pricing_id = cp.id
                    WHERE cp.cost_item_id = (SELECT id FROM cost_items WHERE item_id = ?)
                """, (item_id,))
                
                sources = []
                for source_row in cursor.fetchall():
                    sources.append({
                        'source_url': source_row[0],
                        'product_code': source_row[1],
                        'date_accessed': source_row[2],
                        'reference_type': source_row[3],
                        'company_name': source_row[4],
                        'tier': source_row[5]
                    })
                
                item_data['sources'] = sources
                
                return item_data
                
        except sqlite3.Error as e:
            print(f"Database error retrieving item {item_id}: {e}")
            return None
    
    def get_all_items_from_database(self) -> List[Dict[str, Any]]:
        """Retrieve all items from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT item_id FROM cost_items WHERE status = ?", (STATUS_ACTIVE,))
                item_ids = [row[0] for row in cursor.fetchall()]
                
                items = []
                for item_id in item_ids:
                    item_data = self.get_item_from_database(item_id)
                    if item_data:
                        items.append(item_data)
                
                return items
                
        except sqlite3.Error as e:
            print(f"Database error retrieving all items: {e}")
            return []
    
    def get_items_by_session(self, session_name: str) -> List[Dict[str, Any]]:
        """Retrieve items from specific collection session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT DISTINCT ci.item_id
                    FROM collection_log cl
                    JOIN collection_sessions cs ON cl.session_id = cs.id
                    JOIN cost_items ci ON cl.cost_item_id = ci.id
                    WHERE cs.session_name = ? AND ci.status = ?
                """, (session_name, STATUS_ACTIVE))
                
                item_ids = [row[0] for row in cursor.fetchall()]
                
                items = []
                for item_id in item_ids:
                    item_data = self.get_item_from_database(item_id)
                    if item_data:
                        items.append(item_data)
                
                return items
                
        except sqlite3.Error as e:
            print(f"Database error retrieving session items: {e}")
            return []
    
    def validate_single_item(self, item_id: str) -> bool:
        """Validate a single item and print results"""
        print(f"Validating item: {item_id}")
        
        item_data = self.get_item_from_database(item_id)
        if not item_data:
            print(f"Error: Item {item_id} not found in database")
            return False
        
        summary = self.validator.validate_item(item_data)
        self.print_validation_summary(summary)
        
        if self.output_file:
            self.save_validation_report([summary])
        
        return summary.is_valid()
    
    def validate_all_items(self) -> bool:
        """Validate all items in database"""
        print("Validating all items in database...")
        
        items = self.get_all_items_from_database()
        if not items:
            print("No items found in database")
            return False
        
        print(f"Found {len(items)} items to validate")
        
        summaries = self.validator.validate_batch(items)
        self.print_batch_summary(summaries)
        
        if self.output_file:
            self.save_validation_report(summaries)
        
        # Return True if all items are valid
        return all(summary.is_valid() for summary in summaries)
    
    def validate_session_items(self, session_name: str) -> bool:
        """Validate items from specific session"""
        print(f"Validating items from session: {session_name}")
        
        items = self.get_items_by_session(session_name)
        if not items:
            print(f"No items found for session {session_name}")
            return False
        
        print(f"Found {len(items)} items in session")
        
        summaries = self.validator.validate_batch(items)
        self.print_batch_summary(summaries)
        
        if self.output_file:
            self.save_validation_report(summaries)
        
        return all(summary.is_valid() for summary in summaries)
    
    def print_validation_summary(self, summary):
        """Print detailed validation summary for single item"""
        print(f"\n{'='*60}")
        print(f"VALIDATION SUMMARY: {summary.item_id}")
        print(f"{'='*60}")
        print(f"Overall Score: {summary.overall_score:.2f}")
        print(f"Confidence Level: {summary.confidence_level}")
        print(f"Total Checks: {summary.total_checks}")
        print(f"✅ Passed: {summary.passed}")
        print(f"⚠️  Warnings: {summary.warnings}")
        print(f"❌ Errors: {summary.errors}")
        print(f"🚨 Critical: {summary.critical}")
        print(f"Valid: {'✅ YES' if summary.is_valid() else '❌ NO'}")
        
        if summary.results:
            print(f"\n{'VALIDATION DETAILS':-^60}")
            
            # Group by level
            by_level = {}
            for result in summary.results:
                level = result.level.value
                if level not in by_level:
                    by_level[level] = []
                by_level[level].append(result)
            
            # Print in order of severity
            for level in ['critical', 'error', 'warning', 'info']:
                if level in by_level:
                    level_emoji = {'critical': '🚨', 'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}
                    print(f"\n{level_emoji[level]} {level.upper()}:")
                    
                    for result in by_level[level]:
                        print(f"  • {result.message}")
                        if result.field:
                            print(f"    Field: {result.field}")
                        if result.actual and result.expected:
                            print(f"    Expected: {result.expected}")
                            print(f"    Actual: {result.actual}")
                        if result.suggestion:
                            print(f"    💡 {result.suggestion}")
                        print()
    
    def print_batch_summary(self, summaries):
        """Print batch validation summary"""
        if not summaries:
            print("No validation results")
            return
        
        total_items = len(summaries)
        valid_items = sum(1 for s in summaries if s.is_valid())
        total_warnings = sum(s.warnings for s in summaries)
        total_errors = sum(s.errors for s in summaries)
        total_critical = sum(s.critical for s in summaries)
        avg_score = sum(s.overall_score for s in summaries) / total_items
        
        print(f"\n{'='*60}")
        print(f"BATCH VALIDATION SUMMARY")
        print(f"{'='*60}")
        print(f"Items Validated: {total_items}")
        print(f"Valid Items: {valid_items} ({valid_items/total_items:.1%})")
        print(f"Average Score: {avg_score:.2f}")
        print(f"Total Warnings: {total_warnings}")
        print(f"Total Errors: {total_errors}")
        print(f"Total Critical: {total_critical}")
        
        # Confidence level distribution
        confidence_counts = {}
        for summary in summaries:
            level = summary.confidence_level
            confidence_counts[level] = confidence_counts.get(level, 0) + 1
        
        print(f"\nConfidence Level Distribution:")
        for level in ['VERIFIED', 'HIGH', 'MEDIUM', 'LOW']:
            count = confidence_counts.get(level, 0)
            print(f"  {level}: {count} ({count/total_items:.1%})")
        
        # Show problematic items
        problem_items = [s for s in summaries if not s.is_valid()]
        if problem_items:
            print(f"\nItems with Critical Issues:")
            for summary in problem_items:
                print(f"  • {summary.item_id} ({summary.critical} critical, {summary.errors} errors)")
    
    def save_validation_report(self, summaries):
        """Save validation report to JSON file"""
        report_data = {
            'validation_report': {
                'timestamp': datetime.now().isoformat(),
                'total_items': len(summaries),
                'valid_items': sum(1 for s in summaries if s.is_valid()),
                'average_score': sum(s.overall_score for s in summaries) / len(summaries) if summaries else 0,
                'items': []
            }
        }
        
        for summary in summaries:
            item_report = {
                'item_id': summary.item_id,
                'overall_score': summary.overall_score,
                'confidence_level': summary.confidence_level,
                'is_valid': summary.is_valid(),
                'checks': {
                    'total': summary.total_checks,
                    'passed': summary.passed,
                    'warnings': summary.warnings,
                    'errors': summary.errors,
                    'critical': summary.critical
                },
                'results': [
                    {
                        'rule': result.rule_name,
                        'level': result.level.value,
                        'message': result.message,
                        'field': result.field,
                        'suggestion': result.suggestion
                    }
                    for result in summary.results
                ]
            }
            report_data['validation_report']['items'].append(item_report)
        
        # Save report
        output_path = Path(self.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2, sort_keys=True)
        
        print(f"\nValidation report saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Run data validation on Terra35 cost data')
    
    # Validation targets
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument('--all', action='store_true',
                             help='Validate all items in database')
    target_group.add_argument('--item', type=str,
                             help='Validate specific item by ID')
    target_group.add_argument('--session', type=str,
                             help='Validate items from specific collection session')
    
    # Options
    parser.add_argument('--db-path', type=str,
                       help='Path to database file')
    parser.add_argument('--report', type=str,
                       help='Save validation report to JSON file')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Create validation runner
    runner = ValidationRunner(
        db_path=args.db_path,
        output_file=args.report
    )
    
    # Run validation
    try:
        if args.all:
            success = runner.validate_all_items()
        elif args.item:
            success = runner.validate_single_item(args.item)
        elif args.session:
            success = runner.validate_session_items(args.session)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"Validation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()