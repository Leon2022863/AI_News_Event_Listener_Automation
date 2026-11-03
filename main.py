import os
import time
import requests
import feedparser
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Trusted AI & Tech Feeds
FEEDS = {
    "OpenAI News": "https://openai.com/news/rss.xml",
    "The Verge AI": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"
}

seen_titles = set()

def fetch_and_route_news():
    """Polls feeds and dispatches unread events to Discord."""
    if not DISCORD_WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL environment variable is missing!")
        return

    for source_name, feed_url in FEEDS.items():
        print(f"Checking feed: {source_name}...")
        parsed_feed = feedparser.parse(feed_url)

        # Process in reverse order so older unread items post first
        for entry in reversed(parsed_feed.entries):
            title = entry.title
            link = entry.link

            # Deduplication logic
            if title in seen_titles:
                continue

            print(f"New event detected from [{source_name}]: {title}")
            send_discord_embed(source_name, title, link)
            seen_titles.add(title)

def send_discord_embed(source_name, title, link):
    """Sends formatted rich embeds to the Discord webhook."""
    payload = {
        "embeds": [
            {
                "title": f"🤖 {source_name}: {title}",
                "url": link,
                "color": 3447003,  # Tech Blue
                "footer": {"text": f"Event Source: {source_name} | Automated AI News Gateway"}
            }
        ]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code in [200, 204]:
            print(f"Successfully routed: {title}")
        else:
            print(f"Failed to post to Discord (HTTP {response.status_code})")
    except Exception as e:
        print(f"Error firing webhook: {e}")

if __name__ == "__main__":
    print("Starting AI News Event-Driven Gateway...")
    # Event Polling Loop (Runs continuously every 3 minutes)
    while True:
        fetch_and_route_news()
        time.sleep(180)