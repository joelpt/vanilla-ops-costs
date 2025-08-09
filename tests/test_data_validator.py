#!/usr/bin/env python3
"""
Unit tests for data validation framework (data_validator.py)
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.validation.data_validator import (
    DataValidator, ValidationLevel, ValidationResult, ValidationSummary
)


class TestValidationResult:
    """Test suite for ValidationResult dataclass"""
    
    def test_validation_result_creation(self):
        """Test creating ValidationResult"""
        result = ValidationResult(
            rule_name="test_rule",
            level=ValidationLevel.WARNING,
            message="Test warning message",
            field="test_field",
            expected="expected_value",
            actual="actual_value",
            suggestion="Fix the value"
        )
        
        assert result.rule_name == "test_rule"
        assert result.level == ValidationLevel.WARNING
        assert result.message == "Test warning message"
        assert result.field == "test_field"
        assert result.expected == "expected_value"
        assert result.actual == "actual_value"
        assert result.suggestion == "Fix the value"
        
    def test_validation_result_minimal(self):
        """Test creating ValidationResult with minimal fields"""
        result = ValidationResult(
            rule_name="minimal_rule",
            level=ValidationLevel.INFO,
            message="Info message"
        )
        
        assert result.rule_name == "minimal_rule"
        assert result.level == ValidationLevel.INFO
        assert result.message == "Info message"
        assert result.field is None


class TestValidationSummary:
    """Test suite for ValidationSummary dataclass"""
    
    def test_validation_summary_creation(self):
        """Test creating ValidationSummary"""
        results = [
            ValidationResult("rule1", ValidationLevel.INFO, "Info message"),
            ValidationResult("rule2", ValidationLevel.WARNING, "Warning message"),
            ValidationResult("rule3", ValidationLevel.ERROR, "Error message")
        ]
        
        summary = ValidationSummary(
            item_id="TEST_001",
            total_checks=3,
            passed=0,
            warnings=1,
            errors=1,
            critical=0,
            results=results,
            overall_score=0.7,
            confidence_level="MEDIUM"
        )
        
        assert summary.item_id == "TEST_001"
        assert summary.total_checks == 3
        assert summary.warnings == 1
        assert summary.errors == 1
        assert summary.critical == 0
        assert len(summary.results) == 3
        assert summary.overall_score == 0.7
        assert summary.confidence_level == "MEDIUM"
        
    def test_validation_summary_is_valid(self):
        """Test ValidationSummary.is_valid() method"""
        # No critical errors - should be valid
        summary_valid = ValidationSummary(
            item_id="VALID", total_checks=5, passed=3, warnings=2, 
            errors=0, critical=0, results=[], overall_score=0.8, confidence_level="HIGH"
        )
        assert summary_valid.is_valid() == True
        
        # Has critical errors - should be invalid
        summary_invalid = ValidationSummary(
            item_id="INVALID", total_checks=5, passed=2, warnings=1,
            errors=1, critical=1, results=[], overall_score=0.3, confidence_level="LOW"
        )
        assert summary_invalid.is_valid() == False


class TestDataValidator:
    """Test suite for DataValidator class"""
    
    def test_data_validator_initialization_default(self):
        """Test DataValidator initialization with defaults"""
        validator = DataValidator()
        
        assert validator.db_path == str(project_root / 'data' / 'costs' / 'vanilla_costs.db')
        assert validator.config_path == str(project_root / 'config' / 'validation_config.json')
        assert isinstance(validator.config, dict)
        assert isinstance(validator.rules, dict)
        
    def test_data_validator_initialization_custom(self, temp_db, temp_config_files):
        """Test DataValidator initialization with custom paths"""
        config_path = str(temp_config_files / 'validation_config.json')
        
        validator = DataValidator(db_path=temp_db, config_path=config_path)
        
        assert validator.db_path == temp_db
        assert validator.config_path == config_path
        
    def test_load_validation_config_success(self, temp_config_files):
        """Test loading validation config successfully"""
        config_path = str(temp_config_files / 'validation_config.json')
        validator = DataValidator(config_path=config_path)
        
        assert 'data_quality_thresholds' in validator.config
        assert 'price_ranges' in validator.config
        
    def test_load_validation_config_missing_file(self):
        """Test loading validation config with missing file"""
        validator = DataValidator(config_path='/nonexistent/config.json')
        
        # Should fall back to default config
        assert validator.config is not None
        assert 'data_quality_thresholds' in validator.config
        
    def test_get_default_config(self):
        """Test default configuration structure"""
        validator = DataValidator()
        default_config = validator.get_default_config()
        
        required_sections = [
            'data_quality_thresholds', 'price_ranges', 'data_freshness',
            'required_fields', 'confidence_weights'
        ]
        
        for section in required_sections:
            assert section in default_config
            
        assert default_config['version'] == "1.0"
        
    def test_initialize_validation_rules(self):
        """Test validation rules initialization"""
        validator = DataValidator()
        
        expected_rules = [
            'required_fields', 'item_id_format', 'category_exists',
            'price_range', 'price_unit_consistency', 'price_reasonableness',
            'source_required', 'source_url_format', 'data_freshness',
            'specifications_completeness', 'product_code_format',
            'duplicate_detection', 'price_consistency'
        ]
        
        for rule in expected_rules:
            assert rule in validator.rules
            assert callable(validator.rules[rule])
            
    def test_validate_required_fields_success(self, sample_item_data):
        """Test required fields validation success"""
        validator = DataValidator()
        
        results = validator.validate_required_fields(sample_item_data)
        assert len(results) == 0
        
    def test_validate_required_fields_missing(self):
        """Test required fields validation with missing fields"""
        validator = DataValidator()
        
        incomplete_data = {
            "item_id": "",  # Empty
            "item_name": "Test Product",
            # Missing category
        }
        
        results = validator.validate_required_fields(incomplete_data)
        assert len(results) >= 2  # Missing item_id and category
        
        for result in results:
            assert result.level == ValidationLevel.CRITICAL
            assert "required field" in result.message.lower()
            
    def test_validate_item_id_format_valid(self):
        """Test item ID format validation with valid IDs"""
        validator = DataValidator()
        
        valid_ids = ["FARMTEK_GT1220", "SUPPLIER_PRODUCT_123", "ABC_XYZ_999"]
        
        for item_id in valid_ids:
            item_data = {"item_id": item_id}
            result = validator.validate_item_id_format(item_data)
            assert result is None
            
    def test_validate_item_id_format_invalid(self):
        """Test item ID format validation with invalid IDs"""
        validator = DataValidator()
        
        invalid_ids = ["lowercaseid", "spaces in id", "special-chars!", "123startswithnum"]
        
        for item_id in invalid_ids:
            item_data = {"item_id": item_id}
            result = validator.validate_item_id_format(item_data)
            assert result is not None
            assert result.level == ValidationLevel.WARNING
            assert "format" in result.message.lower()
            
    def test_validate_category_exists_valid(self, temp_db):
        """Test category exists validation with valid category"""
        validator = DataValidator(db_path=temp_db)
        
        item_data = {"category": "infrastructure"}
        result = validator.validate_category_exists(item_data)
        assert result is None
        
    def test_validate_category_exists_invalid(self, temp_db):
        """Test category exists validation with invalid category"""
        validator = DataValidator(db_path=temp_db)
        
        item_data = {"category": "nonexistent_category"}
        result = validator.validate_category_exists(item_data)
        assert result is not None
        assert result.level == ValidationLevel.ERROR
        assert "does not exist" in result.message.lower()
        
    def test_validate_price_range_valid(self):
        """Test price range validation with valid prices"""
        validator = DataValidator()
        
        valid_prices = [1.0, 100.0, 5000.0]
        
        for price in valid_prices:
            item_data = {"pricing": {"unit_cost": price}}
            results = validator.validate_price_range(item_data)
            assert len(results) == 0
            
    def test_validate_price_range_invalid(self):
        """Test price range validation with invalid prices"""
        validator = DataValidator()
        
        # Test extremely low price
        item_data_low = {"pricing": {"unit_cost": 0.005}}
        results_low = validator.validate_price_range(item_data_low)
        assert len(results_low) > 0
        assert any("low" in result.message.lower() for result in results_low)
        
        # Test extremely high price
        item_data_high = {"pricing": {"unit_cost": 200000.0}}
        results_high = validator.validate_price_range(item_data_high)
        assert len(results_high) > 0
        assert any("high" in result.message.lower() for result in results_high)
        
    def test_validate_price_unit_consistency_valid(self):
        """Test price unit consistency validation success"""
        validator = DataValidator()
        
        item_data = {
            "pricing": {
                "unit_cost": 100.0,
                "unit": "each"
            }
        }
        
        result = validator.validate_price_unit_consistency(item_data)
        assert result is None
        
    def test_validate_price_unit_consistency_missing_unit(self):
        """Test price unit consistency with missing unit"""
        validator = DataValidator()
        
        item_data = {
            "pricing": {
                "unit_cost": 100.0,
                "unit": None
            }
        }
        
        result = validator.validate_price_unit_consistency(item_data)
        assert result is not None
        assert result.level == ValidationLevel.ERROR
        assert "unit is missing" in result.message.lower()
        
    def test_validate_source_required_success(self, sample_item_data):
        """Test source required validation success"""
        validator = DataValidator()
        
        result = validator.validate_source_required(sample_item_data)
        assert result is None
        
    def test_validate_source_required_missing(self):
        """Test source required validation with missing sources"""
        validator = DataValidator()
        
        item_data = {"sources": []}
        result = validator.validate_source_required(item_data)
        assert result is not None
        assert result.level == ValidationLevel.CRITICAL
        assert "no source" in result.message.lower()
        
    def test_validate_source_url_format_valid(self):
        """Test source URL format validation with valid URLs"""
        validator = DataValidator()
        
        item_data = {
            "sources": [
                {"source_url": "https://example.com/product"},
                {"source_url": "http://supplier.net/item"}
            ]
        }
        
        results = validator.validate_source_url_format(item_data)
        assert len(results) == 0
        
    def test_validate_source_url_format_invalid(self):
        """Test source URL format validation with invalid URLs"""
        validator = DataValidator()
        
        item_data = {
            "sources": [
                {"source_url": "not-a-url"},
                {"source_url": "ftp://invalid.com"}
            ]
        }
        
        results = validator.validate_source_url_format(item_data)
        assert len(results) >= 1
        assert any("invalid format" in result.message.lower() for result in results)
        
    def test_validate_data_freshness_recent(self):
        """Test data freshness validation with recent data"""
        validator = DataValidator()
        
        recent_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        item_data = {
            "sources": [
                {"date_accessed": recent_date}
            ]
        }
        
        results = validator.validate_data_freshness(item_data)
        assert len(results) == 0
        
    def test_validate_data_freshness_old(self):
        """Test data freshness validation with old data"""
        validator = DataValidator()
        
        old_date = (datetime.now() - timedelta(days=400)).strftime('%Y-%m-%d')
        item_data = {
            "sources": [
                {"date_accessed": old_date}
            ]
        }
        
        results = validator.validate_data_freshness(item_data)
        assert len(results) > 0
        assert any("old" in result.message.lower() for result in results)
        
    def test_validate_data_freshness_critical_age(self):
        """Test data freshness validation with critically old data"""
        validator = DataValidator()
        
        critical_old_date = (datetime.now() - timedelta(days=800)).strftime('%Y-%m-%d')
        item_data = {
            "sources": [
                {"date_accessed": critical_old_date}
            ]
        }
        
        results = validator.validate_data_freshness(item_data)
        critical_results = [r for r in results if r.level == ValidationLevel.CRITICAL]
        assert len(critical_results) > 0
        
    def test_validate_data_freshness_missing_date(self):
        """Test data freshness validation with missing date"""
        validator = DataValidator()
        
        item_data = {
            "sources": [
                {}  # Missing date_accessed
            ]
        }
        
        results = validator.validate_data_freshness(item_data)
        assert len(results) > 0
        assert any("missing access date" in result.message.lower() for result in results)
        
    def test_validate_data_freshness_invalid_date(self):
        """Test data freshness validation with invalid date format"""
        validator = DataValidator()
        
        item_data = {
            "sources": [
                {"date_accessed": "invalid-date-format"}
            ]
        }
        
        results = validator.validate_data_freshness(item_data)
        assert len(results) > 0
        assert any("invalid date format" in result.message.lower() for result in results)
        
    def test_validate_specifications_completeness_present(self):
        """Test specifications completeness with present specs"""
        validator = DataValidator()
        
        item_data = {
            "specifications": {
                "material": "steel",
                "size": "10x20"
            }
        }
        
        result = validator.validate_specifications_completeness(item_data)
        assert result is None
        
    def test_validate_specifications_completeness_missing(self):
        """Test specifications completeness with missing specs"""
        validator = DataValidator()
        
        test_cases = [
            {"specifications": None},
            {"specifications": {}},
            {}  # No specifications key
        ]
        
        for item_data in test_cases:
            result = validator.validate_specifications_completeness(item_data)
            assert result is not None
            assert result.level == ValidationLevel.INFO
            assert "no specifications" in result.message.lower()
            
    def test_validate_product_code_format_valid(self):
        """Test product code format validation with valid codes"""
        validator = DataValidator()
        
        item_data = {
            "sources": [
                {"product_code": "ABC-123"},
                {"product_code": "XYZ_456"},
                {"product_code": "PROD789"}
            ]
        }
        
        result = validator.validate_product_code_format(item_data)
        assert result is None
        
    def test_validate_product_code_format_invalid(self):
        """Test product code format validation with invalid codes"""
        validator = DataValidator()
        
        item_data = {
            "sources": [
                {"product_code": "invalid code with spaces"},
                {"product_code": "special@chars!"}
            ]
        }
        
        result = validator.validate_product_code_format(item_data)
        assert result is not None
        assert result.level == ValidationLevel.WARNING
        assert "unexpected characters" in result.message.lower()
        
    def test_calculate_quality_score_high_quality(self, sample_item_data):
        """Test quality score calculation for high quality data"""
        validator = DataValidator()
        
        # Use sample data which should score well
        score = validator.calculate_quality_score(sample_item_data, [])
        assert score >= 0.799  # Should be high quality (allow for floating point precision)
        
    def test_calculate_quality_score_low_quality(self):
        """Test quality score calculation for low quality data"""
        validator = DataValidator()
        
        # Minimal data with no sources
        poor_data = {
            "item_id": "TEST",
            "item_name": "Test",
            "category": "test"
        }
        
        score = validator.calculate_quality_score(poor_data, [])
        assert score < 0.5  # Should be low quality
        
    def test_calculate_quality_score_with_penalties(self, sample_item_data):
        """Test quality score calculation with validation penalties"""
        validator = DataValidator()
        
        # Create some validation issues
        validation_results = [
            ValidationResult("rule1", ValidationLevel.ERROR, "Error message"),
            ValidationResult("rule2", ValidationLevel.CRITICAL, "Critical message")
        ]
        
        score = validator.calculate_quality_score(sample_item_data, validation_results)
        score_no_penalties = validator.calculate_quality_score(sample_item_data, [])
        
        assert score < score_no_penalties  # Score should be reduced by penalties
        
    def test_determine_confidence_level_cases(self):
        """Test confidence level determination for various cases"""
        validator = DataValidator()
        
        # High score, no critical/errors -> should be VERIFIED
        confidence = validator.determine_confidence_level(0.96, critical=0, errors=0)
        assert confidence == "VERIFIED"
        
        # Good score, no critical/errors -> should be HIGH
        confidence = validator.determine_confidence_level(0.88, critical=0, errors=0)
        assert confidence == "HIGH"
        
        # With critical errors -> should be LOW
        confidence = validator.determine_confidence_level(0.90, critical=1, errors=0)
        assert confidence == "LOW"
        
        # With many errors -> should be LOW
        confidence = validator.determine_confidence_level(0.80, critical=0, errors=3)
        assert confidence == "LOW"
        
        # Acceptable score -> should be MEDIUM
        confidence = validator.determine_confidence_level(0.75, critical=0, errors=0)
        assert confidence == "MEDIUM"
        
        # Low score -> should be LOW
        confidence = validator.determine_confidence_level(0.50, critical=0, errors=0)
        assert confidence == "LOW"
        
    def test_validate_item_complete(self, sample_item_data):
        """Test complete item validation"""
        validator = DataValidator()
        
        summary = validator.validate_item(sample_item_data)
        
        assert isinstance(summary, ValidationSummary)
        assert summary.item_id == sample_item_data['item_id']
        assert summary.total_checks > 0
        assert 0.0 <= summary.overall_score <= 1.0
        assert summary.confidence_level in ["LOW", "MEDIUM", "HIGH", "VERIFIED"]
        
    def test_validate_item_with_exception(self):
        """Test item validation when a rule throws exception"""
        validator = DataValidator()
        
        # Mock one of the rules to throw an exception
        original_rule = validator.rules['required_fields']
        validator.rules['required_fields'] = lambda x: (_ for _ in ()).throw(Exception("Test error"))
        
        try:
            summary = validator.validate_item({"item_id": "TEST"})
            
            # Should handle the exception gracefully
            assert isinstance(summary, ValidationSummary)
            assert summary.errors == 0  # Exception gets converted to critical
            assert summary.critical >= 1
            
        finally:
            # Restore original rule
            validator.rules['required_fields'] = original_rule
            
    def test_validate_batch_success(self, sample_item_data):
        """Test batch validation with successful items"""
        validator = DataValidator()
        
        items = [sample_item_data, sample_item_data.copy()]
        items[1]['item_id'] = 'DIFFERENT_ID'
        
        summaries = validator.validate_batch(items)
        
        assert len(summaries) == 2
        for summary in summaries:
            assert isinstance(summary, ValidationSummary)
            
    def test_validate_batch_with_failure(self, sample_item_data):
        """Test batch validation with failing item"""
        validator = DataValidator()
        
        items = [
            sample_item_data,
            {"invalid": "data"}  # This will cause validation to fail
        ]
        
        summaries = validator.validate_batch(items)
        
        assert len(summaries) == 2
        assert summaries[0].errors + summaries[0].critical == 0  # First should be good
        assert summaries[1].critical >= 1  # Second should have issues
        
    def test_save_validation_config(self, tmp_path):
        """Test saving validation configuration"""
        validator = DataValidator()
        config_file = tmp_path / "test_config.json"
        
        test_config = {"test": "data", "version": "2.0"}
        validator.save_validation_config(test_config, str(config_file))
        
        # Verify file was created
        assert config_file.exists()
        
        # Verify content
        with open(config_file, 'r') as f:
            saved_config = json.load(f)
        
        assert saved_config['test'] == 'data'
        assert saved_config['version'] == '2.0'
        assert 'last_updated' in saved_config  # Should be added automatically