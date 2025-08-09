#!/usr/bin/env python3
"""
Terra35 Vanilla Operations Cost Analysis - Scraper Package

This package provides web scraping capabilities for collecting cost data
from various suppliers and sources for the vanilla operations analysis.

Available scrapers:
- BaseScraper: Abstract base class for all scrapers
- FarmTekScraper: Greenhouse equipment and supplies
- GrowSpanScraper: Greenhouse structures and systems
- FisherScraper: Laboratory equipment and supplies
- VanillaScraper: Vanilla bean suppliers and processors

Usage:
    from scrapers import BaseScraper
    from scrapers.farmtek import FarmTekScraper
    
    scraper = FarmTekScraper()
    results = scraper.run_scraping_session()
"""

from .base_scraper import BaseScraper, ScrapedProduct, ScrapingResult

__version__ = "1.0.0"
__author__ = "Terra35 Analysis Team"

__all__ = [
    'BaseScraper',
    'ScrapedProduct', 
    'ScrapingResult'
]