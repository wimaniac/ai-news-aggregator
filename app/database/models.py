from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

# Khởi tạo Base (Lớp cha cho mọi Model)
Base = declarative_base()

# --- 1. Bảng lưu Video YouTube ---
class YoutubeVideo(Base):
    __tablename__ = "youtube_videos"
    
    video_id = Column(String, primary_key=True) # ID video là duy nhất
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    channel_id = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=False)
    description = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True) 
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# --- 2. Bảng lưu Bài viết (Báo, Blog...) ---
class NewsArticle(Base):
    __tablename__ = "news_articles"
    # Với bài viết, URL thường là thứ duy nhất, nhưng ta nên dùng ID tự tăng (Integer) làm khóa chính cho chuẩn.
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    # unique=True đảm bảo không lưu trùng 1 bài báo 2 lần
    url = Column(String, nullable=False, unique=True) 
    source = Column(String, nullable=False) 
    published_at = Column(DateTime, nullable=False)
    content = Column(Text, nullable=True) 
    summary = Column(Text, nullable=True) 
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))