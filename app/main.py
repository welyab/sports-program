from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

app.include_router(health_router)


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}
