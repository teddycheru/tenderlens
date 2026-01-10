# backend/app/services/scrapers/base_scraper.py
"""
Base scraper class with common scraping functionality.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Browser, Page
import time
from datetime import datetime


class BaseScraper(ABC):
    """
    Base class for all tender portal scrapers.
    Provides common functionality for scraping websites.
    """

    def __init__(self, source_id: str, source_name: str):
        self.source_id = source_id
        self.source_name = source_name
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    def initialize_browser(self, headless: bool = True):
        """Initialize Playwright browser."""
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=headless)
        self.page = self.browser.new_page()

        # Set reasonable timeout
        self.page.set_default_timeout(30000)  # 30 seconds

    def close_browser(self):
        """Close browser and cleanup."""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()

    def wait_and_respect_rate_limit(self, seconds: int = 2):
        """Wait between requests to respect rate limits."""
        time.sleep(seconds)

    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        Main scraping method to be implemented by each scraper.

        Returns:
            List of dictionaries containing tender data
        """
        pass

    def extract_text(self, selector: str, default: str = "") -> str:
        """Safely extract text from element."""
        try:
            element = self.page.query_selector(selector)
            return element.inner_text().strip() if element else default
        except Exception:
            return default

    def extract_attribute(self, selector: str, attribute: str, default: str = "") -> str:
        """Safely extract attribute from element."""
        try:
            element = self.page.query_selector(selector)
            return element.get_attribute(attribute) or default if element else default
        except Exception:
            return default

    def extract_all_text(self, selector: str) -> List[str]:
        """Extract text from all matching elements."""
        try:
            elements = self.page.query_selector_all(selector)
            return [el.inner_text().strip() for el in elements if el.inner_text()]
        except Exception:
            return []

    def create_tender_record(
        self,
        title: str,
        description: str = "",
        deadline: Optional[str] = None,
        published_date: Optional[str] = None,
        category: Optional[str] = None,
        region: Optional[str] = None,
        source_url: Optional[str] = None,
        budget: Optional[str] = None,
        **extra_fields
    ) -> Dict:
        """
        Create standardized tender record.

        Returns:
            Dictionary with tender data ready for staging table
        """
        return {
            "title": title,
            "description": description,
            "deadline": deadline,
            "published_date": published_date or datetime.now().strftime("%Y-%m-%d"),
            "category": category,
            "region": region,
            "source_url": source_url,
            "budget": budget,
            **extra_fields
        }


class SampleScraper(BaseScraper):
    """
    Sample scraper implementation for testing.
    Replace with actual scraper for specific portal.
    """

    def __init__(self):
        super().__init__(
            source_id="sample_portal",
            source_name="Sample Tender Portal"
        )

    def scrape(self) -> List[Dict]:
        """
        Scrape sample tender portal.

        This is a template - implement actual scraping logic here.
        """
        tenders = []

        try:
            self.initialize_browser()

            # Example: Navigate to tender page
            # self.page.goto("https://example.com/tenders")
            # self.wait_and_respect_rate_limit()

            # Example: Extract tender listings
            # tender_cards = self.page.query_selector_all(".tender-card")

            # for card in tender_cards:
            #     title = card.query_selector(".title").inner_text()
            #     description = card.query_selector(".description").inner_text()
            #     deadline = card.query_selector(".deadline").inner_text()
            #
            #     tender = self.create_tender_record(
            #         title=title,
            #         description=description,
            #         deadline=deadline,
            #         category="IT",
            #         region="Addis Ababa"
            #     )
            #     tenders.append(tender)

            # For now, return empty list (implement actual scraping above)
            pass

        except Exception as e:
            print(f"Scraping error: {str(e)}")
        finally:
            self.close_browser()

        return tenders
