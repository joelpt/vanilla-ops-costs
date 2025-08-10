#!/usr/bin/env python3
"""
Database Health Check - Automated Milestone Validation
Validates actual database counts against PLAN.md completion statements

Usage:
    python scripts/database_health_check.py
    python scripts/database_health_check.py --detailed
"""

import sqlite3
import os
import sys
from pathlib import Path

def get_database_path():
    """Get the path to the vanilla costs database"""
    script_dir = Path(__file__).parent
    db_path = script_dir.parent / "data" / "costs" / "vanilla_costs.db"
    
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}")
    
    return str(db_path)

def get_database_counts(db_path):
    """Get counts from all database tables"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    counts = {}
    
    # Get cost items count
    cursor.execute("SELECT COUNT(*) FROM cost_items")
    counts['cost_items'] = cursor.fetchone()[0]
    
    # Get cost pricing count
    cursor.execute("SELECT COUNT(*) FROM cost_pricing") 
    counts['cost_pricing'] = cursor.fetchone()[0]
    
    # Get source references count
    cursor.execute("SELECT COUNT(*) FROM source_references")
    counts['source_references'] = cursor.fetchone()[0]
    
    # Get sources count
    cursor.execute("SELECT COUNT(*) FROM sources")
    counts['sources'] = cursor.fetchone()[0]
    
    conn.close()
    return counts

def validate_milestone_status():
    """Validate milestone completion status against database reality"""
    try:
        db_path = get_database_path()
        counts = get_database_counts(db_path)
        
        print("🔍 DATABASE HEALTH CHECK REPORT")
        print("=" * 50)
        print(f"Database: {db_path}")
        print(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Current database status
        print("📊 CURRENT DATABASE COUNTS:")
        print(f"  • Cost Items: {counts['cost_items']:,}")
        print(f"  • Cost Pricing: {counts['cost_pricing']:,}")
        print(f"  • Source References: {counts['source_references']:,}")
        print(f"  • Sources: {counts['sources']:,}")
        print()
        
        # Coverage analysis - based on cost_pricing entries (actual costed items)
        if counts['cost_pricing'] > 0:
            coverage = (counts['source_references'] / counts['cost_pricing']) * 100
            print(f"📈 SOURCE REFERENCE COVERAGE: {coverage:.1f}%")
            
            if coverage >= 90:
                print("  ✅ EXCELLENT - High source reference coverage")
            elif coverage >= 75:
                print("  ⚠️  GOOD - Acceptable source reference coverage")
            else:
                print("  ❌ POOR - Low source reference coverage needs attention")
        print()
        
        # Milestone 2 validation - based on cost_pricing entries
        print("🎯 MILESTONE 2 VALIDATION:")
        expected_cost_pricing = 500  # Target for comprehensive cost database
        
        if counts['cost_pricing'] >= 500:
            print(f"  ✅ MILESTONE 2 COMPLETE - {counts['cost_pricing']} cost pricing entries")
            milestone_status = "COMPLETE"
        elif counts['cost_pricing'] >= 400:
            print(f"  ⚠️  MILESTONE 2 NEARLY COMPLETE - {counts['cost_pricing']} cost pricing entries (>400 threshold)")
            milestone_status = "NEARLY_COMPLETE"
        else:
            print(f"  ❌ MILESTONE 2 INCOMPLETE - Only {counts['cost_pricing']} cost pricing entries (need 500+)")
            milestone_status = "INCOMPLETE"
        
        print()
        
        # Data quality recommendations
        print("💡 RECOMMENDATIONS:")
        
        if counts['cost_pricing'] == 0:
            print("  • CRITICAL: Database is empty - run population scripts")
        elif counts['source_references'] < counts['cost_pricing'] * 0.8:
            print("  • HIGH: Improve source reference coverage")
        
        if counts['cost_pricing'] < counts['cost_items'] * 0.8:
            print("  • MEDIUM: Some cost items missing pricing data")
        
        if counts['sources'] < 20:
            print("  • LOW: Consider diversifying supplier sources")
        
        print()
        return {
            'status': milestone_status,
            'counts': counts,
            'coverage': coverage if counts['cost_pricing'] > 0 else 0
        }
        
    except Exception as e:
        print(f"❌ ERROR: Database health check failed: {e}")
        return {'status': 'ERROR', 'error': str(e)}

def detailed_analysis(db_path):
    """Provide detailed database analysis"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n📋 DETAILED ANALYSIS:")
    print("-" * 30)
    
    # Items by category
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM cost_items 
        GROUP BY category 
        ORDER BY count DESC
    """)
    
    print("Items by Category:")
    for category, count in cursor.fetchall():
        print(f"  • {category}: {count} items")
    
    # Confidence levels
    cursor.execute("""
        SELECT confidence_level, COUNT(*) as count
        FROM cost_items 
        GROUP BY confidence_level 
        ORDER BY count DESC
    """)
    
    print("\nConfidence Levels:")
    for confidence, count in cursor.fetchall():
        print(f"  • {confidence}: {count} items")
    
    # Top sources
    cursor.execute("""
        SELECT s.company_name, COUNT(*) as ref_count
        FROM sources s
        JOIN source_references sr ON s.id = sr.source_id
        GROUP BY s.company_name
        ORDER BY ref_count DESC
        LIMIT 10
    """)
    
    print("\nTop 10 Sources by Reference Count:")
    for company, ref_count in cursor.fetchall():
        print(f"  • {company}: {ref_count} references")
    
    conn.close()

if __name__ == "__main__":
    import datetime
    
    detailed = "--detailed" in sys.argv
    
    try:
        result = validate_milestone_status()
        
        if detailed and result.get('status') != 'ERROR':
            detailed_analysis(get_database_path())
        
        # Exit codes for automation
        if result.get('status') == 'COMPLETE':
            sys.exit(0)
        elif result.get('status') == 'NEARLY_COMPLETE':
            sys.exit(1) 
        else:
            sys.exit(2)
            
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        sys.exit(3)