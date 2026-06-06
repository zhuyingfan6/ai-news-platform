#!/bin/bash
cd /Users/Isabella/ai-news-platform
source venv/bin/activate
python daily_news_job.py >> logs/daily_job.log 2>&1
