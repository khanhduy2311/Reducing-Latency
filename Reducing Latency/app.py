from fastapi import FastAPI, HTTPException
from api import fetch_data
from cache import Cache
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
cache = Cache(max_size=100)  # Kích thước tối đa của cache

@app.get("/data")
async def get_data(url: str): # Thay url của API tại đây
    if not url:
        logger.error("URL is required")
        raise HTTPException(status_code=400, detail="URL is required")
    
    logger.info(f"Fetching data from {url}")
    data = await fetch_data(url, cache)
    return data

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)