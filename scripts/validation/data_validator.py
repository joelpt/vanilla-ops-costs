#!/usr/bin/env python3
"""
Terra35 Vanilla Operations Cost Analysis - Data Validation Framework

This module provides comprehensive data validation for cost data collection,
ensuring data integrity, quality, and consistency across all sources.

The validation framework includes:
- Schema validation for data structure
- Business rule validation for cost data
- Source quality validation
- Data freshness and completeness checks
- Cross-reference validation between sources
"""

import json
import sqlite3
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class ValidationLevel(Enum):
    """Validation severity levels"""
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ValidationResult:
    """Single validation result"""
    rule_name: str
    level: ValidationLevel
    message: str
    field: Optional[str] = None
    expected: Optional[Any] = None
    actual: Optional[Any] = None
    suggestion: Optional[str] = None

@dataclass 
class ValidationSummary:
    """Summary of validation results for an item"""
    item_id: str
    total_checks: int
    passed: int
    warnings: int
    errors: int
    critical: int
    results: List[ValidationResult]
    overall_score: float
    confidence_level: str
    
    def is_valid(self) -> bool:
        """Check if item passes validation (no critical errors)"""
        return self.critical == 0

class DataValidator:
    """
    Comprehensive data validation framework for cost data
    """
    
    def __init__(self, db_path: Optional[str] = None, config_path: Optional[str] = None):
        self.project_root = project_root
        self.db_path = db_path or str(project_root / 'data' / 'costs' / 'vanilla_costs.db')
        self.config_path = config_path or str(project_root / 'config' / 'validation_config.json')
        
        # Load validation configuration
        self.config = self.load_validation_config()
        
        # Initialize validation rules
        self.rules = self.initialize_validation_rules()
    
    def load_validation_config(self) -> Dict[str, Any]:
        """Load validation configuration"""
        if Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load validation config: {e}")
        
        # Return default configuration
        return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Default validation configuration"""
        return {
            "version": "1.0",
            "data_quality_thresholds": {
                "excellent": 0.95,
                "good": 0.85,
                "acceptable": 0.70,
                "poor": 0.50
            },
            "price_ranges": {
                "min_reasonable_cost": 0.01,
                "max_reasonable_cost": 100000.0,
                "suspicious_high_threshold": 50000.0,
                "suspicious_low_threshold": 0.10
            },
            "data_freshness": {
                "max_age_days": 365,
                "preferred_age_days": 90,
                "critical_age_days": 730
            },
            "required_fields": {
                "cost_items": ["item_id", "item_name", "category"],
                "cost_pricing": ["unit_cost", "unit", "effective_date"],
                "source_references": ["source_url", "date_accessed"]
            },
            "confidence_weights": {
                "has_source": 0.25,
                "recent_data": 0.20,
                "complete_fields": 0.20,
                "reasonable_price": 0.15,
                "has_product_code": 0.10,
                "has_specifications": 0.10
            }
        }
    
    def initialize_validation_rules(self) -> Dict[str, callable]:
        """Initialize all validation rules"""
        return {
            # Required field validation
            'required_fields': self.validate_required_fields,
            'item_id_format': self.validate_item_id_format,
            'category_exists': self.validate_category_exists,
            
            # Price validation
            'price_range': self.validate_price_range,
            'price_unit_consistency': self.validate_price_unit_consistency,
            'price_reasonableness': self.validate_price_reasonableness,
            
            # Source validation
            'source_required': self.validate_source_required,
            'source_url_format': self.validate_source_url_format,
            'source_accessibility': self.validate_source_accessibility,
            'data_freshness': self.validate_data_freshness,
            
            # Data completeness
            'specifications_completeness': self.validate_specifications_completeness,
            'product_code_format': self.validate_product_code_format,
            
            # Cross-validation
            'duplicate_detection': self.validate_duplicate_detection,
            'price_consistency': self.validate_price_consistency,
        }
    
    def validate_item(self, item_data: Dict[str, Any]) -> ValidationSummary:
        """
        Validate a complete cost item with all associated data
        """
        results = []
        item_id = item_data.get('item_id', 'UNKNOWN')
        
        # Run all validation rules
        for rule_name, rule_func in self.rules.items():
            try:
                rule_results = rule_func(item_data)
                if isinstance(rule_results, list):
                    results.extend(rule_results)
                elif rule_results:
                    results.append(rule_results)
            except Exception as e:
                results.append(ValidationResult(
                    rule_name=rule_name,
                    level=ValidationLevel.CRITICAL,
                    message=f"Validation rule failed: {str(e)}",
                    field="validation_system"
                ))
        
        # Calculate summary statistics
        total_checks = len(results)
        warnings = sum(1 for r in results if r.level == ValidationLevel.WARNING)
        errors = sum(1 for r in results if r.level == ValidationLevel.ERROR)
        critical = sum(1 for r in results if r.level == ValidationLevel.CRITICAL)
        passed = total_checks - warnings - errors - critical
        
        # Calculate overall score
        overall_score = self.calculate_quality_score(item_data, results)
        
        # Determine confidence level
        confidence_level = self.determine_confidence_level(overall_score, critical, errors)
        
        return ValidationSummary(
            item_id=item_id,
            total_checks=total_checks,
            passed=passed,
            warnings=warnings,
            errors=errors,
            critical=critical,
            results=results,
            overall_score=overall_score,
            confidence_level=confidence_level
        )
    
    # Validation Rules Implementation
    
    def validate_required_fields(self, item_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate required fields are present"""
        results = []
        
        required_fields = self.config['required_fields']['cost_items']
        
        for field in required_fields:
            if not item_data.get(field):
                results.append(ValidationResult(
                    rule_name='required_fields',
                    level=ValidationLevel.CRITICAL,
                    message=f"Required field '{field}' is missing or empty",
                    field=field,
                    suggestion=f"Provide a valid value for {field}"
                ))
        
        return results
    
    def validate_item_id_format(self, item_data: Dict[str, Any]) -> Optional[ValidationResult]:
        """Validate item ID format"""
        item_id = item_data.get('item_id')
        if not item_id:
            return None
        
        # Expected format: SUPPLIER_PRODUCT_CODE or SUPPLIER_NAME_HASH
        if not re.match(r'^[A-Z]+_[A-Z0-9_]+$', item_id):
            return ValidationResult(
                rule_name='item_id_format',
                level=ValidationLevel.WARNING,
                message="Item ID format doesn't follow convention",
                field='item_id',
                actual=item_id,
                expected="SUPPLIER_PRODUCT_CODE format",
                suggestion="Use format like 'FARMTEK_GH123' or 'SUPPLIER_PRODUCT_CODE'"
            )
        
        return None
    
    def validate_category_exists(self, item_data: Dict[str, Any]) -> Optional[ValidationResult]:
        """Validate category exists in taxonomy"""
        category = item_data.get('category')
        if not category:
            return None
        
        # Check against database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM cost_categories WHERE code = ?",
                    (category,)
                )
                if cursor.fetchone()[0] == 0:
                    return ValidationResult(
                        rule_name='category_exists',
                        level=ValidationLevel.ERROR,
                        message="Category does not exist in taxonomy",
                        field='category',
                        actual=category,
                        suggestion="Use valid category from cost_category_taxonomy.json"
                    )
        except sqlite3.Error:
            pass  # Database not available, skip check
        
        return None
    
    def validate_price_range(self, item_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate price is within reasonable ranges"""
        results = []
        
        pricing_data = item_data.get('pricing', {})
        if not isinstance(pricing_data, dict):
            return results
        
        unit_cost = pricing_data.get('unit_cost')
        if unit_cost is None:
            return results
        
        min_cost = self.config['price_ranges']['min_reasonable_cost']
        max_cost = self.config['price_ranges']['max_reasonable_cost']
        
        if unit_cost < min_cost:
            results.append(ValidationResult(
                rule_name='price_range',
                level=ValidationLevel.WARNING,
                message=f"Unit cost seems unusually low: ${unit_cost}",
                field='unit_cost',
                actual=unit_cost,
                expected=f">= ${min_cost}",
                suggestion="Verify price is correct or check units"
            ))
        
        elif unit_cost > max_cost:
            results.append(ValidationResult(
                rule_name='price_range',
                level=ValidationLevel.ERROR,
                message=f"Unit cost seems unreasonably high: ${unit_cost}",
                field='unit_cost', 
                actual=unit_cost,
                expected=f"<= ${max_cost}",
                suggestion="Verify price is correct or check for data entry error"
            ))
        
        # Check for suspicious prices
        suspicious_high = self.config['price_ranges']['suspicious_high_threshold']
        suspicious_low = self.config['price_ranges']['suspicious_low_threshold']
        
        if unit_cost > suspicious_high:
            results.append(ValidationResult(
                rule_name='price_range',
                level=ValidationLevel.WARNING,
                message=f"Price is unusually high and should be verified: ${unit_cost}",
                field='unit_cost',
                actual=unit_cost,
                suggestion="Double-check source and verify this is correct"
            ))
        
        elif unit_cost < suspicious_low:
            results.append(ValidationResult(
                rule_name='price_range', 
                level=ValidationLevel.WARNING,
                message=f"Price is unusually low and should be verified: ${unit_cost}",
                field='unit_cost',
                actual=unit_cost,
                suggestion="Verify units and source accuracy"
            ))
        
        return results
    
    def validate_price_unit_consistency(self, item_data: Dict[str, Any]) -> Optional[ValidationResult]:
        """Validate price and unit are consistent"""
        pricing_data = item_data.get('pricing', {})
        if not isinstance(pricing_data, dict):
            return None
        
        unit_cost = pricing_data.get('unit_cost')
        unit = pricing_data.get('unit')
        
        if unit_cost is not None and not unit:
            return ValidationResult(
                rule_name='price_unit_consistency',
                level=ValidationLevel.ERROR,
                message="Unit cost provided but unit is missing",
                field='unit',
                suggestion="Specify the unit (e.g., 'each', 'per_sq_ft', 'per_gallon')"
            )
        
        return None
    
    def validate_price_reasonableness(self, item_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate price reasonableness for item type"""
        results = []
        
        pricing_data = item_data.get('pricing', {})
        unit_cost = pricing_data.get('unit_cost')
        unit = pricing_data.get('unit', '')
        category = item_data.get('category', '')
        
        if unit_cost is None:
            return results
        
        # Category-specific reasonableness checks
        category_expectations = {
            'infrastructure': {
                'per_sq_ft': (5.0, 500.0),
                'each': (100.0, 50000.0)
            },
            'operational_costs': {
                'per_pound': (0.50, 100.0),
                'per_gallon': (1.0, 200.0)
            }
        }
        
        if category in category_expectations and unit in category_expectations[category]:
            min_expected, max_expected = category_expectations[category][unit]
            
            if unit_cost < min_expected or unit_cost > max_expected:
                results.append(ValidationResult(
                    rule_name='price_reasonableness',
                    level=ValidationLevel.WARNING,
                    message=f"Price ${unit_cost}/{unit} seems unusual for {category} items",
                    field='unit_cost',
                    actual=unit_cost,
                    expected=f"${min_expected}-${max_expected}/{unit}",
                    suggestion=f"Typical {category} items cost ${min_expected}-${max_expected}/{unit}"
                ))
        
        return results
    
    def validate_source_required(self, item_data: Dict[str, Any]) -> Optional[ValidationResult]:
        """Validate source information is provided"""
        sources = item_data.get('sources', [])
        if not sources:
            return ValidationResult(
                rule_name='source_required',
                level=ValidationLevel.CRITICAL,
                message="No source information provided",
                field='sources',
                suggestion="Add at least one source reference with URL and access date"
            )
        
        return None
    
    def validate_source_url_format(self, item_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate source URL formats"""
        results = []
        
        sources = item_data.get('sources', [])
        for i, source in enumerate(sources):
            if not isinstance(source, dict):
                continue
                
            url = source.get('source_url')
            if url and not re.match(r'^https?://.+', url):
                results.append(ValidationResult(
                    rule_name='source_url_format',
                    level=ValidationLevel.ERROR,
                    message=f"Source URL {i+1} has invalid format",
                    field=f'sources[{i}].source_url',
                    actual=url,
                    expected="Valid HTTP/HTTPS URL",
                    suggestion="Ensure URL starts with http:// or https://"
                ))
        
        return results
    
    def validate_source_accessibility(self, item_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate source URLs are accessible (basic check)"""
        # Note: This is a placeholder for actual URL accessibility testing
        # In production, this would make HTTP requests to verify URLs
        return []
    
    def validate_data_freshness(self, item_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate data freshness"""
        results = []
        
        sources = item_data.get('sources', [])
        max_age = self.config['data_freshness']['max_age_days']
        preferred_age = self.config['data_freshness']['preferred_age_days']
        critical_age = self.config['data_freshness']['critical_age_days']
        
        for i, source in enumerate(sources):
            if not isinstance(source, dict):
                continue
                
            date_accessed = source.get('date_accessed')
            if not date_accessed:
                results.append(ValidationResult(
                    rule_name='data_freshness',
                    level=ValidationLevel.WARNING,
                    message=f"Source {i+1} missing access date",
                    field=f'sources[{i}].date_accessed',
                    suggestion="Record when the data was accessed"
                ))
                continue
            
            try:
                access_date = datetime.fromisoformat(date_accessed.replace('Z', '+00:00'))
                age_days = (datetime.now() - access_date.replace(tzinfo=None)).days
                
                if age_days > critical_age:
                    results.append(ValidationResult(
                        rule_name='data_freshness',
                        level=ValidationLevel.CRITICAL,
                        message=f"Data is critically old ({age_days} days)",
                        field=f'sources[{i}].date_accessed',
                        actual=f"{age_days} days old",
                        expected=f"< {critical_age} days",
                        suggestion="Data needs to be refreshed from source"
                    ))
                elif age_days > max_age:
                    results.append(ValidationResult(
                        rule_name='data_freshness',
                        level=ValidationLevel.ERROR,
                        message=f"Data is too old ({age_days} days)",
                        field=f'sources[{i}].date_accessed',
                        actual=f"{age_days} days old",
                        expected=f"< {max_age} days",
                        suggestion="Consider refreshing data from source"
                    ))
                elif age_days > preferred_age:
                    results.append(ValidationResult(
                        rule_name='data_freshness',
                        level=ValidationLevel.WARNING,
                        message=f"Data is getting old ({age_days} days)",
                        field=f'sources[{i}].date_accessed',
                        actual=f"{age_days} days old",
                        expected=f"< {preferred_age} days preferred",
                        suggestion="Consider refreshing data soon"
                    ))
                    
            except (ValueError, TypeError):
                results.append(ValidationResult(
                    rule_name='data_freshness',
                    level=ValidationLevel.ERROR,
                    message=f"Source {i+1} has invalid date format",
                    field=f'sources[{i}].date_accessed',
                    actual=date_accessed,
                    expected="ISO format date",
                    suggestion="Use ISO format: YYYY-MM-DD"
                ))
        
        return results
    
    def validate_specifications_completeness(self, item_data: Dict[str, Any]) -> Optional[ValidationResult]:
        """Validate completeness of specifications"""
        specs = item_data.get('specifications')
        
        if not specs or not isinstance(specs, dict) or len(specs) == 0:
            return ValidationResult(
                rule_name='specifications_completeness',
                level=ValidationLevel.INFO,
                message="No specifications provided",
                field='specifications',
                suggestion="Consider adding relevant specifications (dimensions, materials, etc.)"
            )
        
        return None
    
    def validate_product_code_format(self, item_data: Dict[str, Any]) -> Optional[ValidationResult]:
        """Validate product code format if provided"""
        sources = item_data.get('sources', [])
        
        for source in sources:
            if not isinstance(source, dict):
                continue
                
            product_code = source.get('product_code')
            if product_code and not re.match(r'^[A-Z0-9-_]+$', product_code):
                return ValidationResult(
                    rule_name='product_code_format',
                    level=ValidationLevel.WARNING,
                    message="Product code contains unexpected characters",
                    field='product_code',
                    actual=product_code,
                    expected="Alphanumeric with hyphens/underscores",
                    suggestion="Verify product code format with supplier"
                )
        
        return None
    
    def validate_duplicate_detection(self, item_data: Dict[str, Any]) -> List[ValidationResult]:
        """Detect potential duplicates"""
        # This would query the database to find similar items
        # Placeholder implementation
        return []
    
    def validate_price_consistency(self, item_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate price consistency across sources"""
        # This would compare prices from multiple sources for the same item
        # Placeholder implementation
        return []
    
    def calculate_quality_score(self, item_data: Dict[str, Any], results: List[ValidationResult]) -> float:
        """Calculate overall data quality score (0.0 to 1.0)"""
        weights = self.config['confidence_weights']
        score = 0.0
        
        # Source quality
        sources = item_data.get('sources', [])
        if sources:
            score += weights['has_source']
            
            # Check for recent data
            for source in sources:
                if isinstance(source, dict):
                    date_accessed = source.get('date_accessed')
                    if date_accessed:
                        try:
                            access_date = datetime.fromisoformat(date_accessed.replace('Z', '+00:00'))
                            age_days = (datetime.now() - access_date.replace(tzinfo=None)).days
                            if age_days <= self.config['data_freshness']['preferred_age_days']:
                                score += weights['recent_data']
                                break
                        except (ValueError, TypeError):
                            pass
        
        # Field completeness
        required_fields = ['item_id', 'item_name', 'category']
        complete_fields = sum(1 for field in required_fields if item_data.get(field))
        if complete_fields == len(required_fields):
            score += weights['complete_fields']
        
        # Price reasonableness
        pricing = item_data.get('pricing', {})
        unit_cost = pricing.get('unit_cost')
        if unit_cost and 0.01 <= unit_cost <= 100000:
            score += weights['reasonable_price']
        
        # Product code presence
        for source in sources:
            if isinstance(source, dict) and source.get('product_code'):
                score += weights['has_product_code']
                break
        
        # Specifications presence
        specs = item_data.get('specifications')
        if specs and isinstance(specs, dict) and len(specs) > 0:
            score += weights['has_specifications']
        
        # Reduce score for validation issues
        error_penalty = 0.05 * sum(1 for r in results if r.level == ValidationLevel.ERROR)
        critical_penalty = 0.10 * sum(1 for r in results if r.level == ValidationLevel.CRITICAL)
        
        final_score = max(0.0, min(1.0, score - error_penalty - critical_penalty))
        
        return final_score
    
    def determine_confidence_level(self, score: float, critical: int, errors: int) -> str:
        """Determine confidence level based on score and issues"""
        if critical > 0:
            return "LOW"
        elif errors > 2:
            return "LOW"
        elif score >= self.config['data_quality_thresholds']['excellent']:
            return "VERIFIED"
        elif score >= self.config['data_quality_thresholds']['good']:
            return "HIGH"
        elif score >= self.config['data_quality_thresholds']['acceptable']:
            return "MEDIUM"
        else:
            return "LOW"
    
    def validate_batch(self, items: List[Dict[str, Any]]) -> List[ValidationSummary]:
        """Validate a batch of items"""
        results = []
        
        for item in items:
            try:
                summary = self.validate_item(item)
                results.append(summary)
            except Exception as e:
                # Create error summary for failed validation
                item_id = item.get('item_id', 'UNKNOWN')
                error_result = ValidationResult(
                    rule_name='validation_system',
                    level=ValidationLevel.CRITICAL,
                    message=f"Validation failed: {str(e)}",
                    field="system"
                )
                
                results.append(ValidationSummary(
                    item_id=item_id,
                    total_checks=1,
                    passed=0,
                    warnings=0,
                    errors=0,
                    critical=1,
                    results=[error_result],
                    overall_score=0.0,
                    confidence_level="LOW"
                ))
        
        return results
    
    def save_validation_config(self, config: Optional[Dict[str, Any]] = None, path: Optional[str] = None):
        """Save validation configuration to file"""
        config_to_save = config or self.config
        
        # Add timestamp if not present
        if isinstance(config_to_save, dict):
            config_to_save = config_to_save.copy()
            if 'last_updated' not in config_to_save:
                from datetime import datetime
                config_to_save['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        config_path = Path(path or self.config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config_to_save, f, indent=2, sort_keys=True)