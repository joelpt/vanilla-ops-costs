# Configuration Files

This directory contains configuration files that define the structure and standards for Terra35's cost data collection project.

## Files Overview

### database_schema.sql
**Purpose**: Complete SQLite database schema with tables, views, triggers, and initial data.

**Features**:
- Normalized schema with foreign key relationships
- Built-in validation triggers and data integrity constraints
- Performance indexes for common query patterns
- Analysis views for reporting and dashboard generation
- Initial revenue streams and validation rules

### database_schema.json
**Purpose**: JSON-based database schema specification for document-oriented storage and API validation.

**Features**:
- Flexible schema definitions with type validation
- Reference constraints between collections
- Query patterns and aggregation specifications
- Validation constraints and business rules
- Compatible with both document databases and API validation

### cost_category_taxonomy.json
**Purpose**: Comprehensive taxonomy of all cost categories aligned with Terra35's three revenue streams.

**Structure**:
- **Revenue Streams**: Grow & Produce, Partner & Produce, Make & Produce
- **Supporting Operations**: Shared costs across all revenue streams
- **Data Attributes**: Required fields and validation standards

**Based On**: Milestone 0 research findings including:
- Production targets (150 gallons Year 1 extract, 400 gallons total)
- Climate requirements (85% humidity, 80-82°F temperature)
- Equipment needs (150L extraction system, paste production capability)
- Regulatory requirements (USDA Organic, FDA registration)

## Database Initialization

### Quick Start
```bash
# Initialize database with default settings
python scripts/init_database.py

# Recreate database (destroys existing data)
python scripts/init_database.py --recreate

# Use custom database path
python scripts/init_database.py --db-path custom/path/database.db
```

### Database Features
- **SQLite with WAL mode** - Concurrent read access, better performance
- **Foreign key constraints** - Data integrity enforcement
- **Validation triggers** - Automatic data quality checks
- **Analysis views** - Pre-built queries for reporting
- **Performance indexes** - Optimized for common access patterns

## Usage

This configuration serves as the master reference for:
1. **Database schema design** - Defines table structures and relationships
2. **Data collection scripts** - Categorizes scraped and researched data
3. **Validation frameworks** - Ensures consistent data classification
4. **Reporting systems** - Groups costs for analysis and visualization
5. **API development** - Provides schema validation and structure

## Schema Evolution

### Version Management
- All schema changes are versioned and documented
- Migration scripts handle database updates
- Backward compatibility maintained where possible

### Adding New Categories
1. Update `cost_category_taxonomy.json`
2. Update database schema files
3. Run migration script or reinitialize database
4. Update data collection scripts to use new categories

## Data Quality Standards

### Required Fields
- Every cost item must have verifiable source
- Confidence levels: LOW, MEDIUM, HIGH, VERIFIED  
- Timestamps for all data collection activities
- Source URLs and access dates for all external data

### Validation Rules
- **Range checks**: Costs within reasonable bounds
- **Source requirements**: Minimum 1 source, prefer Tier 1
- **Data freshness**: Prefer data < 90 days, maximum 365 days
- **Confidence minimums**: MEDIUM or higher preferred

## Maintenance

- **Weekly**: Review new cost categories discovered during collection
- **Monthly**: Validate taxonomy against actual collected data
- **Quarterly**: Review alignment with PLAN.md tasks and project goals
- **Version control**: All changes committed with detailed messages

---

*Last Updated: December 30, 2024*
*Version: 1.1*