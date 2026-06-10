import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://www.supplychain247.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def parse_date(date_str):
    """Parse date like 'June 10, 2026' or 'Jun 10, 2026' into YYYY-MM-DD."""
    date_str = date_str.strip()
    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None

def get_today_articles():
    today = datetime.now().strftime("%Y-%m-%d")
    articles = []
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Find all article containers (div with id="cc")
        article_blocks = soup.select("div#cc")
        print(f"Found {len(article_blocks)} article blocks on main page")
        
        for block in article_blocks:
            # Title and link
            title_tag = block.find("a", class_="news-head")
            if not title_tag:
                # Fallback: any <a> that is not in a menu
                title_tag = block.find("a", href=True)
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            if not title:
                continue
            href = title_tag.get("href")
            if not href:
                continue
            full_url = href if href.startswith("http") else BASE_URL + href
            
            # Date
            date_span = block.find("span", itemprop="datePublished")
            if not date_span:
                # Sometimes date is inside a <div class="dateline">
                date_div = block.find("div", class_="dateline")
                if date_div:
                    date_span = date_div.find("span", itemprop="datePublished")
            if not date_span:
                print(f"Skipping '{title[:40]}...' – no date found")
                continue
            date_text = date_span.get_text(strip=True)
            article_date = parse_date(date_text)
            if article_date is None:
                print(f"Could not parse date '{date_text}' for '{title[:40]}...'")
                continue
            
            if article_date == today:
                # Excerpt
                excerpt_div = block.find("div", class_="text")
                excerpt = excerpt_div.get_text(strip=True) if excerpt_div else ""
                articles.append({
                    "title": title,
                    "link": full_url,
                    "excerpt": excerpt[:300]
                })
                print(f"✓ Added: {title[:50]}... ({article_date})")
            else:
                print(f"✗ Skipped: {title[:40]}... ({article_date})")
        
        print(f"Total articles for {today}: {len(articles)}")
        # Limit to 15 to avoid token overflow
        if len(articles) > 15:
            articles = articles[:15]
            
    except Exception as e:
        print(f"Error: {e}")
    
    return articles
