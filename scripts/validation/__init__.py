#!/usr/bin/env python3
"""
Terra35 Vanilla Operations Cost Analysis - Validation Package

This package provides comprehensive data validation capabilities for
cost data collection and quality assurance.

Available validators:
- DataValidator: Core validation framework for cost data
- ValidationResult: Individual validation result
- ValidationSummary: Aggregated validation results for items
- ValidationLevel: Severity levels for validation issues

Usage:
    from validation import DataValidator, ValidationLevel
    
    validator = DataValidator()
    summary = validator.validate_item(item_data)
    
    if summary.is_valid():
        print(f"Item {summary.item_id} passed validation")
    else:
        print(f"Item {summary.item_id} has {summary.critical} critical issues")
"""

from .data_validator import (
    DataValidator,
    ValidationResult, 
    ValidationSummary,
    ValidationLevel
)

__version__ = "1.0.0"
__author__ = "Terra35 Analysis Team"

__all__ = [
    'DataValidator',
    'ValidationResult',
    'ValidationSummary', 
    'ValidationLevel'
]