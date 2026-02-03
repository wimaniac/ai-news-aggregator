from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import YoutubeVideo, NewsArticle  # Import từ models của bạn
from .connection import get_session     # Import hàm lấy session

class Repository:
    def __init__(self, session: Optional[Session] = None):
        # Nếu không truyền session vào thì tự tạo một cái mới
        self.session = session or get_session()

    # --- CHỨC NĂNG CHO YOUTUBE ---
    def create_youtube_video(self, video_data: Dict[str, Any]) -> Optional[YoutubeVideo]:
        """Lưu video YouTube mới, bỏ qua nếu đã tồn tại"""
        existing = self.session.query(YoutubeVideo).filter_by(video_id=video_data['video_id']).first()
        if existing:
            return None
        
        video = YoutubeVideo(
            video_id=video_data['video_id'],
            title=video_data['title'],
            url=video_data['url'],
            channel_id=video_data['channel_id'],
            published_at=video_data['published_at'],
            description=video_data.get('description', ""),
            transcript=video_data.get('transcript')
        )
        self.session.add(video)
        self.session.commit()
        return video

    # --- CHỨC NĂNG CHO BÁO CHÍ (CÔNG AN, BLOG...) ---
    def create_news_article(self, article_data: Dict[str, Any]) -> Optional[NewsArticle]:
        """Lưu bài báo mới, check trùng dựa trên URL"""
        existing = self.session.query(NewsArticle).filter_by(url=article_data['url']).first()
        if existing:
            return None
            
        article = NewsArticle(
            title=article_data['title'],
            url=article_data['url'],
            source=article_data['source'],
            published_at=article_data['published_at'],
            content=article_data.get('content'),
            summary=article_data.get('summary')
        )
        self.session.add(article)
        self.session.commit()
        return article

    def bulk_create_youtube_videos(self, videos_data: List[Dict[str, Any]]):
        videos_to_add = []
        for video_data in videos_data:
            existing = self.session.query(YoutubeVideo).filter_by(video_id=video_data['video_id']).first()
            if not existing:
                video = YoutubeVideo(
                    video_id=video_data['video_id'],
                    title=video_data['title'],
                    url=video_data['url'],
                    channel_id=video_data['channel_id'],
                    published_at=video_data['published_at'],
                    description=video_data.get('description', ""),
                    transcript=video_data.get('transcript')
                )
                videos_to_add.append(video)
        
        if videos_to_add:
            self.session.add_all(videos_to_add)
            self.session.commit()

    def bulk_create_news_articles(self, articles_data: List[Dict[str, Any]]):
        articles_to_add = []
        for article_data in articles_data:
            existing = self.session.query(NewsArticle).filter_by(url=article_data['url']).first()
            if not existing:
                article = NewsArticle(
                    title=article_data['title'],
                    url=article_data['url'],
                    source=article_data['source'],
                    published_at=article_data['published_at'],
                    content=article_data.get('content'),
                    summary=article_data.get('summary')
                )
                articles_to_add.append(article)

        if articles_to_add:
            self.session.add_all(articles_to_add)
            self.session.commit()

    # --- CHỨC NĂNG CẬP NHẬT TÓM TẮT (SAU KHI AI CHẠY) ---
    def update_article_summary(self, article_id: int, summary: str):
        article = self.session.query(NewsArticle).filter_by(id=article_id).first()
        if article:
            article.summary = summary
            self.session.commit()

    def update_video_summary(self, video_id: str, summary: str):
        video = self.session.query(YoutubeVideo).filter_by(video_id=video_id).first()
        if video:
            video.summary = summary
            self.session.commit()

    # --- TRUY VẤN DỮ LIỆU MỚI ĐỂ HIỂN THỊ ---
    def get_latest_content(self, hours: int = 24):
        """Lấy tất cả video và bài báo mới nhất để làm báo cáo"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        articles = self.session.query(NewsArticle).filter(NewsArticle.created_at >= cutoff).all()
        videos = self.session.query(YoutubeVideo).filter(YoutubeVideo.created_at >= cutoff).all()
        
        return {
            "articles": articles,
            "videos": videos
        }