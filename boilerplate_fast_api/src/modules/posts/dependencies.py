from fastapi import Depends
from sqlalchemy.orm import Session
from src.modules.posts.service import PostService
from src.infrastructure.repositories.post_sqlalchemy import PostSQLAlchemyRepository
from src.infrastructure.database.session import get_db


def get_post_repository(db: Session = Depends(get_db)):
    # Returns the SQLAlchemy implementation, injecting the current DB Session
    return PostSQLAlchemyRepository(db)


def get_post_service(repo=Depends(get_post_repository)) -> PostService:
    return PostService(repo)
