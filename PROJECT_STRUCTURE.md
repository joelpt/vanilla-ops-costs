# Terra35 Vanilla Operations Cost Analysis - Project Structure

## Directory Organization

This project follows a systematic data collection and analysis structure designed for comprehensive cost research.

### 📁 Root Directory Files
- **PLAN.md** - Living implementation plan with task tracking
- **README.md** - Project mission and overview
- **CLAUDE.md** - Implementation guidelines and patterns
- **PROJECT_STRUCTURE.md** - This documentation
- **extract_pptx.py** - PowerPoint content extraction utility

### 📁 Data Management (`data/`)
- **`costs/`** - Structured cost data (JSON/SQLite databases)
  - Primary storage for verified cost information
  - Categorized by revenue stream and cost type
  - Includes confidence levels and validation status

- **`sources/`** - Source reference documentation
  - URLs, timestamps, contact information
  - Screenshot archives for price verification
  - Vendor communication logs

- **`cache/`** - Raw scraped data and temporary files
  - HTML snapshots from supplier websites
  - PDF catalogs and price lists
  - API response caches

- **`raw/`** - Unprocessed research data
  - Initial data collection staging
  - Manual research notes and findings

### 📁 Research Documentation (`research/`)
- **Milestone 0 Research** - Pre-implementation findings
- **Ongoing Research** - Continuous findings and updates
- **Industry Analysis** - Competitive and market research
- **Technical Specifications** - Equipment and process research

### 📁 Code and Automation (`scripts/`)
- **`scrapers/`** - Web scraping tools
  - Supplier-specific scrapers (FarmTek, GrowSpan, etc.)
  - Generic scraper classes and utilities
  - Rate limiting and error handling

- **`analysis/`** - Data processing and analysis
  - Cost calculation utilities
  - Cross-reference validation
  - Report generation tools

- **`validation/`** - Data quality assurance
  - Source verification tools
  - Data consistency checks
  - Confidence level assessment

### 📁 Reporting (`reports/`)
- **`milestones/`** - Milestone completion reports
  - Progress tracking and deliverables
  - Task completion documentation

- **`analysis/`** - Cost analysis outputs
  - Revenue stream cost breakdowns
  - Comparative analysis reports
  - Risk and sensitivity analysis

- **`visualizations/`** - Charts and dashboards
  - Cost trend visualizations
  - Interactive dashboards
  - Executive summary graphics

### 📁 Configuration (`config/`)
- **Database configurations** - SQLite schemas and settings
- **Scraper settings** - Rate limits, user agents, headers
- **API configurations** - Keys and endpoint definitions
- **Validation rules** - Data quality standards

### 📁 Templates (`templates/`)
- **Data structure templates** - JSON/CSV formats
- **Report templates** - Standardized output formats  
- **Documentation templates** - Research and analysis formats

### 📁 Documentation (`docs/`)
- **API documentation** - For any APIs developed
- **Methodology documentation** - Research approaches
- **User guides** - How to use tools and interpret data

---

## File Naming Conventions

### Cost Data Files
- **Format**: `{revenue_stream}_{category}_{date}.json`
- **Example**: `grow_produce_infrastructure_20241230.json`

### Source Documentation
- **Format**: `{supplier}_{product_category}_{date}`
- **Example**: `farmtek_greenhouse_structures_20241230.md`

### Scripts
- **Scrapers**: `scrape_{supplier_name}.py`
- **Analysis**: `analyze_{data_type}.py`
- **Reports**: `generate_{report_type}.py`

### Reports
- **Milestones**: `milestone_{number}_report.md`
- **Analysis**: `{revenue_stream}_cost_analysis.md`

---

## Data Flow Architecture

```
Raw Data Collection → Validation → Structured Storage → Analysis → Reporting
     ↓                   ↓              ↓              ↓          ↓
   cache/            validation/       costs/       analysis/   reports/
```

### 1. Collection Phase
- Web scrapers store raw HTML in `data/cache/`
- Manual research documented in `data/raw/`
- Source metadata captured in `data/sources/`

### 2. Validation Phase
- Scripts in `scripts/validation/` verify data quality
- Cross-reference multiple sources for consistency
- Flag outliers and questionable data points

### 3. Storage Phase
- Validated data stored in structured format in `data/costs/`
- Source references maintained in `data/sources/`
- Database schemas defined in `config/`

### 4. Analysis Phase
- Scripts in `scripts/analysis/` process structured data
- Generate derived metrics and comparisons
- Output analysis reports to `reports/analysis/`

### 5. Reporting Phase
- Executive summaries and visualizations
- Milestone progress reports
- Interactive dashboards for stakeholder review

---

## Git Management

### Repository Structure
- **Main branch**: Production-ready code and documentation
- **Feature branches**: Individual task implementation
- **Research branches**: Ongoing research and experimentation

### Commit Patterns
- **Data**: New cost data collection
- **Code**: Script development and improvements
- **Docs**: Documentation updates and research findings
- **Config**: Configuration and schema changes

---

## Quality Assurance

### Data Integrity
- All cost data must have verifiable sources
- Automated validation checks before storage
- Regular cross-reference verification
- Source freshness monitoring

### Code Quality
- Modular, reusable scraper components
- Error handling and retry logic
- Rate limiting for respectful scraping
- Comprehensive logging and monitoring

### Documentation Standards
- Real-time documentation updates
- Source attribution for all data
- Methodology documentation for reproducibility
- Progress tracking in PLAN.md

---

*Last Updated: December 30, 2024*
*Version: 1.0*
*Status: Milestone 1 Implementation*