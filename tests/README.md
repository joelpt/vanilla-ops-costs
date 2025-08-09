# Terra35 Vanilla Operations Cost Analysis - Test Suite

This directory contains comprehensive unit and integration tests for the Terra35 vanilla operations cost analysis infrastructure built in Milestone 1.

## Test Structure

```
tests/
├── __init__.py                     # Test package initialization
├── conftest.py                     # Pytest configuration and fixtures
├── test_database_initialization.py # Tests for database setup
├── test_base_scraper.py           # Tests for scraper framework
├── test_data_validator.py         # Tests for data validation
├── test_citation_manager.py       # Tests for citation management
├── test_scraper_utils.py          # Tests for scraper utilities
├── test_integration.py            # Integration tests
└── README.md                      # This file
```

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m "unit"

# Integration tests only
pytest -m "integration"

# Database-related tests
pytest -m "database"

# Exclude slow tests
pytest -m "not slow"
```

### Run Specific Test Files

```bash
# Test database initialization
pytest tests/test_database_initialization.py

# Test scraper framework
pytest tests/test_base_scraper.py

# Test data validation
pytest tests/test_data_validator.py

# Test citation management
pytest tests/test_citation_manager.py

# Test scraper utilities
pytest tests/test_scraper_utils.py

# Test integration
pytest tests/test_integration.py
```

### Run Tests with Coverage

```bash
pytest --cov=scripts --cov-report=html --cov-report=term
```

This generates both terminal output and an HTML coverage report in `htmlcov/`.

## Test Components

### 1. Database Initialization Tests (`test_database_initialization.py`)

Tests the `DatabaseInitializer` class that sets up the SQLite database:

- **Schema Creation**: Tests database and table creation from SQL files
- **Configuration Loading**: Tests loading JSON configuration files
- **Data Population**: Tests inserting initial cost categories and revenue streams
- **Error Handling**: Tests handling of missing files, invalid JSON, etc.
- **Verification**: Tests database structure validation
- **CLI Integration**: Tests command-line interface functionality

**Key Test Cases:**
- Creating new databases with proper schema
- Recreating existing databases (with warnings)
- Loading cost categories from taxonomy
- Handling missing configuration files
- PRAGMA settings applied correctly

### 2. Base Scraper Tests (`test_base_scraper.py`)

Tests the `BaseScraper` framework that provides common scraping functionality:

- **Initialization**: Tests scraper setup with various configurations
- **Session Management**: Tests scraping session lifecycle
- **Rate Limiting**: Tests respectful scraping delays
- **Caching**: Tests HTTP response caching and expiration
- **Request Handling**: Tests HTTP requests with retries and error handling
- **Data Parsing**: Tests price parsing and validation
- **Database Integration**: Tests saving scraped products to database

**Key Test Cases:**
- Rate limiting delays between requests
- Cache hit/miss behavior
- HTTP retry logic for failed requests
- Price parsing with various formats
- Product validation before saving
- Database transaction handling

### 3. Data Validation Tests (`test_data_validator.py`)

Tests the `DataValidator` framework that ensures data quality:

- **Configuration Management**: Tests loading validation rules and thresholds
- **Validation Rules**: Tests each validation rule individually
- **Quality Scoring**: Tests confidence score calculations
- **Batch Processing**: Tests validating multiple items at once
- **Error Handling**: Tests graceful handling of validation failures

**Key Test Cases:**
- Required field validation
- Price range and reasonableness checks
- Source URL format validation
- Data freshness validation
- Specification completeness checks
- Overall quality score calculation

### 4. Citation Manager Tests (`test_citation_manager.py`)

Tests the `CitationManager` that creates and validates source citations:

- **Citation Creation**: Tests generating formatted citations
- **Validation**: Tests citation completeness and format validation
- **Confidence Scoring**: Tests automatic confidence score calculation
- **Documentation**: Tests markdown documentation generation
- **Export Functions**: Tests CSV export functionality

**Key Test Cases:**
- Supplier website citation formatting
- Direct quote citation handling
- URL and date format validation
- Confidence score adjustments
- Screenshot filename generation
- Documentation content generation

### 5. Scraper Utils Tests (`test_scraper_utils.py`)

Tests utility functions used across scraping operations:

- **Text Processing**: Tests text cleaning and normalization
- **Data Extraction**: Tests numeric value and dimension parsing
- **Product Categorization**: Tests automatic product categorization
- **URL Validation**: Tests URL format checking
- **Configuration Management**: Tests config save/load operations

**Key Test Cases:**
- HTML entity cleaning
- Price and currency normalization
- Dimension parsing (L×W×H formats)
- Product categorization by keywords
- Unit detection from text
- Configuration file management

### 6. Integration Tests (`test_integration.py`)

Tests interaction between multiple components working together:

- **Database + Scraper**: Tests complete workflow from database setup through data collection
- **Scraper + Validation**: Tests data validation during scraping
- **Validation + Citation**: Tests citation creation and validation together
- **Full System**: Tests complete end-to-end workflow
- **Error Handling**: Tests system behavior under error conditions
- **Batch Processing**: Tests handling multiple products simultaneously

**Key Test Cases:**
- Complete cost data collection workflow
- Cross-component data validation
- Error recovery and graceful degradation
- Batch processing performance
- Data consistency across components

## Test Fixtures and Utilities

### `conftest.py`

Provides shared fixtures used across multiple test files:

- `temp_db`: Creates temporary SQLite database with test schema
- `temp_cache_dir`: Creates temporary directory for cache files
- `sample_config_data`: Provides sample configuration data
- `sample_citation_config`: Provides citation configuration
- `sample_scraped_product`: Creates example scraped product
- `sample_item_data`: Creates example item data for validation
- `mock_requests`: Mocks HTTP requests for testing
- `temp_config_files`: Creates temporary configuration files

### Test Data Patterns

Tests use realistic data patterns that match actual use cases:

- Product names and descriptions typical of greenhouse/lab equipment
- Price ranges and units common in agricultural/scientific markets
- URL patterns from real supplier websites
- Specification formats found in product catalogs

## Test Configuration

### `pytest.ini`

Configures pytest behavior:
- Test discovery patterns
- Output formatting
- Warning filters
- Test markers for categorization

### Markers

Tests are marked for selective execution:

- `@pytest.mark.unit`: Individual component tests
- `@pytest.mark.integration`: Cross-component tests
- `@pytest.mark.database`: Tests requiring database setup
- `@pytest.mark.slow`: Long-running tests
- `@pytest.mark.network`: Tests that would make network calls (mocked)

## Best Practices Demonstrated

### 1. Isolation
- Each test is independent and can run alone
- Temporary files/databases are cleaned up automatically
- No shared state between tests

### 2. Mocking
- External dependencies (HTTP requests, file system) are mocked
- Database operations use temporary test databases
- Time-dependent functions use controlled timestamps

### 3. Edge Cases
- Tests cover both success and failure scenarios
- Invalid inputs and error conditions are tested
- Boundary conditions are validated

### 4. Realistic Data
- Test data matches actual expected formats
- Price ranges and product types are realistic
- URL patterns match real supplier websites

### 5. Performance
- Integration tests validate batch processing
- Cache behavior is tested for performance impact
- Database transaction efficiency is verified

## Running Tests in CI/CD

For automated testing environments:

```bash
# Install dependencies
pip install -r requirements-test.txt

# Run tests with coverage and JUnit XML output
pytest --cov=scripts --cov-report=xml --junit-xml=test-results.xml

# Check coverage thresholds
pytest --cov=scripts --cov-fail-under=80
```

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure test directories are writable
2. **Missing Dependencies**: Install all requirements from `requirements-test.txt`
3. **Path Issues**: Tests assume they're run from project root directory
4. **Database Locks**: Tests clean up temporary databases automatically

### Debug Mode

Run tests with additional debugging:

```bash
pytest -v -s --tb=long --log-cli-level=DEBUG
```

### Specific Test Debugging

```bash
# Run single test with debugging
pytest tests/test_database_initialization.py::TestDatabaseInitializer::test_create_database_new_file -v -s

# Run with PDB debugger
pytest --pdb tests/test_base_scraper.py::TestBaseScraper::test_make_request_success
```

## Test Coverage Goals

- **Unit Tests**: >90% line coverage for all modules
- **Integration Tests**: Cover all major component interactions
- **Edge Cases**: Test all error conditions and boundary cases
- **Performance**: Validate acceptable performance under load

Current coverage can be checked with:
```bash
pytest --cov=scripts --cov-report=term-missing
```

## Contributing New Tests

When adding new functionality, ensure:

1. **Unit tests** for the new component
2. **Integration tests** if it interacts with existing components
3. **Error handling tests** for failure scenarios
4. **Documentation** updates in docstrings and this README
5. **Realistic test data** that matches production patterns

Follow existing test patterns and naming conventions for consistency.