from fetch_news import get_today_articles
from summarizer import summarize_daily_news
from datetime import datetime
import os

def main():
    print("开始抓取今日新闻...")
    articles = get_today_articles()
    print(f"获取到 {len(articles)} 篇文章")
    
    if not articles:
        print("无新闻，退出。")
        return

    date_str = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("daily_briefs", exist_ok=True)

    # 生成中文简报
    print("生成中文简报...")
    zh_summary = summarize_daily_news(articles, language="zh")
    with open(f"daily_briefs/{date_str}_zh.md", "w", encoding="utf-8") as f:
        f.write(f"# Supply Chain 24/7 每日新闻简报 - {date_str}\n\n")
        f.write(zh_summary)

    # 生成英文简报
    print("生成英文简报...")
    en_summary = summarize_daily_news(articles, language="en")
    with open(f"daily_briefs/{date_str}_en.md", "w", encoding="utf-8") as f:
        f.write(f"# Supply Chain 24/7 Daily News Brief - {date_str}\n\n")
        f.write(en_summary)

    print(f"简报已保存：{date_str}_zh.md 和 {date_str}_en.md")

if __name__ == "__main__":
    main()
