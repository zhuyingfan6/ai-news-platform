import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://www.supplychain247.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def get_today_articles():
    articles = []
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Try multiple possible selectors for article containers
        possible_selectors = [
            "div.post",           # old pattern
            "article",            # common pattern
            "div.news-item",      # alternative
            "div.teaser",         # another
            "div.listing-item",   # another
        ]
        
        items = []
        for selector in possible_selectors:
            items = soup.select(selector)
            if items:
                print(f"Found {len(items)} items using selector: {selector}")
                break
        
        # If no items found, fallback to finding all <a> tags that look like news links
        if not items:
            print("No items with standard selectors, searching for <a> tags...")
            for a in soup.find_all('a', href=True):
                title = a.get_text(strip=True)
                # Filter likely news titles (at least 20 chars, not "Read more", etc.)
                if title and len(title) > 20 and "read more" not in title.lower():
                    link = a['href']
                    if not link.startswith("http"):
                        link = BASE_URL + link
                    items.append({
                        'title': title,
                        'link': link,
                        'excerpt': ""  # We'll try to get excerpt from parent
                    })
            # Convert list of dicts to list of tag-like objects (simulate)
            # But easier: we'll handle directly
            for item in items:
                articles.append(item)
            return articles
        
        # Process items found via selector
        for item in items:
            # Try to find title link
            title_tag = item.select_one("h2 a, h3 a, .title a, a")
            if not title_tag:
                # If no title link, look for any <a> with text
                title_tag = item.find('a', href=True)
            if not title_tag:
                continue
            
            title = title_tag.get_text(strip=True)
            if not title:
                continue
                
            link = title_tag.get("href")
            if link and not link.startswith("http"):
                link = BASE_URL + link
            
            # Try to get excerpt / summary
            excerpt_tag = item.select_one(".excerpt, .summary, .description, p")
            excerpt = excerpt_tag.get_text(strip=True) if excerpt_tag else ""
            
            articles.append({
                "title": title,
                "link": link,
                "excerpt": excerpt[:300]  # limit length
            })
    except Exception as e:
        print(f"抓取失败: {e}")
    
    return articles
