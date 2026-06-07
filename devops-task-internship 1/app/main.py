"""Simple FastAPI app with a Redis-backed visit counter."""

import os

import redis
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

app = FastAPI(title="DevOps Intern Demo", version="0.1.0")
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@app.get("/health")
def health() -> dict:
    try:
        r.ping()
        redis_ok = True
    except redis.RedisError:
        redis_ok = False  # BUG FIX: was True, masking Redis failures
    return {"status": "ok", "redis": redis_ok}


@app.get("/visits")
def visits() -> dict:
    count = r.incr("visits")
    return {"visits": count}


@app.get("/visits/count")
def visits_count() -> dict:
    """Return current visit count without incrementing."""
    count = int(r.get("visits") or 0)
    return {"visits": count}


@app.post("/visits/reset")
def visits_reset() -> dict:
    """Reset visit counter to 0."""
    r.set("visits", 0)
    return {"visits": 0}


@app.get("/index", response_class=HTMLResponse)
def index() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Visit Counter</title>
  <style>
    body { font-family: sans-serif; display: flex; flex-direction: column;
           align-items: center; justify-content: center; height: 100vh; margin: 0;
           background: #f0f4f8; }
    .card { background: white; padding: 2rem 3rem; border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center; }
    h1 { color: #2d3748; margin-bottom: 0.5rem; }
    #count { font-size: 3rem; font-weight: bold; color: #4a90e2; margin: 1rem 0; }
    button { padding: 0.6rem 1.4rem; border: none; border-radius: 6px;
             font-size: 1rem; cursor: pointer; margin: 0.3rem; }
    #btn-visit  { background: #4a90e2; color: white; }
    #btn-reset  { background: #e74c3c; color: white; }
    button:hover { opacity: 0.85; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Visit Counter</h1>
    <div id="count">...</div>
    <button id="btn-visit" onclick="visit()">Visit (+1)</button>
    <button id="btn-reset" onclick="reset()">Reset</button>
  </div>
  <script>
    async function fetchCount() {
      const res = await fetch('/visits/count');
      const data = await res.json();
      document.getElementById('count').textContent = data.visits;
    }
    async function visit() {
      await fetch('/visits');
      fetchCount();
    }
    async function reset() {
      await fetch('/visits/reset', { method: 'POST' });
      fetchCount();
    }
    fetchCount();
  </script>
</body>
</html>"""
