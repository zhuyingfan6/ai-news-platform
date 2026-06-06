import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def summarize_daily_news(articles):
    if not articles:
        return "今日无新闻。"
    news_text = "\n".join(
        [f"- 标题：{a['title']}\n  摘要：{a['excerpt']}\n  链接：{a['link']}" for a in articles]
    )
    prompt = f"""你是一个专业的供应链新闻编辑。请根据以下今日新闻列表，生成一份简洁的每日供应链新闻简报（中文），包括：1. 总体概要（1-2句）；2. 按主题分类的重点新闻摘要，每条新闻用简短的 bullet point 说明关键信息；3. 重要的原文链接。新闻列表如下：
{news_text}"""
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的供应链新闻分析师。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 总结出错：{e}"

def extract_key_points_from_report(report_text):
    prompt = f"""请对以下这份供应链行业报告进行专业整理，要求：
1. 提取报告的核心主题和关键结论；
2. 罗列所有重要的数据、趋势和观点，用清晰的层次结构呈现；
3. 给出3-5个 actionable 的要点或风险提示；
4. 全文用中文输出，但保留关键英文术语。
报告内容：
{report_text[:8000]}"""
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个顶尖的供应链管理咨询顾问。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 分析出错：{e}"
