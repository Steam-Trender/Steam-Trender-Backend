from fastapi import FastAPI

from app.routes import analysis, posts, status, summary, tags, years


def init_routes(app: FastAPI):
    app.include_router(status.router)
    app.include_router(years.router)
    app.include_router(analysis.router)
    app.include_router(posts.router)
    app.include_router(tags.router)
    app.include_router(summary.router)
