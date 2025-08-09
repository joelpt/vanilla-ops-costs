# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a data collection and analysis project for Terra35's vanilla farming business plan. The goal is to produce comprehensive operational cost analysis with real, verifiable data from legitimate sources for three revenue streams: greenhouse growing, partner production, and cellular agriculture.

## Commands

### Python Environment
```bash
# Install required dependencies
pip install python-pptx requests beautifulsoup4 pandas sqlite3

# Extract PowerPoint content for analysis
python extract_pptx.py

# Run data collection scripts (to be created)
python scripts/collect_greenhouse_costs.py
python scripts/collect_lab_costs.py
python scripts/validate_data.py
```

### Project Management
```bash
# Check current progress
grep -c "\[x\]" PLAN.md

# Find incomplete tasks  
grep "\[ \]" PLAN.md

# Validate all collected data has sources
python scripts/validate_sources.py
```

## Architecture

### Three Revenue Streams Structure
The project analyzes costs for distinct business models:

1. **Grow & Produce**: 5000 sq ft greenhouse vanilla cultivation with outsourced processing
2. **Partner & Produce**: White label vanilla extract production 
3. **Make & Produce**: Cell agriculture lab-grown vanilla

### Data Collection Approach
- **Automated**: Web scraping supplier websites, API integration for commodity prices
- **Manual**: Direct vendor quotes for proprietary equipment, regulatory compliance research
- **Validation**: Cross-reference multiple sources, maintain audit trails

### File Organization
- `PLAN.md`: Living document with 75+ specific tasks organized by milestone
- `data/`: Cost database (JSON/SQLite) and source references
- `scripts/`: Python scrapers and analysis tools
- `reports/`: Generated cost breakdowns and visualizations

## <critical_rules>

### 🚨 DATA INTEGRITY REQUIREMENT 🚨

**MANDATORY**: Every single data point MUST be:
1. **REAL** - Derived from actual legitimate sources
2. **CURRENT** - From 2024-2025 (or explicitly noted if older)
3. **VERIFIABLE** - Include source URL, access date, and screenshot if possible
4. **TRACEABLE** - Complete audit trail from source to final number

**ABSOLUTELY FORBIDDEN**:
- ❌ NO synthetic/made-up data
- ❌ NO placeholder values  
- ❌ NO estimates without real source basis
- ❌ NO assumptions without documentation

**Enforcement**: Any cost without a real source = PROJECT FAILURE

</critical_rules>

## <reasoning_steps>

When collecting any cost data, follow this sequence:

1. **Identify** the specific item needed (check PLAN.md task list)
2. **Research** minimum 3 potential sources (suppliers, reports, databases)
3. **Validate** that sources are legitimate and current
4. **Extract** the data with full context (units, conditions, volume)
5. **Document** source completely (URL, date, screenshot)
6. **Cross-reference** with other sources for validation
7. **Record** in standardized format with confidence level
8. **Update** PLAN.md with progress and any blockers

</reasoning_steps>

## <working_with_plan>

### 🚨 MANDATORY SESSION START PROTOCOL 🚨

**EVERY WORKING SESSION MUST BEGIN WITH:**
1. **Read PLAN.md completely** - Always start by reading the full PLAN.md file
2. **Understand current project state** - Check milestone progress and task status
3. **Identify today's priorities** - Select 3-5 specific tasks to focus on
4. **Update PLAN.md throughout work** - Mark tasks complete, add blockers, update questions

**CRITICAL**: PLAN.md is the living document that drives this entire project. It MUST be kept current and referenced constantly.

### Daily Workflow Sequence

<session_start>
1. **MANDATORY: Read PLAN.md current milestone status and all open tasks**
2. Identify today's specific tasks (maximum 3-5)
3. Check Open Questions that might block progress
4. Review yesterday's collected data for validation needs
5. Set up data collection environment (scripts, browser, tools)
</session_start>

<during_work>
- **Update PLAN.md task status** immediately upon completion
- **Document sources** in real-time (never wait)
- **Update Open Questions** with new discoveries or blockers
- Flag uncertainties with "NEEDS_VALIDATION" tag
- Commit data every hour with descriptive messages
- **Keep PLAN.md synchronized** with actual work progress
</during_work>

<session_end>
1. **Update all task checkboxes in PLAN.md** to reflect completed work
2. **Add discovered questions to Open Questions** section
3. Commit all collected data with sources AND updated PLAN.md
4. Document tomorrow's priorities in PLAN.md if needed
5. Note any vendor callbacks needed
</session_end>

</working_with_plan>

## <data_collection_standards>

### Source Hierarchy

<tier_1_sources>
**PREFERRED - Direct from Supplier**
- Manufacturer websites with published pricing
- Official equipment catalogs with part numbers
- Direct vendor quotes (email/phone documented)
- Current price lists from authorized dealers
Example: "FarmTek.com product page for GrowSpan Series 500"
</tier_1_sources>

<tier_2_sources>
**ACCEPTABLE - Industry Sources**
- Government databases (USDA, EIA, state agencies)
- Industry reports from last 12 months
- Trade publication price surveys
- Academic research with cost data
Example: "USDA 2024 Greenhouse Construction Cost Report"
</tier_2_sources>

<tier_3_sources>
**USE WITH CAUTION - Indirect Sources**
- Comparable product pricing (must note comparison)
- Historical data with inflation adjustment
- Regional averages when specific location unavailable
Example: "Based on similar 50L bioreactor from competitor"
</tier_3_sources>

### Enhanced Data Structure

```json
{
  "item_id": "GH_BENCH_001",
  "item_name": "Commercial Greenhouse Benching System",
  "category": "Grow_Infrastructure",
  "subcategory": "Benching",
  "specifications": {
    "material": "Galvanized steel",
    "load_capacity": "100 lbs/sq ft",
    "dimensions": "4ft x 8ft sections"
  },
  "pricing": {
    "unit_cost": 45.00,
    "unit": "per_sq_ft",
    "volume_discounts": [
      {"quantity": "1000-2499 sq ft", "price": 42.50},
      {"quantity": "2500-4999 sq ft", "price": 40.00},
      {"quantity": "5000+ sq ft", "price": 38.00}
    ],
    "total_5000sqft": 190000
  },
  "source_primary": {
    "company": "FarmTek",
    "product_code": "FS-BENCH-4X8",
    "url": "https://www.farmtek.com/farm/supplies/prod1;ft_greenhouse_benches",
    "date_accessed": "2024-12-30",
    "quote_number": null,
    "contact": null
  },
  "source_validation": [
    {
      "company": "GrowSpan",
      "price": 43.00,
      "date": "2024-12-29"
    }
  ],
  "confidence": "HIGH",
  "data_quality": {
    "is_current": true,
    "needs_update_by": "2025-06-30",
    "last_validated": "2024-12-30"
  },
  "notes": "Price confirmed via phone with FarmTek sales rep. Includes delivery to Pacific Northwest."
}
```

</data_collection_standards>

## Implementation Approach

### Phase 1: Always Start With Research
- Never jump to creating scrapers without understanding the landscape
- Identify top 5 suppliers in each category first
- Check for existing APIs before building scrapers
- Document data availability in PLAN.md

### Phase 2: Build Incrementally
- Create one scraper, test thoroughly, then expand
- Start with manual data collection for complex items
- Automate only after understanding data patterns
- Keep all scripts in `scripts/` directory

### Phase 3: Validate Continuously
- Cross-check prices across multiple sources
- Flag outliers for manual review
- Document why certain sources were chosen
- Maintain audit trail of data decisions

## Project-Specific Patterns

### Web Scraping
```python
# Standard scraper template for this project
class SupplierScraper:
    def __init__(self, supplier_name):
        self.supplier = supplier_name
        self.base_url = None
        self.session = requests.Session()
    
    def extract_price(self, product_url):
        # Always include error handling
        # Always save raw HTML for audit
        # Always timestamp the extraction
```

### Data Storage
- Primary: `data/costs_database.json` - Structured cost data
- Sources: `data/source_references.csv` - All sources with metadata
- Cache: `data/cache/` - Raw HTML, PDFs for audit trail
- Reports: `reports/` - Analysis outputs and visualizations

## Cost Categories Reference

### Grow & Produce (5000 sq ft)
Focus on these specific suppliers:
- **Structures**: FarmTek, GrowSpan, Stuppy Greenhouse
- **Equipment**: Dramm, Netafim, Priva
- **Utilities**: Local Oregon providers, EIA data

### Partner & Produce
Key sources to investigate:
- **Vanilla Beans**: Vanilla.com, Beanilla, Mountain Rose Herbs
- **Equipment**: Apeks Supercritical, ExtraktLAB
- **Packaging**: Berlin Packaging, SKS Bottle

### Make & Produce
Research targets:
- **Bioreactors**: Sartorius, Eppendorf, ABEC
- **Lab Supplies**: Fisher Scientific, VWR, Sigma-Aldrich
- **Cell Culture**: ATCC, Thermo Fisher

## <vendor_outreach_protocol>

### When Direct Contact Required

<triggers_for_outreach>
- No public pricing available online
- Custom equipment requiring specifications
- Minimum order quantities unclear
- Volume discounts not published
- Installation/setup costs needed
</triggers_for_outreach>

<outreach_template>
Subject: Pricing Request - Terra35 Vanilla Cultivation Project

Hello [Vendor Name],

We are researching equipment costs for a commercial vanilla cultivation facility in the Pacific Northwest. We're interested in pricing for:

[Specific Equipment/Service]
- Quantity needed: [Amount]
- Location: [City, State]
- Timeline: Planning phase, implementation in 2025

Could you please provide:
1. Unit pricing for the specified quantity
2. Any volume discounts available
3. Estimated delivery timeframe
4. Installation/setup costs if applicable

Thank you for your assistance.

Best regards,
Terra35 Research Team
</outreach_template>

<tracking_requirements>
- Log all vendor contacts in `data/vendor_contacts.csv`
- Set follow-up reminders for 3 business days
- Document any NDAs or formal quote requirements
- Note if competitor pricing can be used as proxy
</tracking_requirements>

</vendor_outreach_protocol>

## <common_pitfalls>

### Data Collection Mistakes to Avoid

1. **Price Scaling** - Never assume linear scaling
   - ❌ Wrong: "If 100 sq ft costs $1000, then 5000 sq ft = $50,000"
   - ✅ Right: Check actual bulk pricing tiers

2. **Market Segment** - Match commercial vs residential
   - ❌ Wrong: Using Home Depot prices for commercial greenhouse
   - ✅ Right: Commercial supplier quotes only

3. **Hidden Costs** - Include total cost of ownership
   - ❌ Wrong: Equipment price only
   - ✅ Right: Equipment + shipping + installation + first year maintenance

4. **Currency/Units** - Standardize everything
   - ❌ Wrong: Mixing USD and CAD prices
   - ✅ Right: Convert all to USD at current exchange rate

5. **Data Age** - Enforce recency requirements
   - ❌ Wrong: Using 2022 prices without adjustment
   - ✅ Right: 2024-2025 only, or apply documented inflation factor

</common_pitfalls>

## Daily Workflow

### Session Start Checklist
- [ ] Read PLAN.md for current milestone
- [ ] Check Open Questions section
- [ ] Review yesterday's progress
- [ ] Identify today's specific tasks
- [ ] Set up data collection environment

### During Work
- Update PLAN.md task list in real-time
- Document sources immediately (don't wait)
- Flag uncertainties for follow-up
- Commit data frequently with clear messages
- Keep running notes of decisions made

### Session End Protocol
- [ ] Update all task statuses in PLAN.md
- [ ] Add new questions discovered
- [ ] Commit all data collected
- [ ] Document blockers or issues
- [ ] Note priorities for next session

## Quality Assurance Checklist

Before marking any milestone complete:
- [ ] All costs have verified sources
- [ ] Price ranges provided where applicable
- [ ] Confidence levels assigned
- [ ] Assumptions documented
- [ ] Cross-references completed
- [ ] Data validates against schema
- [ ] Reports generated successfully

## Integration with External Tools

### When to Use Python Scripts
- Scraping multiple pages from same supplier
- Processing PDF catalogs
- Calculating derived metrics
- Generating reports

### When to Use Manual Research
- Custom quotes needed
- Phone/email inquiries required
- Complex products with many options
- Regulatory/certification costs

### When to Use APIs
- Utility rates (EIA API)
- Commodity prices
- Currency conversion
- Geographic data

## Progress Tracking

### Milestone Completion Criteria
A milestone is ONLY complete when:
1. All subtasks checked off
2. Data validated and stored
3. Sources documented
4. Confidence levels assigned
5. Reports generated
6. PLAN.md updated

### Red Flags Requiring Immediate Attention
- Cost variance >50% between sources
- Critical data unavailable
- Supplier website changes breaking scrapers
- Regulatory requirements discovered
- Scope creep detected

## Communication Protocol

### When to Ask for Clarification
- Conflicting requirements discovered
- Major cost category missing from PLAN.md
- Technology choice impacts data collection
- Business assumption needed for calculations

### How to Report Blockers
```markdown
### BLOCKER: [Brief Description]
- **Impact**: Which milestone/tasks affected
- **Cause**: Why blocked
- **Options**: Potential solutions
- **Recommendation**: Suggested path forward
- **Decision Needed**: Yes/No
```

## Research Documentation

### Milestone 0 Research Completed (December 30, 2024)
- **Location**: `research/` directory contains all pre-implementation research
- **Summary**: `research/MILESTONE_0_SUMMARY.md` - Executive overview of all findings
- **Key Files**:
  - `usda_organic_certification_research.md` - Certification costs and timelines
  - `vanilla_humidity_temperature_validation.md` - Climate requirement validation
  - `vanilla_extraction_production_targets.md` - Year 1 production targets (150 gallons)
  - `vanilla_paste_production_processes.md` - Paste manufacturing requirements
  - `mid_range_vanilla_operations_analysis.md` - Industry benchmarking analysis
  - `terra35_extracted_content.txt` - PowerPoint content extraction

### Project Structure
- `research/` - All research documents and findings
- `data/milestone0/` - Data collection staging area
- `PLAN.md` - Living implementation plan (updated with research findings)

## Project Memory

### Key Decisions Made
- Milestone 0 completed: All 5 critical research tasks finished with comprehensive documentation
- Production targets established: 150 gallons Year 1 extract, 400 gallons total products
- Climate validation: 85% humidity optimal, 80-82°F temperature recommended
- Equipment needs: 150L extraction system + paste production capability
- Ready for Milestone 1: Infrastructure setup and systematic cost collection

### Lessons Learned
- PowerPoint contained no specific humidity/temperature data - assumptions came from external sources
- Conservative production targets essential for first-year operations due to 6-12 month aging requirements
- USDA organic certification requires 36-month transition period - major timeline consideration
- Mid-range vanilla operations typically operate in 500-5,000 gallon annual range

### Useful Patterns Discovered
- Research-first approach with comprehensive documentation critical for complex projects
- Multiple research documents with executive summary provides actionable intelligence
- Climate requirements validation requires multiple authoritative horticultural sources
- Industry benchmarking through established company analysis provides realistic scaling targets

## Success Metrics Tracking

Monitor these throughout the project:
- Percentage of costs with verified sources: ____%
- Number of high-confidence costs: ____
- Data freshness (% from 2024-2025): ____%
- Automation coverage: ____%
- Source diversity per category: ____

---

## Quick Reference Commands

```bash
# Check current progress
grep -c "\[x\]" PLAN.md

# Find incomplete tasks
grep "\[ \]" PLAN.md

# Run data validation
python scripts/validate_costs.py

# Generate cost report
python scripts/generate_report.py

# Update source references
python scripts/update_sources.py
```

---

*Remember: This is a data collection and analysis project. Every decision should be driven by the goal of delivering accurate, verifiable cost data for Terra35's financial modeling.*

*Last Updated: [Current Date]*
*Version: 1.0*