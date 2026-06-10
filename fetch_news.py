import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

BASE_URL = "https://www.supplychain247.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def get_article_date(article_url):
    """Fetch the article page and extract the date from schema.org markup."""
    try:
        resp = requests.get(article_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        # Look for the date in schema.org format
        date_span = soup.find("span", itemprop="datePublished")
        if date_span:
            date_text = date_span.get_text(strip=True)
            # Parse date like "June 9, 2026"
            try:
                parsed_date = datetime.strptime(date_text, "%B %d, %Y")
                return parsed_date.strftime("%Y-%m-%d")
            except:
                pass
        return None
    except Exception:
        return None

def get_today_articles():
    today = datetime.now().strftime("%Y-%m-%d")
    articles = []
    
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Find all article links with class "news-head"
        article_links = soup.find_all("a", class_="news-head")
        print(f"Found {len(article_links)} article links on main page")
        
        for link in article_links[:30]:  # Process up to 30 to avoid too many requests
            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                continue
            
            href = link.get("href")
            if not href:
                continue
            
            # Build full URL
            if href.startswith("/"):
                full_url = BASE_URL + href
            elif not href.startswith("http"):
                full_url = BASE_URL + "/" + href
            else:
                full_url = href
            
            # Skip non-article URLs
            if not ("/article/" in full_url or "/news/" in full_url):
                continue
            
            # Get the article's publication date
            article_date = get_article_date(full_url)
            if article_date and article_date == today:
                articles.append({
                    "title": title,
                    "link": full_url,
                    "excerpt": ""  # Will be filled by AI from the article content
                })
                print(f"✓ {title[:50]}... ({article_date})")
        
        print(f"Found {len(articles)} articles published today ({today})")
        
        # Limit to 15 to stay within token limits
        if len(articles) > 15:
            articles = articles[:15]
            
    except Exception as e:
        print(f"Error fetching news: {e}")
    
    return articles
