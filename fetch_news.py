import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

BASE_URL = "https://www.supplychain247.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def extract_date_from_article(item, soup=None):
    """Try to find publication date from article item."""
    # Common date selectors
    selectors = [
        '.date', '.published', '.time', '.post-date', 'time', 
        '.entry-date', '.meta-date', 'span.date'
    ]
    for sel in selectors:
        date_elem = item.select_one(sel)
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            # Try to parse date (adjust format as needed)
            match = re.search(r'(\d{4}-\d{2}-\d{2})', date_text)
            if match:
                return match.group(1)
            # Try other formats: Jan 1, 2026
            try:
                parsed = datetime.strptime(date_text, '%b %d, %Y')
                return parsed.strftime('%Y-%m-%d')
            except:
                pass
    return None

def get_today_articles():
    today = datetime.now().strftime("%Y-%m-%d")
    articles = []
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Find all article containers (using existing logic)
        items = soup.select("div.post, article, div.news-item, div.teaser, div.listing-item")
        if not items:
            # Fallback to all <a> tags with title-like text
            for a in soup.find_all('a', href=True):
                title = a.get_text(strip=True)
                if title and len(title) > 20 and "read more" not in title.lower():
                    link = a['href']
                    if not link.startswith("http"):
                        link = BASE_URL + link
                    articles.append({
                        "title": title,
                        "link": link,
                        "excerpt": ""
                    })
            # If we have no date info, assume all are relevant but limit to first 10
            if articles:
                print(f"No date info, limiting to first 10 articles as fallback.")
                articles = articles[:10]
            return articles
        
        # Process each article item
        for item in items:
            # Get title and link
            title_tag = item.select_one("h2 a, h3 a, .title a, a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            if not title:
                continue
            link = title_tag.get("href")
            if link and not link.startswith("http"):
                link = BASE_URL + link
            
            # Try to get date
            article_date = extract_date_from_article(item, soup)
            if not article_date:
                # If no date found, maybe check the linked article page (expensive)
                # For simplicity, we skip articles without date or assume today?
                # We'll include them but later we'll still limit by count? Better to skip.
                continue  # skip articles without date to be safe
            
            # Keep only today's articles
            if article_date == today:
                excerpt_tag = item.select_one(".excerpt, .summary, .description, p")
                excerpt = excerpt_tag.get_text(strip=True) if excerpt_tag else ""
                articles.append({
                    "title": title,
                    "link": link,
                    "excerpt": excerpt[:300]
                })
        
        # If after date filtering we still have more than 20, limit to 20 (avoid token limits)
        if len(articles) > 20:
            print(f"Found {len(articles)} articles for today, limiting to 20.")
            articles = articles[:20]
            
    except Exception as e:
        print(f"抓取失败: {e}")
    
    return articles
