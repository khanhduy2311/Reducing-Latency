# API Latency Reducer Project

Proxy service được xây dựng bằng FastAPI để giảm độ trễ cho một API QA (Question-Answering) mục tiêu thông qua caching và xử lý bất đồng bộ.

## Tính năng

-   **Proxy API:** Chuyển tiếp yêu cầu đến API gốc.
-   **Caching:** Lưu trữ kết quả câu trả lời với TTL (Time-To-Live) để tăng tốc các câu hỏi lặp lại.
-   **Asynchronous Requests:** Sử dụng `httpx` và `asyncio` để gọi API gốc không chặn luồng xử lý chính.
-   **Timeout Management:** Giới hạn thời gian chờ phản hồi từ API gốc.
-   **Connection Pooling:** Tự động tái sử dụng kết nối HTTP.
-   **Configurable:** Dễ dàng cấu hình URL API gốc, TTL cache, timeout, và chi tiết cách gọi API qua biến môi trường hoặc file `.env`.
-   **Basic Metrics:** Theo dõi cache hit/miss.
-   **Health Check:** Endpoint `/health` để kiểm tra trạng thái service.
-   **Cache Management:** Endpoint `/cache/stats` để xem thông tin cache và `/cache/clear` để xóa cache.

## Cài đặt

1.  **Clone repository:**
    ```bash
    git clone <your-repo-url>
    cd api-latency-reducer
    ```

2.  **Tạo và kích hoạt môi trường ảo (khuyến nghị):**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Cài đặt các thư viện cần thiết:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Cấu hình:**
    *   Tạo file `.env` trong thư mục gốc (`api-latency-reducer/`) và định nghĩa các biến môi trường cần thiết. Xem ví dụ trong `app/config.py`.
    *   **Quan trọng nhất:** Đặt `TARGET_API_URL` thành URL của API QA gốc mà bạn muốn tăng tốc.
    *   Tùy chỉnh các biến khác như `CACHE_TTL_SECONDS`, `API_TIMEOUT_SECONDS`, `TARGET_API_METHOD`, `TARGET_API_QUESTION_KEY`, `TARGET_API_ANSWER_KEY`, `TARGET_API_HEADERS` cho phù hợp với API gốc của bạn.

    **Ví dụ file `.env`:**
    ```dotenv
    TARGET_API_URL=http://your-original-qa-api.com/ask
    CACHE_TTL_SECONDS=600 # 10 phút
    API_TIMEOUT_SECONDS=15
    TARGET_API_METHOD=POST
    TARGET_API_QUESTION_KEY=query
    TARGET_API_ANSWER_KEY=answer
    # TARGET_API_HEADERS={"Authorization": "Bearer YOUR_SECRET_TOKEN"} # Bỏ comment và thêm header nếu cần
    ```

## Chạy ứng dụng

Sử dụng `uvicorn` để chạy server ASGI:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload