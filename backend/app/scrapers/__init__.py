"""
Israeli Price Comparison Scrapers
Supports: Zap, KSP, Bug
"""

from .base_scraper import BaseScraper
from .zap_scraper import ZapScraper
from .ksp_scraper import KSPScraper
from .bug_scraper import BugScraper
from .scraper_manager import ScraperManager

__all__ = [
    'BaseScraper',
    'ZapScraper',
    'KSPScraper',
    'BugScraper',
    'ScraperManager'
]
