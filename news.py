import feedparser
import anthropic
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

QUANTUM_FEEDS = [
    "https://news.google.com/rss/search?q=量子コンピュータ&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=quantum+computing&hl=en&gl=US&ceid=US:en",
    "https://feeds.feedburner.com/IeeeSpectrum",
    "https://rss.arxiv.org/rss/quant-ph",
]

PACKAGING_FEEDS = [
    "https://news.google.com/rss/search?q=半導体+アドバンストパッケージング&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=advanced+packaging+semiconductor&hl=en&gl=US&ceid=US:en",
    "https://semiengineering.com/feed/",
    "https://www.eetimes.com/feed/",
]

PHOTONICS_FEEDS = [
    "https://news.google.com/rss/search?q=光電融合&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=シリコンフォトニクス&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=silicon+photonics&hl=en&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=optical+electrical+convergence&hl=en&gl=US&ceid=US:en",
]

TO_ADDRESSES = [
    "ohba.kazuhiro@gmail.com",
    "kazuhiro.oba.ti@icloud.com",
]

def shorten_url(url, max_length=60):
    if len(url) <= max_length:
        return url
    return url[:max_length] + "..."

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

def send_email(quantum_summary, packaging_summary, photonics_summary,
               quantum_articles, packaging_articles, photonics_articles):
    today = datetime.now().strftime("%Y/%m/%d")

    quantum_links = "\n".join([f"・{a['title']}\n  {shorten_url(a['link'])}" for a in quantum_articles])
    packaging_links = "\n".join([f"・{a['title']}\n  {shorten_url(a['link'])}" for a in packaging_articles])
    photonics_links = "\n".join([f"・{a['title']}\n  {shorten_url(a['link'])}" for a in photonics_articles])

    body = f"""量子・半導体・光電融合 ニュースダイジェスト ({today})

=== 量子コンピュータ ニュース ===
{quantum_summary}

【元記事】
{quantum_links}

=== 半導体アドバンストパッケージング ニュース ===
{packaging_summary}

【元記事】
{packaging_links}

=== 光電融合・シリコンフォトニクス ニュース ===
{photonics_summary}

【元記事】
{photonics_links}
"""

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = f"【技術ニュース】{today}"
    msg["From"] = os.environ["GMAIL_ADDRESS"]
    msg["To"] = ", ".join(TO_ADDRESSES)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.environ["GMAIL_ADDRESS"], os.environ["GMAIL_APP_PASSWORD"])
        smtp.sendmail(os.environ["GMAIL_ADDRESS"], TO_ADDRESSES, msg.as_string())

if __name__ == "__main__":
    print("量子コンピュータ記事を取得中...")
    quantum_articles = fetch_articles(QUANTUM_FEEDS)
    quantum_summary = summarize(quantum_articles, "量子コンピュータ")

    print("半導体パッケージング記事を取得中...")
    packaging_articles = fetch_articles(PACKAGING_FEEDS)
    packaging_summary = summarize(packaging_articles, "半導体アドバンストパッケージング")

    print("光電融合・シリコンフォトニクス記事を取得中...")
    photonics_articles = fetch_articles(PHOTONICS_FEEDS)
    photonics_summary = summarize(photonics_articles, "光電融合・シリコンフォトニクス")

    print("メール送信中...")
    send_email(quantum_summary, packaging_summary, photonics_summary,
               quantum_articles, packaging_articles, photonics_articles)
    print("完了！")
