import os
import json
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()

class DigestOutput(BaseModel):
    title: str
    summary: str

# --- CẬP NHẬT PROMPT TIẾNG VIỆT TẠI ĐÂY ---
PROMPT = """Bạn là một chuyên gia phân tích tin tức AI, chuyên tóm tắt các bài báo kỹ thuật, nghiên cứu và video về trí tuệ nhân tạo.

Nhiệm vụ của bạn là tạo ra các bản tóm tắt súc tích, giàu thông tin giúp người đọc nắm bắt nhanh các điểm chính và tầm quan trọng của nội dung.

Hướng dẫn bắt buộc:
1. Ngôn ngữ: TOÀN BỘ kết quả trả về phải là Tiếng Việt.
2. Tiêu đề: Hấp dẫn, ngắn gọn (10-20 từ), tóm tắt được cốt lõi nội dung.
3. Tóm tắt: Viết 2-3 câu làm nổi bật các ý chính, kết quả đạt được hoặc tác động của tin tức đó.
4. Phong cách: Khách quan, chuyên nghiệp, dễ hiểu nhưng vẫn đảm bảo tính chính xác về kỹ thuật.
5. Định dạng: Trả về kết quả dưới dạng JSON object với đúng 2 key là "title" và "summary".
"""

class DigestAgent:
    def __init__(self):
        # 1. Cấu hình API Key (Bắt buộc cho thư viện cũ)
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=PROMPT)

    def generate_digest(
        self, title: str, content: str, article_type: str
    ) -> Optional[DigestOutput]:
        try:
            # Nhắc lại yêu cầu tiếng Việt trong user prompt để chắc chắn
            user_prompt = (
                f"Hãy tóm tắt nội dung sau bằng Tiếng Việt.\n"
                f"Loại bài: {article_type}\n"
                f"Tiêu đề gốc: {title}\n"
                f"Nội dung: {content[:8000]}"
            )
            
            # 3. Gọi hàm generate
            response = self.model.generate_content(
                user_prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            if response.text:
                response_data = json.loads(response.text)
                return DigestOutput(**response_data)
            return None
            
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Lỗi khi đọc JSON từ AI: {e}")
            return None
        except Exception as e:
            print(f"Lỗi hệ thống: {e}")
            return