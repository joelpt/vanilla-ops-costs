# Terra35 Vanilla Operations - Web Scrapers

This package provides web scraping infrastructure for collecting cost data from suppliers relevant to vanilla cultivation and processing operations.

## Architecture Overview

### Base Framework
- **BaseScraper**: Abstract base class with common functionality
- **ScrapedProduct**: Standardized data structure for all scraped items
- **ScrapingResult**: Session results and statistics container
- **scraper_utils**: Common utility functions and helpers

### Key Features
- **Rate limiting**: Respectful scraping with configurable delays
- **Caching**: Automatic response caching for audit trails and efficiency
- **Error handling**: Robust retry logic and error recovery
- **Database integration**: Direct integration with SQLite cost database
- **Validation**: Data validation and quality scoring
- **Logging**: Comprehensive logging and monitoring

## Available Scrapers

### FarmTek Scraper (`farmtek_scraper.py`)
**Target**: https://www.farmtek.com  
**Focus**: Greenhouse equipment, structures, climate control, growing supplies  
**Categories**:
- Greenhouse kits and structures
- Benching and racking systems
- HVAC and ventilation equipment
- Irrigation and fertigation systems
- Growing supplies and materials

### Planned Scrapers
- **GrowSpan**: Greenhouse structures and systems
- **Fisher Scientific**: Laboratory equipment and chemicals
- **Vanilla Suppliers**: Bean sourcing and processing equipment
- **Utility Providers**: Energy and water rate scraping

## Usage Examples

### Basic Scraping
```python
from scrapers import FarmTekScraper

# Create scraper instance
scraper = FarmTekScraper()

# Run complete scraping session
results = scraper.run_scraping_session(max_products_per_category=20)

print(f"Scraped {len(results.products_scraped)} products")
print(f"Made {results.requests_made} requests")
print(f"Cache hits: {results.cache_hits}")
```

### Custom Configuration
```python
scraper = FarmTekScraper(
    cache_dir="custom/cache/path",
    rate_limit_delay=3.0,  # 3 second delays
    max_retries=5,
    timeout=60
)
```

### Implementing New Scrapers
```python
from scrapers import BaseScraper, ScrapedProduct

class MySupplierScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            supplier_name="MySupplier",
            base_url="https://mysupplier.com",
            rate_limit_delay=2.0
        )
    
    def scrape_products(self, **kwargs):
        products = []
        
        # Your scraping logic here
        response = self.make_request("/products/")
        # Parse response and create ScrapedProduct instances
        
        return products
```

## Data Flow

```
Web Request → Response Cache → HTML Parsing → Data Extraction → 
Product Validation → Database Storage → Session Results
```

### 1. Request Phase
- Rate limiting applied automatically
- Responses cached with timestamps
- Retry logic for failed requests
- User-agent rotation and header management

### 2. Parsing Phase
- BeautifulSoup HTML parsing
- Regex-based data extraction
- Price normalization and cleaning
- Specification parsing

### 3. Validation Phase
- Required field validation
- Price reasonableness checks
- URL format validation
- Data completeness scoring

### 4. Storage Phase
- SQLite database insertion
- Source reference creation
- Collection session tracking
- Activity logging

## Configuration

### Scraper Settings
Each scraper can be configured with:
- **Rate limiting**: Delay between requests
- **Caching**: Cache duration and location
- **Retries**: Maximum retry attempts
- **Timeouts**: Request timeout values
- **Categories**: Target product categories

### Database Integration
Scrapers automatically:
- Create cost items with proper categorization
- Store pricing data with confidence levels
- Maintain source references and audit trails
- Track collection sessions and progress

## Data Quality

### Validation Rules
- **Price validation**: Reasonable range checks
- **Required fields**: Name, category, source URL mandatory
- **Unit consistency**: Price/unit relationships validated
- **Source verification**: URL format and accessibility

### Confidence Levels
- **VERIFIED**: Direct supplier confirmation
- **HIGH**: Complete data with product codes
- **MEDIUM**: Standard scraping with validation
- **LOW**: Incomplete or questionable data

## Error Handling

### Request Errors
- Automatic retries with exponential backoff
- HTTP status code handling
- Network timeout recovery
- Rate limit compliance

### Data Errors
- Graceful parsing error handling
- Validation failure logging
- Partial data recovery
- Error aggregation and reporting

## Monitoring and Logging

### Log Levels
- **DEBUG**: Detailed request/response info
- **INFO**: Session progress and results  
- **WARNING**: Data quality issues
- **ERROR**: Critical failures

### Log Files
- `logs/{supplier}_scraper.log`: Individual supplier logs
- Session-based organization
- Structured logging format
- Automatic log rotation

## Ethical Considerations

### Respectful Scraping
- Reasonable rate limits (1-3 seconds between requests)
- Proper User-Agent identification
- Robots.txt compliance (manual verification required)
- Server resource consideration

### Legal Compliance
- Public data only
- No authentication bypass
- Terms of service compliance
- Fair use principles

## Testing and Development

### Testing Individual Scrapers
```bash
# Test FarmTek scraper with limited products
python scripts/scrapers/farmtek_scraper.py

# Test base scraper functionality
python -m pytest scripts/scrapers/tests/
```

### Development Guidelines
- Inherit from BaseScraper for all new scrapers
- Use ScrapedProduct for consistent data structure
- Implement proper error handling and logging
- Include supplier-specific documentation
- Test with small samples before full runs

## Performance Considerations

### Optimization Strategies
- **Caching**: Aggressive response caching reduces duplicate requests
- **Session reuse**: HTTP connection pooling
- **Concurrent limiting**: Respect server resources
- **Database batching**: Bulk insert operations

### Monitoring Metrics
- Requests per minute
- Cache hit ratio
- Error rate tracking
- Data quality scores
- Session completion times

## Maintenance

### Regular Tasks
- **Weekly**: Review error logs and failed requests
- **Monthly**: Update scraper configurations and selectors
- **Quarterly**: Validate data quality and supplier changes
- **Annually**: Review ethical compliance and terms of service

### Troubleshooting
- Check logs for specific error patterns
- Verify website structure hasn't changed
- Validate network connectivity and DNS
- Review rate limiting and blocking indicators
- Test with simplified requests to isolate issues

---

*Last Updated: December 30, 2024*
*Version: 1.0*