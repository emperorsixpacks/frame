"""GitHub App webhook receiver for Frame."""

from fastapi import FastAPI

from app.webhooks.routes import router

app = FastAPI(title="Frame", version="0.1.0")
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
