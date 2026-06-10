import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

BASE_URL = "https://www.supplychain247.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def get_article_date(article_url):
    """从文章详情页提取发布日期"""
    try:
        resp = requests.get(article_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        date_span = soup.find("span", itemprop="datePublished")
        if date_span:
            date_text = date_span.get_text(strip=True)
            # 解析日期格式 "June 9, 2026"
            return datetime.strptime(date_text, "%B %d, %Y").strftime("%Y-%m-%d")
        return None
    except Exception as e:
        print(f"日期提取失败 {article_url}: {e}")
        return None

def get_today_articles():
    today = datetime.now().strftime("%Y-%m-%d")
    articles = []
    
    try:
        # Step 1: 获取首页新闻列表
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        news_links = soup.find_all("a", class_="news-head")
        
        # 降级：如果没有找到 news-head，尝试其他通用选择器
        if not news_links:
            news_links = soup.select("a[href*='/article/']")
        
        print(f"发现 {len(news_links)} 个可能新闻链接")
        
        # Step 2: 依次抓取并过滤
        for link in news_links[:30]:  # 限制扫描数量
            title = link.get_text(strip=True)
            href = link.get("href")
            full_url = href if href.startswith("http") else BASE_URL + href
            
            # 过滤非新闻类链接
            if not ("/article/" in full_url or "/news/" in full_url):
                continue
            
            # Step 3: 获取发布日期
            article_date = get_article_date(full_url)
            if article_date and article_date == today:
                articles.append({
                    "title": title,
                    "link": full_url,
                    "excerpt": ""  # 备用字段, 可留空
                })
                print(f"[✓] 采纳 {title[:40]}... ({article_date})")
            else:
                print(f"[✗] 跳过 {title[:40]}... 日期={article_date or '未获取到'}")
            
            time.sleep(0.3)  # 礼貌性等待
        
        print(f"\n总计今日新闻: {len(articles)} 条")
        return articles[:15]  # 控制最终数量
    
    except Exception as e:
        print(f"抓取异常: {e}")
        return []
