from fetch_news import get_today_articles
from summarizer import summarize_daily_news
from datetime import datetime
import os

def main():
    print("开始抓取今日新闻...")
    articles = get_today_articles()
    print(f"获取到 {len(articles)} 篇文章")
    summary = summarize_daily_news(articles)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("daily_briefs", exist_ok=True)
    filename = f"daily_briefs/{date_str}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Supply Chain 24/7 每日新闻简报 - {date_str}\n\n")
        f.write(summary)
    print(f"简报已保存至 {filename}")

if __name__ == "__main__":
    main()
