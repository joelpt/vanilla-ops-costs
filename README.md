# Terra35 Vanilla Operations Cost Analysis

A comprehensive data collection and analysis project producing verifiable operational cost data for Terra35's three vanilla farming revenue streams.

## 🎯 Mission

Deliver a detailed operational cost database with verified sources and references for three vanilla farming revenue streams, enabling accurate financial modeling and investment planning.

## 📊 Project Status (January 2025)

### ✅ Completed Phases
- **Milestone 0**: Pre-implementation research (5/5 tasks) - Critical requirements validated
- **Milestone 1**: Infrastructure setup (9/9 tasks) - Database, testing, validation frameworks complete  
- **Milestone 2**: Grow & Produce costs (8/29 tasks) - Greenhouse infrastructure research complete

### 🏗️ Current Progress
**Infrastructure Complete**: Database schema, 183 passing tests, validation framework, scraping tools  
**Data Collection Active**: Systematic research on commercial vanilla cultivation costs  
**Quality Assurance**: All data sourced from legitimate 2024-2025 suppliers with audit trails  

## 💰 Key Cost Findings

### Grow & Produce Infrastructure (5000 sq ft)
- **Greenhouse Benching**: $190,000 ($38-45/sq ft with volume discounts)
- **Climate Control**: $75,000-150,000 (complete HVAC installation) 
- **Supplemental Lighting**: $160,000-634,000 equipment + $29,160 annual operation
  - *Key Discovery*: Vanilla's low-light needs reduce power requirements 60% vs high-light crops
- **Trellis Systems**: $25,000-33,000 (galvanized steel with installation)
- **Irrigation/Fertigation**: $15,000-150,000 (basic to advanced automation)

### Post-Harvest Processing
- **Curing Chambers**: $18,000-165,000 (traditional to King Son specialized systems)
- **Dehydration Equipment**: $2,000-50,000 (commercial food dehydrators)
- **Processing Scale**: 400kg minimum vanilla volume for economic viability

## 🌱 Revenue Streams Analysis

### 1. Grow & Produce (5000 sq ft Greenhouse)
- **Location**: Oregon City, Oregon (existing building, IOT sensors in place)
- **Climate**: 85°F temperature, 85% humidity maintained year-round
- **Infrastructure**: Trellis systems, benching, irrigation, climate control, supplemental lighting
- **Processing**: Curing chambers, dehydration equipment for Grade A vanilla production

### 2. Partner & Produce (White Label Processing)
- **Partners**: Loran/Lorann, Cooks, Lochhead (100+ gallon bulk pricing)
- **Sourcing**: Direct from farms + brokers (Madagascar, Uganda, Indonesia, US-grown)

### 3. Make & Produce (Cell Agriculture)
- **Service Partner**: Rheaplant (proven success with cacao/rice applications)
- **Phases**: R&D → Scale-up → Production (service fee structure)

## 🛠️ Technical Infrastructure

### Database & Validation
- **SQLite Database**: Unique constraints, foreign key relationships, data integrity
- **Validation Framework**: Configurable rules, multiple severity levels, audit trails
- **Testing Suite**: 183 passing tests ensuring system reliability

### Data Collection Standards
- **Source Requirements**: Legitimate 2024-2025 suppliers only
- **Audit Trails**: Complete documentation from source to final number  
- **Quality Tiers**: Direct supplier quotes > Industry reports > Comparable pricing
- **No Synthetic Data**: All costs traced to real, verifiable sources

### Technology Stack
- **Language**: Python with requests, BeautifulSoup, pandas, SQLite
- **Testing**: pytest with comprehensive coverage and fixtures
- **Quality**: Black formatting, systematic refactoring, SRP compliance
- **Version Control**: Git with conventional commits and atomic changes

## 📁 Project Structure

```
├── data/                   # Research documents and cost data
│   ├── *_research_2025.md  # Detailed equipment and supplier research  
│   └── costs_database.db   # Structured cost data (SQLite)
├── scripts/                # Data collection and processing tools
│   ├── scrapers/          # Web scraping framework and supplier modules
│   ├── validation/        # Data validation and quality assurance
│   └── utils/             # Citation management and utilities
├── config/                 # Schema, validation rules, taxonomies
├── research/               # Milestone 0 pre-implementation research
├── tests/                  # Comprehensive test suite (183 tests)
└── PLAN.md                # Living document with 100+ tasks by milestone
```

## 🎯 Success Metrics

- **Infrastructure**: ✅ Complete (Database, testing, validation, scraping tools)
- **Data Quality**: All costs from verified 2024-2025 sources with audit trails
- **Coverage**: Systematic research across all three revenue streams
- **Validation**: Cross-referenced pricing from multiple suppliers
- **Documentation**: Executive summaries with key findings and cost ranges

## 📋 Implementation Approach

### Phase 1: Research & Infrastructure ✅ 
- Validated vanilla cultivation requirements and production targets
- Built robust data collection and validation infrastructure
- Established quality standards and testing frameworks

### Phase 2: Data Collection 🔄 (Current)
- Systematic cost research for each revenue stream
- Web scraping and manual research for proprietary items  
- Real-time validation and source documentation

### Phase 3: Analysis & Reporting (Upcoming)
- Cross-reference and validate all collected data
- Generate cost analysis reports and visualizations
- Create interactive dashboards and executive summaries

## 🎯 Key Discoveries

1. **Vanilla-Specific Advantages**: Low-light orchid requirements reduce infrastructure costs significantly
2. **Processing Economics**: Minimum 400kg annual volume needed for economic curing operations  
3. **Oregon Climate**: Supplemental lighting essential October-March, but 60% lower power vs high-light crops
4. **Equipment Integration**: All systems must function in 85% humidity environment
5. **Commercial Pricing**: Wide ranges requiring careful supplier selection and volume negotiations

## 🔍 Quality Assurance

- **Source Verification**: Every cost traced to legitimate supplier with URL and access date
- **Cross-Validation**: Multiple sources for critical cost categories  
- **Confidence Levels**: Assigned to each data point based on source quality
- **Audit Trails**: Complete documentation of data collection decisions
- **No Estimates**: Only real, verified pricing data accepted

---

**Project Team**: Terra35 Vanilla Operations Research  
**Location**: Oregon City, Oregon  
**Timeline**: January 2025 - Implementation Phase  
**Status**: Active data collection with systematic milestone progression