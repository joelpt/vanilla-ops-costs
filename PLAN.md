# Terra35 Vanilla Operations Cost Analysis - Implementation Plan

## Project Overview

This project aims to produce a comprehensive operational cost analysis for Terra35's three proposed vanilla farming revenue streams. The deliverable will be a detailed database of goods and services with actual costs, source references, and supporting documentation to enable financial modeling and investment planning.

### Core Objective
Create a data-driven cost model with verifiable sources for:
1. **Grow and Produce**: Indoor greenhouse vanilla cultivation (5000 sq ft baseline, Oregon City location, 85°F climate control, traditional bench system, Grade A vanilla for fermentation-based curing)
2. **Partner and Produce**: Private/white label extract production (processing service fees for 100+ gallon bulk orders with identified partners: Loran/Lorann, Cooks, Lochhead)
3. **Make & Produce**: Cell agriculture lab-grown vanilla (partnership with Rheaplant for R&D → Scale-up → Production phases)

### Key Deliverables
- Structured cost database (JSON/SQLite) with all operational expenses
- Source reference documentation with timestamps and URLs
- Python scripts for data collection and updates
- Interactive cost analysis dashboard
- Comprehensive documentation of assumptions and methodologies

## 🚨 CRITICAL DATA INTEGRITY RULE 🚨

**MANDATORY REQUIREMENT**: All data and numbers used in the produced documentation/data MUST be real data derived from actual legitimate relevant online sources.

**ABSOLUTELY FORBIDDEN**:
- ❌ NO SYNTHETIC DATA
- ❌ NO MADE-UP NUMBERS
- ❌ NO ESTIMATES WITHOUT REAL SOURCE BASIS  
- ❌ NO PLACEHOLDER VALUES

**This must be strictly enforced! Every single cost figure must trace back to a real, verifiable source.**

## High Level Implementation Plan

### Phase 0: Pre-Implementation Research (Before Week 1)
- Complete critical research requirements that will inform all subsequent cost analysis
- Validate key assumptions about production parameters and regulatory requirements
- Establish baseline production targets for accurate equipment sizing and operational planning

### Phase 1: Infrastructure Setup (Week 1)
- Design cost category taxonomy aligned with Terra35's system architecture
- Create database schema for cost data storage
- Develop web scraping framework using Beautiful Soup/Selenium
- Set up project structure and version control

### Phase 2: Data Collection (Weeks 2-6)
- Execute systematic cost research for each revenue stream
- Implement web scrapers for supplier websites
- Integrate APIs for commodity/utility pricing
- Conduct manual research for proprietary/complex items
- Document all sources with timestamps

### Phase 3: Analysis & Documentation (Weeks 6-7)
- Validate and cross-reference all collected data
- Calculate derived metrics (per sq ft, per kg, monthly rates)
- Create visualizations and analysis reports
- Document assumptions and confidence levels

### Phase 4: Maintenance & Updates (Week 8+)
- Build automated update mechanisms
- Create monitoring dashboards
- Establish data refresh protocols
- Prepare handoff documentation

## Scope

### In Scope
**Revenue Stream 1: Grow & Produce**
- Greenhouse infrastructure (traditional bench system, trellis systems for vanilla vines, irrigation, 85°F climate control)
- Curing facility (fermentation-based chambers, dehydration equipment for Grade A vanilla)
- Extraction facility (self-owned ethanol and water-based processing equipment, no CO2 extraction)
- Monthly utilities (electricity, water, HVAC) with Oregon City rates plus renewable energy premium research
- Growing supplies (substrate, fertilizer, nutrients including earthworm castings)
- Labor costs (100% contractor-based for cultivation, curing, and extraction)

**Revenue Stream 2: Partner & Produce**
- Vanilla bean sourcing (both direct from farms and through brokers, multiple origins with price ranges)
- Partner processing service fees (outsourced extraction with Loran/Lorann, Cooks, Lochhead - bulk pricing starts at 100 gallons)

**Revenue Stream 3: Make & Produce (Cell Agriculture Service Partnership with Rheaplant)**
- Research & Development phase: Service fees paid to Rheaplant for vanilla development, substrate/growth materials costs
- Operational scale-up phase: Service fees for scaled production capacity at Rheaplant facility
- Production operations phase: Per-batch service fees paid to Rheaplant for vanilla production (100% quality, high yield target)

**Supporting Operations**
- Marketing, PR, and communications services
- Regulatory compliance and certifications (FDA, USDA Organic)
- Business insurance (product liability, general)
- Legal and accounting services
- Distribution and packaging

### Out of Scope
- Land acquisition or building purchase costs
- IoT sensor technology (already in place per README)
- Detailed financial modeling (this project provides inputs only)
- Market demand analysis
- Competitive pricing strategy

### Geographic Focus
- Primary: Oregon City, Oregon (confirmed location)
- Utility rates: Oregon City municipal utilities
- Regulatory: Oregon state requirements plus federal (FDA, USDA)
- Founder travel: Seattle-Portland corridor (quarterly), Florida/Hawaii provider relationships (1-2 annual trips)

## Open Questions

### Technical Specifications
1. **USDA Organic Certification**: RESEARCH REQUIRED - Comprehensive research on specific timelines and requirements for certification from first harvest
2. **Greenhouse Humidity**: VALIDATE ASSUMPTION - User believes 85% humidity at 85°F, requires validation against PowerPoint and online vanilla cultivation sources

### Partnership Structure  
3. **Cell Agriculture Lab**: ✓ ANSWERED - Rheaplant operates as service provider with Terra35 paying for production services
4. **Processing Partner Pricing**: RESEARCH REQUIRED - Detailed service fee structures for Loran/Lorann, Cooks, and Lochhead beyond the 100-gallon bulk threshold

### Circular Economy Integration
5. **Water Recycling Systems**: RESEARCH REQUIRED - Specific technologies and costs for achieving near 100% water recycling within reason
6. **Waste Revenue Quantification**: RESEARCH REQUIRED - Realistic revenue projections for cuttings, organic matter, and heat recovery waste streams
7. **Renewable Energy Premium**: RESEARCH REQUIRED - Oregon City's specific premium costs for utility-sourced renewable energy

### Financial Assumptions
8. **Price Volatility Analysis**: ✓ ANSWERED - Use min/max/median ranges when appropriate, focus on costs not sales, avoid excessive complexity
9. **Year 1 Production Volume**: RESEARCH REQUIRED - Study existing vanilla providers to determine realistic mid-range production targets, focusing on ethanol extraction and standard vanilla paste creation processes

### Regulatory & Compliance
10. **FDA Food Facility**: RESEARCH REQUIRED - Specific registration costs and requirements for FDA food facility status
11. **Oregon State Licensing**: RESEARCH REQUIRED - Specific business license requirements and costs for vanilla cultivation and processing in Oregon

### Academic Research
12. **Research Grant Dependencies**: ✓ ANSWERED - If grants not secured, no university engagement; only free academic consultation for expertise

## Research Requirements Summary

### Immediate Research Needed (Before Full Implementation):
1. **USDA Organic Certification** - Timeline and cost requirements from first harvest
2. **Greenhouse Humidity Validation** - Verify 85% humidity at 85°F assumption for vanilla cultivation
3. **Year 1 Production Volume** - Study existing vanilla extractors to determine realistic mid-range targets for ethanol extraction and vanilla paste

### Ongoing Research During Implementation:
4. **Processing Partner Pricing** - Detailed fee structures for Loran/Lorann, Cooks, Lochhead beyond 100-gallon threshold
5. **Water Recycling Systems** - Technologies and costs for near 100% water recycling
6. **Waste Revenue Streams** - Realistic projections for cuttings, organic matter, heat recovery revenue
7. **Oregon City Renewable Energy** - Premium costs for utility-sourced renewable energy
8. **FDA Food Facility Registration** - Specific costs and requirements
9. **Oregon State Business Licensing** - Requirements and costs for vanilla cultivation and processing
## Task List

### Milestone 0: Pre-Implementation Research (Before Week 1) - ✅ COMPLETED
#### Critical Research Requirements
- [x] **COMPLETED** - 0.1 Research USDA Organic certification timeline and cost requirements from first harvest (See: research/usda_organic_certification_research.md)
- [x] **COMPLETED** - 0.2 Validate 85% humidity at 85°F assumption for vanilla cultivation (See: research/vanilla_humidity_temperature_validation.md)
- [x] **COMPLETED** - 0.3 Study existing vanilla extractors to determine realistic Year 1 production targets for ethanol extraction (See: research/vanilla_extraction_production_targets.md)
- [x] **COMPLETED** - 0.4 Research standard vanilla paste creation processes and equipment requirements (See: research/vanilla_paste_production_processes.md)
- [x] **COMPLETED** - 0.5 Investigate mid-range vanilla extractor operations for baseline production volumes (See: research/mid_range_vanilla_operations_analysis.md)

### Milestone 1: Infrastructure Setup (Week 1) - IN PROGRESS
- [x] **COMPLETED** - 1.1 Create project directory structure (See: PROJECT_STRUCTURE.md)
- [x] **COMPLETED** - 1.2 Design cost category taxonomy (See: config/cost_category_taxonomy.json)
- [x] **COMPLETED** - 1.3 Build database schema (SQLite/JSON) (See: config/database_schema.sql, config/database_schema.json, scripts/init_database.py)
- [x] **COMPLETED** - 1.4 Develop base scraper class (See: scripts/scrapers/base_scraper.py, scripts/scrapers/farmtek_scraper.py, scripts/scrapers/scraper_utils.py)
- [x] **COMPLETED** - 1.5 Set up data validation framework (See: scripts/validation/data_validator.py, scripts/validation/validation_runner.py, config/validation_config.json)
- [x] **COMPLETED** - 1.6 Create source citation format (See: config/source_citation_format.json, scripts/utils/citation_manager.py, templates/source_reference_template.md)
- [ ] 1.7 Initialize Git repository

### Milestone 2: Grow & Produce Costs (Weeks 2-4)
#### Infrastructure Costs
- [ ] 2.1 Research greenhouse structures (FarmTek, GrowSpan, Stuppy)
- [ ] 2.2 Price benching/racking systems
- [ ] 2.3 Investigate trellis systems for vanilla vines
- [ ] 2.4 Cost irrigation/fertigation equipment
- [ ] 2.5 Research climate control systems (HVAC, fans, shade cloth)
- [ ] 2.6 Price supplemental lighting if needed

#### Curing Facility
- [ ] 2.7 Research curing chamber systems (fermentation, sweating, drying)
- [ ] 2.8 Price dehydration equipment for flavor development
- [ ] 2.9 Cost temperature/humidity control for curing process
- [ ] 2.10 Investigate packaging equipment for cured beans

#### Extraction Facility (Self-Owned)
- [ ] 2.11 Research extraction equipment (ethanol and water-based methods only, no CO2 extraction)
- [ ] 2.12 Price distillation and concentration equipment for ethanol/water extraction
- [ ] 2.13 Cost extraction facility infrastructure requirements for ethanol/water methods
- [ ] 2.14 Investigate ethanol recovery systems (no CO2 solvent recovery needed)
- [ ] 2.15 Price quality control and testing equipment for ethanol/water-based extracts

#### Operational Costs
- [ ] 2.16 Calculate electricity usage and rates (Oregon City municipal utilities for 85°F climate control)
- [ ] 2.17 Estimate water consumption and costs (Oregon City rates with near 100% recycling targets)
- [ ] 2.18 Research fertilizer/nutrient programs (including earthworm castings, contractor-applied)
- [ ] 2.19 Price growing media/substrate for traditional bench system
- [ ] 2.20 Estimate contractor labor requirements and costs (no full-time employees)

#### Circular Economy Systems (Per Slide 9, 12)
- [ ] 2.21 Research water recycling systems for near 100% water recovery
- [ ] 2.22 Price waste-to-revenue processing equipment for cuttings, organic matter, heat recovery
- [ ] 2.23 Cost organic waste recycling partnerships

#### Renewable Energy Options
- [ ] 2.24 Research Oregon City utility renewable energy premium costs
- [ ] 2.25 Calculate ROI for owned vs purchased renewable energy (no on-site solar/wind installation)

#### Vanilla-Specific Equipment
- [ ] 2.28 Research pollination tools and supplies for Grade A vanilla
- [ ] 2.29 Cost quality testing equipment for Grade A vanilla beans

### Milestone 3: Partner & Produce Costs (Weeks 4-5)
#### Sourcing Costs
- [ ] 3.1 Research Madagascar vanilla bean prices (both direct from farms and brokers)
- [ ] 3.2 Investigate Uganda/Indonesia alternatives (direct and broker channels)
- [ ] 3.3 Analyze US-grown vanilla pricing (direct and broker channels)
- [ ] 3.4 Calculate shipping and import costs for both sourcing channels
- [ ] 3.5 Research minimum order quantities for direct vs broker sourcing

#### Processing Service Costs
- [ ] 3.6 Research Loran/Lorann extraction service provider rates (per kg processed, 100+ gallon bulk pricing)
- [ ] 3.7 Compare Cooks co-packing facility pricing models (100+ gallon bulk pricing)
- [ ] 3.8 Investigate Lochhead packaging and labeling service costs (100+ gallon bulk pricing)
- [ ] 3.9 Calculate quality testing and certification fees for all three partners
- [ ] 3.10 Research logistics and distribution service costs

### Milestone 4: Make & Produce Costs (Rheaplant Cell Agriculture Service Partnership, Weeks 5-6)
#### Research & Development Phase
- [ ] 4.1 Research Rheaplant service fees for vanilla cell culture development (leveraging cacao/rice success)
- [ ] 4.2 Calculate service costs including substrate materials (sugar, growth media components) for vanilla development
- [ ] 4.3 Estimate Rheaplant R&D service fees covering lab resources (water, energy, utilities)
- [ ] 4.4 Price proof-of-concept development service package at Rheaplant facility
- [ ] 4.5 Research vanilla development timeline and total service costs (building on existing capabilities)

#### Operational Scale-Up Phase
- [ ] 4.6 Research Rheaplant service fees for commercial-scale vanilla production setup
- [ ] 4.7 Calculate scale-up service costs for transitioning from R&D to commercial production
- [ ] 4.8 Estimate infrastructure service fees for commercial vanilla production capability
- [ ] 4.9 Price commercial production service packages (100% quality target)
- [ ] 4.10 Research minimum volume commitments for commercial-scale service agreements

#### Production Operations Phase
- [ ] 4.11 Calculate per-batch service fees paid to Rheaplant (high yield target)
- [ ] 4.12 Estimate ongoing service fees for technical support and quality assurance
- [ ] 4.13 Research all-inclusive service pricing covering materials, utilities, and operations
- [ ] 4.14 Calculate total production costs per unit of vanilla output from Rheaplant
- [ ] 4.15 Estimate quality control service costs per batch (100% quality standard)

### Milestone 5: Supporting Costs (Weeks 6-7)
#### Academic Research & Partnerships (Per Slides 8, 10, 23)
- [ ] 5.1 Research free academic consultation opportunities (WSU, OSU, UF) - no paid partnerships if grants unavailable
- [ ] 5.2 Identify expertise available through unpaid academic consultation
- [ ] 5.3 Cost Food Innovation Center partnerships only if grant-funded
- [ ] 5.4 Document grant application requirements for future reference

#### Marketing & Sales
- [ ] 5.5 Research PR agency rates (Pacific Northwest)
- [ ] 5.6 Calculate digital marketing budget
- [ ] 5.7 Estimate packaging/branding design
- [ ] 5.8 Research B2B sales costs

#### Regulatory & Compliance
- [ ] 5.9 FDA food facility registration
- [ ] 5.10 USDA Organic certification costs
- [ ] 5.11 State business licenses
- [ ] 5.12 Insurance quotes (liability, product)
- [ ] 5.13 Legal and accounting services

#### General Business
- [ ] 5.14 Virtual office/administrative costs (no physical office space)
- [ ] 5.15 Software and technology (cloud services, data centers per Slide 12)
- [ ] 5.16 Transportation/logistics and sustainable packaging across all revenue streams
- [ ] 5.17 Contingency planning

#### Founder Travel Costs
- [ ] 5.18 Price Seattle-Portland Amtrak train travel (quarterly meetings, 2 founders)
- [ ] 5.19 Research airfare costs Seattle/Portland to Florida (1-2 trips annually for provider relationships, 2 people)
- [ ] 5.20 Research airfare costs Seattle/Portland to Hawaii (1-2 trips annually for provider relationships, 2 people)
- [ ] 5.21 Estimate accommodation costs for Florida/Hawaii provider meetings
- [ ] 5.22 Calculate meal and ground transportation for business travel

### Milestone 6: Final Compilation (Weeks 7-8)
#### Data Validation
- [ ] 6.1 Cross-reference all sources
- [ ] 6.2 Validate price ranges
- [ ] 6.3 Document confidence levels
- [ ] 6.4 Flag items needing quotes
- [ ] 6.5 Peer review findings

#### Documentation
- [ ] 6.6 Create master cost spreadsheet
- [ ] 6.7 Compile source reference database
- [ ] 6.8 Write assumptions document
- [ ] 6.9 Generate executive summary
- [ ] 6.10 Build interactive dashboard

#### Delivery
- [ ] 6.11 Package all deliverables
- [ ] 6.12 Create user guide
- [ ] 6.13 Set up update procedures
- [ ] 6.14 Conduct handoff meeting
- [ ] 6.15 Archive project materials

## Implementation Notes

### Data Collection Strategy
1. **Automated Sources** (via web scraping):
   - Equipment suppliers (FarmTek, GrowSpan, Fisher Scientific)
   - Utility rate databases
   - Commodity prices

2. **Manual Research** (requiring direct contact):
   - Bioreactor systems (custom quotes)
   - Vanilla bean brokers
   - Certification bodies
   - Insurance providers

3. **API Integration**:
   - Energy Information Administration (EIA)
   - USDA agricultural statistics
   - Local utility companies

### Quality Assurance
- Every cost must have at least one verifiable source
- Prefer 2024-2025 data; note if using older estimates
- Include price ranges, not just point estimates
- Document all assumptions clearly
- Flag low-confidence estimates for follow-up

### Technology Stack
- **Data Collection**: Python, Beautiful Soup, Selenium, Requests
- **Data Storage**: SQLite, JSON, CSV
- **Analysis**: Pandas, NumPy
- **Visualization**: Plotly, Matplotlib
- **Documentation**: Markdown, Jupyter Notebooks
- **Automation**: GitHub Actions, cron jobs

## Success Metrics
- [ ] 100% of critical cost categories have verified sources
- [ ] 90% of costs from 2024-2025 timeframe
- [ ] All three revenue streams fully costed
- [ ] Source documentation complete and accessible
- [ ] Dashboard functional and user-friendly
- [ ] Update mechanism tested and documented

## Risk Mitigation
- **Data Availability**: Have fallback estimation methods for proprietary data
- **Price Volatility**: Document date of price capture, provide ranges
- **Regional Variations**: Note where costs are location-specific
- **Technology Changes**: Design flexible schema for emerging cell ag tech
- **Scope Creep**: Maintain focus on cost data, not business strategy

---

*Last Updated: [Current Date]*
*Version: 1.0*
*Status: Planning Phase*