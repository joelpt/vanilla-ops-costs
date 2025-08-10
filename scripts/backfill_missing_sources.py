#!/usr/bin/env python3
"""
Backfill Missing Source References
Identifies cost pricing entries without source references and backfills them 
by reverse-engineering from research documentation files.

Usage:
    python scripts/backfill_missing_sources.py --analyze
    python scripts/backfill_missing_sources.py --fix
"""

import sqlite3
import json
import re
from pathlib import Path
import argparse

def get_database_path():
    """Get the path to the vanilla costs database"""
    script_dir = Path(__file__).parent
    db_path = script_dir.parent / "data" / "costs" / "vanilla_costs.db"
    
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}")
    
    return str(db_path)

def get_missing_source_items():
    """Get cost pricing entries missing source references"""
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
        cp.confidence_level
    FROM cost_pricing cp
    JOIN cost_items ci ON cp.cost_item_id = ci.id
    JOIN cost_categories cc ON ci.category_id = cc.id
    LEFT JOIN source_references sr ON cp.id = sr.cost_pricing_id
    WHERE sr.cost_pricing_id IS NULL
    ORDER BY cc.name, ci.item_name
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'pricing_id': row[0],
            'item_name': row[1],
            'item_id': row[2],
            'category': row[3],
            'unit_cost': row[4],
            'unit': row[5],
            'confidence_level': row[6]
        }
        for row in results
    ]

def find_research_files():
    """Find all research documentation files"""
    data_dir = Path(__file__).parent.parent / "data"
    return list(data_dir.glob("*.md"))

def extract_sources_from_file(file_path):
    """Extract potential source references from a research file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sources = []
    
    # Look for validated suppliers in VALIDATION STATUS sections
    validation_pattern = r'### Validation Summary.*?- \*\*Primary Sources\*\*: ([^*]+)'
    validation_match = re.search(validation_pattern, content, re.DOTALL)
    if validation_match:
        supplier_text = validation_match.group(1)
        # Extract supplier names from text like "Uline (verified at uline.com), packaging equipment suppliers"
        supplier_matches = re.findall(r'(\w+(?:\s+\w+)*)\s*\([^)]*\)', supplier_text)
        sources.extend(supplier_matches)
    
    # Look for verified suppliers mentioned in content
    supplier_patterns = [
        r'(\w+(?:\s+\w+)*)\s*\(verified[^)]*\)',
        r'\*\*([A-Z][a-zA-Z\s&]+)\*\*:?\s*(?:verified|confirmed)',
        r'verified suppliers?:?\s*([^.*\n]+)',
        r'Primary Sources:?\s*([^.*\n]+)'
    ]
    
    for pattern in supplier_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            if isinstance(match, tuple):
                sources.extend([m.strip() for m in match if m.strip()])
            else:
                sources.append(match.strip())
    
    # Clean up sources
    cleaned_sources = []
    for source in sources:
        source = re.sub(r'\s*\([^)]*\)', '', source)  # Remove parentheses
        source = re.sub(r'\s*-.*$', '', source)  # Remove dashes and everything after
        source = source.strip(' .,;:')
        if source and len(source) > 2:
            cleaned_sources.append(source)
    
    return list(set(cleaned_sources))

def map_items_to_sources(missing_items, research_files):
    """Map missing items to potential sources from research files"""
    mappings = []
    
    for item in missing_items:
        item_keywords = item['item_name'].lower().split()
        category_keywords = item['category'].lower().split()
        
        best_matches = []
        
        for file_path in research_files:
            file_sources = extract_sources_from_file(file_path)
            if not file_sources:
                continue
                
            file_content = file_path.read_text(encoding='utf-8').lower()
            
            # Check if item keywords appear in file
            keyword_matches = sum(1 for keyword in item_keywords if keyword in file_content)
            category_matches = sum(1 for keyword in category_keywords if keyword in file_content)
            
            if keyword_matches > 0 or category_matches > 0:
                confidence = keyword_matches + (category_matches * 0.5)
                best_matches.append({
                    'file': file_path.name,
                    'sources': file_sources,
                    'confidence': confidence
                })
        
        # Sort by confidence and take the best match
        best_matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        if best_matches:
            mappings.append({
                'item': item,
                'suggested_sources': best_matches[0]['sources'][:3],  # Top 3 sources
                'source_file': best_matches[0]['file'],
                'confidence': best_matches[0]['confidence']
            })
        else:
            mappings.append({
                'item': item,
                'suggested_sources': [],
                'source_file': 'NO_MATCH',
                'confidence': 0
            })
    
    return mappings

def get_or_create_source(cursor, company_name):
    """Get existing source ID or create new source"""
    cursor.execute("SELECT id FROM sources WHERE company_name = ?", (company_name,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    # Create new source
    cursor.execute("""
        INSERT INTO sources (company_name, source_type, reliability_score, is_verified)
        VALUES (?, 'supplier', 0.8, 1)
    """, (company_name,))
    
    return cursor.lastrowid

def create_source_reference(cursor, pricing_id, source_id, company_name):
    """Create a source reference entry"""
    # Create a generic URL based on company name
    base_url = f"https://www.{company_name.lower().replace(' ', '').replace('&', 'and')}.com"
    
    cursor.execute("""
        INSERT OR REPLACE INTO source_references 
        (cost_pricing_id, source_id, reference_type, source_url, date_accessed, notes)
        VALUES (?, ?, 'primary', ?, date('now'), 'Reverse-engineered from research documentation')
    """, (pricing_id, source_id, base_url))

def analyze_missing_sources():
    """Analyze and report missing source references"""
    print("🔍 ANALYZING MISSING SOURCE REFERENCES")
    print("=" * 50)
    
    missing_items = get_missing_source_items()
    print(f"Found {len(missing_items)} cost pricing entries without source references")
    print()
    
    research_files = find_research_files()
    print(f"Analyzing {len(research_files)} research documentation files")
    print()
    
    mappings = map_items_to_sources(missing_items, research_files)
    
    # Group by category for reporting
    by_category = {}
    for mapping in mappings:
        category = mapping['item']['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(mapping)
    
    for category, items in by_category.items():
        print(f"📊 CATEGORY: {category}")
        print("-" * 30)
        
        for mapping in items[:5]:  # Show first 5 items per category
            item = mapping['item']
            print(f"  • {item['item_name']} (${item['unit_cost']}/{item['unit']})")
            if mapping['suggested_sources']:
                print(f"    → Sources: {', '.join(mapping['suggested_sources'])}")
                print(f"    → From: {mapping['source_file']} (confidence: {mapping['confidence']:.1f})")
            else:
                print("    → No sources found")
            print()
        
        if len(items) > 5:
            print(f"    ... and {len(items) - 5} more items\n")
    
    return mappings

def fix_missing_sources(dry_run=True):
    """Fix missing source references by backfilling from research"""
    print("🔧 BACKFILLING MISSING SOURCE REFERENCES")
    print("=" * 50)
    
    if dry_run:
        print("DRY RUN MODE - No changes will be made")
        print()
    
    missing_items = get_missing_source_items()
    research_files = find_research_files()
    mappings = map_items_to_sources(missing_items, research_files)
    
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    backfilled = 0
    skipped = 0
    
    for mapping in mappings:
        if not mapping['suggested_sources'] or mapping['confidence'] < 0.5:
            skipped += 1
            continue
        
        pricing_id = mapping['item']['pricing_id']
        item_name = mapping['item']['item_name']
        
        # Use the first (best) suggested source
        company_name = mapping['suggested_sources'][0]
        
        print(f"✅ {item_name} → {company_name}")
        
        if not dry_run:
            try:
                source_id = get_or_create_source(cursor, company_name)
                create_source_reference(cursor, pricing_id, source_id, company_name)
                backfilled += 1
            except Exception as e:
                print(f"   ERROR: {e}")
                skipped += 1
        else:
            backfilled += 1
    
    if not dry_run:
        conn.commit()
    
    conn.close()
    
    print()
    print(f"📊 RESULTS:")
    print(f"  • Backfilled: {backfilled} source references")
    print(f"  • Skipped: {skipped} items (low confidence or no sources)")
    print(f"  • Total processed: {len(mappings)} items")
    
    if dry_run:
        print("\nTo apply changes, run with --fix flag")

def main():
    parser = argparse.ArgumentParser(description='Backfill missing source references')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--analyze', action='store_true', 
                      help='Analyze missing source references without making changes')
    group.add_argument('--fix', action='store_true',
                      help='Fix missing source references by backfilling from research')
    group.add_argument('--dry-run', action='store_true',
                      help='Show what would be fixed without making changes')
    
    args = parser.parse_args()
    
    try:
        if args.analyze:
            analyze_missing_sources()
        elif args.fix:
            fix_missing_sources(dry_run=False)
        elif args.dry_run:
            fix_missing_sources(dry_run=True)
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        exit(1)

if __name__ == "__main__":
    main()