from fastapi import Depends
from src.modules.users.service import UserService
from src.infrastructure.repositories.user_sqlalchemy import UserSQLAlchemyRepository
from src.infrastructure.database.session import get_db
from sqlalchemy.orm import Session

def get_user_repository(db: Session = Depends(get_db)):
    # Returns the SQLAlchemy implementation, injecting the current DB Session
    return UserSQLAlchemyRepository(db)

def get_user_service(repo = Depends(get_user_repository)) -> UserService:
    return UserService(repo)
