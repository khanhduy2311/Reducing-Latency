import aiohttp
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

async def fetch(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()  # Kiểm tra lỗi HTTP
            return await response.json()  # Trả về dữ liệu JSON
    except Exception as e:
        logger.error(f"Error fetching data from {url}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data")

async def fetch_data(url, cache):
    if url in cache:
        logger.info(f"Cache hit for {url}")
        return cache[url]
    
    async with aiohttp.ClientSession() as session:
        data = await fetch(session, url)
        cache[url] = data  # Lưu trữ phản hồi vào cache
        logger.info(f"Cache updated for {url}")
        return data