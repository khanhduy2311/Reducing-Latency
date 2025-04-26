import httpx
import logging
import time
from typing import Any, Tuple, Optional
from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Tạo một HTTP client bất đồng bộ dùng chung để tận dụng connection pooling
# Nên đặt timeout mặc định ở client, nhưng cũng có thể ghi đè ở từng request
async_client = httpx.AsyncClient(timeout=settings.API_TIMEOUT_SECONDS)

async def call_target_api(question: str) -> Tuple[Optional[Any], Optional[float], Optional[str]]:
    """
    Gọi đến API QA gốc một cách bất đồng bộ.

    Args:
        question: Câu hỏi của người dùng.

    Returns:
        Tuple: (answer, api_latency_ms, error_message)
        - answer: Câu trả lời từ API gốc (hoặc None nếu lỗi).
        - api_latency_ms: Thời gian phản hồi của API gốc (hoặc None nếu lỗi).
        - error_message: Thông báo lỗi (hoặc None nếu thành công).
    """
    start_time = time.perf_counter()
    url = settings.TARGET_API_URL
    method = settings.TARGET_API_METHOD.upper()
    headers = settings.TARGET_API_HEADERS
    params = settings.TARGET_API_QUERY_PARAMS
    payload = {settings.TARGET_API_QUESTION_KEY: question}

    try:
        logger.info(f"Calling target API: {method} {url}")
        logger.debug(f"Payload/Params: {payload if method == 'POST' else params}")

        response = None
        if method == "POST":
            response = await async_client.post(url, json=payload, headers=headers, params=params)
        elif method == "GET":
            # Nếu GET, thường câu hỏi nằm trong query params
            get_params = params.copy()
            get_params[settings.TARGET_API_QUESTION_KEY] = question
            response = await async_client.get(url, params=get_params, headers=headers)
        else:
            # Hỗ trợ các method khác nếu cần (PUT, DELETE, etc.)
             return None, None, f"Unsupported HTTP method: {method}"

        # Kiểm tra lỗi HTTP (4xx, 5xx)
        response.raise_for_status()

        api_latency_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"Target API responded in {api_latency_ms:.2f} ms")

        # Trích xuất câu trả lời dựa trên cấu hình
        response_data = response.json()
        answer = response_data
        # Hỗ trợ truy cập key lồng nhau (ví dụ: "result.answer")
        keys = settings.TARGET_API_ANSWER_KEY.split('.')
        for key in keys:
            if isinstance(answer, dict) and key in answer:
                answer = answer[key]
            else:
                logger.error(f"Answer key '{settings.TARGET_API_ANSWER_KEY}' not found in API response: {response_data}")
                return None, api_latency_ms, f"Answer key '{settings.TARGET_API_ANSWER_KEY}' not found in response"

        return answer, api_latency_ms, None

    except httpx.TimeoutException:
        api_latency_ms = (time.perf_counter() - start_time) * 1000
        logger.warning(f"Target API timed out after {api_latency_ms:.2f} ms. URL: {url}")
        return None, api_latency_ms, "Target API request timed out"
    except httpx.RequestError as e:
        api_latency_ms = (time.perf_counter() - start_time) * 1000
        logger.error(f"Request error calling target API: {e}. URL: {url}")
        return None, api_latency_ms, f"Error connecting to target API: {e}"
    except httpx.HTTPStatusError as e:
        api_latency_ms = (time.perf_counter() - start_time) * 1000
        logger.error(f"HTTP error from target API: {e.response.status_code} - {e.response.text}. URL: {url}")
        return None, api_latency_ms, f"Target API returned error: {e.response.status_code}"
    except (KeyError, TypeError, ValueError) as e: # Lỗi parsing JSON hoặc key không tồn tại
         api_latency_ms = (time.perf_counter() - start_time) * 1000
         logger.error(f"Error processing target API response: {e}. Response: {response.text if response else 'No Response'}")
         return None, api_latency_ms, f"Invalid response format from target API: {e}"
    except Exception as e:
        api_latency_ms = (time.perf_counter() - start_time) * 1000
        logger.error(f"An unexpected error occurred: {e}")
        return None, api_latency_ms, f"An unexpected error occurred: {e}"

# Đảm bảo client được đóng khi ứng dụng tắt (quan trọng với asyncio)
async def close_api_client():
    await async_client.aclose()