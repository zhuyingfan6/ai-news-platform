import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def summarize_daily_news(articles, language="zh"):
    """根据语言生成每日新闻简报。language: 'zh' 或 'en'"""
    if not articles:
        return "今日无新闻。" if language == "zh" else "No news today."
    
    news_text = "\n".join(
        [f"- Title: {a['title']}\n  Summary: {a['excerpt']}\n  Link: {a['link']}" for a in articles]
    )
    
    if language == "zh":
        system_prompt = "你是一个专业的供应链新闻编辑。"
        user_prompt = f"""请根据以下今日新闻列表，生成一份简洁的每日供应链新闻简报（中文），包括：
1. 总体概要（1-2句）；
2. 按主题分类的重点新闻摘要，每条新闻用简短的 bullet point 说明关键信息；
3. 重要的原文链接。

新闻列表：
{news_text}"""
    else:  # English
        system_prompt = "You are a professional supply chain news editor."
        user_prompt = f"""Based on the following daily news list, generate a concise supply chain news brief in English, including:
1. Overall summary (1-2 sentences);
2. Key news points organized by topic, each with a short bullet point;
3. Important original links.

News list:
{news_text}"""
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 总结出错 / Error: {e}"


def extract_key_points_from_report(report_text, language="zh"):
    """根据语言对上传的报告进行重点提取。language: 'zh' 或 'en'"""
    if language == "zh":
        system_prompt = "你是一个顶尖的供应链管理咨询顾问。"
        user_prompt = f"""请对以下这份供应链行业报告进行专业整理，要求：
1. 提取报告的核心主题和关键结论；
2. 罗列所有重要的数据、趋势和观点，用清晰的层次结构呈现；
3. 给出3-5个 actionable 的要点或风险提示；
4. 全文用中文输出，但保留关键英文术语。

报告内容：
{report_text}"""
    else:
        system_prompt = "You are a top supply chain management consultant."
        user_prompt = f"""Please analyze the following supply chain industry report and provide a structured summary in English:
1. Extract the core themes and key conclusions;
2. List all important data, trends, and insights in a clear hierarchical structure;
3. Provide 3-5 actionable recommendations or risk alerts;
4. Keep any critical industry terms in their original language if necessary.

Report content:
{report_text}"""
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=2500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 分析出错 / Error: {e}"
