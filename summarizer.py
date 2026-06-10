import os
import streamlit as st
from openai import OpenAI

# ---------- 智能获取 API Key ----------
def get_api_key():
    try:
        # Streamlit Cloud secrets
        api_key = st.secrets.get("DEEPSEEK_API_KEY")
        if api_key:
            return api_key
    except Exception:
        pass
    # Local environment variable
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not found in secrets or environment")
    return api_key

# Initialize client
api_key = get_api_key()
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def summarize_daily_news(articles, language="zh"):
    """Generate daily news brief."""
    if not articles:
        return "今日无新闻。" if language == "zh" else "No news today."
    
    news_text = "\n".join(
        [f"- Title: {a['title']}\n  Summary: {a['excerpt']}\n  Link: {a['link']}" for a in articles]
    )
    
    if language == "zh":
        system_prompt = "你是一个专业的供应链新闻编辑。输出必须使用严格的 Markdown 格式。"
        user_prompt = f"""请根据以下今日新闻列表，生成一份简洁的每日供应链新闻简报（中文）。严格要求：
1. 第一行：总体概要（1-2句话）。
2. 然后按主题分类，每个主题下用 bullet points 列出新闻要点。
3. 每个 bullet point 单独成行，格式为：`- 新闻简述 [Read more](链接)`
4. 禁止出现单独的“原文链接”列表或任何额外的链接汇总。
5. 每个 bullet point 之间留一个空行以便阅读。

新闻列表：
{news_text}"""
    else:
        system_prompt = "You are a professional supply chain news editor. Output must be strict Markdown."
        user_prompt = f"""Based on the following daily news list, generate a concise supply chain news brief in English. Strict requirements:

1. First line: overall summary (1-2 sentences).
2. Then organize by topic. Under each topic, list news points as bullet points.
3. **Each bullet point MUST be on its own separate line.**
4. Format each bullet point as: `- News summary [Read more](link)`
5. Use the original link from the news list.
6. Do NOT create a separate "Original links" section or any extra link list.
7. Leave a blank line between bullet points for readability.

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
    """Extract key points from uploaded report."""
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
