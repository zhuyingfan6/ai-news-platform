import os
import streamlit as st
from openai import OpenAI

# ---------- 智能获取 API Key ----------
# 优先级: Streamlit secrets > 环境变量
def get_api_key():
    # 尝试从 Streamlit secrets 读取
    try:
        api_key = st.secrets.get("DEEPSEEK_API_KEY")
        if api_key:
            return api_key
    except Exception:
        pass  # 不在 Streamlit 环境中时忽略
    
    # 回退到环境变量
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError(
            "未找到 DEEPSEEK_API_KEY。请在 Streamlit secrets 或环境变量中设置。"
        )
    return api_key

# 初始化客户端
try:
    api_key = get_api_key()
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )
except Exception as e:
    client = None
    print(f"警告: OpenAI 客户端初始化失败 - {e}")

def summarize_daily_news(articles, language="zh"):
    """根据语言生成每日新闻简报。language: 'zh' 或 'en'"""
    if not articles:
        return "今日无新闻。" if language == "zh" else "No news today."
    
    news_text = "\n".join(
        [f"- Title: {a['title']}\n  Summary: {a['excerpt']}\n  Link: {a['link']}" for a in articles]
    )
    
    if language == "zh":
        system_prompt = "你是一个专业的供应链新闻编辑。"
        user_prompt = f"""请根据以下今日新闻列表，生成一份简洁的每日供应链新闻简报（中文）。要求：
1. 总体概要（1-2句）。
2. 按主题分类的重点新闻摘要。每条新闻用一个短 bullet point（以 "- " 开头），每个 bullet point 末尾必须紧跟一个 " [Read more](链接)" 格式的链接。
3. 绝对不要出现单独的“原文链接”列表或任何额外的链接汇总。
4. 每个 bullet point 单独成行，保持清晰缩进。

新闻列表：
{news_text}"""
    else:  # English
        system_prompt = "You are a professional supply chain news editor."
        user_prompt = f"""Based on the following daily news list, generate a concise supply chain news brief in English. Requirements:
1. Overall summary (1-2 sentences).
2. Key news points organized by topic, each as a single bullet point (starting with "- "). Immediately after each bullet point, include a " [Read more](link)".
3. Do NOT create a separate "Original links" section or any other link list.
4. Each bullet point on its own line, proper indentation.

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
    if not client:
        return "错误: AI 客户端未初始化，请检查 API Key 配置。" if language == "zh" else "Error: AI client not initialized. Check API key."
    
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
