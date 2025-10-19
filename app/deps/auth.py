"""
Dependências de autenticação para rotas protegidas.

- Define `oauth2_scheme` (Bearer) e `get_current_user_id` para extrair o `sub` do JWT.
- Alinhado com `app/core/security.py` (claim `sub` e algoritmo configurado lá).

Configuração:
- tokenUrl do OAuth2PasswordBearer: "/api/v1/auth/login".
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """Valida o token Bearer e retorna o identificador do usuário (`sub`)."""
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub:
            raise ValueError("Missing sub")
        return sub
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})
