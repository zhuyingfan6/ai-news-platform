import os
import pathlib
from datetime import datetime
from fetch_news import get_today_articles
from summarizer import summarize_daily_news

# ---------- 使用绝对路径 ----------
APP_DIR = pathlib.Path(__file__).parent
BRIEF_DIR = APP_DIR / "daily_briefs"

def main():
    print("开始抓取今日新闻...")
    articles = get_today_articles()
    print(f"获取到 {len(articles)} 篇文章")
    
    if not articles:
        print("无新闻，退出。")
        return

    # 确保简报目录存在
    BRIEF_DIR.mkdir(exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")

    # 生成中文简报
    print("生成中文简报...")
    try:
        zh_summary = summarize_daily_news(articles, language="zh")
        zh_file = BRIEF_DIR / f"{date_str}_zh.md"
        with open(zh_file, "w", encoding="utf-8") as f:
            f.write(f"# Supply Chain 24/7 每日新闻简报 - {date_str}\n\n")
            f.write(zh_summary)
        print(f"中文简报已保存：{zh_file}")
    except Exception as e:
        print(f"生成中文简报失败：{e}")

    # 生成英文简报
    print("生成英文简报...")
    try:
        en_summary = summarize_daily_news(articles, language="en")
        en_file = BRIEF_DIR / f"{date_str}_en.md"
        with open(en_file, "w", encoding="utf-8") as f:
            f.write(f"# Supply Chain 24/7 Daily News Brief - {date_str}\n\n")
            f.write(en_summary)
        print(f"英文简报已保存：{en_file}")
    except Exception as e:
        print(f"生成英文简报失败：{e}")

    print("简报生成完成")

if __name__ == "__main__":
    main()
