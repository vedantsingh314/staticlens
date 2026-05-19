from fastapi import FastAPI
from engine.analyzer import analyze_github_repo
from api.routes.analyze import router as analyze_router
from api.routes.health import router as health_router

app = FastAPI()

app.include_router(analyze_router)
app.include_router(health_router)