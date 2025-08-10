#!/usr/bin/env python3
"""
Generate FIXUP_CHECKLIST.md with checkboxes for each cost_pricing.id in the database.
"""

import sqlite3
import os

def generate_fixup_checklist():
    """Generate FIXUP_CHECKLIST.md with all cost_pricing IDs."""
    
    # Database path
    db_path = "data/costs/vanilla_costs.db"
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all cost_pricing IDs
        cursor.execute("SELECT id FROM cost_pricing ORDER BY id")
        pricing_ids = cursor.fetchall()
        
        conn.close()
        
        if not pricing_ids:
            print("No cost_pricing records found in database")
            return
        
        # Generate checklist content
        checklist_content = "# FIXUP_CHECKLIST\n\n"
        checklist_content += f"Generated from {len(pricing_ids)} cost_pricing records in database.\n\n"
        
        for (pricing_id,) in pricing_ids:
            checklist_content += f"[ ] cost_pricing.id = {pricing_id}\n"
        
        # Write to file
        with open("FIXUP_CHECKLIST.md", "w") as f:
            f.write(checklist_content)
        
        print(f"Generated FIXUP_CHECKLIST.md with {len(pricing_ids)} cost_pricing IDs")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_fixup_checklist()