from fastapi import APIRouter, Depends, HTTPException, status
from src.modules.users.schemas import UserResponse
from src.modules.users.service import UserService
from src.modules.users.dependencies import get_user_service
from src.api.dependencies.auth import get_current_user_id
from src.api.dependencies.acl import require_permissions
from src.core.auth.permissions import Permission
from src.core.domain.exceptions import NotFoundException

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):
    try:
        # Convert user_id back to int if your DB ID is int
        user = user_service.get_by_id(int(current_user_id))
        return user
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )

@router.get("/admin-only")
def test_admin_route(
    payload: dict = Depends(require_permissions([Permission.WRITE_USERS]))
):
    """
    Rota de teste para validar o ACL.
    Somente usuários com a permissão WRITE_USERS (normalmente o ADMIN) conseguem ver.
    """
    return {
        "message": "Acesso concedido!",
        "admin_data": "Este é um dado sensível que apenas administradores veem.",
        "user_role": payload.get("role")
    }

