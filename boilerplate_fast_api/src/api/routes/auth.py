from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from src.modules.auth.schemas import LoginRequest, TokenResponse
from src.modules.auth.service import AuthService
from src.modules.auth.dependencies import get_auth_service
from src.core.domain.exceptions import UnauthorizedException
from src.api.dependencies.auth import security

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, service: AuthService = Depends(get_auth_service)):
    try:
        return service.authenticate(data.email, data.password)
    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    auth: HTTPAuthorizationCredentials = Depends(security),
    service: AuthService = Depends(get_auth_service)
):
    """
    Invalida o token JWT atual em memória no servidor.
    Se a API falhar ou reiniciar, o token voltará a valer se ainda não tiver expirado em tempo.
    """
    service.logout(auth.credentials)
    return

