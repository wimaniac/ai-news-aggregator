import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import feedparser

class Article(BaseModel):
    title: str
    url: str
    published_at: datetime
    content: str
    source: str

class WebScraper:
    def __init__(self):
        # Giả lập trình duyệt thật để không bị chặn (Anti-bot)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _get_article_content(self, url: str) -> str:
        """
        Hàm này truy cập vào link bài viết và bóc tách nội dung chính.
        Lưu ý: Mỗi báo có cấu trúc HTML khác nhau (tên class khác nhau).
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return ""

            soup = BeautifulSoup(response.text, 'html.parser')
        
            content_div = soup.find('div', class_='noi-dung') 
            
            if not content_div:
                # Fallback: Thử tìm thẻ p (paragraph) nếu không tìm thấy div chính
                paragraphs = soup.find_all('p')
            else:
                paragraphs = content_div.find_all('p')

            # 2. Gom tất cả các đoạn văn lại
            full_text = " ".join([p.get_text().strip() for p in paragraphs])
            return full_text

        except Exception as e:
            print(f"Lỗi khi cào nội dung {url}: {e}")
            return ""

    def scrape_rss_feed(self, rss_url: str, hours: int = 24) -> list[Article]:
        try:
            # Use requests with headers to avoid anti-bot blocking (403 Forbidden)
            response = requests.get(rss_url, headers=self.headers, timeout=10)
            feed = feedparser.parse(response.content)
        except Exception as e:
            print(f"Lỗi khi tải RSS: {e}")
            return []

        articles = []
        
        print(f"Tìm thấy {len(feed.entries)} bài viết từ RSS.")

        # Thiết lập mốc thời gian chặn
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        for entry in feed.entries: 
            print(f"Đang xử lý: {entry.title}")

            published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            if published_time >= cutoff_time:
                full_content = self._get_article_content(entry.link)
                
                if full_content:
                    articles.append(Article(
                        title=entry.title,
                        url=entry.link,
                        published_at=published_time,
                        content=full_content,
                        source="Báo Công An"
                    ))
        
        return articles

# --- CHẠY THỬ ---
if __name__ == "__main__":
    scraper = WebScraper()
    rss_url = "https://congan.com.vn/rss/vu-an" 
    
    data = scraper.scrape_rss_feed(rss_url, hours=24)
    
    for article in data:
        print("-" * 50)
        print(f"Tiêu đề: {article.title}")
        print(f"Nội dung (500 ký tự đầu): {article.content[:500]}...")