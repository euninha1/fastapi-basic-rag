"""
Rotas de autenticação: login (OAuth2 password) e logout.

- Usa `verify_password` e `create_access_token` de `app/core/security`.
- Retorna `Token` (access_token + token_type) conforme `app/schemas/auth`.

Variáveis de ambiente (indiretas): definidas em app/core/security (SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth import Token
from app.core.security import create_access_token, verify_password
from app.db.mongo import get_db

router = APIRouter(tags=["auth"])

@router.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    """Autentica via email/senha e retorna JWT Bearer em `access_token`."""
    # Busca o usuário por email
    user = await db["users"].find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(subject=str(user["_id"]))
    return {"access_token": token, "token_type": "bearer"}

@router.post("/auth/logout")
async def logout():
    """Logout stateless: cliente deve descartar o token localmente."""
    # Stateless: apenas instrução para o cliente descartar o token.
    return {"message": "Logged out"}
