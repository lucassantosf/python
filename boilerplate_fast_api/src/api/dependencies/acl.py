from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from src.api.dependencies.auth import security
from src.infrastructure.security.jwt import JWTProvider
from src.core.auth.roles import get_role_permissions
from src.core.auth.permissions import Permission
from typing import List, Callable

def require_permissions(required_permissions: List[Permission]) -> Callable:
    def role_checker(auth: HTTPAuthorizationCredentials = Depends(security)):
        # Verifica se o token está na blacklist
        if JWTProvider.is_token_blacklisted(auth.credentials):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token revogado. Por favor, faça login novamente."
            )
            
        # Decodifica e pega os dados da seção (Payload JWT)
        payload = JWTProvider.decode_token(auth.credentials)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
            
        # O Cargo/Role deve ter sido inserido lá no Auth Service no momento do Login
        user_role = payload.get("role")
        if not user_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role/Cargo não encontrado neste Token")
            
        # Obter tudo o que esta Role pode fazer no domínio real
        allowed_permissions = get_role_permissions(user_role)
        
        # Validar as premissas
        for perm in required_permissions:
            if perm not in allowed_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail=f"Acesso Negado: Faltam privilégios para esta ação ({perm.value})"
                )
                
        # Se sobreviveu até aqui, retorna o payload completo caso precise na rota
        return payload
    return role_checker
