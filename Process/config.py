import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from functools import lru_cache

# Load biến môi trường từ file .env (nếu có)
load_dotenv()

class Settings(BaseSettings):
    # URL của API QA gốc mà bạn muốn tăng tốc
    # Có thể đặt trong file .env hoặc biến môi trường hệ thống
    # Ví dụ: TARGET_API_URL=http://your-original-qa-api.com/ask
    TARGET_API_URL: str = "http://localhost:8080/ask" # URL ví dụ, thay bằng API team

    # Cấu hình Cache
    CACHE_MAX_SIZE: int = 1024  # Số lượng item tối đa trong cache
    CACHE_TTL_SECONDS: int = 300 # Thời gian sống của cache item (vd: 5p) trong cuộc thi là 30p maybe

    # Cấu hình Timeout cho request đến API gốc
    API_TIMEOUT_SECONDS: float = 5.0 # Thời gian chờ tối đa 

    # Cấu hình cách gọi API gốc (linh hoạt)
    # Phương thức HTTP (GET, POST, etc.)
    TARGET_API_METHOD: str = "POST"
    # Key trong JSON payload gửi đi chứa câu hỏi
    TARGET_API_QUESTION_KEY: str = "query"
    # Key trong JSON response trả về chứa câu trả lời
    TARGET_API_ANSWER_KEY: str = "answer"
    # Headers tùy chỉnh (nếu API gốc yêu cầu, ví dụ: API Key)
    # Định dạng: {"Header-Name": "Header-Value"}
    TARGET_API_HEADERS: dict = {"Content-Type": "application/json"}
    # Các tham số query string (nếu dùng GET)
    TARGET_API_QUERY_PARAMS: dict = {}

    # Cấu hình server (cho uvicorn)
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000 # Port của local

    class Config:
        # Cho phép đọc từ file .env
        env_file = '.env'
        env_file_encoding = 'utf-8'
        # Bỏ qua phân biệt chữ hoa/thường cho biến môi trường
        case_sensitive = False

# Sử dụng lru_cache để đảm bảo Settings chỉ được tạo 1 lần (singleton)
@lru_cache()
def get_settings() -> Settings:
    return Settings()

# --- Ví dụ file .env ---
# TARGET_API_URL=https://your-real-api.com/v1/query
# CACHE_TTL_SECONDS=600
# API_TIMEOUT_SECONDS=15
# TARGET_API_METHOD=POST
# TARGET_API_QUESTION_KEY=questionText
# TARGET_API_ANSWER_KEY=result.answer
# TARGET_API_HEADERS={"Authorization": "Bearer YOUR_API_KEY", "X-Custom-Header": "Value"}
