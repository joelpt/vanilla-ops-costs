#!/usr/bin/env python3
"""
Unit tests for citation manager (citation_manager.py)
"""

import pytest
import json
import tempfile
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, mock_open
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.citation_manager import CitationManager, SourceReference


class TestSourceReference:
    """Test suite for SourceReference dataclass"""
    
    def test_source_reference_creation(self):
        """Test creating SourceReference with required fields"""
        ref = SourceReference(
            citation_type="supplier_website",
            citation_formatted="Test Citation",
            source_url="https://example.com",
            company_name="Test Company",
            date_accessed="2024-12-30"
        )
        
        assert ref.citation_type == "supplier_website"
        assert ref.citation_formatted == "Test Citation"
        assert ref.source_url == "https://example.com"
        assert ref.company_name == "Test Company"
        assert ref.date_accessed == "2024-12-30"
        assert ref.verification_status == "pending"
        assert ref.confidence_score == 0.5
        
    def test_source_reference_with_optional_fields(self):
        """Test SourceReference with all optional fields"""
        data_extracted = {"price": "$100.00", "unit": "each"}
        
        ref = SourceReference(
            citation_type="direct_quote",
            citation_formatted="Full Citation",
            source_url="https://supplier.com/quote",
            company_name="Supplier Inc",
            date_accessed="2024-12-30",
            item_id="SUPP_001",
            product_code="PROD-123",
            contact_person="John Doe",
            quote_number="Q2024-001",
            document_title="Price Quote",
            screenshot_path="/path/to/screenshot.png",
            data_extracted=data_extracted,
            verification_status="verified",
            confidence_score=0.9,
            notes="Additional notes"
        )
        
        assert ref.item_id == "SUPP_001"
        assert ref.product_code == "PROD-123"
        assert ref.contact_person == "John Doe"
        assert ref.quote_number == "Q2024-001"
        assert ref.document_title == "Price Quote"
        assert ref.screenshot_path == "/path/to/screenshot.png"
        assert ref.data_extracted == data_extracted
        assert ref.verification_status == "verified"
        assert ref.confidence_score == 0.9
        assert ref.notes == "Additional notes"
        
    def test_source_reference_to_dict(self):
        """Test converting SourceReference to dictionary"""
        ref = SourceReference(
            citation_type="supplier_website",
            citation_formatted="Test Citation",
            source_url="https://example.com",
            company_name="Test Company",
            date_accessed="2024-12-30"
        )
        
        ref_dict = ref.to_dict()
        
        assert isinstance(ref_dict, dict)
        assert ref_dict['citation_type'] == "supplier_website"
        assert ref_dict['citation_formatted'] == "Test Citation"
        assert ref_dict['source_url'] == "https://example.com"


class TestCitationManager:
    """Test suite for CitationManager class"""
    
    def test_citation_manager_initialization_default(self):
        """Test CitationManager initialization with default config"""
        manager = CitationManager()
        
        expected_config_path = str(project_root / 'config' / 'source_citation_format.json')
        assert manager.config_path == expected_config_path
        assert isinstance(manager.config, dict)
        assert isinstance(manager.templates, dict)
        assert isinstance(manager.source_types, dict)
        
    def test_citation_manager_initialization_custom(self, temp_config_files):
        """Test CitationManager initialization with custom config"""
        config_path = str(temp_config_files / 'source_citation_format.json')
        manager = CitationManager(config_path=config_path)
        
        assert manager.config_path == config_path
        assert 'citation_templates' in manager.config
        
    def test_load_citation_config_success(self, sample_citation_config, tmp_path):
        """Test loading citation config successfully"""
        config_file = tmp_path / 'citation_config.json'
        with open(config_file, 'w') as f:
            json.dump(sample_citation_config, f)
            
        manager = CitationManager(config_path=str(config_file))
        
        assert 'citation_templates' in manager.config
        assert 'supplier_website' in manager.templates
        assert 'tier_1_preferred' in manager.source_types
        
    def test_load_citation_config_missing_file(self):
        """Test loading citation config with missing file"""
        manager = CitationManager(config_path='/nonexistent/config.json')
        
        # Should fall back to empty config
        assert manager.config == {}
        assert manager.templates == {}
        assert manager.source_types == {}
        
    def test_load_citation_config_invalid_json(self, tmp_path):
        """Test loading citation config with invalid JSON"""
        config_file = tmp_path / 'invalid_config.json'
        config_file.write_text('invalid json content {')
        
        manager = CitationManager(config_path=str(config_file))
        
        # Should fall back to empty config
        assert manager.config == {}
        
    def test_create_citation_supplier_website(self, sample_citation_config, tmp_path):
        """Test creating supplier website citation"""
        config_file = tmp_path / 'citation_config.json'
        with open(config_file, 'w') as f:
            json.dump(sample_citation_config, f)
            
        manager = CitationManager(config_path=str(config_file))
        
        source_data = {
            'company_name': 'FarmTek',
            'product_name': 'Gothic Arch Greenhouse Kit 12x20',
            'website_name': 'FarmTek.com',
            'source_url': 'https://www.farmtek.com/product/gothic-arch-greenhouse-gt-1220',
            'date_accessed': '2024-12-30',
            'product_code': 'GT-1220'
        }
        
        citation = manager.create_citation('supplier_website', source_data)
        
        assert isinstance(citation, SourceReference)
        assert citation.citation_type == 'supplier_website'
        assert citation.company_name == 'FarmTek'
        assert citation.source_url == source_data['source_url']
        assert citation.date_accessed == '2024-12-30'
        assert citation.product_code == 'GT-1220'
        assert 'FarmTek' in citation.citation_formatted
        assert 'Gothic Arch Greenhouse Kit 12x20' in citation.citation_formatted
        
    def test_create_citation_direct_quote(self, sample_citation_config, tmp_path):
        """Test creating direct quote citation"""
        config_file = tmp_path / 'citation_config.json'
        with open(config_file, 'w') as f:
            json.dump(sample_citation_config, f)
            
        manager = CitationManager(config_path=str(config_file))
        
        source_data = {
            'company_name': 'Supplier Inc',
            'contact_person': 'Jane Smith',
            'quote_number': 'Q2024-001',
            'date_accessed': '2024-12-30',
            'source_url': 'mailto:jane@supplier.com'
        }
        
        citation = manager.create_citation('direct_quote', source_data)
        
        assert citation.citation_type == 'direct_quote'
        assert citation.company_name == 'Supplier Inc'
        assert citation.contact_person == 'Jane Smith'
        assert citation.quote_number == 'Q2024-001'
        assert 'Jane Smith' in citation.citation_formatted
        assert 'Q2024-001' in citation.citation_formatted
        
    def test_create_citation_unknown_type(self, sample_citation_config, tmp_path):
        """Test creating citation with unknown type"""
        config_file = tmp_path / 'citation_config.json'
        with open(config_file, 'w') as f:
            json.dump(sample_citation_config, f)
            
        manager = CitationManager(config_path=str(config_file))
        
        with pytest.raises(ValueError, match="Unknown citation type"):
            manager.create_citation('unknown_type', {})
            
    def test_create_citation_missing_required_fields(self, sample_citation_config, tmp_path):
        """Test creating citation with missing required fields"""
        config_file = tmp_path / 'citation_config.json'
        with open(config_file, 'w') as f:
            json.dump(sample_citation_config, f)
            
        manager = CitationManager(config_path=str(config_file))
        
        incomplete_data = {
            'company_name': 'Test Company',
            # Missing required fields for supplier_website
        }
        
        with pytest.raises(ValueError, match="Missing required fields"):
            manager.create_citation('supplier_website', incomplete_data)
            
    def test_format_citation_string_basic(self):
        """Test basic citation string formatting"""
        manager = CitationManager()
        
        template = "{company_name}. \"{product_name}.\" {website_name}."
        data = {
            'company_name': 'Test Corp',
            'product_name': 'Test Product',
            'website_name': 'TestCorp.com'
        }
        
        result = manager.format_citation_string(template, data)
        expected = 'Test Corp. "Test Product." TestCorp.com.'
        
        assert result == expected
        
    def test_format_citation_string_with_date_formatting(self):
        """Test citation string formatting with date conversion"""
        manager = CitationManager()
        
        template = "Accessed on {date_accessed}."
        data = {'date_accessed': '2024-12-30'}
        
        result = manager.format_citation_string(template, data)
        
        assert 'December 30, 2024' in result
        
    def test_format_citation_string_missing_field(self):
        """Test citation string formatting with missing field"""
        manager = CitationManager()
        
        template = "{company_name}. {missing_field}."
        data = {'company_name': 'Test Corp'}
        
        with pytest.raises(ValueError, match="Missing required field"):
            manager.format_citation_string(template, data)
            
    def test_calculate_confidence_score_tier1(self, sample_citation_config, tmp_path):
        """Test confidence score calculation for tier 1 source"""
        config_file = tmp_path / 'citation_config.json'
        with open(config_file, 'w') as f:
            json.dump(sample_citation_config, f)
            
        manager = CitationManager(config_path=str(config_file))
        
        source_data = {
            'source_url': 'https://supplier.com/product',
            'company_name': 'supplier',
            'date_accessed': datetime.now().strftime('%Y-%m-%d'),  # Recent
            'product_code': 'PROD-123',
            'screenshot_path': '/path/to/screenshot.png'
        }
        
        score = manager.calculate_confidence_score('supplier_website', source_data)
        
        assert 0.8 <= score <= 1.0  # Should be high for tier 1 with good data
        
    def test_calculate_confidence_score_low_quality(self):
        """Test confidence score calculation for low quality data"""
        manager = CitationManager()
        
        # Minimal data, no URL, old date
        source_data = {
            'date_accessed': '2020-01-01',  # Old
            # No URL, product code, etc.
        }
        
        score = manager.calculate_confidence_score('unknown_type', source_data)
        
        assert score < 0.5  # Should be low for poor quality data
        
    def test_calculate_confidence_score_adjustments(self):
        """Test various confidence score adjustments"""
        manager = CitationManager()
        
        base_data = {'date_accessed': '2024-12-30'}
        
        # Test URL quality adjustment
        data_with_url = base_data.copy()
        data_with_url['source_url'] = 'https://example.com'
        score_with_url = manager.calculate_confidence_score('test', data_with_url)
        
        score_without_url = manager.calculate_confidence_score('test', base_data)
        
        assert score_with_url > score_without_url
        
        # Test product code adjustment
        data_with_code = base_data.copy()
        data_with_code['product_code'] = 'PROD123'
        score_with_code = manager.calculate_confidence_score('test', data_with_code)
        
        assert score_with_code > score_without_url
        
    def test_is_valid_url_valid_cases(self):
        """Test URL validation with valid URLs"""
        manager = CitationManager()
        
        valid_urls = [
            'https://example.com',
            'http://supplier.net/product',
            'https://sub.domain.com/path/to/page',
            'https://example.com:8080/page'
        ]
        
        for url in valid_urls:
            assert manager.is_valid_url(url) == True
            
    def test_is_valid_url_invalid_cases(self):
        """Test URL validation with invalid URLs"""
        manager = CitationManager()
        
        invalid_urls = [
            'not-a-url',
            'https://',
            'http:/invalid.com',
            '',
            None
        ]
        
        for url in invalid_urls:
            assert manager.is_valid_url(url) == False
            
    def test_is_official_domain_matches(self):
        """Test official domain checking with matches"""
        manager = CitationManager()
        
        test_cases = [
            ('https://farmtek.com/product', 'FarmTek'),
            ('https://www.growspan.com/page', 'GrowSpan'),
            ('https://supplier-inc.net/', 'Supplier Inc')
        ]
        
        for url, company in test_cases:
            assert manager.is_official_domain(url, company) == True
            
    def test_is_official_domain_no_match(self):
        """Test official domain checking with no matches"""
        manager = CitationManager()
        
        test_cases = [
            ('https://different.com', 'FarmTek'),
            ('https://example.com', ''),
            ('', 'Company'),
            ('invalid-url', 'Company')
        ]
        
        for url, company in test_cases:
            assert manager.is_official_domain(url, company) == False
            
    def test_validate_citation_success(self, sample_citation_config, tmp_path):
        """Test successful citation validation"""
        config_file = tmp_path / 'citation_config.json'
        with open(config_file, 'w') as f:
            json.dump(sample_citation_config, f)
            
        manager = CitationManager(config_path=str(config_file))
        
        citation = SourceReference(
            citation_type="supplier_website",
            citation_formatted="Valid Citation",
            source_url="https://example.com",
            company_name="Test Company",
            date_accessed="2024-12-30",
            confidence_score=0.8
        )
        
        is_valid, issues = manager.validate_citation(citation)
        
        assert is_valid == True
        assert len(issues) == 0
        
    def test_validate_citation_missing_required(self, sample_citation_config, tmp_path):
        """Test citation validation with missing required fields"""
        config_file = tmp_path / 'citation_config.json'
        with open(config_file, 'w') as f:
            json.dump(sample_citation_config, f)
            
        manager = CitationManager(config_path=str(config_file))
        
        citation = SourceReference(
            citation_type="supplier_website",
            citation_formatted="Citation",
            source_url="",  # Missing required field
            company_name="",  # Missing required field
            date_accessed="2024-12-30"
        )
        
        is_valid, issues = manager.validate_citation(citation)
        
        assert is_valid == False
        assert len(issues) >= 2  # Missing required fields
        
    def test_validate_citation_invalid_url(self, sample_citation_config, tmp_path):
        """Test citation validation with invalid URL"""
        config_file = tmp_path / 'citation_config.json'
        with open(config_file, 'w') as f:
            json.dump(sample_citation_config, f)
            
        manager = CitationManager(config_path=str(config_file))
        
        citation = SourceReference(
            citation_type="supplier_website",
            citation_formatted="Citation",
            source_url="invalid-url",
            company_name="Test Company",
            date_accessed="2024-12-30"
        )
        
        is_valid, issues = manager.validate_citation(citation)
        
        assert is_valid == False
        assert any("invalid url format" in issue.lower() for issue in issues)
        
    def test_validate_citation_invalid_date(self, sample_citation_config, tmp_path):
        """Test citation validation with invalid date"""
        config_file = tmp_path / 'citation_config.json'
        with open(config_file, 'w') as f:
            json.dump(sample_citation_config, f)
            
        manager = CitationManager(config_path=str(config_file))
        
        citation = SourceReference(
            citation_type="supplier_website",
            citation_formatted="Citation",
            source_url="https://example.com",
            company_name="Test Company",
            date_accessed="invalid-date"
        )
        
        is_valid, issues = manager.validate_citation(citation)
        
        assert is_valid == False
        assert any("invalid date format" in issue.lower() for issue in issues)
        
    def test_validate_citation_unknown_type(self, sample_citation_config, tmp_path):
        """Test citation validation with unknown citation type"""
        config_file = tmp_path / 'citation_config.json'
        with open(config_file, 'w') as f:
            json.dump(sample_citation_config, f)
            
        manager = CitationManager(config_path=str(config_file))
        
        citation = SourceReference(
            citation_type="unknown_type",
            citation_formatted="Citation",
            source_url="https://example.com",
            company_name="Test Company",
            date_accessed="2024-12-30"
        )
        
        is_valid, issues = manager.validate_citation(citation)
        
        assert is_valid == False
        assert any("unknown citation type" in issue.lower() for issue in issues)
        
    def test_validate_citation_missing_screenshot(self, sample_citation_config, tmp_path):
        """Test citation validation with missing screenshot file"""
        config_file = tmp_path / 'citation_config.json'
        with open(config_file, 'w') as f:
            json.dump(sample_citation_config, f)
            
        manager = CitationManager(config_path=str(config_file))
        
        citation = SourceReference(
            citation_type="supplier_website",
            citation_formatted="Citation",
            source_url="https://example.com",
            company_name="Test Company",
            date_accessed="2024-12-30",
            screenshot_path="/nonexistent/screenshot.png"
        )
        
        is_valid, issues = manager.validate_citation(citation)
        
        assert is_valid == False
        assert any("screenshot file not found" in issue.lower() for issue in issues)
        
    def test_validate_citation_invalid_confidence_score(self, sample_citation_config, tmp_path):
        """Test citation validation with invalid confidence score"""
        config_file = tmp_path / 'citation_config.json'
        with open(config_file, 'w') as f:
            json.dump(sample_citation_config, f)
            
        manager = CitationManager(config_path=str(config_file))
        
        citation = SourceReference(
            citation_type="supplier_website",
            citation_formatted="Citation",
            source_url="https://example.com",
            company_name="Test Company",
            date_accessed="2024-12-30",
            confidence_score=1.5  # Invalid score > 1.0
        )
        
        is_valid, issues = manager.validate_citation(citation)
        
        assert is_valid == False
        assert any("invalid confidence score" in issue.lower() for issue in issues)
        
    def test_generate_screenshot_filename_with_product_code(self):
        """Test screenshot filename generation with product code"""
        manager = CitationManager()
        
        filename = manager.generate_screenshot_filename("FarmTek", product_code="GT-1220")
        
        assert "FarmTek" in filename
        assert "GT-1220" in filename
        assert filename.endswith(".png")
        assert "_001.png" in filename  # Sequence number
        
    def test_generate_screenshot_filename_with_item_id(self):
        """Test screenshot filename generation with item ID"""
        manager = CitationManager()
        
        filename = manager.generate_screenshot_filename("GrowSpan", item_id="GROWSPAN_STRUCT_001")
        
        assert "GrowSpan" in filename
        assert "GROWSPAN_STRUCT_001" in filename
        assert filename.endswith(".png")
        
    def test_generate_screenshot_filename_without_codes(self):
        """Test screenshot filename generation without product code or item ID"""
        manager = CitationManager()
        
        filename = manager.generate_screenshot_filename("TestSupplier")
        
        assert "TestSupplier" in filename
        assert filename.endswith(".png")
        assert len(filename.split('_')) >= 3  # supplier_hash_date_sequence.png
        
    def test_create_source_documentation_file(self, tmp_path):
        """Test creating source documentation file"""
        # Create manager and mock its project_root instance attribute
        manager = CitationManager()
        manager.project_root = tmp_path
        
        citation = SourceReference(
            citation_type="supplier_website",
            citation_formatted="Test Citation",
            source_url="https://example.com",
            company_name="Test Company",
            date_accessed="2024-12-30",
            item_id="TEST_001",
            confidence_score=0.8
        )
        
        doc_path = manager.create_source_documentation_file(citation)
        
        assert doc_path.exists()
        assert doc_path.suffix == '.md'
        
        # Check content
        content = doc_path.read_text()
        assert "Test Company" in content
        assert "2024-12-30" in content
        assert "supplier_website" in content
        assert "0.8" in content
    def test_generate_documentation_content(self):
        """Test documentation content generation"""
        manager = CitationManager()
        
        citation = SourceReference(
            citation_type="supplier_website",
            citation_formatted="Complete Citation",
            source_url="https://example.com/product",
            company_name="Example Corp",
            date_accessed="2024-12-30",
            product_code="EX-001",
            confidence_score=0.9,
            verification_status="verified",
            notes="Test notes"
        )
        
        content = manager.generate_documentation_content(citation)
        
        assert "Source Documentation: Example Corp" in content
        assert "2024-12-30" in content
        assert "supplier_website" in content
        assert "Complete Citation" in content
        assert "https://example.com/product" in content
        assert "EX-001" in content
        assert "Test notes" in content
        assert "verified" in content
        
    def test_export_citations_to_csv(self, tmp_path):
        """Test exporting citations to CSV"""
        manager = CitationManager()
        
        citations = [
            SourceReference(
                citation_type="supplier_website",
                citation_formatted="Citation 1",
                source_url="https://example1.com",
                company_name="Company 1",
                date_accessed="2024-12-30",
                item_id="ITEM_001",
                confidence_score=0.8
            ),
            SourceReference(
                citation_type="direct_quote",
                citation_formatted="Citation 2",
                source_url="https://example2.com",
                company_name="Company 2",
                date_accessed="2024-12-29",
                item_id="ITEM_002",
                confidence_score=0.9
            )
        ]
        
        csv_path = tmp_path / "citations.csv"
        manager.export_citations_to_csv(citations, str(csv_path))
        
        assert csv_path.exists()
        
        # Verify content
        content = csv_path.read_text()
        assert "item_id,citation_type,company_name" in content
        assert "ITEM_001,supplier_website,Company 1" in content
        assert "ITEM_002,direct_quote,Company 2" in content