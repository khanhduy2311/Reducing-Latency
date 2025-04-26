import time
import logging
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware # Thêm nếu cần gọi từ frontend khác domain
from contextlib import asynccontextmanager

from . import cache, models, api_client
from .config import get_settings, Settings

# Cấu hình logging cơ bản
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sử dụng lifespan để quản lý việc khởi tạo/đóng tài nguyên (như HTTP client)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code chạy khi khởi động ứng dụng
    logger.info("Starting API Latency Reducer...")
    # Có thể khởi tạo các kết nối khác ở đây nếu cần
    yield
    # Code chạy khi tắt ứng dụng
    logger.info("Shutting down API Latency Reducer...")
    await api_client.close_api_client()
    logger.info("Resources closed.")

app = FastAPI(
    title="API Latency Reducer",
    description="Proxy service to reduce latency for a target QA API using caching and async requests.",
    version="1.0.0",
    lifespan=lifespan
)

# Cấu hình CORS (nếu cần)
# origins = [
#     "http://localhost:3000", # Địa chỉ frontend của bạn
#     "https://your-frontend.com",
# ]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware để đo tổng thời gian xử lý của mỗi request."""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    logger.info(f"Request {request.method} {request.url.path} completed in {process_time:.2f} ms, Status: {response.status_code}")
    return response

@app.get("/health", response_model=models.HealthCheckResponse, tags=["Management"])
async def health_check():
    """Kiểm tra trạng thái hoạt động của service."""
    # Có thể thêm kiểm tra kết nối đến API gốc ở đây nếu muốn
    return models.HealthCheckResponse(status="OK")

@app.get("/cache/stats", response_model=models.CacheStatsResponse, tags=["Management"])
async def get_cache_statistics(settings: Settings = Depends(get_settings)):
    """Lấy thông tin thống kê về cache."""
    stats = cache.get_cache_stats()
    stats["max_size"] = settings.CACHE_MAX_SIZE # Lấy từ config động
    stats["ttl_seconds"] = settings.CACHE_TTL_SECONDS
    return models.CacheStatsResponse(**stats)

@app.post("/cache/clear", status_code=status.HTTP_204_NO_CONTENT, tags=["Management"])
async def clear_all_cache():
    """Xóa toàn bộ nội dung cache."""
    cache.clear_cache()
    return None # Trả về 204 No Content

@app.post("/ask", response_model=models.AnswerResponse, tags=["QA"])
async def ask_question(
    request_data: models.QuestionRequest,
    settings: Settings = Depends(get_settings) # Inject settings
):
    """
    Endpoint chính để người dùng gửi câu hỏi.
    Hệ thống sẽ kiểm tra cache trước, nếu không có sẽ gọi API gốc.
    """
    start_time = time.perf_counter()
    question = request_data.question.strip() # Chuẩn hóa câu hỏi

    if not question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question cannot be empty.")

    # Tạo cache key duy nhất (bao gồm cả URL API gốc để tránh xung đột nếu proxy cho nhiều API)
    # Có thể cải thiện bằng cách chuẩn hóa text kỹ hơn (lowercase, remove punctuation)
    cache_key = f"{settings.TARGET_API_URL}:{question.lower()}"
    logger.info(f"Processing question: '{question}'")

    # 1. Kiểm tra Cache
    cached_answer = cache.get_from_cache(cache_key)
    if cached_answer is not None:
        total_latency_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"Cache hit for question: '{question}'. Returning cached response.")
        return models.AnswerResponse(
            question=question,
            answer=cached_answer,
            source="cache",
            latency_ms=total_latency_ms
        )

    # 2. Nếu Cache Miss, gọi API gốc
    logger.info(f"Cache miss for question: '{question}'. Calling target API...")
    answer, api_latency_ms, error_message = await api_client.call_target_api(question)

    if error_message is not None:
        # Xử lý các loại lỗi cụ thể từ API client
        if "timed out" in error_message.lower():
             raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=error_message)
        elif "error connecting" in error_message.lower() or "Target API returned error" in error_message.lower():
             raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=error_message)
        elif "Invalid response format" in error_message or "Answer key" in error_message:
             raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=error_message) # Lỗi từ phía API gốc
        else:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message) # Lỗi không xác định

    # 3. Lưu kết quả vào Cache (nếu thành công)
    if answer is not None:
        cache.set_in_cache(cache_key, answer)

    total_latency_ms = (time.perf_counter() - start_time) * 1000
    logger.info(f"Successfully processed question: '{question}' via API.")

    return models.AnswerResponse(
        question=question,
        answer=answer,
        source="api",
        latency_ms=total_latency_ms,
        api_latency_ms=api_latency_ms
    )

# Có thể thêm các endpoint khác nếu cần, ví dụ:
# - Endpoint để cập nhật cấu hình TARGET_API_URL động
# - Endpoint để quản lý người dùng/API keys cho proxy này (nếu cần bảo mật)

if __name__ == "__main__":
    # Chạy ứng dụng bằng uvicorn khi chạy file trực tiếp (chủ yếu để debug)
    # Nên chạy bằng lệnh `uvicorn app.main:app --reload` trong terminal
    import uvicorn
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)