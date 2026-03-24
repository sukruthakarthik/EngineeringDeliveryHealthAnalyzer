import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.issues import router as issues_router
from routes.health import router as health_router
from routes.bottlenecks import router as bottlenecks_router
from routes.workload import router as workload_router
from routes.jira import router as jira_router

app = FastAPI(title="Engineering Delivery Health Analyzer", version="1.0.0")

# CORS origins from environment variable (comma-separated)
cors_origins_env = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://localhost:5175"
)
cors_origins = [origin.strip() for origin in cors_origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(issues_router)
app.include_router(health_router)
app.include_router(bottlenecks_router)
app.include_router(workload_router)
app.include_router(jira_router)


@app.get("/")
def root() -> dict:
    return {"message": "Engineering Delivery Health Analyzer API"}
