from fastapi import FastAPI

from src.api.routes.health import router as hello_router
from src.settings import settings

def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)

    app.include_router(
        hello_router,
        prefix="/api/v1",
        tags=["health"]
    )

    return app

app = create_app()