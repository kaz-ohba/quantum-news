import feedparser
import anthropic
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

def build_section(title, summary, articles):
    summary_html = "".join([
        f'<p style="margin:8px 0; line-height:1.7;">{line}</p>'
        if line.strip() else ""
        for line in summary.split("\n")
    ])
    links_html = "\n".join([
        f'<li style="margin:6px 0;"><a href="{a["link"]}" style="color:#1a73e8;">{a["title"]}</a></li>'
        for a in articles
    ])
    return f"""
<h2 style="color:#1a73e8; border-bottom:2px solid #1a73e8; padding-bottom:6px;">{title}</h2>
{summary_html}
<h3 style="color:#555; margin-top:16px;">元記事</h3>
<ul style="padding-left:20px;">
{links_html}
</ul>
"""

def send_email(quantum_summary, packaging_summary, photonics_summary,
               quantum_articles, packaging_articles, photonics_articles):
    today = datetime.now().strftime("%Y/%m/%d")

    html_body = f"""
<html>
<body style="font-family:sans-serif; max-width:700px; margin:auto; padding:20px;">
<h1 style="color:#333;">量子・半導体・光電融合 ニュースダイジェスト</h1>
<p style="color:#888;">{today}</p>
{build_section("量子コンピュータ ニュース", quantum_summary, quantum_articles)}
{build_section("半導体アドバンストパッケージング ニュース", packaging_summary, packaging_articles)}
{build_section("光電融合・シリコンフォトニクス ニュース", photonics_summary, photonics_articles)}
</body>
</html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"【技術ニュース】{today}"
    msg["From"] = os.environ["GMAIL_ADDRESS"]
    msg["To"] = ", ".join(TO_ADDRESSES)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

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
