import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

BASE_URL = "https://www.supplychain247.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def parse_date(date_str):
    """Parse date like 'June 10, 2026' or 'Jun 10, 2026' into YYYY-MM-DD"""
    # Try full month name
    try:
        return datetime.strptime(date_str, "%B %d, %Y").strftime("%Y-%m-%d")
    except:
        pass
    # Try abbreviated month name
    try:
        return datetime.strptime(date_str, "%b %d, %Y").strftime("%Y-%m-%d")
    except:
        pass
    return None

def get_today_articles():
    today = datetime.now().strftime("%Y-%m-%d")
    articles = []
    
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Look for the main news container (id="news")
        news_container = soup.find("div", id="news")
        if not news_container:
            print("Could not find news container")
            return []
        
        # Find all article blocks inside that container.
        # Each article is wrapped in a <div> with id="cc" (or sometimes class="cc")
        article_blocks = news_container.find_all("div", id="cc")
        if not article_blocks:
            # Fallback: look for divs with class "cc"
            article_blocks = news_container.find_all("div", class_="cc")
        
        print(f"Found {len(article_blocks)} article blocks")
        
        for block in article_blocks:
            # Find title and link
            title_tag = block.find("a", class_="news-head")
            if not title_tag:
                # Sometimes the link is directly inside the block without a class
                title_tag = block.find("a", href=True)
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            href = title_tag.get("href")
            if not href:
                continue
            if href.startswith("/"):
                full_url = BASE_URL + href
            else:
                full_url = href
            
            # Find the date span
            date_span = block.find("span", itemprop="datePublished")
            if not date_span:
                # Try other possible date containers
                date_elem = block.find("div", class_="dateline")
                if date_elem:
                    date_span = date_elem.find("span", itemprop="datePublished")
            if not date_span:
                continue
            
            date_text = date_span.get_text(strip=True)
            article_date = parse_date(date_text)
            if article_date is None:
                continue
            
            if article_date == today:
                # Get excerpt if available
                excerpt_tag = block.find("div", class_="text")
                excerpt = excerpt_tag.get_text(strip=True) if excerpt_tag else ""
                articles.append({
                    "title": title,
                    "link": full_url,
                    "excerpt": excerpt[:300]
                })
                print(f"✓ Added: {title[:50]}... ({article_date})")
            else:
                print(f"✗ Skipped: {title[:40]}... ({article_date})")
        
        print(f"Total articles for {today}: {len(articles)}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    return articles
