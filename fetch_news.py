import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://www.supplychain247.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def get_today_articles():
    today = datetime.now().strftime("%Y-%m-%d")
    articles = []
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        # 下面这行选择器可能需要根据网站实际结构调整
        for item in soup.select("div.post"):
            title_tag = item.select_one("h2.title a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]
            if not link.startswith("http"):
                link = BASE_URL + link
            excerpt_tag = item.select_one("div.excerpt")
            excerpt = excerpt_tag.get_text(strip=True) if excerpt_tag else ""
            articles.append({
                "title": title,
                "link": link,
                "excerpt": excerpt
            })
    except Exception as e:
        print(f"抓取失败: {e}")
    return articles
