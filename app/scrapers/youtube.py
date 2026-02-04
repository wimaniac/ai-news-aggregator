from datetime import datetime, timedelta, timezone
from typing import Optional, List
import os
import feedparser
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.proxies import WebshareProxyConfig

class Transcript(BaseModel):
    text: str

class ChannelVideo(BaseModel):
    title: str
    url: str
    video_id: str
    published_at: datetime
    description: str
    transcript: Optional[str] = None
    
class YoutubeScraper:
    def __init__(self):
        proxy_config = None
        proxy_usename = os.getenv('PROXY_USERNAME')
        proxy_password = os.getenv('PROXY_PASSWORD')

        if proxy_usename and proxy_password:
            proxy_config = WebshareProxyConfig(
                proxy_username=proxy_usename,
                proxy_password=proxy_password
            )
        
        self.transcript_api = YouTubeTranscriptApi(proxy_config=proxy_config)
        
    def _get_rss_url(self, chanel_id: str) -> str:
        return f"https://www.youtube.com/feeds/videos.xml?channel_id={chanel_id}"
    
    def _extract_video_id(self, video_url: str) -> str:
        if "https://www.youtube.com/watch?v=" in video_url:
            return video_url.split("v=")[1].split("?")[0]
        if "https://www.youtube.com/shorts/" in video_url:
            return video_url.split("shorts/")[1].split("?")[0]
        if "youtu.be/" in video_url:
            return video_url.split("youtu.be/")[1].split("?")[0]
        return video_url
    
    def get_transcript(self, video_id: str) -> Optional[Transcript]:
        try: 
            transcript = self.transcript_api.fetch(video_id, languages=['vi', 'en'])
            text = " ".join([snippet.text for snippet in transcript.snippets])
            return Transcript(text=text)
        except (TranscriptsDisabled, NoTranscriptFound):
            print(f"Video {video_id}: Không có phụ đề.")
            return None
        except Exception as e:
            print(f"Lỗi không xác định khi lấy transcript {video_id}: {str(e)}")
            return None
        
    def get_latest_videos(self, channel_id: str, hours: int = 24) -> List[ChannelVideo]:
        # 1. Lấy dữ liệu từ RSS
        feed = feedparser.parse(self._get_rss_url(channel_id))
        if not feed.entries:
            return []
        
        # 2. Thiết lập mốc thời gian chặn
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        videos = []

        # 3. Duyệt và lọc
        for entry in feed.entries:
            if "/shorts" in entry.link:
                continue
            
            # Chuyển đổi thời gian từ RSS sang datetime object
            published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            
            if published_time >= cutoff_time:
                # Trích xuất video_id bằng hàm đã viết trước đó
                v_id = self._extract_video_id(entry.link)
                
                videos.append(ChannelVideo(
                    title=entry.title,           
                    url=entry.link,               
                    video_id=v_id,               
                    published_at=published_time,
                    description=entry.get("summary", "")
                ))

        return videos
    
    def scrape_channel(self, channel_id: str, hours: int = 24) -> list[ChannelVideo]:
        videos = self.get_latest_videos(channel_id, hours)
        res = []
        for video in videos:
            transcript = self.get_transcript(video.video_id)
            res.append(video.model_copy(update={"transcript": transcript.text if transcript else None}))
            
        return res
    
if __name__ == "__main__":
    scraper = YoutubeScraper()
    videos = scraper.get_latest_videos(channel_id="UConnM5zwOP9vG_LPTYbRsAg", hours=24)
    transcript = scraper.get_transcript(video_id="Z7duGGiqQp0")
