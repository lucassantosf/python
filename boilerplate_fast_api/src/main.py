from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.routes.health import router as hello_router
from src.api.routes.auth import router as auth_router
from src.api.routes.users import router as users_router
from src.api.routes.posts import router as posts_router

from src.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)

    # ---------------------------------------------------------------------------
    # Global validation error handler
    # Transforms Pydantic's verbose default format into a clean, consistent shape:
    # {
    #   "errors": [
    #     { "field": "title", "message": "This field is required." }
    #   ]
    # }
    # ---------------------------------------------------------------------------
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            # `loc` is a tuple like ("body", "title") — we grab the last meaningful part
            field = ".".join(str(part) for part in error["loc"] if part != "body")
            raw_msg: str = error["msg"]

            # Map Pydantic's internal messages to friendlier descriptions
            message_map = {
                "Field required": "This field is required.",
                "field required": "This field is required.",
            }
            message = message_map.get(raw_msg, raw_msg.capitalize() + ".")

            errors.append({"field": field or "request", "message": message})

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"errors": errors},
        )

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

    app.include_router(
        posts_router,
        prefix="/api/v1"
    )

    return app


app = create_app()