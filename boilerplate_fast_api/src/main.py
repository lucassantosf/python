from fastapi import FastAPI
from src.api.routes.health import router as hello_router
from src.api.routes.auth import router as auth_router
from src.api.routes.users import router as users_router

from src.settings import settings

def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)

    app.include_router(
        hello_router,
        prefix="/api/v1",
        tags=["health"]
    )

    app.include_router(
        auth_router,
        prefix="/api/v1"
    )

    app.include_router(
        users_router,
        prefix="/api/v1"
    )

    return app


app = create_app()