#!/usr/bin/env python3
"""
Terra35 Vanilla Operations Cost Analysis - Utilities Package

Common utilities and helper functions for the cost analysis project.

Available utilities:
- CitationManager: Source citation creation and management
- SourceReference: Standardized source reference data structure

Usage:
    from utils import CitationManager, SourceReference
    
    citation_mgr = CitationManager()
    citation = citation_mgr.create_citation('supplier_website', source_data)
"""

from .citation_manager import CitationManager, SourceReference

__version__ = "1.0.0"
__author__ = "Terra35 Analysis Team"

__all__ = [
    'CitationManager',
    'SourceReference'
]