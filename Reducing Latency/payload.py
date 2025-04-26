from cache import Cache
from api import fetch_data
from fastapi import FastAPI, HTTPException

app = FastAPI()
cache = Cache(max_size=100) 
@app.get("/data")
async def get_data(url: str, fields: str = None):
    data = await fetch_data(url, cache)
    if fields:
        return {field: data[field] for field in fields.split(",") if field in data}
    return data