def summarize_daily_news(articles, language="zh"):
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
    else:  # English
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
