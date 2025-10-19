"""
Esquemas de autenticação para a API.

- Token bearer retornado após login.
- Payload de login contendo credenciais do usuário.
"""

from pydantic import BaseModel

class Token(BaseModel):
    """Token JWT de acesso no padrão Bearer."""

    access_token: str
    token_type: str = "bearer"

class LoginInput(BaseModel):
    """Credenciais para autenticação via email/senha."""

    email: str
    password: str
