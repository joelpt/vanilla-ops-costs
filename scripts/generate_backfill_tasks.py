#!/usr/bin/env python3
"""
Generate Milestone 3 Backfill Tasks
Creates individual tasks for each cost pricing entry missing source references

Usage:
    python scripts/generate_backfill_tasks.py --output tasks.md
    python scripts/generate_backfill_tasks.py --priority-analysis
"""

import sqlite3
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

def get_database_path():
    """Get the path to the vanilla costs database"""
    script_dir = Path(__file__).parent
    db_path = script_dir.parent / "data" / "costs" / "vanilla_costs.db"
    
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}")
    
    return str(db_path)

def get_missing_source_items():
    """Get detailed information about cost pricing entries missing source references"""
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = """
    SELECT 
        cp.id as pricing_id,
        ci.item_name,
        ci.item_id,
        cc.name as category,
        cp.unit_cost,
        cp.unit,
        cp.confidence_level,
        cp.effective_date,
        ci.specifications
    FROM cost_pricing cp
    JOIN cost_items ci ON cp.cost_item_id = ci.id
    JOIN cost_categories cc ON ci.category_id = cc.id
    WHERE cp.id NOT IN (
        SELECT DISTINCT cost_pricing_id 
        FROM source_references 
        WHERE cost_pricing_id IS NOT NULL
    )
    ORDER BY cp.unit_cost DESC, cc.name, ci.item_name
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    missing_items = []
    for row in results:
        specifications = {}
        if row[8]:  # specifications JSON field
            try:
                specifications = json.loads(row[8])
            except json.JSONDecodeError:
                specifications = {}
        
        missing_items.append({
            'pricing_id': row[0],
            'item_name': row[1],
            'item_id': row[2],
            'category': row[3],
            'unit_cost': float(row[4]) if row[4] else 0.0,
            'unit': row[5],
            'confidence_level': row[6],
            'effective_date': row[7],
            'specifications': specifications
        })
    
    return missing_items

def categorize_by_priority(missing_items: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize missing items by priority levels"""
    
    priority_groups = {
        'HIGH': [],
        'MEDIUM': [],
        'LOW': []
    }
    
    for item in missing_items:
        cost = item['unit_cost']
        confidence = item['confidence_level']
        
        # HIGH PRIORITY: High-cost items, critical infrastructure, VERIFIED confidence
        if (cost > 10000 or 
            confidence == 'VERIFIED' or 
            'infrastructure' in item['category'].lower() or
            'facility' in item['category'].lower()):
            priority_groups['HIGH'].append(item)
        
        # LOW PRIORITY: Low-cost consumables, generic rates, MEDIUM confidence
        elif (cost < 1000 and 
              (confidence == 'MEDIUM' or 
               'consumable' in item['category'].lower() or
               'supply' in item['category'].lower() or
               'utility' in item['category'].lower())):
            priority_groups['LOW'].append(item)
        
        # MEDIUM PRIORITY: Everything else
        else:
            priority_groups['MEDIUM'].append(item)
    
    return priority_groups

def generate_task_markdown(missing_items: List[Dict], output_file: str = None):
    """Generate Markdown formatted backfill tasks"""
    
    priority_groups = categorize_by_priority(missing_items)
    
    markdown_content = []
    markdown_content.append("# Milestone 3: Source Reference Backfill Tasks")
    markdown_content.append("")
    markdown_content.append(f"**Total Missing Source References**: {len(missing_items)}")
    markdown_content.append(f"**Target**: Achieve 100% source reference coverage (539/539 entries)")
    markdown_content.append("")
    
    task_number = 1
    
    for priority in ['HIGH', 'MEDIUM', 'LOW']:
        items = priority_groups[priority]
        if not items:
            continue
            
        markdown_content.append(f"## {priority} PRIORITY ({len(items)} items)")
        markdown_content.append("")
        
        for item in items:
            task_title = f"Task 3.{task_number}: Backfill source reference for {item['item_name']} - {item['category']}"
            
            markdown_content.append(f"### {task_title}")
            markdown_content.append("")
            markdown_content.append("**Item Details**:")
            markdown_content.append(f"- **Pricing ID**: {item['pricing_id']}")
            markdown_content.append(f"- **Item ID**: {item['item_id']}")
            markdown_content.append(f"- **Cost**: ${item['unit_cost']:,.2f} {item['unit']}")
            markdown_content.append(f"- **Confidence**: {item['confidence_level']}")
            markdown_content.append(f"- **Date**: {item['effective_date']}")
            
            if item['specifications']:
                markdown_content.append("- **Specifications**: " + str(item['specifications']))
            
            markdown_content.append("")
            markdown_content.append("**Backfill Process**:")
            markdown_content.append("- [ ] Step 1: Search relevant .md files for source references")
            markdown_content.append("- [ ] Step 2: Use zen thinkdeep for reverse engineering (if needed)")
            markdown_content.append("- [ ] Step 3: Use zen consensus for source validation (if needed)")
            markdown_content.append("- [ ] Step 4: Web search for source identification")
            markdown_content.append("- [ ] Step 5: MCP Playwright for source verification")
            markdown_content.append("- [ ] Step 6: Quality assurance - validate source quality")
            markdown_content.append("- [ ] Step 7: Update database with verified source reference")
            markdown_content.append("- [ ] Step 8: Update documentation with audit trail")
            markdown_content.append("")
            markdown_content.append("**Success Criteria**:")
            markdown_content.append("- ✅ High-quality verified source reference obtained")
            markdown_content.append("- ✅ Database updated with source attribution")
            markdown_content.append("- ✅ Documentation includes audit trail")
            markdown_content.append("")
            markdown_content.append("---")
            markdown_content.append("")
            
            task_number += 1
    
    # Summary statistics
    markdown_content.append("## Summary")
    markdown_content.append("")
    markdown_content.append(f"- **HIGH Priority**: {len(priority_groups['HIGH'])} items")
    markdown_content.append(f"- **MEDIUM Priority**: {len(priority_groups['MEDIUM'])} items")
    markdown_content.append(f"- **LOW Priority**: {len(priority_groups['LOW'])} items")
    markdown_content.append(f"- **Total Tasks**: {len(missing_items)}")
    markdown_content.append("")
    markdown_content.append("**Completion Target**: 100% source reference coverage")
    markdown_content.append("**Success Metric**: 539/539 cost pricing entries with source references")
    
    content = "\n".join(markdown_content)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 Tasks written to {output_file}")
    else:
        print(content)
    
    return content

def analyze_priorities(missing_items: List[Dict]):
    """Analyze and report priority distribution"""
    
    priority_groups = categorize_by_priority(missing_items)
    
    print("🎯 PRIORITY ANALYSIS FOR MILESTONE 3 BACKFILL TASKS")
    print("=" * 60)
    print()
    
    total_cost = sum(item['unit_cost'] for item in missing_items)
    
    for priority in ['HIGH', 'MEDIUM', 'LOW']:
        items = priority_groups[priority]
        if not items:
            continue
        
        priority_cost = sum(item['unit_cost'] for item in items)
        avg_cost = priority_cost / len(items) if items else 0
        
        print(f"📊 {priority} PRIORITY: {len(items)} items")
        print(f"   Total Value: ${priority_cost:,.2f}")
        print(f"   Average Cost: ${avg_cost:,.2f}")
        print(f"   Categories: {set(item['category'] for item in items)}")
        print(f"   Confidence Levels: {set(item['confidence_level'] for item in items)}")
        print()
    
    print(f"📈 OVERALL STATISTICS:")
    print(f"   Total Missing Items: {len(missing_items)}")
    print(f"   Total Value: ${total_cost:,.2f}")
    print(f"   Average Item Cost: ${total_cost/len(missing_items):,.2f}")
    print()
    
    # Show highest cost items
    print("💰 TOP 10 HIGHEST COST ITEMS WITHOUT SOURCE REFERENCES:")
    sorted_items = sorted(missing_items, key=lambda x: x['unit_cost'], reverse=True)[:10]
    for i, item in enumerate(sorted_items, 1):
        print(f"   {i:2d}. {item['item_name']} - ${item['unit_cost']:,.2f} ({item['category']})")
    print()

def main():
    parser = argparse.ArgumentParser(description='Generate Milestone 3 source reference backfill tasks')
    parser.add_argument('--output', '-o', help='Output file for generated tasks')
    parser.add_argument('--priority-analysis', '-p', action='store_true',
                       help='Show priority analysis of missing source references')
    
    args = parser.parse_args()
    
    try:
        missing_items = get_missing_source_items()
        
        if len(missing_items) == 0:
            print("🎉 NO MISSING SOURCE REFERENCES FOUND!")
            print("All cost pricing entries have source references.")
            return
        
        if args.priority_analysis:
            analyze_priorities(missing_items)
        else:
            generate_task_markdown(missing_items, args.output)
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        exit(1)

if __name__ == "__main__":
    main()