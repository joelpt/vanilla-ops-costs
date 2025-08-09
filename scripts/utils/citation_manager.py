#!/usr/bin/env python3
"""
Terra35 Vanilla Operations Cost Analysis - Citation Manager

This module provides utilities for creating, validating, and managing
source citations according to the established citation format standards.

Usage:
    from utils.citation_manager import CitationManager
    
    citation_mgr = CitationManager()
    citation = citation_mgr.create_citation('supplier_website', source_data)
    is_valid = citation_mgr.validate_citation(citation)
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import hashlib
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

@dataclass
class SourceReference:
    """Standardized source reference data structure"""
    citation_type: str
    citation_formatted: str
    source_url: str
    company_name: str
    date_accessed: str
    item_id: Optional[str] = None
    product_code: Optional[str] = None
    contact_person: Optional[str] = None
    quote_number: Optional[str] = None
    document_title: Optional[str] = None
    screenshot_path: Optional[str] = None
    data_extracted: Optional[Dict[str, Any]] = None
    verification_status: str = 'pending'
    confidence_score: float = 0.5
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return asdict(self)

class CitationManager:
    """
    Manager for creating, validating, and maintaining source citations
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.project_root = project_root
        self.config_path = config_path or str(project_root / 'config' / 'source_citation_format.json')
        
        # Load citation configuration
        self.config = self.load_citation_config()
        self.templates = self.config.get('citation_templates', {})
        self.source_types = self.config.get('data_source_types', {})
        
    def load_citation_config(self) -> Dict[str, Any]:
        """Load citation configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)['source_citation_format']
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load citation config: {e}")
            return {}
    
    def create_citation(self, citation_type: str, source_data: Dict[str, Any]) -> SourceReference:
        """
        Create a standardized citation from source data
        
        Args:
            citation_type: Type of citation (supplier_website, direct_quote, etc.)
            source_data: Dictionary containing source information
            
        Returns:
            SourceReference object with formatted citation
        """
        
        # Get template for citation type
        template_config = self.templates.get(citation_type)
        if not template_config:
            raise ValueError(f"Unknown citation type: {citation_type}")
        
        # Validate required fields
        required_fields = template_config.get('required_fields', [])
        missing_fields = [field for field in required_fields if not source_data.get(field)]
        if missing_fields:
            raise ValueError(f"Missing required fields for {citation_type}: {missing_fields}")
        
        # Format citation string
        citation_format = template_config.get('format', '')
        formatted_citation = self.format_citation_string(citation_format, source_data)
        
        # Calculate confidence score
        confidence_score = self.calculate_confidence_score(citation_type, source_data)
        
        # Create SourceReference
        citation = SourceReference(
            citation_type=citation_type,
            citation_formatted=formatted_citation,
            source_url=source_data.get('source_url', ''),
            company_name=source_data.get('company_name', ''),
            date_accessed=source_data.get('date_accessed', datetime.now().strftime('%Y-%m-%d')),
            item_id=source_data.get('item_id'),
            product_code=source_data.get('product_code'),
            contact_person=source_data.get('contact_person'),
            quote_number=source_data.get('quote_number'),
            document_title=source_data.get('document_title'),
            screenshot_path=source_data.get('screenshot_path'),
            data_extracted=source_data.get('data_extracted'),
            verification_status='pending',
            confidence_score=confidence_score,
            notes=source_data.get('notes')
        )
        
        return citation
    
    def format_citation_string(self, format_template: str, data: Dict[str, Any]) -> str:
        """Format citation string using template and data"""
        try:
            # Handle special formatting for dates
            if 'date_accessed' in data:
                date_str = data['date_accessed']
                if isinstance(date_str, str) and len(date_str) == 10:  # YYYY-MM-DD format
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        data['date_accessed'] = date_obj.strftime('%B %d, %Y')
                    except ValueError:
                        pass  # Keep original format if parsing fails
            
            # Format the citation
            formatted = format_template.format(**data)
            
            # Clean up any empty optional fields
            formatted = re.sub(r'\s*\[\]\s*', '', formatted)  # Remove empty brackets
            formatted = re.sub(r'\s*\{\}\s*', '', formatted)  # Remove empty braces  
            formatted = re.sub(r'\s+', ' ', formatted)  # Normalize whitespace
            
            return formatted.strip()
            
        except KeyError as e:
            raise ValueError(f"Missing required field for citation formatting: {e}")
    
    def calculate_confidence_score(self, citation_type: str, source_data: Dict[str, Any]) -> float:
        """Calculate confidence score for source citation"""
        base_score = 0.5
        
        # Base score by citation type (tier)
        for tier, tier_info in self.source_types.items():
            if citation_type in tier_info.get('types', []):
                if tier == 'tier_1_preferred':
                    base_score = 0.8
                elif tier == 'tier_2_acceptable':
                    base_score = 0.6
                elif tier == 'tier_3_caution':
                    base_score = 0.4
                break
        
        # Adjustments based on data completeness and quality
        quality_adjustments = 0.0
        
        # URL quality
        url = source_data.get('source_url', '')
        if url:
            if self.is_valid_url(url):
                quality_adjustments += 0.05
            if self.is_official_domain(url, source_data.get('company_name', '')):
                quality_adjustments += 0.10
        
        # Data freshness
        date_accessed = source_data.get('date_accessed')
        if date_accessed:
            try:
                access_date = datetime.strptime(date_accessed, '%Y-%m-%d')
                days_old = (datetime.now() - access_date).days
                
                if days_old <= 30:
                    quality_adjustments += 0.15
                elif days_old <= 90:
                    quality_adjustments += 0.10
                elif days_old <= 365:
                    quality_adjustments += 0.05
                else:
                    quality_adjustments -= 0.10
                    
            except ValueError:
                quality_adjustments -= 0.05  # Invalid date format
        
        # Product code presence
        if source_data.get('product_code'):
            quality_adjustments += 0.10
        
        # Screenshot archived
        if source_data.get('screenshot_path'):
            quality_adjustments += 0.05
        
        # Contact information for quotes
        if citation_type == 'direct_quote' and source_data.get('contact_person'):
            quality_adjustments += 0.10
        
        # Data extracted completeness
        data_extracted = source_data.get('data_extracted', {})
        if isinstance(data_extracted, dict) and len(data_extracted) > 0:
            quality_adjustments += 0.05
        
        final_score = min(1.0, max(0.0, base_score + quality_adjustments))
        return round(final_score, 2)
    
    def is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def is_official_domain(self, url: str, company_name: str) -> bool:
        """Check if URL appears to be official company domain"""
        if not url or not company_name:
            return False
        
        try:
            domain = urlparse(url).netloc.lower()
            company_clean = re.sub(r'[^a-zA-Z]', '', company_name.lower())
            
            # Simple check for company name in domain
            return company_clean in domain.replace('.', '').replace('-', '')
        except Exception:
            return False
    
    def validate_citation(self, citation: SourceReference) -> Tuple[bool, List[str]]:
        """
        Validate citation completeness and correctness
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Required fields check
        required_fields = self.config.get('citation_requirements', {}).get('mandatory_fields', [])
        for field in required_fields:
            if not getattr(citation, field, None):
                issues.append(f"Missing required field: {field}")
        
        # URL format validation
        if citation.source_url and not self.is_valid_url(citation.source_url):
            issues.append(f"Invalid URL format: {citation.source_url}")
        
        # Date format validation
        if citation.date_accessed:
            try:
                datetime.strptime(citation.date_accessed, '%Y-%m-%d')
            except ValueError:
                issues.append(f"Invalid date format: {citation.date_accessed} (should be YYYY-MM-DD)")
        
        # Citation type validation
        if citation.citation_type not in self.templates:
            issues.append(f"Unknown citation type: {citation.citation_type}")
        
        # Screenshot path validation
        if citation.screenshot_path:
            screenshot_path = Path(citation.screenshot_path)
            if not screenshot_path.exists():
                issues.append(f"Screenshot file not found: {citation.screenshot_path}")
        
        # Confidence score validation
        if not (0.0 <= citation.confidence_score <= 1.0):
            issues.append(f"Invalid confidence score: {citation.confidence_score} (should be 0.0-1.0)")
        
        return len(issues) == 0, issues
    
    def generate_screenshot_filename(self, supplier: str, product_code: Optional[str] = None,
                                   item_id: Optional[str] = None) -> str:
        """Generate standardized screenshot filename"""
        date_str = datetime.now().strftime('%Y%m%d')
        
        if product_code:
            base_name = f"{supplier}_{product_code}_{date_str}"
        elif item_id:
            base_name = f"{supplier}_{item_id}_{date_str}"
        else:
            # Generate hash from supplier and timestamp for uniqueness
            hash_input = f"{supplier}_{datetime.now().isoformat()}"
            hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:8]
            base_name = f"{supplier}_{hash_suffix}_{date_str}"
        
        # Find next sequence number
        screenshot_dir = self.project_root / 'data' / 'sources' / 'screenshots'
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        sequence = 1
        while (screenshot_dir / f"{base_name}_{sequence:03d}.png").exists():
            sequence += 1
        
        return f"{base_name}_{sequence:03d}.png"
    
    def create_source_documentation_file(self, citation: SourceReference) -> Path:
        """Create markdown documentation file for source"""
        
        # Generate filename
        supplier_clean = re.sub(r'[^a-zA-Z0-9]', '_', citation.company_name.lower())
        date_str = citation.date_accessed.replace('-', '')
        
        category = 'general'
        if citation.item_id:
            # Try to extract category from item_id
            parts = citation.item_id.split('_')
            if len(parts) > 1:
                category = parts[1].lower()
        
        filename = f"{supplier_clean}_{category}_{date_str}.md"
        
        # Create documentation directory
        docs_dir = self.project_root / 'data' / 'sources' / 'documentation'
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        doc_path = docs_dir / filename
        
        # Generate documentation content
        content = self.generate_documentation_content(citation)
        
        with open(doc_path, 'w') as f:
            f.write(content)
        
        return doc_path
    
    def generate_documentation_content(self, citation: SourceReference) -> str:
        """Generate markdown content for source documentation"""
        
        content = []
        content.append(f"# Source Documentation: {citation.company_name}")
        content.append(f"")
        content.append(f"**Date Accessed:** {citation.date_accessed}")
        content.append(f"**Citation Type:** {citation.citation_type}")
        content.append(f"**Confidence Score:** {citation.confidence_score}")
        content.append(f"")
        
        # Source Information
        content.append("## Source Information")
        content.append("")
        content.append(f"**Formatted Citation:**")
        content.append(f"{citation.citation_formatted}")
        content.append("")
        content.append(f"**Source URL:** {citation.source_url}")
        
        if citation.contact_person:
            content.append(f"**Contact Person:** {citation.contact_person}")
        
        if citation.product_code:
            content.append(f"**Product Code:** {citation.product_code}")
        
        if citation.quote_number:
            content.append(f"**Quote Number:** {citation.quote_number}")
        
        content.append("")
        
        # Data Collected
        content.append("## Data Collected")
        content.append("")
        
        if citation.item_id:
            content.append(f"**Item ID:** {citation.item_id}")
        
        if citation.data_extracted:
            content.append("**Extracted Data:**")
            for key, value in citation.data_extracted.items():
                content.append(f"- **{key.title()}:** {value}")
        
        content.append("")
        
        # Validation Notes
        content.append("## Validation Notes")
        content.append("")
        content.append(f"**Verification Status:** {citation.verification_status}")
        
        is_valid, issues = self.validate_citation(citation)
        if is_valid:
            content.append("✅ Citation passes all validation checks")
        else:
            content.append("⚠️ Validation issues found:")
            for issue in issues:
                content.append(f"- {issue}")
        
        content.append("")
        
        # Screenshots/Attachments
        content.append("## Screenshots/Attachments")
        content.append("")
        
        if citation.screenshot_path:
            content.append(f"**Screenshot:** {citation.screenshot_path}")
            
            # Check if file exists
            screenshot_path = Path(citation.screenshot_path)
            if screenshot_path.exists():
                content.append("✅ Screenshot file exists")
            else:
                content.append("❌ Screenshot file not found")
        else:
            content.append("No screenshots archived")
        
        content.append("")
        
        # Follow-up Required
        content.append("## Follow-up Required")
        content.append("")
        
        # Determine follow-up actions based on citation quality
        if citation.confidence_score < 0.6:
            content.append("- Consider finding additional sources to verify data")
        
        if not citation.screenshot_path and citation.citation_type == 'supplier_website':
            content.append("- Archive screenshot of source page")
        
        if citation.verification_status == 'pending':
            content.append("- Verify source accessibility and data accuracy")
        
        # Add date-based follow-ups
        try:
            access_date = datetime.strptime(citation.date_accessed, '%Y-%m-%d')
            days_old = (datetime.now() - access_date).days
            
            if days_old > 90:
                content.append("- Data is getting old, consider refreshing")
            elif days_old > 180:
                content.append("- Data needs to be refreshed from source")
        except ValueError:
            pass
        
        content.append("")
        
        # Additional Notes
        if citation.notes:
            content.append("## Additional Notes")
            content.append("")
            content.append(citation.notes)
            content.append("")
        
        # Footer
        content.append("---")
        content.append("")
        content.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        content.append(f"*Terra35 Vanilla Operations Cost Analysis*")
        
        return '\n'.join(content)
    
    def export_citations_to_csv(self, citations: List[SourceReference], output_path: str):
        """Export citations to CSV format"""
        import csv
        
        with open(output_path, 'w', newline='') as csvfile:
            fieldnames = [
                'item_id', 'citation_type', 'company_name', 'source_url',
                'date_accessed', 'product_code', 'confidence_score',
                'verification_status', 'citation_formatted'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for citation in citations:
                row = {
                    'item_id': citation.item_id or '',
                    'citation_type': citation.citation_type,
                    'company_name': citation.company_name,
                    'source_url': citation.source_url,
                    'date_accessed': citation.date_accessed,
                    'product_code': citation.product_code or '',
                    'confidence_score': citation.confidence_score,
                    'verification_status': citation.verification_status,
                    'citation_formatted': citation.citation_formatted
                }
                writer.writerow(row)

# Example usage and testing
if __name__ == '__main__':
    import json
    
    # Create citation manager
    citation_mgr = CitationManager()
    
    print("Testing Citation Manager...")
    
    # Test supplier website citation
    source_data = {
        'company_name': 'FarmTek',
        'product_name': 'Gothic Arch Greenhouse Kit 12x20',
        'product_code': 'GT-1220',
        'website_name': 'FarmTek.com',
        'source_url': 'https://www.farmtek.com/product/gothic-arch-greenhouse-gt-1220',
        'date_accessed': '2024-12-30',
        'item_id': 'FARMTEK_GT1220',
        'data_extracted': {
            'price': '$2,499.00',
            'unit': 'each',
            'specifications': {
                'size': '12\' x 20\'',
                'covering': '6mm twin-wall polycarbonate'
            }
        }
    }
    
    try:
        citation = citation_mgr.create_citation('supplier_website', source_data)
        print(f"\nGenerated Citation:")
        print(f"Type: {citation.citation_type}")
        print(f"Formatted: {citation.citation_formatted}")
        print(f"Confidence: {citation.confidence_score}")
        
        is_valid, issues = citation_mgr.validate_citation(citation)
        print(f"\nValidation: {'✅ Valid' if is_valid else '❌ Issues found'}")
        if issues:
            for issue in issues:
                print(f"  - {issue}")
        
        # Test documentation generation
        doc_path = citation_mgr.create_source_documentation_file(citation)
        print(f"\nDocumentation created: {doc_path}")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()