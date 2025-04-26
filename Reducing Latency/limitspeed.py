from fastapi.middleware.cors import CORSMiddleware
from cache import Cache
from api import fetch_data
from fastapi import FastAPI, HTTPException

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)