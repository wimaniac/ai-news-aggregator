from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import YoutubeVideo, NewsArticle, Digest  # Import từ models của bạn
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
            content=article_data.get('content')
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
                    content=article_data.get('content')
                )
                articles_to_add.append(article)

        if articles_to_add:
            self.session.add_all(articles_to_add)
            self.session.commit()

    # --- CHỨC NĂNG CHO BẢNG TÓM TẮT (DIGESTS) ---
    # --- CHỨC NĂNG TÌM NỘI DUNG ĐỂ TÓM TẮT ---
    def get_articles_without_digest(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        articles = []
        seen_ids = set()
        
        digests = self.session.query(Digest).all()
        for d in digests:
            seen_ids.add(f"{d.article_type}:{d.article_id}")
        
        youtube_videos = self.session.query(YoutubeVideo).filter(
            YoutubeVideo.transcript.isnot(None),
            YoutubeVideo.transcript != "__UNAVAILABLE__"
        ).all()
        for video in youtube_videos:
            key = f"youtube:{video.video_id}"
            if key not in seen_ids:
                articles.append({
                    "type": "youtube",
                    "id": video.video_id,
                    "title": video.title,
                    "url": video.url,
                    "content": video.transcript or video.description or "",
                    "published_at": video.published_at
                })      
        if limit:
            articles = articles[:limit]
        
        return articles

    def get_videos_without_digest(self, limit: Optional[int] = 10) -> List[YoutubeVideo]:
        """
        Lấy các video YouTube chưa có trong bảng tóm tắt (digests).
        Sử dụng LEFT JOIN để tìm các video không có digest tương ứng.
        """
        # NOTE: This marker is also defined in services/process_youtube.py
        # It should ideally be moved to a central constants file.
        TRANSCRIPT_UNAVAILABLE_MARKER = "__UNAVAILABLE__"

        return (
            self.session.query(YoutubeVideo)
            .outerjoin(
                Digest,
                (Digest.article_id == YoutubeVideo.video_id)
                & (Digest.article_type == "youtube"),
            )
            .filter(Digest.id.is_(None))
            .filter(YoutubeVideo.transcript.isnot(None))
            .filter(YoutubeVideo.transcript != TRANSCRIPT_UNAVAILABLE_MARKER)
            .limit(limit)
            .all()
        )

    
    def create_digest(self, article_type: str, article_id: str, url: str, title: str, summary: str, published_at: Optional[datetime] = None) -> Optional[Digest]:
        digest_id = f"{article_type}:{article_id}"
        existing = self.session.query(Digest).filter_by(id=digest_id).first()
        if existing:
            return None
        
        if published_at:
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=timezone.utc)
            created_at = published_at
        else:
            created_at = datetime.now(timezone.utc)
        
        digest = Digest(
            id=digest_id,
            article_type=article_type,
            article_id=article_id,
            url=url,
            title=title,
            summary=summary,
            created_at=created_at
        )
        self.session.add(digest)
        self.session.commit()
        return digest
    
    def get_recent_digests(self, hours: int = 24) -> List[Dict[str, Any]]:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        digests = self.session.query(Digest).filter(
            Digest.created_at >= cutoff_time
        ).order_by(Digest.created_at.desc()).all()
        
        return [
            {
                "id": d.id,
                "article_type": d.article_type,
                "article_id": d.article_id,
                "url": d.url,
                "title": d.title,
                "summary": d.summary,
                "created_at": d.created_at
            }
            for d in digests
        ]

