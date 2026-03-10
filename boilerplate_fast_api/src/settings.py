class Settings:
    PROJECT_NAME: str = "FastAPI Boilerplate"
    SECRET_KEY: str = "your-super-secret-key-change-it-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///./app.db"

settings = Settings()