from src.modules.users.repository import UserRepository
from src.infrastructure.security.jwt import JWTProvider
from src.infrastructure.security.password import PasswordHasher
from src.core.domain.exceptions import UnauthorizedException

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email)
        
        # Note: user.password_hash assumes a certain structure in your domain model
        if not user or not PasswordHasher.verify(password, user.password_hash):
            raise UnauthorizedException("Credenciais inválidas")
        
        token = JWTProvider.create_access_token({
            "sub": str(user.id),
            "role": user.role
        })
        return {
            "access_token": token,
            "token_type": "bearer"
        }

    def logout(self, token: str) -> None:
        JWTProvider.blacklist_token(token)

