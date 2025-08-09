#!/usr/bin/env python3
"""
Terra35 Vanilla Operations Cost Analysis - Constants

Centralized constants used throughout the application to avoid magic values
and maintain consistency across modules.
"""

# Database Record Status Values
STATUS_ACTIVE = 'active'
STATUS_DEPRECATED = 'deprecated'
STATUS_PENDING = 'pending'

# Source Company Types
COMPANY_TYPE_SUPPLIER = 'supplier'
COMPANY_TYPE_GOVERNMENT = 'government'
COMPANY_TYPE_INDUSTRY_REPORT = 'industry_report'

# Source Tiers (quality/reliability ranking)
SOURCE_TIER_PRIMARY = 1      # Primary sources (direct suppliers, official sites)
SOURCE_TIER_SECONDARY = 2    # Secondary sources (aggregators, distributors)  
SOURCE_TIER_TERTIARY = 3     # Tertiary sources (forums, estimates)

# Collection Session Milestones
MILESTONE_DATA_COLLECTION = 'data_collection'
MILESTONE_VALIDATION = 'validation'
MILESTONE_ANALYSIS = 'analysis'
MILESTONE_REPORTING = 'reporting'

# Collection Session Status
SESSION_STATUS_IN_PROGRESS = 'in_progress'
SESSION_STATUS_COMPLETED = 'completed'
SESSION_STATUS_FAILED = 'failed'

# Source Reference Types
REFERENCE_TYPE_PRIMARY = 'primary'
REFERENCE_TYPE_SECONDARY = 'secondary'
REFERENCE_TYPE_VALIDATION = 'validation'

# Collection Activity Types
ACTIVITY_TYPE_CREATED = 'created'
ACTIVITY_TYPE_UPDATED = 'updated'
ACTIVITY_TYPE_VALIDATED = 'validated'
ACTIVITY_TYPE_ARCHIVED = 'archived'

# Default Unit Values
DEFAULT_UNIT = 'each'
DEFAULT_CONFIDENCE_LEVEL = 'MEDIUM'

# Database Schema Constants
DEFAULT_EFFECTIVE_DATE = "DATE('now')"
DEFAULT_DATE_ACCESSED = "DATE('now')"