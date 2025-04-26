from pydantic import BaseModel, Field
from typing import Any, Optional

class QuestionRequest(BaseModel):
    question: str = Field(..., description="Câu hỏi của người dùng")
    # Có thể thêm các tham số khác nếu cần truyền đến API gốc
    # ví dụ: user_id: Optional[str] = None

class AnswerResponse(BaseModel):
    question: str
    answer: Any # Kiểu dữ liệu của câu trả lời có thể đa dạng
    source: str = Field(description="Nguồn của câu trả lời ('cache' hoặc 'api')")
    latency_ms: float = Field(description="Độ trễ xử lý yêu cầu (milliseconds)")
    api_latency_ms: Optional[float] = Field(None, description="Độ trễ của riêng API gốc (milliseconds), nếu gọi API")

class HealthCheckResponse(BaseModel):
    status: str = "OK"

class CacheStatsResponse(BaseModel):
    hits: int
    misses: int
    current_size: int
    max_size: int
    ttl_seconds: int