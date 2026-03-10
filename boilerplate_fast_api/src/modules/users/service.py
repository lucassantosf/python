from src.modules.users.repository import UserRepository
from src.core.domain.exceptions import NotFoundException

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_by_id(self, user_id: int):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("Usuário não encontrado")
        return user
