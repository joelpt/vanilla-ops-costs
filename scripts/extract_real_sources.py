#!/usr/bin/env python3
"""
EXTRACT REAL SOURCE REFERENCES FROM DOCUMENTATION
This script works backwards from the .md documentation files to find
REAL, LEGITIMATE source references and properly populate the database.

NO FABRICATED SOURCES - ONLY REAL ONES FROM RESEARCH DOCUMENTS.
"""

import sqlite3
import json
import re
import os
from datetime import datetime
from pathlib import Path

def extract_verified_sources_from_md(file_path):
    """Extract VERIFIED, REAL sources from markdown files."""
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []
    
    sources = []
    
    # Extract VERIFIED suppliers from validation sections
    verification_patterns = [
        r'\*\*(.*?)\*\*: VERIFIED at (https?://[^\s\)]+)(.*?)(?=\n|$)',
        r'- \*\*(.*?)\*\*: VERIFIED at (https?://[^\s\)]+)',
        r'\*\*(.*?)\*\* \(VERIFIED\): (https?://[^\s\)]+)',
    ]
    
    for pattern in verification_patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            if len(match) >= 2:
                company_name = match[0].strip()
                url = match[1].strip()
                description = match[2].strip() if len(match) > 2 else ""
                
                sources.append({
                    'company_name': company_name,
                    'website_url': url,
                    'tier': 1,  # Verified sources are tier 1
                    'type': 'supplier',
                    'verified': True,
                    'description': description,
                    'source_file': file_path
                })
    
    # Extract pricing sources with specific suppliers mentioned
    pricing_patterns = [
        r'\*\*(.*?)\*\*.*?[:\-] .*?\$([0-9,]+)',  # Company: $price format
        r'- \*\*(.*?)\*\*.*?pricing.*?\$([0-9,]+)',  # Pricing mentions
        r'(https?://[^\s\)]+).*?pricing',  # Direct pricing URLs
    ]
    
    # Extract URLs that appear to be legitimate supplier websites
    url_pattern = r'(https?://(?:www\.)?([a-zA-Z0-9\-]+\.com|[a-zA-Z0-9\-]+\.org|[a-zA-Z0-9\-]+\.net)[^\s\)]*)'
    url_matches = re.findall(url_pattern, content)
    
    for full_url, domain in url_matches:
        # Skip generic domains and focus on supplier domains
        if any(skip in domain.lower() for skip in ['google', 'wikipedia', 'amazon', 'ebay', 'alibaba']):
            continue
            
        # Extract company name from domain
        company_name = domain.split('.')[0].replace('-', ' ').replace('_', ' ').title()
        
        sources.append({
            'company_name': company_name,
            'website_url': full_url,
            'tier': 2,  # URL mentions are tier 2
            'type': 'supplier',
            'verified': False,
            'description': f'Source mentioned in {os.path.basename(file_path)}',
            'source_file': file_path
        })
    
    return sources

def map_cost_items_to_source_files():
    """Map specific cost items to their documentation files using item names."""
    # Read the database to understand what items we have
    conn = sqlite3.connect("data/costs/vanilla_costs.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ci.id, ci.item_name, cc.name as category_name
        FROM cost_items ci
        JOIN cost_categories cc ON ci.category_id = cc.id
        ORDER BY ci.item_name
    """)
    
    items = cursor.fetchall()
    conn.close()
    
    # Documentation files available
    doc_files = [f for f in os.listdir('data') if f.endswith('_2025.md')]
    
    item_to_file_mapping = {}
    
    for item_id, item_name, category_name in items:
        # Find the best matching documentation file
        best_match = None
        best_score = 0
        
        for doc_file in doc_files:
            doc_path = f"data/{doc_file}"
            
            # Calculate match score based on keywords
            score = 0
            item_words = item_name.lower().split()
            file_words = doc_file.lower().replace('_', ' ').replace('.md', '').split()
            
            for word in item_words:
                if any(word in file_word for file_word in file_words):
                    score += 1
            
            # Category-based matching
            category_words = category_name.lower().split()
            for word in category_words:
                if any(word in file_word for file_word in file_words):
                    score += 0.5
            
            if score > best_score:
                best_score = score
                best_match = doc_path
        
        if best_match:
            item_to_file_mapping[item_id] = best_match
    
    return item_to_file_mapping

def populate_real_sources_and_references():
    """Populate database with REAL sources from documentation files."""
    
    # Get all documentation files
    doc_files = []
    for f in os.listdir('data'):
        if f.endswith('_2025.md'):
            doc_files.append(f"data/{f}")
    
    print(f"Analyzing {len(doc_files)} documentation files for REAL sources...")
    
    # Extract all real sources from documentation
    all_sources = {}  # Deduplicate by company name
    
    for doc_file in doc_files:
        print(f"Processing {os.path.basename(doc_file)}...")
        sources = extract_verified_sources_from_md(doc_file)
        
        for source in sources:
            company_name = source['company_name']
            
            # Deduplicate - keep the highest tier (most verified)
            if company_name not in all_sources or source['tier'] < all_sources[company_name]['tier']:
                all_sources[company_name] = source
    
    print(f"Found {len(all_sources)} unique REAL sources from documentation")
    
    # Connect to database
    conn = sqlite3.connect("data/costs/vanilla_costs.db")
    cursor = conn.cursor()
    
    # Insert real sources into database
    source_ids = {}
    for company_name, source in all_sources.items():
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO sources (
                    company_name, company_type, website_url, tier, is_active
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                company_name,
                source['type'],
                source['website_url'],
                source['tier'],
                True
            ))
            
            # Get the source ID
            cursor.execute("SELECT id FROM sources WHERE company_name = ?", (company_name,))
            result = cursor.fetchone()
            if result:
                source_ids[company_name] = result[0]
        
        except Exception as e:
            print(f"Error inserting source {company_name}: {e}")
    
    conn.commit()
    print(f"Inserted {len(source_ids)} real sources into database")
    
    # Now map cost items to their source files and create references
    item_to_file_mapping = map_cost_items_to_source_files()
    
    # Get all cost pricing entries without source references
    cursor.execute("""
        SELECT cp.id, cp.cost_item_id, ci.item_name
        FROM cost_pricing cp
        JOIN cost_items ci ON cp.cost_item_id = ci.id
        LEFT JOIN source_references sr ON cp.id = sr.cost_pricing_id
        WHERE sr.id IS NULL
        ORDER BY ci.item_name
    """)
    
    missing_refs = cursor.fetchall()
    print(f"Need to create source references for {len(missing_refs)} cost items")
    
    references_created = 0
    
    for cost_pricing_id, cost_item_id, item_name in missing_refs:
        
        # Find the documentation file for this item
        doc_file = item_to_file_mapping.get(cost_item_id)
        if not doc_file:
            continue
        
        # Extract sources from that specific file
        file_sources = extract_verified_sources_from_md(doc_file)
        
        if file_sources:
            # Use the first (best) source from the file
            source = file_sources[0]
            company_name = source['company_name']
            
            if company_name in source_ids:
                source_id = source_ids[company_name]
                
                try:
                    cursor.execute("""
                        INSERT INTO source_references (
                            cost_pricing_id, source_id, reference_type, source_url,
                            date_accessed, notes
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        cost_pricing_id,
                        source_id,
                        'primary',
                        source['website_url'],
                        datetime.now().strftime('%Y-%m-%d'),
                        f"Real source from {os.path.basename(doc_file)}: {source.get('description', '')}"
                    ))
                    references_created += 1
                
                except Exception as e:
                    print(f"Error creating reference for {item_name}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Created {references_created} source references from REAL documentation sources")
    
    # Final verification
    conn = sqlite3.connect("data/costs/vanilla_costs.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM cost_pricing")
    total_pricing = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM source_references")
    total_refs = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM cost_pricing cp 
        LEFT JOIN source_references sr ON cp.id = sr.cost_pricing_id 
        WHERE sr.id IS NULL
    """)
    still_missing = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n📊 RESULTS:")
    print(f"Total cost pricing entries: {total_pricing}")
    print(f"Total source references: {total_refs}")
    print(f"Still missing references: {still_missing}")
    print(f"Coverage: {((total_pricing - still_missing) / total_pricing * 100):.1f}%")

if __name__ == "__main__":
    print("🔍 EXTRACTING REAL SOURCE REFERENCES FROM DOCUMENTATION")
    print("=" * 60)
    populate_real_sources_and_references()