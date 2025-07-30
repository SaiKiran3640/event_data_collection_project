import requests
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import urljoin
from typing import List, Dict, Optional
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventbriteScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.max_retries = 3

    def make_request(self, url: str, retries: int = 0) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if retries < self.max_retries:
                wait_time = (2 ** retries) + 1  # Exponential backoff + jitter
                logger.warning(f"Request failed, retrying in {wait_time}s ({retries + 1}/{self.max_retries}): {e}")
                time.sleep(wait_time)
                return self.make_request(url, retries + 1)
            else:
                logger.error(f"Request failed after {self.max_retries} retries: {e}")
                return None

    def clean_text(self, text: str, max_length: int = None) -> str:
        """Clean and truncate text"""
        if not text or text == "Not found":
            return ""
        
        # Remove extra whitespace and newlines
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length - 3] + "..."
        
        return cleaned

    def scrape_event_listings(self, listing_url: str) -> List[Dict[str, str]]:
        """Scrape event titles and URLs from a listing page"""
        logger.info(f"📄 Fetching listings: {listing_url}")
        
        response = self.make_request(listing_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        event_urls = []

        # More comprehensive selectors for Eventbrite
        selectors = [
            'a[data-testid="event-card-link"]',
            'a.event-card-link',
            'a[href*="/e/"]',  # Most reliable - any link with /e/ in URL
            '.event-card a',
            '[data-testid="event-listing-card"] a',
            'article a[href*="/e/"]',
            '.search-event-card-wrapper a',
            'div[data-testid*="event"] a[href*="/e/"]'
        ]

        for selector in selectors:
            cards = soup.select(selector)
            if cards:
                logger.info(f"✅ Found {len(cards)} events using selector: {selector}")
                break
        else:
            logger.warning("❌ No events found with any selector")
            # Debug: save page content for inspection
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.warning("💾 Saved page content to debug_page.html for inspection")
            return []

        for card in cards:
            try:
                # Get title - try multiple approaches
                title_elem = card.select_one('h3, h2, .event-card__title, [data-testid="event-title"], .event-title')
                if not title_elem:
                    # Try to find title in parent elements
                    parent = card.find_parent()
                    if parent:
                        title_elem = parent.select_one('h1, h2, h3, h4, .title, [class*="title"]')
                
                title = title_elem.get_text(strip=True) if title_elem else "No title found"

                # Get link
                link = card.get('href', '')
                if link.startswith('/'):
                    link = urljoin(listing_url, link)

                # Validate link contains event ID
                if link and '/e/' in link and len(link) > 20:
                    event_urls.append({'title': title, 'url': link})
                    logger.debug(f"📝 Found: {title[:50]}...")

            except Exception as e:
                logger.warning(f"⚠️ Error parsing card: {e}")
                continue

        # Remove duplicates based on URL
        seen_urls = set()
        unique_events = []
        for event in event_urls:
            if event['url'] not in seen_urls:
                seen_urls.add(event['url'])
                unique_events.append(event)

        logger.info(f"🎯 Total unique events found on this page: {len(unique_events)}")
        return unique_events

    def scrape_event_details(self, event_url: str) -> Optional[Dict]:
        """Scrape details from an individual event page"""
        logger.debug(f"🔍 Scraping details: {event_url}")
        
        response = self.make_request(event_url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')

        data = {
            'source_url': event_url,
            'title': 'Not found',
            'date_string': 'Not found',
            'location': 'Not found',
            'description': 'Not found',
            'organizer': 'Not found',
            'price': 'Not found'
        }

        # Title - more comprehensive search
        title_selectors = [
            'h1[data-testid="event-title"]',
            'h1.event-title',
            'h1.css-0',
            'h1',
            '.event-title h1',
            '[data-testid*="title"] h1',
            'header h1'
        ]
        for sel in title_selectors:
            tag = soup.select_one(sel)
            if tag and tag.get_text(strip=True):
                data['title'] = self.clean_text(tag.get_text(strip=True), 500)
                break

        # Date - keep original string format
        date_selectors = [
            '[data-testid="event-start-date"]',
            '.date-info__full-datetime',
            'time',
            '.event-details__data',
            '[class*="date"]',
            '[data-testid*="date"]',
            '.event-date'
        ]   

        for sel in date_selectors:
            tag = soup.select_one(sel)
            if tag and tag.get_text(strip=True):
                data['date_string'] = self.clean_text(tag.get_text(strip=True), 500)
                break

        # Location
        location_selectors = [
            '[data-testid="event-venue"]',
            '.location-info__address-text',
            '.venue-name',
            '[class*="location"]',
            '[data-testid*="venue"]',
            '.event-location'
        ]
        for sel in location_selectors:
            tag = soup.select_one(sel)
            if tag and tag.get_text(strip=True):
                data['location'] = self.clean_text(tag.get_text(strip=True), 255)
                break

        # Description
        desc_selectors = [
            '[data-testid="event-description"]',
            '.event-description',
            '.eds-text--left',
            '.description-content',
            '[class*="description"]',
            '.event-details .description'
        ]
        for sel in desc_selectors:
            tag = soup.select_one(sel)
            if tag:
                # Get text from paragraphs and lists
                paragraphs = tag.find_all(['p', 'ul', 'li', 'div'])
                if paragraphs:
                    desc_text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
                else:
                    desc_text = tag.get_text(strip=True)
                
                if desc_text:
                    data['description'] = self.clean_text(desc_text, 10000)
                    break

        # Organizer
        org_selectors = [
            '[data-testid="organizer-name"]',
            '.descriptive-organizer-info-mobile__name-link',
            '.organizer-name',
            'a[href*="/o/"]',
            '[class*="organizer"] a',
            '.event-organizer'
        ]
        for sel in org_selectors:
            tag = soup.select_one(sel)
            if tag and tag.get_text(strip=True):
                data['organizer'] = self.clean_text(tag.get_text(strip=True), 255)
                break

        # Price
        price_selectors = [
            '[data-testid="ticket-price"]',
            '.CondensedConversionBar-module__priceTag___3AnIu',
            '.ticket-price',
            '.price',
            '[class*="price"]',
                '.ticket-info .price'
        ]

        
        for sel in price_selectors:
            tag = soup.select_one(sel)
            if tag and tag.get_text(strip=True):
                data['price'] = self.clean_text(tag.get_text(strip=True), 100)
                break
        
        return data

    def scrape_all_events(self, base_url: str, max_pages: int = 3, delay: float = 1.5) -> List[Dict]:
        """Scrape events across multiple pages with better pagination handling"""
        logger.info(f"🚀 Starting paginated scraping from: {base_url}")
        logger.info(f"📊 Target: {max_pages} pages with {delay}s delay between requests")

        all_events = []
        seen_urls = set()
        consecutive_empty_pages = 0
        max_empty_pages = 3  # Stop after 3 consecutive empty pages

        for page in range(1, max_pages + 1):
            # Construct paginated URL
            if '?' in base_url:
                paginated_url = f"{base_url}&page={page}"
            else:
                paginated_url = f"{base_url}?page={page}"
            
            logger.info(f"\n📄 Scraping page {page}/{max_pages}: {paginated_url}")
            
            # Get listings for this page
            listings = self.scrape_event_listings(paginated_url)
            
            if not listings:
                consecutive_empty_pages += 1
                logger.warning(f"⚠️ Page {page} returned no events (consecutive empty: {consecutive_empty_pages})")
                
                if consecutive_empty_pages >= max_empty_pages:
                    logger.info(f"🛑 Stopping after {consecutive_empty_pages} consecutive empty pages")
                    break
                    
                time.sleep(delay)
                continue
            else:
                consecutive_empty_pages = 0  # Reset counter

            # Process events from this page
            new_events_count = 0
            for event in listings:
                if event['url'] in seen_urls:
                    logger.debug(f"🔄 Skipping duplicate: {event['title'][:40]}")
                    continue
                
                seen_urls.add(event['url'])

                # Scrape event details
                detail = self.scrape_event_details(event['url'])
                if detail:
                    all_events.append(detail)
                    new_events_count += 1
                    logger.info(f"✅ [{len(all_events)}] Scraped: {detail['title'][:50]}")
                else:
                    logger.warning(f"❌ Failed to scrape: {event['title'][:40]}")

                # Rate limiting
                time.sleep(delay)

            logger.info(f"📈 Page {page} summary: {new_events_count} new events, {len(all_events)} total")

        logger.info(f"\n🎉 Scraping complete!")
        logger.info(f"📊 Total events scraped: {len(all_events)}")
        logger.info(f"📄 Pages processed: {page}")
        
        return all_events


# Export function for main.py
def scrape_events() -> List[Dict]:
    """Main function to be called from main.py"""
    scraper = EventbriteScraper()
    
    # URLs to scrape - add more as needed
    urls_to_scrape = [
        "https://www.eventbrite.com/d/online/all-events/",
        # "https://www.eventbrite.com/d/ca--san-francisco/events/",
        # Add more URLs here
    ]
    
    all_events = []
    
    for url in urls_to_scrape:
        logger.info(f"🎯 Starting scrape for: {url}")
        events = scraper.scrape_all_events(url, max_pages=5, delay=1.5)
        all_events.extend(events)
        logger.info(f"✅ Completed {url}: {len(events)} events")
    
    logger.info(f"🏁 All URLs complete: {len(all_events)} total events")
    return all_events