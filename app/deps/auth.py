"""
Dependências de autenticação para rotas protegidas.

- Usa HTTP Bearer (somente token) e `get_current_user_id` para extrair o `sub` do JWT.
- Alinhado com `app/core/security.py` (claim `sub` e algoritmo configurado lá).
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from app.core.security import decode_token

bearer_scheme = HTTPBearer(scheme_name="Token JWT")


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    """Valida o token Bearer (HTTP) e retorna o identificador do usuário (`sub`)."""
    try:
        token = credentials.credentials
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub:
            raise ValueError("Missing sub")
        return sub
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})
