#!/usr/bin/env python3
"""
Script to process FIXUP_CHECKLIST.md and run cost-validator for each incomplete item.
"""

import re
import subprocess
import sys
from pathlib import Path


def read_checklist_file():
    """Read the FIXUP_CHECKLIST.md file and return its content."""
    checklist_path = Path("FIXUP_CHECKLIST.md")
    if not checklist_path.exists():
        print(f"ERROR: {checklist_path} not found!")
        sys.exit(1)
    
    with open(checklist_path, 'r') as f:
        return f.read()


def write_checklist_file(content):
    """Write the updated content back to FIXUP_CHECKLIST.md."""
    checklist_path = Path("FIXUP_CHECKLIST.md")
    with open(checklist_path, 'w') as f:
        f.write(content)


def find_incomplete_items(content):
    """Find all incomplete items (lines with [ ]) and extract the cost_pricing IDs."""
    incomplete_pattern = r'\[ \] cost_pricing\.id = (\d+)'
    matches = re.findall(incomplete_pattern, content)
    return [int(id_num) for id_num in matches]


def run_cost_validator(cost_pricing_id):
    """Run the cost-validator agent for the given cost_pricing ID."""
    claude_cmd = [
        "/Users/joelthor/.claude/local/claude",
        "--dangerously-skip-permissions",
        "-p",
        f"For cost_pricing.id = {cost_pricing_id}, invoke the cost-validator agent to verify and if needed update values in the db to correctly reflect costing_method and any other relevant values for that cost_pricing item"
    ]
    
    print(f"Running cost-validator for cost_pricing.id = {cost_pricing_id}...")
    
    try:
        result = subprocess.run(claude_cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ Successfully processed cost_pricing.id = {cost_pricing_id}")
            return True
        else:
            print(f"❌ Error processing cost_pricing.id = {cost_pricing_id}")
            print(f"   Return code: {result.returncode}")
            if result.stderr:
                print(f"   Error output: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout processing cost_pricing.id = {cost_pricing_id}")
        return False
    except Exception as e:
        print(f"💥 Exception processing cost_pricing.id = {cost_pricing_id}: {e}")
        return False


def mark_item_completed(content, cost_pricing_id):
    """Mark the specified cost_pricing ID as completed in the content."""
    pattern = rf'\[ \] cost_pricing\.id = {cost_pricing_id}'
    replacement = f'[x] cost_pricing.id = {cost_pricing_id}'
    return re.sub(pattern, replacement, content)


def main():
    """Main processing function."""
    print("🔄 Starting FIXUP_CHECKLIST.md processing...")
    
    # Read the checklist
    content = read_checklist_file()
    original_content = content
    
    # Find incomplete items
    incomplete_items = find_incomplete_items(content)
    total_items = len(incomplete_items)
    
    print(f"📋 Found {total_items} incomplete items to process")
    
    if total_items == 0:
        print("✅ No incomplete items found!")
        return
    
    # Process each item
    processed = 0
    failed = 0
    
    for i, cost_pricing_id in enumerate(incomplete_items, 1):
        print(f"\n[{i}/{total_items}] Processing cost_pricing.id = {cost_pricing_id}")
        
        success = run_cost_validator(cost_pricing_id)
        
        if success:
            # Mark as completed in the content
            content = mark_item_completed(content, cost_pricing_id)
            processed += 1
        else:
            failed += 1
        
        # Show progress
        print(f"Progress: {processed} completed, {failed} failed, {total_items - i} remaining")
    
    # Write updated content back to file
    if content != original_content:
        write_checklist_file(content)
        print(f"\n💾 Updated FIXUP_CHECKLIST.md with {processed} completed items")
    
    # Final summary
    print(f"\n🎯 Final Summary:")
    print(f"   Total items: {total_items}")
    print(f"   Completed: {processed}")
    print(f"   Failed: {failed}")
    print(f"   Success rate: {processed/total_items*100:.1f}%")


if __name__ == "__main__":
    main()