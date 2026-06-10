import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

BASE_URL = "https://www.supplychain247.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def is_likely_article_url(url):
    """Filter out non-article links like category pages, home, etc."""
    if not url:
        return False
    # Typical article URL patterns
    patterns = [
        r'/article/',
        r'/news/',
        r'/story/',
        r'/post/',
        r'/\d{4}/\d{2}/',  # date in URL
    ]
    for pattern in patterns:
        if re.search(pattern, url):
            return True
    return False

def extract_date_from_article(item):
    """Try to extract date from article element."""
    # Common selectors for date
    selectors = [
        'time', '.date', '.published', '.post-date', 
        '.meta-date', '.entry-date', 'span.date'
    ]
    for sel in selectors:
        elem = item.select_one(sel)
        if elem:
            date_text = elem.get_text(strip=True)
            # Look for YYYY-MM-DD
            match = re.search(r'(\d{4}-\d{2}-\d{2})', date_text)
            if match:
                return match.group(1)
            # Look for "Jun 10, 2026"
            try:
                parsed = datetime.strptime(date_text, '%b %d, %Y')
                return parsed.strftime('%Y-%m-%d')
            except:
                pass
            # Look for "June 10, 2026"
            try:
                parsed = datetime.strptime(date_text, '%B %d, %Y')
                return parsed.strftime('%Y-%m-%d')
            except:
                pass
    return None

def get_today_articles():
    today = datetime.now().strftime("%Y-%m-%d")
    articles = []
    
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Try various article container selectors
        containers = []
        for selector in ['div.post', 'article', 'div.teaser', 'div.listing-item', 'div.news-item']:
            containers = soup.select(selector)
            if containers:
                print(f"Found {len(containers)} items with selector: {selector}")
                break
        
        if not containers:
            print("No article containers found. Falling back to first 10 relevant links.")
            # Fallback: find all links that look like articles, no date filtering
            for a in soup.find_all('a', href=True):
                href = a['href']
                if is_likely_article_url(href):
                    title = a.get_text(strip=True)
                    if title and len(title) > 20:
                        if not href.startswith('http'):
                            href = BASE_URL + href
                        articles.append({
                            "title": title,
                            "link": href,
                            "excerpt": ""
                        })
                        if len(articles) >= 10:
                            break
            return articles
        
        # Process containers
        for item in containers[:30]:  # limit to 30 to avoid too many
            # Find title link
            title_tag = item.select_one('h2 a, h3 a, .title a, a')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            if not title or len(title) < 15:
                continue
            link = title_tag.get('href')
            if not link:
                continue
            if not link.startswith('http'):
                link = BASE_URL + link
            # Skip non-article links
            if not is_likely_article_url(link):
                continue
            
            # Extract date
            article_date = extract_date_from_article(item)
            # If no date found, assume it's recent but we'll still include (with a warning)
            if article_date is None:
                # Only include if we haven't already exceeded 15 (assume recent)
                if len(articles) < 15:
                    print(f"No date for: {title[:50]}... assuming recent.")
                    excerpt_tag = item.select_one('.excerpt, .summary, p')
                    excerpt = excerpt_tag.get_text(strip=True) if excerpt_tag else ""
                    articles.append({
                        "title": title,
                        "link": link,
                        "excerpt": excerpt[:300]
                    })
                continue
            
            # Keep only today's articles
            if article_date == today:
                excerpt_tag = item.select_one('.excerpt, .summary, p')
                excerpt = excerpt_tag.get_text(strip=True) if excerpt_tag else ""
                articles.append({
                    "title": title,
                    "link": link,
                    "excerpt": excerpt[:300]
                })
        
        print(f"Found {len(articles)} articles for {today}")
        
        # Limit to 20 to avoid token overflow
        if len(articles) > 20:
            articles = articles[:20]
            
    except Exception as e:
        print(f"Error fetching news: {e}")
    
    return articles
