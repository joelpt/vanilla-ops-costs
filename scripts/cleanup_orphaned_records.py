#!/usr/bin/env python3
"""
Cleanup Orphaned Database Records
Removes cost_pricing entries that don't have corresponding cost_items.
These are likely remnants from database population issues.
"""

import sqlite3
from pathlib import Path

def get_database_path():
    """Get the path to the vanilla costs database"""
    script_dir = Path(__file__).parent
    db_path = script_dir.parent / "data" / "costs" / "vanilla_costs.db"
    
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}")
    
    return str(db_path)

def identify_orphaned_records():
    """Identify orphaned cost_pricing records"""
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Find orphaned cost_pricing records
    cursor.execute("""
        SELECT cp.id, cp.cost_item_id, cp.unit_cost, cp.unit, cp.effective_date
        FROM cost_pricing cp
        LEFT JOIN cost_items ci ON cp.cost_item_id = ci.id
        WHERE ci.id IS NULL
        ORDER BY cp.id
    """)
    
    orphaned_records = cursor.fetchall()
    conn.close()
    
    return orphaned_records

def cleanup_orphaned_records(dry_run=True):
    """Remove orphaned cost_pricing records"""
    orphaned_records = identify_orphaned_records()
    
    print("🔍 ORPHANED COST_PRICING RECORDS CLEANUP")
    print("=" * 50)
    print(f"Found {len(orphaned_records)} orphaned cost_pricing records")
    print()
    
    if not orphaned_records:
        print("✅ No orphaned records found - database is clean!")
        return
    
    print("📋 ORPHANED RECORDS TO REMOVE:")
    for record in orphaned_records:
        print(f"  • ID {record[0]}: cost_item_id={record[1]}, cost=${record[2]} {record[3]}, date={record[4]}")
    print()
    
    if dry_run:
        print("🔧 DRY RUN MODE - No changes made")
        print("To apply cleanup, run with: python scripts/cleanup_orphaned_records.py --fix")
        return len(orphaned_records)
    
    # Perform cleanup
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Delete orphaned records
    orphaned_ids = [str(record[0]) for record in orphaned_records]
    cursor.execute(f"""
        DELETE FROM cost_pricing 
        WHERE id IN ({','.join(orphaned_ids)})
    """)
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"✅ CLEANUP COMPLETE: Removed {deleted_count} orphaned cost_pricing records")
    print()
    
    # Verify cleanup
    remaining_orphaned = identify_orphaned_records()
    if not remaining_orphaned:
        print("🎉 DATABASE CLEANUP SUCCESSFUL - No orphaned records remain")
    else:
        print(f"⚠️ WARNING: {len(remaining_orphaned)} orphaned records still exist")
    
    return deleted_count

def main():
    import sys
    
    dry_run = "--fix" not in sys.argv
    
    try:
        result = cleanup_orphaned_records(dry_run)
        print()
        
        if dry_run and result > 0:
            print("💡 RECOMMENDATION: Run cleanup to fix database integrity")
            print("   This will improve source reference coverage calculations")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        exit(1)

if __name__ == "__main__":
    main()