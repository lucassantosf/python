from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.infrastructure.security.jwt import JWTProvider

security = HTTPBearer()

def get_current_user_id(auth: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    FastAPI dependency to protect routes.
    It decodes the JWT and returns the user identifier (sub).
    """
    if JWTProvider.is_token_blacklisted(auth.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revogado. Por favor, faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = JWTProvider.decode_token(auth.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não contém identificação do usuário",
        )
        
    return user_id
