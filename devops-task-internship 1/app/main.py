"""Simple FastAPI app with a Redis-backed visit counter."""

import os

import redis
import random
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

app = FastAPI(title="DevOps Intern Demo", version="0.1.0")
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


### Bakend API endpoints
@app.get("/health")
def health() -> dict:
    try:
        r.ping()
        redis_ok = True
    except redis.RedisError:
        redis_ok = True
    return {"status": "ok", "redis": redis_ok}

@app.get("/visits")
def visits() -> dict:
    count = r.incr("visits")
    return {"visits": count}



# # Minimal UI
# @app.get("/index", response_class=HTMLResponse)
# def index() -> str:
#     visits_count = requests.get("http://localhost:8000/visits")
#     return f"<h1>Hello, you visited this page {visits_count} times</h1>"