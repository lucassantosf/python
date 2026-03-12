from sqlalchemy.orm import Session
from src.modules.users.repository import UserRepository
from src.modules.users.domain import User
from src.infrastructure.database.models.user_model import UserModel

class UserSQLAlchemyRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> User | None:
        user_model = self.session.query(UserModel).filter(UserModel.email == email).first()
        if user_model:
            return User(
                id=user_model.id, 
                email=user_model.email, 
                password_hash=user_model.password_hash,
                role=user_model.role
            )
        return None

    def get_by_id(self, user_id: int) -> User | None:
        user_model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        if user_model:
            return User(
                id=user_model.id, 
                email=user_model.email, 
                password_hash=user_model.password_hash,
                role=user_model.role
            )
        return None
