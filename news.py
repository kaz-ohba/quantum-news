import feedparser
import anthropic
import os
from datetime import datetime

QUANTUM_FEEDS = [
    "https://news.google.com/rss/search?q=量子コンピュータ&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=quantum+computing&hl=en&gl=US&ceid=US:en",
]

PACKAGING_FEEDS = [
    "https://news.google.com/rss/search?q=半導体+アドバンストパッケージング&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=advanced+packaging+semiconductor&hl=en&gl=US&ceid=US:en",
]

def fetch_articles(feeds, max_per_feed=5):
    articles = []
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries[:max_per_feed]:
            articles.append({
                "title": entry.title,
                "summary": entry.get("summary", ""),
                "link": entry.link,
            })
    return articles[:10]

def summarize(articles, topic):
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
            "content": f"以下の{topic}関連ニュースを日本語で簡潔に要約してください。各記事を2〜3文でまとめ、箇条書きにしてください。\n\n{text}"
        }]
    )
    return message.content[0].text

if __name__ == "__main__":
    print("=== 量子コンピュータ ニュース（10件）===")
    quantum_articles = fetch_articles(QUANTUM_FEEDS)
    print(f"{len(quantum_articles)}件取得。要約中...")
    quantum_summary = summarize(quantum_articles, "量子コンピュータ")
    print(quantum_summary)

    print("\n=== 半導体アドバンストパッケージング ニュース（10件）===")
    packaging_articles = fetch_articles(PACKAGING_FEEDS)
    print(f"{len(packaging_articles)}件取得。要約中...")
    packaging_summary = summarize(packaging_articles, "半導体アドバンストパッケージング")
    print(packaging_summary)

    print("\n完了！")
