"""
Segurança da API: JWT e hash de senhas com bcrypt.

- JWT: criação e decodificação de tokens HS256.
- Senhas: hash/verify com bcrypt e salt aleatório interno.

Variáveis de ambiente esperadas:
- SECRET_KEY (string secreta para assinar JWTs)
- JWT_ALGORITHM (padrão: HS256)
- ACCESS_TOKEN_EXPIRE_MINUTES (padrão: 60)
"""

from datetime import datetime, timedelta
from typing import Optional, Any, Dict
from jose import jwt
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_USE_ENV")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def hash_password(plain_password: str) -> str:
    """Gera hash bcrypt com salt embutido. Retorna string codificada em UTF-8."""
    if isinstance(plain_password, str):
        plain_bytes = plain_password.encode("utf-8")
    else:
        plain_bytes = plain_password
    salt = bcrypt.gensalt()  # custo padrão (work factor) 12
    return bcrypt.hashpw(plain_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verifica senha: compara `plain_password` com `password_hash` usando bcrypt."""
    if isinstance(plain_password, str):
        plain_bytes = plain_password.encode("utf-8")
    else:
        plain_bytes = plain_password
    return bcrypt.checkpw(plain_bytes, password_hash.encode("utf-8"))


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None, extra: Optional[Dict[str, Any]] = None) -> str:
    """Cria um JWT assinado (HS256) com `sub` e `exp`. Campos extras opcionais."""
    to_encode: Dict[str, Any] = {"sub": subject}
    if extra:
        to_encode.update(extra)
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decodifica e valida um JWT assinado com `SECRET_KEY` e algoritmo HS256."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])