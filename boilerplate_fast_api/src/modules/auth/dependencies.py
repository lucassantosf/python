from fastapi import Depends
from sqlalchemy.orm import Session
from src.modules.auth.service import AuthService
from src.infrastructure.repositories.user_sqlalchemy import UserSQLAlchemyRepository
from src.infrastructure.database.session import get_db

def get_user_repository(db: Session = Depends(get_db)):
    # Returns the SQLAlchemy implementation, injecting the current DB Session
    return UserSQLAlchemyRepository(db)

def get_auth_service(repo = Depends(get_user_repository)) -> AuthService:
    return AuthService(repo)
