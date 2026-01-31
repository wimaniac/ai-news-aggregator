# AI News Aggregator (AI Agent)

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)
![Gemini](https://img.shields.io/badge/AI-Google_Gemini-orange.svg)

## Giới thiệu (Introduction)

**AI News Aggregator** là một hệ thống tự động hóa (Automated Pipeline) giúp xây dựng thói quen cập nhật tin tức công nghệ hiệu quả. Thay vì phải tự truy cập hàng chục kênh YouTube hay blog mỗi ngày, hệ thống này sẽ thay bạn làm điều đó.

Dự án hoạt động như một "Trợ lý ảo" (Agent): tự động thu thập dữ liệu từ nhiều nguồn (YouTube RSS, Tech Blogs như OpenAI, Anthropic...), lưu trữ có cấu trúc, và sử dụng sức mạnh của **Google Gemini LLM** để tóm tắt nội dung cốt lõi, sau đó gửi báo cáo tổng hợp vào email cá nhân của bạn mỗi 24 giờ.

> **Nguồn cảm hứng & Học tập:**
> Dự án này được xây dựng dựa trên ý tưởng và hướng dẫn từ video [[Build a Complete End-to-End GenAI Project in 3 Hours](https://www.youtube.com/watch?v=E8zpgNPx8jE)] của kênh YouTube [Dave Ebbelaar].

---

## Tính năng chính (Key Features)

* **YouTube Intelligence:**
    * Tự động theo dõi các kênh YouTube qua RSS Feed (không cần API Key tốn kém).
    * Lọc video mới nhất trong 24h.
    * Trích xuất phụ đề (Transcript) video tự động để lấy nội dung chi tiết.
* **Blog Scraping:** Thu thập bài viết mới từ các trang blog công nghệ (OpenAI, Anthropic...).
* **AI Summarization:** Sử dụng **Google Gemini 1.5 Flash** để đọc hiểu và tóm tắt nội dung dài thành bản tin ngắn gọn, súc tích bằng tiếng Việt.
* **Structured Database:** Lưu trữ dữ liệu khoa học với **PostgreSQL** và quản lý schema bằng **SQLAlchemy**.
* **Automated Reporting:** Tự động gửi email tổng hợp (Daily Digest) vào mỗi sáng.
* **Dockerized:** Dễ dàng triển khai môi trường Database với Docker Compose.

---

##  Công nghệ sử dụng (Tech Stack)

* **Ngôn ngữ:** Python 3.12 (Quản lý package bằng `uv`).
* **Backend Logic:** Cấu trúc module trong thư mục `app/`.
* **Database:** PostgreSQL (chạy trên Docker), SQLAlchemy (ORM).
* **AI/LLM:** Google Generative AI (Gemini), LangChain (tùy chọn).
* **Data Collection:** `feedparser` (RSS), `youtube-transcript-api`, `beautifulsoup4`.
* **Infrastructure:** Docker, Docker Compose.

---

##  Cấu trúc dự án (Project Structure)
