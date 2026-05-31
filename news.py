import feedparser
import anthropic
import os
from datetime import datetime

# RSS フィードのURL一覧
FEEDS = [
    "https://news.google.com/rss/search?q=量子コンピュータ&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=quantum+computing&hl=en&gl=US&ceid=US:en",
]

def fetch_articles():
    articles = []
    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:  # 各フィードから最大5件
            articles.append({
                "title": entry.title,
                "summary": entry.get("summary", ""),
                "link": entry.link,
            })
    return articles

def summarize(articles):
    text = "\n\n".join([
        f"{i+1}. {a['title']}\n{a['summary']}"
        for i, a in enumerate(articles)
    ])

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"以下の量子コンピュータ関連ニュースを日本語で簡潔に要約してください。各記事を2〜3文でまとめ、箇条書きにしてください。\n\n{text}"
        }]
    )
    return message.content[0].text

if __name__ == "__main__":
    print("記事を取得中...")
    articles = fetch_articles()
    print(f"{len(articles)}件取得。要約中...")
    summary = summarize(articles)
    print("=== 本日のまとめ ===")
    print(summary)
    print("===================")
