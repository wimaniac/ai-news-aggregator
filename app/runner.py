from typing import List
from app.config import YOUTUBE_CHANNELS, NEWS_RSS_FEEDS
from app.scrapers.youtube import YoutubeScraper, ChannelVideo
from app.scrapers.news import WebScraper, Article
from app.database.repository import Repository

def run_scrapers(hours: int = 24) -> dict:
    youtube_scraper = YoutubeScraper()
    news_scraper = WebScraper()
    repo = Repository()
    
    youtube_videos = []
    video_dicts = []
    for channel_id in YOUTUBE_CHANNELS:
        # Gọi hàm scrape_channel để lấy cả transcript
        videos = youtube_scraper.scrape_channel(channel_id, hours=hours)
        youtube_videos.extend(videos)
        video_dicts.extend([
            {
                "video_id": v.video_id,
                "title": v.title,
                "url": v.url,
                "channel_id": channel_id,
                "published_at": v.published_at,
                "description": v.description,
                "transcript": v.transcript  # Thêm transcript vào đây
            }
            for v in videos
        ])
            
    news_articles = []
    for rss_url in NEWS_RSS_FEEDS:
        articles = news_scraper.scrape_rss_feed(rss_url, hours=hours)
        news_articles.extend(articles)
    
    if video_dicts:
        repo.bulk_create_youtube_videos(video_dicts)
    if news_articles:
        article_dicts = [
            {
                "title": a.title,
                "url": a.url,
                "source": a.source,
                "published_at": a.published_at,
                "content": a.content
            }
            for a in news_articles
        ]
        repo.bulk_create_news_articles(article_dicts)
            
    return {
        "youtube": youtube_videos,
        "news": news_articles,
    }
    
if __name__ == "__main__":
    result = run_scrapers(hours=300)
    print(f"Scraped {len(result['youtube'])} YouTube videos and {len(result['news'])} news articles.")