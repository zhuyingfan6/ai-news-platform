import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

BASE_URL = "https://www.supplychain247.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def get_article_date(article_url):
    """Fetch the article page and extract the date."""
    try:
        resp = requests.get(article_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        date_span = soup.find("span", itemprop="datePublished")
        if date_span:
            date_text = date_span.get_text(strip=True)
            print(f"  Date found: {date_text} for {article_url}")
            try:
                parsed = datetime.strptime(date_text, "%B %d, %Y")
                return parsed.strftime("%Y-%m-%d")
            except Exception as e:
                print(f"  Date parse error: {e}")
        else:
            print(f"  No date span found for {article_url}")
        return None
    except Exception as e:
        print(f"  Error fetching article page: {e}")
        return None

def get_today_articles():
    today = datetime.now().strftime("%Y-%m-%d")
    articles = []
    
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Look for all <a> tags with class "news-head"
        article_links = soup.find_all("a", class_="news-head")
        print(f"Found {len(article_links)} links with class 'news-head'")
        
        # If none found, try other common selectors
        if not article_links:
            article_links = soup.select("a[href*='/article/']")
            print(f"Fallback: found {len(article_links)} links containing '/article/'")
        
        for i, link in enumerate(article_links[:15]):  # limit to 15
            title = link.get_text(strip=True)
            href = link.get("href")
            if not href:
                continue
            if href.startswith("/"):
                full_url = BASE_URL + href
            else:
                full_url = href
            
            print(f"\n[{i+1}] Checking: {title[:50]}...")
            print(f"    URL: {full_url}")
            
            date_str = get_article_date(full_url)
            if date_str:
                print(f"    Parsed date: {date_str}, Today: {today}")
                if date_str == today:
                    articles.append({
                        "title": title,
                        "link": full_url,
                        "excerpt": ""
                    })
                    print(f"    -> Added")
                else:
                    print(f"    -> Skipped (not today)")
            else:
                print(f"    -> No date, skipping")
            
            time.sleep(0.5)  # be polite to the server
        
        print(f"\nTotal articles for {today}: {len(articles)}")
        
    except Exception as e:
        print(f"Error fetching news: {e}")
    
    return articles
